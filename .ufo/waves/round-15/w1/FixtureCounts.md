# FixtureCounts — souji r15 w1 (C1 operability, C2 calibration)

Seat: SoujiR15.FixtureCounts (reviewer, leaf). Axes: operability, calibration.
Mode: source inspection only. No fixture, tool, census, strace, or Git command was executed. No file outside this report was written. No real credential or auth path was opened.

## Evidence status

- Round-15 fixture `tests/fixtures/r15-census-config.py` is **absent** (glob of `tests/fixtures/r15*` empty). Same for `tools/souji-preservation-evidence.py`, `tests/fixtures/r15-preservation-evidence.py`, and `census/round-15/run-verification.py`/`count-claims.py`. Only `census/round-15/{before.json,claims.json,lesson-draft.md}` exist.
- Everything below marked **design-only** is a requirement derived from contract text (`.ufo/waves/round-15/w1-spec.json:10,18,388`) and r14 source. Nothing is verified against r15 bytes.
- `tools/souji-census.sh` is the in-flight working tree (ConfigRepair owns it). Line numbers below are from that read.

## 1. Verified r14 facts (present in source)

1. **r14 namespace fixture cardinality is consistent at 12.** `tests/fixtures/r14-census-boundary.py`: `EXPECTED_IDS` = `R14C2-01`..`R14C2-12` (lines 45-58); `CASES` dict 12 entries (629-642); 12 `case_NN` functions.
2. **Partial runs can PASS.** `--case` (line 665) selects a subset; the exact id-set check is only `if not args.case and tuple(ran) != EXPECTED_IDS` (722-727). A `--case` run with `failed=0` is green for any subset. The r15 gate must reject `--case`.
3. **The r14 fixture has zero config-family cases.** Grep of the fixture for `hooksPath|include|filter.|promisor|worktreeConfig|excludesFile|attributesFile|fsmonitor|alternateRefs|partialClone|benign|mixed` returns no matches. No committed fixture has a benign local-config control or a config-bearing mixed fleet. This matches round-14 closure text (`corpus/lessons/round-14-verifier-spotcheck.md:105-106`).
4. **Refused families are exactly 12 key patterns** (`tools/souji-census.sh:504-506`, lowercased keys at 503): `include.*`, `includeif.*`, `filter.*.clean`, `filter.*.smudge`, `filter.*.process`, `core.hookspath`, `core.attributesfile`, `core.excludesfile`, `core.alternaterefscommand`, `remote.*.promisor`, `extensions.partialclone`, `extensions.worktreeconfig`. Value-blind: keys come from `git config --name-only --list` (500); values are never read, so `extensions.worktreeConfig=false` and `remote.*.promisor=false` are refused.
5. **Non-refused but handled**: `core.worktree` is boundary-checked (511-521; only `~` is refused); `core.fsmonitor` is overridden with `-c core.fsmonitor=false` (710).
6. **One refused repo aborts the whole fleet.** `protected_fail` exits 2 (160-164). `list_repos` calls `guard_git_surface` per child before any row (954-967). `emit_census` prints the header only after the loop (991). A single refusal yields exit 2 and zero rows for every peer. This is the round-14 harm mechanism (verifier-spotcheck 102-106).
7. **Only `status` carries the neutralizing overrides.** `git -C … worktree list` (688, 836), `for-each-ref` (694), `rev-list` (698, 702), and `rev-parse --is-inside-work-tree` (859) run without `-c` overrides and read local config, including includes. The include boundary therefore has to hold before every one of these reads, not just before status (710-712).
8. **Baseline gate is hard-wired to the legacy tool.** r14 `is_baseline = digest == BASELINE_SHA` (703) with `BASELINE_SHA` = a31642d (61). The access requirement exempts case IDs by literal (711-712). The round-14 harmful tool (installed digest `fcff8b057b3e…`, per `round-14.md` evidence) is not the legacy baseline, so the gate would classify it as `other` and silently skip the access check. Cloning this pattern would drop the r15 baseline oracle.

## 2. Proposed r15 fixed set (design-only; ConfigFixture must pin literal IDs)

Prefix `R15CFG-NN`, distinct from `R14C2-NN`. Minimum floor per family; the literal tuple is to be pinned by the fixture author and asserted by set equality with no `--case` escape.

| Family (source) | Min | Benign/safe expectation (repaired) | Unsafe expectation (repaired) |
|---|---|---|---|
| F01 `include.path` | 5 | safe relative in-repo include preserved; missing target preserved | absolute protected, `~` protected, cycle refused/bounded |
| F02 `includeIf.*` | 4 | non-matching `gitdir:`/`onbranch:` preserved | matching protected `gitdir:` refused with zero store access |
| F03 `filter.*.clean/smudge/process` | 4 | config-only filter with no `.gitattributes` reference preserved, never executed; empty value preserved | attribute-bound filter (`filter=<name>`) refused or neutralized; protected command refused, no exec |
| F04 `core.hooksPath` | 3 | `/dev/null`; in-repo hooks dir preserved, marker never created | protected path: zero access |
| F05 `core.attributesFile` | 3 | `/dev/null` preserved | protected path: zero access; in-tree eol attr fidelity pinned |
| F06 `core.excludesFile` | 3 | in-repo excludes honored, count pinned | protected path: zero access |
| F07 `core.alternateRefsCommand` | 2 | empty value preserved | non-empty refused, no exec |
| F08 `remote.*.promisor` | 4 | `false`/`no`/`off`/`0`/empty preserved | `true`/`yes`/`on`/`1`/bare key refused; invalid refused fail-closed |
| F09 `extensions.partialClone` | 2 | safe-only case preserved (decision pending, see D6) | present with promisor refused |
| F10 `extensions.worktreeConfig` | 3 | `false` preserved; `true` + in-repo `config.worktree` preserved | `true` + protected `config.worktree`: zero access |
| F11 `core.worktree` (path config) | 3 | in-repo relative preserved; linked worktree preserved | protected target and `~` refused, zero access |
| F12 `core.fsmonitor` (neutralized) | 2 | fsmonitor marker command never runs | protected fsmonitor path: zero access |
| F13 key/subsection case and false-positive shapes | 3 | `remote.Origin.promisor=false` preserved; cross-line `filter.x.required` + `diff.clean.driver` preserved (see §4) | value containing `remote.x.promisor=true` not parsed as a key |
| F14 mixed fleet | 4 | benign-config repo among normal repos, first and last ordering; unaffected row content asserted | unsafe repo among normal repos: policy per D1 |
| F15 global/system poisoning | 2 | poisoned `HOME/.gitconfig` and `GIT_CONFIG_GLOBAL` have no effect | same, with protected include: zero access |
| F16 dirty fidelity | 2 | untracked and modified counts equal legacy a31642d counts | — |

Floor total: **49** new IDs (`5+4+4+3+3+3+2+4+2+3+3+2+3+4+2+2`). Plus the unchanged `R14C2-01..12`, which must be run separately on the changed tool with 12/12 green as the namespace control.

Named safe families from the wave prompt are all covered: safe includes (F01/F02), mixed fleet (F14), false promisor/worktreeConfig (F08/F10), safe clean filters (F03), neutralized hooks/attrs/excludes/fsmonitor (F04/F05/F06/F12), path config (F11). **Gap:** `core.worktree` appears in ConfigRepair's "path config" but in none of the 12 refused families; it must be its own family (F11).

## 3. Blocking decisions (fixture expectations cannot be written until these are pinned)

- **D1 — mixed fleet with an unsafe repo.** Current behavior: exit 2, zero rows (§1.6). "Ensure unaffected mixed-fleet rows … retained" (ConfigFixture prompt) implies rows must print. Options: (a) rows for unaffected repos + stderr finding + exit 2 (recommended: partial output is not a success); (b) skip + exit 0 (rejected: silently suppresses refusal); (c) abort (current, enshrines harm). Operator/L1 must choose; fixture must assert row content for (a).
- **D2 — baseline identity.** `claims.json` baseline is commit `cc2168325…`. Not verified to contain the round-14 harmful tool (digest `fcff8b057b3e…`). RoundRunner must hash the extracted baseline and assert it equals `fcff8b057b3e…` (or the equivalent measured digest). Fixture must add a `TOOL-KIND baseline-r14` pin; do not reuse `BASELINE_SHA` a31642d.
- **D3 — evidence type per red.** Benign-config harm is contract-only (exit 2 `git-config-unsupported`, no protected access expected). The r14 rule "every baseline red needs `access:` evidence" (line 713-715) would mark these as wrong-reason reds. Each case needs an explicit expected-red reason: `contract` for benign harm, `access` for protected-path controls.
- **D4 — dirty fidelity under neutralization.** Status overrides `core.excludesFile` and `core.attributesFile` to `/dev/null` (711-712). Legacy a31642d did not override, so in-repo excludes/attributes that ignore or convert files change dirty counts. Restoring support while neutralizing silently changes counts (DirtyFidelity). F05/F06 must pin the expected count and label which side (legacy or neutral) it reflects.
- **D5 — hooks oracle.** `status` runs with `--no-optional-locks`, so no index write and likely no `post-index-change` hook [INFERENCE from git semantics, not verified]. A marker hook alone may never fire. The fixture oracle for F04 should be strace `execve`/`openat` under the hooks dir, which the r14 `%file,getdents64,execve` filter already covers.
- **D6 — F09 `extensions.partialClone` without promisor.** Source refuses on key presence (505). Whether `partialClone` alone is safe is undecided. Pin it, do not assume.

## 4. Source-level hazard (INFERENCE, not executed)

`keys` is newline-joined (500), lowercased (503), then matched with bash `case` globs (505). Bash `*` matches newlines. So `*filter.*.clean*` can match across lines: a config whose key list contains `filter.x.required` followed by `diff.clean.driver` would match (`filter.` … `.clean`) and be refused, though it has no filter command. Benign-case F13 should encode this shape. The fix (per-line match) belongs to CaseParsing/ConfigRepair; the fixture must catch it.

## 5. Acceptance the fixture must meet (exact)

- **A1** Literal tuple of `R15CFG-NN` IDs; `--list` prints exactly that tuple; the no-`--case` run asserts `ran == EXPECTED` and exits 1 on mismatch (r14 pattern, 722-727). `--case` must be rejected for the gate.
- **A2** One `CASE` line per ID with `PASS`/`FAIL`; each line includes exit code, finding ID, and row content for every expected row (repo path, worktrees, unpushed, dirty, verdict). Header-only success fails.
- **A3** Per-ID expectation table: baseline outcome, changed outcome, and red-reason kind (`contract`/`access`) per D3. Replace the literal `07/08` exemption (712) with this table.
- **A4** Baseline gate keyed on the r14 harm digest (D2), not a31642d.
- **A5** Forbidden-access evidence per case from strace (`-e trace=%file,getdents64,execve`) and spies on `find du git cat head tail readlink realpath stat`; `EACCES` on mode-000 store is the store oracle. Unsafe cases must show zero store access on the changed tool.
- **A6** Synthetic `HOME` with poisoned global config and `GIT_CONFIG_GLOBAL`; uid 0 refused (r14 fixture 678-679 pattern).
- **A7** Cleanup must not swallow `rmtree` errors (r14 audit M4) and row path matches use `os.path.realpath` (r14 audit M3).
- **A8** Record schema shared with AdmissionChecker: ID tuple, per-ID baseline/changed exit, stdout digest, tool digests (baseline and changed), fixture digest.

## 6. Checks for the main agent after all seats land (not run here)

1. `python3 tests/fixtures/r15-census-config.py --list | wc -l` equals the declared total (49+ floor) and equals the number of unique IDs.
2. `sha256sum` of the extracted baseline equals `fcff8b057b3e…` (D2).
3. Baseline run: each F01–F16 benign case FAILs with `git-config-unsupported` (contract); each unsafe case PASSes refusal with zero store access.
4. Changed run: all `R15CFG` PASS with row content; `R14C2-01..12` 12/12 PASS; legacy `tools/souji-census.sh --selftest` unchanged.
5. Negative control: replace the fixture's expected IDs with a 48-ID tuple; the gate must fail.

## Tooling record

No tools installed or upgraded. No pacman transactions. No `~/.omp` or credential file was read.

## Messages sent

- To `SoujiR15` (lane coordinator): D1–D5 and the 49-ID floor, short form.

## Boundary disclosure (no-query rule)

- Violated, early in this seat: (1) `_glob` over `/home/vgpnk/Projects/shokunin/souji-shokunin/**/*` (whole-lane recursive glob); its result listed filenames under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `.hold.json`, `quarantine-mtimes-t0.tsv`, `results/`). (2) `_grep` with `path: /home/vgpnk/Projects/shokunin/souji-shokunin` (whole-lane recursive content search); it traversed the operator sweep directory with no path filter. (3) `_read` of the lane root directory listing, which also surfaced operator-sweep child names.
- Limitation: those calls returned filenames and matching content lines from other paths. I did not open, read, copy, query, or modify any operator-sweep file. No finding in this report depends on operator-sweep content. All cited evidence comes from explicit source paths (`tools/`, `tests/fixtures/r14-*`, `corpus/lessons/`, `census/round-14/*`, `.ufo/waves/round-15/`).
- No runtime probes, tests, or shell empirical probes were run by this seat.
