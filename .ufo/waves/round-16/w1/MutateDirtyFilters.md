# C1 status-path mutation probe — MutateDirtyFilters

**Axes:** operability; calibration.

STATUS: SURVIVED M02 — disabling the HOME/.config/git default passes both allowed detectors. Seven of eight mutants were killed; zero probes were inconclusive. This is a coverage finding, not permission to weaken C1.

## Scope and controls

- Sampled only `tools/souji-census.sh`; eight one-line mutations, each in an isolated copy under `/var/tmp/souji-r16-MutateDirtyFilters/M01` through `M08`.
- For every copy, ran exactly the same full config fixture and legacy selftest on pristine, mutated, and byte-restored content: 48 detector executions total, at most four detector processes concurrently. No additional fixture flags, narrowed cases, live census, alternative detector, commit, staging, or lane-source edit.
- All eight pristine pairs and all eight restored pairs returned exit 0: config `SUMMARY\ttotal=20\tfailed=0`; selftest `selftest: 38 checks, 0 failed`. No timeouts, setup failures, or nonempty captured stderr from any detector.
- The initial copy-creation anchor assertion for M05 failed before any detector ran; the remaining copies were created after matching the displayed continuation line. This was not a behavioral baseline failure.
- No tools were installed or updated.

## Mutants, expected detector, and measured verdict

Line references below are to the sampled lane source. Each mutation changed only the named line.

| Mutant | Source site and defect | Expected detector | Mutated config output / exit | Mutated selftest output / exit | Verdict |
| --- | --- | --- | --- | --- | --- |
| M01 | `tools/souji-census.sh:881` (status_info_file): Force explicit excludes/attributes to /dev/null | R15CFG-04 honored excludes row | `SUMMARY total=20 failed=1`; rc 1 | `selftest: 38 checks, 0 failed`; rc 0 | **killed** |
| M02 | `tools/souji-census.sh:884` (status_info_file): Ignore HOME/.config/git fallback when XDG_CONFIG_HOME is unset | Default XDG/HOME ignore or attributes fidelity (coverage may be absent) | `SUMMARY total=20 failed=0`; rc 0 | `selftest: 38 checks, 0 failed`; rc 0 | **survived** |
| M03 | `tools/souji-census.sh:920` (guard_bound_filters): Return success immediately for configured filter drivers | R15CFG-14 status-skipped row and bound-filter execution sentry | `SUMMARY total=20 failed=5`; rc 1 | `selftest: 38 checks, 0 failed`; rc 0 | **killed** |
| M04 | `tools/souji-census.sh:926` (guard_bound_filters): Read the attribute-name slot rather than the value slot | R15CFG-14 status-skipped row and bound-filter execution sentry | `SUMMARY total=20 failed=1`; rc 1 | `selftest: 38 checks, 0 failed`; rc 0 | **killed** |
| M05 | `tools/souji-census.sh:949` (count_dirty): Suppress untracked paths in status dirty counts | R15CFG-04/05 dirty fidelity and selftest dirty assertions | `SUMMARY total=20 failed=2`; rc 1 | `selftest: 38 checks, 3 failed`; rc 1 | **killed** |
| M06 | `tools/souji-census.sh:954` (count_dirty): Treat failed git status as clean | R15CFG-07 invalid-promisor status-unverifiable row | `SUMMARY total=20 failed=1`; rc 1 | `selftest: 38 checks, 0 failed`; rc 0 | **killed** |
| M07 | `tools/souji-census.sh:1090` (census_one): Emit clean instead of error for could-not-evaluate config | R15CFG-03 per-repository error-row assertion | `SUMMARY total=20 failed=1`; rc 1 | `selftest: 38 checks, 0 failed`; rc 0 | **killed** |
| M08 | `tools/souji-census.sh:147` (GIT_NO_LAZY_FETCH): Keep lazy-fetch prevention shell-local instead of exported | R15CFG-08 GIT_NO_LAZY_FETCH=1 pin on every git call | `SUMMARY total=20 failed=1`; rc 1 | `selftest: 38 checks, 0 failed`; rc 0 | **killed** |

## Actual failure output

All failed CASE/FAIL lines are reproduced verbatim below. Successful cases are represented by the actual summary lines in the table and the control results above.

### M01

Mutation: `    printf '%s' "$tgt"` → `    printf '/dev/null'`

config, exit 1:

```text
CASE	R15CFG-04	FAIL	r-excl-all: dirty=1 want 0; r-excl-all: verdict_flags=dirty want clean	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=1
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```


### M02

Mutation: `  base=${XDG_CONFIG_HOME:-}` → `  base=${XDG_CONFIG_HOME:-/dev/null}`

config, exit 0:

```text
SUMMARY	total=20	failed=0
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```


### M03

Mutation: `  [ "${#drivers[@]}" -gt 0 ] || return 0` → `  [ "${#drivers[@]}" -gt 0 ] && return 0`

config, exit 1:

```text
CASE	R15CFG-08	FAIL	exec: fsmonitor sentinel sentinel-fsmonitor was created	observed_exit=0	observed_finding=none
CASE	R15CFG-11	FAIL	exec: fsmonitor sentinel sentinel-fsmonitor was created; exec: fsmonitor sentinel sentinel-fsmonitor was created; exec: fsmonitor sentinel sentinel-fsmonitor was created; exec: fsmonitor sentinel sentinel-fsmonitor was created	observed_exit=2	observed_finding=path-protected:git-config-unsupported
CASE	R15CFG-14	FAIL	r-filter-clean: r-filter-clean: verdict_flags=unpushed want unpushed,status-unverifiable; r-filter-process: r-filter-process: verdict_flags=unpushed want unpushed,status-unverifiable; status-skipped diagnostic missing from stderr; status-skipped diagnostic missing from stderr; exec: bound-filter sentinel sentinel-bound-filter was created	observed_exit=0	observed_finding=none
CASE	R15CFG-17	FAIL	exec: fsmonitor sentinel sentinel-fsmonitor was created	observed_exit=2	observed_finding=path-protected:include-protected
CASE	R15CFG-19	FAIL	exec: fsmonitor sentinel sentinel-fsmonitor was created; exec: fsmonitor sentinel sentinel-fsmonitor was created	observed_exit=2	observed_finding=path-protected:credential-store
SUMMARY	total=20	failed=5
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```


### M04

Mutation: `  for ((i = 2; i < ${#recs[@]}; i += 3)); do` → `  for ((i = 1; i < ${#recs[@]}; i += 3)); do`

config, exit 1:

```text
CASE	R15CFG-14	FAIL	r-filter-clean: r-filter-clean: verdict_flags=unpushed want unpushed,status-unverifiable; r-filter-process: r-filter-process: verdict_flags=unpushed want unpushed,status-unverifiable; status-skipped diagnostic missing from stderr; status-skipped diagnostic missing from stderr; exec: bound-filter sentinel sentinel-bound-filter was created	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=1
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```


### M05

Mutation: `      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \` → `      -c core.attributesFile="$at" status --porcelain --untracked-files=no --ignore-submodules=all -- . \`

config, exit 1:

```text
CASE	R15CFG-04	FAIL	r-excl-devnull: dirty=0 want 1; r-excl-devnull: verdict_flags=clean want dirty	observed_exit=0	observed_finding=none
CASE	R15CFG-05	FAIL	r-dirty: dirty=1 want 2	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=2
```

selftest, exit 1:

```text
FAIL dirty count=0 want 2
FAIL dirty flags='clean,scratch,secret-shaped'
FAIL compare missing dirty row
selftest: 38 checks, 3 failed
```


### M06

Mutation: `    printf 'unverifiable'` → `    printf '0'`

config, exit 1:

```text
CASE	R15CFG-07	FAIL	r-prom-maybe: r-prom-maybe: verdict_flags=clean want status-unverifiable; r-prom-maybe2: r-prom-maybe2: verdict_flags=clean want status-unverifiable	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=1
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```


### M07

Mutation: `    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"` → `    printf '%s\t0\t0\t0\t0\t\tclean\n' "$(sanitize_field "$repo")"`

config, exit 1:

```text
CASE	R15CFG-03	FAIL	r-inc-cycle: r-inc-cycle: row ['0', '0', '0', '0', '', 'clean'] want zero counts + error; r-inc-tildeuser: r-inc-tildeuser: row ['0', '0', '0', '0', '', 'clean'] want zero counts + error; r-inc-fifo: r-inc-fifo: row ['0', '0', '0', '0', '', 'clean'] want zero counts + error; r-cfg-nul: r-cfg-nul: row ['0', '0', '0', '0', '', 'clean'] want zero counts + error; r-wtc-maybe: r-wtc-maybe: row ['0', '0', '0', '0', '', 'clean'] want zero counts + error	observed_exit=0	observed_finding=config-unsupported:git-config-unparsed
SUMMARY	total=20	failed=1
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```


### M08

Mutation: `export GIT_NO_LAZY_FETCH=1` → `GIT_NO_LAZY_FETCH=1`

config, exit 1:

```text
CASE	R15CFG-08	FAIL	env: GIT_NO_LAZY_FETCH values ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''] want all 1	observed_exit=0	observed_finding=none
SUMMARY	total=20	failed=1
```

selftest, exit 0:

```text
selftest: 38 checks, 0 failed
```

## Coverage interpretation

- **Operability:** the config fixture detects disabled explicit excludes, a skipped filter guard, a check-attr triplet off-by-one, suppressed untracked files, a falsely clean failed status, a falsely clean soft-config row, and missing exported lazy-fetch protection. The legacy selftest kills only M05 in this set; it survives the other seven status/config regressions.
- **Calibration:** M02 replaces `base=${XDG_CONFIG_HOME:-}` with `base=${XDG_CONFIG_HOME:-/dev/null}` at `tools/souji-census.sh:884`. When XDG_CONFIG_HOME is unset, the nonempty `/dev/null` base bypasses the HOME/.config fallback at lines 885–887. Both actual detectors stay green (20/20 and 38/38). [INFERENCE] Default-file fidelity therefore has a coverage gap in these detectors; this probe did not add or run another default-file scenario.
- M03 also produced fsmonitor-sentinel failures in R15CFG-08/11/17/19, in addition to the expected R15CFG-14 bound-filter execution and row failures. Those observed extra failures are retained above rather than reduced to the expected signal. They are not counted as additional independent mutants.
- The bound-filter oracle is concrete: `tests/fixtures/r15-census-config.py:1225–1237` requires dirty=0, status-unverifiable, a status-skipped diagnostic, and no bound-filter sentinel. The lazy-fetch oracle is at lines 928–935; the soft-config error-row case is at lines 1078–1084; explicit excludes fidelity is at lines 1087–1102.

## Hashes and exact restoration

Pristine sampled SHA-256 (**P**): `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`.

Fixture SHA-256 at both initial and final hash calls: `9151cde8817d283376f089797ededd5896bc8812feb05f180ccc59760e1eb1af`.

Every detector recorded its input hash immediately before and after execution. All 48 before/after pairs were equal. Both mutated detectors for each copy saw the mutant hash below; both pristine and both restored detectors saw P.

| Copy | Pristine before/after | Mutated before/after SHA-256 | Restored before/after |
| --- | --- | --- | --- |
| M01 | P / P | `16255b44b097e5c5302aa3e267777a27e0a8c97da7675663d584e9d17e5f76ee` | P / P |
| M02 | P / P | `97de76826deae98edfe4ca4a1fa12c15f4fbb1bfd50fd4350e9836dd90643423` | P / P |
| M03 | P / P | `4f98c87f5ffd201eb8a4c4187e61effef55d0091f6c6a57118d80639fcfe421c` | P / P |
| M04 | P / P | `d25c15673d816b7f91fc126b0446c1a7cfd3c86e930b0cb20abee2982b83da5e` | P / P |
| M05 | P / P | `80513ed68a927c9da33a6bce647d49bc9304dad38c62268e881d6f5e51a79f05` | P / P |
| M06 | P / P | `e25a7e4ddac2672b3cd7758135dd5fa1b5408b02d5fc2baf6713c63e6ab3319b` | P / P |
| M07 | P / P | `66f741502122cc2641f4681610115f0437d88e92b17f9d59b39cc041ab846940` | P / P |
| M08 | P / P | `607f7dea2a2510516eb911c5ffbce024a31550fe63a49b355a52d2c62f5da97e` | P / P |

After restoring every changed line, a separate `sha256sum` call independently reported P for all eight scratch scripts. Each restored copy again passed both full detectors. The scratch directory was then deleted with Python `shutil.rmtree`; the immediately observed absence check returned `True`.

**Concurrent source drift:** the final hash call reported live lane `tools/souji-census.sh` SHA-256 `feba44c7a598888844debb84efe4d29d90869f0dd640ea3f0229969eacd1aa88`, different from P. This seat never edited that path. Results are pinned to the initially captured P bytes, not a claim about the later live bytes. No re-probe or source overwrite was performed.

## Commands

All direct shell commands and detector invocations are listed below, in start order. Detector lines show the exact argv with `TMPDIR=/var/tmp`; they were executed by Python subprocess without a shell, with cwd `/var/tmp/souji-r16-MutateDirtyFilters`. The two `sha256sum` commands used the lane cwd. File copying, mode setting, assertions, hash capture, and cleanup used Python Eval/file tools, not additional shell commands. Mutations and restorations used the edit tool. Repeated command lines correspond to the pristine, mutated, and restored phases, respectively.

```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh --selftest
TMPDIR=/var/tmp python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py --tool /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh
TMPDIR=/var/tmp bash /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh --selftest
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /var/tmp/souji-r16-MutateDirtyFilters/M01/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M02/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M03/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M04/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M05/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M06/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M07/souji-census.sh /var/tmp/souji-r16-MutateDirtyFilters/M08/souji-census.sh
```
