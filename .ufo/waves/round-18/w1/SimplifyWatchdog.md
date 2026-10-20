STATUS: DONE — minimal pure-bash C1 watchdog: 37-line `emit_census` (+14 net), no new dependency, no trap, no TERM→KILL; 4 contract clauses named droppable, 2 named load-bearing; 3 falsifiers found (2 in the fixture layer the claim relies on).

Axis: operability (primary); calibration/coverage only where the simplification would lose a measured row.

Scope: leaf simplifier, no delegation, no commits, no census/script execution. Baseline
`b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`; `tools/souji-census.sh` unmodified in the lane
(`git -C … status --short -- tools/souji-census.sh` → no lines, per SentinelWatchdogKill.md; I
re-read the file at HEAD and cite its line numbers).

---

## 1. Verdict

**Holds, with three named exceptions.** The contract's safety property ("no single repository can
hang the fleet census; no lane fixture leaves a blocked process behind") is reachable with **one
temp file, one `set -m` pair, one background poller, and no trap**. The literal contract text is
*more* machinery than the property needs in three places (SIGTERM→SIGKILL, the marker's implied
file protocol, and an identity guard), and *less* in one place (the fixture kill, F1 below).

The kernel evidence in `census/round-18/leaked-procs-before-1631.txt` is still live and is the
strongest argument for the minimal form:

```
$ ps -o pid=,stat=,wchan:24=,args= -p 185605,289668,562279,574989
185605 S wait_for_partner   /usr/bin/git -C …/r-inc-fifo rev-parse --is-inside-work-tree
289668 S wait_for_partner   /usr/bin/git -C …/r-inc-fifo rev-parse --is-inside-work-tree
562279 S wait_for_partner   /usr/bin/git -C …/d2-fifo/b --no-optional-locks status --porcelain …
574989 S wait_for_partner   /usr/bin/git -C …/d2-fifo/b --no-optional-locks -c core.fsmonitor=false …
```

All four are `S` in `wait_for_partner` — blocked in `open(2)` on a writer-less FIFO,
**interruptible**. Every instance of the named harm class dies on the first signal that is sent.
SIGTERM therefore buys no deliverability that SIGKILL lacks; it buys only a grace period and a
second exit code. That is the whole justification for drop D1.

---

## 2. The sketch (recommended form)

Numbered for the justification table. `…unchanged…` = byte-identical to the current file.

```bash
 1  emit_census() {
 2    local root repo row rc pid self=$$ row_tmp
 3    root=$(guard_path root "$ROOT") || exit 2                        # …unchanged (:1396)
 4    [ -d "$root" ] || { printf 'souji-census: root is not a directory: %s\n' "$root" >&2; exit 1; }
 5    ROOT_RAW_IS_SYMLINK=0                                            # …unchanged (:1398-1399)
 6    if [ -L "$ROOT" ]; then ROOT_RAW_IS_SYMLINK=1; fi
 7    list_repos "$root"                                               # …unchanged (:1400)
 8    local -a rows=()                                                 # …unchanged (:1401)
 9    row_tmp=$(mktemp /var/tmp/souji-census-row.XXXXXX) || { printf 'souji-census: mktemp failed\n' >&2; exit 1; }
10    for repo in "${REPOS[@]+"${REPOS[@]}"}"; do                     # …unchanged (:1402)
11      set -m
12      census_one "$repo" </dev/null >"$row_tmp" &
13      pid=$!
14      ( n=0
15        while [ "$n" -lt "$REPO_TIMEOUT" ] && kill -0 "$pid" 2>/dev/null && kill -0 "$self" 2>/dev/null; do sleep 1; n=$((n + 1)); done
16        kill -0 "$pid" 2>/dev/null || exit 0
17        : >"$row_tmp.to"
18        kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
19      ) </dev/null >/dev/null 2>&1 &
20      set +m
21      if wait "$pid"; then rc=0; else rc=$?; fi
22      if [ "$rc" = 2 ]; then exit 2; fi
23      if [ -e "$row_tmp.to" ] && [ "$rc" != 0 ]; then
24        printf 'souji-census: repo-timeout %ss %s\n' "$REPO_TIMEOUT" "$repo" >&2
25        rows+=("$(sanitize_field "$repo")"$'\t0\t0\t0\t0\t\terror')
26      elif [ "$rc" = 0 ]; then
27        rows+=("$(<"$row_tmp")")
28      else
29        printf 'souji-census: census failed for %s (rc=%s)\n' "$repo" "$rc" >&2
30        exit 1
31      fi
32      rm -f -- "$row_tmp.to"
33    done
34    rm -f -- "$row_tmp"
35    printf '%s\n' "$HEADER"                                          # …unchanged (:1413)
36    for row in "${rows[@]+"${rows[@]}"}"; do printf '%s\n' "$row"; done
37  }
```

Surface, three sites, `+8` lines:

```bash
# after :199 (SELFTEST=0)
REPO_TIMEOUT="${SOUJI_CENSUS_REPO_TIMEOUT:-600}"

# in the arg loop, after :2037 (--include-root)
    --repo-timeout)
      [ "$#" -ge 2 ] || usage_err "--repo-timeout needs seconds"
      REPO_TIMEOUT=$2; shift 2 ;;
    --repo-timeout=*) REPO_TIMEOUT=${1#*=}; shift ;;

# immediately BEFORE :2053  (if [ "$SELFTEST" = 1 ]; then run_selftest; fi)
case "$REPO_TIMEOUT" in
  ''|*[!0-9]*) usage_err "--repo-timeout must be integer seconds 1..86400" ;;
esac
if [ "${#REPO_TIMEOUT}" -gt 5 ] || [ "$REPO_TIMEOUT" -lt 1 ] || [ "$REPO_TIMEOUT" -gt 86400 ]; then
  usage_err "--repo-timeout must be integer seconds 1..86400"
fi
```

Syntax-checked without execution (see §8): `bash -n` rc 0; `shellcheck -s bash -` rc 0.

---

## 3. Every line, and why it is there

| L | line | why it cannot be removed without losing a named property |
|---|---|---|
| 1 | `emit_census()` | same entry point; `emit_compare` (:1512) calls it with stdout redirected, so the function must not assume a tty. |
| 2 | locals incl. `self=$$` | `$$` is the *script's* pid even inside the later subshell (POSIX: `$$` is the invoking shell); captured once so the watchdog can test the census's life without a race on `$PPID`. `row_tmp` declared with the others so `set -u` cannot fire. |
| 3–8 | unchanged | — |
| 9 | `mktemp … \|\| {…exit 1}` | **load-bearing.** The worker's stdout must be a *file*, not `$(…)`. With command substitution the parent blocks on **pipe EOF**, and pipe EOF is held by every writer — including a grandchild that survives the kill (D-state, or a `setsid` escape, Sentinel F3). File stdout + `wait "$pid"` bounds the parent to the **one process it reaps**. Same `/var/tmp/souji-census-*.XXXXXX` convention as :1510. |
| 10 | loop | unchanged; `REPOS` is already sorted by `list_repos`. |
| 11 | `set -m` | puts the *next* background job in its own process group, so the group id **is** `$!` and one negative-target kill reaches the whole `census_one` tree. `set -m` (not `set -e`-visible) is the only bash primitive that does this without an external `setsid`. |
| 12 | worker fork, `</dev/null >file` | `set` and `census_one` are shell functions, so `timeout(1)`/`setsid(1)` cannot call them (see D5). `</dev/null`: a job in a non-foreground pgroup that reads the tty takes SIGTTIN; git must never depend on inherited stdin. `>file` per L9. stderr stays inherited so `config-unsupported` / `status-skipped` / `git-metadata-*` diagnostics keep streaming exactly as today (see D6). |
| 13 | `pid=$!` | fresh from this fork, never defaulted, never carried across iterations. A `^[1-9][0-9]*$` guard therefore has **no reachable input** (D4). |
| 14–19 | watchdog subshell | one process per repo, no state outside the repo's iteration. |
| 15 | poll | `n < T` is the bound; `kill -0 $pid` exits the poller as soon as the repo is done (so a healthy repo costs ≤1 s of poller life, not T); `kill -0 $self` makes the poller also the **parent-death cleaner**: if the census is killed by an operator harness, the poller notices within 1 s and reaps the worker group instead of leaving it (F1/F3). `sleep 1` keeps it to builtins + one coreutils call; `[[`-free `[` matches file style. |
| 16 | `kill -0 \|\| exit 0` | re-check before signalling: closes most of the PGID-reuse window and stops the just-finished race from emitting a spurious timeout. |
| 17 | `: >"$row_tmp.to"` | the **only** timeout witness. Written *before* the kill so that any parent that observes a nonzero `rc` also observes the marker (L23). `:` is a builtin; no new command. |
| 18 | `kill -KILL -- -"$pid" \|\| kill -KILL "$pid"` | group kill is the *residue* property (git's own children, the fixture shim); the `\|\|` fallback is the *bound* property, and it holds even if `set -m` turned out to be a no-op (restricted shell, exotic build). Explicit `--` prevents a leading-dash pid from being parsed as a signal name. |
| 19 | `) … &` with `</dev/null >/dev/null 2>&1` | **load-bearing for callers.** An unredirected watchdog keeps the caller's stdout write end open, so `out=$(souji-census …)` or the Python fixture's `communicate()` waits on a process that is not the census. The contract's "holds no stdout/stderr pipe" clause is exactly this line. `&` also gives the poller *its own pgroup* because L11's `set -m` is still in force — that is what lets it survive a group TERM to the census (F1) and clean up. |
| 20 | `set +m` | restores the shell's signal/job handling for the rest of the loop body (bash re-installs SIGINT/SIGQUIT disposition; [INFERENCE] bash internals, F5). |
| 21 | `if wait …; then rc=0; else rc=$?; fi` | `wait` is a builtin and **waits only for that pid**, not for its group and not for pipe EOF; the `if` form suspends `set -e` for the expected nonzero statuses. |
| 22 | `rc = 2 → exit 2` | **first** branch, deliberately. `protected_fail` (:203) exits 2 from inside the worker; if the marker test came first, a protected refusal that landed in the same microsecond as the watchdog's decision would be downgraded to an `error` row and exit 0. Protected refusal must never be maskable. |
| 23 | marker ∧ `rc != 0` | the exact timeout predicate. Either term alone is wrong: marker-only discards a complete row when the repo finishes at the instant the poller fires (harm: lost measurement); `rc != 0`-only mislabels an OOM kill (137) as a timeout (harm: false stderr claim). Together they have no reachable false positive. |
| 24 | stderr line | byte-exact contract shape: `souji-census: repo-timeout <N>s <repo>`. |
| 25 | placeholder row | byte-exact contract row: `repo\t0\t0\t0\t0\t<empty>\terror`, passing through `sanitize_field` like the existing placeholder rows (:1266). |
| 26–27 | success | `$(<file)` is a builtin read; `census_one`'s stdout is all-or-nothing (every `printf` in it is a final complete row followed by `return 0`), so a partial row cannot be mistaken for a measurement. |
| 28–30 | other nonzero | unchanged contract semantics: message + exit 1. |
| 31–32 | `fi` / `rm -f …to` | marker cleared per repo; it is the only cross-iteration state and it is a file, so no variable can leak it. |
| 33–34 | `done` / `rm -f row_tmp` | the one temp file per run, removed on the normal path. (A run killed mid-loop leaves one 0-length `/var/tmp/souji-census-row.*`; `cleanup_census_tmp` (:211-215) only knows `CENSUS_TMP`, and extending it would clobber `emit_compare`'s own EXIT trap at :1511 — not worth a line.) |
| 35–37 | header + rows | unchanged. |

Behavioural delta that is *not* visible in the diff: `census_one` now runs in a background
subshell instead of the command-substitution subshell. It already had its own process; nothing in
`emit_census` reads `CFG_SOFT_REASON` / `META_SOFT_REASON` / any other global that
`guard_git_surface` (:904-905) sets, and both are reset at the top of each guard pass, so the
change removes a latent cross-repo leak rather than adding one.

---

## 4. What can be dropped — ranked, with the property each drop does not touch

| # | Drop | Saves | What is preserved | What is genuinely lost |
|---|---|---|---|---|
| **D1** | **SIGTERM→2 s→SIGKILL ⇒ SIGKILL only** | 2 lines, 2 s per timed-out repo, one rc code, the whole stale-PGID anchor problem (Sentinel F1) | The bound, the row, the stderr line, exit 0. All 58 named harmed processes are `S`/`wait_for_partner`; SIGKILL terminates them on the first signal. `census_one` installs no trap and has no cleanup to run. `GIT_OPTIONAL_LOCKS=0` (:174) and `--no-optional-locks` (:1122) mean the only lock-taking git call cannot leave `index.lock` behind. Its stdout goes to a file that L23 discards anyway. | A 2 s grace window in which a slow-but-progressing `git status` could finish (it will not: the bound is 600 s by default), and the 143-vs-137 distinction (unused: L23 keys on the marker). **Verifier-visible**: an arm that asserts "TERM observed, then KILL" (Sentinel's acceptance test 4) fails on D1. Reverting is a **2-line delta confined to L17-18**, because the decision block never inspects *which* signal killed the worker: `kill -TERM -- "-$pid" …/…; sleep 2;` inserted before L18. If the claim's wording is kept verbatim, take that delta; nothing else changes. |
| **D2** | **Per-repo stderr spool file** (Sentinel F2's "spool both streams") | 2 lines + a `cat` dependency | The bound, the row, the exit codes. The caller-pipe hazard is closed on the *stdout* side by L9/L19; on the stderr side it is closed by fixing the harness (F1) or by the group kill. | Live streaming order of `config-unsupported` lines relative to the row. If L1 declines F1, this drop must be reversed: `2>"$row_tmp.err"` on L12 plus `cat -- "$row_tmp.err" >&2` after L21, and `cat` joins :165. |
| **D3** | **`exit`/`TERM`/`INT` trap** | 2 lines, and the `trap`-clobbering risk against `emit_compare`'s `cleanup_census_tmp` (:1511, cleared at :1516) | Everything, because the poller's `kill -0 "$self"` clause (L15) covers *all* ways the census can die, including SIGKILL — which no bash trap can catch. | Nothing. This is a strict improvement over the trap, not a trade: one mechanism covers TERM, INT, SIGKILL, and a crash. The only cost is that the poller itself must be outside the census's pgroup, which L11/L19 give for free. |
| **D4** | **`^[1-9][0-9]*$` pid guard** | 2 lines | Everything. `pid=$!` is assigned from a fresh fork on the immediately preceding line; `$!` is a positive pid; `set -u` makes empty impossible; nothing else assigns `pid`. | Nothing. The guard Sentinel F1 asks for guards against a *stale or defaulted* variable that this construction cannot produce. Adding it is dead code; if a reviewer wants the invariant *documented*, one comment word ("fresh from this fork") is cheaper than three lines of test. |
| **D5** | **`timeout(1)` / `setsid(1)` as the whole watchdog** | would be 1 line — **rejected**, not dropped | — | `census_one` is a **shell function**; `timeout` can only exec a program. Wrapping it needs either `export -f` of the whole helper graph (re-importing the `BASH_FUNC_*` surface the header neutralises at :160-165) or a self-invocation `"$SELF" --root "$repo" --include-root` (double guards, header-stripping, two `guard_git_surface` passes per repo). Both are larger and less predictable than the 6 lines they replace. This is the one place where "fewest lines" loses to operability. |
| **D6** | **`--repo-timeout` flag (keep env only)** | 4 lines + 2 selftest arms | The bound, default, range. | Scriptability of the one-off (`--repo-timeout 1` fixtures, operator triage). The declared interface names both spellings, so this drop is *available* but **should not be taken** in round 18; it is listed because it is the only flag in the contract that adds no safety. |
| **D7** | **Upper bound 86400** | 1 test clause | The bound (`>= 1` is what safety needs). | Typo protection (`--repo-timeout 600600` would silently disable the watchdog for a run). Keep: it is one clause, and a too-large bound is exactly the foot-gun a 600 s default exists to prevent. |

**Not droppable, in one sentence each:**

- **The temp file (L9, L12/L27)** — with `$(…)` the parent waits for pipe EOF, i.e. for a process
  it does not reap; that is the original hang wearing a different hat.
- **`set -m` + negative target (L11, L18)** — without it the watchdog can only kill the leader and
  git's children (the actual `open(2)` blocker in the leaked list is a *grandchild* of the census
  shell) survive as residue; the bound would hold, C3's surface would not.
- **The marker (L17, L23)** — without it `rc` cannot distinguish the watchdog's kill from an OOM
  kill, and the honest stderr line becomes a lie.
- **`rc = 2` first (L22)** — the one exit that must never be masked.

---

## 5. Falsifiers and smallest fixes (outside the sketch)

**Ownership:** F1 and F2 are integration-owned — they land in `tests/fixtures/r17-census-hygiene.py`,
`census/round-17/run-matrix.py` and `run_selftest` (`tools/souji-census.sh:1608-2049`), which belong
to L1's patch, not to the wave-1 fixture author, whose scope is the historical r14/r15/r17 timeout
audit. L1 applies them; the fixture author was notified only so the audit does not read as settling
the residue question.

### F1 — HIGH: the fixture's `killpg` cannot reach the worker group the fix creates

`tests/fixtures/r17-census-hygiene.py:291-321` and `census/round-17/run-matrix.py:89-108` both do
`start_new_session=True` then, on `TimeoutExpired`, `os.killpg(proc.pid, SIGKILL)` followed by
`proc.communicate()`. Once `emit_census` puts the worker in its **own** pgroup (the contract's own
`set -m` line), `proc.pid` is the session leader's pgid only. A *failing* arm — precisely the arm
that hangs — therefore leaves the blocked git in a sibling pgroup, and `communicate()` waits on a
pipe the worker still holds on the stderr side. The fixture would reproduce the leak it is
supposed to detect.

Smallest fix, one line in each harness (do not add a containment layer to the tool):

```python
subprocess.run(["pkill", "-KILL", "-s", str(proc.pid)], check=False)  # session-wide; sid == proc.pid under start_new_session
```

and keep the `os.killpg` call as the first attempt. If procps is unacceptable, the equivalent is a
`/proc/*/stat` scan for field 6 == sid (~8 lines). The contract's fixture sentence should be
amended to "…on timeout kills the **session** (sid), not just the leader's group".

### F2 — MEDIUM: `--selftest` inherits a tight bound and then fails against a correct fix

`run_selftest` invokes the tool ~10 times (`:1699-1701,1810-1811,1826-1827,1841-1842,1863-1864,1872,1884-1886,1895-1897,1955-1956,2005-2006`) with `env -u GIT_DIR … "$SELF"`. Adding
`REPO_TIMEOUT="${SOUJI_CENSUS_REPO_TIMEOUT:-600}"` makes every one of those children inherit the
operator's env. `souji-census.sh --selftest --repo-timeout 1` (or the env spelling) would then time
out the worktree fixtures and the selftest would report FAIL on a correct implementation.

Smallest fix, one line at `:1614` (next to the `ST_TMP` trap):

```bash
  export SOUJI_CENSUS_REPO_TIMEOUT=600   # fixtures must not inherit a tight bound
```

The new timeout arm passes `--repo-timeout 1` explicitly; the flag arm (:2037) assigns *after* the
env default, so the flag wins.

### F3 — MEDIUM: the bound is only a bound for signal-deliverable waits

`wait "$pid"` returns when the leader is **reaped**. A leader in uninterruptible I/O (FUSE/sshfs/
NFS mount inside the scanned tree, or a FIFO on one) does not die from SIGKILL until the syscall
returns, so the fleet can still block — with state `D`, not `S`. Nothing in userspace fixes that:
skipping the `wait` only converts the block into a poll-plus-zombie leak.

Smallest fix: **do not add machinery**; narrow the claim by one sentence in the existing residual
paragraph (`:144-152`, which already ends "the guard and the later access are not one atomic
operation"): "the per-repo bound terminates any process that can take a signal; a process in
uninterruptible I/O is not bounded by it." The evidence class in
`census/round-18/leaked-procs-before-1631.txt` is entirely `S` (§1), so the declared harm is
covered; the claim's absolute wording is what needs the qualifier.

### F4 — MEDIUM: two new production command names must join the `unset -f` allowlist (:165)

`sleep` does not appear anywhere in the tool today (grep below), and the sketch makes it the
watchdog's clock. An inherited `BASH_FUNC_sleep` that returns immediately would make the poll loop
burn its T iterations in microseconds and **time out every repo on every run** — a fleet-wide DoS
through the exact vector the header names at `:160-164`. `mktemp` is already used at `:1510`, but
the patch moves it onto the always-taken path.

Smallest fix, one word each on `:165`:

```bash
unset -f git find du stat awk grep sort head cut date readlink mktemp sleep 2>/dev/null || true
```

If D2 is reversed, add `cat` in the same edit (`cat` is already used at `:1722`/`:1823`, but only
in the selftest).

### F5 — LOW: `set -m`'s signal-disposition window

While job control is on, bash sets SIGINT/SIGQUIT to be handled by the job-control machinery; the
window here is L11-L20 per repo. A signal delivered inside it is not lost — it reaches the census
after `set +m` and the poller's `$self` clause cleans up ≤1 s later — but an INT that used to reach
in-flight git no longer does; git is now SIGKILLed by the poller instead of SIGINTed. [INFERENCE:
bash internals read, not executed under the probe rule.] No change recommended; note it where the
claim says "no lane fixture leaves a blocked process behind", because a verifier watching for
"SIGINT forwarded" would see a different signal.

### F6 — LOW: PGID reuse widens 2 s ⇒ one syscall under D1

The poller re-checks `kill -0` at L16 immediately before the single kill. `kill(2)` documents that
group success means "at least one signal was delivered", so no wait-for-reap is implied. D1 is the
smallest exposure this class of mechanism can have without a pidfd; note it, do not engineer past
it.

---

## 6. Patch plan (exact anchors, line budget)

| site | anchor at b576341 | change |
|---|---|---|
| defaults | after `:199` (`SELFTEST=0`) | `REPO_TIMEOUT="${SOUJI_CENSUS_REPO_TIMEOUT:-600}"` (1) |
| emit_census | replace `:1394-1416` | sketch L1-L37 (**+14 net**, 23 → 37) |
| arg loop | after `:2037` (`--include-root`) | `--repo-timeout` + `--repo-timeout=` arms (4) |
| validation | before `:2053` (selftest dispatch) | digit + length + range block (3) |
| selftest env pin | after `:1614` | `export SOUJI_CENSUS_REPO_TIMEOUT=600` (1) |
| timeout fixture | after `:2007` (benign-neighbour check), before the hardlinked-config control at `:2009` | shim + 5 assertions (≈12) |
| command allowlist | `:165` | `mktemp sleep` (+`cat` iff D2 reversed) (0 lines) |
| docs | `:16-17` CLI block; after `:75` (`--selftest` paragraph); `:153-157` exit codes; `:158-160` Env | `--repo-timeout SECONDS`; row/stderr contract; `SOUJI_CENSUS_REPO_TIMEOUT`, default 600, 1..86400, invalid → 2 (4) |

Total ≈ **+39 lines, 0 deletions**. Exit codes are unchanged (0/1/2/3).

**Smallest fixture that proves the whole contract in-tool** (no Python, no FIFO, no new dependency;
PATH shim is the post-guard swap class L1 used, so the guard still sees a normal repo):

```sh
# $ST_TMP/bin/git   (chmod +x);  HANG and PIDF interpolated by the fixture
#!/bin/sh
case "$*" in *"$HANG"*status*) printf '%s\n' "$$" > "$PIDF"; sleep 60 ;; esac
exec /usr/bin/git "$@"
```

invoked as `PATH="$ST_TMP/bin:$PATH" … "$SELF" --root "$fleet3" --repo-timeout 1` and asserting:
rc 0; the hanging repo's columns 2-5 are `0` and flags `error`; stderr carries
`repo-timeout 1s <path>`; the neighbour row is still measured; and `kill -0 "$(cat "$PIDF")"`
fails — the last one is the "0 blocked processes" proof, using only a builtin, and it proves the
*group* kill because the shim is a grandchild of the worker.

---

## 7. Interface conformance

| contract clause | sketch |
|---|---|
| own process group, `set -m` only around the fork | L11-L20 (one pair around **both** forks — the poller's own pgroup is what makes D3 work) |
| stdout to a private temp file | L9, L12 |
| watchdog after the bound | L15 (T+≤1 s; measured in 1 s slices, zero added latency to a healthy repo) |
| SIGTERM → SIGKILL 2 s later | **D1: SIGKILL only**; 2-line revert shown in D1 |
| `<repo>\t0\t0\t0\t0\t\terror` | L25 |
| `souji-census: repo-timeout <N>s <repo>` | L24 |
| other repos measured, exit 0 | L33 + fall-through to `:2071` |
| `--repo-timeout N` / `SOUJI_CENSUS_REPO_TIMEOUT`, 1..86400, 600, invalid → 2 | surface block; validated before selftest dispatch, so `--selftest --repo-timeout 0` is also a usage error |
| `census_one` 2 → whole run 2; other nonzero → 1 | L22 then L28-L30 |
| watchdog never outlives its repo, no caller pipe | L15 (`$self`), L19 (redirects) |
| fixtures `start_new_session` + killpg | **F1: killpg is insufficient; use the session (sid)** |

---

## 8. Evidence

Read-only, at the lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`:

```text
read tools/souji-census.sh:1-80,84-200,204-283,499-643,1180-1345,1340-1470,1599-1703,1930-2072
grep  'timeout|REPO_TIMEOUT|repo-timeout'            tools/souji-census.sh  => no matches (feature absent)
grep  '^(emit_census|census_one|list_repos|guard_git_files|guard_git_surface|count_dirty|emit_compare|run_selftest)\(\)'
      => 546 guard_git_files, 902 guard_git_surface, 1104 count_dirty, 1261 census_one,
         1343 list_repos, 1394 emit_census, 1504 emit_compare, 1608 run_selftest
grep  'CENSUS_TMP=|trap '                           => 202 ''; 1510 mktemp; 1511 trap cleanup; 1515-1516 reset
grep  'unset -f'                                    => 165 (allowlist: git find du stat awk grep sort head cut date readlink)
grep  'GIT_OPTIONAL_LOCKS|no-optional-locks'        => 174 export GIT_OPTIONAL_LOCKS=0; 1122 git -C … --no-optional-locks
grep  '\bsleep\b'                                   => no matches (sleep is a new production command name)
read  tests/fixtures/r17-census-hygiene.py:271-321   => start_new_session=True; os.killpg(proc.pid, SIGKILL); communicate()
read  census/round-17/run-matrix.py:80-115           => same pattern; comment says "kill the whole group"
read  census/round-18/leaked-procs-before-1631.txt:1-17 (named evidence file)
ps -o pid=,stat=,wchan:24=,args= -p 185605,289668,562279,574989
      => 4 live: state S, wchan wait_for_partner (interruptible FIFO open)
bash -n        over the sketch via stdin                         => rc 0, no output
shellcheck -s bash -  over the sketch via stdin (v0.11.0)       => rc 0, no output
```

Not run, by the probe rule: `tools/souji-census.sh`, any copy, any `--selftest`, any fixture, any
kill/pkill, any git write, `jj`. The sketch's mechanism claims that depend on bash internals
(`set -m` pgroup creation, `$$` in subshells, `set +m` restoring handlers, 128+signal `wait`
status) are marked [INFERENCE]: syntax-validated, not executed. No tool was installed or updated.

## 9. Tradeoff

The recommended form trades a 2 s graceful window and a verifier-visible TERM for a 2 s smaller
per-repo worst case, a single-signal PGID window, no trap, no anchor process, and no new
dependency — and it keeps the two properties that actually carry the claim: the parent waits only
on a process it reaps (temp file), and the kill reaches the process that is blocked (its group).
The next deletion that would improve anything is D2's stderr spool, and it is only safe *after*
F1 lands; without F1 it converts a fixture-visible hang into a silent one.
