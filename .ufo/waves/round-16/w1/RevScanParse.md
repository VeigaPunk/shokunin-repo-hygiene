# RevScanParse — `scan_config_file` key/subsection/variable split vs git-config(1)

Round-16 review. Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
(1784 lines; worktree HEAD is the same commit, 0 dirty tracked files). Method: source
inspection only — no census run, no synthetic repo, no execution of the tool. The
reference is the installed `git-config(1)` / `git-worktree(1)` man pages
(`/usr/share/man/man1/git-config.1.gz`, rendered with `col -b`), not memory.

## Verdict

- The **key / subsection / variable split** in `scan_config_file` (lines 594–603), the
  **bare-vs-empty** discriminator (595–599, consumed at 610/620/627/634), **dotted
  subsections** (602–603) and **case folding** (600–601) are **correct** against
  git-config(1). **No defect found in the split itself.** Evidence in §1.
- Three real defects exist in the same config-scanning surface. One is a hard bypass of the
  round's own "the filter driver never runs" invariant and sits in the *same* `git config
  --list/-z` record idiom, re-implemented at lines 910–919; that one is reported although its
  home function (`guard_bound_filters`) is outside this item's literal charter. The other two
  are a state-model error in the `extensions.worktreeConfig` grant and a control-character
  refusal that contradicts the round's declared failure shapes.

## 1. Split verification — why there is no defect here

**1.1 Record shape and bare-vs-empty (lines 594–599).**
git-config(1) `--null`: *"For all options that output values and/or keys, always end values
with the null character (instead of a newline). Use newline instead as a delimiter between key
and value."* Therefore a value-bearing record is `key\nvalue\0`, a valueless key is `key\0`,
and an explicitly empty value is `key\n\0`. A record can never contain a newline before its
delimiter because keys cannot: git-config(1) §CONFIGURATION FILE — *"Subsection names are case
sensitive and can contain any characters except newline and the null byte"* (section and
variable names are narrower still: alphanumeric, `-`, and `.`; variables also start alpha).
Consequently `[[ $rec == *$'\n'* ]]` (595) is an exact "has a value" test, `${rec%%$'\n'*}`
(596) is an exact key, `${rec#*$'\n'}` (596) keeps a multi-line value whole, and `bare=1`
(598) occurs iff no delimiter byte is present. Bare (implicit true) and explicit-empty (false
literal) therefore remain distinguishable — the discriminator is sound, including for values
that themselves contain newlines.

**1.2 Section / variable / subsection (lines 600–603).**
git-config(1) §CONFIGURATION FILE: *"the fully qualified variable name of the variable itself
is the last dot-separated segment and the section name is everything before the last dot"*;
variable names *"allow only alphanumeric characters and `-`"* — no dots. The last dot is
therefore always the variable separator, and the first dot is the section-proper boundary, so
`sec=${key%%.*}` (600), `var=${key##*.}` (601) and the middle slice `sub` (602–603) are exact.
Dotted subsections survive: `includeif.gitdir:/a.b/.path` → `sec=includeif`,
`sub=gitdir:/a.b/`, `var=path`. The deprecated `[section.subsection]` spelling produces the
same flat key; the empty-subsection key `includeif..path` yields `sub=""` and is skipped (608),
which matches git: an unknown/empty include condition is false. Tested mentally against the
fixture's key-parsing cases (fixture lines 655–660: remote named `include.d`, remote subsection
`x.promisor-mirror`, `filter.x.required`/`diff.clean.driver`) — none can reach the
`include/includeif` branches, so those cases hold.

**1.3 Include matching is exact-string equivalent (lines 605–608).**
`sec=include`, `sub=""`, `var=path` is exactly the canonical key `include.path`; `sec=includeif`
with non-empty `sub` and `var=path` is exactly `includeif.<cond>.path`, the key shape git's
include machinery compares. There is no over-broad matching: `include.path.path`,
`include.foo.path` (deprecated subsection), `remote.include.path` and `includeif..path` are all
excluded. Over-approximation of *conditions* (every `includeIf` is followed, lines 605–608) is
pinned by the fixture (lines 32–36) and is not a split defect.

**1.4 Case folding (lines 600–601, 603).**
git canonicalizes keys with *"section and variable names ... lowercased, but subsection names
are not"* (git-config(1) `--regexp`). The code folds `sec` and `var` only, and never folds
`sub`; that is the documented rule. Since `--list` prints canonical keys, the `${x,,}` folds
are normally no-ops; they are locale-sensitive (`${x,,}` follows the ambient locale) but cannot
corrupt an already-lowercase ASCII key, so this is not a defect. It would only become one if a
future change relied on them to normalize non-canonical input; then `LC_ALL=C` is required.

**1.5 `extensions.worktreeConfig` bare vs empty (lines 633–638).**
git-config(1) §Values: *"a variable defined without `=` `<value>` is taken as true"*; false
literals are *"`no`, `off`, `false`, `0` and the empty string."* So the bare branch (634) is
correctly true and the empty value correctly resolves false via `--type=bool --get`
(635–638). Matches the fixture's `r-wtc-empty` benign case (fixture line 604).

**1.6 Path bases.** `include.path` resolves against `${cfg%/*}` (611) — the containing file's
directory, as git does. `core.worktree` resolves against the gitdir (628) — git-config(1) `core.worktree`:
*"The value can be an absolute path or relative to the path to the .git directory."*
`core.excludesFile`/`core.attributesFile` use `${dir%/*}` (621), the main worktree root for
the only gitdir shapes that reach this function with a real config; the operative status path
re-guards the effective value from `$wt` (874–882), so linked-worktree relative values are
still guarded before `git status`. No hole found.

## 2. Findings

### RSP-1 — High — a filter command ending in a newline is classified as an empty value; a bound driver can run
`tools/souji-census.sh:910-919` (the test is line 914).

`guard_bound_filters` re-decodes `git config -z --get-regexp` records with:

```bash
913    # An explicitly empty value (`key\n`) defines no command.
914    case "$rec" in *$'\n') continue ;; esac
```

That pattern matches any record **ending** in a newline, not only the empty-value record
`key\n`. A filter command value may itself end in a newline (config values decode `\n`; e.g.
`[filter "x"]` + `clean = "sh -c '...'\n"`), producing the record
`filter.x.clean\nsh -c '...'\n\0`. Line 914 then `continue`s before line 918, so `x` is never
added to `drivers`, the attributes binding comparison at 926–930 never sees it, the function
returns 0 (931), and `count_dirty` runs the full `git status` at 947–953 — where git executes
the bound clean/process command for a file that needs hashing. This breaks the round's stated
invariant (header lines 98–100: "the driver never runs") and the fixture's bound-filter sentinel
assertion (fixture 503–506, 1226–1237). The fixture's only bound-filter value has no trailing
newline (506), so the shape is untested.

Minimal patch — replace 913–914 (name extraction at 915–917 stays):

```bash
    # A bare key or an explicitly empty value defines no command; a command
    # value may itself end in a newline and must still be registered.
    case "$rec" in
      *$'\n'*) [ -n "${rec#*$'\n'}" ] || continue ;;
      *) continue ;;
    esac
```

Equivalently: extract `val=${rec#*$'\n'}` first and `continue` unless `val` is non-empty and
differs from `rec`.

Scope note: `guard_bound_filters` is adjacent to this item rather than inside
`scan_config_file`; it is reported because it is the same `--list -z` record idiom with the
same bare-vs-empty question, and because it is the only finding here that is an execution
bypass. A sibling seat may independently own that function.

### RSP-2 — Medium — the `extensions.worktreeConfig` grant is writable from `config.worktree` and leaks across worktrees
`tools/souji-census.sh:633-639`, `654-665`, `741`, `773-794`.

git derives the grant only from the common config: git-config(1) §FILES —
*"`$GIT_DIR/config.worktree` ... is optional and is only searched when
`extensions.worktreeConfig` is present in `$GIT_DIR/config`"*; git-worktree(1) — *"When
`extensions.worktreeConfig` is enabled, the config file `.git/worktrees/<id>/config.worktree`
is read after `.git/config` is."* The scanner instead writes the global `CFG_WT_ENABLED` from
**any** scanned file, including `config.worktree` itself (633–639, reached through 663), and
line 741 hands the *current* value to every linked-worktree admin. Concrete shape: `.git/config`
sets `worktreeConfig = true`; `.git/config.worktree` sets `worktreeConfig = false`; the linked
worktree's `worktrees/w1/config.worktree` carries `[include] path = <store>`. The main
`config.worktree` scan flips the flag at 638; 741 then passes `0`; `guard_wt_config` returns
early at 656; w1's `config.worktree` is never scanned, although `git status` in w1 (reached at
1072) reads it. The compensating scan of w1's file at 829 runs only later, via
`worktree_extra_flags`→`guard_git_surface` (1068, 1117), and only when the worktree directory
exists; `count_worktrees` (1111) runs first. I did not execute the end-to-end path, so
exploitability is unverified — but the state model is wrong regardless, and guard soundness
should not depend on command order.

Minimal patch — `guard_wt_config` (654–665) saves and restores the grant, because a record in
`config.worktree` must not change it:

```bash
guard_wt_config() { # $1 resolved gitdir (main or linked admin)
  local dir=$1 wtc="$1/config.worktree" saved=$CFG_WT_ENABLED
  [ "$CFG_WT_ENABLED" = 1 ] || return 0
  ...
  CFG_STACK=()
  if ! scan_config_file "$dir" "$wtc" 0; then CFG_WT_ENABLED=$saved; return 1; fi
  CFG_WT_ENABLED=$saved
  return 0
}
```

### RSP-3 — Low — control characters in a config path still force a whole-run exit 2 under a `git-config-unsupported` reason
`tools/souji-census.sh:526-528` (the case), call sites 614, 624, 631.

`guard_config_path` turns any `\n`, `\t` or `\r` in the raw path into
`protected_fail "$reason"` (526–528), and `protected_fail` always exits 2 for the whole run —
even when the caller's reason is `git-config-unsupported` (624, 631). That contradicts the
round's declared shapes (header 90–97: only a config-named path reaching a protected root
refuses; a config that cannot be evaluated degrades to one `error` row) and the C1 wording
("only a protected-namespace reach keeps whole-run exit 2"). Concrete benign case:
`core.excludesFile = "patterns\tfile"` — a tab inside a quoted value is legal, git opens that
file, and nothing touches the store — yet the entire fleet run exits 2 with
`path-protected: git-config-unsupported`. Likewise an `include.path` value containing a
newline that names a nonexistent file (git: missing include targets are benign; fixture line 35)
refuses the whole run. Low severity because such values are contrived, but it is the r14
"benign value → whole-run refusal" shape the round exists to remove, and the refusal label is
factually wrong for these cases.

Minimal patch — pre-test the value in `scan_config_file` before it reaches
`guard_config_path` (insert once after each emptiness guard at 610, 620, 627):

```bash
        case "$val" in *$'\n'*|*$'\t'*|*$'\r'*)
          cfg_soft "git-config-unsupported"; return 1 ;;
        esac
```

This degrades to the promised per-repository `error` row and, because the value never reaches
`guard_config_path`/`resolve_guarded`, also avoids `resolve_guarded`'s hard `ambiguous-path`
refusal (380) for these inputs.

## 3. Residual risk and verification gaps

- All three findings are unexecuted (source inspection only). RSP-2's exploitability hinges on
  whether any command between the skip at 741/794 and the later scan at 1068–1117 reads a
  linked worktree's `config.worktree`.
- Fixture coverage gaps matching the findings: no trailing-newline filter command value
  (503–506); no `extensions.worktreeConfig` record inside `config.worktree` (600–626); no
  control-character path values.
- `git config --list` runs twice per file (589 and 592). A change between the calls yields an
  empty capture and a silent `return 0`; this is not a new atomicity hole (header 115–119
  concedes guard-vs-access is not atomic), but a single captured read would remove one window
  and one fork per config file.
- `includeIf` conditions are deliberately not evaluated (fixture 32–36), so a non-matching
  `includeIf` naming a protected path still forces exit 2. Pinned by the fixture; not a finding.
- `sec`/`var` folding is locale-sensitive but no-op on canonical keys (§1.4); only a risk if a
  future change relies on it for non-canonical input without `LC_ALL=C`.

STATUS: no defect in the `scan_config_file` key/subsection/variable split; RSP-1 (High) is a
real filter-execution bypass in the same `--list -z` record idiom, RSP-2 (Medium) is a
`worktreeConfig` state-model defect, RSP-3 (Low) is a declared-shape contract mismatch. No
check was executed against a real repository.

## Commands

Transcribed from the session. Every command was read-only inspection of the named file,
named revisions, or the installed man pages. One temporary copy of the target was written to
`/var/tmp/r16-revscan-target.sh` and deleted in the next command; it was never executed and not
used for any result below. No census invocation, no fixture, no synthetic repository, no
`census/operator-sweep-20261019/`, `~/.omp`, `.ufo/state`, `.ufo/watchdog.log`, `MANIFEST.json`
or sibling-lane access occurred. `git status --porcelain -uno` was used once to confirm the
worktree is clean (read-only); it is not in the enumerated probe list, nor are `wc`, `diff`,
`ls`, `zcat|col` (doc reading) — recorded here for the L1 audit.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l && git rev-parse HEAD && git status --porcelain=v1 -uno | wc -l
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/r16-revscan-target.sh 2>/dev/null; sha256sum /var/tmp/r16-revscan-target.sh; wc -l /var/tmp/r16-revscan-target.sh
rm -f /var/tmp/r16-revscan-target.sh; cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n "scan_config_file\|config --list\|--list -z\|config_list\|config" | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n "^[a-zA-Z_][a-zA-Z0-9_]*()\s*{\|^function " | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '505,690p' | cat -n | awk '{printf "%d\t%s\n", $1+504, substr($0, index($0,$2))}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | awk '{printf "%5d|%s\n", NR, $0}' | sed -n '1,140p'
man git-config 2>/dev/null | col -b | grep -n -A14 -- '^ *--null' | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=1 && NR<=170 {printf "%5d|%s\n", NR, $0}'
ls -l /usr/share/man/man1/git-config.1.gz /usr/share/doc/git/ 2>&1 | head -20; command -v man col zcat
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n "LC_ALL\|LANG\|export LANG"
zcat /usr/share/man/man1/git-config.1.gz | grep -n -i -m 40 -E 'lowercase|case sensitive|case-insensitive|subsection|deprecated'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n -i "worktreeconfig\|worktree_config\|empty\|bare" | grep -v "^1[0-9][0-9]:"
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -B12 -A16 'spelled in lowercase'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -B4 -A12 'null character'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | awk 'NR>=560 && NR<=650 {printf "%5d|%s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat cc21683 cbf688ab -- tools/souji-census.sh && echo "=== diff cc21683..cbf688ab (config region) ===" && git diff -U3 cc21683 cbf688ab -- tools/souji-census.sh | grep -n "" | sed -n '1,120p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat b410186 cbf688ab -- tools/souji-census.sh; echo "=== b410186..cbf688ab ==="; git diff -U2 b410186 cbf688ab -- tools/souji-census.sh | wc -l; git diff --stat a31642d cbf688ab -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && diff <(git show b410186:tools/souji-census.sh | sed -n '/^scan_config_file()/,/^}/p') <(git show cbf688ab:tools/souji-census.sh | sed -n '/^scan_config_file()/,/^}/p') && echo IDENTICAL; echo "--- b410186 syntax ---"; git show b410186:tools/souji-census.sh | bash -n /dev/stdin; echo "b410186 bash -n rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tools/souji-census.sh | bash -n /dev/stdin; echo "changed bash -n rc=$?"; git show cbf688ab:tools/souji-census.sh | shellcheck -s bash -f gcc - 2>&1 | grep -n "scan_config_file\|config" | sed -n '1,40p'; echo "shellcheck done"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tools/souji-census.sh | awk 'NR>=700 && NR<=840 {printf "%5d|%s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tools/souji-census.sh | awk 'NR>=860 && NR<=960 {printf "%5d|%s\n", NR, $0}'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -i -B6 -A14 'worktreeConfig'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -i -B8 -A10 'taken to be true\|no value is\|implicit'
zcat /usr/share/man/man1/git-config.1.gz | col -b | sed -n '1390,1425p'
zcat /usr/share/man/man1/git-worktree.1.gz | col -b | grep -n -B4 -A18 'worktreeConfig'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tools/souji-census.sh | awk 'NR>=1035 && NR<=1170 {printf "%5d|%s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tools/souji-census.sh | awk 'NR>=197 && NR<=240 {printf "%5d|%s\n", NR, $0}' && git show cbf688ab:tools/souji-census.sh | awk 'NR>=365 && NR<=460 {printf "%5d|%s\n", NR, $0}'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tests/fixtures/r15-census-config.py | grep -n "filter\|SENTINEL\|sentinel" | sed -n '1,60p'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -B3 -A9 'newline, and' | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tests/fixtures/r15-census-config.py | awk 'NR>=490 && NR<=520 {printf "%5d|%s\n", NR, $0}'; git show cbf688ab:tests/fixtures/r15-census-config.py | awk 'NR>=1224 && NR<=1240 {printf "%5d|%s\n", NR, $0}'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -B2 -A10 '^core\\.worktree$\|core\.worktree$' | sed -n '1,50p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab:tests/fixtures/r15-census-config.py | awk 'NR>=595 && NR<=632 {printf "%5d|%s\n", NR, $0}'
zcat /usr/share/man/man1/git-config.1.gz | col -b | sed -n '1030,1065p'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -A9 'Set the path to the root of the working tree'
zcat /usr/share/man/man1/git-config.1.gz | col -b | grep -n -A6 'excludesFile' | sed -n '1,40p'
zcat /usr/share/man/man1/git-config.1.gz | col -b | sed -n '3960,3968p'
```
