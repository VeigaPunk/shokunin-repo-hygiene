# ExecLessonScaffold — round-27 lesson skeleton DRAFT

## Status

STATUS: PASS — drafted `round-27.md` skeleton with all required sections; R27-M1 grounded at `watchdog.log:1377`; no fabricated evidence; no lane mutation beyond the two w1 files.

## Evidence

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt` (read first; frozen claims/counters, lane base e78ac7c, attempt 1 died with no lane writes).
- `read /home/vgpnk/Projects/shokunin/.ufo/watchdog.log:1365-1395`:
  line 1377 `2026-10-25T14:46:45-03:00 lane-dead-no-report souji round=27; retry same round (hyaku-inline attempt=1: L1 misread inline-spawn handoff (expected orchestrator to supply claims/ready), declared blocked, refused resume; no lane writes)`; line 1378 attempt=2 launch.
- `read souji-shokunin/corpus/lessons/round-26.md` (sections: Gate / Findings / Residuals / Receipts / Mistakes table; R26-M1 row style reused for R27-M1).
- `read souji-shokunin/.ufo/waves/round-27/w1-spec.json` (reportDir `.ufo/waves/round-27/w1`).

## Findings

1. Wrote `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/round-27.md` (draft, 2640 bytes) with `## Gate` (candidates/admitted/rejected/spot-check placeholders), `## Findings`, `## Residuals`, `## Receipts`, `## Mistakes` (R27-M1 row ready), `## Seat-reported failures` (empty template).
2. R27-M1 row: class=landing; captured-by none; fix = C3 pre-report gate incl. `prereg`/handoff readiness check + prompt states L1 writes the ready file; evidence quote `watchdog.log:1377` (15 words, verbatim from bytes opened this run).
3. No prior `round-27.md` existed in `corpus/lessons/` or `w1/` (observed via glob); L1 installs the draft as `corpus/lessons/round-27.md`.
4. Tooling: none installed/updated (no tool needed; RULES.md not consulted for any install).

## Attack log

None — this seat is not an attack item; no counter/predicate contested. [INFERENCE] none.
