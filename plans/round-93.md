# souji round 93 — plan, dispositions and amendments (L1 SoujiR93)

Lane base `91c9bcb1041b18be154ca466ac3c047ac7862fe1` (r92 closed). Contract: `census/round-93/preregistration.txt`
(commit F). Amendments below never widen a frozen sentence; a wave artifact that falsifies a claim's wording is
recorded here as a narrowing or an honest stop before filing (Amendment 59).

## A0 — before the wave

### A0.0 Claim choice (L1 planner seat)

- Load: MISSION.md, AXES.md, CORPUS.md (SOURCES contract), lane SCORECARD.md `### Planned (r93)`, the r92 non-author
  spot-check (`corpus/lessons/round-92-verifier-spotcheck.md` §7 routed items 1-5), the r92 wave reports R92MutC1
  (§2 E1, §3c a491c22) and R92MutC2 (forgeries C/D/E survive 20/20).
- Lowest owned non-retired axis: calibration 7 (SCORECARD `## Axes`) → C1. Routed item 2 (E1 binding row) is C1; the
  spot-check's "asserting rc 1" reading is used (R92MutC1's "expect_rc 0" wording is wrong: the pristine counter
  exits 1 on a run with one unresolved item — `census/round-93/records/c1-pristine-after.txt` LD5 `rc=1`).
- Routed item 1 (C2 maximality case) is C2, named coverage: the surface moved is the fixture's edge class (cut
  position), the tool is unchanged; the r92 fixture is the command that shows it unmoved (control `rejected=5`).
- Routed item 3 (search robustness) rides C1's instrument (kill rule, SIGINT/SIGTERM cleanup, `--emit` /tmp guard);
  it is not a claim. Routed item 4 (SOURCES rule 2): r93 appends S356 only and edits no existing cell (checked by
  R93Connector). Routed item 5 (seat write scope): the wave context forbids fleet-root writes; the misroot sweep
  checks it.
- Sourced claim: C2 rests on S356 (WHATWG Encoding Standard §8.1.1, opened 2026-11-09). S351 already holds the
  Python codecs page, so the `surrogatepass` handler doc was not a new row; the decoder algorithm is new ground.

### A0.1 Round shape: `labrat` is not a swarm role

The prereg's ROUND SHAPE lists `1 labrat`. The wave validator refused it (`.ufo/waves/round-93/w1-run.err` first
run: `items[8].role "labrat" is not a swarm role`). R93Labrat runs as a `mutation-tester` with the same item; the
attack share under the addendum's four roles is unchanged (6/13). No claim sentence is affected.

### A0.2 Lost control runs (L1 tooling mistake)

The L1 first started the three controls as background jobs in ONE shell call (`&` … `wait`); the shell tool
panicked (`JoinHandle polled after completion`) and only the C1 control file was written. The two C2 controls were
re-run sequentially on the same committed bytes before P2; every committed control receipt is from a completed run.
Mined as a lesson mistake.

### A0.3 Pre-freeze feasibility

Disclosed in `census/round-93/controls/prefreeze-feasibility-note.txt`: the C2 after arms and the C1 pristine
harness were run before F; no C1 mutant was scored on the r93 population before F (`census/round-93/c1-prediction.txt`
is in P1).
