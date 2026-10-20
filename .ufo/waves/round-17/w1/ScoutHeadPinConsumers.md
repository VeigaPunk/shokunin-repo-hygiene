STATUS: DONE — three live `rev-parse HEAD` measurement sites (r13 consumer :384, r14 demo :166 via 3 call sites, r16/r17 matrix template :81) must move to the branch tip; `tools/souji-landing-gate.py` has no production HEAD pin but silently drops frozen-pin checks when a recorded `measured_commit` no longer resolves.

# ScoutHeadPinConsumers — HEAD/`rev-parse HEAD` measurement sites

Seat `SoujiR17-3.ScoutHeadPinConsumers` · round 17 wave 1 · lane `/home/vgpnk/Projects/shokunin/souji-shokunin` (jj-colocated, branch `master`, base `5fa6017`). Static, read-only; no tool installed or upgraded.

## 1. Ground truth observed in this lane

```
$ git rev-parse HEAD refs/heads/master refs/remotes/origin/master
5fa6017ddcae9f6bd4412df44765f6360cb16294
5fa6017ddcae9f6bd4412df44765f6360cb16294
5fa6017ddcae9f6bd4412df44765f6360cb16294
$ git symbolic-ref -q HEAD || echo DETACHED
DETACHED
$ test -d .jj && cat .jj/repo/store/git_target
.jj present (colocated)
../../../.git
$ git for-each-ref --format='%(refname)' refs/jj | wc -l
8
```

So today HEAD is **detached** but numerically equal to `refs/heads/master` and `refs/remotes/origin/master`. Equality is incidental, not structural:

- jj docs, *Git compatibility* § Colocated Jujutsu/Git workspaces: "`jj` commands will usually put the Git repo in a "detached HEAD" state, since in `jj` there is not concept of a "currently tracked branch"." Same page's `jj git colocation enable` recipe: "Convince jj to update .git/HEAD to point to **the working-copy commit's parent**".
- jj docs, same page § Format mapping details: "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC."
- jj FAQ "Why does my bookmark not move to the new commit after `jj new/commit`?": "Jujutsu does not have a concept of a "current bookmark"" — bookmarks move only via `jj bookmark move`.
- Round-16 sibling observation (JjAuditSouji F2, sandbox): after `jj commit -m 'c1 unbookmarked'`, `git symbolic-ref -q HEAD` → DETACHED, `git rev-parse HEAD` → `d3def146…`, `git log --branches --not --remotes` → empty, and the commit was contained only by `refs/jj/keep/d3def146…`.

Consequence, stated as inference from the two sources above: in a colocated lane `git rev-parse HEAD` is **`@-`**, the parent of the jj working-copy commit. It can be a commit no branch or remote contains, held only by a `refs/jj/keep/*` grace ref that jj may drop. It is never the bookmark merely because the bookmark exists.

Empirical check of every commit already recorded in committed evidence (all are ancestors of `refs/heads/master` today, i.e. **no realised dangling pin yet**; all predate colocation or were made through the lane helper):

| recorded at | commit | on master |
|---|---|---|
| `census/round-13/verification.json` `measured_commit` | `6f8ee0f3…` | yes |
| `census/round-14/verification.json` `measured_commit` | `552cae42…` | yes |
| `census/round-16/c1-matrix.json` `lane_head` | `cbf688ab…` | yes |
| `census/round-16/c1-matrix-final.json` `lane_head` | `0a70beff…` | yes |
| `census/round-16/gate-landing.json` `resolved_rev` | `6ff91f53…` | yes |

## 2. Site inventory (the four assigned files)

Legend: **LIVE** = runs again and writes/feeds current-round evidence → must resolve the branch tip. **FROZEN** = committed historical artifact, leave and document. **SAFE** = no HEAD dependency.

| # | file:line | exact expression | role | class |
|---|---|---|---|---|
| 1 | `census/round-13/run-verification.py:384` | `revision = git("rev-parse", "HEAD")` | sets `CURRENT_REV` for the whole run | **LIVE** |
| 2 | `census/round-13/run-verification.py:238` | `item["measured_commit"] = CURRENT_REV` | every result row in the emitted JSON | **LIVE** (derived from #1) |
| 3 | `census/round-13/run-verification.py:435` | `record = dict(round=…, measured_commit=revision, …)` | top-level field of the new `census/round-N/<new>.json` | **LIVE** (derived from #1) |
| 4 | `census/round-13/run-verification.py:210` | prints/returns `retained["measured_commit"]` from the prior file | `--retry-failed` keeps a prior file's commit verbatim in a new JSON | **LIVE** (propagation) |
| 5 | `census/round-13/run-verification.py:403` | `git show BASE:tools/souji-quarantine.sh`, `BASE = "31984f47…"` (:39) | fixed baseline extraction | **SAFE** |
| 6 | `census/round-14/cache-demonstration.py:166` | `["git", "-C", LANE, "rev-parse", "--verify", "HEAD"]` in `git_head()` (:163) | the only revision reader in the file | **LIVE** (3 call sites) |
| 7 | `…/cache-demonstration.py:264` → `:276`/`:277` | `commit, commit_error = git_head()` → `measured_commit`, `measured_commit_error` | per-command result rows | **LIVE** |
| 8 | `…/cache-demonstration.py:410` → `:459`/`:460`, `:470`/`:471` | `commit_now, commit_error = git_head()`; raises `DemoBlocked("measured-commit-unavailable")` at :412 if None | producer evidence + result `measured_commit`/`harness_revision` | **LIVE** |
| 9 | `…/cache-demonstration.py:1107` → `:961`/`:962`, `:973`/`:974` | `initial_commit = git_head()`; top-level `measured_commit` with literal basis string `"git -C lane rev-parse --verify HEAD at demonstration start"` | run-level provenance | **LIVE** |
| 10 | `…/cache-demonstration.py:506-508, 541, 632, 668-669, 728, 739, 746, 778, 788, 825, 869-872, 952-955, 981, 1020` | derived fields/assertions over the values from #7–#9; `:952-955` emits advisory `head-changed-between-gate-invocations` | reporting only | derived |
| 11 | `census/round-16/run-matrix.py:81` | `"lane_head": git("rev-parse", "HEAD").strip()` | provenance field of the emitted matrix JSON | **LIVE template** (r17 copy) |
| 12 | `census/round-16/run-matrix.py:107` | `full = git("rev-parse", rev).strip()` | records each arm's resolved commit; `rev` from `ARMS` (:26) or `--changed` | **LIVE template**, caller-dependent |
| 13 | `census/round-16/run-matrix.py:105` | `git show <rev>:tools/souji-census.sh` | reads arm bytes; `--changed HEAD` would read `@-` | caller-dependent |
| 14 | `tools/souji-landing-gate.py:164` | `rev-parse --verify --quiet <rev>^{commit}` in `resolve_commit` | resolves the caller's required `--rev` (`:985`, required at `:994`) | **SAFE** (no default) |
| 15 | `tools/souji-landing-gate.py:687` | `_commit_all` → `g("rev-parse", "HEAD")` | synthetic `/var/tmp` selftest repos | **FROZEN** (selftest) |
| 16 | `tools/souji-landing-gate.py:766`, `:960` | `check(..., rev="HEAD")` default; `evaluate(repo, "HEAD", 16)` | selftest only | **FROZEN** (selftest) |
| 17 | `tools/souji-landing-gate.py:463-481` | `record.get("measured_commit")` → `rev-parse --verify … measured^{commit}` → `blob_at_path(root, measured, …)` | consumes a *recorded* commit from a frozen `expected.json`; read-only | **SAFE consumer**, with defect below |

Confidence: high on every line number (read from the committed bytes at `5fa6017` with `grep -n`/`read`, listed in §5).

## 3. Classification and verdict

### 3.1 `census/round-13/run-verification.py` — LIVE, must resolve the branch tip

`SKILL.md:216` names this file as the live consumer: "The actual consumer is `census/round-13/run-verification.py`; historical JSON is never rewritten. Its entry requires explicit `--round N --output census/round-N/<new>.json`". Its round directory name is historical; its invocation is current-round. Therefore #1 (and its derived #2/#3) is a **live consumer**, not frozen evidence.

Why it matters concretely: #2/#3 write the detached commit into a *new committed* evidence file, and #4 lets a prior file's commit be copied verbatim into that new file, so one jj-held commit can spread across rounds. `tools/souji-evidence-cache.py` validates `measured_commit` only as 40 lowercase hex (`:875-880`, echoed at `:1216-1217`) and **never dereferences it** (no `rev-parse`/`cat-file` in that file; dependencies are measured against the current `--root` bytes at `_evaluate_dependencies` `:929-1020`). So the pin's only consumers are humans, audits, and `souji-landing-gate.py:463-481`.

Fix (smallest, fails closed):

```python
revision = git("rev-parse", "--verify", "refs/heads/master")   # :384
```
plus, for disclosure, record the selector and the detached state in the same `record` (#3): `"measured_basis": "refs/heads/master"`, `"head_commit": <HEAD>, "head_detached": <bool>`. If `refs/heads/master` is absent, exit 2 could-not-evaluate — **do not** fall back to `HEAD`, which would silently reinstate the defect.

### 3.2 `census/round-14/cache-demonstration.py` — LIVE, same fix, lower blast radius

`SKILL.md:220` documents it as the current isolated demonstration. Its records are synthetic under `/var/tmp` (`TMP_BASE = "/var/tmp"` :83; `mkdtemp` :1121) and it writes only stdout (`emit` :1069-1071; the only two `add_argument`s are `--gate`/`--keep` at `:1076`/`:1081`). So a detached pin here corrupts *provenance wording*, not a gate decision — but the fields are literally named `measured_commit`/`harness_revision` and the whole point of the file is honest measurement.

The authors already treat HEAD as unstable: `:952-955` collects `decision["evidence"]["measured_commit"]` across three invocations and emits the advisory `head-changed-between-gate-invocations`. Under jj that advisory fires whenever a concurrent `jj` command re-snapshots the working copy mid-run.

Fix: change `git_head()` (:166) to resolve `refs/heads/master`, keep a second reader for the raw `HEAD` if the detached value is wanted, and relabel the literal basis string at `:962` (and the scope note at `:974`) to `"refs/heads/master at demonstration start"` with `worktree_head` recorded separately.

### 3.3 `census/round-16/run-matrix.py` — FROZEN file, but the LIVE template for the r17 counting command

As a round-16 artifact it is historical: its outputs `census/round-16/c1-matrix{,-final}.json` are committed and cited at `SKILL.md:239`. But `census/round-17/` does not exist yet (glob of `census/*` lists `round-1…round-16` and the operator sweeps only), and claim C1 names `census/round-17/run-matrix.py` as the counting command — i.e. this file *is* the pattern the executor will copy. `lane_head` (#11) is written into the **new committed JSON**, so the defect transfers verbatim.

Fix in the r17 copy:
- `:81` → `git("rev-parse", "--verify", "refs/heads/master")`, plus `"lane_head_basis": "refs/heads/master"` and a diagnostic `"head_detached"`/`"head_commit"` pair.
- `:107`: `--changed HEAD` currently resolves and records `@-` and `:105` reads its bytes. Map `HEAD` → `refs/heads/master` (the arm then means "the branch tip") or refuse `HEAD` with a diagnostic; keep `WORKTREE` as the only worktree-bytes arm, which is already the honest way to measure uncommitted bytes.

The `census` `unpushed` column remains branch-based per C3's disclosure; this ticket does not change it.

### 3.4 `tools/souji-landing-gate.py` — no production HEAD pin; one consumer-side coverage defect

- Production path: `--rev` is required (`:985`, `:994-997`) and `resolve_commit` (`:164`) resolves exactly the caller's selector. Nothing in the tool defaults to `HEAD`; `HEAD` appears only in selftest helpers (`:687`, `:766`, `:960`) on synthetic `/var/tmp` repos. Class: **SAFE** — but the gate cannot tell a durable from an ephemeral selector, because `emit` stores only `resolved_rev` (`:625`) and not the input string. A replay recorded with `--rev HEAD` is indistinguishable from one recorded with `--rev refs/heads/master`. Smallest fix: add `"requested_rev": rev` (and `base` likewise) to the payload; document at `SKILL.md:152` that lane runs pass `refs/heads/master` or an explicit commit.
- **Defect (consumer side, matters if any frozen record ever pins a jj commit):** `check_frozen_pins` resolves the record's `measured_commit` (`:463-474`); when it does not resolve, `measured_ok = False` (`:476`) skips the whole comparison block (`if measured_ok:` `:477`) — no `LG-FROZEN-MEASURED` finding, **and `n_checks` is not incremented** (`:478-481`). The comment at `:467-468` states the policy: "A dangling measured_commit contributes no checks". A pruned/unreachable jj commit in a frozen record therefore makes the gate silently vacuous for that whole pin set while still exiting 0. Smallest fix: when `files` is non-empty and `measured_ok` is False, append a finding (either `LG-FROZEN-MEASURED` with detail `measured_commit %s does not resolve` or a new id) and count it.
- The gate's own committed replay `census/round-16/gate-landing.json` carries `resolved_rev = 6ff91f53…` (on master) and `resolved_base = null`, `exit = 0`, so today's evidence is sound; the gap is prospective.

## 4. Adjacent site (outside the four named files, same class)

`census/round-14/run-verification.py:54` — `revision = git("rev-parse", "HEAD")`, written as `measured_commit=revision` at `:85` of the round-14 evidence record. This is the round-14 sibling copy of #1: `--round` is fixed at 14, its output (`census/round-14/verification-attempt-N.json`) is refused on overwrite (":53 Refuse overwriting exercised evidence"). Class: **FROZEN by round scope** — leave the bytes, document that it must not be re-run in a colocated lane; if a future round's verifier is cloned from it, it inherits the pin.

## 5. Commands run (read-only; nothing executed against a real repo by the tools under test)

```
grep -n 'rev-parse|HEAD|measured_commit|CURRENT_REV' census/round-13/run-verification.py
grep -n 'rev-parse|HEAD|measured_commit|git_head'     census/round-14/cache-demonstration.py
grep -n 'rev-parse|HEAD|measured|commit|rev'          census/round-16/run-matrix.py
grep -n 'rev-parse|HEAD|measured'                     tools/souji-landing-gate.py
grep -n 'measured_commit|rev-parse|cat-file'          tools/souji-evidence-cache.py
git ls-files census | awk -F/ '{print $1"/"$2}' | sort -u
git ls-files census/round-14 ; git ls-files census/round-16
python3 - <<'EOF'   # read committed JSON fields (lane_head / measured_commit / resolved_rev)
git rev-parse HEAD refs/heads/master refs/remotes/origin/master
git symbolic-ref -q HEAD || echo DETACHED
test -d .jj ; cat .jj/repo/store/git_target
git for-each-ref --format='%(refname)' refs/jj | wc -l
for c in 6f8ee0f3… 552cae42… 0a70beff… cbf688ab… 5fa6017d…; do git cat-file -t $c;
  git merge-base --is-ancestor $c refs/heads/master && echo on-master; done
```

Representative outputs are quoted in §1; every ancestry test returned `on-master`, `git cat-file -t` returned `commit` for all five, and `grep -n '"HEAD"' census/round-13/run-verification.py` returned exactly one line (`384:`). No `jj` subcommand, no git write, and no gate tool was executed. Web reads: `docs.jj-vcs.dev/latest/git-compatibility/`, `docs.jj-vcs.dev/latest/faq/`.

## 6. Verdict and remaining unknowns

- **Holds** for the static premise: the lane is colocated, HEAD is detached, and three files in scope record `rev-parse HEAD` as a measured revision; the r16 matrix is the live template for the r17 counting command.
- **Fails (partial)** for the required semantics: no in-scope live site resolves the branch tip. Fix list is §3.1, §3.2, §3.3 (`:81`, `:105`/`:107`), plus the landing-gate silent-skip and `requested_rev` gaps (§3.4).
- **Fails closed, so no false green is created by the pin itself**: `measured_commit` is provenance-only for `souji-evidence-cache.py` (never dereferenced), and the landing gate's use of it can only *drop* checks, never pass a wrong digest.
- Unresolved: whether a concurrent `jj` snapshot can change `@-` (and therefore `HEAD`) *during* a single r13/r14 run in this lane — I did not run `jj`, so this rests on the documented "every `jj` command updates the working-copy revision" plus JjAuditSouji's sandbox observation, not on a live trace. Also unmeasured: whether `refs/heads/master` is guaranteed present in every scanned repo (the fix needs an explicit absent-ref policy, not a fallback).
