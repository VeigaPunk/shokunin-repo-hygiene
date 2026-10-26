# SwarmConnector36 — cross-claim pattern finder (read-only)

Report: .ufo/waves/round-31/w1/SwarmConnector36.md
Delivery: .ufo/waves/round-31/w1/deliver-cross-claim.md

## Status

STATUS: PASS — all four connector questions answered from bytes opened this run (C1 mis-parse
hazard: real but shape-specific; C2↔C1 L06/L07/L40 coupling: quantified at base; M1↔C2
sequencing: no hard dependency, denominator verified; C3↔C1: verified no touch), plus a
mistake-class table for rounds 26-30. No counter, predicate or target is challenged; nothing
here is an ATTACK.

## Evidence

- Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; preregistration commit
  `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; freeze commits ed17ff6 (controls+A0), 1b81136
  (C1 base output + M1 red-before); HEAD 1b811368461785040e955f41f9c97e62f61fd67c. SCORECARD.md
  is byte-identical base..HEAD (git diff --name-only).
- C1 counter at base (command:
  `python3 -B tools/souji-capability-cells.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --scratch /fast/scratch/hyaku/souji-r31/SwarmConnector36/c1`):
  `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` — matches controls.tsv.
  Key ITEM lines: L06 `RUN-MISMATCH ... observed=SELFTEST pass=65 fail=0`; L07
  `RUN-MISMATCH ... observed=SUMMARY total=15 failed=0`; L40 `MATCH ... cases=7 pass=7 control=FALSE-GREEN-REJECTED`.
- Round-26 report arithmetic at base (`git ls-tree -r --name-only 9f17a1e -- .ufo/waves/round-26/`
  and `-- census/round-26/waves/`): ufo=466, census=495, distinct relpaths=495; all 29
  capture-only reports swept for the gate failure vocabulary (`STATUS: fail|partial|...` prefix
  regex from tools/souji-landing-gate.py:93-103): zero hits. Rounds 27/28: ufo=0, census=94/61.
- M1 red-before receipt (census/round-31/records/m1-red-before.txt): round 26 `findings=18 ...
  checked_reports=466 carry_heading=0`; round 27 `findings=29 ... checked_reports=94`; round 28
  `findings=21` (19 LG-SEAT-UNCARRIED + 2 LG-DANGLING-PTR at
  corpus/lessons/round-28-verifier-spotcheck.md:36,71) `checked_reports=61`.
- Lesson headings at base (`git show 9f17a1e:corpus/lessons/round-2{6,7,8}.md | grep -n '^## '`):
  no `## Seat-reported failures` in any of the three (round-26 has Gate/Findings/Residuals/
  Receipts/Mistakes table; round-27 Gate/Findings/Residuals/Receipts/Mistakes; round-28
  Gate/Findings/Receipts/Mistakes/Residuals/Wave).
- ROW-shaped rows in SCORECARD at HEAD: none
  (`grep -nE '^\|\s*L[0-9]{2}\s*\|\s*SCORECARD\.md:[0-9]+'` on `git show HEAD:SCORECARD.md`).
- Fixture pins read at base: tests/fixtures/r30-landing-gate-discovery.py D3
  ("both present, same relative report path, different bytes. The capture copy carries no
  STATUS line" → checked_reports=1, status_lines=1) and D1-D7 case list; gate reader
  tools/souji-landing-gate.py:391-403 `failures_section_lines` stops at the next heading;
  pointer sources list tools/souji-landing-gate.py:962-971 includes SCORECARD.md and all
  corpus/knowledge/*.md; CARRY_TOKEN_RE tools/souji-landing-gate.py:111
  `(?i)\bopen\b|resolved@[0-9a-f]{7,}`.
- Quotes (bytes opened this run): tools/souji-capability-cells.py docstring
  "Effective statement of an item at REV: the LAST row, in the part of SCORECARD.md after the
  --base bytes, of the form" (line 12); corpus/lessons/round-30.md ## Mistakes
  "cites the wave path `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`" (line 63);
  census/round-31/records/amendments.txt A0 "the fixture is run once more with PATH led by a
  shim dir whose jj and git log their argv" (L12, why-block).
- No installs/upgrades this run; no lane git/jj mutation; scratch
  /fast/scratch/hyaku/souji-r31/SwarmConnector36 removed after use.

## Findings

1. C1 mis-parse hazard is real but shape-specific (deliverable §A). The counter's effective
   statement is the LAST `| Lnn | SCORECARD.md:<line> | <literal> | run/record: ... |` row per
   item anywhere in the append tail; a later measurement-table row in that exact column order
   silently supersedes a correct binding row and can flip the item to RUN-MISMATCH/BAD-ROW at
   the tip. Safe today: zero such rows at HEAD, R30-CORRECTION lines are space-separated and
   structurally cannot match, capability-row tables name the capability in cell 1. L1
   mitigation: keep C1 binding rows last among Lnn-shaped rows, or give measurement tables
   distinct first two cells.
2. SCORECARD.md is a gate pointer source (tools/souji-landing-gate.py:962-971), so C1's appended
   rows sit inside C2's scanner at the tip. The run/record shape rules keep the cells clean;
   the exposure is any `.ufo/waves/round-31/` token in a note cell before the capture lands —
   the exact r30 reference-drift mistake (round-30.md ## Mistakes row 2). C2's frozen LANE leg
   reads content at BASE, so C1 rows cannot move fp=0.
3. C2↔C1 coupling is concentrated and quantified (deliverable §C): L06 and L07 are already
   RUN-MISMATCH at base (observed `SELFTEST pass=65 fail=0`, `SUMMARY total=15 failed=0`), and
   C2's REGRESS leg pins those last lines equal base↔rev, so C1 must supersede both via appended
   rows regardless of C2. L40 MATCHes at base and is the live axis-harm path: a C2 fix that
   breaks any r30-fixture case flips REGRESS to differs (C2 miss) and L40 to RUN-MISMATCH at
   the tip (C1 miss, C1 unchanged). The unique fix shape satisfying D3 + G1 + G2 together is
   union keyed by relative path with .ufo bytes preferred.
4. M1 has no hard sequencing dependency on C2 (deliverable §D): lessons 26/27/28 have no carry
   heading at base, so M1's single end-of-file section is readable even by the base
   first-section reader. C2's union fix raises round-26 checked_reports 466→495, but the sweep
   shows the 29 capture-only reports carry no failure-vocabulary STATUS lines, so M1's
   red-before-sized carry lists stay sufficient; rounds 27/28 are capture-only trees (union
   inert). Round-28 tip green additionally needs C2's tokenizer (2 dangling pointers in the
   verifier-spotcheck, G6/G8 classes). Mid-file-section lessons (15/19/23/24/25) are the ones
   that truly need C2's multi-section reader before any append-only fix is decidable.
5. C3↔C1 is a verified negative (deliverable §E): the frozen enumeration and every record-round
   set are ⊆ r12-r30; C3's new files are outside C1's counter, C2's REGRESS set and C2's LANE
   content. Sole shared surface: the C3 entry is a corpus/knowledge/*.md gate pointer source at
   the tip — clean by construction, provided wave-2 edits keep cited paths committed.
6. Recurring mistake classes and round-31 repeat vectors are tabulated in deliverable §F;
   highest-probability repeats: (a) wave-path-before-capture citations from wave-2 SCORECARD
   rows and delivery files; (b) uncarried wave-2 STATUS failures if the lesson carry is authored
   before wave 2 lands; (c) sentence-to-record overreach in C3 entry prose beyond L10's
   backticked-RESULT coverage; (d) stale-receipt citations at the tip.

## Deliveries

- .ufo/waves/round-31/w1/deliver-cross-claim.md — the cross-claim analysis (sections A-F).
