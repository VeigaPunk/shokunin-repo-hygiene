# AttackE08b — adversarial falsification of W1's E08b finding (souji r34 w2, seat SwarmCritic11)

## Status

W1's E08b **verdict** (MISMATCH reproduced under the do-nothing control) stands formally, but W1's
**classification** of E08b as "value drift" is **falsified**. The measured `last=0` is not registry
content drift; it is the deterministic output of a transcription-defective frozen argv. The pinned
measurement is intact: the row's own command yields exactly `4` at the pinned revision `6cb22dc`,
matching the frozen predicate `^4$`. The defect is real but mis-mechanized; there is an honest
rule-conforming route W1 under-weighted (argv-correction restatement restoring the row's own script).

## Evidence

Frozen row (list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`, `census/round-34/c1-items.tsv:49`):

```
E08b	SCORECARD.md:32	0	^4$	corpus/knowledge	6cb22dc20c9fdb3c7a49eaa1accabca339054c17	bash -c "grep -lE '^ground: F4' corpus/knowledge/ | wc -l"
```

The bound cell's own recorded command (base `9c76c72:SCORECARD.md:32`, C2 F4 origin-record coverage row):

```
row grep, `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`, ...   → measured "grounded F4 `4`", at 6cb22dc20c9fdb3c7a49eaa1accabca339054c17
```

The r33 enumeration source (`.ufo/waves/round-33/w1/deliver-c1-enumeration-misses.md:21`, E08 row):

```
`grep -rlE '^ground: F4' corpus/knowledge/` piped to `wc -l`  → at 6cb22dc: 135 rows, F4 4
```

So the recorded/authoritative argv is **`grep -rlE` (recursive)**; the frozen r34 row dropped the `-r`.

Bounded probes actually run this seat (all read-only on the lane; scratch under
`/fast/scratch/hyaku/souji-r34/E08b/`, <1 MB):

```
cd /fast/scratch/hyaku/souji-r34/E08b && rm -rf probe && mkdir probe && cd probe
git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive 6cb22dc20c9fdb3c7a49eaa1accabca339054c17 corpus/knowledge | tar -x
bash -c "grep -rlE '^ground: F4' corpus/knowledge/ | wc -l"   → 4   (recursive-rc=0)
bash -c "grep -lE '^ground: F4' corpus/knowledge/ | wc -l"    → 0, stderr: grep: corpus/knowledge/: Is a directory  (frozen-rc=0)
```

Same frozen argv re-run in the lane working tree (HEAD `51acb5fb`): also `0` with the identical
"Is a directory" stderr; pipeline rc=0 because `wc -l` is the last pipe stage. GNU grep never
recurses into a directory argument without `-r`; the frozen argv therefore emits `0` at **every**
revision — at `6cb22dc` (verified via archive), at base `9c76c72` (0 by construction; `git grep`
confirms the *content* count there is 6 for the recursive form), and in the working tree.

W1 do-nothing record (`.ufo/waves/round-34/w1/deliver-c1-do-nothing.txt:38`):
`ITEM E08b MISMATCH original rc=0 expect_exit=0 predicate fails last=0 load=26.77` — exactly the
deterministic output of the defective argv, confirming W1's run faithfully executed the frozen text.

W1's mismatch table (`.ufo/waves/round-34/w1/SwarmExecutor13.md:51`) classes E08b as "value drift
— 0 vs 4". W1's Q76 check (same file, finding 3) found no same-cell correction; independently
reproduced here:

```
git show 9c76c72:SCORECARD.md | grep -cE "SCORECARD\.md:32([^0-9]|$)"  → 0
git show 9c76c72:SKILL.md     | grep -cE "SCORECARD\.md:32([^0-9]|$)"  → 0
```

## Findings

1. **Mechanism falsified: not value drift.** The pinned measurement is unchanged. At the pinned
   tree, the row's own recursive command yields `4` (= frozen predicate `^4$` = SCORECARD.md:32's
   recorded value); the frozen argv yields `0` at any revision because non-recursive GNU grep
   refuses the `corpus/knowledge/` directory argument (stderr "Is a directory", `wc -l` = 0,
   pipeline rc = 0). The r34 frozen list transcribed the r33-recorded `grep -rlE` as `grep -lE`,
   dropping `-r`. This is a frozen-list transcription defect, not registry drift. W1's formal
   MISMATCH verdict is correct (frozen argv vs frozen predicate), but its "value drift"
   classification mis-mechanizes the defect and would misdirect any L1 restatement toward a
   value claim instead of an argv correction.
2. **Honest rule-conforming route exists (argv-correction restatement).** The hardened rules
   (`census/round-34/c1-items.tsv:13`) allow "an argv-correction restatement must run the row's
   own script". SCORECARD.md:32's own script is `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`,
   which returns `4` at the pin and satisfies `^4$`. E08b is therefore correctable to AGREE by an
   argv restatement that restores the recorded command; it does not belong to the class of
   content-drifting cells, and it weakens any inference from the do-nothing run that the registry
   itself moved.
3. **W1's Q76 claim confirmed.** No R30/R31 L/R32 N/R33 K correction row references
   `SCORECARD.md:32` at base (0 hits in both SCORECARD.md and SKILL.md), so E08b is not a Q76
   false positive. The q76-honoring note (".ufo/waves/round-34/w1/deliver-q76-honoring.txt:81")
   that "E08b is a revision-bound F4 count (4 at 6cb22dc)" is consistent with this probe.
4. **Adjacent frozen-list integrity defects (reported, not adjudicated).** (a) The frozen header
   comment (`c1-items.tsv:9`) names "E08b/E15b (restated by r33 rows or merged)" among excluded
   items, yet E08b occupies frozen row 49 — the frozen comment contradicts the frozen rows; the
   row governs, but a future freeze must reconcile. (b) E08a and E08b both bind the same cell
   `SCORECARD.md:32` (different (argv, statement) pairs, so permitted by the header's uniqueness
   rule, but shared-cell binding doubles measurement authority over one SCORECARD row).
   (c) `SwarmCritic19`'s note that excluded rows "were not counter-executed as separate frozen
   items" holds for E08b only in the formal sense — its content claim was independently checkable
   from the pinned tree, and this seat checked it.

## Attack log

- Target: falsify W1's E08b "value drift" classification. Result: **falsified as to mechanism**;
  verdict upheld as to the frozen item's formal state. No honest route to "AGREE original" exists
  (the frozen argv can never emit 4), but the argv-correction restatement route is open and was
  available under the frozen rules.
- Counterexample to the classification: identical `0` output at pinned tree, base rev, and working
  tree — drift cannot be revision-invariant while the recursive count at the pin equals the
  predicate.
- Strongest test run: exact frozen argv and row's-own argv against an archive-extracted pin tree
  (commands in ## Evidence); no lane files modified, no clone created, scratch <1 MB.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE08b.md` (this file)
- `.ufo/waves/round-34/w2/SwarmCritic11.md` (seat report)

Smallest safe correction: L1 records E08b as an **argv-correction restatement** restoring
`grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` (the row's own script per SCORECARD.md:32 and
the r33 enumeration), pinned at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`, predicate `^4$`,
expected exit 0 — no change to the frozen list or predicate; reclassify the mismatch in any
ledger from "value drift" to "frozen argv transcription defect (dropped -r)".
