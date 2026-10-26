source: S222 — git-reflog(1) at tag v2.56.0 (placeholder id: the L1 renumbers by document) — https://git-scm.com/docs/git-reflog — § DESCRIPTION lines 66-70; OPTIONS for `expire`, `--expire=<time>` lines 111-117 and `--expire-unreachable=<time>` lines 119-127 — snapshot census/round-31/sources/git-reflog.adoc
source: S063 — git-gc(1) reachability — https://git-scm.com/docs/git-gc — § DESCRIPTION lines 16-21, § NOTES lines 141-151; § CONFIGURATION gc.pruneExpire, gc.reflogExpire and gc.reflogExpireUnreachable, which git-gc(1) includes from Documentation/config/gc.adoc at tag v2.56.0 lines 96-147 — snapshot census/round-31/sources/gc.adoc for the config fragment
source: S002 — git-gc(1) grace periods on git's own deletions — https://git-scm.com/docs/git-gc — § CONFIGURATION gc.reflogExpire, gc.reflogExpireUnreachable, as the registry cell records them; no new byte of S002 was opened this round
source: S117 — git-prune(1) — https://git-scm.com/docs/git-prune — § DESCRIPTION, § OPTIONS -n/--dry-run and --expire, as the registry cell records them (prune acts on unpacked objects only)
source: S220 — jj CLI reference at tag v0.45.1 — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap — § `jj util gc` lines 3793, 3799-3805
source: S054 — jj source at tag v0.45.1, lib/src/git_backend.rs — https://github.com/jj-vcs/jj/blob/v0.45.1/lib/src/git_backend.rs — line 900 (doc comment), line 925 (head test), lines 939-945 (loose-ref mtime gate), lines 970-987 (run_git_gc) — held capture census/round-30/sources/git_backend.rs, sha256 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69 re-fetched byte-identical this run
verified-at: 2026-10-26 — three snapshots and the jj source were fetched live from their tags this run and hashed: git-reflog.adoc sha256 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54 (5657 B), gc.adoc sha256 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a (7753 B), git-compatibility.md sha256 0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641 (12284 B), git_backend.rs sha256 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69 (identical to the round-30 capture, so its line anchors still address these bytes); the measurement runs on jj 0.45.1 and git 2.56.0, whose version lines are in the run record; the record is `census/round-31/records/jj-object-clock-run.txt` (sha256 085b87c781dcd323a1576ee92a4a2779c1fa69dce3b62e978e0db315bad207e5, 17 `RESULT` lines) and each quoted `RESULT` span was matched as a whole line of those bytes
recheck: 365d — bash -c 'd=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-r31-objclock.XXXXXX"); curl -fsSL -o "$d/r.adoc" https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc; curl -fsSL -o "$d/g.adoc" https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc; curl -fsSL -o "$d/c.md" https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md; curl -fsSL -o "$d/b.rs" https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs; sha256sum "$d"/*; rm -r "$d"'   # expect 59e7f0f1… 0ab75f6f… 0fb71f99… 95147270…
ground: F1 — git-native housekeeping vs receipts (object lifetime behind a dropped keep ref)

# What keeps a dropped-keep-ref commit's object present, and what removes it

## Claim (F1: object clock behind a dropped keep ref)

How a `refs/jj/keep/*` ref is written and how it is removed is the held rule of
`corpus/knowledge/jj-keep-ref-expiry.md`; this entry does not restate it. What that entry's
`## Round 30 wave-2 corrections` leave open is the next object in the chain: after the keep ref
naming the abandoned commit B is gone, which roots still hold B's git object, and which actions
finally drop it. Below, B is the abandoned commit of the round-30 fixture's naming, and a `root` is
anything `git gc` consults before it deletes.

1. **git gc tests reachability from roots, not the existence of one ref.** It keeps objects
   referenced by branches and tags, the index, remote-tracking branches, reflogs, "and anything
   else in the refs/* namespace" (git-gc.adoc:141-146) [S063], and it says outright that a
   missing deletion is to be diagnosed by walking those locations (git-gc.adoc:148-151) [S063].
   Deleting B's keep ref removes one root; it does not make B unreachable.
2. **Keeper A — a descendant's keep ref.** jj rewrites the keep-ref set from the heads it is
   given: the doc comment of `recreate_no_gc_refs` says "Recreates `refs/jj/keep` refs for the
   `new_heads`, and removes the other" (git_backend.rs:900), and a keep ref survives only when
   `new_heads.contains(&id)` (git_backend.rs:925) [S054]. An abandoned commit that is a parent
   of a live head therefore has no keep ref of its own while remaining reachable from the
   descendant's ref — the mechanism behind the round-30 wave-2 observation that reflog expiry
   plus `git gc --prune=now` still left B present, and behind this round's role 3, where the
   same two levers leave B present until that ref is deleted.
3. **Keeper B — a reflog entry naming B.** A reflog entry is not a ref and needs no `refs/*`
   name, yet git counts it as a root: reflogs "may reference commits in branches that were later
   amended or rewound" (git-gc.adoc:144-146) [S063]. The lifetime of that root is git's reflog
   window, not the object's prune date: `git reflog expire` removes an entry older than `expire`
   (default 90 days, `gc.reflogExpire`) or older than `expire-unreachable` (default 30 days,
   `gc.reflogExpireUnreachable`) when it is not reachable from the current tip
   (git-reflog.adoc:66-68, :111-127) [S222]; the two defaults are stated identically in the
   config fragment (gc.adoc:115-132) [S063]. `--expire=all` and `--expire-unreachable=all` drop
   entries regardless of age (git-reflog.adoc:115-116, :124-126) [S222].
4. **Keeper C — object age against the prune date, and the hook that overrides it.** Independent
   of every root, any object whose modification time is newer than the `--prune` date is kept
   "along with everything reachable from it" (git-gc.adoc:160-161) [S063]; the default date is
   two weeks ago and `gc.pruneExpire` moves it, `now` disabling the grace entirely
   (gc.adoc:96-105) [S063]. `gc.recentObjectsHook` names object ids git must treat as recent
   regardless of their true age (gc.adoc:140-147) [S063]. So an unreachable B survives a default
   `git gc` even with every ref and every reflog entry gone, for as long as its own mtime is
   inside the window.
5. **Remover 1 — reflog expiry of the entries that name B.** `git reflog expire` is the action
   described here that drops reflog entries, and `git gc` lists reflog pruning among its
   housekeeping tasks beside the removal of unreachable objects (git-gc.adoc:16-20) [S063] — two
   levers, two dates. The record measures the separation: `git-gc-prune-now` leaves
   `reflog_hits=1` in all three arms, and only `reflog-expire-then-prune` reaches 0. The reason is
   that `--prune` is a loose-object date (git-gc.adoc:81-87) [S063] while the reflog date is read
   from `gc.reflogExpire` (git-reflog.adoc:111-117) [S222], so a prune cannot be offered as
   evidence that a reflog is empty.
6. **Remover 2 — a prune that sees the object unreachable.** Expiry alone deletes no object: it
   removes the entry, and an object becomes prunable only once nothing reaches it. `git prune`
   is not the general remover here — its scope is unpacked unreachable objects, packed ones
   remain [S117, registry cell] — so the action that removes a packed or crufted B is `git gc`
   with a prune date at or after B's mtime, `--prune=now` being the total form
   (git-gc.adoc:81-87) [S063]. Expiry before prune is necessary but not sufficient: the prune
   removes B only once no keep ref names B or a descendant of B, because a keep ref is a root
   like any other and outlives both levers (Observed, roles 3 and 4). A receipt that expires a
   reflog and prunes, while a keep ref still names a descendant, has removed the entry and
   nothing else.
7. **jj's own lever does not shorten the reflog window.** The command `jj util gc` is documented
   as backend-dependent garbage collection [S220], its head is implemented in
   cli/src/commands/util/gc.rs:44-66 (opened this run,
   https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/src/commands/util/gc.rs, sha256
   9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b; no registry row yet), and
   the git backend shells out with `git --git-dir=.` and the format string `--prune=@{} +0000`
   (git_backend.rs:970-987) [S054]:
   the instant it passes is the object-prune date, while the reflog dates stay at
   `gc.reflogExpire` and `gc.reflogExpireUnreachable`. jj documents only that "It should be safe
   to run `git gc` in the Git repo", and calls that untested (git-compatibility.md:52-54) —
   which is a reason to read the outcome, not a guarantee about it.

**Observed:** `census/round-31/records/jj-object-clock-run.txt` (fixture
`tests/fixtures/r31-jj-object-clock.sh`, run under `$TMPDIR` on jj 0.45.1 and git 2.56.0; the
record opens with `jj-version: jj 0.45.1-…` and `git-version: git version 2.56.0`) holds 17
`RESULT ` lines across three repositories: `solo`, `descendant` and `reflog-only`. Fields:
`keep_refs` counts `refs/jj/keep/*`, `target_keep` says whether a keep ref still names B,
`reflog_hits` counts the reflog entries that still name B, and `object_present` is
`git cat-file -e` on B's id. Every span below is one whole line of the record, copied from the
bytes read this round.

- **Role 1 — a reflog entry alone holds the object.** Arm `reflog-only` first deletes every keep
  ref naming B, leaving one `HEAD` reflog entry as the only root; `git gc --prune=now` then
  leaves B present:
  `RESULT arm=reflog-only step=git-gc-prune-now keep_refs=6 target_keep=no reflog_hits=1 object_present=yes`
  The step before it, `drop-keep-refs-naming-target`, reads the same except for the ref count
  (`keep_refs=6`, `reflog_hits=1`, `object_present=yes`).
- **Role 2 — expiring that entry and pruning removes it.** Same arm, `reflog-expire-then-prune`:
  `RESULT arm=reflog-only step=reflog-expire-then-prune keep_refs=6 target_keep=no reflog_hits=0 object_present=no`
- **Role 3 — the surviving descendant keep ref defeats both levers.** Arm `solo`,
  `reflog-expire-then-prune`: the entries naming B are gone, yet B is still present, because the
  working-copy commit that `jj abandon` rewrote still has a keep ref and B is its parent.
  `jj op abandon ..@-` plus `jj util gc --expire=now` removes further keep refs (`keep_refs` 6 to
  2) and B stays present; deletion appears only when those refs are deleted from the git side:
  `RESULT arm=solo step=reflog-expire-then-prune keep_refs=6 target_keep=no reflog_hits=0 object_present=yes`
  `RESULT arm=solo step=delete-descendant-keep-refs-and-prune keep_refs=1 target_keep=no reflog_hits=0 object_present=no`
- **Role 4 — a live descendant outlasts jj's own levers.** Arm `descendant` holds B through every
  assigned step, `op-abandon-and-util-gc` included; B goes at
  `abandon-descendant-and-op-abandon-and-util-gc` and stays gone at `git-gc-prune-now-again`:
  `RESULT arm=descendant step=abandon-descendant-and-op-abandon-and-util-gc keep_refs=2 target_keep=no reflog_hits=0 object_present=no`
  `RESULT arm=descendant step=git-gc-prune-now-again keep_refs=2 target_keep=no reflog_hits=0 object_present=no`

Read together: roles 1 and 2 are the only pair that isolates a reflog entry's reachability, and
they need the third repository, because in the assigned order the reflog is expired at step 4
before any descendant ref is dropped. Roles 3 and 4 are the precedence claim — a keep ref naming
a descendant outranks reflog expiry and every `git gc --prune=now` in the run. The run also
measures the independence asserted in step 5: in all three arms `git-gc-prune-now` leaves
`reflog_hits=1`, so a `--prune=now` did not expire the entry, while only the explicit
`git reflog expire` step moves it to 0. Finally, `op-abandon-and-util-gc` lowers `keep_refs`
in both jj arms and never removes B — the ref-removal side, which the held entry already covers.

**Field definitions (L1, at landing):** `reflog_hits` is the number of `git reflog --all` entries
whose commit (`%H`) is B (fixture header, line 50); in the run's repositories the only reflog file
is `logs/HEAD` (detached HEAD, no `refs/heads`, no reflogs for `refs/jj/keep/*`), so the field
counts HEAD reflog entries jj's export wrote. `object_present` is the exit code of
`git cat-file -e` on B's id. The `reflog-only` arm is a third repository beyond the two arms the
preregistration named; it was added so that one arm isolates the reflog as the only keeper.

**Held ground, cited not re-claimed:** the reachability rule of claim 1 is held by
`corpus/knowledge/jj-keep-ref-expiry.md` (S063); the 90/30-day reflog windows of claim 3 and the
two-week prune date of claim 4 are held by `corpus/knowledge/git-grace-periods-and-expire-to.md`
and S002; the `--prune=@<keep_newer>` shell-out of claim 7 is that entry's claim 3 (S054); and
plain-git object removal under `gc --prune=now` was already observed in round 12
(`corpus/knowledge/git-grace-periods-and-expire-to.md`). What this entry adds is measured in a
jj-colocated repository: a HEAD reflog entry written by jj's export is a keeper on its own (roles 1
and 2), a keep ref naming a descendant outranks reflog expiry and every prune (roles 3 and 4), and
jj's own `jj op abandon` plus `jj util gc` does not remove the object while a descendant is live;
`gc.recentObjectsHook` (claim 4) is the one new sourced item.

## Consequence for souji receipts

An object's presence is not a receipt. Three independent keepers hold B after its keep ref is
gone — a descendant head's keep ref, a reflog entry inside a 90/30-day window, and B's own mtime
against a two-week prune date — so `git cat-file -e <id>` succeeding says only that no deletion
has completed, and says nothing about whether a deletion was attempted, authorised or even
possible. The receipt-grade observation is the other direction: B absent after a named `git gc`
whose prune date is at or after B's mtime, with the reflog entries naming B expired (or their
windows asserted), no keep ref naming B or any descendant of B, and B's id recorded. A receipt
that cannot name all three — the prune date, the reflog state and the keep-ref state — has not
established a deletion: the run's role 3 expires the entries and finds B still present because a
descendant's keep ref remains.

Corollary for a lane that checks the reverse direction: absence is cheap to establish and
presence is expensive, so a receipt that reports B missing must also say which gc it observed
(MUST be one the lane itself ran, or one whose argv it recorded), because a default-window gc
that happens to run before expiry proves nothing. jj's own store gc is not that witness: it
passes an object-prune date only (git_backend.rs:970-987) [S054], and the ref-removal side of the
same command is the held rule of `corpus/knowledge/jj-keep-ref-expiry.md`.

The held rule that already excludes `refs/jj/*` from a receipt's roots and refuses novel
keep-only content is `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4; it is not
restated here. This entry supplies the object clock that runs after that rule has done its work.

## What this does NOT establish

- **No lane or fleet repository was measured.** Every repository of the run is a scratch repo
  under the round's scratch root; no lane repo is gc'd, and no keep ref outside scratch is
  touched.
- **The record is installed byte-identical to the bytes the spans were copied from.**
  `census/round-31/records/jj-object-clock-run.txt` (sha256
  `085b87c781dcd323a1576ee92a4a2779c1fa69dce3b62e978e0db315bad207e5`, 17 `RESULT` lines) is the
  fixture seat's delivery installed unchanged (`cmp` equal at landing); the six quoted spans are
  whole lines of it (counter leg L10).
- **Which reflog file carries the entry naming B is not settled here.** `reflog_hits` counts
  entries, not files; the seat reports `logs/HEAD` as the only log in its repositories, with no
  `refs/heads` and no reflogs for keep refs, but that is its observation of three scratch repos,
  not a claim about jj repositories in general.
- **The reflog windows are sourced, not measured.** The 90-day and 30-day defaults come from
  git-reflog(1) and the config fragment; no arm waits out a default window, so the window's
  effect on a real keeper is documented behaviour plus the arms' explicit expiry.
- **`git gc` inside jj's shell-out is not shown to expire reflogs with `--all`.** git-gc(1) lists
  reflog pruning among its tasks [S063]; the exact argv it uses internally was not opened for
  this entry, so the composition claim in step 5 stays [INFERENCE].
- **No jj command was swept for a way to drop the rewritten working-copy commit's keep ref.** The
  record shows only that `op-abandon-and-util-gc` lowers `keep_refs` without removing B, and the
  seat reports the fixture's `jj abandon` on that commit printing the already-hidden skip
  message — text that is not in the record, so the entry does not claim no such command exists.
- **No receipt tool, class or gate moves.** This is vocabulary and mechanism for F1; the deletion
  certification stays OFF and K5 HELD.

## Lane link

- `corpus/README.md`:46 lists F1's remaining work; `PROVINCE.md`:205-212 carries the round-30
  boundary note that the object-prune clock is unmeasured. This entry is that clock's claim; the
  F1 map row and the frontier line are the L1's to update in the same commit.
- Held rule, not restated: `corpus/knowledge/jj-keep-ref-expiry.md` (ref removal, and its
  wave-2 correction that a descendant keep ref keeps B reachable) and
  `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4 (receipt roots).
- Instrument and record: `tests/fixtures/r31-jj-object-clock.sh` and
  `census/round-31/records/jj-object-clock-run.txt`. The fixture builds colocated repositories
  only under `$TMPDIR`, calls `jj` and `git` by bare name so the PATH-shim leg can observe them,
  and never runs against a lane repository.

## Gate

opened: 2026-10-26 — the three snapshots named below were fetched live from their tags this run
and opened; each quote is copied from the bytes named on its own line, is at most 25 words, and
contains no pipe character. Snapshot paths are this round's capture paths under
`census/round-31/sources/`.

- S222 git-reflog(1) v2.56.0, § DESCRIPTION lines 66-68 — "Entries older than `expire` time, or entries older than `expire-unreachable` time and not reachable from the current tip, are removed from the reflog." — https://git-scm.com/docs/git-reflog — snapshot: census/round-31/sources/git-reflog.adoc
- S222 git-reflog(1) v2.56.0, OPTIONS `--expire=<time>` lines 115-116 — "prunes entries regardless of their age" — https://git-scm.com/docs/git-reflog — snapshot: census/round-31/sources/git-reflog.adoc
- S222 git-reflog(1) v2.56.0, OPTIONS `--expire-unreachable=<time>` lines 119-121 — "that are not reachable from the current tip of the branch" — https://git-scm.com/docs/git-reflog — snapshot: census/round-31/sources/git-reflog.adoc
- S222 git-reflog(1) v2.56.0, OPTIONS `--expire=<time>` lines 113-115 — "configuration setting `gc.reflogExpire`, which in turn defaults to 90 days" — https://git-scm.com/docs/git-reflog — snapshot: census/round-31/sources/git-reflog.adoc
- S222 git-reflog(1) v2.56.0, OPTIONS `--expire-unreachable=<time>` lines 122-124 — "configuration setting `gc.reflogExpireUnreachable`, which in turn defaults to 30 days" — https://git-scm.com/docs/git-reflog — snapshot: census/round-31/sources/git-reflog.adoc
- S063 git-gc(1) v2.56.0, § CONFIGURATION gc.reflogExpire lines 115-119 (config fragment) — "removes reflog entries older than this time; defaults to 90 days" — https://git-scm.com/docs/git-gc — snapshot: census/round-31/sources/gc.adoc
- S063 git-gc(1) v2.56.0, § CONFIGURATION gc.reflogExpireUnreachable lines 124-128 (config fragment) — "this time and are not reachable from the current tip; defaults to 30 days" — https://git-scm.com/docs/git-gc — snapshot: census/round-31/sources/gc.adoc
- S063 git-gc(1) v2.56.0, § CONFIGURATION gc.pruneExpire lines 96-97 (config fragment) — "When 'git gc' is run, it will call 'prune --expire 2.weeks.ago'" — https://git-scm.com/docs/git-gc — snapshot: census/round-31/sources/gc.adoc
- jj docs/git-compatibility.md v0.45.1, § Git-specific behaviours, section Garbage collection line 52 — "It should be safe to run `git gc` in the Git repo, but it's not tested" — snapshot: census/round-31/sources/git-compatibility.md

- ADMIT: `corpus/knowledge/jj-dropped-keep-object-lifetime.md` — reason: closes the object-prune-clock gap named at `PROVINCE.md`:208 and in the held entry's wave-2 correction, with three tag-verified sources and one measured run, and leaves the ref-removal rule and the receipt root rule untouched.
- REJECT: reading `git gc --prune=now` as a reflog expiry — reason: `--prune` is documented as a loose-object date while reflog dates come from `gc.reflogExpire`/`gc.reflogExpireUnreachable`, so a lane receipt cannot claim a reflog to be empty from a prune invocation alone.
