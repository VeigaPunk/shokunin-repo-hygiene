# ComparePreserve — souji round 15, wave w1

Seat: `SoujiR15.ComparePreserve` (reviewer). Axes: operability (primary, C1), calibration (C2).
Basis: SOURCE INSPECTION ONLY. Nothing executed, no tests, probes, builds or edits. No operator-sweep path, no credential path, no sibling file opened. Tooling installed or updated: none.
Source state: `tools/souji-census.sh` is still the round-14 bytes (1539 lines). The ConfigRepair change has not landed, so pre-repair findings are read from source and the post-repair acceptance is **design-only**.

## 1. Contract under review (old fixture)

The `--compare` contract is 0 / 3 / 2 (SKILL.md:131; tool header `tools/souji-census.sh:58-65`):

| Case | Required exit | Required stdout | Source |
|---|---|---|---|
| identical census vs baseline | 0 | exactly `DIFF_HEADER` (`repo\tfield\tbefore\tafter\tchange`) | `emit_compare` 1097, return 0 at 1141 |
| any changed/added/removed row | 3 | header + changed rows | return 3 at 1140 |
| malformed baseline / usage | 2 | empty | `load_census` 1030, 1039, 1043, 1047, 1051, 1055; `usage_err` 147 |

The "old fixture" that carries this contract is the embedded legacy selftest, `run_selftest` (`tools/souji-census.sh:1187-1497`):
- Fleet built at 1194-1303. **It writes no local `.git/config` in any repo.** I grepped the fleet section and the whole selftest: the only `config` hits are the protected-store canary at 1456 and comments.
- Baseline `out1`/`out2` generated at 1274-1278, byte-identical check 1280.
- Identical: 1383-1394 (`cmp_st=0` and `cmp_out == DIFF_HEADER`, with `2>&1` so any stderr fails it). Blank-after-header: 1396-1410.
- Changed: mutation at 1412-1422 (`cmp2_st=3`), row greps 1423-1430 (`dirty-shokunin` scratch_bytes and dirty).
- Malformed: 1432-1445. Four files (`bad`, `empty`, `blank-lead`, `blank-before-header`) assert only `rc == 2`.
- Protected compare alias: 1454-1480.

The round-14 fixture `tests/fixtures/r14-census-boundary.py` covers protected-path refusal (R14C2-01..12). Its only compare case is R14C2-05 (store-path alias, lines 569-576). Its only config injection is env-based (`GIT_CONFIG_KEY_0=core.worktree`, 607-609). `SAFE_FLEET` has no benign local config. The only `.git/config` it writes is inside the protected store (221-223).

Round-14 closure reported the legacy selftest as 38 checks, 0 failed (`corpus/lessons/round-14-verifier-spotcheck.md:98`). That is a recorded observation; I did not re-run it.

## 2. Pre-repair behavior (round-14 source, source-inspected)

**Finding O-1 (HIGH, operability): `--compare` inherits the census-wide abort, so 0 and 3 are both lost for any fleet containing one key-matched repo.**
- `emit_compare` calls `emit_census` (1091) before any output. `emit_census` calls `list_repos` (979), which calls `guard_git_surface` for every repo (931, 934, 964). That calls `guard_git_config` (613, 628, 650, 665; admin 581).
- `guard_git_config` refuses on a substring match of lowercased key names, value-blind (`tools/souji-census.sh:504-507`). The refused keys include `*include.*`, `*filter.*.clean*`, `*filter.*.smudge*`, `*filter.*.process*`, `*core.hookspath*`, `*core.attributesfile*`, `*core.excludesfile*`, `*remote.*.promisor*`, `*extensions.worktreeconfig*` and others.
- Refusal calls `protected_fail` (160-163), which exits 2. The header is printed only at 991 (census) and 1097 (compare), so **stdout is empty**.
- Consequence: an identical fleet that contains one benign `core.hooksPath=/dev/null` repo returns rc 2 instead of 0. A changed fleet returns rc 2 instead of 3. Unaffected peers are suppressed. This matches the round-14 disclosure (`round-14-verifier-spotcheck.md:104-106`, 148, 160). The "[INFERENCE]" tag there applies to a deployment that was not probed; the source path itself is directly established.

**Finding O-2 (MEDIUM, operability): the refusal is not needed for the keys the census already neutralizes.**
- The only `git status` call (710-712) forces `-c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null`. These are exactly three of the refused keys. A local value for those keys is therefore never consumed by the census status run.
- The other census git calls (`worktree list` 688 and 836, `for-each-ref` 694, `rev-list` 698 and 702, `rev-parse` 859) do not read excludes or attributes. [INFERENCE from git semantics; not executed.] Hooks are not run by these read-only commands. [INFERENCE.]
- Acceptance implication: a value-aware repair may accept these keys without proof-by-value, but only for call sites that already neutralize them. Do not generalize that to all keys.

**Finding O-3 (safety constraint, keep refused): executable or include-bearing keys must stay refused and be tested as negatives.**
- `filter.*.clean|smudge|process` can run commands during `git status` on attributed paths. [INFERENCE.] Keep refused unless a value-aware rule proves no execution.
- `include.*` / `includeif.*`: census reads config with `--no-includes` (500, 511), but later `git -C` calls without that flag would follow includes. Keep refused unless the include target is boundary-checked.
- `remote.*.promisor`, `extensions.worktreeConfig`: keep refused in this round (owned by PromisorSafe / WorktreeCfg seats).

## 3. Calibration findings (C2)

**Finding C-1 (HIGH, calibration): the 0/3 contract is green-only with respect to configured repos.** The legacy compare controls run on a fleet with no local config (1194-1303). They cannot detect the round-14 regression. This is the "green-only preservation evidence" class the C2 admission checker must reject. Paired benign-config red/green controls are required.

**Finding C-2 (MEDIUM, calibration): exit 2 has several causes, and the malformed-baseline controls accept any of them.** Lines 1432-1445 assert only `rc == 2`. A `protected_fail` from a config refusal (exit 2, 160-163) passes the same assertion. Malformed-baseline controls must assert the specific stderr message from `load_census` (1030, 1039, 1043, 1047, 1051, 1055) and must not match `path-protected`.

**Finding C-3 (MEDIUM, calibration): changed-control assertions are row-presence only.** Lines 1423-1430 match a single `dirty-shokunin` row. They do not assert that unaffected rows are absent or that no extra rows appear. A mixed-fleet suppression bug (or a repair that adds spurious rows) would pass. Assert the exact expected row set.

**Finding C-4 (safety, for the repair): a repair must never make an unevaluated repo look identical.** If the repair skips a benign repo instead of censusing it, both baseline and current omit it. Then compare returns identical 0 for a repo that was never evaluated. Rule: a benign-config repo must produce its real census row, and a protected or unsupported repo must produce rc 2.

## 4. Acceptance required after the config repair (design-only; L1 runs)

Retain all existing legacy assertions (1383-1445) byte-for-byte. Add the following paired controls. Red = pre-repair tool, green = post-repair tool.

| ID | Fleet | Action | Expected red (pre-repair) | Expected green (post-repair) |
|---|---|---|---|---|
| A1 | clean repo + `core.hooksPath=/dev/null` local config | `--compare` against baseline captured without the config | rc 2, empty stdout | rc 0, stdout == DIFF_HEADER, stderr empty |
| A2 | same, with `core.excludesFile=/dev/null` and `core.attributesFile=/dev/null` | same | rc 2 | rc 0, header only |
| A3 | benign-config repo | census TSV row with config vs. same repo without config | row absent (rc 2) | rows byte-identical (config is census-inert for these keys) |
| A4 | benign-config repo + one change (dirty file) | `--compare` against the no-config baseline | rc 2 | rc 3, exactly one `<repo>\tdirty\t…` row, no other rows |
| A5 | mixed fleet: benign-config repo B (unchanged) + clean repo C (changed) | `--compare` | rc 2 | rc 3, rows only for C; no row for B |
| A6 | negatives: `include.path` to a path outside the boundary; `filter.x.clean=<cmd>`; `remote.origin.promisor=true`; `extensions.worktreeConfig=true`; unparseable config | identical and changed scenarios | rc 2 | rc 2 both scenarios, empty stdout, stderr names `git-config-unsupported` or `git-config-unparsed`; never 0 or 3 |
| A7 | malformed baselines (existing four files) | assert specific `load_census` message | rc 2 (passes) | rc 2 with the exact message; a `path-protected` line fails the control |

Each green must be paired with its red (the same fixture file run against the pre-repair tool). A green without a red is not acceptance evidence.

## 5. Keep-moves and no-harm constraints

- Keep the `--no-includes` parse and the `git-config-unparsed` path.
- Keep the core.worktree boundary check (`guard_target core-worktree`, 520).
- Keep the `status` overrides at 710-712. Do not remove them to "simplify".
- No change to `DIFF_HEADER`, the 0/3/2 mapping, or the `ABSENT/PRESENT` rows.
- Do not turn refusal into silent omission (C-4).

## 6. Residual risk and verification gaps

- Not run: legacy selftest, r14 fixture, any compare red/green. L1 runs the final acceptance.
- Not verified: whether `git worktree list` or `rev-list` read include or attributes paths when config is present (O-2 is inference from git semantics).
- Not verified: whether `git status` executes a `filter.*.clean` on racy-clean entries in this census fleet (O-3 is inference).
- Stale reference: `.ufo/waves/round-15/w1` registry text (`registry-draft.md:173`) cites compare asserts 0/3/2 at lines 707-756. Current lines are 1383-1445. Doc-only, not a defect.

## Routed

- To SoujiR15: O-1, C-1, C-4 (material).
- To peer MixedFleet: paired mixed-fleet controls A5 and C-3.

## 7. Boundary disclosure

- Violation (one call, not repeated): first `_glob` over `souji-shokunin/**/*` with `gitignore: false`, `limit` 400, a recursive walk of the whole lane root. Its returned listing included names under `census/operator-sweep-20261019/` (names only, e.g. `stage-hold-delete.sh`, `.hold.json`, `kotodama-children-sizes.tsv`, `results/`). No file under that path was opened, read, copied, edited, or staged.
- Limitation: the names above were visible in tool output and are the only exposure. The findings in sections 1-6 do not depend on any operator-sweep content.
- All later reads and greps used explicit files or named tools/tests/corpus/census round directories (`census/round-13|14|15`, `.ufo/waves/round-14|15`).
- No runtime probes or tests were run.
