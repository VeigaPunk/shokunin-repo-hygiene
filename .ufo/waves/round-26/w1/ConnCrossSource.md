# ConnCrossSource — Cross-Source Pattern & Knowledge Collision Check for C2

## Status
STATUS: PASS — Zero within-scope duplicate documents (E04 clean; 0 append-refusals) across all 5 staged rows at base and HEAD; 3 outside-scope repository hits recorded as warnings (distinct files in tag v2.56.0 tree); zero knowledge filename collisions in `corpus/knowledge/` against base (both admitted filenames landed cleanly in round 26 without colliding with existing entries).

## Evidence

1. **Grep 1 (`git-scm.com/docs/git-fetch`)**:
   - Command: `grep -n 'git-scm.com/docs/git-fetch' corpus/SOURCES.md`
   - Output: `149:| S128 | git-fetch(1) — https://git-scm.com/docs/git-fetch | docs | A | git 2.56.0 fetch's own auto-maintenance switch, not whether it prunes worktree registrations | ...`
   - Hit count: 1 hit in current registry (line 149, row S128, appended in round 26). Base `0eca7c8` hit count: 0.
   - Quote (`corpus/SOURCES.md:149`, 22 words): "fetch ends by running `git maintenance run --auto`; the operator can disable that run per invocation with `--no-auto-maintenance` / `--no-auto-gc`; the switch is default-on"

2. **Grep 2 (`github.com/git/git/blob/v2.56.0`)**:
   - Command: `grep -n 'github.com/git/git/blob/v2.56.0' corpus/SOURCES.md`
   - Output:
     - Line 85: `S064` (`https://github.com/git/git/blob/v2.56.0/attr.c`) — scope: `how git opens $GIT_DIR/info/attributes and .gitattributes; not which commands consult attributes`
     - Line 141: `S120` (`https://github.com/git/git/blob/v2.56.0/path.c`) — scope: `which $GIT_DIR names count-objects -v reports as linked-checkout garbage when the repository has a separate common dir; not the loose or pack scans (S122) and not a ref-backend claim`
     - Line 143: `S122` (`https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c`) — scope: `when count-objects runs its garbage reporters and how garbage and size-garbage accumulate and print; not which $GIT_DIR names the linked-checkout sweep tests (S120) and not a write-safety claim (S115)`
     - Line 150: `S129` (`https://github.com/git/git/blob/v2.56.0/builtin/fetch.c`) — scope: `the set of porcelain commands that call run_auto_maintenance at tag v2.56.0; call sites only, not a behavioural proof that any of them prunes`
     - Line 151: `S130` (`https://github.com/git/git/blob/v2.56.0/builtin/pull.c`) — scope: `how git pull reaches fetch's auto-maintenance: it spawns git fetch as a child process, so the trigger is inherited rather than duplicated`
   - Quote (`corpus/SOURCES.md:150`, 24 words): "fetch, merge, rebase, am and commit each call `run_auto_maintenance`; the calls sit after the work completes and merge/rebase ignore errors from `git maintenance run --auto`"

3. **Grep 3 (`builtin/pull.c`)**:
   - Command: `grep -n 'builtin/pull.c' corpus/SOURCES.md`
   - Output: `151:| S130 | git/git v2.56.0 builtin/pull.c — https://github.com/git/git/blob/v2.56.0/builtin/pull.c | code | A | how git pull reaches fetch's auto-maintenance: it spawns git fetch as a child process, so the trigger is inherited rather than duplicated | ...`
   - Hit count: 1 hit (line 151, row S130, appended in round 26). Base `0eca7c8` hit count: 0.
   - Quote (`corpus/SOURCES.md:151`, 23 words): "`git pull` runs `git fetch` as a child, so pull's auto-maintenance exposure is fetch's, reached by process spawn rather than a second `run_auto_maintenance` call"

4. **Grep 4 (`r23-trigger-prune`)**:
   - Command: `grep -n 'r23-trigger-prune' corpus/SOURCES.md`
   - Output: `152:| S131 | souji round-2 fixture r23-trigger-prune.sh — lanes/souji/round2/fixtures/r23-trigger-prune.sh | own-work | A | whether git fetch/merge/rebase/pull auto-maintenance actually prunes a worktree registration on git 2.56.0; measured on this host, not inferred from call sites | ...`
   - Hit count: 1 hit (line 152, row S131, appended in round 26). Base `0eca7c8` hit count: 0.
   - Quote (`corpus/SOURCES.md:152`, 18 words): "fetch, pull, merge and rebase each take a stale worktree registration 2 to 1 with no souji receipt"

5. **Grep 5 (`r23-worktree-census`)**:
   - Command: `grep -n 'r23-worktree-census' corpus/SOURCES.md`
   - Output: `153:| S132 | souji round-2 census r23-worktree-census — lanes/souji/round2/evidence/r23-worktree-census.out | own-work | A | whether the fleet's own git worktree set holds registrations today's git would prune; a read-only census of the live fleet, not the round-12 point-in-time figure | ...`
   - Hit count: 1 hit (line 153, row S132, appended in round 26). Base `0eca7c8` hit count: 0.
   - Quote (`corpus/SOURCES.md:153`, 11 words): "the fleet repo has 5 registrations, 0 prunable and 0 locked"

6. **Knowledge filename check**:
   - Command: `git ls-tree 0eca7c8 corpus/knowledge/` and `ls corpus/knowledge/`
   - Base `0eca7c8`: 15 files, neither `git-auto-maintenance-trigger-set.md` nor `git-auto-maintenance-trigger-set-r23.md` existed.
   - Nearest related file: `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md` (present since round 12; non-colliding distinct basename covering git 2.55.0 commit-path pruning).

7. **Automated validator run**:
   - Command: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
   - Output: 34 W04 warnings on pre-existing rows, 0 E03 (duplicate ID), 0 E04 (duplicate URL within scope), 0 E11 (missing used-by), final line `souji ok /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`, exit 0.

## Findings

1. **No within-scope duplicate documents (E04 clean across all 5 rows).**
   None of the 5 staged documents (`git-fetch(1)`, `v2.56.0 builtin call sites`, `builtin/pull.c`, `r23-trigger-prune.sh`, `r23-worktree-census.out`) existed in `corpus/SOURCES.md` at base `0eca7c8`. The only hits in `corpus/SOURCES.md` today are the 5 appended rows themselves (S128–S132), each with its own non-overlapping scope. Location: `corpus/SOURCES.md:149-153`.

2. **Outside-scope warnings on git.git v2.56.0 tree are benign distinct-file references.**
   The query `github.com/git/git/blob/v2.56.0` matches 3 pre-existing rows (`S064` attr.c, `S120` path.c, `S122` builtin/count-objects.c) alongside the two new rows (`S129` builtin/fetch.c, `S130` builtin/pull.c). Each names a completely different source file in the repository tree, addresses a completely different scope, and normalized URL tokens differ (`/attr.c` vs `/path.c` vs `/count-objects.c` vs `/fetch.c` vs `/pull.c`). Neither E04 nor W04 triggers on these rows. Location: `corpus/SOURCES.md:85,141,143,150,151`.

3. **Zero knowledge file name collisions in `corpus/knowledge/`.**
   The two staged knowledge files (`git-auto-maintenance-trigger-set.md` and `git-auto-maintenance-trigger-set-r23.md`) did not exist at base `0eca7c8`. The pre-existing file `git-auto-maintenance-prunes-worktrees.md` shares the `git-auto-maintenance-` prefix but possesses a distinct name, distinct frontmatter sources (`S009`, `S001`, `S003`, `S010`), and different scope (proves `git commit` auto-maintenance pruning on git 2.55.0). The two new entries are complementary expansions rather than name overwrites. Location: `corpus/knowledge/`.

4. **Validator architectural blind spot: `own-work` rows bypass E04 / W04 duplicate checking.**
   In `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:600-603,643-654`, `url_of()` extracts URLs matching `https?://`. For `own-work` rows citing local repo paths (`lanes/...` or `tests/...`), `url_of()` returns an empty string `""`. Consequently, lines 644–654 skip `url_seen` and `url_scopes` tracking completely. Duplicate own-work fixture or evidence paths cannot be detected by K3 automated validation, leaving own-work duplication enforcement entirely dependent on manual reviewer grepping. Location: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:600-654`.

5. **Frontmatter URL divergence on S129.**
   In both `corpus/knowledge/git-auto-maintenance-trigger-set.md:2` and `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md:2`, the frontmatter cites `https://github.com/git/git/tree/v2.56.0/builtin`, whereas `corpus/SOURCES.md:150` records `https://github.com/git/git/blob/v2.56.0/builtin/fetch.c`. The entry references the directory tree, while the registry references the primary fetch call site. E04 validator operates on registry rows, so validation exits 0, but citation URL resolution differs.

## Non-obvious Move (Connector Proposal)

### Proposed Move
**Generalize `sources-census.sh` document identity extraction to index `own-work` filesystem paths alongside HTTP/HTTPS URLs, mechanically closing the silent E04/W04 blind spot for own-work rows.**

- In `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, expand `url_of()` (or introduce `document_key_of(source, kind)`) to parse non-URL path tokens when `kind == "own-work"` (e.g., regex `/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-/]+(\.[a-z0-9]+)/` matching paths such as `lanes/souji/round2/fixtures/r23-trigger-prune.sh`).
- Feed the extracted canonical path into `url_seen` and `url_scopes`.

### Evidence
- `scripts/sources-census.sh:601` isolates `https?://` only; own-work rows S031, S041, S109, S131, S132 produce `u=""`.
- `ExecRenumberMap.md` Finding 2 explicitly recorded: "E04 cannot see the own-work rows... own-work source cells yield an empty key so E04/W04 skip them."
- A census of all 5 `own-work` rows in `corpus/SOURCES.md` reveals 5 completely distinct paths (`tests/fixtures/r12-maintenance-guard.sh`, `corpus/lessons/round-14-verifier-spotcheck.md`, `lanes/souji/round2/evidence/noreplace_probe.py`, `lanes/souji/round2/fixtures/r23-trigger-prune.sh`, `lanes/souji/round2/evidence/r23-worktree-census.out`). Zero collisions exist today.

### Affected Axes
- **Operability (8)**: **Improves**. Replaces ad-hoc, manual seat-by-seat string grep review of own-work fixtures with automated, mechanical enforcement in the maintained fleet validator (`sources-census.sh validate`).
- **Calibration (7)**: **Improves**. Eliminates discrepancy between the documented registry validation contract ("E04 duplicate URL+scope") and actual tool behavior (which silently permitted duplicate own-work paths within the same scope).
- **Coverage (8)**: **Harms none**. Zero existing own-work rows are rejected; all 132 rows remain valid (`exit 0`).

### Risks
- If a future own-work row cites multiple relative paths in a single cell (e.g. `probe.py and probe.out` in S109), path extraction must either select the primary executable or token-split. Bounded mitigation: take the first matched executable/artifact path or key on the normalized path before the `and`.

### Verification
- Test run in isolated scratch (`/var/tmp`): running the generalized path-indexing logic over `corpus/SOURCES.md` yields exactly 132 valid rows, 0 E04, 0 E03, 0 W04 on own-work rows. A synthetic test appending a duplicate `r23-trigger-prune.sh` row triggers `E04 duplicate url within scope` as expected.

## Attack Log
None: not an attack seat; no frozen predicate, target, or case set is challenged.
