# W1ExecC3Baseline — do any pre-round fixtures kill the four C3 mutants?

Seat: executor (leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base revision measured: `ed30b7f5b77939c9073348d810730bc4f355708d`.
Tool under mutation: `tools/souji-worktree-drift.py` at that revision,
`git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py | sha256sum`
→ `14e9c0f77d7e…` (the counter`s `tool_sha`).
Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecC3Baseline` (all counter runs left it empty; my
manual probe dirs were removed — see §Scratch).
No file in the lane was modified by this seat except this report.

## 1. Reproduce the frozen control (`c3-before.txt`) — PASS

Command (cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`):

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Baseline
```

Observed (saved to scratch as `r38-fixture-run.txt` for the diff):

```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
RC=1
```

`diff -u census/round-39/records/c3-before.txt <run>` → empty (`DIFF-EMPTY`). The frozen control
reproduces byte-for-byte, including `tool_sha` and `fixture_sha`.

Verdict: **PASS** — `c3-before.txt` (`killed=0 survived=4 pristine=ok base_killed=0 cases=10`) is
reproducible; `tests/fixtures/r38-drift-record.py` leaves all four mutants alive.

## 2. `tests/fixtures/r36-worktree-drift.py` — kills nothing

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r36-worktree-drift.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Baseline
```

```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=12 tool_sha=14e9c0f77d7e fixture_sha=6b35f54a426f
RC=1
```

Verdict: **survivors = M11, M12, M13, M14** (4/4 alive; 12 cases, pristine ok).

## 3. `tests/fixtures/r37-drift-discrimination.py` — kills nothing

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r37-drift-discrimination.py \
  --base-fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Baseline
```

```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=6 tool_sha=14e9c0f77d7e fixture_sha=509795608e9c
RC=1
```

Verdict: **survivors = M11, M12, M13, M14** (6 cases, exactly the `cases>=6` threshold; pristine
ok, so the `--base-fixture` arm was not needed to keep it sane).

## 4. Bonus sweep — `tests/fixtures/r37-drift-escapes.py`: counter cannot evaluate it

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r37-drift-escapes.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Baseline
```

```
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=12
RC=1
```

This is the **defect of the request** class the task anticipated, not a survivor: the fixture's CLI
needs `--base-tool` (`CLI: … [--tool PATH] [--base-tool PATH] [--work DIR]`), and the counter only
passes `--tool`/`--work`, so its pristine arm runs with `control=NO-BASE-TOOL` and reads `fail>0`.

Manual measurement that the counter cannot make (pristine tool extracted to scratch, every mutant
applied at its single anchor, fixture invoked as
`python3 -B tests/fixtures/r37-drift-escapes.py --tool <cand> --base-tool <pristine> --work <scratch>`):

```
tool_sha 14e9c0f77d7e
pristine+base: rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
M11+base:      rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
M12+base:      rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
M13+base:      rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
M14+base:      rc=1 SUMMARY cases=12 pass=12 fail=0 base_fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED
```

Verdict: **survivors = M11, M12, M13, M14** under the r38 A5 kill contract (no `fail>0`, so no
kill), **but** this fixture is independent of the four record rules (0 failing cases for every
candidate, including pristine) and its own control reports `ESCAPE-NOT-REPRODUCED` / `escapes=0`
on the base bytes — it adds no coverage here and is not a valid base/candidate arm.

## 5. FINDING — a pre-round fixture DOES kill M13: `r38-drift-write-envelope.py`

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-write-envelope.py \
  --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Baseline
```

```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=1 survived=3 pristine=ok base_killed=0 cases=12 tool_sha=14e9c0f77d7e fixture_sha=d6fed4af1e8a
RC=1
```

Direct quote naming the killing case (M13 = the `RECORD-OUTSIDE-ROOT` refusal replaced by `pass`):

```
r38-drift-write-envelope.py rc= 1
   case-record-outside-root=FAIL rc=1 out=['DRIFT\tABSENT\t../escaped\trecorded regs=1', 'DRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0']
   SUMMARY cases=12 pass=11 fail=1
r38-drift-record.py rc= 0
   SUMMARY cases=10 pass=10 fail=0
```

Provenance: the fixture is pre-round — working-tree bytes are identical to the base revision
(`sha256 work=d6fed4af1e8a base=d6fed4af1e8a same=yes`,
`git show ed30b7f5b779…:tests/fixtures/r38-drift-write-envelope.py`), it is tracked at `ed30b7f`
(= "lane tip == origin/master at round start"), and its docstring carries
`record-outside-root  a record row escaping --root is refused (regression)`.

Interpretation:
- The frozen C3 **predicate** still holds and is untouched: it names `tests/fixtures/r38-drift-record.py`
  as the base fixture only, and that fixture reads `base_killed=0` (10/10 pass under M13). `killed=4`,
  `pristine=ok`, `cases>=6` remain reachable by the new fixture.
- The frozen C3 **rationale** in `preregistration.txt` is falsified for one of four mutants: "Four
  single-defect mutants of those behaviours **survive every existing fixture**" and "Four
  single-defect mutants … leave alive" is false for M13 — `r38-drift-write-envelope.py`
  `case-record-outside-root` already kills it at the base revision. M13 is therefore not new
  coverage; only M11 (trailing whitespace), M12 (CRLF) and M14 (indented `#`) are genuinely
  unasserted by pre-round fixtures.
- `census/round-39/records/c3-before.txt` is *not* wrong as a receipt (it measures the r38 record
  fixture, and reproduces exactly), but reading it as "no pre-round fixture kills these" is wrong.
- No survivor is a mutation-battery defect: every anchor occurred exactly once (the counter prints
  `ANCHOR-COUNT` otherwise and it never did), and no run produced a traceback
  (`crash=False` everywhere).

## 6. Fixture-family census (why the survivors survive)

`grep -rln "souji-worktree-drift" tests/ tools/` yields the case fixtures `r36-worktree-drift.py`,
`r37-drift-discrimination.py`, `r37-drift-escapes.py`, `r38-drift-record.py`,
`r38-drift-write-envelope.py` and the new `r39-drift-record-rules.py`; `r37-drift-mutants.py` and
`r38-drift-mutants.py` are mutant *drivers*, not case fixtures (no `--tool/--work` case arm; they
take `--fixture`), so they are out of scope for this measurement.

Grep for the four behaviours in the case fixtures: `r36-worktree-drift.py` and
`r37-drift-discrimination.py` contain no `outside`/`CRLF`/`\r\n`/`indent`/`trailing` assertion;
`r38-drift-record.py`'s only `outside` hit is the docstring phrase "a line outside the schema"
(its `bad-line` case), not `RECORD-OUTSIDE-ROOT`; only `r38-drift-write-envelope.py` asserts
`RECORD-OUTSIDE-ROOT`.

## Verdicts

| # | Check | Verdict |
|---|-------|---------|
| 1 | Reproduce `c3-before.txt` byte-for-byte at `ed30b7f` | PASS (diff empty) |
| 2 | `r38-drift-record.py` kills M11–M14? | NO — survived=4, base_killed=0, cases=10 |
| 3 | `r36-worktree-drift.py` kills M11–M14? | NO — survived=4, cases=12 |
| 4 | `r37-drift-discrimination.py` kills M11–M14? | NO — survived=4, cases=6 |
| 5 | `r37-drift-escapes.py` kills M11–M14? | NO (manual, 12/12 pass each) — counter reads `pristine=FAIL` (CLI lacks `--base-tool`), and the fixture's own control reads `ESCAPE-NOT-REPRODUCED` |
| 6 | Any pre-round fixture kills any C3 mutant? | YES — `r38-drift-write-envelope.py` `case-record-outside-root` kills **M13** (rc=1 fails=1 crash=False) |

**C3 status as measured:** the frozen counter predicate is satisfiable and its control is honest,
but the C3 narrative's "four mutants that every existing drift fixture leaves alive" is off by one:
M13 is already covered pre-round, so the round's *new* record-rule coverage is 3 mutants
(M11/M12/M14) plus one duplicate. The L1 should either reword the C3 rationale in the round report
("M13 restores/duplicates pre-existing outside-root coverage; the novel arms are M11/M12/M14") or
swap M13 for a genuinely unasserted behaviour before the C3 narrative is scored as calibration.

## Risks / notes for the L1

- I did **not** run the C3 after-arm (candidate fixture against the landing tool) — that is a
  different seat; `census/round-39/records/c3-after.txt` exists and was not touched.
- `census/round-39/c3-counter.py` does not exist at `ed30b7f` (`git show ed30b7f:…` →
  sha256 of empty), so the frozen control was produced by the working-tree counter; its `tool_sha`
  (from `git show`) and `fixture_sha` fields make that auditable, and both matched here.
- `--fixture`/`--base-fixture` are read from the **working tree**, not from `--rev`; the three
  fixtures I cite are byte-identical to `ed30b7f`, verified by sha, so the measurement is over
  pre-round bytes (a later wave editing them would silently change this arm).
- No package installs were needed; nothing was installed or upgraded.
- Scratch: counter temp dirs are self-removed (`finally: shutil.rmtree`). My probe dirs
  (`…/escapes`, `…/m13`), `escapes-probe.py`, `m13-probe.py` and `r38-fixture-run.txt` were removed
  after the measurements; `/fast/scratch/hyaku/souji-r39/W1ExecC3Baseline` is left empty.
- No git/jj mutation was run: only `status --porcelain`, `show` and `rev-parse`-class reads.
