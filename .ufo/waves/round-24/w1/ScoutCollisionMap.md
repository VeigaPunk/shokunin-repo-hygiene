# ScoutCollisionMap — souji round 24, wave 1

## Status
STATUS: PASS — all 11 colliding ids mapped. Every one is a different document on each side. The 0–3-space guard is proven in scratch: the column-zero-only pattern misses the indented `S120` row and the frozen pattern catches it. The next free lane id is **S120**.

## Evidence
Revisions: lane HEAD `f9db2181647d91470a724a12d626bd6106805076` (the last commit touching `corpus/SOURCES.md` is `476525026cdb179f2d49441e1cb6c6f7316f3124`; the file is clean in the working tree). shokuknow HEAD `8b94c5c12c0521e4cd9ed8e5b6939afd8518c715`; last commit touching `merge/souji/SOURCES.append.md` is `ba6779f0160d12dd7373627e00291d6d5e3ba7ee` (read-only).
sha256: lane `corpus/SOURCES.md` `027379dc…7e0c9`; staged `SOURCES.append.md` `1510052e…f7d6`.

E1 — re-derived the id lists with the frozen pattern and compared them with the wave files (pi-uu-grep, then re-run with GNU grep 3.12):
```
$ grep -E '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | sed -E 's/^ {0,3}\|[[:space:]]*(S[0-9]+).*/\1/' > lane.ids
lane 119 rows, 119 unique, max S119 ; staged 134 rows, 134 unique
diff lane.ids reg-ids -> REG-IDS-MATCH ; diff staged.ids staged-ids -> STAGED-IDS-MATCH
comm -12 -> S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119   (= collisions, 11)
/usr/bin/grep -cE <frozen> -> SOURCES.md:119  SOURCES.append.md:134
```

E2 — the indent guard in scratch `/var/tmp/souji-r24-ScoutCollisionMap/scratch-registry.md` (`cat -A` shown):
```
| id | source |$
|----|--------|$
| S119 | col-zero row |$
  | S120 | two-space indented row |$
   | S121 | three-space indented row |$
    | S122 | four-space = indented code block, not a table row |$

$ /usr/bin/grep -nE '^\|[[:space:]]*S[0-9]{3,}' scratch-registry.md      # column-zero only
3:| S119 | col-zero row |
$ /usr/bin/grep -cE '^\|[[:space:]]*S120' scratch-registry.md ; echo exit=$?
0
exit=1                                                                     # MISSES S120

$ /usr/bin/grep -nE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' scratch-registry.md # frozen
3:| S119 | col-zero row |
4:  | S120 | two-space indented row |
5:   | S121 | three-space indented row |
$ grep -cE '^ {0,3}\|[[:space:]]*S120' scratch-registry.md
1                                                                          # CATCHES S120
```
pi-uu-grep 0.2.0 gave identical output. Line 6 (4 spaces) is correctly excluded: in CommonMark, 4 or more spaces of indentation starts an indented code block, so that line is not a table row.

E3 — next free id:
```
$ grep -E <frozen> corpus/SOURCES.md | sed -E 's/^ {0,3}\|[[:space:]]*S0*([0-9]+).*/\1/' | sort -n | tail -1 | awk '{printf "max=S%03d next=S%03d\n",$1,$1+1}'
max=S119 next=S120
$ grep -cE '^ {1,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md SOURCES.append.md  -> 0 and 0
$ grep -cE '^ {0,3}\|[[:space:]]*S120\b' corpus/SOURCES.md -> 0
```

E4 — compared the first URL in each row's source cell across all ids, using a join on the URL (from `L.url` and `A.url`; scratch has since been removed):
```
lane  staged  url
S001  S170    https://git-scm.com/docs/git-maintenance
S002  S169    https://git-scm.com/docs/git-gc
S042  S143    https://git-scm.com/docs/git-config
S057  S143    https://git-scm.com/docs/git-config
S063  S169    https://git-scm.com/docs/git-gc
S110  S116    https://man7.org/linux/man-pages/man2/rename.2.html
S111  S115    https://man7.org/linux/man-pages/man1/mv.1.html
S112  S137    https://man.archlinux.org/man/gio.1.en
S113  S126    https://docs.gtk.org/gio/method.File.trash.html
S114  S117    https://man7.org/linux/man-pages/man2/statx.2.html
S114  S125    https://man7.org/linux/man-pages/man2/statx.2.html
S115  S112    https://git-scm.com/docs/git-count-objects
S116  S113    https://git-scm.com/docs/git-fsck
S117  S114    https://git-scm.com/docs/git-prune
S118  S138    https://qiita.com/koseki/items/f1af58f1ec1693f0536a
S119  S139    https://bbs.csdn.net/weixin_33940469/article/details/100327798
URL-less rows: lane 5 (S026 S031 S039 S041 S109), staged 34
```

## Findings
1. **Collision map: all 11 ids point to different documents.** Each entry below gives the lane row (`/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`, lines 129–139) and then the staged row (`/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, lines 7–17). Each title is quoted verbatim from its source cell.
   - **S109** — lane L129: "souji round-2 RENAME_NOREPLACE probe, vendored", own-work with no URL (`lanes/souji/round2/evidence/noreplace_probe.py`). Staged L7: "git-fetch(1)", https://git-scm.com/docs/git-fetch. **DIFFERENT**.
   - **S110** — lane L130: "rename(2), man-pages 6.19", https://man7.org/linux/man-pages/man2/rename.2.html. Staged L8: "git/git v2.56.0 builtin/fetch.c, builtin/merge.c, …", https://github.com/git/git/blob/v2.56.0/builtin/fetch.c. **DIFFERENT**.
   - **S111** — lane L131: "mv(1), GNU coreutils", https://man7.org/linux/man-pages/man1/mv.1.html. Staged L9: "git/git v2.56.0 builtin/pull.c", https://github.com/git/git/blob/v2.56.0/builtin/pull.c. **DIFFERENT**.
   - **S112** — lane L132: "gio(1), GIO commandline tool (glib2 2.90.1)", https://man.archlinux.org/man/gio.1.en. Staged L10: "git-count-objects(1)", https://git-scm.com/docs/git-count-objects. **DIFFERENT**.
   - **S113** — lane L133: "GLib GIO g_file_trash() method reference", https://docs.gtk.org/gio/method.File.trash.html. Staged L11: "git-fsck(1)", https://git-scm.com/docs/git-fsck. **DIFFERENT**.
   - **S114** — lane L134: "statx(2), man-pages 6.19", https://man7.org/linux/man-pages/man2/statx.2.html. Staged L12: "git-prune(1)", https://git-scm.com/docs/git-prune. **DIFFERENT**.
   - **S115** — lane L135: "git-count-objects(1)", https://git-scm.com/docs/git-count-objects. Staged L13: "mv(1), GNU coreutils", https://man7.org/linux/man-pages/man1/mv.1.html. **DIFFERENT**.
   - **S116** — lane L136: "git-fsck(1)", https://git-scm.com/docs/git-fsck. Staged L14: "rename(2), renameat2(2) — Linux man-pages 6.19 (2026-02-08)", https://man7.org/linux/man-pages/man2/rename.2.html. **DIFFERENT**.
   - **S117** — lane L137: "git-prune(1)", https://git-scm.com/docs/git-prune. Staged L15: "statx(2) — Linux man-pages 6.19 (2026-02-08)", https://man7.org/linux/man-pages/man2/statx.2.html. **DIFFERENT**.
   - **S118** — lane L138: "Git のガベージコレクションについて (Qiita, koseki)", https://qiita.com/koseki/items/f1af58f1ec1693f0536a. Staged L16: "On the resemblance and containment of documents", https://doi.org/10.1109/SEQUEN.1997.666900. **DIFFERENT**.
   - **S119** — lane L139: "Git 仓库瘦身全攻略 (CSDN, weixin_33940469)", https://bbs.csdn.net/weixin_33940469/article/details/100327798. Staged L17: "git-fetch(1), Chinese edition", https://git-scm.com/docs/git-fetch/zh_HANS-CN. **DIFFERENT**.

   Result: 0 of 11 are the same document, so a verbatim append would bind 11 ids to two documents each. Every staged row S109–S119 would have to be renumbered from S120, or dropped.

2. **Six of the eleven colliding staged rows duplicate lane documents under shifted ids** (E4):

   | staged | lane | document |
   |---|---|---|
   | S112 | S115 | git-count-objects |
   | S113 | S116 | git-fsck |
   | S114 | S117 | git-prune |
   | S115 | S111 | mv |
   | S116 | S110 | rename |
   | S117 | S114 | statx |

   For these, renumbering is the wrong fix: the document already has a lane id, so the staged row is a duplicate of an existing lane row, not a new source. Only staged S109, S110, S111, S118 and S119 have no lane counterpart by URL.

3. **Same-document rows outside the colliding range.** Staged S125 (statx) matches lane S114, S126 matches S113, S137 matches S112, S138 matches S118, S139 matches S119, S143 matches S042/S057, S169 matches S002/S063, and S170 matches S001. Staged S126 and S138 are also in the quarantine slice (`.ufo/waves/round-24/assimilation/quarantine-slice`), which overlaps the collision set at S114 and S118.

4. **Next free lane id: S120.** It is the lane maximum S119 plus 1, and no lane row carries S120. However, staged S120 already exists: L18, "Git の内部 - メンテナンスとデータリカバリ (Pro Git, Japanese edition)". Any appended row must be numbered from the lane maximum and never keep its staged id.

5. **The guard is proven but changes nothing on today's data.** The frozen pattern catches 2- and 3-space-indented rows (E2), but both registries have 0 indented id rows (E3). The 119 and 134 counts are therefore identical under either pattern; the guard only protects against future indentation drift.

## Attack log
- A1 (calibration of the duplicate check, not the frozen counter): URL equality is a lower bound [INFERENCE]. It cannot see the 5 lane and 34 staged URL-less rows, such as own-work lane S109. It uses only the first URL, so a document served from a mirror under a different URL would be missed. A finding of no counterpart for staged S109/S110/S111/S118/S119 is not proof that the document is new.
- A2 (frozen pattern edge cases, tested only in part): a tab-indented row (`\t| S1xx`) is not caught. This is consistent with CommonMark, where a tab counts as 4 spaces and starts a code block. A column-zero `| S1xx |` line inside a fenced ``` block would be counted as a registry row. This was not tested; the claim rests on the regex form alone [INFERENCE].
- A3: the quarantine-slice line `S118\`   the cited source could not be fetched…` has a stray backtick after the id and no `payload-absent` token, unlike the other 7 lines (`cat -A`). A consumer that splits this file on the backticked token could mis-parse S118. I did not edit it.

Tools installed: none. Scratch `/var/tmp/souji-r24-ScoutCollisionMap/` was removed at the end of the run. No lane or shokuknow writes besides this report.
