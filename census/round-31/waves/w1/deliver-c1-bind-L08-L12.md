# C1 capability-cell bindings — items L08–L12 (round 31, wave 1)

Seat SwarmExecutor02. Claim C1 (calibration; axis calibration 7, the lowest non-retired axis). Read-only
seat: this delivery and the seat report `.ufo/waves/round-31/w1/SwarmExecutor02.md` are the only lane writes;
lane git index, jj state and every other file are untouched.

Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` (branch master). Enumeration `census/round-31/c1-cells.tsv`
read at prereg list-rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`. Counter `tools/souji-capability-cells.py`
(frozen by the preregistration). Measured revision for the two run rows: lane tip
`1b811368461785040e955f41f9c97e62f61fd67c`; `git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` is empty, so
the base line numbers are the tip's line numbers.

**Literal notation warning.** The L08/L09/L10 literals contain a literal TAB (0x09) between `total=…` and
`pass=…`. The bound records are tab-separated summary lines and the counter's record branch compares raw
bytes; a tab expanded to spaces reads RECORD-MISMATCH (negative control measured below). The fenced block is
byte-identical to the block committed in the scratch proof apart from its leading blank separator line
(compared byte-for-byte; the fenced content carries 3 tab bytes, one per record literal). Keep one blank line
between the end of the base SCORECARD bytes and the heading, as the proof commit does.

## Exact rows to append

Append after the last byte of the base SCORECARD.md (the counter requires the base bytes as an exact prefix).

```
### Round 31 capability-cell supersessions

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L08 | SCORECARD.md:159 | total=32	pass=32 | record: census/round-21/read-fixture-after.txt | r21 read-fixture-after.txt is the read-fixture run capture whose SUMMARY states total=32 pass=32, the cell's read32/32. |
| L09 | SCORECARD.md:159 | total=32	pass=18 | record: census/round-21/read-fixture-before.txt | r21 read-fixture-before.txt runs that same fixture against the base auditor named in its COMMAND line and states total=32 pass=18, the cell's base18/32. |
| L10 | SCORECARD.md:159 | total=4	pass=4 | record: census/round-21/render-edges-after.txt | r21 render-edges-after.txt is the renderer-fixture capture whose SUMMARY states total=4 pass=4, the cell's renderer4/4. |
| L11 | SCORECARD.md:160 | total=29 failed=0 | run: python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh | Re-running the base cell command at the measured revision prints SUMMARY total=29 failed=0, restating the cell's 29/0 in the fixture's own notation. |
| L12 | SCORECARD.md:161 | total=35 failed=0 | run: bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools | Re-running the base cell command at the measured revision prints SUMMARY total=35 failed=0 skipped=2, restating the cell's 35/0 in the fixture's own notation. |
```

## Provenance of each base literal (writing commit → the record it committed or cited → chosen binding)

| item | base line | base literal | writing commit | what the literal is | binding |
|---|---|---|---|---|---|
| L08 | 159 | `32/32` | `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe` (r21, "complete claims, independent oracle and scoped falsification evidence"); `af73b8ba92fa2783d9f4653bd504233939daa2d6` (r22, 2026-10-25) changed only `literal32/32` → `read32/32` | read fixture pass/total: `census/round-21/read-fixture-after.txt` line 34 `SUMMARY total=32 pass=32 fail=0 base_discriminating=14`, COMMAND line names `tests/fixtures/r21-read-root.py` | record |
| L09 | 159 | `18/32` | same two commits | the same fixture run against the base auditor: `census/round-21/read-fixture-before.txt` line 34 `SUMMARY total=32 pass=18 fail=14`, COMMAND line names `--tool /var/tmp/souji-r21-base-auditor.py` | record |
| L10 | 159 | `4/4` | same two commits | renderer fixture: `census/round-21/render-edges-after.txt` line 5 `SUMMARY total=4 pass=4 fail=0` | record |
| L11 | 160 | `29/0` | `d98065ded46b27cb8f135255dfda72b1936e0743` (r17) | the row cites `census/round-17/c1-matrix-4f48343.json`, whose `arms.changed["r17-hygiene"]` records `total` 29, `failed` 0 over 29 PASS case verdicts; the fixture prints `SUMMARY total=29 failed=0` | run |
| L12 | 161 | `35/0` | `d98065ded46b27cb8f135255dfda72b1936e0743` (r17) | `census/round-17/jj-receipts-4f48343.txt` (the record the cell names by glob) ends `SUMMARY total=35 failed=0 skipped=0`; the fixture now prints `total=35 failed=0 skipped=2` | run |

Record identity beyond provenance: the `read32` and `render4` command entries of
`census/round-21/final-code-verification.json` carry stdout byte-equal to the CASE+SUMMARY block of the two
`.txt` captures (that JSON is the record `corpus/lessons/round-21.md:192` names as the holder of
"read32/32, renderer4/4"). The `.txt` captures are bound instead because their bytes carry the summary in a
plain form (`total=…`/`pass=…`), not the JSON's escaped form.

## Why L08–L10 take a record binding and not a run binding

The frozen counter admits a `run:` row only when the script's basename stem occurs on the item's base
SCORECARD line. At base there are 231 paths under `tools/` and `tests/fixtures/`; **zero** of their basename
stems occur on SCORECARD.md:159. Lines 160 and 161 do contain the stems the run rows use
(`r17-census-hygiene`, `r17-jj-receipts`). Measured:

```
paths_under_tools_and_fixtures= 231
stems_hit_on_line159= 0
```

## Record blobs unchanged base → tip

```
census/round-21/read-fixture-after.txt   63ed0ae4803b7cf3d5073f591946e2ff3a9d8be1 SAME
census/round-21/read-fixture-before.txt  3bfe37c1545981448a7c2460fc15807196ce7992 SAME
census/round-21/render-edges-after.txt   41998d406fec9725ffb9b4a9fbdf0ad138ee2e59 SAME
```

Each is under `census/round-21/` (in the items' `rounds` set `16,20,21`), carries no `waves`/`transcripts`
path component, and restates the base literal with exactly its integers (`32/32` → `total=32 pass=32`;
`18/32` → `total=32 pass=18`; `4/4` → `total=4 pass=4`).

## Baseline the rows remove (measured at base, not copied)

`python3 -B tools/souji-capability-cells.py --root <lane> --rev 9f17a1ef… --base 9f17a1ef… --list-rev
1d45496a… --only L08,L09,L10,L11,L12`:

```
ITEM	L08	SCORECARD.md:159	literal=32/32	base-cell	binding=-	UNBOUND
ITEM	L09	SCORECARD.md:159	literal=18/32	base-cell	binding=-	UNBOUND
ITEM	L10	SCORECARD.md:159	literal=4/4	base-cell	binding=-	UNBOUND
ITEM	L11	SCORECARD.md:160	literal=29/0	base-cell	binding=run	RUN-MISMATCH	python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh rc=0 observed=SUMMARY total=29 failed=0
ITEM	L12	SCORECARD.md:161	literal=35/0	base-cell	binding=run	RUN-MISMATCH	bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
SUMMARY items=5 bound_run=0 bound_record=0 unbound=3 mismatches=5 partial=1 rev=9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
```

## Acceptance proof (scratch clone, origin removed)

Clone `/fast/scratch/hyaku/souji-r31/C1BindB/r.1skKGk/c` (`git clone -q --no-local` from the lane, `origin`
removed, `rev-parse --show-toplevel` printed that clone), checked out at tip
`1b811368461785040e955f41f9c97e62f61fd67c`, rows appended under `### Round 31 capability-cell
supersessions`, committed with a scratch-only identity as `60d8f14301c6d314816988c594d62934a61e5b78`
("r31 C1 bindings L08-L12 (scratch proof)"), tree clean.

Command, run twice with byte-identical output (`cmp` silent), rc=0 both times:

```
python3 -B tools/souji-capability-cells.py --root /fast/scratch/hyaku/souji-r31/C1BindB/r.1skKGk/c \
  --rev 60d8f14301c6d314816988c594d62934a61e5b78 \
  --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
  --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 \
  --only L08,L09,L10,L11,L12 \
  --scratch /fast/scratch/hyaku/souji-r31/C1BindB/cnt
```

```
ITEM	L08	SCORECARD.md:159	literal=total=32	pass=32	superseded	binding=record	MATCH	census/round-21/read-fixture-after.txt
ITEM	L09	SCORECARD.md:159	literal=total=32	pass=18	superseded	binding=record	MATCH	census/round-21/read-fixture-before.txt
ITEM	L10	SCORECARD.md:159	literal=total=4	pass=4	superseded	binding=record	MATCH	census/round-21/render-edges-after.txt
ITEM	L11	SCORECARD.md:160	literal=total=29 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh rc=0 observed=SUMMARY total=29 failed=0
ITEM	L12	SCORECARD.md:161	literal=total=35 failed=0	superseded	binding=run	MATCH	bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
SUMMARY items=5 bound_run=2 bound_record=3 unbound=0 mismatches=0 partial=1 rev=60d8f14301c6d314816988c594d62934a61e5b78
```

## Negative control (tab bytes are load-bearing)

Same clone, same rows with each literal TAB replaced by a space, committed as
`db93191858e245289d0bc82468a1d0e4cd02e0e7`:

```
ITEM	L08	SCORECARD.md:159	literal=total=32 pass=32	superseded	binding=record	RECORD-MISMATCH	census/round-21/read-fixture-after.txt
ITEM	L09	SCORECARD.md:159	literal=total=32 pass=18	superseded	binding=record	RECORD-MISMATCH	census/round-21/read-fixture-before.txt
ITEM	L10	SCORECARD.md:159	literal=total=4 pass=4	superseded	binding=record	RECORD-MISMATCH	census/round-21/render-edges-after.txt
SUMMARY items=3 bound_run=0 bound_record=0 unbound=0 mismatches=3 partial=1 rev=db93191858e245289d0bc82468a1d0e4cd02e0e7
```

So the three record bindings are not a grep coincidence: the literal is exactly the record's own
tab-separated notation and the counter re-derives it from the unchanged bytes.

## Risks / notes for the L1

- **Tab preservation.** After integrating, confirm three tabs are present (`grep -c $'total=[0-9]*\tpass=' SCORECARD.md`
  → expected 3) and re-run the counter; each item then re-derives its literal from the committed record.
- **Run rows depend on fixture bytes.** If any seat changes `tests/fixtures/r17-census-hygiene.py`,
  `tests/fixtures/r17-jj-receipts.sh`, `tools/souji-census.sh` or the `--tool-dir tools` surface this round,
  re-measure L11/L12 before landing; the counter then reads RUN-MISMATCH rather than a silent drift.
- **L12 skipped count moved 0→2** between the r17 record and now (total 35 and failed 0 unchanged). The row
  literal states the unchanged pair; the disclosure is here, not hidden.
- **Alternative L12 binding**, if a record is preferred: `census/round-17/jj-receipts-4f48343.txt` is
  unchanged and contains `total=35\tfailed=0`; it was not used because the run shows the count is current.
- **Scope.** These are 5 of the 41 enumerated items; the global C1 target (`unbound=0 mismatches=0`) also
  needs the other seats' rows. Sibling delivery `deliver-c1-bind-L30-L41.md` covers L30–L41.
- No tool install or upgrade, no `pacman` transaction, no lane git/jj mutation; scratch removed.
