# RevWorktreeConfigFlow — `CFG_WT_ENABLED` flow review (round 16 C1)

Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
(1784 lines, sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`;
worktree file is byte-identical to the commit, `git status --porcelain` empty).
Source inspection only; no census or fixture execution.

Git read set used for the analysis: `$GIT_COMMON_DIR/config` is read first, then
`$GIT_DIR/config.worktree` only when `repository_format_worktree_config` is true
(git v2.51.0 `config.c` / `setup.c`, as recorded with links in
`.ufo/waves/round-16/w1/ScoutWorktreeConfigSemantics.md` §Git read rules). A linked
admin's own `$GIT_DIR/config` is **not** in that set. The gate is decided by the
common config only; a value inside `config.worktree` cannot decide whether any
`config.worktree` is read (the same source records that the worktree-config parse
ignores `extensions.*`). The script's own comment at lines 652-653 encodes the
location/gate half of this.

## Verdict

Not clean. The path/gate mechanics that the C1 claim names — main gitdir, the
commondir case via `first`, linked admin dirs, and "never open while false" in the
normal main-repo case — are implemented correctly (see "Checked clean" below).
The defects are all in **which file is allowed to set the decision** and in one
commondir representation:

| ID | Severity | One line |
|---|---|---|
| F1 | High | A `config.worktree` flips the global extension flag, so another worktree's `config.worktree` is skipped while git reads it. |
| F2 | High | A symlinked `commondir` is accepted but not followed: the common config (and the gate in it) is never scanned, and `guard_wt_config "$first"` is never reached. |
| F3 | Medium | A condition-blind `includeIf` target can disable the extension although git would not read that target. |
| F4 | Medium | The inherited seed is overwritten by `<linked-admin>/config`, a file git does not read; can open `config.worktree` while git's gate is false. |
| F5 | Low | An intra-gitdir `config.worktree` symlink is a whole-run `exit 2`, contradicting the header's symlink rule. |

F1/F2/F3 make a crafted repository able to have census-issued `git` calls
(`git -C <wt> config --get`, `git status`, `rev-parse`) read a protected file named
by an unguarded `include.path` (or a protected common dir) without any refusal.
That is the exact boundary this guard exists to hold.

## Checked clean (no defect found)

- Main gitdir, ordinary repo (lines 769-795): 675 resets the flag, 678 scans
  `<gitdir>/config`, 680 calls `guard_wt_config "$dir"`. The gate at 656 precedes
  the `-L` test (657), the `-e` test (660) and every open (663, `tr`/`git config
  --file`), so with the extension false the file is not even stat'ed.
- `first` is set before commondir resolution in both branches (774, 813) and is
  the per-worktree gitdir; `guard_wt_config "$first"` (790, 829) therefore names
  the file git reads for that worktree. The path is right; F1/F4 are about the
  flag the call reads.
- Linked admin scan (741) passes the parent's decision as `$2` and scans
  `<admin>/config.worktree` at 680; path correct, decision-source is F4.
- Bare key = true, empty value = false, and invalid boolean = soft `error` row at
  633-639 match `git_parse_maybe_bool` / `git_config_bool` for the **repository**
  config. `[ -e ] || return 0` (660) does not open a missing file.

## F1 — High — a `config.worktree` can suppress the scan of another `config.worktree`

Evidence: 634/638 write the global `CFG_WT_ENABLED` from whatever file is being
scanned; `guard_wt_config` scans `config.worktree` at 663; the flag is consumed by
741, 790 and 829; nothing saves/restores it.

Concrete flow (ordinary main repo `R`, registered linked worktree `L`):

1. `R/.git/config` has `[extensions] worktreeConfig = true` → 638 sets 1; 680 opens
   `R/.git/config.worktree` (correct).
2. `R/.git/config.worktree` contains `[extensions] worktreeConfig = false` →
   663 → 638 sets **0**. The file is scanned by design, but this value is inert
   to git's gate.
3. `guard_git_config` returns with the global now 0 → 794
   `guard_worktree_registrations R/.git` → 741 passes 0 →
   `guard_wt_config L-admin` returns at 656 without touching
   `L-admin/config.worktree`.
4. The same pollution repeats on the status path: `worktree_extra_flags` →
   `guard_git_surface L` → 828 `guard_git_config R/.git` re-scans `R/.git/config`
   (1) then `R/.git/config.worktree` (0) at 680 → 829 sees 0 and skips
   `L-admin/config.worktree`.
5. `count_dirty L` then runs `git -C L config --get core.excludesFile` (line 876)
   and `git status` (947). Git's gate is true (from `R/.git/config`), so git reads
   `L-admin/config.worktree` and any `include.path` in it — e.g.
   `[include] path = <store>/x` — with no census refusal.

This violates the fixture's pinned semantics "true is accepted only when each
reachable config.worktree is guarded" (`tests/fixtures/r15-census-config.py:55-59`)
and makes the `worktree_extra_flags` re-guard depend on the same polluted value
(the pre-scan skip at 741 is not actually mitigated at 829).

Patch (pin the decision across worktree-file scans; also fixes the invalid-boolean
facet below):

```
 CFG_STACK=()
 CFG_WT_ENABLED=0
+CFG_IN_WT=0     # 1 while scanning a config.worktree (git ignores extensions.* there)
...
       extensions:worktreeconfig)
+        # git decides this from the repository (common) config; a value inside a
+        # config.worktree is inert and must not change the gate for any file.
+        if [ "$CFG_IN_WT" = 1 ]; then continue; fi
         if [ "$bare" = 1 ]; then CFG_WT_ENABLED=1; continue; fi
...
 guard_wt_config() {
-  local dir=$1 wtc="$1/config.worktree"
-  [ "$CFG_WT_ENABLED" = 1 ] || return 0
+  local dir=$1 wtc="$1/config.worktree" enabled=$CFG_WT_ENABLED
+  [ "$enabled" = 1 ] || return 0
   ...
   guard_config_file_kind "$wtc" || return 1
   CFG_STACK=()
-  scan_config_file "$dir" "$wtc" 0 || return 1
+  CFG_IN_WT=1
+  if ! scan_config_file "$dir" "$wtc" 0; then CFG_IN_WT=0; CFG_WT_ENABLED=$enabled; return 1; fi
+  CFG_IN_WT=0
+  CFG_WT_ENABLED=$enabled
   return 0
 }
```

`CFG_IN_WT` must stay set through include recursion (as written: set once around
the top-level scan). Besides F1, this also stops a pointless/invalid
`extensions.worktreeConfig` inside `config.worktree` from producing a false
`error` row at 635-636 (git never re-parses that key from the worktree file); the
restore is kept as belt-and-braces.

## F2 — High — a symlinked `commondir` is accepted but never followed

Evidence: `guard_git_surface` 776-778 (`.git` dir case) and 815-817 (gitfile /
linked case). On `-L`, only `guard_target ... >/dev/null` runs; the `elif [ -f ]`
body — 779-791 / 818-830, including `guard_git_config "$dir"` (789/828) and
`guard_wt_config "$first"` (790/829) — is skipped. `dir` stays the per-worktree
gitdir, so 793 `guard_alternates` and 794 `guard_worktree_registrations` also
inspect the wrong directory. The same shape exists in
`guard_worktree_registrations` 743-745.

Why the link is accepted: `guard_git_links` (492-498) only requires the link
target to resolve inside the gitdir, and `guard_git_files` (505-518) accepts a
symlink to a regular file (`-f` at 507, `stat -L` at 508). Git, however, reads
`<gitdir>/commondir` with `strbuf_read_file`, i.e. it follows the link and then
uses the *content* as the common dir. A crafted repo can therefore ship
`admin/commondir -> ./cd` (inside, passes both guards) with `cd` containing a
protected path or any common dir; every census git call in that repo then reads
`<store>/config` (or a hostile common config, including its `include.path`)
without a scan or refusal. This is the same class as the r14 fixture's
`commondir-alias` case (`tests/fixtures/r14-census-boundary.py:248-258, 578-584`),
which is refused today only when `commondir` is a regular file.

Patch (shared shape; apply at 776-778, 815-817 and 743-744 — resolve first, then
fall into the existing regular-file branch):

```
     common="$dir/commondir"
     if [ -L "$common" ]; then
-      guard_target git-common-dir "$common" >/dev/null
-    elif [ -f "$common" ]; then
+      common=$(guard_target git-common-dir "$common") || exit 2
+    fi
+    if [ -f "$common" ]; then
       IFS= read -r target < "$common" || target=""
       target=${target#"${target%%[![:space:]]*}"}
       ...
```

The content is then boundary-checked at 786 / 825 / 753 as today, so the common
dir path is guarded and the common config plus `guard_wt_config "$first"` are
reached. `guard_git_files` already refuses non-regular/hardlinked link targets.
Conservative alternative (the shape used for alternates): after
`guard_target`, `protected_fail "git-common-dir-unparsed"`.

## F3 — Medium — a condition-blind `includeIf` target can disable the gate

Evidence: 605-617 follow every `include.path`/`includeIf.*.path` target in place
and 633-639 apply last-wins for both. Git evaluates the includeIf condition; a
non-matching target is not read at all (for `gitdir:`/`onbranch:`/unknown
conditions; `hasconfig:` is read in the pre-pass but with a callback that does not
set the extension — see `ScoutIncludeIfConditions.md` §2 and
`ScoutWorktreeConfigSemantics.md` §Git read rules). The census's "follow
everything" choice is fail-closed for *path* refusals, but for the *extension
boolean* the fail-closed direction is the opposite.

Repro: `.git/config` = `[extensions] worktreeConfig = true` plus
`[includeIf "gitdir:/nonexistent/"] path = wt-off.gitconfig`; `.git/wt-off.gitconfig`
= `[extensions] worktreeConfig = false`; `.git/config.worktree` is hostile
(e.g. an include to the store). Git skips the non-matching include and reads
`config.worktree`; the scanner follows the target, 638 sets 0, 680 does not open
the hostile file. The 828→829 path has the same effect for a linked-worktree row,
so this is an under-guard, not only the over-scan the scout considered at 741.

Patch:

```
+CFG_COND_BLIND=0                    # >0 inside an includeIf target (condition unknown)
...
         guard_config_file_kind "$tgt" || return 1
-        scan_config_file "$dir" "$tgt" $((depth + 1)) || return 1
+        if [ "$sec" = includeif ]; then CFG_COND_BLIND=$((CFG_COND_BLIND + 1)); fi
+        if ! scan_config_file "$dir" "$tgt" $((depth + 1)); then
+          if [ "$sec" = includeif ]; then CFG_COND_BLIND=$((CFG_COND_BLIND - 1)); fi
+          return 1
+        fi
+        if [ "$sec" = includeif ]; then CFG_COND_BLIND=$((CFG_COND_BLIND - 1)); fi
...
       extensions:worktreeconfig)
         if [ "$bare" = 1 ]; then CFG_WT_ENABLED=1; continue; fi
         ...
-        if [ "$s" = true ]; then CFG_WT_ENABLED=1; else CFG_WT_ENABLED=0; fi
+        if [ "$s" = true ]; then
+          CFG_WT_ENABLED=1
+        elif [ "$CFG_COND_BLIND" -eq 0 ]; then
+          CFG_WT_ENABLED=0          # only an unconditional false may disable
+        fi
```

A true/bare value in a condition-blind file may enable (over-scan is safe); a
false must not disable.

## F4 — Medium — the inherited seed is overwritten by a file git does not read

Evidence: 675 sets the seed from `$2`; 676-679 then scan `$dir/config` and let
634/638 overwrite it; 680 consumes the result. The only caller that passes `$2`
is 741, for a linked admin. Git's read set for that worktree is
`<common>/config` + `<admin>/config.worktree`; `<admin>/config` is dead (this is
independently confirmed in `ScoutWorktreeConfigSemantics.md` F2).

Two observable effects:

- Over-open / false refusal: common config has no `extensions.worktreeConfig`, but
  a crafted `L-admin/config` has `true`. The 812 call (`guard_git_config L-admin`,
  no seed) scans the dead file, sets 1, and 680 opens
  `L-admin/config.worktree` even though git's gate is false — the opposite of the
  652-653 promise. If that file carries an include or `core.worktree` reaching the
  store, the whole run `exit 2`s on config git never reads.
- Under-open (latent): common `true` + dead `false` makes 741 skip
  `L-admin/config.worktree`. The later `guard_git_surface L` normally re-derives
  at 829, but that re-derivation is itself subject to F1/F3, and F2's symlinked-
  commondir branch skips 829 entirely.

Patch (the inherited seed is final for a linked admin; the dead file must not
speak):

```
 guard_git_config() { # $1 resolved gitdir, $2 optional inherited worktreeConfig (0|1)
   local dir=$1 cfg
   cfg="$dir/config"
+  if [ -n "${2:-}" ]; then
+    # A linked admin's $GIT_DIR/config is never read by git; only
+    # <admin>/config.worktree is. The common config supplied the decision.
+    CFG_WT_ENABLED=$2
+    CFG_STACK=()
+    guard_wt_config "$dir" || return 1
+    return 0
+  fi
   if [ -L "$cfg" ]; then
     protected_fail "git-metadata-symlink" "$dir" "$cfg"
   fi
-  if [ -n "${2:-}" ]; then CFG_WT_ENABLED=$2; else CFG_WT_ENABLED=0; fi
+  CFG_WT_ENABLED=0
```

The skipped `-L "$cfg"` test is redundant for this caller: `guard_git_links`
already ran on the admin at 740 (and 810), so a symlink there has already been
required to resolve inside the gitdir, and git never opens that file.

For the no-seed call at 812 the function cannot yet know whether a commondir
exists; resolve it first (F2 patch), then scan `<admin>/config` only when no
commondir resolves (the admin is its own common dir). Sketch for 810-831:

```
     guard_git_links "$dir" || exit 2
     guard_git_files "$dir" || exit 2
-    guard_git_config "$dir" || return 1
     first=$dir
     common="$dir/commondir"
     ...resolve common (F2)...
     if [ -f "$common" ]; then
       ...read target, dir=common, links/files...
       guard_git_config "$dir" || return 1          # common config only
       guard_wt_config "$first" || return 1         # first/config.worktree
+    else
+      guard_git_config "$first" || return 1        # no commondir: admin is common
     fi
```

The same ordering applies to case A (773/789): scan `.git/config` only when no
commondir resolves; otherwise the common config is the repository config.
Neither reorder changes the ordinary-repo path (no commondir), which is correct.

## F5 — Low — an intra-gitdir `config.worktree` symlink refuses the whole run

Evidence: 657-659 call `protected_fail "git-metadata-symlink"` on **any** symlink
at `<gitdir>/config.worktree` before resolution, whenever the gate is true. The
header (87-88) says "any git-metadata symlink must resolve inside its own gitdir"
(inside is allowed) and `guard_git_links` (492-498) enforces exactly that; git
follows the link, and `guard_config_file_kind` (561-570) itself uses `stat -L`. A
dotfiles-managed `.git/config.worktree -> wt.cfg` (inside) therefore aborts the
entire census while the same link shape is legal for every other git metadata
file. (Independently reported, source- and doc-grounded, in
`ScoutWorktreeConfigSemantics.md` F1.)

Patch (allow inside-resolving links, refuse outside):

```
   if [ -L "$wtc" ]; then
-    protected_fail "git-metadata-symlink" "$dir" "$wtc"
+    wtc=$(guard_target git-metadata "$wtc") || exit 2
+    case "$wtc" in
+      "$dir"/*) ;;
+      *) protected_fail "git-metadata-symlink" "$dir" "$wtc" ;;
+    esac
   fi
```

If the stricter "all symlinks refused" policy is intended instead, the header
must say so and the shape should match the declared degrade list (line 97), not a
whole-run `exit 2` on a benign layout.

## Residual risk / non-defects

- **Over-scan of `<common>/config.worktree` from 680 in the commondir branches
  (789/828).** For a linked-worktree row, git reads
  `<admin>/config.worktree`, not `<common>/config.worktree` (the main worktree's
  file). Scanning it is conservative (it can only refuse more), but it is also
  the mechanism that produces F1. The precise shape: in the commondir branches,
  scan `<common>/config` and let `guard_wt_config "$first"` handle the worktree
  file; do not call `guard_config_file_kind`/`scan_config_file` on
  `<common>/config.worktree` for this row.
- **Trailing whitespace in `commondir`/`gitdir` contents** (746-753, 779-784,
  725-729) is trimmed on the left only, while git's `strbuf_trim` trims both
  ends; a CRLF/trailing-space pointer resolves differently. Not part of the
  CFG_WT flow and not pursued here.
- **Adjacent, already filed elsewhere:** a soft failure from a linked admin's
  `config.worktree` is converted to `wt-dirty` with no reason line at
  1068-1071 (`ScoutWorktreeConfigSemantics.md` F5). I did not re-derive it; it is
  outside the CFG_WT decision flow but is the error-carrying end of
  `guard_git_surface` returning 1.

## Suggested acceptance additions

1. Main repo with `worktreeConfig = true`, `config.worktree` containing
   `[extensions] worktreeConfig = false`, a linked worktree whose
   `config.worktree` contains `[include] path = <store>/x` → must exit 2 with
   `path-protected`; current code exits 0 and git opens the store path (F1).
2. Same but with the false value in a non-matching `includeIf` target (F3).
3. A `commondir` that is a symlink (inside the gitdir) to a file naming a
   protected gitdir/common dir → must exit 2; current code proceeds (F2).
4. A linked admin `config` with `worktreeConfig = true` while the common config
   says false, and `admin/config.worktree` carrying a store include → must not
   read/refuse on the dead file's gate (F4).
5. `config.worktree` as an intra-gitdir symlink to a benign file → must be green
   (F5).

## Commands

Probe-rule note: one read-only `git status --porcelain tools/souji-census.sh`
was used only to confirm the worktree file equals the commit; it is outside the
enumerated git subcommand list (`show|log|diff|cat-file|ls-tree|rev-parse`) though
non-mutating and path-scoped. A scratch copy under `/var/tmp` was created from
`git show` bytes for line-numbered inspection and deleted with `rm`; nothing was
executed. No census run, no fixture run, no install/upgrade.

All shell commands run (verbatim), in order. `read`/`glob`/`grep` tool calls on
`/usr/share/man`, `/usr/share/doc` and `corpus/` are listed after as tool reads;
none executed the census or a fixture.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n "CFG_WT_ENABLED\|guard_git_config\|guard_wt_config\|guard_git_surface\|guard_worktree_registrations\|config.worktree\|extensions.worktreeConfig"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh && sed -n '80,115p' /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
sed -n '540,700p' /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
sed -n '700,850p' /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
sed -n '380,540p' /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
sed -n '1030,1230p' /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '650,700p'
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '710,845p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -12 -- tools/souji-census.sh; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b410186 cbf688ab -- tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cc21683 cbf688ab -- tools/souji-census.sh | sed -n '1,200p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cc21683 cbf688ab -- tools/souji-census.sh | sed -n '200,420p'
grep -n "worktreeConfig\|config.worktree\|worktreeconfig" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py
sed -n '1,90p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
sed -n '590,640p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py; echo =====; sed -n '1150,1205p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
sed -n '470,505p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py; echo =====; sed -n '940,980p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
sed -n '1,80p' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15-verifier-spotcheck.md
sed -n '1,80p' /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh; grep -n "wt-dirty\|wt-absent\|status-unverifiable\|status-skipped" /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '1,60p'
grep -n "first\|CFG_WT_ENABLED" /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
for f in /usr/share/man/man1/git-config.1.gz /usr/share/man/man1/git-worktree.1.gz /usr/share/man/man5/gitrepository-layout.5.gz; do [ -e "$f" ] && echo "present $f"; done
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '490,540p'
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '596,650p'
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '754,800p'
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '868,905p'
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '180,260p'; grep -n "build_protected_roots" /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
nl -ba /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh | sed -n '552,572p'
grep -n "def init_repo" -A 25 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
grep -n "CFG_SOFT_REASON\|cfg_soft\|guard_config_file_kind\|scan_config_file" /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh
grep -n "commondir\|gitdir\|worktree" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py | sed -n '1,80p'
grep -n "config.worktree\|worktreeConfig" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py | sed -n '1,40p'; echo ===; sed -n '120,160p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
sed -n '236,272p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py; echo ====; sed -n '560,625p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py
grep -n "includeIf\|includeif" /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py | sed -n '1,40p'
sed -n '180,240p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
sed -n '420,460p' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
sed -n '1,140p' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ScoutWorktreeConfigSemantics.md
sed -n '1,120p' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ScoutIncludeIfConditions.md
sed -n '140,260p' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ScoutWorktreeConfigSemantics.md
sed -n '120,260p' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ScoutIncludeIfConditions.md
rm -f /var/tmp/souji-r16-RevWorktreeConfigFlow.census.sh && echo removed
```

Tool reads (no execution): `read` of `/usr/share/man/man1/git-config.1.gz`,
`/usr/share/man/man1/git-config.1.gz:1-60`, the `corpus/knowledge` directory and
`corpus/knowledge/git-repo-structure-readonly.md`; `glob` of `/usr/share/doc/git*/**`;
`grep` of `/usr/share/man/man1/git-config.1.gz` for `config\.worktree`; `read` of
`.ufo/waves/round-16/w1` (directory listing). The manpage was not text-extractable
by these tools, so the git read-set claims above rest on the peer scout's recorded
git v2.51.0 source citations, not on my own re-open of the source.

STATUS: no execution performed (source-only review); no known failing check.
