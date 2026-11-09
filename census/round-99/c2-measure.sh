#!/bin/bash
# souji r99 C2 measurement (L1). Run from the lane root. Receipts under census/round-99/records/.
# Each counter run gets its own fresh --work under the L1 scratch so argv reap tokens never collide with
# other seats' runs. Escapee check: after the counter exits, count live processes whose argv carries that
# run's own T1 token (<work>/arms/fixture-pipe-holder.py).
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
cd "$LANE" || exit 2
S=/fast/scratch/hyaku/souji-r99/L1/c2
OUT=census/round-99/records
mkdir -p "$OUT" "$S"
FPASS=tests/fixtures/r93-k4-flagfail.py
FFAIL=tests/fixtures/r92-k4-flagfail.py
PROBE=census/round-98/c2-forgery-probe.py
TOOL=tools/souji-record-agreement.py
BEFORE=census/round-92/controls/c2-before-tool.py

escapee() { # $1=counter work dir (the --work passed to the counter); prints live T1 carriers of this run
  local tok="$1/fixture-pipe-holder.py" n=0 p
  for p in /proc/[0-9]*; do
    if tr '\0' '\n' < "$p/cmdline" 2>/dev/null | grep -qxF -- "$tok"; then n=$((n+1)); fi
  done
  echo "ESCAPEE-ALIVE token=$tok alive=$n"
}

run_counter() { # $1=label $2=counter path
  local label="$1" counter="$2" W="$S/$1-work"
  rm -rf "$W"; mkdir -p "$W"
  {
    echo "## counter=$counter label=$label"
    python3 -B "$counter" --probe "$PROBE" --fixture-pass "$FPASS" --fixture-fail "$FFAIL" \
      --tool "$TOOL" --before "$BEFORE" --work "$W/arms" --jobs 4 --arm-timeout 200
    echo "COUNTER-EXIT=$?"
    escapee "$W/arms"   # FIXED r99 L1: prints token $W/arms/fixture-pipe-holder.py (earlier build doubled /arms)
  } > "$OUT/c2-counter-$label.txt" 2>&1
}

run_decoy() { # $1=label $2=counter path
  local label="$1" counter="$2" W="$S/decoy-$1"
  rm -rf "$W"; mkdir -p "$W"
  python3 -B census/round-99/c2-decoy-test.py --counter "$counter" --probe "$PROBE" --tool "$TOOL" \
    --before "$BEFORE" --work "$W" --arm-timeout 200 --plant-delay 2 > "$OUT/c2-decoy-$label.txt" 2>&1
  echo "DECOY-EXIT=$?" >> "$OUT/c2-decoy-$label.txt"
}

run_decoy r99 census/round-99/c2-setup-arms.py
run_decoy r98 census/round-98/c2-setup-arms.py
run_decoy r97 census/round-97/c2-setup-arms.py
run_decoy cm8 census/round-98/c2-cm8-mutant.py
run_counter r99 census/round-99/c2-setup-arms.py
run_counter r98 census/round-98/c2-setup-arms.py
run_counter r97 census/round-97/c2-setup-arms.py
echo DONE
