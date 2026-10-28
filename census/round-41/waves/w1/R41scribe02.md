# R41scribe02 — C1 correction block (scribe), evidence report

Seat: R41scribe02 (role scribe). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, freeze commit `e2a74312af4233963e44e4dbb38838ece07b8bd2`. MEASURED revision for every derivation: `bffcc0f660ff36eb8add3f61582748a7af019a5b`.
Frozen inputs read and not edited: `census/round-41/preregistration.txt`, `census/round-41/c1-counter.py` (sha256 pin in the preregistration), `census/round-41/c1-items.tsv`, `census/round-41/controls/c1-control.txt`, `census/round-41/score-candidate.sh`, `corpus/lessons/round-40.md`, `corpus/lessons/round-40-verifier-spotcheck.md` §6.

## Candidate

- Path: `.ufo/waves/round-41/w1/R41scribe02/round-41.md` (seat directory only).
- Content: `## Corrections to filed round-40 statements`, three `CORRECTION` lines (I1, I3, I4) in the counter's grammar, each with a one-sentence reason and its counting command. No round-40 text rewritten. The candidate is not in any tracked path.
- I1's line names `source=S258`. That registry row is drafted by another seat and does not exist at the lane tip or in the scratch clone.

## Commands run and observed output

Scratch: `/fast/scratch/hyaku/souji-r41/R41scribe02/` (created by me; the scorer makes and removes its own clone under it).

### 1. Re-derivation of I1 (counter's own rule: ROW = `^\|\s*(S\d{3,})\s*\|`)

Command (python3, reading `git show bffcc0f…:corpus/SOURCES.md`):
```
rows total: 181
rows containing worktree.c: 2
rows containing v2.56.0/worktree.c: 0
   | S009 | git/git source at tag v2.55.0: builtin/gc.c, worktree.c, run-command.c, builtin/commit.c — https://github.com/git/g…   (line 38)
   | S033 | gitrepository-layout(5) … (line 62; `worktree.c` appears in its notes cell)
```
Plain-text cross-check (same file, no row filter):
```
git show bffcc0f…:corpus/SOURCES.md | grep -c 'worktree\.c'                        -> 3   (lines 38, 62, 240; line 240 is a non-row bullet)
git show bffcc0f…:corpus/SOURCES.md | grep -c 'v2\.56\.0/worktree\.c'               -> 0
git show bffcc0f…:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'worktree\.c'        -> 2
git show bffcc0f…:corpus/SOURCES.md | grep -E '^\| S[0-9]+ ' | grep -c 'v2\.56\.0/worktree\.c' -> 0
```
Derived: `rows=2,v2.56.0=0`. The filed "9 rows" disagrees (mismatch=yes). The round-40 spot-check's "1 row" (§6 R40-D-PRUNE) also undercounts; the counter's row count is 2.

### 2. Re-derivation of I3 (first `register_cells=` in each receipt)

```
git show bffcc0f…:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*' | head -1   -> register_cells=6
git show bffcc0f…:census/round-40/records/c1-after-h.txt | grep -o 'register_cells=[0-9]*' | head -1  -> register_cells=3
```
Header lines of the receipts (verbatim, the two register files differ):
- `c1-before.txt`: `# command: … --register census/round-39/cells.tsv --min-cells 3 …`
- `c1-after-h.txt`: `… --register census/round-40/cells.tsv --min-cells 3 …`

Derived: `before=6,after=3`. Filed "like-for-like" is wrong (mismatch=yes).

### 3. Re-derivation of I4 (counter: occurrences of `flagged as potentially` under `census/round-40/waves/`)

```
git ls-tree -r --name-only bffcc0f… census/round-40/waves/ | wc -l                 -> 136
… | while read -r f; do git show "bffcc0f…:$f" | grep -c 'flagged as potentially'; done | awk '{s+=$1} END{print s+0}'   -> 0
git show bffcc0f…:LOG.md | grep -c 'flagged as potentially'                          -> 1   (the anchor, LOG.md line 1909, not counted by the rule)
```
Derived: `occurrences=0`. Filed "error-text-recorded" is wrong (mismatch=yes).

### 4. Frozen scorer on the candidate (the only supported scoring path)

Command:
```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41scribe02 corpus/lessons/round-41.md=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41scribe02/round-41.md
```
Output (verbatim):
```
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=2 uncorrected=1 junk=0 rewritten=0 sourced=0
```
Exit code: **1**. As expected: the S258 row is absent in the scratch clone, so I1 is not corrected (`sourced=0`), and corrected=2 (I3, I4). Expected per the assignment; the target (`corrected=3 sourced=1`) is unmet at this scoring.

### 5. Control: same candidate with a stand-in S258 row (scratch only, not evidence for landing)

I copied `corpus/SOURCES.md` from `bffcc0f`, inserted one synthetic row after S257 (`| S258 | git v2.56.0 \`worktree.c\` (SYNTHETIC scratch row …) | code | A | … | mined | 2026-10-28 | on-release | — |`, 11 cells, tier A, status `mined`, opened `2026-10-28`, cells naming `v2.56.0` and `worktree.c`), and scored it with the same scorer:
```
bash …/census/round-41/score-candidate.sh c1 /fast/scratch/hyaku/souji-r41/R41scribe02 corpus/lessons/round-41.md=…/round-41.md corpus/SOURCES.md=/fast/scratch/hyaku/souji-r41/R41scribe02/synthetic/SOURCES.synthetic.md
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
```
Exit code: 0. This shows only that the I1 line validates against a row with the counter's required properties. The synthetic row is not a source; the real S258 must be opened and landed by the drafting seat, and I did not verify it.

## Checks on the candidate's grammar

- The counter's `junk=0` in runs 4 and 5: no `CORRECTION` line fails to validate; the prose lines do not begin with `CORRECTION`.
- `rewritten=0`: the three filed files are unchanged at the scratch commit (`intact=yes` on all three items).

## Findings for the L1

1. **Pending dependency.** C1 cannot reach its target until the registry row S258 lands at the tip. My line for I1 is correct against the counter's rule (run 5), but the scorer result at the lane tip cannot be `corrected=3 sourced=1` without that row.
2. **Count disagreement between two round-40 artifacts.** The round-40 spot-check reports `worktree.c` in "1 row" (S009); the counter counts 2 rows (S009, S033). The correction block uses the counter's value (2) and states the spot-check's figure is also wrong. No frozen file was edited.
3. No frozen-file defect found in `c1-counter.py` while deriving I1, I3, I4 by its rule.

## Tools

No tools installed or upgraded. Only `git`, `grep`, `awk`, `python3` (stdlib), and the frozen scorer were used.

## Cleanup

Scratch `/fast/scratch/hyaku/souji-r41/R41scribe02/` (including `synthetic/`) removed after this report was written (see final command in the session). No git mutation was run in the lane or fleet; no commit, push, or jj command.

## Verdict

- I3 and I4: candidate lines validate against the frozen counter (`corrected` for both, `junk=0`, `rewritten=0`, derived values equal the counter's own derivation).
- I1: candidate line validates when the `source=S258` row exists (run 5); at the scratch scoring it is not corrected (`sourced=0`), exit 1, as expected.
- Overall for this seat: **candidate complete and scored; C1 target not met at the scratch scoring (`corrected=2 sourced=0`, exit 1), pending S258.** The seat does not claim C1 passes.
