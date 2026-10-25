## Status
STATUS: PASS — delivered `census/round-28/records/scorecard-draft.md` with the Round 28 measurements table (Round 27 table shape, frozen prereg counters, before-receipt values, `[AFTER]` placeholders) and the r29 planned bullet carrying residuals.

## Evidence
- Frozen contract read first: `census/round-28/records/preregistration.txt` lines 5/7/9 (raw) — C1 findings 2→0, C2 grounded F4 4→6 rows 135→138 gate ok=2, C3 dirty_waves 163→0 + manifests + fixture cases=6 pass=6 control=TAMPER-REJECTED. Full claim text read (no truncation).
- Before receipts read: `c1-before.tsv` (`findings=2 checked_reg=52` at 3a2a80d0d18940a5e352ebc526da22a57dad83c4, c1_rc=2), `c2-before.tsv` (`grounded_f4=4 rows=135`), `c3-before.tsv` (`dirty_waves=163 manifests_26=absent manifests_27=absent`).
- Shape source: `SCORECARD.md` Round 27 measurements table (lines 17–25) — columns `claim | axis | before | after | counting command | measured commit`.
- r28 planned bullet (line 213, raw) used verbatim for the SCORECARD/SHONEN measurement residual and "C1 r27 target remains failed" carry.
- Lane git: HEAD `0c96332` (round-28 preregistration commit), base `3a2a80d` present (git log).
- Deliverable written: `census/round-28/records/scorecard-draft.md` (3060 B). Report: `.ufo/waves/round-28/w1/SwarmExecutor20.md`.
- No tools installed; no tooling channel used.

## Findings
1. The Round 27 table shape is exactly `| claim | axis | before | after | counting command | measured commit |`; the draft reproduces it, including the `calibration 7`/`coverage 8`/`operability 8` axis cells and `measured commit` cells carrying receipt paths plus the base revision.
2. After values are `[AFTER]` placeholders only; frozen targets are quoted separately (e.g. `findings=0`, rows `138`, dirty `0`) so no target is passed off as measured.
3. Counting commands are the frozen prereg counters: C1 full landing-gate invocation; C2 `grep -cE '^ground: F4'`, row grep, gate-check, coverage-agreement, sources-census validate; C3 porcelain awk counter, manifest `test -s`, fixture invocation. Pipes inside the C3 awk code span are escaped (`\|`) to keep the table well-formed.
4. The r29 planned bullet carries residuals grounded in the r28 plan (SCORECARD/SHONEN measurement, S119 disposition, pre-report gate retention) plus standing holds (certification OFF, K5 HELD, F5 reap + NAMESPACE).
5. Sibling drafts confirming the delivery convention (other seats write `census/round-28/records/*-draft` files): `log-entry-draft.md`, `s119-disposition.tsv` present.

## Attack log
None — this seat's item is a deliverable draft, not an attack. No counter/predicate/target challenged.
