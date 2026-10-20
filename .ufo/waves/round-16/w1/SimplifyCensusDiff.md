# SimplifyCensusDiff — YAGNI review of the r16 census diff

Scope: `git diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh`
(299 insertions / 54 deletions; file is 1784 lines at `cbf688a`, sha256
`fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`, extracted
with `git show`). **No repo file was edited.** All experiments ran on a copy under
`/var/tmp/souji-r16-SimplifyCensusDiff/`, deleted at the end.

## Axes

- **A1 operability (judged axis).** A deletion is only admissible if exit codes,
  stderr strings, row counts and the refusal set stay identical. Nothing below
  changes a single emitted byte.
- **A2 review surface.** The duplicated guard copies are the drift machine: r16
  patched the *same four statements twice* (`guard_git_config`, `first=$dir`,
  `guard_wt_config "$first"`, and the `exit 2`→`return 1` mapping appear in both
  `guard_git_surface` branches). Every future config change must be made twice.
- **A3 weight.** Lines and spawned processes.

Accepted: A2 improves, A3 improves, A1 untouched. Rejected: anything that would
trade A1 for A3.

## Accepted deletions (5 local + 1 structural) — net −34 lines, verified parse-clean

Conditional arithmetic: −33 if a bound-filter propagation patch lands first, because
that patch re-adds A4's `recs=()` line (see A4). All other hunks are disjoint from
the known in-flight work.

All line numbers are in `tools/souji-census.sh` at `cbf688a`.

### A1 — `guard_config_path` re-implements `resolve_guarded`'s own pre-checks (lines 526–531, −6)

```
526:  case "$raw" in
527:    *$'\n'*|*$'\t'*|*$'\r'*) protected_fail "$reason" "$dir" "$cfg" ;;
528:  esac
529:  if protected_reason_input "$(lexical_abs "$raw")" >/dev/null; then
530:    protected_fail "$reason" "$dir" "$cfg"
531:  fi
```

Delete all six lines; keep `local …` (525) and the `resolve_guarded` block (532–534).

Proof (not a guess — both checks are inside the call that follows):
- `resolve_guarded "$raw" 1 1` (`tools/souji-census.sh:365-445`) with
  `allow=1` sets `lex=$raw` for an absolute raw (the documented contract of `$4`),
  then executes the *same* control-character refusal (`*$'\n'*|*$'\t'*|*$'\r'*`)
  and, because `final=1`, `protected_reason_input "$lex"`.
- `protected_reason_input` normalises with `lexical_abs` itself (line 346), so
  `protected_reason_input "$(lexical_abs "$raw")"` is *literally the same call
  with the same value* as `protected_reason_input "$lex"`.
- Every inner failure is `exit 2` inside the command substitution
  `resolved=$(… 2>/dev/null)`; the outer `if !` then runs
  `protected_fail "$reason" "$dir" "$cfg"` — byte-identical stderr and exit 2,
  because the inner message is suppressed by `2>/dev/null`.
- No syscall ordering regression: the final-input check happens *before* the
  component walk, so no `stat`/`readlink` touches a protected path either way.
  The fixture's `no_open` assertions observe `openat`, unaffected.

### A2 — `status_info_file` repeats the same lexical pre-check (lines 894–896, −3)

```
894:  if protected_reason_input "$(lexical_abs "$tgt")" >/dev/null; then
895:    printf '/dev/null'; return 0
896:  fi
```

Identical proof, sharpened by `SoujiR16.RevBoundFilters` (bytes-checked): line 897
already calls `resolve_guarded "$tgt" 1 1`, and because that call is inside
`tgt=$( … )` its `protected_fail` `exit 2` ends only the command-substitution
subshell, with stderr already discarded by `2>/dev/null`; the enclosing
`if tgt=$(…) && [ -f "$tgt" ]` therefore falls through to the existing
`printf '/dev/null'` else-branch. Same output, same rc 0. The ancestor half of
`protected_reason_input` cannot rescue the pre-check either: `tgt` is always
`$base/git/<ignore|attributes>`, so the only reachable overlap with a protected
root is equal-or-descendant, which the walker refuses inside the subshell and the
same call site converts to `/dev/null`.

### A3 — `guard_git_config`'s inherited parameter is a self-assignment (line 675, 1→1)

```
675:  if [ -n "${2:-}" ]; then CFG_WT_ENABLED=$2; else CFG_WT_ENABLED=0; fi
```
→
```
  [ -n "${2:-}" ] || CFG_WT_ENABLED=0
```

The only two-argument call site is line 741
`guard_git_config "$admin" "$CFG_WT_ENABLED"`, i.e. `$2` *is* the global being
assigned — the `then` branch is a no-op. The `else` branch is the whole behaviour.
(The same argument says the parameter can be dropped entirely, but that would cost
4 explicit `CFG_WT_ENABLED=0` lines at 773/789/812/828 and lose the inheritance
site at 741 — net worse. Keep the parameter.)

### A4 — `recs=()` before `mapfile` is dead (line 921, −1)

```
920:  [ "${#drivers[@]}" -gt 0 ] || return 0
921:  recs=()
922:  mapfile -d '' -t recs < <(…
```

`mapfile` clears the target array before assigning unless an explicit origin is
given with `-O` (bash(1), `mapfile`; the wording was cross-checked by
`SoujiR16.RevBoundFilters` — my own basis was `[INFERENCE]` until then), so 921
has no effect; the `drivers` array was already consumed.
**Order dependence:** the landed bound-filter propagation patch replaces exactly
this region (cbf688a 921–926) and re-adds `recs=()`; that re-add is harmless, so
A4 is observable only when applied alone. Treat it as cosmetic, not as a saving
to bank.

### A5 — `2>&1` after `>/dev/null` in `protected_fail` (line 186, −0)

```
186:  if [ -n "$shown" ] && protected_reason_inside "$shown" >/dev/null 2>&1; then
```
→ `… "$shown" >/dev/null; then`

`protected_reason_inside` writes only to stdout (`printf '%s' "$reason"`, lines
330–343); `2>&1` re-points stderr at the already-null stdout. Dead token, and it
is the only `2>&1` in the file's predicate calls.

### A6 — `guard_git_surface`: the `.git`-dir and `.git`-file branches are one chain duplicated (lines 763–836, −24)

This is the "duplicated guard logic" the item asks for, and the reason r16 needed
four paired edits. Both branches run the identical 22-statement chain after
deriving `dir` (compare 769–795 with 809–834). Flatten the two entry tests and
keep the chain once; `-f` and `-d` are mutually exclusive, and `-L` is still
tested first, so the `-f`/`-d` reordering in the entry tests cannot change
behaviour. No helper function, no global out-parameter — a helper called in a
`$( … )` would lose `CFG_WT_ENABLED` (read later at line 741) and
`CFG_SOFT_REASON` (read at 1089), because `guard_git_config`/`guard_wt_config`
mutate globals; flattening keeps everything in the caller's shell.

Replacement (50 lines, was 74):

```bash
guard_git_surface() { # $1 repo dir; exits 2 on a protected reach, rc 1 on a degraded repo
  local repo=$1 g="$1/.git" target common dir first
  if [ -L "$g" ]; then
    guard_target git-metadata "$g" >/dev/null
    return 0
  fi
  if [ -f "$g" ]; then
    IFS= read -r target < "$g" || target=""
    case "$target" in
      gitdir:*) target=${target#gitdir:} ;;
      *) return 0 ;;
    esac
    target=${target#"${target%%[![:space:]]*}"}
    [ -n "$target" ] || protected_fail "unresolved-path" "$repo" "$g"
    case "$target" in
      /*) ;;
      *) target="$repo/$target" ;;
    esac
    dir=$(guard_target gitdir "$target") || exit 2
  elif [ -d "$g" ]; then
    dir=$(guard_target gitdir "$g") || exit 2
  else
    return 0
  fi
  guard_git_links "$dir" || exit 2
  guard_git_files "$dir" || exit 2
  guard_git_config "$dir" || return 1
  first=$dir
  common="$dir/commondir"
  if [ -L "$common" ]; then
    guard_target git-common-dir "$common" >/dev/null
  elif [ -f "$common" ]; then
    IFS= read -r target < "$common" || target=""
    target=${target#"${target%%[![:space:]]*}"}
    if [ -n "$target" ]; then
      case "$target" in
        /*) ;;
        *) target="$dir/$target" ;;
      esac
      dir=$(guard_target git-common-dir "$target") || exit 2
      guard_git_links "$dir" || exit 2
      guard_git_files "$dir" || exit 2
      guard_git_config "$dir" || return 1
      guard_wt_config "$first" || return 1
    fi
  fi
  guard_alternates "$dir" || exit 2
  guard_worktree_registrations "$dir" || return 1
  return 0
}
```

Statement-by-statement equivalence: the `.git`-file branch's `non-gitdir → return 0`,
`empty target → protected_fail unresolved-path`, relative-target rebasing and
`guard_target gitdir` all move intact into the `if [ -f "$g" ]` arm; the `.git`-dir
branch's derive is unchanged; the terminal `return 0` covers both arms (the file
branch previously fell through to line 835, same result).

## Rejected candidates (kept, with the reason)

| # | Site | Why it is not deleted |
|---|---|---|
| R1 | `"${CFG_STACK[@]+"${CFG_STACK[@]}"}"` 583, 594; `"${recs[@]+…}"` 910 | `mapfile -d` already requires bash ≥ 4.4, where plain `"${a[@]}"` is nounset-safe, so the `+` guards are redundant — but the file already carries this idiom at **9 pre-existing sites**; deleting only the new three would create the second convention the role forbids. |
| R2 | `[ "$bare" = 1 ] \|\| [ -z "$val" ]` 610, 620, 627 | Logically subsumed (`bare=1` ⇒ `val=""` by construction at 595–597), zero lines saved, and the disjunct documents "bare key has no value". Optional at best. |
| R3 | `\|\| true` inside `<( … )` at 911 and 925 | Provably without effect (a process substitution's status is never observed), but every other `|| true` in this file sits in a `$( … )` whose status *is* observed under `set -e`; removing two makes the idiom locally inconsistent for 2 tokens. |
| R4 | `git config --type=bool --get` re-read at 635 | Could be a 6-arm `case "${val,,}"` saving one spawn, but it would replace git's own boolean grammar (case-insensitive true/yes/on/1, false/no/off/0, empty=false, bare=true) with a copy. The spawn is the authority for "invalid boolean ⇒ `git-config-unparsed`"; drift risk > one spawn. |
| R5 | `git config --file "$cfg" --no-includes --list -z` run twice (589 + 592) | One spawn is the parse-status oracle, the other captures records. A single spawn needs a temp file (new machinery), `shopt -s lastpipe` (a global pipeline-semantics switch), or `$( … )` capture (bash drops NUL bytes ⇒ corrupt `-z` parse). Keep both. |
| R6 | `sec`/`var`/`rest`/`sub` derivation 598–601 → one lowered-key `case` | **Not** behaviour-identical: the current `"$sec:$var"` match is deliberately loose (`core.foo.excludesfile` matches `core:excludesfile`), i.e. fail-closed over-inclusion. Narrowing it would shrink the refusal set. |
| R7 | `CFG_STACK=()` 662 in `guard_wt_config` | Dead for every current caller (each is preceded by `guard_git_config`, which clears on success and `return 1`s before `guard_wt_config` on failure; stale cross-repo entries can never equal another repo's `config.worktree`). Buys 1 line at the cost of the local invariant that makes the stack discipline auditable — L1's call, I would keep it. |
| R8 | `${CFG_SOFT_REASON:-git-config-unsupported}` 1089 | Unreachable by construction (all rc-1 returns go through `cfg_soft`), but it is the only thing standing between a future `return 1` and an empty reason in the error row. Keep. |
| R9 | Extract the shared chain into a helper instead of flattening | A `$( … )` helper loses the `CFG_*` globals (see A6); a `local -n` or `GUARD_DIR` out-parameter is a new convention. Flattening (A6) gets the dedup for free. |

## Documentation defects (deletions of stale prose, not code)

- **D1 (fixed by A6's header).** Line 763 says `guard_git_surface` "exits 2 on a
  protected/unsupported git surface". Since r16, "unsupported" (unevaluable
  config) is `return 1` → one `error` row at exit 0. The doc is stale; A6's
  replacement comment states the real contract.
- **D2 (keep, reword).** Lines 904–905: "could run during status: **refuse**
  (round 16)". `guard_bound_filters` does not refuse: it returns 1 and
  `count_dirty` (940–944) emits `status-skipped` + `unverifiable` for that repo
  only, exit 0. The header prose (100–104) is the authoritative one; the function
  comment is a leftover from the refuse-everything era.
- **D3 (out of r16 scope).** `guard_git_pointer` (706–710) is a resolver whose
  last line `[ -n "$admin" ] || return 0` is a no-op tail. Pre-existing, present
  identically in `cc21683`; not touched by this diff.
- **D4 (latent contradiction, do not "fix" by deletion).** `status_info_file`
  lines 877–879 promote an unexpandable `~user`/`%(prefix)` value to a whole-run
  `exit 2`, while the header (lines 96–98) promises one `error` row. It is
  unreachable today because `scan_config_file` soft-fails the same value first
  (`census_one` line 1087 returns before `count_dirty`), so C1's prose holds — but
  it is the one place where a config-named path can still kill the run. Keep the
  net; if a later change lets status run on a soft-failed config this becomes a
  whole-run refusal again.
- **D5 (correctness, not a deletion — verified, from `SoujiR16.RevBoundFilters`).**
  `guard_bound_filters` lines 913–914 classify "record ends with newline" as
  "empty value" (comment 913, `case "$rec" in *$'\n') continue ;; esac` 914;
  `drivers+=("$name")` at 918 is guarded by nothing else). With
  `git config -z --get-regexp`, a *bare* key emits `key\0`, an empty value emits
  `key\n\0`, and a value that legitimately ends in a newline emits `key\ncmd\n\0`
  — so a double-quoted `clean = "cmd\n"` (a non-empty command per config.c
  `\n` handling, and `convert.c apply_filter` runs any `cmd && *cmd`) is skipped
  as inert and the driver can then run during status for a tracked path bound by
  `.gitattributes`. `b410186:742` classified by the value part
  (`if [ -n "$v" ]; then CFG_DRIVERS+=("$sub"); fi`) and is the right shape; r16
  keyed it on the record. No deletion of mine touches this line, but no
  simplification here should be merged in a way that freezes it. The correct
  test is the value part — `[ -n "${rec#*$'\n'}" ]` (bare key ⇒ empty ⇒ inert;
  `cmd\n` ⇒ non-empty ⇒ driver counted) — which is r15's `[ -n "$v" ]` shape.

## Anti-deletion warning (would be a false positive)

ShellCheck reports `SC2329` at line 173 (`usage_err` "never invoked"). It is a
false negative of shellcheck: `usage_err` has live call sites (1257, 1258, 1262
and further), and the same note exists at line 149 of `cc21683`. Do not delete it.
The other four shellcheck notes are `SC2094` false positives on
`tr -d '\000' < "$cfg" | cmp -s -- - "$cfg"` (line 586) — reading a file while
comparing it to stdin is the intent.

## Adjacent observations (other lanes, no action taken here)

1. `guard_bound_filters` fails **open**: if `ls-files | check-attr` errors, the
   pipeline's `2>/dev/null || true` leaves `recs` empty, the loop finds nothing
   and the function returns 0, i.e. status runs as if no filter were bound.
   Correction from `SoujiR16.RevBoundFilters` (verified here): deleting the two
   `|| true` tokens (my R3) does **not** close it — `mapfile` from `< <( … )`
   cannot see the producer's status at all, and `2>/dev/null` hides the error.
   Two shapes close it: a status sentinel record inside the substitution plus a
   pre-loop `len % 3` test (no `$!` dependency), or — what the dirty-tree patch
   does, unattributed in-flight executor work, see the drift note — `pid=$!`
   after the `mapfile` with `wait "$pid" || return 1` and the same `% 3` test.
   That form is the BCS process-substitution exit-capture idiom, but it rests on
   `$!` being the substitution PID: if `$!` is empty or stale, `wait` returns 127
   and `return 1` fires for **every** repo that defines any
   `filter.<n>.{clean,smudge,process}` key, so all of those rows lose their
   accurate dirty count (status-unverifiable), not just the bound ones. Pin the
   assumption in a comment, or use the sentinel form.
   `b410186:1086-1097` carried it by `if ! bound=$( … | awk …)` under the global
   `pipefail` (`set -euo pipefail` at 135), and its consumer at 1289 mapped
   `checkattr-fail` to a per-repo `error` row — so r16's fail-open is a
   regression from a per-repo degrade, not from an absent check. R3 therefore
   stays a token cleanup, never a fix. D5 below is the
   second defect in the same function: the "empty value" test is keyed on the
   record, not the value.
   Caveat on citing that revision for *shape*: `b410186` does not parse —
   `bash -n` stops at line 1368 with `syntax error near unexpected token '}'` —
   so its constructs are source-level precedent only, not runnable prior art.
2. Cost model of the new guard: per config file, `2` spawns for `--list -z`
   (R5, deliberate), plus `1` per `extensions.worktreeConfig` line (R4,
   deliberate). When both the worktree config and the common config enable
   `worktreeConfig`, `$first/config.worktree` is scanned twice (773's internal
   `guard_wt_config` and 790) — 2 wasted spawns, but the two calls have *different*
   gates (own config vs common config), so they are not interchangeable. Keep.
3. `list_repos` runs `guard_git_surface` and then `census_one` runs it again for
   the same repo (1176/1181/1206 + 1087) — pre-existing double scan, owned by
   `SoujiR16.RevListReposDoubleScan`, not introduced here.
4. The fixture's `CONFIG_REASONS` allowlist (tests/fixtures/r15-census-config.py:958-975)
   contains `config-worktree-protected`, which neither `cc21683` nor `cbf688a`
   ever emits. Allowlist broader than the emitter — fixture lane.

## Verification performed (on the scratch candidate only)

- `bash -n candidate.sh` → `parse-ok`.
- `shellcheck -f gcc candidate.sh` → exactly the same five notes as the original
  (`SC2329` + four `SC2094`), only line numbers shifted; no new findings.
- `wc -l`: 1784 → 1750 (−34 lines; `git diff --no-index --stat` reports
  31 insertions / 65 deletions, the 31 being A6's re-indented chain).
- Behaviour was **not** executed (census runs are forbidden to this seat); the
  equivalence arguments above are static and each names the mechanism.
- Scratch directory `/var/tmp/souji-r16-SimplifyCensusDiff/` used and then
  deleted. **I wrote nothing in the lane tree — but the lane tree has since moved
  past `cbf688a` on its own**: `git status` shows ` M tools/souji-census.sh`
  (uncommitted; `HEAD` is `cbf688a`). It is **unattributed executor work** —
  neither this seat nor `SoujiR16.RevBoundFilters` (review-only, owns only its
  own report) wrote it; `git diff --numstat` read `138 68` when I measured it and
  the patch is still moving, so treat any count as a snapshot. The in-flight
  change adds soft-finding
  accumulation with `soft=1` in `guard_git_surface`, rc 3 (`degrade`) returns
  from `guard_config_path`/`status_info_file`, spelled-name include bases, and a
  `set -o pipefail` + `pid=$!` + `wait` propagation in `guard_bound_filters`.
  Therefore **every line number here is a `cbf688a` anchor; apply by quoted
  text, not by offset.** Applicability against the live file:
  - A6 is *more* valuable there, not less: the live patch had to make the same
    `soft=1` edit **eight times** in the two `guard_git_surface` copies.
  - A1/A2 stay rc-equivalent (the live `guard_config_path` decides
    protected-vs-unresolvable by matching the `path-protected: <reason> ` text
    captured with `2>&1`; `resolve_guarded`'s own pre-walk check emits exactly
    that text, so the deleted pre-checks are still redundant), but the
    equivalence now rests on that message-text parse — re-verify before applying.
  - A3, A4, A5 are still present verbatim in the live file.
  - Adjacent #1 is being fixed in-tree (`wait "$pid" || return 1` + a `% 3`
    check, i.e. fail-closed). D5's `case` is still live at line 943.

**STATUS: complete — 6 deletions proposed (net −34 lines, parse/lint clean,
behaviour-identical by construction), 9 rejected with reasons, plus one verified
correction (adjacent #1) and one new correctness finding (D5) from the
`SoujiR16.RevBoundFilters` exchange. No known failure.**

## Commands

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 --stat -- tools/souji-census.sh && echo '---' && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | wc -l
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cc21683 cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/souji-r16-SimplifyCensusDiff/census-new.sh 2>/dev/null || (mkdir -p /var/tmp/souji-r16-SimplifyCensusDiff && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/souji-r16-SimplifyCensusDiff/census-new.sh); git show cc21683:tools/souji-census.sh > /var/tmp/souji-r16-SimplifyCensusDiff/census-old.sh; wc -l /var/tmp/souji-r16-SimplifyCensusDiff/*.sh
cd /var/tmp/souji-r16-SimplifyCensusDiff && grep -n 'guard_git_config\|CFG_WT_ENABLED\|CFG_STACK\|CFG_SOFT_REASON\|cfg_soft\|guard_config_path\|expand_config_path\|guard_config_file_kind\|scan_config_file\|guard_wt_config' census-new.sh
cd /var/tmp/souji-r16-SimplifyCensusDiff && sed -n '1,60p' census-new.sh | grep -n 'set -' ; echo '--- set flags:'; grep -n '^set ' census-new.sh; echo '--- bash-version guard:'; grep -n 'BASH_VERSINFO\|bash 4\|bash5' census-new.sh; echo '--- protected_reason_input / lexical_abs / resolve_guarded / sanitize_field defs:'; grep -n 'protected_reason_input()\|lexical_abs()\|resolve_guarded()\|sanitize_field()\|guard_target()\|protected_reason_inside()' census-new.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls tests/fixtures/ | head -40; echo '=== grep assertions ==='; grep -n 'include-protected\|ambiguous-path\|git-config-unsupported\|protected>\|<protected>' tests/fixtures/r15-census-config.py | sed -n '1,60p'
cd /var/tmp/souji-r16-SimplifyCensusDiff && grep -n 'protected_reason_input "$(lexical_abs\|case "$raw" in\|if \[ -n "${2:-}" \]; then CFG_WT_ENABLED\|CFG_STACK=()\|recs=()\||| true)$\||\[ "$bare" = 1 \] || \[ -z "$val" \]' census-new.sh
cd /var/tmp/souji-r16-SimplifyCensusDiff && echo '=== protected_fail call arity ==='; grep -n 'protected_fail ' census-new.sh | wc -l; echo '--- 2-arg-looking calls:'; grep -nE 'protected_fail "[^"]*" *$|protected_fail "[^"]*" *\)' census-new.sh; echo '=== bracket-guard idiom counts (new vs old) ==='; grep -c '\[@\]+' census-new.sh; grep -c '\[@\]+' census-old.sh; echo '=== mapfile -d usage (old) ==='; grep -n 'mapfile' census-old.sh | head -20
cd /var/tmp/souji-r16-SimplifyCensusDiff && echo '=== guard_git_pointer call sites ==='; grep -n 'guard_git_pointer' census-new.sh; echo '=== old-file guard_git_pointer ==='; grep -n 'guard_git_pointer' census-old.sh; echo '=== shellcheck version ==='; shellcheck --version | head -3; echo '=== bash -n new ==='; bash -n census-new.sh && echo parse-ok; echo '=== shellcheck new (only new funcs) ==='; shellcheck -S warning census-new.sh 2>&1 | sed -n '1,40p'
cd /var/tmp/souji-r16-SimplifyCensusDiff && echo '=== shellcheck all severities ==='; shellcheck -f gcc census-new.sh 2>&1 | head -30; echo '=== rc ==='; shellcheck -f gcc census-new.sh >/dev/null 2>&1; echo $?
cd /var/tmp/souji-r16-SimplifyCensusDiff && shellcheck -f gcc census-old.sh 2>&1 | head -20; echo '=== RC2329 in old ==='; shellcheck -S note -f gcc census-old.sh 2>&1 | grep SC2329
cd /var/tmp/souji-r16-SimplifyCensusDiff && echo '=== usage_err occ ==='; grep -n 'usage_err' census-new.sh census-old.sh; echo '=== config-worktree-protected ==='; grep -n 'config-worktree-protected' census-new.sh census-old.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py; echo '=== git-metadata-nonregular emitters ==='; grep -n 'git-metadata-nonregular' census-new.sh | head
cd /var/tmp/souji-r16-SimplifyCensusDiff && diff -u census-old.sh census-new.sh | grep -c '^+' ; echo '--- old guard_git_config block:'; sed -n '/^guard_git_config()/,/^}/p' census-old.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'ambig\|tabular\|\\\\t\|newline\|control\|%\(prefix\)\|%(prefix)\|~user' tests/fixtures/r15-census-config.py | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'reason\|stderr' tests/fixtures/r15-census-config.py | sed -n '1,80p'
cd /var/tmp/souji-r16-SimplifyCensusDiff && cp census-new.sh candidate.sh && sha256sum census-new.sh candidate.sh
cd /var/tmp/souji-r16-SimplifyCensusDiff && bash -n candidate.sh && echo 'parse-ok'; echo '=== shellcheck candidate ==='; shellcheck -f gcc candidate.sh 2>&1; echo "rc=$?"; echo '=== line counts ==='; wc -l census-new.sh candidate.sh
cd /var/tmp/souji-r16-SimplifyCensusDiff && git diff --no-index --stat census-new.sh candidate.sh; echo '---'; git diff --no-index -U0 census-new.sh candidate.sh | grep -E '^[-+][^-+]' | head -60
rm -rf /var/tmp/souji-r16-SimplifyCensusDiff && ls -d /var/tmp/souji-r16-SimplifyCensusDiff 2>&1; echo "cleanup-rc=$?"
# --- follow-up after the RevBoundFilters IRC message (r15 precedent check) ---
mkdir -p /var/tmp/souji-r16-SimplifyCensusDiff && cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh > /var/tmp/souji-r16-SimplifyCensusDiff/r15.sh && cd /var/tmp/souji-r16-SimplifyCensusDiff && wc -l r15.sh && bash -n r15.sh; echo "bash-n-rc=$?"
cd /var/tmp/souji-r16-SimplifyCensusDiff && grep -n 'rec#\*\|case "$rec"\|\[ -n "\$v" \]\|guard-check\|bound=\$(git\|check-attr' r15.sh | head -20
cd /var/tmp/souji-r16-SimplifyCensusDiff && sed -n '735,750p' r15.sh; echo '=== 1080-1100 ==='; sed -n '1080,1100p' r15.sh; echo '=== 1355,1370 ==='; sed -n '1355,1370p' r15.sh
cd /var/tmp/souji-r16-SimplifyCensusDiff && grep -n '^set ' r15.sh; echo '=== checkattr consumers ==='; grep -n 'checkattr-fail\|unsupported)' r15.sh | head; echo '=== count_dirty r15 ==='; grep -n 'checkattr\|unverifiable' r15.sh | head -20
cd /var/tmp/souji-r16-SimplifyCensusDiff && sed -n '1360,1380p' r15.sh; echo '=== r15 line 1368 raw ==='; sed -n '1368p' r15.sh; echo '=== case/esac counts ==='; grep -c '^[[:space:]]*case ' r15.sh; grep -c '^[[:space:]]*esac' r15.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain -- tools/souji-census.sh; git log --oneline -3 -- tools/souji-census.sh; echo '=== diff live vs cbf688a ==='; git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | sed -n '60,200p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh | sed -n '200,300p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n 'An explicitly empty value\|case "$rec" in\|drivers+=("$name")\|^guard_bound_filters\|^  \[ "${#drivers\[@\]}" -gt 0 \]\|^  recs=()$\|protected_reason_inside "$shown"'; echo '=== scratch state ==='; ls -A /var/tmp/souji-r16-SimplifyCensusDiff 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --numstat cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh; git status --porcelain -- tools/souji-census.sh; git rev-parse --short HEAD
rm -rf /var/tmp/souji-r16-SimplifyCensusDiff && ls -d /var/tmp/souji-r16-SimplifyCensusDiff 2>&1; echo "cleanup-rc=$?"
```

(`sed -n` above only prints named-file ranges — it was never used to edit. The
`r15.sh` `bash -n` result is the parse-failure fact cited in D5. `git status`
is the drift fact in "Verification performed". File reads and the numbered
`grep` tool calls on the same exact paths are tool calls, not shell commands; no
other command was run. No tool install or upgrade was needed.)
