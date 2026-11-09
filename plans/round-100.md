# souji round 100 — plan (L1 SoujiR100)

Lane base `a662bb0d7e033cc5ceccd70b52eb234404300845` (r99 tip; r99 spot-check
`corpus/lessons/round-99-verifier-spotcheck.md`: C1 improved, C2 harmed,
routed defect C2 escapee successor → r100 ONE).

## A0.1 Frozen predicates (written before any scoring; L1 owns the freeze)

- **C1 (operability 8, Q177): session-owned escapee reap.** The successor
  counter `census/round-100/c2-setup-arms.py` records, at arm spawn, the spawn
  pid's session id (`stat` field 6, S075/S078-class) plus the spawn pid's own
  starttime. On the T1 arm, a process is owned iff (a) it is the spawn pid
  starttime-verified OR (b) its session id equals the spawn pid's recorded
  session id AND it carries the fixture token byte-exactly AND it is NOT a
  foreign decoy (its own driver/session differs). The r97 argv-only kill is
  NOT restored: a foreign decoy with the token but a different session id is
  never killed. Frozen target triple, measured on committed receipts:
  (1) r100 successor: `ESCAPEE-ALIVE alive=0` while the arm's decoy
  (`census/round-100/c2-decoy-test.py`) reports `verdict=spared` 83/83;
  (2) r99 counter (do-nothing): `alive=1` (committed
  `census/round-99/records/c2-escapee-r99.txt`);
  (3) CM8 argv-only mutant: decoy `verdict=killed`. The `m_noppid` mutant
  (session key removed) must FAIL predicate (1) (`alive>=1`).
  Counting command: the frozen `census/round-100/c2-decoy-test.py` SUCCESSOR
  invocation (one command that runs the decoy test and the T1 escapee check
  over a scratch work dir and prints `DECOY-SUMMARY` + `ESCAPEE-ALIVE` lines).
  Do-nothing control is r99's counter on the same probe (alive=1) and r97's
  counter on the decoy (killed). A rewound branch-(c) rule, run on the same
  probe, must also kill the decoy (Q175: the predicate must punish a
  too-wide rule), otherwise predicate (1) is vacuous and the claim is
  withdrawn to an honest stop.
- **C2 (calibration 7, correction-class): stale source attribution repair.**
  Repaired by an appended correction block (append-only; no in-place
  rewrite) in `corpus/knowledge/deadline-owned-reaping.md` that cites S332
  for the field-4 ppid wording, and add `corpus/knowledge/deadline-owned-reaping.md`
  to S075's `used-by` cell (append-only allowed cell; the field-22
  starttime sentence it grounds is accurate). S332 already exists as a
  SOURCES row (line 313); no new row is opened. ROW AXIS CLAIM:
  calibration, because the claim moves is self-assessment honesty
  (authority files match observed state), not registry coverage.
  Frozen predicate: the bidirectional check — `grep -c 'S332'`
  `corpus/knowledge/deadline-owned-reaping.md` prints >= 1 (entry cites its
  row) AND the S075 row's `used-by` cell names the entry (row names the
  entry) — both legs measured on committed bytes at the landing tip. Before
  at base: leg 1 prints 0, leg 2 prints 0. Do-nothing control: an entry
  citing a row the row does not name prints the same two zeros, so the
  predicate can fail (the instrument is the pair of greps, not the claim).

## A0.2 Round shape

One v1 wave, 14 seats (band 8–16): 3 executor, 2 reviewer, 1 critic,
2 mutation-tester, 1 sentinel, 1 connector, 1 scout, 1 scribe, 1 revenger,
1 labrat. Attack seats (reviewer, critic, mutation-tester, labrat,
sentinel): 7/14 = 50% (≥25%). Connector: 1 (≤2). The L1 holds the canonical
planner seat; the planning data-walk rides the connector seat. Residual
calls: none. Role→model routing is `task.agentModelOverrides` (operator):
connector @m_antigravity, scout/scribe/sentinel @m_mim, the rest
@m_cru. Never pass `model`.

## A0.3 Sources

Re-open this round: S075 (proc_pid stat fields 5/6/22 — field 6 is the
candidate session key), S332 (kernel emission order; grounds C2's field-4
attribution correction), S368 (setsid new session/group; grounds the T1
escapee being a new-session process). The sourced claim is C1 (operability),
which rests on S075 + S368 opened this round. C2 is sourced too (S332).

## A0.4 Frontier step (inside the claim cap, §2b)

- Census before/after: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate
  --root /home/vgpnk/Projects/shokunin souji` at round start (294 rows, EXIT 0)
  and end (294 rows expected — C2 opens no new row, EXIT 0).
- One mistake mined into `corpus/lessons/round-100.md ## Mistakes` (the
  session-key candidate risk: field 6 is shared by every process in a
  session, so the session key alone may be too wide — the decoy leg must
  prove it is not).
- Assimilation: none this round (no `merge/souji/` theme taken). considerthese:
  the lane has no `considerthese/` dir.

## A0.5 Inviolable constraints (every seat prompt)

- Scratch root: `$HYAKU_SCRATCH=/fast/scratch/hyaku`, seat dir
  `/fast/scratch/hyaku/souji-r100/<seat-name>/`. Never rely on `/tmp` for
  anything ≥50 MB; pass `--work` under the seat dir. A seat deletes its
  scratch dir before yielding (`trap 'rm -rf -- "$S"' EXIT` in shell,
  `finally: shutil.rmtree` in Python); receipts copied first into the wave dir.
- L0 reap authority is OPEN (r97/r98 lineage): C1 is a counter-ownership
  repair, not a grant of new signalling authority; no kill runs on any
  process the counter did not plant in this round's fixture.
- Every `Report:` trailer path is relative to
  `/home/vgpnk/Projects/shokunin/souji-shokunin` — write it at
  `/home/vgpnk/Projects/shokunin/souji-shokunin/<that path>`.
- Git discipline: any fixture repo is `git -C "$D" init` with
  `git -C "$D" rev-parse --show-toplevel` verified before any commit.
  Never run a mutating git/jj command in the lane or fleet repo directly.
- Seats NEVER commit, push, or run a mutating git/jj command anywhere.
  Only the L1 commits, through `jj-lane.sh` (lane) / `fleet-commit.sh` (report).
- Tooling authorization: installs via official channels only (no pacman per
  the host pause); record tool/version/channel/reason in the wave report.
