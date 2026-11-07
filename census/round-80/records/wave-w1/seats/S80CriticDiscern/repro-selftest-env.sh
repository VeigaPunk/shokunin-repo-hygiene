#!/bin/bash
# S80CriticDiscern r80: F3 reproducer — the C2 selftest conjunct is lane-bound, not mode-bound.
# Usage: bash repro-selftest-env.sh [scratch-root]
# Materializes the W2 candidate (836dac3e) in a scratch dir, runs --selftest at 0755 and at 0644 from the
# lane cwd, and prints the failure counts. The committed receipts are 47-fail-free only when the lane's
# own tools/ tree is the instrument's REPO_ROOT (108/0).
set -u
S=${1:-/fast/scratch/hyaku/souji-r80/S80CriticDiscern/repro-selftest}
L=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S/d" "$S/t"
git -C "$L" show 836dac3e336863c57d9d7125837ed22b22d8d044:tools/souji-quarantine.sh > "$S/d/souji-quarantine.sh"
chmod 0755 "$S/d/souji-quarantine.sh"
for mode in 755 644; do
  chmod 0$mode "$S/d/souji-quarantine.sh"
  out=$S/t/$mode.out
  ( cd "$L" && TMPDIR=$S/t bash "$S/d/souji-quarantine.sh" --selftest ) > "$out" 2>&1 || true
  printf 'mode=%s %s rc126_lines=%s\n' "$mode" "$(tail -1 "$out")" "$(grep -c 'got=126' "$out")"
done
printf 'committed receipt: '; grep '^selftest:' "$L/census/round-80/records/c2-regress-selftest-committed-mode.txt"
