# AttackE32 — adversarial falsification of W1's E32 finding (seat SwarmCritic25, souji r34 w2)

## Status

- W1's core E32 claim (MISMATCH in the C1 do-nothing control) is **REPRODUCED and real** — three
  independent readings (one committed, two W1) all verdict MISMATCH, and the mismatch is
  deterministic, not load-dependent at the verdict level.
- W1 finding 6 (E32 load-sensitivity, Q77) is **CONFIRMED** with the mechanism identified
  (T12's unsandboxed base run of `tools/souji-census.sh --selftest` flips with host load; T18
  fails always). W1's implied remedy (restatement quoting the bound line beside its recorded
  load) is **moot**: no honest restatement of E32 can exist under the frozen rules.
- W1 finding 7 (instrument-detail inconsistency) is **FALSIFIED as stated**: it misquotes the
  committed record. The committed record is internally consistent. The genuine label anomaly
  is in a *different* W1 receipt (`deliver-q76-honoring.txt:69`), which W1 missed; verdict
  impact is none.
- Honest route: **NONE found**. Confirmed no rule-conforming route under the frozen cause,
  argv, exit, statement, and Q76 rules. E32 cannot honestly AGREE at any C1 landing reachable
  under C1's write scope, so the frozen target `agree=60 mismatches=0` is unreachable via
  this item independent of the other 59.

## Evidence

1. Frozen item bytes — `census/round-34/c1-items.tsv:76`, byte-identical at the re-pin list
   revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` and the attempt-1 list revision
   `2b591924f607940febbb99f922cc9bb090508eb6` (verified with `git show … | sed -n 76p | cat -A`):
   `E32  SCORECARD.md:478  0  SUMMARY items=27 pass=26 fail=1  census/round-32/c2-counter.py  {REV}
   python3 -B census/round-32/c2-counter.py --root . --rev {REV} --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c`
2. Source row — `SCORECARD.md:478` at base `9c76c7222a8abff027af42e37f0d160d52526bba`: the
   round-32 C2 row "C2 lane-tool scratch discipline (27 items over 22 files)"; its own text
   records the landing `pass=26 fail=1` (T18) as "not reproduced" — two a2w1 runs and the L1
   read `pass=25 fail=2` (T12, T18), "**missed** (`fail=0`)", and states "T12's base flips
   under load". The load flip W1 flagged is already documented in the source row.
3. Counter exit semantics — `census/round-32/c2-counter.py:24-26` (docstring: "Exit 0 iff
   fail=0; 1 otherwise") and `:186` `return 0 if failed == 0 else 1`; SUMMARY printed from the
   same counters (`:188-190`). Therefore a last line of `… fail=1` implies rc=1, and rc=0
   implies a `fail=0` line — the frozen (exit=0, statement `… fail=1`) pair cannot both be
   satisfied by any run of this counter at any revision, at any load.
4. Three E32 readings, byte-verified:
   - committed `census/round-34/records/controls-c1-do-nothing.txt:60`: `rc=1 expect_exit=0
     predicate holds last=SUMMARY items=27 pass=26 fail=1 … load=10.15` — consistent label;
   - W1 `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:65`: `rc=1 expect_exit=0
     predicate fails last=SUMMARY items=27 pass=25 fail=2 … load=32.35` — consistent label;
   - W1 `.ufo/waves/round-34/w1/deliver-q76-honoring.txt:69`: `rc=1 expect_exit=0 predicate
     holds last=SUMMARY items=27 pass=25 fail=2 … load=36.63` — **inconsistent label** (see
     Findings F3).
5. Executed replay (this seat, in-process import; no clone, no fixture run):
   ```
   python3 -B - <<'EOF'   # importlib load of census/round-34/c1-counter.py (main() guarded)
   frozen_pred("SUMMARY items=27 pass=26 fail=1", ["SUMMARY items=27 pass=26 fail=1"], ".", "9c76c72…")
     -> (True, 'predicate holds')
   frozen_pred("SUMMARY items=27 pass=26 fail=1", ["SUMMARY items=27 pass=25 fail=2"], ".", "9c76c72…")
     -> (False, 'predicate fails')
   ```
   The q76 receipt's "predicate holds" against `pass=25 fail=2` is impossible under the
   frozen counter with the frozen predicate (identical in both list revisions, item 1).
6. Restatement gates — `census/round-34/c1-counter.py:243-323` (`judge`): same-argv
   restatement requires `held is True` at the cause's parent for the frozen original
   (`:298-302`); argv-correction requires the cause to have written the row's line and the
   row's own argv to fail at the cause (`:303-312`), plus a corrected argv naming a basename
   from `item["files"]` (`:287-289`); restated statement must equal the collapsed last
   digit-bearing line exactly (`:309-313`); restated exit may be `*` (`:307`).
7. Q76 — zero prior correction rows bind cell `SCORECARD.md:478`: `grep -cE
   "SCORECARD\.md:478([^0-9]|$)"` = 0 in both `SCORECARD.md` and `SKILL.md` at base
   `9c76c72…` (this seat re-ran the counts directly; both 0).
8. Cause candidate for an argv-correction — `9da5e9a559f76ecbd275a9685226883d334dc8f9`
   ("round-32: attempt-2 integration …"), the sole `-S "C2 lane-tool scratch discipline"` hit
   on SCORECARD.md; it **is** an ancestor of list-rev `2b0171e2…` (merge-base check passed)
   and its parent `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` is a full 40-hex — so the
   mechanical gates for an argv-correction restatement are satisfiable, but no honest
   corrected argv exists (Findings F2).
9. Frozen rules — `census/round-34/preregistration.txt:40-58`: statement binds to the run's
   last digit-bearing line; AGREE iff exit equals and predicate holds; restatement shape
   (Q75/Q76) with executed-cause gates; Q77 flock serialization with load recorded beside
   each ITEM line (already automatic in the counter); C1 write scope `:62-67` — "No tools/ or
   tests/ edit other than new r34 fixtures", i.e. the T12 load flip cannot be repaired under
   C1's scope.
10. T12/T18 legs — `census/round-32/c2-items.tsv` at `3ec84fc…`: `T12 = bash
    tools/souji-census.sh --selftest`, `T18 = python3 -B tests/fixtures/r20-input-binding.py
    --baseline 12516f7d…`. Data: fail=1 (T18 only) at load≈10; fail=2 (T12+T18) at
    load≈32-36 — consistent with the SCORECARD's "T12's base flips under load".

## Findings

- **F1 — The mismatch is real, deterministic, and stronger than W1 stated.** W1 framed E32
  as a value-drift/load case. In fact the frozen (exit=0, statement `SUMMARY items=27
  pass=26 fail=1`) pair is a logical contradiction under the instrument's own exit rule
  (Evidence 3): `fail=1 ⇒ rc=1`, and `rc=0 ⇒ fail=0 ⇒ predicate fails`. The original item
  can never AGREE at any revision or load. All three observed readings verdict MISMATCH, and
  even the low-load reading where the predicate *holds* (`pass=26 fail=1`, committed record)
  mismatches on exit. Not a measurement artifact.
- **F2 — No honest rule-conforming route exists (route search, all gates checked).**
  (a) *Same-value restatement* — categorically blocked by the value-drift BAD-CAUSE gate
  (`judge` requires the frozen original to *hold* at the cause's parent, `held is True`);
  the original never holds anywhere (F1), so no cause can certify. (b) *Argv-correction* —
  the row's argv faithfully runs the frozen r32 counter and is not broken; the only
  mechanically-eligible cause (Evidence 8) has no associated honest correction, and any
  tweak (--only, different --base/--list-rev, added --scratch) changes the measurement basis
  rather than repairing the row — dishonest under Q75's "runs the row's own script" and the
  junk-control anti-pattern. (c) *Load flip* — even if a restatement were certifiable, the
  bound line flips between `pass=26 fail=1` (load≈10) and `pass=25 fail=2` (load≈32-36), so
  no single quoted statement agrees in both regimes; Q77's load annotation records the
  regime but cannot stabilize the binding. (d) *Scope* — C1's write scope forbids `tools/`
  edits, so the T12 flip cannot be honestly removed either. Conclusion: E32 is permanently
  MISMATCH under honest play; the frozen `agree=60` target is unreachable via this item.
  W1's "blockage" conclusion is valid but was reached with a weaker argument than available.
- **F3 — W1 finding 7 is falsified; the real label anomaly is elsewhere and unflagged by W1.**
  SwarmExecutor13 (`w1/SwarmExecutor13.md`, finding 7) claims the committed record reads
  "`predicate fails last=SUMMARY items=27 pass=26 fail=1`". Byte inspection
  (Evidence 4, first bullet) shows the committed record reads "`predicate **holds** last=
  SUMMARY items=27 pass=26 fail=1`", which is exactly what the frozen predicate replay
  returns for that line — the committed record is **internally consistent**; the defect
  finding 7 alleges does not exist. The genuine instrument-record inconsistency in W1 is
  `deliver-q76-honoring.txt:69`: `predicate holds` bound to `last=SUMMARY items=27 pass=25
  fail=2` — my executed replay (Evidence 5) proves that label is impossible for the frozen
  predicate under the frozen counter with inputs byte-identical to the do-nothing run. The
  q76 receipt's E32 line is therefore not a faithful record of a frozen-counter run
  (transcription error or doctored receipt). Verdict impact: none — rc=1 dominates and
  MISMATCH is correct in all three readings. Nature: W1 report-fidelity defect, not a
  counter or frozen-item defect. (For calibration I checked the sibling SCORECARD rows
  E23a/E24/E27/E29: their frozen statements are the *original* `fail=0`-family values, so
  their "predicate fails" labels against drifted lines are correct — E32-in-q76 is the lone
  impossible label.)
- **F4 — W1 finding 6 confirmed, with corrected emphasis.** The load sensitivity is real
  and mechanistically explained (T12 unsandboxed base run flips; Evidence 10). But "any E32
  restatement needs its recorded load beside it" is moot: Q77 makes load recording automatic
  in the counter, and per F2 no honest restatement exists at all. The operative fact for the
  round is F1+F2: E32's frozen (exit, statement) pair is self-contradictory and unrepairable
  within C1's scope.

## Attack log

All commands read-only against the lane clone at `/home/vgpnk/Projects/shokunin/souji-shokunin`;
no lane file modified, no commit, no push, no fixture executed, no scratch directory created
(0 MB of the 50 MB ceiling used). `git rev-parse --show-toplevel` was not needed — no git
mutation was performed anywhere.

1. `grep -n "E32" census/round-34/c1-items.tsv` → frozen row at line 76.
2. `head -10 census/round-34/c1-items.tsv` → column semantics and Q76/Q77 hardening header.
3. `git show 9c76c72…:SCORECARD.md | sed -n '470,485p'` → source row text (C2 r32 row,
   load-flip documentation).
4. Read of `census/round-32/c2-counter.py` (191 lines) → exit rule `:186`, SUMMARY `:188-190`,
   docstring `:24-26`; item legs T12/T18 from `git show 3ec84fc…:census/round-32/c2-items.tsv`.
5. Read of `census/round-34/c1-counter.py:109-173,193-323,340-401` → predicate binding,
   verdict, restatement gates, Q77 load recording, `__main__` guard (confirms the import
   probe executed no main).
6. Replay probe (executed, this seat — Evidence 5): importlib load of the frozen
   `c1-counter.py`, `frozen_pred` against both observed last lines; results as quoted.
7. `git show 2b0171e2…:c1-items.tsv | sed -n 76p | cat -A` and same for `2b591924…` →
   byte-identical E32 rows in both list revisions.
8. `sed -n 60p census/round-34/records/controls-c1-do-nothing.txt | cat -A`; `grep -n E32
   .ufo/waves/round-34/w1/deliver-q76-honoring.txt | cat -A`; same for
   `deliver-c1-do-nothing-check.txt` → byte-level verification of all three E32 lines
   (Evidence 4).
9. `git show 9c76c72…:SCORECARD.md | grep -cE "SCORECARD\.md:478([^0-9]|$)"` = 0; same for
   `SKILL.md` = 0 → Q76 clear (no prior correction binding cell 478).
10. `git log --format=… -S "C2 lane-tool scratch discipline" -- SCORECARD.md` → author
    `9da5e9a5…`; `git merge-base --is-ancestor 9da5e9a5… 2b0171e2…` → pass; parent
    `4e56c48b…` full-40 → mechanical eligibility of the argv-correction cause (Evidence 8).
11. `grep -E "^E23a|^E24|^E27|^E29" census/round-34/c1-items.tsv` → sibling predicates
    confirm the q76 E32 label is the lone impossible one (F3).
12. Read of `census/round-34/preregistration.txt:36-73` → frozen C1 rules, restatement shape,
    scope limits (Evidence 9).

No counter run was executed (the full c2-counter run is a 30+ min, host-load-dependent
fixture; the committed record plus two W1 reruns already bound both load regimes, and the
decisive gates were proven from the frozen source plus an in-process predicate replay).

## Deliveries

- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackE32.md`
- Scoped seat findings: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/SwarmCritic25.md`
- No other files touched; no scratch artifacts; no frozen artifact modified.
