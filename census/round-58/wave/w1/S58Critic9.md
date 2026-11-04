# S58Critic9 — frozen-claim/control attack

## Axes and boundary

C1 calibration: measured assessment accuracy, not Markdown visibility. C2 operability: five specified receipt-interface refusals and preservation of three real receipts. Coverage and legacy numeric scores unchanged. Predicate identity and historical-byte preservation are constraints, not replacement axes. This is critic evidence, not admission or a canonical Rust judgment.

## Counterexample attempts and observed evidence

### C1: unchanged state, wrong measurement, moved predicate

I executed the frozen counter bytes from `e7f64f30324e8ddb3f2266302daa9066054cdbb3` against that revision and correction revision `dccdc469f4c2e0415e1a1dcc317364e1b4d3191e`.

| Arm | Assertions | Mismatches | Identical | Exit-zero pair | EXIT |
|---|---:|---:|---:|---|---:|
| Frozen unchanged control | 2 | 2 | 34 | 10,8 | 1 |
| Correction revision | 2 | 0 | 34 | 10,8 | 0 |

Independent named-column arithmetic found 36 rows per committed matrix, unique fixture identities, matching fixture order, 34 equal `(exit, findings_all)` pairs and per-file zero-exit counts 10 and 8. Thus combined total 18 is not a per-file result. Counter SHA256 `52ccdb1be66dd8379fb7bf81eae7e28965f156aa50e1e4573b82adb23bd0dea7` is unchanged between the frozen and scored revisions. The observed correction patch adds seven SCORECARD lines and deletes none.

Evidence: `S58Critic9/c1-results.json` and `S58Critic9/c1-receipts.txt` retain commands, committed blob output, counter output and EXIT. Invocation: `python3 -B .ufo/waves/round-58/w1/S58Critic9/c1-probe.py`, EXIT=0.

Deletion legs were **not rerun by this seat**. Reviewed sibling evidence `S58Reviewer7/results.json`: omit either note => mismatches=1, EXIT=1. Its notes-without-original-assertion and duplicate-row mutants can remain green: the frozen counter checks correction strings and positional matrix comparisons, not general append-only integrity or identity preservation. These are counter-authority limits, not observed corruption of the scored correction. Smallest safe correction: retain the immutable matrix/revision evidence and do not promote this bounded assessment repair into a Markdown/parser or universal provenance claim; do not rewrite the frozen predicate after scoring.

### C2: exact same fixture under old and changed implementations

I reused the delivered independent acceptance builder once, then ran both implementations against the **same eight case inputs**, not separate approximations. The old arm was extracted from the frozen commit, not a mutable working-tree copy. The three real rows exactly match `census/round-57/manifests/after.tsv`.

| Case | Frozen r57 EXIT / finding IDs | Changed EXIT / finding IDs |
|---|---|---|
| Absolute path | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| `../` traversal | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| Intermediate symlink escape | 0 / none | 1 / RECEIPT-PATH-UNCONFINED |
| Annotated tag object OID | 0 / none | 1 / RECEIPT-REV-ABSENT |
| Conflicting standalone rev headers | 0 / none | 1 / RECEIPT-REV-CONFLICT |
| Real c1-tip receipt | 0 / none | 0 / none |
| Real c2-tip receipt | 0 / none | 0 / none |
| Real standing receipt | 0 / none | 0 / none |

The fixture verifies that the supplied tag OID has raw type `tag` and peels to the reachable fixture commit. Hence the old clean result is a real raw-object-identity counterexample, not a missing-object approximation. Both conflict headers name reachable commits. All path controls point to otherwise honest receipt bytes.

Evidence: `S58Critic9/c2-results.json` retains fixture construction commands, guarded scratch toplevel checks, manifest text, full finding lines, stdout/stderr, EXIT, real-receipt hashes, and tag/receipt contents. The r57 control meets none of the five refusal expectations; the changed candidate meets all eight expectations. Both gate hashes stayed identical before/after scoring:

- Frozen r57: `174d7b8a3c105875f1757f9137f26ed54e38ac11c963a134015bce8a9dd16ec2`.
- Changed delivery `S58Executor3/c2-gate.py`: `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`.
- Acceptance builder `S58Executor4/c2-acceptance.py`: `55b5e063fa57a02d7fcf186c9d8e9b719b0ecb76b08001ad0988ad76aa3fc82e`, unchanged after scoring; planner identifies its frozen commit as `1880343ed04337379c5478f91408c30c8fbd4b77` (peer-reported, not independently resolved by this seat).

Invocation: `python3 -B .ufo/waves/round-58/w1/S58Critic9/c2-probe.py /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-58/w1/S58Executor3/c2-gate.py`, EXIT=0. JSON command records are absolute.

Implementation identity changed after the first scoring: executor reported an L1-authorized fixture-safety revision, replacing initial `dfd90d9da263d0bdc28d118bbc75f355c41432034854a2de3b3ab7749cbc3bdf`. I did not transfer prior success to new bytes: I reran the unchanged acceptance builder and all eight cases against the new digest above, with the same observed outcomes, EXIT=0. Original observations remain in `S58Critic9/c2-results-superseded-dfd90d9.json`; current `c2-results.json` records the rescored identity. Predicate bytes did not change. Selftest cleanup behavior itself was not probed by this seat. Own scratch was removed again after evidence capture.

A second L1-authorized implementation revision removed the emit-expected overwrite CLI and changed malformed-expected handling (executor-reported purpose). I again rescored all eight assigned cases using unchanged acceptance bytes: final digest `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543` has the same required outcomes, invocation EXIT=0. Previous safety-revision results remain in `S58Critic9/c2-results-superseded-7c35d3e.json`; current `c2-results.json` is final-identity evidence. Malformed-expected CLI behavior was not independently probed by this seat.

Smallest safe correction to the old counterexamples is the candidate's confinement-before-read, exact raw commit-object typing and conflicting-header refusal; no additional production correction is supported by these eight observations. The changed gate prefers standalone rev headers over rev tokens in body output. Accordingly, the result is not evidence of execution authentication or rejection of every body-token ambiguity. Acceptance compares ordered finding IDs and preserves full lines; it does not independently assert exact finding-detail text.

## Disposition and unrun legs

Neither do-nothing control reaches its frozen target. No required candidate failure or scored predicate drift was observed in the assigned probes. C1 supports only measured assessment correction; C2 supports only the five refusals and three clean preserved receipts above. No claim is made about universal parsing, privacy, races, cleanup, or historical counter correctness. These bounds are tradeoffs for the canonical judge, not a critic admission.

This seat did not run gate selftests, acceptance stub selftests, idempotence legs, broad historical suites, builds, lint or formatters. Sibling selftest claims are not substituted for own execution. No production/sibling file edits, commits, pushes, installs, services or configuration changes. Scratch git fixture init/add/commit were confined to guarded explicit `-C` paths. Own scratch was removed after copying evidence; cleanup command EXIT=0. Reusable probe drivers remain in this seat's delivery directory.

Self-evaluation: accuracy 4/5 (immutable own observations; acceptance-freeze commit peer-reported); completeness 4/5 (all assigned control/candidate cases exercised; deletion legs sibling-reviewed only); clarity 4/5 (case table and scope limits); actionability 4/5 (exact hashes and smallest correction, integration reserved to planner); conciseness 4/5 (raw receipts separated). Overall 4.0/5. Improvement: integration should bind the scored gate digest to its final committed identity without modifying predicates. Would the user agree? Expected yes: no expanded repair/admission claim.

Report: .ufo/waves/round-58/w1/S58Critic9.md
