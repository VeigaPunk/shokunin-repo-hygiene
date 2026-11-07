#!/bin/bash
# S80Sentinel unit repro: q_kill_session/q_proc_sid trust the *session id* alone.
# (a) it kills a session it was not told to own (a session this script started), and
# (b) it returns 0 and kills nothing when the sid's leader is already gone.
set -u
. /fast/scratch/hyaku/souji-r80/S80Sentinel/funcs.sh

# (a) an unrelated session (started by this test, never by the tool)
setsid sleep 300 &
victim=$!
sleep 0.2
q_proc_sid "$victim" && echo "victim=$victim sid=$Q_SID (leader=$([ "$Q_SID" = "$victim" ] && echo yes || echo no))"
q_kill_session "$victim"
sleep 0.2
if kill -0 "$victim" 2>/dev/null; then echo "A: victim SURVIVED"; else echo "A: victim killed by sid alone = yes"; fi

# (b) a stale sid: start a leader, kill and reap it
setsid sleep 300 &
stale=$!
sleep 0.2
kill -KILL "$stale" 2>/dev/null
wait "$stale" 2>/dev/null
q_kill_session "$stale"
echo "B: q_kill_session(dead sid=$stale) rc=$?"
