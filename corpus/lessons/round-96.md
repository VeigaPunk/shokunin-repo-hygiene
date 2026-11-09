# Round 96 — the EH clear is a trade; the probe's counter does not kill what the docs said it kills

Lane base `689d1c9570a5df2344e16a5916c49e24b46823ab` (r95 closed admitted; spot-check
`corpus/lessons/round-95-verifier-spotcheck.md` §7). Instruments P1 `0656de3f`, controls P2 `4dd8a103`, freeze F
`c1209623`. Wave: one v1 wave, 13 seats, `w1` (attempt 1, SoujiR96). Amendments: `plans/round-96.md` A1–A11.

## Claims

- **C1 (calibration 7).** The r96 EH clear makes the declared-shape table `mismatched=0` (r95 hook 2). Verdict:
  **harmed (trade)**. The same frame-name clear turns terminating module-level `finally` and re-raise exits from
  errored (r95 70) to declared (r96 1). Reproduced by the L1 (`plans/round-96.md` A1). Not admitted; score stays 7.
- **C2 (operability 8).** The r96 probe refuses the T1 pipe-holder with exit 2 + FATAL at its own timeout (r95: `hung`);
  `ARMS-SUMMARY arms=20 conform=20` on rerun 2. Verified, narrowed: counted quantity is exit-code discipline (A7); the
  counter does not reap the grandchild (A4); a first-run S12 SIGTERM stays on the record (A8).

## Gate

Source rows this round (URL · access date · located quote, ≤25 words · location):

| row | URL | access | located quote | location |
|---|---|---|---|---|
| S368 (new, tier A) | https://man7.org/linux/man-pages/man2/setsid.2.html | 2026-11-09 | "The calling process also becomes the process group leader of a new process group in the session" (17 words) | § DESCRIPTION; capture `census/round-96/srcs/setsid.2.html` sha256 52cbc190…, occurrence 1 |
| S369 (supersedes S365) | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 (capture reused; live bytes re-fetched by the scout seat, identical) | "An exception is handled." (4 words) | § Events, EXCEPTION_HANDLED; capture `census/round-96/srcs/monitoring.html` |
| S370 (supersedes S366) | https://docs.python.org/3/library/os.html | 2026-11-09 (capture reused; scout re-fetch identical) | "Set the blocking mode of the specified file descriptor." (9 words) | § File Descriptor Operations, os.set_blocking; capture `census/round-96/srcs/os.html` |
| S371 (supersedes S367) | https://docs.python.org/3/library/subprocess.html | 2026-11-09 (capture reused; scout re-fetch identical) | "If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess." (22 words) | § Popen Constructor, start_new_session; capture `census/round-96/srcs/subprocess.html` |

Rejected or screened candidates: `write(2)` § ERRORS EAGAIN (https://man7.org/linux/man-pages/man2/write.2.html, quote
"The file descriptor fd refers to a file other than a socket and has been marked nonblocking ( O_NONBLOCK ), and the write
would block.", 25 words, screened by the scout seat, not rowed: the corpus has no row that needs its scope this round; flip:
a claim that states what a write to a full non-blocking pipe returns).

Sources-census before/after (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`):
before 286 registry rows at the r95 close (census EXIT 0); after 293 rows (S368–S371 added; no existing cell touched);
EXIT 0 at the round end. The W04 duplicate-URL warnings are the expected cross-scope warnings.

Knowledge entries touched: `corpus/knowledge/crash-channels-beyond-excepthook.md` (r96 section rewritten as a trade
verdict), `corpus/knowledge/deadline-owned-reaping.md` (two false limit clauses withdrawn; process-group claim now cites
S368). Both entries' `source:` lines cite the new rows.

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M1 — a clear scoped by frame name, not by "handled".** Class: a predicate gate whose table omits the shape that
  would break it. Evidence: `plans/round-96.md` A1; `.ufo/waves/round-96/w1/R96ScoutSources.md` §3; L1 reproducer
  `fshape_modfin.py` / `fshape_reraise.py` (r95 hook 70, r96 hook 1). Captured-by: none (the twelve-shape table had no
  module-level finally or re-raise shape, and the prereg's limit (i) named only "shapes not in the table" in general
  terms). Fix: r97 RERAISE-aware rule plus the two shapes added to the table. Shown able to fail: the r96 hook prints
  `rc=1` on the module-finally reproducer where the r95 hook prints 70 — the check fails on today's rule.
- **M2 — "cannot block the exit" and "momentarily" written from the fix's intent, not measured.** Class: an absolute
  stated about the crash path without a stack or a second channel. Evidence: `.ufo/waves/round-96/w1/R96Sentinel.md`
  F-1 (E10: excepthook and thread channels hang in the traceback print, before the raw write) and F-2 (E5/E9: the
  fallback leaves fd 2 non-blocking). Captured-by: none before the wave. Fix: narrowed in `plans/round-96.md` A2/A3;
  the r97 instrument restores the flag and routes the traceback print. Shown able to fail: the stack dump (E10) shows
  `hook=r96 HUNG` for the excepthook channel and the faulthandler frame in `_souji_excepthook`.
- **M3 — a kill sentence written without measuring the kill's reach.** Class: a stated-limit about another process's
  fate, copied from intent. Evidence: `plans/round-96.md` A4; `R96Sentinel.md` F-4 (E6c: `killpg(probe.pid)` leaves the
  setsid grandchild alive, two survivors after the counter-style kill); scribe relay `.ufo/waves/round-96/w1/R96Scribe/reapcheck.out`
  (B: 1 survivor, C: 2 survivors). Captured-by: none. Fix: limit (iv) narrowed; the corpus entry's false clauses
  withdrawn; r97 reaps by identity and counts survivors. Shown able to fail: reapcheck B fails the sentence "the counter
  kills it" on today's counter.
- **M4 — a counted quantity that a cheap edit reaches.** Class: a number that certifies an outcome, not the mechanism.
  Evidence: `.ufo/waves/round-96/w1/R96Critic.md` (2): basename special-case reaches `ARMS-SUMMARY arms=20 conform=20`
  EXIT 0; `R96MutC2.md` survivors M3, M5. Captured-by: the critic seat (Amendment 59). Fix: counted quantity narrowed to
  exit-code discipline (A7); r97 adds a T1 variant with a different basename and a surviving-grandchild count. Shown able
  to fail: the cheat's receipt (`c2-cheatA-fullrun.txt`) is reproduced by the seat, so the narrowing is not vacuous.
- **M5 — a label copied from a receipt into the prefreeze note and a docstring.** Class: attribution of a number to the
  wrong instrument. Evidence: `R96ReviewerShapes.md` §3; `census/round-96/controls/prefreeze-feasibility-note.txt`
  ("r94-rule control mismatched=6"); the search docstring. Captured-by: the reviewer seat. Fix: A9. Shown able to fail:
  the r94 search reproduces 4 (r96 kind logic) or 0 (plain-vs-hooked), never 6.

## Wave findings

Seats (13, dispatched by the orchestrator via `.ufo/waves/round-96/w1.ready`, validated under `ufo-wave-policy.json`):
R96ExecC1, R96ExecC2, R96ExecCensus (executor); R96ReviewerC1, R96ReviewerC2, R96ReviewerShapes (reviewer); R96Critic
(critic); R96MutC1, R96MutC2 (mutation-tester); R96Sentinel (sentinel); R96Connector (connector); R96ScoutSources (scout);
R96Scribe (scribe). Attack seats: 8/13. A first ExecC2 run and a first control run each had an unattributed S12 SIGTERM
(A8); reruns on identical bytes conform.
