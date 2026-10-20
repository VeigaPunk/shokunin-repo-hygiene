# FixtureOracles — souji round 15 (design-only review)

Seat: `SoujiR15.FixtureOracles`. Axes: operability, calibration.
Mode: source inspection only. No tests, probes, builds, or edits. No tool installed or upgraded.

## Status

- Source state: `tests/fixtures/r15-census-config.py` does not exist yet (`ls tests/fixtures | grep -c r15` = 0). `tools/souji-census.sh` is unchanged (worktree sha256 `fcff8b05…` = HEAD `552cae4`). This review is design-only; the acceptance below is what the eventual fixture's expected values must satisfy.
- Pinned reference hashes (git objects, verified):
  - `a31642d:tools/souji-census.sh` sha256 `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`. Matches `BASELINE_SHA` in `tests/fixtures/r14-census-boundary.py:61`.
  - `552cae4` (= HEAD, the r14 refusing tool) sha256 `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`.
  - `48f8945` sha256 `fd234148f0c44bcd1edc6857388e08354eba0bc98a59b78e480adf5ab2c3028c`. Not a reference for round 15.

## Findings (ordered by impact)

**F1. Round-14 fixture has zero coverage of any r14 refused config family.** `grep -i 'filter|promisor|worktreeconfig|excludes|attributes|alternaterefs|partialclone' tests/fixtures/r14-census-boundary.py` returns nothing. The only config touchpoint is `gitdir/config` `bare = true` (line ~221). Neither over-refusal (benign) nor harm (unsafe) for `include*`, `filter.*`, `hooksPath`, `attributesFile`, `excludesFile`, `promisor`, `worktreeConfig`, `alternateRefsCommand`, `partialClone` is exercised. Acceptance: one paired benign/unsafe case per family (see table).

**F2. Refusal oracle does not pin the reason.** `refusal_problems` (r14 fixture ~line 147) checks only that the token `path-protected` appears on stderr. The tool's `protected_fail` (`tools/souji-census.sh:160-163`) prints the reason as `$1`: `git-config-unsupported`, `git-config-unparsed`, `git-metadata-*`, `unresolved-path`, etc. A repair that refuses benign configs for the wrong reason would pass. Acceptance: each refusal case asserts the exact reason token; each benign case asserts exit 0 and the literal row.

**F3. "Mixed fleet rows retained" is unsatisfiable under current design.** `protected_fail` calls `exit 2` (`:163`), and `guard_git_surface` runs per repo before any row is emitted. One refused child aborts the whole census, so stdout is empty. The round-14 fixture asserts exactly that (`stdout is not empty`, `refusal_problems`). The ConfigFixture text ("unaffected mixed-fleet rows retained") contradicts this. Decision needed (D1). Recommended: mixed fleet = several benign children, all PASS with literal rows; any unsafe child = whole-run exit 2 with empty stdout. Per-row emission would be a new contract, not a repair.

**F4. Setup ordering hazard: harm markers fire during fixture setup.** `init_repo` (r14 fixture ~162-170) runs `git add` (applies clean filters), `git commit` (runs pre-commit hook), and `git update-ref` (runs `reference-transaction` hook). Any `filter.*`, `core.hooksPath`, or fsmonitor config written before setup will create the marker during setup and produce a false red/green. Acceptance: write harm config only after all setup git commands; measure marker by snapshot delta around the tool run, not by existence afterwards.

**F5. Non-vacuity: marker-absence is only meaningful if the trigger fires on the baseline.**
- Clean filter runs in `git status` only for tracked files whose stat differs from the index and that have an in-tree `filter=<name>` assignment. Fixture must `touch -d` the tracked file and commit it with the attribute before the tool run. Assert the marker exists on the a31642d baseline (red) and is absent on the repaired tool (green).
- `core.hooksPath`: census git commands (`worktree list`, `for-each-ref`, `rev-list`, `rev-parse`, `status`) fire no hooks. A hooksPath case is therefore green on the baseline and red only against the r14 refusing tool (`fcff8b…`). The gate must treat it that way. A baseline-red claim for hooksPath would be false.
- Acceptance: pin, per case, the expected result on both `a31642d` and `552cae4`. Both must be listed; a case that is green on both is a preservation control, not a discriminator.

**F6. Expected `dirty` must be literal by construction, not produced by `git status`.** `count_dirty` (`:710-713`) overrides `core.fsmonitor`, `core.hooksPath`, `core.excludesFile`, `core.attributesFile`, but not `filter.*` and not `status.showUntrackedFiles`. Consequences for the oracle:
- `core.excludesFile` ignoring `local.log`: census expected dirty is **1** (override makes the ignored untracked file visible); plain `git status` says 0. Oracle must pin 1 and state the override semantics, or refuse. Not 0.
- Transforming clean filter (e.g. `tr a-z A-Z`) and an unmodified tracked file: accurate dirty is **0**. Neutralizing the filter (no override exists) or using an empty clean yields dirty 1 (false dirty, not false clean). Acceptance: expect 0, which forces refusal rather than neutralization. This is a contract decision (D3).
- `status.showUntrackedFiles = no` (git-config docs, `status.showUntrackedFiles`) with one untracked file: the tool passes no `-u` flag, so dirty would be **0** (false clean). `status.showUntrackedFiles` is not in the r14 refusal list. Source-inspected, unrun. Pin expected dirty 1 and require refusal or an explicit `-unormal` override (D8). This is a candidate pre-existing false-clean, not something a benign-preservation change may silently keep.

**F7. Boolean values: oracles must follow git's rules, not tool output.** git-config Boolean section: true = `yes|on|true|1` (case-insensitive) and a bare key (no `=`); false = `no|off|false|0` and the empty string. Required cases:
- `remote.origin.promisor` bare → true → refuse; `promisor =` (empty) → false → PASS; `promisor = off`, `= No` → PASS; `promisor = Yes`, `= TRUE` → refuse.
- Same matrix for `extensions.worktreeConfig`.
- Expected values are hard-coded in the fixture table, never derived from `git config --bool` run by the tool.

**F8. Key-name matching hazards in the current guard (`tools/souji-census.sh:500-506`).**
- `keys` is lowercased in full (`:503`); subsection names are case-sensitive in git. `filter.Probe.clean` and `filter.probe.clean` are distinct drivers. Case: `.gitattributes filter=Probe` must map only to `filter.Probe.*`. A lowercased comparison mis-maps it.
- The substring pattern `*include.*` refuses benign keys such as `branch.include.remote` or `remote.include.url` (a subsection literally named `include`). Benign twin required: branch/remote named `include` → PASS.

**F9. Included-file contents are not inspected.** `guard_git_config` reads with `--no-includes` (`:500`, `:511`). Harm inside an included file is invisible to the guard today. Any repaired include handling must read and check the included file before git does. Required unsafe cases (each: marker absent, zero store access, exit 2, reason pinned):
- included `filter.x.clean` assigned by tree attribute;
- included `core.worktree` pointing outside the boundary;
- included store-target path;
- include chain A→B→A (must not hang; expected exit 2, bounded by timeout).
Benign: included file with `[color] ui = never` → PASS, literal row.

**F10. Multi-value and order.** `include.path` may repeat (git-config Includes). Acceptance: `[benign include, store include]` → refuse; reversed order → refuse (no stop at first match). Duplicate single-valued harm keys (e.g. `filter.x.clean` set twice, unsafe then empty): git uses the last value. Pin the expectation (D5); recommended conservative refuse-if-any-unsafe, with the reverse-order case pinned to match.

**F11. includeIf applicability.** git-config Conditional includes: `gitdir:` (globs; `**/` auto-prepended; trailing `/` adds `**`; symlink and realpath forms both match), `gitdir/i:`, `onbranch:`, `hasconfig:remote.*.url`.
- gitdir match to a store-target include → refuse, zero store access (required).
- non-matching gitdir to a store-target include → pin one of: (a) refuse regardless of condition, or (b) PASS with zero access. Recommended (a): deterministic, does not require the tool to re-implement glob matching. Decision D4.
- symlinked gitdir: fixture must include the symlink form, since git matches both forms.

**F12. Relative and tilde paths.** Relative include paths resolve from the including file's directory (git-config Includes). A local `include.path = ../../../../<store>` relative to `<repo>/.git/` must refuse. `./extra.cfg` inside `.git` → PASS. `~/`-prefixed paths expand from HOME; the fixture HOME is synthetic (`run_tool` env, r14 fixture ~line 28). `~/.omp/agent/...` refuses; `~/outside.cfg` outside the store passes with literal row. `~user/` behaviour is not documented in the sections read; do not pin it without a source check.

**F13. worktreeConfig.** `extensions.worktreeConfig = true` makes git read `config.worktree` in the admin dir, which the guard never reads. Required: `true` with a harmful `config.worktree` → refuse. `false`/empty with a harmful `config.worktree` present → git ignores the file. Expected PASS with zero access to `config.worktree`; pin as D7 since it relies on git's extension gating rather than the guard.

**F14. Neutralized keys: verify both the override and the effect.**
- `core.fsmonitor = true` → override `false` (`:710`); oracle asserts no `fsmonitor--daemon` socket or pidfile under the repo's gitdir.
- `core.hooksPath` pointing into the store or to `~/` → census never reads it; expect PASS with zero store access (strace).
- `core.attributesFile` with an assignment: override `/dev/null` (`:712`). In-tree `.gitattributes` assigning a non-empty filter is **not** neutralized. Harm case: marker absent via refusal, not PASS-with-marker.

**F15. Promisor / partial clone.** `remote.origin.promisor = false` → PASS with literal `verdict_flags=clean` (requires `refs/remotes/origin/master`, which `init_repo` creates at line ~170). `promisor = true` → refuse. `extensions.partialClone` present → refuse (matches current list).

**F16. alternateRefsCommand.** None of the census git calls (`:688-702`) advertises alternate refs. Pin: non-empty value → refuse (conservative). Empty value expected outcome must be pinned (D6); do not infer it from tool output.

**F17. Gate reference constants.** The r14 gate knows only `BASELINE_SHA`; anything else prints `TOOL-KIND other` (`:703-705`). Round 15 must add a second constant for `552cae4` (`fcff8b…`). Otherwise the gate cannot tell a repaired tool from the over-refusing r14 tool, and the baseline-red check (`:711-713`) does not fire on it.

**F18. Canaries and trace coverage.** Canary strings must be placed in every protected target a case can reach: store `config.yml`, store-target include file, store-target `config.worktree`, store-target symlink. Existing trace checks (`trace_access`, `follow_open_symlinks`) already cover opens below the store; extend the case list, not the checker.

## Oracle table (expected values; literal, not derived from tool output)

Format: family / variant → expected exit · finding or row · store access · marker.

| family | safe variant → expected | unsafe variant → expected |
|---|---|---|
| hooksPath | `/tmp-hooks` with hook writing marker → 0, `clean`, marker absent | `~/` or store path → 0, `clean`, zero store access |
| excludesFile | file ignoring `local.log` with `local.log` present → 0, dirty=1 (D2) | — (already neutralized; no unsafe variant) |
| attributesFile | file assigning benign `text eol=lf` → 0, dirty=0 | file assigning `filter=probe` with marker clean → exit 2, marker absent |
| filter.clean | empty value, no attribute → 0, dirty=0 | non-empty clean + tree attribute + stat-dirty tracked file → exit 2, marker absent (D3) |
| include.path | benign `./extra.cfg` → 0, clean | store target → exit 2, `path-protected`, zero access |
| includeIf | matching gitdir, benign target → 0, clean | matching gitdir + store target → exit 2, zero access; non-matching store target → D4 |
| promisor | `false` / `=` empty / `off` → 0, clean | bare / `true` / `Yes` / `TRUE` → exit 2, `git-config-unsupported` |
| worktreeConfig | `false` with harmful `config.worktree` → 0, zero access | `true` → exit 2 |
| alternateRefsCommand | D6 | non-empty → exit 2 |
| partialClone | — | `extensions.partialClone` → exit 2 |
| fsmonitor | `true` → override, no daemon artifacts, clean | — |
| status.showUntrackedFiles | `normal`, one untracked → 0, dirty=1 | `no`, one untracked → exit 2 or dirty=1 via override (D8) |
| mixed fleet | benign children only → 0, all literal rows | any unsafe child → exit 2, stdout empty (D1) |

## Decisions required (for SoujiR15)

- D1 mixed fleet: whole-run refusal with empty stdout (recommended) vs per-row emission (new contract).
- D2 excludesFile expected dirty: 1 under override (recommended, conservative) vs refuse.
- D3 transforming clean filter with unmodified file: expected dirty 0 → refuse (recommended) vs accept neutralized dirty 1.
- D4 includeIf non-matching store target: refuse regardless (recommended) vs PASS with zero access.
- D5 duplicate single-valued harm keys: refuse-if-any-unsafe (recommended) vs last-value semantics.
- D6 alternateRefsCommand empty value: PASS vs refuse.
- D7 worktreeConfig=false with config.worktree present: PASS with zero access (git gating) vs refuse.
- D8 status.showUntrackedFiles=no: refuse vs explicit `-unormal`/`-uall` override; expected dirty must be pinned either way.
- D9 hooksPath into store: PASS zero access vs refuse (recommended: PASS, census never reads it).

## Unrun checks / residuals

- Nothing executed. All line numbers and hashes come from source and `git show`.
- Candidate false-clean vectors (`status.showUntrackedFiles`, `core.fileMode=false`, `core.sparseCheckout`) are source-inspected and unverified at runtime.
- Acceptance for the eventual fixture: the expected table above committed in-file before the tool edit; each refusal case paired with a benign twin; `a31642d` and `552cae4` both pinned and each case's expected red/green recorded on both.

## Boundary disclosure (SoujiR15 no-query reminder)

- Violation: an unfiltered `_glob` over the whole lane root (default path, pattern `**`, limit 200) recursed into `census/operator-sweep-20261019/` and listed its entry names: `stage-hold-delete.sh`, `kotodama-children-sizes.tsv`, `kagi-routing-children.txt`, `kagi-routing-paths.txt`, `lore-scratch-verdicts.tsv`, `second-check.py`, `.hold.json`, `quarantine-mtimes-t0.tsv`, `tmp-kept.tsv`, `tmp-removed.tsv`, and `results/kotodama-chunk-*.tsv|.err`. Names only.
- Also visible without contents: `ls -la` on the lane root (directory entry `census`) and `git status --short` (`?? census/operator-sweep-20261019/` name line).
- Contents of the operator sweep were NOT opened, read, copied, queried, staged, or modified. No finding in this report depends on it.
- Limitation: that glob was the only out-of-bounds call. No runtime probe was run. Every other read was an explicit known file or a `git show`/`git cat-file` object read.
