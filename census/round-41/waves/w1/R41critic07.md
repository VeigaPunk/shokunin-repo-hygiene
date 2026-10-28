# R41critic07 — causal separability and axis harm (round 41, wave 1)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · freeze e2a74312af4233963e44e4dbb38838ece07b8bd2 (HEAD at start) · instruments 6682b98175b995ee4646ffd1ea6bd8a12cd353dd · base 7eebc183f2685d1ea9b004b4de22c09a8a4035a7 (ancestor of HEAD: verified).

Scope: read-only attack. No candidate was landed or committed; no git/jj mutation; scoring only in scratch clones made by `score-candidate.sh` or by my own `git clone --shared`. Probe files live only under this seat directory (`probes/`). Receipts copied to `receipts/`. Scratch `/fast/scratch/hyaku/souji-r41/R41critic07` removed before yield.

## Verdict

- **Separability: PASS.** No counter reads another claim's landed file, and each counter's SUMMARY is byte-identical whether or not the other two claims' stub artifacts are present (dynamic check below).
- **Harm to owned axes: none observed** from the stubs and probes I could construct. The six PRIOR drift fixtures still pass 6/6 against the pinned tool (sha256 b2a603cf…). The tool's bytes are unchanged at HEAD. The C1 probe row passes the registry shape check and adds no registry mismatch.
- **Named couplings and limits (not failures):** the registry tool is already red at the tip (pre-existing S146 K1 defect); the SKILL.md registry convention is unmet for the r40 fixtures; R1's PRIOR set omits four drift fixtures that all pass on the pinned tool; counters run fixtures from scratch copies, which constrains candidate fixtures.
- **Not tested:** real candidates for C2 (`tools/souji-freeze-check.py`) and real C3/R1 fixtures were not built. Harm from *real* landings is unmeasured; only stubs, controls and one probe row were run.

## 1. Frozen-input integrity (pre-check)

Command: `git rev-parse 6682b98:<f>` vs `git rev-parse HEAD:<f>` for each frozen file.

```
same census/round-41/r1-counter.py
same census/round-41/c3-counter.py
same census/round-41/c2-counter.py
same census/round-41/c1-counter.py
same census/round-41/c3-sites.tsv
same census/round-41/c1-items.tsv
same census/round-41/c2-cases.tsv
same tools/souji-worktree-drift.py
```
(`census/round-41/preregistration.txt` correctly absent at 6682b98: it is added by the freeze commit e2a7431 — HEAD's parent chain contains it.)

Digests at HEAD (sha256, first 64 chars):
```
8860dc7a…  census/round-41/c1-counter.py      (pinned 8860dc7af55848db…  ✔)
85ffe263…  census/round-41/c2-counter.py      (pinned 85ffe2638a5ed0c8…  ✔)
9ef99e8f…  census/round-41/c3-counter.py      (pinned 9ef99e8f20805501…  ✔)
8352eed4…  census/round-41/r1-counter.py      (pinned 8352eed44705066d…  ✔)
4854335a…  census/round-41/c2-cases.tsv       (pinned 4854335abdd47942…  ✔)
2d2a548e…  census/round-41/c1-items.tsv       (pinned 2d2a548e253b7863…  ✔)
be363c0d…  census/round-41/c3-sites.tsv       (pinned be363c0de5d332dc…  ✔)
b2a603cf…  tools/souji-worktree-drift.py     (pinned b2a603cf42472b45…  ✔)
```

## 2. Separability — static: which files each counter reads

| counter | files read at --rev / from pinned bytes | other-claim files read? |
|---|---|---|
| C1 `census/round-41/c1-counter.py` | `census/round-41/c1-items.tsv` (pinned), `corpus/lessons/round-41.md` (its own claim), `corpus/SOURCES.md` (C1's registry row), `census/round-40/records/c1-before.txt`, `c1-after-h.txt`, `census/round-40/waves/` at MEASURED bffcc0f (see `derive()`/`MEASURED`, lines ~47-50 and derive()) | No. Its only registry dependency is the row it itself adds. |
| C2 `census/round-41/c2-counter.py` | `tools/souji-freeze-check.py` (its own claim), `census/round-41/preregistration.txt` (`PREREG_PATH`, line 77), `census/round-40/preregistration.txt` (`RETRO_PATH`, line 78); all other inputs are scratch-built synthetic repos (`build()`) | No. Reads the frozen prereg, not C1/C3 landed files. |
| C3 `census/round-41/c3-counter.py` | `tools/souji-worktree-drift.py` (pinned, `TOOL_PATH` line 45), `tests/fixtures/r41-refusal-sites.py` (its own claim, `FIXTURE_PATH` line 46), `census/round-41/c3-sites.tsv` (pinned, `SITES_PATH` line 47) | No. |
| R1 `census/round-41/r1-counter.py` | `tools/souji-worktree-drift.py` (`TOOL` line 46), `tests/fixtures/r39-…`, `r40-…` (base-frozen), `tests/fixtures/r41-drift-record-order.py` (its own claim, `F41` line 49), and the six `PRIOR` fixtures (lines 50-52) | No. PRIOR fixtures are r36-r40, all pre-round-41. |

Only shared surface: all four counters read `tools/souji-worktree-drift.py` at the pinned digest, and C3/R1 both mutate that *same* pinned source. No counter writes into the lane; each writes to `--scratch`/TMPDIR.

## 3. Separability — dynamic: cross-landing SUMMARY invariance

I ran each counter with stub artifacts for the other claims landed in the same scratch commit (score-candidate.sh accepts several `dest=src` pairs). Stubs are the frozen controls under `census/round-41/controls/`.

Commands (all run from the lane; `S=/fast/scratch/hyaku/souji-r41/R41critic07`, `TMPDIR=$S`):

```
bash census/round-41/score-candidate.sh c3 $S tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py
bash census/round-41/score-candidate.sh c3 $S tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py corpus/lessons/round-41.md=census/round-41/controls/c1-junk-round-41.md
bash census/round-41/score-candidate.sh r1 $S tests/fixtures/r41-drift-record-order.py=census/round-41/controls/r1-stub-fixture.py tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py corpus/lessons/round-41.md=census/round-41/controls/c1-junk-round-41.md
bash census/round-41/score-candidate.sh c1 $S corpus/lessons/round-41.md=census/round-41/controls/c1-junk-round-41.md
bash census/round-41/score-candidate.sh c1 $S corpus/lessons/round-41.md=census/round-41/controls/c1-junk-round-41.md tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py
bash census/round-41/score-candidate.sh c2 $S tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py
bash census/round-41/score-candidate.sh c2 $S tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py corpus/lessons/round-41.md=census/round-41/controls/c1-junk-round-41.md tests/fixtures/r41-refusal-sites.py=census/round-41/controls/c3-stub-fixture.py
```

Observed (verbatim SUMMARY lines):

| run | SUMMARY | same as alone? |
|---|---|---|
| C3 stub alone (`receipts/c3-alone.out`) | `SUMMARY sites=19 probes=21 pristine=ok killed=0 survived=19 misattributed=0 docclasses=10 site_regex=ok docclasses_match=ok tool_sha=b2a603cf4247 fixture_sha=6ed213bd68cc` | — |
| C3 stub + C2 stub + C1 junk (`receipts/c3-with-c1c2.out`) | identical line | **yes** |
| R1 base, nothing landed (`receipts/base-r1.out`) | `… PRISTINE FAIL FIXTURE-ABSENT … SUMMARY mutants=11 killed=0 survived=11 pristine=FAIL … prior=6/6 cases=0 …` | prior=6/6 reproduced |
| R1 with R1 stub + C3 stub + C2 stub + C1 junk (`receipts/r1-with-others.out`) | `SUMMARY mutants=11 killed=8 survived=3 pristine=ok regress=8/8 new_killed=0/3 old_fixtures_killed_new=0 prior=6/6 cases=8 tool_sha=b2a603cf4247 fixture_sha=4768a5d6a21a` | identical to `controls/` R1 stub line |
| C1 junk alone (`receipts/c1-junk-ref.out`) | `SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0` | — |
| C1 junk + C2 stub + C3 stub (`receipts/c1-with-c2c3.out`) | identical line | **yes** |
| C2 stub alone (`receipts/c2-stub.out`) | `SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5ccb4fb2705b` | — |
| C2 stub + C1 junk + C3 stub (`receipts/c2-with-c1c3.out`) | identical line | **yes** |

The stubs reproduce the frozen do-nothing controls exactly (e.g. C2 stub `pass=2 fail=19`, C1 junk `junk=3`, R1 stub `killed=8 survived=3`), so the controls are the same values the counters produce in isolation. Other claims' landings do not change any counter's verdict. (Stub-level values only; real-candidate invariance not measured.)

## 4. Harm — the six PRIOR fixtures against the pinned tool

Pristine = `git show HEAD:tools/souji-worktree-drift.py` (sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6, matches `PRISTINE_SHA256`). Fixtures run as `python3 -B <fixture> --tool <pristine> --work <dir>`, each in its own work dir, outputs in `receipts/`.

```
r36-worktree-drift            rc=0  SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED   traceback=0
r37-drift-discrimination      rc=0  SUMMARY cases=6 pass=6 fail=0                            traceback=0
r38-drift-record              rc=0  SUMMARY cases=10 pass=10 fail=0                           traceback=0
r38-drift-write-envelope      rc=0  SUMMARY cases=12 pass=12 fail=0                           traceback=0
r39-drift-record-rules        rc=0  SUMMARY cases=7 pass=7 fail=0                             traceback=0
r40-drift-record-branches     rc=0  SUMMARY cases=8 pass=8 fail=0                             traceback=0
```

Also the counter's own PRIOR step (via `score-candidate.sh r1`, nothing landed): `prior=6/6`. No harm from the pinned tool's side.

## 5. Harm — drift fixtures outside PRIOR (coverage gap in the frozen regression set)

`SKILL.md:248-283` registers drift fixtures that are not in `census/round-41/r1-counter.py` PRIOR (lines 50-52). Four further drift fixtures exist in the lane; I ran them against the pinned tool:

```
r37-drift-escapes     --tool pristine --base-tool <git show 5f0dd45:tools/…>  rc=0  SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
r37-drift-mutants     --tool pristine --fixture tests/fixtures/r37-drift-discrimination.py   rc=0  SUMMARY mutants=6 killed=6 survived=0
r38-drift-mutants     --tool pristine --fixture r38-drift-record.py --base-fixture r37-drift-discrimination.py  rc=0  SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0
r40-docstring-joined  --tool pristine --analyzer census/round-40/docstring-classes.py (copied from HEAD)  rc=0  SUMMARY cases=9 pass=9 fail=0
```
Note: my first `r37-drift-mutants` and `r40-docstring-joined` invocations used wrong arguments (fixture = the mutants file itself; analyzer defaulting from a copied location) and returned rc=2 or 1; both were my invocation errors and were rerun correctly above. The `r40-docstring-joined` default analyzer resolves via `os.path.dirname(__file__)/../..` (line 104), so it works only when run inside the lane.

Result: no harm on the pinned tool, but R1's `prior=6/6` does not cover these four. That is a named limit of R1's regression set; it is not an edit target (the PRIOR list is frozen).

## 6. Harm — registry axis (C1 row and lesson)

Registry tool: `tools/souji-registry-agreement.py` (K1 registry<->entry; K2 stale statements). Its `--list-rev` must be the round-29 prereg commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (the commit that adds `census/round-29/records/frozen-digests.txt`; the tool's K2 `facts()` runs the frozen r29 counter there). Using HEAD as list-rev returns rc=2 `derived facts are trivial`; that was my first error, corrected below.

Baseline at HEAD (`receipts/regagree-baseline.out`):
```
$ python3 -B tools/souji-registry-agreement.py --root <lane> --rev e2a74312af4233963e44e4dbb38838ece07b8bd2 --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
SUMMARY k1=1 k2=0 mismatches=1 rev=e2a74312af4233963e44e4dbb38838ece07b8bd2
rc=1
```
**Pre-existing red at the tip, not caused by round 41.** A knowledge entry cites S146, which has no SOURCES row. Round-41 must not be credited for, or blamed for, this line.

C1 probe (my construction, under `probes/`): I added row S258 (13-field line, `used-by` = `corpus/lessons/round-41.md`, tier A, status `mined`, opened 2026-10-28, source `git v2.56.0 builtin/worktree.c`) to a copy of SOURCES.md, and a four-line `corpus/lessons/round-41.md` with three `CORRECTION` lines carrying the counter's own derived values and `source=S258` on I1. Committed in a `git clone --shared` scratch clone; then ran both frozen counters:

```
$ python3 -B census/round-41/c1-counter.py --root <clone> --rev <probe> --scratch <S>     (rc=0)
ITEM I1 present mismatch=yes derived=rows=2,v2.56.0=0 corrections=1 intact=yes
ITEM I3 present mismatch=yes derived=before=6,after=3 corrections=1 intact=yes
ITEM I4 present mismatch=yes derived=occurrences=0 corrections=1 intact=yes
SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
$ python3 -B tools/souji-registry-agreement.py --root <clone> --rev <probe> --list-rev b8cb4b31…  (rc=1)
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
SUMMARY k1=1 k2=0 mismatches=1
```
Findings:
- The C1 row adds **zero** new K1 mismatches (count stays at the one pre-existing S146 line). The row passes the 13-field check (`tools/souji-registry-agreement.py` `registry()`: `if len(c) != 13` → RuntimeError exit 2; a malformed C1 row would turn the whole tool into rc=2, not a finding). The counter's `sourced()` needs 11 cells, which the probe satisfies.
- The K1 `used-by-no-cite` check requires the lesson to contain the row id: the `source=S258` token is what satisfies it. A C1 landing that cites S258 in the row but omits it from the lesson would turn K1 red.
- The C1 counter accepts any CORRECTION line whose four fields equal the counter's own derived strings. This is correct by its spec ("carrying the counter's own re-derived value") but it means the calibration target measures echo-format, not prose quality. Limit, not defect.

## 7. Harm — SKILL.md registry convention (C2/C3/R1 landing)

- `SKILL.md:254` (`souji-worktree-drift` row) lists exactly the ten refusal classes in the tool docstring (`tools/souji-worktree-drift.py` header, the "Exit" block). Neither C3 nor R1 changes the tool; the row stays accurate.
- `SKILL.md:283` (R39-C1-06) records that four r38 gate fixtures had no registry row and were fixed by adding rows. **The same defect recurs for round 40:** `grep -c "r40-" SKILL.md` = 0; `r40-drift-record-branches.py`, `r40-docstring-joined.py`, `r40-c1-evidence.py` all have 0 SKILL rows. No enforcing gate was found (`grep` of tools/ and tests/ for SKILL registry checks returns only the landing gate's citation-existence check, `LG-MISSING-REG`, which checks citations *in* SKILL.md, not completeness). So landing C2's `tools/souji-freeze-check.py`, C3's fixture or R1's fixture without SKILL rows would repeat R39-C1-06 without a red check. Prospective convention harm; the L1 decides whether to add rows.

## 8. Harm — C2 tool placement and fixture-execution constraints

- **C2 tool landing:** no tool enumerates `tools/`. Searched: `os.listdir`/`sorted(os.listdir(...))` appear only in `tools/souji-size-census.py:176` (a pack dir), `tools/souji-worktree-drift.py` `discover()` (a measured root, not tools/), and `tests/runner-31.sh:526-529` (tests/fixtures listing). `tools/souji-landing-gate.py` checks SKILL.md citations, not the set of tool files. **No harm found** from adding `tools/souji-freeze-check.py`.
- **C3 / R1 fixture landing:** `tests/runner-31.sh:526-529` snapshots the `tests/fixtures` listing into `tests/results/runner-31.json` (`fixture_inventory_tests_fixtures_dir`) on each rerun. The committed `tests/results/runner-31.json` changes only when that runner is rerun; no gate reads it (I did not rerun runner-31). `tests/fixtures/.gitignore` ignores only `tests/fixtures/*/repo/` and `tests/fixtures/*/*/repo/`, so the new fixture names are not ignored. **No harm found.**
- **Fixture execution constraint (operability):** both counters execute fixtures from *scratch copies* (C3: `fixture.py` in scratch, line ~116; R1: `local[path]` copies, lines ~167-172). A candidate fixture that resolves lane files through `__file__` (as `tests/fixtures/r40-docstring-joined.py:104` and the PRIOR fixtures' `lane_root` at r36:133 / r40:131 do) will fail when run from a copy unless the path is passed explicitly. The PRIOR copies still pass 6/6 because the counter passes `--tool` (the `lane_root` fallback is never taken for `--tool`). A C3 or R1 candidate that reads `census/round-41/c3-sites.tsv` or its own location by `__file__` would be scored wrong. Constraint: candidate fixtures must take every lane path explicitly or be self-contained.

## 9. Commands actually run (exact)

All ran with `TMPDIR=/fast/scratch/hyaku/souji-r41/R41critic07`, lane cwd, python3 -B. Nothing was installed.

1. `git rev-parse HEAD`, `ls census/round-41/`, `cat preregistration.txt`, `cat` of r1/c3/c2 counter specs.
2. `git rev-parse 6682b98:<f>` vs `HEAD:<f>` for eight frozen files (table §1).
3. `sha256sum` of counter/population/tool files (§1).
4. `git merge-base --is-ancestor 7eebc18… HEAD` → ok; `git merge-base --is-ancestor bffcc0f… HEAD` → ok.
5. Extraction of PRIOR fixtures from HEAD into scratch; `python3 -B <fixture> --tool <pristine> --work <dir>` for the six PRIOR fixtures (§4).
6. `bash census/round-41/score-candidate.sh r1 $S` (nothing landed) → `prior=6/6`.
7. Cross-landing runs (§3), seven `score-candidate.sh` invocations.
8. `git grep` for `souji-worktree-drift`, `r40-` in SKILL.md, `grep` for `listdir|glob|iterdir|os.walk` in tools/tests.
9. `python3 -B tools/souji-registry-agreement.py --root <lane> --rev HEAD --list-rev HEAD` → rc=2 (`derived facts are trivial`); corrected to `--list-rev b8cb4b31…` → rc=1, `K1 cited-no-row S146` (§6).
10. C1 probe: `git clone -q --shared` to scratch, `cp` probe SOURCES.md and lesson, `git commit` (identity via GIT_*_NAME/EMAIL env only), `c1-counter.py` rc=0 SUMMARY `corrected=3 sourced=1`, `souji-registry-agreement.py` rc=1 mismatches=1 (§6); clone removed.
11. Four unlisted drift fixtures (§5) with `--tool <pristine>`; rc=0 for three; r40-docstring-joined rerun with `--analyzer` (rc=0 `pass=9`).
12. `git show HEAD:tests/fixtures/<f>.py | grep -n __file__ / lane_root` for PRIOR (§8).
13. `git status --porcelain` at lane: empty (seat outputs are under the git-ignored `.ufo/waves/`).

No `git commit`, `git add`, `jj`, `git config`, or write to tests/, tools/, census/, corpus/, SKILL.md or any tracked file. Scratch removed (`rm -rf` after receipts were copied).

## 10. Receipts (in this seat directory)

`.ufo/waves/round-41/w1/R41critic07/receipts/`: `base-r1.out`, `c3-alone.out`, `c3-with-c1c2.out`, `r1-with-others.out`, `c1-probe.out`, `c1-junk-ref.out` (not copied; the same line is in the `c1-with-c2c3.out` receipt), `c1-with-c2c3.out`, `c2-stub.out`, `c2-with-c1c3.out`, `regagree-baseline.out`, `regagree-probe.out`, `r36-worktree-drift.out`, `r37-drift-discrimination.out`, `r38-drift-record.out`, `r38-drift-write-envelope.out`, `r39-drift-record-rules.out`, `r40-drift-record-branches.out`, `r37e.out`, `r37m.out`, `r38m.out`, `r40dj.out`.
Probe candidates: `.ufo/waves/round-41/w1/R41critic07/probes/SOURCES.md` (the base registry plus S258 row) and `probes/round-41.md` (four-line lesson). Neither is a landing candidate for the L1; they exist to evidence §6.

## 11. Findings for the L1 (named limits, no frozen-file edit proposed)

1. Pre-existing registry red at the tip: K1 `cited-no-row S146` (`corpus/knowledge/origin-record-format-gvfs-r40.md`). Not a round-41 claim; the L1 should report it as is.
2. R1's PRIOR set omits `r37-drift-escapes`, `r37-drift-mutants`, `r38-drift-mutants`, `r40-docstring-joined`; all pass on the pinned tool today. Named limit.
3. R40 gate fixtures and (prospectively) C2/C3/R1 artifacts lack SKILL.md rows; R39-C1-06 convention unmet at round 40 (`SKILL.md:283`).
4. Candidate fixtures for C3/R1 must not resolve lane paths from `__file__` (both counters run scratch copies).
5. The C1 target accepts any CORRECTION line that echoes the counter's derived value; calibration is measured as format plus echo, by the frozen design.

## Verdict (restated)

Separability: **PASS** — each counter verifies on the instruments and its own artifact alone; cross-landing SUMMARY lines unchanged (§3). Harm to owned axes: **none observed** on the pinned tool (§4), registry (§6: C1 probe adds zero mismatches), or tool enumeration (§8); the named couplings and limits in §11 are reported, not edited. Scope note: real C2/C3/R1 candidates were not built, so real-landing harm is unmeasured.
