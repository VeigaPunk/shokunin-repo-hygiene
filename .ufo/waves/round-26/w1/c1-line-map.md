# C1 line map — `superseded by SCORECARD.md:NNN` targets

The five refs are the bare lines at base 250-254 (inside the r25 block, which the edit moves to
draft 36-40). They were computed at the r25 base `a6d2d15` (byte-identical to the r24-tip file
`315422b`, `git diff 315422b a6d2d15 -- SCORECARD.md` empty, 228 lines) and resolved exactly there;
at base `89e0fce` four of the five are already +1 stale, because r25 inserted the scaffold. Two
readings are given: the LITERAL one (number as written, resolved against base bytes) and the
SEMANTIC one (what the referring sentence means, i.e. its `a6d2d15` referent). Recommendation: the
appended note should use the semantic mapping and disclose the staleness — the literal numbers were
already wrong before r26.

## Literal mapping (number as written, resolved against base `89e0fce`)

| ref | what that base line contains | landed a529c76 | DRAFT (235 lines) | exact variant (230 lines) |
|---|---|---|---|---|
| :181 | r24 table, C3 receipt verify/run symmetry row | 50 | 50 | 47 |
| :180 | r24 table, C2 coverage-map agreement row | 49 | 49 | 46 |
| :92 | capabilities, blob-bound receipts (r23) row | 153 (row plus R3 note) | 153 (row plus R3 note) | 149 |
| :224 | scaffold fence opener, no surviving line | 199 (payload 3 start) | 201 (payload 3 start) | 197 |
| :225 | r24 planned bullet (payload 3, line 1 of 2) | 199 | 201 | 197 |

## Semantic mapping (r24-tip `315422b` referent to its post-edit line)

| ref | r24-tip target | equals base line | landed a529c76 | DRAFT | exact |
|---|---|---|---|---|---|
| :180 | C3 receipt verify/run symmetry row | 181 | 50 | 50 | 47 |
| :181 | assimilation row (slice_verdicts=8 sentence) | 182 | 51 | 51 | 48 |
| :92 | blob-bound receipts (r23) row | 92 | 153 | 153 | 149 |
| :224 | r24 planned bullet | 225 | 199 | 201 | 197 |
| :225 | r25 planned bullet | 226 | 200 | 202 | 198 |

## Calibration caveat for the note
At the r25 base `a6d2d15` (== r24-tip bytes) the refs were exact (`:180`=C3 row, `:181`=assimilation row, `:224`=r24 planned bullet,
`:225`=r25 planned bullet). At base `89e0fce` they are +1 stale (`:180`=C2 row, `:181`=C3 row,
`:224`=fence opener, `:225`=r24 planned bullet). `:92` is the only ref still correct at base — the
`## Capabilities` table never shifted, precisely because the two r24 rows were never integrated.
Note the two planned bullets are a +26/-26 shift, not +1: r24 `:224` (bullet) lands at landed 199 /
draft 201, r25 `:225` (bullet) lands at landed 200 / draft 202.
