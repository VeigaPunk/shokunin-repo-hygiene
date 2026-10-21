# FinalReportability — round 20 final falsification (calibration scope)

STATUS: PARTIAL — two blocking source defects at pin `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` contradict the C1 and C2 contracts the round claims. (1) `tools/souji-seat-audit.py` admits an `OWN ONLY` grant spelled with `..` once normalized, contrary to QUALITY Q39 "traversal … remain refused". (2) `census/round-14/run-targeted.py` lets a syntax-invalid dirty r14 wrapper escape as an uncaught `SyntaxError` (exit 1, traceback), not the Q40 exit-2 refusal, and the r20 input-binding oracle has no case that exercises it. Both are source-derived; nothing was executed.

## Scope and method

- Read-only. Every file was read via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>`, plus `grep`/`sed`/`awk` over those bytes. No directory was listed or recursed, no target code, test, build, or smoke was run, and no process was inspected or signalled.
- The operator-owned `census/operator-sweep-20261019/` was not opened.
- Tool installs or updates: none.
- The round's Gate quotes were not re-opened on the live web. This item named no exact URL, so source-row claims below are checked only for internal consistency.
- Pinned commit confirmed present (`git rev-parse --verify` returned the full SHA).

## Finding 1 (blocking, C1 calibration): `..` in an `OWN ONLY` grant is normalized into an allow

Pinned code:
- `owned_paths()` (`tools/souji-seat-audit.py:127–131`) takes each absolute `/home|/var/tmp` string after `OWN ONLY` and only strips trailing punctuation. It never rejects `..`.
- `audit_seat` builds `allowed = [report, *owned]` (`:342`), then adds `deliveries` (`:343`).
- Target checks in `target_verdict` (def `:259`) compare `any(n == _norm(p) for p in allowed)` (for example `:287`, `:309`). `_norm` is `os.path.normpath`, so a grant containing `..` collapses to a real path.
- The `..` refusal in `target_verdict` applies only to the write target string, not to the grant string.
- `run()` (`:387`) takes `spec["reportDir"].rstrip("/")` and builds each seat's report path from it. Only the wave parser validates that (disclosed in QUALITY Q38), but the same normalized comparison applies.

Counterexample (source-derived, [INFERENCE] until a gate executes it): an item prompt containing `OWN ONLY /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/x/../../tools/extra.py` yields `owned = [".../.ufo/x/../../tools/extra.py"]`. A later `edit` on `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/extra.py` has no `..`, so `_norm` matches and the verdict is `None` (allowed), not `V-WRITE-SCOPE`.

Contract conflict: QUALITY Q39 (`corpus/QUALITY.md:98`) says "traversal … remain refused"; Q38 (`:92`) says "with no `..`". The lesson's R20-M-table has no entry or fix for grant traversal. The catalogue lists `GrantTraversal` as OPEN with no closure (`census/round-20/recovery-status-catalog.json`).

Fixture gap: `tests/fixtures/r20-audit-contract.py:183–186` tests `..` only in the write target (`traversal_lane/.../../../../../tools/escape.py`). `own-only-exact` (`:179–181`) covers only exact grants. No control places `..` inside an `OWN ONLY` path, so the oracle cannot discriminate this case.

Requested disposition: reject any `..` component in an `OWN ONLY` or `reportDir`-derived allow path, or require `_norm(p) == p`, and add the traversal-grant control to the independent oracle.

## Finding 2 (blocking, C2 operability): `run-targeted` import escapes the refusal contract for a dirty wrapper

Pinned code:
- `census/round-14/run-targeted.py:16–18` runs `spec.loader.exec_module(module)` on `census/round-14/run-verification.py` at import time, outside any `try`.
- The `__main__` handler (`:65`) catches only `(OSError, ValueError, RuntimeError)`, not `SyntaxError`.
- The r14 runner's own helper loader (`run-verification.py:56–70`) does catch `SyntaxError`, so the repaired path is the helper. The wrapper load in `run-targeted` is not repaired.

Outcome for a syntax-invalid dirty `run-verification.py`: an uncaught `SyntaxError` at import, exit 1 with a traceback, and no record written. Q40 (`QUALITY.md:99`) requires exit 2 with no output for every dirty input class.

Oracle gap: `tests/fixtures/r20-input-binding.py` lists `targeted-helper-syntax-invalid` (`:132`) and `targeted-wrapper-dirty` (`:132`) but no `targeted-wrapper-syntax-invalid`. The r14 list (`:130–131`) likewise has no `r14-wrapper-syntax-invalid`. The fixture would pass with the defect present. The lesson's "Additional bootstrap refusal defect" (R20-M8) says "targeted uses the r14 loader," which covers only the helper path.

Requested disposition: wrap the import in `run-targeted.py` with `SyntaxError` (and `ImportError`) handling that returns exit 2 with stderr only. Add wrapper-syntax-invalid cases for targeted and r14 to the independent oracle. Do not count this run as exercised.

## Finding 3 (non-blocking, calibration of the record): catalogue dispositions are uniform and partly stale

- `census/round-20/recovery-status-catalog.json` gives every one of its 21 status entries the same `"disposition": "open; source/limit retained pending pinned runtime and independent closure"`. This includes `SourceTimeout`, whose paragraph reads "STATUS: no blocker", and `ContainmentLimit`, whose body is only "## STATUS: OPEN". The catalogue cannot separate resolved from open.
- Several OPEN premises are stale at the pin, and the lesson does not reconcile them:
  - `InputR13Fixtures` says `tools/souji-rev-pin.py:156–164` has no `onerror`. Pinned `input_snapshot` (`:94`) has `os.walk(..., onerror=walk_error)` at `:161–162`.
  - `ReceiptAuditor` says `run()` reads `Path(__file__)` late (`:364–365`). Pinned `:72` computes `AUDITOR_SOURCE_SHA256` at import and `run()` rechecks it at `:384`. The residual import-time race is disclosed as non-atomic, which is honest, but the catalogue entry is not updated.
  - `F5Enumeration` says SKILL lacks the exclusion wording. Pinned `SKILL.md:324–335` carries the self/descendant exclusion and unreadable/racing skip, consistent with Q43.
- Recommended: give each catalogue entry a disposition of resolved-at-pin (cite the pinned line), open (cite the defect), or no-blocker.

## Finding 4 (non-blocking, source tally): S089 quotes exceed the Gate

`corpus/SOURCES.md:109` (S089) names `GIT_DIR`, `GIT_COMMON_DIR` and `GIT_INDEX_FILE`. The lesson's Gate quotes only `GIT_WORK_TREE`. S094 is admitted as "current-version" from a 2026-09-19 Wayback capture, which records a snapshot, not a live current page. Both are labelled tier A. Neither changes a decision, but the row text should cite the quote it relies on.

## Checked at pin, no defect found

- SCORECARD commands resolve. `tests/fixtures/r20-audit-contract.py` takes `--tool` and `--base-tool`. `tests/fixtures/r20-input-binding.py` takes `--root` and `--baseline`. `census/round-20/run-acceptance.py` takes `--root --rev --output`. All four named files are present.
- Acceptance count is consistent: 13 literal steps plus `COUNTER_EXPECTATIONS` (5 entries, asserted at `:520`) equals 18, matching SKILL and the lesson.
- Q45 (root reads) is implemented: the auditor flags lane/fleet root reads as `V-RECURSIVE` (`tools/souji-seat-audit.py` `:32`, and tests `:484–485`).
- Q41 cutover: no short-ID counter or rev-pin command appears in README, SKILL, PROVINCE, SCORECARD, QUALITY, SOURCES, the process-residue entry or the r20 lesson. The README's five current commands (`corpus/README.md:304–308`) use full IDs. This grep is pattern-limited, not exhaustive.
- Gate tally is consistent across LOG, lesson and SOURCES: S089–S095 yield 7 pages, 6 mined admits and 1 rejected S090. The admitted set is S089, S091, S092, S093, S094 and S095. S090 is rejected as cleanup authority.
- Erratum table has 20 rows. The errata text lives in the round-19 report, which is outside this item's named set, so I did not verify it against the report.
- Recovery counts agree: `census/round-20/recovery-seat-outcomes.json` gives started 64, completed 39, dead 25, replacements 0. The dead list has 25 entries and `role_mix` sums to 64. The pre-spawn refusals are recorded as zero starts.
- Coordinator deviation: `census/round-20/coordinator-start-excerpt.txt:43` is the lane-root `read` line, and `coordinator-scope-deviation.json` matches it. The LOG correction is appended, not rewritten.
- SHONEN: all four author assertions remain `[~]`, with no `[x]`. SCORECARD's r20 rows state "changed measurement not yet run", add no r20 capability row, and keep numeric delta 0. Calibration is not pre-claimed.

## Out of scope / not claimed

- No runtime pass, promotion, certification or K5 change is asserted. Certification stays OFF, K5 HELD, F5 reap and NAMESPACE_SHA256 HELD.
- No seat is credited or respawned. Missing reports remain unavailable, not dead.
- Findings 1 and 2 are source-derived counterexamples and stay [INFERENCE] until the parent's post-integration gate executes the proposed controls.

## Routed to L1

1. Reject `..` in `OWN ONLY` and report-derived allow paths; add the grant-traversal control to `tests/fixtures/r20-audit-contract.py`.
2. Guard `census/round-14/run-targeted.py:18` for `SyntaxError`/`ImportError` with exit 2 and stderr only; add wrapper-syntax-invalid cases to `tests/fixtures/r20-input-binding.py`.
3. Reconcile the catalogue dispositions (Finding 3) and the S089 quote scope (Finding 4).
