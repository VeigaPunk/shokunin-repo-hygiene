# S258 — draft registry row (R41scribe05, round 41 wave 1)

Draft only. Not landed: the L1 lands any registry change through jj-lane.sh. Source opened 2026-10-28 from the upstream raw URL at tag v2.56.0; fetched bytes live in the seat scratch dir (not evidence), and the sha256 and line numbers below are the citable pointers.

## Registry row (for corpus/SOURCES.md, after the S257 row)

| S258 | git/git source at tag v2.56.0: builtin/worktree.c — https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c | code | A | what git worktree prune deletes from .git/worktrees at git 2.56.0 and the --expire cutoff; not the lock check (it lives in should_prune_worktree(), which this file calls but does not define) and not the gc caller (S009) | tag v2.56.0, builtin/worktree.c sha256 af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc, 1541 lines: delete_git_dir 149-162, prune_worktree 171-177, prune_dups 201-210, prune_worktrees 212-246 (should_prune_worktree call at 229), prune options 248-266 (--expire at 254-255, expire = TIME_MAX at 259) | prune deletes the admin directory of every entry the library selects, plus duplicate-path entries, and --expire sets the cutoff that defaults to TIME_MAX; v2.56.0 re-pins the v2.55.0 prune region (lines 171-266 identical to the v2.55.0 file; only the should_prune_worktree call at 229 gains a the_repository argument), so the prune reading S009 gives for this file is unchanged at 2.56.0 | mined | 2026-10-28 | on-release | corpus/lessons/round-41.md |

## Gate

- URL: https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c
- Access date: 2026-10-28
- Fetched file: sha256 af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc, 1541 lines (scratch copy, not cited)
- Quote (≤25 words, verbatim, line 255 of the fetched file, the N_() help string for the prune --expire option): "prune missing working trees older than <time>"
- Uniqueness check: `grep -n -F -c 'prune missing working trees older than <time>'` on the fetched file prints 1; `grep -n` prints `255:				N_("prune missing working trees older than <time>")),`
- Comparison pin: the v2.55.0 file (sha256 2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884, 1493 lines) has the same prune region at the same lines 171-266; the only difference inside that region is line 229 of each file, where the v2.56.0 call gains `the_repository` as its first argument.
