# ScoutLaneMeasure — r24 w1, C1 lane-bound measurement prep (read-only)

## Status
STATUS: PASS — every requested field was read on the lane only. No fsck was run, nothing was written outside this report, and no scratch was created. The lane is jj-colocated (it has `.jj/` and 425 `refs/jj/keep/*` refs).

## Evidence
All commands ran against `/home/vgpnk/Projects/shokunin/souji-shokunin` on 2026-10-25 between about 06:20 and 06:21 (-03:00), with git 2.56.0. HEAD was `f9db2181647d91470a724a12d626bd6106805076`, detached (the preregistration commit), and the base `a65fac9…` is an ancestor (`merge-base --is-ancestor` rc=0).

1. `GIT_OPTIONAL_LOCKS=0 git -c maintenance.auto=false -C <lane> count-objects -v`
   ```
   count: 5665
   size: 39564
   in-pack: 1544
   packs: 3
   size-pack: 8791
   prune-packable: 0
   garbage: 0
   size-garbage: 0
   ```
   There was no `warning: garbage found:` line on stderr.
2. `git -C <lane> rev-parse --path-format=absolute --git-common-dir` returned `/home/vgpnk/Projects/shokunin/souji-shokunin/.git`. `--git-dir` returned the same path, so the lane is its own main worktree.
3. `git -C <lane> worktree list --porcelain` listed one entry, `worktree /home/vgpnk/Projects/shokunin/souji-shokunin` / `HEAD f9db218…` / `detached`. `.git/worktrees/` does not exist.
4. `objects/info/alternates` is ABSENT. `objects/info/` holds only `commit-graphs/` and `packs`.
5. Colocation: `.jj/` EXISTS (`repo/`, `working_copy/`, `.gitignore`). `for-each-ref --count=5 refs/jj/` printed 5 `refs/jj/keep/<oid>` commit refs, the first being `005f3d37…`. Full ref census:

   | namespace | refs |
   |---|---|
   | `refs/jj/keep` | 425 |
   | `refs/heads` | 5 |
   | `refs/remotes/origin` | 2 |
   | total | 432 |

   There are no other `refs/jj/*` names, such as `root` or `remote-tags/` (grep -v rc=1).
6. Pack layout: `ls .git/objects/pack/` and `git show-index < idx | wc -l`:
   - `pack-4e7d760b…`: 71 objects. It has a `.mtimes` sidecar, so it is a cruft pack.
   - `pack-6f97363d…`: 1018 objects.
   - `pack-f9f38aac…`: 455 objects.
   - The three sum to 1544, matching `in-pack`. There is also a `multi-pack-index`.
   - All 256 loose fan-out dirs exist. There are no stray files directly in `objects/`.
7. Reachability split, from `git rev-list` (read-only):

   | root set | objects | commits |
   |---|---|---|
   | `--branches --remotes` | 5485 | 160 |
   | `--all` (includes `refs/jj/keep`) | 6142 | 475 |

8. Repo config: no `extensions.partialClone`, no `remote.*.promisor`, no `shallow`. `gc.auto` and `maintenance.auto` are unset in the local config.
9. The worktree is dirty in two tracked files: `.ufo/waves/round-23/w2/W2D3.md` and `W2K1.md` (`status --porcelain --untracked-files=no`).

## Findings
1. **The common dir equals the git dir.** `<lane>/.git` is not a linked worktree, so preregistration case 4 (the linked-worktree discount) is not exercised by the lane run. `garbage: 0` here agrees with the design probe's "main worktree `garbage: 0`" (preregistration.txt:16).
2. **Alternates is absent, so the expected `alternates=0`.** The 0 comes from the file not existing, not from reading an empty or zero-size alternate database. README.md:489 requires that "`alternate` object databases must be read by any size figure (S115)".
3. **The lane is jj-colocated.** The 425 `refs/jj/keep/*` refs pin 315 commits and 657 objects that branches and remotes do not reach (6142 − 5485). README.md:217 says "colocated repos inflate structure counts versus a plain clone", and README.md:233-234 says "a colocated/plain byte-comparison is a precondition for any `git repo structure` baseline."
4. **A cruft pack is present.** `pack-4e7d…` has 71 objects plus `.mtimes`. These objects were already judged unreachable by an earlier `gc --cruft`. [INFERENCE] The L1's later `fsck --unreachable` figure will count cruft-pack objects that are still unreachable. U therefore counts old debris that was already packed away, not new debris.
5. **Most objects are loose.** 5665 objects (39564 KiB) are loose, against 1544 packed (8791 KiB). [INFERENCE] jj snapshots and commits keep writing loose objects and keep refs (S054 row: "jj writes a keep ref for every commit it creates or imports"). The figures move with every jj operation, including other seats' work in this lane during the wave.
6. **Disclosure on the index.** I ran `git status` twice without `GIT_OPTIONAL_LOCKS=0`; the contract lists `git status` as allowed. `.git/index` has mtime 06:19:51.97, and other seats were writing in `w1/` at 06:20. I cannot attribute any index refresh, and I did no other writes.

### What a reader must NOT infer from the lane figure
- **Not a fleet figure.** preregistration.txt:66-67 says "It is a figure about this repo only; no fleet figure is claimed."
- **Not a plain-clone figure.** Keep refs inflate the reachable set (Finding 3). They also suppress `unreachable`: anything a keep ref holds is reachable to fsck. [INFERENCE] Dropping `refs/jj/keep/*` could expose up to 657 more objects as unreachable; that bound is an upper estimate and overlap with packs was not computed. U is therefore not comparable to any plain repo's count.
- **Loose `count` is not debris.** `count`/`size` include reachable loose objects. Only `garbage`, `size-garbage` and fsck `unreachable` speak to debris, and U is qualified by Findings 3 and 4.
- **`size-pack` is not content size.** It is on-disk pack KiB and includes the cruft pack; the multi-pack-index is not counted in it.
- **`garbage=0` says nothing about linked worktrees.** The lane has none (Finding 1). It also does not show that the case-4 false-positive discount works.
- **`alternates=0` is not a measured alternate size.** It means the file is absent (Finding 2).
- **The figure is not bound to a commit.** The object database is not versioned, so the figure is not a property of base `a65fac9` or of tip content. It holds only at the moment of the run, with HEAD detached at `f9db218` and a dirty tree (Evidence 9). A rerun after any jj or git activity will differ.
- **It does not show that fsck is safe on the lane.** This seat ran no fsck, and the no-write envelope is a fixture (/var/tmp) claim only.

## Remaining unknowns
- U, the fsck unreachable count, is unmeasured here by design; the L1 runs the tool.
- The overlap between keep-only objects and the cruft or loose stores is not computed.
- jj keep-ref expiry is unmeasured. This is carried from README.md:216: "keep-ref expiry unmeasured".

Tools installed or updated: none.
