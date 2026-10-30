# S44executor14 — C1 partition 14/16

Axes: calibration (assigned); operability and coverage not assessed by this seat.

Files: `corrections.txt` (four selected register lines); this report.

Executed counter command from the explicitly assigned scratch directory:

```sh
python /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor14 --emit
```

It returned exit 0 and emitted 66 unique records. Selected zero-based positions divisible by 16 with remainder 13, i.e. 1-based R44-14, R44-30, R44-46, R44-62. Their exact output-derived class/stale/derived tuples are respectively:

- `line=174 class=mismatch:path-absent stale=c1-control-stub.tsv derived=census/round-24/records/c1-control-stub.tsv`
- `line=540 class=mismatch:path-absent stale=controls.txt derived=multi:census/round-33/records/controls.txt;census/round-34/records/controls.txt`
- `line=722 class=mismatch:path-absent stale=c2-after6.txt derived=census/round-38/records/c2-after6.txt`
- `line=811 class=mismatch:path-absent stale=c3-after-h.txt derived=census/round-40/records/c3-after-h.txt`

Independent committed-base inspection used `git show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md` for each cited historical line and `git ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f` to resolve token referents. Observed: line 174 contains token `c1-control-stub.tsv`, and only `census/round-24/records/c1-control-stub.tsv` matches; line 540 contains `controls.txt` and two matching paths (round 33/34 records); line 722 contains `c2-after6.txt`, matched by round 38 records; line 811 contains `c3-after-h.txt`, matched by round 40 records. This supports the emitted deterministic exact/sorted referent values, including multi-valued case.

Q76 prior-correction check: inspect `corpus/lessons/round-42.md` and `corpus/lessons/round-43.md` as committed in the base for correction-register coverage of these four `(file,line,class,stale)` items. None of these four was confirmed as already covered by a prior R42/R43 correction; therefore the partition registers each one. This registration is not a claim of a new factual correction; it records the existing base-SCORECARD token referents only. Historical line numbers are retained; SCORECARD was not edited.

Limitations: the script's counter emitter and committed base inspection were exercised; no full C1 population acceptance counter was run, and this seat does not assert the overall 66/70 counter target. No tool was installed or updated. The output grammar omits optional disposition/capture/register fields as required.
