# S56executor01 — round 56, w1 — C1 reproduction (executor)

Seat: S56executor01 (executor, leaf)
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Measured revision for every claim: cce21b555a617cadda782613ec1e9d3a0c12ac83 (base fafe371694fea41c5d23f63083865d5ccf3f1d36)
Scratch: /fast/scratch/hyaku/souji-r56/S56executor01/ (deleted before yield; receipts copied here)
Receipts: ./receipts/ (each ends with an `EXIT=` line)

VERDICT: AGREE

All four assigned steps reproduce: the pinned selftest passes 33 cases, the wrong-pin guard refuses by name with exit 2, the official matrix reproduces all four TSVs byte for byte against both the committed records and the pre-freeze dry-run copies, the independent TSV-only derivation of T1–T5 passes on all predicates, and the real-lane v5 run is byte-identical to the committed `census/round-56/records/c1-tip.txt` including its `EXIT=0` line.

## Pin verification (before probing)

Working tree bytes and committed bytes at the measured revision both equal the frozen pins (sha256):

```
975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179  census/round-56/c1-counter.py
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8  census/round-56/c2-counter.py
2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a  census/round-56/fixtures/build-fixtures.py
a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3  census/round-56/fixtures/run-matrix.sh
48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb  census/round-56/records/c1-selftest-expected.tsv
90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3  census/round-56/records/c2-selftest-expected.tsv
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
```

Repeated via `git show cce21b55:<path> | sha256sum` for all eight paths: identical values. No pin mismatch, so the probe proceeded.

Disk before the heavy pass (`bash /home/vgpnk/Projects/shokunin/scripts/hyaku/disk-guard.sh status`): `/fast/scratch/hyaku` 50% used, 405.5G free; `/tmp` 25%, 95.9G free. No ENOSPC.

## Step 1 — pinned selftest: AGREE

Command (lane root as cwd):

```
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor01/ python3 -B census/round-56/c1-counter.py \
  --selftest --work /fast/scratch/hyaku/souji-r56/S56executor01/st \
  --builder-sha256 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a \
  --expected-sha256 48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb
```

Output (receipt `receipts/receipt-step1-selftest.txt`, 35 lines):

```
SELFTEST-CASE F1-HONEST-TIP pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F2-MULTI-ANNOT pass rc=1 want_rc=1 finding=MULTIPLE-ANNOTATIONS want_finding=MULTIPLE-ANNOTATIONS
SELFTEST-CASE F3-INERT pass rc=1 want_rc=1 finding=INERT-CORRECTION want_finding=INERT-CORRECTION
SELFTEST-CASE F4-FENCE pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F5-REWRITE pass rc=1 want_rc=1 finding=DELETED-LINES want_finding=DELETED-LINES
SELFTEST-CASE F6-RECORD-DRIFT pass rc=1 want_rc=1 finding=RECORD-SHA-MISMATCH want_finding=RECORD-SHA-MISMATCH
SELFTEST-CASE F7-TILDE-FENCE pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F8-BT4-PARITY pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F9-HTML-COMMENT pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F10-STRADDLE pass rc=1 want_rc=1 finding=ZONE-TOKEN-STRADDLES-EDGE want_finding=ZONE-TOKEN-STRADDLES-EDGE
SELFTEST-CASE F11-BOGUS-RECOMP pass rc=1 want_rc=1 finding=BOGUS-RECOMPUTED want_finding=BOGUS-RECOMPUTED
SELFTEST-CASE F12-LOG-UNFILED pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F12b-LOG-FILED pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F7-FF pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F12c-LOG-POINTER-EXEMPT pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F8b-BT4-SHORT-RUN pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F13-DUAL-ANCHOR pass rc=1 want_rc=1 finding=ANCHOR-ALIAS-MISMATCH want_finding=ANCHOR-ALIAS-MISMATCH
SELFTEST-CASE F14-PAIR-STALE-FILING pass rc=1 want_rc=1 finding=PAIR-FILING-INERT want_finding=PAIR-FILING-INERT
SELFTEST-CASE F15-PAIR-NOROWS pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F16-PAIR-ARROW pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F17-INDENT4-FENCE pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F18-BTINFO-FENCE pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F19-PAIR-IN-FENCE pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F20-R1-INDENT-SWALLOW pass rc=1 want_rc=1 finding=BOGUS-RECOMPUTED want_finding=BOGUS-RECOMPUTED
SELFTEST-CASE F21-R1-ONELINE-SWALLOW pass rc=1 want_rc=1 finding=BOGUS-RECOMPUTED want_finding=BOGUS-RECOMPUTED
SELFTEST-CASE F22-PTR-TIMESTAMP pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F23-SOURCES-RECOMP pass rc=1 want_rc=1 finding=SOURCES-RECOMPUTE-MISMATCH want_finding=SOURCES-RECOMPUTE-MISMATCH
SELFTEST-CASE F7-FF2 pass rc=1 want_rc=1 finding=CORRECTION-IN-FENCE want_finding=CORRECTION-IN-FENCE
SELFTEST-CASE F24-PAIR-HIDDEN-FILING pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F26-INDENT4-COMMENT-OPENER pass rc=1 want_rc=1 finding=UNFILED-SOURCES-ANNOTATION want_finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F27-BINARY-NUMSTAT pass rc=1 want_rc=1 finding=DELETIONS-UNREADABLE-BINARY want_finding=DELETIONS-UNREADABLE-BINARY
SELFTEST-CASE F28-NUL-CORRECTION-UNCHANGED pass rc=1 want_rc=1 finding=CORRECTION-FILE-BINARY want_finding=CORRECTION-FILE-BINARY
SELFTEST-CASE F29-PROSE-COMMENT-MENTION pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST pass cases=33
EXIT=0
```

`SELFTEST pass cases=33`, EXIT=0, and this receipt is byte-identical (`cmp`) to the committed `census/round-56/records/c1-selftest.txt` at 148f39a6 (`git show …:census/round-56/records/c1-selftest.txt | sha256sum` = `5d2f64f3f31e62cb06e8ff870580b148121b38f4b5052045ee20130072ea95aa`; no diff).

Wrong-builder pin (0*64 in place of the builder sha256):

```
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor01/ python3 -B census/round-56/c1-counter.py \
  --selftest --work /fast/scratch/hyaku/souji-r56/S56executor01/st-wrongpin \
  --builder-sha256 0000000000000000000000000000000000000000000000000000000000000000 \
  --expected-sha256 48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb
```

Output (receipt `receipts/receipt-step1b-wrongpin.txt`):

```
CANNOT-EVALUATE PIN-MISMATCH builder sha256 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a != pinned 0000000000000000000000000000000000000000000000000000000000000000
EXIT=2
```

`CANNOT-EVALUATE PIN-MISMATCH`, exit 2, and no SELFTEST-CASE line was emitted — the pin check runs before any fixture is exec'd, as the prereg's T6 states.

## Step 2 — official matrix: AGREE (byte-identical)

Build:

```
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor01/ python3 -B census/round-56/fixtures/build-fixtures.py \
  --work /fast/scratch/hyaku/souji-r56/S56executor01/selftest
```

→ `BUILT` for 49 fixtures (33 C1 + 16 C2), `MANIFEST …/fixture-manifest.tsv`, EXIT=0 (receipt `receipts/receipt-step2-build.txt`).

Matrix (outdir = scratch, so the driver's output lands in scratch, never the lane):

```
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/fixtures/run-matrix.sh \
  /fast/scratch/hyaku/souji-r56/S56executor01 /fast/scratch/hyaku/souji-r56/S56executor01
```

Output (receipt `receipts/receipt-step2-matrix.txt`):

```
c1-v4 rc=0
c1-v5 rc=0
c2-v4 rc=0
c2-v5 rc=0
EXIT=0
```

Byte comparison of my four TSVs against the committed records and against `records/matrix-dryrun/` (receipt `receipts/receipt-step2-bytecmp.txt`):

```
c1-matrix-v5.tsv sha256=3bfa8180d3711bfd1b150a144828937247f3ca5b1598f6e1f5efc007ef86d72e vs_committed=IDENTICAL vs_dryrun=IDENTICAL
c1-matrix-v4.tsv sha256=4b6fd50499ff86573538e3205f33ce1dab3aebf4d51ba310f92b42d7ba303bcc vs_committed=IDENTICAL vs_dryrun=IDENTICAL
c2-matrix-v5.tsv sha256=d8613afdeb0c18897cd453db405ececbf8d964750764b02053c1bbe62df128e6 vs_committed=IDENTICAL vs_dryrun=IDENTICAL
c2-matrix-v4.tsv sha256=d7bf3a720bca0f3196444dbf46167fb67b184dfb4614bdcfb773fcfeb5c90c48 vs_committed=IDENTICAL vs_dryrun=IDENTICAL
EXIT=0
```

No first differing line exists. The committed `c1-matrix-v5.tsv` blob at 148f39a6 is the same 3bfa8180… as the dry-run blob at the freeze revision cce21b55, so the post-freeze official matrix reproduces the pre-freeze dry-run for C1 (and the same holds for v4 and both C2 arms).

## Step 3 — independent T1–T5 derivation: AGREE (all PASS)

Method deliberately shares nothing with the counter: `receipts/derive-targets.py` parses only the two committed matrix TSVs (7 columns, joined on fixture name, 33 rows each) and asserts the T1–T5 predicates in plain Python. No counter code, no fixture builder, no summary parsing. Full output: `receipts/receipt-step3-derive.txt`; below the literal evidence.

### T1 — {v4 exit 0, v5 exit ≠0} = {F24, F26, F28} with the named first findings: PASS

```
T1 SET F24-PAIR-HIDDEN-FILING,F26-INDENT4-COMMENT-OPENER,F28-NUL-CORRECTION-UNCHANGED
T1 PASS want_set=F24-PAIR-HIDDEN-FILING,F26-INDENT4-COMMENT-OPENER,F28-NUL-CORRECTION-UNCHANGED got_set=F24-PAIR-HIDDEN-FILING,F26-INDENT4-COMMENT-OPENER,F28-NUL-CORRECTION-UNCHANGED
T1 PASS F24-PAIR-HIDDEN-FILING v4_exit=0 v5_exit=1 v5_finding=UNFILED-SOURCES-ANNOTATION want=UNFILED-SOURCES-ANNOTATION
T1 PASS F26-INDENT4-COMMENT-OPENER v4_exit=0 v5_exit=1 v5_finding=UNFILED-SOURCES-ANNOTATION want=UNFILED-SOURCES-ANNOTATION
T1 PASS F28-NUL-CORRECTION-UNCHANGED v4_exit=0 v5_exit=1 v5_finding=CORRECTION-FILE-BINARY want=CORRECTION-FILE-BINARY
T1 PASS F24 v5 SUMMARY flag pairhidden=1 present=True
T1 LITERAL_V5_F24 F24-PAIR-HIDDEN-FILING	v5-r56	3b7923f3af56	3b7923f3af56	1	UNFILED-SOURCES-ANNOTATION	SUMMARY … logunfiled=1 … pairhidden=1 recomputed=79 rev=3b7923f3af56 base=3b7923f3af56
T1 LITERAL_V5_F26 F26-INDENT4-COMMENT-OPENER	v5-r56	aed35e4cff78	aed35e4cff78	1	UNFILED-SOURCES-ANNOTATION	SUMMARY … logunfiled=1 … recomputed=79
T1 LITERAL_V5_F28 F28-NUL-CORRECTION-UNCHANGED	v5-r56	33f40a5c12fa	33f40a5c12fa	1	CORRECTION-FILE-BINARY	SUMMARY … recomputed=79
T1 LITERAL_V4_F24 F24-PAIR-HIDDEN-FILING	v4-r55	3b7923f3af56	3b7923f3af56	0	-	SUMMARY …
T1 LITERAL_V4_F26 F26-INDENT4-COMMENT-OPENER	v4-r55	aed35e4cff78	aed35e4cff78	0	-	SUMMARY …
T1 LITERAL_V4_F28 F28-NUL-CORRECTION-UNCHANGED	v4-r55	33f40a5c12fa	33f40a5c12fa	0	-	SUMMARY …
```

(`…` above is my elision of SUMMARY fields that the derivation also has verbatim in the receipt; all 7 TSV columns are present in the file.)

F24's parenthetical — "also prints PAIR-FILING-HIDDEN" — cannot be read from the matrix, which stores only the first `FINDING` line (the runner's §5.2 rule). Verified by running the v5 counter directly on the F24 fixture:

```
######## F24-PAIR-HIDDEN-FILING (rev=3b7923f3af56 base=3b7923f3af56) v5
FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 3 -> 4 rows but the registry holds 3; no pair-form filing names it
FINDING PAIR-FILING-HIDDEN LOG.md:2 matching filing sits in a hidden line (fence or comment); it does not file
SITE path=SCORECARD.md line=5 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=3 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=1 logrecomp=0 alias=0 pairinert=0 pairhidden=1 recomputed=79 rev=3b7923f3af56 base=3b7923f3af56
EXIT=1
```

### T2 — F27: v5 exit 1, first finding DELETIONS-UNREADABLE-BINARY: PASS

```
T2 PASS F27-BINARY-NUMSTAT v5_exit=1 v5_finding=DELETIONS-UNREADABLE-BINARY want=1/DELETIONS-UNREADABLE-BINARY
T2 LITERAL_V5 F27-BINARY-NUMSTAT	v5-r56	16c08d97816b	e56028b65d02	1	DELETIONS-UNREADABLE-BINARY	SUMMARY … appended=DELETED … rev=16c08d97816b base=e56028b65d02
T2 LITERAL_V4 F27-BINARY-NUMSTAT	v4-r55	16c08d97816b	e56028b65d02	1	DELETED-LINES	SUMMARY … appended=DELETED …
```

The direct v5 run prints the name with its detail: `FINDING DELETIONS-UNREADABLE-BINARY LOG.md deletions unreadable (binary numstat entry) between e56028b65d02..16c08d97816b` (`receipts/step3-findings.out`). This is the claimed FINDING-NAME amendment only: v4 already exited 1 on the row, mislabelled `DELETED-LINES` (deletions read as −1).

### T3 — F7-FF2: v5 exit 1, first finding CORRECTION-IN-FENCE: PASS

```
T3 PASS F7-FF2 v5_exit=1 v5_finding=CORRECTION-IN-FENCE want=1/CORRECTION-IN-FENCE
T3 LITERAL_V5 F7-FF2	v5-r56	b4a1675bf10a	b4a1675bf10a	1	CORRECTION-IN-FENCE	SUMMARY … fenced=2 … rev=b4a1675bf10a base=b4a1675bf10a
```

Direct run shows two `FINDING CORRECTION-IN-FENCE` lines (SCORECARD.md:10 and :11 against the two sites), i.e. the form-feed shape enters the frozen set as ERRATUM-R55-1 intended, not as a new finding.

### T4 — {v4 exit ≠0, v5 exit 0} = {F29} only, honest over-hide states unchanged: PASS

```
T4 PASS want_set=F29-PROSE-COMMENT-MENTION got_set=F29-PROSE-COMMENT-MENTION
T4 LITERAL_V4 F29-PROSE-COMMENT-MENTION	v4-r55	bf0488f93345	bf0488f93345	1	CORRECTION-IN-FENCE	SUMMARY … unfiled=2 fenced=2 …
T4 LITERAL_V5 F29-PROSE-COMMENT-MENTION	v5-r56	bf0488f93345	bf0488f93345	0	-	SUMMARY … filed=2 unfiled=0 fenced=0 …
T4 PASS F17-INDENT4-FENCE v4_exit=0 v5_exit=0 (both 0)
T4 PASS F18-BTINFO-FENCE v4_exit=0 v5_exit=0 (both 0)
T4 PASS F19-PAIR-IN-FENCE v4_exit=0 v5_exit=0 (both 0)
```

The honest over-hide states F17/F18/F19 stay exit 0 under both counters, and F29's v5 SUMMARY carries `filed=2 unfiled=0 fenced=0`, i.e. the prose mention no longer opens a region to EOF.

### T5 — every other fixture identical exit and first finding: PASS (27 rows)

```
T5 ROWS n=27 F1-HONEST-TIP,F10-STRADDLE,F11-BOGUS-RECOMP,F12-LOG-UNFILED,F12b-LOG-FILED,F12c-LOG-POINTER-EXEMPT,F13-DUAL-ANCHOR,F14-PAIR-STALE-FILING,F15-PAIR-NOROWS,F16-PAIR-ARROW,F17-INDENT4-FENCE,F18-BTINFO-FENCE,F19-PAIR-IN-FENCE,F2-MULTI-ANNOT,F20-R1-INDENT-SWALLOW,F21-R1-ONELINE-SWALLOW,F22-PTR-TIMESTAMP,F23-SOURCES-RECOMP,F3-INERT,F4-FENCE,F5-REWRITE,F6-RECORD-DRIFT,F7-FF,F7-TILDE-FENCE,F8-BT4-PARITY,F8b-BT4-SHORT-RUN,F9-HTML-COMMENT
T5 PASS F1-HONEST-TIP v4=0/- v5=0/-
T5 PASS F10-STRADDLE v4=1/ZONE-TOKEN-STRADDLES-EDGE v5=1/ZONE-TOKEN-STRADDLES-EDGE
T5 PASS F11-BOGUS-RECOMP v4=1/BOGUS-RECOMPUTED v5=1/BOGUS-RECOMPUTED
T5 PASS F12-LOG-UNFILED v4=1/UNFILED-SOURCES-ANNOTATION v5=1/UNFILED-SOURCES-ANNOTATION
T5 PASS F12b-LOG-FILED v4=0/- v5=0/-
T5 PASS F12c-LOG-POINTER-EXEMPT v4=0/- v5=0/-
T5 PASS F13-DUAL-ANCHOR v4=1/ANCHOR-ALIAS-MISMATCH v5=1/ANCHOR-ALIAS-MISMATCH
T5 PASS F14-PAIR-STALE-FILING v4=1/PAIR-FILING-INERT v5=1/PAIR-FILING-INERT
T5 PASS F15-PAIR-NOROWS v4=1/UNFILED-SOURCES-ANNOTATION v5=1/UNFILED-SOURCES-ANNOTATION
T5 PASS F16-PAIR-ARROW v4=1/UNFILED-SOURCES-ANNOTATION v5=1/UNFILED-SOURCES-ANNOTATION
T5 PASS F17-INDENT4-FENCE v4=0/- v5=0/-
T5 PASS F18-BTINFO-FENCE v4=0/- v5=0/-
T5 PASS F19-PAIR-IN-FENCE v4=0/- v5=0/-
T5 PASS F2-MULTI-ANNOT v4=1/MULTIPLE-ANNOTATIONS v5=1/MULTIPLE-ANNOTATIONS
T5 PASS F20-R1-INDENT-SWALLOW v4=1/BOGUS-RECOMPUTED v5=1/BOGUS-RECOMPUTED
T5 PASS F21-R1-ONELINE-SWALLOW v4=1/BOGUS-RECOMPUTED v5=1/BOGUS-RECOMPUTED
T5 PASS F22-PTR-TIMESTAMP v4=1/UNFILED-SOURCES-ANNOTATION v5=1/UNFILED-SOURCES-ANNOTATION
T5 PASS F23-SOURCES-RECOMP v4=1/SOURCES-RECOMPUTE-MISMATCH v5=1/SOURCES-RECOMPUTE-MISMATCH
T5 PASS F3-INERT v4=1/INERT-CORRECTION v5=1/INERT-CORRECTION
T5 PASS F4-FENCE v4=1/CORRECTION-IN-FENCE v5=1/CORRECTION-IN-FENCE
T5 PASS F5-REWRITE v4=1/DELETED-LINES v5=1/DELETED-LINES
T5 PASS F6-RECORD-DRIFT v4=1/RECORD-SHA-MISMATCH v5=1/RECORD-SHA-MISMATCH
T5 PASS F7-FF v4=1/CORRECTION-IN-FENCE v5=1/CORRECTION-IN-FENCE
T5 PASS F7-TILDE-FENCE v4=1/CORRECTION-IN-FENCE v5=1/CORRECTION-IN-FENCE
T5 PASS F8-BT4-PARITY v4=1/CORRECTION-IN-FENCE v5=1/CORRECTION-IN-FENCE
T5 PASS F8b-BT4-SHORT-RUN v4=1/CORRECTION-IN-FENCE v5=1/CORRECTION-IN-FENCE
T5 PASS F9-HTML-COMMENT v4=1/CORRECTION-IN-FENCE v5=1/CORRECTION-IN-FENCE
T5 PASS complement_rows=27 want=27
T5 POPULATION rows_v4=33 rows_v5=33
OVERALL PASS
EXIT=0
```

Method note (my harness, not the claim): my first run of the derivation script asserted `complement_rows=29`, an arithmetic slip on my side (33 fixtures − the 6 rows covered by T1/T2/T3/T4 = 27). The prereg's own T5 enumeration (F1–F23 + F7-FF + F12b + F12c + F8b) is exactly the same 27 rows; every per-row check passed before and after the constant was corrected. No matrix byte and no counter byte was touched. Similarly, one intermediate step-4 receipt was captured from the wrong cwd (my `cd` leaked into the next brace), producing a Python "can't open file" exit 2; it was re-captured from the lane root and the failed attempt is disclosed here as a method slip, not a claim result.

## Step 4 — real lane, v5 counter: AGREE (byte-identical receipt)

Command (cwd = lane root):

```
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor01/ python3 -B census/round-56/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev cce21b555a617cadda782613ec1e9d3a0c12ac83 \
  --base fafe371694fea41c5d23f63083865d5ccf3f1d36 \
  --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 \
  --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 \
  --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 \
  --scratch /fast/scratch/hyaku/souji-r56/S56executor01
```

Output (receipt `receipts/receipt-step4-reallane.txt`):

```
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=cce21b555a61 base=fafe371694fe
EXIT=0
```

`cmp` against the committed receipt `census/round-56/records/c1-tip.txt`: byte-identical including the trailing `EXIT=0` (both sha256 `399112bfc330f433c150b1e527ecb96b75382d22fd6a57abe6824ed1e1605e10`). So the SUMMARY line and both SITE lines are byte-equal to the committed receipt (the assignment's "EXIT line excluded" condition is satisfied trivially). Every T7 field in the prereg is present with the prescribed value: `unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79`.

Independent cross-check of the SUMMARY's numeric claims from committed bytes, without the counter:

- `git show cce21b55:census/round-51/records/ws-drift-vs-r46.tsv | sha256sum` = `2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30` → `record_sha=ok`.
- Same blob, lines starting with `ADDED`: 79 → `recomputed=79`.
- `git show cce21b55:SCORECARD.md` line 1196 states `` `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` (78) `` → stated=78, mismatch, filed.
- `git show cce21b55:census/round-51/preregistration.txt` line 125 states the same `(78)` → second mismatch, filed.
- `git show cce21b55:SCORECARD.md` carries 0 NUL bytes → no CORRECTION-FILE-BINARY on the real lane.
- The two filings that make `filed=2` are visible lines of the correction file: `1243:R52-CORRECTION SCORECARD.md:1196 stale=78 recomputed=79` and `1245:R52-CORRECTION census/round-51/preregistration.txt:125 stale=78 recomputed=79`.

## Repository state observed (not mine; reported, not judged)

At the end of my run the lane HEAD is `148f39a6c902b27e997ac36d395735406d3ad9de` ("round-56: post-freeze receipts …"), with `cce21b55` confirmed an ancestor (`git merge-base --is-ancestor`), and the working tree carries two uncommitted changes: `SCORECARD.md` (+15-line round-56 measurements table, mtime 19:44:52) and `census/round-56/records/landing-suite-standing.txt` (rewritten at 19:47:00, during my run). Neither is mine: I wrote nothing to the lane repo outside this seat directory and my scratch; the claim reads used only `git show cce21b55:<path>` and the counter's own `--rev cce21b55` object reads. `census/round-56/records/{c1-matrix-v4,c1-matrix-v5,c2-matrix-v4,c2-matrix-v5}.tsv` at 148f39a6 equal the dry-run blobs at cce21b55 (sha256s above), and `c1-tip.txt` / `c1-selftest.txt` at 148f39a6 equal my reproduced receipts byte for byte.

Observation on the standing-check receipt (reported, not judged, not edited — it is outside my scope): `census/round-56/records/landing-suite-standing.txt` does not exist at the freeze revision; it was added at 148f39a6 with a harness argument error as its content (`usage: c1-counter.py [-h] --root ROOT --rev REV [--work WORK]` / `c1-counter.py: error: unrecognized arguments: --scratch /fast/scratch/hyaku/souji-r56/L1/off/c1` / `EXIT=2`). During my run another process replaced the working-tree copy with `COULD-NOT-EVALUATE dirty worktree at run time: 2 unexpected rows` / `EXIT=2` — consistent with the two modified rows above (this file plus the uncommitted SCORECARD.md). So at the time of writing the prereg's standing landing-suite check ("the standing landing-suite counter census/round-46/c1-counter.py at the round tip (exit 0)") has no exit-0 receipt in either the committed or working-tree copy of that file; both are exit 2, one from a CLI-argument mismatch and one from a dirty-worktree refusal. This does not touch C1 (my evidence reads committed bytes at cce21b55), but the L1 should not cite this file as the standing-check pass.

## Named limits (routed, not edited)

1. **Matrix granularity.** `run-matrix.sh` records only the first `FINDING` line per fixture. Second findings (F24's PAIR-FILING-HIDDEN) are not in the TSV; T1's parenthetical is therefore verified by a direct counter run plus the `pairhidden=` SUMMARY flag, not by the matrix. Any future claim that reads a multi-finding fixture from the matrix alone inherits this limit. Receipt: `receipts/step3-findings.out`.
2. **Runner pair-scan revision choice.** `run-matrix.sh` passes `--sources-rev-before/--sources-rev-after` equal to each fixture's tip, so the fixture arms exercise the pair scan over the fixture only. Correct for the fixture claim; it does not exercise the cross-revision pair scan that the real-lane leg does. No effect on T1–T5 as specified.
3. **Real-lane `filed=` semantics** counts a site as filed when a visible R52/R53 correction line names it; the correction file's *hidden* lines are now excluded by the same v5 rule, and I verified the two real filings are on visible lines 1243/1245. A filing that exists only inside a fence would read as unfiled under v5 — that is the intended direction (it is the F24 repair), and it is not exercised on the real lane.
4. **`registry_count` gate.** The pair scan is gated by `registry_count(corpus/SOURCES.md)` (202 rows at the measured revision), an internal ceiling not surfaced in SUMMARY; the SCORECARD rows state `rows=126` for the r51 census, a different quantity. Not a claim element, recorded only so a later reader does not read the 202-to-126 difference as a discrepancy.
5. **Method slips (mine, disclosed above).** T5 complement constant 29→27 in my derivation script, and one step-4 receipt captured from the wrong cwd (Python exit 2). Both were corrected inside my scratch; no frozen byte, no lane byte and no matrix byte changed.

## Scope, tools, scratch

- Files changed in the lane: only `.ufo/waves/round-56/w1/S56executor01/S56executor01-report.md` and `…/receipts/` (9 files). No counter, fixture, builder, expected TSV, record, control or SCORECARD byte touched; nothing committed.
- Tools installed or upgraded: none (no pacman, uv, npx, cargo, npm invocation).
- Scratch `/fast/scratch/hyaku/souji-r56/S56executor01/` deleted before yield; receipts copied into `./receipts/`.
- Every receipt in `./receipts/` ends with an `EXIT=` line (`receipt-step1-selftest.txt` EXIT=0, `receipt-step1b-wrongpin.txt` EXIT=2, `receipt-step2-build.txt` EXIT=0, `receipt-step2-matrix.txt` EXIT=0, `receipt-step2-bytecmp.txt` EXIT=0, `receipt-step3-derive.txt` EXIT=0, `receipt-step4-reallane.txt` EXIT=0; `step3-findings.out` is the merged six-invocation record, carries one `EXIT=` per invocation (F24 EXIT=1, F26 EXIT=1, F28 EXIT=1, F27 EXIT=1, F7-FF2 EXIT=1, F29 EXIT=0) and closes with `EXIT=0`).
