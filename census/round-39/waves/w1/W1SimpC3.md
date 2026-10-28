# W1SimpC3 — YAGNI review: `census/round-39/c3-counter.py` vs `tests/fixtures/r38-drift-mutants.py`

seat: simplifier (leaf, advisory — no lane bytes written, no git/jj mutation)
round 39 wave 1, item W1SimpC3
lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (`$L` below)
state read: base `ed30b7f5b77939c9073348d810730bc4f355708d`, freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
HEAD `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` (worktree clean except untracked `census/round-39/make-cells.py`
and four untracked `census/round-39/records/*.txt`)
scratch: `/fast/scratch/hyaku/souji-r39/W1SimpC3` (`$S` below) — removed at the end of this seat.

write scope: this seat wrote exactly one file — this report. `git -C $L status --short` at the end of the
seat reads ` M LOG.md`, ` M SKILL.md`, ` M corpus/QUALITY.md` plus the five pre-existing untracked
`census/round-39/` entries; none of those three edits is mine (they appeared mid-seat from sibling seats),
and no tracked byte I touched exists outside this report.

## Axes (named before measuring)

- **calibration** — does the counter's own bytes decide the claim it is the predicate for?
- **operability** — does the frozen command run from the documented start directory, refuse with the
  documented class, and honour its documented flags?
- **coverage** — do the two mutant batteries measure disjoint defects, or one defect twice?

Move kept only if it improves one axis and harms none.

## Checks run

`L=/home/vgpnk/Projects/shokunin/souji-shokunin`; `S=/fast/scratch/hyaku/souji-r39/W1SimpC3`;
`SNAP=d4c17557b92fd98044e4c8f0ddc79c6d75701b15`; `BASE=ed30b7f5b77939c9073348d810730bc4f355708d`.

### 1. Overlap size (harness vs contract)

```
$ wc -l $L/census/round-39/c3-counter.py $L/tests/fixtures/r38-drift-mutants.py $L/tests/fixtures/r37-drift-mutants.py
  188 …/census/round-39/c3-counter.py
  132 …/tests/fixtures/r38-drift-mutants.py
  106 …/tests/fixtures/r37-drift-mutants.py
$ grep -Fxf $L/census/round-39/c3-counter.py $L/tests/fixtures/r38-drift-mutants.py | wc -l
56
$ grep -Fxf $L/census/round-39/c3-counter.py $L/tests/fixtures/r38-drift-mutants.py | grep -vE '^\s*$|^import |^from ' | wc -l
35
```

35 non-import lines are byte-identical (mutant loop, `score()` body, pristine `subprocess.run` shape,
scratch/`rmtree` teardown, `__main__`). **Verdict: duplication is real and harness-shaped — ~19 % of the
188-line counter, and a third copy of the same shape already exists in `r37-drift-mutants.py`.**

### 2. Functional overlap (do the batteries measure the same defects?)

```
$ git -C $L show $BASE:tools/souji-worktree-drift.py > $S/tool-base.py   # sha 14e9c0f77d7e
$ cd $L && TMPDIR=$S/d python3 -B tests/fixtures/r38-drift-mutants.py \
    --tool $S/tool-base.py --fixture $L/tests/fixtures/r39-drift-record-rules.py \
    --base-fixture $L/tests/fixtures/r38-drift-record.py --work $S/d
MUTANT M7 killed=no base_killed=yes rc=0 fails=0 crash=False base:rc=1 fails=1 crash=False
MUTANT M8 killed=no base_killed=yes rc=0 fails=0 crash=False base:rc=1 fails=1 crash=False
MUTANT M9 killed=no base_killed=yes rc=0 fails=0 crash=False base:rc=1 fails=1 crash=False
MUTANT M10 killed=no base_killed=yes rc=0 fails=0 crash=False base:rc=1 fails=1 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=4
rc=1
```

The r39 fixture leaves all four r38 mutants alive, and the r38 record fixture kills all four. **Verdict:
zero functional overlap — M7-M10 and M11-M14 share no anchor, no rule and no fixture.** The overlap is
the *harness*, not the coverage.

### 3. The reading to preserve: base arm with the r38 fixture

```
$ cd $L && TMPDIR=$S/b python3 -B census/round-39/c3-counter.py --root $L --rev $SNAP --base-rev $BASE --scratch $S/b
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

and at the base revision (same command with `--rev $BASE`):

```
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
rc=0
```

**Verdict: the reading this review must preserve holds — with the r38 fixture as scorer, 0 of 4 killed,
4 survived (`base_killed=no` on every mutant), at both `--rev $SNAP` and `--rev $BASE`.** See finding F2
for the *other* half of that base run, which does **not** hold.

### 4. Pristine strictness: what parameterising into the r38 battery would lose

```
$ cat $S/f/fake-fixture.py
import sys
print("SUMMARY cases=9 pass=1 fail=0")
sys.exit(0)
$ cd $L && TMPDIR=$S/f python3 -B tests/fixtures/r38-drift-mutants.py \
    --tool $S/tool-base.py --fixture $S/f/fake-fixture.py --work $S/f
MUTANT M7 killed=no rc=0 fails=0 crash=False
…
SUMMARY mutants=4 killed=0 survived=4 pristine=ok
r38-battery rc=1
$ cd $L && TMPDIR=$S/f python3 -B census/round-39/c3-counter.py --root $L --rev $BASE --base-rev $BASE \
    --fixture $S/f/fake-fixture.py --scratch $S/f
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=9
c3 rc=1
```

A degenerate fixture that passes 1 of 9 cases scores `pristine=ok` in the r38 battery (its rule is the
substring `fail=0`) and `pristine=FAIL` in c3 (its rule is `pass==cases and cases>=6`).
**Verdict: parameterising loses the strict pristine rule unless the r38 battery is strengthened.**

### 5. Exit status: `base_killed` does not gate the r38 battery

```
$ cd $L && TMPDIR=$S/j python3 -B tests/fixtures/r38-drift-mutants.py --tool $S/tool-base.py \
    --fixture $L/tests/fixtures/r38-drift-record.py --base-fixture $L/tests/fixtures/r38-drift-record.py --work $S/j
MUTANT M7 killed=yes base_killed=yes …
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=4
base-kills-ignored rc=0
```

`r38-drift-mutants.py` returns `0 if pristine_ok and killed_n == len(results) else 1` — `base_n` is
printed, never scored. C3's kill rule requires `base_killed=0`. **Verdict: a wrapper would have to
re-impose the base-kill gate that the r38 battery deliberately does not enforce.**

### 6. Frozen command from the documented start directory

```
$ cd /home/vgpnk/Projects/shokunin && TMPDIR=$S/a python3 -B $L/census/round-39/c3-counter.py \
    --root $L --rev $SNAP --base-rev $BASE --scratch $S/a
Traceback (most recent call last):
  File "…/census/round-39/c3-counter.py", line 124, in main
    candidate_src = open(args.fixture, encoding="utf-8").read()
FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/r39-drift-record-rules.py'
rc=1
```

**Verdict: FAIL.** The prereg's frozen predicate is `python3 -B census/round-39/c3-counter.py --root <lane> …`
and every seat starts in the fleet root; `--fixture`/`--base-fixture` are opened as bare relative paths,
so the predicate dies before scoring. `c2-counter.py` already owns the round's convention —
`lane_root_of()` returns `os.path.abspath(args.root)` and joins instrument paths onto it
(`census/round-39/c2-counter.py:63-65,170`). The docstring also promises exit 2 for "could-not-evaluate
input"; an unreadable fixture exits 1 with a traceback (R10-class docstring/behaviour mismatch, inside
C2's own defect family).

### 7. `--base-rev` is dead input

```
$ cd $L; for b in $BASE b769bfb84a264d8b284c09bc211d99f39a3e9126; do
    TMPDIR=$S/g python3 -B census/round-39/c3-counter.py --root $L --rev $SNAP --base-rev $b --scratch $S/g > $S/g/out-${b:0:7}.txt; done
$ diff $S/g/out-ed30b7f.txt $S/g/out-b769bfb.txt && echo IDENTICAL
IDENTICAL
```

`grep -n 'base_rev\|base-rev' census/round-39/c3-counter.py` → lines 23 (docstring), 110 (argparse),
116 (resolvability check only). **Verdict: the flag is validated and then never read; the counter measures
no base arm at `--base-rev`.** The only base arm it measures is `base_killed` (the r38 fixture against the
same mutant), which is independent of `--base-rev`.

### 8. The frozen control receipt does not reproduce

```
$ cd $L && TMPDIR=$S/c python3 -B census/round-39/c3-counter.py --root $L --rev $BASE --base-rev $BASE --scratch $S/c
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
…
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
rc=0
$ cat census/round-39/records/c3-before.txt
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

Same tool bytes (`14e9c0f77d7e`), different fixture: the receipt names `ac0be0e7a49e` / 10 cases, the
committed fixture is `567c37a679f5` / 7 cases.

```
$ git -C $L log --format='%h %s' -- tests/fixtures/r39-drift-record-rules.py
b769bfb round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
$ git -C $L show b769bfb…:tests/fixtures/r39-drift-record-rules.py | sha256sum | cut -c1-12
567c37a679f5
$ git -C $L show b769bfb…:census/round-39/records/c3-before.txt | tail -1
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
```

**Verdict: FAIL (calibration).** The freeze commit carries a control receipt whose `fixture_sha` names a
fixture revision that exists in no commit (the fixture has exactly one committed version, at the freeze
commit itself). With the committed fixture the counter at `--rev $BASE` prints `killed=4 survived=0` — the
C3 predicate is reachable by the do-nothing state, exactly the shape C2's kill rule forbids for its own
counter (`if the base-arm control prints pass=6`). This is the r38 R8/R9 class (stale receipt bytes)
recurring inside the r39 freeze.

### 9. Weight-only deletions, verified in a scratch copy

`$S/patched-c3.py` = the counter with (D1) the unused third element of `score()`'s return deleted
(`return killed, detail, cases` → `return killed, detail`; both call sites unpacked `_` and discarded it)
and (D3) fixtures resolved against `--root` (`open(os.path.join(os.path.abspath(args.root), args.fixture))`,
the `c2-counter.py` convention). 188 → 189 lines.

```
$ cd /home/vgpnk/Projects/shokunin && TMPDIR=$S/h python3 -B $S/patched-c3.py --root $L --rev $SNAP --base-rev $BASE --scratch $S/h
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
patched-from-fleet-root rc=0
$ … --rev 0000…0000 …
REFUSAL COULD-NOT-EVALUATE: --rev 0000000000000000000000000000000000000000 does not resolve
unresolvable-rev rc=2
$ … --fixture $S/f/fake-fixture.py …
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=9
fake-fixture rc=1
$ … --rev $BASE --base-rev $BASE …
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
patched-base rc=0
```

**Verdict: both moves are behaviour-preserving (identical SUMMARY and per-mutant lines at HEAD and at
base; refusal and pristine paths unchanged) and D3 fixes check 6.** D1 is a dead-interface deletion; D3 is
a one-line alignment with an existing convention, not a new one.

### 10. `GIT_ENV` triplication (measured, not recommended)

```
$ python3 - (ast) GIT_ENV comparison
c2==c3: True
c1 present: True
```

Three byte-identical `GIT_ENV` dicts in the round's three counters. A shared module would make each frozen
predicate's meaning depend on a fourth file the predicate does not name; three eight-line constants are
cheaper than that. **Verdict: leave it; revisit only if a fourth copy appears.**

## Option A — make the r39 battery a parameterised call to the r38 battery

One mechanism: `tests/fixtures/r38-drift-mutants.py` grows `--mutants SPEC` (a JSON file of
`[[id, anchor, replacement], …]`) and the counter passes `census/round-39/c3-mutants.json`. To make that
call carry C3's contract it would additionally need:

1. `--min-cases 6` and `pass==cases` in the pristine rule (today: substring `fail=0`, check 4);
2. `base_killed` in the exit status (today: informational only, check 5);
3. `--env`/`--tmpdir` for the fixture children (today it passes no `env=`, so the ambient `HOME` and git
   config leak in; c3 pins `GIT_ENV` + `TMPDIR=scratch`);
4. a `cases=` field in its SUMMARY (it prints none; C3's predicate needs `cases>=6`);
5. tool bytes by revision, or a scratch tool path plus the wrapper owning `tool_sha` (the battery reads a
   path and has no revision identity);
6. a resolution for `--base-fixture`'s role collision — in the r38 battery it means the r37 discrimination
   fixture (docstring), in C3 it means `r38-drift-record.py`.

Net: c3 loses ~50 lines of harness and keeps refusal + rev extraction + SUMMARY re-emission; the r38
battery gains ~30 lines and four options; one new data format is introduced.

## What would be lost

- **Kill-rule provenance.** The frozen predicate is `python3 -B census/round-39/c3-counter.py …`. Today
  `mutants=4` is decidable from that file's bytes; with a spec file the mutant set lives outside the
  predicate, and each mutant's tie to a documented record behaviour (M11↔trailing whitespace, M12↔CRLF,
  M13↔outside-root, M14↔indented comment) becomes an unvalidated data comment. r37 and r38 express
  mutants as tuple literals; the spec file is a second convention, which this seat must not create.
- **Per-mutant base arm, in the form the claim needs.** `base_killed` would ride a flag whose meaning
  changes by round (item 6) and would still not gate the exit (item 5) — the wrapper would re-derive and
  re-gate it, so the parameterisation buys only the loop, not the arm.
- **Pristine strictness** (check 4): a 1-of-9 fixture would score `pristine=ok`.
- **Env/scratch isolation** for fixture children (item 3), which the round's scratch rule depends on.
- **Revision provenance in one place**: `tool_sha`/`fixture_sha` and the `--rev` binding would split across
  a fixture and a counter, and the drift in F2 was only visible because both shas sit in one SUMMARY line.

## Recommendation

**Option B — keep `census/round-39/c3-counter.py` as its own script.** The two batteries share a harness
shape, not a contract: zero shared mutants, opposite fixture kills (checks 2 and 3), four divergent
semantics (rev resolution, pristine strictness, env isolation, exit gating), and the frozen predicate is
decided by the counter's own bytes. Parameterising would delete ~50 lines, add ~30 + a data format, and
cost the decidability of `mutants=4`.

Cheap moves to keep (both verified in check 9, both improve operability, neither adds a convention):

- **D3 (recommended for landing):** resolve `--fixture`/`--base-fixture` against `--root`, matching
  `c2-counter.py:63-65,170`. Fixes the frozen command failing from the fleet root (+1 line).
- **D1 (optional):** drop `score()`'s unused `cases` return (dead interface; identical output).

**Preserved reading, stated as the acceptance asks: at base, with the r38 fixture as scorer, `killed=0
survived=4` — `base_killed=no` on M11, M12, M13, M14 at both `--rev $SNAP` and `--rev $BASE` (check 3).**
Option B preserves it by construction; Option A preserves it only after items 1-6 are added, and only if
the r38 battery's base arm is made to gate its exit.

## Findings the L1 must decide (outside this seat's edit scope)

- **F1 — `--base-rev` is dead input** (check 7): the frozen predicate passes a flag the counter never
  reads. Either make it the base arm it was receipted as, or amend the predicate to drop it. Note that
  making it real will *fail* today: at `--rev $BASE` the candidate fixture already kills all four
  mutants, so `killed=0 at base` is not reachable with the committed fixture.
- **F2 — `c3-before.txt` is unreproducible and the C3 predicate is do-nothing-reachable** (check 8):
  receipt `fixture_sha=ac0be0e7a49e cases=10`; committed fixture `567c37a679f5 cases=7`; at `--rev $BASE`
  the counter prints the frozen predicate line verbatim and exits 0. A tighter-only amendment
  (re-capture the control against the committed fixture, or make the control the r38-fixture arm
  `base_killed=0`) is required before the C3 after-reading can be said to discriminate.
- **F3 — fixture paths and the documented exit-2 class** (check 6): R10-class docstring/behaviour
  mismatch in the counter itself; D3 fixes the path half.

## Not claimed

- I did not edit, stage or commit any lane byte; D1/D3 exist only in `$S/patched-c3.py` (removed with the
  scratch). The L1 integrates.
- I did not re-run C1 or C2, or any r36/r37 fixture, beyond what checks 2-5 and 9 quote.
- I did not judge the C3 coverage claim itself (whether four mutants are enough) — only the battery's
  shape, its overlap with the r38 battery, and the reproducibility of its control.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1SimpC3` was created for this seat and removed before this report was
finalised (`rm -rf -- "$S"`); nothing of this seat's remains on disk.
