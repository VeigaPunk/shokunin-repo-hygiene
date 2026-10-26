# SwarmExecutor05 — r30 wave 1, lane C1RowsC (calibration rows R13-R18)

## Status

STATUS: PASS — rows R13-R18 of `census/round-30/c1-rows.tsv` were re-run twice at the lane tip; R13 and R17 MATCH and need nothing, R14/R15/R16/R18 are corrected by four append-only `R30-CORRECTION` lines (delivered, not applied — this seat is read-only). Acceptance proven in a scratch clone: `k1=0 k2=0 mismatches=0`, exit 0.

## Evidence

Lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; measured at tip `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (`SCORECARD.md` there is byte-identical to the base blob: append-only prefix check, `len_base=54403 len_rev=54403`); list-rev `d4928ec86b667e3d1ed0adb07fb088e500cf1631`.

Before (twice, byte-identical), `--only R13,R14,R15,R16,R17,R18`:

```
ROW	R13	SCORECARD.md:172	stated=8/8	rc=0	observed=selftest=8/8	MATCH
ROW	R14	SCORECARD.md:173	stated=9/9	rc=0	observed=selftest=15/15	MISMATCH kind=value
ROW	R15	SCORECARD.md:174	stated=8/8	rc=0	observed=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED	MISMATCH kind=value
ROW	R16	SCORECARD.md:175	stated=9/9	rc=2	observed=r24-coverage-agreement.py: error: the following arguments are required: --tool	MISMATCH kind=rc
ROW	R17	SCORECARD.md:313	stated=cases=20 pass=20	rc=0	observed=cases=20 pass=20 control=FALSE-GREEN-REJECTED	MATCH
ROW	R18	SCORECARD.md:314	stated=cases=15 pass=15	rc=0	observed=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]	MISMATCH kind=value
SUMMARY k1=4 k2=0 mismatches=4 rows=6 pointers=10 partial=1 rev=df6afe817d096e4ad71ba2b9cc21a83f126eb658
```

After (twice, identical, exit 0) at scratch-clone commit `835014cf09a6319f911c6c0498623ef757d744c3` = tip + the four delivered lines:

```
ROW	R14	SCORECARD.md:173	stated=9/9	rc=0	observed=selftest=15/15	CORRECTED
ROW	R15	SCORECARD.md:174	stated=8/8	rc=0	observed=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED	CORRECTED
ROW	R16	SCORECARD.md:175	stated=9/9	rc=0	observed=cases=9 pass=9 control=FALSE-GREEN-REJECTED	CORRECTED
ROW	R18	SCORECARD.md:314	stated=cases=15 pass=15	rc=0	observed=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]	CORRECTED
SUMMARY k1=0 k2=0 mismatches=0 rows=6 pointers=10 partial=1 rev=835014cf09a6319f911c6c0498623ef757d744c3
```

Raw single-row reruns, in the clone checked out at the tip (`TMPDIR` inside scratch, `python3 -B` / `bash`): R14 `selftest=15/15` then `control=FALSE-GREEN-REJECTED`, rc 0; R15 last line `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, stderr empty, rc 0; R16 with `--tool` rc 0, `cases=9 pass=9 control=FALSE-GREEN-REJECTED`; R18 rc 0, stdout ends `cases=15 pass=15 control=TAMPER-REJECTED`, stderr ends with the tool's usage block (case 14). Host git 2.56.0 (R15's fixture precondition is git >= 2.46, satisfied).

## Findings

1. **R13 MATCH, no correction.** `python3 tests/fixtures/r23-receipt-run.py` → `selftest=8/8`, rc 0 at base and tip; the row literal at `SCORECARD.md:172` is honest.
2. **R17 MATCH, no correction.** `python3 -B tests/fixtures/r29-registry-agreement.py` → `cases=20 pass=20 control=FALSE-GREEN-REJECTED`, rc 0 at base and tip; `SCORECARD.md:313` is honest.
3. **R14 stale count (`SCORECARD.md:173` states 9/9).** The fixture was extended in r25: `tests/fixtures/r23-record-agreement.py:41` "Cases 13-15 (round 25, routed residuals R15/R17/R19; the L1-adjudicated W2K1 shapes):". Command path unchanged, rc 0, so only the count is stale → correction `observed=selftest=15/15`.
4. **R15 stale count (`SCORECARD.md:174` states 8/8).** `tests/fixtures/r24-size-census.py:1-2` "r24 C1 counter: F2 write-safety size census over the frozen 8-case set, extended by r25 C2"; cases 9-12 are the refusal surface, so the fixture prints `cases=12 pass=12 ...` → correction with that exact line.
5. **R16 enumerated command omits a required argument (`SCORECARD.md:175`, stated 9/9).** As enumerated it exits 2: `tests/fixtures/r24-coverage-agreement.py:331` "ap.add_argument("--tool", required=True)". r24's own receipt records the argv that produced 9 passes, `census/round-24/records/c2-fixture-after.tsv:5` "cmd=python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py". Because the fixture prints `cases=9 pass=9`, never `9/9`, the correction carries both `cmd=` (same first path token, script identity preserved) and `observed=`.
6. **R18 the counter's last-line rule lands on a diagnostic, not the result (`SCORECARD.md:314`, stated 15/15).** The stated literal is shorthand the fixture never prints; its final print is `tests/fixtures/r28-wave-evidence-capture.sh:537` (`cases=15 pass=<n> control=TAMPER-REJECTED`). Case 14 (`tests/fixtures/r28-wave-evidence-capture.sh:519`, `bash "$tool" "$lane" 26x`) drives the tool's non-numeric-round branch `tools/souji-wave-evidence-capture.sh:122` ("usage >&2; exit 1"). The counter's `S` is the last digit-bearing line of **stdout+stderr concatenated**, so the stderr usage block (printed at case 14) outranks the green stdout `cases=15 pass=15` line even though the run is rc 0 and all 15 cases pass. The honest correction records that observed string.
7. **The frozen row commands write outside `TMPDIR`.** Three of these fixtures hardcode `/var/tmp` scratch: `tests/fixtures/r23-record-agreement.py:67`, `tests/fixtures/r24-size-census.py:30`, `tests/fixtures/r24-coverage-agreement.py:50`; only the r28 capture fixture honours an override. Under the counter's run the fixtures still self-clean. No residue from this seat's runs: `/var/tmp` entries visible at check time (e.g. `/var/tmp/souji-r29-wave-capture-fixture`, empty) carry mtime 01:38 while the runs finished at 04:38 UTC.

## Attack log

Advisory (this seat is not an attack seat; filed because the preregistration's ATTACK clause binds any seat that finds a counter gameable).

- **A-C1-1 (K1 last-line rule).** A row's verdict rests on `summary_line` = last digit-bearing line of the concatenated stdout+stderr. (a) R18 shows a genuinely green row scored MISMATCH because a later stderr diagnostic wins; a correction then encodes that diagnostic as the observed value, so the recorded "agreement" is with the noise rather than with the claim. (b) Symmetrically, a row could be marked CORRECTED while the actual count line is red, as long as the last loud line carries digits and is copied into the correction. Not a request to change the frozen counter — recorded for the L1.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-c1-corrections-R13-R18.txt` — the four verbatim `R30-CORRECTION` lines for R14/R15/R16/R18, one reason per line with locations, the before/after counter output, and the raw acceptance log.

Notes: no tool installed or upgraded; no writes outside these two files; scratch clone `/fast/scratch/hyaku/souji-r30/C1RowsC/` (origin removed) removed after the runs; lane git index, jj state, `.ufo/state`, `.scratch/` and every sibling lane untouched.
