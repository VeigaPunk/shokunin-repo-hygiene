STATUS: DONE — `@` matches master after the four helper commits; `rev-list | head` hides the only unpublished LOG.md blob and 15 older phantom-deletion commits.

Attacked claim: after helper commits `3f822e8`, `42d9ff3`, `2fc5f33`, `5efb519`, the colocated working copy has no phantom deletion and no unexpected tracked path, and no keep-only commit holds content that is not on master. Judged axis: operability.

# Axes

- Operability (judged): `@` must stay equal to `refs/heads/master`, and a keep-only snapshot from these four commits must not be the only copy of census, gate, or proc-census bytes.
- Calibration (do not harm): Q28 / `jj_keep_novel` stays a leaf-blob test against remote history (`tools/souji-quarantine.sh:1008-1031`, same predicate in `tools/souji-verify.sh:242-265` and `tools/souji-vault-verify.sh:435`). Do not special-case `LOG.md`.
- Coverage (do not harm): the 15 historical p6repo deletions stay a keep-ref fact. Do not clear them by editing `@`, and do not fold them into the proc-census.

# Proposal

Replace `git rev-list --glob='refs/jj/keep/*' --not --branches --remotes --tags | head` as the post-landing keep check. Keep two predicates the four commits already satisfy, and do not change `jj_keep_novel`.

1. Phantom / unexpected path passes only when `jj --ignore-working-copy status` is empty and `git rev-parse '@^{tree}'` equals `git rev-parse 'refs/heads/master^{tree}'`. This round passes. Both `tests/vault/vadv54-run/p/p6repo/one.txt` and `inner/keep.txt` are in `@`. Do not re-track them on the next landing.
2. "Content not on master" means a leaf blob in a keep-only commit that is absent from `git rev-list --objects --remotes -- <path>`, over the full rev-list, not the first 10 lines. The only such blob today is `LOG.md` `7a1877036cba781ceefb815ffa4b0607f6265dea`, and it is not a product of the four commits.

No edit to `tools/souji-census.sh`, `tools/souji-landing-gate.py`, `tools/souji-proc-census.sh`, or `jj_keep_novel`. Do not `jj op abandon` or `jj util gc` this round: the live `@` is itself keep-only (`refs/jj/keep/0e14747fa027aa7d3da9382db1a86d82e7986863`), and the lane helper does not own gc (`corpus/knowledge/jj-colocation-receipts.md` Limits).

# Evidence

Tools installed: none. `jj` and `git` were already on the host. Pacman is paused; nothing new was required.

## `@` is the master tree

`jj --ignore-working-copy -R /home/vgpnk/Projects/shokunin/souji-shokunin status`

```
The working copy has no changes.
Working copy  (@) : xuulysqq 0e14747f (empty) (no description set)
Parent commit (@-): otvrkvvt 5efb519f master | round-18: r15 frozen preservation record regenerated at 2fc5f33 (changed census/fixtures), replay gate note
```

`.git/HEAD` is detached at `5efb519f00075d958c3d1109ef6fcb24c487eb87`. `refs/heads/master` and `refs/remotes/origin/master` are that same commit. Detached HEAD at the bookmark is the colocated normal case (S051, quoted in `corpus/lessons/round-17.md`). It is not a second tree.

`git rev-parse 'HEAD^{tree}' '5efb519f00075d958c3d1109ef6fcb24c487eb87^{tree}' '0e14747fa027aa7d3da9382db1a86d82e7986863^{tree}'` → all three `52856c68ee5c2dbc0b714fdb8b26f602b9b8a663`.

`git diff --name-status 5efb519f00075d958c3d1109ef6fcb24c487eb87` empty. `git diff --cached --name-status` empty. `git ls-files -d` empty. `git ls-files -v | cut -c1 | sort | uniq -c` → `2376 H` (no assume-unchanged, no skip-worktree).

`git cat-file -e 0e14747fa027aa7d3da9382db1a86d82e7986863:tests/vault/vadv54-run/p/p6repo/one.txt` and `…/inner/keep.txt` both succeed. Both paths exist on disk. `tests/vault/vadv54-run/p/p6repo/.git` is absent. Same presence on `master:`.

The four commits, oldest first: `3f822e8` 17:56:15 -0300, `42d9ff3` 18:03:55, `2fc5f33` 18:09:56, `5efb519` 18:12:51. Combined `git diff --name-status b576341 5efb519` is adds and modifications only (no deletion of the p6repo pair). Tip `tests/fixtures/r14-census-boundary.py` blob `c6a3b31d54b705148aa5a84687a312014b68de67` equals `b576341` and `2fc5f33`. `3f822e8` and `42d9ff3` hold the other blob `f9fb339181eb2588246350f8014d969df4664260`, which is on master, not keep-only.

## `head` shows the harmless end of the keep list

`git for-each-ref refs/jj/keep --format='%(objectname)' | wc -l` → `55`.

`git rev-list --glob='refs/jj/keep/*' --not --branches --remotes --tags | head` prints 10. The same rev-list without `head` prints 42. The first 10 are:

```
0e14747fa027aa7d3da9382db1a86d82e7986863
2ec2a6c4648c8744653bc7ecb7971dda616b1e44
15a1eb72e88f49435047c87c656f733282664c92
23bb62f776547e0f9142c18da6fc5c7764168641
2651e6f87a3f428389f163aca63696384530a013
a2c601891b0d4de3234ad27d1d8972cdbfc443bf
d56cc3d50512f0adf7c1e7babb97736367830c8d
dee48f6fed863b09041e5ec1aab57a233f9bbdba
0404a05d8f34da8586521bf047bba155d5df3c8f
10de69188ddb419a00b20b3b15daa1aec01fd496
```

Thirteen keep-only commits are parented on `b576341`, `3f822e8`, `42d9ff3`, `2fc5f33`, or `5efb519` (the thirteen include `49cdbee`, `5256ca8`, and `563bbcb`, which `head` cuts off). Four of those thirteen have trees that match no commit on master (`2651e6f` tree `43443a07`, `a2c6018` tree `6cd1aed1`, `0404a05` tree `2cd37bbd`, `563bbcb` tree `91eba8ce`). Every leaf blob those four change relative to their parent is already in `git rev-list --objects master`, including:

- `0404a05:tools/souji-census.sh` `03b763550487e3c758ed4e61e031627c199e9b84`
- `0404a05:tools/souji-proc-census.sh` `979ff356bef7b96a0d0d8bdbc8503ea847a5dd53`
- `0404a05:tools/souji-landing-gate.py` `2cbb939ecb794e8b286aa6c36e9e55b5c5098b7e`
- `563bbcb:tools/souji-census.sh` same census blob
- `2651e6f:tools/souji-landing-gate.py` `fd976ecacee6afe998182f41ce9ccd04ebf764e1`
- `a2c6018:LOG.md` `7f3527c6a2fd62b87ffe5def7ad0b8e1904bdbab` (this is master's LOG blob)

`2651e6f:tests/fixtures/r14-census-boundary.py` is already the restored pin `c6a3b31`, while its parent `42d9ff3` still has `f9fb339`. That revert landed in `2fc5f33`. None of the thirteen deletes either p6repo path.

## The one blob that is not on master

Parents of all 42 keep-only commits are reachable from branches, remotes, or tags, except root `dcc1512e2a4f4db48de025081485223ac8ee8246` (empty tree `4b825dc642cb6eb9a060e54bf8d69288fbee4904`, no paths). Novel bytes can only be blobs a keep-only commit changes relative to that parent.

That scan finds one blob, five times: `LOG.md` `7a1877036cba781ceefb815ffa4b0607f6265dea` on

- `073875f2a20df764d92339d19924291a8107e9a4` parent `4f48343`
- `16c5548824be5a069b97e1cafbabc40b071f575a` parent `4f48343`
- `ec561bed222b31731011cbb12b9416d7d108a0a0` parent `4f48343`
- `5d20347ee81182851b60c13af766dd013d9972e4` parent `d7e648d`
- `a4fd871184408fd9374375eae6ed535b832df423` parent `d7e648d`

`git rev-list --objects --remotes -- LOG.md` has 99 objects and does not contain `7a187703`. `jj_keep_novel` (`tools/souji-quarantine.sh:1024-1031`) therefore returns novel for `LOG.md`. Contradiction, both measured: `git diff --numstat 5efb519 073875f2 -- LOG.md` is `0	9	LOG.md` (zero lines in the keep blob that master lacks; nine lines on master that the blob lacks). `git diff 073875f2 5efb519 -- LOG.md` shows those nine lines are the round-17 and round-18 LOG headings already in `5efb519`. The hash test says unpublished. The line test says the four helper commits' LOG text is not trapped in the keep ref. Those five parents are `d7e648d` (14:24:42 -0300) and `4f48343` (15:57:26 -0300), before `3f822e8`.

## Phantom deletions are not in `@` and not in the first 10

Fifteen keep-only commits lack `one.txt` and `inner/keep.txt` while their parent has both. `head` shows none of them.

```
16c5548824be5a069b97e1cafbabc40b071f575a
5d20347ee81182851b60c13af766dd013d9972e4
a4fd871184408fd9374375eae6ed535b832df423
ec561bed222b31731011cbb12b9416d7d108a0a0
4bd640b0345374921e0cd03a1dc9a80959776edc
ca6cbbf5fbc3c5309f7523ac972f1f649cc00bdf
0a213617dba90c3cabe69763998261f7b6aca83f
7732a164e819b51b83f6b2f83a0b7b40a52ceeec
be4e630b464ee161c45b07e87a64176031e4a4e5
e30ceecf1668be5b36779d988252b9bd0f79620e
f7f3a4e584e601ce1d0ba382acaadebb9305dd67
0254661427750f47e04f20864c5091cfc74e2e0e
1e0d8d1644cf18a0e02189bc27b33a5a6b55474c
719154dc9d15ea25a0204ba12c35493526d6c1ed
41ab059d7dd5c3465bb84d7049a87756cdc19926
```

Four of those fifteen also hold `7a187703` (`16c5548`, `5d20347`, `a4fd871`, `ec561be`). `073875f2` holds the LOG blob and still has both p6repo files. `corpus/knowledge/jj-colocation-receipts.md:74` says this lane holds four such phantom-deletion commits. The rev-list shows 15. `@` shows zero. Deletions have no leaf blob, so `jj_keep_novel` does not refuse them (`:1022-1027`).

# Verdict

Partial, split by predicate.

- Holds for the four helper commits and for `@`: no phantom deletion, no unexpected tracked path, no unpublished census/gate/proc-census/r14 bytes. r14 at tip is the `b576341` pin.
- Fails as a repo-wide reading of "any keep-only commit with content not on master" only for blob `7a187703` on five pre-round commits. Fails as a description of `@` if someone checks out one of the 15 phantom commits; the current `@` does not contain that deletion.

# Smallest fix

Leave the r18 tools alone. Point the next landing check at tree equality of `@` and at the full keep-only rev-list's leaf blobs (the query `jj_keep_novel` already runs), not at `head`. Keep file-exact pathspecs: the helper still commits before it refuses a phantom deletion (`scripts/hyaku/jj-lane.sh`, commit then the check; wave-1 `ConnJjInteraction.md` cites `:604` versus `:618-654`). A directory pathspec over a future `@` that has been moved onto one of those 15 commits would record another keep-held deletion. Do not weaken `jj_keep_novel` so that "zero insertions against `master:<path>`" counts as not novel: that would clear this LOG.md blob and would also clear a keep commit that only deletes lines.

# Risks

- Leaving `| head` in the checklist sends the next wave at `2651e6f`, `a2c6018`, and `0404a05` (novel trees, published blobs) and away from `7a187703` and the 15 phantoms.
- A pushed receipt whose target is `LOG.md` stays NOT-SAFE while those five keep refs exist, even though master already contains every line of `7a187703` plus the nine round-17/18 heading lines. The four commits already pushed later LOG bytes (`a2c6018`'s LOG blob is master's) because the lane helper does not call `jj_keep_novel`. That receipt bit is not a census hang.
- `jj edit` / `jj undo` onto any of the 15 puts the deletion back in `@`. With `snapshot.auto-track = "none()"` it sticks (`jj-colocation-receipts.md:68`). File-exact commits of other paths do not take it with them.
- GC of keep refs would drop `7a187703` and the phantom commits, and would also drop the protection on empty `@` `0e14747` if that ref were pruned early. Not this round's lever.

# Verification

Read-only, on `/home/vgpnk/Projects/shokunin/souji-shokunin`, no souji tool executed. Commands and the outputs above: `jj --ignore-working-copy status`; `for-each-ref refs/jj/keep | wc -l` (55); `rev-list --glob='refs/jj/keep/*' --not --branches --remotes --tags` (42, first 10 quoted); `rev-parse` of the three trees; `git diff` / `diff --cached` / `ls-files -d` / `ls-files -v`; `cat-file -e` for the two p6repo paths on `@` and `master`; per-commit `diff-tree` against parent for every keep-only commit, blob membership in `git rev-list --objects master` and in `git rev-list --objects --remotes -- LOG.md`. No clone. No install.
