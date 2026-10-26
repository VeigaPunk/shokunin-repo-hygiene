# SwarmScribe33 — round 31 wave 2 (scribe): SCORECARD measurements/capability rows/planned r32 and LOG entry, with counter re-derivations

## Status

STATUS: PASS — the assigned delivery is drafted from readings this seat re-derived from committed bytes (every frozen and amended counter re-run at base, at each claim's landing commit and at the tip); the C1 miss, the enumeration scope limit, the gate's letters-only blind spot, the 54 uncarried seat-failure lines left by M1's scope and the gate's `/var/tmp` snapshot are reported as findings, none of them as a proposal to relax a target.

Seat scope: report + one delivery file under `.ufo/waves/round-31/w2/`; read-only on the lane; no subagent dispatch.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`. Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, tip read `2c16d018e40db7c23420a2c3bb546b52957bcc25` (`git rev-parse HEAD`; `git log --oneline 9f17a1e..tip` lists 11 round-31 commits). Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe33/`, `TMPDIR` set there; every counter ran serially in this seat.

**1. Frozen and amended instrument digests** (`sha256sum` of working-tree files vs the recorded digests):

- `tools/souji-capability-cells.py` = `edf0933d…607da3` (A4 block); the v1 blob `git cat-file -p 1d45496:tools/souji-capability-cells.py | sha256sum` = `eced32ea…2e2d9b520` = `frozen-digests.txt`.
- `census/round-31/c2-counter.py` `7f912cc6…`, `c2-counter-v2.py` `95540fad…`, `c2-counter-v3.py` `12593a3b…`; `c3-counter.py` `c978ad7c…`, `c3-counter-v2.py` `72a946e3…`, `c3-counter-v3.py` `5553b6d8…`; `census/round-31/c1-cells.tsv` `413e6d2f…`; `records/preregistration.txt` `450984a3…`. All equal the values in `records/frozen-digests.txt` and `records/amendments.txt` (A0-A5).

**2. C1 — `python3 -B tools/souji-capability-cells.py --root <lane> --rev <R> --base 9f17a1ef… --list-rev 1d45496… --scratch <scratch>`** (and the same with the v1 blob written to scratch):

```
R=1d45496 (base content)   SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34   rc=1
R=24f343c (landing), v1    SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1    rc=1
R=24f343c (landing), A2+A4 SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1    rc=1
R=2c16d01 (tip),     A2+A4 SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1    rc=1
R=2c16d01 (tip),     v1    SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1    rc=1
```

Base split counted from the ITEM lines of my own base run: 22 `UNBOUND` + 12 `RUN-MISMATCH` = 34; 7 base-cell run `MATCH`. At landing/tip: 40 `MATCH` (20 run + 20 record) and one `UNBOUND` (L29). `git diff --stat 24f343c..2c16d01 -- SCORECARD.md tools/` is empty. These five lines equal `records/c1-before.txt`, `records/c1-after-v1.txt`, `records/c1-after-a4.txt`.

**3. C2 — `python3 -B census/round-31/c2-counter{,-v2,-v3}.py --root <lane> --rev <R> --base 9f17a1ef… --fleet-root /home/vgpnk/Projects/shokunin`:**

```
R=1d45496 v1  SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same   rc=1
R=8024b54 v1  SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same          rc=0
R=8024b54 v2  SUMMARY fp=0 … shift=ok                                                       rc=0
R=8024b54 v3  run1 shift=ok, run2 shift=ok (fresh random SHIFT-PROBES each run)             rc=0
R=2c16d01 v1/v2/v3  SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same [shift=ok]  rc=0
```

Base run: `FIXTURE absent fail` / `REDARM absent fail` (the fixture is r31 content). Landing REDARM: `base_cases=[('G1','FAIL'),('G2','PASS'),('G3','FAIL'),('G4','FAIL'),('G5','FAIL'),('G6','FAIL'),('G7','FAIL'),('G8','FAIL'),('G9','PASS'),('G10','PASS')] ok`. Two v3 runs drew different probes (e.g. `tools/souji-gate-check.py:260–264 … real=tools/wcktfgl-r31.py` and `tools/souji-rev-pin.py:312–318 … real=tools/vuntix-r31.py`) and both returned `shift=ok`. Matches `records/c2-after-v1.txt`, `c2-after-v2.txt`, `c2-after-v3.txt` (the v3 record's base control at `1d45496` reads `fp=13 … shift=fail`, the line I reproduced as v1).

**4. C3 — `python3 -B census/round-31/c3-counter{,-v2,-v3}.py --root <lane> --rev <R> --base 9f17a1ef…`:**

```
R=1d45496 v1  SUMMARY legs=11 fail=10 f1_entries=3   rc=1
R=1d45496 v2  SUMMARY legs=12 fail=11 f1_entries=3   rc=1
R=1baf4da v1  SUMMARY legs=11 fail=0 f1_entries=4    rc=0
R=1baf4da v2  SUMMARY legs=12 fail=0 f1_entries=4    rc=0   (L12 rc=0 results_equal=True jj_calls=26 git_calls=111)
R=1baf4da v3  SUMMARY legs=13 fail=0 f1_entries=4    rc=0   (L13 M1/M2 rc=0 lines=17 differs=True no=0<4=True)
R=2c16d01 v1/v2/v3  legs=11/12/13 fail=0 f1_entries=4  rc=0
```

Matches `records/c3-after-c3-counter{,-v2,-v3}.txt` and `records/controls.tsv` (`C3-do-nothing(base)` `fail=10` / `fail=11`).

**5. Capability-row evidence (commands that run, fresh output this seat):**

- `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` → `CASE G10 PASS …` … `cases=10 pass=10 control=FALSE-GREEN-REJECTED` (rc 0). Base-tool arm from the C2 REDARM line above: `cases=10 pass=3`.
- `bash tests/fixtures/r31-jj-object-clock.sh` with `TMPDIR` in scratch → `jj-version: jj 0.45.1-7c41cdeb…`, `git-version: git version 2.56.0`, 17 `RESULT ` lines; `diff` of the `RESULT` lines against `records/jj-object-clock-run.txt` is empty (`RESULT-LINES-IDENTICAL`).

**6. Landing gate at the tip, per round (`python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d01 --round N --fleet-root /home/vgpnk/Projects/shokunin`):**

```
round 15 findings=1   (LG-SEAT-UNCARRIED 1)
round 19 findings=3   (LG-SEAT-UNCARRIED 3)
round 23 findings=12  (LG-SEAT-UNCARRIED 10 + LG-DANGLING-PTR 2)
round 24 findings=17  (LG-SEAT-UNCARRIED 17)
round 25 findings=23  (LG-SEAT-UNCARRIED 23)
round 26 findings=0   round 27 findings=0   round 28 findings=0   (M1 carries read; 495/94/61 reports)
```

Uncarried total 1+3+10+17+23 = 54. Without `--fleet-root` every round also reports three `../.ufo/waves/hyaku/jj-w1/` paths (`corpus/README.md:217`, `corpus/knowledge/jj-colocation-receipts.md:148`), which resolve under the fleet root.

**7. M1 receipts:** `records/m1-red-before.txt` base gate — round 26 `findings=18`, round 27 `29`, round 28 `21` (19 uncarried + 2 dangling); `records/m1-after.txt` — base and tip gate both `findings=0` at `c610830` for all three rounds. Carry-bullet counts read from the lessons: round 26 = 26, round 27 = 29, round 28 = 19.

**8. Content figures for the LOG block:** `corpus/SOURCES.md` rows `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` = 145 at base, 146 at tip (S222 at `corpus/SOURCES.md:167`, `git Documentation/git-reflog.adoc at tag v2.56.0`); `records/census-start.txt` ends `exit=0` with 36 `W04` duplicate-URL warnings. Waves: `w1-results.json` reads `seats=38` with 38 result payloads and `census/round-31/waves/summary.tsv` lists the roles (executor 10, scribe 9, scout 4, critic 4, reviewer 3, mutation-tester 3, connector 2, simplifier 1, sentinel 1, revenger 1); `w2-spec.json` 36 items (critic 10, executor 6, scribe 6, reviewer 5, mutation-tester 3, scout 2, connector 2, sentinel 1, simplifier 1). `corpus/QUALITY.md` still ends at Q66; `corpus/lessons/round-31.md` does not exist yet.

**9. Source/cell quotes opened this run** (verbatim, pipe-free): `SCORECARD.md:147` `at 64-seat parallelism, dry-run`; `:151` `baseline 33 rows, mined=16 queued=15`; `:161` `(5fa6017 tools: 13 fail)`; `:168` `auditor selftest118/0; r19-seat-audit-shapes17/0 (base12)`; `:170` `3/3 each18/18`; `tools/souji-landing-gate.py:1182` `snapdir = tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")`.

## Findings

1. **C1 misses its frozen target by one item, at the landing commit and at the tip.** `SCORECARD.md:170` states L29's count only as scalars (`"matched_command_count": 18`), so the frozen rule admits no binding; the counter reads `unbound=1 mismatches=1` under v1 and A2+A4 (`records/c1-after-a4.txt`). Axis: calibration — the round accrues 40/41, not the target.
2. **The 41-item enumeration is notation-selected, so "every enumerated cell literal is bound" is true of a notation subset, not of the capability cells.** At the tip the same cells still carry counts outside it: `SCORECARD.md:147` `(246 rows)`, `:151` `baseline 33 rows, mined=16 queued=15`, `:161` `(5fa6017 tools: 13 fail)`, `:168` `(base12)`, `:170` `3/3 each18/18`. Axis: calibration (scope of the claim, routed by A4 not counted).
3. **The gate's letters-only rule suppresses genuinely absent prose paths.** Repro: scratch clone at the tip, commit `6fc56a50bd3855a4935da00e7d8f626ba6098877` appends to `corpus/lessons/round-19.md` the probes `corpus/knowledge/absentdir`, `census/waves` and control `corpus/knowledge/absent-probe-r31.md`; the tip gate at that rev reports only the `.md` control (`findings=4` = 3 uncarried + 1 dangling). I then tested all 13 base false positives for reality at base: 4 resolve (ellipsis over three `census/round-18/seat-audit-*.json`; en-dash line ranges on `tools/souji-seat-audit.py`, `corpus/knowledge/process-residue-observations.md`, `tests/fixtures/r18-proc-census.sh`; `.gitignore:fixture/` over `.gitignore.captured`), and the 8 absent tokens are prose phrases at their sources (`corpus/authority`, `corpus/helper`, `corpus/source/QUALITY`, `corpus/census/tools`, `tools/kill/killpg`, `tools/tests/census/corpus`, `corpus/knowledge/registry` as a grep pattern, the vault `.gitignore` with the `:fixture/` suffix). Axes: operability (a real extension-less dangling citation would pass), calibration-adjacent (the FP count is the only reading). Disclosed by A3/G8; no live harm shown today.
4. **C2's LANE leg counts only `LG-DANGLING-PTR`; real carry lines never move the target.** `census/round-31/c2-counter-v3.py:135-146` reads the gate output for dangling lines only, and at the tip the gate reports 54 `LG-SEAT-UNCARRIED` lines in rounds 15/19/23/24/25 while C2 reads `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok`. Axis: operability — the frozen reading cannot detect a regression of the multi-section carry rule on committed lessons (the G1/G3/G10 fixture legs are synthetic only). Same class as wave-1 SwarmReviewer25 finding 1; my tip numbers are independent.
5. **The gate writes its parse snapshot and selftest trees under `/var/tmp`, ignoring `TMPDIR`.** `tools/souji-landing-gate.py:1182` and `:1499`; the module header at `:25` says `snapshot removed in finally`. Axis: operability/hygiene (operator scratch directive of 2026-10-25 puts seat scratch under `/fast/scratch`); disclosed by wave-1 SwarmCritic31 item 8, verified here in current bytes.
6. **No counter drift and no false green found.** All frozen and amended readings reproduced line-for-line at base, landing and tip; the delivered C1 prose discloses L29 rather than hiding it; C2/C3 claim bytes are unchanged between landing and tip (`git diff --stat` empty for the gate, the precision fixture, the entry, the C3 fixture/record/snapshots).

## Attack log

- **A1 — letters-only blind-spot construction.** Wrote two genuinely absent letters-only paths and one `.md` control into a scratch clone at the tip and ran the tip gate on that commit: the two letters-only paths were not reported, the control was (`6fc56a5`). Result: reproduced, bounded (no live harmful instance among current suppressions).
- **A2 — carry-blind LANE leg.** Read the leg code and measured the tip: 54 real uncarried lines, none of which any C2 leg counts. Result: reproduced; reported as a boundary, not as a counter defect (the fixture is the contract's carrier of that rule).
- **A3 — counter drift hunt.** Re-ran every version (v1, A2+A4, v1/v2/v3 for C2, v1/v2/v3 for C3) at base, landing and tip, including two v3 C2 runs with fresh random probes. Result: all recorded SUMMARY lines reproduced exactly; no drift, no stale record.
- **A4 — revision-change assumption check.** Instead of inferring tip readings from unchanged diffs, ran C1/C2/C3 at `2c16d018e40d` directly; C1 stays `mismatches=1`, C2 stays `fp=0 … shift=ok`, C3 stays `fail=0 f1_entries=4`.
- **A5 — instrument identity check.** Hashed every frozen and amended counter against `frozen-digests.txt` and `amendments.txt`; all match, so the readings above are from the declared instruments.
- **A6 — base false-positive audit.** Classified all 13 base `LANE-FP` tokens against base content (`git cat-file -e`, `git ls-tree -r`): 4 resolve to real files/dirs through the tokenizer's own rules, 8 are prose phrases or grep patterns at their source lines. Result: no live dangling pointer is hidden by the current suppressions; the letters-only class remains the open hole (finding 3).
- **A7 — M1 honesty check.** Verified the base gate really reads the three lessons as uncarried before the fix (`records/m1-red-before.txt` 18/29/21) and that both base and tip gates now read `findings=0` at `c610830`; counted the carry bullets (26/29/19). No inflation found.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-scorecard-log.md` — Block A `### Round 31 measurements` (three rows, r30 column layout, both counter versions and the `c1-before`/`c1-after-v1`/`c1-after-a4`, `c2-after-v1/2/3`, `c3-after-c3-counter{,-v2,-v3}` records, measured at `24f343c8…`, `8024b540…`, `1baf4da0…`, plus tip readings at `2c16d018…`), Block B `### Round 31 capability rows (appended)` (capability-cell binding audit, landing-gate reading precision, jj object-clock fixture, each with a command and its observed output), Block C `### Planned (appended at round 31)` r32 bullet (L29, notation-selected enumeration, letters-only blind spot, 54 uncarried lines of rounds 15/19/23/24/25, `/var/tmp` snapshot), Block D LOG.md entry in the round-30 style. No `| Lnn | SCORECARD.md:` row appears in the file (`grep -nE '^\|\s*L[0-9]{2}\s*\|\s*SCORECARD\.md:'` → no match).
- `.ufo/waves/round-31/w2/SwarmScribe33.md` — this report.
- Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe33/` removed after the delivery was written; no lane mutation (no `git add/commit/push/stash/checkout/reset`, no `jj` command in the lane), no writes outside the two delivery paths.
