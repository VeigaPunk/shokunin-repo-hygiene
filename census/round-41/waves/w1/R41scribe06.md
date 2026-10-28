# R41scribe06 — draft Q98 (calibration, scribe)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lane tip at measurement: `e2a74312af4233963e44e4dbb38838ece07b8bd2` (the freeze commit). Scratch used: `/fast/scratch/hyaku/souji-r41/R41scribe06` (created, used for `TMPDIR`, empty, removed before yield). Nothing committed; no mutating git or jj command run; no file outside my seat directory written.

## Inputs read
- `census/round-41/preregistration.txt` (frozen; read first, not edited).
- `corpus/QUALITY.md`: header rules (every criterion cites its lesson; supersede by a new row, never rewrite), the table header `| id | criterion | applies-to | test | lesson |`, and the last rows Q89-Q97 (last row = Q97, line 248). No Q98 existed (`grep -c Q98 corpus/QUALITY.md` = 0).
- `corpus/lessons/round-40-verifier-spotcheck.md` §4 (row S160, disagree-in-part) and §6 (R40-D-PRUNE, item 1).
- `corpus/lessons/round-40.md` line 49-50 (`## Assimilation gate`, the source of the "9 rows" reject).
- `corpus/SOURCES.md` S009 and S033 rows; `git diff --stat bffcc0f HEAD -- corpus/SOURCES.md` produced no output (SOURCES.md unchanged between the spot-check tip and the freeze tip).

## Re-run of the spot-check's cited count (commands and observed output)

| # | command (run from the lane) | observed |
|---|---|---|
| 1 | `git show bffcc0f:corpus/SOURCES.md \| grep -c 'worktree\.c'` | `3` (spot-check reported 3: reproduced) |
| 2 | `git show bffcc0f:corpus/SOURCES.md \| grep -c 'v2.56.0/worktree\.c'` | `0` (spot-check reported 0: reproduced) |
| 3 | `git show HEAD:corpus/SOURCES.md \| grep -c 'worktree\.c'` | `3` (identical at the freeze tip) |
| 4 | `git show HEAD:corpus/SOURCES.md \| grep -n 'worktree\.c' \| cut -c1-60` | `38:` (S009 row), `62:` (S033 row), `240:` (round-40 negative note in the notes section) |
| 5 | `git show HEAD:corpus/SOURCES.md \| grep '^\| S[0-9]' \| grep -c 'worktree\.c'` | `2` (S-id rows S009 and S033 only) |
| 6 | `git show HEAD:corpus/SOURCES.md \| grep -no '.\{0,40\}worktree\.c.\{0,30\}'` | line 38: `builtin/gc.c, worktree.c, run-command.c` and `worktree.c:954-956, :1001-1008` (both in S009); line 62: S033 `although worktree.c ages by it` (prose mention, not a source row); line 240: `worktree.c:1001-1008`@v2.55.0 (notes) |
| 7 | `git show HEAD:corpus/SOURCES.md \| grep '^\| S009' \| grep -o '.\{0,80\}\(recheck\|pending\|v2\.56\).\{0,80\}'` | no output: the S009 row pins `v2.55.0` only and its recheck column reads `on-release`; no v2.56.0 pending-recheck text in the lane |

Verdict on the cited count: **reproduced** (3 lines, 0 at v2.56.0). The "9 rows" statement at `corpus/lessons/round-40.md:49` is **not reproduced** under any scope: 3 lines contain the string, 2 S-id rows contain it, 1 row (S009) cites `worktree.c` as a source file, and that row is pinned at v2.55.0, not v2.56.0.

Caveats on the spot-check's wording (calibration, reported not fixed):
- Spot-check §4 says S033/S058/S232 "match as worktrees pages". Measured: S033 matches only as a prose mention of `worktree.c`; S058 and S232 contain no `worktree\.c` substring (they match `worktree` in other forms, which the count does not use).
- Spot-check §4 says "S009 … carries a pending-recheck note for v2.56.0". Measured: no such text in the lane's S009 row (command 7). The staged S160 text is outside the lane; I did not locate the staged `fleet-prune-safety-r28.md` in the fleet paths I searched (`find` for the name returned nothing; the only `SOURCES.append.md` found is `tsukuroi-shokunin/.ufo/waves/round-37/assimilation/SOURCES.append.md`, which has no `S160` or `worktree.c` line). The v2.56.0 re-pin wording therefore remains unverified by me.

## Why the count matters for Q98 (scope, not only filename)
`worktree\.c` as a regex also matches `worktree.config` (a real git config name). No such literal occurs in SOURCES.md at the tip (command 4 shows only the three lines above), so this is a hazard for the criterion, not an observed miscount. The observed scope problem is command 5 vs command 1: a substring count mixes file-of-record rows (S009) with prose mentions (S033, the notes line 240). Q98 therefore requires the rationale to state which kind it counted.

## Deliverable
- Draft row: `.ufo/waves/round-41/w1/R41scribe06/Q98.md` (one line, 5 cells, verified by `awk -F'|'` = 5 cells, 1 line). Criterion: an "already held" reject must cite a re-runnable count with its command and revision, must name the held row's tag beside the candidate's tag (a newer tag is a freshness gain, not a duplicate), and must say whether the count is file-of-record or prose. Lesson cell: `corpus/lessons/round-40-verifier-spotcheck.md` section 6 R40-D-PRUNE (and section 4 S160 row); `corpus/lessons/round-40.md` `## Assimilation gate` line 49.
- `corpus/QUALITY.md` was not edited (QUALITY rows are landed by the L1 through `jj-lane.sh`).
- Scoring: `census/round-41/score-candidate.sh` accepts only `c1|c2|c3|r1` and has no QUALITY counter; the draft is therefore **not scored by any frozen counter**. Its test column is a checklist for the L1, not an executed check.

## Tooling
None installed, updated or removed.

## Verdict
- Re-run of the spot-check's count: **reproduced** (3; 0 at v2.56.0), with commands and output above.
- The "9 rows" reject ground: **not reproduced** (3 lines / 2 S-id rows / 1 file-of-record row at v2.55.0).
- Q98 draft: **written** as one QUALITY-grammar row; **not landed, not scored by a frozen counter**.
- Two spot-check wording points are imprecise or unverified (above); they are reported here and not corrected in the lane.
