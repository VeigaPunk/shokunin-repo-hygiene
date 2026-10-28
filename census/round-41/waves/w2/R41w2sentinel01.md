# R41w2sentinel01 — strace safety and operability review of `tools/souji-freeze-check.py`

Seat: R41w2sentinel01 (role sentinel), wave r41 w2, item "falsify the landed C2 tool". Leaf seat, no subagents.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Lane tip `1d41c13574db80fdd9a4bde490b712da7ce2a85f` (`cat-file -t` = commit).
Subject: the landed tool at `119c26fa3bbb85e215824de9538bd2eb34e9f874`, blob sha256
`3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b` (= candidate R41executor07). Checked with
`git -C <lane> show 119c26f…:tools/souji-freeze-check.py | sha256sum`; the pinned copy used by every run had the same sha.

## Verdict

- **Security line holds on this battery.** No file content was read outside the repository. The tool never opened a
  work-tree file itself. No shell was exec'd. The only write was `/dev/null`. No `--output=` marker file was created.
  `..`, absolute, leading-dash, symlink, gitlink, directory and FIFO inputs produced refusals or findings, never a read.
- **Operability is not clean.** Five defects, all reproduced with rc and output below:
  1. **Hang (new):** a FIFO named `.mailmap` in the work tree blocks the tool indefinitely. `git log` opens
     `<root>/.mailmap` with `O_NOFOLLOW`. The tool was killed at 30 s with no output.
  2. **Silent passes (rc 0, claims counted, zero findings):** empty `Counter:`/`Population:`/`Control:`/`Base:` values;
     claim blocks under `## C2b`, `## c2` or `## C2_x` headers; a duplicate `Counter:` key (first wins); a missing or
     non-numeric `Round:` line (R41S-02, unchanged); and dispatch files whose names git quotes (`"` in the name, or
     non-ASCII under the default `core.quotePath`).
  3. **Caller env changes verdicts:** `GIT_DIR` can turn a red Base or Counter green, or turn a good `--root` into a
     refusal. `GIT_WORK_TREE` never changes a verdict. In-repo `refs/replace/*` (honoured by default, not disabled by
     the tool) turns a digest mismatch green with no env at all.
  4. **Traceback with exit 1:** NUL bytes in a Counter, Population or Control value raise `ValueError: embedded null
     byte`. Exit 1 is also the findings exit code, so a crash is indistinguishable from a red claim at the status level.
  5. **No caps:** a 300 MiB Population takes 1.04 GB max RSS (0.69 s); 2000 claims take 9.3 s. R41S-06 is unchanged.
- **Frozen counter coverage:** none of the defects in 2–4 appears among the 21 cases in `census/round-41/c2-cases.tsv`.
  The counter's `field-empty-target` case covers Target only; `dispatch-before-freeze` uses `Round: 41` only. These pass
  the frozen counter unseen.
- **Remedy checked, not applied:** `git -c log.mailmap=false log …` on the FIFO fixture returns rc 0 in under 10 s;
  `git log --no-use-mailmap` still hangs (rc 124). No tool or counter byte was edited.

Wave-1 R41S status on the landed bytes: R41S-01 (`..` crash) **fixed**; R41S-04 (trailing slash) **fixed**;
R41S-07 (option injection) **fixed**; R41S-02 (Round silent), R41S-03 (space path), R41S-05 (duplicate key) and
R41S-06 (no caps) **unchanged**; the `.mailmap` hang is **new**.

## Method

- Tools: `/usr/bin/strace` 7.2, `git` 2.56.0, Python 3.14.8. **No installs or upgrades** (all present; nothing added to
  `~/.local/bin` or any PATH directory).
- Tool invocation under test (98 invocations in total):
  `strace -f -qq -e trace=%file,%process -o <log> python3 -B <pinned tool> --root <root> --prereg <p> --rev <rev>`, run
  in its own session under a timeout; on expiry only that process group was killed (every process was spawned by the
  driver). `TMPDIR` and every fixture path under `/fast/scratch/hyaku/souji-r41/R41w2sentinel01/` (deleted after receipts
  were copied; other seats' directories there were not touched).
- Fixtures: built only with `git -C <dir>`; toplevel asserted equal to the fixture dir before the first commit; author
  identity only through `GIT_AUTHOR_*`/`GIT_COMMITTER_*`. Sentinel `OUTSIDE-SECRET.txt` (29 bytes, last line `EXIT=1`)
  lies outside every fixture. Had a traversal read it, a `Control` would have passed, so an escape would be visible.
- Classifier (on every `openat`/`open`/`stat`/`readlink`/`access` path and every write-class syscall): ROOT-WORKTREE,
  ROOT-GITDIR, ENV-GITDIR, SENTINEL, SYSTEM, HOME-GITCONF, SCRATCH-OUTSIDE-ROOT, OTHER, plus metadata-only classes
  (ANCESTOR-STAT, ROOT-DIR-STAT, PATH-LOOKUP, PY-IMPORT-PROBE). Relative paths are resolved against `--root` because git
  runs `-C root`. Positive control of the detector: the sentinel was stat-probed in 4 runs and registered as SENTINEL
  each time, so the zero `openat` count is a real zero.
- Driver: `driver/attack_freeze_check.py` (92 battery runs, plus 3 wall-time/RSS wrappers) and `driver/attack_mailmap.py`
  (3 worktree-`.mailmap` runs). Two earlier passes were discarded after a classifier bug (PATH probes counted as escapes;
  relative git paths misclassified). The numbers below are from the final pass only.

## Commands actually run (verbatim, lane paths absolute)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 119c26fa3bbb85e215824de9538bd2eb34e9f874:tools/souji-freeze-check.py | sha256sum
  -> 3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b  -
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t 1d41c13574db80fdd9a4bde490b712da7ce2a85f  -> commit
git -C /home/vgpnk/Projects/shokunin/souji-shokunin for-each-ref refs/replace refs/evil  -> (empty)
git -C /home/vgpnk/Projects/shokunin/souji-shokunin config --show-origin --get-all core.quotepath  -> (empty, unset)
ls /home/vgpnk/Projects/shokunin/souji-shokunin/.mailmap  -> No such file (lane has no .mailmap)
cd .../w2/R41w2sentinel01/driver && TMPDIR=/fast/scratch/hyaku/souji-r41/R41w2sentinel01 python3 -B attack_freeze_check.py
  -> 92 battery runs, wall 30.7 s (stdout: receipts/battery-stdout.log)
cd .../w2/R41w2sentinel01/driver && TMPDIR=/fast/scratch/hyaku/souji-r41/R41w2sentinel01 python3 -B attack_mailmap.py
  -> 3 runs (receipts/runs-mailmap.json)
remedy probe (fixture wt-fifo-mailmap, read-only log, scratch):
  timeout 10 git -C $FX log --diff-filter=A --no-renames --full-history --reverse --format=%H $F -- census/round-41/preregistration.txt     -> rc=124 (hung)
  … same with --no-use-mailmap                                                                                                              -> rc=124 (hung)
  … with -c log.mailmap=false                                                                                                              -> rc=0
  git config --show-origin --get log.mailmap                                                                                               -> unset (git default)
```

## Findings with evidence

Evidence pointers: `receipts/runs.json` (per run: `rc`, `stdout`, `stderr`, `secs`, `classes`, `sentinel_hits`,
`worktree_opens`, `escape_opens`, `writes`, `execs_ok`, `env`, `markers_present`), `receipts/strace/*.strace.gz` (raw
strace for 15 key runs), `receipts/runs-mailmap.json`, `receipts/battery-stdout.log`.

### F1 — hang: FIFO `.mailmap` in the work tree (new; operability and safety)

- Run `wt-fifo-mailmap`: fixture commits a clean prereg; the work tree then gets an uncommitted FIFO `.mailmap`
  (`prw-r--r--` at the root). Result: `rc=-9 timed_out=True secs=30.031`. The driver killed the group at 30 s.
- Strace: `git log --diff-filter=A … -- census/round-41/preregistration.txt` (the `freeze_rev` call) is blocked at
  `openat(AT_FDCWD, ".mailmap", O_RDONLY|O_NOFOLLOW` with no return. It is the last line of its strace log.
- A symlink `.mailmap` is refused by `O_NOFOLLOW`. A regular `.mailmap` is read by git: run `wt-mailmap-content` gives
  `openat(".mailmap", O_RDONLY|O_NOFOLLOW) = 3` and rc 0, and `wt-mailmap-content-bad-digest` gives rc 1 with
  `COUNTER-DIGEST` (the same kind of finding as the no-file fixture `hostile-bad-digest`). The content does not change the verdict, but git still reads the work tree.
- FIFOs at the Population, Counter and prereg paths in the work tree (`wt-fifo-pop`, `wt-fifo-prereg`,
  `wt-fifo-counter`) all returned rc 0 with `SUMMARY claims=1 findings=0`. They do not hang, because the tool reads blobs. A FIFO at the Control path was not run.
- Remedy probe (scratch, `timeout 10`): `-c log.mailmap=false` → rc 0; `--no-use-mailmap` → rc 124 (hung).

### F2 — silent passes (rc 0, `SUMMARY claims=1 findings=0`)

| case (receipt tag) | prereg defect | rc | output |
|---|---|---|---|
| hostile-empty-counter | `Counter:` with no value | 0 | `SUMMARY claims=1 findings=0` |
| hostile-empty-pop | `Population:` with no value | 0 | same |
| hostile-empty-control | `Control:` with no value | 0 | same |
| hostile-empty-base | `Base:` with no value | 0 | same |
| hostile-dup-counter | second `Counter:` line pointing at the sentinel digest | 0 | same (first wins, R41S-05) |
| hostile-hidden-C2b | second claim under `## C2b` with a wrong digest | 0 | `claims=1 findings=0` (block dropped) |
| hostile-hidden-lower-c2 | same under `## c2` | 0 | same |
| hostile-hidden-underscore | same under `## C2_x` | 0 | same |
| disp-no-round-line | no `Round:` line, dispatch file before freeze | 0 | `claims=1 findings=0` (R41S-02) |
| disp-round-word | `Round: forty-one` | 0 | same |
| disp-round-traversal | `Round: 41/../../x` | 0 | same |
| disp-quoted-names | dispatch files `ü-dispatch.json` and `q"x-dispatch.json`, both before freeze | 0 | same (`--name-only` output is quoted; `endswith('-dispatch.json')` misses both) |

Mechanism, read from `tools/souji-freeze-check.py` at 119c26f: `evaluate` tests `if f.get("Counter")`, `if f.get("Population")`,
`if f.get("Control")` and `if f.get("Base")`, so an empty value is skipped; `FIELD-EMPTY` is applied only to Target and
Kill. `HEADER` matches `^## C(\d+)(?![0-9A-Za-z_])`, so `## C2b` and the other variants set `cur = None` and their keys are
discarded. `parse_claims` keeps the first occurrence of each key. `dispatch_findings` returns `[]` when `ROUND` does not
match. `dispatch_findings` compares `base.endswith("-dispatch.json")` against the raw `--name-only` line, which is quoted.
The quoting was confirmed: with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.quotepath GIT_CONFIG_VALUE_0=false`
(`disp-quoted-names-quotepath-off`) rc becomes 1 and reports `FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-41/ü-dispatch.json`.
The `"` name stays silent under either setting.

### F3 — caller-set `GIT_DIR` / `GIT_WORK_TREE` and other git env change verdicts

The tool's env is `dict(os.environ, LC_ALL=C, GIT_OPTIONAL_LOCKS=0, GIT_TERMINAL_PROMPT=0)`, so every `GIT_*` variable
the caller sets is inherited by every git call.

| run (receipt tag) | caller env | rc | output (abridged) | verdict vs. control |
|---|---|---|---|---|
| base-clean | none | 0 | `SUMMARY claims=1 findings=0` | control |
| base-env-gitdir-clone | `GIT_DIR=<bare clone, same objects>` | 0 | same | **unchanged** (GIT_DIR alone is harmless when objects match) |
| base-env-gitdir-empty | `GIT_DIR=<empty bare repo>` | 2 | `REFUSAL … --rev … does not resolve to a commit in <root>` | **changed** (refusal; the message names `--root`, not GIT_DIR) |
| base-env-objdir-empty | `GIT_OBJECT_DIRECTORY=<empty dir>` | 2 | same refusal | **changed** |
| base-env-gitdir-dotgit-plus-worktree | `GIT_DIR=<root>/.git GIT_WORK_TREE=<other dir>` | 0 | `SUMMARY claims=1 findings=0` | unchanged |
| base-env-worktree-only | `GIT_WORK_TREE=<other dir, different census/c1.py>` | 0 | `SUMMARY claims=1 findings=0` | **unchanged**: GIT_WORK_TREE never changes a verdict |
| notarepo-root-no-env | `--root` is a plain directory | 2 | refusal | control |
| notarepo-root-env-gitdir | same `--root`, `GIT_DIR=<base>/.git` | 0 | `SUMMARY claims=1 findings=0` | **changed**: `--root` is not checked; GIT_DIR picks the repository |
| side-base-not-ancestor | Base is a real commit that is not an ancestor of the freeze | 1 | `FINDING C1 BASE-NOT-ANCESTOR …` | control (red) |
| side-base-env-gitdir-grafts | same, `GIT_DIR=<clone>` with `info/grafts` line `F S` | 0 | `SUMMARY claims=1 findings=0` | **red → green** |
| side-base-inrepo-replace-graft | same, in-repo `git replace --graft F S`, no env | 0 | `SUMMARY claims=1 findings=0` | **red → green** |
| side-base-inrepo-replace-graft-nrepl | same, `GIT_NO_REPLACE_OBJECTS=1` | 1 | `BASE-NOT-ANCESTOR` | restores red |
| repl-none-digest-mismatch | prereg states digest of forged bytes; real bytes committed | 1 | `FINDING C1 COUNTER-DIGEST census/c1.py at freeze hashes 2703…, stated b3b5…` | control (red) |
| repl-none-env-gitdir-with-refs-replace | `GIT_DIR=<clone>` holding `refs/replace/<real blob>`→forged | 0 | `SUMMARY claims=1 findings=0` | **red → green** |
| repl-inrepo-refs-replace | in-repo `refs/replace/<real blob>`→forged, no env | 0 | `SUMMARY claims=1 findings=0` | **red → green** |
| repl-inrepo-refs-replace-nrepl | same, `GIT_NO_REPLACE_OBJECTS=1` | 1 | `COUNTER-DIGEST` | restores red |
| repl-env-no-env | `refs/evil/<real blob>`→forged, no replace ref | 1 | `COUNTER-DIGEST` | control (red) |
| repl-env-replace-ref-base | same, `GIT_REPLACE_REF_BASE=refs/evil/` | 0 | `SUMMARY claims=1 findings=0` | **red → green** |
| disp-control | dispatch file before freeze | 1 | `FINDING C0 DISPATCH-BEFORE-FREEZE …` | control |
| disp-env-gitdir-grafts | `GIT_DIR=<clone>` with graft `F B0` | 1 | same verdict, but the named adding commit is now the freeze itself: `first added at 99c095d870d4, not after freeze 99c095d870d4` | verdict unchanged; diagnostic misleading |
| disp-inrepo-replace-graft | in-repo `git replace --graft F B0` | 1 | `DISPATCH-BEFORE-FREEZE` | unchanged (the check accepts `c == freeze`) |
| disp-quoted-names-quotepath-off | `GIT_CONFIG_COUNT=1` `core.quotepath=false` | 1 | finding for the `ü` file only | **silent → red** (the `"` name stays silent) |

Reading the table: `GIT_DIR` changes verdicts (red→green in five cases, green→refusal in two, refusal→green in one). `GIT_WORK_TREE` does not.
In-repo `refs/replace/*` changes verdicts without any env, because `git cat-file` and `git log` honour replace refs by
default and the tool does not set `GIT_NO_REPLACE_OBJECTS`. This lane has no `refs/replace` or `refs/evil` refs and does not
set `core.quotepath`; the exposure is latent here and live for any fetched repository. Git's global configuration
(`~/.gitconfig` and `~/.config/git/config`) is an additional input: git read it in 91 of the 92 battery runs; the one run without the read was not investigated.

### F4 — tracebacks and refusals with misleading wording

- `hostile-nul-counter`, `hostile-nul-control`, `hostile-nul-pop`: prereg values containing `\x00` →
  `ValueError: embedded null byte` from `subprocess` (`Repo.run` catches only `OSError`), **rc 1**.
  `hostile-nul-base` (NUL after a 40-hex Base) gives a clean `BASE-UNRESOLVED`; `hostile-nul-digest-tail` gives a clean
  `COUNTER-DIGEST … has no sha256=<64 hex>`.
- `hostile-long-arg-200k` (one 200 KB argument): **rc 2**, `REFUSAL COULD-NOT-EVALUATE: cannot run git: [Errno 7] Argument list
  too long: 'git'`. Safe refusal, but the wording names git, not the value.
- `base-env-objdir-empty`: `REFUSAL … --rev … does not resolve to a commit in <root>` although GIT_OBJECT_DIRECTORY decided it.
- No `..`-path traceback: the BrokenPipe seen in wave 1 (R41S-01) does not occur on the landed bytes.

### F5 — no caps (R41S-06, unchanged)

| run | size | rc | wall | max RSS (child tree, `RUSAGE_CHILDREN`) |
|---|---|---|---|---|
| huge-pop-300MiB (`census/pop.tsv` of 300 MiB, 100-byte lines) | 300 MiB Population | 0 | 0.686 s | 1,036,732 KB |
| hostile-filler-30m | 30 MB prereg, one claim | 0 | 0.129 s | 147,532 KB |
| hostile-many-2000 | 2000 claims | 0 | 9.272 s | 25,272 KB |
| hostile-many-500 (under strace) | 500 claims | 0 | 9.824 s | — |

Scaling beyond these sizes was not measured.

### F6 — refusals, findings and controls that behave as specified

- Refusals (rc 2, no read): `base-rev-newline` (rev with a trailing newline, `does not resolve`), `base-rev-short` (12-char rev),
  `base-rev-is-base` (rev where the prereg is absent), `base-prereg-dotdot`, `base-prereg-abs`, `base-prereg-dash-eq`
  (`--prereg=-x`), `base-prereg-dash-output` (`--prereg=--output=<marker>`), `hostile-long-arg-200k`.
- Findings (rc 1): `hostile-trav-counter-up/-abs/-deep/-inrepo`, `hostile-trav-pop-mid`, `hostile-trav-control-up/-dotslash/-abs`,
  `hostile-trav-base-abs`, `hostile-dash-counter/-pop/-base/-control/-counter-opt` (all `*-MISSING` or `BASE-UNRESOLVED`; no marker file),
  `hostile-sym-counter-abs/-rel/-loop/-dangling` (`COUNTER-DIGEST`; link text hashed, target not read), `hostile-sym-pop-abs`
  (`POPULATION-DIGEST` + `POPULATION-EMPTY`), `hostile-sym-control-abs` (`CONTROL-NOT-RED`, the link text is shown, not the target),
  `hostile-gitlink-counter/-pop`, `hostile-dir-counter`, `hostile-space-path`, `hostile-trailing-slash`,
  `hostile-long-name-5000`, `hostile-indented-keys` (`FIELD-MISSING Counter`), `hostile-sym-prereg` (`NO-CLAIMS`),
  `base-prereg-…` as above.
- Clean controls that stay clean: `hostile-crlf`, `hostile-latin1-comment` (non-UTF-8 bytes), `hostile-leading-dash-prereg-file`
  (`--prereg=-p.txt`), `hostile-real`, `base-clean`, `lane-tip-r41-prereg`.

### F7 — strace: opens, execs, writes across all 92 battery runs

- **Execs (successful, union):** `/usr/bin/python3`, `/usr/bin/git`. No `sh`, `bash` or other shell.
- **Writes (union):** `openat /dev/null` only (Python `subprocess` `DEVNULL`). Nothing under the root, the work tree,
  `.git` or scratch. `markers_present` is empty for every run.
- **Sentinel:** 0 `openat`. Four `newfstatat` probes, all git's, all `ok`: `base-prereg-abs` (strace line 712,
  `newfstatat(AT_FDCWD, "/fast/…/sentinel/OUTSIDE-SECRET.txt", …, AT_SYMLINK_NOFOLLOW) = 0`); `hostile-trav-counter-abs`;
  `hostile-trav-control-abs`; `hostile-trav-pop-mid` (`census/../../../sentinel/…`, line 1340). Each returned a
  refusal or `*-MISSING`. This is an existence probe, not a read.
- **Escapes (other than metadata):** git's cwd and ancestor discovery (`newfstatat`/`readlink` of `/fast`, `…/souji-r41`,
  `…/R41w2sentinel01/cwd`; `.git`/`HEAD` probes for a non-repo `--root`); Python import probes; `openat` of the tool
  itself (`TOOL`) and of its directory; `~/.gitconfig` and `~/.config/git/config`.
- **Worktree opens:** the tool never opens a work-tree file. Git opens `<root>/.mailmap` (`O_NOFOLLOW`) on every `log`
  (fails here; see F1). `newfstatat census/…` lstat probes come from prereg-derived strings and are metadata only.
- **PATH probes:** failed `execve`/`stat` of `…/bin/git` and `…/bin/python3` in each `PATH` directory come from
  `subprocess` and are not counted as escapes.

## Limits

- The classifier is line-based over strace output. The one blocked call (F1) appears as an `<unfinished …>` line, which
  was read by hand.
- Timings are single runs, with the wrapper's `RUSAGE_CHILDREN` for RSS. Scaling past 300 MiB and 2000 claims was not measured.
- Not tested: a very large regular `.mailmap` in the work tree; the `/dev/zero`-symlink `.mailmap` (refused by `O_NOFOLLOW`
  per the open flags, not run); git global config beyond `core.quotepath`.
- No candidate or counter was scored and no frozen byte was touched. The C2 Target result (claims=3 findings=0 on the R41
  prereg; red on R40) was observed on the lane tip: `lane-tip-r41-prereg` rc 0 `SUMMARY claims=3 findings=0`, `lane-tip-r40-prereg` rc 1 with 18 findings.

## Receipts (inside this seat directory)

- `driver/attack_freeze_check.py` (battery), `driver/attack_mailmap.py` (`.mailmap` cases). Both regenerate every fixture under scratch.
- `receipts/runs.json` (92 battery records plus 3 RSS wrapper records; each record's `argv`, `env`, `rc`, `stdout`, `stderr`,
  `classes`, `sentinel_hits`, `worktree_opens`, `escape_opens`, `writes`, `execs_ok`, `markers_present`, `secs`).
- `receipts/runs-mailmap.json` (the 3 `.mailmap` runs).
- `receipts/battery-stdout.log` (the battery's printed table).
- `receipts/strace/*.strace.gz` (15 raw strace logs: base-clean, base-prereg-abs, base-env-gitdir-empty, hostile-trav-pop-mid,
  hostile-nul-counter, disp-control, disp-quoted-names, side-base-not-ancestor, side-base-env-gitdir-grafts, repl-none-digest-mismatch,
  repl-none-env-gitdir-with-refs-replace, notarepo-root-no-env, lane-tip-r41-prereg, wt-fifo-mailmap, wt-mailmap-content).

## Tooling

No installation, upgrade, or PATH change. `strace` (`/usr/bin/strace` 7.2), `git` 2.56.0 and Python 3.14.8 were used as
already installed. Scratch `/fast/scratch/hyaku/souji-r41/R41w2sentinel01/` was deleted after the receipts above were copied.

## Lane and fleet state

Read-only on the lane: `git show`, `cat-file -t`, `for-each-ref`, `config --get-all`, `ls`, and the landed tool (which
writes nothing). No git mutation, no commit, no push. The only files written are under this seat directory.
