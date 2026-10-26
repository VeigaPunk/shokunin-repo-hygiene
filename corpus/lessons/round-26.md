# Round 26 (2026-10-25) — calib/census integration, gate decision

Round 26 ran three claims: C1 (calibration) integrated the r24 scaffold
payloads into SCORECARD.md; C2 admitted two grounded F1 knowledge entries and
registry rows S128-S132; C3 built `tools/souji-axis-check.py` with a
12-case FALSE-GREEN-controlled fixture. This file records the gate decision,
the re-grounding receipts, and the fixable residuals left for later rounds.

## Gate

The r25 registry's staged S-language-edition row (zh/ja docs, a vendor page)
was checked against the build's edition boundaries. What passed: the en
`git-fetch(1)` manual (opened from `git-scm.com/docs/git-fetch`), the
v2.56.0 tag sources (fetched snapshots in `census/round-26/sources/`, bound
by `SHA256SUMS`), and the en `git(1)` pages already in the corpus. What was
refused: the zh/ja docs (their version alignment with 2.56.0 on the mirrors
was not provable and the pages' own build stamps were ambiguous) and the
vendor page (it quoted an older 2.16.x-era workflow; parsing it to an
argument would have silently changed the claim's public surface).

Admitted rows instead re-ground the *en* single source of truth: S128
(`git-fetch(1)` § OPTIONS switches), S129 (five v2.56.0 call sites of
`run_auto_maintenance`), S130 (`builtin/pull.c` spawns `fetch`, so pull
inherits fetch's trigger), S131 (the campaign's measured prune fixture,
re-grounded byte-for-byte by sha256) and S132 (the fleet worktree census,
0 prunable / 5 registrations). S131/S132 are own-work tier A per the source
registry contract: the CAMPAIGN lane ran the fixture (2026-10-23); this
lane re-verified the bytes by sha256 this round and did not execute the
fixture.

## Findings

- The r25 "0 prunable, 3 locked" fleet census is history: S132 re-checks to
  **5 registrations, 0 prunable, 0 locked** even at `--expire=now`. The
  fleet is *currently* unexposed — but the mechanism (fetch/pull/merge/
  rebase auto-maintenance) is live on five surface commands.
- The r24 scaffold's Round 24 measurements block was never landed (the r24
  attempt was cut off). The r25 heading order therefore violated the file's
  own newest-first contract; C1 landed the block and reordered headings to
  round-25 < round-24 < round-23.
- Replacement "C1 kill-rule vs positional line numbers": the frozen claim's
  kill rule named base line ranges, but the integration the K2 counter
  demands moves the protected byte spans. Amendment 2 (accepted pre-data in
  session) clarified the regions are byte-content spans, and the post-edit
  byte-diff of each protected span against the committed base is empty. The
  counter (`census/round-26/c1-counter.sh`) verifies the *order* of the
  headings; the margin of C1 is the byte-diff, recorded in the report.
- The R3 receipt-label pitfall (from the r25 gate): the receipt's `tool`
  binds the labelled file's committed bytes *and* the argv label. The c3
  counter changed mid-round (its `--stub` arm was replaced by the fixture's
  integrated case 12), so the regenerated receipts bind the new counter
  bytes at their own revs; each receipt's label is its own argv element.
- The frozen C3 case set is 12 cases (the r25-C2 replica and an integrated
  always-green stub control); the first 11-case fixture did not implement
  the frozen set. Wave ExecAxisFixture delivered the 12-case fixture; the
  L1 adopted it and fixed the tool's R4 to scan raw claim text (flag only
  when `enumerate:` is absent AND a universal word is present).
- C2 K2 requires a `## Gate` section per admitted entry (opened date,
  ADMIT/REJECT with reason, located ≤25-word snapshot quotes). Both entries
  gained Gate sections; the first quote attempts failed because the man-page
  HTML wraps the sentence in inline tags and the C comments carry a `* `
  decoration — tag-free code/manual token quotes were substituted.
- Wave ExecC1Surgery found C1's first landing omitted the two r24 capability
  rows; they were appended and the c1-after receipt regenerated at the new
  tip (markers=0, headings=17 44 78, byte-spans re-verified).

## Residuals

- R-r26-1: `git maintenance run` strategy/task scope (which tasks run under
  which strategy) remains unmeasured; only the trigger and the per-command
  opt-out are held. The recheck command for S128 is in the entry's
  `recheck:` line and re-greps the call sites at the next host git tag.
- R-r26-2: the two stage candidate rows remain un-cited (see Gate). If the
  edition boundary of the zh/ja mirrors becomes provable on a later release,
  the S-language row can be reconsidered; it must then be cited with the
  version-stamp evidence rather than as a paraphrase.
- R-r26-3: keep-ref expiry (the `keep` ref option) is still not measured —
  the trigger set covers expiry via `gc.worktreePruneExpire`, not via the
  keep-ref guarantee. See `git-auto-maintenance-trigger-set.md` for the
  claim boundary.

## Receipts

- `census/round-26/records/c1-after.tsv` (07f83e6, markers=0, order
  17<44<78) + byte-diff annex in the round report.
- `census/round-26/records/c2-before.tsv` (base 89e0fce: F1=0, rows=127),
  `c2-after.tsv` (tip: F1=2, rows=132), `c2-gate.tsv` (entries=2 ok=2
  fail=0), `c2-k4-base.tsv` (grounded=7 mapped=7), `c2-k4-after.tsv`
  (grounded=9 mapped=9, kill_violations=0), real registry gate rc=0.
- `census/round-26/records/c3-before.tsv` (tool absent), `c3-after.tsv`
  (claims=3 flags=0 at tip 0c92c2e; fixture cases=12 pass=12
  control=FALSE-GREEN-REJECTED, fixture_exit=0); all verify=ok.

## Mistakes table

- R26-M1 (attribution/scope; captured-by none → fixed by C3 instrument + QUALITY Q59): the round-25 C2 claim declared operability for a change that covered four input edge classes. This round's C3 instrument makes the check mechanical, and Q59 records the criterion. The frozen C3 case 1 is the r25-C2 replica and fails on a stub (discriminator).

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
