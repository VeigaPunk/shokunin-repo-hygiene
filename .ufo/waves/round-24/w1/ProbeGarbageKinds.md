# ProbeGarbageKinds — souji r24 wave 1

## Status
STATUS: PASS — every cell ran (31 cells, git 2.56.0). The hypothesis holds in direction but is wrong about `rounds`: `size-garbage` is the floor of the **summed** bytes divided by 1024. The staged entry `garbage-false-positive-modes-r26.md` is falsified in its headline claim ("Nothing else does").

## Evidence
- Revision: lane HEAD `f9db2181647d91470a724a12d626bd6106805076`; `git version 2.56.0` (`/usr/bin/git`); git source is a depth-1 clone of tag v2.56.0 at `a018953688f1b10bddf91bff8747068f5f4746a4`.
- Harness: `/var/tmp/souji-r24-ProbeGarbageKinds/probe.sh` (sha256 `0851a538…cdb30`). It builds one fresh repo per cell with `LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null`, makes one commit, adds one planting, and runs `git -C <repo> count-objects -v`. The output went to `probe.out` (sha256 `b4de44ca…6f046`). Both scratch files have been removed. Repo paths in stderr are shown relative to the scratch cells root. Every cell exited 0.

Per-cell output (stdout fields | stderr), verbatim from the run:

| cell | planting (one per repo) | stdout | stderr | verdict |
|---|---|---|---|---|
| c00 | none (loose) | `garbage: 0 size-garbage: 0` | (empty) | baseline |
| c00p | none (after `repack -a -d`) | `in-pack: 3 garbage: 0 size-garbage: 0` | (empty) | baseline |
| a1 | 10240 B file `objects/stray.txt` | `garbage: 0 size-garbage: 0` | (empty) | NOT counted — hypothesis CONFIRMED |
| a2 | dir `objects/straydir/` holding a 10240 B file | `garbage: 0 size-garbage: 0` | (empty) | NOT counted — CONFIRMED |
| a2b | non-hex 2-char dir `objects/zz/` holding a file | `garbage: 0 size-garbage: 0` | (empty) | NOT counted (only `%02x` subdirs are scanned) |
| t2 | 10240 B `objects/tmp_obj_Xy12Ab` (top level) | `garbage: 0 size-garbage: 0` | (empty) | NOT counted |
| a3 | 5 B `objects/pack/junk` | `garbage: 1 size-garbage: 0` | `warning: garbage found: .git/objects/pack/junk` | counted — CONFIRMED |
| a3b | 5 B `objects/pack/junk.txt` | `garbage: 1 size-garbage: 0` | `warning: garbage found: .git/objects/pack/junk.txt` | counted — CONFIRMED |
| a4 | 5 B `objects/12/zz` | `garbage: 1 size-garbage: 0` | `warning: garbage found: .git/objects/12/zz` | counted — CONFIRMED |
| b1023 | 1023 B pack junk | `garbage: 1 size-garbage: 0` | `warning: garbage found: .git/objects/pack/junk` | KiB, truncated |
| b1024 | 1024 B pack junk | `garbage: 1 size-garbage: 1` | same | KiB |
| b10239 | 10239 B pack junk | `garbage: 1 size-garbage: 9` | same | floor, not round — hypothesis wording REFUTED |
| b10240 | 10240 B pack junk | `garbage: 1 size-garbage: 10` | same | 10 KiB → 10 — CONFIRMED |
| b2x | two 600 B pack junk files | `garbage: 2 size-garbage: 1` | two `garbage found` lines (junk1, junk2) | bytes summed before /1024 |
| m1 | 3×10240 B pack junk + 10240 B `objects/12/zz` | `garbage: 4 size-garbage: 40` | four `garbage found` lines | count and size add up across kinds |
| h1 | 10240 B pack junk, `count-objects -v -H` | `garbage: 1` `size-garbage: 10.00 KiB` | `warning: garbage found: .git/objects/pack/junk` | `-H` changes the unit; the bare number is KiB only without `-H` |
| t1 | 10240 B `objects/ab/tmp_obj_Xy12Ab` | `garbage: 1 size-garbage: 10` | `warning: garbage found: .git/objects/ab/tmp_obj_Xy12Ab` | counted (no `tmp_obj_` exemption in count-objects) |
| okeep | 10240 B orphan `pack-0123…4567.keep` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .idx or .pack: .git/objects/pack/pack-0123456789abcdef0123456789abcdef01234567.keep` | counted |
| opromisor | orphan `.promisor` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .idx or .pack: …pack-0123…4567.promisor` | counted |
| obitmap | orphan `.bitmap` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .idx or .pack: …pack-0123…4567.bitmap` | counted |
| orev | orphan `.rev` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .idx or .pack: …pack-0123…4567.rev` | counted |
| omtimes | orphan `.mtimes` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .idx or .pack: …pack-0123…4567.mtimes` | counted |
| oidx | orphan `.idx` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .pack: …pack-0123…4567.idx` | counted, different message |
| opack | orphan `.pack` | `garbage: 1 size-garbage: 10` | `warning: no corresponding .idx: …pack-0123…4567.pack` | counted, different message |
| k1 | control: 10240 B `.keep` next to a real pack+idx | `in-pack: 3 garbage: 0 size-garbage: 0` | (empty) | not counted (correct negative) |
| k2 | control: 10240 B `.promisor` next to a real pack+idx | `in-pack: 3 garbage: 0 size-garbage: 0` | (empty) | not counted |
| d38 | empty dir named 38-hex inside `objects/12/` | `count: 3 garbage: 1 size-garbage: 0` | `warning: garbage found: .git/objects/12/0123456789abcdef0123456789abcdef012345` | counted (`!S_ISREG`); dir adds 0 bytes |
| up | 10240 B file with UPPERCASE 38-hex name in `objects/12/` | `count: 4 size: 24 garbage: 0 size-garbage: 0` | (empty) | NOT garbage: counted as a loose object (false negative) |
| w1main | main worktree of a repo with one linked worktree | `garbage: 0 size-garbage: 0` | (empty) | matches prereg design probe |
| w1linked | linked worktree path | `garbage: 1 size-garbage: 0` | `warning: garbage found: w1/.git/worktrees/w1-linked/refs` | matches prereg design probe |

## Findings
1. **Hypothesis: confirmed except for one word.** Stray files or directories directly in `objects/` are not counted (a1, a2, a2b, t2). Junk in `objects/pack/` (a3, a3b) and invalid names in `objects/<2hex>/` (a4) are counted. `size-garbage` is in KiB (b1024=1, b10240=10). Small files read 0 by **truncation of the byte sum**, not by rounding: b10239 gives 9, and b2x gives 1 because 2×600 B are summed before the division. Source: git v2.56.0 `builtin/count-objects.c:152` "(unsigned long)(size_garbage / 1024));". Doc: `Documentation/git-count-objects.adoc:41` "size-garbage: disk space consumed by garbage files, in KiB (unless -H is".
2. **Why `objects/` top level is blind:** only the 256 `%02x` subdirectories are walked. Source: `object-file.c:1060` "strbuf_addf(path, \"%02x\", subdir_nr);" and `object-file.c:1121` "for (int i = 0; i < 256; i++) {".
3. **Why `<2hex>/` names count:** any entry whose name is not 38 hex characters goes to `cruft_cb`. Source: `object-file.c:1080` "if (namelen == algop->hexsz - 2 &&". Under `-v`, that callback reports garbage: `builtin/count-objects.c:80` "loose_garbage(path);". A *directory* with a valid hex name also counts (d38): `builtin/count-objects.c:66` "if (lstat(path, &st)" (the line continues with an or-test of "!S_ISREG(st.st_mode))").
4. **`tmp_obj_*` in `<2hex>/` is counted (t1).** git itself writes `tmp_obj_XXXXXX` files in that directory while storing objects: `odb/source-loose.c:641` "strbuf_addstr(tmp, \"tmp_obj_XXXXXX\");". fsck exempts these files, but count-objects does not: `odb/source-loose.c:1096` "if (!starts_with(basename, \"tmp_obj_\"))". [INFERENCE] A census taken while a concurrent object write is in flight can read a transient `garbage` ≥1, so the C1 lane-bound measurement should be taken on a quiescent repo.
5. **Orphan sidecars in `pack/` are counted (okeep, opromisor, obitmap, orev, omtimes, oidx, opack), with three distinct messages; sidecars next to a real pack+idx are not (k1, k2).** Source: `odb/source-packed.c:781` "ends_with(file_name, \".keep\")" (a known suffix is deferred to pairing, not reported at once), and `odb/source-packed.c:707` "if (seen_bits == (PACKDIR_FILE_PACK" (the line continues with the IDX bit: only a basename with both .pack and .idx suppresses the report). The message map is in `builtin/count-objects.c`, `bits_to_msg`.
6. **False negative (up):** a file with an uppercase-hex 38-char name is counted as a loose object (`count: 4`), not as garbage. So `garbage=0` does not certify that loose object names are canonical.
7. **The staged entry `merge/souji/knowledge/corpus/knowledge/garbage-false-positive-modes-r26.md` is falsified** (read-only source, not edited). Its claim at line 16, "**Nothing else does.**", and at line 24, "the trigger is exclusively the linked-worktree path", are contradicted by a3, a3b, a4, t1, d38 and all seven orphan cells. Its arms only planted in `objects/` top level, which is the one region the scan never visits (Finding 2). Its line 40 says the field reads 0 "because the counted entries are **directories**"; that is true only for the linked-worktree `refs` hit, while b10240 and m1 give 10 and 40. Recommendation for the assimilation gate: **reject r26 as-is**. Its correct fragment, `builtin/count-objects.c:118` "report_linked_checkout_garbage(the_repository);", holds at v2.56.0 and is already carried by the preregistration design probe.
8. The w1 cells reproduce the preregistration's linked-worktree oracle (main 0, linked 1 with `…/worktrees/<id>/refs`). Mechanism: `path.c:111` "{ 0, 1, 1, \"refs\" }," (no ignore_garbage bit) against `path.c:104` "{ 1, 1, 1, \"logs\" },".

## Attack log
- **A1 (C1 case 3 / case 8, the size_garbage field is unfalsified).** Frozen case 3 asserts only `garbage=1`. If the fixture's junk file is under 1024 B, the real `size_garbage` is 0 (cells a3, b1023), identical to the case-8 stub's `size_garbage=0`. The stub is still rejected through garbage, unreachable and alternates, but no frozen case can detect a tool that mis-parses or zeroes `size-garbage`. This is reported, not re-specified. [INFERENCE] The tool fixture would discriminate only if its pack junk is ≥1024 B; that is the executor's choice within the frozen predicate.
- **A2 (C1 lane-bound measurement).** Finding 4 means one census run can be inflated by an in-flight `tmp_obj_*`. The figure should be read with its `census.warning=` lines; a `tmp_obj_` path there marks a transient, not debris.

## Tooling / scope
- No installs or upgrades. Network reads only: raw.githubusercontent.com for `builtin/count-objects.c` and a depth-1 `git clone` of git.git tag v2.56.0, both into scratch.
- Writes: this report only. Scratch `/var/tmp/souji-r24-ProbeGarbageKinds/` was created, then removed. Nothing in the lane, the fleet, or shokuknow was modified.
