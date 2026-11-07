#!/bin/bash
# MEDIUM-3: SIGTERM kills the gate, not its git child (no trap in the gate).
. "$(dirname "$0")/probe-common.sh"; prep; D=$(mkfix)
printf '[core]\n\trepositoryformatversion = 0\n[include]\n\tpath = "nl\\nfifo"\n' > "$D/.git/config"; mkfifo "$D/.git/"$'nl\nfifo'
setsid bash -c 'echo $$ > '"$H/term.pid"'; exec timeout -k 5 45 bash '"$GATE"' --lane '"$D"' --branch master --report '"$D"'/report.md --prereg '"$D"'/prereg.txt' >"$H/term.out" 2>&1 &
sleep 4; GP=$(cat "$H/term.pid"); kill -TERM "$GP"; sleep 2
echo "gate alive after TERM: $(kill -0 $GP 2>/dev/null && echo yes || echo no)"
echo "survivors: $(ps -eo args | grep -F "$D" | grep -vc grep) (expect 2: timeout + git, bounded by 45 s)"
pkill -f "$D"; sleep 1
