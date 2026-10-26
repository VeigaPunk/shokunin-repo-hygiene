# SwarmExecutor16 — r32 w1, C2 operability, items T23 T25

## Status
STATUS: PASS — both enumerated items now pass the frozen sandbox check at scratch commit `b31c89878f4ac8960219266337a6c186c9c3f839` (base `85b61a151923986e7e6b48f7084b9122561b5f3d`): `SUMMARY items=2 pass=2 fail=0 partial=1`, counter rc 0; the same two items FAIL at base under the same counter (red-before reproduced).

## Evidence

All commands run in the scratch clone `/fast/scratch/hyaku/souji-r32/C2Fix24/c` (`git clone --no-local` of the lane, `origin` removed, toplevel verified = that path before the first commit, throwaway identity set only with `git -C <scratch> config`), with `TMPDIR=/fast/scratch/hyaku/souji-r32/C2Fix24/tmp`. Nothing was written in the lane except this report and the three delivery files.

1. Counter at the patched revision (full output):
```
python3 -B .../census/round-32/c2-counter.py --root <scratch>/c --rev b31c89878f4ac8960219266337a6c186c9c3f839 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only T23,T25 --scratch <scratch>/cnt

ITEM	T23	PASS	base=rc0:W1217:cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED	sbox=rc0:W1218:cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
ITEM	T25	PASS	base=rc0:W27:cases=12 pass=12 control=FALSE-GREEN-REJECTED	sbox=rc0:W28:cases=12 pass=12 control=FALSE-GREEN-REJECTED
SUMMARY items=2 pass=2 fail=0 partial=1 rev=b31c89878f4ac8960219266337a6c186c9c3f839
COUNTER_RC=0
```

2. Red-before, same counter with `--rev 85b61a1… --base 85b61a1…` (do-nothing reading, both items):
```
ITEM	T23	FAIL	base=rc0:W1216:cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED	sbox=rc1:W0:cases=12 pass=0 control=FALSE-GREEN-ACCEPTED lost_found=NOT-DETECTED	regress work-dropped
ITEM	T25	FAIL	base=rc0:W27:cases=12 pass=12 control=FALSE-GREEN-REJECTED	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
SUMMARY items=2 pass=0 fail=2 partial=1 rev=85b61a151923986e7e6b48f7084b9122561b5f3d
COUNTER_RC=1
```
The failure mode at base is exactly the frozen defect: the fixture writes its scratch under a literal `/var/tmp` (unreachable in the sandbox) regardless of TMPDIR.

3. Each patched command run once with the caller's TMPDIR and once with TMPDIR unset (patched tree = delivered bytes):
```
T23  TMPDIR=<scratch>/tmp  python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py
     rc=0  last=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
T23  env -u TMPDIR         python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py
     rc=0  last=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
T25  TMPDIR=<scratch>/tmp  python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py
     rc=0  last=cases=12 pass=12 control=FALSE-GREEN-REJECTED
T25  env -u TMPDIR         python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py
     rc=0  last=cases=12 pass=12 control=FALSE-GREEN-REJECTED
```
All four runs wrote no stderr; the last line is byte-identical to the base run's last line for each item, so the counter's predicate (a) compares equal strings.

4. Delivery integrity: `sha256sum` of each delivered file equals the file at the patched commit in the scratch clone.
```
eae7f0320d5b43f9778d4b8ad965f3f5642768918a3670527d87465203160395  r24-size-census.py (clone and delivery)
be6540992883b6bb0950fb3c6a81dfd0cb0c6f6b32cc88c5047d2e16c6af10e6  r26-axis-check.py (clone and delivery)
```

5. Tooling: no install or upgrade was needed. `bwrap` = `/usr/bin/bwrap`, `strace` = `/usr/bin/strace`, both pre-existing on PATH; no pacman transaction was attempted.

## Findings

1. `tests/fixtures/r24-size-census.py:30` — `SCRATCH_PARENT = '/var/tmp'` was the only hard-coded root; `scratch()` at `:107` already passed it as `dir=` to `tempfile.mkdtemp`, so deriving the constant from `tempfile.gettempdir()` (now `SCRATCH_PARENT = tempfile.gettempdir()`) makes all twelve cases honour the caller's TMPDIR with one line. The write-safety envelope is untouched: `case_detector` still calls `fsck --lost-found` inside the case and asserts `gitdir/lost-found/other/<oid>` appears, and the run still prints `lost_found=WRITE-DETECTED`; `case_dangling` still asserts the `lost-found` directory is absent. `Scratch.env` already copies the caller's environment (minus `GIT_*`) and pins `HOME` under the scratch root, so children inherit the caller's TMPDIR — no `/var/tmp` was injected there.
2. `tests/fixtures/r26-axis-check.py:47-48` — `SCRATCH_BASE`/`SCRATCH_PREFIX` were literal `/var/tmp/...`; now `SCRATCH_ROOT = tempfile.gettempdir()` with both paths `os.path.join`-ed from it, so the safety guard `SCRATCH_BASE.startswith(SCRATCH_PREFIX)` and the `islink`/`isdir` checks keep their meaning against the TMPDIR-rooted path (Rule: guards that matched `/var/tmp/<prefix>.*` match the TMPDIR path instead). The per-run world directory, the finally-block `rmtree`+`rmdir`, all 12 cases, the control arm and the exit code are unchanged; `import tempfile` added at `:46`.
3. Neither fixture-wrapped tool writes scratch: `grep -E 'var/tmp|/tmp|mkdtemp|TemporaryDirectory|mktemp'` over `tools/souji-size-census.py` and `tools/souji-axis-check.py` returns no matches, matching the item rows (T23/T25 list only the fixture file). No test-data string mentioning `/var/tmp` was altered (the r26 `R25C2_REPLICA` and `SCORECARD` literals are synthetic text; no code creates files there).
4. Docstrings now name TMPDIR instead of the literal (`r24-size-census.py:5`, `r26-axis-check.py:34`); no other output line, case name, count or exit code changed — confirmed by the identical base/sbox S lines in evidence 1.

## Risks
- Integration is the L1's: these bytes exist only as deliveries plus scratch commit `b31c898…`; the lane copies are still at base content.
- With TMPDIR unset both fixtures fall back to Python's default temp dir (`/tmp`), which is the caller's environment, not a hard-coded lane root; the C2 predicate only requires the caller's TMPDIR to be honoured when set.
- The `partial=1` marker in the SUMMARY is the counter's expected `--only` annotation, not a partial pass.

## Deliveries
- `.ufo/waves/round-32/w1/deliver-r24-size-census.py`
- `.ufo/waves/round-32/w1/deliver-r26-axis-check.py`
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor16.diff` (`git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- tests/fixtures/r24-size-census.py tests/fixtures/r26-axis-check.py`)
- `.ufo/waves/round-32/w1/SwarmExecutor16.md` (this report)
