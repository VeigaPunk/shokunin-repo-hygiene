STATUS: DONE — post-guard FIFO blocks inside the shared process group; `set -m` makes fixture `killpg` miss that group.

Axes: operability (judged), calibration, coverage. The move closes the operability leak the `set -m` sketch reopens. Row shape, finding ids, and residue classes stay as specified. Installs: none.

## C1 — FIFO swapped after the guard, on `status`
`guard_git_files` (`tools/souji-census.sh:546-585`) `stat -L`s `.git/info/attributes`, sees a regular file, returns. `census_one:1264` therefore calls git. The shim swaps on `status`, so `rev-parse` (`:1280`), `worktree list` (`:1000`), and `for-each-ref` (`:1006`) return. `count_dirty:1122` runs PATH `git … status` (`-c core.attributesFile` still opens `info/attributes`). Git blocks in `open(2)`. `emit_census:1403` `row=$(census_one)` shares the parent's process group and blocks in the substitution read; `HEADER` (`:1412`) is never printed; later repos are skipped. Outer `timeout 15` → rc 124, zero rows. A FIFO present before the guard already emits `<repo>\t0\t0\t0\t0\t\terror` at `:1265-1266` and never execs git.

Overfit of `:1403`: `set -m` only around `(census_one >tmp) &`; `set +m`; watchdog `sleep N; kill -TERM -$kid; sleep 2; kill -KILL -$kid` with stdio on `/dev/null`; on timeout discard `tmp` and print that error row plus `souji-census: repo-timeout <N>s <repo>`; keep going; exit 0.

The overfit fails when: the outer harness `SIGKILL`s first (default bound 600); `wait` rc 143 is treated as timeout (exit 2 at `:1407` must abort the whole run; any other nonzero stays exit 1; a finished row must survive a late TERM); only `count_dirty` is wrapped (`r-inc-fifo` leaks are stuck in `rev-parse`, `census/round-18/leaked-procs-before-1631.txt`); stdout is a pipe; `/usr/bin/git` bypasses the shim; an out-of-range `--repo-timeout` / `SOUJI_CENSUS_REPO_TIMEOUT` is clamped (usage exit 2, integer 1..86400, default 600). Header `:9` is bash+coreutils+git, so a python `prctl` is a new dependency. `set -m` must actually split the group with stdin not a tty, and the child must stay out of state `T`.

Evidence the groups are shared today: pid 562279 `(git)` state `S`, wchan `wait_for_partner`, ppid 562277, pgrp=session=558610, same as bash 562276 (ppid 1497) and 562277. `os.killpg(558610, SIGKILL)` would reap them. After `set -m` the worker pgrp is new and that `killpg` does not.

## C2 — `census/round-17/gate-replays-ddb7347.json` at `SKILL.md:163`
`evaluate` (`tools/souji-landing-gate.py:607`) cites paths only via `CITED_PATH_RE` (`:77-79`): `tools|tests/fixtures|census/round-<n>/` ending `.sh|.py`. The `.json` token is invisible, so `LG-MISSING-REG` stays quiet and `--round 18` can exit 0. `LG-DANGLING-PTR` is absent from `FINDING_IDS` (`:115-123`). `check_frozen_pins:548-567`: `rev-parse --verify measured^{commit}` rc 1 sets `measured_ok=False` and adds no check (Q25(b), `corpus/QUALITY.md:64`). Selftest covers a hash mismatch (`:1075`) and an absent blob (`:1101`), not a missing commit.

Overfit: one hardcoded absence check for that json path.

The overfit fails on the other unresolved tokens, on `:line`, `{a,b}`, and `round-6..11`, on tokens containing `<` `>` `*` or `round-N`, on fleet-only paths (report `fleet`, not a finding), and on `corpus/pointer-exemptions.tsv`. It also fails the replay pin if it runs for `--round` &lt; 18. Folding Q25(b) into every round can add `LG-FROZEN-MEASURED` on a rev the five pinned replays never asserted; the round&gt;=18 gate is the only replay lock the claim already names.

## C3 — orphan FIFO reader, deleted `/var/tmp`
Pid 562279, uid 1000 (this uid). cwd `/var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo/b (deleted)`. cmdline is `git -C` that path plus the `count_dirty:1122` status argv. `stat` of the path is ENOENT. starttime 1340976, `CLK_TCK` 100, age ≈11871s at this read. Ancestor 562277 cwd is the deleted temp dir, wchan `do_wait`.

Overfit: emit 562279 because argv contains that missing `/var/tmp/...` path.

The overfit fails when the filter is state `D` (`S` + `wait_for_partner` is the FIFO open), when `/tmp*` matches `/tmpfoo`, when cwd is deleted but argv is clean (562277), and for `/tmp` and `/dev/shm`. A live FIFO whose directory still exists is outside this claim. The tool stays read-only: no signal, redact and truncate the command, skip ESRCH. Residue classes governed: repo rows only → deleted-cwd plus dangling tmp argv.

## Move
Keep the inner watchdog (`set -m` worker, private stdout file, TERM then KILL 2s, watchdog stdio `/dev/null`, started after `set +m`). Fixture teardown, given `start_new_session`, signals every pid whose session id equals the leader, not only `os.killpg(leader)`. That is the same session the live orphans already share, and it still reaps the split pgrp after `set -m`. No `prctl` helper.

## Risks
A session walk without `start_new_session` hits the runner. `SIGKILL` of the leader reaps the worker only if that walk exists; the EXIT trap cannot run. Ungated Q25(b) can move historical replay exits.

## Verification
L1: `--repo-timeout` inside the outer bound; shim on `status`; neighbour row kept; exit 0; error row and stderr line; exit 2 still aborts; no pid left with that sid; child pgrp differs under a non-tty stdin. Gate `--round 17` replay multiset unchanged; `--round 18` dangling token is `LG-DANGLING-PTR`. Proc census row for 562279 shows `S` / `wait_for_partner` and does not signal it.
