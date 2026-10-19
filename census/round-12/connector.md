# r12 connector — sibling-overlap scan

Author: W2RoundSouji-8.R12Connector (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12Connector`; this committed copy is the durable form). 2026-10-19.

### 1. Axes & Posture

- **Calibration:** Verify empirical boundary claims against live sibling declarations; never infer absence without an exhaustive sweep.
- **Coverage:** Map sibling frontiers and existing registered sources to prevent redundant external discovery.
- **Operability:** Ground cross-lane failure patterns (auto-maintenance pruning, pathspec leakage, `/tmp` inode exhaustion) into executable lane rules.

---

### (1) Contested Scope Scan: F1 / F3 / F4 Ground

**Finding:** **Zero contested scope.** No sibling lane claims or owns git-native housekeeping (F1), duplicate-file deduplication (F3), or FreeDesktop/same-filesystem restorable quarantine (F4). Souji holds unpartitioned, uncontested authority over these domains.

| Frontier Ground | Scope Definition | Sibling Claims Found | Status | Absence Sweep Command |
|---|---|---|---|---|
| **F1: Git-Native Housekeeping** | `git maintenance run --auto`, `worktree-prune`, `gc.worktreePruneExpire`, `gc.pruneExpire`, `git repack --expire-to`, `git repo structure` | None (`0`) | **Uncontested** | `bash -c 'grep -EIn "git[ -]maintenance|maintenance\.auto|expire-to|gc\.(pruneExpire|worktreePruneExpire)|git\s+repo\s+structure" /home/vgpnk/Projects/shokunin/*-shokunin/{PROVINCE.md,SKILL.md,corpus/README.md} /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/*-shokunin/{PROVINCE.md,SKILL.md,corpus/README.md} 2>/dev/null \| grep -v "/souji-shokunin/" \| wc -l'` $\rightarrow$ `0` |
| **F3: Duplicate-File Verdicts** | Duplicate binary/config finders on disk (`rmlint`, `fclones`, `jdupes`, `fdupes`, `czkawka`, `rdfind`) | None (`0`). Sibling "duplicate" usages govern claim spans (`chousa`), JSON members (`kotoba`), markdown headers (`kotodama`), env keys (`kagi`), process daemons (`kumitate`), or HTTP submissions (`tabi`). | **Uncontested** | `bash -c 'grep -EIn "rmlint|fclones|jdupes|fdupes|czkawka|rdfind" /home/vgpnk/Projects/shokunin/*-shokunin/{PROVINCE.md,SKILL.md,corpus/README.md} /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/*-shokunin/{PROVINCE.md,SKILL.md,corpus/README.md} 2>/dev/null \| grep -v "/souji-shokunin/" \| wc -l'` $\rightarrow$ `0` |
| **F4: Restorable Quarantine** | FreeDesktop Trash specification 1.0, `trash-cli`, same-filesystem atomic renames (`GNU mv`/`rm --one-file-system`, `EXDEV`) | None (`0`). FreeDesktop hits in siblings cover Wayland protocols (`mado`) or systemd D-Bus services (`mori`), never trash/quarantine. | **Uncontested** | `bash -c 'grep -EIn "trash-cli|freedesktop.*trash|trash\s+spec|\.trash\b|one-file-system|same-filesystem" /home/vgpnk/Projects/shokunin/*-shokunin/{PROVINCE.md,SKILL.md,corpus/README.md} /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/*-shokunin/{PROVINCE.md,SKILL.md,corpus/README.md} 2>/dev/null \| grep -v "/souji-shokunin/" \| wc -l'` $\rightarrow$ `0` |

---

### (2) Sibling Adjacency Matrix for Souji PROVINCE.md

| Sibling Lane | Sibling Domain & Province Ref | Souji Boundary / Hand-off Interface | Evidence Command |
|---|---|---|---|
| **`tsukuroi-shokunin`** | Host operability & system repair (`/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/PROVINCE.md:3,18`). Owns pacman state, systemd units/timers, kernel modules, boot triage. Refuses package removal or service restarts. | Tsukuroi diagnoses host OS health and system unit states; Souji removes workspace/repo artifacts and never touches OS packages (`/var/lib/pacman`) or host configuration. | `bash -c 'grep -Hn -E "Domain|Never installs" /home/vgpnk/Projects/shokunin/tsukuroi-shokunin/PROVINCE.md'` |
| **`kagi-shokunin`** | Secrets & vault operations (`/home/vgpnk/Projects/shokunin/kagi-shokunin/PROVINCE.md:3-6`). Owns credential hygiene evidence, shape-only secret detection, env parsing. Refuses git history rewriting. | Kagi owns credential hygiene and secret classification; Souji identifies unreferenced debris and routes sensitive-data-removal (`git-filter-repo`, `S012`/`S015`) and credential findings to Kagi/operator, never reading secret content. | `bash -c 'grep -Hn -E "Domain|Owns|Refuses" /home/vgpnk/Projects/shokunin/kagi-shokunin/PROVINCE.md'` |
| **`mori-shokunin`** | Fleet & host observability (`/home/vgpnk/Projects/shokunin/mori-shokunin/PROVINCE.md:3,6,12`). Owns watchdog liveness, wave settlement, memory pressure/kill signals, resource runway. Refuses remediation. | Mori observes fleet health, progress, and disk runway; Souji acts on abandoned workspace scratch (`.scratch/`, dead worktrees) gated on git-clean and Obsidian receipts, never killing processes. | `bash -c 'grep -Hn -E "Domain|Owns|Refuses" /home/vgpnk/Projects/shokunin/mori-shokunin/PROVINCE.md'` |
| **`chousa-shokunin`** | Deep-research methodology (`/home/vgpnk/Projects/shokunin/chousa-shokunin/PROVINCE.md:3,5,10`). Owns question framing, primary source hierarchy, claim-vs-source verification, referential integrity gates. | Chousa governs research source tiering and referential integrity checking; Souji adopts Chousa's citation standards for `corpus/SOURCES.md` and knowledge entries, applying them to git/filesystem specs. | `bash -c 'grep -Hn -E "Domain|Owns|Refuses" /home/vgpnk/Projects/shokunin/chousa-shokunin/PROVINCE.md'` |
| **`kumitate-shokunin`** | Multi-agent task dispatch & orchestration (`/home/vgpnk/Projects/shokunin/kumitate-shokunin/PROVINCE.md:3-6`; `kumitate-art.md:129,267`). Owns task worktree creation and concurrency locking (`git worktree lock`). | Kumitate locks active worktrees during task dispatch; Souji cleans dead worktree registrations (`git worktree prune`) only after verifying they are unlocked, unreferenced, and all commits are pushed or empty. | `bash -c 'grep -Hn -E "BUGS|lock" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/kumitate-art.md:129'` |

---

### (3) Shared Sources Registered Across Sibling Lanes

| Registered Source & URL | Sibling Registration (ID & Path) | Souji Counterpart (ID & Role) | Cross-Reference Value & Interface | Evidence Command |
|---|---|---|---|---|
| **Git Worktree Documentation**<br>`https://git-scm.com/docs/git-worktree` | `kumitate-art.md:129`<br>`[S009]` (docs, tier A) | `souji-art.md:103`<br>`[S003]` (docs, tier A) | Kumitate documents worktree isolation and `--lock` race-freedom for agent sessions (`kumitate-art.md:267`); Souji uses porcelain `-z` lock attributes to fence `git worktree prune`. | `bash -c 'grep -Hn "git-worktree documentation" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/kumitate-art.md'` |
| **Unofficial Bash Strict Mode**<br>`http://redsymbol.net/articles/unofficial-bash-strict-mode/` | `connect-instruments.md:270` `[S004]` & `connect-sources.md:152` `[S006]` | `souji-verify.sh`, `souji-quarantine.sh` baseline | Standardizes `set -euo pipefail`, pipeline exit unmasking, and preventing SIGPIPE 141 crashes under early-exiting `grep -q`. | `bash -c 'grep -Hn "unofficial-bash-strict-mode" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/connect-instruments.md'` |
| **FreeDesktop.org Specifications**<br>`https://specifications.freedesktop.org/` | `mado-art.md:40-59` (`S009`-`S028`) & `mori-art.md:101-109` (`S007`-`S015`) | `souji-art.md:122`<br>`[S022]` (Trash Spec 1.0) | Shared XDG filesystem governance (`$XDG_DATA_HOME/Trash`, `.Trash`, `.Trash-$UID`). S022 establishes restorable quarantine without home directory clutter. | `bash -c 'grep -Hn "Trash Specification" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/souji-art.md'` |
| **ShellCheck SC2115 / SC Rules**<br>`https://github.com/koalaman/shellcheck/wiki/SC2115` | `driver.md:13,203-204`<br>(checks watchdog scripts) | `souji-art.md:127`<br>`[S027]` (docs, tier A) | Fleet-wide bash linting: ShellCheck treats `SC2115` (`rm -rf "$VAR/"*`) as `warning`. `-S error` blinds gates to catastrophic root deletion; both lanes require warning-level checks. | `bash -c 'grep -Hn "SC2115" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/souji-art.md'` |
| **Removing Sensitive Data from Git**<br>`https://docs.github.com/en/authentication/.../removing-sensitive-data-from-a-repository` | `kagi-art.md:172-173`<br>(Gitleaks S028, TruffleHog S029) | `souji-art.md:115`<br>`[S015]` & S012 (`git-filter-repo`) | Kagi detects secret leaks in working files and commits; Souji flags repository size/pack bloat, referencing S015/S012 while explicitly refusing history rewrites. | `bash -c 'grep -Hn "Removing sensitive data" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/souji-art.md'` |

---

### (4) Cross-Lane Patterns Worth a Souji Lesson

| Pattern & Hazard | Fleet Manifestation & Sibling Evidence | Root Cause | Souji Lesson & Guard Rule | Evidence Command |
|---|---|---|---|---|
| **`/tmp` Quota & Inode Exhaustion** | - `kotodama`: `/tmp` inode table 100% full (`round-10.md:23`, `round-11.md:29`, `l0.md:109`).<br>- `game-dev-3d`: `/tmp` quota caused `mktemp` failures despite free disk space (`r105-unreal-lifecycle.md:111`).<br>- `kotoba`: test harness wiped under disk quota (`round-12.md:44`).<br>- `souji`: host `/tmp` quota broke fixture runs (`round-8.md:24`). | Unbounded shared tmpfs `/tmp` fills up under concurrent multi-agent runs through inode exhaustion or file count caps. | Fixtures and quarantine staging must NEVER run in `/tmp`; MUST use `/var/tmp/souji-r12-XXXXXX` or per-lane `$HOME/.cache/` with explicit trap cleanups and `df -i` checks. | `bash -c 'grep -Hn -E "inode-exhausted|table 100% full" /home/vgpnk/Projects/shokunin/kotodama-shokunin/corpus/lessons/round-10.md /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/l0.md'` |
| **Unanchored `git add -A` Scope-Adds** | - `kotoba`: `corpus/` pathspec swept sibling's lesson into commit (`mistakes.md:273` M072).<br>- `kengaku`: `git add` pathspec failure left scorer and lesson uncommitted (`kengaku-state.md:194` M10).<br>- `souji`: `git add -A` swept 10 live `.scratch/*.out` and an in-flight report into commit `e20f4fa` (`souji-state.md:153-158`). | Blanket staging flags (`-A`, `.`) ignore live background processes and sweep unverified scratch or sibling checkouts. | Hygiene commits must NEVER use `git add -A` or unanchored pathspecs; MUST stage explicitly enumerated paths (`git add -- <paths>` or `git commit -- <paths>`). | `bash -c 'grep -Hn "M072" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/mistakes.md'` |
| **Git Background Auto-Maintenance (`maintenance.auto`)** | - `souji`: Git 2.54+ defaults unscheduled maintenance to `geometric`, causing porcelain commands (`commit`, `fetch`, `merge`, `rebase`) to trigger `git maintenance run --auto` in the background, which runs `worktree-prune` and deletes unregistered worktree metadata without a receipt (`souji-art.md:35,164-196`).<br>- `kumitate`: Claude Code prevents concurrent deletion by holding `git worktree lock` during execution (`kumitate-art.md:78,260,267`). | Git porcelain commands execute background cleanup tasks by default when unmanaged. | All automated hygiene commits must pass `-c maintenance.auto=false`; prunable worktrees containing unpushed commits must be held with `git worktree lock --reason`. | `bash -c 'grep -Hn -C 2 "maintenance.auto" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/souji-art.md:174'` |
| **ShellCheck Severity Masking (`-S error`)** | - `souji`: 8 of 10 recorded shellcheck invocations used `-S error` (`souji-art.md:362-364`). `SC2115` (`rm -rf "$VAR/"*`) is warning severity, allowing fatal empty-variable deletions to pass exit 0. | Using `-S error` in CI/gating hides all ShellCheck warnings, including catastrophic empty-path expansions. | All deletion and quarantine scripts must pass `shellcheck -S warning -i SC2115,SC2114`. | `bash -c 'grep -Hn -C 2 "SC2115" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/souji-art.md:362'` |
| **Symlinked Quarantine Escape** | - `souji`: in r10 C2-Q1, a symlinked `.ufo-quarantine` directory followed references outside repo bounds (`census/round-10/S06-cluster-C-member2.md:53-63`).<br>- FreeDesktop Trash Spec 1.0 § 5 requires top-level `.Trash` to not be a symbolic link (`souji-art.md:122,275`). | Naive directory creation follows symlinks across filesystem boundaries. | Quarantine roots must be verified with `test -L` and `stat -c %d` (same filesystem device) before staging files. | `bash -c 'grep -Hn -C 2 "symlink" /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/souji-art.md:275'` |

---

### (5) Recommended 3-Line `## Adjacent` Block for Souji PROVINCE.md

```markdown
## Adjacent

- mori observes fleet runway/scratch; tsukuroi repairs OS substrate without deleting files; souji removes workspace artifacts under receipts, never touching processes or host packages.
- kagi owns credential hygiene and secret classification; souji detects unreferenced debris and routes sensitive-data removal (git-filter-repo) or credential leaks to kagi/operator.
- kumitate locks live worktrees during task dispatch; chousa sets source hierarchy and citation integrity; souji validates dead metadata and cross-references authoritative git/filesystem specs.
```
