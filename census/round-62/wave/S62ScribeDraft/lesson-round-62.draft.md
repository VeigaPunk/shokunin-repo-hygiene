# Round 62 — index-flag concealment refused before a clean-tree receipt (C1 calibration)

One claim. C1 calibration (the lowest owned axis, score 7; no reproducible 0–10 mapping, so the numeric score
is unchanged): `tools/souji-receipt-write.py` refuses a receipt whose index carries a non-`H` tag (skip-worktree
`S`, assume-unchanged `h`) before its clean-tree check runs. The round-61 review defect (reviewer
HIGH-1, `corpus/knowledge/skip-worktree-concealment.md`) is the motivating defect: the base dirty check is
`git status --porcelain` alone (`tools/souji-receipt-write.py` line 131), and a tracked path with skip-worktree set
is silent under it.

Lane base `16fa821fdce00e709d6895ccfc7aaffa465af195`; freeze `{{FREEZE}}`; control receipts `{{CONTROL}}`;
after-measurement at `{{COMMIT_MEASURED}}`. Predicate `census/round-62/preregistration.txt`.

## Claim

C1 is the refusal rule and nothing else: in `write_receipt`, before the existing `# behaviour 7` dirty-status
block, the writer runs `git ls-files -v -z`. If that fails it refuses `cannot read index flags ...`; for each record
whose tag (first byte) is not `H` it refuses with a message beginning `RECEIPT-INDEX-FLAG-CONCEALED:` that names the
path and tag. The refusal is unconditional: `--allow-dirty` does not override it. No other behaviour changes; the r60
fixture bytes stay green.

Frozen 7-case matrix (the counter builds each repo):

| row | shape | expected |
|---|---|---|
| A | honest-clean: committed instrument, counter and notes; clean tree; no flags | ACCEPT |
| B | A plus a visible tracked edit to notes, passed with `--allow-dirty` | ACCEPT |
| C | visible tracked edit to notes, no `--allow-dirty` | REFUSE, `lane worktree is dirty` |
| D | `update-index --skip-worktree tools/counter.py` plus forged counter bytes | REFUSE, `RECEIPT-INDEX-FLAG-CONCEALED` (base: ACCEPT) |
| E | `update-index --assume-unchanged tools/counter.py` plus forged bytes | REFUSE, `RECEIPT-INDEX-FLAG-CONCEALED` (base: ACCEPT) |
| F | `update-index --skip-worktree tools/counter.py`, bytes unchanged | REFUSE, `RECEIPT-INDEX-FLAG-CONCEALED` (base: ACCEPT) |
| G | `update-index --skip-worktree tools/instr.sh` plus forged instrument bytes | REFUSE, `RECEIPT-INDEX-FLAG-CONCEALED` (base: REFUSE, instrument-differs reason) |

Frozen predicate: over rows A–G the candidate scores `new_forgeries=0` (D, E, F refused), `new_honest=2` (A, B
accepted), `class_mismatches=0` (each refusal names its expected class), G refused; and
`tests/fixtures/r60-receipt-write.py --tool <candidate>` reports `{{R60_FIXTURE_TALLY}}` with both controls rejected.
Kill rule: any of those is false, or the counter exits nonzero.

Frontier (sourced): the claim's evidence cites git-update-index(1) NOTES (S291, re-opened this round) and the
git-ls-files(1) `-v` tag definitions (S292, opened this round by a scout seat).

## Gate

Sources opened 2026-11-05 by the wave's scout seat (`S62ScoutSources`) under the lane's dispatch; captures and
digests in `.ufo/waves/round-62/w1/S62ScoutSources/captures/` (`SHA256SUMS`).

- **S292 {{S292_DISPOSITION}} (git-ls-files(1) `-v`)** — https://git-scm.com/docs/git-ls-files, anchor `{{ANCHOR_S292}}`,
  access date `{{ACCESS}}`. Located quote: `{{QUOTE_S292}}`.
  Scope: the tag letters `git ls-files -v` prints for index entries carrying skip-worktree (`S`) or assume-unchanged
  (`h`). Used by the C1 rule that refuses any non-`H` tag. The row does not document how other git commands treat the
  bits; that caveat is S291's.
  Rejected inference (proposed): "a path whose `git ls-files -v` tag is lowercase or `S` has a clean worktree".
  Flip: a manual statement that the tag reflects worktree content. Whether the scout's capture contains one is
  decided by the scout's report, not by this draft `[INFERENCE]`.
- **S291 re-open (git-update-index(1), NOTES)** — https://git-scm.com/docs/git-update-index, anchor
  `Documentation/git-update-index.txt---notes`, access date `{{ACCESS}}`. Re-open result: `{{S291_REOPEN_RESULT}}`.
  Located quote: `{{QUOTE_S291}}`.
  Scope: the skip-worktree bit makes a clean porcelain status unreliable as evidence about worktree bytes. Recheck
  `2026-11-05`, result `{{S291_RECHECK_RESULT}}`, status `mined`, `used-by` unchanged.
- **Admit/reject lines for the knowledge update** (`corpus/knowledge/skip-worktree-concealment.md`):
  - admit S292 as the tag-definition source for the `RECEIPT-INDEX-FLAG-CONCEALED` rule — `{{S292_DISPOSITION}}`;
  - admit S291 re-open with recheck `2026-11-05` — `{{S291_RECHECK_RESULT}}`;
  - keep the rejected inference "a silent `git status --porcelain` certifies the worktree bytes of a flagged path";
    rejected on S291 NOTES; the knowledge entry's `## Consequence` section is updated to name the C1 refusal as
    implemented in round 62 (was: routed).
- Non-author spot-check (`LEARNING.md`): **pending**. The L1 does not check its own gate decisions; the closure
  reviewer must re-open S292 and S291 and sample at least one admit and the rejected inference. Recorded as
  `not yet spot-checked`.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Concealment trusted as clean-tree evidence: the receipt writer's dirty check reads `git status --porcelain` alone, which does not report a tracked path whose index entry carries skip-worktree or assume-unchanged; the r61 reviewer probe reproduced the silence | `tools/souji-receipt-write.py` line 131 (`st = git(root, "status", "--porcelain")`); r61 wave seat `S61ReviewerC2` HIGH-1, cited in `corpus/lessons/round-61.md` (Wave findings, Named limits) and in `corpus/knowledge/skip-worktree-concealment.md` (Measured) | none: no rule required the writer to see index flags; the r61 wave routed the finding without a gate | C1 refusal `RECEIPT-INDEX-FLAG-CONCEALED` in `write_receipt` before behaviour 7, unconditional under `--allow-dirty`. Fix shown able to fail: base bytes in the candidate slot give `new_forgeries={{DO_NOTHING_FORGERIES}} EXIT={{DO_NOTHING_EXIT}}` (frozen expectation 3 and EXIT 1; the measured value is pasted by the L1, not the prediction) |

## Wave findings

One v1 wave, 10 seats (`.ufo/waves/round-62/w1/`). Attack share `{{ATTACK_SHARE}}`. Planner held by the L1.
Every C/H finding of the wave appears in this table with its disposition (QUALITY Q121); the L1 fills one row per
finding from the wave sweep. The row below is a template, not a finding.

| finding | sev | source | disposition |
|---|---|---|---|
| {{FINDING_ID}} | {{SEV}} | {{SEAT}} | {{DISPOSITION}} |

## Routed defects (round 61 spot-check)

| # | routed defect (r61) | disposition in r62 |
|---|---|---|
| 1 | HIGH-1: the honest writer accepts skip-worktree concealment of a non-instrument file | claimed as C1 this round; refusal `RECEIPT-INDEX-FLAG-CONCEALED` in the writer |
| 2 | MACHINE BLOCK absent from the preregistration (axis-check Q59; critic F13) | not implemented this round; an L0 question is appended (`l0-questions.draft.txt`): the operator must confirm that `souji-axis-check.py` runs on the preregistrations |
| 3 | F3 matrix row: delete-and-re-add at freeze | not in this round; named limit (see below) |
| 4 | historical records (rounds 41–55 freeze records and the r60 record) | unchanged, carried; append-only, not rewritten |
| 5 | numeric axis mapping (no reproducible 0–10 mapping) | not resolved; an L0 question is appended; the calibration score cell is unchanged (7) |

## Named limits

- **No concurrent-writer proof.** The refusal is a point check over `git ls-files -v -z` at the moment the writer runs.
  It does not show that no other process changes the index during the run.
- **Stderr-substring class check.** The counter identifies each refusal's class by the substring
  `RECEIPT-INDEX-FLAG-CONCEALED:` in stderr, not by a structured code.
- **TOCTOU window.** A flag set after the index read and before the receipt is written is not bound by the receipt.
- **Seven rows only.** The counter runs rows A–G; sparse-checkout, submodule paths and other flag shapes are not
  in the matrix.
- **Historical receipts are not re-scored.** Receipts already committed under the base writer keep their verdicts.

## Integrated verification

Values in `{{...}}` are not yet measured; bracketed predictions in the wave brief are not evidence until the L1 pastes
the measured line.

- Candidate writer selftest (`python3 -B tools/souji-receipt-write.py --selftest --work DIR`): `{{SELFTEST_TALLY}}`.
- r60 writer fixture (`python3 -B tests/fixtures/r60-receipt-write.py --tool <candidate> --work DIR`): `{{R60_FIXTURE_TALLY}}`.
- Do-nothing (base bytes in the candidate slot): `new_forgeries={{DO_NOTHING_FORGERIES}} EXIT={{DO_NOTHING_EXIT}}`.
- After (candidate bytes, at `{{COMMIT_MEASURED}}`): `new_forgeries={{AFTER_FORGERIES}} new_honest={{AFTER_HONEST}}
  class_mismatches={{CLASS_MISMATCHES}} row_G={{ROW_G}} EXIT={{AFTER_EXIT}}`.
- Counter command (exact, from the executor's receipt): `{{COUNTER_COMMAND}}`.
