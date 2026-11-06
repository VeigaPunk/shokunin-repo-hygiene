#!/usr/bin/env bash
# S71CriticClaims — counterexample to r71 C1's property (HIGH finding).
# A committed `.gitattributes` carrying `ident` is a lossy checkin conversion with NO configured
# driver, so the r71 candidate's RECEIPT-FILTER-DRIVER-SET check (filter attribute only) never sees
# it: `git status --porcelain` reports a clean tree over size-preserving changed bytes and the
# candidate writes a receipt (rc 0). Run from anywhere; scratch only.
set -u
S=${1:?usage: ident-forgery-fixture.sh SCRATCH_DIR}
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p "$S" || exit 1
D=$(mktemp -d -p "$S" fixture-ident.XXXXXX) || exit 1
[ -n "$D" ] && [ -d "$D" ] || exit 1
trap 'rm -rf -- "$D"' EXIT
git -C "$D" init -q || exit 1
[ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo TOPLEVEL-MISMATCH; exit 1; }
mkdir -p "$D/tools"
printf '#!/bin/sh\nexit 0\n' > "$D/tools/instr.sh"; chmod 755 "$D/tools/instr.sh"
printf '*.txt ident\n' > "$D/.gitattributes"
printf '$Id: v1 $\npayload\n' > "$D/data.txt"
git -C "$D" -c user.name=fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false add -A
git -C "$D" -c user.name=fixture -c user.email=fixture@example.invalid -c commit.gpgsign=false commit -qm init
REV=$(git -C "$D" -c user.name=fixture -c user.email=fixture@example.invalid rev-parse HEAD)
echo "index blob: $(git -C "$D" cat-file -p "HEAD:data.txt" | tr '\n' '|')"
printf '$Id: v2 $\npayload\n' > "$D/data.txt"
echo "status after size-preserving edit: [$(git -C "$D" status --porcelain)]"
mkdir -p "$S/ident-cand"
cd "$D" && python3 -B "$LANE/tools/souji-receipt-write.py" --root "$D" --rev "$REV" \
  --instrument tools/instr.sh --out "$S/ident-cand/receipt.txt" --allow-outside -- /bin/true
echo "CANDIDATE rc=$?  receipt: $(ls "$S/ident-cand" 2>/dev/null | tr '\n' ' ')"
