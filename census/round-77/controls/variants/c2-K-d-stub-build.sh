#!/usr/bin/env bash
# r77 CONTROL K-d build: a --shared scratch clone of the lane base with empty stubs committed at the two
# capture paths (P09/P10 file, P11/P18 directory). Usage: c2-K-d-stub-build.sh LANE DIR (DIR must not exist).
set -euo pipefail
lane=$1 d=$2
[[ -n $d && ! -e $d ]] || { echo "refusing: $d" >&2; exit 2; }
git clone -q --shared "$lane" "$d"
[[ $(git -C "$d" rev-parse --show-toplevel) == "$(cd "$d" && pwd -P)" ]] || { echo "toplevel mismatch" >&2; exit 2; }
git -C "$d" checkout -q --detach d4f515637884695b3aa016da169d859d3ece6ac4
mkdir -p "$d/.ufo/waves/round-63/w1/S63ExecWriter" "$d/.ufo/waves/round-64/w1/S64ExecFreeze"
: > "$d/.ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py"
: > "$d/.ufo/waves/round-64/w1/S64ExecFreeze/stub.txt"
git -C "$d" add -f .ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py .ufo/waves/round-64/w1/S64ExecFreeze/stub.txt
git -C "$d" -c user.name=fixture -c user.email=fixture@invalid commit -qm 'K-d stub capture'
git -C "$d" rev-parse HEAD
