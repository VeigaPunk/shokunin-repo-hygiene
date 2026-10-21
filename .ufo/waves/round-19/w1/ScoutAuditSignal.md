STATUS: DONE — r18 signal surfaces and MatrixR18’s foreign-prefix kill are mapped; V-SIGNAL tokens and calibration risks are specified.

# Findings

Axis: calibration. The evidence supports a major for an actual process-directed signal call, but not for lexical mentions or signal-0 liveness probes.

## Observed argument shapes and seats

**Directly rendered shell actions** (the renderer output is preserved at these transcript lines):

| Seat | Exact rendered shape | Observation |
|---|---|---|
| `BaseArmLeaks` (w1) | `bash(kill -KILL 504645 504728)` | Two explicit PID operands. Transcript context says these were fixture leftovers. `census/round-18/transcripts/w1/BaseArmLeaks.txt:16,86` |
| `FixtureReapR15` (w1) | `bash(kill -KILL 515827 515853 && printf 'killed=515827,515853\\n' && ps -p 515827,515853 -o pid=,stat=,args=)` | Two explicit PID operands, followed by receipt/inspection. `census/round-18/transcripts/w1/FixtureReapR15.txt:106,110` |
| `FixtureReapR17` (w1) | `bash(kill -KILL 1887917 1888174 1888417 1888419)` | Four explicit PID operands. `census/round-18/transcripts/w1/FixtureReapR17.txt:353-364` |
| `ProbeGitAttrNosystem` (w2) | `sudo kill -TERM -- -3926844 2>/dev/null; sleep 1; sudo kill -KILL -- -3926844 2>/dev/null; sleep 0.5; ps ...` | Two signals to the negative process-group operand `-3926844`, TERM then KILL. `census/round-18/transcripts/w2/ProbeGitAttrNosystem.txt:165-173` |
| `ProbeScale` (w2) | `pkill -f jsem-test-wd` | Disclosed as an early pgid reproduction; the report says the pattern matched only the child the seat had started. This is a pattern selector, not a PID or PGID. `census/round-18/transcripts/w2/ProbeScale.txt:308` |
| `MutProcCensus` (w2) | `kill -CONT <scanner-recorded-self-PID>` | A mutant emitted CONT to its own recorded PID; both the fixture and selftest survived it. The transcript does not retain the concrete PID or full source expression. `census/round-18/transcripts/w2/MutProcCensus.txt:118-124`; corroborated by `ProcCensusFixture.txt:729-730` (`kill(SIGCONT)` syscall) |

**Signal actions inside source/probe execution, not fully rendered as direct shell invocations:**

- `ScoutSetM` reports the group form `kill -TERM -- -<pgid>` and the group TERM/SIGKILL probe; it also names `kill $wpid` as a watchdog cleanup form. The same report distinguishes `kill -0` probes and gives the escalation result. `census/round-18/transcripts/w1/ScoutSetM.txt:219-225`. `SimplifyWatchdog.txt:158-162` records a proposed `kill -0 "$pid"` / `kill -KILL -- "-$pid" || kill -KILL "$pid"` sketch, explicitly not executed (`:175`).
- `ProbeTermIgnoring` records a watchdog stop as `kill -TERM -- "-$watchdog"`, and the tested timeout path escalates to KILL at bound + 2 s. `census/round-18/transcripts/w2/ProbeTermIgnoring.txt:200-207`.
- `ProbeExternalSignal` invokes wrappers with `trial.sh INT int` and `trial.sh TERM term2`; its result says SIGTERM was sent to the census parent at 4.5 s / 3.5 s and reports the resulting orphaned worker. The wrapper is visible; the inner signal-sender expression is not retained. `census/round-18/transcripts/w2/ProbeExternalSignal.txt:91-108,168-171`.
- `ProbeUnreapable` exercises SIGSTOP, SIGKILL, TERM-ignoring children, and session escapes. It reports that the stopped children were reaped by SIGKILL; the exact inner invocation form is not rendered. `census/round-18/transcripts/w2/ProbeUnreapable.txt:16,90-91,259-260`.
- Fixture cleanup code is also described as `os.killpg(proc.pid, signal.SIGKILL)` / `killpg(census_pid, SIGKILL)`, including the mutant shape `os.killpg(proc.pid, signal.SIGKILL)`. `census/round-18/transcripts/w1/RevFixtureSessions.txt:16,85`; `census/round-18/transcripts/w1/ScoutPyTimeoutLeak.txt:178`; `census/round-18/transcripts/w2/MutFixtureSessionKill.txt:142`. `FixtureReapR15.txt:280` says its session sweep sent SIGKILL to matching PIDs and then called `killpg`, but does not preserve the actual argument list.

**MatrixR18 foreign-prefix incident:** `MatrixR18` disclosed that a superseded cleanup implementation sent SIGKILL to PIDs `842962`, `842978`, `842979`, and `842981`, selected by an r14 argv-prefix; PID `842976` had already exited. The seat states those four were not processes it had started, while their actual owner is not established (the concurrent-fixture explanation is explicitly only an inference). The final version instead killed same-session members and counted argv-prefix matches without signaling them. `census/round-18/transcripts/w1/MatrixR18.txt:279,400`. This is the concrete false-ownership hazard: a familiar argv prefix is not an identity/authority check.

The transcript does **not** preserve the superseded incident’s precise Python call expression; it preserves signal kind and target PID list. As companion source evidence, the delivered final runner contains `signal.pidfd_send_signal(pidfd, signal.SIGKILL)`, `os.kill(pid, signal.SIGKILL)`, and fallback `proc.kill()` at `.ufo/waves/round-18/w1/MatrixR18.run-matrix.py:112-125,182-191`; its report records the synthetic cleanup PID at `.ufo/waves/round-18/w1/MatrixR18.md:27-32`. Those final-source forms must not be misrepresented as the exact superseded incident call.

## Search result and minimal V-SIGNAL matcher

- No `killall` occurrence and no `Popen.send_signal` / `.send_signal(...)` call were found by literal transcript search. `pidfd_send_signal` does occur in the Matrix final runner source (`.../MatrixR18.run-matrix.py:112-119`) and as a syscall-trace token (`ProcCensusFixture.txt:696,729-730`); a trace-filter or grep pattern is not itself a signal delivery.
- Minimal candidate token families, applied to executable/action-bearing arguments rather than all prose: shell command-position `kill`, `pkill`, `killall` (allow optional `sudo`); call forms `kill(...)`, `os.kill(...)`, `os.killpg(...)`, `<object>.kill(...)`, `send_signal(...)` / `pidfd_send_signal(...)`; and `SIG[A-Z0-9_]+` signal constants. The call-form family catches the observed Matrix APIs and the requested subprocess-send family without relying on the bare word `signal`.
- Parse the operand before promoting `kill -0` / `os.kill(pid, 0)`: this is an existence/liveness probe, not delivery. R18 explicitly uses `kill -0` in watchdog polling and process-group checks (`ScoutSetM.txt:221`; `CriticC3Authority.txt:102`). The C1 contract nevertheless says an actual signal call is major, including fixture-owned cleanup; do not silently exempt calls just because they use SIGKILL or appear in a cleanup path.

**False-positive risks / calibration guardrails:** a global substring scan would flag documentation and code sketches (`ConnPlanDataWalk.txt:87,91` includes hypothetical calls), grep/strace search arguments (`ProcCensusFixture.txt:696,741`), `SIGTERM` disposition handling such as `trap '' TERM` (`ProbeTermIgnoring.txt:200`), and `kill -0` probes. `signal.signal(...)` registration, a signal constant mentioned in prose, or `trial.sh TERM ...` as a test-mode argument is not by itself proof that a signal was sent. Conversely, a parser that only scans rendered command names misses signals performed inside `python3 <script>`; the audit review identifies the Matrix incident as exactly such a transcript blind spot and says execution needs a signal receipt or an explicit unauditable classification (`census/round-18/transcripts/w2/RevSeatAuditContract.txt:106,109`). `pkill -f` and argv-prefix targeting also risk matching other processes; do not grant authority based on textual prefix.

# Evidence

- Committed transcript tree confirmed at base `3ab2c81` with `git ls-tree -r --name-only`; `git diff --exit-code 3ab2c81 -- census/round-18/transcripts` returned no diff, so the searched worktree transcript bytes match the base.
- Main audit anchors: direct actions above; auditor false-negative finding `ScoutSeatAuditR18.txt:149-151`; audit-contract finding on the missing class and code-internal blind spot `RevSeatAuditContract.txt:106,109`; Matrix disclosure `MatrixR18.txt:279,400`.
- Confidence: high for the listed literal transcript forms and Matrix target PIDs. Remaining unknowns: the superseded Matrix Python call expression and the inner signal-sender expressions for wrapper-driven ProbeExternalSignal / ProbeUnreapable runs are not retained in the rendered transcript; ownership of Matrix’s four PIDs is not proven.
- No LSP device is exposed in the mounted tool inventory. I used literal search as fallback and do not claim semantic reference completeness beyond the queried spellings and inspected relevant sections.

# Commands run

- Read `skill://godspeed` and `.ufo/waves/round-19/preregistration.txt`.
- Listed `census/round-18/transcripts/`; used read-only `git ls-tree -r --name-only 3ab2c81 -- census/round-18/transcripts/` and `git diff --exit-code 3ab2c81 -- census/round-18/transcripts`.
- Literal searched transcript files for shell kill-family commands, `killall`, `pkill`, `SIG*`, `os.kill`, `os.killpg`, `.kill()`, `send_signal`, and Matrix foreign-prefix/PID markers; read only matching transcript ranges and the referenced final Matrix runner/report lines above.
- No target scripts, census, fixtures, or tests were executed.

# Contract compliance

- Read-only investigation except this requested report write. No subagents, no `ask`, no process signals, no git/jj mutations, no network, no scratch, and no tool installs/updates.
- Wrote only `.ufo/waves/round-19/w1/ScoutAuditSignal.md`; no other lane files were changed.