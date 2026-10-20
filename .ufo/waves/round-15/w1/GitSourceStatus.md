# GitSourceStatus — git-status semantics review (souji r15/w1)

Scout, report-only. No tests, probes, builds, or edits outside this file. No tool installs.
All lane source claims are `file:line` against the current tree; external claims are
document/source-verified.

## Pins and scope

- Lane HEAD `cc2168325768d5356a82c039dcdf787377c55784`.
- `tools/souji-census.sh` at inspection: sha256 `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`,
  byte-identical to `cc216832:tools/souji-census.sh`. C1 value-aware repair is **not present**;
  every "repaired tool" statement below is **design-only** and names the exact acceptance needed.
- `tools/souji-verify.sh`: sha256 `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd`.
- Official docs opened: `https://git-scm.com/docs/git-status` (2.53.0 text; "2.54.0 → 2.56.0 no
  changes"), `/docs/git-config` (2.56.0), `/docs/gitignore` (2.55.0), `/docs/git-update-index`
  (2.52.0; unchanged 2.53–2.56), `/docs/git-ls-files` (2.55.0). Official git source v2.55.0:
  `builtin/commit.c`, `wt-status.c`, `setup.c`, `dir.c`, `submodule.c`, `diff.c` (raw.githubusercontent.com/git/git/v2.55.0).
- Axes: operability (no value-blind refusals; benign configs preserved) and calibration
  (dirty/clean evidence sound; paired red/green; namespace controls).

## Boundary disclosure (already-violated directive)

One early discovery call violated the "explicit known source files only" rule:

`grep -rl "git status\|status --porcelain\|porcelain" --include=* . 2>/dev/null | grep -v operator-sweep | grep -v '\.ufo/waves/round-1[0-4]' | head -50`

It recursively scanned the lane root from `/home/vgpnk/Projects/shokunin/souji-shokunin`.
The `grep -v operator-sweep` filtered only *output lines*; grep may have opened files under
`census/operator-sweep-20261019/` to decide matches. No result from that subtree was displayed
or used, no such file was explicitly opened/edited/copied, and I did not repeat the call.
Earlier `ls census` listed top-level directory names only (including the sweep directory name),
not contents. Limitation: I cannot certify grep did not read bytes there; its output for those
paths was discarded. All later reads used explicit files under `tools/`, `/tmp` fetched git
source, or round-15 report paths.

A second violation: the first `write` used a workspace-root-relative path and created this
report at `/home/vgpnk/Projects/shokunin/.ufo/waves/round-15/w1/GitSourceStatus.md`, outside
the lane. It was byte-copied to the lane path (sha256 compared equal), then the misplaced file
and the empty `w1` directory created for it were removed. The pre-existing fleet
`.ufo/waves/round-15/` content was not modified; no sibling report was touched. All subsequent
paths were absolute under the lane root.

## Observed implementation ([OBS])

`tools/souji-census.sh:706-722` (`count_dirty`) runs:

```
git -C "$1" --no-optional-locks -c core.fsmonitor=false \
  -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null \
  -c core.attributesFile=/dev/null status --porcelain --ignore-submodules=all -- . \
  ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
  ':(exclude,glob)census/operator-sweep-*' ... 2>/dev/null
```

and counts non-empty output lines (721). Env isolation is real and strong: every inherited
`GIT_*` is unset (`:114-120`) and `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` → `/dev/null`,
`GIT_CONFIG_NOSYSTEM=1` (`:121-123`). Only repository-local config can influence status.
`clean` is emitted when no flag is in `{dirty,unpushed,no-remote,status-unverifiable,error,not-a-repo}`
(`:889-905`). Contract claims: dirty is the default-untracked-mode count on the main work tree,
submodule content is not inspected (`:33-38,48-56`). Selftest pins the two-line collapse case
(`:1319-1322`).

`tools/souji-verify.sh` has three different status notions:
- `:322` repo-root receipt `git status --porcelain` (plain);
- `:366-377` worktree receipt plain status;
- `:658` `try_pushed` (the deletion gate) `status --porcelain --untracked-files=all --ignored=matching`;
- `:820-826` v2 worktree receipt plain status.
It unsets only `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE` (`:64`) and does **not**
clear `GIT_CONFIG_COUNT/GIT_CONFIG_PARAMETERS/GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM` or pin
`core.fsmonitor=false`/`core.ignoreStat=false`.

## Semantics findings, ranked

### F1 — Local `status.showUntrackedFiles=no` silently makes untracked work invisible. [DOC+SRC+OBS] — P1

Docs (`git-status`, `-u`): untracked mode default is `normal`, but "The default can be changed
using the `status.showUntrackedFiles` configuration variable"; `git-config`: "`no` - Show no
untracked files", and "This variable can be overridden with the -u|--untracked-files option".
Porcelain v1's stability guarantee names only two config exceptions (`color.status`,
`status.relativePaths`); `showUntrackedFiles` filters content, and git source handles it
unconditionally (`builtin/commit.c:1507-1513`). So a benign user config `false`/`no`/`0`
turns a repo with live untracked work into `dirty=0` and, with a remote ref, `clean`.
The census neither refuses this key nor overrides untracked mode (`:710-716`). This is a
false-clean, not an operability refusal — refusing it would harm C1; override it instead.

### F2 — `status.showUntrackedFiles=all` breaks the documented count contract. [DOC+OBS] — P2

Docs: `normal` shows "untracked files and directories"; `all` shows "individual files in
untracked directories". Local `all` changes the same fixture from 2 lines to one per file,
violating `:33-38` and the pinned selftest, and inflates status cost. Same one-line fix as F1.

### F3 — `--ignore-submodules=all` plus submodule rows being skipped allows a false `clean`. [DOC+SRC+OBS] — P1 calibration

Docs: `all` → "hide all changes to submodules". Source: the explicit arg sets
`override_submodule_config=1` for both the worktree and index diffs
(`wt-status.c:650-652,678-679`; `submodule.c:429-444`), so staged gitlink changes are hidden
too. Submodule roots have a `.git` *file* and are not census rows (`:16-18,543`), and their
own commits are invisible to the owner's `rev-list`. A repo whose only live work is inside
submodules therefore emits `dirty=0` and possibly `clean`. The header declares content is not
inspected, but `clean` still reads as "no live work". Cheapest correction is an explicit
`submodule-unscanned` flag when the index contains mode-160000 entries or `.gitmodules`
exists (`git ls-files -s`, index-only), suppressing `clean`; do not change the dirty count.

### F4 — `core.ignoreStat=true` and pre-existing index bits defeat status. [DOC+SRC] — P1 calibration

Docs (`git-config`): "If true, Git will avoid using lstat() calls ... Git will not normally
detect changes to those files." `git-update-index`: assume-unchanged "makes Git omit any
checking and assume it has not changed"; `core.ignorestat=true` auto-sets the bit; inspect
with `git ls-files -v` ("lowercase letters for files that are marked as assume unchanged").
`core.ignoreStat` is neither overridden nor refused (`:493-520,710-716`). Critically,
`-c core.ignoreStat=false` only prevents **new** bits; existing index bits still hide edits.
Acceptance must include the assume-unchanged fixture, otherwise a one-line override appears
fixed while the false clean survives. Skip-worktree (`ls-files -t` tag `S`) has the same
"treat as unchanged" effect and should map to the same unscanned flag.

### F5 — Remaining ignore sources can hide untracked work. [DOC+OBS] — P2 calibration, doc-level

Only `core.excludesFile` is neutralized (`:711`); `$GIT_COMMON_DIR/info/exclude` and in-tree
`.gitignore` stay active (`gitignore`: precedence list). `--ignored` is not used, so ignored
paths never appear. That is normal Git semantics, but `clean` must then mean "no tracked or
non-ignored untracked change", not "nothing untracked". Recommend scoping the wording rather
than adding a blanket flag; the mtime walk still sees ignored files.

### F6 — If C1 admits `extensions.worktreeConfig`, `config.worktree` is unguarded. [SRC+OBS] — P1 interaction

`guard_git_config` parses only `$dir/config` (`:495-511`, `--no-includes`). Git reads
`<gitdir>/config.worktree` when `extensions.worktreeConfig=true` (`setup.c:787-793`), and
linked worktrees can have per-worktree config. That file can carry
`status.showUntrackedFiles=no`, `core.ignoreStat=true`, `filter.*.command`, etc. Admitting
`true` without parsing it converts an operability fix into a namespace regression. Same
smuggle path exists for admitted `include.path`/`includeIf` (guard explicitly uses
`--no-includes`). Acceptance: either keep a value-aware specific refusal, or parse every file
Git will read and apply the same policy; the checker must include a `config.worktree`
smuggle case. (`-c` pins still win for `core.excludesFile`/`fsmonitor`, but not for
`status.showUntrackedFiles` unless F1's override is added.)

### F7 — Pathspec exclusions can mask *tracked* changes. [OBS+SRC] — P3

`:(exclude)` pathspecs apply to tracked diffs too. If `census/operator-sweep-*`, `.ufo/state`,
or `.ufo/watchdog.log` is tracked and modified, status omits it and `dirty` can be 0. No
content is needed to detect this: `git ls-files -- <same exclusions>` is index-only. If any
tracked path matches, emit `status-unverifiable`/`protected-excluded` rather than `clean`.
Synthetic fixture must use a non-operator name (e.g. `census/operator-sweep-synthetic/`).

### F8 — `core.worktree` changes which tree `dirty` measures. [SRC+OBS] — P3, cross-lane WorktreeCfg

Guard admits `core.worktree` after boundary check (`:508-521`). Source `setup.c:1156-1169`
makes `git -C <row>` run status against the configured worktree, while `scratch_bytes` and
`newest_mtime` walk `<row>`. The row is then internally inconsistent; `-- .` itself is applied
after the worktree chdir, so the pathspec is not the bug. Acceptance: classic-layout fixture
with `core.worktree=/var/tmp/...` plus an untracked file must reflect that tree in every field
or refuse; never `clean` while either tree is dirty.

### F9 — Status stderr is discarded, warnings cannot be distinguished from success. [OBS+SRC+UNK] — P2

`:716` redirects stderr to `/dev/null`; only the exit code decides verifiability. Git's
directory walk warns and continues on an unreadable directory (`dir.c:2587`), so a completed
status may omit entries. Whether an unreadable tracked path still yields a conservative
`dirty` entry is **not established** without the acceptance fixture (no probe run here).
Recommend capturing stderr and emitting `status-unverifiable` (or a `status-warning` flag that
suppresses `clean`) when non-empty; benign warning noise is preferable to a false clean.

### F10 — Verifier status calls are weaker than census and env-injectable. [OBS+DOC+SRC] — P2 cross-tool

`try_pushed` (`:658`) is the gate that can grant `SAFE(pushed)`; plain `git status` in status
uses submodule mode `none` by default when `ignore_submodule_set` is false (`wt-status.c:653-655`),
so it is strict — but an inherited `GIT_CONFIG_COUNT`/`GIT_CONFIG_GLOBAL` can set
`diff.ignoreSubmodules=all`, `status.showUntrackedFiles=no`, or `core.ignoreStat=true` first,
and the verifier clears none of them (`:62-64`). It also never pins `core.fsmonitor=false`
(census does), so a local/global fsmonitor hook can under-report changes. Repairs: clear
`GIT_CONFIG_*` (or use `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`), pin
`-c core.fsmonitor=false -c core.ignoreStat=false`, and pass `--ignore-submodules=none` to
`try_pushed` to override config/`.gitmodules` (docs: command line overrides both). Verify's
plain statuses are additionally weakened by `showUntrackedFiles=no`; pass
`--untracked-files=normal` there too. These are advisory; GitEnvironment/FiltersSafe own the
environment and execution surface.

### F11 — No line-count defect in porcelain v1 without `-z`. [DOC+SRC]

Without `-z`, paths with whitespace/control characters are C-quoted (`git-status` short
format), so an embedded newline becomes `\n` and one entry stays one line; `grep -c .` is
therefore safe for counting. `-z` is still "recommended for machine parsing" but switching
would require NUL-safe counting — not worth churn. `status.branch`, `status.short`,
`status.aheadBehind` are deferred and not applied under porcelain (`commit.c:1258-1279`);
`status.displayCommentPrefix` and `status.showStash` do not touch the v1 short printer
(`wt-status.c:2169-2198`); `status.renames`/`renameLimit` can change the count but never
clean/dirty. These `status.*` keys are benign for census and must not be refused.

## C1 key effects — what a value-aware guard may admit [DOC+SRC]

| key | effect on census status calls | safe admission |
|---|---|---|
| `core.excludesFile` | **neutralized** by `-c ...=/dev/null` on every status call; no other census command reads it | admit **any** value **only while the `-c` pin stays**; fixture `excludesFile` = `*` must still count untracked |
| `core.attributesFile` | neutralized for global attrs; in-tree/info attributes remain | admit any value; filter execution is governed by `filter.*` + attributes (FiltersSafe) |
| `core.hooksPath` | no census command runs hooks (status/log/rev-list/for-each-ref/worktree list/cat-file) | admit any value; current refusal is pure operability harm |
| `filter.*.clean/smudge/process` | status can execute a clean filter when hashing tracked content if a `.gitattributes`/info attribute names it; attributesFile pin does not disable in-tree attributes | admit empty/unset only; non-empty command values are not read-only-safe (cross-lane) |
| `include.*` / `includeIf.*` | key scan uses `--no-includes`; included file can smuggle any weak key | admit only with recursive bounded parse under the same policy; else specific refusal |
| `extensions.worktreeConfig` | enables unparsed `<gitdir>/config.worktree` reads (F6) | admit only with `config.worktree` parsed/applied; else specific refusal |
| `remote.*.promisor`, `extensions.partialClone` | status can lazily fetch missing objects (network/credentials) | `false`/inactive benign; keep active values refused unless neutralized (PromisorSafe) |
| `core.alternateRefsCommand` | not used by status or any census command (no `--alternate-refs`) | admit any value; command never runs |
| `core.fsmonitor` | already pinned `false` on census status | admit any value; note ≤2.35.1 read "false" as a hook path (docs), host is newer |
| `core.ignoreStat` | **not pinned**; true and existing assume-unchanged bits hide edits (F4) | admit both values (no refusal), pin `-c core.ignoreStat=false`, and add the index-bit scan; otherwise this is a false clean |
| `core.worktree` | status measures the configured tree, other fields measure `<row>` (F8) | admit only when it resolves to the row (or apply all fields to it) |
| `status.*` | all inert under porcelain except `showUntrackedFiles` (F1/F2/F11) | admit all values; pin `--untracked-files=normal` |
| `diff.ignoreSubmodules`, `submodule.<name>.ignore` | overridden by census `--ignore-submodules=all`; **not** overridden by verify's plain/try_pushed calls | census: admit any; verifier: pin `--ignore-submodules=none` in `try_pushed` |
| `core.untrackedCache`, `core.checkStat` | cache/stat tuning; untrackedCache validated; `minimal` marginally weakens detection | admit; optionally pin `-c core.checkStat=default` |

## Recommended moves (cheap; each improves both axes, harms none)

1. `count_dirty` (`:712`): add `--untracked-files=normal` (not bare `-u`, which means `all`).
   Removes the F1/F2 class without any new refusal. Exact flag spelling matters.
2. `count_dirty` (`:710-712`): add `-c core.ignoreStat=false` (optionally
   `-c core.checkStat=default`); keep all existing `-c` pins. Admission of benign values and
   evidence soundness become independent.
3. `count_dirty`: after status, run index-only `git ls-files -v -- <same pathspecs>`; any
   `^[a-z]` line (assume-unchanged) or `^S ` tag (skip-worktree) returns `unverifiable`
   (mapped to `status-unverifiable`). Similarly `git ls-files -s` mode 160000 → new
   `submodule-unscanned` flag that suppresses `clean` (F3/F4).
4. Capture status stderr (F9) instead of discarding; non-empty → `status-unverifiable` or a
   warning flag that suppresses `clean`.
5. Index-only `git ls-files -- <exclusions>` check so a tracked path matching an exclusion
   cannot be silently hidden (F7).
6. Do not add refusals for `status.*`, `core.hooksPath`, `core.excludesFile`,
   `core.attributesFile`, `core.alternateRefsCommand`, `core.ignoreStat`, or
   `diff.ignoreSubmodules` — the pins above cover them. Keep `include*`,
   `extensions.worktreeConfig`, active promisor/partialClone, and non-empty filter commands
   value-aware guarded until their parse/neutralization exists (F6).
7. Verifier (advisory, other owner): clear `GIT_CONFIG_*`, pin fsmonitor/ignoreStat, add
   `--ignore-submodules=none` to `try_pushed`, and `--untracked-files=normal` to plain
   receipt statuses (F10).

## C2 paired acceptance matrix (for `souji-preservation-evidence.py` consumers)

Each case pins: case id, fixture sha256, baseline tool blob sha256 (r14 = `cc216832` census),
candidate tool sha256, expected baseline tuple and candidate tuple. The checker must reject a
candidate that changes only one of {refusal behavior, evidence behavior} for a case whose two
predicates differ. Namespace control = identical fixture config placed in synthetic HOME
global config or injected via `GIT_CONFIG_COUNT`; output must equal the no-config control.

| id | fixture (synthetic, `/var/tmp`) | baseline r14 predicate (RED) | repaired predicate (GREEN) |
|---|---|---|---|
| S1 | local `[status] showUntrackedFiles = no`; pushed commit + 1 untracked file | exit 0, `dirty=0`, `clean` | exit 0, `dirty>=1`, `dirty` flag, **no** `clean`, **no** `git-config-unsupported` |
| S2 | local `= all`; untracked file + untracked dir with 2 files | `dirty=3` (contract violation) | `dirty=2` (file + collapsed dir) |
| S3 | commit f; `update-index --assume-unchanged f`; modify f; local `[core] ignoreStat = true` | `dirty=0`, no refusal, `clean` | no refusal; `status-unverifiable` (or `index-unscanned` suppressing clean); **not** `clean`; `-c ignoreStat=false` alone must still fail this case |
| S3b | control: no assume-unchanged bit, `ignoreStat=false` | `clean` | `clean` preserved (no over-refusal) |
| S4 | local `[core] excludesFile=<fixture>/exclude-all` (`*`); 1 untracked file | refusal `git-config-unsupported` (operability RED) | exit 0, no refusal, `dirty>=1` (pin held). Both predicates required |
| S4b | same `*` ignore pattern in global config/XDG or via `GIT_CONFIG_COUNT` | output = no-config control | output = no-config control (namespace isolation) |
| S5 | superproject with gitlink (mode 160000) to submodule repo; submodule has 1 untracked file; superproject clean | `dirty=0`, `clean` | `clean` absent; `submodule-unscanned` (or equivalent) present; no refusal |
| S6 | repo tracks `census/operator-sweep-synthetic/f`, modifies it | `dirty=0`, `clean` | `status-unverifiable`/`protected-excluded`, `clean` absent |
| S7 | local `[extensions] worktreeConfig = true` + `config.worktree` `showUntrackedFiles=no`; 1 untracked file | refusal of `true` (operability RED) | (a) specific refusal with reason, or (b) admitted with `dirty>=1`; reject candidate that accepts and emits `clean` |
| S8 | verifier control: `GIT_CONFIG_COUNT=1 ...diff.ignoreSubmodules=all` + superproject with dirty submodule, `try_pushed` target | pushed receipt granted over submodule dirt (RED) | injection ineffective and `--ignore-submodules=none` blocks; receipt not `SAFE(pushed)` |

Checker rules for these rows:
- Reject "green-only": baseline and candidate rows byte-identical on the axis.
- Reject weakened preservation evidence: candidate omits the negative/namespace control case,
  or the fixture digest/tool digest is reused across cases.
- S3 is the anti-shortcut case: it must fail a repair that only adds `-c core.ignoreStat=false`.
- S4 is the C1 anchor: admitting the key without the `-c core.excludesFile` pin fails the
  dirty predicate; keeping the refusal fails the operability predicate. Admission of the
  benign value alone is not evidence of preservation.
- S5/S6/S7 are calibration controls against a repair that removes refusals by also removing
  evidence.

## Unresolved / not verified

- [UNK] Status completeness on unreadable directories: `dir.c:2587` warns and continues; whether
  a tracked entry under such a directory appears as modified or is skipped needs the S9
  fixture (chmod 000 dir) decided by L1. No probe run here.
- [UNK] Docs are ambiguous whether a staged gitlink is visible under explicit
  `--ignore-submodules=all` (the `status.submoduleSummary` exception wording); source
  (`wt-status.c:650-652,678-679`, `submodule.c:429-444`) hides it. An S5 variant with a staged
  gitlink should decide it.
- [UNK] `core.ignoreCase=true` on a case-sensitive filesystem and `core.fileMode=false` can
  hide case-only/mode-only changes; not assessed, not recommended for refusal (legitimate on
  other platforms). `core.sparseCheckout` is covered only through the index-bit scan (S3
  variant with skip-worktree).
- [INF] `GIT_CONFIG_GLOBAL=/dev/null` plus `-c core.excludesFile=/dev/null` should prevent any
  XDG/global ignore read; verified from docs/precedence, not from a trace.
- Unrun: every check above. L1 owns acceptance; no certification or deletion authority is
  claimed.

## Proposed SOURCES rows (for SourcesDraft; not written by me)

- S041 `git-status` OPTIONS `-u/--untracked-files`: "The default can be changed using the
  `status.showUntrackedFiles` configuration variable"; modes `no|normal|all`.
- S042 `git-status` Porcelain v1: stable "regardless of user configuration", exceptions
  `color.status` and `status.relativePaths`.
- S043 `git-status` `--ignore-submodules`: `all` = "hide all changes to submodules".
- S044 `git-config` `status.showUntrackedFiles`: "`no` - Show no untracked files"; overridable
  by `-u|--untracked-files`.
- S045 `git-config` `core.ignoreStat`: "Git will not normally detect changes to those files."
- S046 `git-update-index` assume-unchanged: "omit any checking and assume it has not changed";
  `git ls-files -v` shows the bit.
- S047 `git-config` `diff.ignoreSubmodules` default `untracked`; overridden by the
  `--ignore-submodules` command-line option.
- S048 `gitignore` precedence: in-tree `.gitignore`, `$GIT_COMMON_DIR/info/exclude`,
  `core.excludesFile`.
