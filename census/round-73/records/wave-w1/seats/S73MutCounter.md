# S73MutCounter — r73 counter forgery-witness mutation probe (w1, leaf)

VERDICT: the r73 C2 claims reproduce on pristine bytes; 17 single-edit mutants → 12 killed, 5 survived (3 MEDIUM + 2 LOW findings; one survivor provably equivalent).

Baseline (pristine copy sha256 3809ee7d…fed == lane census/round-73/c1-counter.py, never edited):
- selftest `SELFTEST cases=52 pass=52 fail=0 EXIT=0`; main arm `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=3 new_honest=21 class_mismatches=3 new_echo=0 errors=0 regress=PASS` `EXIT=1` (== controls/c1-K-a-do-nothing.txt); D1 arm `SUMMARY … base_unwitnessed=1 …` `EXIT=1`, `CASE FWr … base_witness=no` (== records/c2-after-D1.txt).
Commands (cwd lane root, S=/fast/scratch/hyaku/souji-r73/S73MutCounter): `python3 -B $S/<m>.py --selftest --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1… --work $S/st/<t>`; main arm `python3 -B $S/<m>.py --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1… --rev a789486d… --tool tools/souji-receipt-write.py --work $S/work/<t>-main`; D1 arm `python3 -B census/round-73/apply-edit.py --set census/round-73/c2-defang.json --id D1 --src $S/<m>.py --out $S/d1/<t>-D1.py` then the main arm over that file. 17 selftests, 10 main arms, 7 D1 arms; raw outputs in S73MutCounter/evidence.txt.

| id | edit | selftest | main unw/for | D1 | verdict |
|---|---|---|---|---|---|
| M01 | tree_divergence→[] | 48/52 | – | – | KILLED-ST |
| M02 | always non-empty | 51/52 | – | – | KILLED-ST |
| M03 | untracked ignored | 51/52 | – | – | KILLED-ST |
| M04 | exec bit ignored | 51/52 | – | – | KILLED-ST |
| M05 | bytes ignored | 51/52 | – | – | KILLED-ST |
| M06 | witness=pre only | 52/52 | 5/15 | – | KILLED-MAIN |
| M07 | witness=post only | 52/52 | 1/15 | – | KILLED-MAIN |
| M08 | failed read ⇒ witnessed | 52/52 | 0/15 | unw=1, FWr no | SURVIVED |
| M09 | claim drops base_unwitnessed | 51/52 | – | – | KILLED-ST |
| M10 | unwitnessed on base-refused rows | 52/52 | 11/15 | – | KILLED-MAIN |
| M11 | classifier errors ignore witness | 51/52 | – | – | KILLED-ST |
| M12 | classifier forgeries ignore witness | 52/52 | 0/15 | unw=1, FWr no | SURVIVED (equivalent) |
| M13 | .git exclusion removed | 47/52 | – | – | KILLED-ST |
| M14 | symlink target ignored | 52/52 | 0/15 | unw=1, FWr no | SURVIVED |
| M15 | gitlink skip removed | 52/52 | 0/15 | unw=1, FWr no | SURVIVED |
| M16 | summary hardcodes unw=0 | 52/52 | 0/15 | unw=0 | KILLED-D1 |
| M17 | new witness=pre only | 52/52 | 0/15 (new_unw=2) | unw=1, FWr no | SURVIVED |

Findings — HIGH: none. MEDIUM F1 (M08): "a failed witness read is never a witness" (c1-counter.py:1414) is untested; the fail-open edit passes all three detectors, so a base-accepted refuse row whose witness read fails would be credited witnessed.
MEDIUM F2 (M17): `new_unwitnessed` is printed but no predicate reads it (claim_upheld:1477-1483 gates base only); de-witnessing the new slot (FX1/FX3 new_unwitnessed 0→2) passes selftest+main+D1, yet classify_outcome:1497-1512 binds battery forgery kills on that same n_wit.
MEDIUM F3 (M14): the declared witness kind "different symlink target" (preregistration C2) has no selftest case and no matrix row whose witnessing depends on it; probe: same-content retarget → pristine `[('tools/link','target')]`, mutant `[]`.
LOW F4 (M15): the gitlink skip is untested (G1/LG1 are base=refuse); also lstat precedes the skip (c1-counter.py:1093-1099), so a missing/uninitialized gitlink path reports "missing" even on pristine — a false-positive witness direction.
LOW F5 (M12): provably equivalent (48/48 synthetic row fates identical; the errors term preempts), no defect — only shows classify_outcome's forgeries term cannot be pinned in isolation (the selftest pins outcome_counts instead).
Killed-mutant evidence: M01 fails 4 section-10 checks (mode/untracked/missing/bytes), M02/M03/M04/M05/M13 the named witness checks (M13 flags every .git file as untracked), M09/M11 their claim/classifier checks; M06/M07/M10 the main arm (unw 5/1/11 — AS2 FM2 FWi FX1 FX3 / FWr / 11 rows); M16 the D1 arm (prints unw=0).

Restoration: lane census/round-73/c1-counter.py sha256 3809ee7d…fed before and after; `git status --porcelain` over counter/matrix/writer empty; lane HEAD 312e8f29…e64e unchanged; all mutants and copies lived only under /fast/scratch/hyaku/souji-r73/S73MutCounter (deleted after the evidence copy).

Files written: .ufo/waves/round-73/w1/S73MutCounter.md, .ufo/waves/round-73/w1/S73MutCounter/{mutants.tsv,evidence.txt,arm-pristine.txt,d1-pristine.txt}.
