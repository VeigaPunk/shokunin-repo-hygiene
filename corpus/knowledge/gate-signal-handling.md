# Gate signal handling — why a killed shell script leaves its `timeout` children running

source: S325, S326, S328, S068
round: 79, 80
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
  substitution. At base a TERM or HUP to the tool's pid killed the shell and left timeout's group running; INT was
  held until the child ended (`census/round-80/controls/c2-K-a-do-nothing.txt`: 12 of 12 signal rows orphaned).
- r80 splits the tool in two processes instead. The front shell starts the worker — the same file — as
  `setsid "$BASH" "$SELF" "$@" <&0 &` and only `wait`s on it. A background job of a non-interactive shell is not
  a process-group leader, so setsid execs in place ("setsid runs a program in a new session. The command calls
  fork(2) if already a process group leader.", S328): `$!` is the new session's id, and every descendant that does
  not call setsid itself stays in that session, timeout's new groups included (S326 changes the group, not the
  session). The worker refuses to run if it is not its own session leader.
- On TERM/INT/HUP the front's trap fires at once (it is in `wait`, S325) and scans `/proc/*/stat` for field 6, the
  session id (S068), after the last `) ` (the comm field may hold spaces and parentheses), with no fork per process;
  it SIGSTOPs every member (so none can fork during the kill), SIGKILLs them, repeats until none is left (at most 8
  passes), removes the worker's private TMPDIR (the worker's own scratch, selftest fixtures and error files live
  there), prints `SIGNAL<TAB>SIG<name><TAB>RECEIPT-QUARANTINE-SIGNALED` and exits 128 + n. A first draft that
  forked a `$(...)` per /proc entry took more than the 5 s settle on 9 of 15 rows
  (`census/round-80/records/prefreeze-feasibility.txt`).
- Measured (`census/round-80/records/c2-after.txt`): 15 rows, 0 mismatches, 0 orphans; a trap-only tool and a front
  that kills only the worker pid both stay at 12 orphan rows (`controls/c2-K-b-trap-only.txt`,
  `controls/c2-K-c-no-session-kill.txt`) — killing the worker leaves its `$(...)` subshells and timeout groups.
- Limits: SIGKILL to the front; a descendant that calls setsid itself or double-forks into another session; a SIGINT
  the caller ignored before starting the tool (S325, above: both processes then ignore it); the stage-2 move and
  later stages of a non-dry-run invocation use the same mechanism but no row measures them.

