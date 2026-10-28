# R41w2executor03 — axis-harm audit: gates at base 7eebc18 vs tip 1d41c13

Verdict: **no gate that passes at base fails at tip.** 59 of 61 rows give identical exit codes at both revisions (`r18-leak-count` is the one row that differed in a single run; it was a flake, see below). One **new landing-gate finding** is attributable to the tip (below), and it is the only harm-shaped difference.

## Method (commands actually run)
- Trees: `git archive 7eebc183f2685d1ea9b004b4de22c09a8a4035a7 | tar -x -C /fast/scratch/hyaku/souji-r41/R41w2executor03/base` and the same for `1d41c13574db80fdd9a4bde490b712da7ce2a85f` into `.../tip` (dirs named `base`/`tip`, not by rev). Because an archive has no `.git`, I also made live checkouts `git clone --no-local <lane> gbase|gtip` + `checkout` of each rev (toplevel verified = dir) for rows that need a git worktree.
- Runner: `.ufo/waves/round-41/w2/R41w2executor03/run-gates.py` (kept here; the 61 command lines are in it). Each command runs with cwd inside the tree, `TMPDIR` = per-case scratch dir, 120 s timeout, JOBS 4–8 in parallel, both revisions run the same command line. Pass 1 = archive trees (`run1.out`), pass 2 = git checkouts `GIT=1` (authoritative for all rows except those noted), pass 3 = `VARTMP=1` for the legacy `TMPDIR=/var/tmp` selftests (rows 0-3, 23).
- Commands are the SKILL.md row self-test / default invocation, with `--tool tools/<x>` for the current tool and `<blob>` baselines extracted from lane git read-only (`6ff3413` auditor/proc blobs verified by the row's own sha256; `1e771ed` drift blob for r37-drift-escapes; `4c257b7` for r38-write-envelope; `8513d6ac`/`522dcd76` runners).
- Receipts: `receipts/logs/*.txt` (command line + rc + full output; `base-NN`/`tip-NN` = archive tree, `gbase`/`gtip` = git checkout, `vbase`/`vtip` = /var/tmp), `receipts/results-*.json`, `receipts/*.txt` extra reruns.

## Table (rc base / rc tip; last SUMMARY line; git-checkout run unless noted)
| # | gate / self-test | base rc | tip rc | summary |
|---|---|---|---|---|
| 0 | souji-verify selftest | 0 | 0 | selftest: 49 checks, 0 failed |
| 1 | souji-vault-verify selftest | 0 | 0 | selftest: 57 checks, 0 failed |
| 2 | souji-census selftest | 0 | 0 | selftest: 69 checks, 0 failed |
| 3 | souji-quarantine selftest | 1 | 1 | /var/tmp: 108 checks, 2 failed (G1 guard rc=4 got=2, G1 guard token) |
| 4 | r12-maintenance-guard --selftest | 0 | 0 | selftest=PASS ids=6/6 |
| 5 | souji-cert-evidence selftest | 0 | 0 | selftest: 36/36 passed |
| 6 | r13-cert-evidence | 0 | 0 | fixture: 5/5 checks passed |
| 7 | r13-repo-structure | 0 | 0 | selftest=PASS ids=7/7 |
| 8 | r13-quarantine-bounds | 0 | 0 | SUMMARY total=5 failed=0 hung=0 |
| 9 | souji-evidence-cache selftest | 0 | 0 | selftest: 48/48 passed |
| 10 | r14-evidence-cache | 0 | 0 | fixture: 22/22 checks passed |
| 11 | r14-census-boundary | 0 | 0 | SUMMARY total=12 failed=0 |
| 12 | r15-census-config | 124 | 124 | TIMEOUT 120s |
| 13 | r17-census-hygiene | 0 | 0 | SUMMARY total=29 failed=0 |
| 14 | r17-jj-receipts | 0 | 0 | SUMMARY total=35 failed=0 skipped=2 |
| 15 | souji-preservation-evidence selftest | 0 | 0 | selftest: 47/47 passed |
| 16 | r15-preservation-evidence | 0 | 0 | fixture: 8/8 checks passed |
| 17 | souji-landing-gate selftest | 0 | 0 | SELFTEST pass=65 fail=0 |
| 18 | r18-landing-pointers | 0 | 0 | SUMMARY total=11 failed=0 |
| 19 | r16-landing-gate | 0 | 0 | SUMMARY total=15 failed=0 |
| 20 | souji-seat-audit selftest | 0 | 0 | SELFTEST pass=118 fail=0 |
| 21 | r17-transcript-manifest --check | 0 | 0 | check OK: 144 files verified |
| 22 | r18-census-bounded | 124 | 124 | TIMEOUT 120s |
| 23 | souji-proc-census selftest | 0 | 0 | souji-proc-census: selftest PASS (newline comm parser, live literal cwd/fd, age identity, all redact |
| 24 | r18-proc-census | 1 | 1 | SUMMARY total=19 failed=1 |
| 25 | r18-leak-count selftest | 1 | 0 | (JSON selftest record; see flake note) |
| 26 | souji-rev-pin selftest | 0 | 0 | SUMMARY total=11 failed=0 |
| 27 | r19-rev-pin | 0 | 0 | SUMMARY total=13 failed=0 base_discriminating=6 |
| 28 | r19-carry-wrap | 0 | 0 | SUMMARY total=4 failed=0 base_discriminating=2 |
| 29 | probe-carry-invariants | 0 | 0 | SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0 |
| 30 | r19-seat-audit-shapes | 0 | 0 | SUMMARY total=17 failed=0 base_discriminating=12 |
| 31 | verify-agreement-pin selftest | 0 | 0 | SUMMARY total=5 failed=0 |
| 32 | r20-audit-contract | 0 | 0 | SUMMARY total=66 pass=66 fail=0 base_discriminating=0 |
| 33 | r21-read-root | 0 | 0 | SUMMARY total=32 pass=32 fail=0 base_discriminating=14 |
| 34 | r21-reason-canary | 0 | 0 | SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160 |
| 35 | r21-read-render-edges | 0 | 0 | SUMMARY total=4 pass=4 fail=0 |
| 36 | r21-replay-boundaries | 0 | 0 | SUMMARY total=8 pass=8 fail=0 base_discriminating=4 |
| 37 | r21-source-head | 0 | 0 | SUMMARY total=3 pass=3 fail=0 base_discriminating=1 |
| 38 | r22-result-oracle | 0 | 0 | total=258 (JSON receipt) |
| 39 | r22-mutation-adequacy | 0 | 0 | killed=52 survived=7 disagreeing=[] |
| 40 | r27-pre-report-gate fixture | 0 | 0 | cases=4 pass=4 control=FALSE-GREEN-REJECTED |
| 41 | souji-report-contract selftest | 0 | 0 | SUMMARY cases=9 pass=9 fail=0 |
| 42 | r36-report-gate | 0 | 0 | SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED |
| 43 | r36-worktree-drift | 0 | 0 | SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED |
| 44 | r37-citation-reconcile | 0 | 0 | SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED |
| 45 | r38-counter-arms | 0 | 0 | SUMMARY cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED |
| 46 | r37-drift-escapes | 0 | 0 | SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED |
| 47 | r37-drift-discrimination | 0 | 0 | SUMMARY cases=6 pass=6 fail=0 |
| 48 | r37-drift-mutants | 0 | 0 | SUMMARY mutants=6 killed=6 survived=0 |
| 49 | r29-registry-agreement fixture | 0 | 0 | cases=20 pass=20 control=FALSE-GREEN-REJECTED (abs --tool, extra/) |
| 50 | r28-wave-evidence-capture | 0 | 0 | cases=15 pass=15 control=TAMPER-REJECTED |
| 51 | r30-landing-gate-discovery | 0 | 0 | cases=7 pass=7 control=FALSE-GREEN-REJECTED |
| 52 | r31-landing-gate-precision | 0 | 0 | cases=10 pass=10 control=FALSE-GREEN-REJECTED |
| 53 | r38-citation-commit | 0 | 0 | SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED |
| 54 | r38-drift-write-envelope | 0 | 0 | SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3 |
| 55 | r38-drift-record | 0 | 0 | SUMMARY cases=10 pass=10 fail=0 |
| 56 | r38-drift-mutants | 0 | 0 | SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 |
| 57 | r39-citation-rev | 0 | 0 | SUMMARY cases=8 pass=8 fail=0 |
| 58 | r39-drift-record-rules | 0 | 0 | SUMMARY cases=7 pass=7 fail=0 |
| 59 | souji-registry-agreement (lane check) | 1 | 1 | k1=1 k2=0 mismatches=1 (K1 cited-no-row S146) |
| 60 | souji-landing-gate (lane check; same-round: `--round 40` at both revs, `--round 41` at both) | 1 (r40: findings=3) / 2 (r41: findings=3 + CNE) | r40: 1 (findings=3) / r41: 2 (findings=4 + CNE) | r40 identical both revs; r41 tip adds `LG-DANGLING-PTR .ufo/waves/round-40/w2-run.err corpus/lessons/round-41.md:113` |

## Findings
1. **Harm candidate (landing gate, round 41): one new `LG-DANGLING-PTR`.** Evidence `receipts/extra/lg-*.txt`, also `logs/gtip-60.txt` (cmd `python3 -B tools/souji-landing-gate.py --root <git checkout> --rev <rev> --round N`):
   - `--round 40`: base rc=1 and tip rc=1, identical 3 findings (`corpus/README.md:217` ×2, `corpus/knowledge/jj-colocation-receipts.md:148`), `checked_reports=117` — nothing the tip adds changes the round-40 reading.
   - `--round 41`: base rc=2 (findings=3, CNE no round-41 reports at rev); tip rc=2 (findings=**4**, CNE no round-41 reports at rev). Added line: `LG-DANGLING-PTR .ufo/waves/round-40/w2-run.err corpus/lessons/round-41.md:113 cites path absent at 1d41c13574db`. Line 113 of the C1 lesson cites that path on purpose ("`.ufo/waves/round-40/w2-run.err` is empty and untracked"); the file exists in the lane worktree (0 bytes, `.ufo/waves/` gitignored) but not at the committed rev, which the gate reads. Either the lesson is reworded/exempted or the L1 must accept the finding; the gate will not clear it as is. The CNE (no round-41 reports committed) is the pre-landing state, not a regression; both revs show it.
2. **r18-leak-count selftest flake (not a harm).** First git-checkout pass: base rc=1 (`deleted FIFO reader was not counted exactly once (before=60, after=55)`), tip rc=0. Six reruns sequentially (3 base, 3 tip, `receipts/leak.txt`): all rc=0. The selftest counts live host processes; other fleet seats run concurrently. Tool bytes are identical at both revisions.
2b. Pre-existing at both revisions (unchanged by tip): `souji-registry-agreement --list-rev b8cb4b31…` → `k1=1 k2=0 mismatches=1`, `K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md` (rc=1 at 7eebc18 and 1d41c13; S258 row added at tip does not fix it). My first registry run used `--list-rev` = freeze commit and base-tip merge and got `COULD-NOT-EVALUATE derived facts are trivial` rc=2 at both (wrong list-rev; discarded).
3. **Same failure at both revisions (environment, not harm):**
   - `souji-quarantine --selftest`: rc=1 both; 108 checks / 58 failed with scratch TMPDIR, 2 failed (`G1 guard rc=4 (got=2)`, `G1 guard token`) with `TMPDIR=/var/tmp` as the row prescribes.
   - `r18-proc-census`: rc=1 both, `P7 traced census failed (rc=124 timed_out=True)`, 19 cases / 1 failed; repeated 2× at each rev sequentially. (One tip repeat printed `failed=2`; I did not capture which second case, a re-run printed `failed=1`.)
   - `r15-census-config` and `r18-census-bounded`: exceed 120 s at both revisions (rc 124): not evaluated, skipped per the 120 s rule.
4. Git-less archive false failures (cleared by the live checkout): rows 18, 19, 28, 30, 38, 39 need a git worktree; with it they pass at both. `r29-registry-agreement.py` fixture fails 20/20 with a relative `--tool` (fixture runs from a /var/tmp dir) and passes `cases=20 pass=20 control=FALSE-GREEN-REJECTED` at both with an absolute `--tool` (`receipts/r29-fixture.txt`).
5. Tip-only artifacts (no SKILL.md row, outside the base/tip comparison): `tests/fixtures/r41-drift-record-order.py` → `SUMMARY cases=12 pass=12 fail=0`; `tests/fixtures/r41-refusal-sites.py --tool tools/souji-worktree-drift.py --work <scratch>` → `SUMMARY probes=21 pass=21 fail=0` (rc 0 both). The tip's only edit to an existing tool is `tools/souji-worktree-drift.py` (+11/−2); every drift gate row (36, 37-x3, 38-x4, 39) is green at tip with unchanged literals.

## Not run / limits
- Needs a baseline git rev or live fleet and not provided: `r20-input-binding` (`--baseline` rev in cwd git; cwd is a checkout but I did not attempt it), `r17-census-matrix`, `r18-census-matrix`, `r17-gate-replays`, `r21-acceptance`/`replay-matrix`, `r21-source-refs`, `souji-seat-audit` with a real spec, `souji-pre-report-gate` real lane, `souji-census` live fleet runs, `souji-rev-pin` real-lane calls, `r30/r31/r32 jj-*` probes (jj-based, no gate verdict).
- Historical counters (`r29-c2-counter`, r30-r39 `c*-counter`, `souji-capability-agreement/-cells`, `souji-record-contract`, `souji-citation-reconcile` against a real register) were not run: their pinned prereg revisions/scratch arguments are per-round and the comparison is by revision, not by tool bytes. This audit covers the rows with a tool-bytes-sensitive self-test or fixture.
- Scratch dirs were `/fast/scratch/hyaku/souji-r41/R41w2executor03/{base,tip,gbase,gtip,clone.git,tmp,...}`, deleted before yield (two mode-000 `.omp/agent` dirs created by r15-census-config required chmod first, per R41w2scout01).
