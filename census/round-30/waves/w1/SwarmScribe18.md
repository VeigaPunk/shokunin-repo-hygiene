# SwarmScribe18 — Q63/Q64 criteria drafts and matching Gate-registry rows

## Status

STATUS: PASS — both criteria and both `## Gate registry` rows are drafted in the exact column layout of the files they extend, each carries a runnable check with its exit map, and both checks were exercised red at the lane base; no lane file outside my report and delivery was written.

## Evidence

Lane tip during the work: `df6afe817d096e4ad71ba2b9cc21a83f126eb658`, `git status --porcelain` = `?? corpus/lessons/round-30.md` (only entry). Lane base and frozen inputs used as cited: `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` (base), `d4928ec86b667e3d1ed0adb07fb088e500cf1631` (preregistration / `--list-rev`).

1. C1 counter, full frozen set at base — scratch `TMPDIR` and `--scratch` under `/fast/scratch/hyaku/souji-r30/SwarmScribe18/`:

   `python3 -B tools/souji-capability-agreement.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631`

   → rc 1, 31 s; `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` and `KINDS value=7 shape=5 rc=1`. Identical SUMMARY to the committed per-row receipt `census/round-30/records/c1-before.txt`, which I read: 18 rows, 5 `MATCH` (R01 R02 R12 R13 R17) and 13 `MISMATCH` (`kind=value` 7, `kind=shape` 5, `kind=rc` 1 — R16), matching `KINDS value=7 shape=5 rc=1`.

2. Diagnostic arm (proves `--only` cannot satisfy the check):

   `… --only R05,R10` → rc 1, 2.9 s; `SUMMARY k1=2 k2=0 mismatches=2 rows=2 pointers=10 partial=1`.

3. Discovery fixture, red arm, against the committed gate:

   `python3 -B .ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py` → rc 1, 1.0 s;

   ```
   CASE D1 FAIL … FAIL(COULD-NOT-EVALUATE printed; … checked_reports=0 want 2; status_lines=0 want 2)
   CASE D2 PASS   CASE D3 PASS
   CASE D4 FAIL … FAIL(template token flagged: round-%s; template token flagged: round-{N})
   CASE D5 PASS
   CASE D6 FAIL … FAIL(mapped: exit=1 want 0; mapped: capture-backed pointer flagged)
   CASE D7 FAIL … FAIL(missing LG-SEAT-UNCARRIED)
   CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=D1,D2,D3,D5,D6,D7
   cases=7 pass=3 control=FALSE-GREEN-REJECTED
   ```

   Same seven `CASE` lines and same tail as the peer receipt `.ufo/waves/round-30/w1/deliver-c2-fixture-red-before.txt` — two independent runs agree. No `/var/tmp/souji-landing-gate-*` residue after the run.

4. Prerequisite absent today: `[ -e tests/fixtures/r30-landing-gate-discovery.py ]` → absent (the fixture exists only as `.ufo/waves/round-30/w1/deliver-r30-landing-gate-discovery.py`, 19,698 B), so the Q64 command as written currently exits 2 on a missing script. `[INFERENCE]` it reads `cases=7 pass=7 control=FALSE-GREEN-REJECTED` only after the L1 lands the fixture and the gate change.

5. Layout sources read: `corpus/QUALITY.md:146-149` (heading, blank, `| id | criterion | applies to | check | motivating evidence |`, separator) and rows `:150-152`; `SKILL.md:178-179` (8-column header) with the table ending at `:228` (`r29-c2-counter`). My four table lines parse as 5/5 and 8/8 columns (checked by splitting on the pipe character).

## Findings

1. `--only` is the one way to make Q63 green without measuring: it emits `partial=1` on the SUMMARY line (`tools/souji-capability-agreement.py:99` help text, `:226` emission). The drafted row therefore makes `partial=1` a failure, not a pass with `mismatches=0`.
2. Q63's target cannot be reached by editing a literal: the tool fails closed on non-append-only bytes (`tools/souji-capability-agreement.py:29-30`, "does not begin with its `--base` bytes, every K1 … item is a mismatch"), so wave-2 must add `R30-CORRECTION` lines after the base bytes.
3. `mismatches=` counts only the two `MISMATCH` verdict forms; `CORRECTED` and `MATCH`/`RESOLVES` items are printed but excluded (`tools/souji-capability-agreement.py:188` for K1, `:223` for K2). The row states this so a reader does not treat a printed `CORRECTED` line as a failure.
4. The discovery fixture's control arm is strong, not decorative: the always-zero emitter fails 6 of 7 cases (`…/deliver-c2-fixture-red-before.txt` CONTROL line, reproduced), so a gate that is clean because it read nothing cannot pass D1-D7.
5. `tests/fixtures/r30-landing-gate-discovery.py` is not in the lane at `df6afe8`; Q64's check is therefore red-by-absence today (exit 2), not green. Recorded so the L1 does not read the 2 as a failed fixture.
6. `SKILL.md:198` (`souji-landing-gate`) still states discovery from `.ufo/waves/round-N/` only; left unamended it would contradict Q64. Delivery §4 carries the two cell additions (verdict map, self-test) for the L1 to apply or reject.
7. Both QUALITY rows must cite `corpus/lessons/round-30.md`, but that file today holds only the head and the `reading:` line (`corpus/lessons/round-30.md:1-7`); `## Mistakes`/`## Findings` are still owed by the lesson author. Each row also names a committed receipt (`census/round-30/records/c1-before.txt`, `corpus/lessons/round-29-verifier-spotcheck.md:131-132`) so the evidence cell stays checkable if the lesson's section names differ.

## Attack log

Not an attack seat; none filed. No predicate, target, counter or case set was challenged in this item.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-quality-q63-q64.md` — Q63 and Q64 rows for `corpus/QUALITY.md` (with the insertion block), the matching `souji-capability-agreement` and `r30-landing-gate-discovery` rows for `SKILL.md` `## Gate registry`, the advisory patch to `SKILL.md:198`, and the red-before/not-exercised record.

Scratch `/fast/scratch/hyaku/souji-r30/SwarmScribe18/` created with `mkdir -p` and removed after the runs; the counter and fixture removed their own clones and temp trees. No tool was installed or upgraded (nothing needed; pacman untouched). No `git add/commit/push/stash/checkout/reset`, no `jj`, no `rm`/`mv` outside my scratch, no signals, no write under `/home/vgpnk/Projects/shokunin` outside this lane.
