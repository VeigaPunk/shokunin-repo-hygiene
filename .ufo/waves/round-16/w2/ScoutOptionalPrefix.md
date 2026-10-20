# Scout — `:(optional)` pathname prefix: which keys honor it (C1 census config guard)

Seat: SoujiR16.ScoutOptionalPrefix-4. Recon only; no lane file edited except this report.
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Installed git: **2.56.0** (`git --version`, 2026-10-20).
All URLs below accessed **2026-10-20**. Web reads are source inspection only; nothing was executed
against a real repository (PROBE RULE: no census run, no fixture). Counterexamples below are derived
from source, not run — they are labelled where they are inference.

HEAD note: the assignment names lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`, but the
worktree is now at `163158a706352f1c0ee3521c4da2e5289970db57` (L1's lesson/SOURCES commit).
`tools/souji-census.sh` is byte-identical at both: blob `b8442e2ead501ad0ba1f68472e265516040f4aa0`
(same as `0a70bef`), and the worktree copy hashes to the same blob. Every census line number below
is therefore valid for HEAD as assigned and as present.

## Question

Which config keys honor the `:(optional)` prefix — `core.excludesFile`, `core.attributesFile`,
`core.worktree`?, `include.path`? — per git-config docs and `config.c`, and what does that mean for
the C1 census guard?

## Short answer

| key | honors `:(optional)`? | evidence |
|---|---|---|
| `core.excludesFile` | **YES** (git >= 2.52) | environment.c:492-495 → `git_config_pathname()` |
| `core.attributesFile` | **YES** (git >= 2.52) | environment.c:363-366 → `git_config_pathname()` |
| `core.worktree` | **NO** | setup.c:593-597 stores `xstrdup(value)`; used literally |
| `include.path` | **NO** | config.c:142-190 `handle_path_include()` uses `interpolate_path()` only |
| `includeIf.<cond>.path` | **NO** | same handler, config.c:439-447 |

The prefix is not a pathspec feature and not a parser-wide feature. It is honored exactly by
variables parsed through `git_config_pathname()` (“pathname” type), and by nothing else. The
docs’ generic `pathname::` paragraph describes that type, not all path-looking keys.

## Source evidence

### Mechanism (git 2.56.0 and master)

`git_config_pathname()` is the only site that strips the prefix. v2.56.0 `config.c:1321-1335`
(https://raw.githubusercontent.com/git/git/v2.56.0/config.c):

```c
bool is_optional;
...
is_optional = skip_prefix(value, ":(optional)", &value);
path = interpolate_path(value, 0);
...
if (is_optional && is_missing_file(path)) {
	free(path);
	*dest = NULL;
	return 0;
}
```

`is_missing_file()` (`wrapper.c:802-812`, same URL base) is `stat()` plus ENOENT; other stat errors
die. So “missing” follows symlinks and means ENOENT.

Docs, `Documentation/config.adoc:415-416` (v2.56.0):
> “If prefixed with `:(optional)`, the configuration variable is treated as if it does not exist, if the named path does not exist.” (22 words)

Release note, `Documentation/RelNotes/2.52.0.adoc:54-56` (master):
> “Configuration variables that take a pathname as a value (e.g. blame.ignorerevsfile) can be marked as optional by prefixing ":(optional)" before its value.” (23 words)

Version floor is **2.52.0**, not older:
- `v2.51.0/config.c` `git_config_pathname()` is the plain `interpolate_path` form with no
  `is_optional` (https://raw.githubusercontent.com/git/git/v2.51.0/config.c).
- `v2.52.0/config.c:1279-1294` already contains `is_optional`/`skip_prefix`
  (https://raw.githubusercontent.com/git/git/v2.52.0/config.c).
- `RelNotes/2.52.0.adoc:54` announces it.

Two supporting behaviours worth knowing:
- `git config --type=path` also honors it: `builtin/config.c:350-351` calls `git_config_pathname()`
  (https://raw.githubusercontent.com/git/git/v2.56.0/builtin/config.c). The test fixture
  `t/t1300-config.sh` (master) has `missing=:(optional)no-such-path` and `exists=:(optional)expect`
  (lines 2530-2533); the `list --type=path` expectation contains `section.exists=expect` and omits
  `section.missing` (https://raw.githubusercontent.com/git/git/master/t/t1300-config.sh).
- `git_configset_get_pathname()` also routes through `git_config_pathname()` (config.c:2018-2020 in
  master), so programmatic pathname reads inherit the behaviour.

### Key-by-key

**`core.excludesFile` — YES.**
`environment.c:492-495` (v2.56.0):
```c
if (!strcmp(var, "core.excludesfile")) {
	FREE_AND_NULL(cfg->excludes_file);
	return git_config_pathname(&cfg->excludes_file, var, value);
}
```
Docs call it a pathname (`Documentation/config/core.adoc:488-492`):
> “Specifies the pathname to the file that contains patterns to describe paths that are not meant to be tracked” (20 words)
URL: https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/core.adoc

**`core.attributesFile` — YES.**
`environment.c:363-366` (same file) calls `git_config_pathname()`. Docs call it a pathname
(`core.adoc:505-509`: “Specifies the pathname to the file that contains attributes”).

**`core.worktree` — NO.**
`setup.c:588-598` (v2.56.0):
```c
} else if (strcmp(var, "core.worktree") == 0) {
	if (!value)
		return config_error_nonbool(var);
	free(data->work_tree);
	data->work_tree = xstrdup(value);
```
It is then applied literally: absolute values are passed through, relative values are resolved with
`chdir(gitdirenv); chdir(value)` (`setup.c:1193-1202`), and `repo_set_worktree()` only calls
`real_pathdup()` (`repository.c:252-255`). There is no `interpolate_path()`, no `~` expansion, and no
`:(optional)` strip anywhere on that path. The one `interpolate_path()` in `setup.c` (line 1851) is
`enter_repo()`, a completely different entry point. Docs (`core.adoc:327-347`) also promise only:
> “The value can be an absolute path or relative to the path to the .git directory” (20 words)
URL: https://raw.githubusercontent.com/git/git/v2.56.0/setup.c
URL: https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/core.adoc

**`include.path` / `includeIf.<cond>.path` — NO.**
`config.c:142-190` (`handle_path_include`) calls `interpolate_path(path, 0)` and nothing else:
`interpolate_path()` (path.c:698-746) recognizes only `%(prefix)/` and `~`; it copies
`:(optional)foo` through verbatim. Both call sites use it: `include.path` at config.c:436-437 and
`includeIf.*.path` at config.c:439-447 (v2.56.0,
https://raw.githubusercontent.com/git/git/v2.56.0/config.c).
A missing include is already silent, independent of the prefix: `access_or_die(path, R_OK, 0)`
treats ENOENT/ENOTDIR as OK (`git-compat-util.h:1065-1068` and `wrapper.c:716-739`), so
`include.path` is skipped when absent. Therefore the prefix is inert there except as part of a
literal filename: a file actually named `:(optional)foo` would be included.
Docs are the only source of ambiguity: `config.adoc:93-96` says
> “The variable takes a pathname as its value, and is subject to tilde expansion.” (15 words)
so the include section reads as if the generic pathname paragraph applied; the implementation does
not apply the optional strip. This is a doc/code nuance, not a behavior question — behavior is NO.

## Relation to `tools/souji-census.sh` at HEAD (blob b8442e2)

The census comments and code reference:

- lines 562-564 (comment): “Callers strip `:(optional)` themselves where git honors it (pathname
  keys, not include.path).”
- line 640: include branch — `expand_config_path "$val"` (no strip).
- line 652: `core.excludesFile`/`core.attributesFile` branch — `expand_config_path "${val#:(optional)}"`.
- line 660: `core.worktree` branch — `expand_config_path "${val#:(optional)}" "$dir"`.
- lines 939-941 (status comment): “an `:(optional)` value whose target is missing counts as unset.”
- lines 947-951: `status_info_file()` strips, then `[ -e "$tgt" ] || rc=1` (missing → unset → XDG).

### Holds

- **include.path/includeIf target resolution (line 640).** No strip, literal resolution, missing
  target accepted. This matches `handle_path_include` + `interpolate_path` exactly, including the
  literal-file edge case. Holds.
- **`core.excludesFile`/`core.attributesFile` value model (line 652, 947-951).** Stripping and
  “missing optional target = unset, then XDG default” matches `git_config_pathname()` on the
  installed git 2.56.0. Holds on git >= 2.52.
- The claim “not include.path” holds; the include handler genuinely does not support the prefix.

### FAILS — `core.worktree` is not a pathname key; line 660 strips a prefix git never strips

Git stores `core.worktree` verbatim (`setup.c:597`), so `:(optional)` is part of the path, and a
missing worktree is still fatal to git (setup chdir). The census treats the value as an optional
pathname and drops the prefix. Two concrete divergences:

**C-A (whole-run false refusal; exit 2 where git simply fails the one repo).**
Repo config `[core] worktree = :(optional)/home/vgpnk/.omp/agent`:
- git: value starts with `:`, so `is_absolute_path()` is false; setup resolves it relative to the
  gitdir as `<gitdir>/:(optional)/home/vgpnk/.omp/agent` (nonexistent; that repo's git commands
  fail, but nothing protected is read).
- census line 660: `${val#:(optional)}` → `/home/vgpnk/.omp/agent`, then
  `guard_config_path core-worktree-protected` performs its lexical protected test first
  (`souji-census.sh:547-549`) and calls `protected_fail` → stable finding `path-protected`, **exit 2
  for the whole census**. That is the r14-style value-blind abort that round 16 exists to remove; the
  same input under the intended model (prefix kept) would be an unresolvable relative path → one
  `error` row, or git’s own failure → `status-unverifiable`. Fails the script’s own
  value/effect-aware promise (header lines 93-96).

**C-B (guard-completeness, [INFERENCE] from path arithmetic; not executed).**
For a relative value the literal `:(optional)` component consumes one `..` under git but is deleted
by the census, so the two resolves sit one directory apart. With value
`:(optional)../../../.omp/agent` and gitdir `/home/vgpnk/repo/.git`:
- git: `<gitdir>/:(optional)/../../../.omp/agent` = `/home/vgpnk/.omp/agent` (the protected store);
- census: `${val#:(optional)}` = `../../../.omp/agent` from `<gitdir>` = `/home/.omp/agent`
  (unprotected).
Preconditions: the repo creator ships a directory `.git/:(optional)/` (trivial for the repo owner),
and the census-resolved shadow path `/home/.omp/agent` exists and is unprotected. Then the guard
passes and the census runs git in a repo whose effective worktree is the agent store — a fail-open
against the boundary. If either precondition fails, git dies (ENOENT on the literal component) or
the census degrades to one error row; the mismatch is latent rather than exploitable in that layout.

**Smallest fix:** line 660 must not strip: `expand_config_path "$val" "$dir"`. Even that leaves the
tilde issue: `expand_config_path()` expands `~/`, but git does not interpolate `core.worktree` at
all (`xstrdup`), so `~/x` is a relative literal for git and `$HOME/x` for the census. Model
`core.worktree` literally — absolute as-is, otherwise join to `$dir`, no `~`/`%(` expansion — or
drop the branch and degrade the repo to one `error` row when it cannot be modelled. Also correct
the line 563 comment: `core.worktree` is not a pathname key; the strip is valid only for
`core.excludesFile` and `core.attributesFile`.

### PARTIAL — optional+missing target inside a protected root still aborts the run

`status_info_file()` (line 951) correctly treats a missing optional target as unset, but the config
scan (line 652) guards *before* checking existence. `[core] excludesFile = :(optional)~/.omp/agent/ignore`
(and the attributes equivalent), where that file does not exist:
- git 2.56: strip prefix, expand `~`, `stat` ENOENT → variable set to NULL → excludes file unset,
  never reads the store.
- census: strip, expand, `guard_config_path` lexical protected test → `protected_fail`, **exit 2
  whole run**, although the census itself elsewhere models this exact value as “unset”.
This contradicts lines 939-941 and the “only a protected reach refuses” rule; the reach has no
effect. **Smallest fix:** in the `core:excludesfile|core:attributesfile` branch, mirror
`status_info_file`: if the raw value starts with `:(optional)` and the expanded target is missing
(`[ -e ]`, which, like `is_missing_file()`, follows symlinks), `continue` without guarding.
(Residual: EACCES/ENOTDIR differ — git 2.56 dies in `is_missing_file()` for non-ENOENT stat errors
while `[ -e ]` is simply false. Treat that as unmodelled/degrade, not as absent.)

### PARTIAL — unstated git-version precondition

The strip in lines 652/947 is only correct for git >= 2.52.0 (`v2.51.0/config.c` has no
`is_optional`; `v2.52.0` does; RelNotes 2.52). The script’s only version reference is “git >= 2.45”
for `GIT_NO_LAZY_FETCH` (lines 115-116, 155-156), so a host on 2.45-2.51 would get a census model
that disagrees with its own git (git would treat `:(optional)…` literally, census strips it and
passes the stripped path via `-c core.excludesFile=…` / `-c core.attributesFile=…`). **Smallest
fix:** state/require git >= 2.52 in the header (or `git version` gate the strip and degrade to the
literal interpretation below 2.52). On the workstation’s git 2.56.0 this is not a live defect.

## Confidence

- Source facts (functions, call sites, version floor, test expectations): **high** — read at
  v2.56.0/v2.51.0/v2.52.0 tags, not inferred from memory.
- C-A: **high** — follows directly from setup.c literal handling and census lines 547-549 + 660.
- C-B: **medium** — path arithmetic is exact, but fail-open additionally requires the shadow path
  to exist; marked INFERENCE and not executed.
- Fleet impact wording: **inference**; no census was run.

## Remaining unknowns

- No runtime test of any counterexample (probe rule); no git repository was created or mutated.
- Whether the census intends to support hosts older than git 2.52 (header names only 2.45).
- `expand_config_path()`’s `~/` expansion for `core.worktree` is a second divergence from
  setup.c’s literal `xstrdup`; not separately counterexampled.
- `is_missing_file()` dies on stat errors other than ENOENT (EACCES, ENOTDIR); the census’s `[ -e ]`
  check cannot distinguish those from absent. Edge, not modelled.

STATUS: FAIL — census strips `:(optional)` for `core.worktree`, which git parses literally
(`setup.c:597` `xstrdup`); `souji-census.sh:660` can abort the whole run on a benign config and, for
relative values, resolve one level away from git’s effective worktree.

## Commands

```
git --version
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD HEAD:tools/souji-census.sh && git -C /home/vgpnk/Projects/shokunin/souji-shokunin hash-object tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -5 -- tools/souji-census.sh && git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae^{commit} a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae:tools/souji-census.sh
```
