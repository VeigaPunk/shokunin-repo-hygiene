# ScribeAxisDocs — round 26 W1, axis-of-surface documentation drafts (C3 lane support)

## Status

STATUS: PARTIAL — the three requested drafts are written, quoted and land-pinned at
`.ufo/waves/round-26/w1/axis-check-docs.md`; the two SKILL.md rows pin the frozen K2 literal, which the
landed fixture cannot produce (11 cases, `--tool` ignored), and the tool draft the peer report tells the
L1 to install scores 6/12 on the frozen case set.

## Evidence

Revisions: lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; working HEAD at first read
`44531281914ddd200432cdc7dae8ad958c5447e3`; working HEAD at close
`d6c13b0f00066cbb342fdc50167849a5f1c726e5`. `git diff --stat HEAD -- tools/souji-axis-check.py
tests/fixtures/r26-axis-check.py` is empty, so both instrument files are committed and byte-identical
across those two revisions.

Deliverable: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/axis-check-docs.md`
(14,534 bytes). It contains (a) the Q59 row + `## Round 26 criteria` block to append at
`corpus/QUALITY.md` EOF after :142, (b) the `souji-axis-check` and `r26-axis-check` rows to append
after `SKILL.md:223`, (c) the taxonomy paragraph to land in `corpus/lessons/round-26.md` under
`## Gate` before `### Opened sources and curation (2026-10-25)`. Nothing was inserted into QUALITY.md
or SKILL.md.

Runs (all `python3 -B`, `TMPDIR=/var/tmp/souji-r26-ScribeAxisDocs`, from the lane root):

```
$ python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0                                              rc=0

$ python3 -B tests/fixtures/r26-axis-check.py
...
cases=11 pass=11                                              rc=0      (no control= line)

$ python3 -B tests/fixtures/r26-axis-check.py --tool tests/souji-axis-check.py
cases=11 pass=11                                              rc=0      (identical; --tool ignored)

$ python3 -B tests/fixtures/r26-axis-check.py --stub
cases=11 pass=4
control=FALSE-GREEN-REJECTED                                 rc=1
```

```
$ python3 -B .ufo/waves/round-26/w1/r26-axis-check.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-axis-check.py
CASE 12 control-always-green-stub PASS stub_passed=2/11 discriminator=PASS control=FALSE-GREEN-REJECTED
cases=12 pass=12 control=FALSE-GREEN-REJECTED                rc=0      <- frozen K2 literal, unlanded

$ python3 -B .ufo/waves/round-26/w1/r26-axis-check.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/souji-axis-check.py
CASE 7 r3-no-claim-on-lowest-axis FAIL rc=0 claims=2 flags=0 rules=-
CASE 10 wellformed-surface-class-and-enumerate FAIL rc=1 claims=1 flags=1 rules=R3
cases=12 pass=6 control=FALSE-GREEN-REJECTED                 rc=1
```

Synthetic r25-C2 replica (fixture-expansion on operability + one calibration claim), scratch prereg:

```
FLAG C1 R2 surface-class 'fixture-expansion' declared on 'operability'; allowed only on 'coverage'
claims=2 flags=1                                              rc=1
```

```
$ sha256sum tools/souji-axis-check.py tests/fixtures/r26-axis-check.py w1/souji-axis-check.py w1/r26-axis-check.py
14bc9632…  tools/souji-axis-check.py
2ffc1828…  tests/fixtures/r26-axis-check.py
0805afff…  .ufo/waves/round-26/w1/souji-axis-check.py
220eed2e…  .ufo/waves/round-26/w1/r26-axis-check.py
```

Committed C3 receipts: `census/round-26/records/c3-after.tsv` binds rev `d2e6253`, stdout
`axis_check_tool=present` / `claims=3 flags=0` / `axis_check_exit=0`; `c3-control.tsv` binds the same
rev with `cases=11 pass=4` and `control=FALSE-GREEN-REJECTED`, rc 1.

Anchors read this run: `corpus/QUALITY.md` 142 lines, `## Round 25 criteria` :137, header :139,
separator :140, Q57 :141, Q58 :142 (EOF); older header shape `applies-to | test | lesson` at :23, :47,
:54, :62, :69, :76, :88, :96. `SKILL.md` registry header :177, separator :178, last row
`r22-mutation-adequacy` :223, blank :224, `Sources for this skill` :225. `corpus/lessons/round-25.md`
C2 row :10, boundary paragraph :13, `## Gate` :25, `### Opened sources and curation (2026-10-25)`
:27. `corpus/lessons/round-26.md` does not exist.

Quotes used in (c), each from bytes opened this run, each ≤25 words, none containing a pipe:
`corpus/lessons/round-25.md:10` "W2 review shows the change is coverage of edge classes, not a change
to runnable operability" (17 words) and "unprovable on the declared axis" (6); `:13` "C2's actual
surface is coverage, which overlaps C3; it cannot be silently reassigned" (15); prereg C3 R2 "This is
the r25-C2 shape made mechanical." (7).

Writes: only `w1/axis-check-docs.md` and this report. Scratch `/var/tmp/souji-r26-ScribeAxisDocs`
removed. Tooling: nothing installed or upgraded; no `pacman` call.

## Findings

1. **Landed fixture is the 11-case copy; K2 is unproducible at its landing path.**
   `tests/fixtures/r26-axis-check.py:198-220` runs `CASES` of length 11 and prints `cases=11 pass=11`
   with no `control=` token in normal mode; the frozen C3 K2 target is
   `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, exit 0. Location:
   `tests/fixtures/r26-axis-check.py:198-220`, prereg C3 `FROZEN COUNTERS` K2.

2. **`--tool PATH` is accepted and ignored.** The tool path is the module constant `TOOL`; the stub arm
   is the `--stub` flag (`tests/fixtures/r26-axis-check.py:198-201`). The frozen K2 command therefore
   selects nothing and still exits 0 on the stale case set.

3. **The frozen 12-case fixture exists only as an unlanded draft, and it does pass.** 
   `.ufo/waves/round-26/w1/r26-axis-check.py` (sha `220eed2e…`, 11 named cases + case-12 control,
   case 1 = `r25-c2-replica-fixture-expansion-on-operability`) run against the landed tool prints
   `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0 (observed above). Installing it at
   `tests/fixtures/r26-axis-check.py` is the only step between the current tree and K2.

4. **The tool draft named for installation is the weaker copy.** `w1/souji-axis-check.py` (sha
   `0805afff…`, 227 lines) is what `ExecAxisTool.md:129` tells the L1 to copy to
   `tools/souji-axis-check.py`; it scores 6/12 against the 12-case fixture, with case 7
   (`r3-no-claim-on-lowest-axis`) returning rc 0 and no R3 flag at all. The landed tool
   (`tools/souji-axis-check.py`, sha `14bc9632…`) is the copy that satisfies the case set. Location:
   `ExecAxisTool.md:129`, `w1/souji-axis-check.py` R3 block.

5. **The committed control receipt records the 11-case set.** `census/round-26/records/c3-control.tsv`
   lines 10-21: `cases=11 pass=4`, `control=FALSE-GREEN-REJECTED`, rc 1 at rev `d2e6253`; no committed
   receipt records the `cases=12 pass=12` positive arm, and `c3-after.tsv` binds only the K1 half.

6. **R4's prose qualifier predicate is not discriminated by the landed instrument.**
   `tools/souji-axis-check.py:72` captures only `axis|surface-class|enumerate`, so a `text:` line is
   never read; the quantifier scan at `:120` covers the `enumerate:` value. Frozen case 8 passes only
   because that claim has no `enumerate:` line, not because a quantifier was matched. [INFERENCE, not
   executed as a mutant: deleting the quantifier scan would leave the landed fixture at 11/11.]
   Location: `tools/souji-axis-check.py:72`, `:120`.

7. **Neutral surface classes open an R2 bypass that the frozen contract does not name.**
   `tools/souji-axis-check.py:41` (`NEUTRAL_SURFACES = {"receipt-binding", "measurement"}`) and
   `w1/souji-axis-check.py:46` treat unlisted classes as neutral, and the 12-case fixture's case 10
   blesses `surface-class: measurement` as clean (`w1/r26-axis-check.py:229-236`). Any claim can
   therefore declare an unnamed class and skip the axis/surface binding the rule exists to enforce.
   Frozen C3 R2 names four classes only. Location: `tools/souji-axis-check.py:41`, `:170`.

8. **Q59 landing has a pointer precondition and a placement ambiguity, both recorded in the
   deliverable.** `tools/souji-landing-gate.py:905-990` scans `corpus/QUALITY.md` (`:922`) with
   `POINTER_PATH_RE` (`:141-146`) and emits `LG-DANGLING-PTR` for absent `corpus/...` paths, so the
   row's `corpus/lessons/round-26.md R26-M1` citation requires that lesson file to exist at the graded
   tip; the file does not exist yet. Prereg C3 says "beside Q58" while every round since r14 owns its
   own `## Round N criteria` section (`corpus/QUALITY.md:45`–`:137`) and no later round has ever
   appended into an earlier block; the deliverable drafts the new-section placement and records the
   fallback without choosing for the L1. Location: `corpus/QUALITY.md:137-142`,
   `tools/souji-landing-gate.py:905-990`.

9. **Header shape conflict, resolved in favour of the block the task named.** The task lists
   "criterion / applies-to / test / lesson"; the Round 25 block it names for the shape uses
   `| id | criterion | applies to | check | motivating evidence |` (`corpus/QUALITY.md:139`), while
   rounds 14–20 use the literal `applies-to | test | lesson` header (`:23`). The draft uses the Round 25
   header and states the mapping explicitly.

## Attack log

Not an attack seat, and no predicate, target, case set or axis is proposed for change. One
ATTACK-shaped observation is logged as finding 7: the implementation's neutral surface classes let a
claim bypass R2 by naming a class the frozen contract does not define, and the 12-case fixture encodes
that bypass as a passing case. Reported for the judge; I do not propose relaxing or reinterpreting C3.

## Boundaries

No lane write beyond `w1/axis-check-docs.md` and this report; no `git add/commit/push/stash/checkout/
reset`, no `jj` mutation, no `rm`/`mv` of another seat's file. `git log/show/diff/ls-tree/cat-file/
rev-parse` were read-only. `.scratch/`, `.ufo/state/`, `watchdog.log`, `MANIFEST.json`, fleet
`scripts/`/`templates/`, sibling lanes, `/proc`, `census/operator-sweep-*` and
`/home/vgpnk/Projects/shokuknow` were never read or written.
