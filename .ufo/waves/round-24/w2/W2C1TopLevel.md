# W2C1TopLevel — attack on the `--repo must be the top level` refusal (souji-size-census.py)

Seat: L1Souji24.W2C1TopLevel (critic, read-only). Lane tip read: `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`
(wave-1 reports only; `git diff ca7fc1c c3ca7ad -- tools/souji-size-census.py tests/fixtures/r24-size-census.py` is empty).
Tool attacked: `ca7fc1c:tools/souji-size-census.py` (byte-identical to the after-state 778747e and to the lane worktree copy,
`cmp` exit 0). Comparison: instruments `1efe406:tools/souji-size-census.py`. git 2.56.0. Scratch:
`/var/tmp/souji-r24-W2C1TopLevel/` (removed). No installs.

## Status
STATUS: FAIL — the refusal rejects **every bare repository** (exit 2, "not a repository"), a legit input the tool's own
docstring and the frozen CLI contract accept; the C1 fixture is blind to it and to deleting the refusal outright (all mutants 8/8, exit 0).

## Evidence
1. Root cause, raw git (scratch bare clone `bare.git`, and `main/.git`):
   `git -C bare.git rev-parse --path-format=absolute --git-common-dir --git-dir --is-bare-repository --show-toplevel`
   -> stdout prints the 3 lines (`…/bare.git`, `…/bare.git`, `true`) then stderr `fatal: this operation must be run in a work tree`, **rc=128**.
   Same for `bare.git/`, `bare.git/hooks`, `main/.git` (`false`, rc=128).
2. `resolve()` asks `--show-toplevel` in the same call and treats any non-zero rc as "not a repository", before the bare branch:
   - `tools/souji-size-census.py:134` `"--show-toplevel")`
   - `tools/souji-size-census.py:135-136` `if rc != 0:` / `raise Refused("not a repository: " + fail_text(argv, rc, err))`
   - `tools/souji-size-census.py:141` `top = gitdir if bare == "true" else (lines[3] if len(lines) > 3 else "")` — the bare arm is unreachable.
   - `tools/souji-size-census.py:145-146` `return common, "bare"` — dead; `census.invoked_from=bare` can no longer be emitted.
3. Contract it breaks:
   - `tools/souji-size-census.py:6` "PATH must be a work-tree top level (main or linked) or a bare repository's"
   - `.ufo/waves/round-24/preregistration.txt:37` "exit 0 ok; 2 refused (unknown argv incl. any --lost-found, promisor/partialClone repo, not a"
     (a non-promisor bare repository is none of these).
   - Requested fix it mis-implemented: `.ufo/waves/round-24/w1/SentinelSizeEnvelope.md:59` "refuse with exit 2 unless `realpath(--repo)` equals `rev-parse --show-toplevel` (or, for a bare repo, `--absolute-git-dir`)".
4. Input matrix (`python3 -B tool-{instr,after}.py --repo <p>`, cwd = scratch root, every repo has ≥1 commit):

| # | input | expected | got @1efe406 (instr) | got @ca7fc1c (after) |
|---|---|---|---|---|
| 1 | `main` (top) | 0 main | 0 main | 0 main |
| 2 | `main/` trailing slash | 0 main | 0 main | 0 main |
| 3 | `./main/.` | 0 main | 0 main | 0 main |
| 4 | `$S/main` absolute | 0 main | 0 main | 0 main |
| 5 | `mlink` -> main (symlink to top) | 0 main | 0 main | 0 main |
| 6 | `$S.alias/main` (ancestor symlink) | 0 main | 0 main | 0 main |
| 7 | `wt` linked worktree | 0 linked | 0 linked | 0 linked |
| 8 | `wt/` trailing slash | 0 linked | 0 linked | 0 linked |
| 9 | `wtlink` -> wt | 0 linked | 0 linked | 0 linked |
| 10 | `bare.git` (bare, its git dir) | 0 bare | 0 bare | **2 "not a repository"** |
| 11 | `bare.git/` | 0 bare | 0 bare | **2 "not a repository"** |
| 12 | `$S/bare.git` absolute | 0 bare | 0 bare | **2 "not a repository"** |
| 13 | `par/repo.git` (bare inside plain dir) | 0 bare | 0 bare | **2 "not a repository"** |
| 14 | `par` (parent of a bare repo, not a repo) | 2 | 2 not a repository | 2 not a repository |
| 15 | `bp/.git` (bare clone named `.git`) | 0 bare | 0 bare | **2 "not a repository"** |
| 16 | `bp` (parent of that bare `.git`) | 2 (not the git dir) | 0 bare (walked in) | 2 "not a repository" (right code, wrong reason) |
| 17 | `main/nb.git` (bare nested in a work tree) | 0 bare | 0 bare | **2 "not a repository"** |
| 18 | `main/sub` tracked subdir | 2 | 0 (census of main) | 2 must name the repository itself |
| 19 | `main/sub/deep` | 2 | 0 | 2 must name … |
| 20 | `main/plain/x` ignored non-repo dir inside repo | 2 | 0 (enclosing leak) | 2 must name … |
| 21 | `main/lnk` -> sub (in-repo symlink to subdir) | 2 | 0 | 2 must name … |
| 22 | `main/other-link` -> ../other (in-repo symlink to another top) | 0 other | 0 other | 0 other |
| 23 | `main/inner` nested untracked repo | 0 inner | 0 inner | 0 inner |
| 24 | `main/.git` (non-bare git dir) | 2 (contract: top level) | 0 main | 2 "not a repository" (wrong reason) |
| 25 | `bare.git/hooks` | 2 | 0 bare | 2 "not a repository" (wrong reason) |
| 26 | `main/.git/worktrees/wt` | 2 | 0 linked | 2 "not a repository" (wrong reason) |
| 27 | `sepwt` (`--separate-git-dir` work tree) | 0 main | 0 main | 0 main |
| 28 | `sep.gitdir` (its separate git dir) | 2 | 0 main | 2 "not a repository" |
| 29 | `sm-host/smod` submodule top | 0 | 0 (common `.git/modules/smod`) | 0 |
| 30 | `$'nl\nrepo'` top level with newline | 0 | 1 (count-objects on `$S/nl`) | 2 must name … (`top`=`repo/.git`) |
| 31 | `nope` nonexistent / `main/f` file / `nonrepo/d` | 2 | 2 | 2 |
| 32 | `main/plain/x` with caller `GIT_CEILING_DIRECTORIES=$S/main` | 2 | 0 (ceiling dropped with GIT_*) | 2 must name … |
| 33 | `E/sub/D`, enclosing E has `core.worktree=$S/E/sub/D` | boundary | 0 (common `E/.git`) | 0 (common `E/.git`) |
| 34 | `F/plain/G` with planted `.git` gitfile -> `F/.git` | boundary | 0 (common `F/.git`) | 0 (common `F/.git`) |

   Raw control for 32: `GIT_CEILING_DIRECTORIES=$S/main git -C main/plain/x rev-parse --show-toplevel` -> `fatal: not a git repository (or any of the parent directories): .git`.
5. Fixture blindness. `python3 -B tests/fixtures/r24-size-census.py --tool <t>` at c3ca7ad:

| --tool | last line | exit |
|---|---|---|
| `tool-after.py` (= ca7fc1c) | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 0 |
| `mut-norefusal.py` (lines 142-144 deleted) | same | 0 |
| `mut-refusebare.py` (bare branch -> `raise Refused("bare")`) | same | 0 |
| `mut-fix2.py` (correction below) | same | 0 |

   Every fixture call passes a top level (`tests/fixtures/r24-size-census.py:142,151,163,173,185,204,217,231,233` all `'--repo', repo|linked|partial`); no case uses a bare repo, a subdirectory, or a non-repo path.
6. Lane measurement unaffected: `census/round-24/size-census-lane.txt:12` `census.invoked_from=main`.

## Findings
1. **Bare repos refused (regression vs 1efe406, contract breach).** Rows 10-13, 15, 17: exit 2 "not a repository". Location `tools/souji-size-census.py:131-146`. Cause: `--show-toplevel` is in the same `rev-parse` as `--is-bare-repository`; git exits 128 in any bare/git-dir cwd, so the rc gate refuses before line 141 runs. Docstring lines 6-7, 25, 45 (`invoked_from=…bare`) and 62 now describe unreachable behaviour. Impacted axes: operability, calibration.
2. **Wrong refusal reason.** Rows 16, 24-26, 28 refuse with "not a repository" although git resolved one; the operator is told the wrong thing. Same location.
3. **C1 fixture is blind to the refusal in both directions** (Evidence 5). The frozen case set (C=8) has no bare, subdir, or enclosing case, so neither "refusal deleted" nor "all bare refused" moves the counter. Not fixable this round without re-specifying a frozen case (forbidden after scoring), so it is an ATTACK on the counter, not a defect in it: C1's 8/8 says nothing about `--repo` resolution. Impacted axis: coverage.
4. **The enclosing-repo guard works for the plain case.** Rows 18-21, 32: refused; at 1efe406 they censused the enclosing repo. The env allowlist drops a caller's `GIT_CEILING_DIRECTORIES`, so this realpath check is the only guard, and it holds. Survives.
5. **Boundary: `core.worktree` / planted gitfile.** Rows 33-34 census the enclosing repo's common dir from a path physically below it, because git reports that path as the top level. This needs repo config or a planted `.git` file, so it is a tradeoff, not a reject. But the docstring sentence at `tools/souji-size-census.py:25-26` ("so discovery cannot walk up to an enclosing repository") is false for row 33: discovery from `E/sub/D` (no `.git`) does walk up to `E/.git`. Correction: reword it to say the path must be what git reports as the top level. Impacted axis: calibration.
6. **Newline in the top-level path.** Row 30: the after-state refuses a legit top level with a garbled `top` (`repo/.git`), because of the `out.split("\n")` parse at line 137. This was already broken at 1efe406 (exit 1). Low severity; the correction below turns it back into exit 1 (`common` still mis-parses).
7. **Undeclared widening of the exit-2 set.** Subdirectory, non-top, `.git`, `.git/worktrees/<id>` and separate-git-dir inputs (rows 18-21, 24-26, 28) went from exit 0 to exit 2 between the instruments and the after-state. The frozen refusal list (`preregistration.txt:37`) does not name this class. It is stricter and does not change the counter, but it should be disclosed as a CLI deviation in the C1 write-up.
8. **Legit non-bare inputs all survive.** Rows 1-9, 22-23, 27, 29: trailing slash, `./x/.`, symlink to top, ancestor symlink, linked worktree (plain, trailing slash, symlinked), nested repo, separate-git-dir work tree, submodule top.

## Attack log
- Counterexample: `--repo <any bare repo>` -> exit 2 `refused: not a repository` at ca7fc1c; exit 0 `census.invoked_from=bare` at 1efe406.
- Smallest safe correction (`mut-fix2.py`, verified in scratch: rows 10-13, 15, 17 -> 0 bare; rows 18-21, 25 -> 2 "must name"; 24, 26, 28 -> 2 "not a work-tree top level"; rows 1, 7, 27 unchanged; row 33 still 0; fixture 8/8 exit 0). Drop `--show-toplevel` from the combined call and ask for it only when the repo is not bare:

```python
    rc, out, err, argv = git(env, "-C", path, "rev-parse",
                             "--path-format=absolute", "--git-common-dir",
                             "--git-dir", "--is-bare-repository")
    ...
    top = gitdir
    if bare != "true":
        rc, out, err, argv = git(env, "-C", path, "rev-parse", "--show-toplevel")
        if rc != 0:
            raise Refused("not a work-tree top level: " + fail_text(argv, rc, err))
        top = out.rstrip("\n")
```

- Fixture-side remedy is next-round only (frozen C=8): add a bare-repo arm (expect exit 0, `invoked_from=bare`) and a subdir plus ignored-non-repo arm (expect exit 2, manifest unchanged). Either arm kills both mutants in Evidence 5.
- Commands run: the rev-parse probe (Evidence 1); the 34-row matrix over both tool revisions; four fixture runs; the `mut-fix2` matrix; `rg` provenance over `.ufo/waves/round-24/w1/`. Not run: `souji-receipt-run.py verify` (not in this item).
