# R41reviewer01 — independent re-derivation of C1 item I1 ("worktree.c appears in 9 rows")

Seat: R41reviewer01 (reviewer, calibration). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Pinned revision: bffcc0f660ff36eb8add3f61582748a7af019a5b (`round-40: final measurement receipts...`, tree e4e29837).
Freeze commit e2a74312af4233963e44e4dbb38838ece07b8bd2 checked for the same derivation.
All git calls were read-only (`cat-file`, `show`, `grep`, `ls-tree`, `log`, `merge-base`, `rev-parse`). No commit, no writes to the lane, no installs.

## Filed statement (what is being checked)

- `corpus/lessons/round-40.md:49-50` (at bffcc0f): "The lane already holds git's prune gate (`worktree.c` appears in 9 rows of `corpus/SOURCES.md`); adopting it again would be a duplicate, not new ground."
- Frozen item row: `census/round-41/c1-items.tsv` I1 — file `corpus/lessons/round-40.md`, anchor "appears in 9 rows", claimed `9-rows`, derive `rows-worktree-c`.

## Method A (mine, derived before reading the counter)

Extracted the committed bytes of `corpus/SOURCES.md` at bffcc0f, then counted with awk/grep on the raw lines, not with the counter's regex.

Commands and observed output (verbatim):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t bffcc0f660ff36eb8add3f61582748a7af019a5b
commit
$ git ... show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md > /fast/scratch/hyaku/souji-r41/R41reviewer01/SOURCES.bffcc0f.md
300 lines
$ grep -n 'worktree\.c' SOURCES.bffcc0f.md
38:| S009 | git/git source at tag v2.55.0: builtin/gc.c, worktree.c, run-command.c, builtin/commit.c — ... | ... worktree.c:954-956, :1001-1008; ... | ... | corpus/knowledge/git-auto-maintenance-prunes-worktrees.md |
62:| S033 | gitrepository-layout(5) — ... | docs | A | git 2.55.0 worktrees/<id> admin files | ... the page lists no worktrees/<id>/index entry although worktree.c ages by it | queued | ...
240:- **Negative: does gitrepository-layout(5) document `worktrees/<id>/index`? (2026-10-19).** ... Index entries found: 0, yet `worktree.c:1001-1008`@v2.55.0 ages registrations by that file. ...
$ grep -n 'v2\.56\.0/worktree\.c' SOURCES.bffcc0f.md
(no output, exit 1)
$ awk 'substr($0,1,1)=="|" && index($0,"worktree.c"){n++} END{print n+0}'                       -> 2
$ awk 'substr($0,1,1)=="|" && index($0,"worktree.c") && index($0,"v2.56.0"){n++} END{print n+0}'  -> 0
$ awk 'index($0,"worktree.c") && index($0,"v2.56.0/worktree.c"){n++} END{print n+0}'            -> 0
$ awk 'index($0,"worktree.c"){n++} END{print n+0}'                                              -> 3
$ grep -o 'worktree\.c' SOURCES.bffcc0f.md | wc -l                                              -> 4
```

Derived value (Method A): table rows (registry rows, S-id rows) containing `worktree.c` = **2** (S009 line 38, S033 line 62). Rows containing `v2.56.0/worktree.c` = **0**. Table rows containing `v2.56.0` at all = 13 (awk, leading-pipe test); none of them contains the literal `v2.56.0/worktree.c`.

Freeze commit check (`git show e2a7431…:corpus/SOURCES.md`): `worktree.c` lines = 3, rows with both literals = 0. `git merge-base --is-ancestor bffcc0f e2a7431` succeeds (bffcc0f is an ancestor of the freeze).

History check: `git log --format=%H -- corpus/SOURCES.md` (52 commits); for each commit, the max count of lines containing `worktree.c` was **3** and table rows containing it was **2** in every commit. The number 9 never appears in any committed revision of SOURCES.md that I could read.

## Method B (the counter, read only after Method A)

`census/round-41/c1-counter.py` sha256 = 8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63 (matches the pin). `c1-items.tsv` sha256 = 2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf (matches the pin).

I read `derive()` (lines 71-93) and `sourced()` (96-107) only after Method A. The counter's `derive('rows-worktree-c')` takes lines matching `^\|\s*(S\d{3,})\s*\|` and counts `worktree.c` and `v2.56.0/worktree.c`. I called that function in-process (`python3 -B`, `sys.dont_write_bytecode=True`, no file written):

```
counter derive rows-worktree-c -> ('rows=2,v2.56.0=0', True)
MEASURED = bffcc0f660ff36eb8add3f61582748a7af019a5b
counter ROW regex matched rows count: 181
sourced(S009) -> False
```

Agreement: Method A rows=2, v2.56.0=0; counter rows=2, v2.56.0=0; mismatch flag True (2 != 9). The two methods differ in regex (leading-pipe test vs S-id prefix), but both select the same two rows for this literal.

## Is "rows containing the literal" the fair reading of "appears in 9 rows of corpus/SOURCES.md"?

Yes, it is the most literal and most natural reading: "X appears in N rows of file F" in this lane's usage means N registry rows of F that contain X. The lane's registry is a table of S-id rows, so a row is a table row. Under that reading the filed number is 2, not 9.

Other readings I computed at bffcc0f (all from committed bytes):

| Reading | Count |
|---|---|
| Table rows containing `worktree.c` (fair reading) | **2** |
| Any line containing `worktree.c` (includes note at line 240) | 3 |
| Occurrences of `worktree.c` (`grep -o`) | 4 |
| Table rows containing `worktree.c` and `v2.56.0` | 0 |
| Table rows containing `worktree` (any case) | 26 |
| Table rows containing `worktree` and `.c` substring | 22 |
| Table rows containing `worktree` and col 4 = `code` | 4 |
| Table rows containing `v2.56.0` and `worktree` | 4 |
| Corpus-wide, lines containing `worktree.c` (`git grep -- corpus`) | 12 |
| Corpus-wide, table rows containing `worktree.c` | 4 |
| SOURCES.md, max over all 52 committed revisions, lines containing `worktree.c` | 3 |

No reading I could compute from committed bytes gives 9. The broadest term ("worktree" in any table row, 26) overshoots, and the only readings close to 9 (corpus-wide lines 12; table rows containing `worktree`+`.c` 22) use a different needle or a different file set. Under every reading I tested, the filed "9" disagrees with the committed registry.

Unverifiable residue: the lesson's "9 rows" could have counted the staged package `fleet-prune-safety-r28.md` (S160), whose bytes are not committed here. `census/round-40/assimilation/` holds only id lists (`reg-ids`, `staged-ids`, `collisions`), and no committed file at bffcc0f contains the package text. I could not check that origin, so I report it only as an unverified possibility. The filed sentence names `corpus/SOURCES.md` explicitly, so the package is not the stated referent.

## Verdict

- I1 **mismatched** (filed 9, re-derived 2 table rows; 0 rows carry `v2.56.0/worktree.c`). Independent of the counter, and the counter's own derivation agrees (`rows=2,v2.56.0=0`).
- The literal "rows containing the literal" reading is the fair one. No other reading tested gives 9.
- Consequence for the lane: a CORRECTION for I1 must carry `derived=rows=2,v2.56.0=0` at bffcc0f. The counter's `sourced()` also requires a tier-A `mined` registry row dated 2026-10-28 whose cells name both `v2.56.0` and `worktree.c`; none exists at bffcc0f (`sourced(S009)` = False, and the literal-both count = 0), so that row must be newly added by a candidate. This report does not check any candidate.
- No defect found in the frozen counter for I1: its derivation is correct for the literal reading.

## Commands run (summary list)

1. `git -C <lane> cat-file -t bffcc0f…` → `commit`
2. `git -C <lane> show bffcc0f…:corpus/SOURCES.md > <scratch>/SOURCES.bffcc0f.md` → 300 lines
3. `grep -n 'worktree\.c'`, `grep -n 'v2\.56\.0/worktree\.c'`, awk row counts, `grep -o | wc -l` (outputs above)
4. `git -C <lane> show bffcc0f…:corpus/lessons/round-40.md` → read lines 43-58 (filed sentence at 49-50)
5. `git -C <lane> show e2a7431…:corpus/SOURCES.md | awk …` → worktree.c=3, both=0
6. `git merge-base --is-ancestor bffcc0f… e2a7431…` → ancestor
7. Loop over `git log --format=%H -- corpus/SOURCES.md` (52 commits), per-commit counts; max lines = 3
8. `git grep` over `corpus/` at bffcc0f → 12 lines, 4 table rows
9. `sha256sum` on counter and items (pins match)
10. `python3 -B` in-process call of `c1-counter.derive('rows-worktree-c')` → `('rows=2,v2.56.0=0', True)`
11. `ls-tree` of `census/round-40/assimilation`, grep for package bytes → ids only, no `worktree.c` text

Scratch files under `/fast/scratch/hyaku/souji-r41/R41reviewer01/` (SOURCES.bffcc0f.md, round-40.bffcc0f.md) are copies of committed bytes; deleted before yield.

## Scope notes

- No candidate scored and no CORRECTION line written (out of assignment).
- No install or upgrade of any tool.
