#!/bin/bash
# $1 name, $2 fixture ; SIGINT the fixture python while a child tool process is live (scratch-only)
S=/fast/scratch/hyaku/souji-r41/R41w2sentinel02
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
export TMPDIR=$S/tmp
name=$1; fx=$2; W=$S/work/$name; mkdir -p "$W"
strace -f -y -s 300 -e trace=%file,%desc,%process,%signal -o "$S/strace/$name.strace" \
  python3 "$fx" --tool "$LANE/tools/souji-worktree-drift.py" --work "$W" >"$S/strace/$name.stdout" 2>"$S/strace/$name.stderr" &
SPID=$!
FXPID=""
for _ in $(seq 1 2000); do
  FXPID=$(pgrep -P "$SPID" -x python3 | head -1)
  if [ -n "$FXPID" ] && [ -n "$(pgrep -P "$FXPID" | head -1)" ]; then break; fi
  sleep 0.01
done
echo "$name fixture-pid=$FXPID SigIgn=$(grep SigIgn /proc/$FXPID/status | awk '{print $2}') SigCgt=$(grep SigCgt /proc/$FXPID/status | awk '{print $2}')"
kill -INT "$FXPID"
wait "$SPID"; echo "$name strace-wrapper-rc=$?"
sleep 1
echo "$name leftover-entries-in-work=$(find "$W" -mindepth 1 | wc -l)"
echo "$name tool-children-still-alive=$(pgrep -fc "souji-worktree-drift.py --root $W")"
grep -c "SIGINT" "$S/strace/$name.strace"
grep "SIGINT" "$S/strace/$name.strace" | head -3 | cut -c1-200
cat "$S/strace/$name.stdout" | tail -3
