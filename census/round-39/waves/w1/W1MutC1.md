# W1MutC1 — mutation probe on `census/round-39/c1-counter.py`

role: mutation-tester · round 39 wave 1 · lane `/home/vgpnk/Projects/shokunin/souji-shokunin`
base revision: `ed30b7f5b77939c9073348d810730bc4f355708d`
lane tip observed while probing: `2201778e7736af82e7d8a42dec2494f115bf3923`
scratch: `/fast/scratch/hyaku/souji-r39/W1MutC1` (removed at end of seat — see §Restoration)
no lane byte written; no git/jj mutation run.

## 0. Preconditions observed

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin
$ git log --oneline -1 HEAD -- census/round-39/c1-counter.py
b769bfb round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
$ git status --porcelain census/round-39/c1-counter.py
(empty — working tree == HEAD)
$ sha256sum census/round-39/c1-counter.py
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  census/round-39/c1-counter.py
$ git show HEAD:census/round-39/c1-counter.py | sha256sum
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  -
$ sha256sum census/round-39/records/c1-before.txt
d5c3a21acef64d3a63de29198229a233e349ed68ae885ef8d12eb233bcb184a8  census/round-39/records/c1-before.txt
```

Environment fact used by every run: `census/round-39/cells.tsv` does **not** exist in the working
tree at probe time (`cells.tsv exists: False`), so the register leg takes its `REGISTER-ABSENT`
path and prints `register_cells=0`. That matches `c1-before.txt` exactly, so the base arm is
reproduced with the frozen register argument unchanged. Consequence for this seat: every base run
exits 1 on the `cells >= min_cells(6)` floor regardless of the item arm, so **the exit code carries
no discriminating power in this arm — only the printed `SUMMARY` line does.**

## 1. Pristine control reproduction (baseline; a baseline failure would make kills inconclusive)

```
$ python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --items /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv \
    --register /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/cells.tsv \
    --scratch /fast/scratch/hyaku/souji-r39/W1MutC1
```

observed (16 ITEM lines elided only in this quote; full text compared byte-wise below):

```
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

stdout is **byte-identical** to `census/round-39/records/c1-before.txt`
(`stdout==c1-before.txt: True`), and `items_sha=d892b74f8358` matches the committed receipt.
Baseline: PASS (`open=16`).

Base-arm shape, quoted from the run (this is the structural fact the whole probe turns on):

```
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
...
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
...
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
```

All 16 base rows fail at the **anchor arm** or the **file arm**; none reaches the predicate arm
(`PREDICATE-MISSING` appears zero times in the receipt).

## 2. Mutants applied (each a single-behavior edit, in a scratch copy only)

Pristine source read from the lane file; each mutation asserted to match exactly once
(`text.count(old)==1`) before writing.

| id | edit | mutant sha256 |
|---|---|---|
| M1 | drop the `mustnot` conjunct from the `good` list comprehension | `3e56fd5d028f…` |
| M2 | `all(has_token(l, t) for t in row["must"])` → `any(...)` (one hit line may satisfy a *subset* of `must`) | `3cf24a658825…` |
| M3 | `if text is None:` branch prints `ITEM <id> CLOSED` and no longer increments `open_count` (missing file = CLOSED) | `efe85537077f…` |
| M4 | `open_count = 0` inserted immediately before the `SUMMARY` print (hard-coded `open=0`) | `4c44f5dfe3f0…` |

Exact diffs against pristine (`M1`):

```
-                if all(has_token(l, t) for t in row["must"])
-                and not any(has_token(l, t) for t in row["mustnot"])
+                if all(has_token(l, t) for t in row["must"])
```

(`M2`) `all(` → `any(` on the first conjunct line. (`M3`)

```
-            if text is None:
-                print("ITEM %s OPEN FILE-ABSENT %s" % (row["id"], row["file"]))
-                open_count += 1
-                continue
+            if text is None:
+                print("ITEM %s CLOSED" % row["id"])
+                continue
```

(`M4`) one inserted line `    open_count = 0` above the `SUMMARY` print.

## 3. Score — base arm, `--rev ed30b7f5b77939c9073348d810730bc4f355708d`

Command per mutant (path is the only variable):

```
$ python3 -B /fast/scratch/hyaku/souji-r39/W1MutC1/<mutant>.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --items /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv \
    --register /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/cells.tsv \
    --scratch /fast/scratch/hyaku/souji-r39/W1MutC1
```

| mutant | rc | SUMMARY line at base | stdout == `c1-before.txt` | reading | verdict |
|---|---|---|---|---|---|
| pristine | 1 | `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` | True | `open=16` | baseline PASS |
| M1 drop-mustnot | 1 | `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` | True | `open=16` | **SURVIVED — control defect** |
| M2 any-subset-of-must | 1 | `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` | True | `open=16` | **SURVIVED — control defect** |
| M3 missing-file-closed | 1 | `SUMMARY items=16 open=11 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` | False | `open=11` | KILLED |
| M4 hard-code-open=0 | 1 | `SUMMARY items=16 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` | False | `open=0` | KILLED |

M1 and M2 produce **zero diff lines** against pristine at base (unified diff of the full 18-line
stdout: `diff lines: 0`, `(identical output)`), not merely the same `open=` count.

M3 item-level diff (5 rows flip, `16-5=11`):

```
-ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
-ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
-ITEM R39-C1-05 OPEN FILE-ABSENT corpus/lessons/round-39.md
+ITEM R39-C1-03 CLOSED
+ITEM R39-C1-04 CLOSED
+ITEM R39-C1-05 CLOSED
-ITEM R39-C1-07 OPEN FILE-ABSENT corpus/lessons/round-39.md
+ITEM R39-C1-07 CLOSED
-ITEM R39-C1-15 OPEN FILE-ABSENT corpus/lessons/round-39.md
+ITEM R39-C1-15 CLOSED
-SUMMARY items=16 open=16 ...
+SUMMARY items=16 open=11 ...
```

M4 diff is the `SUMMARY` line alone (`open=16` → `open=0`); per-item lines unchanged.

## 4. Are M1/M2 live, or inert? (supplementary, synthetic item rows)

Survival only means "the control cannot see it" if the mutation actually changes behaviour. Two
one-row probe item files in scratch (`--root` and `--rev` unchanged, base bytes, anchor on a
line-unique anchor of `census/round-38/preregistration.txt` at base):

probe A — `id/file/anchor/must/mustnot` = `P-MUSTNOT | census/round-38/preregistration.txt | lane state | lane state | inherited`
(the only line carrying the anchor also carries the `mustnot` token `inherited`):

```
pristine  rc=1 ITEM P-MUSTNOT OPEN PREDICATE-MISSING census/round-38/preregistration.txt missing=[] hits=1 | SUMMARY items=1 open=1 ...
M1        rc=1 ITEM P-MUSTNOT CLOSED | SUMMARY items=1 open=0 ...
M2        rc=1 ITEM P-MUSTNOT OPEN PREDICATE-MISSING ... missing=[] hits=1 | SUMMARY items=1 open=1 ...
M3        rc=1 ITEM P-MUSTNOT OPEN PREDICATE-MISSING ... | SUMMARY items=1 open=1 ...
M4        rc=1 ITEM P-MUSTNOT OPEN PREDICATE-MISSING ... | SUMMARY items=1 open=0 ...
```

probe B — `P-SUBSET | census/round-38/preregistration.txt | C1 | C1,zzz-not-present | -`
(anchor present on 6 lines, one `must` token absent everywhere):

```
pristine  rc=1 ITEM P-SUBSET OPEN PREDICATE-MISSING census/round-38/preregistration.txt missing=['zzz-not-present'] hits=6 | SUMMARY items=1 open=1 ...
M1        rc=1 ITEM P-SUBSET OPEN PREDICATE-MISSING ... missing=['zzz-not-present'] hits=6 | SUMMARY items=1 open=1 ...
M2        rc=1 ITEM P-SUBSET CLOSED | SUMMARY items=1 open=0 ...
```

Verdict on liveness: **M1 and M2 are behaviourally live** (each flips a row the pristine counter
reads OPEN). They survive the frozen control because the frozen item set contains no discriminating
row, not because the mutated code is unreachable.

## 5. Same mutants against the landing tip (diagnostic; not part of the assigned base arm)

```
$ python3 -B <mutant>.py --root <lane> --rev 2201778e7736af82e7d8a42dec2494f115bf3923 ...
pristine | HEAD rc=1 SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
M1-drop-mustnot | HEAD rc=1 SUMMARY items=16 open=2 ...
M2-any-subset-of-must | HEAD rc=1 SUMMARY items=16 open=2 ...
M3-missing-file-closed | HEAD rc=1 SUMMARY items=16 open=0 ...
M4-hardcode-open-zero | HEAD rc=1 SUMMARY items=16 open=0 ...
diff pristine vs M1 at HEAD: 0 lines
diff pristine vs M2 at HEAD: 0 lines
```

At the tip the only rows that reach the predicate are `R39-C1-05` and `R39-C1-07`
(two hit lines each, all `must` present on a hit line, no `mustnot` on it), so the predicate arms
M1/M2 mutate are executed but never at a boundary — both arms read `open=2`, identical to pristine.
The still-open rows are `R39-C1-03` and `R39-C1-04` (`FILE-ABSENT` at the tip).

## Verdicts

- **M1 (drop `mustnot`) — SURVIVED.** Base control reads `open=16`, stdout byte-identical to the
  frozen receipt. A counter that ignores every `mustnot` token is not distinguished by the control.
  **Defect of the control.**
- **M2 (`any` subset of `must`) — SURVIVED.** Base control reads `open=16`, stdout byte-identical.
  A counter that closes a row on one hit line carrying a single `must` token is not distinguished.
  **Defect of the control.**
- **M3 (missing file = CLOSED) — KILLED.** `open=11` ≠ `open=16`; receipt comparison catches it.
- **M4 (hard-code `open=0`) — KILLED.** `open=0` ≠ `open=16`; also the one class the frozen C1 KILL
  RULE names literally ("if the base-revision control … reads `open=0`").

Calibration finding (advisory to the L1; the contract is frozen and this seat does not change it):
the base control's discriminating power is confined to the `open_count`-shaped mutants (M3/M4).
Because all 16 base rows fail at the anchor/file arms, **no** predicate-arm mutant can be killed by
the control, and the frozen item set supplies no row that reaches the predicate with a `mustnot`
token present or with a partial `must` set, so the landing arm is blind to the same two mutants.
The C1 counter's `mustnot` conjunct and its `all`-over-`must` conjunct are therefore unexercised by
both arms of the frozen predicate. A tighter-only remedy would be a control-side leg that runs the
counter over a one-row item file whose anchor line carries a `mustnot` token (expected OPEN) and one
whose line carries only a subset of `must` (expected OPEN) — i.e. the probe item rows in §4 — so a
mutant in either conjunct changes the control reading. This is a recommendation only; M1/M2 survive
as a coverage/control finding, not as permission to alter the contract.

## Restoration / hygiene

- Lane `census/round-39/c1-counter.py` was never written: `sha256sum` after the whole probe is
  `f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed`, identical to the
  pre-probe hash and to `git show HEAD:` bytes.
- All four mutants and the two probe item files lived under
  `/fast/scratch/hyaku/souji-r39/W1MutC1` only; the tree was removed at the end of the seat
  (`rm -rf`), so nothing is left on disk.
- No `git`/`jj` mutating command was run; only `rev-parse`, `log`, `status`, `show`, `cat-file`
  via the counter, and `sha256sum`.
- No tool installed or upgraded; no network access needed.
