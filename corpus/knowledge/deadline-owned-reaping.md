# The timeout owner owns the pipes: a child that escapes its process group still holds them

source: S367 (Python `subprocess`, the `start_new_session` parameter); scored against census/round-96/c2-forgery-probe.py and census/round-96/c2-setup-arms.py at round 96.
verified-at: page opened 2026-11-09 from docs.python.org/3 (Python 3.15 documentation), capture census/round-96/srcs/subprocess.html with its tag-stripped text beside it; quoted sentence occurrence count in its SOURCES row.
recheck: 365d, or when the quoted sentence changes.

Round 96 (C2, operability of the forgery probe's exit-code discipline). Ground: r95 closure A6 (plans/round-95.md A6), R95ReviewerC2 Q1-pipe-holder, R95Sentinel F2.

## The gap

The r95 probe killed a timed-out fixture's process group but then called `p.communicate()` again, which waits for the
child's stdout/stderr pipes to reach EOF. A fixture whose `setsid()` grandchild keeps those pipes open therefore hangs
the probe past its own `--timeout` (r95 T1: `ARM T1 exit=hung`). S367: "`start_new_session` is true the `setsid()`
system call will be made in the child process prior to the execution of the subprocess." A new session is a new
process group; a group kill cannot reach it.

## The r96 fix

`_wait_output` waits for the fixture's own output, and on timeout kills the group, then waits only for the integer
returncode — never for pipe EOF. The pipe-holding grandchild is left to the arm counter's own kill; the probe names
the timeout and exits 2 within its `--timeout` (~120 s, T1 `conform=yes`).

## Limits

- The probe does not reap the escaped grandchild; it only stops being held by it (the arms counter kills it).
- A fixture that writes unbounded output still blocks on a full pipe before the timeout fires; only the post-kill
  wait is now bounded.
- `--timeout 0` and a read-only `--work` refused with exit 2 and their own arms (T2/T3) are setup refusals, not
  deadline semantics; the abort fixture (T4) is a no-SUMMARY setup failure, never the probe's verdict.
