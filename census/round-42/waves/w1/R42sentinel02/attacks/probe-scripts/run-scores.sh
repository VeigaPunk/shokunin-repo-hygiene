#!/usr/bin/env bash
# runs one frozen c2 score per hostile/honest variant, cwd = scratch cwdprobe
cd "/fast/scratch/hyaku/souji-r42/R42sentinel02/cwdprobe" || exit 2
run_one() {
  v="$1"
  bash "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh" c2 "/fast/scratch/hyaku/souji-r42/R42sentinel02" "tools/souji-freeze-check.py=/fast/scratch/hyaku/souji-r42/R42sentinel02/cands/$v.py" > "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42sentinel02/receipts/score-c2-$v.txt" 2>&1
  echo "exit=$?" >> "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42sentinel02/receipts/score-c2-$v.txt"
}
export -f run_one
export SCR SEAT LANE
printf '%s\n' v0-honest v2-stub-tripwire v4-stub-plain v5-reexec-isolated v6-pathstrip v7-hashlib-new v8-probe-writes v9-child-bytecode | xargs -P 4 -I{} bash -c 'run_one {}'
echo ALL-DONE > "/fast/scratch/hyaku/souji-r42/R42sentinel02/receipts/scores-done.txt"
