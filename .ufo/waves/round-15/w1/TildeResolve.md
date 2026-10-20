# TildeResolve: critic, round 15 w1 (C1 operability, calibration)

## Status and evidence class

- **Design-only against the repair contract.** At report time (2026-10-20T05:24-03:00), `tools/souji-census.sh` was still the round-14 snapshot `#EAEA` (mtime 04:56:30, 1539 lines). `guard_git_config` still refuses on key presence alone (L500-506). ConfigRepair had not landed. `tests/fixtures/r15-census-config.py` did not exist.
- **Code inspection.** I read census L59-143, L146-703 and L704-841, plus `tests/fixtures/r14-census-boundary.py` (HOME handling only).
- **Primary source: git v2.55.0**, the host version (`git --version` = 2.55.0). Files were fetched read-only from `raw.githubusercontent.com/git/git/v2.55.0/` into `/var/tmp/tilde-v2550-*` and removed afterwards: `path.c`, `config.c`, `environment.c`, `abspath.c`, `builtin/config.c`, and `repo-settings.c` (that last one was grepped only).
- **Exercised evidence: none.** I ran no git, census, fixture or probe. Claims about git behaviour come from reading its source. Propagation steps are marked `[INFERENCE]` where they apply.
- **Not touched:** `~/.omp/agent` beyond the skill, `census/operator-sweep-*`, and every sibling or fleet file. Tool installs and updates: none (only `curl` and `jq`, already present).

## Process deviation (disclosed after the parent's no-query reminder)

- **Two recursive greps ran over the whole lane root** before the reminder arrived, and could have traversed `census/operator-sweep-20261019/`:
  - (1) `grep` pattern `HOME|expanduser|home_dir|includeIf|include\.path|tilde|~/`, path `/home/vgpnk/Projects/shokunin/souji-shokunin`
  - (2) `grep` pattern `value-blind|rejected-harmed|key-only`, same path
- **Neither call returned a match under `census/operator-sweep-*`**, and no file from it was opened, copied, edited or hashed. Calls (1) and (2) are not repeated.
- **`git --version` was executed once** to pin the source tag (output `2.55.0`). It was a version query, not a probe of any repository.
- Upstream sources were also fetched with `curl` to `/var/tmp/tilde-*`. Those files were deleted after reading. None of this is acceptance evidence.

## Git ground truth (v2.55.0)

| # | Fact | Source |
|---|---|---|
| G1 | `include.path` values are expanded by `interpolate_path(path, 0)`. If expansion returns NULL, that is an `error()` | config.c:153-155 |
| G2 | `~` and `~/…` use **raw** `getenv("HOME")`, with no realpath and no normalisation. **Unset HOME gives NULL.** `~user/…` uses `getpwnam(user)->pw_dir`, never `$HOME`; an unknown user gives NULL. `%(prefix)/…` gives `system_path()` | path.c:698-731, :706-707, :714-716, :726-728 |
| G3 | Relative paths are checked **after** expansion. They are joined to the **unresolved directory string** of the including file (`find_last_dir_sep(kvi->filename)`). The kernel then resolves the joined string physically | config.c:162-175 |
| G4 | `access_or_die(path, R_OK, 0)`: ENOENT/ENOTDIR silently skip the include. Any other errno (for example EACCES) **dies**. Depth > 10 dies | config.c:177-182 |
| G5 | A callback error such as G1 breaks the parse. For file sources the default error action is DIE, so git dies with "bad config line" | config.c:1134-1135, :1147, :1169-1171, :1393; `[INFERENCE]` repo config uses the default action (config.c:2302-2315) |
| G6 | `includeIf "gitdir:~…"` patterns use `interpolate_path(pat, 1)`, which **realpaths HOME**. HOME="" dies ("empty string is not a valid path"). A HOME with a missing non-final component dies ("Invalid path"). Unset HOME leaves the pattern literal, prefixed with `**/` | config.c:207-212, :227-228; path.c:717-718; abspath.c:89-91, :130-134, :318-327 |
| G7 | A relative `./` includeIf base is `realpath(kvi->filename)`, so it **resolves the leaf symlink**. That differs from G3 | config.c:214-226 |
| G8 | `core.excludesFile` and `core.attributesFile` are parsed eagerly through `git_config_pathname` for every config entry. An unexpandable `~` **dies** (`failed to expand user dir`). The `:(optional)` prefix applies only to pathname keys | environment.c:334-336, :463-465; config.c:1316-1319 |
| G9 | `core.hooksPath` is read lazily from the configset, and the last value wins (`repo_config_get_pathname`). The census `-c core.hooksPath=/dev/null` therefore wins, and the local `~` value is never expanded | repo-settings.c:205-209; path.c:400-401 |
| G10 | `git config --type=path` calls `git_config_pathname`. It strips `:(optional)` and stats the expanded path when the prefix is present | builtin/config.c:343-360 |
| G11 | `GIT_CONFIG_GLOBAL` set: neither `~/.gitconfig` nor XDG config is consulted. HOME matters only for values that are expanded | config.c:1525-1533 |

## Findings

### T1: HIGH (operability + calibration). Unset HOME: a "neutralized" or admitted value still makes git die, and the census emits false zeros

- **Counterexample:** run `env -u HOME souji-census.sh --root F`, where fleet F contains repo R with `core.excludesFile = ~/x` (or `include.path = ~/x`).
  - **Under the contract assumption** "existing status neutralizations count" (census L710-712 passes `-c core.excludesFile=/dev/null`): the local entry is parsed before the command-line entry, so `git_config_pathname` dies (G8). For an include, G1→G5 also die.
  - **Effects on the row:**
    - `count_worktrees` gives `0` (L688 `|| true`).
    - `count_unpushed` gives `0` (L698/L702 `|| printf '0'`).
    - Only `count_dirty` gives `unverifiable` (L716-718).
  - **Result:** a row claiming 0 worktrees and 0 unpushed commits. That is false reassurance and false provenance.
- **Also:** HOME **set but empty** turns `~/x` into `/x`, which is absolute and does not die. Census L216 already skips an empty HOME when building protected roots. An expansion helper written as `${HOME:-…}`, or with a passwd fallback, would guard a different file from the one git opens.
- **Also:** a **relative HOME** (`HOME=rel`) makes `~/x` expand to `rel/x`. That is then based on the config directory (G3), not on `$PWD` the way `lexical_abs` (L169-175) would base it.
- **Also:** under `set -u` (L108), a bare `$HOME` in new code aborts the whole fleet with exit 1. Every use must test `${HOME+x}`.
- **Smallest correction:**
  1. Expand exactly as G2 does, from `${HOME+x}` and the raw `$HOME`.
  2. When expansion would fail, refuse that repository: HOME unset with a `~`/`~/` value, an unknown `~user`, or HOME="" or broken together with an `includeIf gitdir:~` pattern (G6).
  3. Keep `core.hooksPath` admitted even when unexpandable (G9).
  4. Treat `core.excludesFile` and `core.attributesFile` as neutralized **only when expansion succeeds** (G8).
  5. Prefer a per-row `config-unexpandable` flag with blank counts over a fleet-wide `protected_fail`. These are operability failures, not namespace failures, and a fleet abort harms the mixed-fleet goal.

### T2: HIGH (namespace, identity). `~user` is not `$HOME`

- **Counterexample:** the fixture or a poisoned run sets `HOME=$T/home`. The repo has `include.path = ~vgpnk/store-link/auth.json`, and a pre-existing `/home/vgpnk/store-link` points to `.omp/agent`.
  - A naive helper `${v/#\~/$HOME}` checks `$T/homevgpnk/store-link/auth.json`. That path is absent, so the helper treats it as "git skips" and admits.
  - Git opens `/home/vgpnk/.omp/agent/auth.json` (G2).
  - The `.omp/agent` component-pair check (L286-288) never sees the store, because the literal value hides it behind the link.
- **Smallest correction:** resolve `~name` with `getent passwd name` field 6. This is the same NSS lookup git does. If the lookup fails, refuse. Then pass the result through `guard_target`, which follows the hop and refuses at the folded `.omp/agent` candidate (L377-384). Rejecting `~name/` outright is an acceptable, rarer alternative.
- **`%(prefix)/`** goes to git's install prefix (G2). It must be refused or resolved to `git --exec-path`'s prefix. Never treat it as a relative literal.

### T3: HIGH (namespace). Lexical normalisation of a relative include bypasses a symlinked parent

- **Counterexample:** the fleet has `F/hop -> $HOME/.omp/agent/sessions`. R's `.git/config` contains `include.path = ../../hop/../auth.json`.
  - `lexical_abs` (L169-186) collapses this to `F/auth.json`, which is unprotected and absent, so it would be admitted.
  - The kernel follows `hop`, then `..`, and reaches `$HOME/.omp/agent/auth.json` (G3).
- **Correct primitive already exists:** `guard_target` (L422-426 → `resolve_guarded` with `allow=1`, L337-411) folds each hop and refuses at the protected candidate before any lstat below the store.
- **Smallest correction:** join `<including-file directory string>/<expanded value>` and call `guard_target` on the raw join. **Never** call `lexical_abs` or `readlink -m` on include values. The base for top-level repo config is the resolved gitdir that `guard_git_config` already receives (L493). Physical resolution makes it equivalent to git's string.

### T4: MEDIUM-HIGH (namespace). Nested-include base is the dirname of the *link*, not of the resolved file

- **Counterexample:**
  - R's config has `include.path = ../inc-link`, where `R/inc-link -> $T/decoy/real`.
  - `real` contains `[include] path = n`.
  - Git bases `n` on the dirname of the joined string `R/.git/../`, which is `R/` (G3). `R/n` is a symlink into `$HOME/.omp/agent/auth.json`.
  - A helper that recurses from `dirname(resolved target)` checks `$T/decoy/n`. That is absent, so it admits.
- **Smallest correction:** the nested base = `guard_target "${joined%/*}"`, the parent of the **unresolved** joined string. Do not take `dirname` of the resolved file.
- **Contrast:** includeIf `./` patterns use `realpath(file)` (G7). The two rules must stay separate.

### T5: MEDIUM (operability + calibration). Readability and type decide whether git dies, independent of namespace

- G4 means an EACCES include target makes git die. An example is `include.path = ~root/x` for a non-root user, since `/root` is 0700.
- `resolve_guarded` passes such paths (L385 `[ -L ]` is just false).
- **Correction:** after the guard, a missing target means admit with no recursion. Any other target must be readable, regular and have nlink 1 before it is read with `git config --file T --no-includes`. The hardlink rule mirrors L480-486. Otherwise refuse with `git-config-include-unreadable` or `-nonregular`.
- Depth and cycle handling belongs to IncludeCycle; FIFO handling belongs to SpecialConfig.

### T6: MEDIUM (namespace regression surface). Admitting includes opens a new content-read path into a symlink-relocated store

- The header's documented residual (L93-99, L257-259) is that a store relocated by a symlink outside `.omp/agent` naming is not detected.
- Before r15, no repo config could make git open such a file, because all includes were refused. After r15, `include.path = /data/omp-agent/auth.json` passes every guard.
- The same applies to `HOME=/data/omp-agent` with `~/x` when `PI_CODING_AGENT_DIR` is unset. Compare r14 case_09 (`HOME=AGENT`), which the synthetic `.omp/agent` pair still catches.
- **Smallest correction (L1 tradeoff):**
  - Admit include targets that resolve inside the repo's own worktree or gitdir. Common benign forms such as `../.gitconfig` are covered.
  - Also admit missing targets, because git skips them.
  - Refuse only *existing* out-of-repo targets with an effect-based reason.
  - Otherwise update the header so the residual explicitly covers include targets.

### T7: LOW-MEDIUM. Value extraction must not delegate to git expansion unsafely

- `git config --type=path` (G10) is an exact expander, but it stats `:(optional)` targets before the guard runs. Because `include.path` does **not** honour `:(optional)` (G1 calls `interpolate_path` directly), it would also check a different file.
- Use `--no-includes --null --get-all include.path` (`-z` keeps embedded newlines intact) and expand in bash.
- Never use `--includes`, because it would make git read the targets before the guard.

## Acceptance needed (ConfigFixture / L1; synthetic `/var/tmp` HOME only)

| id | setup | expect (repaired) | r14 baseline |
|---|---|---|---|
| TR-1 | `env -u HOME`; R has `include.path=~/inc` | refuse or row-flag `config-unexpandable`; **never** a row with 0/0 counts | exit 2 (key) |
| TR-2 | `env -u HOME`; R has `core.excludesFile=~/x` | same as TR-1 (G8) | exit 2 |
| TR-3 | `env -u HOME`; R has `core.hooksPath=~/x` | admitted; row equals control row (G9) | exit 2 → **harm repaired** |
| TR-4 | `HOME=""`; `include.path=~/absent-souji` → `/absent-souji` | admitted; row equals control | exit 2 → repaired |
| TR-5 | `HOME=""`; `includeIf "gitdir:~/nomatch/".path=x` | refuse/flag (git dies, G6) | exit 2 |
| TR-6 | HOME unset; same includeIf | admitted, no read (pattern literal) | exit 2 → repaired |
| TR-7 | `F/hop` → `$HOME/.omp/agent/sessions`; `include.path=../../hop/../auth.json` | exit 2 `credential-store`; trace shows no openat or stat under AGENT | exit 2 |
| TR-8 | nested `inc-link` → decoy, `R/n` → store (T4) | exit 2 `credential-store`; no store openat | exit 2 |
| TR-9 | `include.path=~nosuchuser-souji/x` | refuse/flag `config-unexpandable` | exit 2 |
| TR-10 | `include.path=$T/locked/x`, with `locked` mode 000 | refuse/flag `include-unreadable` | exit 2 |
| TR-11 | benign `include.path=../.gitconfig` (tracked, `[core] autocrlf=false`) plus a sibling plain repo | both rows emitted; R equals its no-include control | exit 2 / no TSV → **harm repaired, mixed fleet** |
| TR-12 | benign `~/.gitconfig.repo` in synthetic HOME (exists) and `~/absent` | admitted; equals control | exit 2 → repaired |

The r14 12-case fixture must still pass unchanged (namespace retention; NamespaceRetain owns this).

## Axes

- **Operability:** TR-3, TR-4, TR-6, TR-11 and TR-12 are the benign-preservation gains. T1, T5 and T6 are the regression traps the repair must not introduce.
- **Calibration:**
  - T1 false-zero rows.
  - T2, T3 and T4 guard a different file than git opens.
  - Header L85-91 and L93-99 must describe expansion and base rules, and every remaining refusal by its effect: "git would die" or "out-of-repo content read". Key presence must no longer be the stated reason.

## Final L1 commands (not run by this seat)

- `bash -n tools/souji-census.sh`; `shellcheck tools/souji-census.sh`
- `tools/souji-census.sh --selftest`
- `python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh` (namespace retention, unchanged)
- `python3 tests/fixtures/r15-census-config.py --tool <r14 baseline>` (red) and `--tool tools/souji-census.sh` (green), with cases TR-1..TR-12 present
- Static: `grep -nE 'HOME\+|getent passwd|%\(prefix\)|--no-includes|lexical_abs' tools/souji-census.sh`. Expect no `lexical_abs` on include values and a `${HOME+x}` test before any `~` expansion.
