# SwarmReviewer05 — audit of landed C1 rows N27–N34 (SCORECARD.md:422)

Rev audited: `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93` (C1 rows landing, "round-32: C1 capability-count binding rows (38 of 44 items: 21 bound, 17 withdrawn; 6 left unbound)"). Base `85b61a151923986e7e6b48f7084b9122561b5f3d`, list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`. Scratch `/fast/scratch/hyaku/souji-r32/AuditC1N27N34/` (clone origin removed, detached at the rev; removed before finish). No tools installed (none needed).

## Status

`STATUS: PASS` — of the 8 assigned items, exactly 2 rows landed (N27, N32), both the cell's OWN evidence (HONEST); the other 6 landed with no row and the absence is correct (no admissible observable exists under the frozen v1/v2 rules — closure proven per kind below); zero `withdrawn:` rows in range; one gameability hole in the FROZEN counter reproduced as ATTACK (unused by the landing). The C1 claim itself is MISSED at this commit, and the miss is overdetermined (unbound=6, mismatches=6, withdrawn=17 > 8), exactly as the L1 recorded.

## Evidence

**1. Counter runs (pasted verbatim).** Both counters, same args, `--only N27,…,N34`, at the landing rev:

```
===== c1-counter-v2.py --only N27..N34 @ 9e8982b =====
ITEM	N27	SCORECARD.md:422	literal=items=41	binding=record	MATCH	census/round-31/records/c1-after-a4.txt:43
ITEM	N28	SCORECARD.md:422	literal=20	binding=-	UNBOUND
ITEM	N29	SCORECARD.md:422	literal=20	binding=-	UNBOUND
ITEM	N30	SCORECARD.md:422	literal=1	binding=-	UNBOUND
ITEM	N31	SCORECARD.md:422	literal=1	binding=-	UNBOUND
ITEM	N32	SCORECARD.md:422	literal=unbound=22	binding=record	MATCH	census/round-31/records/c1-before.txt:43
ITEM	N33	SCORECARD.md:422	literal=34	binding=-	UNBOUND
ITEM	N34	SCORECARD.md:422	literal=41	binding=-	UNBOUND
SUMMARY items=8 bound_run=0 bound_record=2 bound_field=0 withdrawn=0 unbound=6 mismatches=6 partial=1 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93
v2-exit=1
===== c1-counter.py (v1) --only N27..N34 =====
[identical 8 ITEM lines and SUMMARY; v1-exit=1]
```

**2. The cell (base line 422, `SCORECARD.md` @ 85b61a15).** Evidence column names the command `python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, quotes "SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1", and cites exactly three basenames: `c1-after-a4.txt`, `c1-before.txt`, `c1-cells.tsv`. No `.json` basename, no `*` glob token on the line.

**3. Bound records (blobs unchanged base→landing; `git diff --stat` empty for all four cited paths).**
- `census/round-31/records/c1-after-a4.txt:1`: "A2+A4 (current tools/souji-capability-cells.py): python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab" — the record IS the output of the cell's own argv; `:43`: "SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=24f343c8ffc820c0f89b4252cbdc94ab9a673aab" then `rc=1`. It is the ONLY line in the file containing any of the five unit words (grep -n over the whole file: line 43 only).
- `census/round-31/records/c1-before.txt:1`: "C1 do-nothing full output: python3 -B tools/souji-capability-cells.py --root <lane> --rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525"; `:43`: "SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525". Also its only unit-bearing line.
- `census/round-31/c1-cells.tsv`: no `items` word anywhere; its only digit-boundary `41` is the item id `L41` (line 48) — not a count of 41.

**4. Tool probes (base blob of `tools/souji-capability-cells.py`, unchanged base→landing).**
- Cell's own pinned argv re-run: prints the identical SUMMARY (`items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=24f343c8…`), rc=1 — the r31 cell still reproduces at its pinned rev.
- Same tool at the landing rev (`--rev 9e8982b…`): `SUMMARY items=41 bound_run=19 bound_record=20 unbound=1 mismatches=2 rev=9e8982b…`, rc=1 (captured directly, not through a pipe).
- False-green probe: `--only X01` → "SUMMARY items=1 bound_run=0 bound_record=0 unbound=0 mismatches=0 partial=1 rev=24f343c8…", tool rc=0.

**5. Landed rows match the wave-1 delivery verbatim** (`.ufo/waves/round-32/w1/deliver-c1-bind-N27-N34.md` §1): only N27 and N32, same literals, same record targets, same reasons. Nothing extra was landed for my range.

## Findings

1. **N27 — HONEST.** Row `| N27 | SCORECARD.md:422 | items=41 | record: census/round-31/records/c1-after-a4.txt:43 | … |`. The record's header logs the exact argv the cell quotes and its line 43 is that run's SUMMARY with `items=41`; same round (r31), same measurement (the post-state tool run at rev 24f343c8). Not coincidental: the cell names this file as its record and the integers match verbatim. Passes every v2 predicate: basename cited on base line 422 (A0a), blob unchanged base↔rev, round 31 ∈ item rounds, unit `items` adjacent to 41 (`items=41`), single occurrence (no other unit-bearing line in the file).

2. **N32 — HONEST.** Row `| N32 | SCORECARD.md:422 | unbound=22 | record: census/round-31/records/c1-before.txt:43 | … |`. The cell itself quotes "base `census/round-31/records/c1-before.txt` `unbound=22 mismatches=34`"; the record's header logs the do-nothing control argv (`--rev 1d45496a…`, the r31 prereg rev) and line 43 carries `unbound=22` with the unit adjacent. Same round, same measurement, the cell's own cited baseline record. Not coincidental.

3. **N28, N29, N30, N31, N33, N34 — no row landed; the absence is CORRECT (verdict: HONEST-as-absence).** Closure proven per binding kind, independently of the wave-1 delivery:
   - `run:` closed for ALL six (and all eight): the only script stem on base line 422 under `tools/`/`tests/fixtures/` is `souji-capability-cells`; the r31 tool's row regex (`tools/souji-capability-cells.py:71`) accepts only `L\d{2}` ids with run/record kinds, so L29's landed `field:` row is invisible to it → L29 unbound at every rev → `mismatches>=1` → the tool exits 1 at every rev (exit rule `tools/souji-capability-cells.py:318`), and the counter's run MATCH requires rc==0 (`c1-counter-v2.py:316`). Empirically: rc=1 at rev 24f343c8 AND at the landing rev. Additionally at the landing rev the SUMMARY itself drifts to `bound_run=19 … mismatches=2`, so even a rc=0 world would not print `bound_run=20`. `unbound=1`/`mismatches=1` (N30/N31) can never appear on an rc=0 SUMMARY by the tool's own arithmetic (unbound counts into mismatches).
   - `record:` closed for the six: each cited record file has exactly ONE unit-bearing line (line 43 in each), already taken by N27/N32 — a second row there is `BAD-ROW(shared-occurrence)` (`c1-counter-v2.py:50`); `c1-cells.tsv` contains none of the five unit words (its only boundary `41` is the id `L41`, line 48), so it fails the unit/adjacency rule for every one of the six; no other basename is cited on base line 422, so no other path passes A0a (`c1-counter-v2.py:325`).
   - `field:` closed for the six: field paths must end `.json` and be cited on the base line; line 422 cites no `.json` basename and no glob token.
   - `withdrawn:` unavailable for the six: the frozen definition is "withdrawn <reason of at least 8 words>: the cell's integer is withdrawn as evidence (no observable shows it);" (`c1-counter-v2.py:47`) — observables DO show each integer (`c1-after-a4.txt:43` shows bound_run=20/bound_record=20/unbound=1/mismatches=1; `c1-before.txt:43` shows unbound=22/mismatches=34), so a withdrawal reason would be false. The wave-1 delivery's refusal to withdraw (its §5) was the honest reading. Note the counter never verifies a withdrawal reason's truth (only ≥8 words) — see finding 6.

4. **ATTACK on the FROZEN counter — gameable `--only`, reproduced, NOT used by the landing.** `c1-counter-v2.py` computes `n = len(items) if not only else len(only)` and skips non-listed items; with `--only` naming non-item ids every real item is skipped, all counts are 0, `ok` holds, exit 0. Tool side reproduced: `--only X01` → "SUMMARY items=1 … partial=1", rc=0. Consequence (counter-side, derived from the run rule at `c1-counter-v2.py:316` + `at_bounds`): a `run:` row whose argv carries 41 non-existent ids would print `items=41 … partial=1` rc=0 and MATCH literal `items=41` (N27/N34) or any `=0` literal; `--only` with exactly the 20 currently-passing r31 ids would print `bound_run=20` and circularly bind N28. This is a hole in the frozen predicate, reported per the contract as an ATTACK with reproduced state — no predicate change proposed; the landed rows do not use it.

5. **Cross-claim drift discovered while auditing (for the L1): the r31 tool's re-run state degrades at the landing rev — one r31 run binding flips.** Re-running the r31 tool with `--rev 9e8982b…` gives `bound_run=19 … mismatches=2` (vs the r31 record's `bound_run=20 … mismatches=1`): L31's run binding `python3 tests/fixtures/r23-receipt-run.py` goes MATCH (`rc=0 observed=selftest=8/8` in `census/round-31/records/c1-after-a4.txt:32`) to "RUN-MISMATCH python3 tests/fixtures/r23-receipt-run.py rc=1 observed=selftest=1/8". Root cause, reproduced: the r31 tool executes the run script's r31-BASE blob (`tools/souji-capability-cells.py:209-213`) under its own fresh TMPDIR (`:215-216`); that frozen fixture blob hardcodes `SCRATCH_PARENT = "/var/tmp"`, while the C2 landing deliberately made `tools/souji-receipt-run.py` honour TMPDIR and refuse `--out` outside it (`OUT-OUTSIDE-SCRATCH`) — the old fixture's `/var/tmp` --out is then refused (reproduced: `selftest=1/8`, rc=1, `codes=['OUT-OUTSIDE-SCRATCH', 'REV-ABSENT']`). Classification: NOT a C2 regression — it is the intended C2 behaviour change interacting with the frozen r31 measurement blob; the landing-tree fixture itself passes 8/8 rc=0, and the r31 cell's own pinned argv still reproduces exactly. No r32 claim consumes the r31 tool's re-run at a later rev, and no landed C1 row is invalidated (both N27/N32 records are unchanged blobs measured at their own revs). Residual: the r31 binding rows' run bindings are not rev-stable; the L1's final-tip measurement should not expect the r31 tool's re-run SUMMARY to stay at the r31 values.

6. **Robustness of the C1 verdict (for the L1): the miss is overdetermined and interpretation-proof.** At the landing commit the full-counter state is `unbound=6 mismatches=6 withdrawn=17` (`census/round-32/records/amendments.txt:24`: "No amendment for C1 or C2 after data. C1 reads `unbound=6 mismatches=6 withdrawn=17` at the integration commit"). Even if my six items had been perfectly bound (impossible, finding 3), `withdrawn=17 > WITHDRAW_MAX=8` (`c1-counter-v2.py:73`) alone fails the target; and had the six been withdrawn under a looser reading of "no observable shows it", withdrawn would rise to 23 — still a fail. No reading of the withdrawal rule flips the outcome; the MISSED verdict is stable.

7. **No `withdrawn:` rows exist in my range** (N27–N34): the landed section holds only the N27/N32 record rows; the counter shows `binding=-` for the other six. Nothing to truth-check — vacuously satisfied.

## Attack log

- **A1 (run binding for N28/N34 via tool re-run): CLOSED.** Attempted the obvious binding — re-run the cell's own tool. rc=1 at rev 24f343c8 (mismatches=1) and at the landing rev (mismatches=2, `bound_run=19`); L29's landed `field:` row is invisible to the r31 tool's id/kind regex (`tools/souji-capability-cells.py:71`), so no rev lets the tool exit 0. Any run row for the six is RUN-MISMATCH.
- **A2 (record bindings for the six on the cited files): CLOSED.** `c1-after-a4.txt` and `c1-before.txt` each have exactly one unit-bearing line (43), both taken; `c1-cells.tsv` has no unit word (only boundary `41` is the id `L41`, line 48). Shared-occurrence + A0a block every alternative.
- **A3 (field bindings): CLOSED.** No `.json` basename or glob token on base line 422 → A0a refuses any field path.
- **A4 (withdrawn rows for the six): UNAVAILABLE and would not help.** Observables show the integers, so the frozen reason would be false; and withdrawn=17 already exceeds the cap, so the target fails regardless (finding 6).
- **A5 (frozen-counter `--only` gameability): REPRODUCED, unused** — see finding 4. Recorded as gameability, not evidence.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/SwarmReviewer05.md` — this report (the only file written; no tool installs; scratch `/fast/scratch/hyaku/souji-r32/AuditC1N27N34/` removed after writing).
