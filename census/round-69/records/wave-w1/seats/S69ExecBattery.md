# S69ExecBattery — C1 battery falsification (independent re-derivation)

Seat dir: .ufo/waves/round-69/w1/S69ExecBattery/ ; scratch: /fast/scratch/hyaku/souji-r69/S69ExecBattery/
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin

## 1. SHA256SUMS verification
Command: `cd /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-69/battery && sha256sum -c SHA256SUMS`
Result: all 28 members OK (D01,D02,D03,D04,D05,D06,D07,D08,D10,D18,D19,D21,D29,D30,K1-K8,M-CD-CALL,M-CD-EMPTY,M-CD-NCABS,M-CD-NCRAW,M-CD-ROOTREL,M-CD-SCRUB), EXIT=0. Directory holds 28 .py members + GEN.txt + SHA256SUMS = 30 files; SHA256SUMS lists 28 lines. Expected 28 members: CONFIRMED.

## 2. Battery run (own, independent; run before reading L1 receipt)
Command (from lane root, timeout 1800, 428s wall):
`python3 -B census/round-69/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work /fast/scratch/hyaku/souji-r69/S69ExecBattery/battery --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery`
Observed: EXIT=0, stderr empty. 26 MUTANT lines, 1222 CASE lines (26 runs × 47 rows), 364 `base=accept`.
MUTANT/BATTERY/EXIT lines (verbatim):
- BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0
- EXIT=0
- Outcome counts by grep: forgery=18, label-only=5, over-refusal=2, echo-violation=1, survived=0, error=0.
- Per-mutant outcome==expected for all 26 (forgery: K2 K3 K4 K5 K6 K7 K8 M-CD-CALL M-CD-EMPTY M-CD-SCRUB D01 D05 D06 D07 D08 D10 D19 D21; label-only: K1 M-CD-ROOTREL D02 D03 D04; over-refusal: M-CD-NCABS M-CD-NCRAW; echo-violation: D30).
- D18 and D29 are NOT in the 26-mutant manifest (they are named limits; their survived receipts live in controls/d18-limit-battery.txt and controls/d29-limit-battery.txt). survived=0 is therefore consistent with the frozen predicate, not a contradiction.
Evidence: preregistration.txt C1 predicate (BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0 EXIT=0); battery-manifest.tsv 26 mutants + header.

## 3. Diff against L1 after-receipt (read only after own run)
Command: `diff <(grep -E '^(MUTANT|BATTERY|EXIT=)' <own-stdout>) <(grep -E '^(MUTANT|BATTERY|EXIT=)' census/round-69/records/c1-after-battery.txt)`
Result: DIFF-IDENTICAL (no differing lines). L1 receipt BATTERY and EXIT match mine byte-for-byte, including per-mutant forgeries/echo/honest/label/errors/regress fields.

## 4. Do-nothing control (base writer bytes)
Commands: `git show 3639087917eaeb28719d7603110a6ec22782100e:tools/souji-receipt-write.py > <scratch>/base-writer.py` (1478 lines); then
`python3 -B census/round-69/c1-counter.py --root ... --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work <scratch>/donothing --new-tool <scratch>/base-writer.py`
Observed (verbatim): `SUMMARY matrix=47 base_forgeries=3 base_honest=11 new_forgeries=3 new_honest=11 class_mismatches=4 new_echo=0 errors=0 regress=PASS`, `EXIT=1`, REGRESS base=PASS new=PASS.
Diff vs census/round-69/controls/c1-do-nothing.txt over ^(CASE|SUMMARY|REGRESS|EXIT=): DONOTHING-IDENTICAL.
Matches preregistration C1 do-nothing predicate (EXIT=1, new_forgeries=3 W1/W2/W4).

## Verdict
All frozen numbers reproduced exactly from committed bytes. No mismatch. No HIGH/MEDIUM/LOW findings in this seat's scope.

## Files written
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-69/w1/S69ExecBattery.md (this report; Report path: .ufo/waves/round-69/w1/S69ExecBattery.md)
- Scratch (not lane files): /fast/scratch/hyaku/souji-r69/S69ExecBattery/{battery-stdout.txt,battery-stderr.txt,donothing-stdout.txt,donothing-stderr.txt,base-writer.py}
Scratch retained for L1 inspection; not deleted.
