# R41connector02 — cross-claim routed-defect scan (souji round 41)

Freeze commit measured: `e2a74312af4233963e44e4dbb38838ece07b8bd2` (read via `git grep` / `git show`; lane not modified).
Scope: routed defects in `corpus/lessons/round-38-verifier-spotcheck.md` §Routed (R1–R16), `round-39-verifier-spotcheck.md` §Routed (D1–D3), `round-40-verifier-spotcheck.md` §6 (R40-D-PRUNE, R40-D-C1-BEFORE, R40-D-FREEZE, R40-D-TOTAL). Excluded as covered by C1–C3 or R1: R40-D-PRUNE clause 1 (C1 I1), R40-D-C1-BEFORE (C1 I3), R40-D-FREEZE freeze-grammar (C2), R40-D-TOTAL (R1).
Verdict: **5 open routed items + 3 cross-round patterns; 1 attack reproduced (M40-12).** Nothing was edited; no git/jj mutation; no candidate written.

## Closed at freeze (not reported as open)

Each row below has an appended correction or an instrument change at the freeze commit:
- r38 R2 → `corpus/lessons/round-38.md:287` (R39-C1-02); r38 R1 → `round-38.md:285` (R39-C1-01); r38 R5 → `round-39.md:49` (R39-C1-05); r38 R6 → `SKILL.md:278-281` (4 registry rows); r38 R7 receipt-path prose → `round-39.md:51` (R39-C1-07); r38 R8 → `census/round-38/preregistration.txt:229` (A10); r38 R9 → `census/round-38/preregistration.txt:231` (A11); r38 R10/R11 → r39 tool repair (r39 spot-check §C2 table); r38 R12 → `SCORECARD.md:739` (R39-C1-10); r38 R13 → `corpus/lessons/round-38.md`/`QUALITY.md:222` (R39-C1-11/12/13); r38 R14 → `round-38.md:289` (R39-C1-14); r38 R15 → `round-39.md:53` (R39-C1-15); r38 R16 → `corpus/lessons/round-36.md:176` (R39-C1-16); r39 D3 → `SCORECARD.md:785` (R40-CLAIM-D3 / R40-CELL-03, `commit_rows=`/`commit_hashes=`); M40-2 names the same routing.

## Open items (≤ 8)

### 1. R40-D-PRUNE, clause 2 (QUALITY criterion) — OPEN, not covered by C1
- Pointer: `corpus/lessons/round-40-verifier-spotcheck.md:72` (item 1, second sentence: "add a QUALITY criterion that a reject by 'already held' cites a reproducible count and compares version/scope"). `git grep -n -i 'already held' e2a7431 -- corpus/QUALITY.md` → no match. Last criterion at freeze: `git show e2a7431:corpus/QUALITY.md | grep -oE '^\| Q[0-9]+' | tail -1` → `| Q97`. C1 item I1 only requires a CORRECTION line and a registry row; it does not require the QUALITY criterion.
- Proposal: r42 appends the next free QUALITY id (Q98) with the reject-by-"already held" rule, citing `round-40-verifier-spotcheck.md`.

### 2. M40-12 — U+FFFD decoder value not asserted; surviving decoder mutant reproduced — OPEN, not covered by C3 (refusal sites) or R1 (M19–M21)
- Pointer: `corpus/lessons/round-40.md:168-173` (fix: "Next round's fixture must assert the exact decoded name/value … include the surviving decoder mutants"). `tests/fixtures/r40-drift-record-branches.py:12-14` documents the `replace` handler; cases at `:116-119` assert only `ABSENT` / `SUMMARY`/`record_repos=2`; no assertion on the decoded name.
- Attack (scratch only): the pristine tool's only record decode is `tools/souji-worktree-drift.py:148` `decode("utf-8", "replace")`. Three one-token mutants of that line were run against the frozen r40 fixture (`python3 -B fixture.py --tool <mutant> --work <dir>`):
  - pristine: `SUMMARY cases=8 pass=8 fail=0`, rc 0
  - `backslashreplace`: `SUMMARY cases=8 pass=8 fail=0`, rc 0 — **survives** (confirms M40-12)
  - `latin-1`: `SUMMARY cases=8 pass=6 fail=2`, rc 1 — killed, but both kills are a Python traceback in the tool, not a value assertion (`case-invalid-utf8-in-repo-name`, `case-invalid-utf8-in-comment`)
  - `ignore`: `SUMMARY cases=8 pass=7 fail=1`, rc 1 — killed by the `ABSENT` case (the stripped name matches a repo)
  - So r40's "latin-1 and ascii pass both arms" is not reproduced for latin-1 in this form; `backslashreplace` is the surviving one.
- Receipts: `.ufo/waves/round-41/w1/R41connector02/{pristine,mut_bsr,mut_latin1,mut_ignore}.out` with `SHA256SUMS`.
- Proposal: a residual sibling fixture asserts the decoded repo name equals the U+FFFD form (and the comment case is value-checked), with `backslashreplace` and `ignore` as named kill targets; it is not a C3 site and must not edit `r41-refusal-sites.py`.

### 3. R40-D-FREEZE residue — C3 base fixture path and digest not frozen — OPEN, invisible to C2
- Pointer: `census/round-41/preregistration.txt:38-46` (C3 block: Counter, Population, Control, Target, Kill, Predicate, Control — no base fixture path or digest). R1 block `:48-55` has the same gap. r40 requirement: `corpus/lessons/round-40-verifier-spotcheck.md:74` ("the exact C3 base fixture path+digest including TOTAL ordering and U+FFFD value assertions").
- Why C2 cannot see it: `census/round-41/c2-counter.py` key list (`Base, Counter, Population, Control, Target, Kill`) and finding classes (`FIELD-MISSING`, `COUNTER-DIGEST`, `POPULATION-DIGEST`, `CONTROL-NOT-RED`, `FROZEN-EDITED`, …) have no base-fixture key or class.
- Proposal: L1 records this as a named limit in the round-41 lesson (the frozen prereg is not edited); r42 adds a `Base fixture:` key and a `BASE-FIXTURE-DIGEST` finding class to the C2 grammar.

### 4. R39-D1 — stale "after" census receipt — OPEN, not in C1 items
- Pointer: `census/round-39/records/census-after.txt:3-4` reads `rows=173` / `W04=47`. Counting `^| S[0-9]` rows in `corpus/SOURCES.md` at `0242085` gives **174** (`git show 0242085:corpus/SOURCES.md | grep -cE '^\| *S[0-9]{3,}'`), the value the r39 spot-check cites. `corpus/lessons/round-39.md:44` says "170 -> 173". No appended correction names the receipt as pre-S250; `git grep -n 'W04=48\|rows=174' e2a7431 -- corpus/lessons/round-39*` matches only the spot-check. M40-2/M40-10 declare it "unprovable" and do not correct the receipt.
- Proposal: append a correction line to `corpus/lessons/round-41.md` naming `census-after.txt` as measured before S250 (`e9958ee`), with the value `rows=174 W04=48` at `0242085` and the counting command.

### 5. R39-D2 — receipt header names a different revision — OPEN, not in C1 items
- Pointer: `census/round-39/records/final-tip-measure.txt:1` header "re-measure at `544104503a3ad70687ba399fcafd12bd30648169`"; the r39 SCORECARD/LOG state tip `0242085`. `git grep -n '5441045' e2a7431 -- SCORECARD.md LOG.md corpus/lessons/round-39.md` shows no appended correction; only the spot-check and M40-2 restate D2.
- Proposal: append one line in `round-41.md` naming `5441045` as the measured revision of `final-tip-measure.txt`, with `git diff --stat 5441045 0242085 -- census tools tests` as the bytes-unchanged check.

### 6. Cross-round pattern A — a count is measured before the last registry append (r38 → r39 → r40)
- Instances: r38 R1 — frontier reads "162 -> 167", tip measures 170 (`round-38.md:64,285`), S244–S246 appended after; r39 D1 — `census-after.txt` rows=173 before S250 (item 4); r40 M40-10 — `census/round-40/records/census-after.txt` reports rows=178/W04=49 "before W2 added corrective rows S255-S257", final `census-final.txt` 181/W04=52.
- Live state: `corpus/SOURCES.md` at freeze has 181 `S`-rows (`git show e2a7431:corpus/SOURCES.md | grep -cE '^\| *S[0-9]{3,}'`). The frozen Frontier start receipt `census/round-41/records/census-before.txt` carries a W04 listing but no line beginning `rows=` (`git show e2a7431:census/round-41/records/census-before.txt | grep -E '^rows='` → empty), so the count the pattern tracks is not stated in that receipt.
- Proposal: r42 counter binds any census receipt's `rows=`/`W04=` to the registry row count at its `measured_at` revision and refuses a receipt that predates a later `corpus/SOURCES.md` commit; r41 L1 states the frozen census value in the round lesson as the last step.

### 7. Cross-round pattern B — receipts name scratch paths; prose correction without re-run (r38 → r40)
- Instances: r38 R7 — `census/round-38/records/consumers-after{,2..6}.txt:14` run `r37-drift-escapes.py --base-tool /fast/scratch/hyaku/souji-r38/...` (not re-runnable); closed only by prose at `corpus/lessons/round-39.md:51` (R39-C1-07), receipts unchanged. The same substring recurs in round 40: `git grep -l '/fast/scratch' e2a7431 -- census/round-40` lists `records/c1-after-d.txt`, `c1-after-e.txt`, `c2-after-d.txt`, `c2-after-e.txt`, `c3-after-d.txt`, `c3-after-e.txt` (plus wave JSON). I did not classify each match as a command line versus captured output.
- Proposal: a gate lint over committed receipts (`census/round-*/records/*.txt`) that refuses a `## python3 …` / command line naming `$HYAKU_SCRATCH`, `/fast/scratch` or another reaped path; r42 re-runs affected consumers from a revision.

### 8. Cross-round pattern C — in-place edits of append-only artifacts (r38 → r39)
- Instances: r38 R9 — `census/round-38/preregistration.txt` replaced a frozen sentence in place ("must be tighter-only." → "is tighter-only unless stated otherwise."), corrected by appended A11 (`:231`); r38 R16 — `corpus/lessons/round-36.md:23` rewritten in place, corrected by R39-C1-16 (`:176`), which states that from r39 an in-place lesson edit is a routed defect.
- Mechanical check at freeze: C2's `FROZEN-EDITED` covers only Counter/Population blobs (`c2-counter.py` finding list). Lessons and preregistration prose have no equivalent check. Deletion-bearing commits to round lessons since r38 (`git log --numstat -- corpus/lessons/round-3[89].md corpus/lessons/round-40.md`) include `9b44320` (58 lines), `50972f0` (13), `d86ef3e` (6); these are within each round's filing commit, so they are not proven violations.
- Proposal: r42 counter over `git diff --numstat <prior-close> <freeze> -- corpus/lessons census/*/preregistration.txt`, refusing any hunk that deletes a line from a previously closed file.

## Commands run (read-only, lane not mutated)

- `git -C souji-shokunin rev-parse HEAD` → `e2a74312af4233963e44e4dbb38838ece07b8bd2`
- `git grep -n` over `e2a7431` for: `r38-(citation-commit|drift-write-envelope|drift-record|drift-mutants)` (SKILL.md: 6 matches incl. rows 278–281); `tighter-only`, `A10`, `A11`; `round-36.md` correction; `fcdecaa` (SCORECARD:739); `cases=9 pass=3 fail=6`; `Q9[89]|Q10x` (none); `already held` (QUALITY: none); `commit_rows|commit_hashes` (SCORECARD:785); `FFFD`/`ufffd`/`replace` in `tests/fixtures/r40-drift-record-branches.py`.
- `git show e2a7431:tools/souji-worktree-drift.py | sha256sum` → `b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6` (matches the prereg pin).
- Row counts: `git show e2a7431:corpus/SOURCES.md | grep -cE '^\| *S[0-9]{3,}'` → 181; `git show 0242085:corpus/SOURCES.md | grep -cE ...` → 174.
- `git show e2a7431:census/round-39/records/census-after.txt | sed -n 3,4p` → `rows=173`, `W04=47`.
- `git show e2a7431:census/round-40/records/census-final.txt` → 181 rows / W04=52 (`corpus/lessons/round-40.md:164`).
- Mutation attack (scratch `/fast/scratch/hyaku/souji-r41/R41connector02/m/`): `python3 -B fixture.py --tool {pristine,mut_bsr,mut_latin1,mut_ignore}.py --work <scratch>/work`; outputs copied to `.ufo/waves/round-41/w1/R41connector02/` (sha256 in `SHA256SUMS`).
- No tool was installed or upgraded. No `score-candidate.sh` run (no candidate filed).

## Verdict

- Calibration: items 1, 4, 5, 6 are calibration defects (filed numbers or revisions not reproduced by the cited receipt); none is covered by C1 items I1/I3/I4.
- Operability: item 3 is an operability gap in the C2 freeze grammar; item 7 is an operability gap in receipt reproducibility.
- Coverage: item 2 is a coverage gap in the r40 fixture; reproduced by a surviving `backslashreplace` mutant. Not covered by C3 or R1.
- Item 8 is a discipline pattern without a mechanical check at freeze.
- Routed items closed at freeze are listed above and were not re-opened.
