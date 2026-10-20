# TrendMap — round 15, wave 1 (connector, source inspection only)

Scope: C1 operability repair of round-14 value-blind Git-config refusals; C2 calibration input from the same defect. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Baseline: cc2168325768d5356a82c039dcdf787377c55784 (census/round-15/claims.json).

Status: **design-only for C1**. The repair is not in the source read here: `tools/souji-census.sh:504–507` still holds the round-14 key-only `case`. Acceptance below is the exact evidence required; nothing was run.

Tool installs/updates: none. No runtime probes, tests, builds or operator-sweep access. No `~/.omp/agent` or credential file opened.

## Boundary disclosure (no-query reminder)

One out-of-bounds call occurred in this seat, before the reminder arrived. Exact call: `glob` with path `/home/vgpnk/Projects/shokunin/souji-shokunin`, pattern-free lane-root listing, `limit` 200, intent "Locating souji lane source files". It was a recursive listing of the whole lane root, which returned names under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `.hold.json`, `tmp-kept.tsv`, `tmp-removed.tsv`, `second-check.py`, `results/*.tsv`, `results/*.err`). Limitation: only file names and directory entries were returned; no file under the operator sweep was opened, read, copied, edited, moved, staged or deleted, and no content from it is used in this report. Every other read, grep or glob in this seat used an explicit known source, tool, test, census/round-14, corpus or `.ufo/waves/round-15` path. No runtime probes or tests were run. The statement in the Tool installs/updates line above is otherwise unchanged.

## Axes

- **Judged:** operability (C1), calibration (C2). Legacy scores 7/8/8 (calibration/operability/coverage); numeric delta stays 0.
- **Trend axes mapped:** expansion, quality, discernment (corpus lesson vocabulary).

## Trend map

| trend | current source state | verdict if the move lands with the acceptance below | why |
|---|---|---|---|
| operability | **harmed** (round-14 closure `corpus/lessons/round-14-verifier-spotcheck.md:104–106,148`) | improved, only with paired red→green on benign and mixed-fleet controls and 12/12 namespace retained | restores benign support; removes whole-fleet abort for harmless values |
| calibration | unchanged; r14 "improved" row in SCORECARD.md:15 overstates | improved only if a checker rejects green-only pairs | r14 12/12 namespace fixture alone passes green-only evidence |
| expansion | unchanged (admitted 5, HELD 1; source rows 40) | unchanged | restoring a supported class is preservation, not new knowledge; no source-row count may be cited |
| quality | unchanged | unchanged | no admitted knowledge touched; the new value table must replace the blanket rule, not sit beside it |
| discernment | unchanged | improved only if the outside disagreement becomes a committed negative control | Q22 (`corpus/QUALITY.md:56`) requires it |

## Source facts (exact lines, inspected)

1. **Key-only refusal.** `guard_git_config` (`tools/souji-census.sh:493–522`) reads key names only (`--name-only --list`, line 500), lowercases them (503), and refuses on pattern match with no value check (504–507). Any `core.hooksPath`, `core.attributesFile`, `core.excludesFile`, `remote.*.promisor`, `extensions.worktreeConfig` key is refused whatever its value.
2. **Whole-fleet abort.** `protected_fail` exits 2 (`160–164`). `guard_git_config` is called from `guard_git_surface` at 613, 628, 650, 665; `list_repos` (964) runs before `emit_census` prints the header (979, 991). One refused repo therefore yields exit 2 and no TSV. [source-derived; not probed]
3. **Already-neutralized values.** `count_dirty` forces `core.fsmonitor=false`, `core.hooksPath=/dev/null`, `core.excludesFile=/dev/null`, `core.attributesFile=/dev/null` on `git status` (`710–712`). Other census git verbs are `worktree list` (688, 836), `for-each-ref` (694), `rev-list` (698, 702), `rev-parse` (859). None runs hooks or reads excludes/attributes. [source inspection of the verb set; re-verify when verbs change]
4. **Value-aware precedent.** `tools/souji-repo-structure.sh:215–233` checks `remote.*.promisor` by value (`--type=bool --get-regexp`, `*" true"`). Reuse this pattern.
5. **No benign control.** `tests/fixtures/r14-census-boundary.py` EXPECTED_IDS (45–58) are all alias/namespace cases; `CASES` (629–642) has no config case. `tools/souji-census.sh --selftest` (1100–1483) has no config-refusal case.
6. **Fixture cannot be reused unchanged.** `BASELINE_SHA` is a31642d (61); `is_baseline` (703–715) forces access-evidence red semantics for every case except 07/08. A paired benign fixture needs its own pinned baseline and tool arguments.
7. **Docs carrying the old contract.** Tool header 85–91; `SKILL.md:216–220`; SCORECARD operability row 15 and capability row 46 (ScorecardDraft's file, not edited here).

## Proposed move (one bounded proposal)

Replace the key-only `case` at 504–507 with a per-key effect table. Refuse when **any** value of a key is effect-bearing (`--get-all`, not last-wins). Keep parse failures and protected-path refusals as they are.

| lowercased key | r14 | r15 proposal | basis |
|---|---|---|---|
| `include.*`, `includeif.*` | refuse | refuse | reads other files; no neutral value |
| `filter.*.clean`/`smudge`/`process` | refuse | refuse | executes commands [INFERENCE: status may run clean filters; verify in git docs before claiming] |
| `core.alternaterefscommand` | refuse | refuse | executes a command; no override |
| `extensions.partialclone` | refuse | refuse | presence means partial clone |
| `core.hookspath` | refuse | **accept when every value is exactly `/dev/null`**; refuse otherwise | no census verb runs hooks; `/dev/null` is the value `count_dirty` forces |
| `core.excludesfile`, `core.attributesfile` | refuse | **minimum:** accept exact `/dev/null`. **broader (operator scope call):** accept any value, with a no-access control | only `git status` reads them, and it is overridden at 710–712 |
| `remote.*.promisor` | refuse | refuse if any value is `true` or unparseable; accept `false` | r13 precedent, `souji-repo-structure.sh:215–233` |
| `extensions.worktreeconfig` | refuse | refuse if any value is `true` or unparseable; accept `false` | config.worktree is not read when disabled [INFERENCE; verify in git-config(1) before claiming] |
| `core.worktree` | boundary-check | unchanged | already value-aware |

Implementation constraints:
- Lowercase keys before matching (keeps current conservative direction).
- Read values with `git config --file "$cfg" --no-includes --null --get-all <key>` or equivalent. Last-wins is insufficient: `core.hooksPath=/dev/null` followed by `core.hooksPath=/tmp/x` must refuse.
- Unsupported (not harmless) repos keep the abort-all behavior. Per-row skipping for genuinely unsupported configs is a scope change for the operator, not part of this repair.
- Update tool header 85–91 and `SKILL.md:216–220` to the value-aware wording (Q23).

## Acceptance (L1 runs after all seats finish; not run here)

**C1 paired controls, identical committed fixture bytes** (new file, e.g. `tests/fixtures/r15-census-config.py`; `r14-census-boundary.py` unchanged), taking `--baseline PATH --tool PATH` and recording both sha256 values:

1. Benign: one repo with `core.hooksPath=/dev/null` plus one ordinary repo.
   - Baseline (r14 bytes, 552cae4): exit 2, reason `git-config-unsupported`, no TSV. This is the red.
   - Changed: exit 0; both rows present; worktrees/unpushed/dirty exact.
   - Preservation reference: pre-r14 a31642d bytes exit 0 on the same fixture. Observed by L1; not assumed.
2. Mixed fleet: benign-hooksPath repo + dirty repo (exact dirty count) + unpushed repo + ordinary repo. Changed: all rows exact. Baseline: exit 2.
3. Benign accepted (changed): `remote.origin.promisor=false`, `extensions.worktreeconfig=false`, and (if broader option chosen) `core.excludesfile` pointing into the synthetic store with zero store access under the existing spy/strace oracle.
4. Negatives (changed must refuse, exit 2): `core.hookspath=/tmp/x`; multi-value `hooksPath=/dev/null` then `/tmp/x`; uppercase `Core.HooksPath=/tmp/x`; `remote.origin.promisor=true`; `extensions.partialclone=origin`; `include.path=...`; `filter.x.clean=...`.
5. Namespace unchanged: `python3 tests/fixtures/r14-census-boundary.py --tool <changed>` → 12/12 PASS; with a31642d baseline still 2/12 PASS with access evidence.
6. Legacy: `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` ≥ 38 checks, zero failures; `shellcheck -S warning tools/souji-census.sh` exit 0.

**C2 checker (independent of the lane's fixture code):** must reject (exit nonzero) each of: a green-only record with no committed baseline red; a benign-control baseline that is not `git-config-unsupported`; changed expected IDs or exit codes; installed digest ≠ recorded digest; missing mixed-fleet rows; removed namespace case IDs. Self-invocation: feed it a doctored green-only record and require rejection.

## Risks

1. **Over-acceptance.** Accepting `excludesfile`/`attributesfile` with any value is safe only while `status` is the sole reader. Guard with a static assertion on the verb set plus the no-access control. A new verb that reads them would silently fail open.
2. **Under-acceptance.** Exact-`/dev/null` hooksPath still refuses common benign hook directories (e.g. `.githooks`). That residual must be disclosed as an unsupported class, not claimed restored.
3. **Fixture reuse.** Do not change `is_baseline` logic in the r14 fixture. Paired r15 fixture must pass explicit digests.
4. **Mixed-fleet scope.** The fix covers harmless values only. A genuinely unsupported repo still aborts the census; claims must say so.
5. **Config race.** Config is read before status; a concurrent change between guard and read remains an undisclosed-by-tests residual (already disclosed in the r14 header).
6. **Doc drift.** SCORECARD row 15 still says "improved" for r14 operability; ScorecardDraft must carry the closure's harmed verdict.

## Verification the main agent should run (not run by this seat)

- Pinned baseline bytes: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 552cae4:tools/souji-census.sh` into `/var/tmp`, plus a31642d bytes, both sha256-recorded.
- Items 1–6 under Acceptance, each with its exact command and observed exit code recorded in `census/round-15/verification.json`.
- Checker selftest including its doctored green-only negative.

## Sent to

Material findings (source-state, design-only label, ready-to-implement table) to `SoujiR15` by id.
