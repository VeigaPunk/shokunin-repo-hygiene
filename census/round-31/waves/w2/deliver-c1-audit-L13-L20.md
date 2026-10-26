# C1 audit — supersession rows L13-L20 (round-18 final-verification JSON, round-21 reason receipts)

Seat SwarmReviewer03, Souji r31 wave 2. Read-only audit at the C1 landing commit
24f343c8ffc820c0f89b4252cbdc94ab9a673aab; records re-checked unchanged at lane tip
2c16d018e40db7c23420a2c3bb546b52957bcc25. Base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc.

## Verdicts

| Row | Cell (base line) | Literal | Record occurrence (file:line at 24f343c8) | Verdict |
|---|---|---|---|---|
| L13 | SCORECARD.md:163 bounded repository-content census (r18) | `12/9` | census/round-18/final-verification-4800fd7.json:25, matrix-final stdout r17-base segment | HONEST |
| L14 | SCORECARD.md:163 | `12/0` | same record:25, matrix-final stdout changed segment | HONEST |
| L15 | SCORECARD.md:163 | `69/0` | same record:25, matrix-final stdout changed segment | HONEST |
| L16 | SCORECARD.md:164 evidence-pointer gate (r18) | `pass=61\tfail=0` | same record:38, gate-selftest check stdout | HONEST |
| L17 | SCORECARD.md:164 | `total=11\tfailed=0` | same record:66, gate-r18-fixture check stdout | HONEST |
| L18 | SCORECARD.md:164 | `total=15\tfailed=0` | same record:52, gate-r16-fixture check stdout | HONEST |
| L19 | SCORECARD.md:165 process-residue observations (r18; r21 synthetic repair) | `total=27\tpass=27` | census/round-21/reason-after.txt:29 | HONEST |
| L20 | SCORECARD.md:165 | `total=27\tpass=6` | census/round-21/reason-oracle-before.txt:49 | HONEST |

No `run:` rows in L13-L20; step (3) of the assignment is vacuous for this range.

## Per-row evidence

All quotes are verbatim bytes opened this run from the blobs at 24f343c8 (records unchanged base→landing→tip; `git diff --stat` empty both hops).

- **L13** — fv.json:25 r17-base segment: `selftest=49/0fail\tr18-bounded=12/9fail\tr17-hygiene=29/0fail`. Same capability (r18-bounded column = the bounded census), same run (check `matrix-final`, fv.json:13-28, whose command carries `--output /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-18/c1-matrix-4800fd7.json` — the cell's cited record), same count (c1-matrix-4800fd7.json r17-base arm `r18-bounded` total=12 failed=9, matrix.json:2446/2497/2509). Reason sentence true: the matrix-final run wrote the cited record; its r17-base stdout row prints the literal. Nuance: the r14-harm segment of the same stdout also prints `r18-bounded=12/9fail` (c1-matrix-4800fd7.json r14-harm arm failed=9, matrix.json:1863) — same capability, same run, coincidentally same count under harm injection; the row names the r17-base row, which is the cell's base arm. Not a defect.
- **L14** — fv.json:25 changed segment: `selftest=69/0fail\tr18-bounded=12/0fail\tr17-hygiene=29/0fail`. Changed-arm rev is the measured commit (matrix.json `changed_rev`/`git_head` = 4800fd79488e5f2c11a18117958f104171d85dc8), so "at 4800fd7" is true; c1-matrix-4800fd7.json changed arm r18-bounded total=12 failed=0 (matrix.json:544/595/607). Nuance: `12/0` also occurs 3x in the same stdout as `r14-namespace=12/0fail` — a different capability with the same digits; the row names the changed-arm r18-bounded occurrence, the honest one. Not a defect.
- **L15** — fv.json:25 changed segment: `changed\t21c19ff620ad\tbash-n=0\tsc=0\tselftest=69/0fail`. 21c19ff620ad is the recorded sha256 prefix of tools/souji-census.sh in the record's `tools_sha256`, i.e. the changed arm IS the measured census; c1-matrix-4800fd7.json changed arm selftest checks=69 failed=0 (matrix.json:611-613). Cell states "census selftest 69/0". Same run, same capability, same count.
- **L16** — fv.json:38, check `gate-selftest` (command `python3 .../tools/souji-landing-gate.py --selftest`, fv.json:29-35), stdout ends `SELFTEST\tpass=61\tfail=0`. The two-byte `\t` escapes are the record's own JSON-escaped notation, exactly the row's literal shape. Cell states "selftest 61/0" for the evidence-pointer gate; the check is that gate's selftest.
- **L17** — fv.json:66, check `gate-r18-fixture` (command `python3 .../tests/fixtures/r18-landing-pointers.py --tool .../tools/souji-landing-gate.py`, fv.json:56-63), stdout ends `SUMMARY\ttotal=11\tfailed=0`. Cell states "pointer fixture 11/0"; the r18 pointer fixture is tests/fixtures/r18-landing-pointers.py, 11 cases.
- **L18** — fv.json:52, check `gate-r16-fixture` (command `python3 .../tests/fixtures/r16-landing-gate.py --tool .../tools/souji-landing-gate.py`, fv.json:42-49), stdout ends `SUMMARY\ttotal=15\tfailed=0`. Cell states "r16 fixture 15/0".
- **L19** — reason-after.txt:1 `COMMAND bash .../tests/fixtures/r21-reason-canary.sh --tool .../tools/souji-proc-census.sh --base /var/tmp/souji-r21-base-proc.sh`; line 29 `SUMMARY\ttotal=27\tpass=27\tfail=0\tleaks=0\tbase_leaks=19\tmax_reason_bytes=160`. Every field the reason lists is on that line; the canary fixture makes it the synthetic 27/27 the cell states.
- **L20** — reason-oracle-before.txt:49 `SUMMARY\ttotal=27\tpass=6\tfail=21\tleaks=19\tbase_leaks=19\tmax_reason_bytes=454`. "Same 27-case canary": the CASE name columns of the two receipts are byte-identical (27 names, `diff` empty). "Against the old tool": the receipt carries no COMMAND line, so this rests on the committed r21 lesson, corpus/lessons/round-21.md:9 "the same27-case oracle is6/27 baseline versus27/27 changed, leaks19→0", and is corroborated inside the receipts themselves: oracle-before leaks=19 equals reason-after's base_leaks=19 (the old tool's reference leak count). Cell states "old emissions6/27". Honest, with the provenance nuance recorded.

## Reason-sentence and rule checks (all rows)

- Record paths exist at 24f343c8 and are byte-unchanged base→landing→tip (`git diff --stat` empty both hops); no `waves`/`transcripts`/`sources` component, no `:line` suffix, no code suffix — A4(b) satisfied.
- Row pointers match the enumeration: c1-cells.tsv at 1d45496a rows L13-L15 (line 163, round set 18), L16-L18 (line 164, rounds 16,18), L19-L20 (line 165, rounds 18,21); every record sits in census/round-18/ or census/round-21/ — inside the item's round set.
- Integer multisets row↔base: {12,9}, {12,0}, {69,0}, {61,0}, {11,0}, {15,0}, {27,27}, {27,6} — all equal to the tsv base literals 12/9, 12/0, 69/0, 61/0, 11/0, 15/0, 27/27, 6/27.
- No two items in the range share a (record, literal) pair — A4(d) satisfied.
- SCORECARD cells at lines 163-165 are untouched at tip (base→tip diff has zero removed lines; only the appended supersession section).

## Counter re-derivation

`python3 -B tools/souji-capability-cells.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 24f343c8... --base 9f17a1ef... --list-rev 1d45496a... --only L13,L14,L15,L16,L17,L18,L19,L20` (scratch clone, origin removed):

```
ITEM   L13 ... literal=12/9   superseded binding=record MATCH census/round-18/final-verification-4800fd7.json
ITEM   L14 ... literal=12/0   superseded binding=record MATCH census/round-18/final-verification-4800fd7.json
ITEM   L15 ... literal=69/0   superseded binding=record MATCH census/round-18/final-verification-4800fd7.json
ITEM   L16 ... literal=pass=61\tfail=0   superseded binding=record MATCH census/round-18/final-verification-4800fd7.json
ITEM   L17 ... literal=total=11\tfailed=0 superseded binding=record MATCH census/round-18/final-verification-4800fd7.json
ITEM   L18 ... literal=total=15\tfailed=0 superseded binding=record MATCH census/round-18/final-verification-4800fd7.json
ITEM   L19 ... literal=total=27   pass=27 superseded binding=record MATCH census/round-21/reason-after.txt
ITEM   L20 ... literal=total=27   pass=6  superseded binding=record MATCH census/round-21/reason-oracle-before.txt
SUMMARY items=8 bound_run=0 bound_record=8 unbound=0 mismatches=0 partial=1 rev=24f343c8...
```

(partial=1 is the diagnostic `--only` marker.) The L1's landed reading holds for this slice: all eight rows bind and match.

## Conclusion

All eight rows L13-L20 are HONEST: each literal's stated occurrence is the measurement the cell states (same capability, same run, same count), every reason sentence is true, and the records are unchanged pre-round records of the row's own round. No falsification found in this range; C1's landed claim is not refuted by this slice.
