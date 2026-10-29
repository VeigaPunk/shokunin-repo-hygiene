#!/usr/bin/env bash
SCR=/fast/scratch/hyaku/souji-r42/R42sentinel02
SEAT=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42sentinel02
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
set -u
# 1) re-run v11 with explicit exit capture
cd "$SCR/cwdprobe" || exit 2
bash "$LANE/census/round-42/score-candidate.sh" c2 "$SCR" "tools/souji-freeze-check.py=$SCR/cands/v11-scratch-poison.py" > "$SEAT/receipts/score-c2-v11-scratch-poison.txt" 2>&1
echo "exit=$?" >> "$SEAT/receipts/score-c2-v11-scratch-poison.txt"
# 2) GIT_DIR hostile environment against a decoy repository only (never the lane)
rm -rf "$SCR/decoy"; mkdir -p "$SCR/decoy"
git init -q "$SCR/decoy"
echo decoy > "$SCR/decoy/README"
git -C "$SCR/decoy" add -A
git -C "$SCR/decoy" -c user.name=f -c user.email=f@example.invalid commit -q -m decoy-base
before=$(git -C "$SCR/decoy" rev-parse HEAD)
GIT_DIR="$SCR/decoy/.git" bash "$LANE/census/round-42/score-candidate.sh" c2 "$SCR" "tools/souji-freeze-check.py=$SCR/cands/v4-stub-plain.py" > "$SEAT/receipts/env-GIT_DIR-decoy-scorer.txt" 2>&1
echo "exit=$?" >> "$SEAT/receipts/env-GIT_DIR-decoy-scorer.txt"
after=$(git -C "$SCR/decoy" rev-parse HEAD)
{ echo "decoy-before=$before"; echo "decoy-after=$after"; echo "decoy-commits=$(git -C "$SCR/decoy" rev-list --count HEAD)"; git -C "$SCR/decoy" log --format='%s' | head -3; } > "$SEAT/receipts/env-GIT_DIR-decoy-state.txt"
echo MISC-DONE > "$SCR/receipts/misc-done.txt"
