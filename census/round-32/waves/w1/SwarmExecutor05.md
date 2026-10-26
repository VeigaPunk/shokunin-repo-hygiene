# SwarmExecutor05 (r32 wave 1) — C1 bindings for N27–N34

## Status

STATUS: PARTIAL — 2 of 8 assigned items (N27, N32) bind MATCH under both `c1-counter.py` and
`c1-counter-v2.py`; the other 6 have no admissible observable under the frozen rules (receipts in
§Findings 1–3), so I wrote no row for them rather than a `withdrawn:` row whose definition they contradict.

## Evidence

All commands read-only on the lane; private clones under `/fast/scratch/hyaku/souji-r32/C1BindE/`
(origin removed right after clone, throwaway identity set with `git -C <scratch> config`).

1. Base line and its cited files (924 bytes, `census/round-31/…` only):

```
git -C <lane> show 85b61a15…:SCORECARD.md | sed -n '422p'
→ | capability-cell binding audit (r31) | … `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`
  (`census/round-31/records/c1-after-a4.txt`; base `census/round-31/records/c1-before.txt` `unbound=22 mismatches=34`);
  `census/round-31/c1-cells.tsv` (41 items) | r31 (claim missed: L29 unbound) |
```

Only three paths are cited on that line: `c1-after-a4.txt`, `c1-before.txt`, `c1-cells.tsv`.

2. The two cited records, line 43 each (unchanged since base: `git diff --stat 85b61a15… HEAD -- <both>` empty):

```
census/round-31/records/c1-after-a4.txt:43
  SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=24f343c8ffc820c0f89b4252cbdc94ab9a673aab
census/round-31/records/c1-before.txt:43
  SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525
```

3. The cell's own command re-executed from the base blob (`--root .`, cwd = clone at the measured rev):

```
--rev 24f343c8… --base 9f17a1ef… --list-rev 1d45496a…
  SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=<HEX>   rc=1
--rev 1d45496a… --base 9f17a1ef… --list-rev 1d45496a…
  SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=<HEX>   rc=1
--rev 85b61a15… (lane tip)
  SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=<HEX>   rc=1
```

4. Acceptance proof — clone `7822e1bfdbbba9c025b2e314d5e0f99d7e9e5fee`, two rows appended, both counters,
`--base 85b61a15… --list-rev 3ec84fc8… --only N27,N28,N29,N30,N31,N32,N33,N34`:

```
v2: N27 record MATCH c1-after-a4.txt:43 | N32 record MATCH c1-before.txt:43
    N28 N29 N30 N31 N33 N34  binding=- UNBOUND
    SUMMARY items=8 bound_run=0 bound_record=2 bound_field=0 withdrawn=0 unbound=6 mismatches=6
v1: identical verdicts.
```

5. Attack receipt — clone `ea9307591d6a577b6a6246d94e8cfba0812a3ee0`, all eight items on the two cited
lines (the maximal record-only allocation): 8 × `BAD-ROW(shared-occurrence)`, `SUMMARY … unbound=0
mismatches=8`.

6. Unit-word sweep of `census/round-31/c1-cells.tsv`: `grep -ci` = 0 for each of `items`, `bound_run`,
`bound_record`, `unbound`, `mismatches`, so that file cannot carry any of the eight as a `record:`.

## Findings

1. **`run:` is closed for this cell (location: `SCORECARD.md:422`; `tools/souji-capability-cells.py`
   return path).** The tool returns 0 only when `mismatches==0`; L29 has no superseding row at any rev
   after the r31 rows (`grep -n '^| L29 ' SCORECARD.md` → no match at the lane tip), so every measurable
   state yields `mismatches>=1` and rc=1. The counter requires `rc == 0`, so its own command can never
   bind the five post-state counts (measured: 6 `RUN-MISMATCH` — 5 on the post-state argv, 1 on the
   baseline argv).
2. **One item per `(path, line)` caps line 422 at two bound items (location:
   `census/round-32/c1-counter-v2.py`, `occ`/`shared` block; v1 carries the same rule).** The cell's
   eight integers stand on two SUMMARY lines plus an uncountable tsv; all eight on those lines is
   `BAD-ROW(shared-occurrence)` ×8. The r32 enumerator (`c1-enumerate.py`) splits one count statement
   into one item per digit run, which this uniqueness rule makes unwinnable.
3. **`withdrawn:` is not available for these six (location: `c1-counter.py:36-37`).** The kind is defined
   as "no observable shows it"; `bound_run=20`, `bound_record=20`, `unbound=1`, `mismatches=1`,
   `mismatches=34` are each shown by a cited, unchanged record line. Writing withdrawn rows would have
   satisfied the counter while misstating the record, so I did not.
4. **The two admissible bindings are exact-byte correspondences (location `SCORECARD.md:422`).**
   N27's `items=41` is the post SUMMARY's own field, committed verbatim at `c1-after-a4.txt:43`; N32's
   `unbound=22` is the number the cell attributes to `c1-before.txt`, standing on that file's line 43
   beside `mismatches=34`. Tie-break inside each line: lowest item id (N27 over N28–N31, N32 over N33).
5. **No integer on line 422 is wrong.** The observed values equal the cell's (24f343c8 →
   `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`; 1d45496a → `unbound=22
   mismatches=34`), so this is a binding-rule defect, not a stale count.

## Attack log

A1 — **`--only` produces a false green (reproduced).** `tools/souji-capability-cells.py … --only X01,…,X41`
(non-item ids) prints `SUMMARY items=41 bound_run=0 bound_record=0 unbound=0 mismatches=0 partial=1` and
exits 0: a `run:` row with 41 bogus ids would MATCH `items=41` (N27/N34) and `=0` literals while measuring
nothing; `--only` over exactly the 20 passing items would publish `bound_run=20` (N28/N29) circularly. I
used neither. State: rc=0, `partial=1`, counts all zero, observed at the r31 landing rev.

A2 — **Line-422 target is unreachable as frozen (reproduced).** Max attainable = 2 MATCH; the remainder
cannot be `withdrawn:` (A1-adjacent definition argument, Finding 3). No predicate/target/item change is
proposed here (data exists); the receipts are in the delivery file for the L1's decision.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-c1-bind-N27-N34.md` — the two ready-to-append rows, the six blocked
  items with reasons, attack receipts A1/A2, and the acceptance output.

Notes: no tool installs or upgrades (pacman untouched, no `uv`/`npx`); no `git add/commit/push` in the
lane and no jj mutation (all commits were in scratch clones with `-C`); lane reads only, plus this report
and the delivery file. Scratch `/fast/scratch/hyaku/souji-r32/C1BindE` removed after the delivery was
copied into the lane.
