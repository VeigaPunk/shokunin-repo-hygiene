#!/bin/bash
# S80CriticDiscern r80: F4 reproducer — the v3 domain trial's guard passes an all-blocked pair.
# Usage: bash repro-v3-blocked.sh [scratch-root]
# Copies the committed v3 probe (60c7f50e), points its three targets at untracked scratch files, runs the
# base (f80f9368) and candidate (836dac3e) tools, and prints TRIAL. Expect: 3 DRY-RUN-BLOCKED RESULT lines
# per arm, dryrun-pass=0, result_lines_*=3, TRIAL identical=yes, EXIT=0 (the v1 vacuity class one level up).
set -u
S=${1:-/fast/scratch/hyaku/souji-r80/S80CriticDiscern/repro-v3}
L=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S"
git -C "$L" show 60c7f50eb803a6ee6d887fabdd32ab0e9e8102bc:census/round-80/probes/domain-trial.sh > "$S/dt.sh"
git -C "$L" show f80f9368a8a20679438b1dffd72d0faab0ccf194:tools/souji-quarantine.sh > "$S/base.tool"
git -C "$L" show 836dac3e336863c57d9d7125837ed22b22d8d044:tools/souji-quarantine.sh > "$S/cand.tool"
printf 'a\n' > "$S/untracked-a.txt"; printf 'b\n' > "$S/untracked-b.txt"; printf 'c\n' > "$S/untracked-c.txt"
sed "s|^tg=.*|tg=(\"$S/untracked-a.txt\" \"$S/untracked-b.txt\" \"$S/untracked-c.txt\")|" "$S/dt.sh" > "$S/dt-blocked.sh"
bash "$S/dt-blocked.sh" "$S/base.tool" "$S/cand.tool" "$S/w" 2>&1 | grep -E 'base_rc|result_lines|TRIAL|SUMMARY'
