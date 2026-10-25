author: hyaku closure (non-author integrator, @m_opus)

# Round 16 — non-author closure and verifier spot-check

## Decision

**Status: ok; admitted: true; verdict: admitted.** The report is substantive and committed, not a marker. Both declared claims verify within their declared scope. C1 (operability) was re-measured statically and its matrix evidence verified. C2 (calibration) was verified from committed gate evidence. Neither claim harms an axis against the round baseline `58ace9f`, whose census (`b410186` bytes) did not parse.

This admission covers round 16's two claims only. It does not admit round 14 retroactively. It does not certify the census as no-harm against pre-harm `a31642d`, and the lane does not claim that either ("improved, not no-harm"). The residual contractions against `a31642d` are inherited round-14 debt. They stay open under the lane's L0 question, which is the route the round-14 closure prescribed: "obtain explicit operator/canonical scope-change adjudication; do not call that a no-harm improvement". The admission-blocking predicate routed by the r14 and r15 closures was the value-blind refusal of benign config, with paired benign and mixed-fleet controls. That predicate is repaired and measured (see C1). No lane-authored file and no SHONEN box is changed by this closure.

Reviewed: before `58ace9fba9e58058c2333944175a226be53d0b52`, after `c46eabf80f4c5b34a6774cd8725a0787306ba754`. References: last parsing census `cc21683` (r14) and pre-harm `a31642d` (r13). Auxiliary read-only seats dispatched by this closure, not by the lane: `ClosureSoujiR16.C1NoHarmLedger` (critic), `C1EvidenceCheck`, `C2GateEvidence` and `RoutedR3R7Check` (reviewers). This integrator owns the verdict. No lane gate, selftest, fixture, matrix runner or census was executed (PROTOCOL §Gate standard, Closure consequence). Static checks (`bash -n`, `shellcheck -S warning` 0.11.0, Python `ast.parse`) ran on `git show` bytes in `/var/tmp` scratch directories. Those directories were removed afterwards.

Driver digest (copied from mutable `.ufo/watchdog.log`, lines 479 and 490):
- `2026-10-20T10:51:17-03:00 launch souji round=16 pgid=2432921 driver=hyaku-inline attempt=1`
- `2026-10-20T12:29:49-03:00 complete souji round=16; hyaku-inline attempt=1`
- `lane-dead-no-report souji round=16` count: 0.

## Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report landed by lane | `git log --format='%an %H' -- .ufo/reports/round-16/souji.md` | `souji-shokunin 85f2aa9b9f275109f69c7485c79046cb166efe6d` (12:29:11-03:00) | ok |
| report after commit | lane `c46eabf` 12:27:07-03:00; report 12:29:11-03:00 | | ok |
| cited hashes ancestors | `merge-base --is-ancestor <h> refs/heads/master` for cbf688a 0a70bef c6207bd 7a79dc2 a6ec781 163158a fb23b12 4f9a4e8 79bbe7a 6ff91f5 c46eabf 58ace9f b410186 cc21683 a31642d; also the 8 distinct `resolved@` hashes in the lesson | all `anc ok` | ok |
| pushed | `jj-lane.sh state` → `local=remote=c46eabf… ahead=0 behind=0 head=attached tracked=0 untracked=1`; `ls-remote origin refs/heads/master` → `c46eabf…` | | ok |
| no uncommitted round work | `git status --porcelain` → only `?? census/operator-sweep-20261019/` | operator-owned. Metadata fingerprint `f6a84466…` with 155 entries, identical to the r13 and r15 readings. Not opened. | ok |
| SHONEN heading | report `## SHONEN`, 4 lines, all `[~]` | | ok |
| LOG binding | `LOG.md:836` round 16; `LOG.md:886` wave-2 corrections; correction entry `LOG.md:817-833` | | ok |
| prompt fidelity | Python `difflib`: `templates/round-prompt.md` with `{{LANE}}/{{ROUND}}/{{FLEET_ROOT}}` substituted vs `.ufo/prompts/souji-round-16.md` before `## 6.` | 4 diff lines: the `<souji-repo>` working-dir expansion and the `{{AXES}}` expansion. §6 hyaku addendum appended. Prompt committed by `souji-shokunin` in `63f4df6`. | ok |
| Sources & frontier, trend verdicts, cross-domain line (R6) | present in the report (lines 49-60, 72) | | ok |

Conformance defects (status-neutral): none blocking. Precision notes are listed under routed items D6 and D7.

## Per-claim re-check

### C1 operability: improved (re-measured statically; matrix and live-fleet evidence verified)

| measurement | command | observed | vs claim |
|---|---|---|---|
| census parses, per revision | `git show <rev>:tools/souji-census.sh > f; sha256sum f; bash -n f; shellcheck -S warning f` | a31642d `6a000c59…` 0/0; cc21683 `fcff8b05…` 0/0; **b410186 `dab4122c…` rc 2, `line 1368: syntax error near unexpected token '}'`** (SC1046/SC1073 at 1324, SC1047/SC1072 at 1368); 0a70bef = c46eabf `64a60fd0b0ed…` rc 0, 0 findings | agrees |
| matrix tallies | `jq` over `census/round-16/c1-matrix-final.json` and `c1-matrix-landing.json` | changed: r15-config 20/20, r14-ns 12/12, selftest 38/38. cc21683 fails 16/20: exactly the 15 HARM_CASES plus R15CFG-19. a31642d fails exactly 02,03,08,11,14,17,18,19 (and r14-ns 10/12). b410186 fails every case, selftest rc 2. | agrees |
| matrix bindings | `sha256sum` of `git show <rev>:<path>` | fixture `85de2a43…` = 0a70bef bytes; landing `27474396…` = 7a79dc2 and c46eabf bytes; r14-ns `e6a984b1…`; runner `2815712b…` = `census/round-16/run-matrix.py` | agrees |
| live fleet | `jq` over `census/round-16/live-fleet-final.json` | 21 rows per arm; `r14-harm.rows == changed.rows` exactly; tool digests match git bytes; rc 0 | agrees (preservation only, as disclosed) |
| r14-closure repair predicate | committed fixture `tests/fixtures/r15-census-config.py`; `jq '.arms[]["r15-config"].cases'` over `c1-matrix-final.json` | `r-hooks-devnull` expected clean (case 04, :1149-1165). Mixed fleet `a-benign`/`m-safe-config`(hooksPath=/dev/null)/`z-benign` expected clean in order (case 16, :1314-1322). Per-repo degrade keeps neighbours clean (case 03). Changed arm: 03/04/16 PASS. r14-harm: all three FAIL (04 `observed_exit=2`). Pre-harm fails 03 only. | repaired |
| R1 correction sweep | `git grep 'unverified candidate'` over LOG, SKILL, SCORECARD, README, knowledge | only LOG:820, quoted inside the correction. SKILL:18-23 and 171-173, SCORECARD:15, README:189-195 are corrected | agrees |

No-harm ledger, read from committed source at a31642d, cc21683 and c46eabf (C1NoHarmLedger):
- **Against the round baseline:** operability goes from a census that does not parse to a working census. Nothing can regress against a tool that cannot start.
- **Against cc21683, the last parsing census:** one narrower whole-run trigger is re-landed: an `info/attributes` file that is hardlinked or not a regular file (c46eabf :521, :528-532). `git log -S` places its entry at `b410186`, the round-baseline bytes. It belongs to the same metadata-guard class as r14's hardlinked `config`/`HEAD` guards, which the r14 closure verified as namespace gains. It is a safety guard, not a value-blind config refusal. The lane discloses it, and the L0 question covers it.
- **Silent false clean.** Repo-local `status.showUntrackedFiles=no` yields a false-clean row at all three revisions. No revision passes an untracked-files mode (`git status --porcelain` at a31642d :131, cc21683 :712, c46eabf :1037). One variant is newly reachable against cc21683: the key arriving through an `include` or `config.worktree`, which cc21683 refused value-blind. That is exactly the a31642d behaviour the r14 closure asked to restore, so it is not new harm against the admitted reference. It is a real defect for a cleanup lane and is routed (D1).
- **Relaxations, not contractions:** `--ignore-submodules=all` and the unread global/system config are inherited from r14. Filter-driver keys and `~user`/`%(prefix)` paths move from whole-run refusal (cc21683 :505, :514) to a per-repo `status-unverifiable` or `error` row.

Verdict: the claim **verifies**, and the operability axis is **improved**. The census runs again, the value-blind config refusals are replaced, the namespace cases are retained, and no output on the live fleet changed.

### C2 calibration: improved, scoped (evidence-verified; the gate was not executed)

| item | evidence (path@commit) | observed | status |
|---|---|---|---|
| registry row | `SKILL.md:152`@c46eabf | name, `gate`, entry `--root/--rev/--round`, verdict map 0/1/2, `--selftest`, pinned path, write scope, owner `souji`: all present | conformant |
| can fail | source `evaluate()`: `exit 1 if findings`; `EvalError`→2 | a gate, not a probe. A null stub fails 14/15 on the fixture (`w2/RerunGateFixture.md:28`) | ok |
| training instance `b410186 --round 15` | `.ufo/waves/round-16/w2/RerunGateReplayR15.md:20-32` | exit 1, 5 findings. The seat re-derived all five statically: parse rc 2 at 1368; pin `b5187351…` vs `dab4122c…`; `fc3a8d4` census `fcff8b05…` and r15 fixture absent; `ConfigRepair.md:7` not carried | agrees (committed transcript) |
| r13 / r14 zeros | `RerunGateReplayR13.md`, `RerunGateReplayR14.md:25` | findings 0 (reg 10/15, pins 7/9, markers 0, reports 32) | agrees; exercises parse and pin classes only, as disclosed |
| self-test 18/18 | 18 cases counted in source (15 `check()` at :784-939 plus 3 inline); `RerunGateSelftest.md:11,21` | `SELFTEST pass=18 fail=0` | agrees; asserts exit plus id membership, not exact sets (D6) |
| fixture 15/15 | 14 `case()` plus a vacuity stub; vacuity fix `fb23b12` (`exp_rc 1→0`, `passed = vacuous and not ok` :508-522) | 15/15 in committed `MutateGate*.md` transcripts | agrees |
| round-end run | `census/round-16/gate-landing.json`@c46eabf | `resolved_rev 6ff91f5`, exit 0, findings 0, reg 21, pins 16, markers 30, reports 141. The seat independently counted the same values. | agrees |
| `79bbe7a` → 29 uncarried | prose only (report:45, lesson) | re-derived: 30 markers, 29 uncarried | agrees; `LOG.md:902` says "28" (D3) |
| R4 frozen record | `tests/fixtures/r15-preservation-frozen/expected.json`@c46eabf | pins `e6a984b1…`, `27474396…`, `64a60fd0…` equal committed bytes at `c6207bd` and c46eabf; `measured_commit` resolves; `--frozen clean` transcript `RerunFrozen.md:12`; 47/47 `RerunCheckerSelftest.md:11,21`; 8/8 `RerunCheckerFixture.md:27`; **24/47 prose only**; `regenerate.py:130` writes `"verdict": "clean"` literally (disclosed R16-M2) | verified with gaps (D6) |

Verdict: **verifies, scoped**. Before the round, the three r15 landing-defect classes were caught only by an outside hand read. Now a committed, registered gate fails on its training instance, and its round-end run is committed with the revision it measured. Calibration is **improved**. The lane's own scope limits (not hostile-content safe, STATUS-only channel, synthetic fixture) are accurate.

### Axes

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 above |
| calibration | improved | C2 above. The minor wording errors D3 and D4 are routed; none is an overreach left standing in the claim |
| coverage | unchanged | no knowledge entry or frontier row; admitted knowledge stays 5, K5 HELD |
| depth | unchanged | not claimed. SKILL registry rows and Q25/Q26 were added (both cite R16-M1/M2/M4/M5 and `round-16.md`) |
| freshness | unchanged | not claimed. Three knowledge entries gained a "verified on 2.55.0, recheck" note; nothing was re-verified |
| adjacency | unchanged | R6 line added; its citations resolve (tameshi `017a2b0:PROVINCE.md:49-57`, `w1/SiblingOverlap.md:39`, `w2/ConnSiblingOverlap2.md` F5/F7) |

`git diff 58ace9f c46eabf -- SCORECARD.md`: no score number moved (calibration 7, operability 8). Both verdict rows were rewritten "outside admission pending". In the capabilities table, the protected-namespace row was replaced by the r16 value/effect-aware row, and two rows were added: landing-claim gate and seat transcript audit. Every pointer resolves at c46eabf.

## Routed R1–R7 from the round-15 closure

| item | disposition | evidence |
|---|---|---|
| R1 parse restore + correction sweep | resolved | parse and ShellCheck clean at 0a70bef = c46eabf; LOG:817-833, SKILL, SCORECARD:15, README:189-195 corrected |
| R2 r14 value-blind config harm | resolved for its admission-blocking predicate; broader residuals open under L0 | cases 03/04/16; `.ufo/l0-questions.md:59`, added by fleet commit `273d6a6` |
| R3 seat failures carried verbatim | resolved with gaps | lesson :43-93: 12 + 29 + 4 = 45 lines; every `resolved@` hash is an ancestor; gate scan 30 markers, 0 uncarried. Gaps in D5 |
| R4 frozen pins | resolved | re-pinned and measured at `c6207bd`; pins match bytes |
| R5 probe rule enforced | partially: audit, not enforcement (as disclosed) | `seat-audit-w1/w2.json` totals match (65/3173 and 79/4348). Gaps in D4 |
| R6 cross-domain line | resolved | report:72; citations resolve |
| R7 git-status rejected row | resolved | `corpus/SOURCES.md:58` S044 `rejected`; quote checked below |

## Discernment spot-check (`corpus/lessons/round-16.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S049 git(1) GIT_NO_LAZY_FETCH | admit, A, mined | https://git-scm.com/docs/git (served "last updated in 2.56.0"), re-opened 2026-10-20 | agree | The quote "Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand." is present (21 words). The teaches cell matches the census: `export GIT_NO_LAZY_FETCH=1` at c46eabf :161, before every git call. |
| S047 gitignore(5) | admit, A, mined | https://git-scm.com/docs/gitignore (served "last updated in 2.55.0") | agree | The quote "Its default value is $XDG_CONFIG_HOME/git/ignore. If $XDG_CONFIG_HOME is either not set or empty, $HOME/.config/git/ignore is used instead." is present (17 words). Its scope (default location only) is properly narrow. |
| C1 candidate admit | admit (claim) | `census/round-16/c1-matrix-final.json`; census source at three revisions | agree | Measured red/green on identical fixtures with all four arms, plus the live preservation run. The author's "not no-harm vs pre-harm" scoping is accurate. |
| S048 ShellCheck SC1046 | reject (365d) | https://www.shellcheck.net/wiki/SC1046 (no version line) | agree | The page says only "Couldn't find `fi` for this `if`." plus a generic rationale. The r15 break is established by `bash -n` on committed bytes; this page adds no evidence about any lane revision. |
| S044 git-status(1) | reject (on-release) | https://git-scm.com/docs/git-status (served "last updated in 2.53.0") | agree | "guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration" is present (16 words). The page does not say which config values abort or neutralize, so it cannot ground the value/effect guard. It does document `status.showUntrackedFiles`, which supports routed defect D1. |
| "disclosure enforcement" label for C2 | reject | `RoutedR3R7Check` scan of `.ufo/waves/round-16/w1` | agree | The channel is STATUS-vocabulary only: 55 non-vocabulary wave-1 lines, 11 carried, the disclosed 9 confirmed, and `RevGateSpec.md:226` is one more. "Enforcement" would overclaim. |

Newly written row re-opened: S049 (above). Its quote is ≤25 words and located at lesson line 32; the registry row's anchor names § ENVIRONMENT VARIABLES.

SOURCES census, re-derived by this closure with `git show <rev>:corpus/SOURCES.md`, counting anchored `^\|\s*S\d{3,}\s*\|` rows with a Counter over the tier and status cells:
- before `58ace9f`: 42 rows, sha256 `5185720f…`, `{'A': 38, 'B': 3, 'C': 1}`, `{'mined': 25, 'queued': 15, 'rejected': 2}`
- after `c46eabf`: 50 rows, sha256 `b0683473…`, `{'A': 46, 'B': 3, 'C': 1}`, `{'mined': 31, 'queued': 15, 'rejected': 4}`
- the only touched old row is S042 (used-by widened)

All of this matches the report.

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` gave exit 0:

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S049 duplicate url git-scm.com/docs/git across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

## Trend verdicts

- **expansion: unprovable-but-better.** This closure is the named non-author reviewer, and it agrees with the author. Two capabilities are demonstrated running with committed evidence: the landing gate (`gate-landing.json`) and the seat audit (`seat-audit-w1/w2.json`). Six tier-A sources were mined. No knowledge entry or frontier row advanced, so the LEARNING "improved" predicate is not met.
- **quality: improved.** Agrees with the author. The r15 harm was "an entry found false and left unmarked": `SKILL.md` pointed at a non-parsing census. It is now true and measured. The r15 frozen record is regenerated, and its pins match committed bytes. Stale-on-2.55.0 entries are now marked. No admitted entry failed a re-check.
- **discernment: improved.** Agrees with the author. Every r15 outside disagreement became a mistake row (R16-M1..M6) and a grounded criterion: Q25 cites R16-M1/M2/M4 and Q26 cites R16-M5, both pointing at `round-16.md`. This spot-check agrees with all sampled admits and rejects.

## Routed defects (souji next round unless noted)

1. **D1, false clean (cleanup-safety, highest).** Repo-local `status.showUntrackedFiles=no` gives a dirty repo a clean row, because `count_dirty` (c46eabf :1035-1041) passes no untracked-files mode. The variant carried by `include`/`config.worktree` is newly reachable against cc21683; the directly set key is inherited from a31642d. Add an explicit `--untracked-files=normal` (keeps the one-line collapse) or equivalent. Add a paired fixture case, run on pre-harm, r14 and changed arms.
2. **D2, `info/attributes` whole-run trigger.** A hardlinked or non-regular `info/attributes` (c46eabf :521, :528-532) aborts the whole fleet run. Degrade it per repo (patch in `RevCensusScanFinal.md` S5), or keep it explicitly under the L0 ruling.
3. **D3, append-only LOG corrections.** Two named correction entries are needed. `LOG.md:902` says the gate flagged "28" uncarried wave-2 STATUS lines; the lesson, the report and the re-derivation give 29. `LOG.md:858-859` says "pre-harm fails only refusal/safety cases"; it also fails 03 (degrade) and 18 (preserve), as `round-16.md:20` correctly states.
4. **D4, seat audit precision and evidence.** The 3 wave-2 `V-WRITE-SCOPE` majors are audit false positives:
   - one is the seat's own report path, misread because `target.lstrip("./")` drops `.ufo`'s dot (`tools/souji-seat-audit.py:76-82`);
   - two are prose read by the first-comma `write_target` split (`:68-73`).

   The report's description "all failed edit calls, no bytes written" therefore mischaracterizes them. The audited transcripts live only in `/var/tmp/souji-r16/transcripts`: they are uncommitted and have no digest binding. Commit a digest manifest, or state that the audit is not reproducible. The report's no-install sweep rests on the same bytes.
5. **D5, R3 carry format.** `round-16.md:54` has `resolved:` with no `@<hex>`. Two wave-2 quotes (`ReopenS048.md:102`, `ScoutOptionalPrefix.md:238`) stop at a line wrap with no ellipsis. Round-15 lines :91 and :93 are joined or paraphrased. `RevGateSpec.md:226` is one more uncarried non-vocabulary defect line. Widen the channel or carry by reading, as the lesson already routes.
6. **D6, gate evidence pinning.** The replay verdicts are committed only as seat transcripts or prose: b410186→5, a31642d/cc21683→0, 18/18, 15/15, `79bbe7a`→29, and checker 24/47 (prose only). Commit `--json` frozen runs with expected verdicts. Make the self-test assert exact id sets, since an over-firing gate currently passes. `regenerate.py:130` writes `"verdict": "clean"` as a literal (disclosed in R16-M2).
7. **D7, minor wording.** The report says "`gate-landing.json` (gate at `6ff91f5`)". The file lands at `c46eabf` and records a run over `6ff91f5` blobs.
8. **Operator (not lane).** Rule on L0 `souji | round-16` (scope of the residual contractions against `a31642d`). Separately, decide the disposition of the untracked `census/operator-sweep-20261019/`, still unchanged.

SHONEN: all four boxes are `[~]`. None is certified checkable by this closure: the live end-to-end task and the operational instructions were not executed here (no lane tool runs at closure). Promotion stays operator-owned.

Tool installs/updates by this closure and its seats: none.
