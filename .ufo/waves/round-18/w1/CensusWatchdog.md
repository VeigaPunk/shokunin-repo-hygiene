STATUS: DONE — Added bounded per-candidate guards and per-repository census watchdogs.

## Axes
- **Operability (primary):** a blocked Git/metadata operation is isolated and bounded; healthy repositories continue.
- **Coverage and calibration (supporting):** pre-census metadata guards are bounded too, and protected refusals retain exit 2.

## Implementation and evidence
- `tools/souji-census.sh:15-17,63-65,157-175,245-258,2584-2617` documents and parses `--repo-timeout N` / `SOUJI_CENSUS_REPO_TIMEOUT`, default 600, integer range 1..86400, with invalid values exiting 2.
- `tools/souji-census.sh:1386-1456,1653-1717` keeps parent discovery to metadata classification and runs candidate path, gitfile, symlink, and repository guards in bounded worker groups before any census Git commands. Exit-2 refusals abort the full run; soft guard outcomes remain compatible.
- `tools/souji-census.sh:1470-1651` launches each guard/census worker with stdout and stderr in private files under `CENSUS_TMP`. Job control is enabled only for the worker fork; a separate `setsid` watchdog is redirected to `/dev/null`, writes a `timed_out` sentinel before SIGTERM, sends SIGKILL two seconds later, and is stopped/reaped on normal completion. Parent-side state polling bounds post-KILL reaping; an unreaped survivor emits `souji-census: repo-timeout-unreaped <repo>`.
- `tools/souji-census.sh:1663-1717` replays child stderr, checks rc 2 before timeout attribution, emits sanitized timeout diagnostics and the exact placeholder row, and preserves measurement of neighbors. `tools/souji-census.sh:1817-1823` keeps compare-mode output and per-repo files within the existing temp cleanup lifecycle.
- `tools/souji-census.sh:1925-1926,2323-2469,2471-2559` fixes selftest children to the 600-second default and adds the status/FIFO race, exact row/diagnostic, wall-time, no-reader, blocked-Git-PID-gone, slow-Git, protected-refusal, and invalid-timeout checks.

## Verification
All commands below ran in the scoped clone at `/var/tmp/souji-r18-CensusWatchdog/lane`; no tools were installed.

- `bash -n tools/souji-census.sh` — exit 0; no stdout/stderr.
- `shellcheck -S warning tools/souji-census.sh` — exit 0; no stdout/stderr.
- `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` — exit 0; 62 checks, 0 failed; measured total wall time 31.51 s. Exact emitted output:

```text
PASS repeat: two runs byte-identical
PASS header matches contract
PASS row count 4 (main repos only)
PASS plain-dir skipped
PASS dot-dir skipped
PASS linked worktree not a separate row
PASS clean-shokunin verdict=clean (clean)
PASS clean worktrees=1
PASS clean unpushed=0
PASS clean dirty=0
PASS dirty count=2 (untracked file + collapsed .scratch/)
PASS dirty scratch_bytes=48 (>0)
PASS dirty flags include dirty,scratch,secret-shaped (dirty,scratch,secret-shaped)
PASS unpushed count=1
PASS unpushed worktrees=3
PASS unpushed flag present (unpushed,wt-absent,wt-dirty)
PASS wt-dirty flag present (unpushed,wt-absent,wt-dirty)
PASS wt-absent flag present (unpushed,wt-absent,wt-dirty)
PASS noremote flag present (unpushed,no-remote)
PASS noremote unpushed=1 (>=1, unverifiable but counted)
PASS secret file contents absent from census
PASS forbidden surface contents absent
PASS mtime_iso shape (2026-10-20T17:24:50-03:00)
PASS mtime ignores future .ufo/state and .ufo/watchdog.log
PASS compare identical: exit 0, header only
PASS blank-after-header compares clean (exit 0, header only)
PASS compare mutation: exit 3
PASS compare reports scratch_bytes
PASS compare reports dirty delta
PASS bad compare baseline exits 2
PASS empty compare baseline exits 2
PASS blank-lead compare baseline exits 2
PASS blank-before-header compare baseline exits 2
PASS unknown flag exits 2
PASS protected root refused before access (exit 2, path-protected)
PASS protected compare alias refused (exit 2, path-protected)
PASS hygiene fleet: exit 0 (per-repo degrade)
PASS showUntrackedFiles=no: dirty=2 (no false clean)
PASS showUntrackedFiles=no: dirty flag present (dirty)
PASS hardlinked info/attributes: error row
PASS hardlinked info/attributes: dirty placeholder 0
PASS hardlinked info/attributes: stderr finding + path
PASS git-metadata-unsupported printed once per repo (2)
PASS FIFO info/attributes: error row (no hang)
PASS FIFO info/attributes: stderr finding + path
PASS hygiene neighbour unaffected (clean)
PASS hardlinked config still refuses whole run (exit 2)
PASS watchdog FIFO race exits 0
PASS watchdog timeout emits the exact error placeholder row
PASS watchdog timeout diagnostic exact
PASS watchdog neighbour neighbour-a measured normally
PASS watchdog neighbour neighbour-b measured normally
PASS watchdog wall time 3603ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18317ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.l7u7HE)
selftest: 62 checks, 0 failed
```

- Synthetic-root census command:

```sh
start=$(date +%s%N)
env -u GIT_DIR SOUJI_CENSUS_REPO_TIMEOUT=10 bash tools/souji-census.sh --root /var/tmp/souji-r18-CensusWatchdog/synthetic-root > /var/tmp/souji-r18-CensusWatchdog/synthetic.tsv 2> /var/tmp/souji-r18-CensusWatchdog/synthetic.err
finish=$(date +%s%N)
printf 'elapsed_ms=%s\n' "$(((finish-start)/1000000))"
printf '%s\n' '--- stdout ---'
cat /var/tmp/souji-r18-CensusWatchdog/synthetic.tsv
printf '%s\n' '--- stderr ---'
cat /var/tmp/souji-r18-CensusWatchdog/synthetic.err
```

  Output:

```text
elapsed_ms=261
--- stdout ---
repo	worktrees	unpushed	dirty	scratch_bytes	mtime_iso	verdict_flags
/var/tmp/souji-r18-CensusWatchdog/synthetic-root/healthy-shokunin	1	0	0	0	2026-10-20T17:04:52-03:00	clean
--- stderr ---
```

- Baseline selftest count: 49 (assignment context). Final count: 62 (+13).
- Retained timing: status/FIFO timeout 3,603 ms with a 1-second bound (requirement <6,000 ms); slow shim measured 9 Git calls at 18,317 ms under a 30-second bound; synthetic-root census 261 ms.
- `git diff --stat b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-census.sh` — `1 file changed, 592 insertions(+), 39 deletions(-)`; numstat `592 39 tools/souji-census.sh`; changed path only `tools/souji-census.sh`.

## Discarded falsifier and risk
An exploratory stat-shim that swapped `.git/config` after stat returned `rc=2` in 370 ms, so it did not reproduce a blocking preflight read; that fixture was removed rather than retained as a passing timeout test. The preflight guard path is still bounded by the same watchdog. An actual uninterruptible D-state survivor was not induced; it is reported and bounded in code but not dynamically exercised. The implementation now requires util-linux `setsid` and Linux `/proc`, both available in the exercised environment.

## Verdict
**Holds** for the exercised FIFO/status timeout, neighbor continuity, exact error row and diagnostic, no job-control warning, no leftover Git PID/reader, slow-Git non-timeout, protected exit-2, invalid-timeout exit-2, and synthetic-root census. No blocker remains. Patch: `.ufo/waves/round-18/w1/CensusWatchdog.patch`.
