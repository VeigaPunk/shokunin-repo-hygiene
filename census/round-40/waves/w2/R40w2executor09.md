# R40w2executor09 — shape of the r39 SCORECARD measurement block and LOG entry (for the r40 appends)

Verdict: **SAFE** (shape question; nothing falsified — no counter was attacked). Read-only; no scratch dir created (nothing to remove).
Lane HEAD at read: `549d9ec53a1f5932337ff14438fcd22b0621828d`; SCORECARD.md 785 lines, LOG.md 1899 lines.

## Commands run (all read-only)
- `_grep '^#{1,4} '` on `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md` (heading list)
- `_grep '^#{1,4} .*(39|r39|R39)'` on LOG.md; `_grep '^(## |### )'` on LOG.md:1840-2100
- `read SCORECARD.md:736-790`, `read LOG.md:1888-1915`
- `_grep 'Round 40|R40|round 40|r40'` on LOG.md -> `No matches found` (LOG has NO r40 entry yet)
- `git log --oneline -5`, `git show --stat 128e412…`, `git rev-parse HEAD` (outputs above)

## SCORECARD.md — r39 block, headings in order (copied verbatim; file:line)
```
737 ### R39 finality correction (round 39, appended; the blocks above stand as written)
741 ### Round 39 register cells (appended; every row's commit is later than its receipt_rev)
749 ### Round 39 register cells, second set (appended; the first set names its own stale token and so cannot serve as a register row)
757 ### Round 39 measurements (2026-10-28; base `ed30b7f5b77939c9073348d810730bc4f355708d`; preregistration `b769bfb84a264d8b284c09bc211d99f39a3e9126`; amendment A1 `bbd9b9746ba9e3c5d640bf095bbad18a00c80e83`)
767 ### Round 39 capability rows (appended)
777 ### Planned (appended at round 39)
```
Then (r40, already present) `781 ### Round 40 closure cells (bound before measurement)` with three bullets `- R40-CLAIM-D1 / R40-CELL-01 — …` to `…-D3 / …-03` (783-785, EOF). So the r40 measurements/capability/Planned headings are NOT yet written; they follow line 785.

Prior-round headings to mirror for r40 (same pattern at r38: `### Round 38 measurements (…)` 662, `### Round 38 capability rows (appended)` 676, `### Planned (appended at round 38)` 684):
```
### Round 40 measurements (2026-10-28; base `<lane base40>`; preregistration `<prereg40>`; amendment(s) `<…>` if any)
### Round 40 capability rows (appended)
### Planned (appended at round 40)
```
Blocks are APPENDED at EOF (K2: SCORECARD stays append-only; r29 line 309 says so), not inserted in `## Capabilities` (:143) or `## Planned` (:177).

### Measurement table (SCORECARD.md:759-760) — 6 columns, exact header
```
| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
```
Row shape (:761-763): one row per claim, `claim` = `C<n> <short title>`; `axis` = `<axis> <score>` (calibration 7 / operability 8 / coverage 8); `before` = `` `SUMMARY …` rc N (`census/round-N/records/cK-before.txt`) ``; `after` = `` `SUMMARY …` rc 0 (`cK-after.txt`): <plain-words gloss> ``; `counting command` = `` `python3 -B census/round-N/cK-counter.py --root <lane> --rev <full40> [--base-rev <base40>] [--scratch <dir>]` ``; `measured commit` = bare full 40-hex (e.g. `2f6e981a105fc759205767d2a749a5f7d4fd0b8a`).
Followed (blank line, :765) by one paragraph beginning `Owned score values unchanged (calibration 7, operability 8, coverage 8): …` stating the lane has no reproducible 0-10 mapping, no axis harmed, frozen predicates not relaxed, earlier fixtures byte-identical, consumers green.

### Capability table (SCORECARD.md:769-770) — 4 columns, exact header
```
| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
```
Row shape (:771-775): `name` = `<noun phrase> (r39)`; `what it can now do` = prose; `evidence pointer` = `` `<exact command>` -> `<printed SUMMARY>` (`census/round-N/records/…-after.txt`) ``; `first-working round` = `r39`. r39 has 5 rows: three counters (c1,c2,c3) + two fixtures (`tests/fixtures/r39-citation-rev.py`, `r39-drift-record-rules.py`). r40 analogue: three counters + `tests/fixtures/r40-drift-record-branches.py` (+ `census/round-40/docstring-classes.py` if counted as a tool).

### Planned block (SCORECARD.md:777-779)
Heading `### Planned (appended at round 39)`, single bullet `- **r40 (planned r39):** calibration: …; operability: …; coverage: … Certification OFF, K5 HELD.` → r40 writes `- **r41 (planned r40):** calibration: …; operability: …; coverage: … Certification OFF, K5 HELD.`

## LOG.md — r39 entry shape (LOG.md:1873-1899)
Pre-entry correction/register blocks (append-only, LOG's own, level 3, before the `##` entry):
```
1873 ### R39 append-only corrections (round 39, 2026-10-28)
1879 ### R39 register cells (round 39, appended)
1885 ### R39 register cells, second set (round 39, appended)
```
Then the entry itself, a level-2 heading and exactly 8 bullets (`- `), no sub-headings, no tables:
```
1891 ## 2026-10-28 — Round 39 attempt 1 (hyaku run 11): routed-defect closure, revision resolution, record-rule mutation coverage
```
r40 form: `## 2026-10-28 — Round 40 attempt 1 (hyaku run 11): <C1 theme>, <C2 theme>, <C3 theme>` (r38 form for a fresh start: `… Round 38 attempt 1 (hyaku run 11, fresh start): …`, :1864). No `### Round 40` LOG heading exists yet (grep returned no matches).
Bullet order in the r39 entry:
1. 1893 — opener: first round after the prior closure; claims frozen at `<prereg40>` (lane base `<base40>`), do-nothing controls committed before after-data (`census/round-40/records/{c1,c2,c3}-before.txt`), amendments listed.
2. 1894 — `C1 calibration (lowest non-retired axis, 7): …` control `SUMMARY` rc, after `SUMMARY` rc 0 (`c1-after.txt`). `Measured at <full40>.`
3. 1895 — `C2 operability: …` control `legs=… ` / after `legs=… harm=0` (`c2-after.txt`).
4. 1896 — `C3 coverage: …` control / after (`c3-after.txt`).
5. 1897 — `Wave: …` seat counts by role, settled/dead, report-file count, evidence capture path `census/round-N/waves/` with `records=… failed=0 uncovered=0 at <rev>`.
6. 1898 — `Frontier: corpus/SOURCES.md <n> -> <m> rows (S…), W04 …, census rc 0 at both ends; …` plus `Assimilation: …`.
7. 1899 — `No tools installed or upgraded; pacman stayed paused. Owned scores unchanged (calibration 7, operability 8, coverage 8). Certification OFF, K5 HELD.`

(The r39 entry has 7 bullets: 1893-1899; the numbering above is by line.) LOG is append-only: add the r40 entry after line 1899 (EOF), after any `### R40 …` correction/register blocks.

## Observations for the L1 (not falsifications)
- The r40 closure-cells block (`SCORECARD.md:781-785`) is already appended as the register-cells analogue; the r40 measurement table must land after it (EOF), mirroring r39 where register cells (741-755) precede `### Round 39 measurements` (757).
- r40 closure cells cite verified commit `556c24a5cacf208c5144c459838712594a43e1f2` and instrument commit `8a5fbdbddaab24c5ba43fc6a133499efb405f214`; the landed commit under attack is `128e412b0ced3c243dc27c3dd3332054a611bc2e` (`git show --stat` lists `census/round-40/{c1,c2,c3}-counter.py`, `docstring-classes.py`, `preregistration.txt`). The r40 measurements row's `measured commit` column must say which of these it means — r39 used the single revision all three claims were measured at.
- No tools installed or upgraded; pacman not run.
