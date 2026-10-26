# SwarmScribe31 — round-31 wave-2 seat-failure carry for wave 1 (scribe, leaf)

## Status

STATUS: PASS — the `## Seat-reported failures` section for `corpus/lessons/round-31.md` is drafted from the gate's own failure channel over all 38 wave-1 reports (7 failure STATUS lines, 7 bullets), each bullet's disposition is grounded in a named commit and a reading at the tip, and the section is verified to take a red-before of `findings=7 … checked_markers=7 carry_heading=0` to `findings=0 … carry_heading=1 rc=0` with a one-bullet negative control reading exactly `findings=1`.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`, tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`, base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`. Python 3.14.8, git 2.56.0, jj 0.45.1. No tool installed or upgraded; no pacman call. Lane worktree clean for this scope (`git status --porcelain` printed nothing; the delivery is under gitignored `.ufo/`). Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe31/` with its own `TMPDIR`, clone `git clone -q --no-local` with `origin` removed and `rev-parse --show-toplevel` verified.

1. **Detection (gate's channel, imported not re-implemented).**
   `python3 -B -c` with `importlib` on `tools/souji-landing-gate.py`, calling `seat_failure_lines` over the 38 `Swarm*.md` in `.ufo/waves/round-31/w1/`:
   ```
   SwarmCritic29.md L4   FAIL     SwarmReviewer25.md L4  PARTIAL
   SwarmExecutor04.md L5 PARTIAL  SwarmReviewer26.md L4  PARTIAL
   SwarmExecutor06.md L5 PARTIAL  SwarmScribe23.md L5    PARTIAL
   SwarmSimplifier38.md L4 PARTIAL
   ```
   Status vocabulary over all 38 reports: `{'pass': 31, 'fail': 1, 'partial': 6}` — one STATUS line per report, so the 7 hits are exactly the non-PASS lines and no PASS line is a false hit.

2. **Red before, at the lane tip with no round-31 lesson** (`python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d018… --round 31 --fleet-root /home/vgpnk/Projects/shokunin`): 7 `LG-SEAT-UNCARRIED`, `SUMMARY findings=7 checked_reg=63 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=7 status_lines=39 carry_heading=0 checked_reports=60`, rc=1. Without `--fleet-root` the same run adds 3 `LG-DANGLING-PTR` for the fleet-only `../.ufo/waves/hyaku/jj-w1/` citations in `corpus/README.md:217` and `corpus/knowledge/jj-colocation-receipts.md:148` (`findings=10`).

3. **After, in the scratch clone** (lesson = scratch header + the delivered section, scratch-local commit `02fecb13d86802200db53bcb4bbebee59b89646e`, gate at that rev with `--fleet-root`): `SUMMARY findings=0 … checked_markers=7 status_lines=39 carry_heading=1 checked_reports=60`, rc=0 — zero uncarried, zero dangling. The procedure is reproducible from the delivered section alone; the clone and its commits are deleted with the scratch dir.

3b. **Final rehearsal from the delivery's own bytes**, not from the generator output: the block extracted between the delivery's markers (sha256 `fbb270da7852b39312f0a1c39be4e1d3845f91f899308df29f07a2745e8478cd`, identical to the generator output) lands as `corpus/lessons/round-31.md` in the clone (scratch-local commit `fd497e11d062347b9a624c81a45587a67c18b7a1`) and the gate reads the same `findings=0 … carry_heading=1`, rc=0.

4. **Negative control** (same lesson with the SwarmReviewer26 bullet deleted, next scratch commit): `SUMMARY findings=1 … checked_markers=7 carry_heading=1`, the single finding being `LG-SEAT-UNCARRIED census/round-31/waves/w1/SwarmReviewer26.md line 4`. The section is load-bearing per bullet, not in bulk.

5. **Union equivalence for the final tip**: sha256 of every `.ufo/waves/round-31/w1/Swarm*.md` equals its `census/round-31/waves/w1/<same name>` capture blob — `reports=38 mismatches=[]` — so the wave-dir + capture union the final-tip gate reads resolves to the bytes verified here.

6. **C1 re-derivation at the tip** (`python3 -B tools/souji-capability-cells.py --root <lane> --rev 2c16d018… --base 9f17a1e… --list-rev 1d45496…`): `ITEM L29 SCORECARD.md:170 literal=18/18 base-cell binding=- UNBOUND`, `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`, rc=1. The landed block holds 40 `| L` rows and no `| L29` row.

7. **C3 re-derivation at the C3 landing** (`python3 -B census/round-31/c3-counter.py --root <lane> --rev 1baf4da02b71b012ee2426ea7c309496c0c3aca0 --base 9f17a1e…`): `L1 PASS f1_entries=4`, `L4 PASS snapshots=3 bad=[]`, `L8 PASS run_record=present results=17`, `L9 PASS replays=[(0, 17, True), (0, 17, True)]`, `SUMMARY legs=11 fail=0 f1_entries=4`, rc=0.

8. **C2 fixture at the tip** (`python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py`): 10 `CASE` lines PASS, `cases=10 pass=10 control=FALSE-GREEN-REJECTED`, rc=0.

9. **M1 after-state at the tip** (gate `--round 26|27|28` at `2c16d018…`): `findings=0` for all three, `checked_markers=26/29/19`, `carry_heading=1`, `checked_reports=495/94/61` — the landed M1 claim holds at the tip by independent re-measurement.

## Findings

1. **C1 misses its frozen target by one item at the tip (calibration).** `SCORECARD.md:170` / `census/round-31/records/c1-cells.tsv` L29: the landed append block (40 rows under the block that opens at `SCORECARD.md:361`) has no L29 row, and the frozen counter at `2c16d018…` reads `unbound=1 mismatches=1` against target `unbound=0 mismatches=0`. Wave-1 SwarmExecutor04 and amendment A4 both forecast this before landing; the miss stands at the tip as well as at the C1 landing commit `24f343c8ffc820c0f89b4252cbdc94ab9a673aab`. This is the calibration axis itself.

2. **The round-31 carry is still owed at the tip, and wave 2 is already adding to it (operability of the carry instrument).** `corpus/lessons/round-31.md` does not exist at `2c16d018…`, so the tip gate reads `carry_heading=0 findings=7`. Independently, at read time 3 of the 13 `Swarm*.md` already in `.ufo/waves/round-31/w2/` carry failure STATUS lines (`SwarmCritic18.md:5`, `SwarmCritic21.md:9`, `SwarmScout19.md:4`); each will be an `LG-SEAT-UNCARRIED` at the final tip unless carried. The delivered section closes the 7 wave-1 lines and claims nothing about wave 2.

3. **A carry bullet may not cite an untracked path (operability).** My first draft of the section's preamble cited the wave-2 delivery file; the tip gate flagged it `LG-DANGLING-PTR corpus/lessons/round-31.md:7 cites path absent`. Only `.ufo/waves/round-N/…` citations that map to the committed capture survive, because `_pointer_candidates` adds the capture-mapped form (`tools/souji-landing-gate.py:1013-1026`). The delivered preamble therefore names no uncommitted path and the delivery states that the section must be landed at or after the wave-1 capture commit.

4. **The captured wave-1 plan still commits lane-relative write targets (hygiene; would harm operability if reused).** `census/round-31/waves/w1-dispatch.json`: task 5 (`SwarmExecutor06`) "Implement C2 in the landing gate /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py", task 6 (`SwarmExecutor07`) "Write the frozen C2 fixture tests/fixtures/r31-landing-gate-precision.py", task 7 (`SwarmExecutor08`) "Write tests/fixtures/r31-jj-object-clock.sh" — seats start at the fleet root, so the imperatives name out-of-lane paths. No commit in `9f17a1e..2c16d018` edits those bytes; the wave-2 plan does not repeat the class (0 hits for the same four phrasings in `census/round-31/waves/w2-dispatch.json`, 36 tasks), so this is a latent wave-1 defect, not a live one.

5. **The M1 landing duplicated the carry heading in round 26 (bookkeeping/calibration decoration).** `corpus/lessons/round-26.md:98` and `:105` are two `## Seat-reported failures` headings with byte-identical 4-line preambles, both added by `c6108301cbf0ca0ad086ff0ece6b76adad6b74b6` (base file had 0 such headings). The gate is unaffected — it concatenates every section's lines — and my re-measurement gives `findings=0` for round 26 at the tip, but a reader or a stricter future parser sees the same carry announced twice.

6. **Nothing in the frozen C2 counter scores exit status or corpus-wide carry precision (operability of the instrument).** `census/round-31/c2-counter-v3.py:206-211` passes only on `fp/real/cne/r26/fixture/redarm/same/shift`, and the SHIFT leg's own predicate (`:206`) is `got == want and no COULD-NOT-EVALUATE`; no leg counts `LG-SEAT-UNCARRIED` or `## Seat-reported failures` sections on the corpus. The consequence for this seat: the plain final-tip gate run is the only instrument that can show the round-31 carry complete — which is exactly what Findings 2 and the delivery's red-before/after pair measure.

## Attack log

- **A1 — draft from the gate's own channel.** Generated every quote with `norm_line(status_paragraph(...))` in the same module the counter/receipts use, so no transcription step exists to break `carries()`. 7 bullets, 17 lines.
- **A2 — path-citation hazard (reproduced, then fixed).** Committed the first draft into the scratch clone; gate returned `findings=1` (`LG-DANGLING-PTR` on the delivery path). Removed the citation, re-committed (`02fecb13…`), `findings=0`.
- **A3 — one-bullet negative control (reproduced).** Deleting the SwarmReviewer26 bullet yields exactly `findings=1` naming that report; the section cannot pass by bulk.
- **A4 — truncation attack not needed.** All seven STATUS paragraphs are single physical lines (`status_paragraph` length 1 for each), so the full-paragraph quote is also the maximal quote; no `...` prefix is used and no mid-line cut exists.
- **A5 — vocabulary blind-spot sweep.** Compared the gate's 7 hits against a raw `STATUS`-line sweep of all 38 reports: 38 lines, one per report, words `pass/fail/partial` only; no bold/`STATUS —`/table/fence variant hides a failure, and no PASS line is mis-flagged.
- **A6 — union byte-equality.** 38/38 wave-1 reports are byte-identical to their capture blobs, so the verification at the capture-only rev carries to the final-tip union reading.
- **A7 — disposition falsification.** Re-ran the instruments instead of trusting the reports: C1 at the tip (`unbound=1`, Executor04 confirmed, not discharged), C3 v1 at `1baf4da…` (`legs=11 fail=0 f1_entries=4`, Scribe23 discharged), C2 fixture at the tip (`cases=10 pass=10`, Executor06 discharged), M1 after-state at the tip (r26/27/28 `findings=0`).
- **A8 — over-credit check on the two `resolved@` bullets.** Executor06's only asserted defect was the uncommitted fixture (present at `8024b540…`, legs ok); Scribe23's only blocker was the absent C3 entry (present at `1baf4da…`, counter green). Neither bullet was resolved for its neighbours' still-open findings (Critic29 finding 2 / Reviewer26 clause (c) stay `open`).
- **A9 — mixed-paragraph discipline.** Five paragraphs assert several defects each and were disposed `open` where any one still stands (Critic29, Reviewer25, Reviewer26, Simplifier38, Executor04); the delivery states the rule and the per-clause evidence.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-w1-seat-failures.md` — the section to append (between `<<<SECTION-START` / `SECTION-END>>>` markers, verified byte-equal to the generator output), the detection re-derivation, the per-bullet disposition basis with commits and readings, the red-before/after/negative-control receipts, and three landing notes for the L1 (capture-commit ordering, wave-2 carry still owed, disposition checkability).
- `.ufo/waves/round-31/w2/SwarmScribe31.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe31/` is removed after copying the delivery into the lane wave directory.
