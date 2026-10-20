STATUS: DONE — C1 no-harm holds on all recorded suites and both live pairs; two narrow new-harm counterexamples (false-timeout race, external-TERM orphan leak), one stale "6 s" figure.

# CriticC1NoHarm — C1 no-harm vs b576341

Axes named: **operability** (any previously-working repo class degraded; new hangs, orphans, or failure modes a consumer sees), **calibration** (rows/stderr/exit codes a consumer could read differently), **coverage** (is the bounded region actually complete). Seat: CriticC1NoHarm. Read-only seat: no lane execution, no live census, no writes except this report.

Evidence: `census/round-18/c1-matrix-worktree.json`, `census/round-18/live-fleet-pairs/*.tsv`, `tools/souji-census.sh` at `b576341` vs `5efb519` (git show/diff), `corpus/lessons/round-18.md:6`, `.ufo/waves/round-18/w1/CriticC1Scope.md`, `w1/CriticC1Harm.md`.

---

## 1. Any arm/suite where changed is worse — NONE

Recorded (`c1-matrix-worktree.json`), changed arm vs the b576341-class arms (r17-base = b576341; pre-harm = a31642d; r14-harm = cc21683):

| suite | changed | r17-base | pre-harm | r14-harm |
|---|---|---|---|---|
| r14-namespace | 12/0 | 12/0 | 10 FAIL | 12/0 |
| r15-config | 20/0 | 20/0 | 8 FAIL | 16 FAIL |
| r17-hygiene | 29/0 | 29/0 | 21 FAIL | 14 FAIL |
| r18-bounded | 8/0 | 5 FAIL | 6 FAIL | 5 FAIL |
| selftest | 62/0 | 49/0 | 36/0 | 38/0 |

Every changed-arm suite is equal-or-better than every arm; no FAIL→worse anywhere. `leftover_procs` lists are byte-identical across all four arms (44 / 14 PIDs — pre-existing residue from fixture runs, not attributable to the diff). `stderr_tail` empty everywhere; `bash_n`/`shellcheck` rc 0 both arms. Claimed numbers (r18-bounded 8/5-fail → 8/0, r17 29/0, r15 20/0, r14 12/0 both arms, selftest 49→62) all match the record verbatim.

**Evidence caveat (not a harm):** `fixtures_dirty` records the matrix ran a *patched* r14 fixture (`fixtures_sha256.r14-namespace` `6c1c0cfd…` ≠ tip bytes `e6a984b1…` = b576341 bytes). The claimed 12/0-for-landed-fixture is a valid inference only because tip == b576341 and r17-base ran the same patched fixture to 12/0. Verified:

```
$ git show b576341:tests/fixtures/r14-census-boundary.py | sha256sum = git show 5efb519:… = e6a984b1daf1f79a…
$ git diff b576341 5efb519 -- tests/fixtures/r14-census-boundary.py → empty
```

## 2. Row-shape / stderr changes a consumer could see

- **Stdout shape unchanged**: same header, same 7 columns, same flag vocabulary (`error` was already emitted by guard-soft/rev-parse-failed rows at census_one `:1308/:1321` tip). Timed-out rows are `<repo>\t0\t0\t0\t0\t\terror` — indistinguishable in the TSV from a degraded row (w1 CriticC1Harm §GAP-2 conflation; disclosed in lesson :26 "a bound converts a hang into a 'not measured' error row"). A `--compare` run sees error↔measured flaps where base either hung forever or measured; priced and documented.
- **Stderr: two additive line forms** — `souji-census: repo-timeout <N>s <repo>` (`:1678`,`:1707`) and `souji-census: repo-timeout-unreaped <repo>` (`:1641`). Both exist only where base produced *no output at all* (it hung). A consumer pattern-matching `^souji-census: (census failed|.*protected)` sees no ambiguity; `unreaped` omits the `<N>s` field, matching the header comment :163.
- **Ordering**: base interleaved guarded-read stderr with measurement in sorted repo order; changed emits per-repo staged stderr during the preflight pass in *glob order* (`GUARD_CANDIDATES`, `:1665-1690`), then sorted measurement stderr. Cosmetic; no suite counts ordering.
- **Guard-work is NOT doubled** (refutes the naive reading): base `list_repos` already ran `guard_git_surface`/`guard_git_pointer` inline (b576341 `:1352`,`:1381`,`:1385`) *and* `census_one` re-ran `guard_git_surface` (`:1264`) — two guarded passes at base, two bounded passes now. What changed: both passes moved into watchdog children (`emit_census` `:1665` preflight + `:1698` census), and `protected_reason_input` moved out of the parent into the bounded `guard_repo_candidate` (`:1441-1442`). Refusal semantics preserved: worker exit 2 → `if [ "$rc" = 2 ]; then exit 2` (`:1676`,`:1705`), stdout still empty, verified by B7 PASS and r15/r17 refuse-class PASS.
- **New exit-1 surface**: a non-timeout non-2 failure inside a *preflight* guard worker now prints `census failed for %s (rc=%s)` + exit 1 (`:1682-1683`); at base the same failure class exited 1 from the row loop only. Same diagnostic, earlier phase — additive, not a regression.

## 3. Pair-2 mado difference — explained, verified live-lane writes

```
pair2-base-b576341.tsv:16   mado-shokunin … 10 … 2026-10-20T17:29:30-03:00 dirty,secret-shaped
pair2-changed-worktree.tsv:16 mado-shokunin … 13 … 2026-10-20T17:29:56-03:00 dirty,secret-shaped
```

Pair 1 is identical excluding `tameshi` mtime (+12 s); pair 2 otherwise differs only in `mado` dirty 10→13 and `mori`/`tabi`/`tameshi` mtimes. Lesson :6: "pair 2 differs only in mado-shokunin dirty 10 → 13, a lane writing during the run." Consistent and independently supported: `git -C /home/vgpnk/Projects/shokunin/mado-shokunin ls-files -m -o --exclude-standard` (read-only, allowed) currently lists active `.ufo/waves/round-20/w2/*` artifacts — mado is a live working lane; untracked churn between two sequential census runs fully explains +3 `git status --porcelain` entries. The changed tool counts dirty via the same `git status --porcelain` (`count_dirty`, tip `:1147-1176`, unchanged from base), so identical-state → identical-count (pair-1 proves it). **No tool-side counterexample possible from this evidence.**

## 4. The 11 s vs 6 s live runtime — figure is half-stale, mechanism explained

- The pair TSVs record **no wall times**; "6 s" (base) appears nowhere in the records or wave-1 reports I could find — only `corpus/lessons/round-18.md:26` "the whole live fleet takes about 11 s" (changed arm). The 6 s base figure is [INFERENCE] from the task framing; unverifiable from recorded evidence, and stale by ~2× if it's meant as a measured pair.
- The +Δ is explained without hand-waving: per repository the changed tool now spawns a `set -m` worker subshell plus a `setsid bash` watchdog (`:1478-1501`), polls `/proc/<pid>/stat` at 0.1 s quanta, and stages two temp files — ~0.15–0.25 s per bounded region × ~42 regions (21 repos × preflight+census) ≈ 4–6 s over ~21 repos. Guarded-read count is unchanged (§2). This is bounded, documented cost of the feature, not a regression class.
- Operability consequence the lesson already prices (CriticC1Scope disclosure 2): worst case is Σ bounds = 21 × ~605 s ≈ 3.5 h if every repo hangs — a bound, not a hang. No suite or live run approaches it.

## 5. Residual counterexamples (small, real)

**N1 — false-timeout boundary race (operability, ~0.1–0.2 s window per repo per run).**
Watchdog loop (`:1483-1498`): `elapsed` reaches `limit` → `kill -0 -pgid` → `mkdir $state_path` (wins the arbiter) → `timed_out` → TERM. If the worker exits *naturally* within the final ~1 s before the limit and is still an unreaped zombie when the watchdog's final `kill -0 -pgid` runs, the pgid exists, `mkdir` wins against the parent (parent sleeps 0.1 s per poll, `:1523`), and a clean measured repo is reported `error` + `repo-timeout` while its complete row sits in `row_file`. Worker `wait` then returns 0 (`:1519-1521`, `dead=1` path) but `REPO_TIMED_OUT=1` already won (`:1539`), so `emit_census` emits the error row and exit stays 0 — a *measured* repo recorded as unmeasurable. Probability: the worker must die inside a ~0.2 s window out of 600 s ≈ 0.03 %/repo/run — rare but nonzero, and silently wrong rather than loud.
*Smallest fix:* in the parent, when `wait` already collected rc=0 *and* `row_file` parses as exactly one well-formed row, prefer the row over `timed_out`; or have the watchdog re-check `kill -0 -pgid` *after* `mkdir` succeeds and bail without `timed_out` when the group is gone (shrinks but doesn't fully close the window; the row-preference check closes it completely).

**N2 — external-TERM orphan pair (operability residue; w1 CriticC1Harm H-pipe, still unfixed).**
Base: the census's in-flight `census_one` shared the script's process group — `kill <census-pid-group>` (or a harness `killpg`, or `timeout`'s TERM) killed the measurement child too. Changed: worker is its own pgrp (`set -m`, `:1478-1481`) and the watchdog its own session (`setsid`, `:1482`), and **no TERM/INT trap exists** in the tool (`grep -n 'trap' → only EXIT cleanup`). Killing the script mid-repo now orphans the worker+watchdog pair for up to `REPO_TIMEOUT`+2 s (bounded, self-cleaning — the watchdog still fires — vs unbounded hang at base). Net improvement in liveness, net regression in prompt-kill hygiene: a SIGTERM'd run leaves a `git status`/`find`/`du` process working a repo for up to 10 min after its parent died, inside a removed `CENSUS_TMP` (rm -rf under a live writer).
*Smallest fix:* `trap 'kill -TERM -- "-$worker" "-$watchdog" 2>/dev/null; …' TERM INT` armed inside `run_repo_with_watchdog` (or an EXIT-time sweep of recorded pgids) — restores base kill semantics; the watchdog already bounds the orphaned worst case, so this is hygiene, not liveness.

**N3 — timeout masks a racing protected refusal (calibration, narrow).**
If a worker writes `path-protected:` to `stderr_file` and hangs before `exit 2` (e.g., blocked in a subsequent open inside the same guarded pass), the timeout path (`:1539` → REPO_TIMED_OUT → row `error`, rc 0) wins: the run exits **0** with a `path-protected:` line on stderr — a shape the r17 refusal oracle (exit 2 + finding + empty stdout) forbids. w1 CriticC1Harm GAP-2(b) named exactly this precedence and recommended scanning staged stderr for `path-protected:` before emitting the timeout verdict; the landed code does not scan.
*Smallest fix:* after `cat "$stderr_file"`, on the timeout path `grep -q 'souji-census: path-protected' "$stderr_file"` (re-read or check before cat) → `exit 2` instead of error row. One-line precedence, no new state.

**N4 — preflight timeout suppresses a retryable repo (design note, likely fine).**
`preflight_timeout["$repo"]=1` (`:1680`) marks a repo from its *guard* pass timing out and skips `census_one` entirely. Correct (the same guarded surface re-runs inside `census_one` and would re-block), but note a `kind=path`/`gitfile`/`symlink` candidate timeout still emits a `repo-timeout <N>s <path>` stderr line for a path that produces **no row** — a consumer counting `repo-timeout` lines vs `error` rows sees a mismatch. Documented behavior per header :161; flag for record.

## 6. Checked and clean

- `validate_repo_timeout` runs before any repo work/temp (`:2603`), covers env+flag, range 1..86400, strips leading zeros — B6/B7 and selftest invalid-timeout arms pass; invalid env exits 2 pre-work as required (w1 H-usage fixed).
- `set -m` is scoped to the worker fork (`:1478-1481`), `set +m` immediately after — no monitor-mode leak, no stray job notices (selftest asserts "no job-control warning").
- Rows buffered → printed after the loop, same as base; `row=$(<"$row_file")` discards torn partial rows on timeout (H-partial fixed); stderr staged per repo and `cat`'d at region end (H-stderr fixed).
- `emit_compare` tmp-file → tmp-dir conversion (`:1821-1826`) consistent with `prepare_census_tmp`; `load_census` reads `now.tsv` correctly.
- `command -v setsid` hard-checked at startup (`:2618`) — missing-setsid fails fast exit 1, not silent feature loss.
- Watchdog `kill -0 -pgid`-before-every-action ordering means a dead group is never signalled (no recycled-pgid kill within the run's own flow; the orphan case of N2 is bounded by the watchdog itself).
- `leftover_procs` identical across all arms — no new residue attributable to the diff.
- r14-namespace 12/0 both arms: the revert to b576341 fixture bytes (`e6a984b1…` == tip) holds; `souji-preservation-evidence.py` digest pin unaffected (fixture is byte-identical to the pinned baseline).

## Verdict

**Holds, with reservations.** Every recorded no-harm comparison is equal-or-better (§1), the row/stderr contract changes are additive on paths where base emitted nothing (§2), the pair-2 mado delta is live-lane writes (§3, verified), and the ~2× live runtime is mechanism overhead, not doubled work (§4). The three residual counterexamples (N1 false-timeout race, N2 TERM-orphan leak, N3 timeout-masks-refusal precedence) are each narrow, fixable, and none invalidate the claimed numbers — N1/N3 are race-shaped correctness nits the canonical judge may price as acceptable residuals; N2 is the strongest because it is deterministic given a mid-run external TERM, but it trades an *unbounded* hang-residue for a *bounded* orphan, which is still a strict operability improvement on the axis judged.

## Commands run (all read-only; no tool installs, no lane/fleet mutation)

```
git -C souji-shokunin diff b576341 5efb519 -- tools/souji-census.sh
git -C souji-shokunin show {b576341,5efb519}:tools/souji-census.sh (+ sed/grep ranges)
git -C souji-shokunin show {b576341,5efb519}:tests/fixtures/r14-census-boundary.py | sha256sum
git -C souji-shokunin diff b576341 5efb519 -- tests/fixtures/r14-census-boundary.py  → empty
read census/round-18/c1-matrix-worktree.json (all 4 arms), live-fleet-pairs/*.tsv (4 files)
grep lane.id|ufo mado-shokunin/.git/config → no lane.id; git -C mado-shokunin ls-files -m -o --exclude-standard → 7 active round-20 artifacts
grep -rn 'live-fleet|wall|6 s|11 s|runtime' .ufo/waves/round-18/w{1,2}*/ corpus/lessons/round-18.md → 11 s only (lesson :26); no recorded 6 s
read .ufo/waves/round-18/w1/{CriticC1Scope,CriticC1Harm}.md — w1 defect cross-check vs landed code
```
