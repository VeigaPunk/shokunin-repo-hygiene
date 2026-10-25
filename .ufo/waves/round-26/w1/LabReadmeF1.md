# LabReadmeF1 — which coverage-map row must name the two new C2 entries

## Status
STATUS: PASS — 11 rows with a letter+digit ground token exist at HEAD `ba8b54b`; the coverage-agreement instrument keys
the map per ground number and **unions** every row with that number (`tools/souji-coverage-agreement.py:153-154`), so
naming the two entries in *any* F1 coverage-map row satisfies K4 — the r12 row `:39` is **not** required. At the real tip
both entries are already named in `:39`, in the same commit that added them (`0833de9`), and K4 is green at both
`0833de9` and `ba8b54b`.

## Evidence

E1 — row census at HEAD `ba8b54b85814dd980aa96050fe111c7cbfd4956a`
```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -nE '^\| *F[0-9]' HEAD -- corpus/README.md   # 11 lines
39:| F1 git-native housekeeping vs receipts | 40:| F2 repository size census | 41:| F3 duplicate verdicts |
42:| F4 restorable quarantine, ... | 68:| F2 repository size census | 216:| F1-jj jj-colocated lane repos |
217:| F2 caveat, disclosed only: ... | 242:| F5 process residue | 274:| F5 process residue |
517:| F2 repository size census | 544:| F2 repository size census |
```
Exact entries cells (from the tool's own `cells()`/`map_rows()`, tip `HEAD`):

| row | ground token | k | entries cell |
|---|---|---|---|
| 39 | `F1 git-native housekeeping vs receipts` | 1 | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md` |
| 40 | `F2 repository size census` | 2 | — |
| 41 | `F3 duplicate verdicts` | 3 | `knowledge/dupe-finders-detect-then-act.md` |
| 42 | `F4 restorable quarantine, file-system semantics` | 4 | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md` |
| 68 | `F2 repository size census` | 2 | `knowledge/git-repo-structure-readonly.md` (S035/S036/S037); `../tools/souji-repo-structure.sh`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-13/verification.json` |
| 216 | `F1-jj jj-colocated lane repos (edge class of F1)` | 1 | `knowledge/jj-colocation-receipts.md`; `../tests/fixtures/r17-jj-receipts.sh`; `../census/round-17/jj-receipts-base5fa6017.txt`, `../census/round-17/jj-receipts-4f48343.txt` (changed arm 0 failed; r18 correction: was a `ddb7347` record name never committed) |
| 217 | `F2 caveat, disclosed only: ...` | 2 | `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` step 5; `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` F3 |
| 242 | `F5 process residue` | 5 | `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh`; `../census/round-18/leak-count.py`; `../census/round-18/proc-census-live-1721.tsv` |
| 274 | `F5 process residue` | 5 | `knowledge/process-residue-observations.md` (S082–S085; S075/S076 rechecked); `../tools/souji-proc-census.sh`; `../tests/fixtures/r18-proc-census.sh` |
| 517 | `F2 repository size census` | 2 | `knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py`; `../census/round-24/size-census-lane.txt` |
| 544 | `F2 repository size census` | 2 | `knowledge/git-repo-structure-readonly.md` (SOURCES S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (SOURCES S120–S123); `knowledge/git-repo-structure-common-dir.md` (SOURCES S124–S126); `../tests/fixtures/r24-size-census.py`; `../tests/fixtures/r13-repo-structure.sh`; `../census/round-25/sources/` |

Sections: `:39-42` under `### Coverage map` (`:34`, r12 table header `:37`); `:68` under `## Round 13 ...` (`:64`, header `:66`);
`:216-217` under `## Round 17 ...` (`:205`, header `:214`); `:242` under `## Round 18 ...` (`:236`, header `:238`);
`:274` under `## Round 19 ...` (`:270`, header `:272`); `:517` under `## Round 24 ...` (`:504`, header `:515`);
`:544` under `## Round 25 ...` (`:538`, header `:542`). File length 558 lines.

E2 — what the tool actually reads (`python3 -B`, import of the lane tool, `map_rows(show(root, rev, 'corpus/README.md'))`)
```
BASE 0eca7c8a5d : map_rows=21; token rows 38(no) 39 F1 40 F2 41 F3 42 F4 68 F2 216 F1 217 F2 240(no) 241(no) 242 F5
                 274 F5 275(no) 276(no) 277(no) 517 F2 518(no) 519(no) 544 F2
HEAD ba8b54b858 : identical row set (same 21 rows, same line numbers)
```
Hence all 11 letter+digit rows are read; the 10 non-token rows are read but contribute no ground key.

E3 — decisive probe (scratch repo `/var/tmp/souji-r26-LabReadmeF1/mirror`, `git init`, `rev-parse --show-toplevel` = that dir,
corpus/README.md + corpus/knowledge copied from the lane at HEAD, README seeded from base `0eca7c8` so row 39 names only the
two old entries; tool run `python3 -B /home/…/tools/souji-coverage-agreement.py --root $D --rev <sha>`)

| variant | README shape (row 39 untouched unless stated) | result |
|---|---|---|
| V1 | tip row 39 names all four | `grounded=9 mapped=9 dangling=0 mismatches=0` rc 0 |
| V0 | base row 39 (old two) | rc 1, `mapped=7`, 2 × `MISSING-FROM-MAP … ground=F1 map_rows_F1=2` |
| **V2** | new `## Round 26` table at EOF, row `F1 git-native housekeeping vs receipts (later row)` naming both | `grounded=9 mapped=9 … mismatches=0` rc 0 |
| **V3** | both named only in the r17 `F1-jj` row `:216` | `grounded=9 mapped=9 … mismatches=0` rc 0 |
| V4 | later `F1` row, names only in the **status** cell | rc 1, `mapped=7`, `map_rows_F1=3` |
| V5 | later table whose 3rd header cell is `notes` | rc 1, `mapped=7`, `map_rows_F1=2` (row not a coverage map) |
| V6 | both named in the `F3` row `:41` only | rc 1, `mapped=7`, `map_rows_F1=2` |
| V7 | later `F1` row separated by a blank line from its header | rc 1, `mapped=7`, `map_rows_F1=2` |
| V8 | later row with ground `F01 …` | `grounded=9 mapped=9` rc 0 (k parsed as 1) |
| V9 | later row with ground `F1. …` | rc 1, `mapped=7` (`F1.` is not a token) |

Scratch removed (`rm -rf /var/tmp/souji-r26-LabReadmeF1`; re-`ls` → no such directory). No lane write, no git mutation in the lane.

E4 — real tip state, K4 (`census/round-26` counter contract K4)
```
$ python3 -B tools/souji-coverage-agreement.py --root . --rev ba8b54b85814dd980aa96050fe111c7cbfd4956a \
    --base-rev 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0      rc=0
$ … --rev 0833de9591a7db81cdfa4efda2cdad2e75606f58 --base-rev 0eca7c8a…         (same output, rc=0)
$ … --rev 0eca7c8a… --base-rev 0eca7c8a…
grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0      rc=0
$ git -C . show 0eca7c8a…:corpus/README.md | sed -n 39p
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md` |
$ git -C . show HEAD:corpus/README.md | sed -n 39p
| F1 git-native housekeeping vs receipts | frontier, entries held | `knowledge/git-auto-maintenance-prunes-worktrees.md`, `knowledge/git-grace-periods-and-expire-to.md`, `knowledge/git-auto-maintenance-trigger-set.md`, `knowledge/git-auto-maintenance-trigger-set-r23.md` |
$ git -C . diff --stat 0eca7c8a… HEAD -- corpus/README.md   → 1 file changed, 2 insertions(+), 2 deletions(-)
   (only :39 entries cell and the `## Frontier` F1 bullet at :45)
$ git -C . grep -l '^ground: F[0-9]' HEAD -- corpus/knowledge/ | wc -l   → 9
$ git -C . log --diff-filter=A --oneline -- corpus/knowledge/git-auto-maintenance-trigger-set.md \
      corpus/knowledge/git-auto-maintenance-trigger-set-r23.md          → 0833de9 …
$ git -C . show --stat --oneline 0833de9 → adds both entries, both SOURCES rows, corpus/README.md (4 +-), sources, C3 tool
```

## Findings
1. **Row set.** 11 letter+digit ground rows at HEAD `ba8b54b`: F1 at `:39` (r12) and `:216` (`F1-jj`, r17); F2 at `:40`,
   `:68`, `:217`, `:517`, `:544`; F3 `:41`; F4 `:42`; F5 `:242`, `:274`. Entries cells in E1.
2. **The tool "selects" no single row.** `map_rows()` (`tools/souji-coverage-agreement.py:74-88`) yields every row of every
   table whose header cell 1 is `ground` and cell 3 starts `entries`; `measure()` keys each row by `GROUND_TOKEN`
   (`:34`, `^F([0-9]+)(?=[ \-]|$)`) and does `mapped_by_k.setdefault(k, set()).update(names)` (`:154`). The map test is
   `name not in mapped_by_k.get(k, set())` (`:159`). So it is a **per-k union**, with `rows_by_k` (`:153`) used only as
   diagnostic text. There is no earliest-row preference and no row-exclusivity.
3. **Answer to the Q56 row question.** Naming the two entries in a **later** F1 coverage-map row satisfies the rule (V2 PASS),
   as does naming them in the r17 `F1-jj` edge-class row (V3 PASS). The r12 row `:39` is not required by Q56
   (`corpus/QUALITY.md:135`: "a … coverage-map row whose ground cell starts with the token F<k>") or by the instrument.
   What *is* required is same-ground, same-commit (`QUALITY.md:135`, "A new grounded entry and its map row land in the same commit").
4. **The real tip already satisfies it.** `0833de9` added both entries, both SOURCES rows, the `:39` entries-cell edit and the
   `## Frontier` F1 bullet in one commit; K4 is `grounded=9 mapped=9 … kill_violations=0` rc 0 at `0833de9` and at
   `ba8b54b`. No further README edit is needed for C2 K4.
5. **Lane position drift (observation for the receipts).** HEAD is `ba8b54b`, **detached** (`git rev-parse --abbrev-ref HEAD`
   → `HEAD`) and 16 commits ahead of base `0eca7c8`; the prereg header says "lane commit 89e0fce …, branch master, ahead=0"
   (that commit exists). K4's after-receipt must therefore name whichever full-40 sha the landing uses; the value is already
   9/9/0/0 at both candidates. At report time a sibling's uncommitted, **addition-only** edit was present on both entry files
   (`git diff --stat -- corpus/knowledge/` → +9/+9 lines, appending `## Gate` blocks after the `# ` heading), so the
   `ground: F1` front-matter lines are untouched; the instrument reads committed bytes (`git show`), so this does not change
   any number above — the receipt must still be run against the final commit, never the worktree.
6. **Attribution defect in the landed history.** `0833de9`'s subject is "round-26 C3: tools/souji-axis-check.py + 11-case fixture"
   yet it also lands both C2 knowledge entries, their SOURCES rows and the C2 README map/prose. Not a K1–K4 violation (no
   counter reads commit subjects), but C2's entry/map pair is recorded under a C3 label — flag it in the landing note.
7. **Stale rows still count.** The r12 F2 row `:40` declares itself "superseded by Round 24 F2 row (:517)" and `:544` (r25) is
   the newest F2 statement, but all five F2 rows feed the same union. A name left in a superseded row keeps an entry
   "mapped". Nothing in C2 needs changing; recorded as a coverage risk (A1).
8. **Status cells are invisible** (V4): Q56's own stated limit. The r12 `:39` status still says "frontier, entries held"
   while its entries cell now carries the two r26 entries — calibration prose not read by any counter.

## Attack log
- **A1 (ground-union, real).** Because `mapped_by_k` unions across rows, an entry can be "mapped" by the `F1-jj` edge-class row
  `:216` (V3) or by any future/duplicate F1 row (V2) without the canonical r12 F1 row changing, and an F2 entry can be kept
  mapped by the superseded `:40` after `:517`/`:544` drop it. Evidence: V2, V3 PASS with row `:39` at base content.
  Not a predicate change request — reported as a gameable shape for the next Q56 revision.
- **A2 (token spelling).** `F01 …` maps to k=1 (V8 PASS) while `F1. …` and `F1<other>` do not (V9 FAIL). A typo in a ground
  cell silently converts to MISSING (strict) or to the wrong-free k (lenient for zero padding). Same regex is documented in
  the r24 fixture case 6 comment (`tests/fixtures/r24-coverage-agreement.py:240-241`).
- **A3 (table continuity).** Rows are only read inside a contiguous table whose header was seen; a blank line after the
  separator drops the row (V7 FAIL, `map_rows_F1=2`). Blocks "hide the row" only in the stricter direction, but it means a
  visually valid map table can be invisible to the counter — an operability trap for future editors.
- **A4 (header-shape).** A table whose third header cell is not `entries…` (V5) or whose first cell is not `ground` is ignored
  entirely; and a wrong-ground row (V6, F3 row naming an F1 entry) does not map. Consistent with Q56, but means map-table
  header edits are load-bearing and unguarded.
