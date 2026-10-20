STATUS: DONE — One medium operability defect found in parent-signal cleanup.

Attacked claim: C1 operability — per-repository watchdog in `tools/souji-census.sh` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`.

## Finding

**MEDIUM — Parent-only SIGTERM can disable the watchdog and leave a hung worker unbounded.** The worker is launched in a separate process group (`set -m`, `$!`; lines 1478–1481), while the watchdog is detached into a new session (`setsid`; lines 1482–1502). The EXIT trap installed by `prepare_census_tmp` removes the shared `CENSUS_TMP` directory (lines 232–243). The watchdog's state file is under that directory (line 1474), and it only sends TERM/KILL if it can `mkdir "$state_path"` (lines 1492–1499). If an orchestrator sends SIGTERM to the census PID alone while a repo worker is hung, shell exit cleanup removes the directory; the still-running watchdog later fails that `mkdir` and exits without signaling the worker. Since neither child shares the census process group, the parent-only signal does not stop them. A hung repository process can therefore outlive the census without the claimed bound.

**Smallest remediation:** on parent termination, stop and reap the active worker group and watchdog before deleting the shared state directory; alternatively keep watchdog state alive until the watchdog has completed, with a cleanup path that still terminates/reaps workers.

## Requested boundary checks

- **Empty/zero PGID:** no reachable path identified. The signal IDs come from `$!` for the started worker/watchdog (lines 1480, 1500–1502), and group operands are quoted as `"-$pgid"`, `"-$worker"`, or `"-$watchdog"` with `--` (e.g. lines 1488, 1495, 1527, 1547). They are not sourced from the timeout environment.
- **PGID reuse:** a narrow check-then-signal window exists between `kill -0 -- "-$pgid"` and TERM/KILL (lines 1492–1497; the fallback is lines 1546–1548). If the group vanishes after the check and its numeric ID is reused before the signal, an unrelated same-user process group could be signaled. This is a theoretical race from static review, not an exercised exploit; no safe conclusion that reuse is impossible. Consider this lower confidence than the parent-cleanup defect.
- **`setsid`:** the watchdog is isolated from the worker and caller groups (lines 1482–1502); no zero/empty target issue observed. The detach also means parent-only termination needs explicit cleanup, as above.
- **Temporary paths/symlinks:** `mktemp -d /var/tmp/...XXXXXX` creates the census directory (lines 238–242); state names are created with `mktemp` under that directory and then replaced by a directory (lines 1474–1475). This avoids predictable-name/symlink attacks from other UIDs under normal `/var/tmp` permissions. Same-UID processes remain within the same filesystem trust boundary. The signal-cleanup issue is separate: the private directory is removed too early while the detached watchdog still depends on it.
- **`SOUJI_CENSUS_REPO_TIMEOUT`:** value is read as data (line 220), rejects non-digits and normalizes leading zeroes, then enforces 1..86400 (lines 245–257); CLI parsing is followed by validation (lines 2581–2603). No shell-evaluation/injection path found. Very long all-zero input is stripped before the length check, an untested potential CPU-cost edge, not an observed injection.
- **`unset -f` coverage:** line 180 includes `setsid`, `sleep`, `mktemp`, `kill`, `mkdir`, `rm`, and `bash` (as well as the other listed commands). No missing function name found for the watchdog's external commands.

## Evidence / verdict

Static inspection only; no lane code was run (the assignment supplied no `ALLOWED-EXEC`). Relevant source ranges: lines 178–258, 232–243, and 1470–1650.

Exact revision commands and outputs:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
5efb519f00075d958c3d1109ef6fcb24c487eb87

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 5efb519f00075d958c3d1109ef6fcb24c487eb87
5efb519f00075d958c3d1109ef6fcb24c487eb87
```

Verdict: **C1 partially fails** for interruption/parent-only termination, despite the normal timeout path using nonempty positive child PIDs and bounded TERM/KILL escalation. No remediation was made.