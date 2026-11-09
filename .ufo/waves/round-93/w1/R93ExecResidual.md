# R93ExecResidual — residual 78-id set on r92 vs r93 populations

## Runs (exact commands, cwd /home/vgpnk/Projects/shokunin/souji-shokunin)

Shared args: `--counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --jobs 4 --ids census/round-93/c1-residual-plus-e1.json`.

r92 population:
`python3 -B census/round-93/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-92/c1-false-rows.tsv --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work /fast/scratch/hyaku/souji-r93/R93ExecResidual/work-r92 --jobs 4 --ids census/round-93/c1-residual-plus-e1.json --emit .ufo/waves/round-93/w1/R93ExecResidual/survivors-r92.json` → EXIT 0, 347.81 s.

r93 population: same with `--population census/round-93/c1-false-rows.tsv --work /fast/scratch/hyaku/souji-r93/R93ExecResidual/work-r93 --emit .ufo/waves/round-93/w1/R93ExecResidual/survivors-r93.json` → EXIT 0, 323.80 s.

## SEARCH-SUMMARY lines

- r92 pop: `SEARCH-SUMMARY generated=78 ambiguous=0 uncompiled=0 hung=0 scored=78 errored=0 killed=0 survived=78`
- r93 pop: `SEARCH-SUMMARY generated=78 ambiguous=0 uncompiled=0 hung=0 scored=78 errored=0 killed=2 survived=76`

Full receipts: seat dir `receipt-r92.txt`, `receipt-r93.txt` (78 SEARCH lines + summary + `EXIT=0` each). Emitted survivors: `survivors-r92.json` (78), `survivors-r93.json` (76); both verified set-equal to the corresponding `killed=no` sets. Full per-id verdict table: `verdict-table.tsv` (78 rows, plus the r91 column below).

## (a) Verdict differences between populations: exactly 2

| id | r92 pop | r93 pop | Killing ROW line (r93 harness.out) |
|---|---|---|---|
| `h-ok-admits-one` | survived (rc=0) | killed (rc=1) | `ROW LD5 where=ledger-drop rev=BASE item=P04 class=- expect=UNRESOLVED/1 got=UNRESOLVED rc=0 match=no` (exit-code arm binds it) |
| `a491c22-<-to-<=` | survived (rc=0) | killed (rc=1) | `ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=UNRESOLVED rc=1 match=no` |

All other 76 ids: `killed=no` on both populations. The two diffs are exactly the two C1 targets from `census/round-93/c1-targets.json`; witness receipts: seat dir `harness-h-ok-admits-one.out`, `harness-a491c22.out` (full harness.out for each killed mutant).

## (b) Errored/hung ids: none

- r92 population: `errored=0 hung=0` — no id reads `errored`, no id timed out.
- r93 population: `errored=0 hung=0` — no id reads `errored`, no id timed out.
- Therefore there is no first-failing ROW line to report for either population.

## (c) Extra-kill verdict: none

The only ids killed on r93 are `h-ok-admits-one` and `a491c22-<-to-<=`, both C1 targets. No unpredicted extra kill. (Corroboration of the prereg's "REPORTED, NOT CLAIMED" statement: `killed=0 survived=78` on r92, `killed=2 survived=76` on r93, with both kills being the two targets.)

## (d) Cross-check against census/round-92/records/c1-search-r91-full.txt (old kill rule)

- The r91 receipt's `killed=no` rows total 124 (`grep -c 'killed=no'`); 77 of the 78 residual ids appear among them, and all 77 still read `killed=no` on the r92 population under the r93 kill rule: **none reads `errored`, none flipped the other way either.**
- The 78th id, `h-ok-admits-one`, is a r93 hand edit and does not appear in the r91 receipt at all (it is the only id not in the r91 survivor set — verified by set difference against the regenerated 270-id generation order).

## FALSIFICATION / NO-FALSIFICATION

NO-FALSIFICATION. Numbers re-derived exactly as the prereg's reported (not claimed) statement requires, and nothing this seat produced falsifies any sentence of C1 or C2: on the 78-id residual set the r92 vs r93 difference is precisely the two predicted kills, no extra kill, no errored/hung rows, and all 77 old-rule survivors hold. (This seat ran no C2 fixture or probe; nothing produced here bears on C2.)

## Notes and risks

- Both searches ran with `--jobs 4`; each per-mutant tree clone (~0.7 GB) was deleted once scored by the search itself (LIVE cleanup per its docstring); scratch was deleted after receipts were copied to the seat dir (verified absent). Nothing was committed, pushed, or written outside the seat dir and report.
- Scratch was removed, so `--work` trees no longer exist; the only durable evidence is the two receipts, two emitted survivor JSONs, two harness.out files, and the verdict table in the seat dir.
- This run used lane path `/home/vgpnk/Projects/shokunin/souji-shokunin` (the seat lands in the same checkout the L1 integrates). Results are path-independent given `--fleet-root`.
- One methodological caveat: the r91 cross-check compares rows matched **by mutant id string** across the r91 receipt and the r93 generation. Id strings encode line/column/token, and the counter is byte-identical (sha256 pinned in the prereg, unchanged since r87), so id equality implies edit equality here; the a573-like lookalikes (e.g. `a573c27->-to->=` vs `a573c29-0-to-1`) are distinct ids in both sets and were not conflated.

## Files written

- `.ufo/waves/round-93/w1/R93ExecResidual/receipt-r92.txt`, `receipt-r93.txt` (full search output, 78 SEARCH lines each)
- `.ufo/waves/round-93/w1/R93ExecResidual/survivors-r92.json` (78), `survivors-r93.json` (76)
- `.ufo/waves/round-93/w1/R93ExecResidual/harness-h-ok-admits-one.out`, `harness-a491c22.out`
- `.ufo/waves/round-93/w1/R93ExecResidual/verdict-table.tsv`
- `.ufo/waves/round-93/w1/R93ExecResidual.md` (this report)

No tool installs (none needed). No commits, no pushes, no git/jj mutations anywhere.
