# FinalReplayRuntime — round 20

## Result

Calibration move complete on the pinned build. The three authorized fixture commands exited 0. The carry-wrap fixture passed 4/4 with both intended baseline discriminators; the pointer fixture passed 11/11; and the pinned replay runner reported exact semantic matches for all five replay cases. No production code was changed.

One provenance caveat: the replay record reports `expected.gate_sha256_match: false` while `match: true`. The frozen expected gate hash is `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`; the gate bytes at the pinned build hash to `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`. All five replay records have `match: true` and `divergences: []`; the replay runner's semantic verdict compares exit codes and exact `(finding id, path)` multisets, while the hash equality is recorded separately. Therefore this is a byte-pin difference, not a semantic replay divergence; the exact expected gate hash is not the build's gate hash.

## Pinned clone and source digests

- Scratch: `/var/tmp/souji-r20w2-FinalReplayRuntime/lane`
- Branch created: `souji-r20-FinalReplayRuntime`
- Clone default/base branch: `refs/remotes/origin/HEAD` resolved to `refs/remotes/origin/master`; its recorded base revision is `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`
- `git rev-parse HEAD` (branch): `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`
- Base revision: `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`
- Execution caveat: the parent’s per-command Git hook/maintenance neutralization guidance arrived after clone and checkout, so those initial commands were not run with those flags. I did not inspect global/system configuration. Hook/automatic-maintenance suppression cannot be attested retrospectively.
- Source SHA-256 values from the clone:
  - `tests/fixtures/r19-carry-wrap.py`: `a6929c89ee9e4b14c21c287f0c55f76f4c4416f06e0124527f0ef03e976c3d73`
  - `tools/souji-landing-gate.py`: `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`
  - `census/round-17/gate-replays.py`: `c4d5cf6e0276bf4dc979d1641625cc231d84c629fc1fbbfc7b6e504af835bfdc`
  - `tests/fixtures/r18-landing-pointers.py`: `66b503aa0f0f8692ceb3054486d869c1c1fa9ae638a64d5bbe3b1630a76b47ed`

## Executed evidence

1. In the clone: `python3 -B tests/fixtures/r19-carry-wrap.py --tool tools/souji-landing-gate.py` — exit 0; `SUMMARY total=4 failed=0 base_discriminating=2`.
   - Changed gate: unmarked wrapped STATUS cut → exit 1, `LG-SEAT-UNCARRIED`; ellipsis-marked cut, complete paragraph, and wrapped lesson bullet → exit 0, no findings.
   - Baseline gate: unmarked cut → exit 0/no finding (false pass); wrapped lesson bullet → exit 1/`LG-SEAT-UNCARRIED` (false failure). These are the two required discriminators; the two other baseline cases passed.

2. In the clone: `mkdir -p census/round-20 && python3 -B census/round-17/gate-replays.py --gate-rev 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 --output /var/tmp/souji-r20w2-FinalReplayRuntime/lane/census/round-20/final-replay.json` — exit 0. The private JSON record was read for replay tuples and hash values. It records `lane_head` and resolved gate revision as `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1`, gate SHA-256 `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`, `match: true`, and `expected.gate_sha256_match: false`.

   Each row below is the observed `(short rev, round, exit, exact finding-id/path multiset)`; the record says its expected semantic tuple matched exactly (`match: true`, no divergences), and `process_rc` equals `exit` in every row. Full resolved revisions and the recorded counter vector follow.

   - `b410186` (`b410186cea626a67c92396ac58fbd57fb86876ac`), round 15, exit 1: `[(LG-FROZEN-MEASURED, tests/fixtures/r15-preservation-frozen/expected.json) ×2, (LG-FROZEN-PIN, tests/fixtures/r15-preservation-frozen/expected.json), (LG-PARSE-REG, tools/souji-census.sh), (LG-SEAT-UNCARRIED, .ufo/waves/round-15/w1/ConfigRepair.md)]`. Summary vector `(findings, checked_reg, checked_changed, checked_pins, checked_measured, checked_markers, status_lines, carry_heading, checked_reports) = (5,18,0,13,3,1,17,0,64)`.
   - `a31642d` (`a31642d14006830ec62edf40b0354c3699728c4a`), round 13, exit 0: `[]`. Summary vector `(0,10,0,7,0,0,1,0,32)`.
   - `cc21683` (`cc2168325768d5356a82c039dcdf787377c55784`), round 14, exit 0: `[]`. Summary vector `(0,15,0,9,0,0,0,0,32)`.
   - `6ff91f5` (`6ff91f534eece9adde5f667cb7dad400c145351b`), round 16, exit 0: `[]`. Summary vector `(0,21,0,13,3,30,146,1,141)`.
   - `79bbe7a` (`79bbe7a62199260694943ec7186fef6ebff9d41a`), round 16, exit 1: 29 tuples, all with `LG-SEAT-UNCARRIED`, at `.ufo/waves/round-16/w2/` reports `ConnQuality2.md`, `CriticC1NoHarm2.md`, `CriticFixtureRound2.md`, `CriticHonestyAudit.md`, `CriticR4Laundering.md`, `CriticSeparability2.md`, `DraftLogFinal.md`, `DraftMistakesFinal.md`, `DraftTrendVerdicts.md`, `MutateGateCarry.md`, `MutateGateFrozen.md`, `MutateGateParse.md`, `MutateSeatAudit.md`, `ReopenS044.md`, `ReopenS045.md`, `ReopenS048.md`, `RerunGateFixture.md`, `RerunGateReplayR14.md`, `RerunGateSelftest.md`, `RerunLegacySelftest.md`, `RerunSeatAudit.md`, `RevCensusStatusFinal.md`, `RevGateSnapshot.md`, `RevMatrixRunnerFinal.md`, `RevengeSeatViolations.md`, `ScoutLsFilesPathspec.md`, `ScoutOptionalPrefix.md`, `ScoutXdgEmpty.md`, and `SentinelGateSafety.md`. Summary vector `(29,21,0,13,3,30,146,1,141)`.

3. In the clone: `python3 -B tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` — exit 0; `SUMMARY total=11 failed=0`. Exact case verdicts: `skill-uncommitted-target` PASS (exit 1, expected dangling pointer); `knowledge-committed-target` PASS (0); `lesson-line-suffix-resolves` PASS (0); `brace-one-missing` PASS (1, missing member only); `round-range-expands` PASS (0); `placeholder-skipped` PASS (0); `exemption-honored` PASS (0); `malformed-exemption-exit2` PASS (2); `round-17-no-pointer-finding` PASS (0); `historical-b576341-round-18` PASS (observed exit 2 and required minimum findings); `vacuity-stub` PASS (the empty rc-0 stub fails the required finding assertion).

   Scope note: the fixture source has a fixed `LANE` constant for its historical replay, in addition to its synthetic repositories. That subcase ran as part of the explicitly authorized fixture command and reported exit 2 with the required minimum assertions satisfied; its passing verdict is not a claim that the historical gate emitted no other findings.

## Bounded conclusion

The attacked axes were carry-wrap discrimination, pinned replay semantic/count coverage, and pointer handling including malformed-exemption refusal and vacuity resistance. The observed counterexamples are the baseline's unmarked-wrap false pass and wrapped-bullet false failure; the pinned gate fixes both. The five pinned replay semantics match exactly. The only qualification is the separately reported source-hash mismatch against the frozen replay record; no source implementation defect was established by these runs. No tools were installed.
