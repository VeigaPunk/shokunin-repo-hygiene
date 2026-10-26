# SwarmMutationTester25 — C2 gate mutation probe (souji r30 w2)

## Status
STATUS: PASS — attack ran end-to-end: 10 mutants (>=8 required) against tools/souji-landing-gate.py @ 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8; 9 KILLED with named killing cases, 1 SURVIVED (coverage finding, non-fatal); baseline and restored legs green; lane untouched.

## Evidence
- Target bytes: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py` at tip 9dcd3676, sha256 `ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056`, unchanged after the run (re-hashed); scratch clone `git status --porcelain` = 0 entries; no lane path written except this report and the four receipt files below.
- Detector (identical for pristine / every mutant / restored bytes):
  1. FIXTURE — `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool <gate>` (cases D1-D7 plus the always-zero control emitter).
  2. NOCAP — c2-counter-v2 leg replayed: fresh `--no-local` clone at tip, scratch commit `git rm -rq -- census/round-29/waves`, gate run `--round 29 --fleet-root /home/vgpnk/Projects/shokunin` must print COULD-NOT-EVALUATE.
  3. PTRARM — c2-counter-v2 leg replayed: scratch commit appending the counter's four backticked pointers to corpus/QUALITY.md; LG-DANGLING-PTR lines naming corpus/QUALITY.md must be exactly `census/round-29/r30v2-absent.md` and `.ufo/waves/round-29/w1/R30v2Absent.md` (counter: `want = sorted(["census/round-29/r30v2-absent.md", ".ufo/waves/round-29/w1/R30v2Absent.md"])`).
- Baseline (pristine): fixture `cases=7 pass=7 control=FALSE-GREEN-REJECTED` rc=0; NOCAP rc=2 `COULD-NOT-EVALUATE\tno .md reports under .ufo/waves/round-29/ or census/round-29/waves/ at 5a41f03c4fabc1e41d8592e8e2260b34cfc62a53`; PTRARM flagged exactly the two absent paths, real pointer `.ufo/waves/round-29/w1/SwarmConnector63.md` resolved, zero dangling from other sources.
- Restored: fresh copy of the pristine bytes re-run through the same detector — identical green results (fixture 7/7, NOCAP ok, PTRARM exact).
- Mutants were separate files under scratch; each compiled (`py_compile`) and differed from pristine. Scratch removed after receipts were copied.

## Findings
1. **Coverage gap (non-fatal): the reworded no-reports error message is pinned by no instrument.** Mutant m08 reverted `tools/souji-landing-gate.py:492` `"no .md reports under %s or %s at %s"` to the base form and SURVIVED every leg: fixture D2 asserts only the COULD-NOT-EVALUATE substring, NOCAP asserts the line prefix, PTRARM is untouched, and the selftest's `expect_err` is a substring test satisfied by both forms (`expect_err="no .md reports under"`, gate lines 1453/2226). A1's REGRESS leg drops that text by design: "except that the free-text ` err=<message>` tail of a selftest `CASE` line is dropped". So the only pinned surface is the COULD-NOT-EVALUATE prefix, not the wording — a deliberate A1 exemption, reported as a coverage finding, not a contract violation.
2. **Observation: the discovery fixture alone does not pin the `round-` cut rule.** Mutant m05 (rule at gate line 879 `or part.rstrip("/").endswith("round-")` dropped) passes D1-D7 — no fixture world contains a `round-`-cut token. It is killed only by PTRARM against the lane's own committed bytes: corpus/QUALITY.md:150 carries `pre=g("census/round-"+rd+"/records/preregistration.txt")` and `les=g("corpus/lessons/round-"+rd+".md")`, which become dangling `census/round-` / `corpus/lessons/round-` findings without the rule. The rule holds, but its only behavioral pin lives in lane prose, not the fixture.
3. **Observation (supports the landed C2 claim): the capture fallback is load-bearing at tip.** Dropping it (m09) or rerouting it through the `--fleet-root` disk (m03) makes the gate flag two committed lane pointers, `.ufo/waves/round-29/` and `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`, that the pristine gate resolves through census/round-29/waves/ and census/round-30/waves/ — i.e. BIND's `dangling=0` at tip genuinely depends on the C2 change.

## Attack log
| # | Mutant (behavior-bearing point) | Verdict | Killing case |
|---|---|---|---|
| m01 | drop capture fallback, report discovery (check_carry lines 482-489 removed) | KILLED | FIXTURE: D1 `COULD-NOT-EVALUATE printed; checked_reports=0 want 2` + D7 same |
| m02 | count capture AND wave dir (unconditional concat, double count) | KILLED | FIXTURE: D3 `checked_reports=2 want 1 (double count?)` |
| m03 | map pointers via --fleet-root disk instead of the tree (check_pointers) | KILLED | FIXTURE D6 (`mapped: exit=1 want 0; capture-backed pointer flagged`) and PTRARM (real pointer flagged; 2 lane-level danglings) |
| m04 | TEMPLATE regex dropped (gate line 878) | KILLED | FIXTURE D4 (`template token flagged: round-%s; round-{N}`) and PTRARM (3 flagged != 2) |
| m05 | `round-` cut rule dropped (gate line 879) | KILLED | PTRARM only: flagged gains `census/round-` + `corpus/lessons/round-` from corpus/QUALITY.md:150; fixture passes all 7 |
| m06 | template rule widened to skip any token containing `round-` | KILLED | FIXTURE D5 (`exit=0 want 1`) + D6 both halves; PTRARM flagged_quality=[] != 2 (aux knock-on: LG-DANGLING-PTR-EXEMPT-STALE for the quarantine exemption) |
| m07 | capture mapping without suffix (gate line 916 returns bare `census/<round>/waves`) | KILLED | FIXTURE D6 (`mapped-dir: capture-directory-only resolution`) and PTRARM (absent pointer resolves via bare capture dir, 1 flagged != 2) |
| m08 | error message reverted to base wording | SURVIVED | none — see Finding 1 |
| m09 | drop capture fallback, pointer resolution (check_pointers lines 1002-1006 removed) | KILLED | FIXTURE D6 (`mapped: capture-backed pointer flagged`) and PTRARM (real pointer flagged) |
| m10 | bonus: capture mapping bound to the evaluated round instead of the pointer's own round (D6's anti-shortcut pin) | KILLED | FIXTURE D6 (`mapped-missing: uncaptured pointer not flagged` — resolved by the evaluated round's capture) |

Per attacked item: NOCAP leg HOLDS for all mutants (every mutant still prints COULD-NOT-EVALUATE with the capture deleted — the leg alone cannot distinguish a capture-reading gate, exactly why the fixture's D1 is needed); PTRARM leg HOLDS as a killer for m03-m07, m09; FIXTURE HOLDS as a killer for m01, m02, m04, m06, m07, m09, m10. No mutant was inconclusive; no baseline failure occurred.

## Deliveries
- `.ufo/waves/round-30/w2/SwarmMutationTester25.md` (this report)
- `.ufo/waves/round-30/w2/SwarmMutationTester25-mutate.py` (mutant generator + detector harness; regenerates all 10 mutants deterministically)
- `.ufo/waves/round-30/w2/SwarmMutationTester25-pristine.json` (baseline detector output)
- `.ufo/waves/round-30/w2/SwarmMutationTester25-mutants.json` (per-mutant detector output)
- `.ufo/waves/round-30/w2/SwarmMutationTester25-restored.json` (restored-bytes detector output)
