STATUS: DONE — the packed wave has no active executors; all known pre-pack executor targets and sidecars are distinct. D1’s receipt filename remains unspecified.

# Findings

## Scope and basis

The write-scope inventory uses the active `souji-r19-w1b` spec: it sets `reportDir` to `.ufo/waves/round-19/w1/` and contains 68 items, with no item whose role is `executor` (structured projection of `w1b-spec.json`). The original `souji-r19-w1` `w1-spec.json` contains 90 items and 11 executor roles; those executors are absent from the packed spec. I therefore separate (1) active report writes, (2) intended L1 integration targets named by the preregistration and original executor prompts, and (3) the pre-pack executor artifacts, which are not active w1b writes.

There is no explicit `OWN` field in the item objects. Ownership below is derived from each prompt’s named artifact/target and the shared wave `reportDir`. The active items’ non-report paths are read-only inputs, proposal targets, or private scratch/copies; proposal-only prompts explicitly say not to modify the target files.

## Active w1b lane writes: 68 unique reports

Every active item’s report is its own `<reportDir>/<item-name>.md`; the full lane-relative paths are:

- `.ufo/waves/round-19/w1/ScoutCarryCode.md`
- `.ufo/waves/round-19/w1/ScoutCarrySeven.md`
- `.ufo/waves/round-19/w1/ScoutCarryReplay.md`
- `.ufo/waves/round-19/w1/RevCarryVacuity.md`
- `.ufo/waves/round-19/w1/RevCarryRule.md`
- `.ufo/waves/round-19/w1/CriticCarryScope.md`
- `.ufo/waves/round-19/w1/MutCarryEllipsis.md`
- `.ufo/waves/round-19/w1/MutCarryJoin.md`
- `.ufo/waves/round-19/w1/ConnCarryParsers.md`
- `.ufo/waves/round-19/w1/ScoutAuditModel.md`
- `.ufo/waves/round-19/w1/ScoutAuditSignal.md`
- `.ufo/waves/round-19/w1/RevAuditShapes.md`
- `.ufo/waves/round-19/w1/CriticAuditWhitelist.md`
- `.ufo/waves/round-19/w1/MutAuditPatchPath.md`
- `.ufo/waves/round-19/w1/ScoutRevSites.md`
- `.ufo/waves/round-19/w1/ScoutDurableRef.md`
- `.ufo/waves/round-19/w1/RevRevPin.md`
- `.ufo/waves/round-19/w1/CriticRevPin.md`
- `.ufo/waves/round-19/w1/MutRevPin.md`
- `.ufo/waves/round-19/w1/ConnRevPinSiblings.md`
- `.ufo/waves/round-19/w1/ScoutCountClaims.md`
- `.ufo/waves/round-19/w1/ScoutProcCwd.md`
- `.ufo/waves/round-19/w1/ScoutProcFd.md`
- `.ufo/waves/round-19/w1/ScoutProcWchan.md`
- `.ufo/waves/round-19/w1/ScoutProcStatRecheck.md`
- `.ufo/waves/round-19/w1/ScoutProcStatus.md`
- `.ufo/waves/round-19/w1/ScoutKernelSuffix.md`
- `.ufo/waves/round-19/w1/ScribeProcEntry.md`
- `.ufo/waves/round-19/w1/RevProcEntry.md`
- `.ufo/waves/round-19/w1/CriticProcEntry.md`
- `.ufo/waves/round-19/w1/ConnProcAdjacency.md`
- `.ufo/waves/round-19/w1/ScribeProcSkillRow.md`
- `.ufo/waves/round-19/w1/ScoutProcPointers.md`
- `.ufo/waves/round-19/w1/ScoutProcFixtureMap.md`
- `.ufo/waves/round-19/w1/ScoutDefects.md`
- `.ufo/waves/round-19/w1/RevD5.md`
- `.ufo/waves/round-19/w1/CriticD5.md`
- `.ufo/waves/round-19/w1/ScoutD1Receipt.md`
- `.ufo/waves/round-19/w1/ScribeSources.md`
- `.ufo/waves/round-19/w1/RevSourcesQuotes.md`
- `.ufo/waves/round-19/w1/ScoutSourceSearch.md`
- `.ufo/waves/round-19/w1/ScoutS038.md`
- `.ufo/waves/round-19/w1/ScoutKillSession.md`
- `.ufo/waves/round-19/w1/ScoutProcCounter.md`
- `.ufo/waves/round-19/w1/ScoutReportCarry.md`
- `.ufo/waves/round-19/w1/ConnPlanDataWalk.md`
- `.ufo/waves/round-19/w1/ConnClaimSeparability.md`
- `.ufo/waves/round-19/w1/ReviewerClaims.md`
- `.ufo/waves/round-19/w1/CriticRoundAdmission.md`
- `.ufo/waves/round-19/w1/ScoutInherited.md`
- `.ufo/waves/round-19/w1/ScoutWriteScope.md`
- `.ufo/waves/round-19/w1/ScoutQualityMap.md`
- `.ufo/waves/round-19/w1/ConnSiblingOverlap.md`
- `.ufo/waves/round-19/w1/ConnToolsPatterns.md`
- `.ufo/waves/round-19/w1/ConnEvidenceLayout.md`
- `.ufo/waves/round-19/w1/SimplCarryRule.md`
- `.ufo/waves/round-19/w1/SimplRevPin.md`
- `.ufo/waves/round-19/w1/SimplAuditShapes.md`
- `.ufo/waves/round-19/w1/SentinelCarryRegex.md`
- `.ufo/waves/round-19/w1/SentinelWaveContract.md`
- `.ufo/waves/round-19/w1/RevCarryHistory.md`
- `.ufo/waves/round-19/w1/RevHeadIntent.md`
- `.ufo/waves/round-19/w1/RevAuditOrigin.md`
- `.ufo/waves/round-19/w1/ReviewerCarryFixture.md`
- `.ufo/waves/round-19/w1/ReviewerRevPinHelper.md`
- `.ufo/waves/round-19/w1/ReviewerProcEntryPtrs.md`
- `.ufo/waves/round-19/w1/ReviewerGateBaseline.md`
- `.ufo/waves/round-19/w1/ReviewerWavePlan.md`

Each is a distinct leaf path. The active packed spec has no `.patch`/`.py` executor sidecars, so there are no active executor-to-executor ownership collisions.

## Planned integration ownership map

The following lane targets are the disjoint planned integration set named by preregistration and the pre-pack executor briefs. These are target owners, not active w1b direct writes; the executor jobs that emitted sidecars are absent from w1b.

| Claim / item | Unique intended lane target(s) | Ownership / collision note |
|---|---|---|
| C1 / `ExecGateCarry` | `tools/souji-landing-gate.py` | Only carry-gate target owner. |
| C1 / `ExecCarryFixture` | `tests/fixtures/r19-carry-wrap.py` | Unique fixture target. |
| C1 / `ExecAuditShapes` | `tools/souji-seat-audit.py` | Only auditor target owner. |
| C1 / `ExecAuditFixture` | `tests/fixtures/r19-seat-audit-shapes.py` | Unique fixture target. |
| C1 / L1 re-audit | `census/round-19/seat-audit-r18-recheck.json` | Preregistration measurement output, separate from all other r19 records. |
| C2 / `ExecRevHelper` | `tools/souji-rev-pin.py` | Helper has one writer; runner patches consume it, not edit it. |
| C2 / `ExecRunner13` | `census/round-13/run-verification.py`; `census/round-13/count-claims.py` | No other executor owns either file. |
| C2 / `ExecRunner14Wrap` | `census/round-14/run-verification.py`; `census/round-14/run-targeted.py`; `census/round-14/count-claims.py` | These three are unique to this executor. |
| C2 / `ExecRunner14Demo` | `census/round-14/cache-demonstration.py` | Same parent directory as ExecRunner14Wrap, but a different file. |
| C2 / `ExecRevFixture` | `tests/fixtures/r19-rev-pin.py` | Unique fixture target. |
| C3 / L1 integration from proposal-only scribes | `corpus/knowledge/process-residue-observations.md`; `corpus/SOURCES.md`; `corpus/README.md`; `SKILL.md` | `ScribeProcEntry`, `ScribeProcSkillRow`, and `ScribeSources` provide proposals, not direct edits; their target files are distinct. |
| C3 / corrected count record | `census/round-19/counts.json` | Spec correction names this as the byte-level count record. |
| D2 / `ExecD2Pin` | `census/round-19/verify-agreement-pin.py`; `census/round-19/proc-agreement-pinned.json` | Checker target and L1-written record are different files in the same directory. |
| D5 / `ExecD5Recheck` | `tests/fixtures/r15-census-config.py`; `tests/fixtures/r17-census-hygiene.py` | Distinct pre-existing fixture files, unique to D5. |

The pre-pack sidecars, each named uniquely beside its seat report in `.ufo/waves/round-19/w1/`, are: `ExecGateCarry.patch`, `ExecCarryFixture.py`, `ExecAuditShapes.patch`, `ExecAuditFixture.py`, `ExecRevHelper.py`, `ExecRunner13.patch`, `ExecRunner14Wrap.patch`, `ExecRunner14Demo.patch`, `ExecRevFixture.py`, `ExecD2Pin.py`, and `ExecD5Recheck.patch`. No two pre-pack items claim the same sidecar name.

### Collisions and shared paths

- **No same-file write collision** appears among the 11 pre-pack executors’ named lane targets. Likewise, their report/sidecar leaves are unique.
- **Shared directories are non-conflicting:** `tests/fixtures/` contains distinct new C1/C2 fixture names and the two different D5 files; `census/round-14/` has three runner files plus the separate cache demo; `census/round-19/` contains distinct audit, count, D2 checker, and D2 record filenames. The shared report directory uses unique item-name leaves.
- **Dependency, not ownership collision:** ExecRevHelper’s `tools/souji-rev-pin.py` is imported/called by the three C2 runner groups. The single helper owner and its consumers have disjoint write targets.
- **C3/C2 measurement coupling:** the corrected C3 counter invokes `census/round-13/count-claims.py`, which ExecRunner13 is tasked to patch for C2. This is a shared read/measurement dependency, not a second writer; the corrected C3 command supplies an explicit revision, which the C2 brief says to retain.
- **Unresolved D1 path:** `ScoutD1Receipt` asks where a compliant receipt belongs under `census/round-19/` but gives no exact filename. Therefore a completely closed collision check for a future D1 receipt cannot be made until that path is named; it must not be assigned by guess.
- **D3 lesson target not path-qualified:** pre-pack `ScribeD3` names an append-only `LOG.md` correction and a sentence for the r19 lesson but does not state the lesson file path. `LOG.md` is identifiable; I do not infer a lesson filename.

## Other preregistration outputs

C1 targets and records are enumerated at `.ufo/waves/round-19/preregistration.txt:18-31`; C2’s helper, callers, and fixture are at `:40-49`; C3’s knowledge entry/README and counting commands are at `:56-64`. The appended correction explicitly names `census/round-19/counts.json` and changes C3’s measured count from 5→6 to 6→7 (`:79-96`).

## Packed-spec discrepancy

The active spec has 68 items, but `ReviewerWavePlan` still describes the reviewed plan as “90-item” (`.ufo/waves/round-19/w1b-spec.json:544-550`). This is stale plan wording, not an ownership collision; the 68-item `w1b` inventory is the one used above.

# Evidence

- `.ufo/waves/round-19/preregistration.txt:18-31` — C1 gate, fixtures, selftests, and re-audit output.
- `.ufo/waves/round-19/preregistration.txt:40-49` — C2 helper, runner call sites, and fixture.
- `.ufo/waves/round-19/preregistration.txt:56-64,79-96` — C3 entry/README/counting plan and corrected record/path/count.
- `.ufo/waves/round-19/w1b-spec.json:1-6,408-413` — active wave label, report directory, item list, and this item’s requested scope.
- `.ufo/waves/round-19/w1b-spec.json:224-261,312-320` — C3 proposal-only target declarations.
- `.ufo/waves/round-19/w1-spec.json:39-53,128-141,200-237,392-405` — original executor roles, target files, and sidecar delivery names.
- `.ufo/waves/round-19/w1-spec.json:424-437` — pre-pack D3 proposal and D1 receipt task; D1 asks for a census/round-19 location without naming the file.
- Structured JSON projections of `w1b-spec.json` and `w1-spec.json` returned respectively 68 items / zero executor items and 90 items / 11 executors.

# Commands run

No shell, git, test, build, or network commands. Used `grep` to locate spec declarations and line ranges, and `read` JSON projections to enumerate item names, roles, report paths, counts, and executor targets. No source executable was run.

# Contract compliance

- Wrote only `.ufo/waves/round-19/w1/ScoutWriteScope.md`.
- No subagents, git/jj mutation, live census, fleet access, network, signal, scratch files, or tool installs.