STATUS: DONE — the expanded fixture is implemented and passes P1–P11 against the updated census tool; it rejects the header-only stub.

## Files and behavior

- `tests/fixtures/r18-proc-census.sh` (new, executable; patch: `.ufo/waves/round-18/w1/ProcCensusFixture.patch`). Covers deleted-cwd FIFO detection, argv-path detection, live-control omission, argv-prefix selection, minimum age, secret redaction, non-signalling, invalid-usage exit 2, deleted-fd detection, nested-boundary exclusion, and starttime identity. It validates the leading boot-id comment and exact ten-column TSV header, maps rows by header name, and compares `starttime` with `/proc/<pid>/stat` field 22 (`tests/fixtures/r18-proc-census.sh:186-232,353-381,460-493`).
- P9 holds stdout open on a file in a separately removed `/var/tmp` top-level directory while its cwd and argv remain clean; P10 deletes `/var/tmp/<top>/sub` while `<top>` remains live (`tests/fixtures/r18-proc-census.sh:306-351`). P4 selects P2 and excludes P6 according to argv-prefix semantics (`tests/fixtures/r18-proc-census.sh:401-416`).
- Workers and census invocations use `start_new_session=True`; timed-out invocations and cleanup signal only fixture-created process groups. Main scratch is trapped under `/var/tmp`; additional temporary roots are reaped in `finally` (`tests/fixtures/r18-proc-census.sh:62-72,116-124,165-185,252-269,496-502`).

## Commands and retained evidence

- Clone: `git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18-ProcCensusFixture/lane && git -C /var/tmp/souji-r18-ProcCensusFixture/lane checkout --quiet --detach b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` — no output.
- Availability: `command -v shellcheck && shellcheck --version` — `/usr/bin/shellcheck`; version `0.11.0`.
- `bash -n /var/tmp/souji-r18-ProcCensusFixture/lane/tests/fixtures/r18-proc-census.sh` — exit 0, no diagnostics.
- `shellcheck -S warning /var/tmp/souji-r18-ProcCensusFixture/lane/tests/fixtures/r18-proc-census.sh` — no ShellCheck diagnostics.
- Final live fixture command: `/var/tmp/souji-r18-ProcCensusFixture/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18-ProcCensus/lane/tools/souji-proc-census.sh` — exit 0:
  ```text
  CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
  CASE	P2	PASS	argv-path-gone row present
  CASE	P3	PASS	live control absent
  CASE	P4	PASS	prefix retained P2 and excluded P6
  CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
  CASE	P6	PASS	secret-shaped argv redacted
  CASE	P7	PASS	all fixture workers remain alive
  CASE	P8	PASS	invalid usage exited 2
  CASE	P9	PASS	deleted stdout fd reported
  CASE	P10	PASS	deleted nested boundary omitted
  CASE	P11	PASS	starttime matches /proc field 22
  SUMMARY	total=11	failed=0
  ```
  An earlier live run caught the tool emitting `wchan='-'` despite setup observing `wait_for_partner`; the tool owner fixed EOF handling, and the final rerun above passes P1.
- Header-only stub command: `/var/tmp/souji-r18-ProcCensusFixture/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18-ProcCensusFixture/header-only.sh || printf 'EXPECTED_STUB_EXIT=%s\n' "$?"; rm -f -- /var/tmp/souji-r18-ProcCensusFixture/header-only.sh` — expected fixture exit 1; P1 and P2 fail, proving non-vacuity. Captured output:
  ```text
  CASE	P1	FAIL	missing FIFO reader row (ok)
  CASE	P2	FAIL	missing or wrong argv-path-gone row
  CASE	P3	PASS	live control absent
  CASE	P4	FAIL	--prefix did not select P2/exclude P6 (ok)
  CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
  CASE	P6	FAIL	missing P6 row or secret not redacted
  CASE	P7	PASS	all fixture workers remain alive
  CASE	P8	PASS	invalid usage exited 2
  CASE	P9	FAIL	missing or wrong fd-path-gone row
  CASE	P10	PASS	deleted nested boundary omitted
  CASE	P11	FAIL	starttime mismatch reported=None stat=2641726
  SUMMARY	total=11	failed=6
  EXPECTED_STUB_EXIT=1
  ```
  The temporary stub was removed after the run.
- Final patch generation: `git -c diff.mnemonicPrefix=false -C /var/tmp/souji-r18-ProcCensusFixture/lane diff b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tests/fixtures/r18-proc-census.sh > /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-18/w1/ProcCensusFixture.patch` — no output. Patch readback (`ProcCensusFixture.patch:1-6`) records new file mode `100755`, blob `3c9f8e0`, and 505 added lines. No tools were installed or updated.

## Verdict and risks

Syntax, ShellCheck, all eleven live cases, and header-only-stub falsification are exercised. The live run used the ProcCensus seat's updated tool in its `/var/tmp` clone; the parent remains responsible for the post-integration gate. No unrelated repository paths were changed.