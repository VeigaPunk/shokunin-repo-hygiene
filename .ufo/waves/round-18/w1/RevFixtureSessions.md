STATUS: DONE — current same-process-group cleanup is sound for the fixture’s bash/git tree; the recorded d2 leaks came from executions that did not start a new session.

## Axis

Operability.

## Findings by severity

### Moderate — the d2-fifo residue is from a runner execution without the committed session isolation, not evidence that current `run_tool` missed its own group

The current fixture’s `Popen(..., start_new_session=True)` at `tests/fixtures/r17-census-hygiene.py:293-304` makes the launched bash process a new session/process-group leader. Thus, absent a descendant explicitly changing groups, PGID equals `proc.pid`; `os.killpg(proc.pid, SIGKILL)` at :309-318 targets that process and its same-group descendants. Shell command substitutions, a fork, or a double-fork alone inherit the group and are covered.

The leaked-process inventory contradicts that launch mode for the affected runs: `census/round-18/leaked-procs-before-1631.txt:7-20` records four d2-fifo/d2-symlink-fifo process trees started 13:40:26–13:41:27. Their root bash PIDs (562276, 574643, 596478, 597162) have PGIDs/SIDs 558610 or 558608, not their PIDs; their git descendants are in those same inherited groups and blocked in `wait_for_partner` on `git ... status`. `ps` later showed PID 1497, their reparenting target, is `/usr/lib/systemd/systemd --user`, consistent with the fixture parent having exited while these children remained. These executions therefore did not run the current `start_new_session=True` path (or any equivalent isolation).

The timestamps fit old closure-run bytes: the recorded roots predate `ddb7347`’s committer time (14:22:08 -03:00); the round-17 lesson says the later wave-2 fixes landed at `4f48343` (committer time 15:57:26 -03:00). The recorded `a31642d.sh` and `cc21683.sh` names identify historical census-tool snapshots, not hashes of the fixture runner, so the exact old runner bytes/closure cannot be attributed from this inventory alone. Importantly, the committed fixture already contains the session-kill path in `ddb7347` and `4f48343`; the leak records show an earlier/different execution, not a failure reproduced against those committed bytes.

Mechanism: in a runner without a new session, `killpg(proc.pid, ...)` need not address the child’s inherited PGID. If it returns `OSError`, this fixture catches and ignores it, then calls unbounded `proc.communicate()` (:309-318). A Git process blocked opening the FIFO keeps the pipe open, so `communicate()` can hang; `unblock_fifos()` is after it (:328-334), and `cleanup()` is only reached from `main()`’s `finally` (:1166-1169, :1295-1296). An outer termination of that stuck runner leaves the blocked descendants orphaned. The smallest fix is already present in the current fixture: run every tool invocation in its own session before using `killpg`.

### Low — process-group killing is not a universal descendant-containment mechanism

A grandchild that only double-forks remains in the same process group and is killed. A descendant that calls `setsid()` (or otherwise moves to another process group) escapes `killpg(proc.pid, ...)`. If such a process inherits stdout/stderr, the unbounded second `communicate()` can wait forever; if it closes those pipes, `communicate()` may return while that descendant still runs. Because FIFO unblocking comes after `communicate()`, it cannot rescue a pipe-holding escaped reader. The ignored `killpg` error also has no bounded fallback. No such detached process is evidenced here; the observed Git status processes are in their original groups. For the current fixed bash/Git fixture this pattern is sufficient, but it is not complete for arbitrary daemonizing descendants. If that broader guarantee is required, use containment that survives `setsid` (for example, a per-run cgroup); otherwise scope the guarantee to children that remain in the process group.

## Verification / evidence

- Read `tests/fixtures/r17-census-hygiene.py:271-334`, `:1166-1169`, and `:1295-1296`; read `corpus/lessons/round-17.md:80` and `census/round-18/leaked-procs-before-1631.txt:1-58`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tests/fixtures/r17-census-hygiene.py` → no output (no current worktree diff for this fixture).
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --follow --format='%h %s' -- tests/fixtures/r17-census-hygiene.py` → `4f48343 ...`; `ddb7347 ...`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -E 'start_new_session|killpg|communicate\(\)|unblock_fifos' ddb7347 -- tests/fixtures/r17-census-hygiene.py` → lines 300, 311, 314-315, 325; same command for `4f48343` → lines 303, 314, 317-318, 328. This is literal fallback only; no semantic proof is claimed from grep.
- `git show --no-patch --format='%H%n%aI%n%cI%n%s' ddb7347` → author 2026-10-20 12:42:34 -03:00, committer 14:22:08 -03:00; `4f48343` → author 14:24:42 -03:00, committer 15:57:26 -03:00.
- `ps -o pid,ppid,pgid,sid,lstart,stat,wchan:24,args -p 562276,562277,562279,574643,574984,574987,574989,596478,596479,596480,597162,597357,597358,597359` → the listed roots and descendants share PGID/SID 558610 or 558608; roots’ PIDs differ from those IDs; git rows are in `wait_for_partner`. `ps -o pid,ppid,pgid,sid,lstart,stat,wchan:24,args -p 1497,558608,558610` → PID 1497 is user systemd; no rows for group leaders 558608/558610.
- LSP unavailable: `read xd://lsp` returned `No such tool: xd://lsp` (the mounted-device list has no LSP device). Therefore no LSP status/references/definition/diagnostics were available; the literal search was not treated as semantic proof.

## Residual risk and verification gaps

No tests or fixture runs were launched. The process inventory does not record the fixture runner’s source digest, so it establishes that those starts lacked a new session but cannot identify the exact closure or runner bytes. The group-kill claim is bounded to same-process-group descendants; arbitrary descendants that detach remain outside this mechanism.
