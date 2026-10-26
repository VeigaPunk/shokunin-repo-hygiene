#!/usr/bin/env bash
# r32 measurement runner: every frozen counter at one full revision, read-only on the lane.
# Usage: measure.sh <full40-rev> [c1|c2|c3|all]
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
B=85b61a151923986e7e6b48f7084b9122561b5f3d
P=3ec84fc81b3243429c834a051880b0bcde06291c
R=${1:?rev}; W=${2:-all}
S=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r32/measure; mkdir -p "$S"
run() { printf '$ %s\n' "$*"; "$@" 2>&1 | grep -E '^(SUMMARY|ITEM|L[0-9]+ |COULD)' ; printf 'exit=%s\n' "${PIPESTATUS[0]}"; }
case $W in all|c1)
  run python3 -B "$LANE/census/round-32/c1-counter.py" --root "$LANE" --rev "$R" --base $B --list-rev $P --scratch "$S/c1"
  run python3 -B "$LANE/census/round-32/c1-counter-v2.py" --root "$LANE" --rev "$R" --base $B --list-rev $P --scratch "$S/c1v2";;
esac
case $W in all|c2)
  run python3 -B "$LANE/census/round-32/c2-counter.py" --root "$LANE" --rev "$R" --base $B --list-rev $P --scratch "$S/c2";;
esac
case $W in all|c3)
  run python3 -B "$LANE/census/round-32/c3-counter.py" --root "$LANE" --rev "$R" --base $B --list-rev $P --scratch "$S/c3";;
esac
