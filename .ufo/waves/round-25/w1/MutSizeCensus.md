# MutSizeCensus — size-census tool-clause mutants, 8-case vs 12-case fixture (souji r25, wave 1, D3)

## Status
STATUS: DONE — 20 clause mutants of the committed tool measured against both fixtures. The frozen 8-case fixture kills 6/20; ExecC2's 12-case draft kills 12/20. On the r24 W2C1MutTool 11-mutant set: 4 killed / 7 survived under the 8-case fixture → 6 killed / 5 survived under the extension (case 11 pins m04, case 10 pins m11). Survivors after extension: m02, m05, m06, m07, m09, m14, m19, m20. Pristine passes both fixtures (8/8, 12/12, rc 0); the stub control is rejected by both (4/8, 4/12, rc 1).

## Evidence
- Tool bytes: `git show a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe:tools/souji-size-census.py` (blob `182001dbc9aecbd5c877af34301a383fe79c8e02`, sha256 `c5690681…a6eb3`). `git diff --stat 6e4737e..HEAD -- tools/souji-size-census.py tests/fixtures/r24-size-census.py` empty at lane tip `6deb535`.
- 8-case fixture: `a6d2d15:tests/fixtures/r24-size-census.py` (blob `fe08f3aa06ca530630322c125b508f1b12e2a6dc` = r24's blob, sha256 `373ef1f0…084f`).
- Extended fixtures — the draft path moved during the run, so two drafts were measured: draft A sha256 `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528` (now `w1/ExecC2-2/r24-size-census.py`); draft B sha256 `5bd7e74fb7344e2b583858eaeee761272aadc0d3a0a4cfbbec89fd8f68754238` (now the canonical `w1/r24-size-census.py`). Both add only helpers and cases 9–12; cases 1–8 and `case_control` are byte-identical to the 8-case fixture. The kill matrices are identical (cmp of the mutant/cases/FAIL columns is empty), so the 12-case column holds for either draft.
- Environment: git 2.56.0, Python 3.14.8. Detector per tool: `python3 -B <fixture> --tool <tool>`. All 22 tools ran under both fixtures; each matrix was run twice and every `cases=`/`CASE … FAIL` line was identical across runs (E1==E2, A1==A2, B1==B2).
- Baselines: pristine 8-case `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` rc=0; pristine 12-case `cases=12 pass=12 …` rc=0 (both drafts). No baseline failure, so no inconclusive verdicts.
- Stub control (emits `garbage=0 size_garbage=0 unreachable=0 alternates=0`): 8-case rc=1 pass=4 FAIL 2,3,5,6; 12-case rc=1 pass=4 FAIL 2,3,5,6,9,10,11,12. The fixture's internal CASE 8 control passes in every run (`stub_failed=dangling,garbage,alternates`).
- Mutants: separate files built by exact string replace with a per-edit match-count assertion (`mkmut.py`); pristine never edited. `sha256sum -c` reported OK for tool/fixture8/fixtureA/fixtureB/stub after all runs — no restore needed; the lane was not written except this report. No git/jj mutation; no tools installed or updated.

| # | Clause mutated (tool line @a6d2d15) | 8-case | 12-case |
|---|---|---|---|
| m01 | count-objects on resolved common dir → `-C <path>` (:182, :208) | KILLED (3,4) | KILLED (3,4) |
| m02 | alternates from raw `objects/info/alternates` lines (:210) | survived | survived |
| m03 | drop `objects/pack/*.promisor` scan (:177) | KILLED (6) | KILLED (6) |
| m04 | subdir refusal `realpath(path) != realpath(top)` → `False` (:150) | survived | KILLED (11) |
| m05 | env allowlist → `dict(os.environ)` (:89) | survived | survived |
| m06 | drop `timeout=TIMEOUT_S` (:103) | survived | survived |
| m07 | drop `-c core.fsmonitor=false` (:74) | survived | survived |
| m08 | `size_garbage=0` literal (:219) | KILLED (3) | KILLED (3) |
| m09 | `fsck --dangling`, count `dangling ` (:198, :200) | survived | survived |
| m10 | garbage-warning allowlist → any stderr fails (:184) | KILLED (3) | KILLED (3) |
| m11 | stderr-is-failure dropped at all 6 sites | survived | KILLED (10) |
| m12 | drop bare special case (`if bare == "true": top = gitdir` → `if False:`) (:142) | survived | KILLED (9,10) |
| m13 | drop `extensions.partialClone` refusal (:162–166) | survived | KILLED (12) |
| m14 | drop `remote.*.promisor` refusal (:172) | survived | survived |
| m15 | `invoked_from=bare` → `main` (:154) | survived | KILLED (9) |
| m16 | stderr ignored in `checked()` only (fsck/version) (:118) | survived | KILLED (10) |
| m17 | counts line not last (trailer `census.end=ok` appended) | KILLED (1–5) | KILLED (1–5,9) |
| m18 | extra argv accepted (`len(argv) != 2` → `< 2`) (:127) | KILLED (6) | KILLED (6) |
| m19 | linked worktree labelled `main` (:155) | survived | survived |
| m20 | stderr ignored at the 5 non-`checked` sites (resolve ×2, refuse_promisor ×2, count_objects) | survived | survived |

Totals: 8-case killed=6 survived=14; 12-case killed=12 survived=8; inconclusive=0.
- r24 set (m01–m11, same clauses as W2C1MutTool m01–m11): 8-case killed 4 / survived 7 — reproduces r24's `uncovered=7`; 12-case killed 6 / survived 5 (m02, m05, m06, m07, m09).
- r25-surface set (m12–m20): 8-case killed 2/9; 12-case killed 6/9.
- **Surviving set after extension:** m02, m05, m06, m07, m09, m14, m19, m20.

Out-of-fixture witnesses (`witness.sh`; own mkdtemp repos; `env -i` clean env; same input to pristine and mutant):
- m14: repo with only `remote.origin.promisor=true` → pristine `rc=2 refused: promisor remote`; mutant `rc=0` counts 0,0,0,0.
- m19: linked worktree → pristine `census.invoked_from=linked`, mutant `census.invoked_from=main` (same counts).
- m09: unreferenced tree holding one blob → pristine `unreachable=2`, mutant `unreachable=1`.
- m02: alternates file `# comment` + one real path → pristine `alternates=1`, mutant `alternates=2`.
- m05: caller `GIT_TRACE=1` → pristine rc=0, mutant rc=1 (trace on stderr).
- m20: alternates naming a missing dir → both rc=1 (pristine fails at resolve `rev-parse`; mutant later at fsck via `checked()`). Input does not discriminate.
- m06, m07: not re-witnessed this run; cite r24 `W2C1MutTool.md` (m06 FIFO-alternates hang 900 s vs unbounded; m07 no behavioral witness — fsmonitor override masked by `--git-dir`).

## Findings
1. **D3 before/after measured.** The r24 11-mutant set goes from 7 survivors to 5 under the 12-case draft; across all 20 mutants, survivors drop 14 → 8. Case 11 (subdir) kills m04; case 10 (bare-empty) kills m11 and m16; case 9 kills m12 and m15; case 12 kills m13. Location: draft CASES (:339–343).
2. **The task brief inverted the r24 figure.** Lesson `corpus/lessons/round-24.md:58`: "The fixture kills 4 of 11 tool-clause mutants (`uncovered=7`, `W2C1MutTool`)." This run reproduces kills=4, survivors=7 on the 8-case fixture. Any D3 disclosure must say "7 survive".
3. **m14 remote-promisor refusal unpinned (new survivor, witnessed).** Case 6's blobless clone also carries the `.promisor` pack, so after the remote config is stripped the pack scan still refuses; case 12 has no remote. No case has `remote.*.promisor=true` alone. Tool :172.
4. **m19 linked label unpinned (new survivor, witnessed).** Case 9 asserts `census.invoked_from=bare` (draft :303) but no case asserts `=linked`; case 4 checks only counts. Tool :155.
5. **stderr-is-failure is pinned at exactly one site.** Case 10 kills m11/m16 solely through `checked()` on fsck's `notice: No default references`. Stderr checks at the other five sites (m20) survive both fixtures; on a missing-alternate input the downstream fsck `checked()` masks them (both rc=1) [INFERENCE: defense in depth whenever fsck also writes stderr for the same condition].
6. **Carried r24 survivors unchanged.** m02 (alternates source), m05 (env allowlist; fixture strips `GIT_*`), m06 (timeout; fixture `TIMEOUT = 120` :35 < tool `TIMEOUT_S = 900` :76), m07 (fsmonitor), m09 (unreachable vs dangling) still pass 12/12. C2's frozen case set was not designed to cover them — coverage findings, not C2 kills.
7. **Internal control scope.** `case_control` still runs only `CASES[1:5]` (draft :283), so the stub control never exercises cases 9–12. Run directly as `--tool`, the stub fails all four new cases, which shows they discriminate. Matches the prereg (stub must fail ≥1 case); disclosure only.
8. **Amendment 2 §3 text vs implementation.** Amendment `preregistration-amendment-2.txt:18`: "the implementing fixture adds an unchanged-manifest condition to both, disclosed in the report." The implementation docstring (draft B :14): "Cases 10-12 report manifest_changed but do not gate on it (not in the frozen predicate)." Neither draft gates on `manifest_changed` for cases 10–12. Internal inconsistency between amendment text and implementation; no frozen predicate is touched, so I am not raising an attack — flagging for L1.

## Attack log
- A1–A11 (r24 clause set re-run): 8-case 4 KILLED / 7 SURVIVED; 12-case 6 KILLED / 5 SURVIVED (m04→case 11, m11→case 10).
- A12 no bare special case → SURVIVED 8 / KILLED 12 (9,10).
- A13 no `extensions.partialClone` refusal → SURVIVED 8 / KILLED 12 (12).
- A14 no `remote.*.promisor` refusal → SURVIVED both; witness rc 2→0.
- A15 bare labelled main → SURVIVED 8 / KILLED 12 (9).
- A16 fsck stderr ignored → SURVIVED 8 / KILLED 12 (10).
- A17 counts line not last → KILLED both (1–5; +9 under 12).
- A18 extra argv accepted → KILLED both (6, `--lost-found` arm).
- A19 linked labelled main → SURVIVED both; witness linked→main.
- A20 stderr ignored except `checked()` → SURVIVED both; no discriminating witness on missing-alternate input.

Hygiene: the assigned scratch `/var/tmp/souji-r25-MutSizeCensus/` collided with a concurrent seat (L1Souji25.MutSizeCensus) at 09:29; I removed only the files I had created there, left that seat's files untouched, notified it, and re-ran everything in `/var/tmp/souji-r25-MutSizeCensus-2/`, removed at the end. Both seats target `w1/MutSizeCensus.md`; the other seat's report is at `w1/MutSizeCensus-s1.md` and this report is at the canonical path. Lane write scope: this report only.
