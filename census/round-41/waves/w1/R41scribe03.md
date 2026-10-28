# R41scribe03 — C1 correction block (scribe)

Seat: R41scribe03 (role scribe, round 41 wave 1). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Frozen instruments at `6682b98175b995ee4646ffd1ea6bd8a12cd353dd` (prereg). Measured revision `bffcc0f660ff36eb8add3f61582748a7af019a5b`.

## Deliverable

- Candidate: `.ufo/waves/round-41/w1/R41scribe03/round-41.md` (2172 bytes). Contains only `## Corrections to filed round-40 statements`, three `CORRECTION` lines (I1, I3, I4) and one prose paragraph per item. Nothing under `corpus/` was edited; no round-40 text was edited; no git mutation was run.

## Inputs read

- `census/round-41/c1-counter.py` (full, lines 1-172): derivation at lines 71-93, `sourced()` at 96-107, grammar `LINE` at 52, `main()` at 110-168. Counter sha256 `8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63`.
- `census/round-41/c1-items.tsv` (3 rows: I1 `9-rows`/`rows-worktree-c`, I3 `like-for-like`/`register-cells`, I4 `error-text-recorded`/`committed-occurrences`). Sha256 `2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf` (matches the pinned digest).
- `census/round-41/preregistration.txt` (C1 block; target `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1 (exit 0)`).
- `corpus/lessons/round-40-verifier-spotcheck.md` §6 (routed defect R40-D-PRUNE, R40-D-C1-BEFORE) and `corpus/lessons/round-40.md` (Gate, Mistakes M40-1..M40-13 layout), `corpus/lessons/round-39.md` (Gate table and Mistakes `### Mn — title` / class / evidence pointer / captured-by / fix style).

## Re-derivation at the measured revision (commands and observed output)

All commands are read-only (`git show`, `git grep`, `git cat-file`, `ls-tree`); `-C` names the lane.

1. `git -C $L cat-file -t bffcc0f660ff36eb8add3f61582748a7af019a5b` → `commit`.
2. I1, counter's row arm (`^\| *S[0-9]{3,} *\|` rows, substring `worktree\.c`):
   `git -C $L show $M:corpus/SOURCES.md | grep -E '^\| *S[0-9]{3,} *\|' | grep -c 'worktree\.c'` → `2` (rows S009, S033).
   Same with `v2\.56\.0/worktree\.c` → `0`.
   Bare-substring count over the whole file (not what the counter uses): `grep -c 'worktree\.c'` → `3` (the third line is `SOURCES.md:240`, a prose line, not a row). The spot-check's "3 lines / 1 row" figure is this bare count; the counter's row count is 2.
   Counter's own function, imported read-only (`importlib`, `-B`, lane root), `derive(root, "rows-worktree-c")` → `('rows=2,v2.56.0=0', True)`.
3. I1 anchor: `git -C $L show $M:corpus/lessons/round-40.md | grep -n 'appears in 9 rows'` → `49:  \`worktree.c\`).** ... (\`worktree.c\` appears in 9 rows of` (present).
4. I3, `register_cells=` in the two receipts:
   - `git -C $L show $M:census/round-40/records/c1-before.txt` line 2 command: `--register census/round-39/cells.tsv`; line 11: `... register_cells=6 ...`, trailer `# counter exit: 1`.
   - `git -C $L show $M:census/round-40/records/c1-after-h.txt` line 3 command: `--register census/round-40/cells.tsv`; line 11: `... register_cells=3 ...`.
   - `derive(root, "register-cells")` → `('before=6,after=3', True)`.
   - I3 anchor: `SCORECARD.md:791` `| C1 evidence-bound closures + strict-descendant register | calibration 7 | ...` (present).
5. I4, `derive(root, "committed-occurrences")` → `('occurrences=0', True)`. Shell check: 136 committed files under `census/round-40/waves/` (`git ls-tree -r --name-only`), each `grep -o 'flagged as potentially' | wc -l`; no file non-zero; total `0`.
   - I4 anchor: `LOG.md:1909` contains `flagged as potentially` (present). The line names R40w2reviewer01/04 and the provider text `Codex error event: Invalid prompt: your prompt was flagged as potentially violating our usage policy`.
6. `git -C $L grep -n S258 -- corpus/` at the lane tip: no S258 row (absent, as the brief said).

Derived values are therefore `rows=2,v2.56.0=0`, `before=6,after=3`, `occurrences=0`; they match the counter's derivation exactly.

## Scoring (frozen counter, scratch clone)

Command (run from `/fast/scratch/hyaku/souji-r41/R41scribe03`, `TMPDIR` set to the same scratch root):

```
TMPDIR=/fast/scratch/hyaku/souji-r41/R41scribe03 bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41scribe03 corpus/lessons/round-41.md=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41scribe03/round-41.md
```

Observed output, verbatim:

```
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0
```

Exit code: **1**.

Interpretation (expected per the brief): I3 and I4 are corrected (`corrections=1`, `corrected=2`). I1's line validates on id, file, filed, derived, rev and intact-ness (`corrections=1`), but its `source=S258` is absent from the scratch clone (`sourced=0`), so I1 is not counted as corrected. The only failing gate is that absence; `junk=0` and `rewritten=0`. Once the S258 row (tier A, status `mined`, opened `2026-10-28`, cells naming `v2.56.0` and `worktree.c`) lands at the lane tip, the same candidate should read `corrected=3 sourced=1`; that was not run, since the row is drafted by another seat and I did not fabricate it.

Scratch cleanup: `rm -rf /fast/scratch/hyaku/souji-r41/R41scribe03` run and confirmed (`scratch removed: yes`). The scorer's own trap also removes its clone.

## Findings for the L1 (observations, not edits)

- F1 (counter population, I1): `derive` counts only registry lines that match the row regex, so the derived `rows=2` excludes the prose line `SOURCES.md:240`, which contains `worktree.c`. The routed spot-check's "3 lines" and the counter's "2 rows" are both true under their own readings; the counter's `rows=` label is correct only because it counts ROW-matched lines. Named limit, not a defect that changes the value.
- F2 (counter population, I4): the derivation counts the provider-text string under `census/round-40/waves/` only. The text is recorded in `LOG.md:1909`, which is outside the counter's population, so `occurrences=0` is an answer to the wave-tree question, not to "is the text recorded anywhere". The filed token `error-text-recorded` is therefore correctly contradicted only under the counter's reading. Named limit.
- F3 (I3 receipts): `c1-after-h.txt` reports at `--rev dc8bd47c…`, not at `bffcc0f`. The register-file difference is unaffected by that, but a reader of the correction should know the receipts' own revisions differ. The candidate's I3 prose cites only the register files and counts.

## Verdict

- C1 candidate (scribe deliverable): **complete as drafted; target not reached in scratch** — `SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0`, exit 1. Expected: `sourced=0` and `corrected=2` because S258 is absent from the scratch clone. Not verified: the post-S258 state (see above).
- No candidate file was placed outside the seat directory; no frozen file, tracked file or round-40 text was touched; no git mutation was run; no tool was installed or upgraded.
