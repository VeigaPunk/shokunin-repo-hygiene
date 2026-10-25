# ScribeQualityQ57 — Q57 / D6 / R24-M2 drafts (round 25, wave 1, scribe)

## Status
STATUS: PASS — draft file written at `.ufo/waves/round-25/w1/quality-q57.md`; red/green arms
proven at lane `6deb53561aace9aa14a399f88cf8150da4d4f4bd`. No lane file edited besides the two
drafts named in this report; no git/jj mutation; no installs.

## Evidence

Draft file: `.ufo/waves/round-25/w1/quality-q57.md` (sections: Q57 QUALITY.md row; R24-M2
old→new log line; D6 mapping statement adopted from ScoutD6Slice; TSV pointer comment lines;
q57-check.sh with red/green/control runs).

Red arm (lane tip `6deb53561aace9aa14a399f88cf8150da4d4f4bd`):

```
$ bash q57-check.sh /home/vgpnk/Projects/shokunin/souji-shokunin \
    census/round-24/records/slice-verdicts.tsv \
    .ufo/waves/round-24/assimilation/slice-verdicts.tsv \
    corpus/lessons/round-25.md \
    corpus/lessons/round-24.md:240 corpus/lessons/round-24.md:232:S118 LOG.md:1692 SCORECARD.md:181
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
NO-POINTER census/round-24/records/slice-verdicts.tsv
NO-POINTER .ufo/waves/round-24/assimilation/slice-verdicts.tsv
STALE corpus/lessons/round-24.md:240: Tally: 7 accepted, 1 unverifiable, 0 rejected (`slice_verdicts=8 slice_total=8`). These are not lane
STALE corpus/lessons/round-24.md:232:S118: | S118 | unverifiable | DOI → IEEE 202, 0 bytes, twice; quote in IEEE staging + PDF mirror; venue cell wrong |
STALE LOG.md:1692: only), 4 rejected. Quarantine slice 8 rows: 7 accepted, 1 unverifiable
STALE SCORECARD.md:181: | assimilation (rides inside C1; no claim slot) | coverage 8 | F2 grounded entries 2 (`ground: F2` lines at `a
q57=FAIL
rc=1
```

Green arm (scratch `/var/tmp/souji-r25-ScribeQualityQ57/green/`: same five files at `6deb535` +
two pointer comments + one appended `superseded by` note per site):

```
recount census/round-24/records/slice-verdicts.tsv: 8 accepted
POINTS census/round-24/records/slice-verdicts.tsv -> corpus/lessons/round-25.md
POINTS .ufo/waves/round-24/assimilation/slice-verdicts.tsv -> corpus/lessons/round-25.md
SUPERSEDED corpus/lessons/round-24.md:240
SUPERSEDED corpus/lessons/round-24.md:232:S118
SUPERSEDED LOG.md:1692
SUPERSEDED SCORECARD.md:181
q57=PASS
rc=0
```

Controls (all fail as designed): one-sided mapping pointer (`NO-POINTER`); authoritative-class
swap S114→`refused` (recount `7 accepted, 1 refused`, all four sites `STALE`); superseded note
without the exact `file:line` (`STALE`); S118 revert to `unverifiable` makes tally sites
`AGREE` — the check verifies agreement, not correctness (documented limitation).

Script sha256: `9b3d8f58dac13b0d506de859d1052a493ccdd4d00182e46eaad7a5a434237e3a`.

## Findings

1. **Criterion shape.** Q57 as drafted names one authoritative file
   (`census/round-24/records/slice-verdicts.tsv`), requires quoted tallies to match a recount or
   carry an appended `superseded by` note naming the exact citing `file:line` and the recounted
   figure, and requires any disagreement fix to either make artifacts agree or ship a mapping
   both files point to (a one-sided mapping does not close it). Motivating evidence points to
   R24-M22 (`corpus/lessons/round-24.md:170`).
2. **The two TSVs currently name no mapping, and four records quote a stale tally.** The red arm
   shows `NO-POINTER` on both TSVs and `STALE` at round-24.md:240, round-24.md:232 (S118 row),
   LOG.md:1692 and SCORECARD.md:181. All four stale mentions were written in `315422b`, the same
   commit that re-graded S118 to `accepted` (ScoutD6Slice finding F3ii corroborates).
3. **Mapping statement adopted from ScoutD6Slice verbatim** (per assignment): gate record =
   `census/round-24/records/slice-verdicts.tsv`; detail map present/present-via-mirror/
   present-quote-needs-fix → `accepted`; S126/S138 are r22 `present` → r24 `accepted` by
   declared collapse, not re-grade; S118 is the only re-grade (r22 `unverifiable` → r24
   `accepted`, flip round 22 named); r22 TSV stays frozen 5/2/1/0; tally r24 = 8 accepted.
4. **Sibling divergence on S126/S138.** ScoutD6Slice frames the r24 `accepted` for S126/S138 as
   a declared collapse of round 22's `present` (A6: header must state it). ScribeD5D6 calls the
   same pair "disclosed drift, not repaired" and says re-classing to `present` is a decision for
   a re-opening round. Both agree the classes stand unmodified this round; the conflict is over
   narrative only. I adopted ScoutD6Slice's mapping per the assignment; the divergence is
   reported to the L1 for the lesson's final wording.
5. **Line-number pointer drift.** The round-24 lesson's R24-M2 row said the marker should name
   `:504`; both README patch drafts (readme-patch.md, readme-patch-2.md) and ScoutScorecardLines
   target the row at `:517`. The draft's old→new log line records the appended span
   `; superseded by Round 24 F2 row (:517)` (readme-patch-2 spelling) and notes the `:504` vs
   `:517` distinction explicitly.
6. **Check limits disclosed** in the draft: agreement ≠ correctness (revert control); row-level
   sites can only be `SUPERSEDED` when the row retains another class token; SITE list is an
   explicit enum; the script does not verify mapping-vs-detail-table consistency (ScoutD6Slice's
   cross-table check remains a separate instrument).

## Attack log
None (scribe seat; no falsification item). Q57's own limits are disclosed as findings 6.

Scratch `/var/tmp/souji-r25-ScribeQualityQ57/` removed after this report. The draft embeds the
full check script, so no scratch is needed to reproduce the arms.
