# SwarmMutationTester32 — C1 counter mutation test (round 31, wave 1)

Item: mutation-test `tools/souji-capability-cells.py` in scratch
(`/fast/scratch/hyaku/souji-r31/MutateC1Counter/`). Lane read-only; no lane
bytes were modified. Tooling: python 3.14.8, git 2.56.0; nothing installed
(no pacman, no new tools).

## Status
STATUS: PASS — all 10 mandated mutants were killed by a committed-control-equivalent
state or a purpose-built scratch state; zero survivors; the frozen base control
(`C1-do-nothing(base)`) is reproduced byte-identical by pristine and by every mutant.

## Evidence

### Baseline reproduction (control `C1-do-nothing(base)`)
Command: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-cells.py --root <scratch clone of lane> --rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`
Output (rc=1): `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`
— identical to `census/round-31/records/controls.tsv` line 2. All ten mutants
produce the same SUMMARY line byte-for-byte on this state (none disturbs the
frozen base behavior).

### Committed junk-control revs are unreachable
The five `C1-junk*` revs recorded in `controls.tsv` (42c0018f…, 8af12a02…,
9749c995…, 84b931f1…, d9bcb0e6…) do not exist in a fresh clone of the lane
(`git cat-file -e <rev>^{commit}` fails for each), and `/fast/scratch/hyaku/souji-r31/L1controls/`
is empty. Equivalent states were therefore recreated; pristine on each recreated
state reproduces the recorded control SUMMARY modulo the `rev=` field
(`items=1 … mismatches=1 partial=1`).

### Matrix
11 programs (pristine + m1..m10) × 11 states (do-nothing + 10 adversarial) =
121 runs, `--scratch` fresh per run, all `python3 -B`. Each adversarial state
is a scratch clone (origin removed) with a synthetic base (= lane-base tree plus
fixture/record files) and a tip that appends one supersession row (or edits in
place for S-inplace).

| mutant (defect) | kill state | pristine verdict → mutant verdict |
|---|---|---|
| m1 drop append-only guard (lines 159, 209) | S-inplace (≡ C1-junk5) | `MISMATCH(append-only-violated)` → L30 base-cell `MATCH` (`bound_run=1`, `mismatches=0`) |
| m2 accept record not at base (lines 255-257) | S-newrec (≡ C1-junk3) | `BAD-ROW(record-not-unchanged-base-blob)` → `MATCH` (`bound_record=1`, `mismatches=0`) |
| m3 drop waves/transcripts exclusion (lines 247-248) | S-waves (≡ C1-junk1) | `BAD-ROW(record-shape)` → `MATCH` (`bound_record=1`) |
| m4 drop round-set check (line 246) | S-roundset | `BAD-ROW(record-shape)` → `MATCH` (`bound_record=1`) |
| m5 drop integer-multiset check (line 249) | S-multiset (≡ C1-junk4) | `BAD-ROW(record-shape)` → `MATCH` (`bound_record=1`) |
| m6 drop stem-on-line rule (line 229) | S-foreignstem (≡ C1-junk2) | `BAD-ROW(run-shape)` → `MATCH` (`bound_run=1`) |
| m7 drop literal-not-in-argv (line 231) | S-argvlit | `BAD-ROW(run-shape)` → `MATCH` (`bound_run=1`) |
| m8 accept rc!=0 (lines 237, 262) | S-rcfail | `RUN-MISMATCH` (rc=3, observed=`TOTAL 18/18`) → `MATCH` (`bound_run=1`) |
| m9 plain substring match, no digit boundaries (line 102) | S-substr | `RECORD-MISMATCH` → `MATCH` (`bound_record=1`) |
| m10 let R30-CORRECTION lines bind (lines 53-57) | S-r30 | L37 `UNBOUND` (`mismatches=1`) → `MATCH` (`bound_record=1`) |

Representative ITEM lines (mutant side):
- m8: `ITEM L06 SCORECARD.md:158 literal=18/18 superseded binding=run MATCH bash tests/fixtures/toy-fail-print.sh rc=3 observed=TOTAL 18/18`
- m7: `ITEM L06 SCORECARD.md:158 literal=18/18 superseded binding=run MATCH bash tests/fixtures/toy-print.sh 18/18 rc=0 observed=TOTAL 18/18`
- m10: `ITEM L37 SCORECARD.md:313 literal=8/20 superseded binding=record MATCH census/round-29/rec-r30.txt`
- m3: `ITEM L36 SCORECARD.md:313 literal=cases=20 pass=20 superseded binding=record MATCH census/round-29/waves/w1/rec.txt`

### Restoration evidence
MD5 at creation vs after all runs, identical: pristine `6a4aa0e794410dff25f6a50c2e74ea53`; m1 `ad6bab22d9929abba84baca8fecf3bf0`; m2 `66c1a78659276f440ea753e6117e011a`; m3 `61aa51850aedfb8573be62157bb515e4`; m4 `cb2ae9e931f92a9564ef436eec0884c4`; m5 `492446f5aadbb7c5e1f49fe239ffdd31`; m6 `5ce9a4be1b887e7b141c9b3b68dfac6f`; m7 `5512540934cbc9a734339660ec339f2e`; m8 `b4c4ed847f5a7e4333d611f171c2f007`; m9 `5db7c80788bc5c40dde4996a92b05111`; m10 `346fce3fc7a63c4896283f7e6167cd89`. The lane tool file was never written to.

## Findings
1. No survivor: every tested check is behavior-bearing. The append-only guard,
record-at-base blob equality, waves/transcripts path exclusion, round-set
membership, record integer-multiset, run stem-on-line, literal-not-in-argv,
rc=0, digit-boundary matching, and R30-row rejection each flip an observable
verdict when removed.
2. The record branch (line 249) enforces integer-multiset equality with the base
literal; the run branch does not — see Attack log.
3. Test-harness correction: my first S-rcfail build appended stem token
`(toy-print)` while the script was `toy-fail-print.sh`, so the pristine state was
`BAD-ROW(run-shape)` — not the intended `RUN-MISMATCH`. Rebuilt with
`(toy-fail-print)` on line 158; after rebuild m8 is killed (rc=0 vs pristine
rc=1). Pristine on the rebuilt state yields `RUN-MISMATCH … rc=3 observed=TOTAL 18/18`.
4. Junk-control revs are not in the lane repo (and the L1 scratch controls dir
is empty); the control table pins only outputs. Recreated equivalent states match
the recorded outputs exactly, but the original five control commits cannot be
re-run by a later seat.

## Attack log
ATTACK (reproduced): the superseding RUN-row binding never compares the row's
literal integers with the enumerated item's base literal (only `len(ints(lit)) >= 2`
at line 221; cf. record branch line 249). A tail row may therefore re-state an
item's literal as different integers and be counted `bound_run` the moment a
command prints those numbers.

Reproduced state (scratch, still present this session): synthetic base
`94b53321f7ee5f9ea163f3fb225c559de4265275` adds
`tests/fixtures/toy-restate.sh` (prints `cases=21 pass=21`; stem `toy-restate`
appended to SCORECARD.md line 313); tip `383c3f6406ceb6ba39fcdad17d38d2a6f23cb651`
appends row `| L36 | SCORECARD.md:313 | cases=21 pass=21 | run: bash tests/fixtures/toy-restate.sh |`.
Pristine counter, `--only L36`:
`ITEM L36 SCORECARD.md:313 literal=cases=21 pass=21 superseded binding=run MATCH bash tests/fixtures/toy-restate.sh rc=0 observed=cases=21 pass=21`
`SUMMARY items=1 bound_run=1 bound_record=0 unbound=0 mismatches=0 partial=1 rev=383c3f6406ceb6ba39fcdad17d38d2a6f23cb651`
(rc=0), although the enumerated L36 base literal is `cases=20 pass=20`
(`census/round-31/c1-cells.tsv` line 46). Closing asymmetry: apply the same
integer-multiset guard to the run branch (stricter-only amendment; not proposed
as a counter change).

## Deliveries
- `census/round-31/waves/w1/SwarmMutationTester32.md` (this report) at
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/SwarmMutationTester32.md`.
- No other files delivered; scratch removed on completion.
