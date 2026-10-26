# C1 bindings L13-L20 — append-only supersession rows (SwarmExecutor03, r31 w1)

Scope: items L13-L20 of `census/round-31/c1-cells.tsv` (SCORECARD.md base lines 163, 164, 165 at
`9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`). All eight are record bindings; none has a base command, and no
`tools/` or `tests/fixtures/` script basename stem occurs on lines 163-165, so a `run:` row would be
`BAD-ROW(run-shape)`.

## Byte-notation warning (integration-critical)

Two rows use the record's own separators, which are not spaces:

- L16, L17, L18 rows carry the two bytes `\` `t` (a JSON *escape*), because
  `census/round-18/final-verification-4800fd7.json` stores its stdout fields as JSON strings.
- L19, L20 rows carry one real U+0009 TAB inside the literal cell, because
  `census/round-21/reason-after.txt` and `reason-oracle-before.txt` separate summary fields with real tabs.

Verify after appending, on the lane repo:

```
sed -n '/^### Round 31 capability-cell supersessions$/,$p' SCORECARD.md | cat -A | grep -E '^\| L1[36]|^\| L19|^\| L20'
```

`L16-L18` must show `pass=61\tfail=0` (backslash printed literally); `L19-L20` must show `total=27^Ipass=27`
and `total=27^Ipass=6` (`^I` is cat -A's tab).

## Append block (verbatim; sha256 of the block below = `da4e633283777d4fab3b7e44a4c37d73b4d763abd6d16770ffead6f25cdebea6`)

```
### Round 31 capability-cell supersessions

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L13 | SCORECARD.md:163 | 12/9 | record: census/round-18/final-verification-4800fd7.json | The r18 final-verification record holds the matrix-final run whose command wrote the cited c1-matrix-4800fd7.json, and its r17-base stdout row prints r18-bounded=12/9fail. |
| L14 | SCORECARD.md:163 | 12/0 | record: census/round-18/final-verification-4800fd7.json | The same record's changed-arm stdout row prints r18-bounded=12/0fail at 4800fd7, the post-fix 12/0 the cell states. |
| L15 | SCORECARD.md:163 | 69/0 | record: census/round-18/final-verification-4800fd7.json | The same changed-arm row prints selftest=69/0fail, the census selftest 69/0 the cell states. |
| L16 | SCORECARD.md:164 | pass=61\tfail=0 | record: census/round-18/final-verification-4800fd7.json | The record's gate-selftest check prints SELFTEST\tpass=61\tfail=0, so 61 cases and 0 failed are restated in the record's own JSON-escaped notation. |
| L17 | SCORECARD.md:164 | total=11\tfailed=0 | record: census/round-18/final-verification-4800fd7.json | The record's gate-r18-fixture check prints SUMMARY\ttotal=11\tfailed=0, the pointer fixture 11/0 restated in the record's own JSON-escaped notation. |
| L18 | SCORECARD.md:164 | total=15\tfailed=0 | record: census/round-18/final-verification-4800fd7.json | The record's gate-r16-fixture check prints SUMMARY\ttotal=15\tfailed=0, the r16 fixture 15/0 restated in the record's own JSON-escaped notation. |
| L19 | SCORECARD.md:165 | total=27	pass=27 | record: census/round-21/reason-after.txt | The cited r21 reason-canary receipt's SUMMARY line prints total=27 pass=27 fail=0 leaks=0 base_leaks=19, the synthetic 27/27 the cell states. |
| L20 | SCORECARD.md:165 | total=27	pass=6 | record: census/round-21/reason-oracle-before.txt | The r21 pre-repair oracle receipt of the same 27-case canary against the old tool prints total=27 pass=6 fail=21 leaks=19, the old emissions 6/27. |
```

## Why each record IS the row's evidence

| item | base literal | record (unchanged blob at base and tip) | located quote (verbatim, from bytes opened this run) |
|---|---|---|---|
| L13 | 12/9 | `census/round-18/final-verification-4800fd7.json` (blob `0d37a056…` at base and at `1b81136`) | `checks[0]` matrix-final stdout, r17-base row: `r18-bounded=12/9fail` |
| L14 | 12/0 | same blob | `checks[0]` stdout, changed row: `r18-bounded=12/0fail` |
| L15 | 69/0 | same blob | `checks[0]` stdout, changed row: `selftest=69/0fail` |
| L16 | 61/0 | same blob | `checks[1]` gate-selftest stdout: `SELFTEST\tpass=61\tfail=0` |
| L17 | 11/0 | same blob | `checks[3]` gate-r18-fixture stdout: `SUMMARY\ttotal=11\tfailed=0` |
| L18 | 15/0 | same blob | `checks[2]` gate-r16-fixture stdout: `SUMMARY\ttotal=15\tfailed=0` |
| L19 | 27/27 | `census/round-21/reason-after.txt` (blob `d9b25a31…`) | line 29: `SUMMARY<TAB>total=27<TAB>pass=27<TAB>fail=0<TAB>leaks=0<TAB>base_leaks=19<TAB>max_reason_bytes=160` |
| L20 | 6/27 | `census/round-21/reason-oracle-before.txt` (blob `69dd8498…`) | line 49: `SUMMARY<TAB>total=27<TAB>pass=6<TAB>fail=21<TAB>leaks=19<TAB>base_leaks=19<TAB>max_reason_bytes=454` |

Base cells quoted for traceability (SCORECARD.md at `9f17a1e`): line 163 `12/9 failed →12/0` and
`census selftest 69/0`; line 164 `selftest 61/0, pointer fixture 11/0, r16 fixture 15/0`; line 165
`r21 synthetic27/27 (old emissions6/27, leaks19→0)`.

Line 163's cell cites `census/round-18/c1-matrix-4800fd7.json` for 12/9 → 12/0, but that file is
field-serialized (`"failed": 9`, `"total": 12`) and contains no slash form; the counter refuses it
(control below). `census/round-18/final-verification-4800fd7.json` is the r18 acceptance record whose
matrix-final check ran `run-matrix.py --changed 4800fd7… --output …/c1-matrix-4800fd7.json` and kept the
matrix stdout, so it is the run receipt of the same measurement, at the same measured revision.

L19's cell cites `census/round-21/reason-after.txt` (post-repair canary: 27/27). L20's 6/27 is the same
27-case canary run against the old tool, committed in the same round as
`census/round-21/reason-oracle-before.txt` (`4d5bf78`, r21 repair commit); that receipt also states
`leaks=19`, matching the cell's `leaks19→0`.

## Acceptance proof (scratch, origin removed)

Scratch: `/fast/scratch/hyaku/souji-r31/C1BindC/`. Clone parent: current lane tip
`1b811368461785040e955f41f9c97e62f61fd67c` (SCORECARD.md byte-identical to base:
`git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` empty). Append block committed in scratch as
`1edc8240a1a7ff5eb5e1a148d2c01f83bd253c2c` (13 insertions, one file).

Base state of these eight items (red before), `--only` on the lane repo at the tip:

```
ITEM	L13	SCORECARD.md:163	literal=12/9	base-cell	binding=-	UNBOUND
…
SUMMARY items=8 bound_run=0 bound_record=0 unbound=8 mismatches=8 partial=1 rev=1b811368461785040e955f41f9c97e62f61fd67c
```

Proof, run twice (identical output both times):

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-cells.py --root /fast/scratch/hyaku/souji-r31/C1BindC/c --rev 1edc8240a1a7ff5eb5e1a148d2c01f83bd253c2c --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L13,L14,L15,L16,L17,L18,L19,L20 --scratch /fast/scratch/hyaku/souji-r31/C1BindC/cnt
ITEM	L13	SCORECARD.md:163	literal=12/9	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L14	SCORECARD.md:163	literal=12/0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L15	SCORECARD.md:163	literal=69/0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L16	SCORECARD.md:164	literal=pass=61\tfail=0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L17	SCORECARD.md:164	literal=total=11\tfailed=0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L18	SCORECARD.md:164	literal=total=15\tfailed=0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L19	SCORECARD.md:165	literal=total=27	pass=27	superseded	binding=record	MATCH	census/round-21/reason-after.txt
ITEM	L20	SCORECARD.md:165	literal=total=27	pass=6	superseded	binding=record	MATCH	census/round-21/reason-oracle-before.txt
SUMMARY items=8 bound_run=0 bound_record=8 unbound=0 mismatches=0 partial=1 rev=1edc8240a1a7ff5eb5e1a148d2c01f83bd253c2c
rc=0
```

(In the L19/L20 `literal=` fields the gaps are the real U+0009 bytes; `cat -A` shows them as `^I`.)

## Control: forced bindings fail (the rule bites)

Second scratch clone at base, two forced rows, commit `ec827f76260539553ec195e6f4da524a8fef1171`:

```
ITEM	L13	SCORECARD.md:163	literal=12/9	superseded	binding=record	RECORD-MISMATCH	census/round-18/c1-matrix-4800fd7.json
ITEM	L16	SCORECARD.md:164	literal=61/0	superseded	binding=record	RECORD-MISMATCH	census/round-18/final-verification-4800fd7.json
SUMMARY items=2 bound_run=0 bound_record=0 unbound=0 mismatches=2 partial=1 rev=ec827f76260539553ec195e6f4da524a8fef1171
rc=1
```

So: the cell's own cited matrix JSON cannot carry `12/9` (byte absence, not a judgement), and a slash form
of L16 cannot be invented — the escape restatement is forced by the record bytes.

## Not run here

- The full 41-item counter after integration (target `unbound=0 mismatches=0`): the L1's landing gate.
  My proof used `--only`, whose SUMMARY is `partial=1`.
- Any write to the lane: rows only, no commit by me.
