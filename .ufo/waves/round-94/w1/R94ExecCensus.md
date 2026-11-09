# R94ExecCensus — how many of the r93 search's historical KILLS are crashes?

Seat: R94ExecCensus (executor). Lane: souji-shokunin. Round 94, C1 census (reported, not claimed).
Scope: score EVERY generated mutant of the frozen r87 counter on the r93 population, twice —
(a) r94 search (crash sentinel + r94 rule), (b) r93 rule control — same harness/population/counter
arguments as the C1 predicate, `--jobs 5`, no `--ids`.

## Instruments (all frozen, unchanged)

- Counter `census/round-87/c1-pointer-counter.py` sha256 `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b`
- Harness `census/round-93/c1-false-row-harness.py` sha256 `1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4`
- Population `census/round-93/c1-false-rows.tsv` sha256 `d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e`
- r94 search `census/round-94/c1-survivor-search.py` sha256 `97b8defa5c3c007cc10814483fe6dae6fe0f0a0bdb066b0f14169561b9f374ae`
- r93 rule control `census/round-94/c1-control-r93-rule.py` sha256 `b733032f2b5b9e19e2286f65f5f348340223af43f55672bb2eb5906982de8736` (runs frozen r93 search sha256 `6089260be7d18c5f48c5bf1289e159efba534f2ef1c5d730f9b4f356d37ed71d` with HAND extended by the 2 crash edits)

Population (gen check, computed before runs): 273 generated (268 operator mutants + 5 HAND) —
9 ambiguous (old line occurs >1: a235c7-not-to-drop, a236c15-False-to-True, a273c11-False-to-True,
a333c36-1-to-0, a381c15-True-to-False, a426c16-and-to-or, a426c20-not-to-drop, a488c15-not-to-drop,
a488c29-or-to-and), 0 uncompiled => 264 scored expected (minus hangs).

## Commands (run sequentially, never concurrently)

(a) `python3 -B census/round-94/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work /fast/scratch/hyaku/souji-r94/R94ExecCensus/work-a --jobs 5 --emit .ufo/waves/round-94/w1/R94ExecCensus/survivors-r94.json` — EXIT 0, 986 s.
(b) `python3 -B census/round-94/c1-control-r93-rule.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work /fast/scratch/hyaku/souji-r94/R94ExecCensus/work-b --jobs 5` — EXIT 0, 838 s.

## Results — both SEARCH-SUMMARY lines

- (a) r94: `SEARCH-SUMMARY generated=273 ambiguous=9 uncompiled=0 hung=1 scored=263 errored=48 killed=139 survived=76`
- (b) r93 rule: `SEARCH-SUMMARY generated=273 ambiguous=9 uncompiled=0 hung=1 scored=263 errored=20 killed=167 survived=76`

Full outputs: `search-r94-full.out`, `search-r93-full.out` in this seat dir
(sha256 afdd9bbc…, 810d457f…); run (a) also emitted `survivors-r94.json` (76 records).
Per-mutant `harness.out` preserved as `harness-r94/mNNNN.out` (265 files) and
`harness-r93/mNNNN.out` (264 files); `mNNNN` = index in `gen()` order (submitted
`enumerate(muts)`, so it includes ambiguous mutants; verified by reconstructing gen() order).
Comparison script: `compare.py` (run prints the tables below).
Scratch (`/fast/scratch/hyaku/souji-r94/R94ExecCensus/work-a`, `work-b`) deleted after receipts copied; only harness.out files retained.

### Difference table — 28 ids whose verdict differs (all r94=errored, r93=yes)

All 28 have `rc=70` ROWs in their r94 harness.out (crash rows). rc=70 row counts are from
`harness-r94/mNNNN.out` for the mapped mutant.

| id | harness.out | rc=70 ROWs / 66 | r94 | r93 |
|---|---|---|---|---|
| a165c13-and-to-or | m0003.out | 66 | errored (rc=1) | yes (rc=1) |
| a165c30-!=-to-== | m0004.out | 66 | errored | yes |
| a165c33-0-to-1 | m0005.out | 66 | errored | yes |
| a206c59-False-to-True | m0006.out | 66 | errored | yes |
| a210c12-==-to-!= | m0009.out | 60 | errored | yes |
| a218c15-not-to-drop | m0014.out | 60 | errored | yes |
| a220c41-1-to-0 | m0015.out | 60 | errored | yes |
| a250c20-not-to-drop | m0027.out | 60 | errored | yes |
| a250c28-0-to-1 | m0028.out | 60 | errored | yes |
| a268c39-0-to-1 | m0040.out | 1 | errored | yes |
| a315c66-0-to-1 | m0074.out | 66 | errored | yes |
| a320c40-1-to-0 | m0081.out | 46 | errored | yes |
| a336c26-1-to-0 | m0097.out | 16 | errored | yes |
| a415c16-and-to-or | m0144.out | 1 | errored | yes |
| a417c16-and-to-or | m0150.out | 1 | errored | yes |
| a417c64-and-to-or | m0154.out | 1 | errored | yes |
| a422c16-and-to-or | m0156.out | 1 | errored | yes |
| a425c16-and-to-or | m0160.out | 1 | errored | yes |
| a425c53-and-to-or | m0163.out | 1 | errored | yes |
| a429c16-and-to-or | m0168.out | 1 | errored | yes |
| a429c53-and-to-or | m0171.out | 1 | errored | yes |
| a491c26-or-to-and | m0201.out | 2 | errored | yes |
| a492c29-0-to-1 | m0203.out | 1 | errored | yes |
| a536c16-not-to-drop | m0223.out | 66 | errored | yes |
| a537c20-1-to-0 | m0224.out | 66 | errored | yes |
| a544c80-1-to-0 | m0234.out | 66 | errored | yes |
| h-crash-late | m0271.out | 66 | errored | yes |
| h-crash-index | m0272.out | 1 | errored | yes |

Of these 28, 9 crash on all 66 rows, 4 on 60 rows, 1 on 56, 1 on 46, 1 on 16, 1 on 2, 11 on exactly 1 row.
Sample crash row (a165c13, m0003): `ROW NF1 ... got=- rc=70 match=error detail='Traceback ... sys.exit(main(sys.argv[1:]))'` —
the uncaught exception in the mutant counter, sentinel exit 70. In the r93 run the same rows read
`rc=1` with `match=no` on some row (e.g. a268c39: `ROW NF6i ... got=REFUSED rc=1 match=no`),
so the r93 rule counted them yes (killed). That is exactly how a crash counted as a kill under the
old rule: the counter crashed AFTER printing a verdict (or printed a verdict and then died),
the harness row still compared asserted-vs-got and found a mismatch.

### Errored / hung lists (run a)

- `errored` (48): the 28 above + 4 crash-errored in both rules (a249c87-False-to-True 3/66 rc=70,
  a250c31-1-to-0 3/66, a269c82-or-to-and 1/66, a565c92-1-to-0 56/66 — under r93 they were already
  errored: r93 harness.out shows `match=error` rows and NO `match=no` row, so no kill was scored
  either way) + 16 non-crash errored in both rules (a509c21-!=-to-==, a509c24-0-to-1,
  a515c15-not-to-drop, a520c66-and-to-or, a520c70-not-to-drop, a521c16-!=-to-==, a521c31-0-to-1,
  a521c49-!=-to-==, a521c68-!=-to-==, a554c18-0-to-1, a558c19-not-to-drop, a561c26-!=-to-==,
  a561c36-1-to-0, a561c39-not-to-drop, a561c59-not-to-drop, a578c27-1-to-0 — harness rows
  `rc=2 match=error detail='C2-COUNTER-FATAL: --rev does not name a commit'`, i.e. the
  `==`-to-`!=`/`and`/`not`/`0↔1` edits break the counter's rev-resolution guard (exit 2), never the
  sentinel; r93 scored them errored too via the same rc=2 path).
- `hung` (1): a272c34-1-to-0 (line 272) — SKIP state=hung in both runs; harness.out in both runs
  has 9 ROWs then `--hung: killed after --timeout--`. A mutant that loops the counter (matches the
  r93-note "a272c34 loops"); identical under both rules.
- `ambiguous` (9): identical sets in both runs (listed in Instruments above).
- Survivors: 76 ids, sets IDENTICAL between (a) and (b) (verified set-equality; a127c26-True-to-False
  is among them: `killed=no rc=0` in both. Targets also verified in this run: h-crash-late/h-crash-index
  `killed=errored` in (a) and `killed=yes` in (b); h-ok-admits-one and a491c22-<-to-<= `killed=yes` in both.)

### Arithmetic

r93: killed 167 = 139 still-killed + 28 reclassified crashes. errored 20 (both rules) = 4 crash-without-match=no + 16 rev-guard rc=2. r94: errored 48 = 20 + 28. Scored 263 in both, skip sets identical, survivors 76 identical, recount from SEARCH lines matches both summaries (compare.py).

## Is any non-crash verdict different between the two rules?

NO. Every one of the 28 differences is `errored` (r94) vs `yes` (r93) on a mutant with rc=70 ROWs —
a crash the r93 rule counted as a kill. No survivor became killed, no kill became survived, no
`no`/`yes` pair flipped. The r94 rule reclassifies only crash mutants (those with at least one
rc=70 row), exactly as the r94 preregistration's STATED LIMITS (i) frames the claim ("the claim is
about these five verdicts, not a census of every generated mutant (a full re-score is reported,
not claimed, if the wave runs it)") — this re-score is that reported-not-claimed census, and it
confirms the mechanism on the full population: 28 of the r93 search's 167 historical kills (16.8%)
are crashes, plus 4 further crash mutants that were errored under both rules. The claim
"the rule only reclassifies crashes" holds on the full generated population with one nuance:
4 crash mutants were NOT r93 kills (errored in both rules) because their crashing rows never
produced a `match=no` line (r93 harness.out match dist = {yes, error}, SUMMARY errors=3/3/1/56,
mismatches=0).

## NO-FALSIFICATION

Nothing in this census falsifies the C1 stated wording (preregistration §C1). The five target
verdicts re-derive exactly in the full run; the rule change moves only crash mutants. What was
exercised: full — both searches over all 273 generated mutants, all 263 scored mutants compared
id-by-id, all 32 rc70-bearing harness.out files enumerated, all 20 both-rules-errored ids
characterized, survivor-set equality checked, skip-set equality checked.

## Verdict

Reported, not claimed: 28 of the r93 search's historical KILLS (of 167) are crashes — the r94
sentinel + rule moves exactly those 28 (and no other id) from `killed=yes` to `errored`, plus the
2 hand-written crash fixtures among them (26 operator mutants + 2 HAND). 4 more crash mutants were
errored under both rules; total crash-bearing mutants = 32 (12.2% of 263 scored). All other
verdicts, the survivor set, and the skip set are unchanged between the two rules.
