#!/bin/bash
# verbatim copy of q_proc_sid + q_kill_session from 836dac3e tools/souji-quarantine.sh lines 185-207
q_proc_sid() { # $1 pid -> Q_SID = session id (field 6 of /proc/<pid>/stat, after the parenthesised comm); no fork
  local st f
  Q_SID=
  { read -r st < "/proc/$1/stat"; } 2>/dev/null || return 1
  st=${st##*) }
  read -r -a f <<< "$st"
  Q_SID=${f[3]:-}
  [ -n "$Q_SID" ]
}
q_kill_session() { # $1 session id: SIGSTOP, then SIGKILL, every process in it; repeat until none is left
  local sid=$1 p pass pids
  for pass in 1 2 3 4 5 6 7 8; do
    pids=()
    for p in /proc/[0-9]*; do
      p=${p#/proc/}
      q_proc_sid "$p" && [ "$Q_SID" = "$sid" ] && pids+=("$p")
    done
    [ "${#pids[@]}" -gt 0 ] || return 0
    kill -STOP "${pids[@]}" 2>/dev/null || true
    kill -KILL "${pids[@]}" 2>/dev/null || true
  done
  return 0
}
