# Round 16 / w1 — MutateScanConfig
STATUS: Probe complete: 8 single-line mutants; 5 killed, 3 survived (m2, m4, m6: fixture gaps); 0 inconclusive. Every pristine and restored detector run passed. m8 included an observed, bounded FIFO timeout. Scratch restored exactly, then deleted.
## Axes and scope
- **Operability:** challenge config-path protection and per-repository degradation without running a census on a real directory.
- **Calibration:** distinguish killed mutants from surviving coverage gaps; do not infer pristine-tool correctness from this sample or change the contract.
- Source: `cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh`, copied verbatim into `/var/tmp/souji-r16-MutateScanConfig/m1` through `m8`, each at `tools/souji-census.sh`. All tool line references below are to that committed source. Only one behavior-bearing line changed per copy. No sibling/production source changed.
- Behavioral commands: only the assigned full `r15-census-config.py --tool <copy>` and `r14-census-boundary.py --tool <copy>`, without case selection or additional flags. Each pair ran on pristine, mutated, and restored bytes for every copy: 48 fixture invocations. Independent synthetic worlds; at most four fixture processes at once.
- No delegation, commits, staging, live census, installs, upgrades, selftest, matrix, shellcheck, or additional behavioral probes.
## Mutants and observed verdicts
`r15` = `tests/fixtures/r15-census-config.py`; `r14` = `tests/fixtures/r14-census-boundary.py`. Counts below are passed cases; detector exit codes are distinct from the census exits printed in CASE details.
| Mutant | Source point | Single defect | Mutated r15 (exit; passed) | Mutated r14 (exit; passed) | Verdict / killing case IDs |
|---|---|---|---|---|---|
| m1 | `tools/souji-census.sh:614` (`scan_config_file`) | Drop include-target guard_config_path call | 1; 17/20 | 0; 12/12 | **killed**; R15CFG-02, R15CFG-11, R15CFG-17 |
| m2 | `tools/souji-census.sh:584` (`scan_config_file`) | Drop include-cycle equality check | 0; 20/20 | 0; 12/12 | **survived**; none — fixture gap |
| m3 | `tools/souji-census.sh:605` (`scan_config_file`) | Ignore includeIf.*.path keys | 1; 19/20 | 0; 12/12 | **killed**; R15CFG-02 |
| m4 | `tools/souji-census.sh:543` (`expand_config_path`) | Treat ~/ as literal base-relative text instead of expanding HOME | 0; 20/20 | 0; 12/12 | **survived**; none — fixture gap |
| m5 | `tools/souji-census.sh:530` (`guard_config_path`) | Return 1 instead of protected_fail for lexical protected reach | 1; 17/20 | 0; 12/12 | **killed**; R15CFG-02, R15CFG-11, R15CFG-17 |
| m6 | `tools/souji-census.sh:648` (`scan_config_file`) | Drop CFG_STACK pop after completed config scan | 0; 20/20 | 0; 12/12 | **survived**; none — fixture gap |
| m7 | `tools/souji-census.sh:617` (`scan_config_file`) | Do not recursively scan an existing include target | 1; 18/20 | 0; 12/12 | **killed**; R15CFG-02, R15CFG-03 |
| m8 | `tools/souji-census.sh:546` (`expand_config_path`) | Leave relative config path unanchored to its supplied base | 1; 17/20 | 0; 12/12 | **killed**; R15CFG-02, R15CFG-03, R15CFG-10 |

All eight mutated r14 runs printed `SUMMARY	total=12	failed=0`; r14 did not independently kill any of these config-only mutants. The r15 fixture supplied all five kills.
## Surviving mutants: concrete coverage findings
1. **m2 — cycle predicate absent, both detectors green.** Removed `tools/souji-census.sh:584`; the depth guard remains at line 582. The cycle fixture is `tests/fixtures/r15-census-config.py:466-468`, called by `case_03` at lines 1078-1084. Its soft oracle at lines 1010-1032 accepts the generic `config-unsupported` diagnostic without pinning the cycle-specific reason or early cutoff. [INFERENCE] The retained depth guard can compensate for the missing cycle check under the declared public degradation shape. This is a cycle-predicate discrimination gap, not evidence that the current C1 public contract is violated.
2. **m4 — missing HOME expansion undetected.** Replaced `tools/souji-census.sh:543` with literal base-relative treatment of `~/`. The benign tilde include at `tests/fixtures/r15-census-config.py:425-431` only sets `user.name`; `case_01` at lines 1053-1061 checks census rows. All 20 config cases still passed. [INFERENCE] A tilde include whose reachable config names a protected path would distinguish the required scan from this mutant; that additional probe was not run. This is a fixture gap in safety-relevant `~/` expansion, not permission to remove expansion.
3. **m6 — stack-pop omission undetected.** Removed `tools/souji-census.sh:648`; all 20 config cases and 12 boundary cases still passed. Existing benign includes at `tests/fixtures/r15-census-config.py:402-441` do not exercise a shared target repeatedly within a single scan traversal. [INFERENCE] A repeated or diamond-shaped benign include would expose stale entries being mistaken for an active cycle. No additional probe or fixture change was made.
## Expected detectors and actual output excerpts
Excerpts below are verbatim CASE/SUMMARY lines from captured stdout, not reconstructed results. The fixture records only the final invocation in `observed_exit`/`observed_finding` for multi-repository cases (`tests/fixtures/r15-census-config.py:1449-1455`); an earlier named subcase can fail while those trailing fields look correct. All 48 fixture invocations had empty stderr.
### m1 — killed

- Expected detector: R15CFG-02 (direct/includeIf/symlink store targets), R15CFG-17 (mixed unsafe fleet).
- Exact original line → mutated line:

```bash
        tgt=$(guard_config_path include-protected "$dir" "$cfg" "$tgt") || exit 2
# replaced with
        :
```

Actual r15 detector exit: `1`.

```text
CASE	R15CFG-02	FAIL	r-inc-store: exit=0 want 2; r-inc-store: finding path-protected missing from stderr; r-inc-store: stdout is not empty; r-inc-store: access: strace store access: 3829606 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7fffd79a2770, 0) = -1 EACCES (Permission denied) | 3833874 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7fffd79a0a20, 0) = -1 EACCES (Permission denied); r-incif-store: exit=0 want 2; r-incif-store: finding path-protected missing from stderr; r-incif-store: stdout is not empty; r-incif-store: access: strace store access: 3835981 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffc6a2d4200, 0) = -1 EACCES (Permission denied) | 3840004 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffc6a2d24b0, 0) = -1 EACCES (Permission denied); r-incif-hc-store: exit=0 want 2; r-incif-hc-store: finding path-protected missing from stderr; r-incif-hc-store: stdout is not empty; r-incif-hc-store: access: strace store access: 3845194 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffd31c8b4c0, 0) = -1 EACCES (Permission denied) | 3849565 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffd31c89770, 0) = -1 EACCES (Permission denied); r-incif-unknown: exit=0 want 2; r-incif-unknown: finding path-protected missing from stderr; r-incif-unknown: stdout is not empty; r-incif-unknown: access: strace store access: 3851332 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffd4cf36040, 0) = -1 EACCES (Permission denied) | 3854620 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffd4cf342f0, 0) = -1 EACCES (Permission denied); r-inc-nested: exit=0 want 2; r-inc-nested: finding path-protected missing from stderr; r-inc-nested: stdout is not empty; r-inc-nested: access: strace store access: 3859194 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7fffd994f5f0, 0) = -1 EACCES (Permission denied) | 3862549 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7fffd994d8a0, 0) = -1 EACCES (Permission denied); r-inc-symlink: exit=0 want 2; r-inc-symlink: finding path-protected missing from stderr; r-inc-symlink: stdout is not empty; r-inc-symlink: access: strace store access: 3864957 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/unsafe-repos/r-inc-symlink/.git/../link.inc", 0x7ffc4c43ef90, 0) = -1 EACCES (Permission denied) | 3869184 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/unsafe-repos/r-inc-symlink/.git/../link.inc", 0x7ffc4c43d240, 0) = -1 EACCES (Permission denied)	observed_exit=0	observed_finding=none
CASE	R15CFG-11	FAIL	r-wtc-hostile: exit=0 want 2; r-wtc-hostile: finding path-protected missing from stderr; r-wtc-hostile: stdout is not empty; r-wtc-hostile: access: strace store access: 4093894 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7fff87c86060, 0) = -1 EACCES (Permission denied) | 4096704 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7fff87c84310, 0) = -1 EACCES (Permission denied)	observed_exit=2	observed_finding=path-protected:git-config-unsupported
CASE	R15CFG-17	FAIL	exit=0 want 2; finding path-protected missing from stderr; stdout is not empty; access: strace store access: 4189547 newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffeae286f00, 0) = -1 EACCES (Permission denied) | 3486  newfstatat(AT_FDCWD</var/tmp/r15-census-config.6bhpwbwp>, "/var/tmp/r15-census-config.6bhpwbwp/home/.omp/agent/secret.gitconfig", 0x7ffeae284db0, 0) = -1 EACCES (Permission denied)	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=3
```

### m2 — survived

- Expected detector: R15CFG-03 r-inc-cycle; depth fallback may mask the missing cycle predicate.
- Exact original line → mutated line:

```bash
    if [ "$s" = "$cfg" ]; then cfg_soft "git-include-cycle"; return 1; fi
# replaced with
    :
```

Actual r15 detector exit: `0`.

```text
CASE	R15CFG-03	PASS	ok	observed_exit=0	observed_finding=config-unsupported:git-config-unparsed
SUMMARY	total=20	failed=0
```

### m3 — killed

- Expected detector: R15CFG-02 r-incif-store/r-incif-hc-store/r-incif-unknown.
- Exact original line → mutated line:

```bash
      include:path|includeif:path)
# replaced with
      include:path)
```

Actual r15 detector exit: `1`.

```text
CASE	R15CFG-02	FAIL	r-incif-store: exit=0 want 2; r-incif-store: finding path-protected missing from stderr; r-incif-store: stdout is not empty; r-incif-hc-store: exit=0 want 2; r-incif-hc-store: finding path-protected missing from stderr; r-incif-hc-store: stdout is not empty; r-incif-hc-store: access: strace store access: 3918520 access("/var/tmp/r15-census-config._txofral/home/.omp/agent/secret.gitconfig", R_OK) = -1 EACCES (Permission denied); r-incif-unknown: exit=0 want 2; r-incif-unknown: finding path-protected missing from stderr; r-incif-unknown: stdout is not empty	observed_exit=2	observed_finding=path-protected:include-protected
SUMMARY	total=20	failed=1
```

### m4 — survived

- Expected detector: R15CFG-01 r-inc-tilde; may survive because its include only changes user.name.
- Exact original line → mutated line:

```bash
    \~/*) [ -n "${HOME:-}" ] || return 1; v="$HOME/${v:2}" ;;
# replaced with
    \~/*) v="$base/$v" ;;
```

Actual r15 detector exit: `0`.

```text
CASE	R15CFG-01	PASS	ok	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=0
```

### m5 — killed

- Expected detector: R15CFG-02/R15CFG-11/R15CFG-17 require path-protected stderr finding.
- Exact original line → mutated line:

```bash
    protected_fail "$reason" "$dir" "$cfg"
# replaced with
    return 1
```

Actual r15 detector exit: `1`.

```text
CASE	R15CFG-02	FAIL	r-inc-store: finding path-protected missing from stderr; r-incif-store: finding path-protected missing from stderr; r-incif-hc-store: finding path-protected missing from stderr; r-incif-unknown: finding path-protected missing from stderr; r-inc-nested: finding path-protected missing from stderr	observed_exit=2	observed_finding=path-protected:include-protected
CASE	R15CFG-11	FAIL	r-wtc-hostile: finding path-protected missing from stderr; r-wtc-cwt: finding path-protected missing from stderr; r-attrs-store: finding path-protected missing from stderr; r-excl-store: finding path-protected missing from stderr	observed_exit=2	observed_finding=none
CASE	R15CFG-17	FAIL	finding path-protected missing from stderr	observed_exit=2	observed_finding=none
SUMMARY	total=20	failed=3
```

### m6 — survived

- Expected detector: A benign repeated/diamond include should fail falsely; existing R15CFG-01 may not reuse a target.
- Exact original line → mutated line:

```bash
  unset 'CFG_STACK[${#CFG_STACK[@]}-1]'
# replaced with
  :
```

Actual r15 detector exit: `0`.

```text
CASE	R15CFG-01	PASS	ok	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=0
```

### m7 — killed

- Expected detector: R15CFG-02 r-inc-nested and R15CFG-03 r-inc-cycle.
- Exact original line → mutated line:

```bash
        scan_config_file "$dir" "$tgt" $((depth + 1)) || return 1
# replaced with
        :
```

Actual r15 detector exit: `1`.

```text
CASE	R15CFG-02	FAIL	r-inc-nested: exit=0 want 2; r-inc-nested: finding path-protected missing from stderr; r-inc-nested: stdout is not empty; r-inc-nested: access: strace store access: 154739 access("/var/tmp/r15-census-config.snr4z_v6/home/.omp/agent/secret.gitconfig", R_OK) = -1 EACCES (Permission denied)	observed_exit=2	observed_finding=path-protected:include-protected
CASE	R15CFG-03	FAIL	r-inc-cycle: finding config-unsupported missing from stderr	observed_exit=0	observed_finding=config-unsupported:git-config-unparsed
SUMMARY	total=20	failed=2
```

### m8 — killed

- Expected detector: R15CFG-02 r-inc-nested/r-inc-symlink; R15CFG-03 cycle/FIFO.
- Exact original line → mutated line:

```bash
    *) v="$base/$v" ;;
# replaced with
    *) ;;
```

Actual r15 detector exit: `1`.

```text
CASE	R15CFG-02	FAIL	r-inc-nested: exit=0 want 2; r-inc-nested: finding path-protected missing from stderr; r-inc-nested: stdout is not empty; r-inc-nested: access: strace store access: 214048 access("/var/tmp/r15-census-config.qm1dqwgb/home/.omp/agent/secret.gitconfig", R_OK) = -1 EACCES (Permission denied); r-inc-symlink: exit=0 want 2; r-inc-symlink: finding path-protected missing from stderr; r-inc-symlink: stdout is not empty; r-inc-symlink: access: strace store access: 216657 access(".git/../link.inc", R_OK) = -1 EACCES (Permission denied)	observed_exit=0	observed_finding=none
CASE	R15CFG-03	FAIL	r-inc-cycle: finding config-unsupported missing from stderr; r-inc-fifo: exit=124 want 0; r-inc-fifo: finding config-unsupported missing from stderr; r-inc-fifo: census header missing; r-inc-fifo: rows [] want exactly one	observed_exit=0	observed_finding=config-unsupported:git-config-unparsed
CASE	R15CFG-10	FAIL	on-fleet: exit=2 want 0	observed_exit=2	observed_finding=path-protected:core-worktree-protected
SUMMARY	total=20	failed=3
```

For m8, the recorded `r-inc-fifo: exit=124 want 0` is the fixture's own 90-second bound (`tests/fixtures/r15-census-config.py:736-748`), not a baseline failure. Its same run also failed R15CFG-02 and R15CFG-10; kill classification does not rest solely on the timeout.
## Pristine and restoration evidence
Every copy began at 65,991 bytes with SHA-256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`. All eight were restored by reversing their one-line edit. `sha256sum` matched the pristine hash on every copy both before and after the restored detector runs.
| Copy | Pristine r15 / r14 | Restored r15 / r14 | Before / after restoration SHA |
|---|---|---|---|
| m1 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m2 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m3 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m4 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m5 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m6 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m7 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |
| m8 | exit 0, 20/20 / exit 0, 12/12 | exit 0, 20/20 / exit 0, 12/12 | `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` / `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` |

Mutated hashes (each distinct from pristine):

| Copy | SHA-256 while mutated |
|---|---|
| m1 | `53ee628242eb94b16fffa991e67750ef3eea9525559235485227ef61404f5af6` |
| m2 | `674fa51e3148bce287b7516da8750722b9bb998e0f747a5141725b63435c6d5b` |
| m3 | `a44a1f1e0bd42a8e0e5db5cc627010cb31da02211844203621e0b0be3e4d98cc` |
| m4 | `90217ca90bdff957ad9a5c969b8b311dce3e42150fe736c82b04f1f4ec8c0cbd` |
| m5 | `37314b9a60db9af9efb6227b740fe7150fd836283e2dfcc9a7471c6776131882` |
| m6 | `81f918c0016ba1c1359c776dd46148eea89e4010366c11a051fe64331e835339` |
| m7 | `6208affee59c361196ea54c31d11afc14cf1dcedcbe1e0e523ff3e26b1264bb3` |
| m8 | `308ba1660bc2eb02128a2620c5861d420db692dc82682f6befad85142f2b5a4a` |

Actual successful detector summary lines, emitted on every pristine and restored copy:

```text
SUMMARY	total=20	failed=0
SUMMARY	total=12	failed=0
```

Deletion used the Python API `shutil.rmtree` only on `/var/tmp/souji-r16-MutateScanConfig`, after restoration and the final hashes. Actual cleanup result:

```text
{'removed': '/var/tmp/souji-r16-MutateScanConfig', 'exists_after_removal': False}
```

Advisory findings only. No C1/C2 judgment, integration, contract adjustment, or acceptance run was performed. The three survivors are disclosed for L1 calibration.
## Commands
Every externally invoked command is listed verbatim below, including duplicate invocations, in launch order. The first `git show` was the direct tool read; the second captured the immutable bytes for API writes. All commands used absolute named target paths. Scratch creation, anchored edits/restoration, output capture/classification, and deletion used tool/Python APIs, not extra shell commands. No tools were installed or updated.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh
sha256sum /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
sha256sum /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
sha256sum /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
sha256sum /var/tmp/souji-r16-MutateScanConfig/m1/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m2/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m3/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m4/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m5/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m6/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m7/tools/souji-census.sh /var/tmp/souji-r16-MutateScanConfig/m8/tools/souji-census.sh
```
