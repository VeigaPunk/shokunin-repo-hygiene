# W1RevC3Battery — attack C3's mutation battery

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Reviewed revision: `2201778e7736af82e7d8a42dec2494f115bf3923` (HEAD at review time)
- Base revision: `ed30b7f5b77939c9073348d810730bc4f355708d`
- Scratch: `/fast/scratch/hyaku/souji-r39/W1RevC3Battery` (132 K, **still on disk**: `pristine.py`, `base.py`,
  `M11.py`-`M14.py`, `apply_mutants.py`, `before-repro.txt`, `after-repro.txt`; the `work/` subdir was removed)
- No commit, push, or mutating git/jj command was run. Only read-only git (`log`, `show`, `status`,
  `rev-parse`, `cat-file`, `ls-files`). No tool was installed.
- Task focus: anchor uniqueness, single-defect property, wrong-reason kills, and independent
  re-application of M11-M14 scored with both fixtures.

## Headline

**Frozen C3 predicate: PASS, reproduced exactly.** **C3's prose premise: FALSIFIED for M13.** M13 is
already killed by a committed pre-existing fixture (`tests/fixtures/r38-drift-write-envelope.py`,
case `record-outside-root`), so the claim "Four single-defect mutants of those behaviours survive
every existing fixture" holds for three mutants, not four. The counter cannot see this because its
base arm is a *single named fixture*, not the fixture set.

---

## 1. Provenance of the bytes under review

```
$ git rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923
$ git show 2201778...:tools/souji-worktree-drift.py > $S/pristine.py
$ sha256sum $S/pristine.py tools/souji-worktree-drift.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  /fast/scratch/.../pristine.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
$ git ls-files --error-unmatch census/round-39/c3-counter.py && git show HEAD:census/round-39/c3-counter.py | sha256sum && sha256sum census/round-39/c3-counter.py
ff18d64c09f48a2ee8fd9502ad8e6d549a92466fd7aad777b31ba7b513d3bcd1  -
ff18d64c09f48a2ee8fd9502ad8e6d549a92466fd7aad777b31ba7b513d3bcd1  census/round-39/c3-counter.py
$ git show HEAD:tests/fixtures/r39-drift-record-rules.py | sha256sum ; sha256sum tests/fixtures/r39-drift-record-rules.py
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d  -   (HEAD)
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d        (worktree)
$ git show HEAD:tests/fixtures/r38-drift-record.py | sha256sum ; sha256sum tests/fixtures/r38-drift-record.py
ac0be0e7a49e683cd324ffa485fecb15d11c5636fde55f3244d9776020b021d6  -   (HEAD)
ac0be0e7a49e683cd324ffa485fecb15d11c5636fde55f3244d9776020b021d6        (worktree)
```

Verdict: counter, candidate fixture, base fixture and tool all equal their HEAD bytes — the review
is of committed content. (The fixture identity matters for F3 below: the counter does *not* prove
this equality itself.)

## 2. Anchor uniqueness in the audited tool

Independent applier (`$S/apply_mutants.py`) transcribed the four anchors from
`census/round-39/c3-counter.py` and counted them against `pristine.py`:

```
$ python3 -B apply_mutants.py
pristine sha256=e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76 bytes=19688
M11 anchor_count=1    M11 lines_before=451 lines_after=452 delta=+1 sha256=fb5eb30dc549
M12 anchor_count=1    M12 lines_before=451 lines_after=451 delta=+0 sha256=23cf3eb327fc
M13 anchor_count=1    M13 lines_before=451 lines_after=451 delta=+0 sha256=12d2807b4c8b
M14 anchor_count=1    M14 lines_before=451 lines_after=451 delta=+0 sha256=878f6311515e
```

**VERDICT: PASS.** Each anchor occurs exactly once (`SKIP_ANCHOR` at line 153 is shared by M11 and
M14, but the counter builds each mutant independently from the pristine bytes, so the sharing cannot
serialize or contaminate; a non-unique anchor would make the counter print `ANCHOR-COUNT` and count
the mutant as surviving, which is the correct failure direction).

`diff -u pristine.py M11.py` shows one hunk, `+        line = line.rstrip()` inserted before the skip
check (the `delta=+1` insertion makes a naive zip-diff report 292 "changed" lines — a diff artifact
of the line shift, not a multi-line mutant). `diff -u pristine.py M13.py` shows exactly
`- raise Refusal("RECORD-OUTSIDE-ROOT: ...")` / `+ pass`.

## 3. Single-defect property and wrong-reason kills — independent scoring

Every mutant was scored by hand with both fixtures (`--tool` pointing at my own copies):

```
$ for T in pristine M11 M12 M13 M14; do
    python3 -B tests/fixtures/r39-drift-record-rules.py --tool $S/$T.py --work $S/work   # candidate
    python3 -B tests/fixtures/r38-drift-record.py         --tool $S/$T.py --work $S/work   # base
  done
```

Candidate fixture (`r39-drift-record-rules.py`), FAIL lines and summary:

```
pristine  SUMMARY cases=7 pass=7 fail=0
M11  case-trailing-space=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema']
     SUMMARY cases=7 pass=6 fail=1
M12  case-crlf=FAIL rc=2 out='REFUSAL RECORD-MALFORMED: line 1 does not match the census schema '
     SUMMARY cases=7 pass=6 fail=1
M13  case-outside-root=FAIL rc=1 want=2 missing=['RECORD-OUTSIDE-ROOT']
     out='DRIFT\tABSENT\t../escape\trecorded regs=1 DRIFT\tUNRECORDED\talpha\tlive regs=1 ...'
     SUMMARY cases=7 pass=6 fail=1
M14  case-indented-comment=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema']
     SUMMARY cases=7 pass=6 fail=1
```

Base fixture (`r38-drift-record.py`): `SUMMARY cases=10 pass=10 fail=0` for **all five** tools —
pristine and every mutant.

| mutant | documented behaviour | candidate FAIL case(s) | attributable to its own case? | base fixture |
|---|---|---|---|---|
| M11 | trailing-space REPO line accepted | `trailing-space` only | yes | 10/10 alive |
| M12 | CRLF records rejected | `crlf` only | yes | 10/10 alive |
| M13 | row outside-root refusal removed | `outside-root` only | yes (against the candidate fixture) — **but see F1** | 10/10 alive |
| M14 | indented `#` treated as comment | `indented-comment` only | yes | 10/10 alive |

**VERDICT: PASS** on single-defect shape and on wrong-reason immunity *within this fixture pair*:
each mutant fails exactly one case, the case that names the mutated behaviour; zero tracebacks
(`crash=False` in the counter's own detail string and no `Traceback` in my captures), and the
failures are semantic (`rc=0` where 2 is required, or a missing refusal token), not harness errors.
My initial hypothesis that M11 would collaterally break `indented-comment` was **disproved by
measurement**: `rstrip` is right-only, so `"  # indented comment"` keeps its leading spaces and is
still a schema violation — M11 fails only `trailing-space`.

## 4. The counter reproduces, and its control arm is real

```
$ python3 -B census/round-39/c3-counter.py --root <lane> --rev 2201778... --base-rev ed30b7f... --scratch $S
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
RC=0
$ diff -u census/round-39/records/c3-after.txt $S/after-repro.txt   -> AFTER-RECEIPT-IDENTICAL
```

Before control reproduced with the base tool and the r38 fixture as both arms:

```
$ python3 -B census/round-39/c3-counter.py --rev ed30b7f... --base-rev ed30b7f... \
    --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r38-drift-record.py
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
RC=1
$ diff -u census/round-39/records/c3-before.txt $S/before-repro.txt -> BEFORE-RECEIPT-IDENTICAL
```

**VERDICT: PASS.** The predicate `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` is
reproduced byte-for-byte, `rc=0`; the before arm yields `survived=4`, `rc=1`, so the kill logic is
non-vacuous. (`cases=7` satisfies the frozen `cases>=6` floor semantically; the SUMMARY prints the
number, not the literal `cases>=6` token.) Base-vs-HEAD tool delta is docstring-only, so
`parse_record` is byte-identical and the behaviour under test lives entirely in the new fixture:

```
$ diff <(grep -vE '^\s*#|^\s*$' $S/base.py) <(grep -vE '^\s*#|^\s*$' $S/pristine.py)
<   RECORD-MISSING         the record path cannot be read
<   RECORD-MALFORMED       a line does not match the schema, duplicates a name, ...
>   RECORD-MISSING         EACCES or ELOOP opening the record path: the path ...
```

## 5. "Survives every existing fixture" — tested against all eight drift fixtures

Six of the eight fixtures take `--tool` and were scored on pristine and every mutant:

```
$ for T in pristine M11 M12 M13 M14; do for F in r36-worktree-drift r37-drift-discrimination \
    r37-drift-escapes r38-drift-write-envelope; do ... done; done
pristine r36-worktree-drift       rc=0 SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
pristine r37-drift-discrimination rc=0 SUMMARY cases=6  pass=6  fail=0
pristine r37-drift-escapes        rc=1 SUMMARY cases=12 pass=12 fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
pristine r38-drift-write-envelope rc=0 SUMMARY cases=12 pass=12 fail=0
M11/M12/M14 x the four above     -> all pass=all, fail=0 (identical to pristine)
M13 r36-worktree-drift            rc=0 cases=12 pass=12 fail=0
M13 r37-drift-discrimination      rc=0 cases=6  pass=6  fail=0
M13 r37-drift-escapes             rc=1 cases=12 pass=12 fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
M13 r38-drift-write-envelope      rc=1 SUMMARY cases=12 pass=11 fail=1
```

`r37-drift-mutants.py` and `r38-drift-mutants.py` are mutation drivers (they mutate `--tool` and
score a `--fixture`), so by construction they cannot kill a tool mutant and were excluded.

### F1 (HIGH — claim defect, not predicate defect): M13 does not survive every existing fixture

```
$ python3 -B tests/fixtures/r38-drift-write-envelope.py --tool $S/M13.py --work $S/work
case-record-outside-root=FAIL rc=1 out=['DRIFT\tABSENT\t../escaped\trecorded regs=1', 'DRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0']
SUMMARY cases=12 pass=11 fail=1
$ python3 -B tests/fixtures/r38-drift-write-envelope.py --tool $S/pristine.py --work $S/work
SUMMARY cases=12 pass=12 fail=0
```

The case is the row-level guard M13 deletes (`tests/fixtures/r38-drift-write-envelope.py:259-265`):

```python
# record-outside-root
write(rec, "REPO\t../escaped\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
rc, out, elapsed, hung = invoke(tool, path, rec, [])
check("record-outside-root", (not hung) and rc == 2 and has_token(out, "RECORD-OUTSIDE-ROOT"), ...)
```

and it existed before this round:

```
$ git cat-file -e ed30b7f...:tests/fixtures/r38-drift-write-envelope.py && echo present
present
$ git show ed30b7f...:tests/fixtures/r38-drift-write-envelope.py | grep -n "record-outside-root"
28:  record-outside-root      a record row escaping `--root` is refused (regression)
260:        # record-outside-root
264:        check("record-outside-root", (not hung) and rc == 2 and has_token(out, "RECORD-OUTSIDE-ROOT"),
```

Consequences:
- `census/round-39/preregistration.txt` C3's "Four single-defect mutants of those behaviours survive every
  existing fixture" is **false for M13**; the honest coverage delta is **three** new classes
  (trailing-space, CRLF, indented comment), with `outside-root` re-asserted rather than newly covered.
- The new fixture's own docstring is narrower and defensible (it names only `r36-worktree-drift.py`,
  `r37-drift-discrimination.py`, `r38-drift-record.py` — all three indeed miss the class), but the
  frozen prose generalises to "every existing fixture", which no counter arm tests.
- `base_killed=0` cannot detect this: `--base-fixture` defaults to **one** file
  (`tests/fixtures/r38-drift-record.py`) and `base_n` sums only that fixture's score (counter lines
  112/173). The KILL RULE also says only "the base fixture", so the frozen predicate still passes —
  the defect is in the claim and in what the counter is able to falsify, not in the predicate arithmetic.

Recommended (L1's call, prereg is frozen): record an erratum that C3 closes **3** uncovered record
classes plus 1 re-assertion, and either add `r38-drift-write-envelope.py` to the base arm or replace
M13 with a behaviour no committed fixture asserts.

## 6. Counter defects found while attacking it

### F2 (MEDIUM): `--base-rev` is inert

```
$ grep -n "base_rev" census/round-39/c3-counter.py
115:    for flag, rev in (("--rev", args.rev), ("--base-rev", args.base_rev)):
```
That is the only use: `--base-rev` is validated with `cat-file -e <rev>^{commit}` and then never
consulted. The base arm is a *fixture*, not a revision. Measured consequence:

```
$ python3 -B c3-counter.py --rev ed30b7f... --base-rev ed30b7f... --scratch $S
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
RC=0
```
The frozen predicate prints the pass state on the **base** tool bytes as well (only `tool_sha` changes),
so the flag reads like a before/after control it does not perform. This is not a KILL-RULE violation
(C3's kill rule has no revision arm), but the pre-registered invocation
`--base-rev ed30b7f...` advertises a discrimination the counter does not make.

### F3 (MEDIUM): fixture provenance is unpinned

Counter line 122 reads the tool from the revision (`git_show`), lines 123-124 open both fixtures from
the **working tree**:
```python
candidate_src = open(args.fixture, encoding="utf-8").read()
base_src = open(args.base_fixture, encoding="utf-8").read()
```
No `git show <rev>:tests/fixtures/...`. An uncommitted or dirty fixture changes the score, while
`fixture_sha` in the SUMMARY is a worktree hash — so the receipt cannot be reproduced from
rev + counter bytes alone. (Today both hashes match `git show HEAD:...`, verified in §1; and
`census/round-39/records/c3-after.txt` is still **untracked** — `?? census/round-39/records/c3-after.txt`
— which is exactly the R4-class evidence question.)

### F4 (MEDIUM): the documented exit-2 "could-not-evaluate" path is unreachable for fixtures

```
$ python3 -B c3-counter.py --rev 2201778... --base-rev ed30b7f... --fixture /nonexistent/r39.py
  File ".../census/round-39/c3-counter.py", line 123, in main
    candidate_src = open(args.fixture, encoding="utf-8").read()
FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/r39.py'
RC=1
```
The docstring promises "Exit: ... 2 usage / could-not-evaluate input", and the refusal text
`REFUSAL COULD-NOT-EVALUATE: tool or fixture absent at %s` covers only `source is None` (tool absent
at rev). A missing/garbled fixture produces a traceback and `rc=1`, which reads as "mutants failed"
rather than "input unusable" — the same doc-vs-behaviour class C2 exists to police. A bad revision is
handled correctly:
```
$ python3 -B c3-counter.py --rev deadbeef ...
REFUSAL COULD-NOT-EVALUATE: --rev deadbeef does not resolve
RC=2
$ python3 -B c3-counter.py --rev 5a2b32941bc5c3da628ee92f75be1c33192ca311 (blob)
REFUSAL COULD-NOT-EVALUATE: --rev 5a2b32941bc5c3da628ee92f75be1c33192ca311 does not resolve
RC=2
```

### F5 (LOW): `cases>=6` is a weak proxy

Only 4 of the 7 cases discriminate the battery; `good`, `total-before-rows` and `comments-total-only`
are regression guards (the latter two do assert two additional documented ordering behaviours, so
they are not padding in fact — but the floor would be met by padding, and it does not require that
each of the four mutants has a *dedicated* failing case).

### F6 (LOW, residual risk): fixture `ENV` lacks git config isolation

`r39-drift-record-rules.py`'s `ENV` has `GIT_CONFIG_NOSYSTEM=1`/`GIT_CONFIG_GLOBAL=os.devnull` **not**
set (the counter's `GIT_ENV` does). On a host whose global config forces commit signing or a hooks
path, `make_repo`'s `git commit` would fail and every case would flip. On this host no
`commit.gpgsign` is configured (`git config --get commit.gpgsign` → rc=1, unset), so there is no
current effect; it is a portability hazard for the fixture, not a defect today.

## 7. Residual risk / verification gaps

- I did not score `r37-drift-mutants.py` or `r38-drift-mutants.py` as killers of M11-M14: they are
  mutation drivers with a required `--fixture`, so they cannot reject a tool mutant by construction.
- `r37-drift-escapes.py` exits `rc=1` on **pristine** as well (`escapes=0 control=ESCAPE-NOT-REPRODUCED`):
  because the base tool is behaviourally identical to HEAD, its base-discrimination control can never
  fire here. Its `pass=12 fail=0` on every mutant is therefore a genuine "not killed" reading, but its
  own rc is not evidence about mutants.
- F1 was measured against the six tool-scoring fixtures; the conclusion for M13 needs only the one
  (`r38-drift-write-envelope`).
- No check of the C1/C2 legs was performed — out of this seat's scope.

## Verdict summary

| check | verdict |
|---|---|
| four anchors unique in the audited tool (count exactly once) | PASS (1,1,1,1) |
| each mutant changes exactly one documented behaviour | PASS (single-hunk; one failing case each) |
| a mutant dies for a wrong/unrelated reason | NO (no collateral FAIL, no traceback, all failures semantic) |
| independent re-application scores identically with the counter | PASS (byte-identical `c3-after.txt`, rc=0) |
| base fixture keeps all four alive (`base_killed=0`) | PASS (10/10 on every mutant) |
| before control reproduces and is non-vacuous | PASS (identical, `survived=4`, rc=1) |
| "every existing drift fixture leaves these alive" | **FAIL for M13** (F1: `r38-drift-write-envelope` case `record-outside-root`) |
| counter input/error contract | DEFECTS (F2 inert `--base-rev`, F3 unpinned fixture provenance, F4 fixture-absence traceback instead of exit 2) |
