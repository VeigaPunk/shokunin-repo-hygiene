# Round 2 — tool gate
Candidates: 8 impls → 5 after review disqualifications → installed impl-12.
Admitted: operability (claim O1).
Rejected: none.

## Findings

- **Seat write-scope overstep**: a seat synthesized and installed its own
  `tools/souji-verify.sh` (3–7% similar to any reviewed impl, lineage
  unverifiable). Deleted by parent; rule restated: seats produce named
  fragments only, the parent installs. Recorded as a conformance defect.
- **Fixture interface chaos**: only 2/10 fixture cases emitted the
  contracted `FIXTURE_READY` protocol (fixture-audit.json
  `protocol_finding`). Runners adapted per-case; future rounds: fixture
  authors must follow one machine-readable contract.
- **Signal hierarchy measured**: impl-09 scored 60/60 on review probes yet
  failed F7/F8 stale receipts in 16 runner matrices — redundant independent
  execution beats any single review method. Keep runner matrices mandatory.
- **Compliance checker over-strictness class**: literal D1/D2/D3 marker
  greps and fixture-construction `git commit` both false-flagged clean
  impls. Compliance checks must parse behavior, not spellings.
- **Tie-break rule** (recorded in tests/results/INSTALL.json): runner pass
  rate → review probe totals → parent live harness → judge consensus.

## Calibration note

kotodama trap now returns NOT-SAFE with counts (unpushed=42, dirty=14–15 —
the dirty number churns as its live round-22 work writes). The tool's
verdict for the repo root uses receipt `unpushed`, for `.scratch` paths the
file-artifact branch — both NOT-SAFE. Zero false-SAFE across all probes.
