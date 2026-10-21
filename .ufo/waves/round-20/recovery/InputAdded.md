# InputAdded — operability review

## Finding — Major: r14 binding omits the counted knowledge directory

**Axis:** operability harmed for the promised measured-input boundary. This is a static source finding, not a fresh execution result.

At `tools/souji-rev-pin.py:148-168`, `input_snapshot` walks only the explicitly selected paths; its equality check at `:171-177` therefore cannot see leaves outside those paths. Round 13 selects `corpus/knowledge` as a directory (`census/round-13/run-verification.py:92-115`), so a new file there is included in its before/after snapshot, regardless of Git tracking state. In contrast, round 14's `MEASURED_PATHS` includes `corpus/SOURCES.md` but omits `corpus/knowledge` (`census/round-14/run-verification.py:32-46`). A newly added counted knowledge file is outside that snapshot, so this binding cannot reject it as an added leaf. `run-targeted.py:23-28` inherits the same incomplete list, and `cache-demonstration.py:80-89` has a separate measured list with no knowledge directory either. The preregistered C2 oracle explicitly requires each actual caller to reject a newly added counted knowledge path (`.ufo/waves/round-20/preregistration.txt:3`).

**Concrete counterexample / oracle change:** in the caller-level refusal fixture, start from a clean durable revision, add an admitted-format file under `corpus/knowledge/` that is both untracked and ignored, then require each applicable r14 caller (runner, targeted wrapper, cache demonstration) to refuse with exit 2 and no output. Include `corpus/knowledge` in each caller's measured input set (targeted may inherit the runner's set) and assert the receipt does not get written. This exercises directory re-enumeration rather than a tracked-file-only change.

## Evidence identity

Observed HEAD: `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline). Working-tree SHA-256 values captured for the bounded source set:

- `tools/souji-seat-audit.py` — `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6`
- `tools/souji-rev-pin.py` — `d3e9111b66f17242124df97db0327195c75a5c44252566d2130ff38c5755f32e`
- `census/round-13/run-verification.py` — `72f35605dbda4b2f06b44aa5ad63c8bfc93ff5276628f66475dccb5708df4633`
- `census/round-14/run-verification.py` — `70aa1ba2f503781ea0359756ef204ae5323e270b044f2856b8c3aab657eba96d`
- `census/round-14/run-targeted.py` — `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2`
- `census/round-14/cache-demonstration.py` — `df9209ac21169087bb8c4f114608d17124ad4b092a318a65c88f9aea48b98697`

## Residual risk and verification gaps

This review is source-only: no target code, tests, or runners were executed. No LSP device is mounted (`xd://lsp` returned “No such tool”), so no semantic references/definition/diagnostics were available; evidence above is from bounded source reads, not grep. The check does not establish runtime refusal behavior, and no claim is made about unrelated calibration or coverage axes. No tools were installed or updated.
