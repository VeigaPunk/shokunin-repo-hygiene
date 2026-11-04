# S58Executor5 — independent C1 behavioral evidence

Axes: calibration correctness; sensitivity to each correction; append-only preservation; confinement/reproducibility.

## Result

All five assigned C1 legs passed against frozen predicate commit `e7f64f30324e8ddb3f2266302daa9066054cdbb3`.

| Committed fixture | mismatches | counter EXIT |
|---|---:|---:|
| Frozen SCORECARD and matrices | 2 | 1 |
| Append both exact emitted MISSING notes, stripping `MISSING ` | 0 | 0 |
| Separate fixture without carry-identical correction | 1 | 1 |
| Separate fixture without exit-zero correction | 1 | 1 |
| Append unrelated junk calibration note only | 2 | 1 |

Every leg asserted the complete summary: `assertions=2`, `carry_identical=34`, `exit_zero=10,8`, and the expected mismatch count. Deletion and junk legs additionally asserted both exact individual MATCH/MISSING lines. The two-note remedy preserved the original SCORECARD byte prefix. Separate deletion fixtures contain the original frozen SCORECARD plus just the retained correction, byte-equivalent to deleting the other correction from the appended remedy.

Exact appended notes:

```text
R58-CALIBRATION carry_identical=34 supersedes the r57 SCORECARD claim "all 33 carry-over rows".
R58-CALIBRATION exit_zero=10,8 counted separately per matrix; the r57 two-file awk command emits the combined total 18, not the pair.
```

## Retained delivery and invocation

- `.ufo/waves/round-58/w1/S58Executor5/c1-tests.py`: standalone standard-library behavioral driver, fetching pinned repository blobs; no imports from sibling deliveries.
- `.ufo/waves/round-58/w1/S58Executor5/receipts.txt`: every invoked subprocess command, complete stdout/stderr, observed EXIT, tool version outputs, fixture toplevel checks, and cleanup record.
- `.ufo/waves/round-58/w1/S58Executor5/results.json`: exact correction strings, per-leg fixture commits/output/EXIT, input SHA-256 values.
- `.ufo/waves/round-58/w1/S58Executor5/inputs/`: retained frozen SCORECARD, both matrices, and counter, preserving input bytes for inspection after scratch removal.

Observed command (EXIT 0):

```text
python -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-58/w1/S58Executor5/c1-tests.py
PASS base=2 append=0 delete-note-1=1 delete-note-2=1 junk=2
```

Driver refuses existing scratch; every fixture git command uses explicit `-C`. Fixture init requires no enclosing checkout; toplevel is checked after init and before each add/commit. Identity is process-environment-only, hooks disabled for commits, global/system git configuration excluded. Commits are disposable fixture commits only. Scratch `/fast/scratch/hyaku/souji-r58/S58Executor5/` was removed after evidence was copied.

## Bounds, risks, and unrun legs

No production edits; no historical counter changes; no fleet/sibling edits; no installs, configuration changes, services, pushes, or non-fixture commits. C2, builds, lint, formatters, and repository-wide tests were not run (outside assignment). No Markdown visibility or parsing repair is claimed. This proves sensitivity of the pinned literal-note predicate, not truth enforcement for arbitrary narrative or rendered Markdown. The driver requires Python, Git, and the pinned source commit still available in the repository; retained inputs preserve inspected bytes but the driver intentionally re-fetches the pinned objects. No LSP tool is mounted; no symbol refactor was needed.

Self-assessment: accuracy 4/5 (frozen predicate only, not arbitrary prose); completeness 5/5 (all five requested legs and cleanup observed); clarity 4/5 (full transcript intentionally verbose); actionability 4/5 (rerun requires pinned Git objects); conciseness 4/5 (retained raw input stdout duplicates copied inputs). Overall 4.2/5. Improvements outside this assignment: optional portable input-only rerun mode; condensed transcript index. User-agreement check: evidence supports only bounded C1 assessment correction, with every assigned leg run.

Report: .ufo/waves/round-58/w1/S58Executor5.md
