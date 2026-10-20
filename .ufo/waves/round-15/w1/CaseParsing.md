# Round 15 · w1 · CaseParsing (reviewer)

Axes: operability (C1), calibration (C2 scope only where it touches config parsing).
Mode: source inspection only. No tests, probes, builds, or edits. Nothing installed or upgraded.
Not read: `census/operator-sweep-20261019/`, `~/.omp/agent/**`, any auth or credential file.
Git references: installed `git` 2.55.0 man page `git-config(1)` (`/usr/share/man/man1/git-config.1.gz`) and upstream source at tag `v2.55.0` (`config.c`, `builtin/config.c`, `setup.c`), fetched from raw.githubusercontent.com. Line numbers below are upstream line numbers.

## Scope of the current guard (as read)

- `tools/souji-census.sh:493-522` `guard_git_config`:
  - `:500` `keys=$(git config --file "$cfg" --no-includes --name-only --list)`. Values are never printed, so values cannot be parsed as keys. Good.
  - `:503` `keys=${keys,,}`, then `:504-507` a single `case "$keys" in` glob over the **whole newline-joined list**.
  - `:511` `wt=$(git config ... --get core.worktree)`, then `:514` `"~"*` refusal and `:516-520` boundary check.
- Calls to `guard_git_config`: `:581, :613, :628, :650, :665`.
- Gitfile and commondir pointer reads: `:617-618, :635-641, :654-655`. Worktree registration reads: `:565, :586`.

## Findings (by severity)

### F1 · HIGH · fail-open pointer reads on embedded newline (`:635-641`, `:617-618`, `:654-655`, `:565`, `:586`)

The guard reads a pointer file with `IFS= read -r target < file`. That reads only the first line. Git reads the whole file:

- `setup.c:1005-1016` (`read_gitfile_gently`): after trimming only trailing CR/LF, `dir = buf + 8` uses the entire remainder. An interior LF stays in the path.
- `setup.c:335-345` (`get_common_dir_noenv`): commondir is read as whole content, trailing CR/LF trimmed, and the rest is used as a path.

Consequence: for `gitdir: A<LF>B`, the guard validates `A`. Git uses the path `A<LF>B`, which resolves through a directory literally named `A<LF>` and then `..`. A hostile fleet child can create that directory, so the path git follows can leave the root while the guard validated an in-root target. This is the same embedded-newline class the round asks about, and the existing lexical newline refusal (`:351-352`) does not reach it because the newline is dropped before `guard_target` sees the value.

Repair pattern: read the whole file with `IFS= read -r -d '' whole < "$f" || true`, then emulate git exactly: strip trailing CR/LF in a loop, then refuse if any LF, CR, or NUL remains (`protected_fail` or `unresolved-path`). Existing repo pattern for NUL-in-list detection: `tools/cand-merge-quarantine.sh:727-731` (`IFS= read -r -d '' nul_prefix <"$LIST_FILE"`). Its return value is 0 exactly when a NUL is present.

Not verified: the worktree `gitdir` reader at `:565/:586` mirrors the same first-line pattern. I did not read git's worktree reader, so treat it as [INFERENCE] until checked.

### F2 · HIGH · glob over the joined key list causes cross-line and substring matches (`:503-507`)

Bash `case` `*` matches newlines. The pattern therefore runs across record boundaries of the newline-joined list, and it is substring-based. Every match fires on key presence, not value.

Concrete mechanisms (source-reasoned, not run):
- Cross-line: a record `remote.origin.url` followed by a record `alias.promisor` makes `*remote.*.promisor*` match the joined text. A benign config with `[remote "origin"]` and `[alias] promisor = …` is refused as `git-config-unsupported`.
- Cross-line: a record `filter.lfs.required` followed by any `*.clean` record matches `*filter.*.clean*`.
- Substring inside a subsection: `[branch "feature/include.x"]` produces `branch.feature/include.x.*` and matches `*include.*`. `remote.include.url` matches as well.

These are false refusals for benign configs (C1 operability). The pattern list also refuses `core.hookspath`, `extensions.worktreeconfig` and `remote.*.promisor` regardless of value, so `…=false` and `…=` are refused. That is the round-14 "value-blind" harm, and the value-aware repair belongs to the peer seats (HooksNeutral, PromisorSafe, WorktreeCfg, BoolVariants).

No bypass found in the current pattern set for section and variable names. Git lowercases those (`config.c:598`, `:1001`), so ASCII patterns match them reliably. The defect is over-refusal and mis-scoping, not under-refusal.

Repair (C1): match per record on parsed components, not on the joined blob:
- `git config --file "$cfg" --no-includes -z --name-only --list`, read with `while IFS= read -r -d '' rec`.
- Canonical key: section = text before the first `.`; variable = text after the last `.` (variable names cannot contain `.`); subsection = text between.
- Test `section` and `variable` with exact equality (`include`/`includeif`; `filter` + `clean|smudge|process`; `core` + `hookspath|attributesfile|excludesfile|alternaterefscommand`; `remote` + `promisor`; `extensions` + `partialclone|worktreeconfig`). Test subsection only where the rule needs it.

### F3 · MEDIUM · key case and subsection rules the matcher depends on (source-verified)

| Rule | Source |
|---|---|
| Section and variable names are case-insensitive; canonical key output is lowercase for both | `config.c:598` (`do_parse_config_key` `tolower`), `:1001` (`get_base_var` `tolower`), `:1100-1120` (`tolower(c)` for variable) |
| Quoted subsection `[sec "Sub"]`: subsection bytes preserved, case-sensitive | `config.c:950-986` (`get_extended_base_var` appends raw bytes) |
| Deprecated dotted header `[sec.Sub]`: whole header lowercased | `config.c:988-1002` (`get_base_var` applies `tolower` to every header byte) |
| LF is rejected in subsection and headers; `\` is consumed before the next byte | `config.c:955, :967, :973` (`error_incomplete_line`); `:599-603` (`invalid key (newline)`) |
| Valueless entry `name` has `value = NULL` | `config.c:929-934` |
| Valueless entry in `--null` output prints key with no delimiter | `builtin/config.c:460-466` (`TYPE_NONE`) |
| `-z` terminator is NUL; key/value delimiter becomes LF | `builtin/config.c:1024-1027` |
| Man: valueless `name` is boolean true | `git-config(1)` installed man, "a variable defined without =<value> is taken as true" |
| Man: subsection may not contain newline or NUL; `\` escaping of `"` and `\` | `git-config(1)` installed man, "Subsection names are case sensitive and can contain any characters except newline and the null byte" |
| Man: `--get-regexp` matches a canonical key (section and variable lowercased, subsection not) | `git-config(1)` installed man, `--get-regexp` paragraph |

Notes:
- The source excerpt I read (`:950-986`) contains no NUL check, while the man page forbids NUL in subsections. Treat NUL in subsections as [INFERENCE] and fail closed (F5).
- Matching `${keys,,}` lowercases subsections too, which is harmless for section/variable matching.

### F4 · MEDIUM · valueless versus `key=` must not be conflated in any value-aware repair

- Valueless `promisor` (or `worktreeConfig`) means boolean true (`config.c:929-934` gives NULL; man: true).
- `promisor=` gives an empty string, which the boolean parser treats as false [INFERENCE; not read in source].
- A split like `IFS== read -r key value` or `IFS=$'\n' read -r key val` turns a valueless record into `value=""`. That reverses the decision, so `remote.x.promisor` (valueless, true) would be allowed.
- Use `git config --type=bool` for value decisions, which lets git normalize valueless to true and invalid bools to an error. Treat any non-zero exit other than 1 (no match) as fail closed. Or detect the LF delimiter explicitly and treat a key-only record as true.

### F5 · MEDIUM · NUL and newline handling in key lists and values

- `$(...)` drops NUL bytes and trailing LF. A subsection containing NUL would be silently shortened in the guard's view while git's C-string consumers see a different key. Fail closed instead: refuse any config file containing a NUL byte before the key list is built. Cheap check: `n=$(LC_ALL=C tr -cd '\000' < "$cfg" | wc -c)`; refuse if `n != 0`.
- Keys can never contain LF (`config.c:599-603`, `:955`), so newline-delimited `--name-only` output is safe for keys. The defect is the matching (F2), not the output mode. The `-z` form is still preferable because it removes all ambiguity.
- Values can contain LF through the `\n` escape. Any parser that splits on newline across value-bearing output is unsafe. Split `-z` records on NUL, then split the key on its first LF only. Never split on values.

### F6 · LOW · `core.worktree` value trailing LF (`:511`)

`wt=$(git config ... --get core.worktree)` strips trailing LF. For a value `x<LF>` (created by escape), the guard checks `x` while git uses `x<LF>`. Interior LF is already refused (`:351-352`). Fix: read with `-z`, then refuse any LF or CR. The `"~"*` refusal at `:514` is correct, since git expands `~` for `core.worktree`.

### F7 · LOW · `${keys,,}` locale

`${keys,,}` is locale-dependent. Under `tr_TR`, uppercase `I` maps to dotless `ı`. Because git already lowercases section and variable names (F3), the only affected bytes are in subsections, and no pattern literal depends on them. No bypass found. Recommended: drop `,,` and match canonical git output, or run the match under `LC_ALL=C`.

## Acceptance the repaired guard should meet (for ConfigFixture; not run here)

1. Benign: `[remote "origin"] url=…` plus `[alias] promisor = !x` is allowed (cross-line, value-blind false refusal fixed).
2. `remote.origin.promisor` = `false`, `no`, `off`, `0`, and empty: allowed. `true`, `yes`, `on`, `1`, valueless: refused (`promisor-remote-unsupported`). Invalid value such as `maybe`: refused fail-closed.
3. `extensions.partialclone` presence in any form (including empty): refused. `extensions.worktreeconfig=false`: allowed. `=true` or valueless: refused.
4. Case: `[Remote "origin"] PROMISOR=true` refused; `[extensions] PartialClone` refused; dotted `[remote.Origin] promisor=true` refused.
5. Subsection containing `include.`, `core.hookspath`, or `filter.x.clean`: allowed (no false refusal).
6. Gitfile `gitdir: <safe>` followed by LF and a second path: refused (F1). Gitfile with trailing LF only: consistent with git.
7. `core.worktree` value with trailing LF or interior LF: refused (F6).
8. Config file containing NUL: refused (F5).
9. Key-looking value: `core.worktree = x` followed by a `\n`-escaped `remote.origin.promisor` text in the value: not parsed as a key, and no refusal from that text.

## Calibration notes

- Every row above is source-derived. Nothing was executed. Behavioural claims about bash glob semantics and about git output are [INFERENCE] until a fixture runs them.
- F1's exploit path requires a hostile fleet child that can create a directory named with an LF. That is within the threat model (fleet children are untrusted) and is not covered by the r14 path guards.

## Unrun checks for L1 after integration

- Fixture cases for items 1-9 above, each with a stable case ID, run against the baseline tool and the repaired tool. The baseline must fail for the expected reason (F1 gitfile escape; F2 cross-line refusal).
- `grep -n 'IFS= read -r target <' tools/souji-census.sh`: every pointer read should become whole-file and NUL-checked.
- `grep -n ',,' tools/souji-census.sh` on the guard: should be gone or moved under `LC_ALL=C`.

## Messages

Findings sent to `SoujiR15` and to `SoujiR15.ConfigRepair` (executor owning the repair).

## Boundary disclosure (SoujiR15 reminder)

Before the reminder, three calls exceeded the explicit-path boundary. Each returned results from a lane-root or recursive scope, so census/operator-sweep-20261019 names and metadata may have been listed. No contents were opened, copied, or quoted.

- `_glob` on `souji-shokunin/**` (recursive, lane root). Its output listed census/operator-sweep-20261019 filenames.
- `_grep` with path `/home/vgpnk/Projects/shokunin/souji-shokunin` (recursive, lane root), pattern for git config. Results were limited to tools, tests, .ufo, and census/round-15, but the search scope included the sweep directory.
- `_bash` `grep -rn` over `tests tools census/round-14 .ufo/waves/round-14` with `grep -v operator-sweep`. The sweep directory was not in the scope, so this is a scoping note only.

Also before the reminder: `ls -la` of the lane root and `ls` of `census/` (names only, via `_bash` and `_glob`). Nothing from the sweep was read.

No runtime probes, tests, or builds were run. The findings above rely on source reads of tools/souji-census.sh and upstream git source, not on sweep contents. After the reminder, no further recursive or lane-root searches were made.
