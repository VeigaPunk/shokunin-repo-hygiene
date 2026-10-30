# S44executor15 — C1 correction-register partition

## Axes
Calibration / operability / coverage. This assigned move registers a deterministic C1 partition; it does not establish new factual corrections, alter admission, or change historical SCORECARD text.

## Result
Created `corrections.txt` with emitted zero-based indices 14, 30, 46, and 62 (one-based emitted IDs R44-15, R44-31, R44-47, R44-63). All four rows use the required `CORRECTION-R44` grammar, `scope=base-SCORECARD-token-referents`, and `rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f`; no optional disposition/capture/register fields are present.

## Reproducible evidence
Executed from the lane:

```sh
python3 -B census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor15 --emit
```

The selected exact output records:

```text
R44-15 line=175 class=mismatch:path-absent stale=c2-after.tsv derived=multi:census/round-24/records/c2-after.tsv;census/round-25/records/c2-after.tsv;census/round-26/records/c2-after.tsv;census/round-27/records/c2-after.tsv;census/round-28/records/c2-after.tsv;census/round-42/waves/w1/R42critic01/k4/c2-after.tsv
R44-31 line=666 class=mismatch:path-absent stale=c1-vacuity2.txt derived=census/round-38/records/c1-vacuity2.txt
R44-47 line=725 class=mismatch:path-absent stale=a7-counter-fixes2.txt derived=census/round-38/records/a7-counter-fixes2.txt
R44-63 line=821 class=mismatch:path-absent stale=controls/c1-control.txt derived=multi:census/round-41/controls/c1-control.txt;census/round-42/controls/c1-control.txt
```

Independently checked emitted derivations against committed base data with:

```sh
root=/home/vgpnk/Projects/shokunin/souji-shokunin
rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f
git -C "$root" show d314fd6e85d62565344fa6c4b102f52f62297884:SCORECARD.md | awk 'NR==175 || NR==666 || NR==725 || NR==821 {print NR ":" $0}'
git -C "$root" ls-tree -r --name-only "$rev" | grep -E '(^|/)c2-after.tsv$|(^|/)c1-vacuity2.txt$|(^|/)a7-counter-fixes2.txt$|(^|/)c1-control.txt$'
git -C "$root" show "$rev":SCORECARD.md | awk 'NR==175 || NR==666 || NR==725 || NR==821 {print NR ":" $0}'
```

Observed in the base tree: `c2-after.tsv` has exactly the six listed basename matches (r24–28 and r42 critic fixture); `c1-vacuity2.txt` and `a7-counter-fixes2.txt` each have the single listed path in `census/round-38/records/`; `controls/c1-control.txt` has exactly the two matching suffix paths in r41 and r42. The frozen lines show the selected token occurrences (line 725 is a wrapped prose statement beginning with the token on that line). Thus the tokens are not themselves equal to those committed paths; derived values describe matching committed referents under the counter's basename/suffix rule.

## Q76 prior-correction check
- **R44-15 / SCORECARD.md:175 / `c2-after.tsv`: already covered** by round 42's explicit `CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent` at `corpus/lessons/round-42.md:81-87`. The new registration records the r44 token-bound referent result, not a new fact.
- **R44-31 / line 666 / `c1-vacuity2.txt`: no prior r42/r43 correction for this item found.**
- **R44-47 / line 725 / `a7-counter-fixes2.txt`: no prior r42/r43 correction for this item found.** Round 42 discusses the separately named `a7-counter-fixes.txt` receipt at another SCORECARD line; it does not correct this token/line.
- **R44-63 / line 821 / `controls/c1-control.txt`: no prior r42/r43 correction for this item found.** Round 42's erratum discusses the attribution/provenance of the round-42 control at other text; no correction for this SCORECARD token occurrence was identified.

Round 43's C1 correction register concerns three round-39 receipt values, not these four SCORECARD references. Registration alone does not mean the historical statements are new or newly false; no historical SCORECARD content was edited.

## Limitations / status
The bounded `--emit` run completed successfully and produced 66 unique emitted records. This seat did not run the full C1 gate or whole-suite checks. `--emit` derives from committed bytes but does not establish natural-language meaning of each historical cell; the explicit prior-correction check is a bounded search/read of r42/r43 lesson text. Existing unrelated working-tree changes were observed before work and left untouched. No tool was installed or updated. Scratch was removed before handoff.
