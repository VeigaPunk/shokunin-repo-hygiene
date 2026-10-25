#!/usr/bin/env bash
# souji round 26 C3 frozen counter (receipt-bound). Prints the axis-check
# instrument's presence and, when present, its verdict on this round's
# frozen preregistration AND the 12-case falsification fixture (K1/K2).
# Read-only; everything runs in /var/tmp scratch.
set -u
cd "$(dirname "$0")/../.." || exit 2
export LC_ALL=C
if [ -f tools/souji-axis-check.py ]; then
  printf 'axis_check_tool=present\n'
  python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
  printf 'axis_check_exit=%s\n' "$?"
  python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py | tail -n 1
  printf 'fixture_exit=%s\n' "${PIPESTATUS[0]}"
else
  printf 'axis_check_tool=absent\n'
fi
