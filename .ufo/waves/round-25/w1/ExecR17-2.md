# ExecR17-2 — residuals R15/R17/R19: record-agreement docstring + three fixture cases (adjudicated set)

Seat: L1Souji25.ExecR17-2 (leaf). Lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`, HEAD `6e4737e`.
No edits to `tools/` or `tests/`. Scratch `/var/tmp/souji-r25-ExecR17-2b/` (removed at the end).
Duplicate-dispatch note: sibling `ExecR17` owns the shared draft paths and `w1/ExecR17.md`; my drafts
are `w1/ExecR17-2-*.py` and this report is `w1/ExecR17-2.md`.

## Status
STATUS: PASS.

Per the L1 adjudication (ScoutR17RecordAgreement-2): red arm = `c872eec:tools/souji-record-agreement.py`
(sha `dd53c228…`, the pre-fix blob), green arm = committed tool / draft. Measured:
- Red (pre-fix `c872eec`): **selftest=14/15**, failing case 13 `post-stderr-shadow`
  (`rc=0 mismatches=0` false green), final line `control=FALSE-GREEN-REJECTED`, **rc=1**.
- Base (committed HEAD tool, sha `41db9ca8…`, identical to the `a6d2d15` blob): **15/15 rc 0**.
- Draft tool (docstring-only): **15/15 rc 0**.
- Committed 12-case fixture stays 12/12 under the pre-fix tool and under every mutant (blindness baseline).

The L1-adjudicated case set is exactly:
1. `post-stderr-shadow` — fenced receipt stdout `mismatches=7` + trailing `mismatches=0` after the
   stderr fence; expect K1 `value-disagree` (kills the old tool and whole-text parse).
2. `stdout-two-line` — wrong `# summary` before the stdout fence + wrong-then-true counts inside
   stdout; expect green (last stdout line wins; kills first-match `matches[0]`).
3. `receipt-rev-object` — receipt `rev=` and SCORECARD token both name a non-commit; expect K1
   `receipt-rev-object` (kills the guard-removed mutant).

R15 (K1 decoy-line anchoring) stays a **disclosed limit**: no fixture case added; the tool docstring
makes no R15 coverage claim.

## Evidence
All arms ran sequentially (`python3 -B`), each with a fresh `SCRATCH_ROOT` under
`/var/tmp/souji-r25-ExecR17-2b/fx-*` (the committed fixture wipes its own shared scratch on start).

| arm | tool (sha256) | extended fixture (15) | committed fixture (12) |
|---|---|---|---|
| red | pre-fix `c872eec` (`dd53c228…`) | **14/15**, case 13 FAIL, rc=1 | 12/12 |
| base | committed HEAD (`41db9ca8…`) | 15/15 rc 0 | 12/12 |
| green | draft `ec5b809d…` | **15/15 rc 0** | 12/12 |
| `mut-first` (`matches[0]`) | on old base | 14/15, case 14 FAIL | 12/12 |
| `mut-noguard` (rev-object elif → `elif False`) | on HEAD | 14/15, case 15 FAIL | 12/12 |
| `mut-nofence` (whole-text region) | on HEAD | 14/15, case 13 FAIL | 12/12 |

Each of the three new cases kills a distinct mutant that the committed 12-case fixture lets through
(12/12 for all three mutants), so each is a real witness.

`post-stderr-shadow` detail (red arm, case 13):
`got=rc=0 mismatches=0 keys=4` — exactly the round-24 W2R23F4 false pass, reproduced on the pre-fix blob.

R15 probe (probe copy, cases 16-17, not a deliverable): both R15 shapes still escape the committed
tool (`rc=0 mismatches=0` for row-dropped+decoy, and for wrong-calibration-bound-to-other-rev+decoy).

### Draft files
| file | sha256 | change |
|---|---|---|
| `w1/ExecR17-2-souji-record-agreement.py` | `ec5b809d…` | docstring only (K1 note line 11 + new "Receipt counts" paragraph lines 28-34). Code AST-identical to HEAD once docstrings are stripped. No R15 coverage claim. |
| `w1/ExecR17-2-r23-record-agreement.py` | `8b4c23e5…` | 12 committed cases unchanged (`git show HEAD:tests/fixtures/r23-record-agreement.py | diff -` touches only additions), plus cases 13-15 and a docstring note. |

Receipts (raw runs incl. `rc`, tool/fixture sha256, command, UTC):
`w1/ExecR17-2-receipts/`: `red-prefix-c872eec.txt`, `base-head.txt`, `green-draft.txt`,
`committed12-old-c872eec.txt`, `committed12-base.txt`, `mut-first-ext15.txt`, `mut-first-c12.txt`,
`mut-noguard-ext15.txt`, `mut-noguard-fixed-ext15.txt`, `mut-noguard-c12.txt`,
`mut-nofence-ext15.txt`, `mut-nofence-c12.txt`, `probe-r15.txt`.

## Findings
1. **The inherited red-arm premise in the brief was wrong** (`a6d2d15` already carries the r24 fix,
   sha `41db9ca8…`, scores 15/15). The L1 adjudication's correction is validated: `c872eec` blob
   (sha `dd53c228…`) is the red arm and gives 14/15. See also `ScoutR17RecordAgreement.md` F1.
2. **Docstring wording deviation** (kept intentionally): the brief's "last non-empty stdout line"
   is not what the code does — `counts_of` takes the last *counts-shaped match* inside the stdout
   section, which need not be the last line (a label line may follow). The draft says exactly that
   and notes it need not be the last stdout line. `[INFERENCE]` none; this is a recorded behavior of
   `tools/souji-record-agreement.py:116-135`.
3. **R15 remains open** (probe): K1 is not anchored to the calibration row; a correct decoy line
   elsewhere still satisfies `seen>=1`. Disclosed; the draft makes no R15 claim.
4. **Missing append-only correction** (for the L1 to land): `corpus/lessons/round-23.md:144-146`
   still says last-wins closed shadowing; per r24 `W2R23F4` and R24-M12, a post-fence counts line
   still shadowed stdout until `315422b`'s region fix. The lesson needs an append-only note citing
   R24-M12 / `315422b` and naming the three new fixture cases (routed to r25).
5. **Duplicate-seat coordination**: the sibling `ExecR17` and I both built fixtures for the same
   three adjudicated cases; sibling owns the shared draft paths and `ExecR17.md`; my prefixed drafts
   + report are independent and equivalent in outcome (14/15 → 15/15).

## Attack log
None (executor seat; no adjudication of claims). The red-arm correction above is a brief-fix note,
not an attack on a frozen predicate. No tools installed or updated.
