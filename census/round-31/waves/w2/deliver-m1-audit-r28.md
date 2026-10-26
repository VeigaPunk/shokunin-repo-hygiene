# M1 audit — round-28 carry (19 entries) at c6108301cbf0ca0ad086ff0ece6b76adad6b74b6

Seat SwarmCritic26, round 31 wave 2, lane base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc.
Landed section: `corpus/lessons/round-28.md:54-82` (append-only `## Seat-reported failures`).
Lane tip read: 2c16d018e40db7c23420a2c3bb546b52957bcc25.

Method: parse each bullet, compare the quoted STATUS span byte-wise to the committed report at the
cited path:line at c6108301; then re-derive each disposition from git (commit stat + diff hunks) and
from the tip state. Commands run read-only against the lane, from a scratch clone/dir with origin removed.

## Verdict table

| # | report:line | STATUS | disposition | quote | verdict |
|---|---|---|---|---|---|
| 1 | SwarmCritic42.md:4 | FAIL | open | exact | OK (reason inaccurate) |
| 2 | SwarmCritic43.md:2 | FAIL | resolved@765fe8b | exact | WRONG-RESOLVED (partial) |
| 3 | SwarmCritic45.md:2 | PARTIAL | open | exact | OK |
| 4 | SwarmExecutor10.md:2 | PARTIAL | resolved@765fe8b | exact | OK |
| 5 | SwarmExecutor12.md:2 | PARTIAL | resolved@765fe8b | exact | OK |
| 6 | SwarmExecutor13.md:2 | PARTIAL | resolved@765fe8b | exact | WRONG-RESOLVED (partial) |
| 7 | SwarmExecutor19.md:2 | PARTIAL | resolved@765fe8b | exact | OK |
| 8 | SwarmMutationTester47.md:2 | PARTIAL | open | exact | SHOULD-BE-RESOLVED |
| 9 | SwarmMutationTester49.md:2 | PARTIAL | open | exact | SHOULD-BE-RESOLVED |
| 10 | SwarmReviewer31.md:4 | PARTIAL | resolved@ed270c4 | exact | OK (duplicate pin survives) |
| 11 | SwarmReviewer32.md:2 | PARTIAL | resolved@765fe8b | exact | OK |
| 12 | SwarmReviewer33.md:2 | PARTIAL | open | exact | OK (second half unaddressed) |
| 13 | SwarmReviewer35.md:2 | PARTIAL | resolved@765fe8b | exact | OK |
| 14 | SwarmReviewer37.md:2 | PARTIAL | resolved@765fe8b | exact | WRONG-RESOLVED |
| 15 | SwarmReviewer38.md:2 | PARTIAL | resolved@765fe8b | exact | OK (r26 receipt rc=1) |
| 16 | SwarmReviewer39.md:5 | PARTIAL | open | exact | OK (reason contradicted at :49) |
| 17 | SwarmScribe22.md:2 | PARTIAL | resolved@691dd29 | exact | OK (live-S215 detail false) |
| 18 | SwarmScribe27.md:2 | PARTIAL | resolved@fec846d | exact | OK (pinned r26 line non-reproducible) |
| 19 | SwarmSentinel61.md:2 | PARTIAL | resolved@ed270c4 | exact | OK |

Counts: OK 14, WRONG-RESOLVED 3, SHOULD-BE-RESOLVED 2, MISQUOTED 0. Quotes: 19/19 byte-equal to the
whole cited line (no prefix/suffix omitted, no escaped pipe).

## Quote exactness (all 19)

Each bullet's quoted span equals the full text of the cited line; prefix and suffix are empty strings
(`line.split(quote)` → `("", "")`). Confirmed by re-reading every report blob at c6108301 and by the
committed line lengths (e.g. SwarmCritic42:4 = 223 bytes, SwarmReviewer31:4 = 396 bytes).

Coverage of the STATUS set: 68 reports committed at `census/round-28/waves/w1/`; 19 carry a non-PASS
STATUS line; the 19 carried (path, line) pairs equal that set exactly (0 missing, 0 extra).

## Per-entry evidence

1. **Critic42** — quote exact; `open` holds (frozen C2 target still missed, 139 vs 138). Reason
   "the two intrinsic C2 defects stand" is refuted: the round-28 gate checker over the committed
   entries and snapshots at 765fe8b returns `entries=2 ok=2` (scratch root built with
   `git archive 765fe8b corpus/SOURCES.md corpus/knowledge/origin-record-*-r28.md census/round-28/sources`;
   output `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=1` — the `fail=1` is `slice-missing`
   because my scratch root stages no slice; check1-check5 are what this evidence claims),
   and the landed Gate quotes are present in the whitespace-squashed snapshot bytes (open.html,
   rename.html, fsync.html: all True), while the rejected draft quotes are absent from the same bytes.
   The Residuals entry (`corpus/lessons/round-28.md:39`) records the 138-target miss and the 6/6
   literal, not the two defects the carry names.
2. **Critic43** — `resolved@765fe8b` is real for the instrument (`tools/souji-wave-evidence-capture.sh`,
   203 added) and both receipt trees (`census/round-26/waves/manifest.sha256` 1382 lines,
   `census/round-27/waves/...`). The residue clause is scope-substituted: `git diff --name-only
   765fe8b^ 765fe8b -- .ufo` returns 0 paths, so the named commit contains no r26 restoration; the
   cited range `0c96332..1b81136` under `.ufo/waves/round-26` is empty only because no commit ever
   touched those paths (`git log --oneline 0c96332..2c16d018 -- .ufo/waves/round-26` → 0 commits;
   `git diff --name-only 50443f5 2c16d018 -- .ufo/waves/round-26` → 0 files). Separately, the receipt
   the commit lands does not verify from its own bytes: `sha256sum -c census/round-26/waves/manifest.sha256`
   at 765fe8b → 1228 OK, 152 "FAILED open or read", 2 improperly formatted, rc 1 (tree d246d803,
   identical at ed270c4/691dd29/tip). r27 verifies: 124/124 OK, rc 0.
3. **Critic45** — no per-claim no-op failure receipt exists for round 28 at tip (`git grep` for
   `L2 floor`/`no-op failure` returns only the carry text and round-31 per-claim controls). `open` OK.
4. **Executor10** — both F4 entries exist at 765fe8b with `ground: F4` (`origin-record-exclusivity-r28.md:5`,
   `origin-record-durability-r28.md:4`). OK.
5. **Executor12** — `census/round-28/records/searchlog-draft.md` committed at 765fe8b; its two prose
   blocks are spliced into `corpus/SOURCES.md` (`:172` F4 primitives, `:174` S119 re-open). The STATUS
   also names C1/C2/C3 completion, which the disposition does not address (and C2 did not complete,
   see entry 1). OK for the delivered part.
6. **Executor13** — `.gitignore` created at 765fe8b with exactly the three named lines; the tracked
   r26 restoration is not in that commit (0 `.ufo` paths in its diff) and exists in no commit.
   Wrong attribution for the restoration half.
7. **Executor19** — lesson at 765fe8b carries `## Gate` (:3), `## Findings` (:18), `## Receipts` (:24),
   `## Mistakes` (:31), `## Residuals` (:37), `## Wave` (:43), all populated, no placeholder tokens. OK.
8. **MutationTester47** — the 10 baseline `LG-SEAT-UNCARRIED` findings existed at the seat's pristine
   projection rev; at the tip the round-28 gate returns `findings=0` (tip tool) and this very section
   names all 19 non-PASS reports, including those baseline findings. The reason "never named, so they
   stay uncarried" is refuted by the section itself. Disposition should move to resolved-at-M1.
9. **MutationTester49** — `census/round-30/records/d3-green-r28-wave-evidence-capture.txt` (commit
   df6afe8) records the same fixture path running green: `case-4: PASS (special file refused rc=3 rc=3)`,
   `cases=15 pass=15 control=TAMPER-REJECTED`, `rc=0`; the fixture was rewritten at b862007. The claim
   that the symlink-control failure "has no recorded resolution" is false.
10. **Reviewer31** — ed270c4 replaces the S215 row pin; the new value is the 64-hex
    `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`, equal to the sha256 of the
    committed `census/round-28/sources/git-fetch-zh-HANS-CN.html`. The same page's pin in the search
    prose (`corpus/SOURCES.md:187`) still carries the 65-hex garbled form
    (`...f1811a1abd...`) at tip, so "the S215 pin now reads <hash>" is true of one of two occurrences.
11. **Reviewer32** — the two entries are committed at 765fe8b with `## Gate` (:44 in both), ids remapped
    to S212/S213/S214, and `census/round-28/sources/fsync.html` committed with sha256 `5c2975ab...`;
    the entries return `entries=2 ok=2` on the round-28 gate checker. OK.
12. **Reviewer33** — verified at tip: `census/round-28/sources/SHA256SUMS` lists only open.html,
    rename.html, fsync.html; `git-fetch-zh-HANS-CN.html` is committed in the same directory but unlisted.
    The STATUS's second half (disposition quote not an exact transcription) is untouched by the carry and
    the tsv is unchanged since 765fe8b; `open` remains right for both halves.
13. **Reviewer35** — rows S212/S213/S214 are added at 765fe8b (`corpus/SOURCES.md` hunk) and both entries
    cite them on their `source:` lines. OK.
14. **Reviewer37** — the entry concedes "the revert itself left no commit". The seat's missing item was
    the capture/revert evidence; capture is committed, the revert has no committed trace, and the cited
    `0c96332..HEAD` diff is structurally empty (no commit in the range touched `.ufo/waves/round-26`), so
    it cannot evidence a worktree revert. `resolved` overstates.
15. **Reviewer38** — `census/round-26/waves` and `census/round-27/waves` are committed at 765fe8b with
    manifest.sha256 and summary.tsv (r27 verifies 124/124). The r26 manifest does not verify from the
    same commit (152 unreadable, rc 1), which the lesson Residual at :40 and the R29 corrections record;
    the disposition states presence only, so it is honest but hides that the receipt refuses verification.
16. **Reviewer39** — the Gate/Mistakes splice landed at 765fe8b. The reason "the lesson body still states
    no counting command of its own" is contradicted by `corpus/lessons/round-28.md:49`, which states
    `python3 -B census/round-29/c2-counter.py ... → SUMMARY manifests=3 failed=152 uncovered=14 ...`; only
    the "of its own" (for the round-28 claim) reading survives. `open` is defensible under that reading.
17. **Scribe22** — 691dd29 adds only `corpus/lessons/round-28-verifier-spotcheck.md` (126 lines). It
    re-fetches POSIX live (S212 `57b77091...`, S214 `5c2975ab...`) and checks S215 from the committed
    snapshot (`git show fec846d:... | sha256sum`), matching the row pin. It does not re-fetch S215 live
    (no git-scm fetch in the file), so the carry's "re-fetches POSIX and S215 live" is false for S215.
18. **Scribe27** — fec846d adds `c1-after.tsv`, `c2-after.tsv`, `c3-after.tsv` and rewrites three
    SCORECARD cells. The pinned `c3-after.tsv` asserts `round26_sha256sum_check=rc0; 1380 OK`, which does
    not reproduce from the same revision's committed bytes (rc 1, 1228 OK, 152 unreadable). The record is
    a worktree measurement corrected later by the R29 append; the resolution itself holds.
19. **Sentinel61** — `census/round-28/waves/w1-results.json` is committed at ed270c4 and is byte-identical
    to the live `.ufo/waves/round-28/w1-results.json` (and to w1-spec, w1-dispatch, w1.ready, w1-run.err;
    five of five sha256 equal). The seat's path also exists on disk now. The `[WAIT]` verification itself
    (its five-item checklist) has no run record at tip; the disposition claims only that the input exists.

## Red-before/after arithmetic (control)

Base gate blob at 9f17a1e, `--round 28`:
- with `--fleet-root /home/vgpnk/Projects/shokunin`: `findings=21` (19 UNCARRIED, 2 DANGLING);
- without `--fleet-root` (the invocation printed in the carry header): `findings=24` (19 UNCARRIED,
  5 DANGLING). The three extra dangling pointers are `../.ufo/waves/hyaku/...` in `corpus/README.md:217`
  and `corpus/knowledge/jj-colocation-receipts.md:148`.
Tip gate at tip: `findings=0`; base gate at tip: `findings=2` (dangling only). M1's frozen per-round
target (UNCARRIED → 0) holds for round 28 at the tip.
