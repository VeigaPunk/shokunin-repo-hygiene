#!/usr/bin/env bash
# usage: shimrun.sh <fixture> <name>; runs a fixture against the logging shim in its own dir
set -u
d="$(mktemp -d -p "/fast/scratch/hyaku/souji-r42/R42critic05" shim.XXXXXX)"
cp "/fast/scratch/hyaku/souji-r42/R42critic05/shimdir/pristine.py" "/fast/scratch/hyaku/souji-r42/R42critic05/shimdir/mut-SHIM.py" "$d/"
w="$(mktemp -d -p "/fast/scratch/hyaku/souji-r42/R42critic05" work.XXXXXX)"
python3 -B "$1" --tool "$d/mut-SHIM.py" --work "$w" > "/fast/scratch/hyaku/souji-r42/R42critic05/shim-$2.out" 2> "/fast/scratch/hyaku/souji-r42/R42critic05/shim-$2.err"; rc=$?
n=$(cat "$d/shim.log" 2>/dev/null | wc -l)
echo "$2 rc=$rc tool_invocations=$n" > "/fast/scratch/hyaku/souji-r42/R42critic05/shim-$2.sum"
rm -rf "$d" "$w"
