# ScribeLesson — round-25 lesson skeleton (souji r25 w1)

Seat: `L1Souji25.ScribeLesson-2` (scribe, leaf). Lane HEAD `6e4737eab43d8fde1b85eb9f57023d29046705b4`
(base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`). Draft written:
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-25/w1/lesson-skeleton.md`. No other lane
file edited; no git/jj mutation; no installs or updates.

## Status
STATUS: PARTIAL — the skeleton has every requested section (summary, Gate, Mistakes R25-M1, Seat-reported
failures stub, Trend drafts). Two items are left to the L1 by design: the S125 choice (two seat drafts
conflict) and committing the R25-M1 red arm (the receipts are draft-only, in the wave dir).

## Evidence
- Prereg read first: `.ufo/waves/round-25/preregistration.txt` (C1/C2/C3, § Assimilation "none this
  round", routed R15/R17 "14/15 -> 15/15 red-before witness").
- Base receipts at `6e4737e`: `census/round-25/records/c1-control-base.tsv` rc=2 "unrecognized
  arguments: --base-rev"; `c2-control-base.tsv` `cases=8 pass=8 control=FALSE-GREEN-REJECTED
  lost_found=WRITE-DETECTED`; `c3-control-base.tsv` `selftest=PASS ids=5/5`;
  `coverage-agreement-at-base.tsv` `grounded=6 mapped=6 dangling=0 mismatches=0`;
  `record-agreement-at-base.tsv` `keys=4 records=4 occurrences=17 mismatches=0`.
- Tool blobs: `sha256sum tools/souji-record-agreement.py` → `41db9ca8…036d` (last commit `315422b`);
  `git show c872eec:tools/souji-record-agreement.py | sha256sum` → `dd53c228…bb0f` (r23 blob).
- Docstring vs code at tip: `tools/souji-record-agreement.py:12` "A tuple on an r22 line that names some
  other revision is outside K1" vs `:199-203` `rev-disagree` / `:204-208` `unbound-tuple`; `counts_of`
  docstring `:119-122` agrees with `:124-133` since `315422b`.
- Quote re-match (this seat, host `git 2.56.0-1`), `MANWIDTH=400 man -P cat <page> | col -bx | tr -s ' '`:
  gitrepository-layout L136 "If this file exists, $GIT_COMMON_DIR (see git(1)) will be set to the path
  specified in this file if it is not explicitly set." and L28 (§ objects) matched; gitglossary L397
  "One "worktree" consists of …" matched; git(1) L868 "If this variable is set to a path, non-worktree
  files that are normally in $GIT_DIR will be taken from this path instead." matched.
- S123 snapshot `census/round-24/sources/git-worktree.1.txt` (sha256 `624821a6…b51a`) L170: "Within a
  linked worktree, $GIT_DIR is set to point to this private directory … and $GIT_COMMON_DIR is set to
  point back to the main worktree’s $GIT_DIR".
- ExecR17 draft receipts (read, not re-run): `ExecR17/red-arm-prefix-3a90ddc.tsv` tool_sha256
  `dd53c228…` → `selftest=14/15` (case 15 FAIL); `ExecR17/base-arm-716731f.tsv` tool_sha256 `41db9ca8…`
  → 15/15; `ExecR17/green-arm-draft.tsv` tool_sha256 `04811c24…` → 15/15; fixture sha256 `40ddcbeb…ac57`.
- Slice table: `census/round-24/records/slice-verdicts.tsv` sha256 `dca22c1a…5311`; `git diff --stat
  a6d2d15 6e4737e` lists only round-25 prereg/receipt files.

## Findings
1. **S125 conflict (verbatim, for the L1).** `ScoutSourcesOpen.md` F3: "Replacement S125 (recommended):
   git(1) § ENVIRONMENT VARIABLES `GIT_COMMON_DIR`". `sources-rows.md` (ScribeSources) S125 row:
   "gitglossary(7) § worktree — https://git-scm.com/docs/gitglossary". The C3 entry draft
   `git-repo-structure-common-dir.md:2` already follows the glossary. Both are in the skeleton's Gate as
   options (a)/(b); the briefed glossary `common directory` anchor is rejected (0 matches,
   `ScoutSourcesOpen` F2).
2. **The scout's overlap claim is inexact.** `ScoutSourcesOpen` F3 Alt A says S123 cites "the adjacent
   "private $GIT_DIR" sentence". In the snapshot, L170 is one sentence that carries both clauses, so S123's
   anchor already covers the `$GIT_COMMON_DIR … point back` clause. The linked-worktree half that S124
   lacks (`ScoutSourcesOpen` A2) can cite S123, and S123's `used-by` then gains the entry, logged old→new.
3. **R25-M1 residual drift.** The ExecR17 draft tool (`.ufo/waves/round-25/w1/souji-record-agreement.py:13`)
   keeps "names some other revision is outside K1". Code `:199-203` still flags `rev-disagree` for a
   same-value tuple bound to another revision, so the module docstring stays partly inexact after the fix.
   Route this to RevR17/ExecR17.
4. **Bare-id hazard.** S124 is also a campaign id row of the r24 slice table and of round-22 records
   (`ScoutGateCensus` F5, `ScoutSourcesOpen` F4). The skeleton tells writers to use "SOURCES S124/S125".
5. **Stale slice tallies.** `round-24.md:240`, `SCORECARD.md:181` and `LOG.md:1692` still read "7 accepted,
   1 unverifiable" (`ScoutD6Slice`). They are carried into the quarantine-slice note as append-only
   supersede targets.
6. **The red arm is not committed.** The 14/15 witness exists only in wave-dir draft receipts. The prereg
   pattern needs it committed before any after-data.

## Out of scope / limits
- Seat-reported failures: a stub only, to be filled post-wave (per brief).
- I did not re-run any counter or fixture. Every count above is read from committed receipts or from seat
  draft receipts.
- Scratch: this seat created none. `/var/tmp/souji-r25-ScribeLesson/` exists, but it was not created by
  this seat (probably the sibling `L1Souji25.ScribeLesson`), so it was left untouched.
