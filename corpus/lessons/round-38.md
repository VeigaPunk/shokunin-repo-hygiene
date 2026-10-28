# Round 38 — commit-arm citations, the drift write envelope, record-validation discrimination

author: souji L1 (SoujiR38), hyaku run 11, attempt 1. Lane base
`ca4369a9296011644636711a624da6a8074e8e2a`; frozen contract `census/round-38/preregistration.txt`
(freeze commit `4090ee5b04ca3205d61c044b89fd9f318cf9850c`, amendments A0-A3 appended after the wave
seats that produced them). Fresh-start round: the r37 non-author spot-check (admitted, eight routed
defects) and the r37 lesson's named limits were read first.

## Claims

- **C1 calibration (score 7, the lowest non-retired axis).** r37 reconciled ten self-assessment
  cells but named the missing arm: "the schema binds an expected token to both a citation line and
  a receipt blob, and a commit id is in neither" — a measured-commit cell naming a revision where
  the receipt does not exist, or reads another value, stayed unverifiable (routed defects 2, 7).
  The reconciler gains an optional eighth register cell: the commit must resolve
  (`COMMIT-UNRESOLVED`), be an ancestor of the audited revision (`COMMIT-NOT-ANCESTOR`), be named
  on the anchored line (`COMMIT-UNNAMED`), and the receipt blob **at that commit** must exist
  (`COMMIT-RECEIPT-ABSENT`) and carry the expected token (`COMMIT-RECEIPT-DISAGREES`). Ten routed
  cells are reconciled append-only (SCORECARD, LOG, QUALITY). Counter:
  `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev <landing> --register
  census/round-38/cells.tsv --register-rev 4090ee5b04ca3205d61c044b89fd9f318cf9850c` →
  `SUMMARY cells=10 mismatches=0`, rc 0 (`census/round-38/records/c1-after2.txt`). Base control
  (`c1-before.txt`): `cells=10 mismatches=10`, rc 1; vacuity control (`c1-vacuity2.txt`):
  `mismatches=9`, rc 1. Fixture `tests/fixtures/r38-citation-commit.py`:
  `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED`; the r37 fixture stays 16/16.
- **C2 operability (score 8).** The r37 named limits name three defects in the drift tool's output
  envelope, each reproduced on the r37 blob before any repair: a `--json` FIFO blocked a blocking
  `O_WRONLY` open forever (`timeout 8` → rc 124); `--record X --json X` replaced the record with
  JSON and exited 0; and the module docstring's exit-2 enumeration omitted four classes the code
  raises (routed defect 6). The open is now `O_NONBLOCK` with a post-open `S_ISREG` refusal, the
  output must not alias the input by resolved path or inode, and the docstring names every class.
  Counter: `python3 -B tests/fixtures/r38-drift-write-envelope.py --base-tool <r37 blob>` →
  `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3`, rc 0
  (`c2-after3.txt`). The three behavioural base failures are `fifo-json-refused`,
  `record-alias-refused` and `docstring-enum`; the other three are class-name differences on
  behaviour the base already had (`BASE-BEHAVIORAL` line, `c2-base-composition.txt`).
- **C3 coverage (score 8).** The tool's record-validation arm — three TOTAL/REPO cross-checks and
  the duplicate-name refusal — is never exercised by the r37 discrimination fixture (its
  `record()` helper always writes a consistent TOTAL and never repeats a name), so the four
  record-validation mutants all survive that fixture's six cases. This is a coverage move on the
  tool's documented refusal surface, not an operability move (the r25 axis-attribution lesson).
  Counter: `python3 -B tests/fixtures/r38-drift-mutants.py --fixture
  tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py` →
  `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0`, rc 0 (`c3-after2.txt`), with
  `tests/fixtures/r38-drift-record.py` at `cases=10 pass=10 fail=0`. Base control (`c3-before.txt`):
  `killed=0 survived=4 pristine=ok`.

## Gate

New sources opened this round, read from the installed man pages on this host (`man 2.13.1`,
`git 2.56.0-1`, Linux man-pages 6.19) with the canonical URL recorded; the line numbers are from
`MANWIDTH=100 man <page>` and the live HTML pages were fetched for the same 6.19 text.

| id | source (URL) | access | located quote (<=25 words) | verdict |
|---|---|---|---|---|
| S239 | git-merge-base(1) § OPTIONS `--is-ancestor` — https://git-scm.com/docs/git-merge-base#Documentation/git-merge-base.txt---is-ancestor | 2026-10-28 | "exit with status 0 if true, or with status 1 if not" (§ OPTIONS, lines 41-43) | **admit** — the arm must read status 1 as not-an-ancestor and any other non-zero as an error, which is why it resolves the object first |
| S240 | git-cat-file(1) § OPTIONS `-e` — https://git-scm.com/docs/git-cat-file#Documentation/git-cat-file.txt--e | 2026-10-28 | "Exit with zero status if <object> exists and is a valid object." (§ OPTIONS, lines 39-41) | **admit** — an unresolvable commit cell is a distinct class from a non-ancestor, and the fixture keeps the two cases apart |
| S241 | fifo(7) § DESCRIPTION — https://man7.org/linux/man-pages/man7/fifo.7.html | 2026-10-28 | "Normally, opening the FIFO blocks until the other end is opened also." (§ DESCRIPTION, line 16; roff 27-29) | **admit** — the exact blocking behaviour the r37 blob reproduced as a hang, and the nonblocking alternative the repair takes |
| S242 | open(2) § ERRORS `ENXIO` — https://man7.org/linux/man-pages/man2/open.2.html | 2026-10-28 | with O_NONBLOCK plus O_WRONLY set, "the named file is a FIFO, and no process has the FIFO open for reading" (§ ERRORS, lines 544-545; roff 1219-1222) | **admit** — the errno branch the tool now classifies as JSON-NOT-REGULAR instead of blocking |
| S243 | pipe(7) § DESCRIPTION — https://man7.org/linux/man-pages/man7/pipe.7.html | 2026-10-28 | "Nonblocking I/O is possible by using the fcntl(2) F_SETFL operation" (§ DESCRIPTION, lines 27-33) | **reject** — that is read/write readiness on an open pipe, not the open-time block or ENXIO the refusal needs; flip: the page states the open-time contract |

Row changes: S239-S242 new tier-A `mined` rows, S243 new and `rejected`; no existing row's
`status`, `recheck` or `used-by` cell changed. `used-by` for S239-S242 is this lesson (C1 rests on
S239/S240, C2 on S241/S242). Registry grep count 162 → 167; census exit 0 both ends (the report
carries the commands and exit codes). Two curation notes from the source seats, recorded rather
than acted on: `man 7 fifo` and `man 2 open` already carry rows at scope-adjacent URLs (the census
warns W04, which is allowed), and the Python `os.open` page was opened and is **not** a valid
source for either fact — it defers to `open(2)` and states no FIFO-open sentence
(`W1ScoutFifoDocs`), so no row was written for it.

## Mistakes

### M1 — a fixture assertion that cannot occur on one line (vacuous)

**Class:** vacuous. The first `tests/fixtures/r38-drift-record.py` success cases asserted the token
`SUMMARY record_repos=2`; the tool prints `SUMMARY record=<path> record_repos=2 ...`, so the token
never occurs and three PASS-expected cases failed for a reason unrelated to the tool.
**Evidence pointer:** first local run `SUMMARY cases=10 pass=7 fail=3`, each failure
`missing=['SUMMARY record_repos=2']`.
**Captured-by:** none at the time — the fixture had no oracle for its own expectations.
**Fix:** assert `SUMMARY` and `record_repos=2` separately; the repaired run reads 10/10.

### M2 — a fixture that silently graded an empty cell (survivor)

**Class:** survivor. The commit-arm fixture built the "not an ancestor" case with
`git rev-parse "c0^{tree}"` where `c0` was already a hash, so the revision was invalid, the dangling
commit cell came back empty and the tool skipped the arm for a row that then passed.
**Evidence pointer:** `case-commit-not-ancestor=FAIL rc=0 want_rc=1 missing=['COMMIT-NOT-ANCESTOR']`
with `SUMMARY cells=1 mismatches=0`.
**Captured-by:** the case's own expected class, before any after-data.
**Fix:** `c0 + "^{tree}"`; the case reads `COMMIT-NOT-ANCESTOR` and the fixture is 14/14.

### M3 — an expectation that disagreed with the documented class (stale-premise)

**Class:** stale-premise. `json-directory` expected `JSON-NOT-REGULAR` while the code classified an
`EISDIR` open failure as `JSON-UNWRITABLE`; the docstring and the case disagreed about one input.
**Evidence pointer:** `case-json-directory=FAIL rc=2 ... REFUSAL JSON-UNWRITABLE: [Errno 21]`.
**Captured-by:** the fixture case (it compares the class, not only the exit code).
**Fix:** classify `ENXIO` and `EISDIR` as `JSON-NOT-REGULAR` (tighter, and what the docstring says);
`ELOOP`/`EACCES` stay `JSON-UNWRITABLE`.

### M4 — a number that never lived in the named fixture (number-drift)

**Class:** number-drift. The C3 narrative and the record fixture's docstring said a record mutant
"survived the r37 fixture 12/12"; the r37 discrimination fixture has six cases
(`SUMMARY cases=6 pass=6 fail=0`, blob stable at `ca4369a` and `4090ee5`). The 12 belongs to the r36
and r38 envelope fixtures. **Evidence pointer:** wave-1 seat `W1ExecC3Battery` §4 F1.
**Captured-by:** none in the round — the number was copied from a sibling fixture, exactly the class
C1 exists to repair, living inside this round's own instrument.
**Fix:** corrected in the fixture docstring and in prereg amendment A0; the argument is unchanged
because the four mutants survive all six cases.

### M5 — a case narrower than the claim it certifies (claim-wider-than-counter)

**Class:** claim-wider-than-counter. The first `docstring-enum` case read
`source.split('"""')[1]` and matched substrings, so it false-rejected a raise form inside a comment
(a1), accepted a module constant as the docstring (b1), accepted a doc-only phantom class (d),
accepted a prefix (d2), and missed the tool's second exit-2 idiom `REFUSAL <TOKEN>:` on stderr (c2).
Wave-1 seat `W1RevDocstring` measured all eleven variants. **Captured-by:** the seat, not a rule.
**Fix:** prereg amendment A1 — the case now reads `ast.get_docstring(clean=False)`, drops comment
tokens, collects both idioms, removes the docstring token from the code text, and matches whole
tokens in both directions. Landing 12/12; a1 now PASS; c2, d and d2 FAIL
(`census/round-38/records/a1-docstring-variants.txt`). Underscore-token raise forms and
`argparse`'s own exit 2 remain outside the case (named limits).

### M6 — a base-arm count read as if every unit were behavioural (attribution)

**Class:** attribution. The C2 evidence sentence "the base receipt itemises the six failing cases"
implies all six reproduce the routed defects. Wave-1 seat `W1CritC2` measured the split: three are
behavioural (hang, destroyed record, missing doc tokens) and three are class-name differences on
behaviour the base already had. **Fix:** A3 publishes `BASE-BEHAVIORAL` and `behavioral_fail=3` in
the receipt (`c2-base-composition.txt`); the report states the composition.

## Adjudications (wave 1, 42 seats, 0 dead)

- **C1 (calibration) — instrument strengthened by the wave, claim predicate unchanged.**
  `W1ExecC1Receipts` re-derived all ten rows (token present at the named commit, all ten ancestors of
  both the base and the landing), and `W1MutCounter` killed five commit-arm mutants 5/5 while
  reporting two discriminator facts: the receipt-at-commit cases shared `ANCHOR-ok` and were
  co-saturated with `COMMIT-UNNAMED` (amendment A2 gives them anchors that name their own commits),
  and all ten register rows carry `commit == receipt_rev`, so the live register cannot distinguish
  the arm from the receipt arm. `W1CritC1` executed the cheapest forged pass: an author who writes
  the same line and the same `commit` cell can claim a receipt-owning commit and leave the defective
  commit in the prose, and the counter scores 0. Both facts are named limits below, not fixes: the
  register was frozen before data, and no counter can police an author who will not name the
  revision they are claiming about.
- **C2 (operability) — case tightened twice.** `W1MutEnvelope` killed all four C2 repair mutants
  (no survivor) and `W1RevDocstring` produced the eleven-variant table behind A1. `W1CritC2` showed
  the base failures are 3 behavioural + 3 class-only (A3) and that a 16 s sleeper would be read as a
  hang: the 15 s bound cannot distinguish "blocked" from "slow", which is a named limit.
- **C3 (coverage) — axis confirmed, magnitude narrowed.** `W1CritC3` found `M7` (the TOTAL-repos
  check) already dies on the pre-existing r36 fixture, so the marginal new coverage is three
  classes (regs, prunable, duplicate-name), not four; the frozen kill rule (`base_killed=0` against
  the r37 fixture) and the claim's fixture-scoped wording hold as written.

## Frontier

SOURCES census before → after: 162 rows, rc 0 → 167 rows, rc 0. Rows added by tier: A ×5
(S239-S242 admitted, S243 rejected); touched old→new: none. No `ground: F<k>` line moved: the four
admitted rows ground the C1/C2 repairs, not new frontier ground, so no F row advances. Mined
mistake: M4 (a number copied from a sibling fixture). Assimilation: none this round — the
`merge/souji/` package's staged entries do not touch citation auditing or a tool's output
envelope, and adopting one would not serve a frozen claim; the package stays unadopted and no row
from `SOURCES.append.md` was appended.

## Named limits (disclosed, status-neutral)

- **The commit cell is self-authored.** The counter binds a row to the commit it *names*; an author
  who names the receipt's own revision cannot be caught (`W1CritC1` DEMO2, executed). `mismatches=0`
  therefore means "the ten rows are faithful to the commits they name", not "no stale prose
  survives anywhere in the lane".
- **`commit == receipt_rev` on all ten rows**, so the live register does not exercise the arm's
  revision discrimination; only fixture case R6 (`commit=c2`, `receipt_rev=c1`) does. Routed to r39.
- **The C1 base bound was frozen at `mismatches>=6`** while the measured constant was 10; the
  tighter number was available pre-freeze and was not used (`W1CritSizing`). The predicate is not
  re-written after data.
- **The C2 15 s bound conflates blocked with slow** (`W1CritC2`: a 16 s sleeper reads as a hang), and
  `base_fail` mixes behavioural and class-only failures — A3 publishes the split, but the frozen
  kill rule still counts both.
- **The docstring case binds textual token presence**, not that each token is reachable or that its
  trigger is documented (M5); underscore-token raises and `argparse`'s own exit 2 are outside it.
- **C3's marginal coverage is three classes**, not four: the TOTAL-repos check is already killed by
  the r36 fixture (`W1CritC3`). The fixture's other record rules (comment/blank skipping, optional
  TOTAL) are asserted but not mutation-scored.
- The ten reconciled cells are the ones the r37 spot-check routed and the lane owns; the r37
  report's own cells are fleet-repo bytes outside this round's write scope and are carried as an
  errata section in the round-38 report, not claimed.

## Corrections after wave 1 (appended 2026-10-28)

- **C1 composition, disclosed (wave-1 seat W1CritCorrections Q2).** Of the ten reconciliation rows,
  four bind cells that were stale at the base — the three LOG `R38-C1-7/8/9` lines (the round-37 C2
  bullet quoted the six-case draft's counts) and `R38-C1-10` (the Q84 evidence cell). The six
  SCORECARD rows (`R38-C1-1`-`6`) re-cite values the lane already held at the freeze (`escapes=9`,
  `base_fail=9`, `killed=6`, `survived=0`, `cases=16`, `cells=11 mismatches=0`), which is the r33 M3
  artifact: they add a commit binding, not a corrected number. The cell class routed defect 2 names
  — the measured-commit cells (`0be9bd0` in the r37 rows) — is carried by **no** row and survives;
  the arm is demonstrated by fixture case R6 only, and all ten register rows carry
  `commit == receipt_rev`. The claim's frozen predicate (`cells=10 mismatches=0`) holds; the
  calibration *credit* for a cell repair is four rows, not ten.
- **A4 (record FIFO TOCTOU, seat W1SentEnvelope F1/R3).** `parse_record`'s `isfile`-then-`open` pair
  hung forever when the path was swapped to a FIFO; the record is now opened `O_RDONLY|O_NONBLOCK`
  with an `fstat` regular-file check. Every existing case is unchanged (10/10).
- **A5 (battery kill gate, seat W1RevBattery).** A fixture that printed one `=FAIL` line, a SUMMARY
  and then crashed scored `killed`; a kill now needs the fixture's own `fail=N` with `N > 0` and no
  traceback. Four mutants still 4/4.
- **A6 (record fixture opacity, seat W1RevRecordFixture F1/F2).** The record filename carried the
  case name, so a name-inferring stub passed 10/10 without reading the file; names are opaque now
  and the refusal cases assert the exact message values.
- **A7 (counter envelope and matching, seat W1SentCounter S1/S3/S4).** `receipt_rev` is now bound
  (resolve + ancestor), the expected token is matched against the SUMMARY line cut at its first
  comment marker (the `# expected cells=3` tail no longer satisfies it; the r37 fixture's
  two-field `cases=21 pass=21` still does), and the register is opened `O_NOFOLLOW|O_NONBLOCK` with
  an `S_ISREG` check (a FIFO register used to hang). Evidence:
  `census/round-38/records/a7-counter-fixes.txt`.

### Additional named limits (appended after wave 1)

- **Post-guard rename race (`W1ExecAliasMatrix` `info-rename-swap`).** Alias detection is
  invocation-time; an actor that renames the record onto the `--json` path after the guard still
  loses it. 52/52 invocation-time spellings are refused; the race is outside the claim.
- **The measured-tree guard is a path check while the writer re-walks the path**
  (`W1SentEnvelope` F2/R2: 31 of 60 runs wrote the JSON inside `--root` after a directory swap;
  F3: a `--json` path in the gitdir of a measured repository is written). F4: a write that fails
  after `ftruncate` leaves the target empty (data loss on error). These are real residuals of the
  envelope, not of the three routed defects.
- **Any blob carrying a SUMMARY line can be a "receipt"** (`W1SentCounter` S2): the counter checks
  the named blob, not that the blob is a receipt. Author-chosen evidence is the arm's design limit.
- **`--json ""` is silently ignored** (`W1RevEnvelope` F1) and refusals after the measurement emit
  the SUMMARY first (F2); both are cosmetic and outside C2.
