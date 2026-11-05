#!/usr/bin/env bash
# usage: run-receipt.sh NAME TOOL FIXTURE TAG
# Runs FIXTURE (python3 -B) against TOOL in a fresh --work dir, then writes a receipt:
# mutant sha256, exact command, combined output, EXIT=<rc>. Work dir removed after the receipt.
set -u
name=$1; tool=$2; fixture=$3; tag=$4
S=/fast/scratch/hyaku/souji-r61/S61MutationCounter
D=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-61/w1/S61MutationCounter/receipts
mkdir -p "$D" "$S/work"
work=$(mktemp -d -p "$S/work" "$name.$tag.XXXX")
sha=$(sha256sum "$tool" | cut -d' ' -f1)
fsha=$(sha256sum "$fixture" | cut -d' ' -f1)
cmd="python3 -B $fixture --tool $tool --work $work"
out=$(cd "$S" && python3 -B "$fixture" --tool "$tool" --work "$work" 2>&1)
rc=$?
{
  echo "mutant=$name"
  echo "mutant_sha256=$sha"
  echo "fixture=$fixture"
  echo "fixture_sha256=$fsha"
  echo "command=$cmd"
  echo "output:"
  echo "$out"
  echo "EXIT=$rc"
} > "$D/$name.$tag.txt"
rm -rf -- "$work"
echo "$name [$tag] rc=$rc"
echo "$out" | grep -E '^(CASE|SUMMARY|# control)' || true
