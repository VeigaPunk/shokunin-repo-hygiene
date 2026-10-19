source: S002 git-gc(1) § OPTIONS/CONFIGURATION/NOTES (installed Git 2.55.0; https://git-scm.com/docs/git-gc); S004 git-repack(1) --expire-to (installed Git 2.55.0; https://git-scm.com/docs/git-repack); S029 Google SRE ch.26 § First Layer: Soft Deletion (https://sre.google/sre-book/data-integrity/)
verified-at: 2026-10-19 — installed Git man pages 2.55.0; host git 2.55.0
recheck: man git-gc | grep -nE '2.weeks|3.months|90 days|30 days|60 days|15 days'

# Git grace periods are separate from souji's quarantine hold

## Git defaults (S002, installed 2.55.0)
- Loose/unreachable objects: `gc.pruneExpire` defaults to `2.weeks.ago`; `git gc` calls `prune --expire 2.weeks.ago` (`git-gc.1.txt:316-330`, especially :321-327).
- Reflog entries: `gc.reflogExpire` defaults to 90 days (`git-gc.1.txt:343-347`).
- Unreachable reflog entries: `gc.reflogExpireUnreachable` defaults to 30 days (`git-gc.1.txt:349-363`).
- Stale worktree admin files: `gc.worktreePruneExpire` defaults to `3.months.ago` (`git-gc.1.txt:333-341`).
- Rerere records: resolved are kept 60 days; unresolved, 15 days (`git-gc.1.txt:395-408`).

## Early expiry and backup
`--prune=now` ignores object age and “increases the risk of corruption if another process is writing to the repository concurrently” (`git-gc.1.txt:110-114`). For cruft repacking, `git repack --cruft -d --expire-to=<dir>` writes pruned objects to a separate directory; the man page calls this “useful for keeping a copy of any pruned objects in a separate directory as a backup” and says it is only useful with `--cruft -d` (`git-repack.1.txt:130-135`).

## Comparison with souji's hold
Google SRE § First Layer: Soft Deletion says: “Common choices of soft deletion delays are 15, 30, 45, or 60 days.” Git's object, reflog, worktree-metadata, and rerere expiries are distinct mechanisms and config values, not souji hold settings. The current SKILL hold is at least one driver tick / 450 seconds, with 24 hours preferred for anything not pushed (`SKILL.md:45-46`). Changing that hold is an operator/SKILL decision; this entry records facts only.

## Failure case (Q3)
Git documents that `--prune=now` can risk corruption with concurrent writers (S002, `git-gc.1.txt:113,414-440`). Separately, the r12 reachability probe found the detached worktree commit absent from refs and reflogs, marked unreachable, still present after default two-week pruning, and absent after `gc --prune=now` (`tests/results/r12-maintenance-guard.txt:33-40`). The fixture demonstrates deletion of that orphaned commit under forced expiry; it does not simulate concurrent-writer corruption.
