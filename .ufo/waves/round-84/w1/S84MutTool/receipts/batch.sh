#!/bin/bash
S=/fast/scratch/hyaku/souji-r84/S84MutTool
for n in "$@"; do "$S/run_mut.sh" "$n" & done
wait
echo "BATCH-DONE $*"
