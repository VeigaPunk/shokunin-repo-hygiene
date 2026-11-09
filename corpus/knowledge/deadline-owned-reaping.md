# The timeout owner owns the pipes: a child that escapes its process group still holds them

source: S367 (Python `subprocess`, the `start_new_session` parameter; that the child calls setsid()); S368 (Linux man-pages `setsid(2)` DESCRIPTION; that the new session is a new process group); scored against census/round-96/c2-forgery-probe.py and census/round-96/c2-setup-arms.py at round 96.
verified-at: S367 page opened 2026-11-09 from docs.python.org/3 (capture census/round-96/srcs/subprocess.html); S368 page opened 2026-11-09 from man7.org (capture census/round-96/srcs/setsid.2.html, sha256 52cbc190…, man-pages 6.19). Quoted sentence occurrence counts are in the SOURCES rows. Gate: S368 quote "The calling process also becomes the process group leader of a new process group in the session" (17 words, occurrence 1, access 2026-11-09). S369–S371 correct the teaches cells of S365–S367 (see the amendments in plans/round-96.md A11).
recheck: 365d, or when the quoted sentence changes.

Round 96 (C2, operability of the forgery probe's exit-code discipline). Ground: r95 closure A6 (plans/round-95.md A6), R95ReviewerC2 Q1-pipe-holder, R95Sentinel F2.

## The gap

The r95 probe killed a timed-out fixture's process group but then called `p.communicate()` again, which waits for the
child's stdout/stderr pipes to reach EOF. A fixture whose `setsid()` grandchild keeps those pipes open therefore hangs
the probe past its own `--timeout` (r95 T1: `ARM T1 exit=hung`). S367: "`start_new_session` is true the `setsid()`
system call will be made in the child process prior to the execution of the subprocess." A new session is a new
process group (S368); a group kill directed at the probe's group cannot reach a grandchild that called setsid().

## The r96 fix

`_wait_output` waits for the fixture's own output, and on timeout kills the group, then waits only for the integer
returncode — never for pipe EOF. The probe names the timeout and exits 2 within its `--timeout` (~120 s, T1
`conform=yes`). The pipe-holding grandchild is NOT reaped by the probe or by the arm counter (plans/round-96.md A4).

## Limits

- The probe does not reap the escaped grandchild; it only stops being held by it. The arm counter's group kill
  (`killpg` of the probe's session) does not reach the `setsid()` grandchild either, so one T1 grandchild survives every
  T1 arm run, re-parented to init (measured: plans/round-96.md A4; R96Sentinel F-4 E6a–E6c; reapcheck.out B/C).
  The earlier sentence "the arms counter kills it" was false and is withdrawn.
- A fixture that writes unbounded output in unbounded time is not refused by the timeout: the probe drains the pipes
  into its own memory (27.3 GB RSS observed at --timeout 8, SIGTERM at 36 s, no FATAL line; plans/round-96.md A5).
  The earlier sentence "still blocks on a full pipe" was false and is withdrawn. Rate-limited and finite floods are
  refused cleanly.
- `--timeout 0` and a read-only `--work` refused with exit 2 and their own arms (T2/T3) are setup refusals, not
  deadline semantics; the abort fixture (T4) is a no-SUMMARY setup failure, never the probe's verdict.

## r97 fix (counter-owned reaping by identity; survivors counted)

Round 97 (C2, operability 8). Ground: plans/round-96.md A4/A5/A8, census/round-97/c2-setup-arms.py,
census/round-97/c2-forgery-probe.py.

- **Reaping by argv identity.** The counter now reaps the T1 grandchild itself: `_reap_by_identity` signals
  exactly the own-uid processes whose argv carries the arm's absolute fixture path byte-exactly, skipping the
  counter and the probe, and re-verifies starttime at act time. A new session is a new process group (S368), so
  the group kill cannot reach the grandchild; argv identity is the counter-owned key. The run prints
  `survivors=<n>` on every T1 ARM line. Measured: `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0`
  (census/round-97/records/c2-after.txt); the r96 probe leaves survivors=1 on the same arm. The counter never
  signals a process it did not plant (limit (i) in the prereg).
- **Output cap.** The probe drains the pipes with selectors and refuses output over `--max-output` (8 MiB
  default) as a setup failure (exit 2, `C2-FORGERY-FATAL:`), instead of draining into its own memory and ending
  with SIGTERM before the timeout (the r96 A5 limit: 27.3 GB RSS, SIGTERM at 36 s, no FATAL).
- **Signal exits.** A killed-by-signal child prints as `exit=-15` in the ARM line (A8): it never reads as a
  verdict exit. The counter only ever SIGKILLs its own sessions and records the resulting status instead of
  coercing it.

### r97 correction (appended after the wave; plans/round-97.md A12, A13)

- The reap does NOT signal only processes the counter planted. It SIGKILLs every own-uid process whose argv carries the
  arm's absolute fixture path and that was not in the snapshot taken at arm start. A foreign process that acquires the
  path during the arm is killed (measured: 30 of 42 decoys in a continuous run). The reap is not safe to run on a shared
  path. Do not cite the r97 reap as a safe ownership mechanism.
- A signal exit renders as `exit=-15` on both the r96 and r97 counters. No distinct mark exists.

### r98 correction (appended after the wave; plans/round-98.md A0.1, A12)

- The reap is now by ownership (S075 field 4/22, S368): `_reap_owned` kills only the pid the arm recorded at
  spawn (re-verified by its starttime, stat field 22) and its ppid-chain (field 4) descendants, or an orphan
  reparented to the counter itself (the counter sets `PR_SET_CHILD_SUBREAPER(1)`). argv may select candidates
  but never authorises a kill. A foreign decoy (its ppid is its own driver, never the counter) is never reached
  and never killed.
- **Do not cite the r97 argv reap as an ownership mechanism** (r97 correction above stands). The r98 ownership
  rule is the successor: a foreign own-uid process planted after the arm starts carrying the arm's fixture
  token is spared by the r98 counter and killed by the r97 counter (committed decoy test
  `census/round-98/c2-decoy-test.py`, Q174).
- The T1 survivors byte is counted by the descendant relation, not by a starttime comparison against the spawn
  pid (F12/C-5: the old comparison could never count an owned escapee and was same-tick nondeterministic).
  `conform` now binds `survivors=0` on T1, so a counter that reaps nothing cannot pass on conform alone (C-3).
