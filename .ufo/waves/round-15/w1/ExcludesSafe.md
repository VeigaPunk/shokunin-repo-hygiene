# Souji R15 w1 — ExcludesSafe (core.excludesFile vs dirty count)

Seat: ExcludesSafe (reviewer, leaf). Source inspection only. No tests, probes, builds, commits, or edits outside this report. No operator-sweep, credential, or agent.db access. Tools installed or upgraded: none. Read-only commands: `git show`/`git log`/`git rev-parse` on the lane repo, `zcat` on installed git man pages (git 2.55.0).

Source state: round-14 source landed at HEAD `cc21683`; `tools/souji-census.sh` is committed clean. The round-15 repair is not landed, so every repair statement below is **design-only**. Line numbers are for the committed file.

Axes: **operability** (primary; the round-14 rejected-harmed defect). **calibration** (the dirty-count semantic change and the acceptance evidence).

## Verdict

1. The key-only refusal of `core.excludesFile` is redundant for safety. `count_dirty` is the only reader of ignore rules in the census. It already forces `-c core.excludesFile=/dev/null`, so a repo-local value is never opened or stat'd. Removing the refusal does not weaken protected-namespace containment.
2. The override is the load-bearing control and must stay. Without it, a repo-local excludes file that ignores everything (`*`) would hide untracked content and produce a false `clean`. With it, the dirty count can only rise or stay the same relative to the excludes-honouring view.
3. Repair shape: **effect-aware, not value-aware**. Delete `*core.excludesfile*` from the refusal list. Do not add a value check that resolves the configured path. Resolving it would stat a possibly protected path, which is the F-B class from round 14.
4. Separate finding (calibration, MEDIUM): the round-14 override changed the dirty count for every repo, not only repos with the key. Pre-round-14 `count_dirty` honoured the repo excludes file and the XDG default ignore file. The new count can be higher, so `--compare` against pre-round-14 censuses will show drift. This is not a safety regression, but it is undisclosed in the census header.

## Facts (source, committed HEAD `cc21683`)

**F1. Value-blind refusal.** `guard_git_config` reads key names only (`git config --name-only --list`, line 500; lowercased, line 503). A key-presence `case` refuses on `*core.excludesfile*` (line 505) through `protected_fail "git-config-unsupported"` (line 506). The value is never inspected. The same applies to `*core.attributesfile*` on the same line.

**F2. Whole-census abort, not a per-row skip.** `protected_fail` writes to stderr and `exit 2` (lines 160-163). `list_repos` calls `guard_git_surface` for each direct child in the parent shell (line 964; include-root at 931 and 934). That reaches `guard_git_config` through `guard_git_surface` (call site line 613 and 628/650/665 in the sibling worktree/gitfile paths). `emit_census` calls `list_repos` (line 979) before it prints the header (line 991). One benign repo therefore exits 2 with no TSV and no peer rows. Linked-worktree and `census_one` paths run in a `$(...)` subshell, but `emit_census` propagates rc 2 (lines 982-988), so the outcome is the same. This confirms the round-14 closure statement at `corpus/lessons/round-14-verifier-spotcheck.md:104-106` (reopened here, not relied on).

**F3. The only ignore-rule reader is `count_dirty`.** The only `status` invocation in the tool is lines 710-716. Other census git calls do not read excludes or attributes: `worktree list` (688, 836), `for-each-ref` (694), `rev-list` (698, 702), `rev-parse --is-inside-work-tree` (859). `count_dirty` is called at 832 (linked worktrees) and 870 (main tree). [F, grep of `souji-census.sh` for `status`, `count_dirty`, `excludes`]

**F4. The override is already present and covers the value.** Lines 710-712:
`git -C "$1" --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null status --porcelain --ignore-submodules=all -- .`
Git documents `-c` as overriding values from configuration files (`git(1)`, `-c <name>=<value>`, read from the installed man page). The repo-local `core.excludesFile` value is therefore inert for `status`. Git documents `core.excludesFile` as lowest-precedence ignore source, after command line, per-directory `.gitignore`, and `.git/info/exclude`, defaulting to `$XDG_CONFIG_HOME/git/ignore` (`git-config(1)` core.excludesFile; `gitignore(5)` precedence list). [F, installed man pages]

**F5. Monotone effect on the dirty count (for `core.excludesFile` only).** Let D0 be the count with excludes honoured and D1 the count with `-c core.excludesFile=/dev/null`.
- Tracked-path status (modified, deleted, staged) does not depend on ignore rules. Unchanged.
- Ignored paths never appear in `status --porcelain` without `--ignored`. Unchanged.
- Untracked paths: removing the lowest-precedence ignore layer can only turn an ignored path into a shown `??` path. A collapsed untracked directory stays one line. A directory that was fully excluded can now appear as one line.
- Result: **D1 ≥ D0**, always. The override can add dirty lines. It cannot hide any. [INFERENCE from the documented precedence order, not an executed fixture]
- Consequence: dropping the refusal cannot produce a false `clean` through excludes. A false `clean` would need the override removed. A repo-local `*` excludes file is the attack shape. It is neutralized only by F4.

**F6. Dirty-count semantic change in round 14 (undisclosed in header).** At `a31642d`, `count_dirty` (lines 127-137) ran plain `git status --porcelain` with no `core.excludesFile` override. The override and the key refusal both landed in round 14 (commits `48f8945` and `552cae4`; `git show` on each shows lines 711-712 and the header at 86). Consequences:
- Every repo with an XDG default ignore file, or a repo-local excludes file, now reports higher `dirty` than pre-round-14 `count_dirty`. Operator impact is [INFERENCE]; code facts are [F].
- `--compare` (lines 1028-1029 header check; drift exit 3) will report dirty drift against pre-round-14 TSVs for those repos.
- The header at 33-36 says dirty is "`git status --porcelain` line count", which is no longer what the operator's own `git status` reports for such repos. The header must say that dirty ignores repo and XDG excludes.
- Routing: safety outranks compatibility here. Honouring the repo-local excludes file would require reading a repo-chosen path, possibly into the store. Do not reverse the override to restore the old count.

**F7. Attributes are not covered by the same monotone argument.** `core.attributesFile=/dev/null` (line 712) also removes the attributes layer. Attributes can enable or disable EOL and content normalisation during the modified check, so the dirty count may move in either direction. [INFERENCE; out of scope for this seat, route to the attributes seat.]

**F8. Hang class.** Git reads the excludes file only inside `status`. The override replaces the path with `/dev/null`, so a FIFO or huge excludes file cannot hang or be opened. Removing the refusal does not reintroduce that hang. [INFERENCE from F4; no FIFO probe permitted]

**F9. No benign-config control exists.** `tests/fixtures/r14-census-boundary.py` has 12 cases (`EXPECTED_IDS`, lines 45-58). Positive cases 07, 08, 12 (lines 591-598, 617-626) use normal repos. Case 09 sets only `core.worktree` through env (lines 601-611). Grep of the fixture and of `census/round-14` finds no `core.excludesFile`. The round-14 closure states the same gap (`round-14-verifier-spotcheck.md:105`). [F]

## Recommendations (design-only, for the executor seat that owns the repair)

R1. Delete `*core.excludesfile*` from the refusal case at line 505. Keep every other pattern in that case unless another seat's finding removes it.

R2. Do not add a value check or `guard_target` on the configured excludes path. The configured value is never read, so resolving it adds a stat of a possibly protected path.

R3. Keep `-c core.excludesFile=/dev/null` at line 711 unconditionally. Add a static invariant: the count of `status --porcelain` in `tools/souji-census.sh` equals the count of `-c core.excludesFile=/dev/null` on the same command. Any future `status` call without the override is a false-clean path.

R4. Update the header refused-list at lines 85-88 and `CensusBoundary.md` lines 103-112 and 226-227 to remove `core.excludesFile`. Add a header sentence: dirty ignores repo-local and XDG excludes, so it may exceed plain `git status`, and `--compare` drift against pre-round-14 TSVs is expected for such repos (F6).

R5. Do not change `core.attributesFile` in this seat's repair. Route F7 to the attributes seat.

## Acceptance for the repair (L1 to run; synthetic `/var/tmp` fixtures only)

A1. **Red/green, benign local excludes.** Repo with `core.excludesFile=.ignore-local` in-repo, `.ignore-local` contains `*.log`, untracked `a.log`, tracked and committed `keep.txt` clean. Round-14 source: rc 2, `git-config-unsupported`. Changed source: rc 0, one row, `dirty=1`. Assert **dirty=1, not 0**. A 0 means the override was dropped.

A2. **Anti-false-clean control.** Same as A1, but `.ignore-local` contains `*`, untracked `b.txt`. Changed source must report `dirty ≥ 1`. A `dirty=0` is a fail.

A3. **Mixed fleet.** A1 repo plus a plain repo under one root. Changed source: rc 0, header first, both rows present. Round-14 source: rc 2, no header.

A4. **No read, no stat, no hang of the configured path.** `core.excludesFile` points at a synthetic store-like path (a FIFO and a sentinel file under `/var/tmp`). Changed source: rc 0 under `timeout`. The spy trace (the fixture's `SPY_TOOLS` method, or `strace -e trace=openat,newfstatat,statx,readlink,access` filtered to the path) shows zero hits on that path. This covers F-B widened tracing too.

A5. **Namespace non-regression.** `R14C2-01..12` (fixture lines 45-58) keep their current expected outcomes. Legacy census selftest unchanged.

A6. **Compare drift documented, not hidden.** A pre-round-14 TSV and a changed census of a fleet with one XDG-ignored untracked file: `--compare` exit 3 with a single `dirty` row for that repo. Any `dirty` drift for a repo with no ignore rules is a regression.

A7. **Static invariant.** The R3 grep check returns equal counts.

## Unrun checks

Nothing executed. A1-A7 are specifications, not results. No runtime evidence is claimed. F5, F7, F8 are [INFERENCE] from the documented precedence rules and the source, not from an executed fixture.

## Residual risk

- Untested monotonicity assumption for directory-collapse cases (F5). Checkable by A1/A2 plus one partially-excluded-directory fixture.
- Operator-facing dirty semantics change (F6) needs an explicit note in the header and in any closure text.
- Attributes behaviour (F7) is not analysed here.

## Query-boundary disclosure

My early discovery calls were broader than the boundary now stated by SoujiR15. (1) A recursive `_glob` of `souji-shokunin/**/*` listed file names under `census/operator-sweep-20261019/` (names only, no contents read). (2) A `_grep` over the whole lane root matched across the tree, including `census/` paths, with no operator-sweep path exclusion. Neither call opened, copied, or modified operator-sweep content, but both queried that directory's namespace. Those calls are not repeated. Every later source read was limited to named files (`tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, `corpus/lessons/round-14-verifier-spotcheck.md`, `census/round-15/claims.json`, `.ufo/waves/round-15/*`, and `census/round-14` and `corpus/` path-scoped greps). Git reads were `git log`, `git show <rev>:tools/souji-census.sh`, `git rev-parse`, and a path-scoped `git status -- tools/souji-census.sh`. No runtime probes or tests were run. The findings above rest only on the named files, and the operator-sweep listing contributed no finding.
