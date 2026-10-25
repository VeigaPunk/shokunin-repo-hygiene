# Round 11 — gate record
Declared: census --compare contract fix, toolchain re-certification, rubric
scoring. Outcome: **REJECTED as a round — fix landed and verified;
certification NOT granted.**

## Landed
- tools/souji-census.sh = cand-census-02 (52-line load_census fix):
  empty/blank-led/malformed priors exit 2; selftest 36/36; all three
  cert-16 regression shapes refuse. The last open defect class from r9
  is closed in the tools.

## Why certification was NOT granted
- Certifier evidence-integrity defects (upheld by the final judges):
  cert-16.json was used as a shared relay and overwritten repeatedly;
  CERTIFIED verdicts were attached to bytes other than those measured;
  one candidate-selection rule (most selftest checks) picked a candidate
  that fails the class. Per fail-closed discipline: no certification on
  compromised evidence.
- Rubric appliers ran, but new scores stay UNRATED until a clean
  certification pass exists.

## Next session carry
Re-run the certifier suites under a no-relay protocol (each certifier
writes its own fragment; parent aggregates), then flip certification and
rate the axes.
