#!/usr/bin/env bash
# r28-wave-evidence-capture.sh — selftest fixture for
# tools/souji-wave-evidence-capture.sh.
#
# Runs six isolated cases under ${TMPDIR:-/var/tmp} (never the real lane wave
# dirs) and prints `cases=6 pass=6 control=TAMPER-REJECTED` when all pass.
set -u
set -o pipefail
export LC_ALL=C

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
tool="$repo_root/tools/souji-wave-evidence-capture.sh"
if [[ ! -f $tool ]]; then
  printf 'fixture-error: tool missing: %s\n' "$tool" >&2
  exit 99
fi

base=$(mktemp -d "${TMPDIR:-/var/tmp}/r28-wave-fixture.XXXXXX") || exit 98
trap 'rm -rf -- "$base"' EXIT

pass=0
fail=0
control_tamper=0

check() { # $1 id $2 desc $3 actual rc $4 expected rc
  local id=$1 desc=$2 rc=$3 want=$4
  if [[ $rc -eq $want ]]; then
    printf 'case-%s: PASS (%s rc=%s)\n' "$id" "$desc" "$rc"
    pass=$((pass + 1))
  else
    printf 'case-%s: FAIL (%s rc=%s want=%s)\n' "$id" "$desc" "$rc" "$want"
    fail=$((fail + 1))
  fi
}

mk_lane() { # $1 case id -> $lane
  lane="$base/lane-$1"
  mkdir -p "$lane/.ufo/waves/round-26" "$lane/.ufo/waves/round-27"
}

mk_lane_nosrc() { # $1 case id -> $lane (no wave dirs)
  lane="$base/lane-$1"
  mkdir -p "$lane"
}

# ---- case 1: happy path, 2 files (a.txt + w1-results.json) ----
mk_lane 1
printf 'alpha\n' > "$lane/.ufo/waves/round-26/a.txt"
cat > "$lane/.ufo/waves/round-26/w1-results.json" <<'JSON'
{"lane": "L", "round": 26, "wave": "w1", "seats": 2, "results": [
  {"name": "One", "agent": "executor", "id": "One", "output": "{'text': '{\"status\": \"PASS\"}'}"},
  {"name": "Two", "agent": "executor", "id": "Two-2", "output": ""}
]}
JSON
bash "$tool" "$lane" 26
rc=$?
check 1 "happy path rc=0" "$rc" 0
if [[ $rc -eq 0 ]]; then
  rec="$lane/census/round-26/waves"
  if [[ -s $rec/manifest.sha256 && -f $rec/summary.tsv ]]; then
    lines=$(wc -l < "$rec/summary.tsv")
    if [[ $lines -ne 3 ]]; then
      printf 'case-1: FAIL (summary lines=%s want=3)\n' "$lines"
      fail=$((fail + 1))
    fi
  else
    printf 'case-1: FAIL (receipt files missing)\n'
    fail=$((fail + 1))
  fi
fi

# ---- case 2: missing source directory ----
mk_lane_nosrc 2
bash "$tool" "$lane" 26
check 2 "missing source refused rc=2" "$?" 2

# ---- case 3: tampered manifest flips verification ----
mk_lane 3
printf 'beta\n' > "$lane/.ufo/waves/round-26/b.txt"
bash "$tool" "$lane" 26
if [[ $? -ne 0 ]]; then
  printf 'case-3: FAIL (initial capture failed)\n'
  fail=$((fail + 1))
else

  rec="$lane/census/round-26/waves"
  python3 -B -c '
import sys
p = sys.argv[1]
d = bytearray(open(p, "rb").read())
d[0] ^= 1
open(p, "wb").write(bytes(d))
' "$rec/manifest.sha256"
  bash "$tool" "$lane" 26 --verify
  rc=$?
  check 3 "tampered manifest rejected rc=4" "$rc" 4
  [[ $rc -eq 4 ]] && control_tamper=1
fi

# ---- case 4: special file (fifo) inside snapshot ----
mk_lane 4
printf 'ok\n' > "$lane/.ufo/waves/round-26/ok.txt"
mkfifo "$lane/.ufo/waves/round-26/evil-fifo"
bash "$tool" "$lane" 26
check 4 "special file refused rc=3" "$?" 3

# ---- case 5: path traversal attempt in lane argument ----
mk_lane 5
bash "$tool" "$base/lane-5/../.." 26
check 5 "traversal refused rc=1" "$?" 1

# ---- case 6: empty directory captures cleanly ----
mk_lane 6
bash "$tool" "$lane" 26
rc=$?
check 6 "empty dir captured rc=0" "$rc" 0
if [[ $rc -eq 0 ]]; then
  rec="$lane/census/round-26/waves"
  captured=$(find "$rec" -type f ! -name manifest.sha256 ! -name summary.tsv | wc -l)
  if [[ $captured -ne 0 ]]; then
    printf 'case-6: FAIL (captured files=%s want=0)\n' "$captured"
    fail=$((fail + 1))
  fi
fi

# supplementary (not a case): symlink entries are preserved verbatim, never
# dereferenced, and sit outside the manifest hash set
mk_lane 7
printf 'inner\n' > "$lane/.ufo/waves/round-26/inner.txt"
ln -s inner.txt "$lane/.ufo/waves/round-26/in-link"
ln -s /etc/hostname "$lane/.ufo/waves/round-26/abs-link"
bash "$tool" "$lane" 26 >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
  printf 'supplementary: FAIL (symlink capture)\n'
  fail=$((fail + 1))
else
  rec="$lane/census/round-26/waves"
  if [[ -L $rec/in-link && -L $rec/abs-link ]]; then
    if grep -q 'in-link' "$rec/manifest.sha256"; then
      printf 'supplementary: FAIL (symlink leaked into manifest)\n'
      fail=$((fail + 1))
    fi
  else
    printf 'supplementary: FAIL (symlink not preserved as link)\n'
    fail=$((fail + 1))
  fi
fi

printf 'cases=6 pass=%s control=TAMPER-REJECTED\n' "$pass"
if [[ $fail -eq 0 && $control_tamper -eq 1 ]]; then
  exit 0
fi
exit 1
