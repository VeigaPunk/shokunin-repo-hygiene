# NoHarm — Round 14 W1 Connector Report

**Seat:** `SoujiR14.NoHarm` (connector, leaf)  
**Lane:** `souji-shokunin` (`/home/vgpnk/Projects/shokunin/souji-shokunin`)  
**Axes:** calibration, operability  
**Role:** UFO-FSD connector — bounded synthesis connecting source correction, cache integrity, and census boundary to no-harm conditions; enumeration of supported legacy invocation preservation checks and explicit nonclaims.

---

## 1. Tooling Directive & Evidence Separation

### 1.1 Tool Installs and Upgrades
- **Installed or upgraded tools:** None. All required tools (`bash`, `python3`, `git`, `readlink`, `realpath`, `strace`, `shellcheck`, `grep`, `awk`) are already installed on the host.
- **Privilege/channel actions:** None taken.

### 1.2 Code and Document Inspection vs. Exercised Evidence
- **Exercised evidence:** **None.** Under the leaf-seat contract, this seat ran zero builds, tests, linters, formatters, selftests, or smoke runs. No live census, no credential-path access, and no real `~/.omp/agent/` access were performed.
- **Code and document inspection:**
  - `corpus/QUALITY.md`: criteria Q1–Q19, with particular focus on Q6 (measured digests / author fragments), Q17 (contained regular non-symlink files), Q18 (separation of integrity gate from tool safety), and Q19 (bounded operations / non-regular file refusal / fail-closed diagnostics).
  - `SCORECARD.md`: calibration, operability, coverage definitions and round-13/14 baseline scores.
  - `PROVINCE.md`: domain scope, refusal of credentials and operator-tooling runtime, refusal to execute deletion without certified receipts.
  - `corpus/SOURCES.md`: rows S001–S037, specifically S034 and the pending S038 correction.
  - `tools/souji-census.sh`: full read of baseline snapshot `#5156` (827 lines).
  - `census/round-13/run-verification.py`: full read of lines 1–138 (specifically lines 31–36 and 48–54 retention branch).
  - `corpus/lessons/round-13-verifier-spotcheck.md`: spotcheck finding 3 (retention caveat).
  - Peer reports in `.ufo/waves/round-14/w1/`:
    - `BoundaryReviewRoot.md`, `BoundaryReviewScratch.md`, `BoundaryReviewCompare.md`, `BoundaryReviewGit.md`
    - `SafetyCredential.md`, `SiblingOverlap.md`
    - `CacheReviewSchema.md`, `CacheReviewPaths.md`, `FixtureCacheAudit.md`, `FixtureBoundaryAudit.md`
    - `CachePrecedent.md`, `RetentionAttack.md`, `ProtocolEvidence.md`, `GateRegistry.md`, `Bookkeeping.md`, `SourceLedger.md`.

---

## 2. Declared Axes

The round evaluates two declared axes, while holding the third constant:

1. **Calibration (Score 7, Delta 0 proposed):**
   - *Goal:* Digest-bound evidence-cache eligibility; stale or legacy retained green results must never be reused; per-result measured revisions remain explicit; strict separation between evidence integrity and tool safety/execution proof.
   - *Harm Condition to Avoid:* Laundering stale or modified results through blind retention; claiming that cache eligibility proves historical command execution; claiming that a passing integrity gate grants deletion authority.
2. **Operability (Score 8, Delta 0 proposed):**
   - *Goal:* Census refuses credential-store roots, ancestors, descendants, and aliases before any enumeration or filesystem content read; synthetic fixture distinguishes baseline from installed tool without live credential access; clean fleet census operations remain fully operational.
   - *Harm Condition to Avoid:* Breaking legitimate fleet census workflows (default root, `--root`, `--include-root`, `--compare`, `--selftest`); altering TSV column schemas; leaking temp files; failing open on unreadable baselines; hanging on FIFOs.
3. **Coverage (Score 8, Neutral / Unchanged):**
   - *Harm Condition to Avoid:* Claiming frontier promotion or coverage score increases on pure source corrections or unadmitted knowledge entries.

---

## 3. Connecting the Round 14 Triad to No-Harm Conditions

The round’s technical work consists of three tightly coupled elements:
1. **Source Correction:** S034 locator errata corrected by S038.
2. **Cache Integrity (C1):** `tools/souji-evidence-cache.py` and `tests/fixtures/r14-evidence-cache.py`.
3. **Census Boundary (C2):** `tools/souji-census.sh` and `tests/fixtures/r14-census-boundary.py`.

### 3.1 Source Correction (S034 → S038)
- **Observed Defect in S034:**
  `corpus/SOURCES.md` S034 cited `/usr/share/info/coreutils.info.gz` node "timeout invocation" § 23.6 with lines 15316–15317 for `--kill-after` and line 15349 for exit 124. In the installed vendor coreutils 9.11-2 documentation:
  - Heading § 23.6 begins at line 15286.
  - Option header `-k/--kill-after` is at 15317–15318, and the KILL sentence is at lines **15319–15320** (a +3 line offset).
  - Exit 124 is defined at line **15365**; line 15349 is actually `-v` (verbose diagnostics).
  - Furthermore, S034's teaches cell asserted: *"interruption can leave operation residue and does not authorize deletion"*. That statement is a valid lane lesson inference, but it does **not** appear in the vendor documentation.
- **No-Harm Connection:**
  - *Immutability:* S034 remains byte-identical and immutable in historical registry rows; S038 is appended as a new row superseding S034's locators only (`corpus/SOURCES.md` append-only rule).
  - *Provenance Integrity:* S038 restricts its teaches cell strictly to vendor-grounded claims (timeout exits 124 without `--preserve-status`; `--kill-after` sends secondary KILL). The lane's deletion-safety inference is detached and attributed to lane lessons.
  - *Calibration:* Accurately locates primary vendor evidence without creating URL duplication warnings (W04).

### 3.2 Cache Integrity (C1)
- **Observed Defect in Round 13:**
  In `census/round-13/run-verification.py:48–54`, `--retry-failed` reused any test result where `matched: true` in the prior run without inspecting file bytes, tool digests, or git revisions. As demonstrated in `RetentionAttack.md` (CE-1) and `CachePrecedent.md`, `evidence-frozen` was retained from commit `6ed10a7` even after `tools/souji-cert-evidence.py` had been edited and re-hashed at commit `6f8ee0f`.
- **C1 Implementation:**
  `tools/souji-evidence-cache.py` evaluates `{name, matched, measured_commit, dependencies: {relative-path: sha256}}` against `--root DIR`. It exits 0 only when all dependencies match disk SHA-256 digests, `matched` is true, and the record is well-formed.
- **No-Harm Connection:**
  - *No False Green:* Stale or modified files fail closed (exit 1 `stale/failed`), preventing recurrence of CE-1.
  - *No Over-Strictness (Negative Control):* An unchanged dependency must remain reusable (exit 0) when unrelated files in the repository are modified. If modifying an unrelated file invalidated the cache, caching utility would be destroyed, harming operability.
  - *Explicit Revision Preservation:* The record's original `measured_commit` is echoed verbatim; it is never overwritten with the current git revision.
  - *Disclaimed Execution:* Output explicitly states: *"No proof of actual historical execution"*.

### 3.3 Census Boundary (C2)
- **Observed Defect in Baseline Census:**
  `tools/souji-census.sh` had zero checks against credential-store roots, ancestors, descendants, or symlink aliases. Furthermore, as revealed by `BoundaryReviewRoot.md`, `BoundaryReviewScratch.md`, and `BoundaryReviewCompare.md`:
  - `--compare` loaded and read baseline files before validating `--root`.
  - Linked-worktree registrations (`git worktree list --porcelain`) were passed directly to `git status`, which hashes tracked files whose stat drifted (accidental content reads of secrets).
  - `mktemp` in `emit_compare` used `${TMPDIR:-/tmp}`, violating Q4 and risking disk residue.
- **C2 Implementation:**
  `tools/souji-census.sh` enforces pre-enumeration refusal on `--root`, `$SHOKUNIN_ROOT`, `--compare`, child directories, and worktree gitdirs overlapping the credential store (`$HOME/.omp/agent` and passwd-home `/.omp/agent`).
- **No-Harm Connection:**
  - *Pre-Access Refusal:* The guard halts execution with exit 2 and a stable finding ID before any `git`, `find`, `du`, `stat`, or content read.
  - *Legacy Operability Preserved:* Clean fleet repos produce identical 7-column TSV outputs; valid comparisons produce identical 5-column diff TSVs; exit codes (0 clean, 3 diff) are preserved.
  - *Q4 Conformance:* Compare buffers and selftest scratch paths are pinned to `/var/tmp` with cleanup traps, eliminating `/tmp` residue.

---

## 4. Grounding in QUALITY Criteria (Q6, Q17, Q18, Q19)

| Criterion | Mandate | Application to Round 14 | No-Harm Boundary |
|---|---|---|---|
| **Q6** | A verdict names the sha256 of the bytes it measured; each certifier writes its own fragment; candidate-selection exercises the class under test. | C1 cache records explicitly bind relative dependency paths to their measured sha256 digests. Scribe and reviewer seats author separate fragments without shared writable relays. | Cache eligibility confirms declared byte identity against current disk bytes. It does **not** substitute for running the candidate-selection suite or proving the tested class passed. |
| **Q17** | A claimed fixture or evidence fragment must resolve to a contained regular, non-symlink file at the measured revision; prose naming a fixture is not a substitute for the file. | C1 rejects symlink dependencies (`dependency-symlink`), directory escapes (`dependency-escape`), and missing files (`dependency-missing`). C2 skips child symlinks and refuses root symlinks resolving into protected stores. | Prevents symlink redirection from bypassing integrity checks or pulling external secrets into the dependency tree. Fails closed on any non-regular file. |
| **Q18** | Certification integrity and tool safety are separate verdicts. A passing integrity gate never grants deletion authority; evidence must name installed digest, author fragment, command, exit status, and tested class. | C1 is an evidence integrity gate, NOT an authorization engine. C2 is an input refusal guard, NOT a tool deletion certification. Certification remains **OFF**. | A passing cache eligibility check (exit 0) or boundary refusal (exit 2) grants zero live deletion authority. Receipts remain advisory. S038 citation accuracy does not expand operational authority. |
| **Q19** | Supersedes Q8's marker counting: per-target moves and digest readers are bounded; special files refuse; failed or timed-out operations emit diagnostics and fail closed. | C1 lstats dependencies and refuses FIFOs/devices before `open()`, preventing hangs. C2 refuses protected paths before spawning `find` or `git`. Both use timeout bounds (per S038 coreutils timeout exit 124). | Operations are behaviorally enforced rather than grep-counted. A stalled or FIFO dependency emits a diagnostic and exits 2, never blocking the runner indefinitely. |

---

## 5. Enumeration of Supported Legacy Invocation Preservation Checks

To ensure that the C2 boundary guard does not harm existing automated fleet operations, the following legacy invocation patterns of `tools/souji-census.sh` must be verified by L1 as preserved:

1. **Default Zero-Argument Fleet Scan:**
   - *Command:* `tools/souji-census.sh`
   - *Behavior:* Uses `SHOKUNIN_ROOT` (or parent of `REPO_ROOT`); enumerates immediate child repositories; emits 7-column census TSV to stdout; exits 0.
   - *Preservation Check:* Must scan all sibling workspace repositories without tripping false-positive boundary refusals; output must be byte-identical to baseline.
2. **Explicit Directory Root Scan (`--root`):**
   - *Command:* `tools/souji-census.sh --root /path/to/fleet` and `tools/souji-census.sh --root=/path/to/fleet`
   - *Behavior:* Scans specified root directory; emits 7-column census TSV to stdout; exits 0.
   - *Preservation Check:* Both `--root DIR` (space-separated) and `--root=DIR` (equals-separated) syntax forms must remain supported and functionally identical.
3. **Include Root Option (`--include-root`):**
   - *Command:* `tools/souji-census.sh --root /path/to/repo --include-root`
   - *Behavior:* Evaluates the target root itself as a main repository (if it contains a valid `.git` directory) alongside its children; emits corresponding row; exits 0.
   - *Preservation Check:* `--include-root` must continue to evaluate the root repository when safe, but refuse if the root itself is a credential store or symlink into one.
4. **Baseline Comparison (`--compare`):**
   - *Command:* `tools/souji-census.sh --compare PREV.tsv` and `tools/souji-census.sh --root DIR --compare PREV.tsv`
   - *Behavior:* Loads `PREV.tsv`; executes census on current root; emits 5-column diff TSV (`repo field before after change`) to stdout; exits 0 if no diff, exits 3 if differences exist.
   - *Preservation Check:* Valid baseline TSVs must produce accurate differential diffs. Malformed baselines (bad header, empty file, short row) must exit 2 with clean stderr diagnostics and zero stdout pollution.
5. **Combined Options:**
   - *Command:* `tools/souji-census.sh --root DIR --compare PREV.tsv --include-root`
   - *Behavior:* Correctly combines root override, root inclusion, and baseline comparison.
   - *Preservation Check:* Argument order independence must be preserved; all flags compose without parse collisions.
6. **Built-in Hermetic Selftest (`--selftest`):**
   - *Command:* `tools/souji-census.sh --selftest`
   - *Behavior:* Builds synthetic fixture fleet under `/var/tmp`; executes two successive census runs; verifies byte-identical determinism; mutates one fixture; verifies `--compare` diff and exit 3; cleans up scratch directory; exits 0 on pass, 1 on fail.
   - *Preservation Check:* Must continue to exit 0. Must use `/var/tmp` exclusively (eliminating legacy `${TMPDIR:-/tmp}` fallback).
7. **Output Channel and Stream Purity:**
   - *Behavior:* Stdout is strictly reserved for machine-readable TSV data (census rows or diff rows). Stderr is reserved for diagnostics, warnings, and usage errors.
   - *Preservation Check:* On usage error or boundary refusal, help text or finding strings must NEVER be printed to stdout. Pipelined consumers (`tools/souji-census.sh | awk ...`) must not receive corrupt text.
8. **Output Schema Invariance:**
   - *Census TSV Header:* `repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags` (7 columns).
   - *Compare TSV Header:* `repo\tfield\tbefore\tafter\tchange` (5 columns).
   - *Preservation Check:* No columns added, removed, reordered, or renamed. Valid verdict flags (`clean`, `dirty`, `unpushed`, `no-remote`, `scratch`, `secret-shaped`, `wt-absent`, `wt-dirty`, `status-unverifiable`, `not-a-repo`, `error`) maintain exact spellings.

---

## 6. Enumeration of Explicit Non-Claims

To maintain calibration and prevent over-claiming, the lane explicitly records four non-claims:

1. **Non-Claim 1: Cache Eligibility is NOT Historical Execution Proof.**
   - A clean exit 0 from `tools/souji-evidence-cache.py` verifies only that the recorded dependency files exist on disk and match their declared SHA-256 digests at `measured_commit`.
   - It does **not** prove that the underlying command was ever executed on the host, does not prove runtime environmental purity, and does not capture undeclared external dependencies (such as system binaries, kernel state, or network endpoints).
2. **Non-Claim 2: Integrity Verification & Boundary Refusal are NOT Tool Deletion Certification.**
   - Tool Certification remains strictly **OFF**.
   - Neither `souji-evidence-cache.py` nor `souji-census.sh` authorizes live deletion or quarantine cleanup. Receipts generated by `souji-verify` or `souji-census` remain purely advisory until full defect-class re-certification suites are executed in future rounds (Q18).
3. **Non-Claim 3: Credential-Store Boundary Refusal is NOT Comprehensive Secret Redaction.**
   - The C2 boundary guard refuses traversal of designated credential-store roots (`$HOME/.omp/agent` and passwd-home `/.omp/agent`) and their symlink/commondir aliases.
   - It does **not** certify that the scanned repositories are free of secret entropy, does not scan for exposed API keys in arbitrary files, and does not replace the domain authority of `kagi-shokunin`.
4. **Non-Claim 4: Source Locator Correction (S038) is NOT Frontier Coverage Promotion.**
   - S038 corrects line locators for GNU timeout in coreutils 9.11-2 and untangles vendor facts from lane policy inferences.
   - It does **not** expand PROVINCE core or frontier scope, does not promote new knowledge entries, and leaves the coverage score unchanged at 8.

---

## 7. The Proposed Move: Tri-State Exit Decoupling with Symmetric Pre-Enumeration Boundary Guard

### 7.1 Synthesis Across Round 14 Proposals
A critical contradiction emerged between the C1 cache proposals and the C2 census proposals:
- *In C1:* Reviewers (`CacheReviewSchema`, `CacheReviewPaths`) and critics (`RetentionAttack`, `CachePrecedent`) noted that an ambiguous exit-code mapping between "stale dependency" and "refused/malformed input" would cause test runners (like `run-verification.py --retry-failed`) to treat security or boundary refusals as normal test failures, triggering infinite retries or invalid re-executions.
- *In C2:* Reviewers (`BoundaryReviewRoot`, `BoundaryReviewCompare`, `BoundaryReviewGit`, `BoundaryReviewScratch`) demonstrated that `souji-census.sh` read `--compare` before root validation, hashed tracked secrets during `git status`, and leaked temporary files in `${TMPDIR:-/tmp}`.

### 7.2 The Non-Obvious Move
Synthesize a **Unified Fail-Closed Boundary Architecture with Tri-State Exit Decoupling**:

```
                       Input Path / Evaluation Request
                                     │
                                     ▼
                     [Tier 1: Lexical Normalization]
                     - Absolute path resolution (realpath -m -s)
                     - Lexical '..' traversal & component check
                     - Refuse if path overlaps protected set
                                     │
                                     ▼
                     [Tier 2: Canonical Verification]
                     - Canonical resolution (readlink -m, fail-closed)
                     - Refuse if canonical path overlaps protected set
                     - Refuse symlink aliases into protected set
                                     │
                                     ▼
                     [Tier 3: Invariant Evaluation]
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
      Exit 0                      Exit 1                      Exit 2
  [Clean / Reusable]        [Operational Drift]         [Contract Violation]
- All deps match sha256    - Dependency digest drift   - Protected path overlap
- Matched is true          - Prior matched: false      - Symlink / path escape
- Unchanged deps reusable  - Compare diff detected     - Non-regular file (FIFO)
  (negative control)         (census exit 3)           - Malformed JSON / dup keys
```

#### Exact Rules of the Move:
1. **Strict Tri-State Exit Decoupling:**
   - `Exit 0`: Reusable / Clean. In C1, dependencies match disk digests; in C2, census scan completed without error.
   - `Exit 1`: Operational Divergence / Stale. In C1, a declared dependency has drifted in hash (valid candidate for rerun); in C2, git unpushed/dirty counts are non-zero.
   - `Exit 2`: Contract Refusal / Could-Not-Evaluate. Boundary violation, protected path overlap, symlink escape, non-regular file (FIFO/device), duplicate JSON keys, or malformed revision.
   - **Crucial Invariant:** Exit 1 must NEVER be returned for a boundary refusal or malformed input. This prevents any outer retry runner from misclassifying a security violation as an eligible rerun candidate.
2. **Symmetric Protected Boundary Enforcement:**
   - Both C1 and C2 derive their protected boundary from the union of `$HOME/.omp/agent` and the real passwd-home `$(getent passwd "$(id -u)" | cut -d: -f6)/.omp/agent`.
   - In C1: `--root` and any dependency path resolving into this set exits 2 (`dependency-protected`).
   - In C2: `--root`, `$SHOKUNIN_ROOT`, `--compare`, child repositories, and worktree gitdirs resolving into this set exit 2 (`protected-path`).
3. **Hermetic `/var/tmp` Buffer Management:**
   - Replace the legacy `${TMPDIR:-/tmp}` compare buffer at `souji-census.sh:418` with an explicit `/var/tmp` mktemp wrapped in an `EXIT INT TERM` cleanup trap, or capture census output in an in-memory bash variable, guaranteeing zero disk residue on failure.
4. **Tracked Secret Pathspec Exclusion in Census:**
   - In `souji-census.sh:count_dirty`, add pathspec exclusions (`:(exclude,glob)**/.env*`, `:(exclude,glob)**/credential*`, etc.) to prevent `git status --porcelain` from hashing tracked secret files when file mtimes drift.

### 7.3 Second-Order Effects
- **Runtime Surface:** Outer test harnesses and verification runners branch cleanly on exit 2 without hanging or looping. Child processes (`find`, `du`, `git`) are never spawned against denied paths.
- **Contract Surface:** Upholds `PROVINCE.md:30–31` (refusal of credentials) without expanding Souji into secret management (`kagi-shokunin`'s domain). Satisfies QUALITY Q4, Q16, Q17, Q18, Q19.
- **Substrate Surface:** Pinned scratch allocation under `/var/tmp` prevents `/tmp` quota exhaustion (r8 lesson) and forbids `/dev/shm` (Q16). Host `~/.omp/agent/` remains completely untouched.
- **Verification Surface:** Fixtures using synthetic HOME under `/var/tmp` and command spies can reliably prove that zero unauthorized commands are executed before refusal occurs.

### 7.4 Contradictions and Risks
- **Contradiction 1: Synthetic Test HOME vs. Host Security:**
  Synthetic test fixtures require setting `HOME=/var/tmp/...` to verify boundary refusals. A naive check against `$HOME` alone would leave the real host credential store exposed during operator runs.
  *Resolution:* The protected set evaluates the union of `$HOME/.omp/agent` and passwd-home `/.omp/agent`.
- **Contradiction 2: Compare Header Gate vs. Content Access:**
  In baseline census, `load_census` checked the compare header after opening and reading the file.
  *Resolution:* The lexical and canonical boundary guard executes before `[ -f "$COMPARE" ]` and before opening the file descriptor.
- **Contradiction 3: Retrying Runners vs. Stale Green:**
  If a runner re-evaluates dependency digests at *retain* time from current disk bytes rather than comparing against the recorded baseline, the check becomes vacuous.
  *Resolution:* The cache tool strictly compares recorded dependency digests against current disk bytes, failing closed if the record lacks dependencies.

---

## 8. Final L1 Commands (For Main Agent Verification)

The following commands are identified for the L1 integrator to run after all executor seats land their files. No checks were run mid-flight by this leaf seat.

```bash
# -----------------------------------------------------------------------------
# Stage 1: Syntax & Compilation Verification
# -----------------------------------------------------------------------------
python3 -m py_compile tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py
bash -n tools/souji-census.sh

# -----------------------------------------------------------------------------
# Stage 2: Static Boundary & Hygiene Checks
# -----------------------------------------------------------------------------
# Q4 / Q16: Verify scratch isolation (expect 0 hits for /tmp and /dev/shm)
grep -c 'TMPDIR:-/tmp' tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py
grep -c '/dev/shm' tests/fixtures/r14-evidence-cache.py tests/fixtures/r14-census-boundary.py tools/souji-evidence-cache.py
# Q18: Verify no subprocess/eval execution in cache gate (expect 0 hits)
grep -nE 'subprocess|os\.system|eval\(|exec\(|shell=True' tools/souji-evidence-cache.py || true

# ShellCheck warning level on census script (expect exit 0)
shellcheck -S warning tools/souji-census.sh

# -----------------------------------------------------------------------------
# Stage 3: C1 Evidence Cache Selftest & External Fixtures (Calibration)
# -----------------------------------------------------------------------------
# Run embedded selftest (expect exit 0)
python3 tools/souji-evidence-cache.py --selftest; echo "c1_selftest_rc=$?"

# Run external discriminating fixture (expect exit 0)
python3 tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py; echo "c1_fixture_rc=$?"

# Run red-arm baseline discrimination test (expect exit 1 with tool-missing)
python3 tests/fixtures/r14-evidence-cache.py --tool /var/tmp/nonexistent-cache-tool || true

# -----------------------------------------------------------------------------
# Stage 4: C2 Census Boundary Selftest & External Fixtures (Operability)
# -----------------------------------------------------------------------------
# Run built-in census selftest (expect exit 0)
TMPDIR=/var/tmp bash tools/souji-census.sh --selftest; echo "c2_selftest_rc=$?"

# Run external census boundary fixture on baseline (expect exit 1, red for right reason)
git show a31642d:tools/souji-census.sh > /var/tmp/souji-census.baseline.sh
python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-census.baseline.sh; echo "baseline_red_rc=$?"
rm -f /var/tmp/souji-census.baseline.sh

# Run external census boundary fixture on installed tool (expect exit 0)
python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh; echo "c2_fixture_rc=$?"

# -----------------------------------------------------------------------------
# Stage 5: Legacy Invocation Preservation Check (Operability Invariance)
# -----------------------------------------------------------------------------
# Verify clean fleet census matches expected 7-column schema on synthetic fleet
TMPDIR=/var/tmp bash tools/souji-census.sh --root /home/vgpnk/Projects/shokunin | head -n 5

# -----------------------------------------------------------------------------
# Stage 6: Sources Registry Validation & Scratch Cleanup Check
# -----------------------------------------------------------------------------
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji

# Verify zero leftover scratch directories under /var/tmp (expect 0)
ls -d /var/tmp/*souji* /var/tmp/*r14* 2>/dev/null | wc -l
```

---

## 9. Residual Risk & Verification Gaps

1. **Unlanded Executor Artifacts:**
   At the time of this inspection, `tools/souji-evidence-cache.py`, `tests/fixtures/r14-evidence-cache.py`, and `tests/fixtures/r14-census-boundary.py` were not yet committed to the working tree. All analysis and requirements herein represent design contracts and invariant constraints derived from `w1-spec.json`, baseline code, and sibling review reports.
2. **Inherent Kernel Alias Detection Limits:**
   Path-based lexical and canonical checks cannot detect hardlinks or bind mounts pointing directly to protected inodes without `stat`'ing the protected target. The C2 boundary guard relies on link-count validation (`st_nlink == 1`) on the compare path and strict path containment on roots.
3. **transitive Dependency Incompleteness:**
   As noted in `RetentionAttack.md` (CE-4), C1 cache eligibility verifies declared dependencies only. Transitive dependencies (e.g. scripts invoked by test runners or external binaries) must either be explicitly declared in the record or marked non-cacheable.
