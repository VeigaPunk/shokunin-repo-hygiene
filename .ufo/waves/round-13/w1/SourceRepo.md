# Scoped Source Report: S005 `git-repo(1)` & Frontier F2 Size Census

**Author**: SoujiR13.SourceRepo (Scout)  
**Round / Wave**: Souji Round 13 / Wave 1  
**Target Path**: `.ufo/waves/round-13/w1/SourceRepo.md`  
**Absolute Path**: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/SourceRepo.md`  
**Host Environment**: Arch Linux x86_64, Git 2.55.0 (`git version 2.55.0`, package `git 2.55.0-1`)  
**Role & Posture**: UFO-FSD scout under `/skill:godspeed` (Axes: Calibration, Operability, Coverage). Leaf seat — own only report; no delegation; no commits.

---

## 1. Axes & Executive Summary

1. **Calibration**: Ground S005 against both installed roff source (`/usr/share/man/man1/git-repo.1.gz`, Git 2.55.0-1, 2026-06-29) and primary canonical documentation (`https://git-scm.com/docs/git-repo`, access date 2026-10-20, upstream 2.56.0). Cites exact roff line numbers and word-counted quotes (<=25 words).
2. **Operability**: Document exact `--format` syntax for `git repo structure` (`table`, `lines`, `nul`, `-z`), verify machine-parsing guarantees, identify the total absence of documentation-level read-only guarantees, and establish empirical write-safety bounds under `/var/tmp`.
3. **Coverage**: Formulate concrete, lesson-grounded recommendations for admitting Frontier F2 (`corpus/knowledge/git-repo-structure-size-census.md`) without granting deletion certification, bounded by `GIT_OPTIONAL_LOCKS=0` and `-c maintenance.auto=false`.

---

## 2. Primary Documentation & Installed Manual Audit (S005)

### 2.1 Canonical Primary Source
- **URL**: `https://git-scm.com/docs/git-repo`
- **Access Date**: `2026-10-20`
- **Upstream Revision Tracked**: Git 2.56.0 documentation (published 2026-09-28; noting Git 2.55.0 had no doc changes from 2.54.0).
- **Delta vs Installed 2.55.0**: Upstream 2.56.0 introduces four additional keys under `git repo info` (`path.commondir.absolute`, `path.commondir.relative`, `path.gitdir.absolute`, `path.gitdir.relative`). The `structure` subcommand synopsis, flags, and format semantics are strictly identical between 2.55.0 and 2.56.0.

### 2.2 Installed Host Manual
- **Manual Path**: `/usr/share/man/man1/git-repo.1.gz`
- **Host Package / Version**: Git 2.55.0-1 (`git version 2.55.0`)
- **Roff Header**: `.TH "GIT-REPO" "1" "2026-06-29" "Git 2.55.0" "Git Manual"` (roff line 10)
- **Manual Synopsis** (roff lines 34–38):
  ```text
  git repo info [--format=(lines|nul) | -z] [--all | <key>...]
  git repo info --keys [--format=(lines|nul) | -z]
  git repo structure [--format=(table|lines|nul) | -z]
  ```

### 2.3 Located Quotes (<= 25 words)

1. **Experimental Disclaimer** (§ DESCRIPTION, roff line 44; web doc § DESCRIPTION):
   > "THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY CHANGE."  
   *(8 words)*

2. **Table Format Machine-Parsing Warning** (§ COMMANDS › `structure`, roff line 166; web doc § COMMANDS):
   > "This format may change and is not intended for machine parsing."  
   *(11 words)*

---

## 3. Command Syntax & Machine-Readable Output

### 3.1 Subcommand: `git repo structure`
- **Synopsis**: `git repo structure [--format=(table|lines|nul) | -z]`
- **Formats**:
  - `table` (Default): Human-oriented ASCII tabular layout. Roff line 166 explicitly warns that this format is volatile and not intended for automated consumption.
  - `lines`: Key-value pairs delimited by newline, with key and value separated by `=` (`key=value`). Values with unusual bytes are quoted according to `core.quotePath` (git-config(1)).
  - `nul`: Key-value pairs separated by `\n` between key and value, terminated with `\0` (NUL) after each value. Unquoted.
  - `-z`: Direct alias for `--format=nul`.

### 3.2 Reported Metric Keys (Observed in `lines` / `nul` modes)
Empirical execution against a test repository produces the following deterministic key schema:
- **References**:
  - `references.branches.count=<int>`
  - `references.tags.count=<int>`
  - `references.remotes.count=<int>`
  - `references.others.count=<int>`
- **Reachable Objects Count**:
  - `objects.commits.count=<int>`
  - `objects.trees.count=<int>`
  - `objects.blobs.count=<int>`
  - `objects.tags.count=<int>`
- **Total Inflated Size (Bytes)**:
  - `objects.commits.inflated_size=<bytes>`
  - `objects.trees.inflated_size=<bytes>`
  - `objects.blobs.inflated_size=<bytes>`
  - `objects.tags.inflated_size=<bytes>`
- **Total Disk Size (Bytes)**:
  - `objects.commits.disk_size=<bytes>`
  - `objects.trees.disk_size=<bytes>`
  - `objects.blobs.disk_size=<bytes>`
  - `objects.tags.disk_size=<bytes>`
- **Largest Reachable Objects**:
  - `objects.commits.max_size=<bytes>`, `objects.commits.max_size_oid=<oid>`
  - `objects.commits.max_parents=<int>`, `objects.commits.max_parents_oid=<oid>`
  - `objects.trees.max_size=<bytes>`, `objects.trees.max_size_oid=<oid>`
  - `objects.trees.max_entries=<int>`, `objects.trees.max_entries_oid=<oid>`
  - `objects.blobs.max_size=<bytes>`, `objects.blobs.max_size_oid=<oid>`
  - `objects.tags.max_size=<bytes>`, `objects.tags.max_size_oid=<oid>`

---

## 4. Documentation Guarantees vs Reality: Read-Only Analysis

### 4.1 Absence of Documentation Guarantees
- The manual states only: *"Retrieve statistics about the current repository structure."*
- **No Read-Only Guarantee**: There is **no** text in `git-repo(1)` or `git-scm.com/docs/git-repo` guaranteeing that the command does not mutate repository state, create temporary packfiles, update indices, or take locks.
- **No `--dry-run` Flag**: Unlike modifying commands (e.g. `git clean -n`, `git repack --dry-run`), `git repo structure` provides no execution simulation flags.
- **Inherent Porcelain Risks**: In standard Git operation, porcelain invocations may implicitly trigger `git maintenance run --auto` (pruning worktrees if expired, per S001/S009) or refresh index timestamp entries unless explicitly suppressed.

### 4.2 Empirical Write-Safety Verification
To establish empirical bounds (satisfying Q2, Q4, and resolving the r12 deferral in `corpus/lessons/round-12.md:133`), tests were executed under an isolated `/var/tmp` test harness:
1. **Stat Comparison**:
   - Created isolated fixture repo at `/var/tmp/srepo-write-test.XXXXXX` with commit.
   - Pre-invocation stat snapshot: `find .git -exec stat -c "%n %s %Y" {} +`.
   - Executed:
     - `GIT_OPTIONAL_LOCKS=0 git -C "$TMPDIR" -c maintenance.auto=false repo structure --format=lines`
     - `GIT_OPTIONAL_LOCKS=0 git -C "$TMPDIR" -c maintenance.auto=false repo structure --format=nul`
     - `git -C "$TMPDIR" repo structure --format=table`
   - Post-invocation stat snapshot: identical file tree, identical sizes, identical mtimes (`diff -u` produced 0 lines).
2. **Syscall Tracing (`strace`)**:
   - `strace -e trace=open,openat -f git -C "$TMPDIR" repo structure --format=lines`
   - Result: Exactly 0 repository files or `.git/` administrative files were opened with write flags (`O_WRONLY`, `O_RDWR`, `O_CREAT`). The only write fd opened was descriptor 3 on `/dev/null`.

---

## 5. Frontier F2 Recommendation & Admissible Scope

### 5.1 F2 Knowledge Admission Strategy
- **Prerequisite Closure**: Resolves the r12 Gate C3 deferral (*"ART §9 open question unresolved: whether git repo structure writes or takes locks was not tested"*).
- **Recommended Knowledge Entry**: `corpus/knowledge/git-repo-structure-size-census.md`.
- **Source Transition in `corpus/SOURCES.md`**:
  - Row `S005`: Update `status` from `queued` to `mined`.
  - Row `S005`: Update `used-by` from `—` to `corpus/knowledge/git-repo-structure-size-census.md`.
  - Pair with `S006` (`GIT_OPTIONAL_LOCKS=0`).

### 5.2 Mandatory Operational Envelope (Empirical Write-Safety Bound)
Any production or tool usage of `git repo structure` within souji tools (e.g. `tools/souji-repo-structure.sh`) MUST enforce the following invocation bounds:
```bash
GIT_OPTIONAL_LOCKS=0 git -C "$REPO" -c maintenance.auto=false repo structure --format=lines
```
1. `GIT_OPTIONAL_LOCKS=0`: Enforces read-only index behavior (prevents background refreshes).
2. `-c maintenance.auto=false`: Prevents automatic maintenance triggers from pruning worktree registrations or repacking.
3. `-C "$REPO"`: Eliminates directory drift.
4. `--format=lines` (or `--format=nul`): Mandatory for programmatic consumption. `--format=table` is forbidden in automated pipelines due to S005's explicit instability warning.

### 5.3 Boundaries & Limitations (No Deletion Certification)
- **Informational Census Only**: An F2 entry and size probe provide object and disk accounting only. Under `PROVINCE.md` § Refuses and `corpus/QUALITY.md` Q18, size census **NEVER** grants deletion authority or certifies live artifact removals.
- **Experimental Status Caveat**: Because upstream classifies `git repo` as EXPERIMENTAL, parsing logic in souji tools must gracefully handle unexpected keys or key renames without crashing.
- **Split Gitdir / Bare Repos**: Submodules, separate gitdirs (`--separate-git-dir`), and bare repos require regression testing in fixture suites to confirm identical non-mutating behavior.

---

## 6. Proposed Verification Checks for L1

1. **Self-Contained Fixture**: Run `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-repo-structure.sh --selftest` (verifying isolation under `/var/tmp` and zero `.git` stat delta).
2. **Sources Census Validation**: Validate that `corpus/SOURCES.md` row S005 conforms to `SOURCES-CONTRACT-v1` (11 columns, tier A, valid enum status `mined`).
3. **Format Parsing Integrity**: Verify that `tools/souji-repo-structure.sh` rejects `--format=table` for programmatic queries and requires `--format=lines` or `--format=nul`.
