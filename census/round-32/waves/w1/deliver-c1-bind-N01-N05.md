# C1 bindings N01-N05 — delivery (round 32 w1, SwarmExecutor01)

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; list-rev (prereg) `3ec84fc81b3243429c834a051880b0bcde06291c`.
All counters run on a private `git clone --no-local` with `origin` removed, scratch under
`/fast/scratch/hyaku/souji-r32/C1BindA/`; SCORECARD.md at base and at the prereg commit is the same blob
(`771250313133d5f38b7f51a0922212db50990520`), verified with `git rev-parse`.

Verdict state: `unbound=0 mismatches=0 withdrawn=2`, exit 0, under **v1 and v2** for these five items.
The two withdrawals are forced by A0(a) and consume 2 of the round's 8-item withdrawal cap; see "Why N02/N03
are withdrawn" and the falsifier states below.

## Rows to append (verbatim, under `### Round 32 capability-count bindings`)

```markdown
| item | base line | literal | binding | reason |
|---|---|---|---|---|
| N01 | SCORECARD.md:147 | 246 rows | field: census/round-1/census-summary.json rows_total=246 | r1 commit ab7f2f706f35f466b515b474fc9c76e0ddd71ae2 wrote the cell and its own census-summary.json records rows_total 246 for the 246-row census.tsv. |
| N02 | SCORECARD.md:151 | 33 rows | withdrawn: no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37 | r13 commit 6ed10a7cd6c7b26f8068dd6e02497e860f9c4317 wrote the baseline counts from census/round-13/baseline-measures.md:15, which the cell does not cite; corpus/SOURCES.md at 31984f473ce4bdab61a99b16cca194b28108cb81 still holds 33 rows. |
| N03 | SCORECARD.md:151 | 16 mined | withdrawn: no cited record holds 16 mined since verification.json prints the ending census mined 20 | the same r13 commit took mined 16 from the uncited baseline-measures.md:15 and the cell's pointer verification.json records sources.statuses.mined 20 for its 37-row ending census. |
| N04 | SCORECARD.md:151 | 15 queued | field: census/round-13/verification.json sources.statuses.queued=15 | the cell's own r13 pointer records its sources status histogram queued 15, the value the 31984f473ce4bdab61a99b16cca194b28108cb81 baseline shows. |
| N05 | SCORECARD.md:151 | 2 rejected | field: census/round-13/verification.json sources.statuses.rejected=2 | the same pointer records rejected 2 in that status histogram, matching the 31984f473ce4bdab61a99b16cca194b28108cb81 baseline. |
```

## How each integer was produced

`git -C LANE log -S'<token>' --format='%H %ad %s' -- SCORECARD.md` over the base blob.

- **N01 = 246 rows, SCORECARD.md:147.** Cell: "`census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows)".
  Writing commit **ab7f2f706f35f466b515b474fc9c76e0ddd71ae2** (r1, 2026-10-18), which added the capability row itself.
  Record it committed: `census/round-1/census-summary.json` line 6 `"rows_total": 246,` (blob at base and REV unchanged).
  Binding kind `field` because the JSON key carries the unit word and the integer together (`rows_total`).
  Cross-check of the same quantity in the cell: `census/round-1/census.tsv` has 246 data rows.
- **N02 = 33 rows, N03 = 16 mined, N04 = 15 queued, N05 = 2 rejected, SCORECARD.md:151.** Cell:
  "baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f473ce4bdab61a99b16cca194b28108cb81".
  Writing commit **6ed10a7cd6c7b26f8068dd6e02497e860f9c4317** (r13), which added the row and, in the same commit,
  `census/round-13/baseline-measures.md`; the counts are its table line 13 (`SOURCES rows / malformed / dup / enum` →
  33 / 0 / none / none) and line 15 (`SOURCES status mined/queued/rejected` → mined=16 queued=15 rejected=2).
  The full 40-hex baseline hash in the cell was expanded later, in 5ff5041b64964d4e6e8374b0eefb8b12010b9997 (r22);
  the four integers themselves date from 6ed10a7c.
  Independent re-derivation at the named baseline: `git show 31984f473ce4bdab61a99b16cca194b28108cb81:corpus/SOURCES.md`
  counted per status column → `rows=33 state mined=16 queued=15 rejected=2`. The cell is **correct**.
  - N04, N05 bind as `field` to the cell's own cited census `census/round-13/verification.json`
    (`sources.statuses.queued` = 15 at line 258, `sources.statuses.rejected` = 2 at line 259).
  - N02, N03 have no v2-legal binding; see below.

## Why N02/N03 are withdrawn (exhaustive, not lazy)

`census/round-13/verification.json` is the **only** blob under census/round-12 or round-13 that the cell cites
(basename on the base line; the line carries no `*` glob and no tools/ or tests/fixtures/ stem). It is the
*ending* source census (measured_commit 6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6, 37 rows):

```
sources.rows = 37            (line 250)
sources.tiers.A = 33         (line 252)
sources.statuses.mined = 20  (line 257)
sources.statuses.queued = 15 (line 258)
sources.statuses.rejected = 2 (line 259)
```

Sweep over all 34 eligible round-12/13 blobs (record-path rules from the counter, `cited()` against the base line 151):
only `census/round-13/verification.json` is cited; it has **0** lines where `33` stands within 3 non-alphanumeric
bytes of `rows` and **0** where `16` stands within 3 of `mined`. No tools/ or tests/fixtures/ basename stem occurs
on line 151, so no `run:` is legal either. Hence:
- N02: 33 is a row count and the cited record's row count is 37; `tiers.A = 33` is a tier count, not rows.
- N03: 16 is the baseline mined count and the cited record's mined count is 20 (the ending census).

The record that *does* hold both is `census/round-13/baseline-measures.md:13` (rows 33) and `:15` (mined=16) — added by
the same r13 commit — but the cell's evidence pointer does not name it, so A0(a) rejects it. This is a cell-pointer
defect, not a counter defect; the honest fix is an append-only correction to the cell's pointer list (the counter reads
row_text from the base line, so no appended text can cure it inside round 32).

## Acceptance runs (pasted output)

Private clone: `/fast/scratch/hyaku/souji-r32/C1BindA/r.8QIZQW/c` (origin removed, toplevel verified by the counter).
Scratch commit **97a9edbec07ca48309648bfa5898f9092d79aefe** = prereg 3ec84fc8 tree + the five rows above.

v2 (`c1-counter-v2.py`):

```
ITEM	N01	SCORECARD.md:147	literal=246 rows	binding=field	MATCH	census/round-1/census-summary.json rows_total=246
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=withdrawn	WITHDRAWN	no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=withdrawn	WITHDRAWN	no cited record holds 16 mined since verification.json prints the ending census mined 20
ITEM	N04	SCORECARD.md:151	literal=15 queued	binding=field	MATCH	census/round-13/verification.json sources.statuses.queued=15
ITEM	N05	SCORECARD.md:151	literal=2 rejected	binding=field	MATCH	census/round-13/verification.json sources.statuses.rejected=2
SUMMARY items=5 bound_run=0 bound_record=0 bound_field=3 withdrawn=2 unbound=0 mismatches=0 partial=1 rev=97a9edbec07ca48309648bfa5898f9092d79aefe
```

v1 (`c1-counter.py`), same rev and rows:

```
ITEM	N01	SCORECARD.md:147	literal=246 rows	binding=field	MATCH	census/round-1/census-summary.json rows_total=246
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=withdrawn	WITHDRAWN	no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=withdrawn	WITHDRAWN	no cited record holds 16 mined since verification.json prints the ending census mined 20
ITEM	N04	SCORECARD.md:151	literal=15 queued	binding=field	MATCH	census/round-13/verification.json sources.statuses.queued=15
ITEM	N05	SCORECARD.md:151	literal=2 rejected	binding=field	MATCH	census/round-13/verification.json sources.statuses.rejected=2
SUMMARY items=5 bound_run=0 bound_record=0 bound_field=3 withdrawn=2 unbound=0 mismatches=0 partial=1 rev=97a9edbec07ca48309648bfa5898f9092d79aefe
```

## Falsifier states (why these rows are not the cheapest path)

State A — the tempting value-matching fields, rev `10fc77bc367ac08e5fd15ea60236a55a522daaca`:

```
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=field	BAD-ROW(field-shape)	census/round-13/verification.json sources.tiers.A=33
ITEM	N03	SCORECARD.md:151	literal=20 mined	binding=field	BAD-ROW(field-shape)	census/round-13/verification.json sources.statuses.mined=20
SUMMARY items=2 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=2 partial=1 rev=10fc77bc367ac08e5fd15ea60236a55a522daaca
```

State B — the real record, cited or not, rev `3c51e7d18064c22336e9c083a55c9233e78067b2`:

v1 (`c1-counter.py`):

```
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=record	MATCH	census/round-13/baseline-measures.md:13
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=record	MATCH	census/round-13/baseline-measures.md:15
SUMMARY items=2 bound_run=0 bound_record=2 bound_field=0 withdrawn=0 unbound=0 mismatches=0 partial=1 rev=3c51e7d18064c22336e9c083a55c9233e78067b2
```

v2 (`c1-counter-v2.py`):

```
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=record	BAD-ROW(A0a-not-cited)	census/round-13/baseline-measures.md:13
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=record	BAD-ROW(A0a-not-cited)	census/round-13/baseline-measures.md:15
SUMMARY items=2 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=2 partial=1 rev=3c51e7d18064c22336e9c083a55c9233e78067b2
```

State B is the whole story: the exact record exists, v1 accepts it, and A0(a) refuses it because the cell does not
cite it. Withdrawing N02/N03 is the only state that satisfies both counters without touching the frozen predicate.

## Notes for the L1

- Appending these rows leaves `bound_field=3 withdrawn=2` for these five items; the remaining 39 items carry 6
  withdrawals of headroom.
- No v1 binding for N01–N05 uses `run:`; no item here needs the base blob of a script.
- No lane file was modified by this seat; the only writes are this delivery and `.ufo/waves/round-32/w1/SwarmExecutor01.md`.
