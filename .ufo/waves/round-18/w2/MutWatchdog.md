STATUS: DONE — Six isolated watchdog mutants probed: 2 killed, 4 survived; all pristine/restored controls passed and exact source bytes were restored before scratch deletion.

# MutWatchdog — round 18, wave 2

## Attacked claim and axes

C1 test sensitivity at pinned commit `5efb519f00075d958c3d1109ef6fcb24c487eb87`: do the required selftest and B1–B8 fixture expose the six specified watchdog/list-phase defects?

- **Operability (assigned):** bounded process-group cleanup, timeout classification, refusal precedence, and list-phase liveness.
- **Coverage (diagnostic only):** which requested mutants the existing detectors kill.
- **Calibration:** a surviving mutant is reported as a detector limitation, not a production failure or permission to weaken C1.

Scoped detector verdict: **partial sensitivity — 2/6 killed, 4/6 survived, 0 inconclusive**. This is not an integration/round verdict or a judgment that production C1 fails.

## Isolation, controls, and commands

Only the private clone source was mutated, one mutant at a time. No lane source, sibling source, fixture bytes, live fleet, operator sweep, credentials, network writes, jj command, or git write outside the clone was used. The two independent required detectors ran concurrently within each byte state; byte states never overlapped. No subagent or other agent runtime was invoked.

Clone setup (completed without output):
```sh
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-MutWatchdog/lane && git -C /var/tmp/souji-r18w2-MutWatchdog/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
git -C /var/tmp/souji-r18w2-MutWatchdog/lane rev-parse HEAD
```
Observed HEAD: `5efb519f00075d958c3d1109ef6fcb24c487eb87`.

The pinned selftest hardcodes `/var/tmp/souji-census-selftest.*` (`tools/souji-census.sh:1920`); the pinned fixture hardcodes `/var/tmp/souji-r18-FixtureR18Bounded` (`tests/fixtures/r18-census-bounded.py:35,111–112`). Parent explicitly authorized the bwrap mapping. Each detector therefore received a private mount/PID/network namespace with this seat directory mapped onto sandbox `/var/tmp`. Actual host writes stayed below `/var/tmp/souji-r18w2-MutWatchdog/`. PID namespaces were separate for the two detectors. Shared fixture scratch from other seats was inaccessible, so no shared-SEAT_TMP contamination was observed. Home was an empty tmpfs to avoid host configuration/credential reads.

The following are the exact successful detector commands, with host cwd `/var/tmp/souji-r18w2-MutWatchdog/lane`; `S` and `F` below refer to them:
```sh
# S — unchanged requested selftest, TMPDIR=/var/tmp in sandbox
/usr/bin/bwrap --unshare-pid --unshare-net --die-with-parent --ro-bind / / --bind /var/tmp/souji-r18w2-MutWatchdog /var/tmp --tmpfs /tmp --tmpfs /home/vgpnk --proc /proc --dev /dev --chdir /var/tmp/lane --setenv TMPDIR /var/tmp bash tools/souji-census.sh --selftest
# F — unchanged requested full B1–B8 fixture
/usr/bin/bwrap --unshare-pid --unshare-net --die-with-parent --ro-bind / / --bind /var/tmp/souji-r18w2-MutWatchdog /var/tmp --tmpfs /tmp --tmpfs /home/vgpnk --proc /proc --dev /dev --chdir /var/tmp/lane python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh
```

A Python subprocess controller captured stdout/stderr and recorded each started bwrap PID. `communicate` deadlines were 180 s for S and 700 s for F; F itself bounds each census invocation to 40 s (`tests/fixtures/r18-census-bounded.py:33,530–569`). No outer deadline fired. bwrap PID namespaces constrain even mutant descendants to this seat; namespace teardown cannot signal another seat. Initial attempts to submit the same commands through async bash were rejected before execution with `Background job limit reached (100)`. They are not baseline failures and are not counted among the 26 completed detector runs.

The initial pristine S/F pair passed. After every mutant, original bytes were written back from the pinned git-show snapshot in a `finally` block, SHA-256 was checked, and the same complete S/F pair passed. The preceding restored state is the pristine control for the next mutant. No baseline failure was scored as a kill.

## Mutation results

| Mutant | Pinned source lines in tools/souji-census.sh | Selftest exit / failed checks | Fixture exit / failed cases | Verdict / killed by |
|---|---|---|---|---|
| M1-leader-only | 1470 / 1495,1497 | 1 / 2 | 1 / B1, B2, B3, B4, B8 | **KILLED** — B1, B2, B3, B4, B8; selftest wall-time and FIFO-reader checks |
| M2-no-SIGKILL | 1497 | 0 / 0 | 0 / none | **SURVIVED** — none |
| M3-signal-rc-classifier | 1539 | 0 / 0 | 0 / none | **SURVIVED** — none |
| M4-no-rc2-priority | 1645–1648 | 0 / 0 | 0 / none | **SURVIVED** — none |
| M5-unbounded-list-phase | 1670–1671 | 0 / 0 | 1 / B8 | **KILLED** — B8 only; selftest survived |
| M6-inherited-watchdog-stdio | 1500–1501 | 0 / 0 | 0 / none | **SURVIVED** — none |

### Exact edits and expected detectors

- **M1-leader-only**, `tools/souji-census.sh:1470 / 1495,1497`: Signal only the leader: replace both watchdog TERM/KILL targets "-$pgid" with "$pgid".
- **M2-no-SIGKILL**, `tools/souji-census.sh:1497`: Delete the watchdog SIGKILL escalation; retain the killed marker.
- **M3-signal-rc-classifier**, `tools/souji-census.sh:1539`: Replace the timed_out marker predicate with [ "$rc" = 143 ] || [ "$rc" = 137 ]. The earlier marker-directory arbitration is otherwise unchanged.
- **M4-no-rc2-priority**, `tools/souji-census.sh:1645–1648`: Delete the rc=2-first return block immediately before the timeout return. emit_census caller checks are unchanged.
- **M5-unbounded-list-phase**, `tools/souji-census.sh:1670–1671`: Call guard_repo_candidate directly instead of through run_repo_with_watchdog in the list phase.
- **M6-inherited-watchdog-stdio**, `tools/souji-census.sh:1500–1501`: Remove >/dev/null 2>&1 from the watchdog launch.

1. **M1 leader-only:** expected sensitivity is the existing process/FIFO cleanup checks plus the <6000 ms selftest timeout bound (`tools/souji-census.sh:2433–2469`), and B1/B2/B3/B4/B8 resource checks (`tests/fixtures/r18-census-bounded.py:814–1008,1069–1104`). Actual selftest: `FAIL watchdog wall time 9849ms (want < 6000ms)` and `FAIL timed-out FIFO nonblocking open did not return ENXIO (rc=2)`. Each failed fixture case reported processes surviving census completion before fixture cleanup. Expected rows/exit alone still passed, showing the cleanup assertions matter. B6 subsequently passed after fixture cleanup; it is not incorrectly credited as a kill.

2. **M2 no escalation — concrete coverage gap:** the required detectors both passed when the sole normal-path watchdog `kill -KILL` at line 1497 was absent. The watchdog still announces its `killed` marker at line 1498; fallback KILL at lines 1546–1548 is conditional on that marker being absent. The existing FIFO injections therefore do not establish sensitivity to a missing normal-path KILL. [INFERENCE] Smallest test improvement: one bounded target descendant that ignores TERM, records its PID, and remains blocked until KILL; assert its death/FIFO ENXIO and absence from its private session before fixture cleanup. Do not change the timeout contract.

3. **M3 signal-status classifier — coverage gap:** both detectors passed after marker-based timeout classification at line 1539 was replaced by rc 143/137. This mutation deliberately retains the earlier state-directory arbitration; it attacks the actual marker predicate, not a new unconditional classifier. [INFERENCE] Current runs do not distinguish a marked timeout whose worker has a different exit status; in particular the implementation can synthesize rc 124 when it cannot reap the worker (`tools/souji-census.sh:1510–1524`). Smallest test improvement: exercise a marked timeout with a non-143/137 worker outcome while still requiring the exact error row and timeout diagnostic. This inference is not a new runtime probe.

4. **M4 lost rc-2 precedence — coverage gap:** both detectors passed without the rc=2-before-timeout block (`tools/souji-census.sh:1645–1649`). The selftest refusal is a fast in-census refusal (`tools/souji-census.sh:2511–2540`); B7 is a protected-root refusal (`tests/fixtures/r18-census-bounded.py:1059–1067`). Neither passing result proves the deadline/refusal overlap. [INFERENCE] Smallest test improvement: a deterministic bounded race/handshake where the timeout marker is established but the worker exits 2 for a protected-path refusal; demand exit 2, not a timeout placeholder.

5. **M5 unbounded preflight:** B8 killed the mutant (`tests/fixtures/r18-census-bounded.py:1069–1104`), while all 62 selftest checks passed. Actual B8 output included `"observed_exit":124`, `"fixture timeout rc 124 is FAIL, never SKIP"`, missing rows/header, and missing exact repo-timeout diagnostic. This is the fixture deadline, not the required graceful repo timeout. B1–B7 passed. B8 provides distinct list-phase coverage not supplied by the built-in selftest.

6. **M6 inherited watchdog stdio — survivor, non-equivalence not demonstrated:** both detectors passed without the launch redirection (`tools/souji-census.sh:1500–1501`). The allowed probes supplied no watchdog output or descriptor-lifetime failure, so this receipt does not prove a production defect; it may be behaviorally equivalent for these inputs. [INFERENCE] If descriptor/output isolation is intended as a tested invariant, the smallest discriminating test is a controlled watchdog-only stdout/stderr sentinel (e.g. a deterministic test shim), checked absent from both captured channels, plus bounded pipe closure. Otherwise do not count this survivor as demonstrated non-equivalent missing coverage.

No proposed test improvement was implemented or run; the assignment stops after these six mutation probes. No production fix was made.

## Hashes and restoration evidence

All pristine-before and restored-after source hashes (`P`) are `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`.
Pinned and final fixture hash (unchanged): `2249616641f4a1b9427f8c667b8c67d47e3320e551504b4ac5d8d3a5c87d5bc1`.

| Mutant | Before | Mutated SHA-256 | Restored after | Restored S/F |
|---|---|---|---|---|
| M1 | P | `6b493f76d1b5e6a57f3fc76f0d1275cadc45bfea81b5258d2cb0e14457034d81` | P (exact) | 0/0; 62/0 checks, 8/0 cases |
| M2 | P | `88ddddf21de06ba0def23a14c705def9c2229f30d3fe0f5ee62dc3c9cb3a7fa5` | P (exact) | 0/0; 62/0 checks, 8/0 cases |
| M3 | P | `97f121fe1d581e5d2119f8e6729cef36d110701076596c7245add39cf70b64c6` | P (exact) | 0/0; 62/0 checks, 8/0 cases |
| M4 | P | `7500636c9d5f467d31fa8b803b842e9b2d87f1853b40952a9931fc1847a76d98` | P (exact) | 0/0; 62/0 checks, 8/0 cases |
| M5 | P | `641bbd8162919b06300131e837a7212782fbceba5b438e4f5c37d95187258042` | P (exact) | 0/0; 62/0 checks, 8/0 cases |
| M6 | P | `5489d0fdefed22e4bf49323f58a387b526571aed22e9929489169bcf7734fbd2` | P (exact) | 0/0; 62/0 checks, 8/0 cases |

Observed initial and final command/output:
```text
sha256sum /var/tmp/souji-r18w2-MutWatchdog/lane/tools/souji-census.sh /var/tmp/souji-r18w2-MutWatchdog/lane/tests/fixtures/r18-census-bounded.py
7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd  /var/tmp/souji-r18w2-MutWatchdog/lane/tools/souji-census.sh
2249616641f4a1b9427f8c667b8c67d47e3320e551504b4ac5d8d3a5c87d5bc1  /var/tmp/souji-r18w2-MutWatchdog/lane/tests/fixtures/r18-census-bounded.py
```

After the final restored pair and final digest capture, scratch cleanup completed without output:
```sh
rm -rf -- /var/tmp/souji-r18w2-MutWatchdog
```

This deleted the clone and its isolated test scratch. All bwrap commands had returned before deletion. The sole durable lane write is this report.

## Tooling and limitations

- Existing `/usr/bin/bwrap --version` returned `bubblewrap 0.13.1`. No tool was installed or updated; no pacman transaction/service restart occurred.
- These are controlled private PID/mount-namespace tests, not a live-fleet operability or host-zombie-reaping claim. Empty private home/tmp and namespace-init cleanup are deliberate confinement boundaries. Kill attribution is paired against passing controls in that same environment.
- Source citations use original pinned line numbers. Later edits by other seats are outside this report; the detector fixture was not changed to their newer work.

## Complete captured detector output

Each receipt below identifies its exact command as S or F above, started host bwrap PID, source hash, observed process exit, wall time, and whether the outer controller deadline fired. stdout/stderr are the actual captured strings; `(empty)` denotes zero captured bytes in that channel.

### pristine — selftest

Command S; host PID `590925`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `35.995 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:18:52-03:00)
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
PASS watchdog wall time 3819ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18326ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.Qk9pv5)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### pristine — fixture

Command F; host PID `590928`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `75.875 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### M1-leader-only — selftest

Command S; host PID `2155686`; SHA-256 `6b493f76d1b5e6a57f3fc76f0d1275cadc45bfea81b5258d2cb0e14457034d81`; exit `1`; wall `41.18 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:20:50-03:00)
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
FAIL watchdog wall time 9849ms (want < 6000ms)
PASS watchdog stderr has no job-control warning
FAIL timed-out FIFO nonblocking open did not return ENXIO (rc=2)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18400ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.VZqYWe)
selftest: 62 checks, 2 failed
```
stderr:
```text
(empty)
```

### M1-leader-only — fixture

Command F; host PID `2155687`; SHA-256 `6b493f76d1b5e6a57f3fc76f0d1275cadc45bfea81b5258d2cb0e14457034d81`; exit `1`; wall `105.145 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=6b493f76d1b5e6a57f3fc76f0d1275cadc45bfea81b5258d2cb0e14457034d81
CASE	B1	FAIL	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":["processes survived census completion before fixture cleanup: [{'pid': 2652, 'state': 'S', 'ppid': 1, 'pgid': 2504, 'session': 1621}, {'pid': 2794, 'state': 'S', 'ppid': 2652, 'pgid': 2504, 'session': 1621}, {'pid': 2795, 'state': 'S', 'ppid': 2794, 'pgid': 2504, 'session': 1621}]"]}
CASE	B2	FAIL	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":["processes survived census completion before fixture cleanup: [{'pid': 5993, 'state': 'S', 'ppid': 1, 'pgid': 5845, 'session': 4962}, {'pid': 6135, 'state': 'S', 'ppid': 5993, 'pgid': 5845, 'session': 4962}, {'pid': 6137, 'state': 'S', 'ppid': 6135, 'pgid': 5845, 'session': 4962}]"]}
CASE	B3	FAIL	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":["processes survived census completion before fixture cleanup: [{'pid': 9324, 'state': 'S', 'ppid': 1, 'pgid': 9176, 'session': 8293}, {'pid': 9466, 'state': 'S', 'ppid': 9324, 'pgid': 9176, 'session': 8293}, {'pid': 9467, 'state': 'S', 'ppid': 9466, 'pgid': 9176, 'session': 8293}]"]}
CASE	B4	FAIL	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":["processes survived census completion before fixture cleanup: [{'pid': 15308, 'state': 'S', 'ppid': 1, 'pgid': 15017, 'session': 13243}, {'pid': 15587, 'state': 'S', 'ppid': 15308, 'pgid': 15017, 'session': 13243}, {'pid': 15588, 'state': 'S', 'ppid': 15587, 'pgid': 15017, 'session': 13243}]","processes survived census completion before fixture cleanup: [{'pid': 15295, 'state': 'S', 'ppid': 1, 'pgid': 15004, 'session': 13244}, {'pid': 15580, 'state': 'S', 'ppid': 15295, 'pgid': 15004, 'session': 13244}, {'pid': 15581, 'state': 'S', 'ppid': 15580, 'pgid': 15004, 'session': 13244}]"]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	FAIL	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":["processes survived census completion before fixture cleanup: [{'pid': 19675, 'state': 'S', 'ppid': 1, 'pgid': 19589, 'session': 19261}]"]}
SUMMARY	total=8	failed=5
```
stderr:
```text
(empty)
```

### restored-M1 — selftest

Command S; host PID `3272830`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `34.114 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:22:44-03:00)
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
PASS watchdog wall time 3806ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18296ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.yKCQaO)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### restored-M1 — fixture

Command F; host PID `3272832`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `74.402 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### M2-no-SIGKILL — selftest

Command S; host PID `3937032`; SHA-256 `88ddddf21de06ba0def23a14c705def9c2229f30d3fe0f5ee62dc3c9cb3a7fa5`; exit `0`; wall `31.796 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:24:04-03:00)
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
PASS watchdog wall time 3580ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18273ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.dPhqzS)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### M2-no-SIGKILL — fixture

Command F; host PID `3937033`; SHA-256 `88ddddf21de06ba0def23a14c705def9c2229f30d3fe0f5ee62dc3c9cb3a7fa5`; exit `0`; wall `72.119 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=88ddddf21de06ba0def23a14c705def9c2229f30d3fe0f5ee62dc3c9cb3a7fa5
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### restored-M2 — selftest

Command S; host PID `4181784`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `30.828 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:25:16-03:00)
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
PASS watchdog wall time 3576ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18253ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.h3vQIQ)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### restored-M2 — fixture

Command F; host PID `4181785`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `71.386 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### M3-signal-rc-classifier — selftest

Command S; host PID `236690`; SHA-256 `97f121fe1d581e5d2119f8e6729cef36d110701076596c7245add39cf70b64c6`; exit `0`; wall `30.794 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:26:40-03:00)
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
PASS watchdog wall time 3577ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18256ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.9Iv9QY)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### M3-signal-rc-classifier — fixture

Command F; host PID `236691`; SHA-256 `97f121fe1d581e5d2119f8e6729cef36d110701076596c7245add39cf70b64c6`; exit `0`; wall `71.28 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=97f121fe1d581e5d2119f8e6729cef36d110701076596c7245add39cf70b64c6
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### restored-M3 — selftest

Command S; host PID `399942`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `32.462 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:27:51-03:00)
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
PASS watchdog wall time 3795ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18273ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.aRsyKD)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### restored-M3 — fixture

Command F; host PID `399943`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `74.166 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### M4-no-rc2-priority — selftest

Command S; host PID `677636`; SHA-256 `7500636c9d5f467d31fa8b803b842e9b2d87f1853b40952a9931fc1847a76d98`; exit `0`; wall `32.506 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:29:18-03:00)
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
PASS watchdog wall time 3794ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18273ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.s7H5kK)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### M4-no-rc2-priority — fixture

Command F; host PID `677635`; SHA-256 `7500636c9d5f467d31fa8b803b842e9b2d87f1853b40952a9931fc1847a76d98`; exit `0`; wall `74.289 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7500636c9d5f467d31fa8b803b842e9b2d87f1853b40952a9931fc1847a76d98
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### restored-M4 — selftest

Command S; host PID `996975`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `33.154 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:30:33-03:00)
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
PASS watchdog wall time 3792ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18370ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.G7CN9p)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### restored-M4 — fixture

Command F; host PID `996976`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `74.318 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### M5-unbounded-list-phase — selftest

Command S; host PID `1361939`; SHA-256 `641bbd8162919b06300131e837a7212782fbceba5b438e4f5c37d95187258042`; exit `0`; wall `29.42 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:31:53-03:00)
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
PASS watchdog wall time 3559ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18296ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.V3zCW4)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### M5-unbounded-list-phase — fixture

Command F; host PID `1361938`; SHA-256 `641bbd8162919b06300131e837a7212782fbceba5b438e4f5c37d95187258042`; exit `1`; wall `103.352 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=641bbd8162919b06300131e837a7212782fbceba5b438e4f5c37d95187258042
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	FAIL	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":124,"observed_rows":{},"problems":["exit=124 expected 0","fixture timeout rc 124 is FAIL, never SKIP","census header missing","row names=[] expected ['a', 'b', 'c']","a: row missing; expected clean","b: row missing; expected error","c: row missing; expected clean","a: missing from no-shim control or injected run","c: missing from no-shim control or injected run","timeout diagnostic missing: 'souji-census: repo-timeout 8s /var/tmp/souji-r18-FixtureR18Bounded/fixture.l0c9prs0/b8-list-config-fifo/b'"]}
SUMMARY	total=8	failed=1
```
stderr:
```text
(empty)
```

### restored-M5 — selftest

Command S; host PID `1582725`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `32.262 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:33:37-03:00)
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
PASS watchdog wall time 3797ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18276ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.NZIsFj)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### restored-M5 — fixture

Command F; host PID `1582726`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `74.333 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### M6-inherited-watchdog-stdio — selftest

Command S; host PID `1887157`; SHA-256 `5489d0fdefed22e4bf49323f58a387b526571aed22e9929489169bcf7734fbd2`; exit `0`; wall `33.601 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:34:58-03:00)
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
PASS watchdog wall time 3803ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18286ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.90ou0K)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### M6-inherited-watchdog-stdio — fixture

Command F; host PID `1887156`; SHA-256 `5489d0fdefed22e4bf49323f58a387b526571aed22e9929489169bcf7734fbd2`; exit `0`; wall `74.43 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=5489d0fdefed22e4bf49323f58a387b526571aed22e9929489169bcf7734fbd2
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```

### restored-M6 — selftest

Command S; host PID `2139752`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `34.275 s`; outer deadline `false`.

stdout:
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
PASS mtime_iso shape (2026-10-20T18:36:13-03:00)
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
PASS watchdog wall time 3806ms (< 6000ms bound+5)
PASS watchdog stderr has no job-control warning
PASS timed-out FIFO has no reader (nonblocking open returns ENXIO)
PASS timed-out Git process is gone
PASS two-second Git calls measured normally (9 calls, 18292ms)
PASS slow-Git census did not time out
PASS census_one protected refusal remains exit 2
PASS invalid CLI and environment timeouts exit 2
PASS no forbidden git subcommand
PASS fixtures under mktemp (/var/tmp/souji-census-selftest.wnqGSk)
selftest: 62 checks, 0 failed
```
stderr:
```text
(empty)
```

### restored-M6 — fixture

Command F; host PID `2139751`; SHA-256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`; exit `0`; wall `74.182 s`; outer deadline `false`.

stdout:
```text
TOOL	/var/tmp/lane/tools/souji-census.sh	sha256=7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
CASE	B1	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B2	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B3	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B4	PASS	{"expected_exit":0,"expected_rows":{"attributes/a":"clean","attributes/b":"error","attributes/c":"clean","ignore/a":"clean","ignore/b":"error","ignore/c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
CASE	B5	PASS	{"expected_exit":0,"expected_rows":{"slow":"clean"},"observed_exit":0,"observed_rows":{"slow":"clean"},"problems":[]}
CASE	B6	PASS	{"expected_exit":0,"expected_rows":{},"observed_exit":"none","observed_rows":{},"problems":[]}
CASE	B7	PASS	{"expected_exit":2,"expected_rows":{},"observed_exit":2,"observed_rows":{},"problems":[]}
CASE	B8	PASS	{"expected_exit":0,"expected_rows":{"a":"clean","b":"error","c":"clean"},"observed_exit":0,"observed_rows":{"a":"clean","b":"error","c":"clean"},"problems":[]}
SUMMARY	total=8	failed=0
```
stderr:
```text
(empty)
```
