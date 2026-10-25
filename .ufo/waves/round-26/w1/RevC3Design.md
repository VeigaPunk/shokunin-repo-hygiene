# RevC3Design — attack on C3 tool design

## Status
STATUS: FAIL — the C3 checker's R2/R4 design is not sound against adversarial preregs; the swept adversarial input (`claims=1 flags=0`, rc 0) hides every defect C3 exists to catch, and the landed fixture deviates from the frozen 12-case set,including the r25-C2-replica discriminator).

## Evidence
All runs at lane HEAD `0833de9591a7db81cdfa4efda2cdad2e75606f58` (tools/souji-axis-check.py + tests/fixtures/r26-axis-check.py landed in that commit), real SCORECARD.md; scratch `/var/tmp/souji-r26-RevC3Design/`.

- Self-host on frozen r26 prereg: `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`, rc 0.
- Fixture: 11/11 PASS (control arm separate via `--stub`), prints `cases=11 pass=11` — not the frozen `cases=12 pass=12 control=FALSE-GREEN-REJECTED`.
- Real SCORECARD parse probe: `{'coverage': 8, 'calibration': 7, 'operability': 8}`; lowest = calibration. R3 parse correct on the real file.
- Adversarial runs (all rc/flag output captured):
  - ADV1 (universals in claim prose after END): `claims=2 flags=0`, rc 0.
  - ADV2 (surface-class: measurement on operability): only unrelated C3 instrument-on-coverage flagged; the measurement-on-operability claim passes (rc 1 solely for the C3 line).
  - ADV3 (fixture-expansion + receipt-binding double surface-class on operability): `claims=2 flags=0`, rc 0.
  - ADV4 (decoy first machine block): `claims=1 flags=0`, rc 0 — real CLAIM C2 never parsed.
  - ADV5 (enumerate with quoted `'^(all|every|none|no)[a-z]'`): FLAGGED (false positive inside quotes).
  - ADV5b (enumerate with `forall`/`nohup`): `claims=2 flags=0`, rc 0 (embedded universals bypass).
  - ADV6 (unknown surface-class `garbage-typo` on operability): `claims=2 flags=0`, rc 0.
  - ADV7 (three-way score tie, 7/7/7): claims on any axis satisfy R3, `claims=2 flags=0`, rc 0.
  - ADV8 (combined worst input): `claims=1 flags=0`, rc 0.

## Findings

1. **[CRITICAL] R4 is inverted vs its frozen spec** (tools/souji-axis-check.py:116-123). Frozen spec: "a claim text containing a whole-word all/every/complete/none/no without a same-claim `enumerate:` line naming its counting command is flagged". Implementation flags only when the `enumerate:` VALUE contains a whole-word universal; the claim text is never scanned, and prose outside the MACHINE BLOCK is invisible (parse_prereg regex `:56). ADV1/ADV8: `ALL`/`EVERY`/`NO` in claim prose → no flag. The universal-clause scan as designed does not exist.

2. **[CRITICAL] R2 neutral/unknown classes are an unconstrained hole** (lines 41, 110-114). `receipt-binding`/`measurement` are never checked against the axis; any claim can declare `axis: operability` + `surface-class: measurement` (ADV2) and pass. Worse, ANY unrecognized surface class passes (ADV6 `garbage-typo`): only the five enumerated classes are constrained — the entire remaining class space is the hole, and the label is claimant-declared with no verification (the tool cannot know whether a claim genuinely touches a runnable command's behavior). This is the exact C2-misattribution shape made bypassable.

3. **[CRITICAL] `last-wins` overwrite masks a mismatch** (line 74 `claims[cur][kv.group(1)] = kv.group(2)`). Repeated `surface-class:` lines overwrite; ADV3 puts `fixture-expansion` (would flag on operability) then `receipt-binding` → parser sees only the neutral → rc 0. The frozen r25-C2 misattribution shape passes if a neutral class line follows. Same mechanism on repeated `axis:`/`enumerate:`.

4. **[CRITICAL] Decoy first-block shadowing** (line 56 `re.search` first-match-wins). A benign minimal MACHINE BLOCK before the real one makes the tool parse only the decoy; all real claims are invisible (ADV4, ADV8). The checker validates a decoy, not the prereg.

5. **[HIGH] Frozen fixture case set not delivered** (frozen prereg case list (1)-(12) vs tests/fixtures/r26-axis-check.py CASES). Landed fixture: 11 cases, prints `cases=11 pass=11` with control separate; frozen target `cases=12 pass=12 control=FALSE-GREEN-REJECTED`. Missing: the r25-C2-replica discriminator (frozen case 1 — the round's stated purpose), bookkeeping-on-coverage (5), instrument-on-calibration (6); impl case 3 substitutes fixture-expansion-on-calibration; impl case 8 contradicts frozen case 9 ("universal clause WITH enumerate passes"). c3-after.tsv records only the self-host run (`axis_check_tool=present claims=3 flags=0 axis_check_exit=0`), no fixture line; K2 as frozen cannot be satisfied by the landed artifact (commit message itself says "11-case fixture").

6. **[MEDIUM] Word-boundary scan is syntactic noise** (line 121). `\ball\b` misses embedded universals (`forall`, `nohup` — ADV5b rc 0) yet fires inside quoted strings (ADV5 false positive). The scan neither catches "no"/"all" hidden in command words nor avoids punishing harmless uses.

7. **[MEDIUM] R3 tie semantics** (line 126 `min`). With equal lowest scores, the first row in file order wins and a claim on any tied axis satisfies R3 (ADV7 rc 0). Current real file has a unique lowest (calibration 7), so R3 is correct today — verified parse.

8. **[LOW] Axes-section parse fragility** (line 89 `(?=^## )`). The section spans `###` sub-sections; measurement rows don't match `^\|\s*(\w+)\s*\|\s*(\d+)\s*\|` today, but a future numeric second cell in the measurements section would silently overwrite axis scores (verified: a scorecard ending without a trailing `##` section → rc 2 refusal).

## Attack log

Attack on C3 (instrument-acquisition, operability): the surface-class→axis table DOES encode the r25 lesson correctly on paper — round-25-verifier-spotcheck.md:34/71 establishes C2's changed surface was four fixture edge classes with production tool untouched → coverage, not operability, and `fixture-expansion→coverage` is exactly that. But the mapping is not sound: the label is a self-report, the neutral list and unknown classes are open (finding 2), overwrite hides the mismatch (finding 3), and a decoy block hides the claims (finding 4).

**Strongest adversarial input (confirmed, rc 0, `claims=1 flags=0`)** — ADV8: MACHINE BLOCK starts with a clean minimal decoy (`CLAIM C1 / axis: calibration / surface-class: bookkeeping-file / enumerate: ...` — satisfies R1+R3), followed by the substantive claim declaring `axis: operability`, `surface-class: fixture-expansion`, then a trailing `surface-class: receipt-binding` (last-wins masks R2), with universal overreach (`**ALL** ... MUST ... no exception`) in prose after the decoy's END (invisible to R4). The tool reports pass; every defect C3 exists to catch is hidden. This SHOULD flag and does not.

Residual risk: none beyond the above — the checker's four rules are all bypassable by construction as implemented; the fixture's missing discriminator means the bypasses are not even regression-tested.

Verification gaps: I did not (and cannot, read-only) modify the tool or fixture; no dynamic analysis of the scorecard beyond the cases above; the K2 "12/12" score was never achievable against the landed 11-case artifact, so the claim's own after-literal is unchecked by its own instrument.

Tooling record: no tools installed or upgraded this run (none needed).
