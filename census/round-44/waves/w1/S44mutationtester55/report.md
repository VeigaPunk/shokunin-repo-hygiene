# S44mutationtester55 — C2 discrimination mutation probe

**Result: SURVIVED the bounded discrimination detector; coverage finding, not a contract change.** No production counter/audit bytes were changed. Admission remains outside non-author closure; no scoring or shipping judgment is made.

Axes: calibration, operability, coverage. Focus: operability of frozen C2 control discrimination.

## Frozen inputs

Wave revision: `d314fd6e85d62565344fa6c4b102f52f62297884` (round-44 freeze). Read `census/round-44/preregistration.txt`, `c2-counter.py`, `c2-hidden-audit.py`, scenarios and retained do-nothing receipt.

SHA-256 at the wave revision matches the worktree/scratch input:

- counter: `0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252`
- audit: `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`
- scenarios: `6a68a10161745c7974e93afe9724853f1a61fc192185c128c88840b1977a7054`
- tool: `f7f54e8f0a71aa952a66f53abb12dcd96f2805d8a8ef141c4b741a7865d87999`

Calibration note: the preregistration's claim Base `55d7af6f5a22340f7a3de1c386e514ababfaa75f` predates the r44 census files. `git show BASE:census/round-44/c2-hidden-audit.py` reports that the path exists on disk but not at that revision. This is not a baseline behavioral failure: the actual probe uses the specified wave freeze revision above.

## Single defect

Only scratch audit line 162 changed:

```diff
-            ok = p.returncode == want_exit and classes(p) == sorted(want)
+            ok = True
```

Plausible defect: confusing successful subprocess completion (`p is not None`, the enclosing condition) with a correct scenario result. This removes exit-code/finding-class discrimination for h1–h9; the separately implemented h10 refusal check stays intact.

Preserved candidate: `c2-hidden-audit.mutated.py`. Pristine candidate and the exercised driver are also retained beside this report.

## Detector and exact commands

The same `drive.py` runs all three phases. It extracts the real tool from the frozen wave revision, runs the audit against that tool plus the counter's byte-identical `STUB_CLEAN` and `STUB_FINDINGS`, parses `(pass, fail, total)` using the counter's regex, and applies its exact rejection predicate:

```python
ok = v is not None and v[1] > 0 and v[0] < v[2]
```

All subprocesses use the seat scratch as cwd and distinct fixture work directories. The outer driver invocation has a 240-second bound; each audit invocation also has a 1200-second bound, with the frozen audit's own per-candidate 300-second timeout.

Let `S=/fast/scratch/hyaku/souji-r44/S44mutationtester55`. Exact exercised commands (fully expanded in receipts):

```sh
python3 -B $S/drive.py $S/c2-hidden-audit.pristine.py pristine
python3 -B $S/drive.py $S/c2-hidden-audit.mutated.py mutated
# Restore the mutated file by exact byte copy from the pristine snapshot.
python3 -B $S/drive.py $S/c2-hidden-audit.mutated.py restored
```

The restoration copy is in a Python `finally` block, before the restored run. Raw stdout/stderr and exact expanded commands: `receipts/pristine.txt`, `receipts/mutated.txt`, `receipts/restored.txt`.

## Actual results

Counts below are audit `SUMMARY scenarios=10 pass=P fail=F`; exit is the audit exit, not merely driver success. Every driver invocation exited 0 and produced empty stderr.

| Phase | Real tool (P/F; exit) | Clean stub (P/F; exit) | Findings stub (P/F; exit) | Counter-equivalent discrimination fields |
|---|---|---|---|---|
| Pristine | 10/0; 0 | 2/8; 1 | 0/10; 1 | hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED |
| Mutated | 10/0; 0 | 9/1; 1 | 9/1; 1 | hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED |
| Restored | 10/0; 0 | 2/8; 1 | 0/10; 1 | hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED |

This is **survival**, not a crash and not a killed mutant. All nine mutated ordinary scenarios report PASS for both constant-output stubs. Only `h10-missing-prereg-refusal` reports FAIL for each stub. That single remaining failure satisfies the frozen counter's `fail>0 && pass<total` predicate, so both remain labelled REJECTED. The pristine baseline is green for the exercised property and the restored behavior reproduces it exactly.

Observed finding: the aggregate discrimination legs cannot distinguish their fully checking audit from one that ignores correctness for nine scenarios. They establish that these two stubs fail somewhere, not that each scenario discriminates. This does not authorize changing the frozen contract.

## Restoration and limits

Audit SHA-256 sequence:

- before: `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`
- mutated: `cea1f700a426d05628f2d66677e2f89f3b25b6e0e89f9a600aeda545029453bc`
- restored: `50872b0da7a36d377ced9cf0e51579ef00f0f0ae402eebad8c579fce6e5e843e`

Machine-readable evidence: `receipts/hashes.json`. Scratch is removed after preserving these receipts; deletion evidence is recorded in `receipts/cleanup.txt`.

Scope: this is one bounded audit/control-discrimination mutation probe, not a full invocation of the blob-bound C2 counter. Its historical r43/r42 retention chain, population, direct-control-run and selftest legs were not run or certified. No complete C2 target exit is claimed. The counter's applicable verdict predicate is exercised verbatim on measured audit outputs. Only the assigned output paths and seat scratch were written; no production, sibling, fleet index or shared bookkeeping was edited. No commits/pushes/delegation. Fixture histories were built by the frozen audit inside seat scratch. Python 3.14.8 was already available; no tools were installed or updated.

## Self-evaluation

Accuracy 4/5: raw exits and summaries retained; full counter success intentionally not claimed. Completeness 4/5: one defect, three phases and cleanup covered; evidence is bounded to discrimination, not the historical retention chain. Clarity 4/5: table separates driver/audit exits; verbose raw details live in receipts. Actionability 4/5: exact predicate and reproducible candidates identify where aggregate rejection loses sensitivity. Conciseness 4/5: hashes and command receipts add length but preserve reproducibility. Overall 4.0/5. Highest-impact improvement for the integration owner to consider separately: evaluate per-scenario discrimination expectations rather than only aggregate stub failure. The user should agree with the bounded survival finding; no whole-counter conclusion follows.
