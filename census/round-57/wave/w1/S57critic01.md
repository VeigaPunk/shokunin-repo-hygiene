# S57critic01 — critic, souji round 57 w1

Measurement state: lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `805482129d022b13db672654f5478952def607a6`,
freeze `d749f7ee081ec1b382b2f92577eb22bfba1c7761`, base `b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd`, measured
2026-11-03T23:37Z. All 13 pinned hashes re-derived and matched; `git diff d749f7ee 80548212 -- census/round-57`
is empty (no frozen byte changed since the freeze). Raw command lines and observed output:
`S57critic01/receipts.txt` beside this file. Scratch root `/fast/scratch/hyaku/souji-r57/S57critic01`
(deleted before yield; the two scratch fixture repos were created with `git init` under it and
`git rev-parse --show-toplevel` asserted equal to each).

## Verdicts

| claim | verdict on the frozen predicate | detail |
|---|---|---|
| **C1** (calibration 7) | **SURVIVE** | T1–T7 all observed at the measured revision. The before arm is non-vacuous (v5 exit 0 on B4/C4; exit-0 10/36 vs 8/36). No target is vacuously satisfiable. Two residual shapes are attacked below; both are out of the frozen population, so they do not falsify a target, but they do mean the claim's *title* ("closes the r56 inline-comment over-acceptance") overstates what the frozen grammar implements. |
| **C2** (operability 8) | **SURVIVE on T1, T3, T5-before, T6; the after half is a sequencing fact, not yet instantiated** | At 23:37Z `manifests/after.tsv` did not exist; at 23:38Z a 3-row manifest appeared while `c2-tip.txt` and `standing.txt` were still being written (gate: `receipts=3 findings=2`, two `RECEIPT-MISSING`, rc 1 — a transient, since the wave's own uncommitted evidence keeps the tree dirty and the L1 produces the final manifest only after the wave settles). A 3-row probe of the executor's three recorder receipts yields `SUMMARY receipts=3 findings=0`; each binds rev + committed-blob digest + `EXIT=` (the standing receipt records `EXIT=2 COULD-NOT-EVALUATE dirty worktree`). See “C2 after half” below. |

## 1. Before arm non-vacuous — YES

```
build-fixtures.py --work $S/selftest --manifest .../fixture-manifest.tsv   -> 52 fixtures, rc 0
run-matrix.sh $S $S/matrix                                                -> both TSVs, rc 0
cmp $S/matrix/c1-matrix-v{5,6}.tsv records/matrix-dryrun/...              -> IDENTICAL (both arms)
awk exit==0 : v5 = 10 of 36 ; v6 = 8 of 36
v5 on B4 -> rc=0 filed=2 unfiled=0 ; v5 on C4 -> rc=0 filed=2 unfiled=0
```

The official post-freeze matrices in `records/` are byte-identical to the dry-run and to my
independent rebuild. The v5 exit-0 set is exactly 10 rows, so the 8-vs-10 delta is not vacuous.

## 2. Target is do-nothing-proof — YES for T1 in both claims

- **C1 (change undone).** A scratch copy of v6 with the whole `if indent <= 3:` inline-scan block
  removed (1143 bytes; fence/block paths untouched) scores B4 and C4 at `rc=0 filed=2 unfiled=0`:
  it fails T1 by construction, while C6/F29 stay green. T1 therefore has kill power over exactly
  the claimed change.
- **C1 absent-instrument control.** A nonexistent counter path prints no SUMMARY and exits 2.
- **C2 (always-clean gate).** A stub that counts manifest rows and prints `findings=0` exits 0 with
  no finding over `before.tsv` (`SUMMARY receipts=1 findings=0`, rc 0): it fails T1. The committed
  `controls/c2-stub.py` prints `receipts=0 findings=0`, rc 0: also fails T1.

## 3. Visibility judgement — CORRECT (0, 0, 2, 2)

markdown-it-py **4.2.0** in a scratch venv (`uv 0.13.0`, `uv pip`; no host tool changed), rendered
`git show <tip>:SCORECARD.md`, stripped `<!--...-->` spans (DOTALL), counted `R52-CORRECTION`:

```
B4  raw=2 spans=1 visible=0      C4  raw=2 spans=1 visible=0
C6  raw=2 spans=1 visible=2      F29 raw=2 spans=0 visible=2
LANE@d749f7ee raw=2 spans=0 visible=2   (filed=yes in the counter matches the render)
```

This is the exact expectation in the assignment and it agrees with the v6 hidden-class behaviour.

## 4. T4 counts exact — YES

`v6 exit-0 = 8 of 36`; `v5 exit-0 = 10 of 36` (re-derived from my own run; the committed official
matrices are identical). T3's operative condition also holds: only B4 and C4 change; the other 34
rows are identical in exit code and full ordered finding list.

## 5. Real lane at the measured revision — YES

The preregistration's exact command at `d749f7ee` exits **0** with
`SUMMARY … filed=2 unfiled=0 … fenced=0 … rev=d749f7ee081e base=b4ef0bc84ada` (sites 2,
mismatches 2, record_sha ok). `records/c1-tip.txt` records the same revision and the frozen
instrument pin `e18872…`.

## 6. C2 after half — receipts bind; final population is a sequencing fact

The three recorder receipts in `.ufo/waves/round-57/w1/S57executor02/` each carry
`rev=d749f7ee081ec1b382b2f92577eb22bfba1c7761` (durable: `master` is a descendant), a pin equal to
the committed blob at that rev (`c1-counter.py` `e18872…`, `c2-counter.py` `174d7b8…`,
`round-46/c1-counter.py` `5455fb46…` — all re-derived with `git show rev:path | sha256sum`), and an
`EXIT=` line. A 3-row probe manifest of them gives `SUMMARY receipts=3 findings=0`, rc 0.
The committed population moves: at 23:37Z `manifests/after.tsv` was absent; at 23:38Z it appeared
with 3 rows (`c1-tip.txt`, `c2-tip.txt`, `standing.txt`) while `c2-tip.txt` and `standing.txt` were
still unwritten, so the gate reported `FINDING RECEIPT-MISSING` twice and
`SUMMARY receipts=3 findings=2` (rc 1). That is the expected transient: the L1 produces the final
after manifest only after the wave settles, because the standing receipt needs a clean tree and the
wave's own uncommitted evidence keeps it dirty (`r-standing.txt`: `EXIT=2 COULD-NOT-EVALUATE dirty
worktree at run time: 6 unexpected rows`). T2/T4/T5-over-the-after-manifest are therefore
uninstantiated at my measurement time as a sequencing fact, not a defect; T5's grep is 1 on each of
the three seat receipts and 0 on the base r56 receipt. Re-run after the wave settles:
`python3 -B census/round-57/c2-counter.py --root LANE --manifest census/round-57/manifests/after.tsv`
must print exactly `SUMMARY receipts=3 findings=0`.

## Attacks found (none falsifies a frozen target; classify and route)

| # | class | severity | evidence (this session) | impacted axis |
|---|---|---|---|---|
| A1 | **C1 under-hide (false green): a second `<!--` after the first closer is never opened.** v6 breaks out of the line after the first span, so `…<!-- a --> <!-- b` + filings + a later `-->` counts both filings as filed while markdown-it hides them. Same *harm class* as the r56 B4/C4 defect the claim repairs. Already on record (`records/probe-second-opener-harm.txt`, reviewer01 HIGH; L1 reproduced). | HIGH (out of population) | my scratch fixture: v5 rc=0 filed=2, v6 rc=0 filed=2, render spans=2 visible=0 | calibration 7 |
| A2 | **C1 over-hide (false red) introduced by v6: opener inside an inline code span** (` `<!--` `) followed by a later `-->`. v5 accepted; v6 refuses visible filings. Not in the docstring's named limits. Already on record (`records/probe-code-span-overhide.txt`). | MEDIUM (out of population) | my scratch fixture: v5 rc=0 filed=2; v6 rc=1, 2×`CORRECTION-IN-FENCE hidden_by=inline`; render spans=0 visible=2 | calibration 7 |
| A3 | **T3's frozen parenthetical miscounts its own set** ("33 carried rows minus F17/F18/F19/F29" = 29, while the operative condition is 34 identical rows including C6). Disclosed as ERRATUM-R57-1; both readings hold in my matrix. | prose only | `changed_rows B4,C4`; 34 identical | calibration 7 (documentation) |
| A4 | **C2 target is satisfiable by a refusal receipt.** The gate checks binding, not success: a 3-row manifest including `r-standing.txt` (`EXIT=2 COULD-NOT-EVALUATE dirty worktree`) gives `receipts=3 findings=0` rc 0. T2/T4 say “an `EXIT=` line”, never `EXIT=0`, so the after half can be green with no successful standing-suite measurement. | MEDIUM (target vacuity) | probe run above; seat receipt verbatim | operability 8 |
| A5 | **C2 contract/behaviour mismatch: annotated tag OBJECT id accepted.** Docstring: `RECEIPT-REV-ABSENT` for “a full40 token that names no commit object”; behaviour peels it and reports durable `branch`. Confirmed by reviewer02; lessons line now says accepted. | MEDIUM | scratch repo: `durable_kind(tagobj)=branch`, `check_receipt(...)=[]`; `probe-rev-shapes.txt` | operability 8 |
| A6 | **C2 manifest paths are not confined to `--root`.** An absolute receipt path outside root, or `../` escape, is read and can pass (`SUMMARY receipts=1 findings=0`, rc 0) though the docstring says both paths are relative to `--root`. Corroborates reviewer02. | MEDIUM | scratch repo root vs `$S/outside/receipt.txt` and `../receipts/commit.txt` — both rc 0 | operability 8 |
| A7 | **C2 token provenance is unanchored.** `EXIT=` and `rev=` found anywhere satisfy the check: a receipt with `EXIT=0` embedded in the command output (no trailing line) and a `rev=` mentioned only in prose both pass. `record-receipt.sh` writes the canonical trailing lines, so the round's receipts are fine; a hand-written/forged receipt is not distinguished. | LOW (hardening) | scratch `exitembedded.txt`, `revprose.txt`: `findings=[]` | operability 8 |

Not attacked / not needed: the M1 pair was re-derived (all-findings mutant fails F24, `SELFTEST fail
cases=36`; first-finding-only mutant passes 36/36) — T5's all-findings assertion has real kill power.

## Targets vacuously satisfiable — named

- **C2 T2 (and T4's “EXIT= line”)**: satisfied by a bound receipt that records a *failed* measurement
  (A4). The target measures binding, not that the standing suite ran.
- **C2 T2/T4/T5-after**: uninstantiated at measurement time as a sequencing fact — the final after
  manifest is produced after the wave settles (the 23:38Z 3-row manifest referenced two receipts not
  yet written). Re-run the gate after the receipts land.
- **C1 T7** is non-vacuous here because the claim cites `records/c1-tip.txt` (`EXIT=0`) and the
  selftest/matrix receipts all carry `EXIT=`; the matrix TSVs have no `EXIT=` line but are tables,
  not per-run receipts. No C1 target is vacuously satisfiable.

## Impacted axes

- **C1 calibration 7**: predicate holds (T1–T7); A1 leaves the motivating harm class open in a
  narrower shape and A2 adds an over-hide class — the frozen grammar rule (“first `-->` after the
  opener”) is implemented only for the first opener per line. The wave's own closure reaches
  “not admitted” for the same reason; I concur on the *instrument*, while the frozen targets survive.
- **C2 operability 8**: binding capability works and is mutation-guarded; A4/A5/A6/A7 are gate
  contract weaknesses, and the after half is not yet instantiated.

## Smallest safe corrections (r58; frozen bytes must not be edited)

1. C1: after closing an inline span, continue scanning the remainder of the closer line (and the
   opener line after the closer) for further `<!--` openers; alternatively add the second-opener and
   code-span shapes to the named limits. Add both shapes as fixtures before changing the grammar.
2. C2: require the `EXIT=` line to be the final non-empty line (as `record-receipt.sh` writes it);
   confine `root / rel` to `root`; either require `EXIT=0` (or an explicit admitted-rc column) for the
   after population, or state that a refusal receipt is an acceptable after row; align the
   `RECEIPT-REV-ABSENT` docstring with tag-object peeling (refuse tag objects or document acceptance).

## Tooling record

- `markdown-it-py` 4.2.0 installed with `uv 0.13.0` (`uv venv` + `uv pip install`) into the scratch
  venv only; reason: the visibility judgement. No host tool upgraded, no PATH directory touched.
- No subagent, no background job, no git/jj mutation outside the two scratch fixture repos created
  under `/fast/scratch/hyaku/souji-r57/S57critic01`.
