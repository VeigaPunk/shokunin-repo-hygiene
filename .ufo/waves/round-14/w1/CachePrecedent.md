# CachePrecedent — Round 13 Retention Branch & Prior Spotcheck Caveat Analysis

Seat: `SoujiR14.CachePrecedent` (scout, leaf member).
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axes: calibration, operability.
Scope: source inspection of `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/run-verification.py` retention branch and `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-13-verifier-spotcheck.md` spotcheck retention caveat. Identification of exact failure precondition and causal red-before test. Own report only.

---

## 1. Executive Summary

In Round 13, `census/round-13/run-verification.py` introduced a `--retry-failed` mode to avoid repeating successful checks across verification attempts. While designed to accelerate test passes, the mechanism had no dependency tracking, recorded no dependency digests, and evaluated retention eligibility solely on whether a check had `matched: true` in `census/round-13/verification.json`.

During Round 13 closure, the non-author verifier (`corpus/lessons/round-13-verifier-spotcheck.md:132`) issued a critical caveat:
> "3. **Retention caveat, not a current claim failure:** the runner's retained-green selection does not itself compare tool digests before retaining an old observation. This closure checked unchanged files and the sole production-irrelevant parser delta directly. Actual per-result revisions plus the report's explicit retained-run disclosure are authoritative; top-level measured_commit must not erase them."

This report establishes:
1. The exact structural failure precondition under which Round 13's retention branch accepts stale, broken, or laundered green results.
2. The empirical manifestation in Round 13 where `evidence-frozen`, `historical-replay-wrong-bytes`, and `historical-replay-candidate` were retained from commit `6ed10a7` even though their underlying tool (`tools/souji-cert-evidence.py`) had been modified and re-hashed at commit `6f8ee0f`.
3. The specification of the causal red-before test required for Round 14's C1 gate (`tools/souji-evidence-cache.py` / `tests/fixtures/r14-evidence-cache.py`) to discriminate sound digest-bound retention from vulnerable Round 13 retention.

---

## 2. Code Inspection of Round 13 Retention Branch

### 2.1 Implementation in `census/round-13/run-verification.py`

Inspection of `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/run-verification.py`:

- **Lines 31–36 (Selection Logic):**
  ```python
  PREVIOUS = json.loads(OUTPUT.read_text()) if "--retry-failed" in sys.argv else None
  PREVIOUS_RESULTS = {item["name"]: item for item in PREVIOUS["results"]} if PREVIOUS else {}
  RETRY_NAMES = {name for name, item in PREVIOUS_RESULTS.items() if not item["matched"]}
  if "quarantine-bounds" in RETRY_NAMES:
      # The fixture itself changed: repeat the paired baseline with identical new bytes.
      RETRY_NAMES.add("quarantine-red-before")
  ```
- **Lines 48–54 (Retention Branch):**
  ```python
  def run(name, command, expected=0, seconds=120):
      if PREVIOUS and name not in RETRY_NAMES:
          retained = dict(PREVIOUS_RESULTS[name])
          retained["measured_commit"] = retained.get("measured_commit", PREVIOUS["measured_commit"])
          retained["retained_from"] = "census/round-13/verification-attempt-1.json"
          print(f"{name}: retaining prior exercised result at {retained['measured_commit']}", flush=True)
          return retained
  ```
- **Lines 80–87 & 126–134 (Commit Stamping & Verification Envelope):**
  ```python
  revision = git("rev-parse", "HEAD")
  ...
  record = dict(round=13, measured_commit=revision, baseline_commit=BASE,
                recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                installed_sha256=after, artifacts_unchanged_during_run=before == after,
                results=results, sources=census, admitted_entries=admitted,
                prior_attempt="census/round-13/verification-attempt-1.json" if PREVIOUS else None,
                deletion_certification="OFF", scope="Declared integrity and bounded fixtures; no complete class-suite certification")
  ```

### 2.2 Observed Architectural Flaws

1. **Blind Reuse without Digest Comparison:**
   `run()` evaluates eligibility solely with `name not in RETRY_NAMES`. It performs zero `stat` or `sha256` comparisons on the command binary, arguments, scripts, fixtures, or runtime inputs.
2. **Ad-hoc Coupling vs Systematic Dependencies:**
   Lines 34–36 contain a single hardcoded coupling: `if "quarantine-bounds" in RETRY_NAMES: RETRY_NAMES.add("quarantine-red-before")`. Every other test in the suite is treated as isolated and zero-dependency.
3. **Absence of Dependency Metadata:**
   The results schema in `census/round-13/verification.json` records `{name, command, exit_code, expected_exit, matched, stdout, stderr, seconds, measured_commit}`, but completely lacks a `dependencies` dictionary mapping relative file paths to their expected sha256 digests.
4. **Historical Manifestation in Round 13 Artifacts:**
   Inspection of `census/round-13/verification-attempt-1.json` (commit `6ed10a7`) vs `census/round-13/verification.json` (commit `6f8ee0f`):
   - At `6ed10a7`, `tools/souji-cert-evidence.py` had sha256 `a029aaa0a604fb53dfcba650f95b3626d543890bd1d96110d2340cd30144ece1`.
   - In attempt 1, `evidence-frozen`, `historical-replay-wrong-bytes`, and `historical-replay-candidate` passed (`matched: true`).
   - Between `6ed10a7` and `6f8ee0f`, `tools/souji-cert-evidence.py` was altered to fix an underscore regex bug in its finding id parser. Its sha256 became `943d664c5df4e795c23821892a1691847772e95ef36752d532f5cbeff0e544d4`.
   - In attempt 2 (`run-verification.py --retry-failed`), because `evidence-frozen` was not in `RETRY_NAMES`, the runner blindly reused the result from attempt 1 (`6ed10a7`).
   - The test was NEVER executed against the newly installed `tools/souji-cert-evidence.py` (`943d664...`).
   - While the non-author closure reviewer confirmed after the fact that the parser delta was production-irrelevant, the mechanism itself was unsafe. If `tools/souji-cert-evidence.py` had suffered a breaking corruption, `evidence-frozen` would still have been published as green!

---

## 3. The Outside Spotcheck Retention Caveat

Inspection of `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-13-verifier-spotcheck.md`:

- **Section 5 (Routed findings), Item 3 (Line 132):**
  The outside reviewer identified that the runner's retained-green selection is ungrounded because it does not bind observations to tool digests:
  - "the runner's retained-green selection does not itself compare tool digests before retaining an old observation."
  - "This closure checked unchanged files and the sole production-irrelevant parser delta directly."
  - "Actual per-result revisions plus the report's explicit retained-run disclosure are authoritative; top-level measured_commit must not erase them."
- **Core Lesson for Round 14:**
  A retained green is only valid if and only if every artifact, tool, and fixture file it touches has an identical sha256 digest at the current commit. Without explicit, cryptographically bound dependency assertions, `--retry-failed` is an uncalibrated shortcut that creates false negatives for regressions.

---

## 4. Exact Failure Precondition

Formally, the failure precondition under which Round 13's retention logic fails is defined by the conjunction of four conditions:

Let:
- $T$ be a test registered in the verification suite.
- $\text{Cmd}(T) = [c_0, c_1, \dots, c_k]$ be the command line executed for $T$.
- $\text{Deps}(T) = \{p_1, p_2, \dots, p_m\}$ be the true set of filesystem dependencies read or executed by $T$ (executable scripts, libraries, test fixtures, input manifests).
- $R_0(T)$ be the prior recorded execution record of $T$ at commit $C_0$, containing `matched: true`.
- $C_1$ be a subsequent commit where the suite is executed with `--retry-failed` against prior records $R_0$.

**The exact failure precondition is:**
1. **Prior Green State:**
   $$R_0(T).\text{matched} == \text{True}$$
2. **Underlying Dependency Mutation:**
   $$\exists p \in \text{Deps}(T) \quad \text{such that} \quad \text{sha256}(p \text{ at } C_1) \ne \text{sha256}(p \text{ at } C_0)$$
   (or $p$ is deleted, renamed, or made non-regular).
3. **Defect Introduction:**
   The change to $p$ causes $T$ to fail ($T \text{ at } C_1 \implies \text{exit} \ne \text{expected\_exit} \lor \text{matched} == \text{False}$).
4. **Digest-Agnostic Decision:**
   The runner evaluates retention solely via $T \notin \text{RETRY\_NAMES}$ (i.e. $R_0(T).\text{matched} == \text{True}$) without verifying:
   $$\forall p \in \text{Deps}(T), \quad \text{sha256}(p \text{ at } C_1) == \text{expected\_sha256}(p)$$

**Failure Consequence:**
When conditions (1)–(4) hold, the verification runner:
- Suppresses execution of $T$.
- Carries forward $R_0(T)$ into $C_1$'s verification manifest.
- Attests that the tree at $C_1$ is verified green, masking a confirmed defect in $p$.
- Erases the causal connection between the measured code bytes and the test verdict.

---

## 5. Causal Red-Before Test

To prove the defect in the legacy Round 13 logic and verify the correction in Round 14's C1 gate (`tools/souji-evidence-cache.py`), a causal red-before test must be established.

### 5.1 Test Topology & Scenarios

The test uses an isolated synthetic environment under `/var/tmp` (complying with QUALITY Q4 and Q16):

```
/var/tmp/souji-r14-precedent-fixture.<id>/
├── tools/
│   └── probe.sh            (the tool under test)
├── tests/
│   └── fixture.txt         (input data)
└── record.json             (the prior verification record)
```

#### Case 1: Drifted Tool Digest (Stale-Green Refusal)
- **Initial State ($C_0$):**
  `tools/probe.sh` has content `echo "ok"; exit 0`.
  Digest: $H_0 = \text{sha256}(\text{tools/probe.sh})$.
  Record:
  ```json
  {
    "name": "probe-test",
    "matched": true,
    "measured_commit": "c000000000000000000000000000000000000000",
    "dependencies": {
      "tools/probe.sh": "H0"
    }
  }
  ```
- **Mutation ($C_1$):**
  `tools/probe.sh` is mutated to broken code: `echo "syntax error"; exit 1`.
  Digest on disk becomes $H_1 \ne H_0$.
- **Vulnerable Round 13 Baseline Behavior:**
  Input `record.json` has `matched: true`. The Round 13 runner (`run-verification.py --retry-failed`) executes:
  `if PREVIOUS and name not in RETRY_NAMES: return retained`
  **Outcome:** Returns 0 (retained green). The broken tool is declared PASS. **RED (Defect Demonstrated)**.
- **Round 14 C1 Gate Behavior (`souji-evidence-cache.py`):**
  Command: `python3 tools/souji-evidence-cache.py --root <dir> --record record.json`
  Evaluator hashes `tools/probe.sh` on disk, detects $H_1 \ne H_0$.
  **Outcome:** Exits 1 (`stale/failed`) with stable finding id `dependency-digest-mismatch`. Refuses reuse. **GREEN (Sound Calibration)**.

#### Case 2: Legacy Record without Dependencies (Fail-Closed)
- **Input Record:**
  `record.json` matches Round 13's actual results structure (has `name`, `matched: true`, `measured_commit`, but NO `dependencies` key or empty `{}`).
- **Vulnerable Round 13 Baseline Behavior:**
  Retains and reuses unconditionally.
- **Round 14 C1 Gate Behavior:**
  Fails closed. Exits with non-zero exit code (1 or 2) and named stable finding id `legacy-no-dependencies` or `missing-dependencies`.

#### Case 3: Prior Unmatched Record (`matched: false`)
- **Input Record:**
  `matched: false`, even if `dependencies` hashes match current disk bytes.
- **Round 14 C1 Gate Behavior:**
  Exits 1 (`stale/failed`) with named stable finding id `record-not-matched`.

#### Case 4: Non-regular / Symlink / Traversal Dependency
- **Input Record:**
  Specifies dependency `../outside.txt`, a symlink `tools/link.sh`, or a non-regular file.
- **Round 14 C1 Gate Behavior:**
  Fails closed before reading. Exits 2 (`could-not-evaluate`) with named stable finding id (`dependency-symlink`, `dependency-traversal-escape`, `dependency-not-regular`).

---

## 6. Code Inspection vs. Exercised Evidence

In accordance with leaf agent rules, lane boundaries, and QUALITY standards:
- **Code Inspection (Performed):**
  - Read and analyzed `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/run-verification.py` lines 1–138.
  - Read and analyzed `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-13/verification-attempt-1.json` and `verification.json`.
  - Read and analyzed `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-13-verifier-spotcheck.md` (specifically line 132).
  - Read and analyzed `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-13.md` and `corpus/QUALITY.md`.
- **Exercised Evidence (None):**
  - No build, test, fixture, CLI, or runner was executed during this session.
  - No temporary directories under `/var/tmp` or `/tmp` were created.
  - No git commands modifying repo state were invoked.
  - No protected paths (`census/operator-sweep-*`, `~/.omp`, credentials) were accessed.
- **Tool Installs / Updates:**
  - None performed; standard file tools (`read`, `grep`, `glob`, `write`) only.

---

## 7. Recommendations for Round 14 Implementation

1. **For `SoujiR14.CacheGate` (`tools/souji-evidence-cache.py`):**
   - The CLI must enforce: `--root DIR --record JSON`.
   - Record schema must strictly require `dependencies: {relative-path: sha256}` where each hash is `[0-9a-f]{64}`.
   - Reject duplicate keys using `json.loads(..., object_pairs_hook=...)`.
   - Reject legacy records (missing or empty `dependencies`) fail-closed.
   - Enforce exact exit codes:
     - `0`: Reusable (dependencies match disk hashes, `matched: true`).
     - `1`: Stale / failed (digest mismatch, `matched: false`).
     - `2`: Malformed / could-not-evaluate (syntax error, missing file, symlink, path traversal, non-regular file, protected path).
   - Preserve `measured_commit` verbatim from the input record; never overwrite with the current git revision.
   - Output must explicitly include the disclaimer: "No proof of actual historical execution".
2. **For `SoujiR14.RetentionRunner` (new Round 14 verification runner):**
   - Must invoke `souji-evidence-cache.py` to evaluate eligibility for every retained check.
   - If `souji-evidence-cache.py` exits non-zero, the check MUST be re-executed.
   - Unpack individual check results with their original `measured_commit` preserved.
3. **For `SoujiR14.FinalEvidencePlan`:**
   - Incorporate the red-before causal test cases into the final evidence plan.

---

## 8. Final L1 Commands (For Main Agent Verification)

Commands to be run by the main agent (L1) from `/home/vgpnk/Projects/shokunin/souji-shokunin` after all executor seats land:

```sh
# 1. Syntax & compilation check of C1 tool and fixture
python3 -m py_compile tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py

# 2. Execute C1 gate selftest (isolated under /var/tmp)
python3 tools/souji-evidence-cache.py --selftest; echo "selftest_exit=$?"

# 3. Execute C1 black-box fixture with discriminating positive/negative controls
python3 tests/fixtures/r14-evidence-cache.py; echo "fixture_exit=$?"

# 4. Static assertion of safety boundaries (must return 0 matches for violations)
grep -nE 'subprocess|os\.system|eval\(|exec\(|shell=True' tools/souji-evidence-cache.py
grep -c 'TMPDIR:-/tmp' tests/fixtures/r14-evidence-cache.py         # expect 0 (Q4)
grep -c '/dev/shm' tests/fixtures/r14-evidence-cache.py             # expect 0 (Q16)

# 5. Verify git status has no stray untracked artifacts outside approved wave files
git status --porcelain
```
