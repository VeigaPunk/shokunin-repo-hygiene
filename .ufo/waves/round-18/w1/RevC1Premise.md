STATUS: DONE — C1’s post-guard FIFO hang reproduced; the census emitted no output before timeout.

# Axes
- **Operability (judged):** The one-repository hang blocks the run and loses every census row.
- **Calibration:** The reproduced race is at base `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, after the existing metadata guard.
- **Coverage:** The control completed; the race arm timed out; no process for this lab remained afterward.

# Finding — High: C1 premise holds
The specified post-guard replacement of `.git/info/attributes` with a FIFO reproduces a fleet-wide census hang. The base census buffers rows until the entire loop completes, so a blocked repository prevents even the header and healthy-neighbour rows from being emitted.

## Fixture and source identity
Extracted with:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh > /var/tmp/souji-r18-RevC1Premise/census.sh
```

Observed: `wc -l` → `2072`; SHA-256 → `006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd`.

`setup.sh` built `/var/tmp/souji-r18-RevC1Premise/root/{a,b,c}` as three ordinary repositories, each with one committed `tracked.txt`. Before the final arms, b had a regular `.git/info/attributes` containing `tracked.txt text`; `$HOME` was the empty lab directory. The PATH shim fires only when its args include the b path and `status`; it removes the regular attributes file, creates a FIFO, runs `touch` on b’s tracked file (mtime only), then execs `/usr/bin/git`.

## Control
Run from `/var/tmp/souji-r18-RevC1Premise`:

```sh
HOME=/var/tmp/souji-r18-RevC1Premise/home PATH=/usr/bin:/bin timeout -k 2 15 bash census.sh --root root > runs/control.stdout 2> runs/control.stderr
```

Observed exit status: **0**. Stderr was empty. Stdout:

```text
repo	worktrees	unpushed	dirty	scratch_bytes	mtime_iso	verdict_flags
/var/tmp/souji-r18-RevC1Premise/root/a	1	1	0	0	2026-10-20T16:58:49-03:00	unpushed,no-remote
/var/tmp/souji-r18-RevC1Premise/root/b	1	1	0	0	2026-10-20T17:01:08-03:00	unpushed,no-remote
/var/tmp/souji-r18-RevC1Premise/root/c	1	1	0	0	2026-10-20T16:58:49-03:00	unpushed,no-remote
```

## Post-guard FIFO arm
Run from the same lab directory:

```sh
HOME=/var/tmp/souji-r18-RevC1Premise/home PATH=/var/tmp/souji-r18-RevC1Premise/shim:/usr/bin:/bin timeout -k 2 15 bash census.sh --root root > runs/shim.stdout 2> runs/shim.stderr
```

Observed exit status: **124** at **15 seconds**. Stdout was empty (zero rows, including no header); stderr was empty. Therefore neither a nor c was emitted, and b was not emitted either. The shim log at the triggering call recorded:

```text
CALL <-C> </var/tmp/souji-r18-RevC1Premise/root/b> <--no-optional-locks> <-c> <core.fsmonitor=false> <-c> <core.hooksPath=/dev/null> <-c> <core.excludesFile=/dev/null> <-c> <core.attributesFile=/dev/null> <status> ...
SWAP before exec: /var/tmp/souji-r18-RevC1Premise/root/b/.git/info/attributes is regular=yes
SWAP complete: attributes FIFO; touched tracked.txt mtime only
```

This establishes that the injected change was post-guard in this run: the shim observed a regular file at b’s `status` invocation, and the census first executes `guard_git_surface` in `census_one` (`tools/souji-census.sh:1261-1268`) before calling `count_dirty` (`:1291`), whose Git status is at `:1122-1125`. `list_repos` also runs `guard_git_surface` while collecting repositories (`:1384-1386`). A pre-existing nonregular attributes file follows the existing soft-error path (`guard_git_files`, `:539-585`; `census_one`, `:1264-1267`) rather than proceeding to status; that path is supported by source inspection but was not run as a separate arm.

Total row loss is explained by `emit_census`: it accumulates each `census_one` result in `rows` (`:1401-1410`) and prints the header and rows only after the whole loop (`:1412-1414`).

## Cleanup and verification gaps
After the timed-out arm, `ps -eo pid,ppid,pgid,stat,wchan:20,args` was captured and searched for `souji-r18-RevC1Premise`; no matching process remained. No unrelated processes were signalled. The lab directory was removed after preserving these results here.

No live `/proc` wait-channel sample or syscall trace was captured, so the timeout and the block at b’s status call are observed; the more specific claim that the blocked syscall was `open(2)` remains unverified by this probe. The `lsp` device is unavailable (`read xd://lsp` returned “No such tool”), so source control-flow evidence is from the exact extracted base script.

**Verdict:** C1’s operability premise holds. The smallest fix remains per-repository process-group isolation with a bounded watchdog and buffered per-repository output, so a timed-out repo becomes an error row without suppressing healthy rows. No source changes were made.

## Probe correction note
An initial non-equivalent arm appended bytes to b’s tracked file instead of using mtime-only `touch`; it completed with rc 0 and three rows and is excluded from the finding. The corrected arm above uses literal `touch` as assigned. One fixture-reset attempt then timed out after 40 seconds because it tried writing attributes over the FIFO left by that initial arm; the failed shell was gone in the subsequent process snapshot. The fixture was reset safely by unlinking the FIFO before recreating the regular file. No tool was installed or updated.
