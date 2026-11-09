# R97Sentinel — findings (souji r97, seat R97Sentinel)

Status: COMPLETE. Scope: safety and robustness of the signal-safe crash write, the /tmp guard
and the probe's timeout reap (the four numbered seat items). All work is read-only against the
lane except for the copies made into my own seat dir; the lane's `census/`, `tests/`, `tools/`
and `corpus/` were never modified. Scratch lived under
`/fast/scratch/hyaku/souji-r97/R97Sentinel/` and has been deleted; every receipt cited below was
copied into my seat dir first (paths under `.../R97Sentinel/`).

Reproducer scripts (copied to `.ufo/waves/round-97/w1/R97Sentinel/`):
- `repro_foreign_pid_kill.py` — finding 1 (foreign pid killed by the counter's T1 identity reap).
- `repro_decoy_kill.py` — finding 1, earlier variant (EARLY vs LATE decoys).
- `probe_fd_leak_measure.py` — finding 4 (probe descriptor accounting).

## FALSIFIES-WORDING

### C2 — "it signals only processes it planted"

Exact sentence (census/round-97/preregistration.txt, C2 CLAIM paragraph):

> the r97 counter census/round-97/c2-setup-arms.py reaps the T1 grandchild by argv identity
> (the arm's absolute fixture path, verified at act time; **it signals only processes it planted**)

and the same restriction repeated in STATED LIMITS (i):

> (i) Twenty arms, chosen by the L1; the reaping identity is the counter's own arm spawn (its
> absolute fixture path): **the counter never signals a pid it did not plant**, and a recycled
> argv token is guarded by the counter's own before/after identity set on this host.

**Falsified.** The counter SIGKILLs own-uid processes it did not plant.

Mechanism (`census/round-97/c2-setup-arms.py`, the T1 arm, `one()`): the identity set is
`before = _snapshot() if aid == "T1" else set()`, taken when the **T1 arm starts** — it is a
snapshot of token carriers, not a record of what the counter planted. At the END of the T1 arm the
counter SIGKILLs every own-uid process whose argv contains the arm's absolute fixture path and
whose `(pid, starttime, boot_id)` is **not** in that snapshot. Any process that acquires the token
in its argv during the ~120 s the T1 arm runs is killed, although the counter never spawned it.
The before/after set guards against pid *recycling* only; it does not establish ownership.

Reproducer: `repro_foreign_pid_kill.py` (receipt `repro_foreign_pid_kill.out`).

```
T1 arm running (snapshot taken); token carriers: [2790881, 2790884]
planted FOREIGN decoy pid 2790887 -- never planted by the counter
counter exit: 0
FOREIGN decoy pid 2790887 state after the counter run: ZOMBIE(SIGKILLed)
T1 arm line: ['ARM T1 exit=2 want=2 line=yes conform=yes survivors=0']
```

The decoy is a plain `sleep` whose argv carries the arm's absolute fixture path as an exact element
— the same argv shape as the T1 grandchild, but a different process the counter never spawned. It
is SIGKILLed by the counter's reap. The counter's own T1 receipt records `planted-killed 2`
(receipt `continuous_decoy_T1.out`).

Scale, continuous variant: 42 decoys planted at 4 s intervals across a full counter run; **30 of
them were SIGKILLed** (receipt `continuous_decoy_42_planted.out`, `ZOMBIE` state = killed,
not yet reaped). The counter's T1 receipt for that run reads `planted-killed 31`.

Control that isolates the mechanism (receipt `` and the exp57 run): decoys planted
**before** the counter starts are in the snapshot and survive; decoys planted **after** the T1
snapshot are killed. The kill tracks the snapshot boundary, not parenthood.

Impact. In the lane's own runs the token is the counter's private `--work` path, so the blast radius
is small — but the stated limit is a security-relevant ownership guarantee, and it does not hold:
any process on the host that happens to carry the arm's absolute fixture path in its argv during the
T1 arm is killed. That includes an operator's own `tail`/`less` on that path, a sibling souji seat
using the same work directory, or any unrelated tool invoked with the path as an argument. A
concurrent souji seat sharing a `--work` path would have its processes SIGKILLed mid-run.

Smallest remediation: make the identity check ownership-based rather than snapshot-based — e.g.
record the pids the arm actually spawned and only signal those (plus their descendants, by
`/proc/<pid>/stat` ppid chain), rather than "any argv carrier not in the startup snapshot". Failing
that, at minimum restrict the kill to processes whose ancestry includes the arm's own probe pid.

Note for the L1: the T1 predicate line the prereg asks for (`ARM T1 exit=2 want=2 line=yes
conform=yes survivors=0`) is still printed — the counter's `survivors=` counter excludes anything in
the snapshot, so the foreign kill is invisible in the printed numbers. The claim's *number* is
unaffected; the claim's *ownership sentence* is falsified.

## FINDINGS (no wording falsified)

### Finding 1 — HIGH — the C2 counter kills pids it did not plant

See FALSIFIES-WORDING above. The reproducer and receipts are named there.

### Finding 2 — MEDIUM — the /tmp guard is string-prefix only; bare `/tmp` and a symlink to it pass

The guard in every r97 instrument is a literal prefix test on the *resolved* path:

```
census/round-97/c1-survivor-search.py:389   os.path.realpath(os.path.abspath(v)).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))
census/round-97/c2-forgery-probe.py:181      os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))
census/round-97/c2-setup-arms.py:156        os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))
census/round-97/declared-shapes.py:38       os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))
census/round-97/c1-forgery-controls.py:48   os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))
census/round-97/c2-forgery-controls.py:42   os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))
```

The tuple has a trailing slash on every element, so `realpath("/tmp") == "/tmp"` does **not**
match `"/tmp/"`. The same is true of `/var/tmp` and `/dev/shm`. So the guard refuses
`/tmp/anything` but accepts `/tmp` itself. `realpath` resolves symlinks, so `--work <symlink to /tmp>`
also resolves to `/tmp` and is accepted.

Demonstrated in a private mount namespace (empty tmpfs on `/tmp`, so the "not empty" second guard
does not fire):

| instrument | `--work` | exit | what landed in `/tmp` |
|---|---|---|---|
| `c2-forgery-probe.py` | `/tmp` | 2 | 0 entries (fixture path guard fired later) |
| `c2-setup-arms.py` | `<symlink> -> /tmp` | 1 | **33 entries** (S1..S14, T1..T4, all fixtures, all `.out` files) |
| `c1-survivor-search.py` | `<symlink> -> /tmp` | 0 | **12 entries** (`check`, `hook`, `m0000`..`m0009`) and the search printed its full predicate line `# crash-sentinel rc=70 check=pass ...` |

Receipts: `probe_work_bare_tmp.err`, `counter_work_symlink_tmp.err`,
`search_work_symlink_tmp.out`.

Severity MEDIUM, not HIGH: the lane's own runs pass a private `--work` path, so nothing escapes to
`/tmp` in practice; the hole is reachable only by an operator (or another seat) that passes
`/tmp` or a symlink to it. It is a real guard gap, not a theoretical one — the guard is the only
thing standing between the instruments and `/tmp`, and the guard's own tuple is what misses the
bare path.

Smallest remediation: normalise the resolved path and compare path *components*, e.g.
`p = os.path.realpath(work); if p in ("/tmp", "/var/tmp", "/dev/shm") or p.startswith(("/tmp/", "/var/tmp/", "/dev/shm/")): refuse`.
Apply the same to `--emit` in the C1 search (which already guards `--emit` at line 389).

### Finding 3 — MEDIUM — the no-free-tool-id fallback can hang on a full stderr pipe (A3 is a partial fix)

Seat item 1 asked whether the r97 crash write's fd-2 change can alter the behaviour of a process
that continues after the crash write. Answer: **no** for the crash path itself — `_souji_crash` ends
in `os._exit(70)`, so the writing process never continues. But two related facts are worth recording.

(a) The A3 repair is correct but **incomplete in the other direction**: the r96 fallback set fd 2
non-blocking and left it that way (the A3 defect); r97 restores blocking mode at line 233. However
the r97 fallback then performs a **blocking** `os.write(2, ...)` on that restored fd. If fd 2 is a
full, undrained pipe, the write blocks forever and the process hangs at import time — the very
failure the A2 reordering was introduced to prevent, re-introduced one branch down.

Demonstrated: with tool ids 3,4,5 pre-occupied (so the fallback branch is taken) and stderr wired to
a full pipe, the r97 hook **hangs** (killed at the 8 s harness timeout, `rc=HUNG`), while the r96
hook on the identical setup exits 0 immediately (r96's fallback leaves fd 2 non-blocking, so its
write raises `BlockingIOError` and is swallowed). Receipts:
`fallback_hook_r97_sitecustomize.py`, `fallback_hook_r96_sitecustomize.py`.

Reachability in the lane: the fallback branch requires that `sys.monitoring.use_tool_id` fail for
ids 3, 4 and 5 — i.e. another tool (coverage, a debugger, a profiler) already holds all three.
That is not the normal case, and I did not observe it in the lane's own runs. Severity MEDIUM
because the branch is genuinely rare but the hang is unbounded and would freeze a whole census run.

(b) The fd-2 non-blocking mode set by `_souji_crash` is a property of the **open file description**,
so it is shared with any child that inherited fd 2 across `fork()`. A forked sibling therefore
observes `os.get_blocking(2) == False` after the parent's crash write, and its next stderr write
raises `BlockingIOError` instead of blocking. Demonstrated directly:

```
child get_blocking(2)=False        # after the parent's crash write, on the shared OFD
child stderr write FAILED: BlockingIOError: [Errno 11] Resource temporarily unavailable
```

This is inherent to the A2 design (the marker write must not block) and is the same in r96; it is
recorded for completeness, not as a defect. It matters only where a hook-loaded process forks and
the child keeps writing to stderr.

### Finding 4 — LOW — probe descriptor accounting is clean; the pipe-holder grandchild is NOT reaped by the probe

Seat item 4 asked for a descriptor-leak check and whether the pipe-holder grandchild is reaped.

(a) **Descriptors: no leak.** The r97 probe (`c2-forgery-probe.py`) opens one pipe pair per fixture
run and never closes it explicitly, but the `Popen` object is dropped at the end of `run()` and the
fds are reclaimed by the GC. Measured across six consecutive max-output refusals in one process:
`fds at start: 6` → `6, 8, 8, 8, 8, 8` (a one-off +2 that then plateaus; no unbounded growth), and
no zombie children accumulated. Receipt: `probe_fd_leak_measure.py` and its output.
The +2 is the last run's pipe pair held by the traceback of the in-flight `Fatal`; it does not grow.

(b) **The grandchild is not reaped by the probe — by design, and the counter covers it.** The r97
probe's timeout path calls `os.killpg(p.pid, SIGKILL)`; the T1 fixture's grandchild called
`os.setsid()`, so it is in a different process group and `killpg` cannot reach it. Measured: after
the probe's own `--timeout` fires, the grandchild is still alive and still carries the fixture token
in its argv. The counter's T1 identity reap is what removes it (planted-killed count, `survivors=0`
in the printed line). After a full counter run: `processes still carrying the T1 fixture token: 0`
and no pipe-holder zombies — so the end-to-end reaping does work, and it works *because* of the
identity reap that Finding 1 shows is over-broad. The two findings are the same mechanism seen from
opposite sides: the reap is necessary (nothing else reaps the grandchild) and it is too broad
(it kills non-planted pids).

(c) The r97 probe's max-output refusal is clean: it kills the group, raises `Fatal`, and the probe
exits 2 — no child survives (`flooder processes still visible: (none)`), no fd growth.

### Item-3 answer (does anything write under /tmp regardless of TMPDIR/--work?)

**No**, for the instruments as shipped.

- Every r97 instrument takes `--work` explicitly and writes only beneath it (search: `hook/`,
  `check/`, `m0000..m0009` under `--work`; counter: all synthetic fixtures and `.out` files under
  `--work`; probe: `F1..F7` copies and `.out` files under `--work`).
- `TMPDIR` is not consulted by any r97 instrument (grep for `TMPDIR`/`tempfile`/`mkdtemp` across
  `census/round-97/*.py` finds none). The fixture's `git` calls inherit the ambient `TMPDIR`, but
  `git init`/`add`/`commit`/`clone` were measured to leave `TMPDIR` empty (receipt: the TMPDIR watch
  in the run showed `count: 0` after `git init/add/commit` and after `git clone --shared`).
- The C2 counter's `S13` arm names an absent `/tmp/souji-r95-arm-S13-<pid>-absent` and asserts it
  does not exist (`if os.path.lexists(tmp_work): fatal`). Confirmed: no such path is created by any
  run; the counter writes its own S13 target nowhere.
- The C2 counter's `T2` arm chmods `work/T2` to `0555` so the probe's write refusal must still be
  exit 2. Confirmed: `ARM T2 exit=2 want=2 line=yes conform=yes`, and the probe's stderr for T2 is
  `C2-FORGERY-FATAL: the fixture printed no SUMMARY line for the positive control (exit 1)` — the
  refusal is real, not a silent success.
- The one way something lands under `/tmp` is Finding 2 (bare `/tmp` or a symlink to it as `--work`),
  which is a guard hole, not an unconditional write.

### Item-1 answer (does the crash write's fd-2 change alter a continuing process?)

**No** for the crash path: `_souji_crash` ends in `os._exit(70)`, so the process that wrote the marker
never continues. The fd-2 mode is a shared-OFD property, so a *forked sibling* inherits the
non-blocking mode (see Finding 3(b)) — that is the only way the crash write changes a surviving
process's behaviour, and it is identical in r96. The related gap that does bite a continuing process
is the **fallback** branch (Finding 3(a)): there the process *does* continue (it only prints a
notice), and r97's restored blocking fd makes the notice write able to hang forever.

### Negative results / things I tried that did NOT reproduce

- **The crash path never blocks.** With fd 2 wired to a full, undrained pipe, every r97 crash channel
  (excepthook, thread, unraisable/atexit) exited `rc=70` in 0.0 s. The A2 reordering works on the
  channels it covers.
- **No /tmp write escapes the instruments** under any normal `--work` (item 3 above).
- **The r97 hook's unraisable channel does not lose the traceback** the way I first suspected:
  `u.print_exception()` exists on CPython 3.14.8's `UnraisableHookArgs` (my earlier probe of
  `dir(args)` was reading a *stub* object). Under the r97 hook the atexit/unraisable channel prints
  `SOUJI-R97-CRASH unraisable ZeroDivisionError` and exits 70; the r95 shapes hook additionally
  prints the `Exception ignored in atexit callback` traceback. r96 and r97 behave identically here
  (receipts `hook_r97_unraisable_stderr.txt`, `hook_r96_unraisable_stderr.txt`).
- **The r97 hook drops the traceback on the excepthook and thread channels** (it calls `_souji_crash`
  before any print and then `os._exit`s). This is exactly what A2 claims ("crash FIRST on the raw
  write, then print") and is not a defect — but note the "then print" never happens, because
  `os._exit` follows immediately. The r96 hook printed the traceback *first*. So the r97 hook is
  strictly quieter than r96 on those two channels: the traceback is gone, not merely reordered. It
  does not affect any predicate (the reason string is still asserted by the CHECK), and I record it
  here only because the prereg's wording ("write before the traceback print") could be read as
  "the traceback is still printed". It is not a falsification — the C1 claim sentence is
  "reorders the excepthook/thread crash channels to write before the traceback print", which the
  code satisfies — but the diagnostic is lost relative to r96.

## What I verified positively (no finding)

- **C1 predicate reproduces.** `python3 -B census/round-97/c1-survivor-search.py --counter
  census/round-87/c1-pointer-counter.py --harness census/round-93/c1-false-row-harness.py
  --population census/round-93/c1-false-rows.tsv --lane . --fleet-root
  /home/vgpnk/Projects/shokunin --work <empty> --jobs 5 --ids census/round-97/c1-targets.json`
  printed `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70
  declared=1 argparse=2` (exit 0) — matches the prereg predicate.
- **C1 shape table reproduces.** `python3 -B census/round-97/declared-shapes.py --search
  census/round-97/c1-survivor-search.py --scripts census/round-97/shapes --work <empty>` printed
  `SHAPES-SUMMARY shapes=14 mismatched=0`, exit 0 — matches the prereg predicate. Per-shape:
  t1/t4 declared (plain 0, hooked 0), x1/x2 hooked 70, the four crash shapes hooked 70.
- **C2 predicate reproduces.** `python3 -B census/round-97/c2-setup-arms.py --probe
  census/round-97/c2-forgery-probe.py --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail
  tests/fixtures/r92-k4-flagfail.py --tool tools/souji-record-agreement.py --before
  census/round-92/controls/c2-before-tool.py --work <empty> --jobs 4` printed
  `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` and `ARMS-SUMMARY arms=20 conform=20`,
  exit 0 — matches the prereg predicate.
- **C2 control reproduces.** The same command with `--probe census/round-96/c2-forgery-probe.py`
  also printed `ARMS-SUMMARY arms=20 conform=20` with `survivors=0` — identical to the after arm, so
  the r96 probe and the r97 probe are indistinguishable on this counter's printed numbers (the
  prereg's control receipt `c2-control-r96-probe.txt` shows the same). The claim's "after 20 with
  survivors=0" therefore does not by itself discriminate the r97 probe from the r96 probe; the
  discrimination the prereg names for GD (the counter's identity check) is what carries it, and that
  is the mechanism Finding 1 shows to be over-broad.

### Corroborating observation from another seat's scratch (not my run)

While cleaning up I observed long-lived `fixture-hang.py` and `fixture-pipe-holder.py` processes
under a *sibling seat's* scratch (`souji-r97/R97MutC2/...`), reparented to init. Those are the same
two shapes my Finding 1 and Finding 4(b) are about — a `setsid`-escaped fixture descendant that
survived a `killpg` and was never reaped. I did not touch them (not my seat's processes, and I was
told not to mutate sibling-lane state), but it is independent corroboration that the escaped-grandchild
class of leak is real on this host and not confined to my instrumented runs.

## Scope note (no claim widening)

I did not modify any frozen instrument, test, tool or corpus file, and I did not change the claim
wording anywhere. The findings above are reported against the frozen bytes as they stand. The L1
records the C2 ownership-sentence falsification as a narrowing amendment in plans/round-97.md; the
finding text here is the evidence, not an amendment.

## Tooling

No tool was installed, upgraded or removed this round (`uv`/`npx`/official-binary channels were
available; none was needed). Nothing was written outside
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-97/w1/R97Sentinel/` and the
scratch tree `/fast/scratch/hyaku/souji-r97/R97Sentinel/` (deleted at the end of the seat). No git
or jj command was run against the lane; the only git-adjacent work was `git clone --shared` executed
by the frozen fixture inside the C2/C1 instruments, into scratch `--work` dirs.
