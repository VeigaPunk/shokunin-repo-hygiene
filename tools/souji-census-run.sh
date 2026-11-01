#!/usr/bin/env bash
# souji-census-run.sh — host adapter for the round contract's census command
# (souji r48). The contract names the conf form
#
#     sources-census.sh validate --root <fleet-root> <lane>
#
# which resolves lane `souji` through the fleet conf to
# `$ROOT/souji-shokunin/corpus/SOURCES.md`. On this host that path is absent
# (the lane checkout here is `shokunin-repo-hygiene/`; PROVINCE.md host
# correction, r46), so the raw contract form exits 2 "souji missing" — a
# documented host correction, kept disclosed, never masked: this adapter
# RUNS the conf form first and records its raw verdict, then runs the
# documented explicit-lane-directory form against THIS checkout (the repo
# one level above tools/), and exits with the directory form's code.
#
#   tools/souji-census-run.sh --fleet-root DIR [--lane souji] [--out PATH]
#                             [--today YYYY-MM-DD]
#   tools/souji-census-run.sh --selftest
#
# Output sections (machine-readable markers, then the fleet tool's own TSV):
#   PROVENANCE line  `# fleet-script sha256=<64hex> path=<fleet script>`
#   CONF-FORM BEGIN/END around the raw conf-form output
#   DIR-FORM BEGIN/END around the raw directory-form output
#   final line       `CENSUS-RUN lane=<lane> conf_rc=<n> dir_rc=<n>`
# Exit: the explicit-lane-directory form's exit code (2 usage/environment).
# Read-only: runs the fleet instrument unmodified (sha256 recorded); writes
# only stdout / --out. Never edits the fleet root or the conf.

set -u

usage() { sed -n '2,32p' "$0"; exit 2; }

FLEET=""; LANE="souji"; OUT=""; TODAY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --fleet-root) [ $# -ge 2 ] || usage; FLEET=$2; shift 2 ;;
    --lane)       [ $# -ge 2 ] || usage; LANE=$2; shift 2 ;;
    --out)        [ $# -ge 2 ] || usage; OUT=$2; shift 2 ;;
    --today)      [ $# -ge 2 ] || usage; TODAY=$2; shift 2 ;;
    --selftest)   SELftest=1; shift ;;
    *) usage ;;
  esac
done

selftest() {
  # Two arms over a synthetic fleet root. Arm A1 copies the REAL fleet
  # census script (read-only source: $SOUJI_FLEET_SCRIPT, or the documented
  # host path) into the fixture and reproduces the host condition: the conf
  # row names an ABSENT lane dir -> conf-form rc=2 while the adapter still
  # exits with the dir form's rc=0. Arm A2: fleet script missing -> adapter
  # exit 2 (environment, not findings). Arm A3: the dir form's ok-line.
  local REAL="${SOUJI_FLEET_SCRIPT:-C:/Users/jpvei/.zcode/workspace/95b1ba4d-5089-47a4-9fd8-54adebbce2ae/shokunin-clone/shokunin/scripts/sources-census.sh}"
  local ok=1 pass=0 cases=3
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/r48-census-selftest-XXXXXX") || return 2
  trap 'rm -rf "$tmp"' EXIT
  local ran_a1=0
  if [ -f "$REAL" ]; then
    ran_a1=1
    mkdir -p "$tmp/fleet/scripts"
    cp "$REAL" "$tmp/fleet/scripts/sources-census.sh"
    out=$(bash "$0" --fleet-root "$tmp/fleet" --lane souji 2>&1); rc=$?
    conf_rc=$(printf '%s\n' "$out" | sed -n 's/^CENSUS-RUN lane=souji conf_rc=\([0-9]*\) dir_rc=[0-9]*$/\1/p')
    dir_rc=$(printf '%s\n' "$out" | sed -n 's/^CENSUS-RUN lane=souji conf_rc=[0-9]* dir_rc=\([0-9]*\)$/\1/p')
    if [ "$rc" = 0 ] && [ "$conf_rc" = 2 ] && [ "$dir_rc" = 0 ]; then
      echo "SELFTEST-CASE pass host-condition conf_rc=2 dir_rc=0 adapter_rc=0"; pass=$((pass+1))
    else
      echo "SELFTEST-CASE fail host-condition rc=$rc conf_rc=$conf_rc dir_rc=$dir_rc"; ok=0
    fi
    if printf '%s\n' "$out" | sed -n '/^DIR-FORM BEGIN$/,/^DIR-FORM END$/p' \
        | grep -q $'^[a-z0-9][a-z0-9-]*\tok\t'; then
      echo "SELFTEST-CASE pass dir-form-ok-line"; pass=$((pass+1))
    else
      echo "SELFTEST-CASE fail dir-form-ok-line"; ok=0
    fi
  else
    echo "SELFTEST-CASE skip host-condition (real fleet script not found; set SOUJI_FLEET_SCRIPT)"
    echo "SELFTEST-CASE skip dir-form-ok-line"
  fi
  out2=$(bash "$0" --fleet-root "$tmp/missing-fleet" --lane souji 2>/dev/null); rc2=$?
  if [ "$rc2" = 2 ]; then
    echo "SELFTEST-CASE pass missing-fleet exit=2"; pass=$((pass+1))
  else
    echo "SELFTEST-CASE fail missing-fleet got=$rc2 want=2"; ok=0
  fi
  if [ "$ok" = 1 ]; then
    if [ "$ran_a1" = 1 ]; then echo "SELFTEST cases=$cases pass=$pass fail=0"; return 0; fi
    echo "SELFTEST cases=$cases pass=$pass fail=0 skip=$((cases-pass)) (env-dependent arms skipped)"; return 0
  fi
  echo "SELFTEST cases=$cases pass=$pass fail>=1" >&2; return 1
}

[ "${SELftest:-0}" = 1 ] && { selftest; exit $?; }

[ -n "$FLEET" ] || usage
SCRIPT=$(cygpath -u "$FLEET" 2>/dev/null || printf '%s' "$FLEET")
FLEET=$SCRIPT
FLEET_SCRIPT="$FLEET/scripts/sources-census.sh"
[ -f "$FLEET_SCRIPT" ] || { echo "ERROR: fleet script missing: $FLEET_SCRIPT" >&2; exit 2; }
[ -x /usr/bin/sha256sum ] && SHA=$(sha256sum "$FLEET_SCRIPT" | cut -d' ' -f1) \
  || SHA=$(shasum -a 256 "$FLEET_SCRIPT" | cut -d' ' -f1)
LANEDIR=$(cd "$(dirname "$0")/.." && pwd)

emit() { printf '%s\n' "$*"; }

TODAY_ARG=""
[ -n "$TODAY" ] && TODAY_ARG="--today $TODAY"

emit "# fleet-script sha256=$SHA path=$FLEET_SCRIPT"
emit "CONF-FORM BEGIN"
conf_out=$(bash "$FLEET_SCRIPT" validate --root "$FLEET" "$LANE" $TODAY_ARG 2>&1)
conf_rc=$?
emit "$conf_out"
emit "CONF-FORM END"
emit "DIR-FORM BEGIN"
dir_out=$(bash "$FLEET_SCRIPT" validate --root "$FLEET" "$LANEDIR" $TODAY_ARG 2>&1)
dir_rc=$?
emit "$dir_out"
emit "DIR-FORM END"
emit "CENSUS-RUN lane=$LANE conf_rc=$conf_rc dir_rc=$dir_rc"

if [ -n "$OUT" ]; then
  { printf '%s\n' "# fleet-script sha256=$SHA path=$FLEET_SCRIPT"
    printf 'CONF-FORM BEGIN\n%s\nCONF-FORM END\n' "$conf_out"
    printf 'DIR-FORM BEGIN\n%s\nDIR-FORM END\n' "$dir_out"
    printf 'CENSUS-RUN lane=%s conf_rc=%s dir_rc=%s\n' "$LANE" "$conf_rc" "$dir_rc"
  } > "$OUT"
fi
exit "$dir_rc"
