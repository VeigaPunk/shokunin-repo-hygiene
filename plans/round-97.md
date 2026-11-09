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

### A7 — C2 CONTROL surivor-expectation correction: the r96-probe `survivors=1` number is wrong (frozen number, corrected)

Artifact: census/round-97/controls/c2-control-r96-probe.txt line `ARM T1 exit=2 want=2 line=yes conform=yes
survivors=0` under the r97 counter with the r96 probe as `--probe` (full receipt: conform=20, EXIT 0, no
`--survivors` detail). The prereg CONTROL paragraph's sentence "Against the r96 probe: conform=20 with
`survivors=1` on T1" claims an observed 1; the receipt says 0, twice (the detached run's T1.out
`--survivors 0 planted-killed 1` and the final receipt). The counter's snapshot reaper counts only the planted
identity, and r96's probe kills its own fixture grandchild-side via the timeout group kill once it stops
waiting on pipe EOF: the survivor is probe-owned, not counter-owned, so 0 is the correct number under the
snapshot counter. The C2 measured quantity (conform=20 with survivors=0) is therefore NOT discriminated by
the r96-probe control; the r95 probe (T1 hung, conform=19, EXIT 1, census/round-97/controls/
c2-control-r95-probe.txt) is the discriminating control. Amendment 59 (i): the claim does NOT depend on the
r96 control's survivor number; the counting predicate is the same (20/20 + survivors=0), the control that
shows the move is the r95 per-arm hang, and the survivor count is disclosed as a probe-owned count. No number
in the predicate or summary changes; only the control sentence is corrected. The gauge the wave re-derives is
the r95 hang; GD's failure (survivor) is unaffected.

### A8 — GD forgery survives as label-only (same shape as A7): no forgery-refusal gain, reported honestly

Artifact: census/round-97/controls/c2-forgery-controls.txt GD line: `arms_exit=0 summary=arms=20,conform=20
refused=no` (survivors=0 by the counter's snapshot count; planted-killed absent for this probe because the
probe's timeout group kill reaps its planted grandchild before the counter's reap pass). GD's ONE-edit family
(the probe claims setup refusal without reaping by identity) does not bind the counterexample it named: the
counter's snapshot counts a survivor only when it is caller-visible at reap time, and the GD probe already
removed it via the probe session kill. Per Amendment 59 the honest-offering is option (ii): C2's counted
quantity — "the counter reaps the T1 grandchild by identity (the fixture's per-arm absolute path)" — is NOT
proved on the planted-vs-recycled distinction by this control set, and the forgery-refusal number is
GA/GB/GC-refused 3/3 plus GD label-only (survivors=0 reported with a planted-killed count of 0/1 in the arm
.out, which the counter does not bind). The claim's falsifiable numbered predicate (conform=20 with
survivors=0, exit 0) stands; the capability sentence is narrowed. GC `conform=0` (every arm exit=1, line=no,
survivors variable) is refused by a different mechanism than the prereg's "no fixture timeout" wording — the
prereg's GC mechanism (S12/T1 exit 2 hung arms) is superseded by this measured one: removing the output cap
makes the probe's --max-output refusal (C2-FORGERY-FATAL, exit 2) unreachable and the probe verdict exits 1
on every arm (GA-adjacent behaviour).

## Wave findings and amendments (wave w1, 13 seats, WAVE-DONE 2026-11-09; results `.ufo/waves/round-97/w1-results.json`)

Amendments are append-only. A7 and A8 above stand except where A7-correction says otherwise. None of these
amendments widens a frozen sentence; each narrows or withdraws one. Claim verdicts are in SCORECARD.md `### Round 97`.

### A7-correction — the survivor explanation in A7 was wrong; the control provenance is also defective

A7 said the r96-probe control's `survivors=0` was "probe-owned". That is false. The reap is the counter's (the
r96 counter, committed at 2bbbab6d, left `survivors=1`; the r97 counter reaps, so `survivors=0` with the r96 probe).
Separately, census/round-97/controls/c2-control-r96-probe.txt was produced by a counter whose sha256 is
`b460c6f4…`, not the frozen `da30593c…` (the snapshot edit landed after that control ran). The P2 r96-control
receipt is therefore not a receipt of the frozen bytes (ExecC2 H-2). The prereg sentence "conform=20 with
`survivors=1` on T1" is falsified as a number against the r96 probe under the frozen counter (observed 0).
Narrowed: the before-side survivor number for the reap claim is the r96-committed-counter receipt (survivors=1, census/
round-96 records, A4); the r97 counter's measured effect is survivors 1 → 0 on the r96 probe (scribe reap-removed mutant:
`survivors=1`; committed counter: `survivors=0`). The control receipt is re-labelled, not replaced.

### A9 — C1 "closes the trade": FALSIFIED by q1q (regression) and q1o (unfixed). C1 harmed.

Artifacts: `.ufo/waves/round-97/w1/R97ReviewerC1.md` (Q1 q1o, q1q, with receipts `receipts/q1o.py`, `receipts/q1q.py`);
`.ufo/waves/round-97/w1/R97Critic.md` §1.
- q1q: `try: helper() except SystemExit: pass` at module level (object 1, pending), then a direct terminating
  `helper()` (object 2). The atexit flush pops object 1's pending record and clears the live foreign mark belonging to
  object 2 (same function name). Plain rc 1, r97 hooked rc 1 with no marker (want 70). The r96 hook scores 70.
  This is a regression from r96 on a shape class the r96 trade did not touch.
- q1o: `try: helper() except SystemExit as e: saved = e` then `raise saved` outside the `except`. The bare raise
  fires RAISE but not RERAISE, so the pending candidate is not cancelled and the flush clears the mark. Plain 1, hooked 1.
Verdict: C1 is HARMED (trade): the 14-shape table moves mismatched 2 → 0, but q1q moves 70 → 1 (r96 → r97). Under the
admission rule a trade is not an improvement. C1 is not admitted. The calibration score stays 7 (no reproducible 0–10
mapping).
Narrowed sentence (the claim as it now stands): "on the fourteen declared-exit shapes, the r97 search keeps t1/t4
declared and x1/x2 errored (mismatched=0); the latch does NOT close the EH-clear trade for a caught-then-terminating
sequence (q1q) or a saved-then-bare-raise (q1o)."
Routed to r98: a successor latch keyed on the exception object's own state (not a global pending flag), plus q1o/q1q/q1i in
the shape table (q1i: a finally-unwind that a later module-level except catches stays errored — disclosed in the prereg).

### A10 — C1 limit (i): FALSIFIED as written (a4 is in the table). Also a predicate-strength finding.

Artifacts: `.ufo/waves/round-97/w1/R97ReviewerShapes.md` §3 (limit i); `R97Critic.md` §1.
- Limit (i) says "a SystemExit caught at a non-module frame is a shape the table does not exercise (a4 is the
  counterpart)". a4-caught-then-return.py raises and catches inside `main()` and is in the table (`plain=3 hooked=3`).
  Narrowed: the table has a4; the uncovered shapes are q1i, q1o, q1q and the no-free-tool-id fallback leg (O1 in
  R97ReviewerShapes: the fallback drops the SystemExit leg, plain 1).
- Critic: the counted quantity is rc-70-ness on 14 fixed files plus the check line. A basename-keyed hook prints the
  same SHAPES-SUMMARY (not built). The predicate does not measure the latch. Conceded as predicate strength; C1 is not
  claimed as measuring the latch's mechanism.

### A11 — C1 mechanism clause "reorders ... to write before the traceback print": FALSIFIED as a mechanism (effect holds)

Artifacts: `.ufo/waves/round-97/w1/R97ScoutSources.md` §5 (DEFECT 3); `R97Scribe.md` F-6, F-7.
The r97 hook does not reorder: it removes `sys.__excepthook__` and `threading.__excepthook__` from the excepthook and
thread channels, and `_souji_crash` exits. Measured: r96 stderr carries a Traceback, r97 carries none on those channels.
The effect the claim names (a blocking print cannot hold the exit hostage) holds. The diagnostic loss is undisclosed in
the prereg and in crash-channels-beyond-excepthook.md (r97 section); a correction is appended there. Routed to r98: either
restore a traceback print after the marker write inside `_souji_crash` before `os._exit`, or state the removal.

### A12 — C2 "signals only processes it planted": FALSIFIED (HIGH). C2 not admitted.

Artifact: `.ufo/waves/round-97/w1/R97Sentinel.md` (FALSIFIES-WORDING; Finding 1; receipts
`repro_foreign_pid_kill.py/.out`, `continuous_decoy_42_planted.out`, `continuous_decoy_T1.out`).
The T1 reap snapshots token-carrying pids at arm start and SIGKILLs every own-uid argv carrier not in that snapshot at arm
end. A foreign process that acquires the arm's absolute fixture path during the arm is killed. Measured: one foreign decoy
killed (zombie, not reaped), 30 of 42 decoys killed in a continuous run (counter `planted-killed 31`). The printed
`survivors=0` hides it, because the foreign kill is not counted as a survivor.
Verdict: C2 is not admitted. The reap is a refusal-boundary violation (PROVINCE: no signalling of inherited or unrelated
processes; QUALITY Q32/Q33). The frozen counter is NOT edited after the freeze (a fix would change the claim's rule after
data). The lane's `census/round-97/c2-setup-arms.py` keeps the reap and carries an L0 question for the operator. Routed to
r98: ownership by recorded spawn pid and its ppid chain; no argv-only kill.

### A13 — C2 "recording a signal exit (-15) distinctly (A8)": FALSIFIED. A8 withdrawn.

Artifact: `.ufo/waves/round-97/w1/R97Scribe.md` F-2 (receipt `receipts/signal-exit-r96-vs-r97.txt`: `ARM T1 exit=-15 …`
on both counters; the rc block is byte-identical; `exit=signal` exists only in the counter docstring). The preregistration
sentence describing r96 as the defect ("printed inside the same `exit=` field with no mark") applies equally to r97.
Narrowed: a signal exit renders `exit=<negative rc>` (corpus/knowledge/deadline-owned-reaping.md states this correctly).

### A14 — C2 numbers: GD not refused, GC refused for a syntax reason, control 3/4 not 4/4

Artifacts: `.ufo/waves/round-97/w1/R97ExecC2.md` §5 (N-2, N-3, N-4, H-3); `R97Critic.md` §2.
- `C2-FORGERY-CTL-SUMMARY forgeries=4 refused=3`, EXIT 1 (prereg says 4/4, EXIT 0). GD is not refused: the counter
  reaps whatever the probe says. GC's forged probe is a SyntaxError (`unexpected indent`, line 129), so every arm exits 1
  for a syntax reason, not the no-timeout reason the prereg gives. Refused: GA, GB, GC. Not refused: GD.
- Critic basename cheat (3 lines in the probe, no cap, no selector wait, no reap by the probe) reaches
  `ARMS-SUMMARY arms=20 conform=20`, `survivors=0`, EXIT 0 (54.6 s). The sentence "No work does not reach survivors=0 with
  conform=20" is false: the cheat is work that reaches it. The predicate does not bind the probe's mechanism.
- r96-control survivor number: see A7-correction.

### A15 — C2 mutant discrimination (MutC2, neutral): 9 surviving mutants, one broken counter

Artifact: `.ufo/waves/round-97/w1/R97MutC2.md` (11 probe mutants PM1–PM11, 8 counter mutants CM1–CM8).
Killed: PM1, PM2, PM4, PM7, PM9, CM3–CM6. Surviving: PM3, PM5, PM6, PM8, PM10, PM11, CM1, CM7, CM8. CM8 (a counter
mutant) gives the r96 probe 20/20: a broken counter passes the predicate. Recorded as a discrimination gap for r98, not a
falsified sentence.

### A16 — corpus registry: S372 row shape and word count (corpus cell, fixed in-round)

Artifacts: `.ufo/waves/round-97/w1/R97ScoutSources.md` §3–4; `R97Scribe.md` M3. The S372 row landed at P1 with 7 of 11
cells, `used-by` glued into `teaches`, and an anchor word count of 14 (the quote has 13). `sources-census.sh validate`
exited 1 (`E01 S372 fields=7`). Repaired in the lane (the row's own landing commit; no other row touched): 11 cells, anchor
13 words, `status mined`, `opened 2026-11-09`, `recheck 365d`, `used-by` in its own cell. Census re-run: EXIT 0, no E01
(receipt in the report). This is a same-round correction of the round's own registry row, not an edit of an earlier row.

### A17 — ExecC1 docstring number and ExecCensus expectation (neutral, routed)

- `census/round-97/c1-survivor-search.py` docstring says the frozen r95 hook scores `mismatched=4`; measured 2 (P2
  controls/shapes-r95.txt). The sentence is in an instrument docstring, not in a prereg predicate. Routed to r98 as a
  docstring correction; no count depends on it.
- ExecCensus: "r96 errored=48" was a seat expectation, not a claim; measured 53 (both searches). No claim sentence
  depends on it. The no-harm result stands: over 278 generated mutants, 0 verdict changes and survivor sets byte-identical.
