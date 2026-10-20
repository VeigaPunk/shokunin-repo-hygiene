STATUS: DONE — session-wide timeout cleanup eliminates the reproduced R17 FIFO residue (4 processes → 0).

# FixtureReapR17 — r18 W1

Axis: operability.

## Scoped change

Changed only `tests/fixtures/r17-census-hygiene.py` in `/var/tmp/souji-r18-FixtureReapR17/lane`.

- `kill_session` at lines 149–170 reads `/proc/<pid>/stat`, selects processes whose session field (field 6) equals the launched leader PID, sends `SIGKILL`, then also kills the leader process group.
- `run_process_group` at lines 173–201 starts a new session and, on timeout, performs the session sweep, process-group kill, and reap before raising `TimeoutExpired`.
- `run_setup` (203–210), `run_tool` (337–359), and the locale probe (1129–1137) use the common runner. `run_tool` unblocks fixture FIFOs only after the timed-out session has been killed and reaped. Cases and expectations are unchanged.
- Delivered `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/FixtureReapR17.patch`.

## Evidence

### Original census behavior

The exact `5fa6017:tools/souji-census.sh` copy has SHA-256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`. Running R17-08 against it before modifying the copy yielded exit 1 with `observed_exit=2`, `observed_finding=path-protected:git-metadata-nonregular`. Its `guard_git_files` checks `info/attributes` at line 521 and refuses a non-regular object at line 532, before Git reaches `status`; this plain historical arm measured 0 → 0 residue.

### Forced timeout arm

To exercise the reported job-control failure without changing lane sources, a temporary `/var/tmp` census copy was used. It removes only the non-regular refusal for `info/attributes` and models the R18 `set -m` census worker: each `census_one` runs as a background job with stdout redirected to a private temp file. The original 5fa source has no such job-control grouping, so merely removing its guard did not produce the session/PGID split. Final test-copy census SHA-256: `e8757824b6d0e33af3d91aadff60a5a2a35519ddab61826ba5ec6324e1418d8e`.

Temporary copies of the base and patched fixtures used a 10-second `run_tool` timeout to exercise the unchanged timeout branch more quickly; the R17-08 case and its expectations were not changed. Test-copy SHA-256 values: base `3c09ea43ba7bed1a6aeafe125577be4b6521e00d8ddb6b34007bec0eeaf09597`; patched `76116ed2edc769ae5130d98e63260e8dde4be555a73ab1f222f3b92f573c238c`.

Base command:

```text
/usr/bin/timeout --kill-after=2s 20s python3 -u /var/tmp/souji-r18-FixtureReapR17/evidence/base-r17-census-hygiene.py --case R17-08 --census /var/tmp/souji-r18-FixtureReapR17/evidence/r16-census-with-guard.sh
```

Observed output was the `TOOL` line for census SHA `e8757824…`; the outer timeout returned 124 after 20 seconds because the base fixture's `proc.communicate()` remained blocked after its process-group kill. `ps -eo pid,ppid,pgid,sid,etime,state,wchan:32,args` then found **4** processes under `/var/tmp/r17-census-hygiene.78k9ul0n/d2-fifo`: PIDs 1887917, 1888174, 1888417, and 1888419 (the last was `git ... status`). All had PGID 1887917 and SID 1886385. I killed only those four fixture-owned PIDs, then confirmed no `78k9ul0n` process remained. The associated fixture tree and its row tempfile were removed.

Patched command:

```text
/usr/bin/timeout --kill-after=2s 20s python3 -u /var/tmp/souji-r18-FixtureReapR17/evidence/patched-r17-census-hygiene.py --case R17-08 --census /var/tmp/souji-r18-FixtureReapR17/evidence/r16-census-with-guard.sh
```

Observed output:

```text
TOOL	/var/tmp/souji-r18-FixtureReapR17/evidence/r16-census-with-guard.sh	sha256=e8757824b6d0e33af3d91aadff60a5a2a35519ddab61826ba5ec6324e1418d8e
CASE	R17-08	FAIL	class=repair	fleet run timed out (blocked on non-regular metadata)	observed_exit=124	observed_finding=none
SUMMARY	total=1	failed=1
```

The fixture returned exit 1 because this historical census copy does not implement the R17 repair. Its timeout path completed, unblocked the FIFO, and cleaned up. The post-run process inventory contained **0** processes from the patched run's scratch path: forced-arm residue **4 → 0**. A pre-existing set of leaked processes from other runs remained visible and was not signalled.

No tools were installed or updated. No build, lint, or broader test suite was run.

## Risk

The positive reproduction uses a temporary copy that models R18's per-repository job-control fork; the untouched 5fa revision guards this FIFO before `status`, so its direct arm cannot reproduce the leak. The test-copy-only `set -m`/temp-file changes and 10-second timeout are not part of the delivered patch.