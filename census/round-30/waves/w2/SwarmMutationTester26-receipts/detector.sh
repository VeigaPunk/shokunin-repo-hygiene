#!/usr/bin/env bash
# Bounded behavioral detector for seat SwarmMutationTester26 (r30 w2).
# Replicates exactly two frozen legs against the fixture bytes currently at
# c/tests/fixtures/r30-jj-keep-expiry.sh:
#   E3 (census/round-30/c3-counter-v2.py:61-77): run `bash FIX` with cwd=clone root,
#      TMPDIR under scratch; exit 0 AND its jj-version:/git-version:/RESULT  lines
#      equal, in order, those of census/round-30/records/jj-keep-expiry-run.txt@TIP.
#   L8 (census/round-30/c3-counter.py:118-123): committed record at TIP has a line
#      starting `jj-version: jj 0.45.1` and >= 3 `RESULT ` lines; ENTRY names the
#      record path and contains `refs/jj/keep` and `util gc`.
# Usage: detector.sh <label>
set -u
S=/fast/scratch/hyaku/souji-r30/MutateJjFixture
C=$S/c
TIP=9dcd367655fc28ba73d679a0e2cadaff96d2bcb8
FIX=tests/fixtures/r30-jj-keep-expiry.sh
RUN=census/round-30/records/jj-keep-expiry-run.txt
ENTRY=corpus/knowledge/jj-keep-ref-expiry.md
LABEL=$1
mkdir -p "$S/out" "$S/tmp"
export TMPDIR=$S/tmp
OUT=$S/out/$LABEL

git -C "$C" cat-file blob "$TIP:$RUN"  > "$OUT.record" 2>/dev/null
git -C "$C" cat-file blob "$TIP:$ENTRY" > "$OUT.entry" 2>/dev/null

cd "$C" || exit 9
bash "$FIX" >"$OUT.out" 2>"$OUT.err"
rc=$?

awk '/^(jj-version:|git-version:|RESULT )/' "$OUT.out"    > "$OUT.kept"
awk '/^(jj-version:|git-version:|RESULT )/' "$OUT.record" > "$OUT.rec.kept"

e3=FAIL
if [ "$rc" -eq 0 ] && [ -s "$OUT.kept" ] && cmp -s "$OUT.kept" "$OUT.rec.kept"; then e3=PASS; fi

nres=$(grep -c '^RESULT ' "$OUT.rec.kept")
ok8=FAIL
if grep -qF "$RUN" "$OUT.entry" \
   && grep -q '^jj-version: jj 0.45.1' "$OUT.rec.kept" \
   && [ "$nres" -ge 3 ] \
   && grep -qF 'refs/jj/keep' "$OUT.entry" \
   && grep -qF 'util gc' "$OUT.entry"; then ok8=PASS; fi

echo "DETECTOR label=$LABEL rc=$rc E3=$e3 L8=$ok8 kept=$(wc -l <"$OUT.kept") rec_kept=$(wc -l <"$OUT.rec.kept")"
if [ "$e3" = FAIL ]; then
  echo "--- first differences (record vs replay) ---"
  diff "$OUT.rec.kept" "$OUT.kept" | head -24
fi
