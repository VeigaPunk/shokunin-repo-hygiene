# R40w2scout01 — calibration sweep

## Verdict: FALSIFIED (scope: round-40 self-assessment coverage)

**Attack:** the claim that self-assessment values without a revision-bound receipt pointer are all identified/closed. C1 checks only the three rows in `census/round-40/c1-items.tsv`; it is not a whole-file sweep of `SCORECARD.md` or `LOG.md`.

### Round-40 cells inspected

- `SCORECARD.md:783` — `rows=178`, `W04=49`, exit 0: names `census/round-40/records/census-after.txt` and its commit `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`. **No missing pointer** under the task's receipt/revision criterion.
- `SCORECARD.md:784` — `legs=7`: names `census/round-40/records/c2-after.txt` and commit `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`. **No missing pointer**.
- `SCORECARD.md:785` — `killed=4`: names `census/round-40/records/c3-after.txt` and commit `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`; also names instrument revision. **No missing pointer**.
- `LOG.md`: the read at lines 1890–1899 ends with the Round 39 entry; no Round 40 self-assessment entry is present there at this revision.

The broader calibration failure is that the counter takes a caller-supplied item TSV, evaluates only those rows, and succeeds with 3/3 supplied cells. It has no SCORECARD/LOG discovery or enumeration. The C1 closure output below proves it did not discover a separately introduced pointer-free assessment line. The actual lane-wide injected probe was immediately removed; it is not retained as a committed or working-tree change.

## Reproduction

All commands were run in `/home/vgpnk/Projects/shokunin/souji-shokunin`; no install/update performed.

Command (committed-byte C1 counter):

```sh
mkdir -p /fast/scratch/hyaku/souji-r40/w2/R40w2scout01
export TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2scout01
python3 -B census/round-40/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --register-rev 549d9ec53a1f5932337ff14438fcd22b0621828d --min-cells 3 --min-commit-rows 3 --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2scout01
```

Real stdout / exit:

```text
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
counter_rc=0
```

**Counterexample operation actually run:** appended `R40-UNREGISTERED-PROBE cases=987 pass=987` to `souji-shokunin/.ufo/waves/round-40/w2/R40w2scout01-probe.tmp`, outside the item list's three rows, then reran the exact command above. It emitted the identical output (`items_sha=8f97b0097e09`, `forged_sha=915b1184e9c6`, `counter_rc=0`) and did not mention the probe. Removed that probe immediately. This demonstrates bounded-input checking, not automatic file discovery; it does not alter the committed lane.

Revision pin command/output:

```sh
git rev-parse HEAD && git rev-parse --abbrev-ref HEAD && git log -1 --format='%H %ci %s' && git merge-base --is-ancestor 128e412b0ced3c243dc27c3dd3332054a611bc2e HEAD; echo ancestor_rc=$?; git cat-file -t 128e412b0ced3c243dc27c3dd3332054a611bc2e; git rev-parse --show-toplevel
```

```text
549d9ec53a1f5932337ff14438fcd22b0621828d
HEAD
549d9ec53a1f5932337ff14438fcd22b0621828d 2026-10-28 17:08:52 -0300 round-40: C1 closure cells and bound register
ancestor_rc=0
commit
/home/vgpnk/Projects/shokunin/souji-shokunin
```

The requested landed instrument commit was inspected with `git show --stat`; output identified `128e412b0ced3c243dc27c3dd3332054a611bc2e`, subject `round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery`, and its 24-file summary. HEAD includes it and three later round-40 commits.

## Evidence boundary

Observed: `census/round-40/c1-items.tsv` has exactly three rows, for `R40-CLAIM-D1` through `D3`; the C1 source evaluates only its parsed `--items`/`--forged` rows. The three registered closure cells above have pointers. The supplied fake rows remain OPEN (as intended).

Finding: that is not evidence that every value-bearing self-assessment in the full `SCORECARD.md` and `LOG.md` carries a receipt and revision. The acceptance request asks for a whole-file inventory; C1 does not implement one. I do not claim an exhaustive inventory of historical self-assessment lines: the round-40 records checked are listed above, and broader historical line-by-line classification is unresolved. No LSP semantic server was used/available in this scouting run; source behavior is established from the directly read implementation, not grep as semantic proof.

Scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2scout01` was removed before report write. No software installed or updated.
