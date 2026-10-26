# C1 audit — supersession rows L30-L41

Seat SwarmCritic05, Souji round 31 wave 2 (read-only falsification seat). Landing rev
`24f343c8ffc820c0f89b4252cbdc94ab9a673aab`; append-only base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`;
enumeration `census/round-31/c1-cells.tsv` at prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`;
lane tip re-checked at `2c16d018e40db7c23420a2c3bb546b52957bcc25`.

Scope: the 12 appended rows L30-L41 (L29 has no row). Nothing in the lane was written, moved or
staged; every command ran from a private `git clone -q --no-local` with `origin` removed under
`/fast/scratch/hyaku/souji-r31/w2-SwarmCritic05/`.

## Verdicts

| Row | cell (base line) | item literal | row literal | binding | occurrence at 24f343c8 | verdict |
|---|---|---|---|---|---|---|
| L30 | SCORECARD.md:171 | 8/8 | 8/8 | run: tools/souji-declared-evidence.py --selftest | rc=0, `selftest=8/8` | HONEST (already MATCH at base) |
| L31 | :172 | 8/8 | 8/8 | run: tests/fixtures/r23-receipt-run.py | rc=0, `selftest=8/8` | HONEST (already MATCH at base) |
| L32 | :173 | 9/9 | 15/15 | run: tests/fixtures/r23-record-agreement.py | rc=0, `selftest=15/15` | HONEST (fixture grew 9 to 15) |
| L33 | :174 | 8/8 | cases=12 pass=12 | run: tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py | rc=0, `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | HONEST (fixture grew 8 to 12) |
| L34 | :174 | 4/8 | cases=8 pass=4 | record: census/round-24/records/c1-control-stub.tsv | re-run at 1efe406e byte-identical | HONEST |
| L35 | :175 | 9/9 | cases=9 pass=9 | run: tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py | rc=0, `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | HONEST (base argv lacked --tool, rc=2) |
| L36 | :313 | cases=20 pass=20 | cases=20 pass=20 | run: tests/fixtures/r29-registry-agreement.py | rc=0, `cases=20 pass=20 control=FALSE-GREEN-REJECTED` | HONEST (already MATCH at base) |
| L37 | :313 | 8/20 | cases=20 pass=8 | record: census/round-29/records/c1-fixture-red-before.txt | count re-derived with the v1 tool at commit b8cb4b31; record's control token and FAIL list NOT reproducible | HONEST (literal), record-fidelity defect |
| L38 | :314 | cases=15 pass=15 | cases=15 pass=15 | run: tests/fixtures/r28-wave-evidence-capture.sh | rc=0, `cases=15 pass=15 control=TAMPER-REJECTED` | HONEST (already MATCH at base) |
| L39 | :314 | 8/15 | cases=15 pass=8 | record: census/round-29/records/c2-fixture-red-before.txt | re-run with r29-base tool c63a9f0c: `cases=15 pass=8 control=TAMPER-REJECTED` | HONEST |
| L40 | :355 | cases=7 pass=7 | cases=7 pass=7 | run: tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py | rc=0, `cases=7 pass=7 control=FALSE-GREEN-REJECTED` | HONEST (already MATCH at base) |
| L41 | :355 | 3/7 | cases=7 pass=3 | record: census/round-30/records/c2-fixture-red-before.txt | re-run with base gate blob e67810d1: `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc=1 | HONEST |

No row is WRONG-OCCURRENCE, FALSE-REASON or NOT-REPRODUCED. Two rows carry defects that the frozen
rule does not see: L37's record is not a faithful capture (F2), and L34's record binds an 8-case
receipt for a fixture that has 12 cases at the revision (F6).

## Method

- Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin $D/c`,
  `git -C $D/c remote remove origin`, `git -C $D/c rev-parse --show-toplevel` == `$D/c`.
- Run rows, twice each: `git -C c checkout -qf --detach 24f343c8…`, `git -C c clean -fdxq`, fresh
  `TMPDIR`, argv exactly as the row states (no shell); variant 2 additionally writes the script's
  `--base` blob over the REV copy (frozen counter rule A4(c)).
- Record rows: open the blob at 24f343c8, locate the literal, then re-derive it from committed bytes
  (fixture/tool blobs named by the record or by the lesson) instead of trusting the receipt.
- Lane counters run serially in my seat with `--scratch` under my scratch dir; never two at once.

## Per-row evidence

### L30 — SCORECARD.md:171, `python3 tools/souji-declared-evidence.py --selftest`
Base cell states the same command beside 8/8. Run at 24f343c8: rc=0, last digit-bearing line
`selftest=8/8` (REV blob and base blob identical output). The item already MATCHes as a base-cell
run at 9f17a1ef (`ITEM L30 … MATCH … observed=selftest=8/8`), so the row changes no state.

### L31 — :172, `python3 tests/fixtures/r23-receipt-run.py`
Run at 24f343c8: rc=0, `selftest=8/8`; base blob same. MATCH already at base. Row is a restatement.

### L32 — :173, `python3 tests/fixtures/r23-record-agreement.py`
Cell says `tests/fixtures/r23-record-agreement.py` 9/9 and "reject an always-zero emitter on eight
of nine fixture cases". Run at 24f343c8: rc=0, `selftest=15/15`. Growth verified at both ends: the
fixture at the cell's writing commit 476525026cdb179f2d49441e1cb6c6f7316f3124 prints
`selftest=9/9`, and at 728b2ce71acbe574ae3036b456724d0a3d6f8f08 prints `selftest=15/15`. At base the
item is RUN-MISMATCH (literal 9/9 vs observed selftest=15/15), so the row is a real correction. The
cell's prose count is not touched by the row (F3).

### L33 — :174, `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py`
Run at 24f343c8: rc=0, `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`
(REV and base blob). Growth: the r24 receipt `census/round-24/records/c1-after.tsv` (rev
778747eb671f8e85ef5387bc3d7023337b30467c) states `cases=8 pass=8 …` for the 8-case fixture, and the
fixture at the cell's appending commit 07f83e69979b1032f9de4fe876739a8dccc7242b already prints
`cases=12 pass=12`. Real correction; the cell's "over 8 frozen cases" survives (F3).

### L34 — :174, record `census/round-24/records/c1-control-stub.tsv`
Occurrence: line 17, `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`
(single occurrence). Re-derived, not trusted: the record's own `rev=1efe406e…` and cmd were replayed
at 1efe406e — `python3 -B tests/fixtures/r24-size-census.py --tool
census/round-24/controls/stub-size-census.py` prints the record's eight CASE lines and line 17
byte-for-byte, rc=1; the fixture's sha256 at 1efe406e is `373ef1f0a02f8ca11fccd4ff32d8511c1eaaf3ede672c37ed11ef2b10968084f`,
equal to the record's `tool_sha256`. The round-24 lesson cites it (round-24.md:18, "Stub control:
`cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` rc=1"). Same capability
(the stub emitter control of the debris census), same run, same count. Staleness caveat: the same
stub control at 24f343c8 prints `cases=12 pass=4` (12-case fixture), so the receipt is a historical
observable, which the record branch of the frozen rule allows.

### L35 — :175, `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py`
At base the enumerated argv (no `--tool`) exits 2 (`error: the following arguments are required:
--tool`), so the item is RUN-MISMATCH at base. With `--tool` as the row states: rc=0,
`cases=9 pass=9 control=FALSE-GREEN-REJECTED`. The fixture at the cell's appending commit already
printed 9/9, so no count changed; the row supplies the runnable argv. A4(a) forces a run row here
(the cell names a command), so the shape is the only admissible one.

### L36 — :313, `python3 -B tests/fixtures/r29-registry-agreement.py`
rc=0, `cases=20 pass=20 control=FALSE-GREEN-REJECTED`; MATCH already at base. Restatement.

### L37 — :313, record `census/round-29/records/c1-fixture-red-before.txt`
Occurrence: line 12, `cases=20 pass=8 control=TOLERATED` (single occurrence). Count re-derived: the
r31 fixture run against the v1 tool at commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (blob
`68c97278907b7b89d55b8d3fbc3f6bd8d4175d30`) prints
`cases=20 pass=8 control=FALSE-GREEN-REJECTED` with 12 FAIL lines on stderr, the record's 11 FAIL
lines being a subset of them. The lesson cites it (round-29.md:60, "v1 tool 8/20,
reverse-check-deleted mutant 15/20: `records/c1-fixture-red-before.txt`") and the record's second
section `cases=20 pass=15 control=TOLERATED` is the mutant. Literal is the cell's measurement. The
record itself is not reproducible from committed bytes (F2).

### L38 — :314, `bash tests/fixtures/r28-wave-evidence-capture.sh`
rc=0, `cases=15 pass=15 control=TAMPER-REJECTED`; MATCH already at base. Restatement.

### L39 — :314, record `census/round-29/records/c2-fixture-red-before.txt`
Occurrence: line 22, `cases=15 pass=8 control=TAMPER-REJECTED` (single occurrence). Re-derived: the
r29-base capture tool blob `c63a9f0ccf78702cdb44d5d916c40e00e3613503` run under the r31 fixture
prints the record's 21 FAIL lines verbatim plus the `case-N: PASS` lines the receipt filtered out,
summary `cases=15 pass=8 control=TAMPER-REJECTED`, rc=1. The lesson cites it (round-29.md:61, "base
tool 8/15: `records/c2-fixture-red-before.txt`"). Same fixture, same tool, same count; the receipt is
a FAIL-only capture.

### L40 — :355, `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py`
rc=0, `cases=7 pass=7 control=FALSE-GREEN-REJECTED`; MATCH already at base. Restatement.

### L41 — :355, record `census/round-30/records/c2-fixture-red-before.txt`
Occurrence: line 32 `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, and again in the hand-written
header at line 14 with `exit 1`. Fully re-derived from committed bytes: the record pins fixture
sha256 `e830339332aa6ae1b1f614e33445327b68f47d0904428a04d6d812e394c66271`, which is the committed
capture `census/round-30/waves/w1/deliver-r30-landing-gate-discovery.py` (554 lines) and also the
blob of `tests/fixtures/r30-landing-gate-discovery.py` at 24f343c8; the record pins base gate blob
`e67810d130817879fddd71c5ceeb5d5fd37e6ea8` sha256
`02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`, which is
`tools/souji-landing-gate.py` at `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`. Replay at 9420341d with
those two blobs: the record's seven CASE lines and CONTROL line byte-for-byte, `cases=7 pass=3
control=FALSE-GREEN-REJECTED`, rc=1 (the record's `RC=1`). Scope caveat: that gate is the r30 base
gate, not the r31 base gate (`51f98ed7f9b6cf834e93be94c6bbdd9e392e17a6` at 9f17a1ef), which prints
7/7 (F5).

## Rule checks (all 12 rows)

- Row line equals the item's base line (171/172/173/174/174/175/313/313/314/314/355/355); base
  SCORECARD is a byte prefix of the landing and of the tip file.
- Integer multisets, row literal vs base literal: {8,8}, {8,8}, {9,9}, {8,8}, {4,8}, {9,9}, {20,20},
  {8,20}, {15,15}, {8,15}, {7,7}, {3,7} — each equal; `cases=N pass=P` orientations are correct
  (pass first on the cell side, `cases` then `pass` on the record side), so no swapped restatement.
- Record paths: no `:line`, no `waves`/`transcripts`/`sources` component; all four are byte-identical
  at base, landing and tip; each is inside a round of the item's round set ({24}, {29}, {29}, {30}).
- No two rows in the whole 40-row block share a (record, literal) pair; the four record paths in this
  range are distinct.
- Run rows: script under tools/ or tests/fixtures/ with its stem on the base line; no `-c`, `-h`,
  `--help`, `--version`; literal does not occur in the argv.
- Landing vs tip: `git diff 24f343c8 2c16d018 -- SCORECARD.md` is empty; every audited fixture,
  tool and record blob is byte-identical at the tip.

## Counter re-derivation (frozen tool, A2+A4)

```
python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8… --base 9f17a1ef… \
  --list-rev 1d45496a… [--only L30,…,L41]
```
- My range at the landing: `items=12 bound_run=8 bound_record=4 unbound=0 mismatches=0 partial=1`.
- Full enumeration at the landing (my run): `items=41 bound_run=20 bound_record=20 unbound=1
  mismatches=1 rev=24f343c8…`; `--only L29` → `UNBOUND`, so C1 misses its frozen target by one item,
  as the L1 states.
- My range at base (`--rev 9f17a1ef`): `items=12 bound_run=5 bound_record=0 unbound=4
  mismatches=7` — L30, L31, L36, L38, L40 MATCH as base cells; L32/L33/L35 RUN-MISMATCH; L34/L37/L39/L41
  UNBOUND. So 7 of the 12 rows change the item's state and 5 restate cells that were already bound.

## Findings

### F1 — C1 misses its own frozen target (calibration; claim-level, disclosed)
`unbound=1 mismatches=1` at the landing and at the tip: L29 has no row. My `--only L29` run gives
`UNBOUND`; the L1's section preamble states this before the rows. No row in L30-L41 is at fault. The
frozen target ("unbound=0 mismatches=0") is not met; per the prereg the claim is a miss, not a
partial pass.

### F2 — L37's receipt is not a faithful capture (calibration; record used as evidence)
`census/round-29/records/c1-fixture-red-before.txt` line 12 says `cases=20 pass=8 control=TOLERATED`,
but the committed fixture at 24f343c8 with the same v1 tool prints
`cases=20 pass=8 control=FALSE-GREEN-REJECTED`. The control is tool-independent in that fixture
(`control(emitter)` re-runs the fixture with its own always-zero emitter), so TOLERATED cannot come
from the committed bytes. The receipt also lists 11 FAIL lines while `pass=8` of 20 implies 12
failing cases; my re-run emits 12 and the receipt's 11 are a subset (the missing one is
`indent-4-flagged`). The count pair itself is true. Smallest safe correction: re-run the red-before
at the landing fixture with the v1 tool (commit b8cb4b31, blob 68c97278…) and replace the receipt, or mark the receipt as a
pre-amendment-fixture capture in the row reason; the literal and the binding survive either way.

### F3 — the cells' prose counts stay stale under the supersession rows (calibration)
:173 still says "reject an always-zero emitter on eight of nine fixture cases" while the fixture at
the revision has 15 cases and 12 of them require a mismatch (`CASES` at 24f343c8: 12 True, 3 False);
at the cell's writing commit (476525026cdb179f2d49441e1cb6c6f7316f3124) the fixture had 7 of 9, so
"eight of nine" matches neither. SCORECARD.md:174 still says "The no-write envelope is a `/var/tmp` fixture claim over 8 frozen cases" while the
fixture has 12. A4 discloses that notation-external count statements are routed, not counted, so
this does not move the frozen target; but the round-30 defect C1 answers ("capability cells still
state old literals") is only partly closed: two audited cells still carry counts contradicted at the
revision. Smallest safe correction: none inside the frozen rules; record it as the next calibration
move (same class as the L29 residual) rather than a wave-2 amendment.

### F4 — five of twelve rows supersede cells that were already bound (calibration)
L30, L31, L36, L38 and L40 produce MATCH as base-cell runs at 9f17a1ef, i.e. the row restates a
correct literal. The block's `bound_run` count therefore overstates corrections; in this range only
L32, L33 and L35 (run) and L34, L37, L39, L41 (record) change the item's verdict. Not a rule defect
(the preamble says "supersedes", not "was stale"), but a reader of the block should not read 40 rows
as 40 stale literals.

### F5 — L41's "base gate" is the r30 base gate, two generations older than the r31 base (calibration, scope)
The record pins blob e67810d1 (gate at 9420341d, the r30 base). The r31 base gate is 51f98ed7 and
already prints 7/7, so the cell's "(base gate 3/7)" is a historical statement; the row's record
binding is the right one for the cell's own round but not an observable of the revision's base gate.
No counter rule is violated; the row's reason is true. Note only.

### F6 — L34 binds an 8-case receipt for a fixture that has 12 cases at the revision (calibration)
The stub control at 24f343c8 prints `cases=12 pass=4`, so the cell's "stub control 4/8" no longer
describes the revision's fixture; the row's `cases=8 pass=4` receipt is byte-identical and the
frozen record branch admits it. Same class as F5: a historical observable presented as the cell's
binding. The pass count (4) is stable; only the denominator grew.

## Tooling

No installs, no upgrades, no pacman. Used system `python3 -B`, `git`, `bash`, `diff`, `sha256sum`
only.

## Scratch

`/fast/scratch/hyaku/souji-r31/w2-SwarmCritic05/` (removed after this file was copied into the lane).
