source: S035 — https://git-scm.com/docs/git-repo, COMMANDS / structure; S036 — https://git-scm.com/docs/git, ENVIRONMENT VARIABLES / GIT_OPTIONAL_LOCKS; S037 — https://github.com/git/git/blob/v2.55.0/builtin/repo.c, structure_count_references / count_objects / cmd_repo_structure
verified-at: 2026-10-20; host Git 2.55.0 (package 2.55.0-1), web docs 2.56.0; empirical result recorded in census/round-13/verification.json
recheck: bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh
ground: F2 — repository size census (structure census of refs-rooted reachable objects)

# Repository structure census: describe reachable objects, do not authorize removal

Coverage-map ground: F2 repository size census. This entry closes the r12 deferred fixture prerequisite, not the full repository-size frontier.

`git repo structure --format=lines` reports reference counts, refs-rooted reachable-object counts, total inflated and disk sizes by object type, and largest objects. The default table is explicitly not intended for machine parsing; `lines` or NUL supplies explicit delimiters, without promising future stability. The command is EXPERIMENTAL, so record the Git version and recheck on releases (S035, DESCRIPTION and COMMANDS / structure).

The lane probe is `bash tools/souji-repo-structure.sh --repo <absolute-repo>`. It suppresses optional locks and lazy fetching, disables auto-maintenance, reports the common Git directory, and refuses partial/promisor repositories. S036's `GIT_OPTIONAL_LOCKS=0` skips optional lock-taking operations; it is not a universal prohibition on writes. The isolated fixture compares Git-directory state before and after the probe. Its observed no-persistent-change result is bounded to the fixture and host version, not arbitrary hooks, configuration, concurrent writers, alternates, transient writes, atime, or future Git versions.

## Decision table

| Observation | Decision |
|---|---|
| Need a machine-readable reachable-object census | Run the probe read-only; preserve its version, command, and output. |
| Need to know filesystem space recoverable by deleting a path | Structure metrics are insufficient; obtain per-artifact receipts and actual filesystem measurements. |
| Need unreachable-object accounting | Use a separate read-only object census; reachable totals do not count unreachable objects. |
| Command unavailable or rejects the repository | Record could-not-evaluate, never substitute zero bytes or a clean deletion verdict. |
| Proposed remedy is gc, repack, pruning, or history rewrite | This probe authorizes none of these; history rewriting remains operator-owned. |

## Failure case and scope

A large reachable-object total is not a stale-artifact receipt. It cannot distinguish live work from preserved content, and deleting a worktree does not necessarily free corresponding object storage. The earlier F2 candidate was deferred precisely because documentation alone did not demonstrate the read-only claim (`corpus/lessons/round-12.md`, Gate; `PROVINCE.md`, F2). This entry requires the committed isolated fixture; no live fleet repository is mutated for the demonstration.

Checklist: record Git version; use the delimited format; disable optional locks, lazy fetch and auto-maintenance; retain the observed output; report size without proposing a deletion unsupported by the receipt taxonomy. The command internally reads Git objects; only metadata is emitted. This round demonstrates it on synthetic fixtures, not credential-bearing repositories.

## Observed failure that narrows the wrapper

AttackCoverage observed on Git 2.55.0 that a `--filter=tree:0` partial clone
made three lazy fetches and changed its Git-directory file count from 28 to
40, even with optional locks off and auto-maintenance disabled. With lazy
fetch disabled, the raw command still returned zero with incomplete counts.
Evidence and exact commands: `.ufo/waves/round-13/w1/AttackCoverage.md`.
The observation is accepted as ground truth, not rerun just to confirm it.

Tagged S037 starts traversal at refs, skips failed object-info reads, and
returns zero after reporting statistics. Therefore the wrapper refuses
partial/promisor repositories and any nonempty stderr or nonzero status;
these guards still do not prove completeness for a corrupt or concurrently
modified arbitrary repository. Detached-HEAD-only and unreachable objects
are outside the refs-rooted census. Linked-worktree outputs describe the
shared common store, so do not sum them as independent repositories.

Freshness note (r16, 2026-10-20): the host now runs Git 2.56.0 (pacman `git 2.56.0-1`, installed 2026-10-20); this entry was verified on 2.55.0 and has not been re-verified on 2.56.0. Treat it as pending recheck (routed to r17), not as re-confirmed.

Re-verification (r24, 2026-10-25): the `recheck:` command above was run unchanged on host Git 2.56.0 (pacman `git 2.56.0-1`) and printed `selftest=PASS ids=5/5` (manifest-control, write-free, object-metrics 29 checks, bogus-repo, promisor-refusal), exit 0; output `census/round-24/records/r13-repo-structure-recheck-git2.56.0.out`, receipt `census/round-24/records/r13-recheck-receipt.tsv`. This closes the r16 freshness note for 2.56.0 only. Its bounds stand and one is sharpened by r24 review (`.ufo/waves/round-24/w1/ReviewRepoStructureFixture.md`): the fixture's manifest is rooted at `--absolute-git-dir`, so from a linked worktree it would not see writes to the shared object store, and its write-free case also passes a probe that does nothing. The r24 debris census fixture (`tests/fixtures/r24-size-census.py`) roots its manifest at the common git dir instead.
