#!/usr/bin/env bash
# r31 L1 amended controls (A1 C3 v3, A2 C1 count shape, A3 C2 v2 SHIFT): junk states from the wave-1 attacks, scored
# with the frozen v1 counters and the stricter amended ones. Scratch clone only (origin removed). TSV on stdout.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FLEET=/home/vgpnk/Projects/shokunin
B=9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
P=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
SCR=${HYAKU_SCRATCH:-/fast/scratch/hyaku}/souji-r31/L1controls-amended
mkdir -p "$SCR"; D=$(mktemp -d "$SCR/ctl.XXXXXX") || exit 2
trap 'rm -rf -- "$D"' EXIT
git clone -q --no-local "$LANE" "$D/c" || exit 2
C="$D/c"; git -C "$C" remote remove origin
[ "$(git -C "$C" rev-parse --show-toplevel)" = "$C" ] || { echo "toplevel mismatch"; exit 2; }
g() { git -C "$C" -c user.name=ctl -c user.email=ctl@localhost -c core.hooksPath=/dev/null "$@"; }
git -C "$LANE" show $P:tools/souji-capability-cells.py > "$D/c1-v1.py"
c1v1() { python3 -B "$D/c1-v1.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" --only "$2" 2>&1 | grep '^SUMMARY'; }
c1a2() { python3 -B "$LANE/tools/souji-capability-cells.py" --root "$C" --rev "$1" --base $B --list-rev $P --scratch "$D/s1" --only "$2" 2>&1 | grep '^SUMMARY'; }
c2v2() { python3 -B "$LANE/census/round-31/c2-counter-v2.py" --root "$C" --rev "$1" --base $B --fleet-root $FLEET --scratch "$D/s2" 2>&1 | grep -E '^SHIFT|^SUMMARY' | tr '\n' ' '; }
printf 'control\tcounter\tresult\n'
# C1 junk (SwarmCritic31 finding 2): record binding to non-count text that carries the base integers
g checkout -q --detach $P
REC=$C/census/round-16/run-matrix.py   # SwarmCritic31 probe B: a matrix arm id at run-matrix.py:77, not a count
printf '\n### control\n\n| item | base line | literal | binding | reason |\n|---|---|---|---|---|\n| L07 | SCORECARD.md:158 | 15-config": LANE / "tests/fixtures/r15 | record: %s | junk |\n' "${REC#$C/}" >> "$C/SCORECARD.md"
g commit -qam junk-a2; J=$(g rev-parse HEAD)
printf 'C1-junk-A2(non-count literal, record %s)\tc1-v1\t%s\n' "${REC#$C/}" "$(c1v1 $J L07)"
printf 'C1-junk-A2(non-count literal, record %s)\tc1-a2\t%s\n' "${REC#$C/}" "$(c1a2 $J L07)"
# C2: the base gate (what a replay-by-revision or base-token allowlist gate does on unseen tokens) under v2 SHIFT
printf 'C2-do-nothing(base gate) under A3 SHIFT\tc2-v2\t%s\n' "$(c2v2 $P)"
