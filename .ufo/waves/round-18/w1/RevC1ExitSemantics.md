STATUS: DONE — C1 contract reviewed against the current census source; no implementation diff was present to review.

# C1 exit-semantics review

**Axes:** operability (primary); calibration (preserving the protected-refusal classification); coverage (making the failure modes observable in fixtures).

**Verdict:** The stated timeout-row behavior can coexist with the existing census contract, but only if worker status, output buffering, stderr, temp cleanup, and worker-group lifecycle are handled explicitly. The source tree had no `tools/souji-census.sh` diff at review time, so this is a contract/test review, not approval of a landed watchdog implementation.

## Source-grounded baseline

- `tools/souji-census.sh:211-215, 222-230`: `cleanup_census_tmp` unlinks the global `CENSUS_TMP`; `protected_fail` prints the protected finding to stderr and executes `exit 2`.
- `tools/souji-census.sh:1261-1341, 1394-1416`: `census_one` is currently run as `row=$(census_one "$repo")` inside an `if`. The status of that assignment is retained; `emit_census` maps 2 to whole-run exit 2 and every other nonzero to a `census failed ... (rc=...)` diagnostic plus exit 1. It buffers rows, emits no TSV until every repository succeeds, then emits one header and rows in `REPOS` order.
- `tools/souji-census.sh:546-585`: a protected hardlink/non-regular metadata finding exits 2; `info/attributes` is the special per-repository soft-failure case.
- `tools/souji-census.sh:1504-1516`: compare mode sets `CENSUS_TMP`, installs `trap cleanup_census_tmp EXIT`, redirects `emit_census` to that file, then loads it. A child that runs this EXIT handler can delete the parent’s comparison census before `load_census`.
- `tools/souji-census.sh:1613-1614`: selftest separately installs an EXIT cleanup for its fixture directory. The only trap registrations found are these EXIT traps; there is no current INT trap.
- `tools/souji-census.sh:1936-2012`: the current hardlinked-config control expects exit 2. However, `list_repos` calls `guard_git_surface` before adding the repo (`:1384-1386`), so a hardlink already present when scanning begins is rejected before the `census_one` command substitution. That control does **not** prove an asynchronous worker’s `wait` status of 2 is preserved.

## Findings / rewrite hazards and required assertions

Severity below is the consequence if the rewrite omits the assertion or corresponding handling.

### High — Do not lose protected exit 2 or convert it to a timeout / generic error

`protected_fail` uses `exit 2`, which exits the current shell. With the current `$(...)` call, the enclosing assignment returns 2 and `emit_census` observes it. In a background worker, the parent must get the worker PID’s final status via `wait`; `$!` itself is only the launch status. A bare `wait` under `set -e`, testing `if ! wait` and then reading `$?`, or recording `$?` after another command can all lose the original status. A signal status (e.g. 143/137) is not by itself proof that the watchdog timed out.

**Assertion:** add a deterministic fixture that lets `list_repos` pass its guard and then causes the worker’s later `guard_git_surface` to encounter protected metadata (for example, mutate the fixture between `list_repos` and the worker guard). Assert exit 2, the `path-protected` diagnostic, no `census failed` diagnostic, and empty stdout. Also force a worker wrapper to return a non-2 status after writing partial stdout; assert outer exit 1, exact `census failed for <repo> (rc=<N>)`, and empty stdout. Existing hardlinked-config control at `:2002-2012` is insufficient for this worker-status assertion because the hardlink is present before `list_repos` checks the repo.

**Smallest fix:** wait on the recorded worker PID in a status-preserving conditional, capture `$?` immediately, and keep the protected status distinct from watchdog-generated timeout state. Do not let `set -e` exit the parent before it classifies the result and cleans/reaps children.

### High — A timed-out worker must not leave a blocked process, watchdog, or held caller pipe

The current scan is synchronous. Enabling job control to give each worker its own process group changes signal delivery: a terminal INT reaches the foreground parent group, not necessarily the background worker group. The script currently has no INT/TERM handler that cancels worker groups. The watchdog must be a separate process/group, be canceled and reaped when a repo finishes early, and on timeout send TERM then KILL after the specified two-second grace. It must not retain caller stdout/stderr descriptors. A worker’s child processes must remain in the worker group for group termination to bound the operation.

**Assertion:** with fixture-only commands, cover both a fast worker and a git shim blocked in the FIFO open while ignoring TERM. Verify the fast scan returns without waiting for the configured timeout; the blocked scan returns after the timeout plus at most the two-second escalation allowance; the timeout row and other repo rows are present; and `ps`/`/proc` inspection of the test session shows no blocked worker descendants or watchdog afterward. Run the capture through a caller pipe and assert EOF is delivered promptly after the census exits. Send INT/TERM to the fixture parent during a blocked worker and assert it promptly terminates/reaps the worker and watchdog and removes temps. Assert worker PGID differs from parent/watchdog, while worker descendants targeted by the shim share the worker PGID; the signal must not hit the parent or a healthy neighbour.

**Smallest fix:** scope `set -m` to the worker fork, restore monitor mode immediately, install parent-side cleanup for active worker/watchdog PIDs and temp paths on INT/TERM/EXIT, and ensure the watchdog closes caller descriptors. Track/cancel/reap the watchdog on normal worker completion.

### High — Discard a killed worker’s partial stdout file; keep census stdout transactional

The present implementation accumulates rows and prints the header only after all repositories have succeeded. A file redirected from a worker may contain partial bytes if it is terminated. Treating any nonempty file as a row, or printing successful rows as jobs finish, can leak a fragment, duplicate a timeout row, reorder rows, or emit a partial TSV before a later protected refusal/non-timeout failure.

**Assertion:** make one fixture worker write a partial row then block; after timeout assert its bytes are absent and exactly one replacement row is emitted, byte-for-byte as `<repo>\t0\t0\t0\t0\t\terror\n`. Assert exactly one header and one row per repo, with all rows in `REPOS`/sorted order even when completion order is reversed. In separate cases, make a later worker exit 2 and exit non-2; assert stdout remains empty in both. For the FIFO timeout case assert exit 0, the exact `error` row, the `souji-census: repo-timeout <N>s <repo>` diagnostic once, and successful measurement of healthy neighbours.

**Smallest fix:** retain per-repo files only as private staging; on timeout or any nonzero worker result discard the entire file; synthesize the timeout row only for an actual watchdog timeout; collect/validate all results before printing header and rows in original sorted order.

### Medium — Preserve stderr content and deterministic ordering

Today repositories are processed serially in sorted order and each worker’s stderr is inherited by the caller. Concurrent jobs can reorder/interleave diagnostics, while redirecting stderr to staging can accidentally drop the protected finding or existing soft/status diagnostics. The timeout message must be emitted by the parent once, even if the worker is killed while writing stderr.

**Assertion:** create two repos that emit distinguishable diagnostics and arrange for them to complete in the opposite order from sorted repo order; assert stderr retains complete lines in the chosen contract order (preserve current sorted order if deterministic behavior is retained), has no merged/truncated line, contains each worker diagnostic once, and contains the timeout line once for the timed-out repo. Repeat the protected worker case and assert its original `path-protected` stderr survives staging and is not replaced by `repo-timeout` or `census failed`.

**Smallest fix:** stage worker stderr per repo and replay it in sorted order, or explicitly document and test a new order; write parent timeout/failure diagnostics separately and never synthesize them from an ambiguous signal status.

### Medium — Keep worker EXIT traps from deleting compare-mode `CENSUS_TMP`

Compare mode installs `trap cleanup_census_tmp EXIT` while `CENSUS_TMP` names the whole-census file. A background function/subshell can have copied that variable and may run the EXIT cleanup on its own exit; that would unlink the parent’s file before `load_census "$CENSUS_TMP" after`. This must be tested rather than assumed away. The selftest EXIT trap is another handler to consider if any worker is started in that shell.

**Assertion:** exercise `--compare` through a normal completed worker scan and through a protected worker refusal. For the successful scan assert comparison output/status is correct (including identical baseline → header-only/exit 0), `load_census` reads the still-existing whole-census temp, and the parent removes it at completion. For refusal assert exit 2 and cleanup still occurs. Also assert every per-repo temp is gone after success, failure, timeout, and interruption.

**Smallest fix:** prevent worker shells from running the parent’s EXIT handler (or clear `CENSUS_TMP`/the inherited EXIT trap in the worker only) while leaving the parent cleanup trap intact; track all per-repo temps in parent cleanup.

### Medium — Preserve the existing `set -e` call context and wait semantics

The function currently runs in the condition `if row=$(census_one ...)`; Bash errexit behavior inside a function invoked in a conditional differs from running `census_one ... &` as a standalone asynchronous command. A direct background invocation can therefore exit on an otherwise tolerated intermediate nonzero command rather than reaching the row/explicit status handling. With monitor mode enabled, wait semantics for stopped jobs also need care; waiting for a state change is not the same as waiting for termination.

**Assertion:** add a controlled worker-status fixture that exits nonzero after partial output and verify the exact parent mapping above; include a stopped/TERM-ignoring fixture and verify the parent does not treat a stopped job as completed and returns only after it is terminated. Exercise the actual wait call under `set -euo pipefail` and prove the parent still performs cleanup and status mapping.

**Smallest fix:** run the worker function in a wrapper that preserves the conditional/errexit context, captures its status, and exits with that exact status; wait for termination (not merely a stopped-state transition) and reap each PID exactly once.

### Medium — Do not race watchdog completion against a successful worker

A watchdog left sleeping until its deadline can delay an otherwise fast census, emit a false timeout, or signal a process group after the worker has completed. A generic worker SIGTERM must not be misclassified as a timeout; only a watchdog-confirmed timeout should produce the timeout placeholder.

**Assertion:** a fast worker with a very small-but-valid timeout completes normally with its measured row and no timeout diagnostic; a worker that exits with a signal status without the watchdog firing maps to the ordinary nonzero path; a blocked worker that the watchdog terminates maps to the timeout row. After each case assert both worker and watchdog are reaped and the parent did not signal a subsequent worker or unrelated group.

**Smallest fix:** use an explicit watchdog-fired state coordinated with worker completion, cancel and reap the watchdog on normal completion, and only classify the repo as timed out when that state records the watchdog’s action.

### Low — Validate timeout bounds without starting work

The new flag/env contract requires integer seconds 1..86400, default 600, and invalid input → usage exit 2. A parsing or arithmetic error under `set -e` can become exit 1 or start a worker before validation.

**Assertion:** cover default, 1, 86400, 0, 86401, negative, fractional, nonnumeric, and malformed/overflow input via both supported input paths. Invalid cases must exit 2 with usage diagnostics and no worker/watchdog/temp creation; accepted boundary values must parse without arithmetic overflow.

**Smallest fix:** validate the full decimal token and range before repo enumeration or temp/process creation; route invalid values through `usage_err`.

## Verification performed / gaps

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff -- tools/souji-census.sh` → no output (no source diff at review time).
- Read the exact source ranges cited above, including `:200-262`, `:539-593`, `:986-1027`, `:1127-1211`, `:1239-1427`, `:1487-1527`, `:1927-2023`, and `:2032-2072`.
- Literal trap inventory of `tools/souji-census.sh` found `trap cleanup_census_tmp EXIT` at 1511 and the selftest `trap 'rm -rf -- "$ST_TMP"' EXIT` at 1614; no INT trap occurrence. This inventory is not used as semantic proof; the behavior claims above are grounded in the source ranges.
- `read xd://lsp` → unavailable (`No such tool: xd://lsp`); no LSP server was available for status/references/definition/diagnostics.
- No census, selftest, build, lint, or runtime fixture was executed. The assignment did not authorize an `ALLOWED-EXEC` command, and this report is a static contract review. The watchdog/fixture assertions above remain verification gaps until exercised by the build owner.
- No tools installed or updated.
