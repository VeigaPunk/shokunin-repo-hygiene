# ScribeEntry — assimilated F2 entry draft (souji r24 w1)

Seat: L1Souji24.ScribeEntry (scribe, leaf, read-only on the lane). Lane rev read: `f9db2181647d91470a724a12d626bd6106805076`, plus the uncommitted `census/round-24/sources/` and `tools/souji-size-census.py` present at 06:25.
Proposed lane path: `corpus/knowledge/count-objects-linked-worktree-garbage.md`. Access date for every source: 2026-10-25.
Revision 2 applies the L1 decisions sent over IRC at 09:25 UTC: ids S120–S123, the `census/round-24/sources/` snapshot names, `line N` locators for `.c` files, and the ADMIT r27 / ADMIT r25 matrix / REJECT r26 / REJECT r23 dispositions.
Scratch: `/var/tmp/souji-r24-ScribeEntry/` and `/var/tmp/souji-r24-ScribeEntry2/` (both removed). Tools installed or upgraded: none.

## Status

STATUS: PARTIAL. The entry below follows every L1 decision. The lane's Q54 locator checker passes it against the committed snapshot dir: `entries=1 locators=3 locators_bad=0` (Finding 6). One gap keeps it short of PASS: `tests/fixtures/r24-size-census.py`, which the entry names as the committed witness of the five-mode matrix (case 4) and of debris counting (case 3), does not exist yet. It is marked `[PENDING C1 landing]`. The recheck has the same dependency.

## Evidence

Each command below ran on host `git version 2.56.0`, with `LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null HOME=<scratch>`, in `/var/tmp` scratch.

| what | command | result |
|---|---|---|
| snapshot digests | `sha256sum census/round-24/sources/*` | `git-v2.56.0-path.c f98ba344…d21d2`, `git-v2.30.0-path.c 7c5b0710…a62d4a`, `git-v2.56.0-builtin-count-objects.c ec13ae40…64e03e`. These equal this seat's own `curl` of `raw.githubusercontent.com/git/git/<tag>/…`, made independently in revision 1. `git-worktree.1.txt 624821a6…`, `gitrepository-layout.5.txt 41439c3f…` |
| tag commits | `git ls-remote https://github.com/git/git.git 'refs/tags/v2.56.0^{}' 'refs/tags/v2.30.0^{}'` | `a018953688f1b10bddf91bff8747068f5f4746a4`, `71ca53e8125e36efbda17293c50027d31681a41f` |
| table lines | `grep -n` on the two path.c snapshots | v2.56.0: `"info"` 102, `"info/sparse-checkout"` 103, `"logs"` 104, `"logs/HEAD"` 105, `"logs/refs/{bisect,rewritten,worktree}"` 106-108, `"refs"` 111, `"refs/{bisect,rewritten,worktree}"` 112-114, `"gc.pid"` 120; comment 90; function 365-385; `different_commondir` 371. v2.30.0: comment 102, `logs/refs/*` 118-120, `"refs"` 123, `refs/*` 124-126. All `refs/*` and `logs/refs/*` rows are `{ 0, 1, 0, … }` at both tags |
| count-objects lines | `sed -n` on the count-objects snapshot | `size_garbage += st.st_size;` 50, `report_linked_checkout_garbage(the_repository);` 118, `(unsigned long)(size_garbage / 1024));` 152 |
| snapshot headings | Q54 `SHORT_CAPS` rule applied to both `.txt` snapshots | git-worktree: NAME SYNOPSIS DESCRIPTION COMMANDS OPTIONS REFS `CONFIGURATION FILE` DETAILS `LIST OUTPUT FORMAT` EXAMPLES CONFIGURATION BUGS GIT. gitrepository-layout: NAME SYNOPSIS DESCRIPTION HEAD `GIT REPOSITORY FORMAT VERSIONS` `SEE ALSO` GIT NOTES. There is no `refs` heading, so no `§` locator points into gitrepository-layout |
| quote membership | whitespace-normalised substring test against `git-worktree.1.txt` | the three git-worktree quotes in the Gate: True / True / True |
| trigger probe (this seat, rerun of ScoutPkgEntries E4) | repo with 3 commits and linked worktrees a, b, c; `git -C <wt> count-objects -v` | plain: `garbage: 1` (`…/refs`). `bisect start` alone: 1. After `bisect bad HEAD` + `bisect good HEAD~2`: **2** (`…/refs`, `…/refs/bisect`); main: 0. `update-ref refs/worktree/x HEAD`: **2** (`…/refs`, `…/refs/worktree`). `update-ref --create-reflog refs/worktree/y HEAD`: **3** (`…/logs/refs/worktree`, `…/refs`, `…/refs/worktree`). `--git-dir=<common>`: 0 |
| sparse probe (revision 1) | `git -C <wt> sparse-checkout set d` | linked **3** (`…/info`, `…/info/sparse-checkout`, `…/refs`); main 0 |
| lane files | `ls tools/souji-size-census.py tests/fixtures/r24-size-census.py` | tool present (8009 B, 06:25); fixture **absent** |

Inputs read:
- staged (READ-ONLY): `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/{garbage-false-positive-modes-r25,-r26,-r27,count-objects-garbage-semantics-r23,-r24}.md`;
- lane: `corpus/knowledge/repo-size-census-readonly.md` (shape), `corpus/QUALITY.md` Q1/Q2/Q54, `corpus/SOURCES.md` (last row S119), `tests/fixtures/r23-locator-heading.py`;
- seat reports: `.ufo/waves/round-24/w1/{ScoutPkgEntries,ProbeGarbageKinds,ProbeLinkedModes,ScoutPathC,ScoutCountObjectsC,ScoutWorktreeDoc}.md`.

## Draft entry (proposed `corpus/knowledge/count-objects-linked-worktree-garbage.md`)

Each id below is named by its document, so the L1 re-points by document:
- S120 = https://github.com/git/git/blob/v2.56.0/path.c
- S121 = https://github.com/git/git/blob/v2.30.0/path.c
- S122 = https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c
- S123 = https://git-scm.com/docs/git-worktree
- S115 is the existing lane row for https://git-scm.com/docs/git-count-objects.

~~~markdown
source: S120 — https://github.com/git/git/blob/v2.56.0/path.c — line 89-124 (struct common_dir, common_list), line 365-385 (report_linked_checkout_garbage) — tag commit a018953688f1; snapshot census/round-24/sources/git-v2.56.0-path.c
source: S121 — https://github.com/git/git/blob/v2.30.0/path.c — line 101-136 (common_list), line 376-396 (report_linked_checkout_garbage) — tag commit 71ca53e8125e; snapshot census/round-24/sources/git-v2.30.0-path.c
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
   90). The table belongs to the git doing the reading, so the git that created
   the worktree does not change the count.
2. **`refs` is unflagged at both tags read.** The entry is `{ 0, 1, 1, "refs" },`
   at v2.56.0 (S120 line 111) and at v2.30.0 (S121 line 123). `logs`,
   `logs/HEAD` and `gc.pid` carry `ignore_garbage = 1` (S120 line 104, 105,
   120).
3. **Every way of creating a linked worktree leaves `refs`, so every one reads 1.**
   Inside a linked worktree, `$GIT_DIR` is the private sub-directory, and
   `refs/bisect`, `refs/worktree` and `refs/rewritten` are not shared (S123
   § DETAILS, § REFS). On git 2.56.0 the five creation modes (`--detach`, `-b`,
   `--orphan -b`, and detach or `-b` followed by a commit) each leave a `refs`
   directory there and read `garbage: 1`, while the main worktree reads 0.
   Removing the empty `refs` drops the linked read to 0.
   [lane-measured: `.ufo/waves/round-24/w1/ProbeLinkedModes.md`; committed
   witness: `tests/fixtures/r24-size-census.py` case 4 `linked`
   — PENDING C1 landing]
4. **There is not one trigger.** Both tags leave `ignore_garbage = 0` on
   `logs/refs/bisect`, `logs/refs/rewritten`, `logs/refs/worktree` (S120 line
   106-108; S121 line 118-120) and on `refs/bisect`, `refs/rewritten`,
   `refs/worktree` (S120 line 112-114; S121 line 124-126). Each one counts once
   it exists in the private gitdir. On git 2.56.0:
   - an active bisect with a bad and a good commit marked reads `garbage: 2`
     (`refs`, `refs/bisect`); `bisect start` alone still reads 1;
   - a `refs/worktree/*` ref reads `garbage: 2`;
   - the same ref with a reflog reads `garbage: 3` (adds `logs/refs/worktree`).

   [lane seat runs: `.ufo/waves/round-24/w1/ScoutPkgEntries.md` E4, re-run by
   ScribeEntry] The table also leaves `info` and `info/sparse-checkout`
   unflagged (S120 line 102-103), so a linked worktree holding them counts them
   too. [observed by ScribeEntry, uncommitted: `git sparse-checkout set` in a
   linked worktree reads `garbage: 3`]
5. **Real object-directory debris is counted from any worktree.** `garbage`
   counts files that are neither valid loose objects nor valid packs (S115
   § OPTIONS -v/--verbose). On a **main** worktree on 2.56.0, twelve planted
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
   — PENDING C1 landing]
6. **`size-garbage` is floor(sum of bytes / 1024).** Every reported path is
   `stat`ed and its `st_size` added, directories included (S122 line 50). The
   sum is printed as `size_garbage / 1024` in KiB, unless `-H` is given (S122
   line 151-152). Measured: 1023 B reads 0, 1024 B reads 1, 10239 B reads 9, and
   two 600 B files read 1. [lane-measured: ProbeGarbageKinds] A 0 therefore
   means "less than 1 KiB in total", not "the counted entries are directories".
   An empty directory adds 0 on btrfs.
7. **The census rule.** Run `count-objects -v` against the resolved common git
   dir, for example `git --git-dir=<common> count-objects -v`. There
   `different_commondir` is false, the private-gitdir sweep never runs (S120
   line 371), and a linked-worktree path reports the common-dir figure. This is
   what `tools/souji-size-census.py` does (C1, r24). The rule is exact for every
   trigger in items 3–4 and keeps item 5's real debris counted. Subtracting 1 per
   linked worktree is not exact, because a bisecting or `refs/worktree` linked
   worktree contributes 2 or 3.

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
- **Directory size on other filesystems is not measured.** On a filesystem that
  reports a non-zero directory `st_size`, item 6's code adds it. [INFERENCE:
  not run off btrfs]
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
- ADMIT: "{ 0, 1, 1, "refs" }," — path.c@v2.56.0 line 111 and path.c@v2.30.0 line 123 — reason: refs is unflagged at both tags, so the reading git counts it whoever wrote it — snapshot: census/round-24/sources/git-v2.30.0-path.c
- ADMIT: "{ 0, 1, 0, "refs/bisect" }," — path.c@v2.56.0 line 112 — reason: a second unflagged per-worktree path; an active bisect reads garbage 2 — snapshot: census/round-24/sources/git-v2.56.0-path.c
- ADMIT: "{ 0, 1, 0, "refs/worktree" }," — path.c@v2.56.0 line 114 — reason: a refs/worktree ref reads garbage 2, and 3 with its reflog (logs/refs/worktree, line 108) — snapshot: census/round-24/sources/git-v2.56.0-path.c
- ADMIT: "report_linked_checkout_garbage(the_repository);" — builtin/count-objects.c@v2.56.0 line 118 — reason: the sweep runs only on the -v path the census uses — snapshot: census/round-24/sources/git-v2.56.0-builtin-count-objects.c
- ADMIT: "(unsigned long)(size_garbage / 1024));" — builtin/count-objects.c@v2.56.0 line 152 — reason: size-garbage is the floored KiB of summed bytes, not a directory signal — snapshot: census/round-24/sources/git-v2.56.0-builtin-count-objects.c
- ADMIT: "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared." — § REFS — reason: these namespaces live in the private gitdir, which is why each one is countable there — snapshot: census/round-24/sources/git-worktree.1.txt
- ADMIT: "Within a linked worktree, $GIT_DIR is set to point to this private directory" — § DETAILS — reason: the swept directory is documented per-worktree structure, not debris — snapshot: census/round-24/sources/git-worktree.1.txt
- ADMIT: "garbage: the number of files in the object database that are neither valid loose objects nor valid packs" — § OPTIONS -v/--verbose — reason: object-directory debris is counted from any worktree, so the census must keep it while discounting the sweep — snapshot: census/round-23/sources/git-count-objects.1.txt
- ADMIT: staged garbage-false-positive-modes-r27, re-sourced to S120/S121/S122/S123 — reason: its reader-decides reading and the refs row at both tags verify byte-exact in the committed snapshots; its "nothing but the linked-worktree path" bullet and its shokuknow-only S153 row are dropped, and the refs/* and logs/refs/* triggers it omitted are added — flip: reject if a later tag flags refs with ignore_garbage
- ADMIT: staged garbage-false-positive-modes-r25, five-mode matrix only, as lane-measured — reason: all five creation modes read garbage 1 with refs present, re-run by ProbeLinkedModes, with C1 case 4 as the committed witness — flip: reject if C1 case 4 fails at the landing tip or a later git stops creating the private refs
- REJECT: staged garbage-false-positive-modes-r25 headline ("There is no second trigger mode") and its directory-size reason — reason: path.c@v2.56.0 lines 106-108 and 112-114 leave refs/* and logs/refs/* unflagged, an active bisect or a refs/worktree ref reads garbage 2, and size-garbage is floor(sum/1024) — flip: none for the headline at v2.56.0; re-open only if a later tag flags those rows
- REJECT: staged garbage-false-positive-modes-r26 — reason: its central claim ("Nothing else does", "exclusively the linked-worktree path") is falsified by 12 ProbeGarbageKinds cells on a main worktree; its arm 1 read the live fleet repo; its only evidence (S147) lives in shokuknow; and its fsck pointer names lane S113, which is g_file_trash — flip: admit a restated claim scoped to "a stray file or directory placed directly in objects/ is not counted", re-measured by a lane-committed /var/tmp fixture with no fleet arm and citing lane S115/S116
- REJECT: staged count-objects-garbage-semantics-r23 — reason: its title, census claim and lane link are fleet claims; S131 is quarantined payload-absent; its S112 and S113 collide with lane ids for gio(1) and g_file_trash; "the only two fields not object-graph state" is contradicted by the alternate field; and its directory-size reason is wrong — flip: split it, re-citing the linked-worktree observation to a lane fixture and the field reading to lane S115/S116 with alternate acknowledged, deleting the fleet census, and moving the vendor reclamation material to its own entry under fresh non-colliding ids
- REJECT: the staged provenance cells as-is (S130 S131 S134 S141 S147 S153, 2026-10-23 dates) — reason: they are own-work rows whose evidence lives in shokuknow, and this lane's ids for those numbers name other documents — flip: re-point by document to S120–S123 after the lane mints them, with this round's access date
~~~

## Findings

1. **All L1 decisions are applied.** Ids S120–S123 are as assigned. Snapshot paths use the committed `census/round-24/sources/` names, and `.c` citations use `line N`. ADMIT r27 (re-sourced) and ADMIT the r25 matrix (lane-measured). REJECT r26 and r23, each with a reason and a flip. "Not one trigger" is item 4, the floor-sum `size-garbage` rule is item 6, the common-dir rule naming the tool is item 7, and no fleet figure appears.
2. **The L1's second-trigger claim is confirmed by this seat's own rerun.** An active bisect reads 2 and a `refs/worktree` ref reads 2, matching ScoutPkgEntries E4. Two refinements are written into item 4:
   - bisect needs a marked term; `bisect start` alone stays at 1;
   - a `refs/worktree` ref with a reflog reads 3, through `logs/refs/worktree` (path.c line 108).
3. **`refs/rewritten` is in the table but was not run.** It is unflagged at path.c line 113, and the L1 asked to check the snapshot: it is `{ 0, 1, 0, "refs/rewritten" },` at both tags. No probe ran a rebase that writes it, so the entry cites it from the table only.
4. **Revision-1 content dropped or demoted to fit the L1's four ids.**
   - The git-sparse-checkout, `odb/source-packed.c` and `object-file.c` rows (former placeholders S124–S126) are gone.
   - The sparse-checkout trigger stays in item 4 only as path.c line 102-103 plus an uncommitted observation.
   - The pack-dir and loose-name mechanisms stay as ProbeGarbageKinds measurements, without code citations.
   - If the L1 wants them sourced, it can mint rows for https://git-scm.com/docs/git-sparse-checkout (§ COMMANDS `set`) and the two `.c` files at v2.56.0. Revision-1 digests: `7952d0dc…` (adoc), `bfb57f4c…`, `e011ce18…`.
5. **No `§` locator points at `gitrepository-layout.5.txt`.** Its heading set (Evidence) has no `refs` or `worktrees` heading, so any `§ refs` locator there would be LOCATOR-BAD under Q54. The entry uses git-worktree § REFS and § DETAILS instead.
6. **Q54 checker on this draft.** The fenced block was extracted to scratch, and `python3 -B tests/fixtures/r23-locator-heading.py --entries <draft> --snapshot-dir census/round-24/sources` was run from the lane root. Result: `entries=1 locators=3 locators_bad=0`, exit 0 (145-line draft). The three locators are `§ REFS`, `§ DETAILS` and `§ OPTIONS` in the ADMIT quote lines; `§ OPTIONS` resolved through `census/round-23/sources/git-count-objects.1.txt`. No REJECT line carries a `§`.
7. **C2 coupling.** The F2 row of the `corpus/README.md` coverage map (l.68, entries cell) must list `knowledge/count-objects-linked-worktree-garbage.md`, or `MISSING-FROM-MAP` fires.

## Attack log

- **ATTACK (C1 case 4, coverage; reported, no change proposed).** Case 4 builds a linked worktree whose only counted path is `refs`. A tool that discounts by "subtract 1 per linked worktree" passes it exactly like the frozen common-dir read. That tool reports 1 on a bisecting or `refs/worktree` linked worktree (raw 2), and 2 with a reflog or sparse-checkout (raw 3). The frozen cases cannot tell the two discounts apart. ScoutPkgEntries A1 reports the same gap independently. The case set stays frozen.
- **Observation (Q54 checker, low).** `r23-locator-heading.py` resolves a locator by substring (`head.lower() in h`), so a short `§ REF` would resolve against `refs`. Not used in this draft.
