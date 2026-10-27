# C1 slice 5 — G24 (SKILL.md:249, souji-capability-agreement) — ATTACK, no restatement possible

## Counter ITEM line (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
ITEM	G24	MISMATCH	original	rc=2 expect_exit=0 predicate fails last=python3: can't open file '/fast/scratch/hyaku/souji-r34/RestateC1s5/cnt/c1.tal5l_x8/G24.icwibca2/c/tools/souji-capability-agreement.py': [Errno 2] No such file or directory load=4.29
```
Same flocked run as G23 (loadavg before `2.84 2.72 1.92`, after `4.43 3.07 2.04`).

## Prior-correction grep (Q76) — none

Over `git show 9c76c72:SCORECARD.md` (dumped to scratch): `grep -n -E '\| (G23|G24|G26|E01|E04) \|'` → no match, `grep -n 'Round 34 registry restatements'` → no match (count 0). No append-only restatement row binds this cell.

The only other place the value appears is `SCORECARD.md:344`, inside `### Round 30 capability rows`: "`SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10` (v1; A3 reads `k1=12`, R18 matching on stdout)" — an r30 capability row inside the r33-covered capability sections, not a registry restatement of `SKILL.md:249`, so it does not make the item agree under Q76. It does show where the frozen item's predicate text came from: the row's own red-arm/A3 reading, which the row's outcome column maps to exit 1.

## Why no honest row exists

The frozen item pins `at = 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`, and the counter applies `at` as the **checkout revision** of every clone (`checkout_rev`), for the frozen argv, for both cause probes and for the corrected-argv run. The row's own script does not exist at that revision:

```
git -C lane cat-file -e 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b:tools/souji-capability-agreement.py
fatal: path 'tools/souji-capability-agreement.py' exists on disk, but not in '9420341d...'
```
The script is introduced at `d4928ec86b667e3d1ed0adb07fb088e500cf1631` (round-30 freeze) and amended at `02aea483b4366da8705342657995a310cd21a708` (A3).

Executed evidence that the row's command is sound and that only the item's `at`/exit cells are broken — same argv run at the base revision, where the script exists (fresh clone of 9c76c72, scrubbed env, load 15.69):

```
python3 -B tools/souji-capability-agreement.py --root . --rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b \
  --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631
rc=1
SUMMARY k1=12 k2=0 mismatches=12 rows=18 pointers=10 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
```
i.e. the run reproduces the item's frozen predicate text exactly, but exits 1, while the item's frozen `exit` cell says 0. The registry row's own outcome column ("0 `SUMMARY k1=0 k2=0 mismatches=0`; 1 any `MISMATCH` row …") agrees with the observed 1: the frozen exit cell, not the run, is wrong.

Engine check of the only mechanically admissible row shape (argv correction, cause = the commit that first wrote the row's line text, `f732978506f3fa8ef32d4af1b4ee5bc962603aaf`; that cause probe passes because every clone is pinned to 9420341d where the script is absent, so the frozen argv fails there):

```
| G24 | SKILL.md:249 | restated | 1 | `python3 -B tools/souji-capability-agreement.py --root . --rev 9420341d... --base 9420341d... --list-rev d4928ec...` | `SUMMARY k1=12 k2=0 mismatches=12 rows=18 pointers=10 rev=9420341d...` | f7329785... | probe only ... |
ITEM	G24	MISMATCH	restated	rc=2 expect_exit=1 statement is not the run's last digit-bearing line last=python3: can't open file '/fast/scratch/hyaku/souji-r34/RestateC1s5/eng/cnt/c1.js502yqo/G24.3opg1wtk/c/tools/souji-capability-agreement.py': [Errno 2] No such file or directory load=55.82
```
The failure line carries the counter's per-run random scratch path, so it can never be quoted as a reproducible statement. `same` (value drift) cannot help either: both candidates touch `tools/souji-capability-agreement.py`, but `holds(...)` at their parents runs in a clone that is still at 9420341d, so the parent can never hold.

A workaround that materialises the script in the pinned worktree (`git show d4928ec:tools/… > tools/…` inside the argv cell) would satisfy the letter of the argv rule while mutating the measured checkout and hiding the item defect; refused and reported instead of used.

## Attack

ATTACK A3 (frozen item, G24): `at = 9420341d…` predates the row's own script (`d4928ec`), and the frozen `exit` cell (0) contradicts the frozen predicate text, which is the red-arm line the row's own outcome column maps to exit 1. Reproduced state above. Every other cell of the item (argv, predicate, where at SKILL.md:249 — the correct row at the list revision) is consistent; the honest row would be `restated | 1 | <the row's own argv> | SUMMARY k1=12 k2=0 mismatches=12 rows=18 pointers=10 rev=9420341d… | <authoring cause>` if `at` were a revision that contains the script. No amendment is proposed here — the L1 owns item decisions.

## Proposed row

None. The item cannot reach AGREE under the frozen bytes.
