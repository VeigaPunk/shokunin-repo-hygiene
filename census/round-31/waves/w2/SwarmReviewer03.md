# SwarmReviewer03 — C1 audit, supersession rows L13-L20

## Status

STATUS: PASS — all eight audited rows (L13-L20) re-derived HONEST at the C1 landing commit 24f343c8ffc820c0f89b4252cbdc94ab9a673aab and unchanged at lane tip 2c16d018e40db7c23420a2c3bb546b52957bcc25; no falsification found; the L1's C1 counter reading holds for this slice (8/8 record MATCH, mismatches=0).

## Evidence

Commands (scratch clone /fast/scratch/hyaku/souji-r31/w2-c1-L13-L20/c, origin removed, removed after delivery):

1. Rows read: `grep -n '^| L' SCORECARD.md` → L13-L20 at SCORECARD.md:379-386, all `record:` rows; no `run:` rows in range (assignment step 3 vacuous).
2. Base cells: `git show 9f17a1ef...:SCORECARD.md | sed -n '160,166p'` → line 163 bounded repository-content census (r18) "`census/round-18/c1-matrix-4800fd7.json` (12/9 failed →12/0); census selftest 69/0"; line 164 evidence-pointer gate (r18) "selftest 61/0, pointer fixture 11/0, r16 fixture 15/0"; line 165 process-residue observations "r21 synthetic27/27 (old emissions6/27, leaks19→0), `census/round-21/reason-after.txt`".
3. Records at 24f343c8 opened byte-exactly: census/round-18/final-verification-4800fd7.json (226 lines), census/round-21/reason-after.txt, census/round-21/reason-oracle-before.txt. Stability: `git diff --stat 9f17a1ef 24f343c8 -- <three records>` and `24f343c8..2c16d018` both empty.
4. Occurrence locations (file:line at 24f343c8), each verified same capability + same run + same count, not merely same digits:
   - L13 `12/9` → fv.json:25 matrix-final stdout r17-base segment `selftest=49/0fail\tr18-bounded=12/9fail\tr17-hygiene=29/0fail`; corroborated by the run's own output record c1-matrix-4800fd7.json r17-base arm r18-bounded total=12 failed=9 (matrix.json:2446/2497/2509). The matrix-final command (fv.json:14-21) carries `--output .../census/round-18/c1-matrix-4800fd7.json` — the cell's cited record — so the reason's "command wrote the cited" is true.
   - L14 `12/0` → fv.json:25 changed segment `selftest=69/0fail\tr18-bounded=12/0fail\tr17-hygiene=29/0fail`; changed arm = measured commit (matrix.json changed_rev/git_head = 4800fd79488e...); matrix changed arm failed=0/total=12 (544/595/607).
   - L15 `69/0` → fv.json:25 changed segment `changed\t21c19ff620ad\tbash-n=0\tsc=0\tselftest=69/0fail`; 21c19ff620ad = record's tools_sha256 prefix of tools/souji-census.sh; matrix changed arm selftest checks=69 failed=0 (611-613).
   - L16 `pass=61\tfail=0` → fv.json:38 gate-selftest check (`python3 tools/souji-landing-gate.py --selftest`) stdout ends `SELFTEST\tpass=61\tfail=0` — the record's own JSON-escaped notation, matching the row's two-byte `\t` literal.
   - L17 `total=11\tfailed=0` → fv.json:66 gate-r18-fixture check (`python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py`) stdout ends `SUMMARY\ttotal=11\tfailed=0` — the r18 pointer fixture.
   - L18 `total=15\tfailed=0` → fv.json:52 gate-r16-fixture check (`python3 tests/fixtures/r16-landing-gate.py --tool tools/souji-landing-gate.py`) stdout ends `SUMMARY\ttotal=15\tfailed=0`.
   - L19 `total=27\tpass=27` → reason-after.txt:29 `SUMMARY\ttotal=27\tpass=27\tfail=0\tleaks=0\tbase_leaks=19\tmax_reason_bytes=160`; line 1 COMMAND names tests/fixtures/r21-reason-canary.sh (the reason-canary receipt).
   - L20 `total=27\tpass=6` → reason-oracle-before.txt:49 `SUMMARY\ttotal=27\tpass=6\tfail=21\tleaks=19\tbase_leaks=19\tmax_reason_bytes=454`.
5. Reason-truth checks: c1-cells.tsv at 1d45496a — L13-L15 line 163 rounds {18}; L16-L18 line 164 rounds {16,18}; L19-L20 line 165 rounds {18,21}; all records inside their round sets, no waves/transcripts/sources component, no code suffix (A4(b)); integer multisets row↔base all equal ({12,9},{12,0},{69,0},{61,0},{11,0},{15,0},{27,27},{27,6}); no shared (record, literal) pair in range (A4(d)); SCORECARD base→tip diff has zero removed lines (cells at 163-165 untouched, only the appended supersession section).
6. Counter re-derivation (serial, `python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8... --base 9f17a1ef... --list-rev 1d45496a... --only L13,L14,L15,L16,L17,L18,L19,L20`): `SUMMARY items=8 bound_run=0 bound_record=8 unbound=0 mismatches=0 partial=1` — all eight `binding=record MATCH` (partial=1 is the diagnostic marker).

## Findings

1. No defect in L13-L20. Every row HONEST: the located occurrence is the measurement the cell states (same capability, same run, same count), every reason sentence true, records unchanged pre-round records of the row's own round. Axis calibration unaffected by this slice.
2. Observation (no defect, disclosed in A4's own "not addressed"): the counter's record rule is occurrence-blind. `12/9` occurs twice in fv.json:25 (r14-harm and r17-base segments — same capability, same run, coincidentally equal counts; c1-matrix-4800fd7.json r14-harm arm failed=9 at matrix.json:1863) and `12/0` occurs 4x (1x r18-bounded changed + 3x `r14-namespace=12/0fail`, a different capability with the same digits). The rows disambiguate correctly by naming the arm/check; the hand audit this seat performed is the check A4 said wave-2 reviewers would do, and it passes.
3. Observation (no defect): L20's "against the old tool" is not verifiable from the receipt bytes — reason-oracle-before.txt has no COMMAND line. It is attributed by the committed r21 lesson, corpus/lessons/round-21.md:9 "the same27-case oracle is6/27 baseline versus27/27 changed, leaks19→0", and corroborated internally: oracle-before leaks=19 equals reason-after's base_leaks=19, and the two receipts' 27 CASE names are byte-identical (`diff` empty). Honest on the pre-round record + lesson; noted as provenance nuance.

## Attack log

- Digit-collision attack (same digits, other capability/arm): tried the `12/0`↔`r14-namespace` and `12/9`↔r14-harm collisions against L13/L14 — both rows name the correct arm and capability; no WRONG-OCCURRENCE.
- Provenance attack on L20 ("old tool" not in receipt bytes): resolved via r21 lesson line 9 + internal leak-count/case-name identity; HONEST with nuance, not FALSE-REASON.
- Stability attack (record swapped after landing, cells edited): records byte-unchanged base→landing→tip; rows byte-unchanged landing→tip; cells untouched (no removed lines in SCORECARD diff). Held.
- Notation attack (row literal shape vs record bytes): L16-L18 two-byte `\t` literals match the JSON-escaped record bytes; L19-L20 real-tab literals match the plain-text receipts' tab-separated SUMMARY lines. Held.
- Counter re-derivation: 8/8 record MATCH at 24f343c8 — the L1's landed reading re-derived for this slice, not refuted.

## Deliveries

- .ufo/waves/round-31/w2/deliver-c1-audit-L13-L20.md (full per-row audit)
- .ufo/waves/round-31/w2/SwarmReviewer03.md (this report)

Scratch /fast/scratch/hyaku/souji-r31/w2-c1-L13-L20 removed after delivery. No lane mutation; read-only git only.
