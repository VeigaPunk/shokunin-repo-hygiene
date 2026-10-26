# C1 audit — supersession rows L21-L29 (r19 run rows, r20 closure excerpt, r21 matrix record, the L29 hole)

Seat SwarmCritic04, Souji r31 wave 2. Read-only audit at the C1 landing commit
24f343c8ffc820c0f89b4252cbdc94ab9a673aab, re-checked at the lane tip
2c16d018e40db7c23420a2c3bb546b52957bcc25. Base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc;
enumeration census/round-31/c1-cells.tsv at 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525.
Every command below ran from a `--no-local` clone with `origin` removed, at the named revision.

## Verdicts

| Row | Cell (base line) | Item literal | Row literal | Occurrence at 24f343c8 | Verdict |
|---|---|---|---|---|---|
| L21 (SCORECARD.md:387) | :166 paragraph-aware carry gate (r19) | `4/0` | `total=4 failed=0` | run: tests/fixtures/r19-carry-wrap.py | HONEST |
| L22 (:388) | :167 durable revision stamps (r19) | `11/0` | `total=11 failed=0` | run: tools/souji-rev-pin.py --selftest | HONEST |
| L23 (:389) | :167 | `13/0` | `total=13 failed=0` | run: tests/fixtures/r19-rev-pin.py | HONEST |
| L24 (:390) | :168 seat-audit delivery and signal classes | `118/0` | `118/0` | census/round-21/r20-closure-excerpt.json:40 | HONEST |
| L25 (:391) | :168 | `17/0` | `total=17 failed=0` | run: tests/fixtures/r19-seat-audit-shapes.py | HONEST |
| L26 (:392) | :168 | `78/0` | `78/0` | census/round-21/r20-closure-excerpt.json:31 (also :40) | HONEST (one reason clause imprecise) |
| L27 (:393) | :170 clone-isolated acceptance replay | `3/3` | `scenarios=3\treplayed=3` | census/round-21/final-code-verification.json:111 | HONEST |
| L28 (:394) | :170 | `18/18` | `matched=18/18` | same record:111 (three SCENARIO lines) | HONEST |
| L29 | :170 `remote-source-after.json18/18` | `18/18` | **no row** | none honest; four same-digits records pass | premise CONFIRMED |

`grep -c '^| L[0-9]' SCORECARD.md` = 40; `grep -n '^| L29 ' SCORECARD.md` = NONE. Base
SCORECARD.md is a byte prefix of the landing and tip files (61956 → 73035 bytes), so every
row points at an unedited cell.

## Per-row evidence

- **L21** — base line 166 carries `` `tests/fixtures/r19-carry-wrap.py` 4/0 base-discriminating ``.
  Run at 24f343c8 and again at 2c16d018: rc=0, last digit-bearing stdout line
  `SUMMARY total=4 failed=0 base_discriminating=2`. Script blob 308d8d925ee66d4b6524a29ba34425a5c3dc4b8f
  is identical at base, landing and tip, so A4(c)'s base-blob substitution cannot diverge.
  Reason sentence (4 cases, 0 failures, 2 base-discriminating) is exactly the output.
- **L22** — `python3 tools/souji-rev-pin.py --selftest`: rc=0, `SUMMARY total=11 failed=0`,
  blob ee952a2ca9927e8b07df9d5ddaa1871832febcec identical base→tip. Reason true.
- **L23** — `python3 tests/fixtures/r19-rev-pin.py`: rc=0,
  `SUMMARY total=13 failed=0 base_discriminating=6`, blob 07a85ff0017c0a9a1d159aa5dce9c59d15f81876
  identical base→tip. Reason true, including "6 base-discriminating".
- **L24** — item L24 literal `118/0` sits on the auditor-selftest clause of base line 168. Record
  `census/round-21/r20-closure-excerpt.json` (blob 5cd2243dd0f30854752f2a4608ca146866ccfb95,
  unchanged base→landing→tip) states, line 40: "auditor selftest 118/0; r19-seat-audit-shapes 17/0 (12 base-disc); carry-wrap 4/0".
  Same capability, same count. Independently: census/round-21/step-inventory.json:8-11 names the
  step `auditor-selftest` with `"pass_count": 118`, and `python3 tools/souji-seat-audit.py --selftest`
  prints `SELFTEST\tpass=118\tfail=0` (tab separators, `cat -A` checked) at 6ff3413b (the closure commit), 19571543 (the r21 measured
  commit), 24f343c8 and 2c16d018. Reason clause two is true: base line 168 contains no script path
  at all (`grep -o '[A-Za-z0-9._/-]*\.py'` over that line returns nothing), so no run row exists.
  Nuance: the bound record is the round-20 closure recheck retained under census/round-21, not the
  r21 "18-step receipts" the cell names; the row's reason says so, and the r21 receipt states the
  same 118 in `pass=118` notation, which the counter's shape rule could not bind.
- **L25** — `python3 tests/fixtures/r19-seat-audit-shapes.py`: rc=0,
  `SUMMARY total=17 failed=0 base_discriminating=12`, blob f681a40e2ab6109b6419f81b7e7abc88b5b069ab
  identical base→tip. Reason true (17/0, base12).
- **L26** — item literal `78/0`. Record excerpt line 31: "r20 oracle 78/0, 11 base-discriminating; baseline 12516f7 auditor 40/38 on the same oracle";
  line 40 states the run form "r20-audit-contract 78/78/0 base_discriminating=11". Re-derived end to
  end at 24f343c8: `python3 tests/fixtures/r20-audit-contract.py` prints
  `SUMMARY\ttotal=66\tpass=66\tfail=0\tbase_discriminating=0`; with `--base-tool` pointed at the
  12516f7 auditor extracted by `git show` (sha256 62522acc350c23513f63d855231f82a9a6209b28b61535fb346e83cdf54e02e6,
  matching the closure's receipt) it prints `SUMMARY\ttotal=78\tpass=78\tfail=0\tbase_discriminating=11`.
  That is the record's count, the step-inventory's expected summary, and 66+12=78. Same capability
  (the r20 audit-contract oracle), same count. See finding 2 for the imprecise clause.
- **L27** — record `census/round-21/final-code-verification.json` (blob
  6483d98f7ea9bd7ddd1997648f64a143c1c56901, unchanged base→tip), key `matrix.stdout` at line 111:
  `SCENARIO\tS1\texit=0\tmatched=18/18\tsrc_sample_unchanged=yes` for S1-S3 followed by
  `MATRIX\tscenarios=3\treplayed=3\tsummaries_equal=True` (these separators are the record's own
  JSON-escaped tabs, i.e. the two bytes backslash t; replay-final.txt holds real tab bytes and
  therefore cannot satisfy this literal). The same run is the cell's cited
  record: census/round-21/accepted-matrix.json has `"scenarios": 3`, `"replayed": 3`,
  `"summaries_equal": true` and three records whose command is run-acceptance.py at rev 19571543 over
  s1 (clone), s2.git (bare) and the lane root. Same capability, same run, same count. Reason true,
  including the escape note.
- **L28** — same record, line 111: three `SCENARIO` lines each carrying `matched=18/18`, and
  accepted-matrix.json each record `"matched_command_count": 18` with `"all_matched": true`. Same
  run as the cell's "each18/18". Reason true (one occurrence per accepted source shape; the remote
  replay is a separate `remote` key, so it is not silently included).
- **L29** — base line 170's third count literal, `remote-source-after.json18/18`; no base command.

## L29: is there an honest binding?

- Item shape: line 170 computes rounds {20,21}; no basecmd, so only a `record:` row is admissible,
  and a run row is impossible (no tools/ or tests/fixtures/ script on that line).
- Its own record, census/round-21/remote-source-after.json (blob f4123cf12614e43bc26e500a75befbcfadbe3bac),
  states the count only as scalars: line 3 `"all_matched": true`, line 4566
  `"expected_command_count": 18`, line 4724 `"matched_command_count": 18`, line 4726
  `"observed_command_count": 18`. `grep -F '18/18'` over that file: NONE.
- Honest-shaped attempts are refused by the frozen counter (A2+A4, live runs at my scratch commits):
  `| L29 | SCORECARD.md:170 | 18/18 | record: census/round-21/remote-source-after.json |` →
  `RECORD-MISMATCH`; and `| ... | matched=18 | record: ... |` → `BAD-ROW(line-or-literal)`.
- `git grep -l -F '18/18' <rev> -- census/round-20 census/round-21` returns six files; every
  occurrence is the acceptance matrix or a quotation of it: replay-final.txt:2-4, replay-integrated.txt:2-4,
  final-verification.json:113, final-code-verification.json:111, r20-closure-excerpt.json (inside the
  78/78/0 sentence), recovery-status-catalog.json:226 ("the available `18/18` acceptance does not cover all final-tip hashed bytes").
  The remote-source replay's own count is printed as `matched=18` (final-code-verification.json:129,
  `remote.stdout`) or as the scalar field, never in `18/18` notation.
- Reproduced counter defect: each of four wrong-occurrence records is accepted for L29 with
  `mismatches=0`, `unbound=0` — replay-final.txt, final-code-verification.json, final-verification.json
  and recovery-status-catalog.json (full ITEM lines in the seat report, Attack log A7). With the 40
  landed rows unchanged and only this one wrong-occurrence L29 row added, the full frozen counter
  prints `SUMMARY items=41 bound_run=20 bound_record=21 unbound=0 mismatches=0` at rev
  1edd6476bd83aba17347686f16c9c8a93a835aa3: C1's frozen target is satisfiable by misattribution.
- Conclusion: the L1's section-preamble claim is true — under the frozen rule L29 has no honest
  binding, and C1 misses its target by one item (`unbound=1 mismatches=1`) at the landing commit and
  at the tip. The miss is a voluntary honesty choice, not a counter-forced outcome, and the counter
  cannot detect the substitution.

## Counter re-derivation (frozen tool, A2+A4)

```
python3 -B tools/souji-capability-cells.py --root <lane> --rev 24f343c8ffc820c0f89b4252cbdc94ab9a673aab \
  --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 \
  --only L21,L22,L23,L24,L25,L26,L27,L28,L29
```
```
ITEM L21 ... literal=total=4 failed=0  superseded binding=run    MATCH ... observed=SUMMARY total=4 failed=0 base_discriminating=2
ITEM L22 ... literal=total=11 failed=0 superseded binding=run    MATCH ... observed=SUMMARY total=11 failed=0
ITEM L23 ... literal=total=13 failed=0 superseded binding=run    MATCH ... observed=SUMMARY total=13 failed=0 base_discriminating=6
ITEM L24 ... literal=118/0             superseded binding=record MATCH census/round-21/r20-closure-excerpt.json
ITEM L25 ... literal=total=17 failed=0 superseded binding=run    MATCH ... observed=SUMMARY total=17 failed=0 base_discriminating=12
ITEM L26 ... literal=78/0              superseded binding=record MATCH census/round-21/r20-closure-excerpt.json
ITEM L27 ... literal=scenarios=3\treplayed=3 superseded binding=record MATCH census/round-21/final-code-verification.json
ITEM L28 ... literal=matched=18/18     superseded binding=record MATCH census/round-21/final-code-verification.json
ITEM L29 ... literal=18/18             base-cell binding=-        UNBOUND
SUMMARY items=9 bound_run=4 bound_record=4 unbound=1 mismatches=1 partial=1
```
Identical ITEM lines and the same SUMMARY line at `--rev 2c16d018e40db7c23420a2c3bb546b52957bcc25`.

## Rule checks (all rows)

- Row line == item line for L21-L28 (counter re-checks it; all MATCH); row pointers use base line
  numbers 166/167/168/170, matching c1-cells.tsv.
- Integer multisets row↔base: {4,0}, {11,0}, {13,0}, {118,0}, {17,0}, {78,0}, {3,3}, {18,18} — all
  equal to the tsv base literals.
- Record paths: no `:line`, no `waves`/`transcripts`/`sources` component, `.json` (not .py/.sh) —
  A4(b) satisfied; both records are in the item's round set ({19,20,21} and {20,21}) and are
  byte-unchanged base→landing→tip.
- No two items share a (record, literal) pair — A4(d) satisfied; L24 and L26 share the record but
  not the literal.
- Run rows keep the script stem on the base line and name no banned flag; the literal is not in the
  argv.

## Conclusion

L21-L28 are HONEST: every literal's occurrence is the measurement the cell states (same capability,
same run, same count), each reason sentence is true except the L26 clause noted, and all counts hold
at the landing commit and at the tip. L29's declared hole is real, so C1's self-reported miss is
accurate; the counter can nevertheless be satisfied dishonestly for exactly that item, which is a
defect of the instrument, not of the landed rows.
