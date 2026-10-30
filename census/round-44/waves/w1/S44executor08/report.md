# S44executor08 — C1 correction-register partition 8/16

Axes: calibration (C1); operability and coverage not exercised by this seat.

Ran the frozen emission command:

`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor08 --emit`

It exited successfully and emitted 66 unique-key rows. Partition is the records with zero-based emitted index congruent to 7 mod 16 (1-based IDs R44-08, R44-24, R44-40, R44-56). The selected counter output was:

```
R44-08 line=68 class=mismatch:path-absent stale=repo-size-census-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/repo-size-census-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/repo-size-census-readonly.md;corpus/knowledge/repo-size-census-readonly.md
R44-24 line=478 class=mismatch:path-absent stale=.ufo/waves/round-32/a2w1/SwarmExecutor08.md derived=UNHELD
R44-40 line=702 class=mismatch:path-absent stale=a7-counter-fixes2.txt derived=census/round-38/records/a7-counter-fixes2.txt
R44-56 line=762 class=mismatch:path-absent stale=c2-after.txt derived=multi:census/round-36/records/c2-after.txt;census/round-37/records/c2-after.txt;census/round-38/records/c2-after.txt;census/round-39/records/c2-after.txt;census/round-40/records/c2-after.txt;census/round-41/records/c2-after.txt;census/round-42/records/c2-after.txt
```

Independently checked committed base-tree paths with `git ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f`: R44-08 yields the three exact basename matches shown; the requested R44-24 path has no basename match; R44-40 has the unique basename match `census/round-38/records/a7-counter-fixes2.txt`; R44-56 yields the seven exact basename matches shown. This confirms the counter's path derivations from committed tree bytes. No SCORECARD line was edited.

Historical status: analogous items were already registered in r42's C1 register. The r42 `c1-items.tsv` and `c1-register.tsv` evidence explicitly contains line 68 `repo-size-census-readonly.md`, line 478 report, line 702 `a7-counter-fixes2.txt`, and line 762 `c2-after.txt`; the register resolves each. Thus all four selected referents have earlier correction coverage (R44-40 exact token specifically matches the r42 line-702 token). Registration alone is not a new factual correction. `corrections.txt` contains only the four required grammar lines, exact scope and base revision, and no optional fields.

Evidence/limits: emission did not print its derivation revision; inspected counter source pins derivation to `BASE_REV=55d7af6f5a22340f7a3de1c386e514ababfaa75f` and derives from committed `git show`/`ls-tree`. Prior-coverage claim is based on the retained r42 inventory/register records. No tool installation. No builds, lint, tests, or unrelated suite run.
