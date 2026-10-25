# RevR17-2 — falsify R15/R17/R19 record-agreement fix plan

Seat: L1Souji25.RevR17-2 (reviewer, leaf). Lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`, HEAD `6e4737e` (freeze). Scratch `/var/tmp/souji-r25-RevR17/r17-2/` (own subdir; twin seat's `r1/` untouched, removed by it). Evidence below was produced this run; every fixture run used a byte-identical copy of the lane fixture changed only in `SCRATCH_ROOT`. The peer seat `L1Souji25.RevR17` reaches the same headline conclusions in `.ufo/waves/round-25/w1/RevR17.md`; this report adds the second-extended-fixture matrix, the current-draft re-runs, the stderr-only/decoy-anchor probe cases and the receipt-verify neutrality probe, and is written to `RevR17-2.md` per coordination to avoid clobbering.

## Status
STATUS: FAIL (plan as written). The docstring-only change is behavior-neutral, but it is redundant (base already carries r24's code fix and a matching docstring); the plan's red-arm oracle is wrong (the a6d2d15 blob scores 15/15, not 14/15); and the three planned fixture cases do not cover R15's decoy-anchor shape, which remains open on every tool version.

## Axes
- calibration: does the 14/15 → 15/15 witness mean what the prereg says? No — it belongs to r24 (W2R23F4) and needs the c872eec blob, not a6d2d15.
- coverage: do the added cases kill real mutants and cover R15/R17? R17 yes (case 15); R15 no.
- operability: existing cases intact? Yes (12, not 9); the shared hard-coded `SCRATCH_ROOT` is a collision risk.

## Evidence

Blobs (this run):
- old/pre-fix: `c872eec:tools/souji-record-agreement.py` = blob `3a90ddc`, sha256 `dd53c228…` (r23 tool, whole-text last-wins).
- base: `a6d2d15:tools/…` = blob `716731f`, sha256 `41db9ca8…` (already carries the r24 stdout-section fix + docstring describing it).
- committed fixture: blob `2ff3cbb` (r23-record-agreement.py), sha256 `eda4fafa…`.
- ExecR17 drafts at write time: tool `04811c24…`; fixture `40ddcbeb…`.
- ExecR17-2 drafts at write time: tool `ec5b809d…`; fixture `658b2488…`.

AST/neutrality: with docstrings stripped, base == ExecR17 draft == ExecR17-2 draft (AST-equal). `git diff --no-index` base vs either draft touches only docstring lines (module K1 note + `counts_of` docstring). So both tool drafts are docstring-only.

Baseline: committed fixture (byte-identical copy, SCRATCH_ROOT changed) vs committed tool `41db9ca8…` → `selftest=12/12 control=FALSE-GREEN-REJECTED rc=0`. The lane run at a6d2d15 with `--no-worktree` → `keys=4 records=4 occurrences=17 mismatches=0` rc 0 for base, doconly and old alike.

### Matrix A — ExecR17 extended fixture (15 cases)

| tool | score | failing cases |
|---|---|---|
| old `dd53c228` | 14/15 rc 1 | 15 trailing-shadow (expects value-disagree, got M=0) |
| base `41db9ca8` | 15/15 rc 0 | — |
| ExecR17 draft `04811c24` | 15/15 rc 0 | — |
| ExecR17-2 draft `ec5b809d` | 15/15 rc 0 | — |
| my doconly variant | 15/15 rc 0 | — |
| mut-first (`matches[0]`) | 14/15 rc 1 | 14 decoy-line (in-stdout decoy now present) |
| mut-whole (whole-text findall) | 14/15 rc 1 | 15 |
| mut-noend (no stderr end fence) | 14/15 rc 1 | 15 |
| mut-noguard (receipt-rev-object elif deleted) | 14/15 rc 1 | 13 |

### Matrix B — ExecR17-2 extended fixture (15 cases)

| tool | score | failing cases |
|---|---|---|
| old | 14/15 rc 1 | 15 trailing-shadow |
| base / both drafts / doconly | 15/15 rc 0 | — |
| mut-first | 15/15 rc 0 | — (case 14 here is record-side value-disagree, not in-stdout decoy) |
| mut-whole | 14/15 rc 1 | 15 |
| mut-noend | 14/15 rc 1 | 15 |
| mut-noguard | 15/15 rc 0 | — (case 13 expects occurrence-absent, which fires even without the guard) |

Both extended fixtures pass cases 1–12 with every tool and produce output identical to the committed 12-case run. So the "9-case set" in the brief is stale: the committed fixture has had 12 cases since c872eec; the extension is 12 → 15.

### Probe cases I added (on a copy of ExecR17's 15-case fixture; 18 cases total)
- case 16 stderr-only: counts only after the stderr fence, empty stdout. Expect `receipt-malformed`. base/doconly pass; old fails (false green). Discriminates old vs fixed.
- case 17 stdout-last-wins: two counts lines inside stdout (wrong then true). Expect green. base passes; mut-first fails (14/18). Pins last-wins within the section.
- case 18 R15 decoy-anchor (W2K1 F2 shape): calibration-row tuple set wrong and bound to another (real) rev token; a prose decoy quotes the true tuple at the receipt rev. Expect red (K1 ≥1). **Every tool** — old, base, both drafts, doconly — prints `rc=0 mismatches=0` (false green). This is exactly the W2K1 F2 "not anchored to the calibration row" residual.

### Receipt neutrality probe (scratch clone)
`git clone --no-local` of the lane at a6d2d15; committed both ExecR17 drafts at tip and ran `souji-receipt-run.py verify` on the at-base receipt (`record-agreement-at-base.tsv`) and the r23 receipts (`agreement-after.tsv`, `declared-evidence-after.tsv`): all `verify=ok` (rc 0), and the K-run with the draft tool at the clone tip prints the same counts as base. The docstring change does not break the receipt chain.

## Findings
1. **Stale premise — no docstring to correct.** The base tool's docstring already states the stdout-section rule ("A fenced receipt's measured value is its recorded stdout section … Within the section the last match wins") and the code implements it (r24 315422b). The draft rewrites/re-phrases only; AST-equal after docstring strip, behavior identical on committed and extended fixtures and on the real lane. Any SCORECARD/LOG line crediting "docstring correction" as a fix overstates it.
2. **Red arm as written is green.** ExecR17's brief (and the prereg's "OLD tool blob at a6d2d15 → 14/15") is false: that blob (already fixed) scores 15/15. A valid red arm must name `c872eec:tools/souji-record-agreement.py` (`dd53c228…`) → 14/15 (only case 15 fails), or a named mutant. ExecR17's receipts already do this (`red-arm-prefix-3a90ddc.tsv`); the L1 must not accept a red receipt against `41db9ca8`.
3. **The three new cases do discriminate (against the right old blob/mutants):** case 15 kills old, mut-whole, mut-noend; case 13 kills mut-noguard (ExecR17 set); case 14 kills mut-first only when the in-stdout decoy is present (current ExecR17 draft — my earlier copy without it let mut-first score 15/15; the updated draft is the discriminating one). ExecR17-2's set covers a different pair (occurrence-absent; record-side value-disagree) and lets mut-first live.
4. **R15 is not covered by any planned case.** Case 18 (decoy-anchor) false-greens on every tool. R15 is a code-level predicate gap (K1 is not anchored to the calibration row; other-revision tuples are ignored while a decoy supplies `seen`). It cannot be closed by a docstring-plus-fixture change; it needs its own claim/predicate change or stays disclosed. Label the planned case 14 "decoy-line" carefully: it is not the R15 shape.
5. **R19 partial.** The "28 uncovered mutants" figure was measured on the r23 tool; I did not reproduce the full set. Of the sampled single mutants, 13/14/15 kill whole/noend/noguard (+ first in the ExecR17 set, + last-wins in my case 17). Remeasure before claiming an R19 count; at minimum the `matches[0]` mutant should not be reported as covered by ExecR17-2's set.
6. **Operability risk — shared SCRATCH_ROOT.** Both committed and draft fixtures hard-code `/var/tmp/souji-r23-ExecFixtureAgreement` and `rmtree` it at start. Two concurrent runs collide (one deletes the other's in-flight repos). I therefore ran byte-identical copies with `SCRATCH_ROOT` changed and could not run the committed bytes verbatim without racing other seats; the integrator should run the committed baseline/after runs serially or patch the root.

## Adjudication
| plan element | verdict |
|---|---|
| docstring-only correction behavior-neutral | holds (AST-equal, 12/12 and 15/15 identical, lane counts identical) — but redundant |
| 14/15 → 15/15 red-before witness | falsified as specified; valid red arm = c872eec/blob `3a90ddc`/`dd53c228` |
| new cases discriminate | holds against c872eec and named mutants; both drafts' sets pass 1–12 and reach 15/15 |
| R17 trailing-shadow covered | holds (case 15) |
| R15 decoy-anchor covered | falsified (false green on all tools; remains open) |
| R19 | partial — remeasure; sample coverage differs between the two drafts |

Recommended landing (L1 decides): keep the extended fixture (one of the two variants), record the red arm against `c872eec`/`dd53c228` plus named mutants, credit R17's code fix to r24 (315422b), keep R15 open/disclosed, and label the docstring change cosmetic. Consider adding a stderr-only case (kills old) and my stdout-last-wins case (kills `matches[0]`) for the two variants that do not already carry them.

## Attack log
1. Old-blob vs base-vs-draft diff + AST strip: neutral; premise "docstring contradicts code" is stale. Not landed as defect.
2. Committed fixture baseline (byte-identical copy): 12/12 on committed tool and on old/mutants; landed as R19 observation.
3. Extended-fixture runs on both drafts × 9 tools: current-draft matrix above; the a6d2d15 old-arm is green. Landed.
4. My attack cases: stderr-only discriminates (case 16); R15 decoy-anchor false-green on every tool (case 18). Landed.
5. Receipt-chain clone probe with drafts committed: verify=ok on at-base and r23 receipts. No recorded figure affected; no tool installed.
