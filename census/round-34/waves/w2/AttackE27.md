## Status

INFERENCE — W1’s reported E27 mismatch is supported by its committed base reading; I found no honest restatement route that satisfies the frozen cause rules. I did not execute a probe. No artifacts were changed.

## Evidence

- Frozen list row `census/round-34/c1-items.tsv:72` (revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`): E27 is `SCORECARD.md:346`, expected exit 0, predicate `SUMMARY legs=9 fail=0 f1_entries=3`, row file `census/round-30/c3-counter.py`, argv `python3 -B census/round-30/c3-counter.py --root . --rev {REV}`.
- Base do-nothing receipt `census/round-34/records/controls-c1-do-nothing.txt:1` pins the original freeze list; the independent W1 remeasurement ` .ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:61` records E27 `MISMATCH`, rc=1/expected 0, last line `SUMMARY legs=9 fail=2 f1_entries=5`, at base `9c76c7222a8abff027af42e37f0d160d52526bba`. `SwarmExecutor13.md:62` independently reports the same result and no prior correction.
- Frozen C1 cause requirements are `census/round-34/preregistration.txt:48-57`; specifically, same-argv correction requires the original result to hold at cause parent and fail at cause, while argv correction requires the row writer as cause and the original argv already failing at that cause. Q76 recognizes only an already-binding correction for this item; the W1 sweep reports none for E27 (`SwarmExecutor13.md:30,62`).
- Frozen counter’s implementation confirms these branches: `census/round-34/c1-counter.py:284-291` checks parent/cause transition for same argv; `:293-300` checks that argv-correction cause introduced the row and that original argv did not hold at cause. Corrected argv must name an item file (`:263-268`), and statements bind to the measured run’s final digit-bearing line (`:269-272,301-313`).
- The relevant SCORECARD source row is the Round 30 C3 entry at `SCORECARD.md:346`; the prior section states the C3 landing was `76c94eb41fc38093d7143a016006b6275e102d5d` (`SCORECARD.md:346`, with the measured-commit context at `:340-348`).

## Findings

1. **No counter-evidence to W1’s base mismatch.** The receipt is an actual committed counter reading, not just an interpretation of the claimed SCORECARD outcome. This is a genuine value-and-exit mismatch, not merely a last-line measurement artifact: both the expected exit and predicate differ from the recorded run.
2. **No honest `same` correction is apparent under the frozen rule.** A same-argv restatement must use a cause touching the item file, namely `census/round-30/c3-counter.py`, and demonstrate original predicate+exit true at its parent and false at cause. The SCORECARD’s claim records the older C3 outcome (`fail=0`); the natural row-writer/landing cause is `76c94eb41fc38093d7143a016006b6275e102d5d`. W1’s finding that the base command instead reports `fail=2` is consistent with later drift, but by itself does not establish the required parent/cause transition. Any alternate same-argv cause must still independently satisfy that exact transition and touch the row file.
3. **The plausible argv-correction escape is blocked by the cause clause.** One could imagine correcting argv to pin the historical C3 measurement revision and restating its actual final output. But a valid argv-correction cause must have written the E27 row and the frozen original argv must already fail at that cause. At the row-writing cause the original row’s command is the very command that produced the claimed `fail=0` C3 measurement (or at least the correction would need to prove otherwise); a later unrelated commit where the command has drifted cannot serve as cause because it did not write the row. The frozen counter checks exactly this at `c1-counter.py:293-300`. Thus pinning a historical revision is not, by itself, an honest route around the cause requirement.
4. **Verdict:** genuine unreachable-by-the-obvious-restatement-routes defect under the frozen contract, not a demonstrated instrument bug. The precise cause-parent execution was not reproduced in this seat, so the impossibility conclusion remains source-level inference rather than executed proof. W1’s base mismatch itself is reproduced in committed evidence.

## Attack log

- Read the frozen preregistration, E27 row, base control, W1 C1 control receipt and the W1 consolidated mismatch finding.
- Checked the frozen `judge()` cause branches and the SCORECARD’s Round 30 C3 statement/landing context against the possible same-argv and argv-correction routes.
- No fixture, clone, command, or bounded runtime probe was executed; therefore no execution output is claimed. No LSP device was available/queried in this environment; cited evidence is from committed text/source.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE27.md` — this scoped adversarial review.
