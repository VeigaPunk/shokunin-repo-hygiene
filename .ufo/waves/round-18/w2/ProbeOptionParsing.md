STATUS: DONE — census `--repo-timeout`/env option contract exercised at 5efb519: every invalid value exits 2 with empty stdout and the exact message+usage on stderr; flag overrides env in both directions; verdict holds, with two totality/doc nits and no operability defect.

# ProbeOptionParsing — C1 option contract

Attacked claim (C1 operability, option clause): `tools/souji-census.sh` honours
`--repo-timeout N` / `SOUJI_CENSUS_REPO_TIMEOUT` (1..86400, default 600);
invalid values exit 2 as a usage error; the flag overrides the env var.

Seat sandbox: clone `/var/tmp/souji-r18w2-ProbeOptionParsing/lane`, checked out
detached at `5efb519f00075d958c3d1109ef6fcb24c487eb87` (`git rev-parse HEAD`
confirmed; `git status --porcelain` empty). All executions were
`./tools/souji-census.sh` from that clone; the default root is
`/var/tmp/souji-r18w2-ProbeOptionParsing` (one repo, the clone itself), so no
real/fleet directory was scanned. `env -u SOUJI_CENSUS_REPO_TIMEOUT` cleared
the env except where stated. Nothing in the lane or fleet was modified.

## Executed matrix (exact results)

| # | invocation | rc | stdout | stderr |
|---|---|---|---|---|
| 1 | `--repo-timeout 0` | 2 | 0 lines | 61 lines: `souji-census: invalid repo timeout (expected integer 1..86400)` + 60-line usage |
| 2 | `--repo-timeout -1` | 2 | 0 lines | identical to #1 |
| 3 | `--repo-timeout 86401` | 2 | 0 lines | identical to #1 |
| 4 | `--repo-timeout abc` | 2 | 0 lines | identical to #1 |
| 5 | `--repo-timeout 1e3` | 2 | 0 lines | identical to #1 |
| 6 | `--repo-timeout ' 5'` | 2 | 0 lines | identical to #1 |
| 7 | `--repo-timeout=7` | 0 | 2 lines (header + `lane` row) | empty |
| 8 | `SOUJI_CENSUS_REPO_TIMEOUT=abc` (no flag) | 2 | 0 lines | identical to #1 |
| 9 | `SOUJI_CENSUS_REPO_TIMEOUT=abc --repo-timeout 7` | 0 | 2 lines (header + row) | empty |
| 10 | `SOUJI_CENSUS_REPO_TIMEOUT=7 --repo-timeout abc` | 2 | 0 lines | identical to #1 |
| 11 | `--repo-timeout 1` | 0 | 2 lines | empty |

Boundary/adjacent probes: `--repo-timeout 86400` rc 0; `--repo-timeout 007`
rc 0 (normalised); `--repo-timeout=` rc 2 (`invalid repo timeout`); bare
`--repo-timeout` rc 2 (`--repo-timeout needs an integer`); `--repo-timeout -h`
rc 2 (`invalid repo timeout`, `-h` consumed as the value); `--bogus` rc 2
(`unknown flag: --bogus`); `--help` rc 0, 60 usage lines on stdout; `trailing`
positional rc 2; `--selftest --repo-timeout 0` rc 2 (selftest does not bypass
validation); `--repo-timeout 0 --help` rc 0 (see F2);
`--repo-timeout abc --repo-timeout 7` rc 0 and the reverse rc 2 (see F1).

All ten invalid-path stderr files were byte-identical
(sha256 `132337477468988bee7dff40dc93d21a6753bcc636036473fa8fb05ea1fffc5a`),
containing exactly one `souji-census: ` line followed by the 60-line usage.
`bash -n tools/souji-census.sh` rc 0; `shellcheck -S warning` 0.11.0 rc 0, no
findings. No tools installed or upgraded.

## Static trace (tools/souji-census.sh at 5efb519)

- `:220` `REPO_TIMEOUT="${SOUJI_CENSUS_REPO_TIMEOUT-600}"` — default 600; a
  set-but-empty env is kept as `''` (see F3).
- `:245-257` `validate_repo_timeout`: rejects non-digits/empty, strips leading
  zeros, rejects length >5 after stripping, then rejects `<1`/`>86400`; each
  failure calls `usage_err` → stderr message + usage, `exit 2` (`:230`,
  `:225-228`). Arithmetic operands are bounded, so no injection or overflow.
- `:2581-2601` parse loop: `--repo-timeout` requires a following token
  (`:$# -ge 2`, message is specific), `--repo-timeout=*` accepted;
  `-h|--help` calls `usage 0` immediately (`:2597`); unknown `-*` and bare
  operands are usage errors. No value is validated at assignment.
- `:2603` `validate_repo_timeout` runs before `run_selftest` (`:2605`) and
  before the `--root` requirement and `guard_path root`
  (`:2607-2621`), i.e. invalid timeout fails before any filesystem/git work.
- `:1500-1501` the validated global is passed as a positional argument to the
  per-repo `setsid` watchdog (`limit=$2`, `:1485`), not interpolated into
  script text; `run_repo_with_watchdog` does not shadow it.
- `:1925-1926` `run_selftest` reassigns `REPO_TIMEOUT=600` and exports it
  after validation (see F4).

## Findings

F1 (minor totality defect, observed). Repeated flags are last-wins because no
value is validated until `:2603`: `--repo-timeout abc --repo-timeout 7` exits
0, while `--repo-timeout 7 --repo-timeout abc` exits 2.
`:65` states unconditionally "invalid values exit 2"; it does not say the last
occurrence is the only one validated. Smallest fix: one doc clause at `:65`
("last `--repo-timeout` occurrence wins; earlier values are not validated"),
or, for behavioural totality, validate in the `:2584-2587` cases.

F2 (observation, conventional help precedence). Because `usage 0` exits inside
the loop at `:2597`, help placed after an invalid value suppresses the error:
`--repo-timeout 0 --help` → rc 0, usage on stdout. The `:65`
"invalid values exit 2" sentence has an undocumented help exception; no
operability impact (help was requested). Smallest fix if wanted: document the
exception on `:65`.

F3 (observation, env ergonomics). `${SOUJI_CENSUS_REPO_TIMEOUT-600}` treats a
set-but-empty env (`export SOUJI_CENSUS_REPO_TIMEOUT=`, common in templated
wrappers) as `''`, so validation rejects it with exit 2 rather than falling
back to 600. This matches the literal docs ("integer … (default: 600)";
empty is not an integer) but differs from the usual `${VAR:-600}` convention.
Not a claim violation; noted for operators. Static only (line 220/246).

F4 (doc gap, no behavioural fault). The `--repo-timeout=N` form accepted at
`:2587` is absent from the synopsis at `:17` and the option block at `:63-65`;
`--root=`/`--compare=` are in the same undocumented-equivalence family, so
this is consistent rather than a repo-timeout-specific bug. Also, a valid
`--repo-timeout` is validated and then overwritten by `--selftest` at
`:1925-1926` (selftest's own nested censuses pass explicit values), so the
flag is inert for `--selftest`. Smallest fix: add the `=` form to `:17` or
drop `:2587`.

No finding touches the operative guarantee: six invalid values and an invalid
env all exit 2 with empty stdout and the exact usage error; the valid flag and
env paths run, exit 0, and treat the flag as authoritative; validation
precedes selftest, root resolution and the protected-path guard; the validated
integer is the value handed to each per-repo watchdog.

## Verdict

C1 option contract: **holds**. The parser implements the documented 1..86400
range, default 600, override direction and exit-2 usage errors; every
enumerated invocation matched the claim byte-for-byte on rc and stderr.
Remaining defects are F1 (invalid earlier duplicate silently discarded), F2
(help bypasses validation) and F4 (undocumented `=` form / selftest
overwrite) — all doc-level, none harmful to operability. Smallest single fix:
document last-wins (and the help exception) at `tools/souji-census.sh:65`, or
validate at assignment to make "invalid values exit 2" literal.

## Residual unknowns

- Per-repo timeout enforcement (row `<repo>\t0\t0\t0\t0\t\terror`, stderr
  `… repo-timeout <N>s <repo>`, `repo-timeout-unreaped`, exit 0) was not
  re-executed here; it belongs to the bounded fixture arm. My matrix proves
  the value reaches the watchdog call site only statically (`:1500`).
- Default 600 is static-only: no observable difference between unset and an
  explicit 600 without a deliberately hanging repository.
- Selftest check counts (49→62) were not evaluated (out of seat scope).
