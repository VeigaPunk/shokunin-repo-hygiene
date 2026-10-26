# SwarmCritic04 — C1 row audit L21-L29 (falsification wave 2, fleet hygiene lane)

## Status

STATUS: PASS — all eight landed rows L21-L28 re-derive as the measurements their cells state at the
C1 landing commit 24f343c8 and at lane tip 2c16d018 (four `run:` rows re-executed, four `record:`
occurrences located and corroborated); the L29 "no honest binding" declaration is confirmed against
all of census/round-20 and census/round-21, so C1's frozen target is genuinely missed by one item
(`unbound=1 mismatches=1`) as declared. Two non-blocking defects are recorded: one imprecise reason
clause (L26) and a reproducible wrong-occurrence acceptance for L29's exact slot.

## Evidence

Revisions: base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc; enumeration 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525;
C1 landing 24f343c8ffc820c0f89b4252cbdc94ab9a673aab; tip 2c16d018e40db7c23420a2c3bb546b52957bcc25.
Scratch clone `/fast/scratch/hyaku/souji-r31/w2-SwarmCritic04/c` (`--no-local`, origin removed,
`rev-parse --show-toplevel` verified before any scratch commit).

Cell lines at base (unchanged at tip; base SCORECARD.md is a byte prefix, 61956 → 73035 bytes):
166 paragraph-aware carry gate, 167 durable revision stamps, 168 seat-audit delivery and signal
classes, 170 clone-isolated acceptance replay. Rows occupy SCORECARD.md:387-394; 40 rows total;
`grep -n '^| L29 '` → NONE.

Run rows, re-executed at 24f343c8 and at 2c16d018, rc=0 each, last digit-bearing line:

```
r19-carry-wrap.py            SUMMARY total=4 failed=0 base_discriminating=2
souji-rev-pin.py --selftest  SUMMARY total=11 failed=0
r19-rev-pin.py               SUMMARY total=13 failed=0 base_discriminating=6
r19-seat-audit-shapes.py     SUMMARY total=17 failed=0 base_discriminating=12
```

Those four lines are byte-verbatim (the r19 fixtures separate fields with spaces). All four scripts
are byte-identical base→tip (blobs 308d8d92, ee952a2c, 07a85ff0, f681a40e), so A4(c)'s base-blob
substitution has nothing to diverge from and the rows' "at this revision" clause is measured, not
inherited. The auditor and the r20 oracle emit real tab separators (checked with `cat -A`): quoted
below as `\t`.

Records (blobs unchanged base→landing→tip): census/round-21/r20-closure-excerpt.json
5cd2243dd0f30854752f2a4608ca146866ccfb95; census/round-21/final-code-verification.json
6483d98f7ea9bd7ddd1997648f64a143c1c56901. Literal occurrences: excerpt:40
"auditor selftest 118/0; r19-seat-audit-shapes 17/0 (12 base-disc); carry-wrap 4/0"; excerpt:31
"r20 oracle 78/0, 11 base-discriminating; baseline 12516f7 auditor 40/38 on the same oracle";
final-code-verification.json:111 `MATRIX\tscenarios=3\treplayed=3\tsummaries_equal=True` with three
preceding `SCENARIO ... matched=18/18` lines.

Independent re-derivations: `python3 tools/souji-seat-audit.py --selftest` → `SELFTEST\tpass=118\tfail=0`
at 6ff3413b, 19571543, 24f343c8, 2c16d018; census/round-21/step-inventory.json:8-11 names
`auditor-selftest` with `"pass_count": 118` and :34-37 names `r20-audit-contract` with
`"expected_summary": "SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11"`;
`tests/fixtures/r20-audit-contract.py` alone → `SUMMARY\ttotal=66\tpass=66\tfail=0\tbase_discriminating=0`,
with `--base-tool` set to `git show 12516f7:tools/souji-seat-audit.py`
(sha256 62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6) →
`SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11`. census/round-21/accepted-matrix.json has
`"scenarios": 3`, `"replayed": 3`, `"summaries_equal": true` and three records (clone s1, bare
s2.git, lane root) each `"matched_command_count": 18` — the same run whose stdout L27/L28 bind.

Frozen counter (A2+A4), `--only L21..L29`: `SUMMARY items=9 bound_run=4 bound_record=4 unbound=1
mismatches=1` at 24f343c8 and the same at 2c16d018.

Frozen counter, all 41 items, on a scratch commit that keeps the 40 landed rows and adds one
dishonest L29 row (`record: census/round-21/replay-final.txt`):
`SUMMARY items=41 bound_run=20 bound_record=21 unbound=0 mismatches=0 rev=1edd6476bd83aba17347686f16c9c8a93a835aa3`.

L29 search: `git grep -l -F '18/18' <rev> -- census/round-20 census/round-21` → six files, all
acceptance-matrix occurrences or quotations of it (replay-final.txt:2-4, replay-integrated.txt:2-4,
final-verification.json:113, final-code-verification.json:111, r20-closure-excerpt.json's 78/78/0
sentence, recovery-status-catalog.json:226). The remote replay's record
census/round-21/remote-source-after.json carries only scalars — :3 `"all_matched": true`,
:4566 `"expected_command_count": 18`, :4724 `"matched_command_count": 18`,
:4726 `"observed_command_count": 18` — and `grep -F '18/18'` over it returns NONE.

## Findings

1. **Frozen counter accepts a wrong-occurrence binding for L29's exact slot (calibration, operability).**
   Location: tools/souji-capability-cells.py record rule (integer multiset + path shape only) against
   census/round-21/replay-final.txt:2-4. Reproduced: a scratch row
   `| L29 | SCORECARD.md:170 | 18/18 | record: census/round-21/replay-final.txt |` yields
   `ITEM L29 ... binding=record MATCH` and `unbound=0 mismatches=0`. Three further records pass the
   same way (final-code-verification.json, final-verification.json, recovery-status-catalog.json),
   although every one of those bytes is the acceptance matrix's matched=18/18, not the remote-source
   replay. Full-run reproduction: the 40 landed rows plus this one wrong-occurrence row give
   `SUMMARY items=41 bound_run=20 bound_record=21 unbound=0 mismatches=0` — C1's frozen target met.
   Consequence: the landed miss is a voluntary honesty choice, not a forced outcome, and a future
   seat cannot be stopped by the counter. This is A4's disclosed file-granularity residual, now with
   a reproduced state. No landed row uses it.
2. **L26 reason clause is imprecise (calibration).** SCORECARD.md:392 claims the 12 extra records
   "need an uncommitted baseline auditor copy". The bytes are committed: 12516f7:tools/souji-seat-audit.py
   is a blob with sha256 62522acc…, the closure's own receipt, and I extracted it with `git show`
   this run. What is missing at the revision is a working-tree copy, not a committed one. Secondary
   nit: `BASE_BROAD_CASE_IDS` holds 11 ids; the twelfth record is the base-broad-authorization-inventory
   line, so 66+12=78 is right but "12 baseline cases" is 11 cases + 1 inventory record. Count and
   binding are unaffected.
3. **Bound record's provenance is an out-of-lane excerpt (calibration, informational).**
   census/round-21/r20-closure-excerpt.json:2 records `"source": "...MANIFEST.json rounds[402] (read-only excerpt copied by L1 SoujiR21 ...)"`.
   The fleet MANIFEST is outside this seat's write/read bound, so the copy's fidelity cannot be
   checked in-lane; both counts are nevertheless corroborated in-lane by step-inventory.json and by
   live re-runs, so no axis is harmed. [INFERENCE] a tampered excerpt would have to be caught by a
   fleet-root reader.
4. **C1 lands one item short of its frozen target (calibration), as declared.** L29 is UNBOUND at
   the landing commit and at the tip; the section preamble's account (`"matched_command_count": 18`
   only) is accurate. Not a new defect — recorded so the wave's ledger is unambiguous.

## Attack log

- A1 base-line ↔ row-pointer cross-check: all eight rows point at their item's line (166/167/168/170);
  counter re-checks and MATCHes; no duplicate ids; 40 rows; no L29 row.
- A2 re-execute every `run:` argv in a fresh clone at the landing commit, then at the tip; compared
  exit code and last digit-bearing line with the row literal. All rc=0, all literals present at digit
  bounds (8/8). No NOT-REPRODUCED.
- A3 A4(c) substitution divergence check: the four scripts are byte-identical base→tip, so the
  counter's base-blob replacement is a byte-level no-op here; a passing literal cannot be manufactured
  that the as-committed run would not print.
- A4 record occurrences by hand: excerpt:40 and :31 and final-code-verification.json:111 located,
  context read, same capability and same run confirmed (auditor selftest; r20 audit-contract oracle;
  replay-matrix.sh at 19571543). No contradicting statement elsewhere in either record (a single
  `matrix` key; the 78/0 and 78/78/0 statements agree; one auditor-selftest statement).
- A5 L24's "no run row is possible" clause: base line 168 yields zero `.py` paths, so the auditor's
  stem cannot appear; true. The same count is live at four revisions.
- A6 L26 arithmetic attacked end to end: fixture without `--base-tool` = 66, with it = 78/78/0,
  base_discriminating=11; equals the record and the r21 step inventory. The "uncommitted" adjective
  fails (finding 2); the numbers do not.
- A7 L29 premise attacked from both sides. Honest-shaped rows are refused by the frozen counter:
  `18/18` → `RECORD-MISMATCH`, `matched=18` → `BAD-ROW(line-or-literal)`. Dishonest-shaped rows are
  accepted: `MATCH` for replay-final.txt (rev 1edd6476), final-code-verification.json (5d9a24f7),
  recovery-status-catalog.json (1da4b91d) and final-verification.json (80ffa958), each with
  `unbound=0 mismatches=0`. Premise confirmed, instrument gap demonstrated.
- A8 tip-stability: bound records unchanged base→tip; all six re-runs at the tip print the same
  counts; counter at the tip reproduces the landing SUMMARY. No tip regression in this slice.
- A9 append-only: base SCORECARD.md is a prefix at both the landing commit and the tip; the cells the
  rows supersede are byte-unchanged, so no row silently edits its own cell.
- A10 exact-vs-environment: run commands in the clone with `TMPDIR` under my scratch; no lane writes,
  no git mutation in the lane, no signals. Tooling: nothing installed or upgraded this seat.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-c1-audit-L21-L29.md` — per-row verdicts, occurrence quotes, rule
  checks, counter re-derivation, L29 search and the four-cheat reproduction.
- `.ufo/waves/round-31/w2/SwarmCritic04.md` — this report.
