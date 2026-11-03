# S56critic01 — critic report, souji round 56 w1 (single v1 wave)

Seat: critic (falsify C1 and C2 on their frozen predicates and their discriminating power).
Measured revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83` (freeze), base `fafe371694fea41c5d23f63083865d5ccf3f1d36`, post-freeze tip read for official receipts: `148f39a6c902b27e997ac36d395735406d3ad9de`.
Method: every verdict below is taken from committed bytes at the revisions named (git show / git cat-file), the frozen counters run with scrubbed env, and fixtures built by the frozen builder into my scratch. No lane file was written; no mutating git/jj command was run anywhere.

**VERDICT: SURVIVED**
BOUNDS-VOCABULARY MAPPING: no DISAGREE, no ATTACK-FOUND on the claims; two always-zero-passable clauses (C1-T7, C2-T5) are named below and are conjunction-guarded.

## 1. Pin audit (stop-and-report gate — passed)

All 8 assignment pins sha256-verified at the freeze revision via `git -C <lane> show cce21b55…:<path> | sha256sum`; the working tree bytes are byte-identical (no drift):

| pin | prereg sha256 == observed | working tree |
|---|---|---|
| census/round-56/c1-counter.py | 975d3520…bbf179 OK | same |
| census/round-56/c2-counter.py | 56082011…59cb8 OK | same |
| census/round-56/fixtures/build-fixtures.py | 2f26d6aa…b85a OK | same |
| census/round-56/fixtures/run-matrix.sh | a7e1a892…62de3 OK | same |
| census/round-56/records/c1-selftest-expected.tsv | 48a7cc0e…c5bfb OK | same |
| census/round-56/records/c2-selftest-expected.tsv | 90517c4d…841b3 OK | same |
| census/round-55/c1-counter.py | 944feafa…921a2 OK | same |
| census/round-55/c2-counter.py | e4eb34e6…a568c OK | same |

The prereg's four additional pins (ws-drift record `2b90a262…6dad30`, census tool `e7e79952…7a5b`, r55 capture `088aaa26…73d40`, r55 run receipt `479b2715…bab45`) verified at the freeze revision — see `receipts/pins-full-audit.txt` (ends `EXIT=0`).

Dry-run vs official matrix bytes: `records/matrix-dryrun/{c1,c2}-matrix-v{4,5}.tsv` (freeze) vs `records/{c1,c2}-matrix-v{4,5}.tsv` (tip 148f39a6) — **4/4 IDENTICAL**. Beyond the byte comparison, I re-ran the frozen runner myself (`bash census/round-56/fixtures/run-matrix.sh $S $S/runs/frozen`, EXIT=0): my four regenerated TSVs are **byte-identical** to the committed dry-run and official bytes (c1-v4 `4b6fd504…`, c1-v5 `3bfa8180…`, c2-v4 `d7bf3a72…`, c2-v5 `d8613afd…`). Rebuilt fixture tips match the committed matrix rev column on all 49 rows (spot-checked F1 `55b56e65f805`, F24 `3b7923f3af56`, F29 `bf0488f93345`) — fixture determinism receipt.

## 2. Do-nothing control (the falsification instrument)

Stub (scratch-only, never in the lane): prints `SUMMARY sites=2 mismatches=0 filed=0 unfiled=0 …` (C1) / `SUMMARY entries=49 rows=49 … receipt=ok sorted=ok tool_pin=ok …` (C2) and **exits 0 for every input**; rev/base echoed for verisimilitude. Driven through the committed runner's exact arm logic by hand over the manifest: **33 C1 rows** (same arg shape incl. the F5/F6/F27 base-column special case) and **16 C2 manifest rows**, plus both stub selftests and both stub real-lane legs. Receipts: `receipts/stub-c1-matrix.tsv`, `receipts/stub-c2-matrix.tsv` (each ends `EXIT=0`).

**Clauses the stub passes: C1 — 1 of 8 (T7 only). C2 — 1 of 7 (T5 only).** Every detection clause fails it:

| clause | stub result | why |
|---|---|---|
| C1 T1 (flip set == {F24,F26,F28} + named findings) | **FAIL** | stub set = ∅; F24/F26/F28 stub rows all (0,'-') |
| C1 T2 (F27 v5 rc1 DELETIONS-UNREADABLE-BINARY) | **FAIL** | stub (0,'-') |
| C1 T3 (F7-FF2 v5 rc1 CORRECTION-IN-FENCE) | **FAIL** | stub (0,'-') |
| C1 T4 (narrowing set == {F29}) | **FAIL** | stub narrowing set = 24 fixtures |
| C1 T5 (carry-over identity, 27 fixtures) | **FAIL** | 21/27 rows differ |
| C1 T6 (`SELFTEST pass cases=33`, pins) | **FAIL** | stub prints no SELFTEST line |
| C1 T7 (real-lane SUMMARY fields, rc0) | **passes as written** | always-zero clause (see §4) |
| C1 T8 (EXIT= on cited receipts) | n/a (not an instrument predicate) | receipts checked in §4 |
| C2 T1 (flip set == {FC1,FC2,FC3}) | **FAIL** | stub set = ∅ |
| C2 T2 (narrowing set == ∅) | **FAIL** | stub narrowing set = 11 fixtures |
| C2 T3 (carry-over identity incl. FA9/FB4 arms) | **FAIL** | 11/13 manifest rows differ; FA9/FB4 rows absent |
| C2 T4 (`SELFTEST pass cases=18`, pins) | **FAIL** | no SELFTEST line |
| C2 T5 (real-lane receipt/sorted/tool_pin ok, rc0) | **passes as written** | always-zero clause (see §4) |
| C2 T6 (row-set mutant fails) | **FAIL** | stub has no row-set machinery |

The prereg's own do-nothing sentences ("v4 … fails T1 by construction"; "an always-zero stub … would fail T1–T3") are accurate and conservative — the stub in fact fails T1–T6 (C1) and T1–T4+T6 (C2). The targets must fail the stub: **they do** → no DISAGREE from the control.

## 3. Clause-by-clause falsification table

Official differentials from my reproduced matrices (== committed bytes): C1 v4=0→v5≠0 is EXACTLY {F24-PAIR-HIDDEN-FILING, F26-INDENT4-COMMENT-OPENER, F28-NUL-CORRECTION-UNCHANGED}; v4≠0→v5=0 is EXACTLY {F29-PROSE-COMMENT-MENTION}; F17/F18/F19 exit 0 under both. C2: v4=0→v5≠0 is EXACTLY {FC1,FC2,FC3}; narrowing set ∅.

### C1 (calibration 7)

| target | predicate as written — falsifiable? | discriminated by committed fixtures? | holds? |
|---|---|---|---|
| T1 | Yes: a v5 that misses any of the three shapes (or fires elsewhere) breaks the exact set. F24's first finding UNFILED-SOURCES-ANNOTATION and its PAIR-FILING-HIDDEN second line both pinned — verified live (`FINDING UNFILED…` then `FINDING PAIR-FILING-HIDDEN`, receipts/f24-findings.txt) | Yes: v4 side is measured (all three rows 0), not assumed; stub fails | **HOLDS** |
| T2 | Yes: the finding-NAME change is the claim (prereg honestly scopes it: "a FINDING-NAME claim only: v4 already refused the shape, mislabelled") | Yes: stub keeps v4's rc and fails; a v5 that kept DELETED-LINES would fail | **HOLDS** |
| T3 | Formally falsifiable, but **zero v5-discriminating content**: the v5 expectation (rc1 CORRECTION-IN-FENCE) is identical to the committed v4 row, so T3 is implied by T5 + the v4 row — **holds by construction given T5**. Its real content is bookkeeping: the ERRATUM-R55-1 shape enters the frozen population | No (carry-over pin; the prereg labels it as such) | **HOLDS** (by construction) |
| T4 | Yes: exact narrowing set + F17/F18/F19 stay 0 under both (verified in both reproduced matrices) | Yes: stub inflates the set to 24; any v5 regression elsewhere lands here | **HOLDS** |
| T5 | Yes: identity on 27 named fixtures | Yes: stub fails 21; a v5 that broke any carried-over check fails | **HOLDS** |
| T6 | Yes against the frozen bytes (selftest ran: `SELFTEST pass cases=33`, rc0, with pins; receipt receipts/c1-selftest-critic.txt). Letter-level caveats in §4: a printing forger could emit the line, and pin verification is silent on success (mechanism proven live by my wrong-pin probes, both counters `CANNOT-EVALUATE PIN-MISMATCH`, EXIT=2) | Partially (line is forgeable; cases=33 pins the row count via `len(C1_FIXTURES)`) | **HOLDS** |
| T7 | **As written, passable by an always-exit-0 counter** — my stub reproduced the required fields verbatim. Discriminating only inside the conjunction with T1–T6 | No (alone) | **HOLDS** on the real instrument: my run at cce21b55 → rc0, `unfiled=0 … recomputed=79`, identical to the committed c1-tip.txt |
| T8 | Not an instrument predicate: any receipt-writer satisfies it | No | **HOLDS** on cited receipts: c1-selftest.txt, c1-tip.txt, c1-tip-v4-before-arm.txt all end `EXIT=0`. Letter note: the two committed controls print `observed-rc: 128` without an `EXIT=` trailer |

### C2 (coverage 8)

| target | falsifiable? | discriminated? | holds? |
|---|---|---|---|
| T1 | Yes (exact set + named finding) | Yes: v4 exits 0 on all three (measured); stub fails | **HOLDS** |
| T2 | Yes (empty narrowing set) | Yes: stub inflates to 11; any v5 narrowing lands here | **HOLDS** |
| T3 | Yes: identity on 15 rows incl. the FA9/FB4 selftest arms | Yes: stub fails 11 manifest rows and runs no FA9/FB4 arms | **HOLDS** |
| T4 | Yes against frozen bytes (`SELFTEST pass cases=18`, rc0, pins; receipts/c2-selftest-critic.txt); same forging/pin-silence caveats as C1 T6 | Partially | **HOLDS** |
| T5 | **Always-zero-passable as written** (stub passed verbatim); conjunctively guarded | No (alone) | **HOLDS** on the real instrument: my run at cce21b55 → rc0 `receipt=ok sorted=ok tool_pin=ok`, identical to committed c2-tip.txt |
| T6 | Yes — the strongest clause in either claim: genuinely discriminating | Yes: my scratch mutant (FA9 arm removed from the run list) → `SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN`, `SELFTEST fail cases=17`, **EXIT=1** (receipts/c2-mutant-rowset-selftest.txt) | **HOLDS** |
| T7 | Not an instrument predicate | No | **HOLDS** on cited receipts (c2-selftest.txt, c2-tip.txt, c2-tip-v4-before-arm.txt: `EXIT=0`) |

Note (asymmetry, not a defect): C1's selftest has no SELFTEST-ROW-MISMATCH mechanism — C1 T6 compensates via the literal `cases=33` count (a dropped builder fixture prints cases=32 and fails T6). C2 got the by-name row-set check because r55 mutation01 routed it; C1 has no equivalent routed item. If a r56+ attacker deletes a C1 arm *and* edits the count string, only the expected-TSV pin (`--expected-sha256`) catches it — that pin exists and fires (my wrong-pin probe).

Residual unfalsified surface: SUMMARY field values on fixture rows whose (rc, first finding) match (e.g., pairhidden= on rows other than F24). These are not pinned by any target clause, but they ARE pinned by byte-identity of the matrices (standing check), which I verified twice (official==dry-run; my rerun==both).

## 4. Real-lane legs, controls, and receipt hygiene (run by this seat)

- C1 recompute at measured rev: `python3 -B census/round-56/c1-counter.py --root <lane> --rev cce21b55… --base fafe3716… --record-sha256 2b90a262… --sources-rev-before f778b9d1… --sources-rev-after 9bf9234a… --scratch <scratch>` → rc0, `unfiled=0 record_sha=ok appended=ok … recomputed=79` (receipts/c1-reallane-critic.txt, `EXIT=0`). Matches T7 exactly and the committed c1-tip.txt.
- C2 recompute at measured rev with r55 capture/receipt + tool pin → rc0, `receipt=ok sorted=ok tool_pin=ok` (receipts/c2-reallane-critic.txt, `EXIT=0`). Matches T5 and c2-tip.txt.
- v4 before-arm on the real lane (committed c1-tip-v4-before-arm.txt): rc0 with the v4 SUMMARY shape (no `pairhidden=` field) — consistent with the prereg's claim that the F29 shape hides the SCORECARD tail without changing the current verdict (all corrections sit above line 1378; the committed probe-real-scorecard-hidden-tail.txt shows v4 hides 14 lines to EOF, v5 hides 0).
- Wrong-pin liveness: C1 `--builder-sha256 000…0` → `CANNOT-EVALUATE PIN-MISMATCH`, EXIT=2; C2 `--expected-sha256 deadbeef…` → same, EXIT=2.
- Absent-instrument controls (committed): record `observed-rc: 128` with the exact git cat-file command — reproducible and honest, but see the letter note on `EXIT=` below.

## 5. Honesty-of-wording findings (r13 discipline)

1. **Prereg line "ERRATUM-R55-1 closed: F7-FF2 pins the exact form-feed S1 shape"** — "closed" is stronger than the measured content: T3 is a carry-over pin with zero v5-discriminating power (§3). The closure consists of fixture-set bookkeeping, which is real, but the verb should be "pinned (carry-over)". No 'closes'-wholesale violation found elsewhere: "instruments" is used consistently across prereg, lesson Claims, and the knowledge entry (grep for closes/guarantees/proves/ensures/eliminates: only grammar descriptions match).
2. **Standing-check receipt contradicts the prereg's parenthetical**: prereg says the r46 landing-suite counter runs "at the round tip (exit 0)", but the committed post-freeze receipt `records/landing-suite-standing.txt` shows the r46 counter rejecting `--scratch` (its CLI takes `--work`) with a usage error, **EXIT=2**. Standing checks are "reported, not claimed", so no kill rule trips — but as committed, the receipt does not demonstrate the declared state. Routed item: re-run without `--scratch` and commit the honest receipt.
3. **"with the pins verified" (C1 T6, C2 T4)**: the success path prints no pin evidence (only mismatches print). The mechanism is live (my EXIT=2 wrong-pin probes) and the r55 wave has wrong-pin refusal receipts, but no r56 claim receipt demonstrates it. Suggest a `pins=ok` field in the SELFTEST line for the next freeze.
4. **Knowledge entry "so the defect was live, not only a fixture"**: accurate in the trigger sense (v4 really hides 14 real SCORECARD lines to EOF — probe receipt), but verdict-neutral at the measured revision (v4 real-lane rc0, before-arm receipt). The receipts themselves state exactly what was measured; no overclaim, noted for precision.
5. "Kill-power on 3 committed rows…" (lesson Claims): this is before/after differential power (v4 exit 0 → v5 exit 1), not mutation-suite kill power; the T4/T5 exact-set conjunction supplies the actual carry-over kill power. Shorthand is acceptable; the prereg's kill rules define it precisely.
6. Controls print `observed-rc: 128` rather than an `EXIT=` trailer — the exit code is present and unambiguous; flagging only because T8's parenthetical names the trailer form.

Named limits confirmed present and disclosed in both counter docstrings and the lesson (32-char zone, line-level comment grammar, first-unknown-key-only, LF-only numstat with differential receipt quotepath-differential.txt, fixed pair sites, CR-only files, rstripped fence closers). No undisclosed limit found by this seat's probes.

## 6. Verdict rationale

No C1 or C2 target holds by construction in the sense that matters (the only by-construction clause, C1 T3, is labeled a carry-over pin and still fails the stub; the always-zero-passable clauses C1-T7/C2-T5 pass my stub verbatim but are conjunctively guarded by detection clauses the stub fails). The frozen fixtures discriminate every detection clause; official == dry-run bytes; both real-lane legs reproduce at the measured revision; the row-set and pin mechanisms are live. Claims say "instruments", not "closes"; the two wording items (§5.1, §5.2) are documentation fixes, not falsifications.

**VERDICT: SURVIVED**

## Receipts (this seat dir, receipts/)

- pins-full-audit.txt — 12-pin sha256 audit at cce21b55 (EXIT=0)
- stub-c1-matrix.tsv, stub-c2-matrix.tsv — do-nothing stub arms over 33+16 manifest rows (EXIT=0)
- c1-selftest-critic.txt — v5 selftest with builder+expected pins, `SELFTEST pass cases=33` (EXIT=0)
- c2-selftest-critic.txt — v5 selftest with pins, `SELFTEST pass cases=18` (EXIT=0)
- c1-reallane-critic.txt, c2-reallane-critic.txt — real-lane legs at cce21b55 (EXIT=0)
- c2-mutant-rowset-selftest.txt — FA9-arm-removed mutant: SELFTEST-ROW-MISMATCH, cases=17 (EXIT=1)
- f24-findings.txt — F24 prints UNFILED-SOURCES-ANNOTATION then PAIR-FILING-HIDDEN (EXIT=0)
- wrongpin-c1-c2.txt — both counters refuse wrong pins (EXIT=2)

Tooling record (operator authorization): no tools installed or upgraded — stock python3, git, awk, sha256sum only; no pacman transactions (host-wide pause respected). Scratch /fast/scratch/hyaku/souji-r56/S56critic01/ deleted before yield; disk-guard checked before the heavy pass (406G free on /fast).
