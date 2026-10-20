# FixtureAudit — Round 13 (souji-r13-w1)

Seat: `SoujiR13.FixtureAudit` (scout, leaf member, read-only).  
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin` (Baseline HEAD `31984f4`).  
Judged on: **calibration**, **operability**, **coverage**.  
Execution: **STRICT ZERO EXECUTION**. No test suites, fixtures, tools, or certifier scripts were run. No files outside this report were created or modified.  
Tooling directive: No tools installed or upgraded. All audits performed using read-only inspection (`Read`, `Grep`, `Glob`, `git ls-files`, `sha256sum`).

---

## 1. Executive Summary & Core Verdict

1. **Regression Fixture Discovery (`tests/` and `tools/`)**:
   - `tests/` contains **865 tracked files**. It divides into two historical fixture clusters (`tests/fixtures/case-F1`..`F10` for round-2 file verification and `tests/vault/case-V1`..`V8` for round-4 vault verification), six legacy round-2 runners (`tests/runner-23.sh`..`runner-32.sh`, `judge-60.sh`), and one modern PROTOCOL-compliant registered gate (`tests/fixtures/r12-maintenance-guard.sh`).
   - `tools/` contains the canonical tool suite (`souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh`, `souji-census.sh`), the round-9 shared selftest helper (`souji-round9-selftest.sh`), cluster-specific regression harnesses (`cand-b1-regress.sh`, `cand-b2-selftest.sh`, `cand-c2-clusterc-selftest.sh`, `cand-e1-regress.sh`, `souji-round9-s18-test.py`), the round-10 merged harness (`cand-merge-selftest.sh`), and the round-10/11 certifier harness (`cand-s16-cert.py`).
2. **Mapping r9 Defect Classes (J01–J23)**:
   - All 23 adjudicated round-9 defect classes (`J01`–`J23`) plus 7 fresh variant families (`V01`–`V07`) are mapped to concrete entry commands across `tools/cand-merge-selftest.sh`, `tools/cand-s16-cert.py`, `tools/souji-round9-s18-test.py`, `tools/cand-c2-clusterc-selftest.sh`, and the tools' built-in `--selftest` suites.
3. **Mapping r10 and r11 Claimed Closures**:
   - **r10**: Composed candidates (`cand-merge-*`) closed classes J01–J13 and J15–J23. One class remained open: `souji-census.sh --compare` accepting empty/near-empty baselines (`final22/empty-census-compare`, `s16-fresh/J14`, `s16-fresh/V07`), resulting in `NOT-CERTIFIED` (3 unsafe outcomes, 0 bytes lost).
   - **r11**: Closed the empty-prior census class in candidates (`cand-census-02.sh`, `cand-census-03.sh`, `cand-census-08.sh`), but certification was rejected due to **evidence-integrity defects**: shared-relay overwrites (`cand-s16-cert.py:1859` hardcoded write to `census/round-10/cert-16.json`), detached verdicts, and candidate selection contradicting the class under test (M40, M41, QUALITY Q6).
4. **Smallest Final Validation Set**:
   - A minimal, non-redundant, clean set of **6 runnable entry commands** for L1 that provides 100% executable coverage of closed defect classes, executes strictly in hermetic `/var/tmp` sandboxes with `maintenance.auto=false`, eliminates relay corruption, and avoids runner sprawl.
5. **Omissions & Scope Discipline**:
   - Historical round-2 and round-4/5 test harnesses, redundant cluster scripts, and `cand-s16-cert.py` (due to line 1859 relay pollution) are omitted from the active validation set with precise justifications.
   - Per contract, **no broad deletion or cleanup** of historical files is proposed.

---

## 2. Comprehensive Inventory of Existing Fixtures & Scripts

### 2.1. Canonical Tools & Built-in Selftests (`tools/`)
The four installed tools each carry an integrated `--selftest` mode executing hermetic `/var/tmp` Git plumbing tests:

| Tool Path | Current Installed SHA-256 | `--selftest` Entry Command | Built-in Checks & Sub-delegations |
|---|---|---|---|
| `tools/souji-verify.sh` | `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd` | `TMPDIR=/var/tmp bash tools/souji-verify.sh --selftest` | 40 checks: 24 internal checks + 16 checks via `tools/souji-round9-selftest.sh verify` (line 1270). |
| `tools/souji-vault-verify.sh` | `f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b` | `TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash tools/souji-vault-verify.sh --selftest` | 51 checks: 35 internal checks + 16 checks via `tools/souji-round9-selftest.sh vault` (line 1576). |
| `tools/souji-quarantine.sh` | `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` | `TMPDIR=/var/tmp bash tools/souji-quarantine.sh --selftest` | 91 checks: 63 internal checks + 28 checks via `tools/souji-round9-selftest.sh quarantine` (line 1502). |
| `tools/souji-census.sh` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | 36 checks: 32 base checks + 4 compare contract checks (line 790). *(Byte-identical to `cand-census-02.sh`).* |

### 2.2. Regression Test Batteries & Helpers (`tools/`)

1. **`tools/souji-round9-selftest.sh`**:
   - *Role*: Shared round-9 regression helper invoked directly by verify (16 checks), vault (16 checks), and quarantine (28 checks).
   - *Cases*: Covers nested dirty/stale/pushed repo, nested gitfile, failed worktree queries (named/detached), read-only index (`GIT_OPTIONAL_LOCKS=0`), Turkish locale (`LC_ALL=C`), ledger revocation (file/dir), NUL in list (path/pin/prefix), default-ref rollback/missing.
   - *Entry Command*: `bash tools/souji-round9-selftest.sh <verify|vault|quarantine> <tool-path>`
2. **`tools/cand-merge-selftest.sh`**:
   - *Role*: Round-10 S15 merged selftest helper. Ports the pre-existing r9 battery and adds explicit regression cases for r9 defect classes J01–J23 expressible per tool kind, plus S15 merge-specific cases (`s15-g2-backdated-descendant`, `s15-f2-gitfile-root`).
   - *Entry Command*: `bash tools/cand-merge-selftest.sh <verify|vault|quarantine> <tool-path>` (exits 0, prints `R10 <pass> <fail>`).
3. **`tools/cand-c2-clusterc-selftest.sh`**:
   - *Role*: Round-10 S06 cluster-C regression battery: filesystem scope boundaries, symlink containment, and quarantine root protection.
   - *Cases*: 12 deterministic cases (`C2R01`–`C2R12`): nested `.git` dir, nested `.git` gitfile, outside symlink in scope, dangling symlink, symlinked quarantine root, symlinked quarantine DATE dir, poisoned row, index-write contract, absent index not created, mode-000 subdir, controls.
   - *Entry Command*: `bash tools/cand-c2-clusterc-selftest.sh <tools-dir> [label]`
4. **`tools/cand-b1-regress.sh` & `tools/cand-b2-selftest.sh`**:
   - *Role*: Round-10 S03/S04 cluster-B batteries testing ledger authority (B1-a independent record, B1-b revocation across hold) and control character / TSV parser refusal (B2).
   - *Entry Command*: `bash tools/cand-b1-regress.sh <verify|vault|quarantine> <tool-path>`
5. **`tools/cand-e1-regress.sh`**:
   - *Role*: Round-10 S09 cluster-E battery testing git command failure propagation (E1a–E1d), Turkish locale `id_*` secret preservation (E2a), and unique-commit count excluding candidate's own detached HEAD (E3a).
   - *Entry Command*: `bash tools/cand-e1-regress.sh --tools <tools-dir>`
6. **`tools/souji-round9-s18-test.py`**:
   - *Role*: Round-9 S18 independent hardening battery: 15 fixture families (31 tool-case checks) verifying fail-closed refusals.
   - *Entry Command*: `python3 tools/souji-round9-s18-test.py --tool-dir <tools-dir> --suffix ''`

### 2.3. Certifier Scripts & Historical Relays (`tools/` & `census/`)

1. **`tools/cand-s16-cert.py`**:
   - *Role*: Round-10/11 master certifier harness. Assembles candidates in `/var/tmp`, executes 15 corpora/suites (`s10`, `s09`, `s22`, `s21`, `s23`, `s24`, `s11`, `s05`, `s07`, `s12`, `s15`, `final22`, `final23`, `selftest`, `s16-fresh`), and grades safety invariants.
   - *Defect / Limitation*: **Line 1859 unconditionally overwrites `census/round-10/cert-16.json`** (`fragment = R10 / "cert-16.json"`). Even with `--out`, it dirty-writes the committed repository path. This is the root cause of M40 / Q6.

### 2.4. Fixtures in `tests/fixtures/`

1. **`case-F1` through `case-F10`** (Round 2 legacy fixtures):
   - Tracked under `tests/fixtures/case-F<N>/`. Audited in `tests/results/fixture-audit.json`.
   - *Protocol Status*: Only 2 of 10 emit the contracted `FIXTURE_READY` protocol (`case-F7`, `case-F8`). `case-F10` lacks a `make-fixture.sh` builder (static payload of synthetic `app.env`, `creds.pem`, `notes.txt`). Their scenarios are now integrated inside `souji-verify.sh --selftest`.
2. **`tests/fixtures/r12-maintenance-guard.sh`** (Round 12 modern gate):
   - *Role*: Registered gate in `SKILL.md:106`. Proves git ≥2.54 auto-maintenance worktree pruning hazard on plain commit and validates `maintenance.auto=false` / `git worktree lock`.
   - *Interface*: PROTOCOL-compliant (`0=clean`, `1=failed`, `2=could-not-evaluate`). Emits finding IDs `SOUJI-R12-MAINT-<case>`.
   - *Entry Command*: `bash tests/fixtures/r12-maintenance-guard.sh --selftest` (6/6 PASS).

### 2.5. Vault Fixtures & Test Runners (`tests/vault/` and `tests/`)

1. **`tests/vault/case-V1` through `case-V8`**:
   - Round-4 Obsidian vault verification fixtures (`case-V1` to `case-V8`). Each has `make-fixture.sh`, `expected.json`, `selftest.sh`.
   - Exercised by round-4 runner scripts (`tests/vault/runner-25.sh`..`runner-40.sh`) and adversarial suites (`vadv-49`, `vadv-51`, `vadv-52`, `vadv-56`, `judge-60-vault.sh`).
2. **`tests/runner-23.sh`, `runner-25.sh`..`runner-32.sh`, `tests/judge-60.sh`**:
   - Round-2 independent runners testing `souji-verify.sh` against `souji-verify.spec.md`.
   - *Limitations*: Several hardcode `/tmp` instead of `/var/tmp` (e.g. `runner-32.sh:17`), violating QUALITY Q4; hardcode output writes to `tests/results/runner-*.json`; do not exercise vault, quarantine, or census tools.

---

## 3. Mapping of r9 Defect Classes (J01–J23) to Exact Entry Commands

The 23 defect classes adjudicated in round 9 (`corpus/lessons/round-9.md:8-17`, `corpus/lessons/round-12.md:94-100`, `tools/cand-s16-cert.py:428-808`), together with fresh variants `V01`–`V07`, are mapped below to exact entry commands:

| Class ID | Defect Invariant & Failure Mode | Tool Scope | Exact Entry Command & Location | Observed Closure Evidence / Rule |
|---|---|---|---|---|
| **J01** | Pushed verdict ignores uncommitted replacement bytes (dirty-pushed). | `verify`, `vault-verify` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `j01-dirty-pushed`, line 298)*<br>Alternative: `python3 tools/souji-round9-s18-test.py --tool-dir tools --suffix ''` *(case `dirty-pushed`, line 69)* | Target with uncommitted changes over a pushed file is refused (`NOT-SAFE`), never `SAFE(pushed)`. |
| **J02** | Stale sweep omits hidden live references (`.reference.md`). | `verify`, `quarantine` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `j02-hidden-live-ref`, line 306)*<br>Variant: `cand-s16-cert.py` case `V01` (line 809) | `rg` sweep scans hidden files (`.reference.md`, `.active-reference`) and refuses stale receipt if referenced. |
| **J03** | Stale directory receipt lacks descendant closure (aged container, fresh child). | `verify`, `quarantine` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `s15-g2-backdated-descendant`, line 377)*<br>Alternative: `cand-s16-cert.py` case `J03` (line 450) | Container age does not launder fresh descendant; ctime/mtime checked on descendants; refuses stale receipt. |
| **J04** | Pushed directory closure over ignored descendants (unpushed ignored files). | `verify`, `quarantine` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `j03-dir-ignored-payload`, line 313)*<br>Variant: `cand-s16-cert.py` case `V02` (line 821) | Directory holding uncommitted/ignored files (`.gitignore` payload) refused; prevents deleting untracked assets. |
| **J05** | Ledger copy does not independently survive removal (self-referential row). | `vault-verify`, `quarantine` | `bash tools/cand-merge-selftest.sh vault tools/souji-vault-verify.sh`<br>*(case `j05-self-ledger`, line 323)*<br>Alternative: `cand-s16-cert.py` case `J05` (line 474) | Row where `vault_path == source_path` fails independence check; returns `NOT-SAFE` / `NOT-AUTHORIZED`. |
| **J06** | Directory ledger row accepts missing vault digest. | `vault-verify` | `bash tools/cand-merge-selftest.sh vault tools/souji-vault-verify.sh`<br>*(case `j06-missing-vault-digest`, line 331)* | Ledger row with empty `vault_sha256` for directory target fails strict schema; refused. |
| **J07** | Symlinked quarantine root escapes repository containment (`.ufo-quarantine -> /outside`). | `quarantine` | `bash tools/cand-merge-selftest.sh quarantine tools/souji-quarantine.sh`<br>*(case `j07-quarantine-root-symlink`, line 361)*<br>Alternative: `bash tools/cand-c2-clusterc-selftest.sh tools` *(cases `C2R05`, `C2R06`, lines 135-175)* | Symlinked quarantine root detected via `lstat`/`[ -L ]`; refuses move; outside directory left untouched. |
| **J08** | Unpushed local commit touching scratch file falls through to stale (unpushed veto). | `verify` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `j08-unpushed-stale`, line 342)*<br>Variant: `cand-s16-cert.py` case `V04` (line 852) | `git log --branches --not --remotes --oneline -- <path>` detects unpushed commits and vetoes stale fallback. |
| **J09** | Failed git queries become zero-count receipts (e.g. `git` missing / exit 127). | `verify`, `quarantine` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(cases `git-failure-named`, `git-failure-detached`, line 147)*<br>Alternative: `bash tools/cand-e1-regress.sh --tools tools` *(cases `E1a`..`E1d`, line 9)* | Broken/failing git query emits `NOT-SAFE(git-unverifiable)`; non-zero pipeline status checked fail-closed. |
| **J10** | Pushed second check loses default-origin ancestry (origin ref rolled back/deleted during hold). | `quarantine` | `bash tools/cand-merge-selftest.sh quarantine tools/souji-quarantine.sh`<br>*(cases `default-rollback`, `default-missing`, line 271)*<br>Alternative: `cand-s16-cert.py` case `J10` (line 542) | Quarantine hold second-check re-resolves default ref; missing/rewound origin causes `ABORTED`, staging kept. |
| **J11** | Turkish locale (`tr_TR`) case folding bypasses protected-name refusal (`ID_*`). | `verify`, `vault-verify`, `quarantine` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `turkish-locale`, line 185)*<br>Alternative: `bash tools/cand-e1-regress.sh --tools tools --only E2a` (line 14) | Tools export `LC_ALL=C`; `id_*` / `ID_*` matching does not suffer Turkish dotless-i folding (`ı`). |
| **J12** | Branch-only unpushed queries omit detached HEAD commits. | `verify` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `j12-detached-head`, line 351)*<br>Alternative: `bash tools/cand-e1-regress.sh --tools tools --only E3a` (line 16) | Query includes `HEAD` in unpushed graph traversal (`git log HEAD --not --remotes`); detached work preserved. |
| **J13** | Read-only inspection rewrites or creates git index (`.git/index`). | `verify`, `vault-verify`, `census` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(case `readonly-index`, line 175)*<br>Alternative: `bash tools/cand-c2-clusterc-selftest.sh tools` *(cases `C2R08`, `C2R09`, line 210)* | Tools export `GIT_OPTIONAL_LOCKS=0`; strace / sha256 verifies index bytes before and after are identical. |
| **J14** | Empty prior census accepted as unchanged baseline (0-byte prior diff). | `census` | `B=$(mktemp -d -p /var/tmp); : > "$B/empty.tsv"; bash tools/souji-census.sh --root "$B" --compare "$B/empty.tsv"`<br>Alternative: `cand-s16-cert.py` case `J14` (line 627) | `load_census()` checks line-1 header before blank-line skips; exits 2 on empty/malformed baseline. |
| **J15** | Unavailable reference scope treated as zero refs (missing `$SHOKUNIN_ROOT`). | `verify`, `quarantine` | `cand-s16-cert.py` case `J15` (line 644) | Sweep verifies `$SHOKUNIN_ROOT` directory exists before trusting zero grep hits; fails closed if absent. |
| **J16** | NUL-erased list bytes alter authorized target path or receipt. | `quarantine` | `bash tools/cand-merge-selftest.sh quarantine tools/souji-quarantine.sh`<br>*(cases `nul-path`, `nul-pin`, `nul-prefix`, line 258)*<br>Alternative: `tools/souji-quarantine.sh --selftest` *(case U5, line 1478)* | Entire `--list` file pre-scanned for NUL bytes (`grep -P '\x00'`); exits 2 immediately before moving any file. |
| **J17** | Tab-spliced path forges verdict fields in quarantine TSV parser. | `quarantine` | `python3 tools/souji-round9-s18-test.py --tool-dir tools --suffix ''`<br>*(case `tab-path-verdict-injection`, line 86)*<br>Variant: `cand-s16-cert.py` case `V05` (line 866) | Strict 2-column TSV validation; control characters and tabs in target paths refused before engine evaluation. |
| **J18** | Atomic ledger revocation ignored after row capture. | `quarantine`, `vault-verify` | `bash tools/cand-merge-selftest.sh quarantine tools/souji-quarantine.sh`<br>*(cases `ledger-file`, `ledger-directory`, line 204)*<br>Alternative: `cand-b1-regress.sh` case `B1-b` (line 12) | Ledger content sha256 pinned before capture and re-checked before second-check removal; aborts if modified. |
| **J19** | Worktree uniqueness excludes candidate via its own HEAD (`--not --all`). | `verify` | `python3 tools/cand-s16-cert.py --corpora s16-fresh`<br>*(case `J19`, line 704)*<br>Alternative: `tools/souji-round9-s18-test.py` case `worktree-unique-detached-head` | Unique commit count compares against durable refs (`refs/heads`, `refs/tags`, `refs/remotes`), excluding own worktree HEAD. |
| **J20** | Last-writer registration map masks unpushed owner (multiple admin dirs). | `verify` | `python3 tools/cand-s16-cert.py --corpora s16-fresh`<br>*(case `J20`, line 728; variant `V06`, line 874)* | All registrations for target evaluated; unpushed registration cannot be masked by later pushed registration. |
| **J21** | Tab-delimited owner metadata in worktree list corrupts identity. | `verify` | `python3 tools/cand-s16-cert.py --corpora s16-fresh`<br>*(case `J21`, line 750)*<br>Alternative: `bash tools/cand-b1-regress.sh verify tools/souji-verify.sh` | Worktree list porcelain parsing handles tab/whitespace paths safely without field offset corruption. |
| **J22** | Naming-filtered owner discovery falls through to stale (non-`*-shokunin`). | `verify` | `python3 tools/cand-s16-cert.py --corpora s16-fresh`<br>*(case `J22`, line 771)* | Owner repo discovery searches fleet root broadly, refusing to fall through to `stale` for valid linked worktrees. |
| **J23** | Main gitfile repository root misclassified as pushed artifact. | `verify` | `bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh`<br>*(cases `s15-f2-gitfile-root` line 389, `nested-gitfile` line 139)*<br>Alternative: `cand-c2-clusterc-selftest.sh` case `C2R02` | Repository root whose `.git` is a gitfile (`gitdir: ...`) is classified as kind-1 repo root, never kind-3 file. |

---

## 4. Mapping of r10 and r11 Claimed Closures

### 4.1. Round 10 Closure Claims & Adjudication
- **Target Declared**: Close all r9 defect classes and certify the toolchain (`corpus/lessons/round-10.md:2`).
- **What Landed**: Candidates composed from 7 cluster pairs into `cand-merge-*` and installed over canonical tools (`tools/cand-merge-verify.sh`, `cand-merge-vault.sh`, `cand-merge-quarantine.sh`, and `cand-merge-selftest.sh`).
- **Selftest Expansion**: Verify 24→40, Vault 35→51, Quarantine 63→91, Census 32 checks.
- **Outcome**: **REJECTED on O1 — 3 residual unsafe outcomes (one defect class)**:
  `souji-census.sh --compare` accepted empty or newline-only baselines as clean exit 0 diffs (`census/round-10/cert-16.json:28-98`):
  1. `final22/empty-census-compare` (0-byte prior vs empty root → exit 0).
  2. `s16-fresh/J14` (0-byte prior vs empty root → exit 0, expected exit 2).
  3. `s16-fresh/V07` (newline-only prior vs empty root → exit 0, expected exit 2).
- **Exact Entry Commands proving r10 closures & remaining gap**:
  ```bash
  # Proved closed (J01-J13, J15-J23):
  bash tools/cand-merge-selftest.sh verify tools/souji-verify.sh
  bash tools/cand-merge-selftest.sh vault tools/souji-vault-verify.sh
  bash tools/cand-merge-selftest.sh quarantine tools/souji-quarantine.sh
  bash tools/cand-c2-clusterc-selftest.sh tools

  # Proved open (J14 / V07 defect on r10 census 11bf9cdf):
  B=$(mktemp -d -p /var/tmp)
  mkdir -p "$B/empty-root"; : > "$B/empty.tsv"
  bash tools/souji-census.impl-33.sh --root "$B/empty-root" --compare "$B/empty.tsv"
  echo "r10 census rc=$?"  # emitted 0 (defect)
  rm -rf "$B"
  ```

### 4.2. Round 11 Closure Claims & Evidence Defects
- **Target Declared**: Fix `souji-census.sh --compare` contract, re-certify toolchain, score rubric (`corpus/lessons/round-11.md:2`).
- **What Landed**: Fixed `load_census()` in `tools/souji-census.sh` (`cand-census-02.sh`, sha256 `6a000c59`): moved line-1 header check before blank-line skips and added post-loop `n<1` guard (`census/round-11/S08-fragment.md:20-25`). All 3 empty-prior cases refuse with exit 2.
- **Why Certification Was NOT Granted (The M40/M41 Relays)**:
  1. **Shared Writable Relay Overwrites (M40 / QUALITY Q6)**: `tools/cand-s16-cert.py` line 1859 hardcoded writing to `census/round-10/cert-16.json`. Multiple seats (S02, S11, S15, S16, S22, S25, S29, S30, S31) ran concurrently, repeatedly overwriting the single file with differing candidate hashes.
  2. **Verdicts Attached to Unmeasured Bytes (M40)**: Seat S31 certified census sha `462dabd2` while attaching the selftest tail of `cand-census-08.sh` (`35 checks, 0 failed`), when `462dabd2` actually failed 2 checks (`36 checks, 2 failed`).
  3. **Selection Rule Contradiction (M41 / QUALITY Q6)**: Candidate selection picked candidates failing selftests.
  4. **Installed Working-Tree Discrepancy**: S30 confirmed that installed working-tree census `462dabd2` was RED (36/2), whereas candidate `cand-census-02.sh` (`6a000c59`) was GREEN (36/0).
  5. *Status*: Round rejected. Certification remains **OFF**.

---

## 5. Smallest Final Validation Set (Executable Recommendations for L1)

To validate the entire toolset without running redundant test sprawl, without writing to shared relays, and without violating `/var/tmp` or git invariants, L1 should execute **only the following smallest validation set**:

### Command Suite for L1 Verification

```bash
#!/usr/bin/env bash
# Smallest Final Validation Set — Souji R13
set -euo pipefail

LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
export TMPDIR="/var/tmp"
export LC_ALL="C"
export GIT_CONFIG_NOSYSTEM="1"
export GIT_CONFIG_GLOBAL="/dev/null"
export GIT_AUTHOR_NAME="souji-selftest"
export GIT_AUTHOR_EMAIL="souji-selftest@fixture.invalid"
export GIT_COMMITTER_NAME="souji-selftest"
export GIT_COMMITTER_EMAIL="souji-selftest@fixture.invalid"

# --- 1. Installed Tool Built-in Selftests (Hermetic /var/tmp) ---
# Asserts 40/40, 51/51, 91/91, 36/36 green
TMPDIR=/var/tmp bash "$LANE/tools/souji-verify.sh" --selftest
TMPDIR=/var/tmp SOUJI_CLI_BIN=/bin/false bash "$LANE/tools/souji-vault-verify.sh" --selftest
TMPDIR=/var/tmp bash "$LANE/tools/souji-quarantine.sh" --selftest
TMPDIR=/var/tmp bash "$LANE/tools/souji-census.sh" --selftest

# --- 2. Ported & Merged Adversarial Suite (J01-J23 coverage) ---
# Asserts R10 0 failed across all three engines
bash "$LANE/tools/cand-merge-selftest.sh" verify "$LANE/tools/souji-verify.sh"
bash "$LANE/tools/cand-merge-selftest.sh" vault "$LANE/tools/souji-vault-verify.sh"
bash "$LANE/tools/cand-merge-selftest.sh" quarantine "$LANE/tools/souji-quarantine.sh"

# --- 3. Scope, Nested Git & Symlink Containment Suite ---
# Asserts 12/12 PASS
bash "$LANE/tools/cand-c2-clusterc-selftest.sh" "$LANE/tools"

# --- 4. Census Contract Refusal Probes (J14 / V07 Closure) ---
# Asserts exit 2 on 0-byte and newline-only baselines
B=$(mktemp -d -p /var/tmp souji-census-probe.XXXXXX)
trap 'rm -rf "$B"' EXIT
mkdir -p "$B/empty-root"
: > "$B/empty.tsv"
printf '\n' > "$B/newline.tsv"
bash "$LANE/tools/souji-census.sh" --root "$B/empty-root" --compare "$B/empty.tsv" && exit 1 || [ $? -eq 2 ]
bash "$LANE/tools/souji-census.sh" --root "$B/empty-root" --compare "$B/newline.tsv" && exit 1 || [ $? -eq 2 ]

# --- 5. Registered Maintenance Guard Gate ---
# Asserts 6/6 PASS, finding ids SOUJI-R12-MAINT-*
bash "$LANE/tests/fixtures/r12-maintenance-guard.sh" --selftest

# --- 6. Round-13 Wave 1 New Deliverables (once integrated by L1) ---
# BoundQuarantine: Bounded staging/digest & FIFO rejection fixture
# bash "$LANE/tests/fixtures/r13-quarantine-bounds.sh" --tool "$LANE/tools/souji-quarantine.sh"
# EvidenceGate: Executable evidence validator selftest
# python3 "$LANE/tools/souji-cert-evidence.py" --selftest
# SizeProbe: Read-only repo structure probe selftest
# bash "$LANE/tests/fixtures/r13-repo-structure.sh" --selftest
```

### Why this set is minimal and complete:
- Covers all 23 r9 classes, all r10 merged clusters, and r11 census compare fixes.
- Runs entirely in memory / temporary directories under `/var/tmp` with traps.
- Does not modify any tracked or committed file.
- Takes less than 45 seconds total.

---

## 6. Omissions & Scope Limitations (No Broad Cleanup)

The following existing scripts are intentionally **omitted** from the active validation set:

| Omitted File / Script | Category / Origin | Reason for Omission from Active Set | Retention Status |
|---|---|---|---|
| `tools/cand-s16-cert.py` | Certifier Script | **Harmful shared-relay defect**: line 1859 unconditionally overwrites `census/round-10/cert-16.json`, polluting git status and reproducing defect M40. | Retain as historical certifier source; do NOT execute in-place. |
| `tests/runner-23.sh` .. `runner-32.sh`, `tests/judge-60.sh` | Round-2 Runners | Obsolete: tests only `souji-verify.sh` against round-2 spec; lacks vault, quarantine, census, and r9-r12 classes; several violate Q4 (`/tmp` hardcoded); overwrite `tests/results/`. | Retain as historical audit evidence. |
| `tests/fixtures/case-F1` .. `case-F10` direct runs | Round-2 Fixtures | Protocol drift: 8/10 fixtures do not emit `FIXTURE_READY`; `case-F10` lacks builder; fully subsumed by `souji-verify.sh --selftest`. | Retain as spec reference. |
| `tests/vault/case-V1` .. `case-V8`, `tests/vault/runner-*` | Round-4/5 Vault Suites | Historical: targeted deprecated CLI implementations (`impl-17`..`impl-24`); subsumed by `souji-vault-verify.sh --selftest` and `cand-merge-selftest.sh vault`. | Retain as vault benchmark evidence. |
| `tools/cand-b1-regress.sh`, `cand-b2-selftest.sh`, `cand-e1-regress.sh` | Round-10 Cluster Suites | Redundant: their cases were merged into `cand-merge-selftest.sh` and `cand-c2-clusterc-selftest.sh`. | Retain as cluster candidate evidence. |
| `tools/souji-round9-s18-test.py` | Round-9 S18 Battery | Redundant with `cand-merge-selftest.sh`, which ports S18 into bash with strict `/var/tmp` cleanup. | Retain as S18 candidate evidence. |

**Strict No-Cleanup Invariant**: In accordance with the engineering contract ("Delete dead weight; prefer boring design to needless abstraction", "Do not propose broad cleanup"), these historical files MUST NOT be deleted. They are historical reference artifacts that document past rounds and judge decisions.

---

## 7. Audit Findings & Remaining Open Debts

1. **Installed Census Sha Verified Clean**:
   - `sha256sum tools/souji-census.sh` evaluates to `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`, which is byte-identical to `cand-census-02.sh`. The red selftest defect of `462dabd2` (M50 / S30-C02) is NOT present in the currently installed `souji-census.sh`.
2. **Quarantine Timeout & FIFO Still Open in Baseline (M43, M44)**:
   - `grep -c timeout tools/souji-quarantine.sh` is `0`.
   - Lines 184 and 722 have duplicate `file_sha` definitions; lines 186 and 727 have duplicate `dir_digest` definitions.
   - Stage-2 `mv` operations (lines 529, 536) have no bounds.
   - *Resolution*: Being addressed in round 13 wave 1 by `SoujiR13.BoundQuarantine`.
3. **No Independent Executable Evidence Validator in Baseline (M40, M41)**:
   - Certification remained OFF in rounds 11 and 12 because certification was mediated by shared JSON files rather than an executable validator.
   - *Resolution*: Being addressed in round 13 wave 1 by `SoujiR13.EvidenceGate` (`tools/souji-cert-evidence.py`).
4. **Git Repo Structure Write Safety (C3 / F2)**:
   - Experimental command `git repo structure` lacked an empirical write-safety fixture under `/var/tmp`.
   - *Resolution*: Being addressed in round 13 wave 1 by `SoujiR13.SizeProbe` (`tests/fixtures/r13-repo-structure.sh`).

---

## 8. Verification Checks for L1 Integrator

When L1 runs final wave integration, L1 should verify:
1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` shows only assigned wave 1 artifacts.
2. The smallest validation set in §5 is executed cleanly.
3. Neither `census/round-10/cert-16.json` nor `census/round-11/cert-16.json` is modified during test runs.
4. Certification remains **OFF** in documentation until all four installed tools are verified by the new `souji-cert-evidence.py` validator.
