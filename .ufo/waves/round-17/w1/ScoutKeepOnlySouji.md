STATUS: DONE — 6 keep-only commits, 4 carry phantom p6repo deletions, 0 have a patch-id twin on master; 5 share one jj change-id with master tip.

# ScoutKeepOnlySouji — commits held only by `refs/jj/keep/*`

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (jj-colocated, detached HEAD, `master` tip
`5fa6017ddcae9f6bd4412df44765f6360cb16294`). Read-only git only; no `jj` run; no writes outside this report.

## 1. Exact enumeration (observed)

Command:

```
git rev-list --glob='refs/jj/*' --not --branches --remotes --tags
```

Output (6 commits, in this order):

```
0254661427750f47e04f20864c5091cfc74e2e0e
1e0d8d1644cf18a0e02189bc27b33a5a6b55474c
719154dc9d15ea25a0204ba12c35493526d6c1ed
41ab059d7dd5c3465bb84d7049a87756cdc19926
dcc1512e2a4f4db48de025081485223ac8ee8246
dd2e3226864c182165c8c725b1d0ff3fbc3a37e1
```

Supporting counts (`git rev-list <spec> --count`):

| spec | count |
|---|---|
| `--all` | 58 |
| `master` | 52 |
| `--no-merges master` | 52 (no merge commits on master) |
| `--branches --remotes --tags` | 52 |
| `--glob=refs/jj/*` | 58 |
| `--glob=refs/jj/* --not --branches --remotes --tags` | 6 |

`refs/jj` holds exactly 8 refs, all loose under `.git/refs/jj/keep/<sha>` (no `packed-refs` entry).
Two of the 8 point at commits already reachable from `master` — `refs/jj/keep/5fa6017…` (tip) and
`refs/jj/keep/c46eabf…` (`master~1`) — so keep refs pin landed commits *and* hidden ones. Loose-ref
creation times (`.git/refs/jj/keep/*` mtime) preserve the rewrite order:

```
12:29:49.916 dcc1512…  12:29:49.919 c46eabf…  12:29:49.925 dd2e322…  12:29:50.030 41ab059…
12:42:34.302 1e0d8d1…  12:42:34.315 719154d…  12:42:34.331 5fa6017…  12:42:34.332 0254661…
```

## 2. Per-commit dossier (observed)

All six have an **empty commit message**. All carry a jj `change-id` header (raw commit object), absent
from the git-authored master commits.

| # | commit | parent | tree | author @ | committer @ | change-id | diff vs parent |
|---|---|---|---|---|---|---|---|
| 1 | `0254661` | `5fa6017` (master tip) | `8506f32` | protocol-shokunin 12:42:34 | protocol-shokunin 12:42:34 | `mnokvtruxqvtopytvnnwzowwspvnvwvm` | `D` both p6repo files |
| 2 | `1e0d8d1` | `c46eabf` (master~1) | `8506f32` | Joao Pedro Veiga 12:29:50 | souji-shokunin 12:42:34 | `yurlroyqvvttpsvlvokzpwtxyullxoxy` | `A` lesson (149) + `D` both p6repo files |
| 3 | `719154d` | `c46eabf` | `8506f32` | protocol-shokunin 12:29:50 | protocol-shokunin 12:42:34 | `yurlroyqvvttpsvlvokzpwtxyullxoxy` | identical patch to #2 |
| 4 | `41ab059` | `c46eabf` | `50fb432` | Joao Pedro Veiga 12:29:50 | Joao Pedro Veiga 12:29:50 | `yurlroyqvvttpsvlvokzpwtxyullxoxy` | `D` both p6repo files |
| 5 | `dcc1512` | *none (root)* | `4b825dc` (**empty tree**) | Joao Pedro Veiga 12:29:49 | Joao Pedro Veiga 12:29:49 | `opnrkwuyqryqsqnknkuvxnmtptnkprvz` | — |
| 6 | `dd2e322` | `c46eabf` | `80a2fbd` (= `c46eabf` tree) | Joao Pedro Veiga 12:29:49 | Joao Pedro Veiga 12:29:49 | `yurlroyqvvttpsvlvokzpwtxyullxoxy` | **empty commit** |

Raw stats (`git show --stat`):

- `0254661`: `tests/vault/vadv54-run/p/p6repo/inner/keep.txt | 1 -`, `…/one.txt | 1 -` — 2 deletions.
- `1e0d8d1`: `corpus/lessons/round-16-verifier-spotcheck.md | 149 +`, `…/inner/keep.txt | 1 -`, `…/one.txt | 1 -`.
- `719154d`: same three paths/counts as `1e0d8d1`.
- `41ab059`: the same two deletions only.
- `dcc1512`, `dd2e322`: no stat rows at all (tree-identical to parent / empty root).

## 3. Phantom-deletion verdict (observed + causal gap)

**4 of 6 delete `tests/vault/vadv54-run/p/p6repo/*`** (#1–#4) — matching the lane's "4 with phantom
deletions" figure. They are *phantom* on the following measured evidence:

- Both files exist in the worktree and in the index; worktree, index and `HEAD` are the same blobs:
  `one.txt` = `00508d39f3a7811030b79d1a3683616396b89081`, `inner/keep.txt` =
  `5fd8799df92613b474f6c2f027feff41728b5cbb` from `48a64d8` (2026-10-18, the only commit that ever
  touched the path) through `HEAD` and `git hash-object` of the worktree files.
- `git diff --stat HEAD -- tests/vault/vadv54-run/p/p6repo` → empty (exit 0).
- `git log --diff-filter=D master -- tests/vault/vadv54-run/p/p6repo` → empty: **no master commit ever
  deletes these files**, so no landed state corresponds to the deletion.
- `git ls-tree -r <commit> tests/vault/vadv54-run/p/p6repo` is empty for all four (#1–#4); it lists
  both files for `dd2e322`, consistent with it being a no-change snapshot.

Mechanism (source, not re-observed here): `JjTrialSouji.md:76` records that an empty untracked
`p6repo/.git/` makes jj treat `p6repo/` as a nested repo and report `D` for files present on disk, and
that a directory pathspec commits those deletions. **The stub is gone today** —
`stat tests/vault/vadv54-run/p/p6repo/.git` → `No such file or directory` — so the keep refs are the
only surviving artifact of that state; the worktree cannot reproduce it.

`dd2e322` and `dcc1512` are content-free: `dd2e322`'s tree hash equals its parent's (`80a2fbd`), and
`dcc1512` is the **only empty-tree commit** in the 58-commit `--all` graph (no master commit has the
empty tree; master's root is `ccbb132`). `dcc1512` is not an ancestor of `master` or of `dd2e322`.

## 4. Closest master commit with the same patch (observed: none)

Patch-ids via `git show <c> | git patch-id --stable`, compared against the stable patch-id map of all
52 master commits (`git log -p --no-merges master | git patch-id --stable`; `--no-merges` is lossless
because master has 52 total commits):

| commit(s) | stable patch-id | master commit with same patch-id |
|---|---|---|
| `0254661`, `41ab059` | `9ad6fe90f47738d6f3108b016b4944ea965d4db1` | **none** |
| `1e0d8d1`, `719154d` | `a726362b2db68377abead3d9e610871fbb760e70` | **none** |
| `dcc1512`, `dd2e322` | (empty patch) | n/a |

So the answer to "the closest master commit with the same patch" is: **there is no exact twin on
master for either patch**. Nearest master commits by identity/content:

- **`719154d` / `1e0d8d1` → `5fa6017` (master tip).** All three share jj change-id
  `yurlroyqvvttpsvlvokzpwtxyullxoxy`, and the landed lesson blob is byte-identical:
  `5fa6017:corpus/lessons/round-16-verifier-spotcheck.md` = `719154d:…` = `1e0d8d1:…` =
  `b17bfbc5d125abf73b31aa122e852587929a3eab`. `git diff --stat 719154d 5fa6017` and
  `git diff --stat 0254661 5fa6017` are each exactly the 2-line restoration of the two fixture files.
  `5fa6017`'s own patch-id is `0d50379a383e4ba1b7d948d87bc742352419c1be` — a **pure 149-line add**
  (its stat: `round-16-verifier-spotcheck.md | 149 +`), i.e. the landed rewrite **dropped the phantom
  deletions**. `719154d` also shares `5fa6017`'s author identity (`protocol-shokunin`), while
  `1e0d8d1` is the same tree+patch under author `Joao Pedro Veiga` with committer `souji-shokunin`.
- **`41ab059` → `c46eabf`** (its parent; `git diff --stat 41ab059 c46eabf` = the same 2-line
  restoration; `41ab059` tree = `c46eabf` tree minus the two files).
- **`0254661` → `5fa6017`** (its parent; same 2-line relation).
- **`dd2e322` → `c46eabf`** (identical tree).
- **`dcc1512` → no master analogue** (empty tree, separate root history).

## 5. Falsifiers for the C3(a) claim (observed)

Every keep-only commit is invisible to the branch/remote/tag root set and visible to `--all` only
because of its keep ref:

| commit | `rev-list <c> --not --all --count` | `<c> --not --branches --remotes --tags --count` |
|---|---|---|
| all six (`0254661`, `1e0d8d1`, `719154d`, `41ab059`, `dcc1512`, `dd2e322`) | **0** | **1** |

`git rev-list --all --not --branches --remotes --tags --count` = **6**. This is the concrete shape C3(a)
requires: an absent worktree head whose only holder is `refs/jj/keep` scores 0 under `--not --all` and is
therefore candidate-`SAFE(metadata-prune)` under the current roots, while the branch-based query still
sees it.

Nuance for this lane's *present* state: `HEAD` is **detached at `5fa6017`** (master tip); `git rev-list
HEAD --not --branches --remotes --tags --count` = **0**. The lane's live head is not keep-only, so the
false-SAFE is demonstrated by the six historical commits, not by today's HEAD.

## 6. Facts vs inference

**Observed:** everything in §1–§5 (hashes, trees, parents, identities, timestamps, change-id headers,
patch-ids, blob ids, ref files, absence of the `.git` stub).

**Inference [INFERENCE]:** `0254661` is jj's current working-copy commit `@`: it is the newest keep ref
(12:42:34.332, immediately after the landed `5fa6017`), has a fresh change-id, an empty message, parent
= master tip, and a tree equal to master tip minus exactly the two phantom-deleted files. Confirming
this needs the jj op log / `jj log`, which is forbidden here.

**Inference [INFERENCE]:** the chain `dd2e322` (empty) → `41ab059` (deletion-only) → `1e0d8d1`/`719154d`
(lesson + deletion, two author identities) → `5fa6017` (lesson only, landed) is one jj change rewritten
four times; the shared change-id and the ref mtimes support it, but the intermediate *operations* are
not recorded in git.

## 7. Residual unknowns

1. Whether `0254661` is literally `@` now (needs `jj`; forbidden).
2. Why the same change briefly existed under two authors (`Joao Pedro Veiga` in `1e0d8d1`/`41ab059`,
   `protocol-shokunin` in `719154d`/`5fa6017`); git alone cannot say which rewrite was the reconcile step.
3. Origin of the empty root `dcc1512` (change-id `opnrk…`): consistent with a jj init-time working-copy
   commit later detached from history, but unverified.
4. The `p6repo/.git` stub's lifetime: it is absent now (`stat` ENOENT), so no timestamped evidence ties
   it to the 12:29–12:42 snapshots; only `JjTrialSouji.md:76` observed it.

## Commands run (exact)

```
git rev-parse --git-dir
git for-each-ref --format='%(refname) %(objectname)' 'refs/jj'
git rev-list --glob='refs/jj/*' --not --branches --remotes --tags
git rev-list --glob='refs/jj/*' --not --branches --remotes --tags --count
git rev-list --all --count ; git rev-list master --count ; git rev-list --no-merges master --count
git rev-list --branches --remotes --tags --count ; git rev-list --glob=refs/jj/* --count
git show --stat --format='%H%n%an <%ae>%n%ad%n%s%n%b' <each of the 6>
git rev-list --parents -n1 <each> ; git rev-parse <c>^{tree}
git diff-tree --no-commit-id --name-status -r -m --first-parent <each>
git show --no-color <each> | git patch-id --stable
git log --no-color -p --no-merges master | git patch-id --stable
git log --oneline --diff-filter=D --name-only master -- tests/vault/vadv54-run/p/p6repo
git log --oneline --name-status master -- tests/vault/vadv54-run/p/p6repo
git diff --stat 719154d 5fa6017 ; git diff --stat 0254661 5fa6017 ; git diff --stat 41ab059 c46eabf
git rev-parse <c>:corpus/lessons/round-16-verifier-spotcheck.md   (5fa6017/719154d/1e0d8d1 → b17bfbc…)
git ls-files -s tests/vault/vadv54-run/p/p6repo
git hash-object tests/vault/vadv54-run/p/p6repo/one.txt …/inner/keep.txt
git diff --stat HEAD -- tests/vault/vadv54-run/p/p6repo      (empty, rc=0)
git ls-tree -r --name-only <each> tests/vault/vadv54-run/p/p6repo
git cat-file -p <each>                                        (change-id headers)
git rev-list <each> --not --all --count ; git rev-list <each> --not --branches --remotes --tags --count
git rev-parse HEAD ; git symbolic-ref -q HEAD ; git log -1 --format=… HEAD
git rev-list HEAD --not --branches --remotes --tags --count
git rev-list --max-parents=0 master ; git show --stat 48a64d8
stat -c '%y %n' .git/refs/jj/keep/* ; stat tests/vault/vadv54-run/p/p6repo/.git
grep -n -i -E 'keep|phantom|p6repo|predecessor|hidden' .ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md
grep -n -i -E 'keep|phantom|p6repo|predecessor|hidden' .ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md
```

Tool installs: none (no install or upgrade was needed).
`/tmp/r17-keeponly-master-patchids.txt` is scratch outside the lane and can be discarded.
