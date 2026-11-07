# S77CriticClaims — r77 falsification (claims attacked, not their owners)

All numbers re-derived on this host (git 2.56.0); S=/fast/scratch/hyaku/souji-r77/S77CriticClaims (removed before yield); deciding receipts copied to .ufo/waves/round-77/w1/S77CriticClaims/.

## Verdicts
1. C1 n8 policy — QUALIFIED. Base row `n8-fifo-gitignore-declared-dir ... clean=PASS rc=0 secs=0.1`; `SUMMARY rows=16 mismatches=9 errors=0 hangs=8`. The frozen 9 = 8 HANG rows + n8 (preregistration.txt:29-30,44-47); on the 8 hang rows alone the claim holds (8→0). "9" overstates defects by one; the split is disclosed.
2. C1 cheaper fix / class fairness — QUALIFIED (measurement gap). Base gate + only `timeout -k 5 300` on check 4's status (sha e944865c) gives `n1 clean=HANG secs=30.0`: a fix that ends the infinite block is scored zero, because the 30 s row bound (prereg:29) is tighter than the gate's own 300 s backstop (gate:86,95). The class requirement (prereg:23) is the only discriminator; fair as diagnostics, but no row separates "prevents hang" from "names the class".
3. C1 o1-o3 — QUALIFIED (decoration for this claim). Base and W both pass o1-o3 and p1-p4; only 9 of 16 rows discriminate; the 7 invariants are anti-mutant guards (K-b/K-c/K-d), not evidence of the change.
4. C2 axis — QUALIFIED. Fits SCORECARD.md:14 ("one instrument, both ends"), but the authoritative pointer check is untouched: at A it still prints `missing=31`; the round's unique product is K's 2 artifacts (4 rows).
5. C2 bookkeeping — HOLDS as criticism. 31/35 rows resolve with no r77 byte (10 MOVED + 8 FLEET + 6 TOKEN + 3 ABSENT + 1 QUARANTINED + 3 LOCAL-POLICY). A 30-line mechanical prefix/digest ledger gives 31/35 at Base and 35/35 at A in 0.6 s; no control measures that 31/35 do-nothing ceiling (K-c is a 4-line ledger).
6. Sourced — C1 rests on S321 (open-then-fstat, srcs:1164-1169; SOURCES.md:280 digest matches); S321:1779 uses PATTERN_NOFOLLOW for per-dir .gitignore. Attributes half rests on S064 (SOURCES.md:99), not captured this round. C2 does NOT rest on S322: the counter verifies with git cat-file; S322 documents only how K was made.

## Commands (from the lane; S/D-<rev> = gate+writer from `git show <rev>:tools/...`)
- python3 -B census/round-77/c1-nonreg-counter.py --gate-dir S/D-base --work S/wk-base; same with --gate-dir S/D-W --work S/wk-W
- python3 -B census/round-76/c1-evade-counter.py --gate-dir S/D-W --work S/wk-r76; python3 -B tests/fixtures/r36-report-gate.py --work S/r36w --gate S/D-W/souji-pre-report-gate.sh; bash tests/fixtures/r27-pre-report-gate.sh
- python3 -B census/round-77/c2-pointer-counter.py --root <lane> --rev d4f5156|ef04ca6 --fleet-root /home/vgpnk/Projects/shokunin [--ledger ...]
- python3 -B tools/souji-pointer-check.py --root . --rev d4f5156|ef04ca6 SCORECARD.md SKILL.md SHONEN.md corpus/QUALITY.md corpus/README.md PROVINCE.md

## Observed
- C1 Base 9/8 (241 s); W 0/0; r76 30/30; r36 cases=21 pass=21; r27 cases=4 pass=4; K-b 7; K-c 11/8; K-d 7/4 — all four controls red, reproduced.
- W gate with both 300 s `timeout` wrappers stripped (sha c76db89c) still scores 16/0/0.
- C2 Base no-ledger 0/35 EXIT=1; A+ledger 35/35 EXIT=0 (receipts are at L 8bf42fc; re-ran at A, identical); pointer check 35→31; K-b 4/0/31, K-c 0/31/4, K-d 0/31/4, K-e 0/32/3.
- Mechanical ledger: Base resolved=31 unresolved=4; A resolved=35 refused=0. Population == the pointer check's 35 MISSING lines exactly (empty set diff).

## Findings
- MEDIUM unmet frozen predicate: prereg:21 says "a symlink counts by its target"; gate:82-83 `find ... ! -type f` does not follow. Fixtures: tracked sub/.gitignore→regular and sub/.gitattributes→regular each give Base clean=PASS 0.1 s, W clean=FAIL RECEIPT-NONREGULAR-SOURCE. No population row. Fix: follow links in the find branch (find -L or -f on the link).
- MEDIUM dead clause: the 300 s backstop (gate:95,97) has no discriminating row (strip → 16/0/0). SKILL.md:119 (S064/S062) says a pre-scan is not a bound, so the clause covering the race is the untested one.
- MEDIUM thin round: C2's do-nothing ceiling is 31/35 and a 0.6 s mechanical ledger meets the frozen after target 35/35; only 4 rows / 2 artifacts are attributable to r77.
- LOW: n8 policy row counted inside "mismatches 9" (defect count 8).
- LOW: "verified bytes" covers 17 rows (MOVED 10, CAPTURED 4, LOCAL-POLICY 3 disk bytes); 8 FLEET and 1 QUARANTINED verify existence, 3 ABSENT absence, 6 TOKEN a parse-artefact target.
- LOW: 35 findings = 25 distinct pointer strings (P03/P24, P12/P17/P20/P32, P13/P33, P19/P27, P29/P34, P30/P35, P09/P10, P11/P18 repeat).
- LOW: core.excludesFile=/dev/null refused (Base PASS / W FAIL) although the gate itself runs git with `-c core.excludesFile=/dev/null` (gate:162).
- LOW: the XDG-default branch the rule names has no row (fixtures unset HOME/XDG); probed working (FIFO at $XDG_CONFIG_HOME/git/ignore: Base TIMEOUT 10 s, W FAIL 0.0 s).

## Files written
.ufo/waves/round-77/w1/S77CriticClaims.md; .ufo/waves/round-77/w1/S77CriticClaims/{c1-base,c1-W,c2-base,c2-after,pc-base,pc-after}.txt; .../ledger-mech-base.tsv. No lane tracked file touched; no git/jj mutation.
