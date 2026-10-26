# C1 capability-cell bindings — items L30–L41 (round 31, wave 1)

Seat: SwarmExecutor05. Claim C1 (calibration), axis calibration 7.
Base: `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` (branch master). Enumeration: `census/round-31/c1-cells.tsv` at
prereg list-rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`. Counter: `tools/souji-capability-cells.py`
(frozen at the preregistration). Measured revision for run bindings: the current lane tip
`1b811368461785040e955f41f9c97e62f61fd67c` (SCORECARD.md unchanged since base: `git diff --stat
9f17a1e..1b81136 -- SCORECARD.md` is empty).

## Exact rows to append (ready for the L1 to paste after the base SCORECARD bytes)

```
### Round 31 capability-cell supersessions

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L30 | SCORECARD.md:171 | 8/8 | run: python3 tools/souji-declared-evidence.py --selftest | Re-running the base cell command at the measured revision prints selftest=8/8, so the cell literal is shown by a run. |
| L31 | SCORECARD.md:172 | 8/8 | run: python3 tests/fixtures/r23-receipt-run.py | Re-running the base cell fixture at the measured revision prints selftest=8/8, so the cell literal is shown by a run. |
| L32 | SCORECARD.md:173 | 15/15 | run: python3 tests/fixtures/r23-record-agreement.py | The fixture has grown to fifteen cases and prints selftest=15/15, restating the cell's stale 9/9 as the observed count. |
| L33 | SCORECARD.md:174 | cases=12 pass=12 | run: python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py | The debris-census fixture now prints cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED, restating the stale 8/8. |
| L34 | SCORECARD.md:174 | cases=8 pass=4 | record: census/round-24/records/c1-control-stub.tsv | The round-24 lesson cites this stub-control receipt, whose own notation cases=8 pass=4 restates the cell's stub control 4/8. |
| L35 | SCORECARD.md:175 | cases=9 pass=9 | run: python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py | The fixture requires --tool and prints cases=9 pass=9 control=FALSE-GREEN-REJECTED, so the cell count is shown by a run. |
| L36 | SCORECARD.md:313 | cases=20 pass=20 | run: python3 -B tests/fixtures/r29-registry-agreement.py | Re-running the base cell command at the measured revision prints cases=20 pass=20 control=FALSE-GREEN-REJECTED. |
| L37 | SCORECARD.md:313 | cases=20 pass=8 | record: census/round-29/records/c1-fixture-red-before.txt | The round-29 lesson cites this v1 red-before receipt, whose cases=20 pass=8 restates the cell's v1 tool 8/20. |
| L38 | SCORECARD.md:314 | cases=15 pass=15 | run: bash tests/fixtures/r28-wave-evidence-capture.sh | Re-running the base cell command at the measured revision prints cases=15 pass=15 control=TAMPER-REJECTED. |
| L39 | SCORECARD.md:314 | cases=15 pass=8 | record: census/round-29/records/c2-fixture-red-before.txt | The round-29 lesson cites this base-tool red-before receipt, whose cases=15 pass=8 restates the cell's base tool 8/15. |
| L40 | SCORECARD.md:355 | cases=7 pass=7 | run: python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py | Re-running the base cell command at the measured revision prints cases=7 pass=7 control=FALSE-GREEN-REJECTED. |
| L41 | SCORECARD.md:355 | cases=7 pass=3 | record: census/round-30/records/c2-fixture-red-before.txt | The cell names this red-before receipt, whose cases=7 pass=3 restates the base gate's 3/7. |
```

## Provenance of each base literal (writing commit, from `git log -S` and `git blame` at base)

| item | base line | base literal | writing commit | run record the commit cites / the record bound |
|---|---|---|---|---|
| L30 | 171 | 8/8 | `70af563` (r22 bookkeeping) | base cell command, re-run rc=0 → `selftest=8/8` |
| L31 | 172 | 8/8 | `4765250` (r23 instruments), line re-appended at `a529c76` (r26) | fixture re-run rc=0 → `selftest=8/8` |
| L32 | 173 | 9/9 | `4765250` (r23 instruments) | fixture re-run rc=0 → `selftest=15/15` (grew) |
| L33 | 174 | 8/8 | `315422b` (r24 final), row re-appended at `07f83e6` (r26) | fixture re-run rc=0 → `cases=12 pass=12 …` |
| L34 | 174 | 4/8 | `315422b` (r24 final), row re-appended at `07f83e6` (r26) | `census/round-24/records/c1-control-stub.tsv`, cited by `corpus/lessons/round-24.md:18` |
| L35 | 175 | 9/9 | `315422b` (r24 final), row re-appended at `07f83e6` (r26) | fixture re-run with its required `--tool` rc=0 → `cases=9 pass=9 …` |
| L36 | 313 | cases=20 pass=20 | `de874ee` (r29) | fixture re-run rc=0 → `cases=20 pass=20 …` |
| L37 | 313 | 8/20 | `de874ee` (r29) | `census/round-29/records/c1-fixture-red-before.txt`, cited by `corpus/lessons/round-29.md:60` |
| L38 | 314 | cases=15 pass=15 | `ed270c4` (r28), rewritten at `de874ee` (r29) | fixture re-run rc=0 → `cases=15 pass=15 …` |
| L39 | 314 | 8/15 | `de874ee` (r29) | `census/round-29/records/c2-fixture-red-before.txt`, cited by `corpus/lessons/round-29.md:61` |
| L40 | 355 | cases=7 pass=7 | `393b011` (r30) | fixture re-run rc=0 → `cases=7 pass=7 …` |
| L41 | 355 | 3/7 | `393b011` (r30) | `census/round-30/records/c2-fixture-red-before.txt`, named by the cell and by `corpus/lessons/round-30.md:65` |

Record blobs verified identical base→tip (`rev-parse <rev>:path`):

```
census/round-24/records/c1-control-stub.tsv        6a06c0337edd18b6c0df6591d7686bd47ce80851 SAME
census/round-29/records/c1-fixture-red-before.txt  aa45f35b5a7f2e67a37abf3aa0ac65127e091d2c SAME
census/round-29/records/c2-fixture-red-before.txt  55d40a9d35c3e51ede03d669484570451c1552d9 SAME
census/round-30/records/c2-fixture-red-before.txt  7aaa3551c57633633cd1e0de170697eb232f3257 SAME
```

Each record states the base literal in its own notation with exactly the base integers: `4/8` → `cases=8 pass=4`;
`8/20` → `cases=20 pass=8`; `8/15` → `cases=15 pass=8`; `3/7` → `cases=7 pass=3`. Every record is under the
item's `rounds` set, carries no `waves`/`transcripts` path component, and is the pre-round receipt the writing
round cited — not a file found by grepping the digits.

## Disclosure: L35 invocation

The base cell names the fixture without its required argument:
`python3 -B tests/fixtures/r24-coverage-agreement.py` → rc=2,
`error: the following arguments are required: --tool`. The row therefore supplies
`--tool tools/souji-coverage-agreement.py`, the fixture's own usage line
(`tests/fixtures/r24-coverage-agreement.py:14`), and states the printed line. This corrects the invocation,
not the predicate; the base literal 9/9 is preserved as the observed `cases=9 pass=9`.

## Acceptance proof (scratch clone, origin removed)

Scratch clone `/fast/scratch/hyaku/souji-r31/C1BindE/clone` (cloned `--no-local` from the lane, `origin`
removed, checked out at `1b811368461785040e955f41f9c97e62f61fd67c`, scratch identity set with
`git -C` inside scratch), rows appended under `### Round 31 capability-cell supersessions`, committed as
`af9c0806c2df687b90560af1577cde9ed1ff917a` ("r31 C1 bindings L30-L41 (scratch proof)").

Command (run twice, identical output both times):

```
python3 -B tools/souji-capability-cells.py --root /fast/scratch/hyaku/souji-r31/C1BindE/clone \
  --rev af9c0806c2df687b90560af1577cde9ed1ff917a \
  --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
  --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 \
  --only L30,L31,L32,L33,L34,L35,L36,L37,L38,L39,L40,L41 \
  --scratch /fast/scratch/hyaku/souji-r31/C1BindE/cnt
```

Run 1 and run 2 output (byte-identical):

```
ITEM	L30	SCORECARD.md:171	literal=8/8	superseded	binding=run	MATCH	python3 tools/souji-declared-evidence.py --selftest rc=0 observed=selftest=8/8
ITEM	L31	SCORECARD.md:172	literal=8/8	superseded	binding=run	MATCH	python3 tests/fixtures/r23-receipt-run.py rc=0 observed=selftest=8/8
ITEM	L32	SCORECARD.md:173	literal=15/15	superseded	binding=run	MATCH	python3 tests/fixtures/r23-record-agreement.py rc=0 observed=selftest=15/15
ITEM	L33	SCORECARD.md:174	literal=cases=12 pass=12	superseded	binding=run	MATCH	python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py rc=0 observed=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
ITEM	L34	SCORECARD.md:174	literal=cases=8 pass=4	superseded	binding=record	MATCH	census/round-24/records/c1-control-stub.tsv
ITEM	L35	SCORECARD.md:175	literal=cases=9 pass=9	superseded	binding=run	MATCH	python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py rc=0 observed=cases=9 pass=9 control=FALSE-GREEN-REJECTED
ITEM	L36	SCORECARD.md:313	literal=cases=20 pass=20	superseded	binding=run	MATCH	python3 -B tests/fixtures/r29-registry-agreement.py rc=0 observed=cases=20 pass=20 control=FALSE-GREEN-REJECTED
ITEM	L37	SCORECARD.md:313	literal=cases=20 pass=8	superseded	binding=record	MATCH	census/round-29/records/c1-fixture-red-before.txt
ITEM	L38	SCORECARD.md:314	literal=cases=15 pass=15	superseded	binding=run	MATCH	bash tests/fixtures/r28-wave-evidence-capture.sh rc=0 observed=cases=15 pass=15 control=TAMPER-REJECTED
ITEM	L39	SCORECARD.md:314	literal=cases=15 pass=8	superseded	binding=record	MATCH	census/round-29/records/c2-fixture-red-before.txt
ITEM	L40	SCORECARD.md:355	literal=cases=7 pass=7	superseded	binding=run	MATCH	python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py rc=0 observed=cases=7 pass=7 control=FALSE-GREEN-REJECTED
ITEM	L41	SCORECARD.md:355	literal=cases=7 pass=3	superseded	binding=record	MATCH	census/round-30/records/c2-fixture-red-before.txt
SUMMARY items=12 bound_run=8 bound_record=4 unbound=0 mismatches=0 partial=1 rev=af9c0806c2df687b90560af1577cde9ed1ff917a
```

RC=0 both times. All 12 assigned items read MATCH.

## Baseline the rows remove (measured, not copied)

`python3 -B tools/souji-capability-cells.py --root <lane> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
--base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496a…` printed
`SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=9f17a1ef…`, matching the frozen
baseline. The same 12 items before the rows: L30/L31/L36/L38/L40 MATCH; L32/L33/L35 RUN-MISMATCH;
L34/L37/L39/L41 UNBOUND.

## Risks / notes for the L1

- The target is global (`unbound=0 mismatches=0` over 41); this delivery supplies 12 of 41. The other items
  are other seats' scope.
- L32 (`15/15`) and L33 (`cases=12 pass=12`) restate counts that grew since the cells were written; the row
  literal is the value the committed fixture prints at `1b81136`. If a later commit in this round changes a
  fixture, the row literal must be re-measured before landing; the counter then reads RUN-MISMATCH.
- Rows for L30/L31/L36/L38/L40 restate literals whose base cells already match, so the binding is explicit in
  the cell record rather than inherited from the base row; removing them would not break those five items.
- No tool installs or upgrades were performed; no `pacman` transaction.
