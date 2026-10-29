#!/usr/bin/env bash
# run.sh <counter.py> <tool-rel-path> <tag>  -> $S/out/<tag>.{out,err,rc}
set -u
S=/fast/scratch/hyaku/souji-r42/R42mutationtester02; C=$S/clone; REV=afe17f416eec04dcf3f480b580a8f928de61d19d
mkdir -p "$S/out" "$S/run/$3"
export TMPDIR="$S/run/$3"
python3 -B "$1" --root "$C" --rev "$REV" --scratch "$S/run/$3" --tool "$2" >"$S/out/$3.out" 2>"$S/out/$3.err"; echo $? >"$S/out/$3.rc"
rm -rf "$S/run/$3"
