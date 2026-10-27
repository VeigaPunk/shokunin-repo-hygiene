# SwarmExecutor05 — r34 w1, C1 slice 5/12 (G23, G24, G26, E01, E04)

## Status

STATUS: PARTIAL — 4 of 5 items resolved (G26, E01, and restated G23/E04 all engine-validated AGREE); G24 cannot reach AGREE under the frozen bytes (item `at` predates the row's own script and its `exit` cell contradicts its own predicate) and is reported as ATTACK A3 with no row.

## Evidence

Base do-nothing reading, one flocked run of the frozen counter (loadavg before `2.84 2.72 1.92`, after `4.43 3.07 2.04`):

```
flock …/cnt.lock python3 -B <lane>/census/round-34/c1-counter.py --root <lane> \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s5/cnt --only G23,G24,G26,E01,E04
ITEM	G23	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=4.29
ITEM	G24	MISMATCH	original	rc=2 expect_exit=0 predicate fails last=python3: can't open file '/fast/scratch/hyaku/souji-r34/RestateC1s5/cnt/c1.tal5l_x8/G24.icwibca2/c/tools/souji-capability-agreement.py': [Errno 2] No such file or directory load=4.29
ITEM	G26	AGREE	original	rc=0 expect_exit=0 predicate holds last=RESULT step=8-control-expire-now keep_refs=6 object_present=yes note=target_keep=no cmd=jj-util-gc-expire-now load=4.29
ITEM	E01	AGREE	original	rc=0 expect_exit=0 predicate holds last=assertions=63 resolved=63 skipped=40 mismatches=0 load=4.43
ITEM	E04	MISMATCH	original	rc=1 expect_exit=2 predicate fails last=SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61 load=4.43
SUMMARY items=5 agree=2 mismatches=3 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
```

Engine validation of my two proposed rows, in a scratch clone of the lane tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c` with only the `### Round 34 registry restatements` section appended (scratch commit `f305fa275999e73d3122511f31cd1662ff75f084`, loadavg `54.23 34.32 16.93`):

```
ITEM	G23	AGREE	restated	rc=1 expect_exit=1 statement is the run's last digit-bearing line last=SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba load=55.63
ITEM	G24	MISMATCH	restated	rc=2 expect_exit=1 statement is not the run's last digit-bearing line last=python3: can't open file '/fast/scratch/…/c/tools/souji-capability-agreement.py': [Errno 2] No such file or directory load=55.82
ITEM	E04	AGREE	restated	rc=1 expect_exit=1 statement is the run's last digit-bearing line last=SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61 load=55.82
SUMMARY items=3 agree=2 mismatches=1 restated=3 partial=1 rev=f305fa275999e73d3122511f31cd1662ff75f084
```

Executed cause walks (one fresh clone per commit, fresh TMPDIR, `PATH` = one `jj` symlink dir + `/usr/bin:/bin`, `GIT_CONFIG_NOSYSTEM=1`, `toplevel == clone` asserted; per-run 1-min loads 10.5–55.8, `load=` on every ITEM line):

* G23 cause `1dc678500c92164b0b2bea82b934dd03d1dfbf38` (parent `b86200714069022954a3b498cf697d894119b45e`): `rc=0`, `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0 rev=1dc6785…` → the frozen predicate already failed at the commit that wrote the row's line (first introducer over all 36 SKILL.md commits).
* G23 at `4d9bf0256f6f61a49ebfec55a524556090015f60`: `rc=0`, `manifests=7 failed=0 uncovered=0 floor_violations=0` → the frozen original HOLDS there (why `4d9bf02` is refused as cause).
* G23 at the true drift `d65a5c4328896742d2ec951f7156c6a70aa9325a` (adds the 8th `waves/manifest.sha256`): `rc=0`, `manifests=8 … uncovered=0`; parent `4d9bf02` holds, cause fails.
* G23 residual `uncovered=1` = `census/round-33/waves/w1-results.json`, added at `af7fd250c8a862130f88b8f77ad29debf343e54d` after that manifest captured 89 records (manifest blob vs `git ls-tree -r 9c76c72 census/round-33/waves`).
* E04 at `de478b48…` (row's measured rev) and at cause `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` (parent `de478b48` lacks the row's line; first introducer over all 73 SCORECARD commits): `rc=2`, `SUMMARY findings=0 checked_reg=52 … checked_reports=0` **plus a stderr `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-28/ at de478b48…`**, which the counter's `stdout+stderr` ordering reads as the last digit-bearing line.
* E04 at parent `7b16731fcd8ab9b95220b50603314aa8dc92b2ec` → same `rc=2` + warning; at drift `68447afef62e4761249af55a2467657f04046537` → `rc=1`, `findings=19 … checked_reports=61`; at base → identical `rc=1` line.
* G24: `git cat-file -e 9420341d…:tools/souji-capability-agreement.py` → absent (introduced at `d4928ec86b667e3d1ed0adb07fb088e500cf1631`, amended at `02aea483b4366da8705342657995a310cd21a708`); the row's own argv run where the script exists (base clone, load 15.69) → `rc=1`, `SUMMARY k1=12 k2=0 mismatches=12 rows=18 pointers=10 rev=9420341d…`.

`grep -n -E '\| (G23|G24|G26|E01|E04) \|'`, `grep -n 'Round 34 registry restatements'`, `grep -n 'r29-c2-counter'` and `grep -n 'findings=0.*checked_reg=52'` over `git show 9c76c72:SCORECARD.md`: no prior correction, supersession or binding row exists for any of my five cells, so Q76 cannot rescue an item.

## Findings

1. G23 (`SKILL.md:247`) — MISMATCH, restatable only through the argv branch: the frozen `where` cell is one line behind the list-rev file (line 247 = `souji-wave-evidence-capture v2`, the `r29-c2-counter` row is line 248), and value drift is structurally impossible because `census/round-29/c2-counter.py` has exactly one history entry. Proposed row: exit 1, statement `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0 rev=9c76c72…`, cause `1dc6785…`, argv pinning the base rev. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md:247`.
2. G24 (`SKILL.md:249`) — MISMATCH, un-restatable: every clone is checked out at `at = 9420341d…`, which predates `tools/souji-capability-agreement.py` (`d4928ec`), so no argv naming the row's script can run; `same` also cannot hold (parent probes run at the same absent revision). Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md:249`.
3. G26 (`SKILL.md:250`) — AGREE under the frozen argv/predicate; its `where` cell is also one line behind (the `r30-jj-keep-expiry` row is line 251, line 250 is `r30-landing-gate-discovery`). No row needed. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SKILL.md:250`.
4. E01 (`SCORECARD.md:14`) — AGREE at base (`assertions=63 resolved=63 skipped=40 mismatches=0`, rc 0), where cell correct. No row.
5. E04 (`SCORECARD.md:21`) — MISMATCH, value drift at `68447af` (r30 gate rewrite, touches `tools/souji-landing-gate.py`); the `same` branch is blocked because the pre-r30 gate's warning lands on stderr and becomes the counter's last digit-bearing line, so the row is drafted through the argv branch with the row's own (unchanged) command and cause `fec846dd…`. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:21`.
6. G23's `uncovered=1` is not a broken record: `census/round-33/waves/w1-results.json` was committed after the r33 manifest was captured; the restated row states it as fact rather than hiding it.

## Attack log

* **A1 (item G23, `where` cell off by one).** Frozen item: `G23 SKILL.md:247 …pred SUMMARY manifests=7 failed=0 uncovered=0 floor_violations=0`. At the list revision `SKILL.md:247` is the `souji-wave-evidence-capture v2` row (probe row + r33 evidence); the row the argv and predicate describe (`r29-c2-counter`) is `SKILL.md:248`. Reproduced: `grep -n 'r29-c2-counter' <base SKILL.md>` → `248`. Consequence: the counter's argv-correction cause check resolves the wrong line text, so the honest cause slot can only be filled by a commit that wrote line 247's text. Routed as a defect observation; no item/counter change is proposed from this seat.
* **A2 (item G23, `files` cell too narrow for value drift).** The real drift is `d65a5c4328896742d2ec951f7156c6a70aa9325a` (executed: parent `4d9bf02` prints `manifests=7`/rc 0, the cause prints `manifests=8`/rc 0) but that commit touches only `census/round-33/waves/*`, while the item's `files` cell names `census/round-29/c2-counter.py`; the frozen value-drift branch therefore refuses the executed cause. Reproduced above.
* **A3 (item G24, `at` before the script and `exit` contradicting the predicate).** `9420341d…` has no `tools/souji-capability-agreement.py` (`git cat-file -e` → absent; introduced `d4928ec`), while the frozen `exit` cell is 0 for a predicate text (`k1=12 … mismatches=12`) that the row's own outcome column maps to exit 1 — executed at base, the row's command prints exactly that line with rc 1. The predicate text is traceable to `SCORECARD.md:344` (`### Round 30 capability rows`: "`SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10` (v1; A3 reads `k1=12`, R18 matching on stdout)"), a capability row inside the r33-covered sections, not a registry restatement of `SKILL.md:249`, so Q76 does not rescue the item. Result: `MISMATCH` that no restatement can repair, so `SUMMARY items=60 agree=60` is unreachable this round unless the L1 treats G24 as a recorded honest miss or amends the item (which the frozen rule reserves for the L1).
* Refused route, not used: materialising the script inside the argv cell (`git show d4928ec:tools/… > tools/… && python3 -B tools/…`) would satisfy the engine while mutating the measured checkout and hiding A3.

## Deliveries

* `.ufo/waves/round-34/w1/deliver-c1-G23.md` — ITEM line, Q76 grep, cause `1dc6785…` + executed parent/drift/base readings, proposed row (engine-validated AGREE).
* `.ufo/waves/round-34/w1/deliver-c1-G24.md` — ITEM line, Q76 grep, `at`-vs-script evidence, executed row-command reading at base, engine rejection of the only admissible row, ATTACK A3.
* `.ufo/waves/round-34/w1/deliver-c1-G26.md` — AGREE, no row needed (note on the line number).
* `.ufo/waves/round-34/w1/deliver-c1-E01.md` — AGREE, no row needed.
* `.ufo/waves/round-34/w1/deliver-c1-E04.md` — ITEM line, Q76 grep, cause `fec846dd…` + executed parent/drift/base readings and the stderr-ordering reason for the argv branch, proposed row (engine-validated AGREE).
* Report: `.ufo/waves/round-34/w1/SwarmExecutor05.md`.

Scratch (`/fast/scratch/hyaku/souji-r34/RestateC1s5`) was used for all clones, probes and the engine validation; no tool install or upgrade was needed (git, python3, jj 0.45.1 and flock were already present). No lane mutation, no credentials, no live /proc census, no fleet-root writes.
