#!/usr/bin/env bash
# P10 probe: run the landed C2 tool's own --selftest under three single-logic sabotages (argv: scratch, lane, tip).
set -u
S=$1; LANE=$2; TIP=$3
mkdir -p "$S/sab"
git -C "$LANE" show "$TIP:tools/souji-freeze-check.py" > "$S/sab/orig.py" || exit 2
python3 -B "$(dirname "$0")/c2-sabotage.py" "$S/sab/orig.py" "$S/sab" || exit 2
for k in digest-inverted freeze-none ancestry-inverted; do
  TMPDIR="$S" timeout 300 python3 -B "$S/sab/$k.py" --selftest > "$S/sab/$k.out" 2>&1
  echo "$k selftest rc=$? tracebacks=$(grep -c Traceback "$S/sab/$k.out") $(grep '^SELFTEST' "$S/sab/$k.out")"
done
TMPDIR="$S" timeout 300 python3 -B "$S/sab/orig.py" --selftest > "$S/sab/orig.out" 2>&1
echo "landed tool unmodified selftest rc=$? $(grep '^SELFTEST' "$S/sab/orig.out")"
