STATUS: DONE — census git open(2) surface mapped on git 2.56.0: only `status` and `check-attr` open attributes/excludes; none of those opens carries `O_NONBLOCK`; `status` opens `.git/info/attributes` only when it must compare content, but opens `.git/info/exclude` and worktree `.gitignore` unconditionally. FIFO blocking reproduced in a synthetic repo and every process I started was reaped.

# ScoutGitOpens — which files each census git invocation opens (r18 W1)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `b576341`. Question answered for C1: per census git call, which files are opened, with which flags; and whether `status` opens `.git/info/attributes` only when it must compare content (touched file).

## Environment and method

- Host: Linux 7.2.11-arch1-1; git 2.56.0; strace 7.2; bash 5.3.20; Python 3.14.8. **No tool was installed or changed** (strace already present).
- Synthetic repos under `/var/tmp/souji-r18-ScoutGitOpens/` (deleted after the run). CWD was the parent dir, never the repo; every invocation used `git -C <abs-repo>` exactly as the census does.
- Repo contents: `tracked.txt`, `sub/note.md`, `.gitignore` (`*.tmp`), worktree `.gitattributes` (`*.md diff=md`), `.git/info/attributes` (`*.txt text eol=lf`), `.git/info/exclude` (`ignored-by-info.txt`); one commit. Two shapes:
  - **racy**: files written and committed in the same second (index timestamp == file mtime);
  - **pristine**: file mtimes set to 2020-01-01 before `git add`/`commit`, so the index is newer than every tracked file.
- Census env (from `tools/souji-census.sh:174-185`), with inherited `GIT_*` cleared:

```
GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 GIT_NO_LAZY_FETCH=1
GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false
GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null
```

- Trace wrapper: `strace -f -qq -e trace=openat -o <log> -- <argv>`. All opens below are `openat(AT_FDCWD, …)` by the single git process (no child processes were spawned in any non-probe run; `-f` showed one pid).
- Per-run census status argv (`tools/souji-census.sh:1122-1130`), with `$EX`/`$AT` set to the guarded paths or `/dev/null`:

```
git -C $R --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null \
  -c core.excludesFile=$EX -c core.attributesFile=$AT status --porcelain \
  --ignore-submodules=all --untracked-files=normal -- . \
  ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
  ':(exclude,glob)census/operator-sweep-*' ':(exclude,glob)census/operator-sweep-*/**' \
  ':(exclude,glob)**/census/operator-sweep-*'
```

`$R` below is the synthetic repo root.

## Opens per census call

### `git -C $R rev-parse --is-inside-work-tree` (`souji-census.sh:1280`)

| file | flags | result |
|---|---|---|
| `$R/.git/HEAD` (absolute) | `O_RDONLY` | OK — discovery validates HEAD |
| `.git/config` | `O_RDONLY` | OK |
| `.git/objects/info/alternates` | `O_RDONLY` | ENOENT |
| `/dev/null` | `O_RDWR` once | git runtime fd |
| `/dev/null` | `O_RDONLY` ×2 | global/system config scopes disabled |

No index, no attributes, no exclude.

### `git -C $R worktree list` (`:1000`) and `worktree list --porcelain` (`:1253`)

Same as rev-parse plus:

| file | flags | result |
|---|---|---|
| `.git/HEAD`, `.git/refs/heads/main` | `O_RDONLY` | OK (main worktree HEAD) |
| `.git/worktrees` | `O_RDONLY\|O_NONBLOCK\|O_CLOEXEC\|O_DIRECTORY` | ENOENT |
| `.git/objects/pack/multi-pack-index`, `…/multi-pack-index-chain` | `O_RDONLY\|O_CLOEXEC` | ENOENT |
| `.git/objects/pack` | `O_RDONLY\|O_NONBLOCK\|O_CLOEXEC\|O_DIRECTORY` | OK |
| `.git/objects/<xx>` (short form only) | `O_RDONLY\|O_NONBLOCK\|O_CLOEXEC\|O_DIRECTORY` | OK |
| `.git/packed-refs` | `O_RDONLY` | ENOENT |

No index, no attributes, no exclude.

### `git -C $R for-each-ref --format='%(refname)' refs/remotes` (`:1006`)

rev-parse set plus `.git/refs/` (`O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY`, OK) and `.git/packed-refs` (`O_RDONLY`, ENOENT). No index/attributes/exclude.

### `git -C $R rev-list --count --branches` (`:1010`) and `… --branches --not --remotes` (`:1014`)

rev-parse set plus:

- `.git/refs/`, `.git/refs/heads/` (directory reads, `O_DIRECTORY|O_NONBLOCK|O_CLOEXEC`), `.git/refs/heads/main`;
- `.git/packed-refs`, `.git/info/grafts`, `.git/shallow` (plain `O_RDONLY`, ENOENT in the synthetic repo);
- `.git/objects/info/commit-graph`, `.git/objects/info/commit-graphs/commit-graph-chain`, `.git/objects/pack/multi-pack-index`, `…/multi-pack-index.d/multi-pack-index-chain` (`O_RDONLY|O_CLOEXEC`, ENOENT);
- `.git/objects/pack` (dir, `O_DIRECTORY|O_NONBLOCK|O_CLOEXEC`), one loose object (`O_RDONLY|O_CLOEXEC`);
- `--not --remotes` adds `.git/refs/remotes/`, `.git/refs/remotes/origin/` (dirs) and `.git/refs/remotes/origin/main`.

No index/attributes/exclude.

### `git -C $R config --get <key>` (`:1027`, once for `core.excludesFile`, once for `core.attributesFile`) and `git -C $R config -z --get-regexp '^filter\..*\.(clean|smudge|process)$'` (`:1069`)

| file | flags |
|---|---|
| `.git/config` | `O_RDONLY` (read twice per call: early parse + query) |
| every `include.path` target (tested with `.git/extra.cfg`) | `O_RDONLY`, absolute or relative to `.git/` |

No index/attributes/exclude. **Observed**: includes are followed by these measurement calls (`--no-includes` is only used in the guard parser at `:698`/`:751`).

### `git -C $R -c core.attributesFile=$AT ls-files -z --cached -- . …` (`:1085-1089`)

rev-parse set plus `.git/index` (`O_RDONLY`, OK). **No attributes/exclude/gitignore opens** — plain `ls-files` reads the index only.

### `git -C $R -c core.attributesFile=$AT check-attr -z --stdin filter` (`:1090-1091`, only reached when a `filter.*` driver exists, `:1069-1083`)

| file | flags | result |
|---|---|---|
| `.git/index` | `O_RDONLY` | OK (observed in every check-attr run) |
| `/etc/gitattributes` | `O_RDONLY` | ENOENT on this host |
| `$AT` target — `/dev/null`, or absolute `$R/.git/info/attributes` when configured | `O_RDONLY` | OK |
| `.gitattributes` (per directory of each input path) | `O_RDONLY\|O_NOFOLLOW` | OK |
| `.git/info/attributes` (native, always) | `O_RDONLY` | OK |
| `sub/.gitattributes` | `O_RDONLY\|O_NOFOLLOW` | ENOENT |

### `git … status --porcelain …` (`:1122-1130`)

**Clean, pristine repo, nothing stat-dirty** (no content compare; `-c …/dev/null` branch):

| file | flags | result |
|---|---|---|
| `.git/config` | `O_RDONLY` | OK (×3) |
| `.git/objects/info/alternates` | `O_RDONLY` | ENOENT |
| `.git/HEAD`, `.git/refs/heads/main`, `.git/packed-refs` | `O_RDONLY` | OK / OK / ENOENT |
| `.git/index` | `O_RDONLY` | OK |
| `.git/refs/` | `O_RDONLY\|O_NONBLOCK\|O_CLOEXEC\|O_DIRECTORY` | OK |
| commit-graph / multi-pack-index probes, `.git/objects/pack` (dir), loose objects | `O_RDONLY…` | as rev-list |
| `/dev/null` then `.git/info/exclude` | `O_RDONLY` | OK — **twice**: once `-c core.excludesFile`, once native |
| `.gitignore` | `O_RDONLY\|O_NOFOLLOW` | OK |
| `$R` and `sub/` | `O_RDONLY\|O_NONBLOCK\|O_CLOEXEC\|O_DIRECTORY` | OK |
| `.git/sequencer/todo` | `O_RDONLY` | ENOENT |

**No attributes file at all** — and no tracked file content is read.

**Any stat mismatch / racy entry** (content compare of a tracked path) adds, in this order:

```
openat(AT_FDCWD, "tracked.txt", O_RDONLY|O_CLOEXEC) = …
openat(AT_FDCWD, "/etc/gitattributes", O_RDONLY) = -1 ENOENT
openat(AT_FDCWD, "$AT", O_RDONLY) = …            # /dev/null, or absolute info/attributes
openat(AT_FDCWD, ".gitattributes", O_RDONLY|O_NOFOLLOW) = …
openat(AT_FDCWD, ".git/info/attributes", O_RDONLY) = …
openat(AT_FDCWD, "sub/.gitattributes", O_RDONLY|O_NOFOLLOW) = …
```

With `-c core.attributesFile=$R/.git/info/attributes` the same file is opened **twice** (absolute via the config value, then relative as native `$GIT_DIR/info/attributes`).

## Flags: `O_NONBLOCK` inventory

- **No non-directory open carries `O_NONBLOCK`.** Attributes, excludes, `.gitignore`, `.gitattributes`, `config`, include targets, `index`, refs, loose objects are all `O_RDONLY` (plus `O_CLOEXEC`/`O_NOFOLLOW` in places).
- `O_NONBLOCK` appears **only** on directory opens: `.git/refs/`, `.git/refs/heads/`, `.git/refs/remotes/…`, `.git/objects/pack`, `.git/objects/<xx>`, `.git/worktrees`, the worktree root `.`, and `sub/` — all with `O_DIRECTORY`, where the flag is inert.
- `O_NOFOLLOW` is used for per-directory `.gitattributes`/`.gitignore`; it blocks symlink following but **does not** prevent opening a FIFO. `.git/info/attributes` and `.git/info/exclude` are opened without `O_NOFOLLOW`.

## The conditional: when does `status` open `info/attributes`?

**It opens it only when it must compare content — but "must compare" is broader than a touched file.**

| repo state | `git status` | attributes opens | tracked content read |
|---|---|---|---|
| pristine, clean (index newer than files) | rc 0, empty | none | none |
| pristine, untracked file only | rc 0, `?? untracked.log` | none | none |
| touched tracked file (same content) | rc 0, empty | `/etc/gitattributes`, `$AT`, `.gitattributes`, `.git/info/attributes` | yes |
| same-size content change | rc 0, ` M tracked.txt` | same set | yes |
| racy index entries (written+committed same second) | rc 0, empty | same set | yes |

The racy case is why my first "clean" repo behaved like a touched one: an entry whose mtime equals the index timestamp is re-checked every run until the index is rewritten. So C1's "touch a tracked file" is a deterministic way to force the attribute path, not the only one.

**But `status` opens two other files unconditionally, even when clean:** `.git/info/exclude` (twice, `O_RDONLY`) and the root `.gitignore` (`O_RDONLY|O_NOFOLLOW`). Those are not gated on content comparison.

## FIFO confirmation (C1 premise)

Probes in fresh synthetic repos (`start_new_session=True`, `ps -eo pid,ppid,pgid,stat,wchan:32,args`, then `os.killpg(..., SIGKILL)`; regular file restored after each):

| repo state | FIFO at | result |
|---|---|---|
| pristine, clean | `.git/info/attributes` | **completed rc 0** (3 s budget) — lazy open confirmed |
| pristine, `tracked.txt` touched | `.git/info/attributes` | **blocked**; git state `S`, `wchan=wait_for_partner`; strace tail: `openat(AT_FDCWD, ".git/info/attributes", O_RDONLY` (unfinished) |
| pristine, clean | `.git/info/exclude` | **blocked**; tail: `openat(AT_FDCWD, ".git/info/exclude", O_RDONLY` (unfinished) |
| pristine, clean | `.gitignore` | **blocked**; tail: `openat(AT_FDCWD, ".gitignore", O_RDONLY\|O_NOFOLLOW` (unfinished) |
| pristine, `sub/note.md` touched | `sub/.gitattributes` | **blocked**; tail: `openat(AT_FDCWD, "sub/.gitattributes", O_RDONLY\|O_NOFOLLOW` (unfinished) |
| pristine | `.git/info/attributes` + census `check-attr` pipeline | **blocked**; tail: `/etc/gitattributes` ENOENT → `/dev/null` → `.gitattributes` `O_NOFOLLOW` → `.git/info/attributes` `O_RDONLY` (unfinished) |

`wait_for_partner` is the kernel wait in `open(2)` on a read-only FIFO with no writer. This is exactly the L1 repro's hang; the watchdog fix bounds it.

## Findings

**FO1 — holds (high confidence).** The blocking surface is confined to `status` and `check-attr`, and no attribute/exclude/config open uses `O_NONBLOCK`. Code: status argv `tools/souji-census.sh:1122-1130`; check-attr `:1090-1091`; env `:174-185`. Observed in every log: all such opens are `O_RDONLY` variants.

**FO2 — holds (high).** `status` opens `.git/info/attributes` only when a tracked entry needs content comparison. Clean pristine repo + FIFO at `info/attributes` → `git status` rc 0 in <3 s; touch → block in `openat`. So the L1 shim's "touch a tracked file" is load-bearing for the attributes vector. Caveat: racy-clean entries also force the comparison and can hang without any touch.

**FO3 — holds (high; simpler repro than C1's).** `.git/info/exclude` is opened by `status` **unconditionally** (clean tree, no touched file), twice: once via `-c core.excludesFile=$EX` and once natively. A FIFO there blocks `status` with no content compare at all. `guard_git_files` does inspect `info/exclude` (`:548`), so this needs the same post-guard swap, but it removes the shim's need to touch a file.

**FO4 — holds (high; unguarded, no race needed).** Worktree `.gitignore` (opened on every `status`) and `.gitattributes` (root and per-directory, opened on content compare) are **never inspected by the census** — `grep -n 'gitignore\|\.gitattributes' tools/souji-census.sh` → no match. A FIFO named `.gitignore` in a repo directory therefore passes every guard and hangs `status` today; no shim or swap race is required. `O_NOFOLLOW` does not help (a FIFO is not a symlink). A cloned repo cannot carry a FIFO, but the census runs over a live, mutable fleet.

**FO5 — holds (medium; new).** `/etc/gitattributes` is read by every attribute lookup (`check-attr`, `status` when comparing) as an absolute path outside the repo, and the census does **not** set `GIT_ATTR_NOSYSTEM=1` (`:174-185`). `GIT_CONFIG_NOSYSTEM`/`GIT_CONFIG_GLOBAL` do not cover attributes. Planting it requires root, but it is one cheap env line to close.

**FO6 — holds (medium).** Every config-reading call (`rev-parse`, `worktree list`, `for-each-ref`, `rev-list`, both `config` gets, `status`) follows `include.path` and opens the target (`O_RDONLY`, observed `.git/extra.cfg`). `guard_git_surface` validates include targets only before measurement (`cfg_soft` on non-regular/hardlinked targets, `:669-674`); a post-guard swap has the same TOCTOU property. The watchdog covers it; no extra work needed.

**FO7 — informational.** `rev-parse`, `worktree list`, `for-each-ref`, `rev-list`, and `config` open no index, attributes or exclude files; `ls-files` opens only `.git/index`. So a FIFO at those surfaces cannot hang the census; the hang set is exactly `status` and `check-attr`, both inside `census_one`.

## Smallest fix

1. The C1 contract's per-repo process-group watchdog is the right invariant and must wrap **the whole `census_one`**, not only the `status` line: `check-attr` (run first, when a filter driver exists) opens the same FIFO, and `status` blocks on `info/exclude`/`.gitignore` with no touched file. `emit_census` (`:1394-1416`) already loops over repos; fork each `census_one` under `set -m`, stdout to a private temp, SIGTERM the group at `--repo-timeout`/`SOUJI_CENSUS_REPO_TIMEOUT`, SIGKILL 2 s later, emit `<repo>\t0\t0\t0\t0\t\terror` + `souji-census: repo-timeout <N>s <repo>`, keep exit 0 (2 for protection refusal). Fixtures: `start_new_session=True` + `os.killpg(..., SIGKILL)` on timeout.
2. One line beside `GIT_NO_LAZY_FETCH=1` (`:183`): `export GIT_ATTR_NOSYSTEM=1` — removes the unguarded `/etc/gitattributes` read from `status` and `check-attr`.
3. Optional hardening, not a substitute: add root `.gitignore`/`.gitattributes` to the `guard_git_files` fixed list (`:548`) and treat a non-regular one as a soft `error` row. A per-directory scan is too expensive and still racy; the watchdog remains the invariant.

## Exact commands run (synthetic only)

Setup per repo (Python `subprocess`, cwd `/var/tmp/souji-r18-ScoutGitOpens`):

```
git init -q -b main <repo>
git -C <repo> config user.name scout
git -C <repo> config user.email scout@example.invalid
# write files, then for pristine repos: os.utime(<file>, (1577836800, 1577836800))
git -C <repo> add -A
git -C <repo> -c commit.gpgsign=false commit -q -m init
git -C <repo> update-ref refs/remotes/origin/main <head>   # for the --remotes variant
```

Traced calls (each `strace -f -qq -e trace=openat -o <log> -- …`, census env above):

```
git -C $R rev-parse --is-inside-work-tree
git -C $R worktree list
git -C $R worktree list --porcelain
git -C $R for-each-ref --format=%(refname) refs/remotes
git -C $R rev-list --count --branches
git -C $R rev-list --count --branches --not --remotes
git -C $R config --get core.attributesFile        # and core.excludesFile
git -C $R config -z --get-regexp '^filter\..*\.(clean|smudge|process)$'
git -C $R -c core.attributesFile=$AT ls-files -z --cached -- . <5 excludes>
git -C $R -c core.attributesFile=$AT check-attr -z --stdin filter   # stdin = ls-files output
git -C $R --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null \
  -c core.excludesFile=$EX -c core.attributesFile=$AT status --porcelain \
  --ignore-submodules=all --untracked-files=normal -- . <5 excludes>
```

with `$AT`/`$EX` = `/dev/null` and = `$R/.git/info/attributes` / `$R/.git/info/exclude`, on pristine and racy repos, clean / untracked / touched / same-size-modified / racy states.

FIFO probes (extra, same synthetic dirs): `os.unlink(path); os.mkfifo(path)`, optional `os.utime(tracked, None)`, `subprocess.Popen([...strace..., git … status], start_new_session=True)`, wait 2–3 s, `ps -eo pid,ppid,pgid,stat,wchan:32,args`, `os.killpg(p.pid, SIGKILL)`, restore the regular file. One probe cell hit the Eval 30 s cap after the third probe started; I then found the two blocked probe processes (`strace` + `git check-attr`, wchan `wait_for_partner`), killed their process group, and verified the process list empty before continuing.

## Cleanup and process audit

- After every probe: `ps -eo … | grep /var/tmp/souji-r18-ScoutGitOpens` → empty. Final check empty as well.
- `/var/tmp/souji-r18-ScoutGitOpens/` removed after extracting the evidence above (10 repos, ~38 strace logs). No file outside `/var/tmp` was written except this report.
- No `jj`, no git write outside the synthetic `/var/tmp` repos, no census/verify/quarantine tool run against any real directory.

## Remaining unknowns

- All observations are on git 2.56.0. Older git may differ (e.g. `O_NOFOLLOW` hardening of attr reads landed in 2.42); the fleet runs host git, so this is the relevant build, but I did not audit other hosts.
- `GIT_ATTR_NOSYSTEM=1` is documented to skip the system attributes file; I did not run the variant to observe the `/etc/gitattributes` open disappear.
- Whether SIGTERM (not KILL) reliably terminates git blocked in `open(2)` on this build: default-disposition reasoning says yes, and the 2 s SIGKILL backstop makes it moot; not separately probed.
- I did not enumerate every possible subdirectory `.gitignore` traversal (`status` reads them while walking untracked dirs); root `.gitignore` is the unconditional one, subdirectory ones are conditionally read during the untracked scan. The hang class is the same.
