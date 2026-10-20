# CheckerGreen — C2 green-only / fabricated-evidence attack (round 15, w1)

Seat: critic, leaf. Axes: operability, calibration.
**Status: design-only.** At write time none of these files exist: `tools/souji-preservation-evidence.py`, `tests/fixtures/r15-preservation-evidence.py`, `tests/fixtures/r15-census-config.py` and `census/round-15/run-verification.py` (globbed twice). The attacks below target the AdmissionChecker, ConfigFixture and RoundRunner contracts (`.ufo/waves/round-15/w1-spec.json`). They also target the round-14 patterns those seats are told to reuse. Nothing was executed. The only commands run were reads: `git show`, `git log`, `sha256sum`.

## Pinned facts (read, not exercised)

- HEAD and round-15 baseline: `cc2168325768d5356a82c039dcdf787377c55784` (`census/round-15/claims.json`).
- Census `tools/souji-census.sh` sha256: the working tree and `cc21683` are identical at `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`.
- Pre-harm census at `a31642d`: `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`. This equals `BASELINE_SHA` at `tests/fixtures/r14-census-boundary.py:61` and the closure's baseline digest (`corpus/lessons/round-14-verifier-spotcheck.md:102`).
- r14 namespace fixture `tests/fixtures/r14-census-boundary.py` sha256: working tree and `cc21683` are identical at `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`. Its IDs `R14C2-01..12` are literal at lines 45-58.

## Findings

### G1 — A declared record can be fabricated and still pass. The claim must be scoped (calibration, blocker for wording)

**Counterexample.** The contract says "No command execution of recorded commands." So the checker sees only text in the JSON. A hand-written record can contain these lines and pass every rule the contract lists:
- `TOOL\t…\tsha256=<baseline>` followed by the expected `CASE … FAIL` lines;
- an installed arm with `CASE … PASS` and `SUMMARY total=N failed=0`;
- the r14 arm with 12×PASS.

The digests of the real tool and fixture bytes can be recomputed from `--root` and copied into the record. Any stdout digest is just as easy to forge.

**Evidence.** The round-14 closure already rules on this: "Matching declared bytes cannot establish a past execution, authenticated author, or omitted dependency set" (`round-14-verifier-spotcheck.md:115`).

**Impact.** Calibration. Admitting C2 as "rejects fabricated evidence" would be false provenance.

**Smallest safe correction.**
- Phrase C2 as: "rejects missing, green-only, weakened, inconsistent or mismatched *declared* paired records."
- The checker's success line should say `declared-record consistency; not execution proof`.
- Authenticity comes only from L1 running `census/round-15/run-verification.py` once, with an exclusively created output file. The checker checks shape; the run carries provenance.

### G2 — Weakened controls stay green on both arms; preservation rows are author-declared (calibration + operability, blocker)

**Counterexample.** With baseline `cc21683` (the harmed tool), the design gives three kinds of rows:
- **Unsafe-value / refusal-retained rows** (e.g. a hostile `core.fsmonitor` or `core.hooksPath` value): already refused at `cc21683`, so they should PASS on both arms.
- **Benign-preservation rows** (the subject of C1).
- **Namespace rows.**

Take a ConfigFixture whose unsafe-value case bodies were weakened to always pass, for example by asserting only exit≠0 rather than "no hook executed / no forbidden access". It produces exactly the same declared record as a strong fixture. Nothing in the pair can discriminate it.

The benign rows have a second problem. Their "PASS" compares the installed output against rows the fixture author wrote. A changed tool that emits *different* rows from the previously supported tool still turns green, as long as the author's expectation matches it. Q22 forbids that kind of evidence: "authored capability rows … do not satisfy this criterion" (`census/round-15/lesson-draft.md:52`). The closure grounded the harm in the *pre-r14* tool's behaviour (`spotcheck:104`, baseline lines 12-18 and 127-137).

**Contract conflict.** The Q22 draft test reads "baseline must be red for the protection row and unchanged for the preservation rows" (`lesson-draft.md:54`). That describes a *pre-harm* baseline (`a31642d`). RoundRunner extracts only `cc21683`. Against `cc21683` the polarity flips: preservation rows are red and protection rows are green. So the round can satisfy neither Q22 nor a discriminating test for its unsafe controls.

**Smallest safe correction.** Add a third arm: run the *same* `r15-census-config.py` command with `--tool <git show a31642d:tools/souji-census.sh>`. The checker then pins a literal per-ID matrix:

| row class | a31642d (pre-harm) | cc21683 (harmed) | installed |
|---|---|---|---|
| benign / mixed-fleet preservation | PASS (rows = prior supported output) | FAIL (refusal/abort, harm detail) | PASS |
| unsafe-value refusal-retained | FAIL where the pre-r14 tool observably reads or executes (access detail) | PASS | PASS |
| r14 namespace fixture (separate command) | already recorded 2/12 (r14) | — | 12/12 |

**[INFERENCE]** Some unsafe rows may not be observably red at `a31642d`. Those IDs must be listed literally as `non-discriminating` in the checker and excluded from any "discriminated" count, never silently counted. If the third arm is refused, the green→green rows must be labelled zero-discrimination controls in the C2 claim.

### G3 — Runner-declared `matched` / `expected_exit` let an expectation fit whatever was observed (calibration, blocker)

**Evidence.** In r14, `run()` writes `expected_exit=expected, matched=code == expected` (`census/round-14/run-verification.py:44-45`). Its "red-before" check counts any exit 1 as red (`:71`) and never inspects stdout. The overall verdict is `all(x["matched"] …)` (`:92`).

**Counterexample.** A record whose baseline result says `exit_code: 0, expected_exit: 0, matched: true` is internally consistent but green-only. So is a baseline exit 1 caused by a *positive-control* failure, or by an access-free FAIL.

**Correction.**
- The checker ignores every `matched`, `expected_exit` and summary/boolean field in the record.
- It recomputes everything from literal expectations plus parsed `TOOL`, `CASE` and `SUMMARY` lines.
- It requires exit/summary consistency:
  - exit 1 ⇔ `failed>0` and at least one FAIL line;
  - exit 0 ⇔ `failed=0` and every line PASS;
  - `total` = number of CASE lines;
  - `failed` = number of FAIL lines.
- Exit 2, negative/timeout exits, and stderr containing `ROUND15_OUTER_TIMEOUT` (an analogue of r14 `:43`) are never red. They make the record rc 1 (honest failure) or rc 2. The closure precedent is that exit-2 setup failures are "not counted as baseline red proof" (`spotcheck:102`).

### G4 — Real execution can still produce green-only evidence through subset selection (operability + calibration)

**Evidence.** In r14, `--case` replaces the selection (`r14-census-boundary.py:674`). The id-set check runs only `if not args.case` (`:722`). Repeated `--case X --case X` runs a duplicate. `--list` exits 0 with no CASE lines (`:669-672`).

**Counterexample.** If ConfigFixture copies this pattern, then `--tool installed --case <one benign id>` *genuinely* prints `SUMMARY total=1 failed=0`, exit 0. The baseline arm with `--case <unsafe id>` genuinely exits 0 as well. Both are real executions and both are green-only.

**Correction.**
- The checker parses `command` argv and rejects:
  - any `--case` or `--list`;
  - any argument other than exactly `--tool <path>`;
  - a fixture path other than `tests/fixtures/r15-census-config.py` (or `r14-census-boundary.py` for the namespace arm).
- It requires the CASE sequence to equal the checker's own literal ordered tuple, with no duplicates, no extras, no `CASE\tid-set\tFAIL`, and `SUMMARY total=<len(literal)>`.
- The case IDs are never read from the record or from the fixture's `EXPECTED_IDS`. Either source would be circular.
- Both config arms must carry the identical fixture digest and identical argv apart from the `--tool` value.

### G5 — Baseline red must be the *harm*, not some other failure (calibration)

**Counterexample.** Suppose `strace` is missing, or a spy fails. The baseline FAIL lines then read `setup: …` or `access: …` for unrelated reasons. The record is still "red", but it does not show that `cc21683` refused a benign config.

**Correction.**
- ConfigFixture should emit a stable harm token in FAIL detail, e.g. `harm: exit=2 expected=0` or `harm: rows-missing=<ids>`.
- For unsafe controls, the PASS detail should carry the observed refusal (e.g. `ok refused=<finding>`) rather than bare `ok`, which is the r14 pattern at `:720`.
- Per-ID, the checker requires the harm token for every literal baseline-red benign ID, and `refused=` for every unsafe ID on the installed arm.
- A red set *smaller* than the literal set is a weakened pair and gives rc 1. A *larger* one (a benign control failing on the installed arm, or an unexpected baseline FAIL) is a mismatch and also gives rc 1.

### G6 — Binding the TOOL line to the arms (identity; overlaps CheckerBindings, noted only for green-only)

Each arm's `TOOL` line sha256 must equal its literal:
- baseline: `fcff8b05…` for `cc21683`, recomputable via `git show <commit>:tools/souji-census.sh`;
- pre-harm: `6a000c59…`;
- installed: sha256 of `<root>/tools/souji-census.sh` at check time, which must equal the record's installed digest.

The namespace arm's fixture digest must equal `e6a984b1…`. The task says "unchanged r14 namespace fixture", and editing that fixture would be a way to weaken the 12/12. Reject a record where the baseline TOOL digest equals the installed one.

The record's `measured_commit` should equal `git -C root rev-parse HEAD`, or the commit that contains the record. Without that, an old green record can be replayed against new installed bytes.

### G7 — The checker's own controls must cover rejection and admission (operability)

A checker that rejects everything trivially "rejects green-only". `--selftest` must include **one admitted positive control**: a well-formed paired record built in-process, which must exit 0. Each of these mutations of it must also be checked; the expected rc is given for each.

| mutation | expected rc |
|---|---|
| baseline arm removed | 1 |
| baseline exit 0 with all PASS | 1 |
| baseline exit 2 / timeout | 1 or 2 per contract, never 0 |
| one benign ID PASS on baseline (weakened red) | 1 |
| unsafe `refused=` token removed | 1 |
| `--case` in argv | 1 |
| duplicate, renamed or extra ID | 1 |
| `SUMMARY` inconsistent with CASE lines | 2 |
| exit inconsistent with summary | 2 |
| `matched:true` contradicting the parsed output | 1, field ignored |
| fixture digest differs between arms | 2 |
| baseline TOOL digest = installed digest | 2 |
| namespace 11/12, or namespace arm missing | 1 |
| r14 fixture digest ≠ `e6a984b1…` | 2 |
| record-supplied `expected_ids` that differ from the literal list | 2 |

These three negatives are required by `lesson-draft.md:47`: only-green outputs, a weakened expected value, and a missing benign control.

The checker's result must not be stored *inside* the record it checks (RoundRunner runs "C2 selftest/external checker" in the same run). Run it after the exclusive create, and record its output in a separate result or file.

## Exact acceptance needed once the sources land (L1 only; not run here)

1. `python3 tools/souji-preservation-evidence.py --selftest` returns exit 0, and its output lists the positive control plus every negative in G7.
2. Against L1's exclusively created `census/round-15/verification*.json`, running `python3 tools/souji-preservation-evidence.py --record <that> --root /home/vgpnk/Projects/shokunin/souji-shokunin` returns exit 0.
3. Against the same record with the baseline result deleted (a copy in `/var/tmp`), the same command returns rc ≠ 0.
4. Source check: the literal ID tuples are in the checker and not read from record or fixture, and there is no `subprocess` call on any recorded `command`.
5. Wording check: the C2 claim and the checker output carry the "declared-record consistency, not execution proof" scope (G1).
6. The decision on G2 is recorded: either a third `a31642d` arm, or an explicit label that the unsafe controls are zero-discrimination.

## Unrun checks
Everything above. No fixture, checker, runner, selftest, shellcheck or census was executed. No tools were installed.

## Boundary disclosure (per SoujiR15 no-query reminder; not repeated after it)
- `grep` pattern `(?i)preservation.?evidence|green.?only|red.?green` with path = whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, recursive. That traversal covered `census/` and so queried `census/operator-sweep-20261019/`. It returned no match from that directory, and I did not open, copy, cite or use any of its contents.
- `read` of the lane root directory listing. It showed the names of the `census/` child directories, including the operator-sweep name, and nothing more.
- Shell commands that read digests and git state, which are not runtime tests:
  - `sha256sum tests/fixtures/r14-census-boundary.py tools/souji-census.sh`;
  - `git show cc21683:<same two files> | sha256sum`;
  - `git show a31642d:tools/souji-census.sh | sha256sum`;
  - `git status --short -- tools tests census/round-15`;
  - `git diff --stat a31642d cc21683 -- tools/souji-census.sh`;
  - `git log --oneline -8`, `git rev-parse HEAD`, `git cat-file -t cc21683…`.
  
  These read the census tool and the fixture only, never the operator sweep. If seat policy counts them as probes, treat the pinned digests in this report as unverified and re-derive them in L1 acceptance.
- Limitation: the findings are unaffected. They rest on explicitly named source lines.
