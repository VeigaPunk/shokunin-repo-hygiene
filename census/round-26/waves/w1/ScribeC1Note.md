# ScribeC1Note — C1 append-only note + Round 26 LOG block (scribe)

## Status

STATUS: PASS — both drafts delivered; while computing the old→new map I found a live C1 defect
(amendment-2 span 5 absent at the landing), which the wave repaired at `07f83e6` after my first
draft landed as `d6fe8a1`; the landed note is now one commit stale in its own defect class, and a
paste-ready append-only delta (`R26-C1b`) plus the corrected LOG block are in the deliverable.

## Evidence

HEAD at start `4453128`; HEAD at finish `07f83e6` (lane advanced `d6c13b0`, `ea0bbe6`, `d6fe8a1`,
`07f83e6` during the run). All commands read-only; no scratch tree needed (no repo created).

Frozen counters, same instrument both ends (`census/round-26/c1-counter.sh`, tool sha256 `c8dbb76c…`):

```text
$ git show 0eca7c8:SCORECARD.md | grep -cE '^(Insert the table below directly above|Optional same-landing correction)'   -> 2
$ git show 0eca7c8:SCORECARD.md | awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}'            -> 17 175 231
$ bash census/round-26/c1-counter.sh                                                                                     -> markers=0 / headings=17 44 78   (at 4453128 AND at 07f83e6)
```
`census/round-26/records/c1-before.tsv`: rev `12fd90bcd9cdfab495e178023eeaa838a977fcbe`, `markers=2`,
`headings=17 175 231`; SCORECARD bytes identical to base `0eca7c8` (`git diff --stat 0eca7c8 12fd90b -- SCORECARD.md` empty).
`census/round-26/records/c1-after.tsv`: rev `a529c762c81272d398727e6a623c801a230ac157`, `markers=0`,
`headings=17 44 78`.

Layout provenance (`a6d2d15` = r25 base = r24-tip bytes):

```text
$ git show a6d2d15:SCORECARD.md | awk 'NR==92||NR==180||NR==181||NR==224||NR==225'
 92  | blob-bound receipts (r23) ...
 180 | C3 receipt verify/run symmetry ...
 181 | assimilation (rides inside C1; no claim slot) ...
 224 | - **r24 (planned r23) — done, ...**
 225 | - **r25 (planned r24):** ...
$ git show 0eca7c8:SCORECARD.md | sed -n '92p;181p;182p;225p;226p'      -> the same five contents, four at +1
$ git log -S'- **r25 — attempted, honest stop' -- SCORECARD.md          -> 728b2ce (inserted at :136)
$ git log -S'Insert the table below directly above' -- SCORECARD.md     -> 315422b (added), a529c76 (removed)
```

Amendment-2 span check, base `0eca7c8` vs HEAD `07f83e6` (line-range compare, `python3 -B`):

```text
span1 1-16     byte_equal=True
span2 231-254  byte_equal=True  (tip 17-40)
span3 175-207  byte_equal=True  (tip 44-76)
span4 17-62    byte_equal=True  (tip 78-123)
span7 138-169  byte_equal=True  (tip 204-235)
span5 rows     byte_equal=True at 07f83e6; ABSENT at a529c76 (:155-156 empty, last row :154)
span6 bullets  tip :201-202 (were :199-200 at a529c76)
```

Deliverable: `.ufo/waves/round-26/w1/c1-append-note.md` (drafted this run; superseded text of my
first draft is already landed at `d6fe8a1`). No tool installs or upgrades. No scratch directories
created. Writes: this report and the deliverable only.

## Findings

1. **The five `superseded by SCORECARD.md:<n>` numbers are r25-base coordinates, and four were
   already stale at the round's frozen base.** `SCORECARD.md:36-40` (tip) were written against the
   layout at `a6d2d15` (= r24 tip `315422b`), where `:180`=C3 row, `:181`=assimilation row,
   `:224`=r24 bullet, `:225`=r25 bullet, `:92`=blob-bound row. `728b2ce` inserted the
   `- **r25 — attempted, honest stop …` bullet at `SCORECARD.md:136`, shifting every later line by
   one; the scaffold block itself was introduced earlier, at `315422b`. So the defect is one
   insertion in r25's own landing, not the r26 cleanup.
2. **Old→new map (delivered):** `:181`→:51, `:180`→:50, `:92`→:153, `:224`→:201, `:225`→:202 at
   HEAD, with `:224`/`:225` at :199/:200 between `a529c76` and `07f83e6`. The five lines themselves
   moved `0eca7c8` 250-254 → 36-40 with bytes unchanged. Independent agreement: the semantic column
   of `.ufo/waves/round-26/w1/c1-line-map.md` matches all five post-edit lines; it attributes the
   +1 to "r25 inserted the scaffold", whereas the measured cause is the r25 planned bullet at :136
   (`git log -S` evidence above).
3. **C1's first landing omitted amendment-2 span 5.** At `a529c76` and `4453128` the two r24
   capability rows (`debris census (r24)`, `coverage-map agreement (r24)`; fenced originals
   `0eca7c8:213-214`) were absent — `grep 'debris census (r24)' SCORECARD.md` returned 0 hits and
   the last capability row was `record agreement audit (r23)` at :154. `07f83e6` repaired it; rows
   are now byte-equal to the base fence at :155-156 and every other protected span still matches.
4. **The K1/K2 instrument is blind to span 5.** `bash census/round-26/c1-counter.sh` printed
   `markers=0` / `headings=17 44 78` at `4453128` (rows missing) and at `07f83e6` (rows present) —
   identical output. The label therefore scores green on a contract it does not test; the omission
   was caught by a span check, not by scoring. Counter-value dispute is not claimed; this is an
   instrument-coverage gap for the revenger/L1 to rule on.
5. **The landed note (`d6fe8a1`, heading now `SCORECARD.md:239`) is stale in its own defect class.**
   Its post-C1 column names :199/:200 for the `:224`/`:225` rows; `07f83e6` inserted two lines at
   :155-156, moving those bullets to :201/:202. The delivered `R26-C1b` paragraph is an append that
   states the shift rather than rewriting the table (the section is append-only). `:50`, `:51`,
   `:153` remain correct because they sit above the insertion.
6. **LOG.md has no Round 26 block yet**; the tail is the Round 25 block (`LOG.md:1723`). The block
   drafted in the deliverable is updated to the post-repair state and carries `RECEIPT-PENDING` for
   every fact I did not measure (C2/C3 receipts, SOURCES deltas, wave seats, R26-C1b landing,
   mistake-row ids, admission verdict).
7. **Limit.** HEAD advanced four commits during this run and the map is a measurement, not a
   contract: the note's own closing instruction is to re-derive per cell at the landing rev. A
   C1 green-after receipt re-run at `07f83e6` was not performed by this seat (its literal triple is
   already the same; its bound rev is `a529c76`) — left as `RECEIPT-PENDING` in the LOG block.
