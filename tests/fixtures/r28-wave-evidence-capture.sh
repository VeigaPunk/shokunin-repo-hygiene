#!/usr/bin/env bash
# r28-wave-evidence-capture.sh — selftest fixture for
# tools/souji-wave-evidence-capture.sh.
#
# Round 29 (v2 layout) replacement for the r28 six-case file: cases 1-6 are
# preserved verbatim in intent, cases 7-12 exercise the committed-bytes
# layout (renames.tsv, excluded.tsv, symlinks.tsv, GNU escaped records and
# `--verify --rev <full40>`).
#
# Every case runs under
# ${SOUJI_R29_C2FIXTURE_BASE:-/var/tmp/souji-r29-wave-capture-fixture} (never the real
# lane wave dirs). Cases that need committed bytes get their own scratch git
# repo, created with `git -C <dir>` and root-verified with
# `git -C <dir> rev-parse --show-toplevel` before the first commit. Prints
# `cases=15 pass=<n> control=TAMPER-REJECTED`; exits 0 only when every check
# passes and the tamper control fires.
#
# CLI under test:
#   bash <tool> <lane-abs> <round-N>                        capture + verify disk copy
#   bash <tool> <lane-abs> <round-N> --verify               re-verify the disk copy
#   bash <tool> <lane-abs> <round-N> --verify --rev <full40> verify COMMITTED bytes
#
# Against the r28 base tool cases 7-12 are red (no `--verify --rev`, no
# bookkeeping tsvs); that is the intended red-before signal.
set -u
set -o pipefail
export LC_ALL=C
# Host git config must not perturb the scratch repos.
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

tool=${SOUJI_CAPTURE_TOOL:-}
if [[ -z $tool ]]; then
  d=$(cd "$(dirname "$0")" && pwd)
  while :; do
    if [[ -f $d/tools/souji-wave-evidence-capture.sh ]]; then
      tool="$d/tools/souji-wave-evidence-capture.sh"
      break
    fi
    if [[ $d == / ]]; then break; fi
    d=$(dirname -- "$d")
  done
fi
if [[ -z $tool || ! -f $tool ]]; then
  printf 'fixture-error: tool missing (set SOUJI_CAPTURE_TOOL)\n' >&2
  exit 99
fi
printf 'tool=%s\n' "$tool"

scratch_root=${SOUJI_R29_C2FIXTURE_BASE:-/var/tmp/souji-r29-wave-capture-fixture}
mkdir -p -- "$scratch_root" || exit 98
base=$(mktemp -d "$scratch_root/run.XXXXXX") || exit 98
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

subfail() { # $1 case id $2 why
  printf '%s: FAIL (%s)\n' "$1" "$2"
  fail=$((fail + 1))
}

mk_lane() { # $1 case id -> $lane
  lane="$base/lane-$1"
  mkdir -p "$lane/.ufo/waves/round-26" "$lane/.ufo/waves/round-27"
}

mk_lane_nosrc() { # $1 case id -> $lane (no wave dirs)
  lane="$base/lane-$1"
  mkdir -p "$lane"
}

# Scratch git lane for the committed-bytes cases: a fresh repository with the
# lane's ignore rules (`.ufo/waves/`, `__pycache__/`, `.git`) and a local-only
# identity. Returns non-zero if the repo root is not the lane directory.
mk_lane_git() { # $1 case id -> $lane
  lane="$base/git-$1"
  mkdir -p "$lane/.ufo/waves/round-26" "$lane/.ufo/waves/round-27" || return 1
  printf '.ufo/waves/\n__pycache__/\n.git\n' > "$lane/.gitignore" || return 1
  git -C "$lane" init -q -b main || return 1
  git -C "$lane" config user.name 'souji-fixture' &&
    git -C "$lane" config user.email 'fixture@localhost' &&
    git -C "$lane" config core.hooksPath /dev/null &&
    git -C "$lane" config commit.gpgsign false || return 1
  [[ $(git -C "$lane" rev-parse --show-toplevel 2>/dev/null) == "$lane" ]] || return 1
  return 0
}

commit_rev() { # $1 lane -> full40 of the receipt commit on stdout (empty on failure)
  local rev
  git -C "$1" add -A -- census >/dev/null 2>&1 || return 1
  git -C "$1" commit -q --no-gpg-sign -m 'r26 receipt' >/dev/null 2>&1 || return 1
  rev=$(git -C "$1" rev-parse --verify HEAD 2>/dev/null) || return 1
  [[ $rev =~ ^[0-9a-f]{40}$ ]] || return 1
  printf '%s' "$rev"
}

# tsvmate.py — tolerant reader for the v2 bookkeeping files. Column 1 of
# renames.tsv/excluded.tsv may be written with or without a leading `./`;
# symlinks.tsv column 1 must be the bare path relative to the waves dir because
# census/round-29/c2-counter.py looks it up as `rel = p[len(d):]`.
cat > "$base/tsvmate.py" <<'PY'
import hashlib, os, sys


def rows(path):
    try:
        with open(path, 'rb') as fh:
            text = fh.read().decode('utf-8', 'surrogateescape')
    except OSError:
        return []
    out = []
    for line in text.split('\n'):
        line = line.rstrip('\r')
        if not line or line.startswith('#'):
            continue
        out.append([f.rstrip('\r') for f in line.split('\t')])
    return out


def unescape(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s) and s[i + 1] in '\\n':
            out.append('\\' if s[i + 1] == '\\' else '\n')
            i += 2
            continue
        out.append(s[i])
        i += 1
    return ''.join(out)


def manifest_lines(rec):
    path = os.path.join(rec, 'manifest.sha256')
    try:
        with open(path, 'rb') as fh:
            text = fh.read().decode('utf-8', 'surrogateescape')
    except OSError:
        return []
    return [l for l in text.split('\n') if l]


def record_name(line):
    if line.startswith('\\'):
        line = unescape(line[1:])
    if len(line) >= 66 and line[64:66] == '  ':
        line = line[66:]
    return line[2:] if line.startswith('./') else line


def manifest_names(rec):
    return [record_name(l) for l in manifest_lines(rec)]


def die(msg):
    print('tsvmate: ' + msg, file=sys.stderr)
    return 1


def main():
    mode, rec = sys.argv[1], sys.argv[2]
    if mode == 'renames':
        orig, stored = sys.argv[3], sys.argv[4]
        for r in rows(os.path.join(rec, 'renames.tsv')):
            if len(r) >= 2 and r[0].endswith(orig) and r[1].endswith(stored):
                return 0
        return die('no renames.tsv row *%s -> *%s' % (orig, stored))
    if mode == 'excluded':
        want, reason, src = sys.argv[3], sys.argv[4], sys.argv[5]
        digest = hashlib.sha256(open(src, 'rb').read()).hexdigest()
        seen = []
        for r in rows(os.path.join(rec, 'excluded.tsv')):
            if len(r) >= 3 and r[0].endswith(want):
                seen.append('%s|%s|%s' % (r[0], r[1], r[2]))
                if r[2] == reason and r[1] == digest:
                    return 0
        return die('no excluded.tsv row *%s with sha256=%s reason=%s (saw %r)'
                   % (want, digest, reason, seen))
    if mode == 'symlink':
        name, target = sys.argv[3], sys.argv[4]
        for r in rows(os.path.join(rec, 'symlinks.tsv')):
            if len(r) >= 2 and r[0] == name and r[1] == target:
                return 0
        return die('no symlinks.tsv row %s\\t%s' % (name, target))
    if mode == 'manifest':
        want = sys.argv[3]
        names = manifest_names(rec)
        return 0 if want in names else die('manifest lacks %s' % want)
    if mode == 'absent':
        want = sys.argv[3]
        names = manifest_names(rec)
        return 0 if want not in names else die('manifest holds %s' % want)
    if mode == 'escaped':
        want = sys.argv[3]
        esc = [l for l in manifest_lines(rec) if l.startswith('\\')]
        for l in esc:
            if record_name(l) == want:
                return 0
        return die('no GNU escaped manifest record for %r (escaped records=%d)'
                   % (want, len(esc)))
    return die('unknown mode ' + mode)


sys.exit(main())
PY

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
mk_lane supp
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

# ---- case 7: nested .gitignore; its rule must not hide the captured file ----
# Source carries `.gitignore` with `fixture/` plus a file under fixture/. The
# .gitignore is stored as `.gitignore.captured` (renames.tsv) so the receipt's
# own path is not ignored: `fixture/keep.txt` is captured, is a manifest
# record, and a committed-bytes verify is clean.
if ! mk_lane_git 7; then subfail case-7 "scratch repo init/root check"; fi
mkdir -p "$lane/.ufo/waves/round-26/fixture"
printf 'fixture/\n' > "$lane/.ufo/waves/round-26/.gitignore"
printf 'gamma\n' > "$lane/.ufo/waves/round-26/fixture/keep.txt"
bash "$tool" "$lane" 26
cap_rc=$?
rec="$lane/census/round-26/waves"
[[ $cap_rc -eq 0 ]] || subfail case-7 "capture rc=$cap_rc want=0"
if [[ ! -f $rec/fixture/keep.txt ]]; then
  subfail case-7 "fixture/keep.txt not captured"
elif ! cmp -s "$lane/.ufo/waves/round-26/fixture/keep.txt" "$rec/fixture/keep.txt"; then
  subfail case-7 "fixture/keep.txt bytes differ"
fi
[[ -e $rec/.gitignore ]] && subfail case-7 "nested .gitignore not neutralised"
python3 -B "$base/tsvmate.py" renames "$rec" '.gitignore' '.gitignore.captured' ||
  subfail case-7 "renames.tsv row missing"
python3 -B "$base/tsvmate.py" manifest "$rec" 'fixture/keep.txt' ||
  subfail case-7 "fixture/keep.txt missing from manifest"
python3 -B "$base/tsvmate.py" manifest "$rec" 'summary.tsv' ||
  subfail case-7 "summary.tsv missing from manifest"
rev=$(commit_rev "$lane") || rev=""
if [[ -z $rev ]]; then
  subfail case-7 "receipt commit failed"
  rc=99
else
  bash "$tool" "$lane" 26 --verify --rev "$rev"
  rc=$?
fi
check 7 "committed-bytes verify rc=0" "$rc" 0
if [[ -n $rev ]]; then
  git -C "$lane" cat-file -e "$rev:census/round-26/waves/fixture/keep.txt" 2>/dev/null ||
    subfail case-7 "committed tree lacks fixture/keep.txt"
fi

# ---- case 8: ignored name (__pycache__/x.pyc) is accounted, not copied ----
# Root `.gitignore` carries `__pycache__/`, so the destination path is ignored.
# The source file is recorded in excluded.tsv (path, sha256 of source bytes,
# reason `ignored`), never copied and never a manifest record; the bookkeeping
# file itself is a manifest record, so committed-bytes verify stays clean.
if ! mk_lane_git 8; then subfail case-8 "scratch repo init/root check"; fi
mkdir -p "$lane/.ufo/waves/round-26/__pycache__"
printf 'pyc-bytes\n' > "$lane/.ufo/waves/round-26/__pycache__/x.pyc"
bash "$tool" "$lane" 26
cap_rc=$?
rec="$lane/census/round-26/waves"
[[ $cap_rc -eq 0 ]] || subfail case-8 "capture rc=$cap_rc want=0"
[[ -e $rec/__pycache__/x.pyc ]] && subfail case-8 "ignored name copied into receipt"
python3 -B "$base/tsvmate.py" excluded "$rec" '__pycache__/x.pyc' ignored \
  "$lane/.ufo/waves/round-26/__pycache__/x.pyc" || subfail case-8 "excluded.tsv row missing/wrong"
python3 -B "$base/tsvmate.py" manifest "$rec" 'excluded.tsv' ||
  subfail case-8 "excluded.tsv missing from manifest"
python3 -B "$base/tsvmate.py" manifest "$rec" 'summary.tsv' ||
  subfail case-8 "summary.tsv missing from manifest"
python3 -B "$base/tsvmate.py" absent "$rec" '__pycache__/x.pyc' ||
  subfail case-8 "ignored name leaked into manifest"
rev=$(commit_rev "$lane") || rev=""
if [[ -z $rev ]]; then
  subfail case-8 "receipt commit failed"
  rc=99
else
  bash "$tool" "$lane" 26 --verify --rev "$rev"
  rc=$?
fi
check 8 "committed-bytes verify rc=0" "$rc" 0

# ---- case 9: symlink listed in symlinks.tsv and present in the commit ----
# symlinks.tsv column 1 is the bare path relative to the waves dir, because
# c2-counter.py resolves committed symlinks as `rel = p[len(d):]`.
if ! mk_lane_git 9; then subfail case-9 "scratch repo init/root check"; fi
printf 'inner\n' > "$lane/.ufo/waves/round-26/inner.txt"
ln -s inner.txt "$lane/.ufo/waves/round-26/in-link"
bash "$tool" "$lane" 26
cap_rc=$?
rec="$lane/census/round-26/waves"
[[ $cap_rc -eq 0 ]] || subfail case-9 "capture rc=$cap_rc want=0"
[[ -L $rec/in-link ]] || subfail case-9 "symlink not preserved as a link"
python3 -B "$base/tsvmate.py" symlink "$rec" 'in-link' 'inner.txt' ||
  subfail case-9 "symlinks.tsv row missing"
python3 -B "$base/tsvmate.py" absent "$rec" 'in-link' ||
  subfail case-9 "symlink leaked into manifest"
rev=$(commit_rev "$lane") || rev=""
if [[ -z $rev ]]; then
  subfail case-9 "receipt commit failed"
  rc=99
else
  bash "$tool" "$lane" 26 --verify --rev "$rev"
  rc=$?
  [[ $(git -C "$lane" ls-tree "$rev" -- census/round-26/waves/in-link | cut -d' ' -f1) == 120000 ]] ||
    subfail case-9 "committed tree entry is not a symlink"
  [[ $(git -C "$lane" cat-file -p "$rev:census/round-26/waves/in-link" 2>/dev/null) == inner.txt ]] ||
    subfail case-9 "committed symlink blob target differs"
fi
check 9 "committed-bytes verify rc=0" "$rc" 0

# ---- case 10: newline in a file name -> GNU escaped record, verify accepts ----
if ! mk_lane_git 10; then subfail case-10 "scratch repo init/root check"; fi
odd=$'odd\nline.txt'
printf 'zeta\n' > "$lane/.ufo/waves/round-26/$odd"
bash "$tool" "$lane" 26
cap_rc=$?
rec="$lane/census/round-26/waves"
[[ $cap_rc -eq 0 ]] || subfail case-10 "capture rc=$cap_rc want=0"
[[ -f $rec/$odd ]] || subfail case-10 "newline-named file not captured"
python3 -B "$base/tsvmate.py" escaped "$rec" "$odd" ||
  subfail case-10 "no GNU escaped manifest record"
rev=$(commit_rev "$lane") || rev=""
if [[ -z $rev ]]; then
  subfail case-10 "receipt commit failed"
  rc=99
else
  bash "$tool" "$lane" 26 --verify --rev "$rev"
  rc=$?
fi
check 10 "committed-bytes verify rc=0" "$rc" 0

# ---- case 11: tamper a blob after the commit -> committed verify exits 4 ----
# First prove the untampered commit verifies (non-vacuity), then change one
# committed blob in a new commit and require rc 4.
if ! mk_lane_git 11; then subfail case-11 "scratch repo init/root check"; fi
printf 'delta\n' > "$lane/.ufo/waves/round-26/d.txt"
bash "$tool" "$lane" 26
cap_rc=$?
rec="$lane/census/round-26/waves"
[[ $cap_rc -eq 0 ]] || subfail case-11 "capture rc=$cap_rc want=0"
rev1=$(commit_rev "$lane") || rev1=""
if [[ -z $rev1 ]]; then
  subfail case-11 "receipt commit failed"
else
  bash "$tool" "$lane" 26 --verify --rev "$rev1"
  [[ $? -eq 0 ]] || subfail case-11 "untampered commit does not verify (vacuous control)"
  printf 'tampered\n' > "$rec/d.txt"
  git -C "$lane" add -A -- census >/dev/null 2>&1 &&
    git -C "$lane" commit -q --no-gpg-sign -m 'tamper one blob' >/dev/null 2>&1 ||
    subfail case-11 "tamper commit failed"
  rev2=$(git -C "$lane" rev-parse --verify HEAD 2>/dev/null) || rev2=""
  [[ -n $rev2 && $rev2 != "$rev1" ]] || subfail case-11 "tamper commit did not advance HEAD"
fi
rev2=${rev2:-}
if [[ ! $rev2 =~ ^[0-9a-f]{40}$ ]]; then
  rc=99
else
  bash "$tool" "$lane" 26 --verify --rev "$rev2"
  rc=$?
fi
check 11 "tampered committed blob rejected rc=4" "$rc" 4

# ---- case 12: `.git` file and `.git/` directory inside the source are stored as `.git.captured` ----
# Rule: no live `.git` path component in the receipt (a nested repo would become a gitlink);
# the bytes are preserved under `.git.captured`, each renamed file is recorded in renames.tsv and
# the manifest, and the committed-bytes verify of the receipt stays clean.
if ! mk_lane_git 12; then subfail case-12 "scratch repo init/root check"; fi
printf 'epsilon\n' > "$lane/.ufo/waves/round-26/e.txt"
printf 'gitdir: /nonexistent\n' > "$lane/.ufo/waves/round-26/.git"
mkdir -p "$lane/.ufo/waves/round-26/sub/.git/hooks"
printf 'ref: refs/heads/main\n' > "$lane/.ufo/waves/round-26/sub/.git/HEAD"
printf '#!/bin/sh\n' > "$lane/.ufo/waves/round-26/sub/.git/hooks/pre-commit.sample"
bash "$tool" "$lane" 26
cap_rc=$?
rec="$lane/census/round-26/waves"
[[ $cap_rc -eq 0 ]] || subfail case-12 "capture rc=$cap_rc want=0"
[[ -e $rec/.git || -e $rec/sub/.git ]] && subfail case-12 "live .git path copied into receipt"
[[ $(cat "$rec/.git.captured" 2>/dev/null) == 'gitdir: /nonexistent' ]] || subfail case-12 ".git file bytes not preserved as .git.captured"
[[ $(cat "$rec/sub/.git.captured/HEAD" 2>/dev/null) == 'ref: refs/heads/main' ]] || subfail case-12 ".git dir bytes not preserved"
python3 -B "$base/tsvmate.py" manifest "$rec" 'renames.tsv' || subfail case-12 "renames.tsv missing from manifest"
python3 -B "$base/tsvmate.py" manifest "$rec" 'sub/.git.captured/hooks/pre-commit.sample' ||
  subfail case-12 "renamed .git file missing from manifest"
python3 -B "$base/tsvmate.py" manifest "$rec" 'e.txt' ||
  subfail case-12 "ordinary sibling file missing from manifest"
rev=$(commit_rev "$lane") || rev=""
if [[ -z $rev ]]; then
  subfail case-12 "receipt commit failed"
  rc=99
else
  bash "$tool" "$lane" 26 --verify --rev "$rev"
  rc=$?
fi
check 12 "committed-bytes verify rc=0" "$rc" 0

# ---- case 13: payload tamper on disk (not the manifest) -> plain --verify exits 4 ----
# Kills a verify that recomputes only the manifest or hashes the source.
mk_lane 13
printf 'zeta\n' > "$lane/.ufo/waves/round-26/z.txt"
bash "$tool" "$lane" 26
cap_rc=$?
[[ $cap_rc -eq 0 ]] || subfail case-13 "capture rc=$cap_rc want=0"
printf 'ZETA\n' > "$lane/census/round-26/waves/z.txt"
bash "$tool" "$lane" 26 --verify
check 13 "disk payload tamper rejected rc=4" "$?" 4

# ---- case 14: non-numeric round argument is a usage error ----
mk_lane 14
bash "$tool" "$lane" 26x
check 14 "bad round usage rc=1" "$?" 1

# ---- case 15: absolute and nested-relative symlink targets survive verbatim ----
if ! mk_lane_git 15; then subfail case-15 "scratch repo init/root check"; fi
mkdir -p "$lane/.ufo/waves/round-26/sub"
printf 'inner\n' > "$lane/.ufo/waves/round-26/sub/inner.txt"
ln -s /etc/hostname "$lane/.ufo/waves/round-26/abs-link"
ln -s sub/inner.txt "$lane/.ufo/waves/round-26/rel-link"
bash "$tool" "$lane" 26
cap_rc=$?
[[ $cap_rc -eq 0 ]] || subfail case-15 "capture rc=$cap_rc want=0"
[[ $(readlink "$lane/census/round-26/waves/abs-link" 2>/dev/null) == /etc/hostname ]] || subfail case-15 "absolute link target changed"
[[ $(readlink "$lane/census/round-26/waves/rel-link" 2>/dev/null) == sub/inner.txt ]] || subfail case-15 "relative link target changed"
rev=$(commit_rev "$lane") || rev=""
if [[ -z $rev ]]; then rc=99; else bash "$tool" "$lane" 26 --verify --rev "$rev"; rc=$?; fi
check 15 "symlinks verbatim and committed-bytes verify rc=0" "$rc" 0

printf 'cases=15 pass=%s control=TAMPER-REJECTED\n' "$pass"
if [[ $fail -eq 0 && $control_tamper -eq 1 ]]; then
  exit 0
fi
exit 1
