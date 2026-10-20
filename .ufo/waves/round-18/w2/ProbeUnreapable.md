STATUS: DONE — the `repo-timeout-unreaped` path was reached and behaves as claimed (both diagnostics, error row, exit 0), but no committed test exercises it, and every escape that leaves the group is invisible to both the alarm and the r18 fixture's residue check (measured, including one survivor found only by a cmdline scan).

# W2 ProbeUnreapable — attacks C1's `repo-timeout-unreaped` clause

Baseline `5efb519f00075d958c3d1109ef6fcb24c487eb87`, clone
`/var/tmp/souji-r18w2-ProbeUnreapable/lane`, probe assets
`/var/tmp/souji-r18w2-ProbeUnreapable/probe`. Read-only against the lane; no lane file touched.

Claim under attack (verbatim, `tools/souji-census.sh:157-163`):

> Candidate metadata guards and census runs each use a private process group. If one exceeds the
> bound, its group receives TERM, then KILL two seconds later; a timed-out repository gets the row
> `<repo>\t0\t0\t0\t0\t\terror` and stderr `souji-census: repo-timeout <N>s <repo>`. Other
> repositories continue. After KILL, reaping is bounded to three seconds; a survivor is reported
> as `souji-census: repo-timeout-unreaped <repo>`.

## Method

Fleet of three clean repos (`a`, `b`, `c`); a `git` shim first on `PATH` hangs on exactly one
`status` call for `b` (same injection point as fixture B1/B3/B5) and plants one child shape. Census
runs with `--repo-timeout 2` in a private session; `/proc` sampled every 100 ms to capture child
states at kill time; after the census exits, the FIFO is probed `O_WRONLY|O_NONBLOCK` (an `fd`
instead of `ENXIO` proves a live reader) and the census session is scanned exactly as the fixture
does (`session_members`: `session == census pid`). Only recorded pids were signalled, each
re-verified by `/proc/<pid>/stat` start time (and the one unrecorded survivor by cmdline).

## Measured

| variant | child shape | state at ~1.0 s | census stderr | row `b` | rc | wall | residue after census exit |
|---|---|---|---|---|---|---|---|
| control | none | — | (empty) | `1 0 0 0 … clean` | 0 | 1.29 s | none |
| stop | in-group child SIGSTOPped by shim | `T` (pgid = worker) | `repo-timeout 2s …/b` | `0 0 0 0 "" error` | 0 | 5.00 s | none (gone by 2.75 s) |
| stopterm | same + SIGTERM ignored | `T` | `repo-timeout 2s …/b` | error | 0 | 4.99 s | none (gone by 2.77 s) |
| vfork | `vfork()` parent, child in FIFO read | parent `D wchan=kernel_clone` | `repo-timeout 2s …/b` | error | 0 | 5.00 s | none (gone by 2.73 s) |
| fuse | in-group reader on a FUSE file whose read never answers | `D wchan=folio_wait_bit_common` | `repo-timeout 2s …/b` | error | 0 | 4.99 s | none (gone by 2.83 s) |
| **zombie** | zombie parked in the worker's group; parent left the group, stayed in the session, never `wait()`s | `Z` in group, parent `S` | **`repo-timeout-unreaped …/b`** + `repo-timeout 2s …/b` | error | 0 | **11.02 s** | parent alive (session member), zombie alive |
| setsid | grandchild via `start_new_session` (own session/pgid) holding the FIFO | `S pgid=sid=<own>` | `repo-timeout 2s …/b` | error | 0 | 5.00 s | **alive, FIFO reader present** |
| daemon | double-fork + `setsid()` holding the FIFO | `S pgid=sid=<own>` | `repo-timeout 2s …/b` | error | 0 | 4.99 s | **alive, FIFO reader present** |
| pgroup | child `setpgid()` into the census's own group (in real use: the caller's group) | `S pgid=<session leader>` | `repo-timeout 2s …/b` | error | 0 | 4.99 s | **alive, FIFO reader present** |
| vforkescape | `vfork()` where the child `setsid()`s before blocking | parent `D` | `repo-timeout 2s …/b` | error | 0 | 5.00 s | **escaped child alive, FIFO reader present** |

Exact bytes, zombie case (`result-case-zombie.json`):

```
row    b: '/var/tmp/…/fleet/b\t0\t0\t0\t0\t\terror'
stderr  : 'souji-census: repo-timeout-unreaped /var/tmp/…/fleet/b\n'
          'souji-census: repo-timeout 2s /var/tmp/…/fleet/b\n'
workers : worker group = {zombie 'Z', pgid=<worker>, comm=git}; escaped parent S, sid=<census>
```

All runs: neighbours `a`, `c` measured `1 0 0 0 <mtime> clean`; exit 0.

## Findings

**F1 — the branch is real and correct, and reachable only via an unkillable group member.**
Every "unreaped" decision is a process-group probe (`kill -0 -- -$worker` at 1571, 1599, 1633;
flag set at 1513, 1548, 1566, 1575, 1595, 1603, 1637; print at 1641). I reached it by parking a
zombie in the worker's group: the zombie cannot be killed and `kill -0 -pgid` still succeeds, so
both 3 s probes fire — 1569-1576 sets the flag, 1617/1626 clear it because `$worker` itself is
gone, and 1630-1638 sets it again. Printed diagnostics, row bytes, neighbour rows, and exit 0 all
match the claim exactly. Holding.

**F2 — no committed test exercises it (attacks the claimed numbers).**
`grep -n unreap tools/souji-census.sh` → only 163 (doc) and 1641 (printf). In
`tests/fixtures/r18-census-bounded.py`: 0 occurrences of `unreap`; 0 of `setsid`. `B1`–`B8` assert
only the `repo-timeout` line (`require_timeout_diag`, 808) and clean FIFO/session state; the
selftest's timeout block (2402-2556: diagnostic 2417, stalled-pid gone 2467, slow path 2505,
protected 2538, bounds 2543-2556) asserts the `repo-timeout` line, the error row, wall < 6 s,
`ENXIO`, and that the stalled git pid is gone — never `repo-timeout-unreaped`. So `r18-bounded
8/0`, `selftest 49→62` and `r15/r17` cannot speak for that clause: no assertion names the string,
and no case creates a survivor, so removing the print at 1641 cannot fail any of those numbers
[INFERENCE from the assertion texts — the mutant was not run]. That
matters because the flag is set by a probe at 1575, cleared at 1617/1626, and set again by the
probe at 1637 before the print.

**F3 — SIGKILL survival: D-state is inducible here but killable; only a zombie survives.**
- `T`-state child (SIGSTOPped, and a TERM-ignoring variant): reaped by the group SIGKILL within
  ~1.5 s both times.
- `vfork()` parent in the vfork wait (`D`, wchan `kernel_clone`): reaped by the group SIGKILL.
- FUSE read with a server that never replies (`D`, wchan `folio_wait_bit_common`): reaped within
  ~1.5 s of SIGKILL (standalone: `D` at 1.0 s, `kill -9`, `ABSENT` at the +1.5 s check and after
  the fs process was killed too). The wait is killable on this kernel.
- Therefore a genuine uninterruptible wait is **not** reachable unprivileged on this host (no
  FUSE/NFS/device hang that resists fatal signals), and the alarm cannot be produced by hanging
  I/O — only by a zombie (F1). If the intent is "hung D-state I/O is reported", that intent is
  untestable here and, on this kernel, moot for FUSE.

**F4 — every escape from the group is silent, and the fixture's residue scan cannot see it.**
`setsid`, double-fork-`setsid`, `setpgid` into another group, and `vfork`+`setsid` all leave a live
process holding the FIFO after the census exits, while stderr carries only `repo-timeout` and the
run exits 0. `session_members` (`tests/fixtures/r18-census-bounded.py:425-430`, used at 573-574 and
checked at 668-671) selects only `session == census pid`; my post-run scan returned **0** members
for the `setsid`, `daemon` and `vforkescape` escapees while each was alive in its own session, so
`leaked_before_cleanup` would be `[]` and `B6`
would pass. (The `pgroup` escapee stays in the census's session, so that scan does see it — yet the
census still prints no alarm; a session sweep would find it but could not kill it, since in real use
that group is the caller's.) Direct proof of detector blindness: the `vfork`+`setsid` child (pid 4160621,
`sid=pgid=pid`, reparented to 1497) survived the census **and** my own session-scoped cleanup; it
was found only by a `cmdline` scan for the seat path and killed after verifying that cmdline.
This agrees with `ProbeSetsidEscape.md`; the additions here are the `setpgid`-into-the-census's-own
-group destination (in real use, the caller's group — unfixable by sweeping, since killing that
group kills the caller) and the `vfork` hybrid. Note the census's own group probe is blind to it by
construction: the escapee is not in `-$worker`, so the claim's parenthetical is literally true —
what fails is the stronger "no residue" claim (`SCORECARD.md:15`, `corpus/lessons/round-18.md:3`).

**F5 — doc timing is understated on the unreaped path (low, accuracy).**
"Reaping is bounded to three seconds" (162) describes one probe, but the code runs two:
1569-1576 sets the flag, then 1608 (`wait watchdog`) is followed by a second 3 s probe at 1630-1638
after clearing it at 1617/1626. Measured wall: 4.99 s for a normal timeout vs **11.02 s** when a
group member survives, at `--repo-timeout 2` (≈ bound + 2 s TERM grace + 2×3 s). Still bounded, but
the sentence should say so.

## Verdict

**partial.** The narrow clause holds exactly as written: a group survivor produces
`repo-timeout-unreaped <repo>` (plus the normal `repo-timeout` line), the `0 0 0 0 "" error` row,
measured neighbours, and exit 0. What fails: (a) no test pins that clause, so the claim's numbers
say nothing about it; (b) the error row and diagnostics imply a clean run while a hostile or
misbehaving repo can leave live processes in a new session (or in the caller's group) with no
diagnostic, and the fixture's residue check is session-scoped and blind to it; (c) the "three
seconds" sentence understates the worst-case probe budget.

## Smallest fix

1. Add `B9` to `tests/fixtures/r18-census-bounded.py` (red at b576341) with exactly the measured
   zombie shape: shim forks `P`, `P` does `setpgid(0,0)` (leaves the group, same session), `P`
   forks `C`, `C` does `setpgid(0,<worker_pgid>)` and `_exit(0)`, `P` sleeps 600 s without
   `wait()`. Assert: row `0 0 0 0 "" error`; stderr contains both `repo-timeout-unreaped <b>` and
   `repo-timeout `N`s <b>`; rc 0; neighbours measured; `leaked_before_cleanup` contains exactly
   `P` (the case must tolerate that one known pid, then kill it — `kill_session` already sweeps its
   group, and the zombie is reaped when `P` dies); `session_after_cleanup` empty.
2. Fix the scope sentence where the guarantee is stated: `tools/souji-census.sh:162-163` →
   "a survivor of that process group is reported …"; `SCORECARD.md:15` and
   `corpus/lessons/round-18.md:3` → "no process in the census's own session/process group is left
   behind; a descendant that calls `setsid()` escapes (known limit)". Correct the probe budget:
   two three-second probes, so worst case ≈ bound + 2 s + 6 s.
3. For real containment (not reachable by sweeping: the `pgroup` escapee can sit in the caller's
   group, where a kill would hit the caller), run each repo in a private PID namespace
   (`unshare --user --map-root-user --pid --fork --mount-proc`, util-linux already required) so
   killing namespace init takes setsid descendants with it, or a systemd scope checked via
   `cgroup.procs` emptiness. Do not add a session-name/cmdline sweep as the only defence.

## Reproduction (exact)

```
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-ProbeUnreapable/lane
git -C /var/tmp/souji-r18w2-ProbeUnreapable/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
cd /var/tmp/souji-r18w2-ProbeUnreapable/probe
gcc -O1 -Wall -o vforkblock vforkblock.c
gcc -O1 -Wall -D_FILE_OFFSET_BITS=64 -I/usr/include/fuse3 -o fuseblock fuseblock.c -lfuse3
python3 census_unreap_probe.py              # all variants; ~54 s
python3 census_unreap_probe.py zombie fuse  # subset
```

Per-variant raw records (stdout, stderr, rows, 100 ms `/proc` samples, worker-group and
census-session membership, FIFO probe): `/var/tmp/souji-r18w2-ProbeUnreapable/work/result-case-*.json`;
FUSE standalone D-state/SIGKILL timing: `probe/fuse_test.py`.

## Tooling and probe hygiene

No installs or updates needed (gcc and libfuse3 3.18.3 + headers were already present; no Python
bindings required; pacman untouched). All
assets under `/var/tmp/souji-r18w2-ProbeUnreapable/`; every census invocation ran only against that
tree. Signals were sent only to pids the shim recorded or to members of the private census session
started by the harness. Disclosure: on the first run my harness mis-parsed its own `triggered`
marker as a pid and attempted `kill(1, SIGKILL)`; the kernel refused with `EPERM`, no process was
signalled, and the parser was fixed (marker excluded, `pid > 1` required, start-time identity check
added). Verified afterwards: no process with the seat path in `argv`, no FUSE mount, FIFO reader
gone.

## Remaining unknowns

- Whether the zombie shape can arise without a shim (e.g. a repo-configured helper that forks and
  refuses to reap): not tested; reachability matches `ProbeSetsidEscape`'s "[INFERENCE]: needs a
  daemonizing helper outside repo config".
- Whether other kernels make FUSE or NFS waits uninterruptible; if so the alarm becomes reachable
  by hung I/O and the 3 s probe would matter operationally (here it never fires for D-state).
- Whether treating a zombie-only group as "survived SIGKILL" is intended; the alarm currently
  conflates a harmless zombie with a hung process (both produce the same line).
