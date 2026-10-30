# S44critic45 — C1 extra-register-row

Axes: calibration / operability / coverage; assigned surface calibration. No admission judgment.

**Result:** frozen counter rejected both the valid 66-entry control and the same register plus one unique out-of-population entry (67 total), exit 1 in both cases. No green bypass was observed; these reds do not establish extra-row detection.

Both printed:

```text
SUMMARY population=70 corrections=66 registered=0 missing=70 junk=0 fenced=0 duplicate=0 retracted=0 rederive=0 rederive_failed=0 new_mismatches=0 instrument_mismatches=66
```

Frozen `c1-counter.py:244` indexes `(line,class,stale)` while lines 249/253 query `(line,token,class)`, making normal registration impossible for this population. Separately, extra correction keys are never rejected and the summary reports population-key count instead of parsed-entry count. The added row changed no summary field. A surviving green extra-row mutant after key-order repair is a static inference, not an executed result.

Smallest safe correction: normalize key ordering, reject out-of-population correction keys, and report actual parsed corrections, retaining 70 occurrences over 66 unique keys. Re-freeze with a passing valid control and failing extra-row control; do not reinterpret the old reds.

Q76 whole-base-file audit: selected population token `c1-control-stub.tsv` at SCORECARD line 174 is already bound by base SCORECARD line 399 (L34, full receipt path and `cases=8 pass=4`); runtime corrections also exist at lines 334/398/505. The synthetic extra token and line 999999 have no base-file matches. Green token registration would not demonstrate 70 newly corrected facts or numeric calibration improvement, consistent with preregistration.

Full report, exact commands, candidate lessons, frozen inputs, fixture commits, outputs and Q76 audit: [S44critic45/report.md](S44critic45/report.md). Control revision `a51fb17330fb7e791e45107743bbcf765c6549b7`; extra-row revision `e95d05f9212cfb81250f21f056e6646235305810` exist only in the isolated fixture. Source revision `d314fd6e85d62565344fa6c4b102f52f62297884`; frozen counter/population hashes asserted against preregistration. Only assigned bounded probes ran. No installations or production changes; owned scratch removed.
