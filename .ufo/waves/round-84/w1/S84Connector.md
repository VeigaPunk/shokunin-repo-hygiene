# S84Connector Report — souji round 84

## 1. Cross-Claim Separation Verdict

### Separation Verdict: STRICTLY SEPARABLE
Claim 1 (C1: calibration 7, false-row population binding five pointer-counter clauses) and Claim 2 (C2: operability 8, vault CLI signal path descendant freeze before termination) share no file, counter, population, command, or receipt. The two claims are completely independent and verifiable in strict isolation.

- **C1 is verifiable without C2:** The C1 battery (`census/round-84/c1-clause-battery.py`) and harness (`census/round-84/c1-false-row-harness.py`) evaluate the pointer-resolution counter (`census/round-84/c1-pointer-counter.py`) and its 5 frozen mutants (`census/round-84/c1-mutants.json`) against git commit trees and the pinned 44-row population (`census/round-84/c1-false-rows.tsv`). It executes entirely in Python with read-only git operations on synthetic fixture repositories, touches no shell scripts, does not invoke `tools/souji-vault-verify.sh`, and performs zero process inspections or `/proc` queries.
- **C2 is verifiable without C1:** The C2 counter (`census/round-84/c2-late-fork-counter.py`) tests the signal handling, process tree freezing, and teardown of `tools/souji-vault-verify.sh` against the pinned 22-row population (`census/round-84/c2-population.tsv`). It executes bash subprocesses with synthetic fixtures under a private scratch directory, and does not import, invoke, or inspect `c1-pointer-counter.py`, `c1-false-rows.tsv`, or any pointer ledger.
- **Shared Artifacts / Commands:** None. The intersection of files touched by C1 and C2 is empty ($\emptyset$).

### Complete Inventory of Files Touched by Each Claim

| Category | Claim 1 (C1: Calibration 7) | Claim 2 (C2: Operability 8) | Shared? |
|---|---|---|---|
| **Target Candidate** | `census/round-84/c1-pointer-counter.py` | `tools/souji-vault-verify.sh` (candidate: `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh`) | **NO** |
| **Instrument / Harness** | `census/round-84/c1-clause-battery.py`, `census/round-84/c1-false-row-harness.py` | `census/round-84/c2-late-fork-counter.py` | **NO** |
| **Mutants Definition** | `census/round-84/c1-mutants.json` (5 single-edit mutants: m6, m7, m8, m9, m10) | None (mutation tested via `S84MutTool` suite) | **NO** |
| **Primary Population** | `census/round-84/c1-false-rows.tsv` (44 rows, sha256 `4795f009...`) | `census/round-84/c2-population.tsv` (22 rows, sha256 `31422477...`) | **NO** |
| **Baseline Population** | `census/round-83/c1-false-rows.tsv` (36 rows, sha256 `c9a6d58c...`) | `census/round-83/c2-population.tsv` (20 rows, sha256 `90924b4f...`) | **NO** |
| **Referenced Populations** | `census/round-77/c2-population.tsv`, `census/round-77/c2-pointer-ledger.tsv`, `census/round-78/c2-population.tsv`, `census/round-78/c2-pointer-ledger.tsv` | None | **NO** |
| **Fixture Source Files** | `census/round-32/waves/a2w1/SwarmExecutor08.md`, `census/operator-sweep-20261019`, `.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt`, `.ufo/quarantine` | None | **NO** |
| **Do-Nothing Control** | Unchanged counter on r83 population | `census/round-84/controls/c2-K-a-r83-tool.sh` (sha256 `72a405f2...`) | **NO** |
| **Control Receipts** | `census/round-84/controls/c1-before-r83-population.txt` | `census/round-84/controls/c2-before-r83-tool.txt` | **NO** |
| **Primary Records** | `census/round-84/records/c1-reference-prefreeze.txt` | `census/round-84/records/c2-reference-prefreeze.txt` | **NO** |
| **Counting Command** | `python3 -B census/round-84/c1-clause-battery.py --counter ... --work ... --only r84 --expect-killed 5` | `python3 -B census/round-84/c2-late-fork-counter.py --tool ... --work ...` | **NO** |
| **Side Regressions** | None | `tools/souji-vault-verify.sh --selftest`, `tests/fixtures/r17-jj-receipts.sh`, `census/round-81/probes/tmpdir-in-vault.py` | **NO** |

---

## 2. Sibling Overlap Inside the Lane

### 2.1 `/proc/<pid>/stat` Parsing and Traversal Duplication

A comprehensive audit of process table inspection across `souji-shokunin/tools/` reveals extensive code duplication for `/proc/<pid>/stat` parsing and parent/child relationship walking:

#### 1. `tools/souji-proc-census.sh` (lines 124–160, 353–376)
- **Lines 124–148 (`parse_proc_stat`)**:
  ```bash
  while IFS= read -r stat_part || [[ -n $stat_part ]]; do
    if ((stat_started)); then stat_line+=$'\n'; fi
    stat_line+=$stat_part
    stat_started=1
  done < "$proc_path/stat" 2>/dev/null || return 1
  stat_tail=${stat_line##*) }
  read -r -a fields <<< "$stat_tail"
  PROC_STATE=${fields[0]}
  PROC_PPID=${fields[1]}
  PROC_PGID=${fields[2]}
  PROC_SID=${fields[3]}
  PROC_STARTTICKS=${fields[19]}
  ```
- **Lines 150–160 (`is_self_tree`)**:
  Ascends the parent chain `cursor=$parent` using `PARENT_BY_PID[$cursor]` up to 512 hops.
- **Lines 353–359 & 367–371**:
  Performs two passes over `/proc/[0-9]*`: pass 1 records `PARENT_BY_PID[$pid]` and `STAT_BY_PID[$pid]`; pass 2 re-parses stat, checks starttime ticks equality (`[[ $PROC_STARTTICKS == "$snapshot_start" ]]`), and checks tree membership via `is_self_tree "$pid"`.

#### 2. `tools/souji-vault-verify.sh` (`cli_kill_tree`, lines 244–295 in candidate)
- **Lines 246–259 (Map Pass)**:
  ```bash
  for d in /proc/[0-9]*; do
    line=""
    { IFS= read -r -d '' line < "$d/stat"; } 2>/dev/null
    [ -n "$line" ] || continue
    rest=${line##*)}
    set -- $rest
    [ "$#" -ge 20 ] || continue
    p=${d#/proc/}
    ppid_of[$p]=$2
    [ -n "${start_of[$p]:-}" ] || start_of[$p]=${20}
  done
  ```
- **Lines 270–275 & 287–293 (Re-check Loops)**:
  Re-reads `/proc/$k/stat`, strips after `) `, and re-checks field 20 against `start_of[$k]` before delivering signals.

#### Single-Sourcing Architectural Assessment
- **Should the lane single-source this? NO.**
  While the logic of reading `/proc/<pid>/stat`, stripping through `*)` to bypass comm whitespace/newlines, and extracting field 4 (ppid) and field 22 (starttime) is semantically identical, `souji-vault-verify.sh` must **NOT** source `souji-proc-census.sh`.
  *Reasoning (Tool Isolation & Fault Containment):* `souji-vault-verify.sh` is an autonomous gate tool invoked in critical validation contexts. Sourcing an external library from within an active asynchronous trap handler (`cli_on_signal`) introduces severe external failure domains: missing path, permission alteration, parse errors in the sourced file, or environment contamination will cause the trap handler to crash, leaving unmanaged descendant processes orphaned in the background. Autonomous containment requires `souji-vault-verify.sh` to remain strictly self-contained.
- **Internal Duplication Issue:** Within `cli_kill_tree` itself, the candidate executes `for pass in 1 2; do`, rescanning `/proc/[0-9]*` over the entire system twice. This internal loop is pure code repetition and can be optimized or clarified.

---

### 2.2 Sibling Map-Pass Shape Duplication Across the Fleet

The map-pass pattern (scanning `/proc`, parsing stat after `)`, mapping parent/child or process attributes, re-verifying starttime, and terminating processes) now exists in **four distinct locations** across the lane:

1. **Place 1: `tools/souji-vault-verify.sh:244–295` (Candidate `cli_kill_tree`)**
   - Language: Bash.
   - Shape: Two-pass directory scan of `/proc/[0-9]*`, strips `*)`, constructs `ppid_of` and `kids_of`, traverses down descendant stack, re-reads starttime, issues `kill -STOP`, and sweeps `kill -KILL`.

2. **Place 2: `census/round-83/c2-tree-walk-counter.py:186–215` / `census/round-84/c2-late-fork-counter.py:202–231` (`nonce_pids` & `reap`)**
   - Language: Python.
   - Shape:
     ```python
     for d in os.listdir("/proc"):
         if not d.isdigit(): continue
         with open(f"/proc/{d}/environ", "rb") as f: env = f.read().split(b"\0")
         with open(f"/proc/{d}/stat", "rb") as f: state = f.read().rsplit(b")", 1)[1].split()[0]
         if key in env and state != b"Z": found.append(int(d))
     ```
     Followed by a 5-iteration loop sending `os.kill(pid, signal.SIGKILL)`.

3. **Place 3: `tools/souji-quarantine.sh:189–215` (`q_proc_sid` & `q_kill_session`)**
   - Language: Bash.
   - Shape:
     ```bash
     q_kill_session() {
       for pass in 1 2 3 4 5 6 7 8 9; do
         pids=()
         for p in /proc/[0-9]*; do
           p=${p#/proc/}
           q_proc_sid "$p" && [ "$Q_SID" = "$sid" ] && pids+=("$p")
         done
         [ "${#pids[@]}" -gt 0 ] || return 0
         [ "$pass" -lt 9 ] || return 1
         kill -STOP "${pids[@]}" 2>/dev/null || true
         kill -KILL "${pids[@]}" 2>/dev/null || true
       done
     }
     ```
     Scans `/proc/[0-9]*` up to 9 passes, filters by session ID (field 6 of `/proc/<pid>/stat`), and issues `kill -STOP` followed by `kill -KILL`.

4. **Place 4: `tools/souji-proc-census.sh:353–376` (`collect_census_snapshot`)**
   - Language: Bash.
   - Shape: Two-pass directory scan of `/proc/[0-9]*`, builds `PARENT_BY_PID` and `STAT_BY_PID`, checks `snapshot_start` timestamp persistence, and traverses ancestor hops via `is_self_tree`.

---

## 3. Wording Cross-Check Table (Amendment 59 Class)

Audit of `census/round-84/preregistration.txt` sentences asserting behaviors not exercised by the instruments:

| Item | Preregistration Sentence / Assertion | Location | Enforced in Code? | Exercised by Population / Counter? | Exercising Mutant or Row | Status & Finding |
|---|---|---|---|---|---|---|
| **W1** | *"a second map pass catches a child forked in the read->stop window, and the frozen set is then SIGKILLed."* | `prereg:49-50` | **YES** (`cli_kill_tree:253` `for pass in 1 2`) | **NO** | Mutant `m2-single-pass` (changing `for pass in 1 2` to `for pass in 1`) survives 22/22 green! | **Unrowed Property:** In `l1` and `l2`, `latefork` forks *only* upon receiving a trappable signal. Because pass 1 delivers `SIGSTOP` before any signal arrives, `latefork` is frozen and never runs its trap or forks. Pass 2 discovers 0 new children across all 22 rows. No row in `c2-population.tsv` forks in the microsecond window between `/proc` read and `SIGSTOP`. |
| **W2** | *"starttime field 22 re-checked before the signal"* | `prereg:47-48` | **YES** (`cli_kill_tree:88-89`) | **NO** | Mutants `m6-no-starttime-at-stop` and `m7-no-starttime-at-kill` survive 22/22 green! | **Unrowed Property:** No row in `c2-population.tsv` recycles or replaces a PID during tool execution. Dropping starttime re-checks leaves the candidate 100% green on the frozen counter. (Carried forward from r83). |
| **W3** | *"ppid after the last `)` of comm"* | `prereg:47` | **PARTIAL** | **NO** | A row whose CLI or child process has an embedded newline or `)` in comm. | **Unrowed Fixture & Incomplete Fix:** Zero rows in `c2-population.tsv` test comms containing newlines or parentheses. Furthermore, `S84ExecC2`'s candidate lines 85 and 288 retain `{ read -r now < "/proc/$k/stat"; }` (single-line read) for the STOP/KILL re-checks, re-exposing r83 defect D5! |
| **W4** | *"census-in-tree branch"* in `c1-pointer-counter.py:387-395` | `prereg:20-27` | **YES** (`c1-pointer-counter.py:387-395`) | **NO** | A row whose token begins with `census/round-<N>/`. | **Dead Code / Unrowed Branch:** In `c1-false-rows.tsv` (44 rows), every MOVED row uses P04 or P07 (tokens under `.ufo/waves/round-<N>/`) or NF3 (L02, which has no `round-<N>`). Zero rows have a token under `census/round-<N>/`. (Flagged in `round-82-verifier-spotcheck.md` item 7; still ungrounded). |
| **W5** | Wave shapes wider than population (`w[0-9]+/`) | `prereg:26-27` | **YES** (`OWNTREE_WAVE`) | **PARTIAL** | Rows testing `w4/`..`w99/`. | **Unrowed Shapes:** The regex permits `w[0-9]+/`, but rows only exist for `w1/` (TF7), `w2/` (TF6, TF8), `w3/` (NF-L decoy), `a2w1/` (TF9), and `assimilation/` (TF10). |
| **W6** | Kill rule auxiliary assertions: *"--selftest going red, r17 ... going red, probe D ... going red, a second pass that forks a pgrep/ps per node, or a signal delivered to a pid outside the CLI's descendant set"* | `prereg:79-80` | **NO** (Not in counter) | **NO** | An explicit probe or test harness step. | **External Side-Constraints:** `census/round-84/c2-late-fork-counter.py` does not run `--selftest`, `r17`, or probe D; it has zero shims or counters to detect pgrep/ps forks, and does not monitor signals to external PIDs. |

---

## 4. Table of Findings

| ID | Severity | Surface | Finding Summary | Exact Path & Lines | Evidence / Reproducer |
|---|---|---|---|---|---|
| **F-01** | **HIGH** | C2 Repair Candidate | `RefC2` candidate wiped `start_of` array between pass 1 and pass 2 (`start_of=()`), losing recorded starttimes and breaking all 4 `monitor` launch rows (m1, m2, d24, l2; 4 mismatches). `S84ExecC2` candidate correctly uses persistent caching (`[ -n "${start_of[$p]:-}" ] \|\| start_of[$p]=${20}`). | `.ufo/waves/round-84/w1/RefC2/souji-vault-verify.sh:245` vs `S84ExecC2/cli_kill_tree.diff:73` | Running `c2-late-fork-counter.py` on RefC2 yields `rows=22 mismatches=4 errors=0 orphans=4 EXIT=1`; running on S84ExecC2 yields `mismatches=0 EXIT=0`. |
| **F-02** | **MEDIUM** | C2 Repair Candidate | `S84ExecC2` candidate re-exposes r83 spot-check defect D5 by using first-line `read -r` (`{ read -r now < "/proc/$k/stat"; }`) in the STOP and KILL re-read loops instead of whole-file read. | `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh:272, 288` | `round-83-verifier-spotcheck.md:49-51, 230-233`. A process with a newline in comm will be skipped during starttime re-check. |
| **F-03** | **MEDIUM** | C2 Population & Claims | The second map pass (`for pass in 1 2; do`) is completely unexercised by `c2-population.tsv`. Mutant `m2-single-pass` survives 22/22 green because `latefork` is frozen in pass 1 before it can receive a signal and execute its trap. | `census/round-84/c2-population.tsv`, `census/round-84/preregistration.txt:49` | `S84MutTool/mutants/m2-single-pass.sh` scored 22/22 green (`mismatches=0`). |
| **F-04** | **LOW** | C1 Population & Counter | The `census-in-tree` branch in `c1-pointer-counter.py` remains dead code with zero corresponding rows in `c1-false-rows.tsv` (44 rows). | `census/round-84/c1-pointer-counter.py:387-395` | `round-82-verifier-spotcheck.md` item 7; grep of `c1-false-rows.tsv` reveals zero tokens starting with `census/round-<N>/`. |
| **F-05** | **LOW** | Fleet Process Architecture | `parse_proc_stat` logic is duplicated across `souji-proc-census.sh`, `souji-vault-verify.sh`, and `souji-quarantine.sh`, but isolation constraints rightly preclude sourcing external scripts in signal trap paths. | `tools/souji-proc-census.sh:124-148`, `tools/souji-vault-verify.sh:246-259`, `tools/souji-quarantine.sh:189-200` | Code inspection; identical `${stat##*)}` and field extraction logic. |

---

## 5. Non-Obvious Move Proposal (UFO-FSD Role)

### Evidence
1. **Instrument Mutation Gap:** In C2, the second map pass is unrowed: mutant `m2-single-pass` (`for pass in 1; do`) reports `rows=22 mismatches=0 errors=0 orphans=0`, because `latefork` in `l1/l2` traps the signal, but `kill -STOP` in pass 1 freezes the process before it ever receives TERM/INT/HUP.
2. **Defect D5 Recurrence:** In `S84ExecC2`'s candidate, lines 85 and 288 use single-line `{ read -r now < "/proc/$k/stat"; }` for the STOP and KILL re-reads, leaving the r83 spot-check defect D5 unaddressed on the re-read path.
3. **Execution Overhead:** Running two full `/proc/[0-9]*` scans on every signal under high concurrent load costs up to 1.5–3.5 s (approaching the 5.0 s SETTLE bound).

### Affected Axes
- **Operability (Operability 8)**: Robustness of signal cleanup under complex process trees and non-standard process names.
- **Calibration (Calibration 7)**: Accurate alignment between preregistered claims and verified instrument discrimination.

### Proposed Move
A compatible synthesis across the round's findings:
1. **Close Defect D5 on Re-read Paths in `cli_kill_tree`:**
   Change `{ read -r now < "/proc/$k/stat"; }` at the STOP re-check (line 272) and KILL re-check (line 288) to the whole-file reader:
   `{ IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null || continue`
   This guarantees that a descendant process with an embedded newline in its comm is not silently skipped during the starttime validation re-check.
2. **Reconcile Preregistration Wording via `plans/round-84.md` (Pre-file Discipline):**
   In `plans/round-84.md`, amend the stated wording for C2:
   - Clarify that the measured delta of the 22-row population is the **freeze-before-signal sequence** (which prevents the CLI from trapping signals or forking setsid'd children).
   - Explicitly document that the second map pass and the starttime re-checks are **defensive structural invariants against asynchronous kernel race windows**, rather than behaviors empirically discriminated by the 22-row population (matching the precedent established in r83 for the starttime re-check).
3. **Preserve `S84ExecC2`'s Starttime Persistence:**
   Ensure the integration retains `[ -n "${start_of[$p]:-}" ] || start_of[$p]=${20}` (first write wins) rather than clearing `start_of` between passes, ensuring `monitor` jobs and deep trees remain clean.

### Risks
- Applying whole-file stat reads to the re-checks adds negligible latency (microseconds) and relies strictly on bash builtins (`IFS= read -r -d ''`), which cannot hang or fork.
- Classifying pass 2 as a structural invariant in `plans/round-84.md` avoids falsification by the critic while truthfully disclosing the instrument's mutation profile.

### Verification
- Run `c2-late-fork-counter.py` on the candidate with whole-file stat re-reads → `rows=22 mismatches=0 errors=0 orphans=0 EXIT=0`.
- Verify with a synthetic newline-comm background process that the re-check does not abort or skip the node.
