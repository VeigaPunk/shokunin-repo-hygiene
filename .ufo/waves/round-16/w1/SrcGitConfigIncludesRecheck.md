# SrcGitConfigIncludesRecheck — round 16 (git-config re-check for the census config guard)

Seat: `SoujiR16.SrcGitConfigIncludesRecheck` (leaf, scout). Opened 2026-10-20.
Scope: re-open **git-config(1)** for the five r16 census uses named by the assignment
(include relative-path base, `~/` expansion, `includeIf` conditions,
`core.alternateRefsCommand` consumer text, `--null`/`-z` list format), and draft
registry proposals. `corpus/SOURCES.md` was **not** edited; S042 was **not** rewritten.

Method: source review only. No census run, no fixture, and no repository-mutating command; the
only shell commands were read-only `diff --stat`/`rev-parse` on the lane repo itself. `tools/souji-census.sh`
in the working tree is byte-identical to `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
(`git diff --stat cbf688ab -- tools/souji-census.sh` printed nothing) and that commit is `HEAD`.
Everything below marked **Observed** is a document or tagged-source read; anything about
guard *behaviour* is **Inference** until L1's acceptance run.

---

## 1. Source record (access 2026-10-20)

| item | value |
|---|---|
| URL | https://git-scm.com/docs/git-config |
| title as served | `Git - git-config Documentation` |
| served version line | **“git-config last updated in 2.56.0”** (page header, above the version selector) |
| release date for that version (page index) | `2.56.0 … 2026-09-28` |
| access date | **2026-10-20** |
| installed vendor doc | `/usr/share/man/man1/git-config.1.gz`, roff line 7 `.\"    Source: Git 2.56.0`, line 10 `TH … "2026-09-27" "Git 2.56.0"` |
| installed set cross-check | `/usr/share/man/man1/git-maintenance.1.gz` and `/usr/share/man/man1/git-status.1.gz` carry the same `Source: Git 2.56.0` / `TH … 2026-09-27` header |
| tagged source read this round | `git/git` tag `v2.56.0`, `config.c` and `path.c` (raw at `https://raw.githubusercontent.com/git/git/v2.56.0/…`) |

**Calibration finding (C-A).** S042's anchor cell says “installed 2.55.0 corresponding
sections via SoujiR15.SourcesDraft”. Observed today: the installed man page set declares
**Git 2.56.0**, not 2.55.0, so that half of the anchor is stale. I did **not** verify the
installed `git` *binary* version (the probe rule does not authorise `git --version`), so the
report claims only what the man-page metadata says. This is a recheck-cell matter, not a
reason to distrust the quoted text: the installed 2.56.0 page contains the same sentences
(see anchors below).

---

## 2. Extracted facts, with quotes and anchors

### F1 — include relative-path base and insertion point (the r16 `include.path` base)
- Web § *Includes*: “The contents of the included file are inserted immediately, as if they
  had been found at the location of the include directive. If the value of the variable is a
  relative path, the path is considered to be relative to the configuration file in which the
  include directive was found.” (web line 1068 carries the insertion sentence and the
  relative-path sentence follows in the same paragraph; installed roff 1076 carries both)
- `include.path` value “takes a pathname as its value, and is subject to tilde expansion.
  These variables can be given multiple times.” (web 1064–1066; installed 1074)
- Example: `path = foo.inc ; find "foo.inc" relative to the current file` (web 1240;
  installed 1362)
- Tagged implementation: `config.c:158-162` — “Use an absolute path as-is, but interpret
  relative paths based on the including config file.” (`handle_path_include`, `config.c:142-145`)

**Consequence for r16:** “relative to the including file” is literal — not the repository,
not the worktree. `tools/souji-census.sh:611` passes `${cfg%/*}` as the base, which is that
directory. **Observed: matches** for the path form the guard models.

### F2 — `~/` expansion (and the other documented path forms)
- `include.path` is “subject to tilde expansion” (web 1066). § *Values › pathname*:
  “`~/` is expanded to the value of `$HOME`, and `~user/` to the specified user’s home
  directory.” (web 1362–1364)
- `%(prefix)/`: “the remainder is interpreted as a path relative to Git’s ‘runtime prefix’”,
  with a literal `./` escape (web 1366–1372).
- `:(optional)`: “If prefixed with `:(optional)`, the configuration variable is treated as if
  it does not exist, if the named path does not exist.” (web 1374–1375)
- `--type=path` canonicalisation repeats the `~`/`~user` rule (web 550–551).
- Tagged `path.c:698-746` `interpolate_path()`: `%(prefix)/ → system_path` (706–707);
  `~` → `getenv("HOME")`, `~user` → `getpw_str` (713–728). It does **not** strip `:(optional)`.
- Where `:(optional)` *is* handled: `config.c:1319-1328` `git_config_pathname()` —
  `is_optional = skip_prefix(value, ":(optional)", &value)`. `include.path` does **not** go
  through that function: it calls `interpolate_path(path, 0)` directly (`config.c:153`).

**Consequence for r16:** the guard's `expand_config_path` (`tools/souji-census.sh:540-551`)
expands `~/` via `$HOME`, treats everything else relative, and refuses `~*`/`%(` forms. That
matches `interpolate_path` for `~/` and relative paths, and *refuses* the two documented forms
it does not model. The `:(optional)` sentence in the doc does **not** apply to `include.path`
(tagged source, `config.c:153` vs `:1327`), so the guard's literal-relative treatment is
correct there — this is **not** a hole, and no fixture is owed for it.

### F3 — `includeIf` conditions
Supported keywords (web § *Conditional includes*, opening at 1076; installed 1077ff):
`gitdir`, `gitdir/i`, `worktree`, `onbranch`, `hasconfig:remote.*.url`.
- `gitdir`: the `.git` location is matched as a glob; `**/` and `/**` are extra wildcards;
  `~/` → `$HOME` (web 1098); `./` → “the directory containing the current config file”
  (web 1101); a pattern not starting `~/`, `./`, `/` gets `**/` prepended; a trailing `/`
  gets `**` appended.
- `gitdir/i`: same, case-insensitive.
- `worktree`: same glob syntax against the worktree location (`git rev-parse --show-toplevel`);
  never matches in a bare repository; contrasted with `extensions.worktreeConfig` at web
  1148–1150.
- `onbranch`: glob against the checked-out branch name (web 1271–1272).
- `hasconfig:remote.*.url`: pattern matched against remote URLs; “Files included by this
  option (directly or indirectly) are not allowed to contain remote URLs.” (web § *Conditional
  includes* › `hasconfig:remote.*.url`; installed 1263–1276).
- Matching notes: symlinks in `$GIT_DIR` are not resolved before matching; outside `$GIT_DIR`
  both symlink and realpath forms are matched; `../` is not special (web § *Conditional
  includes*, the paragraph beginning “A few more notes on matching”; installed 1277ff).

**Doc/code divergences worth carrying (calibration, not r16 safety):**
- For `gitdir`/`worktree` patterns the implementation uses `interpolate_path(pat->buf, 1)` —
  `real_home = 1`, i.e. `strbuf_realpath($HOME)` (`config.c:207`; `path.c:718-720`), while the
  doc says “substituted with the content of the environment variable HOME”. A guard that later
  evaluates conditions must resolve `~` in patterns, not copy `$HOME` verbatim.
- `./` patterns splice in `strbuf_realpath(kvi->filename, 1)` (`config.c:223-231`), i.e. the
  realpath’d config directory, not the lexical one.

**Consequence for r16:** the guard does not evaluate any condition; it guards **every**
`includeIf.*.path` target regardless of condition (`tools/souji-census.sh:605-617`, header
lines 87–89). That is the fail-closed choice: condition semantics cannot cause an unguarded
open. The divergences above therefore do not weaken C1 today; they matter only if a later
round starts evaluating conditions to reduce false refusals.

### F4 — `core.alternateRefsCommand` consumer text
Web § *core.alternateRefsCommand*, heading at 2807; installed roff 3717–3720 (the paragraph
continues to the output-format sentence):
> “When advertising tips of available history from an alternate, use the shell to execute the
> specified command instead of git-for-each-ref(1). The first argument is the absolute path of
> the alternate. Output must contain one hex object id per line (i.e., the same as produced by
> `git for-each-ref --format='%(objectname)')`.”

Also: setting `core.alternateRefsPrefixes` “has no effect” when `core.alternateRefsCommand` is
set (web 2821–2822). Setting the value executes a shell command, but only on the
alternate-advertisement path.

**Consequence for r16:** the guard's inertness claim (`tools/souji-census.sh:640-643`) names
exactly that consumer: no census command advertises alternate refs (`status`, `ls-files`,
`check-attr`, `config`, `rev-parse`), so no shell is spawned for this key. **Observed: the
doc supports the named consumer and nothing broader.** The key is *not* inert in general —
only for the enumerated census commands. The claim should keep that scope.

### F5 — `--null` / `-z` list format, and `--includes` default
- `-z`, `--null`: “For all options that output values and/or keys, always end values with the
  null character (instead of a newline). Use newline instead as a delimiter between key and
  value. This allows for secure parsing of the output without getting confused e.g. by values
  that contain line breaks.” (web 586–590; installed roff 487)
- `--includes` / `--no-includes`: “Defaults to `off` when a specific file is given (e.g., using
  `--file`, `--global`, etc) and `on` when searching all config files.” (web 632–635)

**Consequence for r16:** `tools/souji-census.sh:589` and `:592` run
`git config --file "$cfg" --no-includes --list -z`. The explicit `--no-includes` restates the
default for `--file` and, more importantly, stops git from following includes so the guard can
guard each target itself. The parser (`:595-603`) splits each NUL record at the **first**
newline, which is the documented key/value delimiter; keys cannot contain a newline, so the
split is unambiguous. **Observed: matches.**

### F6 — neutralisation precedent and one version bound
- `core.hooksPath`: `/dev/null` “disable[s] all hooks entirely”, “usually only advisable for
  expert users and on a per-command basis using configuration parameters of the form
  `git -c core.hooksPath=/dev/null` …” (web 3026, 3041–3042).
- `core.fsmonitor`: `true` enables the built-in daemon; the definition “was extended to allow
  boolean values in addition to hook pathnames. Git versions 2.35.1 and prior will not
  understand the boolean values and will consider the ‘true’ or ‘false’ values as hook
  pathnames” (web 2576–2603).

**Consequence for r16:** `-c core.hooksPath=/dev/null -c core.fsmonitor=false` on every status
(`tools/souji-census.sh:947-949`) follows the documented per-command form. The `false`
neutralisation is version-bounded: it is a boolean only on git newer than 2.35.1. The r16
claim should carry that bound (host doc set 2.56.0), not state it as unconditional.

### F7 — include depth (found while checking the guard, worth carrying)
Tagged `config.c:135` `#define MAX_INCLUDE_DEPTH 10`; `config.c:177-179` dies when
`++inc->depth > MAX_INCLUDE_DEPTH` (10 nested includes allowed, 11th refused).
`tools/souji-census.sh:582` uses `depth > 10`, with top-level scans at depth 0 (`:663`, `:678`)
and includes at `depth + 1` (`:617`), and only after the target is known to exist (`:615`).
**Observed: exact parity** — both allow 10 nested includes and refuse the 11th.

---

## 3. Consumption map (fact → r16 guard line)

| r16 claim/use | doc/source anchor | guard line | verdict |
|---|---|---|---|
| include base = including file | F1 (web 1068; `config.c:158-162`) | `:611` `${cfg%/*}` | matches |
| `~/` via `$HOME`; other forms refused | F2 (`path.c:713-728`; `config.c:153`) | `:543` `\~/*`; `:545` `\~*|%\(*` → `cfg_soft` | matches (refusal is documented-form, degrades) |
| `:(optional)` not applied to includes | F2 (`config.c:153` vs `:1327`) | literal relative branch `:547` | matches; not a hole |
| every includeIf target guarded | F3 (web § *Conditional includes*, 1076ff) | `:605-617`, header 87–89 | fail-closed |
| depth limit | F7 (`config.c:135`, `:177-179`) | `:582` | exact parity (10/11) |
| `-z` list parsing, single-file read | F5 (web 586–590, 632–635) | `:589`, `:592`, parser `:595-603` | matches |
| `alternateRefsCommand` inert | F4 (web 2807ff) | `:640-643` | matches for the named consumer only |
| hooksPath/fsmonitor neutralised | F6 (web 3026, 3041–3042, 2576–2603) | `:947-949` | matches; fsmonitor bound > 2.35.1 |
| promisor / partialClone inert | **not grounded by git-config(1)** — `GIT_NO_LAZY_FETCH` is a `git(1)` environment variable | `:145-147`, `:640-644` | out of this source's scope; do not cite S042 for it |

**Secondary calibration finding (C-B), guard claim wording.** C1 says “Only a
protected-namespace reach keeps whole-run exit 2”. Observed code paths that also end the whole
run with exit 2:
- `usage_err` → `usage 2` → `exit "${1:-0}"` (`tools/souji-census.sh:166-171`) — every usage error.
- `protected_fail` classes that are not namespace reach: `ambiguous-path` (`:372-373` for a
  `..` component; control characters in the same function), `unresolved-path` (`:414-416`),
  `symlink-loop` (`:425-426`), `git-metadata-symlink`
  (`:496`), `special-path` (`:1255-1256`), `hardlinked-compare` (`:1264-1267`).
- Defensive unsupported-config path: `status_info_file` calls
  `protected_fail "git-config-unsupported"` (`:879`) if a `core.excludesFile`/`attributesFile`
  value cannot be expanded. In the normal flow the earlier config scan soft-fails the same key
  (`:619-624`), so reachability is **not established** here; it is a fail-closed corner.
- `load_census` exits 2 for a malformed/hardlinked baseline (`:1264-1267`) — compare mode.

The reasons are distinguishable in the finding text
(`souji-census: path-protected: <reason> (<label>: <path>)`, `:184-192`), but the *sentence*
“only a protected-namespace reach keeps whole-run exit 2” overstates. Recommend L1 narrow it to
“config evaluation failures that reach no protected path degrade to one error row; whole-run
exit 2 remains the boundary/usage refusal class.” No runtime test was run for this finding.

---

## 4. Proposed S042 cell updates (recheck/used-by only)

S042 was read verbatim from `corpus/SOURCES.md:54`; its immutable cells are not proposed for
rewrite here.

| cell | current | proposed | rationale |
|---|---|---|---|
| `recheck` | `on-release` | **`on-release` (unchanged)** | the web manual tracks Git releases; 2.56.0 is current as served on 2026-10-20, and the installed page set is also 2.56.0. The re-read event belongs in the round lesson/search log, not in this cell. |
| `used-by` | `corpus/lessons/round-15.md` | **`corpus/lessons/round-15.md, corpus/lessons/round-16.md`** | r16 uses S042 for the guard model. Comma is the validator's list separator and each element is trimmed (`scripts/sources-census.sh` `usedby_findings`, `trim_cell` at ~:566), so the space after the comma is safe. **Order matters:** `corpus/lessons/round-16.md` must exist before integration, or E11 fires on a dangling used-by. |

Notes for L1 (not proposed edits):
- **Anchor staleness (C-A).** `installed 2.55.0` is wrong for the host today; the installed
  man pages declare 2.56.0. Options: (a) correct the anchor cell at integration; (b) if
  immutable cells must not be rewritten, admit a one-line correction row naming S042 (drafted
  conditionally as S044 below) and leave S042 untouched.
- **Scope/teaches widening is optional.** S042's scope (“documented config value effects,
  relative includes, booleans and command-local hooks neutralization”) already covers
  `alternateRefsCommand` value effects, and the r15 convention recorded in `SOURCES.md`
  (“Several anchors within git-config share one row rather than counting every subsection as
  growth”) argues against a second docs row for the same manual. If L1 wants the new
  subsections visible in the row, widen `scope`/`teaches` on a new revision; do **not** add a
  duplicate docs row (E04 would need a `supersedes`, and it would double-count).

---

## 5. Proposed new row — implementation source (S043)

This is a **distinct source** (tagged code, not the manual) and the only new row I recommend.
It resolves the one place where the manual's § *Values › pathname* list is broader than what
`include.path` does. Proposed id **S043** — stated for coordination; **L1 renumbers**, and
`SoujiR16.SrcGitStatusRejected` may claim S043 for the R7 git-status row.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S043 | git/git tag v2.56.0 — config.c and path.c — https://github.com/git/git/blob/v2.56.0/config.c | code | A | what `include.path` actually expands and where the `:(optional)` pathname prefix applies on Git 2.56.0; source inspection, not runtime proof | tag v2.56.0: config.c:135 `MAX_INCLUDE_DEPTH 10`, :142-145 `handle_path_include`, :153 `interpolate_path(path, 0)`, :158-162 relative to including file, :177-179 depth die, :207 pattern `interpolate_path(…, 1)`, :1319-1328 `git_config_pathname` strips `:(optional)`; path.c:698-746 `interpolate_path` | `include.path` expands `~/`, `~user/` and `%(prefix)/`, strips no `:(optional)` prefix, resolves relative paths against the including file, and dies past 10 nested includes; `:(optional)` is honored only by callers reading a pathname, not by `include.path` | mined | 2026-10-20 | on-release | corpus/lessons/round-16.md |

Validator notes (checked against `scripts/sources-census.sh`): kind `code` and tier `A` are in
the enums (E05/E06); 11 columns (NF=13); URL is unique in the registry (E04/W04 clean);
`mined` requires a non-`—` used-by (W03) and E11 requires the lesson path to exist at
integration. If the round-16 lesson does not end up citing S043, admit it as `queued` with
used-by `—` instead (also validator-clean, no warning).

### Conditional row (only if L1 wants an immutable correction row instead of editing S042's anchor)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S044 | installed git-config(1) man page set, git 2.56.0 — /usr/share/man/man1/git-config.1.gz | docs | A | version metadata of the installed vendor documentation only, not the installed binary | roff header line 7 `Source: Git 2.56.0` and line 10 `TH … "2026-09-27" "Git 2.56.0"`; the same header in git-maintenance.1.gz and git-status.1.gz, read 2026-10-20 | the installed man pages on this host declare Git 2.56.0, so an anchor that calls them 2.55.0 is stale; man-page metadata is not proof of the git binary version | queued | 2026-10-20 | on-release | — |

I do **not** recommend S044 if L1 can correct S042's anchor cell directly; two rows for one
document re-read would inflate the source count.

---

## 6. Proposed search-log prose (for L1 to place; `SOURCES.md` untouched)

> **Round-16 git-config re-check for the census config guard (2026-10-20).** Question: does
> git-config(1) still support the r16 guard's value/effect model, and what exactly do includes,
> includeIf conditions, `alternateRefsCommand` and `-z` say? L1 re-opened the official web
> manual (served “last updated in 2.56.0”, 2.56.0 dated 2026-09-28) and the installed man page
> set, which now declares “Source: Git 2.56.0” (TH 2026-09-27) rather than 2.55.0. Tagged
> v2.56.0 `config.c`/`path.c` were opened to separate documented pathname forms from what
> `include.path` actually expands. Identified 3 documents (web manual, installed man page,
> tagged source pair), screened 3; included 1 amended row S042 (recheck/used-by only) and 1 new
> A code row S043; excluded a second docs row for the same manual. Stop: the five r16 use sites
> and the one doc/source divergence are located; no runtime guard behaviour was exercised.

---

## 7. Observed / inference / unresolved

**Observed (document or tagged source):** every quote and line anchor above; the installed
man-page version headers; `tools/souji-census.sh` equals `cbf688ab`; the guard's code paths and
its instrumented `-c` flags; the exit-2 classes listed in C-B.

**Inference (not run):** that the guard's model of `include.path` accepts exactly the forms git
2.56.0 accepts — read from both sides of the comparison, but not exercised. That the
`status_info_file` → `protected_fail` path is unreachable in normal flow — read from call
ordering, not tested.

**Unresolved / out of scope:**
- Installed `git` **binary** version was not measured (probe rule excludes `git --version`);
  only the man-page metadata is recorded.
- `remote.*.promisor` and `extensions.partialClone` inertness is a `git(1)` `GIT_NO_LAZY_FETCH`
  claim, not a git-config(1) claim — S042 must not be cited for it.
- No census, fixture, or runtime probe was executed, so no behavioural pass is claimed.

---

STATUS: source re-check complete and S042 still supports its mined claim; no probe was run by this seat. Two claim-level discrepancies recorded for L1: (1) S042's anchor says installed 2.55.0 but the installed man pages declare Git 2.56.0 (TH 2026-09-27); (2) C1's "only a protected-namespace reach keeps whole-run exit 2" is contradicted by `usage_err` and by non-namespace `protected_fail` classes (`ambiguous-path`, `unresolved-path`, `symlink-loop`, `git-metadata-symlink`, `special-path`, `hardlinked-compare`, `load_census` bad baseline).

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
awk -F'|' '/^\| S043 /{print "S043 fields:", NF-2} /^\| S044 /{print "S044 fields:", NF-2}' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md; wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat -- corpus/SOURCES.md; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/SrcGitConfigIncludesRecheck.md
```

The second command's `wc -l` was a pre-edit count. The third command printed nothing for
`diff --stat` (SOURCES.md unmodified); the digest it printed was of the report **before** the
final citation edits, so it is deliberately not restated here — no self-referential pin.

Non-shell reads (exact files/URLs only): `read` on https://git-scm.com/docs/git-config with
selectors `:301-760`, `:1064-1125`, `:1180-1240`, `:1348-1378`, `:2806-2822`; `grep` on the
same URL for `includeIf|alternateRefsCommand|include\.path`, `%\(prefix\)|prefix.*expanded|relative to the directory`,
`prefix|tilde|HOME`, `core\.fsmonitor|core\.hooksPath`, `specific file is given|null character`;
`read`/`grep` on `/usr/share/man/man1/git-config.1.gz`, `git-maintenance.1.gz`, `git-status.1.gz`
(archive member `:<name>`); `grep` on https://raw.githubusercontent.com/git/git/v2.56.0/config.c
and `…/path.c`; `read` on `…/config.c:130-165`, `:190-215`, `:215-250`, `…/path.c:685-770`;
`read`/`grep` on `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`,
`corpus/QUALITY.md`, `corpus/lessons/round-15.md`, `census/round-15/sources-draft.md`,
`.ufo/waves/round-16/w1/DraftReportSkeleton.md`, `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`,
and `tools/souji-census.sh` (line ranges `:60-112`, `:184-196`, `:330-430`, `:536-650`,
`:860-885`, `:1255-1270`). No installs.
