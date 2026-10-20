STATUS: DONE — hostile `BASH_FUNC_sleep` + `SOUJI_CENSUS_REPO_TIMEOUT=1`: selftest 62/0, rc 0; every write confined to `/var/tmp/souji-census-*`; tempdirs and processes fully reclaimed

# Attack — C1 selftest isolation under a hostile shell environment

Question attacked (verbatim): at 5efb519, run `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` with `SOUJI_CENSUS_REPO_TIMEOUT=1` and `BASH_FUNC_sleep%%=() { :; }` exported — does the selftest still pass and stay isolated (no writes outside its tempdir; no residue)?

Clone: `/var/tmp/souji-r18w2-ProbeCensusSelftestIsolation/lane` @ `5efb519f00075d958c3d1109ef6fcb24c487eb87` (`git rev-parse` verified). No lane/fleet writes; no tool installs (pacman paused host-wide, nothing needed).

## Why the hostile input is inert (static, all paths at 5efb519)

- `tools/souji-census.sh:180` — `unset -f bash cat git kill find du stat awk grep sort head cut date readlink sleep mktemp setsid mkdir rm`: the imported `BASH_FUNC_sleep` is removed before any command runs.
- `:1920-1921` — `ST_TMP=$(mktemp -d /var/tmp/souji-census-selftest.XXXXXX)`; `trap 'rm -rf -- "$ST_TMP"' EXIT`.
- `:1925-1926` — `REPO_TIMEOUT=600; export SOUJI_CENSUS_REPO_TIMEOUT="$REPO_TIMEOUT"` **before** any fixture is built, so the outer `1` cannot shorten a fixture's bound. The env var is only exercised for refusal of 86401 (`:2549-2556`).
- Temp roots hardcode `/var/tmp` (`:240`, `:1817`, `:1920`); `TMPDIR` is never consulted, so `TMPDIR=/var/tmp` is a no-op here (and is not what confines the run).

## Runtime results (exact commands)

| arm | command | rc | checks |
|---|---|---|---|
| control | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` | 0 | 62 PASS / 0 FAIL, 36.35 s |
| graded | `env -u GIT_DIR TMPDIR=/var/tmp SOUJI_CENSUS_REPO_TIMEOUT=1 'BASH_FUNC_sleep%%=() { :; }' bash tools/souji-census.sh --selftest` | 0 | 62 PASS / 0 FAIL, 36.32 s |

`diff control.out hostile.out` — four hunks only: `mtime_iso` fixture stamp, `watchdog wall time` ms, `two-second Git calls` ms, random `ST_TMP` name. Parent stderr: 0 bytes in both arms. The 62 count matches the claim's tip number (the 49 baseline was not re-run — ALLOWED-EXEC is 5efb519 only: residual unknown).

Hostile import was real: `env 'BASH_FUNC_sleep%%=() { :; }' bash -c 'declare -F sleep; … sleep 1 …'` → prints `sleep`, 0 ms; after `unset -f sleep` the same probe sleeps 201 ms. End-to-end, the graded run traced **472** `execve("/usr/bin/sleep")` (534 in the first trace): the function was gone and the real sleeper ran.

## Isolation — every write target resolved

Same command/env under `strace -f -yy` (trace3): 64,484 parsed syscalls with file-write intent; 1,185 distinct targets, **0 unresolved** (relative/`dirfd` targets resolved via `AT_FDCWD<…>`/fd annotations and per-pid `chdir`):

- 1,181 distinct targets / 2,687 write ops under `/var/tmp/souji-census-*` — the only filesystem writes.
- `/dev/null` 3,078 write-opens (expected sinks: `GIT_CONFIG_GLOBAL=/dev/null`, `core.hooksPath=/dev/null`, redirections); `/dev/tty` 146 + 5 resumed, all `-1 ENXIO` (bash job-control probe, no terminal); `mkdir("/var")` ×15 and `"tmp"` ×15, all `EEXIST` (coreutils `mkdir -p` component walk).
- **Zero** writes/creates/unlinks under the lane clone, `$HOME`, `XDG_CONFIG_HOME`, or any other path. The selftest's own containment assertion PASSed: `:2570 case "$fleet" in "$ST_TMP"/*`.

## No residue

- 11 temp roots created (1 `selftest` + 10 `now`) and 11 removed exactly once; created−removed = ∅, removed−created = ∅, none removed twice (trace3).
- `ST_TMP` from each run absent immediately after exit (`JFrMHv`, `Vk6jfz`, `FLiNJ9`); host `/var/tmp` held only peers' live census dirs at times, never a name from my runs.
- Clone clean: `git status --porcelain=v1 -uno` empty, HEAD still 5efb519.
- No process from this seat survives (`ps` filtered on my lane path: no census/watchdog). Host observation, not attributed: older seats' **pre-r18** `souji-census.sh` processes (r16/r17 clones) remain parked on `r-inc-fifo` roots since 11:00–16:00 — consistent with the hang C1 fixes; not signalled.

Timing checks passed in both arms (control 3855 ms / 18372 ms over 9 calls; graded 3873 ms / 18346 ms) — the exported `1` did not bound the fixtures; `--repo-timeout 1` at `:2402` is the only 1 s bound, and it is the intentional FIFO case.

## Adjacent gap (static only — not executed, outside ALLOWED-EXEC)

The `:180` unset list is incomplete for names the script uses for **verdicts and a guard**: `cmp` at `:738` (NUL-poisoned config soft-degrade) and `:2013` (`repeat: two runs byte-identical` PASS); `tr` at `:738`; `python3` at `:2443` (`timed-out FIFO has no reader` PASS). A hostile `BASH_FUNC_cmp%%=() { return 0; }` makes `:2013` pass vacuously and skips the `:738` NUL check; `BASH_FUNC_python3` does the same at `:2443`; a `tr` shadow fails closed (every config degrades). No fixture tests `BASH_FUNC_*` (`grep`: only the comment at `:178`). Severity LOW (requires a hostile environment, which the tool elects to defend). Smallest fix: add `cmp python3 tr` to the `:180` list (plus `ln mkfifo chmod touch diff basename` if sweeping fixture-only commands).

## Verdict

**HOLDS** for the graded question: with `SOUJI_CENSUS_REPO_TIMEOUT=1` and a live hostile `BASH_FUNC_sleep` exported, the selftest still passes 62/0 (rc 0), writes only inside its own `/var/tmp/souji-census-*` tempdirs (plus expected `/dev/null` sinks and failed `EEXIST`/`ENXIO` probes), and leaves no files, tempdirs, or processes behind. The only defect found is the separate LOW-severity unset-list gap above, which the hostile-sleep probe does not reach.
