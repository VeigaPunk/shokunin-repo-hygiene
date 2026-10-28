# R41w2executor04 — axis-harm audit, fixtures (r36..r41) base vs tip

Lane tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f vs base 7eebc183f2685d1ea9b004b4de22c09a8a4035a7.
Both trees extracted with `git archive <rev> | tar -x` into /fast/scratch/hyaku/souji-r41/R41w2executor04/{base,tip} (scratch removed at yield).
Evidence in this seat dir: `w2/R41w2executor04/{drive.py,out-base.txt,out-tip.txt,logs/log-<arm>-<fixture>.txt}` (each log starts with the exact CMD and ends with EXIT).

## Method (commands actually run)
`python3 -B drive.py base > out-base.txt` and `python3 -B drive.py tip > out-tip.txt` (cwd = scratch; each fixture run with cwd = its extracted tree, TMPDIR and --work under scratch, tool = that tree's `tools/souji-worktree-drift.py`).
Arg mapping: drift fixtures `--tool <tree>/tools/souji-worktree-drift.py --work W`; citation fixtures (r37-citation-reconcile, r38-citation-commit, r38-counter-arms, r39-citation-rev) `--tool <tree>/tools/souji-citation-reconcile.py` (first pass wrongly fed them the drift tool: rc 2 "--record required", discarded and rerun); r37/r38 mutants `--fixture r37-drift-discrimination` / `r38-drift-record --base-fixture r37-drift-discrimination`; r37-drift-escapes + r38-drift-write-envelope `--base-tool <base>/tools/souji-worktree-drift.py`; r36-report-gate, r40-c1-evidence `--work` only; r40-docstring-joined `--tool` only.
Tip tool sha256 = b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (equals the frozen pin); base tool sha256 = e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76.

## Results (base | tip; SUMMARY verbatim, exit code)
| fixture | base | tip |
|---|---|---|
| r36-report-gate | `cases=21 pass=21 fail=0 control=STUB-REJECTED` rc0 | identical rc0 |
| r36-worktree-drift | `cases=12 pass=12 fail=0 control=STUB-REJECTED` rc0 | identical rc0 |
| r37-citation-reconcile | `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` rc0 | identical rc0 |
| r37-drift-discrimination | `cases=6 pass=6 fail=0` rc0 | identical rc0 |
| r37-drift-escapes (--base-tool = base tool) | `cases=12 pass=12 fail=0 base_fail=0 escapes=0 control=ESCAPE-NOT-REPRODUCED` rc1 | identical rc1 |
| r37-drift-mutants | `mutants=6 killed=6 survived=0` rc0 | identical rc0 |
| r38-citation-commit | `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` rc0 | identical rc0 |
| r38-counter-arms | `cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED` rc0 | identical rc0 |
| r38-drift-mutants | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0` rc0 | identical rc0 |
| r38-drift-record | `cases=10 pass=10 fail=0` rc0 | identical rc0 |
| r38-drift-write-envelope | `cases=12 pass=12 fail=0 base_cases=12 base_fail=0 behavioral_fail=0` rc0 | identical rc0 |
| r39-citation-rev | `cases=8 pass=8 fail=0` rc0 | identical rc0 |
| r39-drift-record-rules | `cases=7 pass=7 fail=0` rc0 | identical rc0 |
| r40-c1-evidence | `cases=11 pass=11 fail=0` rc0 | identical rc0 |
| r40-docstring-joined | `cases=9 pass=9 fail=0` rc0 | identical rc0 |
| r40-drift-record-branches | `cases=8 pass=8 fail=0` rc0 | identical rc0 |
| r41-drift-record-order | n/a (not at base) | `cases=12 pass=12 fail=0` rc0 |
| r41-refusal-sites | n/a | `probes=21 pass=21 fail=0` rc0 |

`diff` of the base and tip SUMMARY/exit lines (paths stripped): the only differences are the four added r41 lines. No r36..r40 fixture changed result.

Note: r37-drift-escapes exits 1 at BOTH base and tip only because the control wants `--base-tool` = the r36-era blob (its docstring says so); with the base tool the escapes are not reproduced. Rerun with the r36 blob (`git show 0d974ff:tools/souji-worktree-drift.py`, sha256 52b9312178d016a824ec81b08a63fa50076327f5c7929c2195c38b354e5f8f0b), both trees: `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` rc0 (base arm and tip arm). So the exit 1 is a pre-existing control-arg artifact, not a regression.

## Inputs identical base vs tip (cmp)
All 16 r36..r40 fixture files byte-identical; tools/souji-citation-reconcile.py, tools/souji-pre-report-gate.sh, census/round-40/docstring-classes.py byte-identical. The only changed tool is tools/souji-worktree-drift.py (`git diff` base..tip: +9/-2 — docstring wording on RECORD-MALFORMED, `totals = []`, `totals.append(total)`, `for total in totals:` in parse_record).

## Causality of the TOTAL repair
Since fixtures and every other tool are identical, the tool diff is the only variable and no r36..r40 result moved, so the TOTAL repair caused no fixture change (no fixture in r36..r40 supplies a record with a disagreeing TOTAL that is not last, or any multi-TOTAL record; consistent with r40 M40-4 being a survivor). Positive control: the tip r41 fixtures run against the BASE tool: r41-drift-record-order `SUMMARY cases=12 pass=7 fail=5` rc1 (case-total-first-bad-repos/-regs/-prunable, case-total-middle-bad, case-total-before-rows-then-bad all `rc=0 want=2`) — i.e. the repair is exactly what flips those five cases; r41-refusal-sites against base tool `probes=21 pass=21 fail=0` rc0 (it covers refusal sites, not the TOTAL ordering, so it does not discriminate the repair).

## Verdict
No axis harm in the fixture suite: 16/16 r36..r40 fixtures identical base→tip (SUMMARY and exit code); r41 fixtures 12/12 and 21/21 at tip with the pinned tool; the five R1 cases fail on the base tool and pass on the tip tool, so the TOTAL repair is the cause of the only observed delta and it is in the intended direction. Residual observation (not a regression): r41-refusal-sites does not discriminate base from tip tool.
