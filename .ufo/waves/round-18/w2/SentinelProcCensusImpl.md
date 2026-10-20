STATUS: DONE — static review found incomplete credential redaction and a PID-reuse identity gap.

Axes: coverage (requested secret shapes and ownership checks), calibration (credential exposure), operability (output/cleanup behavior).

## Scope and evidence

Reviewed `tools/souji-proc-census.sh` at `5efb519f00075d958c3d1109ef6fcb24c487eb87`, plus `.ufo/waves/round-18/w1/RevProcRedaction.md` and `tests/fixtures/r18-proc-census.sh`. Exact-source digest matched: commit blob and worktree both `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc`.

Checks and observed outputs:

- `printf 'commit '; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5efb519f00075d958c3d1109ef6fcb24c487eb87:tools/souji-proc-census.sh | sha256sum; printf 'worktree '; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh` → `commit c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc  -` and `worktree c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-proc-census.sh`.
- Exact-file search `pattern=environ` → `No matches found`.
- Exact-file search `pattern=kill` → matches at lines 9, 368, 441 only: function unsetting, process-group `SIGKILL` in `cleanup_selftest`, and `kill -0` worker liveness probe.
- No lane code or fixtures were executed; findings below are static analysis, not runtime-test results.

## Findings

### P2 — Credential redaction does not cover the requested argv shapes

**Exploit path:** A same-UID process with a deleted-scratch-path reason can have its argv emitted in the TSV command column. `redact_command` only recognizes `--token=`, `ghp_` followed by alphanumerics, `sk-`, `password=`, and URL userinfo (`tools/souji-proc-census.sh:186-211`). The `RevProcRedaction` required-shape list additionally calls for `-H`/`--header` Authorization values, `xoxb-`, `AKIA` keys, underscore-containing `ghp_` values, and case-insensitive token options (`.ufo/waves/round-18/w1/RevProcRedaction.md:17-27`). There is no Authorization/header, `xoxb-`, or `AKIA` recognizer in the implementation. Its `ghp_` regex ends at the first underscore after the prefix (`tools/souji-proc-census.sh:194-196`), so it can leave suffix material from a value such as `ghp_a_b` in the rendered argument. The fixture only includes the covered lowercase token, simple `ghp_`, `sk-`, password, and URL forms (`tests/fixtures/r18-proc-census.sh:419-420`), so its assertions do not falsify these omissions (`:468-472`).

**Impact:** `[INFERENCE]` argv matching these uncovered shapes will be printed without full redaction whenever the process qualifies for a row; downstream capture/logging can retain credential material. This is a real policy gap, not just the host-count limitation in the prior review.

**Smallest remediation:** Add complete-argument handling for the documented header and token forms and missing token families; extend the fixture with synthetic positive controls for each listed shape and assert every full secret is absent. Keep scanning full argv before clipping.

### P2 — UID check is not bound to the later `/proc/<pid>` reads

**Exploit path:** The scanner snapshots `stat`, checks the process starttime, then reads the first UID in `status` and compares it with `$UID` (`tools/souji-proc-census.sh:314-320`). It subsequently opens `/proc/$pid/cwd`, `cmdline`, `fd`, and `wchan`, then emits a row, without another identity/UID check (`:326-353`). `[INFERENCE]` If the checked process exits and its PID is reused by a different UID in that interval, a sufficiently privileged invocation can read the replacement process's data and associate it with the already-approved PID; this is the remaining other-UID disclosure path. It is a race, not an observed exploit.

**Impact:** Potential cross-UID argv/path disclosure under PID churn when the scanner has permission to read the replacement process.

**Smallest remediation:** Bind all reads to a stable `/proc/<pid>` task identity (or discard the row after a post-read UID and starttime mismatch); do not rely solely on the pre-read snapshot.

### P3 — Selftest group cleanup assumes recorded PGIDs have not gone stale

**Exploit path:** The EXIT cleanup sends `SIGKILL` to each negative recorded `$!` PID as a process-group ID (`tools/souji-proc-census.sh:363-372`); workers are launched with `setsid` and recorded from `$!` (`:422-436`). Under normal operation these are the test's private groups. `[INFERENCE]` If a worker and its group exit before cleanup, and that numeric PGID is reused before the EXIT trap, the unconditional group kill can signal the reused group. The check at `:440-445` only tests worker liveness before census, not identity at cleanup. This is a narrow PID/PGID-reuse race; no such signal was run or observed.

**Impact:** A selftest cleanup can theoretically signal a process group it did not create, contrary to the strict “only its own pids” claim.

**Smallest remediation:** Preserve a live ownership anchor for each test PGID through cleanup, or verify the expected group identity immediately before signaling and avoid signaling a stale/reused ID.

## Requested-property verdict

- **No `/proc/*/environ` read:** holds for reviewed source. Exact-file search found no `environ`; observed proc reads are stat/status/cmdline/cwd/fd/wchan plus global stat and boot ID.
- **No signaling outside `--selftest`:** holds in the ordinary census path. `SIGKILL` is only in the cleanup installed by `run_selftest`; `kill -0` is a selftest liveness probe (`:368`, `:402`, `:441`, `:490-495`).
- **Redaction before truncation:** ordering holds (`redact_command` applies recognizers before the 160-byte slice at `:190-211`; called before row output at `:347-355`). It does not make uncovered shapes safe; see P2 finding.
- **Other-UID exclusion:** ordinary code gates on the first `Uid:` value before reading argv/cwd/fds (`:141-150`, `:319-320`), but the unpinned-PID race above prevents a strict guarantee.
- **Output destination:** ordinary census rows/header are printed to stdout (`:308-309`, `:353-355`); diagnostics use stderr. Selftest intentionally captures its nested census in its generated `/var/tmp` output file and removes it in cleanup (`:398-409`, `:447`, `:380-382`). No caller-selected output file or environment dump was found.
- **Selftest cleanup ownership:** private `setsid` groups and own `$!` records are used, but cleanup lacks stale-PGID identity protection (P3).

**Overall verdict: FAILS the full security claim** because credential redaction omits required shapes and process identity is not pinned across sensitive `/proc` reads; selftest cleanup also has a narrow stale-PGID race. No tool was installed or updated.