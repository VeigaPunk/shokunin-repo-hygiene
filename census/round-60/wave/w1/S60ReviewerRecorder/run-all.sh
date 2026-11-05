#!/usr/bin/env bash
# S60ReviewerRecorder: reproduce every C2 measurement in the report.
# All fixtures live under a scratch dir created here; the lane is read-only (git plumbing only).
set -u
DELIV=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-60/w1/S60ReviewerRecorder
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
BASE=$LANE/census/round-57/record-receipt.sh
GATE=$LANE/census/round-58/c2-gate.py
CAND=$DELIV/cand-souji-receipt-write.py
REF=$DELIV/ref-writer.py
SCR=/fast/scratch/hyaku/souji-r60/S60ReviewerRecorder
mkdir -p "$SCR" && S=$(mktemp -d -p "$SCR") && trap 'rm -rf -- "$S"' EXIT
LOGS=$DELIV/logs; mkdir -p "$LOGS"
cd "$DELIV" || exit 2
step() { local name=$1; shift; "$@" > "$LOGS/$name.txt" 2>&1; echo "STEP $name rc=$?"; }

step eight-base   python3 harness.py eight --tool "$BASE" --mode base --work "$(mktemp -d -p "$S")"
step eight-ref    python3 harness.py eight --tool "$REF"  --mode cand --work "$(mktemp -d -p "$S")"
step eight-cand   python3 harness.py eight --tool "$CAND" --mode cand --work "$(mktemp -d -p "$S")"
step selftest-cand-own python3 "$CAND" --selftest --work "$(mktemp -d -p "$S")"
step attacks-base python3 attacks2.py --tool "$BASE" --work "$(mktemp -d -p "$S")" --gate "$GATE"
step attacks-ref  python3 attacks2.py --tool "$REF"  --work "$(mktemp -d -p "$S")" --gate "$GATE"
step attacks-cand python3 attacks2.py --tool "$CAND" --work "$(mktemp -d -p "$S")" --gate "$GATE"
step extra-base   python3 extra.py "$BASE" "$(mktemp -d -p "$S")" "$GATE"
step extra-ref    python3 extra.py "$REF"  "$(mktemp -d -p "$S")" "$GATE"
step extra-cand   python3 extra.py "$CAND" "$(mktemp -d -p "$S")" "$GATE"
step toctou-cand  python3 harness.py probe --tool "$CAND" --mode cand --work "$(mktemp -d -p "$S")" --probe toctou
step toctou-ref   python3 harness.py probe --tool "$REF"  --mode cand --work "$(mktemp -d -p "$S")" --probe toctou
step sibling-vs-cand    python3 -B sibling-fixture-as-delivered.py --tool "$CAND" --work "$(mktemp -d -p "$S")/fx"
step sibling-vs-base    python3 -B sibling-fixture-as-delivered.py --tool "$BASE" --work "$(mktemp -d -p "$S")/fx"
step sibling-vs-nonatomic python3 -B sibling-fixture-as-delivered.py --tool "$DELIV/nonatomic-stub.py" --work "$(mktemp -d -p "$S")/fx"
step keeponly-allowdirty-cand python3 keeponly-allowdirty.py "$CAND" "$(mktemp -d -p "$S")" "$GATE"
step e3-isolated-cand   python3 e3-isolated.py "$CAND" "$(mktemp -d -p "$S")"
step e3-isolated-ref    python3 e3-isolated.py "$REF"  "$(mktemp -d -p "$S")"
echo "SCRATCH-REMOVED-ON-EXIT $S"
