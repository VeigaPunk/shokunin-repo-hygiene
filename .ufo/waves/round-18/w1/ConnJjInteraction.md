STATUS: DONE — file-exact landing is the safe jj door only after `info/attributes` is a non-FIFO and watchdog temps, fixture `.git`, and proc-census stay outside the lane.

# Axes

- Operability (judged): a landing commit, a census watchdog, or a proc census must not hang the lane lock, leave a keep-only commit, or plant a nested `.git` / temp file in the colocated worktree.
- Calibration (must not worsen): every check below names a file that exists at b576341 or a file the round is required to add; no citation of `census/round-17/jj-receipts-ddb7347.txt` (C2 dangling). The file-exact list has to include every new path the lesson cites, or LG-DANGLING-PTR fires.
- Coverage (must not worsen): proc census still reports both residue classes (deleted cwd, vanished `/tmp` `/var/tmp` `/dev/shm` argv). The `.jj` ban removes a follow-the-cwd implementation that is already a false negative for the deleted-cwd class.

# Proposal

One landing predicate. Do not enter the lane tree except as a helper pathspec of regular files, and only after `info/attributes` is absent or a regular file. Directory pathspecs, in-lane temps, in-lane fixture `.git`, and any proc-census open of `.jj` are the same colocation failure.

Why the file-exact door is not safe by itself: `scripts/hyaku/jj-lane.sh` puts a directory argument on `fs_dirs` and runs `jj file track` (`:535-565`). A file argument is what later runs `git status --porcelain --ignored` (`:664-666`) while `take_lock` / `flock -w 300` is held (`:132-138`, taken at `:511`). That `git status` is the porcelain the C1 FIFO blocks. `flock -w 300` times out the next waiter; it does not kill the holder. A directory pathspec skips `:665` (`files` stays empty) and takes the other door: `jj commit` at `:604`, phantom-deletion refuse only at `:650-654`, bookmark move at `:658`. The refuse still leaves the commit, and jj's keep ref is the Q28 residue (`corpus/QUALITY.md:72`; `corpus/knowledge/jj-colocation-receipts.md:62-69`, operating rules 2–3 at `:99-100`).

# Evidence

## Helper classifies directories, and the refuse is after the commit

`scripts/hyaku/jj-lane.sh:17` commits are pathspec-limited. `:531` refuses `.git` and `.jj` as named paths; that does not stop a directory pathspec from covering a tree that contains them. `:535-539` a directory becomes `root:"…"`, a file becomes `root-file:"…"`. `:556-558` a named directory is tracked like `git add <dir>` (ignored content stays out; non-ignored new files do not). `:604` `jj commit` runs before the phantom check at `:618-654`. `:665` `git status` runs only when at least one named file was passed.

Q28 (`corpus/QUALITY.md:72`): a nested `.git` inside a tracked tree is a phantom-deletion hazard and is never committed through a directory pathspec. Receipts §7 (`jj-colocation-receipts.md:64-69`): jj ignores any directory containing `.jj` or `.git` (S056); the in-lane repair was a helper call that named the files, not the directory. The same section says the post-commit refuse in the helper still leaves a keep-held commit.

## What is in the tree now

`census/round-18/` contains only `leaked-procs-before-1631.txt`. It is not in HEAD:

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -- census/round-18 tests/fixtures/.gitignore
tests/fixtures/.gitignore

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e HEAD:census/round-18/leaked-procs-before-1631.txt
fatal: path 'census/round-18/leaked-procs-before-1631.txt' exists on disk, but not in 'HEAD'
```

`jj file track` of the directory `census/round-18` would therefore pick up that untracked file and any watchdog temp or editor file that appears beside it before the commit. `tests/fixtures/.gitignore` is two lines:

```
tests/fixtures/*/repo/
tests/fixtures/*/*/repo/
```

That pattern does not match `tests/fixtures/<new>/.git`. A `.git` sitting in the new fixture directory makes jj ignore that directory (receipts §7), so a directory pathspec phantom-deletes the tracked fixture script. File-exact cannot see the script either while that `.git` remains; the round-17 repair removed the stub first.

Lane attributes today (safe: absent):

```
$ stat -L -c '%F %n' -- .git/info/attributes .jj
stat: cannot stat '.git/info/attributes': No such file or directory (os error 2)
directory .jj
```

Absent `info/attributes` is not a FIFO. `.jj` is present (colocated). SrcGitAttrC (this wave): git's open of `info/attributes` is a blocking `open(O_RDONLY)` with no `O_NONBLOCK`, and that source read does not itself prove `git status` builds the attribute stack. The r17 fixture is the observation that a census `status` against a writer-less FIFO at that path blocks (`tests/fixtures/r17-census-hygiene.py` header, D2). [INFERENCE] the helper's `git status` at `:665` is that same subcommand, so a FIFO left at the lane's `info/attributes` blocks the landing commit under the flock. Not re-measured here.

## Fixture `.git` already stays under `/var/tmp`

- `tests/fixtures/r17-jj-receipts.sh:67-74` scratch is `mktemp -d` under `/var/tmp`; every git call is `-C` the scratch repo; every jj call is `-R` that repo. `:146-149` a `jj` invocation from the lane cwd rewrites `.jj/repo/config-id` even with `-R`. `:161-167` the script refuses a scratch outside `/var/tmp` and `cd`s there before any git/jj work.
- `tests/fixtures/r17-census-hygiene.py:1222` `mkdtemp(..., dir="/var/tmp")`. `:274-278` the git spy is prepended to PATH only inside the child env, with `TMPDIR=/var/tmp`.
- `tests/fixtures/r15-census-config.py:1481` same `/var/tmp` mkdtemp.
- `tools/souji-census.sh:1613` selftest `mktemp -d /var/tmp/souji-census-selftest.XXXXXX`; `:1943` `mkfifo` is under that fleet; `:2022-2024` fails the selftest if the fleet is not under that temp.

No r18 fixture file exists yet. The new C1 shim (PATH `git` that swaps `info/attributes` for a FIFO on `status`) has to keep that child-env and `/var/tmp` shape. A shim left on the landing shell's PATH makes the helper's `:665` `git status` the thing that plants the FIFO.

## Watchdog temps are not in `emit_census` yet

`emit_census` (`tools/souji-census.sh:1394-1416`) runs `census_one` in the foreground and captures the row in the shell. There is no per-repo temp and no `set -m`. The only production temp is compare's:

- `:1510` `mktemp /var/tmp/souji-census-now.XXXXXX`
- `:211-214` `cleanup_census_tmp` unlinks that one path on EXIT

A bare `mktemp` would follow `TMPDIR`. The hygiene fixture sets `TMPDIR` in the child (`r17-census-hygiene.py:278`); an r18 fixture that points `TMPDIR` at the lane or at `$ROOT` would drop the watchdog's stdout file inside the tree being measured. That file counts as `??` dirty (receipts §6) and is eligible for `jj file track` if the landing pathspec is the parent directory. SentinelWatchdogKill (this wave): `kill` of a zero or empty PGID signals the caller's process group. [INFERENCE] if that caller group contains `jj-lane.sh commit`, the signal can land after `:604` and before `:658`, which is a keep-only commit of whatever pathspec was in flight. The contract's "`set -m` only around the fork" plus a PGID check that fails closed is what keeps the helper out of that group.

## Proc census must not open `.jj`

`tools/souji-proc-census.sh` is absent at b576341. SrcProcCwd (this wave): `readlink(/proc/pid/cwd)` ending in ` (deleted)` is the deleted-cwd class; `stat -L /proc/pid/cwd` and `cd /proc/pid/cwd` both resolve the magic link onto the live inode and classify the 58 leaked fixture processes as healthy directories. Those inodes are deleted `/var/tmp` repos that contain `.git`. The man-page `cd` recipe would also `chdir` the census into the lane if any scanned process's cwd is the lane, which is a directory that contains `.jj` (stat above). From that cwd, a `jj` call rewrites `.jj/repo/config-id` even with `-R` (`r17-jj-receipts.sh:146-149`). ScoutJjLaneAsRule (this wave) reports the repo config toml outside `.jj` (`jj config path --repo` → `~/.config/jj/repos/…/config.toml`); opening `.jj` does not answer the lane-id question R1 is about. C3 is specified as never signalling and has no repo-timeout, so a blocking open or a `jj` invocation in this tool is an unbounded hang outside C1's watchdog.

# Landing-time checks

Run from the lane root after the r18 files exist and before `jj-lane.sh commit`. All of these are read-only except the commit itself, which is L1's.

1. Attributes and PATH, before the helper. Fail the landing on a FIFO or a shim.

```
stat -L -c '%F' .git/info/attributes
# absent (exit 1, "No such file") or "regular file" / "regular empty file". Anything else: stop.
command -v git
# must be the real git, not a fixture spy directory.
```

2. File-exact pathspec. Every path under `census/round-18/` and `tests/fixtures/` that the lesson, LOG, or SOURCES row cites is a regular file argument after `--`. No directory argument. `census/round-18/leaked-procs-before-1631.txt` is on that list if anything cites it (it is untracked at HEAD).

```
# example shape; the path list is the round's real new files, one per line
test -f census/round-18/leaked-procs-before-1631.txt
test ! -d census/round-18/.git && test ! -d tests/fixtures/r18-census-timeout/.git
# reject the commit if any argument fails test -f or passes test -d
```

Helper invocation (fleet helper, lane id, not `--as souji` — that is R1, not this check):

```
scripts/hyaku/jj-lane.sh commit <lane> --as <lane-id> -m '<msg>' -- \
  census/round-18/<each-file> \
  tests/fixtures/<each-new-file> \
  tools/souji-census.sh \
  tools/souji-proc-census.sh
```

Do not pass `census/round-18` or `tests/fixtures` as arguments.

3. New fixture sources. `git init`, `mkfifo`, and any `jj` token only after a scratch directory that matches `/var/tmp/?*`, and only with `cd` into that scratch or `-C`/`-R` aimed at it. Same predicate as `r17-jj-receipts.sh:161-164`. The git shim is assigned in the child environment only.

4. Watchdog temps in `tools/souji-census.sh`. In the new `emit_census` arm: the template is absolute `mktemp /var/tmp/souji-census-one.XXXXXX` (same shape as `:1510`), the parent unlinks it after reap on both the success path and the timeout path (same shape as `:211-214`), and the path is rejected when it is inside the lane root or inside the resolved `--root`. `set -m` is restored after the fork. The recorded PGID is the child `$!`, matches the child's PGID, and is not the census process's own PGID; otherwise the watchdog does not signal (SentinelWatchdogKill). No temp path is created with `mktemp -p "$ROOT"`, a relative template, or `mkfifo`.

5. `tools/souji-proc-census.sh`. Non-comment lines contain no `jj` command and no open, `cd`, or `find` of a `.jj` path. Deleted cwd is `readlink` plus the ` (deleted)` suffix, not `stat -L`, `test -d`, or `cd /proc/<pid>/cwd`. A redaction pattern that matches the two characters `.jj` inside argv text is fine; it must not open the directory. The tool writes no file under the lane.

# Verdict

Holds as a landing constraint. Partial on the tree: existing r15/r17 fixtures and the compare temp already stay under `/var/tmp`; `emit_census` has no watchdog yet and `souji-proc-census.sh` does not exist, so those two cannot pass the checks until they are written. A directory commit of `census/round-18` fails the constraint today because the only member is untracked.

# Smallest fix

L1 lands the new files with the file-exact helper command above, after check 1. The watchdog temp uses the `/var/tmp` template and the PGID fail-closed check. Proc census uses `readlink` only and does not exec `jj` or open `.jj`. Fixture `.git` and `mkfifo` stay under `/var/tmp`.

# Risks

- The `:665` hang under flock is an inference from the r17 status observation plus the helper source, not a new FIFO trial. SrcGitAttrC explicitly does not prove every `git status` builds the attribute stack.
- Whether `jj file track` / `jj commit` themselves open `info/attributes` during git import was not read in `git_backend.rs` here. The established helper hang site is the explicit `git status`.
- A mis-aimed watchdog signal creating a keep-only commit is an inference from source order (`:604` then `:658`) plus SentinelWatchdogKill's PGID-0 case. It is not a current runtime.
- ScoutJjLaneAsRule's external config path was not re-run (`jj` was not invoked). It does not weaken "do not exec `jj`"; the config-id rewrite is the r17 fixture's own comment.
- Forbidding the substring `.jj` in proc census would reject a redaction pattern. The check is open/exec/`cd`, not the two characters in a comment or a redact regex.
- `mktemp /var/tmp/…` is inside `--root` when someone censuses `/var/tmp` itself. The prefix reject against the resolved root covers that case.

# Commands run

Read-only. No `jj`. No census, verify, vault, quarantine, or proc-census execution. No signals. No installs.

```
stat -L -c '%F %n' -- .git/info/attributes .jj
# stat: cannot stat '.git/info/attributes': No such file or directory (os error 2)
# directory .jj

git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-files -- census/round-18 tests/fixtures/.gitignore
# tests/fixtures/.gitignore

git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e HEAD:census/round-18/leaked-procs-before-1631.txt
# fatal: path 'census/round-18/leaked-procs-before-1631.txt' exists on disk, but not in 'HEAD'
# exit 128
```

Also read: `corpus/QUALITY.md:72`, `corpus/knowledge/jj-colocation-receipts.md`, `scripts/hyaku/jj-lane.sh:1-50,120-159,490-671`, `tools/souji-census.sh:211-214,1394-1416,1510-1516,1590-1623,1906-2024`, `tests/fixtures/.gitignore`, `tests/fixtures/r17-jj-receipts.sh:60-169`, `tests/fixtures/r17-census-hygiene.py:1-80,260-289,1205-1234`, directory listings of `census/round-18/` and `tests/fixtures/`, and this wave's `SrcGitAttrC.md`, `SrcProcCwd.md`, `SentinelWatchdogKill.md`, `ScoutJjLaneAsRule.md`, `SentinelProcCensus.md`.

Tool installs/updates: none.
