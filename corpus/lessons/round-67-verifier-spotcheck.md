author: hyaku closure (non-author integrator, @m_zfl)
round: 67 (souji) — non-author closure spot-check
date: 2026-11-05
report: .ufo/reports/round-67/souji.md (fleet repo, commit 907a808a by souji-shokunin <souji@shokunin.local>)
lane HEAD before → after: 3639087917eaeb28719d7603110a6ec22782100e → 485b3b00679d086ba846939349d451ad15d69824

## Conformance results

| check | result | evidence |
|---|---|---|
| report committed by lane identity | PASS | `git log --format='%an <%ae> %H' -- .ufo/reports/round-67/souji.md` → `souji-shokunin <souji@shokunin.local> 907a808a08486080a0044cf7257a8faf3c6c3d2f`; ancestor of fleet master |
| `SHONEN` heading, one line per box | PASS | report `## SHONEN` carries four `[~]` lines, one per SHONEN.md box (4/4); no `[x]` written by the lane |
| every cited lane commit exists and is an ancestor of the branch | PASS | `git -C souji-shokunin merge-base --is-ancestor <h> master` → ANCESTOR-OK for f70da577, 05eb2cee, d544e75a, 832a4d43, b3aa70fe, d874bf0d, 4c61efcb, 2771b02e, e41f022f, 36200ad8, 11a96e07, 485b3b00, c13fbb4e (branch ref `master`, not `@{u}`; HEAD detached, jj-colocated) |
| lane repo clean and pushed | PASS | `scripts/hyaku/jj-lane.sh state` → `local=485b3b00… remote=485b3b00… ahead=0 behind=0`; `git status --porcelain` → empty; `ls-remote origin refs/heads/master` → `485b3b00…` |
| dispatched prompt carries the template contract | PASS | `.ufo/prompts/souji-round-67.md` sections 1–5 render `templates/round-prompt.md` (all six section headers present; L2 floor "at least 8 … ONE batched AgentSwarm call" at line 82; report path line 101; SHONEN-heading line 118 + self-check line 521; commit-then-push line 133; push scope line 135; L0 line 138; write scope line 448; report-lands-last line 516); hyaku addendum §6/§7 and run-15 notes appended. No role→route table quoted in the prompt, so the MISSION.md bucket-match clause has nothing to contradict |
| report lands last | PASS | lane HEAD 485b3b00 committed 14:10:51 -03:00 < report commit 907a808a 14:12:48 -03:00 < watchdog complete 14:14:02 -03:00 |
| dispatch/complete digest | PASS | watchdog.log lines 2872/2887: `2026-11-05T12:44:43-03:00 launch souji round=67 pgid=3800627 driver=hyaku-inline attempt=1` / `2026-11-05T14:14:02-03:00 complete souji round=67; hyaku-inline attempt=1` (copied to MANIFEST notes) |
| marker rule | PASS | real report: two declared claims, committed work, evidence pointers, all six required sections present — not a marker |
| frozen instruments unchanged freeze → HEAD | PASS | `git rev-parse 4c61efcb:<f>` == `git rev-parse 485b3b00:<f>` for c1-counter.py, c1-matrix.tsv, c2-counter.py, c2-statements.tsv, c2-mutate.py, preregistration-attempt4.txt — all SAME |
| census at closure | PASS | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → exit 0, `souji ok`; S-row count 223 (report: 222→223); malformed-row awk 0; only the pre-existing status-neutral W04 duplicate-URL warnings (report disclosed them) |

## Per-claim re-check (evidence-verified, gates not executed)

Both claims rest on lane-owned registered gates (`SKILL.md` registry rows "r67 writer GIT_COMMON_DIR matrix" and "r67 redirect-claim statement agreement", lines 893–894, with verdict maps and self-test spellings). Per PROTOCOL §Gate standard (Closure consequence) their committed evidence was verified; no counter, selftest, mutant recipe, or gate was executed by this spot-check. Plain measurements (hashing/grepping committed bytes, counting rows) were run by this checker.

**C1 — operability (receipt-binding, value-checked caller `GIT_COMMON_DIR`), measured at `f70da577`:**

- Receipts: `census/round-67/controls/c1-do-nothing.txt` `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=2 new_honest=6 class_mismatches=2 regress=PASS`, `EXIT=1` (W1/W2 accept on base bytes); `census/round-67/records/c1-after.txt` `SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS`, `EXIT=0` (W1/W2 refuse `RECEIPT-ENV-COMMONDIR-MISMATCH`; W3 accept). Both carry `rev=`, `instrument_sha256=`, matrix hash, per-case rows and the counter-internal regress control (`cases=8 pass=8 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`).
- Hash pins re-measured by this checker: landed writer bytes `sha256sum` of `git show f70da577:tools/souji-receipt-write.py` = `b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725`, byte-identical at HEAD 485b3b00 and to the wave candidate + its committed `SHA256SUMS`; `c1-counter.py` = `69f11706ce98fe0c635bdbec7f24d8be5d1a36a54c4c5cfa1d019c362aa136b2`; `c1-matrix.tsv` = `5d26b341e4718ba1dc62b8bec2d6ba0d29fafdcf1fdb302d1435736cd976a692` — all equal to the freeze (`preregistration-attempt4.txt` at `4c61efcb`) pins; prereg byte-identical freeze↔HEAD.
- Writer code inspection (grep over committed bytes, not execution): `_check_env_commondir()` refuses on empty value (`if value == "": refuse(...)`), compares `os.path.realpath(value)` against the root-resolved common dir, and `git()` scrubs `GIT_COMMON_DIR`/`GIT_DIR`/`GIT_WORK_TREE` from every git call — so the two clauses the frozen matrix does not measure (M9: scrub-every-call, empty-value refusal) are present in the landed bytes, corroborating the round's decision not to count them as measured passes.
- Committed selftest tally: `census/round-67/wave/w1/S67ExecWriter/candidate/selftest.txt` → `SELFTEST cases=37 pass=37 fail=0`, `EXIT=0`; kill witness `selftest-mutant-nocall.txt` → `cases=37 pass=34 fail=3`.
- Frozen target met on the do-nothing control (before) and landed bytes (after); reported values match the committed records exactly.

**C2 — calibration (redirect-claim marker check; lowest owned axis 7), measured at pinned `c13fbb4e` (= the round-66 landing commit):**

- Receipts: `census/round-67/controls/c2-do-nothing-r66.txt` (round-66 counter, same state) `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0`; `census/round-67/records/c2-after.txt` (r67 counter) `FINDING SCOPE-OVERREACH s5: … claim redirects_closed needs writer markers cdred; writer blob lacks them`, `MARKERS … cdred=0`, `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1`.
- Kill power receipts: `records/c2-selftest.txt` `SELFTEST pass cases=17 fail=0`, `EXIT=0`; `records/c2-mutant-reverted-selftest.txt` `SELFTEST-CASE m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `fail=1`, `EXIT=1` (the M2 vacuous-draft repair shown able to fail); `records/c2-mutant-enumweak.txt` `findings=0 verdict=PASS`, `EXIT=0` at the pinned state.
- Population check: `c2-statements.tsv` 5 rows (s1–s5); s5 `after_claim` names `redirects_closed`; the finding's `cdred=0` marker condition matches the row note (the pinned r66 writer lacks the marker). Counter + population sha256 match the freeze pins (`045b47d1…`, `8782a21d…`); `c2-mutate.py` is bound by the freeze-commit blob only — the prereg carries no sha256 pin for it (observation, below).
- Frozen target met; this is a detection of a historical overreach at a pinned state, not a score move (calibration 7 unchanged, correctly not claimed as one).

**No owned axis harmed:** `git diff 3639087917 485b3b00 -- SCORECARD.md` touches only the planned list and an appended `### Round 67 measurements` section; the axes table is byte-identical base↔tip (calibration 7, coverage 8, operability 8; `## Retired: None`), and the round's own row records "Trend-visible score changes: none".

## Per-axis verdicts

| axis | verdict | reason |
|---|---|---|
| operability | improved | C1 frozen predicate verified on committed evidence (forgery rows W1/W2 closed 2→0, honest accepts kept 6/6 including the equal-value W3, regress control green both slots); the unmeasured clauses are corroborated in code; the relative-value trade is fail-closed (no accepted redirect), routed to the operator, and not counted as an improvement |
| calibration | improved | C2 verifies: the new counter flags the round-66 s5 scope overreach the round-66 counter scored clean, with selftest kill power over the reverted-rule mutant; a detection claim, score honestly unchanged |
| coverage | unchanged | coverage 8 untouched; the F4-adjacent common-dir route entered as frontier (`corpus/README.md` `### Frontier (r67 GIT_COMMON_DIR route)`), not core — correctly not claimed as coverage movement |

## Discernment spot-check (lesson `## Gate` sample, re-opened by this checker)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S300 admitted (tier A, code, scope "common-dir resolution", mined) | admit | live `https://raw.githubusercontent.com/git/git/v2.56.0/setup.c`, `…/environment.c`, `…/Documentation/git.adoc` (HTTP 200 ×3) + committed captures `S67ScoutSources/setup.txt`, `doc-git.txt` | agree | All three located quotes match the live v2.56.0 bytes by fixed-string whitespace-normalized search (setup.c `get_common_dir` body lines 310–317; git.adoc `GIT_COMMON_DIR::` entry line 580; environment.c `local_repo_env[]` lines 84–100 ending `GIT_COMMON_DIR_ENVIRONMENT, NULL };`), and the committed captures are byte-identical to the live files (sha256 `8316b1ad…` and `050c5330…` re-measured equal). Tier A (primary source + official docs) fits the scoped claim; the knowledge entry's `source:`/`verified-at:`/`recheck:` trio cites S300+S298 and is re-runnable |
| "git scrubs `GIT_COMMON_DIR` for every child process" (rejected inside the entry) | reject | live `environment.c` `local_repo_env[]` | agree | The array shows git treats the variable specially in its own setup paths (membership), not a universal child-process scrub; a universal claim would need a sweep the source cannot ground. The lane's reject reasons match the re-opened source |
| "a relative value is canonicalized against the writer cwd, the same rule git applies" (prereg L2 wording; rejected as M4) | reject | live `setup.c` `get_common_dir` (value used as given, `strbuf_addstr(sb, git_env_common_dir)`, no canonicalization at read) + committed probe `census/round-67/probes/relative-value-probes.txt` P-rel1 | agree | Git resolves the value later, against its own `-C <root>` cwd; a writer running with cwd ≠ root compares cwd-canonical against root-relative and fails closed. The prereg wording overclaimed; the round disclosed it (M4, named limit, operator L0 `ca47fecf`) instead of counting it — the honest disposition |

Sample: 1 admit + 2 rejects, all agreed. No disagreement to learn from; Q130 (QUALITY.md line 346, supersedes Q129) is grounded in lesson M7 as the discernment-trend criterion requires.

## Trend verdicts (checker's, agreeing with the report)

- **expansion: improved.** One admitted knowledge entry on ground the coverage map did not hold (round-66 W2 named the `GIT_COMMON_DIR` route open, `census/round-66/probes/w2-w3-env-probe.txt`), `source:` citing mined rows S300 (new) and S298 (`used-by` extended both directions, logged old→new per M11); registry 222→223 with census exit 0; README frontier row added.
- **quality: improved.** The round-66 false named limit (repository-local `core.excludesFile`) is corrected by probe PK3 (M3), the overstated enumeration wording corrected (M7 → Q130), the unmeasured claim clauses named rather than counted (M9); no admitted entry found false and left unmarked. The named relative-value trade is disclosed and routed, not hidden.
- **discernment: improved.** Non-author seats disagreed with four L1 statements and each disagreement became a lesson row with a grounded criterion or named limit (M4, M7, M9, M11; Q130); this closure spot-check agrees with the sampled admit and rejects above.

## Routed defects / notes for the next round

1. **c2-mutate.py unpinned:** the frozen prereg pins sha256 for both counters and both populations but not for `c2-mutate.py` (path-only reference); its bytes are bound only by the freeze commit's blob. Route: the next prereg pins every instrument it names.
2. **Two C1 claim clauses unmeasured by the frozen matrix** (scrub-every-call, empty-value refusal — M9, lane-disclosed, corroborated by code inspection at `f70da577`): route to the next frozen counter as rows.
3. **Relative-value trade** (`GIT_COMMON_DIR` relative, writer cwd ≠ root, fail-closed refusal): operator L0 `souji | round-67` (fleet commit `ca47fecf`); lane routed around it — not resolved this round.
4. **Wave role split:** the protocol's minimum split names three executors; this wave had one (lane-disclosed conformance defect, recorded for the route-map owner).
5. **Counter hermeticity:** `c1-counter.py`'s `clean_env()` does not scrub the operator's ambient `GIT_COMMON_DIR` (sentinel M1/M2; run procedure `env -u`); the next frozen counter adds the scrub (lane-routed).
6. SHONEN boxes look fully checkable by a non-author on this round's evidence (decision tables/checklists/cited sources; end-to-end task logged with measured commits; counters self-contained with records; PROVINCE unchanged) — operator-owned promotion decision.
