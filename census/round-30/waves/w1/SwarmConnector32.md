# SwarmConnector32 — cross-claim pattern finder, souji round 30 wave 1

## Status

STATUS: PASS — all six assigned intersections traced against committed bytes
(lane HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658`, base
`9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`); one bounded synthesis move
proposed, no counter/predicate/target touched, no axis harmed.

## Evidence

- Read-only git against the lane: `git log --oneline` (tip df6afe8, ahead of
  base by the 3 pre-data commits), `git ls-tree -r --name-only
  9420341d9a814cb6089c25fb03a4cc9b23dc0d1b census/round-29/waves | grep -c
  '\.md$'` -> **86** (matches the frozen C2 reports= target), and
  `git cat-file -e 9420341d9a...:<path>` -> OK for all ten paths cited inside
  the draft R30-CORRECTION lines (so the appended lines are clean under the
  gate's pointer sweep).
- `census/round-30/records/c1-before.txt` (committed control): base
  `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10`; row R18 already
  exhibits the born-stale append defect.
- `.ufo/waves/round-30/w1/receipt-SwarmExecutor01-c2-counter.txt` at delivered
  gate rev 3408f38: `GATE rc=1 reports=86 cne=0 dangling=0 other=7`, REGRESS
  same both legs — the 7 `other` are the LG-SEAT-UNCARRIED the r29 carry
  block clears.
- Tool bytes read this run: `tools/souji-capability-agreement.py` (corrections
  parsed only from the SCORECARD.md tail; rows frozen as blob at --list-rev),
  `census/round-30/c2-counter.py` (exit 0 ignores `other`; REGRESS legs),
  `census/round-30/c3-counter.py` (L1-L9 legs), `tools/souji-landing-gate.py`
  (sweep sources incl. `corpus/knowledge/*.md` and `corpus/lessons/round-%d.md`;
  POINTER_PATH_RE root prefixes), `tools/souji-registry-agreement.py` K2
  (stale list read from `census/round-29/stale-statements.tsv`: LOG.md:1758,
  SCORECARD.md:23, round-28.md:22,40 — no round-29.md record), fixtures
  r23-record-agreement.py / r29-registry-agreement.py / r24-coverage-agreement.py
  (all synthetic-repo, --root-honouring), `corpus/lessons/round-2[5-9].md`
  ## Mistakes sections.
- Wave deliveries read: deliver-r29-carry-block.md, deliver-r29-gate-correction.md,
  deliver-souji-landing-gate.py/.diff, deliver-c1-corrections-*.txt,
  c1-corrections-acceptance.txt, receipt-c2-fixture-arms.txt,
  deliver-r30-jj-keep-expiry.sh, deliver-jj-keep-expiry-run.txt.

## Findings

1. **C1 R05/R06 x C2 gate change** — `tools/souji-landing-gate.py` is one byte
   stream serving four roles (C2's changed surface, R05's executed command,
   the REGRESS artifact, an LG-PARSE-REG cited script). C1's kill rule at the
   final tip is protected only by C2's REGRESS leg
   (c2-counter.py docstring: "REGRESS ... ok iff (rc, last digit-bearing line)
   are equal"); at delivered rev 3408f38 both REGRESS legs print "same"
   (receipt lines 4-5), so the draft corrections `R05 ... observed=SELFTEST
   pass=65 fail=0` / `R06 ... observed=SUMMARY total=15 failed=0` stay valid
   at any later tip that keeps REGRESS.
2. **C1 corrections x SCORECARD rows the round appends** — one shared tail,
   counter reads only `^R30-CORRECTION ` lines under the base-prefix invariant
   (tools/souji-capability-agreement.py:98 "sc_append = sc_rev.startswith(sc_base)";
   frozen rule: "SCORECARD.md/SHONEN.md at REV must begin with their base
   bytes, else every item counts"). Registry K2 pins SCORECARD.md:23 and
   LOG.md:1758 with the same append-only shape (registry tool :156 "if not
   rb.startswith(bb):"); a single in-place edit anywhere above the tails fails
   C1, registry K2 and the sweep together. New r30 rows are outside C1's
   frozen enumeration (rows_tsv = blob at --list-rev), so nothing re-derives
   their literals — the R18 born-stale pattern
   ("stated=cases=15 pass=15 ... observed=Usage: bash
   tools/souji-wave-evidence-capture.sh ... MISMATCH kind=value") is repeatable
   this round.
3. **C3 fixture x C1 enumeration — confirmed separation.** The fixture
   `tests/fixtures/r30-jj-keep-expiry.sh` cannot enter C1: the row list is a
   frozen blob, no row names it, and a correction `cmd=` override must keep
   the row's first path. Reverse coupling is real, though: the new knowledge
   entry is a gate sweep source (gate `sources` set includes
   "corpus/knowledge/" depth-2 .md files), so every repo-relative token in
   `corpus/knowledge/jj-keep-ref-expiry.md` must resolve at the final tip or
   C2's dangling=0 breaks. C3's own fixture self-refuses to run outside
   scratch (delivery lines 31-35) — the r29 clone-origin mistake class is
   closed here.
4. **r29 carry block x counters — C2-only, and load-bearing.** The gate reads
   `corpus/lessons/round-29.md` (--round 29) for the carry section; C1 and C3
   never read it. With only the gate change, the C2 SUMMARY prints other=7
   (receipt line 1); the carry block is what returns it to 0. Append order
   matters: the D4 `## Gate` H2 and the `## Seat-reported failures` section
   must not interleave, because the gate's section reader stops at the next
   heading.
5. **D4 r29 Gate correction x registry K2 — no disturbance.** K2 records are
   LOG.md:1758, SCORECARD.md:23, round-28.md:22,40 (stale-statements.tsv,
   read verbatim); round-29.md is not a K2 record; `R30-CORRECTION ` cannot
   match the `R29-CORRECTION ` marker filter; R14/R17/R16 fixtures run on
   synthetic repos and are byte-independent of the real lesson.
6. **Recurring mistake classes** (round-25..29 ## Mistakes): number-drift /
   stale literal (r25 R25-M1, r28 stale-premise, r29 row 1 — "the
   committed-bytes count is 152 absent records"), vacuous/gameable counter
   (r29 row 4), scope breach via clone origin (r29 row 5), attribution
   (r25 R25-M2, r29 row 3), reference-drift (r29 row 2). This round's live
   repeats: number-drift on newly appended SCORECARD rows (finding 2) and
   attribution via the `other=` kill-rule tension below.
7. **Contract tension, stated not smoothed** — preregistration C2 says both
   "other= is reported, not targeted" and "Kill rule: any other SUMMARY at the
   C2 landing commit or the final tip is a miss", while the c2-counter exit
   code ignores `other` and the disclosed probe predicts 7 LG-SEAT-UNCARRIED.
   Landing the carry block before the C2 landing commit satisfies both
   sentences literally.
8. **Proposed move** (full detail in the delivery): commit-order +
   append-discipline synthesis — (a) land the r29 carry block and D4
   correction at or before the C2 landing commit, sections kept contiguous;
   (b) author every SCORECARD row appended for r30 from a fresh scratch-clone
   run of its command at the landing rev (or cite a census receipt instead of
   an inline count); (c) mine the class into `corpus/lessons/round-30.md`
   ## Mistakes. Operability and calibration improve; coverage and all
   counters/targets untouched.

## Attack log

Not an attack seat. One contract tension recorded as Finding 7 (other=
reported-not-targeted vs the any-other-SUMMARY kill rule); resolution is
procedural (landing order), not a predicate amendment, so no ATTACK is filed.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-cross-claim.md` — the cross-claim map,
  mistake-class table, tension statement, and the bounded synthesis move with
  L1 verification commands.
- `.ufo/waves/round-30/w1/SwarmConnector32.md` — this report.

No lane bytes outside `.ufo/waves/round-30/w1/` were written; no git/jj
mutation anywhere; no tools installed (none needed). Scratch: none created
beyond reading committed blobs and wave-1 deliveries; nothing left on disk.
