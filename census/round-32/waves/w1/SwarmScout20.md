# SwarmScout20 — git v2.56.0 cruft-pack mtime clock (F1), source read + spot measurement

## Status

STATUS: PASS — all five questions answered from v2.56.0 source with file:line and quotes; every quote below was copied from bytes opened this run; six behaviours were also exercised on host git 2.56.0 in a scratch repo (scratch removed). Not inspected: the C3 entry/fixture/record themselves (not yet delivered at read time), so the "NEW" list below is vs. the two held entries, not vs. the C3 draft.

## Evidence

Bytes: raw files fetched from `https://raw.githubusercontent.com/git/git/v2.56.0/<path>` into `/fast/scratch/hyaku/souji-r32/SwarmScout20/` (sha256, full):

| path | sha256 |
|---|---|
| builtin/gc.c | 17a03f6f413a82f9a532596b0b3bf5c43119c1d9e8209149dff8d5f69e41e21d |
| builtin/repack.c | fe71f22630652ba9fd4836f34a8d6e6c22b9ea5f5e396293dba1514ecf67ce64 |
| builtin/pack-objects.c | c5911d601c5fa75e85a05adb63b9d824f26eb2ba69aae22a4e02bc1552ce3167 |
| reachable.c | 1608989c9753b5e2a8f9160ea06258ffaa9c9feb187608dc43153de68a344be4 |
| builtin/prune.c | 5d141d0cdceb3766f82b557f3b1c8af783fab804acd92461bc0f547b0e05daf9 |
| odb/source-files.c | a5df6ee4eaa6ea7cee78d8c29ff36b73ddd028dd38ba7dfcba2f2342d0c657ab |
| odb/source-packed.c | bfb57f4c3f4ff9428273106afa03296344b777db5b0de3390514db7d987cec4a |
| odb/source-loose.c | 361d08ae0400a2d5b939cca3c52b5efda2ea14b3dd4d8545e11b9edab287ac38 |
| packfile.c | 021b1b9b25551070a3a1f986d1972ef93ef9695c3ff4f60eeb0a9a0798b94032 |
| repack-cruft.c | d88bca0d0a1bc3baec8f438c9bd7bac358c4f89d79ee1a9b8f820aa01f82d7e1 |
| repack.c | 080f25c40915577bfcf4aefb28984d95de48cd1b2429fa0a9c0c1b0a2e72d506 |
| pack-write.c | 4ee471db6c0372dc3bc209ef6d2d030caaf9bf221b3db631ee618e8bcb775c79 |
| date.c | ee1f260f43aab1c6c79b7688d408eafc511fd1086764cc320771dd8f2972858e |
| Documentation/git-gc.adoc | e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c (= r30 capture hash) |
| Documentation/config/gc.adoc | 0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a (= r31 capture hash) |
| Documentation/git-repack.adoc | 474d4147f1390401f38e07a7c5950f21d6d402212984e1f7d98dd6c71da460f6 |
| Documentation/git-pack-objects.adoc | f00868369d0fcc5474febcfb6db612074b5df73af500dc2bbd4ae8bd104e6d00 |
| Documentation/gitformat-pack.adoc | ec285ba4f4e15a68ad83a570eaf74e8549b477496e49933126ef935d9291381b |

Layout fact that matters for anchors: in v2.56.0 `git gc` no longer builds the repack argv in `builtin/gc.c`; it calls `odb_optimize` (builtin/gc.c:563, `maintenance_task_odb`), and the argv is built in `odb/source-files.c`. `builtin/repack.c` is a driver; the cruft-pack writer is `repack-cruft.c`; `.mtimes` writing is `pack-write.c`. A C3 entry that anchors to `builtin/gc.c`/`builtin/repack.c` for those steps would point at the wrong file.

Measurement (host `git version 2.56.0`, scratch repo, `GIT_TRACE=1`, objects backdated with `touch -d`, `.mtimes` parsed with a 10-line script reading `git show-index` order + the be32 table; scratch deleted):

- default `git gc` argv (trace): `git repack -d -l --cruft --cruft-expiration=2.weeks.ago`, then inner `git pack-objects ... --cruft --cruft-expiration=2.weeks.ago --non-empty`, then `git prune --expire 2.weeks.ago`. 30-day-old loose blob absent after; fresh loose blob present.
- fresh loose blob -> `.mtimes` age 0.00 days, magic `MTME`, version 1, hash id 1; cruft `.pack` mtime age 0.000.
- loose blob backdated 20 days, then `git -c gc.pruneExpire=30.days.ago gc`: `.mtimes` records 20.00 days for it and 0.00 for the fresh one while the cruft pack file itself is 0.000 days old. A following default `git gc` removes the 20-day object (`X absent`), fresh one stays.

## Findings

1. **Per-object mtime recorded in a cruft pack** — the value depends on where the object was found; the pack file's own mtime is used only for objects that sat in a non-cruft pack.
   - Loose object: its file mtime. `odb/source-loose.c:114` `*oi->mtimep = st.st_mtime;` (also `:155`); the no-expiry path stats directly, `builtin/pack-objects.c:4560-4561` `add_cruft_object_entry(oid, type, NULL, 0, NULL, st.st_mtime);`. Measured: loose blob backdated 20 days is recorded at 20.00 days in `.mtimes`.
   - Object already in a cruft pack: that pack's `.mtimes` entry. `packfile.c:1375` `*oi->mtimep = nth_packed_mtime(p, index_pos);`.
   - Object in a non-cruft pack: that pack file's mtime. `packfile.c:1377` `*oi->mtimep = p->mtime;`.
   - Older object reachable from a recent one: the expiry value, not its true age. `builtin/pack-objects.c:4212-4214` "it's at least as old as our expiration value. Rather than find it exactly, just use that value." (passed at `:4221`, `cruft_expiration`).
   - Merge rule when an object is seen twice: the larger wins, `builtin/pack-objects.c:4204` `if (mtime > oe_cruft_mtime(&to_pack, entry))`.
   - Written to disk as a table: `pack-write.c:323` `hashwrite_be32(f, oe_cruft_mtime(to_pack, e));`; format `Documentation/gitformat-pack.adoc:351-352` "The ith value is the modification time (mtime) of the ith object in the corresponding pack".
   - Why not the pack mtime: `Documentation/gitformat-pack.adoc:635-636` "Git must store these unreachable objects loose in order to keep track of their per-object mtimes." (cruft packs exist to avoid the pack-mtime collapse, `:636-642`).

2. **Default `--cruft-expiration` passed by `git gc`**: `2.weeks.ago`, the same value as the prune date, via `gc.pruneExpire`.
   - Default: `builtin/gc.c:143` `.prune_expire = xstrdup("2.weeks.ago"), \`; cruft on by default `builtin/gc.c:138` `.cruft_packs = 1, \`.
   - Argv: `odb/source-files.c:490-493` `strvec_push(args, "--cruft");` then `strvec_pushf(args, "--cruft-expiration=%s", opts->prune_expire);`.
   - Config override: `builtin/gc.c:176` reads `gc.pruneexpire` into `cfg->prune_expire`; `--prune=<date>` overrides at `builtin/gc.c:631-634`.
   - Documented: `Documentation/config/gc.adoc:97-99` "(and 'repack --cruft --cruft-expiration 2.weeks.ago' if using cruft packs via `gc.cruftPacks` or `--cruft`)".
   - A loose-object `git prune` still runs after the cruft repack: `odb/source-files.c:740` `/* run `git prune` even if using cruft packs */` with `prune --expire <prune_expire>` (`:739-741`). Measured trace confirms `git prune --expire 2.weeks.ago` after the cruft repack.
   - EXCEPTION (not in either held entry): `--prune=now` (or `gc.pruneExpire=now`) does NOT write a cruft pack. `odb/source-files.c:487-489` `if (opts->prune_expire && !strcmp(opts->prune_expire, "now") &&` ... `strvec_push(args, "-a");` (condition also requires `!(opts->cruft_packs && opts->expire_to)`). Measured: trace `git repack -d -l -q -a`, then `git prune --expire now`; the 20-day cruft object and the fresh cruft object both absent, only the reachable pack remains.
   - `gc.pruneExpire=never`: passed verbatim as `--cruft-expiration=never` (measured trace) and `prune --expire never`. `builtin/pack-objects.c:5085` `cruft_expiration = approxidate(arg);` and `date.c:1202-1205` `date_never` sets `time_t n = 0;`, so expiry = 0, and `builtin/pack-objects.c:4370-4373` takes the `else enumerate_cruft_objects();` branch: nothing is eliminated, matching `Documentation/git-pack-objects.adoc:143-144` "If unspecified (and given `--cruft`), then no objects are eliminated." (`never` is the 0 case of the same branch, [INFERENCE] from source, MEASURED outcome below). `git prune --expire never`: expiry parses to 0 (`builtin/prune.c:98` `if (st.st_mtime > expire)` is then always true, keep). Measured: a 30-day-old loose blob went into the cruft pack with `.mtimes` age 30.00 days and stayed present; the 20-day object stayed present.

3. **How an object already in a cruft pack is expired on the next `git gc`** — by rewrite-and-delete, using the per-object mtimes, not by touching or aging the pack.
   - Every existing cruft pack is handed to `pack-objects` as a discard: `repack-cruft.c:89-90` `for_each_string_list_item(item, &existing->cruft_packs)` / `fprintf(in, "-%s.pack\n", item->string);`.
   - With a non-zero expiry, `pack-objects` re-walks all local objects (including those in the discarded cruft pack) and makes an object a traversal tip only if its mtime is newer: `builtin/pack-objects.c:4370-4371` `if (cruft_expiration) enumerate_and_traverse_cruft_objects(&fresh_packs);`, `reachable.c:186` `if (mtime > data->timestamp)` (strictly newer; `reachable.c:183-192` `obj_is_recent`), mtime for packed objects from `packfile.c:1375`/`:1377`. Objects not recent and not reachable from a recent one are not written to the new cruft pack.
   - The old cruft pack is then deleted: `builtin/repack.c:719-722` `if (delete_redundant && pack_everything & ALL_INTO_ONE) {` ... `existing_packs_mark_for_deletion(&existing, &names);` and `repack.c:253-254` marks `&existing->cruft_packs`; removal `builtin/repack.c:751`. So expiry is implicit: the object is dropped because no new pack carries it (`builtin/repack.c:657-659` comment "pruning is implicit").
   - Loose unreachable objects that are still recent are packed into the new cruft pack and the loose copies removed by `prune_packed_objects` (`builtin/repack.c:760`); older loose ones are removed by the following `git prune` (`builtin/prune.c:98`, `:68` `mark_reachable_objects(revs, 1, expire, progress);` keeps recent ones' closure).
   - A rewrite does not refresh an object inside a cruft pack: `odb/source-packed.c:653-654` `if (e.p->is_cruft)` / `return 0;` — freshen refuses, so a re-write of the same content makes a NEW loose copy with a fresh mtime, which then wins the max-merge at `pack-objects.c:4204`. Measured: `git hash-object -w` of a blob already in the cruft pack (recorded 20 days) created a loose copy age 0.0 d; after default `git gc` the `.mtimes` entry for that blob is age 0.00 d and the object is present.
   - `touch` on the cruft `.pack` or `.mtimes` file does not move the clock: measured, after `touch .git/objects/pack/*.pack .git/objects/pack/*.mtimes` the 20-day object is absent after default `git gc`; fresh one present.

4. **`gc.cruftPacks=false`: yes, `git gc` explodes unreachable objects loose, and the loose mtime is the source PACK file's mtime, not the object's own.**
   - Argv: `odb/source-files.c:499-503` `strvec_push(args, "-A");` then `strvec_pushf(args, "--unpack-unreachable=%s", opts->prune_expire);`. Measured trace: `git repack -d -l -q -A --unpack-unreachable=2.weeks.ago`, then `git prune --expire 2.weeks.ago`.
   - Explode: `builtin/pack-objects.c:4694-4695` `if (force_object_loose(the_repository->objects->sources,` / `&oid, &p->mtime))` — the mtime handed to the loose write is `&p->mtime` (pack file), applied with `odb/source-loose.c:821` `.modtime = *mtime,` via `utime` at `:824`. `Documentation/git-repack.adoc:53-55` "any unreachable objects in a previous pack become loose, unpacked objects".
   - Discard rule: `builtin/pack-objects.c:4693` `!loosened_object_can_be_discarded(&oid, p->mtime)` with `:4621-4623` `if (!unpack_unreachable_expiration)` / `return 0;` / `if (mtime > unpack_unreachable_expiration)` — keyed on the PACK mtime too, so a fresh cruft pack's old per-object entries are loosened, not discarded, unless reachable-recent logic (`:4981-4989`, `record_recent_object`) already spared them. Recent-set is computed per object (`add_unseen_recent_objects_to_traversal`, reachable.c:247-284), but "discard" is decided on pack mtime.
   - Measured, same repo state (reachable pack + cruft pack holding blob X recorded at 20 days, cruft pack file 0 d old): default cruft gc -> X absent; `git -c gc.cruftPacks=false gc` -> X present as a LOOSE file of age 0.001 d (clock reset), no cruft pack left. A second `gc.cruftPacks=false` default gc leaves it present (`X present`). With `-c gc.pruneExpire=30.days.ago` the same explosion also gave age 0.0 d for both X (20-day) and the fresh blob.
   - Doc: `Documentation/config/gc.adoc:85-88` "Store unreachable objects in a cruft pack ... instead of as loose objects. The default is `true`." says nothing about the explode mtime.

5. **Is `touch` on a loose object the documented input to that clock? No — the documented input is "operations that add an object ... update the modification time"; `touch(1)` is not named.**
   - Documented: `Documentation/git-gc.adoc:160` "Any object with modification time newer than the `--prune` date is kept," and `:163-164` "Most operations that add an object to the database update the modification time of the object if it is already present".
   - Code that does the update: `object-file.c:71-82` `freshen_file` calls `utime`; `odb/source-files.c:196-205` freshen tries packed then loose; packed freshen touches the whole `.pack` (`odb/source-packed.c:657` `if (utime(e.p->pack_name, timesp))`) and is skipped for cruft packs (`:653-654`).
   - Sweep: grepped `touch` over the seven doc files fetched (git-gc, config/gc, git-repack, config/repack, git-prune, git-pack-objects, gitformat-pack): only hit is unrelated `git-repack.adoc:321,326` ("only touched"). No man page in that set tells a user to `touch` an object file. `git prune` and the `-A`/cruft readers only read the loose file's `st_mtime` (`builtin/prune.c:98`, `odb/source-loose.c:114`), so a `touch` on the loose file is an effective but undocumented input. Measured: a loose blob backdated 30 days then `touch`ed (-> now) survived default `git gc` and landed in the cruft pack with `.mtimes` age 0.00 d; the same blob left at 30 days is dropped.
   - Also: `gc.recentObjectsHook` is the documented way to force "recent" regardless of age (`Documentation/config/gc.adoc:144-147` "By treating their mtimes as "now", any objects (and their descendants) mentioned in the output will be kept"); wired at `reachable.c:172` and consulted at `reachable.c:189-191` only when the object's own mtime is not newer.

## What the held entries already hold (sourced, not measured) vs C3 NEW

Held, `corpus/knowledge/jj-dropped-keep-object-lifetime.md`:
- claim 4 (lines 44-51): any object newer than `--prune` date kept with everything reachable (git-gc.adoc:160-161), two-week default via `gc.pruneExpire`, `now` disables, `gc.recentObjectsHook` (gc.adoc:96-105, 140-147).
- claim 6 + r31 correction (lines 60-69, 233-234): `git prune` loose only (git-prune.adoc line 30); `git gc` also runs `repack --cruft --cruft-expiration 2.weeks.ago` (gc.adoc:97-99). Both sourced from docs, not from code.
- qualification (line 238): the mtime keeper is "isolated in no arm", "sourced rather than measured".
- the 90/30-day reflog windows; `jj util gc` shell-out `--prune=@{} +0000`.
Held, `corpus/knowledge/git-grace-periods-and-expire-to.md`:
- `gc.pruneExpire` default `2.weeks.ago` (man pages of git 2.55.0, not 2.56.0; line 37 flags it unverified on 2.56.0), `--prune=now` risk, `--expire-to` with `--cruft -d`; r12 plain-git deletion under `--prune=now`.
- It carries NO statement about per-object cruft mtimes, `.mtimes`, explode, or touch.

NEW ground C3 can add (each is a located source fact plus a measurement from this scout; C3 must reproduce it in its own fixture and record to claim it as measured):
1. Per-object clock is carried inside the cruft pack (`.mtimes`), and the pack file's own mtime is not the clock: pack-objects.c:4204, packfile.c:1375/1377, pack-write.c:323; measured 20.00 d entry in a 0.000 d pack, dropped by the next default gc.
2. The 2.56.0 argv is built in `odb/source-files.c:487-503`, not `builtin/gc.c`; default `--cruft --cruft-expiration=2.weeks.ago` plus a separate `git prune --expire` (source-files.c:736-741) — measured by trace.
3. `--prune=now`/`gc.pruneExpire=now` takes the `-a` branch (source-files.c:487-489): no cruft pack, existing cruft pack deleted, objects absent — the "total form" of claim 6 is not a cruft expiry at all.
4. `gc.pruneExpire=never` preserves each object's own mtime in the cruft pack (the expiry==0 branch, pack-objects.c:4370-4373) — measured 30.00 d entry kept present.
5. `gc.cruftPacks=false` explodes with the PACK mtime (pack-objects.c:4695, source-loose.c:821), resetting the object's age to the cruft pack's age and resurrecting an object that default cruft gc would drop — measured X absent (cruft) vs present loose age 0.001 d (cruftPacks=false) from identical states.
6. A rewrite of an object inside a cruft pack does not freshen it (source-packed.c:653-654) — it creates a new loose copy (measured age 0.0 d, `.mtimes` then 0.00 d). `touch` of the cruft `.pack`/`.mtimes` does not extend an object's life (measured).
7. `touch` on a loose object file works as a keeper and lands in the cruft pack with the new mtime (measured) but is undocumented: the documented input is object re-write freshening (git-gc.adoc:163-164) and the hook; no doc fetched names `touch`.
8. "Older object reachable from a recent one gets the expiry value as its recorded mtime" (pack-objects.c:4212-4221) — a source-only fact, not measured here; if C3 does not run an `old`-under-`recent`-parent arm, it stays [INFERENCE]/sourced. This is the one C3 contract arm that touches it is `mixed`.

Contract mapping notes for the C3 counter (`c3-contract.txt` arms/steps/where): `arm=nocruft` is finding 4, `step=gc-pruneexpire-never` and `gc-prune-never` are finding 2's never branch (note `--prune=never` on the CLI is accepted by `parse_expiry_date`, `builtin/gc.c:635-636`), `where=pack` (non-cruft reachable pack) vs `where=cruft` (`.mtimes` present) matter for finding 1, and `now` is outside the frozen step set (it is a different, non-cruft path).

## Attack log

None (research item). Possible gameability noted for the L1 only as a design caution, not a counter attack: any C3 `where=cruft` check that tests only "object present in a pack" cannot tell a cruft pack from a reachable pack; the presence of `pack-*.mtimes` is the discriminator (`Documentation/git-pack-objects.adoc:120-121` "denoted by the existence of a `.mtimes` file").

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/SwarmScout20.md` (this report). No lane file other than this report was written; scratch `/fast/scratch/hyaku/souji-r32/SwarmScout20/` removed. No tools installed.
