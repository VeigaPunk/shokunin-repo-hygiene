# ContainmentLimit — D5 and frozen r14 boundary

## Scope and observed bytes

Axes reviewed: **signal-identity containment**, **durable-ref/frozen-input boundary**, and **signal-auditor oracle coverage**. The preregistration declares baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`. Initial working-byte SHA-256 observations were:

| Path | SHA-256 |
|---|---|
| `tools/souji-seat-audit.py` | `78d73d85ba198df6614a47b5d4d9388038da5c74407b475148713bc8958f6269` |
| `tools/souji-rev-pin.py` | `869d399ca1ec2868e9c794e438298a9dfd844eed76e5d477fa38b710f170e49d` |
| `census/round-13/run-verification.py` | `945cf6ecd5f4472c2556eb6f0b26e0a42193268a158cf3a0a8d776c00ef1d0cc` |
| `census/round-14/run-verification.py` | `bde95f972e09de393d32b1aa840bc2282f1677c147399ae7ed24c6558f525f73` |
| `census/round-14/run-targeted.py` | `a0c08e1252df3b7c20cab6eaecaa8222c7eed5f39ba19188eca2da031c5fd3f2` |
| `census/round-14/cache-demonstration.py` | `706200486d0938322a773116ae01377f3a56ec82443415e0d1956cd126c95bd6` |

These are working-byte observations; I did not compare them with Git object blobs. This was static source/document review only: no target code, tests, fixtures, or runtime were executed; no tool was installed. The r15/r17 fixture sources were outside the allowed read set and were not opened. No LSP device was mounted (`xd://lsp` returned “No such tool”); literal grep results below are not semantic reference evidence.

## Findings

### MEDIUM — the documented D5 signal residual does not inventory the r13/r14 runner timeout paths

**Fresh source analysis:** `census/round-13/run-verification.py:279-281` starts each child in a new session; after `communicate()` raises `TimeoutExpired`, lines `285-290` call `os.killpg(process.pid, SIGTERM)` and, after another timeout, `os.killpg(process.pid, SIGKILL)` without rechecking process-group identity. `census/round-14/run-verification.py:107-108,112-118` has the same sequence for `child.pid`. `census/round-14/run-targeted.py:43` calls `module.run(...)`, so its commands use the r14 timeout path too.

**[INFERENCE]** If the child’s process group disappears after timeout detection but before `killpg`, and its numeric PGID is reused, the signal could reach a different process group. This is a possible race inferred from the call sequence, not an observed event. These calls are not the fixture cleanup cited in the r19 D5 discussion, but they present the same check/observation-to-signal boundary (without the fixture’s `(pid, starttime)` recheck).

**Historical receipts, not fresh execution:** `.ufo/reports/round-19/souji.md:184-188` calls D5 a bounded improvement, records the check-to-signal window and an unguarded fixture-cleanup `killpg`, and routes an open operability residual to r20; lines `373-375` say the later `killpg` is not covered by the per-PID check. The cited discussion does not mention the runner timeout call sites above. **Documentary correction:** include both runner paths in the D5 residual inventory, or explicitly state the rationale for treating runner-created session groups as outside that residual. This is a scope correction, not a request to make a runtime change in this lane.

### LOW — the auditor recognizes `killpg` but its selftest does not lock that case

**Fresh source analysis:** `tools/souji-seat-audit.py:113-115` includes `os.killpg` and `killpg` in `SIGNAL_LIB_RE`. Its selftest rows at `:529-531` cover shell `kill`, `os.kill`, and quoted grep prose, but no `killpg` case. The rule summary at `:20-22` also lists `os.kill/proc.kill/send_signal` without naming `os.killpg/killpg`.

**Concrete oracle change:** add a selftest case equivalent to `("signal-killpg", "executor", "→ bash(python3 -c 'os.killpg(4242, 9)') ⇒ ok", [("V-SIGNAL", "major")], None)`. That makes the D5-relevant cleanup shape regression-visible and aligns the summary with the implemented matcher. This is a suggested oracle change only; it was not run here.

## Held-boundary observations (no adverse finding)

- `tools/souji-rev-pin.py:34-35` keeps `COMMIT_RE` at lowercase full 40-hex and `DURABLE_NAMESPACES` at exactly `refs/heads`, `refs/tags`, and `refs/remotes`. `:197-198,220-222` refuse HEAD/branch/short forms and revisions reachable only through `refs/jj`; static selftest cases at `:296-299,317-331` cover keep-only, HEAD, branch, and abbreviated-ID refusals. No namespace widening is present in the observed bytes.
- `census/round-14/run-verification.py:32-45` includes `tools/souji-rev-pin.py`, `census/round-14/run-targeted.py`, `tests/fixtures/r14-cache-frozen`, `corpus/SOURCES.md`, and the historical r13 evidence in `MEASURED_PATHS`; line `143` shows the frozen directory is actually passed to the `--frozen` check. `checked_inputs()` at `:75-78` compares the snapshot, and `:159-170` performs that recheck before opening the output file. This is source evidence of the intended binding, not a fresh run proving it.
- The separate F5 hold is documentary: the round-20 preregistration at `.ufo/waves/round-20/preregistration.txt:4` says F5 reap/NAMESPACE L0 requests are **HELD**, and `corpus/lessons/round-19-verifier-spotcheck.md:106,162` says `NAMESPACE_SHA256` remains held. I did not inspect or calculate that value or access operator-owned census content.

## STATUS: OPEN

The D5 signal-identity residual remains open for documentary disposition: the allowed current-source read shows unguarded r13/r14 timeout `killpg` paths in addition to the r19 fixture-cleanup residual. The process-group reuse scenario is an inference, and no fixture-level PID-recycle proof was freshly reproduced. Historical fixture counts `20/0` and `29/0` in `.ufo/reports/round-19/souji.md:43,77` are receipts only, not execution in this review. The durable-ref namespace and the stated F5 hold remain consistent with the bounded material inspected; this is not independent closure or runtime verification.