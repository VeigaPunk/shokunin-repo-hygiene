# W2Collisions — §10 id-collision re-run at ca7fc1c (registry 123 rows)

## Status
STATUS: PASS — survives. The re-run shows 15 collisions, up from 11: lane S120–S123 now collide with staged S120–S123, and all four pairs name DIFFERENT documents. Every lane S120–S123 row and citation resolves by document (URL); none resolves by staged id or by arithmetic. One report-completeness gap and two hazards are noted (Findings 5–7).

## Evidence
Revision: registry read with `git show ca7fc1cb6dd1333096c6f3bdbad304686691d126:corpus/SOURCES.md`. The bytes are identical (`cmp`) at master c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface and in the lane worktree. Staged file: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, sha256 `1510052e…f7d6`, read only. Scratch: `/var/tmp/souji-r24-W2Collisions/`, removed at the end.

The commands are exactly §10 (`/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-24.md` L415-421), with `$A` set to scratch:
```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' SOURCES.md@ca7fc1c | grep -oE 'S[0-9]+' | sort > reg-ids
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' $S/merge/souji/SOURCES.append.md | grep -oE 'S[0-9]+' | sort > staged-ids
comm -12 reg-ids staged-ids > collisions
```
Output: `123 reg-ids`, `134 staged-ids`, `15 collisions`. `uniq -d reg-ids` is empty.
sha256 of the outputs: reg-ids `c58a9a35…84d1`, staged-ids `639868f1…8277`, collisions `d77832cd…f0f1`.

Diff against the committed `.ufo/waves/round-24/assimilation/` files (committed in f9db218):
- `reg-ids`: `119a120,123 > S120 > S121 > S122 > S123`
- `staged-ids`: identical
- `collisions`: `11a12,15 > S120 > S121 > S122 > S123`

Lists (re-run):
- reg-ids (123): S001 through S123, contiguous with no gaps.
- staged-ids (134): S109 through S242, contiguous.
- collisions (15): S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123
- committed collisions (11): S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119
- new collisions (4): S120 S121 S122 S123

Guard proof (scratch registry `guard-reg.md` with rows at 2, 3 and 4 leading spaces, run through the same extractor and `comm`): output `S120 S121`. The 0–3-space rows are caught, and the 4-space row (not census-valid) is excluded, as designed.

## Findings
1. **New collisions: yes, 4, and all name different documents.** Lane rows are from `corpus/SOURCES.md@ca7fc1c` L140-143; staged rows are from `SOURCES.append.md` L18-21.

   | id | lane (ca7fc1c) | staged |
   |---|---|---|
   | S120 | "git.git path.c at tag v2.56.0 — https://github.com/git/git/blob/v2.56.0/path.c" | "Git の内部 - メンテナンスとデータリカバリ (Pro Git, Japanese edition)" (git-scm.com/book/ja/v2/…) |
   | S121 | "git.git path.c at tag v2.30.0 — https://github.com/git/git/blob/v2.30.0/path.c" | "Atlassian Support, Bitbucket Cloud, リポジトリのサイズを減らす (Japanese edition)" |
   | S122 | "git.git builtin/count-objects.c at tag v2.56.0" | "link(2) — Linux man-pages 6.19 (2026-02-08) — https://man7.org/linux/man-pages/man2/link.2.html" |
   | S123 | "git-worktree(1) § REFS — https://git-scm.com/docs/git-worktree" | "souji round-2 fixture r23-trigger-prune.sh — lanes/souji/round2/fixtures/r23-trigger-prune.sh" (own-work) |

   This is the expected consequence of append-only numbering (CORPUS.md rule 2). The §10 remedy is re-pointing by document, not avoiding the ids; `/home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-24.md` L427-428: "re-pointed **by document** — the URL/anchor is the evidence and the id follows it, never arithmetic".

2. **Lane S120–S123 are re-pointed by document, not by staged id.**
   - Every front-matter citation in the admitted entry `corpus/knowledge/count-objects-linked-worktree-garbage.md@ca7fc1c` carries the same URL as the lane row it cites. L1 reads "source: S120 — https://github.com/git/git/blob/v2.56.0/path.c"; L2–L4 give the v2.30.0 path.c, builtin/count-objects.c and git-worktree URLs; L5 cites S115, which is git-count-objects in both the entry and the lane row.
   - The `used-by` cells of lane S120–S123 list exactly this entry, plus `tools/souji-size-census.py` for S120 and S122. The tool's docstring (L30-32) describes S120 as path.c@v2.56.0 and S122 as builtin/count-objects.c@v2.56.0, which matches the lane rows.
   - The staged source entry `garbage-false-positive-modes-r27.md` L2 cites only "source: S153 — lanes/souji/round6/evidence/r27-garbage-git-versions.out", a shokuknow own-work row. The lane replaced it with the documents that row reads (path.c at v2.56.0 and v2.30.0) as lane S120 and S121. The mapping S153→S120/S121 is not a numeric shift, so it is by document.
   - The entry's Gate states this (L140): "ADMIT: staged garbage-false-positive-modes-r27, re-sourced to S120/S121/S122/S123".

3. **No lane URL came from a staged row with a colliding id.** I grepped the staged rows for each lane S120–S123 URL. Both path.c URLs (`blob/v2.56.0/path.c`, `blob/v2.30.0/path.c`) and `blob/v2.56.0/builtin/count-objects.c` match 0 staged rows. git-worktree appears in staged rows only as S230 (`https://git-scm.com/docs/git-worktree/2.56.0`, a different URL) and S231 (zh_HANS-CN). Lane S123 uses the unversioned URL, as lane S003 and S058 already do; it is a third same-URL row with a distinct § REFS scope, which follows existing lane convention.

4. **Staged S120–S123 documents are absent from the lane under any id.** Grepping lane `SOURCES.md@ca7fc1c` for `git-scm.com/book/ja`, `support.atlassian.com/ja/bitbucket-cloud/docs/reduce-repository-size`, `man2/link.2.html` and `r23-trigger-prune` returns 0 matches each. No duplicate was created. Any later adoption of these documents needs fresh ids of S124 or higher.

5. **Gap: the post-append collision count and renumber map are not yet recorded.** The committed `assimilation/collisions` (11) and preregistration.txt L130 ("Collision check: reg-ids 119, staged-ids 134, collisions 11") are the pre-append snapshot, which is correct as frozen evidence. However, no round-24 artifact at ca7fc1c or c3ca7ad records the post-append count of 15 or the by-document map. r22 did record its post-append re-run (`corpus/lessons/round-22.md` L425-427). §10 requires the report to "Paste both id lists, the collision count and the renumber map into the report". The round report or lesson should carry 123/134/15 and this map:

   | staged | lane | document |
   |---|---|---|
   | S153 | S120 | path.c@v2.56.0 |
   | S153 | S121 | path.c@v2.30.0 |
   | (none) | S122 | builtin/count-objects.c@v2.56.0 |
   | (none; S230 is a different URL) | S123 | git-worktree § REFS |

6. **Hazard: bare "S123" in round-22 lessons is now ambiguous.** `corpus/lessons/round-22.md` L298 ("Rows S123/S131/S133 quote man-page prose"), L351 and L363, and `corpus/lessons/round-22-verifier-spotcheck.md` L199 use bare `S123` to mean the staged own-work S123 (register slice). Since ca7fc1c, lane S123 is git-worktree § REFS. The same hazard already existed for S114 and S118 since r22. The lessons are append-only, so only a named correction or disambiguation note can clear it. The admitted entry itself avoids the problem: staged ids appear only in Gate prose labelled "staged" or "shokuknow" (L140, L143-145), never as `source:` citations.

7. **Hazard: the staged file is not reproducible from a shokuknow commit.** `git -C /home/vgpnk/Projects/shokuknow status` shows `M merge/souji/SOURCES.append.md`, with 41 uncommitted rows (S202–S242) compared with HEAD. The HEAD version yields 93 ids, while §10 reads the worktree file and yields 134. That count is identical to the committed staged-ids, so nothing drifted since f9db218, and S120–S123 are the same rows at HEAD. Still, the 134-id list is pinned only by the committed `staged-ids` and the sha256 above, not by any shokuknow revision.

## Attack log
- A1: Does a lane citation resolve to a staged document through a colliding id? I checked all S1xx tokens in the admitted entry: S115–S117 are the lane's count-objects, fsck and prune rows (L58, L121); S120–S123 match the lane URLs; S130/S131/S134/S141/S147/S153 appear only in Gate reject prose. Not falsified.
- A2: Were ids assigned by arithmetic (staged id plus k)? The only staged source of r27 is S153, and lane S120/S121 are not derived from it numerically. S122 and S123 have no staged counterpart. Not falsified.
- A3: Did the append duplicate a staged document already in the lane? See Findings 3–4. Not falsified.
- A4: Does the extractor false-green on indented rows? The guard fixture catches the 2- and 3-space rows. Not falsified.
- A5: Did the staged set drift since the committed scratch? The staged-ids diff is empty. Not falsified; see Finding 7 for the provenance caveat.

Tools installed: none.
