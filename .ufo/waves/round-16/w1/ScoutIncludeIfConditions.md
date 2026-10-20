# Scout — includeIf conditions vs. the census's unconditional include guard

Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423` (HEAD of
`/home/vgpnk/Projects/shokunin/souji-shokunin`; worktree clean for that file, so line
numbers below are the committed bytes). Sources accessed 2026-10-20.

**Verdict:** the census's design — guard *and* follow every `includeIf.*.path` target
without evaluating its condition — is a **sound superset of git's config reads**, and for
`hasconfig:remote.*.url` it is not merely conservative: git really does read those targets
before the condition is resolved. No under-guard found on the census's command surface.
Two costs are real but fail-safe (whole-run `path-protected` exit 2 for an unmatchable
store-reaching target; one `error` row for an unmatchable target whose contents cannot be
evaluated).

## 1. Observed semantics (documentation)

- Condition forms and matching. "gitdir", "gitdir/i", "onbranch", "hasconfig:remote.*.url",
  plus `worktree` / `worktree/i` in current master (docs stamped 2.56.0):
  https://git-scm.com/docs/git-config — "The condition starts with a keyword followed by a
  colon and some data" — accessed 2026-10-20.
- Include insertion order: https://raw.githubusercontent.com/git/git/master/Documentation/config.adoc
  — "The contents of the included file are inserted immediately, as if they had been found
  at the location of the include directive." — accessed 2026-10-20. (Backs the census
  comment at lines 577-578 that includes are followed in place for last-wins order.)
- `gitdir`/`gitdir/i`: same doc — "If the pattern does not start with either `~/`, `./`
  or `/`, `**/` will be automatically prepended."; "if the pattern ends with `/`, `**`
  will be automatically added"; "Symlinks in `$GIT_DIR` are not resolved before matching.";
  "Both the symlink & realpath versions of paths will be matched outside of `$GIT_DIR`.";
  "`../` is not special and will match literally". Matching is against the **final** `.git`
  directory for gitfile/linked worktrees. `gitdir/i` is the case-insensitive variant.
- `worktree`/`worktree/i`: same doc — pattern matched against `git rev-parse
  --show-toplevel`, realpath only: "This condition will never match in a bare repository
  (which has no worktree)." (New in the 2.56 doc; see Residual R2.)
- `onbranch`: same doc — matched against "the name of the branch that is currently checked
  out"; glob with `**/` and trailing-`/` expansion. Source `include_by_branch()`
  (https://raw.githubusercontent.com/git/git/master/config.c, accessed 2026-10-20) returns
  0 when HEAD is not a symref into `refs/heads/`, i.e. **detached HEAD never matches**.
- `hasconfig:remote.*.url`: same doc — "The first time this keyword is seen, the rest of
  the config files will be scanned for remote URLs (without applying any values)." and
  "Files included by this option (directly or indirectly) are not allowed to contain
  remote URLs." Condition input is the glob-matched set of **all** `remote.*.url` values.
- Unknown keywords: `config.c` `include_condition_is_true()` — "unknown conditionals are
  always false" (comment + fall-through `return 0`). They are not an error.

## 2. Can a hasconfig include be read before the condition is known? YES

Documentation, https://raw.githubusercontent.com/git/git/master/Documentation/config.adoc:
"resolving this condition relies on information that is not yet known at the point of
reading the condition" — accessed 2026-10-20.

Source chain, `https://raw.githubusercontent.com/git/git/master/config.c` (accessed
2026-10-20), in `git_config_include()`:

1. `include_by_remote_url()` first call → `populate_remote_urls()` → `config_with_options(...,
   inc->config_source, inc->repo, &opts)` with `opts.unconditional_remote_url = 1`.
   `config_with_options()` installs `git_config_include` again whenever `respect_includes`
   is set (it is, from `repo_read_config()`), so the **whole config chain is re-read,
   includes and all**, before the first hasconfig decision.
2. During that pre-pass `include_by_remote_url()` starts with `if
   (inc->opts->unconditional_remote_url) return 1;` — every `includeIf hasconfig` in the
   chain therefore evaluates **true**, and:
3. `git_config_include()` sets `inc->fn = forbid_remote_url` and calls
   `handle_path_include()` → `access_or_die(path, R_OK, 0)` →
   `git_config_from_file_with_options(...)`, i.e. it **opens and parses the target** and any
   includes it in turn contains; `forbid_remote_url()` dies with "remote URLs cannot be
   configured in file directly or indirectly included by includeIf.hasconfig:remote.*.url".

So an unmatched hasconfig target is still read by git. The fixture's rationale at
`tests/fixtures/r15-census-config.py:32-34` ("hasconfig pre-pass reads it") is **confirmed at
code level**, not just plausible.

## 3. Is guarding every include target a safe superset? YES

Guard set ⊇ read set, for the command surface the census runs (`git -C <repo> status`,
`rev-parse`, `worktree list`):

- `gitdir`/`gitdir/i`/`worktree`/`worktree/i` patterns can match the repo at scan time or
  later (symlinked spellings, case-insensitive filesystems, branch changes); evaluating them
  means re-implementing `wildmatch` plus the `~/`, `./`, `**/`, trailing-`/`, realpath-vs-
  symlink dual matching. A mismatch in either direction is worse than over-guarding.
- `onbranch` needs HEAD resolved (a git call, and a moving target — the branch can change
  between guard and `status`).
- `hasconfig` is read pre-resolution (§2), so a "cannot match" shortcut is simply false
  for it.
- Unknown conditions are false *today*; the docs call the naming "forwards compatibility
  with a naming scheme that supports more variable-based include conditions", so treating
  unknown as never-read would silently under-guard a future git. Guarding is version-proof.
- Scope closure: the census clears inherited `GIT_*` (lines 135-147) and pins
  `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`
  (lines 143-144), so no global/system/`-c` include can reach a repo run; `-c` options are
  the census's own fixed pair. `config.worktree` is scanned when enabled (lines 654-663).
  With `--file`, includes are off by default — "Defaults to `off` when a specific file is
  given (e.g., using `--file`, `--global`, etc)"
  (https://raw.githubusercontent.com/git/git/master/Documentation/git-config.adoc, accessed
  2026-10-20) — and the census also passes `--no-includes` explicitly (lines 589, 592), so
  during parsing git itself never follows an unguarded include.

Costs of the superset (all fail-safe, none reads protected bytes):

1. `includeIf "gitdir:/nonexistent/"` / `includeIf "forge:x"` pointing at the store is a
   whole-run `path-protected` exit 2 even though git would never read it. That is exactly
   what the fixture pins (`r-incif-store`, `r-incif-hc-store`, `r-incif-unknown`; expected
   refusal list `tests/fixtures/r15-census-config.py:1064-1076`, `CONFIG_REASONS` at 962).
   C1's shape claim ("only a protected-namespace reach keeps whole-run exit 2") is not
   violated: the reach exists lexically; only its *would-git-read-it* status is
   over-approximated.
2. An unmatchable target that the census follows but cannot evaluate (cycle, NUL,
   `~user`, FIFO/hardlink) yields one `error` row with exit 0 for a repo git would have
   counted — e.g. `[includeIf "gitdir:/nonexistent/"] path = ~root/x`. Fail-safe, but see
   F2.

## 4. Line-by-line relation to the script

| Lines | Behavior | vs. git |
|---|---|---|
| 87-89 | header: "recursively through include.path/includeIf.*.path targets (every target is guarded, whatever its condition)" | Accurate. "Guarded" is honest; it does not claim conditions are evaluated. |
| 605-608 | `case "$sec:$var"` `include:path|includeif:path`; include with a subsection and includeIf without one are skipped | Matches `git_config_include()`: only exact `include.path` and `includeif.<cond>.path` / `key == "path"`. |
| 611 | relative target resolved against `${cfg%/*}` | Matches "relative to the configuration file in which the include directive was found". |
| 612 | `~user` / `%(prefix)` → `cfg_soft git-config-unsupported` | `handle_path_include()` bails via `if (!expanded) return error(...)` for unexpandable paths, so per-repo degrade ≥ git's own failure. Conservative. |
| 614 | `guard_config_path include-protected` **before** existence test, `stat`, or `open` | Correct ordering; symlink walk in `resolve_guarded` (line 365 onward) runs before any access to the target. |
| 615 | missing target → `continue` | Matches git: `access_or_die()` ignores missing-file errors (`access_error_is_ok()` → `is_missing_file_error()`), so the include is silently skipped. |
| 616 | non-regular / hardlink → `cfg_soft` (per-repo `error`, exit 0) | Deliberate over-refusal. A FIFO would block git's `fopen`/read; a folder makes git fail parsing; a hardlink is readable by git but refused by policy. Safe, row-shape divergence only. |
| 617 | recurse with depth+1; depth > 10 at 582 and cycle at 584 | Same boundary as `MAX_INCLUDE_DEPTH 10` (`++inc->depth > 10` dies). Census degrades instead of dying; cycle detection is an addition. |
| 1088-1089 | one `error` row + `souji-census: config-unsupported: <reason> (<repo>)`, exit 0 | Matches declared C1 degradation; no git command runs in that repo (`census_one` returns before the status call). |
| 143-147 | global/system config disabled; `GIT_NO_LAZY_FETCH=1` | Closes the only other config scopes that could carry `includeIf`. |

## 5. Findings

F1 (none, confirms the claim). The unconditional guard is correct and complete for the
census's git surface; the `hasconfig` case is a genuine pre-resolution read, and the
`gitdir`/`onbranch` cases are fail-closed over-approximations. No path was found by which
git could open a target the census leaves unguarded.

F2 (low, advisory, documentation only). Lines 87-89 say every target is "guarded, whatever
its condition" but not that every target is also **parsed**; because line 617 follows the
target unconditionally, an unmatchable target's contents can downgrade a repo git would
have counted cleanly to an `error` row. Suggest one clause in the header (e.g. "and is
parsed, whatever its condition") so the exit-0 row loss is declared, not surprising. No
code change is warranted: condition evaluation would be a read-safety regression.

F3 (low, comment accuracy). Line 609-610's "A bare or empty path makes git itself fail;
nothing is opened" is slightly imprecise: an empty value expands to the including file's
directory, which `fopen`s successfully and only fails on read. Safety is unaffected (an
empty path cannot name the store), but the comment overstates "nothing is opened".

F4 (informational). The census is forward-compatible with `worktree:`/`worktree/i:`
conditions that a condition-evaluating implementation keyed to older keywords would treat
as unknown/false.

## Confidence

- Condition semantics and the hasconfig pre-pass: **high** — primary docs plus the exact
  code path (`unconditional_remote_url` → `include_by_remote_url` → `handle_path_include`).
- Guard-is-superset for this command surface: **high** for config scopes; the only residual
  is documented TOCTOU (guard and later access are not one atomic operation, already in the
  script header).
- Host git's keyword set: **unknown** — whether the installed git has `worktree:` (2.56
  docs) is not verified here (peer `SoujiR16.ScoutGitHostVersion` owns that). Nothing in
  this report depends on it; F4 assumes only that the census's condition-blind guard is
  unaffected either way.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat | cat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -i -E "include|includeIf|gitdir|onbranch|hasconfig|fsmonitor|promisor|partialclone|alternaterefs|hookspath"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E "includeIf|gitdir|onbranch|hasconfig|condition" tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E "no-includes|scan_config_file|guard_git_config|CFG_SOFT_REASON|config-unsupported|cfg_soft" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E "GIT_CONFIG|GIT_ATTR|GIT_DIR|GIT_NO_LAZY|env -i|--no-optional-locks|GIT_CEILING|GIT_DISCOVERY" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E "R15CFG-0[0-9]|r-incif|includeif|include-protected" tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'if \[ ! -e "\$tgt" \]|guard_config_file_kind "\$tgt"|scan_config_file "\$dir" "\$tgt"|expand_config_path "\$val"|guard_config_path include-protected' tools/souji-census.sh
```

Reads: `tools/souji-census.sh` lines 79-123, 129-163, 179-473, 469-663, 664-700, 1060-1110;
`tests/fixtures/r15-census-config.py` lines 1-63, 394-473, 1035-1103;
`https://git-scm.com/docs/git-config`;
`https://raw.githubusercontent.com/git/git/master/Documentation/config.adoc`;
`https://raw.githubusercontent.com/git/git/master/Documentation/git-config.adoc`;
`https://raw.githubusercontent.com/git/git/master/config.c` (lines 1-300, 300-560, 1400-1900,
2000-2800);
`https://raw.githubusercontent.com/git/git/master/wrapper.c` (lines 620-780);
`https://raw.githubusercontent.com/git/git/master/path.c` (lines 800-1150).
No tools installed or upgraded this round.

STATUS: complete — no operand defect found; F2/F3 are documentation/comment nits only.
