# SwarmCritic05 — C1 supersession rows L30-L41 (round 31, wave 2)

## Status

STATUS: PARTIAL — all 12 audited rows state a true literal whose occurrence is the measurement the
cell names, and the L1's landing reading reproduces exactly; no row is WRONG-OCCURRENCE or
FALSE-REASON, and 11 of 12 receipts/runs reproduce byte-for-byte (L37's count reproduces, its
receipt as a whole does not). But C1 still misses its frozen target by one item (L29 unbound), L37's
receipt is not reproducible from committed bytes, and two audited cells keep count prose the
revision contradicts.

## Evidence

Seat lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only). Audited rev
`24f343c8ffc820c0f89b4252cbdc94ab9a673aab`; base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`;
enumeration `c1-cells.tsv` at `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; tip
`2c16d018e40db7c23420a2c3bb546b52957bcc25` (`rev-parse HEAD`), working tree clean.

- Rows: `git -C <lane> grep -n '^| L' 24f343c8… -- SCORECARD.md` → 40 rows L01-L28, L30-L41 (no L29),
  inside `### Round 31 capability-cell supersessions` at SCORECARD.md:361.
- Base cells: `git show 9f17a1ef:SCORECARD.md | sed -n '<171,172,173,174,175,313,314,355>p'` — the
  eight lines the 12 rows point at, quoted per row in the delivery.
- Run rows (8) re-run in a `--no-local` clone at 24f343c8 (origin removed, `checkout -qf --detach` +
  `clean -fdxq`, fresh `TMPDIR`), argv exactly as the row states, twice per row (REV blob and the
  `--base` blob per A4(c)). All rc=0; last digit-bearing stdout line equals the row literal:
  L30 `selftest=8/8`; L31 `selftest=8/8`; L32 `selftest=15/15`; L33 `cases=12 pass=12
  control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`; L35 `cases=9 pass=9
  control=FALSE-GREEN-REJECTED`; L36 `cases=20 pass=20 control=FALSE-GREEN-REJECTED`; L38
  `cases=15 pass=15 control=TAMPER-REJECTED`; L40 `cases=7 pass=7 control=FALSE-GREEN-REJECTED`.
- Record rows (4) re-derived, not trusted:
  - L34 `census/round-24/records/c1-control-stub.tsv`: replay of its own `rev=1efe406e…` + cmd at
    1efe406e reproduces its eight CASE lines and `cases=8 pass=4 control=FALSE-GREEN-REJECTED
    lost_found=WRITE-DETECTED` byte-for-byte, rc=1; fixture sha256 at 1efe406e equals the record's
    `tool_sha256` 373ef1f0…
  - L37 `census/round-29/records/c1-fixture-red-before.txt`: r31 fixture vs the v1 tool (commit b8cb4b31, blob 68c97278…) →
    `cases=20 pass=8 control=FALSE-GREEN-REJECTED` with 12 FAIL lines; the record says
    `cases=20 pass=8 control=TOLERATED` and lists 11.
  - L39 `census/round-29/records/c2-fixture-red-before.txt`: r31 fixture vs r29-base capture tool
    c63a9f0c → the record's 21 FAIL lines verbatim, `cases=15 pass=8 control=TAMPER-REJECTED`, rc=1.
  - L41 `census/round-30/records/c2-fixture-red-before.txt`: replay at 9420341d with the pinned
    blobs (fixture sha256 e83033…, gate sha256 02b58f81…) reproduces all seven CASE lines and
    `cases=7 pass=3 control=FALSE-GREEN-REJECTED`, rc=1 (the record's `RC=1`).
- Frozen counter, my serial runs (lane tool, A2+A4, `--scratch` under my seat):
  `tools/souji-capability-cells.py --rev 24f343c8…` → `SUMMARY items=41 bound_run=20
  bound_record=20 unbound=1 mismatches=1`; `--only L29` → `UNBOUND`; `--only L30…L41` at the
  landing → `items=12 bound_run=8 bound_record=4 unbound=0 mismatches=0`; the same 12 at
  `--rev 9f17a1ef` (base cells) → `items=12 bound_run=5 bound_record=0 unbound=4 mismatches=7`.
- Landing vs tip: `git diff 24f343c8 2c16d018 -- SCORECARD.md` empty (SCORECARD blob 002c9fb9 at
  both); the four records, the six fixtures and the eight tools the rows run are byte-identical at
  the tip, so every row reading above holds at the tip.

## Findings

1. **Frozen target missed (calibration, claim-level).** L29 (`SCORECARD.md:170`, `18/18`) has no
   row; its record `census/round-21/remote-source-after.json` carries the count only as scalars
   (`grep -c '18/18'` = 0, `matched_command_count` = 1 occurrence), so the counter's record branch
   cannot bind it and no script on that line permits a run row. `unbound=1 mismatches=1` at the
   landing and at the tip; the L1 states the miss before the rows. C1 is a miss, not a pass.
2. **L37's record is not a faithful capture (calibration).** `c1-fixture-red-before.txt:12` says
   `cases=20 pass=8 control=TOLERATED`; the committed fixture at the landing with the same v1 tool
   prints `control=FALSE-GREEN-REJECTED`, and the fixture's control does not depend on `--tool`, so
   TOLERATED cannot come from the committed bytes. The receipt lists 11 FAIL lines where `pass=8` of
   20 implies 12 (my run's 12th, `indent-4-flagged`, is absent). The count pair is true. Smallest
   safe correction: re-run the red-before with the v1 tool (commit b8cb4b31, blob 68c97278…) and replace the receipt, or state in the
   row reason that the receipt is a pre-amendment-fixture capture.
3. **Cells keep stale prose counts (calibration).** SCORECARD.md:173 says "reject an always-zero
   emitter on eight of nine fixture cases" while the revision fixture's `CASES` has 15 entries (12
   requiring a mismatch) and its own writing commit had 7 of 9; :174 says "The no-write envelope is
   a `/var/tmp` fixture claim over 8 frozen cases" while the revision fixture runs 12. A4 routes
   notation-external counts, so the frozen target is untouched — but the r30 defect C1 answers is
   only partly closed.
4. **Five of twelve rows are restatements (calibration).** L30, L31, L36, L38, L40 MATCH as base-cell
   runs at 9f17a1ef already; only L32, L33, L35 (run) and L34, L37, L39, L41 (record) change an
   item's verdict. `bound_run=20` should not be read as twenty stale literals corrected.
5. **L41 binds the r30 base gate, not the revision's base gate (calibration, scope).** The pinned
   blob e67810d1 is the gate at 9420341d; the r31 base gate is 51f98ed7 and already prints 7/7. The
   row's reason is true and the cell's own round is r30; note only.
6. **L34 binds an 8-case receipt for a 12-case fixture (calibration).** The same stub control at the
   revision prints `cases=12 pass=4`; the receipt `cases=8 pass=4` is byte-identical and legal under
   the record branch, but it is a historical observable.

No finding harms operability or coverage: no row touches a tool, a fixture, a record or an entry
outside its cell's own capability, and the 12 rows leave C2's and C3's surfaces byte-unchanged.

## Attack log

- A1 — Substitute a *base-cell* reading for each row: ran the counter at `--rev 9f17a1ef` (7
  mismatches over my 12). Result: 5 rows were already MATCH; the block's improvement in this range
  is 7 items, not 12. Finding 4.
- A2 — Re-run each run row with the REV blob and with the `--base` blob (A4(c)): identical rc and
  last line for all eight, so no row depends on an in-round fixture edit. Cleared.
- A3 — Re-derive each record row instead of reading it: L34 byte-identical, L39 and L41 byte-identical
  modulo receipt filtering/trailing rc, L37's count reproduced but its control token and one FAIL
  line are not. Finding 2.
- A4 — Swapped-orientation test (`cases=8 pass=4` for cell `4/8`, etc.): all four orientations are
  correct; a naive multiset match would not have caught a swap, but none is present. Cleared.
- A5 — Shared-record test across the whole 40-row block: no two rows share a (record, literal) pair;
  the L13-L18 and L24/L26 record sharing uses distinct literals (already disclosed in A5). Cleared.
- A6 — Staleness test of the cells' non-notation counts at the revision: :173 "eight of nine" and
  :174 "over 8 frozen cases" are both contradicted by the committed fixtures (15 and 12 cases);
  :173's count matches neither the revision nor its writing commit. Finding 3.
- A7 — Tip test: SCORECARD diff landing→tip is empty and every audited blob is unchanged, so no row
  reading is a landing-only artifact. Cleared.
- A8 — L29 hole premise test: `grep -c '18/18'` over `census/round-21/remote-source-after.json` = 0,
  `matched_command_count` present; the preamble's "no honest binding" premise holds. Finding 1.
- A9 — Reason-sentence truth test for every row (record path, lesson citation, growth, command):
  round-24.md:18 and round-29.md:60/61 cite the named receipts verbatim; :173 grew 9→15 between
  47652502 and 728b2ce; :174's fixture was already 12 cases at the cell's appending commit. All
  reasons true; L37's reason true but its receipt imperfect (Finding 2).

## Deliveries

- `souji-shokunin/.ufo/waves/round-31/w2/deliver-c1-audit-L30-L41.md` — per-row verdicts,
  reproduction commands, counter readings and findings F1-F6.

Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmCritic05/` removed after the delivery copy. No lane
commit, no git index, no jj mutation, nothing outside the lane touched.
