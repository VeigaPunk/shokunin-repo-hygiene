# NamespaceRetain — round 15 w1 (sentinel, source inspection only)

Axes: **operability** (C1 repair must not lose any R14C2 namespace gain) and **calibration** (what the unchanged r14 fixture can and cannot prove about retention).

**Status: design-only.** At report time `tools/souji-census.sh` is byte-identical to HEAD `cc21683`: `git diff --stat HEAD` is empty and sha256 is `fcff8b05…aee9`, the round-14 installed digest. ConfigRepair has not landed. `tests/fixtures/r15-census-config.py` is absent. The unchanged r14 fixture `tests/fixtures/r14-census-boundary.py` has sha256 `e6a984b1…14b2` and was last changed at `552cae4`. Every line number below refers to those bytes. Behavioural claims about git are cited from docs or marked **[INFERENCE]**. Nothing was executed.

## 1. Per-case ordering invariants the repair must keep

| Case | What it pins (fixture lines) | Source ordering that makes it pass | Repair change that would turn it red |
|---|---|---|---|
| 01/02/03 store, descendant, HOME ancestor | rc 2, `path-protected`, empty stdout, no stat of store root (`refusal_problems`, strict `allow_root_stat=False`, 480-502) | `main` guards at 1527-1528 before `command -v` and git. `resolve_guarded` refuses at 357-361 before the first lstat. | Any git or `stat` call moved above 1527, or a new input path (for example an include value) checked only after a stat. |
| 04 symlink alias and `alias/..` | same | `..` is refused as ambiguous for user input (341-343). The walk folds each link one hop at a time. The suffix check at 380-384 runs before `[ -L ]` at 385. | Using `readlink -m`/`realpath` on input, or allowing `..` in user paths (`allow=1` belongs only to internal git targets, 422-426). |
| 05 compare direct, alias, `/proc/self/fd` | same | Order is `guard_path` (1528), then `load_census` `guard_path` (1007), then the special-path refusal (1009-1010), then `[ -f ]` (1012), then the nlink check (1015-1023), then the read (1025-1054). | Reordering `[ -f ]`/`[ -r ]` above 1007-1010. |
| 06 gitfile, `.git` symlink, commondir to store (`--include-root`) | same | `list_repos` 926-936 calls `guard_git_surface`. For gitfile and commondir, `guard_target` runs (647, 662). **`guard_git_config` (613, 650) runs before the commondir guard (614-630, 651-667).** | Any git call added inside `guard_git_config` that does repo discovery (see N1). |
| 07 safe fleet | rc 0, row `1/0/0/clean`, no store string in spy or strace, strict stat (505-541) | Startup `resolve_guarded "$lex/.omp"` (260) stats `.omp` only, never `.omp/agent`. | Seeding roots by resolving `.omp/agent` itself. A new column or a changed `clean` derivation (HEADER pinned at fixture 42). |
| 08 `.scratch` → store | rc 0, `scratch_bytes=0`, lenient root stat | `[ -L ]` runs before `[ -e ]`/`[ -d ]`/`du` (726-728). | Any new attribute/include/ignore logic that touches `.scratch`. |
| 09 poisoned `GIT_*` + `HOME=<store>` | rc 0 normal row, no store access | `GIT_*` scrub (119) runs before any git. `build_protected_roots` skips resolving a home that is itself protected (244). Status passes `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` (711-712). | Dropping those two overrides, or adding any excludes- or attributes-reading git call without them (N4). Re-exporting `GIT_*` before 119. |
| 10 worktree admin commondir → store | rc 2, empty stdout | `guard_worktree_registrations` (555-601) runs inside the surface guard during `list_repos`, before `git worktree list` (688, 836). Admin `guard_git_config` (581) runs before the admin commondir guard (582-595). | Same as 06. Moving the registration guard after `count_worktrees`. |
| 11 alternates chain → store | rc 2, empty stdout | `guard_alternates` (631/668) recursion depth ≤5, in `list_repos`, before any git. | Running any object-touching git call before 631. |
| 12 symlink child → store repo | rc 0, row for normal2, strict stat | Order: lexical candidate check (948), then `[ -L ] && continue` (952), then `[ -d ]` (953). | Swapping 952/953. `[ -d ]` follows the link through the mode-000 store and gives EACCES. |

Cross-cutting: all rows are buffered and the header is printed only after every repository has been guarded (980-994). A late refusal therefore still leaves stdout empty. Streaming rows for mixed-fleet support would break that refusal contract for multi-repo fleets. The r14 fixture tests single-repo refusals only, so it would not catch this.

## 2. Findings

### N1 — HIGH (conditional on the repair) — git calls that depend on config, placed inside `guard_git_config`, run before the commondir, alternates and worktree guards

- **Exploit path.** `guard_git_config` is called at 581, 613 and 650, before the commondir guard (582-595, 614-630, 651-667), `guard_alternates` (631, 668) and `guard_worktree_registrations` (632, 669). A value-aware repair might evaluate includeIf applicability with git: `rev-parse --git-dir`/`--show-toplevel` for `gitdir:`/`worktree:`, or `symbolic-ref` for `onbranch:`. It might also switch to `git -C "$dir" config …` or `--includes`. Each of those triggers repository setup. **[INFERENCE]** Repository setup reads `commondir` and `<commondir>/config` (format and extension checks), so on the R14C2-06 commondir shape and the R14C2-10 shape it opens `GD/config` under the mode-000 store before the guard can refuse.
- **Why r14 cannot see it.** The fixture's repositories carry no config families (FixtureCounts #3). A git call that runs only when `include`/`includeIf`/`worktreeConfig` keys are present is never reached. R14C2-06/10 stay green while the regression is live.
- **Smallest remediation.**
  1. `guard_git_config` runs no git command except `git config --file <already-guarded file> --no-includes [-z]`.
  2. Treat every `includeIf.*.path` as reachable, so the guard covers a superset of what git reads. Do not evaluate conditions in the guard. IncludeIfSafe notes that `hasconfig:` reads its target unconditionally anyway.
  3. Alternatively, move all config scanning in `guard_git_surface` to after the commondir, alternates and registration guards.
- **Acceptance (r15 fixture).** Pair a benign `includeIf "gitdir:…"`/`onbranch:` with each of: commondir → store, worktree-admin commondir → store, alternates → store. Expected: rc 2, `path-protected`, empty stdout, zero `trace_access(..., allow_root_stat=False, follow_open_symlinks=True)` hits.

### N2 — HIGH (conditional) — nested relative includes must resolve against the path git builds, not the resolved target

- **Git semantics.** Git resolves a relative include against the directory of the config file that contains the directive ([git-config Includes](https://git-scm.com/docs/git-config#_includes)). For a nested include, that file is the include path as git constructed it. **[INFERENCE from `config.c` `handle_path_include`, which uses `kvi->filename`.]** If an included file is a symlink, nested relative includes are therefore based on the symlink's directory, not the target's.
- **Exploit path.**
  - Repo config: `include.path=/fleet/inc/a.inc`.
  - `a.inc` is a symlink to `/fleet/other/b.inc`.
  - `b.inc` contains `path = c.inc`.
  - `/fleet/inc/c.inc` is a symlink to a store file. `/fleet/other/c.inc` is benign.
  - A guard that takes the base from `guard_target a.inc` (which gives `/fleet/other`) checks the benign file. Git then opens `/fleet/inc/c.inc` and reaches the store.
- **Remediation.** Carry the unresolved path git uses for each level, build `${parent_unresolved%/*}/$value`, and pass that string to `guard_target`. For top-level configs the gitdir base is equivalent either way, because kernel resolution of the directory is the same.
- **Acceptance.** Add exactly this world as a red case, plus a benign mirror world (symlinked include whose nested target is benign) that stays green.

### N3 — HIGH — namespace refusals must stay whole-run exit 2; only non-namespace "unsupported" may degrade per row

- **Constraint.** R14C2-06/10/11 assert rc 2, `path-protected` and empty stdout for a single `--include-root` repo (fixture 480-502, 579-588, 617-622). If the mixed-fleet repair routes a protected hit through a new per-row path such as a `config-unsupported` flag, those cases go red. If it routes a store-pointing include, `config.worktree` or `core.worktree` value through that path, the namespace contract weakens silently.
- **Required split.**
  - Every path-shaped value goes through `guard_target`, so a protected hit gives `protected_fail <reason>` and exits 2 for the whole run, consistent with R14C2-06.
  - Only refusals not caused by a store path (filter commands, true promisor, non-path unsupported) may use a distinct row flag or finding.
  - The current label `path-protected: git-config-unsupported` (506, 514) mislabels non-namespace refusals. That is a calibration defect, but changing it does not affect r14 (no case asserts it).
- **Mutation oracle.** Replace `protected_fail` with a per-row skip inside `guard_target` or `guard_git_surface`. R14C2-06, 10 and 11 must fail on rc and stdout.

### N4 — MEDIUM — the status overrides are what keep R14C2-09 (`HOME=<store>`) green; keep them on every call that reads excludes or attributes

- **Exploit path.** With `HOME=AGENT`, the defaults for `core.excludesFile`/`core.attributesFile` are `$XDG_CONFIG_HOME/git/{ignore,attributes}`, falling back to `$HOME/.config/git/…` (git-config core.excludesFile/attributesFile). `GIT_CONFIG_GLOBAL=/dev/null` (122) does not disable those defaults. Only `-c …=/dev/null` (711-712) does.
- **[INFERENCE]** Dropping either override, for example to honour a benign repo-local excludes file, or adding `check-ignore`, `check-attr`, `ls-files --exclude-standard` or `diff` without them, makes git `access()` a path under the mode-000 store. That gives EACCES, a strace hit, and R14C2-09 home-store goes red.
- **Calibration value.** R14C2-09 is a genuine oracle for the overrides. It is not an oracle for include closure or other config values.
- **Remediation.** If HooksNeutral A2 introduces a shared `GIT_RO` wrapper, it must carry all four overrides on every census git call. Do not honour a repo-local excludes value by removing the default-blocking override (agrees with ExcludesSafe R2/F6).

### N5 — LOW (pre-existing; the repair adds more instances) — the guard's `git config --file` does repository discovery from `$PWD`

- **Source.** 500 and 511 run `git config --file "$cfg"` with the caller's working directory. **[INFERENCE: the `config` builtin sets up the repository gently and discovers from cwd.]**
- **Exploit path.** If the operator's cwd is inside the store, or inside a worktree whose gitfile or commondir points into the store, git reads store metadata before or independently of any guard.
- **Coverage.** Untested, because the fixture always runs with `cwd=SCRATCH` (394).
- **Remediation.** Run every guard-time `git config --file` from `/` in a subshell (`cd / && git config --file …`). Do **not** use `-C "$dir"`, which triggers N1.

### N6 — LOW (pre-existing) — `id`/`getent` are not on the `unset -f` list

- **Source.** `passwd_home` (199-206) calls `id` and `getent`. 112 removes imported functions only for `git find du stat awk grep sort head cut date readlink`.
- **Exploit path.** An exported `BASH_FUNC_getent%%` that prints nothing removes the passwd-home root. With HOME also poisoned (the R14C2-09 shape), a relocated `~/.omp` symlinked to a directory not named `.omp` loses the protection added at 257-267.
- **Bound.** The `.omp/agent` component-pair rule (286-288) still covers lexical and symlink-chained aliases.
- **Remediation.** Add `id getent` to 112, plus any new external command the repair introduces (for example `sed` or `tr`).

### N7 — MEDIUM (calibration, C2) — 12/12 on the unchanged r14 fixture is necessary, not sufficient, for "namespace gains retained"

- **Why.** The r14 fixture has no config-bearing repository, so it cannot show that any new value-aware path is safe: include closure, `config.worktree`, `core.worktree` from `config.worktree`, a hooks/excludes value pointing into the store.
- **What the admission checker must require:**
  1. r14 fixture sha256 `e6a984b1…14b2` unchanged at the measured commit.
  2. The exact ID set R14C2-01..12, PASS 12/12, `TOOL-KIND other`, with the installed tool digest bound to the measured commit.
  3. The r15 config fixture's **protected-value** cases, each with trace oracles: include to store, includeIf with a false condition to store, nested include to store, the N2 symlinked nested include, `config.worktree` to store with the extension true, N1 commondir/alternates/worktree combos, and a FIFO include target.
  4. Benign red→green pairs.
- **Reject:** a record with green-only benign rows, or with r14 12/12 but no protected-value rows.

## 3. Unrun checks for L1 (after all seats land)

1. `python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh`. Expect `total=12 failed=0`, exit 0, `TOOL-KIND other`. Record the fixture and tool sha256 values.
2. The r15 config fixture rows listed in N1, N2, N3 and N7, on the baseline `cc21683` tool and on the installed tool.
3. Mutation spot checks, run only on a `/var/tmp` copy:
   - Swap 952/953: expect R14C2-12 red.
   - Drop 711-712 overrides: expect R14C2-09 home-store red **[INFERENCE]**.
   - Turn `protected_fail` in `guard_target` into a per-row skip: expect R14C2-06, 10 and 11 red.
4. `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` and warning-level ShellCheck.

## Provenance

- **Read:** `tools/souji-census.sh` (whole file), `tests/fixtures/r14-census-boundary.py` (whole file), `corpus/lessons/round-14-verifier-spotcheck.md`, `census/round-15/claims.json`, the round-15 dispatch tasks, and sibling w1 reports (grep only, for de-duplication).
- **External:** https://git-scm.com/docs/git-config (Includes and Conditional includes; `config.worktree`; `extensions.worktreeConfig`).
- **Commands:** `git log/status/diff --stat`, `git show --stat cc21683`, `sha256sum` on two lane files. No tests, probes, census runs or builds.
- **Tool installs/updates:** none.
- **Not opened:** `~/.omp/agent/**`, credential or auth files. No file under `census/operator-sweep-20261019/` was opened, edited, copied or moved.
- **Boundary violation (disclosed, not repeated).** My first discovery batch ran `grep pattern="namespace" case=false path="souji-shokunin"`, a recursive search over the whole lane root. That includes the untracked operator directory `census/operator-sweep-20261019/` (searched, not opened) and printed matching lines from `census/operator-sweep-20261018/stale-*.txt`. None of that output was used in this report. Limitation: the findings above rest only on the explicit source paths listed under "Read". After the parent's reminder, no further lane-root or census-recursive grep or glob was issued. A second grep, scoped to `.ufo/waves/round-15/w1`, stayed inside the round-15 evidence path.
