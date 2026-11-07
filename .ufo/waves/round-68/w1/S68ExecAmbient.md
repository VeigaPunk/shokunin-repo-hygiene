# S68ExecAmbient — C2 after-arm (ambient-environment operability)

Frozen instrument verification (lane dir /home/vgpnk/Projects/shokunin/souji-shokunin):
`sha256sum census/round-68/c1-counter.py` = ab3ac5c78a623c145e768ffb0c233e9f65a892a78431de44790187da3fdb37f0 (matches preregistration) — PASS
`sha256sum census/round-68/c1-matrix.tsv` = bb56e69a1c6cff948e4b706756305324654745a9605fd21c309f4ac2a792b2c7 (matches) — PASS
Neither differs; proceeded.

## Commands run

Clean run:
`python3 -B census/round-68/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix census/round-68/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev f70da577eb1e1624cc63ab8fd0468565927d9b6a --tool tools/souji-receipt-write.py --work <scratch/clean-XXXXXX> --receipt .ufo/waves/round-68/w1/S68ExecAmbient/clean-receipt.txt > clean.txt`

Ambient run (same, prefixed):
`env GIT_COMMON_DIR=/nonexistent-r68-probe GIT_NAMESPACE=r68probe GIT_CEILING_DIRECTORIES=/nonexistent-r68-probe python3 -B … --work <scratch/ambient-XXXXXX> --receipt …/ambient-receipt.txt > ambient.txt`

Flips:
`diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' clean.txt) <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' ambient.txt) | grep -c '^[<>]'` → 0

Before-arm check (read-only):
`diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' census/round-68/controls/ambient/r67-clean.txt) <(grep … r67-ambient.txt) | grep -c '^[<>]'` → 35

Do-nothing control: `grep EXIT= census/round-68/controls/c2-do-nothing-ambient.txt` → EXIT=1 (last line).

## Verdicts

- C2 VERIFIED: flips after = 0 (predicate: must be 0).
- Both runs EXIT=0, both SUMMARY = `matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS` (the C1 candidate SUMMARY).
- Before arm flips = 35 as committed in census/round-68/controls/ambient/ (≥1, claim not already met).
- Committed do-nothing control c2-do-nothing-ambient.txt still EXIT=1 (still refuses under ambient) — as frozen.
- No counter/matrix/mutant bytes altered; no commits made.

## Files written (seat dir .ufo/waves/round-68/w1/S68ExecAmbient/)

- clean.txt (95 lines, stdout of clean run)
- ambient.txt (95 lines, stdout of ambient run)
- clean-receipt.txt (98 lines)
- ambient-receipt.txt (98 lines)

Scratch dir /fast/scratch/hyaku/souji-r68/S68ExecAmbient removed before yielding. No installs performed.

No HIGH/MEDIUM/LOW findings.
