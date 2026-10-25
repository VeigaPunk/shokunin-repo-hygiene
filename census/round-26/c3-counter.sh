#!/usr/bin/env bash
# souji round 26 C3 frozen counter (receipt-bound). Prints the axis-check
# instrument's presence and, when present, its verdict on this round's
# frozen preregistration. Read-only.
set -u
cd "$(dirname "$0")/../.." || exit 2
export LC_ALL=C
if [ -f tools/souji-axis-check.py ]; then
  printf 'axis_check_tool=present\n'
  python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
  printf 'axis_check_exit=%s\n' "$?"
else
  printf 'axis_check_tool=absent\n'
fi
