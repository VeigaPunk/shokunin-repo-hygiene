# S44reviewer21 — C2 scenario 5/10

## Result / findings

No actionable production defect found in the assigned scenario. Frozen h5 passes its independently derived oracle in both r44 v2 and historical r43. A single-defect class regression is killed despite preserving the correct tool exit code. This is a scoped recommendation, not admission or integration approval.

Axes: calibration / **operability** / coverage. No numerical score delta claimed; admission remains outside non-author closure.

## Independent expected multiset

Selected row: `h5-control-symlink-exit0-text` (`census/round-44/c2-scenarios.tsv:6`, audit `SCENARIOS` at line 119).

From `tools/souji-freeze-check.py:7-27`, the checker reads committed blobs, reports sorted findings, exits 1 for findings, and refuses Control symlinks at FREEZE without treating their link text as control content. The fixture (`c2-hidden-audit.py:48-89`) creates one otherwise valid C1 claim, an ancestral Base, matching Counter/Population hashes, no dispatch files, and a committed `census/control.txt` symlink whose target text is `EXIT=0`. Freeze equals the evaluated revision, so there is no edited-frozen finding. A Git blob exists for the symlink even though its filesystem target is absent.

Therefore the independently expected **multiset** is exactly `{C1:CONTROL-SYMLINK × 1}`, tool exit **1**, one claim, one finding. No CONTROL-MISSING or CONTROL-NOT-RED: `evaluate()` gets the symlink blob, takes `repo.is_symlink()` before receipt parsing (`tools/souji-freeze-check.py:223-237`); `Repo.is_symlink()` checks tree mode 120000 (`:88-90`). The TSV and v2 row agree with this derivation.

## Bounded execution and exact output

Frozen source revision: `d314fd6e85d62565344fa6c4b102f52f62297884`. `probe.py` retrieves all inputs using `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show REV:PATH`, not mutable worktree bytes. SHA-256 receipts: `frozen-sha256.json`; counter and population match preregistration hashes.

Commands executed:

```sh
mkdir -p /fast/scratch/hyaku/souji-r44/S44reviewer21 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer21
# cwd=/fast/scratch/hyaku/souji-r44/S44reviewer21
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44reviewer21/probe.py
```

Driver exit: 0. The driver copies each audit into scratch, selects only h5 with an AST table filter, and invokes its existing `main()` and canonical tool subprocess. Its Git adapter asserts fixture `git rev-parse --show-toplevel` equals the fixture before every post-init Git call; init is followed immediately by the same assertion. No lane/index mutations occurred. Exact subprocess argv (including generated commit), cwd, stdout, stderr and exit are retained in the three JSON receipts below.

V2 baseline (`v2-baseline.json`), tool exit 1, stderr empty:

```text
FINDING C1 CONTROL-SYMLINK census/control.txt is a symlink at freeze
SUMMARY claims=1 findings=1
```

Audit exit 0:

```text
scenario-h5-control-symlink-exit0-text=PASS
SUMMARY scenarios=1 pass=1 fail=0
```

Historical r43 selected row (`r43-baseline.json`): identical tool output, tool exit 1, stderr empty, identical audit PASS output and audit exit 0. Its h5 expectation (`census/round-43/c2-hidden-audit.py:117`) is unchanged. The historical full audit remains documented red due to h4 repetition notation and h6 missing FROZEN-EDITED; neither defect affects h5. No historical full-audit rerun was performed or claimed.

## Single-defect mutant killed

Scratch-only replacement at `tools/souji-freeze-check.py:229`, retained exactly in `mutant-change.txt`:

```diff
- found.append((label, "CONTROL-SYMLINK", "%s is a symlink at freeze" % path))
+ found.append((label, "CONTROL-NOT-RED", "%s is a symlink at freeze" % path))
```

This regresses only the observable finding class of the Control-symlink branch. V2 selected h5 rejects it (`v2-mutant.json`): tool still exits 1, stderr empty, but stdout is:

```text
FINDING C1 CONTROL-NOT-RED census/control.txt is a symlink at freeze
SUMMARY claims=1 findings=1
```

Audit exit 1:

```text
scenario-h5-control-symlink-exit0-text=FAIL
#   got rc=1 classes=C1:CONTROL-NOT-RED
SUMMARY scenarios=1 pass=0 fail=1
```

Thus h5 checks the class, not merely a nonzero exit. This does not demonstrate sensitivity to every possible symlink implementation defect.

## Residual risk / verification gaps

- Only scenario 5 was executed: no whole counter, full ten-case audit, selftest, resume or runtime-routing checks. No claim of 10/10 saturation.
- The auditor's `classes()` (`:101-107`) compares class multiplicity and return code, not detail strings or SUMMARY correctness. Changes limited to those text fields can survive h5; no broader output-contract guarantee is established here.
- Semantic tooling was unavailable: `read xd://lsp` returned `No such tool`. No answering server existed for references/definition/diagnostics. Source-path reasoning above is textual, not semantic-reference proof.
- No tool installs/upgrades or service restarts. Used existing Python 3.14.8 and git 2.56.0.
- Driver printed `SCRATCH_REMOVED=True`; all seat scratch was removed before handoff. Retained artifacts contain no fixture repository or frozen-counter modifications.
- Permanent production changes and shared bookkeeping were intentionally untouched. All executable candidates existed only in seat scratch; the retained replay driver and receipts reside in the seat output directory.

## Self-evaluation

Accuracy 4/5: raw outputs and frozen hashes retained; no LSP evidence available. Completeness 4/5: selected scenario, historical contrast and killed mutant covered; no full-audit result claimed. Clarity 4/5: independent derivation precedes receipts; generated absolute argv is delegated to JSON for brevity. Actionability 4/5: retained replay driver and one-line mutant are concrete; replay requires the named scratch path to be writable. Conciseness 4/5: repeated exact outputs are intentional evidence. Overall 4.0/5. Improvement priority: semantic tooling if available, then stronger detail/SUMMARY assertions in a separately authorized audit change. The scoped claims should match the user's assessment; these ratings are not admission.
