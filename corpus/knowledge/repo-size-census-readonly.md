source: S115 — https://git-scm.com/docs/git-count-objects — § OPTIONS -v/--verbose — git 2.56.0
source: S116 — https://git-scm.com/docs/git-fsck — § OPTIONS --unreachable, --dangling, --no-reflogs, --lost-found — git 2.56.0
source: S117 — https://git-scm.com/docs/git-prune — § DESCRIPTION, § OPTIONS -n/--dry-run, --expire — git 2.56.0
verified-at: 2026-10-25 — host git 2.56.0-1; the three pages opened live this round and the installed man pages re-read the same day
recheck: on-release — re-read `man git-count-objects`, `man git-fsck`, `man git-prune` after a host git upgrade (matches the S115–S117 rows)
ground: F2 — repository size census (the census instruments and the write side effect a write-safety fixture must fence)

# A read-only size census needs three different instruments, and one of them writes

## Claim (F2: repository size census)

The census cannot be built from one instrument, and **one of the three candidate
instruments writes to the repository** unless it is explicitly held back.

1. **`git count-objects -v` is the size instrument, and it reports files git
   considers garbage (not objects).** § OPTIONS `-v, --verbose` lists `count`, `size`,
   `in-pack`, `packs`, `size-pack`, `prune-packable`, `garbage`, `size-garbage`
   and `alternate`. Two census consequences: `garbage`/`size-garbage` are not
   object-graph state at all — they are unrecognised files, so a size census that
   ignores them under-reports disk use; and `alternate` must be read, because an
   object database shared through an alternate makes the same bytes appear under
   more than one path.
2. **`git fsck` is the reachability instrument, and it distinguishes classes.**
   § OPTIONS: `--unreachable` prints objects reachable from no reference node;
   `--dangling, --no-dangling` prints objects that exist but are never *directly*
   used (default); `--no-reflogs` refuses to treat reflog-only commits as
   reachable. § OPTIONS fixes the default head set: the index file, all SHA-1
   references in the `refs` namespace, and all reflogs.
3. **`git fsck --lost-found` WRITES.** § OPTIONS: it writes dangling objects into
   `.git/lost-found/commit/` or `.git/lost-found/other/`, and for a blob the
   *contents* are written into the file rather than its object name. **This is the
   write-safety trap the F2 fixture must fence:** a census on a live repository
   must not use `--lost-found`. The read-only forms are `--unreachable` and
   `--dangling`.
4. **`git prune` is the deleter, and it is narrower than "unreachable".**
   § DESCRIPTION: prune runs `git fsck --unreachable` over `refs/` and prunes all
   *unpacked* objects unreachable from those heads; unreachable **packed** objects
   remain. § OPTIONS gives `-n, --dry-run` and `--expire <time>`. So an
   unreachable count from `git prune --dry-run` is not the set
   `git fsck --unreachable` reports, and is not the set `git gc` would free.

## What this does NOT establish

- `garbage` counts **files**, not objects; a file may be a valid loose object, a
  valid pack, or neither. No claim is made about how to classify the "neither"
  case.
- `git fsck`'s default head set depends on the **index** and the **reflogs**, both
  of which vary per repository; a census run against a different worktree or with
  a different index is not the same census.
- `git prune` is an ancillary command (`git(1)`, Ancillary Commands /
  Manipulators — not a plumbing command), and the page's own note says users
  should run `git gc`, which calls it. Nothing here recommends running either.
- No claim is made that any of these instruments is safe to run concurrently with
  another writer; that is exactly what the `/var/tmp` write-safety fixture would
  have to establish and is still owed.
- No fleet repository was censused for this entry: no `count-objects`, `fsck` or
  `prune` run is reported here, and no size figure for this lane or the fleet is
  claimed.

## Lane link and consequence

`corpus/knowledge/git-repo-structure-readonly.md` (S035/S036/S037) covers
`git repo structure`, which reports the **reachable** object graph; its probe is
`tools/souji-repo-structure.sh`, and its observed no-persistent-change result is
recorded in `census/round-13/verification.json` (measured_commit `6f8ee0f3…`,
`structure-selftest` exit 0, `artifacts_unchanged_during_run` true). This entry
supplies the halves that entry names as missing — the **unreachable** census
(read-only forms only) — and the size census it does not report, including
`garbage`/`size-garbage`/`alternate`. The `--lost-found` write is the concrete
hazard such a fixture must exclude. (`git-repo-structure-readonly.md`'s
structure-selftest exit-0 result is bound at `census/round-13/verification.json`'s
measured_commit, not at the hash this entry's parenthetical once named.)

## Round 24 narrowing (appended 2026-10-25; the text above stands as filed)

- **Claim 1 is narrowed.** `garbage` is not always unrecognised object-database
  files. Read inside a linked worktree, `count-objects -v` also counts parts of
  that worktree's private gitdir (`refs`, and `refs/bisect`, `refs/worktree`,
  `logs/refs/*` once they exist), which are healthy structure and carry no disk
  use worth reporting; read against the common git dir it does not. A size
  census therefore reads past that sweep instead of adding it to disk use. See
  `count-objects-linked-worktree-garbage.md` (S120–S123) and the census rule
  that `tools/souji-size-census.py` applies.
- **The write-safety fixture now exists for sequential runs.**
  `tests/fixtures/r24-size-census.py` fences `count-objects -v` and
  `fsck --unreachable --no-reflogs` with a common-dir `.git` manifest and shows
  `fsck --lost-found` writing (`cases=8 pass=8 … lost_found=WRITE-DETECTED`,
  receipt `census/round-24/records/c1-after.tsv`). Concurrency with another
  writer is still not established and stays owed.

## Gate

url: https://git-scm.com/docs/git-count-objects
snapshot: census/round-23/sources/git-count-objects.1.txt
opened: 2026-10-25

- ADMIT: "garbage: the number of files in the object database that are neither valid loose objects nor valid packs" — § OPTIONS -v/--verbose — reason: the field a size census must read, and the staged claim's first consequence — snapshot: census/round-23/sources/git-count-objects.1.txt
- ADMIT: "alternate: absolute path of alternate object databases; may appear multiple times, one line per path." — § OPTIONS -v/--verbose — reason: an alternate makes the same bytes appear under two paths, so the size census must read it — snapshot: census/round-23/sources/git-count-objects.1.txt
- ADMIT: "Print out objects that exist but that aren’t reachable from any of the reference nodes." — § OPTIONS --unreachable — reason: the read-only unreachable census this entry supplies for F2 — snapshot: census/round-23/sources/git-fsck.1.txt
- ADMIT: "Do not consider commits that are referenced only by an entry in a reflog to be reachable." — § OPTIONS --no-reflogs — reason: it moves reflog-only commits into the unreachable set, so the head set must be recorded with the count — snapshot: census/round-23/sources/git-fsck.1.txt
- ADMIT: "Write dangling objects into .git/lost-found/commit/ or .git/lost-found/other/, depending on type." — § OPTIONS --lost-found — reason: the write side effect the read-only fixture must fence, quoted from the page — snapshot: census/round-23/sources/git-fsck.1.txt
- ADMIT: "prunes all unpacked objects unreachable from any of these head objects from the object database" — § DESCRIPTION — reason: prune's scope is unpacked objects only, so its count is not fsck's unreachable set — snapshot: census/round-23/sources/git-prune.1.txt
- ADMIT: "Do not remove anything; just report what it would remove." — § OPTIONS -n, --dry-run — reason: the only non-deleting prune form, and it still reports a different set than fsck — snapshot: census/round-23/sources/git-prune.1.txt
- REJECT: git fsck --lost-found as a census instrument — reason: it materialises blob contents under .git/lost-found, so a census on a live repository would write; the read-only forms cover the same objects — flip: admit it only for a census run on a disposable copy under /var/tmp whose writes are discarded, with that copy named in the receipt
- REJECT: the staged entry's provenance cells (staged ids and its 2026-10-23 access date) — reason: this lane's registry resolves those ids to different documents, so an as-is append would cite the wrong pages — flip: re-point by document after the lane's own ids are minted, with this round's access date and the quotes above
