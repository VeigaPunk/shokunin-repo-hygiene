#!/usr/bin/env bash
# Supplementary C2 probe: does an existing-OUT overwrite get through? Throwaway repo per shape.
set -u
S=/fast/scratch/hyaku/souji-r61/S61MutationCounter
TOOLS=("$S/base/souji-receipt-write.py" "$S/c2/m5-replace-no-exists.py")
for tool in "${TOOLS[@]}"; do
  for shape in committed-out-clean-tree untracked-out-allow-dirty; do
    D=$(mktemp -d -p "$S" "c2probe.XXXX")
    git -C "$D" init -q
    [ "$(git -C "$D" rev-parse --show-toplevel)" = "$D" ] || { echo "TOPLEVEL MISMATCH"; exit 9; }
    printf '#!/bin/sh\necho instrument-ok\n' > "$D/instrument.sh"
    git -C "$D" -c user.name=probe -c user.email=probe@invalid add instrument.sh
    git -C "$D" -c user.name=probe -c user.email=probe@invalid commit -q -m seed
    REV=$(git -C "$D" rev-parse HEAD)
    printf 'SENTINEL\n' > "$D/receipt.txt"
    extra=""
    if [ "$shape" = committed-out-clean-tree ]; then
      git -C "$D" -c user.name=probe -c user.email=probe@invalid add receipt.txt
      git -C "$D" -c user.name=probe -c user.email=probe@invalid commit -q -m out-committed
      REV=$(git -C "$D" rev-parse HEAD)
    else
      extra="--allow-dirty"
    fi
    out=$(python3 -B "$tool" --root "$D" --rev "$REV" --instrument instrument.sh --out "$D/receipt.txt" --allow-outside $extra -- echo hi 2>&1); rc=$?
    now=$(head -c 9 "$D/receipt.txt" | tr -d '\n')
    echo "TOOL=$(basename "$tool") SHAPE=$shape rc=$rc out_after_first9='$now' stderr_or_record=$(echo "$out" | tail -1)"
    rm -rf -- "$D"
  done
done
