# SwarmCritic21 — C1 K23 falsification (SCORECARD.md:423, r31 landing-gate precision)

## Status
STATUS: PASS — K23 HOLDS: the frozen argv is deterministic, the frozen predicate is exactly the row's stated outcome and rejects 5/5 tested regressions of its covered behaviours; one prose clause of the same cell ("fenced headings are text") is not exercised by any G-case and a regressed tool still prints the frozen line (LAX residual, reported as an attack, not a mismatch).

## Evidence
Measured revision 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 for all runs; frozen items/list commit 2d9bca55a9f042a2c9ed60a797a8069e74c41f46; base 6017a482e7068d5afb7617640198fbb0fe743357. Scratch clone `/fast/scratch/hyaku/souji-r33/AuditK23/c` (`git clone -q --no-local`, origin removed, detached, `rev-parse --show-toplevel` = clone).

1. Determinism — argv `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` in the clone, cwd clone root:
   - run1 TMPDIR=`$D/fresh1` rc=0, run2 TMPDIR=`$D/fresh2` rc=0; `diff out1 out2` empty, both md5 `66f0ee36d30aa1134c00349135154f5b`; stderr 0 bytes.
   - last lines both: `CONTROL always-zero-emitter FALSE-GREEN-REJECTED failed=G1,G2,G9,G10` / `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; the predicate string occurs exactly once in the output.
   - run3 `env -u TMPDIR` rc=2: `PREREQ FAIL TMPDIR is unset (build synthetic repos under $TMPDIR)` + `cases=0 pass=0 control=FALSE-GREEN-ACCEPTED` — a stated prerequisite refusal, not nondeterminism; the counter always passes TMPDIR (counter docstring, "Run:").
2. Frozen counter — `python3 -B census/round-33/c1-counter.py --root <lane> --rev 2d9bca55… --list-rev 2d9bca55… --scratch /fast/scratch/hyaku/souji-r33/AuditK23/cnt --only K23` ->
   `ITEM	K23	AGREE	original	rc=0 expect_exit=0 predicate holds last=cases=10 pass=10 control=FALSE-GREEN-REJECTED`, `SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55…`, rc=0.
3. Base-tool clause re-derived — tool at 52ebd480461b481aeabadf143881223290c6fea2 (parent of the r31 C2 commit 8024b54; blob `51f98ed7…`, identical to the r31 counter's `--base` 9f17a1e tool): `cases=10 pass=3 control=FALSE-GREEN-REJECTED` rc=1, CASE FAIL exactly G1 G3 G4 G5 G6 G7 G8, PASS exactly G2 G9 G10 — byte-identical for the r31 fixture and the current (r32) fixture (the only r31→list-rev fixture diff is a docstring hunk, tool blob ids 943f42d3 vs 13b551d9).
4. Record quotes verified at 2d9bca55 (`census/round-31/records/c2-after-v1.txt`, blob `2cd9461c…`, same at base): line 23 `REDARM rc=1 base_cases=[('G1', 'FAIL'), ('G2', 'PASS'), ('G3', 'FAIL'), ('G4', 'FAIL'), ('G5', 'FAIL'), ('G6', 'FAIL'), ('G7', 'FAIL'), ('G8', 'FAIL'), ('G9', 'PASS'), ('G10', 'PASS')] ok`; line 28 contains `fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same` (row adds `rev=8024b54…`); `shift=ok` at c2-after-v2.txt:29 and c2-after-v3.txt:30,60.
5. Mutant probes (copies of the list-rev tool under `$D/mut/`, run through the same fixture, fresh TMPDIR each):
   - m1 `_report_paths` capture prefix dropped (no `.ufo/waves` ∪ `census/waves` union): `cases=10 pass=9`, G1 FAIL (`checked_reports=1 want 2`).
   - m2 carry scanner returns at the first section end (r31 base behaviour): `cases=10 pass=9`, G3 FAIL (`LG-SEAT-UNCARRIED count=1 want 0`).
   - m3 ellipsis skip removed in `_pointer_paths`: `cases=10 pass=9`, G4 FAIL (`dangling=1`).
   - m4 `:line`-spec trim removed in `_trim_pointer_token`: `cases=10 pass=9`, G5 FAIL (`dangling=2`, `tools/x.py:2-3`, `tools/x.py:274–277`).
   - m5 `_path_exists_in_tree` always True: `cases=10 pass=9`, G9 FAIL (`dangling=0 want 6`).
   - m6 fence-awareness removed in `failures_section_lines` (fenced heading becomes a section boundary): `cases=10 pass=10 control=FALSE-GREEN-REJECTED`, rc=0 — NOT caught; `tools/souji-landing-gate.py --selftest` on m6 also `SELFTEST pass=65 fail=0`.

## Findings
1. The frozen predicate is a faithful reading of the stated outcome and is not stricter. SCORECARD.md:423 span states `python3 -B tests/fixtures/r31-landing-gate-precision.py --tool tools/souji-landing-gate.py` -> `cases=10 pass=10 control=FALSE-GREEN-REJECTED`; the fixture prints that line only when `passed == len(CASES)` and the control is rejected and returns 0 on exactly the same condition (fixture `main`, lines 609-632). No additional requirement is placed on the tool.
2. It is not lax for the behaviours G1-G10 name: five targeted regressions (union, all carry sections, ellipsis, line ranges, real-missing detection — each a distinct clause of the cell) all drop `pass` to 9, and the pre-r31 tool drops it to 3. Locations: SCORECARD.md:423 prose; tool `_report_paths` 510-531, `failures_section_lines` 408-440, `_trim_pointer_token` 871-879, `_path_exists_in_tree` 971-972; fixture judges 414-482.
3. LAX residual (out-of-set, reproduced, not a claim mismatch): the cell also states the gate "reads every `## Seat-reported failures` section including append-only carries (fenced headings are text)" — SCORECARD.md:423. No G-case contains a fenced block (`grep -n '```' tests/fixtures/r31-landing-gate-precision.py` at 2d9bca55: no match), so a tool that treats a fenced heading as a section boundary still prints the frozen line (mutant m6, `cases=10 pass=10`, rc=0) and still passes the tool's own 65-case selftest. The clause is unguarded by K23's command and by the selftest; K23 cannot see a regression there.
4. Base-tool clause (same cell, outside the item rule) is base-ambiguous but current under its own anchor: "the same fixture against the base tool prints `cases=10 pass=3`" reproduces exactly with the r31 base tool (blob `51f98ed7…`, = the r31 counter's `--base` 9f17a1e), matching c2-after-v1.txt:23. A literal round-33-base reading (6017a48 tool blob `10069f5c…`, identical to the list-rev tool) prints `cases=10 pass=10`, so the clause is true only under the r31-base reading its citation implies. Not stale; ambiguity only.
5. All other outcome statements in the cell are committed-record quotes and reproduce verbatim at the measured revision (finding 4 evidence): `fp=0 … regress=same`, `shift=ok` x3, the REDARM base-case list. `r26=495` is the record's own `LANE round=26 reports=495` line; not re-executed (its producer is `census/round-31/c2-counter.py` at rev 8024b54, outside this item's measurement) — verified as record content only.
6. Environment dependency, not a defect: the frozen argv has no `{SCRATCH}` and is not self-contained — it refuses with rc=2 unless TMPDIR is set and outside the lane and fleet roots (fixture `prerequisites`, 529-553). The counter's harness always supplies `TMPDIR=<fresh dir under --scratch>`, so the item is measured under a stated environment.
7. Provenance is clean: the fixture touches no lane bytes (LANE_ROOT/FLEET_ROOT appear only in the TMPDIR containment guard, lines 77-78, 542); worlds are built under TMPDIR; the counter ran it from its own clone. No duplicated authority with C2 here.

## Attack log
- A1 (predicate laxness): six mutants of the list-rev tool; five are caught by `pass=9`, one (fence awareness) is not — ATTACK recorded with reproduced state at finding 3. The frozen predicate, item and counter are left unchanged; the correction belongs to a future stricter fixture case (a fenced `## Seat-reported failures` heading in a carry world), not to this round's frozen item.
- A2 (staleness of the non-item outcomes): base-tool run re-derived from the record's own base commit → reproduces (`cases=10 pass=3`, FAIL set G1 G3 G4 G5 G6 G7 G8); record lines verified byte-for-byte. No stale residual found.
- A3 (nondeterminism): two fresh-TMPDIR runs identical (md5 equal); TMPDIR-unset run is a declared refusal (rc=2), not variance. Counter AGREE matches.
- A4 (predicate gaming): the fixture's always-zero control is rejected at G1,G2,G9,G10; per-case expectations conflict across worlds (e.g. `dangling=0` in G4-G8 vs `dangling=6` in G9, `checked_reports=2` in G1 vs `1` in G2), so no constant-output stub can satisfy all ten cases; the frozen line cannot be produced without passing the cases.
- Verdict: **HOLDS** (frozen predicate), with the finding-3 LAX residual carried as an out-of-set attack, not as a K23 mismatch.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic21.md` (this report).
- No lane file edited, no commit, no tool installed; scratch `/fast/scratch/hyaku/souji-r33/AuditK23` removed after the receipts above were copied.
