# R41w2critic04 — hermeticity attack on the landed C3 fixture

Scope: attack `tests/fixtures/r41-refusal-sites.py` at a1144120611b00091ac4839559d8ebf38aa9a83a (candidate R41executor04, sha256 f32022e28fe2293af44d7fee1cb73f9a39221fbcc534022b78d77a8c96551978, 3725 bytes), driven against the pinned tool `tools/souji-worktree-drift.py` at tip 1d41c13574db80fdd9a4bde490b712da7ce2a85f (sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6, matches the preregistered pin). Identity: uid 1000 (vgpnk), not root. Python 3.14.8. Default umask 0022.

Inputs were extracted read-only with `git -C <lane> show <rev>:<path>` into my scratch. Only read-only git calls were made (`show`, `rev-parse`, `status --porcelain`, `cat-file`). `git -C <lane> status --porcelain -- tests tools census corpus` was empty after all runs. No tool installed or updated.

Driver note: attacks 1-9 and 14 ran from inline Python cells (`subprocess` with explicit `env=` dicts, `sh -c 'umask N; exec ...'` for umask). The cell source was not saved as a file; each case's exact invocation is stated below. Attacks 11-14 are saved as `kill_matrix.py` and `followup.py`. Attack 10 is a saved strace command. Attack 15 is a saved counter command.

Every fixture run was `python3 -B FIXTURE --tool TOOL --work WORK`, with FIXTURE and TOOL absolute unless stated. "21/21" = `SUMMARY probes=21 pass=21 fail=0`.

## Results per attack

1. **Two concurrent runs, distinct --work, different cwds** (`cwd other` and `/`, `env -i PATH=... TMPDIR=<work>`). Both 21/21, rc 0, stderr empty, both --work dirs empty afterward.
2. **Two concurrent runs, SAME --work.** Both 21/21, rc 0, --work empty afterward. mkdtemp gives each run its own tree.
3. **umask 077 and umask 000** (`sh -c 'umask N; exec python3 -B ...'`). Both 21/21, rc 0, --work empty.
4. **Stress: TMPDIR and --work both containing spaces; three concurrent runs** (A: umask 000, cwd `/`, own work; B: umask 077, cwd TMPDIR, shared work with C; C: umask 000, cwd `/`, shared work with B). `stress-{A,B,C}.txt`: each `SUMMARY probes=21 pass=21 fail=0 EXIT=0`, stderr empty, both work dirs and TMPDIR empty afterward.
5. **HOME unset.** `env -i PATH=...` (no HOME), and `env -u HOME python3 -B ...`. 21/21, rc 0.
6. **Hostile git env inherited** (`GIT_DIR=/nonexistent/gitdir`, `GIT_CONFIG_GLOBAL=/nonexistent/cfg`, `GIT_TRACE=<scratch file>`, TMPDIR with spaces, HOME absent). 21/21, rc 0. The GIT_TRACE file was NOT created and TMPDIR was left empty. The tool's `git_env()` whitelist strips GIT_* as designed.
7. **Pre-existing stale chmod-000 file and chmod-000 directory (holding a 0500 subdir with a file) in --work.** 21/21, rc 0. The stale entries were untouched and still listed afterward (`stale-dir`, `stale-file`).
8. **Relative paths.**
   - Relative --work and relative --tool, cwd = scratch `cwd other`: 21/21, rc 0, work emptied.
   - Absolute --tool with relative --work, cwd `/`: 21/21, rc 0, work emptied.
   - **Relative --tool, cwd `/` (tool not there):** every probe prints `FAIL rc=2`, `SUMMARY probes=21 pass=0 fail=21`, rc 1. No crash, but results depend on cwd when --tool is relative. The counter always passes an absolute tool path (`run_fixture()` in c3-counter.py), so the measurement path is unaffected.
9. **Nonexistent --work** (`.../does-not-exist`): Python traceback `FileNotFoundError` from `tempfile.mkdtemp`, rc 1, nothing created. The fixture does not validate --work. The counter would read this as a pristine crash (rc 1, crash=True). Not reachable from the counter's own invocation.
10. **Strace of the fixture**, command `strace -f -qq -e trace=openat,open,creat,mkdir,mkdirat,chmod,fchmodat,unlink,unlinkat,rename,renameat,renameat2,link,linkat,symlink,symlinkat,truncate,ftruncate -o logs/strace-fixture.txt python3 -B FIXTURE --tool TOOL --work <dir with spaces>`. Receipt `strace-fixture.txt` (3720 lines), rc 0, `SUMMARY probes=21 pass=21 fail=0`.
    - The fixture performs no open/create/chmod/unlink outside `--work`.
    - Write-class syscalls outside the work tree are only: (a) the tool's `--json /dev/null` probe (P11), which opens `/dev/null` with `O_WRONLY|O_CREAT` by design and then refuses on fstat (tool-side, no effect); (b) interpreter stdio on `/dev/null`.
    - Nothing touched /tmp, $HOME, a cache or __pycache__.
    - chmod calls hit only the expected paths: `o/denied` to 000, `o/ro` to 0500, then `o/ro` back to 0700 in `finally`.
    - The P18 open of `o/ro/o.json` returns EACCES and creates nothing.
11. **Kill mid-run** (`kill_matrix.py`, receipt `kill-matrix.json`, 24 trials). The driver runs the fixture in its own session (`start_new_session=True`) with `slow_tool.py` as the --tool (sleeps 0.5 s, then exec's the pinned tool), so the run is held inside the probe loop after `denied` and `ro` are chmod'ed. It signals the process group (only processes it spawned), then runs cleanup as the same user.
    - SIGKILL at 0.3, 1.5, 4.5, 9.5 s: rc -9, leftover 26 entries each, orphans 0, `rm -rf` ok.
    - SIGTERM at 0.3, 1.5, 4.5, 9.5 s: rc -15, leftover 26 entries each, orphans 0, `rm -rf` ok.
    - SIGINT at 0.3, 1.5, 4.5, 9.5 s: rc -2, leftover 0. The `finally` ran (`o/ro` restored to 0700, tree removed).
    - 12 random SIGKILL trials at 0.13 to 1.13 s with no shim: 11 killed mid-run, each with 26 leftover entries, `rm -rf` ok. 1 completed before the kill (rc 0, leftover 0).
    - Sample leftover after SIGKILL at 1.5 s: `0o0 tmp.../o/denied`, `0o500 tmp.../o/ro`, `0o644 tmp.../gd/HEAD`, and `0o644` entries under `o/` (`dup, empty, fifo, gd, hl, hl2, junk, ok, out`), 26 entries in all including directories.
12. **Strict cleanup after SIGKILL** (`followup.py` F1). The leftover tree contains `o/denied` (mode 0000) and `o/ro` (0500). `shutil.rmtree(W)` WITHOUT ignore_errors: OK, path gone. Removing an entry needs write permission on its parent, not on the entry, so mode-0 files and an empty 0500 dir do not block cleanup. `rm -rf` also succeeded in every kill trial (attack 11).
13. **Parent-only kill** (`followup.py` F2: SIGKILL only the fixture pid, shim child alive). The shim child survived the parent kill (`children_alive_after_parent_kill=[3278083]`). The test cleaned W while the child was still alive. After 2.5 s the child had exited (`children_alive_after_2_5s=[]`) and recreated nothing under W (`recreated_under_W_after_cleanup=false`). Its tool run refuses on the missing record, so nothing is written.
14. **Concurrent kill** (`followup.py` F3). Run A (shim) was SIGKILLed while run B (real tool) shared its --work. Run B: rc 0, `SUMMARY probes=21 pass=21 fail=0`, stderr empty. The only leftover was A's mkdtemp tree (`tmpx35rt7xe`), so B was unaffected.
15. **Committed counter, three concurrent instances with separate --scratch** (`counter-{A,B,C}.txt`). Command: `python3 -B <lane>/census/round-41/c3-counter.py --root <lane> --rev a1144120611b00091ac4839559d8ebf38aa9a83a --scratch <own scratch>`, all three in parallel. Each prints `PRISTINE ok rc=0 probes=21 crash=False dup=False summary=(21, 21, 0)` and `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=f32022e28fe2`, then `EXIT=0`. Scratch dirs were left empty.

## Left behind

- Under `--work` after a SIGKILL or SIGTERM mid-run (attack 11): one mkdtemp tree of 26 entries, including `o/denied` at mode 0000 and `o/ro` at 0500. Nothing reaps it. Cleanup succeeds (attacks 11 and 12), so this is junk, not a cleanup block.
- No leftover after normal exit, SIGINT, or any completed run.
- In the lane: nothing (`git status --porcelain -- tests tools census corpus` empty).
- Fleet, state, watchdog, operator config: nothing written.
- Scratch `/fast/scratch/hyaku/souji-r41/R41w2critic04/`: deleted before yield (receipts copied here first).

## Verdict

**PASS for hermeticity of the landed fixture.** No attack changed a probe result, leaked state between runs, touched anything outside `--work`, read HOME or the caller's GIT_* environment, or depended on umask or a pre-existing stale entry. The one lasting artifact is the 26-entry tree left by SIGKILL or SIGTERM mid-run. Its chmod-0 file and 0500 directory do NOT block cleanup (`rm -rf` and strict `shutil.rmtree` both succeed).

Named limits for the round lesson. None is claim-breaking and none is fixed here; the fixture is frozen by the pre-registration.
- L-a: SIGKILL/SIGTERM leave a work tree. There is no reaper, and `finally` runs only on normal exit or SIGINT. Interrupted runs accumulate under --work.
- L-b: a relative `--tool` resolves against the caller's cwd. A wrong cwd gives 21 FAIL lines, not a usage refusal. The counter passes an absolute path.
- L-c: a nonexistent `--work` gives a traceback (rc 1), not a usage refusal.
- L-d [INFERENCE, untested]: the EACCES probes (P02a, P18) rely on the process lacking DAC override. A process with CAP_DAC_OVERRIDE and a non-root uid would likely FAIL them. The counter refuses uid 0 only.
- L-e [untested]: two counters given the SAME --scratch would share `pristine.py`/`fixture.py`/`mut-*.py` names. The L1 uses one scratch per run.

## Receipts (in this seat dir)

`.ufo/waves/round-41/w2/R41w2critic04/`: `inputs.sha256` (sha256 of fixture.py and tool.py), `fixture.py`, `tool.py`, `kill_matrix.py`, `followup.py`, `slow_tool.py`, `kill-matrix.json`, `followup.json`, `strace-fixture.txt`, `counter-A.txt`, `counter-B.txt`, `counter-C.txt`, `stress-A.txt`, `stress-B.txt`, `stress-C.txt`.
