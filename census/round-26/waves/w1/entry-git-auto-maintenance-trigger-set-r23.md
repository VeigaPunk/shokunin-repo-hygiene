source: S131 — lanes/souji/round2/fixtures/r23-trigger-prune.sh — cases SOUJI-R23-TRIGGER-{fetch,fetch-auto-off,pull,merge,rebase,locked,fresh}; git 2.56.0 (2026-10-23), kernel 7.2.11-arch1-1
source: S129 — https://github.com/git/git/tree/v2.56.0/builtin — tag v2.56.0 call sites in builtin/fetch.c, merge.c, rebase.c, am.c, commit.c
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
   directory removed, index aged past `gc.worktreePruneExpire` — fixture
   `touch -d '4 months ago'` at `fixtures/r23-trigger-prune.sh:126`), the
   registration count goes **2 → 1** under `git fetch`, under `git pull`,
   under a real non-fast-forward `git merge` (fixture line 149), and under
   `git rebase` (evidence rows `id=SOUJI-R23-TRIGGER-{fetch,pull,merge,rebase}
   … verdict=PASS` in `evidence/r23-trigger-prune.out:2-6`). The `git pull`
   result is the expected consequence of S130: pull spawns `fetch`
   (`census/round-26/sources/git-builtin-pull.c:392`), so it inherits fetch's
   trigger by process spawn.
2. **No souji receipt is involved.** The lane's own `PROVINCE.md` makes
   removal receipt-gated — "receipt-gated removal of stale, duplicate, and
   already-preserved artifacts" (PROVINCE.md:3) — and lists dead worktree
   metadata as lane-repo hygiene held to a receipt (PROVINCE.md § Owns).
   Git's own maintenance path performs the registration removal in a
   disposable `/var/tmp` repository with **no receipt, no lane involvement
   and no operator decision**; the fixture contains no receipt tooling (0
   matches for `receipt` in all 206 lines). This is the same class of event the
   lane already records for `git commit` ("Git deletes without a receipt",
   SKILL.md:95, r12).
3. **The two off-switches work, and they are different mechanisms.**
   `maintenance.auto=false`, applied per invocation with `-c` (fixture line
   141), holds the registration at 2 (`case=fetch-auto-off after=2`), and
   `git worktree lock --reason r23-trigger` (fixture line 129) also holds it
   at 2 (`case=locked after=2`, where the case still runs a triggering
   `git commit --allow-empty`). The config switch suppresses the *task*;
   the lock protects the *registration* even if the task runs. A deployment
   that wants neither must set both. S128 documents the per-command form of
   the same off-ramp for fetch: the maintenance run is "enabled by default"
   and the operator can skip it per invocation.
4. **The expiry is a third, independent guard.** The `fresh` case runs the
   same `git fetch` against a registration whose index is **not** aged
   (fixture line 125 skips the age step), and the registration survives at 2
   (`case=fresh after=2`). The fixture's own comment names what the case
   holds: "Registration whose index is NOT aged: the 3.months.ago expiry
   protects" (fixture line 168), and says it is the control separating a
   trigger that did not fire from a trigger the expiry protected (lines
   171-172). So the `3.months.ago` expiry, not the absence of a trigger, is
   what spared the registration, and the other cases can be read as proof
   that the trigger fired.

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
  in `finish_rebase()` (snapshot bytes under `census/round-26/sources/`). A
  merge that is already up to date, or a rebase that is a no-op, does not
  reach the call site. The fixture exercised the *reaching* case; the
  non-reaching case was not separately measured.
- **`maintenance.auto=false` was applied per-invocation** (`-c`), so it does
  not establish that a repo-level or system-level setting behaves
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
**denominator** is now known and measured: five builtins call the trigger at
v2.56.0 (S129), and four commands were measured taking a stale registration
2 → 1 (S131) — `fetch`, `merge`, `rebase` and `pull`, the last reaching the
prune path by way of `git fetch`'s child process (S130). The **numerator**
for the fleet is in S132: 5 registrations, 0 prunable, 0 locked.

## Freshness

Measured on git 2.56.0 (the current host version), closing the 2.55.0-only
coverage the commit-path entry carries for the trigger set.

## Gate

url: https://git-scm.com/docs/git-fetch
snapshot: census/round-26/sources/git-fetch.1.txt
opened: 2026-10-25

- ADMIT: "repository maintenance if needed. This is enabled by default." — § OPTIONS --auto-maintenance — reason: the default-on maintenance run whose skip the entry's off-switch case measures — snapshot: census/round-26/sources/git-fetch.1.txt
- ADMIT: fixture cases SOUJI-R23-TRIGGER-fetch, pull, merge and rebase with before=2 after=1 and verdict=PASS — reason: the measured prune this entry reports, re-grounded from campaign bytes by sha256 this round and not re-executed by this lane — source: lanes/souji/round2/evidence/r23-trigger-prune.out
- ADMIT: census rows 5 registrations, 0 prunable, 0 locked — reason: the fleet numerator, a read-only census of the live fleet and not a point-in-time figure — source: lanes/souji/round2/evidence/r23-worktree-census.out
- REJECT: the staged package's own ids S123, S110, S111 and S109 as-is — reason: each of those lane ids resolves to a different document in corpus/SOURCES.md, so an as-is append would cite the wrong pages — flip: re-point by document to S131, S129, S130 and S128 and append the census as S132, as this round did
