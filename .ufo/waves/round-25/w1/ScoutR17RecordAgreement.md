# ScoutR17RecordAgreement — residuals R15/R17/R19 (r23 record-agreement counter)

Seat: L1Souji25.ScoutR17RecordAgreement (scout, leaf). Lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`
(working tree HEAD `6e4737e`; tool and fixture blobs are identical at both). Scratch
`/var/tmp/souji-r25-ScoutR17RecordAgreement/`. git 2.56.0, Python 3.14.8, every run `python3 -B`.
Lane access was read-only (`git show/log/ls-tree/rev-parse/hash-object`, plus one `--no-worktree`
instrument run). This report is the only file written in the lane.

## Status

STATUS: PARTIAL — two of the brief's premises are false at the base revision, and its case set
conflicts with the preregistered witness.

- The trailing-shadow hole is real, but it is in the r23-era tool blob, not the one at `a6d2d15`.
  The code half of R17 was fixed in r24 (`315422b`, R24-M12).
- The record names the shape and the fix: the r24 lesson and SCORECARD do. The r23 lesson is the
  part still uncorrected.
- The brief's three cases (token-moved, decoy, trailing-shadow) **cannot** give "fixed scores 15/15".
  The fixed tool fails the decoy case, because R15 is still open in the code.
- A three-case set that does give old 14/15 → fixed 15/15 is measured below. It kills more mutants
  than W2R23F4's set does.

## Axes

- **calibration:** the record says the hole is closed or open in ways that do not match the bytes.
- **coverage:** the committed fixture is blind to every fence and anchoring mutant.
- **operability:** the red arm has to name the right blob, or it is vacuous.

## Evidence

### E1 — which blob is "old"

| rev | `tools/souji-record-agreement.py` blob | sha256 | `counts_of` |
|---|---|---|---|
| `c872eec` (r23 final) | `3a90ddc6…` | `dd53c228…` | `COUNTS_RE.findall(text)`, then `matches[-1]` over the whole receipt |
| `315422b` = `a6d2d15` = HEAD | `716731f3…` | `41db9ca8…` | stdout section only (`:124-130`), then `matches[-1]` within it |

At `c872eec` the docstring says "Only the header region before the `--- stdout ---` fence is a
receipt's own claim", but the code does last-wins over the whole text. This is the R17
contradiction, confirmed. At `a6d2d15` the docstring (`:119-122`) describes the stdout section and
the code matches it. **There is no docstring contradiction to correct in the tool at the base.**
The peer seat `ScoutR17RecordAgreement-2` reached the same conclusion independently.

### E2 — `counts_of` probe (`probe.py`, direct call)

| receipt shape | old `dd53c228` | base `41db9ca8` |
|---|---|---|
| stdout `mismatches=7`, then `mismatches=0` after `--- stderr ---` | **`mismatches=0`** (shadow) | `mismatches=7` |
| counts only after `--- stderr ---` | **`mismatches=0`** | `None` (fails closed: receipt-malformed) |
| `# summary …mismatches=7` before the fence, stdout `=0` | `mismatches=0` | `mismatches=0` |

Fence edge probes on the base tool (`probe2.py`):
- **A `--- stdout --- ` fence with a trailing space** is not recognised. Parsing falls back to
  whole-text last-wins, and the post-stderr `mismatches=0` shadows stdout again. This fails open.
  It is a residual, though only a doctored receipt can produce it: the runner writes exact fences.
- CRLF fences are handled (`splitlines`).
- Two counts lines inside stdout resolve last-wins. That is consistent with the runner's
  `counts_line()`.

Lane run at the base: `tools/souji-record-agreement.py --rev a6d2d15… --no-worktree` prints
`keys=4 records=4 occurrences=17 mismatches=0`, rc 0. The committed r24 receipt
`census/round-24/records/r23-agreement-regress.out` reads `tool_sha256=41db9ca8…`,
`selftest=12/12`.

### E3 — the committed record at `a6d2d15`

- **Named:**
  - `corpus/lessons/round-24.md:160` (R24-M12 row: hole, witness, fix, three fixture variants).
  - `:334-339` (fix landed; "an extended fixture scores 14/15 on the old tool and 15/15 on the fix
    … the three extra fixture cases are not committed this round (routed to r25)").
  - `:363`.
  - `SCORECARD.md:225` ("R15 (K1 decoy) and R17 (K1 trailing shadow)" carried open).
- **Not corrected:**
  - `corpus/lessons/round-23.md:144-146` still says last-wins means "a pre-fence summary line
    cannot shadow the measured output. All three holes now have fixture cases (selftest 12/12)".
    The file is 229 lines and has no later append-only correction of those lines.
  - The 12-case committed fixture still has no fenced receipt, so it cannot see the hole.
- **Stale wording:** `SCORECARD.md:225` calls R17 open as a whole. Only its fixture half and its
  r23-lesson half are open.

### E4 — fixture × tool matrix (`matrix.txt`)

Each scratch fixture is the committed fixture `eda4fafa…` with `SCRATCH_ROOT` repointed and cases
appended. Every case builds its own repo, so cases are independent.

Tools:
- `old` = `dd53c228`
- `base` = `41db9ca8`
- Mutants of `base`:
  - `first`: `matches[0]`
  - `noguard`: the `receipt-rev-object` `elif` deleted
  - `wholetext`: findall over `text`, not `region`
  - `nostderr-end`: the region runs to EOF
  - `no-occ-absent`: `if seen == 0` disabled

| fixture (cases 13-15) | old | base | first | noguard | wholetext | nostderr-end | no-occ-absent |
|---|---|---|---|---|---|---|---|
| committed 12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| **W2R23F4 set**: post-stderr-shadow, pre-fence-summary, receipt-rev-object | **14/15** (13) | **15/15** | 15/15 | 14/15 (15) | 14/15 (13) | 14/15 (13) | 15/15 |
| **brief set**: token-moved, decoy-other-rev, post-stderr-shadow | 13/15 (14,15) | **14/15 (14)** | 14/15 | 14/15 | 13/15 | 13/15 | 13/15 (13,14) |
| **recommended**: post-stderr-shadow, receipt-rev-object, token-moved | **14/15** (13) | **15/15** | 15/15 | 14/15 (14) | 14/15 (13) | 14/15 (13) | 14/15 (15) |

`control=FALSE-GREEN-REJECTED` holds on every run.

The 19-case superset adds post-stderr-wrong-trailer (green) and stderr-only (receipt-malformed).
Results: base 18/19 (fails decoy only), old 15/19, and `first` survives every case.

## The three cases to add

These meet the preregistered witness "three new fixture cases (14/15 → 15/15)". Expectations use
the fixture's own `case_k1` helper.

1. **`post-stderr-shadow`** (R17 trailing shadow). The tip's K1 receipt is rewritten fenced:
   `rev=<measured>` / `--- stdout ---` / `AFTER_TUPLE_WRONG` / `--- stderr ---` / blank /
   `AFTER_TUPLE`. The SCORECARD line is unchanged.
   - Expect `rc!=0 K1 value-disagree>=1`.
   - Kills `wholetext` and `nostderr-end`. This is the case the old tool fails.
2. **`receipt-rev-object`** (W2K1 F3 guard, still unwitnessed). The receipt `rev=` and the
   SCORECARD token both become `WRONG_REV` (`"ab"*40`, no such commit).
   - Expect `rc!=0 K1 receipt-rev-object>=1`.
   - Kills `noguard`.
3. **`token-moved`** (R19 "token-moved" shape). The SCORECARD token moves to `WRONG_REV` **and**
   the tuple becomes `AFTER_TUPLE_WRONG`, so no tuple is bound to the receipt rev.
   - Expect `rc!=0 K1 occurrence-absent>=1`.
   - Kills `no-occ-absent`, which survives the committed 12 cases and the W2R23F4 set.
   - This differs from the existing `rev-disagree` case, which keeps the right tuple and asserts
     only `rev-disagree`.

Red arm, measured:
- Old blob `c872eec:tools/souji-record-agreement.py` (sha256 `dd53c228…`): **14/15**, failing
  post-stderr-shadow, rc 1.
- Fixed blob at `a6d2d15` (sha256 `41db9ca8…`): **15/15**, rc 0.
- Both runs: `control=FALSE-GREEN-REJECTED`.

The W2R23F4 set reproduces the same 14/15 → 15/15. Its third case, `pre-fence-summary`, is a green
control that kills no mutant of the current code (`first` and `wholetext` both pass it), so swap it
for `token-moved`.

## Attacks on "plain fixture extension"

1. **The red arm can be vacuous.** Taking "OLD tool blob at a6d2d15" literally, as the brief and the
   C1 prereg wording do, gives the fixed tool, which scores 15/15 on the new cases. The R17 red arm
   must name `c872eec:tools/souji-record-agreement.py` (blob `3a90ddc6…`, sha256 `dd53c228…`), and
   its receipt must be committed before after-data.
2. **There is no tool docstring to correct.** The prereg's "record-agreement docstring correction"
   has no target in the tool at the base. What actually needs correcting:
   - The **fixture** docstring. `:38-39` "Cases 2-8 are the always-zero control" is stale for 15
     cases. The header must also say that the K1 receipt payload is unfenced while the new cases
     are fenced.
   - An **append-only** note under `corpus/lessons/round-23.md:144-146` citing R24-M12 and
     `315422b`.
3. **The decoy case cannot be in a 15/15 set.** `decoy-other-rev` (wrong calibration tuple bound to
   another rev, plus a correct prose decoy at the receipt rev) gets `mismatches=0` rc 0 on the fixed
   tool. That is W2K1 F2 = R15, still open. Adding it with a red expectation breaks 15/15. Adding it
   with a green expectation would make the fixture certify a known false green. Closing R15 means
   anchoring K1 to the calibration row, which is a predicate change. It needs its own claim with its
   own before/after, not a counter edit inside a fixture extension.
4. **The closure must not take credit for the r24 fix.** The fixture cases are r25's witness. The
   code fix is r24's (`315422b`). Any SCORECARD/LOG line closing R17 should say that and leave R15
   open.
5. **The within-section first/last choice is unwitnessed.** The `first` mutant survives all 19 cases.
   A fourth case (two counts lines in stdout, last one true, matching the runner's `counts_line()`)
   would pin it. It lies outside the frozen three, so disclose it or carry it forward.
6. **The fence spelling fails open** (E2): a trailing-space fence falls back to whole-text
   last-wins. Disclose it. Fixing it (e.g. `.rstrip()` on fence lines, or refusing a near-fence) is a
   code change, so it needs its own before/after.
7. **R19 is only partly addressed.** The lesson's "28 uncovered mutants" figure was measured on the
   r23 tool. These three cases kill 4 of the 5 mutants probed here. Remeasure before claiming any
   R19 count.

## Disposition

| residual | actable as a fixture extension | open after it |
|---|---|---|
| R17 | yes: post-stderr-shadow plus fixture-docstring and r23-lesson append-only notes (the code was fixed in r24) | the trailing-space fence edge (disclose) |
| R19 | partly: token-moved and receipt-rev-object | the `first` mutant and the rest of the 28-mutant figure |
| R15 | no: the fixed tool fails the decoy case | all of it (needs K1 row anchoring, a separate claim) |

## Peer coordination

The peer seat `L1Souji25.ScoutR17RecordAgreement-2` has the same brief and reported, over IRC,
writing three files into this scratch directory briefly and then moving them out. I checked
afterwards: `fixture-base.py`, `tools/old-c872eec.py` and `tools/base-a6d2d15.py` still match their
extracted blob hashes (`eda4fafa…`, `dd53c228…`, `41db9ca8…`). The peer's report is
`ScoutR17RecordAgreement-2.md`.

## Tooling

Nothing was installed or updated; this used the host's git 2.56.0 and Python 3.14.8.
Scratch is kept for reproduction: `mk.py`, `probe.py`, `probe2.py`, `fx-*.py`, `tools/`,
`matrix.txt`, `out-*.txt`, `hashes.txt`. The fixtures' own `run/` subtrees were trap-cleaned. Remove
the scratch with `rm -rf /var/tmp/souji-r25-ScoutR17RecordAgreement`.
