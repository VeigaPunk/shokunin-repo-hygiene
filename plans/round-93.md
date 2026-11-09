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

The prereg's ROUND SHAPE lists `1 labrat`. The wave validator refused it (`items[8].role "labrat" is not a swarm
role`; the first run's stderr was overwritten by the second run's empty `w1-run.err`, so the refusal is reproduced
on a scratch copy of the spec with that one role restored: `census/round-93/controls/labrat-role-refusal-repro.txt`,
EXIT 1). R93Labrat runs as a `mutation-tester` with the same item; the attack share under the addendum's four roles
is unchanged (6/13). No claim sentence is affected.

### A0.2 Lost control runs (L1 tooling mistake)

The L1 first started the three controls as background jobs in ONE shell call (`&` … `wait`); the shell tool
panicked (`JoinHandle polled after completion`) and only the C1 control file was written. The two C2 controls were
re-run sequentially on the same committed bytes before P2; every committed control receipt is from a completed run.
Mined as a lesson mistake.

### A0.3 Pre-freeze feasibility

Disclosed in `census/round-93/controls/prefreeze-feasibility-note.txt`: the C2 after arms and the C1 pristine
harness were run before F; no C1 mutant was scored on the r93 population before F (`census/round-93/c1-prediction.txt`
is in P1).

## Wave findings and amendments (after WAVE-DONE; `.ufo/waves/round-93/w1-results.json`, 13/13 settled)

### A1 — C1 wording: "because no r92 run reaches their clause" (FALSIFIED as worded; narrowed)

R93ReviewerC1 §2 S2/S2a/S2b (`.ufo/waves/round-93/w1/R93ReviewerC1.md`, receipts `log-r92-pristine.txt`,
`log-r92-hok.txt`, `log-r92-a491.txt`): both clauses execute in every r92 run, and under `h-ok-admits-one` three r92
runs (NF-R, NF-S, NF-W) change the counter's exit 1 → 0 while their rows assert no exit code (`REFUSED/-`). R93Critic
item 1 independently: the instrument measures survival, not reachability. **Narrowed sentence (replaces the
"because" clause; nothing widened):** "Two counter edits survive every r92 row: no r92 row asserts an outcome either
edit changes (under h-ok-admits-one three r92 runs change exit 1 → 0 on rows that assert no exit code; under
a491c22 no r92 run's outcome changes)." The predicate, control and after numbers are unchanged.

### A2 — C1 wording: "bind both" means the two edits, not their clauses

R93MutC1 §1: three other spellings of the same clauses survive the r93 population (m5 `resolved == len(pop) -
len(unknown)`, m6 `resolved >= len(pop) - len(unknown)`, g2 `len(r) not in (3, 4)`); R93Critic item 2. Stated limit
(i) already says "two edits are bound, not their clauses"; the claim sentence "bind both" is read as "make the harness
exit 1 with a row mismatch on both named edits" and nothing more.

### A3 — C1 kill rule: "tighter than r84-r92" holds only for counter exit 2 (FALSIFIED as worded; narrowed)

R93Sentinel M1 (`R93Sentinel/repro/h-crash3.out`), R93Scribe FK1 (`R93Scribe/fk1-verdict.txt`), R93MutC1 §2 k2: a
counter that raises an uncaught exception exits 1, not 2; the harness then prints `got=- ... match=no` on the
ledger rows and `verdict()` returns `yes`. The search docstring's parenthetical "(the counter crashed, rc 2)" is
false for that case. **Narrowed sentence:** "the r93 kill rule scores a harness exit 2 and a counter exit 2
(`match=error`) as `errored`; a counter that raises an uncaught exception exits 1 and is still scored killed." Both
C1 kills are semantic, not crashes: the killing rows read `got=UNRESOLVED` (LD5 `rc=0 match=no` for h-ok-admits-one;
LD6 `rc=1 match=no` for a491c22), attributed one-row-each by R93ExecC1 §5, R93ExecResidual (a) and R93MutC1 §3.
The frozen search is not edited this round; the fix (score `got=-` rows or a counter traceback as `errored`) is
routed to r94.

### A4 — C1 reproducibility: the harness reads two gitignored lane-disk paths (stated limit added)

R93Critic separability (a): in a plain clone both targets read `errored` (rc 2) because the harness needs
`census/operator-sweep-20261019/` and `.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt`, both
gitignored. The predicate names `--lane .` (this checkout), so the numbers hold; C1 is not reproducible from committed
bytes alone. Inherited from the r79+ harness lineage; routed.

### A5 — C2 wording: "the r92 fixture checks" and "independent reference cut" (precision; narrowed)

R93ReviewerC2 note: the prefix/suffix sentence describes KFF18, the r92 fixture's only cut-position case (other cases
check spellings). R93Critic item 3: the reference is independent of the tool's implementation and of Python's codec
(no codec call; R93ExecC2 §3 ast/grep; R93Critic refcheck 77,305,472 comparisons, 0 mismatches) but copies the
excerpt-format constants (limit 200, head 100, keep 99) from the tool's contract. **Narrowed sentences:** "KFF18, the
r92 fixture's cut-position case, checks only that ..."; "a reference cut independent of the tool's implementation
and of Python's codec (it shares the excerpt-format constants)". Numbers unchanged.

### A6 — C2 axis wording (no score change)

R93Critic §C2: coverage fits through AXES.md's "edge classes" clause, but 8/8 is a count over a chosen forgery set,
not a fraction of a surface. The SCORECARD row names the edge class moved (cut position) and the command that shows it
unmoved (the r92 fixture, `rejected=5`); coverage stays 8.

### Neutral / within stated limits

- R93ExecC1, R93ExecC2, R93ExecResidual, R93Labrat, R93ScoutSources, R93Connector: every number re-derives; the 78-id
  residual set differs between populations by exactly the two targets (`killed=0 survived=78` → `killed=2
  survived=76`, no errored, no hung); 300,000 random payloads 0 filed-tool disagreements with the reference; SIGTERM/
  SIGINT exit 130 with 0 trees left (SIGKILL still strands, stated r92 residual); S356 live byte-identical; rule 2
  compliant (one added row, zero removed lines).
- R93MutC2: 9 forgeries, 7 rejected; survivors c_reprokey (prereg limit iii) and h_filler_a (limit i, filler `a`);
  a_window3 equivalent. R93Critic: two more forgeries (G1b lookback-2, G2-max3) rejected by KFF19.
- R93Sentinel M2 (MEDIUM, conservative): an in-process exception in a tool under test (KFF18/KFF19) escapes
  `score()` and crashes the fixture; it can only under-count rejections. Routed.
