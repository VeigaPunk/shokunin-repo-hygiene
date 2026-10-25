# SOURCES row fixture — one good row, one row per defect class

Block read by `row-check.py --table rows-fixture.md --expect
rows-fixture.expect.tsv`. Every row below is checked exactly as the tool checks
a row about to be appended to `corpus/SOURCES.md`. This file holds ONE table:
prose here is deliberately pipe-free, because the tool treats every table row it
is given as a row it must judge.

Defect classes, in file order, and the code each row must draw:

- S990 — good row — none: 11 columns, well-formed id, valid enums, `90d`
  recheck, used-by path that exists.
- S901 — column count — E01: ten cells, one short of eleven.
- S91 — id format — E02: `S` + two digits; the contract requires three or more.
- S902 — leading indent — X01: four leading spaces is indented code, which the
  census skips silently, so the row would vanish.
- S903 — literal pipe inside a cell — X02 (and E01): the `|` in `teaches` is
  unpadded on both sides, so it reads as a column boundary as well.
- S904 — escaped pipe inside a cell — X02 (and E01): the contract forbids the
  pipe in any form, escaped included; the census still splits on it.
- S905 — status enum — E07: `watch` is not a status; a cadence belongs in
  `recheck`.
- S906 — recheck format — E09: `90 days` is neither an ISO date, the `NNd` form,
  nor a cadence this lane uses.
- S907 — used-by path — E11: names a knowledge file absent under the root.
- S908 — kind enum — E05: `blog` is not a kind.
- S909 — tier enum — E06: `D` is not a tier.
- S910 — opened format — E08: `2026-13-01` is not a calendar date.
- S911 — community at tier A — E10: `community` is never tier A.
- S114 — id already in the registry — E03: the lane registry already ends at
  S114, so this id cannot be appended.

The two pipe rows carry E01 as well as X02, because the census splits on every
`|`; X02 is the code that names the cause. Every other row draws exactly its own
code.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S990 | fixture good row — https://example.invalid/good | docs | A | fixture scope | § 1 | a good row teaches one thing | queued | 2026-10-25 | 90d | corpus/knowledge/trash-spec-restorable-quarantine.md |
| S901 | fixture column count — https://example.invalid/cols | docs | A | fixture scope | § 1 | ten columns only | queued | 2026-10-25 | 90d |
| S91 | fixture id format — https://example.invalid/id | docs | A | fixture scope | § 1 | id cell has two digits | queued | 2026-10-25 | 90d | — |
    | S902 | fixture indent — https://example.invalid/indent | docs | A | fixture scope | § 1 | four spaces of indent | queued | 2026-10-25 | 90d | — |
| S903 | fixture literal pipe — https://example.invalid/pipe | docs | A | fixture scope | § 1 | a|b inside one cell | queued | 2026-10-25 | 90d | — |
| S904 | fixture escaped pipe — https://example.invalid/escpipe | docs | A | fixture scope | § 1 | a\|b inside one cell | queued | 2026-10-25 | 90d | — |
| S905 | fixture status — https://example.invalid/status | docs | A | fixture scope | § 1 | status cell holds watch | watch | 2026-10-25 | 90d | — |
| S906 | fixture recheck — https://example.invalid/recheck | docs | A | fixture scope | § 1 | recheck cell holds the long form | queued | 2026-10-25 | 90 days | — |
| S907 | fixture used-by — https://example.invalid/usedby | docs | A | fixture scope | § 1 | used-by names a missing file | queued | 2026-10-25 | 90d | corpus/knowledge/r22-append-target-absent.md |
| S908 | fixture kind — https://example.invalid/kind | blog | A | fixture scope | § 1 | kind cell holds blog | queued | 2026-10-25 | 90d | — |
| S909 | fixture tier — https://example.invalid/tier | docs | D | fixture scope | § 1 | tier cell holds D | queued | 2026-10-25 | 90d | — |
| S910 | fixture opened — https://example.invalid/opened | docs | A | fixture scope | § 1 | opened is not a date | queued | 2026-13-01 | 90d | — |
| S911 | fixture community at A — https://example.invalid/community | community | A | fixture scope | § 1 | community is never tier A | queued | 2026-10-25 | 90d | — |
| S114 | fixture id collision — https://example.invalid/collision | docs | A | fixture scope | § 1 | id already exists in the registry | queued | 2026-10-25 | 90d | — |
