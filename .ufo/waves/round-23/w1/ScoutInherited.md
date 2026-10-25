# ScoutInherited — classification of the inherited r22 uncommitted leftovers (D1)

STATUS: PASS — all 5 modified reports are genuine in-round content updates (content hunks, no
whitespace-only churn) and both untracked evidence digests match the digests the modified report
claims; recommendation is COMMIT all 7 as one atomic unit, plus one flag on the operator-owned
sweep dir.

Lane revision measured: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (branch master, clean of
staged changes; nothing was staged, committed or reverted by this seat).

## Evidence

### E1 — working-tree inventory (revision 1208bfb, read-only)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain
 M .ufo/waves/round-22/attempt2/w1/CritC1Axis.md
 M .ufo/waves/round-22/attempt2/w1/DraftScorecard.md
 M .ufo/waves/round-22/attempt2/w1/ImplDeclaredA.md
 M .ufo/waves/round-22/attempt2/w1/evidence/CritC1Axis.md
 M .ufo/waves/round-22/attempt2/w1/evidence/DraftScorecard.md
?? .ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.counts
?? .ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.tsv
?? .ufo/waves/round-23/
?? census/operator-sweep-20261019/
```

`git diff --numstat` vs `git diff -w --numstat` (content vs whitespace, 5 modified files):

| file | numstat | -w numstat |
|---|---|---|
| CritC1Axis.md | 149/150 | 149/150 |
| DraftScorecard.md | 130/109 | 130/109 |
| ImplDeclaredA.md | 27/10 | 27/10 |
| evidence/CritC1Axis.md | 126/134 | 121/129 |
| evidence/DraftScorecard.md | 54/50 | 54/50 |

Only `evidence/CritC1Axis.md` has any whitespace-touched lines (10 of its 260 changed lines: the
`-w` diff drops 5 added and 5 deleted); 28 of ~486 changed lines in the whole set are blank-line
reflow. `git diff --check` rc 0. All five are UTF-8 LF, no CRLF flip.

### E2 — untracked evidence digests vs the digests the modified report claims

```
$ sha256sum evidence/impl-a/head-c9f1fe3.counts evidence/impl-a/head-c9f1fe3.tsv
5899dd50304d679ab4b723a401d46f92f06d44001e6b0c98abeb7124a59f3c66  head-c9f1fe3.counts
9b343c6cc9f6d2c9257cd688ef42d2d89a0531d87a9ee63f4b822d008e3fd106  head-c9f1fe3.tsv
```

Claim in `.ufo/waves/round-22/attempt2/w1/ImplDeclaredA.md:24-25` (added by this same uncommitted
diff):

```
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.counts` | `5899dd50304d679ab4b723a401d46f92f06d44001e6b0c98abeb7124a59f3c66` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.tsv` | `9b343c6cc9f6d2c9257cd688ef42d2d89a0531d87a9ee63f4b822d008e3fd106` |
```

Both MATCH. The `.counts` body (`assertions=61 resolved=61 skipped=46 mismatches=0` / `exit=0`)
is also byte-identical to the counts line `ImplDeclaredA.md:105-107` quotes for c9f1fe3.

### E3 — re-derivation (this seat, 2026-10-25, candidate A tool as committed in the wave dir)

```
$ python3 -B evidence/impl-a/souji-declared-evidence.py --root <lane> --file SCORECARD.md \
      --rev c9f1fe3 --format counts
assertions=61 resolved=61 skipped=46 mismatches=0      rc=0
$ ... --rev c9f1fe3 --format tsv > /var/tmp/.../re-c9f1fe3.tsv
$ sha256sum re-c9f1fe3.tsv  ->  9b343c6cc9f6d2c9257cd688ef42d2d89a0531d87a9ee63f4b822d008e3fd106
$ diff re-c9f1fe3.tsv <lane>/.../head-c9f1fe3.tsv   ->  0 lines
```

Byte-exact: the untracked pair is reproducible from committed bytes at c9f1fe3.

### E4 — the numbers the modified reports assert, re-derived with the committed instrument

```
$ git show af73b8b:tools/souji-declared-evidence.py | sha256sum
58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
$ git show c9f1fe3:tools/souji-declared-evidence.py | sha256sum
65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4   (= worktree tools/ copy)
$ tool@c9f1fe3 --rev <R> --file SCORECARD.md --format counts
4edb25d  assertions=55 resolved=52 skipped=33 mismatches=3  rc=1
70af563  assertions=57 resolved=56 skipped=37 mismatches=1  rc=1
5fdd5d5  assertions=60 resolved=60 skipped=38 mismatches=0  rc=0
c9f1fe3  assertions=60 resolved=60 skipped=38 mismatches=0  rc=0
```

Every one of those rows appears verbatim in the modified `DraftScorecard.md` (table at
`:25-33`), and `60/60/38/0` + `55/52/33/3` are the two numbers `CritC1Axis.md:16-18` and
`evidence/CritC1Axis.md:18` rest on. Tool digests `65817d0d…f21448f4` (claimed in
`evidence/DraftScorecard.md:8` and `evidence/CritC1Axis.md:18-19`) and `58ddbfef…`
(`evidence/CritC1Axis.md:24`) both match.

### E5 — provenance timeline (mtimes local -0300, commit times same clock)

```
c9f1fe3  03:56:51  round-22: wave report evidence (52 of 53 seats)
head-c9f1fe3.counts/.tsv   03:57:03   (+12s after that commit)
ImplDeclaredA.md           03:58:20
evidence/DraftScorecard.md 03:59:25
evidence/CritC1Axis.md     03:59:06
DraftScorecard.md          04:00:01
CritC1Axis.md              03:59:31
```

The measurement pair was written 12 s after the tip it names was created, and the five reports
were edited after it — exactly the "the lane moved while I wrote this" ordering each diff asserts.

### E6 — atomicity of the commit (why the 7 are one unit)

```
$ git grep -c head-c9f1fe3 HEAD -- .ufo/waves/round-22/    -> (no output, rc 1)
$ git show HEAD:.ufo/waves/round-22/attempt2/w1/ImplDeclaredA.md | grep -c c9f1fe3  -> 0
```

No committed byte cites the untracked pair; its only citing report is itself uncommitted.
Committing the evidence without the report leaves orphan blobs; committing the report without
the evidence leaves a dangling digest table.

### E7 — exemption surface for K4 (context for the L1, not a repair)

```
$ grep -c '^uncommitted:' corpus/pointer-exemptions.tsv   -> 0
$ ls -A census/operator-sweep-20261019 | wc -l            -> 29   (names counted only; contents never read)
```

### E8 — inventory drift during this seat's run (re-checked at close)

The E1 inventory was re-taken when this report was written. The 7 inherited paths were unchanged
(same 5 `M`, same 2 `??`, no digest change), but four paths that were not in E1 are now present,
all from sibling seats of round 23, not from this seat:

```
?? tools/__pycache__/                 (05:11-05:12, souji-gate-check + souji-rev-pin .pyc)
?? tools/souji-receipt-run.py         (05:12:52, 8582 B)   -- prereg C2 deliverable
?? tools/souji-record-agreement.py    (05:13:10, 14187 B)  -- prereg C1 deliverable
```

`git diff --cached --stat` is empty: nothing is staged, so no seat has half-landed the inherited
set.

## Findings

1. **`.ufo/waves/round-22/attempt2/w1/CritC1Axis.md` — COMMIT.** 149+/150−, `-w` identical; the
   diff is the review's revision advance to `c9f1fe3` (retitled `## Counterexample` ->
   `## Tip movement during review (kept, not overwritten)`, `7→8` proposal withdrawn, "24
   capability columns" replacing "22"), and its two load-bearing numbers re-derive exactly (E4).
   Seat header unchanged (`Seat L1Souji22.CritC1Axis`, line 5).
2. **`.ufo/waves/round-22/attempt2/w1/DraftScorecard.md` — COMMIT.** 130+/109−, `-w` identical;
   replaces single-point measurements with the 8-row revision table whose 4 checked rows match
   E4 byte for byte, and adds the dual before-measurement (`56/53/33/3` receipt vs `55/52/33/3`
   current scanner). Only the drafted-text row `66/66/44/0` (`:63-64`) is not re-derivable now —
   its `/var/tmp/ds-cand` candidate is gone; `[INFERENCE]` it is seat-asserted, and it is
   consistent with the base `60/60/38/0` plus the +6 assertions the same block enumerates.
3. **`.ufo/waves/round-22/attempt2/w1/ImplDeclaredA.md` — COMMIT (with findings 6 and 7).** 27+/10−,
   `-w` identical; adds the digest table that binds the two untracked files (E2, both MATCH), the
   c9f1fe3 re-measurement, and the `4a6ee90` escaped-pipe explanation. Committing this file alone
   would commit a digest table pointing at untracked paths.
4. **`.ufo/waves/round-22/attempt2/w1/evidence/CritC1Axis.md` — COMMIT.** 126+/134−, `-w` 121/129
   (10 whitespace-touched lines, 5 per side; no whitespace-only file); the transcript is
   compressed from raw
   `sha256sum <(...)` invocations to recorded values while keeping all three byte states
   (`ac838b4c…`, `05b53b7d…`, `58ddbfef…`); `58ddbfef` and `65817d0d` both re-derived (E4). No
   filed finding is deleted — E1's heading is renamed, not dropped.
5. **`.ufo/waves/round-22/attempt2/w1/evidence/DraftScorecard.md` — COMMIT.** 54+/50−, `-w`
   identical; base/drafted numbers moved from `d6a75ba` to `5fdd5d5`/`c9f1fe3` and the cited
   instrument digest `65817d0d…f21448f4` matches the committed blob (E4).
6. **`.ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.counts` (untracked) — COMMIT
   with finding 3.** Digest `5899dd50…` equals the claim (E2) and the body reproduces (E3);
   it is byte-identical to `head-5fdd5d5.counts`, which is expected — `SCORECARD.md` bytes did
   not change between `5fdd5d5` and `c9f1fe3`, so the same scanner must print the same line.
7. **`.ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.tsv` (untracked) — COMMIT
   with finding 3.** Digest `9b343c6c…` equals the claim and equals this seat's fresh
   re-derivation byte for byte (E3). Its 107 data rows reconcile with the counts line
   (61 resolved + 46 skipped; class A 51 + B 10 = 61; the trailing line 109 is the counts line,
   not a row). The only delta from `head-5fdd5d5.tsv` is the revision token in the `detail`
   column — the signature of a re-run at a new tip, not of a hand-edited file.
8. **`census/operator-sweep-20261019/` — DO NOT STAGE, DO NOT READ.** Operator-owned (29
   entries, names counted only); not in this seat's scope and not in the 7. FLAG for the L1:
   `corpus/pointer-exemptions.tsv` has **0** `uncommitted:` rows (E7), so under the frozen C1/K4
   predicate this path — and `?? .ufo/waves/round-23/` — currently counts as mismatches. Whether
   that is intended (round-23 output lands at the tip) or needs one operator-owned exemption row
   is C1's call, not a scout edit; no row was written by this seat.
9. **No defect found in the inherited set.** Zero of the 7 is whitespace-only, zero is a
   revision-regression (every changed number moves toward the later tip), zero cites a digest
   that disagrees with the bytes on disk. The spot-check's D1 is therefore "uncommitted, not
   wrong": the repair is one commit, not a revert of any file.
10. **`tools/__pycache__/` — NEVER STAGE; owner should remove it (flag, not my edit).** It did
    not exist in the E1 inventory; it appeared at 05:11-05:12 alongside the round-23 tools and
    holds `souji-gate-check.cpython-314.pyc` + `souji-rev-pin.cpython-314.pyc` — a sibling
    seat's interpreter byproduct (this seat ran every Python invocation with `-B`, and its
    scratch was `/var/tmp`). The lane has **no `.gitignore`** (`git check-ignore` rc 1), so this
    directory is an unexempted `git status --porcelain` path and therefore a K4 mismatch under
    the frozen C1 predicate, and committing it would put host-specific bytecode in the tree.
    Route: the owning seat removes it and/or the lane adopts `PYTHONDONTWRITEBYTECODE`/`-B` in
    its tool invocations. `tools/souji-receipt-run.py` and `tools/souji-record-agreement.py`
    (same window) are this round's C2/C1 deliverables named in the preregistration — expected,
    out of this item's scope.

## Notes

- No tool was installed or upgraded (no pacman transaction; host pacman transactions are paused).
- Scratch `/var/tmp/souji-r23-ScoutInherited/` was used for the re-derivation and removed.
- Nothing in the lane was staged, committed, reverted, moved or deleted by this seat; only
  read-only `git log/show/diff/status/ls-tree/cat-file/rev-parse/grep` were run.
- Unresolved: the `66/66/44/0` drafted-text row (finding 2) cannot be re-derived without the
  vanished scratch candidate; it is the one number in the 7 files resting on seat assertion.
