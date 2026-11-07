# ConnSources — Cross-Source Pattern Finder & Assimilation Mapping for C2

## Status
STATUS: PASS — cross-source audit complete: 134 staged package rows in `SOURCES.append.md` compared against 132 lane rows in `corpus/SOURCES.md`; mapped all 24 ID collisions (14 already held under earlier lane IDs, 2 rejected, 8 unassimilated); evaluated the F4 origin-record cluster (S152, S210, S211, and S022-adjacent rows), the F3 near-duplicate taxonomy cluster (S118, S122, S136, S145, S151, S213–S217), and 6 cross-cluster rows; formulated a bounded connector synthesis to commit a canonical renumber & alias map, neutralizing the C2 kill-rule vulnerability.

## Evidence

1. **Lane revision base & frozen before-counters**:
   - Command: `git rev-parse HEAD` in `/home/vgpnk/Projects/shokunin/souji-shokunin`
   - Output: `e78ac7c4837b81b634db4a927605a751a7f006ba` (HEAD == origin/master, ahead=0).
   - Registry row count at base: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `132`.
   - Grounded F4 count at base: `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` → `2` (`quarantine-staging-no-copy-r23.md`, `quarantine-origin-record-fields-r24.md`).
   - Quote (`.ufo/waves/round-27/preregistration.txt:7`, 21 words): "Kill rule: any counter failing, or the id-collision proof producing a nonempty collisions set without a committed renumber map, fails C2."

2. **Staged package inspection (`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`)**:
   - Total staged rows: 134 rows spanning ID range `S109` to `S242`.
   - Staged F4 reference writer row S152 (`gio/glocalfile.c` tag 2.84.0).
   - Quote (`SOURCES.append.md:50`, 14 words): "the record is written by GLib's local-file trash, and its writer's guarantees are explicit"
   - Staged F3 near-duplicate taxonomy row S118 (Broder 1997).
   - Quote (`SOURCES.append.md:16`, 17 words): "similarity splits into two distinct measures - resemblance and containment - each a number between 0 and 1"
   - Staged F3 empirical threshold row S216 (Breitinger et al. 2014).
   - Quote (`SOURCES.append.md:120`, 15 words): "a low t increases the false-positive rate while a high t decreases the true-positive rate"

3. **ID collision reproduction (`.ufo/waves/round-27/assimilation/collisions`)**:
   - Exact §10 comm command:
     ```bash
     grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort > reg-ids
     grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > staged-ids
     comm -12 reg-ids staged-ids > collisions
     ```
   - Observed output: exactly 24 collisions (`S109` through `S132`), byte-identical to committed `.ufo/waves/round-27/assimilation/collisions`.
   - Quote (`corpus/SOURCES.md:152`, 18 words): "fetch, pull, merge and rebase each take a stale worktree registration 2 to 1 with no souji receipt"

## Findings

### 1. F4 Origin-Record Cluster & S022-Adjacent Rows
The lane registry currently holds `S022` (FreeDesktop Trash Spec layout: `.trashinfo` format, `files/` and `info/` directories), `S023` (`trash-cli`), `S112` (`gio(1)` CLI trash read/restore), `S113` (`g_file_trash()` method reference: recoverability and refusal contract), and `S114` (`statx(2)` identity fields). The staged set provides the missing reference writer sequence, the three-phase mechanism separation, temporary-file exclusivity, and substrate standards:

| Staged ID | Aspect Not Held | Recommended Action | Rationale / Mapping |
|---|---|---|---|
| S152 | Reference implementation writer sequence: `O_CREAT / O_EXCL` creation, unique-name loop, URI-escape, content write before payload move, failure rollback unlinks info file | **adopt** | Preregistered in C2. Re-grounded at GLib tag 2.84.0 in `origin-record-writer-r27.md`. ID S152 > S132 (no collision). |
| S210 | Order and complementary roles of the three mechanisms: exclusive create is name reservation (descriptor closed empty), content write is by path with `CONSISTENT / ONLY_EXISTING`, rollback unlinks reservation. Proves existence != final content | **adopt** | Preregistered in C2. Re-grounded at GLib tag 2.84.0 in `origin-record-mechanism-set-r33.md`. ID S210 > S132 (no collision). |
| S211 | Where `O_EXCL` sits: in `g_file_set_contents_full`, `O_EXCL` belongs to temporary file (`g_mkstemp_full`), while destination safety is handled by `ONLY_EXISTING` plus atomic `g_rename` | **adopt** | Preregistered in C2. Re-grounded at GLib tag 2.84.0. ID S211 > S132 (no collision). |
| S146 | Reference reader parser implementation: `daemon/trashlib/trashitem.c` parsing `[Trash Info]`, `Path`, `DeletionDate`, URI unescaping, relative path base resolution | **adopt** | Queue for future reader mechanism grounding; complements S022 spec and S152 writer. ID S146 > S132. |
| S158 | Substrate guarantee: IEEE Std 1003.1-2024 `open()` specifying atomicity of `O_CREAT / O_EXCL` existence check + creation and `[EEXIST]` on concurrent collision | **adopt** | Provides normative POSIX substrate grounding for S152/S210 name reservation. ID S158 > S132. |
| S159 | Substrate guarantee: IEEE Std 1003.1-2024 `rename()` specifying atomicity of publishing and destination preservation on failure (untouched unless `[EIO]`) | **adopt** | Provides normative POSIX substrate grounding for S211 atomic publication. ID S159 > S132. |
| S173 | Substrate durability: IEEE Std 1003.1-2024 `fsync()` defining the boundary of crash-resilience vs directory entry atomicity | **adopt** | Grounding for future durability analysis; atomicity alone does not survive kernel panics. ID S173 > S132. |
| S115 | `mv(1) --no-copy` staging verb refusing cross-filesystem copy fallback | **already-held** | Already held in lane as `S111` (`corpus/SOURCES.md:132`). Numeric ID collision S115. |
| S116 | Atomic `RENAME_NOREPLACE` kernel primitive in `rename(2)` | **already-held** | Already held in lane as `S110` (`corpus/SOURCES.md:131`). Numeric ID collision S116. |
| S117 | `statx(2)` identity fields (`stx_ino`, `stx_nlink`, `stx_btime`, `stx_mnt_id`) | **already-held** | Already held in lane as `S114` (`corpus/SOURCES.md:135`). Numeric ID collision S117. |
| S124 | Host device probe confirming `RENAME_NOREPLACE` returns `EEXIST` on existing targets | **already-held** | Already held in lane as `S109` (`corpus/SOURCES.md:130`). Numeric ID collision S124. |
| S125 | `statx(2)` `STATX_MNT_ID_UNIQUE` Linux 6.8+ guarantee for cross-reboot receipt keying | **adopt** | Distinguishes ephemeral mount IDs from reboot-persistent receipt keys. Needs renumbering to S136+ (collides with lane S125). |
| S126 | `g_file_trash()` API contract: recoverable, refusal on system mounts | **already-held** | Already held in lane as `S113` (`corpus/SOURCES.md:134`). Numeric ID collision S126. |
| S133 | Probe testing 8 filesystem paths over `RENAME_EXCHANGE` and `RENAME_WHITEOUT` | **adopt** | Expands S109's 5-directory probe to swap and whiteout primitives. Needs renumbering to S137+. |
| S137 | `gio(1)` CLI commands (`gio trash --list`, `--restore`) | **already-held** | Already held in lane as `S112` (`corpus/SOURCES.md:133`). Numeric ID collision S137. |

### 2. F3 Near-Duplicate Taxonomy Cluster (S213–S217 and Neighbours)
The lane corpus currently deferentially marks duplicate detection as an "OPERATOR DECISION" (`corpus/knowledge/dupe-finders-detect-then-act.md`) based on tool behavior (fclones S020/S021). It lacks mathematical definitions, empirical threshold studies, byte-comparison oracles, and receipt gap evidence:

| Staged ID | Aspect Not Held | Recommended Action | Rationale / Mapping |
|---|---|---|---|
| S118 | Mathematical foundation of near-duplicate detection: splits similarity into two asymmetric metrics — *resemblance* ($r \in [0, 1]$, set intersection / Jaccard similarity) and *containment* ($c \in [0, 1]$), establishing that "duplicate" is a thresholded family of mathematical verdicts rather than a binary equivalence relation | **adopt** | Andrei Z. Broder (1997). Foundational paper for near-duplicate taxonomy. Renumber to S138 (lane S118 is occupied by Qiita S118). |
| S122 | Hard-link identity rule: `link(2)` kernel rule that two paths sharing `(stx_dev, stx_ino)` are identical inodes; duplicate detection must check inode identity before byte comparison to avoid false duplication | **adopt** | Essential safety rule for duplicate finders. Renumber to S139 (lane S122 is occupied by `builtin/count-objects.c`). |
| S136 | Deterministic byte-equality oracle: `cmp(1)` tri-state exit contract (0 = identical, 1 = different, 2 = trouble/I/O error), distinguishing true mismatch from operational faults | **adopt** | Foundational primitive for exact-duplicate receipt generation. Staged ID S136 is free in the lane (lane is at S132). |
| S145 | Architectural receipt census: proves lane machine receipts support 3 classes (pushed, moved-to-obsidian, stale) + `SAFE(metadata-prune)`, with `duplicate` named in docs but completely unimplemented | **adopt** | Evidence grounding for F3 roadmap. Staged ID S145 is free in the lane. |
| S151 | Historical decision audit: proves corpus deliberately deferred duplicate actions as an "OPERATOR DECISION" (K3), establishing that inaction is an explicit safety stance | **adopt** | Prevents erroneous "unhandled bug" classifications. Staged ID S151 is free in the lane. |
| S213 | Canonical bibliographic identity for Breitinger et al. (IFIP DF 2014, DOI 10.1007/978-3-662-44952-3_11) and resolution of direct PDF download URI (`https://inria.hal.science/.../978-3-662-44952-3_11_Chapter.pdf`) | **adopt** | Bypasses the bot-blocked landing page that stalled earlier rounds. ID S213 > S132. |
| S214 | Pinned history of Gitea GC config: proves `cron.git_gc_repos` existed at v1.15.0 and refutes phantom ledger name `git_weekly_gc` | **reject** | Negative history disproving a defunct ledger typo; low operational value. |
| S215 | Pre-cron Gitea config: documents `GC_INTERVAL_TIME` and `GC_ARGS` at v1.12.0 | **reject** | Negative history; obsolete configuration knobs. |
| S216 | Empirical similarity threshold study: analyzes ssdeep match score thresholds ($t = 40$ vs $t = 60$) over 4,457 files; demonstrates that threshold choice is an empirical trade-off between false-positive rate and true-positive rate dependent on the corpus | **adopt** | Core literature authority proving duplicate thresholds cannot be set a priori. ID S216 > S132. |
| S217 | Unpaywall routing record for 10.1007/978-3-662-44952-3_11 (HAL vs publisher PDF) | **reject** | Ephemeral routing discovery metadata; S213 and S216 capture canonical identity and text. |

### 3. Cross-Cluster Rows (F1 Git Maintenance & F2 Size Census / Reclamation)
Six additional staged rows evaluated across themes:

| Staged ID | Aspect Not Held | Recommended Action | Rationale / Mapping |
|---|---|---|---|
| S119 | Simplified Chinese translation of git-fetch auto-maintenance flag | **reject** | Corroboration only; zero semantic difference from English S128; no snapshot pin. Gate reject in `origin-record-writer-r27.md`. |
| S144 | Self-hosted Git GC cron configuration: Forgejo cheat sheet exposing `@every 72h` schedule, disabled by default, defining an operator-controlled periodic deadline rather than a vendor quota lock | **adopt** | Introduces the schedule-shaped reclamation deadline pattern. ID S144 > S132. |
| S149 | Multi-vendor corroboration of self-hosted `@every 72h` GC cron (Gitea Simplified Chinese) | **adopt** | Corroborates self-hosted periodic GC patterns across independent forks. ID S149 > S132. |
| S150 | Scheduled reachability census: Gitea `cron.repo_health_check` running `git fsck --unreachable --tags` at `@midnight` by default | **adopt** | Industry operational precedent for automated reachability sweeps matching lane census methods. ID S150 > S132. |
| S218 | Normative definition of `gc.worktreePruneExpire`: defaults to `3.months.ago`, accepted values (`now`, `never`), and trigger (`git gc`) | **adopt** | Crucial F1 authority proving unmanaged worktrees face a 3-month expiration under stock Git. ID S218 > S132. |
| S220 | Normative scope of `maintenance.<task>.enabled`: documents that the `gc` maintenance task executes `git gc`, which triggers worktree pruning | **adopt** | Connects porcelain auto-maintenance triggers to worktree pruning. ID S220 > S132. |

### 4. Anatomy of the 24 ID Collisions (`S109`–`S132`)
The 24 collisions identified by `comm -12` between the lane's registry and the staged package are an artifact of shokuknow's historical staging sequence. A comprehensive semantic mapping reveals:
- **14 rows already held under earlier lane IDs**:
  - Staged S109 (`git-fetch(1)`) → Held as **Lane S128**
  - Staged S110 (`builtin/fetch.c, merge.c...`) → Held as **Lane S129**
  - Staged S111 (`builtin/pull.c`) → Held as **Lane S130**
  - Staged S112 (`git-count-objects(1)`) → Held as **Lane S115**
  - Staged S113 (`git-fsck(1)`) → Held as **Lane S116**
  - Staged S114 (`git-prune(1)`) → Held as **Lane S117**
  - Staged S115 (`mv(1) --no-copy`) → Held as **Lane S111**
  - Staged S116 (`rename(2)`) → Held as **Lane S110**
  - Staged S117 (`statx(2)`) → Held as **Lane S114**
  - Staged S123 (`r23-trigger-prune.sh`) → Held as **Lane S131**
  - Staged S124 (`noreplace_probe.py`) → Held as **Lane S109**
  - Staged S126 (`g_file_trash()` method) → Held as **Lane S113**
  - Staged S131 (`r23-worktree-census.out`) → Held as **Lane S132**
  - Staged S125 (`statx(2)` URL) → Held as **Lane S114** (scope refinement needed)
- **2 rows rejected**:
  - Staged S119 (`git-fetch` zh-Hans) → Corroboration only; no semantic gain.
  - Staged S120 (`Pro Git ja`) → Popular exposition; low priority.
- **8 unassimilated candidate rows**:
  - Staged S118 (Broder resemblance/containment) → Needs renumbering (lane S118 is Qiita).
  - Staged S121 (Bitbucket Cloud ja) → Unassimilated vendor doc.
  - Staged S122 (`link(2)`) → Needs renumbering (lane S122 is `builtin/count-objects.c`).
  - Staged S127 (GitLab 30-min GC grace) → Unassimilated hosted doc.
  - Staged S128 (Alibaba Cloud 90% quota lock) → Unassimilated hosted doc.
  - Staged S129 (Bitbucket maintain repo ja) → Unassimilated vendor doc.
  - Staged S130 (`r23-garbage-probe.out`) → Unassimilated probe.
  - Staged S132 (`r24-fleet-config-census.out`) → Unassimilated census.

## Non-obvious Move (Connector Proposal)

### Proposed Move
**Commit a canonical, machine-checkable assimilation renumber & alias map (`corpus/assimilation-map.tsv` or `.ufo/waves/round-27/assimilation/renumber-map.tsv`) that resolves every colliding staged ID (S109–S132) to its existing lane alias or allocated forward ID, explicitly closing the C2 kill-rule vulnerability.**

Specifically:
1. Generate `renumber-map.tsv` containing 4 columns: `staged_id`, `status` (`aliased`, `admitted`, `rejected`, `projected`), `lane_id` (e.g. `S111`, `S152`, `—`, `S138`), and `canonical_name`.
2. Map all 24 colliding rows: the 14 aliased rows resolve to their active lane IDs (e.g. `S115` → `S111`), the 2 rejected rows mark `—`, and the 8 unassimilated rows receive pre-allocated non-colliding IDs (`S136`–`S143`).
3. For round-27 admitted rows (`S152`, `S210`, `S211`), record `admitted` with identity mapping `S152` → `S152`.
4. Add a one-line assertion in `tools/souji-landing-gate.py` verifying that any ID present in `assimilation/collisions` is accounted for in `renumber-map.tsv`.

### Evidence
- `preregistration.txt:7` frozen kill rule: "the id-collision proof producing a nonempty `collisions` set without a committed renumber map, fails C2".
- `.ufo/waves/round-27/assimilation/collisions` contains 24 rows (`S109`–`S132`).
- `CritAssimAttack.md` Finding 1 and Attack Log A1 explicitly warn: `collisions` is nonempty and no renumber map exists, leaving C2 vulnerable to literal failure by strict audit.
- Sibling `ExecAssimMirror.md` bypassed this by observing that adopted IDs S152/S210/S211 are disjoint from collisions, but left the literal kill-rule clause unsatisfied in the tree.

### Affected Axes
- **Coverage (8)**: **Improves**. Formally fulfills the frozen C2 kill-rule contract ("without a committed renumber map, fails C2"). Prevents accidental duplicate admissions in future waves by permanently indexing aliases.
- **Calibration (7)**: **Improves**. Reconciles the mathematical collision set (`comm -12` = 24 rows) with repository truth (14 rows were previously assimilated under different IDs). Replaces ambiguous text narratives with a structured, verified TSV.
- **Operability (8)**: **Harms none**. Requires zero new tool dependencies; introduces a deterministic 24-row TSV consumable by `souji-gate-check.py` and `sources-census.sh`.

### Risks
- **Registry monotonicity**: Appending S152, S210, S211 after S132 creates gaps (S133–S151, S153–S209).
  - *Mitigation*: Empirical test in `ExecAssimMirror.md` and `scripts/sources-census.sh:637-641` confirms the validator only checks `E02` (format) and `E03` (uniqueness), tolerating non-contiguous IDs. The renumber map explicitly reserves the intervening slots for the unassimilated colliding rows (e.g. S118 Broder → S138).

### Verification
- `test -s .ufo/waves/round-27/assimilation/renumber-map.tsv`
- `comm -23 <(sort .ufo/waves/round-27/assimilation/collisions) <(cut -f1 .ufo/waves/round-27/assimilation/renumber-map.tsv | sort)` emits empty output (0 unmapped collisions).
- `python3 -B tools/souji-landing-gate.py --root . --rev HEAD --round 27 --fleet-root /home/vgpnk/Projects/shokunin` passes without collision defects.

## Attack Log
None: not an attack seat; no frozen predicate, target, or case set is challenged.
