# S60CriticRound — pre-freeze falsification of the round-60 admission conjunction

Seat: S60CriticRound (critic, leaf). Date: 2026-11-04. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`,
read-only. Lane HEAD at review: `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4` (`git rev-parse HEAD`).
No lane file, index, jj state or production path was written. Fixtures were built only under
`/fast/scratch/hyaku/souji-r60/S60CriticRound/`.

Method: read the frozen rules (QUALITY.md Q99/Q100/Q102/Q120), the r59 lessons and r59 verifier
spot-check, the r57/r59 preregistrations, the wave spec and every delivered seat artifact; then
executed the delivered counters/fixtures against the base bytes and against the delivered candidates,
and built two synthetic freeze records to test the round's own record under the arm it lands.

Artifacts measured (sha256; wave paths are untracked because `.gitignore:1:.ufo/waves/`):

| artifact | sha256 |
|---|---|
| `tools/souji-freeze-check.py` @ `1e8bfd87` (base) | `d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364` |
| `census/round-57/record-receipt.sh` (C2 base, unchanged since r57 freeze) | `84148011abc9574048fc77e02427bee9010850418beeeaaa1babe59185109aa9` |
| `S60ExecFreezeArm/souji-freeze-check.py` (C1 candidate) | `928745cd7f294320e6a37551334f32f43eb409728169bb5d8606c8b7054cb24e` |
| `S60ExecRecorder/souji-receipt-write.py` (C2 candidate) | `b916a4fd28206ac80208bc22027abc31778d8b893e8f3744270d612684b53e9f` |
| `S60ExecMatrix/c1-counter.py` | `96ec711aa48359248c0ee4e7b9392e0e10f39a232fb526191635834b7e54b715` |
| `S60ExecMatrix/c1-matrix.tsv` | `7973d52030f9bf7d34867c2a46527708556cf82765c1e5b4a5f087bcb310132d` |
| `S60ExecControls/c1-counter.py` | `a1874cde66163fbf57ad264c42a69c85f223aa9f69db89f1d642b3688eb69b30` |
| `S60ExecControls/c1-matrix.tsv` | `ba1777d0793d06ee260661f00bdc74a55f448b693951e9dfb944155d4dee5320` |
| `S60ExecControls/c2-fixture.py` | `8f9bad4ea668dab27ef6f408bfcddfb266f551ea5740fdebba02e0706d881deb` |
| `S60ExecRecorderFix/r60-receipt-write.py` | `d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114` |
| `S60ExecControls/do-nothing-c1.txt` | `f3a263cfbfd8bf4815044d8bffb75d0f092c8702e75b16e2f04f4fcec9af66e6` |
| `S60ExecControls/do-nothing-c2.txt` | `7cc38e89b5bf9b029f5a42a51e30583b1dac8e7dce8acd06b08ecd252d729337` |
| `S60ExecMatrix/base-run.txt` | `d105746a9a570b75e471658ab5a9607846dd5e3e84cb0bab21dbb7e31cec1fcd` |
| `S60ExecMatrix/new-run.txt` | `35139492a88d6b77e3c15c482d740e717c01851b43513be1790c3f541b4c6197` |
| `S60ExecRecorderFix/base-run.txt` | `e68b2a7dd4f7b320ac60550ec427de79ce228de2d7a65eff9f3709ed8090bbaa` |
| `S60ExecRecorderFix/new-run.txt` | `ead0b28e34505c0a66197608304891a30db361024c5ca841c566c8630cf934a7` |

---

## Findings

### 1. C2's frozen base value is false: the round's own fixture measures 4/8, not 3/8 — VIOLATES

The claim text (frozen in the wave spec) says "base recorder `census/round-57/record-receipt.sh` = 3/8".
Two independently authored fixtures, and the pre-freeze control receipt itself, measure **4/8**:

```
$ python3 -B .ufo/waves/round-60/w1/S60ExecRecorderFix/r60-receipt-write.py \
    --tool census/round-57/record-receipt.sh --work <scratch>
CASE 1 clean-write fail        (command= line missing)
CASE 2 overwrite fail          (tool rc=0, want 2)
CASE 3 atomic-in-flight pass
CASE 4 kill-residue pass
CASE 5 bound fail              (tool rc=127, want 2)
CASE 6 rev-short pass
CASE 7 instrument-absent pass
CASE 8 dirty-tree fail         (tool rc=0, want 2)
SUMMARY cases=8 pass=4 fail=4 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED
EXIT=1
```

The delivered control receipt says the same: `S60ExecControls/do-nothing-c2.txt` →
`SUMMARY cases=8 pass=4 fail=4`, `EXIT=1`. The four passing cases are `atomic-in-flight`,
`kill-residue`, `rev-short`, `instrument-absent`; the base already refuses short/absent revs and already
buffers output before writing, so those four cannot be made red without changing the case definitions.

Rule: Q120 ("independent expected rc/findings"), Q99 (`Target:` is the frozen predicate), Q3 of the seat
question. A `Target:` of `base=3/8` is false at the freeze commit and no after-data can repair it; the
frozen predicate would contradict the frozen `Control:` receipt. This is the round's most direct
rejection ground.

Smallest safe correction: freeze the measured value — `base pass=4` and name the four cases — or remove
the base count from `Target:` and keep only `new=8/8` plus `base<8`.

### 2. The round's own freeze record is refused by the arm it lands — VIOLATES (Q100/Q120)

The delivered pre-freeze receipts (`do-nothing-c1.txt`, `do-nothing-c2.txt`, `S60ExecMatrix/base-run.txt`)
carry **no column-0 `instrument=`, `instrument_sha256=`, `rev=` or `command=` lines** (grep returns
NONE for all three). The C1 arm requires exactly those lines on the `Control:` receipt. Building the
round's own record from the delivered bytes (Counter = `S60ExecMatrix/c1-counter.py`,
Population = `c1-matrix.tsv`, Control = `do-nothing-c1.txt`, `Round: 60`) and running the candidate:

```
$ python3 -B S60ExecFreezeArm/souji-freeze-check.py --root <fixture> \
    --prereg census/round-60/preregistration.txt --rev <freeze> --substance
FINDING C1 CONTROL-COMMAND-MISSING ... has no command= line
FINDING C1 CONTROL-INSTRUMENT-MISSING ... has no instrument= line
FINDING C1 CONTROL-INSTRUMENT-MISSING ... has no instrument_sha256= line
FINDING C1 CONTROL-REV-MISSING ... has no rev= line
SUMMARY claims=1 findings=4
EXIT=1
```

So the round would land an arm that rejects the round's own freeze record. A compliant wrapper — the same
run body prefixed with `instrument=<Counter path>`, `instrument_sha256=<Counter blob digest>`,
`rev=<strict ancestor>`, `command=...<Counter path>...` and ending `EXIT=1` — makes both instruments
accept the record:

```
$ python3 -B S60ExecFreezeArm/souji-freeze-check.py ... --substance   → SUMMARY claims=1 findings=0  EXIT=0
$ python3 -B tools/souji-freeze-check.py ...                          → SUMMARY claims=1 findings=0  EXIT=0
```

Rule: Q100 (substance check reads the artifact against the source it cites), Q120 (controls with exact
bytes/revisions/instrument digest before freeze). The wrapper is a byte-level edit of the receipt, not a
re-run; it does not backdate anything.

### 3. Duplicate authority: two C1 counters, two matrices, two new-arm semantics — VIOLATES (Q120 exactness)

- `S60ExecMatrix/c1-counter.py` (`96ec711a…`) always appends `--substance` to the NEW arm; at base bytes
  that is an argparse error → `EXIT=2` (could-not-evaluate), unless `--new-arm plain` is passed (the
  seat's `base-run.txt` does pass it).
- `S60ExecControls/c1-counter.py` (`a1874cde…`) drives NEW as "the tool at `--rev`" with no flag; at base
  it yields `forgeries_accepted=5 honest_accepted=3`, `EXIT=1`.
- The two matrices are not interchangeable: ExecMatrix's `class` column is `honest|forgery` and its
  honest-2 row names `matrix/honest-2/ctl-c1.txt`; ExecControls' `class` column holds finding ids and its
  honest-2 row names `ctl1.txt,ctl2.txt`.

The same nominal invocation therefore has two different expected rcs (1 vs 2). Q99 requires the `Control:`
receipt to be the declared Counter's receipt; Q120 requires one exact instrument digest. If the L1 freezes
`S60ExecMatrix/c1-counter.py` as `Counter:` and uses `do-nothing-c1.txt` (which names the ExecControls
runner in its argv and carries no binding lines) as `Control:`, the control is not a run of the declared
counter. Smallest safe correction: freeze the spec-designated ExecMatrix runner + its matrix, and
regenerate the control with it (`--new-arm plain`, already receipted in `base-run.txt`, `EXIT=1`,
`forgeries_accepted=5`), wrapped per Finding 2.

### 4. The C1 matrix does not assert the finding class it names — VIOLATES (Q100)

The seat spec names a class per forgery (`CONTROL-INSTRUMENT-MISSING`, `…MISMATCH`,
`CONTROL-REV-NOT-BEFORE-FREEZE`, `CONTROL-REV-MISSING`, `CONTROL-COMMAND-MISMATCH`). The delivered
ExecMatrix TSV collapses the column to `forgery`; its runner only compares `accept|refuse` and validates
`class ∈ {honest, forgery}`. The ExecControls runner prints `EXPECT-CLASS` but never compares it to the
emitted `FINDING` lines. Observed on the rebuilt cases with the candidate:

```
forgery-rev-at-freeze: FINDING C1 CONTROL-REV-INVALID ctl.txt rev='freezemark' does not resolve to a commit
```

i.e. the case named `CONTROL-REV-NOT-BEFORE-FREEZE` fires a *different* class and still counts as a pass.
A candidate arm that refuses all five forgeries with one wrong class passes the matrix. Q100 requires the
non-counter substance check; the class is the substance here and is unasserted. Correction: add the
finding id to the matrix and compare the emitted `FINDING` lines, or name this as a limit and do not
claim class discrimination.

### 5. `forgery-rev-at-freeze` is not the specified input — VIOLATES (Q120 exact input)

A commit tree cannot contain its own hash, so the builder substitutes the lightweight tag
`rev=freezemark` (builder docstring; `matrix/forgery-rev-at-freeze/ctl.txt`). The candidate rejects the
tag as non-40-hex (`CONTROL-REV-INVALID`) before ancestry is ever evaluated; a candidate that resolved the
tag would fire `CONTROL-REV-NOT-BEFORE-FREEZE`. The case cannot distinguish the two, and it does not test
"rev == the freeze commit" as the spec states. The ExecMatrix `expected.txt` also pins `control_rev=` to
the *ancestor* (`14ab27ee…`), not the freeze (`dc1f00d9…`), so the delivered expectation contradicts the
case's own name. Correction: document the substitution as a limit and keep the class out of the claim, or
replace the case with a constructible non-ancestor (orphan) case and say so.

### 6. C2's "atomic temp+rename" is not established by its fixture — VIOLATES (Q100)

Cases 3 (`atomic-in-flight`) and 4 (`kill-residue`) **pass for the base recorder**, which creates no temp
file at all and writes `OUT` directly after the command returns. They test "OUT absent before the command
completes" and "no residue after SIGKILL", not temp+fsync+`os.replace`. The candidate's atomicity is real
in its code (`mkstemp` beside OUT, `fsync`, `os.replace`, dir fsync, SIGTERM/SIGINT cleanup), but the
fixture never observes it. The claim's operability surface is therefore partly code-read, not measured.
Correction: name it a limit (or add a case that observes the temp path during the final write).

### 7. C1's "substance" is bytes, not execution — NAMED LIMIT (Q100 shim rule)

The arm binds `instrument_sha256` to the Counter blob and `rev` to an ancestor; it never runs the counter.
The reviewer's `c-never-executed` case (base accept, contract "bytes only") shows a receipt claiming a run
that never happened passes if the bytes match. Q100's execution-count shim is absent. The claim must not
claim execution authenticity; the candidate's NOTES.md limit 3 already says the digest binds bytes.

### 8. Chronology is achievable only under a three-commit sequence and the census-copy route — CONDITIONAL

- `git ls-tree -r HEAD .ufo/waves/round-60` is empty; `.gitignore:1:.ufo/waves/` means the wave tree
  (spec, dispatch, receipts, deliveries) is untracked. The r59 precedent is a durable copy at
  `census/round-59/wave/` (present, with `w1-dispatch.json`, `w1-spec.json`, `w1-results.json`).
- If the L1 force-adds `.ufo/waves/round-60/w1-dispatch.json`, `w1-spec.json` or `w1.ready`, the base
  checker's `DISPATCH-BEFORE-FREEZE` fires at the freeze commit (the r59 red pattern) because those files
  were created before any freeze commit can exist.
- Q99: the freeze commit is the *oldest* commit that adds the prereg, and the Counter/Population/Control
  blobs must exist at it. So the order must be: A = `census/round-60/` counter + matrix + control receipt
  (+ candidate instruments), B = the prereg alone, C = the measurements. Any `new-run`/after receipt in A
  or B puts after-data in the freeze.
- Wall clock: the after-data already exists (new-run 8/8, base 4/8, candidate selftests) before the freeze
  commit. The lane's r57 precedent handles this with a disclosed "Development note: before this file
  existed … SCRATCH dry-runs … the official post-freeze matrices must reproduce the dry-run TSVs byte for
  byte". The r60 prereg must carry the same disclosure and require byte-identical post-freeze reproduction;
  otherwise "frozen before data" is false in substance.

### 9. C2 re-declares the rejected r57 C2 without successor framing — VIOLATES (Q120)

r57's C2 was "a receipt must bind the revision it was measured at", recorder `census/round-57/record-receipt.sh`,
8-case fixture — the same surface and the same base file as r60's C2. r57 is **rejected-harmed**
(`corpus/lessons/round-57-verifier-spotcheck.md:12,23,139`; r59 lessons "Prior r56/r57 rejected-harmed …
remain unchanged"). Q120 permits a successor only with executed no-work and forgery controls, exact
input bytes/revisions, commands, instrument digest, independent expected rc/findings and observed outputs
in a commit strictly before the freeze. The r60 claims text names neither the r57 rejection nor successor
status. Correction: declare "successor to rejected r57 C2" in the prereg, cite the r57 rejection, and
pin the corrected expected base value (Finding 1).

### 10. Axis label mixes an axis with a claim type — VIOLATES as written (AXES.md)

C1 is labelled "calibration/capability". Fleet `AXES.md` defines six axes (depth, coverage, operability,
freshness, calibration, adjacency); "capability acquisition" is a claim *type* that "still lands a
per-axis verdict, with the claim type recorded in the round report". The lane owns calibration 7,
operability 8, coverage 8 (`SCORECARD.md:3`). The surface C1 moves — a checker that refuses forged freeze
records — is calibration. Correction: `Axis: calibration` and `Claim type: capability acquisition` as
separate lines. C2's `operability` label is correct.

### 11. C2's dirty-tree refusal is vacuous in the real lane — NAMED LIMIT

`.ufo/waves/` is gitignored, so `git status --porcelain` in the lane is empty even with the whole wave
tree present (observed: `git status --porcelain .ufo/waves/round-60` prints nothing). The dirty-tree case
is only exercised in the synthetic fixture repo. The claim's operability in the real lane is unproven.

### 12. C2 fixture timing and Q102 hidden-case audit — NAMED LIMIT

Cases 3/4 depend on wall-clock offsets (0.3 s, 0.4 s) and the fixture's case names are deterministic and
readable by the tool under test; Q102's hidden-case audit (opaque names, fresh salts, CRLF, spaces, absent
keys, a second claim with a different failure) has not been run on either the writer or the fixture. Q102
requires the miss to be a named limit or a repair, never silence.

---

## Question verdicts

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Is each claim's do-nothing control RED at `1e8bfd87` and reachable with one command? | **holds** (C1, C2) with F2/F3 defects | C1: `c1-counter.py … --new-arm plain` → `forgeries_accepted=5 honest_accepted=3`, `EXIT=1`; C2: fixture vs base → `pass=4`, `EXIT=1`. Both are one command and both are red. But the receipts are not in the substance grammar (F2) and the two C1 counters diverge (F3). |
| 2 | Can a do-nothing round meet either target (a counter that would pass unchanged)? | **holds** (no) | C1: base accepts all 8 → the 5 forgery expectations fail; the always-refuse stub is rejected by the 3 honest rows, the always-accept stub by the 5 forgery rows (`stubs=REJECTED`). C2: base 4/8 < 8/8. |
| 3 | Is each target one concrete value re-derivable from committed bytes, with no universal clause? | **violates** (both) | C1: the claim states a universal property ("a claim's `Control:` receipt is bound …"), and the matrix does not pin the finding class (F4/F5). C2: the target contains a false value, `base=3` vs measured `4` (F1). |
| 4 | Are the two claims causally separable (does C1's counter read C2's files)? | **holds** (file level) | C1 reads `tools/souji-freeze-check.py` + `matrix/` fixtures + `build-matrix.py`; C2 reads `census/round-57/record-receipt.sh` + the writer. No shared file. Gap: the C2 writer's receipts are never fed to the C1 arm; if the L1 uses the writer to produce the C1 control receipt, separability breaks. |
| 5 | Is the freeze chronologically able to precede all after-data? | **conditional / violates as the wave stands** | HEAD `1e8bfd87`, no round-60 prereg committed; after-data (new-run, base-run) already exists pre-freeze; `.ufo/waves/` is gitignored and a force-add of the wave metadata would fire `DISPATCH-BEFORE-FREEZE`. Achievable only as A (controls) → B (prereg) → C (measurements), with the r57 disclosed-dry-run note. |
| 6 | Does either claim re-declare a rejected r56/r57/r58/r59 claim? | **C2 violates; C1 holds** | C2 re-declares rejected r57 C2 (same surface, same base recorder) without successor framing (F9). C1 is new ground (freeze checker substance arm), not r59's classification claim; it must not claim to repair the r59 Q99 grammar red. |
| 7 | Is the axis label the surface actually moved? | **C1 violates as written; C2 holds** | "calibration/capability" mixes an axis with a claim type; the surface is calibration (F10). C2 = operability, correct. |

---

## The single change that most reduces rejection risk

**Freeze the C2 base count at the measured `4/8` (naming `atomic-in-flight`, `kill-residue`,
`rev-short`, `instrument-absent`) instead of `3/8`.** The round's own control receipt already says
`pass=4`; a frozen `Target:` of `base=3` is false at the freeze commit and no after-data can repair it,
so the round would be rejected on a predicate it cannot meet. The companion mandatory fix (not a target
change, a receipt wrapper) is Finding 2: regenerate the C1 `Control:` receipt with
`instrument=`/`instrument_sha256=`/`rev=`/`command=` and the declared counter's digest — demonstrated to
give `findings=0` under both the base Q99 checker and the new arm.

---

## Named limits of this review

1. The wave tree is untracked and was being edited while I read it (the C2 fixture changed between two of
   my runs); all measurements above are pinned by the digests in the table. If the L1 integrates different
   bytes, re-run the two counters.
2. I did not run the candidate `--selftest` under a clean `TMPDIR`; I relied on the seat's
   `selftest-default.txt` / `selftest-substance.txt` (41/41, 12/12) and measured the matrix/candidate
   behavior directly instead.
3. The C1 class observation (F4/F5) is from my rebuild of the delivered matrix via `build-matrix.py`
   into scratch; the rebuilt hashes matched the delivered `expected.txt` (`BUILD_EXIT=0`).
4. `atomic temp+rename` (F6) is verified only by reading the writer's code paths; the fixture does not
   observe it.
5. No tool was installed or updated.
