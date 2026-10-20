# BoundaryPlan: Comprehensive Credential Traversal Map for souji-census.sh

**Seat**: SoujiR14.BoundaryPlan (scout, leaf)  
**Lane**: `/home/vgpnk/Projects/shokunin/souji-shokunin`  
**Target**: `tools/souji-census.sh` (tag #5156, 827 lines)  
**Assigned Axes**: calibration, operability  
**Report Path**: `.ufo/waves/round-14/w1/BoundaryPlan.md`  

---

## 1. Evidence Classification & Environment Status

- **Code Inspection Evidence**: All findings and line citations are derived exclusively from static analysis and structural code review of `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh` (snapshot #5156).
- **Exercised Evidence**: **None**. Per leaf seat constraints and the R14 contract, no live census was run, no test fixtures or selftests were executed, no shell probes were issued, and no real credential stores or operator-sweep directories (`~/.omp/agent/`, `census/operator-sweep-*`) were touched or accessed.
- **Tool Installs / Updates**: **None**. No packages, binaries, or tool upgrades were installed or modified for this analysis.
- **Ground Truth / Inferences**: Behavioral assertions regarding Git, coreutils (`readlink`, `du`, `find`), and Bash built-ins are grounded in source code inspection and standard POSIX/GNU semantics; unexercised behavioral deductions are explicitly flagged as `[INFERENCE]`.

---

## 2. Executive Summary & C2 Verdict

The current implementation of `tools/souji-census.sh` possesses **zero credential-boundary guards**. There is no lexical, canonical, or ancestor check against sensitive credential stores (`$HOME/.omp/agent`, `$HOME/.ssh`, `$HOME/.aws`, `$HOME/.gnupg`, `$HOME/.config`, etc.) at any input entry point. 

As currently written, `souji-census.sh` will:
1. Accept `--root` or `SHOKUNIN_ROOT` pointing directly to, within, or above a credential store, enumerating its contents.
2. Accept `--compare` pointing to sensitive files (such as private keys or API tokens), reading their contents via shell redirection `< "$file"` before header validation.
3. Follow symlink repository roots and symlinked `.git` directories directly into credential stores via directory globbing and `test -d`.
4. Traverse linked worktree registrations pointing into credential stores, executing `git status` inside them.
5. Recursively walk repositories with `find` without pruning `.scratch` or protected paths, statting every file.
6. Permit environmental injection via unscrubbed `GIT_*` variables (`GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_CONFIG*`).

To satisfy C2 operability, `tools/souji-census.sh` must refuse all paths overlapping credential-store boundaries (lexical and canonical, including ancestors and aliases) before any `git`, `find`, `du`, `stat`, or file content access, exiting fail-closed with exit code `2` and a stable protected-path finding.

---

## 3. Comprehensive Traversal Map & Hole Inventory

### Dimension A: Input & Environment Paths (`SHOKUNIN_ROOT`, `--root`, `GIT_*`, `TMPDIR`)

| Entry Point | Line Numbers | Traversal Mechanism | Vulnerability / Concrete Hole |
|---|---|---|---|
| `SHOKUNIN_ROOT` | L83 | Environment read | Default root assignment `ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"` accepts unvalidated environment variable. If set to `$HOME` or a credential directory, census defaults to scanning it. |
| `--root <DIR>` | L801-804 | CLI parsing | Accepts raw directory strings directly without lexical validation or boundary check. |
| `--include-root` | L320-322, L800 | Root census flag | When enabled, checks `[ -d "$root" ] && [ -e "$root/.git" ]` and adds `$root` directly to census rows. If `--root` is `$HOME` with a dotfiles `.git`, `$HOME` is processed as a repository. |
| `GIT_*` env unset | L71 | Incomplete sanitization | Line 71 unsets only `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE`. It fails to unset `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_CONFIG*`, or `GIT_CEILING_DIRECTORIES`. A poisoned `GIT_COMMON_DIR` redirects refs, configs, and object queries to credential trees. |
| `TMPDIR` | L418, L516 | Temp file creation | `emit_compare` (L418) and `run_selftest` (L516) use `${TMPDIR:-/tmp}` without verifying `TMPDIR` is outside protected boundaries, creating files under potentially sensitive paths. |

### Dimension B: Root Directory Processing (`emit_census`, `canon_path`)

| Operation | Line Numbers | Traversal Mechanism | Vulnerability / Concrete Hole |
|---|---|---|---|
| `canon_path "$ROOT"` | L345 via L95 | Canonicalization | `canon_path` uses `readlink -m -- "$1" 2>/dev/null \|\| printf '%s' "$1"`. It fails open on error (returning the untrusted input string). Furthermore, canonicalization is called **before** any lexical boundary check. |
| `[ -d "$root" ]` | L346 | Filesystem stat | Performs direct `stat` check on `$root` before checking whether `$root` overlaps a credential store or ancestor directory. Exits `1` on non-directory instead of exit `2` protected-path refusal. |
| Direct Credential Root | L345-352 | Directory traversal | Passing `--root ~/.ssh` or synthetic `$HOME/.ssh` passes `[ -d ]` and triggers child repository scanning within the credential store. |
| Ancestor Root | L345-352 | Directory traversal | Passing `--root $HOME` or `--root /` treats the ancestor directory as the fleet root, scanning all immediate subdirectories (including `.ssh`, `.aws`, `.gnupg` if dot-dirs match, or non-dot directories containing keys). |
| Symlink Root Alias | L345-352 | Link resolution | A symlink root (e.g. `/var/tmp/link -> ~/.ssh`) is resolved by `canon_path` without boundary refusal, allowing aliases to reach enumeration. |

### Dimension C: Compare File Access (`--compare`, `load_census`, `emit_compare`)

| Operation | Line Numbers | Traversal Mechanism | Vulnerability / Concrete Hole |
|---|---|---|---|
| `--compare <PREV>` | L805-808, L821 | Flag evaluation | Accepts any file path. Line 821 checks `[ -n "$COMPARE" ]`. If `--compare ""` or `--compare=` is passed, it silently bypasses compare mode and prints a normal census with exit 0 (`F1` in BoundaryReviewCompare). |
| `load_census "$COMPARE"` | L416, L362-386 | File access | Invoked directly in `emit_compare` before any root census execution. |
| `[ -f "$file" ]` | L365 | Symlink following stat | Uses raw uncanonicalized `$file`. `[ -f ]` follows symlinks, dereferencing symlink aliases to credential files. |
| Direct Content Read | L367, L385 | File descriptor open | `done < "$file"` directly opens the target file for reading. `IFS= read -r line` reads file contents into memory. If passed `--compare ~/.ssh/id_rsa`, private key bytes are read into the shell before line 371 rejects the header. |
| Missing Baseline Checks | L363-386 | Input validation | No check for file readability (`[ -r ]`), non-regular files (FIFOs, `/dev/stdin`), hardlinks (`stat -c %h`), or operator-sweep directories (`census/operator-sweep-*`). An unreadable file fails unhandled under `set -e` with exit 1 rather than clean exit 2. |
| Root Coupling | L418-420 | Combined execution | `emit_compare` creates a temporary file and runs `emit_census > "$tmp"` (L419). If `--compare` is valid but `--root` points to credentials, credentials are still scanned. |

### Dimension D: Repository Discovery & Symlinks (`list_repos`)

| Operation | Line Numbers | Traversal Mechanism | Vulnerability / Concrete Hole |
|---|---|---|---|
| Directory Glob | L324 | Shell glob `"$root"/*/` | Matches directory symlinks! If `$root` contains `symlink -> /home/user/.ssh`, glob expansion includes it. |
| Directory Check | L325 | `[ -d "$d" ]` | `-d` dereferences symlinks. Directory symlinks evaluate to true. The script never tests `[ -L "${d%/}" ]`. |
| Dot-Dir Heuristic | L327-330 | `case "$base" in .* )` | Only filters out direct children whose basename starts with `.`. Does not filter non-dot directories or symlinks that point to credential stores (e.g. `keys/`, `credentials/`, `alias_to_ssh/`). |
| `.git` Symlink Acceptance | L333 | `[ -d "${d%/}/.git" ]` | `-d` follows symlinks. If a directory has `.git -> ~/.ssh` (or any credential directory), it evaluates to true. The script fails to require `[ ! -L "${d%/}/.git" ]`. |
| Gitfile Follow | L320, L246-248 | `[ -e "$repo/.git" ]` | Uses `-e` which accepts gitfiles. Git follows the `gitdir:` pointer to arbitrary locations on disk without boundary restriction. |

### Dimension E: Repository Census & Worktree Traversal (`census_one`, `worktree_extra_flags`)

| Operation | Line Numbers | Traversal Mechanism | Vulnerability / Concrete Hole |
|---|---|---|---|
| Repo Canonicalization | L245 | `canon_path "$1"` | Resolves child paths without checking whether the resolved path falls within or overlaps a credential boundary. |
| `rev-parse` Invocation | L253 | Git execution | `git -C "$repo" rev-parse --is-inside-work-tree` runs inside `$repo`. If `$repo` is a credential store or contains malicious `.git/config` / `commondir` / `alternates`, Git reads objects and configuration from that tree. |
| `worktree list` Parsing | L235, L221 | Metadata extraction | Reads `.git/worktrees/*/gitdir` via `git -C "$repo" worktree list --porcelain`. Worktree paths are repo-controlled strings that can reference arbitrary locations (e.g. `/home/user/.ssh`). |
| Unguarded Worktree `git status` | L227, L231 | Directory stat & Git execution | Line 227 tests `[ ! -d "$path" ]` (which follows symlinks), then line 231 executes `d=$(count_dirty "$path")`, running `git -C "$path" status --porcelain`. If `$path` is in a credential store, Git enumerates files inside it. |
| Upward Discovery Hazard | L231 -> L131 | Git upward traversal | If a registered worktree directory `$path` does not contain its own `.git`, `git -C "$path"` discovers upward into the parent tree (e.g. `$HOME/.git`), status-checking the user's home directory. |
| Tracked Secret Hashing | L131-132 | Working tree content read | `count_dirty` runs `git status --porcelain` with pathspec exclusions only for `.ufo/state` and `.ufo/watchdog.log`. If tracked secret-shaped files (e.g. `.env`, `*.pem`) have racy/drifted stat metadata, Git opens and hashes their contents (`F1` in BoundaryReviewScratch). |
| Alternates & Commondir | L119, L123, L253 | Git internals | `.git/objects/info/alternates` and `.git/commondir` cause Git to recursively query alternate object directories and shared repositories, which may point into credential stores. |

### Dimension F: `.scratch` & Tree Walk Traversal (`scratch_bytes`, `newest_mtime`)

| Operation | Line Numbers | Traversal Mechanism | Vulnerability / Concrete Hole |
|---|---|---|---|
| Symlink Check Order | L142-143 | `test -e` before `-L` | Line 142 tests `[ ! -e "$d" ] && [ ! -L "$d" ]`. In POSIX/bash, `-e` follows symlinks. If `$d` is a broken symlink or symlink to a restricted target, `-e` attempts to stat the target before line 143's `[ -L "$d" ]` executes. |
| `du` on Protected Paths | L147 | File size enumeration | If a repo is located within or aliased to a credential store, `du -sb -P -- "$d"` enumerates byte counts of sensitive directories. |
| Recursive `find` Traversal | L165-167 | File hierarchy walk | `cd -- "$repo" && find . -type f -printf '%T@ %P\0'` traverses the entire directory tree. It prunes `.git`, `.ufo/state`, `.ufo/watchdog.log`, but does **not** prune `.scratch` or credential directories if `$repo` contains them. |
| Inadequate Secret Filter | L170-178 | Regex heuristic | The awk `secret_comp()` function only inspects filenames after `find` has already stat'd them. Furthermore, it only checks `.env*`, `credential`, `secret`, `id_`, `*.pem`. It fails to detect `config`, `known_hosts`, `authorized_keys`, `token`, `*.key`, `auth.json`, `.netrc`, `.npmrc`, `.pypirc`, `.docker/config.json`, `.kube/config`, `.aws/credentials`. |

---

## 4. Remediation Architecture & Invariants for CensusBoundary

To close all mapped holes, `SoujiR14.CensusBoundary` must implement defensive ordering adhering to these strict invariants:

1. **Environmental Sanitization**:
   - Wipe all exported `GIT_*` variables at script startup:
     ```bash
     while IFS= read -r _v; do unset "$_v"; done < <(compgen -e | grep '^GIT_' || true)
     export GIT_OPTIONAL_LOCKS=0 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
     ```
2. **Strict Guard Ordering**:
   - **Phase 1: Lexical Normalization & Verification (No Filesystem Access)**:
     - Check raw input strings (`--root`, `--compare`).
     - Reject empty `--compare ""` or `--compare=` immediately with exit `2`.
     - Reject paths containing `..` or leading slashes overlapping known sensitive roots.
   - **Phase 2: Canonical Resolution & Boundary Check (Fail-Closed)**:
     - Canonicalize via `readlink -f` (or strict `readlink -m` verifying non-empty return).
     - Verify the canonical path does not equal, reside inside, or act as an ancestor of any protected credential boundary.
     - Protected boundaries must include: synthetic `$HOME` (in tests) / real `$HOME/.omp/agent`, `$HOME/.ssh`, `$HOME/.aws`, `$HOME/.gnupg`, `$HOME/.config/gcloud`, `$HOME/.azure`, `$HOME/.kube`, `$HOME/.docker`, `$HOME/.netrc`, `$HOME/.password-store`, `/etc/shadow`, etc.
     - Ancestor refusal: If `--root` is `$HOME` or `/`, refuse immediately before enumeration.
   - **Phase 3: Filesystem Access**:
     - Only after Phase 1 and Phase 2 pass: execute `[ -d ]`, `[ -f ]`, globbing, or file opens.
3. **Compare Path Isolation**:
   - Before `load_census` opens `< "$file"`, enforce:
     - Canonical boundary verification.
     - Regular file check (`[ -f "$file" ] && [ ! -L "$file" ]`).
     - Refuse FIFOs, pipes, `/dev/stdin`, unreadable files (`[ -r "$file" ]`), hardlinks (`stat -c %h` == 1), and secret-shaped file basenames.
     - Refuse `census/operator-sweep-*` paths.
4. **Repository Enumeration & Symlink Skipping**:
   - In `list_repos`:
     - Test `[ -L "${d%/}" ]` and skip immediately (never follow repo-root symlinks).
     - Test `[ -L "${d%/}/.git" ]` and skip/refuse (never follow `.git` symlinks).
     - For `--include-root`: verify `$root` is not a symlink and `$root/.git` is a non-symlink directory (`[ -d ] && [ ! -L ]`).
5. **Worktree Registration Verification**:
   - In `worktree_extra_flags`:
     - Canonicalize each worktree `path`.
     - Check canonical path against credential boundary.
     - Require `$path/.git` to exist as a regular file pointing back to the admin `gitdir`.
     - If path overlaps credentials, is a symlink, or lacks `.git`, skip and report refusal/error without running `git status`.
6. **Scratch & Tree-Walk Hardening**:
   - Test `[ -L "$d" ]` first before `[ -e "$d" ]` in `scratch_bytes`.
   - In `newest_mtime`, prune `.scratch` if present or ensure credential boundaries are never entered.
7. **Exit Contract & Output Purity**:
   - Protected path finding on stderr: `souji-census: protected path refused: kind=<root|ancestor|alias|compare|worktree>`.
   - Exit status must be `2` (fail-closed / usage error).
   - Zero output on stdout on boundary refusal.

---

## 5. Peer Notification Log

Per assignment target ("Message CensusBoundary with concrete holes and cite lines"):
- **Recipient**: `SoujiR14.CensusBoundary` (`agent://SoujiR14.CensusBoundary`)
- **Status**: Delivered via `write agent://SoujiR14.CensusBoundary`.
- **Payload**: Comprehensive summary of 6 hole categories citing L71, L83, L95, L131, L142-143, L165-178, L216-240, L245-253, L324-335, L345-346, L365-385, L416, and L801-808, stating the C2 exit 2 contract.

---

## 6. Final L1 Commands (Post-Wave Verification)

The following commands are identified for the L1 integrator to run once all sibling seats land. **No checks or commands were executed by this seat.**

```bash
# 1. Syntax & static validation
bash -n /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh

# 2. Static guard presence check (verify guards precede FS calls)
grep -nE 'protected|HOME|readlink|compgen' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh

# 3. Native selftest verification (under /var/tmp)
TMPDIR=/var/tmp bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh --selftest

# 4. R14 Census Boundary isolation suite with command spies (synthetic HOME under /var/tmp only)
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py \
  --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh

# 5. Targeted regression checks (isolated in /var/tmp)
# a. Empty compare must exit 2 (not exit 0)
TMPDIR=/var/tmp bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh --root /var/tmp/safe --compare ""
# b. Symlink root to synthetic credential directory must exit 2 with 0 git/find spy hits
# c. Worktree registration to synthetic credential directory must exit 2 / error without git status
```

---

## 7. Residual Risks & Uncertainties

1. **Hardlink Aliases**: Hardlinks to credential files share inode numbers and cannot be detected lexically or via `readlink`. Comparing link count (`stat -c %h != 1`) on the compare path mitigates this for files.
2. **Bind-Mount Aliases**: Mount namespaces and bind-mount aliases cannot be resolved by user-space path normalization. Host-level isolation or device/inode boundary checks are the theoretical boundary.
3. **Line Drift**: Line numbers cited herein reflect snapshot `#5156`. When `CensusBoundary` edits `tools/souji-census.sh`, line numbers will shift; citations should be indexed by function names and symbol anchors.
