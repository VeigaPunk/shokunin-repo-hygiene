# RevR14NamespaceRetention — r14 boundary fixture vs the r16 census

Scope: source inspection (no execution, per item) of
`tests/fixtures/r14-census-boundary.py` (735 lines, sha256 `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`)
against `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
(1784 lines, sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`;
blob == worktree file). All `souji-census.sh` line numbers below are the cbf688a blob.

Verdict: **all 12 cases are consistent with the script at cbf688a by source reading**, and
**none of the eight refusal cases can be converted to a soft `error` row by r16 as the fixture
constructs its world**. r16 nevertheless introduced one ordering change (F1) that *does*
convert a namespace refusal into a soft `error` row when the same repository also carries an
unevaluable config; the fixture cannot see it because no refusal-case repo is given a config.
Two smaller deviations (F2 latent, F3 pre-existing) and one diagnostic drop (F4, low) follow.

---

## 1. Refusal / non-refusal map for the 12 cases

Shared machinery (all unchanged from cc21683 except `protected_fail`'s masking, 184–192):

- `protected_fail` → `exit 2`, with `path-protected` in stderr: 184–192.
- `protected_component_reason` (`.omp`+`agent` pair 314–316; `census/operator-sweep-*` 317–319;
  `.ufo/state|watchdog.log` 320–322): 302–325.
- `protected_reason_inside` (component pair or path *under* a root): 330–343.
- `protected_reason_input` (component pair or path *equal to / under / ancestor of* a root, via
  `path_overlaps` 223–225): 346–359.
- `resolve_guarded` (per-component walk, `..` refusal 368–371, input predicate 385–389,
  remaining-suffix pre-lstat check 408–412, symlink hop 413–429, final predicate 433–437): 365–439.
- `guard_path` 441–445, `guard_target` 450–454, `guard_config_path` 524–535.
- `cfg_soft` (the one soft return; sets `CFG_SOFT_REASON`, returns 1): 551–558.
- `census_one` soft→row conversion (`config-unsupported` on stderr, `error` row, **no git
  command runs**): 1087–1092.

| case | invocation | refusing path at cbf688a | lines | can r16 soften it? |
|---|---|---|---|---|
| 01 | `--root <AGENT>` | main guard 1772 → `guard_path` 441 → `resolve_guarded` 386–388 → `protected_reason_input` 346–358 → pair `.omp`+`agent` 314–316 | 1772, 365–388, 346–358, 314–316 | No — no return-1 path in the walkers |
| 02 | `--root <AGENT>/sessions` | same pair, refused before any stat (doc 74–82) | 1772, 386–388, 314–316 | No |
| 03 | `--root <HOME>` | `protected_reason_input` 352–357 → `path_overlaps` 223–225 (root is a *descendant* of the input) | 1772, 352–357, 216–225 | No |
| 04a | `--root <root-alias>` (symlink → AGENT) | input predicate passes lexically; walk reaches the link at 413, `readlink` 414, then remaining-suffix check 408–412 (or component pair 405–407 at `agent`) | 385–412, 413–429 | No |
| 04b | `--root <root-alias>/..` | `case "/$raw/" in *"/../"*` → `ambiguous-path`, filesystem-independent | 368–371 | No |
| 05a | `--compare <AGENT>/records.tsv` | main guard 1773 → pair 314–316; re-guarded in `load_census` 1252 | 1773, 1252, 346–358 | No |
| 05b | `--compare <compare-alias.tsv>` (symlink → RECORDS) | walk 413–429 then pair/suffix 405–412 | 413–429, 405–412 | No |
| 05c | `--compare /proc/self/fd/999` | `guard_path` passes (resolves to `/proc/<pid>/fd/999`); `load_census` `special-path` list | **1253–1256** | No — hard list, not a walker or a config |
| 06a gitfile | `--root <GF_REPO> --include-root` | `list_repos` 1175–1177 → `guard_git_surface` `-f` branch 797 → gitdir target 798–802 → `guard_target` 809 → pair | 809, 346–358 | Hard *before* config (809 < 812) |
| 06b git-symlink | `--root <GS_REPO> --include-root` | `list_repos` 1173–1174 → `guard_target git-metadata` → target is GD → pair | 1173–1174 | No |
| 06c commondir | `--root <GC_REPO> --include-root` | 809–812 pass on `SAFE_GD`; `commondir` read 818 → `guard_target` **825** | 818, 825 | **Ordering risk** — 825 is behind config gate 812 (F1) |
| 07 | safe fleet | positive: config scan 579–650 returns 0 on a `git init` config; `status_info_file` 884–896 cannot resolve into a store (HOME is a synthetic dir); `find -P` 986–990 | 1087–1092, 874–902 | n/a |
| 08 | `.scratch` symlink → AGENT | positive: `scratch_bytes` `-L` 963; `du -sb -P` 968 and `find -P` 986 never follow | 961–974, 980–1035 | n/a |
| 09 | poisoned `GIT_*` + `HOME=<AGENT>` | positive: every `GIT_*` unset 149–151 before any read; `HOME` reaching the store only makes `status_info_file` return `/dev/null` | 149–151, 884–896 | n/a — this is the r16 change that *protects* case 09 |
| 12 | symlink child `alias-child` → LEAK | positive: `protected_reason_input` is lexical (1193), then `-L` skips without following (1197) | 1193–1197 | n/a |

Non-refusal checks the fixture makes that the script satisfies by construction: the header is
printed only after all rows are collected (1236), so every mid-run refusal leaves stdout empty;
`protected_fail` exits 2 from inside command substitutions via `|| exit 2` at 443/452/1252.

---

## 2. The conversion question — answer

**No for the 12 cases as written.** All eight refusals terminate in `protected_fail` at the
namespace walkers, which have no soft variant, or in `load_census`'s hard `special-path` list
(1253–1256). `cfg_soft` is reachable only while *evaluating a config file*:
`guard_config_file_kind` 561–570, `scan_config_file` 579–650, `guard_wt_config` 654–665. Every
fixture repo carries only `git init` keys (`core.repositoryformatversion`, `filemode`, `bare`,
`logallrefupdates`); none matches a `case` arm at 604–646, so `guard_git_config` (669–682)
returns 0 and `census_one` cannot take the error-row branch. Case 09's injected
`GIT_CONFIG_KEY_0=core.worktree` never reaches the scanner because 149–151 unsets all `GIT_*`
before the first read.

**Yes structurally (F1).** r16 replaced r14's `|| exit 2` with `|| return 1` at 773, 789, 794
(and 812, 828, 833), and added the same at 790 and 829, and every one of those sits *before* the
hard git-surface checks it is meant to protect:

- 773 before the commondir guard 776–786, alternates 793, registrations 794;
- 812 before the commondir guard 814–825 (this is case 06c's own guard at 825);
- 741 (`guard_git_config "$admin" … || return 1`) before that admin's commondir guard 742–755
  (this is case 10's guard at 753).

So a repository that is both "namespace-refused" and "config-unevaluable" now yields
`souji-census: config-unsupported: <reason>` + one `error` row + exit 0 (1087–1092) instead of
`path-protected` + exit 2. Concretely: add one
`[includeIf "onbranch:never"] path = ~nobody/inc` line to `WT_OWNER/.git/config` or
`ALT_REPO/.git/config` in the fixture and R14C2-10 / R14C2-11 (and R14C2-06 commondir with a
config in `SAFE_GD`) flip from "exit 2, path-protected" to "exit 0, error row" without reading
the store. No access occurs (1091 returns before any git/du/find call), so this is an exit-code
and finding-fidelity deviation, not a leak — but it contradicts C1's "Only a protected-namespace
reach keeps whole-run exit 2" whenever both conditions coexist, and the 12-case fixture provably
cannot detect it.

### F1 — medium — soft config return pre-empts the hard git-surface guards

`tools/souji-census.sh` 773, 789–790, 794, 812, 828–829, 833 (and 741 inside
`guard_worktree_registrations`). Introduced by cbf688a (cc21683 had `|| exit 2` at each site,
and cc21683's `guard_git_config` could only return 0 or exit 2, so the guard was unreachable).

Minimal patch — defer the soft return until all hard checks have run:

```diff
@@ guard_worktree_registrations (715)
-  local dir=$1 entry reg target wt admin common c
+  local dir=$1 entry reg target wt admin common c soft=0
@@ 741
-            guard_git_config "$admin" "$CFG_WT_ENABLED" || return 1
+            guard_git_config "$admin" "$CFG_WT_ENABLED" || soft=1
@@ 760 (after `done`)
   done
+  [ "$soft" = 1 ] && return 1
 }

@@ guard_git_surface (763)
-  local repo=$1 g="$1/.git" target common dir first
+  local repo=$1 g="$1/.git" target common dir first soft=0
@@ 773
-    guard_git_config "$dir" || return 1
+    guard_git_config "$dir" || soft=1
@@ 789-790
-        guard_git_config "$dir" || return 1
-        guard_wt_config "$first" || return 1
+        guard_git_config "$dir" || soft=1
+        guard_wt_config "$first" || soft=1
@@ 794
-    guard_worktree_registrations "$dir" || return 1
+    guard_worktree_registrations "$dir" || soft=1
+    [ "$soft" = 1 ] && return 1
     return 0
@@ 812, 828-829, 833 (the `-f` branch)
-    guard_git_config "$dir" || return 1
+    guard_git_config "$dir" || soft=1
-        guard_git_config "$dir" || return 1
-        guard_wt_config "$first" || return 1
+        guard_git_config "$dir" || soft=1
+        guard_wt_config "$first" || soft=1
-    guard_worktree_registrations "$dir" || return 1
+    guard_worktree_registrations "$dir" || soft=1
+    [ "$soft" = 1 ] && return 1
   fi
   return 0
```

Effect on the fixture: zero (every fixture repo scans clean, so `soft` stays 0; the 12 outcomes
are unchanged). Effect on a mixed repo: `path-protected`/exit 2 wins over the soft row, which is
what the C1 claim states.

---

## 3. F2 — low (latent) — `status_info_file` still hard-refuses an unevaluable value

`tools/souji-census.sh` 878–880: `expand_config_path` failure (`~user`, `%(prefix)`) calls
`protected_fail "git-config-unsupported"` → exit 2, while the *same key* in `scan_config_file`
619–625 is `cfg_soft` → `error` row ("could-not-evaluate config degrades to one `error` row",
doc 90–97). Unreachable today (the scan soft-fails first, so `count_dirty` 935–959 never runs for
that repo), but it is a live whole-run refusal sitting behind a should-be-soft policy; any later
relaxation of the scan (an R2-class follow-up) silently restores exit 2 for a benign
`core.excludesFile = ~otheruser/x`. Note also that `count_dirty`'s `|| exit 2` at 937–938 turns
any nonzero return from `status_info_file` into exit 2.

Minimal patch (route it to `status-unverifiable`, matching the r14 invalid-promisor precedent,
doc 105–107):

```diff
@@ status_info_file 877
   if [ -n "$val" ]; then
-    tgt=$(expand_config_path "$val" "$wt") \
-      || protected_fail "git-config-unsupported" "$wt" "$key"
+    if ! tgt=$(expand_config_path "$val" "$wt"); then
+      return 1
+    fi
@@ count_dirty 937-938
-  ex=$(status_info_file "$1" core.excludesFile ignore) || exit 2
-  at=$(status_info_file "$1" core.attributesFile attributes) || exit 2
+  ex=$(status_info_file "$1" core.excludesFile ignore) || { printf 'unverifiable'; return 0; }
+  at=$(status_info_file "$1" core.attributesFile attributes) || { printf 'unverifiable'; return 0; }
```

`status_info_file` prints nothing on that path, so the capture stays empty and the `||` branch
returns `unverifiable` for the row; `count_dirty` never reaches the `git status` call at 947–953
with a bogus `-c core.excludesFile=` value.

---

## 4. F3 — low (pre-existing from cc21683) — relocated-store root is not normalized

`tools/souji-census.sh` 253–254: `PROTECTED_HOME_ROOTS+=("$pi/agent")` uses the raw
`PI_CONFIG_DIR` absolute form. `PI_CONFIG_DIR=/srv/creds/` produces `/srv/creds//agent` and
`PI_CONFIG_DIR=/srv/x/../creds` produces `/srv/x/../creds/agent`; `path_under` (216–221) matches
literally, and `protected_component_reason` only knows `.omp/agent` (314–316), so a store
relocated via `PI_CONFIG_DIR` is neither an input predicate hit (354) nor a walk hit (338).
Every sibling root at 261/263 is normalized; this one is not. Same for 280 (relative
`PI_CONFIG_DIR` with a canonical home). Not an r16 regression (cc21683 225–226 are identical).

Minimal patch (253–254, and 280 for the relative form):

```diff
-        /*) PROTECTED_HOME_ROOTS+=("$pi/agent") ;;
-        *) PROTECTED_HOME_ROOTS+=("$lex/$pi/agent") ;;
+        /*) PROTECTED_HOME_ROOTS+=("$(lexical_abs "$pi/agent")") ;;
+        *) PROTECTED_HOME_ROOTS+=("$(lexical_abs "$lex/$pi/agent")") ;;
@@ 280
-            *) PROTECTED_HOME_ROOTS+=("$can/$pi/agent") ;;
+            *) PROTECTED_HOME_ROOTS+=("$(lexical_abs "$can/$pi/agent")") ;;
```

---

## 5. F4 — low — a config-soft registered worktree is silently folded into `wt-dirty`

`tools/souji-census.sh` 1068–1071: r16 now treats `guard_git_surface "$cpath"` returning 1 as
`saw_dirty=1` with **no** `config-unsupported` stderr line, unlike the main-row path at
1087–1092. The doc (57–58) defines `wt-dirty` as "its own `git status --porcelain` is non-empty";
for this path status never ran, and `CFG_SOFT_REASON` set here is never printed. This is silent
degradation of exactly the kind R5 targets, one level down.

Minimal patch:

```diff
@@ 1068
     if ! guard_git_surface "$cpath"; then
+      printf 'souji-census: config-unsupported: %s (%s)\n' \
+        "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$cpath")" >&2
       saw_dirty=1
       continue
     fi
```

---

## 6. Residual risk (recorded, not defects; not exercised by the fixture)

- **Symlinked worktree-registration entry** (718–721): the link target is guarded and then the
  entry is skipped without reading its `gitdir`; a benign target whose `gitdir` names a store
  path is not checked before `git worktree list` (1076). Unchanged from cc21683; exotic.
- **Hardlinked / non-regular include target or `config.worktree`** (561–570) is soft by design
  (doc 95–96). It is the only "store-alias" class r16 turns into an `error` row; the file is not
  opened before the soft return, and the repo runs no git, so there is no read.
- **`protected_fail` masking** (185–190): `lexical_abs` reads only the first line of `$shown`, so
  for the newline/tab refusals at 379–381 / 418–420 the raw control-character path is still
  echoed to stderr (cosmetic; the fixture checks only `path-protected`).
- **06c/10/11 pin the *result*, not the ordering**: after F1 is fixed (or not), a one-line
  fixture addition — an `include.path = ~nobody/x` inside the gitdir that hosts the protected
  commondir/alternates — would make the hard-over-soft contract executable.
- **`census_one` 1097–1103**: the nested `if [ ! -e "$repo/.git" ]` is implied by its own outer
  condition (dead branch, pre-existing).
- r14's key-name blacklist (`include.*`, `filter.*`, `core.excludesFile`, … → hard refusal) is
  gone; the replacement is value/effect-aware, which is the declared C1 repair (doc 86–111), and
  for benign config it is strictly better. Nothing in this fixture distinguishes the two.

Verification gaps: per item, no execution — no `bash -n`, no fixture run, no matrix run, no
comparison against b410186/cc21683 behaviour. Every claim above is from reading the named
revisions; b410186 was extracted only to confirm the revision identities were available and was
not used. Tooling: no installs or upgrades were needed or performed.

STATUS: no defect found that changes any of the 12 case outcomes at cbf688a. F1 is the only
r16-introduced path that converts a namespace refusal into a soft `error` row, and it requires an
unevaluable config the fixture never creates (medium, exit-code/finding fidelity only, no store
read).

---

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/RevR14NamespaceRetention-census-r16.sh 2>&1; wc -l /var/tmp/RevR14NamespaceRetention-census-r16.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat --oneline; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r14-census-boundary.py | sha256sum
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py /var/tmp/RevR14NamespaceRetention-census-r16.sh; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse cbf688ab2ab28e38103e5a9417ca525b5f2ed423
cd /var/tmp && for r in cc21683 b410186 a31642d; do git -C /home/vgpnk/Projects/shokunin/souji-shokunin show $r:tools/souji-census.sh > RevR14-census-$r.sh 2>/dev/null; printf '%s ' $r; sha256sum RevR14-census-$r.sh; done; wc -l RevR14-census-*.sh
grep -n 'protected_fail\|cfg_soft\|CFG_SOFT_REASON\|guard_git_surface\|guard_git_config\|guard_worktree_registrations\|guard_config_file_kind\|guard_config_path\|guard_target\|guard_path\|resolve_guarded\|protected_reason_input\|protected_reason_inside\|protected_component_reason\|return 1\|exit 2' /var/tmp/RevR14NamespaceRetention-census-r16.sh
cd /var/tmp && diff -u RevR14-census-cc21683.sh RevR14NamespaceRetention-census-r16.sh > RevR14-diff-cc21683-r16.txt; wc -l RevR14-diff-cc21683-r16.txt; grep -n '^[-+][^-+]' RevR14-diff-cc21683-r16.txt | grep -cE '^-|^\+'
cd /var/tmp && grep -nE '^[+-].*(protected_fail|cfg_soft|return 1|guard_config_file_kind|guard_git_config|guard_worktree_registrations|guard_git_surface|status_info_file|guard_bound_filters|guard_config_path)' RevR14-diff-cc21683-r16.txt | head -120
diff -u /var/tmp/RevR14-census-cc21683.sh /var/tmp/RevR14NamespaceRetention-census-r16.sh > /var/tmp/RevR14-diff-cc21683-r16.txt; echo "diff rc=$?"; wc -l /var/tmp/RevR14-diff-cc21683-r16.txt; grep -nE '^[+-].*(protected_fail|cfg_soft|return 1|guard_config_file_kind|guard_git_config|guard_worktree_registrations|guard_git_surface|status_info_file|guard_bound_filters|guard_config_path|CFG_SOFT)' /var/tmp/RevR14-diff-cc21683-r16.txt
sed -n '1,100p' /var/tmp/RevR14-diff-cc21683-r16.txt
grep -n 'PI_CONFIG_DIR\|PROTECTED_HOME_ROOTS+=' /var/tmp/RevR14-census-cc21683.sh; echo '=== r16 ==='; grep -n 'PI_CONFIG_DIR\|PROTECTED_HOME_ROOTS+=' /var/tmp/RevR14NamespaceRetention-census-r16.sh
sed -n '240,360p' /var/tmp/RevR14-diff-cc21683-r16.txt
sed -n '360,497p' /var/tmp/RevR14-diff-cc21683-r16.txt
sed -n '88,200p' /var/tmp/RevR14-census-cc21683.sh | cat -n | sed 's/^/r14+87 /' ; echo '=== r14 guard_git_config full ==='; awk 'NR>=1{a=NR} /^guard_git_config\(\)/{print NR": "$0; f=1} f{print NR": "$0} f&&/^}/{exit}' /var/tmp/RevR14-census-cc21683.sh
awk 'NR>=715 && NR<=800 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=800 && NR<=845 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- main ---'; awk 'NR>=1760 && NR<=1784 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=1160 && NR<=1245 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=455 && NR<=480 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo ---; awk 'NR>=1246 && NR<=1275 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=863 && NR<=900 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- census_one ---'; awk 'NR>=1084 && NR<=1112 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=550 && NR<=600 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- roots ---'; awk 'NR>=236 && NR<=300 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=344 && NR<=360 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo ---; awk 'NR>=365 && NR<=445 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
grep -n 'credential-store\|operator-sweep\|operator-runtime\|path_overlaps\|path_under' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- 200-235 ---'; awk 'NR>=203 && NR<=235 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
test -d /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo W1DIR_OK || echo W1DIR_MISSING; test -e /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevR14NamespaceRetention.md && echo REPORT_EXISTS || echo REPORT_ABSENT
awk 'NR>=300 && NR<=330 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- blob vs worktree ---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=70 && NR<=120 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- fn boundaries ---'; grep -nE '^(guard_target|protected_reason_inside|guard_config_path|scan_config_file|guard_wt_config|guard_git_config|status_info_file|guard_bound_filters|count_dirty|scratch_bytes|newest_mtime|worktree_extra_flags|census_one|list_repos|emit_census|build_protected_roots)\(\)' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=446 && NR<=455 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- scan end ---'; awk 'NR>=640 && NR<=690 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=40 && NR<=68 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh; echo '--- case start ---'; awk 'NR>=596 && NR<=622 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=898 && NR<=980 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=1018 && NR<=1084 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
awk 'NR>=980 && NR<=996 {printf "%d: %s\n", NR, $0}' /var/tmp/RevR14NamespaceRetention-census-r16.sh
grep -n 'special-path\|doc 7\|doc 9\|doc 10\|doc 86\|doc 52\|1038\|874–901\|579–644\|601–644\|620–625\|935–955\|448–453\|977–991\|983–991\|955–975' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevR14NamespaceRetention.md
grep -n '52–58\|1038\|doc 97\|86–107' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/RevR14NamespaceRetention.md
```

No `tools/souji-census.sh` execution, no copy under `/var/tmp/souji-r16-*`, no test command from
the item (source inspection only); `/var/tmp` scratch files from the extraction were not deleted
because they are outside any seat-owned directory and were not test input to anything.
