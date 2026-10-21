# GrantPatch — calibration review

**Observed snapshot:** `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; the working `tools/souji-seat-audit.py` SHA-256 was `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6` and the file was marked modified. Review is source-only; no target code or tests were run.

## Major

**Unrequested own-stem `.patch` can evade the major finding when written by Bash.** `tools/souji-seat-audit.py:122,328-331` applies destination checks only to `WRITE_TOOLS` (`write`, `edit`, `ast_edit`). The `bash` branch at `:343-348` checks execution, recursion, and probes, but does not classify file-output targets. Thus a transcript such as `→ bash(printf x > <report-stem>.patch) ⇒ ok` has no `V-WRITE-SCOPE` path through this auditor; for an `executor` it also avoids the non-executor `V-EXEC` check. The path is not one of the forbidden surfaces. **[INFERENCE]** The current control flow would therefore leave an unrequested own-stem patch falsely clean, contrary to the per-item authorization rule.

The requested positive is handled for the supported write tools: `delivery_paths` derives the candidate from the seat report stem and admits a matching explicit directive (`:133-143`); `run` passes those grants into `audit_seat` (`:395`), which adds them to the allowed paths (`:328-331`). An absolute target equal to an allowed path returns no scope finding (`:272-276`). The selftest encodes the exact `DELIVER: <report-stem>.patch` positive expectation (`:579-582`); this was inspected, not executed.

**Concrete oracle change:** add an unrequested shell-redirection transcript targeting `<report-stem>.patch` and require `V-WRITE-SCOPE / major`. Keep the existing exact `DELIVER`-patch positive case. This exposes the bypass while preserving the intended explicit-grant calibration.

**STATUS: OPEN** — the auditor does not enforce the unrequested-patch rule across Bash output paths, so C1 cannot close on this slice.

## Residual risk and verification gaps

- The explicit-grant positive is established by static control flow and an unexecuted selftest expectation, not a fresh runtime receipt.
- LSP was unavailable (`read xd://lsp` returned “No such tool”); the two `grep` calls were used only to locate literal line anchors. Semantic review is from the bounded source read, not grep output.
- No builds, tests, linters, smokes, or target-code execution were performed, per lane instructions.