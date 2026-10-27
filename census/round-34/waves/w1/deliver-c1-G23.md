# C1 slice 5 — G23 (SKILL.md:247, r29-c2-counter)

## Counter ITEM line (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
flock /fast/scratch/hyaku/souji-r34/RestateC1s5/cnt.lock python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/RestateC1s5/cnt --only G23,G24,G26,E01,E04
ITEM	G23	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=4.29
```
loadavg before the run `2.84 2.72 1.92`, after `4.43 3.07 2.04` (Q77 recorded beside the reading).

## Prior-correction grep (Q76) — none

```
git -C lane show 9c76c72:SCORECARD.md > SCORECARD.base.md
grep -n -E '\| (G23|G24|G26|E01|E04) \|' SCORECARD.base.md      -> no match
grep -n 'Round 34 registry restatements' SCORECARD.base.md      -> no match (0 occurrences)
grep -n 'r29-c2-counter' SCORECARD.base.md                      -> no match
```
No appended correction, supersession or binding row exists for this cell at the base revision, so the item cannot agree under Q76.

## Cause and executed readings

Frozen `where` cell = `SKILL.md:247`. At 9c76c72 (== the file at `--list-rev`) line 247 is the `souji-wave-evidence-capture v2` row; the `r29-c2-counter` row that the frozen argv/predicate describe sits at `SKILL.md:248` — the item's line number is one behind the list-rev file. Reported as ATTACK A1.

Value drift is impossible for this item as frozen: `census/round-29/c2-counter.py` has exactly one committing history entry (`b8cb4b3`, round-29 freeze), and at its parent the file does not exist, so the frozen (exit, predicate) cannot hold there. The restatement therefore uses the argv-correction branch, cause = the commit that wrote the row's line text:

* cause full40 `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (round-29 C3 commit), parent `b86200714069022954a3b498cf697d894119b45e`.
* the frozen line text is absent from the parent's SKILL.md and present at the cause (checked over all 36 SKILL.md commits: 1dc6785 is the first introducer).
* executed at the cause (fresh clone, fresh TMPDIR, PATH=/usr/bin:/bin, GIT_CONFIG_NOSYSTEM=1):
  `rc=0` / last digit line `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=1dc6785...` → the frozen predicate (manifests=7) already failed at the commit that wrote the row.
* executed at `4d9bf0256f6f61a49ebfec55a524556090015f60` (r33 integration): `rc=0`, `SUMMARY manifests=7 failed=0 uncovered=0 floor_violations=0 rev=4d9bf02...` → the frozen original HOLDS here (this is why 4d9bf02 is rejected as cause).
* executed at the true drift `d65a5c4328896742d2ec951f7156c6a70aa9325a` (round 33's own evidence capture, adds the 8th manifest): `rc=0`, `SUMMARY manifests=8 failed=0 uncovered=0 floor_violations=0 rev=d65a5c4...`; its parent 4d9bf02 holds. d65a5c4 touches no item file, so the frozen value-drift branch refuses it — ATTACK A2.
* the residual `uncovered=1` is `census/round-33/waves/w1-results.json`, added at `af7fd250c8a862130f88b8f77ad29debf343e54d` after the r33 manifest captured its 89 records (`git cat-file` of the manifest blob vs `git ls-tree -r 9c76c72 census/round-33/waves`).
* executed at base 9c76c72: `rc=1`, `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c72...` (load 54.67 during the d65a5c4 run).

## Proposed row (engine-validated: `ITEM G23 AGREE restated`)

| G23 | SKILL.md:247 | restated | 1 | `python3 -B census/round-29/c2-counter.py --root . --rev 9c76c7222a8abff027af42e37f0d160d52526bba` | `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba` | 1dc678500c92164b0b2bea82b934dd03d1dfbf38 | the row's unpinned argv was stale when written: at its authoring commit it printed manifests=3 with exit 0; round 33 added the eighth manifest (d65a5c4) and left census/round-33/waves/w1-results.json unrecorded (af7fd25), so the current reading is manifests=8 uncovered=1 exit 1; this argv pins the round base revision so the reading is reproducible; the where cell is the frozen item's SKILL.md:247 while the r29-c2-counter row itself sits at SKILL.md:248 |

The corrected argv names the row's own script (`census/round-29/c2-counter.py`) and the statement is the run's collapsed LAST digit-bearing line; both were checked by the frozen counter itself in a scratch clone (parent of the probe commit = lane tip 51acb5fb6fa38a6b593b3badb674cec559d7eb2c, appended row only):

```
ITEM	G23	AGREE	restated	rc=1 expect_exit=1 statement is the run's last digit-bearing line last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=55.63
```

The pinned argv is revision-independent, so the row reproduces identically at the C1 landing commit and at the tip.
