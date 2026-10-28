# R41critic01 — attack on the frozen C1 counter (round 41)

Seat: R41critic01 (critic, leaf). Lane tip scored: `e2a74312af4233963e44e4dbb38838ece07b8bd2`.
Frozen counter `census/round-41/c1-counter.py` sha256 `8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63` (matches the pinned digest in `preregistration.txt`). Population `census/round-41/c1-items.tsv` sha256 `2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf` (matches pin). No frozen file was edited. Nothing was committed or landed.

## Verdict

**The counter can be fooled.** Six candidate lessons (A1-A6) and a registry variant (A8) each make `score-candidate.sh c1` print the target `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` with exit 0, while their prose does not truthfully correct the filed statements or their S258 source is not a source. The derived numbers themselves are correct (independently recounted, §3), so the failure is in what the counter does not look at: prose, fences, row provenance, and malformed lines.

The counter's kill condition "any junk line" is not enforced for malformed `CORRECTION` lines (A5), because the frozen `LINE` regex silently skips any line that does not match the full form.

## 1. What the counter actually checks (read from the frozen source)

- `LINE = ^CORRECTION (\S+) file=(\S+) filed=(\S+) derived=(\S+) rev=(\S+) source=(\S+)\s*$` — whole-line, no leading or trailing text, no bullet. The scan is over every line of `corpus/lessons/round-41.md` at the rev; **fences are not parsed**.
- A line *corrects* an item if it matches and id, file, claimed token, derived value (its own derivation at the pinned MEASURED `bffcc0f6…`) and rev all equal. Duplicates are fine (`corrections` is a list).
- `junk` counts only lines that **match `LINE`** and fail the same test. Non-matching lines are never counted.
- I1 only: `sourced` requires some `source=S###` to point at a registry row at the candidate rev with exactly 11 cells, tier `A`, status `mined`, opened `2026-10-28`, and the substrings `v2.56.0` and `worktree.c` in cell 1 or cell 5. `sourced` does **not** check URL, quote, existence, or that the row is not a placeholder. It takes the **first** matching `S258` row and does not look inside code fences.
- `rewritten` covers only the three item files (append-only and anchor present). `corpus/SOURCES.md` is not append-only-checked. [INFERENCE from code reading; not exercised.]
- `derive` reads MEASURED only, so no candidate can change a derived value. Candidate SOURCES.md edits cannot move `rows=`.

## 2. Attacks run

Every run used `bash census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41critic01 <dests>` from the lane. Candidate sources are in this seat directory (`.ufo/waves/round-41/w1/R41critic01/`). Scratch was removed afterward.

Base lesson template (`L-A1-vacuous.md`) has the three exact correct lines:
```
CORRECTION I1 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=S258
CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-
CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-
```

Vacuous registry row (`S258-vacuous-SOURCES.md`, base `corpus/SOURCES.md` at tip with the row inserted after S257 at line 212; the row is 11 cells, verified by `awk -F'|' NF=13`):
```
| S258 | git v2.56.0 builtin/worktree.c — NOT OPENED, placeholder with no URL | code | A | v2.56.0 worktree.c | placeholder; nothing fetched, no quote located | the v2.56.0 worktree.c prune gate exists | mined | 2026-10-28 | on-release | corpus/lessons/round-41.md |
```

| # | Candidate (seat file) | Dests | Counter output (verbatim SUMMARY) | rc | Verdict |
|---|---|---|---|---|---|
| A0 | `L-A0-norow.md` (honest lines, no S258 row) | lesson | `SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0` | 1 | negative control: the sourced gate bites when no row exists |
| A1 | `L-A1-vacuous.md` + `S258-vacuous-SOURCES.md` | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | **FOOLED**: the row self-declares "NOT OPENED" and still passes |
| A2 | `L-A2-prose.md` + vacuous SOURCES | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | **FOOLED**: prose says "the filed statement … stands … the lines below are bookkeeping, not a retraction" |
| A3 | `L-A3-fence.md` + vacuous SOURCES | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | **FOOLED**: the three lines sit in a ```` ```text ```` fence; prose says "No correction is applied in this round" |
| A4 | `L-A4-dup.md` (A1 lesson twice) + vacuous SOURCES | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | duplicates accepted (`corrections=2` per item) |
| A5 | `L-A5-malformed.md` + vacuous SOURCES | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | **FOOLED, junk kill not enforced**: contains `CORRECTION I4 … derived=occurrences=5 … source=- (filed text stands)` (trailing text → no regex match), a leading-space `  CORRECTION I1 … derived=rows=9,…` and a bulleted `- CORRECTION I3 … derived=before=9,after=3`; all three are invisible to `junk` |
| A6 | `L-A6-combined.md` + vacuous SOURCES | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | **FOOLED** (all of the above at once; the three correct lines appear fenced and unfenced, with "filed text stands" prose and malformed wrong lines) |
| A7 | `L-A7-wellformed-wrong.md` (A0 lesson + well-formed `CORRECTION I4 … derived=occurrences=5 … source=-`) | lesson | `SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=1 rewritten=0 sourced=0` | 1 | control: a *well-formed* wrong line is counted as junk, so A5's pass is caused by the regex skipping malformed lines, not by junk detection working |
| A8 | `L-A0-norow.md` + `SOURCES-A8-fenced-row.md` (S258 row only inside a ```` ```text ```` block appended at end of SOURCES.md) | lesson + SOURCES | `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` | 0 | **FOOLED**: a row that no Markdown renderer shows as a table row still satisfies `sourced` |

Commands (exact, run from the lane): `bash census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41critic01 corpus/lessons/round-41.md=.ufo/waves/round-41/w1/R41critic01/L-A1-vacuous.md corpus/SOURCES.md=.ufo/waves/round-41/w1/R41critic01/S258-vacuous-SOURCES.md` (and the same shape for each row above; the full batch is listed in the transcript and the candidate files are in this directory). `TMPDIR` was set to the scratch root for every call.

Every run printed three `ITEM … corrections=N intact=yes` lines before its SUMMARY. For A1-A6 and A8 all three items show `corrections>=1`; for A0 and A7 (no S258 row) I1 shows `corrections=1` but is not counted as corrected, so the SUMMARY reads `corrected=2 … sourced=0`.

## 3. Independent recount of the derived values (to separate "wrong number" from "wrong prose")

Run at `bffcc0f660ff36eb8add3f61582748a7af019a5b` (MEASURED):
- `git show bffcc…:corpus/SOURCES.md | grep '^| S' | grep -c 'worktree\.c'` → `2`; the same with `v2\.56\.0/worktree\.c` → `0`. Matches `derived=rows=2,v2.56.0=0`. The filed "9 rows" is wrong.
- `census/round-40/records/c1-before.txt` → `register_cells=6`; `c1-after-h.txt` → `register_cells=3`. Matches `derived=before=6,after=3`.
- `git grep -h 'flagged as potentially' bffcc… -- census/round-40/waves/ | wc -l` → `0`. Matches `derived=occurrences=0`.

So the counter's three derived values are correct. Every fooling candidate above carries the correct derived values; what is wrong in them is the prose claim (A2, A3, A6 say the filed text stands) and the source (A1, A2, A3, A5, A6, A8 cite a row whose cells say "NOT OPENED" or sit in a fence).

## 4. Named limits for the L1 (not edited; frozen)

1. **Prose is unchecked.** A CORRECTION line can be accompanied by text asserting the filed statement still stands (A2, A6); the counter reports `corrected=3`. The predicate "CORRECTION lines carry the counter's own derived value" is met with a lesson that retracts nothing.
2. **Fences are not excluded.** CORRECTION lines inside a fenced code block count (A3, A6).
3. **Malformed lines bypass `junk`.** A line with trailing text, leading whitespace, or a bullet is not matched by `LINE` and is never counted, though the kill condition says "any junk line" (A5). A7 shows the same wrong content, well-formed, is counted.
4. **S258 provenance is substring-only.** `sourced` checks eleven cells, tier `A`, status `mined`, date, and two substrings. A placeholder "NOT OPENED" row passes (A1). A fenced row passes (A8). First-match is used if duplicated (not separately exercised).
5. **`rewritten` does not cover `corpus/SOURCES.md`.** [INFERENCE from code, not exercised]. The registry's append-only rule (`SOURCES-CONTRACT-v1`) is not enforced by C1.

Consequence for the claim: the C1 target `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1` is reachable by a lesson that does not correct the three filed statements truthfully. The counter measures the presence of the correct *numbers* in a *pattern*, not calibration.

## 5. Scope and hygiene

- No frozen file edited; no commit, push, or mutating git in the lane or fleet; no `jj`. The only git calls were read-only (`git show`, `git grep`, `git cat-file`, `git rev-parse`, `git ls-tree`, and the frozen scorer's own clone).
- Candidate files are under `.ufo/waves/round-41/w1/R41critic01/` only. Largest is the 150 KB `S258-vacuous-SOURCES.md` (well under 50 MB).
- Scratch `/fast/scratch/hyaku/souji-r41/R41critic01/` removed (`rm -rf`; verified gone). The scorer's own per-run clone was removed by its trap.
- No tool was installed or upgraded. No pacman transaction. No process was signalled.
- No subagent was dispatched (leaf).
