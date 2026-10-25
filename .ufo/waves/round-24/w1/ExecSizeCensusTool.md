# ExecSizeCensusTool — C1 tool draft (souji round 24, wave 1)

## Status
STATUS: PASS — draft written to the frozen C1 CLI, with the L1 amendment applied (alternates from `count-objects -v`, scope line). It is 196 lines, Python 3 stdlib only. On throwaway repos under /var/tmp it produced the expected figures for all five case-1..5 shapes, refused --lost-found and partialClone/promisor repos, and left the .git manifest unchanged in every run. Fixture counter NOT run (not this seat's file).

## L1 amendment applied (pre-data, tool internals only; CLI and counts line unchanged)
- Revised delivery: 196 lines, sha256 `e4ca8b87f74b8a77b09f1dd220d272bfb68948bc568409613f23502ea0662e9a`. This supersedes the pre-amendment sha `4d4a0d84…` quoted below.
- (1) `alternates=` is now the count of `alternate: ` lines from `git --git-dir=<common> count-objects -v` (the `alternates()` reader for objects/info/alternates is gone). GIT_OBJECT_DIRECTORY and GIT_ALTERNATE_OBJECT_DIRECTORIES were already removed from the child env, because every inherited `GIT_*` is dropped. The docstring now names both.
- (2) When alternates > 0, `census.unreachable_scope=includes-alternates` is printed right before the counts line. `unreachable=` is not filtered.
- (3) count-objects stderr is unchanged and already met the amendment: `warning: garbage found:` lines become `census.warning=`; any other stderr line, `error:` included, gives exit 1.

Post-amendment run (final sha e4ca8b87…; boilerplate keys elided; manifest unchanged in every case):
```
clean        garbage=0 size_garbage=0 unreachable=0 alternates=0                 exit=0
dang         garbage=0 size_garbage=0 unreachable=1 alternates=0                 exit=0  no lost-found
garb         census.warning=warning: garbage found: .../garb/.git/objects/pack/junk
             garbage=1 size_garbage=0 unreachable=0 alternates=0                 exit=0
lnk-wt       raw `git -C linked` garbage: 1 ; census invoked_from=linked garbage=0 exit=0
alt (1 path) count.alternate=.../base/.git/objects
             census.unreachable_scope=includes-alternates
             garbage=0 size_garbage=0 unreachable=0 alternates=1                 exit=0
dup (same path twice + `# c` + blank line)
             count.alternate=.../base/.git/objects   (listed ONCE by git)
             census.unreachable_scope=includes-alternates ... alternates=1     exit=0
self (alternates names own objects dir)
             no count.alternate line ... alternates=0                            exit=0
miss (/nonexist/objects)
             git failure: rev-parse exited 0: error: unable to normalize alternate object path   exit=1
dalt (alternate repo holds a dangling blob; dalt itself has none)
             census.unreachable_scope=includes-alternates
             garbage=0 size_garbage=0 unreachable=1 alternates=1                 exit=0
env GIT_ALTERNATE_OBJECT_DIRECTORIES=<dbase> GIT_OBJECT_DIRECTORY=<dang> on clean
             garbage=0 size_garbage=0 unreachable=0 alternates=0                 exit=0
--lost-found exit=2 ; partialClone exit=2
```
The file-line counter would have reported 2 for dup and 1 for self; git resolves them to 1 and 0. This confirms ProbeAlternates' divergence point. In dalt, fsck reports the alternate's debris as unreachable in the borrowing repo, which is why the scope line exists.

## Evidence (pre-amendment revision)
- Delivery: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-24/w1/souji-size-census.py`, 200 lines, sha256 `4d4a0d843056f05a11131d1f593685b0046b72287cda163db95affc48addc4b9` (superseded, see above; L1 copies the file to `tools/souji-size-census.py`).
- Host: `git version 2.56.0`, Python 3.14.8. No tools installed or upgraded.
- Scratch: `/var/tmp/souji-r24-ExecSizeCensusTool/`, removed at the end (`ls: cannot access ... No such file or directory`). The tool was never run against the lane or the fleet repo.
- Manifest = sha256 of the sorted `find -printf '%p %y %m %s %T@'` listing plus the sha256 of every regular file under the repo's .git (atime/ctime excluded). It was taken before and after each run.

Final-bytes run (sha above):
```
$ census --repo .../clean
census.tool=souji-size-census
census.status=ok
census.git_version=git version 2.56.0
census.common_dir=/var/tmp/souji-r24-ExecSizeCensusTool/clean/.git
census.invoked_from=main
count.count=2
count.size=8
count.in_pack=0
count.packs=0
count.size_pack=0
count.prune_packable=0
count.garbage=0
count.size_garbage=0
garbage=0 size_garbage=0 unreachable=0 alternates=0
exit=0   manifest unchanged
$ census --repo .../dang            (one hash-object -w blob)
garbage=0 size_garbage=0 unreachable=1 alternates=0
exit=0   manifest unchanged   no lost-found
$ census --repo .../garb            (junk file in objects/pack)
census.warning=warning: garbage found: /var/tmp/souji-r24-ExecSizeCensusTool/garb/.git/objects/pack/junk
garbage=1 size_garbage=0 unreachable=0 alternates=0
exit=0   manifest unchanged
raw git -C linked: garbage: 1
$ census --repo .../lnk-wt          (linked worktree)
census.invoked_from=linked
garbage=0 size_garbage=0 unreachable=0 alternates=0
exit=0   manifest unchanged
$ census --repo .../alt             (alternates -> existing base/.git/objects)
count.alternate=/var/tmp/souji-r24-ExecSizeCensusTool/base/.git/objects
garbage=0 size_garbage=0 unreachable=0 alternates=1
exit=0   manifest unchanged
$ census --repo .../clean --lost-found
souji-size-census: refused: unknown or missing arguments: --repo ... --lost-found
exit=2   manifest unchanged
$ census --repo .../pc              (extensions.partialClone=origin)
souji-size-census: refused: partial-clone repository (extensions.partialClone=origin)
exit=2   manifest unchanged
--help exit=0
```
Earlier run of the same matrix on the previous revision (it differs from the final only by 3 docstring lines). It also covered these cases:
`--lost-found --repo P` exit 2; no argv exit 2; `remote.origin.promisor yes` exit 2 `promisor remote (remote.origin.promisor true)`; `promisor false` exit 0; non-repo dir exit 2 `fatal: not a git repository`; nonexistent path exit 2 `fatal: cannot change to`; bare clone `invoked_from=bare` exit 0; subdirectory `invoked_from=main` exit 0; inherited `GIT_DIR=<garb>` with `--repo <clean>` → `garbage=0`, exit 0 (the inherited GIT_* is dropped); empty repo (no commit) exit 1; broken alternates path exit 1. Every one of these left the manifest unchanged.

## Findings
1. Behaviour: every walk runs as `git -c maintenance.auto=false -c gc.auto=0 -c core.fsmonitor=false --git-dir=<common> {count-objects -v | fsck --unreachable --no-reflogs --no-progress}`. All inherited `GIT_*` env vars are removed, then GIT_OPTIONAL_LOCKS=0, GIT_NO_LAZY_FETCH=1, GIT_TERMINAL_PROMPT=0, GIT_NO_REPLACE_OBJECTS=1 and LC_ALL=C are set. Calls use argv lists only, stdin is /dev/null, and the tool never runs `cd`. Stdout is written only on success.
2. Discovery is one call: `git -C PATH rev-parse --path-format=absolute --git-common-dir --git-dir --is-bare-repository`. invoked_from is `bare` if the repo is bare, `linked` if realpath(git-dir) != realpath(common), else `main`. A non-zero rev-parse exit gives exit 2 (not a repository). Exit 0 with stderr gives exit 1 (git failure).
3. Refusal happens before any walk. `git -C PATH config --get extensions.partialClone` returning rc 0 → exit 2. `config --type=bool --get-regexp '^remote\..*\.promisor$'` with any `true` (yes/on/1 are normalized by git) → exit 2. Config is read via `-C PATH`, so a worktree's config.worktree is included.
4. Exit 1 on an empty (unborn) repo: git 2.56 `fsck` prints `notice: No default references` on stderr with rc 0. The frozen "any other stderr" rule therefore makes the tool exit 1 there. Every fixture repo needs at least one commit. I sent this to `L1Souji24.ExecSizeCensusFixture`.
5. Case 5 needs a real path: if `objects/info/alternates` names a nonexistent dir, every git call prints `error: unable to normalize alternate object path: ...`, and the tool exits 1 (it fails closed). The fixture's alternates path must be an existing objects dir. I sent this to the fixture seat too.
6. Repeated key: `count-objects -v` prints one `alternate: <path>` line per resolved alternate. These pass through as repeated `count.alternate=` lines, so `count.*` keys are not guaranteed unique. After the amendment, the counts-line `alternates=` is exactly the number of these lines.
7. Git missing (OSError) → exit 1. The contract word is "git failure"; souji-repo-structure.sh uses 2 for this case. `[INFERENCE]` The contract does not pin this case.

## Attack log
- ATTACK (calibration, report only; not a counter change): the unreachable figure is `fsck --unreachable --no-reflogs`. Objects reachable only from reflogs are therefore counted as unreachable, which is the intended debris view. A reader could take `unreachable=` to mean "prunable now", but gc's reflog/prune expiry would keep many of these. The tool reports the figure without claiming they are prunable.
- ATTACK (coverage): the case set has no empty-repo case, and the strict stderr rule makes that shape exit 1 (finding 4). Not gameable, but a lane-bound run on a repo with no default ref would exit 1 and produce no figure.
- Checks the L1 should run after integration: `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` at the landing tip, and the single lane-bound run for `census/round-24/size-census-lane.txt`.
