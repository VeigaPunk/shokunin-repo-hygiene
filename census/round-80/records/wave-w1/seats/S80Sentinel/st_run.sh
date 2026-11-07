#!/bin/bash
# Run the committed tool's --selftest with a scratch TMPDIR; sample the private dir at 4 s.
set -u
S=/fast/scratch/hyaku/souji-r80/S80Sentinel
T="$S/st-tmp"
rm -rf "$T"; mkdir -p "$T"
cd /home/vgpnk/Projects/shokunin/souji-shokunin || exit 1
TMPDIR="$T" bash tools/souji-quarantine.sh --selftest > "$S/st.out" 2>&1 &
p=$!
sleep 4
echo "=== TMPDIR at 4s:"
ls -la "$T"
for d in "$T"/souji-quarantine.*/; do
  [ -d "$d" ] || continue
  echo "=== inside ${d}:"
  ls -la "$d" | head -20
  for e in "$d"*/; do [ -d "$e" ] && { echo "--- $e"; ls "$e" | head -8; }; done
done
wait "$p"; rc=$?
echo "=== selftest rc=$rc"
echo "=== TMPDIR after:"
ls -la "$T"
[ -f "$S/st.out" ] && tail -4 "$S/st.out"
