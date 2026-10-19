# r12 executor (re-dispatch) — K1/K2 verification notes

Author: W2RoundSouji-8.R12ExecGit2 (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12ExecGit2`; this committed copy is the durable form). 2026-10-19.

**Files changed**
- `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`
- `corpus/knowledge/git-grace-periods-and-expire-to.md`

**Behavior documented**
- K1 traces commit auto-maintenance through Git 2.55.0’s geometric strategy to worktree pruning, including the correction that the task is `SCHEDULED | MANUAL` and `WEEKLY`, while `--auto` selects its manual type without applying the weekly schedule filter. It also records the lock, missing-target, index-expiry, and threshold conditions.
- K2 records the distinct Git expiry defaults, forced-prune warning, `--expire-to` backup use, and the current souji hold without proposing a hold-period change.

**Evidence and line verification**
- Verified the cited Git v2.55.0 source ranges: `commit.c:1965`; `run-command.c:1961-1992`; `gc.c:162, 379-427, 1042-1044, 1771-1773, 1894-1921, 1970-1999`; and `worktree.c:949-1008`. The task classification correction is confirmed at `gc.c:1916-1919`.
- Verified the exact RelNotes quote at `2.54.0.adoc:58`, the `maintenance.auto` “Defaults to true.” wording at installed `git-maintenance.1.txt:523-531`, and the worktree lock/prune guidance at `git-worktree.1.txt:58, 167-168`.
- Verified K2’s expiry values in installed Git 2.55.0 `git-gc.1.txt:321-327, 338-352, 395-408`; the `--prune=now` warning at `:110-114, 414-440`; `--expire-to` backup wording at `git-repack.1.txt:130-135`; and the soft-deletion-delay quote in Google SRE § First Layer: Soft Deletion.
- The retained fixture results show plain commit and direct auto-maintenance pruning `2→1`; auto-off, locked, and fresh controls stay `2→2`. The reachability probe shows the detached commit absent from refs/reflogs, unreachable, present after default-expiry pruning, and absent after `--prune=now` (`tests/results/r12-maintenance-guard.txt:11-16, 33-40`). The independent reproduction and correction are recorded in `census/round-12/reviewer-preflight.md:7-36`.

**Call sites, risks, and blockers**
- The cached Git source search found one direct `run_auto_maintenance` occurrence each in `am.c:1942`, `fetch.c:2885`, `merge.c:509`, and `rebase.c:572`; this does not establish exhaustive trigger coverage. The manual `git gc` worktree-prune path was verified in code only, not reproduced.
- **[INFERENCE]** The assignment describes the fleet-root M53 incident, but `corpus/lessons/round-12.md` was absent on direct read in this lane. K1 labels those details assignment-supplied rather than independently verified.
- No implementation blocker. I did not run the fixture or other checks; the parent should run `bash tests/fixtures/r12-maintenance-guard.sh` after integration.
