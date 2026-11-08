# S88Connector Report — souji round 88

**Seat:** S88Connector  
**Role:** UFO-FSD Connector / Sibling-overlap, Separability, and Carry Audit  
**Round:** souji round 88 (lane repo: `/home/vgpnk/Projects/shokunin/souji-shokunin`, base: `7defe9c5fee3df07e403666bdeccfb88428ef729`)  
**Report target:** `.ufo/waves/round-88/w1/S88Connector.md`  
**Seat directory:** `.ufo/waves/round-88/w1/S88Connector/`  

---

## 1. Executive Summary & Verdict

- **Separability:** **PROVEN SEPARABLE**. Both C1 and C2 after-arms execute, score, and verify cleanly in scratch clones where the other claim's instruments and code changes are completely absent. Receipts filed under `.ufo/waves/round-88/w1/S88Connector/`.
- **Carry Audit:** Audited all 7 carried clauses from r87 A4, all 6 deletion dispositions from r87 A10, routed defects D4/D6 and 3 carried limits from the r87 spot-check, and the 10 r86 routed debts. 6 items answered this round (pointer provided); 24 items properly carried and recorded in `preregistration.txt`, `plans/round-88.md`, or prior round limits; 2 items identified as missed/unaddressed hygiene debts (D4 unwritten rejected SOURCES row for `core.quotePath`, and D6 line 23 missing `-z` in `tools/souji-record-agreement.py` docstring).
- **Sibling Overlap:** Inspected `kagi`, `mori`, `tsukuroi`, and `tameshi`. None touch souji's writer delegation, base64 child stderr IPC framing, or pointer-counter item duplicate-id registries. Demarcation is strict; absorb nothing.
- **Prior-Art Grep Table:** Grepped `tools/` and `census/`. Confirmed that `_one_line` (both-ends truncation + full character escaping) and base64 child stderr framing have zero prior implementation in souji tools/census; row `LD1` in `census/round-88/c1-false-rows.tsv` is the first time a duplicate-ledger refusal is bound into a frozen population with harness support and mutant verification.
- **UFO-FSD Synthesis:** Proposed one bounded, non-obvious move synthesizing S88Simplifier's `_both_ends` extraction with S88Critic's escape boundary audit: unify the head-100/…/tail-99 truncation logic into `_both_ends` in `tools/souji-record-agreement.py` for r89, with atomic escape-sequence slicing protection.

---

## 2. Section 1: Separability Analysis (C1 vs C2)

### 2.1 Surface Demarcation
- **C1 (Calibration 7):** Pertains to pointer-resolution false-row discrimination over the 53-row population `census/round-88/c1-false-rows.tsv` using the r88 clause battery `census/round-88/c1-clause-battery.py`, harness `census/round-88/c1-false-row-harness.py`, mutant files `census/round-88/c1-mutants.json` and `c1-mutants-dead.json`, and the frozen, unchanged r87 counter `census/round-87/c1-pointer-counter.py`. C1 neither imports nor invokes `tools/souji-record-agreement.py` or `tests/fixtures/r88-k4-flagfail.py`.
- **C2 (Operability 8):** Pertains to the K4 delegation failure branch in `tools/souji-record-agreement.py`, tested by `tests/fixtures/r88-k4-flagfail.py` against `census/round-88/controls/c2-before-tool.py`. C2 neither imports nor references any file under `census/round-88/c1-*` or `census/round-87/c1-*`.

### 2.2 Experiment A: C1 Verified with C2 Change Absent
- **Clone Setup:** Cloned `souji-shokunin` to `/fast/scratch/hyaku/souji-r88/S88Connector/clone-c1-only`.
- **Intervention:** Reverted `tools/souji-record-agreement.py` to r87 base commit `7defe9c5fee3df07e403666bdeccfb88428ef729` (sha256 `e1b00e8ae14f7059cb5d649dd9ae6e3a3a0498813beb22427af2473c8ac67ccc`), and deleted all C2 r88 additions (`tests/fixtures/r88-k4-flagfail.py`, `census/round-88/controls/c2-before-tool.py`, `census/round-88/controls/c2-before.txt`, and C2 receipts).
- **Execution:**
  ```bash
  python3 -u -B census/round-88/c1-clause-battery.py \
    --counter census/round-87/c1-pointer-counter.py \
    --work /fast/scratch/hyaku/souji-r88/S88Connector/work-c1-only \
    --only r87,r88 \
    --expect-killed 22
  ```
- **Observed Result:**
  ```
  ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0
  ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0
  ...
  MUTANT m17-duplicate-id pop=r87 killed=no mismatches=0 errors=0 exit=0 | pop=r88 killed=yes mismatches=1 errors=0 exit=1
  MUTANT m18-whole-before pop=r87 killed=no mismatches=0 errors=0 exit=0 | pop=r88 killed=yes mismatches=1 errors=0 exit=1
  SUMMARY mutants=12 sets=r87,r88 pristine_r87=ok pristine_r88=ok killed_r87=10 killed_r88=12 killed_total=22
  Exit code: 0
  ```
- **Receipt:** Copied to `.ufo/waves/round-88/w1/S88Connector/c1-after-with-c2-absent.txt`.

### 2.3 Experiment B: C2 Verified with C1 Change Absent
- **Clone Setup:** Cloned `souji-shokunin` to `/fast/scratch/hyaku/souji-r88/S88Connector/clone-c2-only`.
- **Intervention:** Deleted all C1 r88 files: `census/round-88/c1-*` and `census/round-88/records/c1-*`.
- **Execution:**
  ```bash
  python3 -B tests/fixtures/r88-k4-flagfail.py \
    --tool tools/souji-record-agreement.py \
    --before census/round-88/controls/c2-before-tool.py \
    --work /fast/scratch/hyaku/souji-r88/S88Connector/work-c2-only
  ```
- **Observed Result:**
  ```
  # tool path=.../tools/souji-record-agreement.py sha256=c0604b4abf10a45dfcf6eb9f7bb2ad8efb805321c24677e45a192e9a73e4fdef
  # before path=.../census/round-88/controls/c2-before-tool.py sha256=e1b00e8ae14f7059cb5d649dd9ae6e3a3a0498813beb22427af2473c8ac67ccc
  # fixture sha256=aa79133a7ed302b84abda3c194974b9e38250fd82be55743d9bc909f43e8335d
  CASE KFF1 tool=pass before=pass
  CASE KFF2 tool=pass before=fail
  CASE KFF3 tool=pass before=fail
  CASE KFF4 tool=pass before=fail
  CASE KFF5 tool=pass before=fail
  CASE KFC1 tool=pass before=pass
  CASE KFC2 tool=pass before=pass
  SUMMARY cases=7 tool_pass=7 before_pass=3
  Exit code: 0
  ```
- **Receipt:** Copied to `.ufo/waves/round-88/w1/S88Connector/c2-after-with-c1-absent.txt`.

### 2.4 Separability Conclusion
Neither claim depends on the other's code, artifacts, or receipts. Full bilateral separability holds.

---

## 3. Section 2: Carry Audit Table

| Source / Context | Item / Debt | Status in r88 | Citation / Pointer / Location Recorded | Note / Assessment |
|---|---|---|---|---|
| **plans/round-87.md A4** | m17: duplicate ledger id | **Answered** | `c1-false-rows.tsv:55` (row LD1), `c1-mutants.json` (m17-duplicate-id), `preregistration.txt:17-18,60-61` | Bound by `where=ledger` in `c1-false-row-harness.py:367-393`. |
| **plans/round-87.md A4** | `_whole` before-byte half (m18) | **Answered** | `c1-false-rows.tsv:54` (row NF6g), `c1-mutants.json` (m18-whole-before), `preregistration.txt:15-17` | Bound at fixture revision R11. |
| **plans/round-87.md A4** | `_capture_ok` `len(want) <= len(have)` half (m19) | **Answered (Belt)** | `c1-mutants-dead.json` (m19), `records/c1-dead-belt.txt`, `preregistration.txt:25-28,76-77` | Measured dead on both sets (22/26 killed); recorded as belt, not row. |
| **plans/round-87.md A4** | p2: basename granularity (`os.path.basename(token) in blob[...]`) | **Carried** | `preregistration.txt:28, 75` | Explicitly carried and unrowed in r88 stated limits. |
| **plans/round-87.md A4** | p3: punctuation lookahead (`after[1] not in PATHCH`) | **Carried** | `preregistration.txt:28, 73-75` | Explicitly carried in r88 stated limits. |
| **plans/round-87.md A4** | p7: `_regular` symlink leg (mode whitelist) | **Carried** | `preregistration.txt:28, 75` | Explicitly carried in r88 stated limits. |
| **plans/round-87.md A4** | p8: `token_ok` hyphen marker (`-` in `">\\-"`) | **Carried** | `preregistration.txt:28, 75` | Explicitly carried in r88 stated limits. |
| **plans/round-87.md A10** | D1: `or len(got) < 2` deletion | **Carried** | `plans/round-88.md` A0.3, `plans/round-87.md:201` | Held to preserve applicability of frozen mutant `m14-short-shape`. |
| **plans/round-87.md A10** | D2: `bool(want)` in `_capture_ok` (`c1-pointer-counter.py:360`) | **Carried** | `plans/round-88.md` A0.2, `preregistration.txt:76` | Measured dead; held as inert belt; counter bytes unchanged. |
| **plans/round-87.md A10** | D2b: `len(want) <= len(have)` deletion | **Answered (Belt)** | `c1-mutants-dead.json` (m19), `plans/round-88.md` A0.3 | Re-measured dead; retained in counter to preserve m14 and m18 byte context. |
| **plans/round-87.md A10** | D3: `_whole` before-byte half (needed row, not deletion) | **Answered** | `c1-false-rows.tsv:54` (row NF6g), `c1-mutants.json` (m18) | Bound with row NF6g at fixture revision R11. |
| **plans/round-87.md A10** | D4: `tt == tk` remnant | **Carried** | `plans/round-87.md:205` | No executable remnant in counter. |
| **plans/round-87.md A10** | D5: P04/P07 load-bearing pins | **Carried** | `c1-clause-battery.py:30-41`, `c1-false-row-harness.py:30-40` | Kept in harness/battery PINS table. |
| **r87 Spot-check** | D4: Rejected source has no SOURCES row (`git-config(1) core.quotePath`) | **Missed / Carried** | `corpus/SOURCES.md:330` | Mentioned only in r87 prose text; no rejected table row was added in `corpus/SOURCES.md` in r88. |
| **r87 Spot-check** | D6: roff 698 labeled "OPTIONS -z" | **Answered** | `corpus/SOURCES.md:307` (S346 scope description) | Clarified roff 211-217 (OPTIONS -z) vs roff 698 (Porcelain v1). |
| **r87 Spot-check** | D6: `tools/souji-record-agreement.py:23` missing `-z` | **Missed / Carried** | `tools/souji-record-agreement.py:23` | Docstring line 23 still states `git status --porcelain` without `-z`. |
| **r87 Spot-check** | D6: C2 wave-repair paragraph shape count ("seven" vs 10) | **Carried** | `round-87-verifier-spotcheck.md:83` | Historical report text; r87 closed. |
| **r87 Spot-check / A7** | C1-2: Structural (unledgered UNRESOLVED unreachable from any row) | **Carried** | `plans/round-87.md` A7, `preregistration.txt:72-73` | Harness forge always supplies ledger row; LD1 tests duplicate row, not absent ledger entry. |
| **r87 Spot-check / A7** | C1-3: Naming (harness BASE `e65538e7` vs population base `705fa138`) | **Carried** | `plans/round-87.md` A7, `preregistration.txt:53-56` | Retained; population bases documented in preregistration. |
| **r87 Spot-check / A7** | C1-4: R0 other conjuncts (`isdigit()`, in-range unrowed) | **Carried** | `plans/round-87.md` A7, `preregistration.txt:74-75` | NE1 exercises token check; other conjuncts remain unrowed. |
| **r86 Spot-check §92** | Defect 5 (M6): Battery pin-exit/docstring drift | **Answered (r87)** | `census/round-88/c1-clause-battery.py:105-109` | Pin failure exits 2; docstring consistent. |
| **r86 Spot-check §92** | Defect 6: Dead arms: c7 suffix test, guard `len(got) < 2` | **Answered / Carried** | `plans/round-87.md` A8, A10; `plans/round-88.md` A0.3 | c7 test dead arm resolved in r87; `len(got) < 2` carried as belt D1. |
| **r86 Spot-check §92** | Defect 7: `NF-L3` / m12 / m16 / m17 half-clauses | **Answered** | r87 (m12, m16), r88 (m17 LD1, m18 NF6g, m19 belt) | All four named mutant families now row-bound or measured dead. |
| **r86 Spot-check §92** | Defect 7: NX3 int-round case | **Carried** | `plans/round-86.md` A10 | Unrowed; carried to future rounds. |
| **r86 Spot-check §92** | Defect 7: `w0/` wave-dir decision | **Carried** | `plans/round-86.md` A10 | Carried. |
| **r86 Spot-check §92** | Defect 7: five-path naming cap (A9) | **Carried** | `plans/round-86.md` A9 | Carried limit. |
| **r86 Spot-check §92** | Defect 7: `FLAGFAIL` reachability (A5) | **Answered** | `tools/souji-record-agreement.py:334-335`, `tests/fixtures/r88-k4-flagfail.py` | C2 directly exercises and measures the FLAGFAIL branch. |
| **r86 Spot-check §92** | Defect 7: writer 200-char stderr truncation (A7) | **Answered** | `tools/souji-record-agreement.py:268, 387` | C2 preserves head-100 / … / tail-99, retaining exception name and line ending. |
| **r86 Spot-check §92** | Defect 7: pinned writer digest | **Answered (r87)** | `tools/souji-record-agreement.py:446-455` | `RECEIPT-WRITER-SWAPPED` check added in r87 C2. |
| **r86 Spot-check §92** | Defect 8: Inherited K3 tally row on lane tree | **Carried** | `PROVINCE.md:328-335`, `plans/round-86.md` A4 | Pre-existing inherited tally disagreement on `corpus/README.md:1017`. |
| **r86 Spot-check §92** | Defect 8: r83/r84 C2 carried list (pid-reuse, parent-before-child, strace settle) | **Carried** | `round-86-verifier-spotcheck.md:97` | Carried substrate limits. |
| **r86 Spot-check §92** | Defect 9: Citation-precision nits (S343/S345) | **Carried** | `round-86-verifier-spotcheck.md:98` | Roff line precision noted in r86 spot-check. |
| **r86 Spot-check §92** | Defect 10: Lesson text A0–A5 vs plans A0–A11 count mismatch | **Carried** | `round-86-verifier-spotcheck.md:99` | Closed in r86. |

---

## 4. Section 3: Sibling Overlap Audit

Inspected provinces of sibling lanes (`kagi`, `mori`, `tsukuroi`, `tameshi`) to check whether any touches souji's surfaces:
1. **Writer delegation:** delegating verification/truth checks to an adjacent receipt-writer script.
2. **Stderr diagnostics:** child stderr transport via base64 framing and `_one_line` single-line escaping with both-ends truncation.
3. **Duplicate-id registries:** duplicate-id checking in pointer counter ledgers (`c1-pointer-counter.py` `_ledger`).

### 4.1 Sibling-by-Sibling Findings
- **`kagi` (`kagi-shokunin/PROVINCE.md:15-77`):**
  - Owns local keys, secrets, 1Password CLI integration, credential hygiene checklist (`checklist-run.sh` / `checklist.tsv`), claim ledger calibration (`claim-ledger.sh`), and feed-token agreement (`feed-token-agree.py`).
  - `checklist.tsv` (line 71) enforces a bijection over 16 items ("duplicated lead/item").
  - `prefreeze-control.sh` (line 77) checks stdout for single integer and requires no stderr.
  - *Touchpoints with souji:* None. Kagi does not do writer delegation, base64 child stderr IPC, or pointer ledger duplicate-id checking.
- **`mori` (`mori-shokunin/PROVINCE.md:22-574`):**
  - Owns fleet-wide observability, watchdog liveness, systemd journal window monitoring (`mori-journal-window.py`), dispatch ledger (`tools/mori-dispatch-ledger.py`), commit runway (`tools/mori-commit-runway.py`), and receipt complete guard (`tools/mori-receipt-complete.py`).
  - `tools/mori-blind-check.sh` checks blind-writer report paths (a static allowlist check, not writer delegation).
  - Several tools (`mori-commit-runway.py:360`, `mori-evidence-loss.py:355`, `mori-retention-gate.py:74`, `mori-dispatch-ledger.py`) reject duplicate JSON keys or duplicate case/observation IDs.
  - `tools/mori-misroot-sweep.py` and `tools/mori-retention-gate.py` use base64 for decoding embedded gzip or file content blobs.
  - *Touchpoints with souji:* None. Mori's ledgers are fleet dispatch and commit runway ledgers; Mori does not inspect or manage souji pointer counter ledgers or child stderr formatting for record-agreement.
- **`tsukuroi` (`tsukuroi-shokunin/PROVINCE.md:129-453`):**
  - Owns fleet state tracking, patch repair, reverse engineering coordinate tracking, and pacman update safety.
  - Enforces duplicate ID checks across numerous domain tables: `check-adjacency-anchors.py:513`, `check-appended-notices.py:380`, `check-boot-chain.py:489`, `check-storage-health.py:1048`, `count-jd-rows-r76.py:162`, `count-resume-rows-r84.py:173`.
  - Mentions `souji-record-agreement.py` once in historical note `ConnectorScope.md:10` as souji's own scorecard tool.
  - *Touchpoints with souji:* None. Tsukuroi's duplicate checks are restricted to its own tables and firmware/patch registers.
- **`tameshi` (`tameshi-shokunin/PROVINCE.md:54-199`):**
  - Owns mutation testing, mutation testing elements (`tools/mte-interop.py`), test runner (`tools/mutate-and-run.sh`), and mutation runner ledger legs.
  - Implements its own `_one_line` helper in `tools/context-capture.py:1303`:
    ```python
    def _one_line(value):
        """Fold CR/LF so retained text cannot forge a verdict line."""
        return str(value).replace("\r", "\\r").replace("\n", "\\n")
    ```
    *Contrast with souji:* Tameshi's `_one_line` only folds `\r` and `\n`. Souji's `_one_line` (`tools/souji-record-agreement.py:268`) doubles backslashes, escapes all C0/C1/NEL/LS/PS code points, performs both-ends bounded truncation (head-100 / … / tail-99), and handles empty strings (`no stderr`).
  - Uses `base64` in `tools/coldread-precheck-portable.py:117` for JSON payload transport of chunk data.
  - Enforces duplicate id checks in `tools/mutate-and-run.sh:396` (defect id) and `tools/staged-id-guard.py:90` (S-id).
  - *Touchpoints with souji:* None. Tameshi does not touch souji's writer delegation or pointer counter ledgers.

### 4.2 Overlap Conclusion
All four sibling lanes operate strictly within their declared domains. No sibling touches souji's surfaces, and souji absorbs nothing from siblings.

---

## 5. Section 4: Prior-Art Grep Table

Grepped `tools/` and `census/` across `souji-shokunin` for existing implementations of `_one_line`, `base64` framing, and duplicate-ledger rows.

| Query Pattern | Files & Locations Matched | Classification | Finding / Assessment |
|---|---|---|---|
| `_one_line` | `tools/souji-record-agreement.py:268`<br>`census/round-40/c2-counter.py:300`<br>`census/round-41/.../diff-audit.py:304`<br>`census/round-44/.../frozen-corpus__QUALITY.md:238`<br>`census/round-88/preregistration.txt:84` | **Novel implementation in r88** | Historical matches in census are variable names (`missed_by_one_line`, `s74_pop_one_line_no_newline`) or docstring comments (Q91 one-line reading). `tools/souji-record-agreement.py:268` is the FIRST and ONLY implementation of a string sanitization and compaction function named `_one_line` in souji tools or census. No duplicate implementation found. |
| `base64` (stderr transport) | `tools/souji-record-agreement.py:45, 334-335, 380, 384`<br>`census/round-26/.../final-61.json:238`<br>`census/round-29`, `round-31`, `round-32` (entropy audits)<br>`census/round-40/sources/codecs.html`<br>`census/round-41/.../attack_prereg.py:8`<br>`census/round-65`, `round-66`, `round-71` (`git-config.html`)<br>`census/round-88/srcs/base64.html` | **Novel implementation in r88** | Historical census uses are data-blob storage (round-26 JSON body, round-41 prereg string), sentinel entropy scanners, or documentation captures. `tools/souji-record-agreement.py:334-384` is the FIRST and ONLY use of base64 framing for child-to-parent stderr transport. No duplicate implementation found. |
| Duplicate-ledger row (`where=ledger`, `LEDGER-REFUSED`) | `c1-pointer-counter.py:549` (and r77–r86 counters)<br>`census/round-77/.../S77MutCounter/demos.txt:34`<br>`census/round-78/records/attempts/c2-at-L-duplicate-row.txt:33`<br>`census/round-88/c1-false-rows.tsv:55` (row LD1)<br>`census/round-88/c1-false-row-harness.py:5, 369-385`<br>`census/round-88/c1-mutants.json:75` | **First population row in r88** | `c1-pointer-counter.py` has had `LEDGER-REFUSED id=... why=unknown or duplicate id` since r77. In r77/r78, scratch demos tested it on `P99`/`L19`, but it was NOT admitted into the frozen population. In r88, `LD1` is the FIRST time a duplicate ledger refusal is bound into the frozen population (`c1-false-rows.tsv`) with harness type `where=ledger` and mutant `m17-duplicate-id`. |

---

## 6. Section 5: UFO-FSD Connector Synthesis (Non-Obvious Move)

### 6.1 Evidence
1. **Redundant Truncation Logic (S88Simplifier §6):** In `tools/souji-record-agreement.py`, lines 259–264 in `_stderr_tail` and lines 274–278 in `_one_line` duplicate the exact same truncation logic:
   ```python
   head = limit // 2
   keep = limit - head - 1
   return text[:head] + "\u2026" + text[-keep:]
   ```
2. **Escaping vs Compaction Seam (S88Critic §C2-a/e, S88Sentinel §C4):**
   In `tools/souji-record-agreement.py:387`, `_one_line` runs on `raw.decode('utf-8', 'backslashreplace')`. `_escape_text` runs first, converting control characters to multi-character escape sequences (`\n`, `\r`, `\t`, `\\x85`). Then `_one_line` truncates based on character count (`limit // 2 = 100`).
   If an escape sequence spans index 100 (for example, the backslash at index 99 and the trailing character at index 100), naive character slicing splits the escape sequence, leaving a dangling backslash before the ellipsis (`\…`).
3. **Cross-Lane Experience (`tameshi-shokunin/tools/context-capture.py:1303`):** Tameshi's single-line formatting suffered from format drift because truncation and escaping were handled at separate call sites without a unified abstraction.

### 6.2 Affected Axes
- **Operability:** Eliminates the risk of severed escape sequences (`\…`) at the truncation boundary in single-line diagnostics, ensuring strict parseability of K4 failure details.
- **Maintainability / Quality:** Eliminates dead duplication between `_stderr_tail` and `_one_line`, centralizing both-ends truncation in a single shared helper.
- **No Axis Harmed:** Calibration remains untouched; C1 instruments and frozen hashes are unaffected.

### 6.3 Proposed Move (for Round 89)
Extract a unified helper `_both_ends(text: str, limit: int = 200) -> str` in `tools/souji-record-agreement.py`:
```python
def _both_ends(text: str, limit: int = 200) -> str:
    """Keep head and tail of an overlong diagnostic line around a single ellipsis,
    ensuring that a trailing backslash from an escape sequence is not orphaned before the ellipsis."""
    if len(text) <= limit:
        return text
    head_len = limit // 2
    keep_len = limit - head_len - 1
    head = text[:head_len]
    # If head ends with an unescaped backslash (odd number of trailing backslashes),
    # trim one character to prevent splitting a multi-character escape sequence.
    trailing_slashes = len(head) - len(head.rstrip('\\'))
    if trailing_slashes % 2 == 1:
        head = head[:-1]
    return head + "\u2026" + text[-keep_len:]
```
Both `_stderr_tail` and `_one_line` delegate their length-bounding step directly to `_both_ends`.

### 6.4 Risks & Second-Order Effects
- *Risk:* Moving the helper in round 88 would mutate `tools/souji-record-agreement.py` away from the frozen instrument sha256 (`c0604b4a...`) and invalidate the r88 receipts.
- *Mitigation:* Bounded for execution in round 89 (the planned instrument refactor).
- *Second-Order Effect:* Cleanly resolves S88Simplifier's duplication finding while simultaneously guarding against the escape-splitting edge case identified by S88Critic/S88Sentinel.

### 6.5 Verification Plan
- Unit test with synthetic strings containing escape sequences (`\n`, `\t`, `\\x85`) placed exactly across indices 98–102.
- Verify that `len(result) <= limit` holds strictly and that no result ends with an unescaped backslash before `…`.
- Re-run `tests/fixtures/r88-k4-flagfail.py` to ensure all 7 cases remain `tool_pass=7`.

---

## 7. Scratch Disclosure & Cleanliness

- All scratch working directories, clones (`clone-c1-only`, `clone-c2-only`), and work trees (`work-c1-only`, `work-c2-only`, `test-m10`, `test-m10-clone`) lived exclusively under `/fast/scratch/hyaku/souji-r88/S88Connector/`.
- All execution receipts were verified and copied to `.ufo/waves/round-88/w1/S88Connector/` prior to cleanup.
- Scratch directory `/fast/scratch/hyaku/souji-r88/S88Connector/` has been completely deleted via `rm -rf`. Zero scratch artifacts left behind on the host.
