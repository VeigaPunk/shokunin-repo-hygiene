# souji round 98 — plan (L1 SoujiR98)

Lane base `ff254387005e35ff442555451374ff079dafc2db` (r97 closed by non-author spot-check, `corpus/lessons/round-97-verifier-spotcheck.md`:
C1 harmed-trade, C2 not admitted; MANIFEST pause state not in this lane's files — fresh-start history read out of prudence:
round-97 spot-check §3 and §6 read). Round intent per `SCORECARD.md ### Planned (r98)` and spot-check §6.1–6.2.

## A0.0 Claim choice (planner seat, L1)

- Lowest owned non-retired axis: calibration 7 → C1 (the spot-check's routed successor, §6.1).
- C2 (operability 8) is the second claim: the spot-check §6.2 successor (ownership repair). Two claims, two distinct axes,
  causally separable (C1 touches only the crash hook and the shapes table; C2 touches only the arms counter and the
  decoy test).
- Operator L0 question (r97, reap authority) is OPEN. The lane routes around it: the successor C2 is a repair of the
  reap's ownership rule, not a grant of new authority; the round reports the L0 as open and does not treat it as answered.
  If the operator rules the reap must stay disabled, C2 lands as the disabled counter and its claim is re-scoped in r99.

## A0.1 Frozen predicates (written before any scoring; freeze F is the L1's commit after the wave lands)

- C1: `declared-shapes.py` over 17 shapes (r97's 14 + q1i, q1o, q1q) prints `SHAPES-SUMMARY shapes=17 mismatched=0`, with
  q1o and q1q at code 70 and every handled shape at 1. Do-nothing control: the r97 hook on the same 17 shapes prints
  `mismatched>=2`. No-harm: the 278-mutant population has 0 verdict changes between r97 and r98 search and byte-identical
  survivor sets. The expected code per shape is written in `census/round-98/declared-shapes.expected` before the search runs.
- C2: `c2-decoy-test.py` shows the foreign decoy ALIVE after the r98 counter exits (PASS), and KILLED under the r97
  counter (FAIL, the do-nothing control). `c2-setup-arms.py` with the r98 probe prints `ARMS-SUMMARY arms=20 conform=20`
  EXIT 0 with the decoy not killed. CM8 (ownership check removed) must fail the decoy predicate.

## A0.2 Round shape

One v1 wave, 12 seats (policy band 8–16): 3 executor, 2 reviewer, 1 critic, 2 mutation-tester, 1 sentinel, 1 connector,
1 scout, 1 scribe. Attack seats (reviewer, critic, mutation-tester): 5/12 = 42 % (≥25 %). Connector: 1 (≤2). The L1 holds
the canonical planner seat; the planning data-walk rides the connector seat (R98Connector §data-walk). Residual calls: none planned.

## A0.3 Sources

- S075 (proc_pid_stat(5): ppid field 4, starttime field 22) and S372 (sys.monitoring RERAISE/EXCEPTION_HANDLED) are
  re-opened live by R98ScoutSources this round; the verification result is recorded in the report.
  The sourced claim is C2 (ppid/starttime ownership) resting on S075, and C1's RERAISE cancel resting on S372.

## A0.1 freeze amendments (filed at L1 integration; predicates re-stated)

- q1i pinned `declared` (R98Reviewer1 F3, R98Critic K1, R98MutC1 F3): it is genuinely caught at <module>
  (plain 0), so Python semantics give declared; the r98 latch agrees (last stamp EH). The r97 prereg
  "stays errored" limit (i) is superseded by the A0.1 freeze, not silently reinterpreted.
- "every handled shape at 1" is corrected: the measured plain codes of the declared class are 3 (a1, a5,
  a5b, a4, a12, v1) and 0 (t1, t4, q1i); the runner's rule is `plain == hooked`, code-agnostic
  (R98Reviewer2 §0, R98Scribe §1.4).
- C2's conform now binds the T1 survivors byte (R98Connector C-3): `ARMS-SUMMARY arms=20 conform=20`
  with survivors=0 on T1; a counter that reaps nothing cannot pass on conform alone.
- CM8 naming split (R98Connector C-1): r97's CM8 (conform and->or, scoring) is carried forward as the
  r97 falsification chain; r98's CM8 is the ownership mutant (argv-only reap) against the decoy
  predicate. Neither alone retires the other.
- C2 instruments repaired in-round under the frozen A0.1 (see lesson Mistakes M6-M8): the decoy test now
  plants a plain sleeper carrying the counter's OWN T1 reap token and polls the sleeper's pid
  continuously; the T1 survivors count uses the descendant relation instead of a same-starttime
  comparison; the CM8 mutant is a real argv reap.
