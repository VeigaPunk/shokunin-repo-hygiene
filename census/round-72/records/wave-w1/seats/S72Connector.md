# S72Connector — r72 sibling-overlap + cross-claim scan (read-only)

## 1. Numbers re-derived from committed bytes (all frozen invocations, fresh scratch)
- C1(i) harness: `SUMMARY label=c1-after-r72 positive_selftest=PASS x_mutants=11 x_killed=11 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0` (750.9 s) = records/c1-after.txt. TRUE.
- C1(ii) Y6 main arm: my single-occurrence edit of the r72 counter is byte-equal to records/variants/r72-Y6-counter.py (sha256 45f3afdb…b846); run prints `SUMMARY matrix=75 base_forgeries=2 … base_mismatches=10 … new_honest=19 class_mismatches=0 … regress=PASS` / `EXIT=1` = records/c1-Y6-main-arm.txt. TRUE.
- C2(i) battery: `BATTERY mutants=5 kills=5 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0 all_match=true` / `EXIT=0`; five MUTANT lines byte-identical (27daa4b3…, b88c8471…, b21ccdd2…, a9c1fa16…, 798f9344…) = records/c2-after-battery.txt. TRUE.
- C2(ii) honest writer: `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0` = records/c2-honest-writer.txt. TRUE.
- Hash/row checks: counter 7578447d…, matrix cd8490b4… (75 rows = 19 accept + 56 refuse), harness 6c7bf41d…, mutants cfc40608…, writer b7790001…, base writer 118597e0… with 0 matches for FILTER-DRIVER/check-attr/_witness_refusal. Mutant provenance 6/6 byte-equal to the r71 seat files; X6-X10 identical to census/round-71/c2-mutants.json. TRUE.

## 2. Separability (C1 vs C2)
- C2(i) reads neither section (9) nor claim_upheld: a counter copy with section (9) deleted and the `base_mismatches` term dropped emits a **byte-identical** battery transcript (both 162475 B, sha256 b057ab9b…). Code: `battery_verdict` c1-counter.py:1374-1385 takes only (name, obs, exp); `classify_outcome` :1309 reads row_fate; the battery branch :1897-1930 never calls claim_upheld; selftest is a separate branch :1852.
- C1(i) does not read the FW rows as measurements: a counter with FW removed consistently (CASE_ORDER 70, CASE_SPECS 70, 70-row matrix) still scores `x_killed=11 x_survived=0 score=0` `EXIT=0`. But the matrix is closed: removing the five rows from the matrix alone → `C1-COUNTER-FATAL: matrix unusable: matrix rows must be [… 'FWr' …] in order`, EXIT=2 (`load_matrix` :1129-1130). So "C1 reads no new row" is causally true, structurally false. [MEDIUM]
- C2(ii) *does* read the base slot (`claim_upheld` :1291-1297 includes `base_mismatches`), outside the prereg's parenthetical scoped to MUTANT/BATTERY; it is 0 for the honest writer, so dropping the term changes nothing there.
- Verdict: causally SEPARABLE; one formal coupling (closed matrix) and one unscoped term.

## 3. Sibling clean-tree gates × five r72 routes (fixture-verified mechanism)
| class | gates (file:line) | R1 process/clean driver | R2 worktree-only attrs | R3 driver named `set` | R4 driver created in-run | R5 driver removed in-run |
|---|---|---|---|---|---|---|
| status snapshot | kaidoku 29/prefile-check.sh:22, 42/prefile-gate.py:108,286, 45/frozen-path-preflight.py:139, 46/gate.py:175; kama pre-report-gate.py:673, round72-round-scope.py:255, round73-round-scope-cases.py:278; mori mori-index-clean.sh:53,108, mori-unlanded-check.py:58, mori-misroot-sweep.py:234, mori-census.sh:2389 (ls-files -mo); kasegi r46-landing-gate.py (tree-clean), r36/r37/r41-closure.sh (E9); kumitate round-gate.mjs:463; mado check-evidence-pointers.py:187; tabi check-selfassessment.mjs:483 | yes | yes* | yes | n/a | n/a |
| two-witness status | tameshi mutate-and-run.sh:2059,2071 | yes | yes* | yes | yes | yes |
| post-run diff | audio r89-simplifier/proofs/run-all.sh:49 | yes | yes* | yes | yes | yes |
| byte-truth | kama round67-worktree-landing-check.py | no | no | no | no | no |
| clone-only | kengaku plans/ledger_tip.py:134 | n/a | n/a | n/a | n/a | n/a |
Fixture receipts (routes.txt): forged worktree `v2` vs committed `v1` → status `[]`, `diff --quiet` rc 0, `ls-files -m` `[]`, `show HEAD:` `v1`; R2 `check-attr --cached` = `unspecified` vs worktree `t`; R3 `check-attr` prints `set`; R4 pre_drivers 2→3 with pre/post status both `[]`; R5 3→2 with both `[]`; byte compare = DIRTY in every case. *R2 is indistinguishable from R1 for every gate that never reads attributes: grep over all sibling lanes → 0 `check-attr` gates (one prose mention, kengaku plans/refusals46/f20_attributes_file.py:4), 0 filter-driver enumerations, 0 `GIT_ATTR_SOURCE` scrubs, 0 `core.fileMode` pins (only tameshi executor-source-pin-measure-v2.py, a measurement).
New vs r71 list: 6 hits absent from S71Connector.md (kama round67; kasegi r46 + r36/r37/r41; kumitate round-gate; mado check-evidence-pointers; tabi check-selfassessment; kengaku ledger_tip). All are dated 2026-10-23…11-03, before the r71 lane commit (2026-11-06T17:23-03:00): r71 scan misses, not new files.

## 4. README r72 frontier + knowledge r72 section vs named receipts
TRUE: 75 rows; 19 accept; battery 0/5 (controls/c2-before-r71-battery.txt: kills=0 survived=5) and 5/5 (c2-after-battery.txt); probe 10 accept lines in 35, one member per shape (FWr→WM3, FWi→WM4, FWp→WM5, FWw→WM8, FWs→WM6); base slot 8b9345b1 has no filter witness; SOURCES offsets 2608/20533/5164 reproduce exactly under the stated "whitespace-normalized" transform; FWw empty-committed mechanism and its non-empty counter-claim ("different-size worktree edit is reported as modified") both reproduced in a fixture.
LOW: the knowledge sentence "the current writer refuses all five … (probe, records/c2-after-battery.txt, records/c2-honest-writer.txt)" — c2-after-battery.txt's new slot is always a mutant, never the tip writer (0 tip-writer refusals; its 70 RECEIPT-FILTER-DRIVER-SET lines are mutant refusals). Claim true via the probe and c2-honest-writer only.
LOW: c1-Y6-main-arm.txt records `instrument=census/round-72/c1-counter.py` while instrument_sha256 45f3afdb… is the Y6 variant; only the sha identifies the file that ran.

## 5. Findings
- MEDIUM: C1's harness result is matrix-closed (matrix-only FW removal → EXIT=2); the prereg's "reads no new row" needs "given a consistent matrix edit".
- MEDIUM: r71's blanket "every gate can certify a dirty tree" is overstated in scope — kama tools/round67-worktree-landing-check.py compares worktree bytes to the HEAD blob and is not fooled by any of the five routes (the only such sibling gate).
- HIGH (pre-existing, not introduced by r72): none of the five r72 routes is detectable by any sibling clean-tree gate; the 5 routes are unmeasured fleet-wide.
- LOW ×2 as in §4.

## 6. Proposed move (bounded, no lane edit)
Route to r73 a byte-truth witness class (worktree bytes vs `rev-parse`/`git show` blob) as the matrix row shape no sibling status gate and none of the five r72 routes can fool; evidence: routes.txt (status `[]` while byte compare DIRTY in all five shapes) and kama round67. Affected axes: C2 coverage (adds a measured protection class), C1 untouched. Risks: byte-truth covers declared paths only (no untracked/index-flag coverage), and it must not replace the status witness (it cannot see additions). Verification: the same fixture shape as a new counter row plus a writer mutant that drops the byte compare.

Files written: .ufo/waves/round-72/w1/S72Connector.md; .ufo/waves/round-72/w1/S72Connector/{main-arm.txt,battery.txt,harness.txt,selftest.txt,revbat.txt,y6-main-arm.txt,routes.txt,harness-noFW.txt,matrix-closure.txt}. Scratch removed before yield.
