STATUS: DONE — No unbounded repository-file open found in the list-phase guards.

# Attacked claim

C1 operability: “list-phase guards are bounded.” Axes reviewed: per-repository open coverage (primary) and discovery-time latency (residual).

# Findings

## No in-scope defect found — list-phase repository-file opens are under the watchdog

`list_repos()` (tools/souji-census.sh:1386–1438) does not call a guard and contains no `read <`, `tr`, `cmp`, or `git` repository-file open. It gathers immediate-child candidates by glob and classifies them using path/type tests at 1392–1433; it sorts repo paths at 1435–1437. `emit_census()` calls it at 1660, then sends each candidate through `run_repo_with_watchdog ... guard_repo_candidate` at 1665–1671. `guard_repo_candidate()` dispatches repository dirs to `guard_git_surface`, gitfiles to `guard_git_pointer`, symlink candidates to `guard_target`, and ordinary paths to a no-op (1440–1455). `run_repo_with_watchdog()` starts the worker in its own job-control process group at 1478–1480 and starts the timeout watchdog at 1482–1502.

Repository-file opens reachable from those candidate guards:

| Open | Guard path / evidence | Under per-repo bound? |
| --- | --- | --- |
| `tr -d '\000' < "$cfg"` and `cmp -s -- - "$cfg"` read the config file (738); `git config --file "$cfg" ...` reads it at 741 and 744, and conditionally at 794. Includes are explicitly guarded and recursively scanned at 757–771; `config.worktree` is scanned by `guard_wt_config()` at 817–833. | `guard_git_config()` / `guard_git_surface()` (838–855, 945–1026), reached from the `repo` candidate dispatch (1445–1449). | Yes: each runs in the `guard_repo_candidate` worker launched at 1670–1671. |
| The line-oriented read of `objects/info/alternates` at 548–558. | `guard_alternates()` recurses over alternates files (537–563), called by `guard_git_surface()` at 980 and 1022. | Yes: candidate guard worker at 1670–1671. |
| `.git` pointer line read at 863; worktree registration `gitdir` read at 900; linked-worktree `.git` pointer read through `gitfile_admin()` at 912; registration `commondir` read at 923; main gitdir `commondir` read at 966; `.git` file read at 986 and its `commondir` read at 1008. | `gitfile_admin()` / `guard_git_pointer()` (861–884), `guard_worktree_registrations()` (889–940), and `guard_git_surface()` (945–1026). | Yes: all are called via the candidate guard worker at 1670–1671. |

The guard performs additional filesystem checks that are not file-content opens: `guard_git_links()` traverses symlink metadata with `find` (565–580); `guard_git_files()` type/link-count checks with `stat` (589–628); and config-file-kind checks use `-f`/`stat` (709–719). They are likewise inside the candidate worker. `guard_git_surface()` calls the remaining checks before returning, including the worktree-registration scan (945–1026).

The separate measurement worker is also covered: `emit_census()` passes the entire `census_one "$repo"` invocation to `run_repo_with_watchdog` at 1697–1699. Thus its Git reads (including worktree/unpushed counts, status/config/attributes queries, and linked-worktree status) execute in that worker, not in the outer emitter (see `count_worktrees` 1041–1045, `count_unpushed` 1047–1059, `status_info_file` 1068–1104, `guard_bound_filters` 1109–1144, `count_dirty` 1147–1178, `worktree_extra_flags` 1258–1300, and `census_one` 1303–1384).

Protected refusal remains a distinct error path: `run_repo_with_watchdog()` returns status 2 before the timeout return at 1645–1649, and the emitter exits 2 for that status at 1674–1676 and 1703–1705.

**Verdict:** The scoped claim holds: no repository-file open in list-phase guard work occurs before or outside its per-repository watchdog. No smallest fix is indicated for this attack.

# Residual risk and verification gaps

`list_repos()` itself is outside the per-repository watchdog: its immediate-child glob, `.git` type tests, and sort at 1407–1437 are fleet/root-wide discovery work. Those operations are not `read <`, `tr`, `cmp`, or `git` content opens, so they do not establish the requested unbounded-open failure; they can nevertheless add unbounded discovery latency on a very large or stalled filesystem. The 600s/default or configured per-repo timeout begins only when each candidate worker starts.

LSP was unavailable: `read xd://lsp` returned `No such tool: xd://lsp`; the mounted device list did not expose an LSP route. I used exact-file reads and literal search as the fallback; no grep result is treated as semantic proof.

# Revision and command evidence

Commands run:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 5efb519f00075d958c3d1109ef6fcb24c487eb87:tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh
```

Observed outputs, in order:

```text
5efb519f00075d958c3d1109ef6fcb24c487eb87
03b763550487e3c758ed4e61e031627c199e9b84
4b90562b66ec4d636a4416583a111eebe05e66a6
```

Diff command:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --unified=4 b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tools/souji-census.sh
```

Observed diff summary: `tools/souji-census.sh | 631 +++++++++++++++++++++++-`; `1 file changed, 592 insertions(+), 39 deletions(-)`. The checked-out `HEAD` is the assigned tip; source line references above are from that file.