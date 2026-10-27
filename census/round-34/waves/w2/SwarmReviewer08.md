# SwarmReviewer08 — seat report (souji r34 w2, AttackE04)

Full report: `.ufo/waves/round-34/w2/AttackE04.md` (same lane, read-only; scratch `/fast/scratch/hyaku/souji-r34/e04`, 112 KB).

## Status

W1's E04 finding **CONFIRMED** — the calibration defect is real and the proposed restatement row is valid under the frozen cause/argv/exit/statement/Q76 rules; no honest rule-conforming route was missed. One rule-shape observation recorded (not a defect).

## Evidence

- Frozen item `census/round-34/c1-items.tsv:43`: E04 = SCORECARD.md:21, exit 2, pred `SUMMARY findings=0 checked_reg=52`, argv runs `tools/souji-landing-gate.py --rev de478b48… --round 28`. Committed do-nothing record `census/round-34/records/controls-c1-do-nothing.txt:27` shows the actual reading: rc=1, `SUMMARY findings=19 … checked_reports=61` → MISMATCH.
- Executed probe 1 (pre-r30 gate bytes `fec846dd:tools/souji-landing-gate.py` at the pinned rev, env-scrubbed, scratch TMPDIR): rc=2, stdout SUMMARY `…checked_reports=0`, stderr `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-28/ at de478b48…`. Tree facts: 0 committed `.md` under `.ufo/waves/round-28/`, 61 under `census/round-28/waves/` at de478b48. Counter concatenates stderr after stdout (`c1-counter.py:239,304`), so the digit-bearing warning is always the last digit-bearing line → the original predicate can never hold pre-r30; value drift is unexecutable at any cause. This proves W1's blockage claim.
- Executed probe 2 (current gate, unchanged base→51acb5fb) at the same rev: rc=1, empty stderr, last line exactly W1's restated statement (`SUMMARY findings=19 … checked_reports=61`). Stable across tips (committed-byte provenance via ls-tree/cat-file; C1's touched list cannot touch tools/).
- Cause validity for W1's row (deliver-c1-E04.md:42, argv-correction branch): fec846dd is the unique first writer of the row's exact line (`git log -S` single hit), ancestor of --list-rev 2b0171e2, parent = de478b48 with line 21 byte-different, cause line 21 byte-equal to list-rev, and the row's argv already fails at the cause (probe 1: rc=2 but warning-last → predicate fails). Q76 clean (no `| E04 |` row at list-rev). Amendment A1 tightens, never relaxes.

## Findings

1. W1 blockage claim (value-drift branch unusable) — CONFIRMED by executed reproduction.
2. W1 proposed repair — VALID; effectively the unique rule-conforming encoding (`same` blocked twice over: cause touches none of the item files, and original holds at no parent; mechanism cause 68447af blocked — it does not touch SCORECARD.md; `(exit=1, statement)` pair is forced by the gate's deterministic output).
3. Rule-shape observation (non-defect): the counter keys its cause branch on the row's run-cell form (`same` vs backticked), not on whether the argv differs, so an exit/statement-only drift can ride the argv-correction branch with an identical argv. Frozen text and junk controls permit it; flag for the round lesson.
4. Non-blocking narrative gap: W1's "68447af: rc 1 findings=19" is source-supported (r30 gate reads the census capture) but I did not execute at 68447af; not load-bearing.

## Attack log

where-cell ✓, first-writer ✓, ancestry/parent ✓, value-drift bypass exhausted (none: pre-r30 warning always digit-bearing and stderr-last; post-r30 rc≠2; digit-free-error state unreachable), `same` encoding impossible, alternate cause 68447af impossible, Q76 clean, artifact hypothesis rejected (mismatch independent of stream ordering), tip stability ✓, amendments ✓. Details in AttackE04.md.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE04.md` (full report)
- `.ufo/waves/round-34/w2/SwarmReviewer08.md` (this seat report)
- No lane/frozen artifacts modified; no commits/pushes; no other repos touched.
