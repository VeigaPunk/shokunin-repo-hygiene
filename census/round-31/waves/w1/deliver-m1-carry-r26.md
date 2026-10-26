# deliver-m1-carry-r26 — append-only `## Seat-reported failures` for corpus/lessons/round-26.md

Mined mistake M1 (wave 1, round 31). Target file: `corpus/lessons/round-26.md`
(96 lines at lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; the file
carries `## Gate`, `## Findings`, `## Residuals`, `## Receipts`,
`## Mistakes table` and no failure-carry section).

Landing instruction for the L1: append the block below verbatim at end of file
(after the last `R26-M1` mistakes line, preceded by one blank line; the block
ends with a newline). Nothing above it changes: this is append-only.

## Red-before (base content, base gate)

Gate bytes: `tools/souji-landing-gate.py` blob
`51f98ed7f9b6cf834e93be94c6bbdd9e392e17a6` — identical at base `9f17a1e` and
at lane tip `1b81136`.

```
python3 -B <base gate> --root <clone> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --round 26 --fleet-root /home/vgpnk/Projects/shokunin
rc=1
SUMMARY	findings=18	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=69	carry_heading=0	checked_reports=466
18 LG-SEAT-UNCARRIED, 0 other ids
```

Red-before, capture-only arm (the base gate never reads these; swept with the
gate's own `seat_failure_lines` / `status_paragraph` / `carries` imported from
the base gate by path):

```
before(base lesson) cap_only_reports=29 paragraphs=8 carried=0 uncarried=8
```

So 26 committed seat failure paragraphs are uncarried at base content: 18 over
the 466 reports under `.ufo/waves/round-26/` (gate-visible) and 8 over the 29
capture-only `.md` under `census/round-26/waves/` (gate-blind).

## Block to append

```
## Seat-reported failures

Append-only carry of the round-26 committed seat STATUS failure lines (26 across
the 466 reports under `.ufo/waves/round-26/` and the 29 capture-only `.md`
under `census/round-26/waves/`); one bullet per STATUS paragraph, quote first,
disposition last.

## Seat-reported failures

Append-only carry of the round-26 committed seat STATUS failure lines (26 across
the 466 reports under `.ufo/waves/round-26/` and the 29 capture-only `.md`
under `census/round-26/waves/`); one bullet per STATUS paragraph, quote first,
disposition last.

- .ufo/waves/round-26/w1/CritAmendNeed.md:5 — STATUS: PARTIAL — all three holes are real, and they are not the same kind of hole. (a) R2's neutral classes are undefined in the contract and the landed rule is unbounded (any unknown token is neutral), but it cannot be closed this round without changing frozen fixture cases 3, 7 and 10, which is forbidden. (b) net-new rows is the right direction (supersede is an appended correction row, never an edit), but row count 127 -> 132 is not an append-only predicate: it accepts delete-1-add-6 and base-row rewrites, and the validator has no base revision. (c) Amendment 2 is necessary and its Axes/Planned treatment is correct, but its enforcement sentence is unsatisfiable for region 5 because item 5 itself mandates a mid-span edit; it also drops base 170-171 silently, carries no red-arm receipt, and is absent from LOG.md. Amendment 3 (text below) is proposed for (b), (c) and a C3 scope disclosure; no predicate, target, case set or axis is relaxed by any clause. — open
- .ufo/waves/round-26/w1/CritCoverageCredit.md:5 — STATUS: FAIL — C2's coverage credit is not an expansion: F1 is held ground at base and the map still says so at tip, K1's grounded_f1 0→2 counts front-matter labels (base 0 is an artifact of the two held F1 entries carrying no ground: line), and the frozen K2 gate is red on the committed entries (entries=2 ok=0 fail=2, rc 1) with two of the five required receipts absent and the two K1 receipts refusing verify. — open
- .ufo/waves/round-26/w1/CritQ54Gate.md:3 — STATUS: PARTIAL — Q54's applicability holds on the staged entry bytes (entries=2 locators=2 locators_bad=0), but the instrument the prereg binds for C2's Gate (K2, tools/souji-gate-check.py) cannot resolve any locator, no frozen C2 counter or receipt runs Q54, and at HEAD both admitted entries carry no ## Gate at all (K2 rc=1) while Q54 reports UNSCOPED and exits 0. — open
- .ufo/waves/round-26/w1/CritSourcedClaim.md:5 — STATUS: FAIL — the ticket's specific hypothesis is disproved (no landed row reuses the campaign date; all five new rows read opened=2026-10-25), but the §2b sourced claim is still unsupported as landed: the frozen K2 gate that adjudicates it is RED at the tip (entries=2 ok=0 fail=2, exit 1, both check1-no-gate), the §2b attestation (lesson Gate: URL + access date + ≤25-word located quote per new row) was dropped between the wave drafts and the landing, and two prereg-mandated receipts do not exist. C2's own kill rule (K2 exit != 0 or ok != 2) is met. — open
- .ufo/waves/round-26/w1/ExecC1Surgery.md:4 — STATUS: PARTIAL — the three draft files are delivered and verified (frozen counter on the draft: markers=0, headings=17 44 78), but the landed tip a529c76 violates amendment 2 item 5: both r24 capability rows are absent. Also: the brief's literal layout design contradicts the frozen K2 order; I delivered the counter-correct order (r25 first) and document the conflict instead of implementing it. — resolved@07f83e69979b1032f9de4fe876739a8dccc7242b
- .ufo/waves/round-26/w1/LabReceiptVerify.md:5 — STATUS: FAIL — 3 of the 4 committed red-before receipts refuse verify (RECEIPT-COUNTS-ABSENT): c1-before, c2-before, c3-before. Only c2-k4-base is verify=ok. Each receipt's payload is nonetheless byte-identical to a fresh run at its recorded rev, so the measured numbers stand; the frozen prereg's clause "each verify=ok" (preregistration.txt:65, :144) is unearned for those three. Verified against committed blobs at HEAD ea0bbe66c974062984134bb5b491b21bbb3c17d7 (and identically at d6c13b0, 89e0fce). — open
- .ufo/waves/round-26/w1/LabSourcesCensus.md:9 — STATUS: PARTIAL — every requested census arm and the fleet validator return zero at the frozen rev 89e0fcee, with the controls proving each arm can fire; but five registry rows violate the status/used-by contract (/home/vgpnk/Projects/shokunin/CORPUS.md:103,107) and no arm in the specified set can see them. The assignment's CORPUS.md lane path does not exist at any revision. — open
- .ufo/waves/round-26/w1/RevC1Counter.md:2 — STATUS: PARTIAL — K1 and K2 do not fully establish the stated scaffold-removal and ordering conditions. — open
- .ufo/waves/round-26/w1/RevC3Design.md:4 — STATUS: FAIL — the C3 checker's R2/R4 design is not sound against adversarial preregs; the swept adversarial input (claims=1 flags=0, rc 0) hides every defect C3 exists to catch, and the landed fixture deviates from the frozen 12-case set,including the r25-C2-replica discriminator). — resolved@c5949013f89fe0b8289bdb7050ab64a47e08c911
- .ufo/waves/round-26/w1/RevEntryDrafts.md:2 — STATUS: PARTIAL — Entry A is admit-ready; Entry B has a required source-locator correction. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- .ufo/waves/round-26/w1/RevQ59Text.md:7 — STATUS: PARTIAL — the Q59 draft correctly captures the declared-axis-vs-surface-class rule, cites the right lesson intents (r25 C2 axis misattribution + this round's R26-M1), avoids overreach, and does not contradict Q58; but it is not landable as-is: the check column's discriminator conjunct has no executable carrier in committed bytes, and the motivating-evidence anchor corpus/lessons/round-26.md R26-M1 does not exist yet in the committed lesson file. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- .ufo/waves/round-26/w1/RevR25Residuals.md:2 — STATUS: PARTIAL — D1 and D2 are addressed by the frozen plan; D3 is defensibly left untouched under the explicit read boundary; D4 remains operator-owned. — open
- .ufo/waves/round-26/w1/ScribeAxisDocs.md:5 — STATUS: PARTIAL — the three requested drafts are written, quoted and land-pinned at .ufo/waves/round-26/w1/axis-check-docs.md; the two SKILL.md rows pin the frozen K2 literal, which the landed fixture cannot produce (11 cases, --tool ignored), and the tool draft the peer report tells the L1 to install scores 6/12 on the frozen case set. — open
- .ufo/waves/round-26/w1/ScribeGateDraft.md:5 — STATUS: PARTIAL — the Gate draft is written at .ufo/waves/round-26/w1/gate-draft.md with all five ADMIT lines (S128–S132, each with URL/path, 2026-10-25 access, located quote ≤25 words), the REFUSE line for the staged S119/S120/S121 subset, the five old→new pairs, and the search-log note; it cannot be scored/landed as a green Gate because C2's frozen K2 fails against the tree as it stands (both entries have no ## Gate heading) and the in-tree lesson Gate states a refusal reason that conflicts with the prereg's. — open
- .ufo/waves/round-26/w1/ScribeLessonR26.md:5 — STATUS: PARTIAL — the r25-shaped lesson draft is delivered at .ufo/waves/round-26/w1/lesson-r26.md, but two of the round's frozen counter arms do not hold at the tip revision I read: C2's K2 exits 1 (check1-no-gate on both admitted entries) and C3's K2 prints cases=11 pass=11 against a frozen cases=12 pass=12 control=FALSE-GREEN-REJECTED. I drafted the verdicts from measured bytes instead of asserting the prereg's after-values. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- .ufo/waves/round-26/w1/ScribeLogR26.md:8 — STATUS: PARTIAL — the block is drafted with measured literals, but two frozen-counter conflicts must be resolved by L1 before the block is true: C2's K2 gate check is RED at the tip (entries=2 ok=0 … fail=2, rc 1), and C3's K2 prints cases=11 pass=11, not the frozen cases=12 pass=12. Wave/dead-seat totals and admission verdicts remain RECEIPT-PENDING. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- .ufo/waves/round-26/w1/ScribeScorecardR26.md:5 — STATUS: PARTIAL — the draft (.ufo/waves/round-26/w1/scorecard-r26.md) is complete in all four requested parts with RECEIPT-PENDING where the L1 must fill, but the round cannot report PASS: C2's frozen K2 gate is red at the tip (entries=2 ok=0 fail=2) and C3's committed fixture is the 11-case bytes against a frozen 12-case contract. C1 is green on its counter. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- .ufo/waves/round-26/w1/SentBounds.md:3 — STATUS: PARTIAL — no step in the round-26 work plan writes outside the hard bound, but the bound text names a non-existent path, the frozen receipt instrumentation is not runnable as written and does not verify, the C3 fixture case set was cut 12->11 without an amendment, and the C2 gate's scratch path is already occupied. — open
- census/round-26/waves/w1/CritEntryB.md:12 — STATUS: FAIL — the reviewed entry's strongest claim, "all four commands prune (2->1)", is falsified by the campaign fixture's own case bodies (pull is never invoked; merge and rebase are confounded by a plain git commit), and its verified-at: does not distinguish "campaign measured" from "this lane measured". The review itself completed on every assigned point. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- census/round-26/waves/w1/CritNoHarm.md:9 — STATUS: PARTIAL — the r24 fence→section surgery loses no payload and C2/C3 reproduce their frozen counters, but "no axis is harmed" fails on calibration: the same round appends Round 26 measurements below Round 23 (SCORECARD.md:264), so the measurement sections are ordered 25, 24, 23, 26 — neither newest-first (the ordering C1's K2 enforces) nor oldest-first (the file's observed history) — and the frozen K2 cannot see it. Two further calibration defects (stale post-C1 mapping column; c1-after bound to a pre-tip rev) and one coverage defect (incomplete used-by). Operability itself is not harmed. — open
- census/round-26/waves/w1/ExecVerifyLoop.md:5 — STATUS: PARTIAL — the loop is delivered at .ufo/waves/round-26/w1/verify-loop.sh (syntax-clean, 17 checks, exercised on the lane at 166baa18 and on three falsification arms), but the tip commit 166baa1 landed an earlier broken copy of that same script (bash -n rc 2); my fix exists only as an uncommitted worktree edit and this seat cannot commit. Two checks also FAIL at the tip for real reasons (landing gate, receipts) — that is the loop reporting, not a loop defect. — open
- census/round-26/waves/w1/RevAssimRules.md:4 — STATUS: FAIL — C2's frozen K2 gate is RED at the committed tip: entries=2 ok=0 fail=2, exit 1. The admitted entries as committed (0833de9) carry no ## Gate section; the gate passes only on uncommitted worktree bytes. Required receipts c2-gate.tsv and c2-k4-after.tsv are absent from census/round-26/records/. All other §10 rules are satisfied by evidence below. — resolved@50443f5701d0b301f515202c6706f591b2cdf856
- census/round-26/waves/w1/RevC2Scope.md:9 — STATUS: PARTIAL — C2's substance survives all three attack questions (F1 province: yes; ground genuinely uncovered: yes; renumber collision: none) and every frozen counter is green at 33e6807; but the prereg's own receipt clause "each verify=ok" is structurally unmet: c2-before.tsv and c2-after.tsv fail receipt verification (RECEIPT-COUNTS-ABSENT) because the counter's output shape cannot match the verifier's counts-line grammar. — open
- census/round-26/waves/w1/ScoutAssimRegister.md:5 — STATUS: PARTIAL — the full souji slice (8 rows, ids + class cells) is reported and its C2 contact is resolved, but the lane's own r26 slice-verdict artifact is not consumable by the lane's gate tool (accepted-carried is outside the tool's class vocabulary), so the r26 re-check cannot currently be machine-validated. No predicate, target or case set is challenged; the counters are untouched by this seat. — open
- census/round-26/waves/w1/ScoutF1Gap.md:5 — STATUS: PARTIAL — the gap list is delivered in full and the F1 remaining-open-items enumeration is delivered, but two of the three gap-closing evidence claims in the C2 admit set are confounded (the prunable registration is already gone before the measured command runs), and the round's own numerator is already stale at tip. Both are attack-grade findings, not defects in the frozen counters. — open
- census/round-26/waves/w1/ScoutRegroundDocs.md:3 — STATUS: PARTIAL — all three doc/code rows (staged S109/S110/S111 → lane S128/S129/S130) re-ground successfully: every cited locator was opened and confirmed byte-exact this run, and the snapshot bytes are identical to the lane's census/round-26/sources/ copies. Two evidentiary defects are reported as ATTACK-class findings (F4, F5) and one Gate defect (F3) that bear on C2's admit set; no counter or predicate is proposed for change. — open
```

## Proof (scratch clone, origin removed)

Scratch: `/fast/scratch/hyaku/souji-r31/M1CarryR26/`
(`git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"`,
then `git remote remove origin`; `git -C "$D/c" rev-parse --show-toplevel` →
`/fast/scratch/hyaku/souji-r31/M1CarryR26/c` before the first commit).

Append + commit:

```
git -C "$D/c" rev-parse HEAD        -> 1b811368461785040e955f41f9c97e62f61fd67c
git -C "$D/c" commit                -> 3656eac2b73ef50b62bed4a7083fd70663aaba3a
```

Base gate at the appended commit:

```
python3 -B <base gate> --root "$D/c" --rev 3656eac2b73ef50b62bed4a7083fd70663aaba3a --round 26 --fleet-root /home/vgpnk/Projects/shokunin
rc=0
SUMMARY	findings=0	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=18	status_lines=69	carry_heading=1	checked_reports=466
```

Zero `LG-SEAT-UNCARRIED`; `checked_markers=18` (the axis was exercised) and
`carry_heading=1`.

Capture-only arm at the same commit, same gate functions:

```
after(carry commit) cap_only_reports=29 paragraphs=8 carried=8 uncarried=0
```

Mutation control (proves the green is not vacuous): commit
`9aac35839e62c18ec8dcb84dfb48868a98aef6ac` deletes the ` — open` disposition
from the `CritAmendNeed.md:5` bullet only:

```
rc=1
LG-SEAT-UNCARRIED	.ufo/waves/round-26/w1/CritAmendNeed.md	line 5: STATUS: PARTIAL — all three holes are real, and they
SUMMARY	findings=1	...	checked_markers=18	...
```

## Disposition evidence

Bullets carry `open` or `resolved@<full40>`; a `resolved` needs a commit that
fixed or answered the reported failure, and every one below was read from the
clone at the named commit (bytes or receipt).

| report:line | disposition | basis |
|---|---|---|
| ExecC1Surgery.md:4 | resolved@07f83e69979b1032f9de4fe876739a8dccc7242b | commit `07f83e6` "append the two r24 capability rows … wave ExecC1Surgery found omission" |
| RevEntryDrafts.md:2 | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | `census/round-26/records/c2-gate.tsv` (rev 50443f5) `entries=2 ok=2 … fail=0`: gate checks 3-4 (located ≤25-word verbatim quotes) pass on the admitted entries |
| RevQ59Text.md:7 | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | `R26-M1` row and Q59 landed at `166baa1` (lesson + `corpus/QUALITY.md`); the discriminator carrier Q59's check column names is frozen C3 case 1, executable in the adopted 12-case fixture at `c594901` |
| ScribeLessonR26.md:5 | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | K2 arm fixed at `33e6807` (Gate sections, entries=2 ok=2 fail=0); C3 arm fixed at `c594901` (12-case fixture); 50443f5 is the later of the two on the path to base |
| ScribeLogR26.md:8 | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | same two counter conflicts as above. The drafted LOG block itself was never landed — `LOG.md` has no round-26 entry (see report finding 3); that is a separate gap, not this paragraph's stated blocker |
| ScribeScorecardR26.md:5 | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | same two counter conflicts; the r26 capability row exists at `SCORECARD.md:288` and the r26 lesson at `ea0bbe6` |
| CritEntryB.md:12 (capture-only) | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | `50443f5` "Entry B narrowed per CritEntryB (fetch-only isolated; pull/merge/rebase rows disclosed as confounded)" — the falsified four-command claim is withdrawn and disclosed |
| RevAssimRules.md:4 (capture-only) | resolved@50443f5701d0b301f515202c6706f591b2cdf856 | Gate sections at `33e6807`; the two receipts it named absent now exist (`census/round-26/records/c2-gate.tsv`, `c2-k4-after.tsv`, added `9a6e0f1`); c2-gate receipt at 50443f5 is green |
| RevC3Design.md:4 | resolved@c5949013f89fe0b8289bdb7050ab64a47e08c911 | `c594901` "R4 per frozen contract … adopt wave 12-case fixture (cases=12 pass=12 control=FALSE-GREEN-REJECTED)" |
| LabReceiptVerify.md:5, RevC2Scope.md:9, SentBounds.md:3 | open | re-checked this run at lane tip: `census/round-26/records/{c1,c2,c3}-before.tsv` still exit 2 under `souji-receipt-run.py verify` (RECEIPT-COUNTS-ABSENT); `c2-k4-base.tsv` exits 0 |
| ExecVerifyLoop.md:5 (capture-only) | open | the committed `.ufo/waves/round-26/w1/verify-loop.sh` blob at base still fails `bash -n` (rc 2, "unexpected EOF … matching `\"`"); the seat's fix never landed |
| all other bullets | open | no commit found that fixes or answers the reported failure; the paragraph's own caveats still describe the state at base |

## Limits

- The base gate is blind to the 29 capture-only reports by construction; their
  8 paragraphs are proven carried only by the imported-function sweep above,
  not by a gate SUMMARY line.
- Dispositions are classification, not re-verification of each seat's work;
  `open` means "no commit found that fixes or answers it", not "still true".
- One sentence in two paragraphs (RevC2Scope, SentBounds) states the receipt
  clause as structural; the re-check above is the observable behind `open`.
- Scratch was removed after this file was written.
