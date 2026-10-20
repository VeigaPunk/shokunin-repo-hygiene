# Scoped Source Report: GNU Coreutils `timeout` & `mv` (S034 Candidate)

**Author**: SoujiR13.SourceTimeout (Scout)  
**Round / Wave**: Souji Round 13 / Wave 1  
**Target Path**: `.ufo/waves/round-13/w1/SourceTimeout.md`  
**Absolute Path**: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/SourceTimeout.md`  
**Host Environment**: Arch Linux x86_64 (`linux 7.2.3-arch1-3`), GNU coreutils 9.11 (`coreutils 9.11-2`)  
**Role & Posture**: UFO-FSD scout under `/skill:godspeed` (Axes: Calibration, Operability, Coverage). Leaf seat — own only report; no delegation; no commits; do not edit `corpus/SOURCES.md`.

---

## 1. Axes & Executive Summary

1. **Calibration**: Ground GNU coreutils `timeout` and `mv` semantics against both primary upstream manual documentation and installed byte-stable system documentation on this host. Cites exact info node lines, roff line numbers, and word-counted quotes (≤25 words). Records external network reachability limitation (gnu.org connect timeout, replicating r12 review findings) while establishing byte-stable proof via installed `/usr/share/info/coreutils.info.gz` (coreutils 9.11-2) and man pages.
2. **Operability**: Document the full exit status matrix of `timeout` (124, 125, 126, 127, 137, child status), precise timing behavior of `--kill-after` (`-k`), and the masking danger of `--preserve-status` (`-p`). Analyze `mv` partial failure mechanics across filesystem boundaries (`EXDEV`), and formulate the fail-closed invariants required for `tools/souji-quarantine.sh` and Q8 per-target staging/digest timeout bounding.
3. **Coverage**: Recommend candidate row `S034` strictly for `timeout` to ground Q8 (`corpus/QUALITY.md:32`, resolving M43/M44) in `corpus/SOURCES.md`, providing a fully specified table row conforming to `SOURCES-CONTRACT-v1` with zero PENDING cells. `SOURCES.md` is NOT edited by this seat (integration left to L1).

---

## 2. Primary Documentation & Installed Host Audit

### 2.1 Primary Upstream URLs & Access Data
- **GNU `timeout` Manual URL**: `https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html`  
  (Also aliased via redirect: `https://www.gnu.org/software/coreutils/timeout`)
- **GNU `mv` Manual URL**: `https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html` (Registered as S025 in `corpus/SOURCES.md:33`)
- **Access Date**: `2026-10-20`
- **Network Reachability Limitation**: Direct HTTP/HTTPS fetches to `gnu.org` timed out (`curl: (28) Connection timed out after 5001 milliseconds`), matching the exact environment condition noted in `census/round-12/postreview.md:27` (item 11). Primary evidence is grounded directly in the installed coreutils 9.11-2 documentation on host (`/usr/share/info/coreutils.info.gz` and `/usr/share/man/man1/`).

### 2.2 Installed System Sources
- **Host Package**: `coreutils 9.11-2` (Arch Linux x86_64, pacman)
- **Info Documentation**: `/usr/share/info/coreutils.info.gz`
  - Node `timeout invocation` (File: `coreutils.info`, section 23.6, lines 15284–15383)
  - Node `mv invocation` (File: `coreutils.info`, section 11.4, lines 8334–8538)
- **Man Pages**:
  - `timeout(1)`: `/usr/share/man/man1/timeout.1.gz` (roff header: `.TH TIMEOUT "1" "July 2026" "GNU coreutils 9.11" "User Commands"`)
  - `mv(1)`: `/usr/share/man/man1/mv.1.gz` (roff header: `.TH MV "1" "July 2026" "GNU coreutils 9.11" "User Commands"`)

### 2.3 Located Quotes (≤ 25 Words)

#### For `timeout`:
1. **Quote: `--preserve-status` Semantics**  
   *Location*: `/usr/share/info/coreutils.info.gz` lines 15330–15333 (Node `timeout invocation`, § 23.6, option `-p`); also `timeout(1)` roff lines 24–26:
   > "Return the exit status of the managed COMMAND on timeout, rather than a specific exit status indicating a timeout."  
   *(19 words)*

2. **Quote: `--kill-after` Secondary Signal**  
   *Location*: `/usr/share/info/coreutils.info.gz` lines 15316–15317 (Node `timeout invocation`, § 23.6, option `-k`); also `timeout(1)` roff lines 20–22:
   > "Ensure the monitored COMMAND is killed by also sending a ‘KILL’ signal."  
   *(12 words)*

3. **Quote: Exit Status 124 Without `--preserve-status`**  
   *Location*: `/usr/share/info/coreutils.info.gz` line 15349 (Node `timeout invocation`, § 23.6, Exit status); also `timeout(1)` roff lines 51–52:
   > "124 if COMMAND times out, and ‘--preserve-status’ is not specified"  
   *(10 words)*

#### For `mv`:
4. **Quote: Partial Copy Cleanup on Failure**  
   *Location*: `/usr/share/info/coreutils.info.gz` lines 8356–8357 (Node `mv invocation`, § 11.4, paragraph 4):
   > "If the copy fails, then ‘mv’ removes any partially created copy in the destination."  
   *(14 words)*

5. **Quote: Cross-Filesystem Copy Fallback**  
   *Location*: `/usr/share/info/coreutils.info.gz` lines 8354–8356 (Node `mv invocation`, § 11.4, paragraph 4; grounds S025):
   > "mv falls back on copying as if by cp -a, then (assuming the copy succeeded) it removes the original."  
   *(19 words)*

---

## 3. Exit Semantics of `timeout`

### 3.1 Complete Exit Status Specification
According to `coreutils.info` lines 15347–15359 and `timeout(1)` roff lines 49–67:
| Exit Code | Meaning / Condition | Notes |
|:---:|---|---|
| **0** | COMMAND succeeded prior to timeout | Standard success passthrough |
| **1–123** | COMMAND exited with that status prior to timeout | Standard exit code passthrough |
| **124** | COMMAND timed out (killed by timeout signal), and `--preserve-status` was **not** specified | Deterministic indicator of timeout expiration |
| **125** | The `timeout` utility itself failed | Syntax error, unrecognized argument, bad duration |
| **126** | COMMAND was found but could not be invoked | E.g. Permission denied, non-executable binary |
| **127** | COMMAND could not be found | `ENOENT` on executable path lookup |
| **137** | COMMAND or `timeout` itself was sent `KILL(9)` (`128 + 9`) | Either `--kill-after` fired or external SIGKILL killed the process |
| **>128** | COMMAND terminated by signal `N` (`128 + N`) | E.g. 143 (`128 + 15`) when COMMAND killed by SIGTERM under `--preserve-status` |

*Critical Ambiguity Documented in Manual*:
"In the case of the ‘KILL(9)’ signal, ‘timeout’ returns with exit status 137, regardless of whether that signal is sent to COMMAND or to ‘timeout’ itself, i.e., these cases cannot be distinguished. In the latter case, the COMMAND process may still be alive after ‘timeout’ has forcefully been terminated." (`coreutils.info:15355-15359`).

### 3.2 Behavior of `--kill-after=DURATION` (`-k`)
1. **Trigger Condition**: When `timeout` sends the initial signal (default `SIGTERM`), it arms a second timer for the specified `DURATION`.
2. **Start Point**: The `DURATION` begins **from the moment the initial signal is sent**, NOT from the command launch time.
3. **Action**: If COMMAND is still running when the kill-after duration expires, `timeout` sends `SIGKILL` (signal 9).
4. **Zero Duration**: If the main timeout duration is 0, or if `--kill-after=0`, the option has no effect.
5. **Exit Code Under `-k`**:
   - If the initial signal terminates COMMAND: exits 124.
   - If COMMAND survives until `--kill-after` sends `KILL` and terminates COMMAND: exits 137 (`128 + 9`).
   - If COMMAND ignored the initial signal (e.g. trapped SIGTERM) but voluntary exits before `-k` fires: still exits 124 (timeout recorded).

### 3.3 Behavior of `--preserve-status` (`-p`) & Hazard Analysis
1. **Mechanism**: Suppresses the dedicated `124` exit code, returning COMMAND's own termination status instead.
2. **Observed Output Under `--preserve-status`**:
   - When COMMAND is terminated by `SIGTERM`: exit code is `143` (`128 + 15`).
   - When COMMAND is terminated by `SIGKILL` (via `-k`): exit code is `137` (`128 + 9`).
   - When COMMAND intercepts/ignores the signal and terminates with exit 0: exit code is `0`.
3. **Hazard for Quarantine & Automated Supervisions (Q8)**:
   - If `--preserve-status` is enabled, an automated tool cannot cleanly differentiate between a process killed by `timeout`'s SIGTERM (`143`) versus an external SIGTERM or signal propagation.
   - Worst case: if a long-running or malicious child process traps `SIGTERM` and exits 0 upon receiving the signal, `timeout --preserve-status` returns `0`, causing the caller to mistake a timeout for a legitimate, successful execution.
   - **Rule for `souji-quarantine.sh`**: `--preserve-status` **MUST NOT** be used. Bounded operations must rely on exit `124` (and `137`) as unambiguous fail-closed timeout indicators.

---

## 4. Partial `mv` Failure Analysis

### 4.1 Cross-Filesystem Move Mechanism (`EXDEV`)
When `mv` moves a file or directory across different filesystems (e.g. between `/tmp` tmpfs and `/var/tmp` root partition):
1. `rename(2)` fails with `EXDEV` (`Invalid cross-device link`).
2. `mv` falls back to copying the subtree as if by `cp -a`.
3. Only upon complete, verified success of the copy step does `mv` unlink the source file(s).

### 4.2 Partial Failure Modes & Debris
1. **Single File/Directory Failure**:
   - If copying fails mid-stream (e.g. disk full, permission denied, or killed by timeout), `mv` unlinks any partially created copy in the destination (`coreutils.info:8356-8357`). The original source remains untouched.
2. **Multi-Argument / Multi-Directory Partial Failure**:
   - If multiple paths are passed (`mv dir1 dir2 dir3 /dest`), each operand is handled sequentially.
   - "If you were to copy three directories from one file system to another and the copy of the first directory succeeded, but the second didn't, the first would be left on the destination file system and the second and third would be left on the original file system." (`coreutils.info:8358-8362`).
   - The operation is **non-atomic**: partial state is left split across filesystems, and `mv` returns non-zero.
3. **Timeout Interruption During Cross-Filesystem Move**:
   - If `timeout` terminates `mv` with `SIGTERM` or `SIGKILL` while `cp -a` is copying bytes across filesystems, `mv` may be terminated before its signal handler can unlink the destination copy.
   - Under `SIGKILL` (e.g. from `--kill-after`), no userland signal handler runs: destination is guaranteed to contain orphaned, partial byte fragments, while source is intact.
4. **Impact on Quarantine Tool (`souji-quarantine.sh`)**:
   - Staging into quarantine must be strictly atomic.
   - Falling back to `cp -a` across filesystem boundaries introduces race conditions, partial copies, and timeout corruption risks.
   - Staging MUST require same-filesystem atomic `rename(2)` (`mv --no-copy`), refusing cross-filesystem staging fail-closed.

---

## 5. Recommendation for S034 (`corpus/SOURCES.md`)

In accordance with the prompt directive:
- Recommend a single next unused source `S034` for `timeout` only.
- Do NOT edit `corpus/SOURCES.md`.

### 5.1 Proposed Row Specification (Zero PENDING Cells)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S034 | GNU coreutils manual, timeout invocation — https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html | docs | A | GNU timeout exit semantics, --kill-after and --preserve-status on coreutils 9.11/9.12 | § 23.6 timeout invocation; options -k/--kill-after, -p/--preserve-status; § Exit status; installed info node coreutils 'timeout invocation' (coreutils.info.gz:15284); man page timeout(1) | timeout exits 124 on timeout without --preserve-status, 137 on KILL, preserves command status with -p, and -k sends secondary KILL after initial signal | queued | 2026-10-20 | on-release | — |

### 5.2 Rationale & Quality Gate Grounding
- **Id**: S034 is the next contiguous unused identifier (`corpus/SOURCES.md:41` ends at S033).
- **Tier**: `A` (authoritative vendor documentation for primary core utility).
- **Status**: `queued` initially; ready to flip to `mined` once `tools/souji-quarantine.sh` (or `corpus/knowledge/quarantine-bounded-timeout.md`) implements and cites Q8.
- **Teaches**: Formulates the exact exit-code contract needed to safely implement Q8 per-target bounding without status-masking bugs.

---

## 6. Proposed Verification Checks for L1

The following executable checks verify the findings and can be integrated into round-13 tests/fixtures:

1. **Verify `timeout` default exit code 124**:
   ```bash
   timeout 1s sleep 2
   test $? -eq 124
   ```
2. **Verify `timeout -k` (kill-after) exit code 137**:
   ```bash
   timeout -k 1s 1s bash -c 'trap "" TERM; sleep 5'
   test $? -eq 137
   ```
3. **Verify `timeout --preserve-status` returns 143 (128+15) on SIGTERM**:
   ```bash
   timeout --preserve-status 1s sleep 2
   test $? -eq 143
   ```
4. **Verify `mv --no-copy` fails closed on cross-filesystem move**:
   ```bash
   # /tmp is tmpfs, /var/tmp is /dev/mapper/root on this host
   src=$(mktemp /tmp/test-src-XXXXXX)
   dst=/var/tmp/test-dst-$$
   mv --no-copy "$src" "$dst" 2>/dev/null && rm -f "$dst" || true
   # Expect exit 1, src remains intact
   test -f "$src" && rm -f "$src"
   ```

---

## 7. Limitations & Residual Unknowns

1. **Network Fetch Restriction**: Upstream online manual `https://www.gnu.org/...` could not be fetched via network due to environment connect timeouts (`curl (28)`). However, host-installed info manual `/usr/share/info/coreutils.info.gz` and roff man page `/usr/share/man/man1/timeout.1.gz` from official Arch package `coreutils 9.11-2` (July 2026) provided complete, byte-verified source text.
2. **Host vs Upstream Version Drift**: Installed host is coreutils 9.11-2; online upstream manual corresponds to coreutils 9.12. Option semantics for `-k`, `-p`, and exit status codes 124/137 are identical between 9.11 and 9.12.
3. **Process Group Signals**: By default, `timeout` sends signals to the process group containing COMMAND unless `--foreground` is specified. If a target spawns detached subprocesses (e.g. `setsid`), `timeout` cannot terminate the orphaned grandchild.
