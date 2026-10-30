# S44reviewer18 — C2 scenario 2/10

Axes: calibration / operability / coverage. Primary assignment: operability.
Frozen source revision: `d314fd6e85d62565344fa6c4b102f52f62297884`.
Result: selected scenario passes against frozen tool and kills one single-defect mutant. No actionable production defect found within this scenario. Admission is outside this non-author review; no score delta or whole-suite claim.

## Independent expected multiset

Selected row: `h2-round-spelled-x\t1\tC0:ROUND-MALFORMED` (`census/round-44/c2-scenarios.tsv:3`). Builder kwargs are `{"round_line": "Round: 1729x"}` (`census/round-44/c2-hidden-audit.py:113`).

Derivation from `tools/souji-freeze-check.py`:
- Documented grammar at lines 21–25 permits only ASCII `[1-9][0-9]*` for a present Round value, emits ROUND-MALFORMED otherwise, and suppresses dispatch scanning.
- `ROUND` at line 50 is anchored through trailing whitespace and end-of-line. `1729x` cannot match.
- `dispatch_findings` at lines 130–136 identifies this one present malformed Round line and immediately returns one `("C0", "ROUND-MALFORMED", "detail=Round: 1729x")`.
- Builder lines 65–89 provide one otherwise complete C1 block, valid prior base, exact counter/population digests, two nonblank population lines, red control, and no post-freeze mutation or early dispatch. Therefore no other finding is expected.

Independent expectation: return code **1**, multiset **{C0:ROUND-MALFORMED × 1}**. This agrees with the selected frozen table/audit row; it was not derived merely from their agreement.

## Exact bounded exercise

Command (initial scratch/output directories were explicitly created with `mkdir -p`):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer18/probe.py
```

Execution cwd: `/fast/scratch/hyaku/souji-r44/S44reviewer18`.

`probe.py` reads each source through `git -C LANE show REV:PATH`, copies each audit into seat scratch, imports the copy, and selects only the h2 row via `SCENARIOS = tuple(chosen)`. It wraps git calls to assert the fixture top-level identity before every add/commit, and wraps the audit runner to retain exact command/stdout/stderr/exit/classes. No production/frozen source was edited. All four runs are the selected row only: r44 real/mutant and r43 real/mutant. Source copies, mutant, driver and exact JSON receipts are retained in this directory.

Frozen real tool, both r44 and r43 selected audits:

```text
actual tool exit=1
FINDING C0 ROUND-MALFORMED detail=Round: 1729x
SUMMARY claims=1 findings=1
```

Tool stderr was empty. Actual classes: `["C0:ROUND-MALFORMED"]`.

```text
scenario-h2-round-spelled-x=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Each audit returned 0; audit stderr was empty. `receipts.json` records full commands including exact fixture revision `ffdc127cbeabf7403b014d41b7ab9bb0fb083109`.

## Single-defect mutant killed

Only `ROUND` changes:

```diff
-ROUND = re.compile(r"^\ufeff?Round:[ \t]*([1-9][0-9]*)[ \t]*$")
+ROUND = re.compile(r"^\ufeff?Round:[ \t]*([1-9][0-9]*x?)[ \t]*$")
```

This improperly admits an optional x suffix. Frozen tool SHA-256: `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`.
Mutant SHA-256: `d7310fa0d4baaaceb305aa626fa17858e4629d7fc20e1df06140defcf5983f04`.

Observed against both selected audits:

```text
actual tool exit=0
SUMMARY claims=1 findings=0
```

Tool stderr empty; classes `[]`. Audit output:

```text
scenario-h2-round-spelled-x=FAIL
#   got rc=0 classes=-
SUMMARY scenarios=1 pass=0 fail=1
```

Each audit returned 1. Thus the scenario detects the grammar regression via both required status and required finding multiplicity, without relying on a crash.

## Historical contrast

The r43 h2 tuple (`census/round-43/c2-hidden-audit.py:112`) is identical to r44 h2. Empirically both accept the frozen tool and reject this mutant. The repaired r44 oracle adds no new h2 discrimination; the documented r43 repairs concern h4 and h6, not this row. This selected-row result does not claim the historical full audit is green; preregistration explicitly retains its historical red.

## Residual risk and verification gaps

- This row covers one malformed suffix only. It does not independently establish rejection of leading zero, signs, Unicode digits or other malformed forms, nor dispatch-scan suppression when early wave files coexist. Those were not executed; one killed mutant is not saturation.
- The audit compares return code and sorted classes, not exact details/SUMMARY or empty stderr (`c2-hidden-audit.py:101–107,159–165`). Those observable bytes are retained here but are not assertions of the selected audit.
- `xd://lsp` is unavailable (device returned “No such tool”). Semantic reference/definition/diagnostics queries could not be made. Source reads and runtime receipts are the fallback, not semantic proof from grep.
- No whole C2 counter, full audit, selftest, production mutation, rerouting/resume runtime or unrelated suite was invoked. None is needed for this bounded h2 assignment. No admission or saturation determination was made.

## Provenance and cleanup

`receipts.json` records source hashes, exact expectations/actuals, commands and versions. Frozen scenario-table hash matches preregistration: `6a68a10161745c7974e93afe9724853f1a61fc192185c128c88840b1977a7054`. Relevant C2 counter was read; its registered whole-counter target was not executed or claimed. Python `3.14.8`, Git `2.56.0`; no tool install/update or pacman transaction. Scratch was removed in the driver's `finally` block; observed `scratch_removed=true`. Only seat output artifacts remain.

Self-evaluation: accuracy 4 (bounded observed evidence, no full-suite inference); completeness 5 (derivation, historical comparison, killed mutant and exact receipts); clarity 4 (full raw detail is in JSON rather than inline); actionability 5 (preserved reproducible driver and mutation); conciseness 4 (provenance repeats some receipt fields). Mean 4.4/5. Improvement: consult receipts for full raw commands; broader grammar cases remain explicitly outside this seat's execution scope.
