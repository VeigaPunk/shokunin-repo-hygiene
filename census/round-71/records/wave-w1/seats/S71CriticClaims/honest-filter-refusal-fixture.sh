#!/usr/bin/env bash
# S71CriticClaims — the landed r71 C1 design refuses a repository that legitimately configures a
# clean filter on a CLEAN tree (MEDIUM finding: unmeasured over-refusal shape). Candidate rc=2,
# base writer rc=0. Run from anywhere; scratch only.
set -u
S=${1:?usage: honest-filter-refusal-fixture.sh SCRATCH_DIR}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fixture-honest-filter.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo TOPLEVEL-MISMATCH; exit 1; }
mkdir -p "$D/tools"
printf '#!/bin/sh\nexit 0\n' > "$D/tools/instr.sh"; chmod 755 "$D/tools/instr.sh"
printf '*.bin filter=t\n' > "$D/.gitattributes"
printf 'payload\n' > "$D/data.bin"
git -C "$D" -c user.name=fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false add -A
git -C "$D" -c user.name=fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false commit -qm init
git -C "$D" config filter.t.clean cat
git -C "$D" config filter.t.required true
echo "status (honest clean tree): [$(git -C "$D" status --porcelain)]"
REV=$(git -C "$D" rev-parse HEAD)
mkdir -p "$S/outcand" "$S/outbase"
cd "$D" && python3 -B "$LANE/tools/souji-receipt-write.py" --root "$D" --rev "$REV" \
  --instrument tools/instr.sh --out "$S/outcand/r.txt" --allow-outside -- /bin/true
echo "CANDIDATE rc=$?"
cd "$D" && python3 -B "$LANE/census/round-71/controls/base-writer-8b9345b1.py" --root "$D" --rev "$REV" \
  --instrument tools/instr.sh --out "$S/outbase/r.txt" --allow-outside -- /bin/true
echo "BASE rc=$?"
