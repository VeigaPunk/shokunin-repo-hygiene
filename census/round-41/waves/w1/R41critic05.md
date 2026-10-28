# R41critic05 — attack on census/round-41/r1-counter.py (R1 residual)

Seat: R41critic05 (critic, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, freeze e2a74312af4233963e44e4dbb38838ece07b8bd2.
Frozen inputs verified: `census/round-41/r1-counter.py` sha256 8352eed44705066de36f8775ca421f5325820d5856b25d08d3daab7a63c60556 (= preregistration line 50); pinned tool `tools/souji-worktree-drift.py` sha256 b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 (= PRISTINE_SHA256); base tool `git show 7eebc183f2685d1ea9b004b4de22c09a8a4035a7:tools/souji-worktree-drift.py` sha256 e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76. Interpreter: Python 3.14.8. No installs. No lane, fleet or sibling write; no git mutation. Scratch: /fast/scratch/hyaku/souji-r41/R41critic05/ (removed before yield).

## Verdicts

| # | Question | Verdict |
|---|----------|---------|
| Q1 | Is M19 (`for total in totals[-1:]`) the base tool's behaviour? | **Confirmed.** Semantically identical to base; 150/150 random differential agreement with base. |
| Q2 | Are M20/M21 equivalent mutants under some fixture design? | **Not equivalent in general. Equivalent only under fixtures whose `--root` has no `.git` directory** (plain root: 0 differences in 73/73 cases each). Under a `.git`-directory root they are killable and the probe kills them. |
| Q3 | Does `old_fixtures_killed_new=0` hold for M19-M21 against committed r39/r40? | **Confirmed.** Neither r39 nor r40 kills any of M19, M20, M21 (rc 0, every case passes). |
| F1 | Counter docstring "killed ... by the r40 fixture alone" is not enforced | **Finding (low).** Code checks only the owner fixture; a candidate that also kills M16/M18 is not penalised. Counter-side defect, named limit; not edited. |

## Q1 — M19 is the base behaviour

Textual (base 7eebc18, lines 164 and 169):
```
164:            total = {"repos": int(m.group("repos")), ...}      # overwritten on every TOTAL row
169:    if total is not None:                                       # checks only the LAST TOTAL
```
Base keeps only the last TOTAL and checks it. Pinned pristine (lines ~174-181) iterates `for total in totals:`; M19 replaces it with `for total in totals[-1:]:`, which checks the same single (last) value. Return value: pristine returns the same last `total` in both. Empty totals: base skips, M19 loops zero times; identical.

Differential (`.ufo/waves/round-41/w1/R41critic05/diff-driver.py`, run as `python3 -B diff-driver.py 150` in scratch, mutants built with the counter's own `MUTANTS` anchors, anchors each `count=1`):
```
AGREE M19 vs_base same=150 differ=0
AGREE pristine vs_base same=86 differ=64
```
(150 random records over a plain and a git-root fleet, 0–3 TOTAL rows in random positions, random `--skip-unrecorded`; full stdout+stderr+rc compared. The `pristine vs_base` line reflects the R40-D-TOTAL defect that M19 reintroduces.)

Probe arm `total-first-disagrees-last-agrees` (record = ROWS + `TOTAL repos=1 regs=2` + `TOTAL repos=2 regs=2`):
```
== base 7eebc18 tool on probe   -> case-total-first-disagrees-last-agrees=FAIL rc=0 want=2 (accepted)
== M19 mutant on probe          -> case-total-first-disagrees-last-agrees=FAIL rc=0 want=2 (accepted)
== pristine on probe            -> case-total-first-disagrees-last-agrees=PASS (refused RECORD-MALFORMED)
```
So M19 is exactly the base defect that R40-D-TOTAL names.

## Q2 — M20 / M21 equivalence

Pristine root-discovery (`discover`, line ~ `if os.path.isdir(os.path.join(root, ".git")):`) and root fallback (`repo_path`, `if name == basename(root) and isdir(root/.git)`) both gate on `root/.git` being a **directory**. Consequence:

- M20 (`if False:` on discovery) and M21 (`if False:` on fallback) change nothing when `--root` has no `.git` directory (plain dir, or `.git` file).
- They change behaviour when `--root` is a git work tree with a `.git` directory.

Differential split by root kind (same 150 records, `diff-driver.py` per-kind variant):
```
AGREE M20@plain   vs_pristine same=73 differ=0     AGREE M21@plain   vs_pristine same=73 differ=0
AGREE M20@gitroot vs_pristine same=74 differ=3     AGREE M21@gitroot vs_pristine same=56 differ=21
```
(Output of the earlier run is in the same driver; the two runs match on the gitroot rows.)

Probe (`.ufo/waves/round-41/w1/R41critic05/r41-drift-record-order.probe.py`, sha256 30d71d0d2bf8984dbf632feaa9baf63e88a2ea78cf717856b197514ff977f6df) kills both on a git-root arm:
- `root-unrecorded` (git root `fleet-repo`, record names only alpha/beta, no skip): pristine rc 1 with `UNRECORDED fleet-repo`; M20 rc 0 → killed.
- `root-basename-recorded` (record `REPO fleet-repo` + matching TOTAL, `--skip-unrecorded`): pristine rc 0; M21 reports ABSENT rc 1 → killed.
- `plain-root-basename-absent` (plain root, `REPO fleet-plain`): pristine ABSENT rc 1 and M21 ABSENT rc 1 → the equivalence design; this control passes for M21 by construction.

So the answer to "equivalent under some fixture design" is yes for plain-root fixtures, no for the r41 design which uses a git root. The counter's target `new_killed=3/3` is reachable and was reached (see scoring below).

## Q3 — `old_fixtures_killed_new=0`

Matrix (`.ufo/waves/round-41/w1/R41critic05/matrix-driver.py`, run via the counter's own `run()`/`killed()`; receipt `score-r1-probe.txt` and matrix output below). Pristine:
```
PRISTINE
  r39 rc=0 cases=7 pass=7 fail=0 crash=False failing=- clean=True
  r40 rc=0 cases=8 pass=8 fail=0 crash=False failing=- clean=True
  probe rc=0 cases=6 pass=6 fail=0 crash=False failing=- clean=True
MUTANT M19 owner=r41-drift-record-order.py  r39:killed=False(rc=0,failing=-)  r40:killed=False(rc=0,failing=-)  probe:killed=True(rc=1,failing=total-first-disagrees-last-agrees)
MUTANT M20 owner=r41-drift-record-order.py  r39:killed=False(rc=0,failing=-)  r40:killed=False(rc=0,failing=-)  probe:killed=True(rc=1,failing=root-unrecorded)
MUTANT M21 owner=r41-drift-record-order.py  r39:killed=False(rc=0,failing=-)  r40:killed=False(rc=0,failing=-)  probe:killed=True(rc=1,failing=root-unrecorded,root-basename-recorded)
```
M19 is not caught by r40's `total-conflicting-second` arm (there the last TOTAL disagrees, so the mutant refuses too; r40's arm kills M15, not M19). No r39/r40 arm has a first-disagreeing, last-agreeing pair. `old_fixtures_killed_new=0` holds.

Full matrix for the retained mutants (same run; `killed` is the counter's criterion):
```
M11 r39:killed=True  r40:False  probe:False
M12 r39:killed=True  r40:False  probe:False
M13 r39:killed=True  r40:False  probe:False
M14 r39:killed=True  r40:False  probe:False
M15 r39:False  r40:killed=True  probe:False
M16 r39:False  r40:killed=True  probe:killed (root-unrecorded-skipped, root-basename-recorded)
M17 r39:False  r40:killed=True  probe:False
M18 r39:False  r40:killed=True  probe:killed (total-first-disagrees-last-agrees)
```

## Scoring the probe with the frozen counter (advice only; the L1 measures)

Command (read-only on the lane; clone in scratch, trap-removed):
```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh r1 /fast/scratch/hyaku/souji-r41/R41critic05 tests/fixtures/r41-drift-record-order.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41critic05/r41-drift-record-order.probe.py
```
Output (SCORE_EXIT=0), receipt `.ufo/waves/round-41/w1/R41critic05/score-r1-probe.txt`:
```
MUTANT M19 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=total-first-disagrees-last-agrees
MUTANT M20 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=root-unrecorded
MUTANT M21 owner=r41-drift-record-order.py killed=yes by=r41-drift-record-order.py failing=root-unrecorded,root-basename-recorded
SUMMARY mutants=11 killed=11 survived=0 pristine=ok regress=8/8 new_killed=3/3 old_fixtures_killed_new=0 prior=6/6 cases=6 tool_sha=b2a603cf4247 fixture_sha=30d71d0d2bf8
```
Note: the first scoring of an earlier 5-case version gave `pristine=FAIL ... cases=5` because the counter requires `cases >= 6`; a 6th control (`root-unrecorded-skipped`) was added. That is the counter's own minimum, not a defect.

## F1 — docstring "alone" is not enforced (counter-side, named limit)

`census/round-41/r1-counter.py` docstring: "Retention: M11-M14 must be killed by the r39 fixture alone and M15-M18 by the r40 fixture alone." Code: `regress += 1 if owner_kills` only. Evidence: the probe above kills M16 and M18 as well (`by=r40-drift-record-branches.py,r41-drift-record-order.py`), and the counter still reports `regress=8/8` and exit 0. The committed r39/r40 fixtures do satisfy "alone" (matrix above), so the stated property holds for the frozen fixtures but is not checked. Severity: low; it does not change any target. Routed to the L1 as a counter doc/code mismatch; not edited (frozen).

## Other checks (negative results)
- Anchors: every mutant anchor occurs exactly once in the pinned tool (`count=1` for M11-M21).
- Counter return value for M19: pristine and M19 both return the last TOTAL; no extra difference observed.
- No `crash=True` for any r39/r40/probe run; no traceback-driven kills.

## Commands actually run (summary)
1. `git -C LANE show 7eebc18…:tools/souji-worktree-drift.py` (base) and `sha256sum`; `grep -n` on base/pristine totals logic.
2. `git -C LANE archive e2a7431 tools/... tests/fixtures/r39-... tests/fixtures/r40-... census/round-41/r1-counter.py | tar -x -C scratch` (read-only).
3. `python3 -B matrix-driver.py` (imports the frozen counter's MUTANTS/run/killed) — output above, exit 0.
4. `python3 -B diff-driver.py 150` (and per-kind variant) — output above.
5. `bash census/round-41/score-candidate.sh r1 <scratch> tests/fixtures/r41-drift-record-order.py=<probe>` — SUMMARY above, exit 0.
6. `python3 -B r41-drift-record-order.probe.py --tool {base-tool.py | M19.py | pristine} --work <scratch>/tmp` — outputs above.

Receipts in this seat directory: `matrix-driver.py`, `diff-driver.py`, `r41-drift-record-order.probe.py`, `score-r1-probe.txt`.

## Limits
- The probe is advice; the L1 measures. The probe does not replace the R1 candidate's landed fixture.
- Differential sample is 150 random records (fixed seed 41); the M19 claim rests on the textual argument plus the sample.
- M20/M21 equivalence is stated for `--root` without a `.git` directory (`.git` file case not separately run).
