# Seat S56scout01 Reconnaissance Report: Per-Surface Reconnaissance (Round 56, Wave w1)

- **Seat:** `S56scout01`
- **Role:** scout
- **Lane Repo:** `/home/vgpnk/Projects/shokunin/souji-shokunin`
- **Measured Revision:** `cce21b555a617cadda782613ec1e9d3a0c12ac83`
- **Base Revision:** `fafe371694fea41c5d23f63083865d5ccf3f1d36`
- **Freeze Commit:** `cce21b555a617cadda782613ec1e9d3a0c12ac83`
- **Lane Head at Audit:** `148f39a6c902b27e997ac36d395735406d3ad9de`
- **Scratch Directory:** `/fast/scratch/hyaku/souji-r56/S56scout01/` (deleted before yield)
- **Seat Output Directory:** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-56/w1/S56scout01/`

VERDICT: AGREE

---

## Executive Summary

Reconnaissance by seat `S56scout01` confirmed all ground truths, frozen pins, fixture determinism, host state, and coverage mappings for souji round 56 at measured revision `cce21b555a617cadda782613ec1e9d3a0c12ac83`:
1. **Frozen Pins (12 of 12 verified):** Every declared sha256 pin in `census/round-56/preregistration.txt` matches `git show <rev>:<path> | sha256sum` byte-for-byte with 0 discrepancies.
2. **Fixture Determinism:** The fixture builder `census/round-56/fixtures/build-fixtures.py` is fully deterministic. Manifests generated in independent runs match 100% across all 49 fixtures in all semantic columns (`name`, `kind`, `base`, `tip`, `record_sha256`); identical target paths produce byte-for-byte identical manifests; and every fixture's `rev` and `base` matches the committed dry-run matrices `c1-matrix-v5.tsv` and `c2-matrix-v5.tsv` exactly.
3. **Official vs Dry-Run Matrices:** All four matrix TSVs in `census/round-56/records/` (`c1-matrix-v4.tsv`, `c1-matrix-v5.tsv`, `c2-matrix-v4.tsv`, `c2-matrix-v5.tsv`) match their corresponding pre-freeze files in `census/round-56/records/matrix-dryrun/` byte-for-byte.
4. **Host State:** `sources-census.sh validate` exits 0; `jj-lane.sh state` reports `local=remote` with `ahead=0 behind=0`; git status shows post-freeze receipt additions as expected.
5. **Counter Selftests and Real Lane Runs:** C1 selftest passes all 33 cases (exit 0); C2 selftest passes all 18 cases (exit 0); C2 scratch mutant with an omitted arm fails with `SELFTEST-ROW-MISMATCH` (exit 1); C1 real-lane recomputation passes with `unfiled=0` (exit 0); C2 real-lane recomputation passes with `receipt=ok sorted=ok tool_pin=ok` (exit 0).
6. **Routed-Item Coverage:** All 12 numbered items and 9 named limits from round 55 are comprehensively mapped to committed fixtures, selftest arms, named limits, or classified as open backlog.

---

## 1. Frozen Pin Verification

Every frozen pin declared in `census/round-56/preregistration.txt` was verified via `git show <rev>:<path> | sha256sum` at the frozen commit `cce21b55` or base `fafe3716`. All 12 hashes match with 0 discrepancies.

| Path | Rev | Expected sha256 | Actual sha256 | Status |
|---|---|---|---|---|
| `census/round-56/c1-counter.py` | `cce21b55` | `975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179` | `975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179` | MATCH |
| `census/round-56/c2-counter.py` | `cce21b55` | `5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8` | `5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8` | MATCH |
| `census/round-56/fixtures/build-fixtures.py` | `cce21b55` | `2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a` | `2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a` | MATCH |
| `census/round-56/fixtures/run-matrix.sh` | `cce21b55` | `a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3` | `a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3` | MATCH |
| `census/round-56/records/c1-selftest-expected.tsv` | `cce21b55` | `48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb` | `48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb` | MATCH |
| `census/round-56/records/c2-selftest-expected.tsv` | `cce21b55` | `90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3` | `90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3` | MATCH |
| `census/round-55/c1-counter.py` | `cce21b55` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | MATCH |
| `census/round-55/c2-counter.py` | `cce21b55` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | MATCH |
| `census/round-51/records/ws-drift-vs-r46.tsv` | `fafe3716` | `2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30` | `2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30` | MATCH |
| `tools/souji-fleet-root-census.py` | `fafe3716` | `e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b` | `e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b` | MATCH |
| `census/round-55/records/fleet-root-census.tsv` | `cce21b55` | `088aaa2644eeae1044dfdd5fa272fafe54fee473f31cae11b0543d23e6f73d40` | `088aaa2644eeae1044dfdd5fa272fafe54fee473f31cae11b0543d23e6f73d40` | MATCH |
| `census/round-55/records/fleet-root-census-run.txt` | `cce21b55` | `479b2715466ce4892f065b6be1f5846abe04aa6f79eea03fab976c63c24bab45` | `479b2715466ce4892f065b6be1f5846abe04aa6f79eea03fab976c63c24bab45` | MATCH |

Additionally verified: `census/round-55/c1-counter.py` and `census/round-55/c2-counter.py` at `fafe3716` yield identical sha256 digests (`944feafa...` and `e4eb34e6...`).

### Command Receipt (`receipts/frozen-pins-sha256.txt`)
```
OK census/round-56/c1-counter.py @ cce21b55 actual=975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179 expected=975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179
OK census/round-56/c2-counter.py @ cce21b55 actual=5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8 expected=5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8
OK census/round-56/fixtures/build-fixtures.py @ cce21b55 actual=2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a expected=2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a
OK census/round-56/fixtures/run-matrix.sh @ cce21b55 actual=a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3 expected=a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3
OK census/round-56/records/c1-selftest-expected.tsv @ cce21b55 actual=48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb expected=48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb
OK census/round-56/records/c2-selftest-expected.tsv @ cce21b55 actual=90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3 expected=90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3
OK census/round-55/c1-counter.py @ cce21b55 actual=944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2 expected=944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2
OK census/round-55/c2-counter.py @ cce21b55 actual=e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c expected=e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c
OK census/round-51/records/ws-drift-vs-r46.tsv @ fafe3716 actual=2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 expected=2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30
OK tools/souji-fleet-root-census.py @ fafe3716 actual=e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b expected=e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b
OK census/round-55/records/fleet-root-census.tsv @ cce21b55 actual=088aaa2644eeae1044dfdd5fa272fafe54fee473f31cae11b0543d23e6f73d40 expected=088aaa2644eeae1044dfdd5fa272fafe54fee473f31cae11b0543d23e6f73d40
OK census/round-55/records/fleet-root-census-run.txt @ cce21b55 actual=479b2715466ce4892f065b6be1f5846abe04aa6f79eea03fab976c63c24bab45 expected=479b2715466ce4892f065b6be1f5846abe04aa6f79eea03fab976c63c24bab45
ALL_PINS_OK: True
EXIT=0
```

---

## 2. Fixture Determinism Verification

The committed builder `census/round-56/fixtures/build-fixtures.py` was executed to verify determinism:
1. **Cross-Directory Consistency:**
   - Builder executed into two distinct scratch workspaces (`run1` and `run2`).
   - Comparison across all 49 rows: columns `kind`, `base`, `tip`, and `record_sha256` are identical with 0 discrepancies.
   - The only difference between manifests is the directory prefix in column 3 (`dir`).
2. **Same-Path Reproducibility:**
   - Builder executed into the same scratch path twice.
   - Manifests are 100% byte-for-byte identical (sha256 `d40e11e73204af37632b573771c23efa3c60c49ff211796f651019217afdec87`).
3. **Comparison with Dry-Run Runner Output:**
   - Evaluated against `census/round-56/records/matrix-dryrun/c1-matrix-v5.tsv` (33 fixtures) and `c2-matrix-v5.tsv` (16 fixtures).
   - In C1, `F5-REWRITE`, `F6-RECORD-DRIFT`, and `F27-BINARY-NUMSTAT` evaluate against `base=base[:12]`, while all other C1 fixtures evaluate against `base=tip[:12]`.
   - Every single fixture in the manifest matches the dry-run matrix `rev` and `base` columns exactly (0 mismatches across 49 fixtures).

### Command Receipt (`receipts/fixture-determinism.txt`)
```
=== PART 1: CROSS-DIRECTORY MANIFEST COMPARISON (run1 vs run2) ===
run1 manifest rows: 49
run2 manifest rows: 49
Differences in non-dir columns: 0
All non-dir columns (kind, base, tip, record_sha256) match 100% across all 49 fixtures.
The only difference between manifests is column 3 ('dir') due to scratch workspace prefix.

=== PART 2: SAME-PATH REPRODUCIBILITY ===
Same path rebuild byte-identical: True
Manifest sha256: d40e11e73204af37632b573771c23efa3c60c49ff211796f651019217afdec87

=== PART 3: DRY-RUN RUNNER COMPARISON (c1-matrix-v5.tsv and c2-matrix-v5.tsv) ===
C1 fixtures checked: 33, mismatches: 0
C2 fixtures checked: 16, mismatches: 0

DETERMINISM_VERIFIED: True
EXIT=0
```

---

## 3. Official vs Dry-Run Matrices Byte Comparison

All four matrix files committed in `census/round-56/records/` were byte-compared against their pre-freeze versions in `census/round-56/records/matrix-dryrun/`:
- `c1-matrix-v4.tsv`: 9264 bytes, sha256 `4b6fd50499ff86573538e3205f33ce1dab3aebf4d51ba310f92b42d7ba303bcc` (IDENTICAL)
- `c1-matrix-v5.tsv`: 9760 bytes, sha256 `3bfa8180d3711bfd1b150a144828937247f3ca5b1598f6e1f5efc007ef86d72e` (IDENTICAL)
- `c2-matrix-v4.tsv`: 3294 bytes, sha256 `d7bf3a720bca0f3196444dbf46167fb67b184dfb4614bdcfb773fcfeb5c90c48` (IDENTICAL)
- `c2-matrix-v5.tsv`: 3348 bytes, sha256 `d8613afdeb0c18897cd453db405ececbf8d964750764b02053c1bbe62df128e6` (IDENTICAL)

### Command Receipt (`receipts/official-vs-dryrun-matrices.txt`)
```
IDENTICAL c1-matrix-v4.tsv: bytes=9264 sha256=4b6fd50499ff86573538e3205f33ce1dab3aebf4d51ba310f92b42d7ba303bcc
IDENTICAL c1-matrix-v5.tsv: bytes=9760 sha256=3bfa8180d3711bfd1b150a144828937247f3ca5b1598f6e1f5efc007ef86d72e
IDENTICAL c2-matrix-v4.tsv: bytes=3294 sha256=d7bf3a720bca0f3196444dbf46167fb67b184dfb4614bdcfb773fcfeb5c90c48
IDENTICAL c2-matrix-v5.tsv: bytes=3348 sha256=d8613afdeb0c18897cd453db405ececbf8d964750764b02053c1bbe62df128e6

ALL_MATRICES_BYTE_IDENTICAL: True
EXIT=0
```

---

## 4. Host State Verification

1. **Sources Census Validation:**
   - Command: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
   - Exit code: 0 (`EXIT=0`).
   - Ending confirmation: `souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`.
2. **Jujutsu VCS State (`jj-lane.sh state`):**
   - Command: `bash /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin`
   - Output: `state branch=master local=148f39a6c902b27e997ac36d395735406d3ad9de remote=148f39a6c902b27e997ac36d395735406d3ad9de ahead=0 behind=0 head=detached tracked=2 untracked=0`
   - Confirmed: `local=remote`, `ahead=0 behind=0` (`EXIT=0`).
3. **Lane Porcelain (`git status --porcelain`):**
   - Output:
     ```
      M SCORECARD.md
      M census/round-56/records/landing-suite-standing.txt
     ?? census/round-56/records/row-omission-v4.txt
     ?? census/round-56/records/row-omission-v5.txt
     ```
   - Untracked files are post-freeze measurement receipts (`row-omission-v4.txt`, `row-omission-v5.txt`) written during post-freeze L1 validation as anticipated.

### Command Receipts
#### `receipts/sources-census-validate.txt` (tail)
```
souji	W04	S272 duplicate url docs.python.org/3/library/functions.html across scopes
souji	W04	S275 duplicate url git-scm.com/docs/git across scopes
souji	W04	S276 duplicate url git-scm.com/docs/gitignore across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```
#### `receipts/jj-lane-state.txt`
```
state branch=master local=148f39a6c902b27e997ac36d395735406d3ad9de remote=148f39a6c902b27e997ac36d395735406d3ad9de ahead=0 behind=0 head=detached tracked=2 untracked=0
EXIT=0
```
#### `receipts/porcelain-and-status.txt`
```
 M SCORECARD.md
 M census/round-56/records/landing-suite-standing.txt
?? census/round-56/records/row-omission-v4.txt
?? census/round-56/records/row-omission-v5.txt
EXIT=0
```

---

## 5. Counter Selftests and Recomputation Verification

1. **C1 Counter Selftest:**
   - Invocation: `python3 -B census/round-56/c1-counter.py --selftest --work <scratch> --builder-sha256 2f26d6aa... --expected-sha256 48a7cc0e...`
   - Result: `SELFTEST pass cases=33`, exit 0.
2. **C2 Counter Selftest:**
   - Invocation: `python3 -B census/round-56/c2-counter.py --selftest --work <scratch> --builder-sha256 2f26d6aa... --expected-sha256 90517c4d...`
   - Result: `SELFTEST pass cases=18`, exit 0.
3. **C2 Row-Set Check Mutant (T6/T9):**
   - Invocation: Scratch mutant of `c2-counter.py` omitting `FA9-WRONG-TOOL-PIN` from the selftest run list.
   - Result: `SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN`, `SELFTEST fail cases=17`, exit 1.
4. **C1 Real-Lane Recomputation:**
   - Result: `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=cce21b555a61 base=fafe371694fe`, exit 0.
5. **C2 Real-Lane Recomputation:**
   - Result: `SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=cce21b555a61`, exit 0.

### Command Receipt (`receipts/selftests.txt`)
```
=== C1 COUNTER SELFTEST ===
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
c1_selftest rc=0

=== C2 COUNTER SELFTEST ===
SELFTEST-CASE FH-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FH2-SYMLINK-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FA1-UNSORTED pass rc=1 want_rc=1 finding=ROWS-UNSORTED want_finding=ROWS-UNSORTED
SELFTEST-CASE FA2-COMMENT pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA3-TAMPER pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA4-SPACE-NAME pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA5-EXTRA-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA6-CRLF pass rc=1 want_rc=1 finding=CAPTURE-CRLF want_finding=CAPTURE-CRLF
SELFTEST-CASE FA7-RECEIPT-ENTRIES pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA8-SYMLINK-CLASS pass rc=1 want_rc=1 finding=CLASS-MISMATCH want_finding=CLASS-MISMATCH
SELFTEST-CASE FB1-TAB4-ROW pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FB2-LOWER-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FB3-NOSPACE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC1-UNDERSCORE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC2-DIGIT-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC3-EMPTY-VALUE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA9-WRONG-TOOL-PIN pass rc=1 want_rc=1 finding=TOOL-SHA-ARG-MISMATCH want_finding=TOOL-SHA-ARG-MISMATCH
SELFTEST-CASE FB4-PIN-SHAPE pass rc=2 want_rc=2 finding=TOOL-SHA-ARG-MALFORMED want_finding=TOOL-SHA-ARG-MALFORMED
SELFTEST pass cases=18
c2_selftest rc=0

=== C2 MUTANT SELFTEST (ROW-SET CHECK) ===
SELFTEST-CASE FH-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FH2-SYMLINK-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FA1-UNSORTED pass rc=1 want_rc=1 finding=ROWS-UNSORTED want_finding=ROWS-UNSORTED
SELFTEST-CASE FA2-COMMENT pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA3-TAMPER pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA4-SPACE-NAME pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA5-EXTRA-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA6-CRLF pass rc=1 want_rc=1 finding=CAPTURE-CRLF want_finding=CAPTURE-CRLF
SELFTEST-CASE FA7-RECEIPT-ENTRIES pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA8-SYMLINK-CLASS pass rc=1 want_rc=1 finding=CLASS-MISMATCH want_finding=CLASS-MISMATCH
SELFTEST-CASE FB1-TAB4-ROW pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FB2-LOWER-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FB3-NOSPACE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC1-UNDERSCORE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC2-DIGIT-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC3-EMPTY-VALUE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FB4-PIN-SHAPE pass rc=2 want_rc=2 finding=TOOL-SHA-ARG-MALFORMED want_finding=TOOL-SHA-ARG-MALFORMED
SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN
SELFTEST fail cases=17
c2_mutant rc=1

=== C1 REAL-LANE RECOMPUTATION ===
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 pairhidden=0 recomputed=79 rev=cce21b555a61 base=fafe371694fe
c1_real rc=0

=== C2 REAL-LANE RECOMPUTATION ===
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=cce21b555a61
c2_real rc=0

ALL_SELFTESTS_AND_REAL_RUNS_OK: True
EXIT=0
```

---

## 6. Routed-Item Coverage Map

Mapping of all r55 routed items (numbered 1–12) and named limits (N5, N7, N8, N10, N11, N12, S55-S3, S55-S4, S55-S5) from `corpus/lessons/round-55.md`:

| Item | Origin & Description | Instrumented Fixture / Selftest Arm | Expected Exit | Expected Finding | Classification / Status |
|---|---|---|---|---|---|
| **1. RD-A** | Reviewer02 (r55): first-character receipt unknown key (`_KEY=x`, `1KEY=x`) | `FC1-UNDERSCORE-KEY`, `FC2-DIGIT-KEY` | 1 | `RECEIPT-UNKNOWN-KEY` | INSTRUMENTED (`c2-selftest-expected.tsv` lines 17-18) |
| **2. N1 / D14 / D15** | Reviewer01 / Critic (r55): pair filings inside fences and comments refused | `F24-PAIR-HIDDEN-FILING` | 1 | `UNFILED-SOURCES-ANNOTATION` | INSTRUMENTED (`c1-selftest-expected.tsv` line 29) |
| **3. A09–A13** | Reviewer01 (r55): fence closer with exotic whitespace (VT, FF, NEL, LS, FS) | None | - | - | NAMED-LIMIT (carried into r57; round-56 lesson §Named limits) |
| **4. E09/E10** | Reviewer01 (r55): fence inside list item treated as code | None | - | - | OPEN |
| **5. C04/C07** | Reviewer01 (r55): unannotated first anchor occurrence causes INERT over-refusal | None | - | - | OPEN |
| **6. N4** | Critic (r55): pointer regex `\w.\w{1,5}:\d` exempts ratio `2.5:1` | None | - | - | NAMED-LIMIT (ERRATUM-R55-2; pointer regex intentionally retains ratio exemption) |
| **7. N2, N3, D07/D08, D12, D16, B07, F01** | Reviewer01 / Critic (r55): prose pair variants (`=>`, `—>`, missing prefix, 4-space indent, non-ASCII digits) | None | - | - | OPEN |
| **8. RD-B, RD-C, RD-D, RD-E** | Reviewer02 (r55): receipt KV variants (`KEY-1=x`, `KEY.1=x`, `KEY=x y`), capture header known keys, selftest traceback on malformed TSV | None (empty value `KEY=` addressed via S55-S5/FC3) | - | - | OPEN (partially instrumented via FC3; remainder open) |
| **9. Mutation01 C2-17/18** | Mutation01 (r55): selftest harness assert that every expected row ran | `census/round-56/c2-counter.py` selftest harness | 1 | `SELFTEST-ROW-MISMATCH` | INSTRUMENTED (c2-counter.py lines 406-415; verified via scratch mutant in T6) |
| **10. Revenger items** | Revenger (r55): S4 (`--work` relative path), S5 (`PRISTINE FAIL` in docstring), N6 (exit-code legend) | None | - | - | OPEN |
| **11. Receipts (critic N15)** | Critic N15 (r55): receipts omit exit code; r56 receipts must print `EXIT=` | Prereg C1 T8 & C2 T7; enforced across r56 receipts | 0 | `EXIT=0` | INSTRUMENTED (all r56 official receipts print `EXIT=0`) |
| **12. ERRATUM-R55-1 / numstat** | Sentinel S1 (r55): form-feed fixture and numstat unreadable parse | `F7-FF2`, `F27-BINARY-NUMSTAT`, `F28-NUL-CORRECTION-UNCHANGED` | 1 | `CORRECTION-IN-FENCE` (FF2), `DELETIONS-UNREADABLE-BINARY` (F27), `CORRECTION-FILE-BINARY` (F28) | INSTRUMENTED (`c1-selftest-expected.tsv` lines 28, 31, 32; LF-only numstat is NAMED-LIMIT) |
| **N5** | Critic (r55): two annotation sites only (SCORECARD.md & round-51 prereg) | None | - | - | NAMED-LIMIT (carried into r57; round-56 lesson §Named limits) |
| **N7** | Reviewer02 (r55): first unknown receipt key reported only | None | - | - | NAMED-LIMIT (carried into r57; round-56 lesson §Named limits) |
| **N8** | Reviewer01 (r55): beyond-zone sole annotation exits 2 | None | - | - | NAMED-LIMIT (disclosed named limit) |
| **N10** | Critic (r55): pair annotations outside LOG.md and corpus/README.md invisible | None | - | - | NAMED-LIMIT (carried into r57; round-56 lesson §Named limits) |
| **N11** | Reviewer01 (r55): v4 changes F10 SUMMARY counts (skipped straddling site) | None | - | - | NAMED-LIMIT (unlisted behavior change recorded in r55 lesson) |
| **N12** | Critic (r55): `run-matrix.sh` takes second token of first FINDING line | None | - | - | NAMED-LIMIT (runner format convention) |
| **S55-S3** | Sentinel (r55): corrections outside lexing tolerance never audited (unjudged) | None | - | - | NAMED-LIMIT (disclosed named limit) |
| **S55-S4** | Sentinel (r55): without `-B`, builder writes `__pycache__` in lane | None | - | - | NAMED-LIMIT (mitigated: all committed invocations use `-B`) |
| **S55-S5** | Sentinel (r55): unknown receipt key with empty value (`# BUILDHOST=`) | `FC3-EMPTY-VALUE-KEY` | 1 | `RECEIPT-UNKNOWN-KEY` | INSTRUMENTED (`c2-selftest-expected.tsv` line 19) |

### List of OPEN Items
1. **Item 4 (E09/E10):** CommonMark fence inside list items treated as code rather than hiding block.
2. **Item 5 (C04/C07):** Unannotated first occurrence of anchor with annotated second occurrence reading as INERT.
3. **Item 7 (N2, N3, D07/D08, D12, D16, B07, F01):** Unmodelled prose pair separators (`=>`, `—>`), multiple pair annotations per line, missing `corpus/` prefix, 4-space indented pair lines, bare filing trailing text, non-ASCII digits.
4. **Item 8 (RD-B, RD-C, RD-D, RD-E):** Receipt KV keys containing hyphens (`KEY-1=x`), dots (`KEY.1=x`), or spaces (`KEY=x y`); capture header vs receipt key discrepancies; harness error handling on malformed TSV.
5. **Item 10 (Revenger items S4, S5, N6):** Builder relative path handling (`--work`), docstring wording cleanup (`PRISTINE FAIL`), exit-code legend.

---

## 7. Tooling and Environment Accounting

- **Installed/Upgraded Tools:** None. All checks executed using system Python 3 (`/usr/bin/python3`) and standard utilities.
- **File System / Scratch Cleanup:** All temporary fixtures, mutant scripts, and scratch workspaces under `/fast/scratch/hyaku/souji-r56/S56scout01/` were completely removed before yielding. All verified command receipts were committed to `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-56/w1/S56scout01/receipts/`.
