source: S124 — https://git-scm.com/docs/gitrepository-layout — § commondir — web page "last updated in 2.49.0" (2.49.1 → 2.56.0 no changes); installed man page git 2.56.0-1
source: S125 — https://git-scm.com/docs/git — § ENVIRONMENT VARIABLES GIT_COMMON_DIR — web page "last updated in 2.56.0"; installed git(1) 2.56.0-1
source: S126 — https://git-scm.com/docs/git-worktree — § DETAILS — web page "last updated in 2.56.0"; installed man page git 2.56.0-1
verified-at: 2026-10-25 — host git 2.56.0-1; SOURCES S124/S125/S126 opened live and compared with installed man pages; `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` printed `selftest=PASS ids=7/7`, exit 0 (round-25 fixture, unchanged probe blob 0f42ebf5afac)
recheck: on-release — after a host git upgrade, re-run `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` (cases `linked-common-dir`, `colocated-vs-plain`) and re-read SOURCES S124 § commondir and S126 § DETAILS; 180d — re-fetch SOURCES S124/S125/S126/S127 for URL liveness and absence check
ground: F2 — repository size census (where a linked worktree's structure census reads, and why a colocated figure is not a plain baseline)

# A structure census from a linked worktree reads the common dir; a colocated count is not a plain baseline

## Claim (F2: repository size census)

A linked worktree's git dir is a private directory under the main repository's
`worktrees/<id>`; the object store, shared refs and config live in the common
dir that its `commondir` file names (S124 § commondir; S126 § DETAILS).
`tools/souji-repo-structure.sh --repo <linked-worktree>` reports
`probe.git_common_dir` equal to the main repository's absolute git dir (S126 §
DETAILS; the exact `--git-common-dir` call is at `tools/souji-repo-structure.sh:193`)
and `probe.git_dir` equal to the private gitdir, and its counts describe the shared
store: two worktrees of one repository are one census, never two.

The r13 no-write envelope was rooted at `--absolute-git-dir`, which from a
linked worktree is only the private gitdir; a write into the common dir was
invisible to it. Case `SOUJI-R13-STRUCT-linked-common-dir` roots the manifest at
the common dir (which contains the private gitdir) and separately at the
private gitdir, after detector controls on both roots. On git 2.56.0 the probe
left both unchanged.

Precondition for any size baseline: a jj-colocated repository carries
`refs/jj/keep/*` refs that keep otherwise hidden commits reachable. Case
`SOUJI-R13-STRUCT-colocated-vs-plain` (keep refs simulated with `update-ref`,
no jj binary) observed `references.others.count` 2 against 0 and
`objects.commits.count` 2 against 1 for clones of the same repository. Compare
a colocated figure only with another colocated figure, or subtract the keep-ref
closure explicitly; never read it against a plain-clone baseline.

## Decision table

| Observation | Decision |
|---|---|
| `probe.git_dir` differs from `probe.git_common_dir` | Linked worktree: attribute the counts to the common dir; do not add them to the main worktree's figure. |
| No-write evidence is needed for a linked-worktree run | Manifest the common dir, not only `--absolute-git-dir`. |
| `references.others.count` > 0 with `refs/jj/keep/*` present | Colocated figure; not comparable with a plain baseline. |
| Size difference between colocated and plain clones | Not stale-artifact evidence; authorizes no deletion (PROVINCE.md F2). |

## What this does NOT establish

- Real jj-managed repositories: keep refs are simulated; jj's own ref writes, op log and `.jj/` store are not exercised.
- Packs, bare repositories, alternates, submodules, concurrent writers, or a git version other than 2.56.0.
- Read-time touches in future releases: on 2.56.0 the probe left the private gitdir's `gitdir` file mtime unchanged (the manifest records it). A release that refreshes it on reads would make the private-gitdir manifest report a delta (recheck trigger, not a probe defect).
- Universal write-safety: atime and ctime are excluded; a write that restores its own mtime is invisible.

## Lane link and consequence

This entry is the knowledge side of C3 (r25). It extends
`corpus/knowledge/git-repo-structure-readonly.md` (S035–S037), whose r24 note
named the `--absolute-git-dir` blind spot this entry closes. It must be listed
in the F2 row of the `corpus/README.md` coverage map (Q56).

## Gate

url: https://git-scm.com/docs/gitrepository-layout ; https://git-scm.com/docs/git ; https://git-scm.com/docs/git-worktree ; https://git-scm.com/docs/git-rev-parse ; https://git-scm.com/docs/gitglossary
opened: 2026-10-25

- ADMIT: "If this file exists, $GIT_COMMON_DIR (see git[1]) will be set to the path specified in this file if it is not explicitly set." — S124 § commondir — reason: the linked worktree's commondir file is what puts the shared store outside the private gitdir
- ADMIT: "If this variable is set to a path, non-worktree files that are normally in $GIT_DIR will be taken from this path instead." — S125 § ENVIRONMENT VARIABLES GIT_COMMON_DIR — reason: the common directory holds shared non-worktree files
- ADMIT: "$GIT_COMMON_DIR is set to point back to the main worktree’s $GIT_DIR" — S126 § DETAILS — reason: it grounds the linked-worktree case (probe.git_common_dir equals the main repo's git dir)

The git-rev-parse page was opened as corroborating documentation for the exact probe option, but no separate registry row was added; the source hierarchy is represented by the lane implementation path at `tools/souji-repo-structure.sh:193`.
url: https://git-scm.com/docs/gitglossary
opened: 2026-10-25

- REJECT: SOURCES S127 — the briefed gitglossary `common directory` candidate. The closest § worktree quote is “most of which are shared among other worktrees of a single repository”; a page-wide search `grep -ciE 'common|COMMON_DIR' census/round-25/sources/gitglossary.7.txt` yielded 0. It does not define `$GIT_COMMON_DIR`. Flip: a later release adds a located common-directory definition.
