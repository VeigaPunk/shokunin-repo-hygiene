# MixedFleet — critic, round 15 w1

**Status: DESIGN-ONLY.** No round-15 change to `tools/souji-census.sh` exists yet (HEAD `cc21683`; only `.ufo/waves/round-15/` and `census/round-15/` are untracked). Every line number below refers to the current r14 source `tools/souji-census.sh` (`#EAEA`) unless prefixed `a31642d:` (pre-r14 baseline, read via `git show`). Nothing was executed: no tests, probes or fixtures. Tool installs/updates: none.

**Boundary deviations (disclosed after the parent's no-query reminder; not repeated):**
- `grep` pattern `CASE\\t|printf 'CASE` over the **whole lane root** `/home/vgpnk/Projects/shokunin/souji-shokunin`. This was recursive and gitignore-respecting. Its traversal scope included `census/`, which holds the operator sweep. No operator-sweep path appeared in the results, and no operator-sweep file was opened, copied or edited, but the search did query that tree.
- `read` of the lane-root directory. The listing showed the child directory names `census/operator-sweep-20261018/` and `operator-sweep-20261019/` (names only).
- `git status --short` in the lane root, piped through `grep -v '^?? census/operator-sweep'`. Git still enumerated untracked paths, including the operator sweep, before filtering.
- Small shell reads that were not tests of census behaviour: `git --version` (2.55.0), `git show a31642d:tools/souji-census.sh`, and `zcat` of the installed `git-config.1.gz` man page.

**Limitation:** no finding here depends on operator-sweep content. All cited evidence is from `tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, `LOG.md`, `SCORECARD.md`, `census/round-15/claims.json`, `corpus/lessons/round-14-verifier-spotcheck.md`, the baseline blob and the installed man page.

Axes: **operability** (benign configured repo + mixed fleet keep full row content) and **calibration** (acceptance must reject header-only, skipped-row and partial-output "success").

## Counterexamples

### CX1 — one benign repo suppresses every unaffected row, at any position (confirmed from source)
- `guard_git_config` 500–506 reads key **names only** and refuses on substring presence → `protected_fail` 160–163 → `exit 2`.
- `list_repos` 963–965 runs `guard_git_surface` in the **main shell during discovery**, before any `census_one`. `emit_census` 979–994 prints the header only after every row has been computed. So with the benign repo first, middle or last, the result is the same: rc 2, **empty stdout**, and zero rows for the N unaffected repos.
- Baseline `a31642d:343–353` printed the header first, then streamed one row per repo. It had no config predicate (`a31642d:131` plain `status`).
- Common real configs that trip the predicate: husky `core.hooksPath=.husky/_`, the verifier's `core.hooksPath=/dev/null`, `git clone --filter` (`remote.origin.promisor` + `extensions.partialclone`), `git sparse-checkout` (`extensions.worktreeConfig`), git-crypt/LFS local filters, and project `include.path`.

### CX2 — key-blind false refusals (worse than value-blind)
`keys` is the newline-joined list (500, 503), and the `case` glob `*` matches across newlines (504–505).
- A branch tracked under the name `include` writes `branch.include.remote`, which matches `*include.*`.
- `branch.filter.remote` followed by any later key whose name segment begins with `clean` (e.g. `branch.clean-up.merge`) matches `*filter.*.clean*` **across two different keys**.

These are benign repos refused for no config effect at all. [INFERENCE from bash pattern semantics; not executed]

### CX3 — unaffected rows change content even with no local config (r14 overrides, not refusals)
- Line 122 sets `GIT_CONFIG_GLOBAL=/dev/null` and line 123 sets `GIT_CONFIG_NOSYSTEM=1`. Lines 711–712 force `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` on status.
- Installed git-config(1) (git 2.55.0, `/usr/share/man/man1/git-config.1.gz` lines 3843–3851, 3866–3874) documents that these keys default to `$XDG_CONFIG_HOME/git/ignore` and `$XDG_CONFIG_HOME/git/attributes` (fallback `~/.config/git/…`).
- Baseline `a31642d:131` honoured those defaults, plus any global `status.showUntrackedFiles`.
- Effect: a repo with **no** local config, holding an untracked file covered only by the user's global ignore, goes `dirty 0→N` and `clean→dirty` against baseline.
- This touches every "unaffected" row in a mixed fleet. A refusal-only repair cannot fix it, and a row-equality acceptance against the baseline will be red.
- Two ways out:
  - Restore the effective default ignore/attributes path, guarded through `resolve_guarded`, without opening store paths.
  - Or declare an explicit scope change for operator adjudication. Either way it is **not** "no harm".

### CX4 — repair pitfalls that reintroduce suppression or fake success
| # | Pitfall | Lines | Outcome |
|---|---|---|---|
| a | Degrade or skip only in `list_repos`, while `guard_git_config` stays fatal | guard re-run in subshells at 847 (`census_one`) and 831 (`worktree_extra_flags`); 986 | rc 2 for the whole fleet. The fix must live inside `guard_git_config`/`guard_git_surface` so all three call sites agree |
| b | Silent `continue` instead of `REPOS+=` | 969 → 991 | single-repo fleet gives rc 0 **header-only**, identical to an empty root. Under compare: a `removed` row vs baseline (1116–1118, rc 3), or a false "no drift" header-only diff vs a same-tool baseline |
| c | New flag (e.g. `config-unsupported`) missing from the stable-order list | 909 | flag silently dropped. If counted in `has_problem` (901), `verdict_flags` comes out empty; if not counted, `clean` is asserted on an unverified repo (false provenance). Follow the `status-unverifiable` precedent at 889–891/901/909 |
| d | `census_one` returns a nonzero code other than 2 | 987–988 | whole-run exit 1 |
| e | Stream rows "to keep earlier rows" | 980–994 | a protected repo sorted last leaves rows on stdout before exit 2. This breaks the r14 contract `refusal_problems` (r14 fixture 490–491: stdout must be empty). Keep buffered emission; namespace refusals stay whole-run |
| f | First/last fixture names that collate differently by locale | discovery uses glob order (939), output uses `LC_ALL=C` sort (970) | "first/last" means different things in discovery and output. Use lowercase ASCII names `a0-…`/`z9-…` |

## Required acceptance (for ConfigFixture / L1)

**Fleet:** at least 3 unaffected repos built with r14 `init_repo` (`tests/fixtures/r14-census-boundary.py:162–170`), giving distinct row content: one clean, one dirty, one unpushed. Add one benign repo **B**.

**Placements:** run three times, with B as `a0-benign` (first), middle, and `z9-benign` (last).

**Benign variants of B:**
- `core.hooksPath=/dev/null`
- `core.hooksPath=.husky/_`
- tracked branch named `include` (CX2 control)

**Oracle for each run** (stricter than `positive_problems` 505–541, which checks only one named row and tolerates missing or extra rows):
1. rc 0. Stderr contains no `git-config-unsupported` and no `path-protected`.
2. Line 1 is `HEADER`. Stdout has exactly `1 + N + 1` lines. The repo-column **set equals** the expected set, in C order, with B at the expected index (first or last). A header-only or B-missing result is FAIL.
3. Every row is **byte-equal** to the row the baseline tool `a31642d` produces on the identical fleet. Paired controls:
   - baseline: green;
   - r14 tool `cc21683`: red (rc 2, empty stdout);
   - r15: green.
4. B's row specifically has 7 columns: `worktrees=1`, `unpushed=0`, `dirty=0`, `verdict_flags=clean`.

**Namespace pair (retain r14 gains):** same fleet plus repo **P**, first and last. P has a config value that resolves into the synthetic store (e.g. `core.hooksPath=<STORE>/agent/hooks` or `include.path=<AGENT>/config.yml`). Expect:
- rc 2, empty stdout, `path-protected`, no canary, no spy/strace store access (reuse `refusal_problems`);
- `R14C2-01..12` still 12/12 PASS with the exact id-set.

**Compare (agrees with ComparePreserve A5):** take a baseline TSV from `a31642d` on the B-fleet.
- The r15 compare must give rc 0 with stdout == `DIFF_HEADER` only. This is valid **only when paired** with the census row checks above.
- Then add one untracked file to unaffected repo C. Expect rc 3, with diff lines **only** for C (`dirty 0 1 +1` and `verdict_flags clean→dirty`) and none for B.
- If B is skipped in both the baseline and the post-repair run, compare stays silent. So the post-repair census must separately assert that B's row exists with real values (ComparePreserve C-4).
- For the unchanged case, also check that the post-repair census's full row set equals the baseline/no-config census row set, not just rc and `DIFF_HEADER`.

**Global-ignore control (CX3):** use a synthetic `HOME`/`XDG_CONFIG_HOME` whose `git/ignore` covers an untracked file in one *unconfigured* repo.
- Baseline row: `dirty=0`, `clean`.
- If r15 differs, that is a contraction to repair or disclose. It cannot be admitted as no-harm.

## Smallest safe correction
1. Parse per key (`git config --file "$cfg" --no-includes --list -z`, or `--name-only -z`) and match an anchored `section[.subsection].name`. Do not glob over the joined list.
2. **Effect-neutral keys.** `core.hooksPath`: no census git command runs hooks, and status forces `/dev/null`. Resolve each value with `resolve_guarded` (never open it). A protected value gets whole-run `exit 2`; anything else is admitted with the row unchanged.
3. **Effectful, non-namespace keys** (filters, promisor/partialClone, non-protected includes, worktreeConfig, if still unsupported): emit a per-row flag that is in `has_problem` and in the order list. Never whole-run abort.
   - This keeps every unaffected row.
   - The degraded repo itself is still a contraction versus baseline and must be disclosed as scope, not counted as no-harm.
4. Keep buffered emission and whole-run refusal for namespace hits. Update the header contract comments 84–91 and 102–103 to match.

## Unrun checks
All of the above. Source inspection and the installed man page only. L1 should run:
- the mixed-fleet first/middle/last matrix;
- the namespace pair;
- `python3 tests/fixtures/r14-census-boundary.py` (12/12);
- `tools/souji-census.sh --selftest`, with its row count raised to include B (do not weaken `== 4` at 1297).
