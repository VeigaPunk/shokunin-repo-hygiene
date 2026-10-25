source: S120 — https://github.com/git/git/blob/v2.56.0/path.c — line 89-124 (struct common_dir, common_list), line 365-385 (report_linked_checkout_garbage) — tag commit a018953688f1; snapshot census/round-24/sources/git-v2.56.0-path.c
source: S121 — https://github.com/git/git/blob/v2.30.0/path.c — line 101-108 (struct common_dir), line 110-136 (common_list), line 376-396 (report_linked_checkout_garbage) — tag commit 71ca53e8125e; snapshot census/round-24/sources/git-v2.30.0-path.c
source: S122 — https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c — line 41-53 (real_report_garbage), line 116-119 (-v path), line 151-152 (KiB) — snapshot census/round-24/sources/git-v2.56.0-builtin-count-objects.c
source: S123 — https://git-scm.com/docs/git-worktree — § REFS, § DETAILS — git 2.56.0 (page "last updated in 2.56.0"; installed man page git 2.56.0-1); snapshot census/round-24/sources/git-worktree.1.txt
source: S115 — https://git-scm.com/docs/git-count-objects — § OPTIONS -v/--verbose — git 2.56.0
verified-at: 2026-10-25 — host git 2.56.0-1; path.c read at tags v2.56.0 and v2.30.0 and builtin/count-objects.c at v2.56.0 (snapshot bytes equal a live re-fetch); git-worktree opened live and as the installed man page; the linked-worktree triggers re-run on 2.56.0 under /var/tmp
recheck: on-release — after a host git upgrade, re-read `common_list` and `report_linked_checkout_garbage` in path.c at the new tag (S120) and re-run `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` (cases 3 `garbage` and 4 `linked`); 365d — re-fetch S121 and S123 for URL liveness
ground: F2 — repository size census (why `count-objects -v` read inside a linked worktree reports garbage for a healthy tree, and how the census reads past it)

# A linked worktree's `garbage` comes from git's reader table, not debris — read the common dir

## Claim (F2: repository size census)

`git count-objects -v` run inside a linked worktree counts parts of that
worktree's **private gitdir** as garbage. The figure depends on where it is read
from, not on the repository's health. There is more than one trigger. The census
reads past all of them by counting against the **common** git dir.

1. **The reading git's table decides.** Under `-v`, count-objects installs its
   garbage reporter and calls `report_linked_checkout_garbage()` (S122 line
   116-119). That function returns at once unless the repository has a separate
   common dir (S120 line 371). Otherwise it walks `common_list` under the
   worktree's own gitdir, skips entries flagged `ignore_garbage`, and reports
   every other listed path that exists (S120 line 375-382). The flag's comment
   reads "Not considered garbage for report_linked_checkout_garbage" (S120 line
   90). The table belongs to the git doing the reading: what is counted is decided
   by the reader. What exists to be counted depends on the writer — a worktree
   created by git 2.30.0 has no private `refs` and reads 0 even under the 2.56.0
   reader, while one created by 2.56.0 reads 1 under both [lane seat run, git
   2.30.0 built in scratch: `.ufo/waves/round-24/w2/W2EntryClaims.md`].
2. **`refs` is unflagged at both tags read.** The entry is `{ 0, 1, 1, "refs" },`
   at v2.56.0 (S120 line 111) and at v2.30.0 (S121 line 123). `logs`,
   `logs/HEAD` and `gc.pid` carry `ignore_garbage = 1` (S120 line 104, 105,
   120).
3. **On git 2.56.0 every way of creating a linked worktree leaves `refs`, so every one reads 1.**
   Inside a linked worktree, `$GIT_DIR` is the private sub-directory, and
   `refs/bisect`, `refs/worktree` and `refs/rewritten` are not shared (S123
   § DETAILS, § REFS). On git 2.56.0 the five creation modes (`--detach`, `-b`,
   `--orphan -b`, and detach or `-b` followed by a commit) each leave a `refs`
   directory there and read `garbage: 1`, while the main worktree reads 0.
   Removing the empty `refs` drops the linked read to 0.
   [lane-measured: `.ufo/waves/round-24/w1/ProbeLinkedModes.md`; committed
   witness: `tests/fixtures/r24-size-census.py` case 4 `linked`
   — receipt census/round-24/records/c1-after.tsv]
4. **There is not one trigger.** Both tags leave `ignore_garbage = 0` on
   `logs/refs/bisect`, `logs/refs/rewritten`, `logs/refs/worktree` (S120 line
   106-108; S121 line 118-120) and on `refs/bisect`, `refs/rewritten`,
   `refs/worktree` (S120 line 112-114; S121 line 124-126). Each one counts once
   it exists in the private gitdir. On git 2.56.0:
   - once `bisect bad` has written `refs/bisect`, the read is `garbage: 2`
     (`refs`, `refs/bisect`); `bisect start` alone still reads 1. The count
     follows the directory, not the bisect: it stays 2 after `bisect reset`,
     after the `refs/worktree` ref is deleted, and after `rebase -r --abort`,
     because the emptied directory remains [W2EntryClaims];
   - a `refs/worktree/*` ref reads `garbage: 2`;
   - the same ref with a reflog reads `garbage: 3` (adds `logs/refs/worktree`).

   These two readings hold for the `files` ref backend. With `reftable`, a
   `refs/worktree/*` ref is stored under `worktrees/<id>/reftable/` and the
   linked read stays `garbage: 1` [lane seat run: `.ufo/waves/round-24/w2/W2SrcCountWt.md`].
   The `refs` trigger and the common-dir rule hold on both backends.

   [lane seat runs: `.ufo/waves/round-24/w1/ScoutPkgEntries.md` E4, re-run by
   ScribeEntry] The table also leaves `info` and `info/sparse-checkout`
   unflagged (S120 line 102-103), so a linked worktree holding them counts them
   too. [observed by ScribeEntry, uncommitted: `git sparse-checkout set` in a
   linked worktree reads `garbage: 3`]
5. **Real object-directory debris is counted from any worktree.** `garbage`
   counts files that are neither valid loose objects nor valid packs (S115
   § OPTIONS -v/--verbose). On a **main** worktree on 2.56.0, each planted
   kinds each read `garbage` ≥ 1:
   - junk in `objects/pack/`;
   - an invalid name in `objects/<2hex>/`;
   - a `tmp_obj_*` file;
   - a directory with an object name;
   - seven orphan pack sidecars (`.keep`, `.promisor`, `.bitmap`, `.rev`,
     `.mtimes`, `.idx`, `.pack`).

   A stray file or directory placed directly in `objects/` reads 0. So the
   linked-worktree sweep is not the only source of a non-zero figure.
   [lane-measured: `.ufo/waves/round-24/w1/ProbeGarbageKinds.md`; committed
   witness: `tests/fixtures/r24-size-census.py` case 3 `garbage`
   — receipt census/round-24/records/c1-after.tsv]
6. **`size-garbage` is floor(sum of bytes / 1024).** Every reported path is
   `stat`ed and its `st_size` added, directories included (S122 line 50). The
   sum is printed as `size_garbage / 1024` in KiB, unless `-H` is given (S122
   line 151-152). Measured: 1023 B reads 0, 1024 B reads 1, 10239 B reads 9, and
   two 600 B files read 1. [lane-measured: ProbeGarbageKinds] A 0 therefore
   means "less than 1 KiB in total", not "the counted entries are directories".
   An empty directory adds 0 on btrfs, but a non-empty counted directory has a
   size there (12, 96 and 2520 bytes measured), and 60 `refs/worktree` refs
   gave a raw linked `size-garbage: 2` with no debris at all [W2EntryClaims].
7. **The census rule.** Run `count-objects -v` against the resolved common git
   dir, for example `git --git-dir=<common> count-objects -v`. There
   `different_commondir` is false, the private-gitdir sweep never runs (S120
   line 371), and a linked-worktree path reports the common-dir figure. This is
   what `tools/souji-size-census.py` does (C1, r24). The rule is exact for every
   trigger in items 3–4 and keeps item 5's real debris counted. Subtracting 1 per
   linked worktree is not exact, because a bisecting or `refs/worktree` linked
   worktree contributes 2 or 3. Precondition: `GIT_COMMON_DIR` must be unset.
   At v2.56.0 `repository.c` lines 160-161 force the separate-common-dir flag
   whenever that variable is set, and a healthy repository read with
   `GIT_COMMON_DIR=<common> git --git-dir=<common> count-objects -v` reported
   `garbage: 6` [lane seat run: `.ufo/waves/round-24/w2/W2SrcPath.md`, r24
   correction]. The census tool builds an allowlisted environment, so the
   variable never reaches it.

## What this does NOT establish

- **No fleet figure.** Nothing outside this lane was read. No `count-objects`
  figure is claimed for any fleet repository or worktree. The only lane-bound
  figure is C1's `census/round-24/size-census-lane.txt`, which is about this
  repository alone.
- **Two tags read, one git run.** The table was read at v2.56.0 and v2.30.0
  only. Tags in between and git newer than 2.56.0 are not covered. Only 2.56.0
  was executed.
- **The triggers are not enumerated.** Items 3–4 name the writers observed:
  `worktree add` (`refs`), bisect marks (`refs/bisect`), `refs/worktree/*` refs
  with or without a reflog, and `sparse-checkout set` (`info`). No source audit
  established which other commands write unflagged `common_list` names into a
  private gitdir. `refs/rewritten` (rebase) was read in the table but not run.
- **`garbage: 0` is not a clean certificate.** A file with an uppercase-hex
  38-character name is counted as a loose object, not as garbage.
  [lane-measured: ProbeGarbageKinds cell `up`] An alternate's loose
  directories are not walked by code. [INFERENCE: ScoutCountObjectsC Finding 5,
  not probed]
- **One read is meaningful only on a quiescent repository.** A `tmp_obj_*` file
  left by a concurrent object write is counted (item 5).
- **Directory size off btrfs is not measured.** Item 6's code adds every
  counted directory's `st_size`; other filesystems were not run.
- **A non-zero figure can be another repository's debris.** An alternate's
  loose junk is not counted, but junk in its pack directory is counted from the
  repository that borrows it (`garbage: 1`, `size-garbage: 2` measured), and the
  census tool reports it as this repository's `garbage` [W2EntryClaims]. The
  tool also exits 1 when an alternate holds loose junk, because `fsck` reports
  it on stderr.
- **No cleanup advice.** A counted private `refs`, `refs/bisect` or `info` is
  structure. Nothing here proposes removing it.

## Lane link and consequence

This entry is the knowledge side of C1 (r24). It explains why
`tools/souji-size-census.py` reads the common dir, and why frozen case 4 expects
the raw linked read to be 1 while the tool reports 0. It extends
`corpus/knowledge/repo-size-census-readonly.md` (S115–S117), which defined
`garbage` as a file count but did not say where to read it. It must be listed in
the F2 row of the `corpus/README.md` coverage map.

## Gate

url: https://github.com/git/git/blob/v2.56.0/path.c
snapshot: census/round-24/sources/git-v2.56.0-path.c
opened: 2026-10-25

- ADMIT: "Not considered garbage for report_linked_checkout_garbage" — path.c@v2.56.0 line 90 (same bytes path.c@v2.30.0 line 102) — reason: names the flag that decides what a linked worktree's sweep counts — snapshot: census/round-24/sources/git-v2.56.0-path.c
- ADMIT: "{ 0, 1, 1, "refs" }," — path.c@v2.56.0 line 111 and path.c@v2.30.0 line 123 — reason: refs is unflagged at both tags, so the reading git counts it whenever it exists — snapshot: census/round-24/sources/git-v2.30.0-path.c
- ADMIT: "{ 0, 1, 0, "refs/bisect" }," — path.c@v2.56.0 line 112 — reason: another unflagged per-worktree path; once bisect bad writes refs/bisect the linked read is garbage 2 — snapshot: census/round-24/sources/git-v2.56.0-path.c
- ADMIT: "{ 0, 1, 0, "refs/worktree" }," — path.c@v2.56.0 line 114 — reason: a refs/worktree ref reads garbage 2, and 3 with its reflog (logs/refs/worktree, line 108) — snapshot: census/round-24/sources/git-v2.56.0-path.c
- ADMIT: "report_linked_checkout_garbage(the_repository);" — builtin/count-objects.c@v2.56.0 line 118 — reason: the sweep runs only on the -v path the census uses — snapshot: census/round-24/sources/git-v2.56.0-builtin-count-objects.c
- ADMIT: "(unsigned long)(size_garbage / 1024));" — builtin/count-objects.c@v2.56.0 line 152 — reason: size-garbage is the floored KiB of summed bytes, not a directory signal — snapshot: census/round-24/sources/git-v2.56.0-builtin-count-objects.c
- ADMIT: "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared." — § REFS — reason: these namespaces live in the private gitdir, which is why each one is countable there — snapshot: census/round-24/sources/git-worktree.1.txt
- ADMIT: "Within a linked worktree, $GIT_DIR is set to point to this private directory" — § DETAILS — reason: the swept directory is documented per-worktree structure, not debris — snapshot: census/round-24/sources/git-worktree.1.txt
- ADMIT: "garbage: the number of files in the object database that are neither valid loose objects nor valid packs" — § OPTIONS -v/--verbose — reason: object-directory debris is counted from any worktree, so the census must keep it while discounting the sweep — snapshot: census/round-24/sources/git-count-objects.1.txt
- ADMIT: staged garbage-false-positive-modes-r27, re-sourced to S120/S121/S122/S123 (path.c@v2.56.0 line 111, path.c@v2.30.0 line 123) — reason: its reader-decides reading and the refs row at both tags verify byte-exact in the committed snapshots; its nothing-but-the-linked-worktree-path bullet and its shokuknow-only S153 row are dropped, and the refs/* and logs/refs/* triggers it omitted are added — flip: reject if a later tag flags refs with ignore_garbage
- ADMIT: staged garbage-false-positive-modes-r25, five-mode matrix only (staged file line 12-30) — reason: one creation spelling is committed as a fixture witness (C1 case 4 runs `git worktree add <path>`, the implicit new-branch form, and reads garbage 1); the five named modes are seat-observed, not fixture-committed (ProbeLinkedModes report, committed after 778747e; re-run by W2Rejects) — flip: reject if C1 case 4 fails at a later tip or a later git stops creating the private refs; a committed five-mode probe with a receipt would upgrade this from seat-observed
- REJECT: staged garbage-false-positive-modes-r25 headline (no second trigger mode) and its directory-size reason, staged file line 12-30 and line 48-49 — reason: path.c@v2.56.0 lines 106-108 and 112-114 leave refs/* and logs/refs/* unflagged, an active bisect or a refs/worktree ref reads garbage 2, and size-garbage is floor(sum/1024) — flip: none for the headline at v2.56.0; re-open only if a later tag flags those rows
- REJECT: staged garbage-false-positive-modes-r26 — reason: its central claim (staged file line 16 and line 24: nothing but the linked-worktree path counts) is falsified on a main worktree by the committed C1 case 3 main arm (pack junk reads garbage 1, receipt census/round-24/records/c1-after.tsv) and by 12 seat-observed ProbeGarbageKinds cells; its arm 1 read the live fleet repo; its only evidence (S147) lives in shokuknow; and its fsck pointer names lane S113, which is g_file_trash — flip: admit a restated claim scoped to: a stray file or directory placed directly in objects/ is not counted, re-measured by a lane-committed /var/tmp fixture with no fleet arm and citing lane S115/S116
- REJECT: staged count-objects-garbage-semantics-r23 (staged file line 1-79) — reason: its title, census claim and lane link are fleet claims; S131 is a fleet census whose payload lives only in shokuknow (its slice verdict is accepted, so this is not a fabrication reason); its S112 and S113 collide with lane ids for gio(1) and g_file_trash; the only two fields not object-graph state claim is contradicted by the alternate field; and its directory-size reason is wrong — flip: split it, re-citing the linked-worktree observation to a lane fixture and the field reading to lane S115/S116 with alternate acknowledged, deleting the fleet census, and moving the vendor reclamation material to its own entry under fresh non-colliding ids
- REJECT: the staged provenance cells as-is (S130 S131 S134 S141 S147 S153, 2026-10-23 dates) — reason: they are own-work rows whose evidence lives in shokuknow; none of these ids exists in the lane registry, and the lane's own S120-S123 name other documents than staged S120-S123 — flip: re-point by document to S120–S123 after the lane mints them, with this round's access date
