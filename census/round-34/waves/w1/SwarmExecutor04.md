# SwarmExecutor04 — r34 w1, C1 slice 4/12 (G17b, G18, G19, G20, G21)

## Status

STATUS: PARTIAL — the five items were executed at the base reading; G18, G19 and G20 AGREE (no row), G17b and
G21 MISMATCH and each has an honest restatement drafted and *executed*, but the frozen counter rejects both
honest rows: G17b on `BAD-ROW(cause touches none of the item files)` and G21 on `BAD-CAUSE(cause did not write
the row's line)`. Both rejections are instrument defects, not stale-registry defects, and are reproduced below
as ATTACK A-1 and A-2 (A-2 also shows the same gate ACCEPTS a bogus cause).

## Evidence

Base reading (one run, `flock`-serialized, TMPDIR under my scratch; loadavg `4.20 3.14 2.10` beside it):

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
      --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
      --scratch /fast/scratch/hyaku/souji-r34/RestateC1s4/cnt --only G17b,G18,G19,G20,G21

    ITEM	G17b	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=Note: switching to '9c76c7222a8abff027af42e37f0d160d52526bba'. load=4.15
    ITEM	G18	AGREE	original	rc=0 expect_exit=0 predicate holds last="total": 258 load=4.15
    ITEM	G19	AGREE	original	rc=0 expect_exit=0 predicate holds last="survived": 7 load=4.22
    ITEM	G20	AGREE	original	rc=0 expect_exit=0 predicate holds last=cases=4 pass=4 control=FALSE-GREEN-REJECTED load=4.20
    ITEM	G21	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=FAIL rev-not-40-hex: rc=2 summary=None lines=[] stderr=/usr/bin/python3: can't open file '/var/tmp/souji-r29-c1-fixture/tools/souji-registry-agreement.py': [Errno 2] No such file or directory load=4.20
    SUMMARY items=5 agree=3 mismatches=2 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba

Prior-correction sweep (Q76) at 9c76c72 over `git show 9c76c72:SCORECARD.md` (525 lines):

- `Round 34 registry restatements` — absent.
- `r21-acceptance` -> line 15; `replay-matrix` -> none; `matched=18/18` -> line 394 `L28` binding
  **SCORECARD.md:170**, not the SKILL row G17b names.
- `r22-result-oracle`, `total": 258`, `all258`, `mutation-adequacy`, `59-mutant` -> no match (`mutants` only
  as prose on line 414).
- `r27-pre-report-gate` / `cases=4 pass=4` -> line 33 only (round-27 C3 measurement cell, not the SKILL row).
- `r29-registry-agreement` -> line 313; `cases=20 pass=20` -> line 401 `L36` binding **SCORECARD.md:313** with
  the default (absolute-tool) invocation, not the SKILL row G21 names.

So none of the five items is already bound by a prior correction row; the three AGREE readings are the
counter's own.

Executed cause walk, G17b (value drift). Private clone per revision, origin dropped, toplevel asserted,
`PATH=/usr/bin:/bin` + jj symlink, `GIT_CONFIG_NOSYSTEM=1`, fresh TMPDIR; argv =
`bash census/round-21/replay-matrix.sh --runner census/round-21/run-acceptance.py --lane "$PWD" --rev <rev> --work <scratch>/rm-<tag>`:

| rev | role | result | load |
|---|---|---|---|
| 4f83fd222ffbd8825340221a8c426550ef891191 | last r22 runner commit | RC=0 `matched=18/18` x3, COUNT=3 | `53.07 34.73 17.24` |
| 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 | parent of 98e5203 | RC=0 `matched=18/18` x3, COUNT=3 | `21.97 12.27 6.20` |
| 98e5203d45b4e419a9e72801733d93303acc7ebd | cause | RC=1 `matched=16/18` x3, COUNT=0 | `29.36 15.59 7.61` |
| a416d0b26495ce78b76ea82316533bd8a9ef368c | first parent of a7c35c2 (r33 runner commit) | RC=1 `matched=16/18` x3 | `56.80 39.92 20.33` |
| 9c76c7222a8abff027af42e37f0d160d52526bba | measured rev | RC=1 `matched=16/18` x3 | `4.20 3.14 2.10` |

Executed cause walk, G21 (argv correction). Cause **1dc678500c92164b0b2bea82b934dd03d1dfbf38** wrote the
`souji-registry-agreement` SKILL line verbatim (fixture `cwd=BASE` landed earlier at
8aaacf518d0dc9292d5258abf7d74bdaea1b76e7, an ancestor). At the cause: frozen argv RC=1
`cases=20 pass=0 control=FALSE-GREEN-REJECTED` (load `29.79 17.16 8.42`); corrected argv
`--tool "$PWD/tools/souji-registry-agreement.py"` RC=0 `cases=20 pass=20 control=FALSE-GREEN-REJECTED`
(load `30.52 17.52 8.59`). At the measured rev: frozen RC=1 pass=0, corrected RC=0 pass=20
(load `7.02 4.26 2.59`).

Counter acceptance tests of the honest rows (scratch clones of the list-rev with one appended
`### Round 34 registry restatements` section, throwaway identity, `--list-rev` = the freeze):

    ITEM	G17b	MISMATCH	restated	BAD-ROW(cause touches none of the item files)
    ITEM	G21	MISMATCH	restated	BAD-CAUSE(cause did not write the row's line)
    SUMMARY items=2 agree=0 mismatches=2 restated=2 partial=1 rev=a04274a1a9770e36e10b02ebc7c942d5fc4526df   (load 43.24 25.61 12.48)

    ITEM	G21	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=cases=20 pass=20 control=FALSE-GREEN-REJECTED load=43.24
    SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=228ad4e1385a5e902570fa89e8f69b0083a8475c   (same bogus-cause forgery)

## Findings

1. **G17b value drift is real and starts at 98e5203, outside the item's `files` cell.** SKILL.md's
   `r21-acceptance` row (1-based line 236; the item's `where` is the 0-based 235) claims
   `matched=18/18` exit 0 for the replay matrix. Since round-32's bwrap shim
   (`tests/fixtures/r20-input-binding.py:1296-1310`, `tests/fixtures/r20-audit-contract.py:668-680`) the matrix
   prints `matched=16/18` exit 1 at every revision >= 98e5203, because
   `census/round-21/run-acceptance.py:623/629` stages the payload under literal `/var/tmp` and the shim
   `--bind private /var/tmp --chdir <cwd>` makes that staged cwd disappear
   (`bwrap: Can't chdir to /var/tmp/souji-r21-replay-*/src`). Item `files` = `census/round-21/run-acceptance.py`
   only; 98e5203 touches none of it, and every commit that does touch it either holds (up to 4f83fd2) or
   already fails at its own parent (a7c35c2 at a416d0b). Hence no admissible cause exists.
2. **Restated-statement binding is over stdout+stderr.** `c1-counter.py:296-302` compares a restated statement
   to the collapsed last digit-bearing line of `stdout + stderr`; for G17b that line is the git advisory
   `Note: switching to '<rev>'.` (see the ITEM line), so the honest measurement line
   `MATRIX scenarios=3 replayed=0 summaries_equal=True` cannot be stated.
3. **Items are 0-based, the argv-correction cause path is 1-based.** `c1-counter.py:271-274` reads
   `blob(list_rev, "SKILL.md").split("\n")[lineno-1]` with the item's `where` (e.g. 245 -> index 244 =
   the `souji-pre-report-gate` row, not `souji-registry-agreement` at index 245).
4. **G21's claim is stale by a relative path, not by value.** The fixture resolves `--tool` against
   `cwd=/var/tmp/souji-r29-c1-fixture`, so the row's own relative argv has printed `cases=20 pass=0` since the
   row was written (1dc6785); the absolute-path form prints the stated 20/20 at exit 0. L36 (SCORECARD.md:313)
   already happened to use the working default invocation, so the defect stayed invisible at SCORECARD level.
5. **AGREE readings are unchanged by the round's own appended bytes** [INFERENCE]: G18/G19/G20 run no
   SCORECARD/SKILL/census-34 file, so their base readings carry to the landing commit and the tip; C1's
   touched set does not modify `tools/`, `census/round-21/`, or `census/round-22/`.

## Attack log

**A-1 (frozen item `files` cell, G17b).** State reproduced: honest value-drift row with cause 98e5203 ->
`BAD-ROW(cause touches none of the item files)` (rev a04274a). The parent/cause executions (7a6667c -> 18/18
rc 0; 98e5203 -> 16/18 rc 1) satisfy the drift semantics exactly; only the frozen `files` cell
(`census/round-21/run-acceptance.py`) excludes the commit that carries the mechanism. Consequence: G17b cannot
agree honestly under the frozen bytes; any row that would pass must name a cause that does not contain the
drift.

**A-2 (line-number base mismatch, G21 and every SKILL row).** State reproduced twice: the honest cause
1dc6785 (which wrote the row's line) -> `BAD-CAUSE(cause did not write the row's line)`; the bogus cause
6cb22dc (round-27, the commit that wrote the *previous* row, predating the r29 fixture) -> `AGREE` exit 0 with
the identical argv/statement. So the gate rejects truth and accepts a forgery; a seat that noticed the
off-by-one could land a passing row with a cause that has nothing to do with the claim. No amendment can be
applied honestly without acknowledging that the frozen item numbering is 0-based while the counter is not.

Both attacks are reported, not acted on: frozen items, predicates and counter bytes were not edited, and no
row was written into SCORECARD.md/SKILL.md (this seat is read-only for the lane).

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-G17b.md` (MISMATCH: ITEM line, prior grep, executed cause walk, proposed
  row, rejection receipt)
- `.ufo/waves/round-34/w1/deliver-c1-G18.md` (AGREE)
- `.ufo/waves/round-34/w1/deliver-c1-G19.md` (AGREE)
- `.ufo/waves/round-34/w1/deliver-c1-G20.md` (AGREE)
- `.ufo/waves/round-34/w1/deliver-c1-G21.md` (MISMATCH: ITEM line, prior grep, executed cause readings,
  proposed row, both rejection and forgery-acceptance receipts)
- this report

Tooling: nothing installed or upgraded (no pacman, no uv/npx). Scratch `/fast/scratch/hyaku/souji-r34/RestateC1s4`
removed after the receipts above were written.
