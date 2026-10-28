# W1RevSeparability — r39 w1 claim separability review

Seat: `W1RevSeparability` (reviewer, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane HEAD at review: `2201778e7736af82e7d8a42dec2494f115bf3923`; lane base `ed30b7f5b77939c9073348d810730bc4f355708d`;
prereg freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`.
Scratch: `/fast/scratch/hyaku/souji-r39/W1RevSeparability` (removed at end of seat — see §Scratch).
Read-only git only in the lane. No lane/fleet byte was created, edited or deleted by this seat except this report.

Question: **are C1, C2 and C3 separable** — does each claim's counter verify its own claim while the other
claims' work is absent, and does any claim's verdict depend on another claim's bytes or on r39 prose?

## 0. Claim-to-artifact map (what each counter actually reads)

| claim | counter | reads from `--rev` (committed) | reads from the worktree/cwd |
|---|---|---|---|
| C1 | `census/round-39/c1-counter.py` | every item file; `census/round-39/cells.tsv` at `--register-rev`; `tools/souji-citation-reconcile.py` (lines 150, 174) | `--items` TSV (line 196, cwd-relative) |
| C2 | `census/round-39/c2-counter.py` | `tools/souji-citation-reconcile.py`, `tools/souji-worktree-drift.py` (extracted, lines 181-184) | 5 consumer fixtures + `tests/fixtures/r39-citation-rev.py` (lines 170, 237, 253); `census/round-38/cells.tsv` via the citation child (line 111) |
| C3 | `census/round-39/c3-counter.py` | `tools/souji-worktree-drift.py` (line 122) | `--fixture` / `--base-fixture` (lines 123-124, cwd-relative) |

`grep -n "round-39\|SCORECARD\|lessons\|LOG\.md\|QUALITY"` over the three counters returns only their own
docstrings/CLI lines: **no counter reads `corpus/lessons/round-39.md`, `SCORECARD.md`, `LOG.md`,
`corpus/QUALITY.md`, `SKILL.md` or `census/round-38/preregistration.txt`** — the files C1's corrections touch.
`grep -ln "round-39\|SCORECARD\|lessons/round"` over the seven r36-r39 fixtures prints `NO-TEXT-DEP`.

## 1. C1's counter at the freeze (C2/C3 unimplemented) — what does it read?

At the freeze commit the counters exist but C2's and C3's tool/fixture work does not (tools are base bytes).

```
$ python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev b769bfb84a264d8b284c09bc211d99f39a3e9126 \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
...
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
RC=1
```

**Reads the before-state (`open=16`, `register_cells=0`), rc 1.** Same bytes, same command pointed at the
base revision reproduce `census/round-39/records/c1-before.txt` exactly (`items_sha=d892b74f8358`, last two
lines byte-identical), so the frozen control is reproducible.

C1's *register leg* is the only place C1 touches C2's work (the reconciler bytes at `--rev`). It does not
need C2's fix: base bytes print the same summary the counter's regex expects (`c1-counter.py:174`).

```
$ python3 -B $S/basetool/cit-base.py --root <lane> --rev 2201778e... --register census/round-38/cells.tsv \
    --register-rev 2201778e...        # base bytes ed30b7f, exact argv of register_leg
SUMMARY cells=10 mismatches=0          RC_BASE=0
$ python3 -B $S/basetool/cit-new.py  ... (same argv)
SUMMARY cells=10 mismatches=0          RC_NEW=0
```

Semantically corroborated by `git diff ed30b7f..2201778 -- tools/souji-citation-reconcile.py`: the diff adds
`REFUSAL REV-UNRESOLVED` for unresolvable `--rev`/`--register-rev` and an `ancestor_status` "error" class; the
row loop, the `SUMMARY cells=` format, the commit arm and the receipt arm are unchanged. **Verdict: C1's
verdict does not depend on C2's tool fix.**

## 2. C2's counter with C1's corrections absent — does it depend on r39 lesson/SCORECARD text?

C2 complete, C1 absent: `601195a` (C2's tool fix `bbd9b97` + the single-line docstring rule `601195a`; every
C1 correction lands later at `c0b007b`).

```
$ python3 -B census/round-39/c2-counter.py --root <lane> --rev 601195a0cebafa74fedb598e3f55da1708ae63f1 \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/4e07f1df2a61 fixture_sha=7ab7c3d85a81
RC=0
```

**`pass=6` with every C1 correction absent.** C2 does not read r39 lesson, SCORECARD, LOG, QUALITY, SKILL or
the r38 preregistration (static evidence above); its only worktree reads are the five `CONSUMERS` fixtures
(`c2-counter.py:54-60`, which excludes `tests/fixtures/r39-drift-record-rules.py`) and the r39 citation fixture
(`:170`, `:237`). **Verdict: C2 is separable from C1, and no C2 leg depends on r39 prose.**

C2's own dependency boundary is intra-claim, and it is visible: at `bbd9b97` (before `601195a`) the same
command reads `LEG L4 FAIL ... new_maps=False old_maps=False`, `SUMMARY legs=6 pass=5 fail=1 harm=0`, rc 1.
C2 needs its *own* single-line docstring commit, not C1.

C2 at HEAD (for reference, and the state the L1 will land):

```
$ python3 -B census/round-39/c2-counter.py --root <lane> --rev 2201778e... --base-rev ed30b7f...
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81   RC=0
```

## 3. C3's battery with C2's tool fix absent — does the docstring change affect a mutant?

C3's tool bytes at `--rev` with C2 entirely absent (`ed30b7f`, base drift bytes), and again at `601195a`:

```
$ python3 -B census/round-39/c3-counter.py --root <lane> --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
RC=0
```
```
$ ... --rev 601195a0cebafa74fedb598e3f55da1708ae63f1 ... (same base-rev)
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=4e07f1df2a61 fixture_sha=567c37a679f5
RC=0
```

**`killed=4 survived=0 base_killed=0` with C2's docstring repair absent.** Corroborated statically: neither the
candidate fixture nor the base fixture reads a docstring (`grep -n "docstring\|get_docstring"` over
`tests/fixtures/r38-drift-record.py` and `tests/fixtures/r39-drift-record-rules.py` returns only case labels and
expected stderr classes). **Verdict: the C2 docstring change affects no mutant; C3 is separable from C2.**

## 4. Couplings found (exact lines)

### K1 — C1's register arm is coupled to C2's and C3's after-receipts (C1 ⊃ C2, C1 ⊃ C3)

`census/round-39/make-cells.py:25-29` binds the register rows to the other claims' receipts:

```
25:  ("REG-01", "SCORECARD.md", "R39-REG-01", "legs=6",  "legs=2",  "census/round-39/records/c2-after.txt", "late"),
26:  ("REG-02", "SCORECARD.md", "R39-REG-02", "harm=0",  "harm=3",  "census/round-39/records/c2-after.txt", "late"),
27:  ("REG-03", "SCORECARD.md", "R39-REG-03", "fail=0",  "fail=4",  "census/round-39/records/c2-after.txt", "late"),
28:  ("REG-04", "LOG.md",       "R39-REG-04", "killed=4","killed=1","census/round-39/records/c3-after.txt", "late"),
29:  ("REG-05", "LOG.md",       "R39-REG-05", "cases=7", "cases=9", "census/round-39/records/c3-after.txt", "late"),
```

The reconciler verifies each row's receipt blob at `receipt_rev` (`tools/souji-citation-reconcile.py:312-320`:
`RECEIPT-ABSENT` / `RECEIPT-DISAGREES`). Both receipts are **untracked at HEAD**:

```
$ git ls-files census/round-39/records/      -> c1-before.txt c2-before.txt c3-before.txt   (only the three before-receipts)
$ git cat-file -e 2201778e...:census/round-39/records/c2-after.txt
fatal: path 'census/round-39/records/c2-after.txt' exists on disk, but not in '2201778e...'   rc=128
$ git cat-file -e 2201778e...:census/round-39/records/c3-after.txt
fatal: ... rc=128
```

Probe (fixture repo in scratch, tool = HEAD bytes, one register row naming an uncommitted receipt):

```
MISMATCH REG-99 RECEIPT-ABSENT census/late.txt at 550f90dc63ddbaa630d9fc634332285d9c4ab068
SUMMARY cells=1 mismatches=4      RC=1
```

So **C1 cannot pass unless C2's and C3's after-receipts are committed, at a revision that is an ancestor of
`--rev`, carrying `legs=6`, `harm=0`, `fail=0`, `killed=4`, `cases=7` on a `SUMMARY` line** — and, because
`make-cells.py` uses `"late"` for those rows and `--commit` for the C1 landing, `commit_distinct>=2`
(`c1-counter.py:258`) additionally requires the C2/C3 landing commit to be **strictly earlier** than the C1
landing commit. C1's register arm therefore certifies C2 and C3 pass; it is not independently verifiable.
This is by design in `make-cells.py`, not stated in the frozen C1 predicate, and it is the one real
claim-to-claim dependency in the round.

### K2 — C1's register file is unlanded (C1 currently reads `register_cells=0`)

```
$ python3 -B census/round-39/c1-counter.py --root <lane> --rev 2201778e... \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
(14 others CLOSED)
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
RC=1
```

`census/round-39/cells.tsv` does not exist at HEAD and `make-cells.py` is untracked (`git status --porcelain`:
`?? census/round-39/make-cells.py`, `?? .../c2-after.txt`, `?? .../c3-after.txt`, `?? .../census-{before,after}.txt`).
The C1 predicate's `register_cells>=6` floor (`c1-counter.py:257`) fails, and so does `commit_distinct>=2`.
Separately, items R39-C1-03/04 name files that exist at **no** revision:
`git log --all --oneline -- census/round-39/records/waves-wait.txt census/round-39/records/waves-capture.txt`
prints nothing. **Verdict: C1 is not closed at HEAD — its failure is entirely inside C1's own bytes, not a
cross-claim coupling.**

### K3 — C2/C3 instrument bytes come from the worktree, and this already produced an unreproducible receipt

`census/round-39/c2-counter.py:21-22` states: "Both tool revisions are extracted from committed bytes ... so the
counter never reads the worktree's uncommitted edits." That is true of the *tools* only; the *instruments* are
worktree reads — `c2-counter.py:170` (`fixture_sha`), `:237` (L5 fixture), `:253` (L6 consumer fixtures), and
`c3-counter.py:123-124` (`candidate_src`, `base_src`). `lane_root_of` (`c2-counter.py:63`) documents the
asymmetry; the module docstring contradicts it.

The consequence is measurable. `census/round-39/records/c3-before.txt` (committed at the freeze) records

```
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

but the committed fixture is a different blob with a different case count:

```
$ git show HEAD:tests/fixtures/r39-drift-record-rules.py | sha256sum   -> 567c37a679f5
$ git show b769bfb:tests/fixtures/r39-drift-record-rules.py | sha256sum -> 567c37a679f5   (identical)
$ git log --all --format=%H -- tests/fixtures/r39-drift-record-rules.py  -> 62784a6, 91280d2, b769bfb (all carry the 7-case blob, sha 567c37a679f5)
```

and re-running the same command at the same base tool gives the opposite reading:

```
$ python3 -B census/round-39/c3-counter.py --root <lane> --rev ed30b7f... --base-rev ed30b7f...
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5   RC=0
```

Same `tool_sha`, different fixture blob → `c3-before.txt` was measured against a 10-case fixture draft that was
**never committed**. `corpus/lessons/round-39.md:30` states that reading as the round's control ("Control at
base: `killed=0 survived=4`"), and it cannot be reproduced from committed bytes. This is the C1-axis defect
class (a self-assessment cell stating a value the repo state contradicts) surviving inside the r39 lesson and
its frozen receipt. The C3 *predicate* is unaffected (`killed=4 survived=0 pristine=ok base_killed=0 cases=7`,
rc 0), but its frozen before-control is not evidence of anything.

The same asymmetry, for C2, is documented and benign: `c2-before.txt`'s L5 row reads
`new=(8, 5, 3, 1) old=(8, 5, 3, 1)` with `fixture_sha=c142c1bc28b8`; the same command today reads
`new=(8, 4, 4, 1) old=(8, 4, 4, 1)`, `fixture_sha=7ab7c3d85a81`. Amendment A1 of the prereg names exactly this
(the `register-rev-gone` case was tightened to expect `REFUSAL REV-UNRESOLVED` before measurement); the
`SUMMARY pass=2 fail=4` headline reproduces byte-for-byte.

### K4 — C1 and C3 resolve their instrument paths against the cwd, not `--root`

`c1-counter.py:196` (`open(args.items, ...)`) and `c3-counter.py:123-124` (`open(args.fixture ...)`) take bare
relative paths. Run from the fleet root — the documented starting cwd for every seat — with the frozen
predicate's own relative arguments:

```
$ cd /home/vgpnk/Projects/shokunin && python3 -B <lane>/census/round-39/c1-counter.py --root <lane> \
    --rev 2201778e... --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
FileNotFoundError: [Errno 2] No such file or directory: 'census/round-39/c1-items.tsv'   RC=1
$ cd /home/vgpnk/Projects/shokunin && python3 -B <lane>/census/round-39/c3-counter.py --root <lane> --rev ... --base-rev ...
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/r39-drift-record-rules.py'   RC=1
```

`c1-counter.py:29-30` promises "Exit: ... 2 usage, malformed input, or an unresolvable revision"; a missing
`--items` is an uncaught `OSError` traceback with rc 1, not the promised exit 2. The `--register` path is
inconsistently revision-resolved (`git show` at `--register-rev`) while `--items` is cwd-resolved, so the two
halves of one predicate have different path bases.

## 5. Pair matrix — verdicts

| pair | command that verifies X with Y absent | reading | verdict |
|---|---|---|---|
| C1 / C2 (tool bytes) | `c1-counter --rev b769bfb --register census/round-39/cells.tsv`; base reconciler over the r38 register with `register_leg`'s argv | `open=16 register_cells=0`; `SUMMARY cells=10 mismatches=0` rc 0 | **separable** — C1 needs only the `SUMMARY cells=/mismatches=` format, present in the base bytes |
| C1 / C2 (register data) | `make-cells.py:25-27` + `git ls-files census/round-39/records/` | REG-01..03 cite `c2-after.txt`; untracked at HEAD; probe → `RECEIPT-ABSENT` | **coupled (K1)** — C1 cannot pass unless C2's after-receipt is committed |
| C1 / C3 (register data) | `make-cells.py:28-29` | REG-04/05 cite `c3-after.txt`; untracked at HEAD | **coupled (K1)** |
| C2 / C1 | `c2-counter --rev 601195a --base-rev ed30b7f` | `legs=6 pass=6 fail=0 harm=0` rc 0 | **separable** — no r39 lesson/SCORECARD/LOG/QUALITY read |
| C2 / C3 | `c2-counter` (CONSUMERS `c2-counter.py:54-60` excludes the r39 drift fixture) | `pass=6`, all five consumers green on both arms | **separable** |
| C3 / C1 | `c3-counter --rev ed30b7f --base-rev ed30b7f` | `killed=4 base_killed=0 pristine=ok cases=7` rc 0 | **separable** |
| C3 / C2 | `c3-counter --rev ed30b7f` and `--rev 601195a` | identical `killed=4 ... base_killed=0`; no fixture reads a docstring | **separable** — the C2 docstring repair affects no mutant |

## 6. Residual risk / verification gaps

1. **C3's `killed` field is revision-invariant.** `c3-counter` applies the mutants to the bytes at `--rev`, so
   `killed=4` is produced at the base revision as well (`--rev ed30b7f` → `killed=4 ... rc 0`). C3's
   discriminating evidence is `base_killed=0` (r38 fixture does not kill) plus the fixture's own assertions; the
   frozen before-receipt `killed=0 survived=4` cannot come from the committed fixture (K3).
2. **C2's control receipt is reproducible at the `SUMMARY` level only** (`pass=2 fail=4`), not at the L5 row or
   `fixture_sha`; Amendment A1 explains the divergence, so this is a stale-literal risk, not a claim failure.
3. **Instrument bytes are worktree bytes for C2/C3** (K3). A dirty worktree changes a claim's verdict without
   changing `--rev`; only `fixture_sha` makes that visible after the fact. `git status --porcelain` at review
   time showed `tests/fixtures/` clean, so the readings above are reproducible from HEAD.
4. Not run by this seat (outside the separability question, and the L1's call): the C1 register leg over an
   actual 6-row `cells.tsv` (it does not exist), and any run that would require writing lane bytes.
5. One fixture repo was created under my scratch to demonstrate K1 (`git init -q` in
   `/fast/scratch/hyaku/souji-r39/W1RevSeparability/fixrecv.N5wFou`, `git rev-parse --show-toplevel` asserted
   equal to that dir — `GUARD-OK` — two commits inside it only). No lane or fleet repository was mutated; the
   fixture was removed with the scratch tree.

## 7. Scratch

`/fast/scratch/hyaku/souji-r39/W1RevSeparability` — removed at the end of the seat (`rm -rf`), including the
`basetool/` extraction and the `fixrecv.*` fixture repo; nothing left on disk.

## Verdict

C1, C2 and C3 are separable in their **tool-byte** arms: C1 runs on the base reconciler with an identical
summary format, C2 passes with every C1 correction absent, and C3 kills all four mutants with C2's docstring
repair absent. They are **not** separable in C1's **register-data** arm: `make-cells.py:25-29` makes the C1
register certify C2's and C3's after-receipts (`legs=6 harm=0 fail=0 killed=4 cases=7`) and requires a strictly
earlier C2/C3 landing commit for the `commit_distinct>=2` floor — C1 cannot pass unless C2 and C3 pass and their
receipts are committed first. Two independent calibration defects are present in the round's own evidence:
`census/round-39/records/c3-before.txt` and `corpus/lessons/round-39.md:30` report a control (`killed=0
survived=4 cases=10 fixture_sha=ac0be0e7a49e`) that no committed fixture blob reproduces (the committed blob is
`567c37a679f5`, 7 cases, and reads `killed=4 survived=0` at the same `tool_sha`), and C1 is not closed at HEAD
(`open=2`, `register_cells=0`).
