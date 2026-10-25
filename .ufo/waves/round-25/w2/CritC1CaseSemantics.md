# CritC1CaseSemantics — C1 k1–k7 semantics

Axes: calibration (7, lowest), operability (8), coverage (8). Read-only review; no lane edits beyond this report.

STATUS: PARTIAL

## Evidence

- Frozen C1 semantics: `.ufo/waves/round-25/preregistration.txt:32-55`; amendment 3 adds definitions/cases at `.ufo/waves/round-25/preregistration-amendment-3.txt:5-16`. Amendment 1 corrects expected base count to six at `preregistration-amendment-1.txt:5-13`.
- Current committed case builders: `tests/fixtures/r25-coverage-agreement.py:329-408`; scorer `:427-471`. Actual current tool: `tools/souji-coverage-agreement.py:103-132`.
- Bounded rerun, exact command from lane root: `python3 -B tests/fixtures/r25-coverage-agreement.py --tool tools/souji-coverage-agreement.py` → exit 0, final `cases=16 pass=16 control=FALSE-GREEN-REJECTED`. k1,k2,k5 report one KILL-RULE each; k3,k4,k6,k7 clean with tested=1/violations=0. This verifies only the committed listed fixture cases, not all frozen rule shapes.
- W1 report `.../.ufo/waves/round-25/w1/ExecC1.md:56-60` itself notes per-line counting is not discriminated.

## Findings

1. **Important frozen-shape hole: per-line kill_violations mutant survives.** Amendment 3 explicitly defines `kill_violations` as entries with >=1 violation and not per-line (`preregistration-amendment-3.txt:13-14`). But every violating k case has one entry and one violating ground (k1 deletion; k2 re-ground; k5 loses only F3), while k4 has multiple grounds but no violation and k5 drops only one of its two. A mutant counting failed grounds instead of failed entries returns identical observed counts for all k1–k7 (1 for k1/k2/k5; 0 for clean cases). This is a concrete mutant that passes the 16-case fixture while violating the frozen per-entry count. The fixture checks `kill_violations == kill_rows` (`fixture:468-469`), but those rows likewise are only one per entry in the current examples, so this does not discriminate the mutant.
   - Minimal witness follows the existing k5 builder (`fixture:368-378`): base e.md F2+F3, --rev e.md F2 only. Extend with base F4 too and remove both F3 and F4 at --rev. Required kill_tested=1, kill_violations=1, one KILL-RULE row; per-line mutant yields 2. This distinguishes contract. Alternatively add a separate multi-lost-grounds case.

2. **Base entry missing is covered; multi-ground and partial F removal are only partly exercised.** k1 deletes E (`fixture:335-340`), k4 preserves both F2/F3 (`:358-366`), k5 removes one of two grounds (`:368-378`). Thus missing blob and any-one-F-loss semantics have positive/negative witnesses; no case removes two grounds from one entry, so finding 1 remains.

3. **Several named boundary classes are not built by k1–k7:** extra F is exercised by k6; non-md file exclusion, symlink/type replacement, malformed base revision, and non-ancestor base are not represented in these builders. k9 tests malformed `--rev` only (`fixture:321-327`); it does not test malformed `--base-rev`. The frozen CLI defines full-40-hex and commit validation for base too (`preregistration-amendment-3.txt:15-16`; implementation `tools/souji-coverage-agreement.py:180-184`), but no corresponding fixture expectation. The current implementation checks target tree kind is blob (`:121-126`) but no fixture substitutes a symlink or tree for base E at target. Base need not be ancestor in the current implementation or stated contract; do not infer ancestry as a required semantic. A non-ancestor base is supplemental only absent an explicit frozen ancestry requirement.

4. **Required metrics are specified and nominally tested, with the count-mutant hole above.** `kill_tested` counts base-grounded entries; `kill_violations` counts violating entries, explicitly not lines (amendment 3 `:13-14`). Fixture case records carry expected counts; scorer checks both against expectations and requires violations equal KILL-RULE row count (`fixture:468-469`). Current tool returns `len(base)` and `len(kills)` (`tool:117-132`). However no committed case has >1 lost grounds on a single entry, so kill_violations-per-entry is not exactly distinguishable from per-ground count. `kill_tested` is exercised as 1 in each synthetic kill case, and 6 on real base-vs-base receipt (`w1/ExecC1/ c1-real-base-vs-base.tsv`, stdout line 9); it is not tested with multiple base-grounded entries in one kill repo, so a count-entries-vs-count-ground-lines mutant could potentially survive. The frozen definition requires entries, making that a second metric cardinality gap.

## Amendment separation

- Frozen core from prereg: k1 deleted, k2 regrounded, k3 clean, k4 multi-ground (`preregistration.txt:43-47`); amendments 1/2 do not change these predicates. Amendment 1 fixes the real-run expected count only.
- Amendment 3: k5 partial-removal, k6 extra-ground-allowed, k7 veto-less control, plus the entry-count definitions and non-full40 base refusal (`amendment-3.txt:5-16`).
- Supplemental/unfrozen probes, not a reason to narrow or rewrite the claim: non-md and symlink/type target cases; malformed base-rev despite the amendment's explicit CLI rule is within amendment-3 acceptance; non-ancestor base is not specified as a violation and should not be treated as a required failure absent contract text.

## Smallest safe correction

Add (without dropping or changing existing cases) one multi-base-entry case to assert `kill_tested` counts entries, and one base entry losing at least two distinct grounds to assert exactly one KILL-RULE and `kill_violations=1`. Keep malformed base-rev as a separate CLI test. Do not impose ancestry rejection absent a frozen requirement.
