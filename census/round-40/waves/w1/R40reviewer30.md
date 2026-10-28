# R40reviewer30 — C3 coverage claim attack

- Seat: `R40reviewer30` (role reviewer; leaf member — no subagent dispatch)
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt` (C3 at lines 10–11)
- Base revision under test: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip, per preregistration line 1)
- Tool installs/upgrades: **none**. `pacman` untouched (paused by operator directive). Python 3.14.8, git 2.56.0 — both pre-existing.
- Git/jj/index mutation: **none**. Lane `HEAD` = `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`, unchanged. `git status --short` = `?? census/round-40/` (pre-existing untracked path, left untouched). Lane `tools/souji-worktree-drift.py` sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` — byte-identical to `git show 0242085909…:tools/souji-worktree-drift.py`.
- Only writes: this report + scratch under `/fast/scratch/hyaku/souji-r40/R40reviewer30` (removed before yield). No production file, no lane source, no fixture, no counter, no frozen claim was modified.

---

## Axis and the explicitly named distinct edge case

**Axis: coverage.** Distinct edge case, named explicitly:

> **Edge case 30 — the C3 kill signal is carried by the fixture's *stdout*, and the fixture's stdout contains the tool's stderr. A mutant that makes the tool crash is therefore reported as SURVIVED by the inherited r39 `score()` contract even when the fixture's own failure summary says it was detected.**

This is distinct from every other C3 seat in this wave:

| Seat | Its edge | How edge 30 differs |
|---|---|---|
| `R40executor39` | duplicate `TOTAL` multiplicity (two individually valid `TOTAL` rows) | Edge 30 is not *which* record bytes are parsed but *how the kill verdict is computed*. It holds with one `TOTAL` row. |
| `R40executor51` | duplicate `TOTAL` row parser/cardinality handling | Same — cardinality of `TOTAL` is orthogonal to the kill-computation path. |
| `R40executor63` | byte-decoding failure escaping before the `RECORD-MALFORMED` refusal contract | `R40executor63` targets *which* decode policy the tool uses. Edge 30 targets the **scorer**: the same tool bytes and the same fixture cases yield *opposite* verdicts depending only on whether the fixture echoes tool stderr into its stdout. |

Edge 30 is also distinct from the r39 base-fixture control clause, which is a *separate* axis of the same predicate: the control says "all mutants survive the r39 base fixture"; edge 30 shows the same `score()` function that reports `base_killed` also suppresses kills, so the control arm and the candidate arm share one defect.

---

## F1 (HIGH) — a detected crash-mutant is scored SURVIVED; the counter reports a false green/red

### Mechanism

`census/round-39/c3-counter.py:94-103` (`score()`), which the r40 C3 counter must inherit per the frozen control clause ("r39 fixture/counter"), computes:

```python
summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
...
crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)
killed = proc.returncode == 1 and fails > 0 and not crash
```

`proc` here is the **fixture** process. The fixture captures the tool's stderr into `out` and re-emits it inside the per-case detail string, which the fixture then prints on **its own stdout**:

- `tests/fixtures/r38-drift-record.py:92-93` → `results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (..., out.splitlines()[:3])))`
- `tests/fixtures/r38-drift-record.py:141` → `print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))`
- `tests/fixtures/r39-drift-record-rules.py:79-80` and `:133` → identical pattern

So the tool's traceback text reaches the fixture's stdout, `crash` becomes `True`, and `killed` becomes `False` — **even though the fixture's own `SUMMARY` line says `fail=N` with `N>0`, and the fixture exited 1.** The mutation is detected by the fixture and then discarded by the scorer.

### A/B proof on the COMMITTED r38 base fixture (not a scratch fixture)

Two mutants, identical defect *class* (the `RECORD-MALFORMED` schema-violation refusal on a malformed line), differing only in whether the tool raises a `Refusal` or a `ValueError`:

```
$ python3 -B score.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py \
      mut-crash-on-malformed.py mut-msg-change.py
mut-crash-on-malformed.py    killed=no  rc=1 fails=1 crash=True cases=10
mut-msg-change.py            killed=yes rc=1 fails=1 crash=False cases=10
```

Same fixture, same `fails=1`, same `rc=1`. The only difference is the tool's traceback. The crash variant is scored **not killed**.

Against the **committed r39 fixture** the same inversion holds:

```
$ python3 -B score.py .../tests/fixtures/r39-drift-record-rules.py \
      mut-crash-on-malformed.py mut-msg-change.py
mut-crash-on-malformed.py    killed=no  rc=1 fails=2 crash=True cases=7
mut-msg-change.py            killed=yes rc=1 fails=2 crash=False cases=7
```

Raw fixture stdout for the crash mutant against the committed r38 fixture shows the fixture *did* flag the defect — and its report is what trips the crash detector:

```
case-bad-line=FAIL rc=1 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] out=['Traceback (most recent call last):', '  File ".../mut-crash-on-malformed.py", line 1...']
SUMMARY cases=10 pass=9 fail=1
```

### End-to-end through a scratch r40-style counter

`r40-c3-counter-scratch.py` is the r39 counter **copied verbatim**, with only (a) the `MUTANTS` tuple replaced by r40-shaped single-defect mutants and (b) fixture paths repointed. The r39 `score()` is untouched. The tool bytes are the committed `0242085909…` bytes.

```
$ python3 -B r40-c3-counter-scratch.py --root $FIX --rev $REV --base-rev $REV \
      --fixture $FIX/tests/fixtures/r40-drift-branch.py \
      --base-fixture $FIX/tests/fixtures/r38-drift-record.py --scratch ...
MUTANT N1-strict-decode      killed=no  base_killed=no rc=1 fails=3 crash=True base:rc=0 fails=0 crash=False
MUTANT N2-ignore-decode      killed=yes base_killed=no rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
MUTANT N3-total-first-wins   killed=yes base_killed=no rc=1 fails=2 crash=False base:rc=0 fails=0 crash=False
MUTANT N4-total-dup-refuse   killed=yes base_killed=no rc=1 fails=3 crash=False base:rc=0 fails=0 crash=False
MUTANT N5-skip-never-discover killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT N6-skip-always-discover killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=6 killed=5 survived=1 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=e7bb23b0c5b8
exit=1
```

### Counterfactual: the verdict flips on a fixture-only change

The identical candidate fixture, with the **single** change of not echoing the tool's stderr into the case detail (`cand-noecho-fixture.py`), scores the same mutants differently:

```
### A) candidate fixture ECHOES tool stderr (r38/r39 house style)
SUMMARY mutants=6 killed=5 survived=1 pristine=ok base_killed=0 cases=8 fixture_sha=e7bb23b0c5b8   exit=1

### B) candidate fixture does NOT echo tool stderr
MUTANT N1-strict-decode killed=yes base_killed=no rc=1 fails=3 crash=False base:rc=0 fails=0 crash=False
...
SUMMARY mutants=6 killed=6 survived=0 pristine=ok base_killed=0 cases=8 fixture_sha=27976d79f6d3    exit=0
```

**Same tool bytes. Same mutant bytes. Same eight cases with the same expected verdicts. Opposite counter verdicts (exit 1 vs exit 0), decided solely by whether the fixture's diagnostic detail happens to quote the tool's stderr.**

### Consequence for the frozen C3 predicate

C3 requires "each declared single-defect mutant is killed by the r40 fixture". Under the inherited r39 `score()`:

- A crash-mutant that the fixture **detected** is reported **survived** → C3 fails on a false negative (`exit=1` above, `killed=5 survived=1`).
- The same battery passes cleanly if the fixture merely stops quoting tool stderr → the predicate's outcome depends on a diagnostic-formatting choice that no clause of the frozen predicate constrains.

The frozen predicate names "invalid UTF-8 record bytes" as a required branch. The only natural single-defect mutant for that branch that changes the *decode* contract is `decode("utf-8", "replace")` → `decode("utf-8", "strict")` (N1), and that mutant **crashes** the tool (measured below). So the branch C3 names, combined with the counter C3 names, deterministically produces a false negative under the r38/r39 fixture house style.

This also silently weakens the **control** arm: `base_killed` is computed by the same `score()`, so a base-fixture kill caused by a crash is also recorded as "not killed" (`base_killed=no` in every row above). The control clause "all mutants survive the r39 base fixture" is therefore not evidence that the r39 base fixture is blind to them — only that the scorer discarded the detection.

---

## F2 (HIGH) — invalid UTF-8 in a record is *position-dependent*, and one branch of it is a genuine defect the frozen C3 predicate does not name

C3 names one branch, "invalid UTF-8 record bytes". Measured against the committed `0242085909…` tool bytes, the **same** invalid byte in **six different positions** yields **four distinct observable outcomes**:

| Position of `\xff` | rc | Observable | Class |
|---|---|---|---|
| inside the `REPO` **name** field | **1** | `DRIFT ABSENT al<?>` **and** `DRIFT UNRECORDED alpha` | **not refused — silently accepted, two drift rows** |
| inside the `regs=` numeric field | 2 | `REFUSAL RECORD-MALFORMED: line 1 does not match the census schema` | refused |
| inside a **comment** line | 0 | `SUMMARY … drift_rows=0` | silently accepted, byte dropped |
| inside a garbage line | 2 | `REFUSAL RECORD-MALFORMED: line 1 …` | refused |
| inside the `TOTAL` row | 2 | `REFUSAL RECORD-MALFORMED: line 3 …` | refused |
| inside `TOTAL\trepos=2` | 2 | `REFUSAL RECORD-MALFORMED: line 3 …` | refused |

Exact evidence (probe `A1`–`A6`):

```
CASE A1-badbyte-in-name     rc=1  DRIFT ABSENT al<?>pha recorded regs=1 | DRIFT UNRECORDED alpha live regs=1 prunable=0 | SUMMARY … record_repos=2 … live_repos=1 … drift_rows=2
CASE A2-badbyte-in-numeric  rc=2  REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
CASE A3-badbyte-in-comment  rc=0  SUMMARY … drift_rows=0
CASE A4-badbyte-in-garbage  rc=2  REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
CASE A5-badbyte-in-total    rc=2  REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
CASE A6-badbyte-total-repos rc=2  REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
```

**The name-field case is the sharp one.** `tools/souji-worktree-drift.py:87` defines `ROW = re.compile(r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d+)\tprunable=(?P<prunable>\d+)$")` — `name` is `[^\t]+`, which happily accepts the U+FFFD replacement character produced by `decode("utf-8","replace")` at `tools/souji-worktree-drift.py:144`. So a corrupted name is **not** a schema violation: the row is accepted, the mangled name resolves to nothing, and the tool reports `ABSENT` for the corrupted name **while also reporting the real `alpha` as `UNRECORDED`** — one bad byte manufactures two drift rows and corrupts the `record_repos`/`live_repos` numerator. `live_repos=1` while `record_repos=2` is reported as if a repository had vanished.

That is a *semantic* defect (a mis-attributed numerator), not a parse-classification defect, and the frozen C3 predicate names only "invalid UTF-8 record bytes" with no position. A single r40 fixture case at the name position would assert `rc=1` + `ABSENT` and pass — cementing the two-row mis-attribution as expected behaviour rather than catching it.

**Byte-level observation:** the pristine tool emits the replacement char (`\xef\xbf\xbd`) while a `surrogateescape` mutant emits the raw byte (`\xff`) — same `ABSENT` token, different bytes:

```
pristine.py        rc=1  first-DRIFT-line bytes=b'DRIFT\tABSENT\tal\xef\xbf\xbdpha\trecorded regs=1'
mut-surrogate.py   rc=1  first-DRIFT-line bytes=b'DRIFT\tABSENT\tal\xffpha\trecorded regs=1'
```

Both contain the token `ABSENT`, so a token-matching fixture case cannot distinguish them: `mut-surrogate` is scored `SURVIVED f=0` by every fixture tried (candidate, no-echo candidate, committed r38, committed r39). A fixture that asserts only on decoded text is blind to the decode-policy difference.

---

## F3 (MEDIUM) — the `--skip-unrecorded` branch is only observable if the fleet contains a repository the record omits

The flag gates the discovery loop at `tools/souji-worktree-drift.py:370` (`if not args.skip_unrecorded:`). If every repository under `--root` is named by the record, the flag has **no observable effect at all** — the run is byte-identical with and without it.

Measured with a fleet containing `alpha`, `beta` (both named by the record):

```
### same-fleet fixture (no unrecorded repo present)
pristine.py          killed=no  rc=0 fails=0 crash=False cases=2
mut-skip-never.py    killed=no  rc=0 fails=0 crash=False cases=2
mut-skip-always.py   killed=no  rc=0 fails=0 crash=False cases=2
```

Both `--skip-unrecorded` mutants **survive**. Confirmed end-to-end through the scratch r40-style counter with a padded 7-case fixture (≥6 cases so the pristine gate passes) whose fleet contains no unrecorded repository:

```
### C') candidate fixture, >=6 cases, but NO unrecorded repo in the fleet
MUTANT N1-strict-decode killed=no …   MUTANT N4-total-dup-refuse killed=no …
MUTANT N5-skip-never-discover killed=no …  MUTANT N6-skip-always-discover killed=no …
SUMMARY mutants=6 killed=0 survived=6 pristine=ok base_killed=0 cases=7
exit=1
```

`pristine=ok` yet **zero of six** mutants killed. A fixture can satisfy "adds a `--skip-unrecorded` case" by *passing the flag* while never exercising the branch it names.

The flag's suppression set is also narrower than "skip unrecorded": measured with a fleet that *does* contain an unrecorded `gamma`:

```
S1-clean+unrecorded              rc=1 drift=1 live_repos=2 rows=['UNRECORDED']
S2-clean+unrecorded+flag         rc=0 drift=0 live_repos=2 rows=[]          <- flag suppresses UNRECORDED
S3-regs-mismatch+flag            rc=1 drift=1 live_repos=2 rows=['REGS-CHANGED']  <- recorded drift survives the flag
S4-absent-recorded+flag          rc=1 drift=1 live_repos=1 rows=['ABSENT']        <- recorded drift survives the flag
S5-unrecorded-only-record+flag   rc=0 drift=0 live_repos=1 rows=[]
```

A fixture case that asserts only "rc==0 with the flag" is satisfied by a fleet where the flag is a no-op. To discriminate, the r40 case must use a fleet with an unrecorded repository **and** assert the negative (`UNRECORDED` absent) — the `absent=[...]` check in my candidate fixture — plus a paired no-flag arm showing the row *is* present without it.

---

## F4 (MEDIUM) — "multiple TOTAL rows" has **two** distinct sub-branches, and one of them is order-dependent

C3 names "duplicate/multiple TOTAL rows" as one branch. `parse_record` (`tools/souji-worktree-drift.py:162-165`) overwrites `total` on every `TOTAL` match — **last one wins**, with no duplicate detection at all. Measured against the pristine tool:

```
C1-duplicate-total-same    rc=0 accepted     (two identical TOTAL rows -> accepted; NO duplicate refusal)
C2-two-total-bad-then-good rc=0 accepted     (first disagrees, second agrees -> the DISAGREEING one is silently discarded)
C3-two-total-good-then-bad rc=2 RECORD-MALFORMED: TOTAL repos=3 but 2 REPO rows
C4-two-total-disagree      rc=2 RECORD-MALFORMED: TOTAL repos=9 but 2 REPO rows
C5-triple-total            rc=0 accepted
```

The `C2` result is the substantive one: a record containing a `TOTAL` row that **disagrees** with the `REPO` rows is accepted, because a later `TOTAL` row overwrites the earlier one. The tool's own documented refusal class (`tools/souji-worktree-drift.py:48`, "a TOTAL row that disagrees") is therefore violated for any record with more than one `TOTAL` row — silently, not loudly.

Discriminating power of each sub-case against the two plausible mutants:

| case | pristine | `mut-total-first` (first-wins) | `mut-total-dup-refuse` |
|---|---|---|---|
| C1 dup-identical | accepted | accepted (indistinguishable) | rc=2 MALFORMED |
| C2 bad-then-good | accepted | **rc=2 MALFORMED** | rc=2 MALFORMED |
| C3 good-then-bad | rc=2 MALFORMED | accepted | rc=2 MALFORMED |

**C1 alone cannot kill `mut-total-first`** — it is the order-sensitive case that does. So an r40 fixture that adds only "two identical `TOTAL` rows" satisfies the wording of C3 while leaving the order-dependent sub-branch uncovered, and a first-wins defect would survive. Both C1 *and* C2 are required for that mutant.

---

## Consolidated score matrix (r39 `score()` semantics applied verbatim)

`SURVIVED(crash-suppressed)` = the fixture reported `fail>0` and exit 1, but `score()` discarded it because the fixture's stdout quoted the tool's traceback.

```
mutant (tool bytes)        | candidate (echoes stderr) | candidate (no echo)   | committed r39 fixture | committed r38 fixture
mut-strict                 | SURVIVED(crash-suppressed) f=3 | KILLED f=3      | SURVIVED f=0 | SURVIVED f=0
mut-ignore                 | KILLED f=2                 | KILLED f=2           | SURVIVED f=0 | SURVIVED f=0
mut-surrogate              | SURVIVED f=0               | SURVIVED f=0         | SURVIVED f=0 | SURVIVED f=0
mut-total-first            | KILLED f=2                 | KILLED f=2           | SURVIVED f=0 | SURVIVED f=0
mut-total-dup-refuse       | KILLED f=3                 | KILLED f=3           | SURVIVED f=0 | SURVIVED f=0
mut-skip-never             | KILLED f=1                 | KILLED f=1           | SURVIVED f=0 | SURVIVED f=0
mut-skip-always            | KILLED f=1                 | KILLED f=1           | SURVIVED f=0 | SURVIVED f=0
mut-crash-on-malformed     | SURVIVED(crash-suppressed) f=1 | KILLED f=1 | SURVIVED(crash-suppressed) f=2 | SURVIVED(crash-suppressed) f=1
mut-msg-change             | KILLED f=1                 | KILLED f=1           | KILLED f=2  | KILLED f=1
```

The last row (`mut-msg-change`) is the control that isolates F1: it is detected by the committed fixtures and scored `killed=yes`, whereas the crash mutant — detected by the *same* fixtures with the *same* `fail` count — is scored `killed=no`. Note the last two rows show the committed r38/r39 fixtures **do** kill `mut-msg-change` (`KILLED f=1` / `KILLED f=2`), i.e. they are not blind to the `RECORD-MALFORMED` branch; they are blind only to *how* the mutant manifests.

---

## Commands actually run

All commands were run from `/fast/scratch/hyaku/souji-r40/R40reviewer30` (or with an explicit `cd` into the scratch git fixture root). Exact commands:

```
read /home/vgpnk/.omp/agent/RULES.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e 0242085909fb6a4ee041c5443d76316ac6d59d4b^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py > pristine.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -1 0242085909fb6a4ee041c5443d76316ac6d59d4b
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 0242085909fb6a4ee041c5443d76316ac6d59d4b | grep -E 'drift'
sha256sum pristine.py                       # e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76

# fixture git repo (mktemp; every git command used -C $FIX; top-level asserted before commit)
FIX=$(mktemp -d /fast/scratch/hyaku/souji-r40/R40reviewer30/fixrepo.XXXXXX)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909…:tools/souji-worktree-drift.py > $FIX/tools/souji-worktree-drift.py
cp cand-r40-fixture.py $FIX/tests/fixtures/r40-drift-branch.py
cp .../tests/fixtures/r38-drift-record.py $FIX/tests/fixtures/r38-drift-record.py
git -C $FIX init -q -b main
test "$(git -C $FIX rev-parse --show-toplevel)" = "$FIX"
git -C $FIX add -A && git -C $FIX -c user.name=f -c user.email=f@e.invalid commit -qm "fixture base"

python3 -B probe.py pristine.py                      # F2 position sweep A1..A6, F3 S-cases, F4 C1..C5
python3 -B mutprobe.py                               # per-case mutant x case matrix
python3 -B decode-detail.py                          # decode-policy matrix over A1..A5
python3 -B skip-detail.py                             # --skip-unrecorded suppression set
python3 -B f5.py                                     # C1/C2/C3 discriminating-power table
python3 -B score.py <fixture> <tool>...              # r39 score() semantics, verbatim copy
python3 -B final-table.py                            # consolidated 4x8 matrix
python3 -B r40-c3-counter-scratch.py --root $FIX --rev $REV --base-rev $REV \
        --fixture $FIX/tests/fixtures/r40-drift-branch.py \
        --base-fixture $FIX/tests/fixtures/r38-drift-record.py --scratch /fast/scratch/hyaku/souji-r40/R40reviewer30
```

Git discipline honoured: fixture repos created with `mktemp`, every git command used `-C` with the exact fixture root, and `git rev-parse --show-toplevel` was asserted equal to the fixture root before each commit (the helper raises `SystemExit` on mismatch). The scratch fixture repo is under `/fast/scratch/hyaku/souji-r40/R40reviewer30` and was removed before yield.

---

## Verdict

**The frozen C3 coverage claim is falsifiable, and two of its three named branches cannot be satisfied as written without additional, unstated constraints.** Concretely:

1. **F1 (HIGH) — a concrete falsifier.** The r40 C3 counter inherits r39's `score()` (`census/round-39/c3-counter.py:94-103`), which reads the *fixture's* stdout for `Traceback (most recent call last)`. Because the r38/r39 fixtures quote the tool's stderr inside their per-case detail lines (`tests/fixtures/r38-drift-record.py:92-93,141`; `tests/fixtures/r39-drift-record-rules.py:79-80,133`), a mutant that crashes the tool is scored **SURVIVED even when the fixture detected it** (`fails>0`, exit 1). Demonstrated end-to-end on a verbatim copy of the r39 counter: `SUMMARY mutants=6 killed=5 survived=1 … exit=1`, flipping to `killed=6 survived=0 … exit=0` on a fixture-only change (not echoing tool stderr). The C3-required "invalid UTF-8 record bytes" branch is precisely the branch whose natural mutant (N1, `decode(…,"strict")`) crashes. **The predicate's outcome is currently decided by an unconstrained diagnostic-formatting choice, not by tool behaviour.**

2. **F2 (HIGH) — the named branch is under-specified and hides a real defect.** "Invalid UTF-8 record bytes" is **four** outcomes, not one. At the `REPO`-name position the pristine tool does **not** refuse: the U+FFFD replacement char satisfies `ROW`'s `[^\t]+` name field (`tools/souji-worktree-drift.py:87`, decode at `:144`), so the corrupted row is accepted and the tool emits **both** `ABSENT al<?>` and `UNRECORDED alpha`, reporting `record_repos=2 live_repos=1` — a mis-attributed numerator, not a refusal. A fixture case that asserts `rc=1`+`ABSENT` at that position would ratify the defect.

3. **F3 (MEDIUM)** — a `--skip-unrecorded` case is only discriminating if the fleet contains a repository the record omits; otherwise the flag is a no-op and both skip mutants survive (`SUMMARY mutants=6 killed=0 survived=6 pristine=ok cases=7`).

4. **F4 (MEDIUM)** — "duplicate/multiple TOTAL rows" splits into a multiplicity sub-branch and an **order-dependent** sub-branch (last `TOTAL` wins; a disagreeing `TOTAL` is silently discarded). The duplicate-identical case alone cannot kill a first-wins mutant; the asymmetric order case is required.

**Recommendation (does not alter the frozen claim — this is a measurement-plan input, not a redefinition):** the r40 C3 counter should score kills on the **fixture's own** `SUMMARY` line and the fixture's exit status, and must not read tool stderr out of the fixture's stdout; the r40 fixture should (a) include the invalid-UTF-8 case at the `REPO`-name position and assert the observed `ABSENT`/`UNRECORDED` pair so the mis-attribution is visible rather than ratified, (b) use a fleet with an unrecorded repository and assert the `UNRECORDED` row's presence without the flag and absence with it, and (c) include an asymmetric two-`TOTAL` ordering case. A byte-level (not decoded-text) assertion is additionally required to separate `decode(…,"replace")` from `decode(…,"surrogateescape")`, which are otherwise indistinguishable to any token-matching case.

**Residual risk / verification gaps:** the r40 candidate fixture, its declared mutants, and the r40 counter receipt do not exist in `census/round-40/` (that directory holds only `preregistration.txt`), so the r40 after-state was **not** run — pristine-pass, candidate-mutant kills, and r39-base survival for the real r40 artifacts are **unverified, not pass**. Everything above is measured against the committed `0242085909…` tool bytes with a scratch copy of the r39 counter and scratch candidate fixtures; the lane's own tool and fixtures were never modified.

**Tools installed/upgraded:** none. `pacman` untouched (paused by operator directive).

**Scope:** read-only against the lane apart from this report. Scratch confined to `/fast/scratch/hyaku/souji-r40/R40reviewer30` and removed before yield. No git/jj/index mutation, no commit, no push, no `.ufo/state` write, no fleet/sibling-lane write, no template or fleet-script write.
