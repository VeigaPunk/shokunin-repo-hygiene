# Scout — W2 recon: dropping global `status.showUntrackedFiles` / `core.untrackedCache`

Target: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` at lane HEAD
`a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`, bytes sha256 `64a60fd0b0ed…` (matches the
`changed` arm recorded in `census/round-16/c1-matrix-final.json`). Question: what does clearing
global config (`GIT_CONFIG_GLOBAL=/dev/null`) do to the `dirty` column relative to pre-harm
(the r13 census, `48f8945^`), specifically for `status.showUntrackedFiles` and
`core.untrackedCache`.

## Verdict

- **Literal question (global scope): holds.** Dropping a global `showUntrackedFiles` /
  `core.untrackedCache` cannot make a dirty tree look clean: `no → normal` only adds untracked
  lines, and `all → normal` only changes magnitude (a content-bearing wholly-untracked directory
  stays one line). Empty directories are invisible in both `normal` and `all`. On this host the
  delta is exactly zero because every relevant key is unset globally.
- **Item as a whole: partial.** The identical key at **repository scope** is not pinned and is
  honoured by `count_dirty`. A repo-local `[status] showUntrackedFiles = no` turns an
  untracked-dirty repo into `dirty=0` and, if unpushed=0 and a remote exists, into `clean` —
  the same false-clean class the global clearing was meant to remove, one config layer down.
  The round-16 fixture does not exercise this axis at all, and the census cannot see it because
  the fixture also pins `GIT_CONFIG_GLOBAL=/dev/null`.

## Observed facts

- **F1 (global cleared, pre-harm live).** HEAD clears global/system config at
  `tools/souji-census.sh:153` (`export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`),
  announced at `:122-124`. The pre-r14 function was
  `git -C "$1" --no-optional-locks status --porcelain -- . …` with no config pin
  (`git show 48f8945^:tools/souji-census.sh`, lines 127-138, invocation at 131): global
  `status.showUntrackedFiles` was in force and is what changed at r14.
- **F2 (dirty definition).** `dirty` = `git status --porcelain` line count
  (`tools/souji-census.sh:35-39`), produced by `count_dirty` at `:1035-1047`; the status call at
  `:1037` pins `core.fsmonitor`, `core.hooksPath`, `core.excludesFile`, `core.attributesFile`,
  and passes `--ignore-submodules=all` and the operator-surface pathspec exclusions — but **no**
  `status.showUntrackedFiles` / `-u`. Non-main worktrees reuse the same function at `:1162`.
- **F3 (config guard accepts the key).** `scan_config_file` handles only `include*.path`,
  `core.excludesFile`, `core.attributesFile`, `core.worktree`,
  `extensions.worktreeConfig` (`:631-686`); every other key, including
  `status.showUntrackedFiles`, falls through the `case` with no arm and is treated as inert.
  So a repo-local or repo-included `status.showUntrackedFiles` reaches git unchanged.
- **F4 (clean verdict).** `dirty=0` with unpushed=0 and a remote yields `clean`
  (`tools/souji-census.sh:1224-1239`; only `dirty|unpushed|no-remote|status-unverifiable|error|
  not-a-repo` count as problems). `status-unverifiable` is *not* raised by a valid `no`: git
  exits 0 and prints no `??` lines, so the guard has nothing to degrade on.
- **F5 (tests do not cover the axis).** `tests/fixtures/r15-census-config.py` contains no
  occurrence of `status.showUntrackedFiles` (grep, 1573 lines). Its `run_tool` env pins
  `GIT_CONFIG_GLOBAL=/dev/null` for every invocation (`:765-769`), and its setup env does the
  same (`:296-298`), so neither arm of the round-16 matrix can observe a global setting; case 18
  (`:1330-1357`) poisons the global file but asserts only CLEAN rows (no untracked content), so
  it would pass vacuously for this key. The legacy selftest pins collapse only in the default
  environment (`tools/souji-census.sh:1657-1660`, dirty=2 for one file + collapsed `.scratch/`).
- **F6 (host state, measured read-only).** `git config --global --get-all` returns rc 1 (unset)
  for `status.showUntrackedFiles`, `core.untrackedCache` and `feature.manyFiles`; `core.excludesFile`
  and `core.attributesFile` are also unset at every scope; `/etc/gitconfig` does not exist; the
  lane repo's local config does not set the key. **On this host the r16 census's dirty counts are
  identical to pre-harm on this axis.** (The pre-harm matrix arm `a31642d` also cannot show a
  difference, because the fixture overrides the global file for both arms.)

## Mechanism (git 2.56.0, installed)

- Config is applied before option parsing and independent of output format:
  `status_init_config(&s, git_status_config)` at `builtin/commit.c:1608`; the key is read at
  `builtin/commit.c:1507-1514` into `s->show_untracked_files`. `--porcelain` changes formatting,
  not file selection. A CLI `-u` would override config (`handle_untracked_files_arg`,
  `builtin/commit.c:1210-1230`, called at 1617); the census passes none.
- `no`: `wt_status_collect_untracked` returns immediately (`wt-status.c:806-813`), so no `??`
  lines at all; tracked modifications are unaffected.
- `normal` vs `all`: `DIR_SHOW_OTHER_DIRECTORIES | DIR_HIDE_EMPTY_DIRECTORIES` are set only for
  non-`all` (`wt-status.c:816-819`). With the flags, an untracked non-empty directory is reported
  as one `dir/` entry (`dir.c:2118` with the `check_only` recursion); without them, git recurses
  and reports individual files (`dir.c:2049-2058`). Empty directories are not reported in either
  mode (recursion yields `path_none`), which is why `all → normal` cannot flip non-zero to zero
  for content-bearing trees.
- `core.untrackedCache`: unset or `keep` keeps whatever the index carries; `false` maps to
  `UNTRACKED_CACHE_REMOVE`, and `tweak_untracked_cache` (called from index read,
  `read-cache.c:1965`) removes the extension in memory for that run (`read-cache.c:1922-1938`).
  `--no-optional-locks` suppresses the write but not this in-memory disable. Counts are unchanged
  in the steady state; the only residual is that post-r16 (key absent → `keep`) an existing UNTR
  extension is trusted, with `valid_cached_dir`'s directory-stat validation (`dir.c:2528-2566`)
  and the documented mtime caveat.

## Dirty-count effect vs pre-harm

Let `N_norm` = untracked files outside wholly-untracked directories + one per wholly-untracked
non-empty directory; `N_all` = untracked files at all depths (= pre-harm `all` count);
`F_dir` = files inside wholly-untracked non-empty directories, `D` = their directory count.

| pre-harm global value | pre-harm untracked lines | r16 untracked lines | delta (r16 − pre) | risk |
|---|---|---|---|---|
| unset / `normal` | `N_norm` | `N_norm` | `0` | none |
| `no` | `0` | `N_norm` | `+N_norm ≥ 0` | none; r16 strictly more truthful, false `clean` removed |
| `all` | `N_all` | `N_norm` | `D − F_dir ≤ 0` | none for non-zero: `F_dir ≥ D ≥ 1` implies `N_norm ≥ 1` |
| invalid value | status fails → `status-unverifiable` [INFERENCE on the die path] | `N_norm` (key absent) | loses a loud degradation signal | cosmetic only |
| `core.untrackedCache=true` | may add/keep UNTR | default `keep` | `0` | perf only |
| `core.untrackedCache=false` | UNTR removed for the run → fresh scan | `keep` → uses index UNTR if present | `0` in steady state | narrow undercount only if UNTR is stale (unreliable mtime), untested |
| `feature.manyFiles=true` | sets `untrackedCache=WRITE`, index v4 | key absent → no add | `0` | perf only |

Tracked-change lines are identical under every mode. Note the table isolates this axis only:
other pre-harm↔r16 count deltas (submodule ignoring, operator-surface pathspec exclusions,
excludes/attributes source) are separate and already documented at `:103-121` and `:935-940`.

## The surviving counterexample (repository scope)

`.git/config` (or a repo `include.path` target, or `config.worktree` when
`extensions.worktreeConfig=true`) containing:

```
[status]
	showUntrackedFiles = no
```

with a worktree whose only dirt is one untracked, non-ignored file (the shape of the selftest's
`dirty-shokunin` repo at `:1545-1660`, which asserts dirty=2 in the default environment):
`count_dirty` runs `git status --porcelain` (`:1037`) without a mode pin; `git_status_config`
reads the local value; `wt_status_collect_untracked` returns at `wt-status.c:812`; stdout is
empty; `dirty=0`; flags get `clean` at `:1239`. `scan_config_file` never rejects the key, and
`status-unverifiable` is not raised because git succeeded. Same effect on `wt-dirty` via
`:1162`. This is observable today, not hypothetical: no code path pins the mode. Severity is
exactly the global case the r14 clearing removed (a config that can mask dirt), but the local
layer is reachable by any repo and is the layer the tool is supposed to measure.

Adjacent divergence: `census:35-37` claims the dirty mode matches `souji-verify`, but
`tools/souji-verify.sh` never clears global config (only `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
GIT_NAMESPACE` at `:64`) and computes `dirty` with a plain `git -C "$target" status --porcelain`
at `:322` (also `:366`, `:658`, `:820`). Pre-r14 both tools honoured the operator's global mode
and matched; post-r14 census pins the default and verify does not, so on a host with global
`showUntrackedFiles=no` verify reports dirty=0 and `R_VERDICT` stops treating the tree as
NOT-SAFE while census reports the truth. The parity claim is now conditional and the doc does
not say so.

## Smallest fix

1. `tools/souji-census.sh:1036`: append `-c status.showUntrackedFiles=normal` to the existing
   `-c` cluster of the status invocation (it precedes `status` on `:1037`). One token, applies to
   main and linked worktrees through the shared `count_dirty`, and command scope beats every
   config file. `--untracked-files=normal` beside `--ignore-submodules=all` is equivalent.
2. Header: at `:35-39` (dirty definition) and `:122-124` (global clearing), state that the
   untracked mode is pinned to `normal` regardless of global/local/worktree config, and that a
   pre-r14 baseline produced under a non-default global mode is not count-comparable (the
   `--compare` diff will surface it as numeric delta rows, correctly).
3. Fixture (`tests/fixtures/r15-census-config.py`): one positive case — repo with one untracked
   file plus repo-local `[status] showUntrackedFiles = no`; expect `dirty=1` and no `clean`.
   Optionally add the key to case 18's poison file *and* give one of its repos untracked content,
   so the global-clearing assertion is non-vacuous.
4. Optional, decide explicitly: `-c core.untrackedCache=false` forces a full untracked scan and
   makes a stale UNTR extension irrelevant, at the cost of every run's cache speedup. If not
   taken, add the stale-UNTR/`keep` consequence to the reviewer's residual list at
   `:122-130`.

## Confidence

- Global-scope safety and the exact `no`/`all`/`normal` mechanics: **high** (git source lines
  above, plus the tool's own collapse assertion).
- Repo-local key is honoured and the guard accepts it: **high** (code path read end to end);
  the only unexecuted step is running a mutated fixture, which the probe rules forbid here.
- Host-level zero delta: **high** (five read-only `git config` queries; no `/etc/gitconfig`).
- Stale-UNTR undercount: **medium** (mechanism confirmed, real-world reachability not measured).
- Verify/census parity break under a non-default global: **high** on mechanism, **unknown** on
  whether any operator host actually sets the key.

## Remaining unknowns

- Whether any fleet repo currently sets `status.showUntrackedFiles` locally (no recursive scan
  permitted; the lane repo does not).
- Whether any fleet index carries a UNTR extension written under an earlier
  `core.untrackedCache=true` / `feature.manyFiles=true`, and whether its filesystem mtimes are
  reliable enough to trust it.
- Whether any stored baseline TSV was produced pre-r14 under a non-default global mode (would
  appear as `dirty` delta rows on the first `--compare`, not as an error).
- Exact exit path for an invalid `showUntrackedFiles` value (error return at
  `builtin/commit.c:1510-1512`; propagation to a nonzero status not traced).
- Partial-exclusion traversal inside a wholly-untracked directory (negative pathspec may force
  recursion); not exercised beyond the `.scratch/` selftest assertion.

## Citations (accessed 2026-10-20)

- https://git-scm.com/docs/git-config#Documentation/git-config.txt-statusshowUntrackedFiles —
  "no - Show no untracked files." and "If this variable is not specified, it defaults to normal."
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreuntrackedCache —
  "It will be kept, if this variable is unset or set to keep."
- https://github.com/git/git/blob/v2.56.0/builtin/commit.c#L1507-L1514 —
  "if (!strcmp(k, \"status.showuntrackedfiles\"))".
- https://github.com/git/git/blob/v2.56.0/wt-status.c#L806-L819 —
  "if (!s->show_untracked_files) return;".
- https://github.com/git/git/blob/v2.56.0/read-cache.c#L1922-L1938 —
  "case UNTRACKED_CACHE_REMOVE: remove_untracked_cache(istate);".
- https://github.com/git/git/blob/v2.56.0/dir.c#L2049-L2058 and #L2118-L2133 —
  "return path_recurse;" / "if (!excluded &&".

## Commands

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -5
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
git --version; git -C /home/vgpnk/Projects/shokunin/souji-shokunin config --show-origin --get-all status.showUntrackedFiles; echo "rc=$?"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -S'GIT_CONFIG_GLOBAL' -- tools/souji-census.sh | cat; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format='%h %s%n%b' $(git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format=%H -S'GIT_CONFIG_GLOBAL' -- tools/souji-census.sh | tail -1)
ls /home/vgpnk/Projects/shokunin/souji-shokunin/tools/ | grep -i verify
man git-config 2>/dev/null | col -b | grep -n -A 14 'status\.showUntrackedFiles'; echo ---; man git-config 2>/dev/null | col -b | grep -n -A 12 'core\.untrackedCache'
man git-status 2>/dev/null | col -b | grep -n -B3 -A 10 'showUntrackedFiles'; echo ---; man git-status 2>/dev/null | col -b | grep -n -B2 -A 12 'untracked-files'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 48f8945^:tools/souji-census.sh | grep -n -B4 -A8 'status --porcelain'
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | grep -n -B4 -A18 'showuntrackedfiles\|showUntrackedFiles' | head -80
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | grep -n -B3 -A8 'UNTRACKED_CACHE_REMOVE\|use_untracked_cache' | head -60
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | wc -l; curl -s https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | grep -n -i -B3 -A10 'untrackedfiles' | head -60
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c | grep -n -i -B2 -A10 'showuntrackedfiles\|status\.show' | head -60
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | grep -n -i 'untracked' | head -40; echo ===; curl -s https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | grep -n 'git_status_config\|status\.' | head -20
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | sed -n '806,860p'
man git-status 2>/dev/null | col -b | grep -n -A 12 '^     --porcelain'
grep -n 'status --porcelain\|GIT_CONFIG_GLOBAL\|showUntrackedFiles\|untracked' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh | head -40
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | grep -n -B6 -A10 'DIR_HIDE_EMPTY_DIRECTORIES' | head -80
grep -n 'GIT_CONFIG_GLOBAL\|GIT_CONFIG_SYSTEM\|GIT_CONFIG_NOSYSTEM' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; echo ===; grep -n -c 'status --porcelain' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | grep -n -A 20 'case path_untracked:' | head -60
cut -c1-400 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json | head -40
grep -n 'selftest\|summary\|PASS\|FAIL' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json | tail -20; echo ===; python3 -c "
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json'))
print(sorted(d.keys()))
print(sorted(d['arms'].keys()))
for k,v in d.get('arms',{}).items():
    print(k, sorted(v.keys()))
"
python3 -c "
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json'))
for arm in d['arms']:
    a=d['arms'][arm]
    cases=a['r15-config']['cases']
    p=sum(1 for c in cases.values() if c['verdict']=='PASS'); f=len(cases)-p
    print(arm, 'sha',a['sha256'][:12] if 'sha256' in a else '?', 'r15-config',p,'PASS',f,'FAIL','selftest',a['selftest'],'bash_n rc',a['bash_n']['rc'],'scwarn',a['shellcheck_warning'])
"
for k in status.showUntrackedFiles core.untrackedCache feature.manyFiles core.excludesFile core.attributesFile; do printf '%s: ' "$k"; git config --show-origin --get-all "$k" 2>/dev/null || echo '<unset>'; done; echo ===; git -C /home/vgpnk/Projects/shokunin/souji-shokunin config --local --get-all status.showUntrackedFiles; echo "local rc=$?"; ls -l /etc/gitconfig 2>/dev/null || echo 'no /etc/gitconfig'
man git-config 2>/dev/null | col -b | grep -n -A 8 'core\.excludesFile' | head -20
grep -n 'Global/system git config\|GIT_CONFIG_GLOBAL\|global config' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; echo ===; grep -n '\[status\]\|status\.' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py | head; echo "fixture status-key hits above (none expected)"; echo ===; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 48f8945^:tools/souji-census.sh | sed -n '127,138p' | cat -n
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | grep -n 'treat_directory(dir' ; echo ===; curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | sed -n '2640,2680p'
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | sed -n '2480,2540p'
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | sed -n '1971,2145p'
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | sed -n '2528,2605p'
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | sed -n '1890,1945p'
curl -s https://raw.githubusercontent.com/git/git/v2.56.0/dir.c | grep -n 'if (!(dir->flags & DIR_SHOW_OTHER_DIRECTORIES))\|if (!excluded &&' ; echo ===; curl -s https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | grep -n 'tweak_untracked_cache(' ; echo ===; ls -d /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2 2>/dev/null || echo 'w2 missing'; grep -c 'status --porcelain' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n 'GIT_' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh | head -20; echo ===; sed -n '318,326p' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-verify.sh; echo ===; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only HEAD tools/souji-verify.sh
git config --global --get-all status.showUntrackedFiles; echo "global show rc=$?"; git config --global --get-all core.untrackedCache; echo "global ucache rc=$?"; git config --global --get-all feature.manyFiles; echo "manyfiles rc=$?"; git -C /home/vgpnk/Projects/shokunin rev-parse --git-dir 2>/dev/null || echo 'fleet root is not a repo'
grep -n 'status --porcelain\|if ! st=\|status-unverifiable\|flags+=(clean)\|has_problem=1\|d=$(count_dirty\|dirty           `' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh | head -20; echo ===; sed -n '1222,1240p' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
```

No census execution, no mutation, no writes outside this report; the lane root and fleet root were
never recursively searched. Read-only web/source fetches: git-scm.com docs (git-config, git-status),
raw.githubusercontent.com `v2.56.0` (`repo-settings.c`, `wt-status.c`, `read-cache.c`, `dir.c`,
`builtin/commit.c`). No tools installed or upgraded.

STATUS: ok
