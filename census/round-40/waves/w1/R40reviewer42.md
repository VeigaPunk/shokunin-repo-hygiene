# R40reviewer42 — independent attack on the frozen r40 C3 (coverage) claim

Seat: reviewer. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base revision (frozen, from `census/round-40/preregistration.txt`): `0242085909fb6a4ee041c5443d76316ac6d59d4b`
(round-39 verified tip). Lane HEAD at measurement: `be4cb61`.
Scratch: `/fast/scratch/hyaku/souji-r40/R40reviewer42` (removed at end of seat; see §9).
Read-only against the lane: no commit, no push, no mutating git/jj, no lane file written except this
report. Git used only as `git -C <lane> show|rev-parse|status` (read-only) and `git init/commit`
inside scratch fixture repos.

## 0. The claim under attack

`census/round-40/preregistration.txt` (committed 16:26, `ls -la census/round-40/` shows it is the
only file in `census/round-40/`):

> **C3 — coverage (current evidence 8)**
> Predicate: r40 fixture adds behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`,
> and invalid UTF-8 record bytes; each declared single-defect mutant is killed by the r40 fixture, the
> pristine candidate passes, and all mutants survive the r39 base fixture. Control: r39 fixture/counter
> has no cases for these branches and kills none of the new mutants. Kill if pristine fails, any mutant
> survives, any base mutant is killed, or fixture has no own failure summary.

**Distinct edge case named by this seat (item 42):** the *achievability and vacuity* of the C3
measurement contract, not its topic selection. Specifically: the predicate's kill conditions are
evaluated by a counter whose own shape decides what "a mutant", "a case", and "the r40 fixture" mean,
and three of the predicate's four kill clauses can be satisfied while the *named* branches are
unmeasured. This is a different cut from any other seat's: the topic (three named branches) is
correct and worth covering; the finding is that the frozen predicate as written cannot distinguish
"r40 covered the three branches" from "r40 declared one mutant and added one case".

The three named branches are genuinely uncovered today (control leg verified, §2), so the C3
*direction* is sound. The finding is about the *witness*.

## 1. Method

All measurements reuse the **canonical** scoring contract by importing it from the committed r39
counter rather than re-deriving it:

```python
spec = importlib.util.spec_from_file_location("r39c3", LANE + "/census/round-39/c3-counter.py")
r39c3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r39c3)
score = r39c3.score          # census/round-39/c3-counter.py:87-103
```

Tool bytes come from committed bytes only (`git show <rev>:tools/souji-worktree-drift.py`); fixture
bytes come from `git show <rev>:tests/fixtures/...`. Every mutant is a single-defect anchor
replacement whose anchor count in the base tool is asserted to be exactly 1 (a count != 1 would be a
battery defect, not a kill — the r39 counter's own rule, `c3-counter.py:170-173`).

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin
$ git log --oneline -3
be4cb61 round-39 verifier spot-check (integrator, hyaku): non-author admit/reject
0242085 round-39: lesson — carry entry names its resolution token
c2dcd62 round-39: lesson — Seat-reported failures carry for W1CritAssimilation (LG-SEAT-UNCARRIED)
$ git status --porcelain
?? census/round-40/            # the frozen preregistration, untracked at HEAD
$ git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py | sha256sum
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  -
$ git show be4cb61:tools/souji-worktree-drift.py | sha256sum
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  -
```

The base tool is byte-identical at the frozen base revision and at HEAD, so the base-revision arm
and the after-revision arm of C3 are measured against the same audited bytes.

## 2. Control leg — VERIFIED TRUE (the three branches really are uncovered)

**Verdict: PASS.** The control clause of C3 ("r39 fixture/counter has no cases for these branches and
kills none of the new mutants") holds. Evidence:

```
$ grep -rl -- '--skip-unrecorded' tests/ tools/          # in tests/: NONE (only the tool itself)
tests/fixtures/  -> NONE
$ grep -ln 'xff|surrogate' tests/fixtures/*.py
tests/fixtures/r22-result-oracle.py        # different tool (r16-landing-gate), not the drift record
```

No committed fixture passes `--skip-unrecorded`; none writes two `TOTAL` rows in one record body;
none writes non-UTF-8 bytes into a drift record. Scoring the three branch mutants against the
**committed** r39 fixture:

```
r39-base scores D1: killed=False rc=0 fails=0 crash=False
r39-base scores S1: killed=False rc=0 fails=0 crash=False
r39-base scores U2: killed=False rc=0 fails=0 crash=False
```

`D1` = keep-first TOTAL, `S1` = always skip unrecorded, `U2` = decode "ignore". All three survive the
r39 base fixture (`base_killed=0` as the predicate requires), and none of the three branches has a
committed case. The C3 premise is sound.

## 3. FINDING 1 (HIGH) — the frozen predicate is satisfiable with two of three named branches unmeasured

**Falsifier, executed.** Take the canonical r39 counter, change **only** its `MUTANTS` tuple to
declare **one** mutant (the duplicate-TOTAL branch), and give it a fixture that is the **committed r39
fixture's seven cases plus one duplicate-TOTAL case** (`padded.py`, 8 cases). The `--skip-unrecorded`
and invalid-UTF-8 branches get no case and no mutant.

```
$ python3 -B <r39 counter, MUTANTS patched to one entry> \
    --root <lane> --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
    --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
    --fixture <padded.py: 8 cases> \
    --base-fixture tests/fixtures/r39-drift-record-rules.py --scratch <scratch>
MUTANT D1 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=1 killed=1 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=58d18ac63db9
exit=0
```

Exit 0. Every one of the predicate's four kill clauses reads satisfied:

| frozen kill clause | value | reads as |
|---|---|---|
| pristine fails | `pristine=ok` | not fired |
| any mutant survives | `survived=0` | not fired |
| any base mutant is killed | `base_killed=0` | not fired |
| fixture has no own failure summary | `SUMMARY cases=8 …` present | not fired |

Yet the receipt carries **no evidence at all** for two of the three named branches. The predicate
never binds a *branch* to a *mutant*; it binds the *set* of whatever mutants the counter declares to
the fixture. The counter's own `MUTANTS` tuple is the only thing that says which branches are
claimed, and it is written by the same party that writes the fixture — so the receipt is
self-certifying. Add the other two mutants to the same counter and the same 8-case fixture and the
truth appears immediately:

```
MUTANT D1 killed=yes ... | MUTANT S1 killed=no rc=0 fails=0 | MUTANT U2 killed=no rc=0 fails=0
SUMMARY mutants=3 killed=1 survived=2 pristine=ok base_killed=0 cases=8
exit=1
```

The `survived=2` is the honest reading of the same fixture. The frozen predicate as written accepts
the `mutants=1` reading.

**Why this is a defect of the frozen claim, not a nitpick.** The predicate's own words promise
"behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and invalid UTF-8 record
bytes", and its control clause is stated per-branch ("has no cases for **these branches**"). The
measurement that certifies it therefore has to be per-branch too. A counter that reports one
aggregate `mutants=N killed=N` line cannot certify a per-branch promise; it can only certify that
whatever it declared was killed.

**Minimal repair (does not touch the frozen predicate text, which is frozen):** require the r40
counter to print and gate a per-branch row, e.g. `BRANCH duplicate-total mutants=1 killed=1
survived=0`, `BRANCH skip-unrecorded mutants=1 killed=1 survived=0`, `BRANCH invalid-utf8 mutants=1
killed=1 survived=0`, and require `survived=0` **for each of the three named branches** (not just in
aggregate), plus require the branch set to equal exactly the three names. Then the `mutants=1`
receipt above cannot be produced without covering all three.

## 4. FINDING 2 (HIGH) — the kill contract cannot score the invalid-UTF-8 branch's natural mutant

The canonical `score()` (`census/round-39/c3-counter.py:87-103`) defines:

```python
crash  = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)   # line 101
killed = proc.returncode == 1 and fails > 0 and not crash                       # line 102
```

`proc` here is the **fixture** process, and the r39-shaped fixture deliberately echoes the *tool's*
captured stdout+stderr into **its own stdout** (`tests/fixtures/r39-drift-record-rules.py:79-80`,
`out=%r` of `out.replace("\n"," ")[:160]`; the r38 fixture does the same at
`tests/fixtures/r38-drift-record.py:92-93`). So when the mutated tool **raises**, the fixture's
stdout contains the tool's traceback, the counter's crash detector fires, and the mutant is scored
**survived** even though the fixture's own case genuinely failed.

The invalid-UTF-8 branch's most natural single-defect mutant is exactly a raising mutant: replacing
`decode("utf-8", "replace")` with `decode("utf-8", "strict")` raises `UnicodeDecodeError` on a
non-UTF-8 record byte, and the tool's `main()` catches only `Refusal`, so it propagates.

Executed, with the r40-shaped fixture and the canonical score():

```
MUTANT U1 killed=no base_killed=no rc=1 fails=1 crash=True base:rc=0 fails=0 crash=False
SUMMARY mutants=1 killed=0 survived=1 pristine=ok base_killed=0 cases=6
counter exit=1
```

`fails=1` — the fixture **did** detect the change — but `crash=True` suppresses the kill. The same
effect reproduces against the **committed** r39 fixture (not just my probe), using a tool that
raises on a case the committed fixture already covers:

```
$ <committed r39 fixture> + <tool that raises on the outside-root case>
score -> killed=False rc=1 fails=1 crash=True cases=7
case-outside-root=FAIL rc=1 want=2 missing=['RECORD-OUTSIDE-ROOT']
  out='Traceback (most recent call last): ...'
SUMMARY cases=7 pass=6 fail=1
```

**Consequence for the frozen C3 claim.** The C3 kill clause "any mutant survives" is evaluated by
this contract. If the r40 counter declares the strict-decode mutant for the invalid-UTF-8 branch —
the most direct encoding of that branch — the counter reports `survived=1` and C3 reads as killed,
**even though the r40 fixture killed that mutant**. The defect is in the *measurement*, not the
fixture: the fixture's diagnostic echo (a good practice, and the r38 A5 shape) is read by the
counter as "the fixture crashed".

Two independent fixes, either of which keeps the r38 A5 spirit:

1. **Score the crash against the tool, not the fixture.** The counter already runs the fixture; the
   fixture already knows the tool's stderr. Have the fixture print the tool's stderr on a **separate
   stream** (or a separate marker line the counter strips before the crash check), so the counter's
   crash detector sees only the fixture's own frames. Or: have the counter treat `crash` as fatal
   only when the traceback's frames are in the *fixture* file.
2. **Make the invalid-UTF-8 branch's mutant non-raising**, e.g. decode `"ignore"` (`U2`), which is
   already shown to be killable (§5) — but note this weakens the branch: `"ignore"` vs `"replace"`
   differ in the *replacement* character, while `"strict"` is the only mutant that distinguishes
   "invalid bytes are rejected" from "invalid bytes are tolerated". A counter that silently picks
   `U2` to dodge the crash detector is measuring a weaker property than the branch name implies.

## 5. FINDING 3 (MEDIUM) — the invalid-UTF-8 branch has three different pristine verdicts depending on byte placement

The branch name ("invalid UTF-8 record bytes") does not determine an expected verdict, and the three
placements give three different ones against the pristine base tool. Measured:

| placement | pristine exit | pristine output |
|---|---|---|
| byte in the **name** field (`REPO\tal\xffpha\t…`) | 1 | `DRIFT\tABSENT\tal\ufffdpha` — row **accepted**, byte replaced by U+FFFD |
| byte in the **numeric** field (`regs=1\xff`) | 2 | `REFUSAL RECORD-MALFORMED: line 1 does not match the census schema` |
| byte in a **comment** line (`# note \xff here`) | 0 | `SUMMARY … record_repos=1` — line **ignored** |

A fixture that pins one placement does not pin the branch. And the three placements are **not**
equally discriminating: the name-field placement is the only one where the byte is *replaced* rather
than rejected, so only it distinguishes `decode "replace"` from `decode "ignore"` (both other
placements reject/ignore identically). Measured with the `U2` (decode "ignore") mutant:

```
byte-in-NAME-field     pristine exit=1 (ABSENT)   decode-ignore exit=0   <- discriminated
byte-in-NUMERIC-field  pristine exit=2 (REFUSED)  decode-ignore exit=0   <- discriminated
byte-in-COMMENT-line   pristine exit=0 (ignored)  decode-ignore exit=0   <- NOT discriminated
```

So the comment-line placement is a **dead case**: it passes against the mutant and kills nothing. A
fixture that spends its invalid-UTF-8 case on a comment line would show `killed=0` and could not
distinguish "covered" from "not covered".

**Consequence.** The frozen predicate says "behavioral cases for … invalid UTF-8 record bytes"
without naming a placement, and the kill clause is "each declared single-defect mutant is killed".
A r40 counter could declare `U2`, write the invalid-UTF-8 case on a comment line, and report
`killed=1` — while the branch's *actual* subject (a record byte that is not valid UTF-8 in a field
that carries meaning) is untouched. The receipt cannot distinguish this from a real case.

**Minimal repair:** freeze the placement in the predicate or the counter (name-field, where the byte
is replaced and the row accepted, is the only placement that is both discriminating and reachable
without a refusal class), and require the fixture's case to be killed by the branch's mutant.

## 6. FINDING 4 (MEDIUM) — a duplicate-TOTAL case built from two IDENTICAL TOTAL rows cannot kill the keep-first mutant

The branch name says "duplicate/multiple TOTAL rows". The natural case — two identical TOTAL rows —
is **not discriminating**, because the tool's only distinction is *which* TOTAL it keeps, and with
identical rows first-wins and last-wins produce identical output. Measured:

```
two-TOTAL-IDENTICAL         pristine  exit=0 (SUMMARY …)
two-TOTAL-IDENTICAL         keep-first exit=0 (SUMMARY …)      <- identical, NOT killed
two-TOTAL-FIRST-disagrees   pristine  exit=0 ; keep-first exit=2 (RECORD-MALFORMED: TOTAL repos=9 but 2 REPO rows)
two-TOTAL-LAST-disagrees    pristine  exit=2 ; keep-first exit=0
```

Confirmed end-to-end through the counter: with a duplicate-TOTAL case built from two **identical**
rows, the keep-first mutant `D1` is **not killed**:

```
$ <counter with D1> --fixture <fixture whose duplicate-total case uses two IDENTICAL TOTAL rows>
MUTANT D1 killed=no base_killed=no rc=0 fails=0 crash=False
SUMMARY mutants=1 killed=0 survived=1 pristine=ok base_killed=0 cases=8
```

The duplicate-TOTAL case only kills `D1` if the two TOTAL rows **disagree** (first disagrees, last
agrees) — which is what `padded.py` uses, and which does produce `MUTANT D1 killed=yes … exit=0`.

**Consequence.** "Duplicate/multiple TOTAL rows" is under-specified to the point where the obvious
case for it is a no-op case: a r40 fixture written the obvious way declares the branch, reports a
case for it, and the branch's mutant survives — or, worse, the counter declares no mutant for it
because the obvious case "does not discriminate", and the branch is reported covered anyway. The
pristine tool's real behaviour here is also worth recording: **the last TOTAL row wins and earlier
TOTAL rows are silently discarded** — a record whose first TOTAL disagrees (`repos=9` vs 2 REPO
rows) is accepted with exit 0 when a second, agreeing TOTAL follows. There is no refusal class for a
duplicate TOTAL in the tool's docstring (`tools/souji-worktree-drift.py:44-49` lists
`RECORD-MALFORMED` for "a duplicated name, or a TOTAL row that disagrees"; a *duplicated* TOTAL row
is not named).

## 7. FINDING 5 (MEDIUM) — the "pristine passes" clause is a coin flip on the two undocumented branches

Two of the three named branches have **no refusal class** in the tool's own docstring and no
committed fixture to fix their expected verdict. The two defensible readings of "duplicate/multiple
TOTAL rows" and "invalid UTF-8 record bytes" are: *refuse* them (exit 2, `RECORD-MALFORMED`) or
*tolerate* them (the pristine behaviour). Under the refusal reading the **pristine candidate fails**,
and the frozen kill clause "pristine fails" fires — C3 reads as killed for a reason that has nothing
to do with mutant coverage.

Executed with a refusal-reading fixture against the pristine base tool:

```
$ python3 -B refusal.py --tool <base tool> --work <scratch>
case-multi-total-refused=FAIL
case-invalid-utf8-refused=FAIL
SUMMARY cases=2 pass=0 fail=2
```

and through the counter:

```
3-mutant/refusal-fix  exit=1 | SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=2
```

whereas the tolerance-reading fixture passes pristine cleanly (`focused.py` → `SUMMARY cases=3
pass=3 fail=0`, rc 0). So the same counter and the same mutants produce `pristine=FAIL` or
`pristine=ok` purely as a function of which reading the fixture author picked, and the frozen
predicate does not say which reading is the claimed behaviour.

**This is the deepest form of the seat's edge case.** C3 as frozen asks a *measurement* to certify a
*semantic* claim ("r40 covers these three branches") while the semantics of two of the three are
unpinned. A counter cannot certify semantics it was never given.

**Minimal repair (measurement-side, predicate text untouched):** the r40 counter should state the
expected verdict per branch in its own frozen table (branch → expected rc/tokens), so that both the
candidate fixture and the control arm are scored against one pinned reading; and the counter should
distinguish "pristine disagrees with the pinned reading" (a real tool/fixture defect, worth a kill)
from "the pinned reading was never frozen" (an authoring gap, which the counter should refuse to
evaluate rather than score as a kill).

## 8. What the counter's `cases >= 6` floor does to a focused r40 fixture

The canonical pristine check (`census/round-39/c3-counter.py:155-162`) requires `cases >= 6`:

```python
pristine_ok = (pristine_proc.returncode == 0 and int(match.group(3)) == 0
               and int(match.group(2)) == cases and cases >= 6)
```

A **focused** r40 fixture with exactly one case per named branch (3 cases) is rejected:

```
3-mutant/3-case   exit=1 | SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=3
```

The r39 floor is a round-39 fact (r39's fixture has 7 cases); carried into r40 unchanged it forces
the r40 fixture to pad to six cases — which is compatible with padding with cases that do not touch
the three named branches, i.e. it makes Finding 1 easier to satisfy, not harder. If the r40 counter
keeps the `cases >= 6` floor it should say so in the frozen predicate, or the floor should become
"at least one case per named branch, and at least as many cases as the branch count".

## 9. Verdict

**C3 is directionally right and, as frozen, not falsifiable on its own terms.** The three named
branches are genuinely uncovered (control leg verified, §2). But the frozen predicate's kill clauses
are evaluated by a counter whose own shape decides the claim, and:

| # | Finding | Severity | Evidence |
|---|---|---|---|
| 1 | The predicate is satisfiable with two of three named branches unmeasured: a counter declaring one mutant + an 8-case fixture (7 committed r39 cases + 1 duplicate-TOTAL) exits 0 with `mutants=1 killed=1 survived=0 pristine=ok base_killed=0` while `--skip-unrecorded` and invalid-UTF-8 have no case and no mutant. | HIGH | §3 |
| 2 | The canonical kill contract cannot score the invalid-UTF-8 branch's natural mutant: `score()` reads "Traceback" from the **fixture's** stdout, which the r39-shaped fixture populates with the **tool's** stderr, so the raising mutant `decode "strict"` is scored `survived=1` although the fixture failed the case (`fails=1`). Reproduces against the committed r39 fixture too. | HIGH | §4 |
| 3 | The invalid-UTF-8 branch has three pristine verdicts by byte placement; only the name-field placement discriminates `replace` vs `ignore`; the comment-line placement is a dead case that kills nothing. | MEDIUM | §5 |
| 4 | A duplicate-TOTAL case built from two **identical** TOTAL rows cannot kill the keep-first mutant (`D1 killed=no`); only a *disagreeing* pair discriminates. The tool keeps the LAST TOTAL and silently discards earlier disagreeing ones, with no refusal class named for a duplicate TOTAL. | MEDIUM | §6 |
| 5 | "pristine fails" is a coin flip on the two undocumented branches: the refusal reading of duplicate-TOTAL / invalid-UTF-8 makes pristine fail (`pristine=FAIL`, exit 1) while the tolerance reading passes. The predicate does not pin which reading is claimed. | MEDIUM | §7 |
| 6 | The inherited `cases >= 6` pristine floor rejects a focused one-case-per-branch fixture (`pristine=FAIL cases=3`) and pushes the fixture toward padding. | MEDIUM | §8 |

**Concrete falsifier delivered** (Finding 1): the executed counter receipt
`SUMMARY mutants=1 killed=1 survived=0 pristine=ok base_killed=0 cases=8`, exit 0, against a fixture
that covers one of the three named branches.

**Bounded measurement plan for the r40 counter** (does not alter the frozen predicate text, which is
frozen before after-data):

1. Freeze a per-branch table in the counter: branch → mutant id, anchor, expected verdict
   (rc + tokens), and the fixture case that must kill it. Three rows, one per named branch.
2. Print and gate per branch: `BRANCH <name> mutants=1 killed=1 survived=0`; require `survived=0`
   for **each** of the three named branches, and require the branch set to equal exactly those three
   names. This closes Finding 1.
3. Fix the crash detector (Finding 2): either score the tool's stderr separately from the fixture's
   stdout, or make the invalid-UTF-8 mutant non-raising *and* state in the frozen table that the
   branch is scored by the `replace`/`ignore` distinction, not by `strict`.
4. Pin the placement (Finding 3) and the disagreeing-TOTAL shape (Finding 4) in the per-branch
   table, so "one case per branch" means a discriminating case.
5. Replace the blanket "pristine fails" with "pristine disagrees with the **pinned** per-branch
   verdict" (Finding 5), and refuse to evaluate (exit 2) when a branch has no pinned verdict rather
   than scoring it as a kill.

**Honest limitation:** items 2–5 of the table above are repairs to the *r40 counter*, which does not
exist yet (`census/round-40/` contains only `preregistration.txt`). I have measured the canonical
r39 counter's behaviour, which the r40 counter is expected to inherit (the r39 C3 predicate names
the same contract: "a kill needs the fixture's own `SUMMARY cases=… fail>0`, no traceback, exit 1",
`census/round-39/preregistration.txt`). If the r40 counter deliberately departs from that contract,
Findings 2 and 6 do not bind it — Findings 1, 3, 4, and 5 are properties of the frozen predicate
text itself and bind regardless of the counter.

## 10. Reproduction

Scratch (all under `/fast/scratch/hyaku/souji-r40/R40reviewer42`, removed at end of seat):

| file | role |
|---|---|
| `base-tool.py` | `git show 02420859:tools/souji-worktree-drift.py` (sha256 `e48ed08e6728…`) |
| `r40-candidate.py` | 6-case r40-shaped probe fixture (3 branches + controls) |
| `focused.py` | 3-case fixture, one case per named branch (tolerance reading) |
| `refusal.py` | 2-case fixture, refusal reading of the two undocumented branches |
| `padded.py` | committed r39 fixture's 7 cases + 1 discriminating duplicate-TOTAL case (8) |
| `harness.py` | scores all mutants × {probe, r39 base, r38 base} via the canonical `score()` |
| `isolate.py` | vacuity (empty battery) + crash-echo collision + pristine verdicts |
| `forks.py` | per-branch fork quantification (F1, F1b, F3, control) |

Commands actually run (all read-only against the lane):

```
git -C <lane> rev-parse --show-toplevel
git -C <lane> log --oneline -3
git -C <lane> status --porcelain
git -C <lane> show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
git -C <lane> show be4cb61:tools/souji-worktree-drift.py
git -C <lane> show be4cb61:tests/fixtures/r39-drift-record-rules.py
git -C <lane> show be4cb61:tests/fixtures/r38-drift-record.py
python3 -B harness.py
python3 -B isolate.py
python3 -B forks.py
python3 -B focused.py --tool base-tool.py --work .
python3 -B refusal.py  --tool base-tool.py --work .
```

Every mutant's anchor count in the base tool was asserted to be exactly 1 before scoring; the
counter's own `ALANCHOR-COUNT` guard (`c3-counter.py:170-173`) printed no defect row in any run.

Scratch removal (verified after cleanup):

```
$ rm -rf /fast/scratch/hyaku/souji-r40/R40reviewer42
$ ls -d /fast/scratch/hyaku/souji-r40/R40reviewer42 2>&1
ls: cannot access '/fast/scratch/hyaku/souji-r40/R40reviewer42': No such file or directory
```

No installs were needed for this seat; the toolchain (python3, git) was already present, so the
tooling directive's install channel was not exercised.

**Seat verdict: the C3 claim is NOT falsified in its topic — but its frozen measurement contract is
defective.** Findings 1, 2 and 5 each independently allow a receipt that reads "C3 satisfied" while
the claim it is supposed to certify does not hold. Finding 1 is a concrete, executed falsifier.
