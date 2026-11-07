#!/bin/bash
# #4: the refusal prints a count only, never a path.
. "$(dirname "$0")/probe-common.sh"; prep; D=$(mkfix); rm -f "$D/.git/HEAD"; mkfifo "$D/.git/HEAD"
T=30 rungate > "$H/d30.out" 2> "$H/d30.err"; echo "rc=$?"; cat "$H/d30.err"
echo "path echoes: fixture=$(grep -cF "$D" "$H/d30.err") HEAD=$(grep -cF HEAD "$H/d30.err")"
