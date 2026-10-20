STATUS: DONE — Q10 review found one calibration evidence gap; the other scoped checks hold.

# Attacked claim

Q10 on `SCORECARD.md` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`: every measured number in the r18 axis and capability rows is traceable to a committed record or lesson measurement; `## Planned` names r19; scores are unchanged with `numeric delta 0, legacy-unmapped`.

## Findings (by severity)

### MEDIUM — The final C2 gate result and `53/0` selftest outcome are not evidenced at the round tip

`SCORECARD.md:14` states “after: 0 at the round tip” and `SCORECARD.md:53` claims the landing-gate selftest is `53/0`. The corresponding lesson does not preserve either final result: `corpus/lessons/round-18.md:7` says to run the same command at the round tip and points to “Gate”; `:27` only records a candidate-admit judgment and limitations, with no command output or finding count. It does record the selftest count transition `33 → 53` and the external fixture `11/0` at `:7`, but not the final selftest failure count or return code.

The committed gate JSON is explicitly the **before** measurement: `census/round-18/gate-pointers-before-b576341.json` has `resolved_rev=b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, `exit=2`, and `summary.findings=10`. `census/round-18/gate-replays-r18.json` contains only the historical replay keys `r13-admitted`, `r14-landing`, `r15-landing`, `r16-landing`, and `r16-precarry`; it is not a round-tip result. The committed round-18 census/lesson listing has no post-fix gate-result record. Thus the scorecard’s post-fix `0` and capability `53/0` lack a committed measurement at the claimed revision. The early W1 `GatePointers.md` report is not a substitute: it records an earlier patch run (`51/0` selftest and 12 baseline findings), not the integrated tip.

**Smallest fix:** commit the final gate run’s output/summary measured against the exact round tip, including `findings=0`, and the selftest result (`checks=53`, `failed=0`, `rc=0`); link that record from the scorecard and lesson. Until then, remove or qualify the unsupported results. No gate or selftest was run during this review.

## Checks that hold

- **Scores / planned round:** the pinned baseline and round-tip scorecard both show coverage `8`, calibration `7`, operability `8`; all three current axis rows say `Numeric delta 0, legacy-unmapped` (`SCORECARD.md:13–15`). The current `## Planned` explicitly names **r19 (planned r18)** (`SCORECARD.md:86`). The score values are unchanged, and the row rationale consistently says no mapped numeric delta was applied.
- **C1 / operability:** the lesson’s measurement line (`corpus/lessons/round-18.md:6`) and committed `census/round-18/c1-matrix-worktree.json` support the bounded-fixture `8` cases / `0` failed, baseline `5` failures, the selftest `49 → 62` with zero failures, and retained r17/r15/r14 fixture counts. The lesson records timeout cleanup counts and the r15/r17 before→after residue measurements. The live-pair files are committed, and the correction in the lesson identifies the corrected 21-repository count.
- **C3 / coverage:** `corpus/lessons/round-18.md:8`, `census/round-18/leak-count-live-1721.json` (`total=65`), and `proc-census-live-1721.tsv` support the three residue classes, fixture `11/0`, live `65` versus blind `65`, and pid-set difference `0`.
- **C2 before-result and fixture:** `gate-pointers-before-b576341.json` supports the before count of `10` and its finding breakdown; the lesson records the `11/0` pointer fixture and the `33 → 53` selftest-count change. Only the final-result evidence above is missing.
- **Prior-round figures retained in the r18 axis rows:** the r17 lesson’s measurement lines `6–8` support the referenced census, seat-audit, and jj-receipt counts; the corresponding r17 records are committed. These prior figures do not reveal another Q10 gap.

## Commands / observed output

All checks were read-only inspection; no tests, runtime tools, or LSP queries were run.

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:SCORECARD.md` → baseline axis scores `8 / 7 / 8`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5efb519f00075d958c3d1109ef6fcb24c487eb87:SCORECARD.md` → current axis scores `8 / 7 / 8`, each `Numeric delta 0, legacy-unmapped`; `r19 (planned r18)`; C2 post-tip `0` and selftest `53/0` claims.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5efb519f00075d958c3d1109ef6fcb24c487eb87:census/round-18/gate-pointers-before-b576341.json` → resolved revision `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, exit `2`, `findings=10`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5efb519f00075d958c3d1109ef6fcb24c487eb87:census/round-18/gate-replays-r18.json` → replay keys are the five r13–r16 entries listed above; no round-tip result.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 5efb519f00075d958c3d1109ef6fcb24c487eb87 census/round-18 corpus/lessons` → round-18 records include the before gate JSON and historical replay JSON, but no post-tip gate JSON.

## Verdict

**PARTIAL — Q10 fails on the C2 post-fix evidence only.** Score stability/rationale, r19 planning, C1/C3 measurements, the C2 baseline count and fixture count, and retained prior-round figures are documented. The round-tip C2 `0` and the selftest `53/0` need an authenticated committed result before those numeric claims meet the stated criterion.

## Residual risk / verification gaps

This was a source-and-record audit, not an execution check. The C2 post-fix gate result and selftest failure count remain unverified; no tool was installed or updated.