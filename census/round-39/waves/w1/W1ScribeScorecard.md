# W1ScribeScorecard — SCORECARD.md additions for round 39 (draft, advisory)

Seat: souji round 39, wave 1 (hyaku run 11). Role: scribe. Lane:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Axis: calibration. Leaf member — no dispatch.

Snapshot while this seat ran: HEAD `2201778e7736af82e7d8a42dec2494f115bf3923` at first read,
`d4c17557b92fd98044e4c8f0ddc79c6d75701b15` at report write (one commit landed mid-seat:
`d4c1755`, `census/round-39/c3-counter.py` + `tests/fixtures/r39-citation-rev.py` only).
`SCORECARD.md` at HEAD: blob `7417fe221833dcf7b3b5a43df88c07afc3ca8d52`, sha256
`994b606a83ab515b0c6cb52f5a640e8c2204294342550ea10c8773c8317361f7`, 739 lines, last line
`R39-C1-10 …`, file ends with `\n`. Scratch: `/fast/scratch/hyaku/souji-r39/W1ScribeScorecard`
(still on disk; contents named in §7). No tool installed or upgraded.

## 0. Behavior, in one paragraph

Item (a) is **already landed**: the `R39-C1-10` line exists at `SCORECARD.md:739`, added by
`c0b007b`, and reads CLOSED under the frozen item predicate at both revisions this seat saw — so
I did not duplicate it. Its two required tokens are on one line and its two supporting arms hold
(`fcdecaa` resolves, is an ancestor of HEAD, and `git diff --stat 99efe06 fcdecaa -- tools/ tests/
census/round-38/cells.tsv` is empty), but **one clause is imprecise**: `99efe06..fcdecaa` changes
`SCORECARD.md` plus six added `census/round-38/records/` receipts, not "SCORECARD/lesson bytes".
Item (b) cannot be filled from receipts at this revision — the C1 counter reads `open=2` with
`register_cells=0` at HEAD because `census/round-39/records/waves-{wait,capture}.txt` and
`census/round-39/cells.tsv` do not exist yet, and no `c1-after.txt` exists — so the measurements
table is drafted with the three frozen before-readings (one of which I re-measured) and explicit
`<L1: …>` placeholders for every after cell. Item (c)'s five capability rows are drafted from
predicates I ran: `r39-citation-rev` reads `cases=8 pass=8 fail=0` on HEAD bytes and
`cases=8 pass=4 fail=4` on the base blob; `r39-drift-record-rules` reads `cases=7 pass=7 fail=0`
on **both**, so its base-bytes discrimination is carried only by the c3 mutants — stated in the
row rather than glossed. Nothing was written to `SCORECARD.md`: the L1 integrates (§2, §3).

## 1. Checks run

Every command below ran from `/home/vgpnk/Projects/shokunin/souji-shokunin` (absolute paths in the
argv where the tool takes a root). Read-only git only; no mutating git/jj anywhere.

| # | command | observed output | verdict |
|---|---|---|---|
| 1 | `git rev-parse HEAD` | `2201778e7736af82e7d8a42dec2494f115bf3923` (first read) → `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` (report write) | lane moved once; recorded |
| 2 | `git log --oneline -S 'R39-C1-10' -- SCORECARD.md` | `c0b007b round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows` | (a) already landed before this seat |
| 3 | `git show d4c1755:SCORECARD.md \| grep -c '^R39-C1-10 '` | `1` | one anchored line, unchanged at the newer tip |
| 4 | `git merge-base --is-ancestor 99efe0676f439309a52f001b71bf0ba2ed8af47f fcdecaaf293f0fee3c39cc148ae91389e04ef63c` | rc 0 | `99efe06` is an ancestor of `fcdecaa` |
| 5 | `git merge-base --is-ancestor fcdecaaf293f0fee3c39cc148ae91389e04ef63c HEAD` | rc 0 | `fcdecaa` is an ancestor of the lane tip |
| 6 | `git diff --stat 99efe06 fcdecaa -- tools/ tests/ census/round-38/cells.tsv` | empty, rc 0 | instruments byte-identical across the pair — the line's core claim holds |
| 7 | `git diff --name-status 99efe06 fcdecaa` | `M SCORECARD.md`, `A c1-after4.txt`, `A c1-after8.txt`, `A c1-vacuity3.txt`, `A c2-after7.txt`, `A c3-arms-filed.txt`, `A consumers-after3.txt` (all under `census/round-38/records/`) | **falsifies the "SCORECARD/lesson bytes" clause**: no lesson bytes differ; six receipt blobs were added (F3) |
| 8 | `TMPDIR=$S python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch $S` | sixteen `ITEM … OPEN` lines (`ANCHOR-ABSENT` ×11, `FILE-ABSENT` ×5), `REGISTER cells=0 mismatches=0 commit_distinct=0`, `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358`, rc 1 | base control **reproduced byte-for-byte** against `c1-before.txt` |
| 9 | same counter, `--rev 2201778e7736af82e7d8a42dec2494f115bf3923` | `ITEM R39-C1-10 CLOSED` (and 01,02,05-16 CLOSED); `ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt`; `ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt`; `REGISTER cells=0 mismatches=0 commit_distinct=0`; `SUMMARY items=16 open=2 … register_cells=0 …`, rc 1 | **(a) predicate CLOSED**; C1 after-state **not reachable** at HEAD (F1) |
| 10 | `TMPDIR=$S python3 -B tests/fixtures/r39-citation-rev.py --work $S` | `case-rev-unknown=PASS` … `case-register-absent=PASS`, `SUMMARY cases=8 pass=8 fail=0`, rc 0 | 8/8 on HEAD tool bytes |
| 11 | `git show ed30b7f…:tools/souji-citation-reconcile.py > $S/base-citation.py` then `python3 -B tests/fixtures/r39-citation-rev.py --tool $S/base-citation.py --work $S` | `case-rev-unknown=FAIL rc=1 want=2 missing=['REV-UNRESOLVED']`, `case-rev-blob=FAIL …`, `case-rev-tree=FAIL …`, `case-register-rev-gone=FAIL rc=2 want=2 missing=['REV-UNRESOLVED'] out='REFUSAL USAGE: register … is not at 1111…'`, `SUMMARY cases=8 pass=4 fail=4`, rc 1 | fixture **discriminates** the base blob by 4 cases |
| 12 | `TMPDIR=$S python3 -B tests/fixtures/r39-drift-record-rules.py --work $S` | seven `case-…=PASS`, `SUMMARY cases=7 pass=7 fail=0`, rc 0 | 7/7 on HEAD tool bytes |
| 13 | `git show ed30b7f…:tools/souji-worktree-drift.py > $S/base-drift.py` then `python3 -B tests/fixtures/r39-drift-record-rules.py --tool $S/base-drift.py --work $S` | seven `case-…=PASS`, `SUMMARY cases=7 pass=7 fail=0`, rc 0 | **no base discrimination**: the behaviours pre-exist, only the assertions are new (F5) |
| 14 | `for p in c1-after7 c1-vacuity6 c2-after6 c3-after5 consumers-after6 a7-counter-fixes2; do git cat-file -e cb5737a:census/round-38/records/$p.txt; done` | `cb5737a=ABSENT` for all six; the same six `99efe06=present` | block §718's named receipts do not exist at the revision it names (F4) |
| 15 | `git log --diff-filter=A -1 -- census/round-38/records/<receipt>` | `be66886` adds `c1-after7`, `c1-vacuity6`, `c2-after6`, `c3-after5`, `consumers-after6`, `a7-counter-fixes2`; `8093c70` adds `c1-after8`, `c2-after7`, `c3-arms-filed`; `fcdecaa` adds `consumers-after3` | the blocks label the **measurement** revision; the blobs land one commit later (F4) |
| 16 | `sed -n '1,4p' census/round-38/records/c1-after7.txt` (and `c1-after8.txt`, `c3-arms-filed.txt`) | `# C1 after (final) at cb5737a63a704a7a52a1b97dada3fe5634fea32b` / `# C1 after (filed) at 99efe06…` / `# C3 + arms (filed) at 99efe06…` | receipts are internally consistent with their blocks; only the **blob** is absent at the named revision |
| 17 | `git ls-tree --name-only HEAD census/round-39/records/` | `c1-before.txt`, `c2-before.txt`, `c3-before.txt` only | no `c1-after.txt`/`c2-after.txt`/`c3-after.txt` is committed (F1, F2) |
| 18 | `git status --porcelain` | `?? census/round-39/make-cells.py`, `?? …/c2-after.txt`, `?? …/c3-after.txt`, `?? …/census-after.txt`, `?? …/census-before.txt` | the two existing after-receipts are **untracked worktree files** (F2) |
| 19 | `cat census/round-39/records/c2-after.txt` / `c3-after.txt` | first lines are `LEG L1 PASS …` / `MUTANT M11 killed=yes …`; **no `#` header naming a revision** | neither after-receipt names its measured revision (F2) |
| 20 | `ls census/round-39/cells.tsv` | `No such file or directory` | register absent → `register_cells=0`; C1's register arm unmeasured (F1) |
| 21 | `grep -n "r39" SKILL.md` | rows 273–277; row 273's evidence cell reads "after `c1-after.txt`" | registry row names a receipt that does not exist — R7 class reproduced (F1) |

## 2. Draft (b) — Round 39 measurements block

Insertion point: **append after the current EOF (line 739), preceded by one blank line**. Every
`<L1: …>` token must be replaced from the named receipt before landing; the block is not a claim
until then. Before-column values are the frozen controls; I re-measured only C1's (check 8).

````markdown
### Round 39 measurements (2026-10-28; base `ed30b7f5b77939c9073348d810730bc4f355708d`; preregistration frozen at `b769bfb84a264d8b284c09bc211d99f39a3e9126`; landing `<L1: 40-hex landing revision>`)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 routed-defect closure (16 items) + commit-distinct register | calibration 7 | `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0`, rc 1 — no anchored line exists at the base (`census/round-39/records/c1-before.txt`) | `<L1: SUMMARY line from census/round-39/records/c1-after.txt>` — target `items=16 open=0 register_cells>=6 register_mismatches=0 commit_distinct>=2`, rc 0; at `2201778` the same counter reads `open=2` (items R39-C1-03/04 `FILE-ABSENT`) with `register_cells=0` | `python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing40> --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --register-rev <landing40> --scratch <dir>` | before `ed30b7f5b77939c9073348d810730bc4f355708d` (`c1-before.txt`); after `<L1: landing40>` (`c1-after.txt`) |
| C2 citation/drift tool contracts (6 legs) | operability 8 | `SUMMARY legs=6 pass=2 fail=4 harm=0`, rc 1 — unresolvable `--rev` exits 1 with findings and the drift docstring's class map differs (`census/round-39/records/c2-before.txt`) | `<L1: SUMMARY line from census/round-39/records/c2-after.txt>` — target `legs=6 pass=6 fail=0 harm=0`, rc 0 | `python3 -B census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing40> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <dir>` | before `ed30b7f…` (`c2-before.txt`); after `<L1: landing40>` (`c2-after.txt`) |
| C3 record-rule mutation coverage (M11-M14) | coverage 8 | `SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10`, rc 1 (`census/round-39/records/c3-before.txt`) | `<L1: SUMMARY line from census/round-39/records/c3-after.txt>` — target `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`, rc 0 | `python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing40> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <dir>` | before `ed30b7f…` (`c3-before.txt`); after `<L1: landing40>` (`c3-after.txt`) |

`<L1: one paragraph — owned-score movement (or "unchanged: calibration 7, operability 8, coverage 8"), the harm statement, and the receipt list with each rc. Assert no-harm only from a green consumer arm; do not restate an after value that no committed receipt carries.>`
````

## 3. Draft (c) — Round 39 capability rows

Append after the measurements block, in the lane's four-column shape.

````markdown
### Round 39 capability rows (appended)

| name | what it can now do | evidence pointer | first-working round |
|---|---|---|---|
| routed-defect closure counter (r39) | re-derives the 16 routed r38 spot-check defects from committed bytes only (`git show`), scoring one line-unique anchored line per defect against required and forbidden whole tokens (alphanumeric boundaries, so `cases=21` is not `cases=210`); its register leg counts an eight-column register's rows and the rows whose `commit` differs from `receipt_rev`, re-runs the frozen `tools/souji-citation-reconcile.py` bytes at `--rev`, and applies `--min-cells`/`--min-commit-distinct` floors; refuses an unresolvable revision at exit 2 and prints `items_sha`. The item list is read from the working tree; every scored byte comes from git. | `python3 -B census/round-39/c1-counter.py --root <lane> --rev <full40> --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch <dir>` -> base control `SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0` rc 1 (`census/round-39/records/c1-before.txt`); after `<L1: c1-after.txt>` | r39 |
| tool-contract counter (r39) | six legs over two tool contracts, both revisions extracted from `git show` into private scratch: absent/blob/tree `--rev` must refuse `REFUSAL REV-UNRESOLVED` at exit 2 (base: exit 1 with findings), an unresolvable `--register-rev` stays exit 2 (the harm leg), the drift docstring's `RECORD-MISSING`/`RECORD-MALFORMED` mapping is read through `ast` plus comment-stripped code and matched to the class each trigger actually raises, the eight-case citation fixture must pass on the audited bytes and fail at least two cases on the base bytes, and five consumer fixtures must lose no passing case; prints `tool_sha`/`fixture_sha` | `python3 -B census/round-39/c2-counter.py --root <lane> --rev <full40> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <dir>` -> target `SUMMARY legs=6 pass=6 fail=0 harm=0`; base control `SUMMARY legs=6 pass=2 fail=4 harm=0` rc 1 (`census/round-39/records/c2-before.txt`); after `<L1: c2-after.txt>` | r39 |
| record-rule mutation counter (r39) | applies four single-defect mutants of `tools/souji-worktree-drift.py` — trailing-space tolerance added, `splitlines` replaced by `split("\n")`, outside-root guard removed, indented `#` accepted — to the audited bytes (an anchor that does not occur exactly once is a battery defect, not a kill) and scores each under the r38 A5 kill contract (the fixture's own `fail>0`, no traceback, exit 1), while the r38 fixture must leave every mutant alive (`base_killed=0`); a pristine control and a six-case floor void the run otherwise; prints `tool_sha`/`fixture_sha` | `python3 -B census/round-39/c3-counter.py --root <lane> --rev <full40> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <dir>` -> target `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`; base control `mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10` rc 1 (`census/round-39/records/c3-before.txt`); after `<L1: c3-after.txt>` | r39 |
| revision-resolution fixture (r39) | eight cases against a throwaway git repository: absent, blob and tree `--rev` must refuse `REFUSAL REV-UNRESOLVED` at exit 2; a 12-hex and a symbolic revision must refuse as usage; a clean run must read `mismatches=0` at exit 0; an unresolvable `--register-rev` must refuse `REV-UNRESOLVED`; a register absent at a resolvable revision must still report `not at`. Base bytes fail four of the eight | `python3 -B tests/fixtures/r39-citation-rev.py --work <dir>` -> `SUMMARY cases=8 pass=8 fail=0` rc 0 on the audited bytes; `--tool <git show ed30b7f:tools/souji-citation-reconcile.py>` -> `SUMMARY cases=8 pass=4 fail=4` rc 1, failing `rev-unknown`, `rev-blob`, `rev-tree`, `register-rev-gone` | r39 |
| record-rule fixture (r39) | seven record-file cases over an isolated scratch fleet: a good record, a trailing-space row refused, `TOTAL` before rows accepted, CRLF accepted, an outside-root row refused, an indented `#` refused, and comments plus `TOTAL` only -> `RECORD-EMPTY`. The assertions are new, the behaviours pre-exist, so the base tool also reads 7/7: base-bytes discrimination comes from the c3 mutant battery, not from this fixture | `python3 -B tests/fixtures/r39-drift-record-rules.py --work <dir>` -> `SUMMARY cases=7 pass=7 fail=0` rc 0 on the audited bytes; `--tool <git show ed30b7f:tools/souji-worktree-drift.py>` -> `SUMMARY cases=7 pass=7 fail=0` rc 0 | r39 |
````

Note for the L1: the register's own anchored lines (`R39-REG-01`, `-02`, `-03` naming
`SCORECARD.md`) are emitted by `census/round-39/make-cells.py --write` into
`census/round-39/cells-lines.md` and must be appended here too; their wording is that
generator's, not mine, and I did not duplicate it.

## 4. Optional errata line for the landed (a) line (offered, not landed)

`SCORECARD.md` is append-only, so the imprecise clause in `R39-C1-10` (F3) can only be corrected by
a later line. Proposed, single line, append-only:

````markdown
R39-C1-10a — the `R39-C1-10` clause "only the additive SCORECARD/lesson bytes differ" is imprecise: `git diff --name-status 99efe0676f439309a52f001b71bf0ba2ed8af47f fcdecaaf293f0fee3c39cc148ae91389e04ef63c` lists `M SCORECARD.md` and six added `census/round-38/records/` receipts (`c1-after4`, `c1-after8`, `c1-vacuity3`, `c2-after7`, `c3-arms-filed`, `consumers-after3`) and no lesson bytes; and the six receipts its "block that names `cb5737a`" cites first exist at `be66886`, so read those revision labels as measurement revisions, not blob revisions.
````

Effect on the frozen instrument: item `R39-C1-10` would then match two lines; the predicate
needs at least one qualifying line, so it stays CLOSED (verified by reading `c1-counter.py`'s
`hits`/`good` logic, not by re-running). If the L1 prefers line-uniqueness, land the errata under a
different id and say so in the report.

## 5. Findings

- **F1 (calibration, blocks C1's after cell).** At HEAD the frozen counter reads
  `items=16 open=2 register_cells=0`. Items `R39-C1-03`/`-04` are `OPEN FILE-ABSENT`
  (`census/round-39/records/waves-wait.txt`, `waves-capture.txt`) and the register
  `census/round-39/cells.tsv` does not exist, so `commit_distinct` is 0 and the C1 predicate cannot
  read `open=0 … register_cells>=6 … commit_distinct>=2`. `census/round-39/records/c1-after.txt`
  does not exist either, yet `SKILL.md:273` already names it as the after receipt — the same
  "a cell names an absent receipt path" class the round's R7 item closes.
- **F2 (calibration).** `c2-after.txt` and `c3-after.txt` exist only as untracked worktree files and
  carry no `# … at <rev>` header, so neither names the revision it measured — the exact limit the
  r38 lesson named and the reason the r39 table's after cells are placeholders. Both must be
  re-measured at the landing revision and committed with a header.
- **F3 (calibration, in the landed (a) line).** `99efe06..fcdecaa` is `M SCORECARD.md` + six added
  receipts; no lesson bytes differ. The line's "SCORECARD/lesson bytes" phrasing is falsified by
  check 7. §4 offers the appended correction.
- **F4 (hazard, not falsified).** Block §718 says "measured at `cb5737a`" and names six receipts;
  all six are absent at `cb5737a` and were added by `be66886`. The receipts' own headers say
  `at cb5737a`, so the label is a **measurement** revision, not a blob revision. `R39-C1-10`'s
  instruction to read that block is therefore correct but easy to misread as a blob pin; round 39's
  own register avoids the trap by pinning `receipt_rev` to revisions where the blob exists.
- **F5 (capability-row accuracy).** `r39-drift-record-rules.py` reads `cases=7 pass=7 fail=0` on the
  **base** drift tool too (check 13). Its row must not claim base-bytes discrimination; the round's
  coverage gain is the mutant battery's (`M11`–`M14` each killed only by this fixture). The SKILL
  row (`SKILL.md:277`) already says this; my drafted row keeps it.
- **F6 (positive).** `R39-C1-10` is CLOSED at `2201778` and still the single line at `d4c1755`;
  `fcdecaa` resolves and is an ancestor of the tip; the instrument-identity arm is an empty diff.
- **F7 (process).** The lane advanced once mid-seat (`2201778` → `d4c1755`), touching
  `census/round-39/c3-counter.py` and `tests/fixtures/r39-citation-rev.py`. My fixture readings
  (checks 10, 12) were taken before that commit; the diff is the TMPDIR fix for git children, so
  the readings stand, but the L1's after-measurement must be at one named revision.

## 6. Out of scope / not claimed

- I did not edit `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `SKILL.md`, any fixture, counter or
  receipt, and did not commit, push or run a mutating git/jj command.
- I did not re-run `c2-counter.py` or `c3-counter.py`: their after-receipts are untracked, the
  frozen before-receipts are the controls, and a re-run at a moving tip would decorate rather than
  measure. C2's and C3's before cells are quoted from the committed receipts (checks 18–19).
- No axis score is moved or claimed here; the lane still has no reproducible 0–10 mapping.
- The three counters' first-falsification arms, the register (`cells.tsv`) and the wave capture are
  other seats' items.

## 7. Scratch state

`/fast/scratch/hyaku/souji-r39/W1ScribeScorecard` is **still on disk** with
`base-citation.py` (13309 B, `git show ed30b7f…:tools/souji-citation-reconcile.py`) and
`base-drift.py` (19544 B, `git show ed30b7f…:tools/souji-worktree-drift.py`). Both fixtures clean
their own `mkdtemp` subdirectories under it. Nothing was written to `/tmp`, `~/.local/bin`, the
fleet root, a sibling lane, `.ufo/state/`, `templates/` or `scripts/`.
