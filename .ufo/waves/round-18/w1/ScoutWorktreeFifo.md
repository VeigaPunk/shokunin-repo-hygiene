# ScoutWorktreeFifo — static (no-race) census hang

STATUS: DONE — the C1 hang is **not race-only**: a FIFO placed at a work-tree
`.gitignore` or `.gitattributes` (any depth) that exists **before** the census
starts hangs `souji-census.sh` deterministically, rc 124 under an external
`timeout`, zero rows, neighbours lost. No PATH shim, no swap, no race.

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, REV `b576341` (b5763415cc67ecff1e8fe56c58c39a6fb106d7a3).
- Script under test: `git show b576341:tools/souji-census.sh` → sha256
  `006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd` (80244 bytes, 2072 lines).
- Host: git 2.56.0, bash 5.3.20, HOME pointed at an empty `/var/tmp` dir
  (`env -u XDG_CONFIG_HOME -u GIT_DIR -u GIT_WORK_TREE -u GIT_CONFIG_GLOBAL -u GIT_CONFIG_SYSTEM -u GIT_CONFIG_NOSYSTEM HOME=/var/tmp/souji-r18-ScoutWorktreeFifo/home`).
- Tools installed/updated: none.

## Method

For each arm: fresh root with repos `a`, `b`, `c` (each a real `git init` repo,
one tracked file plus one tracked file under `sub/`, one commit), the FIFO (or
control mutation) created **before any census/git command runs**, then:

```
cd <arm> && env -u XDG_CONFIG_HOME -u GIT_DIR -u GIT_WORK_TREE \
  -u GIT_CONFIG_GLOBAL -u GIT_CONFIG_SYSTEM -u GIT_CONFIG_NOSYSTEM HOME=<empty> \
  timeout -k 2 20 bash /var/tmp/souji-r18-ScoutWorktreeFifo/census.sh \
  --root /var/tmp/souji-r18-ScoutWorktreeFifo/arm-<X>/root
```

stdout/rc/stderr captured; a `ps -eo pid,ppid,pgid,stat,wchan:40,args` snapshot
taken 3 s in; survivors re-checked after `timeout` returned; every arm's
process cwd tree scanned via `/proc/<pid>/cwd` for orphans. External
`timeout` only (base census has no bound of its own — see below).

## Results — static arms

| arm | static setup before run | rc | rows | stderr | blocked proc |
|---|---|---|---|---|---|
| D-none | clean fleet (control) | 0 | 3 | — | none |
| A-wt-gitignore | `b/.gitignore` = FIFO | **124** | **0** | empty | `git … status` in `wait_for_partner` |
| B-wt-gitattributes | `b/.gitattributes` = FIFO | **124** | **0** | empty | same |
| C-sub-gitignore | `b/sub/.gitignore` = FIFO | **124** | **0** | empty | same |
| I-untracked-dir-fifo | `b/untracked-dir/.gitignore` = FIFO (dir has no tracked files) | **124** | **0** | empty | same |
| L-a-gitignore | `a/.gitignore` = FIFO (first sorted repo) | **124** | **0** | empty | same, repo `a` |
| E-exclude-plain | `b/.git/info/exclude` replaced after creation by plain empty file (control) | 0 | 3 | — | none |
| F-info-exclude-fifo | `b/.git/info/exclude` = FIFO *before* run | 2 | 0 | `souji-census: path-protected: git-metadata-nonregular (…/b/.git: …/b/.git/info/exclude)` | none |
| G-info-attrs-fifo | `b/.git/info/attributes` = FIFO *before* run | 0 | 3 (b = `… 0 0 0 0  error`) | `souji-census: git-metadata-unsupported git-metadata-nonregular …/b/.git/info/attributes` | none |
| H-tracked-fifo | tracked `b/tracked.txt` replaced by FIFO | **0** | 3 (b `dirty=1`) | — | none |
| J-index-fifo | `b/.git/index` = FIFO | 2 | 0 | `path-protected: git-metadata-nonregular …/b/.git/index` | none |
| K-config-fifo | `b/.git/config` = FIFO | 2 | 0 | `path-protected: git-metadata-nonregular …/b/.git/config` | none |
| X-xdg | `$HOME/.config/git/ignore` and `…/attributes` = FIFO | 0 | 3 | — | none |

Representative 3-second snapshot (arm A):

```
 455308  455306  455306 S anon_pipe_read  bash …/census.sh --root …/arm-A-wt-gitignore/root
 457360  457089  455306 S do_wait          bash …/census.sh --root …/arm-A-wt-gitignore/root
 457361  457360  455306 S wait_for_partner git -C …/arm-A-wt-gitignore/root/b --no-optional-locks \
   -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null \
   -c core.attributesFile=/dev/null status --porcelain --ignore-submodules=all \
   --untracked-files=normal -- . :(exclude).ufo/state …
```

`wait_for_partner` is the kernel `fifo_open()` wait: git is blocked in `open(2)`
on the FIFO, no writer exists. Pure-git attribution on the same repos:
`git -C …/b status --porcelain` under `timeout -k 1 5` → rc 124, zero output for
A, B, C, I (and F); H rc 0; G not re-run (census guard blocks status first).
So the hang is git's work-tree ignore/attribute reader, reached from
`count_dirty()` at `tools/souji-census.sh:1104`, whose `git status` is
`:1124`, called at `:1291` (`census_one`), inside the command-substitution loop
`emit_census` `:1394-1416` that buffers all rows before printing — hence **zero
rows**, including the healthy neighbours `a`/`c` (or `b`/`c` in arm L).

## Why the static guard misses it

- `guard_git_files()` `:546` enumerates only gitdir-relative names — `:548`:
  `for rel in config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates`.
- `guard_git_surface()` `:902-981` guards the repo `.git` dir, `commondir`,
  alternates and admin worktree registrations; nothing walks the work tree.
- `grep -n 'gitignore' tools/souji-census.sh` → **no matches**; `.gitattributes`
  appears nowhere either. The guard's own comment (`:543-545`, "a FIFO/device/
  socket is refused rather than opened or waited on") is true only for the
  gitdir list it names.

So the static surface is exactly the set git reads from the work tree:
`.gitignore` and `.gitattributes` in every directory `status` descends. Arm I
shows no tracked file is needed in the directory (git still descends to collapse
an untracked dir and reads its `.gitignore`); arm L shows the first sorted repo
suffices to lose the whole fleet.

Controls confirm the guard is statically correct where it looks:
FIFO at `info/exclude` → exit 2 (no open); FIFO at `info/attributes` → exit 0
with a soft `error` row for `b` and neighbours measured. A FIFO at a **tracked
path** does not hang (H: `dirty=1`), and XDG global ignore/attribute FIFOs are
neutered to `/dev/null` by `status_info_file`'s `[ -f ]` test — the hang class
is specifically the work-tree ignore/attributes files.

## Process containment (fixture-relevant)

Every hanging arm was cleared by GNU `timeout -k 2 20`, which signals the
process group: after return, `ps` sweep and `/proc/*/cwd` scan found **zero**
survivors in all arms (A, B, C, I, L included). `fifo_open` is interruptible, so
SIGTERM to the group is sufficient for this block class; the SIGKILL-after-2 s
fallback is not needed for it (harmless as belt-and-braces). This supports the
C1 fixture contract: a `start_new_session=True` subprocess + `killpg(...)` on
timeout leaves 0 blocked processes, and today's host residue is a harness bug,
not an unavoidable property of the hang.

`set -m` design check (bash 5.3.20): a `set -m` async child gets its own pgid
equal to `$!` (observed `pid=pgid=693508` vs shell pgid 3092); `kill -TERM --
-$pid` → `wait` rc 143, **no** job-control notice on the script's stderr. The
C1 watchdog's `set -m` fork + group kill will not pollute the
`souji-census: repo-timeout <N>s <repo>` stderr contract.

## Verdict

**C1's "race only" premise is false.** The bug is a static, deterministic hang
in four work-tree configurations, reproducible with two shell commands and no
shim. The `.git/info/attributes` race is one instance of a wider class; the
other members need no race at all.

The mandated C1 fix (per-repo watchdog, error row, exit 0) restores fleet
operability, but:
- at base there is **no bound at all** (`--repo-timeout` does not exist in this
  script; `grep -n repo-timeout` → no matches), so the static hang is unbounded;
- with the default 600 s bound, every statically-poisoned repo still parks a
  git process blocked in `fifo_open` for up to the bound before the watchdog
  fires — fleet operability holds, but the causal class remains.

**Smallest fix (complement, not replacement, for C1):** close the static class
before `count_dirty` (`:1291`) with one bounded pre-check over the repo tree:

```
find -P "$repo" \( -name .gitignore -o -name .gitattributes \) \
     \( -type p -o -type l \) -print0
```

then `stat -L -c '%F'` each hit (a symlink→FIFO also blocks git), and degrade to
the existing soft `error` row (`emit_soft_diag` + `…\terror`) when any resolves
to FIFO/socket/device. Per-name stats, not per-file: the census already walks
the tree once in `newest_mtime` (`:1156`), so an equivalent guard folded into
that pass costs nothing extra if `newest_mtime` is moved before `count_dirty`.
This keeps the watchdog as the backstop for anything the lstat guard cannot
predict (post-guard swap).

## Remaining unknowns

- Whether the live fleet under `/home/vgpnk/Projects/shokunin` currently
  contains any work-tree FIFO/device `.gitignore`/`.gitattributes` — not swept
  (probe rule forbids tree-wide searches; host residue file shows only
  `.git/info/*` and status fixtures).
- Static FIFO behaviour inside a *linked worktree* (`.git` file + admin dir) was
  not probed; same dir.c reader, expected identical, unverified.
- `core.excludesFile`/`core.attributesFile` pointing at a FIFO: code-read only
  (`status_info_file` `:1050-1054` returns unverifiable on non-regular target);
  not executed.
- Whether `git status --untracked-files=no` would still open a root
  `.gitattributes`; moot for the census (it forces `--untracked-files=normal`
  at `:1124`), untested.

## Commands run (abridged)

- `git -C <lane> show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh > /var/tmp/souji-r18-ScoutWorktreeFifo/census.sh`; `sha256sum` as above.
- Harnesses `/var/tmp/souji-r18-ScoutWorktreeFifo/run-arms.sh` and `run-extra.sh` (verbatim in Appendices A/B).
- Per arm: `env -u … HOME=<empty> timeout -k 2 20 bash …/census.sh --root <root>` → rc/rows/stderr/ps as tabulated.
- Pure git: `env -u XDG_CONFIG_HOME HOME=<empty> timeout -k 1 5 git -C <repo> status --porcelain` → rc 124 for A/B/C/I/F, rc 0 for H.
- Cleanup: workspace deleted after capture; `ps` sweep confirms no leftover processes.

## Appendix A — run-arms.sh (verbatim)

```bash
#!/usr/bin/env bash
# Static (no-race) FIFO probe for souji-census at b576341.
# Every FIFO exists before any census/git command starts.
set -u
W=/var/tmp/souji-r18-ScoutWorktreeFifo
H=$W/home
CENSUS=$W/census.sh
mkdir -p "$H"
printf '== host ==\n'
git --version
printf 'HOME=%s\n' "$H"

mkroot() { # $1 arm dir
  local d=$1 r
  mkdir -p "$d/root"
  for r in a b c; do
    git -c init.defaultBranch=master init -q "$d/root/$r"
    printf '%s\n' "$r" >"$d/root/$r/tracked.txt"
    mkdir -p "$d/root/$r/sub"
    printf '%s\n' "$r" >"$d/root/$r/sub/tracked.txt"
    git -C "$d/root/$r" -c user.name=t -c user.email=t@e add tracked.txt sub/tracked.txt
    git -C "$d/root/$r" -c user.name=t -c user.email=t@e -c commit.gpgsign=false \
      -c core.hooksPath=/dev/null commit -q -m base
  done
}

arm() { # $1 name, $2 mutation command
  local name=$1 mut=$2 d
  d=$W/arm-$name
  rm -rf "$d"
  mkroot "$d"
  eval "$mut"
  printf '\n===== arm %s =====\n' "$name"
  printf 'setup: %s\n' "$mut"
  (
    cd "$d" || exit 9
    env -u XDG_CONFIG_HOME -u GIT_DIR -u GIT_WORK_TREE -u GIT_CONFIG_GLOBAL \
      -u GIT_CONFIG_SYSTEM -u GIT_CONFIG_NOSYSTEM HOME="$H" \
      timeout -k 2 20 bash "$CENSUS" --root "$d/root" \
      >"$d/out.tsv" 2>"$d/err.txt" &
    local bg=$!
    sleep 3
    ps -eo pid,ppid,pgid,stat,wchan:40,args | grep -F "$d" | grep -v grep \
      >"$d/ps-during.txt" || true
    wait "$bg"
    printf '%s\n' "$?" >"$d/rc"
  )
  sleep 0.5
  printf 'rc=%s\n' "$(cat "$d/rc")"
  printf -- '-- rows --\n'
  cat "$d/out.tsv" 2>/dev/null
  printf -- '-- stderr --\n'
  cat "$d/err.txt" 2>/dev/null
  printf -- '-- ps during (3s, wchan) --\n'
  cat "$d/ps-during.txt" 2>/dev/null
  printf -- '-- survivors after timeout --\n'
  ps -eo pid,ppid,pgid,stat,wchan:40,args | grep -F "$d" | grep -v grep || printf '(none)\n'
  # any process whose cwd is still inside the arm dir
  local p cwd
  for p in /proc/[0-9]*; do
    cwd=$(readlink "$p/cwd" 2>/dev/null) || continue
    case "$cwd" in
      "$d"|"$d"/*) printf 'cwd-orphan %s cwd=%s cmd=%s\n' "${p#/proc/}" "$cwd" \
        "$(tr '\0' ' ' <"$p/cmdline" 2>/dev/null)" ;;
    esac
  done
}

# control, no FIFO: fresh repos only
arm D-none ': :'
# case 1: work-tree .gitignore is a FIFO
arm A-wt-gitignore 'mkfifo "$d/root/b/.gitignore"'
# case 2: work-tree .gitattributes is a FIFO
arm B-wt-gitattributes 'mkfifo "$d/root/b/.gitattributes"'
# case 3: nested dir .gitignore is a FIFO
arm C-sub-gitignore 'mkfifo "$d/root/b/sub/.gitignore"'
# stated control: .git/info/exclude replaced after creation by a plain file
arm E-exclude-plain ': >"$d/root/b/.git/info/exclude"'
# static guard probes (FIFO present before the run, no race)
arm F-info-exclude-fifo 'rm -f "$d/root/b/.git/info/exclude"; mkfifo "$d/root/b/.git/info/exclude"'
arm G-info-attrs-fifo 'mkfifo "$d/root/b/.git/info/attributes"'

printf '\n===== pure git attribution =====\n'
for name in A-wt-gitignore B-wt-gitattributes C-sub-gitignore F-info-exclude-fifo G-info-attrs-fifo; do
  d=$W/arm-$name
  env -u XDG_CONFIG_HOME HOME="$H" timeout -k 1 5 git -C "$d/root/b" status --porcelain \
    >"$d/git-status.out" 2>"$d/git-status.err"
  rc=$?
  printf '%s: git status rc=%s rows=%s err=%s\n' "$name" "$rc" \
    "$(wc -l <"$d/git-status.out")" "$(tr '\n' '|' <"$d/git-status.err")"
done
```

## Appendix B — run-extra.sh (verbatim)

```bash
#!/usr/bin/env bash
# Extra static FIFO surfaces + guard sanity, b576341 census.
set -u
W=/var/tmp/souji-r18-ScoutWorktreeFifo
H=$W/home
CENSUS=$W/census.sh

mkroot() {
  local d=$1 r
  mkdir -p "$d/root"
  for r in a b c; do
    git -c init.defaultBranch=master init -q "$d/root/$r"
    printf '%s\n' "$r" >"$d/root/$r/tracked.txt"
    mkdir -p "$d/root/$r/sub"
    printf '%s\n' "$r" >"$d/root/$r/sub/tracked.txt"
    git -C "$d/root/$r" -c user.name=t -c user.email=t@e add tracked.txt sub/tracked.txt
    git -C "$d/root/$r" -c user.name=t -c user.email=t@e -c commit.gpgsign=false \
      -c core.hooksPath=/dev/null commit -q -m base
  done
}

arm() {
  local name=$1 mut=$2 d
  d=$W/arm-$name
  rm -rf "$d"
  mkroot "$d"
  eval "$mut"
  printf '\n===== arm %s =====\nsetup: %s\n' "$name" "$mut"
  (
    cd "$d" || exit 9
    env -u XDG_CONFIG_HOME -u GIT_DIR -u GIT_WORK_TREE -u GIT_CONFIG_GLOBAL \
      -u GIT_CONFIG_SYSTEM -u GIT_CONFIG_NOSYSTEM HOME="$H" \
      timeout -k 2 20 bash "$CENSUS" --root "$d/root" \
      >"$d/out.tsv" 2>"$d/err.txt" &
    bg=$!
    sleep 3
    ps -eo pid,ppid,pgid,stat,wchan:40,args | grep -F "$d" | grep -v grep \
      >"$d/ps-during.txt" || true
    wait "$bg"
    printf '%s\n' "$?" >"$d/rc"
  )
  printf 'rc=%s\n-- rows --\n' "$(cat "$d/rc")"
  cat "$d/out.tsv" 2>/dev/null
  printf -- '-- stderr --\n'
  cat "$d/err.txt" 2>/dev/null
  printf -- '-- ps during --\n'
  cat "$d/ps-during.txt" 2>/dev/null
  printf -- '-- survivors --\n'
  ps -eo pid,ppid,pgid,stat,wchan:40,args | grep -F "$d" | grep -v grep || printf '(none)\n'
}

# H: tracked path becomes a FIFO (index says regular; worktree object swapped)
arm H-tracked-fifo 'rm -f "$d/root/b/tracked.txt"; mkfifo "$d/root/b/tracked.txt"'
# I: untracked dir with no tracked files, its .gitignore is a FIFO
arm I-untracked-dir-fifo 'mkdir -p "$d/root/b/untracked-dir"; mkfifo "$d/root/b/untracked-dir/.gitignore"'
# J/K: guarded gitdir files as FIFO, sanity only
arm J-index-fifo 'rm -f "$d/root/b/.git/index"; mkfifo "$d/root/b/.git/index"'
arm K-config-fifo 'rm -f "$d/root/b/.git/config"; mkfifo "$d/root/b/.git/config"'
# L: worktree .gitignore FIFO in repo a (first in sort order) instead of b
arm L-a-gitignore 'mkfifo "$d/root/a/.gitignore"'

printf '\n===== pure git attribution (extra) =====\n'
for name in H-tracked-fifo I-untracked-dir-fifo; do
  d=$W/arm-$name
  env -u XDG_CONFIG_HOME HOME="$H" timeout -k 1 5 git -C "$d/root/b" status --porcelain \
    >"$d/git-status.out" 2>"$d/git-status.err"
  rc=$?
  printf '%s: git status rc=%s rows=%s err=%s\n' "$name" "$rc" \
    "$(wc -l <"$d/git-status.out")" "$(tr '\n' '|' <"$d/git-status.err")"
done

printf '\n===== global leftover sweep =====\n'
ps -eo pid,ppid,pgid,stat,wchan:40,args | grep -F "$W" | grep -v grep || printf '(none)\n'
```
