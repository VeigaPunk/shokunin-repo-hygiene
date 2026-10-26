# SwarmExecutor15 — r33 w1, C1 item K17

## Status

STATUS: PASS — K17 drafted, proved AGREE (restated) at a scratch landing commit, and identified as VALUE DRIFT caused by `679e2d02f46ec06447d679d9395d6592c5e35f5c` (growth, not regression). Delivery: `.ufo/waves/round-33/w1/deliver-c1-K17.md`.

## Evidence

Base: `6017a482e7068d5afb7617640198fbb0fe743357`; list-rev: `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; scratch clone at
`/fast/scratch/hyaku/souji-r33/RestateK17/c` (origin removed; toplevel verified; `TMPDIR` fresh per run; removed at end).

1. Frozen argv `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py`, 3 runs at 2d9bca55:
   rc=0/0/0, byte-identical stdout, 12 CASE lines all PASS, summary
   `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`. Neither `8/8` nor `cases=8` occurs.
2. First-failing sweep over every commit touching the two item files plus the cause's parent
   (`log --reverse --format=%H -- tests/fixtures/r24-size-census.py tools/souji-size-census.py`):
   1efe406, 778747e, 315422b, 7e4dbef → rc 0, `cases=8 pass=8 …` (frozen outcome holds); 679e2d0 → rc 0,
   `cases=12 pass=12 …` (fails); 98e5203, 2d9bca55 → also 12. `679e2d0` = first failure, names
   `tests/fixtures/r24-size-census.py` in `show --name-only`.
3. Scratch landing commit `4a2d2ca1c33fa303b2ebb3c01074c92fa4d4b2a3` (append of 6 lines to SCORECARD.md at 2d9bca55;
   throwaway identity). Counter:
   `ITEM K17 AGREE restated rc=0 expect_exit=0 statement is an output line last=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`
   / `SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=4a2d2ca1…`, counter rc=0.
4. Do-nothing control, same clone, `--rev 6017a48… --only K17`: `MISMATCH original … predicate fails`,
   `SUMMARY items=1 agree=0 mismatches=1`, rc=1.
5. No tool installed or upgraded this wave.

## Findings

1. K17 row (SCORECARD.md:174 at base) is stale by four cases: the r24 row states `8/8` / `cases=8 pass=8`, the fixture
   now runs 12 and prints `cases=12 pass=12` at 2d9bca55 and at base. Location: SCORECARD.md:174 evidence cell,
   tests/fixtures/r24-size-census.py (case table).
2. Cause is growth, not a capability loss: `679e2d02f46ec06447d679d9395d6592c5e35f5c` ("round-25: exercise
   size-census bare and refusal edge cases") added cases 9-12 (bare-nonempty, bare-empty, subdir, partialClone-only);
   cases 1-8 and both control facts (`FALSE-GREEN-REJECTED`, `WRITE-DETECTED`) are unchanged. No regression reported.
3. The row's prose still says "over 8 frozen cases" (`/var/tmp` fixture claim). The counter judges only the stated
   outcome, and SCORECARD.md is append-only, so this stale description cell cannot be fixed by this round; recorded,
   not edited. Location: SCORECARD.md:174 description cell.
4. The counter's append-only prefix rule forces the `### Round 33 capability currency` section to EOF; a mid-file
   insertion of the section would make every C1 item COULD-NOT-EVALUATE. Location: census/round-33/c1-counter.py
   `main()` prefix check.

## Attack log

Not an attack seat. No frozen predicate, target, item or leg is challenged; the counter behaved exactly as documented
(statement-line branch and value-drift cause branch both exercised).

## Deliveries

- `.ufo/waves/round-33/w1/deliver-c1-K17.md` — the one row (ROW-BEGIN/ROW-END), 3-run receipt, first-failing sweep,
  scratch counter AGREE + base MISMATCH control, growth verdict, placement constraint for the L1.
