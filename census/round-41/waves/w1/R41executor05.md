# R41executor05 — C3 candidate fixture (r41-refusal-sites.py)

Candidate: `.ufo/waves/round-41/w1/R41executor05/r41-refusal-sites.py`
sha256 `841d8562e40972669a25d15adff280f6ed591e471a027d36f8b480edd7f390da`, 13417 bytes. Python stdlib only.

## Design
- Protocol per c3-counter.py: `--tool PATH --work DIR`, 21 `probe-<ID>=PASS|FAIL` lines, `SUMMARY probes=21 pass=.. fail=..`, exit 0 iff fail=0.
- Each run makes a fresh `mkdtemp` under `--work` (the counter reuses one scratch for 20 runs), removes it in `finally` (restoring modes first).
- Each probe builds its own trigger, runs `python3 -B tool` with `subprocess.run(timeout=30)` and the tool's `--timeout 5`, then asserts exit 2, stderr token `REFUSAL <CLASS>:` and a detail substring. The substring separates same-class sites: S01/S03 by trigger, S12/S19 by message, S07/S08/S09 by TOTAL field.
- Hang safety: stdin is DEVNULL. P10a only `mkfifo`s the FIFO and never opens it; the tool's own O_NONBLOCK open returns ENXIO. A `TimeoutExpired` becomes `probe-ID=FAIL tool timed out`. Any other exception becomes a FAIL line, never a traceback.
- euid 0: message on stderr, exit 2, no probe lines.
- Write-stage probes (P10-P11, P15, P17, P18) use an ABSENT row plus `--skip-unrecorded`, so no git runs there. P14 and P16 use one fixture-side `git init` each (`-C` path, config neutralised through env).
- P17 also asserts the hardlinked inode keeps its bytes. P15 asserts the record is unchanged. P16 asserts the JSON file was not created.

## Commands run and output
`bash census/round-41/score-candidate.sh c3 /fast/scratch/hyaku/souji-r41/R41executor05 tests/fixtures/r41-refusal-sites.py=<candidate>` → EXIT=0

```
PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)
SITE S01..S19: all `killed`, failing set == mapped set (e.g. S02 failing=P02a,P02b; S10 failing=P10a,P10b), rc=1
SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=841d8562e409
```

Standalone run on the pinned tool: `SUMMARY probes=21 pass=21 fail=0`, rc=0, `--work` left empty. Scratch dir deleted.

## Not exercised
The euid-0 refusal path (the seat runs as uid 1000; the code is a plain `geteuid()==0` check before any probe).

## Sites not reached
None. All 19 are reached (killed=19).

## Verdict
Target met: `sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`, exit 0. This is a seat score, not the L1 measurement.
