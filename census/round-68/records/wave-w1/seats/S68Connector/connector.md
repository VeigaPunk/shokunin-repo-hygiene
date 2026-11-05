# S68Connector — Sibling Overlap, Assimilation Scan & Non-Obvious Move

Seat: `S68Connector` (connector, leaf, no subagents).
Lane: `souji` (/home/vgpnk/Projects/shokunin/souji-shokunin).
Milestone: souji r68 post-freeze C1 battery and C2 ambient after-arms; attacks on counter, predicates, battery and scope; declared-protection inventory; replace-ref source check; sibling overlap; knowledge and registry drafts.
Operating posture: Read-only across fleet and lane; deliverables strictly isolated to seat wave paths.

---

## 1. Sibling Lane Grep Scan (Hit Table)

Scope: The 20 sibling lane repos under `/home/vgpnk/Projects/shokunin/*-shokunin` (excluding `souji-shokunin` from sibling counts; `souji-shokunin` reported in separate column).
Command: `grep -rl --include=*.md --include=*.py --include=*.sh --include=*.tsv -F <TERM> <REPO>`

| Term | Sibling Repos | Sibling Files | Souji Files | Sibling Breakdown (`repo:file_count`) |
|---|---|---|---|---|
| `GIT_NO_REPLACE_OBJECTS` | 13 | 824 | 900 | kagi:12, kaidoku:113, kake:3, kama:81, kasegi:5, kengaku:1, kotodama:51, kumitate:6, mado:290, mori:8, tabi:165, tameshi:71, tsukuroi:18 |
| `refs/replace` | 13 | 535 | 131 | chousa:1, kaidoku:21, kake:3, kama:208, kasegi:3, kengaku:76, kotodama:17, kumitate:5, mado:67, mori:6, tabi:108, tameshi:16, tsukuroi:4 |
| `GIT_COMMON_DIR` | 13 | 308 | 345 | kaidoku:2, kake:16, kama:14, kasegi:1, kengaku:4, kotoba:6, kotodama:9, kumitate:107, mado:21, mori:41, tabi:13, tameshi:65, tsukuroi:9 |
| `GIT_NAMESPACE` | 11 | 72 | 370 | kaidoku:2, kake:2, kama:8, kasegi:1, kotodama:12, kumitate:7, mado:4, mori:11, tabi:15, tameshi:7, tsukuroi:3 |
| `GIT_CEILING_DIRECTORIES` | 14 | 727 | 110 | kagi:5, kaidoku:2, kake:77, kama:18, kasegi:8, kengaku:88, kotoba:1, kotodama:39, kumitate:110, mado:4, mori:20, tabi:27, tameshi:83, tsukuroi:245 |
| `receipt-write` | 15 | 87 | 513 | audio:2, chousa:3, kagi:1, kaidoku:13, kama:12, kasegi:2, kengaku:1, kotoba:2, kotodama:25, kumitate:1, mado:1, mori:1, tabi:2, tameshi:4, tsukuroi:17 |
| `ambient` | 20 | 2196 | 146 | audio:53, chousa:81, game-dev-2d:134, game-dev-3d:31, kagi:82, kaidoku:159, kake:43, kama:42, kasegi:54, kengaku:30, kotoba:67, kotodama:91, kumitate:142, lore:8, mado:437, mori:98, revenger:3, tabi:67, tameshi:98, tsukuroi:476 |

---

## 2. Shokuknow Staged Theme Review (`/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md`)

Review of all staged themes in the staging package against round-68 themes (replace refs, ambient environment, counter hermeticity, receipt routes):

| Staged Theme / Entry | Staged Topic & Summary | Relation to R68 Theme | Verdict | Reason |
|---|---|---|---|---|
| `git-auto-maintenance-trigger-set[-r23]` | Git auto-maintenance commands prune stale worktrees | Maintenance triggers | **none** | Unrelated to replace refs, counter hermeticity, or receipt routes. |
| `repo-size-census-readonly` | Read-only size census using three tools | Census instrumentation | **none** | Mentions generic refs namespace in prose; no relation to `GIT_NAMESPACE` or counter environment. |
| `quarantine-staging-no-copy[-r23,-r24]` | `RENAME_NOREPLACE` syscall availability on mounts | Filesystem rename flags | **none** | "replace" match is `RENAME_NOREPLACE` syscall flag, not git replacement refs. |
| `duplicate-verdict-identity`, `duplicate-verdict-taxonomy-r24` | Deduplication threshold and verdict taxonomy | Dedup classification | **none** | Unrelated to receipt writer env routes. |
| `quarantine-origin-record-fields[-r23,-r24]`, `origin-record-format-gvfs-r26`, `origin-record-writer-r27`, `origin-record-exclusivity-r28`, `origin-record-durability-r28`, `origin-record-mechanism-set-r33` | Origin record layout, fields, GLib writer, atomic durability | Quarantine records | **none** | Unrelated to `tools/souji-receipt-write.py` or counter hermeticity. |
| `count-objects-garbage-semantics[-r23,-r24]`, `garbage-false-positive-modes-r25..r27` | `count-objects` garbage sweep in git's `builtin/count-objects.c` | Worktree garbage census | **none** | Adjacent word match (`common_dir` struct in git C source for linked worktrees); unrelated to writer `GIT_COMMON_DIR` check or ambient C2. |
| `fleet-maintenance-config-r24`, `fleet-exposure-r24`, `fleet-live-exposure-r25..r27`, `fleet-prune-safety-r28`, `fleet-prune-durability-r28`, `fleet-prune-currency-r30`, `fleet-prune-upstream-confirmed-r31`, `fleet-prune-durability-complete-r32`, `fleet-prune-census-drift-r33`, `fleet-grace-period-exposure-r34`, `fleet-prune-expiry-selection-r35` | Fleet exposure to worktree pruning and git maintenance | Worktree lifecycle | **none** | Unrelated to receipt writer routes or replacement ref forgery. |
| `reclamation-deadline-kinds-r25..r27`, `self-hosted-reclamation-shapes-r28`, `gitlab-reclamation-settings-r28..r29`, `gitlab-reclamation-config-r30`, `gitlab-reclamation-old-shape-r31`, `gitlab-reclamation-name-window-r32`, `gitlab-reclamation-name-phantom-r33` | GitLab housekeeping, reclamation schedules, and deprecations | Self-hosted gitlab settings | **none** | Matches "counter" (database column) and "replace" (deprecated settings replacement); unrelated to test counters or git replace refs. |
| `duplicate-receipt-class-decision-r25..r26` | Adding a duplicate receipt class to `tools/souji-verify.sh` | Census verify receipts | **none** | Concerns souji round-4/25 `souji-verify.sh` taxonomy; unrelated to `tools/souji-receipt-write.py` environment routes. |
| `near-duplicate-threshold-r28`, `near-duplicate-operating-point-r28`, `near-duplicate-relations-r29`, `near-duplicate-literature-identity-r33`, `near-duplicate-threshold-source-r34` | Near-duplicate detection algorithms and thresholds | Corpus deduplication | **none** | Unrelated to round-68 axes. |
| `community-reclamation-practice-r28..r31`, `community-literature-zh-ja-r33..r34`, `community-worktree-literature-r35` | Community practices in English, Chinese, Japanese | Literature review | **none** | Unrelated to round-68 axes. |
| `prune-trigger-levers-r28`, `prune-expiry-behaviour-r29`, `prune-lever-paths-r30`, `git-grace-period-semantics-r34`, `git-grace-period-at-release-r35`, `prune-expiry-mechanism-r36`, `prune-lever-matrix-r36`, `prune-scheduler-scan-r36`, `prune-upstream-durability-r36`, `git-grace-period-japanese-r36` | Git gc grace period and prune options | Prune configuration | **none** | Unrelated to round-68 axes. |

---

## 3. Considerthese Status

Check: `test -d /home/vgpnk/Projects/shokunin/souji-shokunin/considerthese/`
Status: **absent** (directory does not exist; exit code 1).

---

## 4. Assimilation Verdict

**Verdict: `Assimilation: none`**

Reasons:
1. **Zero topic overlap:** None of the 68 staged knowledge entries or 134 staged sources match round-68 claims (C1: receipt writer mutant battery & replace-ref dirty check PK6; C2: counter hermeticity against ambient `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`). The staged package covers rounds 1–16 / 23–36 worktree pruning and quarantine staging.
2. **Registry collision and staleness:** The package assumes a 108-row baseline and assigns IDs `S109`–`S236`. The lane registry (`corpus/SOURCES.md`) already holds 222+ rows up to `S301`. Staged IDs collide with committed lane records.
3. **No re-groundable entries:** Re-grounding criteria cannot be satisfied in this round because the underlying mechanisms of the staged package (GLib origin writers, Linux rename syscalls, GitLab API housekeeping endpoints) are irrelevant to receipt writer environment isolation.

---

## 5. Sibling Overlap and Contested Scope

### Sibling Overlap
1. **`GIT_NO_REPLACE_OBJECTS` & `refs/replace`:**
   - **`tabi-shokunin` (r36–37):** Hardened C2 operability with B1 `GIT_NO_REPLACE_OBJECTS=1` on every git read, plus `refs/replace/*` enumeration refusal (citing S143).
   - **`kotodama-shokunin` (r80–81):** `tools/ledger-token-guard.py:50,168` refuses any repo carrying `refs/replace/` entries (`git for-each-ref refs/replace/`), and `tools/harness/receipt_guard.py:59` sets `GIT_NO_REPLACE_OBJECTS="1"`.
   - **`tameshi-shokunin` (r59, 82):** `tools/executor-source-pin.py:80,93` and `tools/evidence-disposition.py:55,391,2310` set `GIT_NO_REPLACE_OBJECTS=1` on all git calls because "a replace ref rewrites HEAD; only GIT_NO_REPLACE_OBJECTS restores truth".
   - **`kama-shokunin` (r23, 30):** Evaluates `refs/replace` in fault grids (`tests/report-audit/repo-state-grid.py:251`).
   - **`mado-shokunin` (r67):** Authored `corpus/knowledge/replace-ref-citation-boundaries-r67.md` (source S436) documenting git v2.56.0 replace ref semantics.
   - **`souji-shokunin`:** Holds candidate pin `tools/souji-receipt-write.py:104` (`env["GIT_NO_REPLACE_OBJECTS"] = "1"`), tested in C1 via mutant K6 and matrix row PK6 against `refs/replace/<HEAD>`.

2. **`GIT_COMMON_DIR`:**
   - **`kumitate-shokunin`:** `scripts/receipt-bind.mjs:101-104` drops `GIT_COMMON_DIR` in `GIT_ENV_DROP`.
   - **`kama-shokunin`:** `tools/report-landing-audit.py:148` implements prefix-scrub dropping all `GIT_*`.
   - **`kake-shokunin`:** `scripts/citing_set.py:168` scrubs `GIT_COMMON_DIR` in `GIT_LOCAL_ENV`.
   - **`kotoba-shokunin` / `kotodama-shokunin`:** Include `GIT_COMMON_DIR` in subprocess clean env pop lists.

3. **`GIT_NAMESPACE` & `GIT_CEILING_DIRECTORIES`:**
   - 11 siblings scrub `GIT_NAMESPACE`; 14 siblings scrub or enforce `GIT_CEILING_DIRECTORIES`.
   - In `souji`, `c1-counter.py:406-407` scrubs both from ambient environment in C2.

### Contested Scope
1. **Value-Check vs Scrub (Q22):** Siblings unconditionally scrub `GIT_COMMON_DIR`. Souji alone value-checks caller-injected `GIT_COMMON_DIR` in `tools/souji-receipt-write.py:290-316` (accepting equal value W3, refusing mismatch W1/W2 and empty value).
2. **Refusal vs Inertness on Replace Refs:** `tabi` and `kotodama` refuse repositories containing `refs/replace/`. `souji` does not refuse the presence of replace refs on disk; it neutralizes them by passing `GIT_NO_REPLACE_OBJECTS=1` to all git commands, rendering replaced trees inert so dirty tracking remains honest.
3. **Named Limit L3 (Unchecked Writer Variables):** While siblings scrub `GIT_NAMESPACE` and `GIT_CEILING_DIRECTORIES`, and souji's *counter* scrubs them for C2, souji's *writer* (`tools/souji-receipt-write.py:99`) leaves them unhandled. This divergence remains a frozen named limit (L3).

---

## 6. UFO-FSD Connector Proposal: Non-Obvious Move & Synthesis

### Evidence
1. **Instrument vs Writer Hermeticity Divergence (L3):**
   - `census/round-68/c1-counter.py:406-407` achieves C2 ambient hermeticity by scrubbing `GIT_COMMON_DIR`, `GIT_NAMESPACE`, and `GIT_CEILING_DIRECTORIES` in `clean_env()`.
   - In contrast, candidate `tools/souji-receipt-write.py:99` only scrubs `GIT_DIR`, `GIT_WORK_TREE`, and `GIT_COMMON_DIR`. `GIT_NAMESPACE` and `GIT_CEILING_DIRECTORIES` pass unchecked to git plumbing, frozen as named limit L3 (`census/round-68/preregistration.txt:24`).
2. **Receipt Verification Asymmetry:**
   - Seat `S68ExecTrial` (`trial.md:7, 54, 59`) revealed that writer receipts (`instrument=... instrument_sha256=... rev=... command=...`) cannot be verified using `tools/souji-receipt-run.py verify` (which rejects them with `RECEIPT-MALFORMED`).
   - The lane lacks a native CLI verifier for writer receipts, forcing consumers to rely on ad-hoc shell checks or the entire 42-case C1 counter suite.
3. **Replace-Ref Invariance:**
   - Seat `S68ScoutReplace` (`replace-check.md`) verified that `GIT_NO_REPLACE_OBJECTS=1` neutralizes tree-replacement for `git show` and `git status`, whereas `git ls-files` is index-driven.

### Affected Axes
- **`calibration`** (C1, current score 7): improves by aligning subject writer protections with declared counter checks, eliminating L3 blind spots.
- **`operability`** (C2): improves by ensuring that receipt verification and writer execution operate deterministically across ambient environments and tooling boundaries without breaking C1/C2 invariants.

### Proposed Move (Bound for Round 69)
**Dual-Surface Parity Synthesis:**
1. **Close Named Limit L3 in Writer:**
   Extend `tools/souji-receipt-write.py`:
   - Add `GIT_NAMESPACE` to the `RECEIPT-ENV-REDIRECT-SET` gate (`tools/souji-receipt-write.py:325`), treating caller-injected namespace redirection as a refused redirect (matching `GIT_REPLACE_REF_BASE` and `GIT_OBJECT_DIRECTORY`).
   - Add `GIT_CEILING_DIRECTORIES` to the git subprocess scrub tuple (`tools/souji-receipt-write.py:99`), preventing caller ceiling variables from interfering with repository discovery while allowing internal test containment (`case_37`).
2. **Establish Native Receipt Verification Mode:**
   Add a lightweight `--verify <RECEIPT_PATH>` mode to `tools/souji-receipt-write.py` that verifies:
   (a) header formatting and exit status,
   (b) `instrument_sha256` matches `git show <rev>:<instrument>` under `GIT_NO_REPLACE_OBJECTS=1`,
   (c) absence of unrecorded dirty state.

### Risks
- **Low Risk:** Adding `GIT_NAMESPACE` to `RECEIPT-ENV-REDIRECT-SET` is fail-closed; callers intending custom namespaces must unset them before writing receipts.
- **Zero Risk to Frozen R68:** This move is strictly designed as an unexecuted synthesis for round 69 planning; zero writer or counter bytes are modified in round 68.

### Verification
- Round 69 candidate run of `tools/souji-receipt-write.py` with `GIT_NAMESPACE=probe` exits with `RECEIPT-ENV-REDIRECT-SET: GIT_NAMESPACE set in the writer's environment; unset them and retry`.
- Trial run of `tools/souji-receipt-write.py --verify <receipt>` returns rc 0 on valid receipts and rc 2 on modified sha/content, resolving the runner-verify gap identified by `S68ExecTrial`.
