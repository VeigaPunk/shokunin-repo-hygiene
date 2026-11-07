# Gate signal handling — why a killed shell script leaves its `timeout` children running

source: S325, S326
round: 79
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
