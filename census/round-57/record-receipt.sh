#!/usr/bin/env bash
# souji round 57 receipt recorder (Q109 repair: a receipt names the revision it
# was measured at, the instrument it ran, and that instrument's committed
# digest at that revision).
#
# Usage: record-receipt.sh <lane-root> <full40-rev> <instrument-relpath> <out-file> -- <command...>
#
# Writes, in order: instrument=, instrument_sha256= (the committed blob of the
# instrument at <rev>), rev=, the command's combined output, EXIT=<rc>.
# Refuses a short/branch revision (exit 2) and never writes outside <out-file>
# or the caller's scratch. The instrument digest binds BYTES, not execution
# (census/round-57/preregistration.txt, C2 named limits).
set -u
LANE=${1:?lane root}; REV=${2:?full40 rev}; INSTR=${3:?instrument}; OUT=${4:?out file}
shift 4
[ "${1:-}" = "--" ] && shift
[ -n "${1:-}" ] || { echo "usage: record-receipt.sh <lane> <rev> <instrument> <out> -- <cmd...>" >&2; exit 2; }
case "$REV" in
  [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*)
    if [ "${#REV}" -ne 40 ]; then echo "refused: rev is not full 40-hex ($REV)" >&2; exit 2; fi ;;
  *) echo "refused: rev is not full 40-hex ($REV)" >&2; exit 2 ;;
esac
git -C "$LANE" cat-file -e "$REV:$INSTR" 2>/dev/null || {
  echo "refused: $INSTR absent at $REV" >&2; exit 2; }
DIGEST=$(git -C "$LANE" show "$REV:$INSTR" | sha256sum | cut -d' ' -f1)
OUTPUT=$("$@" 2>&1); RC=$?
{
  echo "instrument=$INSTR"
  echo "instrument_sha256=$DIGEST"
  echo "rev=$REV"
  printf '%s\n' "$OUTPUT"
  echo "EXIT=$RC"
} > "$OUT"
echo "RECORD $OUT rev=$REV instrument=$INSTR rc=$RC"
exit "$RC"
