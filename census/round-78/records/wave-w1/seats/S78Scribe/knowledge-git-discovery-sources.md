source: S323 — git config documentation at v2.56.0 § CONFIGURATION FILE / Includes (Documentation/config.adoc, accessed 2026-11-07); S324 — git setup.c at v2.56.0, get_common_dir_noenv() (accessed 2026-11-07); S062 — fifo(7); S124 — gitrepository-layout(5) § commondir
verified-at: 319109b0ddc836c6cf3364fdde3ab99796f21f32 (gate `tools/souji-pre-report-gate.sh` sha256 b746bd9da677aefe67116a192626151685a8b9f23e7bfee96987e04e645b4eef; the 17-row measurement `census/round-78/records/c1-after.txt` was bound to 87d456179668738ca59e607c3176de056e6a9991, where the same gate blob hash holds)
recheck: `python3 -B census/round-78/c1-gitsrc-counter.py --gate-dir <dir holding the gate and tools/souji-receipt-write.py from that revision> --work <fresh empty dir>` must print `SUMMARY rows=17 mismatches=0 errors=0 hangs=0` and `EXIT=0`; on every git release, re-fetch S323 and S324 and compare their sha256

# A git command reads its discovery sources before it runs, so one FIFO among them stops the caller

## Claim

Every git command, whatever the subcommand, first resolves the repository and then its configuration, opening
those files with a plain blocking `open(2)`; a FIFO opens only when the other end does (S062). A FIFO at one of
those paths stops the command before any subcommand code runs — and stops the *caller* with it, so a gate
running `git status` in a repository it does not own waits with no bound of its own.

## What git opens first

| path | when git opens it | ground |
|---|---|---|
| `$GIT_DIR` (a `.git` directory, or a `.git` file naming a gitdir) | first; a non-directory, non-regular `.git` is not a repository | gate rule, r78 |
| `$GIT_DIR/commondir` | discovery: existence test, then a blocking `strbuf_read_file` | S324 lines 327-329 |
| `$GIT_DIR/HEAD` | discovery: `validate_headref()` lstat and read | S324 (line 350, named not quoted) |
| `$GIT_COMMON_DIR/packed-refs` | when a ref is resolved | no source quoted this round; the gate refuses a non-regular one (row g3) |
| `/etc/gitconfig`, `$HOME/.gitconfig`, `$XDG_CONFIG_HOME/git/config` | configuration, system then global scope | S323 lines 3-9 |
| `$GIT_COMMON_DIR/config`, `$GIT_DIR/config.worktree` | configuration, repository then worktree scope | S323 lines 3-9 |
| every file an `include.path` or `includeIf.*.path` names | *while* the including config is read: the contents are inserted at the directive's location | S323 lines 94-103 |

A `commondir` file redirects the shared store (S124), so the config, `packed-refs` and worktree config to test are the ones under the *common* directory.

## Why a FIFO is worse than a missing file

A missing file is a quick negative: git falls back to a default. A FIFO is a positive that never completes —
`access(2)` succeeds, the open blocks, and the tool hangs inside its first git call. On the lane-base gate over
the frozen 17-route population 12 rows HANG and only the 75 s row bound ends them, so the gate never reaches
check 4's cheaper pre-check (`census/round-78/controls/c1-K-a-do-nothing.txt`: `SUMMARY rows=17 mismatches=12
errors=0 hangs=12`); with the r78 gate the same 17 rows return in 0.0-0.2 s (`records/c1-after.txt`).

## The gate's rule (round 78)

Before the first git call that discovers the lane, every source above that exists must be a **regular file**; a
symlink counts by its target and a dangling symlink fails. Include targets are followed — relative to the
including file, `~/` expanded, at most 10 deep — each read with `git config --no-includes --file PATH` run from
`/` under `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, so the follow-up read pulls in no global config.
A refusal prints the class `RECEIPT-NONREGULAR-GITSOURCE` with a count and no path, and skips the two
git-dependent checks (check 1 `tip`, check 4 `clean`) as FAIL.

The one source the gate cannot pre-check is the remote one: `ls-remote` runs `upload-pack` in the origin
repository. Both check-1 git calls (`rev-parse`, `ls-remote`) run under `timeout -k 5 45`, and an expiry (124 or
137) prints `RECEIPT-GIT-TIMEOUT` as well as failing `tip` — route t1 fires the class at 45.1 s. Positive controls
keep a blanket refusal from counting as a gain: an honest repository, a regular include, a missing include, a
FIFO in `hooks/` (which discovery never reads) and regular home/XDG configs all pass (q1-q5).

Scores at `census/round-78/`: before, `controls/c1-K-a-do-nothing.txt` reads mismatches=12, hangs=12, EXIT=1;
after, `records/c1-after.txt` reads 17/17, hangs=0, EXIT=0, and the controls stay red (refuse-any-include 14,
config-only 10, timeout-only 11: K-b, K-c, K-d); regressions r77 16/16, r76 30/30, r36 21/21, r27 4/4.

## Stated limits
- SIGTERM to the gate while a git child runs is not handled: `timeout` protects the child, not the gate.
- The system scope is the build's `/etc/gitconfig`; a git built with another `--sysconfdir` is not covered.
- Include conditions are not evaluated: an include git would not read is held to the regular-file rule anyway.
- A source swapped to a FIFO after the pre-check is caught only by the 45 s backstop.
- `packed-refs` and `HEAD` are refused by the same rule, but this round quotes the commondir read only.
