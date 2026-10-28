# Round 36 — instrument-first round: coverage-map binding, report-contract gate, F1 drift surface

author: souji L1 (SoujiR36), fresh-start round (r30–r35 closures rejected; declared claims sized
so a do-nothing control cannot reach them, and every counter committed with its control receipt
before any after-data). Frozen contract: `census/round-36/preregistration.txt` (freeze commit
`42ea92e999cd8f1a01d2c28f5f7c9b884321ef78`, lane base
`94b5e96ab72b40622449af2dfe7c5b6d73118176`, amendments A1–A4 appended after named wave seats).

## Claims

- **C1 calibration (score 7, the lowest non-retired axis).** The coverage map must name every
  `ground: F<k>` knowledge entry at the landing revision, and every backticked entries-column path
  must resolve there. Counter:
  `python3 -B tools/souji-coverage-agreement.py --root <lane> --rev <landing> --base-rev
  94b5e96ab72b40622449af2dfe7c5b6d73118176` must read `dangling=0 mismatches=0` with
  `kill_tested>0 kill_violations=0`; the resolution clause is carried by the strict probe in
  `census/round-36/records/c1-strict-paths.txt`. Base control (`c1-control-base.txt`):
  `grounded=19 mapped=18 dangling=0 mismatches=1`, rc 1 (the r35 entry
  `corpus/knowledge/fleet-prune-numerator-r35.md` carried `ground: F1` and no map row named it).
- **C2 operability (score 8).** The pre-report gate enforces the round-report contract in seven
  predicates, proved by a fixture whose cases each isolate one predicate and whose controls are
  rejected. Target (after A1–A3):
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
  rc 0; `bash tests/fixtures/r27-pre-report-gate.sh` → `cases=4 pass=4
  control=FALSE-GREEN-REJECTED`, rc 0. Base control (`c2-control-base.txt`): no checker at base
  (`git cat-file -e` rc 128) and the base gate scores `cases=11 pass=0 fail=11`.
- **C3 coverage (score 8, capability acquisition).** F1's fleet worktree-registration numerator
  becomes a re-runnable surface: `tools/souji-worktree-drift.py` re-measures every repository a
  committed census record names, read-only, and reports the drift. Target (after A2+A4):
  `python3 -B tests/fixtures/r36-worktree-drift.py` → `cases=12 pass=12 fail=0
  control=STUB-REJECTED`; the live run against
  `census/round-35/records/prune-census.tsv` → `record_repos=26 record_regs=27 record_prunable=0
  live_repos=22 live_regs=23 live_prunable=1 drift_rows=5 unreachable=0` with the ABSENT set
  exactly `ok`, `research`, `scripts`, `templates`. Base control (`c3-control-base.txt`): the tool
  is absent at base (`git cat-file -e` rc 128).

## Gate

Sources opened this round, admitted by the lane's own bar (PROVINCE scope, QUALITY bar,
coverage-map ground). Each row names the URL, the access date and a ≤25-word located quote.

| id | source (URL) | access | located quote (≤25 words) | verdict |
|---|---|---|---|---|
| S233 | Bash Reference Manual — Bash Conditional Expressions — https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html | 2026-10-28 | “-s file True if file exists and has a size greater than zero.” (§ Bash Conditional Expressions) | **admit** — the r36 pre-report gate's non-empty-report predicate is this test; host GNU bash 5.3.20(1)-release; snapshot `census/round-36/sources/bash-conditional-expressions.html` (sha256 `401cf8ecf01b3aeb29423a6c5fb6f971083fbb733d4e4020261a6b022e9709fd`) |
| S234 | GNU Grep 3.12 manual — https://www.gnu.org/software/grep/manual/grep.html | 2026-10-28 | “Normally the exit status is 0 if a line is selected, 1 if no lines were selected, and 2 if an error occurred.” (§ 2.3 Exit Status) | **admit** — the gate's `grep -c` heading counts read this contract; lane scripts resolve `/usr/bin/grep` (`grep (GNU grep) 3.12-modified`); snapshot `census/round-36/sources/grep-manual.html` (sha256 `517177d02c39c446470c898273036a7616f705e4cbdcb6486b76a25700675f37`) |
| S235 | shell builtin `grep` (pi-uu-grep 0.2.0) resolved by `type -a grep` in an agent tool shell — no locator | 2026-10-28 | none located — the implementation reports itself via `grep --version` only | **reject** — undocumented implementation that no lane tool executes (`bash -c 'grep --version'` prints GNU grep 3.12-modified); flip: a located manual for pi-uu-grep plus a script-visible resolution to it |

Verdict flip (disclosed): the seat spec for S234 asked for a reject on the assumption that this
host runs a non-GNU `grep`. The L1 re-checked before landing the row: `bash -c 'type -a grep'` and
`bash -c 'grep --version'` inside a script resolve `/usr/bin/grep`, which prints
`grep (GNU grep) 3.12-modified` — the manual's own version line — so the row is **mined**, not
rejected. The undocumented implementation the spec saw is the agent tool-shell's builtin
(`pi-uu-grep 0.2.0`, first in `type -a` only in that shell): that is the rejected row, S235. Wave
seat SwarmScribe32's draft kept S234 as a reject per the spec; the L1's re-verification governs.

Registry append order: the scratch mirror (copy of `corpus/` with the append block) was validated
before the lane append; `sources-census.sh validate --file` reported an invalid `recheck=—` on the
reject row (E09, fixed to `365d`) and E11 for the not-yet-written lesson path, and no E03/E04
duplicate id or in-scope duplicate URL. Lane-root census before → after is recorded in the round
report.

## Gate correction (r35 routed defect 2)

The r35 lesson's Gate recorded S231/S232 as mined without URL, access date or located quote. Both
were re-opened this round; the located facts are:

- **S231** (own-work) — `census/round-35/records/prune-census.tsv`, accessed 2026-10-28, sha256
  `8b37041ac1a954263c6f4e665a8105d37ac342c802fb11f596aadb69ec257177`; quote (the record's own
  totals line): `TOTAL	repos=26	regs=27	prunable=0`. Its 26 REPO rows include four non-git
  paths (`ok`, `research`, `scripts`, `templates`) and its `prunable` column is 0 for every row
  because it counted `prune --dry-run` stdout — both defects are reproduced mechanically by
  `tools/souji-worktree-drift.py` (`census/round-36/records/c3-after.txt`).
- **S232** — https://git-scm.com/docs/git-worktree, re-fetched 2026-10-28 (HTTP 200, 98 918
  bytes, sha256 `cf843ea6e3edda3fdda65877063f6c9b8a8e91b54041bc39d0bc89246a6bc72d`, snapshot
  `census/round-36/sources/git-worktree.html`); located quote: “prunable, if the worktree can be
  pruned via git worktree prune.” (§ OPTIONS, the `git worktree list` annotation paragraph).

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `curation-record-incomplete` | `corpus/lessons/round-35.md` `## Gate` names S231/S232 as mined but carries no URL, access date or located quote; the r35 non-author spot-check routed it (`corpus/lessons/round-35-verifier-spotcheck.md`, routed defect 2) | none at r35 — the contract clause (CORPUS.md SOURCES v1, Gate block) was never executed as a check, and the census validator does not read lesson Gate blocks | this round's Gate table carries URL, access date and a ≤25-word located quote for all three rows, and `## Gate correction` re-opens the two r35 rows |
| `counting-wrong-stream` | `census/round-35/records/prune-census.tsv` records 26 "repositories" including the non-git paths `ok`, `research`, `scripts`, `templates`, and `prunable=0`; `git worktree prune --dry-run -v` writes its candidates to **stderr**, so counting stdout always reads zero (r35 spot-check, claim re-check C3) | the r35 non-author spot-check after the fact; no pre-freeze criterion exercised a repository with a real prunable candidate | C3's fixture case `prunable-changed` builds a registered worktree, removes its directory and requires `live=1` from the stderr stream; the live drift run names the four phantom paths as `ABSENT` |
| `claim-wider-than-counter` | the r36 prereg's C1 sentence promised "every backticked entries-column path resolves"; the counter tests basename membership only, and wave seat SwarmCritic07's W2/W3 reach the frozen success line with a map row naming an uncommitted path | none at freeze time — the claim sentence was never mapped clause-by-clause to the counter's code paths | the clause is now carried by the committed strict probe (`census/round-36/records/c1-strict-paths.txt`: `distinct=27 missing=0 nested_entries=0`) and the class becomes QUALITY Q80; the counter's limit is reported, not patched |
| `lane-file-truncated` | at integration `corpus/lessons/round-36.md` held only its two appended sections (1 996 bytes) while the first write was 6 487 bytes; the two appends survived, the head did not, and the committed `007ab53` carries the truncated file | none — the lane has no check that a file it wrote still has its earlier bytes; the candidate cause is the same class as wave seat SwarmExecutor35's symlinked-staging overwrite of `corpus/SOURCES.md` | the lesson is rebuilt in full in a later commit and the round report records the truncation; QUALITY Q81 (copy bytes, never links) is the preventive criterion. No other lane file was affected (byte counts re-checked) |

## Registry corrections (rule 2, used-by only)

Three rejected rows carried a `used-by` citing path, which contradicts `status=rejected` (a citing
path is the definition of mined). Reported by wave seat SwarmScout04 with row lines, history and the
exact corrected cells; wave seat SwarmReviewer03 read S097's round-20 audit as already dispositioned
— the two datasets agree, only the exemption claim differs, and the contract names no exemption.
Changed in place, old → new:

| row | old `used-by` | new `used-by` |
|---|---|---|
| S090 | `corpus/lessons/round-20.md` | `—` |
| S097 | `corpus/lessons/round-20.md` | `—` |
| S127 | `corpus/knowledge/git-repo-structure-common-dir.md` | `—` |

`status`, `tier`, `teaches` and the Gate rows are unchanged. Census after the correction:
`sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` exit 0.

## Findings

- The r35 filed report fails four of the seven contract predicates (`sections`, `trends`,
  `stale-lane`, `measurements`) — exactly the defect set the r35 spot-check recorded by hand
  (`census/round-36/records/c2-filed-reports.txt`); wave seat SwarmExecutor16 re-ran r20–r35 and
  found every recorded defect class flagged and none unflagged.
- The base-rev kill arm is what makes C1's success non-vacuous: de-grounding, deleting or moving
  the measured entry all reach `mismatches=0` on the bare counter and all three raise
  `kill_violations=1` with `--base-rev` (SwarmCritic07 V1/V3/V6; QUALITY Q82).
- The sections predicate was fence-blind before A3: a report whose six headings all sat inside one
  fence passed, and a conforming report that merely quoted a heading failed (SwarmReviewer09). A3
  masks fences and HTML comments and matches the canonical heading text at `##` depth.
- The gate's contract verdict was rc-only before A2: a checker that printed `=FAIL` but exited 0
  produced `check-report-contract=PASS` with rc 0 (SwarmCritic19 H3). A2 binds on both and
  forwards the checker's `SUMMARY`/`ERROR` lines.
- Five measured mutants of the checker (6-hex commit, single span, any token, 40-hex only, any
  slash-shaped token) each die on a named fixture case after A2/A3
  (`census/round-36/records/c2-after.txt`).
- The drift surface reproduces the r35 spot-check's corrected numerator (22 repositories, 23
  registrations, 1 prunable) and localizes both counting defects of the r35 record; wave seat
  SwarmExecutor25 re-derived the same figures by hand.
- The drift tool's failure classification holds: a gitfile pointing nowhere and a corrupted repo both
  read `UNREACHABLE:list-rc=128` with rc 1 (no crash, no hang), and a repository config whose
  `core.fsmonitor` sleeps is bounded by `--timeout` (SwarmExecutor23: the specified hang vector did
  not reproduce).
- The round's landing set is secret-free: the seven-file and HTML sweeps found no credential, token,
  cookie, key, private URL or SSH path (SwarmSentinel38; two apparent hits were recorded as false
  positives).
- The F1 frontier edit is accurate against the tree — the r35 record is still filed unfixed, which
  the frontier bullet says explicitly (SwarmScout05).
- Wave seats disagreed once, on whether S097's round-20 audit exempts its `used-by` contradiction
  (SwarmReviewer03: exempt; SwarmScout04: violation). The contract names no exemption, so the L1
  applied the correction and recorded both readings in `## Registry corrections`.
- Limits disclosed by the wave: the drift tool is blind to bare repositories in both directions
  (SwarmExecutor22 F2), `live_regs` tracks fleet churn while lanes run (SwarmCritic28: 24 → 23 in
  two minutes), and `drift_rows>=5` has one row of margin over the four phantom paths.

## Receipts

- Frozen contract and controls: `census/round-36/preregistration.txt`,
  `census/round-36/records/` (`c1-control-base.txt`, `c2-control-base.txt`,
  `c3-control-base.txt`, `c2-filed-reports.txt`, `c3-live-run.txt`, `c1-after.txt`,
  `c1-strict-paths.txt`, `c2-after.txt`, `c3-after.txt`).
- Instruments: `tools/souji-report-contract.py`, `tools/souji-worktree-drift.py`,
  `tools/souji-pre-report-gate.sh` (`--contract`).
- Fixtures: `tests/fixtures/r36-report-gate.py`, `tests/fixtures/r36-worktree-drift.py`.
- Source snapshots: `census/round-36/sources/bash-conditional-expressions.html`,
  `census/round-36/sources/grep-manual.html`, `census/round-36/sources/git-worktree.html`.
- Wave evidence: `.ufo/waves/round-36/` (specs, dispatch payloads, per-seat reports).

## Residuals

- The r35 census record is left as filed: its two counting defects are reported and exposed by
  the drift tool, never rewritten (the record is evidence, not a document to repair).
- C1's counter still says nothing about whether a mapped entry's *content* is true; it binds the
  map to `ground:` declarations only, and its resolution check is basename-only unless the strict
  probe is run beside it.
- C2's `--contract` predicate is opt-in by argv; a caller that omits the flag prints
  `check-report-contract=SKIPPED (no --contract)` and the run is not covered.
- C3's live numerator moves with the fleet while lanes run; the frozen target binds the phantom
  ABSENT set, not the live counts, and `drift_rows>=5` has one row of margin over them.
- Bare repositories are invisible to the drift tool in both directions (reported, not fixed).
- The lesson truncation's cause is not identified; the file is rebuilt and its bytes are asserted
  before the landing commit.

## Correction (r37, 2026-10-28)

R37-C1-7 — the Claims section above quoted a count for the C2 fixture that no receipt ever carried. Settlement: `census/round-36/records/c2-after.txt` at `1e771ed` carries `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` (amendment A7 refreshed it), and the base control line stays `cases=11 pass=0 fail=11`.
The Claims line is corrected in place (the prereg's in-place branch for current lesson cells); this block records the settlement and names the receipt. The other never-true citations (SCORECARD rows, SKILL registry, the frozen predicate sentence) are reconciled in `SCORECARD.md` `### Round 37 receipt reconciliation` and in the prereg's `R37-C1-8`/`R37-C1-9` block.

### R39 append-only correction (round 39, 2026-10-28)

R39-C1-16 — correction owed since r37 routed defect 4: line-23 of this lesson was rewritten in-place by a later integration instead of being corrected by an appended block, which is the defect r37 routed and r38 left open. The superseded sentence stays in history; this appended correction records it, and from this round an in-place edit of a lesson is a routed defect rather than a documentation choice.
