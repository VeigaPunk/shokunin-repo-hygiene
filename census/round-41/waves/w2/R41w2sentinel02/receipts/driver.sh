#!/bin/bash
# Scratch driver for R41w2sentinel02 (safety review). Writes only under $S.
set -u
S=/fast/scratch/hyaku/souji-r41/R41w2sentinel02
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
TOOL=$LANE/tools/souji-worktree-drift.py
FX1=$LANE/tests/fixtures/r41-refusal-sites.py
FX2=$LANE/tests/fixtures/r41-drift-record-order.py
export TMPDIR=$S/tmp
STRACE_FLAGS=(-f -y -s 300 -e trace=%file,%desc,%process,%signal)

# $1 = name, $2 = fixture, extra args after
run_full() {
  local name=$1 fx=$2; shift 2
  local W=$S/work/$name
  mkdir -p "$W"
  strace "${STRACE_FLAGS[@]}" -o "$S/strace/$name.strace" \
    python3 "$fx" --tool "$TOOL" --work "$W" "$@" \
    >"$S/strace/$name.stdout" 2>"$S/strace/$name.stderr"
  echo "$name rc=$?"
  echo "$name leftover-entries-in-work=$(find "$W" -mindepth 1 | wc -l)"
}

# $1 = name, $2 = fixture ; SIGTERM the fixture python while a child tool process is live
run_term() {
  local name=$1 fx=$2
  local W=$S/work/$name
  mkdir -p "$W"
  strace "${STRACE_FLAGS[@]}" -o "$S/strace/$name.strace" \
    python3 "$fx" --tool "$TOOL" --work "$W" \
    >"$S/strace/$name.stdout" 2>"$S/strace/$name.stderr" &
  local SPID=$!
  local FXPID=""
  for _ in $(seq 1 2000); do
    FXPID=$(pgrep -P "$SPID" -x python3 | head -1)
    if [ -n "$FXPID" ] && [ -n "$(pgrep -P "$FXPID" | head -1)" ]; then break; fi
    sleep 0.01
  done
  echo "$name fixture-pid=$FXPID child-live=$(pgrep -P "$FXPID" | wc -l)"
  kill -TERM "$FXPID"
  wait "$SPID"
  echo "$name strace-wrapper-rc=$?"
  sleep 1
  echo "$name orphan-tool-children-after-1s=$(pgrep -fc "souji-worktree-drift.py --root $W")"
  echo "$name leftover-entries-in-work=$(find "$W" -mindepth 1 | wc -l)"
  find "$W" -mindepth 1 -printf '%M %m %p\n' | head -40
}

case "$1" in
  full1) run_full r41-refusal-sites "$FX1" ;;
  full2) run_full r41-drift-record-order "$FX2" ;;
  term1) run_term term-refusal-sites "$FX1" ;;
  term2) run_term term-drift-record-order "$FX2" ;;
esac
