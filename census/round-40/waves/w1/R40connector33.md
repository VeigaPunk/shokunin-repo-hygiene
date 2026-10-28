# R40connector33 — C3 coverage attack: the base arm of the C3 control clause, and the fixture-set mutation surface

Seat: connector (leaf; no subagent dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Frozen contract read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt`
(C3 paragraph, line 10).
Base revision named by the preregistration: `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
Scratch: `/fast/scratch/hyaku/souji-r40/R40connector33` (removed at exit).
Tool installs / upgrades: **none**; `pacman` untouched. No git/jj/index mutation, no commit, no push.
No lane file written except this report. The frozen claim was not altered.

## Axes

- **Coverage** (this seat's declared judged axis, primary): whether the frozen C3 predicate — in
  particular its control clause *"all mutants survive the r39 base fixture"* — can be *satisfied
  honestly*, and whether the branch surface C3 names is genuinely uncovered by the lane's existing
  fixtures.
- **Operability** (secondary): whether the r39 counter's base arm, as inherited, can carry the r40
  battery.
- Calibration (C1) is **not** assessed here.

## Named distinct edge case (item 33)

**The C3 control clause is evaluated against a single named fixture, but the lane's real mutation
surface is the fixture *set*. Under the single-file base arm every `--skip-unrecorded` mutant reads
"survives the base fixture"; under the fixture set, two of the three natural shapes are **already
killed by two committed pre-r39 fixtures** (`r36-worktree-drift.py`, `r37-drift-discrimination.py`).
The two readings of the same clause therefore disagree — and the reading that makes the clause
satisfiable is the one that overstates the coverage delta.**

This is distinct from every sibling in the wave. Sibling `R40connector45` FINDING 4 observes that
the *obvious* `--skip-unrecorded` mutant (`M17`, flag inversion) is killed by r36/r37; my distinct
edge case is **the base-arm asymmetry that makes that observation a coverage-accounting trap rather
than a footnote** — i.e. the same two fixtures kill the mutant under a widened base arm while the
r39 counter's single-file base arm reports `base_killed=0`, and the *widening the r39 review itself
recommended* flips the frozen C3 control clause from satisfied to violated for those shapes. My
finding also names a second, independent landmine in the same branch (root-repo discovery), which no
sibling names:

| sibling | edge taken | why item 33 differs |
|---|---|---|
| `R40connector21` | the kill-gate misattribution (counter's `crash` veto reads the *fixture's* stdout) | item 33 is **not** about the crash veto or the kill gate; it is about the **base arm** of the control clause and the **fixture-set** mutation surface |
| `R40connector45` | FINDING 4: the obvious `--skip-unrecorded` mutant is already killed by r36/r37; FINDING 5: base-leg reading ambiguity A vs B | item 33 reaches the **same mutants** but by a **different, additional measurement**: the base-arm *asymmetry* (single-file vs set) and the **r39-review-recommendation collision** — the widening that `W1RevC3Battery` F1 recommended makes the frozen clause FAIL for 2 of 3 shapes. I also supply the root-repo discovery landmine, which `R40connector45` does not name |
| `R40revenger60` | invalid-byte fixture I/O (`text=True` capture dies on a lone `0xff`) | item 33 is **not** about fixture I/O at all; my invalid-UTF-8 evidence is a corroborating side-measurement |
| `R40revenger12` / `R40revenger36` | duplicate-TOTAL ordering (first-invalid/last-valid) | item 33 is **not** about TOTAL ordering; my TOTAL evidence is corroborating side-measurement |
| `R40revenger48` | decoder replacement of invalid UTF-8 in an otherwise valid record | item 33 is **not** about decode semantics per se |

## Verdict

**C3 r40 coverage: NOT MEASURED at the candidate (no r40 fixture or counter exists in the lane at
inspection time), but two concrete, executed falsifiers are established against the committed r39
artifacts, plus a bounded measurement plan that resolves them. The coverage *substance* is sound;
the C3 *control clause* as written is not falsifiable without an explicit choice.**

**F1 (falsifier — high severity, instrument level). The frozen C3 control clause "all mutants
survive the r39 base fixture" is evaluated by the r39 counter against exactly ONE file**
(`--base-fixture` default `tests/fixtures/r38-drift-record.py`), and that file happens to contain
**no `--skip-unrecorded` case at all**. Measured: under the single-file base arm all three natural
`--skip-unrecorded` mutant shapes read `base_killed=0` (clause satisfied). Under the **fixture set**
— the surface the lane actually has — **two of the three shapes are already killed** by two
committed pre-r39 fixtures. So the clause as instrumented is satisfied *vacuously* for the
branch, and the coverage delta C3 claims for `--skip-unrecorded` is **overstated by two shapes** if
the r40 battery picks the natural mutant.

**F2 (falsifier — high severity, the r39 review's own recommendation collides with the frozen
clause). `census/round-39/waves/w1/W1RevC3Battery.md` F1 recommended fixing exactly this class of
defect: *"either add `r38-drift-write-envelope.py` to the base arm or replace M13 with a behaviour no
committed fixture asserts"* (lines 214-215) — i.e. **widen the base arm**, because the single-file arm
"cannot detect this" (line 209). **If the r40 counter adopts that recommendation, the frozen C3
control clause flips from satisfied to VIOLATED for 2 of 3 `--skip-unrecorded` mutant shapes**:
`base_killed` becomes non-zero because r36/r37 kill them. Measured below. The round's own
prior-round repair and the round-40 frozen claim are in direct conflict; the claim cannot be
honestly satisfied under the repair.

**F3 (falsifier — medium severity, a second landmine in the same branch, named by no sibling).
`--root` that is itself a git work tree makes the pristine tool report **the root repository itself
as an UNRECORDED drift row** (`DRIFT UNRECORDED <basename(root)>`), because `discover()` inserts
`basename(root)` when `root/.git` is a directory (`tools/souji-worktree-drift.py:227`) and
`repo_path()` maps that name back to `root` (`:205`). Measured: with `--root` = a container
directory the flag-absent run emits exactly one DRIFT row; with `--root` = a git repo the same
record emits **three** rows including `UNRECORDED landB`, and the flag-present run still emits one
(`ABSENT`), so `rc` stays **1** either way. An r40 `--skip-unrecorded` case that asserts
`rc == 0` when the flag is present therefore **passes only by accident of fixture layout** — if
the fixture's `--root` is a git repo, the flag-present expectation `rc=0` is unreachable. The r39
house style dodges this by using `--root root/fleet` (a container), so the hazard is invisible until
the r40 fixture changes layout.

## 1. Evidence pointers (committed r39 artifacts)

1. **Frozen C3 predicate** — `census/round-40/preregistration.txt:10`:
   > "r40 fixture adds behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and
   > invalid UTF-8 record bytes; each declared single-defect mutant is killed by the r40 fixture, the
   > pristine candidate passes, and all mutants survive the r39 base fixture."
   > "Kill if pristine fails, any mutant survives, any base mutant is killed, or fixture has no own
   > failure summary."

2. **The base arm is one file** — `census/round-39/c3-counter.py`:
   ```
   113:    ap.add_argument("--base-fixture", default="tests/fixtures/r38-drift-record.py")
   178:            base_killed, base_detail, _ = score(base_fixture, path, scratch)
   ```
   `score()` is the committed instrument's own function; it was **imported verbatim** for every
   verdict below (no re-implementation).

3. **The single-file base arm cannot see the fixture set** — `census/round-39/waves/w1/W1RevC3Battery.md`:
   ```
   19:  base arm is a *single named fixture*, not the fixture set.
   209: `base_killed=0` cannot detect this: `--base-fixture` defaults to **one** file
   214-215: classes plus 1 re-assertion, and either add `r38-drift-write-envelope.py` to the base
        arm or replace M13 with a behaviour no committed fixture asserts.
   ```

4. **The r39 base fixture has no `--skip-unrecorded` case** — `tests/fixtures/r38-drift-record.py`
   (10 cases, all `--root path --record record --timeout 30`, no flag) and
   `tests/fixtures/r39-drift-record-rules.py` (7 cases, same shape). Grep of all six tool-scoring
   fixtures: `--skip-unrecorded` occurs in **none** of them (verified: `skip-unrecorded=False` for
   all six).

5. **Two committed pre-r39 fixtures DO assert UNRECORDED rows** —
   `tests/fixtures/r36-worktree-drift.py:18-19` (`unrecorded   a live repository the record omits
   -> rc 1, UNRECORDED`), `tests/fixtures/r37-drift-discrimination.py:21-23` (`unrecorded-exact
   UNRECORDED gamma; live_repos=2 live_regs=2`, `unrecorded-unreachable`).

6. **The tool's root-repo discovery** — `tools/souji-worktree-drift.py:227`
   (`names.insert(0, os.path.basename(root.rstrip("/")) or "root")`) and `:205`
   (`if name == os.path.basename(root.rstrip("/")) and os.path.isdir(os.path.join(root, ".git")):`).

7. **The r39 tool bytes are the base bytes** — `git show 0242085...:tools/souji-worktree-drift.py`
   and the worktree file both hash `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`
   (byte-identical; the r39 tip changed only `corpus/lessons/round-39.md`).

## 2. Commands actually run, with outputs

All scratch under `/fast/scratch/hyaku/souji-r40/R40connector33`. The instrument's `score()` was
imported verbatim:

```python
spec = importlib.util.spec_from_file_location("r39_c3_counter",
    os.path.join(LANE, "census/round-39/c3-counter.py"))
r39 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r39)
```

### 2.1 F1 — the base-arm asymmetry (the decisive measurement)

```
$ python3 -B driver9.py     # base_kill matrix: every mutant x every committed fixture
  mutant \ fixture       r36-workt r37-drift r37-drift r38-drift r38-drift r39-drift
  pristine               alive     alive     alive     alive     alive     alive
  S1-skip-inverted       KILLED    KILLED    alive     alive     alive     alive
  S1-skip-never          KILLED    KILLED    alive     alive     alive     alive
  S1-skip-always         alive     alive     alive     alive     alive     alive
  S1-total-first-wins    alive     alive     alive     alive     alive     alive

  single-file base arm (what the r39 counter actually uses): tests/fixtures/r38-drift-record.py
      pristine               base_killed=no
      S1-skip-inverted       base_killed=no
      S1-skip-never          base_killed=no
      S1-skip-always         base_killed=no
      S1-total-first-wins    base_killed=no
```

Reading: **the single-file base arm reports `base_killed=no` for mutants that two committed
fixtures kill.** The C3 control clause is satisfied vacuously for `--skip-unrecorded`.

### 2.2 F2 — the r39 review's recommendation flips the frozen clause

```
$ python3 -B driver10.py
=== base arm: SINGLE file (r39 counter's actual behaviour) vs FIXTURE SET (r39 review's recommended fix) ===
  mutant               single-file base       fixture-set base (killers)
  skip-inverted        alive                  r36-worktree-drift.py, r37-drift-discrimination.py   base_killed=YES  <-- C3 control clause FAILS
  skip-never           alive                  r36-worktree-drift.py, r37-drift-discrimination.py   base_killed=YES  <-- C3 control clause FAILS
  skip-always          alive                  none   base_killed=no
  total-first-wins     alive                  none   base_killed=no
  pristine             alive                  none   base_killed=no

=== frozen C3 clause: 'all mutants survive the r39 base fixture' ===
  With the single-file base arm: every mutant survives -> clause SATISFIED.
  With the widened (fixture-set) base arm:
      skip-inverted        -> killed by r36-worktree-drift.py, r37-drift-discrimination.py
      skip-never           -> killed by r36-worktree-drift.py, r37-drift-discrimination.py
      => the clause FAILS for 2 of 3 skip-branch mutant shapes

=== which skip-branch shapes are ADMISSIBLE under each base arm ===
  skip-inverted    single-arm:alive    set-arm:killed    admissible-under-set-arm=NO
  skip-never       single-arm:alive    set-arm:killed    admissible-under-set-arm=NO
  skip-always      single-arm:alive    set-arm:alive     admissible-under-set-arm=yes

=== is the surviving shape actually killable by an r40 fixture? ===
  skip-inverted    r40-style probe            candidate-killed=yes   rc=1 fails=2 crash=False
  skip-inverted    r40-style probe (no echo)  candidate-killed=yes   rc=1 fails=2 crash=False
  skip-never       r40-style probe            candidate-killed=yes   rc=1 fails=1 crash=False
  skip-never       r40-style probe (no echo)  candidate-killed=yes   rc=1 fails=1 crash=False
  skip-always      r40-style probe            candidate-killed=yes   rc=1 fails=1 crash=False
  skip-always      r40-style probe (no echo)  candidate-killed=yes   rc=1 fails=1 crash=False
```

**This is the falsifier.** The admissible battery under the widened base arm is *narrowed to one
shape* (`skip-always`, i.e. the flag-ignored / always-discover shape), and that shape is confirmed
killable by an r40-style fixture and alive against all six committed fixtures. So the branch **is**
coverable — but only with a deliberately chosen mutant, and only after the round states which base
arm it is using. A battery built around the natural inversion (`if not args.skip_unrecorded:` →
`if args.skip_unrecorded:`) satisfies the clause *only* under the single-file arm.

### 2.3 F3 — the root-repo discovery landmine

```
$ python3 - <<'PY'   # A: --root = container dir (r39 house style); B: --root = a git repo
=== A: --root is a CONTAINER DIR (r39 house style: root/fleet) ===
   flag ABSENT   rc=1  DRIFT rows=['DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0']
   flag PRESENT  rc=0  DRIFT rows=[]

=== B: --root IS a git repo itself ===
   flag ABSENT   rc=1  DRIFT rows=['DRIFT\tABSENT\talpha\trecorded regs=1',
                                  'DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0',
                                  'DRIFT\tUNRECORDED\tlandB\tlive regs=1 prunable=0']
   flag PRESENT  rc=1  DRIFT rows=['DRIFT\tABSENT\talpha\trecorded regs=1']

=== C: the tool source that causes it ===
   tool:205 if name == os.path.basename(root.rstrip("/")) and os.path.isdir(os.path.join(root, ".git")):
   tool:227 names.insert(0, os.path.basename(root.rstrip("/")) or "root")
```

Consequence for the r40 fixture: in layout A the flag-present case yields `rc=0`; in layout B it
yields `rc=1`. An r40 `--skip-unrecorded` case written as "flag present ⇒ `rc=0`" is therefore
**layout-dependent**, and the r39 house style (`--root root/fleet`) is the only reason it holds
today. The fixture must either (a) keep `--root` a container directory and assert the *absence* of
any `UNRECORDED` row rather than the exit code, or (b) assert the exact `UNRECORDED` row set.

### 2.4 Corroborating side-measurements (not the distinct edge case, but load-bearing for the
r40 fixture author)

**(a) The pristine tool does NOT refuse invalid UTF-8 — it silently corrupts.** `parse_record`
decodes with `errors="replace"` (`tools/souji-worktree-drift.py:147`), so an invalid byte in a
REPO *name* becomes U+FFFD and the run proceeds:

```
$ python3 -B driver8.py   # pristine on a record with 0xff in the first REPO name
[E4] pristine on invalid UTF-8, exact bytes
  rc=1 stdout=b'DRIFT\tABSENT\talpha\xef\xbf\xbd\trecorded regs=1\nDRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0\nSUMMARY ...'
```

Byte-position decides the outcome entirely (same record, byte moved):

```
=== V1: invalid-byte POSITION decides the outcome ===
   byte-in-REPO-name    rc=1  'DRIFT\tABSENT\talpha<U+FFFD>\trecorded regs=1' + 'DRIFT\tUNRECORDED\talpha...'
   byte-in-TOTAL-repos  rc=2  ''                (schema refusal)
   byte-in-TOTAL-regs   rc=2  ''
   byte-in-comment      rc=0  'SUMMARY ... drift_rows=0 unreachable=0'
   byte-in-REPO-regs    rc=2  ''
```

So a fixture asserting "invalid UTF-8 ⇒ RECORD-MALFORMED" **fails on the pristine tool**
(`missing=['RECORD-MALFORMED']`, `rc=1` where the case wants `rc=2`) — the frozen C3 kill rule
*"pristine fails"* fires. The r40 case must assert the **observed** behaviour (corruption to
U+FFFD), or assert position-specific outcomes.

**(b) The pristine tool accepts duplicate TOTAL rows, and only the LAST one is validated.**

```
=== G3: duplicate TOTAL vs the tool's own documented contract ===
   tool:47 that does not match the schema, a duplicated name, or
   tool:48 a TOTAL row that disagrees
   tool:159 raise Refusal("RECORD-MALFORMED: line %d duplicates %s" % (lineno, name))   <- duplicate REPO NAME is refused
   two IDENTICAL TOTAL rows -> rc=0 'SUMMARY ...'
   -> no refusal: 'duplicated name' is refused, a duplicated TOTAL row is not
   DISAGREEING first TOTAL, agreeing last TOTAL -> rc=0 'SUMMARY ...'
   -> the disagreeing TOTAL row is never checked: only the LAST one is
```

The docstring lists `RECORD-MALFORMED` for "a duplicated name, or a TOTAL row that disagrees", but
the code refuses a duplicated REPO *name* and silently accepts a duplicated *TOTAL* row, and never
validates a non-final TOTAL row. The r40 case must assert the observed behaviour, and a fixture
author reading only the docstring will write a case the pristine tool fails.

**(c) Side-measurement, corroborating `R40connector21`/`R40revenger60` (not claimed as this seat's
distinct finding): the r39 `score()`'s `crash` veto reads the FIXTURE's stdout, and the house
fixture detail format re-prints the TOOL's stdout+stderr into it.**

```
$ python3 -B driver7.py   # committed counter, MUTANTS tuple extended with the invalid-UTF-8 mutants
CANDIDATE fixture = r39-convention (echoes tool stderr)
  MUTANT M20-utf8-strict killed=no base_killed=no rc=1 fails=1 crash=True base:rc=0 fails=0 crash=False
  MUTANT M21-utf8-noerrors killed=no base_killed=no rc=1 fails=1 crash=True base:rc=0 fails=0 crash=False
  MUTANT M24-utf8-surrogate killed=no base_killed=no NO-SUMMARY rc=1 base:rc=0 fails=0 crash=False
  MUTANT M25-utf8-ignore killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
  SUMMARY mutants=8 killed=1 survived=7 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728
  rc=1

CANDIDATE fixture = same cases, NO echo
  MUTANT M20-utf8-strict killed=yes ...
  MUTANT M21-utf8-noerrors killed=yes ...
  MUTANT M24-utf8-surrogate killed=no ... NO-SUMMARY rc=1 ...
  MUTANT M25-utf8-ignore killed=yes ...
  SUMMARY mutants=8 killed=3 survived=5 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728
  rc=1
```

Isolation of the mechanism, using two purpose-built fixtures that differ **only** in the echo
(`driver5.py`, committed `score()`):

```
=== committed r39 score() with mini-echo (r38/r39 convention) ===
   fixture rc=1 stdout='case-mini=FAIL rc=1 out=\'Traceback (most recent call last): ...
   -> committed score(): killed=no  rc=1 fails=1 crash=True  cases=1
=== committed r39 score() with mini-noecho ===
   fixture rc=1 stdout='case-mini=FAIL rc=1\nSUMMARY cases=1 pass=0 fail=1\n'
   -> committed score(): killed=yes  rc=1 fails=1 crash=False  cases=1
```

Both fixtures **detected** the difference (`fails=1`, `rc=1`); only the echo changed the verdict.
The `surrogateescape` shape is worse: the fixture itself dies, because `text=True` decoding of the
tool's own raw `0xff` byte raises inside the fixture:

```
[E3] the fixture itself dies on the surrogate mutant (text=True decode)
  fixture rc=1 stdout=''
  fixture stderr tail: ["UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 18: invalid start byte"]
```

and the `crash` verdict is **environment-dependent**, because Python's stdout error handler depends
on the locale:

```
[E1] locale mechanism
  LC_ALL=C (fixture ENV)   rc=1 raw0xff_in_stdout=True  stderr_UnicodeEncodeError=False
  no LC_ALL (inherited)    rc=1 raw0xff_in_stdout=True  stderr_UnicodeEncodeError=False
  python stdout under LC_ALL=C: utf-8 surrogateescape
  full inherited            stdout=utf-8 strict   tool rc=1 stderr_UnicodeEncodeError=True raw0xff_stdout=False
```

i.e. under the fixtures' `LC_ALL=C` env the tool *emits* the raw `0xff`; under a strict-stdout env
it *dies* with `UnicodeEncodeError`. Either way the `surrogateescape` shape is unscoreable as a
kill under the committed `score()`.

### 2.5 Commands used to read the frozen claim and the lane state

```
$ read /home/vgpnk/.omp/agent/RULES.md
$ read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show \
      0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py > pristine.py
$ sha256sum pristine.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  pristine.py
$ sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
$ git -C ... status --short
?? census/round-40/          # pre-existing, not mine
$ git -C ... rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e
```

No `git`/`jj` mutation, no commit, no push. `git status` shows the lane unchanged apart from the
pre-existing untracked `census/round-40/` directory.

## 3. Affected axes

- **Coverage (primary).** Improved by this report: the C3 control clause is shown to be
  *instrument-dependent* (F1/F2), and the honest admissible battery for `--skip-unrecorded` is
  narrowed to one shape. Harmed: none — no frozen clause is altered, and the branch is shown to be
  coverable.
- **Operability (secondary).** Improved: the base-arm choice must be stated, and the
  `--root`-is-a-git-repo layout hazard (F3) is a one-line fixture-design constraint that prevents a
  wrong `rc` expectation.
- **Calibration (C1).** Not assessed. Not harmed.

## 4. Proposed move (one move, no aim)

**Make the C3 control clause's base arm explicit and dual, and pin the `--skip-unrecorded` battery
to the flag-ignored shape.**

1. In the r40 C3 counter, keep the existing single-file base arm **and add** a second, clearly
   labelled arm — e.g. `base_set_killed` — that scores the battery against **all six** committed
   tool-scoring fixtures (`r36-worktree-drift.py`, `r37-drift-discrimination.py`,
   `r37-drift-escapes.py`, `r38-drift-record.py`, `r38-drift-write-envelope.py`,
   `r39-drift-record-rules.py`). Report both in the SUMMARY. The frozen clause
   *"all mutants survive the r39 base fixture"* is then satisfied under the reading the
   preregistration supports (the subject is the *new* mutants vs the r39 base fixture), while the
   marginality question — *"does the lane already kill this?"* — is answered explicitly instead of
   being invisible.
2. Declare the `--skip-unrecorded` mutant as the **flag-ignored** shape (`if not args.skip_unrecorded:`
   → `if True:`, i.e. always discover), **not** the natural inversion. Measured: the flag-ignored
   shape is alive against all six committed fixtures and is killed by an r40-style fixture
   (`candidate-killed=yes rc=1 fails=1 crash=False`), so it is the one shape that is *genuinely new
   coverage* and that survives under **both** base-arm readings. This removes the F1/F2 conflict
   without touching the frozen text.
3. In the r40 fixture, keep `--root` a **container directory** (r39 house style) and assert the
   *absence of any `UNRECORDED` row* plus the `drift_rows` count rather than the exit code alone, so
   the F3 root-repo landmine cannot flip the expectation.

This move is compatible with `R40connector21`'s kill-gate repair and `R40connector45`'s
Finding-4/Finding-5 conclusions: it agrees that the battery must use a flag-ignored shape, and it
resolves connector45's "two mutually exclusive readings" by making the base arm explicit in the
receipt instead of leaving it implicit in a default.

## 5. Risks

- **Risk A — the move may be read as changing the frozen claim.** It does not: the frozen clause is
  left byte-identical; the change is to the *counter's reported fields* and to the *battery's
  choice*, both of which are r40-side implementation, not the frozen predicate. L1 owns the wording.
- **Risk B — adding a second arm changes the counter's SUMMARY format**, and any r40 receipt
  consumer that parses `SUMMARY mutants=… killed=… survived=… pristine=… base_killed=… cases=…`
  must tolerate the extra field. Keep the existing field names and append.
- **Risk C — the flag-ignored shape is a weaker mutant than the inversion** (it breaks the flag's
  *effect* rather than its *polarity*). If the round's intent was to assert the flag's polarity
  semantics, the flag-ignored shape still detects it: with `--skip-unrecorded` present, the
  flag-ignored tool still emits the `UNRECORDED` row, which the flag-present case forbids.
  Measured (`driver10.py`): `skip-always` → `candidate-killed=yes rc=1 fails=1 crash=False`, with the
  failing case being `unrecorded-on`.
- **Risk D — the fixture-set arm is a strict superset of the single-file arm, so it can only ever
  report *more* base kills.** That is the point (it is the r39 review's own recommendation), but it
  means a battery that is admissible under the single-file arm may become inadmissible under the set
  arm. This is exactly the F2 conflict; step 2 of the move resolves it by choosing a shape that is
  admissible under both.
- **Risk E — the invalid-UTF-8 kill-gate defect (side-measurement 2.4c) is unresolved by this
  report** and is owned by `R40connector21`/`R40revenger60`. The r40 fixture author must still fix
  the echo or the crash-veto; this seat's contribution is only the corroborating measurement and the
  note that the `surrogateescape` shape is unscoreable either way.

## 6. Verification (what the main agent / L1 should run)

1. **Re-run this seat's decisive measurement** to confirm F1/F2 against committed bytes:
   ```sh
   cd /fast/scratch/hyaku/souji-r40/R40connector33   # recreate: see §7
   python3 -B driver9.py     # base_kill matrix over the fixture set
   python3 -B driver10.py    # single-file vs set base arm + admissibility
   ```
2. **Once the r40 fixture and counter exist**, run the r40 C3 counter with the **flag-ignored**
   mutant and require: `base_killed=0` (single-file arm) **and** `base_set_killed=0` (fixture-set
   arm) **and** the mutant killed by the candidate fixture. A `base_set_killed>0` is the F1/F2
   signal that the battery shape is inadmissible.
3. **Check the fixture layout**: run the r40 fixture's `--skip-unrecorded` case with `--root` set to
   a git repository as well as to a container directory, and require the *same* expectation in both.
   A different result is the F3 signal.
4. **Re-verify the tool bytes** before any of the above:
   `git -C <lane> show <rev>:tools/souji-worktree-drift.py | sha256sum` must equal
   `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` for the r40 base revision
   (it does for `0242085…`).
5. **Do not treat this report's unrun items as pass.** The r40 candidate fixture and counter did
   not exist in the lane at inspection time (`git status` shows only the pre-existing untracked
   `census/round-40/`), so *pristine passes*, *each mutant killed*, and *r39 baseline mutants
   survive* are **unmeasured** here.

## 7. Scratch inventory and cleanup

Scratch root: `/fast/scratch/hyaku/souji-r40/R40connector33` (removed at exit). Contents:

| file | purpose |
|---|---|
| `pristine.py` | `git show 0242085…:tools/souji-worktree-drift.py`, sha `e48ed08e6728…` |
| `probe-fixture.py` | r40-style fixture, 6 cases over the three C3 branches; `--echo-mode stderr` (r39 convention) |
| `probe-fixture-none.py` | same cases, tool output NOT echoed (isolates the crash-veto) |
| `driver.py`–`driver10.py` | the measurement drivers cited above |
| `S1-*.py`, `f1-D-*.py`, `M2*.py`, `crasher.py` | single-defect mutant variants |
| `r40-c3-counter-probe.py` | the committed r39 counter with only its `MUTANTS` tuple extended (diff shown in the receipt) |
| `mini-echo.py`, `mini-noecho.py` | two minimal fixtures differing only in the echo |
| `work/` | fixture scratch (fleets, records) |

**Cleanup: the scratch directory is removed before yield.** Nothing outside the lane's
`.ufo/waves/round-40/w1/` (this file) was written. `TMPDIR` was not set globally; every fixture
scratch was created under the seat's own scratch root or under an explicit `--work` directory
inside it.

## 8. Gates, surfaces, limits

- **Gates observed:** the frozen preregistration contract (read first, unaltered) and committed r39
  artifacts (`census/round-39/c3-counter.py`, `census/round-39/waves/w1/W1RevC3Battery.md`,
  `tests/fixtures/r38-drift-record.py`, `tests/fixtures/r39-drift-record-rules.py`,
  `tools/souji-worktree-drift.py`). No candidate r40 fixture or counter existed to run.
- **Surfaces touched:** this report only, at `.ufo/waves/round-40/w1/R40connector33.md`, plus the
  seat's own scratch.
- **Out of scope / not done:** no production file written, no frozen claim edited, no git/jj/index
  mutation, no commit, no push, no tool installed, `pacman` untouched, no fleet/sibling-lane/
  `.ufo/state`/watchdog/operator-config/template/fleet-script written, no PATH directory touched.
- **Known limits:** the r40 fixture and counter are absent, so C3's own acceptance conditions
  (pristine passes, each mutant killed, r39 baseline mutants survive, fixture has its own failure
  summary) are **unmeasured** here — reported honestly as unrun, not as pass. The F1/F2/F3 findings
  are properties of the *committed r39 instrument and fixtures* under the frozen clause's wording,
  and they are falsifiers of the clause's **measurability**, not of the coverage substance, which
  my measurements show to be sound and coverable.
