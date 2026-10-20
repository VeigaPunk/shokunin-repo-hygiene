# Round 15 · W1 · CommandInjection (critic)

Axes: **operability** (benign values with shell syntax or option-looking text must be preserved) and **calibration** (a value-aware guard must check the same bytes and path that git uses). Source inspection only: no tests, probes, builds, or edits outside this report.

**Snapshot.** `tools/souji-census.sh#EAEA`. This is still round-14 code: ConfigRepair had not landed when I read it (`guard_git_config` :493-522 refuses on key name only). So there are two kinds of finding below:
- **[current]**: a defect in the shipped code.
- **[design]**: an acceptance condition the repair must meet; it fails if the repair takes the obvious route.

**Primary sources.** Git v2.55.0 source, raw.githubusercontent.com, tag v2.55.0, fetched 2026-10-20:
- `config.c`, `setup.c`, `path.c`, `worktree.c`, `convert.c`, `builtin/config.c`

Also https://git-scm.com/docs/git-config, the "pathname", "Includes" and `--null` sections.

## Verified safe (current code)
- No `eval`, `sh -c` or `bash -c` anywhere. Config-derived data reaches only `core.worktree` → `guard_target` (:511-520), and every expansion there is double-quoted.
- `$(touch M)`, backticks, `;` and globs stay literal, because the value never reaches a shell parser.
- Option-looking values cannot become argv options:
  - Relative values are prefixed with `$dir/` (:518).
  - `resolve_guarded` always prints an absolute `/…` (:410).
  - `readlink --` (:386) and `du -P --` (:731) use `--`.
  - `find -P "$dir"` (:458, :470) only ever receives resolved absolute paths.
- `git config --file "$cfg"`: `$cfg` is always `<resolved>/config`, which is absolute.

**Invariant the repair must keep:** every config-derived path goes through `guard_target` before it reaches git, find or du. GNU find has no end-of-options marker for start points, so a raw value such as `-delete` must never reach find. Use the attached form `git config --file="$abs"`.

## Findings

### F1 · HIGH · design · calibration — `--type=path` for `include.path` checks a different file than git opens
**Counterexample** (no symlink needed):
```
.git/config:                [include] path = ":(optional)evil.inc"
.git/:(optional)evil.inc:   [include] path = /home/<u>/.omp/agent/auth.json
```

**What git does.** `handle_path_include` (`config.c:142-186`) calls `interpolate_path` directly. It does **not** strip `:(optional)`. It resolves the value relative to the including file and opens `<gitdir>/:(optional)evil.inc`. Then it follows the nested include and opens the credential file (`access_or_die` at :177, read at :183).

**What a `--type=path` guard sees.** `git config --type=path` goes through `format_config_path` → `git_config_pathname` (`builtin/config.c:343-356`; `config.c:1316-1324`). That path strips `:(optional)` and checks `evil.inc` relative to the **process cwd**. When that file is missing, the entry is silently dropped (`return 1 /* :(optional)no-such-file */`). The guard never sees the include, and the nested store path is never checked.

**Impact.** Fail-open: credential-store read on `status`, `worktree list`, `rev-list` and `for-each-ref`.

**Correction.**
1. Read raw values (`--no-includes -z`, no `--type`).
2. Mirror `interpolate_path` (`path.c:698-728`) exactly:
   - `%(prefix)/` → refuse as unsupported.
   - `~` or `~/` → `$HOME`, the same env that git sees.
   - `~user` → refuse.
   - Anything else is literal.
3. Resolve relative values against `dirname` of the **including file**, not the gitdir or cwd.
4. Run `guard_target` on the result, then recurse with the same reader. Stop at depth ≤10 (`MAX_INCLUDE_DEPTH`, `config.c:135`) and refuse cycles.

### F2 · HIGH · current · calibration — trailing-newline `core.worktree` escapes the guard (:511)
**Counterexample:** `[core] worktree = "../w\n"`, plus `<repo>/w<NL>` as a symlink to `~/.omp/agent`.
- `"\n"` is a legal escape in a config value (`config.c:880-881`).
- `$(git config … --get core.worktree)` strips trailing newlines, so the guard checks `<gitdir>/../w`. That path is benign or missing, so the check passes.
- Git keeps the value verbatim (`setup.c:595-599`, `xstrdup(value)`) and uses `<gitdir>/../w<NL>`.
- The link is inside the work tree. `guard_git_links` scans only the gitdir, and `list_repos` skips names that contain a newline (:946), so nothing ever checks the link.

**Impact.** `count_dirty` runs `status` with the work tree set to the store. That means readdir/lstat of store entries, and the count of untracked store entries lands in the TSV `dirty` column. [INFERENCE: source path, not executed.] `|| true` at :511 also hides read failures (RunnerLimits F2).

**Correction.** Take `core.worktree` from the same `-z` record read as every other key. Then the embedded/trailing newline survives and `resolve_guarded` :352 refuses it as `ambiguous-path`.

### F3 · MEDIUM · design · calibration — `-c filter.<sub>.clean=` neutralization breaks on `=` and on subsection case
- **`=` in the subsection.** Git splits a `-c` argument at the **first** `=` (`config.c:660`, `string_list_split(…, "=", 1)`).
  - Counterexample: `[filter "a=b"] clean = <cmd>`, plus `.gitattributes`: `* filter=a=b`.
  - `-c "filter.a=b.clean="` sets the valid two-level key `filter.a` = `b.clean=`.
  - The driver is not neutralized and `<cmd>` runs on `status`. Fail-open.
- **Subsection case.** Subsections are case-sensitive, but :503 `${keys,,}` lowercases them, so `-c filter.x.clean=` does not neutralize `[filter "X"]`.
- **Why empty values would work.** Empty values do disable execution (`convert.c:1015-1019`, `cmd && *cmd` / `drv->process && *drv->process`). The open part is how the name is passed.

**Correction.**
- Pass neutralizers through `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_n` / `GIT_CONFIG_VALUE_n`. The key and value arrive separately (`config.c:759-775`), so there is no delimiter parsing. Keep the subsection bytes exactly as read from `-z`.
- `--config-env` splits at the last `=` (`config.c:508`). It is second-best.
- If the repair cannot do this, keep filters refused and say so.

### F4 · MEDIUM · current · operability — substring match refuses ordinary submodule names (:503-506)
Many peers report this class: DuplicateValues F6, PromisorSafe F4, FrontierLimits, AlternateRefs F6.

The most realistic counterexample: `git submodule add <url> include`. This writes `submodule.include.url` and `submodule.include.active` to `.git/config`. That key matches `*include.*`, and the whole census exits 2 with no TSV. `*` in a bash `case` pattern also spans the joined lines (:503-505).

**Correction.** Parse each `-z` record as follows:
- section = text before the first `.`, lowercased
- variable = text after the last `.`, lowercased
- subsection = everything between them, verbatim. `includeIf` conditions such as `gitdir:/a.b/` contain dots.

Then match exact triples.

### F5 · MEDIUM · current (pre-existing, adjacent) · calibration — pointer files are parsed differently from git
Affected lines:
- gitfile: `gitfile_admin` :529-541 and :636-646
- commondir: :586-593, :618-625, :655-661
- worktree registration: :565

Census behaviour:
- Reads only the **first line**.
- Accepts `gitdir:` with no space.
- Strips **leading** whitespace (:534, :587, :619, :641, :656).

Git behaviour:
- Reads the whole file.
- Requires the literal `gitdir: ` prefix.
- Strips only **trailing** CR/LF (`setup.c:999-1018`, `:333-336`). `worktree.c:152-156` rtrims the whole file instead.

**Counterexample:** linked worktree `W/.git` = `gitdir: W/x<NL>/..`.
- The census guards `W/x`; a real benign directory passes.
- Git resolves the symlink `W/x<NL>` → `~/.omp/agent/sessions`, then `..`, which lands in the store root.
- `is_git_directory` then stats store entries before failing.

A leading-space variant `gitdir:  /p` works the same way: git treats it as relative `W/ /p`, while the census checks `/p`.

**Impact.** Mostly store metadata access (stat/open) rather than content. [INFERENCE: not executed.]

**Correction.**
- Read the whole file with `IFS= read -r -d ''`.
- Require the exact `gitdir: ` prefix.
- Strip only trailing CR/LF.
- Refuse any remaining control character or leading whitespace.

### F6 · LOW · current · calibration — control characters other than `\n\t\r` reach stderr (:352, :391, :812, :161)
- A value-derived path containing ESC or other C0 bytes passes the ambiguity check and is printed raw by `protected_fail`. That allows terminal escape injection.
- **Correction:** refuse `*[[:cntrl:]]*` at those three checks.
- New refusals must print the key name and the cfg path only, **never the value**. Remote URLs can carry tokens.

### F7 · LOW · design · calibration — do not evaluate `includeIf` conditions in bash
- A quoted pattern compares literally, so it never matches. The include would be skipped while git applies it: fail-open.
- An unquoted pattern uses bash glob/extglob semantics, which differ from git's wildmatch rules: auto-prefixed `**/`, trailing `/`→`/**`, `./`, real-home `~/` (`config.c:207`), `gitdir/i`, `hasconfig:`, `onbranch:`.
- **Correction:** guard every `includeif.*.path` regardless of its condition (a superset). The cost is a refusal only when a non-applicable conditional include points into the store. Disclose that as a tradeoff.

### F8 · LOW · design · operability — neutralized keys need no value read
- `core.hooksPath`, `core.excludesFile`, `core.attributesFile` and `core.fsmonitor` are overridden on `status` (:710-712).
- The other verbs (`worktree list`, `for-each-ref`, `rev-list`, `rev-parse`) run no hooks, fsmonitor, excludes or attributes [INFERENCE from verb semantics].
- So these keys can be admitted **without reading or path-checking their values**. That removes their whole injection and `:(optional)`/`~user` parsing surface.
- A `guard_target` on the `hooksPath` value would add false refusals for benign values such as `~/.githooks`, and no safety.
- To harden this, apply the same neutralizer env to every repo-scoped git call, so a future verb cannot regress it.

## Acceptance cases proposed to ConfigFixture / L1 (not executed)
Each case is paired: r14 baseline vs repaired tool, with a synthetic HOME under `/var/tmp`, a marker-file oracle, and the existing strace store-access oracle.

| id | setup | repaired expectation |
|---|---|---|
| CI-01 | F2: `worktree = "../w\n"` + `w<NL>`→store | exit 2 `ambiguous-path`; 0 store syscalls (baseline: store access) |
| CI-02 | F1: `include.path=":(optional)evil.inc"`, nested include → store | exit 2 `credential-store`; 0 store syscalls |
| CI-03 | F3: `[filter "a=b"] clean=<marker cmd>` + attrs `filter=a=b`, stat-dirty file | marker absent (neutralized) or refusal; never marker present |
| CI-04 | F3: `[filter "X"]` uppercase, marker cmd | marker absent |
| CI-05 | F4: `submodule.include.url`, `remote.include.url` | row emitted, exit 0 (baseline exit 2) |
| CI-06 | shell-syntax benign values: `user.name="$(touch M)\`touch M\`;x"`, `core.hooksPath="-x;$(touch M)"` | row emitted; marker M absent |
| CI-07 | option-looking `include.path="--exec-path=/x"` (relative, missing) | guarded as `<gitdir>/--exec-path=/x`; row emitted |
| CI-08 | value-less `remote.o.promisor` vs `promisor =` | refuse (true) vs admit (false); decided with `--type=bool` |
| CI-09 | ESC byte in a value-derived path | refusal stderr has no raw ESC |
| CI-10 | F5: gitfile embedded newline and leading-space variants | refusal; 0 store syscalls |

## Disclosures
- **Boundary violation, not repeated.** My first call was `grep` on the lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` (pattern `git config|config --get|…`). Its output included matching lines from `census/operator-sweep-20261019/` (`.classify.json`, `.classify2.json`, `.staged.json`, `classification-final.json`, `quarantine-mtimes-t0.tsv`, `tmp-before.txt`, `tmp-removed.tsv`). Those files were not opened, edited or copied. After SoujiR15's reminder, every later search was scoped to explicit tool, round-15 or `/var/tmp` source paths.
- Git v2.55.0 source files were downloaded with `curl` to `/var/tmp/ci-r15-src/` for reading only, then deleted. No git behaviour was executed or probed.
- Not opened: `~/.omp/agent/**`, any auth or credential file, sibling repos.
- Tools installed or updated: none. No pacman transaction.
- All impact statements are [INFERENCE] from source reading. L1 must observe them through the acceptance cases above.
