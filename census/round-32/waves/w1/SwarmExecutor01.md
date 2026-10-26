# SwarmExecutor01 — round 32 w1, C1 bindings N01–N05

## Status

STATUS: PASS — five binding rows written; `unbound=0 mismatches=0 withdrawn=2` under **both** v1 and v2 (rc=0 each) at
scratch rev `97a9edbec07ca48309648bfa5898f9092d79aefe`; the two withdrawals are A0(a)-forced and disclosed below.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `85b61a151923986e7e6b48f7084b9122561b5f3d`,
list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`. SCORECARD.md is the same blob at both
(`771250313133d5f38b7f51a0922212db50990520`, `git rev-parse <rev>:SCORECARD.md`). Scratch clone
`/fast/scratch/hyaku/souji-r32/C1BindA/r.8QIZQW/c`, `origin` removed, toplevel verified by the counter.

Writing commits (from `git -C LANE log -S'<token>' --format='%H %ad %s' -- SCORECARD.md`):

```
ab7f2f706f35f466b515b474fc9c76e0ddd71ae2 2026-10-18 round-1: SCORECARD — coverage 7, calibration 5 with counting commands vs 652b6f8
6ed10a7cd6c7b26f8068dd6e02497e860f9c4317 2026-10-20 round-13: bounded quarantine, declared-evidence gate and F2 census
5ff5041b64964d4e6e8374b0eefb8b12010b9997 2026-10-25 round-22: seat-driven corrections (locators, slice verdicts, stale digest, lesson M17-M21)
```

Rows appended (exact, also in the delivery): N01 `field: census/round-1/census-summary.json rows_total=246`;
N02 `withdrawn`; N03 `withdrawn`; N04 `field: census/round-13/verification.json sources.statuses.queued=15`;
N05 `field: … sources.statuses.rejected=2`.

Acceptance (v2 then v1, same rev, real exit codes):

```
== c1-counter-v2.py rc=0
ITEM	N01	SCORECARD.md:147	literal=246 rows	binding=field	MATCH	census/round-1/census-summary.json rows_total=246
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=withdrawn	WITHDRAWN	no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=withdrawn	WITHDRAWN	no cited record holds 16 mined since verification.json prints the ending census mined 20
ITEM	N04	SCORECARD.md:151	literal=15 queued	binding=field	MATCH	census/round-13/verification.json sources.statuses.queued=15
ITEM	N05	SCORECARD.md:151	literal=2 rejected	binding=field	MATCH	census/round-13/verification.json sources.statuses.rejected=2
SUMMARY items=5 bound_run=0 bound_record=0 bound_field=3 withdrawn=2 unbound=0 mismatches=0 partial=1 rev=97a9edbec07ca48309648bfa5898f9092d79aefe
== c1-counter.py rc=0
(same five ITEM lines, MATCH MATCH WITHDRAWN WITHDRAWN MATCH, same SUMMARY)
```

Baseline re-derivation at the commit the cell names
(`git show 31984f473ce4bdab61a99b16cca194b28108cb81:corpus/SOURCES.md`, status column counted):

```
rows=33
  status[mined]=16
  status[queued]=15
  status[rejected]=2
```

## Findings

1. **SCORECARD.md:151's evidence pointer omits the record that holds its baseline counts.** The cell reads
   "baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f473ce4bdab61a99b16cca194b28108cb81"; the integers are
   correct (finding 2) but its census pointer `census/round-13/verification.json:250,257` is the *ending* census
   (`sources.rows` 37, `sources.statuses.mined` 20, measured_commit `6f8ee0f3…`). The baseline histogram is in
   `census/round-13/baseline-measures.md:13` and `:15`, added by the same r13 commit, and the cell does not name it.
2. **All four r13 integers are right for the named baseline commit** (33 / 16 / 15 / 2 at `31984f47`), so this is a
   pointer defect, not a wrong count. N04 and N05 still bind because the cited ending histogram carries the same
   `queued=15`, `rejected=2`; 33 and 16 do not survive that substitution.
3. **Withdrawals N02/N03 are forced, not lazy.** Sweep over the 34 eligible census/round-12..13 blobs with the
   counter's own `record_path_ok`/`cited`: only `census/round-13/verification.json` is cited by line 151; it has zero
   lines where 33 stands within three non-alphanumeric bytes of `rows`, zero for 16 with `mined`; no tools/ or
   tests/fixtures/ basename stem occurs on line 151, so no `run:` is legal. Cost: 2 of the round's 8 withdrawals.
4. **The counter's A0 blocks both plausible wrong bindings** (reproduced, not inferred): `sources.tiers.A=33` — a value
   coincidence with "33 rows" — and `sources.statuses.mined=20` both score `BAD-ROW(field-shape)` at rev
   `10fc77bc367ac08e5fd15ea60236a55a522daaca`. The uncited but genuine record `baseline-measures.md:13/:15` scores
   `MATCH` under v1 and `BAD-ROW(A0a-not-cited)` under v2 at rev `3c51e7d18064c22336e9c083a55c9233e78067b2`, i.e. A0
   does exactly the citing work the cell's pointer list should have done.
5. **N01 is clean**: r1 commit `ab7f2f70` wrote the `(246 rows)` cell and its own record,
   `census/round-1/census-summary.json:6` `"rows_total": 246` (blob unchanged at base and REV), unit word inside the key.

## Attack log

None filed by this seat. The two reproduced falsifier states (finding 4) are self-checks of my own bindings, both
rejected as intended; no counter, predicate, target or item set is proposed for change.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-c1-bind-N01-N05.md` — verbatim rows, per-item provenance, both acceptance outputs,
  both falsifier states.
- `.ufo/waves/round-32/w1/SwarmExecutor01.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r32/C1BindA` removed after delivery; no lane file other than these two was written.
No tool installed or upgraded (`python3 -B` only, no `__pycache__`).
