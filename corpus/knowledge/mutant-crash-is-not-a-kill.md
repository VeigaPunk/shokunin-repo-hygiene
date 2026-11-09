# A mutant whose counter crashes is a runtime error, not a kill — and the search must be able to see the crash

source: S357 (Stryker Mutator, Mutant states and metrics: the Runtime error state); S358 (sysexits(3), EX_SOFTWARE 70);
S359 (Python `sys.excepthook` / `sys.unraisablehook`, added after the r94 wave);
scored against census/round-94/c1-survivor-search.py, census/round-93/c1-false-row-harness.py and the frozen r87
counter census/round-87/c1-pointer-counter.py at round 94.
verified-at: Stryker docs page opened 2026-11-09, capture census/round-94/srcs/stryker.html sha256
30071cc7b6578a114843f18da568c305b192a08d098511896e7cb4a90a5f89da (27068 bytes); FreeBSD sysexits(3) opened 2026-11-09,
capture census/round-94/srcs/sysexits.html sha256 da498cbc711a743ae309b603ae8615f1164690cb6d4a67dea2e650175cbae139
(59385 bytes); each quoted sentence occurs once in the whitespace-normalized tag-stripped text.
recheck: 365d, or when either page changes the quoted entry.

Round 94 (C1, calibration of the survivor search's verdicts). Ground: S357, S358, the r93 closure's routed defect 2
(corpus/lessons/round-93-verifier-spotcheck.md §5) and R93Sentinel M1.

## Why the r93 rule miscounts

The r93 search scored a mutant KILLED when the harness exited 1 and printed at least one `ROW ... match=no` line. Its
docstring assumed a crashing counter exits 2 (`match=error`). A Python program that raises an uncaught exception
exits 1, the same status the counter uses for "not every item resolved". The harness then reads whatever the counter
printed before the crash and marks a row `match=no` wherever the asserted status or exit code is missed. So a mutant
that only crashes looks exactly like a mutant whose verdict a row caught: the r93 rule scored both r94 crash fixtures
(`h-crash-late`, `h-crash-index`) `killed=yes` (census/round-94/controls/c1-control-r93-rule.txt).

## What a mutation tool does with it

S357 separates the states. Killed: "When at least one test failed while this mutant was active, the mutant is killed."
Runtime error: "The running of the tests resulted in an error (rather than a failed test)." Of a runtime error the page
says "It is not represented in your mutation score" (the same sentence closes the Compile error entry): it is neither
detected nor undetected. Counting it as killed inflates the score with edits no row actually bound.

## How the r94 search sees the crash

The harness does not surface the counter's stderr, so a rule that greps for `Traceback` in the harness output misses
a crash that happens after the counter printed its items (`h-crash-late`). r94 makes the crash visible by exit code
instead: every harness run gets a `sitecustomize.py` on PYTHONPATH whose `sys.excepthook` prints the traceback, flushes
both streams and ends the process with exit 70. Child processes inherit the environment, so the counter the harness
spawns carries the same hook, and the crash shows as `rc=70` on the harness's `ROW` lines. 70 is S358's EX_SOFTWARE,
"An internal software error has been detected.", and no harness verdict (0, 1) or setup error (2) uses it. The search
checks the hook fires in a child before scoring anything (precondition, exit 2 if not).

## Rule

A mutant is `errored` when the harness exits 70 or any `ROW` line reads `rc=70`; otherwise `killed` only on a harness
exit 1 with at least one `match=no` row; exit 0 survives. Both halves are needed: without the sentinel (forgery FB)
the crash fixtures stay `killed`; refusing every non-zero exit (forgery FA) turns the two real kills into `errored`
(census/round-94/controls/c1-forgery-controls.txt).

## Limits

- The hook covers uncaught exceptions in the main thread of a Python counter. A counter that calls `os._exit(1)`, is
  killed by a signal, or crashes in a thread is not caught (threading.excepthook is separate).
- A counter that legitimately exits 70 would be scored errored.
- `python -I`/`-S` or an earlier `sitecustomize` on the path would disable the hook; the precondition check runs the
  hook the way the harness runs the counter, but a harness that changed how it starts the counter would need its own
  check.

## r94 wave corrections (after WAVE-DONE; plans/round-94.md A1-A3)

- **The exit-1 premise is observed, not sourced.** "A Python program that raises an uncaught exception exits 1" has
  no source row (R94ScoutSources FW2). It is grounded here by own-work receipts: the r93 rule's run of both crash
  fixtures reads `rc=1` (`census/round-94/controls/c1-control-r93-rule.txt`), and so does forgery FB (no sentinel,
  `controls/c1-forgery-out/FB.out`).
- **Two more channels the sentinel does not see** (Limits, first bullet, was not exhaustive). S359: "When an
  exception other than SystemExit is raised and uncaught, the interpreter calls sys.excepthook with three
  arguments" — so `raise SystemExit(1)` exits 1 with no hook (R94ScoutSources `repro-sysexit-gap.out`); and an
  exception in an `atexit` callback or a `__del__` finalizer goes to `sys.unraisablehook` ("Called when an exception
  has occurred but there is no way for Python to handle it"), the process keeps its exit status, and a counter that
  finished cleanly then raised at shutdown is scored a SURVIVOR (R94Sentinel F1, `receipts/out-F.txt`).
- **The five-target number does not by itself prove the sentinel is needed.** A no-sentinel rule fitted to the two
  fixtures (`got=-` present OR every row `rc=1`) also reads `errored=2 killed=2 survived=1` (R94Critic
  `receipts/offline-rule-eval.out`). The mechanism's evidence is the `rc=70` ROW lines themselves (66 for
  `h-crash-late`, 1 for `h-crash-index`, `census/round-94/records/c1-after-harness/`) and the full census below.
- **Full census, reported not claimed** (R94ExecCensus): over all 273 generated-plus-hand mutants on the r93
  population the r93 rule reads `errored=20 killed=167 survived=76`, the r94 search `errored=48 killed=139
  survived=76`; the 28 changed verdicts are all `yes` → `errored` and all carry `rc=70` rows — 26 generated
  mutants plus the two fixtures. Of the r93 rule's 167 kills, 28 (16.8 %) were crashes.
