#!/bin/bash
# $1 = mutant basename (without .sh); run the frozen counter on it, receipts into scratch
set -u
S=/fast/scratch/hyaku/souji-r84/S84MutTool
L=/home/vgpnk/Projects/shokunin/souji-shokunin
n=$1
rm -rf -- "$S/work-$n"
cd "$L" || exit 9
python3 -B census/round-84/c2-late-fork-counter.py \
  --tool "$L/.ufo/waves/round-84/w1/S84MutTool/mutants/$n.sh" \
  --work "$S/work-$n" > "$S/$n.txt" 2>&1
echo "EXIT=$?" >> "$S/$n.txt"
