#!/bin/bash
set -u
q_proc_sid() { local st f; Q_SID=
  { read -r st < "/proc/$1/stat"; } 2>/dev/null || return 1
  st=${st##*) }; read -r -a f <<< "$st"; Q_SID=${f[3]:-}; [ -n "$Q_SID" ]; }
q_kill_session() { local sid=$1 p pass pids; local passes=0
  for pass in 1 2 3 4 5 6 7 8; do
    pids=()
    for p in /proc/[0-9]*; do p=${p#/proc/}; q_proc_sid "$p" && [ "$Q_SID" = "$sid" ] && pids+=("$p"); done
    [ "${#pids[@]}" -gt 0 ] || { echo "passes=$passes members_last=0" >&2; return 0; }
    passes=$pass; echo "pass=$pass members=${#pids[@]}" >&2
    kill -STOP "${pids[@]}" 2>/dev/null || true; kill -KILL "${pids[@]}" 2>/dev/null || true
  done
  echo "passes=$passes members_last=${#pids[@]}" >&2; return 0; }
n=$(ls -d /proc/[0-9]* | wc -l); echo "proc_entries=$n"
setsid sleep 600 & p=$!
sleep 0.3
t0=$(date +%s%N); q_kill_session "$p"; t1=$(date +%s%N)
echo "elapsed_ms=$(( (t1-t0)/1000000 )) target_pid=$p"
wait "$p" 2>/dev/null; echo "reaped rc=$?"
