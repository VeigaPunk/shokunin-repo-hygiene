# Round 38 — commit-arm citations, the drift write envelope, record-validation discrimination

author: souji L1 (SoujiR38), hyaku run 11, attempt 1. Lane base
`ca4369a9296011644636711a624da6a8074e8e2a`; frozen contract `census/round-38/preregistration.txt`
(freeze commit `4090ee5b04ca3205d61c044b89fd9f318cf9850c`). Fresh-start round: the r37 non-author
spot-check (admitted, eight routed defects) and the r37 lesson's named limits were read first.

## Claims

- **C1 calibration (score 7, the lowest non-retired axis).** r37 reconciled ten self-assessment
  cells but named the missing arm: "the schema binds an expected token to both a citation line and
  a receipt blob, and a commit id is in neither", so a measured-commit cell naming a revision where
  the receipt does not exist (or reads another value) stayed unverifiable — routed defects 2 and 7.
  The reconciler gains an optional eighth register cell: the commit must resolve, be an ancestor of
  the audited revision, be named on the anchored line, and the receipt blob **at that commit** must
  carry the expected token. Ten routed cells are reconciled append-only (SCORECARD, LOG, QUALITY).
  Counter: `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev <landing> --register
  census/round-38/cells.tsv --register-rev <freeze>` → `SUMMARY cells=10 mismatches=0`, rc 0.
  Base control (`census/round-38/records/c1-before.txt`): `cells=10 mismatches=10`, rc 1.
  Fixture: `tests/fixtures/r38-citation-commit.py` `cases=14 pass=14 fail=0
  control=FALSE-GREEN-REJECTED`; the r37 fixture stays `cases=16 pass=16`.
- **C2 operability (score 8).** The r37 named limits name three defects in the drift tool's output
  envelope, each reproduced on the r37 blob before any repair: a `--json` FIFO blocked a blocking
  `O_WRONLY` open forever; `--record X --json X` replaced the record with JSON and exited 0; and
  the module docstring's exit-2 enumeration omitted four refusal classes the code raises (routed
  defect 6). The open is now `O_NONBLOCK` with a post-open `S_ISREG` refusal, the output must not
  alias the input by path or inode, and the docstring names every class. Counter:
  `python3 -B tests/fixtures/r38-drift-write-envelope.py --base-tool <r37 blob>` →
  `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6`, rc 0; the base receipt itemises the
  six failing cases.
- **C3 coverage (score 8).** The tool's record-validation arm — three TOTAL/REPO cross-checks and
  the duplicate-name refusal — was never exercised by the r37 discrimination fixture (its
  `record()` helper always writes a consistent TOTAL and never repeats a name), so a mutant dropping
  any one check survived 12/12. `tests/fixtures/r38-drift-record.py` (10 cases) and the four-mutant
  battery `tests/fixtures/r38-drift-mutants.py` (with the pristine control the r37 battery lacked)
  put that surface under a frozen battery. Counter:
  `python3 -B tests/fixtures/r38-drift-mutants.py --fixture tests/fixtures/r38-drift-record.py
  --base-fixture tests/fixtures/r37-drift-discrimination.py` →
  `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0`, rc 0; base control
  (`census/round-38/records/c3-before.txt`) `killed=0 survived=4 pristine=ok`.

## Gate

New sources opened this round, all read from the installed man pages on this host
(`man 2.13.1`, `git 2.56.0-1`, Linux man-pages 6.19) with the canonical URL recorded; `## Gate`
cites line numbers from `MANWIDTH=100 man <page>`.

| id | source (URL) | access | located quote (<=25 words) | verdict |
|---|---|---|---|---|
| S239 | git-merge-base(1) § OPTIONS `--is-ancestor` — https://git-scm.com/docs/git-merge-base#Documentation/git-merge-base.txt---is-ancestor | 2026-10-28 | "exit with status 0 if true, or with status 1 if not" (§ OPTIONS, lines 41-43) | **admit** — the commit arm must read status 1 as not-an-ancestor and any other non-zero as an error, which is why it resolves the object first |
| S240 | git-cat-file(1) § OPTIONS `-e` — https://git-scm.com/docs/git-cat-file#Documentation/git-cat-file.txt--e | 2026-10-28 | "Exit with zero status if <object> exists and is a valid object." (§ OPTIONS, lines 39-41) | **admit** — an unresolvable commit cell is a distinct class from a non-ancestor, and the fixture keeps the two cases apart |
| S241 | fifo(7) § DESCRIPTION — https://man7.org/linux/man-pages/man7/fifo.7.html | 2026-10-28 | "Normally, opening the FIFO blocks until the other end is opened also." (§ DESCRIPTION, line 16) | **admit** — the exact blocking behaviour the r37 blob reproduced as a hang, and the nonblocking alternative the repair takes |
| S242 | open(2) § ERRORS `ENXIO` — https://man7.org/linux/man-pages/man2/open.2.html | 2026-10-28 | "O_NONBLOCK | O_WRONLY is set, the named file is a FIFO, and no process has the FIFO open for reading." (§ ERRORS, lines 544-546) | **admit** — the errno branch the tool now classifies as JSON-NOT-REGULAR instead of blocking |
| S243 | pipe(7) § DESCRIPTION — https://man7.org/linux/man-pages/man7/pipe.7.html | 2026-10-28 | "Nonblocking I/O is possible by using the fcntl(2) F_SETFL operation" (§ DESCRIPTION, lines 27-33) | **reject** — that is read/write readiness on an open pipe, not the open-time block or ENXIO the refusal needs; flip: the page states the open-time contract |

Row changes: S239-S242 new tier-A `mined` rows, S243 new and `rejected`; no existing row's
`status`, `recheck` or `used-by` cell changed. `used-by` for S239-S242 is this lesson (C1 rests on
S239/S240, C2 on S241/S242). Registry grep count 162 → 167; the census command and both exit codes
are in the round report.

## Mistakes

### M1 — a fixture assertion that cannot occur on one line (vacuous)

**Class:** vacuous. The first `tests/fixtures/r38-drift-record.py` success cases asserted the token
`SUMMARY record_repos=2`; the tool prints `SUMMARY record=<path> record_repos=2 ...`, so the token
never occurs and three PASS-expected cases failed for a reason unrelated to the tool.
**Evidence pointer:** the first local run (`SUMMARY cases=10 pass=7 fail=3`, all three failures
naming `missing=['SUMMARY record_repos=2']`).
**Captured-by:** none at the time — the fixture had no independent oracle for its own expectations.
**Fix:** assert the single tokens `SUMMARY` and `record_repos=2` separately; the repaired run reads
`cases=10 pass=10 fail=0`.

### M2 — a fixture that silently graded an empty cell (survivor)

**Class:** survivor. The commit-arm fixture built the "not an ancestor" case with
`git rev-parse "c0^{tree}"` where `c0` was already a hash, so the revision was invalid, the dangling
commit cell came back empty, and the tool skipped the arm for a row that then passed.
**Evidence pointer:** `case-commit-not-ancestor=FAIL rc=0 want_rc=1 missing=['COMMIT-NOT-ANCESTOR']`
with `SUMMARY cells=1 mismatches=0`.
**Captured-by:** the case's own expected class — the run exposed it before any after-data.
**Fix:** `c0 + "^{tree}"`; the case now reads `COMMIT-NOT-ANCESTOR` and the fixture is 14/14.

### M3 — an expectation that disagreed with the documented class (stale-premise)

**Class:** stale-premise. `json-directory` expected `JSON-NOT-REGULAR` while the code classified an
`EISDIR` open failure as `JSON-UNWRITABLE`; the docstring and the case disagreed about the same
input.
**Evidence pointer:** `case-json-directory=FAIL rc=2 ... REFUSAL JSON-UNWRITABLE: [Errno 21]`.
**Captured-by:** the fixture case (it compared the class, not only the exit code).
**Fix:** classify `ENXIO` and `EISDIR` as `JSON-NOT-REGULAR` (tighter, and what the docstring says);
`ELOOP`/`EACCES` stay `JSON-UNWRITABLE`.

## Frontier

SOURCES census before → after: 162 rows, rc 0 → 167 rows, rc 0 (records under
`census/round-38/records/`). Rows added by tier: A ×5 (S239-S242 admitted, S243 rejected); touched
old→new: none. No `ground: F<k>` line moved: the four admitted rows ground the C1/C2 repairs, not
new frontier ground, so no F row advances. Mined mistake: M1. Assimilation: see the round report.

## Named limits (disclosed, status-neutral)

- The C1 commit arm binds a token to a commit where the receipt exists; it does not prove the
  *measurement* was run there, and it reads only the first docstring segment of the counter.
- The ten reconciled cells are the ones the r37 spot-check routed and the lane owns; the r37
  report's own cells are fleet-repo bytes outside this round's write scope and are carried as an
  errata section in the round-38 report, not claimed.
- The C2 fixture bounds a FIFO open at 15 s; a base tool that terminates slowly rather than blocking
  would be reported as a hang. The `json-directory` class is `JSON-NOT-REGULAR` by decision, not by
  errno documentation.
- The C3 battery scores four mutants of one function; the fixture's other record rules (comment and
  blank-line skipping, optional TOTAL) are asserted but not mutation-scored.
