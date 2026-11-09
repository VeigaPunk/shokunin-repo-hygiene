# R93ReviewerC1 — C1 falsification review (committed bytes)

Scope: C1 only (calibration 7). Lane base 91c9bcb1; P1 2c82d362 (instruments); P2 0d6442cc (controls); F 9a4ab88f (prereg only, verified: one file, 80 insertions); A 7bdb96b7 (after receipts). Read-only on the lane; scratch under /fast/scratch/hyaku/souji-r93/R93ReviewerC1/ (deleted before yield; text receipts copied to `.ufo/waves/round-93/w1/R93ReviewerC1/receipts/`).

Verdict: one wording falsification (FALSIFIES-WORDING, "reaches their clause"); the verdict-level claim holds on every number and reproducer I ran. No FALSIFIES-NUMBER.

## 1. Independent SUMMARY lines (my runs, same committed bytes)

After, r93 population (`census/round-93/c1-false-rows.tsv`, sha256 d6439f65…), r93 harness, targets `c1-targets.json`, `--jobs 2`, EXIT 0:
```
SEARCH a491c22-<-to-<= line=491 killed=yes rc=1
SEARCH h-ok-admits-one line=552 killed=yes rc=1
SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=2 survived=0
```
Control, r92 population (`c1-false-rows.tsv` at census/round-92, sha256 f66341fc…), same harness and search, EXIT 0:
```
SEARCH a491c22-<-to-<= line=491 killed=no rc=0
SEARCH h-ok-admits-one line=552 killed=no rc=0
SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0 scored=2 errored=0 killed=0 survived=2
```
Pristine r93 harness, r93 population, EXIT 0:
```
ROW LD5 where=ledger-drop rev=BASE item=P04 class=- expect=UNRESOLVED/1 got=UNRESOLVED rc=1 match=yes
ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=MOVED rc=0 match=yes
SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0
```
Both match the prereg predicate and the P1 prediction exactly. Which row killed which mutant (`after-work/m0000`, `m0001` harness.out): `a491c22` only via LD6 (`got=UNRESOLVED rc=1 match=no`); `h-ok-admits-one` only via LD5 (`got=UNRESOLVED rc=0 match=no`). The control prints zero `match=no` rows.

Extra independent runs (r92 harness, census/round-92, r92 population, logging wrapper that passes the real counter's output through unchanged):
```
pristine counter:            SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0   EXIT 0
h-ok-admits-one (hand edit): SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0   EXIT 0
a491c22 (<=, hand edit):     SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0   EXIT 0
```
Both mutants match on all 64 rows, so both survive the r92 harness, as claimed. Mutant diffs: `receipts/mutant-hok.diff`, `receipts/mutant-a491.diff` (one line each).

## 2. Sentence table

Claim text is prereg lines 20-54 (C1).

| # | Sentence (abridged) | Reading | Evidence |
|---|---|---|---|
| S1 | "Two counter edits survive every r92 row" | HOLDS | r92 harness 64/64 match under both mutants (§1); r92-population control survived=2. |
| S2 | "because no r92 run reaches their clause" | **FALSIFIES-WORDING** (literal) | Line 491 (`_ledger` guard) and line 552 (success test) are executed in all 64 r92 runs: every r92 run loads a ledger and computes `ok` (`receipts/log-r92-pristine.txt`, 64 lines, all `ledger=`). Literal "reach" is therefore false for both clauses. |
| S2a | …same sentence, behavioural reading for h-ok-admits-one | **FALSIFIES-WORDING** (narrow) | Under the h-ok mutant three r92 runs change exit code 1→0: rows NF-R (R8, item I85R), NF-S (R8, I85T), NF-W (R9, I85R). Diff: `receipts/log-r92-hok.txt` vs `log-r92-pristine.txt`; ROW lines in `receipts/r92-pristine-harness.txt` vs `r92-hok-harness.txt`. Each row has expect `REFUSED/-`: the harness never asserts rc on them, so the verdict is unchanged. The reach is real; "no r92 run reaches" is not. |
| S2b | …same sentence, behavioural reading for a491c22 | HOLDS (behavioural), FALSIFIES literal | Zero r92 runs change rc under `<= 3` (`receipts/log-r92-a491.txt` vs pristine: 0 differing). No r92 row loads a 3-column ledger row: appended rows are 4-col (LD1, LD1b, LD1c), 2-col (LD2, LD2b), 1-col (LD3); LD4/LD4r use the frozen 4-col ledger. Literal reach as in S2 is still false. |
| S3 | "Two appended rows of two NEW harness row types bind both" | HOLDS | Each mutant is killed only by its own target row (§1). Row types are `ledger-drop` (LD5) and `ledger-trim` (LD6), both new in `c1-false-row-harness.py` (lines 439-457). "Appended" means appended to the population: correct, the rows edit a scratch ledger, not the frozen one. |
| S4 | "LD5 … P04's own row removed … exactly one item is UNRESOLVED and no id is unknown; asserts UNRESOLVED and exit 1" | HOLDS | Counter log for LD5 (`receipts/log-r93-pristine.txt`, run with `ledger=ledger-LD5.tsv`): `items=35 resolved=34 unresolved=1 refused=0 … rc=1`. `refused` counts unknown ids and bad ledger rows (counter lines 547-549), so `refused=0` means no unknown id. Pristine counter exit 1 as asserted. |
| S5 | "LD6 … P04's row cut to its first three columns; asserts MOVED and exit 0" | HOLDS | Log line `rc=0 … ledger=ledger-LD6.tsv … resolved=35 unresolved=0`. The harness keeps `[:3]` of the frozen 4-column r77 P04 row (`P04\tMOVED\tcensus/round-32/waves/a2w1/SwarmExecutor08.md`). |
| S6 | "Population … 66 rows = the r92 64 byte-for-byte plus one comment line, LD5 and LD6" | HOLDS | First 67 lines of r93 TSV (3 comments + 64 rows) are identical to the whole r92 TSV (`diff`, empty). r93 adds one comment line (4 comments total) and two rows: 66 data rows. sha256 d6439f65… matches. |
| S7 | "sha256 d6439f65a632cf83…" | HOLDS | `sha256sum census/round-93/c1-false-rows.tsv` = d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e. |
| S8 | "The two targets were named in P1 … from reading the clauses, before any mutant was scored on the r93 population" | HOLDS (mutant part); see chronology note | `c1-prediction.txt` is in P1 (2c82d362), the first round-93 commit after base; no mutant receipt exists in any commit before P1. "From reading the clauses" is prose I cannot falsify. |
| S9 | "Counter census/round-87/c1-pointer-counter.py unchanged (sha256 fd0a8e24…)" | HOLDS | sha256 fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b; `git diff 91c9bcb1 HEAD -- census/round-87/c1-pointer-counter.py census/round-92` is empty. |
| S10 | Prereg stated limit (iv): "a reviewer must confirm the r92 64 rows are byte-identical and that the two new row types edit only the item's own ledger row" | HOLDS | Byte identity: S6. Own-row only: harness lines 445-454 require `len(own)==1`, then delete (`ledger-drop`) or cut (`ledger-trim`) that single line; other lines are written back unchanged. LD5/LD6 run without `--forge` (harness line 458-459). |
| S11 | Prereg "CONTROL (P2)": r92 population search `killed=0 survived=2` | HOLDS | §1 control (my independent run). |

## 3. Chronology

- `git log` (lane branch): base 91c9bcb1 → P1 2c82d362 (00:31:40) → F 9a4ab88f (00:42:49) → P2 0d6442cc (00:41:24) → A 7bdb96b7 (00:43:29). Commit order in the log is P1, P2, F, A; the prereg text lists F as "commit F" with P2 as control. The timestamps show P2 (00:41:24) before F (00:42:49): consistent with the prereg being frozen after the controls. (F's `git show --stat` contains only `census/round-93/preregistration.txt`.)
- `census/round-93/c1-prediction.txt` and `c1-targets.json` first appear in P1 (`git log -- census/round-93/c1-prediction.txt` → 2c82d362 only). P1 stat lists no receipt under `records/` except `sources-census-before.txt` (not a C1 receipt).
- Disclosed, not a breach: `census/round-93/controls/prefreeze-feasibility-note.txt` (committed in P2) states that the pristine r93 harness on the r93 population was run before P1, with outputs not saved, and that "no mutant was scored on the r93 population before the freeze." I did not re-run that pre-freeze pristine check (it was not saved); my pristine r93 run (§1) reproduces the same SUMMARY and LD5/LD6 lines.
- P2 control receipts are on the r92 population (`c1-control-r92-population.txt` names `census/round-92/c1-false-rows.tsv`), so they satisfy "before any r93-population mutant."

## 4. Kill-rule reading (`census/round-93/c1-survivor-search.py`, `verdict()` lines 86-93)

```
rc==0                                  -> "no"  (survived)
rc==1 and any line startswith ROW and endswith " match=no"  -> "yes" (killed)
otherwise                              -> "errored"
```
- Can a mutant be `yes` without a row mismatch? No. The harness prints `match=no` only when `ok` is false, and `ok` false increments `mism` (harness lines 470, 511, 532, 556). Exit 1 is returned on `mism>0` or `errs>0`. A `yes` therefore always has at least one asserted row mismatch.
- Can a mutant be `no` with a row mismatch? No. `mism>0` forces exit 1, so rc 0 implies zero mismatches (harness line 560).
- Gap (not observed, not a falsification): the verdict does not record which row killed the mutant. A mutant that crashes on its target row (`match=error`, errs>0) but mismatches an unrelated row would be `yes`. In both r93 kills the killing row is the target row (§1), so the observed kills bind the edits. A mutant that fails only through an unrelated row would not, and the search would not show it.
- Mixed case (some `match=error` rows plus one `match=no` row) is `yes` under the literal rule text. Consistent with the rule as written.

## 5. Falsification list

FALSIFIES-WORDING
1. Prereg C1 CLAIM, sentence "…survive every r92 row because no r92 run reaches their clause": the literal "reaches" is false for both clauses. Lines 491 and 552 are executed in all 64 r92 runs. Reproducer: `.ufo/waves/round-93/w1/R93ReviewerC1/receipts/log-r92-pristine.txt` (64 counter runs, all loading a ledger).
2. Same sentence, narrowest true version: h-ok-admits-one changes the counter's exit code in three r92 runs (NF-R, NF-S, NF-W, rc 1→0), none of which asserts rc. Reproducer: `receipts/log-r92-hok.txt` vs `receipts/log-r92-pristine.txt`; `receipts/r92-pristine-harness.txt` vs `receipts/r92-hok-harness.txt` (rows NF-R, NF-S, NF-W). Suggested narrowing (for the L1 to record as an amendment in plans/round-93.md): "no r92 row asserts a verdict or an exit code that either edit changes." Under that wording the survival claim holds.

FALSIFIES-NUMBER
- None. All numbers I checked reproduce: 66 rows, 64-row prefix, SEARCH-SUMMARY (after and control), SUMMARY (pristine r93 and r92 mutants), LD5 `resolved=34 unresolved=1 refused=0`, LD6 `MOVED rc=0`, sha256 values for the population and the counter.

NO-FALSIFICATION (for the rest of C1)
- Sentences S1, S3-S7, S9-S11 hold under my runs. The prediction chronology holds (S8).

## 6. Residual risk / verification gaps

- I did not re-run the r92 search itself (`census/round-92/c1-survivor-search.py`) and did not read `R92MutC1`'s §2 E1 / §3c text (only confirmed the citation exists in `corpus/lessons/round-92-verifier-spotcheck.md` and `round-92.md`). The "no r92 run reaches" check was done by direct logged runs instead.
- Verified rc of the r92-population control with the r93 harness, not with the r92 harness. The r92 harness mutant runs (§1) cover the r92 side.
- The pre-freeze pristine r93 run is disclosed as unsaved; I did not verify it independently beyond my own pristine run.
- Tools: none installed. Python 3 stdlib only.
- Scratch: `/fast/scratch/hyaku/souji-r93/R93ReviewerC1/` (4 harness work trees per batch at most; `--jobs 2`), deleted before yield.
