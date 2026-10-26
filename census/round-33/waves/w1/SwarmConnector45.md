# SwarmConnector45 — round 33 w1 recurrence scan

## Status

STATUS: PASS — all 16 mistake classes from rounds 28–32 (`## Mistakes` tables in
`corpus/lessons/round-28.md`…`round-32.md` plus the Step-1/`## Routed defects` lists in the five
verifier spot-checks) inventoried with rounds and locations; each class mapped against the frozen
round-33 design (preregistration, both counters, both frozen TSVs, feasibility receipts, QUALITY
Q70–Q74) with a closed/partial/open/N/A verdict and the specific closing element. Deliverable
written: `.ufo/waves/round-33/w1/deliver-recurrence.md`.

## Evidence

- Mistakes tables read: `corpus/lessons/round-28.md:31`, `round-29.md:75`, `round-30.md:61`,
  `round-31.md:93`, `round-32.md:73`. Routed-defect lists read:
  `round-28-verifier-spotcheck.md:110`, `round-29-verifier-spotcheck.md:121`,
  `round-30-verifier-spotcheck.md:129`, `round-31-verifier-spotcheck.md:126`,
  `round-32-verifier-spotcheck.md:128` (routed item 2 read in full — the C2 subjects O1–O5).
- Frozen design read at preregistration commit 2d9bca55a9f042a2c9ed60a797a8069e74c41f46:
  `census/round-33/preregistration.txt`; `census/round-33/c1-counter.py` (docstring + judge);
  `census/round-33/c2-counter.py` (docstring + run/leg loop); `census/round-33/c1-items.tsv`;
  `census/round-33/c2-legs.tsv`; `census/round-33/records/feasibility.txt`;
  `corpus/QUALITY.md:175-179` (Q70–Q74).
- Verbatim anchors (bytes opened this run): r28 spot-check Step-1 "No step-1 defect."
  (`round-28-verifier-spotcheck.md:23`); r29 junk-control result "BAD-CAUSE(original at
  parent=False at cause=False; need True/False)" (`records/feasibility.txt`); r32 routed-2
  "fix the trailing-slash TMPDIR regressions in tools/souji-census.sh:1990" (`round-32-verifier-spotcheck.md`).
- Lane tip observed read-only: `git -C … log -6` → a416d0b (C1 restatement rows landed),
  fef88f2 (C2 O1 feasibility leg), 3aec290 (do-nothing controls re-run), 2d9bca5 (preregistration);
  `git status --porcelain` empty.

## Findings

1. **Design closes the three rejected closures' common cause.** r30/r31/r32 were rejected because
   frozen targets were unreachable by honest work (r30 C2 dangling=1; r31 C1 L29 unbindable; r32
   C1 shared-occurrence/digit-unit enumeration, C2 moving anchor + pin consumers). Round 33's
   Q70(a) feasibility legs reached the item-level targets before freeze (C1: both restatement
   kinds AGREE at 190b4b1; C2: O2/O4 PASS at 6a409e1), and Q70(b)/Q70(c) close the flaky-anchor and
   moving-anchor classes for C1 ("no item's anchor counts lane files; K22 reads fixed historical
   revisions only").
2. **The four named example classes resolve as follows.** (a) Citing a wave path before its
   capture lands (C10): closed at claim level — restatement statements must be digit-bearing
   lines of the executed run; no frozen artifact cites a wave path. (b) A gate reading reported
   without a committed run (C16): partially closed — the predicate is a re-runnable printed line
   and controls were re-run at the preregistration commit (lane commit 3aec290), but committing
   the landing/tip receipts remains L1 process, falsifiable by any seat. (c) A frozen anchor that
   moves with lane content (C4): closed for C1 by Q70(c); re-enters inverted for C2 — the six
   no-harm guards compare rev output to a live base re-run, so post-landing lane traffic that
   legitimately moves a guarded count yields harm>0 at the tip without a C2 fault (accepted by the
   Separability clause). (d) A predicate a constants fixture meets (C6): closed for C1 (executed
   cause; both junk controls BAD-CAUSE) and for O1 (strace creation-count condition); partially
   open for O2/O3 — sandbox-nt legs have no creation-count condition, and the closing elements are
   the G4/G5 digest pins plus Q73 re-pin sequencing, not the legs' own predicates.
3. **Class inventory with rounds** (deliverable Part 1): stale-premise r28,r30; contract r31,r32;
   enumeration r32; anchor-selection r32; flaky anchor r32; instrument/vacuous r29–r32; harm
   digest-pinned r32; harm write-scope widening + misroot r32; number-drift r29; reference-drift
   r29,r30; attribution r29; landing r30,r31; record r31; disposition r31; scope r29,r30;
   recording (spot-check class) r28–r32.
4. **Not claimed, not closed:** landing-gate committed-report discovery (r28 routed 3, r30 C2),
   disposition honesty of future carry sections, heredoc-record discipline — all lane-process,
   outside the two frozen claims (deliverable Part 2 verdicts N/A).
5. **No frozen predicate, target, counter, item or leg is attacked.** One design observation is
   reported as analysis, not attack: the C2 guard anchor exposure (finding 2c) and the sandbox-nt
   seam (finding 2d) are disclosed properties of the frozen design, both knowingly accepted in
   the preregistration text; neither violates a frozen rule.

## Attack log

Not an attack seat; no attack filed.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-recurrence.md` — full class inventory + exposure mapping with
  per-class closing elements and residual exposures.
- `.ufo/waves/round-33/w1/SwarmConnector45.md` — this report.

No scratch directory was created (analysis seat; no clones, no counter runs, no installs).
