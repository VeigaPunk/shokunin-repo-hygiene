# souji round 94 — plan, dispositions and amendments (L1 SoujiR94)

Lane base `eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536` (r93 closed admitted). Contract: `census/round-94/preregistration.txt`
(commit F `4ad74b9d`). Amendments below never widen a frozen sentence; a wave artifact that falsifies a claim's wording
is recorded here as a narrowing or an honest stop before filing (Amendment 59).

## A0 — before the wave

### A0.0 Claim choice (L1 planner seat)

- Load: MISSION.md, AXES.md, the SOURCES contract in CORPUS.md, lane SCORECARD.md `### Planned (r94)`, the r93
  non-author spot-check (`corpus/lessons/round-93-verifier-spotcheck.md` §5 routed items 1-5), R93Sentinel M1
  (`.ufo/waves/round-93/w1/R93Sentinel.md`, `repro/h-crash3.out`) and plans/round-93.md A3.
- Lowest owned non-retired axis: calibration 7 (SCORECARD `## Axes`) → C1. Routed item 2 (the kill rule scores an
  uncaught counter exception as killed) is C1: the search's verdict is the lane's self-assessment of a mutant, a crash
  is the observed state, and the counted quantity is the mismatch (crash fixtures scored killed, 2 → 0). Q170 (a
  crash-separating kill rule is tested with a crashing mutant through the same harness before it is cited) is the
  criterion r94 now meets: two crash fixtures run through the r93 harness.
- Routed item 5 (`c2-forgery-probe.py` exits 1 with a traceback when `--work` exists) is C2, named operability: the
  surface is the probe's exit-code contract (setup vs verdict); the arms counter's r93-probe run (conform=3) is the
  command that shows it unmoved. The L1 widened the routed single case to eight setup arms it could enumerate.
- Not claimed, carried: routed item 1 (C1 harness reproducibility from committed bytes), item 3 (clauses, not
  spellings; the 76 residual survivors), item 4 (KFF19 second length/filler; fixture scorer catching in-process
  exceptions).
- Sourced claim: C1 rests on S357 (Stryker Mutator, Mutant states and metrics: the Runtime error state, distinct from
  Killed and left out of the score) and S358 (sysexits(3) EX_SOFTWARE 70, the sentinel's exit code), both opened
  2026-11-09; knowledge entry `corpus/knowledge/mutant-crash-is-not-a-kill.md`.
- Fresh-start bindings (addendum, r59 prerequisites): the do-nothing and forgery controls of both claims were run and
  committed (P2 `39d4163a`) before F; the positive arms are inside each control (the two semantic kills and the
  survivor keep their verdicts; the probe's verdict arms P1/P2), so blanket refusal is not a gain (FA, GA).

### A0.1 Pre-freeze feasibility

Disclosed in `census/round-94/controls/prefreeze-feasibility-note.txt`: forgery FA's per-mutant harness.out files (the
sentinel active) and the C2 forgery receipts (GA/GB conform=9 each) predict both after arms; neither after arm was run
before F.

## Wave findings and amendments (after WAVE-DONE; `.ufo/waves/round-94/w1-results.json`, 12/12 settled)

### A1 — C1 stated limit (ii): the list of unseen crash channels was not exhaustive (FALSIFIED as worded; narrowed)

R94ScoutSources FW1 (`.ufo/waves/round-94/w1/R94ScoutSources/repro-sysexit-gap.out`: `raise SystemExit(1)` → child
rc=1, `verdict=yes`) and R94Sentinel §1/F1 (`.ufo/waves/round-94/w1/R94Sentinel/receipts/out-F.txt`: a counter whose
`atexit` callback raises at shutdown exits 0, harness `mismatches=0`, r94 verdict `no`). Limit (ii) read "The sentinel
covers an uncaught exception in the main thread of a Python process started with site enabled; os._exit, signals,
thread exceptions and a counter that legitimately exits 70 are not distinguished." **Narrowed sentence (replaces
it; nothing widened):** "The sentinel covers an uncaught exception OTHER THAN SystemExit raised in the main thread
of a Python process started with site enabled (S359); SystemExit (any code), exceptions raised in atexit callbacks or
__del__ finalizers (routed to sys.unraisablehook; the exit status is kept, so such a mutant can score survived),
os._exit, signals, thread exceptions and a counter that legitimately exits 70 are not distinguished." The claim
sentence, predicate and numbers are unchanged: both targets raise RuntimeError/IndexError in the main body.

### A2 — C1 knowledge entry: the "uncaught exception exits 1" premise had no source row (grounded; no claim change)

R94ScoutSources FW2: `corpus/knowledge/mutant-crash-is-not-a-kill.md` stated the exit-1 premise as fact with only
S357/S358 behind it. The entry now marks it observed (own-work receipts: `controls/c1-control-r93-rule.txt` rc=1 on
both crash fixtures; `controls/c1-forgery-out/FB.out`) and adds S359 (Python `sys.excepthook`/`unraisablehook`,
opened 2026-11-09) for the hook's SystemExit exclusion and the unraisable channel. The claim does not rest on the
premise; its numbers are measured.

### A3 — C1 predicate strength: the five-target number does not by itself prove the sentinel (reading; stated limit)

R94Critic C1 (`R94Critic/receipts/offline-rule-eval.out`): on the no-sentinel harness outputs, a rule fitted to the two
fixtures (`got=-` present OR all 66 rows `rc=1`) also reads `errored=2 killed=2 survived=1`. The claim sentence
attributes the result to the filed search, which is true (R94ExecC1, R94ReviewerC1 re-ran it; M4/M7 in R94MutC1 show
the ROW `rc=70` disjunct and the PYTHONPATH prepend are load-bearing: removing either fails the predicate). **Reading
recorded:** "the predicate shows the filed search's verdicts on five targets; that the sentinel, not a fitted
pattern, separates crashes is evidenced by the `rc=70` ROW lines (66 and 1, `records/c1-after-harness/`) and the
full census (R94ExecCensus: 28 changed verdicts, all `yes`→`errored`, all with `rc=70` rows), not by the five-target
number alone." No sentence widened.

### A4 — C2 instrument docstring "Every setup failure exits 2" (FALSIFIED as worded; narrowed)

R94Critic (`R94Critic/receipts/c1.err`: a readable non-UTF-8 `--tool` → UnicodeDecodeError, exit 1) and R94ReviewerC2
(`R94ReviewerC2/probe-edge-fast.log` T3: a `--work` whose parent is a regular file → NotADirectoryError, exit 1;
`probe-edge2.log` T6/T7: non-UTF-8 `--tool`/`--before` → exit 1; T9: a hanging fixture has no timeout) and R94Sentinel
F6 (`R94Sentinel/receipts/out-writefail.txt`: a forgery copy that cannot be written mid-run → traceback, exit 1). The frozen
probe's docstring (census/round-94/c2-forgery-probe.py lines 5-6) says every setup failure exits 2; the claim says
"refuses every other setup ARM with exit 2" (the eight arms), which holds. **Narrowed reading of the instrument
sentence (the file is frozen and not edited):** "the setup failures the r94 probe refuses with exit 2 are: --work
under /tmp, an existing non-directory --work, a non-empty --work, a --fixture/--tool/--before that is not a readable
regular file, a fixture that prints no SUMMARY line, and a forgery edit that does not apply once; a non-UTF-8
--tool/--before, a --work whose parent is a regular file, a write failure after the checks and any other uncaught
exception still exit 1, and a
hanging fixture is not timed out." Routed to r95.

### A5 — C2 predicate strength: the ten arms certify a chosen surface (reading; stated limit (i) holds)

R94Critic C2 (`R94Critic/receipts/probe-cheap.py`, `c2-cheap-armname-receipt.txt`): a probe that special-cases the
arms' `--work` basenames reaches `conform=10` without running anything. R94MutC2: two setup checks are unbound by
the arms (M10 edit-applies-once rc 2→1; M11 the /tmp guard), M05 is masked by the forgery-loop check. Stated limit
(i) already says the arms are chosen by the L1; the discipline is evidenced by the code, by GA/GB each refused by
exactly its target arm, and by R94ReviewerC2's off-arm probes (chmod 000 fixture, read-only empty --work, missing
intermediate --work path: all conform). No sentence widened.

### Neutral / within stated limits

- R94ExecC1, R94ExecC2, R94ReviewerC1, R94Scribe: every number re-derives on committed bytes with matching pins;
  R94ReviewerC1 Q1: all four counter-launch branches of the harness print `rc=<counter rc>`, so a main-body crash
  is visible on every branch.
- R94ExecCensus (reported, not claimed): full re-score, r93 rule `errored=20 killed=167 survived=76`, r94
  `errored=48 killed=139 survived=76`; 28 changed verdicts, all `yes`→`errored` with `rc=70` rows; survivor sets
  identical; one hung (a272c34) in both.
- R94MutC1: 3 killed (M3, M4, M7), 5 equivalent, 2 unbound (M6 `endswith` position, M8 precondition no-op) — routed.
- R94Connector: no sibling owns the surface (kama doctrine `error-is-not-a-verdict`, revenger `mutate8.py`
  counter-example, audio `ldstub` sitecustomize precedent); SOURCES rule 2 pass (2 added rows at that time, 0
  removed); r95 draft adopted into SCORECARD `### Planned (r95)`.
- R94ScoutSources: S357/S358 live byte-identical, quotes 1× each; PIT `DetectionStatus` REJECT (out of province, no
  consumer), the round's reject sample.
