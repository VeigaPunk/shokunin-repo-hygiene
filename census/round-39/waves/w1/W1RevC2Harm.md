# W1RevC2Harm — souji round 39, wave 1: attack C2 L6 (harm)

role: reviewer · lane `/home/vgpnk/Projects/shokunin/souji-shokunin` · base `ed30b7f5b77939c9073348d810730bc4f355708d`
audited revision: `2201778e7736af82e7d8a42dec2494f115bf3923` (HEAD at seat start; `git status --porcelain` showed only
untracked `census/round-39/` receipts, so worktree tool bytes == HEAD)
scratch: `/fast/scratch/hyaku/souji-r39/W1RevC2Harm` (see §9 for what remains)

Verdict in one line: **L6 as measured is honest — `pass=6 fail=0 harm=0` reproduces, and no consumer regresses on the
landed bytes — but the leg's harm dimension is under-powered: four single-defect mutants of the *documented* contracts
keep all six legs at `6/6 harm=0`, and three instrument-side weakenings keep L6 green while the receipt still prints the
same `fixture_sha`.** Two of the survivors are docstring/registry lines that the round's own bytes falsify, i.e. the same
R10/R13 class C1 exists to police. Details, commands and outputs below; §7 splits r39 in-scope from r40 named limits.

---

## 1. K1 — the counter reproduces the after receipt (PASS)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && time python3 -B census/round-39/c2-counter.py \
    --root "$PWD" --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch /fast/scratch/hyaku/souji-r39/W1RevC2Harm
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
real 0m8.031s
rc=0
```
Byte-identical to `census/round-39/records/c2-after.txt` (same `SUMMARY` line). **Verdict: PASS** — the frozen C2 predicate
holds on the audited bytes, and the receipt is reproducible.

## 2. K2 — L6 replay by hand: the five consumers do not discriminate base from landing (PASS, note)

Tool bytes extracted read-only from git (`git show <rev>:tools/...`) into scratch, then each consumer run directly:

```
$ for f in r38-drift-record r36-worktree-drift r38-drift-write-envelope; do
    python3 -B tests/fixtures/$f.py --tool $S/bin/drift-new.py --work $S | tail -1
    python3 -B tests/fixtures/$f.py --tool $S/bin/drift-base.py --work $S | tail -1; done
SUMMARY cases=10 pass=10 fail=0            (new)
SUMMARY cases=10 pass=10 fail=0            (base)
SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED   (new)
SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED   (base)
SUMMARY cases=12 pass=12 fail=0            (new)
SUMMARY cases=12 pass=12 fail=0            (base)
$ for f in r37-citation-reconcile r38-citation-commit r39-citation-rev; do ... done
SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED   (new) / identical (base)
SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED   (new) / identical (base)
SUMMARY cases=8  pass=8  fail=0            (new)
SUMMARY cases=8  pass=4  fail=4            (base)
```
`sha256sum` of the extracted bytes: `59f1e57d7af02cac...` (cit-new), `56866ea8f832332c...` (cit-base),
`e48ed08e672824e2...` (drift-new), `14e9c0f77d7e817d...` (drift-base) — they match the `tool_sha` field the counter prints.

**Verdict: PASS** for "no consumer regresses". Note: all five consumers read *identically* on both tool arms, so L6
carries zero discrimination for this round (it is a pure regression guard). That is by design, not a defect — but it is
why the survivors in §3–§5 matter: nothing else in L1–L5 covers the same ground.

## 3. K3–K4 — mutant replay through the *real* counter: two documented contracts survive all six legs (FAIL of the harm dimension)

Method: a synthetic minimal lane in scratch (own `git init` repo, toplevel asserted equal before the first commit:
`toplevel=/fast/scratch/hyaku/souji-r39/W1RevC2Harm/synth-lane.pvgf8sh7`), containing exactly the inputs the counter
declares — `tools/` at `--base-rev` = base bytes, `tools/` at `--rev` = landing bytes, `corpus/SOURCES.md` (L2's blob),
and the six fixture files read from the worktree. Harness: `/fast/scratch/hyaku/souji-r39/W1RevC2Harm/probe-c2.py`.

Control first (fidelity check):

```
### CONTROL pristine new bytes  rc=0
    LEG L1 PASS new rc=2 class=True old rc=2 class=False
    LEG L2 PASS new rc=2 class=True old rc=2 class=False
    LEG L3 PASS new rc=2 old rc=2
    LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
    LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
    LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
    SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
```
`tool_sha` identical to §1 → the synthetic root is a faithful replay.

### S1 — drift `ELOOP` reclassified `RECORD-MALFORMED` (survives, `6/6 harm=0`)

Mutant: `if exc.errno == errno.ENOENT:` → `if exc.errno in (errno.ENOENT, errno.ELOOP):`.

```
### MUTANT drift ELOOP->MALFORMED  rc=0
    LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
    LEG L6 PASS r38-drift-record=10/10(base 10/10) ... r38-citation-commit=14/14(base 14/14)
    SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/299892f9e697 fixture_sha=7ab7c3d85a81
```
The audited docstring line says the opposite (`tools/souji-worktree-drift.py:44-45`):

```
  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
                         exists but cannot be opened or read
```
**Verdict: FAIL** — the `ELOOP` half of the round's own new docstring sentence is unpinned in both directions; no fixture
in the lane mentions `ELOOP` (`grep -rn "ELOOP\|ENOTDIR\|ENAMETOOLONG" tests/fixtures/*.py` → no hit), and L4's two-probe
design (ENOENT + EACCES) cannot reach it.

### S2 — citation receipt-arm `ANCESTOR-ERROR` stops counting as a mismatch (survives, `6/6 harm=0`)

```
### MUTANT citation ANCESTOR-ERROR not counted  rc=0
    LEG L6 PASS r38-drift-record=10/10(base 10/10) ... r38-citation-commit=14/14(base 14/14)
    SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=84333d5e33c8/e48ed08e6728 fixture_sha=7ab7c3d85a81
```
This is not hypothetical — I forced a real `merge-base` error in a scratch fixture (commit chain c0→c1→c2, c0's loose
object removed; `cat-file -e c2^{commit}` still rc 0, `merge-base --is-ancestor c2 c1` → `rc=128`):

```
$ python3 -B $S/bin/cit-new.py --root "$D" --rev 45d3dc0... --register "$D/reg.tsv"
MISMATCH E1 RECEIPT-REV-ANCESTOR-ERROR receipt.txt at a8957216a8a468d2cad7c8abeddca140a07164a2
SUMMARY cells=1 mismatches=1
rc=1
$ python3 -B $S/bin/cit-ancerr.py --root "$D" --rev 45d3dc0... --register "$D/reg.tsv"   # mutant: mismatches += 1 removed
MISMATCH E1 RECEIPT-REV-ANCESTOR-ERROR receipt.txt at a8957216a8a468d2cad7c8abeddca140a07164a2
SUMMARY cells=1 mismatches=0
rc=0
$ python3 -B tests/fixtures/{r37-citation-reconcile,r38-citation-commit,r39-citation-rev}.py --tool $S/bin/cit-ancerr.py
SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED
SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED
SUMMARY cases=8  pass=8  fail=0
```
**Verdict: FAIL** — a documented exit contract (`Exit: 0 mismatches=0, 1 any mismatch`, tool docstring line 45) can be
broken to `rc=0` *with a MISMATCH line on stdout* on a shape no fixture exercises, and every leg stays green.

### Not a survivor (positive control that L6 works at all)

S3 — drift `ENOENT` → `RECORD-MISSING` (the code half of the R10 repair reverted) **is** caught:

```
### MUTANT drift ENOENT->MISSING (R10 revert)  rc=1
    LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
    LEG L6 FAIL r38-drift-record=9/10(base 10/10) ...
    SUMMARY legs=6 pass=5 fail=1 harm=1 tool_sha=59f1e57d7af0/6d33a5de3a71 fixture_sha=7ab7c3d85a81
```
Note L4 still says PASS here — see §4.

## 4. K5–K6 — L4 cannot re-detect the defect it was added for (FAIL of L4's trigger half)

`census/round-39/c2-counter.py:227`:
```python
missing in new_classes and "missing" in new_classes.get(missing, "").lower()
```
The docstring line for `RECORD-MISSING` begins with the token `RECORD-MISSING`, so `"missing" in line.lower()` is
satisfied by the class name itself:

```
docstring RECORD-MISSING line: RECORD-MISSING         EACCES or ELOOP opening the record path: the path
'missing' in line.lower(): True (satisfied only by the class token)
```
That is why S3 keeps `L4 PASS missing=RECORD-MISSING`. **The only real discriminator in L4 is the `EACCES` half** (that
word is not a substring of a class token). So L4's `new_maps=True` is vacuous for the MALFORMED side, and the round's
L4 claim ("the drift docstring's RECORD-MISSING/RECORD-MALFORMED mapping matches the classes the tool actually produces
for a missing and an unreadable record") is narrower than it reads.

### The same docstring line is falsified by two other errno values (live bytes, no mutant)

```
$ python3 -B tools/souji-worktree-drift.py --root "$L" --record "$S/probe/parentfile/rec.tsv/child.tsv" --timeout 10
REFUSAL RECORD-MISSING: [Errno 20] Not a directory: '.../parentfile/rec.tsv/child.tsv'      rc=2
$ python3 -B tools/souji-worktree-drift.py --root "$L" --record "$S/probe/<300 x's>" --timeout 10
REFUSAL RECORD-MISSING: [Errno 36] File name too long: '.../xxx...'                         rc=2
$ python3 -B tools/souji-worktree-drift.py --root "$L" --record "$S/probe/loop_a" --timeout 10
REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: '.../loop_a'          rc=2   (matches the line)
$ python3 -B tools/souji-worktree-drift.py --root "$L" --record "$S/probe/locked.tsv" --timeout 10
REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../locked.tsv'                     rc=2   (matches the line)
```
`ENOTDIR` and `ENAMETOOLONG` raise `RECORD-MISSING` while matching neither named condition ("EACCES or ELOOP … the path
exists"), and the `RECORD-MALFORMED` line ("a missing (ENOENT) or non-regular record path") reads as if a path whose
component is a regular file would be `MALFORMED`. The r39 edit *tightened* this line from "the record path cannot be
read" to an exhaustive-sounding "EACCES or ELOOP", so the round strengthened a claim its own code falsifies.
**Verdict: FAIL (calibration, in-scope).**

## 5. K7–K9 — L6's instrument is not revision-bound and reads only SUMMARY arithmetic (FAIL of the harm dimension)

`c2-counter.py:63` (`lane_root_of` = working tree), `:170` (`fixture_sha` hashes **only** `r39-citation-rev.py`),
`:265` (`green = new_r[0] == new_r[1] and new_r[2] == 0`), `:268` (`if new_r[1] < old_r[1]`). `new_r[3]` (the fixture's
own exit status) and the `control=` field are never read. Three probes, harness
`/fast/scratch/hyaku/souji-r39/W1RevC2Harm/probe-c2b.py`, all against the same synthetic lane:

```
### P1 case deleted from r38-drift-record (pristine tools)  rc=0
    LEG L6 PASS r38-drift-record=9/9(base 9/9) ...
    SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81

### P2 consumer rc forced to 1, SUMMARY still 10/10  rc=0
    LEG L6 PASS r38-drift-record=10/10(base 10/10) ...
    SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81

### P3 ENOENT->MISSING mutant + relaxed expectation  rc=0
    LEG L6 PASS r38-drift-record=10/10(base 9/10) ...
    SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/6d33a5de3a71 fixture_sha=7ab7c3d85a81
```
- P1: deleting a case (10 → 9) is invisible — `green` only compares a fixture against itself.
- P2: a consumer that prints `cases=10 pass=10 fail=0` and exits 1 is green — the fixture's own verdict is ignored.
- P3: the S3 regression that L6 *does* catch (9/10) is fully cancelled by relaxing one expectation in the **uncommitted**
  worktree fixture. `10/10(base 9/10)` also shows the base-arm drop is not harm.
- All three print `fixture_sha=7ab7c3d85a81`, identical to `c2-after.txt` — the receipt cannot distinguish any of them from
  the pristine run, because the five consumer fixtures are never hashed or compared at `--rev`.

**Verdict: FAIL (harm dimension).** The raw fact "fixtures from the working tree" is documented (counter docstring, and the
SKILL row: "Both tool revisions come from `git show`; fixtures from the working tree"), but the *consequences* — a weakened
instrument cancels a caught regression, case-count loss is invisible, the fixture's exit status is ignored — are not, and
the claim "six consumer fixtures stay green" is then a claim the leg cannot substantiate.

## 6. K10–K12 — three further defects, two of them the round's own bytes

### K10 — the SKILL registry row that C2's premise cites is stale on both axes (FAIL, in-scope calibration)

`SKILL.md:250` (unchanged by the round; `git diff ed30b7f..HEAD -- SKILL.md` adds only the nine r39 rows and the R39-C1-06
line):

```
| r37-citation-reconcile | gate | ... | 0 `mismatches=0`; 1 any MISMATCH line — citation (...), receipt
(`RECEIPT-REV-UNRESOLVED`, `RECEIPT-REV-NOT-ANCESTOR`, `RECEIPT-ABSENT`, `RECEIPT-DISAGREES`) or commit
(`COMMIT-UNRESOLVED`, `COMMIT-NOT-ANCESTOR`, `COMMIT-UNNAMED`, `COMMIT-RECEIPT-ABSENT`, `COMMIT-RECEIPT-DISAGREES`);
2 usage / malformed register / non-40-hex rev / non-regular or symlinked register | ... |
```
The landed bytes emit two classes the row does not list — `COMMIT-ANCESTOR-ERROR`
(`tools/souji-citation-reconcile.py:221`) and `RECEIPT-REV-ANCESTOR-ERROR` (`:307`); `grep -rn "ANCESTOR-ERROR" SKILL.md
corpus/ tests/` → only the two tool lines. And the row's exit-2 clause lists "non-40-hex rev" but not the new
`REFUSAL REV-UNRESOLVED` for a 40-hex rev that does not resolve — which is precisely the class C2 claims to have aligned
with the registry. The tool's own docstring enumerates the commit arm as exactly five classes
(`tools/souji-citation-reconcile.py:32-35`), so the sixth is documented nowhere at all.
**Verdict: FAIL** — an enumerated lane set that the bytes contradict (R10/R13 class). The prereg's phrasing "the
could-not-evaluate exit 2 its SKILL registry row promises" is also imprecise: the row's own list does not promise exit 2
for an unresolvable rev; only the general gate map (`SKILL.md:191`) does.

### K11 — `--register-rev` criterion in the docstring is not the implemented criterion (FAIL, in-scope, low)

The new paragraph says both flags "must name a commit that resolves (`git cat-file -e <rev>^{commit}`)". Empirically a
short rev resolves but is refused as unresolvable, because of an extra 40-hex test:

```
$ git -C "$L" cat-file -e 2201778^{commit} && echo "cat-file -e 2201778^{commit} rc=0 (it DOES resolve)"
cat-file -e 2201778^{commit} rc=0 (it DOES resolve)
$ python3 -B $S/bin/cit-new.py --root "$L" --rev 2201778e... --register census/round-38/cells.tsv --register-rev 2201778
REFUSAL REV-UNRESOLVED: --register-rev 2201778 does not resolve to a commit     rc=2
$ python3 -B $S/bin/cit-nohex.py ... --register-rev 2201778      # mutant: 40-hex clause removed
SUMMARY cells=10 mismatches=0                                                    rc=0
$ python3 -B $S/bin/cit-nohex.py ... --register-rev HEAD
SUMMARY cells=10 mismatches=0                                                    rc=0
```
The message is false for a rev that resolves, the docstring criterion and the code criterion differ, and no fixture pins
either side (`r39-citation-rev`'s `rev-short` covers `--rev` only; the nohex mutant keeps `6/6`, §3). One-line docstring
fix ("40-hex and resolving") plus optionally a ninth case.

### K12 — the C2 after receipt is untracked at the audited revision (state observation)

```
$ git -C "$L" status --porcelain census/round-39/
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```
I reproduced `c2-after.txt` byte-for-byte (§1), so the measurement is sound; but at `2201778` the C2 after-receipt lives
only in the worktree. If the round lands without it, that is the r38 R4 class ("untracked wave evidence"). Not a defect in
the counter — a landing obligation for the L1.

### K13 — `ancestor_status` is called twice per register row (low, operability/cost)

`tools/souji-citation-reconcile.py:307-310`: the `== "error"` arm and the `== "no"` arm each invoke `ancestor_status`,
i.e. two `merge-base` subprocesses per row (the first result is discarded on the `no` path). No behavioural divergence is
possible (same inputs, read-only), but it doubles the git calls of a 10-row register. Assign to a local.

## 7. Scope: what is r39 and what is a named r40 limit

**In scope for r39** (lane bytes exist and the claim is falsified by them; each is a one-to-few-line fix):

| id | defect | fix |
|----|--------|-----|
| F1 | `SKILL.md:250` class list and exit-2 list stale; `COMMIT-ANCESTOR-ERROR` / `RECEIPT-REV-ANCESTOR-ERROR` documented nowhere (tool docstring enumerates five commit classes) | add the two classes to the tool docstring and the SKILL row; add `REFUSAL REV-UNRESOLVED` to the row's exit-2 clause |
| F2 | drift docstring `RECORD-MISSING` = "EACCES or ELOOP" falsified by ENOTDIR/ENAMETOOLONG; `RECORD-MALFORMED` line misreads a non-directory component | widen the line to "any open failure other than ENOENT" (no code change) or classify ENOTDIR/ENAMETOOLONG as MALFORMED; pin ELOOP with a fixture case |
| F3 | L4's MALFORMED-side trigger check is vacuous (`"missing"` ⊂ class token) | require a trigger word that is not a substring of the token (`"ENOENT"`) |
| F4 | L6 instrument not revision-bound; ignores fixture exit status and `control=`; case loss invisible | hash the five consumers at `--rev` and compare, require `new_r[3] == 0`, require `new_r[0] >= old_r[0]` |
| F5 | `--register-rev` docstring criterion ≠ code criterion; false "does not resolve" message | docstring "40-hex and resolving"; optional ninth case |
| F6 | C2/C3/census after-receipts untracked at HEAD | L1 lands them with the round |
| F7 | double `ancestor_status` call | assign to a local |

F1, F2, F3 and F5 are calibration/operability defects in the same classes the round routed (R10, R13, R11-adjacent) and
are cheap; F4 is the harm dimension itself and is the difference between "harm=0 measured" and "harm=0 meaningful".

**Named limits for r40** (legitimately outside this round's claim; must be written down rather than implied):

- L6 has no mutant dimension at all. C3 has a four-mutant battery; C2's harm leg is a pass-count comparison. The r40
  lesson should name "C2 L6 cannot distinguish a documented contract from a fixture-visible one" and the S1/S2 mutants as
  its examples.
- The citation tool's refusal set (`REV-UNRESOLVED`, `USAGE`, register lookup) has no fixture for the row-level
  `receipt_rev`/`commit` non-hex shape; the boundary between "refuse" and "find" at row level is unpinned.
- `--register-rev` accepts an empty string as "absent" (falsy check) rather than refusing it; unchanged by the round, not
  claimed, not pinned.
- The `EACCES` probe in L4 needs the process to be non-root; the leg is silently vacuous when run as root (chmod 0 still
  opens). Not exercised here (this host runs as `vgpnk`), but worth naming.

## 8. What I did not do

No lane byte was modified; no commit, push, `git add/stash/checkout/switch/reset`, or `jj` mutation anywhere. All git
fixtures were `mktemp -d` + `git -C "$D" init -q` with `rev-parse --show-toplevel` asserted equal to `$D` before the first
commit (output quoted in §3). Mutants were applied only to copies extracted with `git show` into scratch. No tool was
installed (nothing needed beyond `python3`/`git`).

## 9. Scratch

`/fast/scratch/hyaku/souji-r39/W1RevC2Harm` — 136K, still on disk: the two harnesses `probe-c2.py` (synthetic-lane mutant
replay) and `probe-c2b.py` (instrument-side probes), plus `bin/` with the four `git show`-extracted tool revisions and the
two mutants (`cit-nohex.py`, `cit-ancerr.py`). The git fixtures (`tmp.*`, `synth-lane.*`, `probe/`, counter scratch) were
removed after the runs.

## 10. Verdicts

| check | verdict |
|-------|---------|
| K1 counter reproduces `c2-after.txt` (`6/6 harm=0`) | PASS |
| K2 five consumers green, none regresses vs base | PASS (no discrimination between arms) |
| K3 synthetic-lane replay fidelity (`tool_sha` identical) | PASS |
| K4a S1 `ELOOP`→MALFORMED survives all six legs | FAIL (harm dimension) |
| K4b S2 `RECEIPT-REV-ANCESTOR-ERROR` exits 0 with a MISMATCH line, all legs green | FAIL (harm dimension) |
| K4c S3 `ENOENT`→MISSING caught by L6 at 9/10 | PASS (positive control) |
| K5 drift `RECORD-MISSING` line falsified by ENOTDIR/ENAMETOOLONG | FAIL (calibration) |
| K6 L4 `missing` trigger check vacuous | FAIL (operability of the leg) |
| K7 P1 case deletion invisible (9/9) | FAIL (harm dimension) |
| K8 P2 fixture exit status ignored | FAIL (harm dimension) |
| K9 P3 weakened worktree fixture cancels a caught regression | FAIL (harm dimension) |
| K10 SKILL row class/exit lists stale | FAIL (calibration) |
| K11 `--register-rev` criterion doc ≠ code | FAIL (low) |
| K12 after receipts untracked at HEAD | observation, landing obligation |
| K13 double `ancestor_status` | FAIL (low, cost) |

C2's L6 predicate itself: **admitted as measured** (`pass=6 fail=0 harm=0`, reproducible, no live consumer regression).
C2's *harm* claim: **under-powered** — the seven FAILs above are all shapes the leg cannot see, and four of them are
single-defect mutants that keep the whole counter at `6/6 harm=0`.
