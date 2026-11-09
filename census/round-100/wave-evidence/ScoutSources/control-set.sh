#!/bin/bash
# ScoutSources (souji r100): control set for the C1 escapee finding.
#
# Runs, SEQUENTIALLY (quiet host, one counter at a time), each counter through the
# same escapee measurement helper as census/round-99/c2-measure.sh:
#   after the counter exits, count live processes whose argv carries that run's own
#   T1 token (<work>/arms/fixture-pipe-holder.py).
#
#   r98    expected alive=0  (known-good: subreaper branch (c) owns the escapee)
#   r99    expected alive=1  (the r99 do-nothing baseline)
#   r100   expected alive=0  (the frozen C1 target)
#   m_noppid expected alive=0 -> MUST FAIL (the C1 mutant claim)
#
# Usage: control-set.sh <scratchdir>
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
S=${1:?scratch dir}
OUT="$S/out"
mkdir -p "$OUT"
cd "$LANE" || exit 2
FPASS=tests/fixtures/r93-k4-flagfail.py
FFAIL=tests/fixtures/r92-k4-flagfail.py
PROBE=census/round-98/c2-forgery-probe.py
TOOL=tools/souji-record-agreement.py
BEFORE=census/round-92/controls/c2-before-tool.py

escapee() {
  local tok="$1/fixture-pipe-holder.py" n=0 p
  for p in /proc/[0-9]*; do
    if tr '\0' '\n' < "$p/cmdline" 2>/dev/null | grep -qxF -- "$tok"; then n=$((n+1)); fi
  done
  echo "ESCAPEE-ALIVE token=$tok alive=$n"
}

run() { # $1=label $2=counter path
  local label="$1"
  local counter="$2"
  local W="$S/$label-work"
  rm -rf "$W"; mkdir -p "$W"
  {
    echo "## counter=$counter label=$label"
    python3 -B "$counter" --probe "$PROBE" --fixture-pass "$FPASS" --fixture-fail "$FFAIL" \
      --tool "$TOOL" --before "$BEFORE" --work "$W/arms" --jobs 4 --arm-timeout 200
    echo "COUNTER-EXIT=$?"
    escapee "$W/arms"
  } > "$OUT/c2-counter-$label.txt" 2>&1
  echo "=== $label ==="
  grep -E "^ARM T1|^ARMS-SUMMARY|^COUNTER-EXIT|^ESCAPEE-ALIVE" "$OUT/c2-counter-$label.txt"
}

run r98    census/round-98/c2-setup-arms.py
run r99    census/round-99/c2-setup-arms.py
run r100   census/round-100/c2-setup-arms.py
run m_noppid "$S/mutants/c2-m-noppid.py"
echo "CONTROL-SET-DONE"
