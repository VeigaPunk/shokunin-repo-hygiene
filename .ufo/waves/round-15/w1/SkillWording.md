# Round 15 w1 — SkillWording (scribe, report only)

Axes: operability (primary), calibration. Baseline: HEAD `cc21683` (claims baseline `cc2168325768d5356a82c039dcdf787377c55784`). Scope: source inspection of committed bytes and the existing round-13/14 records. No tests, probes, gates, builds, or edits. Round-15 repairs are not landed yet (`git status`: only untracked `.ufo/waves/round-15/`, `census/round-15/claims.json`, `census/operator-sweep-20261019/`), so the post-repair wording in section 3 is **design-only**. `census/operator-sweep-20261019/` was not opened. A repo-wide grep may have walked it; no hits from it appeared in the output. Tool installs/updates: none.

## 1. Findings

**F1 — operability, high. SKILL config paragraph says "may refuse"; the refusal is deterministic and value-blind.**
`SKILL.md:214-218` says repositories with these settings "may refuse as unsupported." The code refuses on key name alone:
- `tools/souji-census.sh:493-506`: `guard_git_config` reads `git config --file "$cfg" --no-includes --name-only --list`, lowercases the names, and substring-matches them. Any match calls `protected_fail "git-config-unsupported"`. No value is read on this path.
- `tools/souji-census.sh:160-164`: `protected_fail` prints `path-protected: git-config-unsupported (...)` and exits 2. The census aborts with no TSV, so one benign repo suppresses every row.
- `tools/souji-census.sh:710-712`: the tool's own status call already forces `core.hooksPath=/dev/null`, so a benign `core.hooksPath=/dev/null` in a repo's own config is refused although the tool itself neutralises that setting.
- `corpus/lessons/round-14-verifier-spotcheck.md:104-106` records the same inference (`[INFERENCE]`, not an executed fixture). The static code path matches it.

**F2 — operability. The SKILL key list is a paraphrase and omits the exact substring semantics.**
`tools/souji-census.sh:505` matches `*include.*`, `*includeif.*`, `*filter.*.clean*`, `*filter.*.smudge*`, `*filter.*.process*`, `*core.hookspath*`, `*core.attributesfile*`, `*core.excludesfile*`, `*core.alternaterefscommand*`, `*remote.*.promisor*`, `*extensions.partialclone*`, `*extensions.worktreeconfig*`. Lines 513-515 also refuse `core.worktree` values beginning with `~`. SKILL names none of the `core.worktree` refusal and does not say matching is by substring over key names.

**F3 — operability/calibration. "Measured controls" cover no config-bearing repository.**
`SKILL.md:216-218` cites "measured ordinary, linked-worktree and comparison controls." `tests/fixtures/r14-census-boundary.py` (HEAD) has `EXPECTED_IDS` R14C2-01..12 only; its only repo config is `[core] repositoryformatversion = 0 / bare = true` (fixture lines ~221-223). Nothing under `tests/` or `census/round-14/` mentions `git-config-unsupported` or `hookspath`. No benign-config or mixed-fleet control exists. The wording must not imply preservation of config-bearing repositories.

**F4 — calibration. The retention consumer wording overstates reach.**
`SKILL.md:200-204` says "The actual consumer is `census/round-13/run-verification.py`." Verified facts:
- `census/round-13/run-verification.py:175-197` (`attempt_reuse`) is reached only under `--retry-failed` (`:201`, `:364-368`), only for names in the prior run that matched (`RETRY_NAMES = failed`, `:388`), and never for `REUSE_EXEMPT = {sources-contract, shellcheck-warning, quarantine-red-before}` (`:51`, `:177-178`).
- The only exercised evidence is `census/round-14/cache-demonstration.py`: `attempt_reuse` is called directly on isolated synthetic in-memory records (`:587-644`), with `migrated_module.ROOT` rebound to a `/var/tmp` fixture (`:382-385`, recorded `root_rebound_to_fixture` at `:651`).
- The full `run()` dispatch with `--retry-failed` end-to-end was not run (`corpus/lessons/round-14-verifier-spotcheck.md:89`, routed item 3 at `:162`).
- Checked the committed records: `census/round-13/verification.json` (14 results), `census/round-14/verification.json` (6), and `census/round-14/verification-attempt-1.json` (12) have no `dependencies` and no `dependencies_stable` key on any result. Every one is refused as legacy and re-executed. **Zero production retentions are demonstrated.**

**F5 — calibration. SKILL's record contract omits consumer-level preconditions.**
`SKILL.md:184-191` describes only the gate. `attempt_reuse` (`run-verification.py:179-190`) additionally requires `matched is True`, a 40-lowercase-hex `measured_commit`, `dependencies_stable is True`, and a non-empty `dependencies` dict before the gate runs. `dependencies_stable` is not checked by the gate (`tools/souji-evidence-cache.py:1-17`, `:39-43`). A caller that only follows the SKILL text would miss this.

**F6 — calibration/consistency. Two "consumer" claims conflict.**
`census/round-14/cache-demonstration.py:1-6` calls itself "the supported current-round evidence-collection consumer" and says it "neither imports nor wraps" the historical runner. SKILL `:200` names `run-verification.py` as the actual consumer. The lesson (`:162`) calls the demonstrated item a synthetic decision check. The docstring should not claim consumer status; this is a code-file correction, routed to the owner, not edited here.

**F7 — calibration (routed, not my file). Scorecard/LOG overstate operability.**
`SCORECARD.md:15` says "normal controls preserved" for operability. The round-14 lesson rejected that net no-harm claim (`round-14-verifier-spotcheck.md:104-106`, `:148`, `:160`). `SCORECARD.md:15` and the LOG round-14 entry need correction through ScorecardDraft/LOG owners.

**F8 — minor operability. Gate-registry exit-2 row omits the grep token.**
`SKILL.md:131` says exit 2 covers "protected or unsupported Git path (`path-protected`)." Stderr is `path-protected: git-config-unsupported (...)`. Naming the reason token lets operators grep and distinguish namespace refusals from config refusals.

**Out-of-scope note.** `tools/souji-census.impl-36.sh` is tracked and is not mentioned in the SKILL gate registry. Ownership unclear; not analysed.

## 2. Corrected current wording (adopt now; valid at HEAD `cc21683`)

Replace `SKILL.md:200-204` (consumer sentences) with:

> The retention decision is `attempt_reuse(name, prior)` in `census/round-13/run-verification.py`. It is reached only with `--retry-failed` and a readable prior file, and only for previously matched names outside `REUSE_EXEMPT` (`sources-contract`, `shellcheck-warning`, `quarantine-red-before`, always re-executed). It returns the prior result only when `matched` is true, `measured_commit` is 40 lowercase hex, `dependencies_stable` is true, `dependencies` is a non-empty object, and the gate exits 0; every other case re-executes. Its only exercised evidence is `census/round-14/cache-demonstration.py`, which calls the function directly on isolated synthetic in-memory records under `/var/tmp` with the module's `ROOT` rebound to that fixture. The full `run()` dispatch and any retention on real evidence have not been run: every recorded result in `census/round-13/verification.json` and `census/round-14/verification*.json` lacks `dependencies`, so each is refused as legacy and re-executed. No production retention is demonstrated. Historical JSON is never rewritten; the entry requires explicit `--round N --output census/round-N/<new>.json`, and a default invocation refuses with exit 2.

Add to the record sentence at `SKILL.md:186-191`: "The consumer also requires `dependencies_stable: true`, which the gate does not check."

Replace `SKILL.md:214-218` (config paragraph) with:

> `tools/souji-census.sh` reads only the repository-local `config` (`--no-includes`; global/system config and inherited `GIT_*` are cleared). Refusal is by key name, not value: `guard_git_config` refuses the whole census with `path-protected: git-config-unsupported` and exit 2 when any key contains `include.`/`includeif.`, `filter.*.clean|smudge|process`, `core.hookspath`, `core.attributesfile`, `core.excludesfile`, `core.alternaterefscommand`, `remote.*.promisor`, `extensions.partialclone`, or `extensions.worktreeconfig`, or when `core.worktree` begins with `~`. A harmless value such as `core.hooksPath=/dev/null` is refused today. The measured controls (ordinary, linked-worktree, comparison) contain none of these keys; no benign-config or mixed-fleet preservation control exists. This is not support for config-bearing repositories.

Replace `SKILL.md:131` exit-2 cell with: `2 could-not-evaluate usage/malformed baseline; protected-path refusal (stderr \`path-protected: <reason>\`, incl. \`git-config-unsupported\`)`.

## 3. Post-repair wording — DESIGN-ONLY, do not adopt until observed

Round-15 C1 (ConfigRepair) must first land committed evidence. Only then replace the config refusal sentence in section 2 with the value-aware rule the repair actually commits. Do not invent that rule in SKILL before it exists. Keys the repair does not explicitly classify remain refused, and the sentence must say so.

**Exact acceptance needed before adopting section 3:**
1. Paired baseline-red / changed-green controls on a committed fixture: a repo with benign `core.hooksPath=/dev/null` (and any other repair-named benign value) exits 0 and emits its TSV row; the baseline exits 2.
2. A mixed-fleet fixture: one benign-config repo and one refused-key repo. The stated exit code and output for both must match the committed rule, and the benign row must not be suppressed.
3. Each refused key still exits 2 with `path-protected: git-config-unsupported`.
4. R14C2-01..12 keep their IDs and pass; legacy census selftest stays 38/38.
5. The SKILL text names the exact classified keys and values, with the rule's evidence pointer.

For retention wording to move from "synthetic-only" to a real-evidence claim, the required observation is: a real `run-verification.py --retry-failed --round N --output census/round-N/<new>.json` run over a prior record that has `dependencies` and `dependencies_stable: true`, with a committed positive retention and a committed refusal for a dependency change. Until then, keep section 2 wording.

## 4. Verification

Checks not run (none assigned): selftests, fixtures, the census tool, the gate, and the consumer. The findings above are static inspection of committed source, the lesson, and JSON records. `[INFERENCE]` is limited to the operator-visible impact of F1 (whole-census abort on a benign `core.hooksPath`), which the static code path supports but no fixture executed.

Routed: F6 to the cache-demonstration owner; F7 to ScorecardDraft/LOG; the F1 and F3 config claims to ConfigRepair and ConfigFixture.

## 5. Process evidence: search and listing paths (amendment)

Exact calls I issued that touched the lane tree, with scope. Nothing was re-run for this amendment.

- `_grep` pattern `attempt_reuse` (first grep call): path = whole lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, gitignore default. **Whole-lane walk, not explicit files.** Output hit the 200-result limit, so operator-sweep matches in the truncated tail cannot be ruled out; none appeared in the visible output, and no operator-sweep file was opened.
- `_grep` pattern `guard_git_config|git-config-unsupported|core\.hooksPath|worktreeConfig|alternateRefsCommand`: path = explicit directories `tools;tests;census/round-14`. Explicit scope; `census/operator-sweep-20261019` was not included.
- `_grep` pattern `attempt_reuse|retain|synthetic|config|git-config` (second search): path = explicit files `SCORECARD.md;LOG.md;PROVINCE.md;corpus/lessons/round-14.md`. Explicit scope.
- `_glob` (`Finding SKILL files in lane`) with path = whole lane root: **whole-lane listing**. Its output displayed file and directory NAMES under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `.hold.json`, `quarantine-mtimes-t0.tsv`, `tmp-kept.tsv`, `tmp-removed.tsv`) and the `results/` names. This is a name-level exposure I did not intend. No file contents were read, opened, copied, or modified, and no sweep name was used in any finding.
- `_bash` calls: `ls -la` of the lane root (name and mtime for `census/` and root entries, including the `census/operator-sweep-20261019` name); `git status --short` (reports only the untracked directory name); `ls -la .ufo/waves/round-15/w1/` and `ls census/round-15`. No sweep content was read.
- `_read` calls: `SKILL.md`, `census/round-13/run-verification.py` ranges, `corpus/lessons/round-14-verifier-spotcheck.md`, `tools/souji-census.sh` ranges, `census/round-14/*` ranges, `tools/souji-evidence-cache.py:1-80`, `census/round-14/cache-demonstration.py:1-40`, `tests` fixture ranges via `git show HEAD:`. None target `census/operator-sweep-20261019/`.

Limitation: the whole-lane `_grep` and `_glob` do not exclude untracked directories, so operator-sweep names were enumerated. This is disclosed here rather than treated as a finding. Future seats should scope searches to explicit paths.
