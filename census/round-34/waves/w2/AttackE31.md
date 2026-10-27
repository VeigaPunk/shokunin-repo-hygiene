## Status
INFERENCE — no bounded counter replay performed. W1's exit-only mismatch classification is supported by the committed do-nothing receipt; the proposed blockage is not refuted by a frozen-clause escape I could identify.

## Evidence
- Frozen item at list revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`: `census/round-34/c1-items.tsv:75` defines E31 as `SCORECARD.md:477`, exit `0`, statement `SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6`, script `census/round-32/c1-counter.py`, argv `python3 -B ... --rev {REV} --base 85b61a... --list-rev 3ec84...`.
- W1's independent do-nothing receipt reports E31 `MISMATCH original rc=1 expect_exit=0 predicate holds` with the target summary as last digit-bearing line: `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:64`. The same classification is summarized at `.ufo/waves/round-34/w1/SwarmExecutor13.md:32` and `:64` (exit-only; no prior correction).
- Frozen correction rules: `census/round-34/preregistration.txt:48-57` requires a same/corrected-argv restatement row, quoted complete line, full-40 ancestor cause, and executed cause predicates; argv correction must run the row's own script. Target/kill rule is `:59-66`. Counter enforcement for same corrections and argv corrections is `census/round-34/c1-counter.py:284-300`; corrected run's exit and statement must then hold at `:301-315`.

## Findings
- **No alternate frozen route identified (inference).** E31's stated summary predicate holds already, but its required exit does not. A same-value correction cannot honestly explain the observation: the relevant claim has not undergone a value transition (predicate holds at the base measurement), and the frozen same-value cause test requires it to hold at the cause parent and fail at the cause (`c1-counter.py:288-291`). An argv correction cannot merely change the expected exit: the row schema still records an exit and the counter checks `rc == int(exit_)` (`:305`, `:315`); moreover, its cause must have written E31's row and the original row argv must fail at that cause (`:293-300`). No W1 evidence establishes such a cause, and a correction that only relabels rc=1 as expected would contradict the frozen target's declared exit-0 outcome rather than restore the stated claim.
- This is not evidence that no conceivable post-freeze repository change could ever yield an acceptable E31 row. It is a source-level assessment of the stated frozen cause/argv/exit/statement/Q76 paths, not a reproduced impossibility proof. No execution command/output is claimed.

## Attack log
- Compared the frozen E31 tuple, do-nothing receipt, preregistration correction/cause requirements, and counter's branch-specific enforcement. Did not create a scratch clone or run the counter; avoided replay cost and made no lane changes.

## Deliveries
- `.ufo/waves/round-34/w2/AttackE31.md`
- `.ufo/waves/round-34/w2/SwarmReviewer24.md` (seat summary)
