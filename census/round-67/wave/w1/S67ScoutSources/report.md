# S67ScoutSources — git source capture for round 67 C1 (GIT_COMMON_DIR)

Seat: `S67ScoutSources` (wave w1 of round 67). Lane: `souji-shokunin`.
Deliverables in this directory: `environment.txt`, `worktree.txt`, `environment.html`,
`quotes.tsv`, `absences.tsv`, `report.md`, `probes.sh` + `probes.txt` (behavioural probe
receipt), plus supporting captures (`setup.txt`, `run-command.txt`, `git-c.txt`,
`environment-h.txt`, `builtin-worktree.txt`, `doc-git.txt`, `doc-git-worktree.txt`,
`doc-gitrepository-layout.txt`).

No lane file was edited. No git/jj mutation was run in the lane tree. All probes ran in
scratch fixtures under `/fast/scratch/hyaku/souji-r67/S67ScoutSources/`, removed before yield.

## 0. Host version check (bounding)

    $ git --version
    git version 2.56.0

Host git is 2.56.0, so the requested tag `v2.56.0` is the correct tag. **No substitution was
needed.** The rendered `git-scm.com/docs/git` page independently reports "last updated in 2.56.0"
(found in `environment.html`), so the docs capture matches the host version too.

## 1. Captures: access dates, fetch command + exit code, HTTP status, byte counts, sha256

All fetches: `curl -sS -L -o <file> -w '%{http_code}' <url>` (exit code of `curl` recorded as
`exit`; HTTP status as `http`). Access dates are UTC (ISO 8601).

| delivered file | URL | access date (UTC) | fetch | exit | http | bytes | sha256 |
|---|---|---|---|---|---|---|---|
| `environment.txt` | `https://raw.githubusercontent.com/git/git/v2.56.0/environment.c` | 2026-11-05T16:37:02Z | curl -sS -L | 0 | 200 | 20931 | `5b52a5a123a6b340c78eb4762cfc6b3184c983a30106dfc7828efeff4127c5f3` |
| `worktree.txt` | `https://raw.githubusercontent.com/git/git/v2.56.0/worktree.c` | 2026-11-05T16:37:03Z | curl -sS -L | 0 | 200 | 31092 | `da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2` |
| `environment.html` | `https://git-scm.com/docs/git` | 2026-11-05T16:37:04Z | curl -sS -L | 0 | 200 | 244227 | `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1` |
| `setup.txt` | `.../v2.56.0/setup.c` | 2026-11-05T16:38:18Z | curl -sS -L | 0 | 200 | 83214 | `8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589` |
| `run-command.txt` | `.../v2.56.0/run-command.c` | 2026-11-05T16:38:19Z | curl -sS -L | 0 | 200 | 49361 | `5cdcbaccf88f6b6c36397dfe98da9f07e392664a6db79dad63d35ab6853d78b4` |
| `git-c.txt` | `.../v2.56.0/git.c` | 2026-11-05T16:38:19Z | curl -sS -L | 0 | 200 | 30923 | `0e1bbafb1fa791d07a91e9e714adb1274e1247ce5d7b9bde46562f0d55494432` |
| `environment-h.txt` | `.../v2.56.0/environment.h` | 2026-11-05T16:38:19Z | curl -sS -L | 0 | 200 | 8738 | `6dc06c6a9167f72103759908c961da150eb6007fd3b135e8744ac8711bdbb90f` |
| `builtin-worktree.txt` | `.../v2.56.0/builtin/worktree.c` | 2026-11-05T16:38:19Z | curl -sS -L | 0 | 200 | 44631 | `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc` |
| `doc-git.txt` | `.../v2.56.0/Documentation/git.adoc` | 2026-11-05T16:39:30Z | curl -sS -L | 0 | 200 | 47005 | `050c5330f1a231be22bee3db27c7ef90d8ba22bb7bd6c72c8bab462f6f0a1f79` |
| `doc-git-worktree.txt` | `.../v2.56.0/Documentation/git-worktree.adoc` | 2026-11-05T16:38:20Z | curl -sS -L | 0 | 200 | 22021 | `ee8a368564ace74a07e4a034e080b26fb1c3b35d17ef1fe41dcbfcc5595fe8dc` |
| `doc-gitrepository-layout.txt` | `.../v2.56.0/Documentation/gitrepository-layout.adoc` | 2026-11-05T16:41:22Z | curl -sS -L | 0 | 200 | 11890 | `39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439` |
| `repository.txt` | `.../v2.56.0/repository.c` | 2026-11-05T16:47:04Z | curl -sS -L | 0 | 200 | 12445 | `7fb5a64b7592aae4de61a5c2f9affad7e58029a59311207359d6769c11112730` |

Whole-tag cross-check: `https://codeload.github.com/git/git/tar.gz/refs/tags/v2.56.0`
(2026-11-05T16:37:26Z, exit 0, http 200, 12789076 bytes, sha256
`d761232b81394f7d4c3ef1a99fa804ffbe10d278ae1ad302833a0892050ca9fc`). Every delivered
capture is **byte-identical** to its member in that tarball (sha256 compared programmatically;
all 11 matched). This makes the raw.githubusercontent captures trustworthy as tag-pinned bytes.

## 2. What each capture grounds

- `environment.txt` (git v2.56.0 `environment.c`) — `GIT_COMMON_DIR_ENVIRONMENT` occurs exactly
  once, at `environment.c:99`, as a member of `local_repo_env[]` (the list of repository-local
  `GIT_*` variables). `GIT_NAMESPACE_ENVIRONMENT` occurs once, at `environment.c:182` inside
  `get_git_namespace()`. `environment.c` contains **no** `setenv`/`unsetenv`/`putenv` and no
  `getenv` of `GIT_COMMON_DIR`. Grounds: which of the three names git reads, where, and the
  fact that `GIT_COMMON_DIR` is on git's own scrub list.
- `worktree.txt` (git v2.56.0 `worktree.c`) — contains **no** occurrence of `GIT_COMMON_DIR`,
  `GIT_COMMON_DIR_ENVIRONMENT`, `GIT_NAMESPACE` or `GIT_CEILING_DIRECTORIES`, and no
  `getenv`/`setenv`/`unsetenv` at all. It resolves common dirs from the repository struct
  (`repo->commondir`, `repo_get_common_dir`) and, for submodules, deliberately calls
  `get_common_dir_noenv()`. Grounds: the linked-worktree and submodule paths of design
  statement (ii).
- `setup.txt` (git v2.56.0 `setup.c`) — the two `GIT_COMMON_DIR` **read** sites
  (`get_common_dir()` at :311-320, `apply_gitdir_and_environment()` at :1062-1066), the
  no-env file route (`get_common_dir_noenv()` at :321-347) with its relative-path
  canonicalization, the `chdir` into the worktree top level, and the
  `GIT_CEILING_DIRECTORIES` read at :1574.
- `run-command.txt` (git v2.56.0 `run-command.c`) — `sanitize_repo_env()` (scrub of
  `local_repo_env` members) and `prep_childenv()` (a bare name in the delta env *removes*
  the variable). Grounds: git's own scrub semantics, which the candidate's scrub mirrors.
- `git-c.txt` (git v2.56.0 `git.c`) — the only `setenv` of `GIT_NAMESPACE_ENVIRONMENT` in git
  (`--namespace` option). Grounds L3.
- `environment-h.txt` (git v2.56.0 `environment.h`) — canonical spellings of all three names.
- `builtin-worktree.txt` (git v2.56.0 `builtin/worktree.c`) — `add_worktree()`: the child
  environment carries `GIT_DIR` and `GIT_WORK_TREE` only; the linked worktree's common dir is
  written as a **`commondir` FILE**. Grounds design statement (ii).
- `repository.txt` (git v2.56.0 `repository.c`) — `repo_set_commondir()` (:153-168): the caller-injected value
  becomes `repo->commondir` and sets `repo->different_commondir = 1`; `repo_set_gitdir()` (:170-186)
  passes it in. Grounds the second half of design statement (i).
- `doc-git.txt` (tag-pinned `Documentation/git.adoc`) and `environment.html` (live
  `git-scm.com/docs/git`) — the documented contract of `GIT_COMMON_DIR`; both carry the same
  sentence, and the rendered page is the 2.56.0 text.
- `doc-git-worktree.txt`, `doc-gitrepository-layout.txt` — the documented linked-worktree
  mechanism (`.git` file) and the `commondir` file route with its "$GIT_DIR"-relative rule.

`environment.html` was fetched because the two `.txt` captures (C source) contain no
user-facing description of the variable; the docs sentence grounds design statement (i) in
the published contract as well as in the code.

## 3. The two design statements, grounded

### (i) A caller-injected `GIT_COMMON_DIR` redirects the common-dir resolution — CONFIRMED

- `setup.c:311-320` `get_common_dir()`: `getenv(GIT_COMMON_DIR_ENVIRONMENT)`; if set, the value
  is appended to the common-dir buffer and returned, and the on-disk `commondir` file is never
  consulted (`get_common_dir_noenv()` is the `else` branch).
- `setup.c:1062-1066` `apply_gitdir_and_environment()`: the same variable is bound into
  `struct set_gitdir_args` as `.commondir`, i.e. it becomes the repository's own common dir
  (`repository.c:153-168` `repo_set_commondir()` sets `repo->commondir` to it and sets
  `repo->different_commondir = 1`).
- Docs: `git(1)` ENVIRONMENT VARIABLES — "If this variable is set to a path, non-worktree files
  that are normally in $GIT_DIR will be taken from this path instead."
- Behavioral confirmation on this host (scratch fixtures, git 2.56.0):
  `GIT_COMMON_DIR=<copy of .git with core.fileMode=false> git status --porcelain` reported the
  tracked 755→644 mode change as **clean**, while the same tree without the injection reported
  ` M f`. That is the W2 route of the r66 lesson, reproduced mechanically: the injected value
  governs `core.fileMode` because the common dir's `config` is read from the injected path.

### (ii) Git itself sets `GIT_COMMON_DIR` for subprocesses in specific contexts (worktree/submodule) — NOT SUPPORTED by git v2.56.0 source

This is the load-bearing negative of this seat. The sweep is in `absences.tsv`; the summary:

- `setenv(GIT_COMMON_DIR`, `xsetenv(GIT_COMMON_DIR`, `putenv(GIT_COMMON_DIR` → **0 hits** in
  the entire v2.56.0 tree excluding `t/`. The only assignment form `GIT_COMMON_DIR=` occurs
  **only in the test suite** (`t/t0060-path-utils.sh`, `t/t1900-repo-info.sh`).
- `GIT_COMMON_DIR_ENVIRONMENT` has exactly **4** hits in the tree (excluding `t/`): the define
  (`environment.h:9`), the scrub-list membership (`environment.c:99`), and **two reads**
  (`setup.c:312`, `setup.c:1066`). There is no fourth kind of site.
- **Worktree context:** `builtin/worktree.c add_worktree()` pushes **only** `GIT_DIR` and
  `GIT_WORK_TREE` into `child_env` (`:584-585`). The linked worktree's common dir is expressed
  as a **file**: `strbuf_addf(&sb, "%s/commondir", sb_repo.buf); write_file(sb.buf, "../..");`
  (`:543-544`). `git-worktree(1)` says the same in prose: "These settings are made in a `.git`
  file located at the top directory of the linked worktree." The environment variable is a
  *reading* of that file, not an export.
- **Submodule context:** `worktree.c:553-556` `submodule_uses_worktrees()` calls
  `get_common_dir_noenv()` with the comment "The env would be set for the superproject." —
  i.e. git itself **bypasses** `GIT_COMMON_DIR` on the submodule common-dir path. Git's
  submodule child environments go through `prepare_submodule_repo_env()` →
  `prepare_other_repo_env()` → `sanitize_repo_env()`, which **removes** `GIT_COMMON_DIR` from the
  child environment.
- Historical check (same sweep at older tags): v2.5.0, v2.20.0 and v2.30.0 all have the same
  read-only pattern (no export site); v2.4.0 has no `GIT_COMMON_DIR` at all. So the negative is
  not an artifact of the 2.56.0 refactor.

Behavioral confirmation on this host: a `post-checkout` hook inside a linked worktree saw
**no** `GIT_COMMON_DIR` in its environment (only `GIT_DIR=<...>/worktrees/wt`); with
`GIT_COMMON_DIR` exported in the parent, the child inherited it only because the parent had it
— git neither set nor scrubbed it there, because `worktree add`'s child env is built by
`strvec_pushf` additions, not by `sanitize_repo_env()`.

**Consequence for the C1 design (finding, not a claim restatement):** the design's stated
ground for "git sets it for subprocesses in worktree/submodule contexts" does not hold in
git 2.56.0. What the source does support is the *opposite* direction and a stronger one:
`GIT_COMMON_DIR` is on git's own `local_repo_env[]` scrub list, and git's `sanitize_repo_env()`
removes it from child environments. The candidate writer's "scrub the variable on every git
call" rule therefore matches git's own rule for repository-local variables, which is a
defensible ground. Any SOURCES row that says "git sets GIT_COMMON_DIR for subprocesses" would
be false against these captures and should be worded as "git scrubs it; git never sets it".

### Auxiliary facts for the C1 value check (bounded to what the source shows)

- The env value is used **verbatim**: `get_common_dir()` does `strbuf_addstr(sb,
  git_env_common_dir)` with no canonicalization, and `repo_set_commondir()` does
  `xstrdup(commondir)`. Only the *file* route canonicalizes (`strbuf_add_real_path`), and
  relative file paths are anchored at `$GIT_DIR` (`setup.c:336-339`;
  `gitrepository-layout(5)`: "If the specified path is relative, it is relative to $GIT_DIR").
- A relative **env** value is therefore interpreted relative to git's own working directory at
  read time, and git `chdir`s into the discovered worktree top level during setup
  (`setup.c:1225`). Measured on this host: with `-C <repo>/sub` and
  `GIT_COMMON_DIR=../.git`, git resolved the common dir to `<repo-parent>/.git` — i.e. relative
  to the worktree top level, **not** relative to the writer process's cwd and not relative to
  the `-C` directory. This bears directly on prereg limit **L2**, which states the writer
  "canonicalizes a relative value against the writer process's cwd, the rule git applies".
  Against git 2.56.0 source, git's rule is *not* "against the writer process's cwd" — it is
  relative to the worktree top level git chdirs into. **Flagged as a possible L2 wording
  defect for the L1 / reviewer seats**; it is a source-grounded observation, not a claim
  change.
- `GIT_COMMON_DIR` set to an **empty** value: `getenv` returns `""` (non-NULL), so git takes the
  env branch and the common dir becomes the empty string; git then reports "not a git
  repository" (measured, exit 128). So an empty value is not inert for git. This supports the
  C1 predicate's treatment of an empty value as a refusal condition.
- `GIT_COMMON_DIR` set to a *mismatching* directory that has no `config`: git reports "not a
  git repository" (measured, exit 128); a mismatching directory that **does** have a config
  (the r66 W2 shape) is accepted and governs config reads — which is exactly the open route
  this round's C1 delta closes.

## 4. Absence sweep (prereg limit L3)

`absences.tsv` holds the full sweep (33 rows: scope, name searched, result, location, note).
Condensed:

- `GIT_CEILING_DIRECTORIES` / `CEILING_DIRECTORIES_ENVIRONMENT`: **0 hits** in both
  `environment.txt` and `worktree.txt`. In the tree they occur only at `environment.h:23`
  (define) and `setup.c:1574` (read). Git **never sets** it. It is read-only, so nothing in git
  exports it to subprocesses.
- `GIT_NAMESPACE` / `GIT_NAMESPACE_ENVIRONMENT`: **0 hits** in `worktree.txt`; 1 read hit in
  `environment.txt` (`environment.c:182`, `get_git_namespace()`). In the tree: `environment.h:10`
  (define), `environment.c:182` (read), `git.c:233` and `git.c:239` (the **only** `setenv`,
  from the `--namespace` option). Git sets it only on explicit request and never propagates it
  to children.
- Neither name is a member of `local_repo_env[]`, so unlike `GIT_COMMON_DIR` they are **not**
  scrubbed by git for child processes — consistent with prereg limit L3 ("neither refused nor
  pinned by this round's delta"), and the source adds the reason why pinning them is a
  different kind of problem from `GIT_COMMON_DIR`: they are not repository-local, so they
  change *which* objects/refs are seen rather than *where* the repository is.

## 5. Behavioural probe receipt

`probes.sh` (re-runnable; takes a scratch dir argument) and its output `probes.txt` are in this
directory. The script builds every fixture with `git init -q` under the scratch root and never
touches the lane tree. Measured facts it records (git 2.56.0, exit codes shown):

- A) baseline: the tracked 755→644 mode change is reported (` M f`, rc=0).
- B) with `GIT_COMMON_DIR=<copy of .git with core.fileMode=false>`: the same change is **hidden**
  (empty output, rc=0) — the r66 W2 route, reproduced.
- C) `GIT_COMMON_DIR=` (empty): git reports "not a git repository", rc=128 — an empty value is
  not inert.
- D) mismatching `GIT_COMMON_DIR` with no `config`: "not a git repository", rc=128.
- E) the injected text is what git reports as the common dir (`rev-parse --git-common-dir`
  echoes it verbatim, symlink included); `--path-format=absolute` resolves the symlink.
- F) a relative env value resolves from the **worktree top level**, not the writer cwd:
  with cwd `…/main/sub` and `-C …/main/sub`, `GIT_COMMON_DIR=../.git` resolved to `…/.git`
  (base `…/main`), not to `…/main/sub/../.git`.
- G) inside a linked worktree, the child environment carries `GIT_DIR=…/worktrees/wt` and **no**
  `GIT_COMMON_DIR`; with `GIT_COMMON_DIR` exported in the parent, the child simply inherits it
  verbatim (git neither set nor scrubbed it there).

## 6. Method notes and confidence

- Every quote in `quotes.tsv` is verbatim from the delivered capture at the recorded byte
  offset (offset = byte offset of the first byte of the quoted span inside the delivered
  file), each ≤ 25 words (word count column), with the enclosing function named.
- The L1's SOURCES row (S300) needs URL, access date, byte offset, quote and a one-line
  "teaches"; `quotes.tsv` carries all five plus the claim it grounds and the enclosing
  function.
- Confidence: **high** for the read/scrub sites (verbatim capture, byte-identical to the tag
  tarball, and corroborated by behavioral probes); **high** for the negative "git never sets
  `GIT_COMMON_DIR`" (0 hits across three spellings tree-wide, plus four older tags checked);
  **medium-high** for the relative-value base-directory statement, because it is derived from
  `setup.c` semantics plus a measured probe rather than from a single upstream sentence.
- Unresolved / out of scope for this seat: the exact `GIT_COMMON_DIR` wording in the round-67
  knowledge entry and SOURCES row (L1-owned); whether the L2 wording defect flagged in §3 is
  in scope for the round (operator/L1 call). This seat made no claim, counter or lane edit.

## 7. Tools

No tool was installed or upgraded for this seat; the host already had `git 2.56.0` and
`curl`. **No pacman transaction** (host-wide pause), no `sudo`, no service restart, no sysctl
change, no `~/.local/bin` write.
