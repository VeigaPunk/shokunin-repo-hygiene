#!/bin/bash
# S60ExecFreezeArm — extract base tool at the pinned rev, check work-tree parity, run base tool.
# Read-only git in the lane (cat-file only). All writes go to this seat's scratch.
set -u
S=/fast/scratch/hyaku/souji-r60/S60ExecFreezeArm
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
REV=1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4
W="$S/work"; O="$S/out"
mkdir -p "$W" "$O" "$S/tmp"
export TMPDIR="$S/tmp"

git -C "$LANE" cat-file blob "$REV:tools/souji-freeze-check.py" > "$W/base.py" || { echo "EXTRACT FAIL"; exit 9; }
sha256sum "$W/base.py"
wc -l "$W/base.py"
if diff -q "$W/base.py" "$LANE/tools/souji-freeze-check.py" >/dev/null; then
  echo "worktree==base-rev bytes: YES"
else
  echo "worktree==base-rev bytes: NO"
  diff "$W/base.py" "$LANE/tools/souji-freeze-check.py" | head -20
fi

python3 -B "$W/base.py" --selftest > "$O/base-selftest.out" 2> "$O/base-selftest.err"
echo "base-selftest exit=$?"
for r in 59 58 57; do
  argv=(--root "$LANE" --prereg "census/round-$r/preregistration.txt" --rev "$REV")
  echo "argv: python3 -B $W/base.py ${argv[*]}"
  python3 -B "$W/base.py" "${argv[@]}" > "$O/base-r$r.out" 2> "$O/base-r$r.err"
  echo "base-r$r exit=$?"
done
