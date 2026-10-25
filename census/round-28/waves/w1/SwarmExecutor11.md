# SwarmExecutor11 — R28 W1 slice re-derivation report

## Status
STATUS: PASS — re-derived the souji quarantine-slice from the read-only register (data rows: lane/round/id cells) for round 28; slice set and verdicts unchanged vs round 27 (7× payload-absent + S118 unverifiable); zero class changes; both deliverable TSVs staged under w1 for L1 integration.

## Evidence
- Register read in full: `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md` (lines 1–375). Definition (line 6): `A quote the checker could not match is a CANDIDATE, not a verdict.`
- Souji slice rows (lane/round/id): `souji`/r1/S114, r2/S123, r2/S124, r2/S126, r2/S131, r3/S133, r3/S138 — all class `payload-absent` (lines 171–177). By-lane total line 247: `souji` 7.
- NEVER-CHECKED section line 361: `souji`/r1/S118 — source `https://doi.org/10.1109/SEQUEN.1997.666900` unfetchable → unverifiable.
- r27 baseline read: `census/round-27/records/quarantine-slice.tsv` (8 rows) and `census/round-27/records/slice-verdicts.tsv` (8 rows; S114/S123/S124/S126/S131/S133/S138 accepted, S118 unverifiable).
- Comparison: id set identical 8/8; register classes identical → 0 rows changed class since r27. No new souji rows, none dropped.
- Produced (staged in report dir, per leaf-write contract; L1 sole integrator should move to `census/round-28/records/`, matching r27 schema):
  - `.ufo/waves/round-28/w1/quarantine-slice.tsv` (id, verdict; 8 rows)
  - `.ufo/waves/round-28/w1/slice-verdicts.tsv` (id, verdict, note; 8 rows, all carrying S-id)

## Findings
1. Souji slice = 8 rows: S114, S123, S124, S126, S131, S133, S138 = `payload-absent`; S118 = `unverifiable`. Location: register lines 171–177 and 361.
2. No row changed class since r27; verdicts retained unchanged (7 accepted, 1 unverifiable). Notes in `slice-verdicts.tsv` record the register row basis and unchanged status.
3. Deliverables staged under `.ufo/waves/round-28/w1/` (not `census/round-28/records/`): the seat contract limits writes to the report directory; the L1 (only integrator/committer) must integrate the two TSVs to `census/round-28/records/`.
4. Register not edited; no verification fetch performed this run — verdicts rely on register classes and retained r27 verdicts.

## Attack log
None — slice re-derivation is read-only over the register; no counters, predicates, or frozen claims touched.
