# W1ScoutReportGate — tools/souji-report-contract.py

Seat: scout, round 39 wave 1. Advisory only. No lane file edited except this report. No commit. No scratch tree left on disk (the /tmp captures below were removed in the same command).

Axes: (1) predicate fidelity to the tool's code, not the docstring's paraphrase; (2) line-level hit/miss on the filed r38 report; (3) a fail-condition table an r39 report can be checked against before filing.

## Bytes pinned

```
$ sha256sum /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
ec33659f41200b6fd83db4bef6557b2f209437acb594814193e721a713598570  /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md
$ wc -l /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
  279 souji.md
   12 SHONEN.md
```

Tool read: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py` (412 lines). SHONEN boxes are `SHONEN.md:5,7,9,11` — four `- [~]` lines. The checker compares counts, not box text.

## Commands and verdicts

### V1 — filed r38 report. Verdict: PASS, rc 0

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py \
    --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-38/souji.md \
    --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
check-sections=PASS
check-shonen-boxes=PASS
check-trends=PASS
check-stale-lane=PASS
check-measurements=PASS
check-claims=PASS
check-evidence=PASS
SUMMARY checks=7 pass=7 fail=0
rc=0
```

In-process `evaluate()` on the same bytes (module loaded read-only) details: `headings=6 ordered`; `box_lines=4 boxes=4`; `verdicts=3`; `heading_body`; `rows=1`; `claim_ids=C1,C2,C3`; `pointers=52`.

Verdict: the aggregate gate passes. That does not mean every measurement row or every backtick satisfies its predicate. `rows=1` of the three claim rows. See the line table.

### V2 — selftest. Verdict: PASS, rc 0

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py --selftest
case-conforming=PASS observed=[] expected=[]
case-empty-code-span=PASS observed=[] expected=[]
case-missing-section=PASS observed=['sections'] expected=['sections']
case-section-order=PASS observed=['sections'] expected=['sections']
case-shonen-no-box-line=PASS observed=['shonen-boxes'] expected=['shonen-boxes']
case-trend-missing=PASS observed=['trends'] expected=['trends']
case-stale-lane-absent=PASS observed=['sections', 'stale-lane'] expected=['sections', 'stale-lane']
case-no-measured-commit=PASS observed=['measurements'] expected=['measurements']
case-no-evidence-pointer=PASS observed=['measurements', 'evidence'] expected=['measurements', 'evidence']
SUMMARY cases=9 pass=9 fail=0
rc=0
```

### V3 — empty report (/dev/null). Verdict: FAIL 7/7, rc 1

```
check-sections=FAIL
check-shonen-boxes=FAIL
check-trends=FAIL
check-stale-lane=FAIL
check-measurements=FAIL
check-claims=FAIL
check-evidence=FAIL
SUMMARY checks=7 pass=0 fail=7
rc=1
```

stderr:

```
detail-sections: work performed headings=0 expected 1
detail-shonen-boxes: ## SHONEN sections=0 expected 1
detail-trends: no trend verdicts section body
detail-stale-lane: no stale-lane line
detail-measurements: no row with a measured commit and a counting command
detail-claims: claim ids=0 expected 1-3
detail-evidence: no evidence pointer
```

Stdout still prints every `check-*` line. Details go to stderr only for failures (`render`, lines 264-273).

### V4 — usage. Verdict: rc 2

No args:

```
ERROR USAGE: --report ABS --shonen ABS | --selftest
usage_rc=2
```

`--nope` (argparse SystemExit is caught and re-wrapped): stderr is argparse's usage plus the same `ERROR USAGE` line. `nope_rc=2`.

### V5 — help. Verdict: rc 0

`-h` prints the module docstring (43 lines) and exits 0. stderr empty.

## Exit codes (observed)

| rc | when | observed |
|---|---|---|
| 0 | all 7 predicates pass, or `-h` / `--help` | r38 report; `-h` |
| 0 | `--selftest` and every case's failed-set equals its expectation | 9/9 |
| 1 | one or more predicates FAIL | `/dev/null` report, fail=7 |
| 1 | `--selftest` case mismatch | not observed (source: `selftest` returns 1 if `failed_cases`) |
| 2 | missing `--report` or `--shonen`, argparse SystemExit, report unreadable (`REPORT-UNREADABLE`), SHONEN unreadable (`SHONEN-UNREADABLE`) | missing args and `--nope` observed. Unreadable paths not re-run; `main` lines 400-407 |

`--selftest` returns before the file reads (line 396), so a report path beside it is ignored.

## Predicate shapes (code, not the docstring paraphrase)

Mask first (`mask`, lines 79-112): a line inside a triple-backtick or `~~~` fence, or an HTML comment, is blanked before every predicate. A heading or pointer inside a fence does not count. r38 blanks only lines 118-124 (the sources-census fence). No HTML comments.

Headings are `^ {0,3}##\s+(.*\S)\s*$` (`HEADING`, line 59). A section body runs until the next heading.

`normalize_heading` (lines 74-76), observed by calling it:

| heading text | normalized | notes |
|---|---|---|
| `Before → after measurements` (U+2192) | `before -> after measurements` | matches. Original has no ASCII `->`, so only U+2192 is rewritten |
| `Before -> after measurements` | `before -> after measurements` | matches. ASCII `->` also rewrites U+2014 and `--` |
| `Before — after measurements` (U+2014, no ASCII `->`) | unchanged emdash | does not match the measurements key |
| `Stale-lane` / `Stale lane` | `stale-lane` / `stale lane` | both accepted for the stale-lane key only |
| `Stale—lane` | unchanged | not accepted |
| `Sources & frontier` | exact `&` | `and` fails |
| `Work performed` | exact | a suffix such as `Work performed (C1)` fails `sections` |

### 1. sections

Six keys, each exactly once, in this order (`SECTION_KEYS`, lines 51-58): `work performed`, `landed changes`, `before -> after measurements`, `sources & frontier`, `trend verdicts`, `stale-lane`. Comparison is normalized equality, except `stale lane` is also accepted for the last key. Order is the six heading indexes strictly increasing. Extra `##` headings are ignored. A duplicate of any of the six fails (`<key> headings=N expected 1`, or `heading order ... not canonical`).

`## SHONEN` is not one of the six.

### 2. shonen-boxes — SHONEN line rule

- Count `BOX` lines in `SHONEN.md`: `^\s*[-*]\s*\[[xX~ ]\]` (line 63). Zero boxes fails `SHONEN.md carries no boxes`.
- Exactly one report heading whose text matches `^shonen\b` (line 159). Zero or two or more fails `## SHONEN sections=N expected 1`.
- Box-lines inside that section's body must equal the SHONEN.md count. Text is not compared. Continuation lines that are not checkboxes do not count.
- Legal marks: `[x]` `[X]` `[~]` `[ ]`. `[*]`, `[+]`, `[?]` do not match.

### 3. trends — trend-verdict line rule

First section whose raw lowercased heading matches `trend verdicts` (`section_body`, first hit). Empty fails `no trend verdicts section body`.

For each of `expansion`, `quality`, `discernment`, on the lowercased line:

```
^\s*[-*]?\s*\**TREND\**\s*[:—]\s*\**([a-z-]+)
```

The dash in `[:—]` is U+2014 (source line 177). ASCII `-` is not a separator. Optional list marker `-` or `*`, optional bold stars around the name. The verdict is the first `[a-z-]+` token after the separator, and it must be exactly one of `unprovable-but-better`, `improved`, `harmed`, `unchanged` (`VERDICT_TOKENS`, line 49; the hyphenated token is captured whole). `expansion: not improved` fails `expansion line opens with 'not', not a verdict token` (comment at lines 180-182). A second match for the same trend fails `duplicate <trend> verdict`. A missing trend fails `missing verdicts: ...`. Non-matching continuation lines are ignored.

### 4. stale-lane

Pass if a heading normalizes to `stale-lane` or `stale lane` and any body line is non-blank (`heading_body`). Else pass if any unmasked line matches `^stale[- ]lane\s*[:—-]\s*(\S.*)$` (`re.I`; separators colon, U+2014, or ASCII hyphen; body must contain a non-space). Else `no stale-lane line`. The heading is still required by `sections`, so a line-form elsewhere does not replace a missing heading.

### 5. measurements — measurement-row rule

First section whose raw lowercased heading matches `before.*after measurements`. A row qualifies only when all of:

- `lstrip` starts with `|`
- it is not a separator `^\s*\|[\s:\-|]+\|\s*$`
- backtick spans (`` `([^`\n]+)` ``) number at least two
- at least one span, after whitespace `strip` only, matches `^[0-9a-f]{7,64}$` (whole span, lowercase, length 7-64)

The docstring says the second span is "a counting command". The code does not check that. Any second non-empty span is enough. A commit buried inside a longer span (`python3 ... 4090ee5b...`) does not match `COMMIT`. Uppercase hex does not. The predicate is existential: one qualifying row passes; other rows in the same table may miss. Fail detail: `no row with a measured commit and a counting command`.

The selftest conforming row (line 290) is the safe shape: one cell whose entire backtick is the hex, plus another backtick on the same row.

### 6. claims

First section whose raw lowercased heading matches `work performed`. Distinct `\bC([1-9])\b` captures, count in 1..3. `C0` does not match. `C10` does not match as `C1` (the boundary fails between `1` and `0`). `R38-C1-7` does match `C1` if it sits in this section (`-` is a boundary). Ids outside this section do not count. Fail: `claim ids=N expected 1-3`.

### 7. evidence

Every unmasked line. For each backtick span, take the first whitespace-separated field and strip `()[],;` from its ends. Count it if that token matches `^(census|corpus|tools|tests|\.ufo)/` or `^[0-9a-f]{40,64}$`. Need at least one. An empty code span is skipped (lines 237-240). Short hashes (7-39) do not count. Absolute paths do not. Bare `SKILL.md` / `LOG.md` / `SCORECARD.md` / `PROVINCE.md` do not. A `:line` suffix is fine because it stays on the first token (`tools/souji-citation-reconcile.py:22-36,...`).

## r38 line table

Workspace grep (`path:line`, same as `grep -n`):

- `^#{1,3} ` hits headings at 1, 9, 78, 98, 114, 142, 159, 172, 186, 199, 213, 217, 222, 257, 267
- `^\s*[-*]\s*\[[xX~ ]\]` on the report hits 188, 191, 193, 196. On `SHONEN.md` hits 5, 7, 9, 11
- `^[-*] (expansion|quality|discernment):` hits 144, 148, 153
- `^## Stale` / `Stale-lane:` hits 213, 215
- `^\| ` in the before/after section hits 103, 104, 105, 106, 107
- `\bC[1-9]\b` inside Work performed (lines 10-77) hits 13 `C1`, 17 `C2`, 20 `C3` only. Later hits (87, 133, 164, 177, 224, 254, 273, 275) are outside that body and do not feed `claims`

| predicate | r38 result | lines that satisfy | lines that miss the rule |
|---|---|---|---|
| sections | PASS, 6 ordered | headings 9 `Work performed`, 78 `Landed changes`, 98 `Before → after measurements` (U+2192; normalizes), 114 `Sources & frontier`, 142 `Trend verdicts`, 213 `Stale-lane`. Indexes 9<78<98<114<142<213 | none of the six missing or duplicated. Extra headings 159, 172, 186, 199, 217, 222, 257, 267 are allowed. H1 line 1 is not a `##` |
| shonen-boxes | PASS, 4=4 | 188, 191, 193, 196, each `- [~]` | none. Continuations 189-190, 192, 194-195, 197 are not box lines and are not required to be. Box wording is longer than `SHONEN.md` and is not checked |
| trends | PASS, 3 verdicts | 144 `expansion: unchanged`, 148 `quality: improved`, 153 `discernment: improved`. Separator is `:`. Tokens are in the set | none. Continuations 145-147, 149-152, 154-157 do not match the trend regex and are ignored, not duplicates |
| stale-lane | PASS, `heading_body` | heading 213; body 215 non-blank (`Stale-lane: no — ...`) | none. Line 215 would also match the line-form regex, but the heading body returns first |
| measurements | PASS, rows=1 | 105 only. 11 spans; the one whole-span commit is `` `99efe06` `` (7 lowercase hex). The 40-hex `4090ee5b...` sits inside the `python3 ...` span and is not itself a commit span | 103 header: one span `` `ca4369a` `` (is 7-hex, but needs a second span) — does not qualify. 104 separator — ignored, not a candidate. 106 seven spans, no whole-span commit (`ca4369a` is inside the command span). 107 six spans, no whole-span commit. 106 and 107 do not fail the gate because 105 already qualified |
| claims | PASS, `C1,C2,C3` | 13, 17, 20 | none inside the work-performed body. A fourth distinct `C[1-9]` there would fail the section |
| evidence | PASS, pointers=52 | pointer list below | candidate backticks that do not count. The gate still passes |

Evidence hits (52), by line: 4 (40-hex); 5 (two 40-hex); 25 `tools/souji-citation-reconcile.py`; 28 two (`tools/...:22-36,...`, `census/round-38/records/c1-after2.txt`); 31 `corpus/QUALITY.md:212-214`; 32 `census/round-38/cells.tsv`; 33 `tests/fixtures/r38-citation-commit.py`; 35 `census/.../a2-anchor-isolation.txt`; 36 `tools/souji-worktree-drift.py`; 39 two; 40 `tests/fixtures/r38-drift-write-envelope.py`; 43, 44 census receipts; 45, 46 fixtures; 48 census; 49 fixture; 51 census; 57 two corpus paths; 58, 59 corpus; 63 two `.ufo/waves/...`; 66, 71 `.ufo/waves/round-38/w*.md`; 85-91 seven 40-hex commits; 95 two `tools/*.sh`; 101 `census/round-38/records/`; 146 `corpus/README.md`; 166 `corpus/lessons/round-36.md:23`; 170 `.ufo/prompts/`; 174 40-hex; 176 corpus lesson; 189, 190 corpus; 192 `census/round-38/records/`; 203, 204 `.ufo/waves/...`; 210 two `.ufo/`; 264 40-hex.

Evidence misses (backticks that look like pointers and are not counted): L3 absolute `/home/vgpnk/Projects/shokunin/souji-shokunin`; short hex L6 `4090ee5`,`8093c70`, L103 `ca4369a`, L105 `99efe06` (counts for measurements, not for evidence — under 40), L163/L174 `131ea876`, L177 `0be9bd0`, L178 `93a10b6`,`e6be059`,`02b4339`,`bbefcee`, L180 `e987a27`, L181 `0be9bd0`, L183 `68d38c3`, L244 `cb80d0d`,`da92035`, L245 `4bda5f6`; bare files L31 `SCORECARD.md:643-661`,`LOG.md:1864-1869`, L59 `SCORECARD.md:643-693`, L60 `LOG.md:1864-1869`, L85 `LOG.md`, L189 `SKILL.md`, L191 `LOG.md`, L196 `PROVINCE.md`; other L137 `merge/souji/`, L140 `considerthese/`, L145 `knowledge/`. Fenced lines 118-124 are invisible, so `corpus/SOURCES.md` written there adds nothing.

Landed-changes row 92 `` `<integration>` `` is outside the measurements section. It is not a measurement miss and it is not an evidence pointer.

Span dump that classifies the measurement rows (same `COMMIT` / `BACKTICK` objects the tool uses):

```
L103  COMMIT ca4369a                         -> 1 span, does not qualify
L105  COMMIT 99efe06  plus 10 other spans    -> qualifies
L106  7 spans, none a whole-span commit      -> does not qualify
      (ca4369a is inside the python3 span)
L107  6 spans, none a whole-span commit      -> does not qualify
```

## r39 violation table (check before filing)

Run:

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-report-contract.py \
  --report <abs r39 report> \
  --shonen /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md
```

Expect stdout `check-*=PASS` seven times, `SUMMARY checks=7 pass=7 fail=0`, rc 0. Any `FAIL` is rc 1 with `detail-*` on stderr.

| # | If the report does this | predicate | detail (as the tool prints it) |
|---|---|---|---|
| 1 | Any of the six headings missing, duplicated, or not in the order above. `## Before — after measurements` (emdash, no ASCII `->`). `## Sources and frontier`. `## Trend verdict` (singular). `## Work performed (...)` | sections | `<key> headings=N expected 1` or `heading order ... not canonical` |
| 2 | Those six headings present only inside a fence or an HTML comment | sections | same, headings=0 |
| 3 | No heading matching `^shonen\b`, or more than one | shonen-boxes | `## SHONEN sections=N expected 1` |
| 4 | Checkbox lines in that section not equal to box lines in `SHONEN.md` (today 4: lines 5, 7, 9, 11). An extra `- [ ]` fails the same way as a missing one | shonen-boxes | `box lines=N expected 4` |
| 5 | Mark other than `[x]` / `[X]` / `[~]` / `[ ]` | shonen-boxes | that line is not counted, so the count fails as in 4 |
| 6 | Trend section absent, or a trend line missing | trends | `no trend verdicts section body` or `missing verdicts: ...` |
| 7 | Separator is ASCII `-` (`expansion - improved`) instead of `:` or U+2014 | trends | `missing verdicts: expansion` (the line is ignored) |
| 8 | First token after the separator is not one of the four verdict tokens (`expansion: not improved`) | trends | `expansion line opens with 'not', not a verdict token` |
| 9 | Same trend matched twice | trends | `duplicate expansion verdict` |
| 10 | No `## Stale-lane` / `## Stale lane`, or the heading's body is blank and no `Stale-lane: <nonspace...>` line exists | stale-lane (and sections, if the heading is gone) | `no stale-lane line` |
| 11 | Before/after section has no pipe-row with at least two backtick spans and one span that is only `[0-9a-f]{7,64}` | measurements | `no row with a measured commit and a counting command` |
| 12 | The only hashes are inside the command span, or are uppercase, or are shorter than 7, or the row has a single backtick | measurements | same as 11. r38 survives only because line 105 has a standalone `` `99efe06` ``. Copying r38 lines 106 and 107 without a row like 105 fails the gate |
| 13 | Work-performed body has 0 or 4 or more distinct `C1`..`C9` | claims | `claim ids=N expected 1-3` |
| 14 | Claim ids written only under Landed changes or later sections | claims | `claim ids=0 expected 1-3` |
| 15 | No backtick whose first token starts with `census/` `corpus/` `tools/` `tests/` `.ufo/`, and no backtick whose first token is 40-64 lowercase hex | evidence | `no evidence pointer` |
| 16 | Those pointers exist only inside a fence (r38 lines 118-124) | evidence | same as 15 if nothing else qualifies |
| 17 | Relying on a 7-39 hex hash, `SKILL.md`, `LOG.md`, `SCORECARD.md`, `PROVINCE.md`, or an absolute path as the sole pointer | evidence | same as 15. r38's `` `99efe06` `` does not count here |

Not violations (r38 did all of these and still passed): extra `##` sections; SHONEN box text that does not match `SHONEN.md`; trend prose on following lines; a stale-lane body that also repeats the `Stale-lane:` line form; C2/C3 measurement rows with no standalone commit as long as one other row has one; claim ids repeated outside Work performed; short hashes next to real evidence pointers.

Safe minimum, from the tool's own conforming selftest (`SELFTEST_REPORT`, lines 276-309), which case `conforming` passes:

- headings exactly `## Work performed`, `## Landed changes`, `## Before -> after measurements` (ASCII `->` or U+2192 both normalize), `## Sources & frontier`, `## Trend verdicts`, `## Stale-lane`, in that order
- work-performed body names `C1` and/or `C2` and/or `C3` only (1-3 distinct)
- one measurements row with a backtick span that is only 7-64 lowercase hex, plus at least one other backtick on that same row
- three trend lines `- expansion: <token>`, `- quality: <token>`, `- discernment: <token>` with token in {`improved`,`harmed`,`unchanged`,`unprovable-but-better`}
- one `## SHONEN` and exactly four `- [x]` / `- [~]` / `- [ ]` lines (current `SHONEN.md` count)
- `## Stale-lane` followed by a non-blank line
- at least one backtick path under `census/` `corpus/` `tools/` `tests/` or `.ufo/`, outside a fence

## Scratch

No `/fast/scratch/hyaku/souji-r39/W1ScoutReportGate` tree. The `/tmp/w1rg-*` captures used for rc 1 and rc 2 were deleted in those commands.
