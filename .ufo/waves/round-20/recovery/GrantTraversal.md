# GrantTraversal — round-20 calibration review

## Observed source and scope

The preregistration names baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. My first full read of `tools/souji-seat-audit.py` reported a 629-line source image. Later bounded reads showed 651 lines and a subsequent grep index `#9BCF` showed 656 lines, including a changed `scratch_path` signature. Per the item instruction, the finding below is scoped to the first-read bytes; I did not wait for or review a settled post-read version. The read output did not expose a SHA-256 for that first image, so I cannot claim a source-byte digest. No target code was executed.

## Findings (severity order)

### MAJOR — unvalidated `reportDir` traversal becomes an unconditional report-write grant

**STATUS: OPEN.** In the first-read `souji-seat-audit.py`, `run()` takes `spec["reportDir"]` with only `.rstrip("/")`, concatenates it to `lane` to form each seat's `report`, and supplies that path to `audit_seat()` as an allowed target. `target_verdict()` rejects `..` components in the *transcript target*, but for absolute targets it then compares `_norm(target)` against `_norm(p)` for every allowed path. Thus traversal in the authority-side report directory is collapsed into a grant before the lane boundary is checked. The per-item `OWN ONLY` extractor similarly accepts an absolute string without rejecting `..` (`owned_paths()`); it can reach the same normalized-allow path.

**Concrete counterexample:** with `lane=/home/vgpnk/Projects/shokunin/souji-shokunin`, a spec `reportDir="../outside"`, item name `S`, and transcript line `→ write(/home/vgpnk/Projects/shokunin/outside/S.md) ⇒ ok`, `run()` constructs report `/home/vgpnk/Projects/shokunin/souji-shokunin/../outside/S.md`. The target has no `..`; its normalized absolute path equals the normalized report path, so the write is not classified `V-WRITE-SCOPE`, despite being outside the lane. This is a static derivation, not an executed test.

Relevant locations in the later line-indexed source view: `tools/souji-seat-audit.py:126-129` (`owned_paths`), `:258` (`target_verdict`), and `:384-395` (`reportDir` and report construction; latest locator view was `#9BCF`). The first-read source excerpt showed the same logic but the file subsequently reflowed, so these later line numbers are locators, not a claim that the first-read image had identical numbering.

**One oracle change:** add a run-level case with `reportDir="../outside"` and the transcript above; require spec refusal (CLI exit 2, no JSON output) or a major scope violation, never an allowed report write. Also reject `..` components in authority paths before normalization so `OWN ONLY` cannot bypass the same boundary.

## Residual risk and verification gaps

- The other named path boundaries reviewed did not show this lexical traversal-to-grant route: `souji-rev-pin.py:94` onward rejects absolute paths and `.`/`..` components before joining and rejects symlink components; r13 `validate_output()` (`census/round-13/run-verification.py:342` onward) normalizes then checks lane containment, round-directory equality, and symlink ancestors; r14 `output_path()` (`census/round-14/run-verification.py:82` onward) rejects absolute and `..` paths before joining and checks the parent; `run-targeted.py` delegates to that shared output validator. The demo's synthetic dependencies are checked through realpath containment (`cache-demonstration.py:174-176, 432-444`), and its final `git_head()` refusal returns before emitting a result (`:1210-1219`). These are source observations only.
- The seat auditor's lexical scratch containment does not resolve symlinks. A symlink beneath an explicitly granted scratch root could redirect a write outside it; this remains a documented/bounded lexical-symlink limitation, not a tested observation here.
- No LSP route/status was exposed in the available tool inventory, so no semantic references/definition/diagnostics checks were possible. No builds, tests, linters, smokes, or target execution were run, as required.
- Because the auditor source changed between bounded reads, the OPEN finding is specifically against the first-read 629-line image. Post-read L1 behavior is unverified; no polling or re-review was performed.