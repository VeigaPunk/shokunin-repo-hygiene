# Round 15 w1 — MetadataFlow (scout): configs → object-store / worktree / include reads, first-access ordering

Seat: `SoujiR15.MetadataFlow`, leaf, axes operability + calibration. Report only; no edits,
tests, probes, builds, or installs. Lane HEAD `cc2168325768d5356a82c039dcdf787377c55784`.
Source snapshot: `tools/souji-census.sh` sha256
`fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`, 55730 bytes,
mtime 2026-10-20 04:56:30.745043852 -0300, `git diff --quiet` = unmodified vs HEAD.
The C1 repair is **absent** from the tree at inspection; every "repaired" statement below is
**[DESIGN]** and carries its exact acceptance. Line numbers are the pinned snapshot and will
move under ConfigRepair.

External primary sources: installed git 2.55.0-1 manuals (`git-config(1)`, `gitattributes(5)`,
`gitignore(5)`, `gitrepository-layout(5)`) and git tag `v2.55.0` source at
`raw.githubusercontent.com/git/git/v2.55.0/{config.c,setup.c,worktree.c,builtin/worktree.c,convert.c,path.c,wrapper.c,promisor-remote.c,git.c}`.
Confidence: H = quoted source/doc, M = source + one stated assumption, L = design inference.

## 0. Boundary disclosure

Two early discovery calls predate the authoritative no-query reminder; disclosed, not repeated:

- `grep` over the whole lane root with pattern `guard_git_surface` (gitignore on). It is
  unscoped, so the walk may have opened files under `census/operator-sweep-20261019/`.
  Printed hits were only `.ufo/waves/**` markdown and `tools/souji-census.sh`; no
  operator-sweep path or content was printed, used, or quoted. I cannot certify the bytes
  were not read.
- `git status --short`, `git diff --stat`, `git log --oneline -3`, `git diff --quiet` at the
  lane root. Metadata only; `git status` printed the untracked directory *name*
  `census/operator-sweep-20261019/`, not its contents. No census, selftest, fixture, or other
  tool execution followed; `sha256sum`/`stat`/`awk`/`zcat` only on explicit files.

All later reads used explicit paths: `tools/souji-census.sh` ranges,
`.ufo/waves/round-15/*`, `census/round-15/claims.json`, round-15 w1 reports, installed man
pages, git v2.55.0 sources. No credential file, no `~/.omp/agent`, no install.

## 1. Git 2.55.0 config read order (authoritative)

1. **system** `$(prefix)/etc/gitconfig`: skipped — `GIT_CONFIG_NOSYSTEM=1` (tool :123;
   `config.c:1555,1570-1576`).
2. **global** `$XDG_CONFIG_HOME/git/config`, `~/.gitconfig`: replaced by `/dev/null`.
   `GIT_CONFIG_GLOBAL` is set (tool :122); `git_global_config_paths` leaves `xdg_config`
   NULL when it is set (`config.c:1535-1543`), so only `/dev/null` is read
   (`config.c:1579-1585`). XDG ignore/attributes *defaults* are separate (see R9).
3. **local** `<commondir>/config` (`config.c:1553-1566,1587-1590`); for a linked worktree
   `commondir` comes from `<admin>/commondir`, and for a shared `.git` directory from
   `.git/commondir` (`repository.c:259-266`).
4. **worktree** `<gitdir>/config.worktree` only when
   `repo->repository_format_worktree_config` is set and the file is readable
   (`config.c:1592-1597`). `<gitdir>` is the per-worktree gitdir: `.git` for the main
   worktree, `worktrees/<id>` for a linked one (`config.c:1563-1564`). The gate flag is set
   by the **early repository-format read** of the *literal* `<commondir>/config`
   (`setup.c:753-794`), which runs with `opts == NULL` and therefore **does not follow
   includes** (`config.c:1410-1432`; the include wrapper exists only under
   `opts->respect_includes`, `config.c:1619-1627`). Consequences: an
   `extensions.worktreeConfig` set only inside an included file has **no effect**; and a
   literal `true` causes a second literal read of `<gitdir>/config.worktree` for
   `core.bare`/`core.worktree` **before** the general parse (`setup.c:787-794`).
5. **command** `-c` (`config.c:1600+`; docs FILES), highest precedence; the status pins at
   tool :710-712 live here.

Include semantics (all scopes): contents are inserted at the directive
(`config.c:168-181`); relative targets resolve against the **including file's directory**;
`~/` uses `$HOME`, `~user/` uses `getpwnam` (`path.c:690-720`); `access(R_OK)` is tested
before the open, so a missing target (ENOENT/ENOTDIR) is silently skipped while EACCES is
fatal (`wrapper.c:650-658`, `config.c:177`); depth > 10 dies (`config.c:135,178-184`);
`include.path` is multi-valued. `--file` queries are include-free by default; the guard's
`--no-includes` (:500) matches that default and keeps the guard's own read set to one file.

Conditional includes (`config.c:204-320,396-413`):

- `gitdir`/`gitdir/i`: match the **final gitdir** (admin dir for linked worktrees), first
  against `realpath(gitdir)`, then against the non-realpath absolute spelling; pattern
  `~/` is realpath(`$HOME`), `./` is the **realpath directory of the config file**, a
  non-absolute pattern gets `**/`, a trailing `/` gets `**`; `../` is literal;
  `wildmatch(WM_PATHNAME[, WM_CASEFOLD])`.
- `onbranch`: resolves `HEAD` through the ref backend (`refs_resolve_ref_unsafe`,
  `config.c:299-320`) — i.e. HEAD is read **during config parsing**, before the command's
  own ref work; detached HEAD, unborn branch, and bare repositories yield no match.
- `hasconfig:remote.*.url`: the first occurrence triggers `populate_remote_urls`
  (`config.c:342-367`), which re-reads the whole config closure with
  `unconditional_remote_url = 1`. In that scan `include_by_remote_url` returns true
  immediately, so **every hasconfig include target is read regardless of whether any URL
  matches**; only the *application* of its values is conditional. gitdir/onbranch
  conditions are still evaluated normally during the scan.
- Unknown condition keyword → false (`config.c:410-413`).

## 2. Census command / read sequence per row

`census_one` (:844): guard at :847 (`guard_git_surface`), then

- **T1** `git -C "$repo" rev-parse --is-inside-work-tree` (:859)
- **T2** `git -C "$repo" worktree list` (:688, via :866) and later
  `git -C "$repo" worktree list --porcelain` for extra flags (:836, via :872)
- **T3** `for-each-ref` / `rev-list` (:694,:698,:702, via :867)
- **T4** `status --porcelain` with four `-c` pins (:710-716, via :870)
- **T5** per linked worktree: `guard_git_surface "$cpath"` (:831) then `count_dirty`
  (:832)

`guard_git_surface` itself (:603-672) orders: `.git` link check; gitdir resolve →
`guard_git_links` → `guard_git_files` → `guard_git_config` (:610-613); then commondir →
re-guard common (:625-628); then `guard_alternates` (:631/:668); then
`guard_worktree_registrations` (:632/:669). Registration admin files are checked only when
the admin `gitdir` content ends in `/.git` (:572-597).

First-access map (what git opens, in order):

| step | git opens | config-induced? |
|---|---|---|
| T0 | nothing (guard's own single-file `git config --file`) | no |
| T1 | `.git`/gitfile → admin; `commondir`; **literal** `<commondir>/config`; if gate: **literal** `<gitdir>/config.worktree`; then general parse `<commondir>/config` + include closure, then `<gitdir>/config.worktree` + include closure | yes: includes, gate, `core.bare`/`core.worktree` |
| T2 | `worktrees/*/gitdir`, each admin `HEAD`, `locked`; **from a non-current main worktree** (linked row): literal `<commondir>/config.worktree` (`worktree.c:96-110,127-134`; `git_configset_add_file` → include-free `git_config_from_file`, `config.c:1830-1833`) | yes: unconditional `config.worktree` read |
| T3 | refs / `packed-refs` (or reftable), `objects`, `info/alternates`, commit-graph; promisor lazy fetch on missing object | yes: promisor, refStorage |
| T4 | index (`sharedindex.*` if split), `info/attributes`, in-tree `.gitattributes`, `core.attributesFile` (pinned), `/etc/gitattributes`, `info/exclude`, `.gitignore`, `core.excludesFile` (pinned), `info/sparse-checkout`, worktree files; clean/process filters | yes: filter, attrs/excludes values (pinned) |
| T5 | as T1 on `$cpath` (branch differs → different `onbranch` include set), then T4 again | yes |

## 3. Config → read/exec matrix (baseline :603-672, :844-872)

| key / family | read site & order | first census consumer | effect | baseline | repair requirement |
|---|---|---|---|---|---|
| `include.path` | every general config parse (T1 for the row, T5 per worktree) | :859 | reads target file; injected keys take effect immediately | key-presence refused (:505) | walk all values; type/namespace-check target **before** read; parse each with `--no-includes`; ENOENT/ENOTDIR ignored; EACCES → `git-config-unparsed`; `~user`/`~/`/relative-to-includer expansion; depth 10 [H] |
| `includeIf.gitdir`, `gitdir/i`, `onbranch` | same; condition evaluated per worktree | :859/:832 | reads target only if condition true | refused | mirror `config.c:204-320` (realpath + absolute spelling; `./` realpath; `**/`; `/**`; HEAD symref); if not exact, treat as possibly true and guard target [M] |
| `includeIf.hasconfig:remote.*.url` | scan forces condition true | :859 | target read **always** once a hasconfig directive exists; values only if a URL matches | refused | guard every hasconfig target unconditionally; condition affects values only [H] |
| `extensions.worktreeConfig` | early literal `<commondir>/config` only | T1 setup | enables `<gitdir>/config.worktree` (literal early read + full general parse) | key-presence refused (:505) | value-aware bool gate from literal common config; for linked admin, resolve commondir **before** deciding; off ⇒ do not parse [H] |
| `<gitdir>/config.worktree` | T1 setup (literal, `core.bare`/`core.worktree`), T1 general (all keys + includes), T2 **unconditional common one** from a linked row | :859, :866/836 | gate-dependent, except T2 common read is **not** gate-dependent | not in `guard_git_files` (:477), not parsed (:495,499); admin call returns at :499 | add `config.worktree` to fixed-file type/nlink check for common dir and every admin dir before :859/:866; parse only when gate on; T2 common read needs type check even when gate off [H] |
| `core.worktree` (local/common) | early literal commondir config, then literal config.worktree overrides | T1 setup | chooses worktree root status walks; relative base = **that worktree's gitdir** (`core.adoc:327-335`, `setup.c:1157-1166`) | value-aware (:511-520) but base is `$dir`; at :628/:665 `$dir` is **commondir**, not gitdir | resolve against the actual gitdir (admin for linked, `.git` for dir branch even with commondir); expand `~`/`~user` instead of refusing (:514); includes are **not** effective for this decision — literal values only [H] |
| `core.worktree` (config.worktree) | early literal + general | T1 | same | unguarded | same value/boundary check from config.worktree, base = that gitdir [H] |
| `core.attributesFile` | status only | :870 | attr file read | key refused (:505) | admit; `-c core.attributesFile=/dev/null` (:712) wins (command scope) [H] |
| `core.excludesFile` | status only | :870 | ignore file read | key refused | admit; `-c ...=/dev/null` (:711) wins [H] |
| `info/attributes`, `info/exclude`, `info/sparse-checkout` | status | :870 | fixed files in common/per-worktree gitdir | only `info/exclude` is type/nlink-checked | pre-existing FIFO/hardlink residual; sparse-checkout path reads are enabled by `core.sparseCheckout` [M] |
| `filter.*.clean`, `filter.*.process` | status index refresh (`convert_to_git`, `convert.c:1473`; shell exec `convert.c:659-661`) | :870 | arbitrary shell exec, content read | key refused | either keep a specific refusal or neutralize per driver by enumerating drivers from the guarded closure and appending `-c filter.<d>.clean= -c filter.<d>.process=` to :710 (dirty-count semantics change for LFS-like filters) [H/M] |
| `filter.*.smudge`, `filter.*.required` | checkout only | none | not reached by any census command | refused by the same glob | admit; smudge-only/required-only are inert here [H] |
| `core.fsmonitor` | status | :870 | spawns hook program | not refused; pinned false (:710) | admit; pin stays [H] |
| `core.hooksPath` | none | none | no census command runs hooks | refused | admit; refusal is pure harm [H] |
| `core.alternateRefsCommand` | alternate-tip advertisement only (`config/core.adoc:297-300`) | none (`--alternate-refs`/upload-pack never run) | shell exec otherwise | refused | admit; document "not executed by these commands" [H/M] |
| `remote.*.promisor`, `extensions.partialClone` | object lookup during T1/T3/T4 | rev-list/status | lazy **fetch** (network or `file://`/path remote) on missing object | refused | admit plus `GIT_NO_LAZY_FETCH=1` (`git.c:203-207` sets `fetch_if_missing=0`; `promisor-remote.c:30-38` skips fetch). Side effect: rev-list failure at :698/:702 falls back to `0` — silent unverifiable zero [H] |
| `extensions.refStorage`, `core.splitIndex` | refs/object reads | T1/T3 | reftable dir / `sharedindex.<oid>` reads inside gitdir | not refused | no path refusal needed; dynamic-name FIFO/hardlink residual [M] |
| `core.bare` (config.worktree) | early literal | T1 | bare ⇒ status/row semantics; also T2 main-bare check | unguarded when gate admitted | type-check/parse with config.worktree [H] |
| `status.showUntrackedFiles`, `status.*` | status | :870 | count semantics, no external path | not refused | owned by GitSourceStatus; no boundary refusal [H] |
| `submodule.recurse` | status not affected (`submodule.adoc:80-87` list excludes status); `--ignore-submodules=all` also | none | no submodule repo access | not refused | admit [H] |

Object-store specific: `objects/info/alternates` is already read by `guard_alternates`
(:415-471) before any git; promisor fetch is the only config-controlled path that can reach
a **local** store path (`remote.<n>.url` = path / `file://`), and `GIT_NO_LAZY_FETCH=1`
removes it without a value refusal. No config key relocates `GIT_OBJECT_DIRECTORY`
(the environment is cleared at :119-120).

## 4. First-access ordering requirements (acceptance for ConfigRepair)

Ordering invariant: **T0 must validate every file T1-T5 will open, in the worktree that
will open it.** T1(T5) re-parses the whole config closure, so include/config.worktree
checks at :847/:831 cannot be deferred to the command sites.

1. **Gate before worktree file.** Read `extensions.worktreeConfig` from the literal
   `<commondir>/config` with `--no-includes --type=bool`; rc 1 = absent/off. For a linked
   row, resolve commondir before deciding (current :650 runs before :651-665).
2. **Type-check every `config.worktree` before the first git call**: `<commondir>/config.worktree`
   (T2 read, gate-independent) and `<gitdir>/config.worktree` (gate-dependent). Add it to
   the `guard_git_files` list (:477) for common and each admin dir, or an equivalent
   `[ -e ] && ! -d` + `stat -L %h` check; refuse FIFO/device/socket and nlink>1. Parsing
   keys is required only for the gate-on files; the gate-off common file is read literally
   by `git worktree list` (`worktree.c:96-110`) and must at least be type-safe.
3. **Include walker**: enumerate with `git config --file F --no-includes -z --name-only --list`
   (secure key/value parsing, `-z`), take every `include.path` and
   `includeif.*.path` value; expand `~/` (HOME), `~user/` (passwd), relative to `F`'s
   directory; `guard_target` the result, then file-type/nlink check, then parse that file
   with `--no-includes`; recurse with depth cap 10 and git's die-on-depth behaviour. A
   target that is a symlink is resolved by `guard_target` (git follows it); ENOENT/ENOTDIR
   is skipped exactly as git skips it; EACCES/parse failure maps to `git-config-unparsed`.
   Never run `git config --file T` before guarding T (FIFO would block the guard).
4. **Guard the read set, not the value set, for includes**: unconditional includes and
   `hasconfig` targets are read even when their values are inactive; guard them
   unconditionally. gitdir/onbranch are only skippable if the matcher reproduces
   `config.c:204-320` exactly (realpath and absolute spellings, `./` realpath of the
   including file, `**/` prefix, `/**` suffix, HEAD symref per worktree); otherwise treat
   as true and guard.
5. **Effective-value order for path keys**: worktree scope after local, command `-c` last.
   For `core.worktree`, only the two *literal* files matter (early read has no includes);
   resolve against the actual gitdir of the reader, not `$dir` after the commondir
   reassignment (:625/:662). Keep one rule for main and linked.
6. **Worktree-list inputs**: `guard_worktree_registrations` must type/nlink-check each
   `entry/{HEAD,locked,config.worktree}` and the entry links, not only the `*/.git` case
   (:572-597); `worktree list` opens those before printing.
7. **Status pins stay** (:710-712); they are command scope and beat every admitted config
   value. If `filter.*` is admitted, add per-driver neutralizations from the same closure
   (requirement matrix row), or keep a specific filter refusal; otherwise admission is a
   command-execution hole. `smudge`/`required` alone are inert.
8. **Promisor admission requires `GIT_NO_LAZY_FETCH=1`** near :121-123, and calibrate the
   :698/:702 `|| printf '0'` fallback so a missing-object rev-list failure does not read as
   a clean zero.
9. **Header (:85-91) must describe effects**: includes are followed by later git commands
   (the guard's `--no-includes` is not the fence), `config.worktree` is read when enabled
   and also literally by `worktree list`, hooksPath is inert, excludes/attributes/fsmonitor
   are pinned on status, alternateRefsCommand is not invoked, promisor is fetch-disabled.
10. **Static invariants** (no runtime): no `git config --file` call on a path before its
    file-type/nlink check; every such call carries `--no-includes`; every include value
    passes through `guard_target` before its parse; the extension gate uses the literal
    common config; `core.worktree` resolution base is the gitdir variable, never the
    post-commondir `$dir`.

## 5. Corrections to sibling reports (material)

- **WorktreeCfg H5 is incomplete.** "Stray config.worktree with extension off: git never
  reads it" is false for `git worktree list` run from a **non-current** main worktree
  (`--include-root` on a linked worktree, added at :926-935): `get_main_worktree` calls
  `is_main_worktree_bare`, which unconditionally reads the literal
  `<commondir>/config.worktree` (`worktree.c:96-110,127-134`), no gate. Baseline therefore
  has an unguarded literal read at :688/:836 for that row shape even when
  `extensions.worktreeConfig` is off. This is a **pre-existing namespace hole** (open/read
  of a FIFO/hardlink there, symlinks already caught by `guard_git_links`), not introduced
  by the repair; the fixture should assert zero opens of a forbidden target placed there.
- **WorktreeCfg §2 point 4 / H2 base claim.** `"$dir/$wt"` does match git *inside*
  `guard_git_config`, but call sites :625-628 (dir branch with `.git/commondir`) and
  :662-665 (gitfile branch) reassign `$dir` to the **commondir** before calling it, while
  git resolves relative `core.worktree` against the **gitdir** (admin for linked). The
  value-aware check is therefore base-inconsistent for commondir layouts; keep a separate
  gitdir variable.
- **GitSourceIncludes F7** should add the read-set consequence: the `hasconfig` scan sets
  `unconditional_remote_url`, so hasconfig include targets are **read** even when no URL
  matches; only their values are conditional. A "condition false ⇒ no read" argument is
  unsound for that keyword.
- **GitSourceStatus F6 / FiltersSafe dependency**: the clean/process filter is reached by
  `status` (index refresh → `convert_to_git`, `convert.c:1473`, shell exec
  `convert.c:659-661`); `smudge` is not. That resolves the "not established" caveat.

## 6. Residuals / unknowns

- Hardlinks into the store are only refused for fixed metadata + `.git/config`; include
  targets, `config.worktree`, `info/attributes`, `info/sparse-checkout`, reftable and
  `sharedindex.*` remain undetectable without stat'ing the store (pre-existing class).
- TOCTOU: guard and git read are separate operations; every admitted file grows this
  window (header already discloses the general residual).
- `[UNK]` whether `git worktree list` reads per-worktree `config.worktree` for *other*
  registrations (source shows only the main/common one via `is_main_worktree_bare`; no
  observed trace).
- `[UNK]` `core.worktree` set only via an include: the early format read ignores it, so it
  should not move the worktree root; later `git_config` may set `git_work_tree_cfg` without
  re-rooting. Guard only literal values; confirm if fixtures show otherwise.
- `[UNK]` `%(prefix)/` and `:(optional)` pathname forms for include values (documented for
  pathname values generally; not pinned to `include.path` in the Includes section).
- `/etc/gitattributes` is still read by status (`GIT_ATTR_NOSYSTEM` unset): benign system
  path, outside the protected-namespace model; document if the header claims "only
  /dev/null globals".
- `core.ignoreStat`/assume-unchanged and `status.showUntrackedFiles` are calibration issues
  owned by GitSourceStatus; they do not create path reads.

## 7. Unrun checks (L1 after the wave)

- No census run, fixture, selftest, FIFO test, or strace/open-trace was executed here.
- Verify against the repaired tool: static invariants in §4.10; the §5 WorktreeCfg H5
  fixture (linked `--include-root` row + FIFO/hardlink `<commondir>/config.worktree` with
  the extension **off**); a commondir-layout `core.worktree` relative-base fixture; a
  `hasconfig` include whose URL does not match but whose target must still be guarded.
- Paired red (r14 blob) / green (repaired blob): safe include, safe `worktreeConfig`,
  promisor-with-fetch-disabled; refusals must keep zero opens of the protected target.
- Not certified; findings advisory.
