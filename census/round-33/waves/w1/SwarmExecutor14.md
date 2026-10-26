## Status

STATUS: PASS — K16 is value drift (fixture selftest 9 → 11 cases at `1dd8b1e3…`, later 12 → 15); one restated row in the counter's exact 7-cell form flips the item to `AGREE` in scratch (`items=1 agree=1 mismatches=0`, rc 0) while the base reading stays `MISMATCH`. The change is growth, not regression: every revision exits 0 with passed = total and the control line still `FALSE-GREEN-REJECTED`.

## Evidence

Scratch clone `/fast/scratch/hyaku/souji-r33/RestateK16/c` (`git clone -q --no-local` from the lane, origin removed at once, `rev-parse --show-toplevel` printed the clone), `TMPDIR=/fast/scratch/hyaku/souji-r33/RestateK16/tmp`, fresh subdir per run; scratch removed at end of seat.

1. Frozen argv `python3 tests/fixtures/r23-record-agreement.py` at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`, 3 runs, fresh TMPDIR each: rc 0/0/0, stderr empty, stdouts byte-identical except the `scratch=` line. 20 stdout lines: 3 header, 15 `case=`, `selftest=15/15`, `control=FALSE-GREEN-REJECTED`. `grep '9/9'` → 0 matches, so the frozen predicate `\b9/9\b && control=FALSE-GREEN-REJECTED` fails at base. The count line is printed by the fixture itself (`tests/fixtures/r23-record-agreement.py:607-608` at 2d9bca55).
2. Cause walk (`git log --reverse --format=%H -- tests/fixtures/r23-record-agreement.py tools/souji-record-agreement.py`, argv run at each commit): `47652502` 0 `9/9` · `1dd8b1e3` 0 `11/11` · `53780181` 0 `11/11` · `c872eec3` 0 `12/12` · `315422ba` 0 `12/12` · `728b2ce7` 0 `15/15` · `98e5203d` 0 `15/15`; `control=FALSE-GREEN-REJECTED` at every one. First commit where the original outcome stops: `1dd8b1e30a971e662480b49bedf1000667fbddea`. Its first parent (`rev-list --parents -n1`) is `102690017115cb202f292828c90b72705f69bf09`, which prints `selftest=9/9` rc 0 → held=True / stops=False, the value-drift shape. `git show --name-only` at the cause names both item files; `merge-base --is-ancestor 1dd8b1e3… 2d9bca55…` → YES.
3. Counter proof at scratch commit `78d8c9121f250adbb61e3315cbb2f2eb33f415c0` (parent `2d9bca55…`, base SCORECARD.md + appended section + row):
   `ITEM K16 AGREE restated rc=0 expect_exit=0 statement is an output line last=selftest=15/15` /
   `SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=78d8c912…`, rc 0.
   Do-nothing control, `--only K16 --rev 2d9bca55…`: `ITEM K16 MISMATCH original rc=0 expect_exit=0 predicate fails last=selftest=15/15` / `SUMMARY items=1 agree=0 mismatches=1`, rc 1.
4. Full set (24 items, default `--jobs 6`) at `56045a57…` → `SUMMARY items=24 agree=20 mismatches=4 restated=1`, mismatches exactly K04 K05 K17 K18, so K16 was the only verdict my row moved. Repeat full set at `78d8c912…` → `SUMMARY items=24 agree=19 mismatches=5 restated=1`, the extra one being K22 (`bound_run=19 … mismatches=2` instead of `bound_run=20 … mismatches=1`); `--only K22` at that same commit then read `ITEM K22 AGREE … last=SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`. See Attack log.

## Findings

1. **K16 is value drift; cause `1dd8b1e30a971e662480b49bedf1000667fbddea`.** That commit adds two CASES entries and their predicates to `tests/fixtures/r23-record-agreement.py` — `("class-missing", case_k3_class, True)` and `("tally-stale-log", case_k2_tally, True)` — taking the selftest 9 → 11; `c872eec3…` added `unbound-tuple` (12) and `728b2ce7…` added `post-stderr-shadow`, `stdout-two-line`, `receipt-rev-object` (15). Locations: SCORECARD.md:173; CASES table of the fixture.
2. **Growth, not a lost capability.** 9/9, 11/11, 12/12, 15/15 all exit 0 with passed = total, the K1–K4 key arms are all exercised, and the always-zero control is still rejected at every revision. Nothing is restated away.
3. **Line 173's prose is stale beyond the count and is not restatable by a K16 row** (location SCORECARD.md:173): the row says "reject an always-zero emitter on eight of nine fixture cases", but the base fixture runs 15 cases — 1 target (green-on-clean), 2 further green-on-clean cases (`case=10 exempted-dirty`, `case=14 stdout-two-line`) and 12 mismatch-requiring cases; the fixture's own comment (`tests/fixtures/r23-record-agreement.py:527`) reads `# case 1 is the target (green-on-clean); every other case requires >=1 mismatch`. A restatement may quote only one complete digit-bearing output line, so the prose correction is the L1's own append.
4. **The control fact cannot be the quoted statement** (counter docstring, `census/round-33/c1-counter.py` judge branch): `control=FALSE-GREEN-REJECTED` is its own stdout line with no digit, so the only quotable line carrying the count claim is `selftest=15/15`; the control is carried in the reason cell and receipts. Rows quoting the control line would fail as non-digit statements.
5. **Parallel-load instability in K22 can produce a false MISMATCH at a fixed revision** (see Attack log): the same tree, same frozen K22 argv, read `bound_run=19 … mismatches=2` in one full run and `bound_run=20 … mismatches=1` when run alone.
6. **Predicate robustness, reported not amended:** `\b9/9\b` is a substring test over the collapsed stdout+stderr, so a hypothetical `selftest=19/9` line would satisfy K16's frozen predicate ([INFERENCE], not reproduced; no current revision prints it). Stricter-only amendment is the L1's call.

## Attack log

ATTACK R33-A1 (raised by this seat; frozen predicate, target and item untouched — reproduced state only).

- Frozen surface: C1 item K22 (`census/round-33/c1-items.tsv:36`), literal `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`, argv `python3 -B tools/souji-capability-cells.py --root . --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`.
- Reproduced state: at scratch commit `78d8c9121f250adbb61e3315cbb2f2eb33f415c0`, a full `--jobs 6` counter run reported `ITEM K22 MISMATCH original … last=SUMMARY items=41 bound_run=19 bound_record=20 unbound=1 mismatches=2 rev=24f343c8…`, while `--only K22` at the same commit and the same frozen argv reported `ITEM K22 AGREE … bound_run=20 … mismatches=1`. An earlier full run at a tree differing only in SCORECARD.md prose also read K22 AGREE.
- Why content cannot explain it: K22's tool reads SCORECARD.md only at `--base` and `--rev` (`tools/souji-capability-cells.py:173`, with `base_lines`/`append_ok` at `:176-177`) and each inner command runs in a private clone checked out at `--rev`, so a K16 restatement row at the tip is invisible to it.
- Mechanism: `bound_run` counts rows whose command returned rc 0 and matched its literal (`tools/souji-capability-cells.py:299-305`); a single transient failure of one row's command under simultaneous item load flips the item to MISMATCH and increments `mismatches` ([INFERENCE]: which row failed is not surfaced by the counter's one-line verdict, and the two clean readings did not reproduce it).
- Consequence for the claim: the frozen target `mismatches=0` at the C1 landing commit and at the tip can fail for a reason the lane cannot fix, and the kill rule counts any `mismatches>0` as MISSED. This is reported, not acted on: no item, counter or predicate was changed.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-c1-K16.md` — the row verbatim between `ROW-BEGIN`/`ROW-END`, the proven appended block with header/table-header, sibling-merge and EOF-placement constraints, and all receipts (3 base runs with every digit-bearing line, cause walk, first-parent check, counter AGREE/MISMATCH, full-set readings, growth verdict).
- `.ufo/waves/round-33/w1/SwarmExecutor14.md` — this report.

Scope: no lane file, frozen counter, item, leg or preregistration artifact was modified; no git/jj mutation outside the scratch clone; no tools installed; scratch tree `/fast/scratch/hyaku/souji-r33/RestateK16` removed.
