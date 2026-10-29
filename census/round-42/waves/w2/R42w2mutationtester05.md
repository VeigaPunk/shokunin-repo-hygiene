# R42w2mutationtester05 — mutation test of the landed C3 counter (round 42, wave 2, falsify)

Role: mutation-tester (leaf). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. Landed tip under attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`. Frozen counter `census/round-42/c3-counter.py` sha256 `bf0ebf4fef0cf0070daf2dd89184e83575bfabe4e4e82fa50511b3c6c8585d76` (matches the tip blob and the copy I mutated). Lane never written; frozen-file hashes checked before and after (`receipts/frozen-hashes-before.txt`, `receipts/frozen-hashes-after.txt`: identical).

Seat directory: `.ufo/waves/round-42/w2/R42w2mutationtester05/` (receipts, mutants, drivers). Scratch `/fast/scratch/hyaku/souji-r42/R42w2mutationtester05/` (clone, job dirs) removed before this report was written; every receipt cited below sits in the seat.

## Verdict

- **33 single-point mutants** of the counter (target was at least 25), grouped by the counter's own legs: kill definition (6), equivalence guard (5), thresholds (5), anchors check (4), prior leg (4), pristine minimum (2), scratch handling (4), reporting (3). Each mutant copy differs from the pristine copy by exactly one line replaced by one line (`receipts/mutant-inventory.tsv`, all 33 at −1/+1).
- **Measured against the three artifacts** (`census/round-42/controls/c3-stub-allpass.py`, `c3-stub-sniff.py`, `tests/fixtures/r42-drift-conditions.py`), with pristine baseline and three identical replicate runs of the pristine counter for the noise floor:
  - **9 mutants are DET-VISIBLE**: a printed field that the pristine counter reproduces exactly in all four pristine runs moves (K4, K5, A3, A4, P4, G2, M1, M2, M3).
  - **6 mutants change no printed SUMMARY field on any artifact** (strict blind spots): K1, K2, K3, T1, T3, T4. Two of these (T1, T3) are visible only through the exit code, because SUMMARY never prints `met`.
  - **18 mutants move only `old_killed` or `prior`**, the two fields the pristine counter itself moves across identical runs under load. For these the three artifacts give no evidence either way: not a kill, not a proven blind spot.
- **Counter-side defects found (named limits for L1; not edited, frozen file untouched):**
  1. **The frozen target is not reproducible at the host's load.** Three identical pristine runs on the landed fixture printed `old_killed=0`, `0`, and `2`; the `2` run exits 1 (`met` requires `old_killed == 0`). At load average 100–140 the frozen counter reads the landed tip red once in three runs. The fixture is not implicated: its own pristine line reads `pristine=ok killed=13 ... prior=8/8`; the flake is in the prior leg (`receipts/analysis2.txt`, noise-floor block).
  2. **The `prior` field cannot say which prior fixture failed.** It prints `prior=7/8` for a seven-entry tuple (P1, deterministic) and also for a run where one prior fixture returned no clean SUMMARY (four flake occurrences in 99 non-P1 matrix runs, `receipts/analysis2.txt`). Nothing in SUMMARY tells the two apart.
  3. **The `old_killed` leg has no demonstrated deterministic kill power on these artifacts.** P3 (`if args.survey or True:` → `if args.survey:`) disables the prior grid by default, which forces `old_killed` to 0 on every run. It moves no printed field relative to a pristine run that also reads 0. The only values the leg ever printed other than 0 were load-flake values 1–3 and the forced 13 of P4.
  4. **The all-pass control kills no kill-definition mutant.** `c3-stub-allpass.py` exits 0, so every mutant of `killed()` that still requires `rc == 1` (K1, K2, K3, K6) cannot count it killed; its `killed=0` survives all six kill mutants. Only stub-sniff (rc 1, fail 13) registers the kill-definition family (K4 drops it to `killed=0`; K5 shows the landed fixture's kills drop to 2 of 13 when `failed > 1` is required).
  5. **Unexercised legs.** No committed artifact exercises: a non-0/1 exit with a consistent SUMMARY (K1, C1); a fail-0 exit-1 run (K2); a traceback with exit 1 (K3, C4); `passed > cases` (C2); `failed == 1` with `passed == cases` (C3); a prior fixture failing on the pristine tool (P2); a candidate with 1–12 cases (G1); a population/anchor mismatch (A1); `prior_ok` at 6–7 or `killed_n` at 12 (T1, T2) except by flake.
  6. **Scratch handling is partly invisible.** S1 (`rmtree(work)` removed) leaves nothing on disk: the nested work dirs sit inside the counter's own scratch dir, which the outer `finally` removes (measured: 0 leftovers). S3 (outer `rmtree(scratch)` removed) leaves one `souji-r42-c3.*` directory (measured: 1 leftover). Neither moves a SUMMARY field.
  7. **Equivalent mutants (not gaps).** C5 is provably equivalent (below). T4 and T5 change a comparison against a frozen tuple length (6 and 13), so they cannot differ on this counter. A2 skips a check that cannot fail once the pinned-SHA gate passes.

## Commands run (exact) and observed output

All commands ran as uid `vgpnk` (never root). Host load average during the run ranged 70–140 (`uptime`). No tool was installed or upgraded.

1. Frozen-counter identity:
   `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3105a63b23481fccf7df58e74d14a6681e0ea0c8:census/round-42/c3-counter.py | sha256sum` → `bf0ebf4fef0cf0070daf2dd89184e83575bfabe4e4e82fa50511b3c6c8585d76  -` (equal to the working-tree file and to the copy I mutated).
2. Scratch clone (read-only source; no lane writes):
   `git clone --no-local --quiet <lane> <scratch>/clone && git -C <scratch>/clone checkout --quiet 3105a63…` → `git -C … rev-parse --show-toplevel` = `<scratch>/clone`; `HEAD` = `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
3. Full-counter baseline on the clone (pristine copy, `--root clone`, real tip):
   `python3 -B clone/census/round-42/c3-counter.py --root clone --rev 3105a63… --scratch <dir>` → printed `MUTANT B1 candidate=killed …` through `EQUIV H4 candidate=survived …` (matches the landed `records/c3-after.txt`), then
   `SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`
   (wall 175 s; exit status not captured because the output was piped through `tail`).
4. Stub calibration: same with `--fixture census/round-42/controls/c3-stub-allpass.py` → `SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247` (wall 42 s; exit not captured).
5. Matrix: `python3 -B .ufo/waves/round-42/w2/R42w2mutationtester05/driver.py 5` → `built 33 mutant counter copies`, then `DONE 102 records` (33 mutants + pristine, each × three artifacts). Driver log: `receipts/driver.log`. Each record: `receipts/<mutant>__<artifact>.json` (+ `.out`, full stdout).
6. Mutant P1 repair: the first P1 copy (`, "tests/fixtures/r41-refusal-sites.py")` → `")`) left the `PRIOR` tuple unterminated: the counter raised `SyntaxError`, three records had `summary=null`. I replaced the anchor with `, "tests/fixtures/r41-refusal-sites.py")` → `)` (driver line 69), re-compiled the copy (`P1 compiles; anchor count ok`), and reran it on the three artifacts: `P1 stub-allpass … prior=7/8 … anchors=ok`, `P1 stub-sniff … prior=7/8`, `P1 landed-fixture … prior=7/8`. The three broken records were overwritten.
7. Noise floor: `python3 -B …/replicate.py 3` → nine pristine runs (3 per artifact), `DONE 9 replicate records` (`receipts/replicate.log`). Results (all rc/summary from `receipts/analysis2.txt`):
   - stub-allpass: `old_killed=0`, `0`, `1` (all `prior=8/8`)
   - stub-sniff: `old_killed=0`, `1`, `0`
   - landed-fixture: `rc=1 old_killed=2`, `rc=0 old_killed=0`, `rc=0 old_killed=0`
8. Strict comparison (raw SUMMARY vs pristine, `analyze.py` → `receipts/analysis.txt`): six mutants identical on all three artifacts (K1 K2 K3 T1 T3 T4).
9. Noise-aware classification (`analyze2.py` → `receipts/analysis2.txt`, `receipts/table2.json`): `== VERDICT COUNTS == {'BLIND': 6, 'DET-VISIBLE': 9, 'NOISE-CONSISTENT': 18}`. Acceptance table generated by `table.py` → `receipts/acceptance-table.md`.
10. Flake frequencies over the 99 non-P1 matrix runs: `old_killed` 0 in 69, 1 in 23, 2 in 3, 3 in 1, and 13 in 3 (P4, forced). `prior` 8/8 in 95, 7/8 in 4. Landed-fixture exit 0 in 17 runs, 1 in 16 (mutant-caused and flake-caused combined).
11. Scratch-leak probe, stub-allpass, `--scratch <dir>` with `TMPDIR` set to the same dir: pristine `leftovers=0`, S1 `leftovers=0`, S3 `leftovers=1` (`receipts/leak-pristine.out`, `leak-S1.out`, `leak-S3.out`).
12. Frozen-file check before and after: `receipts/frozen-hashes-before.txt` = `receipts/frozen-hashes-after.txt`; command `diff` printed nothing and `FROZEN HASHES UNCHANGED` was echoed.

## Acceptance table

Each cell compares the mutant counter's printed SUMMARY with the pristine counter's SUMMARY for the same artifact. `identical` = every printed field equal. `det` = a DET field moved (killed, survived, equiv, equiv_killed, mutants, pristine, anchors, cases). `(flake)` = only `old_killed`/`prior` moved, inside the observed flake range. `exit N` = exit status differs from the pristine run. Raw SUMMARY lines are in each `receipts/<id>__<artifact>.json`.

Pristine baseline (verbatim, `receipts/analysis2.txt`):
- stub-allpass: `rc=1 SUMMARY mutants=13 killed=0 survived=13 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`
- stub-sniff: `rc=1 SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=6 anchors=ok cases=13 tool_sha=b2a603cf4247`
- landed-fixture: `rc=0 SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`

| counter mutant | change (old -> new) | stub-allpass | stub-sniff | landed-fixture | verdict |
|---|---|---|---|---|---|
| K1 kill-definition | `rc == 1 and failed > 0 and not crash` -> `rc != 0 and failed > 0 and not crash` | identical | identical | identical | BLIND |
| K2 kill-definition | `and failed > 0 and not crash` -> `and failed >= 0 and not crash` | identical | identical | identical | BLIND |
| K3 kill-definition | `and rc == 1 and failed > 0 and not crash` -> `and rc == 1 and failed > 0` | identical | identical | identical | BLIND |
| K4 kill-definition | `rc == 1 and failed > 0` -> `rc == 0 and failed > 0` | identical | killed:13->0; survived:0->13; equiv_killed:6->0 | killed:13->0; survived:0->13; exit 1 | DET-VISIBLE |
| K5 kill-definition | `and failed > 0 and not crash` -> `and failed > 1 and not crash` | identical | identical | killed:13->2; survived:0->11; exit 1 | DET-VISIBLE |
| K6 kill-definition | `cases is not None and rc == 1` -> `rc == 1` | (flake) old_killed:0->2 | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| C1 equivalence-guard | `rc == 0 and failed == 0 and passed == cases and not crash` -> `rc != 1 and failed == 0 and passed == cases and not crash` | identical | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| C2 equivalence-guard | `passed == cases and not crash` -> `passed >= cases and not crash` | identical | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| C3 equivalence-guard | `failed == 0 and passed == cases` -> `failed <= 1 and passed == cases` | identical | (flake) old_killed:0->1 | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| C4 equivalence-guard | `failed == 0 and passed == cases and not crash` -> `failed == 0 and passed == cases` | (flake) old_killed:0->1 | (flake) old_killed:0->1 | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| C5 equivalence-guard | `cases is not None and rc == 0` -> `rc == 0` | identical | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT (provably equivalent, see F7) |
| T1 threshold | `and prior_ok == 8` -> `and prior_ok >= 6` | identical | identical | identical | BLIND |
| T2 threshold | `and killed_n == 13` -> `and killed_n >= 12` | (flake) old_killed:0->2 | (flake) old_killed:0->1 | (flake) old_killed:0->3; exit 1 | NOISE-CONSISTENT |
| T3 threshold | `and old_killed == 0` -> `and old_killed <= 1` | identical | identical | identical | BLIND |
| T4 threshold | `and len(EQUIV) == 6` -> `and len(EQUIV) >= 5` | identical | identical | identical | BLIND (equivalent on this counter) |
| T5 threshold | `len(MUTANTS) == 13` -> `len(MUTANTS) >= 12` | (flake) old_killed:0->1 | identical | identical | NOISE-CONSISTENT (equivalent on this counter) |
| A1 anchors-check | `anchors = "ok" if got == want else "FAIL"` -> `… else "ok"` | identical | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT |
| A2 anchors-check | `if source.count(old) != 1:` -> `if source.count(old) != 1 and False:` | (flake) old_killed:0->1 | identical | identical | NOISE-CONSISTENT (equivalent under pinned SHA, see F7) |
| A3 anchors-check | `got[f[0]] = f[2]` -> `got[f[0]] = f[1]` | anchors:ok->FAIL | anchors:ok->FAIL | anchors:ok->FAIL; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| A4 anchors-check | `if n and len(f) >= 3:` -> `if n and len(f) >= 3 and f[0] != "B1":` | anchors:ok->FAIL | anchors:ok->FAIL | anchors:ok->FAIL; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| P1 prior-leg | `, "tests/fixtures/r41-refusal-sites.py")` -> `)` | (flake) prior:8/8->7/8 | (flake) prior:8/8->7/8 | (flake) prior:8/8->7/8; exit 1 | NOISE-CONSISTENT (deterministic 7/8; indistinguishable from flake, F2) |
| P2 prior-leg | `prior_ok = sum(… and clean(pre[p].result()))` -> `prior_ok = sum(… if p in fixtures)` | (flake) old_killed:0->1 | identical | identical | NOISE-CONSISTENT |
| P3 prior-leg | `if args.survey or True:` -> `if args.survey:` | (flake) prior:8/8->7/8 | identical | identical | NOISE-CONSISTENT (dead old_killed leg, F3) |
| P4 prior-leg | `old_killed += 1 if by else 0` -> `old_killed += 1` | old_killed:0->13 | old_killed:0->13 | old_killed:0->13; exit 1 | DET-VISIBLE |
| G1 pristine-minimum | `cand_pre[1] >= 13` -> `cand_pre[1] >= 1` | (flake) old_killed:0->1; (flake) prior:8/8->7/8 | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT |
| G2 pristine-minimum | `cand_pre[1] >= 13` -> `cand_pre[1] >= 14` | pristine:ok->FAIL | pristine:ok->FAIL | pristine:ok->FAIL; exit 1 | DET-VISIBLE |
| S1 scratch-handling | `shutil.rmtree(work, ignore_errors=True)` -> `pass` | identical | (flake) old_killed:0->1 | identical | NOISE-CONSISTENT (no disk trace, F6) |
| S2 scratch-handling | `e["TMPDIR"] = work` -> `e["TMPDIR"] = scratch` | identical | (flake) old_killed:0->2 | identical | NOISE-CONSISTENT |
| S3 scratch-handling | `shutil.rmtree(scratch, ignore_errors=True)` -> `pass` | (flake) prior:8/8->7/8 | identical | identical | NOISE-CONSISTENT (leaves 1 dir on disk, F6) |
| S4 scratch-handling | `mkdtemp(prefix="souji-r42-c3.", dir=scratch_root)` -> `… dir=None)` | identical | identical | (flake) old_killed:0->1; exit 1 | NOISE-CONSISTENT (invisible when `--scratch` = `TMPDIR`, as in every run here) |
| M1 reporting | `len(MUTANTS), killed_n, len(MUTANTS) - killed_n,` -> `len(MUTANTS) - 1, …` | mutants:13->12 | mutants:13->12 | mutants:13->12; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| M2 reporting | `equiv_killed += 1 if cand else 0` -> `equiv_killed += 1` | equiv_killed:0->6 | (flake) old_killed:0->1 | equiv_killed:0->6; (flake) old_killed:0->1; exit 1 | DET-VISIBLE |
| M3 reporting | `for mid, _d, _o, _n in EQUIV:` -> `… in MUTANTS:` | (flake) prior:8/8->7/8 | equiv_killed:6->13 | equiv_killed:0->13; exit 1 | DET-VISIBLE |

Summary of the table: DET-VISIBLE 9 (K4 K5 A3 A4 P4 G2 M1 M2 M3). Strict blind (no printed field on any artifact): 6 (K1 K2 K3 T1 T3 T4). Noise-consistent: 18.

## Findings (what each attacks)

**F1 — `old_killed` leg and the frozen target (attacks: C3 kill/target reproducibility, L1 landing evidence).** Nine identical pristine runs of the same bytes on the same tip printed `old_killed` 0, 0, 1, 0, 1, 0, 2, 0, 0 and `rc` 1 on the landed fixture in one run (`receipts/analysis2.txt`, noise-floor block). The leg counts prior-fixture kills of the 13 real tool mutants (`c3-counter.py:235-237`); those 13 mutants are identical in every run, so the variation is the prior fixtures (each run has a 300 s timeout, `c3-counter.py:138`) reading differently under load. This matches N-C3b in the lesson and M42-4's r36 flake, and quantifies it: under load the frozen counter cannot reproduce `old_killed=0` on its own tip. Shown by replicate, not by mutant. Attacks the frozen counter's target reproducibility; the fixture is not implicated (its own `pristine=ok killed=13` in every run).

**F2 — the `prior` field is non-diagnostic (attacks: C3 prior leg, `prior=8/8` target).** `prior=7/8` arises both from a seven-entry tuple (P1, deterministic) and from one prior fixture returning no clean SUMMARY (stub-allpass under G1, S3, M3: four flake occurrences in 99 non-P1 matrix runs). SUMMARY does not name the failing fixture (`c3-counter.py:218`), so the two cases cannot be separated from the printed line. The format string hard-codes `/8` (`c3-counter.py:246-249`), so a shorter tuple reads as a short prior, not as a different tuple.

**F3 — the `old_killed` leg has no demonstrated deterministic power on these artifacts (attacks: C3 prior leg, `old_killed==0` target).** P3 disables the prior grid unless `--survey` (`c3-counter.py:226`), forcing `old_killed=0` on every run. Against a pristine run that prints 0 it is invisible (analysis: P3 identical to pristine on stub-sniff and landed-fixture). The only nonzero values the leg produced were flake values 1–3 and the forced 13 of P4. So on the three artifacts the leg reads flake, not kills, and T3 (`old_killed <= 1`) is exit-visible only when a flake produces exactly 1.

**F4 — the all-pass control kills no kill-definition mutant (attacks: C3 control design, the `killed()` leg).** `c3-stub-allpass.py` exits 0 with `fail=0`. Each kill-definition mutant that still requires `rc == 1` (K1, K2, K3, K6) leaves it `killed=0`; K4 and K5 keep it at 0 too. Only stub-sniff (rc 1, fail 13) registers the kill family: K4 drops its `killed` from 13 to 0 and its `equiv_killed` from 6 to 0; K5 drops the landed fixture's `killed` from 13 to 2 (eleven of thirteen kills have exactly one failing case). Shown in `receipts/analysis2.txt`.

**F5 — unexercised legs (attacks: C3 population/artifact coverage).** The three artifacts never reach these branches, so the matching mutants are invisible in SUMMARY (not equivalent, just unreached): K1 (rc other than 0/1 with a consistent SUMMARY), K2 (rc 1 with fail 0), K3 (a traceback with rc 1 and fail > 0), C1 (rc 2 with fail 0 and pass == cases), C2 (pass > cases), C3 (fail 1 with pass == cases), C4 (traceback on an otherwise clean run), P2 (a prior fixture failing on the pristine tool; none does), G1 (a candidate with 1–12 cases), T1 (prior_ok 6–7 except by flake), T2 (killed_n 12), A1 (population mismatch; the population matches at the tip). [INFERENCE: these are reachable by inputs the counter could receive; none of the three artifacts supplies them.]

**F6 — scratch handling is partly invisible (attacks: C3 scratch leg).** Measured: pristine leaves 0 entries, S1 leaves 0 (its nested work dirs are removed by the outer `rmtree(scratch)`, `c3-counter.py:255`), S3 leaves 1 (`receipts/leak-S3.out`). S3's leak is on disk, not in any SUMMARY field. S4 (`dir=None`) is invisible whenever `--scratch` equals `TMPDIR`, which every run here used (static reasoning, `c3-counter.py:200`; not separately measured with `--scratch` ≠ `TMPDIR`).

**F7 — equivalent mutants (not gaps).** C5: when `cases is None`, `failed` is `None`, so `failed == 0` is already false; dropping `cases is not None` (`c3-counter.py:158`) cannot change `clean()` [INFERENCE from the code, consistent with the observed identical rows]. T4 and T5 compare against frozen tuple lengths of 6 and 13 (`c3-counter.py:251`), so on this counter they are equivalent. A2 removes a refusal that cannot fire once the pinned-SHA gate has passed and the pinned anchors are unique (`c3-counter.py:186`) [INFERENCE: the pinned bytes are fixed].

**F8 — the three artifacts do discriminate on the mutants that matter for the population (attacks: artifact sensitivity).** Deterministic sensitivity: the anchors check (A3, A4), the pristine minimum (G2), the mutant count (M1), and the equivalence count (M2, M3, K4, K5). The byte-sniffing control catches the six equivalents (`equiv_killed=6`), so the equivalence guard is not a counter-side gap. The landed fixture kills all 13 real tool mutants in every run in which it is the candidate (pristine + three replicates = four runs).

## Limits of this evidence

- Load average was 70–140 for the whole session; every flake statement is measured at that load, not at the L1's landing load.
- Exit statuses of the full-counter baseline and the stub calibration were not captured (piped through `tail`). The pristine and replicate runs carry exact exit codes.
- The noise classification is by observed range (old_killed 0–3, prior 7/8|8/8), not a proof of flake mechanism. The mechanism (prior-fixture timeout under load) is [INFERENCE]: SUMMARY does not name the failing prior fixture.
- Equivalence claims C5, T4, T5, A2 are static reasoning, labelled above; the others are measured or unexercised.
- Scratch-leak measurement was run on the stub only (≈100 s), not on the landed fixture.
- No counter mutant was run against a different fixture than the three named artifacts; the 13 real tool mutants and the eight prior fixtures were used exactly as the frozen counter uses them.

## Tools and channels

No tool was installed, upgraded or removed. Python 3 (host) ran every script; `git` read-only (`clone --no-local`, `checkout`, `rev-parse`, `show`, `cat-file` in the scratch clone). No git mutation, no jj, no write to the lane or to the fleet, no `~/.local/bin` change.

## Files in the seat

- `driver.py` (mutant table, runner), `replicate.py` (noise floor), `analyze.py` (strict raw comparison), `analyze2.py` (noise-aware classification), `table.py` (acceptance-table generator), `c3-counter.pristine-copy.py` (byte copy of the frozen counter, sha `bf0ebf4f…`), `mutants/mut-*.py` (33 mutant copies + P1 repaired copy).
- `receipts/`: per-run JSON and stdout (`<id>__<artifact>.json|.out`, `PRISTINE__…`, `REP<k>__…`), `driver.log`, `replicate.log`, `analysis.txt`, `analysis2.txt`, `table2.json`, `acceptance-table.md`, `mutant-inventory.tsv`, `leak-*.out`, `frozen-hashes-before.txt`, `frozen-hashes-after.txt`.
