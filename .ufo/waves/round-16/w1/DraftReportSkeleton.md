# Souji — round 16 report skeleton (DRAFT, unverified)

Status: skeleton only. Every value marked `[PENDING]` is awaiting L1 acceptance output or a seat report. Nothing in this draft is an observed pass. Modeled on `.ufo/reports/round-15/souji.md` (read-only). Target destination named by the assignment: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-16/souji.md`; this file is the scoped draft per the Report trailer and is the only file this seat wrote.

## Work performed

Declared claims (from the round-16 contract; not yet observed):

1. **C1 — operability:** restore the parsing, value/effect-aware census config guard at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (from `cc21683` bytes; r15 `b410186` did not parse). Only a protected-namespace reach keeps whole-run exit 2; could-not-evaluate config degrades to one `error` row for that repo; bound filter drivers skip status for that repo only; hooksPath/fsmonitor/alternateRefsCommand/promisor/partialClone are inert. **Verdict: [PENDING — L1 acceptance run].**
2. **C2 — calibration (lowest axis 7):** new `tools/souji-landing-gate.py` mechanically detects the three r15 landing defects (non-parsing registry script; frozen pin matching no committed bytes; seat-reported known failure not carried verbatim into the round lesson). Red on historical `b410186`, green at round end. Sourced on a SOURCES row opened this round (GNU Bash `set -n`). **Verdict: [PENDING].**

Routed defects (`corpus/lessons/round-15-verifier-spotcheck.md`): R1 parse restore; R2 r14 value-blind harm; R3 carry seat failures verbatim; R4 re-pin r15 preservation frozen pins; R5 enforce seat no-probe rule; R6 cross-domain evidence line; R7 `rejected` registry row for git-status(1). **Per-defect status: [PENDING], one line each.**

Dispatch and mutation/critic work: [PENDING — see wave sizes below].

## Landed changes

| commit | landed work | LOG binding |
|---|---|---|
| `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` | Restored parsing value/effect-aware census (C1); revised `tests/fixtures/r15-census-config.py` | [PENDING: LOG.md line] |
| [PENDING] | `tools/souji-landing-gate.py`, SOURCES row for GNU Bash `set -n`, round-16 lesson and report | [PENDING] |

Verified this seat: `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` resolves and is the repository `HEAD` at the time of this draft (`git rev-parse`, see Commands). Commit subject: `round-16: restore parsing value/effect-aware census; execute and repair config fixture (C1)`. Pushed status: [PENDING].

Baseline for the r15 red check: `b410186cea626a67c92396ac58fbd57fb86876ac` resolves (see Commands).

## Before → after measurements

Counting command (declared by the assignment; NOT executed by this seat — forbidden for seats):
`python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py --changed <rev> --output <new.json>`
Arms: pre-harm `a31642d`, r14-harm `cc21683`, r15-baseline `b410186`, changed. Inputs: `tests/fixtures/r15-census-config.py`, `tests/fixtures/r14-census-boundary.py`, legacy `--selftest`, `bash -n`, `shellcheck`.

| check | declared by assignment at `cbf688ab` | observed by L1 | verdict |
|---|---|---|---|
| r15 config fixture (changed) | 20/20 | [PENDING] | [PENDING] |
| r14 census boundary (changed) | 12/12 | [PENDING] | [PENDING] |
| legacy `--selftest` (changed) | 38/38 | [PENDING] | [PENDING] |
| `bash -n tools/souji-census.sh` | parse clean | [PENDING] | [PENDING] |
| `shellcheck` | — | [PENDING] | [PENDING] |
| r15-baseline `b410186` parse | parse fails (expected red) | [PENDING] | [PENDING] |
| landing gate red on `b410186` / green at round end | — | [PENDING] | [PENDING] |

Legacy scores until L1 acceptance: calibration 7 / operability 8 / coverage 8, numeric deltas 0 [PENDING update].

## Sources & frontier

- Before (round-15 end, `b410186`): 42 rows, A/B/C 38/3/1, mined/queued/rejected 25/15/2 (`census/round-15/end-sources.json`, sha256 `5185720f8dfdf1a9a5e69143e61d1dfe99c3116adc058c7c6768a1217999662d`).
- After (round-16 end): [PENDING — counted by Python Eval reading only `corpus/SOURCES.md`, digest bound].
- New rows this round: GNU Bash `set -n` (opened this round; tier/quote [PENDING]); `rejected` row for git-status(1) (R7) [PENDING].
- Source validation, start and end: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` — exit code and stdout [PENDING both].
- Frontier: [PENDING]. Carry-forward from r15: F2 size attribution, unexercised quarantine sites, K5 HELD, certification OFF.

## Trend verdicts

- **Expansion:** [PENDING].
- **Quality:** [PENDING]. Note: no admitted improvement is inferred from a declared-but-unobserved C1/C2 result.
- **Discernment:** [PENDING]. R6 cross-domain evidence line: [PENDING — one line stating which cross-domain evidence was used and its exact source].

## SHONEN

- [~] Decision tables/error patterns/checklists/sources: [PENDING].
- [~] Historical end-to-end task: [PENDING].
- [~] Instructions: [PENDING — `SKILL.md` must warn of any unverified candidate].
- [~] Domain boundary: `PROVINCE.md` [PENDING unchanged or changed].

## Stale-lane

[PENDING: one line — lane state at round end; whether any other souji round/mission was started.]

## Cross-domain evidence line (R6)

[PENDING: one line, exact source path and revision, or `none`.]

## Seat-reported failures (verbatim, R3)

Each seat's `STATUS:` line is carried verbatim below. Do not paraphrase. Do not upgrade.

| seat | verbatim `STATUS:` line | source report path |
|---|---|---|
| SoujiR16.LandingGate | [PENDING] | [PENDING] |
| SoujiR16.LandingGateFixture | [PENDING] | [PENDING] |
| SoujiR16.PreservationRepin | [PENDING] | [PENDING] |
| SoujiR16.MutateScanConfig | [PENDING] | [PENDING] |
| SoujiR16.MutateDirtyFilters | [PENDING] | [PENDING] |
| SoujiR16.CriticClaimSeparability | [PENDING] | [PENDING] |
| SoujiR16.CriticNoHarmPreharm | [PENDING] | [PENDING] |
| SoujiR16.CriticGateVacuity | [PENDING] | [PENDING] |
| SoujiR16.CriticDisclosureR3 | [PENDING] | [PENDING] |
| SoujiR16.CriticNamespaceWeakening | [PENDING] | [PENDING] |
| SoujiR16.CriticFixtureOverfit | [PENDING] | [PENDING] |
| SoujiR16.SentinelStoreAccess | [PENDING] | [PENDING] |
| SoujiR16.SentinelCommandExec | [PENDING] | [PENDING] |
| SoujiR16.DraftLessonGate / DraftLessonMistakes / DraftSkillSection / DraftOperatorQuestion / DraftR15Correction | [PENDING] | [PENDING] |

## Wave sizes, role mix, dead seats

- Dispatched seats: [PENDING — total].
- Role mix: [PENDING — executor / scribe / scout / connector / reviewer / critic / sentinel / simplifier / revenger / mutation-tester / planner, counts].
- Dead or cancelled seats: [PENDING — name, reason].
- Seats that breached the PROBE RULE (whole-lane or fleet-root grep/glob/find/ls; forbidden commands): [PENDING — name, command class, disclosure; these void that seat's evidence per contract].
- Model parameter used: [PENDING].

## Tool installs

- This seat: **none**. This seat did not read `/home/vgpnk/.omp/agent/RULES.md` (`~/.omp` is a credential store, forbidden to seats) and performed no install, upgrade, pacman transaction, or host-service restart.
- Round total: [PENDING — each seat's installs, with tool, version, channel, reason].

## Open L0 questions

- [PENDING — none filed by this seat.]

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format=%H%n%s cbf688ab2ab28e38103e5a9417ca525b5f2ed423
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse b410186cea626a67c92396ac58fbd57fb86876ac HEAD
```

Non-shell reads: `read` on `/home/vgpnk/Projects/shokunin/.ufo/reports/round-15/souji.md` (exact file, model source); `skill://godspeed`; `read` on `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1` (directory listing of the report directory only, which showed `swarm-registry.json`).

STATUS: draft skeleton complete; all acceptance values pending L1. No census, sweep, or test run was executed by this seat.
