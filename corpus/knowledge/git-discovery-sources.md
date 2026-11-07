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

- `$GIT_DIR/HEAD` and `$GIT_DIR/commondir`: git tests that commondir exists and then reads it with
  strbuf_read_file, a blocking read (S324, setup.c get_common_dir_noenv at v2.56.0).
- `$GIT_COMMON_DIR/packed-refs`: read when a ref is not loose (r78 row g3).
- The config files: the system file (`/etc/gitconfig` on this build, read because the gate unsets
  `GIT_CONFIG_NOSYSTEM`), `$HOME/.gitconfig`, `$XDG_CONFIG_HOME/git/config` (or `$HOME/.config/git/config`),
  `$GIT_COMMON_DIR/config` and `$GIT_DIR/config.worktree`.
- Every file an `include.path` or `includeIf.<condition>.path` in one of those names, recursively: "The
  contents of the included file are inserted immediately, as if they had been found at the location of the
  include directive." (S323). Relative values resolve against the including file; `~/` expands to `$HOME`.
- Opening a FIFO for reading blocks until a writer opens it (S062). The same mechanism blocks the exclude
  and attribute sources (S321, r77); r78 extends the rule from check 4 to the files git reads first.

## The rule the pre-report gate applies (r78 C1)

Every listed file that exists must be a regular file (a symlink counts by its target) before the gate's
first git call; includes are walked with `git config --no-includes --file <checked file>` run from `/` with
the global and system config switched off, so the walk itself reads only files already checked. A refusal
prints `RECEIPT-NONREGULAR-GITSOURCE` (a count, never a path) and skips the two checks that run git in the
lane. The remote side cannot be pre-checked — `ls-remote` runs upload-pack in the remote repository — so
check 1 runs under a 45 s timeout and an expiry prints `RECEIPT-GIT-TIMEOUT`.

Measured: the frozen 17-row counter reads 12 hangs at the r78 base and 0 with the rule (rows g1-g11 and t1
refused within the bound; q1-q5, including a regular and a missing include, still pass).

## Limits

- Include conditions are not evaluated: an include whose condition git would not meet is still held to
  the rule (fail closed).
- A FIFO `/etc/gitconfig` cannot be built without root; the rule covers it by path, untested.
- SIGTERM to the gate while a git child runs still leaves the child (r77 S77Sentinel MEDIUM-3).
- Loose refs, `objects/info/alternates` and `shallow` are read by later steps, not discovery; they are not
  in the set.
