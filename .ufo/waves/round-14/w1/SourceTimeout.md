# Scoped Source Report: GNU Coreutils `timeout` Documentation Re-derivation (S038 Correction of S034)

**Seat**: `SoujiR14.SourceTimeout` (Scout)  
**Lane**: `/home/vgpnk/Projects/shokunin/souji-shokunin`  
**Wave**: Round 14 / Wave 1  
**Report Path**: `.ufo/waves/round-14/w1/SourceTimeout.md`  
**Target**: Re-derive S034 corrected quote line numbers and exit 124 location from installed vendor `/usr/share/info/coreutils.info.gz` (timeout invocation node only via `gzip` in `eval`), record `timeout --version`, provide immutable S038 correction row text with $\le 25$-word located quote and access date, identify final L1 commands without editing registry.

---

## 1. Godspeed Posture & Axes

1. **Name the axes**:
   - **Calibration**: Precision and veracity of textual grounding; exact line numbers for vendor citations; zero quote drift; transparent separation of vendor facts from downstream operational inferences; strict conformance to `SOURCES-CONTRACT-v1` with zero `PENDING` cells.
   - **Operability**: Definitive determination of `timeout` exit semantics (124 timeout, 125 internal failure, 126 uninvokable command, 127 command not found, 137 `KILL(9)` signal) and secondary kill mechanics (`-k` / `--kill-after`) to ensure process bounding in souji tooling never masks failure or causes hangs.
2. **Iterate cheap, in parallel**:
   - Decompressed `/usr/share/info/coreutils.info.gz` and `/usr/share/man/man1/timeout.1.gz` in-process via Python `gzip` in `eval`; inspected line-by-line boundaries of node `timeout invocation` without touching external networks or unneeded files.
3. **Keep moves that improve any axis and harm none**:
   - Re-derived exact line numbers correcting S034 errors (15319–15320 for KILL quote vs flawed 15316–15317; 15365 for exit 124 vs flawed 15349); preserved immutability of historical S034 by specifying append-only superseding S038 row.
4. **Don't aim — let the frontier walk itself**:
   - Grounded all findings directly in installed vendor artifacts; no assumptions, no credential access, no registry edits.

---

## 2. Vendor Source & Version Verification (Exercised Evidence)

### 2.1 Execution of `timeout --version`
Executed `timeout --version` on host:
```text
timeout (GNU coreutils) 9.11
Copyright (C) 2026 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Written by Pádraig Brady.
```
- **Binary Version**: GNU `timeout` 9.11
- **Installed Package**: `coreutils 9.11-2` (verified via `pacman -Q coreutils`)
- **Installed Info Documentation**: `/usr/share/info/coreutils.info.gz`
  - Total decompressed lines: 23,832
  - SHA256: `e9d00f9ee22f5fa0b3284ca28129300aa62973105464ba9556ee02635bd1b6dc`
  - Size: 263,279 bytes
- **Installed Man Documentation**: `/usr/share/man/man1/timeout.1.gz`
  - Total decompressed lines: 92
  - Header: `.TH TIMEOUT "1" "July 2026" "GNU coreutils 9.11" "User Commands"`

---

## 3. Re-derivation of Node `timeout invocation` (Lines 15284–15399)

The node `timeout invocation` starts at line 15284 and ends at line 15399 of `/usr/share/info/coreutils.info.gz`.

### 3.1 Line Number Re-derivation & Root Cause Analysis of S034 Flaws

| Feature | S034 Citation (Flawed) | Actual Re-derived Location | Observed Content at Actual Line | Analysis / Reason for S034 Defect |
|---|---|---|---|---|
| **Node Heading** | § 23.6 | Line 15286 | `23.6 ‘timeout’: Run a command with a time limit` | Section heading confirmed. |
| **`--kill-after` Header** | 15316–15317 | Lines 15317–15318 | `15317: ‘-k DURATION’`<br>`15318: ‘--kill-after=DURATION’` | Line 15316 was completely blank; line 15317 was the short option flag. |
| **`--kill-after` KILL Quote** | 15316–15317 | **Lines 15319–15320** | `15319:      Ensure the monitored COMMAND is killed by also sending a ‘KILL’`<br>`15320:      signal.` | **Locator Error (+3 lines)**: Quote was accurate, but lines in S034 pointed to blank/option lines instead of sentence text. |
| **`--verbose` Diagnostic** | *[Misidentified as exit status]* | **Line 15349** | `15349:      Diagnose to standard error, any signal sent upon timeout.` | **Misidentification**: Line 15349 is under `-v` / `--verbose`, NOT Exit status. |
| **Exit Status Heading** | *[Not isolated]* | **Line 15363** | `15363:    Exit status:` | Exit status block begins here. |
| **Exit Status 124** | 15349 | **Line 15365** | `15365:      124 if COMMAND times out, and ‘--preserve-status’ is not specified` | **Locator Error (+16 lines)**: Exit 124 is at 15365, not 15349. |
| **Exit Status 125** | — | Line 15366 | `15366:      125 if ‘timeout’ itself fails` | Diagnostic / internal failure code. |
| **Exit Status 126** | — | Line 15367 | `15367:      126 if COMMAND is found but cannot be invoked` | Invocation failure. |
| **Exit Status 127** | — | Line 15368 | `15368:      127 if COMMAND cannot be found` | Command not found. |
| **Exit Status 137** | — | Line 15369 | `15369:      137 if COMMAND or ‘timeout’ is sent the KILL(9) signal (128+9)` | `KILL(9)` signal termination. |

### 3.2 Cross-Check with `timeout(1)` Roff Source (`/usr/share/man/man1/timeout.1.gz`)
- **Lines 20–22**:
  ```roff
  20: \X'tty: link https://www.gnu.org/software/coreutils/manual/coreutils.html#timeout-k'\fB\-k, \-\-kill\-after=\,DURATION\fP\X'tty: link'\/\fR
  21: also send a KILL signal if COMMAND is still running
  22: this long after the initial signal was sent
  ```
- **Lines 51–52**:
  ```roff
  51: 124
  52: if COMMAND times out, and \fB\-\-preserve\-status\fR is not specified
  ```

---

## 4. Located Quotes ($\le 25$ Words) & Access Date

### 4.1 Primary Located Quote (KILL Signal under `--kill-after`)
- **Access Date**: `2026-10-20`
- **Location**: `/usr/share/info/coreutils.info.gz`, lines 15319–15320 (Node `timeout invocation`, § 23.6); cross-checked with `timeout(1)` roff lines 20–22.
- **Located Quote**:
  > “Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal.”
- **Word Count**: **12 words** ($\le 25$ words).

### 4.2 Secondary Located Quote (Exit Status 124)
- **Access Date**: `2026-10-20`
- **Location**: `/usr/share/info/coreutils.info.gz`, line 15365 (Node `timeout invocation`, § 23.6, Exit status); cross-checked with `timeout(1)` roff lines 51–52.
- **Located Quote**:
  > “124 if COMMAND times out, and ‘--preserve-status’ is not specified”
- **Word Count**: **10 words** ($\le 25$ words).

### 4.3 Combined Exit Context Quote
- **Access Date**: `2026-10-20`
- **Location**: `/usr/share/info/coreutils.info.gz`, lines 15363–15365.
- **Located Quote**:
  > “Exit status: 124 if COMMAND times out, and ‘--preserve-status’ is not specified”
- **Word Count**: **12 words** ($\le 25$ words).

---

## 5. S038 Immutable Correction Row Text

Historical rows in `corpus/SOURCES.md` are immutable per the contract rules (`SOURCES-CONTRACT-v1`). S034 remains intact; S038 is appended as the immutable correction row superseding S034 line citations.

### 5.1 Proposed Row Specification (Standard URL Variant — Aligned with S035/S036)

```markdown
| S038 | GNU timeout(1), installed coreutils 9.11 manual — https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html | docs | A | timeout exit 124 and --kill-after KILL on coreutils 9.11-2; citation correction superseding S034 locator | /usr/share/info/coreutils.info.gz node timeout invocation § 23.6, --kill-after lines 15319-15320, Exit status line 15365; timeout(1) roff 20-22,51-52 | supersedes S034 — exits 124 on timeout without preserve-status; kill-after sends a secondary KILL; corrects line citations (KILL sentence lines 15319-15320, exit 124 line 15365, not 15316-15317 or 15349) | mined | 2026-10-20 | on-release | corpus/lessons/round-13.md |
```

#### Field Verification Checklist (11 Cells / 13 Split Parts)
1. `id`: `S038` (Next unused sequential id after S037; conforms to `^S[0-9]{3,}$`).
2. `source`: `GNU timeout(1), installed coreutils 9.11 manual — https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html`
3. `kind`: `docs` (Valid enum).
4. `tier`: `A` (Authoritative vendor manual for core OS utility; valid enum).
5. `scope`: `timeout exit 124 and --kill-after KILL on coreutils 9.11-2; citation correction superseding S034 locator`
6. `anchor`: `/usr/share/info/coreutils.info.gz node timeout invocation § 23.6, --kill-after lines 15319-15320, Exit status line 15365; timeout(1) roff 20-22,51-52`
7. `teaches`: `supersedes S034 — exits 124 on timeout without preserve-status; kill-after sends a secondary KILL; corrects line citations (KILL sentence lines 15319-15320, exit 124 line 15365, not 15316-15317 or 15349)`  
   *(Contains `supersedes S034`, preventing `E04` duplicate URL error in fleet validator)*.
8. `status`: `mined` (Valid enum).
9. `opened`: `2026-10-20` (Valid ISO date, $\le \text{today}$).
10. `recheck`: `on-release` (Valid symbolic cadence).
11. `used-by`: `corpus/lessons/round-13.md` (Path exists in baseline `a31642d`, passing `E11` existence check).

### 5.2 Alternative Row Specification (URL-Free Variant — Aligned with SourceLedger.md)
If L1 prefers avoiding advisory `W04` ("duplicate url across scopes"):
```markdown
| S038 | GNU coreutils info, node timeout invocation, installed coreutils 9.11-2 (/usr/share/info/coreutils.info.gz) — correction of S034 locator | docs | A | timeout exit 124 and --kill-after KILL on coreutils 9.11-2; supersedes S034 line citations only | /usr/share/info/coreutils.info.gz § 23.6 heading line 15286; -k/--kill-after header 15317-15318 and KILL sentence 15319-15320; -v verbose line 15349; Exit status heading 15363 and code 124 at 15365; timeout(1) roff /usr/share/man/man1/timeout.1.gz lines 20-22, 51-52 | corrects S034 locator only: KILL sentence at 15319-15320, exit 124 at 15365, not 15316-15317 or 15349 (15349 is -v); exits 124 without preserve-status; kill-after sends a secondary KILL; residue and no-deletion claims are not in this vendor text and are not taught here | mined | 2026-10-20 | on-release | corpus/lessons/round-13.md |
```

### 5.3 Teaches Scope Clarification (Calibration Note)
In round 13 S034, the teaches cell stated: *"interruption can leave operation residue and does not authorize deletion"*.  
Our audit of `/usr/share/info/coreutils.info.gz` and `timeout(1)` confirms that while timeout kills processes, the residue/deletion clause is an operational policy deduction formulated in `souji-quarantine.sh`, not a literal statement in the coreutils documentation. S038 teaches text restricts itself to grounded vendor statements (exit 124 without `--preserve-status`, secondary KILL via `--kill-after`), maintaining strict calibration.

---

## 6. Code Inspection vs. Exercised Evidence

- **Exercised Evidence**:
  - Direct execution of `timeout --version` revealing `timeout (GNU coreutils) 9.11`.
  - Package query `pacman -Q coreutils` verifying `coreutils 9.11-2`.
  - In-process decompression and line-by-line inspection of `/usr/share/info/coreutils.info.gz` via Python `gzip` in `eval`.
  - In-process decompression and line-by-line inspection of `/usr/share/man/man1/timeout.1.gz` via Python `gzip` in `eval`.
  - Evaluation of proposed row formatting against `scripts/sources-census.sh` validator logic (split parts == 13, cell enums, `supersedes S034` regex).
  - SHA256 checksum verification of `/usr/share/info/coreutils.info.gz`.
- **Code & Doc Inspection Only**:
  - `corpus/SOURCES.md` (read via `read` / `git show`; unedited by this seat).
  - `corpus/lessons/round-13-verifier-spotcheck.md` (read via `read`).
  - `corpus/lessons/round-13.md` (read via `read`).
  - `.ufo/waves/round-14/w1/SourceLedger.md` (read via `read` for peer coordination).
- **Not Opened / Protected**:
  - `census/operator-sweep-20261019/` and `census/operator-sweep-20261018/`: **NEVER OPENED, COPIED, OR QUERIED**.
  - `~/.omp/agent/`: **NO CREDENTIALS OR RUNTIME QUERIED/TOUCHED** (only `RULES.md` read).

---

## 7. Tool Installs & Updates

- **Installs / Upgrades**: None.
- All operations were carried out using existing Python 3 standard library (`gzip`, `subprocess`, `hashlib`, `re`) and installed system tools (`timeout`, `pacman`).

---

## 8. Final L1 Commands (Integration & Verification for Main Agent)

These commands are identified for L1 to execute during integration; **they were not executed by this leaf seat**:

```bash
# 1. Verify exact vendor line numbers in coreutils.info.gz
python3 -c "
import gzip
with gzip.open('/usr/share/info/coreutils.info.gz', 'rt') as f:
    lines = f.readlines()
print('Line 15319:', lines[15318].strip())
print('Line 15320:', lines[15319].strip())
print('Line 15349 (-v):', lines[15348].strip())
print('Line 15365 (exit 124):', lines[15364].strip())
"
# Expected output:
# Line 15319: Ensure the monitored COMMAND is killed by also sending a ‘KILL’
# Line 15320: signal.
# Line 15349 (-v): Diagnose to standard error, any signal sent upon timeout.
# Line 15365 (exit 124): 124 if COMMAND times out, and ‘--preserve-status’ is not specified

# 2. Append-only diff check on corpus/SOURCES.md after L1 integration
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat a31642d -- corpus/SOURCES.md
# Expected: exactly 1 inserted line, 0 deleted lines ("1\t0\tcorpus/SOURCES.md")

# 3. Source census validation
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
# Expected: exit 0; souji ok line; advisory W04 only if duplicate URL is retained across scopes

# 4. Total row count check
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
# Expected: 38 (S001..S038)
```
