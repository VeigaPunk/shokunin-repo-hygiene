# r12 reviewer — pre-integration source verification

Author: W2RoundSouji-8.R12Reviewer (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12Reviewer`; this committed copy is the durable form). 2026-10-19.

Verification is complete. I wrote nothing in the lane or fleet root. Out-of-scope writes were six stray downloads in the fleet root, which I reported to Main and W2RoundSouji-8. My scratch copies are in `/var/tmp/souji-r12-gppF6V/`. The fixture repos were removed.

## Verdict: plain `git commit` can run worktree-prune on git 2.55.0

**Yes, with default config.** It was reproduced, not just read from code.

Code path (tag v2.55.0):
1. `builtin/commit.c:1965` calls `run_auto_maintenance(the_repository, quiet)`.
2. `run-command.c:1961-1965`: `maintenance.auto` defaults to enabled. `:1974-1976`: detach defaults to true. `:1980`: spawns `maintenance run --auto --quiet --detach`.
3. `builtin/gc.c:1970-1975`: with no `--schedule`, strategy is `geometric_strategy` (`:1974`) and type is `MAINTENANCE_TYPE_MANUAL` (`:1975`).
4. `gc.c:1916-1918`: the worktree-prune entry is `SCHEDULED | MANUAL`, schedule `WEEKLY`.
5. `gc.c:1989`: `if (!(strategy.tasks[i].type & type)) continue;`. The `--auto` run selects tasks whose type includes MANUAL, so worktree-prune is selected. `--auto` is not a type filter.
6. `gc.c:1992-1999`: the WEEKLY schedule is consulted only under `--schedule`, so it is ignored for `--auto`.
7. `gc.c:1771-1773` (`maybe_run_task`): the `--auto` gate is only `auto_condition`. For worktree-prune that is `worktree_prune_condition` (`gc.c:391-427`), which requires at least one prunable registration (limit default 1, `:394`, `:399`).
8. `gc.c:379-388`: runs `git worktree prune --expire <gc.worktreePruneExpire>`, default `3.months.ago` (`gc.c:162`).
9. `worktree.c:954-956`: a `locked` file means skip. `:1001-1008`: a missing gitdir target is prunable when `worktrees/<id>/index` mtime is `<= expire`.
10. Worktree-prune is background-only (`gc.c:1743`). With default detach it runs after `daemonize()` (`gc.c:1815-1824`).

Reproduction (host git 2.55.0, isolated `HOME` and global config, repos under `/var/tmp`, index aged 100 days, detached worktree directory deleted, then `git commit --allow-empty`):

| case | before | after | admin dir |
|---|---|---|---|
| A default (detach) | 2 | 1 | removed |
| B `-c maintenance.autoDetach=false` | 2 | 1 | removed |
| C `-c maintenance.auto=false` | 2 | 2 | kept |
| D locked + autoDetach=false | 2 | 2 | kept |
| E index 1 day old | 2 | 2 | kept |
| G `maintenance.worktree-prune.enabled=false` | 2 | 2 | kept |

Trace (case B, `GIT_TRACE2_EVENT`): the `commit` argv is followed by `git maintenance run --auto --quiet --no-detach`, then regions `worktree-prune` (×2) and `worktree`.

So the ART claim holds. One wording correction: the geometric entries are `SCHEDULED | MANUAL`, not MANUAL-only. The conclusion is unchanged.

## Claim table

| # | claim | observed (URL, line) | verdict |
|---|---|---|---|
| 1a | `strategy = geometric_strategy;` at 1974 | v2.55.0 `builtin/gc.c:1974` (`https://raw.githubusercontent.com/git/git/v2.55.0/builtin/gc.c`). v2.54.0 is `:1973`; v2.53.0 is `:1983` and reads `strategy = gc_strategy;`. | AGREE |
| 1b | worktree-prune config `3.months.ago` at 162 | `gc.c:162` `.prune_worktrees_expire = xstrdup("3.months.ago")` | AGREE |
| 1c | task 379-388; condition 391-420 | task `gc.c:379-389`; condition `gc.c:391-427` | AGREE |
| 1d | geometric table 1894-1921 | `gc.c:1894-1921`; worktree-prune `:1916-1919` `SCHEDULED \| MANUAL`, `WEEKLY`; reflog-expire `:1912-1915` `SCHEDULED \| MANUAL`, `WEEKLY` | AGREE, refine "MANUAL-type" to `SCHEDULED \| MANUAL` |
| 1e | `--auto` includes MANUAL-type tasks | consumer `gc.c:1989`, `maybe_run_task` `:1771-1773`; confirmed by reproduction | AGREE, verdict above |
| 2a | worktree.c 954-956 locked skip | `worktree.c:954-956` `file_exists(…/locked) → goto done` (rc stays 0) | AGREE |
| 2b | worktree.c 1001-1008 index mtime vs expire | `worktree.c:1001-1008`; prunable when `stat(index)` fails or `st_mtime <= expire` (`:1004`) | AGREE |
| 3 | `run-command.c` ~1980 | `run-command.c:1980` `strvec_pushl(…"maintenance","run","--auto")`; `:1987-1992` `run_auto_maintenance` | AGREE |
| 3b | commit.c calls it | `builtin/commit.c:1965` `run_auto_maintenance(the_repository, quiet);` | AGREE. fetch, merge, am, rebase NOT checked. |
| 4 | RelNotes 2.54.0:58 quote | `RelNotes/2.54.0.adoc:58`: "`git maintenance` starts using the "geometric" strategy by default." | AGREE (exact) |
| 5a | rmlint.1.rst:28 | `docs/rmlint.1.rst:28`: "``rmlint`` itself WILL NOT DELETE ANY FILES." | AGREE |
| 5b | fclones dedupe.rs 815-849 modified_before | `dedupe.rs:843` comment and `:845` `if let Some(max_timestamp) = config.modified_before`; length check skips the file, `:~826-840`. | PARTIAL DISAGREE. The group abort is conditional on `modified_before` being configured. The length check skips individual files, not the group. C4's "aborts a group if any file changed" overstates. |
| 5c | jdupes README TOCTTOU quote | `README.md:249-251` (TOCTTOU at :250); `:323-324` "Do not use it on ANY data set for which any amount of data loss is unacceptable"; `:144` `-Q` WARNING | AGREE |
| 6a | trash spec §5 symlink MUST | `trash-spec.html` (Version 1.0, published 2014-01-02, line 65). §5 quote at lines 226-227: "The implementation also MUST check that this directory is not a symbolic link." | AGREE |
| 6b | trash spec §6 info-first MUST | §6 quote at lines 360-362: "When trashing a file or directory, the implementation MUST create the corresponding file in $trash/info first." O_EXCL at :366. | AGREE |
| 7a | mv copy-then-remove quote | `coreutils mv-invocation.html` lines 77-78: "mv falls back on copying as if by cp -a, then (assuming the copy succeeded) it removes the original." | AGREE |
| 7b | rm `--preserve-root=all` quote | `coreutils rm-invocation.html`: "When 'all' is specified, reject any command line argument that is not on the same file system as its parent." | AGREE |
| 8 | census regexes on 11-column form | synthetic 11-column table, 7 rows: count `7`; malformed `0`; tier `A=4 B=1 C=1 D=1`; duplicate `S003`; enum flags S004 tier, S005 status `watch` and tier-inflation; missing used-by flagged. | AGREE: regexes work on the contract's 11-column form. |
| 8b | ART's 9-column table | same census on a 9-column table: malformed count `1`, row count `1` | DISAGREE with ART. The ART table does not conform to contract v1 (11 columns) and fails the malformed check. |

## Residual risk and verification gaps
- The fetch/merge/am/rebase `run_auto_maintenance` call counts (ART §2 item 1) were not checked.
- The v2.55.0 `builtin/worktree.c` prune path was not opened. The claim it uses `should_prune_worktree` with the same expiry rule rests on `worktree.c:337` and `:929`.
- Fixture counts are from one host (git 2.55.0, Linux). Tests used `GIT_TRACE2` and isolated `HOME`.
- The `gc.c:1042` manual `git gc` path also calls `maintenance_task_worktree_prune` ungated by `maintenance.auto`. I read this in code but did not reproduce it.
- The `/trash-spec/1.0/` URL returned 404. The `/trash/latest/` document reports Version 1.0.
