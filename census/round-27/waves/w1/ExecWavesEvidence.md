## Status
STATUS: PASS — w1 evidence files prepared: `w1-validate.out` byte-copied into w1/, spec sha256 recorded, `wave-note.md` drafted with policy band, spawn count and role histogram.

## Evidence
- `cp .ufo/waves/round-27/w1-validate.out .ufo/waves/round-27/w1/w1-validate.out`; sha256 source == dest == `40137d45ce6641bcc7be2f9944b0702a2d86ac154a097c213f2f123f141d734e` (run 2026-10-25).
- `sha256sum .ufo/waves/round-27/w1-spec.json` → `682129e4e0fbef4f14e7c41ddbb6797ec0bb669e2857f40190d2b4e589ba1a55`; spec: 79 items, `wave=souji-r27-w1`, `reportDir=.ufo/waves/round-27/w1`, `maxLanes=100`.
- w1-validate.out parsed (python3 -B): `schema=ufo-swarm-wave-v1`; `counts={spawn:79, resume:0, total:79}`; `policy={waveMinLanes:64, waveMaxLanes:128, maxLanes:100, declaredMaxLanes:100, hardCeiling:256}`; `dispatch={calls:1, kind:task}`; registry `members=79`.
- Role histogram (from `registry.members`): connector 3, scout 11, executor 25, reviewer 12, critic 10, mutation-tester 6, simplifier 3, revenger 1, scribe 8 (sum 79).
- Cross-check: registry member name set == spec item name set (79/79); `counts.spawn == len(members)`.
- Validator NOT run by me (L1's plan output from 2026-10-25T14:53:28 reused byte-for-byte); no tool installs performed.

## Findings
1. The L1's plan-validation output exists at `.ufo/waves/round-27/w1-validate.out` (mtime 2026-10-25T14:53:28, valid ufo-swarm-wave-v1 JSON); it is the `node ... ufo-swarm-wave.mjs plan --spec <spec>` output and was byte-copied to `w1/w1-validate.out`.
2. Spec sha256 `682129e4...ba1a55` recorded in `wave-note.md`; dispatch summary (policy band 64–128, spawn 79, role histogram) recorded there too.
3. Dispatch counts are internally consistent: spawn 79 == registry members 79 == spec items 79; resume 0; one task call, zero hub sends.
