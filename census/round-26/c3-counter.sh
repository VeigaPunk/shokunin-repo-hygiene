#!/usr/bin/env bash
# souji round 26 C3 frozen counter (receipt-bound). Prints the axis-check
# instrument's presence and, when present, its verdict on this round's
# frozen preregistration. With `--stub`, runs the fixture's FALSE-GREEN
# control arm instead (receipt binds the labelled tool, per R3).
# Read-only.
set -u
cd "$(dirname "$0")/../.." || exit 2
export LC_ALL=C
case "${1:-}" in
  --stub)
    python3 tests/fixtures/r26-axis-check.py --stub
    exit $?
    ;;
  "") ;;
  *) echo "usage: c3-counter.sh [--stub]" >&2; exit 2 ;;
esac
if [ -f tools/souji-axis-check.py ]; then
  printf 'axis_check_tool=present\n'
  python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
  printf 'axis_check_exit=%s\n' "$?"
else
  printf 'axis_check_tool=absent\n'
fi
