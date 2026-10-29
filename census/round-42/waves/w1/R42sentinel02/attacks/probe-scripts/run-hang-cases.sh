#!/usr/bin/env bash
SCR=/fast/scratch/hyaku/souji-r42/R42sentinel02
SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42sentinel02
set -u
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
cd "$SCR/instr/clone" || exit 2
cp "$SCR/cands/v12-hang-cases.py" tools/souji-freeze-check.py
git -C "$SCR/instr/clone" add -A
git -C "$SCR/instr/clone" commit -q -m hang-cases
REV=$(git -C "$SCR/instr/clone" rev-parse HEAD)
out="$SEAT/receipts/hang-cases-timeout-instrumented.txt"
{ echo "start $(date +%T)"; python3 -B "$SCR/instr/c2-counter-timeout3.py" --root "$SCR/instr/clone" --rev "$REV" --scratch "$SCR/instr"; echo "counter_rc=$?"; echo "end $(date +%T)"; echo "leftover-scratch=$(ls -d $SCR/instr/souji-r42-c2.* 2>/dev/null | wc -l)"; } > "$out" 2>&1
echo HANG-CASES-DONE > "$SCR/receipts/hang-cases-done.txt"
