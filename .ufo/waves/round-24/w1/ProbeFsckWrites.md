# ProbeFsckWrites — round 24 wave 1

## Status
STATUS: PASS — on git 2.56.0, `fsck --unreachable --no-reflogs --no-progress` and `count-objects -v` (both via `--git-dir=<common>`) left the manifest byte-identical in all three scenarios (clean, dangling blob, linked worktree). `fsck --lost-found` on the dangling-blob repo created `lost-found/other/<oid>` with exactly the blob's content. Neither read-only command changed `index` or `objects/info/commit-graph`. A positive control showed the detector does see writes.

## Evidence
Lane revision read: `f9db2181647d91470a724a12d626bd6106805076` (read-only `rev-parse`; nothing in the lane was touched except this report).
Environment: `git version 2.56.0`, `HOME`=scratch, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `LC_ALL=C`. Scratch was `/var/tmp/souji-r24-ProbeFsckWrites/` and has been removed.

How the manifest works (`manifest.py`, run with `python3 -B`): it walks the whole `.git` tree and writes one sorted line per entry, plus one for the root: `relpath type mode size mtime_ns sha256`. Symlinks are recorded by target. atime and ctime are left out. After setup, every entry in `.git` (and in the linked-worktree directory) was reset with `touch -h -d '2020-01-01'` (mtime_ns `1577847600000000000`), so a rewrite with identical bytes would still show up as a new mtime. Each repo has two commits and a `commit-graph write --reachable`. Scenario (b) adds `hash-object -w` of `dangling-content-r24` (oid `f2f03edc902a7187aff3f26fe2e6f4624000b1a2`). Scenario (c) adds `worktree add <c-linked> -b side`. The `--lost-found` run was done on `cp -a` of (b), named b2.

| run | exit | stdout (relevant) | manifest entries before / after | diff |
|---|---|---|---|---|
| a fsck --unreachable --no-reflogs --no-progress | 0 | (empty) | 48 / 48 | none — byte-identical |
| a count-objects -v | 0 | `garbage: 0` | 48 / 48 | none — byte-identical |
| b fsck --unreachable --no-reflogs --no-progress | 0 | `unreachable blob f2f03edc…a2` | 50 / 50 | none — byte-identical |
| b count-objects -v | 0 | `count: 7` `garbage: 0` | 50 / 50 | none — byte-identical |
| c fsck --unreachable --no-reflogs --no-progress | 0 | (empty) | 60 / 60 | none — byte-identical |
| c count-objects -v (`--git-dir=<common>`) | 0 | `garbage: 0` | 60 / 60 | none — byte-identical |
| c count-objects -v (`-C <linked>`) | 0 | `garbage: 1`; stderr `warning: garbage found: …/w/c/.git/worktrees/c-linked/refs` | 60 / 60 | none — byte-identical; linked-worktree dir also unchanged |
| b2 fsck --lost-found --no-progress | 0 | `dangling blob f2f03edc…a2` | 50 / 53 | see below |

The `index` and `objects/info/commit-graph` lines were the same before and after every read-only run, for example in scenario (b):
```
index f 0o644 209 1577847600000000000 2eb2065d28696d1871d8e42c26aab0ce16552c365c36409b8463a90d5ec434ef
objects/info/commit-graph f 0o444 1232 1577847600000000000 5925f16f73675a2eef0b24cf58aeb016cf414270409bcd69e101d62dc110f1dc
```
`fsck --lost-found` also left both lines unchanged in b2.

Manifest diff for `fsck --lost-found` (b2):
```
1c1
< . d 0o755 0 1577847600000000000 -
---
> . d 0o755 0 1792920027470861258 -
28a29,31
> lost-found d 0o755 0 1792920027470861258 -
> lost-found/other d 0o755 0 1792920027470861258 -
> lost-found/other/f2f03edc902a7187aff3f26fe2e6f4624000b1a2 f 0o644 21 1792920027470861258 e888a083bc0be84c4b94d753dd9bc6dfa3478e067707af386f4418960ade83b2
```
Checking the content of the lost-found file:
```
content: dangling-content-r24
sha256 file  : e888a083bc0be84c4b94d753dd9bc6dfa3478e067707af386f4418960ade83b2
sha256 blob  : e888a083bc0be84c4b94d753dd9bc6dfa3478e067707af386f4418960ade83b2
CONTENT-EQUAL            (cmp of file vs `cat-file blob <oid>`)
git hash-object of file: f2f03edc902a7187aff3f26fe2e6f4624000b1a2
```

Falsifier variant: a fresh repo with natural mtimes, a worktree file modified after commit (inside the racy-index window), one dangling blob, a linked worktree and a commit-graph. Each step was compared with the manifest of the step before it:
```
racy fsck --git-dir: identical
racy count-objects: identical
fsck -C linked: identical          (stdout: unreachable blob 5fca3fd2…da)
git status control: diff at line 1 (. dir mtime) and line 21 -> detector sees writes
```
[INFERENCE] The changed line 21 in the status control is most likely `index` (an index refresh). The output was cut off at 5 lines, so its path was not printed.

## Findings
1. Verdict for `git --git-dir=<common> fsck --unreachable --no-reflogs --no-progress`: NO-WRITE on (a), (b) and (c). It is also NO-WRITE on the racy variant and when run as `git -C <linked> fsck …`. On (b) it reports the dangling blob as `unreachable blob <oid>`. Scratch location: `w/{a,b,c}` (removed).
2. Verdict for `git --git-dir=<common> count-objects -v`: NO-WRITE on (a), (b) and (c), and on the racy variant. Run on its own it changes nothing.
3. Verdict for `git -C <linked> count-objects -v`: NO-WRITE, but it reports `garbage: 1` because of `<common>/worktrees/<id>/refs`, while the common-dir read gives `garbage: 0`. This reproduces the F2 linked-worktree false positive that C1 case 4 relies on.
4. Verdict for `git fsck --lost-found` on (b): WRITES. It creates 3 manifest entries (`lost-found/`, `lost-found/other/`, `lost-found/other/<oid>`) and changes the mtime of the `.git` root directory. The new file has mode 0644 and is 21 bytes. It contains the raw blob content (sha256 matches `cat-file blob`, and `hash-object` of the file gives back the oid), not the oid as text. It exits 0 and labels the object `dangling` rather than `unreachable`. This supports C1 case 7 `lost_found=WRITE-DETECTED`. It also leaves `index` and `commit-graph` untouched, so a detector that only watches those two files would miss this write.
5. `index` and `objects/info/commit-graph` mtimes did not change under any of the probed commands, including `--lost-found`.

## Attack log
- A1 (gameability of C1 case 7, not a predicate change): a manifest that looks only at files would still catch the write, because `lost-found/other/<oid>` is a new regular file. A detector limited to `index`/`commit-graph` mtimes would not catch it (finding 4). The frozen case-1 manifest, which covers every path, is sufficient.
- A2 (mtime resolution): any manifest that compares mtimes taken shortly after setup could miss a same-second rewrite on filesystems with coarse timestamps. Resetting all mtimes to 2020-01-01 before the command removes that risk, and the `git status` positive control shows the probe is sensitive to writes. A fixture SHOULD do the same reset or compare at nanosecond resolution [INFERENCE: whether the C1 fixture does this was not checked].
- Tool installs: none.
