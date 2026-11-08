# S87ExecC2 — C2 (K4) two-arm re-derivation and `-z` regression attack

Seat: S87ExecC2 (executor, leaf). Lane: `souji-shokunin`. Round 87, wave 1.
Read-only lane tip at start: `git rev-parse refs/heads/master` = `6e502c5c05fd3ca4193883921ef0c9b79a7d36a7` (the C2 repair commit);
lane base `5e288bb3`, P `77ccef7c`, F `6ed2d368`. No lane file was modified, no commit/fetch; write scope was this
report plus `.ufo/waves/round-87/w1/S87ExecC2/`.

All receipts are under `receipts/` beside this file; probes are hermetic (the frozen `c2-k4-counter.py` fixture builder
imported read-only; both tool copies run from scratch kits; git 2.56.0; `LC_ALL=C`, pinned `GIT_CONFIG_*` as the
counter sets them). Scratch was `/fast/scratch/hyaku/souji-r87/S87ExecC2/` and is deleted before yield.

## 1. Both C2 arms, re-derived

Commands (from the lane root, work dirs under the seat scratch):

    after : python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work .../after-work
    before: python3 -B census/round-87/c2-k4-counter.py --tool census/round-87/controls/c2-before-base-tool.py --work .../before-work

### 1a. After arm — receipt `receipts/c2-after.out`, process RC 0

    # tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=0ad9e3bfdf428ff1a335f6037043c4c9062a3f33d830beef37346af4426677ee
    # writer path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
    # counter sha256=4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e
    ROW KH1 expect=clean k4=0 named=- rc=1 match=yes
    ROW KH2 expect=clean k4=0 named=- rc=1 match=yes
    ROW KU1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['a.txt|uncommitted-path']
    ROW KU2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['untracked-scratch.txt|uncommitted-path']
    ROW KF1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
    ROW KF2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
    ROW KF3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
    ROW KG1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|index-flag-concealed']
    ROW KG2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
    ROW KN1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
    ROW KN2 expect=header k4=0 named=yes rc=1 match=yes writer_sha=70bbf1c2a92e appended_sha=1b8ecf328ed3
    ROW KN3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['bad\nname2.txt|uncommitted-path']
    SUMMARY rows=12 mismatches=0 errors=0
    EXIT=0

### 1b. Before arm — receipt `receipts/c2-before.out`, process RC 1

    # tool path=.../census/round-87/controls/c2-before-base-tool.py sha256=cf8753673b566da1e9a634d790dda70e93efef396f33bb3e42d4fad1425cbddc
    # writer path=.../census/round-87/controls/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
    ROW KH1..KG2   identical to the after arm (nine r85/r86 rows unchanged)
    ROW KN1 expect=flag k4=1 named=no rc=1 match=no k4rows=['.|stat-cache-concealed'] detail=''
    ROW KN2 expect=header k4=0 named=no rc=1 match=no detail=''
    ROW KN3 expect=flag k4=1 named=no rc=1 match=no k4rows=['"bad\nname2.txt"|uncommitted-path'] detail=''
    SUMMARY rows=12 mismatches=3 errors=0
    EXIT=1

### 1c. Comparison with the frozen receipts

* `receipts/c2-before-vs-frozen.diff` is 0 bytes: the before arm's rows/SUMMARY/EXIT are identical to
  `census/round-87/controls/c2-before.txt` once the `# tool|writer|fixture` path lines are dropped.
* `receipts/c2-after-vs-frozen-before.diff` (662 bytes) changes only KN1, KN2, KN3 and the SUMMARY/EXIT: KN1/KN2/KN3
  become `named=yes match=yes`, `SUMMARY rows=12 mismatches=3 errors=0` -> `rows=12 mismatches=0 errors=0`, `EXIT=1` ->
  `EXIT=0`.
* The KN1 detail was captured independently (`receipts/kn1/`): the filed arm prints
  `... produced no verdict (exit 1: AttributeError: r87 KN1 stub: no truth helper); tracked bytes are unverified`,
  the base arm prints `... produced no verdict (exit 1: Traceback (most recent call last):` — the last-stderr-line
  property (c) holds on the filed arm and fails on the base arm exactly as claimed.

### 1d. Instrument hashes re-measured

All nine frozen instrument hashes MATCH (`receipts/instrument-hashes.txt`): 51-row population `b066fa0f…`, items
`ce80195d…`, mutants `9368b342…` (10 members), pointer counter `fd0a8e24…`, harness `d6f4e612…`, clause battery
`b0c1472b…`, C2 counter `4e2b7c06…`, base tool `cf875367…`, writer `70bbf1c2…`; the filed tool itself measured
`0ad9e3bf…`.

**Verdict on the two arms: both re-derive exactly** — after `rows=12 mismatches=0 errors=0 EXIT=0`, before
`rows=12 mismatches=3 errors=0 EXIT=1`, the three before mismatches being KN1/KN2/KN3 and nothing else.

## 2. Six extra working-tree shapes, line arm vs `-z` arm

Every state was built on the frozen counter's own seed fixture (`rev e295278b…`; the committed C/D seed is
`rev2 5722ffa8…`) and both tools were run on the identical state. Record cells below are the tool's K4 `record` cell
(the path after C-escaping). Raw git status was captured as bytes.

| # | shape | line arm (base bytes) K4 | `-z` arm (filed bytes) K4 | difference | change invisible? |
|---|-------|--------------------------|---------------------------|------------|-------------------|
| 1a | staged rename, both ends (`git mv a.txt a-renamed.txt`) | 1 row `a.txt -> a-renamed.txt` / `R` | 1 row `a-renamed.txt` / `R` | `-z` names the destination; the second NUL field (source `a.txt`) is skipped — the disclosed limit | no |
| 1b | staged rename whose SOURCE has a space at byte 2 (`git mv "ab cd.txt" newname.txt`) | 1 row `ab cd.txt -> newname.txt` | 2 rows: `newname.txt`/`R` and a PHANTOM `cd.txt`/`ab` — the second NUL field (`ab cd.txt`) was NOT skipped | `-z` fabricates a record from the source path: false path, false class pair | no (extra row; nothing hidden) |
| 2 | ignored path (`.git/info/exclude` -> `ignored-here.txt`) | no row | no row | parity: `status` omits ignored paths in both forms | n/a (not status work) |
| 3 | submodule whose nested HEAD did NOT move (nested worktree dirty) | `nest` / `M` | `nest` / `M` | parity (control with nested HEAD moved behaves identically) | no |
| 4 | path carrying CR (`cr\rname.txt`, untracked) | `"cr\rname.txt"` (git C-quoted, 1 row) | `cr\nname.txt` / `??` (1 row) | CR is recorded as **`\n`**, not `\r` (see §3) | no (row present, but the path is wrong) |
| 5 | deleted tracked file (`sub/b.txt`) | `sub/b.txt` / `D` | `sub/b.txt` / `D` | parity | no |
| 6 | path carrying only a TAB (untracked file named `\t`) | `"\t"` (quoted) | `\t` (escaped, 2 characters) | both one physical record; `-z` gives the raw path, escaped | no |

Additional measured shapes (same fixture):

| shape | line arm | `-z` arm | note |
|-------|----------|-----------|------|
| unstaged rename (`a.txt` -> `a-moved.txt` on disk) | `a.txt`/`D` + `a-moved.txt`/`??` | same two rows | parity |
| tab inside a name (`tab\tname.txt`) | `"tab\tname.txt"` | `tab\tname.txt` | escaped, one record |
| newline inside a name (`ctl\nname.txt`) | `"ctl\nname.txt"` (git quoted spelling) | `ctl\nname.txt` (raw path, escaped) | the advertised fix; one record |
| path with a non-UTF-8 byte (`\xff-name.txt`, untracked) | `"\377-name.txt"` / `??` (1 row, counts line printed) | **CRASH: no K4 row, no counts line** | see F1 |
| CRLF inside a name (`crlf\r\nname.txt`) | `"crlf\r\nname.txt"` | `crlf\nname.txt` | CR lost (see F2) |
| leading+trailing space (` lead.txt `) | `" lead.txt "` | ` lead.txt ` | parity; `-z` does not strip, which is at least as faithful |
| vertical tab (0x0b) inside a name | `"vt\vname.txt"` | record cell carries the raw VT byte | disclosed limit ("another control byte still lands raw"); one LF-delimited record, but `str.splitlines()` consumers split it |

## 3. Escaping checks

* **Tab-only path** (`\t`): exactly one `MISMATCH\tK4` physical record, record cell `\t` (backslash + t).
  PASS — expected.
* **CR path** (`cr\rname.txt`): exactly one record, but the cell is `cr\nname.txt`, i.e. **the CR is not
  C-escaped as `\r`; it is recorded as `\n`**. Root cause: the tool's `git()` helper runs
  `subprocess.run(..., text=True)` (`tools/souji-record-agreement.py:139`), whose `_translate_newlines` rewrites
  `\r\n` and `\r` to `\n` while decoding, so the `.replace("\r", "\\r")` at line 478 can never fire for status
  output. Raw bytes were `?? cr\rname.txt\0`; the record cell is `cr\nname.txt`.
* Consequence measured side by side (`receipts/capture/B-collision.*`): three distinct untracked names —
  `x<LF>name.txt`, `x<CR>name.txt`, `x<backslash>nname.txt` — produce **three identical** `-z` cells
  `x\nname.txt`; the line arm keeps them distinct (`"x\nname.txt"`, `"x\rname.txt"`, `"x\\nname.txt"`).
  The escaping is non-injective and the CR path names a file that does not exist.
* The same text-mode translation also defeats the FORGED-detail escape at line 265: a stat-cache-forged
  tracked `cr\rname.txt` is correctly caught (`RECEIPT-WORKTREE-STAT-CONCEALED`, both arms) but its detail prints
  `(cr\nname.txt)`. That half is shared with the line arm (pre-existing, not `-z`-specific) — the status-record
  half is `-z`-specific.
* Physical-record result: both the tab-only and the CR path stay exactly one record; only the CR spelling is wrong.
* The stated limit "only newline, tab and CR are C-escaped, so another control byte still lands raw in the record"
  is accurate for other control bytes (VT measured) but inaccurate for CR: CR is not escaped, it is converted to LF.

## 4. Writer header and absent-writer behaviour

* Every filed-arm run prints exactly one header line:
  `# writer path=<realpath of beside-writer> sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa`,
  equal to the sha256 of `tools/souji-receipt-write.py`. KN2 in the after arm confirms the digest tracks bytes:
  appending one comment line changed the printed digest to `1b8ecf328ed3…`. (b) holds.
* Absent-writer copy (`receipts/extra/W-absent-writer.*`): a filed-tool copy in a kit with **no** writer beside it
  printed `# writer path=.../souji-receipt-write.py sha256=absent` and emitted
  `MISMATCH\tK4\t.\tstat-cache-concealed\tthe receipt writer is not beside this tool (...); tracked bytes are
  unverified`, plus the counts line, RC 1. K4 fails closed, no clean verdict.
* (c) KN1 also verified independently (see §1c).

## 5. Findings

**F1 — HIGH — the `-z` status read crashes on a non-UTF-8 path and publishes no K4 verdict; the uncommitted change
is invisible in the tool's output.**
Reproducer: in the seed fixture create an untracked file named `b"\xff-name.txt"`; run the filed tool
(`receipts/capture/A-invalid-utf8.z.*`). Raw git `-z` output is `?? \xff-name.txt\0`; the tool dies at
`git()`/`subprocess.run(text=True)` with
`UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 3: invalid start byte` (full traceback in
`A-invalid-utf8.z.stderr`). It prints only the 165-byte writer header: **no MISMATCH row, no counts line**; RC 1.
The lane-base line arm on the identical state records `MISMATCH\tK4\t"\377-name.txt"\tuncommitted-path\t??` and the
`keys=4 … mismatches=8` line (`A-invalid-utf8.line.stdout`). Because `k4()` aborts before `emit()` and before
`truth_refusal()`, a stat-cache- or index-flag-concealed change in the same tree would also go unreported. The
failure is loud (traceback, RC 1) but produces no verdict, so a genuine uncommitted change is not visible in K4
output; the r87 change (raw `-z` through a text-mode decoder) is the cause — the line form was safe only because git
C-quotes non-ASCII bytes by default. Repair direction (advisory): read the status as **bytes** and escape at the byte
level (or decode with `surrogateescape`); the writer's own `_status_z`/`_porcelain_paths` already does bytes.

**F2 — MEDIUM — the stated "CR is C-escaped" limit is false; CR paths are recorded as LF and the escaping is
non-injective.**
`cr\rname.txt` -> record cell `cr\nname.txt`; `crlf\r\nname.txt` -> `crlf\nname.txt`; CR, LF and literal
backslash-n names collide to one cell (§3). A CR-named change is still reported (row present, correct count), so this
is not the F1 invisibility class, but the record names a nonexistent path and two distinct paths can become
indistinguishable. Cause: `-` universal-newline translation inside `subprocess.run(text=True)` at line 139 (status
record) and line 254 (`truth_refusal` stdout, shared with the line arm).

**F3 — MEDIUM (claim wording) — "the -z form's second NUL field of a rename is skipped" is not true in general.**
The skip is a content heuristic (`len(rec) < 4 or rec[2:3] != " "`, line 476), not a record-structure rule. With a
staged rename whose source path has a space at byte 2 — `git mv "ab cd.txt" newname.txt` — raw `-z` is
`R  newname.txt\0ab cd.txt\0`; the second field passes the heuristic and the tool emits a phantom
`cd.txt` / `uncommitted-path` / `ab` row (`receipts/capture/C-rename-space.z.stdout`). No change is hidden (an extra
false row is added), but the stated parenthetical is falsified literally, and the false row can be silently dropped
if it happens to match an exemption prefix. The writer consumes the field structurally instead (status byte `R`/`C`,
`tools/souji-receipt-write.py:244-259`).

**F4 — INFO/positive.** Parity where the claim expects it: ignored path, submodule with nested HEAD unchanged (and
the moved-HEAD control), deleted tracked file, unstaged rename, newline path; tab escaping correct; header present
and digest-tracking; absent writer prints `sha256=absent` and fails closed; KN1 last-stderr-line verified.

### Claim-wording assessment (Amendment 59; the planner owns any narrowing)

The sealed 12-row counter re-derives on both arms, but this wave's own artifacts falsify parts of C2's STATED WORDING:
F2 falsifies "CR is C-escaped", F3 falsifies "the -z form's second NUL field of a rename is skipped" (as a general
statement), and F1 adds a `-z`-specific invisibility regression the counter does not cover. C2 should not be filed as
stated without narrowing these sentences; no lane instrument was edited by this seat.

## 6. Scratch disclosure

Scratch `/fast/scratch/hyaku/souji-r87/S87ExecC2/` (probe scripts, fixture clones, work dirs) is deleted before
yield; all receipts and the probe scripts are copied under `receipts/` with a `SHA256SUMS` manifest. Nothing was left
behind.

## 7. Follow-up (L1 request, same wave): repaired bytes re-derived, KB3 shape, copy case

SoujiR87 landed a repair in `tools/souji-record-agreement.py` (new bytes
`c2b0784e9000cba93bd36c8d646c44857dfbe9036f3fd4e3562c0b50cee55f59`, was `0ad9e3bf…`): `git_bytes()` keeps the
status stream as bytes (`tools/souji-record-agreement.py:142`), the status arm decodes each record with
`backslashreplace` and escapes at the record boundary (lines 485-510), and the rename/copy skip is now decided by the
status letters `R`/`C` with exactly one field consumed (lines 493-503) instead of the content test that produced F3.

Re-derived against those bytes (receipts under `receipts/followup/`):

* Frozen 12-row counter: `SUMMARY rows=12 mismatches=0 errors=0` / `EXIT=0` (`k4-repaired.out`) — the claim's
  counter contract is unchanged by the repair.
* `census/round-87/c2-byte-arm.py` on the repaired bytes: `SUMMARY rows=3 mismatches=0` / `EXIT=0`
  (`byte-after.out`); on the first-repair control `census/round-87/controls/c2-first-repair-tool.py` (sha256
  `0ad9e3bf…`): `SUMMARY rows=3 mismatches=3` / `EXIT=1` (`byte-before.out`). Both frozen byte-arm receipts
  re-derive exactly.
* **KB3 shape against my own repro** (independent fixture, staged rename whose source starts `ab `): repaired tool
  emits exactly one K4 row naming the destination and no phantom —
  `git mv "ab src.txt" dst.txt` -> `MISMATCH K4 dst.txt uncommitted-path R` (`R2-rename-ab-src.rep.stdout`);
  my original `git mv "ab cd.txt" newname.txt` -> `MISMATCH K4 newname.txt uncommitted-path R`
  (`R1-rename-ab-cd.rep.stdout`). The first-repair bytes emit the phantom `dir/src.txt|ab` / `cd.txt|ab` on the same
  states.
* **Copy case: the letters-based skip covers `C`.** `git status --porcelain -z` emits a copy record only when
  `status.renames=copies` is set in the repo config **and** the added file equals the modified source's pre-image
  (HEAD bytes); a copy of an *unmodified* source is still reported as plain `A` even with that config (while
  `git diff --cached -C --find-copies-harder` shows `C100`). Measured states:
  - `M  ab dir/src.txt\0C  dst.txt\0ab dir/src.txt\0`: repaired -> `ab dir/src.txt|M` + `dst.txt|C` (no phantom);
    first-repair -> the same two plus phantom `dir/src.txt|ab` (`copy-CP2-copy-ab-source.*`).
  - copy followed by an untracked record: raw `… C  dst.txt\0ab dir/src.txt\0?? zz.txt\0`; repaired reports
    `dst.txt|C`, `ab dir/src.txt|M`, `zz.txt|??` — exactly one field is skipped and the next real record is not
    eaten (no over-skip) (`copy-CP3-copy-ab-source-plus-untracked.*`).
  - `M  a.txt\0C  a-copy.txt\0a.txt\0` (source does not look like a status pair): repaired -> `a-copy.txt|C` +
    `a.txt|M` (`copy-CP1-copy-plain-source.*`).
* **F1/F2 re-check on the repaired bytes:** untracked `\xff-name.txt` -> one row `\xff-name.txt` + counts line;
  untracked `cr2\rname.txt` -> `cr2\rname.txt`; tab-only -> `\t`; newline -> `ctl\nname.txt`; the trio is now
  CR/LF-distinct (`F1-nonutf8`, `F2-cr`, `F2b-trio`, `E-tab-newline` receipts).

### Residuals on the repaired bytes (advisory, not regressions against the frozen 12-row contract)

* **R-1 (LOW): the manual escape is not injective for literal backslashes.** A path containing a real LF and a path
  containing the two characters `\` + `n` both record as `x\nname.txt` (likewise tab/CR); the line arm's git-quoted
  spelling distinguishes them (`"x\nname.txt"` vs `"x\\nname.txt"`). Escaping the backslash first would make the
  record a true C-escape.
* **R-2 (LOW, pre-existing): `truth_refusal` still reads the delegated writer's stdout with `text=True`, so the
  FORGED detail for a stat-cache-forged CR-named tracked file still prints `(cr\nname.txt)` while the status arm now
  prints `\r`** — the same name is spelled two ways inside one K4 key (`D-cr-forged.*`). This is shared with the
  line arm (the repair fixed the status arm only), so it is a carried defect, not a new one.

**Answer to the L1 ask: KB3's shape passes on my repro; the letters-based skip covers the copy (`C`) case as well as
`R`, consumes exactly one field, and does not eat a following record. The two residuals above are advisory.**
