## Status
STATUS: PASS — C2 items T11 and T15 PASS the frozen counter under bwrap (`items=2 pass=2 fail=0`), with each patched command keeping the base run's exit code and last digit-bearing line and losing almost no file work; three files delivered, one file (tools/souji-verify.sh) measured no-change.

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; items/counter read at prereg `3ec84fc81b3243429c834a051880b0bcde06291c`; patch commit `af031c1d0be0f5c7a3fbccafbb2aa2aa202ee7cc` in a throwaway clone (`/fast/scratch/hyaku/souji-r32/C2Struct/r.2888/c`, origin removed, `rev-parse --show-toplevel` verified). The lane worktree and index were not modified.

## Evidence

### 1. Red-before at base (`--rev` = base, both runs base)
Command (cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`):
`python3 -B census/round-32/c2-counter.py --root <clone> --rev 85b61a151923986e7e6b48f7084b9122561b5f3d --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T11,T15 --scratch /fast/scratch/hyaku/souji-r32/C2Struct/cnt-base`

```
ITEM	T11	FAIL	base=rc0:W542:selftest=PASS ids=7/7	sbox=rc2:W2:id=SOUJI-R13-STRUCT-SETUP error=mktemp failed under /var/tmp	regress work-dropped
ITEM	T15	FAIL	base=rc0:W2545:selftest: 49 checks, 0 failed	sbox=rc1:W1734:selftest: 34 checks, 1 failed	regress
SUMMARY items=2 pass=0 fail=2 partial=1 rev=85b61a151923986e7e6b48f7084b9122561b5f3d
```
counter rc=1. T15's sandboxed tail also carried the cause: `mktemp: failed to create directory via template '/var/tmp/souji-round9-selftest.XXXXXX': Read-only file system`.

### 2. Green after patch (`--rev` = patch commit)
Command (cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`):
`python3 -B census/round-32/c2-counter.py --root <clone> --rev af031c1d0be0f5c7a3fbccafbb2aa2aa202ee7cc --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only T11,T15 --scratch /fast/scratch/hyaku/souji-r32/C2Struct/cnt`

```
ITEM	T11	PASS	base=rc0:W542:selftest=PASS ids=7/7	sbox=rc0:W537:selftest=PASS ids=7/7
ITEM	T15	PASS	base=rc0:W2542:selftest: 49 checks, 0 failed	sbox=rc0:W2545:selftest: 49 checks, 0 failed
SUMMARY items=2 pass=2 fail=0 partial=1 rev=af031c1d0be0f5c7a3fbccafbb2aa2aa202ee7cc
```
counter rc=0. T11 file-creating syscalls: 537 sandboxed vs 542 base (99.1 %); T15: 2545 vs 2542. Last lines and exit codes equal in both directions.

### 3. Patched commands once normally, once with TMPDIR unset
In the patch clone, `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` and `bash tools/souji-verify.sh --selftest`:

```
T11 TMPDIR=<scratch>/t5   rc=0  selftest=PASS ids=7/7
T11 env -u TMPDIR         rc=0  selftest=PASS ids=7/7
T15 TMPDIR=<scratch>/t3   rc=0  selftest: 49 checks, 0 failed
T15 env -u TMPDIR         rc=0  selftest: 49 checks, 0 failed
```
T11/T15 also pass inside the same bwrap sandbox by hand (`TMPDIR=<scratch>/t6`, `t4`): `rc=0` / `selftest=PASS ids=7/7` and `rc=0` / `selftest: 49 checks, 0 failed`.

### 4. Residual-write sweep for tools/souji-verify.sh (no-change evidence)
`strace -f -qq -o <log> -e trace=mkdir,mkdirat,creat,open,openat,openat2 bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm --chdir <clone> bash tools/souji-verify.sh --selftest` with `TMPDIR=<scratch>/t7`: `rc=0`, `selftest: 49 checks, 0 failed`. Grepping the trace for operands under `/tmp/`, `/var/tmp/` or `/dev/shm/`, excluding the caller scratch root and `/fast/scratch`, returned 0 lines.

## Findings
1. T15's remaining sandboxed failure was not in `tools/souji-verify.sh`: the selftest delegates at `tools/souji-verify.sh:1485` (`r9_out=$(bash "$SCRIPT_DIR/souji-round9-selftest.sh" verify "$SELF") || r9_rc=$?`, base) to `tools/souji-round9-selftest.sh`, whose line 7 is `R9_TMP=$(mktemp -d -p /var/tmp souji-round9-selftest.XXXXXX)` and whose line 14 is `export TMPDIR=/var/tmp GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null` (base). Both hard-coded `/var/tmp`; the read-only sandbox made mktemp fail, the runner printed no `ROUND9\tN\tM` summary, and verify counted `FAIL R9 runner missing summary exit=1` — exactly `34 checks, 1 failed`.
2. `tools/souji-round9-selftest.sh` is outside the frozen C2 enumeration (c2-items header excludes `souji-round9-*`), but it is a runtime dependency of item T15, so patching it is required for T15 to pass; it is delivered as a third file.
3. T11 needed two independent repairs. (a) `tools/souji-repo-structure.sh:265` is `probe_tmp="$(mktemp -d /var/tmp/souji-repo-structure.XXXXXX)" || {` and `tests/fixtures/r13-repo-structure.sh:188-189` is `WORK="$(mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX)" ||` / `die2 "mktemp failed under /var/tmp"` (base). (b) After the mktemp repair alone the sandboxed fixture still failed: its measured invocation runs under `env -i` with a fixed allowlist (`tests/fixtures/r13-repo-structure.sh:220`, `# Allowlist for the measured invocation: no inherited Git_* can leak in.`), which stripped `TMPDIR`, so the probe fell back to read-only `/var/tmp` and exited 2. Adding `TMPDIR=${TMPDIR:-/var/tmp}` to that allowlist is the second half of the fix; the allowlist's other entries and the `env -i` isolation are unchanged.
4. `tools/souji-verify.sh` needed no edit: its line 539 (`export TMPDIR="${TMPDIR:-/var/tmp}"`, base) and line 1164 (`ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX")`, base) already take the caller's TMPDIR, and §4 shows zero residual operands under the read-only roots. Leaving it untouched keeps its output identical.
5. Changes are path-root-only: the probe still creates one capture directory and deletes it on exit; the fixture still writes only under `WORK`/`$HOME` under that root; the round9 runner still writes only under `R9_TMP`. No check id, case, verdict string, summary format or exit code was altered; base and patched last lines and exit codes are byte-equal (counter §2).
6. [INFERENCE] The `/var/tmp` literals in `souji-verify.sh` remain as fallbacks used only when the caller leaves TMPDIR unset; they are not reached under the operator scratch discipline, so they were not changed (behaviour-preserving scope).

## Deliveries
- `.ufo/waves/round-32/w1/deliver-souji-repo-structure.sh` — sha256 d9aa3b0c4afda53c6845bb88d7297a3e361abf8a0b138db0d3b174d51e3c5751
- `.ufo/waves/round-32/w1/deliver-r13-repo-structure.sh` — sha256 1a3e012dec0e291f99fa2820d1e3c20337f639b0124a5d19924e86c629e9a04e
- `.ufo/waves/round-32/w1/deliver-souji-round9-selftest.sh` — sha256 1dc5be9a590852d6ea5d65fdc688aad360a7b896ee9d09871776e220adf58aa4
- `.ufo/waves/round-32/w1/deliver-SwarmExecutor11.diff` — `git -C <clone> diff 85b61a151923986e7e6b48f7084b9122561b5f3d -- tools/souji-repo-structure.sh tests/fixtures/r13-repo-structure.sh tools/souji-round9-selftest.sh` (99 lines, 3 files, +14/-11)

Tooling: nothing installed or upgraded this wave (no pacman transaction; `python3`, `git`, `bwrap`, `strace` already on PATH). Scratch `/fast/scratch/hyaku/souji-r32/C2Struct` removed after delivery.
