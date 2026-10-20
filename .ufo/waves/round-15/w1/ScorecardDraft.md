# ScorecardDraft — souji r15 w1

Seat: `SoujiR15.ScorecardDraft` (scribe). Scope: source inspection only. No tests, probes, builds, git mutators, or edits outside this file. No `~/.omp` or credential access. `census/operator-sweep-20261019/` not opened. Tool installs/updates: none.

Status: **design-only draft.** The r15 repair (`tools/souji-census.sh`) and the C2 checker (`tests/fixtures/r15-preservation-evidence.py`) are not yet present in the lane. Every number below is either read from committed bytes or is a stated acceptance requirement.

## 1. Axes named

- **operability** (C1): the r14 closure verdict is `harmed`. The repair is not yet measured.
- **calibration** (C2): the r14 C1 verdict is `improved`, bounded. The r15 C2 checker is not yet measured.
- **coverage**: unchanged. Not in scope for this seat.

## 2. Verified r14 correction: what the committed closure says

Source: `corpus/lessons/round-14-verifier-spotcheck.md`.

| Fact | Location |
|---|---|
| Verdict `status: ok; admitted: false; verdict: rejected-harmed` | `:7` |
| operability `harmed`: "key-only benign-config refusal contracts prior census support and aborts all rows" | `:148` |
| calibration `improved`, bounded to C1 `attempt_reuse` on synthetic records | `:71-89`, `:147` |
| Namespace cases improve, but the closure refuses "no-trade" admission | `:91-106` |
| Routed defect 1: "repair benign-config support without weakening protected-namespace refusal ... add paired baseline/changed benign-config controls and a mixed-fleet case" | `:160` |
| Routed defect 3: full migrated dispatch and positive real-evidence retention not run | `:162` |

Source-level root cause, verified by reading, not executed:

- `tools/souji-census.sh:500-506`: `guard_git_config` reads key names only (`git config --name-only --list`), lowercases them, and substring-matches the whole key list. Any hit calls `protected_fail "git-config-unsupported"`. Value is never read for the refused keys.
- Refused substrings include `*core.hookspath*`, `*core.attributesfile*`, `*core.excludesfile*`, `*include.*`, `*filter.*.clean*`, `*remote.*.promisor*`, `*extensions.partialclone*`, `*extensions.worktreeconfig*`.
- `:711-712` already forces `-c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` on status. The key ban adds nothing for those three keys. The closure relies on this at `:104`.
- Propagation: `guard_git_config` is called from the list path (`:581`, `:613`, `:628`, `:650`, `:665`). `list_repos` runs before the header (`emit_census:979`, header at `:991`). `protected_fail` exits 2 (`:160-164`). One refused repo therefore aborts the whole census before any row, which is the mixed-fleet failure.
- Substring over subsection names (inference, not executed): `*include.*` also matches any key containing `include.` inside a subsection, such as `alias.include.x`. The guard does not separate section from subsection, so it can over-refuse further.
- Pre-existing signal, not new: `.ufo/waves/round-14/w1/SafetyCredential.md:61` (N6) and `:80` already listed `core.hooksPath` over-refusal as Open, LOW, to-verify on the real fleet. The r14 build extended the key list without a per-value check.
- Fixture gap, confirmed by grep: `tests/fixtures/r14-census-boundary.py` writes no fleet repo local config with a refused key. Its only writes are the synthetic canary `config.yml` (`:212`) and a bare gitdir with `core.repositoryformatversion` and `core.bare` (`:221-222`). Its 12 cases therefore cannot show a benign-config regression. This matches the closure's `:105-106`.

**Scorecard rows that are now wrong** (current `SCORECARD.md`):

| Line | Current text (excerpt) | Problem | Required correction |
|---|---|---|---|
| 15 | `operability` `8` "improved r14 C2 within tested boundary" | Contradicts closure `:7,:148`. Omits the rejected-harmed verdict | `8` legacy-unmapped; verdict **harmed (r14 closure)**; see §4 |
| 14 | calibration `7` "author verdict pending outside closure" | Closure now exists at `69c1604`, `:147` | Verdict **improved, bounded**, outside closure; round not admitted |
| 46 | capability "supported ordinary census controls remain usable" | Refuted for benign local-config repos (§2 above) | Add explicit restriction and "refused, pending r15 C1" |
| 45 | "actual migrated caller honors nonzero decisions" | Overstated: closure `:89,:162` says only the real `attempt_reuse` on synthetic records was exercised | "decision function exercised on synthetic records; full migrated dispatch not run" |
| 97-102 | "Current r14 state" paragraph | No mention of rejected-harmed or open operability harm | Add the rejected-harmed verdict and open routed defects |
| 66-74 | "r15 (planned r14)" | Lists an r14 quarantine-bound item that is not an r15 claim | Mark as deferred, or remove; r15 claims are `census/round-15/claims.json` C1 operability and C2 calibration |
| `LOG.md:698-702` | r14 author verdict "C2 improved on the stated cases" | Superseded by closure `:7,:148` | Parent annotates with a superseding note; do not rewrite history |

## 3. Pin consistency (blocking for any numeric row)

Three different commit pins appear in the lane:

- `SCORECARD.md:14-15` measured commit `552cae4`
- Closure reviewed-before `a31642d`, reviewed-after `69c1604` (`corpus/lessons/round-14-verifier-spotcheck.md:9`)
- `census/round-15/claims.json:3` baseline `cc2168325768d5356a82c039dcdf787377c55784`

Each operability and calibration row needs **one** measured commit for the r15 row. It must not reuse `552cae4` for an r15 measurement. Whether `cc21683` is an ancestor of `69c1604` is not verified here. L1 must confirm it.

## 4. Numeric delta mapping, r15

Rule set (from `census/round-9/rubric-15.md:25,44,131`, and `census/round-14/claims.json` `score_delta: 0`):

- Scores are **legacy-unmapped**. A numeric change needs the S15 scorer, which requires all 10 gates per axis to be adjudicated PASS/FAIL on baseline and candidate.
- Harm is recorded as a **verdict**, not a numeric decrement. No reproducible mapping exists that turns the r14 benign-config refusal into an integer.
- Fixture and source counts never become score deltas (see §5).

| Axis | Legacy score | r14 closure verdict | r15 numeric delta | Verdict change admissible only when |
|---|---|---|---|---|
| operability | 8 | harmed | **0** | Paired benign-config red/green passes; mixed fleet keeps unaffected rows; 12/12 namespace controls preserved; reviewer admits |
| calibration | 7 | improved, bounded (C1); round not admitted | **0** | C2 checker verifies independent paired preservation evidence; reviewer admits the checker itself |
| coverage | 8 | unchanged | **0** | no r15 coverage claim |

Consequences to write into the scorecard:

- A successful r15 C1 repair restores the operability verdict to "not harmed". It does not raise the score to 9. The numeric 8 remains legacy-unmapped and is not presented as improved.
- If C1 fails, the operability verdict stays harmed and blocks admission. The numeric 8 still does not change.
- A passing C2 checker is capability and verdict evidence. It does not move calibration from 7.

## 5. Counts that must not be cited as score movement

Each of these is a fixture or source count. None justifies a score change:

- r14 namespace cases 12/12 (`census/round-14/verification.json`)
- legacy census selftest 38/38
- cache selftest 48/48; external 22/22; consumer 33/33
- source rows 37→40 (`census/round-14/counts.json`)
- capability rows 9→11
- admitted knowledge 5, HELD 1

## 6. Proposed replacement rows (draft for parent integration)

Parent owns `SCORECARD.md`. This seat does not edit it.

```text
| operability | 8 | legacy-unmapped, numeric delta 0. r14 verdict HARMED (corpus/lessons/round-14-verifier-spotcheck.md:7,148): key-only guard refused benign local config and aborted whole census. r15 C1 verdict pending measured repair; not "improved". Namespace gains retained only as tested. | census/round-14/verification.json; r15 paired benign-config + mixed-fleet evidence (pending) | <single r15 measured commit> | r15 (pending) |
| calibration | 7 | legacy-unmapped, numeric delta 0. r14 C1 verdict improved, bounded to synthetic attempt_reuse; round not admitted. r15 C2 checker pending independent review. | census/round-14/verification.json; r15 checker output (pending) | <single r15 measured commit> | r15 (pending) |
```

Required edits to other rows and sections: the §2 table.

## 7. Acceptance needed before any row can read "not harmed" or "improved"

Source-level requirements; none has been executed.

1. Paired benign-config controls on the same fixture, baseline vs changed. Baseline shows the benign repo refused or aborted. Changed shows it emitted. Benign keys: `core.hooksPath=/dev/null`, `core.excludesFile`, `core.attributesFile`, `include.*` with reachable path, `filter.*` benign, `remote.*.promisor=false`, `extensions.worktreeConfig=false`. Each must be a fleet repo's local `config`.
2. Mixed-fleet case: one benign-config repo plus one unaffected repo. Changed output contains the unaffected row(s). No header-only success.
3. A refused key whose effect is unsafe still refuses (value or effect aware), so the protected-namespace refusal is not weakened. The 12 r14 namespace cases must stay 12/12.
4. Any benign configuration still refused after repair is reported as a **scope change pending operator/canonical adjudication**, not as preserved.
5. Ordering: cases first and last in the fleet, to rule out order-dependent suppression.
6. C2 checker: rejects green-only, missing, or weakened paired records; digest-binds the tool and fixture; requires baseline actual failures on the benign control.

## 8. Unrun checks for L1 (not executed by this seat)

- Consistency check from `census/round-9/rubric-15.md:141-164`, expected: numeric contradictions 0 after correction (8/7/8 agree between table and saturation paragraph); missing capability rows 0.
- Verify the pin in §3 (`cc21683` ancestry against `69c1604` and `552cae4`).
- Re-measure `SCORECARD.md` sha after the parent edits. Do not reuse the r9 pinned hash.

## 9. Routed to other seats

Sent a short summary to `agent://SoujiR15` (see §2 and §3). No edits to `SCORECARD.md`, `LOG.md`, `SOURCES.md` or `QUALITY.md` were made. Those files are not assigned to this seat.

## 10. Boundary disclosure (no-query reminder from SoujiR15)

The lead's reminder forbids whole-lane-root or recursive census searches and any runtime probe. Calls by this seat that breached that boundary, disclosed exactly:

1. `_glob` `souji-shokunin/**/*scorecard*` (gitignore false, hidden true) — recursive over lane root; can enumerate `census/operator-sweep-20261019/`. Result shown contained only `census/round-6/` and root `SCORECARD.md`; no operator-sweep path was printed, but the enumeration itself touched that tree.
2. `_glob` `souji-shokunin/**/*SCORECARD*` — same recursive scope; same limitation.
3. `_glob` `souji-shokunin/**/rubric-15.md` — recursive over lane root; located `census/round-9/rubric-15.md`.
4. `_read` of the lane root directory listing — returned top-level entries and the names of `census/` subdirectories, including the operator-sweep directory name. Its contents were not opened.
5. `_grep` over whole lane root `souji-shokunin` for `rejected-harmed|rejected_harmed|value-blind|harmed`, and a second `_grep` over the same root for `benign|hooksPath|hookspath|cc21683|69c1604|1e0aaa31`. Both are recursive; the second's output was truncated at 50 files ("Showing files 1-20 of 53"), so unshown matches may include operator-sweep paths. Matches printed came from `.ufo/waves/round-*`, `census/round-*`, `corpus/`, `LOG.md`, `results/`, and `census/operator-sweep-20261018/` (a different directory, not 20261019). No operator-sweep-20261019 match was printed.

Mitigation: the report's evidence cites only files reached by explicit paths (`corpus/lessons/round-14-verifier-spotcheck.md`, `tools/souji-census.sh`, `tests/fixtures/r14-census-boundary.py`, `census/round-14/*`, `census/round-15/claims.json`, `.ufo/waves/round-15/*`, `SCORECARD.md`, `LOG.md`, `census/round-9/rubric-15.md`). The pre-existing-signal citation to `.ufo/waves/round-14/w1/SafetyCredential.md` came from the whole-root grep in item 5 and was not re-read by an explicit path. The operator sweep directory `census/operator-sweep-20261019/` was not opened, read, copied, or modified.

No runtime probes, tests, builds, or installs were run. The boundary breaches above were search-only and read-only.
