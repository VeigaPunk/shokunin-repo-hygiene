# Round 35 — fresh fleet numerator; C1/C2 under measurement

author: souji L1 (SoujiR35), cycle-2 attempt 1. Frozen contract: `census/round-35/preregistration.txt` (freeze `4e9c295e9339cc2b13f7a0dd5ec9fc8213a9e18e`; amendment A1 `8788d5565f9e1cbc8cd6e4fe84222b5d6483612c`). Base `1e9cad0b553891c41fe5b7ad1686decc147d76d4`; instrument `d1c940414087b606503662e4d115f51cb0fba40c`.

## Claims

- **C1 calibration (lowest non-retired axis, score 7).** Frozen 60 registry/outcome items. Instrument-revision do-nothing: `SUMMARY items=60 agree=37 unresolved=23 mismatches=23 withdrawn=0 restated=5`, rc 1 (`census/round-35/records/controls-c1-do-nothing.txt`). Final result pending W1/W2; no target claim yet.
- **C2 operability (score 8).** Frozen 13 legs. Pre-instrument no-legs control is CNE rc 2; J1 junk control `cases=5 pass=5 control=STUB-REJECTED`. Feasibility: W1/N4 pass; N3 fails (`cases=12 pinned=True summary=False`); W2 fails (`CASE=20 summary=SUMMARY total=20 failed=1`). W3/W4 remain unmeasured. No target claim yet; failures stay named, not dropped.
- **C3 coverage (score 8, sourced F1 claim).** `fleet-prune-numerator-r35.md` records the read-only 2026-10-28 numerator: 26 repositories, 27 registrations, 0 immediately prunable; S231 is the committed census record, S232 the git-worktree(1) source snapshot. C3 passes at current tip `fedfa4068801164ac2e189029137ebe87a1d94d3`: `SUMMARY entries=1 legs=6 fail=0` (`census/round-35/records/c3-at-current.txt`).

## Gate

S231/S232 were mined and used by the admitted entry; source snapshot and exact census receipt are under `census/round-35/`. Historical staged census 40 registrations / 14 repos (2026-10-24) is dated evidence and is superseded only as the current numerator, not falsified.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `counter-schema-binding` | `census/round-35/records/c3-at-freeze.txt`: SOURCES rows S231/S232 were marked mined and used-by, but C3 L3 reported `status=2026-10-28`; `registry_rows` selected `cells[8]` (`opened`) instead of `cells[7]` (`status`). A1 corrected the binding; `c3-after-A1.txt` and `c3-at-current.txt` pass. | L1 red-before run | Before freezing, map every counter index to the table header and run an admitted-entry golden case against a do-nothing case; assert status and used-by independently. |
| `feasibility` | `n3-feas-test.txt` reports pinned N3 but no summary; `w2-feas-test.txt` reports one failed case in 20; W1/N4 pass. | L1 feasibility probes | Preserve timed-out or failed legs as residuals; do not equate a pin or partial case count with a green leg. |

## Findings

C3's initial frozen-list measurement found and localized the SOURCES status-column bug, which was repaired by A1 without changing the predicate or target. Fixed C3 measured green at the lane tip. C1 and C2 final outcomes, wave receipts, axis score deltas, and admission verdict will be completed after W1/W2 settle.

## Receipts

- Preregistration, controls, and feasibility: `census/round-35/preregistration.txt`, `census/round-35/records/`.
- F1 census: `census/round-35/records/prune-census.tsv`; source: `census/round-35/sources/git-worktree.1.txt`.
- W1 dispatch: `.ufo/waves/round-35/w1-spec.json`; final wave capture pending.
