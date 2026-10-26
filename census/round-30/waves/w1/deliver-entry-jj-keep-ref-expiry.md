source: S220 — jj CLI reference at tag v0.45.1 — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap — section `jj operation abandon` lines 2419; section `jj util gc` lines 3793 and 3799-3805 — snapshot census/round-30/sources/cli-reference@.md.snap
source: S221 — jj source at tag v0.45.1, lib/src/git_backend.rs — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs — line 100 (namespace constant), lines 900-903 (recreate_no_gc_refs), lines 929-937 (mtime check), line 977 (git gc argument), lines 1558-1564 (backend gc) — snapshot census/round-30/sources/git_backend.rs
source: S222 — jj operation log at tag v0.45.1, docs/operation-log.md — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md — section Introduction, lines 5-8 (view contents: refs and set of heads) — snapshot census/round-30/sources/operation-log.md
source: S223 — git-gc(1) at tag v2.56.0, Documentation/git-gc.adoc — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc — section DESCRIPTION lines 18-20; OPTIONS `--prune` lines 81-83; NOTES lines 159-161 — snapshot census/round-30/sources/git-gc.adoc
verified-at: 2026-10-26 — all four snapshots were fetched live from their tags this run and compared byte-for-byte with the round's capture (`cmp` identical): cli-reference@.md.snap sha256 b330694348c2a6fb21b637425c711d48ac9fa41d0b3596b4ca2955f7a9333554, git_backend.rs sha256 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69, operation-log.md sha256 2a48dab85483f8bed666ccc1aebd458d70f4ff57ece1a122aee8889b3209ce18, git-gc.adoc sha256 e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c; the measurement ran on jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 and git 2.56.0 (host binaries; both version lines are in the run record)
recheck: 365d — bash -c 'd=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-r30-keeprecheck.XXXXXX"); curl -fsSL -o "$d/c.snap" "https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap"; curl -fsSL -o "$d/g.rs" https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs; curl -fsSL -o "$d/o.md" https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md; curl -fsSL -o "$d/g.adoc" https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc; sha256sum "$d"/*; rm -r "$d"'   # expect b3306943… 95147270… 2a48dab8… e3dbc408…
ground: F1 — git-native housekeeping vs receipts (keep-ref expiry)

# A `refs/jj/keep` ref is removed by jj's own garbage collection, never by `git gc` alone

## Claim (F1: keep-ref expiry)

How jj 0.45.1 writes `refs/jj/keep/` refs and why a receipt must not treat them as roots is the
held rule of `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4; this entry does not
restate it. What was unmeasured there (its Limits, first bullet) is the removal side: which action
deletes a keep ref, on what threshold, and what a git-side collection does to a commit that only a
keep ref names. Four tag-verified sources and one measured run answer that.

1. **One function rewrites the ref set.** `recreate_no_gc_refs` takes the heads it is given, keeps
   the keep refs for them, and builds the deletion list from every other keep ref whose loose-ref
   file is not newer than `keep_newer`, applying both in one ref transaction
   (git_backend.rs:900-903, :917-961) [S221]. The heads are `index.all_heads_for_gc()` inside the
   backend `gc(index, keep_newer)` (git_backend.rs:1558-1564) [S221]. So the ref set is a function of
   the index/operation views jj reads and of a caller-supplied `keep_newer` instant — not of git.
2. **The age gate, and the hole in it.** A ref that would otherwise go is kept when its loose-ref
   file is newer than `keep_newer` (git_backend.rs:938-944) [S221], and the source comment says this
   check is racy on re-import and that an existing packed ref is not demoted to loose
   (git_backend.rs:929-937) [S221]. A packed keep ref therefore has no loose file whose mtime can
   save it. [INFERENCE] the metadata probe fails for a packed ref and the ref goes regardless of age;
   this path was read, not measured — the fixture's refs are loose.
3. **`jj util gc --expire` is the lever, with two clocks.** The command's `--expire` is a time
   threshold whose default prunes only obsolete objects and operations older than two weeks
   [S220, `jj util gc` lines 3799-3805]; arbitrary absolute and relative timestamps are deferred to
   a later release, so v0.45.1 accepts the single literal `now` and rejects anything else — the
   record's `future-expire-control` step shows `--expire=tomorrow` rejected with rc=1. The backend
   then calls git with `--prune=@<keep_newer>` (git_backend.rs:977) [S221], so the keep-ref age test
   and git's loose-object prune share one instant.
4. **`jj op abandon` changes reachability; it does not delete the ref.** The doc says abandoned
   operations, commits and other unreachable objects can later be garbage collected by using
   `jj util gc`, and that predecessors are discarded once unreachable from the operation history
   [S220, line 2419]. The operation object's view holds the set of heads [S222, lines 5-8], which
   is the state a later `gc` reads. Abandoning is therefore the precondition that lets a keep ref
   fail the current-heads test in step 1; the deletion still happens inside `jj util gc`.
5. **`git gc` alone removes neither the ref nor the commit.** git gc removes unreachable objects
   [S223, lines 18-20] and prunes loose objects older than `--prune`, two weeks by default
   [S223, lines 81-83], keeping objects newer than that date and everything reachable from them
   [S223, lines 159-161]. A keep ref is a ref, so the commit it names stays reachable and stays out
   of that removal. [INFERENCE] that refs are reachability roots is git's ref model rather than a
   sentence quoted here; the record's `git-gc-prune-now` step is the corroboration.

**Observed:** `census/round-30/records/jj-keep-expiry-run.txt` (fixture
`tests/fixtures/r30-jj-keep-expiry.sh`, run under `$TMPDIR` on jj 0.45.1 and git 2.56.0) prints one
`RESULT ` line per step, with `keep_refs=<k>` counting `refs/jj/keep/*` and `target_keep` recording
whether a keep ref still names the abandoned commit: `commit` keep_refs=<k> target_keep=yes;
`abandon` keep_refs=<k> target_keep=yes; `git-gc-prune-now` keep_refs=<k> target_keep=yes;
`util-gc-expire-now` keep_refs=<k> target_keep=no; `op-abandon-then-util-gc` keep_refs=<k>
target_keep=no; `future-expire-control` keep_refs=<k> target_keep=yes with `--expire=tomorrow`
rejected rc=1. The record names those steps `1-commit-A-B`, `2-abandon-B`, `3-git-gc-prune-now`,
`4-util-gc-expire-now`, `5-op-abandon-util-gc-expire-now`, `6-future-expire-control`; steps 6-8 run
on a second repository, so their counts do not continue the first sequence. The commit object is
present at every step: the run separates ref removal from object removal, and only ref removal is
measured here.

## Consequence for souji receipts

A keep-only commit is not a durable receipt root. Steps 3-5 remove its keep ref without either a
git-side collection or a lane action, after which the object is unreachable and a later prune can
drop it; the held rule that already excludes `refs/jj/*` from a receipt's roots and refuses novel
keep-only content is `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4, and it is not
restated here. This entry supplies the mechanism that makes that rule load-bearing: the ref
disappears when jj garbage-collects, on jj's threshold, not when git does.

## What this does NOT establish

- **No automatic collection is shown.** The opened CLI reference documents `jj util gc` as the
  collection command; whether any other jj command invokes backend `gc` was not opened or measured
  here.
- **No deletion time can be promised.** The age test is called racy on re-import in the source
  (git_backend.rs:929-937) [S221], and a packed ref bypasses the test [INFERENCE from :931].
- **Object removal is not measured.** Every step of the record reports `object_present=yes`; that a
  later `git gc --prune=now` removes the unreferenced object is git's documented behaviour for
  unreachable objects [S223] and an inference for this fixture, not a measured row.
- **The future-expire control bounds v0.45.1 only.** It shows `--expire=tomorrow` rejected in this
  release; it says nothing about a later one, where arbitrary timestamps are documented as coming.
- **The hidden-head arm is not measured deterministically.** The fixture's target has a child, so it
  fails the current-heads test and the age gate alone decides it. The mechanism probe in this wave
  (`receipt-SwarmExecutor06-keepref-mechanism.txt`) shows a keep ref surviving two `jj util gc
  --expire=now` runs while naming a commit that `jj log` reports as hidden; which commits
  `all_heads_for_gc()` returns for hidden heads is not settled by the delivered record.
  [INFERENCE] a hidden head keeps its ref because the heads list is the index's heads.
- **No receipt rule is changed.** No class, token, root set or gate moves here; the entry is
  vocabulary and mechanism for F1.

## Lane link

- `corpus/README.md`:46 names keep-ref expiry as the remaining F1 item; this entry is that item's
  claim, and the F1 coverage row is updated in the same commit.
- `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4 hold the receipt rule; its Limits
  first bullet is the gap closed here. Its Limits also records that the lane helper contains neither
  `jj op abandon` nor `jj util gc`, so lane tooling does not exercise step 3.
- Instrument and record: `tests/fixtures/r30-jj-keep-expiry.sh` and
  `census/round-30/records/jj-keep-expiry-run.txt`. The fixture builds colocated repositories only
  under `$TMPDIR` and never runs against a lane repository.

## Gate

opened: 2026-10-26 — the four files were fetched live this round and opened; each quote below is
copied from the bytes named on its own line, is at most 25 words, and contains no pipe character.
Snapshot paths are this round's capture paths under `census/round-30/sources/`.

- S220 jj CLI reference v0.45.1, section `jj operation abandon`, line 2419 — "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history." and "The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command." — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap — snapshot: census/round-30/sources/cli-reference@.md.snap
- S220 jj CLI reference v0.45.1, section `jj util gc`, line 3793 — "To garbage-collect old operations and the commits/objects referenced by them, run `jj op abandon ..<some old operation>` before `jj util gc`." — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap — snapshot: census/round-30/sources/cli-reference@.md.snap
- S220 jj CLI reference v0.45.1, section `jj util gc` OPTIONS `--expire`, lines 3801-3805 — "By default, only obsolete objects and operations older than 2 weeks are pruned." and "can be passed to this parameter." and "Support for arbitrary absolute and relative timestamps will come in a subsequent release." — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap — snapshot: census/round-30/sources/cli-reference@.md.snap
- S221 jj source v0.45.1, lib/src/git_backend.rs lines 900-901, doc comment on `recreate_no_gc_refs` — "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other" — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs — snapshot: census/round-30/sources/git_backend.rs
- S221 jj source v0.45.1, lib/src/git_backend.rs lines 929-937, mtime check on the loose ref — "Check timestamp of loose ref, but this is still racy on re-import" and "existing packed ref won't be demoted to loose ref" — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs — snapshot: census/round-30/sources/git_backend.rs
- S222 jj operation log v0.45.1, section Introduction, lines 5-8 — "Each operation object contains a snapshot of how the repo looked at the end of the operation." and "as well as the set of heads in the repo" — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md — snapshot: census/round-30/sources/operation-log.md
- S223 git-gc(1) v2.56.0, section DESCRIPTION, lines 18-20 — "removing unreachable objects which may have been created from prior invocations of 'git add'" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc — snapshot: census/round-30/sources/git-gc.adoc
- S223 git-gc(1) v2.56.0, OPTIONS `--prune`, lines 81-83 — "Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable `gc.pruneExpire`)." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc — snapshot: census/round-30/sources/git-gc.adoc
- S223 git-gc(1) v2.56.0, section NOTES, lines 159-161 — "Any object with modification time newer than the `--prune` date is kept, along with everything reachable from it." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc — snapshot: census/round-30/sources/git-gc.adoc

- ADMIT: `corpus/knowledge/jj-keep-ref-expiry.md` — reason: closes the keep-ref-lifetime gap named in `jj-colocation-receipts.md` Limits with four tag-verified sources and one measured run, and leaves the held receipt rule of sections 3 and 4 untouched.
- REJECT: reading the loose-ref mtime check as an expiry guarantee for a keep ref — reason: the source comment calls that check racy on re-import and a packed ref skips it, so no deletion time can be promised from it.
