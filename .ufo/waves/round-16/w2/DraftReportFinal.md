# Souji — round 16 report body (DRAFT, scribe seat SoujiR16.DraftReportFinal-4, wave 2)

Status: scoped draft for `/home/vgpnk/Projects/shokunin/.ufo/reports/round-16/souji.md` (the fleet-root destination named by the assignment). This file is the only file this seat wrote. Lane HEAD observed: `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`. Fields marked `[PENDING]` need L1 acceptance output, LOG binding, or a push/validate step this seat did not run. Nothing here is an observed pass unless its row says so.

Evidence labels: **[OBS]** read from a named artifact or git object by this seat; **[REL]** relayed from `corpus/lessons/round-16.md` and not re-observed; **[INF]** inference from source read.

## Work performed

Claims declared by the round-16 contract, with the verdict this seat can support:

1. **C1 — operability** (parsing, value/effect-aware census config guard). **Verdict: supported for the measured checks; two statements remain open.** [OBS] `tools/souji-census.sh` blob sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` at HEAD and in the worktree (clean for the census and fixture paths). [OBS] Both matrices show the changed arm at 20/20, 12/12, 38/38, bash -n rc 0, shellcheck 0 findings (see Before → after). Open: the header claim "the driver never runs" (census:106) and "only a protected-namespace reach keeps whole-run exit 2" (census:88–92 per seat reports) are contested by seat findings that the lesson does not carry (see Seat-reported failures, rows 21–27). [INF] At HEAD, the bound-filter probe now carries `pid=$!`, `wait "$pid" || return 1` and a triplet-parity check (census:1009–1011), and newline-suffixed filter values are treated as defined (census:991); those lines match the mitigations the D1/F1 seat reports asked for, but no seat re-review or run confirms them.
2. **C2 — calibration** (`tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py`). **Verdict: source present at HEAD; gate replays NOT re-run by this seat; carry rule has a documented blind spot (see Seat-reported failures).** [OBS] Gate header (`tools/souji-landing-gate.py:62–84`) restricts the seat failure channel to a `STATUS` prefix at line start whose first value word is in `FAILURE_STATUS_WORDS`. [REL] Replays: b410186 → 5 findings; a31642d → 0; cc21683 → 0; selftest 18/18; fixture 15/15. [OBS] An earlier gate run recorded in `.ufo/waves/round-16/w1/LandingGate.md:121` reported `findings=34` for b410186; that was a pre-narrowing revision, so the 5-finding replay is a different gate version. [PENDING: L1 replay output bound to HEAD.]
3. **R4 — r15 preservation checker repaired and frozen record regenerated.** [REL] Selftest 47/47, external fixture 8/8, `--frozen` clean at c6207bd. [OBS] c6207bd touched `tests/fixtures/r15-census-config.py`, `tests/fixtures/r15-preservation-evidence.py`, `tests/fixtures/r15-preservation-frozen/regenerate.py`, `tools/souji-preservation-evidence.py`. This seat did not run the checker. [PENDING: L1 `--frozen` output at HEAD.]
4. **R5 — seat probe-rule audit.** [OBS] `tools/souji-seat-audit.py` exists; `census/round-16/seat-audit-w1.json` reports 65 seats, 3173 calls, 1 major, 19 minor. [OBS] Reconciled against the transcript records: the 19 minors are 18 `V-RECURSIVE` and 1 `V-WRITE-UNKNOWN` (SentinelCommandExec, transcript line 118). The lesson's wording "19 minor — whole-lane or directory-wide recursive reads" is one short. The audit does not flag git-subcommand allowlist breaches or `python3 -c` use, which seats self-disclosed (see Seat-reported failures, section C).
5. **Routed defects R1–R7** (`corpus/lessons/round-15-verifier-spotcheck.md`):
   - R1 parse restore — [OBS] bash -n rc 0 in both matrices; [REL] r15 baseline b410186 rc 2 at line 1368.
   - R2 r14 value-blind harm — [OBS] changed arm 20/20; r14-harm arm 16 of 20 r15-config cases non-PASS. The lesson says these are the 15 HARM_CASES plus R15CFG-19; this seat verified the 16 ids, not the HARM_CASES tuple.
   - R3 carry seat failures verbatim — **[PARTIAL — not met]**. The lesson's `## Seat-reported failures` omits defect-bearing STATUS text (rows 21–27 below).
   - R4 re-pin frozen pins — [REL] done at c6207bd/7a79dc2; [PENDING: L1 `--frozen` at HEAD].
   - R5 enforce seat no-probe rule — [OBS] audit exists and reports 13 seats with violations; enforcement is partial (see Seat-reported failures, sections B and C).
   - R6 cross-domain evidence line — see Cross-domain line below.
   - R7 `rejected` row for git-status(1) — [REL] S044 rejected, on-release recheck (`corpus/lessons/round-16.md`, Sources). [PENDING: SOURCES.md row verification; SOURCES.md is modified and uncommitted.]

## Landed changes

| commit | landed work | LOG binding |
|---|---|---|
| `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (2026-10-20T11:13:47-03:00) | `round-16: restore parsing value/effect-aware census; execute and repair config fixture (C1)` [OBS] | [PENDING: LOG.md line] |
| `0a70beff3becff2c64944595860a31fc6e193076` (11:40:42) | `round-16: integrate wave-1 review fixes into census, config fixture and matrix runner (C1)` [OBS]; census bytes unchanged from this commit to HEAD [OBS] | [PENDING] |
| `c6207bdac2e0ef52c1da5fbc87dce5d94065972e` (11:52:32) | `round-16: execute and repair the r15 preservation checker, bound fixture details, add frozen regenerator (R4)` [OBS]; changes `tests/fixtures/r15-census-config.py` (fixture bytes change from `85de2a…` to `27474396…`) [OBS] | [PENDING] |
| `7a79dc2d6e282654b9379c391c4c6be985ccf92c` (11:55:35) | `round-16: landing gate, its held-out fixture, seat transcript audit, regenerated r15 frozen record, wave-1 evidence (C2, R4, R5)` [OBS]; 74 files, +20418/−85 | [PENDING] |
| `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` (11:59:22) — HEAD | `round-16: narrow the gate's failure channel to contract STATUS vocabulary; audit honors ALLOWED-EXEC (C2, R5)` [OBS]; touches `tools/souji-landing-gate.py`, `tests/fixtures/r16-landing-gate.py`, `tools/souji-seat-audit.py` only [OBS] | [PENDING] |

Uncommitted in the lane worktree [OBS, `git status --short`]: `M corpus/SOURCES.md`; `?? corpus/lessons/round-16.md`; `?? census/round-16/c1-matrix-landing.json`. Pushed status: [PENDING: L1].

## Before → after measurements

Measured by the L1 matrix runs and read by this seat from the artifacts; this seat ran no census, fixture or gate.

| check | arm / revision | observed (artifact) | verdict |
|---|---|---|---|
| r15 config fixture | changed, `0a70bef` (final) | 20/20 PASS; fixture sha `85de2a43…` [OBS `census/round-16/c1-matrix-final.json`] | pass |
| r15 config fixture | changed, `7a79dc2` (landing rerun) | 20/20 PASS; fixture sha `27474396…` = HEAD fixture [OBS `census/round-16/c1-matrix-landing.json`; `git show HEAD:…` sha256] | pass |
| r14 namespace | changed, both | 12/12 PASS [OBS] | pass |
| legacy `--selftest` | changed, both | 38/38, rc 0 [OBS] | pass |
| `bash -n tools/souji-census.sh` | changed, both | rc 0, no stderr [OBS] | pass |
| `shellcheck -S warning` | changed, both | 0 findings, rc 0; shellcheck 0.11.0 [OBS] | pass |
| r15 config, pre-harm `a31642d` | both matrices | non-PASS: R15CFG-02, 03, 08, 11, 14, 17, 18, 19 (8 of 20) [OBS] | red as expected |
| r15 config, r14-harm `cc21683` | both matrices | non-PASS: R15CFG-01, 03, 04, 06, 07, 08, 09, 10, 12, 13, 14, 15, 16, 18, 19, 20 (16 of 20) [OBS] | red as expected |
| r15 baseline `b410186` | both matrices | `bash -n` rc 2, `line 1368: syntax error near unexpected token '}'` [OBS] | red as expected |
| landing gate replays | HEAD | [REL] b410186 → 5 findings; a31642d → 0; cc21683 → 0; selftest 18/18; fixture 15/15 | [PENDING: L1 output bound to HEAD] |
| live fleet pair | r14-harm vs changed | `census/round-16/live-fleet-final.json`: `rows_identical_excluding_mtime: true`; `root` = `/home/vgpnk/Projects/shokunin` [OBS]; its `note` says the live fleet had no r14-refused key, so the pair shows preservation of live rows only; [REL] "21 repositories" not re-counted | preservation only; not benign restoration |

Measurement caveat (calibration): the lesson says C1 was "Measured at 0a70bef". The fixture bytes measured at 0a70bef (`85de2a…`) differ from HEAD's (`27474396…`); c6207bd changed the fixture after the final matrix. The landing rerun at 7a79dc2 is the measurement bound to HEAD's census and fixture bytes. Results are identical in both runs.

## Sources & frontier

- Before (round-15 end, `b410186`): 42 rows, A/B/C 38/3/1, mined/queued/rejected 25/15/2 — [REL] `census/round-15/end-sources.json`, digest `5185720f…` (lesson Gate). [PENDING: not re-counted by this seat.]
- After (round-16 end): [PENDING — `corpus/SOURCES.md` is modified and uncommitted; count by Python eval over `corpus/SOURCES.md` bound to a digest].
- New rows this round, all sourced by L1 (lesson `## Gate`, Sources): S043 GNU Bash `set -n` (live host timed out; Wayback capture, mined); S044 git-status(1) (rejected, on-release); S045 gitattributes, S046 git-check-attr, S047 gitignore, S049 git lazy-fetch (mined); S048 SC1046 (rejected, 365d); S050 Python `compile()` (mined). S042 used-by updated to include round-16. [REL]
- Source-validation exit codes, start and end: [PENDING — `scripts/sources-census.sh validate` was not run by this seat].
- Frontier: [REL] carry-forward F2 size attribution, unexercised quarantine sites; K5 HELD; certification OFF.
- Note [OBS]: SrcPythonAst's draft proposed id S043 for Python `ast` (`.ufo/waves/round-16/w1/SrcPythonAst.md:3–4`), and the lesson uses S043 for GNU Bash and S050 for Python `compile()`. Renumbering is recorded as "L1 must renumber"; the lesson does not show the Python `ast` page. [PENDING: confirm no row is dropped.]

## Trend verdicts

- **Expansion:** [PENDING]. [OBS] One candidate capability admitted (landing gate, scoped).
- **Quality:** [PENDING]. No admitted improvement is inferred from open or carried-but-unresolved seat findings (rows 21–27).
- **Discernment:** [PENDING]. R6 line below.

## SHONEN

- [~] Decision tables/error patterns/checklists/sources: [PENDING].
- [~] Historical end-to-end task: [PENDING].
- [~] Instructions: [PENDING — `SKILL.md` must warn of any unverified candidate].
- [~] Domain boundary: `PROVINCE.md` [PENDING unchanged or changed].

## Stale-lane

Lane HEAD `a6ec781`; worktree dirty (`M corpus/SOURCES.md`, `?? corpus/lessons/round-16.md`, `?? census/round-16/c1-matrix-landing.json`); census bytes `64a60fd0…` unchanged since `0a70bef`; the C1 final matrix used fixture bytes `85de2a…` replaced by c6207bd, and the landing rerun at `7a79dc2` is bound to HEAD's bytes. No other souji round or mission was observed in the registry or the visible roster; this is a subset observation only.

## Cross-domain evidence line (R6)

`census/round-16/live-fleet-final.json` (committed at `7a79dc2`; `root` = `/home/vgpnk/Projects/shokunin`, the fleet root; `rows_identical_excluding_mtime: true` for r14-harm vs changed). This seat did not re-run it, and its own `note` limits the claim to preservation of live rows.

## Seat-reported failures (verbatim, R3)

Each row quotes the first line of the seat's `STATUS` text verbatim from its wave-1 report under `.ufo/waves/round-16/w1/` (continuation lines are not reproduced; `…` marks a line the read tool truncated). "Lesson" = whether `corpus/lessons/round-16.md` `## Seat-reported failures` carries it. "This seat" = this seat's own check.

**A. Carried by the lesson (rows 1–11; row 12 is an audit cross-reference, not a lesson row):**

| # | source | verbatim STATUS line | lesson | this seat |
|---|---|---|---|---|
| 1 | `ConnLogConvention.md:385` (also `:221`) | `    ## STATUS: INCOMPLETE — file has an unresolved syntax error` (quotation of r15 `ConfigRepair.md:7` inside a draft) | carried; resolved@0a70bef | [OBS] quotation, not an r16 failure |
| 2 | `CriticNoHarmPreharm.md:14` | `STATUS: residual contraction exists and needs operator scope adjudication. Fixable defects: A1, A2, A3, A4, B1, B2, C2, E2. Tradeoffs the operator must rule on: A7, C1, D1, E1. Policy-mandated, no correction: E3.` | carried; open | [OBS] |
| 3 | `MutateDirtyFilters.md:5` | `STATUS: SURVIVED M02 — disabling the HOME/.config/git default passes both allowed detectors. Seven of eight mutants were killed; zero probes were inconclusive. This is a coverage finding, not permission to weaken C1.` | carried; resolved@0a70bef (fixture `r-xdg-default`) | [OBS] `r-xdg-default` present in `tests/fixtures/r15-census-config.py:604,1163`; the run result is not observed |
| 4 | `MutateScanConfig.md:2` | `STATUS: Probe complete: 8 single-line mutants; 5 killed, 3 survived (m2, m4, m6: fixture gaps); 0 inconclusive. Every pristine and restored detector run passed. m8 included an observed, bounded FIFO timeout. Scratch restored exactly, then deleted.` | carried; m4, m6 resolved@0a70bef, m2 open | [OBS] `r-inc-tilde-store`, `r-inc-twice` present (fixture lines 446, 466) |
| 5 | `SentinelCommandExec.md:91` | `STATUS: F1 is open; I inferred it from the docs and did not run it. As a result, the C1 statement that "hooksPath/fsmonitor … are inert" does not hold for repos that define a filter key. F2 is a low-severity fail-open. No tool installs or updates.` | carried; resolved@0a70bef (fixture `s-fsm-filter`) | [OBS] `s-fsm-filter` present (fixture lines 405, 1215); run result not observed |
| 6 | `CriticNamespaceWeakening.md:5` | `STATUS: Source review identifies a definite soft-refusal precedence defect and multiple newly exposed access paths; runtime outcomes are [INFERENCE], not measured failures. C1's namespace-retention claim is not established by the supplied matrix.` | carried; resolved@0a70bef (`r-tilde-then-store`) | [OBS] fixture case present (lines 470, 1119) |
| 7 | `RevengeFrozenPin.md:202` | `STATUS: \`b5187351…\` is unattested — no committed blob, no odb object, no reproducible transcript; frozen verdict \`clean\` is unreachable at \`b410186\` and the pin is still unrepaired at \`cbf688ab\`.` | carried; resolved@c6207bd | [REL] re-pin at c6207bd; [PENDING: L1 `--frozen`] |
| 8 | `SrcGitCheckAttr.md:113` | `**STATUS: PROBE RULE breach self-disclosed — one whole-lane recursive grep was run (\`grep -rn 'SOURCES-CONTRACT' /home/vgpnk/Projects/shokunin/souji-shokunin --include=*.md …\`), which the round-16 PROBE RULE forbids; per contract this voids this seat's evidence unless L1 re-derives it. …` | carried; resolved@a6ec781 (S046 re-derived by L1) | [OBS] audit row V-RECURSIVE (`SrcGitCheckAttr`, transcript line 69) |
| 9 | `SrcBashSetN.md:129` | `STATUS: live gnu.org unreachable from this host on 2026-10-20 (curl exit 28, 12-25 s timeouts, both schemes); quote from Wayback capture 20260930073822, edition line from capture 20260927102039, installed GNU Bash 5.3 man page corroborates. …` | carried; open | [OBS] |
| 10 | `CriticGateVacuity.md:140` | `STATUS: gate file absent at review time — findings are against the pinned contract only; the held-out replays A1/A2 are predictions from the regex applied to committed bytes, not gate runs.` | carried; resolved@a6ec781 | [OBS] gate present at HEAD |
| 11 | `DraftLessonGate.md:98` | `STATUS: skeleton only. No C1 or C2 decision is made; the lead must run the measurements and open S043 before the \`## Gate\` is final. Census not run by this seat.` | carried; resolved (superseded) | [OBS] |
| 12 | `SentinelCommandExec.md` (audit) | audit row `V-WRITE-UNKNOWN`, minor, transcript line 118, tool `write`, args empty | not in lesson's list of 12 breach seats | [OBS] audit `census/round-16/seat-audit-w1.json` |

**B. Defect-bearing STATUS text NOT carried by the lesson** (the lesson's claim covers "every failure-channel STATUS line and every non-ok STATUS line that reports a defect"; these do not satisfy it):

| # | source | verbatim STATUS line | why the gate does not flag it | this seat |
|---|---|---|---|---|
| 21 | `RevScanParse.md:206` | `STATUS: no defect in the \`scan_config_file\` key/subsection/variable split; RSP-1 (High) is a real filter-execution bypass in the same \`--list -z\` record idiom, RSP-2 (Medium) is a \`worktreeConfig\` state-model defect, RSP-3 (Low) is a declared-shape contract mismatch. No check was executed against a real repository.` | first word `no` (not in vocabulary) | High severity; [UNVERIFIED at HEAD] |
| 22 | `RevIncludeResolve.md:16` | `` `STATUS: M1 — nested relative includes resolve against the symlink-resolved directory, not the spelled path git uses (`${cfg%/*}`), so the scanned closure can differ from git's in both directions (unguarded read; false whole-run exit 2). L1/L2 are fail-closed over-refusals that still violate the declared "only a protected-namespace reach keeps whole-run exit 2".` `` | backtick-wrapped, so the line-start regex does not match | contradicts C1's exit-2 claim; [UNVERIFIED at HEAD] |
| 23 | `RevBoundFilters.md:36` | `` `STATUS: no check this seat ran failed — bash -n cbf688a rc 0, shellcheck -S warning cbf688a rc 0 (0 findings), b410186 bash -n rc 2 at line 1368 (expected r15 arm, consistent with C1). D1/D2 are unpatched defects in the reviewed revision.` `` | backtick-wrapped | D1 (MEDIUM, newline-suffixed filter value) and D2 (MEDIUM, `info/attributes` not screened) are not in the lesson; [INF] D1 appears addressed at census:991 |
| 24 | `RevFixtureR16Edits.md:237` | `STATUS: review complete (source inspection, no execution). No blocking defect found in the fixture's oracle logic; F1/F2/T1/T2 should land before C1's "for that repo only" and "driver never runs" claims are accepted, and F4 must be re-pinned or retired.` | first word `review` | the C1 claims are conditioned on F1/F2/T1/T2; not carried |
| 25 | `RevGateSpec.md:226` | `STATUS: review complete — no blocking defect in this deliverable; C2's contract needs P1–P9 applied (G1–G6 are pre-adoption blockers) and cannot be green at cbf688a as written.` | first word `review` | G1–G6 blockers; not carried |
| 26 | `RevRedaction.md:214` | `STATUS: no defect found that breaks either fixture oracle; three real but narrow issues (F1 store-path echo on \`..\` input, F2 namespace mislabel/whole-run abort for structural include failures, F3 unredacted \`--compare\` baseline echo), one informational (F4).` | first word `no` | F1–F3 not carried |
| 27 | `RevStatusInfoFile.md:213` | `STATUS: review complete. F1 (MEDIUM, row accuracy) and F6 are fixed in the live worktree; F2 (MEDIUM, whole-run abort on non-protected unresolvable values) is fixed in the live worktree but untested by the fixture; F3/F4/F5 remain live in both cbf688a and the worktree.` | first word `review` | F3/F4/F5 live at cbf688a; not carried |
| 28 | `RevHeaderDocs.md:9` | `` `STATUS: review complete against cbf688a; the worktree copy is NOT the audited bytes (see Basis drift); no census execution performed.` `` | backtick-wrapped | body F2 (MEDIUM) and F5 (MEDIUM) not carried |
| 29 | `RevengeInertKeys.md:245` | `STATUS: r16 fixture docstring still carries the pre-r16 refusal rules at \`tests/fixtures/r15-census-config.py:46-47,61-62\` …; the \`alternateRefsCommand\` inertness proof is fixture-vacuous for the documented alternate-advertisement trigger (no fixture repo has \`objects/info/alternates\`) and unguarded by the selftest source audit (\`tools/souji-census.sh:1729-1731\`).` | carried only as the docstring item (open); the alternateRefsCommand clause is not carried | C1 claims alternateRefsCommand "inert" |
| 30 | `ConnFrontier.md:242` | `STATUS: no check in this seat failed. Known state: no frontier row advances; the F2 live pointer contradicts committed r13 evidence; C2 is not present at this checkpoint (\`tools/souji-landing-gate.py\` absent) and \`census/round-16/c1-matrix.json\` is untracked author output, not acceptance.` | first word `no` | "C2 not present" is stale at HEAD [OBS]; F2 pointer not carried |
| 31 | `ConnQualityCriterion.md:203` | `STATUS: draft complete and paste-ready; \`corpus/QUALITY.md\` intentionally not edited (owned-file bound). Known failure carried: Q25(b) is red at HEAD \`cbf688ab\` until the r15 frozen pin and \`measured_commit\` are re-bound. Tool installs/updates: none.` | first word `draft`; "Known failure carried" is mid-line | [INF] resolved by c6207bd; not carried as resolved |
| 32 | `CriticFixtureOverfit.md:49` | `STATUS: findings advisory. The 05 and 20 oracle fixes are genuine, not fitted. … HARM_CASES omits 18 and 20, which also fail on harm. tools/souji-preservation-evidence.py still holds the r15 class table and was not migrated. Known fa…` (read tool truncated) | first word `findings` | HARM_CASES claim is against an older revision: HEAD HARM set includes R15CFG-18 and R15CFG-20 (fixture lines 163–164) [OBS]; "Known fa…" not carried |
| 33 | `SrcGitConfigIncludesRecheck.md:295` | `STATUS: source re-check complete and S042 still supports its mined claim; no probe was run by this seat. Two claim-level discrepancies recorded for L1: (1) S042's anchor says installed 2.55.0 but the installed man pages declare Git 2.56.0 (TH 2026-09-27); (2) C1's "only a protected-namespace reach keeps whole-run exit 2" is contradicted by \`usage_err\` and by non-namespace \`protected_fail\` classes …` (read tool truncated) | first word `source` | claim-level contradiction of C1 not carried; "no probe was run" conflicts with two audit `V-RECURSIVE` minors (glob calls, transcript lines 95, 119) |
| 34 | `SimplifyCensusDiff.md:332` | `**STATUS: complete — 6 deletions proposed (net −34 lines, parse/lint clean, behaviour-identical by construction), 9 rejected with reasons, plus one verified correction (adjacent #1) and one new correctness finding (D5) from the \`SoujiR16.RevBoundFilters\` exchange. No known failure.**` | first word `complete` | D5 not carried; content not read by this seat |
| 35 | `SrcGitNoLazyFetch.md:69` | `STATUS: no behavioural probe was executed (Q24/R5-compliant); the git binary version is unverified and the 2.55.0→2.56.0 installed-docs discrepancy is reported, not resolved.` | first word `no` | **Self-report contradicted by audit**: 1 major (`V-WRITE-SCOPE`, edit to `.ufo/waves/round-16/r16-placeholder.md`) and 2 minor `V-RECURSIVE` globs over the lane root (transcript lines 49, 62) |
| 36 | `RevengeR15Landing.md:202` | `STATUS: no blocker. One read-only command outside the enumerated allow-list (\`git ls-files\`) and one single-directory \`grep\` over round-15 seat reports are disclosed above; neither touched a forbidden path and neither result carries a claim.` | first word `no` | self-disclosed allow-list breach; audit reports no violation for this seat |

**C. Seat self-disclosures the audit did not flag** (probe-rule breaches disclosed in the seat's own text; evidence treated as void under the contract unless L1 re-derives it):
- `RevMatrixRunner.md:240–244` — two calls outside the enumerated allow-list (`git -C … status --porcelain | head -50`; a `python3 -c` JSON summarizer). Audit: no violation for this seat.
- `ScoutPromisorConsumers.md:112` — one out-of-enumeration probe (`git --version`). Audit: no violation for this seat.
- `RevengeR15Landing.md:202` — see row 36.

**D. Lesson rows checked against source (`corpus/lessons/round-16.md`):** the 11 lesson rows in group A (1–11) appear in the sources above. The lesson quotes several lines with shortened tails; the verbatim first lines are above. [OBS] The lesson's `resolved@` tokens for rows 3–7 and 10 were checked against fixture case presence only; run results were not observed by this seat.

**E. Gate blind spot (calibration, [INF] from source, not run):** the gate's `STATUS_PREFIX_RE` (`tools/souji-landing-gate.py:71`) matches only a line that starts with `STATUS` after optional `#`, `*`, or whitespace; a backtick at line start defeats it (rows 22, 23, 28). Its `FAILURE_STATUS_WORDS` (`:72–78`) only checks the first value word, so rows 21, 24–27, 29–36 pass with zero findings even though they state defects. Under the stated rule, `LG-SEAT-UNCARRIED` cannot fail on those lines. Nine wave-1 reports have no line-start STATUS at all: `LandingGate.md`, `RevBoundFilters.md`, `RevSoftPropagation.md`, `RevHeaderDocs.md`, `RevIncludeResolve.md`, `PlanWalk.md`, `RevMatrixRunner.md`, `SrcPythonAst.md`, `ScoutAltRefsConsumers.md`. Of these, three have a backtick-wrapped STATUS (rows 22, 23, 28); six have none.

## Wave sizes, role mix, dead seats

- **Wave 1 (`souji-r16-w1`):** 65 seats, all transcripts exported (`missing_transcripts: []`), 3173 calls. Role mix by seat-audit record: scout 17, reviewer 14, connector 9, critic 6, scribe 6, revenger 5, executor 3, sentinel 2, mutation-tester 2, simplifier 1 (sum 65) [OBS, agrees with the lesson's Process line]. Reports on disk: 63 `.md` plus `swarm-registry.json` [OBS `.ufo/waves/round-16/w1/` listing].
- **Dead or non-reporting seats (wave 1):** `SentinelStoreAccess` (no report on disk; [REL] provider policy refusal; transcript 6 calls); `PreservationRepin` (no report on disk; [REL] rate-limited, partial checker edit discarded unrun; transcript 43 calls); `LandingGate` (report on disk, no line-start STATUS; [REL] rate-limited after producing the gate file, which L1 measured and revised; transcript 28 calls).
- **Probe-rule breaches (wave 1, audit):** 13 seats with at least one violation. Minor: `ConnLogConvention` (2), `ConnQualityCriterion` (1), `CriticDisclosureR3` (1), `RevFixtureR16Edits` (1), `RevIncludeResolve` (1), `RevListReposDoubleScan` (1), `RevRedaction` (1), `RevSoftPropagation` (1), `SentinelCommandExec` (1, `V-WRITE-UNKNOWN`), `SrcGitCheckAttr` (1), `SrcGitConfigIncludesRecheck` (2), `SrcGitNoLazyFetch` (2), `SrcPythonAst` (4). Major: `SrcGitNoLazyFetch` (1, `V-WRITE-SCOPE`). Evidence from these seats is void under the contract unless L1 re-derives it. The audit is a lower bound, not proof of absence [REL].
- **Wave 2 (`souji-r16-w2`):** registry `.ufo/waves/round-16/w2/swarm-registry.json` (created 2026-10-20T14:57:55Z, updated 15:02:03Z) lists **79 spawn members**: reviewer 28, scout 20, connector 8, critic 7, scribe 6, mutation-tester 4, revenger 3, sentinel 2, simplifier 1 (sum 79; no executor) [OBS]. The registry has no status field, so **dead or cancelled wave-2 seats: [PENDING — L1 from wave-2 transcripts]**. At this seat's read, the wave-2 report directory held only the registry; no wave-2 reports had landed [OBS].
- **Model parameter used:** [PENDING — not recorded in the registry or the artifacts this seat read].

## Tool installs

- **This seat: none.** This seat read `/home/vgpnk/.omp/agent/RULES.md` (the permitted exact-file read) and made no install, upgrade, pacman transaction, or service restart.
- **Round total: none observed.** No install action appears in the artifacts this seat read. [REL] `corpus/lessons/round-16.md` S043 says "installed `bash(1)` GNU Bash 5.3 roff 11467-11468 by L1", which reads as use of the existing man page; [PENDING: L1 confirms it was not a package install.] This seat did not audit every one of the 65 + 79 seat transcripts for installs.

## Open L0 questions

- **Draft L0 (not verified as filed):** `.ufo/waves/round-16/w1/DraftOperatorQuestion.md:7` asks the operator to adjudicate two safety-motivated residual contractions against pre-harm `a31642d`: (a) a repository with a configured `filter.*.clean|smudge|process` driver bound by attributes now reports `status-unverifiable` with no dirty count; (b) a could-not-evaluate config that reaches no protected path now emits one `error` row and no counts. [REL] The lesson says the L0 question was filed; [PENDING: confirm filed and its text].
- **Scope note [INF]:** the draft's items 1–3 (header claim vs. exit 2; `~user` on `core.excludesFile` aborting the whole run; `GIT_NO_LAZY_FETCH` turning a lazy fetch into `status-unverifiable`) are called defects in that draft, not operator questions. The lesson's Residuals list does not include them, and rows 22 and 33 above overlap them. L1 must route them as defects or as L0 scope, not both.

## Commands

Shell commands run by this seat, verbatim, in order (all `git -C … show` / `rev-parse`-class reads on named revisions, plus `sha256sum`; no census, sweep, gate, fixture, or test was executed):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short -- corpus/SOURCES.md corpus/lessons tools census/round-16
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show -s --format=%H%n%cI%n%s 7a79dc2d6e282654b9379c391c4c6be985ccf92c && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show -s --format=%H%n%cI%n%s 0a70beff3becff2c64944595860a31fc6e193076 && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tests/fixtures/r15-census-config.py | sha256sum && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tools/souji-census.sh | sha256sum
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --format=%H%n%s 7a79dc2d6e282654b9379c391c4c6be985ccf92c && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --format=%H%n%s a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae
for r in 0a70beff3becff2c64944595860a31fc6e193076 7a79dc2d6e282654b9379c391c4c6be985ccf92c a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae; do echo "$r"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$r:tests/fixtures/r15-census-config.py" | sha256sum; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$r:tools/souji-census.sh" | sha256sum; done
for r in a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae 7a79dc2d6e282654b9379c391c4c6be985ccf92c 0a70beff3becff2c64944595860a31fc6e193076; do git -C /home/vgpnk/Projects/shokunin/souji-shokunin show -s --format='%H parents=%P %cI %s' "$r"; done; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show -s --format='%H %cI %s' c6207bd; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show -s --format='%H %cI %s' cbf688ab2ab28e38103e5a9417ca525b5f2ed423
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --name-only --format='%H %s' c6207bdac2e0ef52c1da5fbc87dce5d94065972e; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show -s --format=%P c6207bdac2e0ef52c1da5fbc87dce5d94065972e
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools/souji-census.sh tests/fixtures/r15-census-config.py; echo "rc=$?"; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
```

Non-shell reads (exact named files or non-recursive named-directory listings; no recursive search): `/home/vgpnk/.omp/agent/RULES.md`; `census/round-16/seat-audit-w1.json` (ranges); `census/round-16/c1-matrix-final.json` and `census/round-16/c1-matrix-landing.json` (ranges and `?q=` queries); `census/round-16/live-fleet-final.json` (`?q=` queries); `.ufo/waves/round-16/w2/swarm-registry.json` (`?q=` queries); `tools/souji-seat-audit.py` (header); `tools/souji-landing-gate.py` (ranges 1–203); `tools/souji-census.sh` (grep; range 905–963); `tests/fixtures/r15-census-config.py` (grep); `corpus/lessons/round-16.md`; `corpus/README.md`, `corpus/lessons/round-16.md`, `corpus/lessons/round-15.md` (grep); `.ufo/waves/round-16/w1/*` named reports (grep for STATUS; read `DraftReportSkeleton.md`, `DraftOperatorQuestion.md`, `LandingGate.md` tail); non-recursive directory listings `.ufo/waves/round-16/w1`, `.ufo/waves/round-16/w2`, `.ufo/reports/round-16` (fleet root). One grep on `PROTOCOL.md` returned path-not-found; no content was read from it.

STATUS: ok — draft complete; L1-owned fields are marked `[PENDING]` inline. No census, sweep, gate, fixture, test, or install was executed by this seat. Calibration items (rows 21–36, Gate blind spot, PARTIAL R3, measurement caveat) are reported above for L1.
