STATUS: DONE — added P12–P19 W2 regressions; all 19 cases pass against the W2-fixed 5efb519 tool.

## Scope and behavior

Changed only `tests/fixtures/r18-proc-census.sh` in the detached 5efb519 clone; delivered patch: `.ufo/waves/round-18/w1/ProcCensusFixtureFix.patch`.

- P12/P13 reject live cwd/fd inodes whose literal basename ends in ` (deleted)`; P13 uses the live fd parent as `--prefix` (`tests/fixtures/r18-proc-census.sh:412-431,657-681`).
- P14–P16 check fake Authorization/Bearer, AKIA-shaped, and xoxb-shaped argv values are redacted (`:433-455,683-693`). No real credentials are used.
- P17 uses an existing prefix root and a deleted, similarly prefixed sibling; P18/P19 assert cwd > argv > fd and argv > fd precedence, with P9 preserving fd-only coverage (`:457-489,695-751`).
- P7 traces only the fixture-owned census process tree using `strace -f -e trace=kill,tkill,tgkill,pidfd_send_signal`; fixture-worker setup and cleanup remain outside the trace. The case checks the trace ledger as well as worker liveness (`:220-254,597-618`). P4 failure output now includes rc, timeout, parse result, and stderr (`:550-567`).

## W2 evidence reviewed

- `w2/ProbeProcEdges.md:17-44,74-76`: live cwd/fd targets literally ending in ` (deleted)` and exact mixed-reason precedence.
- `w2/RevRedactionLanded.md:9-21`: Authorization/Bearer, AKIA, and xoxb leaks.
- `w2/MutProcCensus.md:16-20,27-35`: surviving sibling-prefix mutant, liveness-only P7 signal mutant, and precedence coverage gap.

## Commands and retained evidence

- Clone: `git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18-ProcCensusFixtureFix/lane && git -C /var/tmp/souji-r18-ProcCensusFixtureFix/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87` — no output. Clone HEAD readback: `5efb519f00075d958c3d1109ef6fcb24c487eb87`.
- `bash -n /var/tmp/souji-r18-ProcCensusFixtureFix/lane/tests/fixtures/r18-proc-census.sh` — exit 0, no output.
- `shellcheck -S warning /var/tmp/souji-r18-ProcCensusFixtureFix/lane/tests/fixtures/r18-proc-census.sh` — no diagnostics. Existing ShellCheck is 0.11.0; strace is 7.2. No tools were installed or updated.
- Header-only stub run: `/var/tmp/souji-r18-ProcCensusFixtureFix/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18-ProcCensusFixtureFix/header-only.sh || printf 'EXPECTED_STUB_EXIT=%s\n' "$?"; rm -f -- /var/tmp/souji-r18-ProcCensusFixtureFix/header-only.sh` — expected exit 1; P1/P2 fail. It also exercises the strace path:
  ```text
  CASE	P1	FAIL	missing FIFO reader row (ok)
  CASE	P2	FAIL	missing or wrong argv-path-gone row
  CASE	P3	PASS	live control absent
  CASE	P4	FAIL	--prefix did not select P2/exclude P6 (rc=0 timed_out=False table=ok stderr='')
  CASE	P5	PASS	fresh residue workers excluded
  CASE	P6	FAIL	missing P6 row or secret not redacted
  CASE	P7	PASS	strace observed no signal syscalls; fixture workers alive
  CASE	P8	PASS	invalid usage exited 2
  CASE	P9	FAIL	missing or wrong fd-path-gone row
  CASE	P10	PASS	deleted nested boundary omitted
  CASE	P11	FAIL	starttime mismatch reported=None stat=3181818
  CASE	P12	PASS	live literal cwd suffix omitted
  CASE	P13	PASS	live literal fd suffix omitted
  CASE	P14	FAIL	Bearer value not redacted
  CASE	P15	FAIL	AWS-shaped value not redacted
  CASE	P16	FAIL	Slack-shaped value not redacted
  CASE	P17	PASS	similarly prefixed sibling excluded
  CASE	P18	FAIL	wanted=cwd-deleted got=None argv_gone=True fd_gone=True cwd_deleted=True
  CASE	P19	FAIL	wanted=argv-path-gone got=None fd_gone=True cwd_live=True
  SUMMARY	total=19	failed=11
  EXPECTED_STUB_EXIT=1
  ```
- Self-signal mutant stub: `/var/tmp/souji-r18-ProcCensusFixtureFix/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18-ProcCensusFixtureFix/self-signal.sh || printf 'EXPECTED_MUTANT_EXIT=%s\n' "$?"; rm -f -- /var/tmp/souji-r18-ProcCensusFixtureFix/self-signal.sh`. This fixture-owned stub sends `SIGCONT` only to its own PID; P7 fails on the traced syscall, demonstrating detection beyond liveness:
  ```text
  CASE	P7	FAIL	strace observed signal syscall: 3697642 kill(3697642, SIGCONT)          = 0
  SUMMARY	total=19	failed=12
  EXPECTED_MUTANT_EXIT=1
  ```

The following is the final rerun after the tool owner’s last source refresh, which adds a synthetic `/proc/stat` comm-newline selftest case; all 19 fixture cases remained green.

- Full live fixture: `/var/tmp/souji-r18-ProcCensusFixtureFix/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18-ProcCensusFix/lane/tools/souji-proc-census.sh` — exit 0. Tool clone HEAD is `5efb519f00075d958c3d1109ef6fcb24c487eb87`. Complete output:
  ```text
  CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
  CASE	P2	PASS	argv-path-gone row present
  CASE	P3	PASS	live control absent
  CASE	P4	PASS	prefix retained P2 and excluded P6
  CASE	P5	PASS	fresh residue workers excluded
  CASE	P6	PASS	password argv redacted
  CASE	P7	PASS	strace observed no signal syscalls; fixture workers alive
  CASE	P8	PASS	invalid usage exited 2
  CASE	P9	PASS	deleted stdout fd reported
  CASE	P10	PASS	deleted nested boundary omitted
  CASE	P11	PASS	starttime matches /proc field 22
  CASE	P12	PASS	live literal cwd suffix omitted
  CASE	P13	PASS	live literal fd suffix omitted
  CASE	P14	PASS	Authorization Bearer argv redacted
  CASE	P15	PASS	AWS-shaped argv redacted
  CASE	P16	PASS	Slack-shaped argv redacted
  CASE	P17	PASS	similarly prefixed sibling excluded
  CASE	P18	PASS	cwd wins over argv and fd
  CASE	P19	PASS	argv wins over fd
  SUMMARY	total=19	failed=0
  ```
- Final patch generation: `git -c diff.mnemonicPrefix=false -C /var/tmp/souji-r18-ProcCensusFixtureFix/lane diff 5efb519f00075d958c3d1109ef6fcb24c487eb87 -- tests/fixtures/r18-proc-census.sh > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/ProcCensusFixtureFix.patch` — no output. Readback confirms executable mode `100755`, base blob `3c9f8e0`, final blob `2d7c5be`, 476 patch lines.

## Verdict and risks

Syntax, ShellCheck, header-only non-vacuity, self-signal detection, and all 19 live cases passed. The live run used the ProcCensus owner's updated 5efb519 clone; the parent remains responsible for post-integration verification. No unrelated files were changed.