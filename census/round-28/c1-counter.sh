#!/usr/bin/env bash
# souji round 28 C1 frozen counter wrapper (receipt-bound).
# Usage: c1-counter.sh <full40-rev> [label]
#
# Runs the frozen landing-gate counter for a caller-supplied revision:
#   python3 -B tools/souji-landing-gate.py --root <lane> --rev <full40>
#     --round 28 --fleet-root <fleet>
# prints the SUMMARY line and the exit code, and writes a receipt
# census/round-28/records/c1-<label>.tsv holding the gate's finding lines,
# SUMMARY line, stderr (COULD-NOT-EVALUATE), and c1_rc=<exit code>.
# Deterministic: python3 -B, LC_ALL=C, cwd pinned to the lane, no network.
set -u
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
FLEET=/home/vgpnk/Projects/shokunin
export LC_ALL=C

rev=${1:-}
label=${2:-run}
if ! [[ $rev =~ ^[0-9a-f]{40}$ ]]; then
    echo "c1-counter.sh: first argument must be a full 40-hex revision" >&2
    exit 2
fi

cd "$LANE" || exit 2
mkdir -p "$LANE/census/round-28/records" || exit 2
receipt="$LANE/census/round-28/records/c1-$label.tsv"

scratch=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-c1-counter.XXXXXX") || exit 2
trap 'rm -rf "$scratch"' EXIT

python3 -B tools/souji-landing-gate.py \
    --root "$LANE" --rev "$rev" --round 28 --fleet-root "$FLEET" \
    > "$scratch/out" 2> "$scratch/err"
rc=$?

# Receipt: stdout (findings + SUMMARY) then stderr (COULD-NOT-EVALUATE) then rc.
cat "$scratch/out" "$scratch/err" > "$receipt"
printf 'c1_rc=%s\n' "$rc" >> "$receipt"

awk '/^SUMMARY/{print}' "$scratch/out"
printf 'c1_rc=%s\n' "$rc"
exit $rc
