# souji round 97 — plan, dispositions and amendments (L1 SoujiR97)

Lane base `210084b24de1dd1f1fd499f49b0c70744f099f5f` (r96 closed `ok`, MANIFEST rounds index 1615;
r94/r95/r96 all `ok` — no pause, no fresh-start obligation; fresh-start history read out of prudence anyway:
read `corpus/lessons/round-94-verifier-spotcheck.md`, `round-95-verifier-spotcheck.md`,
`round-96-verifier-spotcheck.md`). Round intent per SCORECARD `### Planned (r97)` (line 2423) and the r96
spot-check §7 items 1, 4, 5, 6. Contract: `census/round-97/preregistration.txt` (commit F). Amendments below
never widen a frozen sentence; a wave artifact that falsifies a claim's wording is recorded here as a
narrowing amendment or an honest stop before filing (Amendment 59).

## A0 — before the wave

### A0.0 Claim choice (L1 planner seat)

- Load: MISSION.md, AXES.md, the SOURCES contract in CORPUS.md, lane SCORECARD `## Axes` + `### Planned (r97)`,
  the r96 non-author spot-check (`corpus/lessons/round-96-verifier-spotcheck.md` §7), plans/round-96.md A1–A11,
  corpus/lessons/round-96.md `## Gate`/`## Mistakes`. MANIFEST: souji r90–r96 `ok` — no pause, no fresh-start
  obligation this round.
- Lowest owned non-retired axis: calibration 7 (SCORECARD `## Axes`) → C1. Routed item 1 (r96 spot-check §7.1):
  the EH-clear trade (t1/t4 70→0 vs module-level `finally`/re-raise 70→1 wrong). C1 resolves it with a
  RERAISE-aware eligibility latch: a module-level EXCEPTION_HANDLED clears the foreign mark only if NO
  RERAISE/unwind has occurred for that exception object after the FIRST EH at `<module>`. Measured prototype
  (scratch `/fast/scratch/hyaku/souji-r97/proto`, 9 shapes): terminal module-finally and terminal explicit
  re-raise fire 2 RERAISEs each; caught shapes (t1, t4, naked except) fire 0; a3b fires 2 inside `helper`
  (renders it errored, as r96). Predicted table: shapes=14 (12 inherited + x1 module-finally + x2 module
  re-raise), mismatched=0 under the new hook; the 2 new crash shapes score 70 (errored, correct); the r96
  hook scores mismatched=2 (x1/x2 at 1, wrong). The ten r95 targets keep verdicts (errored=7 killed=2
  survived=1), so the ten-target summary does not discriminate the fix (same as r96); the four forgery
  controls FA/FB/FC refuse it, FD (no EH clear at all) reproduces the r96 shape mismatch.
- Routed items A2/A3 (plans/round-96.md A2/A3, spot-check §7.6): folded into C1 as measured legs of the same
  instrument file and same commit — (A2) `_souji_excepthook` and `_souji_thread` call the raw signal-safe
  `_souji_crash` BEFORE `sys.__excepthook__`/`threading.__excepthook__`, so a full undrained pipe cannot block
  the exit on those channels either (marker is still best-effort); (A3) the no-free-tool-id fallback restores
  fd 2's blocking mode (`os.set_blocking(2, True)`) instead of leaving it non-blocking. Both legs are
  falsifiable via the CHECK reason lines and a shape/control receipt; the RERAISE-latch leg is the causal
  center of C1.
- Routed item 2 (r96 spot-check §7.2, Open L0 #2 reaping authority): NOT claimed. The lane does not kill any
  process; the A4 reaping fix is folded into C2 as `counter-owned-reaping` naming the lane's own arm spawn.
  An L0 question is appended for the operator ruling.
- C2 (operability 8). Routed items A4/A5/A8/A6 (plans/round-96.md, spot-check §7.6): the r97 counter
  `/fast` reaps the T1 setsid grandchild by identity (the fixture's per-arm absolute path is the identity
  token, verified at act time against the printed `fixture-pipe-holder.py` sha256), and prints a
  `SURVIVORS` count per run (the r96 probe leaves 1, the r97 counter leaves 0). The probe caps captured
  output (a `--max-output` byte cap; the unbounded-rate fixture is refused exit 2 within the timeout
  instead of exhausting probe memory). The counter records a signal exit (-15) distinctly (`exit=signal`
  plus the arm set), never coerced. Docstring corrections (sixteen-arm line, T2/T3 mechanism) ride the same
  commit. Forgery controls GA/GB/GC still refuse; a fourth forgery GD (survivor-cheat: report survivors=0
  without reaping) is refused by the identity check.
- Not claimed, carried: the forge-return channel (r92 limit ii), p2 basename granularity, p3 punctuation
  lookahead, p7 `_regular` symlink leg, p8 `token_ok` hyphen marker, the `fleet:` symlink leg, battery
  `--only`/`--expect-killed` stale defaults, r85/r86 C2 list, `_regular` pathspec framing, quarantine
  intro-blob digest row, r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, r17 240 s runners,
  r85–r87 K4 print-only `rc=`, A10 M04/M14 reason-assertion binding (rides C1's forgery runner as a fifth
  control FE: a dropped reason assertion must fail the CHECK), A9 label correction (adopted in the r97
  docstring; the r96 `mismatched=6` label was the r95 receipt).
- Sourced claim: C1 rests on a new `sys.monitoring` RERAISE row (S372), opened this round; Q172's shape
  table is extended 12→14. C2 rests on S368 (setsid(2), process-group identity).
- Controls: the do-nothing and forgery controls of both claims are run and committed (P2) before F; the
  positive arms sit inside each control (the ten r95 targets keep their verdicts under both searches;
  20/20 arms kern
).

### A0.2 Round shape

One v1 wave, 12 seats (policy band 8–16): 3 executor, 3 reviewer, 1 critic, 2 mutation-tester,
1 sentinel, 1 connector, 1 scout, 1 scribe (no labrat seat; the validator rejects labrat as a swarm role).
Attack seats (reviewer, critic, mutation-tester): 6/12 = 50 %. The L1 holds the canonical planner seat (the
validator rejects `planner`); the bounded planning data-walk rides the connector seat. Residual calls: none
planned. Spec header seat-count line is exact (r96 spot-check §7.4): the writer computes the count from the
items array, never a hand-written number.

### A0.3 Wave-evidence durability (r96 spot-check §7.5)

The wave argues over whether `.ufo/waves/round-97/` (git-ignored in the lane) should be archived into the
committed tree. Decision: commit a byte-exact capture of the seat reports + receipt outputs into
`census/round-97/wave-evidence/` under a `MANIFEST.sha256` sibling, mirroring the r17 transcript-manifest
practice (`census/round-17/transcript-manifest.py` pattern), plus an index naming the live-checkout location
as the durable-evidence root. The live `.ufo/waves/round-97/` stays the working evidence; the capture makes
it survive a cold restart. This decision is recorded in the wave spec context so the closure reads it.

## Wave findings and amendments (after the seat reports; wave w1, seats TBD)

Amendments below never widen a frozen sentence. Each falsifying artifact is named with its seat and the line
it falsifies; the ledger `.ufo/waves/round-97/claim-falsification.tsv` points at these amendment ids.
