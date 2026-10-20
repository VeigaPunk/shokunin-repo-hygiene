# Scoped Source Report: S006 `GIT_OPTIONAL_LOCKS=0` & Size Census Writer Boundaries

**Author**: SoujiR13.SourceLocks (Scout)  
**Round / Wave**: Souji Round 13 / Wave 1  
**Target Path**: `.ufo/waves/round-13/w1/SourceLocks.md`  
**Absolute Path**: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/SourceLocks.md`  
**Host Environment**: Arch Linux x86_64 (Linux 7.2.3-arch1-3), Git 2.55.0 (`git version 2.55.0`, package `git 2.55.0-1`)  
**Role & Posture**: UFO-FSD scout under `/skill:godspeed` (Axes: Calibration, Operability, Coverage). Leaf seat — own only report; no delegation; no commits.

---

## 1. Axes & Executive Summary

1. **Calibration**: Ground S006 against primary canonical web documentation (`https://git-scm.com/docs/git` and `https://git-scm.com/docs/git-status`, accessed 2026-10-20) and installed host roff manuals (`/usr/share/man/man1/git.1.gz` and `/usr/share/man/man1/git-status.1.gz`). Record exact versions, roff line numbers, and verbatim quotes strictly $\le 25$ words.
2. **Operability**: Define the exact execution scope of `GIT_OPTIONAL_LOCKS=0` (and its CLI flag equivalent `--no-optional-locks`). Refuse the overstatement that `GIT_OPTIONAL_LOCKS=0` guarantees "no writes": demonstrate empirically and via Git source (`environment.c:202`, `builtin/commit.c:1634`) that mandatory locks and non-optional write operations (`git add`, `git commit`, `git update-ref`, `git gc`) execute unrestricted.
3. **Coverage**: Identify all residual writer and environment risks for the Frontier F2 repository size census (`tools/souji-repo-structure.sh`), including automatic maintenance (`maintenance.auto`), filesystem monitors (`core.fsmonitor`), custom hook execution (`core.hooksPath`), concurrent external writers, alternates, and inode `atime` modification. Deliver a hardened invocation envelope and concrete checks for L1 integration.

---

## 2. Primary Documentation & Installed Manual Audit (S006)

### 2.1 Canonical Primary Web Sources
- **Source A: `git(1)` Primary Documentation**
  - **URL**: `https://git-scm.com/docs/git`
  - **Access Date**: `2026-10-20`
  - **Upstream Version Tracked**: Git 2.56.0 manual (last updated in 2.56.0, 2026-09-28).
  - **Sections**:
    - `OPTIONS` › `--no-optional-locks`
    - `ENVIRONMENT` › `GIT_OPTIONAL_LOCKS`
- **Source B: `git-status(1)` Primary Documentation**
  - **URL**: `https://git-scm.com/docs/git-status`
  - **Access Date**: `2026-10-20`
  - **Upstream Version Tracked**: Git 2.53.0 manual (last updated in 2.53.0, 2026-02-02; unchanged through 2.54.0–2.56.0).
  - **Section**: `BACKGROUND REFRESH`

### 2.2 Installed Host Manuals
- **Host Package / Version**: Git 2.55.0-1 (`git version 2.55.0`)
- **`git(1)` Manual**: `/usr/share/man/man1/git.1.gz`
  - Roff Header: `.TH "GIT" "1" "2026-06-29" "Git 2.55.0" "Git Manual"`
  - `--no-optional-locks`: roff lines 285–291
  - `GIT_OPTIONAL_LOCKS`: roff lines 2195–2201
- **`git-status(1)` Manual**: `/usr/share/man/man1/git-status.1.gz`
  - Roff Header: `.TH "GIT-STATUS" "1" "2026-06-29" "Git 2.55.0" "Git Manual"`
  - `BACKGROUND REFRESH`: roff lines 1113–1115

### 2.3 Located Verbatim Quotes ($\le 25$ Words)

1. **`git(1)` § ENVIRONMENT `GIT_OPTIONAL_LOCKS`** (roff line 2197; web doc § ENVIRONMENT):
   > "If this Boolean environment variable is set to false, Git will complete any requested operation without performing any optional sub-operations that require taking a lock."  
   *(25 words)*

2. **`git(1)` § OPTIONS `--no-optional-locks`** (roff lines 287–290; web doc § OPTIONS):
   > "Do not perform optional operations that require locks. This is equivalent to setting the GIT_OPTIONAL_LOCKS to 0."  
   *(17 words)*

3. **`git(1)` § ENVIRONMENT `GIT_OPTIONAL_LOCKS` (Side Effect Disclaimer)** (roff lines 2197–2200):
   > "this will prevent git status from refreshing the index as a side effect"  
   *(13 words)*

4. **`git-status(1)` § BACKGROUND REFRESH** (roff line 1115; web doc § BACKGROUND REFRESH):
   > "Scripts running status in the background should consider using git --no-optional-locks status (see git[1] for details)."  
   *(16 words)*

---

## 3. Exact Scope of `GIT_OPTIONAL_LOCKS=0`: What It Does and Does Not Do

### 3.1 Mechanism in Git Source Code
In the Git codebase (v2.55.0 and v2.56.0):
- **Declaration & Parsing**: `environment.h:126` declares `int use_optional_locks(void);`. In `environment.c:202`, it evaluates:
  ```c
  int use_optional_locks(void) {
      return git_env_bool(GIT_OPTIONAL_LOCKS_ENVIRONMENT, 1);
  }
  ```
  CLI flag `--no-optional-locks` sets `GIT_OPTIONAL_LOCKS="0"` in the process environment (`git.c:303`), propagating to all child Git processes.
- **Implementation in `status`**: In `builtin/commit.c:1634-1638` (`cmd_status`), `use_optional_locks()` guards index locking:
  ```c
  if (use_optional_locks())
      fd = repo_hold_locked_index(the_repository, &index_lock, 0);
  else
      fd = -1;
  ...
  wt_status_collect(&s);
  if (0 <= fd)
      repo_update_index_if_able(the_repository, &index_lock);
  ```
  When `GIT_OPTIONAL_LOCKS=0`, Git assigns `fd = -1`, skipping `repo_hold_locked_index` and skipping `repo_update_index_if_able`. The in-memory stat refresh computed during status is discarded on process exit rather than written out to `.git/index`.

### 3.2 Refusing the Overstatement: It Is NOT a "No Writes" Guarantee
It is a dangerous falsehood to equate `GIT_OPTIONAL_LOCKS=0` with a general read-only mode or filesystem write prohibition.
1. **Mandatory Locks Are Untouched**: Any command whose core mandate is modification (`git add`, `git commit`, `git checkout`, `git update-ref`, `git merge`, `git gc`) acquires mandatory locks regardless of `GIT_OPTIONAL_LOCKS=0`.
2. **Empirical Proof (`/var/tmp` test)**:
   - Reproducing Git's `t7508-status.sh:1676` magic mtime test in an isolated repository under `/var/tmp`:
     - Index mtime pre-set to epoch timestamp `946692000` (`2000-01-01 00:00:00`).
     - `GIT_OPTIONAL_LOCKS=0 git status`: Index mtime remains `946692000` (opportunistic index update skipped; verified).
     - Bare `git status`: Index mtime updates to host current epoch `1792473383` (index rewritten; verified).
     - `GIT_OPTIONAL_LOCKS=0 git add file.txt`: Index mtime updates to host current epoch (mandatory write executed; verified).
     - `GIT_OPTIONAL_LOCKS=0 git commit -m "second"`: New commit object created, `refs/heads/master` updated (mandatory write executed; verified).
3. **Conclusion**: `GIT_OPTIONAL_LOCKS=0` suppresses only *opportunistic background sub-operation locks*. It provides zero protection against non-optional commands, configuration hooks, or unconstrained maintenance sub-processes.

---

## 4. Residual Writer and Environment Risks for Size Census

When running repository size census operations (e.g. `tools/souji-repo-structure.sh` wrapping `git repo structure` or `git status`), `GIT_OPTIONAL_LOCKS=0` alone leaves substantial residual risks that must be mitigated by the calling environment.

### 4.1 Automatic Maintenance (`maintenance.auto`) [HIGH RISK]
- **Mechanism**: In Git 2.50+ / 2.55.0, porcelain commands automatically evaluate `maintenance.auto` (enabled by default). When triggered, `git maintenance run --auto` executes background maintenance tasks (`worktree-prune`, `loose-objects`, `pack-refs`, `gc`).
- **Hazard**: Worktree registrations missing from disk past expiry are silently pruned (S001, S009), loose objects are repacked, and commit graphs are written. These write operations use mandatory lockfiles (`.git/maintenance.lock`, `.git/worktrees/<id>/locked`) that ignore `GIT_OPTIONAL_LOCKS=0`.
- **Required Mitigation**: Probes MUST explicitly pass `-c maintenance.auto=false`.

### 4.2 Untracked Cache & FSMonitor Daemons (`core.fsmonitor`) [MEDIUM RISK]
- **Mechanism**: If target repository configuration or global Git configuration sets `core.fsmonitor=true` or points to an external hook binary, Git invokes the monitor hook or contacts a background daemon (e.g. Watchman, FSMonitor daemon).
- **Hazard**: FSMonitor hooks can execute arbitrary binaries, open IPC Unix domain sockets, spawn background processes, or write cache files under `.git/`.
- **Required Mitigation**: Probes MUST neutralize hooks and monitor integration via `-c core.hooksPath=/dev/null` and `-c core.fsmonitor=`.

### 4.3 Concurrent External Writers [MEDIUM RISK]
- **Mechanism**: `GIT_OPTIONAL_LOCKS=0` only constrains the spawned probe process. Sibling fleet processes, operator commands, or IDE background jobs may hold locks or mutate the repository concurrently.
- **Hazard**: If another process runs `git gc --prune` or repack while the size probe inspects reachable objects, loose object files may disappear between reference enumeration and object reading, causing transient `missing object` failures.
- **Required Mitigation**: Size probes must handle transient read errors cleanly, reporting `could-not-evaluate` rather than claiming zero size or corrupting logs (`QUALITY.md` Q18).

### 4.4 Object Alternates (`objects/info/alternates`) [MEDIUM RISK]
- **Mechanism**: Repositories using shared object storage specify paths in `.git/objects/info/alternates` or via `GIT_ALTERNATE_OBJECT_DIRECTORIES`.
- **Hazard**: Size probes will traverse objects across alternate paths, which may cross mount points, reside on network filesystems (NFS/SMB), or point to stale parent repos.
- **Required Mitigation**: Census probes must acknowledge that reported disk size may reflect shared alternate pools, not standalone workspace usage.

### 4.5 Filesystem Access Time (`atime`) [LOW RISK]
- **Mechanism**: Reading loose objects (`.git/objects/??/*`) and packfiles (`.git/objects/pack/*.pack`) causes POSIX file read operations.
- **Hazard**: On filesystems mounted without `noatime` (or with strict atime), inode metadata in `.git/` is mutated by the kernel during the probe.
- **Scope**: Kernel inode metadata modification, not a Git repository state change; does not alter Git SHA or file contents.

### 4.6 Experimental Command Stability (`git repo structure`) [LOW RISK]
- **Mechanism**: `git repo` is explicitly designated EXPERIMENTAL in S005 (§ DESCRIPTION: *"THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY CHANGE."*).
- **Hazard**: Upstream may introduce new internal caches or index interactions in future releases (e.g. Git 2.56+).
- **Required Mitigation**: Recheck on every Git release (`corpus/SOURCES.md` recheck policy `on-release`) and maintain isolated self-test fixtures (`tests/fixtures/r13-repo-structure.sh`).

---

## 5. Frontier F2 Invocation Envelope & Recommendations

### 5.1 Hardened Invocation Envelope
For `tools/souji-repo-structure.sh` and any F2 size census probe, the mandatory execution command must combine lock suppression, maintenance prevention, and hook isolation:

```bash
GIT_OPTIONAL_LOCKS=0 git -C "$REPO" \
  -c maintenance.auto=false \
  -c core.hooksPath=/dev/null \
  -c core.fsmonitor= \
  repo structure --format=lines
```

### 5.2 Bounds on Deletion Authority
- **Census Only**: S006 provides the operational foundation to ensure a census probe does not inadvertently write index cache or trigger background lock contention.
- **No Deletion Authority**: Conforming to `PROVINCE.md` § Refuses and `QUALITY.md` Q18, repository size measurements report object counts and disk consumption only. They **NEVER** grant deletion certification, authorize `rm -rf`, or invoke history rewriting tools (`git filter-repo`, `git-filter-branch`).

---

## 6. Proposed Verification Checks for L1

1. **Verify Index Immutability Under `GIT_OPTIONAL_LOCKS=0`**:
   Execute the magic mtime test under `/var/tmp` to confirm that `status` does not alter `.git/index`:
   ```bash
   bash -c 'TMP=$(mktemp -d /var/tmp/s006-check.XXXXXX); trap "rm -rf \"$TMP\"" EXIT; git init -q "$TMP"; touch -d "2000-01-01" "$TMP/.git/index"; GIT_OPTIONAL_LOCKS=0 git -C "$TMP" status >/dev/null; [ "$(stat -c %Y "$TMP/.git/index")" -eq 946692000 ]'
   ```
2. **Verify Maintenance Suppression**:
   Confirm that `-c maintenance.auto=false` is present on all probe callsites in `tools/souji-repo-structure.sh`:
   ```bash
   grep -F "maintenance.auto=false" /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh
   ```
3. **Verify SOURCES.md S006 Row Conformance**:
   Verify that `corpus/SOURCES.md` row S006 maintains Tier A, valid URL, and references `corpus/knowledge/git-repo-structure-readonly.md` without ungrounded "no writes" claims.
