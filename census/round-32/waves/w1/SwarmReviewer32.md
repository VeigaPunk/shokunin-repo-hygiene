# SwarmReviewer32 — C2 base readings re-derived without the counter (souji r32 w1)

## Status
STATUS: PASS — all five sampled C2 items' base readings independently reproduced without the counter; counter agreement is exact on exit code and summary line (5/5) and on W for 3/5 (T11/T19 within observed noise of ±7/±1); the sandboxed base run fails for every item exactly as the base defect predicts; the half-of-base work rule returns the same verdict across two base runs for every item.

## Evidence

Setup (all under `/fast/scratch/hyaku/souji-r32/ReDeriveC2Base/`, removed after the run):
- `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin .../c && git -C .../c remote remove origin`; `git -C .../c rev-parse --show-toplevel` printed `.../c`; detached at `85b61a151923986e7e6b48f7084b9122561b5f3d` (`git log -1`: `85b61a151923986e7e6b48f7084b9122561b5f3d round-31 verifier spot-check (integrator, hyaku): non-author admit/reject`); `git status --porcelain` empty before runs.
- bwrap 0.13.1, strace 7.2, git 2.56.0, python 3.14.8. No tools installed or upgraded (none needed).
- Independent script `.../rederive.py` re-implements the frozen spec from the counter docstring — census/round-32/c2-counter.py:16 "S = last digit-bearing line of normalized stdout" and :21 "SBOX's W is at least half of BASE's W" — and does not import or invoke the counter for these numbers. Item argv taken from the frozen blob `3ec84fc81b3243429c834a051880b0bcde06291c:census/round-32/c2-items.tsv` (T01 :14, T04 :17, T11 :24, T19 :30, T26 :37). Each run: fresh `git checkout -qf --detach <base>` + `git clean -fdxq`, env `TMPDIR=<t1|t2>` `GIT_CONFIG_NOSYSTEM=1`, `GIT_DIR`/`GIT_WORK_TREE` unset, traced with `strace -f -qq -o <log> -e trace=mkdir,mkdirat,creat,open,openat,openat2`; the bwrap leg wraps strace inside `bwrap --dev-bind / / --ro-bind <empty 0555> /tmp --ro-bind <empty 0555> /var/tmp --ro-bind <empty 0555> /dev/shm --chdir <clone>`.

Base readings, four independent samples per cell (mine pass 1 / pass 2, counter run A / run B; rev=base so the counter's SBOX leg is itself a base run):

| item | plain rc | plain S (last digit-bearing line) | plain W samples | bwrap rc | bwrap S | bwrap W |
|---|---|---|---|---|---|---|
| T01 | 0 ×4 | `SELFTEST pass=65 fail=0` | 8306, 8306, 8306, 8306 | 1 ×4 | `OSError: [Errno 30] Read-only file system: '<TMP>'` | 0 ×4 |
| T04 | 0 ×4 | `selftest=8/8` | 87, 87, 87, 87 | 1 ×4 | `OSError: [Errno 30] Read-only file system: '<TMP>'` | 0 ×4 |
| T11 | 0 ×4 | `selftest=PASS ids=7/7` | 537, 535, 540, 538 (+ probe 533, 537) | 2 ×4 | `id=SOUJI-R13-STRUCT-SETUP error=mktemp failed under /var/tmp` | 2 ×4 |
| T19 | 0 ×4 | `cases=8 pass=8 refusals=2/2 regress=5/5` | 154, 155, 154, 155 (+ probe 154, 154) | 1 ×4 | `cases=8 pass=0 refusals=0/2 regress=0/5` | 0 ×4 |
| T26 | 0 ×4 | `cases=4 pass=4 control=FALSE-GREEN-REJECTED` | 537, 537, 537, 537 | 1 ×4 | NONE (stdout has no digit line; stderr mktemp line has none either) | 0 ×4 |

Raw failing lines captured at base (unnormalized): T01/T04 `OSError: [Errno 30] Read-only file system: '/var/tmp/souji-landing-gate-selftest-zqlncudi'` / `'/var/tmp/souji-declared-evidence-t634xlai'`; T26 `mktemp: failed to create directory via template '/var/tmp/souji-r27-pre-report.XXXXXX': Read-only file system`.

Counter invocation (run twice, A and B):
`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 85b61a151923986e7e6b48f7084b9122561b5f3d --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T01,T04,T11,T19,T26 --scratch /fast/scratch/hyaku/souji-r32/ReDeriveC2Base/cnt`

Run A excerpt (run B identical except T11 W 538, T19 W 155):
```
ITEM	T01	FAIL	base=rc0:W8306:SELFTEST pass=65 fail=0	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
ITEM	T04	FAIL	base=rc0:W87:selftest=8/8	sbox=rc1:W0:OSError: [Errno 30] Read-only file system: '<TMP>'	regress work-dropped
ITEM	T11	FAIL	base=rc0:W540:selftest=PASS ids=7/7	sbox=rc2:W2:id=SOUJI-R13-STRUCT-SETUP error=mktemp failed under /var/tmp	regress work-dropped
ITEM	T19	FAIL	base=rc0:W154:cases=8 pass=8 refusals=2/2 regress=5/5	sbox=rc1:W0:cases=8 pass=0 refusals=0/2 regress=0/5	regress work-dropped
ITEM	T26	FAIL	base=rc0:W537:cases=4 pass=4 control=FALSE-GREEN-REJECTED	sbox=rc1:W0:NONE	regress work-dropped
SUMMARY items=5 pass=0 fail=5 partial=1 rev=85b61a151923986e7e6b48f7084b9122561b5f3d
```

Agreement per item (my re-derivation vs counter, both passes):
- T01 exact (rc, S, W=8306 both sources both passes); T04 exact (W=87); T26 exact (W=537).
- T11: rc and S exact; W differs within noise — mine 537/535, counter 540/538.
- T19: rc and S exact; W differs within noise — mine 154/155, counter 154/155.
- SBOX leg (rev=base): exact agreement on rc, S and W for all five items, both passes.

Nondeterminism: exit code and summary line never varied (0 variance over 4+ samples per item per leg). W varies mildly: T11 533–540 over six base samples (spread 7, ≈1.3%), T19 154–155 (spread 1, ≈0.6%), T01/T04/T26 constant. Composition diff of counted strace lines between two T11 plain runs shows the drift sits in git's own scratch-repo internals — e.g. `mkdir(".git/logs/refs", 0777)` plus the `.git/logs/refs/heads/master` reflog append present in one run and absent in the other, `.git/index.lock` and sample-hook creations differing — not in the lane tools' own file work [INFERENCE on cause: git init/clone internals; the lane-side calls were not bisected].

Half-of-base rule stability across two base runs: rule is `W_sbox*2 >= W_base` (census/round-32/c2-counter.py:21). Observed W_sbox constant per item (0, 0, 2, 0, 0); W_base ranges as tabled. Worst margin is T11: 4 vs ≥533 (margin ≥529 creations); all others are 0 vs ≥87. No verdict can flip under the observed variance; the rule's outcome is identical for both base runs of every item. Scope note: with `--rev` = base this validates the instrument's BASE leg and sandbox mechanics only; the patched-tool SBOX outcome at the real REV is out of my seat's scope.

## Findings
1. Base defect independently reproduced for all five items (census/round-32/c2-items.tsv:14,17,24,30,37): plain runs pass at base with a digit-bearing anchor; sandboxed runs fail — T01/T04 crash with `OSError: [Errno 30] Read-only file system` on a literal `/var/tmp/...` mkdtemp (tools/souji-landing-gate.py, tools/souji-declared-evidence.py), T11 exits 2 with `mktemp failed under /var/tmp` (tools/souji-repo-structure.sh via tests/fixtures/r13-repo-structure.sh), T19 does zero work (`pass=0`, W=0; tools/souji-receipt-run.py via tests/fixtures/r24-receipt-verify.py), T26 dies in mktemp with no digit-bearing line (tests/fixtures/r27-pre-report-gate.sh). Consistent with the preregistration's base reading (26/27 FAIL).
2. Counter base readings verified against an independent implementation: exact on rc and S for 5/5 items and on W for 3/5; W deltas (T11 ≤7, T19 ≤1 over six samples) are measurement noise from git's scratch-repo internals, not instrument error — both sources sampled overlapping ranges.
3. Half-of-base work rule is stable for this set (margins ≥529 creations). Robustness note, general case: an item whose base W is single-digit could in principle flip the rule on ±few noise; not reachable here (minimum base W in this set is 87) [INFERENCE — only these five items sampled].
4. Observation, not mine: the lane work tree at HEAD `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` holds one untracked file, `census/round-32/measure.sh` (`git status --porcelain`). I created nothing in the lane outside this report.

## Attack log
None filed. No counter predicate in my scope was found wrong or gameable: the W noise is bounded at ≈1.3% against a 50% threshold and cannot flip any of the five verdicts. If the L1 wants extra strictness, taking W_base as the median of the two runs would remove even that noise — stricter-only, L1's call, not proposed as a change.

## Deliveries
- `.ufo/waves/round-32/w1/SwarmReviewer32.md` — this report (only file written inside the lane).
- Scratch `/fast/scratch/hyaku/souji-r32/ReDeriveC2Base/` removed after writing; nothing delivered from it.
