# RevR17 — falsify the R15/R17/R19 record-agreement fix plan

Seat: L1Souji25.RevR17 (reviewer, leaf). Lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`, HEAD
`6e4737eab43d8fde1b85eb9f57023d29046705b4` (freeze commit; tool and fixture blobs unchanged since base).
Scratch `/var/tmp/souji-r25-RevR17/r1/` (shared root with RevR17-2, who used `r17-2/`; only `r1/` removed).
Evidence copied to `.ufo/waves/round-25/w1/RevR17-evidence/` (all fixture outputs, `fx-attack-17.py`, `sha256.txt`).

## Status
STATUS: FAIL (plan as written). The test mechanics are sound, but the plan's premises and red-arm oracle are wrong.

1. The tool at a6d2d15 already carries the R17 code fix and the corrected docstring. Both landed in
   `315422b` (r24 final), which is an ancestor of the base.
2. Because of that, "OLD tool (a6d2d15 blob) scores 14/15" is impossible. The old tool scores **15/15** on the extended fixture.
3. A docstring-only change can never produce an "old red, new green" split.
4. The R15 decoy-anchor shape is **not covered** by the three planned cases. Every tool version tested gives a false green on it.

## Axes
- calibration: does the red/green witness mean what the prereg says?
- coverage: do the cases kill real mutants and cover the R15/R17 shapes?
- operability: are the existing cases kept intact, and is the change behavior-neutral?

## Evidence

Blobs:
- `pre` = `c872eec:tools/souji-record-agreement.py`, sha256 `dd53c228…`. This is the r23 tool with the trailing-shadow hole.
- `base` = `a6d2d15:tools/…` = HEAD, sha256 `41db9ca8…`, git blob `716731f3…`.
- `exec_tool` = ExecR17 draft `.ufo/waves/round-25/w1/souji-record-agreement.py`, sha256 `04811c24…`.
- `doc` = my own docstring-only variant, used as a second neutral witness.

Mutants of `base`:
- `mut_first`: `matches[-1]` changed to `matches[0]`.
- `mut_noguard`: the `receipt-rev-object` elif deleted.
- `mut_noend`: no stderr end fence.
- `mut_nofence`: whole-text parsing.
- `mut_nofence_first`: whole-text parsing plus first match.

All fixture copies differ from the originals only in `SCRATCH_ROOT`. Tools: git 2.56.0, Python 3.14.8.

### A1. Is the docstring-only correction behavior-neutral? Yes, but it is redundant.
- The `base` and `exec_tool` text diff touches only two hunks, both docstrings: the module docstring at :11 and the
  `counts_of` docstring at :119-122. With docstrings stripped, the AST comparison is **equal**. The same holds for `doc`.
- On the committed 12-case fixture, all three score `selftest=12/12`, rc 0.
- On ExecR17's 15-case fixture, all three score `15/15`, rc 0.
- On the real lane at a6d2d15 with `--no-worktree`, `base`, `doc` and `exec_tool` all print
  `keys=4 records=4 occurrences=17 mismatches=0`, rc 0. This matches `census/round-25/records/record-agreement-at-base.tsv`.
- **Premise falsified:** the base docstring already states the stdout-section rule. It reads: "A fenced receipt's measured
  value is its recorded stdout section, between `--- stdout ---` and `--- stderr ---` … Within the section the last match wins."
  The "docstring contradicts code" defect (RevR23Residuals R17, r24 W2R23F4 F2) was fixed in `315422b`. ExecR17's
  rewrite only rephrases it: it adds "need not be the last stdout line" and a cross-reference at :11.
- The scout task's other premise, "the committed record names neither this shadow shape nor the fix", is also stale.
  `corpus/lessons/round-24.md:334-340` (R24-M12) names the shape, the fix, and the 14/15 → 15/15 witness. Only
  `round-23.md:144-147` lacks it.

### A2. Do the three new cases discriminate? Two do. None does against the a6d2d15 tool.
ExecR17's draft fixture: case 13 is token-moved (receipt `rev=` and the SCORECARD token both moved to a non-commit),
case 14 is decoy-line (a wrong `# summary` line before the stdout fence), and case 15 is trailing-shadow.

| tool | score | failing cases |
|---|---|---|
| pre (`dd53c228`) | 14/15 rc 1 | 15 trailing-shadow |
| **base (a6d2d15)** | **15/15 rc 0** | none |
| exec_tool / doc | 15/15 rc 0 | none |
| mut_noguard | 14/15 | 13 |
| mut_noend, mut_nofence | 14/15 | 15 |
| mut_first | **15/15** | none |
| mut_nofence_first | 14/15 | 14 |

- The prereg says "14/15 → 15/15 red-before witness". That witness exists only with the **c872eec** tool as the old arm.
  It is the r24 W2R23F4 result, already recorded in the r24 lesson. The ExecR17 task's red-arm instruction
  ("OLD tool blob a6d2d15 → 14/15") will instead record 15/15 green. The scout's `matrix.txt` gives the same result:
  base a6d2d15 is 15/15 on `fx-15-w2r23f4.py`.
- Case 15 (trailing-shadow, the R17 shape) is real. It kills `pre`, `mut_noend` and `mut_nofence`.
- Case 13 is real. It kills `mut_noguard`. The name is misleading, though: in W2K1 "token-moved" means the revision
  moved off the tuple's line, which is case 5 (`unbound-tuple`). Case 13 is the r24 `receipt-rev-object` shape.
- Case 14 (decoy-line) is **weak**. Once section anchoring exists, the pre-fence line is already outside the region, so
  single-clause `mut_first` survives. Only the double mutant (whole-text plus first match) fails. It is **not** the R15 decoy.

### A3. Do the cases cover the R15 decoy-anchor and R17 trailing-shadow shapes? R17 yes, R15 no.
I added two attack cases to a copy of ExecR17's fixture (`RevR17-evidence/fx-attack-17.py`):

- **16 decoy-anchor (R15, W2K1 F2):** the calibration row's tuple is set to `…mismatches=9` and bound to another 40-hex
  revision. A prose line quotes the true tuple at the receipt revision.
  - Every tool prints `rc=0 mismatches=0`: pre, base, exec_tool, doc and all mutants. That is a false green.
  - R15 is a predicate gap (K1 is not anchored to the calibration row). No docstring or fixture change closes it.
    Adding this case as "expect red" would fail the fix arm too (16/17). Adding it as "expect green" would freeze the hole.
- **17 stderr-only (r24 M-c):** stdout is empty and the true tuple sits after the stderr fence. Expected `receipt-malformed`.
  - pre, mut_noend and mut_nofence fail. base and exec_tool pass.
  - This discriminates better than case 14: it kills three tools where case 14 kills one double mutant.

### A4. Are the existing cases intact? Yes. Note the count is 12, not 9.
- The baseline committed fixture `eda4fafa…` against the committed tool `41db9ca8…` scores `selftest=12/12`
  `control=FALSE-GREEN-REJECTED`, rc 0.
- The task's "9-case set" is the r23 wave-1 count (`MutCounter`: "the fixture's 9 cases"). The committed fixture has
  had 12 cases since c872eec, so the extension is 12 → 15, consistent with "14/15 → 15/15".
- ExecR17's fixture diff is additions only: a docstring paragraph, two constants, `f_receipt_fenced`, three variants and
  three CASES rows. Cases 1-12 keep their bytes. With the base tool, their `case=` result lines are **identical** to the
  committed fixture's output.
- Side finding (R19): the committed 12-case fixture scores 12/12 on `pre` and on all four single mutants. It has no
  fenced receipt, so none of the r24 fix is guarded by a committed case. The extension is still worth landing as a
  regression guard.

## Adjudication

| plan element | verdict |
|---|---|
| docstring-only correction is behavior-neutral | **holds**: same AST, same fixture scores, same lane counts. **Redundant**: the base docstring already says it. Optional rephrase only; it should not be scored as a fix. |
| "14/15 → 15/15 red-before witness" | **falsified as specified.** At the a6d2d15 old arm the fixture scores 15/15. A valid red arm must name `c872eec:tools/souji-record-agreement.py` (`dd53c228…`) → 14/15 (fails 15), or a named mutant. Since case 13 kills only `mut_noguard`, the receipt should say the witness is mutant-kill coverage, not a before/after of this round's change. |
| three cases cover R17 | **holds**: case 15 is the R17 trailing shadow and discriminates. |
| three cases cover R15 | **falsified**: no case has the decoy-anchor shape, and every tool false-greens on it (attack case 16). R15 needs a K1 code change (anchor to the calibration row, constrain other-revision tuples) or stays a disclosed open residual. It must not be reported as closed. |
| R19 (uncovered mutants) | partial: the extension kills `mut_noguard`, `mut_noend` and `mut_nofence`. `mut_first` survives all 15 cases. Replacing or adding case 14 with `stderr-only` (attack case 17) kills three tools instead of one double mutant. |
| existing cases intact | **holds** (12 cases, byte- and output-identical). |

Recommended prereg-consistent landing (L1 decides):
1. Land ExecR17's fixture extension, optionally with `stderr-only` as a 16th case.
2. Record the red arm against `c872eec`/`dd53c228` plus the named mutants, not against a6d2d15.
3. Mark R17 as "closed in r24 (315422b), fixture guard added r25".
4. Keep R15 open and disclosed.
5. If the docstring rephrase lands, label it cosmetic.

## Attack log
1. Diff and AST comparison, base vs ExecR17 draft vs my own docstring variant: neutral. Not landed as a defect; the premise was stale.
2. Committed fixture run against 8 tool variants: 12/12 everywhere, so it does not discriminate. Landed as an R19 observation.
3. ExecR17's 15-case fixture run against 9 variants: the a6d2d15 old arm is green. **Landed.**
4. R15 decoy-anchor case: false green on every tool. **Landed.**
5. stderr-only case: discriminates. Proposed as an addition.
6. Real-lane run with 4 tools at a6d2d15: all `mismatches=0`. No recorded figure is affected.

## Tooling
None installed or updated. I used the host's git 2.56.0 and Python 3.14.8. The lane was only read (`git show`/`log`/`diff`,
the tool with `--no-worktree`). Files written: this report and `RevR17-evidence/`. Scratch `r1/` removed after writing.
