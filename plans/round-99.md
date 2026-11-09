# souji round 99 — plan (L1 SoujiR99)

Lane base `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b` (r98 spot-check `corpus/lessons/round-98-verifier-spotcheck.md`:
C1 numbers re-derive but predicate movable; C2 evidence-verified measured-not-admitted, branch-(c) wording falsifies the sentence).
Round intent per `SCORECARD.md ### Planned (r99)` + spot-check §routed 1–4.

## A0.0 Claim choice (planner seat, L1)

- Lowest owned non-retired axis: calibration 7 (coverage 8, operability 8, saturation line 8, window 3) → C1.
- C2 (operability 8): spot-check routed 2/3/4. Two claims, two distinct axes, causally separable (C1 touches only the shapes runner + a L1-owned freeze file; C2 touches only the arms counter `_reap_owned` wording + the redundant branch `(c)`).
- L0 question (r97, reap authority) is OPEN. The round routes around it: C2 is a wording-to-code repair, not a grant of new authority; the round reports the L0 as open and does not treat it as answered.
- Sources re-opened this round: S372 (sys.monitoring RERAISE, grounds C1's
  latch), S075 (proc_stat fields 5/6/22; kernel-side field 4 via S332; grounds C2's ppid-chain ownership),
  S368 (setsid(2) new process group; grounds C2's escape).
  R99ScoutSources re-opens each live; the lesson Gate records URL · access date · ≤25-word located quote · location.

## A0.1 Frozen predicates (written before any scoring; L1 owns the freeze file)

- C1 (calibration 7, Q173): the r98 hard-coded `SHAPES` tuple is replaced by
  `census/round-99/shapes.tsv` (17 rows, `name\tkind\tplain\tcomment`, L1-authored, committed at freeze
  before any scoring). `declared-shapes.py --freeze shapes.tsv` reads the freeze file; `mismatched` is computed
  ONLY from its `kind` column, never from a claimant-written label. Frozen target: `shapes=17 mismatched=0` EXIT 0
  with the r98 hook (via `c1-r98-search.py`).
  Do-nothing controls (all on the SAME freeze file):
  (a) r95 hook `mismatched>=4` (r95 receipt);
  (b) r97 hook `mismatched>=2` (q1o/q1q wrongly declared; r97 measured on 17 shapes).
  Relabelling attack (M6 receipt): editing the freeze file's `kind` column moves the count with the hook untouched —
  the round commits ONE relabelled freeze file whose count moves, and the r99 runner must flag the relabelled file
  via a freeze-file SHA pinned in the L1 tranche (8, same commit as the freeze file). The attack reaching 0 while
  the file hash is NOT the pinned one proves the binding. No-harm: 278-mutant population byte-identical survivors.
- C2 (operability 8): `_reap_owned` branch `(c)` is REMOVED as a kill authorisation: the counter-kill requires
  (a) spawn-pid/starttime or (b) a spawn-pid descendant (ppid chain). A counter-descendant carrier with the token
  and no spawn-pid chain is NEVER killed: the committed cross-arm probe must report it `verdict=spared` with the
  probe-side verdict change (pre-r99: `verdict=killed` via `cross_arm_probe.py` reaching a P1-arm carrier by T1's reap,
  R98Sentinel FINDING 4). The T1 escapee remains owned via the subreaper reparent (ppid == counter == spawn pid's
  parent chain recorded at spawn, so it is a spawn-pid-chain member by the recorded parent field, not via the
  `os.getpid()` descendant branch). Reap logic is monotone-restricting (kills ⊆ r98 kills); r98 decoy predicate still
  `spared`, r97 still `killed`. The C2 sentence is re-stated to name the narrower rule exactly (a)+(b) only.

## A0.2 Round shape

One v1 wave, 12 seats (band 8–16): 3 executor, 2 reviewer, 1 critic, 2 mutation-tester, 1 sentinel, 1 connector,
1 scout, 1 scribe. Attack seats (reviewer, critic, mutation-tester): 5/12 = 42 % (≥25 %). Connector: 1 (≤2).
The L1 holds the canonical planner seat; the planning data-walk rides the connector seat. Residual calls: none.

## A0.3 Sources

- S372 (RERAISE, object-keyed latch), S075 (fields 5/6/22; S332 kernel-side field 4), S368 (setsid new group
  escapee) — re-opened live by R99ScoutSources; byte-identical captures verified.
- The sourced claim is C1 (S372), one claim rests on a SOURCES row opened this round.

## A0.4 Frontier step (inside the claim cap, §2b)

- Census before/after: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` at round start and end; both EXIT 0 expected; rows 294→294 (re-verifications only, no new row).
- One mistake mined into `corpus/lessons/round-99.md ## Mistakes` (M6 successor class; captures the M6 movability that r98's own gate missed).
- Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## A99.1 pin amendment (filed after the wave scored; disclosed, does not change any measured number)

- Reviewer1 (R99Reviewer1) showed the freeze-file runner printed `mismatched=0` for a file with a duplicate row
  (`shapes=18`) or a missing row (`shapes=16`), and printed the freeze sha256 without checking it. Scribe M9 (R99Scribe)
  recorded the same population/hash binding gap; Critic (R99Critic, C1 sentence 2) recorded the binding as narrowed.
- Change: `census/round-99/declared-shapes.py` now REQUIRES `--expect-sha256` and refuses (rc 2, `SHAPES-FATAL`) on a
  hash mismatch or a row count other than 17 with distinct names. Pinned value: `8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14`
  (census/round-99/shapes.tsv). The C1 measurement receipt is `census/round-99/records/c1-r99.txt` (M1–M3 and controls).
- Honest status: this is a strengthening amendment decided after seats scored. The pre-amendment measurements (seat
  ExecC1: relabel → `mismatched=3`; control ExecC1b: r95/r97 → `mismatched=3`) are unchanged by it and are cited as such.
  The non-author closure decides whether the amendment is admissible as the claim's rule.

## A99.2 C2 narrowing and harm record (recorded after measurement; no predicate changed)

- The frozen C2 predicate (decoy spared under r99 = PASS; decoy killed under r97 = do-nothing FAIL; CM8 killed) is
  MET on committed receipts: `census/round-99/records/c2-decoy-r99.txt` (`DECOY-SUMMARY verdict=spared`, 83/83 alive),
  `c2-decoy-r97.txt` (`verdict=killed`, dead 60), `c2-decoy-cm8.txt` (`verdict=killed`, dead 82).
- The same frozen claim also says the reap is an operability improvement. It is not: the r99 spawn-chain rule no longer
  reaps the T1 setsid escapee. Measured by a direct live-process count after each counter exits
  (`census/round-99/records/c2-counter-*.txt`, and the escapee check listed there): r99 `alive=1`, r98 `alive=0`,
  r97 `alive=0`. The escapee's ppid is the counter (PR_SET_CHILD_SUBREAPER), not the spawn pid, so the frozen
  `survivors=0` is vacuous (`planted-killed 0`). Sentinel FINDING 1 and Reviewer2 F2 reach the same result on their own probes.
- Verdict: **C2 harmed (trade); not admitted.** The predicate verifies the decoy and CM8 legs; the reap leg loses the
  escapee and no frozen predicate measured that leg (MutC2 `m_noppid` survives every predicate). Under the no-harm rule
  this is not an improvement. The C2 wording is narrowed to what the instrument enforces: the arms counter spares
  foreign carriers and does NOT reap the T1 escapee; no reap claim is made for the escapee in this round.
- Routed to r100 (see SCORECARD `### Planned (r100)`): an escapee ownership key that is not the ppid chain (candidate:
  the arm's recorded session id, verified by starttime), a positive escapee-reap predicate, and the L0 question to the operator.
