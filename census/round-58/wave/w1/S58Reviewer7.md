# S58Reviewer7 — C1 adversarial review

Axes: calibration truth, exact assertion binding, frozen-evidence integrity, no historical/grammar harm.

Reviewed frozen predicate `e7f64f30324e8ddb3f2266302daa9066054cdbb3` and actual landed C1 diff through `dccdc469f4c2e0415e1a1dcc317364e1b4d3191e`. This is a recommendation, not admission. No production edits.

## Findings by severity

### Medium — counter alone does not establish matrix identity/cardinality

`census/round-58/c1-counter.py:18-19` counts positional column five and compares `exit`/`findings_all` with `zip`; it neither joins fixture identities nor checks equal length/uniqueness. Scratch `matrix-identity-byte` changes one fixture identity but still returns the exact target summary and EXIT=0. Scratch `duplicate-v5-nonzero-row` appends an existing refused row to v5 (37 versus 36 rows); the extra row is invisible to zip and does not change zero counts, so the exact target still passes. A changed exit byte and omission of v6's final row were detected (EXIT=1, mismatches=2).

Impact: an exact green summary cannot independently certify that these are the original committed matrices, or that 34 matched pairs refer to the same fixture inventory. This is an instrument coverage limit, **not an observed corruption of the landed matrices**. The actual diff changes only SCORECARD among the reviewed C1 paths; independently inspected inputs have 36 unique fixture IDs in each arm in the same order. Preserve that frozen-input/identity evidence alongside the counter rather than claiming it checks arbitrary matrix corruption. Do not amend historical counters to resolve this review.

### Low — correction presence is not historical-assertion/supersession validation

`census/round-58/c1-counter.py:20-25` tests exact sentence substrings. Scratch `notes-without-original-assertion` replaces the entire SCORECARD with only the two expected notes and still passes; `contradictory-prose` explicitly restores the original assertions' authority after those notes and also passes. Duplicate exact notes pass. Thus the instrument's `mismatches` means missing expected correction sentences, not a general semantic discrepancy census or append-only/history validator.

Actual landed text does not exhibit these attacks: `SCORECARD.md:1432` retains the original assertion and command; `1462-1467` appends the two correction sentences with the exact r57 matrices and instrument as authority. The carry note quotes the exact original assertion substring, and the exit note disambiguates the original two-file awk claim. This finding limits counter-only claims; it does not request Markdown visibility/filing-grammar repair, whose harms intentionally remain open.

## Measured result and controls

Independent named-column assessment of the committed matrices: rows 36/36, unique IDs 36/36, same order, exit-zero 10/8, identical exit plus full-findings pairs 34. Original combined awk command was exercised and emitted `18`, EXIT=0.

Frozen control: assertions=2 mismatches=2 carry_identical=34 exit_zero=10,8, EXIT=1.
Landed revision: assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8, EXIT=0.

Twelve isolated committed scratch-fixture probes:

| Probe | Observed EXIT | Outcome |
|---|---:|---|
| honest | 0 | exact target |
| omit carry note | 1 | mismatches=1 |
| omit exit note | 1 | mismatches=1 |
| junk-only notes | 1 | mismatches=2 |
| wrong numeric notes | 1 | mismatches=2 |
| notes without original assertion | 0 | exact target; binding gap |
| contradictory prose | 0 | exact target; semantic gap |
| matrix exit byte | 1 | carry=33, exit_zero=9,8 |
| matrix identity byte | 0 | exact target; identity gap |
| omit final v6 row | 1 | carry=33, exit_zero=10,7 |
| duplicate refused v5 row | 0 | exact target; inventory gap |
| duplicate notes | 0 | exact target; no uniqueness enforcement |

Recommendation: the two actual appended corrections are numerically supported and both omission kill checks work. No exercised probe falsifies the narrowly frozen two-correction claim **on the unchanged committed matrices**. Do not expand that conclusion into robust matrix validation, semantic prose evaluation, Markdown repair, or historical counter closure.

## Evidence and verification gaps

- `.ufo/waves/round-58/w1/S58Reviewer7/receipts.txt`: observed commands, stdout/stderr, EXIT for frozen inputs, actual diff, production measurement, fixture setup and every probe. Explicit `git -C` and toplevel assertions precede fixture add/commit; identity values were process-local, with no external config changes.
- `.ufo/waves/round-58/w1/S58Reviewer7/results.json`: production/frozen revisions, independent counts, per-case output and fixture commit IDs.
- `.ufo/waves/round-58/w1/S58Reviewer7/probe.py`: reproducible probe driver; fixtures removed after evidence delivery.
- `.ufo/waves/round-58/w1/S58Reviewer7/combined-count.txt`: original command, output `18`, EXIT=0.

LSP device unavailable (`xd://lsp` returned no such tool); semantic references/definition/diagnostics could not be run. Text inspection is not represented as semantic-server proof. No builds, lint, formatters, C2 probes, runtime rerouting/resume/saturation checks, or historical Markdown grammar tests were run; those are outside this assigned C1 leg. No tools installed, no services/config changes, no production commits/pushes. Scratch-only commits were used under the assignment's explicit fixture allowance.

Self-evaluation: accuracy 4 (LSP unavailable); completeness 4 (12 assigned scratch probes, no general semantic parser claim); clarity 4 (separates landed result from counter limitations); actionability 4 (retain frozen identity evidence, no out-of-scope repair); conciseness 4 (full receipts separate). Overall 4.0. Improvement: canonical admission should explicitly retain unchanged matrix evidence rather than infer it from the green summary.

Report: .ufo/waves/round-58/w1/S58Reviewer7.md
