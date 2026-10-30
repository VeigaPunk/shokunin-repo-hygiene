# S44reviewer26 — C2 scenario 10/10

Full report and exact evidence: [S44reviewer26/report.md](S44reviewer26/report.md); raw commands/output: [receipts.json](S44reviewer26/receipts.json).

Result: frozen h10 passes independently derived rc=2, empty finding multiset, and canonical refusal. Historical r43 h10 is identical and also passes. Scenario kills a wrong-exit single-defect mutant.

Medium coverage gap: `census/round-44/c2-hidden-audit.py:138-144` accepts a spurious FINDING on the refusal path because it checks only rc=2 and stderr substring REFUSAL. One added print in the missing-prereg branch survives: expected classes `[]`, actual `[C0:NO-CLAIMS]`, audit still PASS. Recommendation only: tighten repaired h10 output assertion; retain historical r43 unchanged.

Only four selected-row probes were run; no full counter or unrelated validation. LSP unavailable. Scratch removed (`scratch_removed=True`). No production changes or tool installations. Admission remains outside this review.
