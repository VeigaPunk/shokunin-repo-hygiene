# RevCensusScanFinal — source review: `scan_config_file` / `guard_config_path` / `expand_config_path`

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae` (pushed later by L1).
- Target: `tools/souji-census.sh`, sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, 1877 lines; unchanged since `0a70bef`.
- Functions in scope: `scan_config_file` (608-692), `guard_config_path` (542-559), `expand_config_path` (565-573); plus every caller of those three (`guard_wt_config` 696-711, `guard_git_config` 715-733, `status_info_file` 942-978) and the guard helpers they depend on (`lexical_abs` 213, `protected_component_reason` 318, `protected_reason_inside` 346, `protected_reason_input` 362, `resolve_guarded` 381, `cfg_soft` 581, `guard_config_file_kind` 587).
- Method: static source review only. This item carries no `ALLOWED-EXEC`, so the census was not run, not even a copy; no `/var/tmp` directory was created. Git behaviour claims are checked against `git v2.56.0` source and `git-config(1)` for 2.56.0 (the host has no `man5/git-config.5.gz` installed — verified).
- Overlap: `RevCensusSurfaceFinal.md` (same wave) reviews the surrounding git-surface guards. I independently confirm its F3 (relative excludes/attributes base, `scan_config_file:652`) and F7 (a protected excludes/attributes value reported as `git-config-unsupported`, `:655`/`:948`) and do **not** re-report them as new. Its F1 (symlinked `config`/`config.worktree`), F2 (linked admin's own `extensions.worktreeConfig`), F4 (empty `gitdir:`), F5 (unchecked nlink on pointer files), F6 (duplicate passes) are out of this item's scope; S5 below extends F5's *policy* consequence, and S1 below is the correctness half of F6's duplicate pass, which F6 does not cover.

Axis judged: operability (a census run that loses rows, refuses the fleet, or reports a measurement that was never taken).

## Findings

| id | severity | where | verdict |
|---|---|---|---|
| S1 | medium | `scan_config_file:618-621` | **fails** — the read the guard iterates is a process substitution whose producer status is never checked; a failed second `git config` is scanned as if the config had no `include`, and the census then runs `git status` on the config as it stands |
| S2 | low | `guard_config_path:547-549` (with `362-379`, `381-395`) | **partial** — the lexical `..` pre-check contradicts the function's own `allow-dotdot=1` contract and can refuse a benign target whose physical resolution never reaches the store |
| S3 | low (diagnostics) | `guard_config_path:555-558` caller `:948` | **holds with note** — confirmed identical to `RevCensusSurfaceFinal` F7; listed here only to close it against *this* function's contract |
| S4 | info | `scan_config_file:634-651` | **holds as designed** — `includeIf` conditions are not evaluated; documented at header 89-90 and pinned by the fixture, but see the contract caveat |
| S5 | medium (adjacent) | `guard_git_files:526,529,532` via `830-831/848-849/872-873` | **fails** the "only a protected reach exits 2 whole-run" claim for benign hardlinked metadata (e.g. a `cp -al` / `rsync --link-dest` tree) |
| S6 | low (adjacent) | `emit_compare:1465` | **fails** — `--compare` prints numeric deltas against `error`-row placeholders, inventing measurements |

Everything else attacked below is explicitly cleared.

---

## S1 — `scan_config_file:618-621`: the record list is read through an unchecked process substitution (fail-open window)

Evidence (HEAD):

```
618  if ! git config --file "$cfg" --no-includes --list -z >/dev/null 2>&1; then
619    cfg_soft "git-config-unparsed"; return 1
620  fi
621  mapfile -d '' -t recs < <(git config --file "$cfg" --no-includes --list -z 2>/dev/null)
```

`mapfile`'s exit status describes the array assignment, never the producer: with `< <(cmd)` the producer's status is discarded and its stderr is already `2>/dev/null`. The only parse check is the *separate* invocation at 618, on a *previous* read of the file. So the evaluation that the guard actually iterates (`recs`, line 623 onward) can be empty or truncated while `soft` stays 0.

Concrete failure mode (constructed, not executed): the call at 618 succeeds on a parseable config; at 621 the path is transiently unreadable — removed, replaced by a directory, permissions flipped, or an editor's non-atomic write — so `git config` exits nonzero, `recs` is empty, and `soft` stays 0. The guard then evaluates exactly as if the config had no `include` keys, admits the repo, and `count_dirty` (1021-1047) runs `git status`, which re-reads whatever is on disk *then*. If the hostile config is back by that point (a tool that rewrites `.git/config` by unlink+create, or a repo being restored from a backup), the store include is followed with no guard at all.

Direction matters: a *successful* call at 621 always reads the current bytes, so a single rewrite benign→hostile before 621 is caught by the guard. The hole is the unobserved *failure* of the authoritative read. A change after 621 is a separate, inherent pre-flight window that no guard in this shape can close; the patch below does not claim to close it.

It is a correctness hole in the guard's own contract ("the file is checked before it is read"): the check and the read are two different opens, and the read's status is discarded, so a failed read is indistinguishable from a clean config. `RevCensusSurfaceFinal` F6 counts the duplicate pass as cost; it does not note that the authoritative read is unchecked.

Smallest fix — one read, status checked, no second parser pass. `cleanup_census_tmp` (189-193) already exists and `CENSUS_TMP` is removed on `EXIT`; extend it and install the trap at startup so a `protected_fail` `exit 2` mid-scan cannot leak the file:

```diff
@@ cleanup_census_tmp
 cleanup_census_tmp() {
-  if [ -n "${CENSUS_TMP:-}" ]; then
-    rm -f -- "$CENSUS_TMP"
-  fi
+  if [ -n "${CENSUS_TMP:-}" ]; then rm -f -- "$CENSUS_TMP"; fi
+  if [ -n "${CFG_TMP:-}" ]; then rm -f -- "$CFG_TMP"; fi
 }
@@ after cleanup_census_tmp (189-193) — the function must exist before the trap can fire
+trap cleanup_census_tmp EXIT
+CFG_TMP=""
@@ scan_config_file
-  if ! git config --file "$cfg" --no-includes --list -z >/dev/null 2>&1; then
-    cfg_soft "git-config-unparsed"; return 1
-  fi
-  mapfile -d '' -t recs < <(git config --file "$cfg" --no-includes --list -z 2>/dev/null)
+  # One read whose status is checked: a process substitution cannot report the
+  # producer's status, and a second read would race a concurrent rewrite.
+  CFG_TMP=$(mktemp /var/tmp/souji-cfg.XXXXXX) || {
+    CFG_TMP=""; cfg_soft "git-config-unparsed"; return 1
+  }
+  if ! git config --file "$cfg" --no-includes --list -z >"$CFG_TMP" 2>/dev/null; then
+    rm -f -- "$CFG_TMP"; CFG_TMP=""
+    cfg_soft "git-config-unparsed"; return 1
+  fi
+  mapfile -d '' -t recs < "$CFG_TMP"
+  rm -f -- "$CFG_TMP"; CFG_TMP=""
```

The `tr -d '\000' | cmp` NUL check at 615 stays as-is (it also serves as the pre-open readability check). Cost is unchanged (one `git` + one `mktemp` per file instead of two `git`).

## S2 — `guard_config_path:547-549`: the lexical `..` pre-check can refuse a path the physical walk would admit

Evidence:

```
542  guard_config_path() { # $1 reason, $2 gitdir, $3 cfg, $4 absolute raw path
...
547    if protected_reason_input "$(lexical_abs "$raw")" >/dev/null; then
548      protected_fail "$reason" "$dir" "$cfg"
549    fi
550    if out=$(resolve_guarded "$raw" 1 1 2>&1); then
```

`lexical_abs` (213-230) collapses `..` textually; `resolve_guarded` is called with `allow-dotdot=1` precisely so config-named paths may contain `..` and are folded *physically* (381-455). The pre-check runs first and defeats that: a `..` that crosses a symlink is folded the wrong way and can land lexically on a protected root (or on an ancestor of one) while the real path does not.

Constructed counterexample (default root, ancestor form): `HOME=/home/u` (store root `/home/u/.omp/agent`), repo gitdir `/home/u/work/r/.git`, `.git/sl` a symlink to `/tmp/deep/deeper`, and `[include] path = sl/../../../..`. Physical walk: `/tmp/deep/deeper` → `..` → `/tmp/deep` → `..` → `/tmp` → `..` → `/` → `..` → `/` (not protected, admitted). Lexical: `sl` is removed by the first `..`, three more reach `/home/u` → `/home/u` is an *ancestor* of `/home/u/.omp/agent`, so `protected_reason_input` (239-243, 368-373) matches → the whole run exits 2 before the walk is attempted. Nothing protected would have been read.

Descendant form needs a relocated root, because `$HOME/.omp/agent` is otherwise protected by name anywhere: with `PI_CODING_AGENT_DIR=/home/u/store` (seeded at 274-283) and `path = sl/../../../../store/x`, lexical resolves to `/home/u/store/x` (under the root, refused) while physical resolves to `/.store/x` (no `.omp/agent` pair, admitted).

The class is narrow (a `..` sequence after a symlink, positioned so the lexical collapse lands exactly on a root or an ancestor) and over-refusal only, but it is the *same* input class the function's `allow-dotdot=1` says it supports, and it is the one whole-run exit inside these three functions that is not a protected reach.

Smallest fix — let the walk decide, and apply the ancestor/descendant rule to the *resolved* path only (the walk's own pre-lstat suffix check at 425-429 still refuses store descent before any stat, and the walk's `..` branch at 407-412 still re-checks each popped prefix):

```diff
-  if protected_reason_input "$(lexical_abs "$raw")" >/dev/null; then
-    protected_fail "$reason" "$dir" "$cfg"
-  fi
-  if out=$(resolve_guarded "$raw" 1 1 2>&1); then
+  if out=$(resolve_guarded "$raw" 1 0 2>&1); then
+    # `..` is folded physically by the walk; judge the resolved path, not a
+    # lexical collapse that ignores symlinks.
+    if protected_reason_input "$(lexical_abs "$out")" >/dev/null; then
+      protected_fail "$reason" "$dir" "$cfg"
+    fi
     printf '%s' "$out"
     return 0
   fi
```

`final=0` drops both of `resolve_guarded`'s lexical checks (391-395 pre-walk and 447-450 post-walk); the added post-check replaces the post-walk one on the physical result, which is the stronger form. Protection is otherwise unchanged: component/root refusal happens inside the walk before each `lstat`, and the ancestor rule (`path_overlaps`, 239-243) still applies.

## S3 — `guard_config_path:555-558`: refusal reasons are complete; the caller's reason vocabulary is not

Positive half (holds, and closes a question `RevCensusSurfaceFinal` left open): the three reasons matched at 555 are **exactly** the reasons a protected hit can carry. `protected_component_reason` (318-343) prints `credential-store` (`*.omp` + `agent`), `operator-sweep` (`census/operator-sweep-*`), `operator-runtime` (`.ufo/state`, `.ufo/watchdog.log`); `protected_reason_inside` (346-360) adds only `credential-store` for root containment; `protected_reason_input` (362-379) is the union. Every other `protected_fail` inside `resolve_guarded` is a resolution failure — `ambiguous-path` (386, 396, 436), `unresolved-path` (432), `symlink-loop` (442) — and correctly falls through to `return 3` (558), which both callers degrade (`cfg_soft` at 645, 656, 664; `return 3` at 949). Because `protected_fail` always prints `path-protected: <reason> (` (200-206), the trailing-space patterns at 555 cannot miss a protected hit; there is no silent downgrade of a protected reach to a soft row.

Negative half is `RevCensusSurfaceFinal` F7 and is not restated. One addition relevant to *this* function's contract: `guard_config_path`'s `$1` is used both as the *refusal* reason (548, 556) and as the *degrade* reason at the two `>/dev/null` call sites (655, 663). Callers must therefore never pass a word from the soft vocabulary (`git-config-unsupported`) when they mean a protected refusal; 948 does. Fix belongs at 948 (`core-excludes-protected` / `core-attributes-protected`), not in this function.

## S4 — `scan_config_file:634-651`: `includeIf` over-approximation is documented; one contract caveat

The branch follows `include.path` **and** every `includeIf.<cond>.path`, whatever the condition, and folds nested relative paths against the spelled directory (`${spelled%/*}`, 640) — which matches git: `handle_path_include` resolves against `kvi->filename` (`config.c:164-175`) and only strips nothing from the value (`interpolate_path(path, 0)`, `config.c:153`). The over-approximation is documented at header 89-90 ("every target is guarded whatever its condition"), in the fixture contract (`tests/fixtures/r15-census-config.py:31-36`) and pinned by fixture cases `r-incif-store`/`r-incif-hc-store`/`r-incif-unknown` (475-486). Verdict: holds as designed; `hasconfig:` genuinely does read the included file in git (two-pass, `config.c:439-441` plus the `unconditional_remote_url` re-parse), so the safety argument there is sound.

Caveat for the wave claim, not the code: "only a protected path reach exits 2 whole-run" is false for a target behind a `gitdir:`/`onbranch:`/unknown condition that git would never honour — the census refuses the fleet for a file git never opens. The fixture deliberately pins that outcome, so the fix is to the claim's wording (or to the fixture, if the intent were narrower), not a code change now. No patch proposed.

## S5 — adjacent (extends `RevCensusSurfaceFinal` F5): benign hardlinked metadata aborts the whole run

`guard_git_files:519-535` refuses `nlink > 1` for `config`, `HEAD`, `index`, `packed-refs`, `commondir`, `info/exclude`, `info/attributes`, `objects/info/alternates` with `protected_fail` → `exit 2` (529), and the same for non-regular (532) and unreadable-link-count (526). Those calls are reached with `guard_git_files "$dir" || exit 2` at 831, 849, 873. Nothing protected is involved.

Counterexample (constructed, not executed): `cp -al` of a fleet tree, or an `rsync --link-dest` backup restored in place, gives every one of those files `nlink = 2`. The first repo walked exits the whole census with `souji-census: path-protected: git-metadata-hardlink (...)`: zero rows for every repo, and the finding name claims a protected path. This is read-only-safe for the commands the census runs (`--no-optional-locks` suppresses the index write; `config`/`HEAD`/`packed-refs` are only read), so the refusal is a protection policy for hardlink *aliasing* into the store, not a measurement hazard.

Smallest fix — keep the alias protection, drop the fleet abort; the file already soft-degrades hardlinked *includes* (`guard_config_file_kind:594`, `cfg_soft "git-include-hardlink"`), so this is the existing precedent:

```diff
@@ guard_git_files
       if [ "$nlink" -gt 1 ]; then
-        protected_fail "git-metadata-hardlink" "$dir" "$path"
+        cfg_soft "git-metadata-hardlink"; return 1
       fi
     elif [ -e "$path" ] && [ ! -d "$path" ]; then
-      protected_fail "git-metadata-nonregular" "$dir" "$path"
+      cfg_soft "git-metadata-nonregular"; return 1
     fi
   done
@@ (same shape for "git-metadata-unavailable" at 526, keeping the `stat` failure non-fatal)
@@ call sites 831/849/873
-    guard_git_files "$dir" || exit 2
+    guard_git_files "$dir" || soft=1
```

`RevCensusSurfaceFinal` F5 adds nlink checks for the two pointer files; that patch already uses `cfg_soft` for exactly this reason and should stay soft, or it multiplies this abort class.

## S6 — adjacent: `--compare` invents measurements for `error` rows

`census_one:1177-1180` emits an `error` row as `repo\t0\t0\t0\t0\t\terror` (placeholders). `emit_compare:1459-1472` diffs every field and, at 1465, computes a numeric delta for `worktrees|unpushed|dirty|scratch_bytes`. So a repo that degrades (e.g. S1's class, S5's class, or any `cfg_soft`) between two census runs yields `dirty 3 0 -3`, `unpushed 2 0 -2`, plus `verdict_flags … changed`: the diff asserts measurements that were never taken, which is exactly what the `error` row's own contract (header 97-99) promises it will not do.

Smallest fix at 1465 (read field 6 = `verdict_flags` of each side and label the delta):

```diff
-      case "$name" in
-        worktrees|unpushed|dirty|scratch_bytes) chg=$(numeric_change "$before_v" "$after_v") ;;
+      case "$name" in
+        worktrees|unpushed|dirty|scratch_bytes)
+          case "$(field_at "$rest_b" 6)$(field_at "$rest_a" 6)" in
+            *error*) chg=unmeasured ;;
+            *) chg=$(numeric_change "$before_v" "$after_v") ;;
+          esac ;;
```

(`unmeasured` joins the existing non-numeric change vocabulary `added`/`removed`/`changed`/`non-numeric`; consumers that switch on `+N|-N|0` need the one new word, which is the point.)

---

## Explicitly cleared (attacked, no finding)

- **Reason matching cannot misclassify.** All three protected reasons reach 555; `protected_fail` always emits `path-protected: <reason> (` so the trailing-space alternation matches; a protected hit never degrades to 3 and a resolution failure never exits 2 (S3).
- **Depth limit matches git exactly.** Census refuses `depth > 10` with top = 0 (611); git increments before comparing — `if (++inc->depth > MAX_INCLUDE_DEPTH)` at `config.c:178` with `MAX_INCLUDE_DEPTH 10` (135). Both allow ten nested includes and die on the eleventh. (`RevCensusSurfaceFinal` residual risk left this unsettled.)
- **`:(optional)` is correctly *not* stripped for `include.path`.** Git strips it only in `git_config_pathname` (`config.c:1327`); `handle_path_include` calls `interpolate_path(path, 0)` directly (`config.c:153`), so `:(optional)~/.omp/agent/x` is a literal relative path for git exactly as the census treats it (comment 562-564). No hole, and no missing strip.
- **`%(`/`~user` degrade direction is safe.** `expand_config_path:569` returns 1 for `~user/` and `%(prefix)/`; the repo becomes a per-repo `error` row and no git command runs, so a store reachable only through those forms is never opened. `~/` expansion (568) is `$HOME`-based, matching `interpolate_path`'s `$HOME` use; an unset `HOME` degrades instead of guessing.
- **Relative include base is git's spelling rule.** `spelled` (604-607, 640) is threaded through recursion so nested relative includes resolve against the spelled directory, not the resolved one — identical to git's `kvi->filename`-based base (`config.c:164-175`).
- **`..` is folded physically in the walk.** Symlink detection precedes accumulation (415-437); a relative link target is folded against the link's own directory (`acc` is the parent at that point); each popped prefix is re-checked (407-412); the remaining-suffix check (425-429) refuses store descent before `lstat` of the component below it. The only `..` defect found is the lexical pre-check (S2).
- **`core.worktree` base is correct.** `scan_config_file:660` expands against `$dir`; `git-config` 2.56.0 documents `.git`-relative (`docs` 2849-2851). `core.excludesFile`/`core.attributesFile` have no such rule — git opens them at status time relative to the process cwd, which `status_info_file:947` models with `$wt` and `:652` does not (confirmed `RevCensusSurfaceFinal` F3; not restated).
- **Cycle/depth bookkeeping is balanced.** The stack push (622) follows every early return (611-620), so the pop at 691 cannot underflow; a file included twice *sequentially* is not a cycle (the child pops before the second visit) — fixture `r-inc-twice` pins it.
- **Key parsing is faithful.** `git config --list -z` records split on the first `\n` (623-627), so multi-line values survive; `include.foo.path` is rejected (636) and `includeIf.path` without a subsection is rejected (637), matching `parse_config_key(var, "includeif", &cond, ...)` + `cond` checks (`config.c:439`).
- **Non-regular/hardlinked include targets are refused before any open** (`guard_config_file_kind:587-599`; a FIFO cannot block the scan), and a missing target is benign (646-647) as git's `access_or_wait`-style skip is.
- **Caller soft-path handoff is correct.** Both include-branch failures set `soft=1` and `continue` (641-646, 653-657, 661-665), so a later protected reach in the same file still exits 2; the top-level caller turns `soft=1` into one `error` row with no git command (`census_one:1177-1180`), and `CFG_SOFT_REASON` is reset per repo (`guard_git_surface:823`).

## Residual risk / verification gaps

- Static only: S1's race and S2's counterexample are constructed from control flow, not observed (no ALLOWED-EXEC on this item). S5/S6 likewise.
- S2's patch was reasoned against `resolve_guarded`'s walk, not executed; the one behavioural difference it accepts is that a raw path *equal* to the store is now refused by the walk's suffix check (425-429) rather than by the pre-check — still before any `lstat` below the store, but a reviewer should confirm that ordering holds for the exact store path (no trailing component).
- S1's fix assumes `mktemp` failure should degrade the repo; a disk-full `/var/tmp` would then turn every repo into `error`. The alternative (skip the guard on `mktemp` failure) is worse; flag it as the intended trade.
- No census execution, so the matrix's 20/20-changed / r14 12/12 claims are taken from the wave-1 record, not re-measured here; the C1 matrix is `RevMatrixRunnerFinal`'s item.

STATUS: ok

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh && wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -5 -- tools/souji-census.sh
grep -n 'scan_config_file\|guard_config_path\|expand_config_path' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'PROTECTED_FINDING=\|^protected_fail\|^protected_reason_input\|^resolve_guarded\|^lexical_abs\|^guard_target\|^guard_git_surface\|^set ' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'includeif\|includeIf\|include\.path\|includeif' tools/souji-census.sh tests/fixtures/r15-census-config.py census/round-16/run-matrix.py | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git --version && wc -l tests/fixtures/r15-census-config.py census/round-16/run-matrix.py
ls -l /usr/share/man/man5/git-config.5.gz 2>/dev/null; ls -l /usr/doc/git/RelNotes 2>/dev/null | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'optional' tools/souji-census.sh tests/fixtures/r15-census-config.py census/round-16/run-matrix.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'GIT_CONFIG_COUNT\|GIT_CONFIG_KEY\|GIT_CONFIG_VALUE\|GIT_CONFIG_GLOBAL\|GIT_CONFIG_SYSTEM\|GIT_CONFIG_NOSYSTEM\|GIT_NO_LAZY_FETCH\|git_env\|^git_()' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status_info_file\|config-unsupported\|CFG_SOFT_REASON' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'compare_tsv\|emit_diff\|change$\|before\tafter\|^compare' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'error$\|\\terror\|error\\n' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'protected_reason_input "$(lexical_abs\|if out=$(resolve_guarded\|"\$dir"/\*) ;;\|protected_fail "git-metadata-symlink"\|nlink" -gt 1\|protected_fail "git-metadata-hardlink"\|protected_fail "git-metadata-nonregular"\|protected_fail "git-metadata-unavailable"\|if \[ -L "$cfg" \]\|protected_fail "git-metadata-symlink" "$dir" "$cfg"\|worktrees|unpushed|dirty|scratch_bytes\|t0\tt0\tt0\tt0\tt\\terror\|printf .%s\\t0\\t0\\t0\\t0\\t\\terror' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'guard_git_links "$dir"\|guard_git_files "$dir"\|guard_git_config "$dir"\|guard_git_surface "\$cpath"\|guard_git_surface "\$repo"\|guard_wt_config "$first"\|guard_wt_config "$dir"' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w2 2>/dev/null | cat; echo "---"; ls .ufo/waves/round-16 2>/dev/null | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^(cfg_soft|protected_component_reason|protected_reason_inside|protected_reason_input|resolve_guarded|lexical_abs|path_under|path_overlaps|guard_config_file_kind|guard_target|guard_path)\(\)' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -nE '^(scan_config_file|guard_config_path|expand_config_path|guard_git_links|guard_git_files|guard_git_config|guard_wt_config|status_info_file|count_dirty|census_one|emit_compare)\(\)|^  if ! git config --file|^  mapfile -d|^    if ! raw=|^        tgt=\$\(guard_config_path|^        guard_config_path|^        if \[ ! -e "\$tgt" \]|^  if ! tr -d|^  for s in|^  if \[ "\$depth" -gt 10 \]|^  unset |^    s=\$\{s##|^  case "\$out" in|^    \*"\$PROTECTED_FINDING|^  return 3|^    \\~/\*\)|^    \\~\*\|%|^  printf .%s. "\$\{acc:-\/"\}|^      include:path|^      core:excludesfile|^      core:worktree\)|^      extensions:worktreeconfig|^    if \[ -L "\$cfg" \]|^      protected_fail "git-metadata-symlink"|^        "\$dir"\/\*\) ;;|^          \*) protected_fail "git-metadata-symlink"|^      if \[ "\$nlink" -gt 1 \]|^        protected_fail "git-metadata-hardlink"|^    elif \[ -e "\$path" \]|^      printf .%s\\t0\\t0\\t0\\t0\\t\\terror|^        worktrees\|unpushed\|dirty\|scratch_bytes' tools/souji-census.sh | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'git config --file\|mapfile -d\|depth" -gt 10\|tr -d\|raw=\$(expand\|tgt=\$(guard\|guard_config_path git-config\|guard_config_path core-worktree\|guard_config_path include-protected\|if \[ ! -e "$tgt" \]\|s=${s##\|case "$out" in\|PROTECTED_FINDING: credential\|return 3$\|~/\*)\|~)\|%\\(\|include:path\|core:excludesfile\|core:worktree$\|extensions:worktreeconfig' tools/souji-census.sh | cat
```
