#!/usr/bin/env bash
set -u
S=/fast/scratch/hyaku/souji-r74/S74MutGate
L=/home/vgpnk/Projects/shokunin/souji-shokunin
id=$1
cd "$L" || exit 9
mkdir -p "$S/w" "$S/out"
python3 -B census/round-74/c1-gate-counter.py --gate "$S/m/$id/gate.sh" --work "$S/w/$id" > "$S/out/$id.txt" 2>&1
echo "$id rc=$?"
