# CritC2Classification — C2 axis label audit: `operability` vs `coverage`

Seat: L1Souji25.CritC2Classification (critic, leaf; no subagents). Lane bounds:
read-only — no lane edits; scratch `/var/tmp/souji-r25-CritC2Classification/` removed.
Installs: none.

STATUS: **FAIL** (of the "true operability move" thesis) — claim mechanics verify
(green 12/12, red arms discriminate), but the axis label is a misattribution:
C2 is a coverage move, not an operability move, and the mislabel distorts the
round's claim structure and the scorecard's per-axis attribution.

---

## 1. The question

C2 as preregistered (`.ufo/waves/round-25/preregistration.txt:58-85`): "C2 —
operability (8). Size-census refusal surfaces **covered by the frozen fixture**."
The move adds four refusal cases (9 bare-nonempty, 10 bare-empty, 11 subdir,
12 partialClone-only) to the existing runnable fixture
`tests/fixtures/r24-size-census.py`. The production tool is **not touched**
("C2 touches tests/fixtures/r24-size-census.py only (the tool already carries the
fix)", `preregistration.txt:136`). Measured before→after is a case count:
`cases=8 pass=8` → `cases=12 pass=12`.

## 2. Evidence

- **AXES.md definitions** (`/home/vgpnk/Projects/shokunin/AXES.md:11-13`):
  `coverage` = "Fraction of the domain's real surfaces the skill governs (repo
  paths, tools, **edge classes**)"; `operability` = "Runnable artifacts: checklists
  that are executable, commands that exist, scripts that run | A checklist item can
  be run and produces the stated outcome". Bare / empty-bare / subdir /
  partialClone-only are precisely input-domain **edge classes** of the size-census
  tool. The surface the fixture now governs is exactly what the coverage axis
  measures (cases 9–12 each add a governed edge class, counted 8→12).
- **The defect being repaired was classified as coverage in r24**: the routed
  mistake `R24-M24` sits in the r24 mistakes table as **"coverage — a tool
  regression invisible to the frozen fixture"** (`corpus/lessons/round-24.md`
  R24-M24 row). The default's own text says the gap is "the FIXTURE does not cover
  the surface" (`preregistration.txt:62`). Fixing an uncovered surface is a
  coverage move.
- **r24 precedent — same fixture, same kind of work, labeled coverage**: the r24
  claim that *created* this fixture (C1 F2 write-safety debris census) was claimed
  on coverage (8) (`corpus/lessons/round-24.md:18`; `SCORECARD.md` Round 24
  table). r24's W2C1Axis review held "coverage-move holds, qualified"
  (`round-24.md:271`). Extending the same fixture's case set is the same class of
  move, not a different axis.
- **Same-round consistency**: C3 (also a fixture case-add, `r13-repo-structure.sh`
  5/5→7/7) is labeled coverage (8). C2 is structurally the same work; there is no
  principled line separating them.
- **No operability property changed**: the fixture ran before (8/8, `c2-control-base.tsv`
  rc=0) and runs after (12/12, rc=0); its last-line format and exit rule are
  unchanged (ExecC2.md: "The last-line format and exit rule are unchanged").
  ExecC2 itself calls the content "coverage only" for case 12 (ExecC2.md:52).
- **Frozen counter is a coverage measure**: before→after is `cases=8→12`, i.e.
  the count of governed surfaces — the coverage metric, identical in kind to the
  r24 C1 scoring.
- **Bounded replay (scratch, exact commands below)**: tip tool → 12/12 rc 0;
  old blob `1efe406` → 11/12 (case 11 fails); regression blob `778747e` → 10/12
  (cases 9+10 fail). Matches `c2-control-base.tsv` (8/8) + ExecC2 red/green
  receipts. So the fixture does discriminate the refusal surfaces — the coverage
  is real.

### Attack log / commands

```
# lane repo, git show to scratch (removed after)
python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py
  -> cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED, rc 0
python3 -B tests/fixtures/r24-size-census.py --tool <1efe406 blob>
  -> cases=12 pass=11 (11 subdir FAIL), rc 1
python3 -B tests/fixtures/r24-size-census.py --tool <778747e blob>
  -> cases=12 pass=10 (9+10 bare FAIL), rc 1
```

## 3. Verdict

- **Not a true operability move.** Nothing changed about what is runnable,
  how it runs, or what outcome it produces for its declared scope; the fixture
  was runnable and correct before (8/8). What changed is *which domain surfaces
  are governed* (edge classes 9–12). That is the AXES.md coverage definition,
  the r24 classification of the very defect repaired (R24-M24 = "coverage"),
  and the precedent of the same fixture's creation being claimed as coverage.
- **Not calibration either** (as a *move*): the gap was already named honestly in
  r24's report boundaries (`round-24.md:59` — "the fixture is blind to it"), so
  no self-assessment defect was pending; the work is surface expansion, not an
  assessment change. C2's provenance is coverage-adjacent to calibration only in
  that it backfills a prior round's uncovered surface.
- **Recommended label: coverage.** The claim is a coverage move; it should be
  recorded on coverage and counted together with C3 per "two claims on one axis
  count as one claim" (AXES.md:32, round prompt §2.3), or merged with C3.

## 4. Impacted axes / harms

1. **Calibration (7, lowest) — harmed by attribution.** SCORECARD/observations
   must match observed state (AXES.md calibration definition). Recording a
   coverage expansion under "operability 8" (scorecard Round 25 table, C2 row)
   means a reader cannot re-derive what, if anything, improved on operability —
   the row asserts an axis move that did not occur. This is the exact
   self-assessment failure the calibration axis exists to catch.
2. **Claim structure (per-round contract) — distorted.** The round declares
   three claims on three distinct axes. If C2 is coverage, then C2 and C3 both
   target coverage → the round effectively carries two claims on two axes
   (calibration + coverage), and the declared "distinct axes" property is
   false. C2's separation (fixture-only, tool untouched) still verifies, so the
   falsifiable mechanics survive; only the axis typing is wrong.
3. **Coverage — denied credit, not harmed.** C2's expansion is real (confirmed
   by replay) but is booked to the wrong axis; coverage's score/verdict row
   does not receive it (C3 still gives coverage a move, so no scoring gap).
4. **Case-10 freeze (rc=1 on empty-bare) — disclosed tradeoff.** The fixture
   freezes the tool's current refusal of empty-bare repos (exit 1, no counts
   line) as expected; amendment 2 discloses that a future tool reporting zeros
   would trip the kill rule. That is a disclosed, not hidden, lock-in of a
   plausibly-suboptimal behavior on the empty-bare surface; it is worth
   recording as a known normative cost of the new case, not as a new defect.

## 5. Smallest safe correction

Do not touch the frozen claim box, case set, or counter (still frozen). Only the
**taxonomy** needs correction, in two places recorded as a round-25 scorecard
correction:

1. Re-label the scorecard C2 row from `operability 8` to `coverage 8`, citing
   AXES.md coverage definition + R24-M24's own "coverage" class + r24 C1
   precedent; record that the round then has one combined coverage claim
   (C2+C3) per the two-claims-on-one-axis rule. This keeps the before→after
   measurement and kill rule intact.
2. Add an append-only note that no operability move was landed for C2 (the
   fixture's runnability/exit/output contract were unchanged), so operability's
   row shows no change attributable to C2.

These are reporting corrections; they do not alter any frozen predicate, target,
or case set, and do not re-score any claim.
