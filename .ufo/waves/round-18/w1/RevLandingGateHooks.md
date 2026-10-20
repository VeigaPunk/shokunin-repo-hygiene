STATUS: DONE — Scoped compatibility review complete; the requested files have no diff from the supplied base.

Axis reviewed: calibration.

## Findings

- **MEDIUM — Round-77 fixture exercises the new check but does not pin its result.** `tests/fixtures/r16-landing-gate.py:66-68` sets the historical replay to round 15 but all synthetic cases to `ROUND = 77`; synthetic invocations therefore satisfy the proposed `--round >= 18` condition. Case `missing-reg-and-changed` includes `tools/ghost.sh` in `SKILL.md` without creating that file (`:282-305`). Under the specified dangling-pointer rule, that path is a dangling-pointer candidate, so the observed rows will gain `LG-DANGLING-PTR`; current assertions only require `LG-MISSING-REG` and `LG-PARSE-CHANGED` and do not pin the new row. The clean control (`:486-495`) checks `SUMMARY findings=0` and enumerates absent IDs, but omits the new one. The summary already catches an unintended finding there, yet the absent-ID list should be extended for explicit ID coverage. Update the fixture's documented ID list (`:15-27`), assert the new finding in the `tools/ghost.sh` case (or add a dedicated positive case), and add `LG-DANGLING-PTR` to `clean-all-green`'s absent list. This is fixture coverage, not a change to the round-15 replay expectation.

- **LOW — Keep the finding-ID pin synchronized; add round-18 selftest coverage.** `tools/souji-landing-gate.py:56-57` documents the pinned IDs and `:115-123` defines `FINDING_IDS`; add `LG-DANGLING-PTR` to both. The selftest helper at `:882-895` compares each case's exact ID set, but calls `evaluate(..., 16, ...)` at `:888-889`; its existing expectations should remain unchanged if the new check is correctly gated at round 18. Add a dedicated >=18 case with an exact expected ID set to prove the new branch. `FINDING_IDS` is not referenced elsewhere in this file (targeted search found only its declaration), so there is no selftest that directly asserts that tuple as a global closed list. `emit()` (`:705-755`) serializes arbitrary finding IDs generically; no emitter change is required.

## Pinned replay impact

No pinned replay multiset changes if `LG-DANGLING-PTR` is gated by the supplied run's `round_no >= 18`. `census/round-17/gate-replays.py:72-78` pins rounds 15, 13, 14, 16, and 16; the corresponding `gate-replays-expected.json` records those same historical rounds (`:12-23`, `:25-58`, `:60-182`). All are below 18. The fixture's historical `REPLAY_ROUND` is also 15 (`tests/fixtures/r16-landing-gate.py:64-67`). Do not add the new ID to those historical findings or rederive the frozen replay JSON. Its gate identity is deliberately recorded as `5fa6017` (`gate-replays-expected.json:3-9`); the runner reports a gate-SHA match separately, while replay comparison is by exit and exact `(id,path)` multiset (`gate-replays.py:165-190`, `:292-320`). `PROSE_CLAIMS` (`:80-90`) is historical documentation, not a comparison input.

## Verification and gaps

- Scoped diff command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-landing-gate.py census/round-17/gate-replays.py census/round-17/gate-replays-expected.json tests/fixtures/r16-landing-gate.py` → no output.
- Revision command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`.
- Scoped stat command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-landing-gate.py census/round-17/gate-replays.py census/round-17/gate-replays-expected.json tests/fixtures/r16-landing-gate.py` → no output.
- LSP was unavailable: `read xd://lsp` returned `No such tool: xd://lsp` and listed no LSP device, so no semantic references/definition/diagnostics were obtainable. Findings above use the exact-file source reads and targeted searches instead.
- No tests or runtime checks were run. The implementation diff is absent at this base, so the review verifies the compatibility condition and identifies required fixture/selftest updates, not behavior of a landed implementation.
