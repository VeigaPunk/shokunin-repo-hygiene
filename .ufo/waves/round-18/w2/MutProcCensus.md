STATUS: PARTIAL — Six isolated mutation probes completed and restored; two mutants survived both detectors; the environ-read class was not executed because the seat contract forbids every /proc/*/environ read.

# C3 process-census detector mutation probe

Attacked claim: C3 coverage in `tools/souji-proc-census.sh`, tested by `tests/fixtures/r18-proc-census.sh` P1–P11 and the tool's `--selftest`, at landed commit `5efb519f00075d958c3d1109ef6fcb24c487eb87` only. This is a detector-coverage report, not a judgment that the pristine implementation violates C3, and no lane source was fixed.

Axes: mutation sensitivity; valid pristine/mutated/restored attribution; process and byte isolation. Independent detector commands were run concurrently, initially four at a time, then two after an observed pristine P4 failure. That failure was retained, not rerun or reclassified as a mutant kill.

## Killed/survived table

Triples are actual exit codes in **pristine / mutated / restored** order on the same per-mutant pathname. Fixture success means `SUMMARY	total=11	failed=0`; selftest success means the exact PASS line in the raw ledger below. No outer 75-second timeout fired.

| Mutant | Expected detector | Fixture triple / result | Selftest triple / result | Combined result |
|---|---|---|---|---|
| Drop fd class | P9; selftest `fd` check | 0 / 1 / 0 — **killed**, P9 | 0 / 1 / 0 — **killed**, `fd=0` | Killed |
| Prefix without component boundary | P4 / boundary control | 0 / 0 / 0 — **survived** | 0 / 0 / 0 — **survived** | Survived |
| Redaction off | P6; selftest secret check | 0 / 1 / 0 — **killed**, malformed-row cascade, including P6 | 0 / 1 / 0 — **killed**, `redaction=0` | Killed |
| Emit a kill: SIGCONT to scanner's own recorded PID | P7 / no-signalling claim | 0 / 0 / 0 — **survived** | 0 / 0 / 0 — **survived** | Survived; narrowly tests a nonlethal self-signal, not termination of an unrelated process |
| Wrong precedence: fd overrides an existing reason | Mixed-reason precedence assertion | 1 / 0 / 0 — **inconclusive**, pristine P4 failed | 0 / 0 / 0 — **survived** | Inconclusive as a detector pair; selftest survivor |
| Age from PPID instead of start ticks | P1 freshness and P5 minimum age | 0 / 1 / 0 — **killed**, P1 and P5 | 0 / 0 / 0 — **survived** | Killed by fixture only |
| Read environ | No-environ observation | Not run | Not run | Unexercised: higher-priority seat rule forbids all `/proc/*/environ` reads, including synthetic/self environments |

Totals among six exercised mutants: fixture 3 killed / 2 survived / 1 inconclusive; selftest 2 killed / 4 survived; combined 3 killed / 2 survived / 1 inconclusive. The seventh class has no result and is excluded from these totals.

## Findings and smallest detector fixes

1. **Prefix component-boundary mutant survives both detectors.** Implementation membership and stripping are at `tools/souji-proc-census.sh:154-179`. Fixture P4 uses two differently named, randomly suffixed roots (`tests/fixtures/r18-proc-census.sh:306-322,401-416`), not one root and a similarly prefixed sibling. P10 only tests a deleted nested path under a live top (`:324-328,471-472`). The selftest creates a `/tmpfoo/...` argv control at `tools/souji-proc-census.sh:419,434`, but invokes the scanner with **only `/var/tmp`** at `:447`; that control cannot challenge `/tmp` component matching. [INFERENCE] For prefix `/var/tmp/root` and missing argv `/var/tmp/root-other/gone`, the mutant accepts the raw prefix and derives a missing `/var/tmp/root/-other`, thereby allowing an out-of-component row. Smallest fix: add a missing-argv worker in an explicitly similarly prefixed sibling, scan the shorter root, and assert omission; make the selftest's boundary control actually share the scanned prefix.

2. **P7 does not establish “never signals.”** P7 checks only fixture-worker liveness (`tests/fixtures/r18-proc-census.sh:240-249,453-454`). A real `kill -CONT -- "$SELF_PID"` before every census survived P1–P11 and selftest. The mutant logs its own exact Bash PID immediately before that command, and `set -e` plus successful detector runs require that the nonzero-fatal kill command did not fail. It does not use a process-name/prefix target. Four observed target records were 1839717, 1860763, 1891764 and 1948430, all census processes created through this probe's detector calls. No destructive signal was sent to a fleet process. Smallest fix: observe/deny scanner signal syscalls during the census invocation, while excluding the harness's own cleanup signals; a liveness-only assertion cannot prove the no-signal contract. This probe does not claim to test a lethal signal against a fixture worker.

3. **Reason-precedence coverage is incomplete, with a contaminated fixture baseline.** The real fd guard at `tools/souji-proc-census.sh:333-339` protects earlier cwd/argv reasons. Replacing it with a live-proc-directory guard permits fd reasons to overwrite either earlier reason. The fixture's workers isolate cwd (`tests/fixtures/r18-proc-census.sh:289-304`), argv (`:306-322`) and fd (`:330-343`) causes; the selftest similarly constructs separate workers (`tools/souji-proc-census.sh:422-435`). Both mutated commands passed. However, the *same-path pristine fixture* had P4 FAIL, so that fixture trial is **inconclusive**, not a survivor or kill. The selftest had passing pristine/restored controls and genuinely survived this mutant. Smallest fix: add dual-cause workers (cwd+fd, argv+fd, and cwd+argv) and assert the declared cwd > argv > fd ordering; retain/report baseline failures rather than laundering them into kills.

4. **Age is checked by P1/P5, not by selftest.** The PPID age mutant at `tools/souji-proc-census.sh:321` was killed by the fixture's fresh-age bounds (`tests/fixtures/r18-proc-census.sh:357-375,418-435`), but the selftest's row checks (`tools/souji-proc-census.sh:459-486`) ignore age. No additional age fix is required to kill this mutant with the combined named detector pair; a selftest-only coverage claim should be narrowed or supplied an age assertion.

5. **Observed pristine failure remains unresolved.** `probe-wrong-precedence.sh` contained pristine bytes during its first fixture run, yet P4 emitted `FAIL	--prefix did not select P2/exclude P6 (ok)` and the fixture exited 1; all ten other cases passed. The fixture suppresses the captured per-invocation rc/stderr in that failure detail (`tests/fixtures/r18-proc-census.sh:163-185,401-416`), so this evidence does not establish a cause. Later restored output is recorded because the required restoration detector was run, not as a confirmatory rerun. Smallest diagnostic improvement: include the failed invocation's rc, timed_out flag and stderr when P4 fails.

Verdict: **partial detector coverage**. Two fully controlled mutants survive both named detectors, another survives selftest but has an inconclusive fixture control, and one requested mutation class cannot be safely exercised under the stated contract. These are coverage findings, not permission to weaken C3.

## Mutation definitions

Every probe file began as exact pristine bytes. Each received only its named mutation and was restored immediately after the mutation phase. Paths below are under `/var/tmp/souji-r18w2-MutProcCensus/lane/tools/`; the canonical tool and fixture were never edited.

### `probe-drop-fd.sh`

Before:
```bash
      find_deleted_fd_path "$proc_path" || true
```
Mutated:
```bash
      PROC_FD_GONE_PATH=''
```

### `probe-prefix-no-boundary.sh`

Before:
```bash
  path_under_prefix "$path" "$prefix" || return 1
  if [[ $prefix == / ]]; then
    remainder=${path#/}
  else
    remainder=${path#"$prefix"/}
  fi
```
Mutated:
```bash
  [[ $path == "$prefix"* ]] || return 1
  remainder=${path#"$prefix"}
  remainder=${remainder#/}
```

### `probe-redaction-off.sh`

Before:
```bash
    redact_command "$CMD_RAW"
```
Mutated:
```bash
    REDACTED_CMD=${CMD_RAW:0:160}
```

### `probe-signal-self.sh`

Before:
```bash
  local proc_path pid now_epoch clock_ticks age reason cwd wchan snapshot_start
```
Mutated:
```bash
  local proc_path pid now_epoch clock_ticks age reason cwd wchan snapshot_start
  printf 'SIGCONT\t%s\n' "$SELF_PID" >> '/var/tmp/souji-r18w2-MutProcCensus/signal-pids.tsv'
  kill -CONT -- "$SELF_PID"
```

### `probe-wrong-precedence.sh`

Before:
```bash
    if [[ -z $reason ]]; then
```
Mutated:
```bash
    if [[ -d $proc_path ]]; then
```

### `probe-age-from-ppid.sh`

Before:
```bash
    age=$((now_epoch - BOOT_TIME - PROC_STARTTICKS / clock_ticks))
```
Mutated:
```bash
    age=$((now_epoch - BOOT_TIME - PROC_PPID / clock_ticks))
```

## Exact checkout and detector execution

Checkout command (exit 0, no stdout/stderr):
```sh
git clone --quiet --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r18w2-MutProcCensus/lane && git -C /var/tmp/souji-r18w2-MutProcCensus/lane checkout --quiet --detach 5efb519f00075d958c3d1109ef6fcb24c487eb87
```

The raw ledger below lists every actual argv and its exact captured stdout/stderr, including common pristine controls and all six same-path triples (38 commands). All cwd values were `/var/tmp/souji-r18w2-MutProcCensus/lane`. The Python capture wrapper used `start_new_session=True`, DEVNULL stdin, stdout/stderr PIPEs, and `communicate(timeout=75)`; its timeout path could SIGKILL only that recorded child's process group. That path never fired. The unchanged fixture itself has a 12-second per-tool timeout and private worker sessions (`tests/fixtures/r18-proc-census.sh:94,116-125,163-185`). The fixture and selftest necessarily allocate their hard-coded private `/var/tmp/souji-*` scratch locations; no detector was pointed at a real repository or fleet directory. No environ was read. No tool was installed or upgraded.

## Before / mutant / restored SHA-256

Pristine source and every restored probe file have SHA-256:
`c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc`.
The untouched fixture before and after has SHA-256:
`f79124cf67cd77a6409568031f5377ee8d20c1f539f10ad0775047e04133390c`.

Mutant hashes were actually captured by `sha256sum` after applying the edits. A second `sha256sum` over the canonical tool, fixture and all six restored probes showed each probe byte-for-byte identical to the original source hash above.

| Probe | Before | Mutated | Restored |
|---|---|---|---|
| drop-fd | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` | `a09fe4da9846a33fd19aae72e73e79bc0735eab74ab0222c96056a6ef29e3222` | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` |
| prefix-no-boundary | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` | `b409b1e0c5af611c539cd14c35828a1af8805649130b7d37ae8baf6ade276b39` | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` |
| redaction-off | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` | `2fb543effa5e36bce7d8dc05d204bf6b3d2101be7145f5532b1c5f82a4f38b52` | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` |
| signal-self | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` | `d0feb209a8113e148a7cd229d3f612d71d80db28a393526498ad816d11915883` | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` |
| wrong-precedence | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` | `115f87798066f3ca53c6a61245b29ab52df5ed747865eb2cce01dbdfbc7613cb` | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` |
| age-from-ppid | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` | `517db2ca98322f4a8e74213fe70146ced50ef0c607b710fb893bf93eb3079873` | `c2ea79602865c701821489c507afa1f5709cb372d689624176ae8bb0264c70dc` |

Exact hash commands:
```sh
sha256sum /var/tmp/souji-r18w2-MutProcCensus/lane/tools/souji-proc-census.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh
sha256sum /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh
sha256sum /var/tmp/souji-r18w2-MutProcCensus/lane/tools/souji-proc-census.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh
```

Owned signal-PID evidence (recorded immediately before the inserted kill):
```text
SIGCONT	1839717
SIGCONT	1860763
SIGCONT	1891764
SIGCONT	1948430
```

## Raw detector ledger

### pristine-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/souji-proc-census.sh
```
Recorded launcher PID: 504428; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### pristine-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/souji-proc-census.sh --selftest
```
Recorded launcher PID: 504431; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### drop-fd-before-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh
```
Recorded launcher PID: 789895; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### drop-fd-before-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh --selftest
```
Recorded launcher PID: 789893; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### prefix-no-boundary-before-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh
```
Recorded launcher PID: 789902; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### prefix-no-boundary-before-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh --selftest
```
Recorded launcher PID: 789904; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### redaction-off-before-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh
```
Recorded launcher PID: 893808; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### redaction-off-before-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh --selftest
```
Recorded launcher PID: 894093; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 214: /proc/649987/cmdline: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/656551/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/657104/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/657371/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/657689/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/658567/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/658984/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/659154/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/659411/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/659649/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/659958/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/661920/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/662232/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/662470/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/662507/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/662740/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/663144/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 141: /proc/663429/status: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/664580/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/664656/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 141: /proc/665285/status: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/665876/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/666063/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/666138/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/666285/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/666929/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/666958/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/667031/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/669087/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/669737/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 214: /proc/672138/cmdline: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/679343/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/679988/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 141: /proc/681806/status: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/682763/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/683247/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/683717/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/685151/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/685621/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/685669/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/685735/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/686141/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/686909/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/687333/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/687850/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/688275/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/688329/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/689288/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/695885/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/696937/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/697458/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 141: /proc/698734/status: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/699116/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/699646/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/701695/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/701981/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/702277/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/702319/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/702972/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/703271/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/703610/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/703852/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/703888/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/704062/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/704599/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/704638/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/705039/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/705368/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/705664/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/706357/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/706483/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/706953/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/706978/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/707227/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/707292/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/707329/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/707738/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/707794/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/707880/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/708171/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/708287/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/708404/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/708450/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/709376/stat: No such file or directory
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh: line 113: /proc/709419/stat: No such file or directory
```

### signal-self-before-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh
```
Recorded launcher PID: 997648; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### signal-self-before-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh --selftest
```
Recorded launcher PID: 1070256; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### wrong-precedence-before-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh
```
Recorded launcher PID: 1070476; exit: 1; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	FAIL	--prefix did not select P2/exclude P6 (ok)
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=1
```
stderr:
```text
```

### wrong-precedence-before-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh --selftest
```
Recorded launcher PID: 1139463; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### age-from-ppid-before-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh
```
Recorded launcher PID: 1143574; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### age-from-ppid-before-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh --selftest
```
Recorded launcher PID: 1209816; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### drop-fd-mutated-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh
```
Recorded launcher PID: 1624242; exit: 1; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	FAIL	missing or wrong fd-path-gone row
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=1
```
stderr:
```text
```

### drop-fd-mutated-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh --selftest
```
Recorded launcher PID: 1624241; exit: 1; outer timeout: false.

stdout:
```text
```
stderr:
```text
/var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh: line 214: /proc/1620842/cmdline: No such file or directory
souji-proc-census: selftest failed (reader=1 reader_wchan=1 sleeper=1 argv=1 fd=0 control=0 redaction=1)
```

### prefix-no-boundary-mutated-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh
```
Recorded launcher PID: 1633863; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### prefix-no-boundary-mutated-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh --selftest
```
Recorded launcher PID: 1647440; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### redaction-off-mutated-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh
```
Recorded launcher PID: 1706223; exit: 1; outer timeout: false.

stdout:
```text
CASE	P1	FAIL	missing FIFO reader row (malformed row)
CASE	P2	FAIL	missing or wrong argv-path-gone row
CASE	P3	FAIL	live control listed or census unusable
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	FAIL	missing P6 row or secret not redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	FAIL	missing or wrong fd-path-gone row
CASE	P10	FAIL	nested boundary was listed
CASE	P11	FAIL	starttime mismatch reported=None stat=3020289
SUMMARY	total=11	failed=7
```
stderr:
```text
```

### redaction-off-mutated-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh --selftest
```
Recorded launcher PID: 1779011; exit: 1; outer timeout: false.

stdout:
```text
```
stderr:
```text
souji-proc-census: selftest failed (reader=1 reader_wchan=1 sleeper=1 argv=1 fd=1 control=0 redaction=0)
```

### signal-self-mutated-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh
```
Recorded launcher PID: 1839262; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### signal-self-mutated-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh --selftest
```
Recorded launcher PID: 1857400; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### wrong-precedence-mutated-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh
```
Recorded launcher PID: 1916522; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### wrong-precedence-mutated-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh --selftest
```
Recorded launcher PID: 1992067; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### age-from-ppid-mutated-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh
```
Recorded launcher PID: 2047176; exit: 1; outer timeout: false.

stdout:
```text
CASE	P1	FAIL	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	FAIL	--min-age retained a fresh worker (ok)
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=2
```
stderr:
```text
```

### age-from-ppid-mutated-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh --selftest
```
Recorded launcher PID: 2069530; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### drop-fd-restored-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh
```
Recorded launcher PID: 2321423; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### drop-fd-restored-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-drop-fd.sh --selftest
```
Recorded launcher PID: 2321422; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### prefix-no-boundary-restored-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh
```
Recorded launcher PID: 2358794; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### prefix-no-boundary-restored-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-prefix-no-boundary.sh --selftest
```
Recorded launcher PID: 2421842; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### redaction-off-restored-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh
```
Recorded launcher PID: 2459288; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### redaction-off-restored-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-redaction-off.sh --selftest
```
Recorded launcher PID: 2459333; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### signal-self-restored-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh
```
Recorded launcher PID: 2493740; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### signal-self-restored-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-signal-self.sh --selftest
```
Recorded launcher PID: 2551885; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### wrong-precedence-restored-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh
```
Recorded launcher PID: 2586504; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### wrong-precedence-restored-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-wrong-precedence.sh --selftest
```
Recorded launcher PID: 2586509; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

### age-from-ppid-restored-fixture

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tests/fixtures/r18-proc-census.sh --tool /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh
```
Recorded launcher PID: 2623548; exit: 0; outer timeout: false.

stdout:
```text
CASE	P1	PASS	cwd-deleted wchan='wait_for_partner' setup-wchan='wait_for_partner'
CASE	P2	PASS	argv-path-gone row present
CASE	P3	PASS	live control absent
CASE	P4	PASS	prefix retained P2 and excluded P6
CASE	P5	PASS	fresh P1/P2/P6/P9 excluded
CASE	P6	PASS	secret-shaped argv redacted
CASE	P7	PASS	all fixture workers remain alive
CASE	P8	PASS	invalid usage exited 2
CASE	P9	PASS	deleted stdout fd reported
CASE	P10	PASS	deleted nested boundary omitted
CASE	P11	PASS	starttime matches /proc field 22
SUMMARY	total=11	failed=0
```
stderr:
```text
```

### age-from-ppid-restored-selftest

```sh
bash /var/tmp/souji-r18w2-MutProcCensus/lane/tools/probe-age-from-ppid.sh --selftest
```
Recorded launcher PID: 2703701; exit: 0; outer timeout: false.

stdout:
```text
souji-proc-census: selftest PASS (deleted cwd, wchan, missing argv option path, deleted fd, control omission, secret redaction)
```
stderr:
```text
```

## Scratch cleanup

After exact-byte restoration and all required restored detector runs, the following command completed with exit 0 and empty stdout/stderr:
```sh
rm -rf -- /var/tmp/souji-r18w2-MutProcCensus
```
The isolated clone, mutant files, source backup, signal ledger and raw scratch logs were removed. Their complete detector outputs and source hashes are preserved above. The only retained lane write is this assigned report; no lane source, fleet state, or sibling checkout was modified.
