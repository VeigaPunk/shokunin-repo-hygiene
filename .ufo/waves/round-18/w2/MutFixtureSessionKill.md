STATUS: DONE — Authorized cross-PGID helper probe killed the leader-only mutant in both fixtures; original/restored arms passed.

# Attacked claim and axes

C1 operability, specifically the claim that the round-18 changes to `tests/fixtures/r15-census-config.py` and `tests/fixtures/r17-census-hygiene.py` kill every process in the census session on fixture timeout, including children in other process groups.

Axes: bounded fixture completion; live session residue; mutation discrimination; exact-byte restoration and scratch isolation. This is a mutation/coverage finding, not an overall C1 judgment or a production fix.

All source references below are at `5efb519f00075d958c3d1109ef6fcb24c487eb87`. Execution used only `/var/tmp/souji-r18w2-MutFixtureSessionKill/`; the lane received only this report. No subagents or other orchestration runtime were invoked.

# Mutant and expected detector

One plausible defect, applied at the smallest behavior-bearing point in each assigned fixture:

- `tests/fixtures/r15-census-config.py:308`: `kill_session(proc.pid)` → `os.killpg(proc.pid, signal.SIGKILL)`.
- `tests/fixtures/r17-census-hygiene.py:195`: the identical replacement.

The surrounding second `proc.communicate()` remained unchanged (`r15:309`, `r17:196`). The session-scanning helpers (`r15:269–294`, `r17:151–170`) remained present but were bypassed at these timeout callsites.

Expected discrimination: a blocked descendant whose PGID differs from the session leader should survive the mutant's single-group SIGKILL. The detector should observe either a fixture that fails to return within its bound or live session residue after it returns. Pristine and restored fixtures must pass that same detector before a mutant failure can be called a kill.

The fixed detector used a 150-second outer bound for r15 and 90 seconds for r17, unchanged across pristine/mutated/restored arms. Its pass predicate was bounded return plus zero **live** session members, not the census's functional CASE result. It separately counted zombies. A strict zero-process-including-zombies predicate would already fail the r15 pristine baseline and would therefore be inconclusive, not a killed mutant.

# Exact setup and execution

These commands completed with exit 0 and no stdout/stderr:

```sh
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-MutFixtureSessionKill/lane
git -C /var/tmp/souji-r18w2-MutFixtureSessionKill/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
```

The r15 stimulus was the exact stdout bytes of this read-only command, saved using the file-write tool as `/var/tmp/souji-r18w2-MutFixtureSessionKill/r15-census-a31642d.sh`:

```sh
git -C /var/tmp/souji-r18w2-MutFixtureSessionKill/lane show a31642d:tools/souji-census.sh
```

Observed: 30,197 bytes, SHA-256 `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`.

The r17 stimulus was a `/var/tmp` copy of the pinned census, `/var/tmp/souji-r18w2-MutFixtureSessionKill/r17-census-no-watchdog.sh`, with only:

1. `exit 0 # Mutation probe stimulus: disable only the watchdog, keep worker groups.` inserted after the watchdog's `state_path=$3` assignment (original census `tools/souji-census.sh:1485`). The existing `set -m` worker-group creation was retained.
2. The census temporary-directory prefix at original line 240 redirected from `/var/tmp/souji-census-now.XXXXXX` to `/var/tmp/souji-r18w2-MutFixtureSessionKill/census-now.XXXXXX`, solely for the assigned scratch containment.

Its fixed SHA-256 was `ec3d374a8df1e444021fad7ad54394228c13360fe21143e7a691570ed33a1d09`. The unmodified pinned census hash was `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`.

Detector `/var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py`, SHA-256 `88630a0471ce9f9131dcc73d4fb1a36d162142ef39a82467f9fda424dd110612`, ran the fixtures via `runpy.run_path(..., run_name='__main__')`. Instrumentation recorded actual `Popen` session leaders and `os.kill`/`os.killpg` calls, forwarded those calls unchanged, and redirected fixture `tempfile.mkdtemp(dir='/var/tmp')` beneath the arm's scratch directory. The detector was a child subreaper so orphaned dead descendants could be counted before being reaped, rather than left for host PID 1. It read `/proc/<pid>/stat` and `cmdline` only; it never read environ. Any cleanup SIGKILL required a recorded PID with matching starttime/session. No outer SIGKILL was needed in any arm.

Executed outer commands, with each r15/r17 pair launched concurrently through Python asyncio:

```sh
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py parent pristine r15
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py parent pristine r17
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py parent mutated r15
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py parent mutated r17
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py parent restored r15
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/probe.py parent restored r17
```

All six detector commands returned 0, reported `detector_pass: true`, `outer_timeout: false`, `fixture_return_event: true`, and `cleanup_remaining: []`.

Fixture argv used in each arm, executed by that wrapper, **not additional direct invocations**:

```text
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/lane/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r18w2-MutFixtureSessionKill/r15-census-a31642d.sh --case R15CFG-03 --json
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/lane/tests/fixtures/r17-census-hygiene.py --tool /var/tmp/souji-r18w2-MutFixtureSessionKill/r17-census-no-watchdog.sh --case R17-08 --json
```

Two initial asynchronous bash launch requests were refused with `Background job limit reached (100). Wait for running jobs to finish or cancel one.` They did not execute the detector. Execution then used the concurrent asyncio launch above; no peer job was polled or cancelled.

# Observed outputs and process counts

Counts were taken immediately after the fixture wrapper returned, before the detector reaped adopted descendants:

| Fixture | Bytes | Elapsed seconds | Fixture exit | Live residue | Zombie residue | After detector reap | Mutation result |
|---|---|---:|---:|---:|---:|---:|---|
| r15 / R15CFG-03 | pristine | 91.069 | 1 | 0 | 2 | 0 | detector baseline passes |
| r15 / R15CFG-03 | mutated | 91.330 | 1 | 0 | 2 | 0 | **survived**, timeout branch exercised |
| r15 / R15CFG-03 | restored | 90.838 | 1 | 0 | 2 | 0 | detector baseline passes again |
| r17 / R17-08 | pristine | 1.821 | 0 | 0 | 0 | 0 | no fixture timeout |
| r17 / R17-08 | mutated | 1.912 | 0 | 0 | 1 | 0 | **survived, unactivated** |
| r17 / R17-08 | restored | 1.778 | 0 | 0 | 0 | 0 | no fixture timeout |

Every fixture's stderr was the empty string.

Exact r15 stdout summary, identical in all three arms:

```text
TOOL-KIND	pre-harm-a31642d
SUMMARY	total=1	failed=1
```

Each r15 JSON record contained the `r-inc-fifo` invocation with `"exit": 124, "finding": "none"`; the CASE problem list included the exact string `r-inc-fifo: exit=124 want 0`. The fixture's functional FAIL is expected for this deliberately hanging historical census and is not a mutation kill. Other historical incompatibilities also appeared in that CASE. Its final `observed_exit=0` describes the last subsequent mixed-fleet invocation, not the FIFO invocation; the per-run JSON and actual signal records establish that the FIFO timeout was reached (`r15:803–839`, `r15:1171–1191`).

Exact r17 stdout CASE/summary, identical in all three arms:

```text
CASE	R17-08	PASS	class=repair	ok	observed_exit=0	observed_finding=none
SUMMARY	total=1	failed=0
```

Its JSON recorded both census runs with `"exit": 0, "finding": "none"`. Neither `os.kill` nor `os.killpg` was called by the fixture in any r17 arm.

Recorded r15 timeout identities and dead leftovers:

| Arm | Timeout session ID | Session member PIDs at timeout | PGIDs at timeout | Zombies after fixture return | Reaped wait statuses |
|---|---:|---|---|---|---|
| pristine | 1922225 | 1922225, 1922245, 1922770 | all 1922225 | 1922245, 1922770 | both 9 |
| mutated | 3022613 | 3022613, 3022623, 3022914 | all 3022613 | 3022623, 3022914 | both 9 |
| restored | 3879533 | 3879533, 3879545, 3879802 | all 3879533 | 3879545, 3879802 | both 9 |

Pristine/restored each recorded three individual SIGKILL calls plus the helper's final group SIGKILL. Mutated recorded no individual kill calls and exactly one `killpg(3022613, SIGKILL)`; its pre-signal snapshot identified strace, bash, and blocked `git ... rev-parse --is-inside-work-tree`, all in that one PGID. Thus the weaker cleanup reached the same live processes in this stimulus.

The r17 mutant's sole post-return record was PID 3029571, state `Z`, SID 3026670, PGID 3029063, starttime 3031802; the detector reaped it with wait status 0. It was not a live leftover, and the mutated timeout statement had never executed. No causal live-leak claim is made from this scheduling-dependent dead-process observation.

# Initial full-fixture findings and smallest fix

1. **r15: activated but nondiscriminating cleanup coverage.** The a31642d FIFO hang exercised the changed timeout statement, but every observed session member belonged to the leader's process group. It cannot distinguish whole-session cleanup from leader-group cleanup. The mutant survived with exactly the pristine live-residue result. This is a coverage finding, not proof that session-wide cleanup is unnecessary.

2. **r17: prescribed stimulus does not induce a hang.** Disabling only the watchdog does not remove the metadata kind guard. `R17-08` creates its FIFO at `tests/fixtures/r17-census-hygiene.py:782–791`; `tools/souji-census.sh:589–625`, particularly `617–620`, classifies nonregular `info/attributes` and degrades the repository without opening it. Therefore the allowed pinned-copy stimulus completed in about two seconds, and the mutated timeout callsite remained unexecuted. Evidence for behavior *after a timeout* is inconclusive in this arm. No extra guard bypass, new stall injection, or other mutation probe was run beyond the assigned scope.

**Initial verdict (superseded by the activated helper probe below): partial coverage; zero killed mutants.** The weakened cleanup survived both initially prescribed stimuli, but neither observation refutes production session cleanup. The r15 arm lacks a blocked cross-PGID child; the r17 arm lacks a timeout altogether. The missing prerequisite for the intended positive falsifier is a permitted hanging child in another PGID of the fixture-launched session.

**Smallest fix:** strengthen the fixture-lifecycle regression stimulus, not the production cleanup: require an observed timeout with a blocked worker whose PGID differs from its SID, then assert bounded fixture return and zero live session residue. Retain the leader-group-only mutant as the positive detector control. No lane fix was made or justified by this probe.

# Restoration and cleanup evidence

Observed SHA-256 values:

| Fixture | Before | Mutated | Restored |
|---|---|---|---|
| r15-census-config.py | `61208dbd53367fa85b6f2e6d10d521900a34e1f41a27962cfbb1559ea0189f08` | `3c6f96a83bae2048c2d15703a533bd8294985e5e638bdf3dd77c9b7b9fb84158` | `61208dbd53367fa85b6f2e6d10d521900a34e1f41a27962cfbb1559ea0189f08` |
| r17-census-hygiene.py | `716ad2395b74275e162ea085f353ade5a800cc5973e4557c2c8f8380faf2d264` | `aad7b7702961a97748141163eae358ea10bb6adfa85b9f5b5496d8ecc12e1723` | `716ad2395b74275e162ea085f353ade5a800cc5973e4557c2c8f8380faf2d264` |

Both one-line mutations were reversed before the restored-arm runs. The separate `sha256sum` command on both restored absolute fixture paths returned the original hashes above. All six detector receipts recorded no remaining members after their owned-child cleanup/reap; the detector sent no cleanup signal to any live process.

Finally this command returned exit 0 with no stdout/stderr, deleting the restored clone and all disposable harness/stimulus/output files:

```sh
rm -rf -- /var/tmp/souji-r18w2-MutFixtureSessionKill
```

Tooling: existing `/usr/bin/python3` reported `Python 3.14.8`; existing git, bash and strace were used. No tool was installed or updated, no pacman transaction was attempted, and no fleet repository was modified by git.

# Authorized activated helper follow-up

L1 subsequently authorized a synthetic helper invocation to activate the missing discriminator: import the named fixture without calling `main`, invoke its subprocess helper on a writer-less FIFO reader launched by Bash job control in another PGID of the same session, and compare original/mutated/restored cleanup with helper timeout 1 second. This follow-up uses that authorization only; it does not change the original full-fixture observations above.

The previously deleted private clone was recreated with the same clone/checkout commands and pinned again to `5efb519f00075d958c3d1109ef6fcb24c487eb87`. The same one-line mutations at `r15:308` and `r17:195` were applied and reversed only in that clone. No production census was executed in this follow-up.

## Activated detector and command

`/var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py`, SHA-256 `cc4cf9692177732d9aa8729b88663c505085266900a785c4c419dfddb3daf458`, imported each complete fixture using `importlib.util.spec_from_file_location` and `exec_module`, without executing `main`. No setup globals or helper extraction were needed. It called the actual imported helpers:

```python
# r15
module.run_in_session(command, capture_output=True, text=True,
                      errors="replace", timeout=1)
# r17
module.run_process_group(command, timeout=1)
```

Both existing helpers passed `start_new_session=True` to their real `Popen`. A forwarding Popen shim logged that flag and the launched identity. The exact command array used this Bash script, followed by `_`, the arm-private FIFO path, and the arm-private PID log path:

```sh
/usr/bin/bash -c 'printf "leader %s\n" "$BASHPID" >> "$2"; set -m; (printf "reader %s\n" "$BASHPID" >> "$2"; read x < "$1") & wait' _ /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-<arm>-<fixture>/fifo /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-<arm>-<fixture>/pids.txt
```

The Bash `printf` shims recorded leader/reader PIDs before blocking. Before the one-second helper timeout, the detector required actual `/proc` evidence that the reader had the same SID as the leader but a different PGID, state `S`, and `wchan=wait_for_partner`. Every arm satisfied that precondition about 0.031 seconds after wrapper launch.

The same detector and three-second outer deadline were used for every arm. At natural helper-wrapper return, or the outer deadline if it did not return, the subreaper reaped already-dead adopted children and enumerated the target SID. Thus the exact-member counts below include any still-present zombie leader, but do not count a dead reader already reaped. No live process was removed before this checkpoint. If the helper exceeded the bound, only recorded, identity-matching live descendants were SIGKILLed after the failure snapshot; helper completion after that rescue was not counted as an unassisted pass.

Exact executed outer commands, with each fixture pair launched concurrently:

```sh
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py parent pristine r15
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py parent pristine r17
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py parent mutated r15
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py parent mutated r17
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py parent restored r15
/usr/bin/python3 /var/tmp/souji-r18w2-MutFixtureSessionKill/helper-probe.py parent restored r17
```

## Actual outputs: original 0, mutant >0, restored 0

| Fixture / arm | Leader PID = SID = leader PGID | Reader PID = reader PGID | Reader SID | Checkpoint exact SID members | Checkpoint live members | Outer bound exceeded | Detector exit / pass |
|---|---:|---:|---:|---:|---:|---|---|
| r15 pristine | 2479882 | 2479884 | 2479882 | 0 | 0 | false | 0 / true |
| r15 mutated | 2484674 | 2484676 | 2484674 | 2 | 1 | true | 1 / false |
| r15 restored | 2485952 | 2485956 | 2485952 | 0 | 0 | false | 0 / true |
| r17 pristine | 2479880 | 2479883 | 2479880 | 0 | 0 | false | 0 / true |
| r17 mutated | 2484673 | 2484675 | 2484673 | 2 | 1 | true | 1 / false |
| r17 restored | 2485961 | 2485965 | 2485961 | 0 | 0 | false | 0 / true |

All six stimulus proofs recorded `new_session: true`. Every reader was observed before timeout in state `S` and `wchan: "wait_for_partner"`; every leader was state `S`, `wchan: "do_wait"`.

Exact r15 mutant failure snapshot:

```json
[
  {"pid":2484674,"ppid":2484671,"pgid":2484674,"sid":2484674,"state":"Z","starttime":3130811,"wchan":"0"},
  {"pid":2484676,"ppid":2484666,"pgid":2484676,"sid":2484674,"state":"S","starttime":3130811,"wchan":"wait_for_partner"}
]
```

Exact r17 mutant failure snapshot:

```json
[
  {"pid":2484673,"ppid":2484672,"pgid":2484673,"sid":2484673,"state":"Z","starttime":3130811,"wchan":"0"},
  {"pid":2484675,"ppid":2484667,"pgid":2484675,"sid":2484673,"state":"S","starttime":3130811,"wchan":"wait_for_partner"}
]
```

Each pristine/restored helper recorded two individual SIGKILLs, including the reader in its distinct PGID, followed by the helper's group SIGKILL. Each mutant recorded **zero** individual kill calls and exactly one group SIGKILL, targeting only its leader PGID. The mutant readers remained blocked, keeping the captured pipes open and leaving the helper's second `communicate()` unable to finish before the outer deadline. These are activated, baseline-discriminating failures, not failures inferred from the earlier suite CASE results.

Observed timings:

| Fixture / arm | Helper outcome | Helper elapsed seconds | Detector elapsed seconds | Rescue needed |
|---|---|---:|---:|---|
| r15 pristine | TimeoutExpired | 1.0119 | 1.0782 | no |
| r15 mutated | TimeoutExpired, **only after rescue** | 2.9911 | 3.0403 | reader 2484676 SIGKILL |
| r15 restored | TimeoutExpired | 1.0111 | 1.0769 | no |
| r17 pristine | TimeoutExpired | 1.0122 | 1.0790 | no |
| r17 mutated | TimeoutExpired, **only after rescue** | 2.9914 | 3.0401 | reader 2484675 SIGKILL |
| r17 restored | TimeoutExpired | 1.0093 | 1.0769 | no |

The outer deadline is measured from wrapper launch, slightly before helper invocation. This explains the rescued helper's elapsed time just below three seconds; it does not represent natural completion.

Exact child-wrapper stdout, identical across the three arms of each respective fixture after any necessary rescue:

```text
r15: {"outcome": "TimeoutExpired", "timeout": 1, "stdout": null, "stderr": null}
r17: {"outcome": "TimeoutExpired", "timeout": 1, "stdout": "", "stderr": ""}
```

Every wrapper's stderr was empty. The stdout TimeoutExpired alone is not the detector: the pre-rescue bound/residue fields distinguish the mutant. All six child wrappers eventually exited 0, while the outer detector correctly returned 1 for both mutant arms.

## Follow-up verdict and restoration

**Mutant verdict: KILLED in both helpers.** Original and restored each completed promptly and left zero exact SID members after dead-child reap. The leader-only mutant exceeded the fixed bound and left one live cross-PGID reader plus the dead leader in the target SID. Thus the pinned session-wide cleanup holds for this specifically activated behavior. The initial full-fixture stimulus coverage gap remains a separate finding; the activated helper test resolves the earlier missing positive-control prerequisite.

**Smallest fix recommendation:** no production-code change is justified. Keep the existing `kill_session` callsites. If this behavior is to remain regression-protected, add the authorized cross-PGID FIFO-helper stimulus as a lifecycle test and require its leader-only mutant to fail. No lane source or test was changed by this seat.

Restoration used the identical one-line reversals. Actual fixture SHA-256 receipts again matched:

| Fixture | Original | Mutated | Restored |
|---|---|---|---|
| r15 | `61208dbd53367fa85b6f2e6d10d521900a34e1f41a27962cfbb1559ea0189f08` | `3c6f96a83bae2048c2d15703a533bd8294985e5e638bdf3dd77c9b7b9fb84158` | `61208dbd53367fa85b6f2e6d10d521900a34e1f41a27962cfbb1559ea0189f08` |
| r17 | `716ad2395b74275e162ea085f353ade5a800cc5973e4557c2c8f8380faf2d264` | `aad7b7702961a97748141163eae358ea10bb6adfa85b9f5b5496d8ecc12e1723` | `716ad2395b74275e162ea085f353ade5a800cc5973e4557c2c8f8380faf2d264` |

The independent restored `sha256sum` command returned the original hashes. The detector's only rescue signals targeted recorded readers 2484676 and 2484675, with matching PID/starttime/SID. Both were reaped with wait status 9. Pristine/restored readers were likewise reaped after the fixture helpers killed them. Every arm recorded `remaining_after_cleanup: []`; there were no remaining live processes or zombies in any target SID.

After all restored probes, `rm -rf -- /var/tmp/souji-r18w2-MutFixtureSessionKill` again returned exit 0 with no stdout/stderr, removing the restored clone and all follow-up scratch. No tools were installed or updated, no network write or git commit was performed, and the only lane write remains this report.
