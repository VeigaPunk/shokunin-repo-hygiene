#!/bin/sh
# S71Reviewer repro (HIGH): candidate writer a1db6c85 writes a receipt over a forged tree when the
# tracked attribute is the literal value `set` (or `unset` / `unspecified`) and a driver of that name is configured.
# Usage: sh repro-filter-set-forgery.sh <WRITER_PY> <SCRATCH_DIR>   (SCRATCH_DIR under /fast/scratch, not /tmp)
set -eu
W="$1"; S="$2"
D=$(mktemp -d -p "$S"); [ -n "$D" ] && [ -d "$D" ] || exit 1
R="$D/repo"; mkdir "$R"; git -C "$R" init -q
[ "$(git -C "$R" rev-parse --show-toplevel)" = "$R" ] || exit 1
mkdir "$R/tools"; printf '#!/bin/sh\necho instrument-ok\n' > "$R/tools/instr.sh"
printf 'counter v1\n' > "$R/tools/counter.py"; printf 'tools/counter.py filter=set\n' > "$R/.gitattributes"
git -C "$R" add . && git -C "$R" -c user.email=fixture@r71.invalid -c user.name=fixture commit -qm base
git -C "$R" config filter.set.clean 'sed s/v2/v1/'
printf 'counter v2\n' > "$R/tools/counter.py"
echo "status=[$(git -C "$R" status --porcelain)]   (empty = clean filter hides the forged bytes)"
REV=$(git -C "$R" rev-parse HEAD); mkdir -p "$R/.git/receipts"
python3 -B "$W" --root "$R" --rev "$REV" --instrument tools/instr.sh --out "$R/.git/receipts/r.txt" --command "/bin/echo hi"; echo "rc=$?  (0 = receipt written over forged bytes; expected 2 after a fix)"
rm -rf -- "$D"
