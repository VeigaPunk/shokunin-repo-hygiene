# ScoutFsmonitorValues — `core.fsmonitor=false` semantics vs. census index refreshes

Seat: SoujiR16.ScoutFsmonitorValues · Round 16 · read-only recon · 2026-10-20
Target: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` at
`cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (1784 lines; copied to `/var/tmp` for line reads).
Host git: `git version 2.56.0` (measured, see Commands). All Git source citations are tag
`v2.56.0`, matching the host. All URLs accessed **2026-10-20**.

## Question

`core.fsmonitor` boolean vs. hook-path values, and whether `-c core.fsmonitor=false`
fully disables both the built-in daemon and a hook on every census git command that
refreshes the index.

## Verdict

**Yes on the census's one production index-refreshing command (confirmed, high confidence).**
`git status` at `tools/souji-census.sh:947-952` is the only census invocation against
operator repositories that refreshes the index, and it carries both `-c core.fsmonitor=false`
and `-c core.hooksPath=/dev/null`. In Git ≥ 2.36 the `false` value resolves to
`FSMONITOR_MODE_DISABLED`: no hook is executed, no daemon is queried, and no daemon is
auto-started. It does **not** stop a daemon some other process already started, and it is
**version-conditional**: Git ≤ 2.35.1 treats `"false"` as a hook pathname.

`core.hooksPath=/dev/null` is **not** what suppresses the fsmonitor hook — the hook path is
executed straight from `core.fsmonitor` and is unaffected by `core.hooksPath`. The script's
pairing is therefore load-bearing on `core.fsmonitor=false`, not on the hooksPath flag.

## Observed facts

### F1 — `core.fsmonitor` is overloaded: boolean or hook pathname (high confidence)

`git-config(1)` defines both shapes:

> "If set to true, enable the built-in file system monitor daemon for this working directory"
> "Otherwise, this variable contains the pathname of the "fsmonitor" hook command."

Implementation (`fsmonitor-settings.c`, `lookup_fsmonitor_settings`):

```c
switch (repo_config_get_maybe_bool(r, "core.fsmonitor", &bool_value)) {
case 0: /* config value was set to <bool> */
    if (bool_value)
        fsm_settings__set_ipc(r);      /* FSMONITOR_MODE_IPC = 2  */
    else
        fsm_settings__set_disabled(r); /* FSMONITOR_MODE_DISABLED = 0 */
    return;
case 1: /* unset -> GIT_TEST_FSMONITOR fallback */
case -1: /* arbitrary string -> repo_config_get_pathname -> set_hook */
```

The source comment states the intent directly: "allow a boolean value to enable the builtin
FSMonitor or to turn everything off". `fsmonitor-settings.h` fixes the mode order:
`DISABLED = 0`, `HOOK = 1`, `IPC = 2`, `INCOMPATIBLE = -1`.

### F2 — `-c` overrides file scopes, and the last value wins (high confidence)

`git(1)`: "The value given will override values from configuration files."
`git-config(1)` `get`: "If key is present multiple times in the configuration, emits the last value."
Command-line config is applied after system/global/local/worktree, so the repo (including
`include.path`/`includeIf` and `config.worktree`) cannot outvote `-c core.fsmonitor=false`.
The census additionally nils global/system config (`:143-144`) and unsets every inherited
`GIT_*` variable (`:135-140`), so `GIT_TEST_FSMONITOR`, `GIT_CONFIG_COUNT`,
`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` cannot re-enable monitoring either.

### F3 — `false` skips hook, query, and auto-start (high confidence)

`fsmonitor.c` `refresh_fsmonitor`:

```c
if (fsm_mode <= FSMONITOR_MODE_DISABLED || istate->fsmonitor_has_run_once)
    return;
...
if (fsm_mode == FSMONITOR_MODE_IPC) { query_success = !fsmonitor_ipc__send_query(...); ... }
assert(fsm_mode == FSMONITOR_MODE_HOOK);
```

`fsmonitor-ipc.c` only spawns a daemon inside `fsmonitor_ipc__send_query()` (`spawn_daemon()`
runs `git fsmonitor--daemon start`); that function is reachable only from the IPC branch.
`query_fsmonitor_hook()` also returns `-1` unless the mode is `FSMONITOR_MODE_HOOK`.
Therefore with mode `DISABLED`: no hook process, no IPC query, no auto-start.
The daemon doc agrees that auto-start is tied to `true`: "commands, such as git status, will
ask the daemon for changes and automatically start it (if necessary)".

**Scope limit:** this is a per-process disable. An already-running `fsmonitor--daemon`
(or a hook invocation from another process) is neither stopped nor affected; the census
simply never contacts it.

### F4 — `core.hooksPath` does not gate the fsmonitor hook (high confidence)

`fsmonitor.c`, `query_fsmonitor_hook()`:

```c
strvec_push(&cp.args, fsm_settings__get_hook_path(r));
strvec_pushf(&cp.args, "%d", version);
strvec_pushf(&cp.args, "%s", last_update);
cp.use_shell = 1;
```

The executable name comes from the config value itself; `githooks(5)` likewise describes the
hook as configured via `core.fsmonitor` ("set to `.git/hooks/fsmonitor-watchman`"), not via
the hooks directory. `core.hooksPath=/dev/null` can only defeat hooks resolved through the
hooks directory; it cannot defeat this one. The census is correct only because it passes
`core.fsmonitor=false` as well (`:947-948`). `git status` itself runs no hooks-directory hook,
so the hooksPath flag is defense in depth, not the fsmonitor guard.

### F5 — Inventory: which census commands refresh the index (high confidence)

Production path (operator repos):

| Line | Command | Refreshes index? | fsmonitor query possible? |
|---|---|---|---|
| 947-952 | `git ... -c core.fsmonitor=false -c core.hooksPath=/dev/null ... status --porcelain` | yes | overridden to disabled |
| 852, 1076 | `git worktree list [--porcelain]` | no | no |
| 858 | `git for-each-ref` | no | no |
| 862, 866 | `git rev-list --count` | no | no |
| 876 | `git config --get` | no | no |
| 910 | `git config -z --get-regexp` | no | no |
| 922-925 | `git ls-files -z --cached \| git check-attr -z --stdin filter` | no (read-only index open; no `refresh_index`) | no |
| 1104 | `git rev-parse --is-inside-work-tree` | no | no |
| 589/592/635 | `git config --file ...` | no | no |

Selftest only, inside `mktemp -d /var/tmp/souji-census-selftest.XXXXXX` fixtures (`:1437`):

| Line | Command | Refreshes index? | Note |
|---|---|---|---|
| 1402 | `git -C "$repo" add -A` | yes | not reachable: fixture repos; global/system config nil, all inherited `GIT_*` unset, no fixture sets `core.fsmonitor` |
| 1403 | `git -C "$repo" write-tree` | no | reads index only; no refresh/query |
| 1405-1412 | `git ... commit-tree` | no | no index refresh |

`count_dirty` is called at `:1115` (repo row) and `:1072` (each linked worktree row), so the
worktree rows inherit the same guarded command.

### F6 — Index fsmonitor extension is not stripped from operator repos (medium-high confidence)

With mode disabled, `tweak_fsmonitor()` calls `remove_fsmonitor()`, which sets
`FSMONITOR_CHANGED` in memory — a later index *write* would drop the extension. The census
prevents that write twice over: `GIT_OPTIONAL_LOCKS=0` (`:142`) and `--no-optional-locks`
(`:947`). Status remains a full-stat scan and the on-disk index is not rewritten. (The
in-memory removal is certain from source; "no write" rests on the documented optional-locks
contract, not on an executed experiment.)

### F7 — Version caveat: no Git floor in the script (high confidence in docs; runtime detail [INFERENCE])

`git-config(1)` warns: "Git versions 2.35.1 and prior will not understand the boolean values
and will consider the "true" or "false" values as hook pathnames to be invoked." The script
checks only presence of `git` (`:1775`), not a version.

Consequences for the census on old Git, in order of confidence:
- **Integrity still holds:** `-c` still overrides the repo's value, so the repo cannot supply
  the hook path; the only string executed is the constant `false`.
- **On 2.26–2.35.1:** `false` is treated as a hook pathname; Git attempts to run the command
  `false` through a shell, which exits non-zero. `githooks(5)` states: "On error, it will fall
  back to verifying all files and folders." Result is a correct full scan, not a silent skip.
- **On < 2.26:** `git-config(1)` additionally warns that these versions "will silently assume
  there were no changes to report (no scan)". Whether the non-zero `false` command still
  forces the documented fallback on those versions is **[INFERENCE] unverified**; the script
  has no version floor, so this is a real compatibility residual for the "inert" claim.

### F8 — Header/comment accuracy (high confidence)

- `:101-102`: "Accepted: any core.hooksPath/core.fsmonitor value (every status carries
  -c core.hooksPath=/dev/null -c core.fsmonitor=false)" — matches the code.
- `:640-643`: "core.hooksPath/core.fsmonitor are overridden on every status" — accurate, but a
  reader could misattribute hook suppression to `core.hooksPath`. Only `core.fsmonitor=false`
  disables the fsmonitor hook.
- The claim is deliberately scoped to *status*, which is the only index-refreshing production
  command, so the narrower wording is correct rather than an omission.

### F9 — Doc inconsistency, no effect on `false` (high confidence in text; cause unresolved)

`git-config(1)` in v2.56 still says the built-in monitor is "currently available only on a
limited set of supported platforms... Windows and MacOS", while `git-fsmonitor--daemon(1)`
documents Linux/inotify caveats in the same release. Either way, `core.fsmonitor=false`
selects `DISABLED` before platform compatibility is considered, so the census's Linux
behavior is unaffected.

## Residual unknowns

1. No executed experiment: under the probe rule this seat may not run census or synthetic
   index-refresh tests; F3/F5/F6 rest on v2.56.0 source and docs, not observation.
2. Exact behavior of Git < 2.26 with `-c core.fsmonitor=false` (boolean-as-path + V1
   protocol) is documented only at the level quoted; whether the literal `false` command's
   non-zero exit always forces the full-scan fallback there is unverified.
3. An externally pre-started `fsmonitor--daemon` is out of the census's control; `false`
   prevents contact/spawn but not the daemon's existence or its own filesystem watches.
4. The script does not sanitize `PATH`; on Git ≤ 2.35.1 the literal command `false` is
   shell-executed. Normal shells resolve `false` as a builtin, but this is unverified for the
   operator's shell/`PATH` on old Git.

## Sources (URL · quote ≤25 words · accessed 2026-10-20)

| # | URL | Quote |
|---|---|---|
| S1 | https://git-scm.com/docs/git-config#Documentation/git-config.txt-corefsmonitor | "If set to true, enable the built-in file system monitor daemon for this working directory" |
| S2 | same as S1 | "Otherwise, this variable contains the pathname of the "fsmonitor" hook command." |
| S3 | same as S1 | "Git versions 2.35.1 and prior will not understand the boolean values and will consider the "true" or "false" values as hook pathnames to be invoked." |
| S4 | same as S1 | "Git versions prior to 2.26 default to hook protocol V1 and will silently assume there were no changes to report" |
| S5 | https://git-scm.com/docs/git | "The value given will override values from configuration files." |
| S6 | https://git-scm.com/docs/git-config | "If key is present multiple times in the configuration, emits the last value." |
| S7 | https://git-scm.com/docs/git-fsmonitor--daemon | "commands, such as git status, will ask the daemon for changes and automatically start it (if necessary)" |
| S8 | https://git-scm.com/docs/githooks#_fsmonitor | "This hook is invoked when the configuration option core.fsmonitor is set to .git/hooks/fsmonitor-watchman" |
| S9 | same as S8 | "On error, it will fall back to verifying all files and folders." |
| S10 | https://git-scm.com/docs/git-update-index | "the file system monitor is added to or removed from the index the next time a command reads the index" |
| S11 | https://raw.githubusercontent.com/git/git/v2.56.0/fsmonitor-settings.c | "allow a boolean value to enable the builtin FSMonitor or to turn everything off" |
| S12 | https://raw.githubusercontent.com/git/git/v2.56.0/fsmonitor.c | `if (fsm_settings__get_mode(r) != FSMONITOR_MODE_HOOK) return -1;` and `cp.use_shell = 1;` |
| S13 | https://raw.githubusercontent.com/git/git/v2.56.0/fsmonitor-ipc.c | `spawn_daemon()` (`git fsmonitor--daemon start`) is called only from `fsmonitor_ipc__send_query()` |
| S14 | https://raw.githubusercontent.com/git/git/v2.56.0/fsmonitor-settings.h | `FSMONITOR_MODE_DISABLED = 0`, `FSMONITOR_MODE_HOOK = 1`, `FSMONITOR_MODE_IPC = 2` |

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -i "fsmonitor" 
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify cbf688ab2ab28e38103e5a9417ca525b5f2ed423 2>&1
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/scout-fsmonitor-census.sh && grep -n -E "(^|[^[:alnum:]_])git([[:space:]]|$)|GIT_|hooksPath|fsmonitor|promisor|partialClone|alternateRefs" /var/tmp/scout-fsmonitor-census.sh
git --version; command -v man >/dev/null && man --version 2>/dev/null | head -1; ls /usr/share/man/man5/git-config.5.gz /usr/share/doc/git 2>/dev/null
grep -n "status" /var/tmp/scout-fsmonitor-census.sh | grep -v "^[0-9]*:#" | grep -E "git|status --porcelain|unverifiable|st=" 
sed -n '1376,1420p' /var/tmp/scout-fsmonitor-census.sh | cat -n; echo ---CALLERS---; grep -n "fixture_commit\|count_dirty\|make_repo\|ST_TMP=" /var/tmp/scout-fsmonitor-census.sh | head -60
sed -n '1080,1115p' /var/tmp/scout-fsmonitor-census.sh; echo ---; sed -n '1720,1745p' /var/tmp/scout-fsmonitor-census.sh; echo ---; sed -n '1770,1784p' /var/tmp/scout-fsmonitor-census.sh
grep -nE "core\.fsmonitor|GIT_TEST_FSMONITOR|git version|--version|minimum|git >|git <" /var/tmp/scout-fsmonitor-census.sh; echo ---; grep -nE "^[^#]*\bgit\b" /var/tmp/scout-fsmonitor-census.sh | sed -n '1,200p'
sed -n '920,960p' /var/tmp/scout-fsmonitor-census.sh; echo '---env---'; sed -n '133,150p' /var/tmp/scout-fsmonitor-census.sh; echo '---guard-claim---'; sed -n '636,648p' /var/tmp/scout-fsmonitor-census.sh
rm -f /var/tmp/scout-fsmonitor-census.sh
```

STATUS: none — read-only recon completed; no command failed in a way that changes the findings (the `ls /usr/share/doc/git` probe returned non-zero because the path is absent; irrelevant to the result).
