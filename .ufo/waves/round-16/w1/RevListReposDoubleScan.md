# RevListReposDoubleScan — `list_repos` guard vs `census_one` re-guard (r16)

**Artifact:** `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`,
blob sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`,
read via `git show`. `bash -n` on that blob exits 0. Source inspection only: the
fixture, `run-matrix.py`, `--selftest` and shellcheck were **not** run here.

**Verdict:** no defect in the double-scan contract itself — the `CFG_*` globals
are re-derived in the second pass, the second pass is the authoritative one, and
the stderr ordering is sound. One **Low** code finding (F1: one worktree's
`config.worktree` can switch off the scan of its siblings, order-dependently),
one latent trap (T1: `|| true` conflates soft with any nonzero), one peer-claim
correction (P1), and two risks in the *uncommitted* worktree delta (D1, D2).
Findings already owned by siblings are cross-referenced, not duplicated.

## 0. Artifact drift — line numbers are `cbf688a`'s

At review start the worktree byte-matched `cbf688a`. Mid-review the worktree file
became `feba44c7…` (+31/−18 vs `cbf688a`), touching `expand_config_path`,
`status_info_file`, `count_dirty`, `guard_bound_filters`, `run_selftest`. Every
line number below was re-fetched from the revision blob with `git show`, so it is
`cbf688a`'s numbering; after the delta lands, re-anchor by symbol, not by line.
The delta does **not** modify `list_repos`, `census_one`, `guard_git_config`,
`scan_config_file` or `guard_worktree_registrations` bodies (except as noted in §8).

## 1. Consistency of `CFG_*` across the two passes — no defect

The invariant that makes the double scan safe:

- `CFG_SOFT_REASON`, `CFG_STACK`, `CFG_WT_ENABLED` are process globals
  (553-558, 572-573).
- `guard_git_config` (669-682) unconditionally assigns `CFG_WT_ENABLED` at 675
  and clears `CFG_STACK` at 677 before the first scan; `guard_wt_config`
  (654-665) clears `CFG_STACK` again at 662 before its own scan. `scan_config_file`
  (579-652) has three call sites — `guard_git_config` 678 and `guard_wt_config`
  664 (both after a reset) and its own include recursion at 617, which must
  inherit the stack for cycle detection — so a stale stack cannot reach a root
  scan.
- Every soft `return 1` in the guard tree is preceded by `cfg_soft` (556) — there
  is no path that returns 1 without setting a fresh reason, so the reader at
  1088-1089 cannot print a previous repository's reason today.
- `census_one` runs under `row=$(census_one "$repo")` (1227), i.e. in a subshell:
  nothing it computes (including a soft failure of a registered worktree) leaks
  back into the parent or into the next row.
- `list_repos` discards the guard's result (`|| true` at 1176, 1179, 1209).
  Membership is decided only by `.git` shape (1173-1211), so the first pass can
  neither suppress nor authorize a row. Both passes therefore classify every
  enumerated repo identically; the first pass only buys fail-fast ordering.
- Hard refusal ordering is unaffected by the discard because all hard paths call
  `protected_fail`/`exit 2` (e.g. 1090-1092 never runs after a hard refusal), and
  stdout is buffered anyway (1225-1239).

The one place where the "reset at entry" story does **not** hold is F1 below:
`guard_worktree_registrations` passes the live global to each sibling.

**No defect** found in the reader/writer pairing itself.

## 2. Time-of-check gap — r14 vs `cbf688a`

- r14 (`cc21683`) had the same double scan (`list_repos` → `census_one`), but its
  `guard_git_config` (493-520 @cc21683) had **no soft return**: every
  include/filter/hooks/fsmonitor/excludes/attributes/worktreeConfig key was
  `protected_fail` → exit 2. The first pass was therefore a pure early refusal;
  there was no second, softer verdict for the two passes to disagree about.
- `cbf688a` keeps both calls and widens the *content* inspected: `scan_config_file`
  reads each config file with `git config --file` (589 probe, 592 parse), follows
  includes recursively (611-618), and reads `config.worktree` (654-665). The
  check/use gap that matters is unchanged in kind: the authoritative guard runs in
  `census_one` (1087) before `rev-parse` (1104) and before the four measurements
  (1111-1118), and every use-site path re-guards (`status_info_file` 880 re-runs
  `guard_config_path`; `count_dirty` 939 re-checks filter bindings). The
  non-atomicity of "guard" vs "later access" is already declared (doc 115-119).
- Consequence of the soft first pass worth recording as an invariant: a soft
  `guard_git_config` returns **before** `guard_alternates` and
  `guard_worktree_registrations` run in `guard_git_surface`, so those checks are
  skipped for a config-soft repo in *both* passes. That is safe today **only**
  because `census_one` returns at 1087-1092 before any repository-scanning git
  command. A future edit that moves `rev-parse` (1104) or a measurement above the
  guard would silently expose it.
- Net: no new *class* of double-scan TOCTOU. Two new instances inside the widened
  content path — a config-named path that is not a regular file is never
  kind-checked (owned by `RevBoundFilters.md` §FIFO; not repeated here), and the
  guard's own double read (589/592, residual §7).

## 3. Ordering of stderr diagnostics — no defect

- Enumeration-phase hard diagnostics (`protected_fail`, which exits) precede all
  stdout by construction.
- Rows are buffered (1225-1239) and printed only after the loop, so a mid-run exit
  2 yields an empty stdout (atomic), and the header stays the first stdout line on
  success.
- A soft-failed repository prints exactly one
  `souji-census: config-unsupported: <reason> (<repo>)` from `census_one`
  (1088-1089). `list_repos`'s first pass is silent on soft failure, so there is no
  duplicate line.
- `status-skipped` is emitted by `count_dirty` (940-941) per worktree, in REPOS
  order (1215).
- Consumption caveat, not a tool defect: because rows are buffered while stderr
  streams, a caller that merges streams (`2>&1`) gets diagnostics before the
  header, which `load_census` rejects (1275, 1300). `--compare` avoids this by
  redirecting `emit_census` into a temp file (1334-1337).

The only *missing* diagnostic in the changed behavior is the config-soft
registered-worktree path, already reported by `RevR14NamespaceRetention.md` §F4
(silently folded into `wt-dirty`, 1068-1075). Not re-reported; it is the reason
"no ordering defect" is scoped to the lines this review owns.

## 4. F1 — Low — `CFG_WT_ENABLED` is clobbered across sibling worktrees (order-dependent)

`guard_worktree_registrations` (715-762) passes the **live** global to each
registration:

```
741:            guard_git_config "$admin" "$CFG_WT_ENABLED" || return 1
```

`guard_git_config` assigns that argument at 675, and then
`guard_wt_config` → `scan_config_file` may reassign it at 638 when the scanned
file contains `[extensions] worktreeConfig`. So for registrations `wt1`, `wt2` in
glob order, if `wt1/config.worktree` carries `worktreeConfig = false`, then `wt2`
is called with `0` at 741 and `guard_wt_config` early-returns at 656 — **`wt2`'s
`config.worktree` is never opened in this traversal**. The traversal's coverage
therefore depends on `worktrees/*` sort order, and the same file is (correctly)
scanned later by the `-f` branch of `guard_git_surface` (829) before
`count_dirty "$cpath"` (1072). So there is **no current bypass** — the status
site re-guards — but the first traversal is order-dependent and would become a
hole if the `-f` re-scan were ever dropped.

`[INFERENCE]` Git reads `extensions.worktreeConfig` from the common config and
uses it to decide whether `config.worktree` is loaded at all; a value inside
`config.worktree` cannot redefine the gate. The scanner honors it in any file,
which is the divergence behind the clobber.

Minimal patch (order independence, 3 lines):

```diff
-  local dir=$1 entry reg target wt admin common c
+  local dir=$1 entry reg target wt admin common c wtflag
+  wtflag=$CFG_WT_ENABLED
@@
-            guard_git_config "$admin" "$CFG_WT_ENABLED" || return 1
+            guard_git_config "$admin" "$wtflag" || return 1
```

Deeper patch (match git; prevents the clobber at the source, 2 lines at 633-634):

```diff
       extensions:worktreeconfig)
+        # git reads this only from the common config; ignore it in config.worktree.
+        case "$cfg" in */config.worktree) continue ;; esac
         if [ "$bare" = 1 ]; then CFG_WT_ENABLED=1; continue; fi
```

Either alone removes the order dependence; both together match git's semantics.
No fixture/selftest change: `tests/fixtures/r15-census-config.py:620-626` has a
benign `worktreeConfig = true` common config and benign per-worktree
`core.worktree` values, and the selftest's `wt1` admin has no `config.worktree`
(`tools/souji-census.sh:1481-1490`).

## 5. T1 — latent trap — `|| true` maps "soft" and "any nonzero" to the same thing

Three call sites discard the guard's status: 1176, 1179, 1209. Today
`guard_git_surface` either returns 0/1 or calls `exit 2` (no `return 2` exists),
so the discard is correct. But `census_one`'s companion form
`if ! guard_git_surface "$repo"; then` (1087) has the same shape: any future
`return 2` (the natural refactor, since the caller already special-cases rc 2 at
1231) would be read as "soft" and emit an `error` row instead of the whole-run
refusal. This is exactly the misclassification r14 was harmed by.

No current defect; if hardened, use:

```diff
-      guard_git_surface "$d" || true
+      guard_git_surface "$d" || { rc=$?; [ "$rc" = 1 ] || exit "$rc"; }
```

and the `if guard_git_surface "$repo"; then :; else rc=$?; ...` form in
`census_one`. Related, also latent: in every call form (1176, 1179, 1209, 1087)
`set -e` is disabled for the duration of the function body (bash ignores `-e` in
`&&`/`||` and `if` conditions), whereas r14's bare `guard_git_surface "$repo"` in
`census_one` was `set -e`-active. No unguarded failing command exists in the
guard tree today, so this is a note on the refactor surface, not a bug.

## 6. P1 — peer-claim correction — `status_info_file`'s `~user` exit-2 path is unreachable

`DraftOperatorQuestion.md:31` proposes that `core.excludesFile` /
`core.attributesFile = ~user/...` reaches `status_info_file` 878-879 and turns
into a whole-run exit 2 ("only the include path degrades"). That is not
reachable: `scan_config_file` handles the same keys at 619-625, calls
`expand_config_path` at 621, and on failure does `cfg_soft` + `return 1` at 622,
so the repo degrades to the `error` row at 1087-1092 **before** `count_dirty`
(1115) can call `status_info_file`. The scanner reads the same effective config
set that `git config --get` reads (`$GIT_DIR/config`, its includes, and
`config.worktree` when enabled), so there is no source that reaches 878 with an
unmodellable value. Do not integrate that item without a repro. (The uncommitted
delta also reroutes 878-879 to rc 3 → `unverifiable`, which would make the point
moot even if it were reachable.)

## 7. Residual risk / verification gaps

- The claimed 20/20, 12/12, 38/38 and the parse-clean baseline were **not**
  re-run here; only `bash -n` on the blob (exit 0) was checked.
- Double-scan cost: the guard runs `2 + n` times per repo (n = registered
  worktrees), and each `guard_git_surface` re-walks all n admins through
  `guard_worktree_registrations` → O(n²) config scans; each config file is parsed
  twice (589/592). The O(n²) shape is inherited from r14; r16 multiplies its
  constant. If cost matters, shrink the *first* pass to the cheap `.git`-shape
  checks only — do **not** cache its verdict into `census_one`, which would widen
  the authoritative check/use gap.
- `scan_config_file`'s parse read (592) discards stderr and `mapfile` always
  returns 0, so a second read that fails after the 589 probe sees an empty file
  and the guard accepts it. Impact is bounded (git reads the same file later and
  fails → error/status-unverifiable), and the class is covered by the declared
  residual (115-119). Worth a comment at 589-592, not a patch.
- Pre-existing doc/behavior mismatch, outside this round's delta: with
  `--include-root`, a root whose `.git` is a *file* is emitted as a row
  (1175-1177), although the usage says a row is emitted "when it is a main repo"
  (20-21) and linked worktrees are not rows.
- Dead code in `census_one`: the `-L "$repo/.git"` branch (1093-1096) is
  unreachable because `list_repos` (1200-1203) never adds such a repo; the
  `not-a-repo` branch (1097-1103) is reachable only through a
  `.git`-removed-between-passes race. Harmless; documents an old assumption.
- `core.worktree` is accepted when boundary-clean (626-631, doc 90-92). For a
  non-bare repo whose value points elsewhere, `dirty` comes from
  `git -C repo status` (which follows `core.worktree`) while `mtime_iso` /
  `scratch_bytes` come from the repo directory (983-1035), i.e. one row describes
  two trees. Designed acceptance; should be stated in the residual paragraph.
- `CFG_SOFT_REASON` is never cleared (553-558; `guard_git_config` resets only
  `CFG_WT_ENABLED`/`CFG_STACK` at 675-677). Accurate today because every soft
  return sets it and the reader is the immediate caller; a one-line
  `CFG_SOFT_REASON=""` next to 675 would make the reader provably local.
- `tests/fixtures/r15-census-config.py:954-967` allows
  `config-worktree-protected`, which the script never emits (it emits
  `include-protected`, `core-worktree-protected`, `git-metadata-symlink`,
  `git-config-unsupported`). Permissive, but a wrong reason there would not be
  caught.
- C1's wording ("only a protected-namespace reach keeps whole-run exit 2") is
  already contradicted in this wave by `DraftOperatorQuestion.md:26` and
  `ScoutIncludeIfConditions.md:104` (non-protected exit-2 reasons at 426,
  459/464, 487-516, 658/673, 1255). Not re-litigated; one doc nit belongs with
  it: `guard_git_surface`'s header (765) still says "exits 2", although it now
  returns 1 for a soft config, and the Exit-codes block (121-124) omits those
  non-protected refusals.
- Overlap to dedupe: the FIFO/non-regular attrs/excludes hole is covered by
  `RevBoundFilters.md` (104-107); the silent `wt-dirty` fold by
  `RevR14NamespaceRetention.md` §F4; the set-but-empty excludes question by
  `SrcGitignoreXdg.md` B1/U1. The worktree-config flow is also the slice of the
  running `RevWorktreeConfigFlow` seat; F1 should be merged there, not counted
  twice.

## 8. Uncommitted worktree delta — two risks (informational, not defects of `cbf688a`)

1. **D1 — `wait` on a process substitution.** The delta adds, in
   `guard_bound_filters`, `pid=$!` immediately after
   `mapfile … < <(set -o pipefail; git ls-files … | git check-attr …)` and then
   `wait "$pid" || return 1` (fail-closed). `[INFERENCE]` Bash does not document
   `$!` as being set by a process substitution; if it is empty under the target
   bash, `wait ""` fails and **every repo that defines any `filter.*` driver**
   becomes `status-unverifiable`, regressing fixture case 13 (`r-filter-unused`,
   `r-filter-crypt` expect `clean`). The recorded 38/38 was measured at
   `cbf688a` with the old `|| true` code, so it does not cover this path. Re-run
   the fixture after the delta, or capture `ls-files` into a `mktemp` file and
   check its status directly.
2. **D2 — `:(optional)` stripping.** The delta makes `expand_config_path` strip a
   leading `:(optional)`. `[INFERENCE]` Git expands config pathnames through
   `interpolate_path`, which handles `~/` and `%(prefix)` only, not pathspec
   magic; stripping the prefix would make the census read a file git would not.
   Confirm against git before landing.

## 9. Summary

| id | severity | subject | status |
|---|---|---|---|
| F1 | Low | `CFG_WT_ENABLED` clobbered across sibling worktrees (741) | real, order-dependent, latent only today |
| T1 | note | `|| true` conflates soft with any nonzero (1176/1179/1209, 1087) | latent trap |
| P1 | note | `~user` excludes → exit 2 is unreachable (619-625 vs 876-883) | peer claim should not be integrated |
| D1/D2 | note | pending delta: `$!` wait, `:(optional)` strip | verify before landing |

No defect found in (1) `CFG_*` consistency for the two-pass contract, (2) any new
class of check/use gap introduced by the double scan, or (3) stderr diagnostic
ordering. F1 is the only finding in this seat's own slice.

STATUS: no known failing check; source review only — `bash -n` on the blob exits 0, and the census/fixture/selftest were not executed (seat contract).

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat --format='%H %s' -- tools/souji-census.sh tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum && sha256sum tools/souji-census.sh && git rev-parse --short HEAD && git status --porcelain -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E '^(cfg_|CFG_|[a-z_]+\(\)|  *(if|while|done|fi)\b)' | head -100
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^[A-Za-z_][A-Za-z0-9_]*\(\)' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CFG_\|cfg_' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423^:tools/souji-census.sh | grep -n -E 'list_repos|guard_git_surface|census_one' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -6 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 && echo '--- parent list_repos ---' && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423^:tools/souji-census.sh | sed -n '1310,1400p' | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '=== cc21683 (r14) functions ===' && git show cc21683:tools/souji-census.sh | grep -n -E '^(list_repos|census_one|guard_git_surface|guard_git_config)\(\)|guard_git_surface .*\|\| true|row=\$\(census_one' && echo '=== r14 list_repos body ===' && git show cc21683:tools/souji-census.sh | awk '/^list_repos\(\)/{f=1} f{printf "%d: %s\n", NR, $0} f&&/^}/{exit}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423^ cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n -E '^[-+].*(list_repos|guard_git_surface|census_one|CFG_WT|row=\$|guard_git_config)' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | awk 'NR>=480 && NR<=520{printf "%d: %s\n", NR, $0}' && echo '=== r14 worktree_extra_flags guard call ===' && git show cc21683:tools/souji-census.sh | grep -n -B3 -A6 'guard_git_surface "$cpath"'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1000 && NR<=1050{printf "%d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=614 && NR<=636{printf "%d: %s\n", NR, $0} NR>=876 && NR<=936{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1200 && NR<=1260{printf "%d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1039 && NR<=1100{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1100 && NR<=1245{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=100 && NR<=115{printf "%d: %s\n", NR, $0} NR>=548 && NR<=600{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=664 && NR<=690{printf "%d: %s\n", NR, $0} NR>=905 && NR<=934{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=115 && NR<=132{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'wt-dirty\|wt-absent\|worktreeConfig\|config.worktree' tests/fixtures/r15-census-config.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=598 && NR<=640{printf "%d: %s\n", NR, $0} NR>=1160 && NR<=1200{printf "%d: %s\n", NR, $0}' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423^ cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n -E '^\+.*\|\| true|^-.*guard_git_surface' | head -20 && echo '=== b410186 guard_git_config ===' && git show b410186:tools/souji-census.sh | grep -n -A12 '^guard_git_config()'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'CLEAN = \|def positive_problems' -A12 tests/fixtures/r15-census-config.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n -B6 -A8 'cpath' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | wc -l; git show b410186:tools/souji-census.sh | grep -n 'guard_git_config\|list_repos\|cpath' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=88 && NR<=100{printf "%d: %s\n", NR, $0} NR>=760 && NR<=770{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=872 && NR<=960{printf "%d: %s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | grep -n -E '^[-+].*(status_info_file|guard_bound_filters|pid|wait|CFG_SOFT_REASON|guard_git_surface "\$cpath"|census_one)' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum && sha256sum tools/souji-census.sh && git rev-parse --short HEAD && git status --porcelain -- tools/souji-census.sh && git log --oneline -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E 'if ! guard_git_surface|CFG_SOFT_REASON|mapfile -d .. -t recs < <\(git config --file|guard_config_path git-config-unsupported|row=\$\(census_one|guard_git_surface "\$(d|root)" \|\| true|local wt=\$1 key|^guard_bound_filters|^status_info_file|saw_dirty=1|wt-dirty|status-unverifiable|^  pid=|wait '
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=934 && NR<=956{printf "%d: %s\n", NR, $0} NR>=1568 && NR<=1595{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=40 && NR<=62{printf "%d: %s\n", NR, $0} NR>=160 && NR<=180{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=1470 && NR<=1520{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E '^guard_wt_config|^guard_git_config|^scan_config_file|CFG_STACK=\(\)|^load_census|header mismatch|special-path|^emit_compare|CENSUS_TMP=.*mktemp|^  names=\('
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'config-worktree-protected\|git-metadata-symlink\|git-config-unsupported\|core-worktree-protected\|include-protected' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cc21683:tools/souji-census.sh | awk 'NR>=818 && NR<=840{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -o 'protected_fail "[a-z-]*"\|cfg_soft "[a-z-]*"' tools/souji-census.sh | sort -t: -k2 | uniq -c -f1 | sort -k2 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n -iE 'fifo|non-regular|nonregular|wt-dirty|CFG_SOFT_REASON|double scan|two passes|list_repos' RevBoundFilters.md RevScanParse.md RevR14NamespaceRetention.md RevIncludeResolve.md 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -rn -iE ':\(optional\)|pid=\$!|wait "\$pid"|sticky|set-but-empty|empty value|no git command runs|exit 2' --include='*.md' . | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=715 && NR<=762{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | bash -n; echo "bash-n-exit=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=14 && NR<=24{printf "%d: %s\n", NR, $0} NR>=800 && NR<=840{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '831\|25-27\|1334-1337\|765-839' .ufo/waves/round-16/w1/RevListReposDoubleScan.md && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=1328 && NR<=1340{printf "%d: %s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## \|^STATUS:\|^```' .ufo/waves/round-16/w1/RevListReposDoubleScan.md | tail -20 && wc -l .ufo/waves/round-16/w1/RevListReposDoubleScan.md
```

Note: the `grep -rn` line was scoped to the w1 report directory only (to check
sibling coverage), not to the lane root or fleet root. All file-content reads
outside `bash` used the `read` tool on the exact paths named above.
