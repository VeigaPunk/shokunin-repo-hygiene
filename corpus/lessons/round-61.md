# Round 61 — control-chronology binding by content (C1 calibration)

One claim. C1 calibration (the lowest owned axis, score 7; no reproducible 0–10 mapping, so the numeric score
is unchanged): the `--substance` arm of `tools/souji-freeze-check.py` binds a claim's `Control:` receipt to the
commit where its exact bytes first exist. The round-60 rejection (`corpus/lessons/round-60-verifier-spotcheck.md`,
rejected-harmed on the chronology of both control receipts) is the motivating defect; the r60 arm scored that
record `findings=0`.

Base `c7228424c3919ecf142bab1aec8181722d86467b`; instruments and do-nothing control `da7ceba3950fc3ac946a611791f56e12174272bd`;
freeze `9849e71851e28d5f1e88ef658418d3c136f94692` (`census/round-61/preregistration.txt`); after-measurement at the freeze revision.
C2 (receipt-writer fixture and mutant kill-power) is named, not declared: see Named limits.

## Gate

Sources opened 2026-11-05 by the wave's scout seat (`S61ScoutSources`) under the lane's dispatch; captures and
digests in `census/round-61/sources/` (`SHA256SUMS`).

- **S290 admit** — git-log(1), https://git-scm.com/docs/git-log, DESCRIPTION anchor `Documentation/git-log.txt---description`.
  Located quote (14 words): `Various other options and paths parameters can be used to further limit the result.`
  Scope: a path-limited history walk enumerates the commits that touch a receipt path. Used by the content rule's
  `git rev-list -- <path>`. The row does not document blob equality or ancestry composition; those come from
  `git cat-file` and `git rev-list` and are not sourced as a composition.
- **S291 admit (caveat row)** — git-update-index(1), https://git-scm.com/docs/git-update-index, NOTES anchor
  `Documentation/git-update-index.txt---notes`. Located quote (21 words): `This does not work as expected, since Git may
  still check working tree files against the index when performing certain operations.` Scope: the skip-worktree bit
  makes a clean porcelain status unreliable as evidence about worktree bytes.
- **Rejected inference (discernment sample)** — "a silent `git status --porcelain` certifies that the worktree matches the
  committed blob". Rejected on S291 NOTES above. Flip: a manual statement that skip-worktree paths are checked on
  every status call. The reviewer's probe (`S61ReviewerC2`, HIGH-1) reproduced the silence on git 2.56.0; that probe is
  evidence about the host, not a manual fact.
- **Re-opened, cells unchanged**: S288 `os.replace` (scout re-hash: `ece1ab71…79f68079`, 791358 bytes, identical to the
  committed capture; no drift). S289 rejection unchanged.
- **Registry**: 213 → 215 rows (S290, S291 added after S289; both `mined`, `used-by` the two knowledge entries).

Admitted knowledge: `corpus/knowledge/control-chronology-binding.md` (S290, S251), `corpus/knowledge/skip-worktree-concealment.md` (S291).

Non-author spot-check (`LEARNING.md`): **pending**. The L1 does not check its own gate decisions; the closure reviewer
must re-open S290 and S291 and sample at least one admit and the rejected inference. Recorded as `not yet spot-checked`.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Unsurfaced rejection-ground finding: the critic's Finding 1 (control receipts added by the freeze commit) was recorded only in the wave file and was not carried into the r60 report; the r60 report asserted the controls were committed earlier | `census/round-60/wave/w1/S60CriticRound/S60CriticRound.md` Finding 1; `corpus/lessons/round-60-verifier-spotcheck.md` routed defects 1 and 3 | none (no rule required surfacing a C/H finding that contradicts a filed assertion) | QUALITY Q121 (surfacing check) and Q122 (content-bound chronology). Fix shown able to fail: base arm on `rewritten-at-freeze` and `chrono-at-freeze` gives `new_forgeries=2 class_mismatches=2 EXIT=1` (`census/round-61/controls/c1-do-nothing.txt`) |
| M2 | Predicted, not measured: the wave spec predicted the do-nothing count `new_forgeries=2` on an 11-row matrix; the base arm's measured value on that matrix was 1, because the base already refuses `chrono-after` (`CONTROL-MISSING`) | `.ufo/waves/round-61/w1/S61ExecChronoArm/receipts/counter-plain.txt` (`new_forgeries=1`) | none (the prediction was in the wave brief, not checked against a run) | the frozen pins came from a base-arm run before freeze (`census/round-61/controls/c1-do-nothing.txt`), and the matrix gained the `rewritten-at-freeze` row that raises the base count to 2 with a measured reason |
| M3 | Axis misattribution carried into a wave brief: C2 (receipt-writer fixture) was declared operability; the critic classed it coverage (r25 precedent), and the reviewer found the honest writer accepts skip-worktree concealment | `.ufo/waves/round-61/w1/S61CriticRound.md` F7, F8; `.ufo/waves/round-61/w1/S61ReviewerC2.md` HIGH-1 | the critic (wave seat, not a gate) | C2 removed from the claims; the mutants and fixture stay as wave evidence; routed to round 62 with HIGH-1 |
| M4 | Scratch discipline breach by the L1: two run outputs written to `/tmp` (`/tmp/r61-run-out.json`, `/tmp/r61-run-err.txt`), flagged by the sentinel scope check | `.ufo/waves/round-61/w1/S61SentinelScope.md` writeScope | sentinel (scope check) | files removed; later L1 runs write only under `/fast/scratch/hyaku/souji-r61/` |

## Named limits

- **Bytes, not execution.** The rule proves that a receipt's bytes existed before the freeze; it does not prove a command
  produced them. A fabricated receipt committed before the freeze passes. (Same limit as the round-57 recorder doctrine.)
- **Content check is history-bounded.** It walks `git rev-list -- <path>` from the freeze's parents; a merge that hides a
  path-touching ancestor makes the check refuse (fail closed). Not measured on a merge topology; the matrix is linear.
- **F3 not measured separately.** The critic's delete-and-re-add-at-freeze shape is refused by the same rule (bytes differ
  from every ancestor) but is not a matrix row this round.
- **Older records.** Rounds 41–55 freeze records already fail at base and gain `CONTROL-ADDED-NOT-BEFORE-FREEZE` on their
  control receipts. Their verdicts are historical; they are reported, not rewritten (append-only rule).
- **Critic F13 (preregistration completeness).** The r61 prereg lacks a `## MACHINE BLOCK` (axis-check Q59) and per-case
  expected findings in a separate Population; the expected classes live in the matrix and are checked by the counter.
  Not repaired in this round; routed.
- **C2 is not claimed.** Reviewer HIGH-1: `tools/souji-receipt-write.py` accepts a skip-worktree-concealed non-instrument
  file (dirty check is `git status`, line ~131). The r61 fixture (`census/round-61` wave: `S61ExecC2Fixture`) was not run as
  a claim; its partial-visibility case is timing-dependent (critic F9).
- **Mutation evidence (wave).** `S61MutationCounter` reported `m1-newest-add` surviving the frozen rows; under the content
  rule the add-commit family is no longer the candidate, so this survivor is retired with that rule, not with a repair.

## Integrated verification

- Candidate selftests (lane tip `da7ceba3`): `tools/souji-freeze-check.py --selftest` `cases=41 pass=41 fail=0`
  (`census/round-61/records/selftest-candidate-plain.txt`, EXIT=0); `--selftest --substance` `cases=15 pass=15 fail=0`
  (`selftest-candidate-substance.txt`, EXIT=0).
- Do-nothing (before freeze, base bytes in the new slot): `new_forgeries=2 class_mismatches=2 stubs=REJECTED EXIT=1`
  (`census/round-61/controls/c1-do-nothing.txt`).
- After (at freeze `9849e718`, candidate bytes): `matrix=12 base_forgeries=2 base_honest=4 new_forgeries=0 new_honest=4
  class_mismatches=0 stubs=REJECTED`, EXIT=0 (`census/round-61/records/c1-after.txt`).
- Real record, r61 freeze (candidate): `SUMMARY claims=1 findings=0`, EXIT=0 (`real-r61-freeze-candidate.txt`).
- Real record, r60 freeze (candidate): two `CONTROL-ADDED-NOT-BEFORE-FREEZE`, EXIT=1 (`real-r60-prereg-candidate.txt`);
  base: `findings=0` EXIT=0 (`real-r60-prereg-base.txt`).
- Default path byte identity: the base and candidate tools produce identical output without `--substance` on all 37
  lane preregistrations at the lane's full-40 revision (sweep, `census/round-61/records/` and the L1 sweep log); zero
  plain differences and zero refusals.
- Substance sweep (base vs candidate, 37 preregistrations): 11 records differ, every difference an added
  `CONTROL-ADDED-NOT-BEFORE-FREEZE`; no base finding removed; r60 flips pass→fail.

## Wave

One v1 wave, 12 seats (`census/round-61/wave/`): executor 3 (`S61ExecChronoArm`, `S61ExecRealRecord`, `S61ExecC2Fixture`),
scout 1, scribe 1, reviewer 2, critic 1, mutation-tester 1, sentinel 1, connector 1, revenger 1. Attack share 4/12
(reviewer, reviewer, critic, mutation-tester; 33%). Planner held by the L1 (wave validator does not admit planner).
No dead seat. Band 8–16 (run-15 policy). `w1-results.json` `status` per seat recorded in the wave dir.

## Wave findings surfaced (Q121: every C/H finding and its disposition)

| finding | sev | source | disposition |
|---|---|---|---|
| F1 literal `git log` walks HEAD, not the freeze | C | S61CriticRound | superseded: the content rule walks from the freeze's parents only |
| F2 receipt added green in an ancestor, rewritten red at freeze, passes an add-commit rule | H | S61CriticRound; S61ReviewerC1 HIGH-2 | fixed: content-bound rule; matrix row `rewritten-at-freeze` (base accepts, candidate refuses) |
| F3 delete and re-add at freeze with new bytes | H | S61CriticRound | refused by the same content rule; not a separate matrix row (named limit) |
| F4 r60 matrix builder put receipts in the freeze commit | C | S61CriticRound | fixed: honest rows commit the receipt in a group before the freeze; chronology rows built explicitly |
| F5 C1 scored on exit codes only; class not pinned; crashes count as refusals | H | S61CriticRound | fixed: the counter compares every refuse row's finding-class set (`class_mismatches`) |
| F6 do-nothing arm mis-specified | H | S61CriticRound | fixed: the do-nothing arm is the base bytes in the new slot, measured as `new_forgeries=2` |
| F7 C2 declared operability but is coverage | H | S61CriticRound | C2 not declared (M3) |
| F8 C2 honest half already met at base | H | S61CriticRound | C2 not declared (M3) |
| F9 partial-visibility kill is timing-dependent | H | S61CriticRound | C2 not declared; named |
| F10 tool bound by worktree, not the measured revision | M | S61CriticRound | tool bytes committed at `da7ceba3`, sha256 recorded in the after receipt; the freeze check reads committed blobs |
| F11 kill rules not exact negations; no mutant-survival clause | M | S61CriticRound | Kill line restated as the negation of the Target |
| F12 do-nothing reachability through unnamed kills | H | S61CriticRound | measured: base reaches `new_forgeries=2`, candidate `0`; C2 not declared |
| F13 preregistration completeness (MACHINE BLOCK, Q99 wave-dir clause) | M | S61CriticRound | named limit (`## MACHINE BLOCK` absent); routed to r62 |
| HIGH-1 post-freeze re-publication and add-rule blindness (`--diff-filter=A` on a freeze-bounded log) | H | S61ReviewerC1 | fixed by the content rule (same mechanism as F2) |
| C2 HIGH-1 honest writer accepts skip-worktree concealment of a non-instrument file | H | S61ReviewerC2 | routed r62; `corpus/knowledge/skip-worktree-concealment.md`; the C2 claim is not declared |
| m1 newest-add mutant survives the frozen rows | - | S61MutationCounter | retired with the add-commit rule; the content rule is the candidate |
| revenger: r60 `forgery-rev-at-freeze` passed for an accidental reason (`CONTROL-REV-INVALID` on a raw tag name, not the ancestry branch) | H | S61RevTagDegeneracy | the orphan-commit shape (`forgery-rev-orphan`, already in the matrix) pins `CONTROL-REV-NOT-BEFORE-FREEZE`; the tag case is retired |

## Fresh-start reads (operator Amendment 27, 2026-11-05: souji resumes at its next round)

Read before declaring: the rejected closures r58, r59 and r60 and their spot-checks, plus the r56 and r57 spot-checks
(the authorization's three-rejection window). Answers to the routed defects:

- r58 (C2 pre-freeze control chronology): this round's control commit `da7ceba3` precedes the freeze `9849e718`, and
  the do-nothing receipt is in the first commit. Answered for C1.
- r59 defect 1 (whole conjunction through the public path): the matrix covers the four forgery shapes r60 had and the
  two chronology shapes; a nonexistent-instrument row and a fenced decoy are not in this matrix (named limit).
- r59 defect 2 (Q99 `Round` header): the prereg begins `Round: 61`; the default checker grammar accepts it (`findings=0`).
- r59 defect 3 (fixture identity durability): the builder uses fixed dates and pins each case's commit hashes in `expected.txt`.
- r59 defect 4 (negative-claim sweeps): the sweep over 37 lane preregistrations is committed at `census/round-61/records/substance-sweep.txt`.
- r59 defect 5, r57 and r56 harms, r60 critic findings: open debts, carried in Named limits; not closed by this round.
- r57 defect 1 (C1 second opener / code span / escape / link / TAB): not in this round's claim; the visibility parser stays open.
