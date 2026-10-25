source: S131 — lanes/souji/round2/fixtures/r23-trigger-prune.sh — cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1
source: S129 — https://github.com/git/git/tree/v2.56.0/builtin — tag v2.56.0 call sites (the row staged by the lane's promoted round-1 proposal)
source: S130 — https://github.com/git/git/blob/v2.56.0/builtin/pull.c — tag v2.56.0 `builtin/pull.c:392`
source: S128 — https://git-scm.com/docs/git-fetch — § OPTIONS `--auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc` — git 2.56.0
source: S132 — lanes/souji/round2/evidence/r23-worktree-census.out — the fleet's own worktree registrations, 0 prunable
verified-at: 2026-10-25 — git 2.56.0; campaign evidence re-grounded by this lane (fixture sha256 11c136aa…, evidence sha256 510722c1…, census sha256 1ac71c4f… — all verified byte-for-byte this round)
recheck: 90d — re-run `bash lanes/souji/round2/fixtures/r23-trigger-prune.sh` in the campaign checkout (expect 7 PASS, exit 0); fixture is the campaign's own-work evidence, not this lane's run
ground: F1 — git-native housekeeping vs receipts (the trigger set is now MEASURED, not inferred)

# `fetch`, `merge`, `rebase` and `pull` auto-maintenance all prune a stale worktree registration

## Claim (F1, measured)

The lane's existing entry `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md`
proved the `git commit` path on git **2.55.0** and left the other three
commands as "call sites only — whether each prunes was not fixture-run".
This entry closes that gap **on git 2.56.0, on this host**, using the
campaign's own-work fixture and evidence (S131), re-grounded by this lane.

1. **All four commands prune.** With a stale registration (working
   directory removed, index aged past `gc.worktreePruneExpire`), the
   registration count goes **2 → 1** under `git fetch`, under `git pull`,
   under a real non-fast-forward `git merge`, and under `git rebase`
   (evidence rows `id=SOUJI-R23-TRIGGER-{fetch,pull,merge,rebase} …
   verdict=PASS`). The `git pull` result is the expected consequence of
   S130: pull spawns `fetch`, so it inherits fetch's trigger by process
   spawn.
2. **No souji receipt is involved.** The lane's own `PROVINCE.md` § Refuses
   makes removal receipt-gated; git's own maintenance path performs the
   registration removal with **no receipt, no lane involvement and no
   operator decision** — the same class of event the lane already records
   for `git commit` ("Git deletes without a receipt", SKILL.md r12).
3. **The two off-switches work, and they are different mechanisms.**
   `maintenance.auto=false` (S128's switch, applied as a config) holds the
   registration at 2 (`case=fetch-auto-off after=2`), and
   `git worktree lock` also holds it at 2 (`case=locked after=2`). The
   config switch suppresses the *task*; the lock protects the
   *registration* even if the task runs. A deployment that wants neither
   must set both.
4. **The expiry is a third, independent guard.** The `fresh` case runs the
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
(S129), of which four reach the prune path (S131) and one — `git pull` —
reaches it by way of `git fetch` (S130). The **numerator** for the fleet is
in S132: 5 registrations, 0 prunable, 0 locked.

## Freshness

Measured on git 2.56.0 (the current host version), closing the 2.55.0-only
coverage the commit-path entry carries for the trigger set.
