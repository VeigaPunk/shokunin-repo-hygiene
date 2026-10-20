# ScoutSafeDirectory — safe.directory / dubious ownership (round 16, wave 2)

- Seat: `SoujiR16.ScoutSafeDirectory-4` (leaf; no edits outside this report)
- Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Lane HEAD: `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`
- Target: `tools/souji-census.sh`, sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` — matches the committed `0a70bef` blob and the `HEAD` blob; `git diff` for the path is empty.
- Host git: `2.56.0`; docs page read is the 2.56.0 revision.

## Attack

The wave-1 claim that clearing global/system git config is operationally harmless, specifically
`corpus/lessons/round-16.md:75`, which lists `safe.directory` among the "benign layouts" the census
contracts but does not say what a repository owned by another uid produces.

## Verdict: **partial**

Run-level operability holds: the census does **not** abort, does **not** call such a repository
clean, and exits 0. Measurement-level operability is lost: every foreign-owned repository becomes a
zero-placeholder `error` row with **no stderr cause**, and `--compare` can render that loss as
numeric drift. The lesson already submits the contraction to operator adjudication; this seat
confirms the exact mechanism and the row-level gap.

## Observed — Git semantics (docs, access 2026-10-20)

- `safe.directory` is **protected-scope-only**, not global-only:
  "Protected configuration refers to the *system*, *global*, and *command* scopes."
  — <https://git-scm.com/docs/git-config#SCOPES>
- "This config setting is only respected in protected configuration"
  — <https://git-scm.com/docs/git-config#Documentation/git-config.txt-safedirectory>
- Default refusal: "By default, Git will refuse to even parse a Git config of a repository owned by
  someone else" (same URL; 19 words).
- "Git only allows you to access repositories owned by yourself, i.e. the user who is running Git,
  by default." (same URL; 22 words).
- `GIT_CONFIG_GLOBAL`: "Can be set to `/dev/null` to skip reading configuration files of the
  respective level." — <https://git-scm.com/docs/git#Documentation/git.txt-codeGITCONFIGGLOBALcode>
- Under `sudo`, "git checks the `SUDO_UID` environment variable that sudo creates" (same git-config
  URL; 10 words), so a root-run census also trusts the invoking uid.
- Command scope includes the environment-pair channel: `CONFIG_SCOPE_COMMAND (e.g. "-c" option,
  environment variables)` — <https://github.com/git/git/blob/master/config.c> (10 words).

## Observed — Git implementation

- `ensure_valid_ownership()` consults `git_protected_config()` only:
  <https://github.com/git/git/blob/master/setup.c> lines 1413-1443; the protected reader sets
  `.ignore_repo = 1, .ignore_worktree = 1`
  (<https://github.com/git/git/blob/master/config.c> lines 2462-2482). A repository-local
  `safe.directory` therefore cannot rescue a repo, and an `include.path` from repo scope cannot
  either (the include inherits repo scope).
- The refusal is `die_upon_dubious_ownership()` (setup.c 1445-1462) and the
  `GIT_DIR_INVALID_OWNERSHIP` case of `setup_git_directory_gently()` (setup.c 1983-1995).
- `git rev-parse --is-inside-work-tree` calls `setup_git_directory()` unconditionally once an
  argument needs a repository
  (<https://github.com/git/git/blob/master/builtin/rev-parse.c> lines 770-772), so it takes the
  refusal path; it does not print `false` in a dubious repo.
- `git config` is `RUN_SETUP_GENTLY` and `--file` avoids repository discovery
  (<https://github.com/git/git/blob/master/git.c> line 563; `builtin/config.c` 943-1002), so the
  census's config guard still reads a foreign-owned `.git/config`; it does not itself trip the
  ownership check.

## Observed — live probe (read-only; lane repo only)

With Git's own `GIT_TEST_ASSUME_DIFFERENT_OWNER=1` (consulted at setup.c 1419) plus the census's
exact env (`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1`):

| invocation (all `git -C <lane> rev-parse --is-inside-work-tree`) | result |
|---|---|
| no exception | `fatal: detected dubious ownership in repository at '<lane>'`, rc 128 |
| `-c safe.directory='*'` | `true`, rc 0 |
| `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='*'` | `true`, rc 0 |
| `-c safe.directory=<lane>` | `true`, rc 0 |
| `-c safe.directory=<lane>/*` | still fatal (the `/*` form matches children, not the repo path itself) |
| `-c safe.directory=<lane>/../*` (i.e. `parent/*`, lane is a child) | `true` |
| `-c safe.directory=<parent>` | still fatal (parent does not cover children) |
| `-c safe.directory=/nonexistent` | still fatal |

This is the same command-scope channel the census already uses for `core.fsmonitor` and
`core.hooksPath` (`tools/souji-census.sh:162-163`). Caveat: the test knob forces the foreign-owner
branch; the real branch differs only in the explanatory `report` text, which the census discards.

## Observed — census at HEAD (exact lines)

- `tools/souji-census.sh:149-153` clears every inherited `GIT_*` variable, then exports
  `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`.
- `:161-163` adds `GIT_NO_LAZY_FETCH=1` and exactly two command-scope pairs
  (`core.fsmonitor=false`, `core.hooksPath=/dev/null`): `GIT_CONFIG_COUNT=2`. There is **no**
  `safe.directory` anywhere in the file (exact-file grep; also no `GIT_CONFIG_PARAMETERS`).
- `:1194-1196` is the first repository-touching git call:
  `git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1`; on failure it prints
  `path<TAB>0<TAB>0<TAB>0<TAB>0<TAB><empty><TAB>error` and returns 0. `emit_census` appends the row
  and only exits non-zero on rc 2 (`:1305-1313`), so the whole run continues with exit 0.
- `:95-100` documents `error` rows as the **config-unsupported** outcome, with stderr
  `souji-census: config-unsupported: <reason> (<repo>)`. The rev-parse path prints no stderr, so
  the ownership cause is outside the documented cause set and the operator cannot distinguish it
  from a config refusal without re-running git by hand.
- `:1236-1245` gives `error` `has_problem=1`, so the row is never marked `clean` — the safe part.
- `--compare` (`:1439-1483`) compares all six fields; a measured→error transition emits numeric
  deltas such as `dirty 7→0 -7`, `worktrees 4→0 -4`, plus `verdict_flags …→error`. The flags line
  discloses the change, but the numeric deltas read as work loss rather than lost measurement.
- Adjacent boundary, not caused by `safe.directory`: if a foreign-owned `.git` contains a directory
  the scanner cannot read, `guard_git_links` (`:500-508`) calls
  `protected_fail "git-metadata-unreadable"` → exit 2 for the whole run. That is the r14 permission
  guard; it fires for same-owner repos with unreadable metadata too.

## History

- `a31642d` (r14) did not set `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` at all (exact-blob grep: no
  `GIT_CONFIG_*`), so an operator's global `safe.directory` would have been honoured.
- `b410186` (r15) and HEAD both disable global/system; neither carries a command-scope
  `safe.directory`.
- `tools/souji-census.impl-46.sh:107-112` (round 6) wrapped calls with `-c safe.directory='*'`, so
  the r14/r15 rewrite dropped the only exception channel.
- No test covers ownership: exact named files `tools/souji-census.sh`,
  `tests/fixtures/r15-census-config.py`, `census/round-16/run-matrix.py` contain no
  `safe.directory`/`dubious`/`ASSUME_DIFFERENT_OWNER`. The fixture *pins* `GIT_CONFIG_GLOBAL=/dev/null`
  as containment (`tests/fixtures/r15-census-config.py:296,1343-1357`) but never asserts the
  ownership outcome; the census selftest has no `chown` and cannot create a foreign-owned repo
  without root. The matrix runner copies `tools/souji-census.sh` (`census/round-16/run-matrix.py:98-105`),
  i.e. it exercises the no-exception version.

## Concrete counterexample

A world-readable repository owned by uid 0 under a root scanned by uid 1000. Discovery is file-only
(`list_repos`, `:1260-1300`), `guard_git_surface` succeeds, then `:1194` dies with dubious
ownership; the emitted row is `<repo> 0 0 0 0 "" error` with empty stderr. A `--compare` against a
baseline taken as root (or by `impl-46`) reports per-field numeric drift for every such repo. The
run itself still exits 0 and later rows are still emitted.

Inference, not observed: running the census as root without `SUDO_UID` (plain `su`) inverts the
set — user-owned repos become "foreign" and every one becomes an `error` row; under `sudo`,
`SUDO_UID` makes the invoking user's repos acceptable again.

## Smallest fix

1. **Doc (zero behaviour change, smallest):** extend the `error` cause list at
   `tools/souji-census.sh:95-100` with "or `git rev-parse` refused the repository (dubious
   ownership: worktree/gitdir owner is not the invoking uid, and no command-scope `safe.directory`
   exception; that path prints no stderr)". Record in the same place that this is the residual the
   lesson files for operator adjudication.
2. **Cause visibility (one small edit):** capture the stderr of `:1194`
   (`err=$(git … 2>&1 >/dev/null)`) and, when it contains `dubious ownership`, print
   `souji-census: ownership-refused: <repo>` via `sanitize_field` before the row. This removes the
   config-unsupported/ownership conflation without relaxing trust.
3. **Only if the operator rules foreign-owned repos in scope:** after `root=$(guard_path root
   "$ROOT")` in `emit_census` (and therefore `emit_compare`), add two command-scope pairs —
   `safe.directory=<resolved-root>` and `safe.directory=<resolved-root>/*` — growing
   `GIT_CONFIG_COUNT` from 2 to 4. The exact entry is needed because `/*` does not match the root
   repo itself (verified); `/*` does match direct children (verified). This is a deliberate trust
   expansion; `safe.directory=*` (impl-46 behaviour) is broader than the scanned root. Do not add it
   silently. A naive edit at `:162` using the unresolved `$ROOT` is wrong: `$ROOT` may be relative
   or symlinked, while `safe.directory` values are real-path-normalised.

## Confidence

- Git docs and implementation: **high** (docs 2.56.0; source line-level; host git 2.56.0).
- Census row/exit path: **high** as static control flow at exact lines; **not dynamically executed**
  (the census was not run, per contract).
- Absence of tests: high for the three named files only; not claimed for the whole lane.

## Remaining unknowns

- Whether the operator puts foreign-owned repos in the census's scope (lesson says the L0 question
  is filed).
- Whether any current fleet repo is foreign-owned: not enumerated (recursive scanning is forbidden);
  the census's own output would show it as `error`, but running the census is forbidden for this seat.
- Whether some git version's `git config --file` also applies the ownership check: source says it
  does not discover a repository; not executed.

## Probe compliance note

Out-of-class read-only commands used and disclosed: `git status --porcelain` (lane only; used to see
dirty paths), `git config --show-scope --get-all safe.directory` (lane only; empty), and three
directory-wide `grep -rn` calls over `tools/`, `tests/`, `corpus/`, `census/round-16/` (no forbidden
directory touched; outputs were only negative/marker checks, and the substantive absence claim is
re-derived on the three exact named files listed above). No lane file was edited; the only write is
this report.

Web/source reads (read/grep tools, not shell): `https://git-scm.com/docs/git-config` (full; ranges
`:7694-7728`, `:795-830`, `:7728-7765`), `https://git-scm.com/docs/git` (env sections),
`https://git-scm.com/docs/gitfaq` (no `dubious`/`safe.directory` match),
`https://raw.githubusercontent.com/git/git/master/setup.c` (full; `:1339-1475`, `:1935-2000`,
`:1240-1340`), `https://raw.githubusercontent.com/git/git/master/builtin/rev-parse.c` (`:700-790`),
`https://raw.githubusercontent.com/git/git/master/git.c`, `builtin/config.c` (`:1290-1380`),
`config.c` (`:2462-2484`). All accessed 2026-10-20.

STATUS: ok

## Commands

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh && git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -30
grep -n -E "safe\.directory|GIT_CONFIG_GLOBAL|GIT_CONFIG_COUNT|GIT_NO_LAZY_FETCH|safe_directory|dubious|ownership" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "safe.directory" tools/ tests/ corpus/ LOG.md 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '95,180p' tools/souji-census.sh
git --version; git config --show-scope --get-all safe.directory 2>&1 | head; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '905,950p;1025,1060p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1130,1260p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD | grep -n "souji-census" ; echo "---log---"; git log --oneline --all -- tools/souji-census.sh | head -20; echo "---impl status---"; git log --oneline --all -- tools/souji-census.impl-46.sh | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '95,120p' tools/souji-census.impl-46.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E "^git_|git -C|git\(\)|_git|fatal|dubious|ownership|status-unverifiable|error row|ERROR" tools/souji-census.sh | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '700,780p;960,1020p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '450,500p' tools/souji-census.sh
grep -a -o "detected dubious ownership in repository at [^%]*" "$(command -v git)" | sort -u | head -5; echo "---"; grep -a -o "To add an exception for this directory[^%]*" "$(command -v git)" | sort -u | head -3
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "guard_path()\|guard_target()\|rev-parse\|find .*\.git\|-name '\.git'\|-name \"\.git\"" tools/souji-census.sh | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "dubious\|other user\|foreign-owned\|another user" tools/souji-census.sh corpus/lessons/round-16.md LOG.md 2>/dev/null | head -20; echo "---header---"; sed -n '118,124p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && export GIT_TEST_ASSUME_DIFFERENT_OWNER=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1; echo "--- no exception ---"; git -C . rev-parse --is-inside-work-tree; echo "rc=$?"; echo "--- command-scope -c ---"; git -c safe.directory='*' -C . rev-parse --is-inside-work-tree; echo "rc=$?"; echo "--- GIT_CONFIG_COUNT ---"; GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0='*' git -C . rev-parse --is-inside-work-tree; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=500 && NR<=905 && /git -C|git /{print NR": "$0}' tools/souji-census.sh | head -20; echo "---guard_git_surface---"; sed -n '821,905p' tools/souji-census.sh | grep -n "git " || echo "no git calls in guard_git_surface range"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "ASSUME_DIFFERENT_OWNER\|safe.directory\|dubious" tools/souji-census.sh tests/ census/round-16/ 2>/dev/null | head -20; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '65,80p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in b410186 a31642d 0a70bef; do echo "=== $rev $(git rev-parse --short $rev) ==="; git show $rev:tools/souji-census.sh 2>/dev/null | grep -n "safe.directory\|GIT_CONFIG_GLOBAL\|GIT_CONFIG_COUNT\|git_ro()" | head -8; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -e a31642d:tools/souji-census.sh && echo EXISTS; git show a31642d:tools/souji-census.sh | grep -n "GIT_CONFIG\|safe\|git_ro\|--no-optional-locks" | head -15
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | grep -n "git -C\|--no-optional-locks" | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1400,1490p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '500,560p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "error\\\\n\|not-a-repo\\\\n\|config-unsupported\|placeholders, not measurements\|no git command runs" tools/souji-census.sh; echo ---; sed -n '88,100p' tools/souji-census.sh; echo ---; sed -n '1174,1200p' tools/souji-census.sh | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in tools/souji-census.sh tests/fixtures/r15-census-config.py census/round-16/run-matrix.py; do echo "== $f"; grep -n "safe\.directory\|dubious\|ASSUME_DIFFERENT\|chown\|GIT_CONFIG_GLOBAL\|GIT_CONFIG_COUNT" "$f" || echo "(no matches)"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && git diff --stat -- tools/souji-census.sh && git show HEAD:tools/souji-census.sh | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '180,200p;285,302p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1335,1365p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && export GIT_TEST_ASSUME_DIFFERENT_OWNER=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1; p=$PWD; echo "== exact path"; git -c safe.directory="$p" -C . rev-parse --is-inside-work-tree; echo "rc=$?"; echo "== path prefix wildcard"; git -c safe.directory="$p/*" -C . rev-parse --is-inside-work-tree 2>&1 | head -2; echo "rc=$?"; echo "== nonmatching"; git -c safe.directory=/nonexistent -C . rev-parse --is-inside-work-tree 2>&1 | head -1; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "protected_fail()" tools/souji-census.sh; sed -n "$(grep -n 'protected_fail()' tools/souji-census.sh | cut -d: -f1),+8p" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "GIT_CONFIG_PARAMETERS\|safe" tools/souji-census.sh || echo "(none)"; echo "---matrix target---"; grep -n "souji-census\|tools/" census/round-16/run-matrix.py | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && export GIT_TEST_ASSUME_DIFFERENT_OWNER=1 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1; parent=$(dirname "$PWD"); echo "parent=$parent"; echo "== parent/* wildcard"; git -c safe.directory="$parent/*" -C . rev-parse --is-inside-work-tree 2>&1 | head -2; echo "== parent exact"; git -c safe.directory="$parent" -C . rev-parse --is-inside-work-tree 2>&1 | head -2; echo "== parent/ prefix with trailing slash"; git -c safe.directory="$parent/" -C . rev-parse --is-inside-work-tree 2>&1 | head -2
```
