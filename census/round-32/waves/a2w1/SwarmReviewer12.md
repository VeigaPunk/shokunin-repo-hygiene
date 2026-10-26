# SwarmReviewer12 — C2 patch review (souji-census.sh, souji-repo-structure.sh, r13-repo-structure.sh, souji-round9-selftest.sh)

## Status

STATUS: PASS — the C2 diff on the four assigned files changes only the scratch root (TMPDIR-honouring); T11/T12 pass at 98e5203 in both TMPDIR modes with identical summaries to base; guards, refusals and write-scope policy are unchanged; cleanup is complete (strace: zero mkdir outside TMPDIR). Two low-severity edge regressions found (TMPDIR with a trailing slash) — they do not touch any frozen C2 predicate; reported for the L1.

Scope: diff `85b61a151923986e7e6b48f7084b9122561b5f3d..98e5203d45b4e419a9e72801733d93303acc7ebd` for tools/souji-census.sh, tools/souji-repo-structure.sh, tests/fixtures/r13-repo-structure.sh, tools/souji-round9-selftest.sh; behavioural runs in a scratch clone (origin removed, toplevel verified).

## Evidence

Diff census (git diff, 4 files): 25 insertions / 21 deletions; every hunk accounted:
- r13-repo-structure.sh: 2 comment hunks, `mktemp -d "${TMPDIR:-/var/tmp}/souji-r13-repo-structure.XXXXXX"` (was literal `/var/tmp/...`), die2 text `/var/tmp`→`TMPDIR`, `ENV_ALLOW` += `"TMPDIR=${TMPDIR:-/var/tmp}"`.
- souji-census.sh: 2 comment hunks + 8 code sites, all scratch-root tokens: `mktemp -d "${TMPDIR:-/tmp}/souji-census-now.XXXXXX"` (:309, :1879), `ST_TMP` (:2009), `st_worker_tmpdir` case pattern (:1990), TERM/KILL cleanup cases (:2906, :2970), two `prot_err` child envs `TMPDIR="${TMPDIR:-/tmp}"` (:2282, :2293).
- souji-repo-structure.sh: 2 comment hunks + `mktemp -d "${TMPDIR:-/var/tmp}/souji-repo-structure.XXXXXX"` (:266). EXIT trap `cleanup_probe_tmp` at :167 unchanged.
- souji-round9-selftest.sh: `R9_TMP=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX")` (:7, was `mktemp -d -p /var/tmp`), `export TMPDIR="${TMPDIR:-/var/tmp}"` (:14, was literal `/var/tmp`).

Runs (clone `/fast/scratch/hyaku/souji-r32/ReviewC2Census/tmp/clone.ewGoRk/c`, `git rev-parse --show-toplevel` = that path; `bash tools/souji-census.sh --selftest` = c2 item T12; `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` = T11; normal = TMPDIR set to scratch tmp):

| run | rev | TMPDIR | rc | last line |
|---|---|---|---|---|
| T12 base normal | 85b61a15 | set | 0 | `selftest: 69 checks, 0 failed` |
| T12 base unset | 85b61a15 | unset | 0 | `selftest: 69 checks, 0 failed` (fixtures under /var/tmp) |
| T12 C2 normal | 98e5203d | set | 0 | `selftest: 69 checks, 0 failed` (fixtures under `$TMPDIR`) |
| T12 C2 unset | 98e5203d | unset | 0 | `selftest: 69 checks, 0 failed` (fixtures under /tmp) |
| T11 base normal/unset | 85b61a15 | both | 0 | `selftest=PASS ids=7/7` |
| T11 C2 normal/unset | 98e5203d | both | 0 | `selftest=PASS ids=7/7` |
| T11 C2 trailing-slash | 98e5203d | `.../runslash/` | 0 | `selftest=PASS ids=7/7` |

Write-scope attribution: `strace -f -e trace=mkdir,mkdirat` over T12 at C2 (TMPDIR=/fast/...): 0 mkdir attempts under /var/tmp, 328 under /fast — the patched census creates nothing outside the caller's TMPDIR. `/var/tmp/souji-*` deltas seen during runs were other seats' concurrent processes (`souji-proc-control.*`, `souji-proc-out.*`, `souji-r23-receipt-*` — names my four files never create; gone minutes later). Round-9 helper (`bash tools/souji-round9-selftest.sh verify tools/souji-verify.sh`): C2 normal rc=0 `ROUND9 16 0`; C2 unset rc=0 `ROUND9 16 0`; base trailing-slash rc=0 `ROUND9 16 0`; C2 trailing-slash rc=1 `ROUND9 14 2` (see Finding 2).

Tooling: no tools installed or updated this seat (pacman guard respected; nothing to record).

## Findings

1. LOW — trailing-slash TMPDIR regresses the census selftest (false failures, no leak). tools/souji-census.sh:1990 `case "$path" in` matches the worker fd path against `"${TMPDIR:-/tmp}"/souji-census-now.*/*`; the kernel path from `/proc/<pid>/fd/1` is canonicalized (single slash) while the pattern keeps the caller's trailing slash as `//`, so the match misses → `term_tmp_dir`/`kill_tmp_dir` empty → 10 checks fail: `FAIL parent SIGTERM cleanup ... tmp=`, `FAIL parent SIGKILL cleanup ... tmp=` plus 8 downstream (watchdog row/FIFO/worker-kill/odd-name) — `selftest: 69 checks, 10 failed`, rc=1, rev 98e5203d, TMPDIR=`/fast/scratch/hyaku/souji-r32/ReviewC2Census/tmp/runslash/`. Base under the same env: 69/0, rc=0 (base pattern is the literal `/var/tmp/souji-census-now.*/*`). The killed runs' tmp dirs are still reaped by the detached timer (no leftover found under TMPDIR, /tmp, /var/tmp), so the damage is a false-failing selftest, not a leak. Fix shape: normalize once (e.g. `TMPDIR=${TMPDIR%/}`) before building mktemp templates and patterns. Same `//` asymmetry applies to the :2906/:2970 case guards.
2. LOW — trailing-slash TMPDIR regresses the round-9 helper. tools/souji-round9-selftest.sh:7 `R9_TMP=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX")` propagates the raw TMPDIR (with trailing slash) into `R9_GATE_DIR`; the sha256sum-shim gate fires on exact string equality `[ "$PWD" = "$R9_GATE_DIR" ]` (:200), but bash collapses `//` in PWD, so equality fails and the ledger-revocation branch is never reached: `FAIL R9 file ledger revocation was reached` + `FAIL R9 directory ledger revocation was reached`, `ROUND9 14 2`, rc=1 at 98e5203d; base rc=0 `ROUND9 16 0` in the same env; C2 without trailing slash rc=0 `ROUND9 16 0`. Observed verdict diverged to `NOT-SAFE ... stale=not-scratch-type` (tools/souji-verify.sh:348 `kind=$(scratch_type "$target")`).
3. INFO — with TMPDIR unset the census scratch root moved /var/tmp → /tmp (souji-census.sh:309 `${TMPDIR:-/tmp}`), and the census child envs (:2282, :2293) now inherit the caller's TMPDIR instead of forced `/var/tmp`; both are the intended C2 direction and verified by the unset run (rc=0, 69/0, fixtures under /tmp). The other three files keep the `/var/tmp` fallback when unset — fallback roots are now inconsistent across files (census `/tmp`, others `/var/tmp`); behaviour-identical to base when unset for those three.
4. INFO — no guard widened. r13 `ENV_ALLOW` is an `env -i` allowlist for the measured invocation ("Allowlist for the measured invocation: no inherited Git_* can leak in", r13-repo-structure.sh:220-221 area); the added entry is one deterministic assignment, no arbitrary env admitted, Git_* exclusion intact. All census refusal/protected-root logic is byte-identical except the TMPDIR token. No path check that used to match only `/var/tmp/<prefix>.*` now accepts arbitrary paths — every new pattern is anchored at the same-variable root the code itself creates its dirs under.
5. INFO — error-path output text changed in r13-repo-structure.sh:190 (`die2 "mktemp failed under TMPDIR"`, was `"mktemp failed under /var/tmp"`); only reachable when mktemp itself fails. Disclosed for landing-text discipline (prereg defect 4).
6. RESIDUAL — census :1990/:2906/:2970 expand TMPDIR inside `case` patterns, so glob metacharacters in TMPDIR are pattern-interpreted; the `rm -rf` targets remain the real worker fd path (never the pattern), so worst case is a skipped fallback rm of an already-reaped dir, not deletion of an unintended path.
7. RESIDUAL — timing headroom: strace-instrumented T12 at C2 on /fast failed 2 wall-time-budgeted checks (`FAIL watchdog wall time 8127ms (want < 6000ms)`). Separator runs pin the cause: C2+strace with TMPDIR=/var/tmp → 69/0 rc=0; C2+strace on /fast → the 2 failures; C2 untraced on /fast → 69/0. So neither strace alone nor the patch breaks anything — the fixed 6000 ms budget only breaks under strace overhead on the /fast scratch filesystem. Honouring a caller TMPDIR on slower storage narrows the selftest's fixed wall-time budgets — inherent to the C2 goal, worth one line in the L1's after-record.

## Attack log

Attacks attempted against the landed C2 patch (all reproduced, rev 98e5203d):
- A1 guard-widening sweep: enumerated every `mktemp`/`TMPDIR`/tmp-literal site in the four files at C2 (`git grep -nE '/var/tmp|/tmp/'` minus comments; `git grep -nE 'mktemp|TMPDIR'` for census) — no site accepts a broader path family than base; the only variable-rooted patterns match exactly the dirs the same code creates. RESULT: no finding.
- A2 cleanup sweep: before/after snapshots of `$TMPDIR`, runslash, /tmp, /var/tmp across all 11 runs + strace mkdir attribution — nothing created by the four files survives any run (base or C2, any mode). RESULT: no finding (concurrent-seat /var/tmp noise excluded by name family + strace).
- A3 hostile TMPDIR values: trailing slash (Finding 1, Finding 2 — reproduced twice each: census 69/10-fail, round9 14/2); unset (passes everywhere at C2). Glob-metachar TMPDIR not executed, reasoning in Finding 6 is static [INFERENCE from case-pattern semantics]. RESULT: 2 low findings.

## Deliveries

- .ufo/waves/round-32/a2w1/SwarmReviewer12.md (this report; only file written in the lane)

Scratch `/fast/scratch/hyaku/souji-r32/ReviewC2Census` removed after this report was written. Raw run logs referenced above lived there (rc/last-line excerpts pasted inline). No lane file outside the report path was created, modified or deleted; no lane git/jj mutation; no tools installed.
