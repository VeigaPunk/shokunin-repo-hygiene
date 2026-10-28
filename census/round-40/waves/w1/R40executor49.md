# R40executor49 — C1 calibration attack

## Named axis and distinct edge

**Axis: calibration.** Distinct attack edge: the counter's `commit_distinct` summary is a row-level inequality count, not a count of distinct commit revisions, and it does not itself prove the required strict `receipt_rev` ancestry relation. This is separate from the frozen headline attacks (missing evidence-pointer binding and backwards/equal register commits): it tests whether the calibration summary can be misread as a stronger, cardinality-based observation than it actually establishes.

## Evidence and commands

All inspection used the committed r39 artifacts; no lane implementation was modified and no shell command/test was run.

- `census/round-39/c1-counter.py:136-152` (`[souji-shokunin/census/round-39/c1-counter.py#5F80]`): `parse_register` increments `distinct` once for each row where `commit` is nonempty and differs from `receipt_rev`; it does not maintain a set of commit hashes. Its docstring at lines 136-137 calls this the rows whose commit differs.
- Same file `:155-184`: `register_leg` delegates findings to the revision-pinned citation reconciler and returns `ok:<distinct>` from that row counter. The reconciler output summary is parsed, but this function does not independently evaluate graph ancestry between `commit` and `receipt_rev`.
- `census/round-39/cells.tsv:1-7` (`[souji-shokunin/census/round-39/cells.tsv#9309]`): six register rows share the same `commit` (`a8e6d75…`); each differs from its receipt revision. The last receipt revision differs from the five preceding ones. Thus there are six differing rows but only one distinct commit hash.
- `corpus/lessons/round-39-verifier-spotcheck.md:44-52`: independent closure explicitly derives the six rows as strict descendants, then notes `commit_distinct=6` is a count of differing rows and that the register names one distinct commit. This confirms the cardinality distinction from committed review evidence.
- `census/round-40/preregistration.txt`, C1 paragraph: frozen target requires evidence pointers, strict-descendant `commit` vs `receipt_rev`, and a token-only forged item remaining OPEN.

Inspection calls: `read` on the required preregistration and rules; `read` on `corpus/lessons/round-39-verifier-spotcheck.md`; `read` on `census/round-39/c1-items.tsv`, `census/round-39/c1-counter.py`, `census/round-39/cells.tsv`, and `census/round-39/c1-counter.py:136-185`. Search call: regex `receipt_rev|strict descendant|evidence pointer|token-only` over the lane tree. No installs.

## Verdict and bounded measurement

**Verdict: bounded measurement plan, not a falsifier of the frozen C1 predicate.** The evidence demonstrates a reporting-semantic hazard in r39: `commit_distinct=6` can be mistaken for six distinct commit revisions, although the actual register has one. The r39 independent closure already discloses this, so it is not evidence that r40's strict-descendant predicate fails.

To measure the distinct edge on candidate bytes, use a scratch copy of the r40 register with multiple valid receipt rows intentionally sharing one later commit, and compare (a) number of register rows, (b) number of unique commit hashes, and (c) rows where `commit` is a strict descendant of `receipt_rev`. Require the counter's labels/values to distinguish these counts; separately run equal and ancestor/backwards commit controls and confirm each is rejected. This is not yet run: no r40 counter/register candidate receipt was inspected or executed here. The committed r39 comparison remains: six differing rows, one unique commit hash; independent review records the strict-descendant relation for all six.
