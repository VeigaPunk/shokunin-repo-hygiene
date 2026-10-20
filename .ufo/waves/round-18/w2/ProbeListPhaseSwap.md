STATUS: DONE — C1's census_one watchdog holds exactly; C1's row promise FAILS for the one FIFO-reachable list-phase guard timeout (linked-worktree `.git`), and a post-guard non-regular metadata file still aborts the fleet with exit 2 and zero rows.

# ProbeListPhaseSwap — C1 operability, new list-phase swap

Attacked: **C1** — "every repository (list-phase guards and census_one) runs in its own process group under `--repo-timeout`/`SOUJI_CENSUS_REPO_TIMEOUT`; a timeout → row `<repo>\t0\t0\t0\t0\t\terror` + stderr `souji-census: repo-timeout <N>s <repo>`; others measured, exit 0". Tip `5efb519f00075d958c3d1109ef6fcb24c487eb87` (`tools/souji-census.sh` sha256 `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`), baseline `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (sha256 `006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd`). Both read in `/var/tmp` clones; nothing in the lane was modified.

## Method

Two clones (`/var/tmp/souji-r18w2-ProbeListPhaseSwap/lane` @5efb519, `lane-b` @b576341), synthetic roots `/var/tmp/souji-r18w2-ProbeListPhaseSwap/work/<arm>-<M>/root` with repos `a`, `b`, `c`; `b` carries a `commondir` gitfile-style layout plus a registered linked worktree `wt` outside the root (and a `.git/objects/info/alternates` variant for M7/M8). A PATH `git` shim (`shim/git`, first match only) plants the FIFO at an exact invocation:

- `when=census`: at `git -C <root>/a worktree list` — the first census-phase Git call, i.e. **after every candidate guard has passed** (guards run first, `tools/souji-census.sh:1665-1688`; census loop at `:1691`).
- `when=guard`: at `git config --file <root>/a/.git/config` — inside `a`'s candidate guard; glob order is sorted, so `a` precedes `b`.
- `when=revparse`: at `git -C <root>/b rev-parse --is-inside-work-tree` — after `census_one(b)`'s own re-guard (`:1307-1311`).

Runs: `env -u GIT_DIR PATH=<shim>:$PATH SOUJI_CENSUS_REPO_TIMEOUT=5 timeout -k 2 40 bash <lane>/tools/souji-census.sh --root <root>`. A 100 ms poller recorded pid/ppid/pgid/sid/state/wchan/`fd/1`/cmdline for every process belonging to the run; survivors (only processes this harness started) were recorded and killed by pid; `/var/tmp/souji-census-now.*` set diffed around each run (that namespace is shared with other seats, so only `fd/1`-attributed dirs are claimed). Full logs: `/var/tmp/souji-r18w2-ProbeListPhaseSwap/out/<label>/`, timelines `.../state/<label>/timeline.raw`.

Micro-check of what Git actually opens (same host, `/var/tmp`): `.git` FIFO → `fatal: not a regular file` in **1 ms** rc 128; `.git/commondir` FIFO → `git rev-parse` **blocks** (3 s outer timeout, rc 124); `.git/worktrees/wt/gitdir` FIFO → `git worktree list` **blocks** (3 s, rc 124); `.git/objects/info/alternates` FIFO → `git rev-parse` blocks (observed live in M8, `wchan=wait_for_partner`).

## Matrix (rc / wall / data rows / stderr lines / survivors)

| shape (b swap) | tip 5efb519 | base b576341 |
|---|---|---|
| M0 control | 0 / 1394 ms / 3 clean / 0 / 0 | 0 / 1044 / 3 clean / 0 / 0 |
| M1 `commondir` FIFO, census phase | **2** / 669 / **0 rows** / 1 / 0 | 2 / 345 / 0 rows / 1 / 0 |
| M2 `worktrees/wt/gitdir` FIFO, census phase | 0 / 7825 / a clean, **b `0 0 0 0 "" error`**, c clean / 1 / 0 | **124 / 40001 / 0 rows / 0** |
| M3 `.git`→FIFO after guard | 0 / 773 / b error / 0 / 0 | 0 / 427 / b error / 0 / 0 |
| M4 root gitfile `.git`→FIFO after guard read | 0 / 360 / b error / 0 / 0 | 0 / 147 / b error / 0 / 0 |
| M5 `worktrees/wt/gitdir` FIFO, during a's guard | 0 / 7839 / b error, neighbours clean / 1 / 0 | **124 / 40001 / 0 / 0** |
| **M6 linked-worktree `.git`→FIFO before its guard** | **0 / 7523 / only `a` — NO row for b / 1 / 0** | **0 / 363 / only `a` / 0 / 0** |
| M7 `objects/info/alternates` FIFO, census phase | 2 / 784 / 0 rows / 1 / 0 | 2 / 465 / 0 rows / 1 / 0 |
| M8 `objects/info/alternates` FIFO at b's rev-parse (after census guard) | 0 / 7952 / b error / 1 / 0 | **124 / 40001 / 0 / 0** |
| W worktree b, no swap | 0 / 659 / only `a` / 0 / 0 | 0 / 511 / only `a` / 0 / 0 |

Exact tip-M2 timeout row (`od -c`): `<repo>/b \t 0 \t 0 \t 0 \t 0 \t \t e r r o r \n`; stderr exactly `souji-census: repo-timeout 5s <repo>/b\n` (1 line).

## Findings

**F1 — C1's row promise fails for a list-phase guard timeout (tip M6).** A linked worktree `b` is classified `gitfile` at list time (`tools/souji-census.sh:1425-1428`) and is **never added to `REPOS`**; only `kind=repo` guard timeouts are recorded (`:1680`, `if [ "$kind" = repo ]; then preflight_timeout["$repo"]=1; fi`) and rows are emitted only from `REPOS`/`preflight_timeout` (`:1691-1696`). `gitfile_admin` (`:861-875`) reads `$repo/.git` with an **unconditional** `IFS= read -r line < "$file"` (no `-f` re-check), so the FIFO blocks the guard worker inside its own process group (timeline: guard worker pid 552164 pgid 552164, fd1 `.../guard.p5I52P`; child pid 552170 pgid 552164 blocked `wchan=wait_for_partner`; killed at 5 s). Observed: **exit 0, one stderr line `souji-census: repo-timeout 5s <b>`, and no row for `b`** (the stall itself is bounded at 7.5 s, so this is a row-contract defect, not a hang) — 1 data row (`a clean,wt-dirty`), where `a`'s `worktrees=2` proves the run knew `b` existed. This is the only FIFO-reachable guard-phase timeout: every other guarded read re-checks `-f` first (`commondir` `:922/:965/:1007`, `worktrees/*/gitdir` `:899-900`, `config` `:846`, `alternates` `:547`), and `guard_git_files` stat-refuses non-regular files (`:589-628`), so `preflight_timeout` never fires for `kind=repo` with a FIFO. Contradicts the tool's own doc sentence at `:157-160` ("Candidate metadata guards … a timed-out repository gets the row"). Fixture `tests/fixtures/r18-census-bounded.py` has **no** gitfile/linked/pointer case (`grep -n 'gitfile\|linked\|pointer'` → empty; B4's "worktree" is `.gitignore`/`.gitattributes` in a normal repo's work tree), so B1–B8 passing does not cover this.

**F2 — the guard does not classify `.git` itself (tip and base, bounded).** After `[ -L ]`, `[ -d ]`, `[ -f ]` branches (`:945-1027`; branches at `:950/:954/:985`), a `.git` that is a FIFO/device/socket falls through with `soft=0` → guard returns 0; `census_one`'s `[ -e ]` test (`:1312-1321`) then passes it to Git, whose own `fatal: not a regular file` (1 ms) produces the `error` row (M3 tip 773 ms, M4 tip 360 ms). No hang, but `guard_git_files`' stated policy ("a FIFO/device/socket is refused rather than opened or waited on", `:582-588`) is not applied to `.git`; the outcome depends on Git's behaviour, not the guard's.

**F3 — post-guard non-regular metadata still aborts the fleet, exit 2, zero rows (tip and base; pre-existing).** M1/M7: a FIFO on `.git/commondir` or `.git/objects/info/alternates`, planted after the candidate guard passed, is caught by `census_one`'s re-guard; `guard_git_files` calls `protected_fail "git-metadata-nonregular"` (`:622`), the worker returns 2, `emit_census` exits 2 (`:1705`) — stdout is **empty**, so `a`, already measured, is discarded. Same at b576341 (rc 2, 465 ms), so not a C1 regression; but it is the same event class where C1 promises "others measured", and the exit-code block (`:165-169`) lists 2 only for "usage, malformed baseline, protected-path refusal" while this is neither.

**F4 — C1's census_one half holds exactly.** M2/M5/M8 at tip: private per-repo pgid (M2 blocked `git` pid 4158377, pgid 4157703 = worker pid; M5 pgid 531857; M8 pid 1325708 `wchan=wait_for_partner`), exact placeholder row, exact one-line diagnostic, neighbours measured, exit 0, 7.8 s for a 5 s bound (5 s + 2 s TERM→KILL + reap). No survivors and no attributed `CENSUS_TMP` residue (tip-M2 `.../rJ3Lx2` and tip-M6 `.../hdv1JK` gone). Baseline: no per-repo group (blocked `git` pgid 534180 = outer `timeout` pid; M5 timeline shows it alive at `etimes=39`), then **rc 124 at 40 s with 0 rows and 0 stderr** (M2/M5/M8). That is the contrast C1 claims to fix.

**F5 — linked worktrees are never rows (both commits).** W arms: both emit only `a`, no diagnostic — pre-existing design. After F1 that design and the `repo-timeout` wording contradict each other: the diagnostic names a path that cannot have a row.

**F6 — unobserved.** `repo-timeout-unreaped` not exercised (needs a process surviving SIGKILL, e.g. D-state); no survivors in any arm. Not tested: FUSE/regular-file blocking reads, default timeout 600, the `--repo-timeout` CLI spelling (assignment specified the env var). Shared `/var/tmp` namespace means only `fd/1`-attributed tmp dirs are claimed.

## Verdict

**PARTIAL (C1 fails one clause).** Census-phase timeouts are bounded exactly as claimed (F4), and the baseline hang is real and severe. But the claim "a timeout → row `<repo>\t0\t0\t0\t0\t\terror`" is false for the only FIFO-reachable list-phase guard timeout (F1: stderr names `b`, no row, exit 0), and the "others measured" promise does not hold for a post-guard non-regular `commondir`/`alternates` (F3: exit 2, zero rows). F2 is a bounded guard-completeness gap.

## Smallest fix

One place (F1): at `tools/souji-census.sh:1680` drop the `kind = repo` filter — `preflight_timeout["$repo"]=1` for every timed-out candidate — and, just before printing rows, append `"$(sanitize_field "$repo")"$'\t0\t0\t0\t0\t\terror'` for each `preflight_timeout` key not in `REPOS`. That makes M6 emit `a clean` + `b error`, exit 0, and matches the claim/docs. Add a B9 to `r18-census-bounded.py`: linked-worktree `b`, FIFO its `.git` during `a`'s guard (sorted glob order makes it deterministic), assert exactly one `repo-timeout` line **and** the placeholder row, and assert base hangs (rc 124). If worktrees are intentionally not rows, instead rename that diagnostic to `candidate-timeout` and scope the claim to row repositories. For F2, add an explicit type check after the `[ -f "$g" ]` branch in `guard_git_surface`: `[ -e "$g" ] && [ ! -d "$g" ] && [ ! -f "$g" ]` → soft `git-metadata-nonregular` (error row), mirroring r17 D2. For F3, soften `git-metadata-nonregular` in the census-phase re-guard to `meta_soft` (error row) for paths outside protected roots, keeping exit 2 only for protected reaches (and fix the exit-code doc either way).

## Tooling / cleanup

No installs or upgrades (nothing needed). Both clones deleted after the runs; harness and logs left under `/var/tmp/souji-r18w2-ProbeListPhaseSwap/` (`out/`, `state/`, `shim/`, `*.sh`) for audit. No lane file was written except this report; `jj`/git writes only inside the clones.
