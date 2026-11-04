# S59Mutation — bounded mutation probes over the frozen round-59 calibration counter

Seat: S59Mutation (leaf, mutation-tester). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Bounds honoured: no production edit, no sibling/fleet edit, no commit/push, no `jj` mutation, no
task dispatch, no docs beyond this report and its sibling receipts. All fixture Git activity used
explicit `-C` inside this seat's scratch `/fast/scratch/hyaku/souji-r59/S59Mutation/`; the public
controls driver asserts `rev-parse --show-toplevel == <its own mkdtemp>` before every fixture
commit, and a separate guard recorded that the scratch root itself is not inside any checkout
(`git -C <scratch> rev-parse --show-toplevel` → `EXIT 128`). No installs (`environment.txt`).

Frozen inputs read, unchanged by this seat:

| Input | Identity |
|---|---|
| claim/preregistration | `19f44552378d333f401ff2f0864c4e8b9c59ab1f:census/round-59/preregistration.txt` |
| executed controls | `74455b7209e04a2375c2084738a7b6fea59bf6d5:census/round-59/*` |
| counter under test | `census/round-59/c1-counter.py` sha256 `2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d` |
| controls driver (detector) | `census/round-59/controls.py` sha256 `ba8af5cc5404eb4108ab15ee6386d15907c73abf04cda3b780e592b5d7d452b8` |
| fixture base rev | `da5af55b5ea0a2a38edea05635a13416c698e6e7` |
| population | `census/round-59/population.tsv` sha256 `c2e24c9961dd8d54794b3dea1e959ead1072c493c095874d661d59bc0ef9adb0` |

## 1. Executed mutants — three of three killed, no survivors

Detector for every mutant: an independent scratch copy of the public controls driver
(`driver/controls-driver.py`, byte-identical to `74455b72:census/round-59/controls.py`), invoked as

```
python3 -B <driver copy> --root <lane> --rev da5af55b5ea0a2a38edea05635a13416c698e6e7 \
        --counter <stage counter> --work <own scratch>/stages/<mutant>/<stage>/work
```

The driver rebuilds one isolated fixture repository per stage, commits the four retained input
rows, and requires per case both the exit code and the full ordered `FINDING` list, plus the
aggregate `passed` count. It reports `instrument_sha256`, so each stage's measured instrument is
identified in the receipt.

| Mutant | Smallest behaviour-bearing change | Mutant sha256 | Pristine / mutant / restored driver EXIT | Discriminating case(s) | Verdict |
|---|---|---|---|---|---|
| always-clean | `if row[2] != 'gate': findings.append('REGISTRY-KIND-MISMATCH')` → `pass` (verdict always clean) | `11657c1e971d34d2f3ff0b854c35550cdb6c646e2b3590032748911d48c443a4` | 0 / 1 / 0 | `unchanged`, `prose-forgery` (rc 0 seen, 1 expected; findings `[]`, expected `REGISTRY-KIND-MISMATCH`) | **killed** |
| ignore-duplicate-guard | `if len(rows) != 1 or ...` → `if not rows or ...` (duplicate row guard dropped, first row decides) | `3abf9604f805584a9188b5415625354141b67355e490cf658b68c20cbf4ff7f6` | 0 / 1 / 0 | `duplicate-forgery` (rc 1 + `REGISTRY-KIND-MISMATCH` seen, 2 + `REGISTRY-ROW-SHAPE` expected) | **killed** |
| accept-prose-gate | kind test extended with `and 'gate' not in text` (prose occurrence of the word satisfies the kind field) | `a2500457fb4e5e6b671175408f22943a51c6f792cd7eaf9d131dd8aab6218740` | 0 / 1 / 0 | `prose-forgery` (rc 0 + no finding seen, 1 + `REGISTRY-KIND-MISMATCH` expected) | **killed** |

Observed per-stage case passes: always-clean 4/4 pristine, **2/4 mutant**, 4/4 restored;
ignore-duplicate-guard 4/4, **3/4**, 4/4; accept-prose-gate 4/4, **3/4**, 4/4. The `positive`
case passes in every mutant (by construction a positive-only inventory cannot kill an
always-clean defect) and `duplicate-forgery` passes in the first and third mutants — the kills are
each attributable to the named case, not to a blanket run failure.

Restoration evidence (byte identity, all three):

- pristine stage counter digest `2c4d45aa…a6d` == frozen pin, `bytes_equal_frozen=true`;
- restored stage counter digest `2c4d45aa…a6d` == frozen pin, `bytes_equal_frozen=true`, driver
  EXIT 0 with 4/4 cases passing;
- delivered `mutants/<name>.restored.py` re-hashes to the frozen pin independently of the JSON.

## 2. Bounded assessment gate classification (read-only observation)

`freeze-classification.txt` records the frozen counter run over committed blobs only:

```
--rev 19f44552378d333f401ff2f0864c4e8b9c59ab1f -> FINDING REGISTRY-KIND-MISMATCH
                                                  SUMMARY assertions=1 mismatches=1   EXIT=1
--rev da5af55b5ea0a2a38edea05635a13416c698e6e7 -> FINDING REGISTRY-KIND-MISMATCH
                                                  SUMMARY assertions=1 mismatches=1   EXIT=1
```

At the freeze rev the population row is still `evidence` (SKILL.md `r58 assessment comparison`,
line 776), no `r59 assessment comparison` row exists (`r59_rows=0`, `r58_rows=1`), and `SKILL.md`
+ `SCORECARD.md` are byte-unchanged from the base rev. So the frozen target
`assertions=1 mismatches=0` is **preregistered, not yet measured**: the kind edit that makes the
counter read 0 has not landed, and the counter's `r59` branch is inert — the `r58` fallback is what
all four control cases and all three mutants exercise. That is consistent with the freeze text
("No candidate score has run") and with classifying this as a registry-kind correction rather than
parser repair. This seat makes no statement about the implementation's correctness; the frozen
instrument bytes were used unmodified.

## 3. r58 comparator selftest debt — inventory (grounded in bytes, not inferred)

The predecessor comparator `census/round-58/c1-counter.py` (36 lines, sha256
`52ccdb1be66dd8379fb7bf81eae7e28965f156aa50e1e4573b82adb23bd0dea7`) has **no selftest and no
self-invocation**: its argparse accepts only `--root` and `--rev` (lines 33–34). The r58 row still
reads `evidence`, and the round directory `census/round-58/` contains no discrimination fixture —
the only r58 C1 detector is a wave artifact (`census/round-58/wave/w1/S58Executor5/c1-tests.py`,
retained copy under `S58Mutationtester10/c1-tests.py`), where `probe()` raises on an exit-code
mismatch and also asserts the exact per-note `MATCH`/`MISSING` lines. The r59 successor adds
`--selftest`, which delegates to `controls.py`; that harness has the following unmutated debt:

| # | Debt | Exact location | Consequence |
|---|---|---|---|
| d1 | Selftest is path-coupled, not self-contained | `c1-counter.py:31–32` resolves `here.with_name('controls.py')` | a copy of the counter without a sibling harness has no working self-invocation; there is no in-file harness |
| d2 | Measured instrument digest is printed but never pinned | `controls.py:25` computes `instrument_sha256`; no comparison to `2c4d45aa…` anywhere in the file | certification never refuses a non-frozen counter digest; the digest is evidence for a human, not a gate |
| d3 | Fixture confinement guard is a bare `assert` | `controls.py:11` | under `python -O` the toplevel assertion disappears; the driver is normally invoked with `-B` only |
| d4 | No `GIT_*` environment scrub | `controls.py` has no `GIT_` handling (contrast `census/round-58/c2-gate.py:git_env()`) | an ambient `GIT_DIR`/`GIT_CONFIG_*` can redirect the fixture repository and global config |
| d5 | No independent expected-set census | `controls.py:15–19` — the fixture inventory and the expectations are the same literal list | unlike `c2-gate.py`'s `SELFTEST-EXPECTED-SET … extra= missing=`, an omitted expected row is undetectable in principle; rows can only be dropped together with their fixture |
| d6 | Exit code 1 is overloaded | `c1-counter.py:8` `subprocess.check_output` uncaught | a `git show` failure raises a traceback that also exits 1, the same code as `REGISTRY-KIND-MISMATCH`; "data error" and "discrepancy" are not separable by exit status, only by stdout shape |

Debt d5 is the structural reason the third candidate below cannot be caught by the harness as it
stands; d1–d4 are guard-strength debts that a meta-selftest would have to exercise.

## 4. Candidate selftest mutants — exact, unrun, no verdict claimed

Proposed against `census/round-59/controls.py` (sha256 `ba8af5cc…52b8`). Each candidate is built
as exact bytes and a unified diff under `selftest-candidates/`; each pairs with an escape witness
instrument so that a future run has a defined expected discrimination. **Status of every row:
`unrun` — the candidate was constructed, never executed; no kill and no survival is claimed.**
Witnesses `rc-wrong-findings-right` and `findings-suppressed` are likewise unrun; the third witness
is the executed `ignore-duplicate-guard` mutant above.

| Candidate | Exact replacement | Candidate sha256 | Escape witness (sha256) | Would-be runner |
|---|---|---|---|---|
| rc ignored | `passed=r.returncode==expected_rc and actual==expected` → `passed=actual==expected` | `aeb1c8f78d59c7c9f927901dbc7c90e34f018d72b90278558e5f4051c9e898af` | counter `return int(bool(findings))` → `return 0` (`98d95067263b298212b6fade674d8dd4e74e4a3af906b9469e2d7ce22073e1dd`) | `python3 -B candidates/rc-ignored.py --root LANE --rev da5af55… --counter witnesses/rc-wrong-findings-right.py --work …` |
| finding ignored | same line → `passed=r.returncode==expected_rc` | `af507fe601dfd1727f6cc0919fa5cf87e2fe089e65551a79857232ed9ee5a307` | counter with `for finding in findings: print('FINDING '+finding)` deleted (`576ad5719ef979389e34740959e5410def4df5b8ad137b49e88f09b5e4bd1bc6`) | as above with `finding-ignored.py` / `findings-suppressed.py` |
| omitted expected row | delete `('duplicate-forgery', … 2,['REGISTRY-ROW-SHAPE']),` (controls.py:18) | `051a1193f9a0d70c89265dc11911122daf01bf5fa4e13ecef47702902c921036` | executed `ignore-duplicate-guard` mutant (`3abf9604…ff7f6`) | as above with `omitted-expected-row.py` / `ignore-duplicate-guard.py` |

Observed support, not a verdict: the executed `ignore-duplicate-guard` mutant's only discriminating
case against the full four-case inventory was `duplicate-forgery` — the exact row candidate 3
removes. Whether the reduced inventory still fails the witness, and whether candidates 1 and 2
swallow their witnesses, are unmeasured questions for the next round.

Witness anchors for candidates 1–2 are in `census/round-59/c1-counter.py`:
`    return int(bool(findings))` and `    for finding in findings: print('FINDING '+finding)`; both
occur exactly once (the generator asserts anchor cardinality before writing bytes).

## 5. Limits

- Three assigned mutants, one detector, one frozen input cohort. This is not a claim about
  universal counter correctness, and no mutant is a claim that the counter's contract is wrong.
- Surviving nothing here means the retained four-case control set discriminates these three defect
  classes; it says nothing about kinds outside them (row truncation, column-shift, summary text
  forgery, multi-row prose).
- No historical gate was touched, no certification was re-declared, and no closure authority is
  claimed for any lane output other than this seat's own probe result.
- Own scratch was removed only after every receipt above was copied into this directory; the
  delivered `pristine/`, `driver/`, `mutants/*.restored.py` byte-identical copies are what makes
  the triplets re-checkable without that scratch.

## 6. Self-evaluation

Accuracy 5 (all three verdicts are observed triplets with case-level attribution; the classification
section is read-only and explicitly marks the target as unmeasured). Completeness 4 (assignment
asked for executed counter mutants plus proposed selftest mutants; the selftest mutants are
constructed, not run, by instruction). Clarity 4 (dense evidence tables; debt table carries the
reasoning). Actionability 5 (candidate diffs, witness bytes, digests and runner strings are all
delivered). Conciseness 4. Overall 4.4. Improvement: the r58 wave fixture could have been reused
directly instead of a fresh driver copy, at the cost of independence from a prior seat's bytes.

Report: .ufo/waves/round-59/w1/S59Mutation.md
