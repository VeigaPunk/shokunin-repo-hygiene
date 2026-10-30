# S44reviewer61 — C1/Q76 review

Axes: calibration / operability / coverage; scoped axis calibration.

**Result: 0 newly unaccounted self-assessment mismatches under Q76.** All 70 r44 population occurrences exactly repeat r42: 65 already-bound paths and 5 existing scoped corrections; 66 unique keys, four duplicate occurrences.

Bounded frozen-revision runs:
- r42 C1: `items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, exit 0.
- r44 C1: `population=70 corrections=0 registered=0 missing=70 ... new_mismatches=0 instrument_mismatches=66 lesson=absent`, exit 1.

Medium finding: interpreting missing r44-format registration as 70 outstanding fact corrections would overstate calibration. Frozen preregistration line 4 already forbids that interpretation; retain it. Raw scanner mismatches are not erased, and no broader truth/admission claim is made.

Full findings, exact commands/output, per-row classification, limitations and hashes: [S44reviewer61/report.md](S44reviewer61/report.md), [audit.txt](S44reviewer61/audit.txt), [classification.tsv](S44reviewer61/classification.tsv). Canonical evidence: `corpus/QUALITY.md:186`, `corpus/lessons/round-42.md:41-87`, and `census/round-42/c1-register.tsv:2-71` at frozen `d314fd6e85d62565344fa6c4b102f52f62297884`.

LSP unavailable; textual evidence is fallback only. No installs or production mutations. Admission remains outside non-author closure.
