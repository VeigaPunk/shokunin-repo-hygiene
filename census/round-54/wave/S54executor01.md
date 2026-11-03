# S54executor01 — independent reproduction of the r54 C1 v3 matrix

Role: executor (leaf, no dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Scratch (deleted at yield): `/fast/scratch/hyaku/souji-r54/S54executor01/`.
Seat dir: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-54/w1/S54executor01/`.

## 0. Context and instrument pins (measured this seat)

Lane HEAD at run start: `bfdbb336329e6afba3ab1ca83cbd6d9759271062` (the round-54 fresh capture commit).
Prereg freeze commit `3c394cab0cd406bbab72b8d365e0f3deed4ef98a` read first; claims frozen there.

```
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
a7928d05df794f14d5d0213ddb78d042f62819b52f5c49b3c838a1b96da1ed15  census/round-53/c1-counter.py   (v2 arm control)
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
f9d277636d6642de7b287678a145e8916f84f0c9cba00f4768aa16feaca80799  census/round-54/fixtures/run-matrix.sh
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv
```
All four prereg-pinned shas match the bytes on disk (`receipts/instrument-pins.txt`).

## 1. Fixture build (pass 1)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-54/fixtures/build-fixtures.py \
    --work /fast/scratch/hyaku/souji-r54/S54executor01/selftest \
    --manifest /fast/scratch/hyaku/souji-r54/S54executor01/fixture-manifest.tsv
BUILT F1-HONEST-TIP tip=55b56e65f805f850dc6e2d966b3f3131da33697b
BUILT F2-MULTI-ANNOT tip=16de1aecb46651f341f4bcbb9a40582ed33f295c
BUILT F3-INERT tip=1d0104152f26526820dc5fd8ce4e0a933c1c9d26
BUILT F4-FENCE tip=9763f1368ac757b535adc1e692556305fdd3f6a7
BUILT F5-REWRITE tip=569a115185052a76e9ed1cf06eb9099a2a40e4c2
BUILT F6-RECORD-DRIFT tip=0c991a5c51cbe809d88545d22b8357f90dabb8a4
BUILT F7-TILDE-FENCE tip=2daa874557c208faf054b29b53a8c0bb8a1d4653
BUILT F8-BT4-PARITY tip=5a0fafb73fe68974c115d5cc624bddb212ab8de8
BUILT F9-HTML-COMMENT tip=fafd3a2e582febb79abb78b4eff467ebc1bf099c
BUILT F10-STRADDLE tip=aa36dab9c2ca05d2c77d55404e6b6c5b81a17f4a
BUILT F11-BOGUS-RECOMP tip=7325d506da78400f9ff1ba850fd8a100c7a0c267
BUILT F12-LOG-UNFILED tip=ea328890f5c1142ddb0f2910fe1748caa0300a9d
BUILT F12b-LOG-FILED tip=2f6ce4b930a038b0c1ab7ddbf2d67355bdc97ead
BUILT FH-HONEST tip=81c9f21461bf315dcbd062ee47c30ee94d4f7a27
BUILT FH2-SYMLINK-HONEST tip=6815d46eee0f29c663fdaaf6c55b14ab934db13e
BUILT FA1-UNSORTED tip=0a1de12e2395e120ba8190b503f69042aff8c222
BUILT FA2-COMMENT tip=8b035bcf681f0f98dd3eee55639e6e55cd4541f7
BUILT FA3-TAMPER tip=9be703f0c77cccb1c4841a2c06c0f79ae31d44c5
BUILT FA4-SPACE-NAME tip=e0aabc60013d3b7b435a55db03b191937989b916
BUILT FA5-EXTRA-KEY tip=2a6fdc6df02bd026e67adc267f17ddeeb8a5d8ac
BUILT FA6-CRLF tip=17c582af6c10aa2815b7524253e698ca12fbb375
BUILT FA7-RECEIPT-ENTRIES tip=4fe9b56993d97ce6f3a2027f458ab9d45737748b
BUILT FA8-SYMLINK-CLASS tip=e5900e5c500019ffdc022b616c278ef62a99f093
MANIFEST /fast/scratch/hyaku/souji-r54/S54executor01/fixture-manifest.tsv
RC=0
```

Manifest (23 rows: 13 C1 + 10 C2), copied to `receipts/fixture-manifest.tsv`:

```
name	kind	dir	base	tip	record_sha256
F1-HONEST-TIP	C1	.../selftest/F1-HONEST-TIP	fdec0d33c95c279d222a8017c04f798f4d456d61	55b56e65f805f850dc6e2d966b3f3131da33697b	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F2-MULTI-ANNOT	C1	.../selftest/F2-MULTI-ANNOT	31d5cbd4babee3190be7f94c3f07cb58b6e4a63e	16de1aecb46651f341f4bcbb9a40582ed33f295c	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F3-INERT	C1	.../selftest/F3-INERT	d5fae7bf07b8ac6462433f1ce574d54795af5ea9	1d0104152f26526820dc5fd8ce4e0a933c1c9d26	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F4-FENCE	C1	.../selftest/F4-FENCE	1a707bf696584e1c05c29f73c05511d768a725af	9763f1368ac757b535adc1e692556305fdd3f6a7	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F5-REWRITE	C1	.../selftest/F5-REWRITE	e869d6ab4fa22e2798be8f1e9d19901916574fe5	569a115185052a76e9ed1cf06eb9099a2a40e4c2	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F6-RECORD-DRIFT	C1	.../selftest/F6-RECORD-DRIFT	37aff1008a33a26f10125e6ee585b0de8851db5e	0c991a5c51cbe809d88545d22b8357f90dabb8a4	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F7-TILDE-FENCE	C1	.../selftest/F7-TILDE-FENCE	3baee85055dfd1e719eb2ce7b2f2b16d9105e1ba	2daa874557c208faf054b29b53a8c0bb8a1d4653	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F8-BT4-PARITY	C1	.../selftest/F8-BT4-PARITY	c17a5679604495dbf1740ec51a52b4fdf065a257	5a0fafb73fe68974c115d5cc624bddb212ab8de8	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F9-HTML-COMMENT	C1	.../selftest/F9-HTML-COMMENT	7e6f30ddb2b0ac49a8a8f0188251a0995503a981	fafd3a2e582febb79abb78b4eff467ebc1bf099c	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F10-STRADDLE	C1	.../selftest/F10-STRADDLE	9565776b0fde6e6017143f574a8426fde1413bcb	aa36dab9c2ca05d2c77d55404e6b6c5b81a17f4a	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F11-BOGUS-RECOMP	C1	.../selftest/F11-BOGUS-RECOMP	6007cff675cceabb9e0264b768260db27090a853	7325d506da78400f9ff1ba850fd8a100c7a0c267	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F12-LOG-UNFILED	C1	.../selftest/F12-LOG-UNFILED	5978ec6e7164d109c4177e5389c02c25d35d7ce7	ea328890f5c1142ddb0f2910fe1748caa0300a9d	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
F12b-LOG-FILED	C1	.../selftest/F12b-LOG-FILED	af893285b1f1a8256e92812233f2e09640eeb04f	2f6ce4b930a038b0c1ab7ddbf2d67355bdc97ead	d55ffd7f99ad4c0aaabc1ea4c7fc40e7aabf7e702aa2b9f79c2a8b419f98edbf
FH-HONEST	C2	.../selftest/FH-HONEST	81c9f21461bf315dcbd062ee47c30ee94d4f7a27	81c9f21461bf315dcbd062ee47c30ee94d4f7a27	-
FH2-SYMLINK-HONEST	C2	.../selftest/FH2-SYMLINK-HONEST	6815d46eee0f29c663fdaaf6c55b14ab934db13e	6815d46eee0f29c663fdaaf6c55b14ab934db13e	-
FA1-UNSORTED	C2	.../selftest/FA1-UNSORTED	0a1de12e2395e120ba8190b503f69042aff8c222	0a1de12e2395e120ba8190b503f69042aff8c222	-
FA2-COMMENT	C2	.../selftest/FA2-COMMENT	8b035bcf681f0f98dd3eee55639e6e55cd4541f7	8b035bcf681f0f98dd3eee55639e6e55cd4541f7	-
FA3-TAMPER	C2	.../selftest/FA3-TAMPER	9be703f0c77cccb1c4841a2c06c0f79ae31d44c5	9be703f0c77cccb1c4841a2c06c0f79ae31d44c5	-
FA4-SPACE-NAME	C2	.../selftest/FA4-SPACE-NAME	e0aabc60013d3b7b435a55db03b191937989b916	e0aabc60013d3b7b435a55db03b191937989b916	-
FA5-EXTRA-KEY	C2	.../selftest/FA5-EXTRA-KEY	2a6fdc6df02bd026e67adc267f17ddeeb8a5d8ac	2a6fdc6df02bd026e67adc267f17ddeeb8a5d8ac	-
FA6-CRLF	C2	.../selftest/FA6-CRLF	17c582af6c10aa2815b7524253e698ca12fbb375	17c582af6c10aa2815b7524253e698ca12fbb375	-
FA7-RECEIPT-ENTRIES	C2	.../selftest/FA7-RECEIPT-ENTRIES	4fe9b56993d97ce6f3a2027f458ab9d45737748b	4fe9b56993d97ce6f3a2027f458ab9d45737748b	-
FA8-SYMLINK-CLASS	C2	.../selftest/FA8-SYMLINK-CLASS	e5900e5c500019ffdc022b616c278ef62a99f093	e5900e5c500019ffdc022b616c278ef62a99f093	-
```
(`...` = `/fast/scratch/hyaku/souji-r54/S54executor01`; full literal rows in `receipts/fixture-manifest.tsv`.)

## 2. Determinism (r53 R10 closure): second build into a fresh dir, compare base/tip

```
$ mkdir -p $S/selftest2 && python3 -B census/round-54/fixtures/build-fixtures.py --work $S/selftest2 --manifest $S/fixture-manifest-2.tsv
RC2=0
$ cut -f1,4,5 $S/fixture-manifest.tsv > $S/m1.bt; cut -f1,4,5 $S/fixture-manifest-2.tsv > $S/m2.bt; diff $S/m1.bt $S/m2.bt; echo "DIFF_RC=$?"
DIFF_RC=0            # empty diff
$ diff $S/m1.bt <(cut -f1,4,5 census/round-54/records/fixture-manifest.tsv) && echo IDENTICAL
IDENTICAL (empty diff)
```
23/23 base/tip pairs reproduce exactly across two independent builds, and my build's revs equal the L1's committed manifest revs (`census/round-54/records/fixture-manifest.tsv`) column-for-column. No differing rev.

## 3. C1 v3 arm — every fixture row, exactly as `run-matrix.sh`'s `c1_arm`

Rule applied: `--rev <tip>`, `--base <base for F5-REWRITE/F6-RECORD-DRIFT, else tip>`,
`--record-sha256 <manifest record_sha256>`, `--sources-rev-before <tip> --sources-rev-after <tip>`, `--scratch <seat scratch>`.
Per-fixture full output: `receipts/per-fixture/<name>.txt`.

```
fixture	counter	rev	base	exit	finding	SUMMARY
F1-HONEST-TIP	v3-r54	55b56e65f805	55b56e65f805	0	-	SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=55b56e65f805 base=55b56e65f805
F2-MULTI-ANNOT	v3-r54	16de1aecb466	16de1aecb466	1	MULTIPLE-ANNOTATIONS	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=ok multi=1 inert=1 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=16de1aecb466 base=16de1aecb466
F3-INERT	v3-r54	1d0104152f26	1d0104152f26	1	INERT-CORRECTION	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=ok multi=0 inert=1 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=1d0104152f26 base=1d0104152f26
F4-FENCE	v3-r54	9763f1368ac7	9763f1368ac7	1	CORRECTION-IN-FENCE	SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=9763f1368ac7 base=9763f1368ac7
F5-REWRITE	v3-r54	569a11518505	e869d6ab4fa2	1	DELETED-LINES	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=569a11518505 base=e869d6ab4fa2
F6-RECORD-DRIFT	v3-r54	0c991a5c51cb	37aff1008a33	1	RECORD-SHA-MISMATCH	SUMMARY sites=2 mismatches=0 filed=0 unfiled=0 record_sha=MISMATCH appended=DELETED multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=80 rev=0c991a5c51cb base=37aff1008a33
F7-TILDE-FENCE	v3-r54	2daa874557c2	2daa874557c2	1	CORRECTION-IN-FENCE	SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=2daa874557c2 base=2daa874557c2
F8-BT4-PARITY	v3-r54	5a0fafb73fe6	5a0fafb73fe6	1	CORRECTION-IN-FENCE	SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=5a0fafb73fe6 base=5a0fafb73fe6
F9-HTML-COMMENT	v3-r54	fafd3a2e582f	fafd3a2e582f	1	CORRECTION-IN-FENCE	SUMMARY sites=2 mismatches=2 filed=0 unfiled=2 record_sha=ok appended=ok multi=0 inert=0 fenced=2 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=fafd3a2e582f base=fafd3a2e582f
F10-STRADDLE	v3-r54	aa36dab9c2ca	aa36dab9c2ca	1	ZONE-TOKEN-STRADDLES-EDGE	SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=1 fenced=0 straddle=1 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=aa36dab9c2ca base=aa36dab9c2ca
F11-BOGUS-RECOMP	v3-r54	7325d506da78	7325d506da78	1	BOGUS-RECOMPUTED	SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=1 logunfiled=0 logrecomp=0 recomputed=79 rev=7325d506da78 base=7325d506da78
F12-LOG-UNFILED	v3-r54	ea328890f5c1	ea328890f5c1	1	UNFILED-SOURCES-ANNOTATION	SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 recomputed=79 rev=ea328890f5c1 base=ea328890f5c1
F12b-LOG-FILED	v3-r54	2f6ce4b930a0	2f6ce4b930a0	0	-	SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=2f6ce4b930a0 base=2f6ce4b930a0
```

## 4. Cell-by-cell comparison against `records/c1-selftest-expected.tsv`

```
fixture	expected_exit	expected_finding	observed_exit	observed_finding	verdict
F1-HONEST-TIP	0	-	0	-	AGREE
F2-MULTI-ANNOT	1	MULTIPLE-ANNOTATIONS	1	MULTIPLE-ANNOTATIONS	AGREE
F3-INERT	1	INERT-CORRECTION	1	INERT-CORRECTION	AGREE
F4-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	AGREE
F5-REWRITE	1	DELETED-LINES	1	DELETED-LINES	AGREE
F6-RECORD-DRIFT	1	RECORD-SHA-MISMATCH	1	RECORD-SHA-MISMATCH	AGREE
F7-TILDE-FENCE	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	AGREE
F8-BT4-PARITY	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	AGREE
F9-HTML-COMMENT	1	CORRECTION-IN-FENCE	1	CORRECTION-IN-FENCE	AGREE
F10-STRADDLE	1	ZONE-TOKEN-STRADDLES-EDGE	1	ZONE-TOKEN-STRADDLES-EDGE	AGREE
F11-BOGUS-RECOMP	1	BOGUS-RECOMPUTED	1	BOGUS-RECOMPUTED	AGREE
F12-LOG-UNFILED	1	UNFILED-SOURCES-ANNOTATION	1	UNFILED-SOURCES-ANNOTATION	AGREE
F12b-LOG-FILED	0	-	0	-	AGREE
AGREE_COUNT=13/13
```
This table is identical, clause for clause, to my independent run written to `receipts/agree.tsv`.
It is also identical to the L1's `census/round-54/records/c1-matrix-v3.tsv`:

```
$ diff receipts/c1-v3.tsv census/round-54/records/c1-matrix-v3.tsv && echo BYTE-IDENTICAL-TO-L1-MATRIX
BYTE-IDENTICAL-TO-L1-MATRIX
```

## 5. Real-lane run at the capture commit (claim receipt)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-54/c1-counter.py \
    --root . --rev bfdbb336329e6afba3ab1ca83cbd6d9759271062 \
    --base fe12daad2549f534650d406ebdbac9113d59313f \
    --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 \
    --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 \
    --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549
RC=0
```
`diff` against the body of the committed receipt `census/round-54/records/c1-tip.txt`
(its `#` header lines and `EXIT=` trailer stripped): **IDENTICAL**.
`receipts/real-lane.out` holds the bytes.

## 6. v2-arm acceptance control (before-state; prereg kill clause "v3 killing a new attack")

Same fixtures, frozen `census/round-53/c1-counter.py`, per-fixture output in `receipts/per-fixture-v2/`:

```
F7-TILDE-FENCE     exit 0  (no finding)   -> v2 accepted the tilde-fence hidden filing
F8-BT4-PARITY      exit 0  (no finding)   -> v2 accepted the 4-backtick parity mis-parse
F9-HTML-COMMENT    exit 0  (no finding)   -> v2 accepted the HTML-comment hidden filing
F10-STRADDLE       exit 0  (no finding)   -> v2 ignored the zone-edge straddle
F11-BOGUS-RECOMP   exit 0  (no finding)   -> v2 exited 0 with mismatches=1 filed=1 unfiled=0
F12-LOG-UNFILED    exit 0  (no finding)   -> v2 never read LOG.md/README.md pairs
F12b-LOG-FILED     exit 0  (no finding)   -> stays green in both arms
```
Full 13-row v2 matrix: `receipts/c1-v2.tsv` (F1-F6 carry over unchanged from v3: same exits and
same first findings, so no carry-over regression appears).
Non-vacuity holds: v3 kills F7-F12; v2 accepts all six; F12b is green in both.

## 7. Verdict

**AGREE — 13/13 C1 cells.** No DISAGREE row. The v3 counter reproduces the frozen expected matrix
byte-for-byte on independently rebuilt fixtures; the builder reproduces every base/tip rev; the
real-lane run at `bfdbb336` exits 0 with `unfiled=0 … straddle=0 bogus=0 logunfiled=0 logrecomp=0`
and matches the committed receipt body exactly.

Classified defects: none found (no counter defect, no fixture-builder defect, no procedure defect).
No counter edit, no fixture edit, no lane file touched; no tool installed (nothing was needed).

Boundary observations recorded for the L1 as evidence, not as limits:
1. F4/F7/F8/F9 each emit **two** `CORRECTION-IN-FENCE` findings and also drive `unfiled=2`
   (`filed=0`), i.e. the refusal is doubly carried (fence finding + unfiled mismatch counter). The
   expected TSV names only the first finding; that matches.
2. F10 emits `ZONE-TOKEN-STRADDLES-EDGE` first and then `INERT-CORRECTION` for the same correction
   line, with `straddle=1 inert=1`; first-finding comparison is stable.
3. F11's SCORECARD site line reads `status=match filed=no`; the sole refusal is `BOGUS-RECOMPUTED`
   (`recomputed=83` vs record count 79) — exactly the misread class the claim names.
4. F12's `UNFILED-SOURCES-ANNOTATION` fires at `LOG.md:2` ("claims 274 -> 275 rows but the registry
   holds 3") because the fixture registry carries 3 rows; the message shape is the real-lane class.

## 8. Receipts (seat dir)

- `receipts/fixture-manifest.tsv`, `receipts/fixture-manifest-2.tsv` — two independent builds (23 rows each)
- `receipts/determinism.txt` — diff results (both empty)
- `receipts/c1-v3.tsv` — 13 v3 rows; `receipts/c1-v2.tsv` — 13 v2 control rows
- `receipts/agree.tsv` — per-fixture AGREE/DISAGREE table (`AGREE_COUNT=13/13`)
- `receipts/real-lane.out` — real-lane stdout, rc=0
- `receipts/per-fixture/*.txt` — full output + EXIT per v3 fixture
- `receipts/per-fixture-v2/*.txt` — full output + EXIT per v2 attack fixture
- `receipts/instrument-pins.txt` — sha256 of counter/builder/run-matrix/expected
