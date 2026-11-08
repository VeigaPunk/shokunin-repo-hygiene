# Gate signal handling — why a killed shell script leaves its `timeout` children running

source: S325, S326, S328, S075, S329
round: 79, 80, 81
status: mined (lane-verified on this host, bash 5.3.20, coreutils 9.12)

## Claim

A bash script that runs its children as `timeout <s> cmd` cannot be stopped cleanly by a caller's TERM, INT or
HUP unless it is built for it: the shell dies (or ignores the signal) and the child keeps running in a process
group the caller never signalled, for up to the timeout.

## Why

- `timeout` puts itself and the command into a new process group before it forks: "Ensure we're in our own
  group so all subprocesses can be killed." (`if (!foreground) setpgid (0, 0);`, S326, timeout.c main() at
  v9.12). A signal to the script's pid, or to the script's own group, does not reach that group.
- With no trap, TERM and HUP kill the shell outright; the child is orphaned (r79 K-a: 10 of 10 signal rows
  leave the blocked child alive, `census/round-79/controls/c1-K-a-do-nothing.txt`).
- With a trap, bash still cannot act while it waits for a foreground command — `$(...)`, `<(...)` or a plain
  command: "it will not execute the trap until the command completes" (S325, Signals). A trap-only gate
  therefore stays blocked as long as the child does (r79 K-b, `census/round-79/controls/c1-K-b-trap-only.txt`).
- Only `wait` on an asynchronous command returns at once on a trapped signal (S325, same node), so the
  pattern is: start each child with `&`, record `$!`, `wait` on it, and in the trap kill the child's group
  (`kill -KILL -- -<pid>`: timeout made the child pid its group id) and the child itself, then clean up and
  exit 128 + the signal number. Output goes to a private file, since `$(...)` is itself a foreground wait.
- Killing is the part that matters: a gate that traps and exits but kills nothing still orphans the child (r79
  K-c, `census/round-79/controls/c1-K-c-no-kill.txt`). Which kill is enough depends on depth: timeout's own child
  is also covered by `prctl (PR_SET_PDEATHSIG, term_signal)` (S326, lines 608-610), so killing timeout alone ends
  it, and a trap that kills only the pid scores 11/11 on the r79 rows (S79MutGate M01/M02, S79CriticClaims); a
  grandchild (git's own helpers, a shell that forks) is reached only by the group kill, and no r79 row tests
  that (routed to round 80).

## A launch trap for whoever measures this

A process started with `&` by a non-interactive shell starts with SIGINT and SIGQUIT ignored (S325: "When job
control is not in effect, asynchronous commands ignore ‘SIGINT’ and ‘SIGQUIT’"), the ignore survives exec,
and bash cannot trap a signal that was ignored on entry (S325, node Bourne Shell Builtins: "signals ignored upon
entry to a non-interactive shell cannot be trapped or reset"). `timeout` does not forward a signal whose
disposition it inherited as ignored either (S326 `sig_needs_handling`, lines 422-433; S79ScoutSources F3). A signal-sending counter launched with `&` therefore
hands every gate it starts an untrappable INT, and every INT row reads as a gate failure
(`census/round-79/probes/sigint-inherit.sh`, `census/round-79/records/foreground/sigint-inherit.txt`). Such a
counter must reset the dispositions it passes on (Python: `signal.signal(signal.SIGINT, signal.SIG_DFL)` in
the child before exec) or be run in the foreground; the lesson of round 79 records the misdiagnosis this
caused.

## What the r79 gate guarantees, and its limits

- Every git, find, head and python child of `tools/souji-pre-report-gate.sh` runs through `gate_run`; on TERM,
  INT or HUP the gate kills the running child's group, removes its scratch dir, prints `check-signal=FAIL` and
  `RECEIPT-GATE-SIGNALED`, and exits 128 + n (`census/round-79/records/foreground/c1-at-W1-fg-run1.txt`).
- Not covered: SIGKILL (untrappable); a child that leaves timeout's group (`setsid`, a double fork), and a
  grandchild left behind by a child that already finished (S79ExecEvade MEDIUM-1: the trap targets only the
  running child's group); a signal ignored on entry; the few milliseconds of the short `$(...)` forks that remain (realpath, dirname, awk,
  mktemp), during which the trap waits for the fork to end.

## A session front for tools that capture children in `$(...)` (r80, `tools/souji-quarantine.sh`)

- The r79 pattern (every child an asynchronous job the shell `wait`s on) fits a gate with a handful of call sites.
  `tools/souji-quarantine.sh` captures its bounded children (receipt engine 120 s, file digest 120 s, special scan
  60 s, directory digest 300 s, staging mv 60 s) in `$(...)`, often inside functions that are themselves called in
  `$(...)`: rewriting every depth is a large change, and a trap in the outer shell still waits for the innermost
  substitution. At base a TERM or HUP to the tool's pid killed the shell and left timeout's group running; after an
  INT the tool was still running at the 5 s settle (K-a INT rows `exited=n`; S325 says why) (`census/round-80/controls/c2-K-a-do-nothing.txt`: 12 of 12 signal rows orphaned).
- r80 splits the tool in two processes instead. The front shell starts the worker — the same file — as
  `setsid "$BASH" "$SELF" "$@" <&0 &` and only `wait`s on it. A background job of a non-interactive shell is not
  a process-group leader, so setsid execs in place ("The command calls fork(2) if already a process group leader.
  Otherwise, it executes a program in the current process.", S328): `$!` is the new session's id, and every descendant that does
  not call setsid itself stays in that session, timeout's new groups included (S326 changes the group, not the
  session). The worker refuses to run if it is not its own session leader.
- On TERM/INT/HUP the front's trap fires at once (it is in `wait`, S325) and scans `/proc/*/stat` for field 6, the
  session id (S075, which supersedes S068), after the last `) ` (the comm field may hold spaces and parentheses; the whole file is read, because a comm may also hold a newline —
  S80ScoutSources MEDIUM-3, repaired at R3 `4a499e9a`), with no fork per process;
  it SIGSTOPs every member (so none can fork during the kill) and SIGKILLs them, repeating the scan; after 8 kill
  passes a ninth scan that still lists a member makes the front print a stderr note (the SIGNAL line is not proof
  of a kill — the survivor census is; S80Scribe MEDIUM-2), then it removes the worker's private TMPDIR (the worker's own scratch, selftest fixtures and error files live
  there), prints `SIGNAL<TAB>SIG<name><TAB>RECEIPT-QUARANTINE-SIGNALED` and exits 128 + n. A first draft that
  forked a `$(...)` per /proc entry took more than the 5 s settle on 9 of 15 rows
  (`census/round-80/records/prefreeze-feasibility.txt`).
- Measured (`census/round-80/records/c2-after.txt`): 15 rows, 0 mismatches, 0 orphans; a trap-only tool and a front
  that kills only the worker pid both stay at 12 orphan rows (`controls/c2-K-b-trap-only.txt`,
  `controls/c2-K-c-no-session-kill.txt`) — killing the worker leaves its `$(...)` subshells and timeout groups.
- The precondition is real and the wave broke it (S80CriticDiscern F1 HIGH, S80CriticClaims, S80Sentinel F1): with
  job control on in the tool's shell (an exported `SHELLOPTS=monitor`, `bash -m`), the job IS a group leader,
  setsid forks, `$!` is setsid's exiting parent, `wait` returns 0 at once and the worker dies on its deleted TMPDIR
  — the tool exited 0 with no verdict. Repaired after the wave (R `8ba93218`): the front runs `set +m` before the
  launch, the worker refuses unless it leads its own session AND its parent is the front, a nested call runs
  inline only when the session leader's argv names the tool (a caller exporting `SOUJI_Q_SESSION` skipped the
  front), and signals after the worker ended are ignored; R2 `97289f81` sweeps the session when the worker itself
  died by a signal (S80Sentinel F3). Probes `census/round-80/probes/front-launch-modes.py` and
  `front-worker-death.py` fail on the earlier bytes (`census/round-80/records/repair/*-at-W2.txt`, `*-at-R.txt`).
- Limits: SIGKILL to the front (the worker session then runs on; S80Sentinel F2); a descendant that calls setsid
  itself (a double fork or setpgid stays in the session and is killed, S80ExecEvade); a signal in the instant between
  the launch and `$!`; a SIGINT the caller ignored before starting the tool (S325, above); the stage-2 move and
  later stages of a non-dry-run invocation (a signal there leaves the source moved with no RESULT line,
  S80ExecEvade F3) use the same mechanism but no row measures them.

## An asynchronous job for one bounded external call (r81, `tools/souji-vault-verify.sh`)

- When a tool has ONE bounded child that can block for long — here the advisory Obsidian CLI call
  `timeout "$CLI_TIMEOUT" "$bin" vault:hash "$vp"`, run inside `out=$(...)` inside `claim=$(cli_claim ...)` —
  the r80 session front is more than the fix needs. At base a TERM or HUP to the tool's pid killed the shell and
  left the substitution subshell, timeout and the CLI running; the same signal to the tool's whole process group
  still left timeout's own group (S326); INT waited for the CLI (S325)
  (`census/round-81/controls/c2-K-a-do-nothing.txt`: 8 of 8 signal rows orphaned at `SOUJI_CLI_TIMEOUT=300`).
- r81 runs that one call as an asynchronous job whose output goes to a private `mktemp` file, and the shell `wait`s
  on it with TERM/INT/HUP trapped only for the duration of the call. The trap kills timeout's group (`kill --
  -$pid`, falling back to the pid when the group is not set up yet), gives it up to 2 s, sends KILL, removes the
  file, writes `souji-vault-verify: SIG<name> ...` on stderr and exits 128 + n. The result comes back through a
  global (`CLI_CLAIM`), because a function called in `$(...)` runs in a subshell the trap cannot reach.
- The job's stdin must be named: "the standard input for asynchronous commands, in the absence of any explicit
  redirections, is redirected from ‘/dev/null’" (S329, bash Lists of Commands, decompressed lines 758-760). The
  foreground `$(timeout …)` inherited the caller's stdin; a job without `<&0` silently gave the CLI /dev/null
  (`census/round-81/controls/c2-K-c-no-stdin.txt`: p3, a stdin-reading CLI, answers `cli=empty` instead of
  `cli=agree`).
- timeout forwards a signal it receives to its own group (S326, cleanup()), so killing timeout's pid alone already
  ends the CLI in every measured row (`census/round-81/records/prefreeze/c2-pid-only-kill-draft.txt`, 12/0); the group
  kill is kept for a signal that lands before timeout has installed its handlers and for a CLI that ignores TERM,
  which no row measures.
- Measured (`census/round-81/records/c2-after.txt`): 12 rows, 0 mismatches, 0 orphans, pid and group delivery, a
  CLI that forks a grandchild, and four no-signal rows (agree, bounded timeout, stdin, `--fallback`); a trap-only
  tool stays at 8 orphan rows (`controls/c2-K-b-trap-only.txt`).
- Limits: SIGKILL to the tool; a CLI descendant that leaves timeout's group, by itself or because job control put
  it in a group of its own (an exported `SHELLOPTS=monitor` reaches a bash CLI: v7/v8 leave one survivor each,
  `census/round-81/records/launch/c2-at-W2-monitor.txt`, where the base leaves 3-5); a SIGINT ignored on entry
  (S325); signals while the tool runs its other short children (sha256sum, git, find) wait for that child; if no
  private file can be made the call runs in the foreground as before.

- A file the job writes must keep the tool's own write rails. At W2 the private file went to `${TMPDIR:-/tmp}`,
  so a caller whose TMPDIR sat inside a vault made the tool write under the vault during the call (S81Sentinel
  LOW-1; probe `census/round-81/probes/tmpdir-in-vault.py` fails 3 of 4 arms at W2). Repair R `ef76a14f`: the
  asynchronous path runs only when TMPDIR and every vault directory (the row's, the `--vault` hint) are disjoint;
  otherwise the call runs in the foreground as before (`census/round-81/records/repair/`, 4/4, counter still 12/0).

## A descendant-tree kill for a job-controlled grandchild (r82, `tools/souji-vault-verify.sh`)

- With job control in the tool's environment (an exported `SHELLOPTS=monitor`), the CLI's own `sleep 600 &` starts in a
  process group of its own, outside timeout's group, and the r81 trap's group kill misses it: 4 orphan rows under the
  monitor launch (`census/round-82/controls/c2-K-a-do-nothing.txt` under `env SHELLOPTS=monitor`: v7/v8 + m1/m2
  `survivors=1`, `mismatches=4`) while the Base tool passes the default launch (16/16,
  `records/prefreeze/c2-base-default.txt`).
- r82 kills the whole CLI subtree first: `cli_kill_tree` snapshots `pgrep -P` recursion from the timeout pid and
  sends TERM then KILL to each pgrep descendant, before the group kill and the KILL fallback. Measured 16/16 under
  both launches (`census/round-82/records/c2-after.txt`, `c2-after-monitor.txt`), the private file never under a
  vault path (probe D successor: 6/6 arms, `records/probe-d-successor.txt`).
- **The monitor matrix is the counter's two launches, not the row labels.** The counter's `rid.startswith("m-")`
  test (`census/round-82/c2-vault-signal-counter.py:217`) never matches the ids `m1-monitor-term-fork` /
  `m2-monitor-hup-fork`, so those rows carry no monitor of their own; the launch that puts job control into every
  row's tool environment is `env SHELLOPTS=monitor python3 …`, inherited at `:216` (S82MutTool MEDIUM).
- **A handler that reads a pid from a variable must not narrow the variable's fallback.** W2 replaced the base's
  `local pid=${CLI_PID:-${!:-}}` with `local pid=${CLI_PID:-}`, and the window between `timeout … &` and
  `CLI_PID=$!` (4.07 ms on the real tool) then ran the handler with an empty pid: it printed
  `souji-vault-verify: SIG<name> … stopped it, no verdict` and exited 143 with the CLI subtree still alive
  (A/B 150 iterations: base 0 orphans, W2 1). `$!` *is* the timeout pid there — `:290` is the tool's only
  background launch — so the base fallback was correct exactly where it mattered. Repair R1 restored it and the
  frozen 16 rows, the selftest, the r17 fixture and probe D re-pass on the repaired bytes
  (`census/round-82/records/repair-w3/`; S82Sentinel F-1).
- Limits unchanged from the r81 section (SIGKILL, a CLI descendant re-parented beyond pgrep's tree, a SIGINT
  ignored on entry, signals while the tool runs its other short children, the foreground fallback path). Added by
  the r82 wave: the walk forks one `pgrep -P` per tree node and each scans all of `/proc` (≥12 descendants exceeds
  the counter's 5 s settle), the snapshot→KILL gap reaches 6.11 s so a recycled pid in the snapshot can be KILLed,
  `pgrep` is called unguarded (a `pgrep` that fails degrades silently to the group kill), and with no caller
  `TMPDIR` the private CLI file lands in shared `/var/tmp` (S82Sentinel F-2/F-3/F-4/F-5, S82Connector2 F3).

## A one-pass descendant walk for the vault CLI's signal path (r83)

source: S332 (kernel fs/proc/array.c v6.17), S075, S326; census/round-83/c2-tree-walk-counter.py
verified-at: 9994af61565ec87913152cf1102c61ac9a75b04d (2026-11-08)
recheck: python3 -B census/round-83/c2-tree-walk-counter.py --tool tools/souji-vault-verify.sh --work <empty dir outside /tmp>

- **The r82 walk was O(nodes × all processes).** `cli_kill_tree` forked one `pgrep -P` per tree node, each a full
  `/proc` scan (0.53–2.15 s per call at 4–7 k processes): signal→exit was 5.74 s at 12 descendants and 9.64 s at
  24, past the counter's 5 s settle (S82Sentinel F-2). The snapshot-then-TERM-then-KILL shape also left a
  snapshot→KILL gap up to 6.11 s, so a recycled pid could be KILLed (F-3).
- **One fork-free pass builds the map.** Read every `/proc/<pid>/stat` with the `read` builtin, take the substring
  after the LAST `)` (comm is emitted inside parentheses and may itself contain `)` and spaces, S332 lines
  590–594), then field 2 of the remainder is ppid and field 20 is starttime (S332 line 612). No external command
  runs inside the pass; the reverse map `ppid → " pid pid …"` is built in the same pass.
- **Kill as discovered, re-checking identity.** A DFS from the timeout pid signals each descendant the moment it is
  found, re-reading that pid's starttime before the TERM and again before the KILL sweep, so a reused pid is not
  signalled. Measured: `rows=20 mismatches=0 errors=0 orphans=0` (deep rows 0.3–0.4 s at 12 and 24 descendants,
  default and monitor launches; `census/round-83/records/c2-after.txt`), 0 `pgrep` invocations against 108 for the
  r82 tool on the same population (`census/round-83/records/c2-before-pgrep.txt`), selftest 57/0, r17 37/0, probe D
  4/4.
- **Shell trap that cost a draft: `$20` is `${2}` + `0`.** The first draft compared `[ "$20" = … ]`; the positional
  parameter is two digits, so that reads field 2 (ppid) with a literal `0` appended. The guard silently became a
  "the parent did not change" test; when the DFS killed the parent first, every child was re-parented and the
  re-read mismatched, so 7–20 of 24 children were skipped while the tool printed "stopped it, no verdict". Write
  `${20}` for any positional above 9, and assert the field's meaning on one known pid before trusting the guard.
- **Settle is host-dependent; the fork count is not.** On the same bytes the r82 walk took 2.5 s at 12 descendants
  on an idle host (passing) and > 5 s at 24, while on a loaded host (load1 ≈ 250) it failed all four deep rows —
  so a claim about a signal path states the descendant count, the settle AND the load, and uses the per-node fork
  count as the load-independent discriminator.
- Limits: `/proc` reads are not atomic (one read-then-signal window per pid remains), pidfd is not used (bash
  only), a descendant that creates children after the pass reads the map is missed, the deep stub is a flat
  fan-out, and a `pgrep` invoked by absolute path would bypass the probe shim. The stat path emits comm unescaped
  (S332, `proc_task_name(..., false)`), so a comm containing a newline splits the file: the first-line `read`
  yields fewer than 20 fields, the arity guard skips that pid and its children — safe (nothing is signalled) but a
  way for a hostile CLI to keep a descendant out of the map; and the tool runs `set -euo pipefail`, so every parse
  must be arity-guarded (`[ "$#" -ge 20 ] || continue`) or `${20}` aborts the trap handler (measured: the tool
  exited 1 with no `SIG` line and the subtree alive).
