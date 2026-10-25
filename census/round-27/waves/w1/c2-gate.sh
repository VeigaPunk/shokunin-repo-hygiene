#!/usr/bin/env bash
# c2-gate.sh — souji round-27 C2 assimilation gate runner (DRAFT).
# Seat ExecC2GateCheck, wave w1. L1 installs this as
# census/round-27/c2-gate.sh (the draft lives at
# .ufo/waves/round-27/w1/c2-gate.sh).
#
# Invokes tools/souji-gate-check.py with the frozen round-27 C2 argv and
# emits a TSV summary on stdout: entries / ok / fail / rc. The checker's
# own FAIL lines are echoed verbatim first, so the integrator sees the
# individual check failures plus the machine-readable row.
#
# CLI (all optional; defaults match the frozen counter):
#   --root DIR          lane root (default: the souji lane)
#   --round-date D      ISO date (default: today)
#   --entries PATH...   entry paths relative to --root (default: the two
#                       F4 origin-record entries)
#   --snapshot-dir DIR  snapshot dir relative to --root
#   --slice F           slice file relative to --root; ids are any
#                       `S<3+ digits>` token found in its lines (the file
#                       may be empty — then T=0 and V==T holds vacuously)
#   --slice-verdicts F  verdict TSV relative to --root; rows are
#                       `id<TAB>class<TAB>evidence` with class in
#                       {present,accepted,unverifiable,refused}; V (ids
#                       verified) must equal T (slice total). A missing
#                       verdict row is NOT a fail line but cannot raise V.
#
# Exit code: the checker's rc (0 = every entry ok AND slice verified ==
# total AND zero failures). Missing tool -> 2. Nothing is written to the
# lane; this runner is a pure reporter.
set -u
export LC_ALL=C

LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
ROUND_DATE="${SOUJI_ROUND_DATE:-$(date +%F)}"
ENTRIES_DEFAULT="corpus/knowledge/origin-record-writer-r27.md corpus/knowledge/origin-record-mechanism-set-r33.md"
SNAP_DIR=census/round-27/sources
SLICE=census/round-27/records/slice-verdicts.tsv
VERDICTS="$SLICE"

TOOL="$LANE/tools/souji-gate-check.py"

[ -f "$TOOL" ] || { echo "FAIL tool-missing: $TOOL" >&2; exit 2; }

out=$(python3 -B "$TOOL" \
  --root "$LANE" \
  --round-date "$ROUND_DATE" \
  --entries $ENTRIES_DEFAULT \
  --snapshot-dir "$SNAP_DIR" \
  --slice "$SLICE" \
  --slice-verdicts "$VERDICTS" 2>&1)
rc=$?

printf '%s\n' "$out"

# Parse the checker's summary line:
#   entries=N ok=N slice_verdicts=N slice_total=N fail=N
summary=$(printf '%s\n' "$out" | grep '^entries=' || true)
entries=$(printf '%s\n' "$summary" | sed -n 's/.*entries=\([0-9]*\).*/\1/p')
ok=$(printf '%s\n' "$summary" | sed -n 's/.*ok=\([0-9]*\).*/\1/p')
fail=$(printf '%s\n' "$summary" | sed -n 's/.*fail=\([0-9]*\).*/\1/p')

printf 'entries\tok\tfail\trc\n'
printf '%s\t%s\t%s\t%s\n' "$entries" "$ok" "$fail" "$rc"

exit "$rc"
