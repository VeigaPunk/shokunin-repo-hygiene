# Gate signal handling — a signalled shell script and its `timeout` children

source: S325, S326
round: 79
status: mined (bash 5.3.20, coreutils 9.12 on this host)

## Claim

A bash script that runs each child as `timeout <s> cmd` does not stop when a caller signals its pid: with no
trap the shell dies and the child keeps running; with a trap bash does not act while it waits for the child;
and a child of a non-interactive shell may start unable to trap INT at all.

## Why the child outlives the script

- `timeout` calls `setpgid (0, 0)` before it forks (`if (!foreground) setpgid (0, 0);`, S326, main() at v9.12,
  under "Ensure we're in our own group so all subprocesses can be killed."): timeout and the command form a new
  process group. A caller's signal to the script's pid, or to the script's own group, never reaches that group.
- `cleanup()` (S326, line 204) forwards a signal timeout itself receives to the child and then to group 0, so
  signalling timeout works; signalling the script does not.
- With no trap, TERM and HUP terminate the shell outright and the timeout group survives until the timeout expires.

## Why a trap does not fire

- S325, node "Signals": "If Bash is waiting for a command to complete and receives a signal for which a trap has
  been set, it will not execute the trap until the command completes." A foreground command, `$(...)` and
  `<(...)` all block the trap.
- The same node: only `wait` on an asynchronous command returns at once — with an exit status greater than 128 —
  and the shell then runs the trap.

## The pattern

- Start every child with `&`, keep `$!`, and block on `wait`.
- In the trap, kill the child's process group (`kill -KILL -- -<pid>`; timeout made the child pid its group id),
  kill the child itself, remove the private scratch dir, print the refusal class, and exit 128 + the signal
  number.
- Send child output to a file: a `$(...)` inside the trap is itself a foreground wait.

## Why a signal ignored on entry cannot be trapped

- S325, line 3262: "When job control is not in effect, asynchronous commands ignore ‘SIGINT’ and ‘SIGQUIT’ in
  addition to these inherited handlers." The ignore survives exec, and bash does not install a handler for a
  signal that was already ignored when it started, so a `trap ... INT` in such a process never runs.
- A counter that launches the measured script with `&` therefore hands it an untrappable INT and scores every
  INT row red (r79's s4 launch artefact, misread first as a wait race). Reset the dispositions in the child
  before exec, or run the counter in the foreground, and record which disposition was used.

## What the round-79 gate guarantees, and its limits

- Guaranteed: on TERM, INT or HUP while any child runs, the gate kills the running child's process group,
  removes its private directory, prints `check-signal=FAIL` and `RECEIPT-GATE-SIGNALED`, and exits 128 + n
  within 5 s; with no signal its verdicts are unchanged.
- Not covered: SIGKILL (untrappable); a child that leaves timeout's group (`setsid`, a double fork); a signal
  ignored on entry; and the few milliseconds of the short `$(...)` forks that remain (realpath, dirname, awk,
  mktemp), during which the trap waits for the fork to end.
