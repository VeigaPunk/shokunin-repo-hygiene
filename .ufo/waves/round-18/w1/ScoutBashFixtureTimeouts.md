STATUS: DONE — static inventory complete: 24 executed `timeout` source sites (loop bodies repeat at runtime), 0 shell background jobs, 4 no-`-k` sites, 1 producer outside its timeout, 2 nested-group preemption paths, 1 unguarded detached-maintenance case.

# ScoutBashFixtureTimeouts — r18 W1 static inventory

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, base `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (short `b576341`).
Scope: static reads of, and only of, the seven assigned files:

| file | lines | sha256 |
|---|---:|---|
| tests/fixtures/r12-maintenance-guard.sh | 241 | `a359070a66706ad2570eb92f0ce87f5ba840136f02f3cf987adb57272e95a0f9` |
| tests/fixtures/r13-quarantine-bounds.sh | 303 | `23b2b879352b3a3ef2f3fe4297ab2818643c8d45db3a75dda2d5dd9c18b07f5e` |
| tests/fixtures/r13-repo-structure.sh | 659 | `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` |
| tests/fixtures/r17-jj-receipts.sh | 1070 | `e3cd9d3ebd5a82b8c20fd2e548f4b5a94e7353e211d995041707cd0365dc09d5` |
| tools/souji-quarantine.sh | 1842 | `83cc3ce1331bf75ed23b9148ad82b6f0881e9eda1d9a283a224f0318d6ab1de3` |
| tools/souji-verify.sh | 1531 | `f88fed23e2c80fdfea13775659f2dfc157f33a5540772059c7e3ab5dd6c7ff1c` |
| tools/souji-vault-verify.sh | 1776 | `5cb0fb13fc9b0fc306e3841e5857f028610f1698bee8e8cf69d51575ae2810bb` |

No tool install or update was performed.

## 1. Timeout semantics used for the verdicts

Host binary: `/usr/bin/timeout` is **GNU coreutils 9.12** (`/usr/bin/timeout --version`). None of the 24 sites passes `--foreground`/`-f`, `-s`, or `--preserve-status`.

GNU 9.12 help (`/usr/bin/timeout --help`) states that with `-f, --foreground` "children of COMMAND will not be timed out". Therefore, at every site below, the command is placed in its own process group and the expiry signal is sent to that **group**. A descendant blocked in `open(2)`/`read(2)` on a FIFO with default `SIGTERM` disposition dies when the group is signalled; it does not need SIGKILL.

A *blocked grandchild survives* the bound only through one of:

1. **Outside the group** — a producer/sibling not under the `timeout` (quarantine:350), or a grandchild placed in a different group by a nested `timeout`.
2. **TERM-immune** — ignores/catches `SIGTERM` (no `-k`, or the direct child exits first so the `-k` escalation never runs). `-k` is documented as "send a KILL signal if COMMAND is still running"; it is not a group reaper for members left after COMMAND exits. **[INFERENCE: coreutils control flow; the documented wording and observed GNU behavior support it.]**
3. **Uninterruptible D state** — signal is pending until the kernel returns.
4. **Preemption** — an outer timeout kills this `timeout` process before its own timer fires, removing the only timer for its group.

A site with `-k` is therefore "NO for ordinary default-TERM descendants", not an absolute no. Without `-k`, any TERM-immune descendant survives; a TERM-immune direct child also keeps `timeout` itself waiting past the bound.

## 2. Executed `timeout` inventory (24 sites)

Flags column: `-k` = `--kill-after` seconds; `fg` = `--foreground` present. No site uses `fg`.

### 2.1 `tools/souji-quarantine.sh` — 7 executed + 2 display-only strings

| # | line | invocation (abbrev.) | flags | blocked grandchild survives? |
|---:|---:|---|---|---|
| 1 | 350 | `git -C "$CREPO" cat-file blob "$intro:$REL" \| timeout --kill-after=10 120 sha256sum \| cut ...` | `-k10 120` | **YES — producer `git cat-file` is outside the timeout's group**; timeout only owns `sha256sum`. A blocked producer keeps the pipeline/command substitution open after 120 s. |
| 2 | 537 | `emit CMD ... "timeout --kill-after=10 60 git ... mv ..."` | `-k10 60` | N/A — string emitted by `--dry-run`; not executed here. If run as printed, ordinary NO. |
| 3 | 540 | `emit CMD ... "timeout --kill-after=10 60 mv --no-copy -T ..."` | `-k10 60` | N/A — string; not executed here. If run as printed, ordinary NO. |
| 4 | 564 | `timeout --kill-after=10 60 git -C "$crepo" mv -- "$rel" "$qpath"` | `-k10 60` | NO for ordinary descendants (same group, group SIGTERM + SIGKILL). `git mv` does not daemonize. |
| 5 | 566 | `timeout --kill-after=10 60 mv --no-copy -T -- "$ct" "$qpath"` | `-k10 60` | NO (same; `mv` spawns nothing). |
| 6 | 763 | `out=$(timeout --kill-after=10 120 sha256sum -- "$1" 2>/dev/null)` | `-k10 120` | NO — no descendants. |
| 7 | 773 | `timeout --kill-after=10 300 bash -c 'find ... \| sort -z \| xargs ... sha256sum \| sha256sum \| cut' _ "$d"` | `-k10 300` | NO for ordinary pipeline members: one group, no job control, `-k` escalation. |
| 8 | 812 | `out=$(timeout --kill-after=10 60 find ... -print -quit)` | `-k10 60` | NO — no descendants. |
| 9 | 1226 | `V_RAW=$(... timeout --kill-after=10 120 bash "$VERIFY_BIN" ... 2>"$ERRTMP")` | `-k10 120` | NO for ordinary children (`rg`/`git`/process substitutions in the same group); verify does not `setsid` or `set -m`. |

The tool's own header (lines 128–137) claims "Every per-target staging move and digest runs under a fixed GNU `timeout --kill-after=10` bound". Site 1 contradicts that claim on the producer side: the digest *consumer* is bounded, the object *read* is not.

Stage-5 deletion is explicitly not covered by Q8 (`souji-quarantine.sh:137`, `606-614`): `rm -rf -- "$qpath"` (607) and `git -C "$crepo" rm --cached ...` (614) have no timeout. Not an invocation, but an unbounded external call.

### 2.2 `tools/souji-verify.sh` — 0 sites

No `timeout` token anywhere in the file (case-insensitive scan), no `--foreground`, no shell background job. The engine is bounded **only by its callers** (`souji-quarantine.sh:1226`, `r17-jj-receipts.sh:257,876,877,941,953`). Standalone invocation can block indefinitely in `rg` (`224`, `754`), `git`, or its process substitutions (`510`, `1044`).

### 2.3 `tools/souji-vault-verify.sh` — 2 sites

| # | line | invocation (abbrev.) | flags | blocked grandchild survives? |
|---:|---:|---|---|---|
| 10 | 213 | `out=$(timeout "$CLI_TIMEOUT" "$bin" vault:hash "$vp" 2>/dev/null)`; `CLI_TIMEOUT=${SOUJI_CLI_TIMEOUT:-6}` (line 83, sanitized 1760–1762) | **no `-k`** | **YES.** Only SIGTERM at the bound. A CLI (or CLI child) that catches/ignores TERM, or is in D state, survives; `timeout` then waits indefinitely and the command substitution stays open. The V11b selftest hang shim is `sleep 30` (1524–1527, TERM-killable), so it does not exercise this failure. |
| 11 | 1301 | `OUT_TEXT=$(env ... timeout 120 "$SELF" "${args[@]}" 2>&1)` | **no `-k`** | **YES (nested group).** `$SELF`'s inner `cli_claim` timeout (213) creates a separate CLI group. An outer TERM at 120 s kills `$SELF` and the inner `timeout` (both in the outer group) but not the CLI group; the inner timer dies with the inner `timeout`, so no SIGKILL is ever sent. Reaches the real path only when `$SELF` runs in auto/cli mode (line 356 skips the CLI under `--fallback`). |

`--fallback` at line 356 sets `cli=skipped(fallback)`; therefore r17's `vlt_run` (which passes `--fallback`) does **not** create the nested CLI group (see 2.7).

### 2.4 `tests/fixtures/r12-maintenance-guard.sh` — 0 sites

No `timeout`, no `--foreground`, no shell `&`/`wait`/`$!`/`disown`/`coproc`. All `git` calls are unbounded (`g()` at 93–96 and the raw `"${GIT_BASE[@]}" ... commit` at 155). The default case **deliberately** spawns git's detached auto-maintenance: line 155 uses `GIT_BASE` (no `maintenance.autoDetach=false`), so `git commit` daemonizes `git maintenance run --auto` (header 21–24); the case polls up to 30×1 s (171–175) but never waits for or reaps that detached process. It is the only asynchronous child in the seven files.

### 2.5 `tests/fixtures/r13-quarantine-bounds.sh` — 2 sites (1 outer + 1 shim template)

| # | line | invocation (abbrev.) | flags | blocked grandchild survives? |
|---:|---:|---|---|---|
| 12 | 143 | `RUN_OUT=$(env ... "$REAL_TIMEOUT" --kill-after=5 20 bash "$TOOL" --hold 0 "$@" 2>&1)` | `-k5 20` | **YES, conditionally.** The tool's own sites (2.1) create inner groups with 60/120/300 s (+10) timers. When the outer 20 s fires first, it kills the inner `timeout` parents (they are in the outer group) and therefore removes the only timers for the inner groups; the inner commands (e.g. `git mv`, `bash verify`, `bash -c` dir digest) survive. Those in the stage-2 path inherit the outer `RUN_OUT` pipe, so the fixture's `RUN_OUT=$(...)` can stay open past its own 25 s bound. |
| 13 | 154 (generated by 146–156) | `exec <real timeout> --kill-after=1 2 "$@"` — PATH shim used for every tool `timeout` call | `-k1 2` | NO for a properly shimmed call: inner group is TERM+KILLed within 3 s, before the outer 20 s. The shim only matches `--kill-after=<n> <integer>` (150–154), so it cannot bound the un-timeouted producer at `souji-quarantine.sh:350`, nor any `timeout`-less pre-flight. |

Cases 04/05 install the shim (228, 246) so their inner bounds resolve before 20 s. Cases 01/02/03 run **unshimmed**, so the 20 s outer bound is below the tool's 60/120 s inner bounds: any >20 s inner block in those cases is orphaned.

### 2.6 `tests/fixtures/r13-repo-structure.sh` — 2 sites

| # | line | invocation (abbrev.) | flags | blocked grandchild survives? |
|---:|---:|---|---|---|
| 14 | 227 | `"${ENV_ALLOW[@]}" timeout 120 "${cmd[@]}" --repo "$repo"` | **no `-k`** | **YES, conditionally.** Only SIGTERM at 120 s. The probe or a grandchild that catches/ignores TERM, or is in D state, survives; a TERM-immune direct child makes `timeout` wait past the documented bound. |
| 15 | 233 | `"${ENV_ALLOW[@]}" timeout 120 git -c maintenance.auto=false -c maintenance.autoDetach=false -C "$repo" repo structure --format=lines` | **no `-k`** | Same as 227. `git repo structure` does not daemonize, but TERM-immune/D-state children and the missing KILL escalation remain. |

The fixture header claims the measured command "is bounded by `timeout 120`" (109); without `-k` that is a soft TERM-only bound.

### 2.7 `tests/fixtures/r17-jj-receipts.sh` — 11 sites

Every site is `timeout --kill-after=5 240 bash <tool> ...` with no `--foreground`. Direct children are the lane tools; their ordinary descendants inherit the group.

| # | line | target | blocked grandchild survives? |
|---:|---:|---|---|
| 16 | 257 (`vfy_run`) | `souji-verify.sh` | NO ordinary: verify installs no inner timeout/`setsid`; `-k5` group kill. D-state only. |
| 17 | 266 (`vlt_run`) | `souji-vault-verify.sh --fallback` | NO ordinary: `--fallback` skips `cli_claim` (`vault:356`), so no inner group; `-k5` group kill. D-state only. |
| 18 | 277 (`q_run`) | `souji-quarantine.sh --dry-run --hold 0` | **YES, conditionally.** Quarantine's `dir_digest` bound is 300+10 s (`quarantine:773`), which exceeds the outer 240+5 s. For a directory target (J10/J11 pass `"$KREPO/d"`, and dry-run still computes the stage-1 pin at `quarantine:517-530`), an outer preemption kills the inner `timeout` and orphans the dir-digest group with no timer. Its stdout is the inner `$(...)` capture, not `Q_OUT`, so the fixture may proceed but leaks the process; the removed timer is the defect. |
| 19 | 876 | J6 verify selected | NO ordinary (as 16). |
| 20 | 877 | J6 verify baseline | NO ordinary (as 16). |
| 21 | 896 | J6 vault selected | NO ordinary (as 17: `--fallback`). |
| 22 | 897 | J6 vault baseline | NO ordinary (as 17). |
| 23 | 941 | J8 verify before | NO ordinary (as 16). |
| 24 | 953 | J8 verify after | NO ordinary (as 16). |
| 25 | 979 | J8 vault before | NO ordinary (as 17). |
| 26 | 985 | J8 vault after | NO ordinary (as 17). |

Count correction: 16–26 is **11** rows (r17); grand total executed sites = 7 (quarantine) + 2 (vault) + 2 (r13q) + 2 (r13repo) + 11 (r17) = **24**. The two quarantine `emit CMD` strings (537/540) are not executed.

## 3. Background jobs / asynchronous children

Exhaustive scan for a single `&` (excluding `&&`, `>&`, `<&`, `&>`), `wait`, `$!`, `disown`, `coproc`, `setsid`, and `set -m`:

- **Shell background jobs: 0 in all seven files.** No `wait`, no `$!`, no `disown`, no `coproc`. No tool enables job control (`set -m`), so no descendant escapes by that route.
- **Process substitutions** (asynchronous subshells, not jobs):
  - `tools/souji-quarantine.sh`: 924 `< <(ledger_lines)`, 1001 `-f <(printf ...)`, **1377 `< <(git -C "$repo" worktree list --porcelain ...)`**.
  - `tools/souji-verify.sh`: 264 `< <(printf ...)`, 341 and 659 `< <(ledger_lines)`, **510 and 1044 `< <(git ... worktree list ...)`**.
  - `tools/souji-vault-verify.sh`: 457 `< <(printf ...)`, **701 and 1253 `< <(git ... worktree list ...)`**, 860 `< <(ledger_lines)`.
  - r12 / r13q / r13repo / r17: none.
  The `git worktree list` substitutions are unbounded external children. Under a caller's GNU `timeout` they inherit the caller's group and are signalled; standalone they can block the enclosing `while read` loop.
- **Detached process:** `r12-maintenance-guard.sh:155` runs `git commit` with `maintenance.autoDetach` unset, spawning a detached `git maintenance run --auto` (the fixture's own measured hazard). It leaves the fixture's process group by design, is not a shell job, is not covered by any `timeout`, and is not waited for after the 30×1 s poll (171–175). If it outlives the poll, the EXIT trap (`rm -rf "$WORK"`, 71/72) can remove the repo under it, producing exactly the deleted-cwd residue class.

## 4. Findings, ranked, with smallest fix

### F1 (HIGH) — `tools/souji-quarantine.sh:350`: digest bound covers only the consumer
`git -C "$CREPO" cat-file blob ... | timeout --kill-after=10 120 sha256sum | cut ...`
`timeout` owns `sha256sum`; the `git cat-file` producer is a sibling in the tool's process group and is not signalled at 120 s. A producer blocked on a hung object store, a FIFO-based object/alternate, or a promisor lazy fetch (the tool exports neither `GIT_NO_LAZY_FETCH` nor `maintenance.auto=false`) keeps the pipeline open. Standalone, the tool hangs forever despite the documented Q8 bound; under the r13q/r17 wrappers the outer 25 s/245 s bound is the only thing that kills it, so the tool's own contract is still violated.
**Smallest fix:** one rooted shell for producer+consumer:
```bash
blob_sha=$(timeout --kill-after=10 120 bash -c '
  git -C "$1" cat-file blob "$2" 2>/dev/null | sha256sum
' _ "$CREPO" "$intro:$REL" | cut -d' ' -f1 || true)
```
(The outer `timeout` then owns one group containing both `git` and `sha256sum`.) Optionally add `GIT_NO_LAZY_FETCH=1` for promisor repos, but the group bound is the load-bearing fix.

### F2 (HIGH) — nested timeouts defeat outer group kills (r13q:143)
The fixture's outer `-k5 20` is shorter than the tool's own 60/120/300 s (+10 s) inner bounds. When the outer fires first, it kills the inner `timeout` process (the only holder of the inner group's timer); the inner command survives, reparented. Stage-2 `git mv`/`mv` orphans inherit the outer `RUN_OUT` pipe (`2>&1` at 143), so `RUN_OUT=$(...)` can stay open past the fixture's 25 s bound — the fixture hangs on EOF, not on the timeout. Cases 01/02/03 run unshimmed; 04/05 are shimmed and safe.
**Smallest fix:** make the outer bound exceed the reachable inner maximum for the selected case (file flow: 120+10+5 = 135 s; directory flow: 300+10+5 = 315 s), or install the `--kill-after=1 2` shim for every case (it only matches the documented shape, 150–154; note the shim's 2 s duration may be too tight for a slow host's legitimate digest, so the per-case bound is safer). Do not leave 20 s with an unshimmed 60/120 s inner bound.

### F3 (MEDIUM) — r17:277 outer 240+5 s vs quarantine `dir_digest` 300+10 s
For J10/J11 directory targets, dry-run still computes the stage-1 pin (`quarantine:517-530`) via `dir_digest` (`quarantine:773`). A blocked/slow directory digest outlives the outer bound; the outer preemption kills the inner `timeout` and orphans the digest group with no timer. Its stdout is the inner `$(...)` capture, not `Q_OUT`, so the fixture is not guaranteed to hang on EOF, but the process leak is real and invisible to `RUN_RC`/`Q_RC`.
**Smallest fix:** raise `q_run`'s outer bound to ≥315 s, or lower the tool's directory-digest bound to ≤180 s (a 300 s bound in a fixture that otherwise caps at 240 s is internally inconsistent).

### F4 (MEDIUM) — `tools/souji-vault-verify.sh:213`: no KILL escalation
`timeout "$CLI_TIMEOUT" ...` sends only TERM (`CLI_TIMEOUT` default 6 s; r17 exports 2 s at line 190). A CLI that catches/ignores TERM, or is in D state, survives; `timeout` and the enclosing command substitution wait beyond the bound. V11b (1599–1602) passes only because its hang shim is plain `sleep 30` (1526), which dies on TERM.
**Smallest fix:** `timeout --kill-after=2 "$CLI_TIMEOUT" "$bin" vault:hash "$vp"`; add a V11b variant whose shim is `trap '' TERM; sleep 30` to prove the escalation.

### F5 (MEDIUM) — `tests/fixtures/r13-repo-structure.sh:227,233`: no KILL escalation
Both measured calls use bare `timeout 120`. A TERM-immune probe/grandchild or a D-state process outlives the bound; a TERM-immune direct child keeps `timeout` waiting, so the fixture exceeds its documented 120 s bound rather than exiting 2.
**Smallest fix:** `timeout --kill-after=5 120` at both sites.

### F6 (MEDIUM) — `tools/souji-quarantine.sh` stage-1 pre-flight is unbounded
`git_tracked` (`235`), `git_dirty_tracked` → `git --no-optional-locks status --porcelain` (`254`, called at `506/509` and `1310/1311`), `git log --diff-filter=A` / `merge-base` / `rev-list` (`~330-338`), and `q_jj_colocated` state checks are outside every `timeout`. `git status` reads `$GIT_DIR/info/attributes`; a FIFO swapped in there (the exact C1 census trick) blocks stage 1 before the bounded digest runs. Stage-5 `rm -rf` (`607`) and `git rm --cached` (`614`) are also unbounded by design (`137`).
**Smallest fix:** a single helper used for every git call in the tool, e.g. `q_git() { timeout --kill-after=10 60 git "$@"; }`, applied to pre-flight and stage-5 git calls; bound `rm -rf` with `timeout --kill-after=10 60 rm -rf -- "$qpath"`.

### F7 (MEDIUM) — `tests/fixtures/r12-maintenance-guard.sh`: no timeout and an unreaped detached process
No `timeout` anywhere. A `git commit` blocked on a FIFO in `.git/info/attributes` (or any hung git call) hangs the fixture with no bound. The `plain-commit-default` case intentionally daemonizes `git maintenance run --auto` (155, header 21–24); the 30×1 s poll (171–175) detects the effect but never waits for/reaps that process, and the EXIT trap can remove the repo under it.
**Smallest fix:** wrap `g()` and the raw default-case `git` call in `timeout --kill-after=5 60`; after the poll, add a bounded quiescence wait before the trap removes `$WORK` (a fixed settle sleep, or a read-only `/proc/*/cmdline` scan for `git maintenance` whose cwd is the fixture repo — no signals) and record any residual pid in the case detail.

### F8 (LOW) — `tools/souji-vault-verify.sh:1301`: no KILL escalation + nested CLI group
`timeout 120 "$SELF"` has no `-k`; the inner `cli_claim` timeout creates a second group. If the CLI survives its inner TERM, the outer TERM kills `$SELF` and the inner `timeout`, leaving the CLI group with no timer. This path is the selftest/auto-cli path (not r17's `--fallback` runs).
**Smallest fix:** add `--kill-after=5` at 1301 and `--kill-after=2` at 213 so the inner bound (CLI_TIMEOUT+2) always resolves before the outer 120 s.

### F9 (INFO) — `tools/souji-verify.sh` has no internal bound
By design it is a leaf engine; callers must bound it. It has no shell background jobs, but its `git worktree list` process substitutions (510/1044) and `rg` sweeps (224/754) are unbounded children. Standalone invocation can hang. **Smallest fix:** document "must be invoked under `timeout --kill-after`" in the header and in `souji-quarantine.sh`'s engine call (already bounded at 1226); no code change strictly required.

### F10 (INFO) — emitted jj recipe is unbounded
`q_jj_commit_recipe` (`246-251`) emits `jj-lane.sh commit ... --as souji ...` at `549`/`574`; the tool does not execute it, but an operator copying the CMD gets a command with no `timeout`. **Smallest fix:** emit `timeout --kill-after=10 60 jj-lane.sh commit ...` for parity with the 537/540 recipes (note: `--as souji` is the separate R1 finding, not mine).

### F11 (ENV, not a repo defect) — the interactive harness shell shadows GNU `timeout`
`type -a timeout` in this session prints `timeout is a shell builtin` followed by `/usr/bin/timeout`; `enable -a` lists `enable timeout`. A child `bash -c 'type -t timeout; command -v timeout'` prints `file` / `/usr/bin/timeout`, and `BASH_ENV` is empty, so scripts launched normally use GNU 9.12. `r13-quarantine-bounds.sh` resolves via `type -P` (`54-60`), which is builtin-proof. Caveat: sourcing a fixture into an interactive shell, or exporting/loading that builtin via `BASH_ENV`, would silently replace GNU semantics. Recorded so a future run does not attribute a builtin's behavior to coreutils.

## 5. Verification performed (commands and observed output)

```
$ wc -l <seven files>            # 241, 303, 659, 1070, 1842, 1531, 1776
$ sha256sum <seven files>        # hashes in the table above
$ type -a timeout
timeout is a shell builtin
timeout is /usr/bin/timeout
$ /usr/bin/timeout --version | head -1
timeout (GNU coreutils) 9.12
$ /usr/bin/timeout --help        # -f/-k/-p/-s documented; -k = "if COMMAND is still running"
$ bash -n <each of the seven files>
bash-n OK (all seven)
```
Scans used (grep tool, exact named files only): `(?i)\btimeout\b`, `(?i)timeout` (catches `SOUJI_CLI_TIMEOUT`), `timeout` line listings, `<(`, single-ampersand `(^|[^&<>])&([^&<>]|$)`, `\b(wait|disown|coproc|setsid)\b`, `\$!`, `--foreground`. No site in any `timeout` line carries `--foreground`, `-s`, or `--preserve-status`.

## 6. Remaining unknowns / limits

- Static only: no fixture or tool was executed (probe contract; no `ALLOWED-EXEC` item was present). The `-k`-after-leader-exit behavior is **[INFERENCE]** from GNU's documented "if COMMAND is still running" wording and coreutils control flow, not an executed experiment.
- The exact signal disposition of the real `obsidian-cli` is not inspected (it may or may not catch TERM); F4/F8 are structural risks, not measured failures.
- Whether `git cat-file` at `quarantine:350` reads `.git/info/attributes` is not measured; the producer-outside-timeout defect holds regardless (hung object store/promisor is sufficient). The FIFO hazard is directly applicable to `git status --porcelain` at `254` (F6).
- The detached `git maintenance` lifetime in r12 was not measured; the fixture's own header states it detaches, and no code waits for it.
- No claim is made about files outside the seven named paths except the caller/callee lines cited above for interface context.
