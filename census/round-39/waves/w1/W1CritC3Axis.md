# W1CritC3Axis — C3's axis and magnitude: is the record-rule mutation coverage marginal?

Seat: critic (leaf). Role: attack C3's axis and magnitude, not the task owner.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
lane base `ed30b7f5b77939c9073348d810730bc4f355708d`).
Measured revision: lane `HEAD = 2201778e7736af82e7d8a42dec2494f115bf3923` (== `origin/master`).
Scratch: `/fast/scratch/hyaku/souji-r39/W1CritC3Axis` (removed at exit — §Scratch).
No lane file was created or modified by this seat. No mutating git/jj command was run (only `log`,
`show`, `diff`, `status`, `rev-parse`, `ls-tree`, `cat-file`, `merge-base --is-ancestor`).
No tool was installed or upgraded.

## Axes named

| Axis | Question this seat scores |
|---|---|
| A1 marginal coverage | How many record-rule classes does the round *newly* assert, counting only classes no pre-round fixture asserts? |
| A2 claim truth (calibration) | Does the claim's sentence ("four record-rule mutants ... every existing drift fixture leaves alive") survive lane bytes? |
| A3 instrument fidelity | Does `c3-counter.py` measure the property the claim states, over the same quantifier? |
| A4 mutation distinctness | Are M11–M14 four classes or variants of one? Does each kill bind to a distinct assertion? |
| A5 control provenance | Are the frozen before/after receipts reproducible from committed bytes with a named command? |

## Checks

Every command below was run from cwd `/home/vgpnk/Projects/shokunin/souji-shokunin` (or the
scratch dir named in the command); output is quoted verbatim.

### C1 — frozen C3 predicate at HEAD (default arguments)

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch /fast/scratch/hyaku/souji-r39/W1CritC3Axis
```

```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
RC=0
```

Verdict: **PASS** — the frozen predicate (`mutants=4 killed=4 survived=0 pristine=ok base_killed=0
cases>=6`) is met at HEAD, exit 0. This check says nothing about marginality; it only says the
arithmetic of the instrument holds.

### C2 — frozen after receipt reproduces byte-for-byte

Same command as C1, stdout captured in Python (`subprocess`, `cwd=LANE`) and compared to
`census/round-39/records/c3-after.txt`:

```
RC= 0
DIFF-EMPTY
```

Verdict: **PASS** — `c3-after.txt` is honest and reproducible at HEAD, including `tool_sha` and
`fixture_sha`.

### C3 — frozen before receipt reproduces byte-for-byte

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1CritC3Axis
```

```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

`diff` against the receipt: `DIFF-EMPTY`. `sha256sum tests/fixtures/r38-drift-record.py` →
`ac0be0e7a49e…`, i.e. `cases=10`/`fixture_sha=ac0be0e7a49e` are the **r38 record fixture**, not a
draft.

Verdict: **PASS** — the control is honest. Two provenance notes for the L1: the receipt does not
name its `--fixture` argument (only `W1ExecC3Baseline.md` §1 does), and the counter reads the
candidate fixture from the **working tree**, so the control is a property of the caller's `--fixture`
argument, not of `--rev`.

### C4 — base-revision arm with the landed candidate fixture

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch /fast/scratch/hyaku/souji-r39/W1CritC3Axis
```

```
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
RC=0
```

Verdict: **WARN (A3)** — with the delivered fixture, the base revision satisfies every field of the
frozen predicate; the only difference from C1 is `tool_sha`. That is inherent to a coverage claim
(the deliverable is the fixture), but it means the counter's discrimination rests entirely on the
`--fixture` argument and on fixture bytes the counter does not pin to `--rev`. A later edit to
`tests/fixtures/r39-drift-record-rules.py` silently moves both arms.

### C5 — M11–M14 against *every* pre-round case fixture (HEAD)

Driver (scratch, removed at exit): reads `git show HEAD:tools/souji-worktree-drift.py`, applies each
`MUTANTS` edit from `c3-counter.py` at its anchor, then runs each pre-round case fixture with
`--tool <mutant> --work /fast/scratch/hyaku/souji-r39/W1CritC3Axis`.

```
ANCHOR M11 count=1
ANCHOR M12 count=1
ANCHOR M13 count=1
ANCHOR M14 count=1
--- pristine per fixture (at HEAD)
r36-worktree-drift.py          pristine rc=0 SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
r37-drift-discrimination.py    pristine rc=0 SUMMARY cases=6 pass=6 fail=0
r37-drift-escapes.py           pristine rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL
r38-drift-record.py            pristine rc=0 SUMMARY cases=10 pass=10 fail=0
r38-drift-write-envelope.py    pristine rc=0 SUMMARY cases=12 pass=12 fail=0
--- mutant matrix
M11 r36-worktree-drift.py          rc=0 killed=no SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
M11 r37-drift-discrimination.py    rc=0 killed=no SUMMARY cases=6 pass=6 fail=0
M11 r37-drift-escapes.py           rc=1 killed=no SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL
M11 r38-drift-record.py            rc=0 killed=no SUMMARY cases=10 pass=10 fail=0
M11 r38-drift-write-envelope.py    rc=0 killed=no SUMMARY cases=12 pass=12 fail=0
M12 r36-worktree-drift.py          rc=0 killed=no SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
M12 r37-drift-discrimination.py    rc=0 killed=no SUMMARY cases=6 pass=6 fail=0
M12 r37-drift-escapes.py           rc=1 killed=no SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL
M12 r38-drift-record.py            rc=0 killed=no SUMMARY cases=10 pass=10 fail=0
M12 r38-drift-write-envelope.py    rc=0 killed=no SUMMARY cases=12 pass=12 fail=0
M13 r36-worktree-drift.py          rc=0 killed=no SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
M13 r37-drift-discrimination.py    rc=0 killed=no SUMMARY cases=6 pass=6 fail=0
M13 r37-drift-escapes.py           rc=1 killed=no SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL
M13 r38-drift-record.py            rc=0 killed=no SUMMARY cases=10 pass=10 fail=0
M13 r38-drift-write-envelope.py    rc=1 killed=YES SUMMARY cases=12 pass=11 fail=1 case-record-outside-root=FAIL rc=1 out=['DRIFT\tABSENT\t../escaped\trecorded regs=1', 'DRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0']
M14 r36-worktree-drift.py          rc=0 killed=no SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
M14 r37-drift-discrimination.py    rc=0 killed=no SUMMARY cases=6 pass=6 fail=0
M14 r37-drift-escapes.py           rc=1 killed=no SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL
M14 r38-drift-record.py            rc=0 killed=no SUMMARY cases=10 pass=10 fail=0
M14 r38-drift-write-envelope.py    rc=0 killed=no SUMMARY cases=12 pass=12 fail=0
```

Verdict: **FAIL for the claim (A2)** — M11, M12, M14 survive all five pre-round case fixtures; **M13
is killed by the pre-round fixture `r38-drift-write-envelope.py`**, case `record-outside-root`.
"Every existing drift fixture leaves alive" is false for one of four mutants.

### C6 — same matrix at the base revision

```
python3 -B matrix.py ed30b7f5b77939c9073348d810730bc4f355708d
```

```
M13 r38-drift-record.py            rc=0 killed=no SUMMARY cases=10 pass=10 fail=0
M13 r38-drift-write-envelope.py    rc=1 killed=YES SUMMARY cases=12 pass=11 fail=1 case-record-outside-root=FAIL rc=1 out=['DRIFT\tABSENT\t../escaped\trecorded regs=1', 'DRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0']
```

Verdict: **FAIL for the claim (A2)** — identical at `ed30b7f`, so this is pre-round coverage, not an
r39 artefact. `git ls-tree ed30b7f5b77939c9073348d810730bc4f355708d tests/fixtures/r38-drift-write-envelope.py`
→ `100755 blob 0f762f4d64ae0778f833eea47ed926896bef7137 tests/fixtures/r38-drift-write-envelope.py`;
the fixture is in the base tree, and `census/round-39/c2-counter.py:57` enumerates it as a consumer
(`("r38-drift-envelope", "tests/fixtures/r38-drift-write-envelope.py", DRIFT, "--tool")`).

### C7 — the frozen instrument confirms the violation

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1CritC3Axis
```

```
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=1 survived=3 pristine=ok base_killed=0 cases=12 tool_sha=e48ed08e6728 fixture_sha=d6fed4af1e8a
RC=1
```

Verdict: **CONFIRMED (A3)** — the lane's own counter, at the delivered tool bytes, reads `killed=1`
when pointed at the pre-round envelope fixture. `base_killed=0` in C1 is therefore an artefact of
`--base-fixture` defaulting to the single file `r38-drift-record.py`; the counter cannot express the
claim's universal quantifier ("every existing drift fixture").

### C8 — are the four mutants distinct classes or variants of one?

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r39-drift-record-rules.py \
  --tool /fast/scratch/hyaku/souji-r39/W1CritC3Axis/mutants-HEAD/<M>.py \
  --work /fast/scratch/hyaku/souji-r39/W1CritC3Axis
```

```
== M11
case-trailing-space=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema']
SUMMARY cases=7 pass=6 fail=1
== M12
case-crlf=FAIL rc=2 out='REFUSAL RECORD-MALFORMED: line 1 does not match the census schema '
SUMMARY cases=7 pass=6 fail=1
== M13
case-outside-root=FAIL rc=1 want=2 missing=['RECORD-OUTSIDE-ROOT'] out='DRIFT\tABSENT\t../escape\trecorded regs=1 DRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0 DRIFT\tUNRECORDED\tbeta\tlive regs=1 prunable=0 …'
SUMMARY cases=7 pass=6 fail=1
== M14
case-indented-comment=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema']
SUMMARY cases=7 pass=6 fail=1
```

Verdict: **PASS for distinctness (A4)** — each mutant fails exactly one case and a *different* case:
M11↔`trailing-space`, M12↔`crlf`, M13↔`outside-root`, M14↔`indented-comment`. M11 and M14 share the
skip anchor (`SKIP_ANCHOR`) but are not variants: M11 survives `indented-comment` and M14 survives
`trailing-space` (each run reads `pass=6 fail=1`). So the mutation set is four distinct edits, four
distinct assertions — the defect is not redundancy among the mutants, it is that one mutant's class
was already asserted before the round.

### C9 — how much of M13's class does the mutant actually remove?

Probe: a fleet with a real escaping repo, record row `REPO\t../sibling\tregs=1\tprunable=0`, pristine
vs M13.

```
mutants-HEAD/pristine.py rc=2 REFUSAL RECORD-OUTSIDE-ROOT: ../sibling resolves outside /fast/scratch/hyaku/souji-r39/W1CritC3Axis/probe2/root/fleet
mutants-HEAD/M13.py      rc=2 REFUSAL RECORD-OUTSIDE-ROOT: ../sibling gitdir resolves outside /fast/scratch/hyaku/souji-r39/W1CritC3Axis/probe2/root/fleet
```

Verdict: **OVERCLAIM in the counter docstring (A4)** — `c3-counter.py` describes M13 as "the record
row's outside-root refusal is removed". It is not: the gitdir guard (`tools/souji-worktree-drift.py`,
the `RECORD-OUTSIDE-ROOT: %s gitdir resolves outside %s` arm) still refuses a row that resolves to a
real work tree. M13 removes only the name-path guard, so the documented class ("a record row, **or
the gitdir it resolves to**, escapes `--root`") survives for real repositories. The candidate's
`outside-root` case and the pre-round envelope case both use a *non-existent* escape target, i.e.
the same sub-arm.

### C10 — is there a genuinely novel fourth class the fixture already discriminates?

Probe mutant M15 ("a REPO row after a TOTAL row is refused" — insert
`if total is not None: raise Refusal("RECORD-MALFORMED: line %d REPO row after TOTAL" % lineno)`
in the ROW branch; anchor count 1):

```
r36-worktree-drift.py          rc=0 SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
r37-drift-discrimination.py    rc=0 SUMMARY cases=6 pass=6 fail=0
r37-drift-escapes.py           rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL
r38-drift-record.py            rc=0 SUMMARY cases=10 pass=10 fail=0
r38-drift-write-envelope.py    rc=0 SUMMARY cases=12 pass=12 fail=0
r39-drift-record-rules.py      rc=1 SUMMARY cases=7 pass=6 fail=1 case-total-before-rows=FAIL rc=2 want=0 missing=['SUMMARY', 'record_repos=2'] out='REFUSAL RECORD-MALFORMED: line 2 REPO'
```

Verdict: **OPPORTUNITY (A1)** — a fourth class that *is* genuinely unasserted by every pre-round
fixture exists and is already discriminated by the delivered fixture's `total-before-rows` case; the
frozen mutant set simply does not include it (it includes the duplicated M13 instead).

### C11 — "four documented record-file behaviours"?

Docstring tokens (`ast.get_docstring` of `tools/souji-worktree-drift.py`, filtered):

```
46:                         that does not match the schema, a duplicated name, or
```

`grep -rn "CRLF\|crlf\|trailing whitespace" tools/ SKILL.md corpus/QUALITY.md` → no hit in `tools/`;
the only CRLF mention in the lane is the r39 SKILL row and the r39 fixture.

Verdict: **PARTIALLY UNSUPPORTED (A2)** — of the four behaviours: `RECORD-OUTSIDE-ROOT` is named in
the docstring; trailing-space refusal and indented-`#` refusal are instances of the documented
"a line that does not match the schema" class; **CRLF acceptance is documented nowhere** — it is an
emergent property of `str.splitlines`. The fixture therefore pins one undocumented artefact as a
contract (a legitimate future hardening to strict `\n` splitting would now fail a gate fixture).

### C12 — duplicate assertions among the two "ordering classes"

`sed -n '183,196p' tests/fixtures/r36-worktree-drift.py`:

```
        # empty
        root, fleet = build(scratch, "empty")
        rec = os.path.join(root, "record.tsv")
        write(rec, "TOTAL\trepos=0\tregs=0\tprunable=0\n")
        rc, out, summary = invoke(tool, fleet, rec)
        check("empty", rc == 2 and "RECORD-EMPTY" in out + summary, "rc=%d" % rc, results)
```

`grep -n 'TOTAL\t' tests/fixtures/r36-worktree-drift.py tests/fixtures/r37-drift-discrimination.py tests/fixtures/r38-drift-record.py tests/fixtures/r38-drift-write-envelope.py`
shows every existing record body puts `TOTAL` last (or alone).

Verdict: **MIXED (A1)** — `comments-total-only` (comment + TOTAL, no REPO row → `RECORD-EMPTY`)
re-asserts r36's `empty` case (TOTAL-only → `RECORD-EMPTY`); `total-before-rows` is a genuinely new
assertion (no existing fixture places TOTAL before REPO rows) but is not backed by any frozen mutant.

### C13 — existing-fixture census (is the matrix complete?)

```
grep -rln "souji-worktree-drift" tests/fixtures/*.py
```

```
tests/fixtures/r36-worktree-drift.py
tests/fixtures/r37-drift-discrimination.py
tests/fixtures/r37-drift-escapes.py
tests/fixtures/r37-drift-mutants.py
tests/fixtures/r38-drift-mutants.py
tests/fixtures/r38-drift-record.py
tests/fixtures/r38-drift-write-envelope.py
tests/fixtures/r39-drift-record-rules.py
```

Verdict: **PASS (scope)** — five pre-round case fixtures (`r36`, `r37-discrimination`,
`r37-escapes`, `r38-record`, `r38-write-envelope`) plus the candidate; `r37-drift-mutants.py` and
`r38-drift-mutants.py` are mutant *drivers* (they take `--fixture`, not a case arm) and are out of
scope for a "does this fixture kill M13" question, matching `W1ExecC3Baseline.md` §6.

### C14 — is the narrative already corrected?

`ls .ufo/reports/round-39/` → no such directory; `grep -n "M13\|C3" .ufo/reports/round-39/souji.md`
→ no such file.

Verdict: **OPEN (A2)** — no round report exists yet, so the frozen prereg's falsified sentence is
still the only narrative of record. `W1ExecC3Baseline.md` §5 already reported the M13 duplicate;
this seat independently reproduces it and adds the instrument-level and distinctness findings.

## Marginal coverage ledger (exact)

| Candidate case | Pre-round assertion? | Frozen mutant that binds | Marginal class |
|---|---|---|---|
| `good` | yes — every fixture | none | duplicate |
| `trailing-space` | **no** | M11 (only M11) | **new** |
| `total-before-rows` | **no** (new ordering assertion) | none in M11–M14 (M15 would bind) | **new, unmutated** |
| `crlf` | **no** | M12 (only M12) | **new** |
| `outside-root` | **yes** — `r38-drift-write-envelope.py:record-outside-root` | M13 | duplicate |
| `indented-comment` | **no** | M14 (only M14) | **new** |
| `comments-total-only` | **yes** — `r36-worktree-drift.py:empty` (+ r38 `comments-and-blanks`) | none | duplicate |

**Marginal class count = 3 mutant-backed novel classes (M11, M12, M14) + 1 novel unmutated
assertion (`total-before-rows`) = 4 new assertion classes, of which 3 are mutation-killed.**
The claim advertises **4 mutant-backed novel classes**. The overstatement is exactly one mutant
(25 % of the mutant set): M13.

Claim wording verdict, sentence by sentence:

- "Four single-defect mutants of those behaviours survive every existing fixture" (prereg C3) —
  **NOT SUPPORTED**. True for the three fixtures the prereg enumerates (r36, r37, r38-record) and
  for r37-escapes; false for `r38-drift-write-envelope.py`, a base-revision fixture that kills M13
  (C5, C6, C7).
- "four record-rule mutants (M11-M14) that every existing drift fixture leaves alive are killed by
  `tests/fixtures/r39-drift-record-rules.py`" (round goal) — **NOT SUPPORTED**, same evidence.
- "four documented record-file behaviours" (prereg C3, counter docstring) — **PARTIALLY
  UNSUPPORTED**: 1 named in the docstring, 2 instances of the documented schema class, 1 (CRLF)
  documented nowhere (C11).
- Predicate `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6` — **SUPPORTED and
  reproducible** (C1, C2). The defect is in the rationale's quantifier and magnitude, not in the
  counter's arithmetic.

## Findings and smallest safe corrections

**F1 (A2, calibration — must be fixed in the round report).** The C3 rationale's universal quantifier
is falsified by a pre-round fixture. Smallest safe correction: in `.ufo/reports/round-39/souji.md`
and the r39 lesson, state C3 as *three novel record-rule mutants (M11 trailing-space, M12 CRLF, M14
indented-comment) plus one duplicate (M13 outside-root, already killed by
`r38-drift-write-envelope.py:case-record-outside-root` at the base revision)*, and carry the
prereg sentence as an errata line. The prereg itself is frozen and is not to be edited; C1's
routed-defect machinery (R14: a receipt/claim misdescribing its own operation) is exactly the class
this touches, so leaving it uncorrected costs the calibration axis more than the coverage axis gains.

**F2 (A3, instrument — next round, or a tighter-only amendment only if the L1 rules it pre-scoring).**
`c3-counter.py`'s base arm scores a single file (`--base-fixture`, default
`tests/fixtures/r38-drift-record.py`) while the claim quantifies over "every existing drift fixture".
Smallest safe correction: accept a `--base-fixtures` list over the five pre-round case fixtures and
require `base_killed=0` across all of them — M13 then fails the base arm by construction. Second,
pin fixture bytes with `git show <rev>:<fixture>` instead of reading them from the working tree, so
the arm cannot be steered by an uncommitted path (C4).

**F3 (A1, coverage — round 40 unless the L1 rules a pre-scoring amendment).** A genuinely novel
fourth class already exists and the delivered fixture already discriminates it: M15 ("a REPO row
after a TOTAL row is refused") is killed only by `case-total-before-rows` and survives all five
pre-round fixtures (C10). Swapping M13→M15 after `c3-after.txt` was measured is *not* tighter-only;
it belongs in round 40, or in a new prereg amendment if the L1 rules the claim unmeasured — which
C2 contradicts (`c3-after.txt` already exists and reproduces).

**F4 (A2, wording).** "Four documented record-file behaviours" should read "one documented refusal
(`RECORD-OUTSIDE-ROOT`), two instances of the documented schema class, and one undocumented
tolerance (CRLF, `str.splitlines`)" — or CRLF acceptance should be documented in the tool docstring
before a gate fixture pins it.

**F5 (A4, counter docstring).** "M13 the record row's outside-root refusal is removed" is inaccurate:
the gitdir guard survives and still refuses a real work-tree escape (C9). Correct to "M13 the
record row's name-path containment check is removed (the gitdir guard remains)".

**Not a defect.** The four mutants are distinct, single-anchor, crash-free classes (C5, C8); the
before and after receipts are honest and byte-reproducible (C2, C3); `cases=7` clears the frozen
`cases>=6` floor; the mutant anchors occur exactly once at both revisions (`ANCHOR … count=1`).

## Risks / notes for the L1

- The counter reads `--fixture`/`--base-fixture` from the working tree. `git status --porcelain` at
  measurement time showed only untracked `census/round-39/*` files, and
  `sha256sum tests/fixtures/r39-drift-record-rules.py` → `567c37a6…` equals
  `git show HEAD:… | sha256sum`, so the measured fixture is the committed one.
- The `r37-drift-escapes.py` pristine arm reads `control=NO-BASE-TOOL` when driven by the counter
  (it needs `--base-tool`); this is a driver-CLI mismatch, not a survivor, and it matches
  `W1ExecC3Baseline.md` §4. Its `record-escape` case (a *real* work-tree escape) survives M13
  because of the gitdir guard (C9).
- `W1ExecC3Baseline.md` §5 reported F1 before this seat. This seat's additions are: the frozen
  instrument reproducing the kill (C7), the quantifier mismatch in the instrument (C4/C7), the
  partial reach of M13 (C9), and the verified novel replacement M15 (C10).
- **Scratch:** `/fast/scratch/hyaku/souji-r39/W1CritC3Axis` was removed at exit
  (`shutil.rmtree`/`rm -rf`); nothing of this seat remains on disk.
- **Tooling:** nothing installed or upgraded (pacman is paused host-wide; no `uv tool`/`npx` need
  arose).
