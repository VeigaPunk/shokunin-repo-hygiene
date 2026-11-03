# Seat S55scout01 Reconnaissance Report: Per-Surface Reconnaissance (Round 55, Wave w1)

- **Seat:** `S55scout01`
- **Role:** scout
- **Lane Repo:** `/home/vgpnk/Projects/shokunin/souji-shokunin`
- **Measured Revision:** `4b10ddd1741a948c89d283358affd1da2ab3fd95`
- **Lane Tip at Dispatch:** `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`
- **Freeze Commit:** `e8f338674dea386c186aa7657ef2142cbb4b6d48`
- **Scratch Directory:** `/fast/scratch/hyaku/souji-r55/S55scout01/` (deleted before yield)
- **Seat Output Directory:** `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-55/w1/S55scout01/`

---

## 1. Frozen Pin Verification

Every frozen pin declared in `census/round-55/preregistration.txt` was verified via `sha256sum` both in the working tree and at measured revision `4b10ddd1741a948c89d283358affd1da2ab3fd95`. All hashes match the frozen specification with 0 discrepancies.

| Path | Declared Frozen sha256 | Worktree sha256 | Rev `4b10ddd1` sha256 | Status |
|---|---|---|---|---|
| `census/round-55/c1-counter.py` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2` | MATCH |
| `census/round-55/c2-counter.py` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | `e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c` | MATCH |
| `census/round-55/fixtures/build-fixtures.py` | `e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62` | `e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62` | `e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62` | MATCH |
| `census/round-55/fixtures/run-matrix.sh` | `ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315` | `ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315` | `ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315` | MATCH |
| `census/round-55/records/c1-selftest-expected.tsv` | `ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e` | `ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e` | `ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e` | MATCH |
| `census/round-55/records/c2-selftest-expected.tsv` | `63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc` | `63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc` | `63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc` | MATCH |

Receipt preserved at `receipts/frozen-pins-sha256.txt`.

---

## 2. Fixture Determinism Verification

The committed builder `census/round-55/fixtures/build-fixtures.py` was executed to verify determinism across multiple runs and against committed records:

1. **Same-Path Reproducibility:**
   - Builder was run twice pointing to the same scratch workspace.
   - Manifest `m1.tsv` and `m2.tsv` are byte-identical (`cmp` exit 0, sha256 `467614b6367289b48f683e259fbc4b4c39879687d83fc45a1f2eb35d635aec37`).

2. **Cross-Directory Consistency:**
   - Builder was run into two distinct scratch directories (`run1` and `run2`).
   - Manifest comparison: the only textual difference between `run1/fixture-manifest.tsv` and `run2/fixture-manifest.tsv` is the workspace directory path prefix in column 3 (`dir`).
   - Columns `(name, kind, base, tip, record_sha256)` (cut columns 1, 2, 4, 5, 6) are 100% byte-identical across both runs.

3. **Comparison with `records/matrix-dryrun/` and Control Files:**
   - Evaluated all 40 fixtures (27 for C1, 13 for C2).
   - In C1, `F5-REWRITE` and `F6-RECORD-DRIFT` legitimately differ in base revision from tip revision (`base="$b"`), whereas the other 25 C1 fixtures evaluate against `base="$t"`.
   - Every single fixture in the generated manifest matches the dry-run matrix `c1-matrix-v4.tsv`, `c2-matrix-v4.tsv`, and the control-file rows in `c1-control-donothing.txt` and `c2-control-donothing.txt` byte-for-byte in their short and full hash prefixes.
   - Result: **40 of 40 fixtures match dry-run and control-file rows exactly**.

Receipt preserved at `receipts/fixture-determinism.txt`.

---

## 3. Host-Difference Re-Measurement

1. **Sources-Census Validation:**
   - Command: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
   - Exit code: **0** (`RC: 0`).
   - Standard output: all reported `W04` warnings are benign cross-scope duplicate URLs, ending with:
     `souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`
   - Receipt preserved at `receipts/sources-census-validate.txt`.

2. **Jujutsu VCS State (`jj-lane.sh state`):**
   - Command: `bash /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh state /home/vgpnk/Projects/shokunin/souji-shokunin`
   - Output: `state branch=master local=3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f remote=3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f ahead=0 behind=0 head=detached tracked=3 untracked=2`
   - Confirmed: `local=remote` (`ahead=0 behind=0`).

3. **Lane Porcelain:**
   - Current lane HEAD is `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f` (added records and S278 sources).
   - Active worktree modifications observed during round execution reflect live authoring by L1 (`SoujiR55`):
     - Modified: `SKILL.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`
     - Untracked: `corpus/knowledge/splitlines-line-model.md`, `corpus/lessons/round-55.md`
   - Receipt preserved at `receipts/porcelain-and-status.txt`.

---

## 4. Routed-Item Coverage Map

All 17 requested routed surfaces (S1, R1, R2, R3, R4, R5, R6, S2, PTR, M2, M7, M11, N5, NL-1, NL-3, NL-4, NL-5) are mapped to committed fixtures or selftest arms.

| Item | Origin & Defect / Surface Description | Instrumented Fixture / Selftest Arm | Counter | Expected Exit | Expected Finding | Mapping Status & Evidence |
|---|---|---|---|---|---|---|
| **S1** | Sentinel S1 (HIGH): exotic line separators (`\x0c` form-feed) bypass fence refusal in v3 due to `str.splitlines()` LF divergence | `F7-FF` | C1 v4 | 1 | `CORRECTION-IN-FENCE` | Mapped (`c1-selftest-expected.tsv` line 15; prereg §C1) |
| **R1** | Reviewer R1: prefix-tolerant lexing on agreeing sites (leading spaces or one-line `<!--...-->` wrappers never lexed by v3) | `F20-R1-INDENT-SWALLOW` and `F21-R1-ONELINE-SWALLOW` | C1 v4 | 1 | `BOGUS-RECOMPUTED` | Mapped (`c1-selftest-expected.tsv` lines 25-26; prereg §C1) |
| **R2** | Reviewer R2 / AF2d: dual-anchor aliasing; second annotated anchor on same site line with conflicting count ignored by v3 | `F13-DUAL-ANCHOR` | C1 v4 | 1 | `ANCHOR-ALIAS-MISMATCH` | Mapped (`c1-selftest-expected.tsv` line 18; prereg §C1) |
| **R3** | Reviewer R3 / AF3d: pair filing stale drop; stale pair in R53-CORRECTION differs from annotated pair, silently dropped by v3 | `F14-PAIR-STALE-FILING` | C1 v4 | 1 | `PAIR-FILING-INERT` | Mapped (`c1-selftest-expected.tsv` line 19; prereg §C1) |
| **R4** | Reviewer R4 / AF4b: rows-word dodge; pair overstatement without unit word `rows` escaped v3 regex | `F15-PAIR-NOROWS` | C1 v4 | 1 | `UNFILED-SOURCES-ANNOTATION` | Mapped (`c1-selftest-expected.tsv` line 20; prereg §C1) |
| **R5** | Reviewer R5 / AF1f2, AF1g: over-hide false positives against CommonMark 0.31.2 (4-space indent and backtick in info string) | `F17-INDENT4-FENCE` and `F18-BTINFO-FENCE` | C1 v4 | 0 | `-` | Mapped (`c1-selftest-expected.tsv` lines 22-23; honest filings accepted) |
| **R6** | Reviewer R6 / AF4d: pair annotation in fenced example in LOG.md caused false-positive UNFILED in v3 | `F19-PAIR-IN-FENCE` | C1 v4 | 0 | `-` | Mapped (`c1-selftest-expected.tsv` line 24; false positive repaired) |
| **S2** | Sentinel S2 (MEDIUM): pair scan was ASCII-only (`->`); unicode arrow `→` dodged scan | `F16-PAIR-ARROW` | C1 v4 | 1 | `UNFILED-SOURCES-ANNOTATION` | Mapped (`c1-selftest-expected.tsv` line 21; prereg §C1) |
| **PTR** | Connector PTR: pointer exemption was unscoped `PTR_RE = [A-Za-z0-9_.\-]+:\d`, so timestamps (`14:05`) exempted overstatements | `F22-PTR-TIMESTAMP` | C1 v4 | 1 | `UNFILED-SOURCES-ANNOTATION` | Mapped (`c1-selftest-expected.tsv` line 27; prereg §C1) |
| **M2** | Mutation M2 survivor: closing-fence length rule (shorter run inside longer fence is content) | `F8b-BT4-SHORT-RUN` | C1 v4 | 1 | `CORRECTION-IN-FENCE` | Mapped (`c1-selftest-expected.tsv` line 17; prereg §C1) |
| **M7** | Mutation M7 survivor: real pointer exemption branch coverage (`LOG.md` pointer) | `F12c-LOG-POINTER-EXEMPT` | C1 v4 | 0 | `-` | Mapped (`c1-selftest-expected.tsv` line 16; honest state green) |
| **M11** | Mutation M11 survivor: C2 `--tool-sha256` mismatch branch coverage (prereg citation corrected by ERRATUM-R54-1) | `FA9-WRONG-TOOL-PIN` (selftest arm) | C2 v4 | 1 | `TOOL-SHA-ARG-MISMATCH` | Mapped (`c2-selftest-expected.tsv` line 15; prereg §C2) |
| **N5** | Critic N5: `SOURCES-RECOMPUTE-MISMATCH` branch coverage gap | `F23-SOURCES-RECOMP` | C1 v4 | 1 | `SOURCES-RECOMPUTE-MISMATCH` | Mapped (`c1-selftest-expected.tsv` line 28; prereg §C1) |
| **NL-1** | Reviewer02 NL-1: `#`-leading capture rows with 4 tabs were silently dropped by v3 | `FB1-TAB4-ROW` | C2 v4 | 1 | `COMMENT-AMBIGUOUS-NAME` | Mapped (`c2-selftest-expected.tsv` line 12; prereg §C2) |
| **NL-3** | Reviewer02 NL-3 / S3: lowercase unknown receipt key (`# generator=x`) passed in v3 | `FB2-LOWER-KEY` | C2 v4 | 1 | `RECEIPT-UNKNOWN-KEY` | Mapped (`c2-selftest-expected.tsv` line 13; prereg §C2) |
| **NL-4** | Reviewer02 NL-4: receipt unknown key without space (`#BUILDHOST=x`) evaded v3's `# ` anchor | `FB3-NOSPACE-KEY` | C2 v4 | 1 | `RECEIPT-UNKNOWN-KEY` | Mapped (`c2-selftest-expected.tsv` line 14; prereg §C2) |
| **NL-5** | Reviewer02 NL-5: `--tool-sha256` pin shape error (uppercase digest) refused with named error | `FB4-PIN-SHAPE` (selftest arm) | C2 v4 | 2 | `TOOL-SHA-ARG-MALFORMED` | Mapped (`c2-selftest-expected.tsv` line 16; prereg §C2) |

**Unmapped Routed Items:** **0**. All 17 items have verified mappings to committed fixtures or selftest arms.

---

## 5. Counter Selftest Verification

Both counter selftest suites were executed with pinned SHA256 arguments verifying builder and expected fixtures before execution:

- **C1 Counter Selftest (`census/round-55/c1-counter.py`):**
  - Command: `python3 -B census/round-55/c1-counter.py --selftest --work <scratch> --builder-sha256 e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62 --expected-sha256 ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e`
  - Output: `SELFTEST pass cases=27`, `rc: 0`.
- **C2 Counter Selftest (`census/round-55/c2-counter.py`):**
  - Command: `python3 -B census/round-55/c2-counter.py --selftest --work <scratch> --builder-sha256 e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62 --expected-sha256 63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc`
  - Output: `SELFTEST pass cases=15`, `rc: 0`.

Receipt preserved at `receipts/selftests.txt`.

---

## 6. Tooling and Environment Accounting

- **Installed/Upgraded Tools:** None. All checks executed using existing stock Python 3 and system utilities.
- **File System / Scratch Cleanup:** All temporary fixtures, manifests, and scratch runs created in `/fast/scratch/hyaku/souji-r55/S55scout01/` were scrubbed and deleted prior to completion. All command outputs and audit receipts were copied into `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-55/w1/S55scout01/receipts/`.
