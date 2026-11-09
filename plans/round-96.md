# souji round 96 — plan, dispositions and amendments (L1 SoujiR96)

Lane base `689d1c9570a5df2344e16a5916c49e24b46823ab` (r95 closed admitted; its non-author spot-check
`corpus/lessons/round-95-verifier-spotcheck.md` §7 routed items). Contract: `census/round-96/preregistration.txt`
(commit F). Amendments below never widen a frozen sentence; a wave artifact that falsifies a claim's wording is
recorded here as a narrowing or an honest stop before filing (Amendment 59).

## A0 — before the wave

### A0.0 Claim choice (L1 planner seat)

- Load: MISSION.md, AXES.md, the SOURCES contract in CORPUS.md, lane SCORECARD.md `### Planned (r96)`, the r95
  non-author spot-check (`corpus/lessons/round-95-verifier-spotcheck.md` §7), plans/round-95.md A1/A3/A5/A6.
  MANIFEST: souji r90–r95 admitted — no pause, no fresh-start obligation this round.
- Lowest owned non-retired axis: calibration 7 (SCORECARD `## Axes`) → C1. Routed item 1 (the SystemExit leg's
  declared-exit shape table `mismatched=6` carried, Q172 precondition: the leg clears only a terminating exception,
  and the table must read 0) is C1: the search's verdict is the lane's self-assessment of a mutant, the caught-at-
  `__main__` SystemExit is the observed state, and the counted quantity is the mismatch (declared shapes the r96
  hook turns into 70, 6 → 0, with terminating helper-raised exits staying 70). The r95 wave found a `finally` also
  fires `EXCEPTION_HANDLED` (A1), so the clear is scoped to `<module>`; a3b (try/finally, still terminating) stays
  errored by design and is counted as a crash shape, not a mismatch.
- Routed item 3 (S13 binds the /tmp guard — it does not; `plans/round-95.md` A5) is C2, named operability: the
  surface is the probe's exit-code contract; the r95 probe under the twenty-arm counter (conform=19, T1 hung) is the
  command that shows it unmoved. T1 (a fixture that escapes its process group with the pipes held) is the A6 surface;
  T2 (read-only --work) is the r94 mid-run write failure, T3 binds the non-integer --timeout and T4 the abort
  fixture the r95 arms left unbound.
- Not claimed, carried: routed item 2's r95 A3 crash path (now fixed in the r96 hook, reported not claimed beyond the
  signal-safe write — the E16/E18 full-pipe and E3c handler shapes are wave evidence), hook scope to the counter
  subtree (A4: the id discipline already fails closed, r96 keeps the subtree scope deliberately), a finalization-time
  `__del__` fixture, the harness-side crash target (r94 routed 2), KFF19 second length/filler, fixture scorer
  exceptions, KFF20 mirrors, the r91 variant tools (r93 routed 4).
- Sourced claim: C1 rests on S365 (Python `sys.monitoring` EXCEPTION_HANDLED: "An exception is handled.") and S366
  (Python `os.set_blocking`: "Set the blocking mode of the specified file descriptor."), both opened 2026-11-09
  (captures `census/round-96/srcs/monitoring.{html,txt}` and `os.{html,txt}`); C2 rests on S367 (Python
  `subprocess` `start_new_session`, 22 words, opened 2026-11-09, capture `census/round-96/srcs/subprocess.html`).
  Knowledge entries: `corpus/knowledge/crash-channels-beyond-excepthook.md` (r96 audit section) and
  `corpus/knowledge/deadline-owned-reaping.md` (new).
- Controls: the do-nothing and forgery controls of both claims were run and committed (P2) before F; the positive
  arms sit inside each control (the ten r95 targets keep their verdicts under both searches; P1/P2), so blanket
  refusal is not a gain (FA, GA). FD (no EH clear) is refused by the declared-shape table (mismatched=2), not by the
  target-10 summary, which it leaves unchanged — the runner asserts both.
- `Plans this round carries from the r94 routed items`: m5/m6/g2 clause shapes and LD5 `unresolved=1`, the 76
  residual survivors, the r84–r91 clause-battery docstring that calls a harness error a kill, harness-side crash
  target, `--work` TOCTOU/unix-surface concerns (C2 T2 covers the read-only half only).

### A0.1 Pre-freeze feasibility

Disclosed in `census/round-96/controls/prefreeze-feasibility-note.txt`: both after arms were trial-run in scratch
before F (C1 on P1-identical bytes: `SEARCH-SUMMARY generated=10 ... errored=7 killed=2 survived=1` with
`mismatched=0`; C2 with the pipe-holder trial at `--timeout 5`: `C2-FORGERY-FATAL: the fixture run for the positive
control exceeded --timeout 5s; its process group was killed` EXIT 2, and the full twenty-arm counter
`conform=20`); the after receipts (A) are re-run after F on committed bytes.

### A0.2 Round shape

One v1 wave, 12–13 seats (policy band 8–16): 3 executor, 3 reviewer, 1 critic, 2 mutation-tester, 1 sentinel,
1 connector, 1 scout, 1 scribe. Attack seats (reviewer, critic, mutation-tester, labrat): ≥25 %. The L1 holds the
canonical planner seat (the validator rejects `planner`); the bounded planning data-walk rides the connector seat.
Residual calls: none planned.

## Wave findings and amendments (after the seat reports; wave w1, 13 seats)

Amendments below never widen a frozen sentence. Each falsifying artifact is named with its seat and the line
it falsifies; the ledger `.ufo/waves/round-96/claim-falsification.tsv` points at these amendment ids.

### A1 — C1 "keeps a terminating helper-raised exit errored": FALSIFIED as unqualified; the EH clear is a TRADE (harmed)

Artifacts: `R96ScoutSources.md` §3 (module-level `finally`), `R96ReviewerC1.md` Q1 `q1e` (re-raise of the same
exception object at `<module>`). Re-derived by the L1 (scratch `reg/fshape_*.py`, frozen HOOK extracted from each
search file, same `sitecustomize` method as `declared-shapes.py`):

| shape (terminating, plain rc 1) | r95 hook | r96 hook |
|---|---|---|
| `helper()` raises SystemExit, module-level `try/finally: pass` | 70 (errored) | **1 (declared)** |
| `helper()` raises SystemExit, module-level `except SystemExit: raise` | 70 (errored) | **1 (declared)** |
| `helper()` raises SystemExit, `try/finally` inside the helper (a3b) | 70 | 70 |

Cause: `_souji_handled` (EXCEPTION_HANDLED) clears the foreign mark whenever the callback's frame is `<module>`.
CPython fires EXCEPTION_HANDLED in the frame that owns a `finally` and at a re-raising `except`, so a terminating
exit passing through a module-level frame is cleared. The clear is scoped by frame name, not by "handled".

Trade on the table: t1/t4 (caught at top level, plain 0) improve 70 → 0 (r95 hook `mismatched=2` → r96 `0`);
the two terminating module-level shapes above regress 70 → 1 (r95 scored them errored, correctly). The shape table
has no module-level `finally` or re-raise shape, so its `mismatched=0` does not see the regression.

Verdict for C1: **harmed — the trade is not admitted** (admission rule: no axis harmed; a trade is not an
improvement). The calibration score stays 7 (no reproducible 0–10 mapping). This is Amendment 59 option (ii):
the deliverable of C1 is this narrowing and the measured trade, not a count. The operator rules.
Routed to r97: distinguish "handled" from "passed through" (a RERAISE/finally-aware rule), and add the module-level
`finally` and re-raise shapes to the table before any calibration claim on the EH leg is re-attempted.

### A2 — C1 "a full undrained pipe cannot block the exit": FALSIFIED for the excepthook and thread channels

Artifact: `R96Sentinel.md` F-1 (E10: faulthandler stack of the hung child). The r96 `_souji_excepthook` and
`_souji_thread` call `sys.__excepthook__` / `threading.__excepthook__` (traceback print through the blocking
`TextIOWrapper`) before `_souji_crash`; both hang on a full undrained pipe (`hook=r96 HUNG`, frame in the print).
Only the os._exit and atexit channels reach the raw write first (`hook=r96 exited rc=70`).
Narrowed sentence (the prereg C1 CLAIM and `corpus/knowledge/crash-channels-beyond-excepthook.md` are corrected to it):
"the marker write itself cannot block on a full pipe (raw `os.write` on a momentarily non-blocking fd 2); the
excepthook and thread channels print their traceback through blocking stderr before the crash path, so they can still
block on a full undrained pipe." Measured: none of the counted numbers move (the CHECK drains its pipes). Routed r97.

### A3 — C1 "momentarily non-blocking fd 2": FALSIFIED by the no-free-id fallback

Artifact: `R96Sentinel.md` F-2 (E5a–E5c, E9b). The HOOK's fallback branch ("no free sys.monitoring tool id") calls
`os.set_blocking(2, False)` and returns: the process continues with a permanently non-blocking fd 2, shared with
children (O_NONBLOCK is on the open file description). After it, `os.write(2)` on a full pipe raises
`BlockingIOError`, and `sys.stderr.write` silently drops data. Reached only when tool ids 3, 4 and 5 are all busy
(disclosed fail-closed path; the CHECK fails closed on it). Narrowed: "momentarily, inside the crash path; the
no-free-id fallback leaves fd 2 non-blocking". Routed r97 (restore the flag in the fallback).

### A4 — C2 STATED LIMIT (iv) "the counter kills it": FALSIFIED (reaping)

Artifacts: `R96Sentinel.md` F-4 (E6a–E6d, real 20-arm run), `R96Scribe` relay from Main (`reapcheck.out`,
`c2scan.out`): the counter's arm-timeout path does `os.killpg(p.pid)` on the probe; the probe is its own session
leader, and the T1 grandchild calls `os.setsid()`, so the group kill never reaches it. Measured: one T1 grandchild
survives every T1 arm run (E6a: pid alive, ppid 1525 after the probe exits 2; reapcheck B: 1 survivor after a
counter-style killpg). The probe's own kill also does not reach it (reapcheck C: survivors 2 after the probe exits).
Narrowed limit (iv): "the probe does not reap the escaped grandchild and stops being held by it; the counter's group
kill targets the probe's session and does not reach the setsid() grandchild, which survives both and is re-parented
to init." Corpus entry `corpus/knowledge/deadline-owned-reaping.md` corrected at both sentences (Limits and the r96
fix paragraph). The C2 number and the T1 predicate are unaffected (T1 exit 2 + FATAL, measured). Routed r97: reap the
grandchild by an identity that is not the process group (per-arm absolute fixture path, verified at act time), and
count surviving T1 grandchildren per run as a number.

### A5 — C2 STATED LIMIT (i) "a fixture that writes unbounded output still blocks on a full pipe": FALSIFIED (mechanism)

Artifact: `R96ReviewerC2.md` Q1a (`flood2.txt`, `floodhang.py`). The probe drains the fixture's pipes through
`communicate()`, so the pipe never fills and the fixture never blocks. What is unbounded is the probe's memory:
an unbounded-rate, unbounded-duration fixture drove the probe to 27.3 GB RSS and a SIGTERM at 36 s with `--timeout 8`,
and no FATAL line. A rate-limited flood (`slowflood.py`) and a finite 200 MB flood (`flood.py`) are refused cleanly
(exit 2, FATAL, 8.0 s / 1.3 s). Narrowed limit (i): "a fixture that writes unbounded output in unbounded time exhausts
the probe's memory and can end the probe before --timeout fires; the arms do not include such a fixture." Routed r97
(cap the captured bytes; a read limit is part of the instrument).

### A6 — C2 arm docstrings and labels (not claim sentences): neutral, routed

Artifacts: `R96ReviewerC2.md` Q2 (T2 mechanism: the refusal is the fixture's `makedirs`, not the probe's `write()`;
T3 docstring lists a "non-integer --timeout" class no arm exercises; `c2-setup-arms.py` header says "sixteen arms"
for a tuple of twenty), `R96Connector.md` §2.3. These are docstrings of the frozen counter; none is a claim sentence.
Recorded here so the r97 instrument commit can correct them; no count depends on them.

### A7 — C2 counted quantity: the number certifies exit-code discipline, not the pipe mechanism (undermined, not falsified)

Artifact: `R96Critic.md` (2): a basename special-case in the probe reaches `ARMS-SUMMARY arms=20 conform=20`, EXIT 0
(`c2-cheatA-fullrun.txt`). `R96MutC2.md` survivors M3 and M5 (the killed-path Fatal and the `--timeout <= 0` check
are not load-bearing for the arm outcomes). No prereg sentence is false: the claim commits to `_wait_output`, which the
frozen probe has. Narrowed reading of the counted quantity: "conforming arms = exit 2 with one FATAL line within the
arm timeout"; it does not prove the pipe-EOF mechanism, which is shown by the source diff (H5) and by T1 measured
against the r95 probe (`hung` vs `exit 2`), not by the count alone. Routed r97: a T1 variant with a different basename,
and a post-run count of surviving grandchildren (A4).

### A8 — C2 first-run predicate failure: unattributed SIGTERM on arm S12, disclosed

Artifacts: `R96ExecC2.md` (HIGH mismatch), `R96MutC2.md` (baseline). The first after-arm run printed
`ARM S12 exit=-15 … ARMS-SUMMARY arms=20 conform=19`, EXIT 1; the first r95-control run printed the same S12 -15
(conform=18); the first MutC2 baseline printed it too. Each of the three first runs overlapped other seats'
probe batches on this host. Reruns on identical bytes: after arms `conform=20` EXIT 0 (rerun 2); control `conform=19`
EXIT 1 (the frozen P2 value). Not reproduced in four direct S12 runs (exit 2, FATAL, 10–120 s). The counter sends
only SIGKILL and only at the arm timeout (which prints `hung`), so -15 came from outside the counter; the sender was
not found. **C2's predicate is recorded as met on rerun 2 of the after arms; the first run's failure stays on the
record.** Routed r97: the counter must record a signal exit distinctly and never coerce it.

### A9 — C1 control label "r94-rule mismatched=6": FALSIFIED as a label, corrected here

Artifact: `R96ReviewerShapes.md` §3. The `mismatched=6` is the r95 declared-shapes receipt (r95 hook, plain-vs-hooked
scoring), `census/round-95/records/declared-shapes.txt`. No r94 search reproduces 6 on these twelve scripts (the r94
hook gives 4 under the r96 kind logic, 0 under plain-vs-hooked). The label "r94-rule control" in
`census/round-96/controls/prefreeze-feasibility-note.txt` and in the `c1-survivor-search.py` docstring is wrong; the
correct label is "the r95 declared-shapes receipt (r95 hook)". Counts are unchanged; the do-nothing picture is the
r95 hook's `mismatched=2` on the r96 scripts (re-derived, `R96ExecC1` 05-r95-shapes).

### A10 — C1 census and survivors (no claim sentence): neutral

Artifacts: `R96ExecCensus.md` (full population: r96 `killed=139 errored=53 survived=76`, r95 identical; zero differing
verdicts; the seat's expectation "r95 errored=48" was not reproduced and is not a claim), `R96MutC1.md` (14 one-edit
mutants: 8 killed, 6 survived — M04 the sysexit reason assertion, M06 `os.set_blocking`, M08 the main-file test,
M10 the tool-id range, M12 the negative harness rc, M14 the reason assertion loop). The survivors show what the
predicate does not bind; the predicate's counted quantities are not changed by them. Routed r97 as predicate
binding work.

### A11 — Scout source rows and the teaches over-claims (S365–S367): routed, rows frozen

Artifact: `R96ScoutSources.md` §1–2. All three rows re-verify live (hash, size, quote, count, locator). Their
`teaches` cells over-claim: S365's teaches says a finally "does not fire this event", which the frozen preregistration
and the observed trace contradict (a finally does fire EXCEPTION_HANDLED); S366's teaches adds a pipe-full consequence
its quote does not carry; S367's teaches adds the new-process-group inference its quote does not carry. CORPUS rule 2:
rows are append-only, so the honest repair is a superseding row, not an edit. The scout's candidate, setsid(2)
(`https://man7.org/linux/man-pages/man2/setsid.2.html`, 17-word quote, occurrence 1), is **admitted** as a supporting row
(S368) only if the L1 opens it this round — it was opened by the scout seat, and this round's opening is recorded in
the L1's Gate block (see the knowledge entry). Routed r97: supersede S365/S366/S367 with corrected teaches.
