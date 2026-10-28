# Round 38 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Scope: souji round 38, hyaku run 11, attempt 1. Lane base `ca4369a9296011644636711a624da6a8074e8e2a`;
lane tip and `origin/master` at closure `fcdecaaf293f0fee3c39cc148ae91389e04ef63c` (branch `master`, jj-colocated).
Report `.ufo/reports/round-38/souji.md` (commit `6afdd3c6`). This reviewer wrote no lane file, ran no lane
gate (PROTOCOL.md §Gate standard, Closure consequence): a claim resting on a lane-owned instrument is
evidence-verified against its committed receipt, and the static facts around it are re-derived
independently. Every command below was run 2026-10-28 from `/home/vgpnk/Projects/shokunin` (fleet root) or
`/home/vgpnk/Projects/shokunin/souji-shokunin` (lane), read-only.

## Conformance (step 1)

| check | command | observed | verdict |
|---|---|---|---|
| report path + attribution | `git log --format='%an <%ae> %H %s' -- .ufo/reports/round-38/souji.md` | one commit `6afdd3c6`, `souji-shokunin <souji@shokunin.local>`, "round-38: souji report" | pass |
| report lands last | `%ci` of `6afdd3c6` vs of the lane tip | report committer `14:20:17 -0300` > tip committer `14:20:05 -0300` (author date `14:15:01` is the jj change-creation time) | pass |
| cited lane commits exist and are ancestors of the branch | all 25 distinct 7–40-hex tokens in the report: `git -C souji-shokunin rev-parse --verify <h>^{commit}` + `git -C souji-shokunin merge-base --is-ancestor <full> master` | 25/25 resolve to commits, 25/25 ancestor of `master` (`ca4369a`, `4090ee5`, `cb80d0d`, `828f86b`, `2843805`, `7b542e2`, `020cfd5`, `9b44320`, `99efe06`, `4bda5f6`, `8093c70`, `fcdecaa`, and the r37-era hashes, all `OK-ancestor`) | pass |
| lane pushed, no uncommitted round work | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git -C souji-shokunin status --porcelain` | `branch=master local=fcdecaa… remote=fcdecaa… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty | pass |
| `SHONEN` heading, one line per box | `grep -n '^## SHONEN' .ufo/reports/round-38/souji.md` → 186; four following `- [~]` lines; `grep -cE '^- \[[x~ ]\]' SHONEN.md` → 4 | `## SHONEN` + four `[~]` lines, each with a resolvable pointer (`SKILL.md`, S239–S243, `LOG.md` §Round 38, fixtures, `PROVINCE.md`); no `[x]`; `git diff --stat ca4369a fcdecaa -- SHONEN.md` empty | pass |
| prompt carries the template contract | `sed 's/{{FLEET_ROOT}}|{{ROUND}}|{{LANE}}/…/' templates/round-prompt.md` vs `.ufo/prompts/souji-round-38.md` §1–§5 | difference is only the rendered repo-path header and the rendered AXES sentence; §1–§5 verbatim, §2b frontier step included, §6 hyaku addendum appended (64–128 band, 256 ceiling, ≥25 % attack) | pass |
| prompt durability / attribution | `git log --format='%an %H %s' -- .ufo/prompts/souji-round-38.md` | `souji-shokunin` committed `068f75dc` "round-38: souji dispatch evidence" at 13:23:41, one minute before the launch line — the lane committed a fleet path outside its write scope | **defect R5** (status-neutral) |
| L2 route map vs MISSION | `MISSION.md:53-65`; `~/.omp/agent/config.yml` `agentModelOverrides` | MISSION states the ≥8-one-batched-call floor and class buckets it calls *advisory*; the prompt's concrete alias map is the run-11 label. The live config now reads `task/main/executor/… @m_flash`, `scout @m_grok`, so the prompt's `task @m_zfl` and its `@m_auto` review seats are stale labels | no protocol conflict (operator-owned routing) |
| report contract sections | `grep -n '^## '` | Work performed (9) · Landed changes (78) · Before → after measurements (98) · Sources & frontier (114) · Trend verdicts (142) · SHONEN (186) — required order holds; the r37 ledger (159) and errata (172) are interleaved extras | pass |
| waves on disk | `souji-shokunin/.ufo/waves/round-38/{w1-spec,w2-spec,w1-results}.json`; `ls w1|w2` | w1 spec 42 items / 42 reports / 42 result records, roles executor 10, reviewer 8, scout 6, scribe 6, critic 5, sentinel 2, mutation-tester 2, connector 1, revenger 1, simplifier 1; w2 spec 32 items / **31 reports** (`W2MutBattery` absent), roles reviewer 10, critic 10, mutation-tester 6, scribe 4, scout 2; total 74 (band 64–128), attack 43/74 = 58 %; no `w2-results.json` | corroborated, but **R3/R4** |
| driver digest (mutable log; this digest is the pointer) | `.ufo/watchdog.log` lines 1848, 1858 | `2026-10-28T13:24:13-03:00 launch souji round=38 pgid=3581930 driver=hyaku-inline attempt=1`; `2026-10-28T14:21:00-03:00 complete souji round=38; hyaku-inline attempt=1` | pass |
| fleet-repo write scope | `git log --author=souji --since=2026-10-28T13:00 --name-only` | `.ufo/reports/round-38/souji.md` (`6afdd3c6`), `.ufo/prompts/souji-round-38.md` (`068f75dc`) | report in scope; prompt is R5 |
| marker vs report | report body | names 3 claims, 21 lane commits, receipts, evidence pointers and a checkable tip | real report → status `ok` |

## Per-claim re-check

### C1 calibration (score 7, the lowest non-retired axis) — **re-measured by this reviewer**

Register `census/round-38/cells.tsv`: 10 rows, 8 columns (the optional `commit` cell is present on every
row). Independent re-derivation — this reviewer's own script, not `tools/souji-citation-reconcile.py`:
for each row, exactly one line of the named file at revision `R` contains the anchor; that line carries
`expected` as a whole token, names the receipt path, and does not carry `stale`; a `SUMMARY` line of the
receipt blob at `receipt_rev` carries `expected`. Commit cells: 40-hex, resolve, ancestor of `R`, named
on the anchored line (7-hex prefix), receipt-at-commit carries the token.

```
ca4369a9296011644636711a624da6a8074e8e2a   mismatches= 10  (all ten ANCHOR-COUNT hits=0)
99efe0676f439309a52f001b71bf0ba2ed8af47f   mismatches= 0   []
fcdecaaf293f0fee3c39cc148ae91389e04ef63c   mismatches= 0   []
```

Reported `mismatches=10` rc 1 → `mismatches=0` rc 0, vacuity `mismatches=9` rc 1, fixture
`cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED`: **agrees**, and the predicate also holds at the
actual tip, which no committed receipt measures (`c1-after8` names `99efe06`). The instrument is
byte-identical from the receipt revision to the tip:
`git diff --stat 99efe06 fcdecaa -- tools/ tests/ census/round-38/cells.tsv` → empty, so the receipt's
number is the tip's number; only the audited `SCORECARD.md` grew (+8 lines, additive) after it.
Static counts: `tests/fixtures/r38-citation-commit.py` has 14 cases (13 `case(` + 1 `check(`), matching
the receipt; `r38-counter-arms.py` has 6 (`cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED`).
Credit is partial and the lane says so: all ten rows carry `commit == receipt_rev`, so the live register
does **not** exercise the arm's revision discrimination (fixture case R6 only), and four rows repair a
cell that was stale at the base while six re-cite values the lane already held.

### C2 operability (score 8) — **evidence-verified + static re-derivation**

`census/round-38/records/c2-after7.txt` @ `99efe06`: `SUMMARY cases=12 pass=12 fail=0 base_cases=12
base_fail=6 behavioral_fail=3`, rc 0 — matches the report. Base arm, `c2-before.txt` /
`c2-base-composition2.txt`: six itemised base failures — `fifo-json-refused` hangs (`hung=True
elapsed=15.0s`, rc None), `record-alias-refused` exits 0 with `record_intact=False`,
`docstring-enum` `missing=['JSON-HARDLINKED','JSON-INSIDE-MEASURED-TREE','JSON-UNWRITABLE','USAGE']`,
plus three class-name-only differences; `BASE-BEHAVIORAL failed=3
cases=docstring-enum,fifo-json-refused,record-alias-refused`. Static re-derivation:

```
grep -oE 'Refusal\("[A-Z-]+' tools/souji-worktree-drift.py | sort -u
  -> 10 distinct classes: RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT,
     JSON-INSIDE-MEASURED-TREE, JSON-IS-RECORD, JSON-NOT-REGULAR, JSON-HARDLINKED, JSON-UNWRITABLE, USAGE
docstring exit map lists the same ten (plus the drift classes REGS-CHANGED/PRUNABLE-CHANGED/…)
open_nofollow: O_WRONLY|O_CREAT|O_NOFOLLOW|O_NONBLOCK, then fstat S_ISREG -> JSON-NOT-REGULAR
alias guard: realpath equality and (st_dev, st_ino) identity -> JSON-IS-RECORD
grep -cE '^\s+check\(' tests/fixtures/r38-drift-write-envelope.py  -> 12
```

The three routed envelope defects are closed at the tip. Residuals the fixtures do not reach are stated
by the lane (post-guard rename race, path-guard/writer re-walk, ftruncate-on-error, `--json ""`) and are
named limits, not claim failures. One mismatch the docstring/case pair does not cover is routed (R10).

### C3 coverage (score 8) — **evidence-verified + static re-derivation**

`census/round-38/records/c3-arms-filed.txt` @ `99efe06`: `SUMMARY cases=10 pass=10 fail=0`;
`SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0`; `rcs=0/0/0` — matches the report. Base
control `c3-before.txt`: `MUTANT M7..M10 killed=no rc=0 fails=0`; `SUMMARY mutants=4 killed=0 survived=4
pristine=ok`, rc 1. Static: `grep -cE '^\s+run_case\(' tests/fixtures/r38-drift-record.py` → 10;
`MUTANTS` holds exactly four single-defect entries (M7 TOTAL-repos, M8 TOTAL-regs, M9 TOTAL-prunable,
M10 duplicate-name); the base fixture `r37-drift-discrimination.py` has six cases (matching the A0
correction from twelve); record names are opaque (`mkstemp(prefix="record-", suffix=".tsv")`, A9), so a
name-inferring stub cannot pass; `git diff --stat 99efe06 fcdecaa -- tests/fixtures/r38-drift-record.py`
empty, so the receipt measures the filed fixture. Marginal coverage is three classes, not four (the
TOTAL-repos check already dies on the r36 fixture) — disclosed by the lane.

## Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration (claimed) | **improved** | register re-measured 10 → 0 mismatches at base and tip; the measured-commit arm exists with five classes, a 14-case fixture and a 6-case counter-arms fixture; four cells genuinely repaired, six re-bound (disclosed) |
| operability (claimed) | **improved** | three r37-named envelope defects closed with a base arm that reproduces all six failures (3 behavioural) on the pre-round blob; docstring and code now agree on all ten refusal classes |
| coverage (claimed) | **improved** | record-validation mutants 0/4 → 4/4 killed with `base_killed=0` and a pristine control; the fixture reads the file rather than the case name |
| depth | unchanged | not claimed; no `SKILL.md` decision table or knowledge entry added beyond the two registry rows |
| freshness | unchanged | not claimed; the round re-verifies its own instruments but adds no drift pin over an external surface |
| adjacency | unchanged | not claimed; the kama overlap is reported as adjacent, not absorbed (`## Adjacency note`) |
| harmed | **none** | `git diff --numstat ca4369a fcdecaa`: LOG +9/−0, SCORECARD +94/−0, QUALITY +8/−0, SOURCES +8/−1 (one blank line), SKILL +3/−2 (registry rows); only the two claimed tools changed under `tools/`; the five new fixtures are additions; `r36-*`/`r37-*` fixtures, `census/round-35`, `README.md`, `PROVINCE.md` and `corpus/lessons/round-36.md` byte-identical; no predicate, case id, token or exit code relaxed |

## Discernment spot-check (LEARNING.md)

| item | decision | re-opened source | agree? | reason |
|---|---|---|---|---|
| S241 fifo(7) § DESCRIPTION | admit (tier A, `mined`) | `MANWIDTH=100 man 7 fifo`, Linux man-pages 6.19 — line 16: "Normally, opening the FIFO blocks until the other end is opened also."; line 19-20 (roff 22-24): write-only nonblocking open "fails with ENXIO … unless the other end has already been opened" | **agree** | quote verbatim at the stated lines (14 words, ≤25); it grounds exactly the open-time block the r37 blob reproduced as a 15 s hang and the ENXIO branch the repair classifies |
| S244 git-merge-base(1) § OPERATION MODES `--is-ancestor` | admit (`mined`, `supersedes S239`) | `MANWIDTH=100 man git-merge-base`, git 2.56.0 — `OPERATION MODES` heading at line 20, `--is-ancestor` entry at 41-43; `OPTIONS` at 52 carries only `-a`/`--all` | **agree** | the correction is right and the quote is verbatim (23 words): `--is-ancestor` is not under § OPTIONS, so S239's locator was wrong; the lane found it and superseded rather than rewrote |
| S246 pipe(7) § DESCRIPTION | reject (`supersedes S243`) | `MANWIDTH=100 man 7 pipe`, Linux man-pages 6.19 — lines 31-33: "Nonblocking I/O is possible by using the fcntl(2) F_SETFL operation to enable the O_NONBLOCK open file status flag or by opening a fifo(7) with O_NONBLOCK." | **agree** | quote verbatim (18 words, ≤25) with the continuation S243 truncated; the page states read/write readiness on an already-open pipe, not the open-time block or ENXIO the refusal contract needs, and the row names the flip condition |

Sample: 2 admits + 1 reject, all three re-opened, **3/3 agree**, each with its ≤25-word quote located.
The S244/S246 existence is itself evidence against the report's sentence "the panel agreed on the four
admits and the reject": the wave panel's locators were wrong on two of the admits and on the reject's
quote, and the lane corrected them by supersession (R1) — good practice, overstated in prose.

Registry: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok
…/corpus/SOURCES.md`, **rc 0**, 170 rows
(`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 170; base 162; 47 W04
duplicate-URL warnings allowed, base 41). Rows added: 8, all tier A — S239, S240, S241, S242, S244, S245
`mined`; S243, S246 `rejected`; supersessions S244→S239, S245→S242, S246→S243. No pre-existing row's
`status`/`recheck`/`used-by` changed: `git diff --numstat ca4369a fcdecaa -- corpus/SOURCES.md` →
`8 1` with the single deleted line a blank.

## Trend verdicts

| trend | verdict | evidence |
|---|---|---|
| expansion | **unchanged** | registry growth is not expansion: no `knowledge/` entry landed (`git diff --name-status ca4369a fcdecaa -- corpus/knowledge` empty) and no `ground: F<k>` line moved (`corpus/README.md` untouched); the three new capabilities are capability rows, not corpus ground. The report's own numbers for this section are falsified — measured 162 → **170** rows and **8** added (6 `mined`, 2 `rejected`), not 162 → 167 / 5, and the census reads 47 W04, not 44 (R1) |
| quality | **improved** | three envelope defects closed against a base arm that reproduces six failures (3 behavioural); record-validation discrimination 0/4 → 4/4 with `base_killed=0`; the citation counter gains five commit classes (14-case and 6-case fixtures); the round superseded its own weak source rows (S244/S245/S246) and corrected Q84's evidence pointer append-only; every consumer is green at the final instrument bytes and no entry fails its re-check (C1 re-derives to 0 at the tip) |
| discernment | **improved** | wave 1 falsified four of the round's own instrument premises (A0–A3) and wave 2 falsified A1 itself (A8) — each disclosed as an amendment with a receipt; M1–M7 are mined with class, pointer, captured-by and fix; Q86–Q88 each cite a lesson; this non-author spot-check agrees on 2 admits and 1 reject. Overstated in prose: "four … (A0–A3)" ignores A4–A8 and "the panel agreed on the four admits and the reject" is contradicted by S244/S246 (R1) |

## Routed defects (status-neutral; the lane owes these in r39)

1. **R1 — the Sources & frontier section is numerically false.** Report lines 116-127 read "162 → 167",
   "A ×5", "rows touched none", "44 W04"; the tip measures **162 → 170**, **8** rows added (6 `mined`,
   2 `rejected`, three of them supersessions), and **47** W04. The disclosed-limits line says 169 and the
   lesson stops at "167 → 169" (`corpus/lessons/round-38.md:64,158,256`); **S246 appears in no lesson
   byte** (`grep -c S246 corpus/lessons/round-38.md` → 0). Append the corrected census block and name
   S244–S246 in the lesson.
2. **R2 — an unevidenced dead-seat number.** The report's opening line says "4 + 0 dead"; its own waves
   table says w1 dead 0 / w2 dead 0, and the disk shows 42/42 w1 reports and 31/32 w2 reports
   (`W2MutBattery` absent). Nothing supports 4; state the measured numbers and mark the missing seat.
3. **R3 — the report was filed before WAVE-DONE.** `## Filing note` records 11 of 32 wave-2 reports at
   filing and no `w2-results.json`; at closure 31 reports were on disk (27 written after the report's
   author timestamp) and the run-9/run-11 directive "file only after WAVE-DONE" still binds. The late
   seats' findings (this file's R7–R12, the five defects in `W2CritAdmission`, `W2RevHarm` F1–F6,
   `W2CritStale` F1–F5, `W2CritTrends`) are unintegrated.
4. **R4 — wave evidence is untracked.** `.ufo/waves/` is in the lane `.gitignore`, so the specs,
   dispatches, `w1-results.json` and all 74 seat reports exist only on this host; prompt §2 asks for
   them as committed wave evidence and §Evidence standard admits no pointer a fresh session cannot
   reach. Commit the specs/results/registry at least (as round 13 did before the ignore rule).
5. **R5 — the prompt was committed by the lane (r37 routed defect 8 repeated).** `068f75dc` adds
   `.ufo/prompts/souji-round-38.md` under `souji-shokunin`, outside the lane's write scope, while the
   r37 ledger row 8 claims "not repeated — this round committed no `.ufo/prompts/` path". Correct the
   ledger row by erratum and leave prompt commits to the integrator.
6. **R6 — the four claim counters have no gate-registry row.** `SKILL.md` gains only
   `r38-counter-arms`; `r38-citation-commit`, `r38-drift-write-envelope`, `r38-drift-record` and
   `r38-drift-mutants` are absent (`grep -cE 'r38-(citation-commit|drift-write-envelope|drift-record|drift-mutants)' SKILL.md`
   → 0). §Gate standard grades no gate conformant without its registry row at the lane's home.
7. **R7 — a receipt's base arm names a scratch path.** `consumers-after*.txt` run
   `r37-drift-escapes.py --base-tool /fast/scratch/hyaku/souji-r38/final/drift-r36.py`; `$HYAKU_SCRATCH`
   is reaper-deleted and `final/` is already gone, so the command is not re-runnable from committed
   bytes (the blob is `5f0dd45:tools/souji-worktree-drift.py`, per `W2CritAdmission` D5). Cite the
   revision, not the scratch file.
8. **R8 — the prereg's own evidence pointer is stale and its instrument table is incomplete.**
   `census/round-38/preregistration.txt:218-220` names `a7-counter-fixes.txt` (which reads "at
   `9b44320`", predating A7) instead of the regenerated `a7-counter-fixes2.txt`; and
   `tests/fixtures/r38-counter-arms.py` — the only fixture that kills the `RECEIPT-REV-*` guards — is in
   neither the prereg instrument table nor the lesson. Append A10 (the frozen sentence stays as filed).
9. **R9 — the frozen prereg was rewritten in place.** `git diff 4090ee5 fcdecaa --
   census/round-38/preregistration.txt` replaces the frozen sentence "…must be tighter-only." with
   "…is tighter-only unless stated otherwise." — a relaxation of the amendment rule inside the file that
   claims append-only treatment (`census/round-38/preregistration.txt`, A0 clarification). Restore the
   rule by appended amendment that names the superseded sentence; `PROTOCOL.md` allows no in-place edit.
10. **R10 — a docstring→condition mismatch the C2 case cannot see (r37 routed defect 6 residue).**
    `tools/souji-worktree-drift.py` documents `RECORD-MISSING` as "the record path cannot be read", but a
    non-existent record prints `REFUSAL RECORD-MALFORMED: … is not a regular file` (reproduced here:
    `python3 -B tools/souji-worktree-drift.py --root . --record nope.tsv` → that line, rc 2), and
    `tests/fixtures/r38-drift-record.py:119` asserts that class. `docstring-enum` binds the token set in
    both directions, not the class→input mapping. Fix the docstring or the class, and add the case.
11. **R11 — the citation counter never resolves `--rev`.** `git merge-base --is-ancestor` is read as
    "1 = not an ancestor, other non-zero = error" by the arm's own premise (S239/S244), but the code
    collapses every non-zero to "not an ancestor": a mistyped audited revision yields `mismatches=20`
    and rc 1 instead of a could-not-evaluate exit 2 (`W2RevHarm` F1, reproduced by that seat). `SKILL.md`'s
    exit row never declares that case. Resolve `--rev` with `cat-file -e <rev>^{commit}` and split exit
    1 from 128.
12. **R12 — SCORECARD finality labels and the last block's subset.** Four pointer blocks carry three
    finality labels; the last one ("Final tip `99efe06`") measures two commits behind the tip, and it
    drops the vacuity and eight-consumer arms without saying so. Values hold (instruments unchanged
    `99efe06..fcdecaa`), the labels do not (`W2CritStale` F1–F3). Fix by one appended line naming
    `fcdecaa` as the measured revision.
13. **R13 — residual stale literals the r38 corrections do not reach.** `LOG.md:1855` (`cases=9
    pass=3 fail=6`, no r37 receipt carries it), `LOG.md:1862`, and `corpus/QUALITY.md:209`'s "(0)" which
    reads the *fail* field as the escape count. Sweep them against the final receipts (`W2CritStale` F4).
14. **R14 — the C1 vacuity receipt misdescribes its own operation.** `c1-vacuity2.txt` says "register row
    1 expected token replaced by `mismatches=99`", but `mismatches=9` requires all three `escapes=9`
    rows (R38-C1-1/7/10), each emitting three classes; a faithful one-row substitution reads
    `mismatches=3`. Number real, description wrong (`W2RevHarm` F3); the terminal `c1-vacuity5.txt`
    names no operation at all.
15. **R15 — the Landed-changes table does not cover the round.** 9 of the 21 lane commits in
    `ca4369a..fcdecaa` are named nowhere in the report (`6949319`, `78ea25a`, `f10a3a8`, `20eea73`,
    `a512efb`, `9b9e2f8`, `cb5737a`, `be66886`, `c5050ea`), and the last row's commit cell is the
    placeholder `<integration>` — a row that cites no hash in the report whose own rule is "cited by
    hash, never by subject".
16. **R16 — r37 routed defect 4 is still owed.** No appended correction for the in-place rewrite of
    `corpus/lessons/round-36.md:23`; `git diff` confirms the file untouched this round, so the debt is
    open, not repeated. Land the appended entry in r39.

## Notes for the operator

- No promotion or mint is claimed or implied: all four `SHONEN` boxes are `[~]` (author-asserted) with
  resolvable pointers, and all four look checkable by a non-author — box 2 (an end-to-end task executed
  and logged) and box 3 (executable without oral context) are the two a reviewer could now write `[x]`
  on with named evidence. Promotion remains operator-owned.
- No axis is harmed and every declared claim verifies: C1 re-measured by this reviewer at the base, at
  the receipt revision and at the tip; C2 and C3 evidence-verified from committed receipts whose
  instrument bytes are unchanged to the tip, with the repairs re-derived statically. Verdict:
  **admitted**, with 16 routed defects the lane owes in r39 — R1, R2, R8, R9 and R15 are
  self-assessment/bookkeeping defects of exactly the class C1 exists to police.
