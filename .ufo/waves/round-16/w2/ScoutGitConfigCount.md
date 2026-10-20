# ScoutGitConfigCount-4 — GIT_CONFIG_COUNT vs `--file` and in-repo `--get`

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Target `tools/souji-census.sh` bytes `64a60fd0b0ed…` (sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`), 1877 lines — matches the C1 digest.
Axes: operability of the neutralizer (does it actually reach every git call), fidelity of the header claim, and non-pollution of the config guard's own parse.

## Question
Do `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_<n>`/`GIT_CONFIG_VALUE_<n>` apply to `git config --file F --list` and to `git config --get` inside a repo, and where do they sit relative to repo config?

## Observed (git 2.56.0, host, 2026-10-20)
Test values were injected as `zzprobe.key=probeval` and as `core.bare` (a key the lane's `.git/config` already sets to `false`, line 4).

1. **`--file F --list` excludes the env pairs.** `GIT_CONFIG_COUNT=1 … git config --file $LANE/.git/config --list | grep zzprobe` → no output, `rc=1`; with `--show-origin` every row is `file:…/.git/config`, and `| grep -c fsmonitor` = `0`. So the guard's record scan at `tools/souji-census.sh:621` sees exactly the file's own records.
2. **`--file F --get` excludes them too.** `--get zzprobe.key` → `rc=1`. With the key present in the file (`core.bare`) and env set to `true`/`zzz`, `--file … --get core.bare` → `false` (the file value). Env never wins inside a `--file` read.
3. **In-repo `--get` includes them, with highest precedence.** Repo sets `core.bare=false`; `GIT_CONFIG_COUNT=1 …=core.bare VALUE_0=true git -C $LANE config --get core.bare` → `true`. `--get-all core.bare` → `false` then `zzz` (file first, command scope last = winner).
4. **`--get-regexp` merges them.** `git -C $LANE config --get-regexp '^core\.'` lists `core.bare false` and `core.fsmonitor false` (env key canonicalized lowercase, `core.hookspath`).
5. **Pairs are parsed even when not applied.** A malformed pair (`GIT_CONFIG_COUNT=2` with only `GIT_CONFIG_KEY_0`) makes even `git config --file … --list` and `git -C … rev-parse --git-dir` abort: `fatal: unable to parse command-line config`, `rc=128`.
6. **`--show-scope` mislabels `--file` rows.** `git config --file F --list --show-scope` prints `command<TAB>…` for every file row; `--show-origin` is the reliable label. This is cosmetic here — `scan_config_file` uses `--list -z` with neither flag.

## Relation to the script
- `tools/souji-census.sh:152-163` exports `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_COUNT=2` + `core.fsmonitor=false`, `core.hooksPath=/dev/null`, after `unset`-ing every inherited `GIT_*` (`:146-151`). No git command executes before that block (only comments match `git ` at lines <162), and the selftest re-entry at `:1613-1615,1724-1755` uses `env -u GIT_DIR` only, so the child inherits and re-exports the same pairs.
- Guard parse `:618,621` (`git config --file "$cfg" --no-includes --list -z`) and the bool probe `:671` are `--file` reads → env pairs are neither listed nor returned (Observed 1–2). The two synthetic keys therefore **cannot mask or impersonate** a repository's own `core.fsmonitor`/`core.hooksPath` during the guard scan.
- Repo-scoped reads `:944` (`git -C "$wt" config --get core.excludesFile|core.attributesFile`, call sites `:1023,1025`) and `:986` (`--get-regexp '^filter\..*\.(clean|smudge|process)$'`) **do** include command scope (Observed 3–4). No defect today: the injected keys are `core.*` and the filter regexp is anchored at `^filter\.`, and `core.excludesFile`/`core.attributesFile` collide with neither. A future query of `core.fsmonitor`/`core.hooksPath` through the `:944` helper would silently read `false`/`/dev/null` instead of the repo's value.
- The `-c` side-claim is real: status at `:1035-1037` passes `-c core.fsmonitor=false -c core.hooksPath=/dev/null`; docs say `-c` outranks the env pairs, so the two mechanisms agree rather than conflict.

## Verdict — holds
Docs match behavior; the census usage is correct on every current call site. Caveat on wording, not behavior: header `:111-113` says every call "carries" the pairs. For `--file` reads they are *parsed but not applied* (Observed 5 shows they are still validated), so "carries" should not be read as "affects the guarded file's values".

Smallest fix (optional hardening, no behavior change): a one-line comment at `:944`/`:986` — "repo-scoped `config --get` includes command scope; never probe core.fsmonitor/core.hooksPath here — use `--file` for the repository's own value." Not applied (leaf, read-only).

## Citations (accessed 2026-10-20)
- https://git-scm.com/docs/git-config (latest 2.56.0, 2026-09-28), `--file <config-file>`: "For reading options: read only from the specified file rather than from all available files." — matches Observed 1–2.
- Same page, `GIT_CONFIG_COUNT`: "These environment variables will override values in configuration files, but will be overridden by any explicit options passed via `git` `-c`." — matches Observed 3–4 and the `-c` status path.
- Same page, `GIT_CONFIG_COUNT`: "Any missing key or value is treated as an error." — matches Observed 5 (abort even for `--file`).
- Same page, reading default: values "are read from the system, global and repository local configuration files by default, and options … `--file` can be used to tell the command to read from only that location."
- Local corroboration: `man git-config` (git 2.56.0) lines 440–448, 510–512, identical wording.

## Remaining unknowns
- Behavior of a repo whose `core.fsmonitor` is a *command* was not exercised end-to-end (that needs a writable throwaway repo, outside this read-only lane); precedence was proven at the config layer (`--get`/`--get-all`), and index readers resolve through the same config sequence — `[INFERENCE]` for the final step.
- `config.worktree` values under `extensions.worktreeConfig=true` were not separately exercised; docs place command scope last in the same merge, so the conclusion is unchanged by inspection.

## Commands
```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && sha256sum tools/souji-census.sh && wc -l tools/souji-census.sh
git --version; man git-config 2>/dev/null | col -b | grep -n -i -A6 'GIT_CONFIG_COUNT' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'GIT_CONFIG\|GIT_NO_LAZY\|git config\|--file\|--get\|--list\|GIT_CEILING\|GIT_OPTIONAL' tools/souji-census.sh | head -80
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=zzprobe.key GIT_CONFIG_VALUE_0=probeval git config --file /etc/gitconfig --list --show-origin | grep -i zzprobe; echo "file-list rc=$?"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=zzprobe.key GIT_CONFIG_VALUE_0=probeval git config --file /etc/gitconfig --get zzprobe.key; echo "file-get rc=$?"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=zzprobe.key GIT_CONFIG_VALUE_0=probeval git config --get zzprobe.key; echo "repo-get rc=$?"
R=/home/vgpnk/Projects/shokunin/souji-shokunin; echo "--- file --list ---"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=zzprobe.key GIT_CONFIG_VALUE_0=probeval git config --file "$R/.git/config" --list | grep -i zzprobe; echo "rc=$?"; echo "--- file --get ---"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=zzprobe.key GIT_CONFIG_VALUE_0=probeval git config --file "$R/.git/config" --get zzprobe.key; echo "rc=$?"; echo "--- repo precedence (core.bare in repo config) ---"; grep -n 'bare' "$R/.git/config"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.bare GIT_CONFIG_VALUE_0=true git -C "$R" config --get core.bare; echo "rc=$?"; echo "--- file precedence ---"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.bare GIT_CONFIG_VALUE_0=true git config --file "$R/.git/config" --get core.bare; echo "rc=$?"
R=/home/vgpnk/Projects/shokunin/souji-shokunin; echo '--- get-regexp ^core. in repo with env ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git -C "$R" config --get-regexp '^core\.' | grep -E 'fsmonitor|hooksPath|bare'; echo '--- list --show-scope ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git -C "$R" config --list --show-scope | grep -E 'fsmonitor|hooksPath'; echo '--- file list show-origin/core ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git config --file "$R/.git/config" --list --show-origin | grep -E 'fsmonitor|hooksPath|bare'; echo "filegrep rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status_info_file\|guard_bound_filters' tools/souji-census.sh | head -20; echo ---; sed -n '108,126p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- env -i / subshell scrubs ---'; grep -n 'env -i\|env -u\|command env\|sh -c\|bash -c\|recurse-submodules' tools/souji-census.sh | head -20; echo '--- all git -C calls count ---'; grep -c 'git -C' tools/souji-census.sh; echo '--- malformed env pair on --file ---'; GIT_CONFIG_COUNT=1 git config --file .git/config --list >/dev/null; echo "rc=$?"
R=/home/vgpnk/Projects/shokunin/souji-shokunin; echo '--- malformed pair breaks non-config git ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=x.y git -C "$R" rev-parse --git-dir; echo "rc=$?"; echo '--- file list --show-scope ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git config --file "$R/.git/config" --list --show-scope | cut -f1 | sort -u
R=/home/vgpnk/Projects/shokunin/souji-shokunin; echo '--- raw show-scope output (first 12) ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git config --file "$R/.git/config" --list --show-scope | head -12; echo '--- fsmonitor present? ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git config --file "$R/.git/config" --list --show-scope | grep -c fsmonitor; echo '--- show-scope + show-origin ---'; GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null git config --file "$R/.git/config" --list --show-scope --show-origin | grep -E 'bare|fsmonitor'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- git calls before export at 162 ---'; awk 'NR<162 && /git [a-z-]/ {print NR": "$0}' tools/souji-census.sh | head; echo '--- xargs/find-exec git ---'; grep -n 'xargs\|-exec git\|find .*git' tools/souji-census.sh | head; echo '--- selftest env block ---'; sed -n '1608,1620p' tools/souji-census.sh
R=/home/vgpnk/Projects/shokunin/souji-shokunin; echo '--- file value beats env for same key ---'; printf 'core.bare = true\n' > /dev/null; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.bare GIT_CONFIG_VALUE_0=zzz git config --file "$R/.git/config" --get core.bare; echo "rc=$?"; echo '--- get-all ordering in repo (file then command) ---'; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.bare GIT_CONFIG_VALUE_0=zzz git -C "$R" config --get-all core.bare; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status --porcelain\|status -c\|-c core\.' tools/souji-census.sh | head -12
```

STATUS: ok
