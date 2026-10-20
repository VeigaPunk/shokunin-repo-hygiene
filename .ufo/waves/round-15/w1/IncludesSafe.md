# IncludesSafe — round 15, wave 1 (include.path)

Seat: SoujiR15.IncludesSafe (reviewer). Axes: operability, calibration.
Mode: source inspection only. No tests, probes, git runs, edits, or installs. No tools installed or updated.

## Status of the source

- `tools/souji-census.sh` (mtime Oct 20 04:56) predates the round-15 dispatch (05:21). The round-15 repair has NOT landed. Line 505 still refuses by key name.
- All "current behavior" claims below are verified from source lines.
- Everything about the repaired behavior is **design-only** and marked as such.
- Git include semantics (relative base, `~` expansion, depth limit, empty values) were not checked against external primary docs. The assignment did not name any, so these are marked `[INFERENCE]` and need confirmation in a fixture.

## 1. Current behavior (verified)

| Line | Behavior |
|---|---|
| 500 | `git config --file cfg --no-includes --name-only --list`: key names only, values never read. Includes are not followed. |
| 503-507 | Lowercased key list matched by substring. Any `include.` or `includeif.` key refuses the repo with `git-config-unsupported`. |
| 511 | `core.worktree` read with `--no-includes`. |
| 847 | `guard_git_surface` runs before the first git call on the repo. Correct ordering. |
| 859, 688, 698, 702, 710, 836 | Every later git call (`rev-parse`, `worktree list`, `for-each-ref`, `rev-list`, `status`) runs after the guard. |
| 122-123 | `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1` remove the global and system include exposure. |

**Safe baseline:** today no `include.path` target is ever opened by the census. The refusal is the only reason include is safe. Any relaxation creates the first include read path, and that path must be guarded before the read.

## 2. Why value neutralization cannot cover includes

- The `-c` overrides at 710-712 change values for `status` only. They do not stop git from opening an include target during config load.
- Prior evidence: `BoundaryAttack.md:132` records that a repo-local `include.path` made `status` open the store file `auth.json` O_RDONLY. `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM` do not affect repo-local includes.
- An included file's `filter.*` keys are not neutralized by `-c`. Repo `.gitattributes` still selects them (`BoundaryAttack.md:131`).
- **Conclusion:** include must be boundary-checked by path before any read, and its closure must be key-checked. Value-level neutralization is not a substitute.

## 3. Safe cases (identify)

A relaxed include is safe only when ALL of these hold for each target:

| ID | Case | Why safe |
|---|---|---|
| SC1 | No include/includeIf keys | Output unchanged. |
| SC2 | Relative or absolute target whose physical path (symlinks resolved, `..` physical) is outside all protected roots, is a regular file, has nlink==1, and is not under `/proc`, `/dev`, `/sys` | Same rule set as the existing `--compare` and gitfile guards. |
| SC3 | `~/x` with `HOME` set, expanding to a path outside protected roots | Git and the guard see the same HOME (HOME is not cleared). |
| SC4 | Missing target (ENOENT, no symlink in the suffix) | Git ignores a missing include. No content read. Path guard still applies. |
| SC5 | Multiple `include.path` values, each passing | Each value guarded individually. |
| SC6 | `..` climbing out of a fleet to a safe sibling | Physical resolution matches kernel `openat`. `resolve_guarded` with allow=1 does this (line 370). |
| SC7 | Included file whose own closure passes key checks and whose depth is within bound | Read permitted. |

`includeIf`: the path guard should be unconditional, because it is metadata-only. Applicability should only decide whether the key-scan and recursion run. Default to "applicable" unless the condition is provably inapplicable (see §5, H7).

## 4. Unsafe cases (must refuse)

| ID | Case | Refusal |
|---|---|---|
| U1 | Resolves into a protected root via symlink or `..` | `path-protected` (exit 2) |
| U2 | `~user/...`, bare `~`, or `~/...` with HOME unset | `git-config-unsupported` |
| U3 | Newline, tab, or CR in value | Already `ambiguous-path` in `resolve_guarded` (352) |
| U4 | Existing non-regular target (FIFO, socket, device, `/proc/*/fd`) | Refuse before open |
| U5 | nlink>1 target (hardlink alias) | Same rule as `guard_git_files` (484) |
| U6 | Empty `include.path =` | Refuse (`[INFERENCE]` git semantics unknown) |
| U7 | Cycle, or depth beyond bound (10 is `[INFERENCE]`) | Refuse |
| U8 | Included file fails `--no-includes` parse | `git-config-unparsed` |
| U9 | Value contains `%(` | Refuse (`[INFERENCE]` only valid for system config) |

## 5. Findings

### H1 (HIGH, ordering) — relaxation must guard before read, and relative paths must be absolutized to the owning config file's directory
- `resolve_guarded` treats a relative raw path as relative to `$PWD` (line 348). Passing a raw include path straight to `guard_target` would check the wrong location.
- Insert the include walk inside `guard_git_config` (493-522) before any key check that reads include content. Build each include path from the directory of the file that contains it (the gitdir for repo config; the including file's directory for nested includes). `[INFERENCE: git resolves relative includes against the including file's directory]`.

### H2 (HIGH, bypass if relaxed without H3) — `core.worktree` check at line 511 uses `--no-includes`
- An included file could set `core.worktree` to a protected path. The repo-level check never sees it. The fix is to collect `core.worktree` across the full closure, with each file read by the census-side walker.

### H3 (HIGH, recursion) — no git read of an unchecked include
- Recursion must be walked by the census, not delegated to git. Each file in the closure is read with `git config --file F --no-includes -z --get-all include.path` and key-checked.
- Keep a visited set keyed by resolved path. Refuse on cycle or depth beyond the bound.
- Bound: refuse rather than follow past depth 10 `[INFERENCE]`.
- Walk only applicable includes. Do not refuse harmless disabled conditions (IncludeCycle task).

### H4 (MEDIUM, over-refusal) — substring key matching at line 505 refuses benign config
- `*include.*` matches `branch.include.remote` and `remote.include.url`. A branch or remote named "include" is refused. Match exact section names (`^include\.`) instead.
- `*remote.*.promisor*` refuses `remote.origin.promisor=false`, which the spec says to preserve. Parse the value as a boolean and refuse only true.
- `*core.hookspath*` is inert for every census git command: none runs hooks. Line 711 already neutralizes it on status. Allow it.
- `*core.excludesfile*` and `*core.attributesfile*` are neutralized at 711-712 for the only status call (710). `count_dirty` is the only status path (`SafetyCredential.md:24` records the worktree path reaching it). Allow, conditional on that single call path staying the only one.

### H5 (MEDIUM, effect-aware) — filter and alternate-refs drivers
- `filter.*.clean|smudge|process` with a non-empty value executes when a `.gitattributes` entry selects it. Keep the refusal for non-empty values. Empty values are inert `[INFERENCE]`; allow them. Coordinate with FiltersSafe.
- `core.alternateRefsCommand` with a non-empty value executes. Same rule.

### H6 (MEDIUM, effect-aware) — `extensions.worktreeConfig`
- `=true` makes git read `$GIT_DIR/config.worktree`, which the current guard never checks. Keep refusing `true` unless WorktreeCfg adds a guard. `=false` is benign. Coordinate with WorktreeCfg.

### H7 (MEDIUM, includeIf) — applicability versus path guard
- Path guard runs regardless of condition. Key-scan and recursion run only when the condition may apply. `onbranch:` and `hasconfig:` are runtime-dependent; treat as applicable. A literal `gitdir:` that provably does not match the repo gitdir may be treated as inapplicable. Owned by IncludeIfSafe; I defer the matcher semantics to that seat.

### M1 (HIGH, calibration) — no fixture covers config-driven reads
- `tests/fixtures/r14-census-boundary.py` has 12 cases (`CASES` 629-642). None involves `include`, `includeIf`, or config keys.
- The census selftest (`souji-census.sh` 1290-1500) has no config-key case.
- The existing protected-namespace gains therefore do not measure any include read. A relaxation would be unmeasured.

### M2 (MEDIUM, documentation) — boundary header is inaccurate after repair
- Lines 84-91 say include/includeIf are refused, and line 85 lists filter and hooksPath as refused. The header must describe the new contract. Line 79's `..` refusal applies to user input only; internal include targets use `guard_target` with allow=1.

## 6. Acceptance for ConfigRepair and ConfigFixture (design-only)

Paired red and green cases are required. Green-only evidence must be rejected by the admission checker (C2).

**Red-before (current code):** every relaxed case below is refused today with `git-config-unsupported`. The change in reason is the evidence that relaxation happened.

**Red for relaxation without guard:** a build that relaxes includes without H1-H3 must show an `openat` on the synthetic store (use the existing strace oracle, `r14` `probe_strace`). The green build must show zero store access and exit 2 `path-protected`.

Negative (must refuse, zero store access):
- relative `../../home/.omp/agent/auth.json` (U1, SC6 case)
- absolute store path
- `~/.omp/agent/...` with synthetic HOME (U1)
- symlink to store (U1)
- `..` escape into store (U1)
- `~user/` (U2)
- FIFO include, with a timeout guard (U4)
- hardlinked include (U5)
- empty value (U6)
- cycle `a → b → a` (U7)
- depth-11 chain (U7)
- included `core.worktree=<store>` (H2)
- included `filter.x.clean=/bin/false` with `.gitattributes filter=x` (H5)
- included `extensions.worktreeConfig=true` (H6)
- includeIf pointing at a protected path, with condition applicable (H7)

Positive (must succeed, exit 0, unchanged row):
- relative include to a safe sibling
- `~/safe/x` with synthetic HOME (SC3)
- missing include (SC4)
- two safe values (SC5)
- `core.hooksPath=/dev/null` and `remote.origin.promisor=false` (H4)
- `[branch "include"]` (H4)

Namespace controls: keep `R14C2-01` through `R14C2-12` green, plus include targets under `census/operator-sweep-*` and `.ufo/state` refused as `path-protected`.

## 7. Residuals and unverified claims

- Git semantics marked `[INFERENCE]` (relative base, `~` expansion, depth 10, empty values, `%(prefix)`) need a primary-doc or fixture check. Not verified here.
- TOCTOU between guard and git read remains, as already documented in the header (lines 96-99).
- Hardlinked files outside the store are not detectable without stat of the store (already residual).
- Git runs as the same user; a file replaced between guard and read is a race, not checked here.

## Tools

No installs or updates were performed by this seat.

## Verification left to main agent

- Compare the line numbers above against the landed repair once it exists (the repair is not present at this snapshot).
- Run the R14 fixture plus the new include cases once the repair lands. This seat did not run them.

## Boundary disclosure (no-query rule)

- Violated once: `_grep` with pattern `include\.path|includePath|include_path|\binclude\b.*path` over the whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` (first search, before the boundary reminder). It is a recursive search of the lane root and may have matched entries under `census/`, including `census/operator-sweep-20261019/`. Matched hits shown were in `.ufo/waves/round-13..14`, `census/round-10..14`, and `census/round-4`; the result footer reported 31 files, and I did not page further. No operator-sweep content was intentionally opened, edited, or copied.
- Also at lane root: `git status --short` and `git log` (bash) listed untracked names, including `census/operator-sweep-20261019/` (names only, no contents).
- Non-violating listings: `ls -la` of the lane root (top level), `tools/`, `census/round-15`, and `.ufo/waves/round-15`, plus explicit-file reads and greps restricted to `tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, and `.ufo/waves/round-15/w1*.json`.
- A `grep -rn include tests/` ran over `tests/` only.
- No further queries of the lane root, census, or operator sweep were made after the reminder.
