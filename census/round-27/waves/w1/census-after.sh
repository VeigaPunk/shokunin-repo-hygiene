#!/usr/bin/env bash
# Read-only after-state receipt; run only after round-27 integration.
set -u

LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FLEET=/home/vgpnk/Projects/shokunin
OUT=
usage() { printf 'usage: %s --out ABSOLUTE_PATH\n' "$0" >&2; }
while (($#)); do
  case "$1" in
    --out)
      (($# >= 2)) || { usage; exit 2; }
      OUT=$2
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
done
[[ -n $OUT && $OUT = /* ]] || { usage; exit 2; }

# One-line fields keep the receipt a single TSV record.
clean() { local s=$1; s=${s//$'\t'/ }; s=${s//$'\r'/ }; s=${s//$'\n'/ }; printf '%s' "$s"; }
capture() {
  local __value=$1 __rc=$2; shift 2
  local result rc
  if result=$("$@" 2>&1); then rc=0; else rc=$?; fi
  printf -v "$__value" '%s' "$(clean "$result")"
  printf -v "$__rc" '%s' "$rc"
}

capture validate validate_rc /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root "$FLEET" souji
capture rows rows_rc grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' "$LANE/corpus/SOURCES.md"
capture grounded_f4 grounded_f4_rc bash -c 'grep -rlE "^ground: F4" "$1/corpus/knowledge/" | wc -l' _ "$LANE"
rev=$(git -C "$LANE" rev-parse HEAD 2>&1); rev_rc=$?
if ((rev_rc == 0)); then
  capture c1_findings c1_rc python3 -B "$LANE/tools/souji-landing-gate.py" --root "$LANE" --rev "$rev" --round 27 --fleet-root "$FLEET"
  c1_findings=$(printf '%s' "$c1_findings" | tr ' ' '\n' | awk -F'[[:space:]]+' '/^SUMMARY[[:space:]]+findings=/ {sub(/^findings=/, "", $2); print $2}' || true)
else
  c1_findings="rev-resolution-error:$(clean "$rev")"; c1_rc=$rev_rc
fi
capture c3_fixture c3_rc bash "$LANE/tests/fixtures/r27-pre-report-gate.sh"
if leftovers=$(git -C "$LANE" status --porcelain 2>&1); then leftovers_rc=0; else leftovers_rc=$?; fi
leftover_count=$(printf '%s\n' "$leftovers" | awk 'NF {n++} END {print n+0}')
leftovers=$(clean "$leftovers")

printf 'validate_output\tvalidate_rc\tregistry_rows\tregistry_rc\tgrounded_F4\tgrounded_F4_rc\tc1_findings\tc1_rc\tc3_fixture_output\tc3_rc\tleftovers_count\tleftovers_status\tleftovers_rc\n' > "$OUT"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$validate" "$validate_rc" "$rows" "$rows_rc" "$grounded_f4" "$grounded_f4_rc" \
  "$c1_findings" "$c1_rc" "$c3_fixture" "$c3_rc" "$leftover_count" "$leftovers" "$leftovers_rc" >> "$OUT"
