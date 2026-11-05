# Round 62 — index-flag concealment refused before a clean-tree receipt (C1 operability), stale flag statements counted (C2 calibration)

Base `16fa821fdce00e709d6895ccfc7aaffa465af195`. Frozen predicates: `census/round-62/preregistration-freeze3.txt`
(freeze commit `c5af0e0abad41e4e08558e994959def277b7f19f`, `tools/souji-freeze-check.py --substance` → `SUMMARY claims=2 findings=0`,
EXIT 0). Controls commit `71471699` (C1 receipt, C2 population) and `57a85817` (C2 receipt), strictly before the freeze.
Candidate writer commit `a0b396cd`. C2 after-state commit `918bb423`.

## Claim

- **C1, operability (score 8, numeric delta 0; no reproducible 0–10 mapping).** `tools/souji-receipt-write.py` refuses,
  before its dirty check and regardless of `--allow-dirty`, any tracked index entry whose `git ls-files -v` tag is not `H`,
  with the message `RECEIPT-INDEX-FLAG-CONCEALED:`. Counter `census/round-62/c1-counter.py` over the frozen 7-row matrix
  `census/round-62/c1-matrix.tsv`. Measured: `new_forgeries=0 new_honest=2 class_mismatches=0 regress=PASS`, EXIT 0
  (`census/round-62/records/c1-after.txt`). Do-nothing (base bytes in the new slot): `new_forgeries=3`, EXIT 1
  (`census/round-62/controls/c1-do-nothing.txt`). Lane index at base: 17350 entries, all `H` (`git -C <lane> ls-files -v | cut -c1 | sort | uniq -c`), so the refusal blocks no honest run today.
- **C2, calibration (score 7, the lane's lowest owned axis).** Live self-assessment statements about index-flag behaviour
  must not describe the refusal as open or routed once it has landed. Counter `census/round-62/c2-counter.py` reads committed
  bytes of four frozen files. Base: `stale_open=4 landed=0 FAIL` (`census/round-62/controls/c2-do-nothing.txt`). After
  (`918bb423`): `stale_open=0 landed=3 PASS` (`census/round-62/records/c2-after.txt`). The stale statements were
  `SKILL.md:830`, `corpus/README.md:973` and `corpus/knowledge/skip-worktree-concealment.md:35–36`.
- **Dependency, disclosed.** C2's counter reads text, so it can be verified without C1's code, but the statements it
  requires (`landed>=3`) are true only if C1 lands. Stated in `census/round-62/preregistration-freeze3.txt`.

Round shape: two claims on distinct axes (C1 operability, C2 calibration). The first draft of this round declared one
calibration claim on the writer; the critic (`S62CriticClaim`, F1–F3) refused it as a Q59 axis misattribution and
required C2, so the round was re-split before any after-data was taken. The predicate, matrix and kill rule of C1 did not change.

## Gate

Sources opened 2026-11-05 by the scout seat `S62ScoutSources` (captures and checks under
`census/round-62/sources/` and `census/round-62/wave/S62ScoutSources/`; `quote-check.txt` records the verbatim checks).

- **S292 admit** — git-ls-files(1) `-v`/`-t` tags, https://git-scm.com/docs/git-ls-files, OPTIONS, anchor
  `Documentation/git-ls-files.txt--v`; accessed 2026-11-05 (HTTP 200; sha256 `39bbbe6a…f5f08`).
  Located quote (17 words): `Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1]).`
  Verbatim in the raw capture (offset 8351) and the tag-stripped text (offset 7629). The `-t` list (5 words, `tracked file that is skip-worktree`,
  verbatim at offset 7308) gives `S`. Scope: the tag letters the writer's parse depends on. The row does not document
  status or sparse-checkout interaction, which the candidate does not rely on. The probe (scout, `probe_tags.sh`,
  `S62ScoutSources/probe-evidence.txt`) reproduces `S` for skip-worktree and `h` for assume-unchanged on git 2.56.0.
- **S291 re-open (not a new row; no cell change)** — git-update-index(1) NOTES, https://git-scm.com/docs/git-update-index.
  Re-opened 2026-11-05 (captured `census/round-62/sources/s291-reopen-git-update-index.html`, sha256
  `ecaa637b…43fb8`, identical to the r61 capture). Quote verbatim: `This does not work as expected, since Git may still check working tree files against the index when performing certain operations.`
  Recheck decision: the scout proposed `recheck = 2026-11-05`; rejected, because `scripts/sources-census.sh overdue`
  reads an ISO date as a due date and would report the row overdue on the day it was re-read. `recheck` stays `180d`.
  Change old→new: none. `status` `mined`, `used-by` unchanged.
- **Rejected inference (discernment sample).** "A silent `git status --porcelain` certifies that the lane's tracked
  entries match their committed blobs." Rejected on S291 NOTES; the probe `census/round-62/wave/S62ExecCandidate/rows-base.txt`
  shows the silent status with forged bytes under `S` (row D, base ACCEPT). Flip: a manual statement that `status`
  reports skip-worktree paths.
- **Registry**: 215 → 216 rows (S292 added, `corpus/SOURCES.md:252`); `scripts/sources-census.sh validate --root … souji` at round end, see report.
- **Non-author spot-check (LEARNING.md)**: pending. The L1 does not check its own gate decisions. The closure reviewer
  must re-open S292 and sample it, plus the rejected inference. Recorded as `not yet spot-checked`.
- **Assimilation: none.** The connector `S62ConnectorOverlap` read `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` (read-only): the staged package holds no index-flag, skip-worktree or clean-tree theme. No `considerthese/` directory exists in this lane.

Admitted knowledge: `corpus/knowledge/skip-worktree-concealment.md` (source line now names S292; `## Consequence` rewritten for the landed refusal and its named limits). No new knowledge entry; the F1 row stays `frontier, entries held`.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Concealment trusted as clean-tree evidence: the receipt writer's dirty check was `git status --porcelain` alone, so a tracked entry under skip-worktree or assume-unchanged made a forged worktree pass | pre-fix `tools/souji-receipt-write.py` line ~131 (`git status --porcelain`); base do-nothing receipt `census/round-62/controls/c1-do-nothing.txt` (rows D, E, F accepted, `new_forgeries=3`); `census/round-61/` reviewer HIGH-1 (`.ufo/waves/round-61/w1/S61ReviewerC2.md`) | none (no rule required the writer to read index flags; the r61 reviewer's probe was filed as a routed defect, not a gate) | Q123 and the C1 refusal in `tools/souji-receipt-write.py` (commit `a0b396cd`). Shown able to fail: the base bytes give `new_forgeries=3` `EXIT=1` on the same matrix; the candidate gives `new_forgeries=0` `EXIT=0` |
| M2 | Freeze record submitted without running the freeze checker on its controls: two freeze attempts were refused for receipt grammar (no `command=`, `instrument=`, `instrument_sha256=`, `rev=`, last-line `EXIT=`), and the C2 population was prose | freeze 1 `31bb318ddbae586e1c7287f700b004b4cde6b2f6` (`census/round-62/preregistration.txt`), refused by `tools/souji-freeze-check.py --substance` (CONTROL-COMMAND-MISSING, CONTROL-INSTRUMENT-MISSING, CONTROL-REV-MISSING, CONTROL-NOT-RED, POPULATION-MISSING); freeze 2 `a1b2000fff7ef7ceb86343cdc533338dfc807571` (`census/round-62/preregistration-freeze2.txt`) refused for the C2 receipt header | none (the controls were written by hand from seat output; the checker was not run on them before committing the freeze) | controls regenerated in receipt format (`71471699`, `57a85817`); freeze 3 `c5af0e0a` passes `findings=0`. Shown able to fail: freeze 1 and freeze 2 are refused by the same checker; both attempts remain in history, unedited |
| M3 | Self-assessment left an open status after the fact: three live statements said the writer's flag blindness was "routed to round 62" | `census/round-62/controls/c2-do-nothing.txt` (`stale_open=4` at base: `SKILL.md`, `corpus/README.md`, `corpus/knowledge/skip-worktree-concealment.md` ×2) | none (no rule compared the lane's statements against the writer's behaviour) | C2 counter; the three statements rewritten (`918bb423`). After: `census/round-62/records/c2-after.txt` (`stale_open=0 landed=3`) |

Mistake M2 is the round's process defect; M1 and M3 are the claims' own defects.

## Wave findings (Q121: every C or H finding, with disposition)

Wave: one v1 wave, 10 seats (`census/round-62/wave/`): executor 2, scout 1, scribe 1, reviewer 2, critic 1, mutation-tester 1, connector 1, sentinel 1. Attack seats 5/10 (reviewer, reviewer, critic, mutation-tester, sentinel). Planner held by the L1 (the wave validator refuses a planner seat). No dead seat (`census/round-62/wave/w1-results.json`).

| finding | sev | source | disposition |
|---|---|---|---|
| F1 calibration label is a Q59 misattribution: a runnable writer on an input edge class is operability | H | S62CriticClaim | adopted: C1 is operability; C2 added as the calibration claim |
| F2 the lane's `souji-axis-check.py` R2 has no surface class for a runnable tool on an edge class | H | S62CriticClaim | named: the instrument is not changed this round (its R2 grammar is not in this claim) |
| F3 R3 forces a calibration claim when the lowest axis is calibration | H | S62CriticClaim | adopted: C2 on calibration satisfies the lowest-axis obligation |
| F4 the clean-tree assertion survives flags and edits made during the run | H | S62CriticClaim; S62SentinelScope probes 27–29 | named limit (start-of-run only), not claimed; the rewritten knowledge entry says so |
| A10 the counter must bind the refusal class, not the exit code alone (a stub that refuses with another message passes rc) | C | S62ReviewerDesign | adopted: the counter matches `RECEIPT-INDEX-FLAG-CONCEALED` on stderr for rows D–G (`class_mismatches`) |
| A5 / A18 / A19 non-cone sparse checkout sets `S` on paths; the lane is unaffected (17350 `H`) | H | S62ReviewerDesign | named limit: the rule refuses it, the claim does not cover sparse checkouts |
| A9 no bypass: `--allow-dirty`, `--max-bytes`, `--style`, `GIT_DIR`/`GIT_WORK_TREE`, post-check probing all keep rc 2 | H (pass) | S62ReviewerDesign | recorded: no bypass found |
| A2 the `ls-files -v -z` record layout is `tag SP path` with raw paths (newline preserved) | L→H | S62ReviewerDesign; S62ReviewerCandidate (names with newline, space, dash, non-UTF-8 refused) | adopted: the candidate parses `rec.partition(b" ")` and the probes refuse all four names |
| A4 untracked files cannot carry index flags on git 2.56.0 | H→L | S62ReviewerDesign | recorded: the rule covers tracked entries only |
| A8 row F (skip-worktree, unmodified) is a calibrated refusal, not blanket harm | M | S62ReviewerDesign | adopted: F stays a refuse row; the falsifier (an honest `S` on a counter at byte-identical state) is named |
| A11 do-nothing `new_forgeries=3` with G refused for another reason | M | S62ReviewerDesign | adopted as measured; G is an honest refusal of the base, not a forgery; the predicate pins `new_forgeries=3`, not the class count |
| A12 the claim is calibration-labelled but operability in substance | M | S62ReviewerDesign | resolved by the split: C1 operability, C2 calibration |
| A3 skip-worktree on a worktree-deleted path hides the deletion | M | S62ReviewerDesign | named limit; a D2 row was proposed, not added this round |
| A7 gitlink skip-worktree hides a submodule HEAD change | M | S62ReviewerDesign | named; the candidate refuses it unconditionally |
| F5 whole-index scope: a flag on an unrelated unmodified path refuses an honest receipt | M | S62CriticClaim | named limit (no honest lane shape is refused today) |
| F6 row F refuses honest bytes; the writer could hash on-disk bytes instead | M | S62CriticClaim | named cost; kept fail-closed |
| F7 an unmerged path emits `M` tags and is reported as concealment | M | S62CriticClaim | named limit: the refusal message is misleading there |
| F8 do-nothing line: printed `class_mismatches=4`, not the `1` the critic suggested | M | S62CriticClaim | recorded as measured: the frozen predicate does not pin class_mismatches for the do-nothing arm |
| F9 class check is a stderr substring | M | S62CriticClaim; S62ReviewerDesign A10 | named limit |
| F10 the r60 fixture and writer selftest are non-regression only | M | S62CriticClaim; S62ExecCandidate | named limit; regression arm recorded (8/8 both arms) |
| F11 S292 not yet a registry row; capture absent at check time | M | S62CriticClaim | resolved: captures written; row added (`corpus/SOURCES.md:252`) |
| F12 S291 "re-open" was a read, not a re-fetch | L | S62CriticClaim | resolved: the scout re-fetched `update-index` (`census/round-62/sources/s291-reopen-git-update-index.html`, sha256 matches the r61 capture) |
| F13 the lesson requirement (`## Mistakes`, `## Named limits`, Q121 dispositions) | L | S62CriticClaim | adopted: this lesson |
| F-4 TOCTOU: flags set during the wrapped command produce an accepted forged receipt (probes 27, 28, 29) | H | S62SentinelScope | named limit; the receipt does not bind index or worktree state at run time |
| F-5 honest over-refusal (flagged path unrelated to the receipt) | M | S62SentinelScope | named with F5 above |
| M4 `--ignore-submodules=all` and M6 `ls-files --others` survive the r60 fixture's dirty case | M | S62MutDirtyCase | named: the r60 fixture is not a kill-power witness for the dirty block; the C1 matrix does not cover those mutants |
| mut-M1 (dirty block removed) killed by r60 case 8; concealment D, E, F accepted by every mutant including base | H | S62MutDirtyCase | named: the concealment rows are covered only by this round's matrix (C1) |

## Routed defects (round-61 spot-check, `corpus/lessons/round-61-verifier-spotcheck.md`)

1. Receipt-writer skip-worktree blindness (HIGH-1): **closed by C1** (`a0b396cd`; `census/round-62/records/c1-after.txt`).
2. `## MACHINE BLOCK` preregistration requirement (critic F13, Q59): **not implemented**. It needs an operator decision (whether `souji-axis-check.py` binds this lane's preregistrations). L0 question appended (`.ufo/l0-questions.md`, line 324).
3. F3 (delete-and-re-add at freeze with new bytes) matrix row: **not in this round**; a named limit of the freeze checker, unchanged.
4. Historical records (rounds 41–55, 60 gain `CONTROL-ADDED-NOT-BEFORE-FREEZE`): **unchanged**, reported, not rewritten.
5. Numeric axis mapping (no reproducible 0–10 mapping for calibration and coverage/operability): **not resolved**; the score cells are unchanged. L0 question appended (line 325).

## Named limits

- **Start-of-run only.** The writer checks index flags before the wrapped command and does not check them again. A flag set, or a tracked file edited, during the run produces a receipt that binds neither (sentinel probes 27–29; the `instrument_sha256` in the receipt is the committed blob's digest even when the worktree instrument was forged during the run).
- **Whole-index scope; unmerged paths.** Any non-`H` tag anywhere in the index refuses; an unmerged path is reported as concealment.
- **Substring class check.** The counter matches `RECEIPT-INDEX-FLAG-CONCEALED` on stderr; a traceback containing that text would count.
- **Seven rows only.** No sparse-checkout, gitlink, deleted-worktree, or unmerged row in the frozen matrix (reviewer A3, A5, A7; critic F7).
- **C2 is text-only.** `stale_open=0` says the statements are closed; it does not verify that they are true. Their truth rests on C1's counter and on this lesson.
- **Freeze history.** Three freeze records exist (1, 2, 3). Only freeze 3 is the round's predicate.
- **Non-author verification pending** for S292 and for both claims.

## Integrated verification

- Freeze 3: `python3 -B tools/souji-freeze-check.py --root . --prereg census/round-62/preregistration-freeze3.txt --rev c5af0e0abad41e4e08558e994959def277b7f19f --substance` → `SUMMARY claims=2 findings=0`, EXIT 0 (`census/round-62/records/freeze3-check.txt`).
- C1 after (candidate `a0b396cd`): `census/round-62/records/c1-after.txt`: `SUMMARY matrix=7 base_forgeries=3 base_honest=2 new_forgeries=0 new_honest=2 class_mismatches=0 regress=PASS`, EXIT 0.
- C1 do-nothing (base bytes): `census/round-62/controls/c1-do-nothing.txt`: `new_forgeries=3 … class_mismatches=4`, EXIT 1.
- C1 stubs (always-accept and always-refuse, counter must fail both): `census/round-62/controls/c1-stubs.txt` (EXIT 1 for each).
- C2 after (`918bb423`): `census/round-62/records/c2-after.txt`: `SUMMARY files=4 stale_open=0 landed=3 verdict=PASS`, EXIT 0.
- C2 do-nothing (base `16fa821f`): `census/round-62/controls/c2-do-nothing.txt`: `stale_open=4 landed=0 verdict=FAIL`, EXIT 1.
- r60 writer fixture on the candidate (`tests/fixtures/r60-receipt-write.py --tool tools/souji-receipt-write.py`): `SUMMARY cases=8 pass=8 fail=0`, both controls rejected (seat `S62ExecCandidate`, `r60-candidate.log`; the counter's regress arm, `regress=PASS`).
- Lane index after landing: `git ls-files -v` non-`H` count: see report.

## Routed to round 63

- Non-author spot-check of S292 and of both claims (the closure reviewer).
- In-run TOCTOU (F4): a successor claim would bind the receipt to a second index and worktree read after the command, or refuse changes during the run; not claimed here.
- Concealment rows beyond the seven (unmerged, gitlink, deleted-worktree, sparse-checkout), with mutants.
- The class check as a structured field rather than a stderr substring.
- `## MACHINE BLOCK` and numeric-mapping questions, pending the operator.

## Post-review correction (round 63, append-only; R2 of `round-62-verifier-spotcheck.md`)

The `## Gate` sentence "Verbatim in the raw capture (offset 8351)" is wrong. The S292 quote is located only after
HTML markup stripping (tag-stripped offset 7629, the `-v` definition; the raw HTML splits it around `</code>`). The
S291 quote is likewise located after stripping. Located-after-stripping is the claim the row supports.
Recorded in `corpus/lessons/round-63.md` M4. The original sentence is not rewritten.
