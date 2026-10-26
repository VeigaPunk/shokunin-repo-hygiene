# SwarmConnector30 — souji round 30 wave 2, cross-claim attack over landed commits

## Status

STATUS: PASS — the attack ran end-to-end: all four landed claims re-measured live at their landing
commits and the tip, every L1 reading reproduced or refuted from bytes opened this run, one new
environment-sensitivity defect found and race-proven. PASS means the attack ran, not that targets held.

## Evidence

All commands run on private clones (origin removed) of the lane with `python3 -B`; TMPDIR under
`/fast/scratch/hyaku/souji-r30/SwarmConnector30` (scratch dir since removed). Receipts copied to
`.ufo/waves/round-30/w2/receipt-SwarmConnector30-*.txt` before cleanup.

1. `c2-counter.py` v1 at 68447af: `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same` (rc 1) — `receipt-SwarmConnector30-c2v1-68447af.txt`. At tip 9dcd367: `dangling=0 other=0` (rc 0) — `receipt-SwarmConnector30-c2v1-tip.txt`.
2. `c2-counter-v2.py` (A1) at 68447af and at tip: sole failing leg `regress_full=differs` — `receipt-SwarmConnector30-c2v2-{68447af,tip}.txt`.
3. Normalized gate `--selftest` BASE(9420341) vs REV(68447af): 66/66 lines, exactly 2 differ, both `err=` tails — `receipt-SwarmConnector30-selftest-{base,rev}.txt`; space-tolerant strip makes them identical (verified this run).
4. C1 frozen v1 blob (d4928ec) at 7b16731: solo → `k1=0 k2=0 mismatches=0 rows=18 pointers=10` (`receipt-SwarmConnector30-c1v1-solo.txt`); two concurrent counter processes → both `R14 rc=1 observed=selftest=13/15 MISMATCH kind=rc`, `k1=1` (`receipt-SwarmConnector30-c1v1-concurrent.txt`); at tip solo → `k1=0`, R17 MATCH (`receipt-SwarmConnector30-c1v1-tip.txt`).
5. Race probe: two concurrent `tests/fixtures/r23-record-agreement.py` → both crash `RuntimeError(f"git {' '.join(args)} failed: ...")` — `receipt-SwarmConnector30-race-{a,b}.txt`.
6. C3 at 76c94eb: `SUMMARY legs=9 fail=0 f1_entries=3` (`receipt-SwarmConnector30-c3v1.txt`); `SUMMARY-V2 e1=ok e2=ok e3=ok e4=ok f1_exact=3` (`receipt-SwarmConnector30-c3v2.txt`).
7. M1 receipt (9dcd367, `census/round-30/records/m1-r29-carry-red-before.txt`): gate `--round 29` rc 1 `carry_heading=0` at 76c94eb → rc 0 `carry_heading=1` at 936efc8.

## Findings

1. **C1 bytes → C2 gate, landing-commit MISS reproduced (r29-D1 recurrence).** `SCORECARD.md:322`@68447af: "Literal provenance per row: `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`" — cited bytes existed nowhere committed until capture commit aea0525, so the gate (any-round `CAPTURE_POINTER_RE`) scored `dangling=1` at C2's own landing commit. `other=7` = the pre-carry seat-uncarried findings. Verdict reproduced byte-for-byte; met at tip.
2. **A1 v2 counter defect pinned: `strip_err` tab-vs-space.** `census/round-30/c2-counter-v2.py`@68447af: "re.sub(r"\terr=.*$", "", l) if l.startswith("CASE\t")" vs gate `tools/souji-landing-gate.py:1423`@68447af: "detail = "exit=%d ids=%s paths=%s fleet=%s err=%s"" (space-separated `err=`). The only 2 differing selftest lines are exactly the reworded no-reports tails A1 meant to exempt; frozen target `regress_full=same` is unreachable for the true gate at any rev → DEFECT, report-only.
3. **C1 chain environment-sensitive (NEW class).** R14 fixture `tests/fixtures/r23-record-agreement.py:67`@7b16731: "SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"" with `:105` "shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)" — concurrent counter runs race on it: solo k1=0, concurrent k1=1, two-process probe crashes both. Other row fixtures uniquify (r12/r13/r28 `mktemp …XXXXXX`, r29/gate/r16 `tempfile.mkdtemp`); only R14 racy. Any un-serialized wave-2 k1 reading is unreliable in both directions.
4. **C3 ↔ C2 gate and C3 ↔ C1: clean.** C3's files are all in the gate scan set; gate ran green at 76c94eb (M1 receipt, no LG-DANGLING-PTR; my tip runs `dangling=0`); C3's fixture refuses a lane-resident TMPDIR. C1 reads only SCORECARD/SHONEN/c1-rows.tsv; R17 registry-agreement still `cases=20 pass=20` at the tip over C3's S220/S221 + S054/S063 edits.
5. **r29 lesson carry verified.** Gate transition 7 findings rc 1 → 0 findings rc 0 with `carry_heading` 0 → 1 (committed M1 receipt); carried `SwarmCritic49.md` line-5 quote equals committed bytes at df6afe817d096e4ad71ba2b9cc21a83f126eb658: "STATUS: PARTIAL — the claim is real but its instrumentation is not: a restatement pair reaches every".
6. **Mistake-class recurrence r25–r29 → r30** (full table in the delivery): number-drift NOT recurring (BIND pins 86); vacuous-counter recurred in wave-1 attacks → A1–A3 pre-landing, with the new A1 strip residual; stale-premise recurs as the C1→C2 commit-order race; r29-D1 recurred materially; attribution/scope classes not recurring (honest MISS recorded; origin-drop fix carried); environment-race is new.

## Attack log

| Attacked item | Verdict |
|---|---|
| L1 reading "C1 met at 7b16731, k1=0" | HOLDS solo (reproduced); BROKEN under concurrent execution (k1=1, race-crash proven) — DEFECT-NOT-FATAL for the landing verdict; environment sensitivity reported |
| L1 reading "C2 v1 MISSED at 68447af, dangling=1" | HOLDS (reproduced byte-for-byte; `other=7` explained; met at tip) |
| L1 reading "A1 v2 printed regress_full=differs (tab/space)" | HOLDS, root cause pinned to the 2 exempt-able lines — counter DEFECT (BROKEN as a scoring instrument; frozen, report-only) |
| L1 reading "C3 met, v1 legs=9 fail=0 f1_entries=3; v2 e1..e4=ok" | HOLDS (both reproduced, rc 0) |
| r29 lesson carry (936efc8) vs r29 gate | HOLDS (rc 1→0 transition from committed receipt; verbatim quote spot-check passed) |
| Cross-claim surface "C3 rows vs C1 counter" | HOLDS — no interference either direction |

## Deliveries

- `.ufo/waves/round-30/w2/deliver-cross-claim-landed.md` — cross-claim map, recurrence table, one bounded proposed move (mine three evidenced mistakes into `corpus/lessons/round-30.md` `## Mistakes`: commit-order race + D1 recurrence; C1 shared-`/var/tmp` race; A1 strip_err defect).
- Receipts: `.ufo/waves/round-30/w2/receipt-SwarmConnector30-{c2v1-68447af,c2v1-tip,c2v2-68447af,c2v2-tip,c1v1-solo,c1v1-concurrent,c1v1-tip,c3v1,c3v2,race-a,race-b,selftest-base,selftest-rev}.txt`.
- No installs or updates this run (no new tooling needed). No lane bytes modified; read-only git only.
