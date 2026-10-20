# BoolVariants — round 15 w1 critic (source-only)

Axes: operability (benign false/variant configs must not be refused) and
calibration (a repo git treats as true/invalid must never yield a clean row).

**Status: DESIGN-ONLY.** No repair has landed. `tools/souji-census.sh` is
unchanged from r14 (`git diff --stat -- tools/ tests/` is empty). The only
promisor/worktreeConfig logic is still the value-blind refusal at
`souji-census.sh:503-507`. The findings below attack the repair contract that
ConfigRepair is implementing ("preserve … false promisor/worktreeConfig where
safe"). Nothing was executed: no tests, no probes, no git runs against fixtures.

## Ground truth: git v2.55.0 (installed `git version 2.55.0`)

Sources were fetched read-only from
`https://raw.githubusercontent.com/git/git/v2.55.0/<file>`. The doc is the installed
`git-config.1.gz` (sha256 `f75fbd7d…1a89`).

| Rule | Source |
|---|---|
| A valueless key (`[extensions] worktreeConfig` with no `=`) has value NULL and is **true**. An empty value (`key =`) is **false**. | `parse.c:166-171`; doc roff :1332-1335, :1341-1345 |
| `true/yes/on` and `false/no/off` match with `strcasecmp`, so case does not matter. | `parse.c:172-180` |
| Any other text goes through `git_parse_int`, and any nonzero int is true. That covers `2`, `-1`, `+1`, `0x1`, `010`, `1k`. These are false: `0`, `-0`, `0x0`, `00`, `0k`. The doc lists only `1`, so a whitelist built from the doc is fail-open. | `parse.c:183-191`, `:18-52` (`strtoimax(…,0)` plus k/m/g factor), `:5-16` |
| Unquoted leading and trailing whitespace is stripped, including CR. `;` and `#` start comments. Quotes keep the whitespace inside them: `" 1"` is **true** because strtoimax skips leading space; `"1 "` and `" true"` **die**. | `config.c:835-905` |
| An invalid value **dies** with "bad boolean config value". Examples: `maybe`, `y`, `t`, `enable`, `99999999999` (ERANGE). | `config.c:1292-1298` |
| For `remote.<n>.promisor`, every occurrence is parsed, and a true occurrence creates the promisor. A later `false` **never removes it**, so the rule is OR across occurrences, not last-wins. | `promisor-remote.c:132-145` |
| `[remote] promisor = true` (no subsection) is accepted. `parse_config_key` returns subsection NULL, and the result is a promisor remote named `""`. | `config.c:3557-3591`; `promisor-remote.c:129,138` |
| `extensions.partialClone` is **a string (a remote name), not a bool**. `false`, `0`, `no` and `""` all activate a promisor remote with that name. A valueless key is `config_error_nonbool`, which makes the repository unusable. | `setup.c:624-628`; `promisor-remote.c:178-188`; doc roff :5287-5293 |
| `extensions.worktreeConfig` is a bool and last-wins: each occurrence overwrites the previous one, and each passes through `git_config_bool`, which dies on an invalid value. It is honored in v0 repositories. | `setup.c:629-631` |
| Extensions are read from `$GIT_COMMON_DIR/config` **without includes**. | `setup.c:770-773`, `:859-869` (`git_config_from_file`, no include wrapper) |
| When worktreeConfig is true, `$GIT_DIR/config.worktree` is read with includes. That is `.git/config.worktree` for the main worktree and `worktrees/<id>/config.worktree` for a linked one. Its `core.worktree` and `core.bare` also redirect setup. | `config.c:1563-1598`; `setup.c:587-602`, `:787-795` |
| For a linked worktree, `$GIT_DIR/config` is **not read**; only commondir/config is. | `config.c:1563-1567` |
| `git config --type=bool --get` formats **every** matching value non-gently (it dies on any invalid one) and prints the last. `--get-regexp` prints all. rc 1 means not found. | `builtin/config.c:285-301`, `:503-537`, `:630-636` |

## Counterexamples against the planned repair

Severity order. "FO" means fail-open (a calibration or safety harm). "FR" means
false refusal (an operability harm).

1. **FO: invalid or die values swallowed into "false".** The existing pattern at
   `souji-census.sh:511` is `git config … --get … 2>/dev/null || true`. If it is copied to
   promisor or worktreeConfig, `promisor = maybe` (rc 128, empty output) is read as
   "not true" and the repo is admitted.
   - With worktreeConfig invalid, every git command in the repo dies. `count_unpushed` (`:698,:702 || printf '0'`) and `count_worktrees` (`:688 || true`) then emit a **clean 0 row**. Only dirty falls back to `unverifiable` (`:716-718`).
   - r14 refused any presence, so this would be a regression.
   - **Correction:** treat any rc outside {0,1} as `git-config-unparsed` or unsupported. Never `|| true`.
2. **FO: promisor last-wins.** `promisor = true` followed by `promisor = false` under the same remote.
   - `git config --get` prints `false`, but git treats the remote as a promisor.
   - **Correction:** use `--get-regexp` (all values), and refuse if any line ends in ` true`.
3. **FO: subsectionless `[remote] promisor = true`.**
   - The regex `^remote\..*\.promisor$` (the pattern in `souji-repo-structure.sh:216`) misses it.
   - The r14 glob `*remote.*.promisor*` also misses it unless another remote key precedes it.
   - **Correction:** use the regex `^remote\.(.*\.)?promisor$`.
4. **FO: bash-side raw value parsing.** If the repair reads `--list` or raw `--get` and compares strings in bash:
   - A valueless key prints with no `=` or as an empty string. That is indistinguishable from `key =` (false), but git reads it as true.
   - `TRUE`, `Yes`, `On`, `2`, `0x1`, `1k` and quoted `" 1"` are all true in git.
   - **Correction:** never parse bool text in bash. Delegate to `git config --file "$cfg" --no-includes --type=bool …`. Accept only the exact outputs `true`/`false`. rc 1 means absent, and any other rc refuses.
5. **FO: partialClone treated as a bool.**
   - `extensions.partialClone = false` (or `0`, `no`, or empty) is an active partial clone whose promisor remote has that name.
   - **Correction:** keep partialClone value-blind. Refuse on any presence: rc 0 from `--get`, or the key appearing in `--name-only`. A valueless partialClone also refuses, because the repo is unusable.
6. **FO: worktreeConfig true admitted without inspecting `config.worktree`.**
   - The guard reads only `$dir/config --no-includes` (`:500,:511`). A true value lets `config.worktree` inject `core.worktree` (a setup redirect), `include.*`, `filter.*` or `core.hooksPath`, none of which the guard sees.
   - If "true" is supported, every `$GIT_DIR/config.worktree` must pass the full guard: main `.git/` plus each `worktrees/<id>/`, with includes refused or boundary-checked. Otherwise true must keep refusing.
   - The decision has to be made from the **common** config and then applied to each admin dir. `guard_git_config "$admin"` (`:581,:650`) reads `$admin/config`, which git ignores for linked worktrees, so checking each gitdir separately misses the linked `config.worktree`.
7. **FO (interaction with IncludesSafe/ConfigRepair).** If the repair admits safe includes, a `remote.*.promisor=true` inside an included file **is** honored, because repo config respects includes. A `--no-includes` promisor check then misses it.
   - The promisor check must cover reachable include targets (and `config.worktree`) after their boundary check.
   - worktreeConfig and partialClone in includes are **not** honored (`setup.c:863`), so checking them there only over-refuses, which is safe.
8. **FR (r14 baseline harm the fixture should pin).** The r14 `case "$keys"` glob runs on the newline-joined key list (`:503-505`), so `*` crosses lines.
   - A non-promisor remote named `promisor` with two keys matches `*remote.*.promisor*`: `remote.promisor.url\nremote.promisor.fetch` gives `remote.` … `.promisor`. The same applies to `*include.*` with any remote or branch named `include` (for example `remote.include.url`).
   - **Correction:** match each key exactly per line, or ask git with `--get-regexp`.
9. **FR, minor.** r14 refuses keys in `$admin/config` of a linked worktree, which git never reads (`config.c:1563-1567`). This is harmless after the repair if decisions come from the common config.
10. **Defense in depth (not a substitute for the guard).**
    - Census sets no `GIT_NO_LAZY_FETCH` (grep `:114-123`).
    - A misclassified promisor repo lets `status` lazily fetch: network plus promisor-pack writes, as observed in round-13 AttackCoverage CE1.
    - Exporting `GIT_NO_LAZY_FETCH=1` next to `:121` is a one-line belt.

## Acceptance needed (fixture rows for ConfigFixture / L1)

Each case: expected exit and row status, plus a no-forbidden-access trace, as in
the existing r14 fixture pattern.

- **Admit (must not refuse; r14 red, repaired green):**
  - worktreeConfig set to each of: `false`, `FALSE`, `no`, `Off`, `0`, `0x0`, `-0`, `0k`, quoted `""`, empty (`key =`), and `false ; comment`.
  - promisor set to the same values.
  - A non-promisor remote named `promisor` (two keys), when the repo is otherwise benign.
- **Refuse, unsupported (rc 2, no row, no status run):**
  - promisor set to `true`, `TRUE`, `yes`, `On`, `1`, `2`, `-1`, `0x1`, `1k`, quoted `" 1"`, or valueless.
  - promisor `true` then `false` (same remote).
  - `[remote] promisor = true`.
  - `[remote "a b.c"] promisor = yes`.
  - partialClone set to `origin`, `false`, `0`, or empty.
  - worktreeConfig `true` or valueless, **unless** `config.worktree` support lands. In that case add a `config.worktree` case for each of `core.worktree`→protected, `include.path`, `filter.x.clean` and `hooksPath`, for both the main and a linked worktree.
- **Refuse, unparsed (never a clean row):**
  - promisor or worktreeConfig set to `maybe`, `y`, `t`, `99999999999`, quoted `"1 "`, or quoted `" true"`.
  - A valueless partialClone.
- **Mixed fleet:** one variant repo of each class plus one benign repo. The benign row must be byte-identical to the control.

Unrun checks for L1: the full matrix above against r14 (expect the admit rows
red) and against the repair (all green); `shellcheck -S warning
tools/souji-census.sh`; `bash tools/souji-census.sh --selftest`;
`python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh`
(12/12 must hold).

Tooling: no installs or updates. Scratch copies of the git sources were placed in
`/tmp/boolv-*` and removed.

## Boundary disclosure (calls made before the SoujiR15 no-query reminder; not repeated)

- **Recursive grep over the whole lane root.** I ran `grep pattern='(?i)promisor|worktreeConfig'` with
  `path=/home/vgpnk/Projects/shokunin/souji-shokunin`. This search may have traversed
  `census/operator-sweep-20261019/`. The rendered output listed no operator-sweep file. No operator file
  was opened, edited, moved, copied or deleted. A wildcard read `grep … tests/fixtures/*.py tests/fixtures/*.sh` was
  also run, limited to fixtures.
- **Shell commands that read the host or the repo state.** I ran:
  - `git --version`;
  - `git log --oneline -5` and `git diff --stat -- tools/ tests/` in the lane;
  - `ls` on `tools/`, `tests/fixtures/` and `.ufo/waves/round-15/`;
  - `zcat`/`sha256sum` on the installed `git-config.1.gz`;
  - `curl` of the git v2.55.0 sources to `/tmp`, since removed.

  None of these executed the census tool, a fixture, or git against any repository content.
- **Limitation.** The "repair not landed" status rests on that `git diff --stat` call. The installed-version
  claim rests on `git --version`. Every finding above is otherwise derived from source text.
