
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
