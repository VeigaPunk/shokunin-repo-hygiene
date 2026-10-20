# Scout — `ls-files` pathspec magic and `check-attr` `.gitattributes` scope (R16 W2)

Lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; `tools/souji-census.sh` blob at HEAD
sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (matches the
wave-1 hash); git `2.56.0`; docs/source accessed 2026-10-20.

Scope: the `guard_bound_filters` pipeline at `tools/souji-census.sh:1002-1010` and the
status pathspec at `:1037-1041`; nothing else in the tool was re-audited.

## F1 — Pathspec magic as used: HOLDS

The six pathspecs are used in the long form (`:(exclude)` / `:(exclude,glob)`), preceded by
the positive `.`:

```
tools/souji-census.sh:1003  ls-files -z --cached -- . ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
tools/souji-census.sh:1004      ':(exclude,glob)census/operator-sweep-*' \
tools/souji-census.sh:1005      ':(exclude,glob)census/operator-sweep-*/**' \
tools/souji-census.sh:1006      ':(exclude,glob)**/census/operator-sweep-*'
```

Observed semantics, per the Git manual:

- `exclude` is a post-filter over the positive match: “After a path matches any non-exclude
  pathspec, it will be run through all exclude pathspecs” and “If it matches, the path is
  ignored.” (https://git-scm.com/docs/gitglossary, accessed 2026-10-20). With `.` as the
  positive pathspec the filters apply to the whole index; the doc also says an exclusion
  without a positive pathspec applies “as if invoked without any pathspec”, so `.` is
  harmless.
- Default (no `glob`) matching splits at the last slash: “the pathspec up to the last slash
  represents a directory prefix. The scope of that pathspec is limited to that subtree.”
  and the remainder is fnmatch’d, where “in particular, `*` and `?` *can* match directory
  separators” (same URL). A literal remainder that prefixes a path at a directory boundary
  returns `MATCHED_RECURSIVELY` (`dir.c:444-449`,
  https://raw.githubusercontent.com/git/git/master/dir.c, accessed 2026-10-20). This is why
  `:(exclude).ufo/state` excludes the *directory* and every tracked entry below it even
  without `/**`, and `.ufo/watchdog.log` excludes the file (or, if it were a directory, its
  subtree as well).
- With `glob`, “wildcards in the pattern will not match a / in the pathname”; “A leading
  `**` followed by a slash means match in all directories”; “A trailing `/**` matches
  everything inside.” (gitglossary URL above). So `census/operator-sweep-*` matches only the
  root-level entry itself, `census/operator-sweep-*/**` matches everything inside a
  root-level entry, and `**/census/operator-sweep-*` matches an entry at any depth. The
  three operator-sweep patterns are deliberately shaped around FNM_PATHNAME, and for the
  live layout (`census/operator-sweep-20261019/` at repo root) they cover the surface
  completely.

## F2 — Nested operator-sweep contents reach `check-attr`: FAILS (narrow, upstream of the claim)

`tools/souji-census.sh:1000-1001` states: “Same pathspec exclusions as status, so check-attr
never reads an attributes file inside an operator-owned surface.” The string set is the same,
but a wildcard match on a directory name does not extend to its children in the entry-level
matcher: `ls-files --cached` matches every index entry individually
(`builtin/ls-files.c:328-331`, `:370-372`,
https://raw.githubusercontent.com/git/git/master/builtin/ls-files.c), and `git status` uses
the same per-entry matcher for tracked files (`refresh_index` → `ce_path_match` →
`match_pathspec`, `read-cache.c:1555`, `read-cache.h:44-51`). Directory-name pruning exists
only in the untracked walk (`dir_match`’s negative result returns 0, `dir.c:590-604`,
`:1938-1946`; `read_directory_recursive` then returns `path_none`, `dir.c:2020-2027`), so it
cannot rescue the tracked-entry path either.

Counterexample (tracked content, so `--cached` lists it):

```
path: sub/census/operator-sweep-7/.gitattributes      (tracked)
path: sub/census/operator-sweep-7/f.bin               (tracked)
```

- `:(exclude,glob)census/operator-sweep-*` — anchored at root; no match.
- `:(exclude,glob)census/operator-sweep-*/**` — anchored at root; no match.
- `:(exclude,glob)**/census/operator-sweep-*` — matches `sub/census/operator-sweep-7` as a
  path; with FNM_PATHNAME the trailing `*` cannot cross the `/` before `f.bin`, so
  `sub/census/operator-sweep-7/f.bin` is not matched (gitglossary glob bullets above).

Both entries are listed by `ls-files -z --cached` and fed to `check-attr -z --stdin filter`
(`tools/souji-census.sh:1002-1008`). `check-attr` then resolves attributes for those paths
along their directory chain, so it opens
`sub/census/operator-sweep-7/.gitattributes` — a read inside the operator-owned surface the
tool claims never to touch. The same operator-sweep patterns are used by `status` at
`tools/souji-census.sh:1037-1041`; tracked nested-sweep entries are therefore stat’d and
counted there too. Execution safety does not rest on the pathspec: `guard_bound_filters`
queries `check-attr` for those same listed paths, so a configured driver bound there still
forces `status-unverifiable` before `status` runs.

The tool’s own `find` prune already anticipates this layout — `tools/souji-census.sh:1076-1077`
prunes both `./census/operator-sweep-*` and `*/census/operator-sweep-*` — so the nested case
is inside the tool’s declared threat model, not hypothetical.

Smallest fix: add one pathspec to the `ls-files` list (and, for symmetry, the status list):

```
':(exclude,glob)**/census/operator-sweep-*/**'
```

Reachability: the live lane surface is root-level, so this round’s own census run is
unaffected; the failure needs a repo where a `census/operator-sweep-*` sits below another
directory and its content is tracked. Rated partial for the fleet, not for the lane.

## F3 — `check-attr` scope: per-path `.gitattributes` only for listed paths, plus three global frames: PARTIAL

Answer to the question: for the per-directory `.gitattributes` layer, **yes** — attributes
are resolved only along each listed path’s own directory chain. “Git consults
`$GIT_DIR/info/attributes` file (which has the highest precedence), `.gitattributes` file in
the same directory as the path in question, and its parent directories” (gitattributes,
https://git-scm.com/docs/gitattributes, accessed 2026-10-20; source: `attr.c:950-1035`
`prepare_attr_stack` pushes only components of the queried path). `check-attr` itself calls
`git_check_attr` once per input path (`builtin/check-attr.c:75`,
https://raw.githubusercontent.com/git/git/master/builtin/check-attr.c); it never walks the
tree. Worktree files are read first and index blobs are the fallback — “When the
`.gitattributes` file is missing from the work tree, the path in the index is used as a
fall-back.” (same gitattributes page; `attr.c:841-878`). `.gitattributes` is opened with
`READ_ATTR_NOFOLLOW` (`attr.c:702-705`, `attr.c:937`, `attr.c:1028`), so a symlinked
attributes file is not followed out of the worktree — that closes the obvious
boundary-escaping variant.

But three attribute sources are not path-scoped and are consulted for every invocation:
`$GIT_DIR/info/attributes`, `core.attributesFile`, and the system-wide file —
“Attributes for all users on a system should be placed in the `$(prefix)/etc/gitattributes`
file.” and “Finally global and system-wide files are considered (they have the lowest
precedence).” (same URL). The census models the first two: `info/attributes` is boundary- and
regular-file guarded at `tools/souji-census.sh:521`, and `core.attributesFile` is resolved and
guarded (`status_info_file`, `:942-975`), then re-passed as `-c core.attributesFile=...`
at `:1002`, `:1007` and `:1037`. It does not model the
third: no `GIT_ATTR_NOSYSTEM`, and no guard on `$(prefix)/etc/gitattributes`. Worse, heavy
`GIT_*` clearing at `tools/souji-census.sh:150` unsets an inherited `GIT_ATTR_NOSYSTEM`, so
the system file is always enabled; the gate is `git_env_bool("GIT_ATTR_NOSYSTEM", 0)`
(`attr.c:893`) with the read at `attr.c:925-928`.

Consequences: (a) `guard_bound_filters` can see a `filter=` binding that came only from the
system file and skip status for every repo where that driver exists (fail-closed, so no
driver runs, but the row degrades to `status-unverifiable`); (b) the docstring’s model of
“effective attributes file” is incomplete, and the system file is an unguarded source. On this
host the file is absent (`/etc/gitattributes`, `/usr/etc/gitattributes`,
`/usr/local/etc/gitattributes`, and `$XDG_CONFIG_HOME/git/attributes` all absent), so this is
latent, not active. `GIT_ATTR_NOSYSTEM` is implemented but is not described in the 2.56
`git(1)`/`gitattributes(5)` sources (grep of `Documentation/git.adoc` and
`gitattributes.adoc` finds only `GIT_ATTR_SOURCE`).

Smallest fix: `export GIT_ATTR_NOSYSTEM=1` beside `GIT_CONFIG_GLOBAL/SYSTEM` at
`tools/souji-census.sh:153` (inherited values are already cleared, so this only pins the
intent), and add one docstring sentence that the system attributes file is disabled rather
than honoured.

## F4 — Driver non-execution and the `-z` record contract: HOLDS

- `check-attr` only reports “_unspecified_, _set_, or _unset_”
  (https://git-scm.com/docs/git-check-attr, accessed 2026-10-20); it never runs a
  clean/smudge/process driver, and `ls-files --cached` reads the index only
  (“Show all files cached in Git’s index, i.e. all tracked files.”,
  https://git-scm.com/docs/git-ls-files, accessed 2026-10-20). The comment at
  `tools/souji-census.sh:982` is accurate.
- `check-attr -z --stdin filter` prints three NUL-separated fields per path: “unless `-z`
  is in effect, in which case NUL is used as delimiter” (check-attr page, OUTPUT). The
  `% 3` and `recs[i=2,5,...]` logic at `tools/souji-census.sh:1011-1016` matches that format;
  `filter=<driver>` yields the bare driver name, which is what the loop compares.
- `--cached` is not passed to `check-attr`, so the working tree is read first with index
  fallback (“Consider `.gitattributes` in the index only, ignoring the working tree.” is the
  option the tool does **not** use). That is the intended source for status parity.

## Coverage note

Neither the selftest nor `tests/fixtures/r15-census-config.py` exercises a
`census/operator-sweep-*` path or an attributes read inside one (`grep -n operator-sweep`
returns nothing in the fixture); the property in `tools/souji-census.sh:1000-1001` is
untested. The pipeline itself is known-working: matrix cases `R15CFG-13` (unbound drivers,
row clean) and `R15CFG-14` (bound driver, `status-unverifiable` plus `status-skipped`
diagnostic) both PASS in `census/round-16/c1-matrix-final.json`, which also shows the
process-substitution status check (`pid=$!`, `wait "$pid"`, `:1009-1010`) propagates
correctly for the measured bash.

## Remaining unknowns

- Whether any fleet repo currently has a nested `*/census/operator-sweep-*` with tracked
  content: not measured (out of this recon’s allowed probes).
- Host git was verified as 2.56.0; the doc/source citations are from the 2.56-era tree.
  The `$(prefix)` value for `ETC_GITATTRIBUTES` on this build was not introspected — all
  plausible paths were checked directly and absent.

STATUS: PARTIAL — F2 is a real nested-layout gap in the exclusion set for both consumers
(`ls-files`→`check-attr` and tracked-entry `status` filtering); one extra
`:(exclude,glob)**/census/operator-sweep-*/**` pathspec fixes it. F3 leaves the system-wide
gitattributes file unmodelled/undisabled (latent on this host, one env export fixes it). The
root-level pathspec use, driver non-execution, and `-z` contract hold.

## Commands

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "ls-files\|check-attr\|gitattributes\|pathspec\|exclude" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git log --oneline -3 && git --version && sha256sum tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "filter\|ls-files\|check-attr\|attributes" tests/fixtures/r15-census-config.py | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '660,720p' tests/fixtures/r15-census-config.py 2>/dev/null || true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1265,1320p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "operator-sweep" tests/fixtures/r15-census-config.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "operator-sweep\|check-attr\|ls-files" tools/souji-census.sh | sed -n '1,40p'
for f in /etc/gitattributes /usr/etc/gitattributes /usr/local/etc/gitattributes; do if [ -e "$f" ]; then echo "PRESENT $f"; else echo "ABSENT $f"; fi; done; printf 'XDG=%s HOME_ATTR=%s\n' "${XDG_CONFIG_HOME:-<unset>}" "$([ -e "${HOME}/.config/git/attributes" ] && echo present || echo absent)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w2/ 2>/dev/null | head -5; printf '---\n'; git show --stat --oneline HEAD -- tools/souji-census.sh | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "compgen -v GIT_\|GIT_CONFIG_GLOBAL\|GIT_NO_LAZY_FETCH\|GIT_CONFIG_COUNT\|Same pathspec\|Neither ls-files\|fails closed" tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | sha256sum && git rev-parse HEAD:tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'pid=\$!\|wait "\$pid"\|% 3\|for ((i = 2\|attributesFile="\$at"\|status --porcelain\|core.attributesFile=\|status_info_file()' tools/souji-census.sh
```
