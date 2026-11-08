#!/bin/bash
# $1 = label, $2 = tool path; supplementary (non-frozen) probe rows only
set -u
S=/fast/scratch/hyaku/souji-r84/S84MutTool
l=$1; t=$2
rm -rf -- "$S/pwork-$l"
python3 -B "$S/probe-counter.py" --tool "$t" --work "$S/pwork-$l" > "$S/probe-$l.txt" 2>&1
echo "EXIT=$?" >> "$S/probe-$l.txt"
