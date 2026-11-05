# Round 66 — caller-injected env routes (C1 operability) and env-refusal statement agreement (C2 calibration)

Attempt 1. Base `045e103478fa4a7eff77db2cab5b9e2f26959a0a` (lane master at round start, clean, pushed; carries the round-65
landed writer). Landed candidate `c13fbb4e1b563a78278ddc14316c20252e9a6d8d` (writer bytes sha256 `a8c47d36…97fc`).

Chronology: instruments `8410a97e` (superseded, see M3) → instruments `4576f101`; controls `10d175a5` (superseded, see M1) and
`4864c01f`; freeze attempt 1 `5d17a5de` (superseded, see M1, M2); freeze attempt 2 `02cc6609`
(`census/round-66/preregistration-attempt2.txt`); candidate integration and SKILL/QUALITY landing `c13fbb4e`. No candidate
byte existed before attempt-2 freeze; the candidate was produced post-freeze by wave seat S66ExecWriter.

## Claims

Frozen at `census/round-66/preregistration-attempt2.txt`; predicates are not amended here.

- **C1, operability (receipt-binding surface; Q59 neutral).** The writer refuses caller-injected `GIT_CONFIG_*` and
  object-redirect env routes, pins the config routes on every git call, records full permission bits, and refuses a
  same-content symlink retarget, on the 28-row matrix `census/round-66/c1-matrix.tsv`.
  Target `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS`,
  `EXIT=0`. Do-nothing: `new_forgeries=8`, `EXIT=1`.
- **C2, calibration (lowest owned axis, score 7; Q59 bookkeeping-file).** The SKILL.md statement population `c2-statements.tsv`
  (s1–s5) agrees with the writer bytes under the live-marker read, and the round-66 counter kills the M-ENV mutant that the
  round-65 counter scores as live (round-65 M10). Target `SUMMARY rows=5 findings=0 verdict=PASS` plus `findings>=1` on M-ENV,
  while the round-65 counter gives `findings=0` on the same mutant. Do-nothing: `findings=1`, `EXIT=1`.

Named limits frozen with the prereg: ignore routes outside C1; lexical C2 read; one M-ENV mutant.

## Gate

- **Sources opened this round.** S298 git(1) § ENVIRONMENT VARIABLES and S299 git-config(1) (https://git-scm.com/docs/git and
  https://git-scm.com/docs/git-config; accessed 2026-11-05; HTTP 200). Captures `census/round-66/sources/git-environment.{html,txt}`
  (244227 and 58863 bytes; txt sha256 `624e85ef…8035`) and `git-config.{html,txt}` (830605 and 334668 bytes; txt sha256
  `dfc44574…6054`). Located quotes with UTF-8 byte offsets in `census/round-66/sources/quotes.tsv`, re-sliced by the L1 at landing:
  S298 offsets 30753 (`If the object storage directory is specified via this`, 9 words), 46334 (`Setting and exporting this
  environment variable tells Git to`, 9 words), 40302 (`will not be read. Likewise, if GIT_CONFIG_GLOBAL is set, neither`, 10
  words), 31092 (`specifies a ":" separated (on Windows ";" separated) list`, 9 words). S299 offsets 20918 (`If GIT_CONFIG_COUNT
  is set to a positive number, all environment pairs`, 11 words), 21411 (`passed via git -c .`, 5 words), 21376 (`overridden by any
  explicit options`, 5 words), 103037 (`to .gitignore (per-directory) and .git/info/exclude .`, 6 words), 20597 (`Take the
  configuration from the given files instead from global or`, 11 words). Absences (`census/round-66/sources/absences.tsv`):
  `GIT_CONFIG_PARAMETERS`, `GIT_REPLACE_REF_BASE` and `GIT_OBJECT_DIRECTORY`/`GIT_ALTERNATE_OBJECT_DIRECTORIES` (on git-config)
  are not defined on the pages; their behaviour rests on revenger probes.
- **Admitted** S298 and S299 as `mined` rows, both used by `corpus/knowledge/caller-env-routes-receipt-writer.md`.
- **Rejected inside the entry:** "GIT_CONFIG_PARAMETERS is a documented variable" (absent from both pages); "a tool must refuse
  a caller-set redirect" (neither page says so); "GIT_COMMON_DIR is documented as a config route" (not stated; it was not
  searched for, so the entry does not name it as documented).
- **Sourced claim (frontier step, CORPUS.md §2b item 4).** C1 rests on S298/S299 through the knowledge entry it lands.
- **Census.** Before: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` rc 0, 220 registry rows.
  After: rc 0, 222 rows (`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md`). The first landing of the two rows
  failed the census for a 12-cell shape and then for a missing `used-by` file; both were repaired before the census passed.
- **Assimilation: none.** `considerthese/` is absent in this lane (`test -d`). The connector scanned the shokuknow souji merge
  package read-only: no theme touches receipt-writer env routes, untracked visibility or mode bits.

Measured receipts (all at the landed revision unless said otherwise):

- `census/round-66/controls/c1-do-nothing.txt`: base bytes in the new slot, `SUMMARY matrix=28 base_forgeries=8 base_honest=5
  new_forgeries=8 new_honest=5 class_mismatches=8 regress=PASS`, `EXIT=1`.
- `census/round-66/records/c1-after.txt` (rev `c13fbb4e`): `SUMMARY matrix=28 base_forgeries=8 base_honest=5 new_forgeries=0
  new_honest=5 class_mismatches=0 regress=PASS`, `EXIT=0`.
- `census/round-66/controls/c2-do-nothing.txt`: `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1` (s5 absent at base).
- `census/round-66/records/c2-after.txt` (rev `c13fbb4e`): `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0`.
- `census/round-66/records/c2-mutant-m-env.txt`: M-ENV built from the landed writer by `c2-mutate.py` and committed in a scratch
  clone (mutant commit `0c8c5f4b`, not in the lane). Round-66 counter `findings=1 verdict=FAIL` (`SCOPE-OVERREACH s2`,
  `env=0`), EXIT 1. Round-65 counter `findings=0 verdict=PASS`, EXIT 0.
- `census/round-66/records/writer-selftest.txt`: `SELFTEST cases=33 pass=33 fail=0`. `records/c2-selftest.txt`: `cases=14 pass=14`.

## Wave evidence (w1, 10 seats, policy v1 band 8–16)

Seats: `S66ExecWriter` (executor, candidate), `S66MutKill` (mutation-tester), `S66ReviewerDesign` and `S66ReviewerC2` (reviewer ×2),
`S66CriticClaims` (critic), `S66SentinelScope` (sentinel), `S66ScoutSources` (scout), `S66ScribeEntry` (scribe),
`S66ConnectorOverlap` (connector), `S66RevengerProbe` (revenger). Attack share 5/10 (reviewer ×2, critic, mutation-tester,
sentinel). Planner held by the L1 (validator refuses planner). Dead seats: none (10/10 settled with output, `w1-results.json`).
Mirror: `census/round-66/wave/w1/` (seat reports, the candidate bytes and notes, mutation kill matrix, probe transcript, scout
captures, dispatch and spec). Seat outputs are the evidence; none of them is a judge verdict.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Headerless control receipt broke the first freeze. The C2 do-nothing capture `10d175a5` carried counter output without the `rev=`, `instrument=`, `instrument_sha256=` and `command=` lines. Freeze `5d17a5de` was landed and pushed with it. | `tools/souji-freeze-check.py --substance` at `5d17a5de`: 4 findings (CONTROL-REV-MISSING, CONTROL-INSTRUMENT-MISSING ×2, CONTROL-COMMAND-MISSING), rc 1 | the freeze checker caught it; the L1 did not check control receipts before landing them | header-complete control `4864c01f`, re-issued freeze `02cc6609` at a new path; freeze-check at `02cc6609` `SUMMARY claims=2 findings=0`. Shown able to fail: the headerless file fails the checker (above). |
| M2 | Attempt-1 preregistration edited in place by an append. Commit `01bc1e16` (subject "re-issued freeze") changed a frozen file. | `git show 01bc1e16 --stat`; freeze-check at `01bc1e16` `C0 FROZEN-EDITED census/round-66/preregistration.txt differs between freeze and revision` | none (the critic found it, not the L1) | restored by commit `a81280e1` (bytes equal `5d17a5de`); attempt 2 at a new path. The superseded file is kept, not deleted. |
| M3 | `GIT_REPLACE_REF_BASE` without a trailing slash made row E6 measure a git crash. The instrument commit `8410a97e` aborted every E6 run (`BUG: refs.c:1908`), so E6 was never a writer test. | revenger P6a (rc -6) against P6b (rc 0) and P6c (forged replace honoured); the pre-repair value is `git show 8410a97e:census/round-66/c1-counter.py` (`refs/replace-forged-r66`, no slash); the pre-repair do-nothing run printed `CASE E6 ... base=refuse`, rc 2, with the BUG line (L1 session output, not committed) | none | value repaired to `refs/replace-forged-r66/` in `4576f101` before any control or candidate. Shown able to fail: P6a aborts, P6b forges. |
| M4 | The C2 M10 selftest case is vacuous. `m10-returncode-line-not-live` binds the wrong row (s3), so the row resolves `GOVERNED-STATEMENT-UNRESOLVED` regardless of markers. Reverting the repair leaves `--selftest` at 14/14. | `S66ReviewerC2.md` MEDIUM-1 (reverted-rule run `cases=14 pass=14`) | none (the selftest's stub-always-zero control does not test per-case vacuity) | **Not fixed this round.** The counter is frozen; a selftest change is a counter change. Routed to round 67 as a new frozen counter with a row that binds the line, shown to fail on the reverted rule. Q129 text is corrected below to stop citing this case as a guard. |
| M5 | The s5 statement overreaches. "closed for the caller-injected config and object-redirect routes" is universal, and `GIT_COMMON_DIR` is an open config route on the landed candidate (W2). C2 checks needle presence, so it cannot falsify the scope. | `S66CriticClaims.md` §3 items 1 and 5; L1 measurement W2 (`S66ExecWriter`, `S66MutKill` do not cover it): base and candidate both accept, rc 0 | none (route enumeration was by known names, not by git's env surface) | the population is frozen and the literal cannot change. Scope is restated in the SKILL section and the entry's named limits. Routed to round 67: a route sweep of git's environment names as a frozen enumeration, plus a population row that can fail on scope. |
| M6 | The frozen C1 counter docstring says a flag or tracked/untracked edit "is accepted" on the base writer (T1/T2/T3/T5). The base refuses those rows (`census/round-66/controls/c1-do-nothing.txt`). | `S66ReviewerDesign.md` Part A item 1 (LOW) | none | disclosed; the docstring is inside the frozen counter (sha `273d6fc9…`), so not amended. Routed to round 67. |
| M7 | The frozen s4 note in `c2-statements.tsv` says s4 is absent from base SKILL.md. Base SKILL.md contains s4 (grep count 1). | `S66CriticClaims.md` §4 | none | disclosed; population frozen. Routed to round 67. |
| M8 | E3 wording conflict. The claim lists `GIT_CONFIG_GLOBAL` among routes the writer "refuses"; the candidate repoints it to the null device, and E3's frozen class is the dirty check. | `S66CriticClaims.md` §3 item 4; `S66SentinelScope.md` Part B (d) | none | disclosed here and in the entry. Operator ruling on wording; no predicate change. |

Sweep for mistakes at round end: `git log --oneline 045e1034..HEAD -- census/round-66 .ufo/waves/round-66` shows the chronology
above; `grep -c 'GIT_COMMON_DIR' census/round-66/c1-matrix.tsv` → 0 (route absent from the frozen matrix).

## Named limits (carried; none counted as admitted)

- **C1, `GIT_COMMON_DIR` open** (W2, measured on the landed candidate): a tracked 755→644 change passes the clean-tree check with `GIT_COMMON_DIR` set to a copy whose config sets `core.fileMode=false` (rc 0 on both slots). The repository's own `core.fileMode=false` is the same config read.
- **C1, ignore routes** (`.git/info/exclude`, tracked `.gitignore`, repository-local `core.excludesFile`) remain outside C1.
- **C1, honest-run refusal cost (trade).** A writer launched under `git -c` (git sets `GIT_CONFIG_PARAMETERS` for the child) is refused, rc 2 on the candidate, rc 0 on base. Measured by an L1 probe on a scratch repository (output in the round session; not a committed receipt). A host with global excludes would also see those files as dirty (L2, not measured here). Under AXES.md a trade is not an improvement; operator ruling.
- **C1, setgid unmeasured; pre-run setuid/sticky invisible** on a tracked file (git porcelain does not track them).
- **C1, other git-resolution names** (`GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`) not refused; `GIT_CONFIG_SYSTEM` inert once `GIT_CONFIG_NOSYSTEM=1` is pinned.
- **C1, kill power.** Four of eight wave mutants survive the frozen matrix (K3, K4, K6, K7). K3 and K4 are mutually redundant for E3; K6 and K7 need fixtures no row creates.
- **C2 scope and separability.** C2 is not separable from C1: s5 and the M-ENV target read the candidate's needles (`S66CriticClaims.md` §2). The s5 scope overreach (M5) is not falsifiable by C2.
- **C2 kill power.** One mutant; the selftest guard is vacuous (M4).
- **C2 lexical read.** A dead line still carrying `refuse(` stays live (named in the prereg, L4).

## Routed to round 67

1. Route sweep of git's environment surface (git(1) ENVIRONMENT VARIABLES, including `GIT_COMMON_DIR`) as a frozen enumeration, with a do-nothing control and a fixture for the mode-hiding route. Operator decision needed on whether the repository's own `core.fileMode`/`core.excludesFile` are in scope.
2. New frozen counter (not an amendment) fixing M4 and M6: a selftest row bound to the M10 line that fails on the reverted repair, and a corrected docstring.
3. Population that can fail on scope (M5), and the s4 note (M7).
4. Fixtures for K3, K4, K6 and K7 kill power, or an explicit decision that the pins are defence in depth.
5. Operator rulings: honest-run refusal under `git -c` (W3/L2 trade) and the E3 wording (M8).

## Q129 correction (append-only)

QUALITY Q129 cites selftest case `m10-returncode-line-not-live` as its check. That case is vacuous (M4). The check that holds is the frozen M-ENV recipe, whose round-66 and round-65 counter results are recorded above. Q129's text is not edited in place; this correction is the append.

## Verdicts

- **C1 (operability):** the frozen target is met (`EXIT=0` at `c13fbb4e`). Not admitted as harm-free: the open `GIT_COMMON_DIR` route, the setgid gap and the honest-run trade are named and need an operator ruling.
- **C2 (calibration):** the frozen target is met (`findings=0` at `c13fbb4e`; M-ENV `findings=1` for round 66 and `0` for round 65). The critic's would-reject on the s5 scope and non-separability stands as a named limit.
- **Trend — expansion: unchanged.** Two registry rows and one knowledge entry on F4-adjacent ground; no coverage-map row moved.
- **Trend — quality: improved, with a named trade.** Frozen-matrix forgeries 8 → 0; honest accepts kept 5/5; the `git -c` refusal cost is recorded, not hidden.
- **Trend — discernment: unchanged.** The M-ENV kill moved from 0 to 1 on the round-65 mutant, but the vacuous selftest guard and the s5 overreach are disclosed defects that this round's frozen predicates could not repair.
