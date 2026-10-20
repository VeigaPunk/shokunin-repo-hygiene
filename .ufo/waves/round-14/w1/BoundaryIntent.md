# Boundary intent — Souji R14 C2

**Axes:** credential-boundary safety; preservation of ordinary fleet census behavior. **Scope:** code inspection of `tools/souji-census.sh` only. No edits to the census tool or fixture.

## Reconstructed contract and last-known-good invariant

The source documents an immediate-child census: enumerate non-hidden child directories with a `.git` directory, optionally include the root itself, and count linked worktrees on their owner rather than emitting worktrees as separate repository rows (`tools/souji-census.sh` lines 12–16, 316–341). The metadata fields are worktree/commit/status counts, `.scratch` apparent size, timestamps, and stable flags (18–50). The mtime walk emits timestamps and relative names, filters secret-shaped names from its maximum, and does not open those regular files by the code path shown (155–193). The `.scratch` top-level symlink is explicitly reported as zero and `du -P` is used for the directory case (140–153).

The historical safe-use assumption is therefore a trusted fleet root such as `$SHOKUNIN_ROOT`, not an arbitrary path with credential-boundary checks. The new C2 contract is stricter: refuse protected roots/ancestors/aliases and protected comparison inputs before content/Git/enumeration access; do not follow repo-root or `.scratch` symlinks into the protected tree; preserve normal fleet metadata output. These are source-level contracts, not proof of runtime behavior.

## Evidence chain and divergences

1. **Root is not currently a security boundary.** `ROOT` comes from `SHOKUNIN_ROOT`, defaults to the parent of this repository, and can be replaced by either `--root` form (83, 797–804). `canon_path` is `readlink -m` with a raw-input fallback on failure (95). `emit_census` canonicalizes then only checks `[ -d ]` (343–352); it has no protected-path test. Consequently a protected root or ancestor is not rejected before the `list_repos` scan.

2. **Directory aliases are followed before repository canonicalization.** `list_repos` tests each `root/*/` candidate with `-d` and then tests `candidate/.git` (320–335); `census_one` canonicalizes only after that selection (243–254). Its `.git` test accepts any existing `.git`, including a symlink, and then immediately runs `git rev-parse` (246–254). `newest_mtime` later `cd`s to the canonical repo and runs `find` (159–167). Thus an immediate repo symlink into the protected tree can reach metadata enumeration unless checked before the directory/`.git` tests. `--include-root` similarly tests `root/.git` before `census_one` (320).

3. **`--compare` has an earlier read than root validation.** `emit_compare` invokes `load_census "$COMPARE"` before creating a temporary census and calling `emit_census` (414–421). The loader accepts a `-f` path and reads it (365–385), with no lexical/canonical boundary or symlink check. Changed baseline fields are emitted back to stdout (459–461). A protected compare file can therefore be opened before the root is checked and its parsed values can enter output. Reject its path before calling `load_census`; the root guard must also precede this call.

4. **Git owns unresolved metadata paths.** `census_one` invokes Git after only `.git` existence checks (246–267); no code resolves/checks the gitdir/common-dir chain first. The selftest shows the supported linked-worktree representation: a per-worktree metadata directory contains `commondir`, while the worktree `.git` file names its gitdir (560–569). `worktree_extra_flags` later consumes `git worktree list --porcelain` paths and tests/queries existing worktree directories with `count_dirty` (216–235). These paths currently have no protected-path guard before status. The startup environment scrub lists `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, and `GIT_NAMESPACE`, but not `GIT_COMMON_DIR` (71–73). **[INFERENCE]** An ambient `GIT_COMMON_DIR` or a `.git`/`commondir` path into credential storage can redirect Git metadata reads; code inspection establishes that those inputs are not preflighted, not the exact runtime accesses Git would make.

5. **Existing `.scratch` protection is useful but narrow.** `scratch_bytes` rejects a top-level `.scratch` symlink before `du` and uses `-P` (140–148); preserve that behavior. It does not protect a repo root selected through a symlink, and `find` is still run after `cd "$repo"`. The root/candidate path guard must happen before those calls. Avoid describing the whole census as a content-free guarantee: status/refs/worktree queries are Git operations, and this source alone does not prove which metadata Git may read.

## Safe bounded common-dir handling

Keep the current repo selection and output contract; add only the path checks required to stop boundary traversal. First perform component-aware lexical overlap checks for the configured protected root against both root and compare input, including ancestor/equal/descendant cases; reject before `-d`, `-f`, reading the compare TSV, or invoking Git/find/du. Then resolve aliases and apply the same relation to canonical paths, failing closed if resolution fails rather than falling back to an unchecked input. Check each root child and any returned worktree path before directory tests or status; a denied worktree must not be converted silently to absent/clean.

Before any Git command for an accepted repository, keep common-dir discovery filesystem-bounded: reject symlink `.git` entries; for a regular non-symlink gitfile, inspect only its single `gitdir:` target; for a regular non-symlink gitdir, inspect only its optional `commondir` target relative to the gitdir. Resolve and boundary-check the resulting gitdir and common-dir paths lexically and canonically before asking Git to use them. Reject malformed, special, ambiguous, or unresolvable pointer metadata rather than using Git to discover a potentially protected destination. Clear or explicitly boundary-check `GIT_COMMON_DIR` with the existing Git path environment scrub. Do not expand this into general repository/credential discovery: the goal is a direct metadata-path guard, not a new scanner or proof against every possible Git config include/alternate.

## Evidence and confidence

- **Code inspection:** citations above are from `tools/souji-census.sh#5156`; `PROVINCE.md` lines 30–33 and 44–45 place credentials/operator config outside souji's province. Neither the census source nor those province lines specify a concrete protected-root path; do not infer or probe a real credential store. `corpus/QUALITY.md` Q14 (line 38) reinforces report-only treatment of operator runtime surfaces.
- **Exercised evidence:** none. I did not run the census, fixture, Git, or any checks; no runtime safety claim is made. No tools were installed or updated.
- **LSP:** attempted `read xd://lsp`; no LSP device is mounted. The findings are direct file inspection, not semantic reference/call-site proof.
- **Confidence:** high for the ordering and missing guards visible in the shell source; medium for Git's exact downstream path accesses because none were exercised and the report does not claim a comprehensive Git sandbox.

## L1 checks after implementation lands

Not run by this seat. Main/L1 should run both the existing census selftest and the new fixture contract:

```sh
TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
python3 tests/fixtures/r14-census-boundary.py --tool tools/souji-census.sh
```

The fixture invocation follows the R14 task spec (`--tool PATH`) and should use its synthetic HOME/command spies only, never a real credential path. Findings were also sent to `SoujiR14.CensusBoundary`.