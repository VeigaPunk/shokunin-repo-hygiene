# W1RevFreeze — frozen prereg vs instruments (souji round 39, wave 1)

Seat: reviewer. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract read: `census/round-39/preregistration.txt` (brief names freeze commit
`b769bfb84a264d8b284c09bc211d99f39a3e9126`), lane base
`ed30b7f5b77939c9073348d810730bc4f355708d`, lane HEAD at review time
`2201778e7736af82e7d8a42dec2494f115bf3923`.
Scratch: `/fast/scratch/hyaku/souji-r39/W1RevFreeze` (removed at end of seat; see §7).
No tool installs were needed. All git use was read-only; the one fixture repo was
`mktemp -d` + `git init -q` under my scratch with `rev-parse --show-toplevel` asserted.

## 0. Verdict table

| Check | Verdict |
|---|---|
| C1 control `records/c1-before.txt` reproduces at `ed30b7f` | **PASS** — byte-identical |
| C2 control `records/c2-before.txt` reproduces at `ed30b7f` | **FAIL** — 2 lines drift (L5 tuple, `fixture_sha`); SUMMARY top line reproduces |
| C3 control `records/c3-before.txt` reproduces at `ed30b7f` | **FAIL** under the frozen default command; **PASS only** with an unrecorded `--fixture` argument |
| Prereg bytes are frozen at the freeze commit | **FAIL** — Amendment A1 was appended in place after the freeze |
| Every frozen predicate clause has code, every code check has a clause | **FAIL** — 3 clauses with no code, 5 code/clause divergences, 1 falsified premise (§3) |
| Control-receipt SUMMARY parsers match the counters' output format | **PASS** for all three receipts; the frozen **C3** grammar literal `cases>=6` is unprintable and matches nothing |

No fabricated numbers below: every quoted line is pasted from the run that produced it.

## 1. Instrument identity (what the counters actually audited)

```
$ sha256sum census/round-39/c1-items.tsv tests/fixtures/r39-citation-rev.py tests/fixtures/r39-drift-record-rules.py tools/souji-citation-reconcile.py tools/souji-worktree-drift.py   (prefixes)
d892b74f8358  c1-items.tsv
7ab7c3d85a81  tests/fixtures/r39-citation-rev.py
567c37a679f5  tests/fixtures/r39-drift-record-rules.py
59f1e57d7af0  tools/souji-citation-reconcile.py
e48ed08e6728  tools/souji-worktree-drift.py

$ git show ed30b7f:tools/souji-worktree-drift.py | sha256sum        -> 14e9c0f77d7e...
$ git show ed30b7f:tools/souji-citation-reconcile.py | sha256sum    -> 56866ea8f832...

$ for r in b769bfb 2201778; do ... git show $r:tests/fixtures/... | sha256sum ; done
b769bfb rules=567c37a679f5   b769bfb cit=c142c1bc28b8
2201778 rules=567c37a679f5   2201778 cit=7ab7c3d85a81
```

Consequence used repeatedly below: the **candidate C3 fixture is byte-identical at the freeze
commit and at HEAD** (`567c37a679f5`), while the **C2 fixture was rewritten after the freeze**
(`c142c1bc28b8` → `7ab7c3d85a81`).

## 2. The three control receipts at `ed30b7f` (exact reproduction)

All three were run from the lane root (counters open `--items`/fixtures relative to CWD and
`git show` repo-relative paths), `TMPDIR`/`--scratch` inside my scratch, outputs diffed against
the committed receipt with `cmp`.

### 2.1 C1 — `records/c1-before.txt`: PASS, byte-identical

```
$ TMPDIR=$S/c1 python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv \
    --register census/round-39/cells.tsv --scratch $S/c1
rc=1
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
... (16 ITEM lines, all OPEN: 5 FILE-ABSENT, 11 ANCHOR-ABSENT — `grep -c` on the run output)
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358

$ cmp -s $S/c1.out census/round-39/records/c1-before.txt && echo IDENTICAL
IDENTICAL
```

Verdict: the C1 control is reproducible from committed instrument bytes at the base revision;
`open=16` matches the prereg CONTROL clause. `items_sha` proves the items file is unchanged.

### 2.2 C2 — `records/c2-before.txt`: FAIL at leg granularity

```
$ TMPDIR=$S/c2 python3 -B census/round-39/c2-counter.py --root ... --rev ed30b7f... --base-rev ed30b7f... --scratch $S/c2
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=7ab7c3d85a81

$ cmp -s ... ; diff
5c5
< LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
---
> LEG L5 FAIL new=(8, 5, 3, 1) old=(8, 5, 3, 1)
7c7
< SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=7ab7c3d85a81
---
> SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8
```

Cause is fully attributed (not inferred) — the freeze-commit fixture vs the amended one, against
the same base tool bytes:

```
$ python3 -B $S/cit-old.py --tool $S/cit-tool-base.py --work $S/l5old | tail -3     # fixture at b769bfb (c142c1bc28b8)
case-register-rev-gone=PASS
case-register-absent=PASS
SUMMARY cases=8 pass=5 fail=3
$ python3 -B tests/fixtures/r39-citation-rev.py --tool $S/cit-tool-base.py --work $S/l5new | tail -3   # fixture at HEAD (7ab7c3d85a81)
case-register-rev-gone=FAIL rc=2 want=2 missing=['REV-UNRESOLVED'] out='REFUSAL USAGE: register ... is not at 1111111111111111111111111111111111111'
case-register-absent=PASS
SUMMARY cases=8 pass=4 fail=4
$ python3 -B tests/fixtures/r39-citation-rev.py --tool $S/cit-tool-new.py --work $S/l5new | tail -1      # HEAD tool
SUMMARY cases=8 pass=8 fail=0
```

Verdict: the C2 control's **SUMMARY top line** (`legs=6 pass=2 fail=4 harm=0`, `tool_sha`) still
reproduces; its **L5 arm and `fixture_sha` do not**. The receipt is stale with respect to the
fixture amendment (A1), and its recorded sha `c142c1bc28b8` names bytes that no longer exist at
HEAD. `pass=2 fail=4` (the number the prereg CONTROL clause names) is still correct.

### 2.3 C3 — `records/c3-before.txt`: FAIL under the frozen default; PASS only with an unrecorded argument

```
$ TMPDIR=$S/c3 python3 -B census/round-39/c3-counter.py --root ... --rev ed30b7f... --base-rev ed30b7f... --scratch $S/c3
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
rc=0

$ diff $S/c3.out census/round-39/records/c3-before.txt
< MUTANT M11 killed=yes ... (all four killed=yes)
< SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
---
> MUTANT M11 killed=no  ... (all four killed=no)
> SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

The receipt reproduces **only** when the candidate slot is filled with the pre-existing r38
fixture, an argument the receipt does not record:

```
$ python3 -B census/round-39/c3-counter.py --root ... --rev ed30b7f... --base-rev ed30b7f... \
    --fixture tests/fixtures/r38-drift-record.py --scratch $S/c3r
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
$ cmp -s $S/c3r.out census/round-39/records/c3-before.txt && echo IDENTICAL
IDENTICAL

$ sha256sum tests/fixtures/r38-drift-record.py   -> ac0be0e7a49e...
```

Verdict: `records/c3-before.txt` is **not reproducible from the frozen command line**. Its
`fixture_sha=ac0be0e7a49e` is the sha of `tests/fixtures/r38-drift-record.py`, i.e. at control
time the candidate-fixture slot held the base fixture, not `r39-drift-record-rules.py` — which
already existed at the freeze commit with sha `567c37a679f5` and 7 cases. Under the frozen default
the base-revision reading **is the landing reading** (`killed=4 survived=0 cases=7`), so the C3
counter's before/after contrast is not derivable from the predicate's own invocation; it is
derivable only from which fixture is passed. The prereg header's blanket statement ("the counter,
run at the base revision, reads the before-state") is therefore false for C3.

## 3. Frozen predicate ↔ instrument code

Line numbers are from the HEAD working-tree copies of the counters.

### 3.1 C1 (`census/round-39/c1-counter.py`)

| Frozen clause | Code | Verdict |
|---|---|---|
| `SUMMARY items=16 open=0 register_cells>=6 register_mismatches=0 commit_distinct>=2`, exit 0 | `print("SUMMARY items=%d open=%d register_cells=%d ...")` :239; `ok = (open_count == 0 and cells >= args.min_cells and mismatches == 0 and distinct >= args.min_commit_distinct)` :241-246; `return 0 if ok else 1` :247 | MATCH (printed form carries values, floors enforced; actual line adds `items_sha=`) |
| "a single anchored line of a named lane file at `--rev` carrying all its `must` tokens and none of its `mustnot` tokens" | `hits = [l for l in text.split("\n") if row["anchor"] in l]` :212; `good = [... all(has_token(l,t) for t in must) and not any(... mustnot)]` :217-221; `print("ITEM %s CLOSED")` :228 | **DIVERGENCE D1** — "single" is unenforced: any one satisfying line closes the row, a sibling anchored line may carry a forbidden token |
| "each register row verifies through the frozen `tools/souji-citation-reconcile.py` bytes at `--rev`" | `register_leg(...)` :148 — `git_show(root, rev, "tools/souji-citation-reconcile.py")`, run tool, `re.search(r"^SUMMARY cells=(\d+) mismatches=(\d+)$", ...)` | MATCH |
| KILL: "any item reads OPEN at the landing revision" | `open_count` → exit 1 | MATCH |
| KILL: "register leg reports any mismatch or fewer than two rows whose `commit` differs from `receipt_rev`" | `mismatches == 0 and distinct >= 2` | MATCH |
| KILL: "base-revision control (same items, same counter bytes, `--rev ed30b7f`) reads `open=0`" | — no code | **DIVERGENCE D2** — clause with no code; only the receipt enforces it (receipt reads `open=16`, so the clause holds in fact) |
| "committed bytes only (`git show`)" | `git_show` throughout | MATCH |

D1 evidence (probe repo under my scratch, `git rev-parse --show-toplevel` asserted = repo dir):

```
$ printf 'ANCHOR alpha musttok\nANCHOR musttok FORBIDDEN\n' > f.txt ; git -C "$D" add f.txt ; git -C "$D" commit -qm probe
$ printf 'id\tfile\tanchor\tmust\tmustnot\nP1\tf.txt\tANCHOR\tmusttok\tFORBIDDEN\n' > items.tsv
$ python3 -B census/round-39/c1-counter.py --root "$D" --rev "$R" --items items.tsv --register census/round-39/cells.tsv --scratch $S/probe1
ITEM P1 CLOSED
```

`census/round-39/c1-items.tsv` itself asserts the opposite invariant in its header comment
("Line-unique anchors keep the predicate re-derivable") — unenforced by the counter.

### 3.2 C2 (`census/round-39/c2-counter.py`)

| Frozen clause | Code | Verdict |
|---|---|---|
| `SUMMARY legs=6 pass=6 fail=0 harm=0`, exit 0 | :280, `return 0 if passed == len(legs) and harm == 0 else 1` :282 | MATCH |
| L1 "unresolvable `--rev` (base: rc 1 with findings; new: rc 2, `REFUSAL REV-UNRESOLVED`)" | `new_ok = rc==2 and "REV-UNRESOLVED" in stderr`; `old_has = old_p.returncode == 2 and "REV-UNRESOLVED" in old_p.stderr`; `leg("L1", new_ok and not old_has, ...)` :189-191 | **DIVERGENCE D3** — the base arm's "rc 1 with findings" is never checked; a base tool exiting 0 passes. Empirically true but unenforced: base tool at zero rev → `rc=1`, 20 `MISMATCH` lines, `SUMMARY cells=10 mismatches=20` |
| L2 "`--rev` naming a blob (same classes)" | :199-202, same shape (`bool(blob) and new_ok and not old_has`) | **D3** (same base-arm gap) |
| L3 "`--register-rev` unresolvable stays rc 2 (harm)" | :211-213, `harm += 1` on failure | MATCH |
| L4 "docstring's RECORD-MISSING/RECORD-MALFORMED mapping matches the classes the tool actually produces for a missing and an unreadable record (base: differs)" | `docstring_classes` :112-124 (ast, first line per class) + :228-234 | **DIVERGENCE D4** — narrower than the clause: only the line for the *observed* class must contain `missing`/`EACCES`; an inverted pair naming both keywords passes |
| L5 "new fixture passes 8/8 … fails >=2 with the base bytes" | :236-247, `new_f[0] == 8 and new_f[2] == 0 and new_f[3] == 0 and old_f[2] >= 2` | MATCH (verified: `new=(8, 8, 0, 0) old=(8, 4, 4, 1)`) |
| L6 "**six** consumer fixtures stay green" | `CONSUMERS` :54-60 has **5** entries; docstring :19 says "five consumer fixtures"; receipt lists 5 | **DIVERGENCE D5** — frozen clause overstates by one; read literally, the predicate's L6 fails on a passing run |
| KILL "if the base-arm control prints `pass=6`" | — no code | clause with no code (receipt-enforced; receipt prints `pass=2`, so it holds) |
| "both tool revisions extracted from committed bytes (`git show <rev>:tools/...`)" | `extract` :145-152 | MATCH |

### 3.3 C3 (`census/round-39/c3-counter.py`)

| Frozen clause | Code | Verdict |
|---|---|---|
| `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`, exit 0 | :179 prints `... base_killed=%d cases=%d tool_sha=... fixture_sha=...`; floor folded into `pristine_ok` via `cases >= 6` :156 | **DIVERGENCE D6** — the frozen grammar literal `cases>=6` can never appear in output; a parser keyed on the frozen line fails. The counter's own docstring repeats the same unprintable literal (:26) |
| M11 trailing-space tolerance; M12 CRLF splitting broken; M13 outside-root guard removed; M14 indented `#` accepted | `MUTANTS` :50-58 | MATCH to the claim text (verified by four kills) |
| "the candidate fixture is `tests/fixtures/r39-drift-record-rules.py` and the base fixture is `tests/fixtures/r38-drift-record.py` **at `--rev`**" | `candidate_src = open(args.fixture, ...)` :123; `base_src = open(args.base_fixture, ...)` :124 — **worktree reads, never `git show`** | **DIVERGENCE D7** — the "at `--rev`" clause has no code; the frozen candidate fixture does not exist at the base revision (`git cat-file -e ed30b7f:tests/fixtures/r39-drift-record-rules.py` → absent), so an honest rev read would make the base control exit 2 |
| KILL: survivor / `base_killed != 0` / pristine failure / `<6` cases | `killed_n == len(results) and base_n == 0`; pristine block :141-160 | MATCH (folded) |
| "a kill needs the fixture's own `fail>0`, no traceback, exit 1" | `killed = proc.returncode == 1 and fails > 0 and not crash` :102 | MATCH |
| Docstring "Exit: … 2 usage / could-not-evaluate input" (:26-27) | :123-124 read before any `except`; `if source is None: ... "tool or fixture absent at %s"` :125-127 | **DIVERGENCE D8** — absent `--fixture` raises `FileNotFoundError` (traceback, rc 1), and the message names a fixture the code never reads at `--rev` |
| Premise: "Four single-defect mutants of those behaviours survive **every existing fixture**" | `--base-fixture` defaults to one fixture only | **FALSIFIED, D9** — see §4 F4 |

D8 evidence:

```
$ python3 -B census/round-39/c3-counter.py --root ... --rev ed30b7f... --base-rev ed30b7f... \
    --fixture $S/absent-fixture.py --scratch $S/probe2
Traceback (most recent call last):
  File ".../census/round-39/c3-counter.py", line 123, in main
    candidate_src = open(args.fixture, encoding="utf-8").read()
FileNotFoundError: [Errno 2] No such file or directory: '.../absent-fixture.py'
rc=1
```

(`c2-counter.py` :170 has the same shape for its fixture read — before its `try`, so its documented
exit 2 is also unreachable for a missing fixture. Cited, not run: `c2` hardcodes the fixture path.)

## 4. Findings by severity

**F1 (blocker, C3 calibration).** `census/round-39/records/c3-before.txt` records a reading its own
frozen command cannot produce. Frozen default at `ed30b7f` reads
`SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 ... fixture_sha=567c37a679f5`
(identical numbers to the landing arm); the receipt's `killed=0 survived=4 cases=10
fixture_sha=ac0be0e7a49e` is reachable only with `--fixture tests/fixtures/r38-drift-record.py`,
which the receipt does not state. Evidence: §2.3 (`IDENTICAL` only for the substituted run) and
`sha256sum tests/fixtures/r38-drift-record.py = ac0be0e7a49e`. Consequence: C3's do-nothing control
is not the do-nothing state of this instrument, and "the counter at the base revision reads the
before-state" (prereg header) is false for C3.

**F2 (blocker, C2 calibration).** `census/round-39/records/c2-before.txt` no longer reproduces:
`LEG L5 ... new=(8, 5, 3, 1) old=(8, 5, 3, 1)` / `fixture_sha=c142c1bc28b8` vs current
`new=(8, 4, 4, 1) old=(8, 4, 4, 1)` / `fixture_sha=7ab7c3d85a81`. The delta is exactly the A1 case
class (frozen fixture → `pass=5 fail=3`; amended fixture → `pass=4 fail=4`). The receipt was not
re-taken after the amendment it is superseded by.

**F3 (blocker, freeze integrity).** The prereg is not byte-frozen at the named freeze commit:

```
$ git diff b769bfb -- census/round-39/preregistration.txt
@@ -112,3 +112,12 @@
+## Amendment A1 — r39-citation-rev case class (2026-10-28, tighter-only, before any claim measurement)
+... (9 added lines)
```

Freeze-commit sha `2aa70573eae6…` vs HEAD `b063950d1451…`. A1's "before any claim measurement" is
contradicted by F2: the control measurement it invalidates (L5 `fail=3`, sha `c142c1bc28b8`)
precedes it. A1's own narrower claims hold — case count is still 8, the amended case now expects
`REV-UNRESOLVED`, and the base arm still prints `not at` (verified in §2.2). The defect is the
in-place rewrite of the contract, which is the R8/R9 class this round claims to close.

**F4 (major, C3 premise falsified).** "Four single-defect mutants … survive every existing fixture"
is false for M13. `tests/fixtures/r38-drift-write-envelope.py` (sha `d6fed4af1e8a`, unchanged since
r38 commit `4bda5f6`, present at the base revision) already asserts the outside-root refusal
(lines 260-264, `check("record-outside-root", ... has_token(out, "RECORD-OUTSIDE-ROOT"))`) and kills
M13 at the base tool:

```
$ python3 -B census/round-39/c3-counter.py --root ... --rev ed30b7f... --base-rev ed30b7f... \
    --fixture tests/fixtures/r38-drift-write-envelope.py --scratch $S/r38-drift-write-envelope
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=1 survived=3 pristine=ok base_killed=0 cases=12 ... fixture_sha=d6fed4af1e8a
```

Control for the narrow claim: `r38-drift-record.py` and `r36-worktree-drift.py` do leave all four
alive (`SUMMARY ... killed=0 survived=4 ... cases=10` and `... cases=12`, both
`fixture_sha=ac0be0e7a49e` / `6b35f54a426f`). So the prereg's narrower sentence ("its fixture and
the r36/r37 fixtures assert nothing about four documented record-file behaviours") is true; the
universal sentence is not. The counter cannot see this because `base_killed` is computed against a
single named base fixture.

**F5 (major, C2 L6 count).** Frozen "six consumer fixtures" vs `CONSUMERS` (5) and docstring
"five consumer fixtures". A literal reading of the frozen predicate fails on a green run.

**F6 (major, C1 single-line clause).** "a single anchored line" is not enforced (§3.1 D1 probe:
`ITEM P1 CLOSED` while a second anchored line carries the `mustnot` token). The items file's own
"line-unique anchors" invariant is a comment, not a check.

**F7 (major, C3 rev clause).** The frozen "fixtures … at `--rev`" is not implemented; both fixtures
are read from the worktree, and the candidate fixture does not exist at the base revision, so the
clause as written is unsatisfiable for the control arm.

**F8 (minor, C1 register floor is non-discriminating).** `census/round-39/make-cells.py` writes
`commit = args.commit` and `receipt_rev = late|freeze` on all six rows, so `commit != receipt_rev`
holds for every row by construction whenever `--commit` differs from those two revs. The
`commit_distinct>=2` arm cannot fail while the generator is used as specified, so it does not
measure the register's revision discrimination — it measures the argument plumbing. Related: the
register is absent at HEAD (`git cat-file -e 2201778:census/round-39/cells.tsv` → absent), so C1's
after-arm is currently unreachable (`REGISTER-ABSENT` → `cells=0` → exit 1).

**F9 (minor, floor override).** `--min-cells`/`--min-commit-distinct` (:257-258) let a caller lower
the frozen floors; the frozen command line does not pass them, so defaults apply today, but the
floor is not hard-wired.

**F10 (minor, exit classes).** C3's documented exit 2 for could-not-evaluate input is unreachable
for an absent fixture (traceback, rc 1, §3.3 D8); C2's fixture read has the same shape (:170).

**F11 (minor, summary grammar).** C3's frozen `cases>=6` is a comparison, not a printed field
(`cases=%d`, floor checked separately). Brief, prereg and code name three different grammars: the
brief's restatement drops `cases>=6` entirely, the prereg prints it, the counter prints `cases=7`.

## 5. What the instruments do satisfy (positive controls)

```
$ python3 -B census/round-39/c2-counter.py --root ... --rev 2201778... --base-rev ed30b7f...
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc=0

$ python3 -B census/round-39/c3-counter.py --root ... --rev 2201778... --base-rev ed30b7f...
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

Both numeric predicates are reachable at the landing revision (C2 `pass=6 fail=0 harm=0`; C3
`killed=4 survived=0 base_killed=0`, `cases=7 >= 6`). C3's numbers are identical at base and
landing, which is F1 restated: the discrimination lives in the fixture bytes, not the tool bytes.

## 6. SUMMARY parser ↔ output-format check

All three counters' parsers were run against the real producer lines:

```
c1 register parser on reconciler line: ('10', '20')          # re ^SUMMARY cells=(\d+) mismatches=(\d+)$ vs real "SUMMARY cells=10 mismatches=20"
SUMMARY cases=8 pass=4 fail=4 -> ('8', '4', '4')
SUMMARY cases=7 pass=7 fail=0 -> ('7', '7', '0')
SUMMARY cases=10 pass=10 fail=0 -> ('10', '10', '0')
c1-before | SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
c2-before | SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8
c3-before | SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

Verdict: each receipt's field names/order match its counter's `print` format exactly
(c1 :239, c2 :280, c3 :179), and the counters' regexes parse the real producer output — no parser
mismatch. The single format defect is the frozen C3 grammar literal `cases>=6` (F11/D6), which no
parser and no counter can ever emit.

## 7. Residual risk and verification gaps

- I did not run C1's landing arm: the register `census/round-39/cells.tsv` is absent at HEAD, so
  `register_cells>=6` and `commit_distinct>=2` are unverified in fact (only their code path is).
  F8's "by construction" reading of `commit_distinct` is a code-reading finding, not a measurement.
- F4 shows M13 is already covered; the other three mutants' "survive every existing fixture" status
  was checked against the drift fixtures the counter can drive (`r38-drift-record`,
  `r36-worktree-drift`, `r38-drift-write-envelope`). `r38-drift-mutants.py` is the battery, not a
  `--tool` fixture, and refuses that interface (`SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL
  base_killed=0 cases=0`), so it is outside this check.
- The C2 base-arm "findings" clause (D3) is verified empirically once (zero rev, 20 MISMATCH lines);
  the blob arm (L2) was not independently re-run for findings text.
- Scratch `/fast/scratch/hyaku/souji-r39/W1RevFreeze` was removed at the end of this seat; the
  probe fixture repo lived under it and is gone with it.

## 8. Recommended repairs (advisory; the L1 integrates)

1. Re-take `c3-before.txt` with the frozen default command and record the `--fixture`/`--base-fixture`
   arguments in the receipt; or state the control as "base fixture `r38-drift-record.py` as candidate"
   and keep `killed=4` at base out of the claim's before-state.
2. Re-take `c2-before.txt` after A1 (expect `L5 ... new=(8, 4, 4, 1) old=(8, 4, 4, 1)`,
   `fixture_sha=7ab7c3d85a81`), or supersede the receipt by an explicit amendment row.
3. Replace A1's in-place append with a supersession note that names the receipt it invalidates
   (freeze-commit bytes stay untouched; the amendment is a new file or a ledger row).
4. Narrow the C3 premise from "every existing fixture" to the named fixtures, or add the envelope
   fixture to the mutant-scoring set so `base_killed` measures the real pre-existing coverage.
5. Fix the C3 grammar to `cases=%d` plus a stated `>=6` floor in the predicate text, and make the
   C2 L6 clause say five (or add the sixth consumer).
6. Enforce the C1 "single anchored line" invariant (anchor count == 1) and hard-wire the register
   floors.
