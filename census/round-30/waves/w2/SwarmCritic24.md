# SwarmCritic24 — round 30 wave 2 (trend-verdict pre-emption / falsification)

author: SwarmCritic24 (leaf; no subagent dispatch). Scratch `/fast/scratch/hyaku/souji-r30/SwarmCritic24/`,
deleted after this report; every command below ran on a `git clone --no-local` of the lane with origin
removed, `python3 -B`, `TMPDIR` in that scratch dir. No lane, fleet, `.ufo/state`, `MANIFEST.json` or
sibling path was written. Tool installs: none.

## Status

STATUS: PASS — the attack ran to completion on all three L1 readings, the r29 carry/D4 correction
and the new fixture's admission bar. It found that two predicates are not functions of committed
bytes alone (C1's tip checkpoint under the lane's own concurrency; A1's `regress_full`) and one
undisclosed bar failure (Q4) in the C3 fixture, so "C1 met / C2 missed at landing / C3 met" is
confirmed only with those three qualifications. Verdict recommendation at the end: expansion
improved (with a named bar defect), quality unchanged, discernment unchanged.

## Evidence

Revisions: base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; prereg `d4928ec8…`; C1 `7b16731f…`; C2
`68447afe…`; capture + after-records `aea0525…`; C3 `76c94eb4…`; carry `936efc8a…`; tip
`9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`.

I re-ran, rather than trusted, every reading that a trend verdict would rest on:

- **C1 at its landing commit (A3 bytes, my clone).** `SUMMARY k1=0 k2=0 mismatches=0 rows=18
  pointers=10 rev=7b16731f…` — the L1 reading HOLDS at landing.
- **C1 at the tip, serial (v1 blob at `d4928ec` and A3).** Both print `SUMMARY k1=0 k2=0
  mismatches=0 … rev=9dcd3676…`. The frozen target's second checkpoint is met when one instance runs.
- **C1 at the tip, two instances concurrently (same rev, same tree, same env).** Both print
  `SUMMARY k1=1 k2=0 mismatches=1` with `ROW R14 SCORECARD.md:173 stated=9/9 rc=1
  observed=tool_sha256=<HEX> MISMATCH kind=rc`; one earlier A3 run showed the same row as
  `observed=selftest=14/15`. Eight serial runs of that row's command pass: `rc=0`,
  `control=FALSE-GREEN-REJECTED`. Concurrent runs of the same fixture collide: in three paired
  rounds, five of six runs exited rc=1 (`RuntimeError: git add -A failed` / `Another git process
  seems to be running in this repository, or the lock file may be stale`) and one printed the normal
  summary.
  Cause, opened this run: `tests/fixtures/r23-record-agreement.py:67`,
  `SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"` — one fixed path per host, and the
  fixture's own docstring says it "builds a synthetic lane repo under /var/tmp (hard-coded; never
  /tmp), trap-cleaned on exit".
- **C2 at its landing commit (frozen v1).** `GATE rc=1 reports=86 cne=0 dangling=1 other=7`;
  `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same`. The dangling line
  is `LG-DANGLING-PTR .ufo/waves/round-30/w1/deliver-c1-literal-history.tsv SCORECARD.md:322 cites
  path absent at 68447afef62e` — a path in C1's own correction block.
- **C2 at the tip (frozen v1).** `SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok
  regress=same`.
- **C2 under A1 at the tip.** `SUMMARY-V2 reports=86 expected=86 cne=0 dangling=0 bind=ok nocap=ok
  ptrarm=ok fixture=ok redarm=ok regress_full=differs`. The differing bytes are exactly two `CASE`
  lines end to end, and the separator before the reworded tail is a space (`fleet=[] err=…`, verified
  with `cat -A`), while `census/round-30/c2-counter-v2.py:69` strips only `\terr=`.
- **C3 at the tip (v1 and A2 v2).** `SUMMARY legs=9 fail=0 f1_entries=3` and
  `SUMMARY-V2 e1=ok e2=ok e3=ok e4=ok f1_exact=3`. The L1 reading HOLDS at the tip.
- **r29 carry / D4.** `census/round-30/records/m1-r29-carry-red-before.txt` records `findings=7` rc=1
  at `76c94eb4` and `findings=0 carry_heading=1` rc=0 at `936efc8a`; I re-read the gate line for
  `SwarmCritic49.md` line 5 against `corpus/lessons/round-29.md:98` — the carried STATUS paragraph
  matches the wave file's bytes.
- **New-fixture bar.** `tests/fixtures/r30-jj-keep-expiry.sh:5` says it "builds jj-colocated
  repositories ONLY under $TMPDIR, never in a lane or fleet repo"; lines 29-36 require `TMPDIR` and
  refuse the lane and fleet prefixes, but accept `/tmp` as `TMPDIR`. `grep -c '/var/tmp'` on that
  file is 0. Of the 45 regular files under `tests/fixtures`, 36 contain `/var/tmp`; this is the only
  one that takes `TMPDIR` and does not.
- **Corpus deltas.** SOURCES rows 143 → 145 (S220, S221 new), knowledge files 22 → 23,
  `git diff --stat 9420341..9dcd367 -- corpus/QUALITY.md corpus/knowledge/jj-colocation-receipts.md`
  is empty, and `corpus/lessons/round-30.md` has only `## Gate` and `### SOURCES touched-row log`
  (no `## Mistakes`).

## Findings

1. **C1's tip predicate is not stable under the lane's own concurrency (BROKEN as a landing
   predicate).** Same revision, same instrument, same environment: serial `mismatches=0`, concurrent
   `mismatches=1`. The prereg states the observable as a function of the revision and a kill rule on
   any other value: "Kill rule: any other SUMMARY at either revision, or a base value of
   mismatches=0 (claim vacuous), is a miss." A SUMMARY other than the target therefore exists at the
   tip whenever a second instance runs beside the first, so the tip checkpoint is met only when the
   host is quiesced. The cause is pre-existing (`r23-record-agreement.py:67`), not introduced this
   round, but wave seats re-run these counters on the same host (wave 1 did:
   `census/round-30/waves/w1/SwarmReviewer22-c1-base-rerun.txt`), which is exactly the condition that
   exposes it. The frozen contract forbids repairing a failing row under C1 ("a row whose
   command now fails is corrected with its failing rc and reported as an operability limit, not
   repaired under C1"), so the smallest safe correction is: record the tip checkpoint with an
   exclusive lock or with the fixture quiesced, repeat it twice, and route the fixed scratch root as
   an operability limit; do not edit the r23 fixture under C1.
2. **A1's stricter C2 target is unmeetable at every revision (instrument defect, DEFECT-NOT-FATAL).**
   `regress_full=differs` is produced by the amendment's own regex on bytes that are identical except
   for the `err=` tail A1 meant to allow. So the recorded `differs` at `68447afe` is not evidence of a
   gate regression, and no run of A1 can ever reach `regress_full=same`. It does not rescue C2's
   frozen miss: the v1 `dangling=1` is independent and reproduced.
3. **C2's landing miss is confirmed, and its cause falsifies the prereg's separability sentence
   (DEFECT-NOT-FATAL).** The prereg claims "Causal separability: each counter is evaluable at its own
   landing commit without the others." The dangling pointer is
   `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv` at `SCORECARD.md:322`, i.e. C1's
   correction block landed one commit earlier and its wave delivery was not captured until
   `aea0525`, one commit after C2. C2's own target was therefore unattainable at its landing commit
   for a reason that belongs to C1's text and to the capture's timing. This is a sequencing defect
   the L1 must own in the round report; the kill rule still makes C2 a MISS, and it must not be
   restated as "met at the tip".
4. **The C3 entry's fixture fails Q4's test, undisclosed (DEFECT-NOT-FATAL, but bars a silent
   "expansion improved").** Q4's test is "the scratch root is hard-coded under `/var/tmp`"; the new
   fixture has no `/var/tmp`, accepts `TMPDIR=/tmp`, and is the unique such fixture in the directory.
   Q16 keeps Q4 unrelaxed ("so Q4 stands unrelaxed"), and neither `corpus/lessons/round-30.md` nor the
   C3 delivery names the deviation. LEARNING's harm clause for expansion is exactly "an admitted
   entry fails the bar it was admitted under" — so the entry's sound measurement does not by itself
   license an unqualified improved verdict; the deviation must be disclosed and routed, or a Q4
   successor grounded in a lesson must be written before the next admission of this shape.
5. **Discernment has no outside evidence at the tip.** `corpus/lessons/round-30.md` states
   "Spot-check status: none on record." and "Wave reviewers, critics, mutation-testers and scribes
   are lane seats and do not satisfy the independent closure duty." `corpus/QUALITY.md` is untouched
   this round, so the "disagreement becomes a grounded criterion" branch did not fire either.
   Q63/Q64 exist only as an unlanded wave draft (`census/round-30/waves/w1/deliver-quality-q63-q64.md`
   says "Not an integration").
6. **The planned frontier step is incomplete at the tip.** The prereg requires one mistake mined into
   `corpus/lessons/round-30.md` `## Mistakes`; the file has no such section, and the M1 evidence is
   only the census record. Not a claim (claims are C1-C3), but the round cannot close honestly with
   the planned move half-landed.
7. **Minor ledger inconsistency.** The R18 `R30-CORRECTION` line records a usage banner as
   `observed=`, which A3 refuses as an observation; the L1 discloses this in the SCORECARD prose
   ("satisfies only the frozen v1 reading"), and A3 passes the row on its stdout line, so the line is
   latent rather than active. The 13 stale table literals staying in place are the frozen contract's
   own append-only choice, not a defect.

### Trend verdicts — evidence pointer, then the strongest counter-argument

8. **expansion — improved.** Evidence: one entry on ground the map held as unmeasured
   (`corpus/knowledge/jj-keep-ref-expiry.md`, `ground: F1`; base frontier line "remaining: keep-ref
   expiry unmeasured"), the map row now names it (`corpus/README.md:39`), two new mined rows opened
   this round (S220, S221) with tag-pinned snapshots and hashes, SOURCES 143 → 145, knowledge 22 → 23,
   and `census/round-30/records/c3-after-v1.txt` `f1_entries=3` reproduced by me at the tip under v1
   and A2. This is the same shape the r29 outside spot-check accepted as improved. Strongest
   counter-argument: Finding 4 — the fixture fails Q4's test, which under LEARNING's own harm clause
   makes "improved" conditional at best; and the increment is the minimum (one entry, no capability
   row admitted, F1 still frontier with its other remaining item untouched).
9. **quality — unchanged.** Evidence: no existing entry was re-verified, deepened or superseded —
   `git diff --stat 9420341..9dcd367 -- corpus/knowledge/` shows only the new file, and
   `corpus/QUALITY.md` gained no row. What did move is round evidence and bookkeeping: the r29 carry
   (7 STATUS lines, gate findings 7 → 0) and C1's 13 append-only corrections. Strongest
   counter-argument: the r29 outside spot-check scored exactly this kind of repair as quality
   improved ("stale statements corrected append-only"), and r30 repeats it at larger scale. The
   answer to that counter is LEARNING's observable — entries "re-verified, deepened, or superseded"
   — plus the fact that the 13 literals stay wrong in place and the companion entry's Limits text is
   reconciled only in `corpus/README.md`'s corrections block, not in the entry itself. If the L1
   claims improved, it must cite the broader outside reading and name this counter; claiming it
   silently would inflate.
10. **discernment — unchanged; `unprovable-but-better` is NOT earned and must not be used.** Evidence:
    Finding 5 — no outside spot-check of round 30's gate decisions, no QUALITY.md criterion added.
    The r29 disagreements that were closed this round (D3, D4, the attempted C2 closure) are closure
    work; LEARNING requires the disagreement to become a lesson that adds a grounded criterion, and
    none did. Strongest counter-argument: r30's Gate now records per-entry reject reasons and flip
    conditions that the r29 Gate lacked (D4 at `936efc8a`), which is a real discernment artifact.
    It fails the letter (no criterion, no outside judge), and "A subagent the lane dispatched is still
    the lane" — so wave-2 seats, including this one, cannot supply the missing evidence. The honest
    entry is unchanged with the closure duty named as open.

11. **Axis note the same report must honour (pre-empting "operability improved" / "calibration
    improved").** Operability 8 has a real new instrument (the gate now reads the committed capture:
    `86/0/0` at the tip, fixture and red arm ok) but its frozen landing predicate missed and its
    stricter amendment cannot be met; an unqualified "operability improved" would contradict the
    C2 record. Calibration 7's target is met at both revisions only serially, and the amended
    instrument returns `mismatches=1` under the wave's own concurrency; so calibration should be
    reported as "met at the landing commit and at the tip when serialized, with the collision routed",
    not as an unqualified improvement. Coverage's C3 is the only claim that survives unqualified at
    both checkpoints under both instruments.

## Attack log

| attacked item | verdict |
|---|---|
| C1 met at `7b16731` (v1 and A3) | HOLDS — reproduced |
| C1 met at the final tip, serial | HOLDS — reproduced under v1 and A3 |
| C1 met at the final tip as a revision-only predicate (concurrency) | BROKEN — `mismatches=1` twice with two instances; cause located |
| C2 missed its frozen kill rule at `68447afe` | HOLDS (the miss is real) — reproduced with the finding line |
| C2's miss attributable to C2's own bytes | BROKEN — the dangling pointer is C1's `SCORECARD.md:322`; the prereg's separability sentence is false |
| C2 target at the tip under v1 | HOLDS — `86/0/0`, all arms ok |
| C2 target under A1 at the tip | BROKEN — `regress_full=differs` is an instrument defect, unfixable without another amendment |
| C3 met at landing and tip (v1 and A2) | HOLDS — reproduced at the tip |
| r29 carry / D4 correction | HOLDS — findings 7 → 0, carry verbatim on the spot-checked row |
| Q4 bar for the C3 fixture | BROKEN — test fails, `/tmp` accepted, no disclosure |
| round-30 `## Mistakes` mined as planned | MISSING at the tip — record only |
| expansion improved | DEFECT-NOT-FATAL (Finding 4 conditions it) |
| quality unchanged | HOLDS against the strict LEARNING observable; the r29 precedent is the live counter |
| discernment unchanged / `unprovable-but-better` | HOLDS (unchanged); the latter is inadmissible |

## Deliveries

- This report only: `.ufo/waves/round-30/w2/SwarmCritic24.md`. All cited bytes are inlined above; no
  receipt file was created (the seat's item names no delivery file). Scratch
  `/fast/scratch/hyaku/souji-r30/SwarmCritic24/` removed after the runs.
