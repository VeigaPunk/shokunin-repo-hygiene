# r32 w1 — C1 capability-count bindings, items N27–N34 (line 422)

Seat: SwarmExecutor05-4. Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`, items read at
`census/round-32/c1-items.tsv` @ `3ec84fc81b3243429c834a051880b0bcde06291c`.

STATUS: PARTIAL — 2 of the 8 assigned items have an admissible observable under the frozen
`c1-counter.py` (v1) and `c1-counter-v2.py` (v1+A0); the other 6 do not, for the structural reason in
§3, and **no rows are written for them** (a `withdrawn:` row would contradict the kind's own definition —
an observable *does* show each of those integers).

## 1. Rows ready to append (verified: MATCH under v1 and v2)

Append under a heading `### Round 32 capability-count bindings` with the header
`| item | base line | literal | binding | reason |` and `|---|---|---|---|---|`:

```
| N27 | SCORECARD.md:422 | items=41 | record: census/round-31/records/c1-after-a4.txt:43 | The cell's own post-state record commits this command's SUMMARY at line 43, where items=41 is the item count the cell states. |
| N32 | SCORECARD.md:422 | unbound=22 | record: census/round-31/records/c1-before.txt:43 | The cell names this baseline record, whose SUMMARY line 43 carries unbound=22 for the do-nothing control. |
```

Why these two and not others: the cell's eight integers come from exactly three cited files. Two of them
(`c1-after-a4.txt`, `c1-before.txt`) each hold **one** count-bearing SUMMARY line (43); `c1-cells.tsv`
holds none of the five unit words (`items`, `bound_run`, `bound_record`, `unbound`, `mismatches` — grep
counts 0 for each), so it cannot carry any of these items as a record. With v1/v2's
`BAD-ROW(shared-occurrence)` rule (one item per `(path, line)`), the attainable maximum on line 422 is 2.
Tie-break used: the post-state SUMMARY line goes to the lowest-id post item (N27), the baseline SUMMARY
line to the lowest-id baseline item (N32). The L1 may re-assign within each line without changing the count.

## 2. Items with no admissible observable (no row written)

| item | integer | why no admissible binding exists |
|---|---|---|
| N28 | bound_run=20 | only cited observable is `c1-after-a4.txt:43`, which the one-item-per-line rule assigns to N27; `run:` cannot take it (see §3a) |
| N29 | bound_record=20 | same line as N28 |
| N30 | unbound=1 | same line as N28 |
| N31 | mismatches=1 | same line as N28 |
| N33 | mismatches=34 | only cited observable is `c1-before.txt:43`, which the rule assigns to N32 |
| N34 | items=41 | `(41 items)` is the row count of `c1-cells.tsv`, which has no count-bearing line and no unit word; the only numeric statement of 41 is on the two SUMMARY lines above |

## 3. Attack (reproduced states) — the frozen C1 rules cannot bind line 422 beyond 2 of its 8 items

**(a) `run:` is closed for the cell's own command: it exits 1 at every measurable state.**
The r31 tool returns 0 only when `mismatches==0`; L29 has no superseding row at any rev after the r31
rows (`grep -n '^| L29 ' SCORECARD.md` → no match at the lane tip), so `mismatches>=1` everywhere.

```
tools/souji-capability-cells.py --root . --rev 24f343c8… --base 9f17a1ef… --list-rev 1d45496a…
  SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=<HEX>      rc=1
tools/souji-capability-cells.py --root . --rev 1d45496a… --base 9f17a1ef… --list-rev 1d45496a…
  SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=<HEX>       rc=1
tools/souji-capability-cells.py --root . --rev 85b61a15… --base 9f17a1ef… --list-rev 1d45496a…
  SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=<HEX>      rc=1
```

The counter requires `rc == 0 and at_bounds(lit, S)` (v1 line 288 / v2 line 288 region), so all three
observations are `RUN-MISMATCH` (measured: `--only N27…N34` over run rows = 6 `RUN-MISMATCH`).

**(b) The counter's own worst-case record allocation is 8/8 `BAD-ROW(shared-occurrence)`.**
With all eight items bound to the two cited SUMMARY lines (the only lines that hold their integers):

```
ITEM N27 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-after-a4.txt:43
ITEM N28 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-after-a4.txt:43
ITEM N29 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-after-a4.txt:43
ITEM N30 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-after-a4.txt:43
ITEM N31 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-after-a4.txt:43
ITEM N32 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-before.txt:43
ITEM N33 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-before.txt:43
ITEM N34 … BAD-ROW(shared-occurrence)  census/round-31/records/c1-before.txt:43
SUMMARY items=8 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=8
```

Root cause: `c1-enumerate.py` splits one count statement into one item per digit run (8 items on
`SCORECARD.md:422`), while v1/v2 permit one item per `(path, line)`. A cell whose counts all stand on a
single SUMMARY line therefore cannot exceed one bound item per line, and its command exits nonzero.

**(c) False-green path found (not used): `--only` with non-item ids.**
`--only` makes `n = len(only)` and skips every item, so the tool prints and exits 0:

```
--only X01,…,X41 → SUMMARY items=41 bound_run=0 bound_record=0 unbound=0 mismatches=0 partial=1   rc=0
```

A `run:` row carrying 41 non-existent ids would MATCH `items=41` (N27/N34) and any `=0` literal without
measuring anything; `--only` with exactly the passing 20 items would publish `bound_run=20` (N28/N29)
circularly. I did not use either; both are recorded as gameability, not as evidence.

## 4. Acceptance receipts

Counter runs over a private clone at `7822e1bfdbbba9c025b2e314d5e0f99d7e9e5fee` (origin removed) with
only the two rows of §1 appended, `--base 85b61a15… --list-rev 3ec84fc8… --only N27,…,N34`:

```
v2: ITEM N27 … binding=record MATCH census/round-31/records/c1-after-a4.txt:43
    ITEM N32 … binding=record MATCH census/round-31/records/c1-before.txt:43
    ITEM N28,N29,N30,N31,N33,N34 … binding=- UNBOUND
    SUMMARY items=8 bound_run=0 bound_record=2 bound_field=0 withdrawn=0 unbound=6 mismatches=6
v1: identical verdicts (same two MATCH, same six UNBOUND)
```

So the two delivered rows are stable under **both** counters; the six unbound items are the structural
residue of §3, not an unfinished edit.

## 5. What this means for the C1 target

`unbound=0 mismatches=0 withdrawn<=8` cannot be reached for line 422 under the frozen rules: the maximum
is 2 MATCH, and `withdrawn:` is unavailable because the definition requires that no observable shows the
integer, while `c1-after-a4.txt:43` and `c1-before.txt:43` demonstrably do. I propose no predicate,
target or item change (data exists). [INFERENCE] Unless the L1 can bind these six from an observable I
could not find, the C1 claim lands as missed with the root cause in §3.
