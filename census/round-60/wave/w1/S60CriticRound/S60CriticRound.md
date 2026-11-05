# S60CriticRound — pre-freeze falsification of the round-60 admission conjunction

Seat: S60CriticRound (critic, leaf). Date: 2026-11-04. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`,
read-only. Lane HEAD at review start: `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`.

**Freeze timing.** The round froze while this review was running: the L1 committed
`3b5525099356e15ff9d17b7fbd2835c2d3512eee` (instruments + fixtures) at 21:04:17-03:00 and
`2670e96af1b81c7aa793acc34d40361b4beecff8` (control receipts + preregistration) at 21:05:50-03:00;
local == `origin/master`. Every finding below is re-verified against the **frozen bytes at 2670e96a**,
not against the earlier wave deliveries. Findings 1–2 of my pre-freeze draft (the wave text's `base=3/8`
and the unbounded-shape control receipts) were repaired by the freeze; they are recorded under
"Repaired by the freeze" so the L1 does not re-fix them. The surviving findings are numbered from 1.

No lane file, index, jj state or production path was written. Fixtures were built only under
`/fast/scratch/hyaku/souji-r60/S60CriticRound/` (removed after the evidence was copied into the delivery
dir).

Method: read the frozen rules (QUALITY.md Q99/Q100/Q102/Q120, fleet AXES.md, SCORECARD.md), the r57/r59
preregistrations and the r59 lessons/verifier spot-check, the wave spec, and the frozen commit; then ran
the frozen counter, the frozen fixture, both freeze checkers and the arm against synthetic records, and
rebuilt the frozen matrix to observe the emitted finding classes.

Frozen artifacts measured (sha256):

| artifact at 2670e96a | sha256 |
|---|---|
| `census/round-60/preregistration.txt` | `d4bd0b8f3f1f5dce26a826027024a8d8d71bd506e4bdf46a388349e4555332af` |
| `census/round-60/c1-counter.py` (declared Counter) | `76f35c2f33e4f87f120fc0675b8502c47db335c993c8b8c68ea04ae860106d9b` |
| `census/round-60/c1-matrix.tsv` (Population) | `7973d52030f9bf7d34867c2a46527708556cf82765c1e5b4a5f087bcb310132d` |
| `tests/fixtures/r60-receipt-write.py` (declared Counter) | `d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114` |
| `census/round-60/c2-cases.tsv` (Population) | `727c5d71225b6a40a041e4c6cdb69f12f3a1fa19f170c3922ae88d2e520e42c7` |
| `census/round-60/controls/c1-do-nothing.txt` | `01915bff8aaa296a535f12b86aa8763cf62ace57e487b42a739f29c8de262d6c` |
| `census/round-60/controls/c2-do-nothing.txt` | `dfd2234c052cb0620721a3924d97c3ac17b047dd71d9fecec8971e8175b032ec` |
| `tools/souji-freeze-check.py` @ `1e8bfd87` (base) | `d1ca06fd0fb21d4c7a8452dbbc879f2ecf63ffaaf65378efa3c512e4dbfca364` |
| `census/round-57/record-receipt.sh` (C2 base, unchanged since r57) | `84148011abc9574048fc77e02427bee9010850418beeeaaa1babe59185109aa9` |

The four field digests were re-derived from the frozen blobs and match the prereg's
`Counter:`/`Population:` values exactly (see `evidence/frozen-state.txt`).

---

## Surviving findings

### 1. Q120 chronology: the control receipts are added at the freeze commit, and the frozen prereg says they were committed earlier — VIOLATES

The frozen prereg opens with:

> Controls were executed and committed at `3b5525099356e15ff9d17b7fbd2835c2d3512eee`, strictly before
> this freeze commit; both are red there (EXIT=1) and both are written in the bound shape the C1 arm
> requires.

The commit graph contradicts the first clause:

```
$ git ls-tree -r --name-only 3b552509 census/round-60
census/round-60/build-matrix.py
census/round-60/c1-counter.py
census/round-60/c1-matrix.tsv
census/round-60/c2-cases.tsv
census/round-60/matrix/...        (no controls/ directory)
$ git log --oneline -- census/round-60/controls/
2670e96a round-60: freeze the two claim predicates after executed red controls
$ git show --stat --oneline 2670e96a
 census/round-60/controls/c1-do-nothing.txt | 15 ++++++++++
 census/round-60/controls/c2-do-nothing.txt | 24 ++++++++++++++
 census/round-60/preregistration.txt        | 21 +++++++++++++++
```

Both control receipts are **added by the freeze commit itself**. Q120 requires the executed controls
"in a commit strictly preceding predicate freeze"; the freeze commit is the oldest commit that adds the
prereg (Q99), i.e. `2670e96a`. The receipts' `rev=3b552509…` is the revision they were *measured at*
(a strict ancestor, so the C1 arm's own `rev=` check passes), not the commit that added them. The
prereg's provenance sentence is therefore false, and this is the r59 chronology defect repeated in a new
form — r59's verifier tested exactly this with `git ls-tree -r 74455b72 census/round-59` and found the
controls there; the same test on `3b552509` finds none.

The new arm does not catch it: `--substance` on the frozen record returns `SUMMARY claims=2 findings=0`,
`EXIT=0`, because it validates the receipt's `rev=` line and never asks which commit added the receipt.
So the round lands an instrument that cannot enforce the rule the round claims to be about.

Rule: Q120 ("retain executed … controls … in a commit strictly preceding predicate freeze"; "a later
replay never repairs the chronology"). The freeze is pushed (`git rev-parse HEAD` ==
`git rev-parse origin/master` == `2670e96a`), so the commit cannot be split without rewriting a pushed
freeze, and the frozen bytes cannot be edited.

### 2. The C1 matrix does not assert the finding class it names — VIOLATES (Q100)

The frozen matrix's `class` column is `honest|forgery`; the frozen counter validates only that value and
compares `accept|refuse`. The seat spec names a class per forgery. Measured on the frozen matrix
(rebuilt from the frozen `build-matrix.py` and `matrix/`, hashes matching the pinned `expected.txt`):

```
$ python3 -B tools/souji-freeze-check.py --root <frozen case> --prereg pre.txt --rev <freeze> --substance
FINDING C1 CONTROL-REV-INVALID ctl.txt rev='freezemark' does not resolve to a commit
SUMMARY claims=1 findings=1
```

The case named `CONTROL-REV-NOT-BEFORE-FREEZE` fires a *different* class and still counts as a pass.
A candidate arm that refuses all five forgeries with one wrong class passes the matrix. The Target
(`new_forgeries=0 new_honest=3`) is a refusal count, not a class match; the class is the substance Q100
asks for and it is unasserted. Correction: add the expected finding id to the matrix and compare the
emitted `FINDING` lines, or name this as a limit and do not claim class discrimination.

### 3. `forgery-rev-at-freeze` is not the specified input — VIOLATES (Q120 exact input)

A commit tree cannot contain its own hash, so the case uses the lightweight tag `rev=freezemark`
(frozen `matrix/forgery-rev-at-freeze/ctl.txt`). The arm rejects the tag as non-40-hex
(`CONTROL-REV-INVALID`) before ancestry is ever evaluated; a candidate that resolved the tag would fire
`CONTROL-REV-NOT-BEFORE-FREEZE`. The frozen `expected.txt` also pins `control_rev=14ab27ee…` (the
ancestor), not the freeze `dc1f00d9…`, so the delivered expectation contradicts the case's name. The case
cannot test "rev == the freeze commit" as the spec states. Correction: document the substitution as a
limit, or replace it with a constructible non-ancestor (orphan) case and say so.

### 4. C2's "atomic temp+rename" is not established by its fixture — VIOLATES (Q100)

Frozen fixture `tests/fixtures/r60-receipt-write.py` (`d5291501…`), run against the base recorder:

```
CASE 3 atomic-in-flight pass
CASE 4 kill-residue pass
SUMMARY cases=8 pass=4 fail=4 control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED
EXIT=1
```

Cases 3 and 4 **pass for the base recorder**, which creates no temp file at all and writes `OUT`
directly after the command returns. They test "OUT absent before the command completes" and "no residue
after SIGKILL", not temp+fsync+`os.replace`. The candidate's atomicity is real in its code (`mkstemp`
beside OUT, `fsync`, `os.replace`, dir fsync, SIGTERM/SIGINT cleanup), but the fixture never observes it.
The claim's operability surface is therefore partly code-read, not measured. Correction: name it a limit,
or add a case that observes the temp path during the final write.

### 5. C1's "substance" is bytes, not execution — NAMED LIMIT (Q100 shim rule)

The arm binds `instrument_sha256` to the Counter blob and `rev` to an ancestor; it never runs the counter.
A receipt claiming a run that never happened passes if the bytes match (the reviewer's
`c-never-executed` case: base accept; contract "bytes only"). Q100's execution-count shim is absent. The
claim must not claim execution authenticity; the candidate's NOTES.md limit 3 already says the digest
binds bytes.

### 6. C2 re-declares the rejected r57 C2 without successor framing — VIOLATES (Q120)

r57's C2 was "a receipt must bind the revision it was measured at", recorder
`census/round-57/record-receipt.sh`, 8-case fixture — the same surface and the same base file as r60's
C2. r57 is **rejected-harmed** (`corpus/lessons/round-57-verifier-spotcheck.md:12,23,139`; r59 lessons
"Prior r56/r57 rejected-harmed … remain unchanged"). Q120 permits a successor only with the executed
controls in a commit strictly before the freeze; the frozen prereg names neither the r57 rejection nor
successor status. Combined with Finding 1, the successor's prerequisite is not met. Correction: declare
"successor to rejected r57 C2" in the round report (append-only) and cite the r57 rejection; the frozen
prereg cannot be edited.

### 7. Axis binding is absent from the freeze and mixed in the claim text — VIOLATES as written (AXES.md)

The frozen prereg has no `Axis:` line; the wave claim text says "C1 calibration/capability". Fleet
`AXES.md` defines six axes (depth, coverage, operability, freshness, calibration, adjacency);
"capability acquisition" is a claim *type* that "still lands a per-axis verdict, with the claim type
recorded in the round report". The lane owns calibration 7, operability 8, coverage 8
(`SCORECARD.md:3`); the surface C1 moves — a checker that refuses forged freeze records — is calibration.
Correction: the round report records `Axis: calibration` / `Claim type: capability acquisition` for C1 and
`Axis: operability` / capability acquisition for C2. C2's operability label is correct.

### 8. C2 dirty-tree vacuity and the missing Q102 audit — NAMED LIMITS

`.ufo/waves/` is gitignored (`git check-ignore -v .ufo/waves/round-60/w1-spec.json` →
`.gitignore:1:.ufo/waves/`), so `git status --porcelain` in the lane is empty even with the whole wave
tree present; the dirty-tree refusal is exercised only in the synthetic fixture repo. The fixture's
cases 3/4 depend on wall-clock offsets (0.3 s, 0.4 s) and its case names are deterministic; Q102's
hidden-case audit (opaque names, fresh salts, CRLF, spaces, absent keys, a second claim with a different
failure) has not been run on either the writer or the fixture. Q102 requires the miss to be a named
limit or a repair, never silence.

---

## Repaired by the freeze (recorded so they are not re-fixed)

- **Wave text `base=3/8` → frozen `pass=4`.** Both independent fixtures and the frozen
  `c2-do-nothing.txt` measure `pass=4 fail=4` (the four passing base cases are `atomic-in-flight`,
  `kill-residue`, `rev-short`, `instrument-absent`). The frozen C2 `Kill:` correctly says
  "the do-nothing arm … prints pass=4 and exits 1". The wave spec's `3/8` must not be repeated in the
  round report.
- **Control receipts in the bound shape.** Both frozen receipts carry `instrument=`,
  `instrument_sha256=`, `rev=`, `command=`; the frozen record returns `SUMMARY claims=2 findings=0`,
  `EXIT=0` under both the base Q99 checker and `--substance`.
- **One counter, one matrix.** The frozen Counter is `census/round-60/c1-counter.py` (`76f35c2f…`), not
  either delivered seat runner; the two wave matrices are superseded.
- **Both frozen targets verify** at `2670e96a`: C1 → `new_forgeries=0 new_honest=3 stubs=REJECTED`,
  `EXIT=0`; C2 → `pass=8 fail=0`, `EXIT=0`. The numeric claims are not the rejection ground.

---

## Question verdicts (at the frozen commit)

| # | Question | Verdict | Basis |
|---|---|---|---|
| 1 | Is each claim's do-nothing control RED at `1e8bfd87` and reachable with one command? | **holds** | C1 `c1-do-nothing.txt`: `new_forgeries=5 new_honest=3`, `EXIT=1`; C2 `c2-do-nothing.txt`: `pass=4`, `EXIT=1`. Both carry the exact argv and the binding lines; both are one command. |
| 2 | Can a do-nothing round meet either target (a counter that would pass unchanged)? | **holds** (no) | The do-nothing arms fail both targets (`new_forgeries=5` vs 0; `pass=4` vs 8); the always-accept and always-refuse stubs are both rejected. |
| 3 | Is each target one concrete value re-derivable from committed bytes, with no universal clause? | **holds at the frozen `Target:` lines** | C1: `new_forgeries=0 new_honest=3` + `stubs=REJECTED`; C2: `pass=8 fail=0` + both stubs rejected. Re-derived above. The class is not pinned (Finding 2), but the frozen Target does not claim it. The wave text's universal phrasing ("a claim's `Control:` receipt is bound …") is not in the frozen predicate. |
| 4 | Are the two claims causally separable (does C1's counter read C2's files)? | **holds** | C1 reads `census/round-60/c1-counter.py`, `c1-matrix.tsv`, `matrix/`, `tools/souji-freeze-check.py`; C2 reads `tests/fixtures/r60-receipt-write.py`, `tools/souji-receipt-write.py`, `census/round-57/record-receipt.sh`. No shared file; neither control receipt names the other claim's instrument. |
| 5 | Is the freeze chronologically able to precede all after-data? | **violates** | The freeze precedes the after-data (`census/round-60/records/` is untracked, committed after), but the control receipts are added *at* the freeze commit `2670e96a`, not strictly before (Finding 1); the prereg's "committed at 3b552509" is false. |
| 6 | Does either claim re-declare a rejected r56/r57/r58/r59 claim? | **C2 violates; C1 holds** | C2 re-declares rejected r57 C2 (same surface, same base recorder) without successor framing (Finding 6). C1 is new ground (freeze-checker substance arm), not r59's classification claim; it must not claim to repair the r59 Q99 grammar red. |
| 7 | Is the axis label the surface actually moved? | **violates as written** | No `Axis:` line in the freeze; the claim text's "calibration/capability" mixes an axis with a claim type (Finding 7). The surface is calibration; C2's operability is correct. |

---

## The single change that most reduces rejection risk

**Land the round report as an honest-stop that names the control-adding commit `2670e96a` and replaces
the prereg's "committed at 3b552509" provenance with the measured graph fact** — no edit of the frozen
prereg, no re-freeze, no backdated control. The freeze is already pushed and the defect is in the commit
graph, so this is the only change that can move the verdict from *reject* to *rejected-honest-stop*
(the r59 outcome for exactly this defect) rather than leave a false provenance claim in a frozen record.
The smallest safe *instrument* correction, for the next round, is the same rule mechanised: in
`--substance`, require the commit that adds the `Control:` receipt (`git log --diff-filter=A` on the
receipt path, the same `freeze_rev` logic the tool already uses for the prereg) to be a strict ancestor
of the freeze commit; the frozen record would then be red, and the defect could not be hidden.

---

## Named limits of this review

1. The freeze landed mid-review; all findings are pinned to `2670e96a` and the digests above. If the L1
   lands further commits, re-run the two counters (`evidence/frozen-state.txt` has the exact argv).
2. I did not re-run the candidate `--selftest` under a clean `TMPDIR`; I ran the frozen counter, the
   frozen fixture and both checkers directly, which is the stronger measurement.
3. The class observation (Finding 2) is from rebuilding the frozen matrix with the frozen
   `build-matrix.py` into scratch; the rebuilt hashes matched the pinned `expected.txt`
   (`BUILD_EXIT=0`).
4. `atomic temp+rename` (Finding 4) is verified only by reading the writer's code paths; the fixture does
   not observe it.
5. No tool was installed or updated.
