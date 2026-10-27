# deliver-c1-G21 (SKILL.md:245, r29-registry-agreement cases=20 pass=20)

Seat: SwarmExecutor04 (leaf, C1 slice 4/12). Lane base 9c76c7222a8abff027af42e37f0d160d52526bba;
freeze / --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8. Scratch: /fast/scratch/hyaku/souji-r34/RestateC1s4.

## Status

STATUS: FAIL (honest row rejected by the frozen counter). The row is an argv correction: the SKILL row writes
`--tool tools/souji-registry-agreement.py` (relative) and the fixture resolves that path against its own
`cwd=/var/tmp/souji-r29-c1-fixture`, so the tool never loads (cases=20 pass=0, exit 1). The corrected argv
(absolute tool path) prints the stated line at exit 0. The counter rejects the honest cause 1dc6785 with
`BAD-CAUSE(cause did not write the row's line)` because the r34 items file numbers lines 0-based while the
counter's argv-correction path indexes 1-based; the same off-by-one ACCEPTS a bogus cause (r27's 6cb22dc).
Routed as ATTACK A-2 in SwarmExecutor04.md.

## Counter ITEM line (base reading)

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
      --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
      --scratch /fast/scratch/hyaku/souji-r34/RestateC1s4/cnt --only G21

    ITEM	G21	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=FAIL rev-not-40-hex: rc=2 summary=None lines=[] stderr=/usr/bin/python3: can't open file '/var/tmp/souji-r29-c1-fixture/tools/souji-registry-agreement.py': [Errno 2] No such file or directory load=4.20

## Prior-correction grep (Q76)

At 9c76c72, `git show 9c76c72:SCORECARD.md`:

- `Round 34 registry restatements` -> ABSENT
- `r29-registry-agreement` -> line 313 only (the r29 capability cell "declared-record agreement audit (r29)")
- `cases=20 pass=20` -> line 401, `| L36 | SCORECARD.md:313 | cases=20 pass=20 | run: python3 -B tests/fixtures/r29-registry-agreement.py |`

L36 binds the **SCORECARD.md:313** cell and its run form is the default (absolute DEFAULT_TOOL) invocation; it
does not bind the SKILL.md registry row this item names. No prior correction/supersession binds G21.

## Cause (executed)

Cause: **1dc678500c92164b0b2bea82b934dd03d1dfbf38** (round-29: C3 F3 duplicate-verdict entries ...) - the commit
that wrote SKILL.md's `souji-registry-agreement` registry line, verified verbatim at that commit (21 gaps
earlier in the file; the row reads `... | `python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py` -> `cases=20 pass=20 control=FALSE-GREEN-REJECTED`, rc 0; ...`).
The fixture's cwd=BASE behaviour landed earlier at 8aaacf518d0dc9292d5258abf7d74bdaea1b76e7 (r29 C1 repairs),
an ancestor of 1dc6785.

Executed at the cause (private clone, detach, scrubbed PATH + jj symlink, GIT_CONFIG_NOSYSTEM=1, fresh TMPDIR;
cwd = clone root):

- the row's own (frozen) argv `python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py`
  -> RC=1, prints `cases=20 pass=0 control=FALSE-GREEN-REJECTED`, first FAILs
  `stderr=/usr/bin/python3: can't open file '/var/tmp/souji-r29-c1-fixture/tools/souji-registry-agreement.py'`
  (loadavg 29.79 17.16 8.42) - so the row's argv already failed at the cause.
- corrected argv `python3 -B tests/fixtures/r29-registry-agreement.py --tool "$PWD/tools/souji-registry-agreement.py"`
  -> RC=0, last line `cases=20 pass=20 control=FALSE-GREEN-REJECTED` (loadavg 30.52 17.52 8.59).

Executed at the measured revision 9c76c72 (counter argv, {REV} substituted; loadavg 7.02 4.26 2.59):
frozen argv RC=1 `cases=20 pass=0 ...`; corrected argv RC=0 `cases=20 pass=20 control=FALSE-GREEN-REJECTED`.

Corrected argv names the row's own files (`tests/fixtures/r29-registry-agreement.py`,
`tools/souji-registry-agreement.py`); the statement equals the run's LAST digit-bearing line (proven: the
counter itself reports `statement is the run's last digit-bearing line` under the bogus-cause test below).

Tip reading: not executable at draft time (the C1 landing/tip commit does not exist yet). C1's touched set does
not modify `tests/fixtures/r29-registry-agreement.py` or `tools/souji-registry-agreement.py`, so the corrected
argv's 20/20 carries to the landing commit and the tip [INFERENCE].

## Proposed row (honest; counter-rejected on its cause check)

    | G21 | SKILL.md:245 | restated | 0 | `python3 -B tests/fixtures/r29-registry-agreement.py --tool "$PWD/tools/souji-registry-agreement.py"` | `cases=20 pass=20 control=FALSE-GREEN-REJECTED` | 1dc678500c92164b0b2bea82b934dd03d1dfbf38 | the fixture runs the tool with cwd=/var/tmp/souji-r29-c1-fixture, so the row's relative --tool path never loads; the absolute path prints 20/20 at exit 0 |

Acceptance test (scratch clone at list-rev + this row + the G17b row, commit
a04274a1a9770e36e10b02ebc7c942d5fc4526df, loadavg 43.24 25.61 12.48):

    ITEM	G21	MISMATCH	restated	BAD-CAUSE(cause did not write the row's line)

Root cause of the rejection (off-by-one): the counter's argv-correction path reads
`blob(list_rev, "SKILL.md").split("\n")[lineno-1]` with `lineno=245` (c1-counter.py:271-274), i.e. index 244,
which is the r20/`souji-pre-report-gate` row, not the `souji-registry-agreement` row at 1-based 246:

    index 244 -> | souji-pre-report-gate | gate | `bash tools/souji-pre-report-gate.sh --lane ABS --branch ...
    index 245 -> | souji-registry-agreement | gate | `python3 -B tools/souji-registry-agreement.py --root L...

Counter-accepted forgery (proves the gate is inverted, not merely strict): same corrected argv/statement with
the BOGUS cause **6cb22dc20c9fdb3c7a49eaa1accabca339054c17** (round-27, the commit that wrote the
pre-report-gate row; it predates the r29 fixture entirely), scratch clone commit
228ad4e1385a5e902570fa89e8f69b0083a8475c, loadavg 43.24 25.61 12.48:

    ITEM	G21	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=cases=20 pass=20 control=FALSE-GREEN-REJECTED load=43.24
    SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=228ad4e1385a5e902570fa89e8f69b0083a8475c
    EXIT=0

## Deliveries

This file. No SCORECARD/SKILL bytes written by this seat.
