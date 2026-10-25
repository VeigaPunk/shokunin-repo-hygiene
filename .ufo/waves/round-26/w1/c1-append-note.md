# C1 r26 append-only note — scribe deliverable (ScribeC1Note)

State at HEAD `07f83e69979b1032f9de4fe876739a8dccc7242b` (branch master), after the wave landed:

- `d6fe8a1` appended `### Round 26 append-only corrections` at SCORECARD EOF (heading now :239),
  built from this seat's first draft text.
- `07f83e6` appended the two r24 capability rows at SCORECARD.md:155-156 (amendment-2 span 5,
  absent at the C1 landing `a529c76`).
- LOG.md still has **no** Round 26 block (last block is the Round 25 one at :1723); block 2 below
  is still the deliverable, updated to the post-repair state.

Two consequences of that landing order, both measured this run:

1. The landed note's `post-C1 a529c76` column says :199/:200 for the `:224`/`:225` rows. After
   `07f83e6` inserted two lines at :155-156, those two bullets are at **:201/:202**. The landed
   table is one commit stale in exactly the way the note documents. Fix = the appended delta in §1
   (an append, not a rewrite: the section is append-only).
2. The frozen C1 counters stayed green through the omission: at `4453128` (span 5 absent) and at
   `07f83e6` (span 5 present) `bash census/round-26/c1-counter.sh` prints the same
   `markers=0` / `headings=17 44 78`. K1/K2 cannot see span 5. Recorded as a finding, not a
   counter-value dispute.

---

## 1. Append to SCORECARD.md's Round 26 note (after the "Re-derivation per cell" sentence, :261)

Paste verbatim as a new final paragraph of the existing `### Round 26 append-only corrections`
section. Do not edit the table above it.

```markdown

R26-C1b (dated 2026-10-25, `07f83e6`): the post-C1 column above is a measurement at `a529c76`,
not a contract. `07f83e6` appended the two r24 capability rows at SCORECARD.md:155-156
(amendment 2 span 5, absent at `a529c76`), so the `:224` and `:225` rows now resolve at :201 and
:202 instead of :199 and :200; the `:181`, `:180` and `:92` rows are unchanged at :51, :50 and
:153 because they sit above the insertion. Re-derive per cell; never carry this column across a
commit that inserts lines above a named line.
```

---

## 2. LOG.md Round 26 block

**Placement:** append at LOG.md tail (1741 lines; last section is `### Round25 final evidence
addendum`). Style follows the Round 25 block: named-claims paragraph, per-claim paragraphs with
receipts, provenance/mistake paragraph, standard tail. Fill every `RECEIPT-PENDING`.

```markdown

## 2026-10-25 — Round 26: SCORECARD scaffold cleanup, F1 trigger-set assimilation, axis-of-surface checker

Three claims were frozen in `.ufo/waves/round-26/preregistration.txt` at lane base `0eca7c8`
with two pre-data amendments: 1 corrected C2's K4 after-literal from r25's stale
`grounded=8 … kill_tested=6` to the base-derived `grounded=9` / `kill_tested=7` (the R25-M1
mistake class, caught by re-deriving the counter at the named base before any seat scored),
and 2 restated C1's kill rule as byte-content spans rather than base line positions, because
the newest-first reorder the K2 counter demands necessarily moves the protected spans.

C1 calibration (7). The r24 generation scaffold — base lines 170-230: the "Insert the table
below …" instruction, fences holding a second copy of the Round 24 table, the two r24
capability rows and the two planned bullets, the "Optional same-landing correction" paragraph
— is deleted, and its payloads are integrated exactly once: the Round 24 measurements table
above `### Round 23 measurements`, one dated R3 note appended to the `blob-bound receipts
(r23)` row (:153), the two r24 capability rows after `record agreement audit (r23)`
(:155-156), and the two planned bullets in `## Planned` (:201-202). Counter
`bash census/round-26/c1-counter.sh`, tool sha256 `c8dbb76c…`, same bytes both ends: base
`markers=2 headings=17 175 231` (`census/round-26/records/c1-before.tsv`, rev `12fd90bc…`,
whose SCORECARD bytes are identical to the frozen base `0eca7c8`) → landing tip `markers=0
headings=17 44 78` (`census/round-26/records/c1-after.tsv`, rev `a529c762…`, green receipt
`4453128`). The measurement headings read Round 25 (17) < Round 24 (44) < Round 23 (78),
newest first per the file's own contract. The do-nothing control is the base run itself:
untouched bytes score `markers=2`.

The first C1 landing `a529c76` shipped spans 1-4, 6 and 7 byte-equal but omitted amendment-2
span 5's two capability rows (fenced originals `0eca7c8:213-214`; zero hits for
`debris census (r24)` at that rev). `07f83e6` repaired it with rows byte-equal to the base
fence, re-verified all protected spans byte-equal, and left the counter unchanged. The frozen
K1/K2 instrument cannot see span 5 — it printed the same `markers=0` / `17 44 78` before and
after the repair — so this omission was invisible to the labeled counter and was caught by a
span check, not by scoring. RECEIPT-PENDING: whether the C1 green-after receipt is re-run at
`07f83e6` (its literal triple is unchanged; its bound rev is `a529c76`).

`d6fe8a1` appended the `### Round 26 append-only corrections` section mapping the five bare
`superseded by SCORECARD.md:<n>` lines to their targets. Those five lines name pre-cleanup
coordinates (:181, :180, :92, :224, :225) and are left byte-verbatim. Four of the five already
resolved one line early at the frozen base, because r25's landing `728b2ce` inserted the
`- **r25 — attempted, honest stop …` bullet at SCORECARD.md:136 and shifted every later line by
one; they were exact at the r25-base/r24-tip layout (`a6d2d15` / `315422b`), where :180 is the
C3 row, :181 the assimilation row, :224 the r24 bullet and :225 the r25 bullet. Post-cleanup
they resolve at :50, :51 and :153; the two planned-bullet rows moved to :201-202 when
`07f83e6` inserted the capability rows, so the landed table's :199/:200 pair is superseded by
the appended R26-C1b paragraph. RECEIPT-PENDING: R26-C1b landing commit.

RECEIPT-PENDING: C2 coverage — gate `entries=2 ok=2 fail=0`, registry row count 127 → 132,
K1 `ground: F1` count 0 → 2, K4 `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7
kill_violations=0`; receipts `c2-before.tsv`, `c2-k4-base.tsv`, `c2-after.tsv`,
`c2-k4-after.tsv`, `c2-gate.tsv`.

RECEIPT-PENDING: C3 operability — `python3 -B tools/souji-axis-check.py --prereg
.ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0` at
the tip; `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` →
`cases=12 pass=12 control=FALSE-GREEN-REJECTED`; receipts `c3-before.tsv`, `c3-after.tsv`.

RECEIPT-PENDING: SOURCES row count and validation rc, tier/status deltas, and the assimilation
outcome (2 staged packages admitted, 1 language-edition subset refused with its reason and flip
recorded in the round lesson Gate).

R26-M1 is the r25 C2 axis misattribution mined this round (attribution/scope; fix = the C3
instrument plus QUALITY Q59). RECEIPT-PENDING: further r26 mistake rows, which should cover
(a) the four stale superseded-by coordinates and (b) the span-5 omission that the K1/K2
instrument could not see.

RECEIPT-PENDING: wave seat counts and dead/cancelled seats from
`.ufo/waves/round-26/w1-spec.json` and `.ufo/waves/round-26/w1/swarm-registry.json`.

Tool installs: RECEIPT-PENDING (none performed by the C1 note seat). No L0 question;
certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged. Round disposition:
RECEIPT-PENDING: admission verdict per claim.
```

---

## 3. Measured facts (re-derivable)

All at HEAD `07f83e6` unless a revision is named; `b` = `git show 0eca7c8:SCORECARD.md`,
`t` = `git show 07f83e6:SCORECARD.md`.

| what | value |
|---|---|
| counter | `markers=0`, `headings=17 44 78` (same at `4453128`, i.e. before the span-5 repair) |
| base counter (`c1-before.tsv`) | `markers=2`, `headings=17 175 231`, rev `12fd90bc…`, tool sha256 `c8dbb76c…` |
| landing counter (`c1-after.tsv`) | `markers=0`, `headings=17 44 78`, rev `a529c762…` |
| file length | 254 at `0eca7c8`; 233 at `a529c76`; 261 at `07f83e6` |
| span1 base 1-16 vs tip 1-16 | byte-equal |
| span2 base 231-254 vs tip 17-40 | byte-equal (24 lines) |
| span3 base 175-207 vs tip 44-76 | byte-equal (33 lines) |
| span4 base 17-62 vs tip 78-123 | byte-equal (46 lines) |
| span5 rows vs base 213-214 | byte-equal at `07f83e6`; absent at `a529c76` |
| span6 bullets | tip :201-202 (was :199-200 at `a529c76`) |
| span7 base 138-169 vs tip 204-235 | byte-equal (32 lines) |
| superseded-by lines | `0eca7c8` 250-254 → tip 36-40, bytes unchanged |
| target rows now | C3 :50, assimilation :51, blob-bound :153 (+R3 note) |
| +1 shift cause | `git log -S'- **r25 — attempted, honest stop' -- SCORECARD.md` → `728b2ce`, inserted at :136 |
| r25-base/r24-tip layout | `a6d2d15` 92/180/181/224/225 = blob-bound / C3 / assimilation / r24 bullet / r25 bullet |
| pre-cleanup base layout | `0eca7c8` 92/181/182/225/226 = same five contents (four +1) |
| independent cross-check | `.ufo/waves/round-26/w1/c1-line-map.md` semantic column agrees on all five post-edit lines (51/50/153/199/200 at `a529c76`); it attributes the +1 to "r25 inserted the scaffold", while the measured cause is `728b2ce` inserting the r25 planned bullet at :136 (the scaffold block itself was introduced at `315422b`: `git log -S'Insert the table below directly above'`) |
