#!/usr/bin/env bash
# r13 Q8 regression fixture — bounded per-target staging/digest + special files.
#
# Runs tools/souji-quarantine.sh (or --tool PATH, e.g. a baseline copy under
# /var/tmp) against an isolated git repo and asserts the Q8 contract:
#
#   R13Q8-01  regular stale file, full flow -> DELETED (the control case)
#   R13Q8-02  FIFO target, --dry-run        -> special-file-refused, no read
#   R13Q8-03  FIFO descendant, --dry-run    -> special-descendant, no read
#   R13Q8-04  delayed mv                    -> STAGE2-FAILED mv-timeout
#   R13Q8-05  delayed sha256sum             -> NOT-AUTHORIZED digest-timeout
#
# Red-before mode: run the same fixture with `--tool <baseline copy>`. The
# baseline has no per-target bound, so 04/05 HANG at this fixture's outer
# 20s bound, and 02/03 exit silently (set -e in the pin digest, no RESULT).
# A red never depends on the live-fleet guard: the fixture always sets
# SOUJI_QUARANTINE_ALLOW_LIVE=1 for its isolated mktemp repo and pins
# SOUJI_VERIFY_BIN to the installed engine, because a baseline copy outside
# this repo would otherwise look for a missing sibling engine.
#
# Clock compression: the delayed cases put a PATH `timeout` shim in front of
# the tool that rewrites its fixed bound (e.g. 60s) to 2s with kill-after 1,
# preserving GNU timeout semantics. The shim only matches the tool's
# documented `timeout --kill-after=N DURATION COMMAND` shape; a tool that
# never calls timeout (the baseline) hangs and is reported HANG, not PASS.
#
# CLI
#   tests/fixtures/r13-quarantine-bounds.sh [--tool PATH] [--verify PATH]
#        [--case ID ...] [-h]
#   --tool    quarantine tool under test (default <repo>/tools/souji-quarantine.sh;
#             SOUJI_QUARANTINE_BIN is honored when --tool is absent)
#   --verify  receipt engine pinned via SOUJI_VERIFY_BIN (default
#             <repo>/tools/souji-verify.sh)
#   --case    run only the named case(s); repeatable
#
# Output: CASE<TAB><id><TAB>PASS|FAIL|HANG<TAB><detail> ... SUMMARY<TAB>...
# Exit: 0 every selected case PASS; 1 any FAIL/HANG; 2 usage/environment.
# All scratch lives under `mktemp -d /var/tmp/...` and is removed by trap.
set -euo pipefail
export LC_ALL=C

FIXTURE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
LANE_ROOT="$(cd -- "$FIXTURE_DIR/../.." && pwd -P)"

TOOL="${SOUJI_QUARANTINE_BIN:-$LANE_ROOT/tools/souji-quarantine.sh}"
VERIFY="$LANE_ROOT/tools/souji-verify.sh"
SELECT=()

usage() {
  printf 'usage: %s [--tool PATH] [--verify PATH] [--case ID ...]\n' "$0"
  printf 'cases: R13Q8-01 R13Q8-02 R13Q8-03 R13Q8-04 R13Q8-05\n'
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) [ "$#" -ge 2 ] || { usage; exit 2; }; TOOL=$2; shift 2 ;;
    --tool=*) TOOL=${1#*=}; shift ;;
    --verify) [ "$#" -ge 2 ] || { usage; exit 2; }; VERIFY=$2; shift 2 ;;
    --verify=*) VERIFY=${1#*=}; shift ;;
    --case) [ "$#" -ge 2 ] || { usage; exit 2; }; SELECT+=("$2"); shift 2 ;;
    --case=*) SELECT+=("${1#*=}"); shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'r13-quarantine-bounds: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

resolve_bin() { # $1 command name -> absolute path on stdout
  local p=""
  p=$(type -P "$1" 2>/dev/null || true)
  case "$p" in /*) printf '%s' "$p"; return 0 ;; esac
  for p in "/usr/bin/$1" "/bin/$1"; do
    [ -x "$p" ] && { printf '%s' "$p"; return 0; }
  done
  return 1
}

REAL_TIMEOUT=$(resolve_bin timeout) || { printf 'r13-quarantine-bounds: timeout not found\n' >&2; exit 2; }
REAL_MV=$(resolve_bin mv) || { printf 'r13-quarantine-bounds: mv not found\n' >&2; exit 2; }
REAL_SHA=$(resolve_bin sha256sum) || { printf 'r13-quarantine-bounds: sha256sum not found\n' >&2; exit 2; }

[ -r "$TOOL" ] || { printf 'r13-quarantine-bounds: tool not readable: %s\n' "$TOOL" >&2; exit 2; }
[ -r "$VERIFY" ] || { printf 'r13-quarantine-bounds: engine not readable: %s\n' "$VERIFY" >&2; exit 2; }

SCRATCH=$(mktemp -d /var/tmp/r13-qbounds.XXXXXX) || exit 1
cleanup() { rm -rf -- "${SCRATCH:?}"; }
trap cleanup EXIT

REPO="$SCRATCH/repo"
LEDGER="$SCRATCH/ledger.tsv"
mkdir -p "$REPO"
git -c maintenance.auto=false -C "$SCRATCH" init -q --initial-branch=master "$REPO"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LEDGER"

TODAY=$(date -u +%F)
CASE_FAILS=()
RUN_OUT=""
RUN_RC=0

begin_case() { CASE_FAILS=(); }
expect() { # $1 ok(0|1) $2 label
  [ "${1:-0}" = 1 ] || CASE_FAILS+=("$2")
}
has_token() { printf '%s' "$RUN_OUT" | grep -aqF -- "$1"; }
has_no_token() { ! printf '%s' "$RUN_OUT" | grep -aqF -- "$1"; }

finish_case() { # $1 id, $2 detail
  local id=$1 detail=${2:-} status=PASS reason=""
  EMITTED_IDS+=("$id")
  if [ "${#CASE_FAILS[@]}" -gt 0 ]; then
    if [ "$RUN_RC" -eq 124 ] || [ "$RUN_RC" -eq 137 ]; then
      status=HANG
      HANGED=$((HANGED + 1))
    else
      status=FAIL
    fi
    reason=$(printf '%s; ' "${CASE_FAILS[@]}")
    reason=${reason%; }
    FAILED=$((FAILED + 1))
  fi
  if [ "$status" = PASS ]; then
    printf 'CASE\t%s\tPASS\t%s\n' "$id" "$detail"
  else
    printf 'CASE\t%s\t%s\trc=%s %s\n' "$id" "$status" "$RUN_RC" "$reason"
  fi
  return 0
}

run_tool() { # $1 shim dir (empty = none), rest = tool args
  local shims=$1; shift
  local path=$PATH
  if [ -n "$shims" ]; then path="$shims:$PATH"; fi
  RUN_OUT=""
  RUN_RC=0
  RUN_OUT=$(env SOUJI_QUARANTINE_ALLOW_LIVE=1 \
    SOUJI_VERIFY_BIN="$VERIFY" \
    SOUJI_Q_SHOKUNIN_ROOT="$SCRATCH" \
    SOUJI_Q_LEDGER="$LEDGER" \
    PATH="$path" \
    "$REAL_TIMEOUT" --kill-after=5 20 bash "$TOOL" --hold 0 "$@" 2>&1) || RUN_RC=$?
}

mk_timeout_shim() { # $1 dir $2 real timeout path
  {
    printf '#!/usr/bin/env bash\n'
    printf 'set -u\n'
    printf 'case "${1:-}" in --kill-after=*) ;; *) printf "shim-timeout: unexpected argv\\n" >&2; exit 2 ;; esac\n'
    printf 'shift\n'
    printf 'case "${1:-}" in ""|*[!0-9]*) printf "shim-timeout: duration not literal\\n" >&2; exit 2 ;; esac\n'
    printf 'shift\n'
    printf 'exec %q --kill-after=1 2 "$@"\n' "$2"
  } > "$1/timeout"
  chmod 0755 "$1/timeout"
}

mk_sleep_shim() { # $1 dir $2 name $3 real path $4 seconds
  {
    printf '#!/usr/bin/env bash\n'
    printf 'sleep %s\n' "$4"
    printf 'exec %q "$@"\n' "$3"
  } > "$1/$2"
  chmod 0755 "$1/$2"
}

new_aged_file() { # $1 path $2 payload
  printf '%s\n' "$2" > "$1"
  touch -d '3 days ago' "$1"
}

case_01() {
  local t="$REPO/.scratch/aged01.dat"
  begin_case
  mkdir -p "$REPO/.scratch"
  new_aged_file "$t" 'r13 bounds regular payload 01'
  run_tool "" "$REPO" "$t"
  expect "$([ "$RUN_RC" = 0 ] && echo 1 || echo 0)" "rc=$RUN_RC want=0"
  expect "$(has_token "$(printf 'RESULT\t%s\tDELETED\tstale' "$t")" && echo 1 || echo 0)" "missing DELETED/stale"
  expect "$(has_token "SUMMARY" && echo 1 || echo 0)" "missing SUMMARY"
  expect "$([ ! -e "$t" ] && echo 1 || echo 0)" "source still present"
  finish_case R13Q8-01 "regular stale file fully staged and cleaned"
}

case_02() {
  local t="$REPO/.scratch/pipe02.fifo"
  begin_case
  mkdir -p "$REPO/.scratch"
  mkfifo "$t"
  touch -h -d '3 days ago' "$t"
  run_tool "" --dry-run "$REPO" "$t"
  expect "$([ "$RUN_RC" = 3 ] && echo 1 || echo 0)" "rc=$RUN_RC want=3"
  expect "$(has_token "$(printf 'RESULT\t%s\tDRY-RUN-BLOCKED\tspecial-file-refused' "$t")" && echo 1 || echo 0)" "missing special-file-refused"
  expect "$([ -p "$t" ] && echo 1 || echo 0)" "fifo no longer a fifo"
  expect "$([ ! -e "$REPO/.ufo-quarantine" ] && echo 1 || echo 0)" "quarantine dir created"
  finish_case R13Q8-02 "FIFO target refused before any read"
}

case_03() {
  local d="$REPO/.scratch/ageddir03"
  begin_case
  mkdir -p "$d"
  mkfifo "$d/inner.fifo"
  touch -h -d '3 days ago' "$d/inner.fifo"
  touch -d '3 days ago' "$d"
  run_tool "" --dry-run "$REPO" "$d"
  expect "$([ "$RUN_RC" = 3 ] && echo 1 || echo 0)" "rc=$RUN_RC want=3"
  expect "$(has_token "$(printf 'RESULT\t%s\tDRY-RUN-BLOCKED\tspecial-descendant' "$d")" && echo 1 || echo 0)" "missing special-descendant"
  expect "$([ -p "$d/inner.fifo" ] && echo 1 || echo 0)" "descendant fifo gone"
  expect "$([ ! -e "$REPO/.ufo-quarantine" ] && echo 1 || echo 0)" "quarantine dir created"
  finish_case R13Q8-03 "FIFO descendant refused before any digest"
}

case_04() {
  local t="$REPO/.scratch/aged04.dat" shims="$SCRATCH/shims04" qp
  begin_case
  mkdir -p "$REPO/.scratch" "$shims"
  new_aged_file "$t" 'r13 bounds delayed mv payload 04'
  mk_timeout_shim "$shims" "$REAL_TIMEOUT"
  mk_sleep_shim "$shims" mv "$REAL_MV" 30
  qp="$REPO/.ufo-quarantine/$TODAY/.scratch/aged04.dat"
  run_tool "$shims" "$REPO" "$t"
  expect "$([ "$RUN_RC" = 3 ] && echo 1 || echo 0)" "rc=$RUN_RC want=3"
  expect "$(has_token "$(printf 'RESULT\t%s\tSTAGE2-FAILED\tmv-timeout' "$t")" && echo 1 || echo 0)" "missing STAGE2-FAILED mv-timeout"
  expect "$(has_token "SUMMARY" && echo 1 || echo 0)" "missing SUMMARY"
  expect "$([ -f "$t" ] && echo 1 || echo 0)" "source missing after timeout"
  expect "$([ ! -e "$qp" ] && echo 1 || echo 0)" "unexpected quarantine copy"
  expect "$(has_no_token "$(printf 'RESULT\t%s\tDELETED' "$t")" && echo 1 || echo 0)" "deleted after timeout"
  finish_case R13Q8-04 "delayed mv bounded; failure reported, nothing deleted"
}

case_05() {
  local t="$REPO/.scratch/aged05.dat" shims="$SCRATCH/shims05" qp
  begin_case
  mkdir -p "$REPO/.scratch" "$shims"
  new_aged_file "$t" 'r13 bounds delayed sha256sum payload 05'
  mk_timeout_shim "$shims" "$REAL_TIMEOUT"
  mk_sleep_shim "$shims" sha256sum "$REAL_SHA" 30
  qp="$REPO/.ufo-quarantine/$TODAY/.scratch/aged05.dat"
  run_tool "$shims" "$REPO" "$t"
  expect "$([ "$RUN_RC" = 3 ] && echo 1 || echo 0)" "rc=$RUN_RC want=3"
  expect "$(has_token "$(printf 'RESULT\t%s\tNOT-AUTHORIZED\tdigest-timeout' "$t")" && echo 1 || echo 0)" "missing NOT-AUTHORIZED digest-timeout"
  expect "$(has_token "SUMMARY" && echo 1 || echo 0)" "missing SUMMARY"
  expect "$([ -f "$t" ] && echo 1 || echo 0)" "source missing after timeout"
  expect "$([ ! -e "$qp" ] && echo 1 || echo 0)" "unexpected quarantine copy"
  finish_case R13Q8-05 "delayed sha256sum bounded; stage 1 refused"
}

want_case() { # $1 id
  local want
  [ "${#SELECT[@]}" -eq 0 ] && return 0
  for want in "${SELECT[@]}"; do
    [ "$want" = "$1" ] || [ "$want" = all ] || continue
    return 0
  done
  return 1
}

printf 'TOOL\t%s\tsha256=%s\n' "$TOOL" "$("$REAL_SHA" "$TOOL" | cut -d' ' -f1)"
printf 'VERIFY\t%s\n' "$VERIFY"

FAILED=0
HANGED=0
RAN=0
EMITTED_IDS=()
# Independent expected set: removing a loop case or its finding emission fails.
EXPECTED_IDS=(R13Q8-01 R13Q8-02 R13Q8-03 R13Q8-04 R13Q8-05)
for id in R13Q8-01 R13Q8-02 R13Q8-03 R13Q8-04 R13Q8-05; do
  want_case "$id" || continue
  RAN=$((RAN + 1))
  case "$id" in
    R13Q8-01) case_01 ;;
    R13Q8-02) case_02 ;;
    R13Q8-03) case_03 ;;
    R13Q8-04) case_04 ;;
    R13Q8-05) case_05 ;;
  esac
done

if [ "$RAN" -eq 0 ]; then
  printf 'r13-quarantine-bounds: no case matched: %s\n' "${SELECT[*]}" >&2
  exit 2
fi

if [ "${#SELECT[@]}" -eq 0 ] && [ "${EMITTED_IDS[*]}" != "${EXPECTED_IDS[*]}" ]; then
  printf 'CASE\tR13Q8-ID-SET\tFAIL\texpected=%s actual=%s\n' \
    "${EXPECTED_IDS[*]}" "${EMITTED_IDS[*]}"
  FAILED=$((FAILED + 1))
fi
printf 'SUMMARY\ttotal=%d\tfailed=%d\thung=%d\n' "$RAN" "$FAILED" "$HANGED"
[ "$FAILED" -eq 0 ]
