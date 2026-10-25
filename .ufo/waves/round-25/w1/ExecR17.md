# ExecR17 — residuals R15/R17/R19: record-agreement docstring + three fixture cases

Seat: L1Souji25.ExecR17 (leaf). Lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`, HEAD `6e4737e`.
The seat did not edit `tools/` or `tests/`. Scratch was `/var/tmp/souji-r25-ExecR17/` and has been removed.

## Status
STATUS: DONE, with one correction to the brief that the L1 must take into account.

The red-before witness (14/15 → 15/15) holds against the **pre-fix** tool blob `3a90ddc`
(sha256 `dd53c228…`, the tool at `c872eec`, i.e. the one that W2R23F4 scored). It does **not** hold
against the blob the brief names. `a6d2d15:tools/souji-record-agreement.py` is blob `716731f`
(sha256 `41db9ca8…`). That blob already carries the r24 stdout-section fix from `315422b`, and on the
extended fixture it scores **15/15, rc 0**. Any receipt that uses the `a6d2d15` blob as the red arm
will come out green.

## Drafts
| file | sha256 | change |
|---|---|---|
| `w1/souji-record-agreement.py` | `04811c24…2f80d97` | docstring only (two hunks: K1 line 11, `counts_of` 119–127) |
| `w1/r23-record-agreement.py` | `40ddcbeb…df81ac57` | 12 committed cases unchanged, plus cases 13–15 and the docstring note |

Behaviour neutrality of the tool draft:
- The two files have equal ASTs once docstrings are stripped.
- `git diff --no-index` touches only docstring lines (`ExecR17/tool-docstring.diff`).
- On the lane, `--rev a6d2d15 --no-worktree` gives `keys=4 records=4 occurrences=17 mismatches=0` rc 0 for both the base tool and the draft. This matches `census/round-25/records/record-agreement-at-base.tsv`.

The new docstring states what the code does:
- Counts come only from the lines after the first exact `--- stdout ---` line, up to the next exact `--- stderr ---` line (or the end of the text).
- Text before the fence and text after the stderr fence are never counted.
- Within that section, the last counts-shaped match wins.

**Wording deviation from the brief:** the brief says "last non-empty stdout line". The code takes the
**last counts-shaped match in the stdout section**, which need not be the last line (a label line may follow it).
Writing "last line" would describe behaviour the code does not have, and the brief also requires no
behaviour change. So the docstring says "last match", and says explicitly that it need not be the last stdout line.

## Fixture cases added (all on a fenced `receipt=v1` K1 receipt at the tip)
| # | name | shape | expect | kills |
|---|---|---|---|---|
| 13 | token-moved | receipt `rev=` and SCORECARD token both moved to `cd`×20, a hex string that names no commit; they still agree | K1 `receipt-rev-object`, rc≠0 | `mut-noguard` |
| 14 | decoy-line | `# summary <wrong tuple>` before the fence, plus `progress <wrong tuple>` earlier in stdout; true tuple last in stdout | green (rc 0, M=0, keys=4, json-bound) | `mut-first` |
| 15 | trailing-shadow | stdout `…resolved=56 … mismatches=7`; after `--- stderr ---`, a blank line then the true `mismatches=0` tuple | K1 `value-disagree`, rc≠0 | pre-fix tool, `mut-nofence`, `mut-nostderr` |

Case 14 needed hardening. With only the pre-fence decoy, `mut-first` still scored 15/15, because the
fence already hides that decoy. The in-stdout decoy makes the case a real witness for last-wins.

## Validation (receipts in `w1/ExecR17/`)
| tool | extended fixture (15) | committed fixture (12) |
|---|---|---|
| **red arm**: pre-fix `3a90ddc` (`dd53c228`) | **selftest=14/15**, case 15 FAIL (`rc=0 mismatches=0`), final line `control=FALSE-GREEN-REJECTED`, **rc=1** | 12/12 |
| base `716731f` (`41db9ca8`), the brief's "OLD" | 15/15, rc 0 | 12/12 |
| **draft** (`04811c24`) | **selftest=15/15 control=FALSE-GREEN-REJECTED, rc 0** | 12/12 |
| `mut-first` (`matches[0]`) | 14/15 (case 14) | 12/12 |
| `mut-noguard` (receipt-rev-object `elif` removed) | 14/15 (case 13) | 12/12 |
| `mut-nofence` (whole-text parse) | 14/15 (case 15) | n/a |
| `mut-nostderr` (section runs to the end of the text) | 14/15 (case 15) | n/a |

Receipts:
- `ExecR17/red-arm-prefix-3a90ddc.tsv`
- `ExecR17/green-arm-draft.tsv`
- `ExecR17/base-arm-716731f.tsv`
- `ExecR17/tool-docstring.diff`

Each fixture run used a copy that differs from the draft only in `SCRATCH_ROOT` (checked with `diff`).
The copy's sha256 is recorded in each receipt. This avoids racing other seats on the committed
`SCRATCH_ROOT=/var/tmp/souji-r23-ExecFixtureAgreement`, which the fixture `rmtree`s on start.

## Residual disclosure (do not over-claim)
- **R17 (trailing shadow):** the tool was already closed in code at `315422b`. This round adds the fixture witness and the docstring.
- **R19:** this round covers 3 of the 28 uncovered mutants (the 4 sampled here are all killed). The other mutants were not re-measured.
- **R15 (K1 record-side decoy, W2K1 F2):** **still open.** A correct decoy tuple bound to the receipt rev elsewhere in SCORECARD still masks wrong tuples bound to another rev. Case 14 is a *receipt-side* decoy. A record-side F2 case would be red on every tool version, since no tool anchors K1 to the calibration row. It therefore cannot be part of a 14/15 → 15/15 witness, and it needs a code change in a later round.
- The draft fixture keeps the committed shared `SCRATCH_ROOT`. Concurrent fixture runs therefore still collide unless the integrator gives each run its own root.

## Coordination
Seat `L1Souji25.ExecR17-2` (a duplicate dispatch) reported that its fixture edits were reset at 09:30:07.
The likely cause is this seat's `git show a6d2d15:… > w1/r23-record-agreement.py` seeding.
Agreed split: ExecR17 owns both shared draft paths. ExecR17-2 keeps its fixture at
`w1/ExecR17-2-r23-record-agreement.py`, and its write-back guard (`sha == eda4fafa`) is now false.

## Tooling
None installed or updated (git and python3 were already on the host).
