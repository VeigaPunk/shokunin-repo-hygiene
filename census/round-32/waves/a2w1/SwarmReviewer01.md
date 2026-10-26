# SwarmReviewer01 — audit of landed C1 rows N01-N05 (souji r32, attempt 2, wave a2w1)

## Status
STATUS: PASS — all five landed rows are counter-legal under v1 AND v2 at the C1 landing commit 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 and at the current tip 4e56c48b8fc828f9aba2746e324dc46aa538bdbf (`bound_field=3 withdrawn=2 unbound=0 mismatches=0`, exit 0 in all three runs). Verdicts: N01 HONEST (own evidence, same round + same measurement); N02, N03 honest withdrawals (reasons TRUE — exhaustively no admissible observable exists); N04, N05 COINCIDENTAL (value-equal across different snapshots, disclosed in the rows' own reasons, admissible because the frozen field rule does not test snapshot identity). The round-level C1 miss (`unbound=6 mismatches=6 withdrawn=17` > cap 8, census/round-32/records/amendments.txt) involves none of these five items.

## Evidence

Scratch clone `/fast/scratch/hyaku/souji-r32/AuditC1N01N05/r.nSGlIO/c` (`git clone -q --no-local`, origin removed, `rev-parse --show-toplevel` = clone path, detached at 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93). TMPDIR `/fast/scratch/hyaku/souji-r32/AuditC1N01N05/tmp`. No lane write, no lane git mutation.

Counter runs (pasted verbatim):

```
$ python3 -B census/round-32/c1-counter-v2.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only N01,N02,N03,N04,N05 --scratch /fast/scratch/hyaku/souji-r32/AuditC1N01N05/cnt
ITEM	N01	SCORECARD.md:147	literal=246 rows	binding=field	MATCH	census/round-1/census-summary.json rows_total=246
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=withdrawn	WITHDRAWN	no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=withdrawn	WITHDRAWN	no cited record holds 16 mined since verification.json prints the ending census mined 20
ITEM	N04	SCORECARD.md:151	literal=15 queued	binding=field	MATCH	census/round-13/verification.json sources.statuses.queued=15
ITEM	N05	SCORECARD.md:151	literal=2 rejected	binding=field	MATCH	census/round-13/verification.json sources.statuses.rejected=2
SUMMARY items=5 bound_run=0 bound_record=0 bound_field=3 withdrawn=2 unbound=0 mismatches=0 partial=1 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93
v2exit=0
```

v1 (`c1-counter.py`, same args, `--scratch .../cnt1`): identical five ITEM lines and SUMMARY, `v1exit=0`. At the tip 4e56c48b8fc828f9aba2746e324dc46aa538bdbf: identical, `tipexit=0`.

Structural checks (all at 9e8982b7 unless noted):
- Landed rows == wave-1 delivery block byte-identical (`diff` of `grep -E '^\| N0[1-5] \|'` over `git show 9e8982b7:SCORECARD.md` vs `.ufo/waves/round-32/w1/deliver-c1-bind-N01-N05.md` → empty, `LANDED==DELIVERY`).
- Exactly one row per item (N01-N05 count 1 each); zero `| N0` rows at base; base SCORECARD.md = 428 lines, bindings section at line 430 → appended; counter append-only check passes at landing and tip.
- SCORECARD.md blob identical at base and prereg: `771250313133d5f38b7f51a0922212db50990520` (both `rev-parse`).
- Field JSON blobs unchanged base↔rev: `census/round-1/census-summary.json` = `956a5878ac0f1519150f546ce18848f6ce8b798a`, `census/round-13/verification.json` = `879d96b42867dff04e02c5f08636081d1a8ca00f` (both revs each).
- v1 counter has no A0 checks (`grep -c "A0a-not-cited"` = 0, `def adjacent` = 0; v2: 2 and 1) → the "under v1 AND v2" requirement is non-vacuous.
- 9e8982b7 is an ancestor of tip 4e56c48b (`merge-base --is-ancestor` rc=0); tip delta = the five after-record files only, 156 insertions, no SCORECARD change.

## Row verdicts

Base line 147 (N01): cell cites "`census/round-1/census-summary.json`, `census/round-1/census.tsv` (246 rows)". Base line 151 (N02-N05): "baseline 33 rows, mined=16 queued=15 rejected=2 at 31984f473ce4bdab61a99b16cca194b28108cb81".

**N01 — HONEST (own evidence).** `census/round-1/census-summary.json:6` `"rows_total": 246,` — a JSON integer (not bool), key carries the unit (`rows_total`), basename cited on line 147 (A0a). Same round and same measurement: the JSON self-describes `"round": 1`, `"date": "2026-10-18"`, `"mode": "dry-run"`, `"fragments": "64/64"`, and `census/round-1/census.tsv` at base has 247 lines = 1 header + 246 data rows (`wc -l` = 247), so `rows_total` is the row count the cell's `(246 rows)` states. Provenance: the JSON and census.tsv were added by 652b6f8f1a279d2d977f2db208384ca5179994b1 (r1, 2026-10-18 12:39:42, subject "round-1: dry-run census — 64 seats, 246 rows, ..."); the cell by ab7f2f706f35f466b515b474fc9c76e0ddd71ae2 (r1, 12:40:22) — same round, one minute apart.

**N02 — HONEST withdrawal (reason TRUE).** The base line 151's only census/round-K basename is `verification.json` (`corpus/SOURCES.md` is not under `census/round-<K>`; no `tools/`/`tests/` stem: grep count 0; no `*` glob token: count 0), so it is the only admissible record/field path under A0(a). Exhaustive sweep of that blob (273 lines): v2 adjacency (`unit[^A-Za-z0-9]{0,3}int` either order) for (33, "rows") → 0 lines; v1 co-occurrence (33 at digit boundaries AND "rows" anywhere, case-insensitive) → 0 lines; dotted key paths resolving to integer 33 → only `sources.tiers.A` (a tier count; key has no "rows", basename has none → field unit rule fails). The record that does hold it — `census/round-13/baseline-measures.md:13` ("33 / 0 / none / none") — is uncited, so A0(a) refuses it (v1 would MATCH it; v2 prints BAD-ROW(A0a-not-cited); the joint v1+v2 target leaves withdrawal as the only legal state). Reason's factual claims verified: `census/round-13/verification.json:250` `"rows": 37,`; SOURCES.md at 31984f47 counts 33 rows / mined=16 queued=15 rejected=2 (table-row count + status-column tally); r13 commit 6ed10a7c introduced the "baseline 33 rows" phrasing (`log -S'baseline 33 rows'`) and added baseline-measures.md.

**N03 — HONEST withdrawal (reason TRUE).** Same cited-blob sweep: (16, "mined") adjacency → 0 lines, co-occurrence → 0 lines; NO JSON integer 16 exists anywhere in verification.json (key-path sweep empty); the cited record's mined count is `census/round-13/verification.json:257` `"mined": 20,` for its 37-row ending census. The holding record `census/round-13/baseline-measures.md:15` ("mined=16 queued=15 rejected=2") is uncited → A0(a)-refused. Reason verified.

**N04 — COINCIDENTAL (disclosed; counter-legal).** The cell's integer is the baseline histogram at 31984f47; the cited `verification.json` is the ending census — its own header records `"baseline_commit": "31984f473ce4bdab61a99b16cca194b28108cb81",` (line 4) and `"measured_commit": "6f8ee0f38a14a3cb599ee606c486a55ec64e8ae6",` (line 3), and its `sources` object (rows=37, tiers A=33/B=3/C=1, statuses 20/15/2) matches SOURCES.md at 6f8ee0f3 exactly (37 rows, mined=20 queued=15 rejected=2, my tally). `sources.statuses.queued=15` (line 258) is therefore the ending census's queued count, not the baseline measurement the integer describes. The equality is a data coincidence: `git diff 31984f47 6f8ee0f3 -- corpus/SOURCES.md` adds exactly 4 rows (S034-S037, all status mined) and touches no queued/rejected row; baseline tally 16/15/2 vs ending 20/15/2. It is the unique unit-bearing key for 15 in the cited blob, so it is the strongest admissible binding; the row's reason discloses the gap ("the value the 31984f47 baseline shows"). Same round (r13), same quantity (sources status histogram), different snapshot.

**N05 — COINCIDENTAL (disclosed; counter-legal).** Same structure: `sources.statuses.rejected=2` (line 259) is the ending census's rejected count, coinciding with the baseline's rejected=2 because the 4 added rows are mined and no rejected row changed. Only other integer-2 paths in the blob are irrelevant `results.*.exit_code`/`expected_exit` entries. Reason discloses ("matching the 31984f47 baseline").

No `run:` binding exists among N01-N05, so no argv re-run beyond the counters themselves was required.

## Findings

1. **[medium] N04/N05 are coincidental value matches, not the cells' own measurement.** SCORECARD.md:438-439 at 9e8982b7 bind `census/round-13/verification.json sources.statuses.queued=15` / `sources.statuses.rejected=2` — the ending census (measured_commit 6f8ee0f3, rows=37) — while the cells' integers are pinned to the baseline snapshot 31984f47 (rows=33). Verified real coincidence (r13 curation added only mined rows), disclosed in both reasons; the frozen field rule (value + unit + citation, no snapshot identity test) admits them. No rule violated; classification only. Changing them could not rescue C1 (withdrawn or unbound would both worsen the already-missed round state).
2. **[minor] N01's reason attributes the JSON to the wrong r1 commit.** SCORECARD.md:435 reason says r1 commit ab7f2f70 "wrote the cell and its own census-summary.json records rows_total 246"; the JSON actually landed in 652b6f8 (12:39:42), the cell in ab7f2f70 (12:40:22). Same round, material claim (the cell's own cited JSON holds 246) true; the counter does not check reason prose.
3. **[minor] N02's reason compresses the record location.** SCORECARD.md:436 reason says the baseline counts came from "baseline-measures.md:15"; line 15 holds the status histogram (16/15/2), the rows integer 33 sits on line 13. Material claim (the record is uncited) true.
4. **[info] Round-level C1 state at the integration commit is a miss unrelated to these five rows.** census/round-32/records/amendments.txt: "C1 reads `unbound=6 mismatches=6 withdrawn=17` at the integration commit (missed ...)". The landed section indeed has no rows for N28, N29, N30, N31, N33, N34 (6 unbound) and 17 withdrawn rows; N01-N05 contribute 3 MATCH + 2 WITHDRAWN only.
5. **[info] Attempt-1 after-records not relied on.** This audit re-derived the C1 state for N01-N05 directly from SCORECARD.md and the cited blobs at 9e8982b7 and at tip 4e56c48b; the salvage-committed `c1-after-*.txt` files were not read as evidence.

## Attack log

1. Re-ran both frozen counters (v1, v2) at the landing commit and v2 at the tip with `--only N01,N02,N03,N04,N05` — all exit 0, no BAD-ROW / RUN-MISMATCH / FIELD-MISMATCH / shared-occurrence / duplicate.
2. Attacked N01: blob identity base↔rev; integer-not-bool check; semantic identity of `rows_total` vs the census.tsv data-row count (247 lines − 1 header = 246); provenance commits. Held.
3. Attacked the N02/N03 withdrawals ("could an admissible observable exist?"): enumerated the cited-evidence universe on base line 151 (basenames, glob tokens — none, tools/tests stems — none) → only `census/round-13/verification.json` eligible; swept all 273 lines for v2 adjacency and v1 co-occurrence of (33, rows) and (16, mined) → empty; swept every dotted key path for integers 33/16 → only `sources.tiers.A`=33 (unit rule fails), no 16 anywhere; confirmed the holding record `baseline-measures.md` is uncited (A0a) and that the reasons' numbers (rows 37, mined 20; SOURCES.md at 31984f47 = 33/16/15/2) are accurate. Withdrawals stand.
4. Attacked N04/N05 ("same measurement?"): read the JSON's own `baseline_commit`/`measured_commit` header; tallied SOURCES.md at 31984f47 (33 rows, 16/15/2) and at 6f8ee0f3 (37 rows, 20/15/2); diffed the two snapshots (+4 mined rows S034-S037, queued/rejected untouched) → the bindings evidence the ending snapshot, values coincide. Classified COINCIDENTAL, disclosed.
5. Structural integrity: landed rows == delivery, one row per item, append-only vs base bytes (428-line base, section at 430), no shared (path,key) occurrences, JSON blobs unchanged base↔rev.

## Deliveries
- `.ufo/waves/round-32/a2w1/SwarmReviewer01.md` — this report (the only file written; scratch `/fast/scratch/hyaku/souji-r32/AuditC1N01N05/` removed after writing).
