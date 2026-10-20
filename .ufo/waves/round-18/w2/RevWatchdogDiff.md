STATUS: DONE — Static operability review complete; two timeout-boundary gaps found.

# Axes
- Operability: repository discovery must not block outside `--repo-timeout`; interrupted invocations must not orphan bounded workers.
- Contract: protected refusals remain exit 2, while timeout failures remain row-level errors and other repositories continue.

# Attacked claim
C1 operability, limited to `tools/souji-census.sh`: watchdog/list-phase bounding, timeout and protected-refusal exit behavior, stderr/temp lifecycle, process-group scope, option parsing, and selftest coverage.

# Findings (severity order)

## P2 — Repository discovery does filesystem work before any watchdog exists

**Evidence:** `list_repos` performs the root glob and directory/type probes at `tools/souji-census.sh:1407-1433`, including `[ -L "$d" ] || [ ! -d "$d" ]` at 1418 and `.git` probes at 1421-1431. `emit_census` calls `list_repos "$root"` at 1660 and only then prepares the temp directory at 1661 and begins watchdog-wrapped candidate guards at 1665-1671. Thus root readdir/glob expansion and these `stat`-backed path tests are outside `run_repo_with_watchdog` and outside the configured timeout. A stalled network/FUSE path lookup while enumerating or classifying a repo can hold the whole census indefinitely, even with `--repo-timeout 1`.

**Verdict:** Fails the bounded-list-phase claim for discovery/type-classification path operations. This is not evidence that ordinary repository content is read there; the issue is that preflight filesystem operations can themselves block before the guard worker is started.

**Smallest fix:** Put root enumeration and each candidate's filesystem classification behind bounded worker execution (and ensure a failed/hung discovery produces a clear setup/census failure rather than proceeding with incomplete inventory); alternatively, explicitly narrow the timeout contract to exclude discovery and document the remaining unbounded path operations.

## P2 — Exiting the parent can remove the watchdog's arbitration state and strand the worker

**Evidence:** `prepare_census_tmp` installs only `trap cleanup_census_tmp EXIT` at `tools/souji-census.sh:238-242`; cleanup recursively removes the directory at 232-235. `run_repo_with_watchdog` creates its arbitration path inside that directory at 1474-1475, starts the worker as a separate job-control process group at 1478-1481, and starts a watchdog in its own session at 1482-1502. At timeout the watchdog only signals the worker if `mkdir "$state_path"` succeeds (1492-1498). If the parent receives a terminating signal and exits, EXIT cleanup can remove the state directory while both worker and watchdog are isolated from the parent's process group. When the watchdog reaches the deadline, its `mkdir` then fails and the code has no alternate signal path; the repository worker can continue after the caller has exited, instead of being timed out/reaped.

**Verdict:** Fails bounded worker lifecycle on parent cancellation. Normal completion's explicit watchdog teardown and normal timeout handling do not cover this exit path.

**Smallest fix:** Keep active worker/watchdog process-group IDs and, on parent termination/EXIT, signal and reap those groups before deleting their state directory; do not remove the watchdog's arbitration state while an active worker depends on it.

# Other scoped checks
- Normal return paths preserve the intended distinction in the inspected code: a worker rc 2 is returned as 2 (`tools/souji-census.sh:1645-1647`), timeout returns 124 (`1649`), and `emit_census` maps rc 2 to whole-run exit 2 while a timed-out repo gets the exact placeholder row and continues (`1673-1685`, `1702-1715`). The timeout diagnostic is emitted as `souji-census: repo-timeout ${REPO_TIMEOUT}s <repo>` in both phases (1677-1679, 1706-1708); an unreaped worker adds the separate diagnostic at 1640-1642.
- Temporary census output is created under `/var/tmp` and normally removed through the EXIT cleanup; compare also cleans and clears its trap on the success path (`1817-1823`). The cancellation finding above is specifically about cleanup racing an active watchdog/worker.
- The parser rejects nondigits and range values outside 1..86400 after leading-zero normalization (`245-257`); CLI options are parsed and validated before dispatch (`2581-2603`). The new selftest exercises a timed-out FIFO-backed status call, a normal slow Git case, a protected refusal, and invalid bounds (`2320-2578`); it does not cover pre-discovery hangs or parent cancellation.
- Process-group setup is intended to put the worker in its own group (`1478-1481`) and the watchdog in a separate session (`1482`); I found no basis in this static review to claim the ordinary worker launch loses that group assignment.

# Review evidence and verification gaps
- LSP was not available: `read xd://lsp` returned `No such tool: xd://lsp`. Therefore no LSP status/references/definition/diagnostics were available; source reads supplied the line evidence. Literal grep was used only to locate anchors, not as semantic proof.
- Read-only diff command: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tools/souji-census.sh` reported `tools/souji-census.sh | 631 +++++++++++++++++++++++-` and `1 file changed, 592 insertions(+), 39 deletions(-)`; reviewed the patch content.
- Static source inspected at `tools/souji-census.sh:232-257`, `1386-1723`, `1811-1823`, and `2320-2603`.
- No runtime/selftest/build/lint checks were run: assignment scope was static review only, and no `ALLOWED-EXEC` authorization was provided.
