STATUS: DONE — C3 `jj_keep_novel` is safe against shell injection, pathspec magic and object corruption, but it fails on three counts: (F1) under `pipefail` a SIGPIPE turns an identical-content predecessor into a false refusal once a path has more than about 600–1000 pushed commits; (F2) the loop is O(K×N) and timed out at 300 s (rc 124, no output) for 50k keep refs × 100k commits; (F3) a keep ref with a broken name, the only keep ref in the repo, hides novel content and the file gets SAFE(pushed). Both fixes are tested on a copy: 45/45 selftest.

Seat: SentinelJjRefs (W2 falsify, sentinel). Surface: C3 (b') `jj_keep_novel` at ddb7347, plus its call site in `try_pushed`. Advisory; L1 integrates.

## Scope and setup
- Code under attack (byte-identical body in all three tools, checked with `diff` of the `git show` extracts → `SAME-vault`, `SAME-quar`):
  - `tools/souji-verify.sh:241-256` (probe :243, pipe :253, caller `try_pushed` :694-731, jj call :718-721, `GIT_LITERAL_PATHSPECS=1` export :528)
  - `tools/souji-vault-verify.sh:433-448` (pipe :445, caller :914)
  - `tools/souji-quarantine.sh:977-992` (pipe :989, caller :1017)
- Only copies of `souji-verify.sh` were executed:
  - `git show ddb7347:tools/souji-verify.sh` → `/var/tmp/souji-r17-SentinelJjRefs/lane/tools/` (sha256 `92743004912a497b5c629515913690bc3096be6f789fc42df46c56d6611bc30f`, 56672 B). The full `tools/` tree came in through `git ls-tree -r` + `git show`, 126 files.
  - Each run was `timeout 300 bash souji-verify.sh --stale-days 1 -- <target>`.
  - Environment: `SHOKUNIN_ROOT`, `SOUJI_LEDGER` (header only), `HOME`, `GIT_CONFIG_GLOBAL` (gc.auto=0), `GIT_CONFIG_NOSYSTEM=1`, and `TMPDIR` all pointed inside the scratch directory.
- Synthetic repos:
  - Built with `git fast-import` plus plumbing. Remote history is `refs/remotes/origin/main` with `origin/HEAD` as a symref; `main` is checked out clean at the tip.
  - Keep commits are children of the tip. Each one touches `f.txt`.
- Scratch was deleted afterwards (`ls` → No such file; `pgrep` → no-procs). Nothing was run against a real directory. No vault/quarantine execution, no `jj`, no installs.
- Tools used: git 2.56.0, shellcheck 0.11.0, bash.

## Findings

### F1 — minor (calibration; fails closed). SIGPIPE false-novel refuses identical-content predecessors on busy paths
- **Where:** `printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0` at verify.sh:253, vault:445, quarantine:989. `set -euo pipefail` is in effect (verify :82, vault :64, quarantine :158).
- **Exploit path:**
  1. Once `known` is larger than the pipe buffer, a match near the start of `known` makes `grep -q` exit early.
  2. `printf` then dies with SIGPIPE (141), and `pipefail` makes the whole pipeline 141.
  3. `|| return 0` reads that as "novel". `rev-list` lists newest first, so the predecessors that fail are the ones carrying a recent pushed blob. That is the common jj `describe`/rebase predecessor, the J2/J4 shape.
- **Evidence:** K=1 keep commit carrying a pushed blob.

  | Remote commits on path (N) | `known` (bytes) | "recent" blob v(N-1) | "oldest" blob v1 |
  |---|---|---|---|
  | 100 | 13 000 | SAFE pushed | SAFE pushed |
  | 300 | 39 000 | SAFE pushed | SAFE pushed |
  | 600 | 78 000 | SAFE pushed | SAFE pushed |
  | 1 000 | 130 000 | **NOT-SAFE `jj-keep-novel`** | SAFE pushed |
  | 5 000 | 650 000 | **NOT-SAFE `jj-keep-novel`** | SAFE pushed |
  | 100 000 | 13 000 000 | **NOT-SAFE `jj-keep-novel`** (0.84 s) | SAFE pushed (1.01 s) |

  Mechanism check (bash, `set -o pipefail`, 3000 × 40-char lines):
  ```
  early-match rc=141 PIPESTATUS=141 0
  late-match rc=0
  small-known rc=0
  ```
- **Impact:** the (b') claim that identical-content predecessors do not refuse is false for any top-level file with somewhere between 600 and 1000 pushed commits touching it (fewer for deeper paths, which add one tree line per level). The fixture never reaches this size because its paths have ≤3 remote commits. The verdict is a false NOT-SAFE, not a data-loss path.
- **Verdict on C3 (b'):** partial.

### F2 — minor (operability; fails closed, with caveats). Per-target cost is O(K×N): 50k keep refs × 100k commits never finishes
- **Where:** the same loop. Every candidate pays one `git rev-parse` fork, then re-`printf`s all of `known` (about 12 MB at N=100k) into a fresh grep.
- **Evidence:** K keep-only commits all carry the oldest pushed blob, so the match sits at the end of `known` and the full scan runs every time. For comparison, `for-each-ref --count=1` takes 0.072 s and `rev-list --glob` 0.189 s at 50k refs (50000 candidates).

  | N | K | Time | rc | Verdict |
  |---|---|---|---|---|
  | 100 000 | 0 (plain repo) | 0.58 s | 0 | SAFE pushed |
  | 100 000 | 1 000 | 51.4 s | 0 | SAFE pushed |
  | 100 000 | 5 000 | 253.9 s | 0 | SAFE pushed |
  | 10 | 50 000 (loose refs) | 71.25 s | 0 | SAFE pushed (≈1.4 ms/fork) |
  | 10 | 50 000 (after `pack-refs --all`) | 70.8 s | 0 | SAFE pushed |
  | 100 000 | 50 000 | **300.0 s** | **124** | **no stdout** (projected ≈51 ms × 50k ≈ 42 min) |

- **Fail-closed or not:**
  - `souji-verify` itself prints nothing on timeout; it is killed, never certifies.
  - quarantine's engine call is bounded and turns this into `receipt-engine-timeout` (`souji-quarantine.sh:1222-1226`, `timeout --kill-after=10 120`), which is fail-closed. Its own direct `jj_keep_novel` call (quarantine :1017) is unbounded.
  - vault-verify's `run_verify` calls the engine with no timeout (`souji-vault-verify.sh:1128-1129`), and its direct call at :914 is also unbounded. So vault/quarantine would hang for tens of minutes per target in this shape. [INFERENCE: identical function body; vault and quarantine were not executed, per the probe rule.]
- **No leftovers:** `pgrep -af souji-r17-SentinelJjRefs` → none-left after the 124 run.
- **Note:** a novel candidate exits on its first iteration, so the worst case is many keep-only, non-novel, old-blob predecessors. That is exactly what a long-lived jj repo accumulates.
- **Verdict:** partial. Safety holds; liveness does not.

### F3 — low (fails open on hostile or corrupt refs). A broken-name keep ref hides novel content behind the probe
- **Where:** probe `[ -n "$(git … for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null)" ] || return 1` (verify :243, vault :435, quarantine :979).
- **Exploit path:**
  1. A loose ref file written directly as `.git/refs/jj/keep/<bad name>` points at a keep-only commit with novel `f.txt`.
  2. `for-each-ref` prints only `warning: ignoring ref with broken name …` to stderr; the code discards it, so stdout is empty.
  3. The probe returns 1 ("not novel") before `rev-list --glob`, which would have failed: rc 128 `fatal: bad object refs/jj/keep/has space`, which would have meant rc 2 and history-unverifiable.
- **Evidence:**

  | Ref name | for-each-ref | rev-list rc | Verdict |
  |---|---|---|---|
  | `has space` | warn, empty | 128 | **SAFE pushed** |
  | `~tilde` | warn, empty | 128 | **SAFE pushed** |
  | `a\x01ctl` | warn, empty | 128 | **SAFE pushed** |
  | `star*` | warn, empty | 128 | **SAFE pushed** |
  | `..dots` | silent | 0, ignored by git | SAFE pushed (invisible to git everywhere) |
  | `x.lock` | silent | 0, ignored by git | SAFE pushed (invisible to git everywhere) |
  | garbage ref content + novel good ref (H7b) | — | — | NOT-SAFE history-unverifiable |
  | garbage ref content alone (H7) | — | — | SAFE pushed (no content behind it) |

- **Impact:** low. jj 0.45.1 never writes such names. The novel commit stays in the object store, because deleting the worktree file does not delete it. Still, this contradicts the comment at verify :75-76: "a git failure takes the existing history-unverifiable path". Once a valid keep ref is also present, the same broken ref fails closed.
- **Verdict:** partial.

### Held (no counterexample)

| Attack | Result |
|---|---|
| **Shell metacharacters in ref names**: `$(touch${IFS}PWN1)`, `` `touch${IFS}PWN2` ``, `a;touch${IFS}PWN3\|b&c`, `x/y/z` (nested), `-n`, `--all`, `'"q`, `%(refname)`, `@` | All NOT-SAFE `jj-keep-novel`, rc 0. No PWN file anywhere. Ref names never reach a shell or an argv option slot; only `--glob=refs/jj/keep/*` and SHAs do. `..dots` and `~tilde` are refused by `update-ref`. |
| **Keep ref → missing commit**: loose (H5), packed-refs (`packed keep -> missing`), and missing plus a good novel ref (H6) | All NOT-SAFE `pushed=history-unverifiable`. `for-each-ref` still lists the ref; `rev-list` fails → rc 2. Fails closed. |
| **Object corruption under a present keep commit** | Blob missing (H8b) → NOT-SAFE `jj-keep-novel` (`rev-parse c:rel` resolves through the tree). Tree missing (H8t) → history-unverifiable. Loose commit missing (H8c) → history-unverifiable. |
| **Remote-side corruption** | Remote tip blob missing → history-unverifiable (`rev-list --objects` fails [INFERENCE: the other try_pushed queries do not read blobs]). Extra remote ref → missing commit → history-unverifiable. |
| **Keep refs at non-commits** | → annotated tag → novel commit (H2): NOT-SAFE `jj-keep-novel` (peeled). → blob (H1), → tag → blob (H3), → tree with novel `f.txt` (H4): SAFE pushed. Non-commits sit outside the (b') contract ("a commit held only by refs/jj/keep") and carry no path history. Informational: they are silently ignored rather than flagged. |
| **Pathspec magic in the target name**: `:x.txt`, `:!x.txt`, `d/:/x.txt`, `:(icase)X.txt`, `[ab].txt` (with novel `a.txt` pushed), `x*.txt` | All NOT-SAFE `jj-keep-novel`. `GIT_LITERAL_PATHSPECS=1` is exported (verify.sh:528, vault :730, quarantine :718). A bare `git rev-list … -- ':x.txt'` without it finds 0 candidates, so the export is load-bearing. |
| **`known`-set injection through a pushed file named `d/z\n<keep-tree-id>`** | `rev-list --objects` cuts names at `\n` (raw output tail shows `<oid> ` lines), so the injected id never appears (`T anywhere: False`). The file target `d/a.txt` is NOT-SAFE `jj-keep-novel`. The directory target `d` is NOT-SAFE `secrets-refusal` (control-char descendant). |
| **100k remote commits touching the path, one novel keep** | NOT-SAFE `jj-keep-novel` in 0.79 s. N=100k with K=0 (plain repo): 0.58 s; the probe gate adds nothing. |
| **Out-of-contract observation** | Novel keep-only content held by `refs/jj/remote-tags/x`, `refs/jj/keepx`, `refs/stash` or `refs/notes/n` → SAFE pushed. The pre-existing r6 check covers only HEAD and `--branches`, and C3 governs only `refs/jj/keep/*`. This is the same in plain repos, so not a C3 regression. Listed for L1's scope ledger. |

## Smallest fix (tested on a copy; same three-line change applies to vault :433-448 and quarantine :977-992)
```diff
-  local repo=$1 rel=$2 c obj known
-  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>/dev/null)" ] || return 1
+  local repo=$1 rel=$2 c obj known objs=""
+  [ -n "$(git -C "$repo" for-each-ref --format='%(refname)' --count=1 refs/jj/keep/ 2>&1)" ] || return 1
 ...
-    printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0
+    objs+=$obj$'\n'
   done <<< "$c"
+  [ -n "$objs" ] || return 1
+  grep -Fxvq -f <(printf '%s\n' "$known") <<< "${objs%$'\n'}" && return 0
   return 1
```
- **What it does:**
  - F1/F2: one `grep -Fxv -f known` over all candidate objects. `grep` reads the pattern file to EOF, so there is no SIGPIPE, and the `<(…)` status is outside `pipefail`. Cost becomes O(N+K) plus K `rev-parse` forks.
  - F3: probe stderr now counts as "present". A broken keep ref proceeds to `rev-list`, which fails → rc 2 → history-unverifiable. Plain repos still produce empty output and stay byte-identical.
- **Test results:** patched copy sha256 `64bbce85dae785ecd0076b0536a53c86940235402468e1e3b5a23a2e1d7ac676`. `bash -n` rc 0. `shellcheck -S warning -f gcc`: 7 lines with an identical findings digest (`e449ae16…`) in the original and the patched copy; all pre-existing, none in lines 240-262.

  | Case | Original | Patched |
  |---|---|---|
  | sp1000/sp5000/sp100000 "recent" | NOT-SAFE (false) | **SAFE pushed** (0.1 / 0.15 / 2.25 s) |
  | sp100000 "oldest" | SAFE | SAFE (2.22 s) |
  | sanity novel / sanity2 identical / sanity3 plain | NOT-SAFE / SAFE / SAFE | NOT-SAFE / SAFE / SAFE (unchanged) |
  | H5, H8b, H8t, H8c, m0 (metachar), `:x.txt` | as above | unchanged |
  | H1, H4 (non-commit keep refs) | SAFE pushed | SAFE pushed |
  | bn0 `has space`, bn3 ctl | SAFE pushed | **NOT-SAFE history-unverifiable** |
  | H7 garbage only | SAFE pushed | NOT-SAFE history-unverifiable (stricter) |
  | bn2 `..dots`, bn4 `x.lock` | SAFE pushed | SAFE pushed (git ignores them) |
  | N=100k K=1000 | 51.4 s | **3.14 s** |
  | N=10 K=50000 | 71.25 s | 45.77 s |
  | N=100k K=50000 | **rc 124** at 300 s | **53.33 s** SAFE pushed |
  | N=100k K=50000 with 1 novel | 1.06 s | 47.93 s, NOT-SAFE `jj-keep-novel` |
  | N=100k K=1 novel | 0.79 s | 2.11 s, NOT-SAFE |

- **Selftest:** `timeout 300 bash <copy> --selftest` → original `selftest: 45 checks, 0 failed` (`ROUND9 16 0`), rc 0, 1.3 s; patched identical, 45/0. This matches L1's verify 45/0.
- **Optional, not in the minimal fix:** one `git cat-file --batch-check` over `c:rel` would remove the remaining K forks (≈1.4 ms each). It is not equivalent as-is: `missing` lines would have to be split into absent path vs absent object, or the H8b blob-missing case turns into a silent pass. Hence not proposed as the smallest change.

## Exact commands (summary; all under the scratch dir, which is now deleted)
- `git -C <lane> show ddb7347:tools/souji-verify.sh | grep -n …` and `sed -n` ranges; `diff` of the function bodies across the three tools; `git show ddb7347:tools/souji-{vault-verify,quarantine}.sh | grep -n …` for call sites and timeouts.
- Builders: `git init -q`, `git fast-import --quiet`, `git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main`, `git reset -q --hard main`, `git hash-object -w`, `read-tree`/`update-index --cacheinfo`/`write-tree`/`commit-tree` under a temp `GIT_INDEX_FILE`, `git update-ref`, direct loose-ref file writes for broken refs, `git pack-refs --all`, loose-object `rm` for corruption. All inside the synthetic repos only.
- Runs: `timeout 300 bash /var/tmp/souji-r17-SentinelJjRefs/{lane,lanefix}/tools/souji-verify.sh --stale-days 1 -- <target>` and `--selftest`; `shellcheck -S warning [-f gcc]`; `bash -n`; `sha256sum`; `rm -rf /var/tmp/souji-r17-SentinelJjRefs`.

## Verdict
- **Safety** (injection, magic pathspecs, missing or corrupt objects, tag peel): holds; fails closed.
- **Calibration** of (b') at real-world history depth: fails (F1).
- **Liveness** at 50k keep refs × 100k commits: fails (F2, rc 124; quarantine's verify call fails closed after 120 s, but vault's verify call and both tools' direct calls are unbounded).
- **Probe completeness** against broken keep ref names: fails open, low (F3).
- **Fix:** the three-line diff above, applied to all three copies.

## Tool installs
None.
