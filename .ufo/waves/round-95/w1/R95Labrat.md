# R95Labrat — the r95 foreign-SystemExit leg misclassification hunt

Report: .ufo/waves/round-95/w1/R95Labrat.md
Seat: reviewer R95Labrat (runs the labrat task per A0; validator-tolerated role).
Scratch was /fast/scratch/hyaku/souji-r95/R95Labrat (deleted before yield).
Everything below lives as bytes under .ufo/waves/round-95/w1/R95Labrat/receipts/
(scripts + the extracted sitecustomize.py). No commit, no lane mutation.

## Rubric

H: there is a plain, non-crashing exit shape that the r95 sentinel turns into
exit 70, or a crashing shape that keeps its status.
Axes: (i) false-positive rate on ordinary non-crashing exits; (ii) false-negative
rate on crashing shapes that reach the top level; (iii) wording coverage of the
prereg's stated limits. Method: run ≥10 tiny shapes as
`python3 -B <script>`, then `PYTHONPATH=<hookdir> python3 -B <script>`, where
the hook is the literal HOOK text extracted from census/round-95/c1-survivor-
search.py (byte-identical to the search's string constant, written to
sitecustomize.py because CPython only auto-imports `sitecustomize` — the search
writes it to `<work>/hook/sitecustomize.py` and puts it on PYTHONPATH, line
312-316 of the search). `python3 -B` = python3.14.8, sys.monitoring live.

## Shape table (plain rc, hook rc, expected = plain rc unless marked 70)

| shape | plain | hook | expected | verdict |
|---|---|---|---|---|
| sys.exit(main()), helper returns 3 | 3 | 3 | 3 | ok |
| raise SystemExit(main()) at module | 3 | 3 | 3 | ok |
| sys.exit inside try/finally in main | 3 | 3 | 3 | ok |
| raise SystemExit in try/finally in main (finally completes, SE propagates) | 3 | **70** | 3 | **MISCLASS-70** (a3b) |
| SystemExit caught in main, main returns 3 | 3 | 3 | 3 | ok |
| exit() builtin in main | 3 | 3 | 3 | ok |
| quit() builtin in main | 3 | 3 | 3 | ok |
| python -m package legit exit | 3 | 3 | 3 | ok |
| python -m package, main raises SE | 1 | 70 | 70 | ok |
| -m on plain file path (n/a) | 3 | 3 | 3 | ok |
| runpy foreign SE in main fn | 1 | 70 | 70 | ok |
| main raises SE direct | 1 | 70 | 70 | ok |
| nested helper raises SE | 1 | 70 | 70 | ok |
| sys.exit inside main as `sys.exit(helper())` (v3/w1) | 3 | **70** | 3 | **MISCLASS-70** |
| raise SystemExit(helper()) inside main (w2) | 3 | **70** | 3 | **MISCLASS-70** |
| module-level raise SystemExit(3) (v1) | 3 | 3 | 3 | ok |
| module raises SE(main()) (a12) | 3 | 3 | 3 | ok |
| main() with no exit, falls through | 0 | 0 | 0 | ok |
| t1: helper raises SE, caught at module, module falls off end | 0 | **70** | 0 | **MISCLASS-70** |
| t4: SystemExit saved and re-raised at module, caught | 0 | **70** | 0 | **MISCLASS-70** |
| t8: SystemExit(0) in main → sys.exit(main()) | 0 | **70** | 70-ish | mixed |
| t6: atexit callback raises SystemExit | 3 | 70 | 70 | ok |
| t7: atexit callback 1/0 (the fixture shape) | 3 | 70 | 70 | ok |
| u4: weakref.finalize callback 1/0 | 3 | 70 | 70 | ok |
| t5: __del__ raises on explicit del+gc during main | 1 | 70 | 70 | ok |
| a9/u1: __del__ raises at interpreter shutdown after sys.exit(main()) | 3 | **3** | 70 | **MISCLASS-keeps-status** |
| u2: same __del__ at shutdown, script ends by falling off end | 0 | 70 | 70 | ok |
| u3: same __del__, sys.exit(main()=0) | 0 | 0 | 70 | **MISCLASS-keeps-status** |
| u5: __del__ shutdown after atexit registered | 3 | 3 | 70 | **MISCLASS-keeps-status** |
| a8: thread raises SystemExit(5) | 3 | 70 | 3 (parent well-behaved) | **MISCLASS-70** (thread leg) |
| a7: parent spawns subprocess child that crashes | 3 | 3 | 3 | ok (child separately 70, correct) |
| a7b: subprocess child raises SystemExit(9) | 3 | 3/9-child | 3 | ok |

## What the results mean

Kill or confirm H: CONFIRMED on both disjuncts.

1. Several ordinary, non-crashing exits become 70 (False positives):
   - `sys.exit(helper())` called inside `main` (v3/w1/w2): the RAISE callback
     fires when `sys.exit` raises SystemExit **inside main itself**, not inside
     helper, so the sentinel treats a legitimate exit argument evaluation as
     "first raised inside a function of the main script". This is within S360
     letter (SystemExit first raised inside main, reaches top level) but
     outside the prereg's stated "declared exits" enumeration, which names
     only top-level `sys.exit(main(...))`.
   - t1/t4: caught SystemExits (and SystemExit re-raised then caught at module
     level) still trip the sentinel — plain rc 0 → hook 70. The sentinel only
     knows the SystemExit was first raised in a main-script function and never
     learns it was caught.

2. Two crashing shapes keep their status (False negatives):
   - Global-object `__del__` raising RuntimeError during interpreter shutdown
     AFTER `sys.exit(main())` (u1/u3/u5): plain 3→hook 3, 0→0. However, the
     SAME `__del__` raising when the script falls off the end (u2): 0→70. The
     asymmetry is reproducible and the first half is the standard counter
     shape. Root cause: with `sys.exit(main())`, the shutdown finalizer
     exception is rendered by CPython's deallocator-failure path ("Exception
     ignored while calling deallocator ... RuntimeError"), which never reports
     through `sys.unraisablehook`/the threading hook: the sentinel hook fires
     on neither expiry loop, so no 70 is emitted. By contrast, plain-harness
     CPython rounds of `atexit`-callback exceptions DID reach unraisablehook
     (t6/t7 hook=70). So "the sentinel also ends the process with exit 70 on
     an exception reported to sys.unraisablehook (atexit callbacks...)" is
     true for atexit callbacks, and true for shutdown `__del__` when the
     counter falls off the end (u2), but false for shutdown `__del__` when
     the counter exits via the canonical `sys.exit(main(...))` shape (u1).
     This is an interpreter-mechanism finding (CPython 3.14.8) with no
     matching CHECK entry, not something the search's CHECK samples.

3. The thread leg (a8) also fires on SystemExit raised inside a joined thread:
   parent plain 3 (well-behaved) → hook 70. The prereg's thread fixture is a
   RuntimeError-shape crash in a joined thread scored errored by threading.
   excepthook; a thread that raises SystemExit is by definition not crashing
   the parent process, and the parent joined cleanly. Whether this is a
   misclassification depends on how "crashing shape" is read for threads,
   but the parent process exiting 3 cleanly and being scored 70 is a
   false-positive under the claim's own "dies on another channel" framing.

Verdict: H confirmed. The claim's predicate (ten targets' verdicts with exit 0)
is NOT falsified by any of these — none of the target ids is affected: the FP
shapes are absent from the ten, and a wrong verdict on an absent shape only
matters if a future mutant exercises it. But the subject claims in the prereg
(the CLAIM first sentence, the sentinel-coverage sentence, the atexit
sentence, and the stated limits) materially overstate the sentinel's coverage,
and the stated limit (ii) mislabels the helper-call case (it says "a counter
that legitimately calls sys.exit inside its own helper", while the actual
failure is `sys.exit(...)` inside main itself evaluating helper()).

## FALSIFIES-WORDING — exact sentences (highest-confidence first)

- "the sentinel also ends the process with exit 70 on ... an exception reported
  to sys.unraisablehook (atexit callbacks ...)"
  — incomplete as to CPython's shutdown-finalizer path: with the standard
  `sys.exit(main(...))` counter shape, a global object's `__del__` raising
  at interpreter shutdown produces "Exception ignored while calling
  deallocator" and never passes through sys.unraisablehook, so the process
  exits with its own status (receipts: u1-shutdown-del.py / u2-shutdown-del-
  falloff.py: identical __del__, one with sys.exit(main()) → 3/3, one without
  → 0/70).
- "(ii) The SystemExit leg treats the counter's top-level sys.exit(main(...))
  and a SystemExit first raised outside the main script (argparse) as
  declared exits; a counter that legitimately calls sys.exit inside its own
  helper would be scored errored."
  — wrongly locates the helper case (the failing shape is `sys.exit(expr)`
  inside main, not sys.exit inside helper; receipts v3-func-args-pattern.py,
  w1-init-helper.py: 3→70).
- "a counter that dies on another channel keeps its own exit status" —
  stated as a universal after the sentence that limits it to the five
  fixtures only later; on the shutdown-finalizer channel the problem
  persists after r95.

Highest-severity. Severity order: shutdown-finalizer coverage gap >
main-local sys.exit/helper-arg false positives > caught-SystemExit false
positives > thread-SystemExit (claim coverage wording of the thread leg).

## What was NOT falsified

- The predicate line: `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0
  hung=0 scored=10 errored=7 killed=2 survived=1` was NOT re-run here (that
  is SoujiR95/L1's run); nothing in this seat's table touches any of the ten
  target ids' verdicts, so I assert no FALSIFIES-NUMBER on the predicate.
- The five crash-channel fixtures still score errored through the search.
- The r94-target verdicts are unchanged by anything this seat found.

## Files

- receipts/*.py — every shape script above (one per row whose filename matches
  the table basename), plus receipts/runner.py and receipts/runner2.py which
  produced the first and corrected tables (runner2.py is authoritative:
  runner.py's "MISCLASS-NON70" rows for a6/a10/a11/a13/a13b/runpy were
  expectation errors of the runner itself — a13's true plain rc is 0, a6 is
  not a module run — corrected in runner2.py).
- receipts/sitecustomize.py — byte-verified HOOK extraction; sha256
  0f60591cf643a1614fa25c6425bf3105651433050bf2e5290f5548f1a513c7ee.
- Reproduction: `PYTHONPATH=<dir containing receipts/sitecustomize.py>
  python3 -B <any receipts script>` vs `python3 -B <script>`.

## Residual risk and verification gaps

- Not re-run: the full predicate search, the control, or the forgery controls.
  The L1's after-receipts remain authoritative for the numeric predicate; my
  rejection of the wording rests solely on the shape tables above.
- The shutdown-finalizer behavior is specific to CPython 3.14.8 + this
  sentinel's atexit registration order. The prereg's limit (iii) already
  discloses CPython-specific RAISE/atexit behavior; the new finding is that
  the description of the atexit-to-unraisablehook route is overbroad for
  shutdown finalizers under the canonical exit shape. A narrowing amendment
  (add "snapshot of a global __del__ raising at shutdown under sys.exit(...)"
  to the not-covered set, or bound the sentinel sentence to the observed
  route) would close this without touching the predicate.
- All receipts step rc values were measured twice (once in runner2.py, once
  with the a9/u-batch loops) and agree.

H-killer / H-confirmer summary: H confirmed — both disjuncts fire; no sentence
in this report's FALSIFIES-WORDING list is exclusive to one claim, so the L1
can place it where the amendment belongs.
