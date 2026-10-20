STATUS: DONE — SIGTERM of a census blocked on a repo leaves the whole worker tree orphaned permanently; SIGINT-to-pid is inert (bash, no orphan); the r18 fixture never interrupts the census, so the 8/0 battery cannot see this.

# Attacked claim

C1 operability (round 18), interruption cleanup: the seat's attack is "cleanup on interruption" — **any orphan is a finding**. C1 itself claims per-repo process groups and `--repo-timeout` reaping (timeout → `error` row + `repo-timeout Ns` stderr, others measured, exit 0) and is *silent* on what happens when the census itself is terminated.

Probe (ALLOWED-EXEC): at 5efb519, census on a synthetic root whose repo b hangs on a FIFO `.gitignore`; SIGTERM, then separately SIGINT, to the census pid after 2 s; then list processes still in that census's session/process groups.

# Apparatus

- Clone: `/var/tmp/souji-r18w2-ProbeExternalSignal/lane`, HEAD = `5efb519f00075d958c3d1109ef6fcb24c487eb87`.
- Fleet `/var/tmp/souji-r18w2-ProbeExternalSignal/fleet`: `repo-a`, `repo-b`; each a main repo, one commit, `refs/remotes/origin/master` set. Then `mkfifo repo-b/.gitignore`.
- Hang pre-check: `timeout 3 git -C repo-b status --porcelain` → **rc=124** (blocked; git opens the FIFO for read and parks in `wait_for_partner`).
- Census command (identical in every trial):
  `tools/souji-census.sh --root /var/tmp/souji-r18w2-ProbeExternalSignal/fleet --repo-timeout N`
- Census runs in a fresh session, in the foreground of a launcher shell (`setsid --fork bash -c '…; census …; echo $? > rc'`). The launcher's only child is the census, so the census pid is unambiguous. The driver enables job control before spawning, so the census inherits default signal dispositions (verified: without `set -m`, an async child has `SigIgn: …0006`, i.e. SIGINT+SIGQUIT ignored — that would have voided the SIGINT arm).
- Every recorded pid was discovered from `/proc/<pid>/stat` (sid/pgid) and `/proc/<pid>/{cmdline,wchan,children}`; nothing was signalled except pids recorded in that trial.

# Findings

## F1 — SIGTERM leaves the blocked worker tree orphaned, permanently

Trial `term` (`--repo-timeout 30`, SIGTERM delivered at t=4.50 s):

Pre-signal tree (t=2 s):

```
pid=1311442 ppid=1311423 pgid=1311423 sid=1311423 state=S wchan=do_wait cmd=bash …/tools/souji-census.sh --root … --repo-timeout 30
  pid=1319616 ppid=1311442 pgid=1319616 sid=1311423 state=S wchan=anon_pipe_read cmd=bash …/souji-census.sh …
    pid=1320687 ppid=1319616 pgid=1319616 … cmd=bash …/souji-census.sh …
      pid=1321603 ppid=1320687 pgid=1319616 … wchan=do_wait cmd=bash …/souji-census.sh …
        pid=1321607 ppid=1321603 pgid=1319616 … wchan=wait_for_partner cmd=git -C …/fleet/repo-b … status --porcelain --ignore-submodules=all --untracked-files=normal …
  pid=1319617 ppid=1311442 pgid=1319617 sid=1319617 … cmd=bash -c … souji-census-watchdog 1319616 30 /var/tmp/souji-census-now.QwZyvT/watchdog.vi4S4F
```

After `kill -s TERM 1311442`: `census pid exited`; launcher `rc=143` (census killed by SIGTERM). Census stdout/stderr empty (rows are buffered until the end).

Residue:

```
t=+1s survivors in census session 1311423:
1319616, 1320687, 1321603, 1321607   (git still wchan=wait_for_partner)
t=42s recorded-pid liveness (12 s past the 30 s repo-timeout):
1319616, 1320687, 1321603, 1321607   all state=S, git still wait_for_partner
t=42s census session 1311423: same four processes   (no process in census pgroup 1311423)
watchdog 1319617: GONE;  /var/tmp/souji-census-now.QwZyvT: No such file or directory
```

Trial `term2` (`--repo-timeout 10`, SIGTERM at t=3.47 s) pins the mechanism:

```
before signal: watchdog state_path=/var/tmp/souji-census-now.wUoMCm/watchdog.eToTFd parent_exists=yes
after signal:  state_path_parent_exists=no           launcher rc=143
t=+1s: watchdog 3546106 ALIVE; worker 3546104/3546590/3546961 + git 3546962 ALIVE (wait_for_partner)
t=14s (4 s past the 10 s limit): watchdog 3546106 GONE; the same four worker processes still ALIVE
```

Root cause (source, 5efb519):

- `tools/souji-census.sh:241` — the only trap that can run on termination is `trap cleanup_census_tmp EXIT`; there is **no** TERM/INT/HUP trap (all trap sites: 241, 1818, 1823, 1921 — EXIT only). Empirically the EXIT trap *does* run on SIGTERM: `rc=143` and the census tmp dir is gone.
- `tools/souji-census.sh:232-236` — `cleanup_census_tmp` deletes `$CENSUS_TMP`.
- `tools/souji-census.sh:1474-1475` — the watchdog's `state_path` lives inside `$CENSUS_TMP`.
- `tools/souji-census.sh:1478-1481` — the worker is spawned under `set -m`, i.e. in its own process group, so a signal sent to the census pid never reaches it.
- `tools/souji-census.sh:1493-1499` — the watchdog's `kill -TERM/-KILL -- "-$pgid"` is **inside** `if mkdir -- "$state_path" 2>/dev/null; then …`. With the parent directory already removed by the census EXIT trap, `mkdir` fails, the `if` body is skipped, and the watchdog exits **without ever signalling the worker group**.
- Nothing else references those pids; the FIFO has no writer, so `git status` never unblocks.

Consequence: any SIGTERM (operator `kill`, service stop, CI/job timeout) during a hung repository leaves the fast worker shell + blocked `git status` running forever; the nominal `--repo-timeout` bound (default 600 s) no longer applies because the tool's own EXIT trap disarmed its watchdog. Two independent trials show it: 12 s and 4 s past their limits, with the watchdog gone and the worker group intact.

## F2 — SIGINT to the census pid is inert (bash), so no orphan — but no cleanup either

Trial `int` (`--repo-timeout 30`, SIGINT at t=3.68 s):

```
census SigIgn: 0000000001000004      (SIGINT bit clear, SIGQUIT ignored)
census SigCgt: 0000000042817efb      (SIGINT caught)
sending SIGINT to census pid 2630272 → "census pid STILL PRESENT after signal"
t=+1s: census 2630272 alive in do_wait, child sleep 0.1 running; worker tree still present
t=42s: all gone;  launcher rc=0
stdout: repo-a … clean ;  repo-b … error
stderr: souji-census: repo-timeout 30s …/fleet/repo-b
```

The census ignored the pid-targeted SIGINT, continued, its own watchdog fired at 30 s, the repo-b row became `error`, and the run exited 0 — i.e. C1's stated uninterrupted timeout behaviour reproduced exactly. Control: a plain `bash -c 'while :; do sleep 0.1; done'` started the same way has `SigIgn: …0004` and likewise survives SIGINT-to-pid (`CONTROL: plain bash alive 1s after SIGINT-to-pid`). So the SIGINT arm produced no orphan only because **nothing died**; this is generic bash deferral, not census-specific. A terminal Ctrl-C (SIGINT to the foreground process group) would kill the census and enter F1's path — not executed here (outside the exec grant) → [INFERENCE].

## F3 — the r18 fixture cannot observe F1

- `tests/fixtures/r18-census-bounded.py` B1–B8 (`case_b1` :814, `case_b2` :849, `case_b3` :886, `case_b4` :927, `case_b5` :1010, `case_b6` :1048, `case_b7` :1059, `case_b8` :1069) never send SIGTERM/SIGINT to the census; the only signals in the file are cleanup `signal.SIGKILL` (458, 468, 546, 583, 591).
- The harness does look for survivors after a run (`leaked_before_cleanup` :574; flagged in `census_problems` :668-672), but every case lets the census exit on its own; the FIFO cases run to the watchdog timeout, which works while the census is alive.
- The matrix runner reaps by session after each run: `census/round-18/run-matrix.py:169-183` launches with `start_new_session=True` and calls `kill_session(proc.pid)` after `communicate` (:87-140). A session-level residue would therefore be killed by the harness, not reported.
- Net: the claimed r18-bounded 8/0 battery is silent on interruption cleanup; F1 is outside what it exercises.

# Verdict

**FAIL** on the attacked axis (interruption cleanup). C1's stated uninterrupted measurements hold as observed (repo-b `error` row, `repo-timeout 30s` diagnostic, neighbour measured, exit 0), but the tool cannot be stopped cleanly while a repository hangs: SIGTERM leaves a permanent orphan worker group, and its own EXIT trap disables the watchdog that would otherwise reap it. SIGKILL is a different case (no EXIT trap → `$CENSUS_TMP` stays → watchdog can reap at the limit), [INFERENCE] from source, not run.

# Smallest fix

1. Make `cleanup_census_tmp` (232-236) terminate the active worker group and the watchdog **before** `rm -rf "$CENSUS_TMP"`; in `run_repo_with_watchdog` keep `CURRENT_WORKER_PGID` (set after `worker=$!`, 1480) and `CURRENT_WATCHDOG` (after `watchdog=$!`, 1502) in globals and clear them after each normal reap:
   `kill -TERM -- "-${CURRENT_WORKER_PGID:-0}"` (guarded by `-n`), short wait, `kill -KILL`, `kill -TERM "$CURRENT_WATCHDOG"`.
   This alone fixes SIGTERM (the EXIT trap is proven to run on it).
2. Defense in depth: dedent the watchdog's writes/signals (`: > timed_out`, `kill -TERM`, `sleep 2`, `kill -KILL`, `: > killed`, 1494-1498) out of `if mkdir -- "$state_path"` (1493) so a missing/removed state directory can never disable reaping; `mkdir` should only gate writing the `timed_out`/`killed` markers.

# Hygiene

No writes to the lane or fleet repo; only this report. All probe processes were killed by recorded pid and confirmed gone (`post-cleanup liveness: GONE` for every pid); no process with the probe path remains; all three probe tmp dirs (`QwZyvT`, `9uFxdV`, `wUoMCm`) are absent. The clone and scratch dir were deleted. No tools installed or upgraded.

# Remaining unknowns

- Process-group-directed SIGINT (actual Ctrl-C) not exercised — outside the exec grant.
- SIGKILL of the census not run; bounded-leak behaviour inferred from source (EXIT trap does not run on SIGKILL, so the watchdog's `state_path` survives and its kill path stays armed).
