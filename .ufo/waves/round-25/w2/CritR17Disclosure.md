# CritR17Disclosure — falsify the R17 documentation claim (wave 2)

Seat: `L1Souji25.CritR17Disclosure` (critic, leaf). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Assignment: falsify the R17 record-agreement documentation claim (prereg `Residuals R3/R7/R15/R17`:
"R15/R17 record-agreement docstring correction plus three new fixture cases (14/15 -> 15/15 red-before
witness)"). Read-only; no lane edits; scratch `/var/tmp/souji-r25-CritR17Disclosure/` (will be removed).
No tools installed.

STATUS: FAIL — the claim as written bundles R15 with R17 and implies both are resolved by a docstring
correction. The docstring change is real but cosmetic (behavior-neutral, redundant), the 14/15→15/15
red-before witness belongs to the r24 code fix (the prereg's red arm `a6d2d15` scores 15/15, not 14/15),
and R15 (K1 decoy-anchor) remains open on every tool version including the draft.

## Axes attacked

- calibration: does the "docstring correction + 14/15→15/15 red-before witness" mean what the claim says?
- coverage: do the deliverables (docstring + 3 fixture cases) cover R17 and R15?
- operability: is the working-tree docstring accurate against the code?

## Evidence (all re-derived this run)

### E1. The r25 working-tree change is docstring-only (behavior-neutral)

`git diff HEAD tools/souji-record-agreement.py` (HEAD = 6deb535; base blob `a6d2d15` = `41db9ca8` =
r24-fixed blob from `315422b`):

```
@@ -8,7 +8,8 @@ Four frozen keys …
   K1 after-receipt binding (spot-check D2). Every `assertions=/resolved=/skipped=/mismatches=`
      4-tuple on an `r22`/`round-22` line of SCORECARD.md that names the receipt's `rev=` value
-     must equal the receipt's counts line, and at least one such bound occurrence must exist.
+     must equal the receipt's counts (read as stated under "Receipt counts" below), and at
+     least one such bound occurrence must exist.
@@ -24,6 +25,13 @@ Four frozen keys …
+Receipt counts (K1, K2): a fenced receipt's counts are read only from its recorded stdout
+section, the lines between `--- stdout ---` and `--- stderr ---` (to the end when no stderr
+fence follows); the last counts tuple in that section wins, whether or not a label line follows
+it. Text before the stdout fence and text after the stderr fence is never counted, so a
+post-fence `mismatches=0` cannot shadow a stdout `mismatches=7`. An unfenced receipt is read
+whole, last tuple winning.
```

- AST check: `ast.dump` of HEAD vs working tree with docstring constants emptied is **equal** (verified).
- Both w1 drafts (`w1/souji-record-agreement.py` sha `04811c24…`; `w1/ExecR17-2-souji-record-agreement.py`
  sha `ec5b809d…`) are also AST-equal to HEAD minus docstrings.
- The new "Receipt counts" paragraph matches `counts_of` (`tools/souji-record-agreement.py:124-143`):
  fenced region between `--- stdout ---` and `--- stderr ---`, `--` end when no stderr fence
  (`end = lines.index(STDERR_FENCE, start) if STDERR_FENCE in lines[start:] else len(lines)`),
  last regex match wins (`matches[-1]`), unfenced read whole. Accurate; no behavior change.
- Real-lane parity: `census/round-25/records/record-agreement-at-base.tsv` (`rev=a6d2d15`,
  `tool_sha256=41db9ca8…`) = `keys=4 records=4 occurrences=17 mismatches=0` rc 0; ExecR17/RevR17
  measured identical counts for base and drafts.

Conclusion: the r25 change is **behavior-neutral/cosmetic**. It is also **redundant**: the base blob
already carries the r24 code fix *and* a docstring describing the stdout-section rule
(`counts_of` docstring, `:119-123`). There was no docstring contradiction to correct for R17.

### E2. The red-before oracle in the claim is wrong

- Blob `a6d2d15:tools/souji-record-agreement.py` = `716731f` = sha256 `41db9ca8…` = the r24-fixed
  blob (identical to `315422b:tools/…`, verified by sha256). It scores **15/15** on the extended
  15-case fixture, rc 0 — it is green, not red.
- The only red arm is the pre-fix blob `c872eec:tools/souji-record-agreement.py` = `3a90ddc` =
  sha256 `dd53c228…` → **14/15** (case 15 `trailing-shadow`/`post-stderr-shadow`: got `rc=0
  mismatches=0` false green), rc 1.
- So "14/15 → 15/15" is a witness of the **r24 code fix at `315422b`** (R24-M12 / W2R23F4), not of
  anything r25 changed. Any receipt carrying `tool_sha256=41db9ca8…` as a red arm is invalid.

### E3. R15 (K1 decoy-anchor) is NOT closed by any report or by the draft

- Probe (RevR17-2 case 18 / RevR17 attack case 16, W2K1 F2 shape): calibration-row tuple wrong and
  bound to another real rev token, plus a correct prose decoy at the receipt rev. **Every tool** —
  old `dd53c228`, base `41db9ca8`, both drafts, doconly variant — prints `rc=0 mismatches=0`
  (false green). K1 is not anchored to the calibration row (`seen` is satisfied anywhere in
  SCORECARD.md).
- Report sweep (no report implies closure): ExecR17 "R15 … **still open** … needs a code change in a
  later round"; ExecR17-2 "R15 (K1 decoy-line anchoring) stays a **disclosed limit**"; RevR17 "It must
  not be reported as closed"; RevR17-2 "R15 decoy-anchor covered | falsified … remains open";
  ScoutR17RecordAgreement(-2) "R15 | no … needs K1 row anchoring, a separate claim". The working-tree
  SCORECARD append-only corrections draft itself says: "R15 cross-revision K1 decoy anchoring remains
  open."
- **Two phrasings do risk reading as R15 covered** (correction targets): (a) the prereg residual line
  "R15/R17 record-agreement docstring correction plus three new fixture cases (14/15 -> 15/15
  red-before witness)" bundles R15 into a claim whose witness is R17-only; (b) `scorecard-patch.md`
  H1 row "R15/R17 record-agreement fixture cases (routed; not a claim) | calibration 7 | old tool bytes
  … 14/15 … | selftest=15/15" carries the same bundle. Neither names R15 as fixed, but both need an
  explicit "R17-only; R15 open" qualifier.

### E4. The three new fixture cases are real witnesses (R17), but one label is a hazard

- Cases `post-stderr-shadow`, `stdout-two-line`, `receipt-rev-object` kill distinct mutants the
  committed 12-case fixture lets through: `mut-nofence`/`mut-noend`/old tool (case 15),
  `mut-noguard` (case 13), `mut-first` (case 14, only with the in-stdout decoy present).
  Committed 12-case fixture stays 12/12 everywhere. They are a legitimate r25 addition.
- ExecR17 labels case 14 "decoy-line"; R15's record-side decoy shape is different. The lesson must use
  the shape names, not "decoy", or it reads as R15 covered (ScoutR17RecordAgreement-2 A2).

### E5. Remaining docstring inaccuracy in the working-tree K1 note

- `tools/souji-record-agreement.py:13-14` (working tree): "A tuple on an r22 line that names some
  other revision is outside K1 (the r22 row quotes both ends of its own measurement)." The code
  **contradicts** this for same-value tuples: `k1()` emits `rev-disagree`
  (`tools/souji-record-agreement.py:207-211`: `elif m.group(0) == value and bound != rev` → bad
  "rev-disagree") for a same-value tuple bound to another revision — that is *inside* K1 and a
  mismatch. The lesson skeleton's R25-M1 records this ("the K1 same-revision exclusion statement remains
  inexact"). The r25 rephrase kept the inexact sentence unchanged.

### E6. Stale round-23 lesson statement still unmarked

- `corpus/lessons/round-23.md:144-146` still says "switched counts parsing to last-wins so a
  pre-fence summary line cannot shadow the measured output. All three holes now have fixture cases
  (selftest 12/12)." Per R24-M12 / W2R23F4, a **post-fence** counts line still shadowed stdout until
  `315422b`'s region fix. The r25 append-only correction is planned in the SCORECARD draft
  ("…'s K1 last-wins sentence is superseded by an appended r25 correction") but not yet applied to the
  lesson file.

## Findings (numbered)

1. r25's record-agreement change is docstring-only, behavior-neutral, and cosmetic; verified AST-equal,
   fixture-identical, lane-identical. It corrects nothing the base did not already document (E1).
2. The "14/15 → 15/15 red-before witness" belongs to the r24 code fix (`315422b`). The claimed red arm
   `a6d2d15` scores 15/15; only `c872eec`/`dd53c228` (or a named mutant) is a valid red arm (E2).
3. R15 (K1 decoy-anchor) remains open on every tool version; no seat report closes it, but the prereg
   residual line and the scorecard-patch H1 row bundle R15 into an R17-only witness and need a
   "R17-only; R15 open" qualifier (E3).
4. The three new fixture cases discriminate and are a sound r25 addition, provided the "decoy-line"
   label is not read as R15 coverage (E4).
5. The working-tree K1 docstring sentence (lines 13-14) is inexact: same-value tuples bound to another
   revision are K1 `rev-disagree` mismatches, not "outside K1" (E5).
6. `corpus/lessons/round-23.md:144-146` still overclaims last-wins closed shadowing; the append-only
   supersession note has not landed (E6).

## Smallest safe correction

1. In any r25 report/SCORECARD/lesson text, (a) label the record-agreement docstring change
   **cosmetic**, (b) credit the R17 code fix to **r24 `315422b`**, (c) state the red arm as
   **`c872eec`/`dd53c228`** (14/15 → 15/15) — never `a6d2d15`/`41db9ca8` — and (d) keep **R15 open
   and disclosed**; split the residual row into "R17: fixture cases + cosmetic docstring" and "R15:
   open (K1 row anchoring, needs a separate claim)".
2. `tools/souji-record-agreement.py:13-14`: append the qualifier, e.g. "(a same-value tuple bound to
   another revision is a `rev-disagree` mismatch; only a different-value tuple bound elsewhere is
   outside K1)".
3. `corpus/lessons/round-23.md:144-146`: append an append-only supersession note citing R24-M12 /
   `315422b` and naming the three r25 fixture cases; state that the post-fence shadow was closed by the
   r24 region fix, not by r23's last-wins switch.
4. Use the shape names (`post-stderr-shadow`, `stdout-two-line`, `receipt-rev-object`) instead of
   "decoy-line"/"decoy" in the lesson and SCORECARD.

## Attack log

- `git diff HEAD tools/souji-record-agreement.py`: two docstring hunks only (E1).
- AST strip of HEAD vs working tree and vs both w1 drafts: equal (E1).
- `git show 315422b|a6d2d15|c872eec:tools/souji-record-agreement.py` sha256:
  `41db9ca8…` / `41db9ca8…` / `dd53c228…`; r24-fixed blob == base (E1/E2).
- Read `counts_of` (`:124-143`) and `k1()` (`:171-221`) against the new paragraph and the K1 note:
  paragraph accurate; K1 note inexact (E1/E5).
- Read receipt `census/round-25/records/record-agreement-at-base.tsv` (E1).
- Report sweep for R15 closure: ExecR17, ExecR17-2, RevR17, RevR17-2, ScoutR17RecordAgreement(-2),
  scorecard-patch.md, lesson-skeleton.md, working-tree SCORECARD diff (E3/E4/E5/E6).
- No tool installs; scratch will be removed.
