# R41w2executor06 — independent C1 supplement (judged on calibration)

Tip `1d41c13574db80fdd9a4bde490b712da7ce2a85f`, base `bffcc0f660ff36eb8add3f61582748a7af019a5b`. Read-only against the lane; helper at
`.ufo/waves/round-41/w2/R41w2executor06/c1-supplement.py` (reads git objects only). Receipts: `R41w2executor06/run-tip.txt`, `R41w2executor06/run-broken.txt`.

## Commands and output
1. `python3 -B .../c1-supplement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f` (EXIT=0):
```
PASS K1-corrections-fence-dup outside=3 inside_fence=0 ids=I1,I3,I4 dup_ids=- dup_text=0 unclosed_fence=False
PASS K2-sources-insert-only old_lines=300 new_lines=304 inserted_lines=4 unmatched_old_line=- tail_append=False
PASS K3-S258-row-quote-sha cells=11 quote_occurrences=1 sha_match=True snapshot=census/round-41/sources/git-v2.56.0-builtin-worktree.c
PASS K4-r40-files-prefix corpus/lessons/round-40.md=prefix SCORECARD.md=prefix LOG.md=prefix
SUMMARY checks=4 pass=4 fail=0 rev=1d41c13574db80fdd9a4bde490b712da7ce2a85f
```
2. Broken input A (scratch clone, commit 13c6a92: CORRECTION I3 duplicated, I4 wrapped in a code fence, S033 row edited in place) — EXIT=1:
   `FAIL K1 ... inside_fence=1 ids=I1,I3,I3 dup_ids=I3 dup_text=1`; `FAIL K2 ... unmatched_old_line=62`; K3/K4 PASS; `SUMMARY checks=4 pass=2 fail=2`.
3. Broken input B (commit 83fe794: `X` prepended to round-40.md, SCORECARD.md word edited, S258 quote "older"->"newer" and row sha last hex char changed) — EXIT=1:
   `FAIL K3 ... quote_occurrences=0 sha_match=False`; `FAIL K4 ... round-40.md=BROKEN SCORECARD.md=BROKEN LOG.md=prefix`; K1/K2 PASS; `SUMMARY checks=4 pass=2 fail=2`.
4. Unresolvable rev: `REFUSAL COULD-NOT-EVALUATE`, EXIT=2. Tip re-run after the broken runs: identical to (1).

## Finding (calibration)
- K1 (3 CORRECTION lines, none fenced, none duplicated), K3 (11 cells, quote occurs once in the snapshot, sha256 of the committed snapshot == the row's stated `af2bd523…babc`) and K4 hold at the tip.
- **Wording defect:** the landed lesson (N2) and the "pure append" framing say the registry change is a "pure append". K2 as first written (old bytes an exact prefix of new) FAILED at the tip: first differing line 212. `git diff bffcc0f..1d41c13 -- corpus/SOURCES.md` shows 4 insertions at two places: the S258 table row after S257 (line 212) and a blank + "Round-41 bounded source search" + blank block in the Search log (before `## Leads`, ~line 286-289). No old line changed or removed, but it is not an end-of-file append (`tail_append=False`). I redefined K2 as insert-only (every old line byte-identical and in order, old file ended in newline), which is the property the task and N2 intend; it passes. A prefix-based append check would wrongly fail the honest landing.
- Limit: K2 uses greedy subsequence matching, so it cannot say where blank-line insertions sit, and it does not detect a reordering that preserves a subsequence only via duplicated lines. K3 verifies the quote's presence in the snapshot, not that the quote's stated line (:255) matches; it also does not cross-check the lesson's Gate table or SHA256SUMS (both agree by eye: same sha).

## Verdict
Landed C1 artifacts: all four independent checks PASS at the tip (K2 under the insert-only reading; "pure tail append" is false and the filed wording should say "insert-only"). Instrument shown able to fail on both broken inputs (4 distinct FAILs) and to refuse an unresolved rev. Scratch removed; no tracked file touched.
