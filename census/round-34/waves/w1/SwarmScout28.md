## Status
STATUS: PASS — host bwrap and namespace assumptions in `leg_witness` were probed; no C2 leg result claimed.

## Evidence
- Version/sysctl command: `bwrap 0.13.1`, `strace 7.2`, `Python 3.14.8`, `git 2.56.0`, `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`; userns sysctl/proc `1`/`1`; revision inspected `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.
- Full sandbox-envelope probe (bwrap namespace flags, dev-bind root, ro-bind empty `/tmp` and `/dev/shm`, private writable `/var/tmp` bind, TMPDIR): output `TMP_READ_ONLY`, `SHM_READ_ONLY`, `WRITABLE_TARGETS_OK`, rc 0.
- Existing-host-canary bind probe: output `HIDDEN_INSIDE`, bind write succeeded, real host canary remained byte-identical (`host-canary`); rc 0.
- Traced envelope: strace inside bwrap rc 0, 2 file-creation records, bind-target write observed. Load readings recorded beside probes in delivery file.
- Lane source: `census/round-34/c2-counter.py:159-162`, quote: “--unshare-user”, “--unshare-pid”, “--dev-bind”, “--ro-bind”, “--bind”, “--setenv”, “--chdir”.

## Findings
1. Host has bwrap 0.13.1, strace 7.2 and `kernel.unprivileged_userns_clone=1`; the actual requested user/pid namespace sandbox invocation succeeded. Source: `census/round-34/c2-counter.py:159-162`, quote above.
2. Counter's empty-directory read-only mounts at `/tmp` and `/dev/shm`, root dev-bind and TMPDIR assignment worked in the probe. Both protected mounts rejected writes while scratch TMPDIR remained writable. Source: `census/round-34/c2-counter.py:159-162`, quote above.
3. Writable `--bind <scratch>/vt /var/tmp` over the non-empty real host directory hid the host canary inside; writes appeared in the private bind and the host canary reappeared unchanged after. This confirms the mount-over-not-hide behavior asked for. Source: `census/round-34/c2-counter.py:159-162`, quote above.
4. Strace ran inside the full bwrap envelope and traced file-creation calls, supporting host feasibility of the witness instrumentation. This did not test each W1-W4 base/tip comparison or the N3 fixture/pin assertion. Source: `census/round-34/c2-counter.py:156-162`, quote: “strace -f -qq -e trace=%file”.
5. `--chdir <clone>` and `bash -c` are present in the command; this probe did not independently exercise them using a cloned revision. No host-level gap found for the bwrap mount/userns assumptions checked.

## Attack log
None.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-sandbox-recon.txt`
