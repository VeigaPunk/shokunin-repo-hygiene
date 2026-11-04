# S59Reviewer — round 59 bounded assessment gate

Scope: frozen claim `census/round-59/preregistration.txt` @ `19f44552378d333f401ff2f0864c4e8b9c59ab1f`,
executed controls @ `74455b7209e04a2375c2084738a7b6fea59bf6d5`, the frozen instrument
`census/round-59/c1-counter.py`, its four-case control driver, the actual r58 comparator
`census/round-58/c1-counter.py`, and the candidate delivered at
`.ufo/waves/round-59/w1/S59ExecGate/`. Read-only on production; every mutation in this review
happened in `/fast/scratch/hyaku/souji-r59/S59Reviewer/` (fixture repos asserted with
`git rev-parse --show-toplevel` before any commit, plus one read-only `git clone --shared`).
No freeze edits, no production edits, no commits, no history changes.

## Verdict

**Prerequisite: HOLDS.** Controls are committed before the freeze, the frozen bytes are the bytes
the controls pinned, and no candidate measurement existed pre-freeze. `before.txt` reproduces
exactly.

**Claim measurement: NOT ADMISSIBLE AS EVIDENCE UNCHANGED.** The 1→0 transition is reached by a
*population switch*: the counter prefers `| r59 assessment comparison |` and silently stops
counting the `r58` row that `population.tsv` names. On the frozen SKILL.md the same instrument
also returns `mismatches=0` for a one-line **fenced decoy row** and for a row pointing at a
**nonexistent instrument**. The numeric target is therefore necessary but not sufficient, and the
wave report must carry two direct checks the counter cannot perform.

**Selftest substance: PASS for the frozen control battery, PASS for the delivered candidate**
(5/5 cases, 5 mutants killed, 5 real CLI subprocess self-invocations). Both are green while the
claim itself is red, so neither may be cited as evidence that the target is met.

## 1. Canonical-runtime identity (one instrument, one byte identity)

Every count below came from one counter instance; no second implementation was used.

| surface | identity | evidence |
|---|---|---|
| `census/round-59/c1-counter.py` | `sha256=2c4d45aab440ef713f22a8d3b210e651d6e7047451cab26f9d4316f5a6451a6d` | equals the digest pinned in `preregistration.txt:6`; `git show 74455b7:…` hashes to the same value, so the pre-freeze control run bound these exact bytes |
| `census/round-59/controls.py` | `sha256=ba8af5cc5404eb4108ab15ee6386d15907c73abf04cda3b780e592b5d7d452b8` | identical at `74455b7` and at freeze |
| `census/round-59/population.tsv` | `sha256=c2e24c9961dd8d54794b3dea1e959ead1072c493c095874d661d59bc0ef9adb0` | equals `preregistration.txt:7` |
| `census/round-59/preregistration.txt` @freeze | `sha256=8ca0c77503962f8d99d9a652db8d8906c3a00b9eb3e088238ec7cf479bca6ae3` | `git show 19f4455:…` |

Topology: `19f4455` parent `74455b7`, parent `da5af55b` (base). `git diff --name-status 74455b7 19f4455`
is exactly `A population.tsv`, `A preregistration.txt`; `SKILL.md` and `SCORECARD.md` are untouched
across `da5af55b..19f4455`. `git show 74455b7:SKILL.md` contains **zero** `r59` rows and no
`assessment-gate` file exists at either commit. So: controls before freeze — yes; candidate
measurements before freeze — none.

Reproduced baselines (read-only, from the lane root):

```
python3 -B census/round-59/c1-counter.py --root . --rev da5af55b…
  FINDING REGISTRY-KIND-MISMATCH
  SUMMARY assertions=1 mismatches=1 rev=da5af55b…            EXIT=1   (= before.txt, verbatim)
python3 -B census/round-59/c1-counter.py --root . --rev 19f4455…
  FINDING REGISTRY-KIND-MISMATCH
  SUMMARY assertions=1 mismatches=1 rev=19f4455…             EXIT=1   (freeze state is still red)
python3 -B census/round-58/c1-counter.py --root . --rev da5af55b…
  MATCH …carry_identical=34… / MATCH …exit_zero=10,8…
  SUMMARY assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8  EXIT=0
```

## 2. Findings by severity

### B1 — BLOCKER — the declared population is shadowed by the candidate's own registration

`run()` selects r59-prefixed rows and only falls back to r58 when there are none
(`c1-counter.py:10-13`). The declared population is `R58-KIND | SKILL.md r58 assessment comparison`
(`population.tsv:2`), but once the planned r59 row exists the r58 row is never read again.

Minimal repro (`probe-counter-shadow.json`, `Q1` vs `Q2`), full frozen document in
`probe-frozen-artifact.json`:

| fixture | rc | SUMMARY |
|---|---|---|
| `A` frozen SKILL.md + r59 `gate` row inserted after the r58 row (r58 row untouched, still `evidence`) | **0** | `mismatches=0` |
| `B` frozen SKILL.md unchanged + r59 `gate` row appended inside a `~~~` fence | **0** | `mismatches=0` |
| `C` frozen SKILL.md with only the r58 row's kind changed `evidence`→`gate` | **0** | `mismatches=0` |
| `Q2` frozen SKILL.md unchanged (r58 `evidence` only) | 1 | `mismatches=1` |

Consequence: a wave report reading `mismatches 1→0` after (A) is true of the *current* row and false
of the *declared* row, and the counter provides no signal distinguishing a truthful supersession
from a decoy. This is the "same-identity rerouting" failure for this claim: the measurement identity
changes from the r58 row to the r59 row without any instrument-visible event.

**Required before admission (bounded, no freeze edit):** the wave report must carry a direct row
assertion independent of `c1-counter.py`, e.g.

```
git show <candidate>:SKILL.md | awk -F'|' '$2==" r58 assessment comparison " {gsub(/^ +| +$/,"",$3); print "r58kind=" $3}'
git show <candidate>:SKILL.md | awk -F'|' '$2==" r59 assessment comparison " {gsub(/^ +| +$/,"",$3); print "r59kind=" $3}'
```

and must state explicitly whether the r58 row was corrected to `gate` or deliberately left
`evidence` as historical. If it is left `evidence`, the claim as frozen must be described as a
registration of a new current row (population change), not as a correction of `R58-KIND`.

### B2 — HIGH — a fenced decoy row satisfies the target on the real frozen artifact

The counter scans raw lines (`text.split('\n')` + `startswith`) and has no fence model. `B` above
shows the frozen SKILL.md + an appended `~~~` block containing one r59 `gate` row → `EXIT=0`.
`Q4` reproduces the same with a minimal fixture. The four frozen controls cover prose forgery
(`P10`/`prose-forgery`: still rc1, correct) and duplicate forgery, but **not** structural fence
forgery — even though r56/r57 counters in this lane treat fenced text as a named finding class
(`CORRECTION-IN-FENCE`, `PAIR-FILING-HIDDEN`). A `mismatches=0` obtained from chrome is
indistinguishable from a real registration by this instrument.

Disposition: the frozen counter cannot be changed (freeze rule). Record it as a named limit of C1's
measurement and make the B1 direct assertion authoritative; do not describe the four controls as
covering "forgery" without this qualifier.

### H3 — HIGH — kind-string-only: no instrument existence, no self-test cell, no table context

| probe | fixture | rc |
|---|---|---|
| `P5` | row kind `gate`, self-test cell still says *"counter has no self-invocation certification"* (self-contradictory row) | **0** |
| `P6` | row kind `gate`, entry command points at `census/round-59/NOSUCH-gate.py` (no such file) | **0** |

The counter never reads the entry-command path, the self-test column, or the pinned-value column, and
never checks that the row sits in the registry table. The kill criterion "missing actual assessment
gate/self-invocation repair" is **not measured by the frozen instrument at all** — it is a
planner/integrator judgment. The wave report must demonstrate substance independently (section 3).

### M4 — MEDIUM — `assertions=1` is a literal; only one bit carries information

`c1-counter.py:19` prints `assertions=1` unconditionally and `findings` holds at most one element.
The target can never print `assertions=0` or `2`. `assertions=1 mismatches=0` therefore encodes
exactly one fact: the selected row's kind cell equals `gate`. No overclaim should be attached to the
word "assertions".

### M5 — MEDIUM — population.tsv is inert

Neither the counter nor the control driver opens `population.tsv` (verified by grep over
`census/round-59/`; the only references are the preregistration lines). The sha256 pin on it and the
"population byte-identical" clause of the freeze rule constrain nothing. Only the counter and
`controls.py` bytes are load-bearing.

### M6 — MEDIUM — control fixture revisions are dangling and non-replayable

`controls.json` records `input_rev` for each case, but `controls.py` deletes its fixture in
`finally: shutil.rmtree(work)` and commits with **wall-clock** dates (no fixed
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`). Two replays a second apart produced four different OIDs
each (`probe-controls-replay.json`), and the recorded `command` paths point at
`/fast/scratch/hyaku/souji-r59/l1/controls-phpd10up`, which no longer exists. The preregistration's
"Input bytes and fixture revisions retained there" is half true: `input_skill` bytes are retained,
the revisions are not obtainable. The cases still pass and still discriminate (see P8), so this is a
retention/claim defect, not a control defect. The candidate's fixtures do use fixed dates and are
replayable — hold the candidate to that standard and do not copy the frozen wording.

### M7 — MEDIUM — frozen counter conflates could-not-evaluate with mismatch

`P11` (unresolvable rev) and `P12` (non-repo root) both exit **1** with a Python traceback and
**no** `FINDING`/`SUMMARY` line; a genuine mismatch also exits 1. So `EXIT=1` alone is not a claim
signal unless stdout is read. The candidate fixes this properly (rc2 `CANNOT-EVALUATE`, no
traceback), which is an intended extension over r58's accidental rc1 — the registered verdict map
must say so and must not claim byte-parity for invalid inputs.

### M8 — MEDIUM — row uniqueness is per-prefix only

One r58 row + one r59 row is accepted as "unique" (`Q1`). Two r59 rows → rc2 `REGISTRY-ROW-SHAPE`
(`P9`), two r58 rows → rc2 (`Q6`), 11 cells → rc2 (`Q5`), kind `gate ` with trailing spaces → 0
(`Q7`, benign `strip()`), a leading space before the row → falls back to r58 → rc1 (`Q8`,
fail-loud). Good inside a prefix; blind across prefixes.

### P9 — POSITIVE — the frozen four-case battery has real discrimination

`controls.py` runs the counter as a subprocess and compares `returncode` **and** the exact ordered
finding list (`r.returncode==expected_rc and actual==expected`). Re-executed here: `passed=4/4`,
`EXIT=0`. Independent mutants in my scratch, run through the frozen driver:

| mutant | driver rc | failing case |
|---|---|---|
| always-clean (drop the kind comparison) | 1 | `unchanged`, `prose-forgery` (rc 0 vs 1) |
| ignore duplicate guard | 1 | `duplicate-forgery` (rc 1 vs 2) |
| accept prose `gate` word | 1 | `prose-forgery` (rc 0 vs 1) |

`strace -f -e trace=execve` shows the selftest path launches the counter as **4** real CLI children
plus `controls.py` once, and the fixture child is removed. So the claim "executable selftest
substance" is earned for the frozen counter. Two binding limits: the selftest derives its root from
`__file__.parents[2]` and hardcodes base `da5af55b…`, so a faithful copy outside the lane repo exits
1 with a traceback (false red, probe A); and it never measures the candidate revision — at freeze,
`--selftest` is green (`passed=4`) while the claim measurement is red (`mismatches=1`). A green
selftest is not evidence about the target.

### P10 — POSITIVE — the delivered candidate gate is substantive

Candidate: `assessment-gate.py` `sha256=4dfdd13eb7061e52da709e7ee7bd51cada64322cf26939bbf4768ecf53913b66`,
expected TSV `sha256=2eb315f8352b55c6a3ba1c90fc3f4f58a33736c51547f118d199bdb5781635ef` (both match
`S59ExecGate/digests.txt`; the r58 commentary strings are preserved byte-for-byte and stdout at base
is **identical** to the r58 counter's).

Exercised, not read:

* `--selftest --work <scratch>` → `rc=0`, `SELFTEST pass cases=5`, `control=FALSE-GREEN-REJECTED
  stub_meets=1 discriminated=4`, stderr empty, unique child removed, two runs byte-identical (fixed
  dates).
* `strace -f -e trace=execve` → **5** successful child `execve`s of `assessment-gate.py` itself
  (+51 git), i.e. actual CLI self-invocation, not import.
* Five mutants of a scratch copy, each killed by the candidate's own selftest with the right case and
  field named: always-clean (`rc,findings,mismatches,verdict_count`), rc-ignored (`rc`),
  finding-ignored (`findings`), expected row dropped (`SELFTEST-EXPECTED-SET … missing=WRONG-VALUE`),
  summary hard-coded (`mismatches,verdict_count`). Pristine sha restored after each.
* Negative paths: unresolvable rev, non-repo root, missing args → `rc=2`, `CANNOT-EVALUATE`, **no
  traceback**.
* `--root LANE --rev` at base and at freeze → `rc=0`, two `MATCH`, `carry_identical=34`, `exit_zero=10,8`.

Caveat on the built-in control: `control=FALSE-GREEN-REJECTED` compares the *expected table* against
a stub verdict; it does not execute a stub gate. It is honest as a table-level meta-check, but the
kill power comes from the external mutants above — do not describe the built-in control as mutation
testing.

### R11 — RESIDUAL (inherited by design, must be disclosed, not "fixed")

* **Notes are substring matches anywhere in `SCORECARD.md`.** Candidate returns `rc=0` with the two
  notes inside a ``` fence, and `rc=0` with them under `## Archived withdrawn claims`
  (`probe-candidate-limits.json`). This is the r58 derivation, preserved as contracted. Since the
  row's kind becomes `gate`, the registry/limit text must say the gate establishes *presence*, not
  live-section assertion.
* **`zip` truncation.** `identical` iterates `zip(*tables)`, so extra rows in the longer matrix are
  invisible: with 36 v5 rows and 38 v6 rows (one extra divergent row) the candidate still reports
  `carry_identical=34` and `rc=0`. Row cardinality is not asserted. Also `list(row.values())[4]` is
  a positional column assumption on the committed matrix header.

Both are acceptable if disclosed; neither may be cited as coverage of row-set or section-context
conformance. Fixing them would change verdict semantics (rc0 cases become rc1), so it is out of the
"preserve exact derivations" contract.

### L12 — LOW

* `score_case` never inspects the child's `stderr`; a warning on a passing case is invisible (the
  frozen `controls.py` has the same gap).
* The candidate's `_lane_root()` requires the gate to live in a Git worktree with `da5af55b…`
  reachable; running the delivered bytes from outside the lane gives `CANNOT-EVALUATE` (rc2, clean).
  Fine for production, worth one line in the registered write-scope.
* `--selftest` ignores `--root`/`--rev`; not documented in `--help`.
* The `BOTH-MISSING` case proves `mismatches=2` is reachable, but the declared target only exercises
  0/1.

## 3. Production substance check (exact, and what remains unexercised)

No production integration existed at review time: `census/round-59/assessment-gate.py` is absent and
`SKILL.md` still has zero r59 rows; the delivery directory is gitignored (`.gitignore:1:.ufo/waves/`)
so the candidate is not a committed snapshot. Everything below that depends on the *production*
path is therefore **unexercised**; the same checks were exercised against the delivered bytes.

```
CAND=<production>/census/round-59/assessment-gate.py        # sha256 must equal 4dfdd13e… unless changed
1  python3 -B $CAND --selftest --work <scratch>
     expect rc0, SELFTEST pass cases=5, control=FALSE-GREEN-REJECTED, empty work child
2  python3 -B $CAND --root <lane> --rev <candidate-commit>
     expect rc0, two MATCH lines byte-identical to the r58 note text, SUMMARY assertions=2
     mismatches=0 carry_identical=34 exit_zero=10,8
3  independent negative fixture (one note omitted / wrong value) over a committed fixture
     expect rc1, exactly one FINDING ASSESSMENT-MISMATCH, one MISSING line, mismatches=1
4  mutant of the note derivation in a scratch copy -> selftest must return nonzero
5  strace -f -s 400 -e trace=execve … --selftest  -> >=5 successful child execs of $CAND
6  direct registry rows (authoritative; the counter cannot do this once r59 exists):
     git show <candidate>:SKILL.md | awk -F'|' '$2 ~ /^ r5[89] assessment comparison $/ {gsub(/^ +| +$/,"",$3); print $2 "kind=" $3}'
     and confirm the row is a real table row, not inside a fence, and that its entry-command path
     exists at the candidate revision
7  python3 -B census/round-59/c1-counter.py --root <lane> --rev <candidate-commit>
     expect rc0 mismatches=0 — record it as necessary, not sufficient
```

Admission should additionally require the wave report to state which of the two readings of the claim
it is making (B1): correction of `R58-KIND`, or re-registration of a new current row.

## 4. Residual risk and verification gaps

1. B1/B2 mean `mismatches=0` cannot distinguish the honest candidate from a decoy on its own. The
   evidential chain depends on step 6 above being recorded.
2. No independent oracle exists for the two derived notes beyond the r58 source and the paste/awk
   derivation in `S59ExecGate/independent-derivation.txt` (which I re-derived: 10, 8, 34 — agree).
3. The candidate's green does not cover row cardinality or note placement (R11).
4. Controls cannot be replayed to the recorded fixture OIDs (M6). Semantic replay works because
   `input_skill` bytes are retained; the OIDs are decorative.
5. `resume_continuity_v1`: not applicable — this ticket has no resume/preflight path. No
   `lsp` server answered this lane's Python files, so caller/definition checks were done by direct
   source reading of the two instruments and the registry row; no claim here rests on grep semantics
   alone.
6. I did not edit, integrate, ship, or invoke another runtime; the candidate was executed read-only
   from delivery with `--work` in my own scratch. This verdict is a recommendation.

## 5. Receipts

Delivery: `.ufo/waves/round-59/w1/S59Reviewer/` — `verified-sha256.txt`, `probe-counter-semantics.json`
(P1–P12), `probe-counter-shadow.json` (Q1–Q8), `probe-frozen-artifact.json` (A/B/C on the real
frozen SKILL.md), `probe-frozen-selftest-mutants.json`, `probe-frozen-r58-note-semantics.json`
(R1–R6), `probe-controls-replay.json`, `probe-candidate-selftest-mutants.json`,
`probe-candidate-limits.json`. All fixture repositories and mutants were under
`/fast/scratch/hyaku/souji-r59/S59Reviewer/` and were removed after the receipts were captured;
the one clone used the lane read-only via `--shared` alternates.
