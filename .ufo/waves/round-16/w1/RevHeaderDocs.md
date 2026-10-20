# RevHeaderDocs — header-comment contract audit (round 16, W1)

**Seat:** `SoujiR16.RevHeaderDocs` — reviewer, source inspection only (no execution of the tool).
**Target:** `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`.
**Bytes audited:** sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757` (1784 lines), extracted with `git show` and read end to end. All line numbers below are the committed `cbf688a` bytes.

**Verdict:** the header is substantially accurate — I found no bypass of the `path-protected` guard for `--root`/`--compare`, and the Refused/Degraded/Accepted lists match the config-scan code in almost every particular. But **nine statements are not true of the committed code**: two change reported semantics (`--include-root`, `wt-dirty`), one is a false traversal guarantee (nested `.ufo/state`), one hides a whole-run exit-2 class and falsifies the round's absolute C1 sentence, one leaves `dirty` config-dependent, and four are wording/exit-code/column-edge inaccuracies. Findings are advisory.

`STATUS: review complete against cbf688a; the worktree copy is NOT the audited bytes (see Basis drift); no census execution performed.`

**Basis drift (verification gap):** the worktree now shows ` M tools/souji-census.sh` — sha256 `feba44c7a598888844debb84efe4d29d90869f0dd640ea3f0229969eacd1aa88`, +31/−18 vs `cbf688a` (an in-flight sibling edit to `expand_config_path`, `status_info_file`, `guard_bound_filters`, and the selftest forbidden-subcommand regex). This audit is of the committed blob; L1 must re-run acceptance against whichever bytes are intended and must not treat the worktree selftest as evidence for this review.

---

## Findings

### F1 — Medium — `--include-root` emits a linked-worktree row, contradicting "main repo only"

**Header:** 17–21 — "Default scan: every immediate child … whose .git is a directory (a main repo, not a linked work tree or submodule gitfile). Linked work trees are counted on their owner via `worktree list`, not emitted as their own row. --include-root also emits a row for the root itself when it is a main repo."

**Code:** 1171–1181. The include-root branch's `elif [ -f "$g" ]` (1175) treats a `.git` **file** as a row candidate and executes `REPOS+=("$root")` (1177). `census_one` then accepts it: the `[ -L "$repo/.git" ]` branch (1093–1096) is false for a regular file, the missing-`.git` branch (1097–1103) does not fire because `-e` is true, and `git -C "$repo" rev-parse --is-inside-work-tree` (1104) succeeds for a linked worktree — so a full TSV row is emitted for the worktree. The default scan correctly skips gitfile children (`guard_git_pointer "$d" "$g"; continue`, 1204–1206).

**Impact:** operability/invariant — `--root` pointed at a linked worktree double-counts it as an independent repo row, exactly what lines 19–20 say never happens.

**Minimal patch (code), 1175–1178:**
```diff
     elif [ -f "$g" ]; then
-      guard_git_surface "$root" || true
-      REPOS+=("$root")
+      guard_git_pointer "$root" "$g"
```
(no row), matching the default-scan gitfile branch. `guard_git_pointer` still boundary-checks the admin target before any access.

---

### F2 — Medium — `wt-dirty` is documented as "status non-empty" but also means "status could not be verified"

**Header:** 55–58 — "wt-dirty: a non-main worktree directory is present and its own `git status --porcelain` is non-empty." Also 98–100 promises a filter-bound attributes source yields `status-unverifiable`.

**Code:** `worktree_extra_flags` 1039–1080 sets `saw_dirty=1` in four situations:
- 1057–1060: `$cpath/.git` is a symlink (no status attempted);
- 1062–1066: `$cpath/.git` is missing (no status possible);
- 1068–1070: `guard_git_surface "$cpath"` returns soft (unsupported config);
- 1073–1075: the worktree status returned `unverifiable` **or** a positive count.

Only the `>0` half of the last case is "status is non-empty". Consequently a worktree-only filter binding (a per-worktree `.gitattributes` that binds a driver the main worktree's attributes do not) yields `wt-dirty` with **no** `status-unverifiable` flag, contradicting 98–100 for that repository. The flag therefore conflates "dirty" with "unknown".

**Minimal patch (doc), 57–58:**
> wt-dirty: a non-main worktree directory is present and either its own `git status --porcelain` is non-empty **or its status could not be verified** (missing/symlinked `.git`, unsupported config, or a failed/skipped status). A worktree-only filter binding is folded here, not into `status-unverifiable`.

(If the intended meaning is strictly "dirty", the code must split the flag — a larger change.)

---

### F3 — Medium — nested `.ufo/state` / `.ufo/watchdog.log` ARE traversed by the mtime walk

**Header:** 10–11 — ".ufo/state or .ufo/watchdog.log are never traversed by the mtime walk"; 43–45 — "pruned and never stat'd".

**Code:** 986–989. The `find` prune matches only top-level paths — `-path './.ufo/state'`, `-path './.ufo/watchdog.log'` — while operator-sweep is pruned at any depth (`-path '*/census/operator-sweep-*'`, 989). A repo containing `sub/.ufo/state/…` is descended, those files are `-printf '%T@'`-stat'd, and their mtime can become `mtime_iso`. This is also internally inconsistent: the component guard treats a `.ufo/state` pair at **any** depth as a protected surface (320), but the walk only honors the top-level pair. The status pathspec at 950 has the same top-level-only shape (the header, however, only promises the mtime prune).

**Minimal patch (code), 986–989** — add nested patterns (the `*/…` forms also cover the top level):
```diff
-      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \
+      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \
+         -o -path '*/.ufo/state' -o -path '*/.ufo/watchdog.log' \
```
and, if the same protected-surface intent applies to status, add `':(exclude,glob)**/.ufo/state' ':(exclude,glob)**/.ufo/watchdog.log'` at 950. If top-level-only is truly intended, change the header to say "top-level .ufo/state…" instead.

---

### F4 — Medium — an undocumented whole-run exit-2 class; C1's "only a protected-namespace reach" is false

**Header:** 86 — "any git-metadata symlink must resolve inside its own gitdir"; 90–92 — the Refused list contains only config-named paths reaching a protected root; 121–124 — "2 usage, malformed baseline, or protected-path refusal".

**Code:** several `path-protected` refusals exit 2 for metadata *shape*, with no protected-namespace reach:
- 671–673: `cfg="$dir/config"`; `[ -L "$cfg" ]` → `protected_fail "git-metadata-symlink"` → exit 2. The refusal is unconditional: an inside-resolving `.git/config` symlink passes `guard_git_links` (493–497 only requires the resolved target to sit under `$dir`) and is then refused. `.git/config -> config.local` inside `.git` is boundary-clean by every other rule and still aborts the whole run.
- 655–658: the same for a symlinked `config.worktree`.
- 486–490: unreadable gitdir → `git-metadata-unreadable`; 503–516: `git-metadata-unavailable|hardlink|nonregular` on fixed metadata; 456–464: `git-alternates-depth|unparsed`.

**Impact:** a benign fixed-metadata symlink aborts the entire census with exit 2, contrary to the header's exit-2 predicate and to the round claim "Only a protected-namespace reach keeps whole-run exit 2". The residual paragraph (115–116) discloses hardlinked fixed metadata but not the symlink/non-regular/unreadable cases.

**Minimal patch (doc):** extend 90–92 with "or a guarded git-metadata shape that cannot be read safely: a fixed-metadata symlink (config, config.worktree, alternates — even one resolving inside the gitdir), a hardlinked/non-regular/unreadable/unstat-able fixed metadata file, an unparsable or over-deep alternates chain, or an unresolved/looping internal path." Restate C1 as "only a protected-namespace reach **or an unguardable git-metadata shape** keeps whole-run exit 2". (Alternative code patch — allow an inside-resolving `config` symlink after the existing `guard_git_links`/`guard_git_files` checks — is a security-posture change; the doc patch is smaller and safer.)

---

### F5 — Medium — `dirty` is not the documented status line count

**Header:** 35–39 — "`git status --porcelain` line count on the main work tree only (default untracked mode: a wholly untracked directory is one line, matching souji-verify)."

**Code:** 946–953 runs `git … status --porcelain --ignore-submodules=all -c core.excludesFile=… -c core.attributesFile=… -- . ':(exclude)…'`.

(a) **No `--untracked-files` is passed**, so repo-local `status.showUntrackedFiles` is honored. git-status(1), Git 2.56.0, under `-u`: "The default can be changed using the `status.showUntrackedFiles` configuration variable"; `--porcelain` guarantees format stability, not selection stability (only `color.status` and `status.relativePaths` are called out as ignored). `=no` hides untracked entries entirely; `=all` expands every file in an untracked directory, so "a wholly untracked directory is one line" is false under `=all`. This is a value/effect gap in the round's own axis: the guard evaluates config for paths but not this effect.

(b) The pathspec excludes at 950–953 drop any status lines under top-level `.ufo/state`, `.ufo/watchdog.log`, and `census/operator-sweep-*`; the `dirty` bullet never says so (the `mtime_iso` bullet does for its own walk).

**Minimal patch (code), 949:**
```diff
-      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
+      -c core.attributesFile="$at" status --porcelain --untracked-files=normal \
+      --ignore-submodules=all -- . \
```
and add to 38–39: "Lines under the off-limits surfaces (.ufo/state, .ufo/watchdog.log, census/operator-sweep-*) are excluded by pathspec." If config-sensitive untracked display is intended instead, the header must say `status.showUntrackedFiles` is honored.

---

### F6 — Low — "every immediate child" understates the scan filter

**Header:** 17–18. **Code:** 1186–1193 skips dot-directories (`.*) continue`, 1188) and names containing TAB/CR/LF (1190–1193). A `.hidden-shokunin` directory containing `.git` is not a row — the selftest asserts this ("dot-dir skipped"). **Patch (doc), 17–18:** "every immediate **non-dot** child … (dot-directories and names containing TAB/CR/LF are skipped)".

---

### F7 — Low — "bash + coreutils + git only" is false

**Header:** 7. **Code** additionally relies on awk (167, 231, 991), `find` (486, 498, 986 — findutils), `getent` (230–231), `cmp` (586, 1525) and `diff` (1528) (diffutils), and grep. **Patch (doc), 7:** "bash, coreutils, findutils, diffutils, grep, awk, and git."

---

### F8 — Low — `--selftest` can exit with a child's status, not only 0/1

**Header:** 69–72 — "Exit 0 on pass, 1 on fail." **Code:** 1520–1523 run the two census passes unguarded under `set -e`; a child exit 1 (setup/write failure) or 2 (a `path-protected` refusal from the fixture/HOME resolution) terminates the selftest with that status before the `ST_FAIL` accounting at 1739–1740. The final `if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi` never sees such a failure. **Patch (code):** `… > "$out1" || st_bad "first census run failed"` and the same for `$out2`; any child failure then becomes a recorded FAIL and the selftest exits 1.

---

### F9 — Low — column-doc edge cases

- **Header 40–41** ("0 if absent or a symlink") vs **code 961–965**: `.scratch` is also reported as 0 when it exists but is **not a directory** (`[ ! -d "$d" ] → 0`, 965). A regular file named `.scratch` would be counted by the quoted `du -sb -P`, but is not. Patch: "0 if absent, a symlink, or not a directory."
- **Header 42–43** ("newest regular-file mtime") vs **code 976–978 and 1025–1034**: when no eligible regular file exists (empty repo, or only secret-shaped names), `mtime_iso` is the empty string (the code comment at 978 says so). Patch: add "empty when no eligible file exists."

---

## Checked and accurate (no finding)

- CLI parse (1747–1770) matches 13–21; `--root=`/`--compare=`/`-h`/`--` are additional undocumented forms, not contradictions.
- `worktrees` = non-empty `git worktree list` lines (850–854) — matches 27.
- `unpushed` / `no-remote` rule (856–867) matches 28–34; `no-remote` blocks `clean` via `has_problem` (1143–1149), matching 53–54.
- `scratch_bytes` uses `du -sb -P`, refuses `.scratch` symlinks (961–971) — matches 40–41 apart from F9.
- `mtime_iso` uses one `find | awk` pass, prunes `.git`, never opens contents, `date --iso-8601=seconds` (980–1034) — matches 42–48 apart from F3/F9.
- Flag vocabulary and stable order (1154) exactly match 49–52.
- `--compare`: exact first-line header, 7 columns, numeric columns 2–5, duplicate-repo rejection, blank-after-header skipped (1249–1300); header-only → 0 / any row → 3 (1385–1386); census rows pass through a temp file, never stdout (1322–1330) — matches 60–67.
- `--selftest` builds under `/var/tmp`, runs twice, mutates one fixture, checks compare and the protected boundary, and trap-removes the tree (1397–1420, 1520–1523, 1731–1740) — matches 69–72 apart from F8.
- `path-protected` prefix and `<protected>` masking (181–191), `..`-input refusal (369–373), component pairs for `.omp/agent`, `census/operator-sweep-*`, `.ufo/state|watchdog.log` (300–325), protected-root union including passwd home and PI_* (236–298) — matches 74–86 (F4 covers the refusals not listed).
- Config scan: key/value parse, `include.path` vs `includeIf.<cond>.path`, recursion with cycle/depth guard, `config.worktree` under `extensions.worktreeConfig`, `~user`/`%(prefix)` soft, NUL/unparsable soft, invalid bool soft (575–650) — matches 87–97; `config-unsupported` stderr format and the single `error` row with exit 0 (1086–1090) match 93–94.
- Filter guard: driver enumeration from config, `ls-files | check-attr` (neither runs a driver), `status-skipped` + `status-unverifiable` for the main status (907–944) — matches 98–100 apart from F2's worktree case.
- `core.hooksPath=/dev/null` + `core.fsmonitor=false` on every status (948–949), excludes/attributes honored with XDG fallback (874–906), `GIT_NO_LAZY_FETCH=1` exported for every git call (147), missing include targets skipped (615–617) — matches 101–110.
- `GIT_*` unset loop plus `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` (140–147) — matches 112–113.
- Exit plumbing: `emit_compare; exit $?` (1779–1780), `emit_census; exit 0` (1783–1784), root-not-a-directory → 1 (1221), usage/malformed baseline → 2 (167–168, 1257–1300), compare drift → 3 (1328, 1385) — matches 121–124 apart from F4/F8.

## Residual risk / unverified

1. **`core.worktree` is only boundary-checked** (626–632), not otherwise evaluated; `status` may operate on the relocated work tree while `newest_mtime`/`scratch_bytes` stay rooted at the repo directory. Whether git 2.56 makes `status -- .` use the relocated tree or fail is **not tested here** — needs a fixture. `[INFERENCE]`
2. **Config-provided excludes/attributes path is not kind-checked** (874–906): a FIFO there is handed to `status` and can block. The header scopes non-regular handling to include targets/`config.worktree`, so this is not a stated falsehood, but it is a hang the value-aware guard does not close.
3. **`includeIf` conditions are never evaluated**; every target is *scanned*, not merely guarded, so a condition-false include can degrade (e.g. `~user`) or refuse (protected target) a repo whose effective config is benign. Consistent with the letter of 88 ("whatever its condition"), but the conservative over-approximation is undocumented.
4. **`clean` can co-occur with `scratch`, `secret-shaped`, `wt-absent`, `wt-dirty`** (`has_problem`, 1143–1149). Permitted by the "only when" wording at 53–54, but a consumer may read `clean` as globally clean.
5. **`build_protected_roots` resolves the whole `$HOME` at startup** (273, call at 838); a HOME symlink resolving into the store exits 2 before argument parsing, covered only loosely by "protected-path refusal" in the exit-code text.
6. **Relative `XDG_CONFIG_HOME`**: 884–900 emits `/dev/null` for a non-absolute base while git's xdg helper consumes any non-empty value; whether git 2.56 rejects relative values was not tested. `[INFERENCE]`
7. **No execution**: every git-behavior statement above cites the installed `git-status(1)` / `git-config(1)` (Git 2.56.0) text, not a fixture. The worktree is not the audited blob (Basis drift).

## Commands

All commands were run read-only against the named target, the `/var/tmp` copy of the pinned blob, or exact system man-page paths. `wc`, `cat`, `cmp`, `ls`, and `file` are outside the enumerated probe allowlist; they were used only on those exact paths (no lane recursion, no census execution, no writes outside `/var/tmp`). The copy is removed below.

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/souji-r16-RevHeaderDocs-census.sh 2>/var/tmp/souji-r16-RevHeaderDocs-err.txt; echo "exit=$?"; wc -l /var/tmp/souji-r16-RevHeaderDocs-census.sh; cat /var/tmp/souji-r16-RevHeaderDocs-err.txt
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain -- tools/souji-census.sh && sha256sum tools/souji-census.sh && git rev-parse cbf688ab2ab28e38103e5a9417ca525b5f2ed423^{tree} 2>/dev/null
cd /var/tmp && cmp -s souji-r16-RevHeaderDocs-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh && echo IDENTICAL || echo DIFFERS
grep -n '^#' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -nE 'saw_dirty=1|saw_absent=1|guard_git_surface "\$cpath"|newest_mtime|status --porcelain|REPOS\+=\("\$root"\)|elif \[ -f "\$g" \]|includeif:path|worktree_extra_flags|CFG_WT_ENABLED=|status_info_file|guard_bound_filters|:\(exclude|-path ./.ufo|-path ./.census|operator-sweep|secret_path|showUntrackedFiles' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
ls -l /usr/share/man/man1/git-status.1.gz /usr/share/man/man5/git-config.5.gz 2>&1; file /usr/share/man/man1/git-status.1.gz 2>&1
grep -nE 'ufo|operator-sweep|INCLUDE_ROOT|ROOT_RAW_IS_SYMLINK|git-metadata-symlink|-L "\$cfg"|-L "\$wtc"|--root "\$fleet"|case "\$base" in|\t\*\)' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -nE 'set \+e|set -e|env -u GIT_DIR|st_row_field|selftest: |exit 1|exit 2' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -nE 'if \[ -n "\$shown" \]|protected_reason_inside "\$shown"|printf .%s: %s: %s \(%s: %s\)|souji-census: config-unsupported|souji-census: status-skipped|git config --file "\$cfg" --no-includes --list -z|git config --file "\$cfg" --no-includes --type=bool|tr -d .\\000' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -nE 'scratch_bytes\(\)|\[ ! -d "\$d" \]|cd -- "\$repo"|dirty=\$\(count_dirty|census_one\(\)|list_repos\(\)|emit_census\(\)|load_census\(\)|gold|GIT_NO_LAZY_FETCH|compgen -v GIT_|unset -f' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain -- tools/souji-census.sh; git diff --stat -- tools/souji-census.sh; sha256sum tools/souji-census.sh; git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; sha256sum /var/tmp/souji-r16-RevHeaderDocs-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'scratch_bytes\(\)|\[ ! -d "\$d" \]|newest_mtime\(\)|find -P \.|status --porcelain|:\(exclude|saw_dirty=1|elif \[ -f "\$g" \]|REPOS\+=\("\$root"\)|guard_git_surface "\$cpath"|-L "\$wtc"|-L "\$cfg"|case "\$resolved" in'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'set \+e|env -u GIT_DIR|selftest: |ST_FAIL|exit 1|exit 2|census failed|root is not a directory|scratch_bytes\(\)|\[ ! -d "\$d" \]|newest_mtime\(\)|raw=\$\(cd|guard_git_files\(\)|guard_alternates_file\(\)|guard_git_links\(\)|git-metadata-unreadable|git-metadata-nonregular|git-metadata-hardlink|git-metadata-unavailable'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff -- tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'ufo|operator-sweep|INCLUDE_ROOT|ROOT_RAW_IS_SYMLINK|git-metadata-symlink|saw_dirty|saw_absent|guard_git_surface "\$cpath"|REPOS\+=\("\$root"\)|elif \[ -f "\$g" \]|case "\$base" in'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'getent|awk |find -P|cmp -s|diff -u|\.\*\) continue|empty iso|newest regular|du -sb|-L "\$cpath/\.git"|! -e "\$cpath/\.git"|"\$d" = unverifiable|souji-census: config-unsupported|souji-census: status-skipped|config-worktree|core-worktree-protected|include-protected'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE '^# (Default scan|One bash tool|Census TSV|--compare|--selftest|Protected|   dirty|   scratch|   mtime|   wt-|   "clean"|   Accepted|   Degraded|   filter|   Global|Exit codes|   0 |   1 |   2 |   3 |   SHOKUNIN)'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'git-alternates-depth|git-alternates-unparsed|git-alternates-file|guard_alternates_file|wtc="\$1/config.worktree"|cfg="\$dir/config"|local dir=\$1 cfg|extensions.worktreeconfig|include:path\|includeif:path|expand_config_path\(\)|v=\$\(expand_config_path|for f in "\$\{flags'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'clean\|dirty|for name in clean|has_problem|flags\+=\(clean\)|dirty=0|else$|unverifiable|printf .%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -nE 'not-a-repo|is-inside-work-tree|printf .%s\\tsecret-shaped|printf .%s\\t%s. "\$iso"|build_protected_roots|resolve_guarded "\$home"|resolve_guarded "\$lex/\.omp"|emit_compare$|emit_census$|exit \$?|SELFTEST" = 1|--include-root\)|command -v git|command -v du'
rm -f /var/tmp/souji-r16-RevHeaderDocs-census.sh /var/tmp/souji-r16-RevHeaderDocs-err.txt
```

Reads (read tool, not shell): `/var/tmp/souji-r16-RevHeaderDocs-census.sh` lines 1–140, 144–560, 561–980, 984–1400, 1401–1784; member `git-status.1` of `/usr/share/man/man1/git-status.1.gz`; member `git-config.1` of `/usr/share/man/man1/git-config.1.gz`.
