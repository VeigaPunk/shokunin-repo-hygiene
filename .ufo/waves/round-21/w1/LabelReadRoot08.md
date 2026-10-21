# C1 independent V-READ-ROOT labels

Applied only the frozen C1 rules from `.ufo/waves/round-21/preregistration.txt`. Searched each of the 39 named transcript files with the exact grep pattern `→ (read|grep|glob)\(` and inspected the matching physical lines in context. The independently labelled rows are in `LabelReadRoot08.tsv`.

- Matching tool-call lines: 103 (expected 103).
- FLAG: 0.
- OK: 88.
- UNSEEN: 15 (the target/path was visibly truncated with `…`; C1's explicit lower-bound rule says not to flag such calls).
- No glob calls appeared among the matches.

There were no genuinely ambiguous cases under the written rules. In particular, the truncated targets in `recovery-final/F5Authority.txt` lines 57, 66, and 77 and the multi-path grep in `recovery-final/F5Enumeration.txt` line 79 are UNSEEN under the explicit truncation rule, rather than inferred to be violations. Complete URI targets and absolute paths are OK, including absolute paths outside the lane, because C1 expressly excludes them from V-READ-ROOT.

No auditor code was read or executed. No tools were installed.
