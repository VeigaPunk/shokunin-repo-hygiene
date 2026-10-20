# SafetyCredential — C2 credential-store access review (round 14, w1)

Seat: `SoujiR14.SafetyCredential` (sentinel). Scope: C2 only — guard ordering, aliases, synthetic tests.
Axes: calibration (claims match evidence) and operability (the guard refuses before any access, stable exit 2).
Certification is OFF. This report does not claim recertification.

## Surface state at first review (superseded — see "Landed C2 review" below)

- `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` is **unmodified** from HEAD `a31642d` (`git status --short -- tools tests` lists only `tools/souji-evidence-cache.py` as new).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py` **does not exist yet**.
- So this review covers the baseline holes and the requirements the C2 guard must meet. I did not review the guard implementation itself. It had not landed when I read the files. L1 must re-check findings F1–F8 against the landed diff.
- I sent all findings to `SoujiR14.CensusBoundary` by peer message.

## Findings

Severity is the impact if the guard lands without the remediation.

| ID | Sev | Exploit path | Evidence (line refs = HEAD census) | Impact | Smallest remediation |
|---|---|---|---|---|---|
| F1 `tmpdir-into-store` | HIGH | `TMPDIR=<store> souji-census --compare X` or `--selftest` | L418 `mktemp "${TMPDIR:-/tmp}/souji-census-now.XXXXXX"`, L516 `mktemp -d "${TMPDIR:-/tmp}/…"` | The census **writes** a TSV, or a whole fixture fleet with `git init`, inside the credential store. A root/compare guard alone misses this. | Pin to `/var/tmp`, or run TMPDIR through the same protected predicate and exit 2. Also add the `emit_compare` tmp to an EXIT trap: `exit 1` at L346 inside `emit_census > "$tmp"` leaks it today. |
| F2 `home-poisoning` | HIGH | Guard derives the protected set from `$HOME/.omp/agent` only → run with `HOME=/var/tmp/x --root ~real/.omp` | Spec requires synthetic HOME fixtures, so the guard will read `$HOME` | A poisoned or synthetic HOME turns off protection of the real store | Protect the **union** of `$HOME/.omp/agent` and `$(getent passwd "$(id -u)" \| cut -d: -f6)/.omp/agent`, in both lexical and canonical forms. Any env override may only **add** paths. Under `set -u`, an unset HOME must give a protected/could-not-evaluate exit 2, not an unbound-variable exit 1. |
| F3 `canon-before-lexical` | HIGH | `--root <store>/x` → `canon_path` (L95 `readlink -m`) runs before any refusal | Exercised: strace of `/usr/bin/readlink -m` issues `readlink()` on every component, **including entries inside the (synthetic) store**. `/usr/bin/realpath -m -s` issues zero filesystem syscalls. | Metadata queries on the store happen before refusal, which breaks the "guard before access" ordering | 1) Make the path absolute and normalise it lexically with `realpath -m -s --`. 2) Refuse if the lexical path overlaps. 3) Only then run `readlink -m` and refuse if the canonical path overlaps. Compare on component boundaries in both directions: `x==P`, `x` an ancestor of `P` (including `/`), `P` an ancestor of `x`. Lexical `a/link/..` collapse can differ from the physical path, so both steps are required. |
| F4 `child-alias` | HIGH | A safe `--root` holds child `evil -> <store>/repo` | L324 glob `"$root"/*/` and L333 `[ -d …/.git ]` follow symlinks; L245 canonicalises into the store; then git/find/du run there. Exercised on synthetic `/var/tmp`: the glob returned `fleet/evil/` with `dotgit-dir:yes`. | Checking the root alone is bypassed; `git status`/`find` run inside the store | Skip symlink children (`[ -L "${d%/}" ]`), symlink `.git`, and `.git` gitfiles. Apply the predicate to every child, to `--include-root`, and to the absolute `git rev-parse --path-format=absolute --git-dir --git-common-dir` before any status/find/du. |
| F5 `worktree-alias` | HIGH | Repo `.git/worktrees/w/gitdir` → `<store>/repo/.git` | L219-235 `worktree_extra_flags` reads `worktree list --porcelain`, then `[ -d "$path" ]` and `count_dirty "$path"` = `git status` **inside the store** (hashes file contents). Exercised: porcelain listed `worktree …/store/repo`. | Credential file contents are hashed or read through a registered worktree | Run the protected predicate on each worktree `path` before `-d` or status. A protected hit gives a stable finding/exit 2, never a silent skip. |
| F6 `git-env-redirect` | MED | `GIT_COMMON_DIR=<store>/repo/.git souji-census …` | L71 unsets only `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE`. Exercised: with `GIT_COMMON_DIR` set, `rev-parse --git-common-dir` resolved into the synthetic store. | Refs/config/objects are read from the store. `GIT_CONFIG_PARAMETERS`/`GIT_CONFIG_COUNT` can also set `core.fsmonitor`, which runs a command on `git status`. | `unset $(git rev-parse --local-env-vars)` (the git 2.55 list includes GIT_COMMON_DIR, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT), plus `-c core.fsmonitor=false` on status. Alternates (`objects/info/alternates`) into the store: the remediation is to check the canonical `--git-common-dir` and refuse; full alternates parsing is out of scope. |
| F7 `compare-alias` | MED | `--compare /var/tmp/x.tsv -> <store>/file`, `/proc/self/fd/N`, `/dev/stdin` | L365 `[ -f "$file" ]` follows symlinks, then L367-385 reads the file. A header mismatch prints no content, but the file is still opened. | Credential file opened and read | Run the same lexical→canonical predicate on `--compare` before `[ -f ]`. Refuse `/proc/*/fd/*`, `/dev/fd/*`, `/dev/stdin`, since their canonical form may be `pipe:[…]` or a deleted target. **Residual (not fixable without stat'ing the store):** hardlinks or bind mounts that alias store inodes. State this explicitly; do not claim coverage. |
| F8 `fixture-oracle-gaps` | MED | PATH command spies only | Bash builtins (`[ -d ]`, `[ -f ]`, `read < file`, globbing) never hit PATH. `BASH_ENV` and exported `BASH_FUNC_git%%` shadow the spies. | Spies can report "no access" while builtins stat/read the store, so the evidence is mis-calibrated | Run the tool under `env -i HOME=<synthetic> PATH=<spy>:/usr/bin LC_ALL=C TMPDIR=/var/tmp`. Add an OS-level oracle: `/usr/bin/strace -f -e trace=%file,openat,readlink -o LOG` and assert that no syscall path is lexically under the synthetic store (strace 7.0 is present). The synthetic HOME must be a `/var/tmp` mktemp with cleanup; the fixture must never contain a literal `/home/*/.omp`. |

### Lower and residual

- L1 `inherent-alias-readlink`: detecting an alias canonically needs `readlink()` on the alias target, which is metadata inside the store, without open/read. Accept this and document it. Do not escalate it to `readlink -e`/`stat`.
- L2 `scope-of-store`: the boundary covers `~/.omp/agent` only. `~/.ssh`, `~/.gnupg` etc. are protected only by the dot-child skip (L328-330) and the secret-shaped name heuristic (L170-183, name metadata, no content). Treat this as a scope statement, not a defect.
- L3: `.scratch` handling is already symlink-safe for `du` (L143 `-L` check, `du -P`) and for `find` (no `-L`). The remaining scratch risk only comes in through F4: a repo root that is itself an alias.

## Landed C2 review (static only, after CensusBoundary landing message)

I inspected the code of `git diff a31642d -- tools/souji-census.sh` (+690/−59) and `tests/fixtures/r14-census-boundary.py` (584 lines, cases R14C2-01..09). Nothing was executed. All N-findings below are **code inspection**; bash/git behaviour claims are `[INFERENCE]` from documented semantics.

### Status of F1–F8 against the landed tool

| ID | Status | Basis |
|---|---|---|
| F1 | Fixed | `mktemp /var/tmp/…` for both compare and selftest; `cleanup_census_tmp` EXIT trap. |
| F2 | Fixed | `build_protected_roots`: HOME ∪ `getent passwd` home, plus `PI_CONFIG_DIR`/`PI_CODING_AGENT_DIR` additions; `${HOME:-}` safe under `set -u`. |
| F3 | Fixed for inputs | `resolve_guarded` checks each component with `protected_reason_inside` **before** `[ -L ]`/`readlink`; user `..` refused; `readlink -m` removed. |
| F4 | Partially fixed | Children are checked lexically and symlink children skipped, but see N4 (glob stat runs before the skip). No fixture case. |
| F5 | Partially fixed | `guard_worktree_registrations` checks the gitdir target and pointer under errexit; worktree admin `commondir` is not checked there (N1). No fixture case. |
| F6 | Fixed | Every `GIT_*` var unset via `compgen -v GIT_`; global/system config `/dev/null`; `-c core.fsmonitor=false -c core.hooksPath=/dev/null` on status. N3 is a remaining default-path gap. |
| F7 | Fixed | `guard_path compare` before `[ -f ]`; `/proc/*`, `/dev/fd/*`, `/dev/std*` refused after resolution; `nlink > 1` refused (`hardlinked-compare`). No `/proc/self/fd` fixture case. |
| F8 | Partially fixed | `subprocess.run(env=…)` replaces the whole env (no BASH_ENV/exported functions); strace oracle present. But strace is filtered to `execve,open,openat,getdents64`, so stat/lstat/statx/readlink/access are not observed and "guard before stat" is not proven. |

### New findings on the landed code

| ID | Sev | Exploit path | Evidence | Impact | Smallest remediation |
|---|---|---|---|---|---|
| N1 `errexit-swallowed-guard` | HIGH | `--include-root` on a root whose `.git` is a gitfile → safe gitdir whose `commondir` points into the store; or a fleet repo whose `.git/worktrees/w/commondir` points into the store | `emit_census` calls `if row=$(census_one "$repo")`. Bash clears `-e` in command substitutions when `inherit_errexit` is off (no match for `inherit_errexit` in the file), and ignores `-e` in `if` conditions. Inside `census_one`, `guard_git_surface` captures `dir=$(guard_target git-common-dir …)`: the inner `protected_fail` prints `path-protected` and exits its subshell, but `census_one` keeps going with `dir=""`, then runs `git rev-parse`/`git status`, which follow `commondir` into the store. In `list_repos`, the include-root gitfile branch runs only `guard_git_pointer` (target, not commondir), and `guard_worktree_registrations` never checks worktree `commondir`. | Store objects/config/refs read by git; refusal message printed but the exit is 0 with a row emitted. The fixture's R14C2-06 `commondir` case should fail on the landed tool `[INFERENCE]`. | Add `\|\| exit 2` to every guard capture (`guard_git_surface`, `guard_git_links resolved=`, `worktree_extra_flags cpath=`, `census_one repo=`/`wt_extra=`), or propagate a sentinel. In `list_repos`, run the full `guard_git_surface` for an include-root gitfile, and check `worktrees/*/commondir` in `guard_worktree_registrations`. |
| N2 `nested-alternates` | MED | Repo `objects/info/alternates` → safe `/var/tmp/a/objects`, whose own `info/alternates` → store | `guard_alternates` checks a single level; git follows alternates recursively | Store object files opened by `git status` | Recurse up to git's depth limit (5) with the same guard. |
| N3 `git-xdg-defaults` | MED | `HOME=<store>` or `XDG_CONFIG_HOME=<store>` with a safe `--root` | `GIT_CONFIG_GLOBAL=/dev/null` does not cover the default `$XDG_CONFIG_HOME/git/ignore` (fallback `$HOME/.config/git/ignore`), which `git status` reads when `core.excludesFile` is unset; `git/attributes` similarly `[INFERENCE]`. HOME/XDG values are not guarded. | Open attempt inside the store by git | Pass `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` to git calls, or refuse when HOME/XDG_CONFIG_HOME overlaps a protected root. |
| N4 `glob-stat-before-skip` | LOW-MED | Safe fleet containing child `evil -> <store>` | `list_repos` iterates `"$root"/*/`. With a trailing slash, bash's glob tests directories with `stat` (follows links) before the `[ -L "$d" ]` skip runs `[INFERENCE: bash glob_testdir]` | One `stat()` of the store target. Metadata only, no content. | Iterate `"$root"/*`, then check `[ -L ]` before `[ -d ]`. |
| N5 `relocated-store` | MED | `~/.omp` is a symlink to `/x/y`, so the canonical store is `/x/y/agent`; run with `--root /x/y/agent` | The `.omp/agent` component pair does not match `/x/y/agent`. Only HOME is canonicalised, not `<home>/.omp`. | Census runs inside the real store via its canonical path. Conditional on host layout; I did not check `~/.omp`. | Also resolve `<home>/.omp` (the parent, outside the store) and add `<canonical>/agent`. If `<home>/.omp/agent` is itself a link, document it as residual. |
| N6 `unsupported-config-aborts-census` | LOW (operability) | Any fleet repo with local `core.hooksPath`, `include.*`, or `filter.*` | `guard_git_config` → `protected_fail` → exit 2 for the **whole** census, not just a row. `core.hooksPath` is refused even though status already forces `-c core.hooksPath=/dev/null`. | A normal fleet census can fail; to-verify on the real fleet, not checked by me | Drop the `core.hooksPath` refusal (already neutralised). Consider a per-row `unsupported` flag for non-protected config refusals. |

### Fixture coverage gaps (code inspection)

- Not covered: safe-fleet child symlink → store (F4/N4); worktree registration and worktree `commondir` into the store (F5/N1); compare via `/proc/self/fd` (F7); nested alternates (N2); HOME/XDG poisoning (N3). `HOME/agent-alias` is created in `build_world` but no case uses it.
- The strace filter should add `stat,lstat,newfstatat,statx,readlink,readlinkat,access,faccessat2`. Until it does, the fixture's evidence supports "no open/getdents below the store", not "no access".
- Positive cases (07–09) check exit, row shape and store-free output. They do not compare against baseline output byte-for-byte, so the claim "legacy output preserved" depends on the `--tool` baseline run.

## Final-bytes re-review (static only)

Pinned bytes I inspected, matching CensusBoundary's message: `tools/souji-census.sh` 1515 lines, sha256 `034a518e423d206e7de94cc62e2df2695bd6be33a497a5d4919bdebae47317a3`; `tests/fixtures/r14-census-boundary.py` 679 lines, sha256 `a118225bce416fe8ac7f5ccd5e5a6745d37ade02cc9f9aeda6429e36c788825f`. Hashing these lane files was the only command I ran. Everything below is code inspection.

| ID | Status | Basis (final line refs) |
|---|---|---|
| N1 | Closed | Every guard capture ends in `\|\| exit 2`: L403, L412, L435, L447, L522, L530, L553, L586, L601, L623, L638, L790, L822, L848, L951, L983, L1062. `protected_fail` called directly inside `census_one`'s subshell exits it with 2, and `emit_census` turns rc 2 into exit 2. Include-root gitfile now runs the full `guard_git_surface` (L907). Worktree admin `commondir` is guarded before git (L558-571). |
| N2 | Closed | `guard_alternates_file` recurses with depth > 5 refused (L416-437). |
| N3 | Closed for status | `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` on status (L687-688). `[INFERENCE]` Other git calls (rev-parse, worktree list, for-each-ref, rev-list) do not read ignore/attributes files. |
| N4 | Closed | Glob is `"$root"/*` (L915). `[ -L ]` is tested before `[ -d ]` (L928-929). |
| N5 | Closed (conservative) | `<home>/.omp` resolved as a parent and `<canonical>/agent` added (L253-263). If `~/.omp` resolves to a path ending in `/agent`, the whole resolved dir is protected, which over-refuses rather than under-refuses. A symlinked `~/.omp/agent` itself remains a documented residual. |
| N6 | Open, LOW | `core.hooksPath` is still in the refused local-config list (header L86) even though status forces `core.hooksPath=/dev/null`. Operability only: one such fleet repo aborts the whole census with exit 2. to-verify on the real fleet. |

Residual notes:
- R1 (LOW, scope): `build_protected_roots` runs `resolve_guarded "$HOME/.omp"` on every invocation, so on the host it lstats/readlinks the real `~/.omp` (the parent, **not** `~/.omp/agent`). That is within the round contract, which forbids only `~/.omp/agent/`, but it is a real-home metadata access on every run and should be stated in the CensusBoundary report.
- R2 (LOW, calibration): `trace_access` skips every `readlink(` line, including any readlink whose *path argument* is under the store. The store root is mode 000, so a readlink below it yields EACCES and is still caught by the EACCES rule. A readlink of the store directory itself (EINVAL) would not be counted. Narrow the skip to lines whose first argument is outside `AGENT`.
- R3 (LOW, coverage): still no fixture case for a safe-fleet child symlink to the store (N4), a `--compare /proc/self/fd/N`, or HOME/XDG_CONFIG_HOME poisoning (N3). `HOME/agent-alias` (L282) is still created but unused. Cases 10 (worktree owner) and 11 (alternates) now cover F5/N1 and N2. `trace=%file,getdents64,execve` plus the mode-000 store and the positive EACCES probe now cover the stat family, so the fixture's "no access" claim is supported for the traced syscall classes.

I see no remaining HIGH or MED credential-access finding in the final bytes. This is a static review. The L1 runs below are the exercised evidence.

## Superseding pin re-review (static only)

This pin supersedes the pair above: `tools/souji-census.sh` 1533 lines, sha256 `e2a1d50276f74a44a8216383e411617c4b81336fb42f522df22fb57c2548f05a`; `tests/fixtures/r14-census-boundary.py` 726 lines, sha256 `fda498d0c2a19767401222de2ceb0c862ec9f12b096bb5e7067d99783c7ead17`. Hashing these files was the only command I ran. Everything below is code inspection.

- N6: kept as a conservative refusal and documented by the executor. I accept it as an operability trade-off, not a credential defect.
- R1: documented by the executor. Code confirms `build_protected_roots` (L213-270, called at L668 before argument parsing) issues lstat/readlink on HOME/passwd-home components and `<home>/.omp` only. `<home>/.omp/agent` is checked textually and never resolved (L244 skip; walker refuses at the `.omp/agent` component). Wording note: "startup root refusal before any lstat" is accurate for the **`--root`/`--compare` input path** (L1521-1522, through the component walker). It is not accurate for the process as a whole, because the home seed lstats `<home>` and `<home>/.omp` first.
- R2: closed. `trace_access` (fixture L422-444) takes the readlink path argument and flags it when it equals or is below `AGENT`. Alias targets outside the store stay allowed.
- R3: closed with one caveat.
  - R14C2-12 adds the fleet child symlink case.
  - `case_05` adds `/proc/self/fd/999`, refused by the tool's `special-path` finding (L1003-1004, `path-protected`, exit 2).
  - `case_09` adds `HOME=<synthetic AGENT>` as a positive run with the strace oracle.
  - Caveat (LOW): fd 999 is almost certainly not open in the tool process, so the case proves `/proc` prefix refusal, not refusal of a live fd that aliases the store. An open-fd variant would need the fixture to pass an fd. That would open the synthetic store file in the fixture, which is acceptable for a synthetic `/var/tmp` store if L1 wants it.
- `HOME/agent-alias` is still created (L282) and unused (cosmetic).

Verdict: no HIGH or MED credential-access finding remains in the final pin. The remaining items are LOW (N6 trade-off, R1 wording precision, the R3 fd caveat). This is a static review, and the L1 runs are the exercised evidence.

## Process deviation (flagged per L1, SoujiR14)

The round context prohibited builds, tests and smoke runs mid-flight. The strace probes and the probes against a forged synthetic store listed below were verification runs, so they deviated from that rule even though each one ran in its own throwaway `/var/tmp` tree. The observed results are kept below as they were. L1 will not rerun them only to confirm them. After the deviation was flagged, I ran no further probes. The real `~/.omp/agent` was never opened, queried or touched, and no census, selftest or fixture was run.

## Code inspection vs exercised evidence

**Code inspection only:** F1, F2 (not yet implemented), F7, F8 (builtin/BASH_ENV behaviour reasoned from bash semantics), L1–L3. I ran no census and no selftest.

**Exercised by me, synthetic `/var/tmp` mktemp trees only, removed via trap / `rm -rf`. Real `~/.omp/agent` never touched:**
- `strace` of `/usr/bin/realpath -m -s`: no filesystem syscalls. `/usr/bin/readlink -m`: `readlink()` on each component, including inside the synthetic store (F3).
- Bash glob `*/` plus `[ -d link/.git ]` follows a symlinked child into the synthetic store (F4).
- `GIT_COMMON_DIR` redirects `rev-parse --git-common-dir` into the synthetic store (F6).
- A forged `.git/worktrees/w/gitdir` makes `worktree list --porcelain` emit a store path (F5).
- Host facts: git 2.55.0; `git rev-parse --local-env-vars` list as above; GNU coreutils 9.11 `/usr/bin/{realpath,readlink}`; strace 7.0; bubblewrap 0.12.0; `inotifywait` absent.

**Tool installs:** none. strace and bwrap were already present, and inotify-tools is not needed if the strace oracle is used.

## Final L1 commands (after C2 lands; synthetic only)

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin
bash -n tools/souji-census.sh
env -i HOME=/var/tmp PATH=/usr/bin LC_ALL=C TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
env -i HOME=/var/tmp PATH=/usr/bin LC_ALL=C TMPDIR=/var/tmp python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
# baseline-red check (fixture must fail for the protected-path reason, not crash):
git show a31642d:tools/souji-census.sh > /var/tmp/census-baseline.sh && \
  env -i HOME=/var/tmp PATH=/usr/bin LC_ALL=C TMPDIR=/var/tmp python3 tests/fixtures/r14-census-boundary.py --tool /var/tmp/census-baseline.sh; \
  rm -f /var/tmp/census-baseline.sh
```

Acceptance checks L1 should require in the fixture output: cases for direct, descendant, ancestor (including `/` and synthetic HOME), root symlink, child symlink (F4), worktree gitdir alias (F5), `GIT_COMMON_DIR` env (F6), compare symlink plus `/proc/self/fd` (F7), poisoned TMPDIR (F1), and HOME≠passwd-home union (F2, with synthetic passwd-home simulated via override-add only). Each case needs exit 2 with a stable id, plus an empty strace store-path hit list. There must also be one safe positive row with unchanged legacy census output.
