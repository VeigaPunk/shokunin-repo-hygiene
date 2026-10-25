# Round 27 — honest stop with F4 assimilation and pre-report gate

## Gate

Round 27 re-opened two GLib 2.84.0 source files (accessed 2026-10-25; byte pins in `census/round-27/sources/SHA256SUMS`).

- ADMIT: S152 / `gio/glocalfile.c` — `trashname = get_unique_filename (basename, i++);` (line 2256; snapshot `census/round-27/sources/glocalfile.c`): supports the writer's unique-name retry.
- ADMIT: S210 / `gio/glocalfile.c` — `O_EXCL` (line 2261; same snapshot): supports exclusive reservation of the info-file name.
- ADMIT: S211 / `glib/gfileutils.c` — `if (g_rename (old_name, new_name) == -1)` (line 1041; snapshot `census/round-27/sources/gfileutils.c`): supports publication by rename.
- REJECT: staged S119 zh-Hans git-fetch edition: decision-time version state cannot be reconstructed without a pinned snapshot; flip only when a decision-time snapshot and located quote are available.

The writer and mechanism entries each carry their own URL, opened date, located ≤25-word quotes, snapshot paths, and an ADMIT/REJECT decision. The two entries are admitted on F4 implementation ground only; the normative format remains the held S022 specification.

Quarantine slice: 8 rows re-opened (S114, S118, S123, S124, S126, S131, S133, S138); seven accepted with evidence and S118 unverifiable because the registered DOI payload remains unavailable and venue metadata conflicts. Full per-row decisions: `census/round-27/records/slice-verdicts.tsv`.

## Findings

- C1 calibration failed: landing-gate findings remained 2 at base and tip; the two tokens are parser overmatches but the S118 composite site also points at a stale class. No exemption was committed because it could mask a real citation defect. The result is an honest stop, not a narrowed target.
- C2 coverage passed its frozen counters at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`: SOURCES rows 132→135; grounded F4 entries 2→4; gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; sources census rc 0. Collision proof and its 24-row alias/reject/quarantine mapping are in `census/round-27/assimilation/`.
- C3 operability passed at the same candidate: pre-report gate installed; isolated fixture `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, rc 0. It checks remote branch equality, report presence, one SHONEN heading, clean worktree, and a required preregistration.
- The r26 routed S-language pin defect was not fixed by this round: S119 remained rejected; a future re-adoption needs a decision-time pinned snapshot and sha256.
- Attempt 1 ended with `lane-dead-no-report` (fleet watchdog line 1377); attempt 2 used the ready-file handoff. `considerthese/` is absent.

## Residuals

- C1 requires a truthful correction to Q57's composite site / stale class; do not suppress that defect with an exemption.
- No claim of overall admission: C1 failed, so the canonical all-claims admission condition is unmet.
- `.ufo/` wave runtime artifacts are not committable through `jj-lane.sh`; durable receipts and the dispatch results remain under `.ufo/waves/round-27/` for the round record, while committed evidence is in `census/round-27/`.
- 36 inherited r26 W1 files remain under `.ufo/waves/round-26/w1/`; the helper refuses `.ufo` paths. They were catalogued by `ExecInheritedResolve.md` and left untouched rather than bypassing the lane helper.

## Receipts

- C1 before/after: `census/round-27/records/c1-before.tsv`, `c1-after.tsv`.
- C2 after: `census/round-27/records/c2-after.tsv`; registry validation output `sources-census-after.out`.
- C3 after: `census/round-27/records/c3-after.tsv`.
- Frozen preregistration copy: `census/round-27/records/preregistration.txt`; machine instrument `python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`.
- Wave: one v2 wave, 79 seats (25 executor, 12 reviewer, 11 scout, 10 critic, 8 scribe, 6 mutation-tester, 3 connector, 3 simplifier, 1 revenger); no dead seats reported in `w1-results.json`. L1 performed the planner seat. Wave results and full reports remain under `.ufo/waves/round-27/`.

## Mistakes

- R26-M1 (class=landing; evidence `corpus/lessons/round-26-verifier-spotcheck.md:13`; captured-by: none; fix: `tools/souji-pre-report-gate.sh` clean-worktree check). The dirty-tree selftest case returns nonzero with `check-clean=FAIL`, showing the fix can fail on the routed leftover class.
