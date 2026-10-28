# R40w2executor02 — C1 do-nothing control reach (r39 counter over the r40 forged set)

Verdict: **SAFE** for the round's C1 control claim. The r39 counter closes all three forged items at the landed tip, so the OLD counter does not reach the evidence-binding predicate. The r40 counter keeps all three OPEN.

Attacked:
- `census/round-40/c1-forged.tsv:2-4` (three forged items, 6 columns).
- `census/round-39/c1-counter.py:111-126`: items parser. It requires exactly 5 fields, line 120-121.
- `census/round-39/c1-counter.py:224`: closure predicate, `anchor in line` plus the must tokens.
- `census/round-40/c1-counter.py`: run as the comparison arm.

The forged set exists at tip `549d9ec53a1f5932337ff14438fcd22b0621828d`. It was added by commit 549d9ec. It is not in 128e412, the instrument commit.

## Findings
1. **Schema gate.** The r39 counter cannot read `c1-forged.tsv` directly: the file has 6 columns, with `evidence` added. Exact output:
   `REFUSAL USAGE: items .../census/round-40/c1-forged.tsv line 2 has 6 fields, expected 5` (exit 2).
   To measure the control I fed it the first five columns (`cut -f1-5`). That drops the evidence column, which is exactly what the old counter ignores by design.
2. **Result at the tip (549d9ec).** The old counter closes all three forged items:
   `SUMMARY items=3 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=65d8eae23bdb` (exit 0).
   The forged items are an uncited token, an unresolvable evidence revision and a non-ancestor evidence revision.
3. **Old register arm.** `REGISTER cells=6 mismatches=0 commit_distinct=6`. It has no strict-descendant check, as preregistered.
4. **Result at 128e412.** Only the uncited item closes. The two other items are `OPEN ANCHOR-ABSENT`, because their SCORECARD anchors (R40-CLAIM-D1 and R40-CLAIM-D2) do not exist at that revision.
   `SUMMARY items=3 open=2 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=65d8eae23bdb`.
   The control only has full reach at a revision that carries the anchors, meaning the tip or later.
5. **Result at 0242085.** The old counter's result is identical to 128e412, with open=2.
6. **r40 counter, same forged set, at the tip.** All three stay OPEN:
   `SUMMARY items=3 open=3 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=915b1184e9c6 forged_sha=915b1184e9c6` (exit 1).
   Per-item reasons: `EVIDENCE-NOT-BOUND`, `EVIDENCE-REV-UNRESOLVED`, `EVIDENCE-NOT-ANCESTOR`.

## Caveats found (not defects in the claim)
- `--register` is read through `git show REV:path` and must be repo-relative. An absolute path silently yields `REGISTER cells=0 mismatches=0 commit_distinct=0`.
- With an absolute register path the old counter reported `items=3 open=0` with exit 1. The nonzero exit came from the register floor, not from the items. Those first runs are not the control reading. The reading above uses the relative register path.
- The committed `census/round-40/records/c1-control.txt` shows the old counter closing one item at 0242085. This run extends that control to the three-item forged set.

## Commands (relative register path, `--root` is the lane, S=/fast/scratch/hyaku/souji-r40/w2/R40w2executor02)
```
cut -f1-5 $L/census/round-40/c1-forged.tsv > $S/forged5.tsv
TMPDIR=$S python3 -B $L/census/round-39/c1-counter.py --root $L --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items $S/forged5.tsv --register census/round-39/cells.tsv --min-cells 1 --min-commit-distinct 0 --scratch $S/w
  -> ITEM R40-FORGE-UNCITED CLOSED / ITEM R40-FORGE-UNRESOLVED CLOSED / ITEM R40-FORGE-NONANCESTOR CLOSED
  -> REGISTER cells=6 mismatches=0 commit_distinct=6
  -> SUMMARY items=3 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=65d8eae23bdb   (exit=0)
TMPDIR=$S python3 -B $L/census/round-40/c1-counter.py --root $L --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items $L/census/round-40/c1-forged.tsv --forged $L/census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --min-cells 1 --min-commit-rows 1 --scratch $S/w
  -> SUMMARY items=3 open=3 forged=3 forged_open=3 forged_closed=0 ... (exit=1)
```
Runs at 128e412 and 0242085 used the same command with `--rev` changed; their output is in finding 4 and 5.

## Install and scratch
- No tool installs.
- Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2executor02` was **removed**. The final `ls` confirmed it is gone.
- No committed file was edited.
