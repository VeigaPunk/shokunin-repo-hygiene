# ClaimSeparation — Causal Independence of C1/C2 & Lowest Calibration Obligation

**Seat**: `SoujiR14.ClaimSeparation` (UFO-FSD connector, leaf seat)  
**Lane**: `/home/vgpnk/Projects/shokunin/souji-shokunin`  
**Round**: 14 (wave `w1`)  
**Axes Judged**: `calibration` (lowest score: 7), `operability` (score: 8)  
**Evidence Class**: Code and document inspection only. No builds, tests, linters, formatters, or smoke runs executed by this seat. Zero tool installs/upgrades. Zero access to credential stores or operator sweeps.

---

## 1. Executive Summary & Axis Identification (Godspeed Step 1: Name the Axes)

The round targets two coupled yet distinct failure modes inherited from round 13:
1. **Axis: Calibration (Score: 7 / 10; lowest non-retired axis; delta: 0)**
   - **Scope (C1)**: Digest-bound evidence-cache eligibility (`tools/souji-evidence-cache.py`, `tests/fixtures/r14-evidence-cache.py`, `census/round-14/cache-demonstration.py`).
   - **Target Defect (R14-M1)**: `census/round-13/run-verification.py:49-54` blindly retained prior green test runs on `--retry-failed` if `matched == True`, without verifying whether underlying tool bytes, test fixtures, or dependent inputs had changed.
   - **Calibration Mandate**: Declared verdicts must reflect actual measured reality. Stale/legacy retained green must fail closed (not reusable); per-result measured revisions (`measured_commit`) must remain explicit and unlaundered.
   - **Boundary & Non-Claims**: Proving dependency byte matching on disk is **not** proof of historical execution, **not** deletion certification, and **not** comprehensive defect-class coverage. Certification remains **OFF**. Score delta is strictly **0**.

2. **Axis: Operability (Score: 8 / 10; saturation line: 8; delta: 0)**
   - **Scope (C2)**: Pre-access credential-store boundary refusal in the metadata census (`tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`).
   - **Target Defect (R14-M3)**: Arbitrary `--root`, `--compare`, child symlinks, or linked worktrees in `tools/souji-census.sh` can overlap credential-store paths (`~/.omp/agent`, `$HOME/.omp/agent`, etc.), causing `find`, `du`, `git`, or shell `read` to stat, walk, or hash files in forbidden trees.
   - **Operability Mandate**: Pre-access lexical-first and canonical refusal before any filesystem stat, traversal, or content read occurs. Unsafe paths exit 2 with stable finding `protected-path refused`. Normal fleet census operations on legitimate repo roots remain 100% preserved. Score delta is strictly **0**.

3. **Axis: Coverage (Score: 8 / 10; not judged in r14; delta: 0)**
   - Kept byte-identical to round 13 baseline (`31984f4 → 6f8ee0f`). Baseline has 37 source rows (S001..S037), 5 admitted knowledge entries, 1 F2 entry. S038 is an append-only source locator correction for S034; no new ground entry or SKILL promotion is admitted.

---

## 2. Rigorous Test of Causal Independence (C1 vs. C2)

To evaluate whether C1 and C2 are truly independent claims or entangled sub-features, we test causal independence across substrate, failure modes, and second-order interaction surfaces.

### 2.1 Substrate & Language Runtime Surface
- **C1 Substrate**: Pure Python 3 stdlib (`os`, `sys`, `json`, `hashlib`, `pathlib`, `re`). Evaluates structured JSON records against local file sha256 digests. Spawns no external subprocesses, executes no git commands, and performs no filesystem directory sweeps.
- **C2 Substrate**: Pure POSIX/Bash with GNU coreutils and git (`readlink`, `du -sb -P`, `find`, `git status`, `git worktree list`). Inspects filesystem directories, worktrees, and repository object stores.
- **Conclusion**: The execution substrates and runtime dependencies are disjoint.

### 2.2 Failure-Mode Decoupling (Truth Table)

| Scenario | C1 (Evidence Cache) | C2 (Census Boundary) | Joint Feasibility & Mechanism |
|---|---|---|---|
| **Case A** | **PASS** | **FAIL** | **Feasible**: `souji-evidence-cache.py` correctly verifies dependency digests and rejects stale records. Concurrently, `souji-census.sh` lacks boundary guards and allows `--root ~/.omp/agent` to traverse credentials. C1 succeeds while C2 fails. |
| **Case B** | **FAIL** | **PASS** | **Feasible**: `souji-census.sh` enforces pre-access lexical/canonical guards and passes all boundary spy tests. Concurrently, `souji-evidence-cache.py` fails open on empty dependencies or fails to preserve `measured_commit`. C2 succeeds while C1 fails. |
| **Case C** | **FAIL** | **FAIL** | **Feasible**: Neither tool implements its respective hardening, reproducing R14-M1 and R14-M3 simultaneously. |
| **Case D** | **PASS** | **PASS** | **Target State**: Both tools pass their isolated self-tests, fixtures, and regression suites independently. |

Statistical and logical causality: $P(\text{C1 Pass} \mid \text{C2 Pass}) = P(\text{C1 Pass})$. The physical logic of digest caching does not depend on census boundary scanning.

### 2.3 Second-Order Coupling Vectors (The Hidden Traps)

Although runtime execution is decoupled, deep second-order interactions exist at the contract and verification boundary:

1. **Coupling Vector 1 — Verifier-Subject Circularity (Calibration Risk)**:
   In `census/round-14/verification.json`, the execution of C2 (`tests/fixtures/r14-census-boundary.py`) is itself an artifact recorded in the evidence cache. If the test runner reuses a cached green result for C2 when `tools/souji-census.sh` has been edited, a broken C1 invalidates the integrity of C2! C2's reported pass is only as credible as C1's cache invalidation.
2. **Coupling Vector 2 — Credential Traversal via C1 Dependency Injection (Operability/Contract Risk)**:
   `souji-evidence-cache.py` takes `--root DIR` and `dependencies: {relative-path: sha256}`. The lane contract explicitly dictates:
   > *"Never open, copy, query, **hash**, quarantine, or modify anything under ~/.omp/agent/ EXCEPT reading RULES.md and skills; never launch omp CLI."*  
   Notice the word **hash**. If C1 accepts an arbitrary `--root` (e.g. `~/.omp/agent`) or resolves escaping dependency paths (`../../.omp/agent/auth.json`) or symlinks into the credential store and computes their sha256 digests, **C1 violates the zero-credential-access contract directly**! C1 must therefore implement the exact same pre-access containment invariant that C2 implements.
3. **Coupling Vector 3 — Scalar Score Laundering**:
   If L1 attempts to synthesize C1 and C2 into a single composite score bump (e.g., claiming calibration 8 because both landed), it introduces a false causal linkage between a verification gate (C1) and a domain tool (C2).

---

## 3. The Lowest Calibration Obligation

Calibration is scored at **7** in `SCORECARD.md` (the lowest non-retired score in the lane; operability is 8, coverage is 8, saturation line is 8).

### 3.1 Why Calibration is 7
- In round 9, verdict tools were patched (S17), but 16 open defect classes remained.
- In round 11, certification evidence was compromised (shared relay, verdicts on non-installed bytes).
- In round 13, declared-evidence validation (`souji-cert-evidence.py`) verified declared fragments, but explicitly noted: *"labels/coverage/execution remain unproved and certification OFF"*.
- In round 13's closure spotcheck, `census/round-13/run-verification.py:49-54` was found to retain green results without verifying dependency hashes (R14-M1).

### 3.2 The Four Inviolable Calibration Obligations for Round 14

1. **Obligation 1: Strict Zero Score Delta (Delta = 0)**:
   C1 introduces an evidence-cache eligibility check. Proving that dependency files on disk match a declared sha256 digest is **not** proof that:
   - The recorded command was actually run historically;
   - The recorded output was produced by that command;
   - Tool safety or deletion authorization is granted (deletion stays OFF);
   - Outside non-author closure has sampled and verified the round.
   Claiming a score of 8 would be a textbook calibration failure (overclaiming). Calibration **must remain 7**.
2. **Obligation 2: Per-Result Measured Revision Preservation**:
   When an evidence cache record measured at commit $A$ is deemed eligible while the repository is at commit $B$, the record must explicitly preserve `measured_commit: A`. It must **never** launder the revision to $B$.
3. **Obligation 3: Fail-Closed on All Degenerate Records**:
   Any record with missing dependencies, empty dependencies `{}`, `matched: false`, malformed sha256, path escape, symlink, or duplicate JSON keys must exit 1 (stale/failed) or 2 (malformed/could-not-evaluate). It must **never** return exit 0 (reusable).
4. **Obligation 4: Separation of Inspection from Execution**:
   Every finding derived from reading code without execution must be marked `[INFERENCE]` or `to-verify`. Unexercised code must not be scored.

---

## 4. Exact Before-After Counts and Falsifiers (No Inflated 0–10 Scores)

### 4.1 Quantitative Comparison Tables

#### Table 1: C1 Calibration Axis Metrics

| Metric | Baseline (`a31642d`) | Target Round 14 | Delta | Source / Command |
|---|---|---|---|---|
| **Cache Gate Binary** | Absent (`0`) | Present (`1`) | `+1` | `test -f tools/souji-evidence-cache.py` |
| **Eligibility Verification** | None (`0`) | Active (`1`) | `+1` | `python3 tools/souji-evidence-cache.py --selftest` |
| **Stale Green Reuse on Modified Tool** | Permitted (`1` — false pass) | Refused (`0` — fail closed) | `-1` | `census/round-14/cache-demonstration.py` |
| **Legacy / Empty Dependencies Handling** | Passed as green (`1`) | Refused exit 2 (`0`) | `-1` | `tests/fixtures/r14-evidence-cache.py` |
| **Preserved Measured Revision** | Unchecked | Explicitly preserved | `—` | Pinned JSON output assertion |
| **Historical Execution Claimed** | False (`0`) | False (`0` — explicit non-claim) | `0` | Header and output contract |
| **Calibration Score** | **7** | **7** | **0** | `SCORECARD.md` |

#### Table 2: C2 Operability Axis Metrics

| Metric | Baseline (`a31642d`) | Target Round 14 | Delta | Source / Command |
|---|---|---|---|---|
| **Pre-Access Boundary Guard** | Absent (`0`) | Present (`1`) | `+1` | `grep -n 'boundary_guard' tools/souji-census.sh` |
| **Traversal on `--root ~/.omp/agent`** | Allowed (stats/walks) | Refused (exit 2) | `-1` | `tests/fixtures/r14-census-boundary.py` |
| **Content Read on `--compare <cred_path>`** | Allowed (`[ -f ]` + read) | Refused (exit 2 before read) | `-1` | `tests/fixtures/r14-census-boundary.py` |
| **Symlinked Child `.git` into Credential Store** | Followed (reads repo) | Refused / skipped | `-1` | `tests/fixtures/r14-census-boundary.py` |
| **Command Spy Hits on Forbidden Paths** | $>0$ calls on baseline | Exactly `0` calls | All eliminated | Synthetic HOME `/var/tmp` command spy |
| **Normal Fleet Census Regression** | Clean | Clean (byte-identical) | `0` | Baseline fixture control comparison |
| **Operability Score** | **8** | **8** | **0** | `SCORECARD.md` |

---

### 4.2 Discriminating Falsifiers & Expected Behavior

Each claim is governed by an explicit falsifier that discriminates passing implementations from flawed or unhardened variants:

| ID | Claim | Test Condition / Input | Baseline Behavior (`a31642d`) | Changed Target Behavior | Expected Exit & Finding |
|---|---|---|---|---|---|
| **F-C1-01** | Stale-Green Invalidation | Valid record whose dependency file on disk has modified bytes | Reused prior green result (`matched: true`) | Re-computes sha256, detects mismatch, refuses reuse | Exit `1`, finding `dependency-digest-mismatch` |
| **F-C1-02** | Legacy Record Refusal | Record omitting `dependencies` key entirely | Blindly retained as reusable | Fails closed as legacy | Exit `2`, finding `legacy-no-dependencies` |
| **F-C1-03** | Empty Dependency Refusal | Record with `dependencies: {}` | Vacuously reused as green | Fails closed (empty dependency set cannot prove state) | Exit `2`, finding `dependencies-empty` |
| **F-C1-04** | Failed Record Ineligibility | Record with `matched: false` but matching digests | Reused if name matched | Refuses reuse of non-passing test | Exit `1`, finding `record-not-matched` |
| **F-C1-05** | Symlink Dependency Refusal | Record whose dependency points to a symlink | Follows symlink and hashes target | Refuses symlink before hashing | Exit `2`, finding `dependency-symlink-refused` |
| **F-C1-06** | Escape Path Refusal | Dependency path with `../` escaping `--root` | Opens relative to root | Rejects lexical escape before filesystem touch | Exit `2`, finding `dependency-path-escape` |
| **F-C1-07** | Duplicate JSON Key Refusal | JSON with duplicate `"tools/x": "..."` keys | Silently keeps last key | `object_pairs_hook` rejects duplicate keys | Exit `2`, finding `duplicate-json-key` |
| **F-C1-08** | Revision Format Validation | `measured_commit` not 40-char lowercase hex | Accepted verbatim | Validates commit format | Exit `2`, finding `commit-format-invalid` |
| **F-C1-09** | Negative Control | Dependency bytes unchanged, unrelated file in repo modified | Passes | Stays reusable (not over-strict) | Exit `0`, `reusable: true`, `measured_commit` preserved |
| **F-C2-01** | Direct Root Refusal | `--root $HOME/.omp/agent` (synthetic) | Enumerates directory, runs `find`/`git` | Refuses before `[ -d ]` or `readlink` | Exit `2`, finding `protected-path refused: root` |
| **F-C2-02** | Ancestor Root Refusal | `--root $HOME` (synthetic) | Globs children, descends toward credentials | Refuses ancestor root before glob | Exit `2`, finding `protected-path refused: ancestor` |
| **F-C2-03** | Compare Symlink Refusal | `--compare symlink -> cred.tsv` | `load_census` reads file contents | Refuses compare path before `[ -f ]` or `read` | Exit `2`, finding `protected-path refused: compare` |
| **F-C2-04** | Child Symlink `.git` Refusal | Child repo with `.git -> cred_dir` | Runs `git -C` through symlink | Skips or refuses candidate before git call | Exit `0` (or `2`), zero git spy hits on cred path |
| **F-C2-05** | Linked Worktree Refusal | Admin `gitdir` pointing into credential store | Runs `git status` on worktree path | Canonicalizes and refuses before `git status` | Flagged `wt-refused`, zero git spy hits |
| **F-C2-06** | Safe Fleet Control | Normal repo without credential paths | Emits 7-column TSV | Emits identical 7-column TSV | Exit `0`, clean census |

---

## 5. The One Non-Obvious Move (Compatible Synthesis Across Round Proposals)

### 5.1 The Synthesis Tension
Reviewing the round 14 proposals reveals two critical design vulnerabilities:
1. **The Verification Disconnect (`RetentionAttack` vs. `CacheGate`)**:
   `CacheGate` implements `tools/souji-evidence-cache.py` as a standalone CLI. However, if the round's actual verification runner (`run-verification.py`) does not call `souji-evidence-cache.py` to evaluate prior results, **stale-green recurrence (R14-M1) is not prevented in the verification harness itself**! A standalone gate that is not wired into the verification pipeline is merely an ornamental fixture.
2. **The Credential Hashing Backdoor (`CacheReviewPaths` vs. `BoundaryReviewRoot`)**:
   `souji-evidence-cache.py` takes `--root DIR` and reads dependency files. If C1 does not enforce credential-boundary checks, an evidence record can declare dependencies pointing into `~/.omp/agent/`. Computing sha256 digests over credential files breaches the zero-access contract.

### 5.2 The Proposed Move: Dual-Tiered Pre-Access Containment Invariant with Fail-Closed Call-Site Dependency Enforcing

We synthesize the C1 and C2 proposals into a unified containment architecture that resolves both vulnerabilities without cross-substrate coupling:

```
[ External Invocation / CLI ]
       │
       ├── C1 (tools/souji-evidence-cache.py): Python Stdlib
       │     ├── 1. Lexical Root Guard: Reject --root overlapping ~/.omp/agent or $HOME/.omp/agent
       │     ├── 2. Lexical Key Guard: Reject absolute paths, "..", empty parts, non-canonical UTF-8
       │     ├── 3. Descriptor Walk (dir_fd / O_NOFOLLOW): Reject symlinks & hardlinks before open
       │     └── 4. Digest Verification: Match sha256; exit 0/1/2 with stable finding IDs
       │
       └── C2 (tools/souji-census.sh): Bash / Coreutils / Git
             ├── 1. Lexical Input Guard: Reject --root / --compare matching credential patterns
             ├── 2. Canonical Guard (readlink -m): Reject aliases & ancestor overlaps before stat/git
             ├── 3. Traversal Defense: Skip repo-root symlinks; refuse linked worktree gitdir escapes
             └── 4. Read-Only Census: Execute git/find/du on legitimate repos only; exit 0/1/2/3
```

#### Key Architecture Components:
1. **Upstream Lexical Boundary Guard in C1 (Calibration + Operability)**:
   `souji-evidence-cache.py` adopts C2's strict pre-access boundary rule. Before resolving or hashing any dependency, it validates that:
   - `--root` does not lexically or canonically overlap `$HOME/.omp/agent`, `~/.omp/agent`, or passwd-home;
   - Dependency keys do not escape root (`..`), are not absolute, and are not symlinks.
   *Effect*: C1 cannot be weaponized to hash or touch credential files.
2. **Mandatory Explicit Dependency Manifests in Verification Harness (Calibration)**:
   In `run-verification.py`, the blind `if PREVIOUS and name not in RETRY_NAMES` check is replaced by an invocation of `tools/souji-evidence-cache.py`:
   - Every verification test item declares its exact dependencies in `verification.json` (e.g. `{"tools/souji-cert-evidence.py": "<sha256>", "tests/fixtures/r13-cert-evidence.py": "<sha256>"}`).
   - If `souji-evidence-cache.py` returns exit 0, the result is retained with explicit `measured_commit`.
   - If it returns exit 1 or 2 (or if dependencies are undeclared), the harness fails closed and forces re-execution.
   *Effect*: R14-M1 is eradicated from the live verification runner.
3. **Strict Causal Independence via Disjoint Verification Surfaces**:
   Despite sharing the containment invariant conceptually, C1 and C2 remain strictly decoupled in code, tests, and execution. C1 does not call `souji-census.sh`, and C2 does not call `souji-evidence-cache.py`.

### 5.3 Second-Order Effects & Trade-Off Analysis
- **Axis Improvements**:
  - `calibration`: Improves by eliminating stale-green reuse in both the standalone tool and the live verification harness, while guaranteeing explicit `measured_commit` preservation.
  - `operability`: Improves by preventing credential file hashing through C1 dependency parsing and credential traversal in C2 census scanning.
  - `coverage`: Zero harm; remains unchanged at 8.
- **Risks & Mitigations**:
  - *Risk*: A test with undeclared runtime dependencies might be cached when it should re-run.  
    *Mitigation*: Fail-closed rule. Any test lacking an explicit, non-empty dependency dictionary in `verification.json` is ineligible for caching and must always re-run.
  - *Risk*: Pre-access boundary checks on `--root` could reject valid nested subdirectories in synthetic test environments.  
    *Mitigation*: Pre-access boundary checks resolve against the explicit synthetic `$HOME` under `/var/tmp` during fixture runs (`SOUJI_CENSUS_SELFTEST_ACTIVE=1`).

---

## 6. Verification & Final L1 Commands

The following commands are identified for L1 to execute once all assigned executor seats (`CacheGate`, `CensusBoundary`, `RetentionRunner`, etc.) land. **This seat did not run any of these commands.**

```bash
# 1. Syntax, Lint, and Compile Gates
TMPDIR=/var/tmp python3 -m py_compile tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py
bash -n tools/souji-census.sh
shellcheck -S warning tools/souji-census.sh

# 2. C1 Evidence-Cache Gate & Fixture Verification
TMPDIR=/var/tmp python3 tools/souji-evidence-cache.py --selftest
# Expect exit 0, all named finding IDs matching specification

TMPDIR=/var/tmp python3 tests/fixtures/r14-evidence-cache.py
# Expect exit 0, all discriminating falsifiers (F-C1-01 through F-C1-09) passing

# 3. C2 Census Boundary Fixture Verification (Baseline Red vs Changed Green)
# Baseline Red (using baseline a31642d copy under /var/tmp):
TMPDIR=/var/tmp python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-census.baseline.sh
# Expect exit 1 (Red: command spy detects forbidden access on protected cases)

# Changed Green (installed tool):
TMPDIR=/var/tmp python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
# Expect exit 0 (Green: zero command spy hits on protected cases; clean controls pass)

# 4. C2 Tool Self-Test & Regression Verification
TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
# Expect exit 0, legacy fleet metadata format byte-identical

# 5. Regression Verification Across Prior Round Gates
python3 tools/souji-cert-evidence.py --selftest                        # Expect 36/36
python3 tests/fixtures/r13-cert-evidence.py                           # Expect 5/5
bash tests/fixtures/r13-quarantine-bounds.sh                          # Expect 5/5
bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh  # Expect 5/5
bash tests/fixtures/r12-maintenance-guard.sh --selftest               # Expect 6/6

# 6. Hygiene & Residue Checks
ls -d /var/tmp/*r14* /var/tmp/*census* 2>/dev/null | wc -l            # Expect 0 (clean scratch)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status -s         # Verify only approved paths staged
```

---

## 7. Code Inspection vs. Exercised Evidence

Per the lane contract and RULES.md, code and document inspection is strictly separated from exercised evidence:

| Item | Method | Status | Findings / Result |
|---|---|---|---|
| `SCORECARD.md` | Document Inspection | Read lines 1–85 | Identified scores (7/8/8), saturation line (8), planned round 14/15 text |
| `corpus/QUALITY.md` | Document Inspection | Read lines 1–120 | Evaluated Q4 (/var/tmp scratch), Q6/Q18 (certification separation), Q17 (contained fixtures) |
| `corpus/lessons/round-14.md` | Document Inspection | Read lines 1–34 | Analyzed R14-M1 (stale green), R14-M2 (S034 locator drift), R14-M3 (census boundary) |
| `tools/souji-census.sh` | Code Inspection | Read 827 lines (tag `#5156`) | Identified complete absence of credential boundary checks in baseline tool |
| `census/round-13/run-verification.py` | Code Inspection | Read lines 1–138 | Pinpointed lines 49–54 as causal source of R14-M1 stale-green reuse |
| `census/round-14/claims.json` | Document Inspection | Read lines 1–19 | Confirmed declared C1/C2 claims and zero score delta |
| Peer W1 Reports (`CacheReviewSchema`, `BoundaryReviewRoot`, `SourceLedger`, etc.) | Document Inspection | Read 8 peer reports | Extracted schema checklist, spy requirements, and path traversal vulnerabilities |
| Tool / Fixture Execution | **Exercised Evidence** | **NONE** | No builds, tests, linters, formatters, or smoke runs were executed by this seat |
| Protected Store Access | **Exercised Evidence** | **NONE** | Zero reads, queries, hashes, or copies of `~/.omp/agent/` (except RULES.md) or operator sweeps |

---

## 8. Tool Installs / Updates Record

In accordance with the operator tooling directive (2026-10-19):
- **Tools Installed / Upgraded**: None.
- **Reason**: All tasks performed by this seat were read-only document and code analysis and synthesis. Existing environment utilities (`git`, `read`, `write`, `grep`, `glob`) were sufficient.
- **Channel**: N/A.

---

## 9. Final Conclusion

1. **C1 and C2 are causally independent in execution substrate and failure mechanisms**, but share a vital second-order contract constraint: **neither tool may open, traverse, or hash paths in the credential store**.
2. **The lowest calibration score (7) obligates a zero score delta (delta = 0)**. Proving dependency digest equality eliminates stale green retention, but does not prove historical execution, environment invariance, or deletion safety.
3. **The recommended synthesis** applies a pre-access lexical containment guard across both C1 and C2, and wires C1's eligibility check into the verification harness to guarantee that R14-M1 cannot recur in practice.
