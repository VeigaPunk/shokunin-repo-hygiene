# SwarmSimplifier36 — wave-2 spec hygiene (round 31, wave 2)

## Status
STATUS: PARTIAL — every mandatory gate in the assigned check list passes (36 distinct items/prompts, all roles in the fleet allowlist, flash 24/36 = 66.7 % >= 50 %, attack 18/36 = 50 % >= 25 %, all scratch paths per-item, 28 output deliveries with no collision, no item runs the slow C1 counter concurrently with itself), but four item prompts carry relative lane paths, the frozen-contract sentence names A0-A4 while A5 is in force and governs the C2 counter, and seven C2 items run a gate that writes outside the mandated scratch root.

## Evidence

Revisions read: lane master/HEAD `2c16d018e40db7c23420a2c3bb546b52957bcc25` (equals the tip rendered in the dispatch), base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; C1 `24f343c8…`, C2 `8024b540…`, C3 `1baf4da0…`, M1 `c6108301…` all `merge-base --is-ancestor` of the tip (four `-anc` lines printed).

```
$ python3 -B … (w2-spec.json / w2-dispatch.json)
spec items 36 ; roles Counter({'critic':10,'executor':6,'scribe':6,'reviewer':5,
  'mutation-tester':3,'scout':2,'connector':2,'sentinel':1,'simplifier':1})
flash = 6+6+10+1+0+1 = 24 -> 66.7 %   attack = 5+10+3 = 18 -> 50.0 %
unique names 36 36 ; unique tasks 36 ; registry items unique 36 36
spec prompts not embedded exactly once: [] count 0
well-formed tasks 36 of 36   (prefix /skill:godspeed, prompt, Lane bounds, Report trailer)
all agents allowed True      (policy nativeProfiles.omp-native-v1.proposalRoles)
```
Dispatch `counts` spawn 36 / resume 0, `resumeSends` empty, policy maxLanes 64, waveMinLanes 32 (36 ∈ 32..64); w1 38 + w2 36 = 74 seats ∈ 64..100. Wave-1 dispatches likewise carry `resume: 0` (precedent for no addendum sequencing).

Absolute/scratch paths and scope:
```
$ python3 -B … /fast/scratch refs not under /fast/scratch/hyaku/souji-r31/  -> []
per-item scratch binding: ReRunC1->w2-ReRunC1/cnt OK, AttackC1Amended->w2-AttackC1Amended/ OK,
  MutateC1A4, ReRunC2, MutateGate, AttackC2Amended, ReRunC3, ReplicateC3, MutateFixture all OK
deliver collisions among outputs: none (the only repeated token is the W1 *input* deliver-assim-sweep.md,
  read by SwarmScribe32 and SwarmScribe34)
output deliveries: 28 distinct, all under .ufo/waves/round-31/w2/; 12 items name no delivery file
Report trailers: .ufo/waves/round-31/w2/<TaskName>.md, all 36 match their task name
```
Write scope: no prompt asks for a write in the lane outside `w2/`; every mutation instruction says "scratch clone" or "deliver …". `sources-census.sh` (SwarmReviewer22) is self-declared read-only (`writes only stdout or --out`), `validate` is a documented mode.

C1-concurrency check:
```
$ awk '/### Round 31 capability-cell supersessions/,0' SCORECARD.md | grep -c 'run: ' -> 20
$ … | grep -o 'run: [^|]*'  -> no invocation of tools/souji-capability-cells.py
ReRunC1: "Re-run C1 serially: … then run the current counter at <C1L> a second time"
tools/souji-capability-cells.py:191  work = tempfile.mkdtemp(prefix="c1.", dir=a.scratch)
```
→ no item asks for two counter copies at once; the per-invocation mkdtemp also makes the shared `--scratch …/w2-ReRunC1/cnt` non-colliding.

## Findings

1. **Amendment set understated: A0-A4 named, A5 in force.** Location: `w2-dispatch.json` taskCall.context, paragraph 1 ("stricter amendments A0-A4 in …/amendments.txt (read both FIRST)"); the C2 bullet mentions A5 only in parentheses. `census/round-31/records/amendments.txt:47` is `A5 — 2026-10-26T04:22:47-03:00`, and the C2 counter the seats must run is `c2-counter-v3.py`, i.e. A5's. A seat that treats "A0-A4" as the closed contract set under-reads the counter it is told to run. Harmed axis: calibration (frozen-contract fidelity). Items: all 36; directly SwarmExecutor09, SwarmReviewer10, SwarmMutationTester11, SwarmCritic12, SwarmReviewer13, SwarmCritic14, SwarmExecutor15.
2. **SwarmScribe32 (LessonDraft) repeats the omission**: "`## Findings` (…, amendments A0-A4 with the attacks that triggered them, M1)". The round-31 lesson draft would omit A5 and the wave-1 attack (SwarmReviewer26) that forced it. Harmed axis: calibration.
3. **Relative lane paths in four item prompts** (the wave contract says absolute paths only; seat tools start at the fleet root, so each resolves to a nonexistent `/home/vgpnk/Projects/shokunin/<path>`):
   - SwarmCritic04: "retained in census/round-21 and L27/L28 bound to census/round-21/final-code-verification.json" and "search census/round-20 and census/round-21 for the remote-source run's count" (both directories and the file do exist under the lane — the path, not the file, is the defect).
   - SwarmExecutor16: "census/round-31/c3-counter-v2.py" beside the absolute v1 and v3 siblings.
   - SwarmExecutor27: "tests/fixtures/*" and "run tools/souji-registry-agreement.py, tools/souji-coverage-agreement.py, tools/souji-declared-evidence.py at both revs".
   - SwarmMutationTester11: "run tests/fixtures/r31-landing-gate-precision.py and /home/…/census/round-31/c2-counter-v3.py against each mutant".
   Harmed axis: operability 8 (a wrong-path run either fails or, worse, is reported as a finding). Not defects, checked: `git -C <abs> diff … -- tools/…` pathspecs and `{BASE}:corpus/…` rev:path forms are repo-relative by construction, and the `Report:` trailer is relative by the context's own definition.
4. **The gate writes `/var/tmp`, outside the wave's scratch root.** `tools/souji-landing-gate.py:1182` `snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")`, `:1499` the same for `--selftest`, disclosed at `:25` and in the fixture docstring at `tests/fixtures/r31-landing-gate-precision.py:60`. The wave contract allows only `/fast/scratch/hyaku/souji-r31/w2-<ItemId>/` and `/tmp` under 50 MB, and the HARD BOUND forbids deleting what a seat did not create; every gate-running item therefore creates and removes directories in a path the contract does not mention. Items: SwarmExecutor09, SwarmReviewer10, SwarmMutationTester11, SwarmCritic12, SwarmReviewer13, SwarmCritic14, SwarmExecutor15. Harmed axis: operability (the L1 already lists "/var/tmp in the gate" as an r32 residual, but the wave text neither exempts nor authorizes it).
5. **SwarmExecutor09 (ReRunC2) omits c2-counter-v2.py**: it runs v1 and v3 only, so amendment A3's exact v2 reading is not re-derived at the tip. A5 defines v3 as "v2 with every SHIFT probe drawn at random per run", so v3's legs contain v2's mechanism, but the literal v2 target string is unmeasured at `2c16d018…`. Harmed axis: calibration (one frozen target's reading is inferred, not observed).
6. **The executor lane-bounds clause permits a labrat without withholding the slow counters**: six executor items carry "no subagent dispatch except your single labrat", while SwarmExecutor01's serial instruction ("Re-run C1 serially") binds only the seat text. An executor that hands one counter invocation to its labrat produces exactly the two-parallel-runs condition the item is written to detect; work-dir collision is avoided by the counter's mkdtemp, CPU contention is not. Items: SwarmExecutor01 (C1), also 09/15/16/17/27. Harmed axis: operability (self-induced nondeterminism in a re-derivation item).
7. **Twelve items name no delivery file** (evidence lives only in their reports): AttackC1Amended, MutateC1A4, MutateGate, AttackC2Amended, FixtureContract, EntrySentences, ReopenSources, MutateFixture, SiblingOverlap2, CrossClaim2, CredScan2, SpecHygiene2. Contractually allowed ("if your item names one"), so not a violation of the stated check; flagged because wave-2's purpose is integration input and these twelve are the pure-falsification seats. Harmed axis: none directly; operability at the integration step.
8. **Generator bookkeeping miscounts** in `make-spec-w2.py`: `:63` `# ---------------- C1 (9)` holds 8 `add(` calls; `:80` `# ---------------- C3 (9)` holds 8; `:92` `# ---------------- cross-cutting (9)` holds 10 (`C2 (7)` and `M1 (3)` are correct). The comments imply 37 items, the file renders 36. Harmed axis: calibration (the wave's own count bookkeeping).
9. **Generator assertions cover four of the eight checks**: `:106` distinct item ids/prompts, `:109` 32..64 items, flash*2>=n, attack*4>=n. Nothing asserts the role allowlist, absolute paths, per-item scratch binding, delivery-file uniqueness, or the C1-concurrency rule, so each can regress silently (this wave's findings 3 and 4 would have passed unchanged). Harmed axis: calibration/operability of the wave pipeline, not this wave's claims.

Not a defect, verified: 24 inputs reference same-wave wave-1 deliveries, and wave 1 also ran with `resume: 0`; SwarmScribe23 (C3Corrections) is the only item reading *same-wave* wave-2 reports ("read the wave-2 attack reports that exist in <w2>/ when you start and finish"), which is hedged by its own wording and matches wave-1's practice of reading peer deliveries without sequencing — residual scheduling risk only.

## Attack log
- Tried to find two items writing one file: 28 output names, all distinct; the only repeated `deliver-` token is a wave-1 input read by SwarmScribe32 and SwarmScribe34.
- Tried to find duplicate ids/prompts: 36/36 unique; normalizing digits/hex/labels collapses only AuditCarryR26/R27/R28, which differ by round, entry count and git range (intentional).
- Tried to find an item that runs the C1 counter twice at once: enumerated all 20 `run:` rows of the supersession block (none invokes `souji-capability-cells.py`), read ReRunC1's five invocations ("serially", second run after the first), and confirmed the counter mkdtemps inside `--scratch`.
- Tried to find a role outside the fleet allowlist: all nine used roles are in `nativeProfiles.omp-native-v1.proposalRoles`; sentinel is absent from the policy `lanes` roster but present in proposalRoles and in wave 1 (SwarmSentinel37), so accepted.
- Tried to find a write outside `w2/` + scratch: every mutation instruction is "scratch clone" or a `deliver-` file; the only outside-root write is the disclosed gate `/var/tmp`.
- Tried to find a false premise: all referenced records (`c1-before/c1-after-*`, `c2-after-v1/v2/v3`, `m1-red-before`, `jj-object-clock-run`), tools, counters, controls, wave-1 deliveries and the round-30 report exist; every `--only`/`--scratch`/`--round`/`--fleet-root`/`--selftest`/`--json` flag used by the prompts exists in the tool `--help`; SCORECARD line spans 143-176/309-315/350-356 are the capability tables the enumeration-gap item names.
- Tried to find scratch collisions between items: all nine rendered scratch roots are `w2-<own item>/`.

## Deliveries
None (this item names no delivery file). Scratch `/fast/scratch/hyaku/souji-r31/w2-SpecHygiene2/` removed; nothing written in the lane except this report.
