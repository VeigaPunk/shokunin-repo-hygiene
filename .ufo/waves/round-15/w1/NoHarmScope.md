# NoHarmScope — souji round 15, wave w1 (critic)

Seat `SoujiR15.NoHarmScope`. Axes: operability (C1), calibration (C2).
Basis: **source inspection only; design-only for the repair.** At review time `tools/souji-census.sh` was still the
cc21683 bytes (status showed only LOG/SCORECARD/SKILL/QUALITY edits plus untracked round-15 files). The
r15 config fixture/checker/runner were not present. No tests, builds or edits outside this file. `~/.omp/agent` and
auth files were not opened. Tool installs/updates: none.

**Boundary deviation (disclosed, not repeated).** Before the parent's no-query reminder I ran one lane-root recursive
search: `grep pattern='value-blind|rejected-harmed|harmed' path='souji-shokunin' gitignore=false`. That traversal could
query `census/operator-sweep-20261019/`. Its output listed no operator-sweep match and nothing from it was opened or
used, but the search itself breached the contract. I also ran `git -C souji-shokunin status --porcelain` (twice), which
names that untracked directory but does not read it. All other reads were explicit known files or scoped
round-14/15 paths. No runtime probe was run.

## 1. The exact r14 harm to repair (closure `corpus/lessons/round-14-verifier-spotcheck.md`)

- H1, value-blind refusal. `guard_git_config:493–506` refuses when a key is present, whatever its value. Example: `core.hooksPath=/dev/null`, the same value the tool forces itself at `710–712` (closure :104).
- H2, propagation. `protected_fail:160–164` exits 2 during `list_repos:964`, before the header at `emit_census:991`. One repo therefore suppresses every unaffected row (closure :104, :148).
- H3, reference domain. The comparison is against the support before r14 (`a31642d`: every immediate main repo, ordinary `git status`; closure :104). The closure's routing (:160) is: repair with value/effect awareness; add paired benign controls and a mixed-fleet control. If some benign configurations stay unsupported, that is a **scope change for the operator or canonical judge to adjudicate, "not a no-harm improvement"**.

Planned repair (ConfigRepair prompt in `w1-spec.json`): make every key treatment value/effect-aware, count the existing status neutralizations, and keep the namespace fixtures green. Below are the counterexamples where that plan, or peers' acceptance drafts, would still leave H1–H3 open while looking green.

## 2. Counterexamples

### N1 (HIGH, calibration + operability): the preservation oracle refers to itself; "already neutralized" is not "unchanged"

- **Counterexample.** A repo has a local `core.excludesFile=.localignore` that ignores an untracked `build/`.
  - `a31642d` honours it (baseline status at `a31642d:131` has no overrides), giving `dirty=0` and `clean`.
  - Current/repaired `count_dirty:710–711` forces `-c core.excludesFile=/dev/null`, giving `dirty=1` and `dirty`.
  - ComparePreserve A3 (with-config vs without-config, both on the r15 tool) is identical, so it passes while the row differs from the pre-r14 row. [INFERENCE: git excludes semantics; not executed.]
  - The same pattern applies to `core.attributesFile` (eol/text conversion on stat-dirty entries).
- **Same class, no repo key needed.** r14 added `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` (`:122–123`). `a31642d` has neither (grep of `git show a31642d:tools/souji-census.sh`). It also forces `excludesFile=/dev/null`, which drops the XDG default ignore file. Global `status.showUntrackedFiles`, global LFS filters and the user's ignore file therefore stop shaping `dirty` for any repo. git(1): with `GIT_CONFIG_GLOBAL` set, "neither `$HOME/.gitconfig` nor `$XDG_CONFIG_HOME/git/config` will be read".
- **Axes.** Operability, through the fidelity of the `dirty` field and flags. Calibration: the planned red/green uses cc21683 as red and the r15 tool as green, so it cannot see this.
- **Note.** A false-dirty result fails in the safe direction for a cleanup tool. That makes it a judge-weighable tradeoff, not a hidden pass.
- **Smallest safe correction.**
  1. Benign-control oracles must be the **`a31642d` row bytes**: three-way `a31642d` = oracle, cc21683 = red, r15 = green, and green must equal the oracle.
  2. Do not override a path-valued key to `/dev/null`. Resolve the effective value (local, or the default under a synthetic HOME/XDG), `guard_target` it, then let git use it.
  3. If global config stays cleared, disclose it as a retained contraction. Do not report it as "preserved".

### N2 (HIGH, operability): leaving benign families fleet-fatal relabels the r14 harm as "boundary"

- **Counterexample.** ComparePreserve A6/O-3 keeps `remote.origin.promisor=true`, `extensions.worktreeConfig=true` and `filter.*.clean` at rc 2, "never 0 or 3". These are common benign configurations:
  - partial clones (`--filter=blob:none`);
  - sparse-checkout or per-worktree config, which sets `worktreeConfig=true`;
  - local `git lfs install --local` filters.
  `a31642d` emitted rows for all of them, so keeping rc 2 is exactly H1+H2 continuing.
- **Effect-aware treatment that is available from source and primary docs:**
  - **promisor / partialClone:** add `--no-lazy-fetch` to every census git call. git(1): "Do not fetch missing objects from the promisor remote on demand", equivalent to `GIT_NO_LAZY_FETCH=1`; this may be exported after the `GIT_*` clear at `:119`. Then allow the key. `promisor=false` has no effect and must simply pass.
  - **worktreeConfig=true:** today `guard_git_config` reads only `$dir/config`. Dropping the ban **without** also checking `config.worktree` (main gitdir and `worktrees/*/`) with the same predicate would open a namespace bypass (for example `core.worktree` or `include.path` set there). Extend the inspection; do not just delete the key. `false` passes.
  - **filters:** a command's safety cannot be decided statically. Either option is a residual contraction that must be disclosed and routed to operator/canonical adjudication (closure :160). Neither may abort the fleet.
    - (a) Empty per-driver overrides: `dirty` can diverge on stat-dirty filtered paths.
    - (b) Row-level degradation through the existing `status-unverifiable` flag (`census_one:889–891`).
  - **includes / includeIf:** checking a target is not refusing it. Resolve each `include.path` and `includeIf.*.path` relative to its own file, `guard_target` it before git reads it, and apply the same predicate recursively (depth-bounded). Refuse only targets that reach the namespace. Checking every conditional target regardless of its condition is conservative and costs no benign support.

### N3 (HIGH, operability; the namespace constraint is preserved): separate namespace refusal from unsupported-effect refusal

- `refusal_problems` (`r14-census-boundary.py:480–502`) requires rc 2, `path-protected` and **empty stdout** for every namespace case. R14C2-10/11 run a single `--include-root` repo.
- So "print unaffected rows and flag the bad repo" must **not** apply to namespace-reaching values; that would turn R14C2-10/11 red.
- **Correction.** Two outcomes:
  - A value whose effect reaches the protected namespace (include target, core.worktree, config.worktree target) gives `path-protected`, exit 2, empty stdout. This is the existing contract.
  - Any other unsupported effect is per-repo: the row is emitted with a flag (for example `status-unverifiable` or `error`), unaffected rows are byte-identical, exit 0.
- **Same H2 class in neighbouring guards, also mixed-fleet harm against `a31642d`:**
  - `git-config-unparsed` (`:500–501`). In baseline, git failing on a bad config gave an `error` row through the rev-parse check (`a31642d:253`; current `:859–861`). It now aborts the fleet.
  - A symlinked `config` (`:496–497`) aborts even when the target is safe.
  - Correction: unparsed → `error` row. A symlink → `guard_target`, then allow if it is outside the namespace.

### N4 (MEDIUM, operability): the matcher fires falsely across lines, independent of value handling

- `keys=${keys,,}` is a single newline-joined string, and bash `case` `*` also matches newlines.
  - `*filter.*.clean*` matches `filter.lfs.required` (no command) followed by any later key containing `.clean` (for example `branch.clean-up.remote`).
  - `*filter.*.process*` matches a later `branch.processing.merge`.
  - `*include.*` matches `remote.include.url` and `branch.fix/include.h.remote`.
  [INFERENCE: bash pattern semantics; not executed.]
- A value-aware repair that keeps this glob shape keeps the false refusals.
- **Correction.** Parse per line with `--name-only --null` (or a per-line loop). Match exact `section[.subsection].variable` anchors and look up values per key.

### N5 (MEDIUM, operability): tilde `core.worktree` is still value-blind

- `:513–514` refuses any value starting with `~`. A benign `~/src/x` outside the store is refused.
- **Correction.** Expand against the HOME set already built by `build_protected_roots`, then `guard_target`.

### N6 (HIGH, calibration): "retain verified namespace gains" does not constrain the key refusals

- No R14C2 case exercises a config key:
  - cases `:544–626`;
  - the only `.git/config` written is inside the synthetic store (`:221–223`);
  - the only config injection is the env `GIT_CONFIG_KEY_0` (`:607`), handled by the `GIT_*` clear.
- So removing every key refusal cannot turn any of the 12 red. Every refusal that is **kept** is an *unverified* safety claim sitting on top of a *verified* benign harm.
- **Correction.** Each retained refusal family needs its own fixture case with an observed baseline-red store access, using the r14 pattern `:711–715` ("baseline red case has no observed store access" fails).
- **Required case-set membership for ConfigFixture/AdmissionChecker:** a benign control (oracle = `a31642d` row) and a namespace control for each of the families below:
  - `include`, `includeIf`
  - `filter` clean / smudge / process
  - `hooksPath` (incl. `.husky`-style relative and absolute non-store values)
  - `attributesFile`, `excludesFile`
  - `alternateRefsCommand`
  - `remote.*.promisor` true/false
  - `partialClone`
  - `worktreeConfig` true/false
  - tilde `core.worktree`
  - unparsed config
  - the N4 cross-line decoys
  - a mixed fleet, with the benign repo sorted first and last, and row content checked (not header-only).

### N7 (HIGH, calibration): the C1 wording and SCORECARD must not shrink scope silently

- `claims.json` C1 says "Repair value-blind config refusals preserving benign configurations and mixed fleets". It verifies only if **every** family in header `:85–88` plus N3–N5 matches the `a31642d` rows.
- If any family is still refused or degraded, there are two separate things to do:
  1. **C1 itself:** narrow it to the enumerated repaired families. It may still be admissible as an improvement over cc21683 that adds no new harm.
  2. **The residual:** record it in LOG/SCORECARD as **continuing r14 harm debt pending operator adjudication**. It must not be recorded as "unsupported scope" or as a boundary.
- The draft QUALITY Q22 phrase "harmless or already-neutralized value" should read "neutralized with row bytes unchanged from the pre-restriction baseline", because of N1.
- AdmissionChecker must reject a record whose expected case set omits any of these families, or whose benign-control oracle is not the pre-restriction row. A hooksPath-only paired record is a *weakened* record, not green evidence.

## 3. Defect vs judge-level tradeoff

- **Fixable defects:** N2 promisor/worktreeConfig/includes, N3, N4, N5, N6, N7, and the N1 oracle choice.
- **Tradeoffs the canonical judge must reject as no-harm unless the operator adjudicates them:**
  - N1 global-config clearing and path overrides, if kept;
  - N2 filter neutralization or degradation.

## 4. Unrun checks (L1)

- `git show a31642d:tools/souji-census.sh` vs installed: check rows for each benign control under the same synthetic HOME/XDG.
- The r15 config fixture against `a31642d`, cc21683 and the installed tool: the three-way equality from N1.
- The unchanged `tests/fixtures/r14-census-boundary.py --tool <installed>` gives 12/12, with R14C2-10/11 stdout still empty.
- `grep -n 'GIT_NO_LAZY_FETCH\|--no-lazy-fetch\|config.worktree'` in the installed census, if N2 is adopted.
- AdmissionChecker negative records: hooksPath-only, cc21683-oracle and missing-family records must each exit 1.

Sources opened: `tools/souji-census.sh` 59–173, 429–733, 734–1003 (cc21683); `git show a31642d:tools/souji-census.sh`
(grep); `tests/fixtures/r14-census-boundary.py` 45–58, 189–330, 470–546, 629–729; closure lesson; `census/round-15/claims.json`;
`w1-spec.json` prompts; `AXES.md:25–38`; working-tree diff of LOG/SCORECARD/SKILL/QUALITY; peers HooksNeutral.md,
ComparePreserve.md; https://git-scm.com/docs/git (`--no-lazy-fetch`, `GIT_NO_LAZY_FETCH`, `GIT_CONFIG_GLOBAL`).
