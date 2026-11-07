#!/bin/bash
# MEDIUM-1: an include value containing a newline is truncated by the gate's line parser,
# so the file git really includes is never checked.  Expect: check-gitsource=PASS on a repo
# whose include target is a FIFO; check 1 then blocks 45 s (RECEIPT-GIT-TIMEOUT).
. "$(dirname "$0")/probe-common.sh"; prep; D=$(mkfix)
printf '[core]\n\trepositoryformatversion = 0\n[include]\n\tpath = "nl\\nfifo"\n' > "$D/.git/config"
mkfifo "$D/.git/"$'nl\nfifo'
echo "scan emits:"; git --no-optional-locks config --no-includes --file "$D/.git/config" --get-regexp '^include(if\..*)?\.path$'
echo "git discovery (8 s cap):"; timeout -k 2 8 git --no-optional-locks -C "$D" rev-parse --show-toplevel; echo "rc=$? (124 = blocked on the FIFO)"
T=130 rungate 2>&1 | head -8
