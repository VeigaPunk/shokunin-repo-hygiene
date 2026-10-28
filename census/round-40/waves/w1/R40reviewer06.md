# R40reviewer06 — attack the frozen r40 C3 coverage claim

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Reviewed revision: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e` (HEAD at review time)
- Base revision (frozen in the r40 preregistration): `0242085909fb6a4ee041c5443d76316ac6d59d4b`
- Axis: **coverage** (C3). Role: reviewer.
- Scratch: `/fast/scratch/hyaku/souji-r40/R40reviewer06` (1.4 M). **Removed before yield** (see §9).
- No commit, push, or mutating git/jj command was run. Only read-only git (`rev-parse`, `show`,
  `log`, `status`, `cat-file`, `ls-files`). No tool was installed; nothing was added to `pacman`,
  `uv`, `~/.local/bin`, `cargo` or `npm`.

## 0. Distinct edge case under attack (named explicitly)

Item 6 asks for a *different* edge case, source, control or failure mode. Mine is:

> **The "invalid UTF-8 record bytes" branch of the drift tool is a LOSSY-DECODE branch, not an
> error branch.** `tools/souji-worktree-drift.py:147` decodes the record with
> `b"".join(chunks).decode("utf-8", "replace")`, so an undecodable byte becomes U+FFFD and the run
> *continues*. A single-defect mutant that flips the decoder to `"strict"` therefore fails in a way
> no other branch fails in: the **tool** raises an unhandled `UnicodeDecodeError` and prints a
> Python traceback.

This matters because the committed kill contract (`census/round-39/c3-counter.py:101-102`) decides
"the fixture crashed" by scanning the **fixture's** stdout+stderr for the literal
`"Traceback (most recent call last)"`, and every committed drift fixture **echoes the tool's raw
stdout+stderr into its own failure detail**. So the tool's traceback reaches the fixture's stdout
and is misread as a fixture-side crash — the mutant is scored **SURVIVED** even though the fixture
detected it (`fails=3`).

Secondary distinct edge cases named and measured in this report:
- **F2** the pristine tool treats a duplicate `TOTAL` row as **LAST-WINS**, so a "duplicate TOTAL
  rows" fixture case built from two *identical* TOTAL rows has **zero** discriminating power.
- **F4** the `--skip-unrecorded` branch's observable surface is wider than the one `UNRECORDED`
  row: it also owns the `live_regs`/`live_prunable` accounting and the `unreachable` counter.
- **F6** the `unreachable` counter is observable on the unrecorded path only via an unrecorded
  repo whose `.git` is a **file** pointing at a missing gitdir.

## 1. Baseline: the committed r39 C3 counter reproduces exactly

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ S=/fast/scratch/hyaku/souji-r40/R40reviewer06 && mkdir -p $S/scratch
$ python3 -B census/round-39/c3-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2f6e981a105fc759205767d2a749a5f7d4fd0b8a \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch $S/scratch
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

Byte-identical to the committed receipt `census/round-39/records/c3-after.txt` (`tool_sha=e48ed08e6728
fixture_sha=567c37a679f5`, `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`).
The audited tool bytes are identical at the frozen r40 base revision and at HEAD:

```
$ for r in 0242085909fb6a4ee041c5443d76316ac6d59d4b be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e 2f6e981a105fc759205767d2a749a5f7d4fd0b8a; do
    echo -n "$r "; git show $r:tools/souji-worktree-drift.py | sha256sum; done
0242085909fb6a4ee041c5443d76316ac6d59d4b e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  -
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  -
2f6e981a105fc759205767d2a749a5f7d4fd0b8a e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  -
```

So the r40 C3 work is a **fixture + battery** change against an unchanged tool; `parse_record` is
the whole surface under test.

## 2. The three C3-named branches, measured on the pristine tool

Frozen predicate (verbatim, `census/round-40/preregistration.txt`):

> C3 — coverage (current evidence 8). Predicate: r40 fixture adds behavioral cases for
> duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8 record bytes; each
> declared single-defect mutant is killed by the r40 fixture, the pristine candidate passes, and
> all mutants survive the r39 base fixture. Control: r39 fixture/counter has no cases for these
> branches and kills none of the new mutants. Kill if pristine fails, any mutant survives, any
> base mutant is killed, or fixture has no own failure summary.

Pristine behaviour of each named branch, measured with `probe_pristine.py` (tool bytes from
`git show 0242085...:tools/souji-worktree-drift.py`; every git command used `-C` on the exact
fixture root, and `rev-parse --show-toplevel` was asserted equal to the fixture root before each
commit):

```
=== dup-total-identical            rc=0    SUMMARY ... record_repos=2 drift_rows=0
=== dup-total-first-bad-last-good  rc=0    SUMMARY ... record_repos=2 drift_rows=0     <-- bad TOTAL silently ignored
=== dup-total-good-then-bad        rc=2    REFUSAL RECORD-MALFORMED: TOTAL repos=3 but 2 REPO rows
=== dup-total-no-total             rc=0    SUMMARY ... record_repos=2 drift_rows=0
=== skip-unrecorded-off-unrecorded-repo rc=1  DRIFT UNRECORDED beta  live regs=1 prunable=0
=== skip-unrecorded-on-unrecorded-repo  rc=0  SUMMARY ... drift_rows=0
=== skip-unrecorded-off-no-unrecorded-repo rc=0 SUMMARY ... drift_rows=0
=== skip-unrecorded-on-no-unrecorded-repo  rc=0 SUMMARY ... drift_rows=0
=== bad-utf8-in-name               rc=1    DRIFT ABSENT al<U+FFFD>pha  recorded regs=1
=== bad-utf8-in-numeric-field      rc=2    REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
=== bad-utf8-in-comment            rc=0    SUMMARY ... record_repos=2
=== bad-utf8-whole-line            rc=2    REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
=== bad-utf8-in-total-line         rc=2    REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
```

Three facts the r40 fixture author must know, none of which the frozen predicate states:

1. **Duplicate TOTAL is LAST-WINS.** `tools/souji-worktree-drift.py:164` assigns
   `total = {...}` unconditionally, overwriting any earlier TOTAL. A bad TOTAL followed by a good
   TOTAL is **accepted** (rc=0). A good TOTAL followed by a bad TOTAL is **refused** (rc=2).
   Nothing in the tool documents this asymmetry.
2. **`--skip-unrecorded` only suppresses the discovery loop** (`tools/souji-worktree-drift.py:370`).
   When the record already lists every repo, `--skip-unrecorded` is a **no-op** (both arms rc=0,
   `drift_rows=0`): the flag is only observable when an *unrecorded* repo exists under `--root`.
3. **Invalid UTF-8 has three different pristine outcomes** depending on where the byte lands:
   name field → lossy U+FFFD, the row parses and the repo becomes `ABSENT` (rc=1); numeric field
   → the line stops matching the schema and is refused (rc=2); inside a `#` comment → ignored
   (rc=0). A fixture that tests only one of the three positions is testing one third of the branch.

## 3. Systematic mutation scan of the three branches

`mutation_scan.py` applies 16 single-defect edits to the audited bytes and scores each with the
**r39 counter's own `score()` function** (imported from `census/round-39/c3-counter.py`, not
reimplemented), against the committed r39 fixture (the r40 base fixture) and a scratch r40-shaped
fixture (9 cases: `good`, `dup-total-identical`, `dup-total-bad-then-good`, `dup-total-good-then-bad`,
`unrecorded-off`, `unrecorded-on`, `bad-utf8-name`, `bad-utf8-numeric`, `bad-utf8-comment`).

```
== rev=0242085909fb6a4ee041c5443d76316ac6d59d4b tool_sha=e48ed08e6728
MUTANT                       BRANCH                     r39(base)                      r40(candidate)
M41-TOTAL-first-wins         dup-TOTAL                  survived(rc=0 fails=0)         KILL(rc=1 fails=2 crash=False)
M42-TOTAL-dup-refused        dup-TOTAL                  survived(rc=0 fails=0)         KILL(rc=1 fails=3 crash=False)
M49-TOTAL-repos-sum          dup-TOTAL                  survived(rc=0 fails=0)         KILL(rc=1 fails=1 crash=False)
M43-SKIP-always-scan         skip-unrecorded            survived(rc=0 fails=0)         KILL(rc=1 fails=1 crash=False)
M44-SKIP-never-scan          skip-unrecorded            survived(rc=0 fails=0)         KILL(rc=1 fails=2 crash=False)
M45-SKIP-UNRECORDED-class    skip-unrecorded            survived(rc=0 fails=0)         KILL(rc=1 fails=1 crash=False)
M50-SKIP-unreachable-count   skip-unrecorded            survived(rc=0 fails=0)         SURVIVED(rc=0 fails=0 crash=False)
M51-SKIP-live-regs-leak      skip-unrecorded            survived(rc=0 fails=0)         SURVIVED(rc=0 fails=0 crash=False)
M46-DECODE-strict            bad-utf8                   survived(rc=0 fails=0)         SURVIVED(rc=1 fails=3 crash=True)
M47-DECODE-ignore            bad-utf8                   survived(rc=0 fails=0)         KILL(rc=1 fails=2 crash=False)
M48-DECODE-latin1            bad-utf8                   survived(rc=0 fails=0)         KILL(rc=1 fails=1 crash=False)
M52-DECODE-surrogateescape   bad-utf8                   survived(rc=0 fails=0)         SURVIVED(NO-SUMMARY rc=1)
M53-DECODE-utf8-sig          bad-utf8                   survived(rc=0 fails=0)         SURVIVED(rc=0 fails=0 crash=False)
M54-DUP-REPO-not-refused     dup-REPO (not named by C3) survived(rc=0 fails=0)         SURVIVED(rc=0 fails=0 crash=False)
M55-COMMENT-indented         comment (not named by C3)  KILL(rc=1 fails=1 crash=False) SURVIVED(rc=0 fails=0 crash=False)
M56-SCHEMA-trailing-space    schema (not named by C3)   KILL(rc=1 fails=1 crash=False) SURVIVED(rc=0 fails=0 crash=False)
r40 survivors: 8 -> ['M50-SKIP-unreachable-count', 'M51-SKIP-live-regs-leak', 'M46-DECODE-strict',
                     'M52-DECODE-surrogateescape', 'M53-DECODE-utf8-sig', 'M54-DUP-REPO-not-refused',
                     'M55-COMMENT-indented', 'M56-SCHEMA-trailing-space']
base(r39) killed: 2 -> ['M55-COMMENT-indented', 'M56-SCHEMA-trailing-space']
```

**The control arm of the frozen predicate is TRUE and I verified it independently.** All 13 mutants
of the three *named* branches survive the committed r39 fixture (`survived` for every one) — the r39
fixture and counter have no cases for these branches, exactly as the control states. The two mutants
the r39 fixture *does* kill (M55/M56, i.e. r39's own M14/M11) are outside the C3-named branches.

## 4. F1 (HIGH) — the committed kill contract masks a tool-side traceback as a fixture crash

**Mechanism.** `census/round-39/c3-counter.py:87-102`:

```python
def score(fixture, tool, work):
    ...
    crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)
    killed = proc.returncode == 1 and fails > 0 and not crash
```

`proc` is the **fixture** process. The intent (round-38 A5,
`corpus/lessons/round-38.md:204`: "A fixture that printed one `=FAIL` line, a SUMMARY and then
crashed scored `killed`; a kill now needs the fixture's own `fail=N` with `N > 0` and no traceback")
is to reject a fixture that crashes **itself**. But the check is textual over the fixture's *whole*
output, and every committed drift fixture **echoes the tool's raw stdout+stderr** in its failure
detail:

- `tests/fixtures/r39-drift-record-rules.py:76,79-83` → `out = proc.stdout + proc.stderr` … `"out=%r" % (… out.replace("\n", " ")[:160])`
- `tests/fixtures/r38-drift-record.py:90,92-94` → same shape

So when the **tool** raises, its traceback text is echoed into the **fixture's stdout**, the counter
scans the fixture's stdout, finds `Traceback (most recent call last)`, sets `crash=True`, and
withholds the kill.

**Measurement.** M46 = `decode("utf-8", "replace")` → `decode("utf-8", "strict")`:

```
$ python3 -B r40-shaped-fixture.py --tool work/M46-DECODE-strict.py --work work
case-bad-utf8-name=FAIL rc=1 want=1 missing=['DRIFT\tABSENT', 'al<U+FFFD>pha', 'drift_rows=3'] out='Traceback (most recent call last):   File ".../M46-DECODE-strict.py", line 451, in <module>     sys.exit(main(sys.a'
case-bad-utf8-numeric=FAIL rc=1 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] out='Traceback (most recent call last): ...'
case-bad-utf8-comment=FAIL rc=1 want=0 missing=['SUMMARY', 'record_repos=2'] out='Traceback (most recent call last): ...'
SUMMARY cases=9 pass=6 fail=3
fixture rc=1
-- fixture stderr bytes: 0
-- 'Traceback' in fixture stdout: 3
-- 'Traceback' in fixture stderr: 0
-- SUMMARY in stdout: 1
```

The fixture did **not** crash: `stderr` is 0 bytes, it printed its own `SUMMARY cases=9 pass=6
fail=3`, and it exited 1. The traceback it printed is the **tool's**, relayed. Yet:

```
== M46 (strict decode) : mutant whose failure mode is a TOOL-SIDE traceback
    r39-committed  killed=NO  rc=0 fails=0 crash=False
    r40-shaped     killed=NO  rc=1 fails=3 crash=True      <-- detected (fails=3) but scored survived
    r40-scrubbed   killed=yes rc=1 fails=3 crash=False
```

**Consequence for the frozen C3 predicate.** C3's kill rule includes "any mutant survives". Under
the committed scoring contract, the mutant that most directly expresses the C3-named branch
("invalid UTF-8 record bytes" → the tool must not silently accept, and must not die with a
traceback either) is **reported as surviving even though the fixture caught it**. The r40 counter
would print `survived=1` and the C3 claim would be scored as failed **for a scoring artifact, not a
coverage gap**. The symmetric risk is worse: an r40 executor who notices the counter says "survived"
and therefore *softens* the fixture (or drops M46 from the battery) is silently buying a green
C3 receipt by removing the one mutant that tests the branch's hardest case.

**Remedy, measured.** Two independent fixes, both verified:

1. **Scrub the relayed text in the fixture** (fixture-side, no counter change): replace the literal
   `Traceback (most recent call last):` in the echoed detail → `r40-scrubbed killed=yes rc=1 fails=3
   crash=False`.
2. **Score the fixture's crash on the fixture's stderr only** (counter-side, keeps the A5 intent):
   `crash = "Traceback (most recent call last)" in proc.stderr` → `r40-shaped killed=yes rc=1
   fails=3 fixture_crash=False`, while the A5 control (a fixture that prints its SUMMARY and *then*
   raises) is still correctly **not** a kill:

```
== F1 control: the A5 concern (a fixture that crashes AFTER its SUMMARY) is still caught by the stderr-only remedy
   crashy fixture -> killed=NO (rc=1 fails=1 fixture_crash=True)  [must be NO]
```

My first attempt at this control used `raise SystemExit('boom')`, which prints **no traceback** and
scored `killed=yes` — a false negative of my own remedy, corrected by re-running with
`raise ValueError('boom')`. The corrected measurement is the one quoted above. **Recommendation:
fix (2), in the r40 counter, not in the fixture** — a fixture-side scrub hides the tool's traceback
from the receipt, which is exactly the evidence an r40 reader needs.

## 5. F2 (HIGH) — a "duplicate TOTAL rows" case built from two IDENTICAL TOTAL rows is vacuous

**Mechanism.** The pristine tool is LAST-WINS (§2 fact 1). Two identical TOTAL rows are
observationally identical under last-wins and under first-wins, so such a case cannot discriminate
the two semantics. M41 = `total = {...}` → `total = total or {...}` (last-wins → first-wins):

```
== M41 (TOTAL first-wins instead of last-wins)
    r39-committed      killed=NO  rc=0 fails=0 crash=False
    r40-shaped     killed=yes rc=1 fails=2 crash=False      <-- fixture HAS a differing-TOTAL case
    r40-identical-only killed=NO rc=0 fails=0 crash=False    <-- fixture has ONLY the identical-TOTAL case
```

`r40-shaped-fixture-identical-total.py` is the r40-shaped fixture with the two *differing*-TOTAL
cases removed, leaving only `dup-total-identical` — the case a fixture author writes first when
the predicate says "duplicate/multiple TOTAL rows". Under it, **M41 survives**.

The frozen predicate says "duplicate/multiple TOTAL rows" and does not require the rows to differ,
so a literally-compliant r40 fixture can be built entirely from identical TOTAL rows and will
**not** discriminate the last-wins rule — while still satisfying every stated C3 condition
(pristine passes, the fixture has its own failure summary, the base fixture kills none of the new
mutants). The word "duplicate" invites the vacuous shape; "multiple" permits the discriminating
one. **Recommendation: the r40 fixture must include at least one case with two TOTAL rows whose
`repos`/`regs`/`prunable` fields differ** — I verified `dup-total-bad-then-good` (rc=0, bad TOTAL
ignored) and `dup-total-good-then-bad` (rc=2, refused) kill M41.

## 6. F3 (MEDIUM) — the r39 base fixture is not a valid base for a carried-forward battery

The C3 kill rule says "any base mutant is killed" must not fire, with the base fixture being the
r39 one. But the r39 fixture **kills r39's own M11-M14**:

```
== F3: the r39 fixture as an r40 BASE fixture
   r39 M11  r38base=survived r39base=KILL
   r39 M12  r38base=survived r39base=KILL
   r39 M13  r38base=survived r39base=KILL
   r39 M14  r38base=survived r39base=KILL
```

An r40 battery that carries r39's M11-M14 forward (the obvious "extend the battery" move) plus new
mutants therefore trips C3's own kill condition on the base arm, while a battery of **only new**
mutants does not. Simulated:

```
== simulated r40 battery carried forward from r39 (M11-M14 + M41,M42,M46,M43), base = the r39 fixture
   M11                  r40=SURVIV   r39base=KILL
   M12                  r40=SURVIV   r39base=KILL
   M13                  r40=SURVIV   r39base=KILL
   M14                  r40=SURVIV   r39base=KILL
   M41-TOTAL-first-wins r40=KILL     r39base=surv
   M42-TOTAL-dup-refused r40=KILL    r39base=surv
   M46-DECODE-strict    r40=SURVIV   r39base=surv
   M43-SKIP-always-scan r40=KILL     r39base=surv
   SUMMARY mutants=8 killed=3 survived=5 base_killed=4
   C3 kill condition 'any base mutant is killed' -> FIRED
   C3 kill condition 'any mutant survives'        -> FIRED
```

Two independent requirements fall out: (a) the r40 battery must contain **only new** mutants, or
the base arm fires; (b) the r40 **fixture** must be a superset of the r39 fixture's cases (not a
replacement) or the r39 mutants that the r39 fixture kills become survivors of the r40 fixture and
the candidate arm fires. A superset fixture (r39's 7 cases + 8 new = 15) satisfies both:

```
== superset r40 fixture (15 cases) vs a 12-mutant scan
   M41-TOTAL-first-wins       sup=KILL    r39base=surv
   M42-TOTAL-dup-refused      sup=KILL    r39base=surv
   M43-SKIP-always-scan       sup=KILL    r39base=surv
   M44-SKIP-never-scan        sup=KILL    r39base=surv
   M45-SKIP-UNRECORDED-class  sup=KILL    r39base=surv
   M46-DECODE-strict          sup=SURVIV  r39base=surv     <-- F1, not a coverage gap
   M47-DECODE-ignore          sup=KILL    r39base=surv
   M48-DECODE-latin1          sup=KILL    r39base=surv
   M53-DECODE-utf8-sig        sup=KILL    r39base=surv
   M54-DUP-REPO-not-refused   sup=SURVIV  r39base=surv     <-- already killed by the r38 fixture
   M55-COMMENT-indented       sup=KILL    r39base=KILL
   M56-SCHEMA-trailing-space  sup=KILL    r39base=KILL
   SUMMARY mutants=12 killed=10 survived=2 base_killed=2 survivors=['M46-DECODE-strict', 'M54-DUP-REPO-not-refused']
```

M54 (duplicate-REPO refusal removed) is **not** an r40 gap: the committed r38 fixture already kills
it (`M54 (dup-REPO not refused) vs r38 fixture: killed=yes (rc=1 fails=10 crash=False)`). The
superset's two survivors are F1 (a scoring artifact) and M54 (already covered elsewhere).

## 7. F4 / F6 (MEDIUM) — the `--skip-unrecorded` branch owns more than the UNRECORDED row

Two mutants of the named branch survive a fixture that only asserts the `UNRECORDED` row:

- **M51** = `live_regs += regs; live_prunable += prunable` injected into the unrecorded branch.
  Observable — pristine prints `live_regs=1`, M51 prints `live_regs=2`:

```
== pristine rc=1
    DRIFT UNRECORDED beta live regs=1 prunable=0
    SUMMARY ... record_repos=1 ... live_repos=1 live_regs=1 live_prunable=0 drift_rows=1 unreachable=0
== M51 rc=1
    DRIFT UNRECORDED beta live regs=1 prunable=0
    SUMMARY ... record_repos=1 ... live_repos=1 live_regs=2 live_prunable=0 drift_rows=1 unreachable=0
```

  This is a **real accounting defect class**, and the tool already documents the invariant it
  breaks (`tools/souji-worktree-drift.py`, the A6 comment: "live_regs/live_prunable describe the
  RECORD's repositories … an unrecorded repo's figures live on its UNRECORDED row only"). A fixture
  that asserts only the `UNRECORDED` DRIFT row never notices the `SUMMARY` counters moving.

- **M50** = `unreachable += 1` dropped from the unrecorded branch. **Not observable** with a
  healthy unrecorded repo (both arms print `unreachable=0`), because a *healthy* repo is never
  unreachable. It becomes observable only when the unrecorded repo is UNREACHABLE — which needs a
  `.git` **file** pointing at a missing gitdir (a `.git` *directory* is a valid repo):

```
== pristine rc=0   (unrecorded beta is a .git FILE -> list-rc=128 -> UNREACHABLE)
    DRIFT UNREACHABLE beta UNREACHABLE:list-rc=128
    SUMMARY ... drift_rows=1 unreachable=1
== M50 rc=0
    DRIFT UNREACHABLE beta UNREACHABLE:list-rc=128
    SUMMARY ... drift_rows=1 unreachable=0
```

  (Note `discover()` at `tools/souji-worktree-drift.py:~227` accepts a `.git` file as well as a
  directory, which is what makes this reachable.)

  **Recommendation:** the r40 `--skip-unrecorded` case should assert the `SUMMARY` counters
  (`live_regs`, `live_prunable`, `unreachable`), not only the `DRIFT` row, and should include one
  unrecorded repo whose `.git` is a file pointing at a missing gitdir.

## 8. F5 (MEDIUM) — the fixture harness itself can die on the branch it is testing

M52 = `decode("utf-8", "surrogateescape")` makes the **tool** emit the raw `0xff` byte on stdout.
The committed fixtures capture the tool with `text=True` (default UTF-8, strict errors), so the
**fixture** dies:

```
$ python3 -B r40-shaped-fixture.py --tool work/M52-DECODE-surrogateescape.py --work work
  File "/usr/lib/python3.14/subprocess.py", line 2194, in _communicate
    stdout = self._translate_newlines(stdout, self.stdout.encoding, self.stdout.errors)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 15: invalid start byte
```

The counter then reports `NO-SUMMARY rc=1` → **not killed**, for a reason that has nothing to do with
the tool's behaviour:

```
== F5: harness fragility -- the fixture dies on the tool's raw bytes (M52 surrogateescape)
   r40-shaped     killed=NO  (NO-SUMMARY rc=1)
   r40-scrubbed   killed=NO  (NO-SUMMARY rc=1)
```

The r40 fixture must capture the tool's output as **bytes** (`text=False`) and decode defensively
(`errors="replace"`) for the invalid-UTF-8 branch specifically. A fixture that crashes on the
mutant's output reports a false "not killed" — and the C3 kill rule's own "fixture has no own
failure summary" condition would then fire for the wrong reason. Note this interacts with F1:
**both** of the invalid-UTF-8 decode mutants (M46 traceback, M52 raw bytes) fail through the
harness rather than through the assertion.

## 9. What I checked and did not check

**Checked (all executed, all outputs quoted above):**

- The committed r39 C3 counter reproduces its committed receipt byte-for-byte at rc=0 (§1).
- The tool bytes are identical at the r40 base revision, at r39's `2f6e981`, and at HEAD (§1).
- The pristine behaviour of all three C3-named branches, at every position I could construct (§2).
- A 16-mutant systematic scan of the three branches plus three neighbouring branches, scored with
  the committed `score()` function against the committed r39 fixture and three candidate r40
  fixture shapes (§3).
- The control arm of the frozen predicate, independently: **all 13** mutants of the three named
  branches survive the committed r39 fixture; and I checked the new mutants against **all six**
  committed tool-scoring drift fixtures (`r36-worktree-drift.py`, `r37-drift-discrimination.py`,
  `r37-drift-escapes.py`, `r38-drift-write-envelope.py`, `r38-drift-record.py`,
  `r39-drift-record-rules.py`) — **none of the six kills any of M41/M42/M43/M46**, so the control
  statement is honest for the whole fixture set, not merely for the one named base fixture. (This
  is stronger than r39's own M13, which `W1RevC3Battery` showed is killed by
  `r38-drift-write-envelope.py`.)
- Both candidate remedies for F1, and the A5 control for each (§4).
- A carried-forward r40 battery and a 15-case superset r40 fixture, both scored against the
  committed `score()` (§6).

**Not checked:**

- I did not write or land any r40 fixture, counter or mutant file in the lane repo — this seat is
  read-only plus its own report. The r40-shaped, r40-scrubbed, r40-identical-only and
  r40-superset fixtures cited above are **scratch artefacts** under
  `/fast/scratch/hyaku/souji-r40/R40reviewer06`, not deliverables; the executor should build them
  properly in the lane with the lane's conventions.
- I did not evaluate the C1 or C2 axes (out of scope for this seat).
- I did not measure the r40 fixture against the *r39 counter's* `MUTANTS` tuple as the r40 battery;
  the battery is the r40 executor's to declare, and my simulated carry-forward (§6) is a
  construction, not a prediction.
- `r37-drift-mutants.py` and `r38-drift-mutants.py` were excluded: they are mutation drivers that
  mutate `--tool` and score a `--fixture`, so they cannot reject a tool mutant by construction.
- `r37-drift-escapes.py` exits rc=1 on pristine as well (`cases=12 pass=12 fail=0
  control=NO-BASE-…`), so its rc carries no information about mutants here.

## 10. Verdict

**The frozen r40 C3 predicate is not yet falsifiable, and on the evidence I can measure it is
reachable but the counter's kill contract will produce a wrong answer on exactly the branch the
predicate names.**

- **The C3 *coverage* claim is TRUE and independently confirmed**: the r39 fixture and counter
  genuinely have no cases for the three named branches — all 13 mutants of those branches survive
  the r39 fixture, and none of the six committed tool-scoring drift fixtures kills any of them. The
  r40 work has real coverage to add.
- **But the C3 *kill* arm is defective as inherited** (F1, HIGH): the committed scoring contract
  misreads a **tool-side** traceback as a **fixture-side** crash, because the fixture relays the
  tool's raw output into its own stdout and the counter scans the fixture's whole output for the
  traceback marker. The invalid-UTF-8 branch's hardest mutant (M46, strict decode) is therefore
  reported **survived** while the fixture demonstrably caught it (`fails=3`, own SUMMARY, exit 1).
  An r40 counter that reuses `census/round-39/c3-counter.py`'s `score()` unchanged will print
  `survived>=1` on a correct fixture, and C3's kill rule ("any mutant survives") will fire for a
  scoring artifact. **Fix the contract before measuring C3**: score the fixture's crash on the
  fixture's **stderr** only (`crash = "Traceback (most recent call last)" in proc.stderr`), which
  preserves the round-38 A5 intent (a fixture that crashes after its SUMMARY is still not a kill —
  measured) and un-masks M46 (measured `killed=yes rc=1 fails=3 fixture_crash=False`).
- **Two predicate-level traps the frozen wording invites** (both measured):
  - **F2**: "duplicate/multiple TOTAL rows" permits a fixture built only from **identical** TOTAL
    rows, which has **zero** discriminating power against the last-wins rule (M41 survives). The
    pristine is last-wins and the asymmetry (bad-then-good accepted, good-then-bad refused) is
    undocumented. The r40 fixture must use **differing** TOTAL rows.
  - **F3**: the r40 battery must contain **only new** mutants (the r39 fixture kills r39's own
    M11-M14 → `base_killed=4` fires), and the r40 fixture must be a **superset** of the r39 cases,
    not a replacement (carried-forward M11-M14 become survivors of the candidate arm otherwise).
- **Two fixture-design gaps** (measured survivors): the `--skip-unrecorded` case must assert the
  `SUMMARY` counters, not only the `UNRECORDED` row (M51 leaks `live_regs`; M50 drops
  `unreachable` and is observable only via an unrecorded repo whose `.git` is a file pointing at a
  missing gitdir); and the invalid-UTF-8 case must capture the tool's output as **bytes** (F5: with
  `text=True` the fixture itself dies with `UnicodeDecodeError` and the counter reports
  `NO-SUMMARY` → "not killed", for a reason unrelated to the tool).

**Bottom line for the r40 executor:** the coverage claim is sound and the control arm is honest;
the *measurement* is where r40 will go wrong. Fix the crash heuristic (F1) and use the
differing-TOTAL + SUMMARY-counter + bytes-capture case shapes (F2/F4/F5/F6) before spending a
counter run. The 15-case superset fixture I validated in scratch reaches
`mutants=12 killed=10 survived=2` against the committed `score()`, and its two survivors are
explained (F1 artifact; M54 already covered by the r38 fixture) — i.e. the recipe is achievable,
but only after F1 is fixed.

---

| # | finding | severity | kind | status |
|---|---|---|---|---|
| F1 | committed kill contract masks a tool-side traceback as a fixture crash (M46 scored survived despite `fails=3`) | HIGH | counter defect | remedy measured (stderr-only; A5 control preserved) |
| F2 | "duplicate/multiple TOTAL rows" case from *identical* TOTAL rows is vacuous against last-wins (M41 survives) | HIGH | predicate ambiguity | discriminating case measured |
| F3 | carried-forward battery trips `base_killed`; r40 fixture must be a superset, not a replacement | MEDIUM | design constraint | both arms measured |
| F4 | `--skip-unrecorded` owns `live_regs`/`live_prunable`; a DRIFT-row-only case misses M51 | MEDIUM | coverage gap | observable difference measured |
| F5 | fixture harness dies (`UnicodeDecodeError`) on the raw bytes of the very branch it tests (M52 → `NO-SUMMARY`) | MEDIUM | harness fragility | measured; byte capture required |
| F6 | `unreachable` counter observable only via an unrecorded repo whose `.git` is a file → missing gitdir | MEDIUM | coverage gap | measured (`unreachable=1` vs `0`) |
| — | control arm of the frozen C3 predicate ("r39 fixture/counter kills none of the new mutants") | — | **CONFIRMED TRUE** | all 13 new mutants survive the r39 fixture; none of 6 committed drift fixtures kills them |
