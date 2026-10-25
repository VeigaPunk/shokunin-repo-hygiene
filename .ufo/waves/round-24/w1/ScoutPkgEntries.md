# ScoutPkgEntries — staged `garbage` entries (r23, r25, r26, r27): sources, claim classes, admit/reject

## Status
STATUS: PASS — all 4 entries, all 11 cited ids (8 `source:` lines + 3 body-only ids) traced to their SOURCES.append rows; every external source re-opened this run; measured claims re-run in /var/tmp. Verdicts: r27 ADMIT (re-grounded), r25 ADMIT-PARTIAL (matrix only), r26 REJECT, r23 REJECT.

## Evidence
Revisions: lane HEAD `f9db2181647d91470a724a12d626bd6106805076` (= prereg lane commit). shokuknow read only, with no git ops; file sha256 prefixes: r25 `0b44a08f649c4fc9`, r26 `2ce3dc3178eecfc0`, r27 `66f48bcb057095ae`, r23 `c140aee8cbdf1c44`, SOURCES.append.md `1510052ee7ca2b6f`, MERGE-REPORT.md `eea18eed8f2515be`. Host `git version 2.56.0`; /var/tmp fs = btrfs.

E1 — the own-work evidence exists in shokuknow, and the hashes match the rows (`sha256sum`, prefix):
`round2/evidence/r23-garbage-probe.out cb1bb2e6…`, `round2/evidence/r23-worktree-census.out 1ac71c4f…`, `round3/evidence/r24-fleet-garbage-census.out c2df19ee…`, `round4/evidence/r25-garbage-matrix.out ea26206d…`, `round5/evidence/r26-garbage-second-mode.out 7714641c…`, `round6/evidence/r27-garbage-git-versions.out 5a7da661…` (all under /home/vgpnk/Projects/shokuknow/lanes/souji/). Fixtures `round4/fixtures/r25-garbage-matrix.py` and `round5/fixtures/r26-garbage-second-mode.sh` exist.

E2 — upstream re-open (curl rc=0, raw.githubusercontent.com/git/git/<tag>/…):
- `path.c@v2.56.0` 41992 B sha256 `f98ba3446d768e3c`. Line 90: "/* Not considered garbage for report_linked_checkout_garbage */"; :104 `{ 1, 1, 1, "logs" },`; :105 `{ 1, 0, 0, "logs/HEAD" },`; :111 `{ 0, 1, 1, "refs" },`; :106-108 `logs/refs/{bisect,rewritten,worktree}` and :112-114 `refs/{bisect,rewritten,worktree}` all `{ 0, 1, 0, … }`; :120 `{ 1, 0, 1, "gc.pid" },`; :365-381 `report_linked_checkout_garbage` returns early on "if (!r->different_commondir)", then does "if (p->ignore_garbage) continue;" and reports when "if (file_exists(sb.buf))".
- `path.c@v2.30.0` 39042 B sha256 `7c5b071078049826`: line 123 `{ 0, 1, 1, "refs" },`; lines 124-126 `refs/{bisect,rewritten,worktree}` also have ignore_garbage 0.
- `builtin/count-objects.c@v2.56.0` 4439 B sha256 `ec13ae40d08741d0`: line 118 "report_linked_checkout_garbage(the_repository);". Lines 55-58: `loose_garbage` calls "report_garbage(PACKDIR_FILE_GARBAGE, path);". Line 152: "(unsigned long)(size_garbage / 1024));".

E3 — doc/vendor re-open (curl, HTTP 200 each). S112 git-count-objects: "size-garbage: disk space consumed by garbage files, in KiB (unless -H is". The installed `man git-count-objects` says "garbage: the number of files in the object database that are neither valid loose objects nor valid packs". S113 git-fsck: `man git-fsck` --lost-found "Write dangling objects into .git/lost-found/commit/ or .git/lost-found/other/". S127 gitlab.cn (352073 B): "极狐GitLab 运行 Git 垃圾回收时带有 30 分钟的宽限期。". S128 alibabacloud (22286 B): "当容量达到存储限额的90%时" and "当容量超过上限后将禁止写操作". S129 atlassian ja (617915 B, `lang="ja-JP"`, quote count 1): "Git 「GC」（ガベージ コレクション）は、どのブランチやタグも実際に使用せず、何らの参照もしていないすべてのデータをリポジトリから削除します".

E4 — probe `bash /var/tmp/souji-r24-ScoutPkgEntries/probe.sh` (synthetic repos only, GIT_CONFIG_GLOBAL=/dev/null, trap-removed), rc=0. Excerpt:
```
cell=detach        private=[HEAD ORIG_HEAD commondir gitdir index logs refs ] linked: garbage=1 size-garbage=0
cell=branch        private=[HEAD ORIG_HEAD commondir gitdir index logs refs ] linked: garbage=1 size-garbage=0
cell=orphan        private=[HEAD commondir gitdir index refs ] linked: garbage=1 size-garbage=0
cell=detach+commit private=[COMMIT_EDITMSG HEAD ORIG_HEAD commondir gitdir index logs refs ] linked: garbage=1
cell=branch+commit private=[COMMIT_EDITMSG HEAD ORIG_HEAD commondir gitdir index logs refs ] linked: garbage=1
main: garbage=0 ; linked: garbage=1 (warning: garbage found: <W>/base/.git/worktrees/wt/refs)
linked-read-via-common-gitdir: garbage: 0
stray file in objects/: garbage=0 ; stray dir in objects/: garbage=0
junk file in objects/pack/: garbage=1 size-garbage=0 ; invalid loose name objects/12/zz: garbage=1 size-garbage=0
pack without .idx: garbage=2 size-garbage=0
after update-ref refs/worktree/x (linked): garbage=2  (warnings: …/worktrees/wt/refs, …/worktrees/wt/refs/worktree)
during bisect (linked): garbage=2  (warnings: …/worktrees/wt/refs, …/worktrees/wt/refs/bisect); main of same repo: garbage=0
```
An empty directory has `stat` st_size=0 on this btrfs /var/tmp.

## Findings

### Per-entry source map (rows = /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md, line = NR)

1. **count-objects-garbage-semantics-r23.md**: 7 `source:` lines.
   - S130 (L28): "souji round-2 probe r23-garbage-probe", path `lanes/souji/round2/evidence/r23-garbage-probe.out`, own-work, tier A. **Own-work living in shokuknow.**
   - S131 (L29): "souji round-2 census r23-worktree-census", path `lanes/souji/round2/evidence/r23-worktree-census.out`, own-work, tier A. **Own-work in shokuknow, and a fleet census.** It is also in the lane quarantine slice as `payload-absent` (/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/assimilation/quarantine-slice).
   - S112 (L10): "git-count-objects(1)", https://git-scm.com/docs/git-count-objects, docs, tier A. External and re-openable. **The id collides**: lane S112 is "gio(1), GIO commandline tool" (/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md:132). The lane already holds this URL as S115 (:135).
   - S113 (L11): "git-fsck(1)", https://git-scm.com/docs/git-fsck, docs, tier A. External. **The id collides**: lane S113 is "GLib GIO g_file_trash()" (:133), and the lane holds this URL as S116 (:136).
   - S127 (L25): "极狐GitLab 文档中心，代码仓库大小", https://gitlab.cn/docs/jh/user/project/repository/repository_size/, docs, tier **A**. External; not in the lane registry.
   - S128 (L26): "阿里云云效，如何进行代码库容量管理", https://www.alibabacloud.com/help/zh/yunxiao/user-guide/capacity-and-cleanup-instructions, docs, tier **A**. External; not in the lane registry.
   - S129 (L27): "Atlassian サポート，Git リポジトリのメンテナンス（日本語版）", https://support.atlassian.com/ja/bitbucket-cloud/docs/maintain-a-git-repository/, docs, tier B. External; not in the lane registry.
   - Tier inconsistency: the entry body calls S127–S129 "(tier B)", but rows S127 and S128 say A.
2. **garbage-false-positive-modes-r25.md**
   - `source:` S141 (L39): "souji round-4 probe r25-garbage-matrix", path `lanes/souji/round4/fixtures/r25-garbage-matrix.py`, own-work, tier A. **Own-work in shokuknow.**
   - Body-only: S134 (L32), "souji round-3 census r24-fleet-garbage-census", own-work, a fleet census. The lane already REJECTED this row (/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/count-objects-garbage-readings-r25.md:65): "the evidence lives outside this repository, so the row cannot be bound to a lane path".
   - The amendment note points at `corpus/knowledge/count-objects-garbage-semantics-r24.md`, which is a package entry absent from the lane, so the pointer dangles if admitted alone.
3. **garbage-false-positive-modes-r26.md**
   - `source:` S147 (L45): "souji round-5 probe r26-garbage-second-mode", path `lanes/souji/round5/fixtures/r26-garbage-second-mode.sh`, own-work, tier A. **Own-work in shokuknow.**
   - Body-only: S141; and S113 as "which the lane's S113 holds". **That pointer is wrong in the lane**, where S113 is g_file_trash; fsck is lane S116.
   - The amendment note points at r25 and at `count-objects-garbage-semantics-r24.md`; both are absent from the lane.
4. **garbage-false-positive-modes-r27.md**
   - `source:` S153 (L51): "souji round-6 probe r27-garbage-git-versions", path `lanes/souji/round6/evidence/r27-garbage-git-versions.out`, own-work, tier A. **Own-work in shokuknow.** Its content, however, is only a reading of upstream code (E2).
   - Body-only: S147.
   - The amendment note points at r25 and r26.

### Claim classes: (a) lane-reproducible by a /var/tmp probe, (b) upstream-source-checkable, (c) fleet claim (refused)

5. **r23**
   - c1 "linked worktree `garbage: 1` + warning on `…/worktrees/wt/refs`; main `garbage: 0`": (a), REPRODUCED (E4).
   - "filesystem debris, not object-graph state": (b). The man page defines it as files "neither valid loose objects nor valid packs", which does not cover a worktree-private `refs` dir. Over-broad.
   - "size-garbage 0 because a directory has no meaningful byte size": (a)+(b), **WRONG REASON**. size-garbage is integer KiB (count-objects.c:152), and a 5-byte junk file in objects/pack also reads 0 (E4).
   - c2 "`garbage`/`size-garbage` are the only two fields … not object-graph state": (b), **CONTRADICTED** by the man page's `alternate:` field (S112 row teaches alternates too).
   - `bits_to_msg` four messages: (b), VERIFIED (count-objects.c:24-35).
   - "i.e. pack directory debris": (b)+(a), INCOMPLETE. Loose invalid names are also counted (count-objects.c:58; `objects/12/zz` gives 1, E4).
   - "removal list must use fsck --unreachable": (b), VERIFIED (S113 man).
   - c3 (5 registrations, 0 prunable, 0 locked, `prune --dry-run`, index mtimes, r12 figure stale): **(c) refused**.
   - c4 vendor 30-minute grace, 90% threshold plus write-lock, JA reclaim sequence and quote: (b), VERIFIED (E3). Off-theme for F2 linked-worktree garbage.
   - "What this does NOT establish": the first sentence of bullet 1 is (a). "No real debris anywhere in the fleet" and "point-in-time census" are (c).
   - The title clause "the fleet is not currently exposed" and the lane link "the fleet is currently clean" are (c).
6. **r25**
   - S134 recap: "linked `garbage: 1` counting private `refs/`" is (a), REPRODUCED. "path.c common_list ignore_garbage on logs and gc.pid but not refs" is (b), VERIFIED (path.c:104,111,120; it omits logs/HEAD at :105). "The fleet reads 0 only because its linked worktrees have no `refs/`" is (c).
   - c1, five creation modes: `garbage: 1` in every cell, `size-garbage: 0`, `refs` present in all, `--orphan` has no `logs` and no `ORIG_HEAD`, and `COMMIT_EDITMSG` appears after a commit. (a), REPRODUCED 5/5 (E4). The claim that `MERGE_RR` appears after a commit did NOT reproduce under an empty global config. [INFERENCE] It is user-config-dependent (rerere).
   - c2 "single universal property … that directory is what the sweep counts": (a), **FALSIFIED** as a sole trigger. `refs/worktree` or `refs/bisect` in the private gitdir gives `garbage: 2` (E4), per path.c:106-108 and :112-114 (E2). The "universal" half (every mode has `refs`) holds.
   - c3 "run from main or discount linked private gitdirs": (a), HOLDS (main 0; `--git-dir=<common>` 0). "The fleet's own numbers (S134 …) are the correct ones to trust" is (c).
   - "What this does NOT establish": bullet 1 is (c). Bullet 2, the different-git-version gap, is (b), closed by r27's reading. Bullet 3, "size-garbage 0 means directories", has the **WRONG REASON** (see r23).
7. **r26**
   - Arm 1, "the live fleet repo's main worktree → garbage=0": **(c) refused**. The probe also read /home/vgpnk/Projects/shokunin, which a lane seat must not do.
   - Arms 2 and 3, a stray file or dir directly in `objects/` gives 0: (a), REPRODUCED.
   - Arm 4, linked 1 and main 0: (a), REPRODUCED.
   - c1 "Nothing else does" and c2 "trigger is exclusively the linked-worktree path … real debris in the object directory is not counted": (a)+(b), **FALSIFIED**. `objects/pack/junk` gives 1, `objects/12/zz` gives 1, and a pack without `.idx` gives 2 on a main worktree (E4). The man definition (E3) names exactly such files. Inside linked worktrees, `refs/worktree` and `refs/bisect` give 2.
   - "builtin/count-objects.c:118 calling report_linked_checkout_garbage()": (b), VERIFIED.
   - c3 "census rule now settled": partially true (a). The rule also needs objects/pack debris to stay counted.
   - "What this does NOT establish": bullet 1 is (b), closed by r27. Bullet 2 has the wrong size reason; its fsck pointer is (b) but cites the wrong lane id. Bullet 3, synthetic arms, is (a).
8. **r27**
   - c1, the call chain and skip on `ignore_garbage`, plus the struct comment quote: (b), VERIFIED (path.c:90, :365-381; count-objects.c:118). "The reader decides, regardless of writer": (b). [INFERENCE] from the walk over `r->gitdir` with the reader's table; sound.
   - c2, `{ 0, 1, 1, "refs" },` at v2.56.0 and v2.30.0, with logs, logs/HEAD and gc.pid set to 1: (b), VERIFIED byte-exact (v2.56.0:111, v2.30.0:123; :104/:105/:120).
   - c3 "cell closes without a second binary": (b) inference. Sound for the counting rule; the entry itself scopes off private-gitdir content.
   - "What this does NOT establish": bullets 1 and 3 are (b), accurate. Bullet 2, "the round-5 arms (S147) already established that nothing but the linked-worktree path produces a non-zero figure on this host", is **FALSIFIED** (E4).
   - **Omission**: the same table it read shows `refs/bisect`, `refs/rewritten`, `refs/worktree` and `logs/refs/*` with ignore_garbage 0. That is a second linked-worktree trigger, reproduced at `garbage: 2`.

### What MERGE-REPORT says (/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md)
9. The four entries appear only as `new-file` rows: r23 at :26, r25 at :33, r26 at :38 and r27 at :43; the companion `count-objects-garbage-semantics-r24.md` is at :29. Its `used-by` corrections at :114-115 add the r23 entry to S112 and S113. The report flags no dangling citation, collision or claim problem for these entries ("proposed rows refused: **0**").
10. MERGE-REPORT:9 "lane registry currently holds **108** rows; first staged id is **S109**" is **stale**. The lane now holds 119 (reg-ids), so staged S109–S119 collide (the 11 `assimilation/collisions` ids), including the r23 entry's S112 and S113. The adopt checklist (step 3, "Append `SOURCES.append.md` to `corpus/SOURCES.md`") would mis-cite r23 to gio(1) and g_file_trash.

### Recommendations (prereg §Assimilation: at most 2 admitted, at least 1 rejected, own-work shokuknow rows not appendable as-is)
11. **r27: ADMIT (re-grounded)**, as the mechanism half of C1's one F2 entry.
    - Replace the S153 own-work row with new lane rows for `https://github.com/git/git/blob/v2.56.0/path.c` (L90, L104-L122, L365-L381), `…/v2.30.0/path.c` (L123) and `…/v2.56.0/builtin/count-objects.c` (L118, L152). These are the prereg-named "git.git path.c / builtin/count-objects.c at v2.56.0".
    - Drop the falsified "nothing but the linked-worktree path" bullet.
    - Add the `refs/{bisect,rewritten,worktree}` and `logs/refs/*` second trigger.
    - Drop the amendment pointers to r25 and r26.
12. **r25: ADMIT-PARTIAL**: only c1's five-mode matrix (all garbage=1, `refs` in every private gitdir), re-measured by a lane fixture (C1 case 4 can carry it), not S141.
    - Strike the "one trigger" headline and c2's "that directory is what the sweep counts".
    - Strike every S134 and fleet sentence (c).
    - Strike the directory-size reason and `MERGE_RR`.
    - Fold it into the same C1 entry as item 11, so C1 still lands one entry.
    - If the L1 wants a single admit, take r27 only and REJECT r25. Flip condition: a lane-committed matrix receipt at a named revision.
13. **r26: REJECT**.
    - Reasons: its central claim (c1/c2, "Nothing else does", "exclusively the linked-worktree path") is falsified by objects/pack junk, invalid loose names and missing `.idx` (E4) and by the man page definition. Arm 1 is a fleet read (c). S147 is own-work in shokuknow. Its S113 pointer is wrong in the lane.
    - **Flip**: a restated claim scoped to "a stray file or dir placed directly in `objects/` (not `objects/pack/`, not a 2-hex fan-out dir) is not counted". It must be re-measured by a lane-committed /var/tmp fixture with no fleet arm, and cite lane S115/S116 by their lane ids.
14. **r23: REJECT**.
    - Reasons: c3 and its title are fleet claims (c), and S131 is quarantined (`payload-absent`). S112 and S113 collide with lane ids for different documents. c2 "only two fields" is contradicted by `alternate:`, and the size reason is wrong. c4's vendor material is off-theme for the linked-worktree false positive. c1 duplicates what r27/r25 plus the lane fixture carry, and the lane already holds the F2 read side (`count-objects-garbage-readings-r25.md`, `repo-size-census-readonly.md`).
    - **Flip**: split it. Re-cite c1 to a lane fixture and c2 to lane S115/S116 (with `alternate:` acknowledged). Delete c3 and the title clause. Move c4 to a reclamation-deadline entry, with S127–S129 appended under fresh non-colliding ids and tiers reconciled (body says B, rows S127/S128 say A).

## Attack log
- A1 (C1 frozen case 4, gameability, reported, not a proposed edit). Case 4 checks only that the tool reads `garbage=0` on a linked worktree whose raw figure is 1, i.e. the `refs`-only mode. An implementation that subtracts 1 from the linked-worktree figure, instead of reading the common dir as the contract says, passes case 4. It reads 1, not 0, on a linked worktree with `refs/worktree/*` or an active bisect (raw 2, E4). The frozen case set cannot distinguish them; whether `tests/fixtures/r24-size-census.py` happens to check it is for the integrator.
- A2 (contract scope). The prereg's own-work list "(S134/S141/S147/S153 staged ids)" omits S130 and S131. They are the same class (own-work in shokuknow), and S131 is also a fleet census. The same rule must apply to them.

Tools installed/updated: none. Scratch /var/tmp/souji-r24-ScoutPkgEntries/ (probe.sh, fetched sources) removed after writing this report.
