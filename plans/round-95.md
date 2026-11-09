# souji round 95 — plan, dispositions and amendments (L1 SoujiR95)

Lane base `93c3ef13a9eb9678483518562f3692124db714c2` (r94 closed admitted). Contract: `census/round-95/preregistration.txt`
(commit F `59fd7be0`). Amendments below never widen a frozen sentence; a wave artifact that falsifies a claim's wording
is recorded here as a narrowing or an honest stop before filing (Amendment 59).

## A0 — before the wave

### A0.0 Claim choice (L1 planner seat)

- Load: MISSION.md, AXES.md, the SOURCES contract in CORPUS.md, lane SCORECARD.md `### Planned (r95)`, the r94
  non-author spot-check (`corpus/lessons/round-94-verifier-spotcheck.md` §5 routed items 1-5), plans/round-94.md A1/A4.
  MANIFEST: souji r89 rejected-honest-stop, r90-r94 admitted — no pause, no fresh-start obligation this round.
- Lowest owned non-retired axis: calibration 7 (SCORECARD `## Axes`) → C1. Routed item 1 (SystemExit, os._exit,
  atexit/`__del__` and thread exceptions still scored `yes`/`no`) is C1: the search's verdict is the lane's
  self-assessment of a mutant, the counter dying on a crash channel is the observed state, and the counted quantity is
  the mismatch (crash-channel fixtures scored other than errored, 5 → 0). The signal leg (SIGKILL) was named in r94's
  limit (ii) and is added as the fifth channel.
- Routed item 3 (the r94 probe still exits 1 on a non-UTF-8 `--tool`/`--before` and a file-parent `--work`, and has no
  fixture timeout) is C2, named operability: the surface is the probe's exit-code contract; the r94 probe under the
  sixteen-arm counter (conform=12) is the command that shows it unmoved. Two arms bind the r94 setup checks no r94 arm
  exercised (R94MutC2 M10 edit-once, M11 /tmp).
- Not claimed, carried: routed item 2 (a harness-side crash target binding the harness-exit-70 disjunct), item 3's
  mid-run write failure, `--work` TOCTOU and randomized arm names, item 4 (r93 carried: reproducibility from committed
  bytes, m5/m6/g2 clauses and the 76 residual survivors, KFF19), item 5 (seat temp under the round scratch root — put
  into the wave context as a rule, not a claim).
- Sourced claim: C1 rests on S360 (sys.monitoring RAISE), S361 (threading.excepthook), S362 (os._exit), S363
  (subprocess negative returncode) and S364 (atexit exceptions), all opened 2026-11-09; knowledge entry
  `corpus/knowledge/crash-channels-beyond-excepthook.md`.
- Controls: the do-nothing and forgery controls of both claims were run and committed (P2 `48c5efe9`) before F; the
  positive arms sit inside each control (the five r94 targets keep their verdicts; P1/P2/S1-S8/S13/S14), so blanket
  refusal is not a gain (FA, GA).

### A0.1 Pre-freeze feasibility

Disclosed in `census/round-95/controls/prefreeze-feasibility-note.txt`: both after arms were trial-run in scratch
before F (C1 on P1-identical bytes; C2 with an arms counter whose docstring said "fourteen arms", corrected before P1,
code unchanged). The after receipts (A) are re-run after F on committed bytes.

### A0.2 Round shape — labrat seat runs as reviewer (no claim change)

The prereg's ROUND SHAPE names "1 labrat". The wave validator refused it (`items[8].role "labrat" is not a swarm
role`, first validation run); the seat R95Labrat keeps its single-hypothesis task and runs as `reviewer`. Shape: 3
executor, 3 reviewer, 1 critic, 2 mutation-tester, 1 sentinel, 1 connector, 1 scout, 1 scribe; attack seats 6/13 =
46 %, unchanged. Not a claim sentence.

## Wave findings and amendments (after WAVE-DONE; `.ufo/waves/round-95/w1-results.json`, 13/13 settled)

### A1 — C1 stated limit (ii): the false-positive set of the SystemExit leg is wider than "sys.exit inside its own helper" (FALSIFIED as worded; narrowed)

R95Labrat (`.ufo/waves/round-95/w1/R95Labrat.md` shape table, receipts `R95Labrat/receipts/`): `sys.exit(helper())`
called inside `main` (v3/w1), `raise SystemExit(helper())` inside main (w2), a SystemExit raised in try/finally inside
main (a3b), and a SystemExit first raised in a main-script helper but CAUGHT at module level (t1/t4, plain rc 0) all
exit 70 under the hook. Limit (ii) read "a counter that legitimately calls sys.exit inside its own helper would be
scored errored". **Narrowed sentence (replaces it; nothing widened):** "The SystemExit leg treats only a SystemExit
first raised in the main script's top-level code, or first raised outside the main script (argparse), as declared; ANY
SystemExit first raised inside a function defined in the main script — `sys.exit(...)` called in `main` itself, in a
helper, or in try/finally — is scored errored, and so is one that reaches the top level and is caught there (the leg
does not track whether the exception terminates the process)." The claim sentence ("a SystemExit that reaches the
main script's top level after being first raised inside a function defined in the main script") is literally what
the code does; the predicate and numbers are unchanged — none of the ten targets has these shapes, and the frozen
counter's only exit is `sys.exit(main(...))` at top level.

### A2 — C1 claim parenthesis "ends the process with exit 70 on sys.unraisablehook": not at interpreter finalization (FALSIFIED as worded for one shape; narrowed)

R95Labrat u1/u3/u5: a global object's `__del__` raising at interpreter shutdown AFTER `sys.exit(main())` keeps the
process status (3→3, 0→0); the same `__del__` when the script falls off the end exits 70 (u2). **Narrowed reading of
the unraisablehook leg:** "exit 70 on an exception CPython reports to `sys.unraisablehook` while the sentinel's hook is
installed — atexit callbacks (check `atexit=70`) and `__del__` during the run (R95ReviewerC1 Q4 `del_raise.py`); a
finalizer that raises during interpreter finalization after a SystemExit exit is not reported to it and keeps its
status (CPython 3.14.8)." No target exercises it; numbers unchanged.

### A3 — C1 "any os._exit call": also a normal os._exit(0), and the crash path can hang (FALSIFIED for the deadlock shape; narrowed)

R95Critic and R95Sentinel F3: `os._exit(0)` → exit 70 (a clean exit scored a crash; the word "any" is literal, the
consequence was not in the limits). R95Sentinel F1 (`R95Sentinel/exp/E3c_signal_deadlock.py`,
`E7_thread_deadlock.py`, `E18_headroom.out`): the replacement writes to stderr and flushes before the real exit, so an
`os._exit` from a signal handler or another thread while the main thread holds the stderr lock, or with a full
undrained stderr pipe, HANGS instead of exiting 70 (the search would score such a mutant `hung`, not errored).
**Narrowed sentence:** "the sentinel ends the process with exit 70 on any `os._exit` call — including `os._exit(0)` —
provided the diagnostic line can be written to stderr; a call made while the stderr lock is held (signal handler,
another thread) or with a full undrained stderr pipe hangs." Numbers unchanged (h-osexit calls it from the main thread
with a drained pipe).

### A4 — C1 sentinel scope: every Python process under the harness, not only the counter (stated limit added; no claim sentence widened)

R95Sentinel F3/F4: the hook is on PYTHONPATH for the harness subtree, so a forked child's `os._exit(0)` becomes status
70, a tool that wants `sys.monitoring` id 3 is refused, and the loop may take the reserved OPTIMIZER_ID 5 when 3 and
4 are busy; with no free id the sentinel only prints a line, but the search's CHECK fails closed (`sysexit=1` →
`C1-SEARCH-FATAL`, exit 2). The prereg never said the hook is counter-only; recorded as a limit. R95MutC1: m02/m03
(cross-wiring the thread/os._exit legs to the excepthook function) survive the predicate — the check line binds the
exit code, not which replacement produced it. R95MutC1 also scored m11 (the `declared` CHECK row dropped) a survivor
on the summary alone; the frozen predicate names the full check line including `declared=1`, which m11's line lacks
(`R95MutC1.md` m11 row), so under the prereg's own predicate m11 is killed. Routed: m02/m03.

### A5 — C2 instrument sentence "S13/S14 bind the two r94 setup checks no r94 arm exercised" (FALSIFIED for S13; narrowed)

R95MutC2 PM9 (`R95MutC2/results/P-PM9.out`): with `/tmp/` removed from the probe's prefix guard the predicate still
prints `conform=16`: the probe creates the /tmp dir and the FIXTURE's own refusal yields "no SUMMARY line for the
positive control (exit 2)", so S13 still sees exit 2 + a `C2-FORGERY-FATAL:` line. The arms-counter docstring
(census/round-95/c2-setup-arms.py lines 5-6, frozen) and A0.0 above said S13 binds the r94 /tmp guard (R94MutC2 M11).
**Narrowed reading (the file is frozen and not edited):** "S13 binds that the probe ends with exit 2 and a FATAL
line on a --work under /tmp; it does not bind WHICH check refuses it (the fixture's own /tmp refusal is enough);
S14 binds the edit-once check." The claim's counted quantity (conforming arms of 16) is unchanged; the claim sentence
lists S13 among the arms the r94 probe conforms on, which holds.

### A6 — C2 probe docstring "a fixture run that outlives --timeout ... its process group is killed" (FALSIFIED for an escaping grandchild; narrowed)

R95ReviewerC2 `Q1-pipe-holder.txt` and R95Sentinel F2: a fixture whose `setsid()` grandchild keeps the stdout/stderr
pipes open hangs the r95 probe past its own --timeout (`communicate()` waits for pipe EOF; `killpg` cannot reach a new
session); `Q1u2`: a detached grandchild with pipes closed survives the success path. The probe docstring (frozen)
says the run that outlives --timeout is killed and named. **Narrowed reading:** "a fixture run that outlives --timeout
is ended by killing the fixture's process group; a descendant that leaves the group with the pipes held still hangs
the probe, and one that leaves without them is not reaped." The prereg's stated limit (i) already names "a fixture that
escapes its process group" as the wave's to try; the claim (S12 refused with exit 2) holds.

### A7 — corpus rows S360/S361 (this round's own rows; corrected in place, relative to base still add-only)

R95ScoutSources DEFECT-1/DEFECT-2/OBS-1: S361's locator named a `§ Functions` heading the captured page does not have
(the entry sits under `§ Reference`), and its grounds cell stated "the main thread keeps its exit status" as if
sourced; S360's scope cell said "SystemExit included", which the page never names. Both rows were added in P1 this
round, so they are corrected in place: relative to base `93c3ef13`, `corpus/SOURCES.md` still has only added lines.
The lesson's Gate table carries the corrected locator.

### Neutral / within stated limits

- R95ExecC1, R95ExecC2, R95Critic, R95Sentinel, R95Scribe re-ran predicates/controls/forgeries on committed bytes:
  every number re-derives (C1 `errored=7 killed=2 survived=1` and control `errored=2 killed=5 survived=3`, FA/FB/FC
  3/3; C2 `conform=16` and control `conform=12`, GA/GB/GC 3/3); all pins match.
- R95ExecCensus (reported, not claimed): full population, r95 search vs frozen r94 search — the 263 shared generated
  ids change no verdict (killed 139, survived 76 both); errored 48 → 53 is exactly the five new crash fixtures.
- R95ReviewerC1: no non-crash mutant can reach errored through the frozen mutation alphabet (no `70` token, the
  counter has no `__del__`/thread/atexit/os._exit); every harness branch prints the counter's real returncode.
- R95MutC1: 9/13 mutants killed by the precondition CHECK; m11 killed by the predicate's check-line text (A4); survivors
  m02/m03 (A4) and m07 (equivalent here).
- R95MutC2: PM8/PM10 and CM1-CM3 killed; survivors PM1 (utf-8-sig), PM2 (makedirs try redundant with cli's OSError
  handler), PM3 (write() no-op: no write-failure arm, limit (i)), PM4 (SIGTERM), PM5 (catch-all: limit (i)), PM6
  (`--timeout 0`), PM7 (positive-control conjunct) — routed; PM9 is A5.
- R95Connector: no sibling owns the surface; SOURCES rule 2 add-only; r96 draft adopted into SCORECARD.
- R95ScoutSources: S360-S364 live byte-identical, quotes and counts re-derived; `faulthandler` REJECT (the round's
  reject sample; flip stated), PEP 669/PEP 578/`sys.audit` rejected alongside.
