STATUS: DONE — C1's TERM→SIGKILL escalation holds against a TERM-ignoring repo target (10/10 exact, no residue); one adjacent operability defect found in the same watchdog (inherited SIG_IGN TERM makes the per-repo watchdog unstoppable by TERM: +~2 s per healthy repo), plus a test-coverage gap.

# ProbeTermIgnoring — attack the SIGKILL escalation (C1)

Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`, tip `5efb519f00075d958c3d1109ef6fcb24c487eb87`.
Clone: `/var/tmp/souji-r18w2-ProbeTermIgnoring/lane` (detached at 5efb519), deleted after the probe.
Subject: `tools/souji-census.sh` @5efb519, sha256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`, 2625 lines.

## What was attacked

The C1 sentence “a timeout → row `<repo>\t0\t0\t0\t0\t\terror` + stderr `souji-census: repo-timeout <N>s <repo>` … others measured, exit 0”, specifically the escalation at `tools/souji-census.sh:1495-1498` (group TERM, `sleep 2`, group KILL, `killed` marker) against a repository whose git never dies on TERM.

Mechanism under test (read at tip): worker is a `set -m` background subshell with its own pgid (`:1478-1481`); a `setsid bash -c` watchdog polls `kill -0 -- -$pgid` (`:1482-1502`) and, at the bound, `kill -TERM -- -$pgid`, `sleep 2`, `kill -KILL -- -$pgid`. Parent waits for `killed`, reaps, and emits the placeholder (`:1591-1650`, `:1707`).

## A. Escalation holds (the assigned attack)

Fixture (only in `/var/tmp/.../`): 3 real repos `a b c`; `PATH` git shim matches `-C <fleet>/b` and runs
`trap '' TERM INT HUP; exec sleep 297` (the `sleep` inherits SIG_IGN across exec). Normal git is `exec /usr/bin/git "$@"` for every other call. Census run from the clone, own session, `--repo-timeout 3`.

Command shape:
`env PATH=<shim>:/usr/local/bin:/usr/bin:/bin R18_TARGET=<fleet>/b tools/souji-census.sh --root <fleet> --repo-timeout 3`

10/10 runs:
- rc 0; wall 5.581–5.587 s, mean 5.584 s for bound 3 (other repos measured).
- rows: `a …clean`, `b 0 0 0 0 <empty> error`, `c …clean` — exactly the 7-field placeholder.
- stderr exactly `souji-census: repo-timeout 3s /var/tmp/souji-r18w2-ProbeTermIgnoring/fleet/b`; no `repo-timeout-unreaped`.
- residue: the shim’s exec’d `sleep 297` pid absent after every run (`/proc/<pid>` gone; `ps` scan empty); no census/watchdog processes left.

KILL latency (3 instrumented reps; shim writes `pid epoch_ns`): shim start at +0.634/+0.636/+0.653 s; shim pid disappears at +5.597/+5.605/+5.607 s ⇒ **KILL lands 4.955/4.961/4.971 s after the worker started = bound + 2.0 s**. Total wall = other repos + (bound + 2) + ~0.2–0.6 s, so “≈ bound + 2 s” is exact per repo.

Variants, all exit 0 with the same row/diagnostic and no residue:
- 4-repo fleet, every repo matching, `--repo-timeout 1`: 12.633 s (≈3.16 s/repo), 4 error rows, 4 diagnostics.
- env path `SOUJI_CENSUS_REPO_TIMEOUT=2`: 4.829 s, same row/diagnostic.
- child-ignores-TERM (shim itself dies on TERM, background child has `trap '' TERM`): 5.872 s, row error.
- SIGSTOP’d shim: 5.824 s, row error.
- forged row on stdout + stderr noise before the hang: forged `999…clean` row did not leak; row is `error` (census_one captures git output; the row file is discarded on the timeout branch).

## B. Defect found in the same mechanism: inherited SIG_IGN TERM (P1)

The watchdog is started with `setsid bash -c …` (`:1482`) and inherits the census’s signal dispositions. On the *success* path the parent stops it with `kill -TERM -- "-$watchdog"` (`:1527`) then `wait "$watchdog"` (`:1528`). If the census was started with SIGTERM ignored, the watchdog ignores that TERM and `wait` blocks until the watchdog’s next 1 s poll notices the worker group is empty. Two watchdogs run per repo (preflight guard + `census_one`), so each healthy repo pays ~2 s.

Measured (healthy real repos, no shim, default bound 600; census launched with SIGTERM=SIG_IGN via `preexec_fn`, reproduced identically with `bash -c 'trap "" TERM; exec "$1" --root "$2"'`):
- 1 repo: 0.249 s normal → **2.051 s**
- 2 repos: 0.460 s → **4.058 s** (shell-level 4.077/4.078 s vs 0.478 s)
- 6 repos: 1.283 s → **12.086 s**
`ps` sampling of a 2-repo ignored-TERM run shows 4 watchdogs (guard+census per repo), each alive ~0.9–1.0 s; in a normal run each dies immediately on TERM. On a 200-repo fleet this is ~+6.7 min with zero diagnostics — an operability trap for any caller/supervisor that ignores TERM.

Fix validated in the clone (single-line mutant, deleted with the clone): `:1527` `kill -TERM` → `kill -KILL -- "-$watchdog"`. The watchdog owns no state on this path (the parent `rm -rf`s `state_path` at `:1530`), so KILL is safe.
- 2-repo ignored-TERM: **4.058 → 0.454 s**; 2-repo normal 0.453 s (no regression).
- shim timeout + ignored TERM: **10.09 → 5.583 s**, still `error` row + exact diagnostic.
`trap - TERM` is *not* a fix: bash cannot reset a signal ignored on entry (verified: a bash `-c` that does `trap - TERM; kill -TERM $$` prints `BASH-CANNOT-RESET`). `env --default-signal=TERM` can reset it, but the KILL change has no dependency.

## C. Coverage gap (P2)

No declared test exercises a target that survives TERM, so the KILL line (`:1497`) and `repo-timeout-unreaped` (`:1641`) have no regression test. Evidence from the files at tip:
- `tests/fixtures/r18-census-bounded.py`: B1–B4/B8 hang *real* git on a writer-less FIFO (`DEFAULT_REPO_TIMEOUT = 8`, `:34`; `require_timeout_diag` `:808-812`); B5 is slow-but-finite (`:1010-1046`). Real git dies on TERM, so the 2 s KILL is a no-op in every case.
- `tools/souji-census.sh` selftest (`:2340-2440`): `GIT_MODE=fifo` shim ends `exec "$real_git" "$@"` for non-`status` calls; its watchdog assertions (wall < 6000 ms, row, exact diagnostic) also run against a TERM-dies target.
- Grep for `trap ''`/`SIG_IGN` across `tools/souji-census.sh`, `tests/fixtures/r18-census-bounded.py`, `r17-census-hygiene.py`, `r15-census-config.py`, `r14-census-boundary.py`: no occurrence (only `GIT_TERMINAL_PROMPT`/`TERM` substrings).
Smallest fix: add a B9 that runs the fixture’s shim in a TERM-ignoring mode (`trap '' TERM; exec sleep 30`) under `--repo-timeout 2`, asserting the error row, the exact diagnostic, absence of `repo-timeout-unreaped`, and no survivor pid after exit.

## D. Observation: stderr gains a bash job line exactly when KILL is needed (P3)

In the KILL-needed case (worker itself became TERM-immune because the *census* inherited the ignore) the census’s stderr carries one extra line from bash job control:
`/var/tmp/…/souji-census.sh: line 1520: 3898627 Killed                     "$@" > "$row_file" 2> "$stderr_file"`
Minimal repro confirms it is bash behavior, not the script: a `set -m` background job reaped by `wait` prints `Killed` for SIGKILL and nothing for SIGTERM. Membership-based checks (`grep -Fqx`, `expected in splitlines()`) still pass, but any exact-stderr assertion would break. Confidence high; cosmetic.

## Verdict

- **C1 escalation: HOLDS.** A TERM-ignoring (even TERM-ignored-by-inheritance) repo is SIGKILLed at bound + 2.0 s, emitted as the exact placeholder row with the exact diagnostic, other repos measured, exit 0, no residue, 10/10. The asserted “≈ bound + 2 s” is per repo.
- **C1 operability: PARTIAL** — one defect in the same watchdog: inherited SIG_IGN TERM makes the success-path watchdog shutdown cost ~2 s per healthy repo (line `:1527`). One-line fix validated. C1’s timeout guarantee itself is unaffected.

Smallest fix: `tools/souji-census.sh:1527` `kill -TERM` → `kill -KILL -- "-$watchdog"` (or spawn the watchdog via `env --default-signal=TERM`), plus a B9 TERM-ignoring fixture case.

## Remaining unknowns

- `repo-timeout-unreaped` (`:1641`) not exercised: requires a group member in uninterruptible D state surviving SIGKILL; not constructible without kernel help.
- Preflight-guard timeout for non-`repo` candidate kinds (`:1678`) not exercised (the guard is file-only; no hang source without a hostile filesystem).
- I did not run the selftest or B1–B8 (outside my ALLOWED-EXEC); their coverage statements above come from reading the tip blobs, not from executing them.
- The P1 trigger is an environment condition (caller ignores SIGTERM), not a property of the fleet.

## Tooling

No installs or upgrades (only bash, coreutils, git, python3, ps already present). No network. Only processes started by this probe were signalled; all fixtures, the clone, and `/var/tmp/souji-r18w2-ProbeTermIgnoring/` were removed.
