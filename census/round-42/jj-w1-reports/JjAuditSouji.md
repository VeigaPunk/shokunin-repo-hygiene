# JjAuditSouji — git invocations in `souji-shokunin` under jj colocation

Seat `JjAuditSouji-2` · 2026-10-20 · lane `souji-shokunin` · branch `master` · static, read-only.

**Verdict.** The live souji tools do **not** commit, push, fetch, checkout, reset or rebase: zero class-A calls in production, and exactly two class-B calls (both in `souji-quarantine.sh`: `git mv` and `git rm --cached`). The three serious problems are read-side false negatives (`--branches --not --remotes`, `--not --all`, `rev-parse HEAD`) and one integration blocker: the jj helper cannot commit the deletion half of quarantine's move, so a quarantine commit can publish a tree that still contains the artifact while the working copy shows it deleted. Details, exact commands and outputs below. No live repository was written to; `jj` was executed only in `/fast/scratch/jj-wave/JjAuditSouji-2` against sandbox origins.

## 1. Scope and method

In scope and scanned:

- every `*.sh`/`*.py` under `tools/` (121 files, including the archived `cand-*`, `impl-*`, `*.impl-NN`, `*.r9-s18` variants);
- every entry in the SKILL.md gate registry: `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`, `tools/souji-census.sh`, `tools/souji-quarantine.sh`, `tools/souji-cert-evidence.py`, `tools/souji-repo-structure.sh`, `tools/souji-evidence-cache.py`, `tools/souji-preservation-evidence.py`, and `tests/fixtures/{r12-maintenance-guard.sh,r13-cert-evidence.py,r13-repo-structure.sh,r13-quarantine-bounds.sh,r14-evidence-cache.py,r14-census-boundary.py,r15-census-config.py,r15-preservation-evidence.py}`;
- the two census consumers named in SKILL.md: `census/round-13/run-verification.py`, `census/round-14/cache-demonstration.py`;
- root-level `*.sh/*.py/*.mjs/*.js/Makefile`: none exist (`scripts/` and `verifiers/` do not exist in this lane).

Not in scope: `.git`, `.jj`, corpus prose, `.ufo/waves` outputs, `tests/runner-*.sh`, `tests/judge-60.sh`, and `tests/fixtures/case-F*` (not in the gate registry). `case-F3`/`case-F5` were read-only scanned only because they contain the fleet's only class-A calls; they are flagged separately, not counted in the Tier-1 totals.

No git execution exists in `tools/souji-cert-evidence.py`, `tools/souji-evidence-cache.py`, `tools/souji-preservation-evidence.py`, `tests/fixtures/r13-cert-evidence.py`, `tests/fixtures/r14-evidence-cache.py`, or `tests/fixtures/r15-preservation-evidence.py`; their `git` strings are documentation, protected-name patterns, or fixture spy names. `souji-repo-structure.sh` executes git through its `GIT=(...)` array; those call sites are resolved in the table.

Method: a shell-aware static extractor (comments and heredocs skipped; `-C/-c/--git-dir/--work-tree` handled; `timeout`-wrapped commands included; wrapper/array/Python-helper call sites resolved by hand for Tier 1). Live tools were **not executed** against any live path. The sandbox used jj `0.45.1-7c41cdeb` and git `2.56.0`; all experiments used sandbox bare origins and confirmed `git remote -v` before any push/fetch.

Snapshot: line numbers refer to the bytes under `/fast/scratch/jj-wave/JjAuditSouji-2/snapshot` (133 in-scope files; `snapshot.sha256` combined digest `76724908b735e84fd0df412f719f3d6bb91aab3915ba7be37cfbc83366792115`), taken at live `HEAD cbf688a`. `tools/souji-census.sh` was modified in the live worktree during the audit, so its lines below are snapshot lines, not necessarily current HEAD lines.

Live state: at audit start `HEAD 58ace9f`, at completion `HEAD cbf688a` (concurrent lane writes; this seat only ran read-only git), branch `master`, 5 porcelain entries, **no `.jj`** in the live lane at audit time. The audit is therefore prospective for souji, but three other lanes already have colocated `.jj` repositories (`kama`, `mado`, `tameshi`), which souji scans live.

## 2. Counts

### Tier 1 — installed gate tooling, named fixtures, named census consumers (exact)

| class | production | fixture/selftest | total |
|---|---:|---:|---:|
| A (attached HEAD/upstream) | **0** | **0** | **0** |
| B (mutates history/index/worktree) | **2** | 93 | **95** |
| C (reads index/staging state) | **22** | 3 | **25** |
| D (read-only commit/ref/object reads) | **107** | 15 | **122** |
| **total** | **131** | **111** | **242** |

The two production B calls are `tools/souji-quarantine.sh:518` (`git mv`) and `:566` (`git rm --cached`). Every other B is inside a `--selftest` fixture or a `tests/fixtures/*` builder operating on a fresh non-colocated `mktemp` repository.

### Whole-tree direct-token inventory (includes archived copies)

Direct `git` command tokens under the 133-file pinned snapshot: **3,220** sites.

| class | count |
|---|---:|
| A | **2 direct** (plus 3 wrapper sites in §F8; not in the 3,220 token count) |
| B | **1,870** |
| C | **280** |
| D | **1,068** |

This is a token census, not an execution proof: comments/heredocs are skipped and known doc-string prose is filtered by hand, but legacy wrapper calls (`g`, `fixture_git`, `git_ro`, `GIT_*` arrays, Python helpers) are not resolved to subcommands here (about 71 wrapper lines). The Tier-1 table is the exact, resolved set. The legacy delta adds no production write path: every `fetch`/`push`/`checkout`/`clone`/`restore` found is either a fixture, a prose string, or an archived runner (`impl-05.sh`, `qrun-11.sh`, `cand-merge-selftest.sh`).

## 3. Findings (observed; commands and outputs)

### F1 — CRITICAL: `jj-lane.sh` cannot commit a deletion, so quarantine's move is published half-done

The helper filters its argument list at `scripts/hyaku/jj-lane.sh:191-199` with `[ -e "$p" ] || git ls-files --error-unmatch -- "$p"` and then commits only `"${existing[@]}"` at line 230. A moved/deleted source path is neither present in the worktree nor in the git index after `git mv`, so it is dropped with a warning and never reaches `jj commit`. Observed end-to-end in the sandbox (sandbox origin only):

```
(worktree) $ git status --porcelain
R  victim.txt -> .ufo-quarantine/2026-10-20/keep/victim.txt
$ bash jj-lane.sh commit "$SB/repo2" --as souji -m 'quarantine move' -- \\
      victim.txt .ufo-quarantine/2026-10-20/keep/victim.txt
warn: skipping missing path victim.txt
committed 703258e7c9d7a055a0091e77ff830eb2d80ffd1f
pushed 703258e7c9d7a055a0091e77ff830eb2d80ffd1f
$ git --git-dir="$SB/origin2.git" ls-tree -r --name-only master
.ufo-quarantine/2026-10-20/keep/victim.txt
victim.txt
$ git status --porcelain
 D victim.txt
```

A pure deletion is worse — the helper reports success with nothing to do:

```
$ git rm victim.txt; git status --porcelain
D  victim.txt
$ bash jj-lane.sh commit "$SB/repo2" --as souji -m 'delete victim' -- victim.txt
warn: skipping missing path victim.txt
nothing to commit (no such paths)
$ git --git-dir="$SB/origin2.git" ls-tree -r --name-only master | grep -c '^victim.txt$'
1
```

Why it matters for this lane: `souji-quarantine.sh` stages exactly this shape (`git mv <rel> <qpath>` at line 518; stage 5 deletes the staged copy and runs `git rm --cached` at 566). If the lane commits through the helper, the pushed tree keeps the artifact at the old path while the working copy says it is gone; the cited hash does not contain the deletion and `landed = committed AND pushed` is false for the change that matters. This is not a jj limitation: plain `git add -- old new && git commit -- old new` commits a deletion because `git add` records it; the helper's existence filter is the defect. (Plain git also leaves a dest-only path-limited commit split, so the caller must pass both paths; the helper additionally refuses the deletion.)

### F2 — CRITICAL: `--branches --not --remotes` is blind to unbookmarked jj commits

`jj commit` moves `@` and leaves git HEAD detached at the new commit, but does **not** move the git branch unless the helper/bookmark does. Observed after `jj commit -m 'c1 unbookmarked'`:

```
$ git symbolic-ref -q HEAD || echo DETACHED
DETACHED
$ git rev-parse HEAD
d3def146ecd9e7b0a7975c48d010e1175700781b
$ git log --branches --not --remotes --oneline
(no output)
$ git rev-list --count --branches --not --remotes
0
$ git status --porcelain -uall
(no output — the tree is clean)
$ git for-each-ref --contains HEAD --format='%(refname)'
refs/jj/keep/d3def146ecd9e7b0a7975c48d010e1175700781b
```

The commit is unpushed and invisible to the exact query used by the receipts. The receipt query returns nothing in live colocated tameshi and kama; an all-minus-branches/remotes count (`git log --oneline --all --not --branches --not --remotes`) shows branch-excluded commits: tameshi 12, kama 10, mado 16 (7/12/21 keep refs, zero tags). `mado` also has visible unpushed branch commits, so the two states coexist.

Affected production sites (all D class, all currently treated as "no unpushed work" when empty):

- `tools/souji-verify.sh:234,321` (`log --branches --not --remotes`), `:671,952` (`log HEAD --branches --not --remotes` — catches ancestors of HEAD, but not unbookmarked side commits);
- `tools/souji-vault-verify.sh:412,487,859,1140` (same);
- `tools/souji-quarantine.sh:299,931,1251` (same; 299 is the stage-4 second check);
- `tools/souji-census.sh:894,898` (`rev-list --count --branches [--not --remotes]`).

Under the helper protocol the bookmark is moved on every commit, so helper-made commits are visible while unpushed. Any manual `jj commit`, `jj new`, `jj squash`, `jj describe`/rewrite, or an unbookmarked import is invisible. Since the operator directive is to use jj as the lane VCS, that is a first-class workflow, not an abuse.

### F3 — HIGH: `--not --all` and all-ref roots treat `refs/jj/keep` as durable

`git log <head> --not --all` and `git rev-list --count <head> --not <every-ref-oid>` both subtract commits reachable from `refs/jj/keep/*`. For a detached head that no branch or remote contains, the result is zero:

```
$ git log --oneline HEAD --not --all
(no output)
$ git for-each-ref --contains HEAD --format='%(refname)'
refs/jj/keep/5c2fdab4...
refs/jj/keep/91b476b2...
```

This is the exact test used to grant `SAFE(metadata-prune)` to an absent worktree registration (`tools/souji-verify.sh:351`, `tools/souji-vault-verify.sh:517`, and their `rev-list --not "${roots[@]}"` twins at `souji-verify.sh:809-813`, `souji-vault-verify.sh:997-1001`, `souji-quarantine.sh:1069-1073`). `refs/jj/keep` is a garbage-collection grace ref, not a durable branch: once jj drops/expires it, the commit becomes unreachable and can be collected. Live exposure exists: tameshi has 2 worktrees, game-dev-2d 4, kotodama 2, and tameshi/kama/mado already hold keep refs. `_wt_record` skips only the main worktree (`tools/souji-verify.sh:439`), so any absent linked registration whose head is a keep-only commit is the vulnerable case.

### F4 — MEDIUM: jj owns the git index; staged state and `git mv` are not durable signals

Observed sequence (sandbox):

```
$ git add two.txt; git diff --cached --stat
 two.txt | 1 +
$ jj st >/dev/null; git diff --cached --stat
 two.txt | 1 +                 # snapshot did not reset the staged entry
$ jj commit -m 'c2 staged' two.txt; git diff --cached --stat
(no output)                    # mutation reset the index
$ git mv two.txt moved.txt; git status --porcelain
R  two.txt -> moved.txt
$ jj diff --summary
R {two.txt => moved.txt}       # jj saw the worktree rename
$ jj commit -m 'dest only' moved.txt
$ git ls-tree -r --name-only HEAD
base.txt moved.txt one.txt two.txt  # destination added, source deletion left in @
$ git status --porcelain
 D two.txt
```

So `git mv` succeeds and jj records the rename, but the index entry that `git mv` created is not what jj commits. `souji-quarantine.sh` uses the index both to classify tracked/untracked (`git_tracked`, `ls-files --error-unmatch`, line 216) and to stage/rm (518/566). After a jj mutation those answers change; `git rm --cached` can fail and the tool degrades to `index-cleanup-skipped` (non-fatal, but it leaves a porcelain deletion). Plain git has the same destination-only partial-commit behavior, so the jj-specific part is the index reset and the helper interaction in F1.

### F5 — MEDIUM: evidence consumers pin detached `@-` as `measured_commit`

`census/round-13/run-verification.py:384` (`revision = git("rev-parse","HEAD")`, stored at :435) and `census/round-14/cache-demonstration.py:166` (`git rev-parse --verify HEAD`, stored at :276) record HEAD as the measurement commit. In a colocated repo HEAD is `@-`, detached, and may be an unpushed/unbookmarked jj commit held only by `refs/jj/keep` (F2/F3). The record then pins a commit that is not on `master` and is not durable; a later jj gc can make the evidence unreplayable. The fixed-baseline `git show a31642d:tools/souji-quarantine.sh` at `run-verification.py:403` is safe (explicit commit, not HEAD). Positive control: the helper's identity stamping works — the sandbox pushed tip was `author=souji-shokunin <souji@shokunin.local> committer=souji-shokunin <souji@shokunin.local>`.

### F6 — LOW/INFORMATIONAL: `git status` remains a usable dirty proxy, but not a staged-state oracle

- After `jj git init --colocate`, `git status --porcelain -uall` is empty; `.jj` is hidden by `.jj/.gitignore` containing `/*` (observed), so census dirty counts are not polluted.
- After a normal jj commit/push, status is clean; after a split commit it shows the true pending ` D`/`A` entries. Dirty detection in `try_pushed`, `evaluate_repo_root`, `s18_evaluate_worktree_one` and census therefore stays conservative.
- What is no longer trustworthy is any staged/index question. Plain `ls-files` is class D per the brief but its answer now comes from a jj-managed index; `diff-index`/`read-tree`/`update-index` are class C (Tier 1 uses a private `GIT_INDEX_FILE` for the three snapshot calls, so those are isolated).
- Index-lock hygiene is incomplete: `souji-verify.sh:322,366`, `souji-vault-verify.sh:488,532`, `souji-census.sh:1000` run without `--no-optional-locks`; only some status calls carry it. jj itself ignored a synthetic `.git/index.lock` in the sandbox (`jj st` rc 0), but a concurrent git index write can still fail the git side (conservatively).

### F7 — Hook/attribute posture: none in use, and jj bypasses both if added

- `.git/hooks`: 14 `*.sample` files only; no non-sample hook. `core.hooksPath` unset in local, global and system config.
- `.gitattributes`: none tracked at HEAD, none in `.git/info/attributes`; `core.attributesFile` unset; `~/.config/git/attributes` absent. `core.autocrlf`/`core.eol` unset.
- Global config defines `filter.lfs.{clean,smudge,process,required}` (git-lfs), but no attributes select it; inert.
- Observed jj bypass: a `pre-commit` hook writing a marker did **not** run under `jj commit`; a `filter.f.clean` conversion was not applied (`jj file show` returned raw `a`, not `A`); `eol=crlf` was ignored (jj stored `78 0a 79 0a`). No current exposure, but any future byte-changing filter, eol rule or hook would be silently bypassed by the jj write path.

### F8 — Class-A inventory: none in production; five in legacy/out-of-registry files

| file:line | call | context |
|---|---|---|
| `tools/souji-census.impl-45.sh:306` | `git_ro -C "$repo" symbolic-ref -q HEAD` | `is_detached`; under jj always reports detached. Archived impl, not installed. |
| `tools/souji-verify.impl-15.sh:390` | `git -C "$repo" symbolic-ref --short HEAD \|\| printf 'master'` | fixture commit helper; would misname the branch in a colocated fixture. Archived impl. |
| `tests/fixtures/case-F3/make-fixture.sh:189` | `"${g[@]}" rev-parse --abbrev-ref HEAD` | asserts `master`; fixture self-check. |
| `tests/fixtures/case-F3/make-fixture.sh:193` | `"${g[@]}" rev-parse --verify --quiet '@{u}'` | asserts upstream; fixture self-check. |
| `tests/fixtures/case-F5/make-fixture.sh:137` | `git -C "$wt" rev-parse --abbrev-ref HEAD` | asserts `feature-f5`; fixture self-check. |

`case-F3/F5` are not in the SKILL.md registry; they are isolated non-colocated fixtures today, so these are latent only if fixture creation itself moves to jj.

Outside the lane repo, `scripts/hyaku/jj-lane.sh:56` also reads `symbolic-ref -q --short HEAD` first, but its `detect_branch` falls back to `refs/remotes/origin/HEAD`, then `master`/`main`, then the first local branch, so the detached state observed here is handled. The helper's own `print_state` uses `symbolic-ref -q HEAD` only to label attached/detached; no lane decision depends on it.

## 4. Classified table — Tier 1

Risk codes are defined below the table. `file:lines` lists every call site in the group; the command column for production rows is the exact source text (variable operands kept), truncated for width. Fixture rows are grouped by argv shape because the operands vary per case.

### 4.1 Production call sites (131 sites in 126 groups)

| file:line | command | class | risk | jj-safe replacement |
|---|---|---|---|---|
| `census/round-13/run-verification.py:384` | `git("rev-parse", "HEAD")` | D | HEADPIN | S-HEADPIN |
| `census/round-13/run-verification.py:403` | `git show BASE:tools/souji-quarantine.sh` | D | SAFE | none |
| `census/round-14/cache-demonstration.py:166` | `git -C LANE rev-parse --verify HEAD` | D | HEADPIN | S-HEADPIN |
| `census/round-14/cache-demonstration.py:202` | `git -C LANE cat-file -e <commit>:<path>` | D | SAFE | none |
| `census/round-14/cache-demonstration.py:285` | `git -C LANE show <commit>:<path>` | D | SAFE | none |
| `tools/souji-census.sh:602` | `git config --file "$cfg" --no-includes --list -z >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-census.sh:605` | `git config --file "$cfg" --no-includes --list -z 2>/dev/null)` | D | SAFE | none |
| `tools/souji-census.sh:652` | `git config --file "$cfg" --no-includes --type=bool --get "$key" 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-census.sh:884` | `git -C "$1" worktree list 2>/dev/null \| grep -c . \|\| true)` | D | WORKTREE | S-WT |
| `tools/souji-census.sh:890` | `git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null  \| grep -c . \|\| true)` | D | SAFE | none |
| `tools/souji-census.sh:894` | `git -C "$repo" rev-list --count --branches 2>/dev/null \|\| printf '0')` | D | BRANCH | S-BRANCH |
| `tools/souji-census.sh:898` | `git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null \|\| printf '0')` | D | BRANCH | S-BRANCH |
| `tools/souji-census.sh:911` | `git -C "$wt" config --get "$key" 2>/dev/null) \|\| rc=$?` | D | SAFE | none |
| `tools/souji-census.sh:950` | `git -C "$wt" config -z --get-regexp  '^filter\..*\.(clean\|smudge\|process)$' 2>/dev/null \|\| true)` | D | SAFE | none |
| `tools/souji-census.sh:965` | `git -C "$wt" -c core.attributesFile="$attrs"  ls-files -z --cached -- . ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log'  ':(exclude,glob)census/operator-sweep-*'  ':(exclude,g` | C | INDEXQ | S-INDEX |
| `tools/souji-census.sh:970` | `git -C "$wt" -c core.attributesFile="$attrs"  check-attr -z --stdin filter 2>/dev/null)` | D | SAFE | none |
| `tools/souji-census.sh:998` | `git -C "$1" --no-optional-locks -c core.fsmonitor=false  -c core.hooksPath=/dev/null -c core.excludesFile="$ex"  -c core.attributesFile="$at" status --porcelain --ignore-submodules` | C | STATUS | S-STATUS |
| `tools/souji-census.sh:1129` | `git -C "$repo" worktree list --porcelain 2>/dev/null \|\| true)` | D | WORKTREE | S-WT |
| `tools/souji-census.sh:1157` | `git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:216` | `git -C "$1" ls-files --error-unmatch -- "$2" >/dev/null 2>&1` | D | INDEXQ | S-INDEX |
| `tools/souji-quarantine.sh:220` | `git -C "$1" --no-optional-locks status --porcelain -- "$2" 2>/dev/null \|\| true` | C | STATUS | S-STATUS |
| `tools/souji-quarantine.sh:241` | `git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null) \|\| ref=""` | D | SAFE | none |
| `tools/souji-quarantine.sh:244` | `git -C "$repo" show-ref --verify --quiet "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:248,1117` | `git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null) \|\| return 1` | D | SAFE | none |
| `tools/souji-quarantine.sh:288` | `git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null \| head -1 \|\| true)` | D | SAFE | none |
| `tools/souji-quarantine.sh:294` | `git -C "$CREPO" merge-base --is-ancestor "$intro" "$current_ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:299` | `git -C "$CREPO" log --branches --not --remotes --oneline -- "$REL" 2>/dev/null \| wc -l); then` | D | BRANCH | S-BRANCH |
| `tools/souji-quarantine.sh:310` | `git -C "$CREPO" cat-file blob "$intro:$REL" 2>/dev/null \| timeout --kill-after=10 120 sha256sum \| cut -d' ' -f1 \|\| true)` | D | SAFE | none |
| `tools/souji-quarantine.sh:518` | `git -C "$crepo" mv -- "$rel" "$qpath" 2>"$ERRTMP" \|\| mv_rc=$?` | B | MV | S-MV |
| `tools/souji-quarantine.sh:566` | `git -C "$crepo" rm --cached --quiet -- "$qpath" 2>/dev/null \|\|  emit QSTAGE stage5-index "$raw" index-cleanup-skipped "$qpath"` | B | RM | S-RM |
| `tools/souji-quarantine.sh:906` | `git -C "$repo" read-tree "$ref" 2>/dev/null; then` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-quarantine.sh:909` | `git -C "$repo" update-index -q --refresh >/dev/null 2>&1` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-quarantine.sh:910` | `git -C "$repo" diff-index --quiet "$ref" -- "$path" 2>/dev/null` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-quarantine.sh:919` | `git -C "$repo" --no-optional-locks status --porcelain --untracked-files=all --ignored=matching -- "$target" 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-quarantine.sh:925` | `git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null) \|\| [ -z "$intro" ]; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:931` | `git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then` | D | BRANCH+HEAD | S-BRANCH |
| `tools/souji-quarantine.sh:937` | `git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1031` | `git -C "$repo" ls-files -- "$target" 2>/dev/null); then` | D | INDEXQ | S-INDEX |
| `tools/souji-quarantine.sh:1054` | `git -C "$owner" cat-file -e "$head^{commit}" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1059` | `git -C "$owner" rev-list --count "$branch" --not --remotes 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1069` | `git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1073` | `git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null); then` | D | ALLREFS | S-ALLREFS |
| `tools/souji-quarantine.sh:1080` | `git -C "$target" --no-optional-locks status --porcelain 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-quarantine.sh:1113` | `git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)  && git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1114` | `git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1156` | `git -C "$Q_CREPO" rev-parse --verify "$S18_PUSH_REF:$rel" 2>/dev/null) \|\| V_VERDICT=ERROR` | D | SAFE | none |
| `tools/souji-quarantine.sh:1242` | `git -C "$CREPO" rev-parse --verify "$ref:$REL" 2>/dev/null)  \|\| [ "$object" != "${S18_PUSH_OBJECT:-}" ]; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1246` | `git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null) \|\| intro=""` | D | SAFE | none |
| `tools/souji-quarantine.sh:1248` | `git -C "$CREPO" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-quarantine.sh:1251` | `git -C "$CREPO" log --format=%H HEAD --branches --not --remotes -- "$REL" 2>/dev/null) \|\| [ -n "$touching" ]; then` | D | BRANCH+HEAD | S-BRANCH |
| `tools/souji-quarantine.sh:1284` | `git -C "$repo" worktree list --porcelain 2>/dev/null \|\| true)` | D | WORKTREE | S-WT |
| `tools/souji-repo-structure.sh:105` | `git repo structure --format=lines`. Prints probe.* metadata, then the` | D | SAFE | none |
| `tools/souji-repo-structure.sh:181` | `if ! git_dir="$("${GIT[@]}" -C "$repo" rev-parse --path-format=absolute --absolute-git-dir 2>/dev/null)"; then` | D | SAFE | none |
| `tools/souji-repo-structure.sh:191` | `top="$("${GIT[@]}" -C "$repo" rev-parse --show-toplevel 2>/dev/null)" \|\| top=""` | D | SAFE | none |
| `tools/souji-repo-structure.sh:193` | `common="$("${GIT[@]}" -C "$repo" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \|\| common="$git_dir"` | D | SAFE | none |
| `tools/souji-repo-structure.sh:195` | `bare="$("${GIT[@]}" -C "$repo" rev-parse --is-bare-repository 2>/dev/null)" \|\| bare=false` | D | SAFE | none |
| `tools/souji-repo-structure.sh:203` | `"${GIT[@]}" -C "$repo" config --local --get extensions.partialClone >/dev/null 2>&1 \|\|` | D | SAFE | none |
| `tools/souji-repo-structure.sh:216` | `promisor_lines="$("${GIT[@]}" -C "$repo" config --type=bool --get-regexp '^remote\..*\.promisor$' 2>/dev/null)" \|\|` | D | SAFE | none |
| `tools/souji-repo-structure.sh:239` | `help_text="$("${GIT[@]}" -C "$repo" repo structure -h 2>&1)" \|\| true` | D | SAFE | none |
| `tools/souji-repo-structure.sh:271` | `if "${GIT[@]}" -C "$repo" repo structure --format=lines \` | D | SAFE | none |
| `tools/souji-vault-verify.sh:375` | `git -C "$d" rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ]; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:388` | `git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null \| sed 's@^origin/@@' \|\| true)` | D | SAFE | none |
| `tools/souji-vault-verify.sh:389` | `git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:392` | `git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null \| grep -v '^refs/remotes/origin/HEAD$' \|\| true)` | D | SAFE | none |
| `tools/souji-vault-verify.sh:403` | `git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null \| head -1 \|\| true)` | D | SAFE | none |
| `tools/souji-vault-verify.sh:412` | `git -C "$repo" log --branches --not --remotes --oneline -- "$target" 2>/dev/null \| wc -l)" != "0" ]; then` | D | BRANCH | S-BRANCH |
| `tools/souji-vault-verify.sh:416,865` | `git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:487` | `git -C "$target" log --branches --not --remotes --oneline 2>/dev/null \| wc -l \|\| true)` | D | BRANCH | S-BRANCH |
| `tools/souji-vault-verify.sh:488` | `git -C "$target" status --porcelain 2>/dev/null \| wc -l \|\| true)` | C | STATUS | S-STATUS |
| `tools/souji-vault-verify.sh:504` | `git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null \| wc -l); then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:517` | `git -C "$owner" log --oneline "$head" --not --all 2>/dev/null \| wc -l); then` | D | ALLREFS | S-ALLREFS |
| `tools/souji-vault-verify.sh:532` | `git -C "$target" status --porcelain 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-vault-verify.sh:639,1173` | `git -C "$repo" worktree list --porcelain 2>/dev/null \|\| true)` | D | WORKTREE | S-WT |
| `tools/souji-vault-verify.sh:833` | `git -C "$repo" read-tree "$ref" 2>/dev/null; then` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-vault-verify.sh:836` | `git -C "$repo" update-index -q --refresh >/dev/null 2>&1` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-vault-verify.sh:837` | `git -C "$repo" diff-index --quiet "$ref" -- "$path" 2>/dev/null` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-vault-verify.sh:846` | `git -C "$repo" --no-optional-locks status --porcelain --untracked-files=all --ignored=matching -- "$target" 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-vault-verify.sh:852` | `git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null) \|\| [ -z "$intro" ]; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:859` | `git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then` | D | BRANCH+HEAD | S-BRANCH |
| `tools/souji-vault-verify.sh:959` | `git -C "$repo" ls-files -- "$target" 2>/dev/null); then` | D | INDEXQ | S-INDEX |
| `tools/souji-vault-verify.sh:982` | `git -C "$owner" cat-file -e "$head^{commit}" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:987` | `git -C "$owner" rev-list --count "$branch" --not --remotes 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:997` | `git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1001` | `git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null); then` | D | ALLREFS | S-ALLREFS |
| `tools/souji-vault-verify.sh:1008` | `git -C "$target" --no-optional-locks status --porcelain 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-vault-verify.sh:1041` | `git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)  && git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1042` | `git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1045` | `git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null) \|\| return 1` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1080` | `git -C "$Q_CREPO" rev-parse --verify "$S18_PUSH_REF:$rel" 2>/dev/null) \|\| V_VERDICT=ERROR` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1131` | `git -C "$CREPO" rev-parse --verify "$ref:$REL" 2>/dev/null)  \|\| [ "$object" != "${S18_PUSH_OBJECT:-}" ]; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1135` | `git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null) \|\| intro=""` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1137` | `git -C "$CREPO" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-vault-verify.sh:1140` | `git -C "$CREPO" log --format=%H HEAD --branches --not --remotes -- "$REL" 2>/dev/null) \|\| [ -n "$touching" ]; then` | D | BRANCH+HEAD | S-BRANCH |
| `tools/souji-verify.sh:127` | `git -C "$d" rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ]; then` | D | SAFE | none |
| `tools/souji-verify.sh:141` | `git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null \| sed 's@^origin/@@' \|\| true)` | D | SAFE | none |
| `tools/souji-verify.sh:142` | `git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-verify.sh:145` | `git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null \| grep -v '^refs/remotes/origin/HEAD$' \|\| true)` | D | SAFE | none |
| `tools/souji-verify.sh:221` | `git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null \| head -1 \|\| true)` | D | SAFE | none |
| `tools/souji-verify.sh:234` | `git -C "$repo" log --branches --not --remotes --oneline -- "$target" 2>/dev/null \| wc -l)" != "0" ]; then` | D | BRANCH | S-BRANCH |
| `tools/souji-verify.sh:238,677` | `git -C "$repo" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-verify.sh:321` | `git -C "$target" log --branches --not --remotes --oneline 2>/dev/null \| wc -l \|\| true)` | D | BRANCH | S-BRANCH |
| `tools/souji-verify.sh:322` | `git -C "$target" status --porcelain 2>/dev/null \| wc -l \|\| true)` | C | STATUS | S-STATUS |
| `tools/souji-verify.sh:338` | `git -C "$owner" log --oneline "$branch" --not --remotes 2>/dev/null \| wc -l); then` | D | SAFE | none |
| `tools/souji-verify.sh:351` | `git -C "$owner" log --oneline "$head" --not --all 2>/dev/null \| wc -l); then` | D | ALLREFS | S-ALLREFS |
| `tools/souji-verify.sh:366` | `git -C "$target" status --porcelain 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-verify.sh:461,985` | `git -C "$repo" worktree list --porcelain 2>/dev/null \|\| true)` | D | WORKTREE | S-WT |
| `tools/souji-verify.sh:645` | `git -C "$repo" read-tree "$ref" 2>/dev/null; then` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-verify.sh:648` | `git -C "$repo" update-index -q --refresh >/dev/null 2>&1` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-verify.sh:649` | `git -C "$repo" diff-index --quiet "$ref" -- "$path" 2>/dev/null` | C | TEMPIDX | S-TEMPIDX |
| `tools/souji-verify.sh:658` | `git -C "$repo" --no-optional-locks status --porcelain --untracked-files=all --ignored=matching -- "$target" 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-verify.sh:664` | `git -C "$repo" log --diff-filter=A --format=%H -1 -- "$target" 2>/dev/null) \|\| [ -z "$intro" ]; then` | D | SAFE | none |
| `tools/souji-verify.sh:671` | `git -C "$repo" log --format=%H HEAD --branches --not --remotes -- "$target" 2>/dev/null); then` | D | BRANCH+HEAD | S-BRANCH |
| `tools/souji-verify.sh:771` | `git -C "$repo" ls-files -- "$target" 2>/dev/null); then` | D | INDEXQ | S-INDEX |
| `tools/souji-verify.sh:794` | `git -C "$owner" cat-file -e "$head^{commit}" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-verify.sh:799` | `git -C "$owner" rev-list --count "$branch" --not --remotes 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-verify.sh:809` | `git -C "$owner" for-each-ref --format='%(objectname)' 2>/dev/null); then` | D | SAFE | none |
| `tools/souji-verify.sh:813` | `git -C "$owner" rev-list --count "$head" --not "${roots[@]}" -- 2>/dev/null); then` | D | ALLREFS | S-ALLREFS |
| `tools/souji-verify.sh:820` | `git -C "$target" --no-optional-locks status --porcelain 2>/dev/null); then` | C | STATUS | S-STATUS |
| `tools/souji-verify.sh:853` | `git -C "$repo" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)  && git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-verify.sh:854` | `git -C "$repo" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1; then` | D | SAFE | none |
| `tools/souji-verify.sh:857` | `git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null) \|\| return 1` | D | SAFE | none |
| `tools/souji-verify.sh:892` | `git -C "$Q_CREPO" rev-parse --verify "$S18_PUSH_REF:$rel" 2>/dev/null) \|\| V_VERDICT=ERROR` | D | SAFE | none |
| `tools/souji-verify.sh:943` | `git -C "$CREPO" rev-parse --verify "$ref:$REL" 2>/dev/null)  \|\| [ "$object" != "${S18_PUSH_OBJECT:-}" ]; then` | D | SAFE | none |
| `tools/souji-verify.sh:947` | `git -C "$CREPO" log --diff-filter=A --format=%H -1 -- "$REL" 2>/dev/null) \|\| intro=""` | D | SAFE | none |
| `tools/souji-verify.sh:949` | `git -C "$CREPO" merge-base --is-ancestor "$intro" "$ref" 2>/dev/null; then` | D | SAFE | none |
| `tools/souji-verify.sh:952` | `git -C "$CREPO" log --format=%H HEAD --branches --not --remotes -- "$REL" 2>/dev/null) \|\| [ -n "$touching" ]; then` | D | BRANCH+HEAD | S-BRANCH |

### 4.2 Fixture/selftest call sites (111 sites in 46 groups)

| file:line | command shape | class | risk | jj-safe replacement |
|---|---|---|---|---|
| `tests/fixtures/r12-maintenance-guard.sh:101` | `worktree list` | D | WORKTREE | S-WT |
| `tests/fixtures/r12-maintenance-guard.sh:116` | `init` | B | FIXT | none |
| `tests/fixtures/r12-maintenance-guard.sh:118,122` | `add` | B | FIXT | none |
| `tests/fixtures/r12-maintenance-guard.sh:119,123,155,158,165` | `commit` | B | FIXT | none |
| `tests/fixtures/r12-maintenance-guard.sh:120,148` | `worktree add/lock` | B | FIXT | none |
| `tests/fixtures/r12-maintenance-guard.sh:162` | `maintenance` | B | FIXT | none |
| `tests/fixtures/r13-quarantine-bounds.sh:95` | `init` | B | FIXT | none |
| `tests/fixtures/r13-repo-structure.sh:157` | `--version` | D | SAFE | none |
| `tests/fixtures/r13-repo-structure.sh:233` | `repo structure` | D | SAFE | none |
| `tests/fixtures/r13-repo-structure.sh:286,553` | `init` | B | FIXT | none |
| `tests/fixtures/r13-repo-structure.sh:290,555` | `add` | B | FIXT | none |
| `tests/fixtures/r13-repo-structure.sh:291,556` | `commit` | B | FIXT | none |
| `tests/fixtures/r13-repo-structure.sh:292,293,294,297,566,567` | `rev-parse` | D | SAFE | none |
| `tests/fixtures/r13-repo-structure.sh:557,559,564` | `config` | D | SAFE | none |
| `tests/fixtures/r14-census-boundary.py:164,284` | `init` | B | FIXT | none |
| `tests/fixtures/r14-census-boundary.py:167` | `add` | B | FIXT | none |
| `tests/fixtures/r14-census-boundary.py:168` | `commit` | B | FIXT | none |
| `tests/fixtures/r14-census-boundary.py:169,285` | `rev-parse` | D | SAFE | none |
| `tests/fixtures/r14-census-boundary.py:170` | `update-ref` | B | FIXT | none |
| `tests/fixtures/r15-census-config.py:316` | `init` | B | FIXT | none |
| `tests/fixtures/r15-census-config.py:318,501,510,570` | `add` | B | FIXT | none |
| `tests/fixtures/r15-census-config.py:319,502,511,571` | `commit` | B | FIXT | none |
| `tests/fixtures/r15-census-config.py:320` | `rev-parse` | D | SAFE | none |
| `tests/fixtures/r15-census-config.py:321` | `update-ref` | B | FIXT | none |
| `tests/fixtures/r15-census-config.py:623` | `worktree add/lock` | B | FIXT | none |
| `tools/souji-census.sh:1455` | `add` | B | FIXT | none |
| `tools/souji-census.sh:1458,1461` | `commit-tree` | B | FIXT | none |
| `tools/souji-census.sh:1468` | `init` | B | FIXT | none |
| `tools/souji-census.sh:1469,1503` | `symbolic-ref <ref> <target> (write)` | B | FIXT | none |
| `tools/souji-census.sh:1501,1502,1511,1512,1525,1529,1551,1568,1569` | `update-ref` | B | FIXT | none |
| `tools/souji-quarantine.sh:1333` | `add` | B | FIXT | none |
| `tools/souji-quarantine.sh:1336,1338` | `commit-tree` | B | FIXT | none |
| `tools/souji-quarantine.sh:1361` | `init` | B | FIXT | none |
| `tools/souji-quarantine.sh:1362,1373` | `symbolic-ref <ref> <target> (write)` | B | FIXT | none |
| `tools/souji-quarantine.sh:1372,1374,1378,1382` | `update-ref` | B | FIXT | none |
| `tools/souji-quarantine.sh:1424,1515,1598` | `status --porcelain` | C | STATUS | S-STATUS |
| `tools/souji-vault-verify.sh:1276` | `add` | B | FIXT | none |
| `tools/souji-vault-verify.sh:1279,1281` | `commit-tree` | B | FIXT | none |
| `tools/souji-vault-verify.sh:1288` | `init` | B | FIXT | none |
| `tools/souji-vault-verify.sh:1289,1324,1351` | `symbolic-ref <ref> <target> (write)` | B | FIXT | none |
| `tools/souji-vault-verify.sh:1323,1325,1328,1333,1342,1343,1350,1354,1395` | `update-ref` | B | FIXT | none |
| `tools/souji-verify.sh:1077` | `add` | B | FIXT | none |
| `tools/souji-verify.sh:1080,1082` | `commit-tree` | B | FIXT | none |
| `tools/souji-verify.sh:1089` | `init` | B | FIXT | none |
| `tools/souji-verify.sh:1090,1119,1164` | `symbolic-ref <ref> <target> (write)` | B | FIXT | none |
| `tools/souji-verify.sh:1118,1120,1125,1136,1137,1155,1156,1163,1168,1189,1200` | `update-ref` | B | FIXT | none |

**Risk legend.** `SAFE` read-only object/ref/commit query; detached HEAD does not change the answer. `BRANCH` revision set misses jj commits not on an exported bookmark (F2). `BRANCH+HEAD` same, but HEAD ancestry is included, so current commits are caught. `ALLREFS` `--not --all` / all-ref roots count `refs/jj/keep` as durable (F3). `STATUS` reads a jj-synced index plus worktree; dirty is a coarse proxy, staged state is not stable (F6). `INDEXQ` index-based query; jj rewrites the index on mutation (F4/F6). `TEMPIDX` explicit private `GIT_INDEX_FILE`; isolated from jj. `MV`/`RM` quarantine's index mutations; jj discards the index record and the helper drops the deletion (F1/F4). `HEADPIN` pins detached `@-` as `measured_commit` (F5). `WORKTREE` main worktree reports detached after a jj mutation; the branch field is empty. `FIXT` mutates only an isolated non-colocated mktemp repo; no jj interaction.

**Replacement legend.** `S-BRANCH`: add `HEAD` to the revision set for current-work checks and add a jj query (`jj --ignore-working-copy log -r 'remote_bookmarks()..all()'`); a git-only fallback must treat keep-only commits not reachable from remotes as suspicious. `S-ALLREFS`: exclude `refs/jj/*` from durability roots and require a bookmark/remote ref before `metadata-prune`. `S-STATUS`: keep as a coarse dirty proxy; use `jj status`/`jj diff` for truth; add `--no-optional-locks` everywhere. `S-INDEX`: do not base safety on the index; use `jj file list` / `jj diff --summary`. `S-TEMPIDX`: keep; add `--no-optional-locks`. `S-MV`: pass both old and new paths to `jj commit` and fix the helper to admit deletions; verify the old path is absent from the pushed tree. `S-RM`: drop or make best-effort; `jj file untrack` if needed. `S-HEADPIN`: pin `refs/heads/<branch>` and assert it is an ancestor of `refs/remotes/origin/<branch>`; record both. `S-WT`: handle a detached main worktree; for durability use `S-ALLREFS`.

## 5. Top three risks for this lane

1. **Quarantine cannot land its deletion through the jj helper.** `git mv` + `git rm --cached` are the only production B calls in the lane, and `jj-lane.sh` drops the missing source path (observed: pushed tree contains both old and new; pure deletion reports "nothing to commit"). Until the helper admits deletions and the caller passes both paths, quarantine should keep using the git commit path, or the cited hash must be checked with `git cat-file -e <tip>:<old>` before any report cites it.
2. **Unpushed-work blindness in the pushed receipt and census.** `--branches --not --remotes` (and the `HEAD --branches` variant for side commits) misses unbookmarked jj commits; a clean tree plus zero count yields `SAFE(pushed)`/`unpushed=0` for work that exists. Live colocated lanes already hold 10-16 branch-excluded keep commits each. This is a false-SAFE on the lane's core decision.
3. **Keep refs defeat `--not --all` durability checks.** `refs/jj/keep` makes a keep-only commit look reachable, so an absent worktree registration can earn `SAFE(metadata-prune)` for a commit that no durable ref holds and that jj may later collect. This is the lane's worst-failure shape (false SAFE) and applies fleet-wide to tameshi/game-dev-2d/kotodama worktree registrations.

Residual (not top three): detached-HEAD evidence pins (F5), index-reset-driven staged-state drift (F4/F6), and the jj bypass of hooks/attributes (F7, no current exposure).

## 6. Recommendations

1. **Fix the helper before landing quarantine work under jj.** In `jj-lane.sh`, accept a path when it is HEAD-tracked even if absent in the worktree (e.g., `git cat-file -e "HEAD:$p"`), and pass both old and new paths to `jj commit`. Post-push assertion: `git cat-file -e "<tip>:<old>"` must fail and `git cat-file -e "<tip>:<new>"` must succeed. Until then, keep quarantine's commit on the git path (`git add -- <old> <new>` + `git commit -- <old> <new>`).
2. **Make unpushed detection jj-aware.** For each git-only check, add either `HEAD` or a jj query. A conservative pairing: `git rev-list --count HEAD --branches --not --remotes` **or** `jj --ignore-working-copy log -r 'remote_bookmarks()..all()' --no-graph -T 'commit_id'` non-empty ⇒ NOT-SAFE. For path scoping, use `jj log -r 'remote_bookmarks()..all()' -- <path>`.
3. **Exclude `refs/jj/*` from durability.** In `s18_evaluate_worktree_one`/`evaluate_worktree`, do not feed `for-each-ref` all-ref objectnames that include `refs/jj/keep`; either filter `refs/jj/` out or require the head to be reachable from `refs/heads` or `refs/remotes`. Treat keep-only reachability as NOT-SAFE until a bookmark/remote confirms it.
4. **Pin evidence to a durable ref.** Replace `rev-parse HEAD` in `run-verification.py`/`cache-demonstration.py` with `git rev-parse "refs/heads/$branch"` plus `git merge-base --is-ancestor <commit> "refs/remotes/origin/$branch"`; record both the commit and the branch/ref. If the helper printed a pushed hash, use it and verify it is the remote tip.
5. **Index/status hygiene.** Add `--no-optional-locks` to the remaining status calls (`souji-verify.sh:322,366`, `souji-vault-verify.sh:488,532`, `souji-census.sh:1000`). Document `git status` as a jj-approximate dirty check; never use `git diff --cached` or `git ls-files -s` as a safety signal in a colocated repo.
6. **Hooks/attributes.** No action now (none installed, no attributes, LFS filter inert). If a hook, filter or eol rule is added later, enforce it in the helper, because jj commits bypass all three (observed).

## 7. Residual risk and verification gaps

- Static counts are exact for Tier 1 as resolved; the whole-tree 3,220-token figure is an inventory, not proof that every legacy wrapper call was resolved. Legacy duplicates were not executed.
- The live repo was read-only for this seat; HEAD moved during the audit (`58ace9f` -> `cbf688a`) due to concurrent lanes, and 5 porcelain entries were present. No live tool was run against a live path, so the F1/F2/F3 behaviours are demonstrated in sandbox replicas plus read-only live ref/log inspection, not by executing `souji-verify`/`souji-quarantine` against the fleet.
- `jj` was never run with a working directory or `-R` under `/home/vgpnk/Projects/shokunin`; all jj commands ran in `/fast/scratch/jj-wave/JjAuditSouji-2`. That sandbox is preserved because it contains the cited F1 failure state (`repo2`, `origin2.git`, `jj-lane.sh` copy).
- Installations: none. No package, binary or tool was installed or upgraded during this audit.
