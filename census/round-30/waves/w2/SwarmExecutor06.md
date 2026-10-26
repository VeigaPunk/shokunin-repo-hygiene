# SwarmExecutor06 — round-end readiness attack (r30 w2, item PreReportGate)

## Status

STATUS: PASS — both gates were executed at `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8` and in a clean scratch control; the readiness answer is red: the landing gate exits 1 with two uncarried wave-1 failure lines, and the pre-report gate fails 3 of its 5 checks at the lane tip. The exact carry block was proven to clear the landing gate at a scratch commit.

## Evidence

- Landing gate at the tip (command as specified, `--round 30`): `SUMMARY findings=2 checked_reg=59 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=2 status_lines=35 carry_heading=0 checked_reports=49`, rc 1. JSON: `checked_ptrs=978 ptr_exempt=4 ptr_fleet=3`; the only findings are the two below. Receipt `SwarmExecutor06-landing-gate-tip.out` / `-tip.json`.
- Pre-report gate at the tip, canonical report target: `check-tip=PASS check-report=FAIL check-shonen=FAIL check-clean=FAIL check-prereg=PASS`, rc 1; `detail-clean:` lists `SKILL.md`, `corpus/QUALITY.md`, `corpus/lessons/round-30.md`. Receipt `SwarmExecutor06-prereport-lane-canonical.out`.
- Pre-report gate control (clean clone of a bare mirror of the lane at the tip, report carrying one `## SHONEN`): five PASS, rc 0. Receipt `SwarmExecutor06-prereport-scratch-clean.out`.
- Landing gate carry proof on a private `--no-local` clone (`origin` removed), lesson committed in scratch only: draft verbatim `2b331e0f1b36c6ae5d771657e29d96ccaea61a8f` → `findings=2 ... carry_heading=0`, rc 1; draft + the delivered section `fbdaa062293326784ed23d0ea1e31114d6e90050` → `findings=0 ... carry_heading=1`, rc 0. Receipts `SwarmExecutor06-draft-only-gate.out`, `SwarmExecutor06-carry-full-gate.out`.
- Carry-contract probes: mid-line ellipsis cut `580ccafd524cdd9bc5548a9c37cf9360194d4be0` → `findings=1`, rc 1; both entries stripped of `open` `4c634461f54c6969ba4af7235d9254c0de47abba` → `findings=2`, rc 1. Receipts `-variant-midline-ellipsis.out`, `-variant-no-open-token.out`.
- Discovery-precedence probe: draft-only state plus one force-added `.ufo/waves/round-30/w2/Note.md` (`00796bfd6d98518c8a15eb886a906672f838b2fb`) → `findings=0 ... checked_markers=0 status_lines=0 carry_heading=0 checked_reports=1`, rc 0. Receipt `-variant-partial-forceadd.out`.
- Round-29 control at the tip: `SUMMARY findings=0 ... checked_markers=7 status_lines=69 carry_heading=1 checked_reports=86`, rc 0. Receipt `-landing-gate-round29.out`.
- Enumeration: capture `census/round-30/waves/w1` `.md` = 49 = 35 `Swarm*` seat reports + 12 `deliver-*` + 2 `sources/*.md`; live gitignored `.ufo/waves/round-30/w1` `.md` = 47, all present in the capture, none live-only. `w1-spec.json` items = 35. `status_lines=35` = one STATUS line per seat report, 33 PASS + 2 PARTIAL.
- Lane state at the tip: worktree detached at `9dcd367`, `master` = `origin/master` = `9dcd367`; `git status --porcelain=v1 -uall` = ` M SKILL.md`, ` M corpus/QUALITY.md`, `?? corpus/lessons/round-30.md`; `git diff --stat` = SKILL.md +3, corpus/QUALITY.md +8. `.gitignore:1` is `.ufo/waves/`.

## Findings

1. **The landing gate evaluates the round-30 capture and is red, not COULD-NOT-EVALUATE.** Its docstring promises a fallback: "no .md reports in .ufo/waves/round-N/ or at its committed capture census/round-N/waves/" (`tools/souji-landing-gate.py:32`), and it used it. `carry_heading=0` because `corpus/lessons/round-30.md` is untracked at the tip (only `## Gate` is present in the draft, line 9).
2. **The complete uncarried set is two lines, both `STATUS: PARTIAL`, no `STATUS: FAIL`.** Exact bytes from the committed capture (fenced here, so this report adds no failure markers; the two quoted lines are still counted by `status_lines`, which a capture of this report would raise from 35 to 38 while `checked_markers` stays 2):

```
census/round-30/waves/w1/SwarmReviewer22.md line 7:
STATUS: PARTIAL — six of the seven audited checks verify clean against committed bytes and my own base re-runs; one ATTACK is filed: C1's accepted-correction rule is gameable via a `cmd=` substitute that never exercises the stated count (empirically reproduced on two rows, rc 0, `k1=0`). A stricter-only amendment is needed before data.

census/round-30/waves/w1/SwarmSimplifier35.md line 4:
STATUS: PARTIAL — the rendered plan is dispatchable and six of eight enumerated checks hold (distinct ids/prompts, allowed roles, flash and attack shares, unique deliver paths, scratch prefix, role mix), but two mandated rules fail at five sites: the absolute-path rule (shared context plus three items, one undefined placeholder) and the write-scope rule (two items name lane-relative write targets). Findings 1-5 are the violations; 6-10 are spec defects the L1 should reconcile; the non-violations list closes the remaining checks.
```

   The paste-ready `## Seat-reported failures` section carrying both paragraphs is in `deliver-pre-report-findings.md` §2 and `SwarmExecutor06-carry-section.md`; it is proven to clear the gate at scratch `fbdaa06` (findings 2 → 0).
3. **Committing the draft as written does not clear the gate.** The draft has no carry section; committed verbatim in scratch it still yields `findings=2 carry_heading=0` (receipt `-draft-only-gate.out`). The lesson must gain the section before the L1 report is filed.
4. **The pre-report gate is red at the tip for three separable reasons.** Usage `Usage: bash tools/souji-pre-report-gate.sh --lane ABS --branch NAME --report ABS --prereg ABS` (`tools/souji-pre-report-gate.sh:10`). `report`/`shonen`: the round's canonical target `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md` (named at `census/round-30/waves/w1/deliver-records-skeleton.md:83`, whose `deliver-records-skeleton.md:139` supplies the four `## SHONEN` `[~]` lines) does not exist. `clean`: the round's own uncommitted work (two tracked files, one untracked lesson). `tip` PASS and `prereg` PASS. Ordered fix: push, commit lesson + carry + SKILL/QUALITY edits, write the report with `## SHONEN`, rerun.
5. **`checked_reports=49` overcounts reports by two.** The gate counts the captured upstream snapshots `census/round-30/waves/w1/sources/cli-reference.md` and `sources/operation-log.md` as reports; the real count is 47 (35 seats + 12 deliveries, equal to the live `.ufo/waves/round-30/w1` `.md` count). The D1 contract literal is `checked_reports` = capture `.md` count, so this is not a contract violation, but 49 is not the seat count and an upstream document exposing a failure-vocabulary `STATUS` line would be forced into the carry set.
6. **Discovery precedence is a false-green hazard (reproduced).** Any committed `.md` under `.ufo/waves/round-30/` suppresses the capture fallback: one force-added `Note.md` on the draft-only state returns rc 0 with `findings=0 checked_markers=0 status_lines=0 checked_reports=1` while both failures remain uncarried (`-variant-partial-forceadd.out`). The round must not force-add into `.ufo/waves/round-30/`; capture wave 2 under `census/round-30/waves/w2/`.
7. **The r29 carry fix reproduces as a control.** `--round 29` at the same tip: findings 0, `checked_markers=7`, `carry_heading=1`, `checked_reports=86`, rc 0. The tool can read committed captures; round 30's red is round-30 state, not a regression.

## Attack log

| Attacked | Verdict |
|---|---|
| Landing gate discovery over the round-30 capture at the tip | HOLDS (evaluates 49 `.md`, no COULD-NOT-EVALUATE, no dangling pointer) |
| Carry test: whole-paragraph quote of both single-line STATUS paragraphs | HOLDS (findings 2 → 0; `carry_heading=1`) |
| Carry test: mid-line ` ...` truncation of the long line | HOLDS (rejected, findings=1) |
| Carry test: entries without the `open` token | HOLDS (rejected, findings=2) |
| Draft lesson committed verbatim | BROKEN as a readiness property (round would land red) |
| Discovery precedence with one force-added `.ufo/waves/round-30/*.md` | BROKEN (false green, findings=0, rc 0; reproduced) |
| `checked_reports` as a seat count | DEFECT-NOT-FATAL (49 = 47 reports + 2 captured upstream snapshots) |
| Pre-report gate tool wiring (clean clone, `## SHONEN` report) | HOLDS (5/5 PASS, rc 0) |
| Pre-report gate at the lane tip with the canonical report target | BROKEN as readiness (3/5 FAIL: report, shonen, clean) |
| Pre-report gate applied to a seat report | DEFECT-NOT-FATAL (seat reports carry no `## SHONEN`; `check-shonen=FAIL` by design — this gate is the L1 report's) |
| Round-29 replay at the tip | HOLDS (findings=0, carry_heading=1) |

No frozen predicate, target, counter or kill rule was touched, proposed or reinterpreted; every claim above is a measured run or a labelled inference. No tool was installed or updated.

## Deliveries

- `.ufo/waves/round-30/w2/deliver-pre-report-findings.md` — readiness answer, the exact paste-ready carry section, four carry-contract probes, five instrument findings.
- Receipts in `.ufo/waves/round-30/w2/`: `SwarmExecutor06-landing-gate-tip.out`, `SwarmExecutor06-landing-gate-tip.json`, `SwarmExecutor06-landing-gate-round29.out`, `SwarmExecutor06-draft-only-gate.out`, `SwarmExecutor06-carry-full-gate.out`, `SwarmExecutor06-variant-midline-ellipsis.out`, `SwarmExecutor06-variant-no-open-token.out`, `SwarmExecutor06-variant-partial-forceadd.out`, `SwarmExecutor06-prereport-scratch-clean.out`, `SwarmExecutor06-prereport-lane-canonical.out`, `SwarmExecutor06-prereport-lane-seat-report.out`, `SwarmExecutor06-carry-section.md`, `SwarmExecutor06-capture-composition.txt`.
- Scratch `/fast/scratch/hyaku/souji-r30/PreReportGate/` removed after the receipt copy.
