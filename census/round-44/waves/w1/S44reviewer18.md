# S44reviewer18 — C2 scenario 2/10

Full report and exact evidence: [S44reviewer18/report.md](S44reviewer18/report.md), [receipts.json](S44reviewer18/receipts.json), [reproduction driver](S44reviewer18/probe.py).

Axes: calibration / operability / coverage; assigned operability. Frozen revision `d314fd6e85d62565344fa6c4b102f52f62297884`.

Result: independently derived h2 `Round: 1729x` expectation is exit 1 and multiset `{C0:ROUND-MALFORMED × 1}`. Frozen tool produces exactly that; selected r44 and historical r43 audits each report `SUMMARY scenarios=1 pass=1 fail=0`, exit 0. A one-regex optional-x-suffix mutant produces exit 0/no findings and both selected audits reject it with `SUMMARY scenarios=1 pass=0 fail=1`, exit 1. No actionable production defect found within this scenario; no whole-suite, saturation, admission or numerical-score claim.

Residual gaps: only h2 exercised; details/SUMMARY/stderr are retained but not asserted by the audit. LSP device unavailable; source inspection/runtime receipts used instead. No installations, production edits, counter changes or shared bookkeeping edits. Seat scratch removed (`scratch_removed=true`).
