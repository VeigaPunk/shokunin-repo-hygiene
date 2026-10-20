# RerunBoundedArms — WAVE 2 FALSIFY — r18-bounded 8/5 → 8/0

STATUS: DONE — both arms rerun in my clone at 5efb519; claimed matrix reproduces exactly (base 5 FAIL / changed 0 FAIL, per-case verdicts byte-match record); one record-quality defect found (300-char detail truncation in runner), verdicts unaffected.

## Attacked claim

C1 (portion): `tests/fixtures/r18-census-bounded.py` (B1–B8) scores b576341 census 5 FAIL / 8 total and landed census (5efb519) 0 FAIL / 8 total; record `census/round-18/c1-matrix-worktree.json` pins both arms. Judged on operability.

## Identity chain (all verified by sha256)

| Artifact | Record pin | My measurement | Match |
|---|---|---|---|
| changed-arm census | `7e6a92d415f8f256…` (arm `changed`, rev WORKTREE) | landed tip `tools/souji-census.sh` at 5efb519: `7e6a92d415f8f256…` | YES |
| r17-base census | `006b98231f8d138b…` (rev b5763415cc67…) | `git show b576341…:tools/souji-census.sh` → `006b98231f8d138b…` | YES |
| r18 fixture | `2249616641f4a1b9…` | tip `tests/fixtures/r18-census-bounded.py`: `2249616641f4a1b9…` | YES |
| runner | `da61f6be8f6f544b…` | tip `census/round-18/run-matrix.py`: `da61f6be8f6f544b…` | YES |

The record's "changed" arm therefore measures byte-for-byte the artifact that landed, and its "r17-base" arm measures byte-for-byte b576341. Fixture printed the same TOOL sha256 lines at run time.

## Rerun (exact command per ALLOWED-EXEC)

Clone: `git clone --no-local <lane> /var/tmp/souji-r18w2-RerunBoundedArms/lane && git checkout --detach 5efb519f…` (rev-parse confirmed `5efb519f00075d958c3d1109ef6fcb24c487eb87`).

- Changed arm: `cd /var/tmp/souji-r18w2-RerunBoundedArms/lane && python3 tests/fixtures/r18-census-bounded.py --census /var/tmp/souji-r18w2-RerunBoundedArms/lane/tools/souji-census.sh` → RC=0, wall 75.1s, stderr empty.
- Base arm: same with `--census /var/tmp/souji-r18w2-RerunBoundedArms/base.sh` (extracted baseline) → RC=1, wall 231.8s.

### Per-case verdicts vs record

| Case | Record base | My base | Record changed | My changed |
|---|---|---|---|---|
| B1 | FAIL | FAIL | PASS | PASS |
| B2 | FAIL | FAIL | PASS | PASS |
| B3 | FAIL | FAIL | PASS | PASS |
| B4 | FAIL | FAIL | PASS | PASS |
| B5 | PASS | PASS | PASS | PASS |
| B6 | PASS | PASS | PASS | PASS |
| B7 | PASS | PASS | PASS | PASS |
| B8 | FAIL | FAIL | PASS | PASS |

SUMMARY lines: base `total=8 failed=5`, changed `total=8 failed=0` — the claimed **8/5 → 8/0** holds.

- Changed arm: all 8 `CASE` detail JSONs parse and are **byte-identical** to record `arms.changed.r18-bounded.cases.*.detail` (B4's detail is identical too — see finding F2 on what it means).
- Base arm: PASS details (B5/B6/B7) byte-identical; FAIL details match the record's stored 300-char prefix exactly; the record itself is truncated (finding F1). Full untruncated causes from my run, identical shape for B1/B2/B3/B8: `exit=124 expected 0`, `fixture timeout rc 124 is FAIL, never SKIP`, `census header missing`, `row names=[] expected ['a','b','c']`, three `row missing` entries, two `missing from no-shim control` entries, and `timeout diagnostic missing: 'souji-census: repo-timeout 8s <repo-b>'`. B4 adds the same block for both fleets plus `base census hung on static .gitignore FIFO until rc 124` and `…attributes FIFO until rc 124`. I.e. every base FAIL is the baseline census blocking forever on the injected FIFO until the fixture's 40 s deadline — precisely the defect C1's per-repo watchdog removes. Changed arm passes exercised `require_timeout_diag` (exact stderr `souji-census: repo-timeout 8s <repo>`), B7 protected refusal exit 2.

## Residue after each run (PROBE-rule scans, nothing signalled)

- After both runs: `ps -eo pid,ppid,pgid,sid,stat,etimes,args | grep -E "souji-r18-FixtureR18Bounded|base\.sh --root|souji-census\.sh --root|souji-census-watchdog|git-shim|cmp-shim"` → **zero processes referencing my sandbox** `souji-r18w2-RerunBoundedArms` (own-sandbox grep rc=1). Both fixture scratch dirs were rmtree'd by fixture `cleanup()`; no FIFO leftovers (B6 resource check passed: `ENXIO` on all probe opens).
- Record's r18-bounded arms also claim `leftover_procs_count: 0` — consistent with my observation.

## Findings by severity

**F1 · MEDIUM (measurement-record defect; verdicts unaffected) — runner truncates per-case evidence to 300 chars, producing invalid JSON.** `census/round-18/run-matrix.py:219`: `"detail": match.group(3)[:300]`. 43 case details across all four arms are exactly 300 chars and cut mid-string (e.g. r17-base B1 ends `…"census ` at char 288; all 5 r17-base r18-bounded FAILs, plus the same 5 in pre-harm and r14-harm arms, plus r14/r15/r17 FAIL details). Anyone parsing `cases.*.detail` as JSON (as the record's own shape invites) errors out, and the stored *why* of every base-case failure is lost. The 8/5 → 8/0 headline survives because verdict/total/failed are separate fields. Smallest fix: drop the `[:300]` slice (or store `{"problems": [...]}` structured instead of a string slice), regenerate the record.

**F2 · LOW (fixture detail cosmetics) — B4's serialized `expected_rows` is a descriptive label never compared to rows.** `tests/fixtures/r18-census-bounded.py:1092-1099` sets `expected_rows` to six prefixed keys (`ignore/*`, `attributes/*`) only for the CaseResult/detail; actual assertions use per-run `expected_repo_rows = {"a","b","c"}` at :1079/:1087 via `census_problems`, and `observed_rows` in the detail is `row_labels(rows())` of only the *last* run keyed by basename (:1232-1237, `rows_by_name` at :1250). Hence record and my rerun both show `expected_rows={attributes/a,…}` vs `observed_rows={a,b,c}` with `problems:[]` — no false pass (real checks ran and passed), but the detail JSON is self-contradictory to a reader. Smallest fix: name the label field `expected_fleets` or serialize both measured runs' rows.

**F3 · OBSERVATION (host hygiene, other seats' leftovers — not signalled, not mine) — the base census's unbounded FIFO hang is still visible live.** `ps` shows ~20 orphaned `bash …/tools/souji-census.sh --root /var/tmp/r15-census-config.*/unsafe-repos/r-inc-fifo --include-root` processes from other seats' earlier rounds (`souji-r16-*`, `souji-r17-matrix.*`, common ppid 1497), etimes up to ≈26,777 s (~7.4 h). This is the exact unbounded-hang fail mode C1's watchdog eliminates; it corroborates the mechanism behind the base arm's 124s. Out of my lane to kill.

**F4 · NOTE (harness) — fixed shared SEAT_TMP root.** `tests/fixtures/r18-census-bounded.py:35` hardcodes `/var/tmp/souji-r18-FixtureR18Bounded`; runs are concurrent-safe only because each run's scratch is `mkdtemp`-unique (:103-104) and cleanup is per-scratch. During my window a foreign seat was live in the same root (census at `/var/tmp/lane/tools/souji-census.sh`, scratch `fixture.pxotwl_8`, B8 case) plus a foreign `lane/` directory dated Oct 20 16:54 inside the root. No interference with my runs (different scratch dirs, private sessions per census run). Keep an eye on it if a future fixture ever writes fixed-name files there.

**F5 · NOTE (record provenance) — `allow_dirty_fixtures: true` with r14/r15/r17 fixtures modified at run time** (record `fixtures_dirty`). The r18-bounded numbers are immune: its fixture was new/untracked then and the committed tip file is byte-identical to what I ran (digest above), as is the runner. The other suites' arms in this record carry the dirty-fixture caveat — out of my seat's scope.

## C1 sub-claims cross-checked in landed source (code-verified, digest-matched to measured bytes)

`tools/souji-census.sh`: default `REPO_TIMEOUT="${SOUJI_CENSUS_REPO_TIMEOUT-600}"` (:220) and `--repo-timeout` override with integer 1..86400 validation (:245-257); every repo command — list-phase `guard_repo_candidate` (:1655-1690) and `census_one` (:1699-1712) — runs under `run_repo_with_watchdog`: worker in own process group (`set -m`), `setsid` watchdog TERM→KILL on the group (:1477-1501), `repo-timeout-unreaped` diag when the group survives (:1641-1643), exact error row `$(repo)\t0\t0\t0\t0\t\terror` with empty scratch column (:1693, :1711), exact stderr `souji-census: repo-timeout <N>s <repo>` (:1678-1679, :1707-1708), rc 2 protected refusal passed through to exit 2 (:1716-1718 + emit paths), other repos still measured and overall exit 0 (header+rows printed unconditionally). Behavioral proofs: B1–B4, B8 (8 s timeout row+diag, neighbors clean), B5 (30 s finite slow repo measured clean, elapsed < 30 s), B6 (FIFO probe ENXIO, no session members), B7 (exit 2 refusal, no stdout rows).

## Verdict

**HOLDS.** The r18-bounded 8/5 → 8/0 claim reproduces independently at the landed tip with exact per-case agreement and zero residue. No defect found in the measured behavior; the only actionable defect is F1 (record evidence truncation in the runner, cosmetic to the headline numbers).

## Tooling

No tools installed or upgraded (stock bash 5.3.20, git, python3 3.14.8 sufficed; pacman transactions are paused host-wide). Nothing signalled; no network writes; no lane/fleet repo writes except this report file. Sandbox `/var/tmp/souji-r18w2-RerunBoundedArms` deleted after evidence extraction.
