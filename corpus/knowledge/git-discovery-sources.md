# Git discovery sources — what every git command opens before it does anything

source: S323, S324, S062, S321
round: 78
status: mined (lane-verified on this host, git 2.56.0)

## Claim

Before any git subcommand runs its own logic, git discovers the repository and loads configuration. That
step opens a fixed set of files in the repository and in the caller's home with a plain blocking open: a
FIFO (or any file whose open blocks) at one of them stops every git command run there, including the
read-only ones a cleanup gate uses (`rev-parse`, `ls-remote`, `status`).

## The set, as this lane checks it

- `$GIT_DIR/commondir`: only when it exists (an lstat-based existence test), git reads it with
  strbuf_read_file, a blocking open (S324, setup.c get_common_dir_noenv at v2.56.0); a plain repository has
  none, a linked worktree opens it several times (S78ScoutSources, strace).
- `$GIT_DIR/HEAD`: discovery validates it (setup.c validate_headref, line 350; a plain O_RDONLY open at line
  373 of the same file, read by S78ScoutSources, not quoted in a row), so `rev-parse --show-toplevel` alone
  blocks on a FIFO HEAD.
- `$GIT_COMMON_DIR/packed-refs` and the checked branch's loose ref: not read by pure discovery, but by every
  ref resolution — `rev-parse --verify refs/heads/<b>` opens packed-refs even when the ref is loose (r78 row
  g3; the loose-ref FIFO is the wave-repair arm a4).
- The config files: the system file (`/etc/gitconfig` on this build, read because the gate unsets
  `GIT_CONFIG_NOSYSTEM`), `$HOME/.gitconfig`, `$XDG_CONFIG_HOME/git/config` (or `$HOME/.config/git/config`),
  `$GIT_COMMON_DIR/config` and `$GIT_DIR/config.worktree`.
- Every file an `include.path` or `includeIf.<condition>.path` in one of those names, recursively: "The
  contents of the included file are inserted immediately, as if they had been found at the location of the
  include directive." (S323). Relative values resolve against the including file; `~/`, `~user/` and
  `%(prefix)/` are expanded by git (the gate asks git to expand them with `--type=path`). A missing include is
  skipped silently (config.c handle_path_include: an ENOENT access check), but a FIFO passes access(R_OK) and
  is then opened with a blocking fopen (S78ScoutSources).
- Opening a FIFO for reading blocks until a writer opens it (S062). The same mechanism blocks the exclude
  and attribute sources (S321, r77); r78 extends the rule from check 4 to the files git reads first.

## The rule the pre-report gate applies (r78 C1)

Every listed file that exists must be a regular file (a symlink counts by its target) before the gate's
first git call; includes are walked with `git config -z --no-includes --type=path --file <checked file>` run
from `/` with the global and system config switched off, so the walk itself reads only files already
checked, records cannot be split by a space in a condition or a newline in a value, and git's own path
expansion decides each target. The walk keys its seen-set on the canonical path and stops at depth 10 and at
64 config files. A non-regular source prints `RECEIPT-NONREGULAR-GITSOURCE` (a count, never a path); a scan
that fails or overruns prints `RECEIPT-GITSOURCE-SCAN`; either skips the two checks that run git in the lane.
The remote side cannot be pre-checked — `ls-remote` runs upload-pack in the remote repository, whose HEAD,
commondir and config all block the same way — so check 1 runs under a 45 s timeout and an expiry prints
`RECEIPT-GIT-TIMEOUT`.

Measured: the frozen 17-row counter reads 12 hangs at the r78 base and 0 with the rule (rows g1-g11 and t1
refused within the bound; q1-q5, including a regular and a missing include, still pass). The wave found five
routes outside the rows (a space in an includeIf condition, a newline in a value, `~user/` and `%(prefix)/`
values, an include fan-out, a FIFO loose ref); the repair closes them and is pinned by probe arms, not by the
frozen rows.

## Limits

- Include conditions are not evaluated: an include whose condition git would not meet is still held to
  the rule (fail closed); a dangling include symlink is refused although git skips it.
- More than 64 include files, or a chain deeper than 10, is refused as a scan overrun even when git would
  read it (policy; git itself stops at depth 10).
- A FIFO `/etc/gitconfig` cannot be built without root; the rule covers it by path, untested.
- SIGTERM to the gate while a git child runs still leaves the child, now for at most the child's own
  timeout (S78Sentinel MEDIUM-3).
- Any other ref the gate's git calls resolve, `objects/info/alternates` and `shallow` are not in the set;
  check 1's timeout bounds them, check 4's 300 s backstop bounds the rest.
- Other lane tools that run git in the lane (the receipt writer, the pointer and freeze checks, the landing
  gate) do not run this scan (S78Connector).
