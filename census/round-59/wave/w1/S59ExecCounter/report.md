# S59ExecCounter — bounded assessment of the frozen registry-kind counter

Seat: S59ExecCounter (executor, round 59 w1). Assignment: exercise the frozen
`census/round-59/c1-counter.py --selftest --work <own scratch>` through its
public path; assert the four controls cases; independently derive the base
mismatch; classify `census/round-58/c1-counter.py` against the PROTOCOL Gate
standard read from source; probe duplicate current-row shapes and misleading
prose rows in an isolated fixture. No production edit, no frozen-instrument
edit, no commit, no closure authority claimed.

All `evidence/...` receipt paths below resolve under
`.ufo/waves/round-59/w1/S59ExecCounter/evidence/`; the probe receipt records
its temporary fixture toplevel under `/fast/scratch/hyaku/souji-r59/S59ExecCounter/`.

Frozen landmarks read first: `census/round-59/preregistration.txt` at
`19f44552378d333f401ff2f0864c4e8b9c59ab1f` (claim: one bounded calibration
assertion, `mismatches=1 -> 0` for the unique current assessment-comparison
row, kind cell must read `gate`; not parser repair) and the executed controls
at `74455b7209e04a2375c2084738a7b6fea59bf6d5` (`controls.py` four cases:
unchanged 1, prose-forgery 1, duplicate-forgery 2, positive 0).

## Axes

1. Executable selftest substance — the frozen public selftest actually runs and
   discriminates, with the expected values verified independently.
2. Independent measurement fidelity — the base mismatch is recomputed without
   importing the frozen counter and reproduces the finding, summary and exit
   lines recorded in `before.txt`.
3. Classification fidelity — the r58 source is graded clause-by-clause against
   the canonical Gate standard, including the clause it fails.
4. Confinement and no-harm — every write under own scratch or delivery, every
   git call in an isolated fixture whose toplevel was asserted, frozen bytes
   and census unchanged.

## 1. Frozen public selftest — exercised, confirmed

Command (public CLI path, not a direct controls.py call):

```
python3 -B census/round-59/c1-counter.py --selftest --work /fast/scratch/hyaku/souji-r59/S59ExecCounter
```

`EXIT=0`; stderr empty; stdout `census/round-59/controls.py` JSON
(receipt `evidence/01-public-selftest.json`). Instrument digest echoed by the
run is `2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d`,
equal to the preregistration pin.

| case | input fixture rev | rc | findings | controls expectation | verdict |
|---|---|---|---|---|---|
| unchanged | `cb6ab75cbccbe20ff02c64fbfc97d18ac33c7812` | 1 | `REGISTRY-KIND-MISMATCH` | 1 / same | PASS |
| prose-forgery | `44ac8a1d790e9313291c9ca46619961e7012d82f` | 1 | `REGISTRY-KIND-MISMATCH` | 1 / same | PASS |
| duplicate-forgery | `a2fe1b5738691967c28ed7f39e20b139e51ae533` | 2 | `REGISTRY-ROW-SHAPE` | 2 / same | PASS |
| positive | `ff0f22e4727b109d2a9705dd923b7b39da179d78` | 0 | none | 0 / none | PASS |

Independent assertion driver `evidence/02-assert-selftest.py` re-parses the
captured stdout, re-reads the literal case table in `controls.py`, and does
not trust the JSON `passed` field. Result:
`SUMMARY assertions=54 failures=0` / `RESULT SELFTEST-RECEIPT-CONFIRMED`
(`evidence/02-assert-selftest.out`). It also asserts every child command
invokes the frozen counter through the public CLI, every fixture root sits
under this seat's scratch, `controls.py` creates its fixture with
`mkdtemp(prefix='controls-',dir=parent)` and removes only that child, and the
counter bytes still hash to the prereg value.

## 2. Independent derivation of the base mismatch

`evidence/03-derive-base.py` imports nothing from the frozen counter. It reads
`git show da5af55b5ea0a2a38edea05635a13416c698e6e7:SKILL.md`, selects the row
by exact prefix in the frozen order (`r59` branch first, `r58` fallback), and
independently re-parses the same line with a full-row grammar:

```
M1 r59-prefix-lines=0 r58-prefix-lines=1 selected=1 branch=r58
M2 labelled-rows=1
M2 row line=776 label=r58 assessment comparison cells=8 kind='evidence' full-grammar=True
FINDING REGISTRY-KIND-MISMATCH
INDEPENDENT assertions=1 mismatches=1 row_shape_ok=True rev=da5af55b...
EXIT=1
```

The frozen counter itself over the same base and lane
(`evidence/04-base-frozen-counter.out`, stderr empty) prints exactly
`FINDING REGISTRY-KIND-MISMATCH` / `SUMMARY assertions=1 mismatches=1
rev=da5af55b5ea0a2a38edea05635a13416c698e6e7` / `EXIT=1`, matching
`census/round-59/before.txt` and `controls.json` for the unchanged case.
The mismatch is the kind cell (`evidence`) of the unique row at `SKILL.md:776`;
the row shape is 8 cells (10 split fields), so row shape is not the defect.

## 3. Source classification against PROTOCOL §Gate standard

Full clause-by-clause record: `evidence/09-gate-classification.md` (canonical
text at fleet root `PROTOCOL.md:375-408`; lane gate map `SKILL.md:196-204`).

Reading `census/round-58/c1-counter.py` (blob sha256
`52ccdb1be66dd8379fb7bf81eae7e28965f156aa50e1e4573b82adb23bd0dea7`):
it reads the two committed r57 matrices and `SCORECARD.md` at the named
revision (`:8-16`), derives `exit_zero` and `carry_identical` from the committed
TSV values (`:17-19`), interpolates them into two literal note templates
(`:20-22`), compares by exact substring (`:23`), and returns
`int(bool(mismatches))` with 2 reserved for argparse usage (`:25,:29-33`).
Observed over committed blobs (`evidence/07-r58-source-returns.out`):
`83d3813...` -> two `MISSING`, `mismatches=2`, `EXIT=1`;
`da5af55b...` -> two `MATCH`, `mismatches=0`, `EXIT=0`.

Classification returned: a **gate-interface comparator** — committed,
re-runnable, reads surfaces, compares persisted expected values, returns a
fail-capable verdict. It is not a `probe` (it can fail) and not `evidence` in
the lane's own definition (its exit 1 is a consumed runner failure, not
"unused by code"; it writes no record). Its `evidence` registration is the one
REGISTRY-KIND-MISMATCH the frozen counter counts.

Limit carried with the verdict: the source does **not** satisfy the Gate
standard's Self-test clause — no self-invocation mode exists; the r58 row's own
self-test cell says "external discrimination fixture supplied with the round;
counter has no self-invocation certification". So it is a historical gate by
interface with a disclosed conformance debt, which is exactly why the frozen
implementation supersedes it with a selftest-bearing successor instead of
editing only the kind cell. The counter grades classification, not execution.

## 4. Isolated fixture probes — duplicate current-row shapes and misleading prose

Driver `evidence/06-probe-rows.py`: fresh `git init` under this seat's scratch,
`git -C <fixture> rev-parse --show-toplevel` asserted equal to the fixture
before the first commit, fixture removed in `finally`. Full receipt with each
input row and command: `evidence/06-probe-receipt.json`; summary
`evidence/06-probe-rows.out` (`SUMMARY probes=15 passed=15 failures=0`, rc 0).

| probe | intent | rc | findings |
|---|---|---|---|
| dup-r59-identical | two current r59 gate rows | 2 | REGISTRY-ROW-SHAPE |
| dup-r59-mixed-kind | current r59 gate row + r59 evidence twin | 2 | REGISTRY-ROW-SHAPE |
| r59-plus-r58 | stale r58 row beside r59: r59 branch wins | 0 | none |
| prose-r58-gate-words | prose "this is a gate" beside evidence-kind r58 row | 1 | REGISTRY-KIND-MISMATCH |
| prose-r59-gate-words | prose gate claims beside evidence-kind r59 row | 1 | REGISTRY-KIND-MISMATCH |
| padded-kind-gate | kind cell whitespace-padded `   gate   ` | 0 | none |
| upper-kind-Gate | kind `Gate` (case-sensitive compare) | 1 | REGISTRY-KIND-MISMATCH |
| near-miss-prefix | `|  r59 ...` and `| r59 ... (gate) |` decoys + base r58 | 1 | REGISTRY-KIND-MISMATCH |
| short-row-9cells | r59 row missing one cell | 2 | REGISTRY-ROW-SHAPE |
| no-comparison-row | no assessment-comparison row at all | 2 | REGISTRY-ROW-SHAPE |
| fenced-dup-r59 | second current-looking row inside a fenced block | 2 | REGISTRY-ROW-SHAPE |
| dup-r58-mixed-kind | fallback-branch evidence/gate duplicate | 2 | REGISTRY-ROW-SHAPE |
| prose-row-wrong-kind | every other cell says `gate`, kind stays evidence | 1 | REGISTRY-KIND-MISMATCH |
| forged-gate-row | fabricated row with kind `gate` and nonsense command/cells | 0 | none |
| malformed-r59-plus-valid-r58 | malformed exact-prefix r59 line + valid r58 row | 2 | REGISTRY-ROW-SHAPE |

Readings: the duplicate guard is exact-prefix only — a second r59 line counts
even inside a fence, while prefix variations are invisible; once any exact r59
line exists there is no fallback to r58 and a malformed one poisons the check;
the kind test strips whitespace but is case-sensitive; prose words never set
the kind; and a fabricated gate-kind row passes, confirming the frozen note
that the counter counts classification only, not execution authentication.

## Limits

- The counter cannot authenticate execution: `forged-gate-row` exits 0 by
  kind cell alone (preregistration already discloses this).
- Error mapping is narrow: unresolvable/short `--rev` and git failure exit 1
  with a traceback (`evidence/08-error-path-probes.out`); only argparse usage
  errors reach 2, so "could-not-evaluate" is not reached for bad input.
- No timeout/stderr capture in `check_output`; a hung git hangs the counter.
- `--selftest` hardcodes base `da5af55b...`, the lane root as
  `Path(__file__).parents[2]`, and `python3` from PATH; a copied counter would
  grade another tree or fail, and the selftest is not revision-general.
- Row selection is line-prefix based with no fence/heading model; duplicate
  detection applies only to the selected branch (r59 when present).
- The r58 comparator's own semantics are loose (`zip` truncation, positional
  column 5, substring note presence, duplicate notes pass); these are
  lane-owned vocabulary limits, not the registry-kind defect.
- The controls JSON `passed` field is data; the receipt was re-verified
  independently (54 assertions) rather than trusted.

## Integrity and confinement

- `census/round-59/c1-counter.py` sha256 `2c4d45aa...` and `controls.py`
  sha256 `ba8af5cc...` identical before and after every run
  (`evidence/05-frozen-before.sha256` vs `05-frozen-after.sha256`).
- `git diff 19f4455 -- census/` is empty; freeze artifacts untouched
  (`preregistration.txt` 8ca0c775..., `population.tsv` c2e24c99...,
  `before.txt` fe215e71..., `controls.json` 1ec401ec...).
- Lane `git status --porcelain` shows only pre-existing sibling corpus edits
  (`corpus/QUALITY.md`, `corpus/SOURCES.md`, untracked
  `corpus/lessons/round-59.md`); no seat write outside own scratch/delivery.
- All fixture git calls were `-C <scratch fixture>` after toplevel assertion;
  the probe fixture and the controls temp child were removed. All tool
  invocations were local python/git reads; no install, no network, no pacman.

## Verdict

The frozen counter's selftest is substantively executable (4/4 cases, rc 0,
54 independent assertions) and its base reading is independently reproduced
(`mismatches=1`, `REGISTRY-KIND-MISMATCH`, exit 1). The r58 source is a
gate-interface comparator whose `evidence` registration is the counted
mismatch, with an unmet Self-test clause that the r59 successor must cure.
No closure or integration authority is claimed; this seat returns evidence only.
