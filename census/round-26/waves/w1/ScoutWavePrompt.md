# ScoutWavePrompt — round-26 w1 wave shape: role → deliverable matrix

## Status

STATUS: PASS — all 87 items parsed; 87/87 report paths unique, 30/30 delivery-file paths unique (no two seats share a delivery path); **no item asks a seat to make a production edit** (every production-target file is a w1/ draft the L1 copies); the real defects are *content-level* overlaps on the same landing target (SCORECARD.md ×3, LOG.md ×2, corpus/lessons/round-26.md ×3, the round report ×2–3) and three prompt-level path bugs.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `166baa18f808071bc385187691713044a26bd36e` (worktree had `SCORECARD.md` and `corpus/lessons/round-26.md` modified at scan time; `git status --porcelain` shows 6 untracked `__pycache__` dirs — `tools/`, `tests/fixtures/` — from seats that ran lane Python without `-B`).

Spec parse (read-only, `python3 -B`):

```
$ python3 -B -c "import json;d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1-spec.json'));print(len(d['items']))"
87
roles: executor 31, reviewer 15, scribe 11, scout 10, critic 9, mutation-tester 6,
       connector 2, simplifier 2, sentinel 1
report paths unique: 87/87 (no duplicates)
delivery-file basenames unique: 30/30 (no duplicates)
```

Spec-derived delivery map (27 seats write a named deliverable; 60 are report-only):

| seat | role | deliverable (w1/, relative to lane) | L1 lands it as |
|---|---|---|---|
| ExecAxisTool | executor | `souji-axis-check.py` | `tools/souji-axis-check.py` |
| ExecAxisFixture | executor | `r26-axis-check.py` | `tests/fixtures/r26-axis-check.py` |
| ExecAxisSelftest | executor | `souji-axis-check-selftest.md` | prose spec only (no tool change) |
| ExecScratchMirror | executor | `mirror-build.py` | L1-run scratch mirror builder |
| ExecRenumberMap | executor | `renumber-map.md` | input to ScribeSourceRows |
| ExecC1Surgery | executor | `c1-scaffold-extract.md`, `c1-new-scorecard-head.md`, `c1-line-map.md` | SCORECARD.md payload |
| ExecC1Verify | executor | `c1-verify.md` | evidence only |
| ExecSh256Sums | executor | `sha256sums-recipe.md` | recipe for `census/round-26/sources/SHA256SUMS` |
| ExecLandingCheck | executor | `landing-check.md` | recipe only |
| ExecVerifyLoop | executor | `verify-loop.sh` | L1-run post-integration loop |
| ExecCensusAfter | executor | `census-after-recipe.md` | report census-after block |
| ExecCensusTables | executor | `census-delta.md` | report census delta block |
| ExecResultsCount | executor | `results-count.py` | seat-count reporter |
| ExecReportAssemble | executor | `report-assemble.py`, `report-rendered.md` | `.ufo/reports/round-26/souji.md` draft |
| ExecShonenFile | executor | `shonen-lines.md` | report SHONEN section |
| ScribeAxisDocs | scribe | `axis-check-docs.md` | QUALITY.md Q59 row + SKILL.md gate rows |
| ScribeEntryA | scribe | `entry-git-auto-maintenance-trigger-set.md` | `corpus/knowledge/git-auto-maintenance-trigger-set.md` |
| ScribeEntryB | scribe | `entry-git-auto-maintenance-trigger-set-r23.md` | `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md` |
| ScribeSourceRows | scribe | `sources-append-block.md` | `corpus/SOURCES.md` rows S128–S132 |
| ScribeGateDraft | scribe | `gate-draft.md` | lesson `## Gate` section |
| ScribeC1Note | scribe | `c1-append-note.md` | SCORECARD append-only note **+ LOG.md Round 26 block** |
| ScribeScorecardR26 | scribe | `scorecard-r26.md` | SCORECARD Round 26 table + capability row + planned-roll |
| ScribeLogR26 | scribe | `log-r26.md` | LOG.md Round 26 block |
| ScribeLessonR26 | scribe | `lesson-r26.md` | `corpus/lessons/round-26.md` |
| ScribeQ58Note | scribe | `q58-note.md` | LOG.md + lesson Q58-catch text |
| ScribeReportDraft | scribe | `report-draft.md` | report skeleton |
| DistilFindings | scout | `distill-findings.md` | dedup roll-up |

Report-only (60 seats, no deliverable file): all 15 reviewers, all 9 critics, all 6 mutation-testers, both connectors, both simplifiers, the sentinel, 16 executors that are Lab*/Sonic* read-only probes, and 9 of 10 scouts. Every seat writes exactly one report at `.ufo/waves/round-26/w1/<Seat>.md`; no report path collides with any delivery path.

Reports actually present at scan time: 81/87. Missing: `ScoutStagedEntries`, `ScoutF1Gap`, `ScoutAssimRegister`, `DistilFindings`, `ScoutShonen`, `ScoutWavePrompt` (this file). `DistilFindings`' delivery `distill-findings.md` is also absent — the late-wave dedup seat has not run.

Round-26 furniture landed so far: `corpus/QUALITY.md:143` (Q59 row, from ScribeAxisDocs), `tools/souji-axis-check.py`, `tests/fixtures/r26-axis-check.py`, both knowledge entries, `corpus/SOURCES.md` rows S128–S132, `census/round-26/sources/` (7 snapshots + SHA256SUMS), `census/round-26/records/` (8 receipts incl. `c2-k4-base.tsv`), `corpus/lessons/round-26.md`. **Not landed:** `SKILL.md` gate-registry rows for `souji-axis-check` / `r26-axis-check` (`grep -c` = 0), the `prereg axis-check (r26)` capability row, and the `### Round 26 planned-roll` block.

Live checks run read-only this run:

```
$ python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0        rc=0
$ python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py
cases=12 pass=12 control=FALSE-GREEN-REJECTED   rc=0
$ python3 -B tools/souji-gate-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --round-date 2026-10-25 \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources --slice census/round-26/records/empty-slice --slice-verdicts census/round-26/records/empty-verdicts
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0   rc=0
```

Scratch used: `/var/tmp/souji-r26-ScoutWavePrompt/` (removed before finish). No lane write other than this report. No git/jj mutation, no signals, nothing read from `census/operator-sweep-20261019/` or `.scratch/`.

## Findings

1. **No overlapping delivery paths, no production-edit prompts.** All 30 deliverable basenames are unique and all 87 report paths are unique. Every production-target file is produced as a `w1/` draft with explicit L1-copies wording — spec `w1-spec.json:10` reads "the L1 copies it to `tools/souji-axis-check.py`", `:15` "the L1 copies it to `tests/fixtures/r26-axis-check.py`", `:55` "the L1 copies it to `corpus/knowledge/git-auto-maintenance-trigger-set.md`", and `:75` "Produce the C1 SCORECARD integration as DRAFT FILES (the L1 applies it)". ScribeAxisDocs and ScribeLessonR26 likewise draft *text for* `corpus/QUALITY.md` / `SKILL.md` / `corpus/lessons/round-26.md` rather than editing them. The integrator-only discipline holds as specified.

2. **Content-level overlap (same landing target, different w1 files) — SCORECARD.md, three seats.** ExecC1Surgery (`c1-new-scorecard-head.md`, `c1-line-map.md`), ScribeC1Note (`c1-append-note.md`) and ScribeScorecardR26 (`scorecard-r26.md`) all author SCORECARD.md content. `scorecard-r26.md:36` asks for "## 2. Insertion — capability row" inside `## Capabilities`, while `c1-new-scorecard-head.md` reproduces the whole `## Capabilities` and `## Planned` sections as base spans. Landing both naively risks a duplicated capabilities section or a `## Planned` span diff that trips C1's amendment-2 protected-span rule.

3. **Content-level overlap — LOG.md Round 26 block, two seats.** ScribeLogR26 drafts "the full" / "LOG.md Round26 block (mirroring the Round25 block's shape)" (`w1-spec.json:185`) and ScribeC1Note also drafts a "## 2. LOG.md Round 26 block" (`c1-append-note.md:42`) plus "the LOG.md + lesson text recording the Q58 catch (amendment 1)" (ScribeQ58Note, `w1-spec.json:430`). Three seats, one target file, one section. Observed state: `grep -c "Round 26" LOG.md` = 0 — the block is not landed yet, so the L1 must merge three drafts into one section rather than appending them.

4. **Content-level overlap — `corpus/lessons/round-26.md`, three seats.** ScribeLessonR26 drafts the whole file ("corpus/lessons/round-26.md skeleton in the r25 lesson's exact shape", `w1-spec.json:190`), ScribeGateDraft the `## Gate` section ("Keep the exact `## Gate` shape of", `w1-spec.json:70`), ScribeQ58Note the lesson text. The landed file (`corpus/lessons/round-26.md`, 5874 B) is much shorter than the draft (14261 B) and carries 1 "ADMIT" line where the gate draft carries 6 — the merged lesson already differs materially from the drafted lesson.

5. **Content-level overlap — the round report, two producers plus a section.** ScribeReportDraft (`report-draft.md`, 23932 B skeleton) and ExecReportAssemble (`report-assemble.py` → `report-rendered.md`, 15433 B) both produce the report body; ExecShonenFile (`shonen-lines.md`) produces a third overlapping artifact (the SHONEN section). `report-assemble.py` does **not** read `report-draft.md` (grep for `report-draft` in the script: no hit), so the two producers are independent rather than sequential — the L1 must pick one as the base.

6. **Content-level overlap — the census before/after table, two seats.** ExecCensusAfter (`census-after-recipe.md`) and ExecCensusTables (`census-delta.md`) both author the report's before→after census block; `census-delta.md` already records the after-state at `0c92c2e` while `census-after-recipe.md` records a different tip (`c594901`), so the two recipes disagree on the measured tip.

7. **Delivery-vs-landing divergence: the wave's C3 tool draft is NOT the landed tool.** `w1/souji-axis-check.py` (8288 B, sha256 `0805afff…`) differs byte-wise from the landed `tools/souji-axis-check.py` (sha256 `1d1c7f5a…` at HEAD, `14bc9632…` at `0833de9`). Reproduced this run against the wave fixture (byte-identical to the landed fixture): the wave tool draft scores `cases=12 pass=6` (cases 3, 6, 8, 9, 10 each gain a spurious R3 flag) while the landed tool + landed fixture score `cases=12 pass=12 control=FALSE-GREEN-REJECTED`. So the L1 did not copy ExecAxisTool's deliverable; the C3 deliverable named in the item was superseded by an L1-authored tool. The wave record should say which bytes are authoritative. (The landed instrument is the one that satisfies the frozen K2, so this is a bookkeeping gap, not a claim defect.)

8. **Delivery-vs-landing divergence: both knowledge entries.** `w1/entry-git-auto-maintenance-trigger-set.md` (9784 B) vs landed `corpus/knowledge/git-auto-maintenance-trigger-set.md` (4945 B); `-r23` draft 7966 B vs landed 6876 B. The landed entry A carries 2 `snapshot:` tokens where the draft carries 6; both landed entries still pass K2 (`entries=2 ok=2 fail=0`).

9. **Prompt-level path bugs (3 items) that break under the fleet-root cwd.** LabReceiptVerify's assigned command is `python3 -B tools/souji-receipt-run.py verify --root . --rev …`: `tools/` does not exist at the fleet root (`/home/vgpnk/Projects/shokunin/tools` → No such file or directory) and `--root .` resolves to the fleet, not the lane. That seat reported the deeper defect itself: `verify` accepts only `--root` plus a positional receipt and no `--rev`, so the assigned invocation exits 2 with "unrecognized arguments". LabC1AfterSim's `bash census/round-26/c1-counter.sh` is likewise relative. Contrast ExecVerifyLoop, which pins `LANE=/home/vgpnk/Projects/shokunin/souji-shokunin` and `cd "$LANE"` first — the correct pattern the other two prompts should have used.

10. **The prereg's scratch-mirror path was not used.** The frozen C2 SCRATCH MIRROR GATE names ".ufo/waves/round-26/assimilation/validate/, then" (`preregistration.txt:126`); that directory does not exist. The mirror that exists is `/var/tmp/souji-r26-mirror/` (created 14:22:15, `validate.out` last line `file ok …/corpus/SOURCES.md`), and `ExecScratchMirror`'s script defaults to that same `/var/tmp` path. The gate ordering itself is satisfied (mirror built 14:22, `corpus/SOURCES.md` append committed in `0833de9` at 14:27:56), but the lane-repo mirror path named by the prereg was skipped. Observation, not a kill-rule failure — the frozen counters do not name the path.

11. **Two scribe deliverables remain unlanded after the wave's other drafts landed.** `SKILL.md` carries no `souji-axis-check` / `r26-axis-check` gate-registry rows (grep count 0), and SCORECARD.md has no `prereg axis-check (r26)` capability row and no `### Round 26 planned-roll` block — although `scorecard-r26.md` supplies both. `corpus/QUALITY.md:143` (Q59) *was* landed, so only part of ScribeAxisDocs' deliverable reached the lane.

12. **Six seat reports and one delivery file are absent at scan time** (`ScoutStagedEntries`, `ScoutF1Gap`, `ScoutAssimRegister`, `DistilFindings`, `ScoutShonen`, plus this file; `distill-findings.md` also missing). DistilFindings is the wave's late-wave dedup seat and its own prompt requires ≥10 completed reports before it runs — 81 exist, so it should run and its missing output is the one that blocks the L1's roll-up.

13. **Six untracked `__pycache__` directories** (`tools/__pycache__/`, `tests/fixtures/__pycache__/`, plus 4 others) are sitting in the lane worktree, artifacts of seats running lane Python without `-B`. They are untracked and inside the lane repo, so no bound was crossed, but they are workspace debris a hygiene lane should not leave behind — the L1 should not commit them.

14. **Role mix corroborates SonicSpecCount.** Routable share 44/87 = 50.57% (bar ≥50%, met by one seat), attack share 30/87 = 34.48% (bar ≥25%). Independently recomputed from `role` fields; matches that seat's numbers.

## Attack log

Not an attack item — no counter, predicate, target or case set is proposed for change. Findings 2–6 and 11 are integration-ordering observations for the L1 (which draft wins where several seats author one target), not counter amendments; the frozen counters themselves were re-run read-only and hold: C1 `markers=0`, headings ordered 17/44/78; C2 K2 `entries=2 ok=2 fail=0`; C3 `claims=3 flags=0`, fixture `cases=12 pass=12 control=FALSE-GREEN-REJECTED`.

## Tools

None installed or upgraded this run; no `pacman` transaction (host-wide pacman guard respected).
