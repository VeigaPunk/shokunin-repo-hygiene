source: S131 — lanes/souji/round2/fixtures/r23-trigger-prune.sh — cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1
source: S129 — https://github.com/git/git/tree/v2.56.0/builtin — tag v2.56.0 call sites (the row staged by the lane's promoted round-1 proposal)
source: S130 — https://github.com/git/git/blob/v2.56.0/builtin/pull.c — tag v2.56.0 `builtin/pull.c:392`
source: S128 — https://git-scm.com/docs/git-fetch — § OPTIONS `--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc` — git 2.56.0
source: S132 — lanes/souji/round2/evidence/r23-worktree-census.out — the fleet's own worktree registrations, 0 prunable
verified-at: 2026-10-25 — host git 2.56.0; MEASURED IN THE CAMPAIGN, NOT BY THIS LANE: only the fetch 2 -> 1 arm is isolated, in lanes/souji/round2/evidence/r23-trigger-prune.out:2 (run 2026-10-23, git 2.56.0, kernel 7.2.11-arch1-1); the rows named pull (:4), merge (:5) and rebase (:6) do not measure those commands — the pull case runs git fetch (fixture :146) and the merge and rebase cases run a plain git commit after the before-count (fixture :153, :161); this lane read those bytes on 2026-10-25 (sha256 510722c1…, fixture 11c136aa…) and did not execute the fixture
recheck: 90d — re-run `bash lanes/souji/round2/fixtures/r23-trigger-prune.sh` in the campaign checkout (expect 7 PASS, exit 0); fixture is the campaign's own-work evidence, not this lane's run
ground: F1 — git-native housekeeping vs receipts (the trigger set is now MEASURED, not inferred)

# `fetch` auto-maintenance prunes a stale worktree registration (measured); pull/merge/rebase rows are confounded and not attributed

## Claim (F1, measured)

The lane's existing entry `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`
proved the `git commit` path on git **2.55.0** and left the other three
commands as "call sites only — whether each prunes was not fixture-run".
This entry closes that gap **on git 2.56.0, on this host**, using the
campaign's own-work fixture and evidence (S131), re-grounded by this lane.

1. **Fetch prunes, and it is the only isolated measurement.** With a stale
   registration (working directory removed, index aged past
   `gc.worktreePruneExpire` — fixture `touch -d '4 months ago'` at
   `fixtures/r23-trigger-prune.sh:126`), the registration count goes
   **2 → 1** under `git fetch` alone (evidence row
   `id=SOUJI-R23-TRIGGER-fetch case=fetch before=2 after=1 expect=1 verdict=PASS`
   at `evidence/r23-trigger-prune.out:2`; the campaign ran the fixture on
   2026-10-23, git 2.56.0 — this lane only read the bytes this round).
2. **The pull, merge and rebase rows are confounded and are NOT
   attributions to those commands.** The campaign fixture's `pull` case
   runs `git fetch -q origin` (fixture `:144-147`), so its PASS row is a
   second fetch; the `merge` and `rebase` cases run a plain `git commit`
   after the before-count (fixture `:153`, `:161`), and the lane's own
   entry `git-auto-maintenance-prunes-worktrees.md` (SKILL.md:95) shows
   that commit alone prunes under this expiry aging. The merge case is
   additionally a fast-forward (replayed; fixture comment at `:149` is not
   the merge command at `:155`). What remains true: `git pull` inherits
   fetch's trigger by spawn (S130, `builtin/pull.c:392`), and the call
   sites for all five commands exist (S129) — those are inferences from
   source, not measurements.
3. **No souji receipt is involved.** The lane's own `PROVINCE.md` makes
   removal receipt-gated — "receipt-gated removal of stale, duplicate, and
   already-preserved artifacts" (PROVINCE.md:3) — and lists dead worktree
   metadata as lane-repo hygiene held to a receipt (PROVINCE.md § Owns).
   Git's own maintenance path performs the registration removal in a
   disposable `/var/tmp` repository with **no receipt, no lane involvement
   and no operator decision**; the fixture contains no receipt tooling (0
   matches for `receipt` in all 206 lines). This is the same class of event the
   lane already records for `git commit` ("Git deletes without a receipt",
   SKILL.md:95, r12).
4. **The two off-switches work, and they are different mechanisms.**
   `maintenance.auto=false`, applied per invocation with `-c` (fixture line
   141), holds the registration at 2 (`case=fetch-auto-off after=2`), and
   `git worktree lock --reason r23-trigger` (fixture line 129) also holds it
   at 2 (`case=locked after=2`). The config switch suppresses the *task*; the
   lock protects the *registration* even if the task runs. A deployment that
   wants neither must set both.
5. **The expiry is a third, independent guard.** The `fresh` case runs the
   same `git fetch` against a registration whose index is **not** aged, and
   the registration survives at 2 (`case=fresh after=2`). So the task
   demonstrably ran, and the `3.months.ago` expiry — not the absence of a
   trigger — is what spared it. This is the control that separates "the
   trigger did not fire" from "the trigger fired and the expiry protected
   the registration".

## What this does NOT establish

- **One host, one git version.** Every case ran on git 2.56.0 on this
  machine with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`.
  The result is about this configuration; a host with a different
  `gc.worktreePruneExpire` or `maintenance.strategy` may differ. The
  fixture was the campaign's run; this lane re-grounded it by reading the
  evidence bytes, not by re-executing the fixture.
- **The `merge` and `rebase` cases are conditional.** The call sites (S129)
  sit inside the paths that actually update HEAD — `builtin/merge.c:509`
  is inside the merge-updates-HEAD branch, and `builtin/rebase.c:572` is
  in `finish_rebase()`. A merge that is already up to date, or a rebase
  that is a no-op, does not reach the call site. The fixture exercised the
  *reaching* case; the non-reaching case was not separately measured.
- **`maintenance.auto=false` was applied per-invocation** (`-c`), so it
  does not establish that a repo-level or system-level setting behaves
  identically.
- The **fleet's own** registrations are a separate measurement — S132's
  census (2026-10-23) found **5 registrations, 0 prunable, 0 locked** at
  every expiry including `--expire=now`, so the fleet is currently *not*
  exposed while the *mechanism* that would expose it is live on every
  fetch, merge and rebase.
- Nothing here says pruning a worktree registration is *wrong*. It says it
  happens without a receipt, which is what the lane's own SKILL.md already
  treats as a risk worth recording.

## Lane link and consequence

The lane's F1 frontier asked for the exposure census. The census's
**denominator** is now known and measured: five trigger commands at v2.56.0
(S129); the only isolated measured prune arm is `git fetch` (S131); the
remaining named commands are call-sites-only or confounded rows, and
`git pull` inherits fetch's trigger by spawn (S130). The **numerator** for
the fleet is in S132: 5 registrations, 0 prunable, 0 locked.

## Freshness

Measured on git 2.56.0 (the current host version), closing the 2.55.0-only
coverage the commit-path entry carries for the trigger set.

## Gate

opened: 2026-10-25
- ADMIT: the measured prune fixture entry; reason: the campaign ran the fixture (2026-10-23, git 2.56.0, kernel 7.2.11-arch1-1); this lane verified the bytes unchanged (sha256 fixture 11c136aa…, evidence 510722c1…, census 1ac71c4f…) and did not execute it.
- Same-run caveat: the pull row (:4) is a git fetch (fixture :146); the merge and rebase rows (:5-6) are preceded by a plain git commit (fixture :153, :161) that alone takes the count 2 -> 1 — those three rows are not attributions to pull, merge or rebase.
- REJECT: the staged package ids S109/S110/S111/S123 as-is; reason: they collide with the lane registry S109-S127, so the rows were re-pointed by document to S128-S132 before appending.
- "run_auto_maintenance(the_repository, verbosity < 0);" — snapshot: census/round-26/sources/git-builtin-merge.c lines 506-509
- "run_auto_maintenance(the_repository, verbosity < 0);" — snapshot: census/round-26/sources/git-builtin-fetch.c line 2926
- https://github.com/git/git/blob/v2.56.0/builtin/pull.c
