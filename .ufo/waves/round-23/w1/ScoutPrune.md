# ScoutPrune — live git-prune page, installed man, and the prune/fsck set question

STATUS: PASS — the live page (https://git-scm.com/docs/git-prune, opened 2026-10-25) supplied all
five requested quotes, each verified byte-present in both the live page and the installed
`man git-prune` (git 2.56.0, dated 2026-09-27), and the assigned question is answered NO with a
page quote plus four executed counter-examples in a scratch repo.

## Evidence

- Access: `curl -sSL -A <UA> https://git-scm.com/docs/git-prune` → 27823 bytes, 2026-10-25.
  Page header states `git-prune last updated in 2.43.0`; its changelog list states
  `2.43.1 → 2.56.0 no changes`.
- Installed side: `git --version` → `git version 2.56.0`; `MANWIDTH=80 man git-prune | col -b`
  footer → `Git 2.56.0   2026-09-27   GIT-PRUNE(1)`. (`man`, `groff`, `col` all present at
  `/usr/bin`; no tool installed or upgraded this run.)
- Quote presence check (tag-stripped, entity-unescaped, whitespace-normalised, space-before-
  punctuation removed), 11 sentences against live page and man page:
  `desc_unpacked live=True man=True`, `desc_packed_remain True/True`, `dry_run True/True`,
  `expire True/True`, `gc_note_desc True/True`, `gc_note_notes True/True`,
  `fsck_unreachable True/True`, `prune_refs_heads True/True`, `prune_packed_clause True/True`,
  `fsck_lost_found live=False man=True` (live HTML renders `into.git/lost-found/` with the space
  eaten by markup adjacency — same words, see Finding 9), `fsck_default_heads True/True`.
- Executed probes, all in `/var/tmp/souji-r23-ScoutPrune/` (own scratch git repos, `user.name=s`;
  removed at end: `rm -rf` rc=0, `scratch exists: False`). No lane write, no `git` state created
  in the lane, no deletion/move outside the scratch dir.

## Findings

### 1. Prune scope in DESCRIPTION — unreachable **unpacked** objects only

> "prunes all unpacked objects unreachable from any of these head objects from the object database"

— https://git-scm.com/docs/git-prune § DESCRIPTION, 2026-10-25; same sentence in
`/usr/share/man/man1/git-prune.1.gz` § DESCRIPTION. (14 words.)

### 2. Packed objects are explicitly out of scope

> "Note that unreachable, packed objects will remain."

— same § DESCRIPTION (next paragraph); the page adds `If this is not desired, see git-repack[1].`
(8 words.)

### 3. `-n` / `--dry-run`

> "Do not remove anything; just report what it would remove."

— § OPTIONS, `-n` `--dry-run`. (10 words.) Report-only; it does not imply the reported set equals
any other command's set (see Finding 6).

### 4. `--expire <time>`

> "Only expire loose objects older than <time>."

— § OPTIONS, `--expire`. (7 words.) Note the word *loose*: the filter applies to unpacked objects
only, so `--expire` cannot bring packed objects into the reported set.

### 5. The page's own recommendation about `git gc`

> "In most cases, users should run git gc, which calls git prune."

— § DESCRIPTION note block (12 words), and in § NOTES:

> "In most cases, users will not need to call git prune directly, but should instead call git gc"

— § NOTES (18 words; the sentence continues "which handles pruning along with many other
housekeeping tasks"). The page never recommends bare `git prune`; § NOTES closes with
"For a description of which objects are considered for pruning, see git fsck's --unreachable
option."

### 6. ANSWER: `git prune -n` does **not** report the same set as `git fsck --unreachable`

The decisive quote, on the prune side:

> "Note that unreachable, packed objects will remain."

against the fsck side:

> "Print out objects that exist but that aren't reachable from any of the reference nodes."

— https://git-scm.com/docs/git-fsck § OPTIONS `--unreachable`, 2026-10-25 (14 words). `prune -n`
reports what it *would remove*; packed unreachable objects are never removed, so they can never be
reported, while `fsck --unreachable` prints them regardless of storage form. Four executed
counter-examples (git 2.56.0), each `fsck --unreachable --no-reflogs` vs `git prune -n`:

- **Packed unreachable** — commit c2 packed while reachable, then unreferenced (`reset --hard`,
  `reflog expire`): `count: 0 in-pack: 6`; fsck prints 3 lines
  (`unreachable commit 2dd2e84c…`, `unreachable tree 0e493054…`, `unreachable blob f719efd4…`);
  `git prune -n` and `git prune -n --expire=now` both print **nothing**.
- **Cruft pack (modern default)** — same setup then `git gc --cruft -q` (default 2-week expiry):
  `packs: 2`, cruft pack carries a `.mtimes` file; fsck still prints the same 3 objects;
  `git prune -n` prints **nothing**. So on any repository that has been gc'd with defaults,
  `prune -n`'s set is systematically smaller than fsck's.
- **Reachable loose duplicate** — a loose copy of a *reachable* packed blob (`5626abf0…`, written
  by hand as zlib `blob 4\0one\n`): `git prune -n` prints
  `rm -f .git/objects/56/26abf0f72e58d7a153368ba57db4c673c0e171`, i.e. a set member that is
  **reachable** and that fsck therefore never reports. This matches § DESCRIPTION:

  > "prunes the unpacked objects that are also found in packs by running git prune-packed"

  (14 words; `git prune-packed -n` alone prints the identical `rm -f` line.)
- **No default age floor** — a brand-new loose unreachable blob (`git hash-object -w`, mtime now)
  is printed by bare `git prune -n`. The 2-week default belongs to `git gc`, not `git prune`:
  https://git-scm.com/docs/git-gc § OPTIONS `--prune=<date>` (2026-10-25):

  > "Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable gc.pruneExpire)."

  (18 words.) So `--expire` is the *only* age gate on `prune -n`, and it is absent by default.

Additional divergences worth naming: output shape differs (`fsck`: `unreachable <type> <sha>` and
`dangling <type> <sha>` lines; `prune -n`: `<sha> <type>` lines plus `rm -f <path>` lines), and
`fsck` without `--unreachable` labels the same population `dangling` (observed:
`dangling commit 2dd2e84c…`, `dangling blob 715a6426…`), so even the two fsck spellings are not
the same output.

### 7. Head population: the page is narrower than the observed behaviour

§ DESCRIPTION says prune runs fsck "using all the refs available in refs/" (7 words, quoted
verbatim). Observed in 2.56.0, that sentence understates the head set:

- A loose unreachable commit held only by a reflog entry: `git fsck --unreachable` prints nothing
  and `git prune -n --expire=now` also prints nothing → prune counted the reflog as a head.
- A blob reachable only from the index (`git add` without commit): neither fsck nor
  `git prune -n` reports it → prune counted the index as a head.

So on the *head* axis the two commands agree in 2.56.0 (both effectively
"index + refs + reflogs", matching fsck's documented default `git fsck defaults to using the index
file, all SHA-1 references in the refs namespace, and all reflogs`, 18 words); the sets diverge on
the *storage* and *duplicate* axes, not the head axis. This is a doc-versus-behaviour gap, recorded
as [OBSERVED] for 2.56.0 only, not as a general rule.

### 8. Installed man vs live page: AGREES, no drift

`MANWIDTH=80 man git-prune | col -b` (47 lines of body) reproduces NAME, SYNOPSIS, DESCRIPTION
(including both note blocks and the prune-packed and shallow clauses), every OPTIONS entry,
EXAMPLES and NOTES with identical wording. Differences are typographic only: line wrapping,
`git prune`/`git gc` set in italics on the page, and U+2010 hyphenation in the man rendering
(`ob‐ jects`). Version reconciliation: installed 2.56.0, page last updated in 2.43.0, page
changelog `2.43.1 → 2.56.0 no changes` — the installed manual cannot be behind on this command.
No page-only or man-only clause found.

### 9. Consequence for this lane's read-only receipts (cross-lane, not a new claim)

`git prune -n` is not a substitute for an unreachable census: it under-reports packed and cruft
objects and over-reports reachable loose duplicates, and its output mixes two record shapes. The
read-only census path stays `git fsck --unreachable --no-dangling --no-reflogs` without
`--lost-found` — consistent with `w1/ScoutFsck.md` Finding 6 (only `--lost-found` writes), whose
quote the installed man carries as "Write dangling objects into .git/lost-found/commit/ or
.git/lost-found/other/." (the live page has the same words but its HTML renders `into.git/…` with
the space absorbed by markup; quote the man page for a SOURCES.md cell).

## Unknowns / not claimed

- Whether `--expire <time>` also gates the `prune-packed` duplicate lines was not tested (only
  loose-object expiry was exercised); the doc sentence "Only expire loose objects older than
  <time>." does not settle it.
- Alternates (`objects/info/alternates`) and `--full` interplay were not exercised.
- The 2.56.0-only observations in Findings 6 and 7 were not cross-checked against older git; no
  older binary was installed (installs were not needed and none were performed).

## Attack log

None. No counter was run, no predicate/target/key set touched, no file outside
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/w1/` was written; the only
deletion was my own `/var/tmp/souji-r23-ScoutPrune/` scratch.
