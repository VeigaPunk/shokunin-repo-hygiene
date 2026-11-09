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
