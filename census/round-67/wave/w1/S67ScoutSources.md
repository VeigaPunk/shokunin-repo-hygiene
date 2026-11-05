# S67ScoutSources — git source capture for round 67 C1 (GIT_COMMON_DIR)

Seat: `S67ScoutSources` (scout, wave w1, round 67). Lane: `souji-shokunin`.
Full detail: `.ufo/waves/round-67/w1/S67ScoutSources/report.md` (same directory as this file).
All artifacts live under `.ufo/waves/round-67/w1/S67ScoutSources/`. No lane file was edited,
no git/jj mutation was run in the lane tree, no claim or counter was touched.

Milestone: souji r67 — git source capture for the C1 design (post-freeze v1 wave).

## 1. Deliverables (`.ufo/waves/round-67/w1/S67ScoutSources/`)

| file | bytes | sha256 |
|---|---|---|
| `environment.txt` | 20931 | `5b52a5a123a6b340c78eb4762cfc6b3184c983a30106dfc7828efeff4127c5f3` |
| `worktree.txt` | 31092 | `da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2` |
| `environment.html` | 244227 | `534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1` |
| `setup.txt` | 83214 | `8316b1ad961ac6b1fa29dfdf1094a344aec8673f6637e6c00ba913a6668fc589` |
| `run-command.txt` | 49361 | `5cdcbaccf88f6b6c36397dfe98da9f07e392664a6db79dad63d35ab6853d78b4` |
| `git-c.txt` | 30923 | `0e1bbafb1fa791d07a91e9e714adb1274e1247ce5d7b9bde46562f0d55494432` |
| `environment-h.txt` | 8738 | `6dc06c6a9167f72103759908c961da150eb6007fd3b135e8744ac8711bdbb90f` |
| `builtin-worktree.txt` | 44631 | `af2bd523e1c89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc` |
| `doc-git.txt` | 47005 | `050c5330f1a231be22bee3db27c7ef90d8ba22bb7bd6c72c8bab462f6f0a1f79` |
| `doc-git-worktree.txt` | 22021 | `ee8a368564ace74a07e4a034e080b26fb1c3b35d17ef1fe41dcbfcc5595fe8dc` |
| `doc-gitrepository-layout.txt` | 11890 | `39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439` |
| `repository.txt` | 12445 | `7fb5a64b7592aae4de61a5c2f9affad7e58029a59311207359d6769c11112730` |
| `quotes.tsv` (25 rows) | — | see report.md §1/§3 |
| `absences.tsv` (33 rows) | — | — |
| `probes.sh`, `probes.txt` | — | behavioural probe receipt |
| `report.md` | — | full report |

Host `git --version` = **2.56.0**, so the requested tag `v2.56.0` is correct; no substitution.
All captures fetched 2026-11-05T16:37–16:41Z with `curl -sS -L`, exit 0, HTTP 200 each; every
one of the 11 captures is byte-identical to its member in the codeload v2.56.0 tarball
(sha256 `d761232b81394f7d4c3ef1a99fa804ffbe10d278ae1ad302833a0892050ca9fc`).

## 2. Findings

**F1 — design statement (i) CONFIRMED.** A caller-injected `GIT_COMMON_DIR` redirects the
common-dir resolution: `setup.c:311-320` (`get_common_dir()`) reads the variable and, if set,
uses it **instead of** the on-disk `commondir` file; `setup.c:1062-1066`
(`apply_gitdir_and_environment()`) binds it into the repository struct as `.commondir`, which
`repository.c:153-168` turns into `repo->commondir` with `different_commondir = 1`. Documented
in git(1) ENVIRONMENT VARIABLES. Reproduced on this host: with `GIT_COMMON_DIR` pointing at a
copy of `.git` whose config sets `core.fileMode=false`, the tracked 755→644 mode change is
hidden (the r66 W2 route).

**F2 — design statement (ii) NOT SUPPORTED by git v2.56.0 source.** Git never sets
`GIT_COMMON_DIR`. `setenv(GIT_COMMON_DIR`, `xsetenv(GIT_COMMON_DIR`, `putenv(GIT_COMMON_DIR`
→ **0 hits** tree-wide (excluding `t/`); the only assignment form `GIT_COMMON_DIR=` occurs only
in the test suite. `GIT_COMMON_DIR_ENVIRONMENT` has exactly 4 hits tree-wide: the define
(`environment.h:9`), the scrub-list membership (`environment.c:99`), and two reads
(`setup.c:312`, `setup.c:1066`). In the worktree context `builtin/worktree.c add_worktree()`
pushes only `GIT_DIR` and `GIT_WORK_TREE` into the child env and expresses the linked worktree's
common dir as a **`commondir` FILE** (`:543-544`); `git-worktree(1)` says the same ("These
settings are made in a `.git` file"). In the submodule context git **bypasses** the variable:
`worktree.c:553-556` calls `get_common_dir_noenv()` with the comment "The env would be set for
the superproject." Same pattern at v2.5.0, v2.20.0, v2.30.0 (no export site); v2.4.0 has no
such variable. **Consequence for the S300 SOURCES row: do not word it "git sets
GIT_COMMON_DIR for subprocesses"** — that is false against these captures. The defensible
statement, which the source supports, is the opposite one: `GIT_COMMON_DIR` is on git's own
`local_repo_env[]` scrub list and `sanitize_repo_env()` removes it from child environments, so
the candidate writer's "scrub on every git call" rule matches git's own rule for
repository-local variables.

**F3 — prereg limit L3, absence sweep complete.** `GIT_CEILING_DIRECTORIES`: 0 hits in both
captures; tree-wide only `environment.h:23` (define) and `setup.c:1574` (read) — read-only in
git, never exported. `GIT_NAMESPACE`: 0 hits in `worktree.txt`; tree-wide `environment.h:10`
(define), `environment.c:182` (read), `git.c:233`/`git.c:239` (the only `setenv`, from
`--namespace`). Neither name is in `local_repo_env[]`, so unlike `GIT_COMMON_DIR` they are not
scrubbed by git for children — they change *which* refs/objects are seen, not *where* the
repository is. Full sweep in `absences.tsv`.

**F4 — possible L2 wording defect (flagged for the L1/reviewer seats; no claim change made).**
Prereg L2 says a relative `GIT_COMMON_DIR` value "is canonicalized against the writer process's
cwd, the rule git applies". Against git v2.56.0 that rule is not the writer's cwd: git uses the
env value **verbatim** (no canonicalization at read time — `strbuf_addstr`, `xstrdup`; only the
*file* route canonicalizes, anchored at `$GIT_DIR`), and a relative env value is interpreted
relative to the **worktree top level** git chdirs into during setup (`setup.c:1225`). Measured:
cwd `…/main/sub`, `-C …/main/sub`, `GIT_COMMON_DIR=../.git` → resolved `…/.git` (base
`…/main`), not `…/main/sub/../.git`. The candidate's canonicalization base therefore differs
from git's own; whether that is in scope for the round is an operator/L1 call.

**F5 — empty value is not inert for git.** `GIT_COMMON_DIR=` (empty) is non-NULL for `getenv`,
so git takes the env branch and then reports "not a git repository" (rc=128). A mismatching
value pointing at a directory without `config` behaves the same (rc=128); a mismatching value
pointing at a directory *with* a config is accepted and governs config reads — the shape the
r66 W2 route used.

## 3. For the L1 (S300 SOURCES row)

`quotes.tsv` carries, per row: source file (delivered capture name), UTF-8 **byte offset** into
that capture, the verbatim quote (≤ 25 words, word count included), the enclosing function, the
claim it grounds, a one-line **teaches** candidate, and the upstream URL. Access date for every
capture is 2026-11-05T16:37–16:41Z (all HTTP 200, curl exit 0); sha256 and byte counts are in
`report.md` §1. Use the F2 wording: git **scrubs** `GIT_COMMON_DIR`, it never sets it; the
linked-worktree common dir is a file.

## 4. Tools

None installed or upgraded (host already had git 2.56.0 and curl). No pacman transaction, no
sudo, no service restart, no sysctl change, no write to any PATH directory. Scratch removed
before yield.
