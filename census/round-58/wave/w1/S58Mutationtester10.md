# S58Mutationtester10 — bounded mutation probes

Axes: detector discrimination; exact-byte restoration; scratch confinement. Frozen predicate: e7f64f30324e8ddb3f2266302daa9066054cdbb3. No Markdown-repair claim, integration judgment, or production edit.

## Result

Seven independent mutants killed by their assigned bounded detector, no survivors. C2 final implementation tested at SHA256 `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`; independent acceptance SHA256 `55b5e063fa57a02d7fcf186c9d8e9b719b0ecb76b08001ad0988ad76aa3fc82e`.

| Mutant | Expected detector | Observed pristine / mutant / restored EXIT | Verdict |
|---|---|---|---|
| Bypass path_finding with `unconfined = None` | Independent executor02 eight-case acceptance | 0 / 1 / 0; absolute, traversal, parent-symlink all wrongly return 0/no findings | killed |
| Delete raw cat-file type comparison | Same acceptance | 0 / 1 / 0; annotated tag object wrongly returns 0/no findings | killed |
| Delete conflicting-revision refusal | Same acceptance | 0 / 1 / 0; conflict wrongly returns 0/no findings | killed |
| Delete selftest rc equality | Selftest must reject fixed oracle with REV-OK expected rc changed 0→1 | 1 / 0 / 1 | killed |
| Replace full-finding equality with ID-only equality | Selftest must reject fixed oracle with NO-EXIT expected detail changed receipts/noexit.txt→receipts/wrong.txt | 1 / 0 / 1 | killed |
| Delete rowset extra/missing failure | Selftest must reject fixed oracle with EXTRA-UNBUILT row | 1 / 0 / 1 | killed |
| Set C1 `mismatches = 0` | Executor03 five-leg detector, own copy with isolated paths and counter injection | 0 / 1 / 0; mutant base returns 0 where detector expects 1 | killed |

Selftest adverse-oracle probes deliberately expect EXIT 1: a pristine refusal is detector success, not a baseline failure. All three adverse expectation tables are retained, identical across pristine/mutated/restored runs. They supplement independent receipt acceptance; that eight-case interface detector does not itself exercise selftest comparison guards. The two rc0 selftest controls are not being mistaken for failures in the contract.

All three honest r57 receipts remain clean in every final C2 interface run, including mutants. Pristine/restored acceptance observes all five named refusals and all three clean receipts. C1 pristine/restored output: `PASS base=2 append=0 delete-note-1=1 delete-note-2=1 junk=2`. C1 mutant is stopped by the base leg; append/delete/junk legs are therefore unrun on mutant, not claimed individually killed.

## Evidence

All paths below are relative to this report's sibling directory `S58Mutationtester10/`:

- `c2-final-pristine.txt`, `c2-final-no-path.txt`, `c2-final-path-restored.txt`, `c2-final-no-type.txt`, `c2-final-type-restored.txt`, `c2-final-no-conflict.txt`, `c2-final-conflict-restored.txt`: observed argv, complete JSON output, nested commands/output/EXIT and outer EXIT.
- `self-{rc,full,rowset}-{final-pristine,mutated,restored}.txt`: exact selftest invocation, full finding output, EXIT. All pristine/restored challenge runs reject; removed guards falsely accept.
- `c1-{pristine,always-zero,restored}.txt` plus matching subdirectories' `receipts.txt`: observed commands, stdout/stderr/EXIT, guarded scratch Git fixture commands. `c1-mutation.json` holds hashes and traceback.
- `c2-mutations.json`, `selftest-mutations.json`: per-leg hashes and observed results. `restoration.json`: exact-byte equality and removal evidence.
- Final original `c2-gate.py`, `c2-acceptance.py`, `c2-selftest-expected.tsv`, `c1-counter.py`, isolated `c1-tests.py`, and three adverse expected tables retained for reproduction. The C1 test copy changes only scratch/delivery constants and replaces extracted counter bytes before fixture construction.

Final mutant SHA256 values:

| Mutant | SHA256 |
|---|---|
| no-path | bda3d60f55112f48a79c2dd9799c534921a3844ab8e8e57366379eb2cde05e57 |
| no-type | 00411e7d4d713744df968428d3af33d788ac45b9c61cfd84ab765f903fff0568 |
| no-conflict | a9d6824ad2b68f1780bd4fa8146fdb0ba4b0e2eecf618f452fcf479881b98ec2 |
| no-selftest-rc | 67236e2a71e2307a7a095968cde3dd0efd677005613e0d72854e0a1542cc70b3 |
| ID-only-findings | f6456fdcbccf8d43d30dd1b4280e7c44cd3af26260f0a4803d9b0fbbe09d075c |
| no-rowset-guard | bea1b7690ba4b0647e8ec9d923b96dd714a1ceca410a7d5c43e8a9e3d98acff1 |
| C1-always-zero | c45ea5713dfafae28e6f7b646b464c13622ecbf3f5e5b4877f5c1e9b59d1503b |

## Provenance and limits

Initial `c2-pristine.txt` is **inconclusive setup error**, not a killed mutant: a raw read copied a displayed truncation footer into scratch, producing SyntaxError. The copy was replaced with complete source bytes; the complete baseline passed. Evidence retained rather than overwritten. Source then changed under explicit planner-authorized executor revisions; earlier 7c35d3... runs are retained but superseded by every `final-*` interface run and final selftest guard runs. Final executor freeze was acknowledged before completion.

C1 original/restored SHA256: `52ccdb1be66dd8379fb7bf81eae7e28965f156aa50e1e4573b82adb23bd0dea7`. C2 original/restored SHA256: `56f2a31163035726f1190db3e6b827fc121602377e187d16a54a6ae8f15af543`. Both exact byte comparisons true after restoration. Own scratch removed only after copying evidence; `scratch_exists_after=false`. Historical counters and production unchanged. No installs, services, builds, lint, formatters, commits/pushes to source, sibling writes, or other runtime. Fixture Git mutations used explicit -C and guarded toplevel; fixture-only environment identity did not modify global identity.

Self-evaluation: accuracy 4 (setup-error evidence explicitly excluded); completeness 5 (all seven probes, baseline and restoration); clarity 4 (superseded evidence adds noise); actionability 4 (reproduction requires recreating own scratch paths); conciseness 4 (full hashes retained for audit). Overall 4.2. Improvements: use exact file copies initially; freeze implementation before mutation wave. User agreement check: bounded seven-mutant result, not a claim about universal gate correctness.

Report: .ufo/waves/round-58/w1/S58Mutationtester10.md
