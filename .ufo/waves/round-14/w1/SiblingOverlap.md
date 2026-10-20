# SiblingOverlap — Round 14 W1 Connector Report

**Seat:** `SoujiR14.SiblingOverlap` (connector, leaf)  
**Lane:** `souji-shokunin` (`/home/vgpnk/Projects/shokunin/souji-shokunin`)  
**Axes:** calibration, operability  
**Role:** UFO-FSD connector — bounded synthesis across round 14 proposals; boundary fit analysis with sibling provinces.

---

## 1. Tooling Directive & Execution Class

### Tool Installs and Upgrades
- **Installed or upgraded tools:** None. Existing system utilities and runtime environments were sufficient.
- **Privilege/channel actions:** None taken.

### Code/Document Inspection vs. Exercised Evidence
- **Exercised evidence:** **None.** In accordance with the leaf-seat contract, no builds, tests, linters, formatters, selftests, or smoke runs were executed. No live census, no credential path access, and no real `~/.omp/agent/` access were performed.
- **Code and document inspection:**
  - `souji-shokunin/PROVINCE.md` (domain, owns, refuses, core/frontier/adjacent, round 13 boundary refinement).
  - Fleet `MISSION.md` (declared fleet config, axes framework, L2 concurrency, push scope).
  - Bounded sibling provinces discovered and read:
    - `/home/vgpnk/Projects/shokunin/mori-shokunin/PROVINCE.md` (fleet observability, wave settlement, refusal of artifact cleanup/credentials).
    - `/home/vgpnk/Projects/shokunin/kagi-shokunin/PROVINCE.md` (secrets and vault ops, credential hygiene checklists, boundary partitions).
    - `/home/vgpnk/Projects/shokunin/kumitate-shokunin/PROVINCE.md` (orchestration and tooling, task/hub lifecycles, worktree locks).
  - Lane context: `souji-shokunin/AGENTS.md`, `souji-shokunin/corpus/QUALITY.md` (Q1–Q19, specifically Q4, Q6, Q8, Q14, Q16, Q17, Q18, Q19).
  - Round 14 baseline and peer reports:
    - `census/round-14/claims.json`, `census/round-14/before.json`.
    - `.ufo/waves/round-14/w1/Bookkeeping.md`, `BoundaryReviewRoot.md`, `BoundaryReviewScratch.md`, `CacheReviewSchema.md`, `FixtureCacheAudit.md`, `SourceLedger.md`.

---

## 2. Sibling Province Alignment & Boundary Fit

### 2.1 Kagi-Shokunin (Secrets & Vault Ops) — No Credential Hygiene Takeover
- **Kagi's Domain:** Owns 1Password machine-credential custody, SOPS/age key rotation, Vault/OpenBao token lifecycles, credential hygiene checklists (`checklist-run.sh`), op-reference parsing (`op-ref-probe.sh`), and secret-scanning policy.
- **Souji's Refusal (`PROVINCE.md:30-31`):** "Credentials, secrets, tokens, vault refs — kagi-shokunin's province. Souji cites paths/modes only and never reads secret content."
- **Boundary Fit in Round 14 (C2 Operability):**
  - **The Risk:** If Souji's census tool (`souji-census.sh`) attempted to scan file contents for secret entropy, parse token formats, evaluate credential validity, or manage secret lifecycles, it would commit an unconstitutional domain takeover of Kagi-shokunin.
  - **The Architectural Fit:** Souji C2 does **not** perform credential hygiene or secret inspection. Instead, Souji implements an **external pre-enumeration refusal boundary**.
  - **Mechanism:** Before any filesystem traversal, directory enumeration (`find`), disk usage query (`du`), git execution (`git status`), or comparison file read (`load_census`), `souji-census.sh` evaluates candidate roots (`--root`, `$SHOKUNIN_ROOT`), compare paths (`--compare`), child repositories, and worktree gitdirs against known credential-store namespaces (e.g. `$HOME/.omp/agent`, `$HOME/.ssh`, `$HOME/.gnupg`, `$HOME/.aws`, `$HOME/.password-store`, `$HOME/.config/the-janitor`).
  - **Refusal Contract:** When a path overlaps a protected credential-store boundary (as direct target, descendant, ancestor root, symlink alias, or worktree registration), Souji **refuses immediately with exit 2 and a stable finding ID (`protected-path-refused`)**. It never opens, reads, parses, or traverses the target.
  - **Result:** Kagi retains 100% exclusive ownership of credential detection, parsing, and hygiene. Souji acts as a strict non-interfering boundary guard that prevents its own file-system tools from ever trespassing into Kagi's domain.

### 2.2 Kumitate-Shokunin (Orchestration & Tooling) — Local Integrity vs. Fleet Dispatch
- **Kumitate's Domain:** Owns OMP task/hub orchestration, ufo-fsd runtime scripts, agent swarms, and worktree allocation/locks. `PROVINCE.md:63-64` notes: "kumitate-shokunin locks live task worktrees during dispatch; souji prunes only dead, unlocked registrations and never removes a lock it did not set."
- **Souji's Boundary Refinement (`PROVINCE.md:78-80`):** "Evidence-integrity checking is limited to souji's own receipt/certification fragments; it does not become fleet orchestration or an independent promotion authority."
- **Boundary Fit in Round 14 (C1 Calibration):**
  - **The Tool:** `tools/souji-evidence-cache.py` evaluates evidence cache records `{name, matched, measured_commit, dependencies:{relative-path: sha256}}`.
  - **No Orchestration Takeover:** The cache tool explicitly states in its output: `"No proof of actual historical execution"`. It does not execute commands, dispatch tasks, manage agent lifecycles, or replay workflows.
  - **Local Integrity Scope:** The tool performs a deterministic, read-only hash check verifying that dependencies on disk currently match the declared SHA-256 digests at `measured_commit`. If any dependency has mutated, is missing, is a symlink, escapes the root, or if `matched: false`, the record is declared stale/failed (exit 1) or malformed (exit 2).
  - **Result:** Kumitate retains full authority over task execution, scheduling, and lifecycle state. Souji provides only local cryptographic verification of its own retained artifacts, ensuring stale green receipts are not reused.

### 2.3 Mori-Shokunin (Observability) — Read-Only Observability vs. Cryptographic Hygiene
- **Mori's Domain:** Passively observes watchdog liveness, journal kill/OOM events, resource runway, and `.ufo/waves/*` settlement state (`mori-shokunin/PROVINCE.md:6-10`).
- **Mori's Adjacency Finding (`mori-shokunin/PROVINCE.md:76`):** "Souji's receipts distinguish only listed removals: the approval list records hashed aggregator-r10* artifacts and the later sweep marks those exact paths pushed. For precisely those named paths, receipts support a swept (pushed-receipt) classification; for an empty path without a matching receipt, [UNKNOWN] history, so it is not evidence of 'never written.' This is offline evidence reading, not a live census dependency."
- **Boundary Fit:** Souji's receipt records and clean census TSVs provide trustworthy, cryptographically bound evidence of disk cleanup without requiring Mori to guess whether files were removed or never written. Souji never touches system journals, cgroups, or host processes, leaving host observability strictly to Mori.

---

## 3. The Proposed Move: Unified Pre-Enumeration Boundary Invariant (PEBI)

### 3.1 Synthesis Across Round 14 Proposals
Review of the round 14 proposals reveals critical second-order boundary vulnerabilities:
1. **`BoundaryReviewRoot.md` (F2, F4, F6, F7):** `souji-census.sh` loads `--compare` before validating root; reads the file completely without boundary checks; canonicalisation fails open on error; worktree registrations reach `git status` without boundary checks; `.scratch` symlinks are stat'd through before refusal.
2. **`BoundaryReviewScratch.md` (F1, F2):** `count_dirty` in `souji-census.sh` runs `git status --porcelain`, which hashes tracked files whose mtime drifted, causing accidental openat/read of tracked secrets; linked worktree registrations reach `git status` unchecked.
3. **`CacheReviewSchema.md` & `FixtureCacheAudit.md`:** `souji-evidence-cache.py` must validate dependencies `{relative-path: sha256}` without allowing path escapes (`../`), symlinks, or non-regular files to read or hash outside `--root DIR`.
4. **`Bookkeeping.md` & `SourceLedger.md`:** Scores remain 7/8/8 (delta 0); certification remains OFF; S038 corrects S034 locators.

### 3.2 The Non-Obvious Move
Synthesize the boundary protection into an explicit, deterministic **Two-Tier Pre-Enumeration Boundary Invariant (PEBI)** shared in design across both Census (C2) and Evidence-Cache (C1):

```
       Input Path / Record
              │
              ▼
   [Tier 1: Lexical Pass] ────────────► Refuse (exit 2) if:
   - Absolute lexical normalisation       - Absolute path escape
   - Lexical '..' traversal check         - Raw lexical overlap with protected set
              │                           - Non-object / duplicate keys / malformed
              ▼
   [Tier 2: Canonical Pass] ──────────► Refuse (exit 2) if:
   - Fail-closed realpath resolution      - realpath failure (NEVER fail open)
   - Canonical root containment           - Symlink alias into protected set
   - Ancestor overlap check               - Root is ancestor of protected store
              │
              ▼
    [Execution Allowed]
   - Safe find/du/git status (C2)
   - Safe sha256 regular file read (C1)
```

#### Exact Rules of the Invariant:
1. **Pre-Access Sequencing:**
   - In `souji-census.sh`: `--compare` path MUST be checked lexically and canonically before `load_census` touches the filesystem. `--root` and `$SHOKUNIN_ROOT` MUST be checked before `[ -d ]` or `list_repos`. Child paths and linked worktrees MUST be checked before any `git` or `find` execution.
   - In `souji-evidence-cache.py`: Every dependency path MUST be checked lexically (`not isabs`, no `..` prefix after normpath) and canonically (`realpath(root/dep)` starts with `realpath(root) + os.sep`) before calling `os.path.isfile` or opening bytes for SHA-256.
2. **Ancestor Overlap Protection:**
   - A root path $R$ overlaps protected store $P$ if:
     - $R = P$ (exact match)
     - $R \subset P$ ($R$ is an ancestor of $P$, meaning enumerating $R$'s children will traverse $P$)
     - $P \subset R$ ($R$ is a descendant within $P$)
   - *Example:* If $P = /home/vgpnk/.omp/agent$, then `--root /home/vgpnk` MUST be refused because it is an ancestor of $P$. Conversely, `--root /home/vgpnk/Projects/shokunin` is permitted because it is a disjoint sibling subtree.
3. **Fail-Closed Canonicalisation:**
   - If canonical resolution (`readlink -m` or `realpath`) fails, the tool MUST exit 2 (`could-not-evaluate`), NEVER falling back to the unchecked lexical string.
4. **Tracked Secret Hashing Isolation (C2):**
   - In `souji-census.sh`, `count_dirty` must exclude secret-shaped patterns via git pathspecs (`:(exclude,glob)**/.env*`, `:(exclude,glob)**/credential*`, etc.) so that racy or stale mtimes on tracked files do not trigger git blob hashing (content reads).

---

## 4. Affected Axes

| Axis | Effect | Mechanism |
|---|---|---|
| **Calibration (C1)** | **Improved** | Digest checks in `souji-evidence-cache.py` prevent stale green reuse; PEBI prevents symlinks and escape paths from spoofing dependency digests or referencing files outside `--root`; per-result measured revisions remain explicit; stable finding IDs. |
| **Operability (C2)** | **Improved** | Census refuses credential-store roots, ancestors, compare targets, and worktree aliases before any disk read or git spawn; no accidental reads of secrets; exit 2 with stable finding ID; normal fleet census operations remain fully operational. |
| **Coverage** | **Neutral (Harm None)** | Unchanged (8). Round 14 claims no coverage expansion; S038 is an append-only locator correction. |

---

## 5. Trace of Second-Order Effects

1. **Runtime Surface:**
   - Eliminates child-process execution (`find`, `du`, `git status`) on denied directories.
   - Eliminates FIFO/device-node hangs in evidence cache by requiring regular-file validation (`test -f` and `not -L`) before opening digests (satisfying QUALITY Q8/Q19).
2. **Contract Surface:**
   - Fully upholds `PROVINCE.md` refusal of credentials without expanding Souji into secret management.
   - Keeps certification OFF; explicitly disclaims proof of historical execution.
   - Adheres to Q4: all selftest and fixture runs remain strictly bounded under `/var/tmp` with cleanup traps; no `/dev/shm` (Q16).
3. **Substrate Surface:**
   - Protects `$HOME/.omp/agent/` from enumeration or metadata crawling, ensuring host harness integrity.
4. **Verification Surface:**
   - Fixtures (`r14-census-boundary.py` and `r14-evidence-cache.py`) use synthetic environments in `/var/tmp` and command spies to prove zero illegal command invocations occur before refusal.

---

## 6. Contradictions & Risks

- **Contradiction 1: `$HOME` vs. Passed Environment:**
  If a test runner overrides `HOME=/var/tmp/...`, a naive check against `$HOME` would not protect the real host credential store if an absolute path is supplied.
  *Resolution:* The protected set must include both `$HOME/.omp/agent` (for synthetic fixture verification) and the real passwd-home `getent passwd "$(id -u)"` (for host execution protection), plus standard paths (`.ssh`, `.gnupg`, `.aws`, `.password-store`).
- **Contradiction 2: Ancestor Rejection vs. Fleet Root:**
  If the ancestor check is implemented as a simple string prefix without path boundary semantics (`/`), `/home/vgpnk` might collide with `/home/vgpnk-other`.
  *Resolution:* Boundary checks must always compare with trailing path separators (`$path/` vs `$protected/`).
- **Contradiction 3: `--compare` Header Gate vs. Content Access:**
  `souji-census.sh` previously checked the header of `--compare` after reading the file.
  *Resolution:* The lexical and canonical boundary check MUST occur before `[ -f "$COMPARE" ]` and before `load_census` is called.

---

## 7. Verification & Final L1 Commands

The following commands are identified for the L1 integrator to run after C1 (`souji-evidence-cache.py`) and C2 (`souji-census.sh`) executors land their files:

```bash
# 1. Syntax and compilation checks
python3 -m py_compile tools/souji-evidence-cache.py tests/fixtures/r14-evidence-cache.py
bash -n tools/souji-census.sh

# 2. C1 Evidence Cache Selftest and Fixture (Calibration)
python3 tools/souji-evidence-cache.py --selftest
python3 tests/fixtures/r14-evidence-cache.py --tool tools/souji-evidence-cache.py
# Verify baseline failure on missing tool
python3 tests/fixtures/r14-evidence-cache.py --tool /var/tmp/nonexistent-tool || true

# 3. C2 Census Boundary Selftest and Fixture (Operability)
tools/souji-census.sh --selftest
python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh

# 4. Static Invariant Verification (Greps)
# Verify no subprocess/eval/exec in evidence cache
grep -nE 'subprocess|os\.system|eval\(|exec\(|shell=True' tools/souji-evidence-cache.py || true
# Verify protected boundary guard runs before filesystem access in census
grep -nE 'check_protected_boundary|refuse_protected' tools/souji-census.sh

# 5. Regression Suite (R13 Baselines)
python3 tools/souji-cert-evidence.py --selftest
bash tests/fixtures/r13-quarantine-bounds.sh
bash tests/fixtures/r12-maintenance-guard.sh --selftest
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji

# 6. Verify /var/tmp cleanup (QUALITY Q4)
ls -d /var/tmp/*souji* /var/tmp/*r14* 2>/dev/null | wc -l  # expect 0
```
