STATUS: DONE — isolated all three timed fixture subprocesses and delivered the scoped patch

# Scope and behavior

Changed only `tests/fixtures/r14-census-boundary.py` in `/var/tmp/souji-r18-FixtureReapR14/lane`. Added `run_isolated`: each child starts with `start_new_session=True`; on timeout it scans `/proc/<pid>/stat` for session-ID field 6 equal to the child leader PID, SIGKILLs every matching PID (including nested process groups), then sends SIGKILL to the leader process group and reaps with `communicate()`. The setup-Git call (60s), strace probe (20s), and census runner (90s) all use it. Existing timeout handling/results and fixture assertions are unchanged.

Patch delivered at `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/FixtureReapR14.patch`.

# Retained evidence

Extracted the two requested census versions into `/var/tmp/souji-r18-FixtureReapR14/`:

```text
git -C /var/tmp/souji-r18-FixtureReapR14/lane show cc21683:tools/souji-census.sh > /var/tmp/souji-r18-FixtureReapR14/census-r14-harm.sh
git -C /var/tmp/souji-r18-FixtureReapR14/lane show a31642d:tools/souji-census.sh > /var/tmp/souji-r18-FixtureReapR14/census-pre-harm.sh
sha256sum /var/tmp/souji-r18-FixtureReapR14/census-r14-harm.sh /var/tmp/souji-r18-FixtureReapR14/census-pre-harm.sh
fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9  /var/tmp/souji-r18-FixtureReapR14/census-r14-harm.sh
6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026  /var/tmp/souji-r18-FixtureReapR14/census-pre-harm.sh
```

For the before revision, extracted `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tests/fixtures/r14-census-boundary.py` to `/var/tmp/souji-r18-FixtureReapR14/r14-fixture-before.py`; its SHA-256 was `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`.

Full fixture pair against `cc21683` was run sequentially, with job control enabled so the main fixture had a measurable private process group:

```text
set -m; python3 /var/tmp/souji-r18-FixtureReapR14/r14-fixture-before.py --tool /var/tmp/souji-r18-FixtureReapR14/census-r14-harm.sh > /var/tmp/souji-r18-FixtureReapR14/sequential-before-harm.log 2>&1 & first_pid=$!; first_pgid=$(ps -o pgid= -p "$first_pid"); first_pgid=${first_pgid//[[:space:]]/}; wait "$first_pid"; first_rc=$?; first_left=$(ps -o pid= -g "$first_pgid" | wc -l); python3 /var/tmp/souji-r18-FixtureReapR14/lane/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r18-FixtureReapR14/census-r14-harm.sh > /var/tmp/souji-r18-FixtureReapR14/sequential-after-harm.log 2>&1 & second_pid=$!; second_pgid=$(ps -o pgid= -p "$second_pid"); second_pgid=${second_pgid//[[:space:]]/}; wait "$second_pid"; second_rc=$?; second_left=$(ps -o pid= -g "$second_pgid" | wc -l); printf 'before_rc=%s before_pgid=%s before_leftovers=%s after_rc=%s after_pgid=%s after_leftovers=%s\n' "$first_rc" "$first_pgid" "$first_left" "$second_rc" "$second_pgid" "$second_left"
before_rc=0 before_pgid=959502 before_leftovers=0 after_rc=0 after_pgid=978350 after_leftovers=0
```

Both logs ended `SUMMARY total=12 failed=0`. Thus the measured R14-harm fixture process-group residue was **0 before → 0 after**; this fixture run did not itself hit a timeout.

Against the pre-harm `a31642d` census, the old and updated full fixtures were both run with a measured job-control process group. Exact command form and observed output:

```text
set -m; python3 /var/tmp/souji-r18-FixtureReapR14/r14-fixture-before.py --tool /var/tmp/souji-r18-FixtureReapR14/census-pre-harm.sh > /var/tmp/souji-r18-FixtureReapR14/control-before-pre-harm.log 2>&1 & fixture_pid=$!; pgid=$(ps -o pgid= -p "$fixture_pid"); pgid=${pgid//[[:space:]]/}; wait "$fixture_pid"; fixture_rc=$?; leftovers=$(ps -o pid= -g "$pgid" | wc -l); printf 'fixture_rc=%s pgid=%s leftovers=%s\n' "$fixture_rc" "$pgid" "$leftovers"
fixture_rc=1 pgid=828156 leftovers=0

set -m; python3 /var/tmp/souji-r18-FixtureReapR14/lane/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r18-FixtureReapR14/census-pre-harm.sh > /var/tmp/souji-r18-FixtureReapR14/control-after-pre-harm.log 2>&1 & fixture_pid=$!; pgid=$(ps -o pgid= -p "$fixture_pid"); pgid=${pgid//[[:space:]]/}; wait "$fixture_pid"; fixture_rc=$?; leftovers=$(ps -o pid= -g "$pgid" | wc -l); printf 'fixture_rc=%s pgid=%s leftovers=%s\n' "$fixture_rc" "$pgid" "$leftovers"
fixture_rc=1 pgid=828158 leftovers=0
```

Both logs ended `SUMMARY total=12 failed=10`, the expected historical baseline refusal/access failures. The process-group residue remained 0→0 and the assertions/results were unchanged.

# Hang-path evidence and limitation

The local R14 fixture has no FIFO setup and did not trigger its `TimeoutExpired` branch; therefore session-wide timeout cleanup was not dynamically exercised here. The reason to retain this defensive fix is the same measured subprocess leak pattern in the adjacent census fixtures: `ScoutPyTimeoutLeak.md:20,31-36,45` records the R14 call as the same unisolated `strace -f` → census chain (0/58 only because R14 has no FIFO), and traces 44/58 actual orphaned processes to the analogous R15 timed census call, where `git` blocked opening a FIFO after Python killed only the direct `strace` child. This is cross-fixture evidence, not a claim that an R14-local leak was reproduced.

One concurrent initial comparison showed a single `R14C2-09` failure (`exit=2`) for the old fixture; the old fixture’s isolated `R14C2-09` run and subsequent sequential full old/new runs both passed. Cause of that one-off result is undetermined; the sequential comparison above is the retained parity result.

None of my recorded fixture outputs showed an unexpected kill or timeout; the sequential R14-harm runs returned 0 and the pre-harm runs returned 1 with the historical 10 failures. Recorded top-level process groups all had zero leftovers. I did not capture every descendant PID, so I cannot attribute the sibling-reported PIDs 842962/842978/842979/842981; those PIDs were not among my recorded top-level group IDs.

L1’s follow-up requested a session-wide sweep because C1 may create per-repository groups with `set -m`; `kill_session` now signals all processes whose `/proc/<pid>/stat` session field matches the private child session before the leader-group kill and reap. The cited scout report documents that boundary. No FIFO unblocker was added because this assigned R14 fixture creates no FIFO and its expectations remain unchanged.

Verdict: **HOLDS** for the requested session isolation, session-wide timeout cleanup, and process-group kill by implementation. Normal-path before/after fixture results and residue were unchanged; timeout cleanup remains dynamically unexercised by the current R14 cases.