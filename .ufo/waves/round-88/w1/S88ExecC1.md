# S88ExecC1 — C1 re-derivation (round 88)

Status: COMPLETE

## 1. Instrument hashes re-measured
All match the brief (sha256):
- c1-false-rows.tsv b710e368…388a68c3 (53 rows) ✓
- c1-mutants.json baec8026…bc66cec9c (12) ✓
- c1-mutants-dead.json e7963787…015281 (13) ✓
- c1-false-row-harness.py 1ae0cd39…72814042b ✓
- c1-clause-battery.py 6842ca47…24fa2c5ff7 ✓
- c1-pointer-counter.py (r87) fd0a8e24…f74a755220b ✓ (identical to lane base 7defe9c blob via `git show`)
- c1-items.tsv ce80195d…455178d2e9 ✓
- r88-k4-flagfail.py aa79133a…43e8335d ✓
- tools/souji-record-agreement.py c0604b4a…192e9a73e4fdef ✓
- controls/c2-before-tool.py e1b00e8a…f67ccc ✓
- controls/c2-before.txt 28e5ad68…37c8133dc2 ✓
- controls/c1-before.txt ce1352d2…35c7f ✓
- r87 c1-false-rows.tsv b066fa0f…18669220 (51 rows) ✓ (prereg pin)

## 2. Per-row attribution (hand-driven, frozen counter bytes)
Fixture: pristine arm's fixture (`after/run-r88-c1-pointer-counter/fixture`), R11=`b38e928…`, R10=`e5c9ebc…`;
counter SHA verified fd0a8e24… per invocation header.

### NF6g (m18 — `_whole` before-byte half)
Row: `NF6g fixture R11 r78 L06 QUARANTINED target=.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/git-stub got=REFUSED`.
One-row forge `NF6g L06 QUARANTINED <target> REFUSED` scored against r78 population+ledger at R11:
- PRISTINE: `FORGE NF6g item=L06 class=QUARANTINED expect=REFUSED got=REFUSED match=yes`, FORGE-SUMMARY forged=1 matched=1 accepted=0, exit 1 (forge-mismatch accounting).
- m18 mutant (`before_ok = True`): `FORGE NF6g … expect=REFUSED got=QUARANTINED match=no`, FORGE-SUMMARY forged=1 matched=0 accepted=1, exit 1.
- Cross: m17 mutant on NF6g → got=REFUSED match=yes (does NOT fire).
- Control: m18 at R10 (pre-R11 text absent) → got=REFUSED match=yes (fires only on R11 text).
- R11 line (from fixture corpus/lessons/round-79-collision.md): `- retired copy: xtests/vault/vadv54-run/p/p6repo/.git; quarantine slot `.ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/git-stub`.` — token `tests/vault/vadv54-run/p/p6repo/.git` occurs only inside `x…`, so the byte before it is `x` (a PATHCH byte). Only the before-byte half refuses.
- Sole killer: YES (m18 is the only r88-new mutant that moves NF6g; m17 does not).

### LD1 (m17 — `_ledger` duplicate-id refusal)
Row: `LD1 ledger BASE r77 P01 - - LEDGER-REFUSED 1`.
Harness-built duplicate ledger: frozen `census/round-77/c2-pointer-ledger.tsv` (32 lines) + appended `P01 ABSENT - r88 LD1 duplicate-id control` = 33 lines (`…/ledger-LD1.tsv`, sha256 9878aa47…).
Run WITHOUT forge, `--root lane --rev master(486826df…)` [harness uses BASE=e65538e7…; see §4 not-a-finding], `--population census/round-77/c2-population.tsv --ledger ledger-LD1.tsv`:
- PRISTINE (no mutant): prints `LEDGER-REFUSED id=P01 why=unknown or duplicate id`, `SUMMARY items=35 resolved=35 … refused=1`, EXIT 1. ← matches the acceptance criterion literally.
- m17 mutant (`if len(r) < 3`): NO `LEDGER-REFUSED` line; `ITEM P01 … status=REFUSED class=ABSENT why=exists under the fleet root` (the appended ABSENT row wins); `SUMMARY items=35 resolved=34 … refused=1`; EXIT 1. The harness `where=ledger` test sees `got=-` ≠ `LEDGER-REFUSED` → mism=1, battery kill=yes. So "last row wins, no marker" is proven, but the mutant's process exit is still 1 — the kill is attributable to the MISSING MARKER (and the P01 status flip FLEET→REFUSED), NOT to exit-code change. The LD1 row's expected `rc=1` does NOT discriminate by itself; the marker does. See §5 note.
  - Direction check: pristine+dup exit 1 (marker present); m17+dup exit 1 (marker absent). The naïve reading of "…exits 1" in the prereg would be misleading if read as an exit-code delta; the harness in fact keys on the marker (`got==exp_got`) plus `rc==int(exp_rc)` — both are 1, so the marker is the sole discriminator. Flagged as LOW documentation finding.
- Control (pristine + FROZEN ledger, no dup): `SUMMARY items=35 resolved=35 … refused=0`, no marker, EXIT 0. Proves the marker is caused by the duplicate, not by P01 itself.
- Cross: m18 mutant + dup ledger → still `LEDGER-REFUSED id=P01`, P01 status=FLEET (does NOT fire).
- Sole killer: YES (m17 alone moves LD1; m18 does not).

### Attribution table
| row | clause | mutant | pristine | mutant | sole killer |
|-----|--------|--------|----------|--------|-------------|
| NF6g (R11, L06) | `_whole` before-byte half (`before_ok`) | m18-whole-before | got=REFUSED match=yes | got=QUARANTINED match=no | YES |
| LD1 (ledger, P01) | `_ledger` duplicate-id (`r[0] in ledger`) | m17-duplicate-id | LEDGER-REFUSED id=P01 exit 1 | no marker, P01→REFUSED/ABSENT, exit 1 | YES (marker-delivered) |

## 3. Instrument diffs (r87 → r88)
### Population c1-false-rows.tsv
- r87 51 data rows are a strict prefix of r88 (byte-identical, in order); new rows appended: NF6g, LD1. Command-verified (`h88[:51]==h87`). r87 file sha b066fa0f… matches prereg pin; r88 sha b710e368… matches brief.
- Header comment in r88 file is inherited r87 text (starts `# souji r87 C1 population…`) — not a sha change, cosmetic.

### c1-mutants.json (r87 → r88)
- First 10 members byte-identical (parsed JSON equality); appended m17-duplicate-id, m18-whole-before. Single hunk `@@ -66,6 +66,20 @@` (pure addition). No other line changed.
- c1-mutants-dead.json = c1-mutants.json + m19-len-half (verified `r88 == dead[:12]`, `r87 == dead[:10]`). m19 old occurs exactly once in the counter (checked for all 13).

### c1-clause-battery.py (r87 → r88)
Two hunks only:
- Docstring: prepend r88 paragraph (notes: one more PINS entry, counter unchanged; "No arm, kill rule or summary line changed"). The original r87 docstring text is preserved verbatim below it (verified: the `+` lines add 6 lines, the old lines are retained — diff shows `+souji r87 …` as a copy, not a replacement of content).
- PINS: r87 entry retargeted `os.path.join(HERE, "c1-false-rows.tsv")` → `os.path.join(FLEET, "souji-shokunin/census/round-87/c1-false-rows.tsv")`, plus new r88 entry `(HERE, b710e368…, 53)`. Frozen with same pins for r83–r86.
- No arm, kill rule (`rc!=0 or mism>0 or errs>0`), summary format, or mutant-apply logic changed. UNEXPECTED LINES: none. The path retarget is the disclosed mechanical rebase (HERE moved to round-88), not a pin change.

### c1-false-row-harness.py (r87 → r88)
Five hunks, all disclosed:
- Docstring prepended (7 lines): NF6g/R11 + LD1/`where=ledger` described; "No judgement code changed".
- POP_PINS: append r88 sha `b710e368…: 53`.
- build_fixture: R11 block appended after R10 (append `xtests/…/git-stub` declaration line, commit `r88 C1 fixture R11 (longer-path before-byte declaration)`, `revs["R11"]=…`; add `git-stub` to the disk-only leaf loop). Uses the already-defined `q6` prefix.
- Rev-label allowlist: append `"R11"`.
- main loop: `where` now validated against `{lane,fixture,ledger}` (was implicit binary); `where in (lane,ledger)` ⇔ BASE; new `where=="ledger"` branch: builds `ledger-<rid>.tsv` = frozen ledger + `\n` guard + `f"{item}\tABSENT\t-\tr88 {rid} duplicate-id control"`; runs counter with that ledger WITHOUT forge; parses `LEDGER-REFUSED id={item}` as `got`; rc==2 → errors+=1; else `ok = (got==exp_got) and (exp_rc=="-" or rc==int(exp_rc))`, `mism+=0 if ok else 1`, prints `ROW … got=LEDGER-REFUSED/- rc=… match=…`.
- The `_ledger` handling in the normal (non-ledger) path is untouched. UNEXPECTED LINES: none found. One judgment-call note: the ledger branch's `ok` test also requires `rc==int(exp_rc)` (1) — satisfied by both pristine and m17-mutant (see §5), so discrimination rests entirely on `got`. This is the disclosed design, not drift.

## 4. Belt (m19-len-half)
- File `c1-mutants-dead.json` = 12 + m19 (verified). m19 `old` = `return bool(want) and len(want) <= len(have) and have[-len(want):] == want` occurs exactly once (line 360 of the counter, `_capture_ok`).
- Filed belt receipt `census/round-88/records/c1-dead-belt.txt` (hash-consistent, EXIT=0): m19-len-half `killed=no` BOTH sets, `SUMMARY mutants=13 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22 EXIT=0`.
- Seat's own belt re-run (c2.txt) PENDING full battery completion; hand-check of the `old` text uniqueness + code reading: `_capture_ok`'s callers are `_owntree_ok` (guarded by `len(want)<2 or len(got)<2` before the call, m14) and the census-branch guard in `judge` (line 426/430, `token[:kr.start(0)]=="census"` + not `_capture_ok`). Dropping the len half cannot make a longer `want` a suffix of a shorter `have` pass (`have[-len(want):]==want` is already false when `len(want)>len(have)`) — the len half is what Python slicing already enforces. Consistent with r87 A10 D2b "same kill vector". No falsification found; belt sentence stands. Final battery verdict to be appended on completion.
- HIGH falsification check: if the re-run kills m19 on either set, this note is withdrawn and reported as HIGH. Filed record says survivor.

## 5. Notes / minor findings
- LOW (documentation): prereg/counter text says of LD1 "must print LEDGER-REFUSED … and exit 1" / "with the duplicate check dropped the last row wins and the counter exits 0, so the row goes red" (mutants.json note). Measured: m17 mutant exits 1 (the appended ABSENT class then refuses P01 as "exists under the fleet root", making resolved=34). The kill IS real — the harness keys on the missing marker — but the "exits 0" phrase in the mutant note is inaccurate. The prereg's kill rule ("accepted without LEDGER-REFUSED and exit 1") is phrased correctly (marker AND exit 1); the JSON note overstates the exit-code delta. Recommend L1 reword the note; not a claim falsification, the mechanism (marker delivered) matches the prereg wording exactly.

## 6. Battery verdicts (final receipts in §7)
- Pristine arms in seat's own runs (§7): `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, `ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0`.
- Filed receipts `census/round-88/records/c1-after.txt`, `census/round-88/records/c1-dead-belt.txt`, `census/round-88/controls/c1-before.txt` are byte-identical to the seat's runs on all ARM/MUTANT/SUMMARY lines (§7 diff).
- Filed before receipt `census/round-88/controls/c1-before.txt` matches prereg: ten killed=yes, m17/m18 killed=no, `SUMMARY mutants=12 sets=r87 pristine_r87=ok killed_r87=10 killed_total=10 EXIT=0`.

Report trailer: .ufo/waves/round-88/w1/S88ExecC1.md
Scratch: DELETED before yield (`rm -rf /fast/scratch/hyaku/souji-r88/S88ExecC1`); receipts copied to `.ufo/waves/round-88/w1/S88ExecC1/` (c1-after-seat.txt, c1-before-seat.txt, c1-belt-seat.txt, ld1-pristine.txt, ld1-m17.txt, harness/battery/mutants.diff). No scratch left behind.
## 7. Seat's independent full battery re-run (no-deadline, exit 0 on all three)
Commands run from the lane root with cwd=/home/vgpnk/Projects/shokunin/souji-shokunin, work dirs under the seat's own scratch (copied to the seat dir before scratch deletion):
- after: `python3 -B census/round-88/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --work <scratch>/a2 --only r87,r88 --expect-killed 22` → EXIT 0. Receipt: `.ufo/waves/round-88/w1/S88ExecC1/c1-after-seat.txt` (sha256 e776351d…).
  `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`
  `ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0`
  Twelve `MUTANT-PAIR … killed=yes` on pop=r88; `SUMMARY mutants=12 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22`.
- before: same, `--only r87 --expect-killed 10` → EXIT 0. Receipt `c1-before-seat.txt` (be8ba004…).
  `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`, ten `MUTANT-PAIR killed=yes`, `m17-duplicate-id killed=no`, `m18-whole-before killed=no`, `SUMMARY mutants=12 sets=r87 pristine_r87=ok killed_r87=10 killed_total=10`.
- belt: same as after + `--mutants census/round-88/c1-mutants-dead.json` → EXIT 0. Receipt `c1-belt-seat.txt` (ffabd0ae…).
  `MUTANT-PAIR m19-len-half pop=r87 killed=no … | pop=r88 killed=no …`, `SUMMARY mutants=13 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22`.
- Verdict: all three claims' numbers re-derived EXACTLY as prereg states. Battery-exit line: the script prints no `EXIT=` line; `EXIT=0` in filed receipts is the L1's echo of the process exit. Seat+filed ARM/MUTANT/SUMMARY lines are byte-identical (only `EXIT=0` differs — appended by L1 when filing).
- The earlier truncated after/before runs (300s default shell kill) are NOT used: their partial receipts were discarded and re-run with `timeout: 0`. Final receipts above supersede them.

## Verdict
- C1 after/before/belt: RE-DERIVED EXACTLY (all SUMMARY lines, both pristine arms green, 10/12/12 kill split, m19 survivor). No falsification of the stated wording found.
- One LOW documentation finding: `c1-mutants.json` m17 note says the mutant "exits 0" — measured exit is 1 (the appended ABSENT class then refuses P01); the kill is delivered by the missing `LEDGER-REFUSED` marker, which IS the prereg's kill rule. Not a claim failure.
- Instrument diffs: zero unexpected lines (harness = docstring + pin + R11 block + rev-list + ledger branch; battery = docstring + PINS retarget; mutants = pure append).
- Per-row sole-killer attribution: NF6g→m18 YES, LD1→m17 YES (marker-delivered).
- Belt sentence stands: m19-len-half survived both sets in the seat's own run.
