STATUS: DONE — one foreign orphan family (kama-r16-FamilyLoadingRace, 1 process); C3 cwd/argv predicates miss it.

## Axes

calibration (lowest, 7), operability (8), coverage (8). This seat is judged on coverage. No tool was installed.

## Adjacency

On the host at this snapshot, the only non-souji prefix family left orphaned by another lane's fixture is `kama-r16-FamilyLoadingRace` (probable owner lane kama, from that prefix and cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`): 1 process, pid 863272, etimes 21671, state S, wchan `poll_schedule_timeout.constprop.0`, ppid 1497 (`/usr/lib/systemd/systemd --user`). `ps -eo pid,etimes,args` shows only `import argparse`; the scratch paths are the process's stdout and stderr symlinks, both `(deleted)`, and `stat` of `/tmp/kama-r16-FamilyLoadingRace` is ENOENT. Same-window scratch argv families that were still inside a live timeout (mado-r20-SentinelFixtures, 3 processes, ages ~176–203s, `timeout 2400`; tameshi-r18w1 / tameshi-r4-2, ages ≤16s) are in-flight work, and `omp-python-runner-1000` (~35 processes, ppid 3092, `do_epoll_wait`, directory present) is the harness. Deleted-cwd processes were 58, all souji fixture families (`r15-census-config` 44, `r17-census-hygiene` 14), matching `census/round-18/leaked-procs-before-1631.txt` (58 lines, 0 mentions of kama or 863272). Nothing was signalled.

## Evidence

Quoted `ps -eo pid,etimes,args` row:

```
 863272   21671 import argparse
```

`ps -o pid,ppid,etimes,stat,wchan:28 -p 863272` (etimes 21623, a few dozen seconds earlier):

```
   PID PPID ELAPSED STAT WCHAN
863272 1497   21623 S    poll_schedule_timeout.constprop.0
```

`/proc/863272/cwd` → `/home/vgpnk/Projects/shokunin/kama-shokunin` (directory exists; link does not end in ` (deleted)`). `/proc/863272/cmdline` → `import argparse`. `/proc/863272/fd` readlink (not environ):

```
1 -> /tmp/kama-r16-FamilyLoadingRace/loading-current.json (deleted)
2 -> /tmp/kama-r16-FamilyLoadingRace/loading-current.stderr (deleted)
```

`stat` of `/tmp/kama-r16-FamilyLoadingRace`, `.../loading-current.json`, and `.../loading-current.stderr` → `No such file or directory`.

C3 as specified (cwd ends in ` (deleted)`, or an argv element under `/var/tmp`, `/tmp`, or `/dev/shm` whose scratch directory is gone) does not match pid 863272: cwd is the live lane repo and argv contains no scratch path.

Souji leaks do hold deleted scratch fds as well, so an fd walk without precedence would recount them. Examples, readlink only:

```
185592 fd 255 -> /var/tmp/souji-r16-repin.z0t4kl7c/baseline_preharm/tools/souji-census.sh (deleted)
185605 fd 3   -> /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo/.git/config (deleted)
562279 fd 3   -> /var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo/b/kept.txt (deleted)
```

Those three already match cwd-deleted or argv-path-gone. Province keeps process work observational: `PROVINCE.md:46-47` (souji reports on process health via adjacency and does not act on processes).

Classifier pass over `ps -eo pid,etimes,args` plus `/proc/<pid>/{cwd,wchan,stat,cmdline}`: 58 cwd `(deleted)` rows, zero of them outside the two souji fixture families above; zero non-souji `wait_for_partner` / fifo / pipe blockers with etimes ≥ 600.

## Proposed move

Add one residue predicate to both `tools/souji-proc-census.sh` and `census/round-18/leak-count.py`, readlink-only, never signalling, never opening the path: if a `/proc/<pid>/fd/*` target is an absolute path under the scratch prefixes, ends in ` (deleted)`, and the top-level scratch directory is absent, the process is residue. One row per pid, precedence `cwd-deleted` then `argv-path-gone:<path>` then `fd-path-gone:<path>` (strip the ` (deleted)` suffix). Skip the tool's own pid tree. Do not write `/tmp/kama-r16-FamilyLoadingRace` into SKILL.md, SCORECARD.md, PROVINCE.md, QUALITY.md, or LOG.md.

That governs the cross-lane class C3's cwd/argv rules miss, keeps the blind counter comparable (QUALITY Q5), and leaves the 58 souji rows on their existing reasons.

## Affected axes

- Coverage: improves. Governed residue classes go from cwd-deleted and argv-path-gone to those plus fd-path-gone. Host count of the new class at this snapshot is 1 (family `kama-r16-FamilyLoadingRace`).
- Operability: unchanged. The census watchdog, exit codes, and fixture session kills stay as C1 specifies. The new predicate does not signal.
- Calibration: unchanged. The missing `/tmp` path stays out of authority files, so it does not add an `LG-DANGLING-PTR` token.

## Risks

- Emitting fd-path-gone as an extra row for a pid that already has cwd-deleted recounts the souji 58 (the three fds above). Precedence is the cut that prevents that.
- A live tool that unlinks a log inside a scratch directory that still exists must not match; the top-level directory check is what keeps pid 863272 in and a rotated log in a live dir out.
- `readlink` of `/proc/<pid>/fd` is outside the seat probe's `{stat,cmdline,cwd,wchan}` list. L1 can re-read pid 863272 the same way. This seat did not read environ and did not signal.
- ProcCensusFixture cases that assert an exact reason for a synthetic process stay valid if the new case is additive and the two old reasons win when they apply.

## Verification

L1, after both tools exist: on a synthetic `/var/tmp` process whose cwd is a live directory, whose argv has no scratch path, and whose stdout is an unlinked file under a removed `/tmp/<family>/` directory, both tools report that one pid with reason `fd-path-gone` and do not report a second reason. A cwd-deleted control is reported once, as `cwd-deleted`. Live host run: souji cwd-deleted count stays 58 against `census/round-18/leaked-procs-before-1631.txt`; `by_prefix_family` includes `kama-r16-FamilyLoadingRace` with count 1 while pid 863272 still exists. Do not kill it from this seat.

## Verdict

holds — the foreign leftover is real, count 1, and the smallest fix is the fd predicate with one-row precedence. The FIFO-blocked deleted-cwd population remains the souji 58.
