STATUS: PARTIAL — the process-census implementation is absent, so runtime guards cannot be verified; this report records the concrete security acceptance checks.

# SentinelProcCensus — security review

Axis: **coverage**. Scope is the C3 process-residue census contract only. No script, fixture, or process-census item was available to inspect; findings below distinguish the observed blocker from conditional threat checks, not confirmed implementation defects.

## Finding F1 — review blocker: no implementation to inspect

**Severity:** BLOCKER (review completeness, not an asserted vulnerability).

**Exploit path:** Not assessable without the source. An implementation could read another user's `cmdline`, disclose argv secrets, misreport a PID after reuse, forge TSV rows via control characters, read `environ`, signal a process, or write output somewhere other than stdout; none of those behaviors is established here.

**Evidence:** `read` of `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` returned `Path ... not found`; `stat /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` returned `No such file or directory`; `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-proc-census.sh` produced no output. The round work-item directory listing also contained no `ProcCensus` item. The available proposed contract is recorded in `.ufo/waves/round-18/w1/ScribeProvinceProc.md:30-51`.

**Impact:** No claim that the actual implementation meets the read-only, own-UID, redaction, or serialization contract can be made from the evidence available.

**Smallest remediation:** Make the implementation and its named fixture available at the exact round revision, then re-run this review against those files. Do not admit a coverage claim based only on the contract draft.

## F2 — HIGH acceptance risk: PID exit/reuse can mix observations

**Exploit path:** A process exits after `/proc/<pid>` enumeration or between `stat`, `cwd`, and `cmdline` reads; the PID is then reused. A reader that treats one failed read as fatal can lose the census, while one that combines values from different process instances can emit a false residue row or wrong owner/command.

**Evidence:** The contract requires pid/ppid/pgid/age/state/wchan/reason and redacted command in one row (`ScribeProvinceProc.md:33-36`). The opened proc stat source notes that several fields can be reported as zero when the ptrace access check denies access and that `starttime` is in clock ticks (`ScribeRowsProc.md:24, 53-56`); this does not supply an atomic snapshot.

**Impact:** False or internally inconsistent evidence, or one disappearing process aborting the scan and masking neighbours.

**Smallest guard:** Treat `/proc` reads as fallible per-PID observations: skip/retry a PID on ENOENT, EACCES, malformed/short reads, or mismatched identity; never let such a race abort the whole census or emit a partially populated row. Snapshot `(pid,starttime,owner)` before collecting other fields and recheck it after collection; discard the row if identity changed. Parse `/proc/<pid>/stat` with a parser that handles spaces and `)` in `comm`, not a naive whitespace split. Do not treat permission-denied zero fields as genuine values.

**Concrete fixture inputs:** In a private fake-proc fixture, create PID `41001` with valid initial `stat`, then make it disappear before the `cwd` read; assert the run succeeds, no PID 41001 row is emitted, and later valid PID `41002` remains. For PID reuse, serve starttime `100` on the first `stat` read and `200` on the final check; assert no row for `41001`. Also supply a `comm` containing spaces and `)` and a short/denied stat record; assert no field-shifted output and no whole-run failure.

## F3 — HIGH privacy risk: current-UID gate and argv redaction must precede output

**Exploit path:** Scanning another UID's proc entries before an ownership check can read its cwd or command line where proc permissions permit it. Even for the current UID, process arguments commonly contain credentials; printing raw `/proc/<pid>/cmdline` or logging it before redaction discloses them. Redaction applied only to stdout but not stderr/debug output is insufficient.

**Evidence:** The proposed contract limits the scan to processes owned by the current UID and requires a redacted, truncated command (`ScribeProvinceProc.md:32-36, 48-51`). The source note explicitly says its reviewed pages do not cover `/proc/<pid>/cmdline` or ground its redaction/path matching (`ScribeRowsProc.md:55`).

**Impact:** Cross-user information disclosure and credential leakage into the report, logs, or captured stderr.

**Smallest guard:** Capture the caller UID once; establish that a PID belongs to that UID before reading `cwd`, `cmdline`, or `wchan`; do not elevate privilege or broaden to all UIDs when run as root. Keep the default output allowlisted (e.g. safe executable basename plus a fixed redaction marker), not raw argv. If argv is needed for matching, parse NUL-delimited bytes without shell word splitting/eval, redact the complete sensitive argument and its value before any output or diagnostics, and never enable shell tracing. Redact values for separate and inline forms of credential flags, assignments, authorization headers, URL userinfo and `op://` references; do not assume a finite name-pattern list catches every secret.

**Concrete fixture inputs:** Use two synthetic proc entries, one matching the caller UID and one with a different UID; give both `cmdline` a unique `DO_NOT_PRINT_OTHER_UID` sentinel and assert only the current-UID entry is accessed and only its eligible row is emitted. For an owned entry, test NUL-separated argv containing `--password\0DO_NOT_PRINT_SECRET`, `--token=DO_NOT_PRINT_SECRET`, `PASSWORD=DO_NOT_PRINT_SECRET`, `-p\0DO_NOT_PRINT_SECRET`, `--header\0Authorization: Bearer DO_NOT_PRINT_SECRET`, `https://user:DO_NOT_PRINT_SECRET@example.invalid/`, and `op://vault/item`; assert none of the sentinel values appears on stdout or stderr. Include an unmarked positional secret to verify the output is allowlisted rather than relying only on flag-name heuristics.

## F4 — HIGH integrity risk: cwd/argv paths can forge TSV records or defeat path classification

**Exploit path:** A cwd pathname or argv token containing literal tab/newline/carriage-return is interpolated into TSV, splitting one process into attacker-controlled rows or columns. Naive whitespace splitting, `echo -e`, shell evaluation, or following a link while resolving a path can alter fields or classify a path outside the intended scratch roots. A literal directory name ending in ` (deleted)` can also be confused with a kernel-added deleted-path marker.

**Evidence:** The row contract includes process metadata and a command (`ScribeProvinceProc.md:33-36`). The reviewed proc cwd page does not establish the removed-directory suffix; the note routes any such claim to fixture evidence (`ScribeRowsProc.md:53`). No source is available to verify escaping, component-boundary checks, or link handling.

**Impact:** A crafted process can inject fake census rows, corrupt downstream TSV parsing, or cause false residue classification. A false “deleted cwd” result can overstate the orphan count.

**Smallest guard:** Treat proc-provided names/argv as untrusted bytes. Never word-split, evaluate, `cd` to, or follow a proc-derived link for reporting. Encode or reject tab, LF, CR, `%`, and control bytes in every TSV field (including command/path); emit records with fixed `printf` fields so one observation always occupies exactly one physical line and the documented column count. Match scratch roots only on exact path-component boundaries (`/tmp/...`, not `/tmpx/...`), use literal quoted path tests without globbing, and do not canonicalize a missing path by following arbitrary symlinks. Determine deleted cwd status independently of a bare textual suffix and distinguish a real path literally ending ` (deleted)`.

**Concrete fixture inputs:** Use a current-UID process whose cwd contains a literal tab and newline, plus cwd names `literal (deleted)` (still present) and a genuinely unlinked cwd; assert each emitted result is one physical TSV record with the fixed number of columns and encoded controls, and that the literal suffix is not marked deleted. For argv path matching, test `/tmp/r18-missing/x`, `/tmpx/r18-missing/x`, `/var/tmp/r18-missing/x`, `/dev/shm/r18-missing/x`, and a symlink under `/tmp` that points outside the three roots; assert only lexical paths under the exact allowed roots qualify and the outside target is not opened or exposed.

## F5 — CRITICAL contract invariant: no `environ` reads, no signaling, stdout-only/no side effects

**Exploit path:** Any helper that scans `/proc/<pid>/environ`, calls `kill`/`pkill`/`killpg`, logs to a file, or uses a command that emits raw argv on stderr violates the list-only, no-secret-read contract. A “cleanup” signal would turn a census into an unauthorized process action.

**Evidence:** The draft boundary explicitly prohibits signaling and `/proc/<pid>/environ` reads (`ScribeProvinceProc.md:46-51`). This could not be checked against source because F1 applies.

**Impact:** Secret access, process disruption, or findings escaping the promised stdout-only reporting boundary.

**Smallest guard:** Keep the implementation strictly observational: no `kill`-family calls, no `/proc/*/environ` path construction/open, no output files/temp logs, and no raw command text in errors. Send result rows only to stdout; keep operational diagnostics on stderr only if the interface explicitly allows them and ensure they contain no proc-derived secret text. Preserve the target's process state.

**Concrete fixture inputs:** Give a synthetic proc entry an `environ` file containing `DO_NOT_READ_ENV_SENTINEL` and instrument the fake reader to fail the test if that path is opened; assert sentinel absent from both output streams. Run with stdout redirected by the *test harness* to a private capture file, verify the census itself created no files, verify its child fixture remains alive and unchanged after the scan, and statically inspect the exact implementation for signal primitives and environ path opens. Keep fixture cleanup limited to processes that the test itself started; the census must never signal them.

## Commands and verification

- `read /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` → `Path ... not found`.
- `stat /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` → `No such file or directory` (exit 1).
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 -- tools/souji-proc-census.sh` → no output (exit 0).
- Read `.ufo/waves/round-18/w1/ScribeProvinceProc.md:30-51` and `.ufo/waves/round-18/w1/ScribeRowsProc.md:51-56` for the cited contract and evidence gap.
- No implementation or fixture was executed; no tests/checks passed or were claimed. No tools installed or updated.