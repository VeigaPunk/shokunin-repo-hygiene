#!/bin/bash
# souji r99 escapee check: live processes whose argv carries a counter run's T1 token after the counter exited.
# usage: c2-escapee-check.sh <scratch-root-with-<label>-work-dirs>  (labels r99 r98 r97)
set -u
ROOT="$1"
for run in r99 r98 r97; do
  tok="$ROOT/$run-work/arms/fixture-pipe-holder.py"; n=0
  for p in /proc/[0-9]*; do
    if tr '\0' '\n' < "$p/cmdline" 2>/dev/null | grep -qxF -- "$tok"; then
      n=$((n+1)); echo "  pid=${p#/proc/} stat=$(cut -d' ' -f3 "$p/stat" 2>/dev/null) ppid=$(cut -d' ' -f4 "$p/stat" 2>/dev/null)"
    fi
  done
  echo "ESCAPEE-ALIVE run=$run alive=$n token=$tok"
done
