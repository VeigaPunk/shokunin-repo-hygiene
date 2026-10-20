# SimplifyConfig — round 15 w1 (design-only; source inspection, no edits, no runs)

Scope: Git config refusals and command overrides in `tools/souji-census.sh` (the round-14 C2 surface), judged on operability and calibration. Source inspected: `tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, `corpus/lessons/round-14-verifier-spotcheck.md`, `corpus/lessons/round-14.md`, `SKILL.md`. Read-only. Nothing executed. No tools installed or updated (Tooling: none; RULES.md not needed).

Status: design-only. Proposed edits are not applied. Operator/canonical scope decision needed for item C.

## 1. Axes

- operability (primary): repair value-blind refusal of benign local config; keep every verified namespace refusal.
- calibration (secondary): the admission evidence for the config change must contain paired red/green and namespace controls.

## 2. Findings (exact lines, committed source)

### A. Blanket, value-blind refusal of already-neutralized keys (the round-14 defect)

- `tools/souji-census.sh:493-507` `guard_git_config`: after `keys=${keys,,}` (503) it matches the whole key list by substring and calls `protected_fail "git-config-unsupported"` (506) on presence alone. Values are never read on this path.
- Line 505 refuses these keys regardless of value:
  - `*core.hookspath*`
  - `*core.attributesfile*`
  - `*core.excludesfile*`
- The same three keys are neutralized on the only path that reads excludes/attributes/hooks settings:
  - `count_dirty` at `tools/souji-census.sh:710-712` passes `-c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` to `git status`.
  - `-c` on the command line overrides local repo config and the git defaults, so these values cannot be honored on this path.
- Consequence (matches corpus/lessons/round-14-verifier-spotcheck.md:104-106): a harmless local `core.hooksPath=/dev/null` hits the refusal, `protected_fail` exits 2 (`:160-164`), and `emit_census` (`:973-995`) aborts before printing the header. One benign repo suppresses the whole fleet output. Status: source-established. Not run here.
- Refusal is not needed for safety on the keys themselves:
  - `core.hooksPath`: census invokes only status, `rev-list`, `for-each-ref`, `worktree list`, `rev-parse`, `symbolic-ref` (`:688, :694, :698, :702, :836, :859, :710`). None runs hooks. [INFERENCE from git behaviour: hook-running commands are commit/merge/checkout-class; the census does not invoke them.]
  - `core.excludesFile` / `core.attributesFile`: read only by status-class commands, which are overridden at `:711-712`.
  - [INFERENCE] Git's defaults `$XDG_CONFIG_HOME/git/ignore` and `.../git/attributes` are not disabled by `GIT_CONFIG_GLOBAL=/dev/null` (`:122`). The `-c` overrides at `:711-712` are therefore the only neutralizer for those default files, and they must stay on every status call.

### B. Keys that must keep refusal (not blanket; execution or unguarded read)

Keep the key-presence refusal for these, all in line 505 or 514:
- `*include.*|*includeif.*`: followed config reads (the census runs `git status` without `--no-includes`).
- `*filter.*.clean*|*filter.*.smudge*|*filter.*.process*`: status can run clean filters for attribute-matched files. This is the only guard for `.gitattributes` and `info/attributes` selecting a driver.
- `*core.alternaterefscommand*`: command execution.
- `*remote.*.promisor*|*extensions.partialclone*`: lazy fetch.
- `*extensions.worktreeconfig*`: `config.worktree` is not guarded.
- line 514 `"~"*` on `core.worktree`: keep as is.

### C. Protected-vs-unsupported conflation (operability; design-only, needs scope decision)

- `protected_fail` (`:160-164`) exits 2 for every refusal, including `git-config-unsupported` (`:506`, `:514`). Protected-namespace findings (`path-protected`) and merely unsupported local config share one fleet-wide abort.
- `emit_census` (`:979-990`) and `census_one` exit paths (`:580-581`, `:613`, `:628`, `:650`, `:665`) propagate it to the whole run.
- Round-14 routed defect (corpus/lessons/round-14-verifier-spotcheck.md:160): "a harmless local setting cannot suppress unaffected rows."
- Option C1 (preferred if the operator approves): keep `exit 2` for `git-config-unparsed`, `git-metadata-*`, `path-protected`. Emit unsupported-config as a per-row verdict flag `config-unsupported` (new subset entry in header comment `:47-56`) and skip only that row's measurements. Changes the verdict-flag vocabulary, so it needs canonical adjudication. Not no-trade by itself.
- Option C2: leave exit 2 and rely on A to remove benign refusals. Keeps the schema, but genuinely unsupported keys still abort the fleet. Acceptable only if the operator accepts that scope.

### D. Redundant command overrides (maintainability; safe to remove)

1. `tools/souji-census.sh:121` `export GIT_OPTIONAL_LOCKS=0` and `:710` `git --no-optional-locks` do the same thing. Keep one (keep the env export, drop the flag at `:710`).
2. `:122-123` set both `GIT_CONFIG_SYSTEM=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`. The second is redundant. Drop `GIT_CONFIG_NOSYSTEM=1`. (The fixture `tests/fixtures/r14-census-boundary.py:146` also sets both; harmless, leave or align in the same change.)
3. `:713-716` three operator-sweep exclusions:
   - `:(exclude,glob)census/operator-sweep-*`
   - `:(exclude,glob)census/operator-sweep-*/**`
   - `:(exclude,glob)**/census/operator-sweep-*`
   The first is a subset of the third on the directory name; the second supplies contents. [INFERENCE: the set overlaps, but it cannot be consolidated safely without a fixture; do not collapse by reasoning alone.] Keep all until a discriminating control exists.
4. `:710-712` `-c core.hooksPath=/dev/null` stays (it is now the sole neutralizer after A). Do not remove on the ground that status never runs hooks; the override also documents intent and survives future command additions.
5. Header `:84-91` and `SKILL.md:214-218`, `corpus/lessons/round-14.md:92-94`: the "refuse hooks/attributes/excludes" wording must be rewritten to match A/B after the change. Do not leave the old list.

### E. Calibration gaps (for the admission checker)

- `tests/fixtures/r14-census-boundary.py` has no benign local-config case. Grep for `hookspath|excludesfile|attributesfile|fsmonitor|filter\.` returns only env lines (`:66-69, :144-146, :370-372, :607-609`) and no repo config case. The round-14 "green-only" trend is therefore reproduced: a baseline-red→green pair exists only for protected-namespace cases.
- Required paired controls (add before any acceptance):
  - Benign green: local config `core.hooksPath=/dev/null`, `core.excludesFile=/dev/null`, `core.attributesFile=/dev/null` in one repo. Expected: row emitted, exit 0. Baseline tool: exit 2. This is the red/green pair.
  - Neutralization, content-discriminating: local `core.excludesFile` pointing at a file containing `*`. Expected: untracked files still counted (the override is honored). If the override were not honored, the count would be 0. Use the same shape for `core.attributesFile` with a non-filter pattern.
  - Hook canary: local `core.hooksPath` pointing at a script that writes a marker file. Expected: marker absent after census. Discriminates hook execution.
  - Mixed fleet: the benign-config repo plus an unaffected repo. Expected (under C1): both rows present. Under C2 expect exit 0 and both rows (because A removes the refusal).
  - Namespace controls: all 12 existing `r14-census-boundary.py` cases unchanged; `path-protected` still exit 2 for each.
  - Paired negative for the kept refusals: local `filter.x.clean` and local `include.path` must still exit 2 (`git-config-unsupported`). Without these, A could silently widen support.
- Admission rule the checker should enforce: reject any change whose evidence is green-only (no baseline red on the same fixture), reject removal of a refusal key without its own red/green control, reject any case set that lacks a namespace control.

## 3. Suggested edits (not applied)

1. `tools/souji-census.sh:505`: delete `*core.hookspath*|*core.attributesfile*|*core.excludesfile*` from the refusal pattern. Keep the rest.
2. `tools/souji-census.sh:710`: change to `git -C "$1" -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null status ...` (drop `--no-optional-locks`). Put the four overrides in one array (e.g., `STATUS_SAFE=(...)`) used only by `count_dirty`, so there is exactly one neutralization list.
3. `tools/souji-census.sh:123`: drop `GIT_CONFIG_NOSYSTEM=1`.
4. `tools/souji-census.sh:47-56, 84-91`, `SKILL.md:214-218`, `corpus/lessons/round-14.md:92-94`: rewrite the refusal list to the set in section 2B. Name the neutralized keys and where they are overridden.
5. If C1 is approved: split `protected_fail` from a row-level `config-unsupported` verdict in `guard_git_config` (`:506`, `:514`) and `census_one`; add the flag to the header list.
6. `tests/fixtures/r14-census-boundary.py`: add the controls in section 2E before any admission claim.

## 4. Preserved contract

- All namespace refusals in the 12-case fixture stay exit 2 (`path-protected`).
- `git-config-unsupported` stays for include/includeIf, filter drivers, alternateRefsCommand, promisor/partialClone, worktreeConfig, and `core.worktree="~"`.
- Output schema and exit codes unchanged under A and C2. Under C1, one new verdict flag; exit codes unchanged.

## 5. Tradeoffs

- Removing the `core.hooksPath` refusal widens support by reasoning about command set, not by test. The override plus the controls in 2E must carry that claim; without them the change is not admissible under the round-14 no-trade rule.
- C1 changes the stable verdict vocabulary and therefore needs canonical adjudication. C2 keeps the schema but leaves the whole-fleet abort for genuinely unsupported keys.
- `info/attributes` inside `.git` is not checked by the guard; its filter drivers are caught only by the `filter.*` refusal. Do not drop the `filter.*` refusal.

## 6. Unrun checks (main agent should run after all seats land)

- `shellcheck -S warning tools/souji-census.sh` (no edit here, but required after edits).
- `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (legacy 38 checks).
- `python3 tests/fixtures/r14-census-boundary.py --tool <baseline>` and `--tool <changed>`: expect baseline red on the new benign controls, changed green, namespace unchanged.
- Confirm the new exclusion-pattern consolidation (2D.3) with a discriminating fixture before removing any pattern.

No messages were sent beyond the findings summary below. No edits were made outside this report.

## 7. Boundary disclosure (no-query rule)

- Violated call: one `_glob` with pattern `souji-shokunin/**` (gitignore false, limit 200) walked the whole lane root recursively. Its output listed file names under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `.hold.json`, `results/*.tsv`). Names only; no operator-sweep file was opened, read, copied, edited, or queried for content.
- Also non-recursive: one `ls -la` of the lane root and of `.ufo/` and `.ufo/waves/round-15/w1` (names and metadata only). It did not descend into `census/`.
- Limitation: the recursive glob output is not a finding and was not used for any claim in sections 1-6. Every claim rests on explicit reads of `tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, `corpus/lessons/round-14*.md`, `SKILL.md`, and greps scoped to `tools/`, `tests/`, `census/round-14`, `census/round-15`, and named markdown files.
- No further calls touch `census/operator-sweep-*`. No runtime probes or tests were run.
