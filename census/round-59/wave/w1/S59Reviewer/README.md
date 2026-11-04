Receipt index for S59Reviewer (probe outputs are raw; authoritative findings are in ../S59Reviewer.md).

- probe-counter-shadow.json — authoritative shadowing/forgery probes Q1–Q8. Q1: r58 `evidence`
  row + r59 `gate` row => rc0/mismatches=0 with the flagged row untouched. Q4: same r59 row inside
  a `~~~` fence => rc0. Q5/Q6: 11 cells / duplicate r58 => rc2. Q8: leading space => fallback, rc1.
- probe-frozen-artifact.json — the same three scenarios on the real frozen SKILL.md: A (r59 gate row
  inserted) rc0, B (fenced r59 gate decoy appended, no real registration) rc0, C (r58 kind edited
  only) rc0.
- probe-counter-semantics.json — P1–P12. Note: P2/P3 were labelled before the shadow test was
  isolated and are superseded by Q1–Q3; their raw rc/stdout is still valid (the r59 row used in them
  was `evidence`, not `gate`). P8 tests a name-extension decoy and is NOT a hole (the prefix is
  exact; the row is not matched and the counter falls back to r58, rc1).
- probe-frozen-selftest-mutants.json — always-clean / ignore-duplicate / accept-prose mutants run
  through the frozen controls driver; each rc1 at the intended case.
- probe-frozen-r58-note-semantics.json — R1 honest rc0; R2 fenced notes rc0; R3 notes under an
  archived heading rc0; R4 wrong value rc1; R5 missing note rc1; R6 extra divergent row in one
  matrix invisible (`zip` truncation), rc0 with honest notes.
- probe-controls-replay.json — two runs of the frozen controls a second apart: all four fixture
  OIDs differ (no fixed dates) => recorded `input_rev`s are not replayable.
- probe-candidate-selftest-mutants.json — delivered candidate pristine rc0/5 cases + five mutants
  killed by its own selftest (rc/findings/summary fields named per case).
- probe-candidate-limits.json — delivered candidate: selftest 5/5, 5 CLI self-execs, rc2
  CANNOT-EVALUATE without traceback, parity with the r58 counter at base, plus inherited limits
  (fenced notes rc0, archived-section notes rc0, zip truncation rc0 at 36 vs 38 rows).
- verified-sha256.txt — sha256 of every frozen surface pinned by this review, plus the delivered
  candidate bytes.
