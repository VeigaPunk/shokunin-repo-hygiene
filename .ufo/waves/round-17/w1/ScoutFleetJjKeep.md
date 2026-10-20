STATUS: DONE — C3 live exposure is zero today but the F3 false-SAFE is armed in all 7 jj lanes and un-fixed at 4 code sites; C3(b)/(d) not landed, C3(c)/(e) hold.

# ScoutFleetJjKeep — jj keep-ref live exposure across the fleet

Scope: C3(a)(b)(d)(e) live exposure, read-only. No tool in `tools/` was executed. All
git invocations are `for-each-ref|rev-list|log|rev-parse|merge-base|worktree list|cat-file`
against named repos. Nothing written outside this report.

Measurement basis (working tree, concurrent executor edits in flight):
- `tools/souji-verify.sh` sha256 `16b42a6d0e89ec04e9c09ee3fa421893d6f7982cdc4bc06c10314784afdd9ded`
- `tools/souji-vault-verify.sh` sha256 `be3f60bba7dc2aac70e5c2434e5b9de0ccc6743abaef2f305732e4f0a2bf40ee`
- `tools/souji-quarantine.sh` sha256 `df4075112c36bae804b98766c4eb66b0e5b2b80b76d7333475ede27b06b168c4`
- `SKILL.md` `9dcdb2d5…`, `PROVINCE.md` `835b42f9…` (both cited below)
- verify.sh line numbers shifted ~+44 lines between two reads in this session (an executor is
  editing it live); citations below were re-grepped against the digest above.

## 1. Fleet jj/worktree exposure table

`test -d .jj` over the fleet root and all 22 `*-shokunin`: **7 colocated** (kaidoku, kama,
mado, souji, tabi, tameshi, tsukuroi); 15 plain + fleet root plain.

```
repo       .jj refs_jj keep_only  worktree registrations                         head          head_excluded  head_has_keep_ref
kaidoku    yes  27*     14*      1, detached                                    b2aad08ceeee   0              yes
kama       yes  22      10       1, detached                                    54a29268e208   0              yes
mado       yes  39      23       1, detached                                    a210241b5429   0              yes
souji      yes   8       6       1, detached                                    5fa6017ddcae   0              yes
tabi       yes   7       5       1, detached                                    5859243183c4   0              yes
tameshi    yes  27      13       1, detached                                    eb7838b16490   0              yes
tsukuroi   yes  11       2       1, branch refs/heads/master                     6923fe0bd3ad   0              yes
game-dev-2d  no  –       –       3 absent, on refs/heads/wt-r100/r98/r99          (per-reg)      –              n/a
kotodama     no  –       –       1 absent+prunable, DETACHED 4a7aede22cd8        –              –              n/a
```

Collation formula (all read-only):
`for-each-ref --count=100000 refs/jj | wc -l`;
`rev-list --count --glob='refs/jj/keep/*' --not --branches --remotes --tags`;
`worktree list --porcelain`; `rev-list --count <head> --not --branches --tags --remotes`.

`*` kaidoku moved **during this scout**: refs/jj 22→27, keep-only 10→14, HEAD
`eb6c2668e5cb`→`b2aad08ceeee` in ~15 minutes. That churn is itself the finding: `refs/jj/keep/*`
is a GC-grace namespace rewritten continuously by a live lane, so it cannot be a durability root.

Only `refs/jj/keep/*` exists in these repos — 0 `refs/jj/bookmarks`, 0 `refs/stash` in all 7
(`for-each-ref refs/jj` groups to `refs/jj/keep`; `for-each-ref refs/stash` = 0 each).

Ref denominators: every jj repo has exactly **1** `refs/heads` and **0** `refs/tags`;
`refs/remotes` 2–12. So "durable" is a single branch per lane — the narrowest possible base.

### F3 firing status: not firing today, armed structurally

No registration in the fleet has an absent directory *and* a keep-only head:

- 7 jj lanes: registration is the lane itself, dir present, head excluded-vs-durable = **0**
  (branch-backed).
- game-dev-2d: 3 absent registrations, heads on `refs/heads/wt-r*` → durable by `refs/heads`
  (and each is `--not --remotes` = 1, i.e. correctly refused as `unpushed-branch` by the
  earlier branch test, not by `metadata-prune`).
- kotodama `ca02-wt-r34`: absent (`prunable gitdir file points to non-existent location`),
  detached head `4a7aede22cd8` — but `for-each-ref --contains` shows it on
  `refs/heads/main`, `refs/remotes/origin/main`; `rev-list --count … --not --branches --tags
  --remotes` = 0. Durable; not an F3 case.

**But the mechanism is guaranteed, not probabilistic, for every jj lane.** In all 7 lanes the
current HEAD commit has its own `refs/jj/keep/<oid>` ref (jj names keep refs by commit id).
The unfiltered roots expression therefore *always* contains `$head`, so
`rev-list --count "$head" --not <all-refs>` returns 0 for any jj lane — `SAFE(metadata-prune)`
is structural the moment the directory goes absent, independent of branch backing.

## 2. The misjudgment, demonstrated on real commits (no sandbox, no writes)

For existing `refs/jj/keep/<oid>` refs, comparing the honest test with the code's expression:

```
repo      keep oid      rev-list --not --branches --tags --remotes   log --not --all
kaidoku   13b6a5c60754  1                                           0
kama      096831e5ac7d  1                                           0
mado      08a277c88091  1                                           0
souji     025466142775  1                                           0
souji     1e0d8d1644cf  1                                           0
tabi      05bb63c9dfea  1                                           0
tameshi   172e82d4f2c1  1                                           0
tsukuroi  31d2da855e1d  1                                           0
```

8 of 8 probed commits are **not** durable from heads/tags/remotes, and every one of them is
reported as `0` by `log --oneline <c> --not --all` — the exact expression that grants
`SAFE(metadata-prune)`. Fleet total keep-only commits = **73** (14+10+23+6+5+13+2).

Second, independent hole in the same expression: `--not --all` roots at `refs/*` plus the
**owner's** `HEAD` only (git-rev-list: "all the refs in `refs/`, along with `HEAD`"). A linked
worktree's detached HEAD is not a ref, so `--not --all` cannot distinguish a prunable
registration's head from garbage. kotodama's `4a7aede22cd8` is only *accidentally* safe because
`main` still holds it; had that commit been dropped from `main`, the same expression would still
print `0`.

## 3. C3(a) durable roots — FAILS (partially landed, 4 sites open)

Claim: verify :351/:809-813, vault :517/:997-1001, quarantine :1069-1073 use only
`refs/heads|tags|remotes`. Actual, at the digests above:

| site | current content | verdict |
|---|---|---|
| verify:384 | `log --oneline "$head" --not --all` | **open** — header :61-68 claims fixed |
| verify:842-850 | `for-each-ref --format='%(objectname)'` (no prefix) + evidence `durable-refs-only=yes` | **open** |
| vault:554 | `log --oneline "$head" --not --branches --tags --remotes` | fixed |
| vault:1034-1042 | `for-each-ref --format='%(objectname)'` (no prefix) + `durable-refs-only=yes` | **open** |
| quarantine:1069-1077 | `for-each-ref --format='%(objectname)'` (no prefix) + `durable-refs-only=yes` | **open** |

`for-each-ref` with no pattern lists every ref under `refs/`, `refs/jj/keep` included, so the
`roots` array at those three sites contains the very refs the claim excludes. The evidence
string `durable-refs-only=yes` is an assertion the code does not satisfy — it should be
derived from the ref set, not hardcoded.

`grep -c jj tools/souji-quarantine.sh` = **0**: quarantine has no jj awareness at all.

## 4. C3(b) unpushed-touching with keep heads — FAILS (2 of 11 sites wired)

| tool | sites | wired |
|---|---|---|
| verify | :267, :704, :985 (+ root :354) | **0 of 4** |
| vault | :443/:445, :520/:530 | 2 wired (`--branches --glob='refs/jj/keep/*'` + `jj_keep_unpushed`) |
| vault | :896, :1177 | **open**, still `HEAD --branches --not --remotes` |
| quarantine | :299, :931, :1251 | **0 of 3**, no helper, no `refs/jj` string |

verify defines both helpers and references them nowhere:

```
tools/souji-verify.sh:236:jj_keep_touching() { ...
tools/souji-verify.sh:246:jj_repo_keep_unpushed() { ...
grep -n 'jj_keep_touching\|jj_repo_keep_unpushed'  → only those two definition lines
```

Dead code: the fix exists as unreachable shell functions while the four live checks stay
branch-only. This is the worst shape for review — the header comment at :61-68 describes the
intended behaviour and reads as landed.

## 5. C3(c) knowledge entry — HOLDS

`corpus/knowledge/jj-colocation-receipts.md`, 16253 bytes, 11 sections + operating rules +
limits + failure cases. Sourced rows carry URL + `sourced` marker, e.g. :27 (jj keeps
`refs/jj/` to prevent GC), :28 (visible-heads wording; explicitly records that keep-ref
persistence is undocumented), :30 (`--all` = `refs/` + `HEAD`, git-rev-list), :32 (durable roots
= heads/tags/remotes, with the consequence sentence). :5 carries a recheck command
(`jj --version` + docs grep + `mktemp -d /var/tmp` rebuild, never a live path). §7 nested `.git`
phantom deletions matches the fixture behaviour verified in §6 below.

## 6. C3(e) phantom-deletion stub — HOLDS, wording needs one correction

`tests/vault/vadv54-run/p/p6repo` contains exactly two tracked files — `one.txt`,
`inner/keep.txt` — matching "phantom deletions of two tracked files".

The claim cites the stub as a path: `…/p6repo/.git`. **That path does not exist now**, by
design: `tests/vault/vadv54-harness.sh:277` creates it (`mkdir -- "$P/p6repo/.git"`),
:279 installs `trap 'rmdir …' EXIT`, :281 rmdir's it after the case. It is a transient artefact
removed per run, not a committed stub. The claim's noun phrase ("the empty untracked fixture
stub <path>") reads as persistent state and invites a reviewer to `stat` a missing path.
Correct to: "created at vadv54-harness.sh:277 and removed at :281; a leftover stub under
`tests/vault/vadv54-run` is the jj hazard (:273-276)".

## 7. C3(d) SKILL.md / PROVINCE.md jj recipes — FAILS

```
grep -n 'jj' SKILL.md      → 0 hits   (sha256 9dcdb2d5…)
grep -n 'jj' PROVINCE.md   → 0 hits   (sha256 835b42f9…)
```

None of the named recipes (helper-only commits naming both paths, detached HEAD, no `@{u}`)
are in either file. The both-paths rule exists only in the knowledge entry (§8) and in
`JjAuditSouji.md`; the operator-facing recipe surface is untouched. `Skill`-side disclosure of
the phantom-deletion hazard is likewise absent from `tools/` headers (quarantine: 0 jj hits).

## 8. Drift against the cited audit

`JjAuditSouji.md:130` states live exposure "tameshi has 2 worktrees, game-dev-2d 4, kotodama 2".
Measured now: tameshi **1**, game-dev-2d **3** (+ main = 4 total entries, the audit's number
counts total), kotodama **1**. Registrations were pruned since the audit, so its live-exposure
sentence under-reports nothing but mis-describes the shape; the mechanism sentence stays correct.

## 9. Smallest fix (one helper, five call sites)

1. Add to each tool: `durable_roots() { git -C "$1" for-each-ref --format='%(objectname)' refs/heads refs/tags refs/remotes; }`
   and use it at verify:842, vault:1034, quarantine:1069. Deleting the `durable-refs-only=yes`
   literal, or deriving it from an empty-diff assertion on the ref set.
2. verify:384 → the vault:554 form (`--not --branches --tags --remotes`).
3. Wire the two dead helpers: verify :267/:704/:985 take `jj_keep_touching`/`jj_repo_keep_unpushed`;
   vault :896/:1177 get the `--glob='refs/jj/keep/*'` head term.
4. quarantine: import `jj_has_keep`/`jj_keep_unpushed` and apply at :299/:931/:1251, then the
   three (a) sites; the header note from vault :42-50 gives the wording.
5. Keep the census `unpushed` column branch-based, but the C3(e)/§3 disclosure must say the
   73 fleet-wide keep-only commits (6 in souji) are invisible to it.

## 10. Remaining unknowns

- Whether any jj lane writes `refs/jj/bookmarks` under load: 0 observed across 7 repos, but
  kaidoku's ref set changed mid-scout, so a single sample cannot prove absence.
- `refs/jj/keep/*` expiry policy is undocumented in the pages read (knowledge :28 records
  this); the "GC may collect it" claim rests on the docs' purpose statement, not a measured
  collection.
- Whether `git worktree list --porcelain` omits registrations whose `.git` file is missing
  entirely (kotodama's is listed as `prunable`, so it is visible), i.e. no hidden class found.

No tools installed; no channel used. No jj command was run.
