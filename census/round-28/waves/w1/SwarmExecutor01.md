## Status
STATUS: PASS — Q57 site selectors externalized and the check cell now uses the committed mapping authority; checker returned q57=PASS, rc 0.

## Evidence
- Revision inspected: lane HEAD `0c96332932e66bbaf9cf1c246091d3275a0ab612`; preregistration base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`.
- `wc -l census/round-28/q57-sites.txt; awk '{printf "%d: %s\\n", NR, $0}' census/round-28/q57-sites.txt` → 4 lines:
  1 `corpus/lessons/round-24.md:240`
  2 `corpus/lessons/round-24.md:232:S118`
  3 `LOG.md:1692`
  4 `SCORECARD.md:181`
- `bash tests/fixtures/r25-q57-check.sh . census/round-24/records/slice-verdicts.tsv census/round-24/records/slice-verdicts.tsv corpus/lessons/round-25.md $(cat census/round-28/q57-sites.txt)` → recount `8 accepted`; both `POINTS` checks; four `SUPERSEDED` sites; `q57=PASS`; `rc=0`.
- Before (HEAD Q57 check command): `bash tests/fixtures/r25-q57-check.sh . census/round-24/records/slice-verdicts.tsv .ufo/waves/round-24/assimilation/slice-verdicts.tsv corpus/lessons/round-25.md corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692 SCORECARD.md:181`
- After: `bash tests/fixtures/r25-q57-check.sh . census/round-24/records/slice-verdicts.tsv census/round-24/records/slice-verdicts.tsv corpus/lessons/round-25.md $(cat census/round-28/q57-sites.txt)`.
- Findings location: `corpus/QUALITY.md:141`; selectors: `census/round-28/q57-sites.txt`.

## Findings
1. Replaced the uncommitted second mapping argument with `census/round-24/records/slice-verdicts.tsv` and substituted the four explicit selectors with `$(cat census/round-28/q57-sites.txt)`; the unchanged surrounding cell text is preserved. Location: `corpus/QUALITY.md:141`.
2. The checker still passes all four selector checks as superseded using the authoritative mapping. Location: `census/round-28/q57-sites.txt` and `tests/fixtures/r25-q57-check.sh`.

## Attack log
None.
