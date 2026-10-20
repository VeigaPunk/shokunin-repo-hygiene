# Round 14 W1 — SourcePaths (SoujiR14.SourcePaths)

Seat: `SoujiR14.SourcePaths` (scout, leaf member).  
Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.  
Axes: calibration, operability.  
Target: Open primary Python pathlib docs (`https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve`) and GNU realpath documentation (`https://www.gnu.org/software/coreutils/manual/html_node/realpath-invocation.html`). Quote $\le 25$ words with exact location, access date, and scope caveats for lexical vs. resolved path guards.  
Acceptance: Finish only assigned slice. Own report under `.ufo/waves/round-14/w1/SourcePaths.md`. No registry edits, no secondary method. Identify final L1 commands.

---

## 1. Executive Summary

This investigation opens and examines the primary vendor documentation for path manipulation across two authoritative ecosystems:
1. **Python 3.15.0 `pathlib` standard library documentation** (covering `PurePath` vs. concrete `Path.resolve`).
2. **GNU Coreutils manual `realpath invocation`** (Section 18.5, installed Coreutils 9.11-2 and manual node).

The core technical question grounding C2 operability (refusing credential-store roots and aliases before directory enumeration or content readers, as codified in QUALITY criterion Q21) is: **What are the foundational semantic differences and security caveats between a purely lexical path guard and a filesystem-resolved path guard?**

### Key Findings
1. **Pure lexical path computation** operates solely on strings without invoking filesystem I/O (`stat`, `readlink`, `open`). It collapses redundant slashes and `/./`, and can check prefixes against forbidden roots.  
   *Caveat:* Lexical analysis cannot detect symlink aliases or target redirections, and naively resolving `..` lexically is formally unsound when a parent component is a symlink.
2. **Filesystem-aware path resolution** (`Path.resolve()`, GNU `realpath`) dereferences symbolic links, eliminates `..` relative to actual directory structure, and determines the true physical target.  
   *Caveat:* Path resolution itself performs filesystem traversal and I/O. If an untrusted input points into or through a protected credential directory, invoking path resolution without an upfront lexical check can probe, touch, or trigger automounts/permissions on protected filesystem inodes.
3. **The Two-Phase Guard Obligation:** Neither lexical guards nor resolved guards alone are sufficient for credential boundary enforcement. A robust boundary guard requires an **ordered two-phase defense**:
   - **Phase 1 (Lexical Pre-Check):** Normalize string components (`//`, `/./`), resolve relative paths against `$PWD`, and reject strings whose prefix or components match protected roots/ancestors before any filesystem call.
   - **Phase 2 (Canonical Resolution & Resolved Guard):** Canonicalize with fail-closed error handling (exit 2 on error), then verify that the resolved physical destination does not intersect the protected store.
   - **Phase 3 (Pre-Traversal Symlink Refusal):** Skip child or `.scratch` symlinks (`test -L`) before issuing directory checks (`test -d`) or calling `git`/`find`/`du`.

---

## 2. Python `pathlib` Documentation Analysis

- **Document URL:** `https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve`
- **Specification Version:** Python 3.15.0 documentation (`pathlib` — Object-oriented filesystem paths)
- **Access Date:** 2026-10-20
- **Document Status:** Primary Tier-A documentation (corresponds to registry row S040 in `corpus/SOURCES.md`).

### 2.1 Located Quotes ($\le 25$ words)

#### Quote 1: `Path.resolve()` Core Semantics
- **Location:** Section "Concrete paths", subsection "Methods", entry `Path.resolve(strict=False)`
- **Verbatim Quote (13 words):**
  > "Make the path absolute, resolving any symlinks. A new path object is returned:"

#### Quote 2: Elimination of `..` Components
- **Location:** Section "Concrete paths", entry `Path.resolve(strict=False)`
- **Verbatim Quote (13 words):**
  > "“..” components are also eliminated (this is the only method to do so):"

#### Quote 3: Non-Strict Resolution Behavior
- **Location:** Section "Concrete paths", entry `Path.resolve(strict=False)`
- **Verbatim Quote (22 words):**
  > "If strict is False, the path is resolved as far as possible and any remainder is appended without checking whether it exists."

#### Quote 4: Pure Paths (No I/O Guarantee)
- **Location:** Section "Pure paths", intro paragraph
- **Verbatim Quote (12 words):**
  > "Pure path objects provide path-handling operations which don’t actually access a filesystem."

#### Quote 5: Danger of Naive Lexical `..` Elimination
- **Location:** Section "Pure paths", entry `PurePath`
- **Verbatim Quote (21 words):**
  > "(a naïve approach would make PurePosixPath('foo/../bar') equivalent to PurePosixPath('bar'), which is wrong if foo is a symbolic link to another directory)"

---

## 3. GNU `realpath` Documentation Analysis

- **Document URL:** `https://www.gnu.org/software/coreutils/manual/html_node/realpath-invocation.html`
- **Installed Vendor Source:** `/usr/share/info/coreutils.info.gz`, Node `realpath invocation`, Section 18.5 "‘realpath’: Print the resolved file name" (coreutils package 9.11-2); manual page `realpath(1)`.
- **Access Date:** 2026-10-20
- **Document Status:** Primary Tier-A documentation (GNU Coreutils reference).

### 3.1 Located Quotes ($\le 25$ words)

#### Quote 1: Canonicalized Name Definition
- **Location:** Node `realpath invocation`, Section 18.5, lines 1–3
- **Verbatim Quote (19 words):**
  > "an absolute file name that contains neither unnecessary ‘/’ nor components that are ‘.’, ‘..’, or a symbolic link."

#### Quote 2: Default Existence Requirement
- **Location:** Node `realpath invocation`, Section 18.5, paragraph 2
- **Verbatim Quote (16 words):**
  > "By default, ‘realpath’ succeeds if every file name component but the last names an existing directory."

#### Quote 3: Purely Lexical Mode (`-s` / `--no-symlinks`)
- **Location:** Node `realpath invocation`, Option `-s` (`--strip`, `--no-symlinks`)
- **Verbatim Quote (16 words):**
  > "Do not resolve symbolic links. Only resolve references to ‘/./’, ‘/../’ and remove extra ‘/’ characters."

#### Quote 4: Physical Resolution Order (`-P` / `--physical`)
- **Location:** Node `realpath invocation`, Option `-P` (`--physical`, default mode)
- **Verbatim Quote (20 words):**
  > "Symbolic links are resolved in the specified file names, and they are resolved before any subsequent ‘..’ components are processed."

---

## 4. Scope Caveats: Lexical vs. Resolved Path Guard

The primary documentation establishes clear boundaries between lexical processing and canonical resolution. Deploying a path guard in security-critical boundary enforcement (such as protecting credential stores from enumeration) requires understanding the exact capabilities and limitations of each method:

| Dimension | Lexical Path Guard (`PurePath`, `realpath -s -m`) | Resolved Path Guard (`Path.resolve()`, `realpath -P`) |
|---|---|---|
| **Filesystem Access** | Zero I/O operations. Evaluates raw path strings purely in memory. | Active I/O operations. Traverses directories, inspects symlink targets (`readlink`), queries inodes (`stat`). |
| **Protected Inode Safety** | **Safe from probing:** Cannot inadvertently touch, traverse, or probe inodes within forbidden directories. | **Probing Hazard:** Calling resolution on an untrusted path that enters a forbidden directory performs directory traversal and `stat` calls before the target check can run. |
| **Symlink Aliases** | **Blind to Symlinks:** Cannot detect if an innocuous path (e.g. `/tmp/scratch/link`) points to a protected target (`~/.omp/agent`). | **Resolves Symlinks:** Fully expands all symbolic links to determine the true target path. |
| **Handling of `..` (Parent)** | **Ambiguous / Unsound:** Collapsing `foo/../bar` to `bar` lexically is invalid if `foo` is a symlink pointing elsewhere. Not collapsing `..` allows traversal strings to escape simple prefix checks. | **Sound:** Eliminates `..` in physical order (resolves preceding symlink first, then steps up to the actual parent directory). |
| **Missing / Virtual Paths** | Operates uniformly regardless of whether files or directories exist. | If path components do not exist: Python `strict=False` resolves existing prefix and appends remainder; GNU `realpath` requires `-m` (`--canonicalize-missing`) to avoid failing on absent components. |
| **Failure Modes** | Pure parsing; deterministic string matching. | Fails on loops (`ELOOP`), permission denials (`EACCES`), or missing components (in strict mode). Vulnerable to fail-open bugs if fallbacks revert to raw uncanonicalized input. |

---

## 5. Architectural Implications for C2 Boundary Guard

In `tools/souji-census.sh`, the census tool must refuse `--root`, `--compare`, worktree paths, and child repositories that overlap the credential store (`$HOME/.omp/agent` and passwd-derived home).

Applying the insights from Python `pathlib` and GNU `realpath`:

1. **Ordering Mandate (Lexical Precedes Canonical):**
   - An untrusted input path must **first** undergo lexical normalization (making relative paths absolute against `$PWD`, collapsing redundant slashes, and rejecting direct lexical matches against protected roots, ancestors, and descendants).
   - Only after passing the lexical guard may canonicalization (`readlink -m` or `realpath`) be invoked.
2. **Fail-Closed Canonicalization:**
   - As observed in `BoundaryReviewRoot.md`, legacy helper `canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }` falls back to the uncanonicalized input if `readlink` fails.
   - If canonicalization fails, the guard must fail closed with exit 2 (`could-not-evaluate`), never trusting the raw string.
3. **Pre-Traversal Symlink Guarding:**
   - In directory walks (such as `list_repos`), testing `[ -d "$d" ]` automatically follows symlinks.
   - Per Python `pathlib`'s warning on symlinks altering parent directory semantics, the census must explicitly check `[ -L "$d" ]` and refuse/skip symlinks **before** calling `[ -d ]`, `git`, `find`, or `du`.

---

## 6. Code Inspection vs. Exercised Evidence

In accordance with round rules and lane boundaries:

- **Code & Doc Inspection (Performed):**
  - Read primary Python documentation: `https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve` (Python 3.15.0 documentation).
  - Read primary GNU Coreutils manual: `/usr/share/info/coreutils.info.gz` node `realpath invocation` (GNU Coreutils 9.11-2) and `man realpath`.
  - Read lane context: `corpus/QUALITY.md` (Q21), `corpus/SOURCES.md` (S038, S040), `corpus/lessons/round-14.md`, `AGENTS.md`, and peer wave reviews (`BoundaryReviewRoot.md`, `BoundaryReviewCompare.md`, `SourceLedger.md`).
- **Exercised Evidence:**
  - Verified local coreutils package version: `pacman -Qi coreutils` $\to$ `9.11-2`.
  - Verified quote lengths in-process with Python string splitting (all confirmed $\le 25$ words).
  - No census tools, gates, test suites, or live fixtures were run.
  - No credential files, `~/.omp/agent`, or operator sweeps were opened, queried, or modified.
- **Registry Mutations:**
  - **None.** This seat authored only this report. No edits to `corpus/SOURCES.md`, `corpus/lessons/`, or shared bookkeeping.

---

## 7. Tool Installs / Updates

- **Tooling Directive Compliance:**
  - No new packages or tools were installed or upgraded during this session.
  - Standard system tools (`pacman`, `info`, Python 3 stdlib) satisfied all requirements.

---

## 8. Final L1 Commands (For Main Agent Verification)

The following verification commands are recommended for the main agent (L1) during final round closure:

```bash
# 1. Verify existence and location of installed coreutils realpath documentation
info coreutils "realpath invocation" --output=- 2>/dev/null | grep -A 3 "Print the resolved file name"

# 2. Verify word-count constraints on all cited quotes in this report (must be <= 25 words)
python3 - <<'EOF'
import re, pathlib
report = pathlib.Path(".ufo/waves/round-14/w1/SourcePaths.md").read_text()
quotes = re.findall(r'> "([^"]+)"', report)
for q in quotes:
    words = len(q.split())
    assert words <= 25, f"Quote exceeds 25 words ({words}): {q}"
print(f"All {len(quotes)} quotes verified <= 25 words.")
EOF

# 3. Static verification of C2 boundary ordering in tools/souji-census.sh (lexical before canon)
grep -nE 'canon_path|readlink|stat|find|du' tools/souji-census.sh

# 4. Confirm no untracked file pollution from this seat
git status --porcelain .ufo/waves/round-14/w1/
```
