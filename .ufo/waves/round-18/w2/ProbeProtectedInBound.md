STATUS: DONE — protected refusal under `--repo-timeout 3` exits 2 with zero stdout in every detectable static variant, including after a real timeout in the same run; one undetected-by-timeout path exits 0 (documented degrade, no store access).

# Attack: C1 "protected refusal still exit 2"

Claim under attack: `tools/souji-census.sh` (5efb519f00075d958c3d1109ef6fcb24c487eb87,
sha256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`) keeps the
r14 protected boundary under the round-18 per-repo watchdog: a repo whose config
include names the credential store must still abort the whole run with exit 2 and no
partial census table, next to a hanging neighbour, with `--repo-timeout 3`.

Fixture (all under `/var/tmp/souji-r18w2-ProbeProtectedInBound/`, never a real store):
synthetic `HOME=$W/home`, `$W/home/.omp/agent/{config.yml,inc.cfg}` created then chmod 000
(canary `R18W2-CANARY-…`); repo `<fleet>/50-protected/.git/config` gets
`[include]\n path = $W/home/.omp/agent/inc.cfg`; hanging neighbour
`<fleet>/00-hang` is a valid repo with a FIFO `.gitignore` (blocks `git status`
with no shim; control c1 below).

Command shape for every case:

```
env -u GIT_DIR -u GIT_WORK_TREE HOME=$W/home TMPDIR=/var/tmp LC_ALL=C \
  PATH=/usr/local/bin:/usr/bin:/bin \
  bash /var/tmp/souji-r18w2-ProbeProtectedInBound/lane/tools/souji-census.sh \
    --root <fleet> --repo-timeout 3
```

## Result matrix (rc / stdout bytes / stderr)

| case | fleet | rc | stdout | stderr |
|---|---|---|---|---|
| c1 | only `00-hang` (control) | 0 | 151 B: exact `…\t0\t0\t0\t0\t\terror` row | `souji-census: repo-timeout 3s …/00-hang` |
| c2 | `00-hang` + `50-protected` | **2** | **0 B** | `path-protected: include-protected (…/50-protected/.git: …/.git/config)`; no `repo-timeout` |
| c3 | protected first (`~/` include) + hang | **2** | **0 B** | same finding |
| c4 | include via symlink alias into store | **2** | **0 B** | same finding |
| c5 | slow-guard `10-big` + `90-protected` | **2** | **0 B** | `repo-timeout 3s …/10-big` **and** `path-protected …/90-protected`; wall 5195 ms |
| c7 | FIFO `info/attributes` + protected include | **2** | **0 B** | `path-protected` |
| c8 | hardlinked `info/attributes` + protected include | **2** | **0 B** | `path-protected` |
| c9 | `00-hang` + `90-clean` (control) | 0 | header + error row + `clean` row | `repo-timeout 3s …/00-hang`; wall 5390 ms |
| c10 | c2 fleet, `SOUJI_CENSUS_REPO_TIMEOUT=3`, no flag | **2** | **0 B** | `path-protected` |
| c11 | c2 fleet, `--repo-timeout 1` | **2** | **0 B** | `path-protected` |
| c6/c12 | >3 s config **with** the protected include at its end | 0 | header + `error` row + `clean` row | `repo-timeout 3s …/10-bigprot`; **no** `path-protected` |

## Findings

**F1 — Holds: the refusal is detected in the list-phase guard, before any row exists.**
`emit_census` runs every candidate through `run_repo_with_watchdog` *first*
(`tools/souji-census.sh:1676`), and a repo candidate's guard calls
`guard_git_surface` (`:1442-1446`), which reaches the include branch
(`:766-771`) → `guard_config_path` → `protected_fail` (`:265-272`). The header is
printed only after both loops (`:1719`), and rows are accumulated in `rows[]`, so
stdout is empty by construction on exit 2. Observed: c2/c3/c4/c10/c11 all 0-byte stdout,
one finding line, 157–293 ms. `--repo-timeout 1`, `3`, and the env form behave identically.

**F2 — Holds: a genuine timeout earlier in the same run does not mask the refusal.**
c5 forces the guard of `10-big` to exceed the bound (943,718,403-byte comment-only
config; scan cost measured at ~1.1 s/256 MB, so >3 s). The watchdog fires
(`repo-timeout 3s`, wall 5195 ms, exit of the timed-out worker reaped), the loop
continues, then `90-protected` refuses: exit 2, 0-byte stdout. Code agrees:
`run_repo_with_watchdog` resets `REPO_TIMED_OUT` per repo (`:1476`), preserves rc 2
and clears the timeout flag (`:1645-1647`), and `emit_census` exits 2 from both the
guard loop (`:1676`) and the census loop (`:1705`) before printing the header.

**F3 — Holds: r17 soft metadata does not downgrade a refusal.** A FIFO (c7) or
hardlinked (c8) `.git/info/attributes` sets the soft reason but the config scan still
runs (`guard_git_files` then `guard_git_config`, `:958-959`), so the protected include
still aborts the run: exit 2, empty stdout — not the `error` row a lone soft finding
would produce.

**F4 — Holds: no store access.** Under `strace -f -e trace=%file`, the named scenario
(c2) and the hidden-include scenario (c12) show **0** path hits under
`…/world/home/.omp/agent`; the store is mode 000 and the canary never appears in any
stdout/stderr capture. `guard_config_path` refuses before `[ -e ]`,
`guard_config_file_kind` or `scan_config_file` (`:634-651`), so the include target is
never opened. No fixture processes were left after any run.

**F5 — Boundary (not a contract violation, but the claim's wording over-reaches):
a timeout-truncated scan yields exit 0 with a full table.** c6/c12 puts the same
protected include at the *end* of a config whose scan exceeds 3 s. The guard is killed
before it parses the include; the repo becomes a preflight timeout, is skipped entirely
(placeholder row `…\t0\t0\t0\t0\t\terror`), the neighbour is measured, and the run exits
0 with header + 2 rows (265 B). `strace`: 0 store hits and no git command ran in the
repo, so nothing protected was read. This matches the documented round-18 timeout
semantics ("a timed-out repository gets the row", `:158-163`), but the doc's "Config
outcomes: Refused (exit 2)" paragraph does not say the guarantee is conditional on the
config scan finishing within N. So "protected refusal still exit 2" holds only for a
refusal that the bound lets the guard *detect*.

## Unexercised path (code read, not run)

A refusal raised in the **second** guard pass (`census_one`, `:1304-1312`) cannot be
reached by a static fixture: the list-phase guard (`:1442-1446`) runs the identical
`guard_git_surface`, so any static protected include is always refused preflight — as
every case above shows. The lane's own selftest forces that ordering with a git shim
(`:2508-2538`, "census_one protected refusal remains exit 2"). Code propagation there
is rc 2 → `:1645-1647` → `:1705` → exit 2 with the header still unprinted, but I did
not execute it (no shim is named in this seat's ALLOWED-EXEC, and the fixtures here
must not carry lane helpers). This is a residual gap in my evidence, not a defect.

## Verdict

**holds** for every detected refusal: exit 2, zero-byte stdout, no partial table, no
store access, independent of N form (1, 3, env) and of ordering relative to a hanging
neighbour or a real guard-phase timeout. Side observation: in a static fleet the
protected include is refused during preflight, so the named "hanging neighbour" is
never measured (c2 wall 293 ms, no `repo-timeout` line) — refusal preempts the timeout
instead of interleaving with it.

Smallest fix: none required for the claim; one documentation clause under
`--repo-timeout` — "a repo whose guard scan exceeds N is skipped as an `error` row
(exit 0), so a protected config path beyond the N-second scan point is not refused" —
would make the conditional guarantee explicit (c6/c12).

## Method / compliance

- Clone `/var/tmp/souji-r18w2-ProbeProtectedInBound/lane` at 5efb519 (detached);
  scratch under the same root, all fixtures under `/var/tmp`; no real store read.
- Only `tools/souji-census.sh` was executed (plus read-only git setup and `strace`);
  no lane/fleet writes except this report; no `jj`; no git writes in the lane.
- Tool installs: none.
