# SwarmRevenger24 — r31 C1 literal provenance (the 22 no-basecmd capability literals)

## Status
STATUS: PASS — all 22 enumerated literals with an empty `basecmd` (L03 L08-L10 L13-L20 L24-L29 L34 L37 L39 L41) are traced to the commit that wrote them, the round, and a committed record of that round that shows the count in another notation; every one is `record-bindable`, and a scratch-only drill of the frozen counter bound all 22 through `record:` rows (`unbound=0 mismatches=0`).

## Evidence

Revisions: lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, lane HEAD read this run `1b811368461785040e955f41f9c97e62f61fd67c`, drill commit `ca34e3614e5e82baf94b9b00367cd97ec5721427` (scratch only). No tool was installed or upgraded this run.

1. Inputs. `census/round-31/c1-cells.tsv` has exactly 22 rows with an empty fifth field; their base cells were read from the base blob
   `git -C <lane> show 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc:SCORECARD.md` (lines 153, 159, 163, 164, 165, 168, 170, 174, 313, 314, 355).

2. Writing commit. `git log -S'<literal>' --format='%H %ad %s' -- SCORECARD.md` was run for each of the 21 distinct literals, then attributed to the cell: 12 of the 21 changed occurrence count in two or more commits, and 6 of them (`5/5 4/4 3/3 18/18 12/0 78/0`) also occur in axis cells elsewhere in the file, so `-S` alone cannot attribute an occurrence to a capability cell. Attribution used row identity: parse SCORECARD.md at each of the 67 commits touching it up to base, match the capability row by name prefix, take the first commit whose evidence cell contains the literal (verified against the immediately preceding cell text for every item).

3. Record. For each item `census/round-<K>/` was swept for K in the item's `rounds` column, excluding `waves/` and `transcripts/`, for a record that states the same numbers in another notation. Each chosen record is a blob unchanged between base and HEAD (`git -C <lane> diff --stat <base>..HEAD -- <paths>` is empty) and its integer multiset equals the base literal's.

4. Externally re-run proof (scratch clone of the lane, base checked out, the 22 proposed rows appended, commit `ca34e36`, lane untouched):
```
python3 -B <lane>/tools/souji-capability-cells.py \
  --root /fast/scratch/hyaku/souji-r31/SwarmRevenger24/drill/c \
  --rev ca34e3614e5e82baf94b9b00367cd97ec5721427 \
  --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
  --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 \
  --only L03,L08,L09,L10,L13,L14,L15,L16,L17,L18,L19,L20,L24,L25,L26,L27,L28,L29,L34,L37,L39,L41
```
Every line was `superseded binding=record MATCH`; last line:
`SUMMARY items=22 bound_run=0 bound_record=22 unbound=0 mismatches=0 partial=1 rev=ca34e3614e5e82baf94b9b00367cd97ec5721427`, exit 0. This ran the frozen counter bytes, not a reimplementation; it is a scratch drill, so the L1 must still re-run at its own landing commit.

## Findings

1. All 22 are `record-bindable`; none is `record-in-waves-only`, none is `no-record`. Aggregate: 22 record-bindable / 0 / 0. Locations of the 22 chosen records:
   `census/round-13/final-checks.md`, `census/round-21/read-fixture-after.txt`, `census/round-21/read-fixture-before.txt`, `census/round-21/render-edges-after.txt`, `census/round-18/final-verification-4800fd7.json` (L13-L18), `census/round-21/reason-after.txt`, `census/round-21/reason-oracle-before.txt`, `census/round-21/acceptance-c2-first.json` (L24-L26), `census/round-21/replay-final.txt` (L27-L29), `census/round-24/records/c1-control-stub.tsv`, `census/round-29/records/c1-fixture-red-before.txt`, `census/round-29/records/c2-fixture-red-before.txt`, `census/round-30/records/c2-fixture-red-before.txt`.

2. Per-item origin and record (writer = commit that first wrote the literal into that row's evidence cell; round = that commit's round; record line = the line carrying the count):

| id | lit | writer (r) | record:line | record text |
|---|---|---|---|---|
| L03 | 5/5 | 23014d4 (r13) | round-13/final-checks.md:19 | `fixture: 5/5 checks passed` |
| L08 | 32/32 | f7431d7 (r21) | round-21/read-fixture-after.txt:34 | `total=32 pass=32 fail=0` |
| L09 | 18/32 | f7431d7 (r21) | round-21/read-fixture-before.txt:34 | `total=32 pass=18 fail=14` |
| L10 | 4/4 | 4eb2fda (r21) | round-21/render-edges-after.txt:5 | `total=4 pass=4 fail=0` |
| L13 | 12/9 | 74f9adb (r18) | round-18/final-verification-4800fd7.json:25 | `r18-bounded=12/9fail` |
| L14 | 12/0 | 74f9adb (r18) | same:25 | `r18-bounded=12/0fail` |
| L15 | 69/0 | 74f9adb (r18) | same:25 | `selftest=69/0fail` |
| L16 | 61/0 | 74f9adb (r18) | same:38 | `SELFTEST pass=61 fail=0` |
| L17 | 11/0 | 42d9ff3 (r18) | same:66 | `SUMMARY total=11 failed=0` |
| L18 | 15/0 | 74f9adb (r18) | same:52 | `SUMMARY total=15 failed=0` |
| L19 | 27/27 | f7431d7 (r21) | round-21/reason-after.txt:29 | `total=27 pass=27 fail=0 leaks=0 base_leaks=19` |
| L20 | 6/27 | f7431d7 (r21) | round-21/reason-oracle-before.txt:49 | `total=27 pass=6 fail=21 leaks=19` |
| L24 | 118/0 | 4eb2fda (r21) | round-21/acceptance-c2-first.json:209 | `SELFTEST pass=118 fail=0` |
| L25 | 17/0 | 4eb2fda (r21) | same:976 | `SUMMARY total=17 failed=0 base_discriminating=12` |
| L26 | 78/0 | 4eb2fda (r21) | same:588 | `SUMMARY total=78 pass=78 fail=0 base_discriminating=11` |
| L27 | 3/3 | f7431d7 (r21) | round-21/replay-final.txt:5 | `MATRIX scenarios=3 replayed=3 summaries_equal=True` |
| L28 | 18/18 | f7431d7 (r21) | same:2 | `SCENARIO S1 exit=0 matched=18/18 src_unchanged=yes` |
| L29 | 18/18 | 4eb2fda (r21) | same:2 | same |
| L34 | 4/8 | 315422b (r24) | round-24/records/c1-control-stub.tsv:17 | `cases=8 pass=4 control=FALSE-GREEN-REJECTED` |
| L37 | 8/20 | de874ee (r29) | round-29/records/c1-fixture-red-before.txt:12 | `cases=20 pass=8 control=TOLERATED` |
| L39 | 8/15 | de874ee (r29) | round-29/records/c2-fixture-red-before.txt:22 | `cases=15 pass=8 control=TAMPER-REJECTED` |
| L41 | 3/7 | 393b011 (r30) | round-30/records/c2-fixture-red-before.txt:32 | `cases=7 pass=3 control=FALSE-GREEN-REJECTED` |

   Full hashes, exact columns and the base literal per row are in the delivery TSV. Every writer round is inside the item's `rounds` column, and every chosen record lies in the writer's own round directory, so its `census/round-<K>/` factor K is in that column and no chosen path contains a `waves` or `transcripts` component. L17 is the only item whose literal predates the final wording: 42d9ff3 wrote `11/0` beside the r18 pointer fixture, and 74f9adb rewrote the cell into the `final-verification` form that survives at base (SCORECARD.md:164, "selftest 61/0, pointer fixture 11/0, r16 fixture 15/0"). Table cells render record tabs, and the JSON records' two-byte `\t` escapes, as single spaces; the byte-exact shapes are in the delivery TSV and Finding 5.

3. The cell-named record is not always the byte-bindable record (10 items). The frozen record rule requires the row literal to occur contiguously in the record's bytes; these cells cite a different record than the one that carries the literal: L03 (cell cites `census/round-13/verification.json`; bindable `final-checks.md`), L08/L09/L10 (cell cites `census/round-21/oracle-acceptance.json`; bindable the read/render fixture captures), L13/L14/L15 (cell cites `c1-matrix-4800fd7.json`, whose `total` and `failed` are separate keys; bindable the one-line arms summary in `final-verification-4800fd7.json:25`), L20 (cell says "old emissions6/27" beside `reason-after.txt`; the 6-of-27 capture is `reason-oracle-before.txt:49`), L27/L29 (see 4). This is permitted by the frozen rule (any record in the round directory with the literal) but the row should name the record it actually binds.

4. L29's own record cannot bind `18/18`: `census/round-21/remote-source-after.json:4724` holds `"matched_command_count": 18` with `expected_command_count` at :4566 and `observed_command_count` at :4726 on separate lines, so no `18/18`-shaped literal exists in its bytes (SCORECARD.md:170, "remote-source-after.json18/18"). The eligible census records that do carry `18/18` bytes are `census/round-21/replay-final.txt:2-4`, `replay-integrated.txt:2-4`, `final-verification.json:113`, `final-code-verification.json:111`, `r20-closure-excerpt.json:40`, and `census/round-20/recovery-status-catalog.json:226`; the drill bound L29 to `replay-final.txt:2`. L27 has the same shape: `accepted-matrix.json` stores `"scenarios": 3` and `"replayed": 3` on lines 2-3, while `replay-final.txt:5` carries `scenarios=3 replayed=3` on one line.

5. Row-literal forms that the counter accepts (verified by the drill, one row per item): `5/5`; `total=32<TAB>pass=32`; `total=32<TAB>pass=18`; `total=4<TAB>pass=4`; `12/9`; `12/0`; `69/0`; `pass=61\tfail=0`; `total=11\tfailed=0`; `total=15\tfailed=0`; `total=27<TAB>pass=27`; `total=27<TAB>pass=6`; `pass=118\tfail=0`; `total=17 failed=0`; `pass=78\tfail=0`; `scenarios=3<TAB>replayed=3`; `18/18` (L28 and L29); `cases=8 pass=4`; `cases=20 pass=8`; `cases=15 pass=8`; `cases=7 pass=3`. `<TAB>` is a real tab byte (text captures); in the JSON records the blob itself stores the two bytes backslash and `t`, so the row literal must carry `\t` literally (L16 L17 L18 L24 L26); L25's JSON string uses real spaces. Integer multisets equal the base literals, so the counter's restatement guard holds.

6. Rewordings that keep the literal (for audit of "who wrote it"): L08/L09 `fixture32/32` (f7431d7) → `literal32/32` (4eb2fda) → `read32/32` (af73b8b, r22); L24 `73/0; tests/fixtures/r19-seat-audit-shapes.py 5/0` (1db7108, r19) → `auditor selftest118/0` (4eb2fda, r21), the `118/0` notation itself having appeared first in the seat-transcript row at f7431d7; L27 `replay-integrated.txt`3/3 (f7431d7) → `accepted-matrix.json`3/3 (4eb2fda); L29 `each18/18` (f7431d7) → `remote-source-after.json18/18` (4eb2fda); L34's rows were re-appended in r26 (a529c76, 07f83e6) after the r24 append, literal unchanged.

7. `git log -S` is not attributable across cells. The literal sweeps returned: `5/5` 6 commits (earliest 97f22c9 r2, in the r2 operability axis cell), `4/4` 6 (earliest 48a64d8 r4), `3/3` 5 (earliest 42d0b7b r14), `18/18` 4 (earliest 163158a r16), `12/0` 3 (earliest d98065d r17), `78/0` 3 (earliest e41db6d r20, whose SCORECARD.md:14 calibration cell carries `Oracle78/0`). Nine of the 21 literals produced a single `-S` commit (`69/0 61/0 27/27 6/27 118/0 17/0 8/20 8/15 3/7`); the other six multi-commit literals (`32/32 18/32 12/9 11/0 15/0 4/8`) changed only inside their own capability row, through the rewordings and re-appends in Finding 6.

8. No unbound provenance remains in this slice: 22 of 22 items have a writer, a round inside their `rounds` column, and a same-round record whose bytes show the count; the frozen counter's record rule accepts all 22 (drill, Evidence 4). Nothing outside the lane was read or written; no jj command was run; the drill clone and its `origin` removal existed only under `/fast/scratch/hyaku/souji-r31/SwarmRevenger24/` and that directory has been removed.

## Deliveries
- `.ufo/waves/round-31/w1/deliver-c1-literal-provenance.tsv` — 22 rows + header, columns `id line literal writing_commit round record_path record_line record_text class`; `record_text` renders real tab bytes as `\t` to keep 9 columns intact (JSON records already hold backslash-t in their bytes).
