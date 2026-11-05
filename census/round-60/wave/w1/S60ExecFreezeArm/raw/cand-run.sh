#!/bin/bash
# S60ExecFreezeArm — run candidate + base over selftests and three real preregistrations; write receipts.
set -u
S=/fast/scratch/hyaku/souji-r60/S60ExecFreezeArm
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
REV=1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4
W="$S/work"; O="$S/out"
D="$LANE/.ufo/waves/round-60/w1/S60ExecFreezeArm"
mkdir -p "$O" "$S/tmp" "$D"
export TMPDIR="$S/tmp"
CAND="$W/souji-freeze-check.py"
BASE="$W/base.py"
cd "$S" || exit 9

echo "== candidate sha256"; sha256sum "$CAND"
echo "== base sha256"; sha256sum "$BASE"

python3 -B "$CAND" --selftest > "$O/cand-selftest-default.out" 2> "$O/cand-selftest-default.err"
echo "cand selftest default exit=$?"
python3 -B "$CAND" --selftest --substance > "$O/cand-selftest-substance.out" 2> "$O/cand-selftest-substance.err"
echo "cand selftest substance exit=$?"

echo "== default selftest stdout (cand vs base)"
cmp "$O/cand-selftest-default.out" "$O/base-selftest.out" && echo "selftest stdout identical to base"
cmp "$O/cand-selftest-default.err" "$O/base-selftest.err" && echo "selftest stderr identical to base"

for r in 59 58 57; do
  argv=(--root "$LANE" --prereg "census/round-$r/preregistration.txt" --rev "$REV")
  python3 -B "$CAND" "${argv[@]}" > "$O/cand-r$r.out" 2> "$O/cand-r$r.err"; cr=$?
  python3 -B "$CAND" "${argv[@]}" --substance > "$O/cand-sub-r$r.out" 2> "$O/cand-sub-r$r.err"; cs=$?
  echo "r$r cand exit=$cr base-exit=$(cat "$O/base-r$r.err" >/dev/null; echo see-below) cand-substance exit=$cs"
  cmp "$O/cand-r$r.out" "$O/base-r$r.out" && echo "r$r stdout identical to base"
  cmp "$O/cand-r$r.err" "$O/base-r$r.err" && echo "r$r stderr identical to base"
done
