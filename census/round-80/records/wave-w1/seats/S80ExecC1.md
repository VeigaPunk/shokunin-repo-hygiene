# S80ExecC1 — C1 falsification (souji r80): VERDICT: C1 HOLDS on every frozen receipt; 2 LOW record-hygiene findings, 0 HIGH, 0 MEDIUM

Lane tip a4aa8880 (A); W1 bd263c3f. Tree clean at start. Harness sha 6f22b68a…, population 5cce4146…, r80 counter 90ed9031… (= tip = W1 blob), r79 counter f597909b… (= base blob). No tool installs. Scratch removed.

## Harness (frozen command, --lane lane, --fleet-root fleet)
- r80 counter, run A: `SUMMARY rows=18 mismatches=0 accepted=0 errors=0`, EXIT=0. Target met.
- r79 counter (K-a), run: `SUMMARY rows=18 mismatches=3 accepted=3 errors=0`, EXIT=1; accepted rows NF6b (`got=QUARANTINED`), NF8 (`got=TOKEN`), NF10 (`got=MOVED`). Matches controls/c1-K-a-r79-counter.txt ROW+SUMMARY lines byte-for-byte.
- Determinism: run B (r80) stdout IDENTICAL to run A; fixtures F0=6436db6a…, R1=f28736a9…, R2=afc4ceb7…, R3=bdea7114… printed identically both runs.
- records/c1-after.txt ROW+SUMMARY lines IDENTICAL to my run A.
- Refusal reasons (direct counter run on harness fixture): NF8 -> `range member is not a regular file: census/round-73/records/c2-after-D3.txt`; NF6b and NF10 refused (FORGE match=yes); ablations below flip each to accepted, so the refusal is caused by the named rule.

## Controls (replayed; each ROW/ITEM/SUMMARY block IDENTICAL to its receipt)
- K-b refuse-all harness: `SUMMARY rows=18 mismatches=0 accepted=0 errors=0` EXIT=0 (18/18, as frozen).
- K-b refuse-all r78 regression: `SUMMARY items=22 resolved=3 ... FORGE-SUMMARY forged=12 matched=12 accepted=0` EXIT=1 (3/22, as frozen; fails regression conjunct).
- K-c without-regular: `rows=18 mismatches=1 accepted=1` (NF8 got=TOKEN). EXIT=1.
- K-c without-capture-root: `rows=18 mismatches=1 accepted=1` (NF10 got=MOVED). EXIT=1.
- K-c without-whole: `rows=18 mismatches=1 accepted=1` (NF6b got=QUARANTINED). EXIT=1.
- Each ablation file differs from the candidate by exactly one rule (diffed: `if False and dots and not _regular`, `elif False:`, whole-path check replaced by substring `in`).
- Variant sha256 vs bind lines: K-b 192beb9b… OK; K-c-regular e54a0384… OK; K-c-capture-root 284b0cae… OK; K-c-whole 511d44a0… OK.

## Regressions at W1 (copy of bd263c3f blob) and at lane tip (a4aa8880), both at --rev e65538e7
- r78 (22 items, 12 forge): W1 `SUMMARY items=22 resolved=22 ... FORGE-SUMMARY forged=12 matched=12 accepted=0` EXIT=0; tip identical; byte-identical to records/c1-regress-r78.txt ITEM lines.
- r77 (35 items, 7 forge): W1 `SUMMARY items=35 resolved=35 ... FORGE-SUMMARY forged=7 matched=7 accepted=0` EXIT=0; tip identical; ITEM lines identical to records/c1-regress-r77.txt.
- r79 harness with candidate (W1 and tip): `SUMMARY rows=9 mismatches=0 accepted=0 errors=0` EXIT=0 both; ROW lines identical to records/c1-regress-r79-harness.txt.

## Step 4: ITEM diff, r79 counter vs r80 counter, same --rev e65538e7
- r78 population: ITEM lines and FORGE lines: NO DIFF (22 items, 12 forges, identical verdicts and classes).
- r77 population: ITEM lines and FORGE lines: NO DIFF (35 items, 7 forges). No verdict moved; no rule had to be judged.

## Findings
- LOW-1 (records metadata): records/c1-after.txt:2 and records/c1-regress-r{77,78}.txt:2 carry `rev=836dac3e…` (W2; rec.sh:21 stamps lane `master` HEAD at run time), not the base `f80f9368…` that the preregistration states for control receipts, and not the tested counter's commit W1 bd263c3f. Verdicts unaffected (counter bytes verified by sha 90ed9031…), but the rev line does not identify the counter tested.
- LOW-2 (population schema): census/round-80/c1-false-rows.tsv carries the 9 r79 rows with identical id/class/target/expect/source content, but inserts a `rev` column (BASE/F0/R2 labels); the preregistration says "unchanged". Content-equivalent; the r79 file (census/round-79/c2-false-rows.tsv) is not byte-identical.
- No HIGH/MEDIUM finding. No false refusal of legitimate rows (r77/r78 resolved 35/35, 22/22). Stated limits (NF6a, NF9) are not tested here.

## Commands run (cwd lane; SCRATCH=/fast/scratch/hyaku/souji-r80/S80ExecC1, removed)
- `python3 -B census/round-80/c1-false-row-harness.py --counter {census/round-80/c1-pointer-counter.py | census/round-79/c2-pointer-counter.py | controls/variants/c1-K-*.py} --lane <lane> --fleet-root <fleet> --work <scratch>/...`
- `python3 -B {census/round-80/c1-pointer-counter.py | W1 blob | controls/variants/c1-K-b-refuse-all.py | census/round-79/c2-pointer-counter.py} --root <lane> --rev e65538e7… --fleet-root <fleet> --population census/round-7{7,8}/c2-population.tsv --ledger … --forge …`
- `python3 -B census/round-79/c2-false-row-harness.py --counter <W1 or tip counter> …`
- `git show bd263c3f:census/round-80/{c1-pointer-counter.py,c1-false-row-harness.py,c1-false-rows.tsv} | sha256sum`; `git show a4aa8880:…` (same digests); `git diff --stat f80f9368 a4aa8880 -- census/round-79` (empty).

## Files written
- .ufo/waves/round-80/w1/S80ExecC1.md (this report)
- .ufo/waves/round-80/w1/S80ExecC1/replays/ (stdout receipts: c1a, c1b, c1ka, nf6b/nf8/nf10, r77/r78 W1/tip/r79, r79h W1/tip, k-* controls; status.txt files)
