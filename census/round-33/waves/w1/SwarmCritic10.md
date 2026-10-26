## Status
STATUS: PASS — audit executed end to end; K12 reproduces deterministically at base, list-rev and tip, but the frozen predicate is **LAX-PREDICATE**: two reproduced mutant states read AGREE while the row's own stated capability is violated (`|| \b11/11\b` matched an unrelated line over a summary stating `failed=3`; an aggregate `total=11 failed=0` accepted output carrying three `CASE\tFAIL` lines).

## Evidence
Contract read first: `census/round-33/preregistration.txt` (commit 2d9bca55), `census/round-33/c1-items.tsv` K12 row, counter docstring `census/round-33/c1-counter.py:1-36`.

Row 167 at base (measured rev 6017a48; SCORECARD.md byte-identical base→list-rev, `git diff --stat 6017a48 2d9bca5 -- SCORECARD.md` = empty):
```
| durable revision stamps (r19) | refuse HEAD/branch/short/keep-only/dirty-tree revisions before a record and verify tracked measured bytes | `tools/souji-rev-pin.py --selftest` 11/0; `tests/fixtures/r19-rev-pin.py` 13/0 | r19 |
```
Cell quotes (pipe-free): `refuse HEAD/branch/short/keep-only/dirty-tree revisions before a record and verify tracked measured bytes`; outcome span `tools/souji-rev-pin.py --selftest` followed by `11/0`.

(1) Determinism — clone `/fast/scratch/hyaku/souji-r33/AuditK12/c` (`git clone -q --no-local`, origin removed, `rev-parse --show-toplevel` printed the clone, detached at 2d9bca55, tree clean):
```
TMPDIR=<fresh>/run1 python3 -B tools/souji-rev-pin.py --selftest   -> rc=0, 12 lines, IDENTICAL to run2
env -u TMPDIR python3 -B tools/souji-rev-pin.py --selftest          -> rc=0, byte-identical to run1
SUMMARY total=11 failed=0
```
Last digit-bearing line is `SUMMARY total=11 failed=0` in every run; `run1/`–`run2/` TMPDIRs were empty afterwards and the clone stayed clean (selftest `finally: shutil.rmtree(top)` at tools/souji-rev-pin.py:372-376). Direct literal invocation `./tools/souji-rev-pin.py --selftest` (mode `100755`, shebang `#!/usr/bin/env python3`) → `SUMMARY total=11 failed=0`, rc=0, so the rule's `python3` normalization is byte-equivalent to the cell's literal span.

(4) Frozen counter, run exactly as assigned:
```
python3 -B …/census/round-33/c1-counter.py --root …/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/AuditK12/cnt --only K12
ITEM	K12	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=11 failed=0
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```
Same reading at base `--rev 6017a48…` (agree=1, mismatches=0, rc=0) and at tip `--rev fef88f2159f6380a4d1360f73365b3d595973a37` (agree=1, mismatches=0, rc=0); SCORECARD.md unchanged between base, list-rev and tip.

(3) Same cell's other stated outcome, re-derived at 2d9bca55: `python3 -B tests/fixtures/r19-rev-pin.py` → rc=0, `SUMMARY total=13 failed=0 base_discriminating=6` — current, and it is already item K13, so not an out-of-set residual.

Mutant battery in the scratch clone only (throwaway identity; each mutant one commit on 2d9bca55, counter `--root <clone> --rev <mutant> --list-rev 2d9bca55 … --only K12`):
| mutant | change to tools/souji-rev-pin.py | selftest | counter |
|---|---|---|---|
| A `8cd80bf…` | drop `input_snapshot(...)` (bytes verification) — harness untouched | rc=1 `SUMMARY total=11 failed=3` (dirty-tree, path-escape, historical-tree-check FAIL) | MISMATCH `rc=1 expect_exit=0 predicate fails last=SUMMARY total=11 failed=3`, rc=1 |
| D `7254a23…` | delete the `branch-name-refuse` case | rc=0 `SUMMARY total=10 failed=0` | MISMATCH `predicate fails last=SUMMARY total=10 failed=0`, rc=1 |
| C `df44419…` | drop bytes verification **and** misfile a failed case as a pass (`failed += 1` → `passed += 1`) | rc=0, 3×`CASE\tFAIL`, `SUMMARY total=11 failed=0` | **AGREE** `predicate holds last=SUMMARY total=11 failed=0`, rc=0 |
| E `649a2d7…` | drop bytes verification, print `PROGRESS 11/11 checks planned`, force `return 0` | rc=0, `SUMMARY total=11 failed=3` + `PROGRESS 11/11 checks planned` | **AGREE** `predicate holds last=PROGRESS 11/11 checks planned`, rc=0 |

## Findings
1. **Deterministic and reproducible.** K12's argv prints `SUMMARY total=11 failed=0` with rc 0 in three runs (two fresh TMPDIRs, one TMPDIR unset), leaves no writable residue, and the counter reads AGREE at base, list-rev and tip. Location: tools/souji-rev-pin.py:252-376; census/round-33/c1-counter.py:245-260.
2. **First alternative is faithful.** `\btotal=11\b && \bfailed=0\b` is exactly the tool's summary and exactly the notation the file already uses to restate this cell: `SCORECARD.md:388` writes `total=11 failed=0` for `python3 tools/souji-rev-pin.py --selftest`. Count drift (D: `total=10`) and honest failures (A: `failed=3`) are both rejected — the digits are not loosened.
3. **Second alternative is unanchored and matches foreign lines.** `\b11/11\b` never occurs in the healthy output (it is not the cell's `11/0`, and not the restatement at SCORECARD.md:388) but mutant E makes it match a progress line while the same output states `SUMMARY total=11 failed=3`; the counter itself reports `last=PROGRESS 11/11 checks planned` and scores AGREE. Location: census/round-33/c1-items.tsv K12 predicate; census/round-33/c1-counter.py:131-146.
4. **Aggregate count cannot see a stated capability loss that the tool reports itself.** Mutant C stops verifying tracked measured bytes (the cell's second half) and prints three `CASE\tFAIL` lines, yet `total=11 failed=0` + rc 0 reproduces the cell's digits and the item reads AGREE. The row would be false while C1 marks it current. Location: SCORECARD.md:167 prose; tools/souji-rev-pin.py:257-266, 374-376.
5. **No out-of-set residual in this cell.** The cell's only other digit-bearing outcome is `tests/fixtures/r19-rev-pin.py` `13/0`, which is enumerated as K13 and re-derived current (13/0, base_discriminating=6, rc 0). The prose carries no counts; `r19` is a round tag, not an outcome. Nothing outside the rule is stale.
6. **Notation.** The cell shorthand `11/0` is never printed by the command; only the `SUMMARY` rendering exists, which is why alternative 1 is the correct reading and alternative 2 has no basis in the cell or in its in-file restatement (SCORECARD.md:388).
7. **Bounded, not catastrophic.** The laxness needs output that contradicts itself (CASE FAIL beside failed=0, or an incidental `11/11` beside failed=3). Any regression that leaves the accounting honest and the case set intact is caught (mutants A and D). Vice versa, the predicate is not stricter than the cell: the healthy run matches on the first alternative.

## Attack log
- **Counterexample 1 (lax, alternative 2):** rev `649a2d7fb96960a7311868539486aa9159a8b6fa` in scratch; output `CASE FAIL dirty-tree-refuse …`, `SUMMARY total=11 failed=3`, `PROGRESS 11/11 checks planned`, rc 0 → `ITEM K12 AGREE`. A row claiming tracked-byte verification that no longer verifies passes C1.
- **Counterexample 2 (lax, aggregate):** rev `df444191d96cdf83a118359c59b68e2286fa5375`; output with 3 `CASE\tFAIL` lines, `SUMMARY total=11 failed=0`, rc 0 → `ITEM K12 AGREE`.
- **Negative controls:** `8cd80bf…` → MISMATCH (failed=3); `7254a23…` → MISMATCH (total=10). The predicate is not universally lax.
- **Impacted axis:** calibration (C1-CURRENCY) only — K12 can certify a false capability row on self-contradicting output; C2 untouched.
- **Smallest safe correction, available to the L1 and NOT applied by this seat** (stricter-only; the frozen predicate is not mine to change): require the matched alternative to sit on the final digit-bearing output line (`SUMMARY\ttotal=11\tfailed=0$) and drop `\b11/11\b`, or add `&& !CASE\tFAIL`; either keeps the healthy run green and rejects both reproduced states. Because a wave seat has now scored, the practical alternative is to record this as a residual, not to amend.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic10.md` (this report; no other file written). Scratch `/fast/scratch/hyaku/souji-r33/AuditK12` removed after receipts were copied above; no tool installed or upgraded.
