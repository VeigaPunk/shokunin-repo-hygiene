# R41scribe01 — C1 correction candidate (scribe)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Freeze HEAD: e2a74312af4233963e44e4dbb38838ece07b8bd2. Measured revision (counter MEASURED): bffcc0f660ff36eb8add3f61582748a7af019a5b.
Candidate (seat-owned, not tracked): `.ufo/waves/round-41/w1/R41scribe01/round-41.md` sha256 `e2fc776ef10123b216f9a7f8e39907ea5d218f5d185a2b8f4a3b49c11c080f1c`. Destination: `corpus/lessons/round-41.md`. Contents: the heading `## Corrections to filed round-40 statements`, three `CORRECTION` lines (I1, I3, I4), one prose line after each. No round-40 text edited.

## Frozen inputs checked

| check | command | observed |
|---|---|---|
| lane tip | `git rev-parse HEAD` | `e2a74312af4233963e44e4dbb38838ece07b8bd2` |
| items digest at freeze | `git show HEAD:census/round-41/c1-items.tsv \| sha256sum` | `2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf` (matches the pinned ITEMS_SHA256) |
| counter digest at freeze | `git show HEAD:census/round-41/c1-counter.py \| sha256sum` | `8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63` (matches prereg) |
| round-41 lesson at lane tip | `git ls-tree --name-only HEAD corpus/lessons/ \| grep round-41` | no output (file absent) |

## Re-derivations at bffcc0f (the counter's own commands and outputs)

I1 (`rows-worktree-c`; counter `derive()` counts ROW-regex rows of corpus/SOURCES.md):
- `git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -nE '^\|\s*S[0-9]{3,}\s*\|' | grep 'worktree\.c'` → rows at lines 38 (S009) and 62 (S033); count `2`.
- `git show bffcc0f…:corpus/SOURCES.md | grep -c 'v2\.56\.0/worktree\.c'` → `0`.
- Derived value: `rows=2,v2.56.0=0`. Filed "9-rows" (round-40.md line 49: "`worktree.c` appears in 9 rows of") → mismatch.
- Note for the L1: the r40 spot-check §4 says only S009 cites worktree.c; the counter's ROW count is 2 because S033's notes cell also names worktree.c. The candidate uses the counter's value (2), not the spot-check's reading.

I3 (`register-cells`):
- `git show bffcc0f…:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*'` → `register_cells=6` (line 11).
- `git show bffcc0f…:census/round-40/records/c1-after-h.txt | grep -o 'register_cells=[0-9]*'` → `register_cells=3` (line 11).
- Derived value `before=6,after=3`. Filed "like-for-like" (SCORECARD.md line 791) → mismatch.

I4 (`committed-occurrences`):
- `git grep -c -F 'flagged as potentially' bffcc0f… -- census/round-40/waves/` → no output over 136 committed files (`git ls-tree -r --name-only bffcc0f… census/round-40/waves/ | wc -l` → 136).
- Derived value `occurrences=0`. Filed anchor in LOG.md line 1909 ("provider error `…your prompt was flagged as potentially violating our usage policy`") → mismatch.

## Scoring (frozen counter via the shared harness)

Command (run once, from the fleet root, TMPDIR set explicitly):
`TMPDIR=/fast/scratch/hyaku/souji-r41/R41scribe01 bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41scribe01 corpus/lessons/round-41.md=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41scribe01/round-41.md`

Output (verbatim):
```
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0
```
Exit code: **1**. Expected per assignment: S258 is absent from the scratch clone (sourced=0), so I1 is uncorrected and corrected=2.

Diagnostic only (not evidence for C1, not a candidate): to exercise the sourced branch, I scored the same candidate with a stand-in row `| S258 | git v2.56.0 builtin/worktree.c (DIAGNOSTIC ROW ONLY, not a registry entry) | code | A | diagnostic | tag v2.56.0: builtin/worktree.c | diagnostic-only row for scoring the sourced path | mined | 2026-10-28 | on-release | - |` appended to a copy of the lane tip's corpus/SOURCES.md, passed as a second score-candidate argument. Output:
```
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
```
Exit code 0. This shows the grammar and derived values satisfy the counter once a real tier-A S258 row exists; the stand-in row was removed with its copy and is not a registry entry.

## Tooling
No tool installed or upgraded. Used only `git` (read-only: show, grep, ls-tree, rev-parse), `sha256sum`, `grep`, `score-candidate.sh`.

## Git and scratch hygiene
Every git call was read-only. No commit, push, or mutating git/jj command was run in the lane or the fleet. The score harness committed only inside its own scratch clone and removed it on exit (scratch directory listing after the run: empty). The diagnostic SOURCES copy and the scratch dir `/fast/scratch/hyaku/souji-r41/R41scribe01` were deleted before yield.

## Verdict
- Candidate built and scored: `SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0`, exit 1. The I3 and I4 lines validate; the I1 line does not validate in this scratch clone because S258 is absent. Target (corrected=3 sourced=1) is met only when the other seat's S258 row lands with the candidate.
- C1 status from this seat: candidate ready; claim not measured (the L1 lands and measures).
- Routing: L1 must land S258 (tier A, mined, opened 2026-10-28, cells naming v2.56.0 and worktree.c) together with `corpus/lessons/round-41.md`, then re-score at the landed tip.
