STATUS: DONE — independently checked all seven round-16 carries; each is an unmarked cut at the source’s first physical line.

# Findings

Axis: calibration. I compared the seven lesson entries with the STATUS paragraphs at commit `6ff91f5` (`6ff91f534eece9adde5f667cb7dad400c145351b`). In every case, the lesson quote ends exactly where the source’s first physical line ends, the next source physical line continues the same paragraph, and the lesson quote has no ellipsis before its closing quote. None is a complete paragraph carry or an ellipsis-marked cut.

| Lesson line | Source STATUS paragraph (first physical line; then its continuation) | Exact end of lesson quote | Classification |
|---|---|---|---|
| 73 | `.ufo/waves/round-16/w2/ReopenS048.md:102` ``STATUS: PARTIAL — S048 fails narrow cell support (scope "parse error"; `(S043)` stretched over``<br>`:103` ``shellcheck output; anchor unpinned) while `rejected` / `365d` / `used-by —` hold.`` | `stretched over` | Unmarked cut |
| 74 | `.ufo/waves/round-16/w2/RerunGateFixture.md:12` ``STATUS: PARTIAL — both required executions reproduce (real gate 15/15 PASS, exit 0; null-stub``<br>`:13` ``run exit 1 with 14/15 FAIL), but the fixture's own vacuity case (F1) is tautological — it`` | `null-stub` | Unmarked cut |
| 78 | `.ufo/waves/round-16/w2/RerunSeatAudit.md:157` ``STATUS: PARTIAL — selftest, transcript coverage and the 3173-call census hold exactly, and the``<br>`:158` ``single major holds as an attempted (failed) out-of-scope edit; the 19-minor figure is not`` | `and the` | Unmarked cut |
| 79 | `.ufo/waves/round-16/w2/RevCensusStatusFinal.md:359` ``STATUS: PARTIAL — core operability holds (bound filters never execute;``<br>`:360` ``protected reaches refuse; unmeasurable status never becomes a false count or a`` | `(bound filters never execute;` | Unmarked cut |
| 82 | `.ufo/waves/round-16/w2/RevengeSeatViolations.md:260` ``STATUS: FAIL — the wave-1 audit's published disposition is wrong: 4 of its 20 rows are not violations``<br>`:261` ``(two exact-file greps, one bounded file-glob, one aborted `write()`), 1 is unestablished, and only 1 (the`` | `are not violations` | Unmarked cut |
| 83 | `.ufo/waves/round-16/w2/ScoutLsFilesPathspec.md:179` ``STATUS: PARTIAL — F2 is a real nested-layout gap in the exclusion set for both consumers``<br>`:180` ``(`ls-files`→`check-attr` and tracked-entry `status` filtering); one extra`` | `both consumers` | Unmarked cut |
| 84 | `.ufo/waves/round-16/w2/ScoutOptionalPrefix.md:238` ``STATUS: FAIL — census strips `:(optional)` for `core.worktree`, which git parses literally``<br>`:239` ``(`setup.c:597` `xstrdup`); `souji-census.sh:660` can abort the whole run on a benign config and, for`` | `parses literally` | Unmarked cut |

# Evidence

- `git ls-tree -r --name-only 6ff91f5 -- corpus/lessons/round-16.md` and the seven source paths confirmed that all eight blobs exist at the pinned commit.
- Pinned-blob `git show -L` excerpts for each source STATUS line and its continuation, and for lesson lines 73–74, 78–79, and 82–84, showed the exact physical-line boundaries and quote endings above.
- Observed: all seven quoted ends equal the source first-line ending; each has substantive same-paragraph text on the next source line. Classification is therefore seven unmarked cuts, with zero complete carries and zero ellipsis-marked cuts. Confidence: high. Unresolved gaps for these seven comparisons: none. This finding does not assess gate implementation or replay behavior.

# Commands run

`git ls-tree -r --name-only 6ff91f5 -- corpus/lessons/round-16.md .ufo/waves/round-16/w2/ReopenS048.md .ufo/waves/round-16/w2/RerunGateFixture.md .ufo/waves/round-16/w2/RerunSeatAudit.md .ufo/waves/round-16/w2/RevCensusStatusFinal.md .ufo/waves/round-16/w2/RevengeSeatViolations.md .ufo/waves/round-16/w2/ScoutLsFilesPathspec.md .ufo/waves/round-16/w2/ScoutOptionalPrefix.md`

Pinned-blob `git show` of the lesson and seven named reports; targeted excerpts used `git show -L` for source lines 100–105, 10–15, 155–160, 357–362, 258–263, 177–182, 236–241, and lesson lines 73–74, 78–79, 82–84. No execution, network access, installation, or scratch files.

# Contract compliance

Leaf seat; no delegation or peer messages. Git evidence was read only with `git show`/`git ls-tree`. No lane file was changed except this requested report. No tools were installed or updated.
