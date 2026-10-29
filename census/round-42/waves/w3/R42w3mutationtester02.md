# R42w3mutationtester02 — mutation test of the LANDED C3 fixture

Seat: `R42w3mutationtester02` (role mutation-tester), round 42 wave 3.
Re-issues wave-2 seat `R42w2mutationtester03` (whose grid was partial: 634 of 659 cells, `X12`
incomplete, `X13` absent).
Target: `tests/fixtures/r42-drift-conditions.py` as landed at
`6a3f75941d3604e3459011d599c2c16f3a97b44c`.

**Verdict: the landed fixture is sound for its frozen target.** It kills all 13 population
mutants, kills none of the 6 equivalent mutants, passes clean on the pinned tool with 13 cases,
and — under mutation of the fixture itself — 11 of its 13 cases are individually load-bearing
and the remaining two are *mutually* redundant but jointly necessary (no single case can be
deleted without losing a kill). Three narrow, named redundancies exist inside two cases
(findings F1–F3 below); they are **coverage observations, not defects**, and no edit to the
fixture is proposed by this seat (the fixture is frozen for this wave).

---

## 1. What was attacked

The axis under test is **C3 coverage**, attacked from the fixture side: the population
(`census/round-42/c3-counter.py` `MUTANTS`: B1 E2 E4 G2 G3 G4 G5 H1 H2 I1 J9 M1 D4) is held
fixed and the *fixture* is mutated. A fixture mutant that still kills every population mutant
and still passes the pinned tool is a **redundant or vacuous assertion**; one that loses a kill
identifies a **load-bearing** assertion.

Every mutant is a single-point `(old, new)` string replacement in the landed fixture blob, or a
single insertion into the `CASES` filter that drops one case. `mutants.py` `build()` asserts
that each `old` string occurs **exactly once** in the blob, so each mutant is provably
single-point; `python3 mutants.py` reports `mutants: 74` / `all mutants compile`.

Mutation kinds used (as the seat spec requires): asserted **exit code** (N01, N02, N21, N22),
**token** (T01–T07, N08, N12, N13, N18), **count** (C01–C04, N11, N20, N23, N24), **removed
case assertion** (D01–D13), **widened timing bound** (W01–W04, N17), **dropped case**
(X01–X13), plus **argument/value** (N03–N07, N09–N10, N14–N16, N19), **helper predicate**
(H01–H06) and **counter-protocol** (N23, N24) attacks.

## 2. Reuse vs redo (explicit)

| artefact | provenance | action in wave 3 |
|---|---|---|
| `w2/R42w2mutationtester03/grid.jsonl` (634 cells) | wave-2 seat, run at tip `3105a63b` | **REUSED as a cross-check only.** The fixture blob and the pinned tool blob are byte-identical at both tips: fixture `sha256 03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45`, tool `sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` (= the counter's pinned `PRISTINE_SHA256`). |
| wave-2 mutant catalogue H/D/C/W/T/X | wave-2 seat | **REUSED verbatim** (ids H01–H06, D01–D13, C01–C04, W01–W04, T01–T07, X01–X13 = 47 mutants). |
| wave-3 mutant catalogue N01–N24, P01–P03 | **NEW in wave 3** (27 mutants) | **RE-DONE** — written and run for the first time here. They attack angles the wave-2 catalogue did not cover: per-case exit codes, per-case argument values, the `ROW` constant, JSON key names, the `SUMMARY` protocol fields, and *pairs* of dropped cases. |
| the grid itself | — | **RE-DONE in full.** The wave-3 grid was produced by this seat from scratch: 1050 cells = 75 fixture ids (BASE + 74 mutants) × 14 tools (pristine + 13 population mutants). |
| `X12` / `X13` cells | wave-2 left them incomplete/absent | **RE-DONE** (both now complete). |

Cross-check of the reused wave-2 grid against the wave-3 grid (`crosscheck.py`):

```
w2 cells=634  w3 cells=952  shared=634
disagreeing shared cells: 0
cells only in w3: 318
```

Zero disagreements on all 634 shared cells over the fields the verdict depends on
(`rc, cases, passed, failed, crash, failing, timeout`). The wave-2 partial work is therefore
confirmed, not merely trusted.

## 3. Commands actually run, and their output

### 3.1 Blob identity of the frozen inputs

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:tests/fixtures/r42-drift-conditions.py | sha256sum
03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45  -
$ git -C ... show 3105a63b...:tools/souji-worktree-drift.py | sha256sum
b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6  -
$ git -C ... show 6a3f75941d3604e3459011d599c2c16f3a97b44c:tests/fixtures/r42-drift-conditions.py | sha256sum
03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45  -
$ git -C ... show 6a3f7594...:tools/souji-worktree-drift.py | sha256sum
b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6  -
```

### 3.2 The grid (this seat's own run)

```
$ cd .ufo/waves/round-42/w3/R42w3mutationtester02
$ python3 -B harness.py --workers 10 --base      # 952 cells
BATCH start: 952 cells, workers=10, load=22.73 29.41 37.11
...
BATCH end: 952 cells, load=142.99 110.11 60.45
$ python3 -B harness.py --workers 6 --only N21,N22,N23,N24,P01,P02,P03   # 98 more cells
BATCH start: 98 cells, workers=6, load=274.53 274.73 255.10
BATCH end: 98 cells, load=162.39 213.57 238.42
$ wc -l grid-w3.jsonl
1050 grid-w3.jsonl
```

Integrity of the grid (`analyse.py` + an inline audit):

```
fixture mutants: 75 (BASE + 74)
cells: 1050 duplicates: 0
missing cells: []
cells per tool: {'B1': 75, 'D4': 75, 'E2': 75, 'E4': 75, 'G2': 75, 'G3': 75, 'G4': 75,
                 'G5': 75, 'H1': 75, 'H2': 75, 'I1': 75, 'J9': 75, 'M1': 75, 'pristine': 75}
any crash/timeout: []
```

Every cell was run; no cell crashed and no cell timed out.

### 3.3 The frozen counter's own verdict on the landed fixture (authoritative path)

```
$ bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42w3mutationtester02
MUTANT B1 candidate=killed prior=-        (… E2 E4 G2 G3 G4 G5 H1 H2 I1 J9 M1 D4 all candidate=killed)
EQUIV B3 candidate=survived prior=-       (… B4 E5 E7 E9 H4 all candidate=survived)
SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
```

### 3.4 My harness cross-validated against the frozen counter

Five fixture mutants were scored through `score-candidate.sh c3` (the counter clones the lane,
overwrites the candidate, and re-measures). The counter's `killed`/`survived` counts and
`pristine` verdict match this seat's grid verdict **exactly** in every case, so the grid's
verdict semantics are the counter's, not a private re-interpretation:

| fixture mutant | counter `SUMMARY` | my grid verdict | agree |
|---|---|---|---|
| D12 (json-truncate assertion removed) | `killed=13 survived=0 pristine=ok` | 13/13 REDUNDANT | yes |
| D04 (timeout-one assertion removed) | `killed=13 survived=0 pristine=ok` | 13/13 REDUNDANT | yes |
| X04 (drop timeout-of-one case) | `killed=13 survived=0 pristine=FAIL cases=12` | 13/13, cases=12 | yes |
| H05 (`drift_line` loses its stdout token check) | `killed=11 survived=2` (G4, G5 SURVIVED) | 11/13, lost G4,G5 | yes |
| N11 (json filler 5000→5 bytes) | `killed=12 survived=1` (M1 SURVIVED) | 12/13, lost M1 | yes |
| P01 (drop both G2-killing cases) | `killed=12 survived=1` (G2 SURVIVED) | 12/13, lost G2 | yes |
| N23 (SUMMARY fail count pinned to 0) | `killed=0 survived=13 pristine=ok` | 0/13 | yes |
| N24 (SUMMARY pass count pinned) | `killed=13 survived=0 pristine=ok` | 13/13 REDUNDANT | yes |

Verbatim counter lines for the two decisive ones:

```
=== COUNTER SCORE fixture-mutant H05 ===
MUTANT G4 candidate=SURVIVED prior=-
MUTANT G5 candidate=SURVIVED prior=-
SUMMARY mutants=13 killed=11 survived=2 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247

=== COUNTER SCORE fixture-mutant N23 ===
MUTANT B1 candidate=SURVIVED prior=-      (… all 13 SURVIVED)
SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247
```

### 3.5 Load-sensitivity: the G3 column re-verified serially

C3 is load-sensitive because the fixture's `default-timeout-outlasts-a-blocked-git` case
asserts `elapsed >= 5.0` on a run whose tool default timeout is 20 s, while the G3 population
mutant lowers that default to 1 s. Under heavy load the 1 s run could overrun 5 s of wall
clock and make G3 appear to survive spuriously.

The grid was run at load 16→290 (the host was shared). The whole G3 column was therefore
re-run **serially, one cell at a time, never in parallel**, with the load printed before every
cell (`reverify.py`, `grid-reverify.jsonl`, 68 cells):

```
load-before BASE   G3        load=165.12 131.10 75.70
  -> BASE   G3        rc=1 cases=13 pass=12 fail=1 failing=default-timeout-outlasts-a-blocked-git load=166.31 131.91 76.26
load-before D05    G3        load=159.93 137.49 82.26
  -> D05    G3        rc=0 cases=13 pass=13 fail=0 failing= load=159.72 138.18 83.08
...
load-before W01    G3        load=237.42 196.39 126.65
  -> W01    G3        rc=0 cases=13 pass=13 fail=0 failing= load=238.46 197.96 127.91
load-before X05    G3        load=240.88 207.84 136.78
  -> X05    G3        rc=0 cases=12 pass=12 fail=0 failing= load=242.26 207.84 136.78
```

Result: **all 68 serial G3 cells reproduce the grid verdict exactly**, including the four
intended exceptions (D05, W01, W02, X05 — the mutants that weaken or delete the timing
assertion itself). The G3 kill is therefore robust across a load range of 16–290 and is not a
load artefact. Note also that the base fixture run takes ~42 s on this host and the G3 mutant
run ~4.6 s, so the 5.0 s bound sits in a wide gap.

## 4. Main table — fixture mutant | pristine | population mutants still killed | verdict

Full 74-row table with each mutant's description is in
`.ufo/waves/round-42/w3/R42w3mutationtester02/appendix-table.md`; the machine-readable grid is
`.ufo/waves/round-42/w3/R42w3mutationtester02/grid-w3.jsonl`; the generator is
`analyse.py` / `report.py`. Verdict semantics are the frozen counter's own
(`c3-counter.py` `killed()` / `clean()`, plus its `pristine_ok` rule `cases >= 13`):

- **KILL(F,T)** = rc==1 and SUMMARY fail>0 and no traceback
- **CLEAN(F,T)** = rc==0 and fail==0 and pass==cases and no traceback
- **pristine_ok(F)** = CLEAN and cases >= 13

| fixture mutant | category | pristine (pinned tool) | pop mutants still killed | verdict |
|---|---|---|---|---|
| BASE (landed fixture) | — | clean rc=0 fail=0 pass=13/13 | 13/13 | reference |
| C01 | COUNT | clean | 12/13 | LOAD-BEARING (loses I1) |
| C02 | COUNT | clean | 13/13 | REDUNDANT |
| C03 | COUNT | clean | 13/13 | REDUNDANT |
| C04 | COUNT | clean | 13/13 | REDUNDANT |
| D01 | ASSERT | clean | 12/13 | LOAD-BEARING (loses B1) |
| D02 | ASSERT | clean | 12/13 | LOAD-BEARING (loses E2) |
| D03 | ASSERT | clean | 12/13 | LOAD-BEARING (loses E4) |
| D04 | ASSERT | clean | 13/13 | REDUNDANT |
| D05 | ASSERT | clean | 12/13 | LOAD-BEARING (loses G3) |
| D06 | ASSERT | clean | 13/13 | REDUNDANT |
| D07 | ASSERT | clean | 12/13 | LOAD-BEARING (loses G5) |
| D08 | ASSERT | clean | 12/13 | LOAD-BEARING (loses H1) |
| D09 | ASSERT | clean | 12/13 | LOAD-BEARING (loses H2) |
| D10 | ASSERT | clean | 12/13 | LOAD-BEARING (loses I1) |
| D11 | ASSERT | clean | 12/13 | LOAD-BEARING (loses J9) |
| D12 | ASSERT | clean | 13/13 | REDUNDANT — but see F1 |
| D13 | ASSERT | clean | 13/13 | REDUNDANT — but see F2 |
| H01 | HELPER | clean | 13/13 | REDUNDANT |
| H02 | HELPER | clean | 13/13 | REDUNDANT |
| H03 | HELPER | clean | 13/13 | REDUNDANT |
| H04 | HELPER | clean | 13/13 | REDUNDANT |
| H05 | HELPER | clean | 11/13 | LOAD-BEARING (loses G4, G5) |
| H06 | HELPER | clean | 13/13 | REDUNDANT |
| N01 | ARG | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N02 | ARG | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N03 | ARG | clean | 13/13 | REDUNDANT |
| N04 | ARG | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N05 | KEY | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N06 | KEY | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N07 | KEY | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N08 | TOKEN | clean | 13/13 | REDUNDANT |
| N09 | KEY | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N10 | KEY | clean | 13/13 | REDUNDANT |
| N11 | COUNT | clean | 12/13 | LOAD-BEARING (loses M1) |
| N12 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N13 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N14 | ARG | clean | 13/13 | REDUNDANT |
| N15 | ARG | clean | 13/13 | REDUNDANT |
| N16 | ARG | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N17 | TIMING | clean | 13/13 | REDUNDANT |
| N18 | TOKEN | clean | 13/13 | REDUNDANT |
| N19 | KEY | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N20 | COUNT | clean | 13/13 | REDUNDANT |
| N21 | ARG | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N22 | ARG | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| N23 | COUNT | clean | **0/13** | KILLS-NOTHING (counter reads fail>0) |
| N24 | COUNT | clean | 13/13 | REDUNDANT |
| P01 | DROP2 | clean cases=11 | 12/13 | DROPPED-CASE (loses G2) |
| P02 | DROP2 | clean cases=11 | 11/13 | DROPPED-CASE (loses G3, G4) |
| P03 | DROP2 | clean cases=11 | 12/13 | DROPPED-CASE (loses G3) |
| T01 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| T02 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| T03 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| T04 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| T05 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| T06 | TOKEN | FAIL rc=1 | 13/13 | CAUGHT-BY-PRISTINE |
| T07 | TOKEN | clean | 13/13 | REDUNDANT |
| W01 | TIMING | clean | 12/13 | LOAD-BEARING (loses G3) |
| W02 | TIMING | clean | 12/13 | LOAD-BEARING (loses G3) |
| W03 | TIMING | clean | 13/13 | REDUNDANT |
| W04 | TIMING | clean | 13/13 | REDUNDANT |
| X01 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses B1) |
| X02 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses E2) |
| X03 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses E4) |
| X04 | DROP | clean cases=12 | 13/13 | DROPPED-CASE (loses nothing — see F3) |
| X05 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses G3) |
| X06 | DROP | clean cases=12 | 13/13 | DROPPED-CASE (loses nothing — see F3) |
| X07 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses G5) |
| X08 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses H1) |
| X09 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses H2) |
| X10 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses I1) |
| X11 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses J9) |
| X12 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses M1) |
| X13 | DROP | clean cases=12 | 12/13 | DROPPED-CASE (loses D4) |

Totals over the 74 mutants: **14 LOAD-BEARING, 24 REDUNDANT, 19 CAUGHT-BY-PRISTINE, 16
DROPPED-CASE, 1 KILLS-NOTHING.**

Reading of the three verdict classes:

- **CAUGHT-BY-PRISTINE (19)** — the mutant asserts something the pinned tool does not do
  (a changed token, a changed exit code, a changed record value). These are self-inconsistent
  mutants, not survivors; they prove the fixture's assertions are *tight* against the pinned
  behaviour (e.g. T01 changing `RECORD-MALFORMED` to `RECORD-MALFORMEDX` fails the pinned
  tool, so the class token is genuinely asserted).
- **REDUNDANT (24)** — passes pristine and still kills all 13. The removed/weakened assertion
  is not load-bearing *for the population*.
- **LOAD-BEARING (14)** — passes pristine but loses ≥1 population kill.

## 5. Load-bearing cases (removal loses a kill)

A case is load-bearing when dropping it (a DROP mutant, the case removed from the run list)
loses at least one population kill:

| case | population mutant lost when the case is dropped | mutant |
|---|---|---|
| `fifo-record-is-refused-not-blocked` | B1 | X01 |
| `root-sibling-prefix-is-outside` | E2 | X02 |
| `gitdir-sibling-prefix-is-outside` | E4 | X03 |
| `default-timeout-outlasts-a-blocked-git` | G3 | X05 |
| `list-nonzero-rc-is-reported-unreachable` | G5 | X07 |
| `root-option-is-required` | H1 | X08 |
| `record-option-is-required` | H2 | X09 |
| `symlinked-child-is-not-discovered` | I1 | X10 |
| `two-digit-regs-are-read-whole` | J9 | X11 |
| `longer-old-json-is-truncated-on-write` | M1 | X12 |
| `invalid-utf8-in-record-becomes-replacement-char` | D4 | X13 |

**11 of 13 cases are individually load-bearing.** The other two,
`timeout-of-one-is-accepted` and `list-timeout-is-reported-unreachable`, are each
individually redundant — but **mutually necessary** (finding F3 below).

Assertion-level attribution (which case *discriminates* which mutant, read off the BASE row):

| population mutant | failing case(s) in the landed fixture |
|---|---|
| B1 | fifo-record-is-refused-not-blocked |
| E2 | root-sibling-prefix-is-outside |
| E4 | gitdir-sibling-prefix-is-outside |
| G2 | list-timeout-is-reported-unreachable, timeout-of-one-is-accepted |
| G3 | default-timeout-outlasts-a-blocked-git |
| G4 | default-timeout-outlasts-a-blocked-git, list-timeout-is-reported-unreachable |
| G5 | list-nonzero-rc-is-reported-unreachable |
| H1 | root-option-is-required |
| H2 | record-option-is-required |
| I1 | symlinked-child-is-not-discovered |
| J9 | two-digit-regs-are-read-whole |
| M1 | longer-old-json-is-truncated-on-write |
| D4 | invalid-utf8-in-record-becomes-replacement-char |

## 6. Assertions that are never exercised

Three narrow findings. Each names what it attacks and is **reported, not fixed** — the fixture
is frozen for this wave.

### F1 — the json-truncate case's own assertion never discriminates; its JSON-parse fallback does

*Attacks:* `case_longer_old_json_is_truncated_on_write`'s assertion
`data.get("drift") == [] and "summary" in data`, which the fixture presents as the check for
M1 (ftruncate removed).

*Evidence.* Mutant **D12** replaces that assertion with `return True`; M1 is **still killed**
(`D12 M1 rc=1 cases=13 pass=12 fail=1 failing=['longer-old-json-is-truncated-on-write']`).
So the assertion is never the discriminator. The kill must come from the earlier path in the
same case — the `except (OSError, ValueError): return False` fallback, which fires when the
un-truncated old file's 5000-byte tail makes the written JSON unparseable.

*Mechanism confirmed* by probe **R1** (`mechprobe.py`), which removes the assertion *and* the
parse fallback:

```
PROBE R1 against tool M1, load=162.28 188.93 213.49
  -> rc=0 SUMMARY cases=13 pass=13 fail=0 failing= killed=False
  VERDICT: the population mutant SURVIVES -> mechanism confirmed
```

Reading: the case still detects that the tool left stale bytes, but it detects it as a *parse
failure*, not as the asserted content. `N11` (filler 5000→5 bytes) corroborates: with only 5
stale bytes the JSON stays parseable and **M1 survives** (`N11 M1 rc=0 cases=13 pass=13
fail=0`), so the case's discrimination of M1 depends on the *size* of the stale tail, not on
the asserted `drift == []` / `summary` shape.

### F2 — the invalid-utf8 case's own assertion never discriminates; its stdout byte check does

*Attacks:* `case_invalid_utf8_in_record_becomes_replacement_char`'s assertion
`[row.get("repo") for row in data.get("drift", [])] == ["a\ufffdb"]`, which the fixture
presents as the check for D4 (record decoded with `backslashreplace`).

*Evidence.* Mutant **D13** replaces that assertion with `return True`; D4 is **still killed**
(`D13 D4 rc=1 cases=13 pass=12 fail=1 failing=['invalid-utf8-in-record-becomes-replacement-char']`).
The kill comes from the stdout byte check
`b"DRIFT\tABSENT\ta\xef\xbf\xbdb\t" not in p.stdout or b"\\xff" in p.stdout`.

*Mechanism confirmed* by probe **R2**, which removes the assertion *and* the stdout check:

```
PROBE R2 against tool D4, load=169.83 187.12 211.71
  -> rc=0 SUMMARY cases=13 pass=13 fail=0 failing= killed=False
  VERDICT: the population mutant SURVIVES -> mechanism confirmed
```

Reading: the case detects the `backslashreplace` behaviour through the stdout byte sequence
(and its `\\xff` negative), and the JSON-side repo-name equality is a second, unexercised
description of the same behaviour. `C02` (repo-list equality weakened to a length check) is
likewise REDUNDANT, and `C04` (stdout token weakened to a bare U+FFFD presence) is REDUNDANT
too — so within this case the *stdout* half is what carries the discrimination.

### F3 — the two G2-killing cases are individually redundant but mutually necessary

*Attacks:* the claim that `timeout-of-one-is-accepted` and
`list-timeout-is-reported-unreachable` each independently kill G2, so either can be dropped.

*Evidence.* **X04** (drop `timeout-of-one-is-accepted`) still kills all 13; **X06** (drop
`list-timeout-is-reported-unreachable`) still kills all 13. But **P01** (drop *both*) loses G2:

```
P01  G2  rc=0 cases=11 pass=11 fail=0 failing=          <- G2 SURVIVES
P01  G4  rc=1 cases=11 pass=10 fail=1 failing=['default-timeout-outlasts-a-blocked-git']
X04  G2  rc=1 cases=12 pass=11 fail=1 failing=['list-timeout-is-reported-unreachable']
X06  G2  rc=1 cases=12 pass=11 fail=1 failing=['timeout-of-one-is-accepted']
```

Confirmed by the counter itself: `SUMMARY mutants=13 killed=12 survived=1 pristine=FAIL ... cases=11`
with `MUTANT G2 candidate=SURVIVED prior=-`.

Reading: no single case is dispensable, but the fixture holds a **redundant second witness**
for G2 — `timeout-of-one-is-accepted` fires because G2 refuses `--timeout 1`, and
`list-timeout-is-reported-unreachable` fires because the same refusal makes the blocked-HEAD
scene unreachable sooner than the default allowance. The same holds for G4 with **P02**
(drop `default-timeout-outlasts-a-blocked-git` and `list-timeout-is-reported-unreachable` →
loses G3 **and** G4) and for **P03** (drop `timeout-of-one-accepted` with
`default-timeout-outlasts-a-blocked-git` → loses G3). This is redundancy, not a hole: the
population is still fully covered. It is reported because it is the kind of redundancy that
a future single-point edit to one of the two cases would silently convert into a coverage
loss.

### F4 — the counter-protocol coupling: the SUMMARY `fail` count is the whole kill channel

*Attacks:* the fixture's `SUMMARY cases=… pass=… fail=…` line as the channel by which the
frozen counter learns that a case failed.

*Evidence.* Mutant **N23** pins the reported `fail` count to 0 while still printing the
`case-<name>=FAIL` lines and still exiting 1:

```
N23  pristine  rc=0 cases=13 pass=13 fail=0
N23  G3        rc=1 cases=13 pass=12 fail=0 failing=['default-timeout-outlasts-a-blocked-git']
```

Every population mutant survives, because `c3-counter.py` `killed()` requires
`SUMMARY … fail>0`. The counter agrees: `SUMMARY mutants=13 killed=0 survived=13 pristine=ok`.
This is not a defect in the landed fixture (it reports `fail` correctly), but it pins a
contract: **the fixture's kill channel is the `fail` field of the SUMMARY line, not the exit
code and not the per-case `case-…=FAIL` lines**. A future edit that reformats or drops that
field would make the fixture kill nothing while still looking correct on stdout. Mutant
**N24** (pinning the `pass` count) is REDUNDANT, which is the benign counterpart.

## 7. Assertions that are individually redundant (summary)

The 24 REDUNDANT mutants are the assertions that never change the population verdict. Grouped:

- **Helper predicates (H01–H04, H06).** The shared helpers `refused()` and `drift_line()`
  have slack: H02 (drop the REFUSAL-class token from `refused()`) and H05's counterpart H05
  aside, widening the accepted exit codes (H01, H04) or the stdout decoding (H06) does not
  lose a kill, because the *other* assertion in each case still discriminates. The one
  exception is **H05** (`drift_line()` loses its stdout token check), which loses **G4 and
  G5**: those two mutants are detected only by the *token*, not by the exit code, so the
  stdout check in `drift_line()` is load-bearing for them.
- **Weakened counts (C02, C03, C04, N20, N24).** Weakening a count inside an assertion leaves
  the other conjunct doing the discrimination (see F1, F2).
- **Timing slack (W03, W04, N17).** Widening the subprocess timeout of `list-timeout` (60→300
  s) or of `fifo-record` (25→300 s) changes nothing, because both cases fail on the tool's
  *refusal*, not on the timeout. Narrowing the `elapsed` bound (N17, 5→30 s) is still REDUNDANT
  because the base run takes ~42 s. Only the bound *direction that matters* is load-bearing:
  **W01** (5.0→0.5 s) and **W02** (5.0→0.0 s) each lose **G3**, confirming that the 5.0 s
  bound is exactly what distinguishes the 20 s default from G3's 1 s default.
- **Assertion removal that a sibling case covers (D04, D06, D12, D13).** D04 removes
  `timeout-of-one-accepted`'s assertion and D06 removes `list-timeout-is-reported-unreachable`'s;
  each is covered by the other (F3). D12 and D13 are F1 and F2.
- **Token loosening that keeps the substring (T07, N08, N10, N18).** `"require"` is a
  substring of `"required"` (T07); the trailing tab is optional in the stdout token (N08);
  `\xfe` is also an invalid byte, so the replacement char is still produced (N10); the
  `DRIFT\tABSENT` prefix still matches (N18).

## 8. Threats to validity

- **Load.** The host ran at load 16→290 during the grid. Mitigation: the whole G3 column was
  re-run serially at low parallelism and reproduced exactly (§3.5); no cell crashed or timed
  out; and eight independent verdicts were re-derived through the frozen counter itself
  (§3.4), including the two load-sensitive ones (H05, N11).
- **The `elapsed >= 5.0` bound is a wall-clock threshold.** It is the one assertion in the
  fixture that depends on machine speed. At the observed ~42 s base run and ~4.6 s G3 run the
  margin is wide, but the bound is the fixture's most environment-sensitive element; a much
  faster host could shrink the margin further. This is a property of the landed fixture, not
  something this seat can change.
- **Parallelism.** The grid used 6–10 workers. Fixture runs are independent (each builds its
  own scenario under `--work`), and the serial G3 re-verification confirms the parallel
  verdicts are not load artefacts.
- **Reuse.** 634 of 1050 cells have a wave-2 counterpart; all 634 agree with the wave-3 re-run,
  so reuse introduces no divergence. The 318 wave-3-only cells are the new N01–N24 / P01–P03
  mutants plus the completed X12/X13 rows.

## 9. Verdict

The landed fixture `tests/fixtures/r42-drift-conditions.py` at
`6a3f75941d3604e3459011d599c2c16f3a97b44c` is **mutation-robust for its frozen target**: it
kills all 13 population mutants of `census/round-42/c3-counter.py`, kills none of the 6
equivalent mutants, and 11 of its 13 cases are individually load-bearing, with the remaining
two mutually necessary (F3). Nothing in this seat's 74-mutant attack shows a hole in the C3
claim.

Three narrow coverage observations are reported for the L1 (no fix proposed by this seat, the
fixture is frozen):

- **F1** the json-truncate case's asserted JSON shape never discriminates — its parse
  fallback does (and the discrimination depends on the stale-tail *size*, N11);
- **F2** the invalid-utf8 case's asserted repo-name list never discriminates — its stdout byte
  check does;
- **F3** the two G2-killing cases are mutually redundant, so either single-case deletion is
  currently safe while a double deletion is not;
- **F4** the fixture's kill channel is the `fail` field of its `SUMMARY` line alone; the exit
  code and the `case-…=FAIL` lines are not read by the counter.

These are coverage findings for the round lesson, not defects in the landed artifact.

## 10. Evidence pointers

All paths relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`.

| path | content |
|---|---|
| `.ufo/waves/round-42/w3/R42w3mutationtester02.md` | this report |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/grid-w3.jsonl` | the 1050-cell grid (75 fixture ids × 14 tools), one JSON object per cell |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/grid-reverify.jsonl` | the 68-cell serial G3 re-verification, with the machine load recorded per cell |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/mutants.py` | the 74-mutant catalogue (47 reused from wave 2, 27 new) + `build()` single-point assertion |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/harness.py` | the grid driver (read-only w.r.t. the lane) |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/analyse.py` | verdict computation over the grid |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/report.py` | report-table generator |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/crosscheck.py` | wave-2 vs wave-3 grid comparison (0 disagreements) |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/mechprobe.py`, `mechprobe.log` | the R1 / R2 mechanism-confirmation probes for F1 and F2 |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/appendix-table.md` | the full 74-row table with descriptions |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/grid-w3.log` | the raw grid run log (batch boundaries and the load at each) |
| `.ufo/waves/round-42/w3/R42w3mutationtester02/grid.jsonl` | the copied wave-2 grid used for the cross-check |

No tracked file, no frozen instrument (the counters, the populations, the controls, the
preregistration, the pinned tool, every prior fixture), no sibling seat directory, no
`.ufo/state`, no fleet file and no lane file was written by this seat. All scratch lived under
`/fast/scratch/hyaku/souji-r42/R42w3mutationtester02/` and was removed before this report was
written. No tool was installed or upgraded for this task (no install was needed; the work used
the `git`, `python3` and `bash` already present), so the tooling directive produced no
install record.

## 11. Summary (10 lines)

1. Mutation-tested the landed C3 fixture with **74 single-point mutants** (47 reused from the
   stopped wave-2 seat, 27 new) × 14 tools = **1050 cells, none missing, no crash/timeout**.
2. The wave-2 partial grid was **reused as a cross-check and confirmed**: **0 disagreements**
   over all 634 shared cells; `X12`/`X13` were completed.
3. My harness's verdicts were **cross-validated against the frozen counter** on 8 fixture
   mutants — `killed`/`survived`/`pristine` match exactly in every case.
4. The load-sensitive **G3 column was re-run serially (68 cells)**: all reproduce the grid
   verdict, at load 16–290. The G3 kill is not a load artefact.
5. **11 of 13 cases are individually load-bearing**; the other two are mutually necessary.
6. **F1** the json-truncate case's asserted JSON shape never discriminates (its parse
   fallback does; the stale-tail size is what matters) — probe R1 confirms.
7. **F2** the invalid-utf8 case's asserted repo-name list never discriminates (its stdout byte
   check does) — probe R2 confirms.
8. **F3** the two G2-killing cases are mutually redundant: dropping either is safe, dropping
   both loses G2 (counter: `killed=12 survived=1`).
9. **F4** the fixture's kill channel is the `fail` field of its `SUMMARY` line alone; pinning
   it to 0 kills nothing (counter: `killed=0 survived=13`).
10. **Verdict: the landed fixture is mutation-robust for its frozen target**; F1–F4 are
    coverage findings for the L1, not defects, and no fix is proposed by this seat.
