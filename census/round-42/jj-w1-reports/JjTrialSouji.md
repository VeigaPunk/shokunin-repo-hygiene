# JjTrialSouji — jj colocation trial for lane `souji`

Seat: JjTrialSouji-2 · Live repo: `/home/vgpnk/Projects/shokunin/souji-shokunin` (branch `master`, remote github.com/VeigaPunk/shokunin-repo-hygiene) · Sandbox: `/fast/scratch/jj-wave/JjTrialSouji/` · jj 0.45.1 (`~/.local/bin/jj`)

Live lane was never mutated; only read commands + one `cp`/`rsync` outbound copy. All pushes went to sandbox `remote.git`.

## Step 1 — sandbox build

Commands: `git clone --bare <live> remote.git` → `git clone remote.git lane` → `rsync -a --exclude=.git --exclude=.jj <live>/ lane/`.

- `git -C lane status --porcelain | wc -l` → **1** (`?? census/operator-sweep-20261019/`) — identical to live.
- 10 largest untracked (all under `census/operator-sweep-20261019/`, all < 1 MiB): `.staged.json` 792338 B, `tmp-removed.tsv` 768949, `classification-final.json` 408460, `quarantine-mtimes-t0.tsv` 374619, `.classify2.json` 367822, `.classify.json` 367589, `tmp-before.txt` 344312, `fresh-120min.txt` 186904, `kotodama-children-sizes.tsv` 60785, `kotodama-children.txt` 44076.
- Largest **ignored**: `tests/vault/vadv-49/fixture/*/` dirs ≈ 27 KB each (ignored by `tests/vault/vadv-49/.gitignore` line 1 `fixture/`).
- **Deviation noted**: the prescribed rsync `--exclude=.git` also drops nested fixture `.git` dirs. The live tree has **8 nested `.git` dirs** (`tests/vault/vadv-49/fixture/{control,a1,a2,a4,a5,b,c}/.git`, `tests/vault/vadv54-run/p/p6repo/.git`); I rsync'd them back in explicitly so hazards were tested against real content.

## Step 2 — colocate via helper

`HYAKU_STATE=…/state jj-lane.sh init lane souji`

- State line: `state branch=master local=cbf688ab… remote=cbf688ab… ahead=0 behind=0 head=attached tracked=0 untracked=1`
- Init warnings: only the expected "author of the working copy will stay Joao Pedro Veiga…" (helper metaedits at commit time). **No** "@ already tracks N added path(s)" warning.
- `jj --ignore-working-copy config list --repo` → `snapshot.auto-track="none()"`, `user.name="souji-shokunin"`, `user.email="souji@shokunin.local"`, `revset-aliases."trunk()"="master@origin"` ✔
- `git symbolic-ref -q HEAD` → `refs/heads/master` (attached after init; becomes detached after first jj mutation — confirmed in step 4).
- `git status --porcelain` after init: still 1 line, `?? census/operator-sweep-20261019/` — **no change** vs step 1.
- `jj status` ×3 (warm): 0.014 / 0.014 / 0.015 s. Cold was sub-second too.

## Step 3 — auto-track `all()` comparison (`lane-autotrack`, `cp -a` + config set)

- First `jj status` after switching to `all()`: **0.052 s**; snapshot added **152 files** (all of `census/operator-sweep-20261019/`); warm status 0.014–0.018 s.
- **Zero** `new file too large` refusals — every untracked file is < 1 MiB.
- Fallout: `git status` in that clone went from 1 → **152 intent-to-add ` A` entries** (index spam); ignored `tests/vault/` content and nested `.git` content were NOT pulled in (jj honors .gitignore in snapshots).
- **Secret footgun**: `cp -a` of a `.jj` repo prints "repo appears to have been copied" — cloning a colocated lane to create a seat worktree must use `jj git init --colocate` fresh, not cp (or jj copies the repo identity).

## Step 4 — round commit through the helper + operator-push recovery

Prepared: appended LOG.md line, created `corpus/lessons/round-999-jjtrial.md`, left `.scratch/jjtrial-scratch.txt` untracked.

`jj-lane.sh commit lane --as souji -m "round-999: jj trial" -- LOG.md corpus/lessons/round-999-jjtrial.md`
→ `committed 62fcf624c2eba8ca38a56794353ce0d8dbd500fd` / `pushed 62fcf624…` — PASS.

Verifications:
- author AND committer = `souji-shokunin <souji@shokunin.local>` ✔ (metaedit path works)
- `git log -1 --format=%H -- LOG.md` = `62fcf624…` = pushed hash ✔
- `git merge-base --is-ancestor 62fcf624 master` → exit 0 ✔
- `git show --name-status` → exactly `M LOG.md`, `A corpus/lessons/…` — pathspec-limited ✔
- `jj-lane.sh state` → `ahead=0 behind=0 head=detached tracked=0 untracked=2` ✔
- sandbox `remote.git` master = `62fcf624` ✔; scratch file intact (`??`, content preserved) ✔
- HEAD detached at `62fcf62` after the mutation (expected colocation behavior).

Operator-push simulation (second clone `operator`, `considerthese/round-999.md`, pushed `00b416d`), then second helper commit `-- LOG.md`:
→ `committed ac807e69` then **rejected**; helper fetched, rebased the unpushed commit onto `master@origin`, retried → `pushed 0187c8fccfec24a3ddece11e8068335e2739ae8b`. Remote tip = `0187c8f`; history `0187c8f → 00b416d → 62fcf62 → cbf688a`; operator commit is ancestor; cited pushed hash ≠ printed local commit (rebase rewrote only the unpushed commit — correct per helper contract); state `ahead=0`.

## Step 5 — lane's own git-touching checks (300 s timeout each)

| Check | Colocated `lane` | Plain clone `plain` | Verdict |
|---|---|---|---|
| `tools/souji-repo-structure.sh --repo <r>` | exit 0 | exit 0 | PASS but **inflated**: `references.others.count=15` (refs/jj/keep/*), `objects.commits.count=55` vs 44 |
| `tools/souji-verify.sh LOG.md SKILL.md` | exit 0, `SAFE pushed` both | exit 0, identical | PASS — origin-ref-based receipts immune to colocation |
| `tools/souji-census.sh --root <sandbox>` | `dirty=1 unpushed=0` | `dirty=0 unpushed=0` | PASS — correct; but see I-T-A caveat below |

- The 15 extra refs are `refs/jj/keep/<sha>` — jj pins every intermediate working-copy/rebase commit. Any tool that counts "all refs" or unreachable objects sees them; `git rev-list --all` = 55 vs `--branches` = 44.
- Caveat on census: it counts `??` as dirty but apparently **not** intent-to-add ` A` entries — lane-autotrack (152 staged adds) reported `dirty=0, clean`. If any lane ever runs with auto-track≠none, the census's clean/dirty signal loses real information.

## PASS/FAIL table (steps 2–5)

| Step | Result | Notes |
|---|---|---|
| 2 init + config + status parity + timing | **PASS** | HEAD attached→detached as designed; status unchanged; 14 ms warm |
| 3 auto-track measurement | **PASS** (measurement) | 152 adds in 52 ms, no size refusals; confirms `none()` is mandatory |
| 4a commit/push/verify | **PASS** | all 7 checks green |
| 4b operator-push fetch+rebase recovery | **PASS** | cited hash is post-rebase pushed tip |
| 5 git-touching lane checks | **PASS ×3** | no colocation-only failures; structure census inflated by jj refs |

## Colocation hazards specific to this lane

1. **Nested `.git` ⇒ invisible files ⇒ committable phantom deletions [SEVERE].** `tests/vault/vadv54-run/p/p6repo/` contains an **empty** `.git/` dir. jj treats the whole `p6repo/` as a nested repo: `jj status` reports `D p6repo/one.txt`, `D p6repo/inner/keep.txt` for files that exist on disk and that git tracks normally; `jj file track <those>` exits 0 but does nothing. A `jj commit -- tests/vault/vadv54-run` (directory pathspec) **commits those deletions** (verified: commit c31a345 in lane-autotrack) — git then shows the files as untracked; pushing ships the deletion. Only a file-exact pathspec is safe today.
2. **`refs/jj/keep/*` inflation.** 15 keep-refs after one commit cycle; grows unboundedly. Affects: object/ref counts (souji-repo-structure), `git fsck` dangling set, `git log --all` output. Souji's receipt logic uses `--branches --not --remotes` so it is unaffected, but any "count all refs/objects" gate will drift vs a plain clone.
3. **Detached HEAD permanently.** `git rev-parse @{u}` fails ("HEAD does not point to a branch"), `git branch --show-current` prints nothing, `git worktree list` shows `(detached HEAD)`. `git rev-parse master` works. Any lane check that resolves `@{u}` or expects attached HEAD breaks.
4. **jj resets the git index on every mutation.** `git add file` → `A` entry → `jj describe` → entry gone, file back to `??`. The SKILL.md pre-quarantine checklist's `git add -- <paths>` staged-before-commit pattern cannot coexist with interleaved jj calls; helper pathspec commits are unaffected.
5. **Intent-to-add invisibility to `??`-based dirty checks** (only under auto-track≠none; see step 5).
6. **`cp -a` cloning a `.jj` repo** copies repo identity → jj prints a copied-repo warning; seats must init fresh.
7. **Symlinks, FIFOs**: tracked symlinks under `tests/vault/`/`tools/` handled fine; no FIFO/special files found under lane root (find -type p|s|b|c → 0). No LFS, no root `.gitattributes`, no non-sample hooks, no submodules — clean on those axes.
8. Working-copy commit retains the **pre-jj git identity** (`Joao Pedro Veiga`) until a helper commit metaedits it — cosmetic only; committed hashes carry correct lane identity.

## Recommendations (per-lane)

1. **Before colocating souji**: remove the empty `tests/vault/vadv54-run/p/p6repo/.git/` directory (it is an empty fixture stub, not tracked). Until then, NEVER commit with a directory pathspec over `tests/vault/`; use exact file paths. Long-term, teach the helper (or a lane pre-commit check) to refuse any `D` rows in `jj diff --summary -- <paths>` for files that exist on disk.
2. Keep `snapshot.auto-track="none()"` — measured win: 152-file index spam avoided.
3. Root `.gitignore` additions for the lane (also protects auto-track accidents): `/.scratch/`, `/.ufo/state/`, `/census/operator-sweep-*/` (3 untracked sweeps seen in-tree: 20261018 tracked-but-huge 4.1 MB file + 20261019 untracked dir).
4. Update SKILL.md prose: replace the `git add … && git commit -- <paths>` pre-quarantine recipe with `jj-lane.sh commit --as souji …` (or `-c maintenance.auto=false git commit` only when no jj mutation can interleave); document `@{u}` → `origin/master` fallback and that `git worktree list` showing `(detached HEAD)` is normal under colocation.
5. Accept `refs/jj/keep` drift in structure-census baselines, or pin comparisons to `git rev-list refs/heads/*` only.
6. LOG.md append-only + `.ufo/state` exclusion: verified naturally — helper refused nothing needed; `.scratch`/`census` untracked content never entered commits.

Sandbox preserved at `/fast/scratch/jj-wave/JjTrialSouji/` (cites commits 62fcf62/00b416d/0187c8f and the c31a345 hazard commit in `lane-autotrack`).
