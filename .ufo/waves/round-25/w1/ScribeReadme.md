# ScribeReadme — round 25, wave 1 (leaf seat)

Item: draft the round-25 `corpus/README.md` patch text. Draft:
`.ufo/waves/round-25/w1/readme-patch.md` (sha256 `30e9e6728e3c2bac4338dacda9b093d61ce113a2d7878cf05b1e4e0de9c00af0`).
`corpus/README.md` not edited. Scratch: `/var/tmp/souji-r25-ScribeReadme/` (archive of lane HEAD
`6e4737eab43d8fde1b85eb9f57023d29046705b4`, `corpus/` + `tools/`, in a throwaway git repo).
Nothing was written outside `souji-shokunin/.ufo/waves/round-25/w1/` and that scratch.

Duplicate seat: `L1Souji25.ScribeReadme-2` holds the same item. It said it will write
`readme-patch-2.md` / `ScribeReadme-2.md` if these files exist. This report was put in place with an
atomic no-clobber link, and no `-2` file was touched. I could not reply over the agent IRC channel
(no `write` tool to `agent://` in this seat). The L1 should pick one draft or merge the two.

## What the draft contains

1. **:40 status cell**: an in-place append of ` — superseded by Round 24 F2 row (:517)` before the
   closing ` | — |`. Old and new lines are both quoted verbatim, so the round-25 lesson can log
   old→new (D4 / R24-M2). The ground cell and the entries cell (`—`) are unchanged.
2. **Round 24 note (:506-508)**: no change. Its text ("status prose stays as history (:40's
   "frontier, no entry" is stale and superseded here)") is still true after the marker. Editing it
   would break the append-only rule, so the Round 25 section records the :40 fix instead.
3. **Round 25 section**, appended after :536 (Variant A, C3 verified). The new F2 row's entries
   column lists the four r24 F2 entries plus `knowledge/git-repo-structure-common-dir.md`
   (S124/S125), with the same-commit landing condition (Q56). The status cell carries C3's
   envelope result and the colocated/plain precondition. It also has an optional C2 clause
   (bare/subdir/partialClone-only cases 9-12). A non-F "Coverage-map kill rule" row (C1) is
   optional. The draft says what to keep or cut for each.
4. **`### Frontier (r25)`**: only the F2 bullet changes. The envelope and the precondition are
   marked measured (sandbox, `ids=7/7`). Next is a `git repo structure` size baseline on a plain
   clone, with the Git version recorded and the common-dir manifest asserted. The F1/F3/F4/F5
   bullet is the r24 wording verbatim.
5. **Variant B** (C3 not verified): no F2 row and no entry. The F2 bullet reads "unchanged from
   the r24 frontier (:523-527) … stay unmeasured".

## Measurements (scratch repo, lane tool `tools/souji-coverage-agreement.py` at HEAD)

| state | counts line | rc |
|---|---|---|
| lane HEAD, unpatched | `grounded=6 mapped=6 dangling=0 mismatches=0` | 0 |
| :40 change only | `grounded=6 mapped=6 dangling=0 mismatches=0`; diff 1+/1-; :40 still 3 cells | 0 |
| :40 + Round 25 section, no entry | `DANGLING-MAP-PATH … README.md:548`; `dangling=1 mismatches=1` | 1 |
| :40 + section + stand-in F2 entry | `grounded=7 mapped=7 dangling=0 mismatches=0` | 0 |
| stand-in entry, no r25 row | `MISSING-FROM-MAP … ground=F2 map_rows_F2=4`; `mismatches=1` | 1 |
| Variant B (no F2 row, no entry) | `grounded=6 mapped=6 dangling=0 mismatches=0` | 0 |

The applied patch removes one line (:40) and adds 25. Line :517 is still the r24 F2 row, so the
`:517` pointer resolves. The README has 560 lines after the patch, and the new F2 row is :548.
The stand-in entry was scratch-only (front matter `ground: F2`). It does not stand in for C3's
real entry.

## Findings for the L1

- **F-1 (integration constraint):** apply the :40 change in place and only append after :536.
  Any inserted line above :517 makes the new `:517` marker stale, along with the r24 pointers
  (:506-508, :523-527, :531-536). The coverage tool would not catch this, because it does not
  read line pointers in prose.
- **F-2 (Q56 same-commit):** measured both ways. The row without the entry gives exit 1
  (dangling), and the entry without the row gives exit 1 (missing). The row and the entry must
  land in one commit.
- **F-3 (C1 interaction, from the preregistration's separability note):** with C3's entry
  landed, the C1 after-run's `grounded` / `mapped` go up by 1 (6→7 measured with the stand-in).
  `kill_tested` should stay 4, because the new entry is not base-grounded. Check the C1
  after-target wording against 7.
- **F-4 (residual, not fixed):** the r23 prose/table drift class (r24 note :531-536) is still
  undetected by the tool. The draft's F2 row names every F2 entry by hand. Nothing counts this.
- **F-5:** S124/S125 are not yet in the lane's sources registry at HEAD. The only `S124` hits are
  r22/r24 slice-verdict uses of a different document (renumbered in r22). C3 should check that the
  new rows do not collide with that history. Whether `S124` is a bare ID is the same class of
  problem as the S123 disambiguation in D5.

## Tooling

No installs or updates. Used: git 2.56.0, python3 (host), coreutils.
