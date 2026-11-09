# A crash sentinel built on `sys.excepthook` alone misses five ways a Python counter can die

source: S360 (Python `sys.monitoring`, the RAISE event); S361 (Python `threading.excepthook`); S362 (Python
`os._exit`); S363 (Python `subprocess` returncode, negative = killed by a signal); S364 (Python `atexit`, exceptions
in exit handlers); S365 (Python `sys.monitoring`, the EXCEPTION_HANDLED event); S366 (Python `os.set_blocking`);
with S358 (sysexits EX_SOFTWARE 70) and S359 (`sys.excepthook` never sees SystemExit) from r94; S372
(Python `sys.monitoring`, the RERAISE event) from r97; scored against
census/round-96/c1-survivor-search.py, census/round-93/c1-false-row-harness.py and the frozen r87 counter
census/round-87/c1-pointer-counter.py (r95 instruments at round 95, r96 at round 96, r97 at round 97).
verified-at: S360–S364 and S365–S367 opened 2026-11-09 from docs.python.org/3 (Python 3.15 documentation); S360–S364
captures census/round-95/srcs/, S365–S367 captures census/round-96/srcs/ (monitoring, os, subprocess), each with its
tag-stripped text beside it; each quoted sentence's occurrence count in the whitespace-normalized tag-stripped text
is in its SOURCES row.
recheck: 365d, or when a quoted entry changes, or when the host Python changes minor version (the RAISE event,
EXCEPTION_HANDLED and the atexit-to-unraisablehook routing are CPython behaviour observed on 3.14.8).

Round 95 (C1, calibration of the survivor search's verdicts). Ground: the r94 closure's routed defects 1 and 2
(corpus/lessons/round-94-verifier-spotcheck.md §5), R94ScoutSources FW1, R94Sentinel F1/F2, plans/round-94.md A1.

## The r94 gap

The r94 sentinel replaced `sys.excepthook` and ended the process with exit 70. S359: "When an exception other than
SystemExit is raised and uncaught, the interpreter calls sys.excepthook". Every other way a Python process can stop
abnormally keeps its own exit status, so the r94 kill rule still read it as a verdict:

| channel | what Python does | r94 verdict on the r95 fixture |
|---|---|---|
| SystemExit raised mid-function (`h-sysexit`) | not an excepthook case (S359); the status is the exit code or 1 for a message | killed (`rc=1`, every row `got=-`) |
| exception in an atexit callback (`h-atexit`) | "a traceback is printed (unless SystemExit is raised)" (S364); CPython reports it through `sys.unraisablehook` and keeps the status | survived |
| exception in a thread (`h-thread`) | `threading.excepthook` handles it (S361); the main thread goes on | survived |
| `os._exit(1)` (`h-osexit`) | exits "without calling cleanup handlers, flushing stdio buffers" (S362) | killed |
| killed by a signal (`h-sigkill`) | the parent sees returncode -N (S363); the harness prints `rc=-9` | killed |

Receipt: census/round-95/controls/c1-control-r94-rule.txt (the frozen r94 search with only the five hand edits added).

## How the r95 sentinel closes each one

- `sys.unraisablehook` and `threading.excepthook` are replaced: the default hook prints, then the process exits 70.
- `os._exit` is replaced by a function that prints, flushes and exits 70 (the sentinel keeps the real one).
- SystemExit is the hard case: the counter's declared exit path is itself a SystemExit (`sys.exit(main(...))` at the
  top level), and argparse raises one for a usage error. The sentinel registers a `sys.monitoring` RAISE callback
  (S360: "An exception is raised, except those that cause a STOP_ITERATION event."). CPython fires it in the frame
  that raised and again in each frame the exception propagates into; the sentinel remembers the first frame per
  exception object and, when a SystemExit reaches the main script's `<module>` frame, marks it foreign if it was first
  raised in another function defined in the main script. An atexit callback registered before the program runs
  (so it runs last) turns a foreign exit into exit 70. A SystemExit first raised in another module (argparse) or at the
  top level keeps its status.
- The kill rule adds the signal leg: any negative `rc` on a `ROW` line, or a negative harness status, is errored.

The search refuses to score unless a check script, run the way the harness runs the counter, exits 70 on each of five
channels and keeps status 1 for a declared exit and 2 for argparse (`# crash-sentinel ... check=pass` line).

## Limits

- "Foreign SystemExit" is defined for counters whose only declared exit is a top-level `sys.exit(main(...))`. A
  counter that legitimately calls `sys.exit(n)` inside a helper defined in the same script would be scored errored.
- A signal the counter catches, C-level crashes and processes started with `-I`/`-S` are outside the check script;
  SIGKILL is the only signal fixture (`os.abort()` would also show a negative status, but no fixture tests it).
- The RAISE event and the atexit-to-unraisablehook routing are observed on CPython 3.14.8; S364 only promises a
  printed traceback, not the hook.
- The five fixtures are hand edits; the rule's effect on the full generated population is reported by the wave, not
  claimed.

## r95 wave corrections (after WAVE-DONE; plans/round-95.md A1-A4, A7)

- **The SystemExit leg is wider than "a helper's sys.exit".** It scores errored ANY SystemExit first raised inside a
  function defined in the main script — `sys.exit(...)` called in `main` itself, `raise SystemExit(helper())`, a raise
  inside try/finally — and one first raised there that reaches the top level and is caught (R95Labrat v3/w1/w2/a3b,
  t1/t4: plain rc 3 or 0, hooked 70). It does not track whether the exception ends the process. The frozen r87 counter
  exits only through a top-level `sys.exit(main(...))`, so its verdicts are unaffected; a counter that exits from
  `main` would need the leg rewritten (e.g. record the exit at the RAISE in `<module>` that the interpreter actually
  terminates on, or an EXCEPTION_HANDLED event to clear a caught one).
- **The unraisablehook leg stops at finalization.** A global object's `__del__` raising at interpreter shutdown after
  `sys.exit(main())` keeps the process status (R95Labrat u1/u3/u5: 3→3, 0→0); the same `__del__` when the script
  falls off the end exits 70 (u2). A `__del__` that raises during the run is caught (R95ReviewerC1 `del_raise.py`).
- **`os._exit` replaced means every `os._exit`, and the crash path is not async-signal-safe.** `os._exit(0)` becomes
  70 (R95Critic, R95Sentinel F3). The replacement writes to stderr and flushes; called from a signal handler or another
  thread while the main thread holds the stderr lock, or with a full undrained stderr pipe, it hangs (R95Sentinel F1:
  plain rc 0 in 1 s, hooked HUNG at 12 s). A safer crash path writes with `os.write(2, ...)` best-effort and calls the
  real `os._exit(70)` without touching the text streams.
- **Scope: the whole harness subtree.** The hook sits on PYTHONPATH, so every Python process under the harness carries
  it: a forked child's `os._exit(0)` turns into status 70, `sys.monitoring` id 3 is taken in every process, and when ids
  3 and 4 are busy the loop takes 5, the reserved OPTIMIZER_ID (R95Sentinel F3/F4). With no free id the sentinel only
  prints a line; the search's CHECK then fails closed (`sysexit=1`, exit 2).
- **The check line binds exit codes, not mechanisms.** Cross-wiring the thread or os._exit leg to the excepthook
  function still passes every CHECK and target (R95MutC1 m02/m03); a CHECK that asserts the `SOUJI-R95-CRASH` reason
  per channel would bind them.
- S360's page does not name SystemExit and S361's does not state that the main thread keeps its status: both are
  observations on CPython 3.14.8, now disclosed in the rows (A7).


## r96 audit (C1, calibration): the EH clear is a TRADE, not an improvement (verdict: harmed)

Round 96 (C1, calibration 7). Ground: r95 closure §7 (SystemExit-leg rewrite, Q172 precondition), plans/round-95.md
A1, R95Sentinel F1/F3, Q172. Amendments: plans/round-96.md A1–A3, A9.

- **What r96 changed.** The r95 leg marked a SystemExit first raised inside a main-script function foreign and never
  cleared it, so a SystemExit caught at the top level (t1/t4: plain 0) was scored errored (r95 hook `mismatched=2`).
  The r96 hook adds an EXCEPTION_HANDLED callback (S365) that clears the mark when the callback's frame is `<module>`.
- **What it gets right.** t1 and t4 (caught at top level, plain 0) now score declared: `mismatched=0` on the twelve-shape
  table (re-derived by the L1 and four seats).
- **What it gets wrong (measured by the L1 under the frozen hooks).** The same frame-name test also clears a terminating
  exit that passes through a module-level `finally` or a module-level re-raising `except`: CPython fires
  EXCEPTION_HANDLED in the frame that owns the `finally` and at the re-raise. Plain rc 1 (terminating): r95 hook 70
  (errored, correct), r96 hook **1 (declared, wrong)**. The twelve-shape table has no such shape, which is why its
  `mismatched=0` does not see it. The earlier sentence in this entry that a `finally` "does not stop the exception
  terminating, so the clear is scoped to `<module>`" describes the cause, not a protection: a module-level `finally`
  is in `<module>`, so the clear still applies.
- **Verdict.** A gain on one shape class and a loss on another, both measured: a trade. The admission rule (no axis
  harmed) does not admit it as an improvement. The calibration score stays 7. The operator rules.
- **Crash path.** The marker write is a raw `os.write` on a momentarily non-blocking fd 2 (S366, S370). It does not
  block, and the exit code is not affected by it (E16/E18/E3c measured). Two limits, both measured by R96Sentinel:
  (1) the excepthook and thread channels print their traceback through the blocking TextIOWrapper before the crash path,
  so they can still block on a full undrained pipe (E10, faulthandler stack); (2) the no-free-tool-id fallback leaves fd 2
  non-blocking for the rest of the process (E5, E9). The earlier wording "cannot block the exit" was wrong for (1) and
  "momentarily" was wrong for (2).
- **Per-channel CHECK reasons** assert `SOUJI-R96-CRASH <channel>` for each channel the search runs. The mutants that
  drop a reason assertion survive the predicate for some channels (R96MutC1 M04, M14): the predicate does not bind
  every reason. Routed to r97.
- **Scope note.** This entry's teaches cells for S365–S367 are superseded by S369–S371 (SOURCES.md). S368 (setsid(2))
  is the source for the process-group claim in deadline-owned-reaping.md.

## r97 (C1, calibration): the pending-clear latch closes the trade

Round 97 (C1, calibration 7). Ground: plans/round-96.md A1 (the r96 trade), the r96 spot-check §7 routed item 1,
plans/round-97.md A0. Amendments: plans/round-97.md A0.

- **What r97 changed.** The r96 clear-on-any-EH became a pending-clear latch (S372): the foreign mark latches at
  RAISE-`<module>`; a module-level EXCEPTION_HANDLED records a pending candidate for the same exception object;
  a RERAISE of the same object cancels the candidate (S372: "An exception is re-raised, for example at the end of
  a finally block."); atexit flushes a still-pending candidate. Measured ordering on CPython 3.14.8 (scratch
  trace, nine shapes): a terminating module-level `finally` fires EH, RERAISE, EH, RERAISE; a caught-at-top-level
  exit fires a single EH and no RERAISE. The latch keeps t1/t4 declared and x1/x2 (terminating module `finally`
  and re-raise) errored: `SHAPES-SUMMARY shapes=14 mismatched=0` (census/round-97/records/shapes-r97.txt), where
  the r96 hook mismatched=2 (x1/x2 at 1) and the r95 hook mismatched=2 (t1/t4 at 70). The ten-target summary is
  unchanged (errored=7 killed=2 survived=1), which the prereg states is not discriminating for this claim.
- **What else r97 repaired in the same instrument file.** A2: `_souji_excepthook`/`_souji_thread` now call the raw
  signal-safe `_souji_crash` before the traceback print, so the blocking TextIOWrapper print cannot hold the exit
  hostage on a full undrained pipe on those channels either. A3: the no-free-tool-id fallback restores fd 2's
  blocking mode (`os.set_blocking(2, True)`) instead of leaving it permanently non-blocking.
- **Limit carried as a stated limit (prereg (iii)).** The interleaving is an observation on CPython 3.14.8, not a
  documented guarantee. S369 rules finally/re-raise firing out of the EH entry's scope and S372 states only that a
  re-raise fires RERAISE; neither states the ordering the latch relies on. The shape table is a precondition, not
  a census of every exit shape the lane will meet.
