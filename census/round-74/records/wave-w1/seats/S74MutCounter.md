# S74MutCounter — mutation probe of the r74 C2 counter additions (seat S74MutCounter)

Baseline reproduced from committed bytes (counter == ac573032 blob, sha256 e3fc47c2…a2dd20f before AND after): `--selftest` 62/62 fail=0 EXIT=0; main arm `SUMMARY … base_forgeries=15 … base_unwitnessed=0 … EXIT=0`; D6 arm `base_forgeries=14 base_unwitnessed=1 EXIT=1` + `CASE FWw … base_witness=no`. C2 conjuncts (i)(iii)(v) hold; no frozen number refuted.
Commands (from lane root): `python3 -B <X>.py --selftest --root <lane> --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1… --work $S/st-<X>`; main = same + `--rev 43cd74bba84… --tool tools/souji-receipt-write.py`; D6 = `census/round-73/apply-edit.py --set census/round-74/c2-defang.json --id D6`. Mutants built by exact single-occurrence replacement (`build.py`, asserts count==1; all 15 parse).

| id | single edit (target line) | selftest | main (base_unwitnessed / base_forgeries / EXIT) | D6 | verdict |
|----|---------------------------|----------|------------------------------------------------|----|---------|
| X01 | row_scope returns diffs unfiltered (c1-counter.py:1175) | fail=3 EXIT=1 | — | — | killed (selftest) |
| X02 | row_scope always `[]` (:1175) | fail=2 EXIT=1 | — | — | killed (selftest) |
| X03 | row_scope(None)→`[]` (:1170) | fail=1 EXIT=1 | — | — | killed (selftest) |
| X04 | forge_paths discards spec["target"] (:1159) | fail=2 EXIT=1 | — | — | killed (selftest) |
| X05 | forge_paths `elif False` for inrun kinds (:1160) | fail=3 EXIT=1 | — | — | killed (selftest) |
| X06 | INRUN edit-counter-samesize→tools/notes.txt (:1143) | fail=2 EXIT=1 | — | — | killed (selftest) |
| X07 | INRUN index-stat-instrument→tools/counter.py (:1154) | **62/62 EXIT=0** | **1 / 14 / EXIT=1** | — | killed (main control iii) |
| X08 | INRUN chmod-clean→tools/counter.py (:1149) | fail=1 EXIT=1 | — | — | killed (selftest) |
| X09 | new slot unscoped (:1469 no row_scope) | **62/62 EXIT=0** | **0 / 15 / EXIT=0** | **base_unwitnessed=1 EXIT=1** | **SURVIVED** |
| X10 | base slot unscoped (:1468 no row_scope) | **62/62 EXIT=0** | **0 / 15 / EXIT=0** | **base_unwitnessed=0 EXIT=0** | killed (D6 conjunct) |
| X11 | `if b_wit:`→`if True:` (:1488) | fail=1 EXIT=1 | — | — | killed (selftest) |
| X12 | claim drops new_unwitnessed (:1541 `==0`→`>=0`) | fail=1 EXIT=1 | — | — | killed (selftest) |
| X13 | forge_paths ignores chmod_notes (:1162) | fail=2 EXIT=1 | — | — | killed (selftest) |
| X14 | forge_paths ignores index_stat (:1164) | fail=1 EXIT=1 | — | — | killed (selftest) |
| X15 | (9a) check drops new_unwitnessed (:2005) | **62/62 EXIT=0** | **0 / 15 / EXIT=0** | **base_unwitnessed=1 EXIT=1** | **SURVIVED** |

Kill attribution (actual failing checks, `.ufo`-external scratch logs): X01 → "row scope: a set-up-only divergence is not the row's (FWw, FC1, FC2)"; X02/X05/X06 → (9a) "base_unwitnessed=7/3/2"; X03 → "a failed read stays a failed read"; X04 → "forge paths: … | ['AS1','FC1','FC3','FWr','FWp','FWw','FWs']"; X07 → main `base_unwitnessed=1` (FX3 unwitnessed, base_forgeries 15→14); X10 → D6 SUMMARY `base_unwitnessed=0`; X11 → "witness: a failed witness read is unwitnessed (FM1, both slots)"; X12 → "claim verdict: one unwitnessed new-slot forgery fails the claim"; X13 → `['FM1']`; X14 → `['FX2']`.

Two extra probes (labelled, not single-edit): M17 (frozen survivor set, on r74 counter) selftest = **fail=1 EXIT=1**, killed only by `(9a) witness run … new_unwitnessed=3`; P1 = X15+M17 selftest = **62/62 fail=0** → the (9a) new_unwitnessed term is the SOLE detector of M17.

Findings
- **MEDIUM (F1, X09)**: new-slot row scoping has no detector anywhere. Selftest checks `row_scope()` as a function and the (9a) run only asserts `new_unwitnessed==0` (a metric that an unscoped read can only improve), and the frozen D6–D8 arms count only `base_unwitnessed`. Behaviour changes but no conjunct moves: X09-D6 `CASE FWw … base_witness=no new_witness=yes` vs pristine D6 `… new_witness=no`, identical SUMMARY/EXIT. The r73 tree-global defect therefore silently returns on the candidate slot.
- **MEDIUM (F2, X15)**: mutating the (9a) assertion away leaves 62/62 and every C2 conjunct intact, and removes the only kill of M17 (P1 proof). The r74 survivor-kill power rests on a single, un-self-tested assertion.
- **LOW (F3, X07)**: "forge paths: every base-accepted refuse row declares a forged path" (:2144) tests non-emptiness, not correctness — a wrong INRUN_FORGED path passes 62/62 and is caught only by the main positive control. Positive: conjunct (iii) and the D6 conjunct are both load-bearing (X07, X10).
Verdict: 15/15 single-edit mutants built; 13 killed, 2 survived; no frozen claim number falsified.

Restoration: no lane tracked byte touched (counter sha256 e3fc47c2… identical before/after; only file written in the lane is this report); scratch removed. Files: .ufo/waves/round-74/w1/S74MutCounter.md.
