source: S128 — https://git-scm.com/docs/git-fetch — § OPTIONS `--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc` — git 2.56.0 (snapshot census/round-26/sources/git-fetch.1.txt, heading line 2995, option entry lines 3190-3202)
source: S129 — https://github.com/git/git/blob/v2.56.0/builtin/fetch.c — tag v2.56.0 call sites in builtin/fetch.c, builtin/merge.c, builtin/rebase.c, builtin/am.c, builtin/commit.c (snapshots census/round-26/sources/git-builtin-*.c)
source: S130 — https://github.com/git/git/blob/v2.56.0/builtin/pull.c — tag v2.56.0 `builtin/pull.c:384-392`, `run_fetch` spawns `git fetch` (snapshot census/round-26/sources/git-builtin-pull.c)
verified-at: 2026-10-25 — host git 2.56.0; every quote below re-read this run from census/round-26/sources/ (`sha256sum -c SHA256SUMS` → 7 files OK) and the six code snapshots cross-checked byte-identical against raw.githubusercontent.com v2.56.0
recheck: 90d — re-grep the call sites at the host's tag: `v=$(git --version | awk '{print $3}'); for f in fetch merge rebase am commit pull; do printf "%s " "$f"; curl -fsSL https://raw.githubusercontent.com/git/git/v$v/builtin/$f.c | grep -c run_auto_maintenance; done` (expect `1 1 1 1 1 0` while the host is 2.56.0); whole-tree form on the tag tarball: `grep -rn run_auto_maintenance --include=*.c --include=*.h .` (expect the five builtin call lines plus the declaration and the definition)
ground: F1 — git-native housekeeping vs receipts (the trigger set and the per-command opt-out)

# Git's auto-maintenance triggers are a named, per-command set with a per-command opt-out

## Claim (F1: git-native housekeeping vs receipts)

The F1 question — whether `fetch`/`merge`/`rebase` auto-maintenance prunes a
worktree registration on the fleet's live repos — splits in two. This entry
answers only the *trigger* half: which commands can start auto-maintenance at
all, and how an operator turns it off for one invocation.

1. **The trigger set is exactly five builtins at tag v2.56.0.** A whole-tree
   grep over `*.c` and `*.h` returns `builtin/fetch.c:2926`, `builtin/merge.c:509`,
   `builtin/rebase.c:572`, `builtin/am.c:1942` and `builtin/commit.c:1965`;
   the only other hits in the tree are the declaration at `run-command.h:247`
   and the definition at `run-command.c:1987` (the six candidate files, adding
   `builtin/pull.c`, count 1,1,1,1,1,0). The calls sit after each command's
   own work and each is conditional: fetch's is inside `if (enable_auto_gc)`
   (`builtin/fetch.c:2909-2927`), am's inside `if (!state->rebasing)`
   (`builtin/am.c:1940-1943`) under the comment "In rebasing mode, it's up to
   the caller to take care of" housekeeping (`builtin/am.c:1937`), merge's in
   `finish()` (`builtin/merge.c:509`), rebase's in `finish_rebase()`
   (`builtin/rebase.c:572`). `builtin/pull.c` never calls it: `run_fetch()` is
   documented "Runs git-fetch, returning its exit status."
   (`builtin/pull.c:385`) and builds the child argv with
   `strvec_pushl(&cmd.args, "fetch", "--update-head-ok", NULL);`
   (`builtin/pull.c:392`), so `git pull`'s exposure is `git fetch`'s, reached
   by process spawn.
2. **The trigger is default-on and operator-controllable per invocation.**
   `git-fetch(1)` § OPTIONS lists `--auto-maintenance`, `--no-auto-maintenance`,
   `--auto-gc` and `--no-auto-gc` (snapshot lines 3190-3193), then: "Run git
   maintenance run --auto at the end to perform automatic repository
   maintenance if needed." and "This is enabled by default." (lines
   3199-3202). The installed git 2.56.0 man page carries the same paragraph at
   lines 267-274, and the upstream text is `Documentation/fetch-options.adoc:170-176`.
   The default is in the code: `int enable_auto_gc = 1;`
   (`builtin/fetch.c:2528`), both positive spellings bind to that variable
   (`:2619-2622`), and the call is guarded by `if (enable_auto_gc) {` (`:2909`).
   The flag is fetch's alone; for every caller `prepare_auto_maintenance()`
   reads `maintenance.auto` (falling back to `gc.auto`) and returns without
   spawning when disabled (`run-command.c:1961-1967`).
3. **The merge and rebase call sites ignore maintenance errors, in different
   words.** `builtin/merge.c:505-509` and `builtin/rebase.c:568-572` each put
   the call under a comment saying errors are ignored: merge's reads "We
   ignore errors in 'gc --auto', since the" (`builtin/merge.c:506`) and
   rebase's "We ignore errors in 'git maintenance run --auto', since the"
   (`builtin/rebase.c:569`). The difference is load-bearing for anyone grepping
   for one string: a search for the merge wording misses rebase. Both state
   the same rule — a failed `git maintenance run --auto` does not fail the
   merge or rebase that triggered it.

## What this does NOT establish

- **Whether any of these triggers prunes a worktree registration is not proven
  here.** The existing entry
  `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` proved the
  *commit* path behaviourally on git 2.55.0 and left `fetch`/`merge`/`rebase`
  as call-sites-only. This entry adds the trigger set and the opt-out; it
  upgrades none of the five to a proven prune. The behavioural half is carried
  by the sibling entry `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`,
  which is the fixture; nothing in this entry is a measurement.
- **`git pull` inherits fetch's behaviour only if the child actually runs**;
  this entry does not assert that it does on any given host, and no process
  spawn was observed for it.
- **Local configuration can alter the behaviour.** The code path above shows
  where the config gate sits (`maintenance.auto`, `gc.auto`, and downstream
  strategy/task enablement and auto threshold), not what any host's
  configuration is.
- **The trigger set is a property of the tagged tree**, not of any installed
  binary: a host running a different git version may differ.

## Lane link and consequence

The corpus's F1 frontier asked for the exposure census. This entry gives the
census its *denominator*: the set of commands that can trigger maintenance at
all, and the switch that turns the fetch trigger off per invocation. A census
that only watched `git commit` would be watching one of five triggers, plus
`git pull` by way of `git fetch`. The config gate in `prepare_auto_maintenance()`
is the lever that reaches all five at once, which is why the lane's own
scoped quarantine commit carries `-c maintenance.auto=false` rather than a
per-command flag (`SKILL.md:164`).

## Freshness

`git-auto-maintenance-prunes-worktrees.md` was verified on git 2.55.0 and
flagged pending recheck when the host moved to 2.56.0. This entry is read from
tag **v2.56.0** source, the v2.56.0 manual page and upstream
`Documentation/fetch-options.adoc`, so it does not repeat that staleness for
the trigger set — but the *behavioural* prune claim in the older entry remains
unverified on 2.56.0 and is still owed there.

## Limits

- The staged package's language-edition corroboration (a Simplified-Chinese
  fetch page, a Japanese Pro Git section and a Japanese vendor support page) is
  **refused this round**; the round lesson records why — the zh/ja mirrors'
  version alignment with 2.56.0 was not provable and the vendor page quoted an
  older workflow (`corpus/lessons/round-26.md` `## Gate`). No claim here rests
  on a translated edition or a vendor page, and none is cited.
- The five-caller count is read from `builtin/*.c` plus a whole-tree scan of
  `*.c`/`*.h` at the tag; it is call-site evidence, not execution evidence.
- Where the upstream source wraps a sentence across lines (the comments at
  `builtin/merge.c:506-507` and `builtin/rebase.c:569-570`), the Gate quotes
  the first line verbatim and this body gives the full sentence with its span.

## Gate

url: https://git-scm.com/docs/git-fetch ; https://github.com/git/git/blob/v2.56.0/builtin/fetch.c ; https://github.com/git/git/blob/v2.56.0/builtin/pull.c
opened: 2026-10-25

- ADMIT: "at the end to perform automatic repository maintenance if needed. This is enabled by default." — § OPTIONS --auto-maintenance (snapshot lines 3190-3202) — reason: names the run fetch performs and states the default — snapshot: census/round-26/sources/git-fetch.1.txt
- ADMIT: "run_auto_maintenance(the_repository, verbosity < 0);" — builtin/fetch.c line 2926 — reason: one of the five trigger call sites, and the only one with a per-invocation option — snapshot: census/round-26/sources/git-builtin-fetch.c
- ADMIT: "int enable_auto_gc = 1;" — builtin/fetch.c line 2528 — reason: the default-on initialiser both fetch option spellings bind to — snapshot: census/round-26/sources/git-builtin-fetch.c
- ADMIT: "We ignore errors in 'gc --auto', since the" — builtin/merge.c line 506 — reason: merge's call site ignores maintenance failures — snapshot: census/round-26/sources/git-builtin-merge.c
- ADMIT: "We ignore errors in 'git maintenance run --auto', since the" — builtin/rebase.c line 569 — reason: rebase names a different command string, so a grep for merge's wording misses it — snapshot: census/round-26/sources/git-builtin-rebase.c
- ADMIT: "Runs git-fetch, returning its exit status." — builtin/pull.c line 385 — reason: pull reaches the trigger by spawning fetch, not by calling the function — snapshot: census/round-26/sources/git-builtin-pull.c
- REJECT: the staged package's translated-edition and vendor-page corroboration — reason: the lesson records unprovable zh/ja version alignment and a vendor page quoting an older workflow, and the staged ids resolve to different documents in this lane's registry — flip: admit if a later claim rests on a translated edition's own wording, opened and quoted in that language.
