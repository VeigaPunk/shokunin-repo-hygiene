# MutR17Survivors (mutation-tester, wave 2) — R17 15-case fixture mutation set

Seat: L1Souji25.MutR17Survivors (mutation-tester, leaf). Attacks: the W1 R17 record-agreement fixture extension (three new cases 13–15) and the R15 cross-revision decoy residual. All runs in isolated scratch `/var/tmp/souji-r25-MutR17Survivors/`; no lane writes, no commits, read-only git only.

## Status

STATUS: PASS — the three new fixture cases are live and discriminate exactly as claimed:

- case 13 `post-stderr-shadow` kills the **whole-text parse** mutant (and the old r23 blob `dd53c228`);
- case 14 `stdout-two-line` kills the **matches[0]** mutant;
- case 15 `receipt-rev-object` kills the **removed rev-object guard** mutant.

The **R15 cross-revision decoy** shape survives every tool version (pristine, old, base, all three mutants): rc=0, mismatches=0, false green. It is not covered by the fixture — R15 remains open (matches RevR17-2 probe case 18 and the integrated draft's own header note).

## Scope limit

- Probe bytes: lane working-tree W1 integration draft — `tools/souji-record-agreement.py` sha256 `ec5b809d5e21…` (docstring-only delta vs committed base; `git diff` touches only module/docstring lines) and `tests/fixtures/r23-record-agreement.py` sha256 `8b4c23e5a75f…` (committed fixture `eda4fafa…` + exactly three cases 13–15; `git diff` confirms only those additions).
- Binaries: base/HEAD committed tool blob `41db9ca8…` (a6d2d15 == 6deb535); old r23 pre-fix blob `c872eec:tools/souji-record-agreement.py` = `dd53c228…`.
- Fixture runs used byte-identical copies with `SCRATCH_ROOT` redirected to `/var/tmp/souji-r25-MutR17Survivors/fx-scratch` (the committed fixture hard-codes the shared `/var/tmp/souji-r23-ExecFixtureAgreement` and `rmtree`s it at start — RevR17-2 finding 6 collision risk).
- No tool installs made.

## Test command (exact)

```
python3 -B /var/tmp/souji-r25-MutR17Survivors/fx/r23-record-agreement.py --tool <tool-copy> --keep
```

The fixture drives the instrument as `python3 -B tools/souji-record-agreement.py --root <scratch-repo> --rev <tip> --json <case-N.json>` (15 case repos built under scratch per run).

## Mutants (scratch only; all py_compile-clean)

| mutant | defect | sha256 |
|---|---|---|
| pristine (draft) | none — W1 draft bytes | `ec5b809d5e21…` |
| mut-first | `counts_of`: `m = matches[-1]` → `m = matches[0]` (first-wins within stdout section) | `5b11bfcbb30b…` |
| mut-whole | `counts_of`: fenced-region selection removed → `region = text` (whole-text parse, last-wins globally) | `dc0dc62aaff3…` |
| mut-noguard | `Report.k1`: `elif git … cat-file -e {rev}^{commit}` guard deleted (no rev-object check) | `9140cbb604b0…` |

## Scores — R17 15-case fixture (cases 1–15)

| tool | selftest | rc | failing case(s) |
|---|---|---:|
| pristine (draft) | 15/15 | 0 | — |
| base/HEAD (`41db9ca8`) | 15/15 | 0 | — |
| old r23 (`dd53c228`) | 14/15 | 1 | 13 |
| mut-first | 14/15 | 1 | 14 |
| mut-whole | 14/15 | 1 | 13 |
| mut-noguard | 14/15 | 1 | 15 |

`control=FALSE-GREEN-REJECTED` on every run (green controls 10 and 14 observed passing).

### Which new case kills which mutant (exact failing lines)

- **case 13** (`post-stderr-shadow`): pristine `got=rc=1 mismatches=1 keys=4 [K1/value-disagree]`; mut-whole `got=rc=0 mismatches=0 keys=4 -> FAIL`; old `got=rc=0 mismatches=0 keys=4 -> FAIL`.
- **case 14** (`stdout-two-line`): pristine `got=rc=0 mismatches=0 keys=4` (green); mut-first `got=rc=1 mismatches=1 keys=4 [K1/value-disagree] -> FAIL`.
- **case 15** (`receipt-rev-object`): pristine `got=rc=1 mismatches=1 keys=4 [K1/receipt-rev-object]`; mut-noguard `got=rc=0 mismatches=0 keys=4 -> FAIL`.

## R15 cross-revision decoy (probe case 16, added to a second scratch fixture copy)

Shape (RevR17-2 probe case 18): the calibration row is corrupted — wrong tuple (`AFTER_TUPLE_WRONG`) anchored to another **real** revision token (the tip commit), while a decoy line quotes the true tuple at the receipt rev so K1 `seen` stays satisfied. Fixture oracle: red (any K1 mismatch, rc≠0).

| tool | case 16 result |
|---|---|
| pristine | `got=rc=0 mismatches=0 keys=4 -> FAIL` (false green) |
| old / base / mut-first / mut-whole / mut-noguard | same — `rc=0 mismatches=0 -> FAIL` |

Every tool version false-greens the decoy: K1 ignores a tuple whose value disagrees with the receipt when it is bound to any other revision (falls through the `bound==rev` / `value==receipt` / `unbound` branches), while the decoy supplies `seen`. **Survives**: the R15 decoy-anchor shape is not killed by any tool or fixture case — it remains an open, disclosed residual (draft fixture header: "R15 … stays a disclosed limit: no fixture case is added for it").

## Findings

1. The three new cases 13/14/15 are discriminating and non-vacuous: each kills exactly its target mutant, and all three pass on pristine (15/15).
2. Red-before witness holds only against the old r23 blob `dd53c228` (14/15, case 13); the a6d2d15/HEAD blob `41db9ca8` already scores 15/15 — consistent with RevR17-2 finding 2 (validate red receipts against `c872eec`/`dd53c228`, never `41db9ca8`).
3. Case 14 discriminates mut-first only because the in-stdout decoy (`stdout-two-line`) is present; ExecutiveR17-2's earlier variant let mut-first live (RevR17-2 Matrix B) — the integrated draft carries the discriminating shape.
4. R15 decoy-anchor survives everywhere; fixing it needs a code-level predicate/anchor change (K1 bound-to-rev parsing), not a fixture case.

## Attack log

1. Byte-copied draft tool + fixture to scratch (sha256 above); verified `git diff` HEAD-vs-worktree = 3 fixture cases only, tool = docstring-only.
2. Patched `SCRATCH_ROOT` in scratch copies; ran 15-case fixture × 6 tool variants (logs `/var/tmp/souji-r25-MutR17Survivors/logs/run-*.log`, removed with scratch).
3. Built decoy-anchor case (variant + oracle) on a second scratch fixture copy; ran × 6 variants.
4. No counter attack on the fixture itself; no tool installed. Lane bytes untouched; scratch removed before finish.
