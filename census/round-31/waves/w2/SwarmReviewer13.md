# SwarmReviewer13 — w2 — audit of tests/fixtures/r31-landing-gate-precision.py vs frozen C2 G1-G10

## Status

STATUS: PASS — the fixture builds the ten frozen contract worlds faithfully, every judge enforces exactly its prereg iff-clause, the always-zero control is real and is rejected, all four TMPDIR refusals fire with exit 2, the tip run reproduces `fixture=ok`, and the base-gate blob meets the prereg REDARM per-case split exactly. Findings below are latent precision gaps in the fixture's G9 judge and two cosmetic notes; none masks a live gate defect at tip 2c16d018e40db7c23420a2c3bb546b52957bcc25.

## Evidence

Revisions: lane base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; preregistration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525; C2 landing 8024b540b04d677d47cf51a0d1132ec8705ef14a; tip 2c16d018e40db7c23420a2c3bb546b52957bcc25 (branch master).

- Identity: `git -C <lane> diff --stat 8024b540..2c16d018 -- tests/fixtures/r31-landing-gate-precision.py` empty; `git status --porcelain` on the fixture and tools/souji-landing-gate.py empty. Working fixture == landed fixture == tip blob.
- Docstring fidelity: extracted the fixture docstring's G-block (lines 6-46) and preregistration.txt lines 8-17; after whitespace/dash normalization both are 1983 chars and byte-equal (scratch diff_contract.py). The docstring's exit contract at fixture :52-54: "Exit 0 iff every case passes and the control is rejected; 1 otherwise; 2 on a missing prerequisite" — implemented at :631/:575.
- Case-by-case input fidelity (all ten checked against preregistration.txt:8-17):
  - G1 :231-244 — A.md `STATUS: PASS - synthetic pass.` under .ufo tree, B.md `STATUS: FAIL - synthetic union failure b.` under census tree, lesson carries nothing; judge :417-426 demands checked_reports=2, exactly one LG-SEAT-UNCARRIED row containing w1/B.md. Exact.
  - G2 :245-256 — identical duplicate bytes at w1/A.md in both trees, lesson carry with `(open)`; judge :427-431 demands checked_reports=1 and no uncarried. Exact.
  - G3 :257-275 — two carry sections split by a `## Notes` heading, X and Y both FAIL, each carried in its own section; judge :432-437 demands zero uncarried. Exact.
  - G4 :276-286 — literal citation `census/round-18/...seat-audit...json` (PLACEHOLDER_ROUND=18); judge :438-445 demands zero LG-DANGLING-PTR. Exact.
  - G5 :287-297 — tools/x.py committed; citations `tools/x.py:274–277` (U+2013 en dash, source :293) and `tools/x.py:2-3`. Exact.
  - G6 :298-318 — commits census/round-31/waves/v/.gitignore.captured and .gitattributes.captured, cites the three bare names incl. `census/round-31/waves/v/.gitignore:fixture/`. Exact.
  - G7 :319-328 — the `%d`/`%02d` templates stay unformatted literals (spotcheck does not %-format). Exact.
  - G8 :329-339 — three absent extension-less paths, no trailing slash; world has no tools/ tree at all. Exact.
  - G9 :340-360 — six citations, none committed, garbage-census.out under MISSING_ROUND=3; judge :452-468 demands count==6 plus one row containing each needle. See Finding 1 for the one precision gap.
  - G10 :361-375 — report Z FAIL, two carry sections each carrying a non-matching witness line; judge :469-477 demands exactly one uncarried row naming w1/Z.md. Exact.
- RUN1, tip gate: `TMPDIR=$SCRATCH/tmp python3 -B tests/fixtures/r31-landing-gate-precision.py` (tool default = lane tip). All ten `CASE G<k> PASS`, e.g. `CASE G1 PASS exit=1 reports=2 status=2 findings=1 dangling=0 uncarried=1` and `CASE G9 PASS exit=1 reports=1 status=1 findings=6 dangling=6 uncarried=0`; `CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=G1,G2,G9,G10`; last line `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; rc=0. Reproduces the landed `fixture=ok` reading at 8024b54 content (= tip).
- RUN2, base gate blob: `git show 9f17a1ef:tools/souji-landing-gate.py` (2374 lines) run through the same fixture. Result: G1 FAIL (reports=1, uncarried=0 — census tree unseen), G2 PASS, G3 FAIL (uncarried=1, second section unseen), G4 FAIL (dangling census/round-18/...seat-audit...json), G5 FAIL (dangling tools/x.py:274–277), G6 FAIL (3 dangling), G7 FAIL (2 dangling), G8 FAIL (3 dangling), G9 PASS, G10 PASS; rc=1. That is exactly preregistration.txt:18's REDARM requirement: base fails G1 G3 G4 G5 G6 G7 G8 and passes G2 G9 G10.
- RUN3-6, TMPDIR refusals, all rc=2 with PREREQ FAIL lines: unset ("TMPDIR is unset"); lane root (flagged as inside both lane and fleet roots); fleet root /home/vgpnk/Projects/shokunin; nonexistent directory. The guard (:539-546) realpaths both sides and `inside()` (:524-525) appends os.sep before startswith, so a sibling prefix such as a hypothetical /home/vgpnk/Projects/shokunin2 cannot false-negative [INFERENCE from source; a runtime probe would need a fleet-sibling directory, which this seat's hard bound forbids creating].
- RUN7, always-zero control: extracted CONTROL_SOURCE (:510-516) — 193 bytes; standalone run prints exactly one SUMMARY line `findings=0 ... checked_reports=0`, exit 0. Through the same ten judges on the same world repos (run cache keyed (tool, world), fixture :583-594) it fails G1, G2, G9, G10 — on substance (counts), since exercised() passes for it. The control is real and is rejected in both RUN1 and RUN2.
- PROBE, g9 raw gate output at tip: six LG-DANGLING-PTR rows for the six paths; the knowledge row emits `corpus/knowledge/missing.md` with the `:12–14` spec stripped (`line-spec still attached: False`), spotcheck line numbers :3/:5/:7/:9/:11/:13.
- Discipline: runs serial in one seat; scratch /fast/scratch/hyaku/souji-r31/w2-SwarmReviewer13 (base blob and control emitter extracted there); lane touched read-only plus this report; scratch removed after delivery copy.

## Findings

1. G9's judge cannot enforce the "(line spec removed)" clause nor a one-path-per-row shape. tests/fixtures/r31-landing-gate-precision.py:456-468 checks only `len(rows) == 6` and `c.expect(any(needle in row for row in rows)` per needle. Substring needles accept a row emitting `corpus/knowledge/missing.md:12–14` with the spec still attached, and a 6-row output where one row carries two needles and one row is junk passes too. The frozen clause reads "PASS iff exactly 6 LG-DANGLING-PTR lines, one containing each of those six paths (line spec removed)" (preregistration.txt:16); under the strict reading the judge is weaker than contract. Not live: the probe shows the tip gate strips the spec and emits six clean rows. Axis harmed if exploited: operability (C2).
2. exercised() (fixture :397-402) pins only rc in {0,1}, no COULD-NOT-EVALUATE marker, and presence of a checked_reports key; a gate that scans nothing emits zero rows and passes G3-G8 vacuously. This equals the frozen iff-clauses (they are literally "no LG-DANGLING-PTR"), and real scanning is anchored by G1/G2/G9/G10 (counts 2/1/6 and named uncarried rows), so it is not a contract violation — recorded so nobody reads G4-G8 PASS alone as scan evidence. Verified every judge can fire: base blob FAILs G1-G8 (RUN2), control FAILs G2/G9/G10 (RUN1/RUN2 CONTROL lines). Axis: operability (informational).
3. On a prerequisite failure the trailer prints `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` (fixture :574) although no control ran; exit 2 is authoritative, but the literal string is misleading in captured logs. Cosmetic; axis operability.
4. Input deltas vs the contract, all additive and non-weakening: every world also carries SKILL.md and the clean lesson; g4-g8 worlds add an unstated PASS report .ufo/waves/round-31/w1/Seat.md (fixture :283-285 etc.) so the world is not report-less; G4's citation lives in corpus/lessons/round-31-verifier-spotcheck.md, satisfying the contract's "a scanned file". No judged condition depends on the extras. Axis: none.

No case was found whose PASS condition is weaker than its frozen iff-clause other than Finding 1's strict-reading gap on G9.

## Attack log

- A1 Control reality: extracted and ran the always-zero emitter standalone (one clean SUMMARY, exit 0), then confirmed it fails G1, G2, G9, G10 through the fixture's own judges on identical world repos — FALSE-GREEN-REJECTED in both the tip and base runs. The control is not a rubber stamp.
- A2 Base-blob REDARM: ran the fixture against `git show 9f17a1ef:tools/souji-landing-gate.py`; observed exactly the prereg-required split (G1 G3-G8 FAIL, G2 G9 G10 PASS). The landed C2 redarm claim's fixture-level premise holds at base content.
- A3 TMPDIR refusals: unset, lane root, fleet root, nonexistent — four independent runs, each refused at exit 2 before any repo build; lane-root run correctly reports both the lane and fleet containment.
- A4 G9 line-spec probe: rebuilt the byte-identical g9 world through the fixture's own builders and dumped the tip gate's raw rows — spec stripped on the knowledge path; establishes Finding 1 as latent, not active.
- A5 Judge liveness: the base run plus the control run demonstrate all ten judges firing on inputs they should reject, so no PASS condition is vacuous.
- A6 Docstring fidelity: mechanical normalized diff of the fixture's embedded contract block against preregistration.txt lines 8-17 — equal (1983 == 1983 chars).
- A7 Fixture identity: no diff between the C2 landing commit 8024b540 and tip for the fixture; working tree clean for fixture and gate.

## Deliveries

- .ufo/waves/round-31/w2/SwarmReviewer13.md — this report.
