# Round 15 W1 — GitSourceIncludes

Seat: `SoujiR15.GitSourceIncludes` (scout, leaf member).
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Axes: operability, calibration.
Target: open official git-config includes / conditional-includes documentation; report
relative-path and condition quotes with exact locations for the round-15 C1 repair of
value-blind include refusals.
Acceptance: this report only. No tests, probes, builds, edits, registry rows, or
certification. Source inspection only.

---

## 0. Method, snapshot, and boundary disclosure

Opened sources:

- Installed vendor manual: `/usr/share/man/man1/git-config.1.gz`,
  package `git 2.55.0-1` (`pacman -Q git`, 2026-10-20), footer
  `Git 2.55.0  2026-06-29  GIT-CONFIG(1)`.
  Extraction command (line numbers below are for exactly this command):
  `LC_ALL=C MANWIDTH=100 man -P cat git-config | col -b`
  (6761 lines; the earlier non-`LC_ALL=C` render differs only in quote/bullet
  bytes, line numbers identical).
- Web, pinned to the installed release: `https://git-scm.com/docs/git-config/2.55.0`,
  version selector date 2026-06-29, sections `#_includes` and
  `#_conditional_includes`, accessed 2026-10-20.
- Web, latest for the delta check: `https://git-scm.com/docs/git-config/2.56.0`,
  version selector date 2026-09-28, accessed 2026-10-20. The latest page states
  "git-config last updated in 2.56.0".
- Registry context only: `corpus/SOURCES.md` row S042 already records git-config(1)
  includes/relative-path/boolean value effects and is `mined` at 2026-10-20. This
  report adds exact anchors; it makes **no** registry edit.

Source snapshotted: `tools/souji-census.sh`, SHA-256
`fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`,
mtime `2026-10-20 04:56:30.745043852 -0300`, 55730 bytes. ConfigRepair may edit
this file in this wave; if so, line numbers move but the semantics below stand.
No source change was made by this seat.

Boundary disclosure (authoritative no-query reminder):

- One early discovery call from the lane root used a recursive search:
  `grep -rn "includeIf\|include.path\|includes" --include="*.sh" --include="*.py"
  --include="*.md" -l . 2>/dev/null | grep -v "\.ufo/waves"`.
  This traversed the lane root, including `census/`, so grep may have opened
  matching-named files under `census/operator-sweep-20261019/` while searching.
  No match from that region was printed, used, quoted, or incorporated; this
  report contains no operator-sweep content. All later searches used explicit
  files or explicit tool/test/spec paths. This call is not repeated.
- Top-level `ls -la` of the lane root and `ls` of `.ufo/waves`, `tools`, `tests`,
  `corpus` were metadata listings only; no recursive content query.
- No tests, selftests, builds, linters, formatters, smoke runs, or runtime probes
  were executed. No `~/.omp/agent/agent.db*` or credential file was opened,
  copied, or queried. No pacman transaction, no install, no upgrade.

---

## 1. Findings

Confidence: **H** = directly quoted source/doc text; **M** = follows from quoted
text plus one stated assumption; **L** = design inference, needs a fixture.

| id | finding | confidence |
|---|---|---|
| F1 | A relative `include.path` value is anchored to the **directory of the config file containing the directive**, not to cwd, the worktree, or the repo root. For `$GIT_DIR/config` the base is `$GIT_DIR`; a value `../x` therefore resolves against `$GIT_DIR`'s parent. | H |
| F2 | `include.path` values receive tilde expansion, and the `pathname` value type additionally documents `~/`, `~user/`, and `%(prefix)/` expansion. A resolver that handles only `~/` and absolute/relative forms does not cover the documented surface. | H for `~/`, `~user/`, `%(prefix)`; **M** that the generic `pathname` rules apply to `include.path` (the Includes section itself only promises tilde expansion) |
| F3 | Both `include.path` and `includeIf.<condition>.path` "can be given multiple times." A value-aware guard must inspect **all** values; first-value or one-value sampling is unsound. | H |
| F4 | Host git 2.55.0 recognizes exactly four condition keywords: `gitdir`, `gitdir/i`, `onbranch`, `hasconfig:remote.*.url`. `worktree` and `worktree/i` are documented only from 2.56.0 and are absent from the installed 2.55.0 manual. | H |
| F5 | `gitdir` matches the **`.git` directory location** (final directory for a `.git`-file repo such as a linked worktree), with glob rules: `~/` -> `$HOME`; `./` -> the config file's directory; no leading `~/`, `./`, or `/` -> implicit `**/`; trailing `/` -> implicit `**`; `../` is literal and not path traversal. | H |
| F6 | Outside `$GIT_DIR`, **both** the symlink and realpath spellings are matched; inside `$GIT_DIR` symlinks are not resolved before matching. A single-spelling condition evaluator can falsely decide "condition false" while Git applies the include. | H |
| F7 | `hasconfig:remote.*.url` scans the rest of the config files ahead for remote URLs; files included by that option may not declare remote URLs (Git breaks the cycle). Exact truth requires an ordered cross-file scan, so a purely local test is not equivalent. | H |
| F8 | Included content is inserted immediately at the directive, so an admitted include can inject any key in the current refusal list, including keys whose only effect is on the later `git status`. Presence of a benign `include.path` does not by itself imply benign effective configuration. | H |
| F9 | The census's own key scan is intentionally file-local: `--no-includes` at line 500 matches the documented default for `--file` queries. The include read that matters happens later inside ordinary git commands (`status`, `worktree list`, `for-each-ref`, `rev-list`), not in the guard's key scan. Round-14 `BoundaryAttack.md` lines 41 and 132-133 report that a repo-local include made `git status` open a synthetic store file; that is a prior-seat report, not re-observed here. | H / prior report |
| F10 | The current refusal glob at line 505 over-matches: `*include.*` and `*includeif.*` match any key string containing those substrings, not exactly the documented special variables. The docs name exactly `include.path` and `includeIf.<condition>.path`. | H |

---

## 2. Exact quotes and locations

All quotes are verbatim, at most 25 words. Installed line numbers are for
`LC_ALL=C MANWIDTH=100 man -P cat git-config | col -b` on git 2.55.0-1.
Web anchors are for `https://git-scm.com/docs/git-config/2.55.0`, accessed
2026-10-20; the same sentences appear on the latest 2.56.0 page unless noted.

### Includes

| id | quote (words) | installed location | web location |
|---|---|---|---|
| Q1 | "The include and includeIf sections allow you to include config directives from another source." (16) | lines 580-581 | `#_includes` |
| Q2 | "includeIf sections may be ignored if their condition does not evaluate to true" (13) | lines 581-582 | `#_includes` |
| Q3 | "The variable takes a pathname as its value, and is subject to tilde expansion." (16) | lines 584-586 | `#_includes` |
| Q4 | "These variables can be given multiple times." (7) | line 586 | `#_includes` |
| Q5 | "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." (22) | lines 588-589 | `#_includes` |
| Q6 | "the path is considered to be relative to the configuration file in which the include directive was found" (18) | lines 589-591 | `#_includes` |
| Q7 | "relative paths are always relative to the including file (if the condition is true)" (14) | example comment, lines 717-719 | `#_example` |
| Q8 | "path = foo.inc ; find \"foo.inc\" relative to the current file" (12) | example, line 702 | `#_example` |

### Conditional includes — host 2.55.0 keyword set

| id | quote (words) | installed location | web location |
|---|---|---|---|
| Q9 | "The data that follows the keyword gitdir and a colon is used as a glob pattern." (17) | lines 601-602 | `#_conditional_includes` |
| Q10 | "If the location of the .git directory matches the pattern, the include condition is met." (16) | lines 601-603 | `#_conditional_includes` |
| Q11 | "the .git location would be the final location where the .git directory is, not where the .git file is" (21) | lines 604-607 | `#_conditional_includes` |
| Q12 | "If the pattern starts with ~/, ~ will be substituted with the content of the environment variable HOME." (20) | lines 613-614 | `#_conditional_includes` |
| Q13 | "If the pattern starts with ./, it is replaced with the directory containing the current config file." (18) | lines 616-617 | `#_conditional_includes` |
| Q14 | "If the pattern does not start with either ~/, ./ or /, **/ will be automatically prepended." (18) | lines 619-620 | `#_conditional_includes` |
| Q15 | "If the pattern ends with /, ** will be automatically added." (12) | lines 623-624 | `#_conditional_includes` |
| Q16 | "This is the same as gitdir except that matching is done case-insensitively" (12) | lines 627-629 | `#_conditional_includes` |
| Q17 | "If we are in a worktree where the name of the branch that is currently checked out matches the pattern" (20) | lines 632-635 | `#_conditional_includes` |
| Q18 | "The first time this keyword is seen, the rest of the config files will be scanned for remote URLs (without applying any values)." (23) | lines 642-647 | `#_conditional_includes` |
| Q19 | "Files included by this option (directly or indirectly) are not allowed to contain remote URLs." (16) | lines 649-650 | `#_conditional_includes` |
| Q20 | "Symlinks in $GIT_DIR are not resolved before matching." (9) | line 667 | `#_conditional_includes` |
| Q21 | "Both the symlink & realpath versions of paths will be matched outside of $GIT_DIR." (15) | lines 669-670 | `#_conditional_includes` |
| Q22 | "Note that \"../\" is not special and will match literally" (10) | line 678 | `#_conditional_includes` |
| Q23 | "This was not the case in the initial release of this feature in v2.13.0" (15) | lines 673-674 | `#_conditional_includes` |

### Version delta — 2.56.0 only

Source: `https://git-scm.com/docs/git-config/2.56.0`, version selector date
2026-09-28, section `#_conditional_includes`, keyword `worktree` / `worktree/i`,
accessed 2026-10-20. The installed 2.55.0 manual has no `worktree` keyword
(verified against lines 600-663 and a whole-file grep).

| id | quote (words) | web location |
|---|---|---|
| Q24 | "The worktree location is the path where files are checked out (as returned by git rev-parse --show-toplevel)." (19) | `#_conditional_includes`, keyword `worktree` |
| Q25 | "Unlike gitdir, the worktree condition currently matches only the realpath-resolved worktree location." (13) | `#_conditional_includes`, keyword `worktree` |
| Q26 | "This condition will never match in a bare repository (which has no worktree)." (14) | `#_conditional_includes`, keyword `worktree` |

### Path value type, options, precedence, second config file

| id | quote (words) | installed location | web location |
|---|---|---|---|
| Q27 | "A variable that takes a pathname value can be given a string that begins with \"~/\" or \"~user/\"" (18) | lines 800-802 | `#_values` / pathname |
| Q28 | "~user/ to the specified user's home directory" (8) | line 803 | same |
| Q29 | "If a path starts with %(prefix)/, the remainder is interpreted as a path relative to Git's \"runtime prefix\"" (18) | lines 805-806 | same |
| Q30 | "If prefixed with :(optional), the configuration variable is treated as if it does not exist if the named path does not exist." (22) | lines 812-813 | same |
| Q31 | "Defaults to off when a specific file is given" (10) | `--includes, --no-includes`, line 252 | `#_options` |
| Q32 | "This is optional and is only searched when extensions.worktreeConfig is present in $GIT_DIR/config." (13) | lines 326-328 | `#_files` |
| Q33 | "The files are read in the order given above, with last value found taking precedence over values read earlier." (20) | lines 338-339 | `#_files` |
| Q34 | "You may also provide additional configuration parameters when running any git command by using the -c option." (17) | lines 330-331 | `#_files` |
| Q35 | "include.path, includeIf.<condition>.path" (2) | line 4152 | `#_variables` |

---

## 3. Current guard behavior (observed source, snapshot in §0)

- `guard_git_config` lines 493-522: refuses a symlinked `config` (496-498), parses
  file-local keys with `git config --file "$cfg" --no-includes --name-only --list`
  (500), lowercases the key list (503), and refuses on any key matched by the line
  505 glob, including `*include.*` and `*includeif.*` (505-506).
- `core.worktree` is already handled value-aware (511-521): tilde values refused
  (514), absolute values passed through, relative values joined to the gitdir
  (517-519), then `guard_target` resolves and boundary-checks before use (520).
  This is the in-repo precedent for path-valued keys; `include.path` can reuse the
  same shape but must additionally expand `~`/`~user`/`%(prefix)` (F2) and iterate
  all values (F3).
- The guard scans only `$dir/config` (495). It does not scan `$dir/config.worktree`;
  that file is effective only when `extensions.worktreeConfig` is present (Q32).
  On a linked worktree the guard is also called on the admin dir
  (`guard_git_surface` call sites), so `$dir` is the admin gitdir, not the worktree.
- `status` drains later config effects with `-c core.fsmonitor=false`,
  `-c core.hooksPath=/dev/null`, `-c core.excludesFile=/dev/null`,
  `-c core.attributesFile=/dev/null` (lines 710-712). Command-line configuration is
  listed after the config files and last value wins (Q33, Q34), so those four keys
  are overridden for the status invocation regardless of an included value. Other
  git invocations (`worktree list` line 688/836, `for-each-ref` 694,
  `rev-list` 698/702) carry no such `-c` overrides, and other refused keys
  (`filter.*`, `core.alternateRefsCommand`, promisor/partial clone,
  `extensions.worktreeConfig`) are not overridden anywhere.
- `guard_target` line 422 resolves internal targets allowing `..`; `guard_path`
  refuses `..` as ambiguous. Include values are config-authored and legitimately may
  contain `..` (Q6), so include resolution belongs on the `guard_target` side, with
  the target guarded before any read.

---

## 4. What the documentation requires of a value/condition-aware repair

Design inference (ConfigRepair owns the final algorithm); each item cites the
documented constraint it must satisfy.

### 4.1 Include path resolution

1. Parse values with `--no-includes` (current line 500 is correct and matches Q31).
2. Enumerate **all** values, not the first: `include.path` is multi-valued (Q4).
   `git config --file ... --get-all include.path` and a per-condition enumeration
   for `includeIf.<condition>.path` are the documented value forms (Q35).
3. Resolve each value in this order, before any open:
   - empty or unparsable value: refuse as unsupported or define a stable finding;
     the manual does not define an empty include path (unresolved).
   - `:(optional)` prefix: documented for pathname-typed variables (Q30); if
     admitted, strip it before resolution and define missing-target behavior.
     Applicability to `include.path` is **M**, not stated in §Includes.
   - `%(prefix)/`: documented pathname expansion (Q29); resolves against Git's
     install prefix, outside the repository. Either resolve and boundary-check, or
     refuse the form as unsupported. Silent literal interpretation is wrong.
   - `~/` and `~user/`: documented (Q3, Q27, Q28). `~/` uses `$HOME`; `~user/`
     needs passwd lookup. `~user/` is a real escape from both repo and home and
     must not be lexically treated as a relative name.
   - absolute: use as-is.
   - relative: join to the **directory of the config file being scanned** (Q6, Q7,
     Q8), i.e. `$dir`, not cwd and not the worktree root.
4. Guard the resolved target with the protected-namespace resolver before the
   first read of that file, including nested includes. The guard must handle `..`
   as a real component (Q6, Q22) rather than refusing it as ambiguous input.

### 4.2 Included-file effects

Included content takes effect at the directive (Q5). Therefore a benign-looking
include is only as safe as the keys it can inject. A repair that admits an include
without scanning/effective-evaluating its content is value-blind at one remove.

Effect scope for the census's actual invocations:

- `core.fsmonitor`, `core.hooksPath`, `core.excludesFile`, `core.attributesFile`:
  overridden by `-c` on the status call (710-712), so an included value is inert
  **for that invocation** (Q33, Q34). It may still be relevant to other git
  invocations only if those read the key; that must be established per key, not
  assumed.
- `filter.*.clean|smudge|process`, `core.alternateRefsCommand`, promisor/partial
  clone: not neutralized by any `-c` in the tool. Whether any census invocation
  actually executes or reads them is **not established by this report**; do not
  admit them on the strength of "status does not run filters" without a cited
  effect source.
- `extensions.worktreeConfig`: false is inert and reveals nothing; true makes
  `$GIT_DIR/config.worktree` effective (Q32) and that file can itself include.
  Admitting true requires scanning `$dir/config.worktree` (and its includes) under
  the same rules; the current guard never opens it (495). The linked-worktree
  admin-dir path for `config.worktree` is not stated in the pages opened here
  (unresolved; confirm against gitrepository-layout(5) or git-worktree(1) before
  claiming it).

### 4.3 Condition applicability — pin to host 2.55.0

The host runs git 2.55.0-1. Its documented keyword set is Q9-Q23:
`gitdir`, `gitdir/i`, `onbranch`, `hasconfig:remote.*.url`. The `worktree` and
`worktree/i` keywords exist only in 2.56.0 (Q24-Q26) and must not be treated as
known conditions, admitted, or used as a basis for a no-read negative on this host.
Behavior for an unknown keyword in 2.55.0 is not documented in §Conditional
includes; do not assume "false".

If the repair evaluates conditions to prove an include inactive (no-read negative):

- `gitdir`/`gitdir/i` must match the **.git directory location** (Q10, Q11), with
  the glob expansions of Q12-Q16, against **both** symlink and realpath spellings
  outside `$GIT_DIR` (Q21). Inside `$GIT_DIR`, do not resolve symlinks before
  matching (Q20). `./` is relative to the config file's directory (Q13). `../`
  is literal (Q22) and must not be normalized into a parent traversal.
- A single-spelling or cwd-anchored matcher can produce a false "inactive"; if
  the evaluator cannot reproduce both forms and the exact glob rules, it must
  fail closed: treat the condition as possibly true, guard the target, and scan
  its content.
- `onbranch` requires the name of the branch checked out in **that worktree**
  (Q17). Detached HEAD, unborn branch, and bare repositories are not covered by
  the quoted sentence (unresolved); do not turn "no branch name" into an
  undocumented guarantee.
- `hasconfig:remote.*.url` requires the scan-ahead described in Q18 and the
  no-remote-URL prohibition in Q19. With global/system config disabled in this
  tool, the practical scan set is narrower, but the docs do not define that
  reduced set; exact truth remains **M/L** and a local-only test is not proof.

### 4.4 Namespace fence interaction

The include target is opened by git itself during later commands, not by the
guard. `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` do not affect repo-local includes
(prior-seat observation, `BoundaryAttack.md` 132-133). Consequently:

- Every include target that Git could apply must be boundary-checked **before**
  the first git invocation that applies it. "We did not read it ourselves" is not
  a fence; git will.
- A condition-false include can be skipped only when the evaluator is exact per
  §4.3; otherwise guard and scan its target.
- Recursive includes and cycles must be bounded by the repair's own explicit
  limit. The §Includes documentation opened here states no recursion limit (a
  whole-file grep of the 2.55.0 manual shows no include-depth statement), so any
  numeric bound is design-defined and must be labelled as such, not as Git parity.

### 4.5 Exact key matching

Q35 names the special variables exactly. The line 505 globs `*include.*` and
`*includeif.*` also match unrelated sections whose names merely contain those
strings (e.g. `[myinclude]`). The repair should match the documented key prefixes
`include.` and `includeif.` on the already-lowercased key list, so that a benign
unrelated section is not refused and the special variables are still caught.

---

## 5. Exact acceptance needed (behavioral, for ConfigFixture / ConfigRepair)

I did not inspect a repaired tool; at the snapshot above the include family is
still key-presence-refused. The following cases are the minimum falsifiable
acceptance for admitting benign includes while retaining the namespace gains.
All fixtures must use `/var/tmp` synthetic fleets and a synthetic HOME; none may
touch the real store. Baseline pairing: the same fixture run against the r14
baseline must show the safe cases red (`git-config-unsupported`) and the protected
cases refused; the repaired tool must invert only the safe cases.

| id | case | expected |
|---|---|---|
| A1 | `.git/config` has `[include] path = safe.inc`; `.git/safe.inc` has only benign keys (`[user] name = fixture`) | row emitted; verdict identical to a no-include control; no access outside the fixture repo |
| A2 | `path = ../safe.inc` from `.git/config` (resolves in the repo root, outside `.git`) | row emitted; proves the base is the config file's directory and `..` was resolved, not refused as ambiguous |
| A3 | `path = ~/souji-fixture/safe.inc` with fixture HOME | admitted when outside protected namespace and benign; trace shows no real-HOME access |
| A4 | `path = ~/.omp/agent/<canary>` or `path = ../<fixture-home>/.omp/agent/<canary>` | `path-protected`, exit 2, no `openat`/`getdents64` below the synthetic store, canary never emitted |
| A5 | two values: benign first, protected second | refused; proves all values are inspected (Q4) |
| A6 | `includeIf "gitdir:<this repo's gitdir>/"` true vs `gitdir:/definitely/not/this/repo/` false, target benign | true: admitted and content scanned; false: either no-read negative with no open of the target, or refusal; never a silent read |
| A7 | false-condition target is protected | no protected access; refusal or no-read negative both acceptable, finding must be explicit |
| A8 | true-condition included file sets a refused key (`core.hooksPath=...` or a shell filter) | refused, unless the exact invocation-effect analysis proves the key is overridden for every census git call; the chosen policy must be pinned in the fixture |
| A9 | nested include `a.inc -> b.inc`, and a cycle `a <-> b` | bounded termination, every target guarded before read, no hang; exact finding pinned; no claim of Git-parity depth |
| A10 | mixed fleet: one safe-include repo, one ordinary repo, one linked worktree repo | all rows emitted, ordinary/linked verdicts unchanged, compare output unchanged |
| A11 | version pin | fixture records `git --version`; no case asserts `worktree:`/`worktree/i` semantics (2.56-only, Q24-Q26) |
| A12 | unparsable/empty/`~user`/`%(prefix)`/`:(optional)` values | each either resolved per §4.1 or refused with a stable finding; no silent literal interpretation |

Additionally: the failure output must name the reason and path (current
`protected_fail` shape, line 160), and `--selftest` plus the legacy 38-check
coverage must remain green. The repaired header comment (current lines 84-91)
must describe the new value/effect rule rather than "any include key is refused".

---

## 6. Observed, inference, unresolved

Observed (quoted docs / read source):

- The include semantics in §2, including the 2.55.0 vs 2.56.0 keyword delta.
- Line 505 refuses by substrings; line 500 is file-local; lines 511-521 already
  implement a value-aware path key; lines 710-712 override four keys with `-c`.
- The manual documents no include recursion limit in §Includes.

Inference (stated assumption):

- The generic `pathname` expansions (`~user/`, `%(prefix)/`, `:(optional)`) apply
  to `include.path` because the Includes section calls it "a pathname" (Q3, Q27),
  but §Includes itself only promises tilde expansion.
- `-c` overrides included values because the read order lists `-c` after the config
  files and last value wins (Q33, Q34).
- Whether `git status` executes any `filter.*` program, and whether
  `rev-list`/`for-each-ref`/`worktree list` read `core.alternateRefsCommand` or
  promisor settings, is outside the pages opened here; those effects are
  unresolved and must not be asserted.

Unresolved gaps (do not build on them):

- Unknown-condition behavior on 2.55.0.
- Missing include target behavior; empty include path; duplicate include of the
  same file; include of a directory; include of a non-regular file.
- Include recursion/cycle limit (not in the manual).
- `includeIf` evaluation context when `git config --file ... --includes` is used;
  not documented in the option text opened here.
- `config.worktree` path for linked worktrees and its own include base.
- Whether the census's `rev-list`/`for-each-ref`/`worktree list` invocations can
  execute shell commands from config (`core.alternateRefsCommand`) in this tool's
  argument shapes.

---

## 7. Unrun checks

No tests, selftests, fixtures, builds, linters, formatters, smoke runs, or runtime
probes were run. No census was executed. No source, fixture, registry, lesson,
LOG, or SCORECARD file was edited. The exact acceptance in §5 is L1's to execute
after the wave; this report's doc quotes are source inspection, not runtime proof.
