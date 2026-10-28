# R41w2sentinel02 — safety review of the landed r41 fixtures under strace

Role: sentinel (leaf, read-only; no candidate files written; no git/jj mutation).
Subject: `tests/fixtures/r41-refusal-sites.py` (blob 85f3aca, = a1144120) and `tests/fixtures/r41-drift-record-order.py` (blob ccfb424, = a1144120), driving `tools/souji-worktree-drift.py` (blob fd72b2bb, sha256 b2a603cf…3ab3e34dc6, matches the frozen hash in the preregistration).
Lane tip at review: 1d41c13574db80fdd9a4bde490b712da7ce2a85f (unchanged after the runs).
Receipts (gzipped straces, analysis output, drivers, sweep lists): `.ufo/waves/round-41/w2/R41w2sentinel02/receipts/`.
Scratch: `/fast/scratch/hyaku/souji-r41/R41w2sentinel02/` (all runs, `--work` = `…/work/<name>`); deleted at the end (`rm -rf` rc=0).

## Verdict

| Assertion | Verdict | One-line basis |
|---|---|---|
| Every write-open / mutation of the fixtures and tool stays under `--work` | PASS (with the /dev/null caveat below) | strace: all write-class targets are under `$S/work/...`; only exceptions are /dev/null and the scratch stdout receipts |
| Nothing created/modified outside `--work` (find sweep + lane) | PASS, with limits | No lane path written; sweep window has 0 overlap with strace paths; full pre-run manifest not taken (see Limits) |
| chmod confined to `--work` | PASS | 3 chmod calls in refusal-sites, 20 in drift-order, all under the work tree |
| `/dev/null` never written | FAIL (literal) | 20 data writes to `/dev/null` in the refusal-sites run (tool stdout routed by the fixture's `stdout=DEVNULL`); 0 in drift-order; the `--json /dev/null` probe opens it O_WRONLY|O_CREAT but writes nothing and truncates nothing |
| Cleanup succeeds when interrupted by SIGTERM | FAIL | SIGTERM kills the interpreter with no unwinding; `finally` never runs; 26 and 91 leftover entries inside `--work` |
| Cleanup succeeds when interrupted by SIGINT (Python-handled) | PASS | KeyboardInterrupt → `finally` → `rmdir` of the run tree, 0 leftovers, 0 live tool children |
| No child processes escape the run (normal path) | PASS | All children exited 0/2 before the fixture's own rmtree; the only detached process is a `git maintenance --detach` child that exited 0 and wrote nothing after rmtree |
| No root / no privilege use | PASS | uid 1000 throughout; fixture refuses euid 0 by its own guard; no sudo, no chmod outside scratch |

Overall: the fixtures do not write outside their work directory and do not escape into other paths. Two stated acceptance bullets fail as written: the "/dev/null is never written" statement (the fixture deliberately sends tool stdout there) and SIGTERM cleanup (no handler). Remediation is in "Smallest remediation" below; nothing was changed.

## Commands actually run

Environment checks (read-only):
- `which strace; strace -V` → `/usr/bin/strace`, `strace -- version 7.2`. No install performed; no pacman use.
- `id -u` → `1000`. `python3 --version` → 3.14.8. `git --version` → 2.56.0.
- `git -C <lane> rev-parse --show-toplevel` → lane path. `git -C <lane> rev-parse HEAD:<path>` and `git hash-object <path>` for the three files (see verdict table).
- `sha256sum tools/souji-worktree-drift.py` → `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6`.

Static reads: both fixtures, the tool's `open_nofollow` (lines 238–280), `run`/JSON guards (lines 319–348, 419–436), `git()` wrapper and `CHILD_ENV` (lines 79–122).

Full runs (driver `receipts/driver.sh full1|full2`, i.e. `strace -f -y -s 300 -e trace=%file,%desc,%process,%signal -o <name>.strace python3 <fixture> --tool <lane>/tools/souji-worktree-drift.py --work $S/work/<name>`):
- `r41-refusal-sites`: rc=0; stdout `probe-P01=PASS … probe-P19=PASS`, `SUMMARY probes=21 pass=21 fail=0`; stderr empty; leftover entries in `--work`: 0.
- `r41-drift-record-order`: rc=0; `SUMMARY cases=12 pass=12 fail=0`; leftover entries: 0.

SIGTERM runs (driver `term1|term2`: launch under strace, wait until the fixture has a live child tool process, `kill -TERM <fixture pid>`):
- `term-refusal-sites`: fixture pid 3317813 had a live child; `--- SIGTERM {si_signo=SIGTERM, si_code=SI_USER, si_pid=3317801}` then `+++ killed by SIGTERM +++` (trace line 6163–6164). Wrapper rc=143. Leftover entries: 26. Orphan tool children after 1 s: 0.
- `term-drift-record-order`: fixture pid 3320863; `--- SIGTERM …` at trace line 9615, `+++ killed by SIGTERM +++` at 9619. Wrapper rc=143. Leftover entries: 91.

SIGINT contrast:
- First attempt (`int.sh`) discarded: the fixture's inherited SigIgn was `0000000001001006` (SIGINT ignored because the job came from a non-interactive background shell), so SIGINT had no effect and the run finished 21/21. Recorded in the receipts (`int-*.strace.gz`) only as a control that the disposition matters.
- Valid attempt (`int2.py`, child started with `preexec_fn` resetting SIGINT to SIG_DFL): `/proc/<pid>/status` showed `SigIgn 0000000001001000` (SIGPIPE only) and `SigCgt …0002` (SIGINT caught). `--- SIGINT {si_signo=SIGINT, si_code=SI_USER, si_pid=1213061}` at the fixture; Python raised `KeyboardInterrupt` (traceback in stderr); the wrapper ended rc=-2 (interpreter re-raises SIGINT on exit). Leftovers in `--work`: 0. Live tool children: 0. Trace shows `rmdir(".../work/int2-refusal-sites/tmp50ikmn6_") = 0` and for drift-order `rmdir(".../souji-r41-order.s__66ccg") = 0`, with 25 and 90 unlinkat calls in the respective trees.

Analysis (python3 over the traces, receipts `analyze.py`, `analyze2.py`, `analyze3.py`; output `analysis-full.txt`):
- Write-class syscalls by path category, successful exec list, `/dev/null` write calls, post-rmdir activity, `ftruncate` count, chdir count.

Sweep (marker `MARK` touched at 20:19:01 before the first run):
- `find /home/vgpnk /tmp /var/tmp -xdev \( -newer MARK -o -cnewer MARK \) -print` → 7763 entries (`receipts/sweep-after-all.txt.gz`); heavily populated by other fleet seats.
- Time-window list `find … -newer MARK ! -newermt @<end+5s>` → 330 entries (`receipts/sweep-window.txt`).
- Cross-check: set of every absolute path referenced in the four traces intersected with the 330 window entries → 0 common paths.
- `grep` of the window for lane paths excluding `.ufo/waves/round-41/w2/`: none. `/tmp` and `/var/tmp` entries in the window: 6, all `/var/tmp/souji-r18-FixtureR18Bounded.*` owned by other seats, none referenced by our traces.

Cleanup of this seat: copied receipts into `receipts/`, then `rm -rf /fast/scratch/hyaku/souji-r41/R41w2sentinel02` → rc=0; path no longer exists. (This also removed the SIGTERM leftovers, whose `o/denied` is mode 000 and `o/ro` is mode 0500; owner removal worked.)

## Evidence per assertion

### 1. Every path opened for write (strace `openat` with O_WRONLY/O_RDWR/O_CREAT/O_TRUNC/O_APPEND)

refusal-sites (`r41-refusal-sites.strace`, 40 write-open events):
- Fixture-made records and probes, all under `…/work/r41-refusal-sites/tmp*/` (`o/ok`, `o/denied`, `o/dup`, `o/empty`, `o/junk`, `o/t1..t3`, `o/out`, `o/gd`, `o/hl`, `o/hl2`, `gd/HEAD`, `root/r/.git`), mode 0644 each; trace lines ~1429–1475.
- Tool open_nofollow for the JSON probes (inline with `receipts/analysis-full.txt`, "WRITE-OPEN"):
  - P17 `--json o/hl` (hardlink): `openat(…"hl", O_WRONLY|O_CREAT|O_NONBLOCK|O_NOFOLLOW…)` ok → `fstat` nlink=2 → `close`. No `ftruncate`, no write. Refused JSON-HARDLINKED.
  - P10a `--json fifo`: open fails ENXIO; P10b `--json dir`: open fails EISDIR.
  - P11 `--json /dev/null`: `openat(4</dev>, "null", O_WRONLY|O_CREAT|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC, 0644) = 3</dev/null>`, then `fstat` (S_IFCHR), then `close(3)`, `close(4)`, `write(2, "REFUSAL JSON-NOT-REGULAR: /dev/null is not a regular file")`. No write to fd 3, no ftruncate.
  - P18 `--json ro/o.json`: open fails EACCES (`ro` is 0500).
  - P15/P16 (`--json` equal to record, or inside measured tree) refuse before any open: no open of `ok` or `r/o.json` with write flags.
- `ftruncate`/`truncate` syscalls in the refusal-sites trace: 0.

drift-order (`r41-drift-record-order.strace`, 240 write-open events): all targets are inside `…/work/r41-drift-record-order/souji-r41-order.*/` (git init/add/commit/config/hook samples, `index.lock`, `record-*.tsv`, `.git/objects/*/tmp_obj_*`), or relative paths issued by git processes whose cwd was chdir'd into the scratch repos (52 `chdir` calls into `…/plain-root/alpha`, `…/beta`, `…/rootrepo`). No `--json` path exists in this fixture. `ftruncate`/`truncate`: 0.

Both fixtures never open a path outside `--work` for write, except `/dev/null` (section 5) and the fixture's own stdout redirect files under `$S/strace/` (scratch).

### 2. Every chmod / chown

- refusal-sites: `chmod(".../o/denied", 000)`, `chmod(".../o/ro", 0500)`, `chmod(".../o/ro", 0700)` (the `finally` restore). All in `--work`.
- drift-order (20 calls): `chmod` on `plain-root/{alpha,beta}/.git/config`, `.git/config.lock`, and `rootrepo/.git/config(.lock)` and `rootrepo/alpha/.git/config(.lock)` to 0644/0744 by git itself (config write path). All in `--work`.
- No chown/fchown/lchown calls in either trace.

### 3. Every child process

refusal-sites: 1 top-level `execve("/usr/bin/python3", fixture…)`; 22 vfork children, 21 of which exec the tool (`python3 -B tools/souji-worktree-drift.py …`, the 21 probes) and 1 of which is `git rev-parse` issued by the tool for the `.git`-file probe (P14). Successful execve binaries: `/usr/bin/python3` (22), `/usr/bin/git` (1). Failed execve attempts: 264, all PATH-probing `python3`/`git` through `/run/user/1000/fnm_multishells/…`, `/home/vgpnk/.local/share/mise/…`, etc. before `/usr/bin/python3` (both fixtures and the tool resolve their interpreter through `PATH`, not `sys.executable`).

drift-order: 64 vfork/clone children; successful execs `/usr/bin/git` (44), `/usr/bin/python3` (13: fixture + 12 tool invocations, matching `cases=12`), `/usr/lib/git-core/git` (4: `git maintenance run --auto --quiet --detach`, spawned by `git commit` inside `make_repo`). Detached maintenance children: pids 3287941, 3287978, 3287985 exit 0; their last file activity is in the scratch repo and precedes the fixture's `rmdir` of its scratch tree (trace line ~35921); post-rmdir write-class syscalls referencing `work/`: 0.

Signals: `SIGCHLD` only in normal runs; no `kill`/`tgkill` calls by either fixture or tool.

### 4. Nothing created or modified outside `--work`

- strace: the complete set of absolute paths in write-class calls (open-w, mkdir, mknod, symlink, link/linkat, unlink, rename, chmod, rmdir) is inside `$S/work/`, plus `/dev/null` and the scratch stdout files. Relative paths resolve, via chdir, inside the scratch repos.
- Lane: `git -C <lane> rev-parse HEAD` → `1d41c13574db80fdd9a4bde490b712da7ce2a85f` after the runs; the three file blob hashes are unchanged (85f3aca…, ccfb424…, fd72b2bb…). The sweep window has no lane entries outside peers' `.ufo/waves/round-41/w2/` directories.
- Sweep: 0 overlap between the 330 window entries and our strace path set (receipts `sweep-window.txt`, `analysis-full.txt`).

### 5. /dev/null

Literal acceptance ("/dev/null is never written") is not met; the precise facts are:
- refusal-sites: 20 `write(1</dev/null>, …)` calls, 4 per child, from the 5 tool children that reached the SUMMARY print (pids 3286117, 3286221, 3286331, 3287332, 3287479). Payload: `DRIFT\tABSENT…`, `SUMMARY record=…`, newlines. Cause: the fixture runs every probe with `stdout=subprocess.DEVNULL` (trace `dup2(3</dev/null>, 1</…/strace/r41-refusal-sites.stdout>)` in the vfork children), so the tool's stdout goes to `/dev/null` by design.
- refusal-sites: 22 `openat("/dev/null", O_RDWR…)` (21 from the fixture's `DEVNULL` redirections with O_CLOEXEC, and one unflagged O_RDWR by a child at line 26771, pid 3286917; [INFERENCE]: std-fd sanitizing during child startup; no data write follows it).
- refusal-sites: one `open(…"null", O_WRONLY|O_CREAT|O_NONBLOCK|O_NOFOLLOW)` by the P11 `--json /dev/null` guard: opened, fstat-refused, closed; no data write and no ftruncate. This is an open-for-write of a character device; it is not a write of data.
- drift-order: 0 `write(…/dev/null)` calls; `/dev/null` is opened O_RDONLY (git's `GIT_CONFIG_GLOBAL=/dev/null` reads) and O_RDWR for fd sanitizing only.
- Detached git child: `dup2`/`close` on `/dev/null` for stdio daemonizing, no data writes.

### 6. SIGTERM mid-run cleanup

- The fixtures install no SIGTERM handler (SigIgn for signal 15 not set), so SIGTERM terminates the interpreter immediately; Python's `try/finally` (chmod restore + `shutil.rmtree`) never runs. Trace: no `rmdir`/`unlinkat` of the run tree after the SIGTERM line in either term trace.
- term-refusal-sites leftover in `--work` (26 entries): `tmpfvh35ndz/o/ro` `dr-x------` (500), `o/denied` `----------` (000), `o/ok`, `o/loop`, `o/dir`, `o/hl`, `o/hl2`, `o/dup`, `root/r/.git`, `gd/…`.
- term-drift-record-order leftover (91 entries): `souji-r41-order.*/plain-root/alpha/.git/…` and beta/rootrepo trees with sample hooks and config.
- Orphan: in term-drift, tool child pid 3321189 kept running after the fixture was killed; it wrote its REFUSAL/traceback text to the now-closed stderr pipe (`EPIPE`, trace lines ~9675–9700) and exited 120 via SIGPIPE. It performed no file-mutating syscalls after the kill. The driver's `pgrep` check at 1 s found 0 live tool children, which is consistent with the trace.
- Permissions did not block removal: `rm -rf` of the scratch root (including the 000 and 0500 leftovers) returned rc=0.

### 7. SIGINT (Python-handled) cleanup

Passes: `KeyboardInterrupt` → `finally` → `shutil.rmtree`; `rmdir` of the run tree returns 0; leftover 0 for both fixtures; tool children 0. (The fixture then re-raises SIGINT on exit, hence rc=-2.)

## Findings and residuals

1. SIGTERM leaves the run tree behind (inside `--work` only). Not an escape, but cleanup is not guaranteed.
2. The `/dev/null` sentence is inaccurate: tool stdout goes to `/dev/null` by the fixture's `stdout=DEVNULL`, so the tool's output is discarded, and that is the only data write to `/dev/null`.
3. Residual tool-side observation (not part of the claim): `open_nofollow` opens the `--json` target `O_WRONLY|O_CREAT` before its `S_ISREG` check. For a character device it therefore performs an open-for-write before refusing. No data is written (verified), but a `stat`-first check would avoid the open entirely.
4. The fixtures and the tool resolve `python3`/`git` through `PATH`, so the interpreter run is environment-dependent (264 failed exec probes per refusal run are harmless). Noted, not a safety defect.

## Smallest remediation (not applied; read-only seat)

- Fixture (`r41-refusal-sites.py`, `r41-drift-record-order.py`): install `signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))` at the top of `main`/`run_cases` so the existing `finally` runs; alternatively document that SIGTERM leaves the `--work` tree.
- Fixture stdout: either redirect tool stdout to a file under the run tree instead of `subprocess.DEVNULL`, or correct the acceptance wording to "no `--json` write to /dev/null; tool stdout is discarded to /dev/null by the fixture".
- Tool (optional hardening): `os.stat(json_target)` and refuse non-regular targets before the `O_WRONLY|O_CREAT` open.

## Limits

- No full pre-run manifest: `/tmp` alone is 101 GB and the combined find yields 8.7 million entries; the review used the marker-based sweep plus strace, which is the primary evidence here.
- Fleet activity was concurrent; sweep entries were attributed by absence from the strace path set, not by proving their origin.
- The SIGTERM test sent the signal to the fixture pid it spawned; no other process was signalled.

## Tooling record

- No tool installed or upgraded. `strace` 7.2 (`/usr/bin/strace`) was pre-existing and used. No pacman transaction, no `~/.local/bin` change.
