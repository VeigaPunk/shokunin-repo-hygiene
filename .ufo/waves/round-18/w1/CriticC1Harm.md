# CriticC1Harm — no-harm attack on the C1 per-repo watchdog

STATUS: DONE — 13 harm classes checked against `tools/souji-census.sh@b576341` and the four suite
oracles; 2 contract-level gaps, 1 tradeoff the judge must price, the rest fixable inside the contract.

Axes named: **operability** (does the watchdog turn any previously-working repository class into
`error`, a leak, or a new hang), **calibration** (does it ever emit the wrong finding class —
timeout-vs-failed-vs-protected), **coverage** (does the bounded surface actually cover every
repo-controlled blocking open). Every finding cites `tools/souji-census.sh:LINE` at b576341
(`006b9823…`, 2072 lines) unless marked [INFERENCE]. Cross-checked against peer measurements:
`ScoutSetM.md` (bash 5.3.20 semantics, measured), `ScoutWorktreeFifo.md` (static FIFO arms, measured),
`RevC1ExitSemantics.md` (contract review). I ran only read/grep/bash-n-class probes; no tool installs.

---

## GAP 1 (contract-level, operability + coverage) — the scan-phase guards re-open the same blocking-open class, *outside* the watchdog

The watchdog bounds `census_one` (`:1261`) only. But `list_repos` (`:1343-1392`) runs the **full
guard surface in the parent, unwatched**, before any child exists:

- `:1380-1382` `guard_git_pointer` → `gitfile_admin` `IFS= read -r line < "$file"` (`:820`) — reads the
  `.git` file.
- `:1384-1386` `guard_git_surface` → worktree registrations `read < "$entry/gitdir"` (`:857`),
  `gitfile_admin` again (`:869`), `commondir` reads (`:880`, `:923`, `:965`), alternates
  `read < "$alt"` (`:515`), and `guard_git_config` opens `$cfg` twice — `tr -d '\000' < "$cfg" | cmp -s`
  (`:695`) plus `git config --file "$cfg" --list` (`:701`), a **git child in the parent**.

Every site is gated by `[ -f ]`, so a pre-placed FIFO is skipped — but the exact L1 mechanism (regular
file at stat/test time, swapped to FIFO before the open) hangs the **parent** in `open(2)`, before the
per-repo watchdog can exist. `ScoutSetM.md` asserts "`list_repos` runs no git … its guards only stat"
(`:353-360`) — that is wrong for `:695`,`:701`,`:820`,`:857`,`:880`,`:923`,`:965` (and the `.git`
file read at `:943`). The claim "no single repository can hang the fleet census" is false for this
window even after the fix lands: the same TOCTOU, one open earlier.

**Strongest counterexample:** PATH-shim the swap at `.git/commondir` or `objects/info/alternates`
(regular at `guard_git_files` `:548` enumeration, FIFO at `:923`/`:515` read) — the census blocks in
the parent with zero children, watchdog irrelevant, identical symptom to the L1 repro (outer
`timeout 15` → rc 124, zero rows).

**Exposing test:** the same PATH-`git`-shim harness L1 used, retargeted at a parent-side open —
expect bound+`error` row; fails today (unbounded parent hang). Coverage: r17-29 (0 — all bad-metadata
arms pre-position, and D2 soft arms are child-side only), r15-20 (0), r14-12 (0), selftest-49 (0).

**Smallest safe correction:** stop guarding twice. The parent pass in `list_repos` exists only to
populate `REPOS` and pre-refuse; `census_one` re-runs `guard_git_surface` (`:1264`) inside the child
anyway. Reduce `list_repos` to the `-L`/`-f`/`-d` classification (all stat-only, cannot block) and let
the watched child perform every opening guard; the child's `exit 2` already propagates to whole-run
`exit 2` with empty stdout, so refusal semantics are unchanged *and* guard work halves. This is a
contract amendment, not a rejection — the row/stderr shapes survive.

## GAP 2 (contract-level, calibration) — the timeout row must win/lose in a specified order; `error` conflation launders causes into the TSV

Two orderings the contract does not pin and the suites cannot see:

**(a) Sentinel-vs-status precedence.** `wait` returns `143`/`137` for the watchdog's own signals *and*
for an OOM-killed `git` — r15's harness literally exports `RLIMIT_AS=1073741824`
(`r15-census-config.py:287`), so a `/dev/zero`-class attr arm can legitimately die `137` with no
timeout. If the parent infers timeout from `rc∈{143,137}` it prints `repo-timeout` (a lie) instead of
`census failed … (rc=137)` + exit 1. Peers fixed the shape: watchdog writes a sentinel file *before*
its first signal; classify `rc=0` → sentinel → `rc=2` → other (ScoutSetM `:256-272`, measured T4/T5).
**Exposing test:** tiny `RLIMIT_AS` arm → expect exit 1, `census failed`, *no* `repo-timeout`. Coverage:
none in any suite (r15 sets the rlimit but asserts no rc-mapping for it).

**(b) Protected refusal racing the watchdog.** A child in `protected_fail` (`:223-229`, exits 2 after
writing `path-protected:` to stderr) that is killed mid-write yields `wait`→143 + sentinel. If timeout
wins, the run emits a `path-protected` line **and** exits 0 with an `error` row — a classification the
r17 refusal oracle (`refusal_problems`, `r17-census-hygiene.py:424-435`: exit 2, finding, empty stdout)
explicitly forbids. Fixable: stage the child's stderr per repo (needed anyway, see H-stderr below) and
scan it for `path-protected:` before emitting the timeout verdict; a finding line forces exit 2.
Narrow race, cheap insurance. Coverage: none.

**Conflation note (calibration, judge-priced):** the contract pins the timeout row to
`<repo>\t0\t0\t0\t0\t\terror` — byte-identical to the guard-degraded (`:1266`) and `rev-parse`-failed
(`:1281`) error rows. TSV consumers (`load_census`/`emit_compare`, `:1425+`) cannot distinguish
"repo was unmeasurable for Ns" from "repo is permanently degraded"; `mtime_iso` empty in both. A
`--compare` run where a repo flips error↔timeout reports `0` change. The contract is pinned, so this
stays — but the lesson should record that `verdict_flags` is now a lossy channel and stderr is the
only disambiguator.

## TRADEOFF (operability, judge must price) — slow-but-finite repos become `error`

Any bound converts every repository whose census legitimately exceeds it into an `error` row; at base
they were measured (possibly slowly). The default 600 s makes this rare but real: huge dirty worktrees
(`count_dirty`/`newest_mtime` walk, `:1093`,`:1218`), `du` on giant `.scratch` (`scratch_bytes`), FUSE/
NFS stat storms. In `--compare` mode one such repo flips `after` to `error` → `emit_compare` reports
`changed` + exit 3 where base reported identical (`:1554-1561`). This is inherent to any bound — the
contract already chose it — but two obligations follow: (1) `usage()` prints the header comment block
(`:204-207`), so the flag *and its unconditional default* must be documented there or callers learn of
the bound only when a row degrades; (2) the claim phrasing "no single repository can hang the fleet
census" is only true **at the caller's own horizon if the caller sets `--repo-timeout` below it** —
L1's `timeout 15` repro still yields rc 124 at the default. **Exposing test:** PATH `git` shim
`sleep 2 && exec real git`, `--repo-timeout 1` → error row + one `repo-timeout 1s` line + neighbours
measured; `--repo-timeout 5` → clean rows. Coverage: zero (no suite has a timing dimension).

## FIXABLE harms (inside the contract; each with its exposing test)

**H-pipe.** An orphaned *census child* (external TERM/KILL of the script mid-repo) keeps the caller's
stderr pipe → `subprocess.communicate()` blocks past tool death until the child dies; bounded by the
watchdog only if it survives (it is its own pgrp, so it does — bounded at N+2 s, not zero). Worse:
with `set -m`, an external TERM to the script's group no longer reaches the in-flight repo child at
all — base children shared the group and died with `timeout`/killpg. Measured basis: ScoutSetM P2.3 —
"killing the bash parent alone does not free the git child" (`:106-109`), and P4 — an unredirected
watchdog holds the stdout pipe for its whole life (30 s measured, `:190-208`). Fix: parent
TERM/INT trap that `kill -KILL` the current repo pgrp + watchdog pgrp, watchdog subshell fully
redirected (`>/dev/null 2>&1`) — contract already requires "holds no stdout/stderr pipe of the
caller"; extend the same rule to the worker's inherited stderr being staged, not just stdout, so
nothing child-owned pins the caller's pipes after the parent dies. **Test:** send SIGTERM to the
script pid mid-blocked-repo; assert `communicate()` returns promptly, process tree empty, temps gone.
Coverage: none (fixtures only ever kill the whole session).

**H-partial.** SIGKILL mid-`printf` leaves a torn private row file; reading it back emits a
<7-field row → r17 `row has N columns want 7` (`:405-407`) if it ever surfaced. Fix: on timeout (or
any nonzero), discard the file wholesale and synthesize the error row — and *conversely* prefer a
complete 7-field row over a raced kill when the worker finished during TERM delivery (peer ordering
rule). **Test:** shim that writes a half-row then blocks; assert exactly the synthesized error row, no
fragment. Coverage: none.

**H-stderr.** If the child's stderr is inherited live, a SIGKILL mid-write can tear a
`souji-census: …` line — `degrade_diag_problems` counts `git-metadata-unsupported` *lines*
(`:465-468`), and a torn-but-prefix-matching line double-counts or a missing newline merges two
findings. Today's soft-diag rows return before git (`:1265-1268`), so the only realistic torn line is
a `path-protected`/`census failed` — low probability, but GAP 2(b)'s fix requires staged stderr anyway;
replay in repo order keeps diagnostics deterministic (today's order is sorted-repo order).
Coverage: none asserts stderr ordering; counts only.

**H-setm-leak.** `set -m` left on past the fork gives every later `&`/pipeline element its own pgrp —
silently widening the set of processes an external TERM misses (same failure as H-pipe, generalized),
and `wait` without args would then reap stray jobs. Contract says scope `set -m` to the fork; the harm
is *not verifying* it. Cheapest assert: selftest line `set -o | grep -q 'monitor.*off'` after the
loop, or a self-check that `$(jobs)` is empty post-loop. Coverage: none asserts monitor-mode
restoration; r14/r15/r17 never inspect shell options.

**H-fixture-reap.** The fixture contract's `os.killpg(proc.pid, SIGKILL)` signals the *leader's* pgrp
only; `set -m` workers/watchdogs are in different pgids and survive it — a red arm then leaves blocked
procs for up to bound+2 s, not forever. "0 blocked processes" holds only because the watchdog still
fires; if the fixture asserts zero residue *immediately* after killpg it flakes. Correction inside the
stated contract: after killpg, allow bound+grace drain, or sweep the session (`/proc` `session id`)
rather than one pgrp. (RevFixtureSessions covers the sibling side; I confirm the pgrp arithmetic.)
Coverage: this *is* the new fixture's problem — r17's `unblock_fifos`+killpg pattern (`:310-334`) has
the same blind spot today only because base children share the group.

**H-Dstate.** [INFERENCE] A repo child unkillable in D-state (stale NFS/FUSE) never exits; the
parent's `wait` blocks forever — the bound fails open inside the watched loop and the claim quietly
degrades to "no *killable* repository can hang the fleet". Not stageable portably; recommend either a
bounded `wait` (poll `kill -0`, abandon the husk, emit `error`, move on — leaves one leak, fleet
survives) or an explicit claim exception. Coverage: none, unstaged.

**H-usage.** `--repo-timeout`/`SOUJI_CENSUS_REPO_TIMEOUT` validation: `usage_err` exits 2 (`:209`),
colliding with the protected-refusal exit-2 class — callers that treat rc 2 as "protected" (r15's
`R15CFG-17`/`19` oracles do) will misread an operator typo as a refusal. Contract-pinned, acceptable;
but invalid-*env* must exit 2 *before any repo work or temp creation* (peer point 5), else a poisoned
operator env turns a healthy fleet run into rc 2 with half the work done. Coverage: no suite feeds the
env; add 0/86401/abc/`-1` matrix arms.

**H-temp.** Per-repo temp files need the run's `EXIT` trap, not `cleanup_census_tmp` (`:211-215`,
compare-mode only). One `mktemp -d` for the whole run (peer point 4, measured safe vs the child
inheriting-but-not-running the trap, ScoutSetM P3/T11). Assert no `souji-census*` residue in `/var/tmp`
after each of rc 0/1/2 and external-TERM runs. Coverage: none asserts /var/tmp cleanliness.

**H-selftest.** Selftest's inner `env … "$SELF" --root` (`:1699-1702`) inherits the watchdog; its
repos are fast so default 600 never fires, and `cmp -s` byte-identity (`:1704`) is unaffected — *but*
any future `Killed`/`Terminated` job notice on the inner run's stderr does not break `cmp` (stdout
only). Verified noise-free by ScoutSetM P1 when `wait` reaps inside the same iteration (`:101-105`);
the only leaking notice is async-reap, which the design avoids. No test needed beyond H-setm-leak.

**H-include-root.** `--include-root` path (`:1347-1357`) pushes `$root` itself into `REPOS`; the
watchdog wraps it identically — no special case needed, but `guard_git_pointer`'s parent-side read for
a `.git`-file root (`:1351-1352`) is GAP 1 again. Same fix.

**H-sanitize.** `list_repos` already drops `\n\t\r` basenames (`:1366-1368`), so the timeout row's
repo field cannot inject TSV — but the `repo-timeout <repo>` *stderr* line should still run
`sanitize_field` (`:988-994`) for defense-in-depth and because the `<repo>` printed there should be
the same form the row carries. Trivial; peers flagged the row side only.

## Coverage summary

| harm | r17-29 | r15-20 | r14-12 | selftest-49 |
|---|---|---|---|---|
| GAP 1 parent-side opens | — | — | — | — |
| GAP 2a rc-137 ambiguity | — | partial (rlimit set, no assert) | — | — |
| GAP 2b refusal race | — | — | — | — |
| slow-finite→error | — | — | — | — |
| H-pipe / external TERM | — | — | — | — |
| H-partial torn row | — | — | — | — |
| H-stderr tearing/order | counts only | counts only | — | — |
| H-setm-leak | — | — | — | — |
| H-fixture-reap | killpg blind spot pre-fix | — | — | — |
| H-Dstate | — | — | — | — |
| H-usage/env matrix | — | — | — | — |
| H-temp residue | — | — | — | — |

**Verdict: partial.** The contract's mechanism is proven sound by peers (group kill frees the FIFO
open; sentinel ordering fixes ambiguity); the failure is *scope* — the same blocking-open class lives
in the unwatched parent guard pass (GAP 1), and the classification rules need the two explicit
precedences (GAP 2). Both fixable without changing any pinned row/stderr shape. The slow-repo→error
conversion is the priced tradeoff: it must be documented in `usage()` and the lesson, not hidden.
