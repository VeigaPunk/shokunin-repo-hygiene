STATUS: DONE — D2 control flow traced at 5fa6017; exact minimal patch delivered, static only (no census/fixture execution).

# ScoutAttrGuardFlow — `guard_git_files` reachability and the per-repo degrade for `info/attributes` (C1/D2)

Pin: lane HEAD `5fa6017ddcae9f6bd4412df44765f6360cb16294`; `tools/souji-census.sh` sha256
`64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (1877 lines), the C1 census bytes.
Mode: static recon only — no census, verify, vault-verify, quarantine or fixture run; no lane write except this report.
Probe compliance: only exact-file reads/greps and read-only `git rev-parse|log`, `sha256sum`, `stat`, `ls` (one fixture dir, non-recursive).

## 1. How `guard_git_files` (:519-535) is reached from each caller

Top level (normal census path): `main` falls through to `emit_census` (:1876) → `exit 0` (:1877).

```
emit_census (:1308)
├─ list_repos (:1257)                              # pre-pass, result discarded with `|| true`
│  ├─ :1266  guard_git_surface "$root"  (root .git file)   || true
│  ├─ :1269  guard_git_surface "$root"  (root .git dir)    || true
│  └─ :1299  guard_git_surface "$d"     (child .git dir)   || true
└─ census_one (:1174) per row
   ├─ :1177  guard_git_surface "$repo"
   └─ :1207  worktree_extra_flags (:1127) per `git worktree list --porcelain` entry
              └─ :1156  guard_git_surface "$cpath"
```

Inside `guard_git_surface` (:821-901), `local repo=$1 g="$1/.git" target common dir first soft=0` (:822),
`CFG_SOFT_REASON=""` (:823):

| # | line | branch | target guarded | reach condition |
|---|------|--------|----------------|-----------------|
| 1 | :831 | `.git` is a directory (`-d`, :828) | primary gitdir `$dir` | every dir-row repo |
| 2 | :849 | same branch, common gitdir | second `$dir` from `$dir/commondir` (:834-853) | only when `commondir` is a regular file naming a dir |
| 3 | :873 | `.git` is a file (`-f`, :859) | admin gitdir from the `gitdir:` pointer (:859-872) | **root-only** rows with a `.git` file; `list_repos` skips child `.git` files as rows (:1294-1297 `guard_git_pointer`, no `REPOS+=`) |
| 4 | :891 | same branch, common gitdir | admin's `commondir` target | same as #2 |
| 5 | :790 | `guard_worktree_registrations` (:766) | each linked worktree's admin gitdir `$admin` | called at :855 (dir branch) and :897 (file branch); admin comes from `$dir/worktrees/*/gitdir` → `<wt>/.git` → `gitfile_admin` (:795) |

Notes:
- `guard_git_surface` on a symlinked `.git` returns 0 before any files guard (`:824-827`); `census_one` then emits `not-a-repo` (:1184-1186). No row, no git call.
- `guard_git_pointer` (:757-760), used for child `.git`-file repos, never calls `guard_git_files`; those dirs are not rows and no git command runs on them.
- Guard order inside each branch is `links` → `files` → `config`; the worktree-admin path is `files` (:790) → `links` (:791) → `config` (:792).
- `guard_git_files` itself has no repo/worktree argument: only `$dir` (a gitdir, possibly a linked-worktree admin or a common dir outside the row directory) and `$path` ($dir/<rel>). It cannot name the census row.

## 2. `protected_fail` (:200-208) — what it does

```
PROTECTED_FINDING='path-protected'                       # :197
protected_fail() { # $1 reason, $2 label, $3 path        # :200
  local shown=$3
  if [ -n "$shown" ] && protected_reason_inside "$shown" >/dev/null 2>&1; then
    shown='<protected>'                                  # mask a protected path
  fi
  printf 'souji-census: %s: %s (%s: %s)\n' \
    "$PROTECTED_FINDING" "$1" "$2" "$shown" >&2          # :205-206
  exit 2                                                 # :207
}
```

It prints `souji-census: path-protected: <reason> (<label>: <shown>)` to stderr and terminates the whole
run with status 2. It never returns; `guard_git_files`' hardlink (:529), non-regular (:532) and
stat-unavailable (:526) calls all go through it today.

## 3. The r16 per-repo `error` row path (`config-unsupported`) — the pattern to reuse

Soft is a value, not an exit:

- `CFG_SOFT_REASON=""` (:580); `cfg_soft() { [ -n "$CFG_SOFT_REASON" ] || CFG_SOFT_REASON=$1; return 1; }` (:581-584) — first reason wins, always returns 1.
- `scan_config_file` (:608-692) / `guard_config_file_kind` (:587-596) / `guard_wt_config` (:696-711) translate an unevaluable config into `cfg_soft` and keep scanning, so a later protected reach still `exit 2` (:690, :731).
- `guard_git_config` (:715-733) returns 1 when soft (:731). `guard_git_surface` accumulates `soft=1` at :832/:850/:874/:892, :851/:893, :855/:897 and returns 1 at :899.
- Emission:
  - `census_one` :1177-1181: on `! guard_git_surface "$repo"` it prints
    `souji-census: config-unsupported: <reason> (<repo>)` and the row
    `<repo>\t0\t0\t0\t0\t\terror`, then `return 0`.
  - `worktree_extra_flags` :1156-1160: same diagnostic for `$cpath`, sets `saw_dirty=1` (the parent row gets `wt-dirty`; the worktree has no row of its own).
  - `list_repos` :1266/:1269/:1299 discard the soft return with `|| true` and print nothing.
- `emit_census` (:1308-1329) collects all rows; `census_one` returning 0 keeps the process at `exit 0` (:1877). Neighbours are unaffected because no `exit 2` occurs.
- `--compare` interaction: an `error` row is placeholders `0 0 0 0`, and `emit_compare` still computes numeric deltas for `worktrees|unpushed|dirty|scratch_bytes` (:1465-1466, the r16 S6 defect). D2 adds a second class of error rows; it does not fix S6.

## 4. Which later git calls for the same repo read `$GIT_DIR/info/attributes`

After a clean `guard_git_surface`, the same repo's calls are (`census_one` :1194-1208):

| call | site | reads `info/attributes`? |
|------|------|--------------------------|
| `git rev-parse --is-inside-work-tree` | :1194 | no |
| `git worktree list` | :917 | no |
| `git for-each-ref`, `git rev-list` | :923, :927, :931 | no |
| `git config --get` (`status_info_file`) | :944 | no (config only) |
| `git config -z --get-regexp` (`guard_bound_filters`) | :986-987 | no (config only) |
| `git ls-files -z --cached -- . ...` | :1002-1006 | **no as invoked** — plain cached listing reads no attributes; only attribute-reporting modes (`--eol`, `%(eol)`) do [INFERENCE from git-ls-files(1); man page present at `/usr/share/man/man1/git-ls-files.1.gz`, not decoded] |
| `git check-attr -z --stdin filter` | :1007-1008 | **yes** — the attribute stack, with `$GIT_DIR/info/attributes` at highest precedence; `-c core.attributesFile=…` overrides the global file, not this one |
| `git status --porcelain ...` | :1035-1041 | **yes** — path conversion/filter/eol/ident lookups; `--no-optional-locks` and `core.attributesFile` do not remove the per-repo source |
| `git worktree list --porcelain` | :1166 | no |

So the two calls that must be prevented are `check-attr` (:1007) and `status` (:1035); `ls-files`
(:1002) is safe only because no attribute-reporting flag is passed. `guard_git_files` runs `stat`
only — it never opens the file, so a FIFO is detected without blocking; today it then aborts the
whole fleet instead of skipping the repo. `git config --file` calls made by the guard itself
(:618, :621, :671) read config, not attributes.

## 5. Exact minimal control-flow change

Only two shapes change: `rel = info/attributes` with `nlink > 1`, and `rel = info/attributes` that
exists but is neither a regular file nor a directory. Everything else in `guard_git_files`
(`config HEAD index packed-refs commondir info/exclude objects/info/alternates`, the
`git-metadata-unavailable` stat failure, symlink-outside via `guard_git_links`) keeps `exit 2`.
Detection loops over all entries (`continue`, not `return`), so a later entry or a later protected
reach still aborts the run.

### 5.1 `guard_git_files` (:519-535)

```diff
-# Fixed git metadata that git reads directly must be regular or a directory;
-# a FIFO/device/socket is refused rather than opened or waited on.
-guard_git_files() { # $1 resolved gitdir
-  local dir=$1 rel path nlink
+# Fixed git metadata that git reads directly must be regular or a directory;
+# a FIFO/device/socket is refused rather than opened or waited on.
+# Round 17: a hardlinked or non-regular info/attributes does not abort the
+# fleet; it soft-degrades its repository (rc 1). Every other entry, and the
+# stat-unavailable shape, still refuses the whole run.
+guard_git_files() { # $1 resolved gitdir; rc 1 (soft) only for info/attributes
+  local dir=$1 rel path nlink soft=0
   for rel in config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates; do
     path="$dir/$rel"
     if [ -f "$path" ]; then
       nlink=$(stat -L -c %h -- "$path" 2>/dev/null || true)
       case "$nlink" in
         ''|*[!0-9]*) protected_fail "git-metadata-unavailable" "$dir" "$path" ;;
       esac
       if [ "$nlink" -gt 1 ]; then
-        protected_fail "git-metadata-hardlink" "$dir" "$path"
+        if [ "$rel" = "info/attributes" ]; then
+          git_meta_soft "git-metadata-hardlink" "$path"
+          soft=1
+          continue
+        fi
+        protected_fail "git-metadata-hardlink" "$dir" "$path"
       fi
     elif [ -e "$path" ] && [ ! -d "$path" ]; then
+      if [ "$rel" = "info/attributes" ]; then
+        git_meta_soft "git-metadata-nonregular" "$path"
+        soft=1
+        continue
+      fi
       protected_fail "git-metadata-nonregular" "$dir" "$path"
     fi
   done
+  [ "$soft" = 0 ] || return 1
+  return 0
 }
```

### 5.2 New soft channel, next to `cfg_soft` (:584)

```diff
 cfg_soft() { # $1 reason; always returns 1
   [ -n "$CFG_SOFT_REASON" ] || CFG_SOFT_REASON=$1
   return 1
 }
 
+# Git metadata that cannot be verified but reaches no protected root: the
+# repository is skipped (no git command that reads the file runs) and
+# emitted as one `error` row (round 17). Only info/attributes is routed
+# here; every other metadata entry still refuses the whole run.
+# First reason wins; guard_git_surface resets it.
+GIT_META_REASON=""
+GIT_META_PATH=""
+git_meta_soft() { # $1 reason, $2 offending path; returns 0
+  if [ -z "$GIT_META_REASON" ]; then
+    GIT_META_REASON=$1
+    GIT_META_PATH=$2
+  fi
+  return 0
+}
+
```

(`git_meta_soft` returns 0 deliberately: under `set -euo pipefail`, a bare function returning 1
inside the loop body would risk errexit; `soft=1` carries the state.)

### 5.3 Reset per repo/list, next to `CFG_SOFT_REASON` (:823)

```diff
 guard_git_surface() { # $1 repo dir
   local repo=$1 g="$1/.git" target common dir first soft=0
   CFG_SOFT_REASON=""
+  GIT_META_REASON=""
+  GIT_META_PATH=""
   if [ -L "$g" ]; then
```

### 5.4 Call sites — do not abort, bubble soft

```diff
@@ :790 (guard_worktree_registrations; local soft exists at :767)
-            guard_git_files "$admin" || exit 2
+            guard_git_files "$admin" || soft=1
@@ :831
-    guard_git_files "$dir" || exit 2
+    guard_git_files "$dir" || soft=1
@@ :849
-        guard_git_files "$dir" || exit 2
+        guard_git_files "$dir" || soft=1
@@ :873
-    guard_git_files "$dir" || exit 2
+    guard_git_files "$dir" || soft=1
@@ :891
-        guard_git_files "$dir" || exit 2
+        guard_git_files "$dir" || soft=1
```

All five `guard_git_files` call sites have a `soft` local in scope (`:767`, `:822`); no caller change
is needed in `guard_worktree_registrations` beyond the flag (final `:814` already returns 1).

### 5.5 Diagnostics + row emission

Add after `sanitize_field` (:905-910):

```
# One stderr line per soft cause. The fallback preserves the old
# `git-config-unsupported` line if a future soft path sets no reason.
soft_diagnostics() { # $1 row identity (repo or worktree path)
  local shown
  shown=$(sanitize_field "$1")
  if [ -n "$GIT_META_REASON" ]; then
    printf 'souji-census: git-metadata-unsupported: %s (%s)\n' \
      "$GIT_META_REASON" "$(sanitize_field "$GIT_META_PATH")" >&2
  fi
  if [ -n "$CFG_SOFT_REASON" ]; then
    printf 'souji-census: config-unsupported: %s (%s)\n' \
      "$CFG_SOFT_REASON" "$shown" >&2
  elif [ -z "$GIT_META_REASON" ]; then
    printf 'souji-census: config-unsupported: git-config-unsupported (%s)\n' \
      "$shown" >&2
  fi
}
```

Replace the two inline diagnostic blocks:

```diff
@@ worktree_extra_flags :1156-1160
     if ! guard_git_surface "$cpath"; then
-      printf 'souji-census: config-unsupported: %s (%s)\n' \
-        "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$cpath")" >&2
+      soft_diagnostics "$cpath"
       saw_dirty=1
       continue
     fi
@@ census_one :1177-1181
   if ! guard_git_surface "$repo"; then
-    printf 'souji-census: config-unsupported: %s (%s)\n' \
-      "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$repo")" >&2
+    soft_diagnostics "$repo"
     printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
     return 0
   fi
```

Byte-for-byte preservation for the existing r16 config cases: `soft_diagnostics` prints the same
`souji-census: config-unsupported: <reason> (<repo>)` line with the same `sanitize_field` input.
When both causes are present the helper prints two lines and still exactly one `error` row.

### 5.6 Header docs

Amend :86-88 (`these r14 git-metadata guards are unchanged by round 16 and still refuse the whole
run`) to state the single exception: a hardlinked or non-regular `$GIT_DIR/info/attributes`
degrades that repository to one `error` row, stderr
`souji-census: git-metadata-unsupported: <reason> (<path>)`, with no git command that reads the
file, while every other metadata entry and every protected reach still exits 2.
Amend the residual sentence at :125-128 likewise (`fixed git metadata, except info/attributes`).

## 6. Behavior matrix the change produces (for the r17 fixture)

| shape of `$GIT_DIR/info/attributes` | changed | 5fa6017 (r16) | pre-harm a31642d / r14-harm cc21683 |
|---|---|---|---|
| regular, 1 link (or absent) | measured row | measured row | measured row |
| regular, hardlinked (`os.link`, `cp -al`) | exit 0, one `error` row, `git-metadata-unsupported: git-metadata-hardlink (<.../.git/info/attributes>)`, neighbours measured, no `openat` of the file | exit 2 `path-protected: git-metadata-hardlink` | measured row (entry absent before b410186) |
| FIFO (or socket) | exit 0, one `error` row, `…: git-metadata-nonregular (<path>)`, prompt return | exit 2 `path-protected: git-metadata-nonregular` | no metadata guard; `status`/`check-attr` **open the FIFO and block** → fixture `run_tool` timeout 90s → rc 124 (a socket is the non-blocking non-regular alternative for the legacy arms) |
| hardlinked `config` / `HEAD` / `index` / `packed-refs` / `commondir` / `info/exclude` / `objects/info/alternates` | exit 2 | exit 2 | exit 2 (where the entry exists) |
| `info/attributes` symlink resolving outside its gitdir | exit 2 `git-metadata-symlink` (guard_git_links) | exit 2 | unchanged |
| `info/attributes` a directory | admitted (guard treats dirs as allowed), unchanged | admitted | admitted |

Fixture assertion shape: exit 0; stderr contains `git-metadata-unsupported`, the reason token, and
the absolute attributes path; exactly one row for the repo, fields `0 0 0 0`, empty mtime, flag
`error`; both neighbours keep accurate rows; strace shows no `openat(`/` open(` of the attributes
path (stat/access lines are expected — the guard stats). `--compare` will still print numeric
deltas against the placeholder zeros (S6, not in C1).

## 7. Caller identity table — where the row identity is (not) available

| site | function | row identity in scope | consequence |
|------|----------|----------------------|-------------|
| :790 | `guard_worktree_registrations($dir)` | **no** — `$dir` may be a common dir; `$wt` is the linked worktree path, the row's `$repo` is not passed | must only set `(reason, path)` and bubble `soft=1`; the parent row is emitted by `census_one` |
| :831 | `guard_git_surface($repo)` | **yes**, `$repo` (:822) | bubble; `census_one`/`worktree_extra_flags` emit |
| :849 | `guard_git_surface($repo)` | **yes** | bubble |
| :873 | `guard_git_surface($repo)` | **yes** | bubble |
| :891 | `guard_git_surface($repo)` | **yes** | bubble |
| :1177 (`census_one`) | row emitter | **yes**, `$repo` | `error` row + diagnostics |
| :1156 (`worktree_extra_flags`) | worktree emitter | `$cpath` (worktree path) and `$repo` param; the worktree has no row of its own | diagnostic + `wt-dirty` on the parent row |
| :1266/:1269/:1299 (`list_repos`) | pre-pass | repo path available but result discarded (`\|\| true`) | must not print; a second `guard_git_surface` per repo in `census_one` re-detects and emits once |

`guard_git_files` itself cannot reconstruct the row: `$dir` may be `…/.git/worktrees/<id>` (linked
admin) or a common dir that is not under the row directory (submodule/gitfile admin). That is why the
soft state carries the offending path and the emission happens only at :1156/:1177.

## 8. Residuals / unknowns

1. **Reason vocabulary / exact diagnostic** — this report proposes `git-metadata-unsupported:
   {git-metadata-hardlink|git-metadata-nonregular} (<path>)`, reusing the existing reason tokens
   (`protected_fail` vocabulary, also listed in `tests/fixtures/r15-census-config.py:999-1004`).
   The r17 fixture does not exist yet (`tests/fixtures/r17-census-hygiene.py` absent at 5fa6017), so
   this string is not pinned by bytes; if C1 chooses `hardlink`/`nonregular` or adds the repo label,
   only the two `printf` formats in `soft_diagnostics` change.
2. **`git-metadata-unavailable` on info/attributes** — kept `exit 2`: D2 names only hardlinked or
   non-regular. Softening it too is a one-line change with the same mechanism if the fixture asks.
3. **Linked worktree detected only in the `worktree_extra_flags` fallback** — the normal path already
   turns the parent row into `error`: `guard_git_surface` at :855/:897 runs
   `guard_worktree_registrations`, whose :790 soft bubbles up. The :1156 fallback only fires for a
   worktree `git worktree list` reports that the `$dir/worktrees/*` sweep skipped (e.g. a symlinked
   entry, :769-772); there the parent row gets `wt-dirty`, not `error` — conservative, and there is
   no per-worktree row to mark. Decide whether C1 requires an `error` there; it would need a third
   token from `worktree_extra_flags` and a flag mapping in `census_one`.
4. **TOCTOU** — the guard and git's later open are not one atomic operation. The soft path never
   opens the file, so a sample that is benign at guard time and swapped to a FIFO before
   `count_dirty` can still block `status`; this is the inherited non-atomic metadata residual
   (header :128), not introduced here.
5. **`info/attributes` a directory** — passes `guard_git_files` (`-d` exempts it) and is read by git;
   unchanged, not part of D2.
6. **Hardlinked `info/attributes` in a linked admin** is reached at :790 (files before links in that
   path); a symlink pointing outside is still refused by :791 immediately after, so the symlink
   refusal keeps exit 2.

## Commands run (read-only) and outputs

```text
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && sha256sum tools/souji-census.sh && git log --oneline -3 -- tools/souji-census.sh
5fa6017ddcae9f6bd4412df44765f6360cb16294
64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c  tools/souji-census.sh
0a70bef round-16: integrate wave-1 review fixes into census, config fixture and matrix runner (C1)
cbf688a round-16: restore parsing value/effect-aware census; execute and repair config fixture (C1)
b410186 round-15: land operator-stopped config repair candidates; acceptance unrun

$ stat -c '%n %F %s' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r17-census-hygiene.py
stat: cannot stat '…/tests/fixtures/r17-census-hygiene.py': No such file or directory (os error 2)

$ stat -c '%n %F %s' /usr/share/man/man1/git-ls-files.1.gz /usr/share/man/man1/git-check-attr.1.gz /usr/share/man/man5/gitattributes.5.gz
/usr/share/man/man1/git-ls-files.1.gz regular file 5134
/usr/share/man/man1/git-check-attr.1.gz regular file 1837
/usr/share/man/man5/gitattributes.5.gz regular file 16764
```

`tests/fixtures` listing (non-recursive): `case-F1..F10`, `r12-maintenance-guard.sh`,
`r13-cert-evidence.py`, `r13-cert-frozen`, `r13-quarantine-bounds.sh`, `r13-repo-structure.sh`,
`r14-cache-frozen`, `r14-census-boundary.py`, `r14-evidence-cache.py`, `r15-census-config.py`,
`r15-preservation-evidence.py`, `r15-preservation-frozen`, `r16-landing-gate.py` — no r17 fixture.
The man pages were not decoded (the `read` tool listed them as archives only); the `ls-files`
attribute nuance is therefore labelled inference.

Tool installs/updates: none (pacman not touched; no uv/npm/cargo install).

## Verdict

- **Fails (defect confirmed)**: at 5fa6017 a hardlinked or non-regular `$GIT_DIR/info/attributes`
  reaches `protected_fail` from :529/:532 via any of :790/:831/:849/:873/:891 and exits 2 for the
  whole fleet, violating C1/D2's per-repo degrade.
- **Holds (proposed patch, static)**: the diff in §5 is the smallest change that (a) softens only
  `info/attributes` hardlink/non-regular, (b) loops past the softened entry so every other entry and
  every protected reach still exits 2, (c) emits exactly one `error` row and one
  `git-metadata-unsupported: <reason> (<path>)` diagnostic per degraded row with exit 0, (d) runs no
  git command that reads the file (only `git config --file` in the guard remains), and (e) leaves
  existing `config-unsupported` bytes unchanged. It is unexecuted: no `bash -n`, shellcheck, fixture
  or matrix run was performed here, per the assignment.
- **Smallest fix**: apply §5.1-§5.5 (+ §5.6 docs); pin the diagnostic in the r17 fixture with the
  hardlink shape (all four arms discriminate) and the socket shape for the non-regular case if the
  legacy arms must not pay the 90s FIFO timeout.
