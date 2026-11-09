# R95ReviewerC1 — C1 crash sentinel and kill rule, correctness review against the C1 wording

Scope: census/round-95/c1-survivor-search.py (HOOK 81-152, CHECK 153-176, verdict 216-228, score 231-267, main 284-382),
census/round-93/c1-false-row-harness.py (exit paths 387-564, ROW branches 439-558), prereg C1 (census/round-95/preregistration.txt lines 21-69).
Nothing in the lane was edited. Scratch was deleted after receipts were copied here.

Summary: NO-FALSIFICATION for the C1 sentence as worded. Two non-falsifying observations are recorded under Q5 (predicate does not
directly test the unraisablehook leg; a claim-adjacent population effect for the wave to report). I did not run the predicate
commands themselves; the probes below are the foreign-SystemExit and harness-under-hook checks requested in the assignment.

## Q1 — foreign-SystemExit leg: fires on main()-raised SystemExit, not on declared or handled exits

Receipt: .ufo/waves/round-95/w1/R95ReviewerC1/receipts-foreign-sysexit.txt (all rc values are the real child exit codes under
PYTHONPATH=hook, `python3 -B`, the way the search's CHECK runs the counter).

| script (scratch) | shape | rc under r95 hook |
|---|---|---|
| main_raise | `raise SystemExit(3)` inside `main()` defined in main script | 70 (fires) |
| helper_in_main | helper in main script raises SystemExit(6), uncaught | 70 (fires) |
| reraise | SystemExit caught in main() and re-raised | 70 (fires) |
| sysexit_zero | `raise SystemExit(0)` in main() | 70 (fires; see note) |
| declared_ret0 / declared_ret1 | top-level `sys.exit(main())`, main returns 0 / 1 | 0 / 1 (no fire) |
| argparse_err | argparse usage error, raised in argparse.py | 2 (no fire) |
| caught_in_main | SystemExit raised and caught inside main(), returns 5 | 5 (no fire) |
| module_raise | `raise SystemExit(4)` at module top level | 4 (no fire) |
| helper_external | SystemExit raised in imported module exthelper.py | 6 (no fire) |
| osexit0 | `os._exit(0)` in main() | 70 (fires; S362 path) |

Second batch (module-level handling): modcatch (helper raises, module-level `try/except SystemExit`, main returns 0) rc 0;
modcatch_then_exit2 rc 2; suppress (`contextlib.suppress(SystemExit)` around helper) rc 0; caught_then_declared3 (caught at module
level, then `sys.exit(3)`) rc 3. Without the hook the same scripts give 0/2/0/3, so the hook changed no status on any of them.
reraise_module (uncaught re-raise at module frame) rc 70 under the hook, 6 without: this is the intended "reaches top level" case.

Verdict: the leg fires exactly where the wording says (SystemExit first raised in a main-script function that reaches the main
script's `<module>` frame uncaught). It does not fire on the counter's top-level `sys.exit(main(...))` with 0 or 1, on argparse's
exit 2, on a SystemExit handled inside main() or at module level, or on a SystemExit first raised in an imported module
(which keeps its status, as the claim's limit (ii) says). Mechanism: the flag is only set when `seen[1] == main` and
`seen[2] != "<module>"` (HOOK 124-129), and a non-matching propagation overwrites it with None (line 129), so the flag does not
go stale. Note (not a falsification): a main()-raised `SystemExit(0)` also fires (sysexit_zero); the frozen counter has no
sys.exit other than line 578 (grep: only lines 577-578 in census/round-87/c1-pointer-counter.py), so no population mutant can
reach it; this is the limit already stated in the claim (ii).

## Q2 — can any harness path exit 70 or call os._exit when the counter is fine?

Receipt: real harness run under hook (census/round-93/c1-false-row-harness.py with the frozen counter, population
c1-false-rows.tsv, lane clone in scratch, ~74 s): `SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0`, harness rc=0,
stderr empty, 0 `SOUJI` markers in stdout or stderr, 66 `match=yes`.
Static: the harness contains no os._exit and no exit other than line 564 (`sys.exit(main(...))`, grep above). Its return codes
are 0/1 (560) and 2 for fatal setup (402-450). The only uncaught-exception paths that could reach the sentinel are operations
outside try blocks (e.g. open(lane/lfile) at 443 and 479, int(exp_rc) at 469 for a pinned population): those are harness faults
(not "counter is fine" cases), and the rule scoring them errored is the intended behaviour. None fired on the frozen population.
Verdict: no harness path exits 70 or calls os._exit when the counter is fine (observed on the full 66-row population).

## Q3 — does every harness branch print the counter's real returncode, negatives included?

Every ROW branch prints the raw `p.returncode`:
- ledger-drop/ledger-trim 471-472: `rc={p.returncode}`; the rc=2 early branch 466-467 prints the literal `rc=2` only inside the
  guard `if p.returncode == 2` (464), so the literal is correct.
- ledger 512-513 (guard 505, literal rc=2 at 507-508 under the same guard).
- ledger-resolve 533-534 (guard 526, literal at 528-529).
- forge 557-558 raw; forge `not m` error branch 547-548 raw `rc={p.returncode}` (a signal-killed counter prints `rc=-9 match=error`).
verdict regex `rc=(-?\d+) match=` (search 221) captures negatives; verified: verdict(1, "ROW x rc=-9 match=no") -> errored;
verdict(70,...) -> errored; verdict(1,"ROW x rc=1 match=no") -> yes; verdict(0,"") -> no; verdict(2,"") -> errored; verdict(1,"") -> errored.
Note (non-issue): the regex takes the first " rc=N match=" on a line; on match=error lines the detail repr follows and could in principle
contain text, but the counter's stderr is only fixed C2-COUNTER-FATAL text, so no false match occurs.
Verdict: every branch prints the real returncode; negative values reach the signal leg.

## Q4 — can a non-crash mutant reach errored?

- A mutant cannot make the counter exit 70 by its own code: gen() maps only tokens `==,!=,<,<=,>,>=,and,or,True,False,not` and
  NUMBER `0`<->`1` (search 187-213); the token `70` is never produced. So no mutant reaches the CRASH_RC branch by a swap.
- A git child killed by a signal does not reach errored: probe (scratch, under hook): a parent whose child printed child_rc=-9
  and which then exits 0 prints the ROW rc=0 line and verdict = no (survived); the same with exit 1 gives yes. Only the counter's
  own returncode is read (harness 459-461 p.returncode), so a child signal is not an errored verdict unless the counter itself exits negative.
- Mutants that make the counter raise an uncaught exception (non-SystemExit) now become errored, where the r94 rule gave killed
  (exit 1 with match=no rows). This is the crash the claim names (the claim's targets h-crash-late and h-crash-index are the same
  shape and are errored both before and after), so it is the intended change, not a non-crash mutant. Population-level effect:
  for the wave to report (the claim does not talk about the population; the prereg's stated limit (i) says so).
- Mutants that trigger an unraisable exception without a raise in the counter's own flow (e.g. a __del__) would now be errored
  while exiting 0 under r94. A probe confirmed this (del_raise.py: under hook rc=70 with `SOUJI-R95-CRASH unraisable RuntimeError`,
  without hook rc=0). The frozen counter has no __del__, threading, atexit, or os._exit (grep), so no population mutant can introduce
  one by a 0/1, operator or boolean swap; the only route is a swap that makes an existing call raise, which is a crash anyway.
Verdict: no non-crash mutant can reach errored through the frozen population's mutation alphabet; the exception-to-errored change is
the intended crash behaviour and is recorded as a population effect, not a claim falsification.

## Q5 — does the claim sentence say anything the predicate does not check?

Claim sentence (prereg C1, line 25-32): "the sentinel also ends the process with exit 70 on sys.unraisablehook, threading.excepthook,
any os._exit call, and a SystemExit that reaches the main script's top level after being first raised inside a function defined in
the main script ... the rule also scores a negative rc as errored".

- sys.unraisablehook: the CHECK script (lines 153-176) and the predicate's CHECKS tuple (177-178) have no unraisable mode. The
  unraisable leg is only reached indirectly through the atexit check (`atexit.register(lambda: 1/0)`), and my del_raise probe
  shows the leg works (rc 70, `SOUJI-R95-CRASH unraisable RuntimeError`). So the sentence is true, but the predicate does not check it
  directly. Observation, not a falsification (a claim about a hook the predicate does not name is covered only if the atexit path
  routes through it on CPython 3.14.8, as stated in the knowledge file's limits).
- any os._exit call: predicate checks os._exit(1) only (CHECK osexit 168). My osexit0 probe gives 70, so the "any" wording holds
  on the code path (line 117-118 replaces os._exit with no argument check).
- negative rc scored errored: the predicate exercises this only through h-sigkill (rc=-9 on the counter). The harness-level negative
  path (rc=-9 in an ROW line) is verified by verdict() unit probes above, not by the predicate.
- "keeps the verdicts of the five r94 targets": the predicate prints counts (errored=7 killed=2 survived=1); the per-target SEARCH
  lines the prereg names are the check. The frozen control counts (errored=2 killed=5 survived=3) are consistent with the claim
  arithmetic: five r95 channels move from r94 verdicts to errored, r94 targets keep 2 errored, 2 killed, 1 survived. I did not run the
  predicate itself.
- Stated limit (ii) (a counter legitimately calling sys.exit inside a helper scores errored) is consistent with Q1, since the helper
  leg fires for any uncaught SystemExit from a main-script function.

## Falsification record
- FALSIFIES-WORDING: none.
- FALSIFIES-NUMBER: none observed by me (I did not run the search or the control; numbers were not re-derived).
- NO-FALSIFICATION for the C1 sentence as worded, on the probes listed above.
  Open items for the L1 (not falsifications): (a) the predicate has no direct unraisablehook check (Q5); (b) mutant-induced uncaught
  exceptions now score errored instead of killed, a population-level change the wave should report (Q4).

## Tooling and scratch
- No tool was installed. Probes used the host python3 (3.14.8, the interpreter the hook was observed on) and `sh`.
- Scratch: /fast/scratch/hyaku/souji-r95/R95ReviewerC1/ (hook/, check.py, t/, t2/, t4/, harness work tree) was removed after the
  receipts were written; no clone or background process was left running (the harness job bg_2338 completed).
