STATUS: DONE — All four assigned census suites reproduce the claimed no-harm totals at 5efb519.

Attacked claim: C1 operability — selftest and retained R17/R15/R14 census-suite totals at `5efb519f00075d958c3d1109ef6fcb24c487eb87`.

Findings by severity: None. All four commands exited successfully and returned the claimed totals:

- Command: `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest`
  Output: `selftest: 62 checks, 0 failed`.
- Command: `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh`
  Output: `SUMMARY total=29 failed=0`.
- Command: `python3 tests/fixtures/r15-census-config.py --tool tools/souji-census.sh`
  Output: `SUMMARY total=20 failed=0`.
- Command: `python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh`
  Output: `SUMMARY total=12 failed=0`.

All ran in `/var/tmp/souji-r18w2-RerunCensusSuites/lane`, cloned from the named repository and checked out detached at `5efb519f00075d958c3d1109ef6fcb24c487eb87`. The three fixture outputs independently report the census tool SHA-256 as `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`.

Verdict: Holds for the four assigned no-harm totals. Smallest fix: none indicated.

Residual risk and verification gaps: This rerun covers only the specified selftest and R17/R15/R14 fixtures; it does not independently validate the other C1 claims or the rest of the Round 18 assignment. No tools were installed or updated.
