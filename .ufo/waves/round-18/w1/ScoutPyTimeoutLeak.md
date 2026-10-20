STATUS: DONE — static subprocess audit of the six named fixtures + run-matrix.py; 44/58 leaked processes trace to `r15-census-config.py` run_tool, 14/58 to the pre-commit r17 fixture; current r17 fixture reaps, r15/r14 do not.

# Scope
Files read at b576341 (worktree, branch master): `tests/fixtures/{r15-census-config,r17-census-hygiene,r14-census-boundary,r15-preservation-evidence,r14-evidence-cache,r16-landing-gate}.py`, `census/round-17/run-matrix.py`, `census/round-18/leaked-procs-before-1631.txt`. Read-only corroboration: `ps -eo pid,ppid,pgid,sid,stat,wchan,etime,args`, `/proc/<pid>/cwd`, `git -C <lane> show/log/merge-base/cat-file` on the named repo. No tool installs; no writes outside this report.

# 1. Every subprocess call site

Legend for "grandchildren on TimeoutExpired": Python's `subprocess.run` kills only the Popen child it created (`process.kill()` = SIGKILL to that pid); it never signals the child's process group. A `Popen`+`communicate` site's fate is whatever its handler does.

| file:line | call | timeout | start_new_session | grandchildren on TimeoutExpired | reachable census/git FIFO block |
|---|---|---|---|---|---|
| r15-census-config.py:274 (run_setup, body 270-287) | run | 60 (:281) | no | TimeoutExpired uncaught -> traceback; direct child killed only | no: setup git runs on plain repos; FIFOs planted later (:496-497) |
| r15-census-config.py:734 (strace probe) | run | 20 (:746) | no | caught :748 -> die(2); strace killed, `sh`/`cat` may outlive | no: reads AGENT/config.yml |
| **r15-census-config.py:781 (run_tool, 757-806)** | run, argv `strace -f ... -- bash TOOL --root ... --include-root` | **90 (:788)** | **no** | **caught :790-793 -> Result(124), kills nothing; census bash + git survive** | **YES — r-inc-fifo, see §2A** |
| r17-census-hygiene.py:150 (run_setup) | run | 60 (:156) | no | uncaught traceback; direct child only | no: git on plain repos; FIFO planted after init |
| **r17-census-hygiene.py:293 (run_tool, 271-325)** | **Popen** | **60 default (:271), communicate :310** | **YES (:303)** | **:312-318 killpg(proc.pid, SIGKILL) + communicate + unblock_fifos** | **YES by design (case_08/09); reaped at tip** |
| r17-census-hygiene.py:1099 (stat probe) | run | 30 (:1105) | no | direct child only | no: single `stat -L` |
| r14-census-boundary.py:125 (run_setup) | run | 60 (:132) | no | uncaught; direct child only | no |
| r14-census-boundary.py:330 (strace probe) | run | 20 (:350) | no | caught :352 -> die(2) | no |
| **r14-census-boundary.py:392 (run_tool, 361-405)** | run, argv `strace -f ... -- bash TOOL` | **90 (:399)** | **no** | **caught :401 -> Result(124), kills nothing; census bash + git survive** | **no FIFO in this fixture (0 `mkfifo`/`info/attributes` hits) — latent, 0/58** |
| r15-preservation-evidence.py:84 (invoke, 83-90) | run | 180 (:88) | no | caught :290 -> records "timeout", kills nothing | no FIFO input; tool = tools/souji-preservation-evidence.py (:32) |
| r14-evidence-cache.py:64 (invoke, 63-70) | run | 180 (:68) | no | **no TimeoutExpired handler in file -> traceback**, direct child only | no FIFO input; tool = tools/souji-evidence-cache.py (:43) |
| r16-landing-gate.py:94 (git helper) | run | **none** | no | unbounded hang; no handler | no FIFO input (fresh scratch repos) |
| r16-landing-gate.py:155 (Gate.run, 147-161) | run | 180 (:156) | no | only FileNotFoundError caught (:157) -> **TimeoutExpired propagates**, direct child killed, gate's git children survive | no FIFO input |
| run-matrix.py:85 (git helper) | run | none | no | unbounded | n/a (lane rev-parse) |
| **run-matrix.py:94 (run, 89-107)** | **Popen** | **900 default (:89); selftest 600 (:212)** | **YES (:96)** | **:102-106 killpg(SIGKILL) + communicate** | kills the fixture's session group **only when the 900s cap fires**; a fixture that returns early with orphans is not reaped |
| run-matrix.py:200 (git show) | run | none | no | unbounded | n/a |

# 2. Leak matching (`leaked-procs-before-1631.txt`, 58 lines)

Counts: 44 lines = 22 pairs `rev-parse`; 14 lines = 4 groups `status`; 44+14=58. All have ppid=1497 (`systemd --user`), i.e. orphaned; sampled `/proc/<pid>/cwd` are all `(deleted)`; all still alive at audit time (elapsed 52:43 to 03:14:15), so they are not transient.

## A. 44/58 — `bash .../souji-census.sh --root /var/tmp/r15-census-config.<rand>/unsafe-repos/r-inc-fifo [--include-root]` + `git -C .../r-inc-fifo rev-parse --is-inside-work-tree`
- 22 distinct `r15-census-config.*` roots, exactly 2 procs each. Parent copies are the red arms: `souji-r16-repin.*/baseline_preharm/`, `souji-r16-matrix.*/pre-harm/`, `souji-r16-PreservationRepin/preharm/`, `souji-r16/preharm.sh`, `souji-r17-matrix.*/pre-harm/`.
- Producing fixture/call: `r15-census-config.py` case_03 (:1125-1134) -> `soft_repo` (:1079, argv at :1082) -> `run_tool` (:757) -> `subprocess.run` (:781, timeout 90). The FIFO is `repo/fifo.inc` created at :496-497 and wired via `[include] path = ../fifo.inc`; the baseline/pre-harm census has no config guard, so `census_one`'s probe (a31642d:253, current `tools/souji-census.sh:1280`) opens the include and blocks.
- Observed block: `git` wchan `wait_for_partner` (fs/fifo.c `fifo_open`), e.g. pids 185605, 639568; parent bash wchan `do_wait`. The census bash is a direct child of the `strace` that `subprocess.run` SIGKILLs at 90 s; strace detaches tracees on death, so census+git survive (`run_tool` then returns rc 124 and the fixture continues, rmtree'ing the scratch at :1429-1430 -> deleted cwd).

## B. 14/58 — `bash .../souji-census.sh --root /var/tmp/r17-census-hygiene.<rand>/d2-fifo` (+ `/d2-symlink-fifo`) + `git -C .../b ... status --porcelain`
- Groups: d2-fifo arm a31642d (562276,562277,562279) and cc21683 (574643,574984,574987,574989); d2-symlink-fifo arm a31642d (596478,596479,596480) and cc21683 (597162,597357,597358,597359).
- Producing fixture/call: `r17-census-hygiene.py` case_08 (:749-758, `mkfifo(attrs)`) and case_09 (:761-770, symlink -> `attrs.fifo`), through `d2_fleet` (:590) and `degraded_fleet_problems` -> `run_tool(["--root", str(fleet)])` (:501) -> Popen (:293). The census dirt call (a31642d:127-131, current :1104-1124) opens `b/.git/info/attributes` and blocks. Two identical-argv bash procs are the command-substitution shells (`st=$(git ...)`), one of them observed in `anon_pipe_read`.
- Timing: 13:40:26-13:41:27, i.e. before `ddb7347` 14:22:08 — the commit that first adds this fixture *and* its `start_new_session`/`killpg` reaper (`git log -S start_new_session`: only ddb7347; `git show ddb7347^:tests/fixtures/r17-census-hygiene.py` = "exists on disk, but not in 'ddb7347^'"). [INFERENCE] the uncommitted working copy that ran at 13:40 had no reaper; the committed tip does.
- The r15 leaks continue after ddb7347 (14:22:15 through 16:01:58) because `r15-census-config.py` was never given a reaper — `run-matrix.run`'s 900 s killpg never fires (the fixture returns rc 0 after its own much shorter 90 s timeouts).

# 3. Verdict
- C1's operability claim "no lane fixture leaves a blocked process behind" **fails at b576341**: `r15-census-config.py:781` leaks 44/58 with no session/reap; `r14-census-boundary.py:392` carries the identical defect (0/58 today only because it has no FIFO fixture); the 14/58 r17 leaks are historical and the committed fixture would reap them.
- Smallest fix: in both `run_tool`s, mirror r17 (`Popen(start_new_session=True)` + `communicate(timeout)` + `os.killpg(proc.pid, SIGKILL)` on TimeoutExpired). Because a blocked `open(2)` is not released by SIGKILL of the waiter's *ancestor*, also register every fixture FIFO (`r15` :497) and, after killpg, release it with `os.open(path, O_WRONLY|O_NONBLOCK)` + close (r17's `unblock_fifos`, :328-335). Add TimeoutExpired handlers to `r15 run_setup` (:274), `r17 run_setup` (:150), `r14 run_setup` (:125), `r16-landing-gate.py:155`, and a timeout to `r16-landing-gate.py:94`, `run-matrix.py:85`, `run-matrix.py:200`.

## Cross-fix hazard for C1 (L1 must route)
Once `emit_census` uses `set -m` per-repo process groups, a fixture's `killpg(census_pid)` kills only the census shell's group; the per-repo census+git blocked in `open(2)` sits in its *own* group and survives — and the census's own watchdog dies with the shell. So fixture-side reaping must not rely on `killpg` alone: FIFO release (or explicit per-repo pgid kills) is required. Also verify `proc.communicate()` after `killpg`: if an escaped grandchild holds the fixture's stdout/stderr pipe, communicate blocks forever; the contract's "watchdog ... holds no stdout/stderr pipe of the caller" (temp-file stdout) is load-bearing for fixtures too.
- Peer report (SoujiR18.FixtureR18Bounded-5, not independently verified here): its new fixture snapshots the census session via `/proc/<pid>/stat` and kills every pgid still in that session, which does cover `set -m` groups; it also probes each injected FIFO with `O_WRONLY|O_NONBLOCK` for ENXIO (ENXIO = no blocked reader). That technique is the model for r15/r14; its precondition is that the census is started with `start_new_session=True` so its sid is private, and the scan must exclude the fixture's own session.

# Remaining unknowns
- The pre-commit r17 fixture body was never in git; its exact timeout shape is inferred from the leak timestamps and the committed file's own "caught by the 60s process-group kill" comment.
- Whether any leaked grandchild called `setsid`/`set -m`: baseline censuses a31642d/cc21683 contain no such call (grep), but the /var/tmp copies are deleted.
- Process count reconciliation beyond 44+14: exact, 58 lines.

# Commands run (selected)
`ps -eo pid,ppid,pgid,sid,stat,wchan:22,etime,args` filtered to sampled pids; `readlink /proc/<pid>/cwd` (7 pids, all `(deleted)`); `git log -S start_new_session -- <fixture>`; `git show ddb7347^:<fixture>`; `git merge-base --is-ancestor ddb7347 b576341`; `git show a31642d:tools/souji-census.sh | awk ...`; `awk`/`grep` over the leaked list; line-numbered `grep` over the seven source files.
