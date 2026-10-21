# C1 multi-path boundary review

## Findings

No false positive or false negative found for the requested complete/truncated semicolon-component cases in the pinned auditor at `522dcd768ca90afe166532d37d306d3df70aeea5`.

The frozen C1 rule says semicolon-separated path components are judged individually and the call is flagged if any component is outside the lane (preregistration lines 6–10). In `tools/souji-seat-audit.py`, `implicit_root_read` selects the path after the last ` @ ` for grep (lines 379–381), splits that path on `;` (389), skips empty or visibly truncated components (390–392), skips absolute and URI components (395–397), and lexically resolves each remaining relative component at fleet root before checking whether it is outside the lane (398–401). `audit_seat` turns a returned target into one minor `V-READ-ROOT` (455–458).

Bounded outcomes for the requested shapes:

- `grep(pattern @ /absolute/path;corpus/x)`: the complete absolute component is ignored; `corpus/x` resolves from fleet root outside the lane and returns as the flagged target. This is the contract-required positive case.
- `grep(pattern @ /absolute/path;corpus/x…)`: the absolute component is ignored and the visibly truncated relative component is skipped, so no `V-READ-ROOT` is emitted. This is the disclosed lower-bound behavior for a truncated component.
- `grep(pattern @ corpus/x;/absolute/path…)`: the complete relative component is checked and flags; the truncated component cannot suppress it. This follows the contract's per-component rule.

The fixture at `tests/fixtures/r21-read-root.py` includes the complete positive mixed-path case (`semicolon`, line 35) and standalone truncation cases (lines 52–55). It does **not** include a single call mixing complete and truncated components, so it would detect the first case but would not detect a regression specific to the mixed complete/truncated behavior. The historical `grep(PATTERN in PATH)` exception is handled separately in the implementation (lines 382–384) and represented by fixture case `historical-renderer` (line 58), consistent with the clarification (line 2).

## Residual risk and verification gaps

This is a bounded source review of the specified forms, not an execution result. No code, fixture, build, or test was run. The fixture's omission of mixed complete/truncated components leaves that exact interaction without synthetic coverage; it is not evidence of a current behavior defect. No other C1 behavior is assessed here.