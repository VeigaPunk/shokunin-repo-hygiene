# MutC1Surgery — mutation test of the C1 integration plan (souji r26 w1)

Seat: MutC1Surgery (read-only attack seat). Scratch: `/var/tmp/souji-r26-MutC1Surgery/` (removed after run).
Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; frozen prereg `89e0fce` + amendments 1–2 read first.
HEAD observed during run: `0c92c2e` (lane moving under me; all probes below pin named revs). No tool installs performed (none needed).

## Status

STATUS: PASS — all three assigned mutations built from base bytes, exact K1/K2 detectors run on pristine/mutated/restored copies, restoration byte-verified; verdicts below. Two mutants survive K1+K2 (coverage findings, not contract changes).

## Evidence

- Base bytes: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0eca7c8:SCORECARD.md` → 254 lines; sha256 `b42a24f019b2dfa5084a5399dd750302e6ce11bf019820a81db78ada05229310`. K1 hits at :172 and :217; K2 headings at 17 (R23), 175 (R24, fenced), 231 (R25).
- Detector (exact labeled-counter semantics, `LC_ALL=C`, run per scratch copy):
  - K1 `grep -cE '^(Insert the table below directly above|Optional same-landing correction)' F`
  - K2 `awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}' F`
- Reference plan execution: `git show a529c762:SCORECARD.md` → 233 lines, K1=0, K2 `17 44 78`. Amendment-2 span byte-diffs at a529c76: span1 (B1-16→1-16) ✓, span2 (B231-254→17-40) ✓, span3 (B175-207→44-76) ✓, span4 (B17-62→78-123) ✓, span6 bullets (B225-226→199-200) ✓, span7 (B138-169→202-233) ✓; span5 rows absent (repaired byte-equal at `07f83e6`, rows :155-156, span7→204-235 there, K2 still `17 44 78`).
- Pristine control run: K1=2, K2 `17 175 231` (order n25=231 > n24=175 > n23=17 → after-condition FAIL; red arm confirmed).
- Restoration: pristine bytes rewritten and re-detected after the mutant series — K1=2, K2 `17 175 231`, byte-identical to pristine (True).

## Findings

1. **Moving the r25 block is REQUIRED, not forbidden.** K2's after-condition "ordered Round 25 < Round 24 < Round 23 (newest first per the file's own contract)" (`.ufo/waves/round-26/preregistration.txt`, CLAIM C1 K2) is unsatisfiable with the r25 block left at base 231-254, because span4's R23 heading cannot leave the file head region. The pre-amendment-2 position-literal kill rule ("any byte change to the ... base lines 231-240") therefore contradicted the counter the same claim freezes; amendment 2 resolves it: "each protected region is a BYTE-CONTENT span, not a position" (`.ufo/waves/round-26/preregistration-amendment-2.txt`, Clarification). Moving with altered bytes stays forbidden (span byte-diff). M1 below kills this conclusively.
2. **The plan's extraction keeps the fenced heading.** Payload 1 is "Round 24 measurements block (base lines 175-207, 33 lines)" (`.ufo/waves/round-26/w1/c1-scaffold-extract.md`, Payload 1 header), and amendment 2 span 3 pins "the base lines 231-254 span" ordering with payload "base lines 175-207, verbatim from the fenced content" (`preregistration-amendment-2.txt`, items 2-3). Verified: landed :44 bytes == base :175 bytes. The fenced heading DOES match the awk pattern (base K2 = `17 175 231` includes 175), so dropping it is detectable (M3a) but merely rewording it is not (M3b).
3. **K1/K2 are blind to line-map staleness (coverage finding, M2).** The labeled instrument cannot see a span-5-class insertion that invalidates named-line references: identical `markers=0` / `17 44 78` before and after. The lane knows this: "The frozen C1 counters stayed green through the omission" (`.ufo/waves/round-26/w1/c1-append-note.md`, consequence 2) and the R26-C1b rule "Re-derive per cell; never carry this column across a commit that inserts lines above a named line" (same file, §1 code block). Enforcement lives in the amendment-2 span byte-diff + per-cell re-derivation, not in scoring.
4. The five bare `superseded by SCORECARD.md:<n>` lines (base 250-254) are protected verbatim inside span 2 and knowingly cite pre-cleanup coordinates (four +1 stale at the frozen base; literal/semantic split documented in `.ufo/waves/round-26/w1/c1-line-map.md`). Leaving them byte-verbatim is the contract-correct choice; no mutation proposed against them.
5. No defect found in the landed plan's K2-relevant geometry: a529c76 and 07f83e6 both print `17 44 78` with all amendment-2 spans byte-equal (span5 present at 07f83e6 only).

## Attack log

Pristine under test sha256 `b42a24f0…` (full above); detector outputs verbatim.

- **M1 — r25 block left at tail (position-literal misreading of the kill rule; attacks surface a).**
  Mutant: landed edit with span2 (landed 17-41) not relocated — appended at EOF instead. sha256 `aee5d8bd59ce39963f449197f9205ea449724a447412f10df3d5380e213ed12e`.
  Expected: K1 passes (0), K2 order breaks.
  Output: `markers=0`, `headings=19 53 209` (R24@19, R23@53, R25@209).
  Verdict: **KILLED by K2** (not three-in-order n25<n24<n23). K1 alone does not kill it. Proves finding 1.
- **M2 — line-map column carried stale across an above-named-line insertion (attacks surface b).**
  Mutant: landed a529c76 + span5 capability rows (base 213-214) inserted at :155-156 (the 07f83e6 geometry) while the map still claims bullets at :199/:200. sha256 `67998848d15f9c4e18100e9893eb79e7440f87cf0f280d8a04c8703845c72e33`.
  Expected: K1=0, K2 unchanged (survives scoring; falsified only by named-line re-derivation).
  Output: `markers=0`, `headings=17 44 78` — **SURVIVES K1+K2**. At the mutant tip :199 = `- **r25 — attempted, honest stop; …`, :200 = blank, real bullets at :201/:202 — the stale claim is false.
  Verdict: **SURVIVED** (coverage finding → finding 3). Counter contract untouched.
- **M3 — fenced heading handling (attacks surface c); two arms.**
  - M3a heading dropped from the payload (extract table-only). sha256 `8d28b7273fd12cc7732237d5a6636c605770fcd4d1d2fa6874a67d23191e10a0`. Output: `markers=0`, `headings=17 77` — only two matches. **KILLED by K2** ("exactly three headings" arm).
  - M3b heading kept but normalized to bare `### Round 24 measurements` (parenthetical trimmed). sha256 `483b6d0b3e7852182a85a2cec6eaa9d1ecabc2962a2690aa83384352ef926c5e`. Output: `markers=0`, `headings=17 44 78`. **SURVIVES K1+K2** (awk pattern is prefix-anchored only); killed solely by the amendment-2 span-3 byte-diff. Coverage finding: K2 pins heading count/order/line, not heading bytes.

Verdict on the plan: the frozen K2 counter kills both structural misexecutions (M1, M3a); its blind spots (M2, M3b) are exactly the ones amendment 2's span byte-diff and the R26-C1b re-derivation rule were added to cover — both mitigations are present in the landed artifacts. No amendment needed; no contract change proposed.

Restoration evidence: post-series rewrite of the under-test file == pristine bytes (True); pristine sha256 `b42a24f019b2dfa5084a5399dd750302e6ce11bf019820a81db78ada05229310` before and after. Lane repo untouched except this report file.
