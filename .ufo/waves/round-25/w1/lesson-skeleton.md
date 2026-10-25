# Round 25 — kill-rule tool row, size-census refusal coverage, structure probe under the common-dir envelope

DRAFT SKELETON (seat `L1Souji25.ScribeLesson-2`, wave 1). The L1 assembles the final lesson; nothing
here is claim data. Line numbers are at lane commit `6e4737eab43d8fde1b85eb9f57023d29046705b4` unless
stated.

Author: SoujiR25 (lane identity `souji-shokunin <souji@shokunin.local>`). Lane base
`a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`. Preregistration `.ufo/waves/round-25/preregistration.txt`
(frozen at `6e4737eab43d8fde1b85eb9f57023d29046705b4`). Inbound: `corpus/lessons/round-24-verifier-spotcheck.md`
(routed D1–D6) and SCORECARD `r25 (planned r24)` (`SCORECARD.md:225`). After-state: _L1 fills_.

## Claim and boundary (summary)

Three claims on three axes. Each has a do-nothing control receipt committed before any after-data
(`census/round-25/records/c{1,2,3}-control-base.tsv`, landed in `6e4737e`).

| claim | axis | counter (frozen) | before (committed) | after target |
|---|---|---|---|---|
| C1 kill-rule tool row | calibration (7) | `python3 -B tests/fixtures/r25-coverage-agreement.py --tool <path>`; real run `tools/souji-coverage-agreement.py --rev <tip> --base-rev a6d2d15…` | tool rejects `--base-rev`: `rc=2`, "unrecognized arguments: --base-rev" (`c1-control-base.tsv`) | `kill_tested=4 kill_violations=0 mismatches=0` rc 0; fixture `cases=C pass=C control=FALSE-GREEN-REJECTED` |
| C2 size-census refusal surfaces | operability (8) | `python3 -B tests/fixtures/r24-size-census.py --tool <path>` (cases 9–12 added) | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` (`c2-control-base.tsv`) | `cases=12 pass=12 …`, rc 0; red arm = old blob `1efe406e…:tools/souji-size-census.py` fails ≥1 of 9–12 |
| C3 structure probe, common-dir envelope + colocated/plain precondition | coverage (8) | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | `selftest=PASS ids=5/5` (`c3-control-base.tsv`) | `ids=7/7`, rc 0; knowledge entry `corpus/knowledge/git-repo-structure-common-dir.md` (ground F2) citing SOURCES S124/S125 |

Also at base (committed in `6e4737e`): `coverage-agreement-at-base.tsv` `grounded=6 mapped=6 dangling=0
mismatches=0`; `record-agreement-at-base.tsv` `keys=4 records=4 occurrences=17 mismatches=0`.

Kill rules (prereg, verbatim intent): any KILL-RULE violation or `mismatches>0` at tip → C1 not
verified; any case failing at tip → C2/C3 not verified; no case dropped or re-specified after scoring.

## Gate

### Opened sources (2026-10-25)

Registry before: 123 rows S001–S123, contiguous, `validate` rc 0 with 31 W04 and 0 E lines; next free
id S124 (`ScoutGateCensus` F1–F3). After append: 125 rows if both rows land.

**Id hazard (write it into every record):** a bare "S124" also names the campaign/staged-register id
S124 — it is a row of the r24 quarantine-slice table (`census/round-24/records/slice-verdicts.tsv`
"S124 accepted") and of `.ufo/waves/round-22/attempt2/assimilation/staged-ids`; `corpus/lessons/round-22.md:363`
uses it too (`ScoutGateCensus` F5). Write "SOURCES S124"/"SOURCES S125" or the row anchor in the
entry, SCORECARD and README.

Every fetch below returned HTTP 200 with no redirect on 2026-10-25 (`ScoutSourcesOpen` Evidence, fetched
12:28:04Z–12:28:45Z; `ScribeSources` re-fetch byte-identical, `cmp` rc 0). Each quote below was also
re-matched by this seat against the installed `git 2.56.0-1` man pages (`man -P cat <page> | col -bx`).
Snapshots are to be committed under `census/round-25/sources/` with a `SHA256SUMS` line (S120–S123
precedent; `ScoutSourcesOpen` row-candidates note).

- **SOURCES S124 mined** — https://git-scm.com/docs/gitrepository-layout § commondir (anchor
  `#Documentation/gitrepository-layout.txt-commondir`), accessed 2026-10-25. Web html sha256
  `ad7b52fb…c64c`. The web page footer reads "last updated in 2.49.0", so the 2.56.0 claim rests on the
  v2.56.0 `Documentation/gitrepository-layout.adoc` L268-273 and the installed man page (`ScoutSourcesOpen`
  F1, A3). Quote (23 words): "If this file exists, $GIT_COMMON_DIR (see git(1)) will be set to the path
  specified in this file if it is not explicitly set." The web text has `git[1]`; the man page has
  `git(1)`. Second quote (12 words): "The repository with commondir is incomplete without the repository
  pointed by "commondir"." Redirection quote (§ objects, 14 words): "This directory is ignored if
  $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/objects" will be used instead."
  scope limit: the layout page grounds the `commondir` pointer and shared-name redirection; linked
  worktree private `$GIT_DIR` and `$GIT_COMMON_DIR` resolution is grounded in SOURCES S123 § DETAILS
  (`census/round-24/sources/git-worktree.1.txt:170`), which is one sentence containing both clauses.
  If the C3 entry cites S123, `used-by` must include that path and the change must be logged.
- **SOURCES S125 — replacement admitted, not in conflict.** The briefed target (a gitglossary `common
  directory` entry) does not exist at 2.56.0: zero case-insensitive matches for `common` across web,
  installed man and v2.56.0 adoc (`ScoutSourcesOpen` F2), so that proposed anchor is rejected.
  Admit S125 as git(1) § ENVIRONMENT VARIABLES `GIT_COMMON_DIR` (ScoutSourcesOpen F3; the C3 draft's
  existing glossary row is replaced). URL https://git-scm.com/docs/git, anchor
  `#Documentation/git.txt-GITCOMMONDIR`, accessed 2026-10-25; the page is marked last updated in
  2.56.0; html sha256 `a43b6eff…2f0e`, upstream `Documentation/git.adoc` L580-586 and installed
  git(1) 2.56.0-1 L868. Quote (22 words): "If this variable is set to a path, non-worktree files that
  are normally in $GIT_DIR will be taken from this path instead." Continuation: "Worktree-specific
  files such as HEAD or index are taken from $GIT_DIR." It grounds shared vs per-worktree files,
  not how a linked worktree sets the common directory. URL is also used by S036 and S049 under
  distinct scopes (31 W04 baseline; +1 expected).

Registry proposed outcome: 123 → 125 rows. Search log and Paths draft: `sources-rows.md` must be
updated to include this selected S125; avoid carrying its glossary row verbatim.

### Admission / rejection decisions

- **Assimilation: none this round** (prereg § Assimilation: "The round is load-maxed on routed-defect
  remediation; the staged package merge/souji stays untouched"). No staged entry is admitted or
  rejected; the discernment sample from staged assimilation is therefore empty.
- **Source admissions:** ADMIT SOURCES S124 for commondir and shared-name redirection; ADMIT SOURCES
  S125 for shared vs per-worktree file location. REJECT the briefed S125 glossary `common directory`
  anchor because no such entry exists in the opened source. Every rejection reason must be true of the
  repo (R24-M9/M17 class).
- **Rejected scope:** no fleet figure; no `git repo structure` size baseline before the colocated/plain
  precondition holds; no claim that C2's no-write envelope covers atime/ctime, mtime-restoring writes
  or hostile config/env (prereg C2 disclosed limit); no claim that C1 mechanizes status-cell mentions
  (R24-M2 stays a marking fix, D4).


### Quarantine-slice note

The r24 quarantine-slice verdicts stand unchanged (prereg § Assimilation). `census/round-24/records/slice-verdicts.tsv`
(sha256 `dca22c1a…5311`, last touched `315422b`, unchanged `a6d2d15`→`6e4737e`: `git diff --stat` lists
only round-25 files) reads 8 × `accepted`; its own header maps the detail table's
`present`/`present-via-mirror`/`present-quote-needs-fix` to `accepted` and states the ids are campaign
register ids, not lane registry ids. D6 (R24-M22) asks for that mapping in the lesson: both tables, the
class map, S118 re-classed `accepted` everywhere. `ScoutD6Slice` (STATUS PASS) finds the two tables
agree 8/8 under the gate-table header map. S118 is `accepted` only through that map: the detail row
still reads `present-via-mirror` and carries no S118 note. Stale "7 accepted, 1 unverifiable" tallies
remain at `corpus/lessons/round-24.md:240`, `SCORECARD.md:181` and `LOG.md:1692` (`ScoutD6Slice` :17-19,
:34-36). They need append-only `superseded by 8 accepted (R24-M22)` notes; the proposed mapping text is at
`ScoutD6Slice` F5 :84-93. Key the rows as (souji, Sxxx) campaign ids (`ScoutD6Slice` F4).
Slice verdicts are not lane admits/rejects and stay out of the discernment sample (r24 `W2Trend` F13).

## Mistakes

Witness legend as r24: **SHOWN** = executed and failing on the defect, runner named; **NONE** = no
executable witness.

| id | class | evidence | captured-by | fix | failure witness |
|---|---|---|---|---|---|
| R25-M1 | reference-drift — the r23 record-agreement documentation overclaimed the K1 parsing boundary; at the r25 tip the `counts_of` documentation matches the r24 code, but the K1 same-revision exclusion statement remains inexact | At `c872eec`, `tools/souji-record-agreement.py` says header-only at :118-119 while code reads `COUNTS_RE.findall(text)` / `matches[-1]` across the entire text; r24 fixed the implementation and docstring at `315422b` (R24-M12; `corpus/lessons/round-24.md:336-339`). At r25 base/tip `tools/souji-record-agreement.py:12` says a tuple naming another revision is outside K1, while :199-203 emits `rev-disagree` for a same-value tuple bound elsewhere. Thus the broad old mismatch is closed; one narrower reference drift remains. | none — Q55 checks receipt bytes/integrity, not docstring/code agreement (`corpus/QUALITY.md:129`) | r24 code/docstring correction, plus r25 documentation correction narrowly to K1's excluded tuple condition (no K1 predicate change) and three fixture additions: `token-moved`, `decoy-line`, `trailing-shadow` (ExecR17; `ScoutR17RecordAgreement` notes the r25 case set must preserve the 14/15→15/15 witness without treating R15 as fixed) | **SHOWN (draft evidence; old tool is pre-r24, not a6d2d15)**: `c872eec:tools/souji-record-agreement.py` sha256 `dd53c228…` scores 14/15, case 15 trailing-shadow fails (`ExecR17/red-arm-prefix-3a90ddc.tsv`); fixed a6d2d15 tool `41db9ca8…` and docstring draft `04811c24…` score 15/15 (`ExecR17/base-arm-716731f.tsv`, `green-arm-draft.tsv`). Committed 12-case fixture stays 12/12 at both. The old red-arm receipt still needs committing before after-data. |
## Seat-reported failures

_To be filled post-wave_: every wave-1 (and wave-2, if run) report whose `STATUS:` is PARTIAL or
FAIL, verbatim head + disposition (accepted / repaired / disputed), with the count of seats, PASS,
PARTIAL, FAIL and reports without a `STATUS:` line.

## Trend verdicts (draft; non-author closure rules)
- **expansion — provisional `unprovable-but-better`.** One new entry on held F2 ground (C3); expected evidence is the committed C3 after receipt, the C1 after receipt (grounded count +1, `kill_tested` unchanged at 4), and the README F2 entries-cell diff. Assimilation is none, so no staged capability enters.
- **quality — provisional `improved (bounded)`, subject to falsifiers.** C3 targets the common-dir no-write envelope and colocated/plain precondition (5/5 → 7/7); the R25-M1 fixture is an extension rather than a code behavior change because R17 code was fixed at r24. Pointers: C3 after receipt, ExecR17 draft fixture results, README `:40` superseded marker. Harm triggers: any false entry statement (R24-M20 precedent) or a narrowed prior entry left unmarked (R24-M21).
- **discernment — not self-graded; pending non-author spot-check.** Eligible sample is SOURCES S124/S125 admission/rejection only; assimilation is none and quarantine-slice verdicts are excluded. Q57 (D6/R24-M22) must land with the lesson, or the criterion-without-lesson harm trigger applies (r24 `W2Trend` F14).
