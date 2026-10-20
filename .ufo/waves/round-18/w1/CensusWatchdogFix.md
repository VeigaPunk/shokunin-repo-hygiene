STATUS: DONE — Per-repository census and preflight are bounded; selftest and B1–B12 regression suite pass.

## Axes

- **Operability (primary):** a repository-specific Git hang no longer prevents healthy neighbors from producing rows, and normal/selftest cleanup is bounded.
- **Calibration:** timeout configuration and timeout/error attribution are explicit and stable; ordinary nonzero or externally killed workers are not mislabeled as timeouts.
- **Coverage:** both guarded preflight and `census_one` are supervised, including timed-out gitfile candidates.

## Changed behavior

Only `tools/souji-census.sh` changed in the private clone `/var/tmp/souji-r18-CensusWatchdog/lane-5efb` (base `5efb519f00075d958c3d1109ef6fcb24c487eb87`).

- Added `--repo-timeout N` and `SOUJI_CENSUS_REPO_TIMEOUT`; accepted values are integers 1–86400 seconds, default 600, with invalid values exiting 2 (`tools/souji-census.sh:66-68,313-326,3013-3033`).
- Runs each candidate guard and census worker in a private process group with output in CENSUS_TMP files. The detached watchdog records a timeout sentinel before TERM, escalates to KILL after two seconds, and is killed/reaped when its repository finishes. Hot-success polling uses 10ms for the first 20 polls, then 100ms (`tools/souji-census.sh:1544-1706`).
- A timed-out repository produces `<repo>\t0\t0\t0\t0\t\terror` and `souji-census: repo-timeout <N>s <repo>`; neighbors continue. Exit 2 is preserved for protected refusal, and ordinary nonzero worker status remains a census failure (`tools/souji-census.sh:1718-1775`). Timeout attribution is sentinel-based, not inferred from rc 137.
- Preflight timeouts for `repo` and `gitfile` candidates are retained as error rows and deduplicated; unrelated path/symlink candidates do not gain rows (`tools/souji-census.sh:1720-1749`).
- Parent HUP/INT/TERM cleanup stops the active worker and watchdog before deleting temporary state. The timer remains responsible for worker/temp cleanup after an untrappable parent SIGKILL (`tools/souji-census.sh:242-310,1557-1585`).
- Sets `GIT_ATTR_NOSYSTEM=1`; rejects raw TAB/LF/CR paths before lexical normalization; skipped ambiguous repo basenames get sanitized diagnostics (`tools/souji-census.sh:189-203,514-533,1484-1489`).
- Header documentation records the timeout controls, exit behavior, timeout diagnostics, and bounded-reap caveat (`tools/souji-census.sh:150-182`).

## Verification evidence

Commands were run against the final source in the private clone:

```text
bash -n tools/souji-census.sh
exit 0; no output

shellcheck -S warning tools/souji-census.sh
exit 0; no output

TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
exit 0
selftest: 69 checks, 0 failed
```

The original selftest count was 49 (assignment baseline); the final count is 69. The final selftest measured the FIFO timeout case at 3429ms (<6000ms for a 1s bound plus 5s), with both neighbors measured, no job-control warning, no FIFO reader, and no surviving Git PID. The nine-call slow-Git case completed normally in 18282ms. Parent SIGTERM cleanup, parent SIGKILL timer cleanup, protected refusal exit 2, and unmarked worker SIGKILL classification all passed.

```text
PYTHONPYCACHEPREFIX=/var/tmp/souji-r18-FixtureR18BoundedFix/pycache \
  python3 /var/tmp/souji-r18-FixtureR18BoundedFix/lane/tests/fixtures/r18-census-bounded.py \
  --census /var/tmp/souji-r18-CensusWatchdog/lane-5efb/tools/souji-census.sh
```

Completed; fixture output was:
```text
TOOL	/var/tmp/souji-r18-CensusWatchdog/lane-5efb/tools/souji-census.sh	sha256=21c19ff620ad92c26df15550f473158d887a1bba0967e9e2686cf1b5d0f21629
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{"residue":"clean"},"observed_exit":0,"observed_rows":{"residue":"clean"},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B9	PASS	{"expected_exit":0,"expected_rows":{"target":"error"},"observed_exit":0,"observed_rows":{"target":"error"},"problems":[]}
CASE	B10	PASS	{"expected_exit":null,"expected_rows":{},"observed_exit":-9,"observed_rows":{},"problems":[]}
CASE	B11	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B12	PASS	{"expected_exit":0,"expected_rows":{"gitfile/a":"clean","gitfile/b":"error","gitfile/c":"clean","include-root/b12-include-root":"error"},"observed_exit":0,"observed_rows":{"b12-include-root":"error"},"problems":[]}
SUMMARY	total=12	failed=0
```
Fixture wall time: 128.43s.

Synthetic census timing (new isolated Git repositories under `/var/tmp/souji-r18-CensusWatchdog`; each census was started in a new session and its temporary tree removed afterward):

```text
repos=20 exit=0 rows=20 error_rows=0 wall_ms=3046
repos=200 exit=0 rows=200 error_rows=0 wall_ms=30188
```

This is one post-fix sample, not a median. For comparison only, the parent-reported earlier 200-repo medians were 22.464s at the original base and 42.264s at the 5efb candidate; the one-shot 30.188s result is not statistically comparable, and the per-repo watchdog still has measurable overhead.

## Deliverables and limits

- Patch: `.ufo/waves/round-18/w1/CensusWatchdogFix.patch` (36,615 bytes; SHA-256 `be8d7bca94e713d3890f6e93f4ffbf39aee0da307cb18c7e3ed61bc5fbebed1b`). It is the `git diff 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tools/souji-census.sh` output.
- Diff summary: `tools/souji-census.sh | 682 ...`; one file changed, 556 insertions and 126 deletions.
- **Risk:** Linux cannot forcibly reap an uninterruptible D-state process; the implementation bounds its wait and emits `repo-timeout-unreaped`. A target that deliberately escapes the assigned process group/session is also outside the watchdog’s group-kill boundary. The required fixture suite did not leave residue in its tested cases.
- No tools were installed or updated. The mounted toolset exposes no LSP interface.
