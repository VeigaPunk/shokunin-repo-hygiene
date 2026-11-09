#!/usr/bin/env bash
# ConnectorOverlap r100 — sibling-overlap null sweep (read-only).
# Targets: PROVINCE.md, corpus/README.md, the four most recent round lessons (96..99),
# and the r99 non-author spot-check that routed defects 1-2.
set -u
L=/home/vgpnk/Projects/shokunin/souji-shokunin
TARGETS=("$L/PROVINCE.md" "$L/corpus/README.md" "$L/corpus/lessons/round-96.md" \
         "$L/corpus/lessons/round-97.md" "$L/corpus/lessons/round-98.md" \
         "$L/corpus/lessons/round-99.md" "$L/corpus/lessons/round-99-verifier-spotcheck.md")
echo "SWEEP-A session-owned-escapee-reap pattern='(session id|session-id|session_id|field 6|field-6|escapee|setsid)'"
for f in "${TARGETS[@]}"; do
  grep -nE 'session id|session-id|session_id|field 6|field-6|escapee|setsid' "$f" | sed "s#^#$f:#"
done
echo "SWEEP-A exit=$?"
echo
echo "SWEEP-B attribution-repair pattern='(S332|field 4|field-4|used-by|attribution)'"
for f in "${TARGETS[@]}"; do
  grep -nE 'S332|field 4|field-4|used-by|attribution' "$f" | sed "s#^#$f:#"
done
echo "SWEEP-B exit=$?"
echo
echo "SWEEP-C lane-wide prior art for a field-6 session kill (outside the four scan targets)"
grep -rnE 'field 6' "$L/corpus/knowledge" "$L/corpus/README.md" "$L/PROVINCE.md" 2>/dev/null | head -20
