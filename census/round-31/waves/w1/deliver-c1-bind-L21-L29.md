# C1 bindings L21-L29 — append-only supersession rows (SwarmExecutor04, r31 w1)

Scope: items L21-L29 of `census/round-31/c1-cells.tsv` (base SCORECARD.md lines 166, 167, 168, 170 at
`9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`). Two of the three row families name a command, so L21, L22, L23,
L25 take `run:` rows and L24, L26 take `record:` rows because the auditor stem is not on line 168 and the
bare r20 fixture cannot print 78. L27 and L28 take `record:` rows from the accepted-matrix run's retained
stdout; no `tools/` or `tests/fixtures/` basename stem occurs anywhere on line 170, so a `run:` row there
would be `BAD-ROW(run-shape)`.

**L29 has no honest binding under the frozen rule and is deliberately left without a row.** Reproduced state,
the exhaustive sweep and the two controls are below. Target `unbound=0` is therefore not reached for L29 by
this seat; the honest options are the L1's call, and the frozen rule must not be relaxed after data.

## Byte-notation warning (integration-critical)

- The L27 literal carries the two bytes `\` `t` (a JSON *escape*), because
  `census/round-21/final-code-verification.json` stores its matrix stdout as JSON strings. Do not expand it to
  a TAB and do not drop the backslash.
- L21, L22, L23 and L25 literals are SUMMARY-notation restatements of the cells' slash literals: the commands
  print `total=4 failed=0`, `total=11 failed=0`, `total=13 failed=0`, `total=17 failed=0`; none prints `4/0`,
  `11/0`, `13/0`, `17/0` (red-before receipt below shows exactly that `RUN-MISMATCH`).
- L24 and L26 literals are the cell's own slash forms and are matched byte-for-byte.

Verify after appending, on the lane repo:

```
sed -n '/^### Round 31 capability-cell supersessions$/,$p' SCORECARD.md | cat -A | grep -E '^\| L2[0-9]'
```

The L27 row must show `scenarios=3\treplayed=3` with a literal backslash and the letter `t` (`cat -A` prints a
real TAB as `^I`; `^I` there means the literal was corrupted).

## Append block (verbatim; sha256 of the block below = `085c07c92a5d34494d55de7e89c95bf8c5dd3f314ebcd46950a1cbcd2469df2e`)

```
### Round 31 capability-cell supersessions

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L21 | SCORECARD.md:166 | total=4 failed=0 | run: python3 tests/fixtures/r19-carry-wrap.py | The named fixture still prints 4 cases and 0 failures (2 base-discriminating) at this revision, so the cell's 4/0 is restated in the SUMMARY notation the command emits. |
| L22 | SCORECARD.md:167 | total=11 failed=0 | run: python3 tools/souji-rev-pin.py --selftest | The named helper still prints 11 cases and 0 failures at this revision, so the cell's 11/0 is restated in the SUMMARY notation the command emits. |
| L23 | SCORECARD.md:167 | total=13 failed=0 | run: python3 tests/fixtures/r19-rev-pin.py | The named fixture still prints 13 cases and 0 failures (6 base-discriminating) at this revision, so the cell's 13/0 is restated in the SUMMARY notation the command emits. |
| L24 | SCORECARD.md:168 | 118/0 | record: census/round-21/r20-closure-excerpt.json | The r20 closure recheck retained in r21 states the auditor selftest at 118/0, and no run row is possible because the auditor's file stem does not occur on the base line. |
| L25 | SCORECARD.md:168 | total=17 failed=0 | run: python3 tests/fixtures/r19-seat-audit-shapes.py | The named fixture still prints 17 cases and 0 failures (12 base-discriminating) at this revision, so the cell's 17/0 is restated in the SUMMARY notation the command emits. |
| L26 | SCORECARD.md:168 | 78/0 | record: census/round-21/r20-closure-excerpt.json | The same closure recheck states the r20 oracle at 78/0 with 11 base-discriminating, while the fixture alone prints 66 cases because its 12 baseline cases need an uncommitted baseline auditor copy. |
| L27 | SCORECARD.md:170 | scenarios=3\treplayed=3 | record: census/round-21/final-code-verification.json | The record's matrix stdout for the accepted run states 3 scenarios replayed, with the field tab stored as the two bytes backslash t. |
| L28 | SCORECARD.md:170 | matched=18/18 | record: census/round-21/final-code-verification.json | The same record's matrix stdout states matched=18/18 for each of the three accepted source shapes. |
```

## Acceptance proof (scratch clone, origin removed)

Scratch: `/fast/scratch/hyaku/souji-r31/C1BindD/`. Clone parent: lane tip
`1b811368461785040e955f41f9c97e62f61fd67c` (SCORECARD.md byte-identical to base:
`git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` empty). The block was appended after one blank line and
committed in scratch as `4b8010d1850cac1c0ca5490739672edb5996ff41` (13 insertions, one file).

Red before (lane repo at the tip, no supersession rows):

```
$ python3 -B tools/souji-capability-cells.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1b811368461785040e955f41f9c97e62f61fd67c --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L21,L22,L23,L24,L25,L26,L27,L28,L29 --scratch /fast/scratch/hyaku/souji-r31/C1BindD/cnt0
ITEM	L21	SCORECARD.md:166	literal=4/0	base-cell	binding=run	RUN-MISMATCH	python3 tests/fixtures/r19-carry-wrap.py rc=0 observed=SUMMARY total=4 failed=0 base_discriminating=2
ITEM	L22	SCORECARD.md:167	literal=11/0	base-cell	binding=run	RUN-MISMATCH	python3 tools/souji-rev-pin.py --selftest rc=0 observed=SUMMARY total=11 failed=0
ITEM	L23	SCORECARD.md:167	literal=13/0	base-cell	binding=run	RUN-MISMATCH	python3 tests/fixtures/r19-rev-pin.py rc=0 observed=SUMMARY total=13 failed=0 base_discriminating=6
ITEM	L24	SCORECARD.md:168	literal=118/0	base-cell	binding=-	UNBOUND
ITEM	L25	SCORECARD.md:168	literal=17/0	base-cell	binding=-	UNBOUND
ITEM	L26	SCORECARD.md:168	literal=78/0	base-cell	binding=-	UNBOUND
ITEM	L27	SCORECARD.md:170	literal=3/3	base-cell	binding=-	UNBOUND
ITEM	L28	SCORECARD.md:170	literal=18/18	base-cell	binding=-	UNBOUND
ITEM	L29	SCORECARD.md:170	literal=18/18	base-cell	binding=-	UNBOUND
SUMMARY items=9 bound_run=0 bound_record=0 unbound=6 mismatches=9 partial=1 rev=1b811368461785040e955f41f9c97e62f61fd67c
rc=1
```

Proof, run twice (byte-identical output both times):

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-cells.py --root /fast/scratch/hyaku/souji-r31/C1BindD/cf --rev 4b8010d1850cac1c0ca5490739672edb5996ff41 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L21,L22,L23,L24,L25,L26,L27,L28,L29 --scratch /fast/scratch/hyaku/souji-r31/C1BindD/cnt1
ITEM	L21	SCORECARD.md:166	literal=total=4 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r19-carry-wrap.py rc=0 observed=SUMMARY total=4 failed=0 base_discriminating=2
ITEM	L22	SCORECARD.md:167	literal=total=11 failed=0	superseded	binding=run	MATCH	python3 tools/souji-rev-pin.py --selftest rc=0 observed=SUMMARY total=11 failed=0
ITEM	L23	SCORECARD.md:167	literal=total=13 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r19-rev-pin.py rc=0 observed=SUMMARY total=13 failed=0 base_discriminating=6
ITEM	L24	SCORECARD.md:168	literal=118/0	superseded	binding=record	MATCH	census/round-21/r20-closure-excerpt.json
ITEM	L25	SCORECARD.md:168	literal=total=17 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r19-seat-audit-shapes.py rc=0 observed=SUMMARY total=17 failed=0 base_discriminating=12
ITEM	L26	SCORECARD.md:168	literal=78/0	superseded	binding=record	MATCH	census/round-21/r20-closure-excerpt.json
ITEM	L27	SCORECARD.md:170	literal=scenarios=3\treplayed=3	superseded	binding=record	MATCH	census/round-21/final-code-verification.json
ITEM	L28	SCORECARD.md:170	literal=matched=18/18	superseded	binding=record	MATCH	census/round-21/final-code-verification.json
ITEM	L29	SCORECARD.md:170	literal=18/18	base-cell	binding=-	UNBOUND
SUMMARY items=9 bound_run=4 bound_record=4 unbound=1 mismatches=1 partial=1 rev=4b8010d1850cac1c0ca5490739672edb5996ff41
rc=1
```

Second run used `--scratch /fast/scratch/hyaku/souji-r31/C1BindD/cnt2` and printed the same nine ITEM lines and
the same SUMMARY line.

## Why each binding IS the row's evidence

| item | base literal | base-cell evidence at 9f17a1e | chosen binding | why this observable shows the count |
|---|---|---|---|---|
| L21 | 4/0 | line 166 names `tests/fixtures/r19-carry-wrap.py`; writing commit `1db7108d` added the row | `run: python3 tests/fixtures/r19-carry-wrap.py` | the fixture is the row's own case set and prints `SUMMARY total=4 failed=0 base_discriminating=2` at the proof rev, i.e. 4 cases and 0 failures |
| L22 | 11/0 | line 167 names `tools/souji-rev-pin.py --selftest`; writing commit `1db7108d` | `run: python3 tools/souji-rev-pin.py --selftest` | the helper prints `SUMMARY total=11 failed=0` at the proof rev |
| L23 | 13/0 | line 167 names `tests/fixtures/r19-rev-pin.py`; writing commit `1db7108d` | `run: python3 tests/fixtures/r19-rev-pin.py` | the fixture prints `SUMMARY total=13 failed=0 base_discriminating=6` at the proof rev |
| L24 | 118/0 | line 168 rewritten by `4eb2fda5` to `auditor selftest118/0` | `record: census/round-21/r20-closure-excerpt.json` | the r20 closure record the same r21 commit cites in its SCORECARD prose rechecks `auditor selftest 118/0`; the tool itself prints `SELFTEST pass=118 fail=0` today, but no superseding run row is legal because stem `souji-seat-audit` is absent from line 168 |
| L25 | 17/0 | line 168 `r19-seat-audit-shapes17/0 (base12)` | `run: python3 tests/fixtures/r19-seat-audit-shapes.py` | the fixture prints `SUMMARY total=17 failed=0 base_discriminating=12`, the same base-12 discriminant count the cell states |
| L26 | 78/0 | line 168 `r20-audit-contract78/0 (base11)` | `record: census/round-21/r20-closure-excerpt.json` | the record states `r20 oracle 78/0, 11 base-discriminating`; the fixture alone prints 66 because its 12 baseline cases require a baseline auditor blob that is not committed in the lane (sha256 62522acc matches the closure receipt), so no committed argv can print 78 |
| L27 | 3/3 | line 170 `census/round-21/accepted-matrix.json`3/3 | `record: census/round-21/final-code-verification.json` | the record holds the retained stdout of the accepted-matrix run (argv `--rev 195715439a08… --work /var/tmp/souji-r21-matrix-1957`, the same run accepted-matrix.json serializes) and states `scenarios=3 replayed=3` |
| L28 | 18/18 | line 170 `each18/18` | `record: census/round-21/final-code-verification.json` | the same stdout states `matched=18/18` for each of S1, S2, S3, i.e. 18 of 18 predicates in all three accepted source shapes |
| L29 | 18/18 | line 170 `remote-source-after.json18/18` | **none — no honest binding** | see below |

Record blobs are identical at base and at the proof rev: `census/round-21/r20-closure-excerpt.json`
`5cd2243dd0f30854752f2a4608ca146866ccfb95`, `census/round-21/final-code-verification.json`
`6483d98f7ea9bd7ddd1997648f64a143c1c56901` (the counter's own unchanged-blob check passed for both rows).

Located verbatim excerpts from bytes opened this run:

- `census/round-21/r20-closure-excerpt.json`, `closure.verification.rechecks`: `auditor selftest 118/0; r19-seat-audit-shapes 17/0 (12 base-disc)`
- `census/round-21/r20-closure-excerpt.json`, `closure.capabilities_added[0]`: `r20 oracle 78/0, 11 base-discriminating`
- `census/round-21/final-code-verification.json`, `matrix.stdout`: `SCENARIO\tS1\texit=0\tmatched=18/18\tsrc_sample_unchanged=yes`
- `census/round-21/final-code-verification.json`, `matrix.stdout`: `MATRIX\tscenarios=3\treplayed=3\tsummaries_equal=True`
- `tests/fixtures/r19-carry-wrap.py:235`: `SUMMARY total=%d failed=%d base_discriminating=%d`
- `tools/souji-rev-pin.py:374`: `SUMMARY total=%d failed=%d`

The accepted-matrix JSON the cell names states the same two facts only as fields
(`"scenarios": 3`, `"replayed": 3`, `matched_command_count: 18`) and carries neither `3/3` nor `18/18`, which is
why the exact-literal observable is the retained run stdout in the same-round record.

## L29 — no honest binding exists (reproduced state)

The base cell (SCORECARD.md:170 at `9f17a1e`, rewritten by `4eb2fda5`) states `remote-source-after.json18/18`.
The record it names, `census/round-21/remote-source-after.json`
(`f4123cf12614e43bc26e500a75befbcfadbe3bac`, unchanged base to proof rev), records that result as scalar
fields and never as a two-integer literal:

```
"expected_command_count": 18,
"matched_command_count": 18,
"observed_command_count": 18,
"all_matched": true,
```

The record's own 18-step receipts also never state `18/18`: the per-command `observed_summary` lines are
`SELFTEST\tpass=118\tfail=0`, `SUMMARY total=11 failed=0`, `SUMMARY\ttotal=78\tpass=78\tfail=0…`,
`SUMMARY total=17 failed=0…` and so on.

Exhaustive sweep (command run this session): every file under `census/round-20/` and `census/round-21/` was
scanned line by line for substrings whose only integer tokens are exactly two `18`s (the only literals the
counter can accept for base literal `18/18`). Six records carry `18/18`:
`census/round-20/recovery-status-catalog.json` (the r19 acceptance receipt the r19 final tip does not cover),
`census/round-21/r20-closure-excerpt.json` (the r20 acceptance receipt), `replay-integrated.txt` and
`replay-final.txt` (matrix scenarios S1-S3), `final-verification.json` and `final-code-verification.json`
(matrix stdout). Every other hit is a hex or path fragment (`18-clone-executor`, `18/missing.json`). No record
in rounds 20 or 21 states the remote-ref-only source as `18/18`.

Two controls in the scratch clone `/fast/scratch/hyaku/souji-r31/C1BindD/cnt-trap` show what the frozen rule
admits and what it refuses:

```
# control 1 — bind L29 to a blob that merely contains an 18/18 in another block
ITEM	L29	SCORECARD.md:170	literal=18/18	superseded	binding=record	MATCH	census/round-21/final-code-verification.json
SUMMARY items=1 bound_run=0 bound_record=1 unbound=0 mismatches=0 partial=1 rev=682ab74d03ac12153495dcd1add95351bf550ba6
rc=0

# control 2 — bind L29 to the record the cell names
ITEM	L29	SCORECARD.md:170	literal=18/18	superseded	binding=record	RECORD-MISMATCH	census/round-21/remote-source-after.json
SUMMARY items=1 bound_run=0 bound_record=0 unbound=0 mismatches=1 partial=1 rev=7d20a3143beb85f0e7787a847dbdde9921bb1d2c
rc=1
```

Control 2's `RECORD-MISMATCH` (not `BAD-ROW`) also proves the blob is unchanged at base and rev: the counter
checks blob identity before the literal. So the cell's own citation fails on byte absence, not on shape.

Consequence, stated plainly: C1's target `unbound=0 mismatches=0` cannot be reached for L29 by an honest row.
Reaching it requires either (a) the grep-found-digit binding of control 1, which the preregistration forbids,
or (b) an L1 decision about a base cell whose named record never states the literal it is cited for. Any
amendment must be stricter-only and is the L1's to log; this seat does not propose a relaxation and does not
write the row.

## Not run here

- The full 41-item counter after integration: that is the L1's landing gate. All runs above used `--only`,
  whose SUMMARY carries `partial=1`.
- No lane write and no commit by this seat: rows, receipts and the scratch clones only.
- Scratch `/fast/scratch/hyaku/souji-r31/C1BindD/` is removed after the delivery copies above.
