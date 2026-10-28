# S258 registry row draft (seat R41scribe04, round 41)

## (1) Registry row

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S258 | git/git source at tag v2.56.0: builtin/worktree.c, worktree.c — https://github.com/git/git/blob/v2.56.0/builtin/worktree.c | code | A | which registrations `git worktree prune` deletes at git 2.56.0 and how --expire gates them; not the maintenance trigger (S001, S009), not the list-time prunable label (S232), not lock semantics (S003) | tag v2.56.0: builtin/worktree.c prune_worktrees() :212-246 with should_prune_worktree call :229, prune --expire option :254-255, expire = TIME_MAX :259; worktree.c worktree_prune_reason :329-345, should_prune_worktree :937, locked-file exit :966-968, gitdir-target expiry test :1016-1017; sha256 builtin/worktree.c af2bd523c1e89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc, worktree.c da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2 | a present locked file exits with no reason, so the registration is kept; an absent gitdir target is prunable when the index is missing or its mtime is at or before expire; expire defaults to TIME_MAX; v2.56.0 threads the_repository into should_prune_worktree (builtin :229, worktree.c :937) and moves the v2.55.0 lock check (worktree.c :954-956 in S009) to :966-968 and the expiry test (v2.55.0 :1004-1005) to :1016-1017, +12 lines each, with no change to the branches | mined | 2026-10-28 | on-release | corpus/lessons/round-41.md

## (2) Gate

- URL: https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c (the same file as the registry source's blob URL at tag v2.56.0)
- Access date: 2026-10-28
- Fetched file: 1541 lines, sha256 af2bd523c1e89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc
- Located quote (<=25 words), builtin/worktree.c line 255:
  `prune missing working trees older than <time>`
  Verbatim as it appears in `N_("prune missing working trees older than <time>")`. `grep -n -F` over the fetched file returns exactly one match, line 255.
- Grounding: the quote is the help string of the `prune --expire` option; it states the age condition that `expire` applies to missing working trees. The `expire = TIME_MAX` default (line 259) and the gitdir-target test (worktree.c :1016-1017) are read from code, not from this string.
