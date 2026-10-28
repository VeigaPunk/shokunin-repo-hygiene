# W1ConnCoverage — mutation-coverage map across the drift fixtures (souji r39, wave 1)

Seat: connector. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (base `ed30b7f5b77939c9073348d810730bc4f355708d`,
measured at HEAD `2201778e7736af82e7d8a42dec2494f115bf3923`).
Scratch: `/fast/scratch/hyaku/souji-r39/W1ConnCoverage` (removed at end of seat; see §10).
No commit, no push, no mutating git/jj. Read-only git only (`status`, `show`, `rev-parse`).

## 0. Byte binding (the matrix measures committed bytes, not a dirty tree)

```
$ git status --porcelain tools/souji-worktree-drift.py tests/fixtures/r39-drift-record-rules.py \
    tests/fixtures/r38-drift-record.py tests/fixtures/r36-worktree-drift.py \
    tests/fixtures/r37-drift-discrimination.py census/round-39/c3-counter.py
(no output — all six paths clean)
$ sha256sum tools/souji-worktree-drift.py tests/fixtures/r39-drift-record-rules.py | cut -c1-12
e48ed08e6728
567c37a679f5
$ git show HEAD:tools/souji-worktree-drift.py | sha256sum | cut -c1-12
e48ed08e6728
$ git show HEAD:tests/fixtures/r39-drift-record-rules.py | sha256sum | cut -c1-12
567c37a679f5
```

The same two digests are what `census/round-39/c3-counter.py` prints as `tool_sha=e48ed08e6728
fixture_sha=567c37a679f5` (§8), so the matrix and the frozen counter audited identical bytes.

**Verdict:** PASS — worktree bytes == HEAD bytes for every measured file.

## 1. Method

Mutant definitions were *loaded from the frozen sources*, not re-typed, so the matrix scores the
same mutations the batteries score:

- M7–M10 — `tests/fixtures/r38-drift-mutants.py` `MUTANTS`
- M11–M14 — `census/round-39/c3-counter.py` `MUTANTS`

Scoring contract is the r38 A5 one both batteries use: a **kill** needs `rc==1` and the fixture's
own `SUMMARY cases=... fail>0` and no `Traceback` on either stream; a fixture is **pristine-ok**
when `rc==0` and `fail=0`.

Harness (`/fast/scratch/hyaku/souji-r39/W1ConnCoverage/matrix.py`) writes one tool variant per
mutant into scratch and runs every fixture × every variant in its own `--work` dir.

```
$ cd /fast/scratch/hyaku/souji-r39/W1ConnCoverage && \
  TMPDIR=/fast/scratch/hyaku/souji-r39/W1ConnCoverage python3 -B matrix.py
anchors M7=1 M8=1 M9=1 M10=1 M11=1 M12=1 M13=1 M14=1
```

**Verdict:** PASS — every one of the eight anchors occurs exactly once in
`tools/souji-worktree-drift.py`, so no mutant is a battery defect (an anchor count ≠ 1 would have
been scored `ALIVE` and void the row).

## 2. Pristine control (each fixture, unmutated tool)

| fixture | rc | SUMMARY | cases |
|---|---|---|---|
| `r36-worktree-drift.py` | 0 | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | 12 |
| `r37-drift-discrimination.py` | 0 | `SUMMARY cases=6 pass=6 fail=0` | 6 |
| `r38-drift-record.py` | 0 | `SUMMARY cases=10 pass=10 fail=0` | 10 |
| `r39-drift-record-rules.py` | 0 | `SUMMARY cases=7 pass=7 fail=0` | 7 |

**Verdict:** PASS — all four fixtures are green on the unmutated tool; every kill below is
therefore attributable to the mutant, not to a pre-broken fixture. r36's `control=STUB-REJECTED`
confirms its anti-stub leg also passed.

## 3. Killer matrix (measured)

```
=== KILLER MATRIX (rows=mutant, cols=fixture; K=kill, . = alive) ===
mutant r36  r37  r38  r39
M7     K    .    K    .
M8     .    .    K    .
M9     .    .    K    .
M10    .    .    K    .
M11    .    .    .    K
M12    .    .    .    K
M13    .    .    .    K
M14    .    .    .    K
```

Per-kill evidence, quoted from the same run (each kill is exactly one failing case):

```
[r36] M7   KILL  rc=1 fails=1 ... failing=case-total-mismatch=FAIL
[r38] M7   KILL  rc=1 fails=1 ... failing=case-total-repos-mismatch=FAIL
[r38] M8   KILL  rc=1 fails=1 ... failing=case-total-regs-mismatch=FAIL
[r38] M9   KILL  rc=1 fails=1 ... failing=case-total-prunable-mismatch=FAIL
[r38] M10  KILL  rc=1 fails=1 ... failing=case-duplicate-name=FAIL
[r39] M11  KILL  rc=1 fails=1 ... failing=case-trailing-space=FAIL
[r39] M12  KILL  rc=1 fails=1 ... failing=case-crlf=FAIL
[r39] M13  KILL  rc=1 fails=1 ... failing=case-outside-root=FAIL
[r39] M14  KILL  rc=1 fails=1 ... failing=case-indented-comment=FAIL
```

**Verdict:** PASS (coverage map complete) — 8 mutants × 4 fixtures = 32 scored runs, 9 kills, 0
`NO-SUMMARY`, 0 crashes.

## 4. Redundancy: which mutants are killed by more than one fixture

```
M7     killers=2 REDUNDANT        r36,r38
M8     killers=1 unique           r38
M9     killers=1 unique           r38
M10    killers=1 unique           r38
M11    killers=1 unique           r39
M12    killers=1 unique           r39
M13    killers=1 unique           r39
M14    killers=1 unique           r39
```

**M7 is the only redundant mutant, and the redundancy is partial, not duplicate.** r36's
`total-mismatch` case writes `record(root, [("alpha",1,0),("beta",1,0)], total=(3,2,0))`
(`tests/fixtures/r36-worktree-drift.py:182-186`) — `repos=3` against 2 rows while `regs=2` and
`prunable=0` are *consistent*. So r36 exercises only the **repos** arm of the three TOTAL sums;
M8 (regs) and M9 (prunable) are r38-unique. Losing r36 would cost M7 one of its two killers but no
coverage; losing r38 would lose M8/M9/M10 outright and demote M7 to r36-only.

`r37-drift-discrimination.py` kills **none** of the eight (0/8): it discriminates live-measurement
behaviour (REGS/PRUNABLE/ABSENT/UNRECORDED/UNREACHABLE) and never asserts a record-rule refusal.
It is correctly excluded from record-rule coverage claims.

## 5. Gaps: mutants killed by none

```
M7..M14  GAP-NONE
```

**Verdict:** PASS — no mutant in M7–M14 is left alive by the union of the four fixtures, so the C3
`survived=0` reading is not an artefact of a narrow counter: an independent harness over a wider
fixture set agrees.

One real gap exists *outside* the frozen battery, and it is a documented refusal class rather than a
hypothetical (§7).

## 6. Marginal contribution of the new fixture `r39-drift-record-rules.py`

```
M7     pre-r39_killers=r36,r38 r39_kills=False marginal=none
M8     pre-r39_killers=r38     r39_kills=False marginal=none
M9     pre-r39_killers=r38     r39_kills=False marginal=none
M10    pre-r39_killers=r38     r39_kills=False marginal=none
M11    pre-r39_killers=-       r39_kills=True  marginal=YES
M12    pre-r39_killers=-       r39_kills=True  marginal=YES
M13    pre-r39_killers=-       r39_kills=True  marginal=YES
M14    pre-r39_killers=-       r39_kills=True  marginal=YES
```

- **Disjoint from r38, not a superset.** No mutant is killed by both r38 and r39 (matrix column
  intersection is empty), and r39 kills none of M7–M10. The two fixtures partition the eight rules;
  neither can be retired against the other.
- **Exactly 4 of 8 kills are marginal**, and each is single-case and 1:1 with its mutant
  (`trailing-space`→M11, `crlf`→M12, `outside-root`→M13, `indented-comment`→M14). The prereg C3
  claim "four single-defect mutants … survive every existing fixture" is **confirmed on measured
  bytes**: all four read `ALIVE` in r36, r37 *and* r38 (and that is the independent `base_killed=0`
  reading, §8).

**Verdict:** PASS — the new fixture's marginal contribution is exactly the four record-file
behaviours it names, and it subsumes nothing.

### 6a. Are r39's three non-battery cases load-bearing? (per-case probe)

The battery leaves `good`, `total-before-rows` and `comments-total-only` unscored — no M7–M14
mutant changes their verdict. Two single-defect probes (mine, not contract mutants) answer whether
those cases guard anything:

```
$ TMPDIR=… python3 -B probe.py
PROBE P-empty-guard-removed anchor_count=1
  r36  KILL  rc=1 fails=1 ... failing=case-empty=FAIL
  r37  ALIVE rc=0 fails=0 ...
  r38  KILL  rc=1 fails=1 ... failing=case-empty-record=FAIL
  r39  KILL  rc=1 fails=1 ... failing=case-comments-total-only=FAIL
PROBE P-total-after-rows-required anchor_count=1
  r36  KILL  rc=1 fails=1 ... failing=case-empty=FAIL
  r37  ALIVE rc=0 fails=0 ...
  r38  ALIVE rc=0 fails=0 ...
  r39  KILL  rc=1 fails=2 ... failing=case-total-before-rows=FAIL,case-comments-total-only=FAIL
```

```
PROBE P-total-satisfies-empty anchor_count=1      # `if not rows:` -> `if not rows and total is None:`
  r36  KILL  ... failing=case-empty=FAIL
  r38  ALIVE rc=0 fails=0
  r39  KILL  rc=1 fails=1 ... failing=case-comments-total-only=FAIL
PROBE P-total-row-rejected anchor_count=1         # TOTAL rows refused entirely
  r36  KILL  rc=1 fails=9; r37 KILL rc=1 fails=6; r38 KILL rc=1 fails=5 (incl. case-total-ok=FAIL)
  r39  KILL  rc=1 fails=4 ... failing=case-good=FAIL,case-total-before-rows=FAIL,case-crlf=FAIL,case-comments-total-only=FAIL
```

Readings:

- `total-before-rows` is **uniquely load-bearing**: `P-total-after-rows-required` survives r38 and
  is killed by r39 *on that case*. (r36's kill of the same probe lands on `case-empty`, a different
  class, so it is not a substitute.) A fifth record behaviour — TOTAL-before-REPO ordering — is
  covered by r39 and by no other fixture.
- `comments-total-only` is **uniquely load-bearing**, but narrowly: `P-total-satisfies-empty`
  survives r38 (whose `empty-record` body carries no TOTAL row) and is killed by r39, because the
  r39 body is `"# only a comment\n" + TOTAL`. The case therefore asserts "a TOTAL row alone does not
  satisfy RECORD-EMPTY" — one assertion r38 does not make.
- `good` is **non-discriminating and strictly redundant with r38's `total-ok`** — the bodies are the
  same string (`REPO alpha…REPO beta…TOTAL repos=2 regs=2 prunable=0`); every probe that kills
  `good` also kills `total-ok` (`P-total-row-rejected`). It is still needed as r39's own pristine
  anchor (the counter's `pristine=ok` leg runs this fixture alone), so its value is control, not
  discrimination.

## 7. Documented behaviour with no fixture and no mutant (coverage gap, outside the frozen battery)

`tools/souji-worktree-drift.py` documents one refusal class twice — line 50: "RECORD-OUTSIDE-ROOT  a
record row, **or the gitdir it resolves to**, escapes" — and enforces two separate raises: the row
guard (`RECORD-OUTSIDE-ROOT: %s resolves outside %s`) and the gitdir guard
(`RECORD-OUTSIDE-ROOT: %s gitdir resolves outside %s`, ~line 310). M13 removes **only the row
guard**; no fixture writes a `.git` *file* pointing outside `--root` (r36:247 and r37:159,185 write
`gitdir: /nonexistent/gitdir`, which is the broken-repo/UNREACHABLE class, not an escape).

```
$ TMPDIR=… python3 -B gitdir_probe.py
gitdir-arm anchor_count=1
PRISTINE                 rc=2 REFUSAL RECORD-OUTSIDE-ROOT: alpha gitdir resolves outside /fast/scratch/hyaku/souji-r39/W1ConnCoverage/gitdir-probe/fleet-root/fleet
P-gitdir-guard-removed   rc=1 DRIFT	REGS-CHANGED	alpha	record=0 live=1 | SUMMARY ... drift_rows=1 unreachable=0
r36  ALIVE SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
r37  ALIVE SUMMARY cases=6 pass=6 fail=0
r38  ALIVE SUMMARY cases=10 pass=10 fail=0
r39  ALIVE SUMMARY cases=7 pass=7 fail=0
```

The arm is **live** on pristine bytes (rc 2, exact class) and a single-defect mutant that removes it
is **killed by no fixture**: with the guard gone the tool reports `DRIFT REGS-CHANGED` and exits 1
for a repository whose gitdir sits outside `--root`. This does not falsify C3 — C3 claims four
behaviours and delivers four — but the r39 fixture's own framing ("record-file edge classes the
existing drift fixtures never assert") and the tool's docstring both name this fifth class, and it
remains unasserted by every fixture and unmutated by every battery.

**Verdict:** OPEN (advisory) — one documented refusal arm has zero fixture coverage; a one-case
addition to `r39-drift-record-rules.py` (`.git` file → outside gitdir, expect rc 2
`RECORD-OUTSIDE-ROOT`) plus an M15 would close it. Not required by the frozen predicate.

## 8. Cross-check against the two frozen batteries

```
$ TMPDIR=… python3 -B tests/fixtures/r38-drift-mutants.py \
    --fixture tests/fixtures/r38-drift-record.py \
    --base-fixture tests/fixtures/r37-drift-discrimination.py --work /fast/scratch/hyaku/souji-r39/W1ConnCoverage
MUTANT M7 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M8 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M9 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M10 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0
RC=0
```

```
$ TMPDIR=… python3 -B census/round-39/c3-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch /fast/scratch/hyaku/souji-r39/W1ConnCoverage/c3
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
RC=0
```

**Verdict:** PASS — the C3 predicate reading (`mutants=4 killed=4 survived=0 pristine=ok
base_killed=0`, plus `cases=7 ≥ 6`) reproduces on committed bytes and agrees cell-for-cell with the
independent 32-run matrix. `base_killed=0` is corroborated by the matrix's r38 column reading
`ALIVE` for M11–M14.

## 9. Connector finding on the r39 counter itself (operability, same class as R10/R11)

`census/round-39/c3-counter.py` docstring: "Exit: 0 `SUMMARY …`; 1 any survivor, pristine failure,
base kill or short fixture; 2 usage / could-not-evaluate input." A `--scratch` path that does not
exist is a usage error, but it is not validated:

```
$ TMPDIR=… python3 -B census/round-39/c3-counter.py --root … --rev 2201778… --base-rev ed30b7f… \
    --scratch /fast/scratch/hyaku/souji-r39/W1ConnCoverage/nonexistent
RC=1
    _os.mkdir(file, 0o700)
FileNotFoundError: [Errno 2] No such file or directory: '/fast/scratch/hyaku/souji-r39/W1ConnCoverage/nonexistent/souji-r39-c3.lsg5ozik'
```

`tempfile.mkdtemp(... dir=args.scratch ...)` (c3-counter.py:120) raises instead of refusing, so the
tool exits **1 with a traceback** where its own docstring promises **2**. Exit 1 is also the value
that means "a mutant survived", so a caller that only checks the exit code cannot distinguish a bad
invocation from a coverage failure — the exact defect shape C2 repairs in
`tools/souji-citation-reconcile.py` (unresolvable input collapsing into a findings exit). The happy
path is unaffected (§8), and the frozen C3 predicate does not cover it, so this is advisory, not a
C3 falsification.

**Verdict:** OPEN (advisory) — `--scratch` should be validated like `--work` in the fixtures
(`if not os.path.isdir(work): return 2`).

## 10. Risks the matrix exposes

1. **Single-guard kills.** Every one of the eight kills is a single failing case, and M11–M14 are
   killed by exactly one case each. If `crlf`, `outside-root` or `indented-comment` is weakened or
   dropped, the corresponding mutant flips to `ALIVE` with no second guard; `survived` would move
   from 0 to 1 and the C3 predicate would fail loudly (fails closed, good) but the fixture has no
   slack.
2. **Shared anchor between M11 and M14.** Both mutants rewrite the same source line
   (`        if not line.strip() or line.startswith("#"):`, the battery's `SKIP_ANCHOR`). A refactor
   of that one line breaks two of the four r39 mutants together — correlated fragility in the
   coverage instrument, not in the tool.
3. **r38 is load-bearing for three rules.** M8/M9/M10 have r38 as their only killer. r39 must not be
   read as a replacement for r38 in any future consolidation.

## 11. Verdict summary

| check | verdict | evidence |
|---|---|---|
| measured bytes == HEAD bytes | PASS | §0 digests match counter's `tool_sha`/`fixture_sha` |
| all 8 mutant anchors unique | PASS | `anchors M7=1 … M14=1` |
| 4 fixtures pristine on unmutated tool | PASS | `fail=0` ×4, r36 `control=STUB-REJECTED` |
| killer matrix complete (32 runs) | PASS | §3, 9 kills, 0 crashes, 0 NO-SUMMARY |
| no mutant killed by none (M7–M14) | PASS | §5 `GAP-NONE` |
| redundant mutants reported | PASS | M7 only, `r36,r38`, and partial (repos arm only) |
| r39 marginal contribution | PASS | exactly M11–M14, disjoint from r38/r36/r37 |
| r39 cases load-bearing beyond the battery | PASS (2 of 3) | `total-before-rows`, `comments-total-only` uniquely discriminating; `good` = pristine anchor, redundant with r38 `total-ok` |
| frozen C3 counter reproduces | PASS | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`, RC=0 |
| gitdir outside-root arm covered | **OPEN (advisory)** | §7: live arm, mutant survives all four fixtures |
| c3-counter usage exit class | **OPEN (advisory)** | §9: rc 1 + traceback where docstring promises 2 |

No falsification of C1, C2 or C3 was observed on the bytes measured here; the two OPEN rows are
coverage/operability gaps adjacent to C3, not contradictions of its predicate.

Scratch `/fast/scratch/hyaku/souji-r39/W1ConnCoverage` was removed with `shutil.rmtree` /
`rm -rf` after this report was written; no scratch tree is left on disk. No tool was installed or
upgraded for this seat.
