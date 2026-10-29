#!/usr/bin/env bash
# extra invocations the scored harness never makes; tool = tools/souji-freeze-check.py at REV unless stated
set -u
S=/fast/scratch/hyaku/souji-r42/R42mutationtester02; C=$S/clone; REV=afe17f416eec04dcf3f480b580a8f928de61d19d
W=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester02/mutants
ORIG=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester02/c2-counter.py
SCR=$S/run/probe-scratch; mkdir -p "$S/out" "$SCR"
run() { # tag counter args...
  tag=$1; cnt=$2; shift 2
  python3 -B "$cnt" "$@" >"$S/out/probe-$tag.out" 2>"$S/out/probe-$tag.err"; echo $? >"$S/out/probe-$tag.rc"
}
run orig-default-tool "$ORIG" --root "$C" --rev "$REV" --scratch "$SCR"
run M102-default-tool "$W/M102.py" --root "$C" --rev "$REV" --scratch "$SCR"
run orig-shortrev "$ORIG" --root "$C" --rev afe17f4 --scratch "$SCR"
run M100-shortrev "$W/M100.py" --root "$C" --rev afe17f4 --scratch "$SCR"
run orig-absent-tool "$ORIG" --root "$C" --rev "$REV" --tool tools/no-such-tool.py --scratch "$SCR"
run M98-absent-tool "$W/M98.py" --root "$C" --rev "$REV" --tool tools/no-such-tool.py --scratch "$SCR"
run orig-badscratch "$ORIG" --root "$C" --rev "$REV" --scratch "$S/no-such-dir"
run M99-badscratch "$W/M99.py" --root "$C" --rev "$REV" --scratch "$S/no-such-dir"
echo PROBES_DONE
