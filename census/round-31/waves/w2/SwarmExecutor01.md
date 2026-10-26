# SwarmExecutor01 — C1 re-run, souji round 31 wave 2 (attempt 1)

## Status

STATUS: PASS — C1's landed reading is reproduced exactly and deterministically (5 serial runs, 2 counters, 2 revisions: `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`, only L29 UNBOUND), the frozen kill rule reads MISSED at the landing commit and at the tip, and one attack is filed: the landed reason sentence asserts a frozen restriction the frozen bytes do not contain, and the target is mechanically reachable (executed 41/41 under both counters).

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin` read-only at tip `2c16d018e40db7c23420a2c3bb546b52957bcc25` (worktree clean); base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; list-rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`. python3 3.14.8, git 2.56.0. Scratch `/fast/scratch/hyaku/souji-r31/w2-ReRunC1` (TMPDIR exported per run, removed at the end).

Counter bytes: v1 `git show 1d45496:tools/souji-capability-cells.py` sha256 `eced32ea9f36b529e5442709570d28841b9b4bd032f1fd10961a624ce2d9b520`; current `tools/souji-capability-cells.py` sha256 `edf0933d02b8da7c3f04afbef19c32e921e46e89df2b3ff5d29dc25e1d607da3` (= the A4 digest).

Five serial runs (never two counters at once), common args `--root <lane> --rev <rev> --base 9f17a1e… --list-rev 1d45496… --scratch <D>/cnt*`:

| run | counter | rev | SUMMARY | non-MATCH | rc |
|---|---|---|---|---|---|
| R1 | v1 | 24f343c8 | `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1` | `ITEM L29 … base-cell binding=- UNBOUND` | 1 |
| R2 | v1 | 2c16d018 | same | L29 UNBOUND | 1 |
| R3 | current A2+A4 | 24f343c8 | same | L29 UNBOUND | 1 |
| R4 | current A2+A4 | 2c16d018 | same | L29 UNBOUND | 1 |
| R5 | current A2+A4 | 24f343c8 (2nd) | same | L29 UNBOUND | 1 |

The only non-MATCH line, identical in all five runs:

```
ITEM	L29	SCORECARD.md:170	literal=18/18	base-cell	binding=-	UNBOUND
```

Determinism: the full 41-line ITEM blocks (all nine tab fields) are byte-identical for R1 vs R3, R3 vs R5, and R2 vs R4; SUMMARYs differ only in `rev=`. No item flipped. Parallel execution was not attempted — the seat contract forbids two lane counters at once — so the r30 parallel-flip symptom is untested here, not cleared.

Base red control (R8, current counter at `--rev 9f17a1e`): `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34` (rc 1); tally 7 MATCH, 12 RUN-MISMATCH, 22 UNBOUND. This matches the prereg base reading and confirms the A4 correction that the prereg prose "23 literals" is 22 (`unbound=22`).

Row-set / append-only: `git show 1d45496:census/round-31/c1-cells.tsv` → 41 items; SCORECARD supersession table (`sed -n '366,406p'`) → 40 row ids; id-set diff = `29d28 < L29`; `git diff --shortstat 9f17a1ef 2c16d018 -- SCORECARD.md` = `1 file changed, 47 insertions(+)`, zero deletions. `L29` appears in no row (`grep -n '^| L29 ' SCORECARD.md` → none).

Frozen kill rule (prereg line 5 tail, read as bytes): "mismatches>0 at the C1 landing commit or at the tip -> missed." With `mismatches=1` at both revisions under both counters, C1 is MISSED.

Reachability reproduction (R6/R7): in a `--no-local` clone (origin removed, toplevel verified) one row appended after L41 and committed as `bafd068c784ec7674192c25d6f138bad898da69f`:

```
| L29 | SCORECARD.md:170 | 18/18 | record: census/round-21/replay-final.txt | The r21 matrix replay receipt records exit=0 matched=18/18 for each of the three source shapes, the same 18 frozen r20 predicates the cell's remote-source replay restates as 18/18. |
```

Current counter: `SUMMARY items=41 bound_run=20 bound_record=21 unbound=0 mismatches=0 rev=bafd068…` rc=0. v1: identical SUMMARY rc=0. `census/round-21/replay-final.txt` blob `4a679682287aead5f0ae5ce9634bcc10d69c2f54` is unchanged base→tip, lines 2-4 read `SCENARIO S1|S2|S3 exit=0 matched=18/18 src_unchanged=yes`; round 21 is in L29's round set `{20,21}`; A4(d) is not triggered (L28 binds the different literal `matched=18/18` to `final-code-verification.json`).

Enumeration shape audit (`python3 -B` on base blobs, digit-boundary `N/M` plus the counter's own `word=N word=N` shape): every capability-table row inside the frozen ranges is accounted for; no capability row outside `147-175, 313-314, 354-355` carries a count literal (rows at 13-15, 42, 69, 303 are axis/measurement tables, third cell = "before", not an evidence cell). Inside the ranges two spans in capability evidence cells have the counter's count shape but no item: base 151 `mined=16 queued=15 rejected=2` and base 314 `records=1381 failed=0 uncovered=0`.

## Findings

1. **C1 lands MISSED, not PARTIAL — confirmed.** Location: `SCORECARD.md:170` (cell), `SCORECARD.md:361-407` (40 supersession rows), `census/round-31/c1-cells.tsv` (41 items), `tools/souji-capability-cells.py`. All five runs put the single failure on L29 (`18/18`, `remote-source-after.json18/18`); `mismatches=1` at `24f343c8` and at `2c16d018`, under v1 and A2+A4. Axis: calibration (the claim's own target `unbound=0 mismatches=0` is not met).

2. **The landed reason states a frozen rule that the frozen bytes do not contain.** Location: `SCORECARD.md:363` ("its record states the count only as separate scalar fields … so no honest binding exists under the frozen rule and the item stays UNBOUND"). The frozen counter docstring and prereg line 5 require only "a record binding to an unchanged pre-round record of the row's own round that contains it"; A4 itself discloses the record rule as file-granular. `grep -i 'grep\|merely\|honest'` over preregistration.txt and amendments.txt finds no anti-grep/honesty clause (amendments only at line 41, the L1's own pre-landing note, and line 14). Reproduced: one appended row reaches `unbound=0 mismatches=0` under both counters (R6/R7), at rc 0. Axis: calibration — the self-assessment record asserts necessity where the contract expresses none; the honest-count argument (remote stdout prints `matched=18`, one integer, refused by A2 shape) is a reviewer judgment, not a frozen rule. Same mechanical result, independently, in `deliver-c1-audit-L21-L29.md` (SwarmCritic04): "The target was nevertheless reachable at 41/41 by misattribution, which the counter cannot detect."

3. **Enumeration denominator is reading-dependent.** Location: base `SCORECARD.md:151` (`mined=16 queued=15 rejected=2`) and `:314` (`records=1381 failed=0 uncovered=0`), rule in `census/round-31/c1-cells.tsv:1-3`. Under a literal `cases=`/`pass=` reading both are out of scope (41 items is exact); under the counter's own COUNT_FORM (two `word=N` fields) both are in scope and unenumerated, so the prereg sentence "the SCORECARD capability cells state 41 count literals" cannot be re-derived without choosing a reading. Axis: calibration (denominator of the metric). Corroborates, and does not add to, `deliver-c1-enumeration-gap.md` (SwarmScout08 IDs G12/G23).

4. **No counter defect found in the measured readings.** Location: all five runs plus the base control. Values are reproducible and consistent with the frozen docstring (bound=40 at both revisions, unbound=1, base 34 = 12 RUN-MISMATCH + 22 UNBOUND). Axis: operability — no harm demonstrated; the residual risk is untested parallel concurrency (contract-forbidden here), which stays a caveat rather than a finding.

5. **The honest-binding case for L29 is genuine on notation, not on existence.** Location: `census/round-21/remote-source-after.json` (blob `f4123cf1…`, unchanged base→tip; no `18/18` byte), `census/round-21/final-code-verification.json:111` vs `:129` (`remote.stdout` prints `matched=18`). So the remote replay's own count never appears as `18/18`, but the same 18-predicate replay's `18/18` does (matrix receipts). Axis: calibration — the row that would close the item is a misattribution by measurement, not a byte absence; the landed preamble should say that, not that the frozen rule forbids it.

## Attack log

- **Determinism, serial (assignment-mandated).** 5 runs, 2 counters × 2 revisions + repeat; full ITEM blocks byte-identical, no flip. r30's parallel-flip symptom: not tested (contract forbids parallel counters in one seat).
- **v1 vs A2+A4 differential.** Identical item blocks at both revisions; A2/A4 add strictness only where a row would cheat, and no landed row trips them.
- **Base red control.** `mismatches=34 unbound=22` reproduced from base bytes; run-bound cells re-executed from the `--base` blobs (A4(c)), so base-script output, not tip-script output.
- **Row-set and append-only.** 40 row ids = 41 items − L29; SCORECARD diff base→tip = 47 insertions, 0 deletions; no cell edited in place; every `SCORECARD.md:<line>` in the rows equals the item's TSV base line (any drift would be `BAD-ROW(line-or-literal)`, none occurred).
- **Enumeration completeness (two independent scans).** Full-file scan for `N/M` in third cells: no capability row outside the frozen ranges; count-shape scan (`word=N word=N`) inside the ranges: 2 unenumerated spans (finding 3). No target relaxation proposed.
- **Target reachability (main attack).** Appended one record row in a scratch clone and committed (`bafd068`); both frozen counters print `unbound=0 mismatches=0` rc=0. The lane itself was never written; the scratch clone is deleted.
- **Frozen-text check on the landed reason.** Searched preregistration and amendments for the "merely because grep found the digits" prohibition SwarmExecutor04 cites; it exists only in that seat's report, not in the frozen contract. A4's own disclosure (file-granular record rule) is consistent with finding 2.
- **Not attempted:** any lane `git add/commit/stash`, any `jj` mutation, any deletion/classification outside the lane, any parallel counter, any live `/proc` or fleet census, any parent agent dispatch. Scratch removed after copy.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-c1-rerun.txt` — all five SUMMARYs and every non-MATCH ITEM line, the base red control (12 RUN-MISMATCH + 22 UNBOUND), the determinism statement, the enumeration shape result and the two reachability runs with their full evidence.
- `.ufo/waves/round-31/w2/SwarmExecutor01.md` — this report.

No lane files were modified; no tool was installed or upgraded (uv/pacman not used).
