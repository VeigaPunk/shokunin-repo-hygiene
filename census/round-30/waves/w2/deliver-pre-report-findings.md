# Round-end readiness attack — pre-report gate + landing gate at `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`

Seat SwarmExecutor06 (r30 w2, item PreReportGate). Read-only; scratch `/fast/scratch/hyaku/souji-r30/PreReportGate/` (removed after the receipts below were copied here). Nothing in the lane repo was written.

## 1. Landing gate at the tip — it evaluates the capture, and it is red

Command (as specified):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9dcd367655fc28ba73d679a0e2cadaff96d2bcb8 --round 30 --fleet-root /home/vgpnk/Projects/shokunin
```

Not `COULD-NOT-EVALUATE`: the tool read the committed capture at `census/round-30/waves/`. Exit 1, one line per finding:

```
LG-SEAT-UNCARRIED	census/round-30/waves/w1/SwarmReviewer22.md	line 7: STATUS: PARTIAL — six of the seven audited checks verify clean against committed bytes and my own base re-runs; one ATTACK is filed: C1's accepted-correction rule is gameable via a cmd= substitute that never exercises th
LG-SEAT-UNCARRIED	census/round-30/waves/w1/SwarmSimplifier35.md	line 4: STATUS: PARTIAL — the rendered plan is dispatchable and six of eight enumerated checks hold (distinct ids/prompts, allowed roles, flash and attack shares, unique deliver paths, scratch prefix, role mix), but two mandated
SUMMARY	findings=2	checked_reg=59	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=2	status_lines=35	carry_heading=0	checked_reports=49
```

JSON summary at the same revision: `checked_ptrs=978 ptr_exempt=4 ptr_fleet=3` and only the two findings above, i.e. no dangling pointer at the tip.

Reading of the counts: `checked_markers=2` is the complete failure-channel set. `status_lines=35` is every `STATUS` channel line in the 49 captured `.md` files; the other 33 are `STATUS: PASS`, so exactly two lines need a carry. `carry_heading=0` because `corpus/lessons/round-30.md` is untracked at the tip (the committed lesson has no `## Seat-reported failures` heading; the draft has only `## Gate`). There is no wave-1 `STATUS: FAIL`; both uncarried lines are `PARTIAL`.

Enumerated set check: the capture holds 49 `.md` = 35 wave-1 seat reports (`Swarm*`) + 12 deliveries (`deliver-*`) + 2 upstream snapshots (`sources/cli-reference.md`, `sources/operation-log.md`). The live gitignored `.ufo/waves/round-30/w1/` holds 47 `.md`, all of which are in the capture; no report exists only in the live directory. So the carry set below is complete, but see §5 item 5 for the count inflation.

## 2. Exact carry entries the round-30 lesson needs

Append this section to `corpus/lessons/round-30.md` and commit it; the gate reads committed bytes only. Both bullets are single physical lines: the whole STATUS paragraph must be quoted (a mid-line cut is rejected by `carries()`; see §3).

```markdown
## Seat-reported failures

Appended in round 30 wave 2: the round-30 landing gate reads the committed wave capture at
`census/round-30/waves/`, so these two seat-reported failure lines are carried here before the
round closes. Each entry quotes that report's STATUS paragraph verbatim (bytes as committed at lane tip
`9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`) and marks it open: no `resolved@` receipt exists for either
in `corpus/lessons/round-30.md` or `census/round-30/records/`.

- `census/round-30/waves/w1/SwarmReviewer22.md` line 7 — open: STATUS: PARTIAL — six of the seven audited checks verify clean against committed bytes and my own base re-runs; one ATTACK is filed: C1's accepted-correction rule is gameable via a `cmd=` substitute that never exercises the stated count (empirically reproduced on two rows, rc 0, `k1=0`). A stricter-only amendment is needed before data.

- `census/round-30/waves/w1/SwarmSimplifier35.md` line 4 — open: STATUS: PARTIAL — the rendered plan is dispatchable and six of eight enumerated checks hold (distinct ids/prompts, allowed roles, flash and attack shares, unique deliver paths, scratch prefix, role mix), but two mandated rules fail at five sites: the absolute-path rule (shared context plus three items, one undefined placeholder) and the write-scope rule (two items name lane-relative write targets). Findings 1-5 are the violations; 6-10 are spec defects the L1 should reconcile; the non-violations list closes the remaining checks.
```

The two quoted paragraphs are byte-identical to the report bytes at `9dcd367` (the only additions are the path prefix, `line N`, and the `open:` marker the carry contract requires). The same text, as a standalone file, is the receipt `SwarmExecutor06-carry-section.md`.

## 3. Proof that this clears the gate, and the three shapes that do not

All runs are on a private `--no-local` clone with `origin` removed (`/fast/scratch/hyaku/souji-r30/PreReportGate/c`), lesson committed in scratch only; the gate was given `--root` at that clone.

| Provenance | Lesson state | Gate verdict | Receipt |
|---|---|---|---|
| scratch `2b331e0f1b36c6ae5d771657e29d96ccaea61a8f` | the current draft committed verbatim | `findings=2 ... carry_heading=0 ... checked_reports=49`, rc 1 | `SwarmExecutor06-draft-only-gate.out` |
| scratch `fbdaa062293326784ed23d0ea1e31114d6e90050` | draft + the section in §2 | `findings=0 ... carry_heading=1 ... checked_reports=49`, rc 0 | `SwarmExecutor06-carry-full-gate.out` |
| scratch `580ccafd524cdd9bc5548a9c37cf9360194d4be0` | Reviewer22 quote cut mid-line with ` ...` | `findings=1` (Reviewer22 uncarried), rc 1 | `SwarmExecutor06-variant-midline-ellipsis.out` |
| scratch `4c634461f54c6969ba4af7235d9254c0de47abba` | both entries without the word `open` | `findings=2`, rc 1 | `SwarmExecutor06-variant-no-open-token.out` |

So: committing the draft as it stands leaves round 30 red; the shipped section turns it green; shortening the long Reviewer22 line is not allowed; dropping `open` re-opens both findings.

## 4. Pre-report gate at the tip — the round is not report-ready

Usage read from `tools/souji-pre-report-gate.sh:10`; five checks, exit 1 on any FAIL. Run against the lane (read-only; the tool only runs `git ls-remote`, `rev-parse`, `status`, `grep`), with the round's canonical report target from the wave-1 skeleton (`census/round-30/waves/w1/deliver-records-skeleton.md:83` names `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md`):

```
$ bash tools/souji-pre-report-gate.sh --lane /home/vgpnk/Projects/shokunin/souji-shokunin --branch master \
    --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md \
    --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt
check-tip=PASS
check-report=FAIL
check-shonen=FAIL
detail-shonen: found 0 headings, expected 1
check-clean=FAIL
detail-clean:  M SKILL.md
 M corpus/QUALITY.md
?? corpus/lessons/round-30.md
check-prereg=PASS
rc=1
```

- `tip` PASS: `refs/heads/master` = `origin/master` = `9dcd367` (the worktree itself is on a detached HEAD at the same commit).
- `report` FAIL: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md` does not exist (that directory holds other lanes' reports from Oct 22-25).
- `shonen` FAIL: no report, hence no `## SHONEN`. The skeleton at `deliver-records-skeleton.md:139` supplies the four `[~]` lines to fill.
- `clean` FAIL: the round's own uncommitted work — `SKILL.md` (+3 lines), `corpus/QUALITY.md` (+8 lines), and the untracked lesson draft. `.ufo/waves/` is gitignored (`.gitignore:1`), so the wave reports themselves do not dirty the tree.
- `prereg` PASS.

Tool wiring control (same tool, clean tree): a fresh clone of a bare mirror of the lane at `9dcd367` with a report containing one `## SHONEN` heading returns `check-tip=PASS check-report=PASS check-shonen=PASS check-clean=PASS check-prereg=PASS`, rc 0 (`SwarmExecutor06-prereport-scratch-clean.out`). The tool is not broken; the round state is. A seat report is not a valid target: `census/round-30/waves/w1/SwarmReviewer22.md` gives `check-report=PASS check-shonen=FAIL` (no `## SHONEN` in any seat report; 34 of 35 have none) — the gate is the L1 report's gate.

Ordering the L1 must respect: push (`tip`), commit the lesson incl. §2 and the SKILL/QUALITY edits (`clean`), write the report with `## SHONEN` (`report`, `shonen`), then run the gate.

## 5. Readiness findings on the instruments

1. **Count inflation.** `checked_reports=49` counts the two upstream snapshots captured under `census/round-30/waves/w1/sources/` as seat reports. The real report count is 47 (35 seats + 12 deliveries, equal to the live `.ufo/waves/round-30/w1/` `.md` count). The frozen D1 fixture contract ("`checked_reports` equals the `.md` count") is met, so this is not a contract violation, but 49 must not be cited as the seat count, and a captured upstream document containing a line that opens `STATUS: <failure word>` would be forced into the carry set.
2. **Discovery precedence is a false-green hazard (reproduced).** Discovery reads `.ufo/waves/round-N/**.md` when any such file is committed, and only falls back to the capture when none is. One force-added file is enough to hide the whole capture: on top of the draft-only state, `git add -f .ufo/waves/round-30/w2/Note.md` + commit (`00796bfd6d98518c8a15eb886a906672f838b2fb`) yields `SUMMARY findings=0 ... checked_markers=0 status_lines=0 carry_heading=0 checked_reports=1`, rc 0 — green with both failures still uncarried (`SwarmExecutor06-variant-partial-forceadd.out`). Do not force-add anything under `.ufo/waves/round-30/`; capture wave 2 to `census/round-30/waves/w2/`.
3. **The r29 fix reproduces as a control.** Same tool, `--round 29` at the tip: `SUMMARY findings=0 ... checked_markers=7 status_lines=69 carry_heading=1 checked_reports=86`, rc 0 (`SwarmExecutor06-landing-gate-round29.out`). The seven r29 failure lines are carried, so the gate is able to read committed captures; the round-30 red is round-30 work, not a tool regression.
4. **Detached worktree.** The lane worktree is on a detached HEAD at `9dcd367` while `master` also points there; the gate's `tip` check passes, but any `git status`/commit the L1 does should be made on `master` deliberately.
