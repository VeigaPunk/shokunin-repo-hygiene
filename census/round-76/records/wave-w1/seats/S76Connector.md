# S76Connector — separation + sibling overlap (round 76)
## 1. Causal separation — SEPARABLE
Commands (lane root; scratch /fast/scratch/hyaku/souji-r76/S76Connector, deleted at exit):
  git diff --name-status e827d2bf^..e827d2bf (same for 2c7c1ce6^..2c7c1ce6)
  strace -f -qq -e trace=openat,openat2 python3 -B census/round-76/c1-evade-counter.py --gate-dir <W-copy> --work <scratch>/c1
  strace ... python3 -B census/round-76/c2-binding-counter.py --tally census/round-76/c2-kill-tally.py
Observed: W = M .gitignore, M tools/souji-pre-report-gate.sh only; I = A census/round-76/c2-kill-tally.py only (100755).
  C1 trace: 0 opens of round-76/c2* (lane opens = round-7{4,5,6} c1 chain); C2 trace: 0 opens of souji-pre-report-gate|souji-receipt-write (lane opens = round-7{5,6}/c2-* only).
  Binds: records/c1-after.txt:8-17 (counter, populations, r75 evade counter, gate, writer) — no C2 path;
  records/c2-after.txt:8-13 (binding counter, population, tally) — no gate path; c1-K-*/c2-K-* same shape.
  Provenance-only: c2-after rev=e827d2bf per rec.sh:20 (rev=master at write); tally expectations derive from
  census/round-75/c1-counter.py:38 (a C1 counter, untouched by W/I); A bundles both receipts. No byte read.
## 2. Frozen numbers re-derived — all match, none falsified
  C1 W gate 18587bd2… rows=30 mismatches=0 EXIT=0 | K-a base ef3b04e4… mismatches=4 [f7 f9 f10 f14 clean=PASS] EXIT=1
  K-b 36f06903… mismatches=4 EXIT=1 | K-c 43ebc213… mismatches=1 EXIT=1
  C2 cases=10 mismatches=0 EXIT=0, h-honest killed=6 | --tally census/round-75/c2-kill-counter.py mismatches=5 EXIT=1
  | --tally controls/variants/tally-K-b-reject-all.py mismatches=2 EXIT=1 | prereg sha256 8/8 = committed bytes.
## 3. Lane tools vs f7-shape (untracked self-ignoring dir)
| file:line | basis | f7 changes verdict? |
| tools/souji-pre-report-gate.sh:100-144 | ls-files -o -i + check-ignore -v, tracked source | NO (f7/f9/f10/f14 FAIL; base K-a PASS) |
| tools/souji-census.sh:41,1249 (+impl-3x/4x) | status --porcelain counts | YES: under-count (26,376 ignored; live drift); no pass/fail |
| tools/souji-verify.sh:550,594; souji-vault-verify.sh:550,594 | status --porcelain | YES: f7-only dirt reads dirty→none |
| tools/souji-quarantine.sh:283,1037; souji-guard.r9-s18.sh:153 | status; --ignored=matching at target | NO (conservative) |
| census/round-7*/ | fixture machinery only | N/A (no lane-cleanliness decision) |
## 4. Siblings (read-only)
| lane:file:line | (a) clean-miss / (b) unbound tally | vulnerable |
| kama pre-report-gate.py:38 + round73-round-scope-cases.py:210 | (a) status scoped to .ufo/waves; ignored only there | (a) YES outside wave scope |
| kaidoku round-29/prefile-check.sh:22; round-42/prefile-gate.py:9,288 | (a) plain status; ignored residue = advisory warn | (a) YES; PARTIAL |
| mori mori-census.sh:2389 | (a) ls-files -mo --exclude-standard (row, not gate) | (a) YES (count) |
| chousa, kotodama, mado, tameshi, tsukuroi | (a) no status/check-ignore hit | N/A |
| kama round86-mutant-owners.py:2-8; tsukuroi mutation-kill-r83.py:97-148; tameshi tally-audit-v3.py:1-12 | (b) mutant derived+run, no receipts | NO |
| kaidoku round-35/c2-calibration-counter.py:68 | (b) "EXIT=0" in census, no instrument bind | YES (text only) |
Findings: MEDIUM — C1 domain-trial PASS rests on W's .gitignore hunk: 13,621 .jj paths are decided by `.jj/.gitignore`
  ("/*", untracked) without it, so the same gate blob would print RECEIPT-UNTRACKED-UNDECLARED-IGNORE. LOW — 26,376
  ignored paths ride tracked rules (f2 stated limit; 12,573 .ufo/waves, drifting). LOW — replay shadow: C1 importlib probes
  census/round-75/__pycache__/*.pyc (strace), untracked and declared by .gitignore:3; instrument_sha256 binds the .py
  only (both pycs absent now). Files: S76Connector.md; S76Connector/receipts/{c1-after,c1-K-a-base,c1-K-b,c1-K-c,
  c2-after,c2-K-do-nothing,c2-K-blanket}.out.
