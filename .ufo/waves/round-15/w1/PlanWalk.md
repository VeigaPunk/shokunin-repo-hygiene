# PlanWalk — config guard and Git-invocation map, value-aware design (r15 w1)

Seat: `SoujiR15.PlanWalk` (scout, leaf). Axes: **operability** (C1), **calibration** (C2).
Owned write: this report only. No edits, no tests, builds, linters, fixtures, or probes.
Pin inspected: `tools/souji-census.sh` 1539 lines, sha256
`fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` (the r14 closure's
"changed tool" digest). No r15 repair bytes were present in the lane when this seat read it.

## 0. Boundary disclosure and method

Observed facts below come from reading these explicit files only:
`tools/souji-census.sh`, `tools/` listings, `corpus/lessons/round-14-verifier-spotcheck.md`,
`.ufo/waves/round-14/w1/{SafetyCredential,BoundaryReviewRoot,NoHarm}.md`,
`.ufo/waves/round-15/w1/{LessonDraft,ScorecardDraft}.md`, `census/round-15/claims.json`,
`.ufo/waves/round-15/w1-spec.json`, `w1-dispatch.json`, `tests/fixtures/r14-census-boundary.py`,
and installed Git 2.55.0 man pages (`git-config(1)`, `git(1)`, `gitattributes(5)`, `githooks(5)`).

Boundary deviations to disclose (no repeat, no writes):
- One whole-lane recursive search ran before the parent's no-recursive-search instruction:
  `grep -rn "git-config-unsupported\|guard_git_config" --include=*.sh --include=*.py .`.
  It returned no match outside `tools/souji-census.sh` (pipeline filtered that file out, output
  empty). Directory traversal therefore visited the lane tree, but only `*.sh`/`*.py` contents
  could be opened; no `census/operator-sweep-*` content was read or printed.
- One recursive search into `.ufo/waves/round-14/` for `hooksPath|value-blind|config-unsupported`
  (round-14 evidence, not the operator sweep). One `ls -la` of the lane root and one of `tools/`.
- Commands run: `ls`, `wc -l`, `sha256sum`, `sed`/`grep` on the files above, `zcat`/`grep` on
  installed man pages, `man -w`, `git --version`. No census/fixture/selftest/gate execution, no
  fleet probe, no `~/.omp` or credential access, no pacman. Tool installs/updates: **none**.

Confidence labels: **OBSERVED** = read in source/doc bytes; **INFERENCE** = derived from Git
implementation semantics or the source shape, not executed.

## 1. Current guard map (OBSERVED)

Environment sanitation S0, before any Git process:
- `set -euo pipefail` L111; `unset -f git find du stat awk grep sort head cut date readlink` L112.
- All inherited `GIT_*` unset via `compgen -v GIT_` L114-120.
- `GIT_OPTIONAL_LOCKS=0`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0` L121-126.

Boundary primitives:
- `protected_fail` L160-164 prints `path-protected` on stderr and `exit 2`.
- `resolve_guarded` L337 resolves one component at a time, refuses `..` for inputs, refuses a
  protected component before `[ -L ]`, caps symlink hops at 40.
- `guard_path` L413 (input, final predicate) and `guard_target` L422 (internal target, `..`
  allowed, final predicate applied).

Git-surface guard chain:
- `guard_git_links` L456 (every symlink in the gitdir must resolve inside it).
- `guard_git_files` L475 checks `config HEAD index packed-refs commondir info/exclude
  objects/info/alternates` for regular-file/single-link (L477).
- `guard_git_config` L493-525 — **the config guard**.
- `gitfile_admin` L527, `guard_git_pointer` L546, `guard_worktree_registrations` L555.
- `guard_git_surface` L603 for `.git` dir L613, commondir L628, gitfile L650, gitfile+commondir
  L665; calls `guard_git_config` at L581 (registered worktree admin), L613, L628, L650, L665.

Current config predicate (value-blind, OBSERVED L500-506):

```sh
keys=$(git config --file "$cfg" --no-includes --name-only --list)
keys=${keys,,}
case "$keys" in
  *include.*|*includeif.*|*filter.*.clean*|*filter.*.smudge*|*filter.*.process*|\
  *core.hookspath*|*core.attributesfile*|*core.excludesfile*|\
  *core.alternaterefscommand*|*remote.*.promisor*|*extensions.partialclone*|\
  *extensions.worktreeconfig*)
    protected_fail "git-config-unsupported" "$dir" "$cfg" ;;
esac
```

It reads only key names, lowercases the entire newline-joined list, substring-matches, and exits
the **whole census** (discovery failure, before the header: `emit_census` L973, `list_repos` L979,
header L991). `core.worktree` is read separately L511 with `--get`, `~` values are refused L513-515,
relative values are resolved against the gitdir L516-520, and the result is boundary-checked
L521 (`guard_target core-worktree`). `config.worktree` is never read.

Over-match (OBSERVED pattern, INFERENCE on real keys): `*include.*` also matches
`credential.include.helper`; `*filter.*.clean*` matches `filter.<d>.cleanup`;
`*extensions.worktreeconfig*` matches `extensions.worktreeConfigX`. Subsection case is lowered,
so `filter.LFS.clean` and `filter.lfs.clean` are indistinguishable.

## 2. Every Git invocation, before/after sanitation (OBSERVED)

Legend: S0 = env sanitation; S1 = structural/boundary guard; S2 = config guard; S3 = per-command
`-c` neutralizers. "Config reaches git" lists what the **process** will consult, not what the
script intended.

| # | Line | Command | Sanitation in effect | Config surfaces the process reads | Exec-capable config reachable |
|---|------|---------|----------------------|-----------------------------------|-------------------------------|
| 1 | 500 | `git config --file "$cfg" --no-includes --name-only --list` | S0 | only `$cfg`, includes disabled | none (classifier itself) |
| 2 | 511 | `git config --file "$cfg" --no-includes --get core.worktree` | S0 | only `$cfg` | none |
| 3 | 688 | `git -C repo worktree list` | S0+S1+S2 (guard L847 precedes) | repo config + includes + `config.worktree` if extension | none for this subcommand [INFERENCE] |
| 4 | 694 | `git -C repo for-each-ref ... refs/remotes` | S0+S1+S2 | same | none |
| 5 | 698 | `git -C repo rev-list --count --branches` | S0+S1+S2 | same + promisor remotes (lazy fetch) | lazy fetch (network/local) |
| 6 | 702 | `git -C repo rev-list --count --branches --not --remotes` | S0+S1+S2 | same + promisor | lazy fetch |
| 7 | 710-713 | `git -C repo --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null status --porcelain ...` | S0+S1+S2+S3 | repo config + includes + `config.worktree`; clean/process filters; index/HEAD/refs files | **clean/process filter commands**, lazy fetch |
| 8 | 836 | `git -C repo worktree list --porcelain` | S0+S1+S2 (census_one L847 precedes) | repo config + includes + `config.worktree` | none [INFERENCE] |
| 9 | 859 | `git -C repo rev-parse --is-inside-work-tree` | S0+S1+S2 | repo config + includes; honors `core.worktree`/`core.bare` | none |
| 10 | 1157 | selftest `git -C fixture add -A` | **S0 only**; fixture-local config unguarded | fixture repo config + includes + filters + hooks (index write) | **filter clean/process; `post-index-change` hook** |
| 11 | 1158,1160,1163 | selftest `write-tree`, `commit-tree` | S0 only | fixture config | none meaningful |
| 12 | 1170,1171 | selftest `git init`, `symbolic-ref` | S0 only | fixture/global-off | none |
| 13 | 1203-1271 | selftest `update-ref`, `symbolic-ref` | S0 only | fixture config | none |
| 14 | 1530 | `command -v git` | S0 | none | none |

Findings from the map:
- All **row** Git processes run after S1+S2 for the repo being measured. The classifier's own
  calls (#1, #2) are file-scoped (`--file`, `--no-includes`) and read no repo/global config.
- `worktree_extra_flags` runs `guard_git_surface "$cpath"` L831 immediately before
  `count_dirty "$cpath"` L832; the main repo was already guarded by `census_one` L847.
- **Gap G1 (OBSERVED):** for a linked worktree, `guard_git_config` is called on the worktree admin
  dir (`.../worktrees/<id>/config`), which does not exist. The shared config is the main repo's
  (already checked), but `$GIT_DIR/config.worktree` is never classified anywhere. Today this is
  masked only because `extensions.worktreeConfig` is refused wholesale.
- **Gap G2 (OBSERVED):** fixture builders (#10-#13) run under S0 only. If a new r15 fixture writes
  a filter or `core.hooksPath` into a repo **before** `st_commit`, the builder itself executes the
  fixture's clean filter / `post-index-change` hook. Hostile-config fixtures must be written after
  the last builder command, or the builders need the same `-c` neutralizers.
- **Gap G3 (OBSERVED):** `guard_git_files` L477 does not cover `info/sparse-checkout`,
  `info/attributes`, `sharedindex.*`, or `worktrees/*/config.worktree`. A FIFO at one of these can
  hang `status`/`worktree list` before any boundary finding (same class as r14 F-D).

## 3. Effect map: what each refused key can actually do in **this** command set

Installed Git 2.55.0 primary docs. "Consumer" = the census subcommands above.

| Key (structured) | Git-documented effect | Consumer that honors it | Verdict |
|---|---|---|---|
| `core.hooksPath` | path Git looks in for hooks; `/dev/null` disables all hooks (git-config(1)) | only hook-running subcommands; **none used**. `status` is not a hook command; `post-index-change` fires only when the index is written (githooks(5)), and `GIT_OPTIONAL_LOCKS=0`/`--no-optional-locks` prevent optional index writes | inert for #3-#9; `-c /dev/null` on #7 is belt-and-braces |
| `core.attributesFile` | pathname of the attributes file in addition to in-tree `.gitattributes` and `$GIT_DIR/info/attributes` | `status` only; #7 forces `/dev/null`. Other subcommands do not read attributes [INFERENCE] | inert |
| `core.excludesFile` | pathname of ignore file in addition to `.gitignore` and `info/exclude` | `status` only; #7 forces `/dev/null` | inert |
| `core.fsmonitor` | boolean built-in monitor, or legacy hook pathname (git-config(1) §core.fsmonitor) | `status` only; #7 forces `false` | inert |
| `core.alternateRefsCommand` | "When advertising tips of available history from an alternate, use the shell to execute the specified command" (git-config(1)) | advertise/`rev-list --alternate-refs`; **neither used** (`--branches`, `--not --remotes`) | inert |
| `core.worktree` | worktree root; absolute or relative to gitdir | #7, #9 read it | path: must stay boundary-checked |
| `include.path`, `includeIf.*.path` | "contents of the included file are inserted immediately"; relative to the including file; tilde-expanded (git-config(1) Includes) | every command | redirect: read-capable, must be boundary-checked before read |
| `extensions.worktreeConfig` | loads `$GIT_DIR/config.worktree` in addition to `$GIT_COMMON_DIR/config`; those settings override (git-config(1)) | every command | inert by itself, but adds an unclassified config file → **obligation O1** |
| `extensions.partialClone` | value is the name of the promisor remote | object reads (#5,#6,#7) may lazily fetch missing objects | must be neutralized → **O2** |
| `remote.<name>.promisor` | "When set to true, this remote will be used to fetch promisor objects" (git-config(1)) | same | neutralized value-aware: `false` or no URL is inert; `true`+URL needs O2 |
| `filter.<d>.clean` | command converting worktree content on the check-in path (gitattributes(5)) | `status` content comparison (check-in codepath) [INFERENCE] | **execution-capable** when non-empty |
| `filter.<d>.process` | long-running protocol replacing clean/smudge (gitattributes(5)) | same | **execution-capable** when non-empty |
| `filter.<d>.smudge` | command on checkout only (gitattributes(5)) | no checkout subcommand exists | inert |
| `filter.<d>.required` | failure propagation flag only | only if a conversion runs | inert as a command |

Not refused today and not exec-capable here: `core.autocrlf`/`eol`, `core.fileMode`,
`core.symlinks`, `core.ignoreCase`, `core.untrackedCache`, `core.sparseCheckout*`,
`core.bare`, `core.repositoryFormatVersion`, `extensions.objectFormat|refStorage`,
`alias.*`, `submodule.*` (`--ignore-submodules=all`), `diff.*` (`--porcelain` builds no patch),
`credential.*`/`core.askPass`/`core.sshCommand`/`url.*` (no auth/fetch path once O2 holds),
`sequence.*`, `gc.*`/`maintenance.*` (no reachable auto-gc in these subcommands [INFERENCE]).

## 4. Value-aware design (complete; no namespace regression)

### 4.1 Classifier contract

`classify_local_config <gitdir> <config-file>` returns, never prints values:
- `0` accepted;
- `20` policy-unsupported with a stable reason code (`filter-clean`, `config-unparsed`,
  `config-path-unparsed`, `config-nonregular`, `include-depth`, `include-cycle`);
- `path-protected` (exit 2) for any resolved path that reaches the protected namespace — same
  finding and exit as today.

Parsing replaces L500-506: `git config --file "$cfg" --no-includes -z --list` (documented
`-z`: NUL-terminated values, newline between key and value; git-config(1)). Split each record at
the first newline; empty value = boolean true. Split the key structurally at the first and last
dot: section, subsection, variable; lowercase section+variable only. Match exact
`(section,variable)` pairs, never substrings. Values stay in shell memory; reasons and paths only
in diagnostics (a repo-local config may contain credentials; never echo values).

### 4.2 Per-key decision

| Key | Decision | Implementation |
|---|---|---|
| `core.hooksPath` | **accept any value** | none. Keep `-c core.hooksPath=/dev/null` on #7 and `GIT_OPTIONAL_LOCKS=0`. No hook-running subcommand exists; document this as the reason in the header |
| `core.attributesFile` | **accept any value** | #7 already forces `/dev/null`; no other consumer. Never stat/read the value |
| `core.excludesFile` | **accept any value** | same |
| `core.fsmonitor` | **accept any value** | #7 forces `false`; keep |
| `core.alternateRefsCommand` | **accept any value** | add a comment tying it to `--alternate-refs`/advertise; re-check if the command set grows |
| `core.worktree` | **boundary-check, accept benign** | resolve with `git config --file … --type=path` (expands `~`/`~user`, git-config(1)); relative to gitdir; `guard_target core-worktree` before any row Git; protected ⇒ exit 2; unparseable ⇒ reason `config-path-unparsed` |
| `include.path` / `includeIf.*.path` | **boundary-check + recursive classify** | for each value: `--type=path`, relative to the including file's dir; `guard_target config-include` **before reading**; require regular file (`-f`, no FIFO/device/symlink outside; `guard_target` already resolves link targets and protected roots); recurse with a visited set and depth cap 10; classify the included records with the same table. A risky value anywhere ⇒ that reason (the include may override it later; accepting only when every included value is safe is conservative) |
| `includeIf` condition | never evaluated | if the included file is all-safe, accept regardless of condition; if it carries a policy-risky value, return that policy reason for the row. This over-approximates (a false condition would not have read the file). Do not try to reimplement gitdir/onbranch/hasconfig wildmatch — an under-match would accept a truly active risky include |
| `extensions.worktreeConfig` | **accept**, then classify the new file | O1: classify `$GIT_DIR/config.worktree` (main worktree) and `$GIT_COMMON_DIR/worktrees/<id>/config.worktree` for every registered worktree, with the same table and the same `core.worktree` boundary check; add `config.worktree` to the regular-file guard L477; guard symlinks inside those admin dirs (already covered by L581's `guard_git_links`) |
| `extensions.partialClone` | **accept** | O2: export `GIT_NO_LAZY_FETCH=1` in S0 — "Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand" (git(1)). Missing objects then make #5/#6/#7 fail, which already degrade (`0`, `unverifiable`). Set a `partial-clone` row flag when the named remote has a non-empty `remote.<name>.url`, so a degraded count is not read as measured |
| `remote.<name>.promisor` | **accept both values** | boolean-normalize with `--type=bool`; O2 supplies the safety. `true` with no URL is inert (no transport); `true`+URL gets the row flag |
| `filter.<d>.clean` | empty ⇒ accept; **non-empty ⇒ policy `filter-clean`** | O3: do **not** execute. Skip `count_dirty` for the main worktree and per-worktree statuses; emit `dirty=0` plus existing `status-unverifiable` plus `config-unsupported`. `wt`, `unpushed`, `scratch`, mtime still measured (their commands do not convert content) |
| `filter.<d>.process` | same as clean | same |
| `filter.<d>.smudge` | **accept any value** | no checkout subcommand exists |
| `filter.<d>.required` | **accept** | not a command |

Rejected alternative for filters: neutralizing with `-c filter.<d>.clean=` / `.process=` on #7
would preserve the row but silently changes the dirty count for filtered repos (every
filter-tracked file may compare unequal without its clean filter). That trades an honest
`status-unverifiable` for a false number; do not call it preservation.

### 4.3 Abort vs degrade (mixed fleet)

- **Namespace** (`path-protected` from `core.worktree`, any include target, any
  `config.worktree` target, gitdir/commondir/alternates/worktree paths): unchanged — whole-run
  `exit 2` before the affected Git process. This retains every r14 namespace gain.
- **Policy** (r15 reasons): row-scoped. Split the surface guard so `list_repos` runs only the
  namespace checks (it executes no Git), and `census_one` runs `classify_local_config` before any
  row Git. A policy repo becomes a row with `config-unsupported` (and `status-unverifiable` when
  only the status path was skipped); peers keep byte-identical rows; exit 0. Do not let a policy
  refusal remove a repo from `REPOS`, and do not let it call `exit 2`.
- If a whole-row degrade is required (unparseable/too-deep include), zero only the Git-derived
  fields; `scratch_bytes`/newest-mtime are filesystem-only and stay measured. Never present a
  zero as measured without the flag.
- Stable flag order list (L~902) and `has_problem` mapping gain `config-unsupported` and
  `partial-clone`; header/usage (L84-91, L25-58) state both.

### 4.4 Command-set invariants the acceptance must keep

1. #7 keeps exactly `--no-optional-locks`, `-c core.fsmonitor=false`,
   `-c core.hooksPath=/dev/null`, `-c core.excludesFile=/dev/null`,
   `-c core.attributesFile=/dev/null`. Add a source-audit selftest check (next to L1482-1487)
   asserting these strings and `GIT_NO_LAZY_FETCH=1` are present — a static assertion, not a
   behavioral probe.
2. No new Git subcommand may be added without re-running the effect table: `--alternate-refs`,
   any checkout/smudge path, any index-writing command re-opens hooks/filters.
3. S0 stays: unset every `GIT_*` first; only then set the four sanitized values plus
   `GIT_NO_LAZY_FETCH=1`. (`GIT_CONFIG_PARAMETERS`/`GIT_CONFIG_COUNT` are covered by the `GIT_*`
   unset; `-c` cannot be used to suppress includes, so include traversal is the only option.)

## 5. Namespace-regression argument (why each acceptance is safe)

- `hooksPath`/`attributesFile`/`excludesFile`/`fsmonitor`: the value is either never read
  (no consumer) or overridden on the only consumer (#7). No path resolution of the value occurs.
- `alternateRefsCommand`: no consumer executes it.
- `core.worktree`: resolved by `--type=path`, then `guard_target` refuses protected roots before
  `status`/`rev-parse` runs. Unchanged from today except `~` expansion (benign gain).
- `include`: every target resolved with `guard_target` before its first read; nested targets are
  discovered by reading each already-guarded file with `--no-includes`; protected target ⇒ exit 2
  before read. `[INFERENCE]` This is the same ordering guarantee as the r14 input path.
- `worktreeConfig`: `config.worktree` lives inside an already-resolved gitdir; the regular-file
  guard and the classifier run before any row Git. Without O1 this acceptance would be a real
  regression (a `core.worktree` or include hidden in `config.worktree` would be unguarded).
- `partialClone`/`promisor`: `GIT_NO_LAZY_FETCH=1` removes the only consumer behavior; without O2
  this acceptance would allow network egress and object writes from a repo-controlled URL.
- `filter.clean|process`: no non-empty command is ever accepted into a run, so no execution; the
  affected status call is skipped, not neutralized.
- `filter.smudge|required`: no checkout path exists.

## 6. Acceptance requirements for L1 (and for the C2 checker's inputs)

C1 paired evidence (baseline `fcff8b05…` vs changed bytes, same fixture digest):
1. **Benign-config preservation (red→green):** repo with `core.hooksPath=.githooks`,
   `core.attributesFile=.gitattributes.local`, `core.excludesFile=.gitignore.local`,
   `extensions.worktreeConfig=true` with a benign `config.worktree`, `remote.origin.promisor=false`,
   a benign `include.path` to `extra.cfg` containing only `user.name`, and
   `filter.lfs.required=false` (no command). Baseline: exit 2, no rows. Changed: exit 0, row
   present, every numeric field byte-equal to a config-free twin repo in the same fleet.
   This is the exact r14-closure contradiction (spotcheck `:148`, `:160`) in one case.
2. **Mixed fleet:** benign-config repo + plain repo + execution-capable-config repo + plain repo.
   Changed: exit 0; plain rows byte-identical to a config-free fleet run; benign row fully
   measured; risky row present with `config-unsupported` (+`status-unverifiable` when only status
   was skipped).
3. **No-execution control:** risky repo's `filter.<d>.clean` writes a sentinel file; after the
   run the sentinel must be absent. Same for a hooksPath pointing at a hook that writes a sentinel
   (baseline builder must not run it either — see G2).
4. **Namespace controls (must stay red and must abort):** `core.worktree` → synthetic protected
   store; `include.path` → store; `config.worktree` containing `core.worktree` → store; each:
   exit 2, `path-protected`, and no `open/openat/getdents64/newfstatat` below the store (fixture
   trace). Also one negative control where the same keys point at a benign path and pass.
5. **Partial-clone control:** `extensions.partialClone=origin` + `remote.origin.promisor=true` +
   `remote.origin.url=file:///nonexistent`; changed run must not fetch (no new objects/packs, no
   network), row present, `partial-clone` flag; baseline red only if the baseline actually
   refuses (do not claim an observed fetch).

Checker (C2) admission rules the evidence format must support:
- bind both tool digests and the fixture digest; per-case `baseline_observed` and
  `changed_observed`; per-case `red_cause`. Reject green-only (baseline already green), exit-only
  evidence, flag-hidden degradation scored as preservation, numeric field mismatch in rule 1,
  missing namespace control, and any "benign" fixture whose config includes an execution-capable
  value (mislabel). Checker red/green fixture cases: valid pair, green-only, exit-only,
  missing-namespace, mislabeled-benign.
- No certification or deletion authority in any verdict.

## 7. Residuals and unrun checks

- `includeIf` conditions are not evaluated; a risky value under a false condition still degrades
  that row. Documented over-refusal, not a safety gap. [INFERENCE]
- Git's include depth limit is not stated in the installed man page; cap 10 is implementation
  knowledge. Any cap that is too high is still cycle-safe via the visited set. [INFERENCE]
- `status` invoking clean/process filters is not documented as status behavior; it is the
  check-in conversion path used for worktree/index comparison. Treated conservatively. [INFERENCE]
- TOCTOU: the repo-local config can change between classification and the row Git processes.
  Same class as the documented guard-vs-access race; do not claim atomicity.
- `guard_git_files` additions (`info/sparse-checkout`, `info/attributes`, `sharedindex.*`,
  `worktrees/*/config.worktree`) close the FIFO-hang class (G3) but are adjacent hardening, not
  required for the C1 key-policy claim.
- Fixture-builder sanitation (G2) is required for any new config fixture; otherwise a hostile
  fixture executes during construction and invalidates controls.
- Unrun by this seat: census `--selftest`, `tests/fixtures/r14-census-boundary.py`,
  `r15-preservation-evidence.py`, ShellCheck, sources-census validation, any paired fleet run.
  L1 must run them after the repair lands; this report is source inspection only.

## 8. Tools

No installs or updates.
