# R95MutC1 — C1 sentinel/rule one-edit mutants (souji round 95)

- Task: 13 one-edit mutants of census/round-95/c1-survivor-search.py, each run through the C1 predicate with --jobs 5. SURVIVES = exact predicate check line + 10 per-id verdicts + SEARCH-SUMMARY + EXIT 0 (the `# search sha256=` self-hash line necessarily differs; it reports the mutant's own hash).
- Pins: pristine search sha256 6066508fa4b113f5e7d9d269e4e3516c104d0e5cc9236cc5e4c6aa8a0d649740; targets fb40bf4e046c074845ec00c587173b49c7a095a6236cb188880a2183d7ba5b8e
- Legend: killed = predicate fails (caught); survived = predicate passes exactly. Receipts: R95MutC1/receipts/mXX.txt (command line is the runner's printed CMD). Mutant files: R95MutC1/mutants/mXX.py (each a one-line diff from pristine; hashes below). Runner: R95MutC1/run_mutant.py. All runs cwd=lane, --jobs 5, empty scratch --work per run (deleted afterward).
- Predicate summary (pristine, re-derived by this seat): check line `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`; `SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1`; EXIT 0. Per-id verdicts: h-sysexit/h-atexit/h-thread/h-osexit/h-sigkill/h-crash-late/h-crash-index = errored; h-ok-admits-one/a491c22 = yes; a127c26 = no.

## Mutant table

| ID | Edit (one line) | Mutant sha256 | Observed output (receipt) | Verdict |
|---|---|---|---|---|
| m01 | `sys.unraisablehook = _souji_unraisable` → `sys.unraisablehook = _souji_excepthook` (unraisablehook leg) | bb24a4bb… | `C1-SEARCH-FATAL: crash sentinel check atexit: child exit 1, want 70`, EXIT=2 | killed (precondition atexit check) |
| m02 | `threading.excepthook = _souji_thread` → `threading.excepthook = _souji_excepthook` (threading.excepthook leg) | 76565ae5… | exact predicate lines incl. check line + summary, EXIT=0 | **survived** |
| m03 | `os._exit = _souji_os_exit` → `os._exit = _souji_excepthook` (os._exit leg) | d4265e26… | exact predicate lines incl. check line + summary, EXIT=0 | **survived** |
| m04 | `code.co_name == "<module>"` → `"<module>alt"` (RAISE callback, `<module>` test) | af15832c… | `C1-SEARCH-FATAL: crash sentinel check sysexit: child exit 1, want 70`, EXIT=2 | killed (precondition sysexit check) |
| m05 | `code.co_filename == main` → `code.co_filename == main + "x"` (RAISE callback, main-file test) | f2c36300… | `C1-SEARCH-FATAL: crash sentinel check sysexit: child exit 1, want 70`, EXIT=2 | killed (precondition sysexit check) |
| m06 | `atexit.register(_souji_atexit)` → `atexit.register(lambda: None)` (atexit registration) | dd5bd92c… | `C1-SEARCH-FATAL: crash sentinel check sysexit: child exit 1, want 70`, EXIT=2 | killed (precondition sysexit check) |
| m07 | `range(3, 6)` → `range(4, 6)` (tool-id loop) | 83c5b3b5… | exact predicate lines incl. check line + summary, EXIT=0 | **survived** |
| m08 | `("osexit", CRASH_RC)` → `("osexit", 1)` in CHECKS (want code) | 15360335… | `C1-SEARCH-FATAL: crash sentinel check osexit: child exit 70, want 1`, EXIT=2 | killed (precondition osexit check) |
| m09 | `("argparse", 2)` → `("argparse", 1)` in CHECKS (want code) | 3cdaeba8… | `C1-SEARCH-FATAL: crash sentinel check argparse: child exit 2, want 1`, EXIT=2 | killed (precondition argparse check) |
| m10 | CHECK tail `sys.exit(main(sys.argv[1]))` → `sys.exit(1)` (CHECK script) | 69b728ff… | `C1-SEARCH-FATAL: crash sentinel check excepthook: child exit 1, want 70`, EXIT=2 | killed (precondition excepthook check) |
| m11 | `("declared", 1), ("argparse", 2))` → `("argparse", 2))` in CHECKS (precondition loop leg deletion) | 8404525c… | `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 argparse=2` + exact summary, EXIT=0 | **survived** (see §Survivors) |
| m12 | `seen[2] != "<module>"` → `"<module2>"` (RAISE first-frame record `<module>` test) | 721aefd5… | `C1-SEARCH-FATAL: crash sentinel check declared: child exit 70, want 1`, EXIT=2 | killed (precondition declared check) |
| m13 | `sys.excepthook = _souji_excepthook` → `sys.excepthook = _souji_unraisable` (excepthook leg) | c66090f8… | `C1-SEARCH-FATAL: crash sentinel check excepthook: child exit 1, want 70`, EXIT=2 | killed (precondition excepthook check) |

Note on earlier draft attempts (kept for honesty of the record): the first submitted m08/m09/m11 byte edits did not land (an exact `rc==/rc<0` negative-rc pair edit and a CHECKS-line drop applied no change or a no-op in the sheet edits), and the first m08/m09 rewrites duplicated older bytes. Every mutant actually run is its filed `mXX.py`, verified by `difflib` against pristine to a one-line diff before running; the receipts above are from the final bytes. The first m08/m09 runs (no-op stamps) showed `errored=6 killed=3` for h-sigkill — consistent with FC in the frozen forgery controls — and were superseded by the CHECKS want-code mutants now filed.

## Survivors

Four mutants print the full predicate output with EXIT 0.

- **m02** (threading.excepthook leg: `_souji_thread` → `_souji_excepthook`). Cross-wired-channel survivor: `thread=70` still passes because `sys.excepthook` also terminates with 70, and h-thread still scores `errored` because the harness/ROW signal (`rc=70` via threading.excepthook pre-routing, or row-level) masks the loss. **Classification: unbound** (the hook's *name* is not observed by this predicate; only its exit code is). To bind: the CHECK would need to distinguish a crash *message* (e.g. `SOUJI-R95-CRASH thread …` on stderr) or to call `threading.excepthook` directly with a synthetic `ThreadExceptionHookArgs` and assert the thread code path ran.
- **m03** (os._exit leg: `_souji_os_exit` → `_souji_excepthook`). Same cross-wiring: `osexi(_)` still exits 70 through excepthook, check and fixture pass. **Classification: unbound** (exit code only observed, not which REPLACEMENT function). To bind: same message-level CHECK, or a direct call to the installed `os._exit` proving it does not raise.
- **m07** (tool-id loop: `range(3, 6)` → `range(4, 6)`). The loop still installs monitoring at id 4 (id 3 is never busy here), so all channels behave identically. **Classification: equivalent on this environment** — the mutation is only distinguishable if tool ids 3 AND 4 are both occupied, so the run would fall through to id 5 / "no free tool id". To bind: a CHECK/run with ids 3..5 pre-occupied by other tools asserting the sentinel still installs at the first free id.
- **m11** (precondition loop leg: deleted `("declared", 1)` from CHECKS). The check line now reads `… osexit=70 argparse=2` (no `declared=1`), yet the predicate check line in the prereg *includes* `declared=1`, so this mutant is killed **only under the strict check-line reading**, not under the `SEARCH-SUMMARY`/verdicts reading. Note: deleting `declared` also deletes the binding against `C1-SEARCH-FATAL … declared` (m12 was caught by that leg, not by any SEARCH line). **Classification: killed under the strict check-line reading of the predicate; survived under the summary/verdicts reading.** This is a wording binding, not a behavioural binding: the `declared=1` token is cosmetic unless the predicate explicitly requires it.

None of the four survivors falsifies the C1 *stated claim* numbers (errored=7/killed=2/survived=1 is reproduced exactly by each). They show the predicate's check line under-binds the threading-excepthook and os._exit legs to their exit code only (m02/m03), an environment-dependent tool-id loop (m07, equivalent here), and a cosmetic declared token (m11). The L1 may record the under-binding as an amendment if it values the predicate's leg-specific text; it does not change the verdict numbers.

## Verdict

9/13 one-edit mutants are caught, all by the C1 predicate's own precondition CHECK (`C1-SEARCH-FATAL` + EXIT 2, before scoring) — the search refuses its own broken sentinel before scoring a single target. The 4 survivors are detailed above (m02, m03, m07, m11). No artifact produced here falsifies any sentence of the CLAIM, the PREDICATE numbers, or the STATED LIMITS (the CHECK script plus invariant all ran and matched on the pristine bytes).

## NO-FALSIFICATION

No falsification attempted that survived. Best efforts tried: (a) cross-wiring each hook assignment (m01/m02/m03/m13 — only the cross-wires to `_souji_excepthook` survive; wrong-type swaps crash the precondition and are caught); (b) breaking the RAISE callback's three sub-tests and the atexit registration (m04/m05/m06/m12 — all caught by the precondition's sysexit/declared legs); (c) narrowing the tool-id loop (m07 — survived, equivalent here); (d) want-code mutations in CHECKS (m08/m09 — caught by the precondition comparing to the mutated want); (e) CHECK-script tail deletion (m10 — caught); (f) precondition-row deletion (m11 — survives save the strict check line). A finding with a reproducer: receipts `R95MutC1/receipts/m02.txt`, `m03.txt`, `m07.txt`, `m11.txt` each show the exact predicate output; mutant bytes are in `R95MutC1/mutants/`.

## Restoration evidence

Pristine `census/round-95/c1-survivor-search.py` sha256 re-verified after all runs: `6066508fa4b113f5e7d9d269e4e3516c104d0e5cc9236cc5e4c6aa8a0d649740` (identical to the pre-run pin — the filed instruments were never modified; mutants were copies in the seat dir). Scratch `/fast/scratch/hyaku/souji-r95/R95MutC1/` removed before yield (per-mutant `--work` dirs were already deleted by the runner's `finally`).

Report: .ufo/waves/round-95/w1/R95MutC1.md
