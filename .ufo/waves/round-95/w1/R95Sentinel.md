# R95Sentinel — safety and robustness of the widened crash sentinel and the probe's new timeout

Seat: R95Sentinel (sentinel). Lane: souji-shokunin. Round 95, wave 1.
Scope of this seat: the C1 crash sentinel (widened channels, tool id, scope over non-counter processes) and the
C2 probe's new `--timeout` (process-group escape, orphan processes). The predicates themselves were executed
once each as ground truth; this seat does not own the claims.

Lane state observed: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` =
`59fd7be028a7eab071ff8109ad7a1eb10b5f493c` (commit F, the preregistration alone), lane base
`93c3ef13a9eb9678483518562f3692124db714c2`. Python 3.14.8.

## Ground truth executed by this seat (read-only against the lane)

| run | command | result |
|---|---|---|
| C1 after | `python3 -B census/round-95/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root /home/vgpnk/Projects/shokunin --work <empty> --jobs 5 --ids census/round-95/c1-targets.json` | `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`; `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`; all five crash fixtures `killed=errored`; EXIT 0 |
| C1 control | same with `census/round-95/c1-control-r94-rule.py` | `SEARCH-SUMMARY ... errored=2 killed=5 survived=3`; h-sysexit/h-osexit/h-sigkill `killed=yes`, h-atexit/h-thread `killed=no`; EXIT 0 |
| C2 after | `python3 -B census/round-95/c2-setup-arms.py --probe census/round-95/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>` | `ARMS-SUMMARY arms=16 conform=16`, all 16 arms `conform=yes` (S9/S10/S11/S12/S13/S14 all `exit=2`); EXIT 0 |

Receipts: `.ufo/waves/round-95/w1/R95Sentinel/exp/C1-predicate.out`,
`.ufo/waves/round-95/w1/R95Sentinel/exp/C1-control.out`,
`.ufo/waves/round-95/w1/R95Sentinel/exp/C2-arms.out`.
No falsification of either claim's numbers was found. All findings below are ROBUSTNESS findings about the
instruments, not counterexamples to the counted quantities.

## Findings

### F1 — HIGH — the widened sentinel's exit-70 path can DEADLOCK instead of exiting 70

The r95 sentinel replaces `os._exit` with `_souji_os_exit`, which calls `_souji_crash`, which does
`sys.stderr.write(...)` and then `sys.stdout.flush()` / `sys.stderr.flush()` before the real `os._exit(70)`.
`os._exit` is documented as async-signal-safe: it performs no allocation and no I/O, so it may be called from a
signal handler. The replacement is not: it takes the stderr lock and writes.

Reproducer (deterministic, run 3x): `exp/E3c_signal_deadlock.py` and `exp/E7_thread_deadlock.py`.

    [plain  ] rc=0 elapsed=1.0s        # os._exit(0) from a SIGALRM handler: leaves at once
    [hooked ] rc=HUNG elapsed=12.0s    # same child under the r95 sitecustomize: HANGS

Mechanism: the main thread is blocked inside `sys.stderr.write()` on a full, undrained pipe, so it holds the
`TextIOWrapper` lock. The signal handler runs on the main thread and calls `os._exit(0)`; the replacement tries
to write to the same stderr and blocks on the lock the interrupted frame still holds. The plain path never
touches stderr, so it leaves immediately. The same deadlock reproduces when the `os._exit` comes from a worker
thread while the main thread holds the stderr lock (`exp/E7_thread_deadlock.py`:
`[thread os._exit plain] rc=0 elapsed=1.0s` vs `[thread os._exit hooked] rc=HUNG elapsed=12.0s`).

A narrower variant needs no signal at all: with only ~26 bytes of headroom left in an undrained stderr pipe, the
plain `os._exit(1)` returns `rc=1` immediately, while the hooked child HANGS and never reaches exit 70
(`exp/E18_headroom.out`):

    plain  fill=65510 cap=65536 rc=1    t=0.0s crash_marker=False
    hooked fill=65510 cap=65536 rc=HUNG t=5.0s crash_marker=False

Why this matters for the lane: the counter's stderr is a PIPE owned by the search (`subprocess.PIPE`), and the
search drains it with `p.communicate()`. A counter that crashes while its stderr pipe is full and undrained
would hang instead of exiting 70, and the search would score it `hung` (state `hung`, excluded from `scored`)
rather than `errored`. The r94 sentinel replaced only `sys.excepthook`, whose crash path also flushed but never
replaced `os._exit`, so this window is new in r95.

Smallest remediation: make the crash path signal-safe — do the diagnostic write best-effort with a non-blocking
write to a raw fd (e.g. `os.write(2, b"...")`) and never take the buffered-writer lock; or restore `os._exit`
inside a `try/except BaseException` and fall back to a bare `os._exit(70)` if the write cannot complete.

### F2 — HIGH — the C2 probe's `--timeout` does not end the probe: a fixture that escapes the process group hangs it forever

The r95 probe starts a fixture with `start_new_session=True` (so the fixture leads its own session) and, on
timeout, does `os.killpg(p.pid, SIGKILL)` followed by `p.communicate()` with NO timeout. `killpg` reaches the
fixture's group only. A fixture that leaves that group — a descendant calling `os.setsid()`, or the fixture
itself — is not killed, and it keeps the fixture's stdout pipe open, so the second `p.communicate()` blocks
forever. The probe does not end.

Reproducer: `exp/E4b_setsid_escape.py` (deterministic, run 2x) and `exp/E20_composed.py`:

    [X1-setsid-escape] probe rc=PROBE-HUNG elapsed=36.0s (the probe did not end 30s after its own --timeout)
        surviving fixture processes: [4115695]
    [X2-plain-group]   probe rc=2 elapsed=0.1s        # control: a fixture that stays in the group
        surviving fixture processes: []

The escaped process also survives the arms counter's own `--arm-timeout` kill, because the arms counter kills
the PROBE's group (`os.killpg(p.pid)`) while the fixture is in a different group
(`exp/E19_orphan.py`, `exp/E20_composed.py`):

    [E20] probe alive 10s after its own --timeout 5s: True  (a hung probe)
    [E20] ORPHANS left after the arms counter's arm-timeout kill: [1751199]

So the composed failure is: a fixture that escapes its group (a) hangs the probe past its `--timeout`, and
(b) leaves an orphan process that the arms counter's group kill does not reap.

Why this matters for the lane: this is exactly the failure the C2 claim says is fixed. The prereg's C2 wording
is about the frozen S12 fixture (a plain `time.sleep` loop), which stays in its group and is killed correctly —
the predicate passes. But the prereg's STATED LIMITS (i) explicitly leaves "a fixture that escapes its process
group" to the wave, and in that open area the r95 probe does NOT end: it hangs, and the arms counter's
`--arm-timeout` (300 s) is what finally stops it, leaving the escaped fixture orphaned.

Smallest remediation: after `os.killpg(p.pid, SIGKILL)`, close the pipes and give the second `p.communicate()`
a bounded timeout instead of none; and reap any surviving descendant of the fixture (e.g. by scanning
`/proc` for the fixture's session id) before raising `Fatal`.

### F3 — MEDIUM — the sentinel changes the exit status of processes that are NOT the counter

The sitecustomize is on `PYTHONPATH` for the whole harness subtree, so every Python process under the harness
is affected, not just the counter. The harness itself is under the sentinel (proven in `exp/E15_final2.py`,
part P2: a wrapper sitecustomize that prints a marker shows the marker inside the real harness's own stderr).

Consequences measured (`exp/E1b_scope.py`, `exp/E12_buffer_ppe.py`):

    [plain ] S-A os._exit(0)          rc=0   stderr=''
    [hooked] S-A os._exit(0)          rc=70  stderr='SOUJI-R95-CRASH os._exit(0)'
    [plain ] S-B os._exit(3)          rc=3   stderr=''
    [hooked] S-B os._exit(3)          rc=70  stderr='SOUJI-R95-CRASH os._exit(3)'
    [plain ] S-D fork+os._exit        rc=0   stdout='child status: 0'
    [hooked] S-D fork+os._exit        rc=0   stdout='child status: 17920'   # 17920 = 70 << 8
    [plain ] S-E monitor id 3         rc=0   stdout='use_tool_id(3): OK'
    [hooked] S-E monitor id 3         rc=4   stdout='use_tool_id(3): ValueError: tool 3 is already in use'

Three distinct effects: (i) a legitimate `os._exit(0)` becomes exit 70, so a helper that exits cleanly is now
indistinguishable from a crash; (ii) the exit status of a FORKED child changes (0 -> 70), so a parent that
checks a child's status sees a spurious failure; (iii) a Python helper that wants `sys.monitoring` tool id 3 is
refused — the sentinel holds id 3 in every process, so the tool id is consumed process-wide, and a coverage-like
tool dies with `ValueError: tool 3 is already in use`.

Also relevant: the sentinel's crash path FLUSHES stdout before exiting, so it preserves output that a plain
`os._exit` would discard — and, in a forked child, it duplicates the parent's inherited buffer
(`exp/E14_clean_buffer.out`):

    [buffer+os._exit plain ] rc=0 stdout=''                      # plain os._exit discards the buffer
    [buffer+os._exit hooked] rc=70 stdout='BUFFERED-NOT-FLUSHED'  # the sentinel keeps it
    [fork-dup       plain ] rc=0 stdout='PARENT-BUFFERED-TEXT|PARENT-AFTER'
    [fork-dup       hooked] rc=0 stdout='PARENT-BUFFERED-TEXTPARENT-BUFFERED-TEXT|PARENT-AFTER'   # duplicated

Why this matters for the lane: the counter under test is the only Python process whose status the search reads,
so the measured verdict is unaffected (F1–F3 do not change the ten verdicts: the after and control summaries
above are exactly the claimed ones). But the lane's own harness, the C1 search's `sitecustomize` hook directory,
and any future Python helper spawned under the harness inherit all of this. The duplication is latent for the
frozen lane — the harness does not fork, and its own per-mutant output shows no duplicated line (mutant `m0008`
of the after run yields exactly 66 `ROW` lines, no duplicates) — but any helper that forks after writing to
stdout and then crashes will have its parent's buffer written twice.

Smallest remediation: scope the sentinel to the counter process (e.g. install it from a wrapper the search runs
around the counter, not from `PYTHONPATH` for the whole tree), and make the `os._exit` replacement preserve the
caller's status for `os._exit(0)` rather than forcing 70.

### F4 — MEDIUM — the sentinel degrades SILENTLY when no monitoring tool id is free

The hook loops `for _souji_id in range(3, 6)` and takes the first free id. If ids 3, 4 and 5 are all taken, it
prints `SOUJI-R95-SENTINEL no free sys.monitoring tool id` to stderr and continues WITHOUT the RAISE callback.
The SystemExit leg then stops working, but the process keeps running and the sentinel looks installed.

Measured (`exp/E9_unraisable_toolid_orphan.py`, `exp/E13_final.py` part d):

    [E10 ids 3+4 taken   ] owners 3/4/5: other-tool other-tool souji-r95-sentinel   # the sentinel took id 5
    [E10 ids 3+4+5 taken ] owners 3/4/5: other-tool other-tool other-tool
                           err='SOUJI-R95-SENTINEL no free sys.monitoring tool id'
    [d fail-closed sysexit ] rc=1 (search wants 70)  err='SOUJI-R95-SENTINEL no free sys.monitoring tool id'
    [d fail-closed declared] rc=1 (search wants 1)

Two points. First, id 5 is `sys.monitoring.OPTIMIZER_ID` (CPython docs, bundled at
`census/round-95/srcs/monitoring.html`: `DEBUGGER_ID = 0, COVERAGE_ID = 1, PROFILER_ID = 2, OPTIMIZER_ID = 5`),
i.e. a RESERVED id — the sentinel takes it when 3 and 4 are busy, and `use_tool_id` only refuses an id that is
IN USE, not a reserved one. Second, the failure is fail-closed at the search level: the search's own CHECK script
runs the same hook, so with no free id the `sysexit` check exits 1 instead of 70 and the search refuses to run
(`C1-SEARCH-FATAL: crash sentinel check sysexit`). That is correct behaviour, but it means the tool-id
shortage turns a calibration run into a hard failure rather than a skip, and the sentinel's own id-taking order
can collide with the reserved optimizer id.

Why this matters for the lane: the C1 search and the counter both run under the same hook, so an environment that
already holds ids 3–5 (a debugger, a profiler, a coverage tool with `--branch` on a `sys.monitoring` build)
makes the whole calibration run exit 2 at the precondition rather than degrade. Low likelihood, high blast radius.

Smallest remediation: restrict the loop to the two unreserved ids (3 and 4) and, when neither is free, make the
sentinel fail LOUDLY in a way the search's precondition already treats as fatal, plus skip id 5 outright.

### F5 — LOW — the sentinel's `sys.unraisablehook` replacement turns a BENIGN finalizer error into a crash

Replacing `sys.unraisablehook` makes an exception raised inside a `__del__` (which CPython deliberately ignores)
fatal: the process exits 70 instead of continuing (`exp/E9_unraisable_toolid_orphan.py`):

    [E9 unraisable plain ] rc=0  stdout='CONTINUED-AFTER-GC'  stderr='Exception ignored while calling deallocator...'
    [E9 unraisable hooked] rc=70 stdout=''                    stderr='Exception ignored while calling deallocator...'

A GC-time error in an unrelated object now decides the mutant's verdict (`errored` instead of `survived`/`killed`).
The r95 rule counts "ROW rc=70 or negative rc" as `errored`, so a benign finalizer would be scored as a crash
channel rather than a survivor — a false `errored` for the search's calibration, though it does not create a
false survivor.

Smallest remediation: restrict the `sys.unraisablehook` replacement to the `atexit`-callback route the claim
names, or keep the default hook for `__del__`-originated unraisables.

### F6 — LOW — the sentinel's SystemExit leg depends on `sys.modules["__main__"].__file__`, so it does not fire under `python -c`

`_souji_raise` compares the RAISE callback's `code.co_filename` against
`sys.modules.get("__main__").__file__`. With `python -c` there is no `__main__.__file__`, so the leg never arms
(`exp/E13_final.py` part c):

    [c abs  ] rc=70 stderr='sysexit-in-function\nSOUJI-R95-CRASH SystemExit first raised in helper() of the main script'
    [c rel  ] rc=70 stderr='sysexit-in-function\nSOUJI-R95-CRASH SystemExit first raised in helper() of the main script'
    [c -c   ] rc=1  stderr='x'

Both file-based invocations (absolute and relative) work, because CPython 3.14 absolutises `__main__.__file__`.
The `python -c` case exits 1 (the plain SystemExit status) instead of 70. The prereg's C1 STATED LIMITS (iii)
already lists `python -I`/`-S` as not covered; `python -c` is the same family and is likewise not exercised by
the frozen fixtures. Not a defect against the claim; recorded so the L1's limit list can name it.

### F7 — NO FINDING — which rule leg fires for which channel (verified against the real receipts)

The r95 kill rule scores a mutant `errored` on three signals: harness exit 70, harness exit below 0, or any `ROW`
line reading `rc=70` or a negative `rc`. The after-arm receipts show each crash channel arriving on its own leg:

* h-osexit: the harness's `ROW` lines carry `rc=70` (the sentinel's exit status, seen by the harness) — the
  `rc=70` leg. `SEARCH h-osexit line=524 killed=errored rc=1`; the mutant's `harness.out` has 56 `rc=70
  match=error` and 10 `rc=70 match=no` ROW lines.
* h-sigkill: the harness's `ROW` lines carry `rc=-9` (SIGKILL, seen by the harness) — the negative-rc leg
  (S363). The mutant's `harness.out` has 56 `rc=-9 match=error` and 10 `rc=-9 match=no` ROW lines.
* h-sysexit: `ROW ... rc=70` again, via the sentinel's `SystemExit` leg.

Note that in both cases the harness's own exit status is 1 (it reports the mismatch/errors it saw), and the
search's `SEARCH ... rc=1` is the harness's status, not the counter's — the crash is carried by the `ROW` lines.
This is exactly the S363 negative-rc rule doing its job, and it is the mechanism the claim describes. No defect,
recorded so the L1 can see the leg-to-channel mapping was checked rather than assumed.

### F8 — NO FINDING — the instruments do not write under /tmp

Both instruments refuse a `/tmp`, `/var/tmp` or `/dev/shm` `--work` and keep all scratch under `--work`:

* the C1 search: `if v and os.path.realpath(os.path.abspath(v)).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))` for
  `--work` and `--emit` (`census/round-95/c1-survivor-search.py:303`);
* the C2 probe: the same guard on `--work` (`census/round-95/c2-forgery-probe.py:134`);
* the C2 arms counter: the same guard on its own `--work` (`census/round-95/c2-setup-arms.py:71`).

The S13 arm NAMES an absent `/tmp` path and never creates it: `tmp_work = f"/tmp/souji-r95-arm-S13-{os.getpid()}-absent"`
is checked with `os.path.lexists` and passed to the probe, which refuses it (the probe's guard fires before
`os.makedirs`). Measured: `ls /tmp/souji-r95-arm-S13-*` -> "No such file or directory" after a full 16-arm run, and
the S13 arm's own receipt shows `C2-FORGERY-FATAL: --work under /tmp, /var/tmp or /dev/shm` (no directory created).

Snapshot audits of `/tmp`, `/var/tmp` and `/dev/shm` before and after a REAL run of each instrument, with a
private `TMPDIR` set, found nothing outside `--work`:

    [C2-arms] rc=0 new_tmp_entries=[] modified_tmp_entries=[]
       S13 /tmp path present after the run: []

    [E22 C1 search] rc=0 elapsed=32s
        new tmp entries:     []
        modified tmp entries:[]
        TMPDIR contents:     []
        /tmp suouji entries: []
        work tree top level: ['check', 'hook', 'm0000', ..., 'm0009']
        hook dir: ['sitecustomize.py']

The C1 search's `--work` holds only the two directories it creates (`hook/`, `check/`) and the ten per-mutant
directories; the `hook/` directory holds exactly one file (`sitecustomize.py`) — no `__pycache__` is written into
the work tree. Receipts: `exp/E21_tmp_audit.out`, `exp/E22_c1_tmp_audit.out`.

### F9 — NO FINDING — the git-hook / helper reach

The sentinel does reach Python git helpers: the harness and the counter both spawn `git` with
`-c core.hooksPath=/dev/null`, and the lane has no live hooks (`.git/hooks` holds only `*.sample`), so no hook
runs in this round. The mechanism is nonetheless live — a scratch repo with a Python `pre-commit` hook shows the
hook's own process running under the sentinel (`exp/E8_githook_toolid.out`):

    [git-hook plain ] HOOK os._exit is _exit          HOOK excepthook is excepthook          HOOK tool3 owner: None
    [git-hook hooked] HOOK os._exit is _souji_os_exit  HOOK excepthook is _souji_excepthook  HOOK tool3 owner: souji-r95-sentinel

The lane's `core.hooksPath=/dev/null` plus the absence of live hooks is what keeps this from mattering here;
a lane with a Python hook enabled would hand that hook the same altered `os._exit`, `sys.excepthook` and tool id
3 (F3). Recorded as reach, not as an active defect.

## FALSIFIES-WORDING

**NO-FALSIFICATION.** Neither claim's counted quantity, nor any sentence of the C1 or C2 CLAIM paragraphs, is
contradicted by any artifact this seat produced.

Specifically checked and NOT falsified:

* C1 "scores all five `errored` and keeps the verdicts of the five r94 targets" — reproduced exactly: after
  `errored=7 killed=2 survived=1`, with h-sysexit/h-atexit/h-thread/h-osexit/h-sigkill all `killed=errored`; the
  control gives `errored=2 killed=5 survived=3` with h-sysexit/h-osexit/h-sigkill `killed=yes` and
  h-atexit/h-thread `killed=no`. The five r94 targets' verdicts are identical in both arms
  (h-crash-late `errored`, h-crash-index `errored`, h-ok-admits-one `yes`, a491c22 `yes`, a127c26 `no`).
* C1's check line `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70
  declared=1 argparse=2` — reproduced byte-for-byte.
* C1 "the rule also scores a negative rc as errored" — the h-sigkill fixture is scored `errored` in the after
  arm exactly as claimed.
* C2 "the r95 probe ... refuses each of S9-S12 with exit 2 and a `C2-FORGERY-FATAL:` line, and conforms on the
  twelve arms the r94 probe conforms on" — reproduced: `ARMS-SUMMARY arms=16 conform=16`, every arm
  `conform=yes`, S9–S14 all `exit=2` with the fatal line present.
* C2's counted quantity "conforming arms of 16 — before 12, after 16" — the after arm is 16/16; the before arm
  is the r94 probe's 12/16, as the prereg records.

F1–F5 and F9 are robustness findings about the instruments' behaviour OUTSIDE the frozen fixtures and outside
the claims' stated scope; they are not counterexamples to a claim sentence. F2 sits in the area the prereg's
C2 STATED LIMITS (i) explicitly opens to the wave ("a fixture that escapes its process group ... are the wave's
to try") and is reported as such, not as a falsification. F4 and F6 sit in the area the prereg's C1 STATED LIMITS
(iii) opens ("signals other than SIGKILL, a signal the counter catches, C-level crashes, `python -I`/`-S`, a
non-Python child of the counter"). The L1 should record F1, F2 and F3 as narrowing amendments or as follow-up
work; this seat has not modified any filed instrument.

## What was tried, per assignment item

1. **Can the sitecustomize change the behaviour of a process that is not the counter?** Yes — measured (F3):
   `os._exit(0)` in a helper becomes exit 70; a forked child's status changes 0 -> 70; a helper wanting
   `sys.monitoring` tool id 3 gets `ValueError` and dies with rc=4; the harness itself is under the sentinel
   (proved by a marker sitecustomize inside the real harness's stderr); a Python git hook is under it too (F9).
   The counter's own verdict is unaffected.
2. **Does the exit-70 path lose buffered output, or deadlock from a thread or a signal handler?** It does NOT
   lose output — it flushes and keeps it (and duplicates the parent's buffer after a fork, F3). It DOES deadlock
   when called from a signal handler or a worker thread while another thread holds the stderr lock, and when the
   stderr pipe is nearly full (F1, three independent reproducers, deterministic on re-run).
3. **Can a fixture escape the probe's process group and survive? Does the arms counter leave processes after
   S12?** Yes to both, in the composed case: an escaping descendant survives the probe's `killpg` AND the arms
   counter's arm-timeout `killpg`, and the probe itself hangs past its `--timeout` (F2). The frozen S12 fixture
   stays in its group and is killed correctly, so the predicate passes; the orphan appears only when the fixture
   escapes. The r95 probe's `start_new_session=True` is what makes the fixture unreachable from the arms
   counter's group kill (the r94 probe used plain `subprocess.run`, so its fixture died with the probe —
   `exp/E19_orphan.out` shows `[r94-probe] ... ORPHANS after the arm-group kill: []` versus
   `[r95-probe] ... ORPHANS after the arm-group kill: [1332960]`).
4. **Do the C1/C2 instruments write under /tmp regardless of TMPDIR/--work (S13's /tmp path included)?** No
   (F8). All three refuse a /tmp-family `--work`; S13 names an absent /tmp path and creates nothing.

## Files

All receipts and reproducers are under `.ufo/waves/round-95/w1/R95Sentinel/` (text only; no clones). Scratch
(clones, work trees, hook copies) was under `/fast/scratch/hyaku/souji-r95/R95Sentinel/` and has been deleted.

* `exp/E1b_scope.py`, `exp/E1b_scope.out` — scope over non-counter processes (F3).
* `exp/E3c_signal_deadlock.py`, `exp/E3c_signal_deadlock.out`, `exp/E3c_rerun.out` — signal-handler deadlock (F1).
* `exp/E7_thread_deadlock.py`, `exp/E7_thread_deadlock.out` — worker-thread deadlock (F1).
* `exp/E14_clean_buffer.py`, `exp/E14_clean_buffer.out` — buffering / fork duplication (F3).
* `exp/E18_headroom.py`, `exp/E18_headroom.out` — near-full stderr pipe (F1).
* `exp/E4b_setsid_escape.py`, `exp/E4b_setsid_escape.out`, `exp/E4b_rerun.out` — process-group escape (F2).
* `exp/E19_orphan.py`, `exp/E19_orphan.out` — orphan after the arms counter's group kill (F2).
* `exp/E20_composed.py`, `exp/E20_composed.out` — the composed escape-then-orphan sequence (F2).
* `exp/E9_unraisable_toolid_orphan.py`, `exp/E9_unraisable_toolid_orphan.out` — unraisablehook and tool-id
  fallback (F4, F5).
* `exp/E10/E13` outputs — tool-id fallback, fail-closed check, `python -c` (F4, F6).
* `exp/E8_githook_toolid.py`, `exp/E8_githook_toolid.out` — git-hook reach (F9).
* `exp/E21_tmp_audit.py`, `exp/E21_tmp_audit.out`, `exp/E22_c1_tmp_audit.py`, `exp/E22_c1_tmp_audit.out` — /tmp
  audits (F8).
* `exp/C1-predicate.out`, `exp/C1-control.out`, `exp/C2-arms.out` — the three ground-truth runs.

Tooling: no package was installed for this seat (nothing was needed); no pacman transaction was run.
