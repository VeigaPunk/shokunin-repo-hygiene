STATUS: DONE — static review of C1 watchdog risks and current Git execution guards

Axis: operability.

## Verdict

**Partial / conditional.** The inspected baseline `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` has no per-repository watchdog yet: `emit_census` processes `census_one` synchronously, captures its row, and only then advances (`tools/souji-census.sh:1394-1416`). The proposed process-group design can address the FIFO hang, but `kill -TERM -- "-$pid"` is safe only with strict identity and lifetime control. A process group is not a process-tree sandbox: an executable that calls `setsid()` escapes it.

The two explicitly named Git execution paths are already guarded in the inspected source: `core.fsmonitor` is overridden to false for all Git calls and again on status; bound filter drivers make status skip and report `status-unverifiable` instead of running them (`tools/souji-census.sh:163-185,1063-1134`). This is static source evidence, not a dynamic test. Keep that no-repo-code-execution property as a prerequisite for the group-kill claim.

## Findings

### F1 — HIGH if the signal target is not validated and anchored: zero/stale PGID can signal outside the repo job

**Exploit path.** For `kill -TERM -- "-$pid"`, `$pid=0` produces a zero target and signals the caller's current process group; `$pid=1` produces target `-1`, the broadcast target for processes the caller may signal. An empty `$!` does not itself necessarily become zero when interpolated, but fallbacks, arithmetic conversion, stale-variable reuse, or unvalidated input can produce either dangerous value. Separately, after the job's process group disappears, the kernel can reuse its numeric PGID before a delayed TERM/KILL; the watchdog can then signal an unrelated group. `kill -0` or a `/proc` check followed by `kill` is a TOCTOU check, not an identity guarantee.

**Evidence.** The existing loop has no PID/PGID lifecycle machinery (`tools/souji-census.sh:1394-1416`); no watchdog markers were found in the targeted source at the baseline. The new `kill` expression is proposed by C1, not present in that baseline.

**Impact.** A malformed target can terminate the census caller or other same-UID processes; a stale target can kill unrelated work or fail to kill the blocked Git process. With monitor mode disabled, a valid background PID is not its PGID: `kill -- -$pid` will normally miss the worker (it does not inherently target the caller for a positive PID), so a timeout can leave the hang in place.

**Smallest remediation.** Clear the PID variable before each fork; accept only the exact positive-decimal `$!` from that fork (`^[1-9][0-9]*$`), never default or coerce it, and verify that the worker's PGID equals that PID and differs from the caller's PGID before any group signal. If `set -m` did not establish that invariant, fail closed without signaling. Keep a worker-group anchor/sentinel alive until the watchdog is canceled and reaped on success, or through the TERM-to-KILL grace period on timeout; otherwise PGID reuse remains possible between the two signals. Do not treat `kill -0` alone as proof of identity. Ensure the watchdog is outside the worker group so TERM to the worker cannot kill the escalation logic.

### F2 — MEDIUM: cancellation and inherited descriptors can leave a watchdog/fixture behind

**Exploit path.** Any normal return, exit-2 protected refusal, setup failure, or signal to the census can bypass the happy-path timer cleanup. A watchdog shell that runs `sleep; kill ...` may leave its `sleep` child behind if only the shell PID is killed. A watchdog or worker descendant that inherits caller stdout/stderr can also keep the caller's pipe open after the census exits. Existing fixture runners protect their own invocation by creating a session and killing that session on outer timeout, but that is harness containment, not proof that a production census watchdog is reaped (`census/round-17/run-matrix.py:89-108`; `tests/fixtures/r17-census-hygiene.py:291-321`).

**Impact.** A completed census can still leave a timer or blocked descendant; a late watchdog can signal a stale PGID, and inherited pipes can make a supervising caller appear hung even after its main process exits.

**Smallest remediation.** Use one cleanup path covering success, worker failure/refusal, timeout and INT/TERM; cancel and `wait` every watchdog before returning, and always reap the worker. If a shell watchdog has subprocesses, kill/reap its entire separately owned group (or use a single exec'ed timer process); never assume killing the shell PID kills its `sleep`. Redirect watchdog stdout/stderr to `/dev/null`; spool worker stdout and stderr to private files and relay them after the worker is reaped, so descendants cannot retain caller pipes. Keep TERM then KILL escalation tied to the worker group's anchored lifetime.

### F3 — MEDIUM residual / current guard holds statically: `setsid()` defeats process-group containment

**Exploit path.** A repo-controlled filter or fsmonitor executable can call `setsid()` and continue blocking in a new session after the census sends TERM/KILL to the worker PGID. Process-group signaling cannot reach it after the session change.

**Evidence.** The current source explicitly forces `core.fsmonitor=false` globally (`tools/souji-census.sh:179-185`) and for status (`:1122-1129`). `guard_bound_filters` checks tracked-path attributes and skips status with `status-skipped: filter-driver-bound` on a bound/unknown filter (`:1063-1114`). The config scanner also describes these hooks/fsmonitor paths as inert (`:757-766`). Therefore these named paths appear neutralized in the inspected implementation; no dynamic execution test was authorized or run. This does not establish that all future Git features or other repo-controlled execution routes are impossible.

**Impact.** If any path starts executing repository-supplied commands, a process-group timeout no longer proves “no fixture process left behind”; the escaped child may keep running and hold resources/descriptors.

**Smallest remediation.** Preserve and test the current fail-closed filter check and forced fsmonitor override. Add an isolated `/var/tmp` fixture with a bound filter whose command would `setsid` and block, plus an fsmonitor command that would create a marker; require status to be skipped for the bound filter and require neither marker nor child to appear for fsmonitor. Run every arm with the test runner's session/process-group cleanup so a failing arm itself cannot orphan a process. If future requirements allow arbitrary repository-controlled executables, replace the process-group-only guarantee with an OS containment boundary (for example, a per-run cgroup); do not claim `kill -- -$pid` contains `setsid` descendants.

## Concrete acceptance tests (proposed; not run)

1. **PID/PGID guard:** exercise unset, empty, `0`, `1`, negative, non-decimal and stale worker-ID inputs through the watchdog helper with a signal-recording test seam. Assert no signal is issued for invalid identity, caller/neighbor markers remain untouched, and the helper fails closed. For the real fork path, assert `pid > 0`, worker `PGID == pid`, and worker `PGID != caller PGID` before timeout signaling.
2. **Job-control failure:** force the worker launch with monitor mode disabled (or simulate launch failure); assert the timeout path reports supervisor setup failure and does not signal any group or leave the blocked worker running. In the normal case, prove the worker's process group is separate and that the caller survives timeout.
3. **Fast-completion/deadline race and PGID lifetime:** use a barrier to make a fast worker finish as the deadline fires. Assert the timer is canceled/reaped before the row is accepted or the next repo starts; assert the group anchor remains alive until the timer is reaped, and no signal occurs after that anchor exits. Stress the boundary repeatedly; a `kill -0`-only implementation is not sufficient.
4. **Cleanup paths:** separately exercise clean return, worker nonzero, protected refusal/exit 2, timeout and parent INT/TERM. Before each census invocation returns, verify all worker, watchdog and timer PIDs are reaped/gone, no process in the worker/watchdog groups remains, and captured stdout/stderr reaches EOF. On timeout, require TERM then KILL after at most 2 seconds and retain healthy-neighbor rows.
5. **Escaping child limitation:** in an isolated harness only, run a helper that forks then `setsid()` and blocks; demonstrate that worker-PGID kill alone does not kill it. Either require the production reachable-command set to prevent that helper from executing (the current filter/fsmonitor guards) or adopt stronger containment before claiming no residuals.
6. **Git execution guards:** for a repo-local `core.fsmonitor` command with a marker and a bound tracked-path filter driver that would `setsid`, assert fsmonitor marker absence and filter `status-skipped`/`status-unverifiable`, with no child remaining. Also retain a benign repo control to show the rest of the census continues.

## Evidence and checks

Static reads: `tools/souji-census.sh:163-185,757-766,1063-1134,1394-1416`; `census/round-17/run-matrix.py:89-108`; `tests/fixtures/r17-census-hygiene.py:271-321`. No tests, census runs, or subprocess experiments were executed; the assignment supplied no `ALLOWED-EXEC` authorization. No tools were installed.

Commands executed (read-only):

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short -- tools/souji-census.sh
=> b5763415cc67ecff1e8fe56c58c39a6fb106d7a3
=> status emitted no lines

stat -c '%A %a %n' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-census-hygiene.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-17/run-matrix.py
=> -rwxr-xr-x 755 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
=> -rwxr-xr-x 755 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-census-hygiene.py
=> -rwxr-xr-x 755 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-17/run-matrix.py

git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -E 'repo-timeout|process.group|process group|set -m|kill .*--.*-\$|watchdog|repo timeout' b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-census.sh tests/fixtures/r17-census-hygiene.py census/round-17/run-matrix.py
=> no watchdog implementation marker in tools/souji-census.sh; matches were fixture/round-17 process-group timeout comments and unrelated .ufo/watchdog references. Full tool output included those exact-revision matches.

git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -E 'GIT_CONFIG_COUNT|GIT_CONFIG_KEY_[01]|core\.fsmonitor|core\.hooksPath|guard_bound_filters|filter-driver-bound|status-skipped|check-attr' b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-census.sh
=> tools/souji-census.sh:128:   binds to a tracked path (stderr `status-skipped`; the driver never
=> tools/souji-census.sh:131:   Accepted: any core.hooksPath/core.fsmonitor value (every census git
=> tools/souji-census.sh:132:   call carries core.fsmonitor=false and core.hooksPath=/dev/null via
=> tools/souji-census.sh:133:   GIT_CONFIG_COUNT; status also passes them with -c), boundary-clean
=> tools/souji-census.sh:182: repository's core.fsmonitor command.
=> tools/souji-census.sh:184:export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false
=> tools/souji-census.sh:185:export GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null
=> tools/souji-census.sh:757:      # Inert for the census, any value: core.hooksPath (status writes no
=> tools/souji-census.sh:758:      # index, and carries -c core.hooksPath=/dev/null) and core.fsmonitor
=> tools/souji-census.sh:759:      # (status carries -c core.fsmonitor=false, which alone disables the
=> tools/souji-census.sh:1065:# Neither ls-files nor check-attr runs a driver.
=> tools/souji-census.sh:1066:guard_bound_filters() { # $1 worktree, $2 effective attributes file; rc 1 bound or unknown
=> tools/souji-census.sh:1085:  mapfile -d '' -t recs < <(set -o pipefail; git -C "$wt" -c core.attributesFile="$attrs" \
=> tools/souji-census.sh:1091:      check-attr -z --stdin filter 2>/dev/null)
=> tools/souji-census.sh:1110:  if ! guard_bound_filters "$1" "$at"; then
=> tools/souji-census.sh:1111:    printf 'souji-census: status-skipped: filter-driver-bound (%s)\n' \
=> tools/souji-census.sh:1122:  if ! st=$(git -C "$1" --no-optional-locks -c core.fsmonitor=false \
=> tools/souji-census.sh:1123:      -c core.hooksPath=/dev/null -c core.excludesFile="$ex" \
```

A broader exact-revision `git grep` over `tools/souji-census.sh tests census/round-17` was also used to locate process-group fixture evidence; the tool elided the long output. Its relevant matches are cited above.