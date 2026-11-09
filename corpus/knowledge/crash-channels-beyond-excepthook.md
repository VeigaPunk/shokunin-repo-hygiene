# A crash sentinel built on `sys.excepthook` alone misses five ways a Python counter can die

source: S360 (Python `sys.monitoring`, the RAISE event); S361 (Python `threading.excepthook`); S362 (Python
`os._exit`); S363 (Python `subprocess` returncode, negative = killed by a signal); S364 (Python `atexit`, exceptions
in exit handlers); with S358 (sysexits EX_SOFTWARE 70) and S359 (`sys.excepthook` never sees SystemExit) from r94;
scored against census/round-95/c1-survivor-search.py, census/round-93/c1-false-row-harness.py and the frozen r87
counter census/round-87/c1-pointer-counter.py at round 95.
verified-at: all five pages opened 2026-11-09 from docs.python.org/3 (Python 3.15 documentation), captures
census/round-95/srcs/{monitoring,threading,os,subprocess,atexit}.html with their tag-stripped text beside them; each
quoted sentence's occurrence count in the whitespace-normalized tag-stripped text is in its SOURCES row.
recheck: 365d, or when a quoted entry changes, or when the host Python changes minor version (the RAISE event and the
atexit-to-unraisablehook routing are CPython behaviour observed on 3.14.8).

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
