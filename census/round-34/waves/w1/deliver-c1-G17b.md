# deliver-c1-G17b (SKILL.md:235, replay-matrix 18/18)

Seat: SwarmExecutor04 (leaf, C1 slice 4/12). Lane base 9c76c7222a8abff027af42e37f0d160d52526bba;
freeze / --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8. Scratch: /fast/scratch/hyaku/souji-r34/RestateC1s4.

## Status

STATUS: FAIL (honestly un-restatable under the frozen bytes). The base reading mismatches, the true
value-drift cause is 98e5203d45b4e419a9e72801733d93303acc7ebd, and that commit touches neither
`census/round-21/run-acceptance.py` (the item's frozen `files` cell) so the counter rejects the honest row:
`BAD-ROW(cause touches none of the item files)`. Routed as ATTACK A-1 in SwarmExecutor04.md.

## Counter ITEM line (base reading)

    python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
      --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
      --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
      --scratch /fast/scratch/hyaku/souji-r34/RestateC1s4/cnt --only G17b

    ITEM	G17b	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=Note: switching to '9c76c7222a8abff027af42e37f0d160d52526bba'. load=4.15

(load beside the reading: `4.20 3.14 2.10` after the SUMMARY line; run under
`flock /fast/scratch/hyaku/souji-r34/RestateC1s4/cnt/flock.global`.)

## Prior-correction grep (Q76)

At 9c76c72, `git show 9c76c72:SCORECARD.md` (525 lines) greps:

- `Round 34 registry restatements` -> ABSENT
- `r21-acceptance` -> line 15 only (the r21 measurements cell, not this SKILL row)
- `replay-matrix` -> no match in SCORECARD.md
- `matched=18/18` -> line 394, `| L28 | SCORECARD.md:170 | matched=18/18 | record: census/round-21/final-code-verification.json |`

L28 binds the **SCORECARD.md:170** cell, not the SKILL.md registry row this item names, so no prior
correction/supersession binds G17b. The r33 restatement rows (`### Round 33 capability currency`, SCORECARD
lines 502-506) bind SCORECARD cells only.

## Cause (executed)

Cause: **98e5203d45b4e419a9e72801733d93303acc7ebd** (round-32: C2 scratch discipline - 26 tools and fixtures
take scratch from TMPDIR; r20 fixtures run inside a private /var/tmp backed by TMPDIR), parent
**7a6667cd27652baf8d704b5cdb8e3200bd6e27a1**.

Each reading: private `git clone --no-local` (origin dropped, toplevel asserted), detach at the revision,
`PATH=/usr/bin:/bin` + a `jj` symlink dir, `GIT_CONFIG_NOSYSTEM=1`, fresh TMPDIR under my scratch, argv
`bash census/round-21/replay-matrix.sh --runner census/round-21/run-acceptance.py --lane "$PWD" --rev <rev> --work <scratch>/rm-<tag>`
(the frozen item argv with {CLONE}/{REV}/{SCRATCH} substituted).

parent 7a6667c -> HOLDS (exit 0, COUNT == 3):

    RC=0
    SCENARIO	S1	exit=0	matched=18/18	src_sample_unchanged=yes
    SCENARIO	S2	exit=0	matched=18/18	src_sample_unchanged=yes
    SCENARIO	S3	exit=0	matched=18/18	src_sample_unchanged=yes
    MATRIX	scenarios=3	replayed=3	summaries_equal=True
    loadavg 21.97 12.27 6.20

cause 98e5203 -> FAILS (exit 1, COUNT == 0):

    RC=1
    SCENARIO	S1	exit=1	matched=16/18	src_sample_unchanged=yes
    SCENARIO	S2	exit=1	matched=16/18	src_sample_unchanged=yes
    SCENARIO	S3	exit=1	matched=16/18	src_sample_unchanged=yes
    MATRIX	scenarios=3	replayed=0	summaries_equal=True
    loadavg 29.36 15.59 7.61

Base 9c76c72 (same argv, the measured revision) -> FAILS identically (16/18, rc 1); the counter's own
`last=` line above is from that run. Tip reading: not executable at draft time (no landing/tip commit exists);
C1's touched set changes none of `census/round-21/run-acceptance.py`, `tests/fixtures/r20-*.py` or
`tools/`, so 16/18 carries to both [INFERENCE].

Mechanism (98e5203 hunk, tests/fixtures/r20-input-binding.py; tests/fixtures/r20-audit-contract.py carries the
same shim):

    bwrap --dev-bind / / --bind private /var/tmp --chdir os.getcwd() ...

`census/round-21/run-acceptance.py` stages its payload with
`tempfile.TemporaryDirectory(prefix="souji-r21-replay-", dir="/var/tmp")` (line 623/629), so the two r20
fixtures re-exec under bwrap with `--chdir` pointing at a path *inside the rebind target*; the bound
`private` dir does not contain it, so bwrap refuses:
`bwrap: Can't chdir to /var/tmp/souji-r21-replay-<x>/src: No such file or directory` and those two of the 18
programs are lost (16/18).

## History walk over the item's files (executed)

`git log --format=%H -- census/round-21/run-acceptance.py` = 8513d6a, ff425ab, 7753ed4, 1957154, 36c78ba,
4f83fd2, a7c35c2. Two probes bound the flip:

- 4f83fd222ffbd8825340221a8c426550ef891191 (last r22 runner commit) -> RC=0, matched=18/18 x3, loadavg 53.07 34.73 17.24
- a416d0b26495ce78b76ea82316533bd8a9ef368c (first parent of the r33 runner commit a7c35c2) -> RC=1, matched=16/18 x3, loadavg 56.80 39.92 20.33

So every run-acceptance.py commit after r32 already fails at its own parent, and no commit in the item's
`files` history satisfies "holds at parent, fails at it". The flip lives in 98e5203, which changes
`tests/fixtures/r20-audit-contract.py` and `tests/fixtures/r20-input-binding.py` (plus 24 tools/fixtures) and
no `census/round-21/` file.

## Proposed row (honest; counter-rejected)

    | G17b | SKILL.md:235 | restated | 1 | same | `MATRIX scenarios=3 replayed=0 summaries_equal=True` | 98e5203d45b4e419a9e72801733d93303acc7ebd | r32's bwrap shim rebinds /var/tmp under the r21 staging dir, so the two r20 payload fixtures die with "Can't chdir to /var/tmp/souji-r21-replay-*/src" and the matrix prints 16/18 at exit 1 |

Acceptance test of that row (scratch clone at the list-rev + one appended row, throwaway identity, commit
a04274a1a9770e36e10b02ebc7c942d5fc4526df, counter run with loadavg 43.24 25.61 12.48):

    ITEM	G17b	MISMATCH	restated	BAD-ROW(cause touches none of the item files)
    SUMMARY items=2 agree=0 mismatches=2 restated=2 partial=1 rev=a04274a1a9770e36e10b02ebc7c942d5fc4526df

Second, independent blocker if the files gate were relaxed: the counter binds a restated statement to the run's
collapsed LAST digit-bearing line over stdout **and stderr**; the observed last such line for this argv is the
git advisory `Note: switching to '<rev>'.` (see the base ITEM line). The honest measurement line
`MATRIX scenarios=3 replayed=0 summaries_equal=True` is therefore not an acceptable statement under A1(c)
[derived from c1-counter.py:296-302 and the observed ITEM line; not separately executed].

## Deliveries

This file. No SCORECARD/SKILL bytes written by this seat.
