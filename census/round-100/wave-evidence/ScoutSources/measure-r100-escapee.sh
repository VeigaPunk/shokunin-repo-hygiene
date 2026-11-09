#!/bin/bash
# ScoutSources (souji r100): focused ESCAPEE-ALIVE measurement for the r100 counter.
# Mirrors census/round-99/c2-measure.sh's escapee() helper exactly: after the counter
# exits, count live processes whose argv carries that run's own T1 token
# (<work>/arms/fixture-pipe-holder.py).
#
# Usage: measure-r100-escapee.sh <counter-path> <label>
# Writes to $SCRATCH (must be set) and prints the receipt lines.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
COUNTER=${1:?counter path}
LABEL=${2:?label}
S=${SCRATCH:?set SCRATCH}
OUT="$S/out"
mkdir -p "$OUT"
cd "$LANE" || exit 2
FPASS=tests/fixtures/r93-k4-flagfail.py
FFAIL=tests/fixtures/r92-k4-flagfail.py
PROBE=census/round-98/c2-forgery-probe.py
TOOL=tools/souji-record-agreement.py
BEFORE=census/round-92/controls/c2-before-tool.py

escapee() { # $1=counter work dir
  local tok="$1/fixture-pipe-holder.py" n=0 p
  for p in /proc/[0-9]*; do
    if tr '\0' '\n' < "$p/cmdline" 2>/dev/null | grep -qxF -- "$tok"; then n=$((n+1)); fi
  done
  echo "ESCAPEE-ALIVE token=$tok alive=$n"
}

W="$S/$LABEL-work"
rm -rf "$W"; mkdir -p "$W"
{
  echo "## counter=$COUNTER label=$LABEL"
  python3 -B "$COUNTER" --probe "$PROBE" --fixture-pass "$FPASS" --fixture-fail "$FFAIL" \
    --tool "$TOOL" --before "$BEFORE" --work "$W/arms" --jobs 4 --arm-timeout 200
  echo "COUNTER-EXIT=$?"
  escapee "$W/arms"
} > "$OUT/c2-counter-$LABEL.txt" 2>&1

grep -E "^ARM T1|^ARMS-SUMMARY|^COUNTER-EXIT|^ESCAPEE-ALIVE" "$OUT/c2-counter-$LABEL.txt"
echo "RECEIPT=$OUT/c2-counter-$LABEL.txt"
