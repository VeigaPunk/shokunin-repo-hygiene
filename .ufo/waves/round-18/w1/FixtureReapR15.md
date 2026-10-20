STATUS: DONE — R15 fixture timeouts now kill every process in the spawned session; the targeted FIFO repro went from 2 leaked processes to 0.

## Axes

Round axes: calibration 7, operability 8, coverage 8. This move improves operability; no change is claimed for calibration or coverage.

## Implementation

Changed only `tests/fixtures/r15-census-config.py` in the assigned clone.

At `tests/fixtures/r15-census-config.py:269-294`, `kill_session` reads `/proc/<pid>/stat` and selects every process whose session field (field 6) equals the `start_new_session=True` leader PID. It signals those PIDs with `SIGKILL` (leader first), then calls `killpg`; `run_in_session` at lines 297-311 calls `communicate()` to drain/reap and re-raises the original timeout. The former `subprocess.run` call sites now use the helper at lines 320 (`run_setup`), 780 (`probe_strace`), and 827 (`run_tool`). `EXPECTED_IDS`, case logic, timeout values, exit handling, and row assertions were not changed.

**Finding F1 — operability: holds.** The red pre-harm FIFO arm left its own census shell and Git child blocked; final session-wide cleanup left no process with its exact scratch-path prefix. Smallest fix: none beyond session-wide process cleanup.

## Retained evidence

Artifact extraction and identity:

```text
git -C /var/tmp/souji-r18-FixtureReapR15/lane show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tests/fixtures/r15-census-config.py > /var/tmp/souji-r18-FixtureReapR15/fixture-base.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh > /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh
sha256sum /var/tmp/souji-r18-FixtureReapR15/fixture-base.py /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py
```

Output:

```text
27474396808f33ead4c44747d202a8ca0193363651ef6d1adfa458172beffd25  /var/tmp/souji-r18-FixtureReapR15/fixture-base.py
6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026  /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh
57f8986772402872d58068bdcc622302a58683b8bf12e663dca8ad9bfb5d90bb  /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py
```

Baseline run (the selected case contains `r-inc-fifo`):

```text
python3 /var/tmp/souji-r18-FixtureReapR15/fixture-base.py --tool /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh --case R15CFG-03 > /var/tmp/souji-r18-FixtureReapR15/base.out 2> /var/tmp/souji-r18-FixtureReapR15/base.err; rc=$?; printf 'fixture_rc=%s\n' "$rc"
fixture_rc=1
```

Captured output identifies `TOOL-KIND pre-harm-a31642d`; `CASE R15CFG-03 FAIL` includes `r-inc-fifo: exit=124 want 0`; and `SUMMARY total=1 failed=1`. The case is intentionally red against this pre-harm census. Run elapsed 91.94 seconds.

The post-run `ps -eo pid=,args=` listing contained 46 processes across concurrent fixture runs. The two entries with this run's unique path `/var/tmp/r15-census-config.w5w_hag5` were:

```text
515827 bash /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh --root /var/tmp/r15-census-config.w5w_hag5/unsafe-repos/r-inc-fifo --include-root
515853 /usr/bin/git -C /var/tmp/r15-census-config.w5w_hag5/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree
```

Thus the baseline's own count was **2** (other concurrent processes were not attributed to this run). I reaped only those two PIDs with `kill -KILL 515827 515853`; the following `ps -p 515827,515853 -o pid=,stat=,args=` returned no rows (exit 1 because there were no matches).

Modified fixture run against the same extracted pre-harm census:

```text
python3 /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh --case R15CFG-03 > /var/tmp/souji-r18-FixtureReapR15/fixed.out 2> /var/tmp/souji-r18-FixtureReapR15/fixed.err; rc=$?; printf 'fixture_rc=%s\n' "$rc"
fixture_rc=1
```

It retains the pre-harm `R15CFG-03 FAIL` result; elapsed 90.69 seconds. For an exact post-run scratch prefix, a temporary `sitecustomize` recorder logged only the `tempfile.mkdtemp` result; the fixture bytes and census tool were unchanged. That run also returned `fixture_rc=1`, with `TOOL-KIND pre-harm-a31642d`, `CASE R15CFG-03 FAIL`, and `SUMMARY total=1 failed=1`. The exact scratch path was `/var/tmp/r15-census-config.515usna9`.

The scratch-prefix measurement repeated the modified run with a temporary `sitecustomize` recorder on `PYTHONPATH`:

```text
PYTHONPATH=/var/tmp/souji-r18-FixtureReapR15 python3 /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh --case R15CFG-03 > /var/tmp/souji-r18-FixtureReapR15/fixed-instrumented.out 2> /var/tmp/souji-r18-FixtureReapR15/fixed-instrumented.err; rc=$?; printf 'fixture_rc=%s\n' "$rc"
fixture_rc=1
```

Exact after-count command and output:

```text
target='/var/tmp/r15-census-config.515usna9'; count=0; while IFS= read -r line; do case "$line" in *"$target"*) count=$((count+1)); printf '%s\n' "$line";; esac; done < <(ps -eo pid=,args=); printf 'target=%s\nmatches=%d\n' "$target" "$count"
target=/var/tmp/r15-census-config.515usna9
matches=0
```


## L1 follow-up: session-wide cleanup

The initial process-group-only approach was insufficient for census children placed into another process group by job control. The final helper above enumerates the isolated session, kills every matching session member, then issues `killpg` and reaps.

Final targeted rerun against the extracted pre-harm census:

```text
PYTHONPATH=/var/tmp/souji-r18-FixtureReapR15 python3 /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r18-FixtureReapR15/souji-census-preharm.sh --case R15CFG-03 > /var/tmp/souji-r18-FixtureReapR15/fixed-session.out 2> /var/tmp/souji-r18-FixtureReapR15/fixed-session.err; rc=$?; printf 'fixture_rc=%s\n' "$rc"
fixture_rc=1
```

It remains intentionally red on the pre-harm tool (`TOOL-KIND pre-harm-a31642d`, `CASE R15CFG-03 FAIL`, `SUMMARY total=1 failed=1`). The recorded exact scratch path was `/var/tmp/r15-census-config.2v_r9ktj`.

```text
target='/var/tmp/r15-census-config.2v_r9ktj'; count=0; while IFS= read -r line; do case "$line" in *"$target"*) count=$((count+1)); printf '%s\n' "$line";; esac; done < <(ps -eo pid=,args=); printf 'target=%s\nmatches=%d\n' "$target" "$count"
target=/var/tmp/r15-census-config.2v_r9ktj
matches=0
```

Final modified fixture identity:

```text
sha256sum /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py
61208dbd53367fa85b6f2e6d10d521900a34e1f41a27962cfbb1559ea0189f08  /var/tmp/souji-r18-FixtureReapR15/lane/tests/fixtures/r15-census-config.py
```

## Limits and blockers

The explicit FIFO regression was run as `R15CFG-03`, not as the full 20-case fixture suite. No build, lint, formatter, or unrelated tests were run. LSP was not available in the mounted tool inventory; exact-file search found the three former subprocess call sites and no remaining `subprocess.run` call in this fixture. No tools were installed or updated.
