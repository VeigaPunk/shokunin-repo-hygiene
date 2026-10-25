# W1 file-scope audit

STATUS: PARTIAL

Axes: calibration (7, lowest), operability (8), coverage (8).

Evidence: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` and `git -C /home/vgpnk/Projects/shokunin status --porcelain --untracked-files=all`, captured 2026-10-25. W1 artifacts are present under lane `.ufo/waves/round-25/w1/`; W2 list at inspection contained `RevC2RedArm.md`, `ScoutC1Receipts.md`, `ScoutD4Marker.md`, `ScoutFrontierClaim.md`, plus assignments/registry. The two directories are item-specific report directories; no duplicate seat report was proven from the bounded listing.

## Per-path disposition

Lane status entries consistent with intended round work: `SCORECARD.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/round-24.md`, `tools/souji-coverage-agreement.py`, `tools/souji-record-agreement.py`, `tests/fixtures/r13-repo-structure.sh`, `tests/fixtures/r23-record-agreement.py`, `tests/fixtures/r24-size-census.py`, `tests/fixtures/r25-coverage-agreement.py`, `corpus/knowledge/git-repo-structure-common-dir.md`, `.ufo/waves/round-25/w1-dispatch.json`, `w1-spec.json`, `w1/`, `w2-dispatch.json`, `w2-spec.json`, `w2/`, and `census/round-25/sources/`. The fixed claim and routed-fix scope supports these paths, although status alone does not establish authorship.

Potential scope exception: `tests/fixtures/r25-q57-check.sh` and `tests/fixtures/r25-slice-mapping.py` are untracked; their linkage to frozen claim work is not evidenced by preregistration text reviewed here. Disposition: flag for L1 attribution review, not classify as unauthorized.

`census/operator-sweep-20261019/` is untracked but explicitly excluded from inspection by assignment. No contents inspected; disposition unknown, do not touch.

Fleet-root status includes `.ufo/l0-questions.md`, `.ufo/reports/round-25/tabi.md`, multiple `.ufo/state/*` baselines, `.ufo/watchdog.log`, `scripts/hyaku/closure-prompt.md`, `scripts/hyaku/hyaku.env`, `scripts/hyaku/lane-addendum.md`, `.omp/mcp.json`, `.scratch/goal-20261025-hyaku-12h.md`, `.ufo/waves/round-24/w2/RevUnlandedResolution.md`, and `m-rev-vs-rev.py`. They are not shown as round-25 souji seat writes; status cannot establish authorship. Per boundary, no fleet files or excluded `.scratch/`/operator-sweep contents were opened or changed. Fleet-root writes by souji seats: none substantiated by available status evidence.

## Findings

1. **PARTIAL — scope attribution gap.** Two untracked fixture paths are not named in the frozen claim file list reviewed (`r25-q57-check.sh`, `r25-slice-mapping.py`); provenance remains unverified.
2. **No demonstrated duplicate reports.** W1 and W2 report directories contain distinct named artifacts in the visible listing; no same-seat duplicate identified.
3. **No demonstrated fleet misroot.** Fleet status is mixed-owner and includes unrelated lane/operator files. No candidate was attributed to a souji seat, and no fleet path was modified.

Attack log: compared complete lane porcelain status to fleet porcelain status with all untracked file names; inspected W1/W2 directory listings and wave file names. Did not inspect prohibited paths/contents. No deletion or movement performed.
