# S55executor03 — r55 w1 standing receipts at the round tip

Seat: S55executor03 (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Frozen claims read first: `census/round-55/preregistration.txt` (freeze commit
`e8f338674dea386c186aa7657ef2142cbb4b6d48`). All six frozen instrument pins were re-hashed
before any probe and equal the prereg (`pins-and-captures.txt`): c1-counter `944feafa…`,
c2-counter `e4eb34e6…`, builder `e629a2e9…`, run-matrix `ce13d4ff…`, c1-expected
`ca096117…`, c2-expected `63391af…`.

Measured revisions:

- `4b10ddd1741a948c89d283358affd1da2ab3fd95` — receipt correction, pinned by the assignment
  for the landing suite;
- `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f` — lane tip at dispatch (the commit adding the
  real-lane v4 leg records and the S278 capture); the scratch clone's tip equals it.

Scratch clone: `/fast/scratch/hyaku/souji-r55/S55executor03/clone` (`git clone --no-hardlinks`,
`git rev-parse --show-toplevel` verified inside it).

Scratch: `/fast/scratch/hyaku/souji-r55/S55executor03/` — deleted before yield; every receipt
was copied into this seat directory first.

Tooling installed/updated: none (no pacman transaction of any kind; uv/npx/binary channels
unused). Git/jj mutations: none. The only git writes in this seat were `git init`/`commit`
performed by the frozen fixture builder inside my own scratch.

All commands ran with `TMPDIR=/fast/scratch/hyaku/souji-r55/S55executor03`, `python3 -B`, from
either the scratch clone root or the lane root. Every receipt below is verbatim stdout+stderr
followed by its exit line, and carries its own `# … command …` header.

## Verdict table

| # | check | receipt | exit | verdict |
|---|---|---|---|---|
| 1a | r46 landing suite @ `4b10ddd1` (assigned pin) | `r46-landing-suite.txt` | 0 | GREEN `unfiled=0` (note 1) |
| 1b | r46 landing suite @ tip `3ce0ba03` (supplemental) | `r46-landing-suite-tip.txt` | 0 | GREEN, identical SUMMARY |
| 2a | r53 fixture build (frozen builder, scratch) | `r53-build.txt` | 0 | 10 fixtures BUILT |
| 2b | r53 v2 counters over the fixture set | `r53-matrix.txt`, `c1-matrix-v2.tsv`, `c2-matrix-v2.tsv` | 0 | 10/10 verdicts equal the committed matrices |
| 2c | r53 v1 arms (frozen r52 counters, same fixtures) | `c1-matrix-v1.tsv`, `c2-matrix-v1.tsv` | 0 | 10/10 equal the committed matrices |
| 2d | r53 c1/c2 on the real lane at the tip (supplemental) | `r53-reallane-c1.txt`, `r53-reallane-c2.txt` | 0 / 0 | GREEN |
| 3a | r52 c1 at tip, in the clone | `r52-c1.txt` | 0 | GREEN filed=2 unfiled=0 |
| 3b | r52 c2 at tip, in the clone | `r52-c2.txt` | 0 | GREEN receipt=ok |
| 4a | r54 v3 c1, real lane at tip | `r54-c1.txt` | 0 | identical to `census/round-54/records/c1-tip.txt` modulo rev/base |
| 4b | r54 v3 c2, real lane at tip | `r54-c2.txt` | 0 | identical modulo rev |
| 5 | census before-receipt verify | `census-verify.txt` | 0 | `VERIFY ok` |
| S1 | frozen-pin + capture-binding audit | `pins-and-captures.txt` | 0 | all pins equal; 3/3 capture→receipt bindings ok |
| S2 | standing-instrument landing history | `history-immutability.txt` | 0 | each file last touched by its own round's commit |

Assigned items 1–5: **5/5 green, no red**. The two supplemental rows are not assigned; they are
cheap read-only corroboration of the same standing claims and are labelled as such.

## 1. Landing suite (r46 counter)

`r46-landing-suite.txt` — full output:

```
# r46 landing-suite counter @ rev 4b10ddd1741a948c89d283358affd1da2ab3fd95, root=/fast/scratch/hyaku/souji-r55/S55executor03/clone
SUMMARY assertions=580 mismatches=76 registered=76 corrected=0 exempted=0 unfiled=0 instrument_sha256=a332491607129195f59d289b431cc29fb4c8dc21e10859d552700697a3b09831
EXIT=0
```

`r46-landing-suite-tip.txt` (supplemental, at the dispatch tip):

```
# r46 landing-suite counter @ wave tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, root=clone
SUMMARY assertions=580 mismatches=76 registered=76 corrected=0 exempted=0 unfiled=0 instrument_sha256=a332491607129195f59d289b431cc29fb4c8dc21e10859d552700697a3b09831
EXIT=0
```

Both revisions produce the identical SUMMARY; every mismatch present is registered (76/76), so
the unfiled count is zero as required. `instrument_sha256` is unchanged from the r52 standing
receipt (`a3324916…`) — the landing instrument is the same bytes.

**Note 1 (wording deviation, not a failure).** The assignment says “the SUMMARY line ending
`unfiled=0`”. The frozen r46 counter prints `… unfiled=0 instrument_sha256=<64hex>`: `unfiled=0`
is present but the line literally ends with the instrument pin. Exit 0 and `unfiled=0` both hold;
only the assignment's wording does not match the instrument's output format.

## 2. r53 standing counters over the r53 fixture set

Build (`r53-build.txt`, frozen builder `d5ce557e…`, run from the clone root):

```
# r53 fixture build + v2 matrix (frozen builder/run-matrix from commit 3ce0ba03)
BUILT F1-HONEST-TIP tip=98246c8b7ebc02ff1d4e9a0c90acff6e97d1b856
BUILT F2-MULTI-ANNOT tip=73abbfb2303798083baef61df47b815401dfc957
BUILT F3-INERT tip=5763e788b1922c81624bc6bf5099ca98112b8ef9
BUILT F4-FENCE tip=a46012e6e95e2f7557af84e94192d79bc970c16d
BUILT F5-REWRITE tip=40ad0babb9bf852ae41fccb26abe440e62e4a3a2
BUILT F6-RECORD-DRIFT tip=175774b784d5fb3a96b2a4f983fbd97aac63ec57
BUILT FH-HONEST tip=dcae43ee62e7dd1399a4bc6c1f8410972a354bf5
BUILT FA1-UNSORTED tip=6ce84fc6674340d8d94df3c50e65d8eec8a90677
BUILT FA2-COMMENT tip=637986fecd7fffe4ae8d53443a03e57fb0991747
BUILT FA3-TAMPER tip=815dc306538db94bd879113541007c354a73adf6
MANIFEST /fast/scratch/hyaku/souji-r55/S55executor03/selftest/fixture-manifest.tsv
BUILD-EXIT=0
```

Matrix driver (`r53-matrix.txt`, frozen `run-matrix.sh`, cwd = clone root, arg = scratch root):

```
# r53 run-matrix.sh output (scratch root arg)
c1-v1 rc=0
c1-v2 rc=0
c2-v1 rc=0
c2-v2 rc=0
MATRIX-EXIT=0
```

Rebuilt v2 rows (`c1-matrix-v2.tsv`, `c2-matrix-v2.tsv` in this directory):

```
fixture	counter	rev	base	exit	finding	SUMMARY
F1-HONEST-TIP	v2-r53	98246c8b7ebc	98246c8b7ebc	0	-	SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 recomputed=79 rev=98246c8b7ebc base=98246c8b7ebc
F2-MULTI-ANNOT	v2-r53	73abbfb23037	73abbfb23037	1	MULTIPLE-ANNOTATIONS	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=ok multi=1 inert=1 fenced=0 recomputed=79 rev=73abbfb23037 base=73abbfb23037
F3-INERT	v2-r53	5763e788b192	5763e788b192	1	INERT-CORRECTION	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=ok multi=0 inert=1 fenced=0 recomputed=79 rev=5763e788b192 base=5763e788b192
F4-FENCE	v2-r53	a46012e6e95e	a46012e6e95e	1	CORRECTION-IN-FENCE	SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 recomputed=79 rev=a46012e6e95e base=a46012e6e95e
F5-REWRITE	v2-r53	40ad0babb9bf	1faf3a9db85b	1	DELETED-LINES	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 recomputed=79 rev=40ad0babb9bf base=1faf3a9db85b
F6-RECORD-DRIFT	v2-r53	175774b784d5	937465ca4bf2	1	RECORD-SHA-MISMATCH	SUMMARY sites=2 mismatches=0 filed=0 unfiled=0 record_sha=MISMATCH appended=DELETED multi=0 inert=0 fenced=0 recomputed=80 rev=175774b784d5 base=937465ca4bf2
fixture	counter	rev	base	exit	finding	SUMMARY
FH-HONEST	v2-r53	dcae43ee62e7	-	0	-	SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=dcae43ee62e7
FA1-UNSORTED	v2-r53	6ce84fc66743	-	1	ROWS-UNSORTED	SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=FAIL rev=6ce84fc66743
FA2-COMMENT	v2-r53	637986fecd7f	-	1	COMMENT-AMBIGUOUS-NAME	SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=637986fecd7f
FA3-TAMPER	v2-r53	815dc306538d	-	1	CAPTURE-RECEIPT-MISMATCH	SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=FAIL sorted=ok rev=815dc306538d
```

`r53-verdict-diff.txt` — the rebuilt files against the committed
`census/round-53/records/{c1,c2}-matrix-{v1,v2}.tsv`, comparing fixture/counter/exit/finding and
the SUMMARY string with only `rev=`/`base=` masked:

```
# r53 v1-arm rows: committed c1-matrix-v1.tsv / c2-matrix-v1.tsv vs rebuilt (rev masked)
== c1 v1
MATCH(non-rev)
== c2 v1
MATCH(non-rev)
# r53 v2-arm rows: committed vs rebuilt (rev masked)
== c1 v2
MATCH(non-rev)
== c2 v2
MATCH(non-rev)
EXIT=0
```

**Note 2 (fixture-rev reproducibility).** The r53 builder (`d5ce557e…`) contains no
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` pin (checked by grep), so each rebuild yields different
commit ids; the committed r53 matrices' `rev`/`base` cells are therefore build-specific. All 20
rows (10 in the v2 arms the assignment names, plus the 10 v1-arm rows the same driver emits)
match the committed matrices on every verdict field. The r55 builder pins dates; that is a later
round's property, not an r53 regression.

Supplemental real-lane arm (`r53-reallane-c1.txt`, `r53-reallane-c2.txt`, using the argv of the
committed `census/round-53/records/c1-tip.txt` and the r53 capture/receipt):

```
# r53 c1-counter (v2) real lane @ tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, base 9bf9234ae4d11c7b31706354302a9e95ad0d1f81
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 recomputed=79 rev=3ce0ba036275 base=9bf9234ae4d1
EXIT=0
# r53 c2-counter (v2) real lane @ tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, r53 capture+receipt
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok rev=3ce0ba036275
EXIT=0
```

## 3. r52 counters at the tip (clone)

`r52-c1.txt`:

```
# r52 c1-counter @ tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, root=/fast/scratch/hyaku/souji-r55/S55executor03/clone
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record=census/round-51/records/ws-drift-vs-r46.tsv recomputed=79 rev=3ce0ba036275
EXIT=0
```

`r52-c2.txt`:

```
# r52 c2-counter @ tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, root=/fast/scratch/hyaku/souji-r55/S55executor03/clone
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok rev=3ce0ba036275
EXIT=0
```

Facts: r52 c2's capture path is compiled in (`census/round-52/records/fleet-root-census.tsv`);
its CLI is `--root --rev [--scratch]` only. The r52 capture bytes are untouched
(`history-immutability.txt`: last commit `8ec412c6`, round-52 landing), and the r52 run receipt
is a v0 receipt with no `CAPTURE_SHA256` key by design (it echoes the capture's `TOOL_SHA256`
header) — so the binding evidence for r52 is the counter's own `receipt=ok` plus the counter's
`tool_sha=ok` recompute from the committed tool bytes at the tip.

## 4. r54 v3 counters on the real lane at the tip

`r54-c1.txt` (same argv as the v4 leg, `--base` = the r54 base `fe12daad…`):

```
# r54 c1-counter (v3) @ tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, base fe12daad2549f534650d406ebdbac9113d59313f
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=3ce0ba036275 base=fe12daad2549
EXIT=0
```

`r54-c2.txt` (r54 capture + r54 receipt, tool pin `e7e79952…`):

```
# r54 c2-counter (v3) @ tip 3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f, r54 capture+receipt, tool pin e7e79952
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=3ce0ba036275
EXIT=0
```

Both SUMMARY lines are byte-identical to the committed r54 receipts
(`census/round-54/records/c1-tip.txt`, `c2-tip.txt`) once only `rev=`/`base=` are masked
(`diff` exit 0 for both). The r54 capture is untouched (`0c3f42e0…`, binding-ok, last commit
`bfdbb336`), so the v3 real-lane green survives the r55 tip.

## 5. Census before-receipt verify

`census-verify.txt`:

```
# census receipt verify (round-55 before receipt)
VERIFY ok receipt=census/round-55/records/census-before-receipt.txt lane=souji conf_rc=0 dir_rc=0 w04=61 result=ok checks=grammar,digest,raw-section,rc,w04,result,adapter-sha,fleet-script-sha adapter=ok
EXIT=0
```

Command (exactly as assigned): `python3 -B tools/souji-census-receipt.py verify --receipt
census/round-55/records/census-before-receipt.txt --fleet-root /home/vgpnk/Projects/shokunin`.
All eight checks pass, including the fleet-script and adapter digest checks, so the receipt's
embedded raw census output still re-derives its header against the current fleet script bytes.

## 6. Pin and capture-binding audit (supplemental)

`pins-and-captures.txt` (excerpt — full file in this directory):

```
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62  census/round-55/fixtures/build-fixtures.py
ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315  census/round-55/fixtures/run-matrix.sh
ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e  census/round-55/records/c1-selftest-expected.tsv
63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc  census/round-55/records/c2-selftest-expected.tsv
922112361cdd257451e2f62820815ce19493c7d94d06c73c1b40f5dc9756f904  capture-sha  receipt-sha=922112361cdd257451e2f62820815ce19493c7d94d06c73c1b40f5dc9756f904  BINDING-OK  census/round-53/records/fleet-root-census.tsv
0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9  capture-sha  receipt-sha=0c3f42e000e00fd8165e99aee5d42908ccd63cdc3d7461ca840fb1f22f09e1f9  BINDING-OK  census/round-54/records/fleet-root-census.tsv
088aaa2644eeae1044dfdd5fa272fafe54fee473f31cae11b0543d23e6f73d40  capture-sha  receipt-sha=088aaa2644eeae1044dfdd5fa272fafe54fee473f31cae11b0543d23e6f73d40  BINDING-OK  census/round-55/records/fleet-root-census.tsv
```

All six round-55 pins equal the preregistration exactly. The three RECEIPT_VERSION=1 captures
(r53/r54/r55) hash to the `CAPTURE_SHA256` their run receipts bind.

`history-immutability.txt` shows the standing instruments and captures were last touched by
their own round's commit (r52 counters `df7d1300`; r53 counters `61838b54`; r52 capture
`8ec412c6`; r53 capture `1a53bcab`; r54 capture and receipt `bfdbb336`; r46 counter last touched
`3144c16b`, round-46), so "unchanged at the r55 tip" is true of the bytes, not just of the
verdicts.

## Red lines / dead ends

- One non-green invocation, my procedure, recovered: `run-matrix.sh` was first called with the
  fixture dir (`$S/selftest`) as its first argument; the frozen script expects the scratch root
  and looks for `<arg>/selftest/fixture-manifest.tsv`, so it exited 2 with
  `manifest missing: …/selftest/selftest/fixture-manifest.tsv` (`r53-matrix-arg-probe.txt`).
  Re-run with the scratch root: all four arms rc=0 (`r53-matrix.txt`).
- No assigned or supplemental check is red. No counter defect surfaced in any of these probes.

## Risks / blockers

- No blockers.
- The assignment's landing-suite pin `4b10ddd1` is two commits behind the dispatch tip; the r46
  SUMMARY is identical at both (assertions=580, mismatches=76, registered=76, unfiled=0), so the
  landing verdict is span-invariant over those commits.
- The lane worktree was dirty with sibling in-flight edits during the probe (`SKILL.md`,
  `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/knowledge/splitlines-line-model.md`, and
  `corpus/lessons/round-55.md` at the last read). Every counter here reads committed bytes via
  `git show`, so the receipts are unaffected; I wrote nothing into the worktree.
- The v4 C1/C2 claim legs are other seats' assignment; this seat did not re-derive them.

## Scratch disposition

`/fast/scratch/hyaku/souji-r55/S55executor03/` deleted before yield. Receipts, the rebuilt r53
matrices and the fixture manifest were copied into this seat directory first.
