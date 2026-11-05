#!/usr/bin/env bash
# usage: run-c1.sh NAME NEWTOOL
# Runs the frozen C1 matrix counter (snapshot in c1lane/) with NEWTOOL in the NEW slot and writes a
# receipt: tool sha256, exact command, combined output, EXIT=<rc>.
set -u
name=$1; newtool=$2
S=/fast/scratch/hyaku/souji-r61/S61MutationCounter
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
REV=c7228424c3919ecf142bab1aec8181722d86467b
D=$LANE/.ufo/waves/round-61/w1/S61MutationCounter/receipts
mkdir -p "$D" "$S/work"
work="$S/work/c1-$name"
rm -rf -- "$work"; mkdir -p "$work"
sha=$(sha256sum "$newtool" | cut -d' ' -f1)
cmd="python3 -B c1-counter.py --root $LANE --matrix c1-matrix.tsv --base-tool-rev $REV --rev $REV --work $work --new-tool $newtool"
out=$(cd "$S/c1lane" && python3 -B c1-counter.py --root "$LANE" --matrix c1-matrix.tsv --base-tool-rev "$REV" --rev "$REV" --work "$work" --new-tool "$newtool" 2>&1)
rc=$?
{
  echo "mutant=$name"
  echo "new_tool_sha256=$sha"
  echo "counter_sha256=$(sha256sum "$S/c1lane/c1-counter.py" | cut -d' ' -f1)"
  echo "matrix_sha256=$(sha256sum "$S/c1lane/c1-matrix.tsv" | cut -d' ' -f1)"
  echo "command=$cmd"
  echo "output:"
  echo "$out"
  echo "EXIT=$rc"
} > "$D/c1-$name.txt"
echo "$name rc=$rc"
echo "$out" | grep -E '^(SUMMARY|EXIT)|^CASE' | grep -v 'new_findings=\(.*\) expected_class=\1$' || true
echo "$out" | grep -E '^SUMMARY'
rm -rf -- "$work"
