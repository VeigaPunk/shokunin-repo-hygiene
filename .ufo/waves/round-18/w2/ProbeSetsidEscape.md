STATUS: DONE — a `setsid` child escapes the per-repo TERM/KILL sweep, survives the census, and is never reported (worst case: a healthy-looking repo and an empty stderr); the census itself still finishes bounded and exits 0.

# W2 ProbeSetsidEscape — attacks C1 "no residue"

Baseline under test: `5efb519f00075d958c3d1109ef6fcb24c487eb87` (all reads/execs in the clone
`/var/tmp/souji-r18w2-ProbeSetsidEscape/lane`; probe assets in
`/var/tmp/souji-r18w2-ProbeSetsidEscape/probe`).

Claim text attacked (verbatim, `tools/souji-census.sh:157-163`):

> Candidate metadata guards and census runs each use a private process group. If one exceeds the
> bound, its group receives TERM, then KILL two seconds later; a timed-out repository gets the row
> `<repo>\t0\t0\t0\t0\t\terror` … After KILL, reaping is bounded to three seconds; a survivor is
> reported as `souji-census: repo-timeout-unreaped <repo>`.

and the lane's stronger wording: `corpus/lessons/round-18.md:3` "no lane fixture leaves a blocked
process behind", `SCORECARD.md:15` "fixtures kill their whole session on timeout … 0 leftover".

## Method

* Fleet of two clean repos (`stall`, `neighbour`): one commit, `master` + `origin/master`.
* `probe/bin/git` first on `PATH`. The census does not sanitize `PATH` (`command -v git` at 2615 is a
  presence check only), and `unset -f … git` (180) does not remove a `PATH` executable. For one armed
  call on `stall` the shim does `exec 9<>fifo` (writer, so the child's `</fifo` open cannot block),
  then `setsid sh -c 'printf %s $$ > pidfile; exec sleep 300 </fifo' &`, then either
  `exec sleep 300` (block) or `exit 0`. Carriers: `status` (census_one `count_dirty`, 1167),
  `rev-parse --is-inside-work-tree` (census_one, 1323), `config --file .git/config --no-includes
  --list -z` (guard config, 741).
* Runner starts the census under `setsid` so it is a session leader (mirrors the fixture's
  `Popen(start_new_session=True)`), records rc/elapsed, the escaped pid's `/proc/<pid>/stat`, and
  the census's session membership via `ps -eo sid=,pid=`.

## Measured

| label | carrier | shim mode | wall | `stall` row | stderr | `unreaped` | escaped child | census-session members |
|---|---|---|---|---|---|---|---|---|
| v1block | `status` | block | 5525 ms | `…0 0 0 0 <empty> error` | `repo-timeout 3s …/stall` | 0 | **alive** 3252016, sid=pgrp=3252016, ppid 1497 | 0 |
| v2exit | `status` | exit 0, fds inherited | 5518 ms | error | `repo-timeout 3s …` | 0 | **alive** 3299863 | 0 |
| v3pipe | `status` | block, caller reads stdout through `\| cat` | 5524 ms | error | same | 0 | **alive** 3339011 | 0 |
| v4samegroup (control) | `status` | block, **no** `setsid` | 5526 ms | error | same | 0 | **gone** | 0 |
| v5any | first `-C stall` call: `rev-parse --is-inside-work-tree` | block | 5506 ms | error | same | 0 | **alive** 3917698 | 0 |
| v6quiet | `status` | exit 0, child `>/dev/null 2>&1` | **460 ms** | **clean** | **(empty)** | 0 | **alive** 4132400 | 0 |
| v7guard | guard `config --file` | block | 5292 ms | error | same | 0 | **alive** 235457 | 0 |

Every run: census `rc=0`, neighbour measured `1 0 0 0 … clean`. Row bytes (`cat -A`):
`…/fleet/stall^I0^I0^I0^I0^I^Ierror$`. `ps` shows the escaped child as `S` with `pgrp == sid == pid`
(its own session), reparented to 1497, fd 0/9 on the fifo and fd 1 on a pipe (fd 1 only when the
shim does not detach it). Two consecutive identical runs left two survivors (1689001, 1771003) —
one per run.

## What holds

* Bounded at `--repo-timeout 3`: 5.2–5.5 s wall (3 s + TERM grace 2 s + reap), 460 ms when nothing
  hangs; exit 0; exact row; exact diagnostic; neighbours measured.
* No caller-visible hang: with census stdout consumed through a pipe (v3) the pipeline completed in
  5524 ms — the escape does not hold the census's own stdout.
* A backgrounded grandchild that does **not** call `setsid` is killed by the group sweep (v4):
  the boundary is exactly "enters a new session".

## What fails — the survivor test and "no residue"

The sweep and the survivor predicate are group-scoped only: `set -m` (1478) gives the worker its own
group; the watchdog signals `-$worker` (1493-1497); every "unreaped" decision is
`kill -0 -- "-$worker"` (1547-1548, 1575, 1603, 1637) and only that predicate prints
`repo-timeout-unreaped` (1641). A child that calls `setsid()` is in a different group **and**
session, so TERM/KILL never reaches it and the predicate is false.

* v1/v5/v7: timeout row + diagnostic, `unreaped` never printed, escaped child alive.
* v6quiet (the worst case): the shim returned success and detached the child, so the census
  measured both repos `clean`, wrote **nothing** to stderr, exited 0 in **460 ms**, and left the
  child alive. No diagnostic path exists for this.
* Residue accumulates: one escaped process per run per armed repo (measured twice).

## The lane's own evidence cannot see this

* Fixture: `session_members` (425-431) selects `session == census pid`; `leaked_before_cleanup =
  list(members)` (574); only that list fails a case (668-676); `kill_session` (434-475) reaps only
  groups inside that session. Measured session membership after every run: **0 while a child is
  alive** ⇒ the fixture would record `leaked_before_cleanup: []` for v1/v2/v5/v6/v7.
* Runner: `leftover_processes` (143-166) counts only argv-prefix matches (`needle = prefix`, the
  tempdir name). The survivor's argv is `sleep 300` ⇒ `leftover_procs_count: 0`
  (`census/round-18/c1-matrix-worktree.json`, `arms.changed.r18-bounded`, also
  `session_cleanup.killed: []`).
* C3 counter: `census/round-18/leak-count.py` listed 98 same-uid residues; all three survivors were
  **absent** (their cwd, argv path and fd path all exist, so none of cwd-deleted/argv-path-gone/
  fd-path-gone applies).

So 8/0, `leftover_procs_count: 0` and the r15/r17 "2 → 0"/"4 → 0" figures are true of the committed
fixtures but are not evidence for the stated guarantee.

## Secondary (accuracy, still bounded)

v2exit: the shim returned 0, yet the repo was reported `repo-timeout` because the daemon inherited
the command-substitution pipe (`st=$(git … status …)` at 1167 waits for EOF), so a successful git can
be labelled a timeout. Conservative, but it misattributes cause.

## Reachability (scope, not overclaim)

No repository-config vector found: the census neutralizes fsmonitor, hooks, attr-filter drivers and
`alternateRefsCommand` and clears `GIT_*`; the guard region (522-945) reads files directly and its
only git exec is `config --file` (741). The escape class therefore needs a daemonizing `git`
wrapper/helper outside repo config (or a future exec surface) — [INFERENCE], not measured. The defect
is the guarantee's scope plus the evidence's blind spot, not a live repo-config exploit.

## Verdict

**partial.** The timeout/operability contract holds (bounded, exit 0, exact row and diagnostic,
neighbours measured, no caller hang). "A survivor is reported" (162-163) and "no residue" fail at
their stated generality: a setsid child survives silently, and every residue detector the lane uses
is blind to it by construction.

## Smallest fix

1. Scope the sentence where the claim is made, unconditionally: `tools/souji-census.sh:162-163` →
   "a survivor of that process group is reported …"; `SCORECARD.md:15` and
   `corpus/lessons/round-18.md:3` → "no process in the census's own session/process group is left
   behind; a child that calls `setsid()` escapes (known limit)".
2. Add the only detector that can see it, as B9 in `tests/fixtures/r18-census-bounded.py`: the shim
   daemonizes with `setsid` and writes the child pid (same shape as the existing
   `SOUJI_CENSUS_STALL_PID_FILE`, selftest 2346), then the case asserts `/proc/<pid>` is gone after
   the census returns. This is red at 5efb519 and pins the limit; the session/argv checks cannot
   substitute for it.
3. If real containment is wanted instead: run each worker in a PID namespace
   (`unshare --user --map-root-user --pid --fork --mount-proc`; util-linux is already required and
   `kernel.unprivileged_userns_clone` is 1 here) so init death kills every member including a setsid
   child, or a systemd scope and test `cgroup.procs` emptiness instead of `kill -0 -- -$worker`.

## Reproduction (exact)

```
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin \
  /var/tmp/souji-r18w2-ProbeSetsidEscape/lane
git -C /var/tmp/souji-r18w2-ProbeSetsidEscape/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
# fleet: git init -b master, one commit, update-ref refs/remotes/origin/master (stall, neighbour)
# shim at probe/bin/git; runner probe/run-one.sh
LABEL=v1block PROBE_MODE=block PROBE_ESCAPE=setsid PIPE=0 bash probe/run-one.sh
PROBE_CHILD_OUT=/dev/null LABEL=v6quiet PROBE_MODE=exit bash probe/run-one.sh
PROBE_ANY=1 LABEL=v5any PROBE_MODE=block bash probe/run-one.sh
PROBE_GUARD=1 LABEL=v7guard PROBE_MODE=block bash probe/run-one.sh
```
Raw per-variant outputs: `probe/state/<label>/{out,err,summary.txt,rc.txt}`;
`probe/state/v5any/calls.log` (carrier order: `rev-parse --is-inside-work-tree` first,
`status --porcelain …` last; written by the `v5any-log` exit-mode run, whose dir keeps the original
`label=v5guard2` line), `probe/state/v7guard/calls.log` (`guard:config --file …` only).

## Tooling and cleanup

No tool installs or updates (nothing needed; pacman untouched). Only recorded pids were killed:
1457975, 1689001, 1771003, plus each runner's own escaped pid (`cleanup … gone=yes`). Verified no
process holds the probe fifo and no probe process remains. Clone deleted after this report.

## Remaining unknowns

* Whether a shipped `git` daemonizes during `status` on a real host (wrapper, or a `gc.autoDetach`
  path): not tested. The census passes `--no-optional-locks` (1166); its documented effect here is
  index-refresh suppression, and I did not verify whether it also suppresses auto-gc.
* Whether the guard phase has other git execs besides `config --file` (I read 522-1040; other guard
  helpers parse files directly).
* The escape was measured with a `PATH` shim; a repo-config-only escape was not found and may not
  exist.
