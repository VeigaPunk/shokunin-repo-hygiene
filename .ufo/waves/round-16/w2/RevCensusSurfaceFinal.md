# RevCensusSurfaceFinal — source review: census git-surface guards

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Target: `tools/souji-census.sh` (sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, unchanged since `0a70bef`), functions
`guard_git_surface` (821-901), `guard_worktree_registrations` (766-815), `guard_wt_config` (696-711), `guard_git_config` (715-733),
plus `scan_config_file` (608-692) where the two config guards delegate.
Method: static source review only (no ALLOWED-EXEC in this item; the census was not executed, not even a copy).

## Verdict per function

| function | verdict | summary |
|---|---|---|
| `guard_git_config` | **fails** (whole-run contract) | F1: any symlinked `config` is a whole-run exit 2, including an in-gitdir link the header admits; F3: relative excludes/attributes base is wrong for linked admins; F2 origin: it treats its argument as an extension source. |
| `guard_wt_config` | **fails** (whole-run contract) | F1 at 699-700 (same symlink over-refusal). The rest holds: value gating (`CFG_WT_ENABLED`), inherited restore 703/708-709, stack reset 705 are correct. |
| `guard_git_surface` | **partial** | F2 at 874 (and 832 when a commondir exists): a linked admin's own `extensions.worktreeConfig` is honoured, so `config.worktree` is opened/guarded although the documented model calls it inert. F4 at 866: an empty `gitdir:` target is a whole-run exit 2. F6: the function is executed twice per repo. |
| `guard_worktree_registrations` | **holds** (one low-severity gap) | Ordering is right (registrations guarded before `git worktree list` runs); inherited value at 792 is correct; `$reg` non-regular is skipped, not opened (775). F5: `worktrees/*/gitdir` is read without the hardlink check applied to fixed metadata names. |

**Claim under attack — "only a protected reach exits 2 whole-run": FALSE at three inputs.** F1 (in-gitdir symlinked config), F2 (protected path inside a `config.worktree` the model says git never reads), F4 (empty/unparsable `.git` pointer at 866) each terminate the whole run with `path-protected` while the named input reaches no protected path *of the run*. Severities below are per blast radius (HIGH = whole-run loss for a benign repo).

## F1 — HIGH — `guard_git_config:718-719` and `guard_wt_config:699-700` refuse *every* symlinked config file, including links that resolve inside the gitdir

Evidence:

```
718	  if [ -L "$cfg" ]; then
719	    protected_fail "git-metadata-symlink" "$dir" "$cfg"
```
```
699	  if [ -L "$wtc" ]; then
700	    protected_fail "git-metadata-symlink" "$dir" "$wtc"
```

The documented rule is narrower: header 83-88 says *"any git-metadata symlink must resolve inside its own gitdir"*, and `guard_git_links:508-513` implements exactly that (`"$dir"/*` admitted, only an outside-resolving link is `git-metadata-symlink`). Both config guards are unreachable for an outside-resolving link anyway, because `guard_git_links` always runs first on the same directory at every call site (830/848/872/890 for the four branches; 791 for worktree admins). So `-L` fires *only* on an inside-resolving link — the case the header admits. The `commondir` handling elsewhere in this file already uses the correct shape (794-796, 835-837, 877-879: resolve the link through `guard_target`, then keep reading the spelled path).

Counterexample: `repo/.git/config -> config.main` (sibling file inside `.git`) → `guard_git_links` folds and admits it → 718 refuses → entire fleet census exits 2 with `souji-census: path-protected: git-metadata-symlink (<gitdir>: <gitdir>/config)`, no rows for any repo. Same for `<admin>/config.worktree -> cw.main`.

Minimal patch (both sites; keeps the spelled path so relative `include.path` still resolves against the directory git itself uses):

```diff
--- a/tools/souji-census.sh
+++ b/tools/souji-census.sh
@@ guard_wt_config
-  if [ -L "$wtc" ]; then
-    protected_fail "git-metadata-symlink" "$dir" "$wtc"
-  fi
+  if [ -L "$wtc" ]; then
+    # Links leaving the gitdir were refused by guard_git_links; fold this one
+    # so a protected target still refuses (round 16).
+    guard_target git-metadata "$wtc" >/dev/null
+  fi
@@ guard_git_config
-  if [ -L "$cfg" ]; then
-    protected_fail "git-metadata-symlink" "$dir" "$cfg"
-  fi
+  if [ -L "$cfg" ]; then
+    guard_target git-metadata "$cfg" >/dev/null
+  fi
```

Coverage gap: the fixture (`tests/fixtures/r15-census-config.py:498-499`) covers only an *include-target* symlink into the store; `CONFIG_REASONS` (998-1011) does not even contain `git-metadata-symlink`, so this class is untested. Add one case: in-gitdir `config` symlink → green; `config -> ../outside` → exit 2 (already produced by `guard_git_links`).

## F2 — HIGH — `guard_git_surface:874` (and 832 when a commondir exists) takes `extensions.worktreeConfig` from the linked admin's own config, so an inert `config.worktree` is opened and can refuse the run

Evidence: in the `.git`-file branch the admin is guarded *before* the common dir is known:

```
874	    guard_git_config "$dir" || soft=1
875	    first=$dir
876	    common="$dir/commondir"
...
892	        guard_git_config "$dir" || soft=1
893	        guard_wt_config "$first" || soft=1
```

With no `$2`, `guard_git_config` starts at `CFG_WT_ENABLED=0` (721) but `scan_config_file` line 669-675 sets it from `[extensions] worktreeConfig` found in `$dir/config` — here the *per-worktree* config — and line 730 then calls `guard_wt_config "$dir"`. This directly contradicts the function's own comment (706-707: "git takes extensions.worktreeConfig from the common config only") and 727-729 ("A linked admin's own config is never git's extension source"). The header (90-93) says config.worktree is scanned only "when the *common* config's extensions.worktreeConfig is true".

Counterexample (the fixture's own inertness principle, extended): repo with common `[extensions] worktreeConfig = false`, plus `git worktree add ../wt`. Write `[extensions]\n\tworktreeConfig = true` into `.git/worktrees/<n>/config` and a hostile `core.worktree = ~/.omp/agent` or `[include] path = ~/.omp/agent/x` into `.git/worktrees/<n>/config.worktree`. Census: `census_one` → `worktree_extra_flags` → `guard_git_surface <wt>` (1156) → 874 sets `CFG_WT_ENABLED=1` from the admin config → 699/708 opens and scans the admin `config.worktree` → protected reach → whole run exit 2. Git, per the documented model, never reads that file (`worktreeConfig` is off). The same input also trips `tests/fixtures/r15-census-config.py:1242` `no_open=("config.worktree",)` if the fixture's `FL_WTC_OFF` fleet gains one linked worktree. `guard_worktree_registrations:792` is *not* affected (it passes the inherited value and 729 restores it), which is why the defect only shows on the gitfile path.

Minimal patch: the gitfile branch is always a linked admin, and the `-d` branch is one exactly when it has a commondir.

```diff
@@ guard_git_surface (-f branch)
-    guard_git_config "$dir" || soft=1
+    guard_git_config "$dir" 0 || soft=1   # common config decides (893)
@@ guard_git_surface (-d branch)
-    guard_git_config "$dir" || soft=1
+    if [ -f "$dir/commondir" ]; then
+      guard_git_config "$dir" 0 || soft=1
+    else
+      guard_git_config "$dir" || soft=1
+    fi
```

`guard_wt_config "$first"` at 851/893 still scans the admin's `config.worktree` iff the common config enabled it, so no coverage is lost. Add the fixture case above (off + linked admin self-declares): it must stay green and `no_open` must hold.

## F3 — MEDIUM — relative `core.excludesFile` / `core.attributesFile` are expanded against the gitdir's parent, not the censused worktree root

Evidence: `scan_config_file:652` expands excludes/attributes against `${dir%/*}`. For a main repo that is the worktree root (correct by accident), but `guard_git_config` is also called with a linked admin (`.../.git/worktrees/<n>`, from 874 and from 792), where `${dir%/*}` is `.../.git/worktrees`. The tool's own effective-value path uses the worktree root: `status_info_file:948` expands the same keys against `$wt`, and `count_dirty:1037` runs `git -C "$wt" status`, i.e. git's cwd (and therefore `interpolate_path`'s base for a relative value) is also `$wt`. The two disagree for every linked worktree.

Effect: the guard resolves a path git never reads. A benign relative value can be refused for the whole run when the *wrong-base* path touches a protected root (e.g. `<repo>/.git/link` is a symlink into the store, while the real path `<worktree-parent>/link/...` is benign), and the guard's answer is unrelated to what status will open. (The opposite direction — real path protected, wrong-base path clean — is still caught later by `status_info_file` before any status runs, so this is not a read escape; it is a false-refusal/completeness defect.)

Counterexample: linked worktree root `/home/vgpnk/Projects/x-wt`, admin `/home/vgpnk/Projects/x/.git/worktrees/x-wt`, admin config `core.excludesFile = ../link/rules`. Guard: `/home/vgpnk/Projects/x/.git/worktrees/../link/rules` = `/home/vgpnk/Projects/x/.git/link/rules` (guarded path, may be refused); git with cwd `x-wt`: `/home/vgpnk/Projects/link/rules`.

Minimal patch: thread the worktree root. Smallest diff in this file's global style:

```diff
@@ globals
 CFG_STACK=()
 CFG_WT_ENABLED=0
+CFG_WT_ROOT=""            # worktree root whose cwd git will use
@@ scan_config_file (core:excludesfile|core:attributesfile)
-        if ! tgt=$(expand_config_path "${val#:(optional)}" "${dir%/*}"); then
+        if ! tgt=$(expand_config_path "${val#:(optional)}" "${CFG_WT_ROOT:-${dir%/*}}"); then
@@ guard_git_surface entry
   CFG_SOFT_REASON=""
+  CFG_WT_ROOT=$repo
@@ guard_worktree_registrations (per admin; $wt is the registered worktree)
-            guard_git_config "$admin" "$CFG_WT_ENABLED" || soft=1
+            CFG_WT_ROOT=$wt
+            guard_git_config "$admin" "$CFG_WT_ENABLED" || soft=1
```

(Cleaner: an explicit `$3` worktree-root argument on `guard_git_config`/`scan_config_file`; either way 652 must use the cwd base, not the gitdir base.)

## F4 — MEDIUM — an empty `gitdir:` target in a `.git` file is a whole-run exit 2, while the same malformed input is silently skipped elsewhere

Evidence:

```
860	    IFS= read -r target < "$g" || target=""
861	    case "$target" in
862	      gitdir:*) target=${target#gitdir:} ;;
863	      *) return 0 ;;
864	    esac
865	    target=${target#"${target%%[![:space:]]*}"}
866	    [ -n "$target" ] || protected_fail "unresolved-path" "$repo" "$g"
```

Three other readers treat the same classes differently: `gitfile_admin:746` (`[ -n "$target" ] || return 0`), `guard_git_pointer:760` (no admin → return 0), and 863 above (non-`gitdir:` line → return 0, repo later gets an `error` row from `git rev-parse`). So: `printf 'gitdir:' > wt/.git` (a truncated pointer) → `worktree_extra_flags` → 1156 → 866 → the whole census exits 2 with `path-protected: unresolved-path`; the identical child repo at `list_repos:1295` is dropped without a row and without a finding. A same-class line `garbage` yields an `error` row. No reason in the documented refusal list (93-96) covers `unresolved-path`.

Minimal patch (degrade like the other unparsable inputs; the repo then gets the honest `error` row / `wt-dirty`+stderr):

```diff
-    [ -n "$target" ] || protected_fail "unresolved-path" "$repo" "$g"
+    if [ -z "$target" ]; then
+      CFG_SOFT_REASON=${CFG_SOFT_REASON:-git-gitfile-unresolved}
+      return 1
+    fi
```

## F5 — LOW — hardlink aliasing is checked for fixed metadata names but not for the two pointer files that are read

`guard_git_files:519-535` refuses `nlink > 1` for `config`, `HEAD`, `index`, … precisely because a hardlink aliases content; `guard_config_file_kind:587-596` does the same (softly) for include targets and `config.worktree`. The `<repo>/.git` file (860) and `.git/worktrees/*/gitdir` (775-776) are opened and read with no nlink check, so a hardlink to a protected file is read (first line only, never echoed, so no canary leak; it is a pre-access read of protected bytes the boundary is meant to prevent, invisible to the path-based oracle). Minimal patch at 775 and 859:

```sh
nlink=$(stat -L -c %h -- "$reg" 2>/dev/null || true)   # and -- "$g" in the -f branch
case "$nlink" in ''|*[!0-9]*) cfg_soft "git-metadata-unavailable"; continue ;; esac
[ "$nlink" -le 1 ] || { cfg_soft "git-metadata-hardlink"; continue; }
```
(add `nlink` to the `local` list; the `-f` branch can `return 1` with the reason instead of `continue`).

## F6 — LOW (scale) — the same gitdir is fully guarded two-to-W times per run

`guard_git_links` walks the whole `.git` tree twice (`find … -type d`, `find … -type l`, 502/514) and `scan_config_file` spawns `git config` 1-2× per file; `guard_worktree_registrations` re-scans every admin's config for every invocation (768-812). Per repo that work is paid at `list_repos:1266/1269/1299` **and again** at `census_one:1177` — the first result is discarded (`|| true`) and `emit_census` buffers all rows (1315-1330), so a mid-loop exit 2 still prints no rows. Additional passes: one `guard_git_surface` per present linked worktree (1156), each re-walking the common gitdir and re-scanning all W admins ⇒ O(W²) config scans per repo.

Minimal patch: memoize success per resolved dir (a `declare -A` guarded-dir set checked at the top of `guard_git_links`/`guard_git_files`, and a `dir -> ok|soft` result for the `scan_config_file` call in `guard_git_config`). That keeps the early-refusal property and removes both the list_repos duplicate and the W² rescan. Deleting 1266/1269/1299 outright is the alternative (provably redundant with 1177 given the buffered output).

## F7 — LOW (diagnostics) — a protected excludes/attributes value is reported as `git-config-unsupported`

`guard_config_path:655` and `:948` pass the *degrade* reason as the refusal reason, so `protected_fail` prints `souji-census: path-protected: git-config-unsupported (<dir>: <cfg>)` for a real protected reach. The fixture accepts it only because `CONFIG_REASONS:999` lists `git-config-unsupported` as a valid refusal reason. Patch: use `git-excludes-protected` / `git-attrs-protected` at 655 (and the key-specific one at 948), and add those two to `CONFIG_REASONS`. Diagnostics only; no behaviour change.

## Verified clean (no finding)

- Guard-before-git ordering: `guard_git_surface` completes before `rev-parse`, `worktree list`, `rev-list` and `status` in `census_one`; `guard_worktree_registrations` runs before `git worktree list`; `count_worktrees`/`count_unpushed` read no excludes/attributes.
- No blocking open on hostile metadata: FIFO/non-regular `config` → `guard_git_files` 532-536 → exit 2 before any open; FIFO `config.worktree` → `guard_config_file_kind` soft before any open; FIFO `worktrees/*/gitdir` → `[ -f ]` false at 775 → skipped. Directory/FIFO `worktrees` entry is skipped at 773.
- `extensions.worktreeConfig` value handling is value-aware: bare ⇒ true (670, matches git's boolean reading), `git config --type=bool` validates every other spelling, invalid ⇒ soft `git-config-unparsed` (671-672), last value wins (674-675). `CFG_WT_ENABLED` restore at 703/708-709 and 721/729 is correct, and `guard_worktree_registrations:792` passes the common value correctly.
- `CFG_STACK` push/pop is balanced on every `scan_config_file` path (depth and cycle returns happen before the push; 637/691).
- A `.git` symlink is not followed as a row (824-827 + `census_one:1181` + `worktree_extra_flags:1145-1147`), and no git command runs on such a path.
- Empty/unparsable commondir falls through to "no common dir" without opening anything the model says is unread (839-853/881-895).

## Residual risk / verification gaps

- Static review only; no census execution (this item carries no ALLOWED-EXEC), so every claim is from control flow, not observed exit codes.
- Two git behaviours underlying F2/F3 are taken from the tool's own documented model rather than from executed git: (a) `extensions.worktreeConfig` is read from the common config only; (b) a relative `core.excludesFile` resolves against the process cwd (`-C <worktree>`). `status_info_file:948` independently encodes (b), which is the internal evidence used here; `/usr/share/man/man5/git-config.5.gz` is not installed, so the external doc could not be consulted.
- The relative-target base for `worktrees/*/gitdir` (780, "admin dir") and the include-following question for `extensions.*` at depth>0 (669) were not settled; if git resolves either differently, F2's scope grows by one branch and `scan_config_file`'s depth-0 restriction becomes an under-scan.

STATUS: ok

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --oneline HEAD | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 -- tools/souji-census.sh && git diff 0a70bef..HEAD --stat -- tools/souji-census.sh; echo "---"; grep -n "worktree\|symlink\|fifo\|hardlink" tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && bash -n tools/souji-census.sh && echo BASH-N-OK; command -v shellcheck && shellcheck -S warning tools/souji-census.sh; echo "SC-RC=$?"; sha256sum tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "wt-link\|worktrees/\|gitdir\b\|commondir\|\.git ->\|symlink" tests/fixtures/r15-census-config.py | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "config-worktree-protected\|core-worktree-protected\|include-protected\|git-config-unsupported" tools/souji-census.sh tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "config-worktree-protected" -r tools tests | head; echo "---"; sed -n '600,700p' tools/souji-census.sh | grep -n "guard_config_path\|expand_config_path"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=735 && NR<=905 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh | sed -n '1,175p' | grep -nE "guard_git_surface|guard_git_config|guard_wt_config|guard_git_links|guard_git_files|commondir|first=|return [01]|soft"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "guard_git_surface\|guard_git_config\|guard_wt_config\|guard_worktree_registrations" tools/souji-census.sh; echo "---protected-finding---"; grep -n "PROTECTED_FINDING=" tools/souji-census.sh; echo "---list-repos-lines---"; awk 'NR>=1257 && NR<=1307 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh | grep -n "guard_git_surface\|guard_git_pointer\|REPOS+="
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=755 && NR<=800 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh; echo "=== 820-905 ==="; awk 'NR>=820 && NR<=905 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "must resolve inside\|through \`config.worktree\`\|common config's extensions.worktreeConfig\|Refused (exit 2\|Degraded to one\|Skipped for that repository" tools/souji-census.sh; echo "---1156---"; awk 'NR>=1127 && NR<=1160 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh | grep -n "crepo\|cpath\|guard_git_surface\|saw_dirty"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "scan_config_file\|CFG_WT_ENABLED=" tools/souji-census.sh | head -20; echo "---dirs---"; read -r _ < /dev/null; ls -d .ufo/waves/round-16/w2 2>/dev/null || echo NO-W2-DIR
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=83 && NR<=88 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh; awk 'NR>=536 && NR<=540 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && f=.ufo/waves/round-16/w2/RevCensusSurfaceFinal.md && python3 - "$f" <<'EOF'
import sys,io
p=sys.argv[1]
s=open(p,encoding='utf-8').read()
repl=[("header 84-87 says","header 83-88 says"),
      ("`guard_git_files:519-539` refuses","`guard_git_files:519-535` refuses"),
      ("`count_dirty:1032` runs","`count_dirty:1037` runs"),
      ("`CONFIG_REASONS` (995-1011)","`CONFIG_REASONS` (998-1011)"),
      ("`tests/fixtures/r15-census-config.py:1234-1240`","`tests/fixtures/r15-census-config.py:1242`"),
      ("buffers all rows (1314-1330)","buffers all rows (1315-1330)")]
for a,b in repl:
    if a not in s: print("MISS:",a)
    s=s.replace(a,b)
open(p,'w',encoding='utf-8').write(s)
print("done",len(s))
EOF
```
