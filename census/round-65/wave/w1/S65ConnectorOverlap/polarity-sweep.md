# S65ConnectorOverlap — polarity-class sweep (tabi round-62 dead-token class)

Class: a counter that decides by substring presence (`needle in text`) with no liveness anchor — a needle that sits in a comment, a fenced/dead block, or an unreachable branch satisfies the check. Tabi round 62 (`corpus/lessons/round-62.md`, "Mined survivor: M5 polarity coverage gap", and R3 "contradictory duplicate dispositions ... false-green") recorded the same shape on its producer-verdict side. Souji's round-65 C2 answers this with a live-marker rule (a needle counts only on an uncommented line carrying `refuse(` or `return`) and a dead-token second-polarity mutant.

This sweep names sibling counters whose needle checks have no liveness anchor. **Paths only. These are reports for their lanes, not defects fixed here. Nothing was executed; a claim that a counter would false-green is an inference from its source, not a run.**

## Candidates (needle presence, no liveness anchor)

| path | needle check (as printed) | why it could false-green the same way |
|---|---|---|
| tsukuroi-shokunin/tools/check-adjacency-table-r50.py:146–150 | `heading not in text`; `quote not in text` against the pinned `PROVINCE.md` blob | A quote or heading that survives only inside a comment, a fenced block, or a dead section satisfies the pin; no live-line test. |
| chousa-shokunin/tools/claims-audit.py:98–101, 161–164, 183 | `anchor` selected by `next(i for ... if rule["anchor"] in l)`; `spans not in body`; `anchor not in text` | The first line containing the anchor is taken even if it is a commented or dead line; the span check accepts any substring of the target body. |
| chousa-shokunin/tools/claims-audit-v2.py:115–118, 178–179, 200 | same three shapes as claims-audit.py | same |
| chousa-shokunin/tools/quarantine-check.py:57–58 | `f_exact(doc, q): return q in doc` | exact substring of the document; a quoted needle inside a dead section passes. |
| tabi-shokunin/.ufo/waves/round-62/counters/chromium-receipt-r62.mjs and tabi-shokunin/.ufo/waves/round-62/counters/c1-adjacency-host-v21.mjs | the round-62 lesson records the v21 contradictory-duplicate and arbitrary-label false-green (`W/w1/R62Reviewer/real-conflicting-meter.json`, `fabricated-meter.json`, both predicate=true, findings 0); the mined M5 polarity survivor is in the same family | the lesson is the source of record; the counter paths are named for the owning lane. |

## Checked and not in the class

- tabi-shokunin/scripts/check-secondary-round62.mjs:11–12 (`verdict?.findings?.includes(id)`) tests a token in a live verdict object, not a needle in source; it is not in the class.
- Kaidoku and mori `GIT_*` scrub lists (see sibling-overlap.md §2) are drop policies, not needle checks.

## Relation to souji round 65

Souji's C2 counter is the instrument that answers this class for its own lane: the needle counts only on an uncommented line carrying `refuse(` or `return`, and the dead-token second-polarity mutant must produce findings. The named limit stands: C2's live read is lexical and does not prove reachability (an `if False:` refusal keeps its live line and is caught by the C1 matrix, not by C2).
