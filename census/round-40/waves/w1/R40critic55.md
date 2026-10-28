# R40critic55 — C1 calibration attack

- Axis: calibration.
- Distinct edge case: **merge-commit ancestry is reachability through any parent, not proof of first-parent/linear temporal succession**.
- Frozen claim read first: `census/round-40/preregistration.txt:5`.
- Verdict: **bounded measurement plan; r40 candidate behavior NOT MEASURED.** This is an interpretation boundary in the phrase “strict descendant,” not an observed r40 failure.

## Evidence

- The frozen C1 predicate requires every anchored item line to have a resolvable revision-bound pointer and requires register `commit` to be a strict descendant of `receipt_rev`; its explicit kill condition is backwards/equal commits (`census/round-40/preregistration.txt:5`). It does not specify first-parent ancestry.
- The r39 reconciler implements ancestry with `git merge-base --is-ancestor` (`tools/souji-citation-reconcile.py:204-211`); the register loop uses that reachability relation for receipt revision ancestry (`:300-320`). A Git merge commit can therefore be a descendant because the receipt revision is reachable from its *second* parent, even if its first-parent chain does not contain the receipt revision.
- The r39 counter's own `parse_register` only counts nonempty `commit != receipt_rev` strings (`census/round-39/c1-counter.py:136-152`); it does not establish any ancestry or strictness by itself. This reinforces that the new r40 predicate must be assessed from its actual implementation and tests, not the r39 summary field.

## Counterexample / bounded falsifier

Construct a disposable DAG with receipt revision `R`, unrelated first-parent history `U`, and merge commit `M` whose second parent is `R` and first parent is `U`. `R != M`; `R` is an ancestor of `M` under Git's ordinary reachability, but not on `M`'s first-parent chain. If “strict descendant” is intended to mean ordinary commit-graph ancestry, accepting this row is correct and not a falsifier. If the intended calibration requires same-lineage/first-parent succession, accepting it is a concrete counterexample. The preregistration currently names neither interpretation, so this distinction must be resolved by recording which relation the candidate actually enforces; do not silently claim first-parent semantics.

Measure against explicit base/candidate revisions in a disposable fixture: (1) linear strict-descendant control, (2) equal revision, (3) older parent, and (4) the second-parent-only merge above. Keep receipt bytes and all row fields fixed except revision topology. Capture fixture HEAD, exact commands, stdout/stderr and statuses. Under the literal graph-descendant reading, only (2) and (3) must reject; (4) should pass. A candidate that uses first-parent-only semantics should document that stricter interpretation and demonstrate corresponding control. Separately preserve the token-only anchored item probe and require it remain OPEN; it is orthogonal to this topology test.

## Commands actually run

- Read `/home/vgpnk/.omp/agent/RULES.md`.
- Read `census/round-40/preregistration.txt`.
- Read `census/round-39/c1-counter.py:136-163`.
- Read `tools/souji-citation-reconcile.py:204-211,300-320`.
- No shell commands, candidate counter, tests, or fixture were run. No installs, scratch files, or repository mutations.
