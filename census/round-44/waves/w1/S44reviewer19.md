# S44reviewer19 — C2 h3

Axes: calibration / operability / coverage; assigned axis operability.

No actionable defect found in scenario `h3-two-unattached-keys`. Independently derived expected multiset: one `C0:HEADING-MALFORMED` and two `C0:UNATTACHED-KEY`; checker exit 1. Frozen checker matched exactly under both selected r44 and historical r43 audits (each audit exit 0, scenarios=1 pass=1 fail=0). Historical h3 oracle is unchanged and correct; no claim about whole-audit historical red is revised.

One-defect mutant changes BADHEAD's space repetition from `*` to `+`. It emits two `C1:KEY-DUPLICATE` instead, still exits 1, and the selected r44 audit rejects it (exit 1, scenarios=1 pass=0 fail=1). Therefore the scenario discriminates a concrete malformed-heading regression beyond generic exit status.

Detailed derivation, source citations, exact command/output, limits and self-evaluation: [S44reviewer19/report.md](S44reviewer19/report.md). Machine-readable exact receipts: [S44reviewer19/receipts.json](S44reviewer19/receipts.json). Reproducer and frozen source copies are retained in that seat directory.

Bounded probes only; no whole-suite validation or production changes. LSP unavailable (`xd://lsp`: no such tool), so inspection used literal source fallback without semantic-proof claims. Python 3.14.8 / Git 2.56.0; no installs. Seat scratch removed; receipt confirms. No admission or score increase asserted.
