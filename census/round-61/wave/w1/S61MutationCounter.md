# S61MutationCounter: kill-power of the r61 C1 and C2 instruments

Seat: S61MutationCounter (leaf, no subagents). Scratch removed on exit; all receipts and mutant
sources are in `.ufo/waves/round-61/w1/S61MutationCounter/` (`receipts/`, `mutants/SHA256SUMS`).
No tool installed or upgraded. No production file, lane git state or fleet file touched.

## C1: control-chronology binding (candidate from S61ExecChronoArm)

Snapshot of the candidate at scratch: `candidate-freeze-check.py` sha256
`7ef43b8f174fec50717858441822cd83e443bc83be57da8038ef7f3f3bc94828`; `c1-counter.py`
`8b5a993f15d8d14bbca3be6120ec14ab5ad950a692197308a31b884188a10c76`; `c1-matrix.tsv`
`25b70aa14edae8f022ba090e73c2eeb3bcf7a1ab49d86b717318b32802a89600`. Matrix run as
`python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-tool-rev c7228424… --rev c7228424… --work DIR --new-tool T`.

| Tool in NEW slot | rc | SUMMARY (new_forgeries / new_honest / class_mismatches / stubs) | Result |
|---|---|---|---|
| r60 base bytes (`c7228424`, do-nothing) | 1 | 1 / 4 / 1 / REJECTED | RED, as required; `chrono-at-freeze` accepted |
| candidate (control) | 0 | 0 / 4 / 0 / REJECTED | GREEN |
| m1 newest adding commit (`added = ids[0]`) | 0 | 0 / 4 / 0 / REJECTED | **SURVIVOR on all 11 rows** |
| m2 accept add==freeze (`if not is_ancestor(added, freeze)`) | 1 | 1 / 4 / 1 / REJECTED | killed by row `chrono-at-freeze` (accepted) |
| m3 drop `--no-renames --full-history` | 0 | 0 / 4 / 0 / REJECTED | **SURVIVOR on all 11 rows** |
| m4 wrong class (`CONTROL-ADDED-LATER` on the 3 chronology returns) | 1 | 0 / 4 / 1 / REJECTED | killed by row `chrono-at-freeze` (`new_findings=CONTROL-ADDED-LATER`, expected `CONTROL-ADDED-NOT-BEFORE-FREEZE`) |

### Survivors and the shapes that do kill them (supplementary, not in the frozen matrix)

The frozen matrix has one add per control path in every row, so it cannot tell the oldest add from
the newest add (m1), and it has no honest row whose add is hidden by merge simplification (m3).
I built two throwaway shapes (`probe_c1_shapes.py`, deterministic commit dates, throwaway identity,
toplevel asserted before the first commit):

- `readd-at-freeze`: ctl added at ancestor A, removed at R, re-added at freeze F (with prereg).
  candidate rc=0 (oldest = A, a strict ancestor); **m1 rc=1 `CONTROL-ADDED-NOT-BEFORE-FREEZE`**; m3 rc=0.
- `merge-pruned-add`: ctl added on side branch b1; merge X resolves ctl absent (X TREESAME to its first
  parent, so default log simplification prunes b1); F re-adds ctl. candidate rc=0;
  **m1 rc=1** and **m3 rc=1 `CONTROL-ADDED-NOT-BEFORE-FREEZE`** (m3 sees only F, the freeze itself).
- `renamed-in` (honest: ctl born as old.txt, git-mv'd): candidate rc=0, **m3 rc=0 (indistinguishable)**.
  Observed: with a single-path pathspec git filters before rename pairing, so `--no-renames` is inert here.
  I did not find a shape where `--no-renames` alone changes the verdict.

Named limit for the L1: m1 and m3 both pass the frozen 11-row matrix. Killing m1 needs a row where the
receipt is added at an ancestor, removed, then re-added at the freeze. Killing m3 needs a row like
`merge-pruned-add`. Adding rows changes the frozen matrix, so this is an L1 decision; I did not edit it.
Also a semantic note: the rule pins the OLDEST add, so the candidate accepts `readd-at-freeze` (a receipt
committed before freeze, removed, then re-added at freeze). The L1 should confirm that is the intended
semantics before the rows are added.

## C2: receipt-fixture kill-power (r61 fixture `r61-receipt-write.py`, sha256 `fc4b48d3…25161d`)

Honest writer (base `tools/souji-receipt-write.py` bytes, sha256 `367a0ca3…d2c`): pass=10 fail=0,
ALWAYS-WRITE-REJECTED, ALWAYS-REFUSE-REJECTED. Mutants are built from the base writer with `edit`
(`c2/m5…m8`, all parse; sha256 in `mutants/SHA256SUMS`).

| Mutant | Edit | r60 fixture (8 cases) | r61 fixture (10 cases) | Killing case |
|---|---|---|---|---|
| m5 os.replace, no existence check | removed `lexists(out)` refuse; `os.link` → `os.replace` | pass=8 (**survivor**) | pass=10 (**survivor**) | none in fixture |
| m6 no dirty-tree check | removed `git status --porcelain` refuse | fail=1 (case 8) | fail=1 | r60 and r61 case 8 `dirty-tree` |
| m7 (r60 gap a) worktree digest, no byte compare | digest = sha256(worktree bytes), compare removed | pass=8 (gap confirmed) | fail=1 | r61 case 9 `concealed-divergence` |
| m8 (r60 gap b) direct chunked publish to OUT | 16-byte writes straight into OUT after the command | pass=8 (gap confirmed) | fail=1 | r61 case 10 `partial-visibility` |

### m5 survivor: why, and the shape that kills it

Case 2 (`overwrite`) pre-creates OUT as an *untracked* file. The base dirty-tree check then refuses with
rc=2 before the existence check is reached, so case 2 cannot see the missing existence check. Same in r60.
Supplementary probe (`probe_c2_overwrite.sh`, throwaway repo per shape):

- `committed-out-clean-tree` (OUT committed, tree clean): honest rc=2, OUT stays `SENTINEL`;
  **m5 rc=0, OUT replaced by a receipt**.
- `untracked-out-allow-dirty` (OUT untracked, `--allow-dirty`): honest rc=2, OUT stays `SENTINEL`;
  **m5 rc=0, OUT replaced**.

To kill m5 the r61 fixture needs one of these cases. I did not edit the fixture (it belongs to the
S61ExecC2Fixture lane). Recommend adding this as a case.

## Named limits

- Supplementary shapes are mine, not frozen rows; they only test distinguishability.
- Timing cases (r61 3, 4, 10) were run once per mutant, not repeated for flake.
- The C1 matrix was run against my scratch snapshot of the S61ExecChronoArm directory (sha256 above), not
  the live directory.
- The C2 mutants are my own constructions; the S61ExecC2Fixture lane's `mutant-worktree-hash.py` and
  `mutant-direct-write.py` were not run by me.

## Receipts

Each receipt in `receipts/` records mutant or tool sha256, fixture/counter sha256, exact command,
combined output and `EXIT=`:
`c1-base-do-nothing.txt`, `c1-candidate-control.txt`, `c1-m1-newest-add.txt`, `c1-m2-accept-at-freeze.txt`,
`c1-m3-drop-flags.txt`, `c1-m4-wrong-class.txt`, `c1-supplementary-shapes.txt`,
`base-souji-receipt-write.r60.txt`, `base-souji-receipt-write.r61.txt`,
`m5-replace-no-exists.r60.txt`, `m5-replace-no-exists.r61.txt`, `m6-no-dirty-check.r60.txt`, `m6-no-dirty-check.r61.txt`,
`m7-worktree-digest.r60.txt`, `m7-worktree-digest.r61.txt`, `m8-direct-chunked.r60.txt`, `m8-direct-chunked.r61.txt`,
`c2-supplementary-overwrite.txt`.
