# TruncatedTargets — calibration review

## Evidence basis

Read-only source analysis of the bounded round-20 files; no target code, tests, builds, or runtime were executed. The supplied review baseline is `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; I did not compare the working file to a commit blob. The inspected working-tree snapshot of `tools/souji-seat-audit.py` was 672 lines, SHA-256 `ddb03e993c80445ed16c70de83855248bf326ed4a578ba5a95ab169da9266617` (observed 2026-10-21T06:01:20-0300). Earlier reads saw the file grow from 651 to 672 lines; the finding below is anchored to the 672-line snapshot and not an assertion about later edits.

No LSP device/route is exposed in this seat's tool inventory (`read xd://lsp` returned “No such tool”). The grep results used below are literal locators only; no caller/definition/diagnostics semantic proof is claimed. No tools were installed or updated.

## Finding — Major calibration false negative

**`tools/souji-seat-audit.py:251-252, 266-279, 347-350, 668` — a truncated absolute target with a visible prefix under the granted scratch root is cleared, even though the hidden suffix may escape the grant.**

`write_targets` strips the rendered ellipsis and marks the bare target truncated (`:251-252`). `target_verdict` only rejects a visible `..` component before entering the truncated branch (`:266-268`). It then normalizes the visible prefix and returns `None` whenever that prefix is under the scratch root (`:276-277`). `audit_seat` skips every `None` result (`:347-348`), so this path creates no finding at all. In contrast, the same path with its full `..` components visible is classified `V-WRITE-SCOPE` by `:266-267` and, for a successful write, is major. The CLI fails only on major findings (`:668`), so the truncated form can turn an out-of-scratch write into a clean exit.

Concrete rendered counterexample shape, with the selftest scratch grant `/var/tmp/souji-r9-S/`:

```text
→ write(/var/tmp/souji-r9-S/out…) ⇒ ok
```

The pre-truncation path may continue with enough ordinary in-scratch components to reach the renderer's cut, then a suffix containing enough `..` components to climb above `/var/tmp/souji-r9-S` and `/home/u/P/f/lane/SKILL.md`; that complete path normalizes outside scratch. The classifier sees only `/var/tmp/souji-r9-S/out`, considers it under scratch, and emits no violation. The exact renderer cutoff is not specified by the bounded source, so this is a falsifiable classifier-input counterexample, not a claim that a historical seat emitted it.

This contradicts the pinned ambiguity rule at `:40-43` (“too little is visible to allow or refuse”): the hidden suffix makes the target not provably inside scratch. It is also inconsistent with the adjacent fail-closed handling of a truncated prefix of an allowed file (`:280-282`, `V-WRITE-UNPARSED`) and the existing scratch-ancestor ambiguity cases (`:512, :515`). A truncated header can reach the same clearance: `write_targets` records unclosed header fragments as truncated at `:240-243`, and the absolute truncated branch does not distinguish headers.

**One concrete oracle change:** add this case to the `selftest()` cases near `:508-516`:

```python
("scratch-trunc-inside", "executor",
 "→ write(/var/tmp/souji-r9-S/out…) ⇒ ok",
 [("V-WRITE-AMBIGUOUS", "minor")], seat_scratch)
```

This is the minimum severity consistent with the existing `V-WRITE-AMBIGUOUS` contract and makes the current empty result falsifiable. The existing mapping gives ambiguity minor severity (`:349-350`), so that minimal repair surfaces but does not itself make the CLI fail; grading potentially escaping writes as major would require an explicit severity-policy change beyond this oracle case.

## Residual risk and verification gaps

- The tool describes rendered transcripts as a lower bound at `:46-48`; this review did not inspect a historical transcript or establish an incident.
- The assigned rev-pin source uses an exact 40-hex `COMMIT_RE` (`tools/souji-rev-pin.py:34, 195-199`), a fail-closed contrast for abbreviated revisions; that does not repair this separate scratch-target classification.
- LSP semantic checks were unavailable. No test or runtime behavior was exercised, as required for this read-only assignment.
