# R40connector09 — connector seat, round 40 wave 1

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
Target: `census/round-40/preregistration.txt` — **C3 (coverage)**.
Base revision (frozen): `0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip).

Scope: read-only findings. **No production file was written, no frozen claim edited, no
commit/push, no git/jj/index mutation.** The only lane file this seat writes is this report.
All scratch lived under `/fast/scratch/hyaku/souji-r40/R40connector09/` and was removed before
yield. Tool installs/upgrades: **none**; pacman untouched (operator directive: pacman paused).

---

## 0. Named distinct edge case (item 9)

**The base-arm identity conflict: C3's clause "all mutants survive the r39 base fixture" is
unsatisfiable against the r39 fixture as base, because the r39 fixture *kills* every mutant in the
r39 baseline battery (M11–M14). The only base fixture that leaves the r39 baseline battery alive
is the r38 fixture — the one r39 itself used. So "the r39 base fixture" cannot mean
`tests/fixtures/r39-drift-record-rules.py` while the battery contains M11–M14, and the C3 clause
therefore silently forces the r40 battery to *exclude* the r39 baseline mutants, which in turn
means the r40 fixture is free to regress r39's coverage without violating C3.**

Measured, both halves:

```
### BASE-READING MATRIX (base_killed counts base-fixture kills of the battery)
  BASELINE M11  base(r38)=alive   base(r39)=KILLED
  BASELINE M12  base(r38)=alive   base(r39)=KILLED
  BASELINE M13  base(r38)=alive   base(r39)=KILLED
  BASELINE M14  base(r38)=alive   base(r39)=KILLED
  NEW      U1-decode-strict base(r38)=alive  base(r39)=alive
  NEW      U2-decode-ignore base(r38)=alive  base(r39)=alive
  NEW      U3-decode-latin1 base(r38)=alive  base(r39)=alive
  NEW      S1-skip-invert  base(r38)=alive  base(r39)=alive
  NEW      T1-total-first-wins base(r38)=alive base(r39)=alive

### RETENTION: does the r40 candidate fixture still kill the r39 BASELINE battery?
  r40 candidate (minimal,  C3-green)  kills 1/4 r39 baseline mutants
  r40 candidate (superset, C3-green)  kills 4/4 r39 baseline mutants
```

Distinctness from the other C3 seats in this wave (all in `.ufo/waves/round-40/w1/`):

| sibling | edge it took | why item 9 differs |
|---|---|---|
| `R40connector21` | kill-gate misattribution — the `crash` veto reads the *fixture's* stdout, so a tool-side traceback is scored alive | item 9 is **not** about the crash veto at all; item 9 is about **which fixture may occupy the base arm** and what the C3 clause therefore permits |
| `R40reviewer54` | the same scoring-instrument attack (`score()` misreads a reprinted traceback) | same — item 9 is upstream of the scoring rule |
| `R40connector45` | the Reading A / Reading B **ambiguity** of the base clause | item 45 argues the wording is ambiguous and adopts Reading A; **item 9 measures the consequence**: under either reading the base-arm identity is forced, and item 9 additionally shows the r39 fixture kills 4/4 of the baseline battery (the number that makes the conflict concrete) |
| `R40revenger36`, `R40executor39`, `R40executor51` | duplicate/multiple TOTAL multiplicity | item 9 is about the *fixture-role* conflict, not TOTAL semantics |
| `R40revenger48`, `R40revenger60` | decoder replacement of invalid UTF-8; invalid-byte fixture I/O | item 9's byte-level findings are corroborating measurements, not the named edge |
| `R40connector33` | the pristine tool silently corrupts on invalid UTF-8 / accepts duplicate TOTAL | item 9's F3 confirms the same tool behaviour from a different direction (via the fixture's *contract*, not via the tool's bytes) |

---

## 1. Verdict

**A concrete falsifier of the frozen C3 predicate is established, and it is a *battery/contract*
defect rather than a coverage defect.** Three findings, all executed against committed r39
artifacts:

**F1 (falsifier — high severity).** C3 requires *"all mutants survive the r39 base fixture"* and
kills if *"any base mutant is killed"*. But the r39 fixture **kills all four** of the r39 baseline
mutants (M11 trailing-space, M12 CRLF, M13 outside-root, M14 indented-comment) — that is its
entire job. Measured: `M11..M14` against `tests/fixtures/r39-drift-record-rules.py` →
`KILLED rc=1 fails=1 crash=False` each; against `tests/fixtures/r38-drift-record.py` → `alive
rc=0 fails=0` each. So a battery that contains M11–M14 and a base fixture that is the r39 fixture
yields `base_killed=4`, which trips C3's own kill condition. End-to-end with a counter prototype
that mirrors the committed counter (importing its `score()` unchanged):

```
MUTANT M11 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT M12 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT M13 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT M14 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
... (8 new-branch mutants all base_killed=no)
SUMMARY mutants=12 killed=11 survived=1 pristine=ok base_killed=4 cases=13
counter exit=1
```

The r40 counter therefore has exactly **one** base-fixture identity that keeps the r39 baseline
battery alive — the **r38** fixture — and that is the fixture r39 itself already used as base.
C3's phrase "the r39 base fixture" is therefore *not* the r39 fixture under any reading that
keeps M11–M14 in the battery.

**F2 (falsifier — high severity, and the one with teeth).** Because the base clause forces the
r39 baseline mutants out of the r40 battery, **C3 as frozen contains no clause that requires the
r40 fixture to retain r39's coverage at all.** I built a fixture that satisfies every stated C3
condition — pristine passes, all eight new-branch mutants killed, `base_killed=0` — and it kills
only **1 of the 4** r39 baseline mutants:

```
SUMMARY mutants=8 killed=8 survived=0 pristine=ok base_killed=0 cases=10
counter exit=0                       <-- C3 GREEN

  M11    r40-CANDIDATE=KILLED   |  r39-BASE=KILLED
  M12    r40-CANDIDATE=ALIVE    |  r39-BASE=KILLED     <-- regression, invisible to C3
  M13    r40-CANDIDATE=ALIVE    |  r39-BASE=KILLED     <-- regression, invisible to C3
  M14    r40-CANDIDATE=ALIVE    |  r39-BASE=KILLED     <-- regression, invisible to C3
```

Adding r39's five regression cases (`trailing-space`, `crlf`, `outside-root`,
`indented-comment`, `comments-total-only`) restores 4/4 with the C3 verdict unchanged. So the
C3-green state space contains both a coverage-preserving and a coverage-regressing fixture, and
**the frozen predicate cannot distinguish them**. The coverage axis is therefore not merely
unmeasured — it is measured by an instrument that cannot see the regression it exists to prevent.

**F3 (falsifier — medium severity, tool-side contract).** The tool's own docstring promises
`RECORD-MALFORMED` for *"a TOTAL row that disagrees"*
(`tools/souji-worktree-drift.py:47-48`), but with two TOTAL rows only the **last** is validated —
line 165 unconditionally overwrites `total`, so a *disagreeing* first TOTAL row is silently
discarded and the record is **accepted**:

```
### CASE: TOTAL repos=9 (disagrees with 2 REPO rows), then TOTAL repos=2 (agrees)
SUMMARY record=... record_repos=2 record_regs=2 ... drift_rows=0 unreachable=0
rc=0
```

A r40 fixture that asserts the *documented* contract on this branch fails the pristine
(`case-dup-total-first-disagrees=FAIL rc=0 want=2 missing=['RECORD-MALFORMED']`), and C3 kills if
*"pristine fails"*. So the TOTAL branch of C3 has **no contract-stable fixture**: it can assert
the tool's actual behaviour (last-wins) or its documented behaviour (refuse any disagreeing
TOTAL), and only the first keeps the pristine green. The r40 counter must therefore *codify* the
undocumented last-wins behaviour as if it were specified — a coverage claim that pins an
unspecified behaviour rather than measuring a specified one.

**None of F1–F3 falsifies the coverage claim's substance** — the three branches are genuinely
coverable, and §4 shows a fixture that satisfies C3 with all eight new-branch mutants killed.
They falsify the claim **as an instrument-measurable, non-regressing predicate**, and F1/F2 are
one-line repairs. Per the frozen instruction *"a missed predicate is reported honestly"*, this is
reported as a falsifier of measurability and of regression-detection, not of coverage substance.

---

## 2. Evidence pointers (committed r39 artifacts)

| what | where |
|---|---|
| Frozen C3 predicate + kill conditions | `census/round-40/preregistration.txt:10-12` |
| Base revision named by the prereg | `0242085909fb6a4ee041c5443d76316ac6d59d4b` |
| `score()` — the inherited kill rule | `census/round-39/c3-counter.py:101-102` (`crash` at `:101`, `killed` at `:102`) |
| `base_killed` accumulation (base fixture kills of the battery) | `census/round-39/c3-counter.py:178-183` (`:183` sums it into `base_n`) |
| r39 battery M11–M14 + anchors | `census/round-39/c3-counter.py:50-58` |
| r39 counter exit contract (`base_n == 0` required) | `census/round-39/c3-counter.py:186` |
| r39 candidate fixture (`r39-drift-record-rules.py`, 7 cases) | `tests/fixtures/r39-drift-record-rules.py:83-114` |
| r39 base fixture (`r38-drift-record.py`, 10 cases) | `tests/fixtures/r38-drift-record.py:96-125` |
| fixture detail line that reprints the tool's stdout+stderr | `tests/fixtures/r39-drift-record-rules.py:79-80`; `tests/fixtures/r38-drift-record.py:92-93` |
| `parse_record` — UTF-8 `"replace"` decode | `tools/souji-worktree-drift.py:147` |
| TOTAL match: unconditional overwrite (last wins) | `tools/souji-worktree-drift.py:162-165` |
| TOTAL sums validated only for the surviving total | `tools/souji-worktree-drift.py:169-178` |
| docstring promise "a TOTAL row that disagrees" | `tools/souji-worktree-drift.py:46-48` |
| `--skip-unrecorded` guard (the only one) | `tools/souji-worktree-drift.py:370` |
| `--skip-unrecorded` flag definition | `tools/souji-worktree-drift.py:438` |
| r39 committed C3 receipt (M11–M14 killed, base_killed=0) | `census/round-39/records/c3-after.txt:3-6` (measured at rev `2f6e981`; `tool_sha=e48ed08e6728`, `fixture_sha=567c37a679f5` — the same hashes §3.1 reproduces at the frozen base `0242085`) |

---

## 3. Commands actually run, and their outputs

### 3.1 Committed baseline reproduced (the r39 counter at the frozen base revision)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B census/round-39/c3-counter.py --root . \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --scratch /fast/scratch/hyaku/souji-r40/R40connector09/scratch-r39
```
```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
```
This reproduces the committed r39 receipt **byte-identically** — verified by diffing the
`MUTANT`/`SUMMARY` lines against `census/round-39/records/c3-after.txt` (no differences) — and
confirms the lane's instrument works at the frozen base. **Note the `base_killed=0` here is
against the r38 fixture** — the identity conflict of F1.

### 3.2 Byte identity of the fixtures at the base revision (no drift)

```
git show 0242085...:tests/fixtures/r39-drift-record-rules.py | sha256sum
  567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d
sha256sum tests/fixtures/r39-drift-record-rules.py
  567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d
git show 0242085...:tests/fixtures/r38-drift-record.py | sha256sum
  ac0be0e7a49e683cd324ffa485fecb15d11c5636fde55f3244d9776020b021d6
sha256sum tests/fixtures/r38-drift-record.py
  ac0be0e7a49e683cd324ffa485fecb15d11c5636fde55f3244d9776020b021d6
```

### 3.3 F1 — the r39 base fixture kills the whole r39 baseline battery

Scored with the **committed** `score()`, imported unchanged from
`census/round-39/c3-counter.py` (no re-implementation):

```
### Does the r39 fixture (the only sensible r40 BASE fixture) kill the r39 BASELINE battery M11-M14?
  M11  r39-fixture(base for r40)=KILLED  rc=1 fails=1 crash=False | r38-fixture=alive   rc=0 fails=0 crash=False
  M12  r39-fixture(base for r40)=KILLED  rc=1 fails=1 crash=False | r38-fixture=alive   rc=0 fails=0 crash=False
  M13  r39-fixture(base for r40)=KILLED  rc=1 fails=1 crash=False | r38-fixture=alive   rc=0 fails=0 crash=False
  M14  r39-fixture(base for r40)=KILLED  rc=1 fails=1 crash=False | r38-fixture=alive   rc=0 fails=0 crash=False
```

End-to-end, with the baseline battery carried forward (§1, F1):

```
### F1 COUNTERFACTUAL: base fixture = r39 fixture, battery includes r39 baseline M11-M14
MUTANT M11 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT M12 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT M13 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT M14 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
MUTANT U1-decode-strict    killed=yes base_killed=no  rc=1 fails=3 crash=False base:rc=0 fails=0 crash=False
MUTANT U2-decode-ignore    killed=yes base_killed=no  rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
MUTANT U3-decode-latin1    killed=yes base_killed=no  rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT U4-no-decode        killed=no  base_killed=no  rc=1 fails=13 crash=True base:rc=1 fails=7 crash=True
MUTANT S1-skip-invert      killed=yes base_killed=no  rc=1 fails=6 crash=False base:rc=0 fails=0 crash=False
MUTANT S2-skip-always      killed=yes base_killed=no  rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT T1-total-first-wins killed=yes base_killed=no  rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
MUTANT T2-total-refuse-dup killed=yes base_killed=no  rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=12 killed=11 survived=1 pristine=ok base_killed=4 cases=13
counter exit=1
```

`base_killed=4` — C3's kill condition *"any base mutant is killed"* fires on the baseline
mutants themselves.

### 3.4 F2 — a C3-GREEN fixture that regresses r39 coverage 4/4 → 1/4

```
### the C3 verdict on the minimal candidate fixture:
SUMMARY mutants=8 killed=8 survived=0 pristine=ok base_killed=0 cases=10
counter exit=0                       <-- C3 GREEN

### RETENTION: does the r40 candidate fixture still kill the r39 BASELINE battery?
  r40 candidate (minimal,  C3-green)  kills 1/4 r39 baseline mutants
  r40 candidate (superset, C3-green)  kills 4/4 r39 baseline mutants
```
Per-mutant detail for the minimal (C3-green) candidate:
```
  M11    r40-CANDIDATE=KILLED  rc=1 fails=1 crash=False  |  r39-BASE=KILLED  rc=1 fails=1 crash=False
  M12    r40-CANDIDATE=ALIVE   rc=0 fails=0 crash=False  |  r39-BASE=KILLED  rc=1 fails=1 crash=False
  M13    r40-CANDIDATE=ALIVE   rc=0 fails=0 crash=False  |  r39-BASE=KILLED  rc=1 fails=1 crash=False
  M14    r40-CANDIDATE=ALIVE   rc=0 fails=0 crash=False  |  r39-BASE=KILLED  rc=1 fails=1 crash=False
```

### 3.5 F3 — the TOTAL branch has no contract-stable fixture

Tool behaviour on a record whose **first** TOTAL row disagrees:
```
### docstring promise (tool-base.py:46-48):
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
                         that does not match the schema, a duplicated name, or
                         a TOTAL row that disagrees

### CASE: two TOTAL rows, FIRST disagrees (repos=9) then SECOND agrees (repos=2), 2 REPO rows
REPO^Ialpha^Iregs=1^Iprunable=0$
REPO^Ibeta^Iregs=1^Iprunable=0$
TOTAL^Irepos=9^Iregs=9^Iprunable=9$
TOTAL^Irepos=2^Iregs=2^Iprunable=0$
--- tool output ---
SUMMARY record=... record_repos=2 record_regs=2 record_prunable=0 live_repos=2 ... drift_rows=0 unreachable=0
rc=0
```
A fixture asserting the **documented** contract on this branch fails the pristine:
```
=== VARIANT A (assert invalid UTF-8 is REFUSED) on PRISTINE ===   # same shape, invalid-UTF-8 branch
    case-bad-utf8-name=FAIL rc=1 want=2 missing=['RECORD-MALFORMED'] out='DRIFT\tABSENT\tal?pha ...'

=== documented-contract assertion on the TOTAL branch ===
    case-dup-total-first-disagrees=FAIL rc=0 want=2 missing=['RECORD-MALFORMED'] out='SUMMARY record=... record_repos=2 record_regs=2'
    SUMMARY cases=10 pass=9 fail=1
```

### 3.6 Corroborating: the invalid-UTF-8 branch's byte placement decides the contract

Two placements, same raw byte `0xff`, **opposite** observable contracts:

| placement | observed | contract implied |
|---|---|---|
| numeric field (`regs=1\xff`) | `REFUSAL RECORD-MALFORMED` (rc 2) — the byte is not `\d` | schema refusal |
| name field (`al\xffpha`) | **accepted**, `DRIFT ABSENT al?pha` (rc 1) — `errors="replace"` substituted U+FFFD, which still matches `(?P<name>[^\t]+)` | silent corruption |

So an r40 fixture's "invalid UTF-8 record bytes" case is only meaningful if it pins the
**placement**, and the name-field placement is a *silent-corruption* contract, not a refusal —
the pristine never refuses invalid UTF-8. Measured on the committed tool:
```
### CASE B: invalid UTF-8 (raw 0xff) in the REPO name field
DRIFT	ABSENT	al?pha	recorded regs=1
DRIFT	UNRECORDED	alpha	live regs=1 prunable=0
...
SUMMARY ... record_repos=1 ... drift_rows=4 unreachable=0
rc=1
```
This also means the branch is only **byte-level**-discriminating: asserting the literal U+FFFD
(`` "al\ufffdpha" ``) is what separates `errors="replace"` from `errors="latin-1"`. Measured:
```
=== VARIANT B (assert literal U+FFFD) vs latin-1 mutant ===
    case-bad-utf8-name=FAIL rc=1 want=1 missing=['al?pha'] out='DRIFT\tABSENT\tal?pha ...'
```
i.e. without the literal assertion the latin-1 mutant is **ALIVE** (`rc=0 fails=0`) — the
decoding policy is then unpinned.

### 3.7 Corroborating: the `--skip-unrecorded` branch needs a fleet the r39 fixtures do not have

`grep -c "skip.unrecorded"` on both committed base fixtures → **0** and **0**. The branch can
only be observed with a repository present under `--root` that the record does not name; adding
one flips the exit status of every other case that expects rc 0 (the new repo is reported
`UNRECORDED` → rc 1). This is a **fleet-coupling trap** in fixture construction, measured:
```
case-good=FAIL rc=1 want=0 ... out='DRIFT\tUNRECORDED\tgamma ...'     # without --skip-unrecorded
case-crlf=FAIL rc=1 out='DRIFT\tUNRECORDED\tgamma ...'                 # parity case broken by the extra repo
```
and it is fixed by adding `--skip-unrecorded` to the parity cases — i.e. the r40 fixture must
carry r39's parity cases **and** re-flag them, not merely add new ones.

---

## 4. Bounded measurement plan (what the r40 C3 counter must do to be honest)

The counter must **not** reuse the r39 counter's single-base-arm shape. Concretely, and using only
the committed `score()`:

1. **Split the battery into two named arms and score them against two different base fixtures.**
   - Arm A — *new-branch mutants* (TOTAL / `--skip-unrecorded` / invalid-UTF-8): base =
     `tests/fixtures/r39-drift-record-rules.py` (the r39 fixture). All 8 measured new-branch
     mutants are `alive` against it, so `base_killed=0` on this arm holds — **but the arm must be
     labelled as "base = r39 fixture" in the receipt**, and it must **not** contain M11–M14.
   - Arm B — *r39 baseline mutants* M11–M14: base = `tests/fixtures/r38-drift-record.py` (the r38
     fixture), which leaves all four `alive` (`rc=0 fails=0` each, measured). This is the only
     base identity that keeps the baseline battery alive.
2. **Add the retention clause C3 lacks** (this is F2's repair): the r40 candidate fixture must
   kill **4/4** of M11–M14. Measured: the superset fixture does (4/4); the minimal one does not
   (1/4) while still reading C3-green. The clause to add is *"the candidate fixture kills every
   r39 baseline mutant"*, and it must be checked with the r39 fixture's own `score()` semantics.
3. **Repair the crash veto before it can fire on the invalid-UTF-8 arm** (corroborating, and
   already claimed by `R40connector21` / `R40reviewer54`): the committed rule is
   `crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)` where `proc` is
   the **fixture** process, and the fixture reprints the tool's stdout+stderr in its case-detail
   line. Measured consequence on the natural invalid-UTF-8 mutant `decode("utf-8","strict")`:
   ```
   RUN 1 (house-style detail echo):  MUTANT U1-decode-strict killed=no  rc=1 fails=3 crash=True
   RUN 2 (same cases, detail scrubs the tool traceback):
                                     MUTANT U1-decode-strict killed=yes rc=1 fails=3 crash=False
   ```
   The repair is one line in the fixture (redact the tool's traceback from the reprinted detail)
   or in the counter (scan the *fixture's own* stderr for a traceback, not its stdout). Until that
   is done, the invalid-UTF-8 arm of C3 is **not measurable** — the counter reports `survived=1`
   for a mutant the fixture demonstrably detected.
4. **Pin the byte-level contract for the invalid-UTF-8 arm**: assert the literal U+FFFD (not
   merely "ABSENT"), otherwise `errors="latin-1"` survives (`rc=0 fails=0`, measured).
5. **Pin the TOTAL arm to the tool's *actual* behaviour (last TOTAL wins) and say so in the
   receipt**, because the documented contract ("a TOTAL row that disagrees" → RECORD-MALFORMED)
   fails the pristine (measured). A coverage receipt that asserts the documented contract must
   carry a corresponding tool fix; one that asserts last-wins must label the behaviour as
   unspecified-but-observed, not as specified.
6. **Re-flag the fleet-coupled parity cases.** Every r39 parity case that expects rc 0 must carry
   `--skip-unrecorded` once an unrecorded repo exists in the fleet, or the fleet must be split
   (measured: `case-crlf=FAIL rc=1` otherwise).

### The C3-satisfying shape, end to end (measured)

A fixture that (a) passes the pristine, (b) kills all 8 new-branch mutants, (c) keeps
`base_killed=0` on the new-branch arm against the r39 fixture, (d) kills 4/4 of the r39 baseline
mutants, and (e) redacts the tool's traceback from its reprinted detail:

```
pristine rc=0 cases=13 pristine_ok=True
MUTANT U1-decode-strict     killed=yes base_killed=no rc=1 fails=3  crash=False base:rc=0 fails=0 crash=False
MUTANT U2-decode-ignore     killed=yes base_killed=no rc=1 fails=2  crash=False base:rc=0 fails=0 crash=False
MUTANT U3-decode-latin1     killed=yes base_killed=no rc=1 fails=1  crash=False base:rc=0 fails=0 crash=False
MUTANT U4-no-decode         killed=yes base_killed=no rc=1 fails=13 crash=False base:rc=1 fails=7 crash=True
MUTANT S1-skip-invert       killed=yes base_killed=no rc=1 fails=6  crash=False base:rc=0 fails=0 crash=False
MUTANT S2-skip-always       killed=yes base_killed=no rc=1 fails=1  crash=False base:rc=0 fails=0 crash=False
MUTANT T1-total-first-wins  killed=yes base_killed=no rc=1 fails=2  crash=False base:rc=0 fails=0 crash=False
MUTANT T2-total-refuse-dup  killed=yes base_killed=no rc=1 fails=2  crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=8 killed=8 survived=0 pristine=ok base_killed=0 cases=13
counter exit=0
```
plus, separately, the retention arm:
```
  r40 candidate (superset)  kills 4/4 r39 baseline mutants
```

---

## 5. What this does to the C3 predicate

- **Falsified as written:** the clause *"all mutants survive the r39 base fixture"* cannot hold
  for a battery containing the r39 baseline mutants, because the r39 fixture kills all four
  (measured, `base_killed=4`). The clause therefore silently excludes the baseline mutants, and
  with them the only check that would detect a coverage regression.
- **Falsified as a regression gate:** C3 as frozen is green for a fixture that regresses r39's
  record-rule coverage from 4/4 to 1/4 (measured).
- **Unstable as a TOTAL contract:** the documented contract fails the pristine (measured), so the
  branch can only be covered by pinning an unspecified behaviour.
- **Not falsified in substance:** all three branches are genuinely coverable; §4 gives a fixture
  and counter shape that satisfies every stated condition *and* detects the regression.
- **Frozen claims untouched.** Nothing in `census/round-40/preregistration.txt` was modified.

---

## 6. Second-order effects across the other axes

- **Coverage (C3) — harmed by the current shape, improvable.** The base-arm identity conflict and
  the absent retention clause mean C3's green state includes coverage regressions. Splitting the
  battery into two arms and adding the retention clause improves this axis without touching the
  frozen text.
- **Calibration (C1) — unaffected, but note the shared instrument.** The same
  `census/round-39/c3-counter.py` module supplies `score()`, and the crash-veto defect inside it
  is a *shared* instrument flaw: any r40 counter that inherits the module inherits the veto. The
  fix belongs in the counter/fixture, not in the frozen claim.
- **Operability (C2) — a mild coupling.** The `parse_record` TOTAL handling that C3 must pin
  (last-wins) is the same code whose docstring the C2 analyzer reads. If r40 changes the TOTAL
  branch to enforce the documented contract (refuse any disagreeing TOTAL), the C2 class/trigger
  mapping changes with it — the two axes are not independent on that branch. Fixing F3's contract
  ambiguity therefore has to be sequenced against C2, not treated as a C3-local choice.

---

## 7. Scratch and hygiene

- Scratch root: `/fast/scratch/hyaku/souji-r40/R40connector09/` — probe fixtures, a counter
  prototype, the extracted tool bytes, and the mutant battery. Removed before yield.
- The lane repo was **not** mutated: `git status --porcelain` in the lane shows only the
  pre-existing untracked `census/round-40/`; `.ufo/waves/` is git-ignored
  (`.gitignore:1`), so this report is untracked by design.
- Git fixtures used `mktemp`-style scratch dirs under the scratch root; each `git init` was
  followed by `git -C <repo> rev-parse --show-toplevel` asserted to equal the repo's realpath
  before any commit. No commit was made in the lane.
- Tool installs: **none**. pacman untouched.
