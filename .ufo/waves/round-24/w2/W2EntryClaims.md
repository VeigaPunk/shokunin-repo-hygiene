# W2EntryClaims — souji r24 wave 2 (FALSIFY)

Target: `corpus/knowledge/count-objects-linked-worktree-garbage.md` at master `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`, blob `dfbc558b107dfdcc9b2102ffb2f77b15d1f08175`. The blob is unchanged since after-state `778747eb`. The lane tip has moved past the named `ca7fc1cb`, but only wave-1 reports were added (`c3ca7ad`). Line numbers below refer to the committed blob. The working-tree copy carries uncommitted edits by another seat: a `GIT_COMMON_DIR` precondition after line 87, citing W2SrcPath, and the S121 line ranges. Those edits were not attacked.

## Status
STATUS: PARTIAL — every requested reproduction holds on git 2.56.0. Five creation modes read 1. A bisect with bad and good marked reads 2. A `refs/worktree` ref reads 2, and 3 with its reflog. 1023 B reads 0 and 1024 B reads 1. An uppercase-hex loose name is not garbage. `--git-dir=<common>` reads 0 for every trigger. But item 1's "creating git does not change the count" is falsified by a git 2.30.0-created worktree, and four other claims are overstated or incomplete (Findings 1-6).

## Evidence
- Host git `git version 2.56.0`. The scratch harness was `/var/tmp/souji-r24-W2EntryClaims/probe.sh` (sha256 `60078936…81ada`, output sha256 `a3d261bd…9f397`). It ran with all GIT_* unset, `LC_ALL=C GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null`, and HOME in scratch. Every read is `git -C <dir> count-objects -v`.
- Creation modes. Raw linked reads `garbage: 1 size-garbage: 0` with `warning: garbage found: r/.git/worktrees/w-<m>/refs`. Common reads `garbage: 0`. Main reads `garbage: 0`. This holds for `--detach`, `-b`, `--orphan -b`, detach+commit and `-b`+commit. It also holds for extra modes: `--no-checkout`, `--lock`, `-B`, `--relative-paths`, and `worktree move`. In all ten, private `refs` is empty with st_size 0. After `rmdir refs` the read is `garbage: 0`. The tool reports `garbage=0 size_garbage=0 unreachable=0 alternates=0 exit=0`.
- Bisect:

  | step | garbage |
  |---|---|
  | `bisect start` only | 1 |
  | `+bad` | 2 (`refs`, `refs/bisect`) |
  | `+bad+good` | 2 |
  | after a real `git bisect reset` (rc=0) | 2 |

  After the reset, `find` shows `refs` and `refs/bisect` (now empty). The common read is 0. `logs/refs/bisect` is absent.
- `refs/worktree`:

  | state | garbage |
  |---|---|
  | `update-ref refs/worktree/x HEAD` | 2 (no `logs/refs/worktree`) |
  | `--create-reflog` | 3 (`logs/refs/worktree`, `refs`, `refs/worktree`) |
  | after `update-ref -d` | 2 (empty `refs/worktree` stays) |

  The common read is 0 in each state.
- `sparse-checkout set foo` in a linked worktree reads 3 (`info`, `info/sparse-checkout`, `refs`). The common read is 0.
- `rebase -r --exec false HEAD~1` stopped in a linked worktree: `refs/rewritten: [onto]` reads 2. It still reads 2 after `rebase --abort`. The common read is 0.
- 2048 B `objects/pack/junk`:

  | read | garbage | size-garbage |
  |---|---|---|
  | main | 1 | 2 |
  | linked raw | 2 | 2 |
  | linked common | 1 | 2 |
  | tool on linked path | `garbage=1` | `size_garbage=2` |
- Size floor on the main worktree: 1023 B → `size-garbage: 0`, 1024 B → 1, 10239 B → 9, two 600 B files → `garbage: 2 size-garbage: 1`. The filesystem is `btrfs`. Directory st_size: `refs`=12 and `refs/bisect`=96 after bisect. With 60 `refs/worktree` refs, `refs/worktree`=2520 and the linked raw read is `garbage: 2 size-garbage: 2`.
- Uppercase names:
  - `objects/12/ABCDEF0123456789ABCDEF0123456789ABCDEF` (10240 B): `count` goes 4→5, `garbage: 0`.
  - `objects/AB/<38 lowercase hex>`: `count: 4 garbage: 0`. The directory is not walked.
- Alternates, with B borrowing A's objects:
  - A `objects/12/zz` (loose junk), read from B: `garbage: 0`.
  - A `objects/pack/junk` (2048 B), read from B: `garbage: 1 size-garbage: 2` with `warning: garbage found: altsrc/.git/objects/pack/junk`.
  - The tool on B gives `garbage=1 size_garbage=2 unreachable=0 alternates=1` and `census.unreachable_scope=includes-alternates`. There is no corresponding scope label for garbage.
- Cross-version (git 2.30.0 built in scratch, see Tooling). The repo was created by 2.56.0.

  | worktree | private gitdir | 2.56.0 read | 2.30.0 read |
  |---|---|---|---|
  | `g30 worktree add --detach` / `-b b30` | `HEAD ORIG_HEAD commondir gitdir index logs` (no `refs`) | `garbage: 0` | `garbage: 0` |
  | 2.56.0 `worktree add --detach` | adds `refs` | `garbage: 1` | `garbage: 1` |

  2.56.0 `bisect bad` in the 2.30-created worktree then reads `garbage: 2`: `refs` is created lazily.
- Source lines re-read in the snapshots: `sha256sum -c SHA256SUMS` gives 6/6 OK. The quotes match their cited lines:
  - path.c@v2.56.0 line 90: "Not considered garbage for report_linked_checkout_garbage"
  - line 111: `{ 0, 1, 1, "refs" },`
  - line 371: `if (!r->different_commondir)`
  - path.c@v2.30.0 line 123: `{ 0, 1, 1, "refs" },`
  - count-objects.c line 50: `size_garbage += st.st_size;`
  - count-objects.c line 152: `(unsigned long)(size_garbage / 1024));`

  git-worktree.1.txt line 140 "refs inside refs/bisect, refs/worktree and refs/rewritten are not shared" and line 170 are present. The item 1-4 line numbers in entry lines 1-3 all match.
- Committed witness: `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` gives `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`, rc 0. `souji-receipt-run.py verify … census/round-24/records/c1-after.tsv` gives `verify=ok rev=778747eb…`. The README F2 row names the entry (README line 510/516).

## Findings
1. **FALSIFIED — line 26-27**, "The table belongs to the git doing the reading, so the git that created the worktree does not change the count." A worktree created by git 2.30.0 has no private `refs` and reads `garbage: 0` under the 2.56.0 reader. A worktree created by 2.56.0 reads 1 under both the 2.56.0 and 2.30.0 readers. The reader's table decides which names are eligible. The creating git, and every later command that writes there, decides which names exist. The same overstatement is carried in Gate line 132 ("the reading git counts it whoever wrote it") and line 140 ("its reader-decides reading").
2. **OVERSTATED — line 32 heading**, "Every way of creating a linked worktree leaves `refs`, so every one reads 1." The heading has no version scope, and it is false for 2.30.0-created worktrees (Finding 1). The body at line 35 scopes the claim to 2.56.0. There it survives: 10 creation modes all read 1, which is five more than the entry claims.
3. **OVERSTATED — line 47** ("an active bisect with a bad and a good commit marked reads `garbage: 2`"), **Gate line 133 and 142** ("an active bisect"), and **line 86** ("a bisecting or `refs/worktree` linked worktree"). One mark (`bisect bad` alone) already reads 2. After a real `git bisect reset`, the empty `refs/bisect` stays and still reads 2. The same holds for a deleted `refs/worktree` ref (empty dir stays: 2) and for an aborted `rebase -r` (`refs/rewritten` stays: 2). The count tracks leftover directories, not active state. A worktree that ever bisected stays at 2. Item 7's common-dir rule is unaffected: it reads 0 in every case.
4. **COUNT MISMATCH — line 59-66**, "twelve planted kinds". The bullets name 11 kinds: pack junk, an invalid name, `tmp_obj_*`, an object-named directory, and seven sidecars. The twelfth cell in ProbeGarbageKinds is `a3b` (`objects/pack/junk.txt`), which is folded into the first bullet. Either say eleven kinds over twelve cells, or list `a3b`.
5. **INCOMPLETE — line 105-107** (alternates bullet) **and line 81-83** ("a linked-worktree path reports the common-dir figure"). Measured: an alternate's loose junk is not counted, which turns the entry's `[INFERENCE]` into a measurement. But an alternate's `objects/pack/` junk **is** counted from the borrowing repo: `garbage: 1 size-garbage: 2`, with the warning naming the other repo's path. The tool reports that as this repo's `garbage=1`, and it labels only `unreachable` with an alternates scope. So a non-zero census `garbage` can be another repository's debris. The entry does not say so.
6. **INCOMPLETE — line 110-112** ("Directory size on other filesystems is not measured … [INFERENCE: not run off btrfs]"). This frames non-zero directory st_size as an other-filesystem risk. On btrfs itself, a non-empty counted directory has non-zero st_size: `refs`=12, `refs/bisect`=96, `refs/worktree` holding 60 refs=2520. A linked raw read then gives `size-garbage: 2` from structure alone. Item 6's "An empty directory adds 0 on btrfs" (line 79) is correct only for empty directories. The census tool is unaffected because it reads the common dir.
7. **NOT FALSIFIED, under-listed — line 103-105** (uppercase 38-hex counted as a loose object): reproduced, `count` 4→5 and `garbage: 0`. There is a further false negative the entry omits: an uppercase two-hex subdir (`objects/AB/…`) is never walked (`count` unchanged, `garbage: 0`).
8. **EXTENDS — line 102**, "`refs/rewritten` (rebase) was read in the table but not run." Now run on 2.56.0: a stopped `rebase -r` reads 2, it persists after `--abort`, and the common read is 0. This does not contradict the entry.

## Attack log

| item | attack | result |
|---|---|---|
| 1 | cross-version create/read (2.30.0 ↔ 2.56.0) | last sentence falsified (F1); mechanism and line cites survive |
| 2 | snapshot byte check of the flag rows at both tags | survives |
| 3 | 5 + 5 creation modes, `rmdir refs` causal check, older-git creation | 2.56.0 body survives; heading falsified (F2) |
| 4 | bisect each step and reset; `refs/worktree` with and without reflog, and after delete; sparse-checkout | 2/3/3 reproduced; "active" framing overstated (F3) |
| 5 | pack junk read from main, linked and common; alternates | survives; count wording (F4); alternate pack debris omitted (F5) |
| 6 | 1023/1024/10239/2×600 B; non-empty directories on btrfs | numbers survive; directory-size framing incomplete (F6) |
| 7 | `--git-dir=<common>` for every trigger, plus the tool | survives: 0 for all structure triggers, debris kept 1/2 |
| NOT-established | uppercase, alternates, rebase, fleet figure, two tags | survives with additions (F5, F7, F8); no fleet figure found in the entry |

## Residual risk and verification gaps
- The tool, not the entry: `souji-size-census.py` on a repo whose alternate holds loose junk exits 1. The cause is `git failure: … fsck … exited 0: bad sha1 file: …/altsrc/.git/objects/12/zz`, because any fsck stderr is treated as a failure. This is outside this item and is reported only.
- The 2.30.0 binary was built locally and used only to create and read worktrees. Tags between 2.30 and 2.56 were not bisected for when `worktree add` began creating private `refs`. [INFERENCE] ProbeLinkedModes A1 and the amendment's git ≥ 2.46.0 precondition point there.
- No non-btrfs filesystem was run, because scratch is confined to `/var/tmp`.

## Tooling
- git 2.30.0, built from the official tarball `https://mirrors.edge.kernel.org/pub/software/scm/git/git-2.30.0.tar.xz`. Its sha256 `55735021…d334d19` equals the line in `sha256sums.asc`. The `.asc` GPG signature was not verified. Build: `make CFLAGS="-O1 -std=gnu17 -w" NO_CURL=1 NO_OPENSSL=1 …`, because the default GCC 16 C23 mode rejects `thread_local`. It was built under scratch, not installed, and removed with scratch. The reason was to falsify item 1's cross-writer claim. No pacman transaction was run.

## Writes
This report only. Scratch `/var/tmp/souji-r24-W2EntryClaims/` was created and then removed. There were no lane mutations, no fleet paths, and no shokuknow access.
