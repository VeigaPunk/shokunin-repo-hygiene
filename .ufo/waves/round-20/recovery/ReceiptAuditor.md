# Receipt auditor review

Axes reviewed: calibration of the auditor-byte receipt, falsifiability of the claimed binding, and evidence scope.

## Finding

**MEDIUM — C1 receipt can fingerprint disk bytes other than the executing auditor module.** `tools/souji-seat-audit.py:364-365` reads `Path(__file__)` from disk only after `run()` has been entered; the module is already loaded before the CLI calls `run()` at lines 612-626. The drift check at lines 401-404 compares the file only with the bytes captured at line 364, and lines 410-415 publish that snapshot as the auditor input digest. **STATUS: OPEN** — [INFERENCE] If an already-imported auditor's source path is replaced before `run()` captures it (or a concurrent edit lands in the CLI load-to-capture window), the old loaded code can execute while the new stable file's digest is returned; the late reread passes. This does not establish a fresh runtime occurrence, but it is a falsifiable gap in binding the receipt to the auditor that actually ran.

**Concrete oracle:** in an isolated temporary copy, import the auditor, atomically replace that copy's `.py` file before calling `run()`, and assert that the receipt either refuses or binds to the pre-load source bytes—not the replacement bytes. Capture the source identity before module execution, or otherwise make this code/input identity explicit; a post-capture reread alone does not close the load-to-capture interval.

## Observed revision and bytes

At review, `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. The worktree `tools/souji-seat-audit.py` SHA-256 was `08a006657357e94d9153a6279c723340d7b586aa806c2355ec206253f09133c6`; the same path read from `HEAD` had SHA-256 `62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6`. Thus current source bytes differ from the reported/base revision bytes. The receipt serializes `input_sha256` but contains no code-revision field (`tools/souji-seat-audit.py:372, 410-415`); these two identities must not be described as equal. These are source/hash observations only; no auditor run was performed.

## Residual risk and verification gaps

The `lsp` device is unavailable (`read xd://lsp` reported no such tool), so caller/definition/diagnostic checks could not be obtained. A literal local search was used only to locate symbols, not as semantic proof. No tests, builds, linters, formatters, or target-code execution were run; no tools were installed.