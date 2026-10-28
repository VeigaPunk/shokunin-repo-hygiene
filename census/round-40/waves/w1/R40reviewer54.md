# R40reviewer54 — reviewer seat, round 40, wave 1

**Seat:** R40reviewer54 (role: reviewer) · **Axis:** coverage · **Target:** the frozen C3 coverage
claim in `census/round-40/preregistration.txt`.

**Verdict in one line:** the C3 predicate, as frozen, is **not falsifiable as written for the
invalid-UTF-8 branch** and **is satisfiable by a fixture that proves nothing** for the
duplicate-TOTAL branch — I found one concrete falsifier (the invalid-UTF-8 revert that the
inherited A5 scoring contract cannot kill) and two measurement defects that let a C3 receipt
print `killed=N survived=0` while the r40 fixture asserts none of the three branches it claims.

Everything below is read-only analysis of committed r39/r40 bytes. No lane file was modified;
the only bytes this seat wrote are this report.

---

## 0. Named edge case (item 54's distinct target)

**The distinct edge case I attack is the *instrument*, not the tool: the `score()` scoring
contract inherited from `census/round-39/c3-counter.py`, applied to a mutant whose failure mode
is a *tool-side* exception rather than a clean refusal.**

Concretely, the edge case is: **an invalid-UTF-8 record branch whose "fix" raises a new refusal
class, and whose natural revert mutants fail by throwing inside the audited tool.** The r39
fixture's own reporting convention echoes the tool's stdout+stderr into the fixture's stdout
(`out=%r`), and the r39 `score()` treats *any* `Traceback (most recent call last)` in the
fixture's combined output as "the fixture crashed" — so a tool-side traceback is misread as a
broken fixture and the mutant is scored **survived** even though the fixture *did* detect the
behavioural difference (`fails=1`). The same convention also lets the fixture itself die with
`UnicodeDecodeError` (no `SUMMARY` at all) on a different mutant.

This is the branch nobody else on this wave is attacking: the other r40 C3 seats are reading the
`--skip-unrecorded` logic and the TOTAL-row logic. I deliberately took the *measurement
contract* and the *invalid-UTF-8* branch.

---

## 1. Evidence base — committed r39/r40 bytes actually used

All bytes were extracted with `git show` from the **frozen r40 base revision**
`0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip; matches the prereg's
declared base). Nothing was read from the worktree.

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py \
  > $S/tool-base.py
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tests/fixtures/r39-drift-record-rules.py \
  > $S/r39-fixture.py
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tests/fixtures/r38-drift-record.py \
  > $S/r38-fixture.py
```

SHA-256 of the extracted bytes (the two that the frozen receipt pins are marked):

```
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tool-base.py      <- r39 c3-after tool_sha=e48ed08e6728
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d  r39-fixture.py    <- r39 c3-after fixture_sha=567c37a679f5
ac0be0e7a49e683cd324ffa485fecb15d11c5636fde55f3244d9776020b021d6  r38-fixture.py    <- r39 c3-before fixture_sha=ac0be0e7a49e
```

**The committed r39 counter still reproduces its own frozen receipt at the r40 base revision**
(this is the control that the r40 base is not secretly broken):

```bash
python3 -B census/round-39/c3-counter.py --root . \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S
```
```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

This reproduces `census/round-39/records/c3-after.txt` byte-for-byte (same `tool_sha`,
`fixture_sha`, `cases=7`). The r40 base is a clean, honest baseline.

The r40 base tool's relevant branches (`tools/souji-worktree-drift.py` at the base rev):

| line | code | branch |
|---|---|---|
| 147 | `raw = b"".join(chunks).decode("utf-8", "replace")` | **invalid UTF-8 → U+FFFD substitution, never a refusal** |
| 152 | `for lineno, line in enumerate(raw.splitlines(), 1):` | record splitting |
| 153 | `if not line.strip() or line.startswith("#"):` | blank/comment skip |
| 162–165 | `m = TOTAL.match(line)` / `total = {...}` / `continue` | **TOTAL row: last one silently wins, no duplicate check** |
| 169–171 | `if total["repos"] != len(rows):` | TOTAL/REPO disagreement check |
| 370 | `if not args.skip_unrecorded:` | **the only `--skip-unrecorded` guard** |
| 438 | `ap.add_argument("--skip-unrecorded", action="store_true")` | the flag |

---

## 2. Branch behaviour measured on the r40 base bytes

Command: `python3 -B $S/expC_battery.py` (scratch driver; synthesises a git fleet under
`$TMPDIR`, writes record files, invokes the tool, prints `rc` + first 150 chars of output).

### (a) duplicate / multiple TOTAL rows

```
single TOTAL, matching                         rc=0  SUMMARY ... record_repos=2
TWO matching TOTAL rows                        rc=0  SUMMARY ... record_repos=2
DISAGREEING TOTAL first, agreeing second       rc=0  SUMMARY ... record_repos=2      <- !!
agreeing TOTAL first, DISAGREEING second       rc=2  REFUSAL RECORD-MALFORMED: TOTAL repos=99 but 2 REPO rows
single DISAGREEING TOTAL (r38 case)            rc=2  REFUSAL RECORD-MALFORMED: TOTAL repos=99 but 2 REPO rows
duplicate REPO name (r38 case)                 rc=2  REFUSAL RECORD-MALFORMED: line 2 duplicates alpha
```

**Finding A (medium, distinct from other r40 C3 seats): the duplicate-TOTAL branch has no
current behaviour for a fixture to assert.** The tool accepts two identical TOTAL rows, and —
worse — accepts a *disagreeing* TOTAL row followed by an agreeing one, because line 165
unconditionally overwrites `total` and only the **last** TOTAL row is ever checked against the
REPO sums (lines 169–178). The tool's own docstring promises
`RECORD-MALFORMED ... a TOTAL row that disagrees`, so the "disagreeing TOTAL first, agreeing
second" case is a **live contract violation in the r40 base bytes**: the docstring says a
disagreeing TOTAL row is refused, and the code silently discards it. A r40 fixture that asserts
the *documented* behaviour (refuse any disagreeing TOTAL) would fail pristine at the base bytes;
a fixture that asserts the *current* behaviour (accept, last-wins) would be asserting the
contract violation. **The frozen C3 predicate does not say which, and the two readings give
opposite verdicts.** This must be resolved before any r40 fixture can be written, because
"duplicate/multiple TOTAL rows" is currently **unspecified** — the branch has neither a
duplicate check nor a documented last-wins rule.

### (b) `--skip-unrecorded`

```
without flag (gamma unrecorded)                rc=1  DRIFT UNRECORDED gamma live regs=1 prunable=0 | SUMMARY ...
with --skip-unrecorded                         rc=0  SUMMARY ... drift_rows=0
no unrecorded repo, without flag               rc=0  SUMMARY ...
no unrecorded repo, with flag                  rc=0  SUMMARY ...
```

The flag works and is reachable. But **no fixture in the lane exercises it at all** — a grep of
`tests/fixtures/` and `tools/` for `skip-unrecorded|skip_unrecorded` returns only
`tools/souji-worktree-drift.py` (plus its `__pycache__`). So this is genuinely uncovered, and it
is the one branch of the three where the r40 fixture can add real, attributable coverage. Good.

### (c) invalid UTF-8 record bytes

```
invalid byte in NAME field                     rc=1  DRIFT ABSENT al<?>pha recorded regs=1 | DRIFT UNRECORDED alpha ...
invalid byte in numeric field                  rc=2  REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
invalid byte in comment line                   rc=0  SUMMARY ... (accepted, byte silently dropped by the replace)
invalid byte in TOTAL row                      rc=2  REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
invalid byte as a whole line                   rc=2  REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
truncated multi-byte UTF-8 seq                 rc=1  DRIFT ABSENT ale<?>pha ...
```

**Finding B (critical): the invalid-UTF-8 branch has three different current behaviours and
none of them is a UTF-8 refusal.** Line 147's `decode("utf-8", "replace")` means:

* a bad byte in the **name** field is silently replaced with U+FFFD, the row *parses*, the
  census then reports `ABSENT al\ufffdpha` **and** `UNRECORDED alpha` — a **split-brain** result
  where one byte makes one repo appear absent and another appear unrecorded, exit 1;
* a bad byte in a **numeric/comment** position either fails the schema or is dropped entirely;
* a truncated multi-byte sequence produces a *third* name.

Crucially, **a naive r40 fixture case asserting "invalid UTF-8 → rc 2" fails pristine against
the base bytes** (the tool answers rc 1 in the name-field case, which is the interesting one),
so the r40 fixture must either change the tool's behaviour or pin the current split-brain
behaviour. The frozen predicate does not say which. **This is the same under-specification as
Finding A, and it is what makes the C3 branch "invalid UTF-8 record bytes" untestable as
written.**

---

## 3. The concrete falsifier (item 54's primary deliverable)

### 3.1 The falsifier

> **A r40 fixture that adds the invalid-UTF-8 case, and an r40 counter that inherits the r39
> `score()` function, cannot kill the natural single-defect revert of the invalid-UTF-8
> refusal — even when the fixture *does* detect the behavioural difference.** The mutant is
> reported `survived`; a C3 receipt therefore reads `survived=1` and the frozen kill rule
> ("any mutant survives") fires — for a mutant that the fixture actually caught.

### 3.2 Mechanism, in the committed counter's own code

`census/round-39/c3-counter.py`, `score()` (line 87; the crash test at line 101, the kill
predicate at line 102):

```python
summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
...
crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)
killed = proc.returncode == 1 and fails > 0 and not crash
```

`crash` is computed over the **fixture's** stdout+stderr. But the r39 fixture convention
(`tests/fixtures/r39-drift-record-rules.py:76,79`, in `run_case`) puts the **audited tool's**
combined stdout+stderr into the fixture's own failure detail:

```python
out = proc.stdout + proc.stderr
...
results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
    proc.returncode, want_rc, missing, out.replace("\n", " ")[:160])))
```

and `main()` prints that detail to the fixture's **stdout** on failure. So **a traceback raised
inside the audited tool is echoed into the fixture's stdout and is then classified by `score()`
as "the fixture crashed"** — the contract's own anti-crash guard misfires in the wrong direction.

### 3.3 Measurement

Candidate = the tool the r40 round would plausibly need (refuse invalid UTF-8 with a named
class + docstring entry), plus a fixture asserting that class consistently. Pristine gate
passes:

```
PRISTINE (candidate tool + candidate fixture): rc=0 cases=7 pristine_ok=True  SUMMARY cases=7 pass=7 fail=0
```

Revert mutants scored with the **committed** r39 `score()` (imported from
`census/round-39/c3-counter.py`, not re-implemented):

```
revert mutant                        cand-kill  detail
MR1-decode-back-to-replace           KILL       rc=1 fails=1 crash=False
MR5-except -> pass (NameError)       SURVIVE    rc=1 fails=1 crash=True      <- FALSIFIER
MR6-except -> re-raise as MALFORMED  KILL       rc=1 fails=1 crash=False
```

`MR5` detail: `rc=1 fails=1 crash=True`. **The fixture detected it** (`fails=1`, exit 1) and the
counter still scored it **not killed**. The fixture's own output line:

```
case-invalid-utf8-name=FAIL rc=1 want=2 missing=['RECORD-NOT-UTF8'] out='Traceback (most recent call last):   File ".../MR5.py", line 455, in <modu...
SUMMARY cases=7 pass=6 fail=1
```

A second, independent way to lose the same kill: a mutant that makes the tool emit a lone
surrogate (`decode("utf-8","surrogateescape")`) makes the **fixture itself** die, because the
fixture reads the tool's stdout with `text=True` and strict UTF-8 decoding:

```
surrogateescape mutant: killed=False detail=NO-SUMMARY rc=1
fixture rc=1  stderr tail:
   File "/usr/lib/python3.14/subprocess.py", line 1099, in _translate_newlines
     data = data.decode(encoding, errors)
   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 15: invalid start byte
```

**Consequence for the frozen C3 predicate.** The predicate demands "each declared single-defect
mutant is killed by the r40 fixture". For the invalid-UTF-8 branch the *natural* mutant set is
{revert the refusal, remove the except clause, weaken the refusal class}. Two of those three
shapes are unkillable under the inherited contract. A team that picks MR1/MR6 gets a green
receipt; a team that picks the equally natural MR5 gets `survived=1` and a false MISSED. **The
verdict of the round's central coverage claim would depend on which of three equally plausible
mutants was typed** — that is the falsifier. It is a property of the *instrument*, provable
without any r40 artifact existing.

### 3.4 Why this is not a fixture-authoring mistake

It is not fixable by writing the case differently, because the problem is in `score()`'s crash
detector and in the fixture's `text=True` subprocess reads:

* `score()`'s `crash` test cannot distinguish "the fixture crashed" from "the tool crashed and
  the fixture faithfully reported it". The r38 A5 contract that `score()` encodes ("a kill needs
  the fixture's own `fail>0`, no traceback, exit 1") was designed to catch a *broken fixture*;
  it cannot see a *tool* traceback that the fixture echoes.
* The r40 fixture would have to run the tool with `errors="replace"` on its subprocess pipes and
  the counter would have to scope `crash` to the fixture's *own* frames. Neither is specified
  in the frozen predicate, and the predicate explicitly freezes the C3 kill rule as "pristine
  fails, any mutant survives, any base mutant is killed, or fixture has no own failure summary".

### 3.5 Corroborating measurement: an exit-code collision in the audited tool

`tools/souji-worktree-drift.py` documents `0` = no drift, `1` = drift rows, `2` = refusal
(`main()`, lines 41 and 434–451). A tool-side `UnicodeDecodeError` is uncaught, so:

```
tool rc=1  (documented: 0=no drift, 1=drift rows, 2=refusal)
stdout=''
stderr tail: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 7: invalid start byte
  -> a CRASH and 'drift rows found' are indistinguishable by exit code
```

So a fixture that only asserts `rc != 0` for the invalid-UTF-8 case cannot distinguish "the tool
refused" from "the tool crashed". Any r40 fixture for this branch must assert the **class token**
and the exact `rc`, and the C3 kill rule says nothing about that requirement.

---

## 4. Two further measurement defects that let a C3 receipt be green while proving nothing

### 4.1 The aggregate kill signal is not attributable to a case (HIGH)

`score()` returns `killed` from the **aggregate** `fails > 0`. It never says *which* case failed.
Consequence, measured with the same candidate fixture, with and without its invalid-UTF-8 case:

```
fixture WITH the invalid-utf8 case:
   dup-total-refused    killed=True   rc=1 fails=1 crash=False
   skip-flag-ignored    killed=True   rc=1 fails=1 crash=False
   always-skip          killed=True   rc=1 fails=1 crash=False
fixture WITHOUT it:
   dup-total-refused    killed=False  rc=0 fails=0 crash=False
   skip-flag-ignored    killed=False  rc=0 fails=0 crash=False
   always-skip          killed=False  rc=0 fails=0 crash=False
```

**Removing one case that has nothing to do with the TOTAL row or the `--skip-unrecorded` flag
flips all three mutants from `killed=True` to `killed=False`.** The kills were never
attributable to those mutants' behaviour; they were all produced by the same single failing
case. (Because in the "WITH" configuration that case fails at pristine too — the base tool does
not refuse invalid UTF-8 — the pristine gate is what stops the run; but the *per-mutant* kill
labels in the receipt are meaningless.) A receipt of the shape
`SUMMARY mutants=4 killed=4 survived=0` therefore does **not** establish that the r40 fixture
detects the duplicate-TOTAL branch, the `--skip-unrecorded` branch, or the invalid-UTF-8 branch.
The frozen C3 predicate has no per-case attribution requirement, so this defect is invisible to
it.

**Recommendation:** the r40 C3 counter must score **per case** — a mutant counts as killed only
if the *specific case* whose expectation the mutant violates fails, and that case passes on
pristine. The r39 fixture already prints `case-<name>=PASS|FAIL` per case, so the counter can
parse it with no fixture change.

### 4.2 "the r39 base fixture" is ambiguous, and the readings disagree (MEDIUM-HIGH)

The frozen C3 predicate says "all mutants survive **the r39 base fixture**". Two readings exist:

* **(a)** the fixture r39 used *as its base* — `tests/fixtures/r38-drift-record.py` (r39
  counter's `--base-fixture` default);
* **(b)** the fixture r39 *produced* — `tests/fixtures/r39-drift-record-rules.py` (r39 counter's
  `--fixture` default).

These are different files with different coverage, and for a TOTAL-row mutant they give
**opposite verdicts**:

```
total-check-removed    (a) r38-drift-record.py       = KILL     (rc=1 fails=1 crash=False)
                       (b) r39-drift-record-rules.py = survive  (rc=0 fails=0 crash=False)
                       => the readings DISAGREE
dup-total-refused      (a) r38-drift-record.py       = survive
                       (b) r39-drift-record-rules.py = survive
                       => the readings agree
```

A mutant that removes the `TOTAL repos != len(rows)` check (line 169–171) is **base-killed**
under reading (a) and **base-survives** under reading (b). The C3 kill rule ("any base mutant is
killed") therefore fires or does not fire **depending on which file the counter author picked**.
The frozen predicate does not name the file, so the claim's own control is not reproducible from
the frozen text.

**Recommendation:** the r40 preregistration (or its counter's `--base-fixture` default, echoed
into the receipt) must name the exact path, and the receipt must print it.

### 4.3 The "already killed elsewhere" problem — the control is one file, the suite is eight

The C3 control says "r39 fixture/counter has no cases for these branches and kills none of the
new mutants". That is true of the r39 fixture **as one file**, but the lane's drift-fixture
**suite** is eight files. Scanning all eight against the branch mutants:

```
existing-fixture kills of the three r40-branch mutants
  fixture                        dup-total-refused  first-total-wins  skip-flag-ignored  always-skip  decode-strict
  r36-worktree-drift.py          survive            survive            survive             KILL(fail=2)  survive
  r37-drift-discrimination.py    survive            survive            survive             KILL(fail=2)  survive
  r37-drift-escapes.py           survive            survive            survive             survive        survive
  r37-drift-mutants.py           survive            survive            survive             survive        survive
  r38-drift-mutants.py           survive            survive            survive             survive        survive
  r38-drift-record.py            survive            survive            survive             survive        survive
  r38-drift-write-envelope.py    survive            survive            survive             survive        survive
  r39-drift-record-rules.py      survive            survive            survive             survive        survive

mutants ALREADY killed by an existing fixture (so not new coverage):
  always-skip            <- r36-worktree-drift.py, r37-drift-discrimination.py
```

So the `--skip-unrecorded` **always-skip** mutant is already killed by two existing fixtures
(`r36-worktree-drift.py` asserts an `UNRECORDED` row; `r37-drift-discrimination.py` likewise).
A r40 fixture asserting that branch adds no coverage for that mutant shape — the coverage is
already there. The genuinely uncovered shape is the *flag-ignored* mutant (`if True:`), which
**no** existing fixture kills (because no existing fixture ever passes `--skip-unrecorded`).
The C3 control, read against one file, cannot distinguish these two.

---

## 5. Cross-claim coupling the r40 round must not break (verified)

The invalid-UTF-8 branch cannot be fixed by adding a refusal class alone: the r38
`docstring-enum` case requires every `raise Refusal("CLASS:` token to be named in the module
docstring, and forbids phantom docstring classes.

```
PRISTINE                             rc=0  SUMMARY cases=12 pass=12 fail=0
      case-docstring-enum=PASS
candidate NO docstring update        rc=1  SUMMARY cases=12 pass=11 fail=1
      case-docstring-enum=FAIL missing=['RECORD-NOT-UTF8'] phantom=[] tokens=[... 'RECORD-NOT-UTF8', ...]
candidate WITH docstring update      rc=0  SUMMARY cases=12 pass=12 fail=0
      case-docstring-enum=PASS
```

And with a *consistent* candidate (refusal + docstring entry), all four r39 consumer fixtures
stay green, so the fix is admissible:

```
r36-worktree-drift.py            rc=0  SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
r38-drift-write-envelope.py      rc=0  SUMMARY cases=12 pass=12 fail=0
r38-drift-record.py              rc=0  SUMMARY cases=10 pass=10 fail=0
r39-drift-record-rules.py        rc=0  SUMMARY cases=7 pass=7 fail=0
```

Note `r38-drift-write-envelope.py` is one of the five `CONSUMERS` in
`census/round-39/c2-counter.py:54-59` (r39 C2 leg L6). **Any r40 change to the drift tool's
refusal classes is therefore simultaneously a C2 leg**, and the two r40 claims must be read
together, not independently.

Also relevant: `SKILL.md` line 254 carries the registry row for `souji-worktree-drift` listing
the tool's refusal classes (`RECORD-MISSING / RECORD-MALFORMED / RECORD-EMPTY /
RECORD-OUTSIDE-ROOT / JSON-*`). A new `RECORD-NOT-UTF8` class must be added there too, or the
lane's own registry row goes stale — the C1 axis's subject matter, reached from the C3 branch.

---

## 6. Bounded measurement plan for the r40 C3 round

Ordered so each step unblocks the next. Steps 1–2 are cheap and can be done in parallel.

**Step 0 (must precede any fixture authoring) — resolve the two under-specified branches.**
The frozen text does not say what "duplicate/multiple TOTAL rows" and "invalid UTF-8 record
bytes" *should* do. The r40 team must pick, in the same round, and record:

* **duplicate/multiple TOTAL**: refuse a second TOTAL row outright, or refuse any TOTAL row
  that disagrees with the REPO sums *regardless of position* (the second is what the tool's
  docstring already promises — and the current code violates it, §2(a)). I recommend the
  second, since it closes the live contract violation rather than encoding it.
* **invalid UTF-8**: refuse the whole record with a named class (my recommendation: a new
  `RECORD-NOT-UTF8`, with the docstring entry per §5), rather than pinning today's split-brain
  `ABSENT`+`UNRECORDED` behaviour. Refusing the record is the only option that does not make a
  single corrupt byte split one census row into two contradictory drift rows.

**Step 1 — fix the scoring contract before writing mutants.** In the r40 C3 counter:
(a) scope `crash` detection to the **fixture's own** frames (e.g. require the traceback's
filename to be the fixture, or run the fixture with a marker so its own traceback is
distinguishable from the tool's); (b) have the fixture read the tool's pipes with
`errors="replace"` (or in binary) so a tool that emits a lone surrogate cannot kill the
fixture; (c) require the fixture to print a per-case table (it already does) and score
**per case**, not by aggregate `fails > 0`.

**Step 2 — decide the base fixture explicitly** and print its path + sha in the receipt
(§4.2). Name one file, e.g. `tests/fixtures/r39-drift-record-rules.py`, and state in the
predicate that this is the reading.

**Step 3 — declare mutants that are *branch-attributable*,** and prove attribution by the
§4.1 technique: score each mutant with the **full** candidate fixture and with the candidate
fixture **minus the case the mutant is supposed to violate**. A mutant is only credited if it is
killed in the first and survives in the second. Concretely, for each of the three branches:
* duplicate-TOTAL: kill shape = "duplicate TOTAL no longer refused"; base must survive it —
  note under reading (a) it does, under reading (b) it does; but the *total-check-removed*
  shape disagrees between readings (§4.2) and must be either excluded or the reading pinned.
* `--skip-unrecorded`: use the **flag-ignored** shape (`if True:`), not the always-skip shape —
  the latter is already killed by `r36-worktree-drift.py` and `r37-drift-discrimination.py`
  (§4.3), so it is not new coverage.
* invalid UTF-8: use a revert that produces a **clean refusal difference**, not one that
  raises inside the tool; verify with §3.3's `crash` detail that `crash=False`.

**Step 4 — assert the class token and the exact rc** in every new case, never just `rc != 0`,
because of the exit-code collision (§3.5).

**Step 5 — add the docstring + `SKILL.md` registry entries** together with the refusal class
(§5), and re-run `r38-drift-write-envelope.py` (C2 L6 consumer) before claiming C3.

**Step 6 — the falsifier to run against the finished r40 counter.** Take the r40 counter's own
mutant set, and confirm that every mutant's receipt line is reproducible by a *per-case* diff
against the same fixture with that case removed. Any mutant whose kill survives that removal is
a false kill and must be reported.

---

## 7. Verdict

**The frozen C3 coverage claim is not yet falsifiable, and as written it can be satisfied
vacuously.** Specifically:

1. **Concrete falsifier (confirmed):** the natural revert of the invalid-UTF-8 refusal fails by
   throwing inside the audited tool; the r39 `score()` contract — inherited verbatim by any r40
   counter — reads the fixture's echoed tool traceback as a fixture crash and scores the mutant
   **survived** even though the fixture detected it (`rc=1 fails=1 crash=True`). A second
   mutant shape makes the fixture itself die (`UnicodeDecodeError`, `NO-SUMMARY`). The round's
   central coverage verdict therefore depends on which of three equally plausible mutants was
   typed. **The r40 counter must fix the scoring contract (§6 Step 1) before any C3 receipt is
   trustworthy.**

2. **Vacuity hole (confirmed):** the aggregate `fails > 0` kill signal is not attributable to a
   case. Removing one unrelated case from the candidate fixture flips three mutants from
   `killed=True` to `killed=False`. A green `killed=N survived=0` receipt does not establish
   that the r40 fixture covers any of the three named branches. **Per-case attribution is
   required.**

3. **Underspecified branches (confirmed on the base bytes):** "duplicate/multiple TOTAL rows"
   and "invalid UTF-8 record bytes" have no determinate expected behaviour in the r40 base
   tool — a disagreeing-then-agreeing TOTAL pair is **accepted** (last-wins, contradicting the
   tool's own docstring), and an invalid byte in the name field is **accepted** with a
   split-brain `ABSENT` + `UNRECORDED` pair. A fixture asserting the documented behaviour fails
   pristine; a fixture asserting the current behaviour encodes the contract violation. The
   frozen predicate must state which.

4. **Control ambiguity (confirmed):** "the r39 base fixture" names two different files, and for
   a TOTAL-row mutant the two readings give opposite `base_killed` verdicts.

**Recommended disposition:** do not accept a C3 receipt on the current predicate. The r40 C3
counter must (i) fix `score()`'s crash attribution and the fixture's pipe decoding, (ii) score
per case with a per-case attribution proof, (iii) pin the base fixture path in the predicate and
the receipt, (iv) have the round decide and record the expected behaviour for the duplicate-TOTAL
and invalid-UTF-8 branches before the fixture is written, and (v) add the `RECORD-NOT-UTF8`
docstring entry and the `SKILL.md` registry entry alongside the refusal class, since the drift
tool is shared with r39 C2 leg L6.

**Scope note:** this is a recommendation on the frozen claim, not an admission or a shipping
decision. I did not alter `census/round-40/preregistration.txt`, did not write any production
file, and did not mutate git/jj/the index.

---

## Appendix — commands actually run, and the scratch they used

All scratch under `/fast/scratch/hyaku/souji-r40/R40reviewer54` with `TMPDIR` set explicitly
to that directory; removed after the run (see §"Cleanup" below). No `/tmp` use. No installs were
needed (stock `python3` 3.14.8, `git` 2.56.0) — **no tool was installed or updated by this
seat**.

```bash
S=/fast/scratch/hyaku/souji-r40/R40reviewer54
cd /home/vgpnk/Projects/shokunin/souji-shokunin

# evidence base
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py        > $S/tool-base.py
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tests/fixtures/r39-drift-record-rules.py > $S/r39-fixture.py
git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tests/fixtures/r38-drift-record.py     > $S/r38-fixture.py
sha256sum $S/*.py

# frozen control reproduces at the r40 base
TMPDIR=$S python3 -B census/round-39/c3-counter.py --root . \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S

# branch behaviour + mutant battery (imports the COMMITTED r39 score())
TMPDIR=$S python3 -B $S/expC_battery.py       # §2 branch tables + M20..M28 battery
TMPDIR=$S python3 -B $S/expD_mechanism.py     # §3.3 fixture stdout per mutant; r36 consumer interaction
TMPDIR=$S python3 -B $S/expE_docstring.py     # §5 docstring-enum coupling
TMPDIR=$S python3 -B $S/expF_base_fixture.py  # §4.2 base-fixture reading ambiguity
TMPDIR=$S python3 -B $S/expG_candidate_fixed.py  # §3.3 revert mutants on a consistent candidate
TMPDIR=$S python3 -B $S/expH_exitcode.py      # §3.5 exit-code collision
TMPDIR=$S python3 -B $S/expI_endtoend.py      # end-to-end counter-shaped reproduction
TMPDIR=$S python3 -B $S/expJ_crossfixture.py  # §4.3 eight-fixture scan
TMPDIR=$S python3 -B $S/expK_clean_pair.py    # §3.3 clean candidate+fixture pair
TMPDIR=$S python3 -B $S/expL_anomaly.py       # MR2 SyntaxError; MR5 traceback mechanism
TMPDIR=$S python3 -B $S/expM_attribution.py   # §4.1 attribution test
TMPDIR=$S python3 -B $S/expN_percase.py       # §2 per-case attribution; §4.2 disagreement
TMPDIR=$S python3 -B $S/expO_consolidated.py  # all four headlines in one run
```

Every mutant battery was scored with `score()` **imported from the committed
`census/round-39/c3-counter.py`** (via `importlib.util.spec_from_file_location`), not
re-implemented — so the measurements use the frozen instrument, not a paraphrase of it.

Git fixtures: the synthetic fleets were created with `git init` inside `mktemp -d` scratch
directories under `$TMPDIR`; every git command used `-C <exact fixture repo path>`. No commit was
made in the lane repository. The lane's own `git status --porcelain` after this seat's work
shows only the pre-existing untracked `census/round-40/` (the preregistration directory, created
before this wave) — no file written by this seat is tracked or modified.

## Cleanup

`/fast/scratch/hyaku/souji-r40/R40reviewer54` removed at the end of this seat's run; nothing
under `/tmp` was created. The only bytes this seat wrote inside the lane are this report at
`.ufo/waves/round-40/w1/R40reviewer54.md`.
