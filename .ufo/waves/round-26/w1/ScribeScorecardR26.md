# ScribeScorecardR26 — round-26 measurements draft, capability row, planned edits, verdicts

## Status

STATUS: PARTIAL — the draft (`.ufo/waves/round-26/w1/scorecard-r26.md`) is complete in all four
requested parts with `RECEIPT-PENDING` where the L1 must fill, but the round cannot report PASS:
C2's frozen K2 gate is red at the tip (`entries=2 ok=0 fail=2`) and C3's committed fixture is the
11-case bytes against a frozen 12-case contract. C1 is green on its counter.

## Evidence

Lane read-only. Tip moved four times while this seat ran; every cell names its own revision.
`git rev-parse HEAD` at first read `d2e6253`, at final read `ba8b54b`.

| # | command | output excerpt | revision |
|---|---|---|---|
| E1 | `git rev-parse HEAD` | `ba8b54b85814dd980aa96050fe111c7cbfd4956a` | ba8b54b |
| E2 | `bash census/round-26/c1-counter.sh` (`markers`, headings) | `markers=0`, `headings=17 44 78` (Round 25 before Round 24 before Round 23) | worktree at ba8b54b, SCORECARD unmodified since 07f83e6 |
| E3 | `cat census/round-26/records/c1-after.tsv` | `rev=07f83e69979b1032f9de4fe876739a8dccc7242b`, tool sha256 `c8dbb76c…`, `markers=0`, `headings=17 44 78 ` | receipt |
| E4 | `cat census/round-26/records/c1-before.tsv`, `c2-before.tsv` | both `rev=12fd90bcd9cdfab495e178023eeaa838a977fcbe`; `markers=2` / `headings=17 175 231`; `grounded_f1=0` / `registry_rows=127` | receipts |
| E5 | `cat census/round-26/records/c2-k4-base.tsv` | `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0 | rev `0eca7c8` |
| E6 | `cat census/round-26/records/c2-after.tsv` | `rev=e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3`; `grounded_f1=2`, `registry_rows=132` | receipt |
| E7 | `python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts` | `FAIL … check1-no-gate` twice; `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2`; rc 1 | worktree at ea0bbe6 and again at ba8b54b |
| E8 | same gate command, `--root /var/tmp/souji-r26-ScribeScorecardR26/gt`, mirroring the two **draft** entries (`.ufo/waves/round-26/w1/entry-*.md`) plus `corpus/SOURCES.md`, snapshots and empty slice/verdict files | `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`; rc 0 | scratch mirror of worktree bytes |
| E9 | `python3 -B tools/souji-coverage-agreement.py --root . --rev d6fe8a1… --base-rev 0eca7c8…` | `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`; rc 0 | d6fe8a1 |
| E10 | `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | last lines W04 duplicate-url warnings for S092-S108/S123-S126, then `ok …/corpus/SOURCES.md`; rc 0 | worktree at ba8b54b |
| E11 | `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` | `claims=3 flags=0`; rc 0 | worktree at ba8b54b (same value as `c3-after.tsv` at d2e6253) |
| E12 | `cat census/round-26/records/c3-{before,after,control}.tsv` | before `rev=89e0fce`, `axis_check_tool=absent`; after `rev=d2e6253`, `claims=3 flags=0`, `axis_check_exit=0`; control `rev=d2e6253`, `cases=11 pass=4`, `control=FALSE-GREEN-REJECTED`, rc 1 | receipts |
| E13 | `sha256sum tools/souji-axis-check.py tests/fixtures/r26-axis-check.py .ufo/waves/round-26/w1/r26-axis-check.py` | `14bc9632…`; `2ffc1828…` (11 cases, 226 lines); `220eed2e…` (12 cases, 407 lines) | worktree at ba8b54b |
| E14 | `git cat-file -e 0eca7c8:census/round-26/c1-counter.sh` / `0eca7c8:tools/souji-axis-check.py` | both rc 128 (`exists on disk, but not in '0eca7c8'`) | base |
| E15 | `git rev-parse 0eca7c8:SCORECARD.md 12fd90b:SCORECARD.md` and the same for `corpus/SOURCES.md`, `corpus/README.md`, `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` | identical blob ids base vs freeze (`4b564bc6…`, `f3cffccd…`, `a8c97fe9…`, `5e081957…`) | 0eca7c8 vs 12fd90b |

Not run by this seat: the 12-case fixture `python3 -B …/w1/r26-axis-check.py --tool tools/souji-axis-check.py`.
Its `cases=12 pass=12 control=FALSE-GREEN-REJECTED` value is quoted from
`.ufo/waves/round-26/w1/ExecAxisFixture.md` arm B, not from a command of mine — the fixture pins its
scratch base at `/var/tmp/souji-r26-ExecAxisFixture` and a live sibling was running that arm.

## Findings

1. **C2's frozen K2 is red on the committed entries.** Both `corpus/knowledge/git-auto-maintenance-trigger-set.md`
   and `…-r23.md` carry no `## Gate` heading — at `0833de9` (their landing), at `ea0bbe6`, and in the
   worktree; the tool's check1 requires one (`tools/souji-gate-check.py:7,74`). Live result:
   `entries=2 ok=0 fail=2`, rc 1. The wave drafts at `.ufo/waves/round-26/w1/entry-git-auto-maintenance-trigger-set.md:111`
   and `…-r23.md:102` do carry compliant Gate blocks, and the identical command on those bytes in a
   `/var/tmp` mirror is `entries=2 ok=2 fail=0` rc 0 (E8). Landing the drafts' Gate sections is the
   whole gap; the prereg's K2 after-value is achievable.
2. **C3's K2 is not met by committed bytes.** `tests/fixtures/r26-axis-check.py` is 226 lines, 11
   cases, sha256 `2ffc1828…`, with no r25-C2 replica case; `census/round-26/records/c3-control.tsv`
   itself prints `cases=11 pass=4`. The frozen contract is 12 cases with case 1 the r25-C2 replica
   (`preregistration.txt` claim C3, K2). The 12-case delivery is
   `.ufo/waves/round-26/w1/r26-axis-check.py` (sha256 `220eed2e…`) and is unlanded.
3. **The round lesson's `## Receipts` disagrees with its receipts.**
   `corpus/lessons/round-26.md` `## Receipts` says `c2-before.tsv` is at "base 89e0fce" (receipt:
   `12fd90b`) and `c2-after.tsv` at `d6c13b0` (receipt: `e0f8dcd`); its opening paragraph and the
   `0833de9` subject also describe an **11-case** fixture where the prereg freezes 12. Same file,
   `## Gate`, attributes the whole exposure denominator correctly; only the receipt coordinates drift.
4. **The frozen red-before commands are unexecutable at the named base.** `census/round-26/c1-counter.sh`
   does not exist at `0eca7c8` (rc 128, E14), so the prereg's verbatim red-before command cannot run
   there; the receipts bind the freeze commit instead (`c1-before.tsv`, `c2-before.tsv` rev `12fd90b`;
   `c3-before.tsv` rev `89e0fce`). Byte identity of the measured files at base vs freeze is verified
   (E15), so the *values* are base-equivalent, but the receipts do not bind the rev the claim names.
   Report as a contract defect for the judge; do not restate it as a base measurement.
5. **Two required C2 receipts do not exist.** `census/round-26/records/` holds no `c2-gate.tsv` and no
   `c2-k4-after.tsv`, while `d6c13b0`'s subject asserts "real gate rc=0" and the lesson repeats
   "real gate rc=0". That is a claim-level number with no bound receipt (Q55 class); K3 and K4 also
   have no receipted after-state.
6. **The C2 scratch mirror gate left no evidence.** `preregistration.txt` C2 requires a copy of
   `corpus/` plus the append block and admitted entries at
   `.ufo/waves/round-26/assimilation/validate/`, validated with `--file` before the first real append.
   That directory does not exist in the tree or at any commit; `git log -- .ufo/waves/round-26/assimilation`
   returns only `965b869`, which adds `quarantine-slice` and `slice-verdicts-r26.tsv`.
7. **C2 landed under a C3 commit message.** `0833de9` is titled `round-26 C3: tools/souji-axis-check.py
   + 11-case fixture …` but also adds both knowledge entries, the `corpus/README.md` F1 row change,
   rows S128-S132 in `corpus/SOURCES.md`, and all seven `census/round-26/sources/` snapshots (14 files
   total). A claim whose evidence lands in another claim's commit is auditable only by diff, not by log.
8. **Every green-after receipt is at a superseded commit.** `c1-after` binds `07f83e6` (tip later
   `ba8b54b`), `c2-after` binds `e0f8dcd`, `c3-after`/`c3-control` bind `d2e6253`. The draft marks each
   as `RECEIPT-PENDING` at the final tip; the C1 counter's own literal triple will shift again when the
   Round 26 measurements section is inserted above `SCORECARD.md:17`.
9. **`## Planned` is closed to the r26/r27 bullets by C1's own kill rule.** Amendment 2 span 6 is
   "the base `## Planned` section (95-137) with **exactly the two** fenced r24/r25 planned bullets
   appended". Adding a third and fourth bullet there makes that span's byte-diff non-empty, i.e. a C1
   kill; the draft lands them in an EOF `### Round 26 planned-roll` block instead (section 3), which is
   the only placement that keeps both C1 and the newest-first layout contract satisfiable.
10. **No axis was relabelled and no score moved.** C1 calibrates, C2 is coverage on ground F1 already
    held frontier (expansion unchanged, no promotion), C3 is an operability instrument. The r25
    failure mode (C2 declared on operability while changing a coverage surface) is exactly what the new
    R2 rule now flags; the frozen prereg self-checks clean (`claims=3 flags=0`).

## Deliverable

`.ufo/waves/round-26/w1/scorecard-r26.md`: (1) the `### Round 26 measurements` table in the r25
shape with per-cell receipt or `RECEIPT-PENDING` plus the score-delta paragraph, (2) the capability
row `prereg axis-check (r26)`, (3) the r26-done and r27-planned bullets in a landing-safe EOF block,
(4) the quality and discernment verdict sentences, (5) five post-landing checks.

## Limits

- Leaf seat: no subagent dispatch, no lane writes beyond this report and the named delivery file, no
  git/jj mutation. Read-only `git log/show/rev-parse/cat-file/merge-base` only.
- Live runs in E7-E11 are this seat's checks, not claim receipts (no `receipt=v1` binding, no
  `verify=ok`); the draft keeps them labelled as such and leaves the receipt slots empty.
- The 12-case fixture was not executed here (fixed `/var/tmp/souji-r26-ExecAxisFixture` base in use by
  a live sibling); its 12/12 is quoted from `w1/ExecAxisFixture.md`, an execution of another seat.
- The C1 protected-span byte-diff was not re-derived by this seat; the draft cites the round lesson's
  claim that it is empty and leaves the span check as post-landing step 5.
- Tip moved four times during the run (`d2e6253` → `e0f8dcd` → `ea0bbe6` → `d6fe8a1` → `ba8b54b`);
  line numbers in the draft name the revision they were read at and will need one re-read at the final tip.
- No tool install or upgrade was performed or needed; no pacman transaction attempted.
- Scratch `/var/tmp/souji-r26-ScribeScorecardR26/` removed before yield.
