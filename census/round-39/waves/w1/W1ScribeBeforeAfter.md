# W1ScribeBeforeAfter — round 39 wave 1 (hyaku run 11)

Seat: scribe. Role: draft the report's `## Before -> after measurements` section from the three
frozen control receipts, state the counting commands byte-exactly, and flag non-reproducible
arguments. Advisory: the L1 integrates and lands.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
Base: `ed30b7f5b77939c9073348d810730bc4f355708d` · Freeze: `b769bfb84a264d8b284c09bc211d99f39a3e9126`
Tip observed at session start: `2201778e7736af82e7d8a42dec2494f115bf3923`
Tip observed at session end: `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` (**HEAD moved mid-session**: the
L1 landed "round-39: C3/scratch — honour the caller's TMPDIR … (wave-1 W1ExecScratch)").

Scratch: `/fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter` — removed at the end of this session
(`rm -rf`); nothing left on disk. No tool installed or upgraded. No git/jj mutation run; every git
call below is read-only (`log`, `show`, `diff`, `status`, `rev-parse`, `cat-file`, `rev-list`).

---

## Verdict per check

| # | Check | Observed | Verdict |
|---|-------|----------|---------|
| V1 | `c1-before.txt` reproduces at base `ed30b7f` | byte-identical (`diff` empty), rc=1 | PASS |
| V2 | `c2-before.txt` reproduces at base with freeze fixture bytes | byte-identical, rc=1 | PASS |
| V3 | `c3-before.txt` reproduces at base with the **r38** fixture as candidate | byte-identical, rc=1 | PASS |
| V4 | C1 predicate at tip `d4c1755` | `open=2 register_cells=0`, rc=1 | **FAIL (not met)** |
| V5 | C2 predicate at tip `d4c1755` | `legs=6 pass=6 fail=0 harm=0`, rc=0 | PASS |
| V6 | C3 predicate at tip `d4c1755` | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`, rc=0 | PASS |
| V7 | `c3-after.txt` reproduces at tip | byte-identical, rc=0 | PASS |
| V8 | `c2-after.txt` reproduces at tip | all predicate fields identical; `fixture_sha` differs (stale field) | PASS-with-caveat |
| V9 | `c1-after.txt` exists | absent | **MISSING** |
| V10 | C1 register `cells.tsv` exists | absent (`REGISTER-ABSENT` → `cells=0`) | **MISSING** |
| V11 | `--scratch` naming an absent directory | `FileNotFoundError` traceback, rc=1 (not exit 2) | FLAG |
| V12 | `c3-counter.py` run from a cwd ≠ lane root | `FileNotFoundError: 'tests/fixtures/r39-drift-record-rules.py'`, rc=1 | FLAG |
| V13 | Naive do-nothing C3 control (default fixtures) | `killed=4`, rc=0 — contradicts `c3-before.txt` | FLAG (trap) |
| V14 | After receipts tracked in git | `??` for `c2-after.txt`, `c3-after.txt`, `census-after.txt`, `census-before.txt` | FLAG |

---

## Before -> after measurements

Fill rule: each after literal is the counter's **last line plus its exit code**, taken at
`<LANDING_REV>` = the 40-hex commit the L1 lands after every wave-1 seat. Take it after the last
landing; a reading taken before a landing is stale (see F4).

### C1 — calibration

Command (byte-exact, copy-pasteable, cwd-independent):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <LANDING_REV> --items /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv --register /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/cells.tsv
```

- Before (`census/round-39/records/c1-before.txt`, measured at `ed30b7f5b77939c9073348d810730bc4f355708d`):
  `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` (rc=1)
- After: `<AFTER_C1_LITERAL>` — shape must read
  `SUMMARY items=16 open=0 register_cells=<n>=6 register_mismatches=0 commit_distinct=<n>=2 items_sha=d892b74f8358`
  at commit `<LANDING_REV>` (rc=0).
- **Status at this writing: UNMEASURED and currently not met.** At tip `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` the
  counter reads `SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` (rc=1).
  The two OPEN items are `R39-C1-03` (`census/round-39/records/waves-wait.txt`, FILE-ABSENT) and
  `R39-C1-04` (`census/round-39/records/waves-capture.txt`, FILE-ABSENT). The register leg returns
  `REGISTER cells=0` because `census/round-39/cells.tsv` does not exist (the leg returns
  `REGISTER-ABSENT`), and `census/round-39/cells-lines.md` and the `R39-REG-01..06` anchors are
  likewise absent from `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md` (grep found none).

### C2 — operability

Command (byte-exact, copy-pasteable, cwd-independent):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <LANDING_REV> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
```

- Before (`census/round-39/records/c2-before.txt`, measured at `ed30b7f5b77939c9073348d810730bc4f355708d`
  with both arms at the base revision and the pre-amendment fixture):
  `SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8` (rc=1)
- After (`<AFTER_C2_LITERAL>` at commit `<LANDING_REV>`): shape
  `SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=<fixture sha at LANDING_REV>` (rc=0).
- Measured at `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`:
  `SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484` (rc=0).
  This matches the committed `c2-after.txt` on every predicate field; only `fixture_sha` differs
  (`7ab7c3d85a81` in the receipt vs `e555d8281484` at the tip) because the fixture is read from the
  worktree, not from `--rev` (F3), and it was amended after the receipt was written.

### C3 — coverage

Command (byte-exact, copy-pasteable, cwd-independent — absolute fixture paths remove the cwd
dependency flagged as F1):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <LANDING_REV> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r39-drift-record-rules.py --base-fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py
```

- Before (`census/round-39/records/c3-before.txt`, measured at `ed30b7f5b77939c9073348d810730bc4f355708d`
  with the **r38** fixture as the candidate — see F5):
  `SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e` (rc=1)
- After (`<AFTER_C3_LITERAL>` at commit `<LANDING_REV>`): shape
  `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=<n>=6 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5` (rc=0).
- Measured at `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`:
  `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5` (rc=0)
  — byte-identical to the committed `c3-after.txt`.

---

## Reproducibility flags

**F1 — cwd dependence (c3, and c1 as the prereg writes it).** `c3-counter.py` opens
`--fixture`/`--base-fixture` against the **cwd**, not `--root`; `c1-counter.py` opens `--items`/
`--register` against the cwd. The prereg's C1 command spells those two flags as relative paths, so it
is reproducible only when cwd == the lane root. Observed: running c3 from the scratch dir with an
absolute `--root` aborts with
`FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/r39-drift-record-rules.py'`
(rc=1). Mitigation used above: absolute `--items`/`--register`/`--fixture`/`--base-fixture`, which
makes all three commands cwd-independent.

**F2 — `--scratch` must already exist.** All three counters call
`tempfile.mkdtemp(dir=args.scratch or $TMPDIR or "/var/tmp")`; a `--scratch` naming an absent
directory dies with a Python traceback and rc=1 instead of the counters' exit-2 refusal contract.
Observed on c3: `FileNotFoundError: [Errno 2] No such file or directory: '…/absent-dir/souji-r39-c3.ncu5hj62'`
(rc=1). A scratch argument therefore makes the command non-reproducible on any host where that path
does not exist. The commands above omit `--scratch` entirely (they fall back to `$TMPDIR` then
`/var/tmp`), which is the portable form; if a scratch root is required, `mkdir -p` it first.

**F3 — worktree bytes are not pinned by `--rev`.** `c2`'s L5/L6 read
`<root>/tests/fixtures/r39-citation-rev.py` and the five consumer fixtures from the working tree;
`c3` reads its fixtures from the paths given; `c1` reads `--items`. `--rev` governs only the audited
tool bytes (`git show`). The receipts' `items_sha`/`tool_sha`/`fixture_sha` are the only pin, and
`c2` offers no flag to source L5's fixture from a revision. Consequence: `c2-before.txt` cannot be
reproduced from the current worktree, because its fixture bytes (`c142c1bc28b8`) were amended after
the freeze (Amendment A1) and again at `d4c1755`. It **is** reproducible by pointing `--root` at a
scratch mirror of the freeze fixture bytes (recipe under V2 below); no lane mutation is needed.

**F4 — receipts carry no command and no measured revision.** `c1/c2/c3-{before,after}.txt` record
only counters' output lines; unlike `census-before.txt`/`census-after.txt` they do not embed the
command or the revision measured. The "measured commit" for the after literal is therefore not
recoverable from a receipt, and `c2-after.txt` was already stale on `fixture_sha` at the tip. The
after block must name `<LANDING_REV>` in the report text; the receipts should gain a `rev=` line.

**F5 — the C3 before-control needs `--fixture tests/fixtures/r38-drift-record.py`.** `c3-before.txt`'s
`cases=10 fixture_sha=ac0be0e7a49e` are the **r38 base fixture**, not the new candidate: the do-nothing
control is "the four mutants survive every *existing* fixture", so the r38 fixture was passed as the
candidate. `ac0be0e7a49e` is the blob of `tests/fixtures/r38-drift-record.py` at `b769bfb` (verified by
extraction and hashing), not a deleted candidate. A naive re-run of the control with the *default*
candidate reads `killed=4`, rc=0 and would be misread as a falsification of the C3 control (V13).

**F6 — untracked wave evidence.** `git status --porcelain` shows
`?? census/round-39/make-cells.py`, `?? census/round-39/records/c2-after.txt`,
`?? census/round-39/records/c3-after.txt`, `?? census/round-39/records/census-after.txt`,
`?? census/round-39/records/census-before.txt`. The after receipts and the register generator are not
in any commit, so no after literal is currently anchored in lane bytes (the r38 R4 defect class).

---

## Commands run, observed output, verdict

Scratch variable used below (defined once, per shell):
`S=/fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter`.

### V1 — C1 before arm at the base revision

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter > "$S/c1-base.out" 2>&1; diff "$S/c1-base.out" census/round-39/records/c1-before.txt
```

Observed: `diff` produced no output (`IDENTICAL`), rc=1. Last lines of the run:

```
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

Verdict: PASS — the frozen C1 control is byte-reproducible from committed bytes.

### V2 — C2 before arm at the base revision, freeze fixture bytes pinned

```
S=/fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter
R=$S/rootlike-before
mkdir -p "$R/tests/fixtures"
printf 'gitdir: /home/vgpnk/Projects/shokunin/souji-shokunin/.git\n' > "$R/.git"
git -C "$R" rev-parse --show-toplevel          # -> $R (asserted before use)
for p in tests/fixtures/r39-citation-rev.py tests/fixtures/r38-drift-record.py tests/fixtures/r36-worktree-drift.py tests/fixtures/r38-drift-write-envelope.py tests/fixtures/r37-citation-reconcile.py tests/fixtures/r38-citation-commit.py; do git show b769bfb84a264d8b284c09bc211d99f39a3e9126:$p > "$R/$p"; done
python3 -B census/round-39/c2-counter.py --root "$R" --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S" > "$S/c2-before-recon.out" 2>&1; diff "$S/c2-before-recon.out" census/round-39/records/c2-before.txt
```

Observed: `toplevel: /fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter/rootlike-before`;
`c142c1bc28b8` for the mirrored citation fixture; `diff` empty (`IDENTICAL`), rc=1. Output:

```
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 5, 3, 1) old=(8, 5, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8
```

Verdict: PASS — reproducible, with the F3 recipe. Note `old=(8, 5, 3, 1)` (5 pass) here vs
`old=(8, 4, 4, 1)` (4 pass) in the after receipts: the difference is Amendment A1's tightened
`register-rev-gone` case, which the pre-amendment fixture did not yet expect.

### V3 — C3 before arm at the base revision, r38 fixture as candidate

```
python3 -B census/round-39/c3-counter.py --root "$PWD" --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --fixture "$S/fix-b769/base.py" --base-fixture "$S/fix-b769/base.py" --scratch "$S" > "$S/c3-before-recon.out" 2>&1; diff "$S/c3-before-recon.out" census/round-39/records/c3-before.txt
```

(`$S/fix-b769/base.py` is `git show b769bfb:tests/fixtures/r38-drift-record.py`, sha `ac0be0e7a49e`.)
Observed: `diff` empty (`IDENTICAL`), rc=1.

```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

Verdict: PASS — and this fixes the before command that `c3-before.txt` does not record (F5).

### V4 — C1 at the tip

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c1-counter.py --root "$PWD" --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch "$S"
```

Observed (tail), rc=1:

```
ITEM R39-C1-15 CLOSED
ITEM R39-C1-16 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

Also observed at `2201778e7736af82e7d8a42dec2494f115bf3923` (session start): `open=2` too, with
`ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt` and
`ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt`; the other 14 items CLOSED.

Verdict: FAIL (predicate not met at either tip) — after literal unavailable; `c1-after.txt` absent;
`cells.tsv` absent. Items 03/04 need `census/round-39/records/waves-wait.txt` (`waves=1,dead=0`) and
`census/round-39/records/waves-capture.txt` (`records=,failed=0,uncovered=0`).

### V5/V8 — C2 at the tips

```
python3 -B census/round-39/c2-counter.py --root "$PWD" --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"   # rc=0
python3 -B census/round-39/c2-counter.py --root "$PWD" --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"   # rc=0
```

Observed at `d4c1755` (rc=0):

```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
```

`diff` against `census/round-39/records/c2-after.txt` at `2201778` (run after the landing was already
in the worktree) showed exactly one differing line:

```
< SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
---
> SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
```

Verdict: PASS on the predicate (`legs=6 pass=6 fail=0 harm=0`, rc=0) at both tips; V8 caveat — the
receipt's `fixture_sha` is stale and the receipt names no revision (F3, F4).

### V6/V7 — C3 at the tips

```
python3 -B census/round-39/c3-counter.py --root "$PWD" --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S" > "$S/c3-head.out" 2>&1; diff "$S/c3-head.out" census/round-39/records/c3-after.txt
python3 -B census/round-39/c3-counter.py --root "$PWD" --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
```

Observed: `diff` empty (`IDENTICAL`) at `2201778`, rc=0; at `d4c1755`, rc=0:

```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
```

Verdict: PASS at both tips; `c3-after.txt` is byte-reproducible.

### V9/V10 — missing C1 artifacts

```
ls census/round-39/records/c1-after.txt census/round-39/cells.tsv
grep -rn "R39-REG-0" SCORECARD.md LOG.md corpus/QUALITY.md
```

Observed: both `ls` targets absent (`No such file or directory`); the `grep` found no `R39-REG-0`
anchor in any of the three files. `python3 -B census/round-39/make-cells.py --commit d4c1755… --late 2201778… --freeze b769bfb…`
(dry run, no `--write`) emits the six rows `REG-01..REG-06` with `commit=d4c1755…` and
`receipt_rev ∈ {2201778…, b769bfb…}` — i.e. six cells with `commit != receipt_rev` once written and
anchored.

Verdict: FAIL — the C1 after arm is blocked on `cells.tsv` + `cells-lines.md` + the six anchors +
`waves-wait.txt`/`waves-capture.txt`.

### V11 — absent `--scratch`

```
python3 -B census/round-39/c3-counter.py --root "$PWD" --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch /fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter/absent-dir
```

Observed, rc=1:

```
  File "/usr/lib/python3.14/tempfile.py", line 381, in mkdtemp
    _os.mkdir(file, 0o700)
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter/absent-dir/souji-r39-c3.ncu5hj62'
```

Verdict: FLAG (F2) — traceback, not exit 2.

### V12 — c3 from a foreign cwd

```
cd /fast/scratch/hyaku/souji-r39/W1ScribeBeforeAfter && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
```

Observed, rc=1:

```
  File "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c3-counter.py", line 124, in main
    candidate_src = open(args.fixture, encoding="utf-8").read()
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/r39-drift-record-rules.py'
```

Verdict: FLAG (F1).

### V13 — naive do-nothing C3 control (default fixtures)

```
python3 -B census/round-39/c3-counter.py --root "$PWD" --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
```

Observed, rc=0:

```
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
```

Verdict: FLAG (F5) — this is **not** a falsification of C3. With the new candidate as the control
fixture the mutants die on base tool bytes too, which is what C3 claims (the *fixture*, not the tool,
provides the coverage). The frozen control is the r38 fixture (V3).

### V14 — provenance and object-store checks

```
git log --oneline -3
git rev-parse HEAD
git status --porcelain
git cat-file -e ac0be0e7a49e
for c in $(git rev-list --all -- tests/fixtures/r39-drift-record-rules.py); do printf "%s %s\n" "$(git show $c:tests/fixtures/r39-drift-record-rules.py | sha256sum | cut -c1-12)" "$c"; done
git show b769bfb:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12
git show HEAD:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12
```

Observed: HEAD `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` on top of `2201778` and `790d16b`;
`git cat-file -e ac0be0e7a49e` → `fatal: Not a valid object name ac0be0e7a49e`, rc=128 (the sha is a
*content* sha, not a git object id — it is the `r38-drift-record.py` blob content at `b769bfb`, sha
`ac0be0e7a49e`); the candidate fixture path has sha `567c37a679f5` at all three commits that touch it
(`62784a6`, `91280d2`, `b769bfb`); citation fixture `c142c1bc28b8` at `b769bfb` → `e555d8281484` at
the tip.

Verdict: provenance established; untracked after-receipts flagged (F6).

---

## Out of scope / not claimed

- No after literal is asserted here. `<AFTER_C1_LITERAL>`, `<AFTER_C2_LITERAL>`,
  `<AFTER_C3_LITERAL>` and `<LANDING_REV>` are placeholders for the L1 to fill after the last
  landing; the measured readings above are advisory at `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`.
- `census/round-39/records/census-before.txt` / `census-after.txt` are the `SOURCES.md` census
  receipts, not one of the C1/C2/C3 controls; not scored here. Both are untracked.
- No product code, counter, fixture, prereg, receipt, SCORECARD/LOG/QUALITY, or `.ufo/state` byte was
  written or modified by this seat; the only file written is this report.
