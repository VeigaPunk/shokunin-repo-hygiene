## Status
STATUS: PASS — rows R07-R11 of census/round-30/c1-rows.tsv are shape mismatches (stated `N/0` vs the printed `SUMMARY total=N failed=0 ...` line) and are covered by five exact append-only `R30-CORRECTION` lines proven CORRECTED in a scratch clone; R12 already matched and needs no correction.

## Evidence
Contract read first: `census/round-30/records/preregistration.txt` (C1 K1: "nor carries an accepted append-only `R30-CORRECTION SCORECARD.md:<line> <row-id> [cmd=<argv>] rc=<n> observed=<S>` line"). Base state: `census/round-30/records/c1-before.txt` shows R07-R11 `MISMATCH kind=shape`, R12 `MATCH`, `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10 rev=9420341d...`.

Row argv (census/round-30/c1-rows.tsv): R07 `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh`; R08 `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools`; R09 `python3 tests/fixtures/r19-carry-wrap.py`; R10 `python3 tools/souji-rev-pin.py --selftest`; R11 `python3 tests/fixtures/r19-rev-pin.py`; R12 `python3 tools/souji-declared-evidence.py --selftest`.

Stability: each row run twice at base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` and twice at lane HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (24 runs, private `--no-local` clone, origin removed, TMPDIR inside item scratch). All 24 gave identical (rc, last digit-bearing line after the counter's own normalization):

```
R07 rc=0 SUMMARY total=29 failed=0
R08 rc=0 SUMMARY total=35 failed=0 skipped=2
R09 rc=0 SUMMARY total=4 failed=0 base_discriminating=2
R10 rc=0 SUMMARY total=11 failed=0
R11 rc=0 SUMMARY total=13 failed=0 base_discriminating=6
R12 rc=0 selftest=8/8
```

Red before (corrections absent), scratch clone, base revision, exit 1:
```
SUMMARY k1=5 k2=0 mismatches=5 rows=6 pointers=10 partial=1 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
KINDS value=0 shape=5 rc=0 (diagnostic; not part of the target)
```

After (append block committed in scratch as `b9a903e3c286dbb341bb93ae30b7a56e8a59ee5d`), both exit 0:
```
--only R07,R08,R09,R10,R11  -> SUMMARY k1=0 k2=0 mismatches=0 rows=5 pointers=10 partial=1 rev=b9a903e3c286dbb341bb93ae30b7a56e8a59ee5d
--only R07..R12             -> SUMMARY k1=0 k2=0 mismatches=0 rows=6 pointers=10 partial=1 rev=b9a903e3c286dbb341bb93ae30b7a56e8a59ee5d
```
Per-row output in both after-runs: R07-R11 `CORRECTED`, R12 `MATCH`, and all 10 `PTR SHONEN.md:*` lines `RESOLVES` (k2=0). Full ROW/PTR text is in the delivery file.

Counter command shape (no `--only` once the L1 integrates; `--only` is diagnostic per the counter's `--help` text and sets `partial=1`):
`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py --root <lane> --rev <full40> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631`

## Findings
1. SCORECARD.md:160 (R07) states `29/0` but the fixture prints `SUMMARY total=29 failed=0`; `29/0` is not a substring, so the counter classifies it `kind=shape`. `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:160`.
2. SCORECARD.md:161 (R08) states `35/0` but prints `SUMMARY total=35 failed=0 skipped=2`; the fixture header defines SKIP as never a pass — `tests/fixtures/r17-jj-receipts.sh:63` says "and SUMMARY<TAB>total=PASS+FAIL<TAB>failed=N<TAB>skipped=N. Exit 0 when no" and line 65 adds "precondition. SKIP is never counted as a pass."
3. SCORECARD.md:166 (R09) states `4/0`; prints `SUMMARY total=4 failed=0 base_discriminating=2` (`tests/fixtures/r19-carry-wrap.py:235`).
4. SCORECARD.md:167 (R10) states `11/0`; prints `SUMMARY total=11 failed=0` (`tools/souji-rev-pin.py:374`).
5. SCORECARD.md:167 (R11) states `13/0`; prints `SUMMARY total=13 failed=0 base_discriminating=6` (`tests/fixtures/r19-rev-pin.py:220`).
6. R12 (SCORECARD.md:171) is not a defect: `selftest=8/8` contains the stated `8/8` with rc=0, so no `R30-CORRECTION` line is emitted for it; adding one would be inert but noise.
7. Append-only safety: SCORECARD.md and SHONEN.md are byte-identical between base and lane HEAD `df6afe8` (`git diff --quiet` over both paths returned 0), so a five-line EOF append keeps `sc_rev.startswith(sc_base)` true — the condition the counter's append-only guard tests.
8. Line numbers in the correction lines are the c1-rows.tsv line ids (160/161/166/167), not recomputed from the appended file; appending shifts no existing line, and line 167 legitimately carries two rows (R10, R11) distinguished by row id.
9. R08 emits `skipped=2`; recorded verbatim in the observed string rather than interpreted. [INFERENCE] the skips are environment-dependent, so the L1 should re-run the full counter at the C1 landing commit; if a skip disappears the observed line changes and that row would require the recorded line updated to the landing-time output.

## Deliveries
- `.ufo/waves/round-30/w1/deliver-c1-corrections-R07-R12.txt` — the five append-only lines, per-row reasons, 24-run stability table, and the red-before/after counter output with revisions.

Scratch `/fast/scratch/hyaku/souji-r30/C1RowsB` (clone, proof commit `b9a903e`, output captures) was removed after the receipts above were written into the delivery file. No lane file was modified; no git/jj mutation ran outside that scratch; no tool was installed.
