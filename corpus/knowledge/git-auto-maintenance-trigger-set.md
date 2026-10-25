source: S128 — https://git-scm.com/docs/git-fetch — § OPTIONS `--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc` — git 2.56.0
source: S129 — https://github.com/git/git/tree/v2.56.0/builtin — tag v2.56.0 call sites in builtin/fetch.c, merge.c, rebase.c, am.c, commit.c
source: S130 — https://github.com/git/git/blob/v2.56.0/builtin/pull.c — tag v2.56.0 `builtin/pull.c:392`
verified-at: 2026-10-25 — host git 2.56.0; source tag v2.56.0; re-grounded by this lane from fetched snapshots (census/round-26/sources/, SHA256SUMS)
recheck: on-release — re-grep the call sites at the next host git tag: `for f in fetch merge rebase am commit pull; do curl -fsSL https://raw.githubusercontent.com/git/git/<tag>/builtin/$f.c | grep -c run_auto_maintenance; done` (expect 1,1,1,1,1,0 at v2.56.0)
ground: F1 — git-native housekeeping vs receipts (the trigger set and the per-command opt-out)

# Git's auto-maintenance triggers are a named, per-command set with a per-command opt-out

## Claim (F1: git-native housekeeping vs receipts)

1. **Which porcelain commands trigger auto-maintenance.** At tag **v2.56.0**
   exactly five of the candidate builtins call `run_auto_maintenance`:
   `builtin/fetch.c:2926`, `builtin/merge.c:509`, `builtin/rebase.c:572`,
   `builtin/am.c:1942` and `builtin/commit.c:1965` (snapshot bytes
   `census/round-26/sources/git-builtin-{fetch,merge,rebase,am,commit}.c`).
   `builtin/pull.c` has **no** such call: it pushes `"fetch"` into the child
   argv (`builtin/pull.c:392`,
   `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);`, snapshot
   `census/round-26/sources/git-builtin-pull.c`), so `git pull`'s exposure
   is `git fetch`'s, reached by process spawn.
2. **The trigger is operator-controllable per invocation.** `git-fetch(1)`
   § OPTIONS documents `--auto-maintenance, --no-auto-maintenance,
   --auto-gc, --no-auto-gc` (snapshot `census/round-26/sources/git-fetch.1.txt`,
   OPTIONS heading set): "Run git maintenance run --auto at the end to
   perform automatic repository maintenance if needed. This is enabled by
   default." The switch is **default-on** and is the per-command off-ramp
   git offers for fetch.
3. **The merge/rebase call sites ignore maintenance errors.**
   `builtin/merge.c:506-509` and `builtin/rebase.c:569-572` carry the
   comments "We ignore errors in 'gc --auto', since the user should see
   them." and "We ignore errors in 'git maintenance run --auto', since the
   user should see them." respectively (snapshot bytes). A failed
   `git maintenance run --auto` therefore does not fail the merge or rebase
   that triggered it.

## What this does NOT establish

- **Whether any of these triggers prunes a worktree registration is not
  proven by this entry.** The existing corpus entry
  `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` proved the
  *commit* path behaviourally on git 2.55.0 and left `fetch`/`merge`/`rebase`
  as call-sites-only. This entry adds the trigger set and the opt-out; the
  behavioural gap for those three commands is closed by the sibling entry
  `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` (S131), not here.
- **`git pull` inherits fetch's behaviour only if the child actually runs**;
  this entry does not assert that it does on any given host (the sibling
  entry's measured case covers this host on 2.56.0).
- Local configuration (`maintenance.auto`, strategy/task enablement, the
  auto threshold) can alter the behaviour; the staged proposal's
  language-edition corroboration (zh/ja docs and a vendor page) was refused
  this round — see `corpus/lessons/round-26.md` `## Gate`.

## Lane link and consequence

The corpus's F1 frontier asked for the exposure census. This entry gives the
census its *denominator*: the set of commands that can trigger maintenance
at all, and the one flag that turns the fetch trigger off per invocation. A
census that only watched `git commit` would watch one of five triggers, plus
`git pull` by way of `git fetch`.

## Freshness

`git-auto-maintenance-prunes-worktrees.md` was verified on git 2.55.0 and
flagged pending recheck when the host moved to 2.56.0. This entry is read
from tag **v2.56.0** source and the host's 2.56.0 manual, so it does not
repeat that staleness for the trigger set.
