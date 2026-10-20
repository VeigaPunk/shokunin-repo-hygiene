STATUS: DONE — No outside consumer of souji-census output or flags; fleet process-group kill can orphan a detached repo worker.

# Axes
- Operability (judged): a fleet round kill must not leave a census worker running past the repo bound.
- Output contract: seven-column TSV, `error` placeholder row, exit 0 on a degraded repo.
- Substrate: `setsid` session of the per-repo timer versus the lane process group `shokunin-watchdog.sh` records.
- External compatibility: fleet scripts and other lanes' `SKILL.md` that read census stdout, stderr, or flags.

# Attacked claim
C1 operability at `5efb519f00075d958c3d1109ef6fcb24c487eb87`. Question: does anything outside the lane consume `tools/souji-census.sh` output or flags, and would the new `error` rows, per-repo runtime, or `setsid` dependency break them?

# Answer
Nothing outside the lane consumes the tool's stdout, stderr, or flags. The timeout `error` row is the same seven-column placeholder baseline `b576341` already emitted. `--repo-timeout` / `SOUJI_CENSUS_REPO_TIMEOUT` are unread outside the lane. The new hard `setsid` check therefore fails no current outside caller.

The operability break is substrate, not a parser. `shokunin-watchdog.sh` `kill_mission` signals only the lane process group. Census puts the repo worker in another group (`set -m`) and the timer in a new session (`setsid`). Parent SIGTERM runs the EXIT trap, which deletes the timer's state directory, and the timer signals the worker only if `mkdir` of that directory succeeds. A round advance during an in-flight census can leave the repo worker with no bound.

# Outside consumers checked

Prescribed globs, one `grep -n` per existing file. Pattern `souji-census`.

| Surface | Result |
|---|---|
| `/home/vgpnk/Projects/shokunin/scripts/shokunin-watchdog.sh` | no match |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` | no match |
| 17 other `*-shokunin/SKILL.md` files that exist | no match |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md` | matches at 112, 149, 191 — inside the lane |

`SKILL.md` absent (grep has nothing to read): `audio-shokunin`, `game-dev-2d-shokunin`, `revenger-shokunin`. Their top-level `README.md` files also have no `souji-census` match.

Follow-up exact files, because `scripts/*.sh` does not cover `scripts/hyaku/` and the watchdog launches from conf and `templates/round-prompt.md`. Pattern `souji-census|SOUJI_CENSUS`. No match in:

- `scripts/hyaku/append-closure.py`, `await-capacity.sh`, `await-event.sh`, `fleet-commit.sh`, `inline.sh`, `jj-lane-selftest.sh`, `jj-lane.sh`, `probe-alias.sh`, `status.sh`, `hyaku.env`
- `/home/vgpnk/Projects/shokunin/shokunin.conf`
- `/home/vgpnk/Projects/shokunin/templates/round-prompt.md`

`scripts/sources-census.sh` is a different program (SOURCES-CONTRACT-v1, `corpus/SOURCES.md`, TSV `lane<TAB>metric|code<TAB>value`). The fleet driver calls that tool, not souji-census:

```319:332:/home/vgpnk/Projects/shokunin/scripts/shokunin-watchdog.sh
# sources_gate — validate existing lane registries through the census tool.
# Fleet-root lanes are exempt; rc 1 blocks, while rc 2 means unusable/missing
# registry and is a warning that must not prevent round advancement.
sources_gate() { # lane
  local lane="$1" census="$SHOKUNIN_ROOT/scripts/sources-census.sh" rc out
  ...
  out=$("$census" validate --root "$SHOKUNIN_ROOT" "$lane" 2>&1); rc=$?
```

Shared spelling `--root` is a different argv on a different binary. Souji flags `--repo-timeout`, `--compare`, `--include-root` are not passed. Souji rows are not read. Do not point this gate at `tools/souji-census.sh`.

# Contract deltas that would matter to a consumer

Header bytes are unchanged from baseline to tip:

- `b576341:tools/souji-census.sh:192` and `5efb519:tools/souji-census.sh:207`
  `repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags`
- Diff header unchanged: `repo\tfield\tbefore\tafter\tchange`

Baseline already emitted the placeholder row `printf '%s\t0\t0\t0\t0\t\terror\n'` at `b576341:tools/souji-census.sh:1266` and `:1281`. Tip timeout rows at `5efb519:tools/souji-census.sh:1693` and `:1709` are the same shape: `<repo>\t0\t0\t0\t0\t\terror`. New stderr lines are `souji-census: repo-timeout <N>s <repo>` (`:1678`, `:1707`) and `souji-census: repo-timeout-unreaped <repo>` (`:1641`). No outside file matches `souji-census`, so none of those lines are parsed outside the lane.

`setsid` is absent from baseline (`git grep setsid b576341 -- tools/souji-census.sh` exit 1). Tip requires it before census and before `--compare`:

```2615:2617:tools/souji-census.sh
command -v git >/dev/null 2>&1 || { printf 'souji-census: git not found\n' >&2; exit 1; }
command -v du >/dev/null 2>&1 || { printf 'souji-census: du not found\n' >&2; exit 1; }
command -v setsid >/dev/null 2>&1 || { printf 'souji-census: setsid not found\n' >&2; exit 1; }
```

Host already has it: `/usr/bin/setsid`, util-linux 2.42.4 (`setsid from util-linux 2.42.4`). This seat did not install it. Pacman is paused; no package change.

`set -m` is new (only at tip line 1478). Baseline had no job-control split.

# Finding — fleet kill does not cover the new process groups

Worker and timer launch (`5efb519:tools/souji-census.sh`):

```1478:1501:tools/souji-census.sh
  set -m
  "$@" > "$row_file" 2> "$stderr_file" &
  worker=$!
  set +m
  setsid bash -c '
    ...
    kill -0 -- "-$pgid" 2>/dev/null || exit 0
    if mkdir -- "$state_path" 2>/dev/null; then
      : > "$state_path/timed_out"
      kill -TERM -- "-$pgid" 2>/dev/null || true
      sleep 2
      kill -KILL -- "-$pgid" 2>/dev/null || true
```

The timer kills the worker group only after `mkdir` of a path under `CENSUS_TMP` (`:1474`, `:1492-1499`). The only cleanup is:

```232:241:tools/souji-census.sh
cleanup_census_tmp() {
  if [ -n "${CENSUS_TMP:-}" ]; then
    rm -rf -- "$CENSUS_TMP"
  fi
}
...
    trap cleanup_census_tmp EXIT
```

Fleet reap (`/home/vgpnk/Projects/shokunin/scripts/shokunin-watchdog.sh`):

- Launch records the `setsid` bash pid as the lane group: `:209-221`.
- `kill_mission` sends `kill -TERM -- "-$mid"`, waits about 5s, then `kill -KILL -- "-$mid"`: `:253-286`.
- That signal set is the lane group only. The repo worker's pgid is `$!` after `set -m`. The timer is a new session (`setsid` with no `--fork`). Neither is a member of `-$mid`.

Trace, static, assuming ordinary fork inheritance (the census script never calls `setsid` on itself; an agent that `setsid`s the tool before exec is a separate case, called out under risks):

1. Report lands, `advance` calls `kill_mission` (`:349-357`).
2. SIGTERM hits the census parent. Bash runs the EXIT trap. `rm -rf` deletes `CENSUS_TMP`, including `state_path`.
3. Worker and timer survive, because they are not in the lane group.
4. The timer loop only watches `kill -0 -- "-$pgid"` (`:1487-1492`). It does not watch the parent. At `REPO_TIMEOUT` (default 600, `:220`) `mkdir "$state_path"` fails, the `if` body is skipped, and the timer exits without TERM/KILL.
5. `wait_group_exit` sees the lane group gone and `launch_lane` starts the next round (`:360-361`) while the repo worker is still alive. Default tick is 450s (`:52`). The worker is no longer bounded by 600s.

This composes with the parent-EXIT hole already traced in `SentinelWatchdogImpl.md` and `RevWatchdogDiff.md` (signal only after `mkdir`). Those notes cover a parent-only signal. This seat adds the outside driver that sends that signal: `kill_mission` on the lane group, which is exactly a parent SIGTERM that does not include the detached children. Signaling from the parent EXIT trap alone still loses on SIGKILL, and the current trap deletes the directory the timer needs. The timer is the process that survives the group kill, so the reap has to live there and has to run when `mkdir` fails.

# Proposed move
In the `setsid` watchdog at `tools/souji-census.sh:1482`, pass the census pid (`$$`). On each poll, if `kill -0` of that pid fails, TERM then KILL the worker group and exit. At the deadline, if `mkdir "$state_path"` fails, still TERM then KILL the worker group. Leave header bytes, the `error` row, exit 0/2/3, and the live-parent timeout path as they are. Keep the `setsid` dependency: the timer has to outlive the lane group or nothing remains to signal the worker.

# Risks
- Pid reuse can make a dead census pid look alive for one poll interval. The deadline path still signals when `mkdir` fails, so the worker does not become unbounded.
- Do not use the timer's PPID as the liveness bit. With `set +m`, the `setsid` process is not a group leader, and util-linux 2.42.4 `setsid` then execs in place (fork only when it is already a group leader, or with `--fork`). A later `--fork` or a group-leader launch reparents the timer while the census parent is still alive; a PPID check would kill a healthy run.
- If a substrate `setsid`s the census tool itself, `kill_mission` never delivers SIGTERM to that census, the parent-death path does not run, and the in-process timeout still applies. This move does not claim that case.
- Same-uid pid-reuse between `kill -0 -- "-$pgid"` and TERM/KILL remains the narrow race `SentinelWatchdogImpl.md` already recorded. This move does not widen it.

# Verdict
**Partial.** External compatibility holds: no outside fleet script or other lane `SKILL.md` reads souji-census output or flags, and the new timeout row does not change the TSV shape those callers would have had to accept. Operability does not hold for a fleet round kill during `run_repo_with_watchdog`: `setsid` plus `set -m` put the worker outside `kill_mission`, and the timer then drops the bound when EXIT cleanup removes `state_path`.

# Verification
Not run. This seat has no `ALLOWED-EXEC`. Static reads only.

Main agent, in a `/var/tmp` clone at `5efb519`, not against the live fleet:

- Start one blocked repo under the census parent. SIGTERM the parent (and, separately, SIGTERM the process group of a wrapper, matching `kill_mission`). Assert the worker pgid is gone within a couple of seconds.
- Live-parent timeout still prints `souji-census: repo-timeout <N>s <repo>` and the row `<repo>\t0\t0\t0\t0\t\terror`, and the next repo is still measured.

# Commands (abridged)
```
grep -n souji-census /home/vgpnk/Projects/shokunin/scripts/*.sh
# exit 1, no matches. Files: scripts/shokunin-watchdog.sh, scripts/sources-census.sh

grep -n souji-census /home/vgpnk/Projects/shokunin/*-shokunin/SKILL.md
# only souji-shokunin/SKILL.md:112, :149, :191
# absent: audio-shokunin, game-dev-2d-shokunin, revenger-shokunin

git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat \
  b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f00075d958c3d1109ef6fcb24c487eb87 \
  -- tools/souji-census.sh
# tools/souji-census.sh | 631 +++++++++++++++++++++++++++++++++++++++++++++----
# 1 file changed, 592 insertions(+), 39 deletions(-)

git grep -n setsid b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-census.sh
# exit 1

command -v setsid; setsid --version
# /usr/bin/setsid
# setsid from util-linux 2.42.4
```

Tooling: no install. `setsid` was already `/usr/bin/setsid` from util-linux 2.42.4.
