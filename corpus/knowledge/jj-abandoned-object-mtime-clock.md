source: S223 — gitformat-pack(5) at tag v2.56.0 (placeholder id: the L1 renumbers by document) — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — § cruft packs lines 611-689, including the `.mtimes` table at lines 341-354 — snapshot census/round-32/sources/gitformat-pack.adoc
source: S063 — git-gc(1) — https://git-scm.com/docs/git-gc — § OPTIONS --cruft lines 61-65, --prune lines 81-87, --no-prune lines 89-90; § NOTES lines 141-161 — snapshot census/round-32/sources/git-gc.adoc
source: S002 — git-gc(1) grace periods — https://git-scm.com/docs/git-gc — § CONFIGURATION gc.cruftPacks lines 85-88 and gc.pruneExpire lines 96-105, included from Documentation/config/gc.adoc at tag v2.56.0 by git-gc.adoc:136 — snapshot census/round-32/sources/gc.adoc
verified-at: 2026-10-26 — the three snapshots were fetched live from tag v2.56.0 this run and hashed: gitformat-pack.adoc sha256 ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b (27494 B), git-gc.adoc sha256 e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c (6744 B, byte-identical to the round-30 capture at census/round-30/sources/git-gc.adoc, so its line anchors still address these bytes), gc.adoc sha256 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a (7753 B); the run record census/round-32/records/jj-mtime-clock-run.txt is the fixture seat's delivery `.ufo/waves/round-32/w1/deliver-jj-mtime-clock-run.txt` (sha256 01cf6dc0011ae8f22d16922846b6834641df5dbce6e3a26cd0c267ede97e8254, 1887 B, 22 `RESULT` lines) to be installed unchanged at landing; it opens with `jj-version: jj 0.45.1-7c41cdeb…` and `git-version: git version 2.56.0`, and every Observed span below is a whole line of it.
recheck: 365d — bash -c 'd=$(mktemp -d "${TMPDIR:-/fast/scratch/hyaku}/souji-r32-mtime.XXXXXX"); for p in gitformat-pack.adoc git-gc.adoc config/gc.adoc; do curl -fsSL -o "$d/$(basename "$p")" "https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/$p"; done; sha256sum "$d"/*; rm -r "$d"'   # expect ec285ba4… (gitformat-pack) e3dbc408… (git-gc) 0ab75f6f… (config/gc)
ground: F1 — git-native housekeeping vs receipts (the per-object mtime clock behind a dropped keep ref)

# What decides an abandoned commit's object fate once keep refs and reflog entries are gone

## Claim (F1: the object's own clock)

Which roots hold an abandoned commit's object after its keep ref is gone, and which levers remove
it, is the held rule of `corpus/knowledge/jj-dropped-keep-object-lifetime.md`; this entry does not
restate it. That entry names one holder it never isolated — the object's own modification time
against the prune date — and leaves open what its `corpus/README.md`:679-681 frontier line calls
the reach of git's cruft-pack handling. Both are settled below from git's own documentation at tag
v2.56.0, and measured by the r32 fixture's record.

1. **The clock is the object's own mtime, compared with the date the gc passes.** git keeps "Any
   object with modification time newer than the `--prune` date is kept, along with everything
   reachable from it" (git-gc.adoc:160-161) [S063]. Reachability decides nothing at that boundary: an
   unreachable object whose mtime is inside the window survives a gc that removed every ref and
   every reflog entry naming it, and one whose mtime is outside it does not. The record isolates that
   pair: arm `recent` runs a plain `git gc` in a repository whose keep refs and reflog entries were
   just dropped (fixture `seal`, tests/fixtures/r32-jj-mtime-clock.sh:197-202) and leaves B present in
   a cruft pack; arm `old` is built the same way, backdates B's own commit, tree and blob files, and
   the identical `git gc` leaves B absent. Only the backdating differs.

2. **Two expiry calls, one date.** A gc expiring unreachable objects runs `prune --expire` and, when
   cruft packs are in use, also `repack --cruft --cruft-expiration`, and both take the same date:
   "When 'git gc' is run, it will call 'prune --expire 2.weeks.ago'" and "(and 'repack --cruft
   --cruft-expiration 2.weeks.ago' if using cruft packs via `gc.cruftPacks` or `--cruft`)."
   (gc.adoc:96-99) [S002]. The date is a parameter, not a constant: `gc.pruneExpire` overrides it
   (same paragraph), and the total form on the command line is "--prune=now prunes loose objects
   regardless of their age" (git-gc.adoc:84) [S063].

3. **Recent → kept, and the location is the point.** Cruft packs are the default, not an option:
   "`--cruft` is on by default." (git-gc.adoc:64-65), and `gc.cruftPacks` "Store unreachable objects
   in a cruft pack (see linkgit:git-repack[1]) instead of as loose objects. The default is `true`."
   (gc.adoc:86-88) [S002]. So a recent unreachable object is packed, not left loose — "A cruft pack
   eliminates the need for storing unreachable objects in a loose state by including the per-object
   mtimes" (gitformat-pack.adoc:655-656) [S223]. With cruft packs switched off the older path stands
   and the same object is kept loose: "those unreachable objects are stored as loose objects and stay
   that way until they are older than the expiration window" (gitformat-pack.adoc:631-632) [S223].
   A receipt that records presence without that location has not said where the object will be
   looked for next. The record shows both locations for the same age — `arm=recent step=gc-default`
   reports B in `where=cruft`, `arm=nocruft step=gc-cruft-disabled` reports the recent C in
   `where=loose` — so one variable, `gc.cruftPacks`, decides which. `cruft` in the record is not a
   guess about the pack: the fixture reports it only when the pack carries a `.mtimes` sibling (`if
   [ -f "${i%.idx}.mtimes" ]; then printf 'cruft'`, tests/fixtures/r32-jj-mtime-clock.sh:107-120).

4. **The clock travels per object inside the cruft pack.** The reason unreachable objects used to be
   stored loose was the clock itself — "Git must store these unreachable objects loose in order to
   keep track of their per-object mtimes." (gitformat-pack.adoc:635-636) — because a pack carries one
   mtime, and freshening it would "cause the pack's mtime to get updated, and the objects within it
   would never leave the expiration window" (:638-640). A cruft pack removes that limitation by
   carrying the timestamps in a sibling file: the algorithm writes the pack "along with a `.mtimes`
   file that records the per-object timestamps" (:674-675), and that file's table holds one date per
   object, where "The ith value is the modification time (mtime) of the ith object in the
   corresponding pack by lexicographic (index) order." and "The mtimes count standard epoch seconds."
   (:351-354). Consequence: objects in one cruft pack age independently, and the pack's own mtime says
   nothing about any of them. The record witnesses the outcome without reading the table: in arm
   `mixed` the old B sits inside a cruft pack at `gc-prune-never` and is absent after the next default
   gc, while the recent C stays in `where=cruft` with `object_present=yes` across that same gc. One
   pack, one command, two fates, decided by the per-object dates.

5. **Old → dropped, by whichever call owns the object's location.** The cruft date is an expiry, not
   a floor: the `--cruft-expiration` option "allows the generated cruft pack to omit expired objects"
   (gitformat-pack.adoc:684-685) [S223], and "It is linkgit:git-gc[1] that is typically responsible
   for removing expired unreachable objects." (:688-689). The record separates the two calls by
   location. An object already inside a cruft pack is removed by the cruft call: arm `mixed` has the
   old B in `where=cruft` after `gc-prune-never` and `where=absent` after the next default gc, and B
   was not loose at that point, so no loose prune can account for the removal. An object still loose
   is removed by the prune call: arm `nocruft` keeps the old B loose and then, under
   `gc.cruftPacks=false`, reports it absent while the recent C, equally loose, stays present. Either
   way the decisive quantity is the object's age against the date of claim 2.

6. **`gc.pruneExpire=never` takes the clock out of the decision.** The value "never" "may be used to
   suppress pruning." (gc.adoc:102) [S002], and the same variable sets the single date both calls of
   claim 2 receive (gc.adoc:96-99). The record measures the result: `arm=never
   step=gc-pruneexpire-never` leaves the backdated old B present in `where=cruft`, where the plain
   `git gc` of arm `old` left an identically aged object absent. The two arms are built by the same
   sequence and differ in that one config value.

7. **`--prune=never` buys more than its one-line description claims.** The flag is documented for
   loose objects only — "Do not prune any loose objects." (git-gc.adoc:89-90) [S063] — while the
   config variable moves the one date that also reaches `repack --cruft --cruft-expiration`
   (gc.adoc:96-99) [S002], and read literally the flag should leave an object that is already packed
   to the cruft call. The record does not bear that out: in arm `mixed`, `git gc --prune=never` moves
   the old B into a cruft pack and keeps it there (`where=cruft`, `object_present=yes`), so in this
   run the flag did not hand the old object to the cruft call's two-week date. The distinction that
   survives is documentary, not behavioural: a receipt may not infer the cruft call's argument from
   the flag's description, so it must record the argv it ran.

**Observed:** `census/round-32/records/jj-mtime-clock-run.txt` (fixture
`tests/fixtures/r32-jj-mtime-clock.sh`, run under `$TMPDIR` on jj 0.45.1 and git 2.56.0) opens with
`jj-version: jj 0.45.1-7c41cdeb…` and `git-version: git version 2.56.0` and holds 22 `RESULT ` lines
across the five arms of the frozen contract (`census/round-32/c3-contract.txt`); no commit id, path or
timestamp reaches a `RESULT` line, so repeated runs print identical lines (fixture header,
tests/fixtures/r32-jj-mtime-clock.sh:35-46). Every span below is one whole line of the record, copied
from the fixture seat's delivery installed unchanged at landing. Fields: `obj` names the abandoned
commit; `mtime` is the age the fixture gave its object files; `where` is `absent` when `git cat-file
-e` fails, else `loose` if the loose object file still exists and `cruft` if the pack holding it has a
`.mtimes` sibling; `object_present` is the exit status of that `git cat-file -e` (fixture
`where`/`present`/`emit`, tests/fixtures/r32-jj-mtime-clock.sh:105-131).

- **Recent clock, default gc — kept, inside the cruft pack (claims 1, 3):**
  `RESULT arm=recent step=gc-default obj=B mtime=recent where=cruft object_present=yes`
- **Old clock, the same default gc — dropped (claims 1, 2, 5):**
  `RESULT arm=old step=gc-default obj=B mtime=old where=absent object_present=no`
- **`--prune=never` puts the old object into a cruft pack and keeps it (claim 7):**
  `RESULT arm=mixed step=gc-prune-never obj=B mtime=old where=cruft object_present=yes`
- **The next default gc drops that packed old object (claims 4, 5):**
  `RESULT arm=mixed step=gc-default obj=B mtime=old where=absent object_present=no`
- **Its recent pack-mate survives the same gc (claim 4):**
  `RESULT arm=mixed step=gc-default obj=C mtime=recent where=cruft object_present=yes`
- **`gc.pruneExpire=never` keeps the old object instead (claim 6):**
  `RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes`
- **`gc.cruftPacks=false` drops the old object from the loose set (claim 5):**
  `RESULT arm=nocruft step=gc-cruft-disabled obj=B mtime=old where=absent object_present=no`
- **and keeps the recent one loose (claim 3):**
  `RESULT arm=nocruft step=gc-cruft-disabled obj=C mtime=recent where=loose object_present=yes`

## Consequence for souji receipts

A present object is not evidence of retention intent. Under the clock, presence is exactly what a
recent mtime produces with every ref, reflog entry and hook gone — so `git cat-file -e` succeeding
after a gc that named no age says only that the object was young at that instant, and says nothing
about whether anyone meant to keep it. The reverse holds too: the same gc argv empties an old object
and fills a cruft pack with a recent one, so an argv by itself explains neither outcome.

Receipt-grade for a deletion is therefore one field longer than the held rule requires. The receipt
must name (a) the gc invocation it ran or whose argv it recorded, (b) the object's age at that moment
— its mtime, or how that age was manufactured, backdating being the visible case in this round's
fixture — or the expiry setting in force (`--prune`, `gc.pruneExpire`), and (c) whether cruft packs
were on, because that decides both the location a survivor is found in and which of the two calls
applied the date (gc.adoc:96-99) [S002]. A receipt holding only an object id and a gc name reports a
value its own contract cannot explain: that is the r31 D1 shape — a record printing outside its
frozen field set — one level down, in the evidence rather than the format.

`where` is the field today's receipts lack. Presence in a cruft pack and presence loose expire on
different calls of the same invocation, so an unlocated presence cannot be re-checked by a later
seat, and an unlocated absence does not say which call removed the object. The record measures both
removal paths: the packed old object goes at the cruft call (`arm=mixed`), the loose old object at the
prune call (`arm=nocruft`), which is why the location is what tells a later seat which call to check.

Held, not restated: the keeper set and the release direction are
`corpus/knowledge/jj-dropped-keep-object-lifetime.md`; a receipt's root set and the refusal of novel
keep-only content are `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4.

## What this does NOT establish

- **No lane or fleet repository was measured.** Every repository of the run is scratch under the
  round's `$TMPDIR`; no lane repo is gc'd, no keep ref outside scratch is touched.
- **The mtime keeper is not isolated against a live keep ref or a reflog entry.** The fixture drops
  every keep ref naming the tracked commit or a descendant and expires every reflog before the first
  `RESULT` line (`seal`, tests/fixtures/r32-jj-mtime-clock.sh:197-202), and the old arms backdate the
  whole unreachable island so no recent descendant holds B through reachability (`backdate_island`,
  :231-236); this entry therefore says nothing about precedence when an mtime and a ref both hold an
  object, which stays the held entry's.
- **The `.mtimes` contents are never read.** The record's `where=cruft` rests on the existence of the
  `.mtimes` sibling file (:107-120); no line reports an individual date from that table, so the
  per-object clock is document plus outcome (claims 4 and 5), not an inspection of the table.
- **Which argument gc built for the cruft call is not opened.** Claims 6 and 7 rest on outcomes at git
  2.56.0; no `builtin/gc.c` bytes were opened, so the flag's forwarding to the cruft call is measured,
  not explained.
- **Whether an object omitted at repack time also meets the loose prune path in the same invocation
  is not measured.** The record separates the levers by step and by location, not by internal call.
- **`gc.recentObjectsHook`, which overrides the clock for named ids, is r31's claim 4.** No arm here
  uses it, and the held entry's Gate still carries no quote for it; that is a curation item for the
  L1, not a claim of this entry.
- **The two-week default is sourced, not waited out.** Every arm backdates instead of waiting, so the
  window's real passage is untested here.
- **No receipt tool, class or gate moves.** Vocabulary and mechanism only; certification OFF, K5 HELD.

## Lane link

- `corpus/README.md`:679-681 is the F1 frontier line that names the two questions this entry answers
  (whether cruft-pack handling changes the mtime keeper's reach), and `corpus/README.md`:701 is the
  wave-2 correction that the clock is sourced, not measured. The F1 map row and the frontier line are
  the L1's to update in the same commit.
- `PROVINCE.md`:208 (r30 boundary note: the object-prune clock is unmeasured here) and
  `PROVINCE.md`:224 (r31 boundary note: a fourth holder is sourced, not measured) are the boundary
  this entry moves, by one class: the clock is now documented in its cruft-pack form.
- Instrument, record and contract: `tests/fixtures/r32-jj-mtime-clock.sh`,
  `census/round-32/records/jj-mtime-clock-run.txt`, `census/round-32/c3-contract.txt`. The fixture
  builds its repositories under `$TMPDIR` only, backdates with `touch -d '30 days ago'` on the loose
  commit, tree and blob files (tests/fixtures/r32-jj-mtime-clock.sh:222-229), and never runs against a
  lane repository.
- Held rules cited, not restated: `corpus/knowledge/jj-dropped-keep-object-lifetime.md` (roots after a
  dropped keep ref) and `corpus/knowledge/jj-colocation-receipts.md` sections 3 and 4 (receipt roots).

## Gate

opened: 2026-10-26 — the three snapshots named below were fetched live from tag v2.56.0 this run and
opened; each quote is copied from the bytes named on its own line, is 4 to 25 words, and contains no
pipe character. Snapshot paths are this round's capture paths under `census/round-32/sources/`. The
gitformat-pack row is a placeholder id for the L1 to renumber by document.

- S223 gitformat-pack(5) v2.56.0, § cruft packs lines 613-614 — "The cruft packs feature offer an alternative to Git's traditional mechanism of removing unreachable objects." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § cruft packs lines 631-632 — "those unreachable objects are stored as loose objects and stay that way until they are older than the expiration window" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § cruft packs lines 635-636 — "Git must store these unreachable objects loose in order to keep track of their per-object mtimes." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § cruft packs lines 638-640 — "would cause the pack's mtime to get updated, and the objects within it would never leave the expiration window" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § Cruft packs lines 655-656 — "A cruft pack eliminates the need for storing unreachable objects in a loose state by including the per-object mtimes" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § Cruft packs lines 667-668 — "marking any object which is (a) not contained in a kept-pack, and (b) whose mtime is within the grace period" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § Cruft packs lines 674-675 — "Write the pack out, along with a `.mtimes` file that records the per-object timestamps." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § Cruft packs lines 682-683 — "When a repository already has a cruft pack, `git repack --cruft` typically only adds objects to it." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § Cruft packs lines 684-685 — "which allows the generated cruft pack to omit expired objects" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § Cruft packs lines 688-689 — "It is linkgit:git-gc[1] that is typically responsible for removing expired unreachable objects." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § pack-*.mtimes files have the format: lines 351-353 — "The ith value is the modification time (mtime) of the ith object in the corresponding pack by lexicographic (index) order." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S223 gitformat-pack(5) v2.56.0, § pack-*.mtimes files have the format: lines 353-354 — "The mtimes count standard epoch seconds." — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-pack.adoc — snapshot: census/round-32/sources/gitformat-pack.adoc
- S063 git-gc(1) v2.56.0, § OPTIONS --cruft lines 63-64 — "When expiring unreachable objects, pack them separately into a cruft pack instead of storing them as loose objects." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/git-gc.adoc
- S063 git-gc(1) v2.56.0, § OPTIONS --cruft lines 64-65 — "`--cruft` is on by default." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/git-gc.adoc
- S063 git-gc(1) v2.56.0, § OPTIONS --prune lines 82-83 — "Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable `gc.pruneExpire`)." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/git-gc.adoc
- S063 git-gc(1) v2.56.0, § OPTIONS --prune line 84 — "--prune=now prunes loose objects regardless of their age" — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/git-gc.adoc
- S063 git-gc(1) v2.56.0, § OPTIONS --no-prune line 90 — "Do not prune any loose objects." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/git-gc.adoc
- S063 git-gc(1) v2.56.0, § NOTES lines 160-161 — "Any object with modification time newer than the `--prune` date is kept, along with everything reachable from it." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/git-gc.adoc
- S002 git-gc(1) § CONFIGURATION gc.cruftPacks lines 86-88 — "Store unreachable objects in a cruft pack (see linkgit:git-repack[1]) instead of as loose objects. The default is `true`." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/gc.adoc
- S002 git-gc(1) § CONFIGURATION gc.pruneExpire line 97 — "When 'git gc' is run, it will call 'prune --expire 2.weeks.ago'" — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/gc.adoc
- S002 git-gc(1) § CONFIGURATION gc.pruneExpire lines 98-99 — "(and 'repack --cruft --cruft-expiration 2.weeks.ago' if using cruft packs via `gc.cruftPacks` or `--cruft`)." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/gc.adoc
- S002 git-gc(1) § CONFIGURATION gc.pruneExpire lines 100-102 — "may be used to disable this grace period and always prune unreachable objects immediately" — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/gc.adoc
- S002 git-gc(1) § CONFIGURATION gc.pruneExpire line 102 — "may be used to suppress pruning." — https://git-scm.com/docs/git-gc — snapshot: census/round-32/sources/gc.adoc

- ADMIT: `corpus/knowledge/jj-abandoned-object-mtime-clock.md` — reason: it answers the two open items the r31 entry and its frontier line name (the object's own clock, and cruft handling's effect on it) from three tag-verified snapshots plus the round's own record, and leaves the keeper rule and the receipt-root rule untouched.
- REJECT: reading presence in a cruft pack as proof that an object is reachable — reason: the pack holds unreachable objects whose only claim to life is a per-object mtime inside the grace date, so presence there witnesses age, not reachability.
- REJECT: reading `Do not prune any loose objects` as scoping `git gc --prune=never` away from the cruft call — reason: the record's mixed arm shows an old object moved into a cruft pack and kept there under that flag, so the flag's reach is not its one-line description and a receipt must record the argv instead.
