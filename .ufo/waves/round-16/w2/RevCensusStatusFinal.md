# RevCensusStatusFinal — final source review: status_info_file / guard_bound_filters / count_dirty / worktree_extra_flags / census_one

Seat: `SoujiR16.RevCensusStatusFinal-4` (reviewer, leaf). Lane root
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Source review only; the census
and its detectors were **not executed** by this seat.

Target: `tools/souji-census.sh` at `a6ec7810e9b5` (assigned HEAD). While this
review ran, L1 advanced HEAD to `163158a706352f1c0ee3521c4da2e5289970db57`;
`git diff --stat a6ec7810e9b5 -- tools/souji-census.sh` is empty and the file
still hashes `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`,
so every line number below is valid at both commits. Line numbers are relative
to `tools/souji-census.sh` unless prefixed with another path.

Runtime context established from the tree, not assumed: bash
`5.3.20(1)-release` (`/var/lib/pacman/local/bash-5.3.20-1/desc`), git
`2.56.0` (`/var/lib/pacman/local/git-2.56.0-1/desc`). Git behaviour below is
grounded in git 2.56 source/documentation read via the `read`/`grep` tools
(paths cited inline). `bash -n` and `shellcheck -S info` (scoped to lines
935–1260) are clean; the recorded matrix
(`census/round-16/c1-matrix-final.json`, lane_head `0a70bef`; and
`c1-matrix-landing.json`, lane_head `7a79dc2`) reports r15-config 20/20,
r14-namespace 12/12, legacy selftest rc 0, shellcheck rc 0, with R15CFG-13
(`unbound filter` → clean) and R15CFG-14 (bound filter → `status-skipped`)
PASS. That is recorded evidence; this seat did not rerun it.

Verdict summary: the three safety-critical properties of the status path hold
— (1) a filter driver that an attributes source binds is never executed,
(2) a protected config-named reach still refuses the whole run, and (3) a
status that cannot be taken becomes `unverifiable` → `status-unverifiable`
rather than a fabricated count or a false `clean`. Four narrow defects remain
(F1–F4) plus one adjacent base-resolution defect outside the assigned five.

## F1 — LOW (in scope, `worktree_extra_flags`) — a worktree path containing a newline silently truncates; the guard intended to refuse it is unreachable

**Attacks:** the ambiguous-path guard at `:1136-1138`, the parsed worktree path
at `:1130-1134`, and the `worktrees` count at `:915-919`.

`git worktree list --porcelain` prints the path with a plain `%s` and no
quoting (`builtin/worktree.c:1010-1015`: `printf("worktree %s%c", wt->path,
line_terminator)`); `-z` is the NUL-separated machine form
(`builtin/worktree.c:1135-1151`). A filesystem-legal newline in a worktree
path therefore splits the record:

```
worktree /var/tmp/wt
x
<blank>
```

The census reads one line at a time (`:1130`), so `path=/var/tmp/wt`
(the nonexistent prefix), the line `x` is ignored, and
`case "$path" in ... *$'\n'* ...` at `:1137` **can never match** because
`read -r` already removed the only newline it can see. Consequences:
`[ ! -e "$cpath" ]` (`:1141`) is true for the truncated path, so the row gets
`wt-absent`; the real worktree directory is never stat'ed or statused, so a
dirty worktree is reported as an absent registration and its `wt-dirty`
signal is lost. The same path also adds a line to
`git worktree list | grep -c .` (`:917`), inflating the `worktrees` column
(the non-porcelain printer embeds `display->path` raw:
`builtin/worktree.c:1048-1084`).

**Minimal patch** (two lines; makes the existing guard live):

```bash
-  while IFS= read -r line || [ -n "$line" ]; do
+  while IFS= read -r -d '' line || [ -n "$line" ]; do
...
-  done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
+  done < <(git -C "$repo" worktree list --porcelain -z 2>/dev/null || true)
```

With `-z`, `path` retains the newline and `:1137` refuses it as
`ambiguous-path` (exit 2), matching the existing tab/CR policy. If a whole-run
refusal for a benign-but-weird path is judged too strong, the alternative is
a per-worktree skip plus a diagnostic (and a decision on which flag encodes
"present but unmeasured" — see F3); that is a policy choice, and the current
code has already chosen refusal for tab/CR.

**Verdict: fails** for newline-containing worktree paths; holds otherwise.

## F2 — LOW (in scope, `status_info_file`) — relative `XDG_CONFIG_HOME` and `HOME=""` diverge from git's effective file (w1 F5, still live)

**Attacks:** the XDG branch at `:960-969` against the header promise at
`:109-114` ("when unset the XDG default is honored if present and
boundary-clean").

Git 2.56's `xdg_config_home_for` (`path.c:1545-1558`) uses **any non-empty**
`XDG_CONFIG_HOME` verbatim, including a relative value, and falls back to
`$HOME/.config/git/<name>` only when it is unset/empty; the `$HOME` test is
pointer-based (`if (home)`), so `HOME=""` yields `/.config/git/<name>`. The
consumers open that path relative to the process cwd
(`dir.c:3486-3495` for `core.excludesFile`; `attr.c:884-888` and
`read_attr_from_file` for `core.attributesFile`), and every census status runs
`git -C "$wt"`, so cwd is exactly `$wt`.

The census instead maps a relative default to `/dev/null` (`:966-969`, the
`*)` arm) and treats `HOME=""` as unset (`:962`, `${HOME:-}`). Concrete
counterexample: export `XDG_CONFIG_HOME=rel`, put `rel/git/ignore` containing
`*` in repo `foo`, and an untracked file `u`. Plain
`git -C foo status --porcelain` prints nothing; the census resolves the
default to `/dev/null` and passes `-c core.excludesFile=/dev/null` (`:1036`),
counting `?? u` → `dirty=1`. The reverse direction (a relative
`rel/git/attributes` that git would read) is also dropped from both the guard
and status; that case is *not* an execution hole because the census pins the
same `/dev/null` into status, so the guard and status stay self-consistent —
the defect is row parity/coverage, not driver execution.

**Minimal patch** (the w1 RevStatusInfoFile F5 patch):

```bash
-    if [ -z "${HOME:-}" ]; then printf '/dev/null'; return 0; fi
+    if [ -z "${HOME+x}" ]; then printf '/dev/null'; return 0; fi
     base="$HOME/.config"
   fi
   tgt="$base/git/$leaf"
   case "$tgt" in
     /*) ;;
-    *) printf '/dev/null'; return 0 ;;
+    *) tgt="$wt/$tgt" ;;
   esac
```

`wt` is absolute, and under `-C "$wt"` it is git's cwd, which is the base git
itself uses for these relative opens.

**Coverage:** the revised fixture covers only the XDG-unset / absolute-HOME
default (`tests/fixtures/r15-census-config.py:599-605`, `r-xdg-default`); no
case sets a relative XDG or an empty HOME. (The M02 mutant that motivated that
case is now killed; the relative/empty forms remain unobserved.)

**Verdict: fails** for a relative `XDG_CONFIG_HOME` (and for `HOME=""` with a
readable `/.config/git/<leaf>`); holds for the documented common cases.

## F3 — LOW (in scope, `worktree_extra_flags`) — `wt-dirty` is emitted for worktrees whose status was never taken, contradicting its documented meaning

**Attacks:** `:1145-1165` against the flag contract at `:55-58` ("wt-dirty: a
non-main worktree directory is present and its own `git status --porcelain`
is non-empty").

`worktree_extra_flags` sets `saw_dirty=1` in four situations where status was
not run or did not succeed:

- `:1145-1149` — `.git` is a symlink (target guarded, then `saw_dirty=1`);
- `:1150-1155` — `.git` is missing (`saw_dirty=1` with no status);
- `:1156-1161` — `guard_git_surface` is soft (config cannot be evaluated;
  diagnostic printed, `saw_dirty=1`);
- `:1162-1165` — `count_dirty` returned `unverifiable`.

Concrete counterexample for the second: `git worktree add ../wt` then
`rm ../wt/.git`. `git worktree list --porcelain` still lists `/…/wt` (with a
`prunable` annotation), the directory exists, so the census emits `wt-dirty`
although no status ran. A `wt-dirty` consumer therefore cannot distinguish
"this worktree has changes" from "this worktree could not be measured"; the
direction is conservative (no false negative), so this is a contract/meaning
defect, not a safety defect.

**Minimal patch** (docs-only, smallest): replace `:57-58` with

```
#                   wt-dirty: a non-main worktree directory is present and is
#                     not known clean: its own `git status --porcelain` is
#                     non-empty, was skipped, or could not run (missing or
#                     symlinked .git, unsupported config).
```

A machine-readable distinction would need a new flag (e.g. `wt-unverified`)
for the three unmeasured branches; that is larger and changes the row
vocabulary, so it is not proposed as the minimal fix.

**Verdict: partial** — behaviour is safe/conservative; the documented meaning
is wrong.

## F4 — LOW (in scope, `census_one` + the `--include-root` feeder) — a linked-worktree/submodule gitfile root is measured as its own row

**Attacks:** `census_one`'s not-a-repo branches `:1183-1193` and the
`--include-root` branch of `list_repos` `:1261-1271` against the header
contract `:17-21` (rows are main repos; "Linked work trees are counted on
their owner via `worktree list`, not emitted as their own row";
`--include-root` emits the root "when it is a main repo").

`list_repos` adds the root when `<root>/.git` is a **file** (`:1265-1267`),
then `census_one` only rejects a `.git` symlink (`:1183-1186`) or a missing
`.git` (`:1187-1193`); a gitfile is neither, so it proceeds through
`rev-parse --is-inside-work-tree` (`:1194`) and is measured. Counterexample:
`tools/souji-census.sh --root /path/to/a/linked/worktree --include-root`
emits that linked worktree as a row (`worktrees`, `dirty`, `unpushed`,
flags), and the same holds for a submodule root. The two not-a-repo branches
are in fact **unreachable from the only caller**: `list_repos` admits children
only when `.git` is a directory (`:1298-1301`) and roots only via `-d`/`-f`,
and the root's `-L` arm appends nothing (`:1263-1264`), so `census_one` never
receives a `.git` symlink or a missing `.git` path.

**Minimal patch** (matches the header and keeps the guard):

```bash
     elif [ -f "$g" ]; then
       guard_git_surface "$root" || true
-      REPOS+=("$root")
```

If linked-worktree roots are intentionally supported, the alternative is to
update `:20-21` and add a fixture case; leaving the code and the contract
disagreeing is the defect. The now-dead `-L`/missing `.git` branches at
`:1183-1193` can then be deleted (or kept only as defence in depth with a
comment saying they are unreachable from `list_repos`).

**Verdict: fails** for `--include-root` on a gitfile root; the default child
scan and the `-d` root case hold (the fixture exercises the latter:
`tests/fixtures/r15-census-config.py:1041-1048` `unsafe_repo(...)` runs
`--root <repo> --include-root` on main repos).

## Adjacent observation (outside the assigned five) — `guard_worktree_registrations` resolves a relative `gitdir` against the common gitdir instead of the admin dir

**Attacks:** `:774-782`, in particular `:780` (`*) target="$dir/$target"`),
tracing `worktree_extra_flags`' precondition that registrations were
boundary-checked.

Git 2.56 with `extensions.relativeWorktrees` / `git worktree add
--relative-paths` writes the admin `worktrees/<id>/gitdir` content relative to
the **admin dir** (`repo_path` = `<common>/worktrees/<id>`;
`worktree.c:1105-1133`) and resolves it there (`worktree.c:152-167`). The
census resolves a relative content against `$dir` (the **common** gitdir,
`<repo>/.git`), two components shallower. For a worktree inside the tree
(e.g. `<repo>/.worktrees/wt`, relative content `../../../.worktrees/wt/.git`),
`<repo>/.git` + `../../../` lands at `<parent-of-repo>/.worktrees/wt/.git` —
a different path. The registration's real `.git` file is then not found, so
the admin's gitfile/config is not scanned by this pre-scan.

Reachability limits (why this is an observation, not a demonstrated exposure):
a **present** relative-linked worktree is still guarded by
`worktree_extra_flags` → `guard_git_surface` before its status, and that call
reads the worktree's `.git` file whose relative target is correctly resolved
against the worktree (`:867-870`); an **absent** worktree is never accessed, so
no command reads its admin `config.worktree`. I found no path where protected
content is actually read. The residual defect is a wrong guard target and a
possible false whole-run refusal if the mis-resolved path were to overlap a
protected root; no fixture or selftest case uses `--relative-paths` /
`extensions.relativeWorktrees`.

**Minimal patch:** `:780` → `*) target="$entry/$target" ;;` (`$entry` is the
admin dir `$dir/worktrees/<id>`).

## Verified holds (source-grounded, no defect)

- **`guard_bound_filters` `$!`/`wait` idiom (`:1002-1010`) is valid on the
  target bash.** Bash 5.3 NEWS: "Bash now allows waiting for the most recent
  process substitution, since it appears as `$!`" (bash-4.4 section) and
  "`wait -n` can now return terminated process substitutions"; the bash
  reference for `wait` says no-argument `wait` waits for "the last-executed
  process substitution, if its process id is the same as `$!`". The recorded
  matrix is consistent: R15CFG-13 (`r-filter-unused`, a configured but
  unbound driver) is `clean`, which requires `wait "$pid"` to return 0; a
  failed wait would have produced `status-unverifiable` and failed the case.
  The guard fails closed on producer failure and on a short record
  (`:1010-1011`); `set -o pipefail` inside the substitution makes `ls-files`
  failure surface through `wait` even when `check-attr` exits 0.
- **`guard_bound_filters` driver enumeration matches git's key model.**
  `git config -z --get-regexp '^filter\..*\.(clean|smudge|process)$'` returns
  `key\nvalue\0`; a key never contains a newline and the driver is the text
  between the first and last dots (git's section/subsection/key split), which
  is exactly what `:992-995` extracts. An explicit empty value
  (`key\n\0`) is skipped by `:991`; a value that merely ends in a newline is
  retained. Unbound drivers are inert because neither `ls-files` nor
  `check-attr` runs a filter.
- **`guard_bound_filters` and status read the same attribute sources.** The
  guard's `ls-files`/`check-attr` carry the same pathspec exclusions as the
  status call (`:1003-1006` vs `:1038-1040`) and the same
  `-c core.attributesFile` value; both commands run with `-C "$wt"`, so
  worktree `.gitattributes`, `$GIT_DIR/info/attributes` (now regular/nlink
  screened at `:521-534`) and the resolved XDG/configured file are identical.
- **`count_dirty` maps every outcome honestly.** `status_info_file` rc 3 →
  `unverifiable` (`:1023-1026`); any other nonzero → `exit 2` (protected);
  bound/unknown driver → `status-skipped` diagnostic + `unverifiable`
  (`:1027-1032`); status failure → `unverifiable` (`:1035-1044`); otherwise a
  line count. `census_one` turns `unverifiable` into `dirty=0` **plus**
  `status-unverifiable` (`:1224-1226`), so the placeholder is never presented
  as a clean measurement. `-c core.excludesFile`/`-c core.attributesFile`
  reconstruct exactly the file git would use, and the explicit value is
  absolute and tab/CR/newline-free (guard at `:542-546`).
- **`status_info_file`'s set-but-empty and `:(optional)` semantics match git
  2.56.** Explicit empty: `git_config_pathname` keeps a non-NULL empty
  pointer (`config.c:1319-1343`), and `repo_excludes_file` substitutes XDG
  only for NULL (`environment.c:155-163`); the census returns `/dev/null`
  (`:945`) = "no file", matching. `:(optional)` + missing: git sets the
  pointer to NULL (`config.c:1327-1336`), which re-enables the XDG default
  (`environment.c:155-163`; `attr.c:884-888`); the census strips the prefix at
  `:947`, tests `-e` at `:951`, and falls through to the same XDG branch.
  A non-regular target is refused (`:953-957`) so status cannot block on a
  FIFO/device. A protected value exits 2 through `guard_config_path`
  (`:948-949`), printed as `path-protected` by `protected_fail`
  (`:200-208`).
- **Relative config values use git's base.** `status_info_file` expands with
  `$wt` (`:947`) and all consumers run `-C "$wt"`, so a relative
  `core.excludesFile`/`core.attributesFile` resolves to the same file git
  opens (cwd = `$wt` under `-C`). Only the XDG default's relative form
  diverges (F2).
- **A bare pathname key cannot cause a fabricated row.** With no `=`, git's
  callback returns `config_error_nonbool` for `core.excludesFile` (value
  NULL) and `configset_iter` dies on the negative callback return
  (`config.c:1324-1325`, `1670-1685`); the census's status therefore fails
  and becomes `unverifiable`, even though `status_info_file` reads the bare
  key as empty and passes `-c /dev/null` (the earlier value's error is
  processed first, before the command-scope override).
- **`census_one`'s flag vocabulary/order is consistent with the header
  (`:49-58`, `:1233-1250`)**: `clean` only when unpushed=0, dirty=0 and a
  remote ref exists; `status-unverifiable` suppresses `clean`; `error` and
  `not-a-repo` rows are emitted with zeroed numeric placeholders and empty
  mtime as documented.
- **`worktree_extra_flags` sees absolute paths from `git worktree list
  --porcelain`.** `get_linked_worktree` turns relative linking files into an
  absolute `worktree->path` (`worktree.c:71-76`, `152-167`) and porcelain
  prints that path (`builtin/worktree.c:1010-1015`), so `guard_target` and
  the equality test against the resolved main repo are sound; the main
  worktree is skipped (`:1140`), and a missing directory is handled without
  status (`:1141-1144`).

## Residual risk (advisory; not counted as findings)

1. **Hardlink aliases for config-named attributes/excludes.** `status_info_file`
   checks `-f` but not link count; a hardlink at a boundary-clean path to an
   operator-owned file would be read as patterns by `check-attr` and status.
   The header residual acknowledges "arbitrary hardlinks into a store", but
   `.git/info/attributes` *is* nlink-screened (`:521-534`), so the class is
   handled inconsistently. Smallest hardening: reuse the nlink test from
   `guard_config_file_kind` (`:587-596`) on the resolved target and return 3
   when `> 1`.
2. **`:(optional)` with an empty target** (`core.excludesFile = :(optional)`)
   resolves to the worktree directory and returns 3 (`unverifiable`); git treats
   the empty path as missing → XDG default. Obscure; over-degrades one row.
3. **`|| exit 2` in `census_one` (`:1205`, `:1207`)** rewrites any nonzero
   return from `count_dirty`/`worktree_extra_flags` to the protected-refusal
   exit code with no `path-protected` diagnostic. Their only intentional
   nonzero return is 2, but an unexpected shell failure or a signal would be
   mislabelled. `|| exit $?` preserves the real code.
4. **`clean` co-occurs with `wt-dirty` / `wt-absent` / `secret-shaped`** by the
   header's own `clean` rule (`:53-54`, `:1233-1239`). This is per contract,
   but a consumer that treats the substring `clean` as "nothing to do" can
   misread a row whose linked worktree is dirty or whose registration is
   absent.
5. **Untested edges:** no fixture/selftest case for newline worktree paths
   (F1), relative XDG / empty HOME (F2), `--include-root` on a gitfile root
   (F4), or `--relative-paths`/`extensions.relativeWorktrees` (adjacent note).
   The fixture's `--include-root` uses only main repos with `.git` dirs.

## Verification gaps

- No census, fixture, or selftest execution by this seat (no `ALLOWED-EXEC`
  for this item; the probe rule forbids running `tools/souji-census.sh` on a
  real directory). Claims about git are read from git 2.56 source/docs; claims
  about bash `$!`/`wait` are from the shipped bash 5.3.20 docs plus the
  recorded matrix, not from a local probe.
- No live repository with a relative `XDG_CONFIG_HOME`, a newline worktree
  path, or relative worktrees was available; counterexamples are constructed
  from the source semantics above.
- The matrix JSONs record `lane_head` `0a70bef`/`7a79dc2`; the census bytes
  are identical to the assigned `a6ec781`/current `163158a`, which I verified
  by hash and empty diff.

STATUS: PARTIAL — core operability holds (bound filters never execute;
protected reaches refuse; unmeasurable status never becomes a false count or a
false clean). F1 (newline worktree path truncation), F2 (relative
`XDG_CONFIG_HOME`/empty HOME), F3 (`wt-dirty` meaning) and F4 (`--include-root`
gitfile row) are live and narrow; the relative-`gitdir` guard base is an
adjacent, untested defect outside the assigned five.

## Commands

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only HEAD | grep -E 'souji-census|round-16' | head -50
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ 2>/dev/null || echo NO_W2_DIR
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | wc -l && git show HEAD:tools/souji-census.sh | sha256sum && git log --oneline -5 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n '^[a-zA-Z_]*()'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && git status --porcelain -- tools/souji-census.sh && git diff --stat HEAD -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '900,1060p' | nl -ba -v900
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1060,1260p' | nl -ba -v1060
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '540,600p' | nl -ba -v540
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w1/RevStatusInfoFile.md .ufo/waves/round-16/w1/RevBoundFilters.md .ufo/waves/round-16/w1/MutateDirtyFilters.md 2>/dev/null; grep -n 'pid\|\$!\|wait ' .ufo/waves/round-16/w1/RevBoundFilters.md .ufo/waves/round-16/w1/MutateDirtyFilters.md 2>/dev/null | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain | head -40 && git ls-tree -r --name-only HEAD | grep -E 'fixtures/(r15|r16)|round-16/(run-matrix|c1-matrix)'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1,181p' | nl -ba
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '189,260p;381,460p' | nl -ba -v189
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '257,380p' | nl -ba -v257
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n 'guard_config_path\|status_info_file\|guard_bound_filters\|filter\.'
ls -d /usr/share/doc/bash* 2>/dev/null; ls /usr/share/doc/bash 2>/dev/null; ls /var/lib/pacman/local/bash-*/desc 2>/dev/null
grep -n "process substitution" -B2 -A4 /usr/share/doc/bash/COMPAT | head -60
grep -n -i "process substitution" /usr/share/doc/bash/bashref.html | head -20
grep -n -i "appears as\|process substitution" /usr/share/doc/bash/bash.html | head -20
grep -m1 -A2 '^%VERSION%' /var/lib/pacman/local/git-*/desc 2>/dev/null || ls -d /var/lib/pacman/local/git-* 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'filter\|attributes\|excludes\|optional\|XDG\|xdg' | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n ':(optional)\|optional' | head -20; echo ---; git show HEAD:tests/fixtures/r15-census-config.py | sed -n '560,615p' | nl -ba -v560
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'wt-dirty\|wt-absent\|status-unverifiable\|clean' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '598,700p' | nl -ba -v598
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## \|^\*\*Where\|^**Minimal\|^STATUS\|VERDICT\|verdict' .ufo/waves/round-16/w1/RevStatusInfoFile.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' .ufo/waves/round-16/w1/RevStatusInfoFile.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '60,175p' .ufo/waves/round-16/w1/RevStatusInfoFile.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '457,540p;715,760p' | nl -ba -v457
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '766,905p' | nl -ba -v766
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for f in ['census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json']:
    d=json.load(open(f))
    print('==',f)
    print(type(d), list(d)[:10] if isinstance(d,dict) else len(d))
" 2>&1 | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'case_13\|case_14\|ok\|problems\|filter-unused' census/round-16/c1-matrix-landing.json | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-landing.json'))
print('changed',d['changed']); print('invalid',d['invalid_suites']); print('bash',d['bash_version'],'git',d['git_version'],'head',d['lane_head'])
for a in d['arms']:
    if 'filter' in json.dumps(a) or a.get('suite','').startswith('r15'):
        print(a.get('suite'), a.get('id'), a.get('detail'))
" 2>&1 | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-landing.json'))
print(json.dumps(d['arms'], indent=1)[:3000])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --verify 7a79dc2d6e282654b9379c391c4c6be985ccf92c^{commit} 2>&1; git log --oneline -3 -- census/round-16/c1-matrix-landing.json; git show --stat --oneline HEAD | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -4 && sha256sum tools/souji-census.sh && git diff --stat a6ec7810e9b5 -- tools/souji-census.sh; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for f in ['census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json']:
    d=json.load(open(f)); print('==',f,'head',d['lane_head'],'bash',d['bash_version'])
    ch=d['changed']
    print('arms:',list(ch))
    rc=ch.get('r15-config',{})
    print('r15-config total',rc.get('total'),'failed',rc.get('failed'))
    for k in ('R15CFG-13','R15CFG-14','R15CFG-19','R15CFG-20'):
        if k in rc.get('cases',{}): print(k, rc['cases'][k])
    print('r14 failed',ch.get('r14-namespace',{}).get('failed'),'legacy',{k:(v.get('rc'),v.get('failed')) for k,v in ch.items() if 'legacy' in k or 'selftest' in k})
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for f in ['census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json']:
    d=json.load(open(f)); print('==',f,'head',d['lane_head'],'changed=',d['changed'])
    a=d['arms']; print('arm keys:',list(a))
    for suite,v in a.get('changed',{}).items():
        if isinstance(v,dict):
            print(' ',suite,'total',v.get('total'),'failed',v.get('failed'),'rc',v.get('rc'))
            for k in ('R15CFG-13','R15CFG-14'):
                if 'cases' in v and k in v['cases']: print('   ',k,v['cases'][k])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '1230,1320p' | nl -ba -v1230
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a a6ec781 -- tools/souji-census.sh | grep -n '^@@' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a a6ec781 -- tools/souji-census.sh | awk '/^@@/{h=$0} /guard_bound_filters|status_info_file|count_dirty|worktree_extra_flags|census_one|pid=|wait |mapfile \+/{print h; print}' | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688a a6ec781 -- tools/souji-census.sh | sed -n '399,520p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '990,1060p' | nl -ba -v990
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'def unsafe_repo\|def positive_problems\|def single_positive\|CONFIG_REASONS'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n 'census_one\|include-root\|INCLUDE_ROOT\|run_selftest\|--selftest' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1700,1760p' | nl -ba -v1700
cd /home/vgpnk/Projects/shokunin/souji-shokunin && shellcheck -S info -f gcc tools/souji-census.sh 2>&1 | awk -F: '$2>=935 && $2<=1260' | head -40; echo "---rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && bash -n tools/souji-census.sh; echo "bash -n rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '700,760p' | nl -ba -v700
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '1128,1175p' | nl -ba -v1128
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '757,830p' | nl -ba -v757
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'XDG\|HOME' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '240,300p' | nl -ba -v240
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | sed -n '586,610p' | nl -ba -v586
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '^## \|SURVIV\|surviv\|MEDIUM\|HIGH\|LOW\|STATUS' .ufo/waves/round-16/w1/MutateDirtyFilters.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,45p' .ufo/waves/round-16/w1/MutateDirtyFilters.md
true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tests/fixtures/r15-census-config.py | grep -n 'include-root\|relative-paths\|relativeWorktrees\|\\n.*wt\|newline' | head -20; echo ---; git show HEAD:tools/souji-census.sh | sed -n '55,58p;1160,1171p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '1127,1140p' | nl -ba -v1127
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sed -n '915,919p' | nl -ba -v915
```

Non-shell source reads (for the git/bash semantics cited above): git 2.56.0
`config.c` (`:1310-1350`, `:1555-1700`), `environment.c` (`:115-170`,
`:355-500`, `:740-780`), `path.c` (`:690-775`, `:1540-1570`), `wrapper.c`
(`:798-814`), `abspath.c`, `attr.c` (`:693`, `:875-900`, `:925-945`), `dir.c`
(`:3486-3495`), `builtin/commit.c` (`:1451-1530`), `builtin/config.c`
(`:538-650`), `builtin/worktree.c` (`:1010-1086`, `:1130-1151`),
`worktree.c` (`:71-76`, `:152-167`, `:1105-1133`), and
`Documentation/config.adoc` (`:414-416`) via `read`/`grep` on
`https://raw.githubusercontent.com/git/git/v2.56.0/<path>`; bash 5.3.20
`/usr/share/doc/bash/bashref.html` (`wait`, special parameters),
`/usr/share/doc/bash/NEWS` (process substitution 4.4/5.3 sections) via
`read`/`grep`; one `web_search` for bash 5.3 process-substitution NEWS.
No tools were installed or updated.
