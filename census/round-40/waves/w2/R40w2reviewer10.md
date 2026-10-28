# R40w2reviewer10 — C1 self-assessment evidence-binding attack

## Scope and verdict

**SAFE (no round-40 self-assessment cells to falsify at the landed revision).** The committed `SCORECARD.md` contains only the r40 planned-work bullet, not r40 measured/self-assessment cells. The committed `LOG.md` contains no round-40 entry. Therefore there are no r40 stated measurement values whose receipt/revision bindings can be checked or which could fail the C1 evidence-binding predicate. This is an absence-of-target result, not evidence that a future r40 self-assessment will pass.

## Commands and exact output

All reads below target the committed landed revision `128e412b0ced3c243dc27c3dd3332054a611bc2e`.

Command:
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:SCORECARD.md | grep -n -E 'Round 40|R40|r40|SELF-ASSESSMENT'
```
Output:
```text
779:- **r40 (planned r39):** calibration: bind the C1 items to *evidence* rather than token presence (a line that quotes the right tokens but cites nothing passes today; `W1RevC1Forge` demonstrates it) and give the register a row whose `commit` is older than its `receipt_rev` to exercise the other direction. Operability: the C2 L4 analyser still reads one docstring line per class (a wrapped trigger reads False by construction), and the `EISDIR` class the wave found unreachable is now dropped — carry the remaining class-to-trigger pairs the wave listed. Coverage: the parser branches M11-M14 leave uncovered (multiple TOTAL rows, `--skip-unrecorded`, non-UTF-8 records) — mutation-score them next round. Certification OFF, K5 HELD.
```

Command:
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:LOG.md | grep -n -E 'Round 40|R40|r40|SELF-ASSESSMENT'
```
Output:
```text
Command exited with code 1
```

The source command confirms `SCORECARD.md:779` is explicitly a **planned** item, not a measurement cell. `LOG.md` has no matching r40 entry in committed bytes.

## C1 predicate context

`census/round-40/c1-counter.py:119-155` parses evidence as `PATH@REVISION`; `:235-260` checks the revision resolves, is an ancestor of the audited revision, the evidence path exists there, and the anchored item line carries that revision token. Those checks have no r40 SCORECARD/LOG measurement cell to evaluate in this landed snapshot.

No scratch directory or tools were created/installed; scratch removal: **not applicable**.
