# ScoutExcludesRelative — relative `core.excludesFile` / `core.attributesFile`

Seat: `SoujiR16.ScoutExcludesRelative` (leaf, read-only recon). Lane root:
`/home/vgpnk/Projects/shokunin/souji-shokunin`.
Revision audited: `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` — blob `ea05ba722bed6d3dc71003b934ab00b899ea8127`, 65991 bytes.
Proof the worktree file is those bytes: clean `git status` for the path, empty `git diff cbf688a -- tools/souji-census.sh`, and
`git show cbf688a:tools/souji-census.sh | sha256sum` = `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` = `sha256sum tools/souji-census.sh`.
All web sources accessed **2026-10-20**.

## Answer

### 1. Git does not anchor a relative value; it leaves it relative and opens it against the process CWD

`core.excludesFile` / `core.attributesFile` are git-config *pathname* values. The only pathname transformations git performs are:

- leading `~/` → `$HOME`; leading `~user/` → that user's home (docs: "A variable that takes a pathname value can be given a string that begins with `~/` or `~user/`"; "`~/` is expanded to the value of `$HOME`");
- leading `%(prefix)/` → install/runtime prefix ("the remainder is interpreted as a path relative to Git's "runtime prefix"");
- an optional `:(optional)` prefix (implementation detail, see config.c below).

Everything else is stored **verbatim**. `unquote_path`-style interpolation is not applied and no base directory is prepended: `path.c` `interpolate_path()` only expands the two tilde forms / `%(prefix)` and then does `strbuf_addstr(&user_path, to_copy)` — "Return a string with ~ and ~user expanded via getpw*". `environment.c` stores the result unchanged (`cfg->excludes_file`), `dir.c` `setup_standard_excludes()` hands it to `access_or_warn(excludes_file, R_OK, 0)` + `add_patterns_from_file_1()`, and `attr.c` hands it to `read_attr_from_file(path, …)`. Both are ordinary opens, so a still-relative string is resolved by the kernel **relative to the invoking process's current working directory at read time**. [INFERENCE for the open(2)-relative step; the absence of any anchoring is OBSERVED in source.]

The documentation confirms this by contrast: where git means a specific base it says so explicitly, and the two entries here carry no base clause.

| key | documented base |
|---|---|
| `core.excludesFile` | none — "Specifies the pathname to the file that contains patterns to describe paths that are not meant to be tracked" |
| `core.attributesFile` | none — "Specifies the pathname to the file that contains attributes" |
| `core.worktree` | "The value can be an absolute path or relative to the path to the .git directory" |
| `core.hooksPath` | "taken as relative to the directory where the hooks are run" |
| `include.path` | "relative to the configuration file in which the include directive was found" |
| `diff.orderFile` | "If `diff.orderFile` is a relative pathname, it is treated as relative to the top of the working tree." |

So the correct statement is: **not worktree-top, not config-file-relative — CWD-relative.** "Worktree-relative" is only what you observe when git happens to be started at the worktree top.

### 2. `~/` expansion details

- Raw `$HOME` from the environment, no `realpath`: `interpolate_path(value, 0)` (`git_config_pathname` in config.c); `real_home=1` is used only for `includeIf` patterns.
- Only a *leading* `~` expands (`if (path[0] == '~')`); a `~` elsewhere is literal.
- Implementation expands more than the docs promise: bare `~` (no slash) and `~user` without trailing slash also expand (username length before first `/`).
- If `$HOME` is unset or `getpwnam` fails, `interpolate_path` returns NULL and `git_config_pathname` **dies**: `failed to expand user dir in: '<value>'` — the whole git command fails.

### 3. Comparison with `status_info_file` (census)

`status_info_file` (tools/souji-census.sh:874-901) reads the raw value with `git -C "$wt" config --get "$key"` (:876), expands it with `expand_config_path "$val" "$wt"` (:878), guards it (:880), and `count_dirty` passes the resulting path back to git with `-c core.excludesFile="$ex" -c core.attributesFile="$at"` on the status call at :947-949 (and on `ls-files`/`check-attr` in `guard_bound_filters` at :922-925).

`expand_config_path` (:540-549):

- :543 `~/` → `"$HOME/${v:2}"` (raw HOME) — **exact match** with `interpolate_path(value, 0)`.
- :544 any other leading `~`, or `%(prefix)` → return 1 (unsupported) → `cfg_soft` at :621-622 → one `error` row via :1086-1090. Declared in the header at :90-96 for `~user`/`%(prefix)`.
- :546 relative → `"$base/$v"` with `base=$wt`.

Because every consumer invokes git as `git -C "$1"` with **the same directory that was used as `base`** (:878 uses `$wt`; :922/:924 and :947 use `-C "$wt"`/`-C "$1"`), `-C` makes that directory the CWD — "-C <path>: Run as if git was started in '<path>' instead of the current working directory" — and git's implicit base equals the base the script substituted. The script then passes an **absolute** path via `-c`, so git performs no second interpretation. **For the census's own invocation pattern the worktree base is therefore behaviourally exact, not an approximation.** It is, however, pinned by the pairing `base == -C dir`; any future call site that reads these keys without `-C <same dir>` would diverge from the substituted base.

`~/` matches. `~user/`, bare `~` and `%(prefix)` are refused where git would expand; that is a deliberate, repo-scoped degrade (one `error` row), which is the narrow-blast-radius direction required by C1 (git would kill the whole command).

## Findings

### F1 — INFO — relative values: script is correct *for its own call sites*
`base == cwd` because of `-C` (:546 vs :947-949). Not a defect. Precondition to preserve: all reads of these keys must keep using `-C` with the same directory that `expand_config_path` used as base. Current call sites satisfy this (:922, :924, :947).

### F2 — LOW — scan-stage base is not the worktree for linked worktrees/submodules
`scan_config_file` resolves `core.excludesFile`/`core.attributesFile` against `"${dir%/*}"` (:620-624), where `dir` is the **admin** gitdir. For a linked worktree (`…/.git/worktrees/<n>`) or a submodule (`…/.git/modules/<name>`) — reached through the `.git`-file branch at :798-833 — that base is inside the parent's `.git`, not the worktree. `status_info_file` uses the correct `$wt` (:878) and guards it (:880), so a protected reach still ends in exit 2, merely later; the only other consequence is a possible false-positive exit 2 if the admin path with the relative value happens to contain a protected component. Operability unaffected; ordering/guard-base inconsistency only. Confidence: high from source; not exercised.

### F3 — VALUE-AWARENESS GAP — explicit empty value suppresses git's XDG default, the census does not
`[ -n "$val" ]` (:877) treats `""` as "unset" and falls through to the XDG default (:884-897). Git treats `core.excludesFile =` (empty) as *set*:
`environment.c` :492-495 calls `git_config_pathname` (returns `""`), `repo_excludes_file` (:155-163) applies the XDG default only when the pointer is NULL, and `setup_standard_excludes` (:3505-3508) then `access_or_warn("")` fails → **no global excludes file and no XDG fallback**. `attr.c` :885-886 has the same NULL-only default for attributes. Consequence: an explicit empty assignment makes the census read the user's `~/.config/git/ignore` (and `attributes`) where git reads neither, so dirty counts can differ (typically undercount when the XDG ignore hides files the repo asked to track). Note: the comment at :609 ("A bare or empty path makes git itself fail; nothing is opened") belongs to the `include.path` branch, but the skip at :620 applies the same `[ -z "$val" ]` test to `core.excludesFile`/`core.attributesFile`; for those keys a *bare* key makes git fail, while an empty `key =` does not — it is valid config that disables the global file. Confidence: high from source; not executed (probe rule). No `error` row is emitted, so the divergence is silent.

### F4 — LOW — `:(optional)` is unmodelled and then mis-passed
`git_config_pathname` strips `:(optional)` and, when the named path is missing, sets the destination to NULL (:1325-1342), which re-enables the XDG default. `expand_config_path` (:540-546) classifies `:(optional)<path>` as a relative path and yields `"$wt/:(optional)<path>"`; the value handed to git through `-c` starts with `/`, so git no longer strips the prefix, reads a nonexistent file, and suppresses the XDG default. Divergence for both keys and for both missing/existing targets. Low probability; the header's unsupported list (:90-96) names only `~user` and `%(prefix)`.

### F5 — LOW — relative `XDG_CONFIG_HOME` and bare `~`
`path.c` `xdg_config_home_for` (:1551-1560) accepts any non-empty `$XDG_CONFIG_HOME`, relative included, and concatenates, so git opens `$wt/<xdg>/git/ignore` under the census's `-C`. `status_info_file` forces `/dev/null` for a non-absolute base (:889-892). Also, bare `~` and `~user` without a trailing slash are expanded by `interpolate_path` (:715-739) but refused at :544; `~user` is declared at :94, bare `~` is not named there. Divergences are small and in the safe-ish direction, but they are silent.

### F6 — INFO — file location vs pattern base must not be conflated
gitignore(5): patterns from `core.excludesFile` "are treated as if they are specified at the root of the working tree". That is the **matching base inside the file**, not the file's location; the census correctly passes the file path unchanged and rewrites no patterns. No action.

## Observed matches (not defects)

- `$HOME` unset with `~/`: git dies (whole command), census emits one `error` row — both refuse; census is narrower and matches the C1 contract.
- XDG default construction: `$XDG_CONFIG_HOME/git/<leaf>`, else `$HOME/.config/git/<leaf>`, else none — identical to `xdg_config_home("ignore")` / `xdg_config_home("attributes")` (path.c :1568-1571; attr.c :886).
- A configured value **replaces** (does not augment) the XDG default in both implementations.
- A missing configured file: `resolve_guarded` tolerates nonexistent components and returns the lexical path (:388-436); git's `access_or_warn` fails and skips the file — same effect.
- Only these two keys are overridden; `.gitignore` and `.git/info/exclude` precedence is untouched, as is the `$GIT_DIR/info/exclude` half of `setup_standard_excludes`.

## Confidence and remaining unknowns

- OBSERVED: documentation text and git master source listed below; census source at the pinned blob.
- INFERENCE: the final `open(2)` resolving a still-relative string against CWD (git code performs no anchoring); `git config --get` emitting a blank line/exit 0 for an empty value (not executed under the probe rule); the linked-worktree scan-base consequences in F2.
- Not exercised: any git command beyond `show/log/diff/cat-file/rev-parse`; no census matrix, fixture, `bash -n`, or `shellcheck` run — those belong to the executor seats. This report is advisory.

STATUS: recon complete; F3 is the only finding with a plausible dirty-count effect, F2/F4/F5 are silent low-severity divergences.

## Sources (accessed 2026-10-20)

1. https://git-scm.com/docs/git-config — pathname: "A variable that takes a pathname value can be given a string that begins with `~/` or `~user/`"; "`~/` is expanded to the value of `$HOME`"; `%(prefix)/` "the remainder is interpreted as a path relative to Git's "runtime prefix""; `core.excludesFile`: "Specifies the pathname to the file that contains patterns to describe paths that are not meant to be tracked"; `core.worktree`: "The value can be an absolute path or relative to the path to the .git directory"; `diff.orderFile`: "If `diff.orderFile` is a relative pathname, it is treated as relative to the top of the working tree."
2. https://git-scm.com/docs/git — "-C <path>: Run as if git was started in '<path>' instead of the current working directory."
3. https://git-scm.com/docs/gitignore — "Patterns read from exclude sources that are outside the working tree … are treated as if they are specified at the root of the working tree."
4. https://raw.githubusercontent.com/git/git/master/path.c — `interpolate_path` comment "Return a string with ~ and ~user expanded via getpw*"; body `strbuf_addstr(&user_path, to_copy)`; `%(prefix)/` → `system_path`; `xdg_config_home_for` accepts any non-empty `$XDG_CONFIG_HOME`.
5. https://raw.githubusercontent.com/git/git/master/config.c — `git_config_pathname`: `path = interpolate_path(value, 0);` and `die(_("failed to expand user dir in: '%s'"), value);`; `:(optional)` handling.
6. https://raw.githubusercontent.com/git/git/master/environment.c — `repo_excludes_file`: `if (!cfg->excludes_file) cfg->excludes_file = xdg_config_home("ignore");`; `core.attributesfile` / `core.excludesfile` callbacks.
7. https://raw.githubusercontent.com/git/git/master/dir.c — `setup_standard_excludes`: `if (excludes_file && !access_or_warn(excludes_file, R_OK, 0))`.
8. https://raw.githubusercontent.com/git/git/master/attr.c — `if (!cfg->attributes_file) cfg->attributes_file = xdg_config_home("attributes");`; `read_attr_from_file(path, …)`.

Tooling: nothing installed or updated (no package manager action taken).

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify cbf688ab2ab28e38103e5a9417ca525b5f2ed423 2>&1; git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 2>&1
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-census.sh; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n -i -- 'excludesfile\|attributesfile\|worktree)\|prefix)\|expand_config_path' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n -- 'scan_config_file\|CFG_SOFT_REASON\|config-unsupported\|error' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh | sed -n '1,80p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -s cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum
grep -n -E 'expand_config_path\(\)|v="\$HOME|v="\$base|printf .%s. "\$v"|status_info_file\(\)|val=\$\(git -C|\[ -n "\$val" \]|\[ -z "\$val" \]|expand_config_path "\$val" "\$wt"|guard_config_path git-config-unsupported "\$wt"|base=\$\{XDG_CONFIG_HOME|base="\$HOME/.config"|tgt="\$base/git/\$leaf"|printf ./dev/null|resolve_guarded "\$tgt"' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
```

Note: the one `sed -n '1,80p'` was used only to page a `grep -n` result on the exact named file (read-only, no edit); no git command beyond `rev-parse`/`log`/`diff`/`cat-file`/`show` was run.
