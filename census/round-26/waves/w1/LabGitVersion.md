# LabGitVersion — host git version, lane maintenance config, man-page check

## Status

STATUS: PASS — all three probe questions answered on the live host and the lane repo: `git --version` is 2.56.0 as expected; the lane repo carries zero `gc.*`/`maintenance.*`/`fetch.*` config, so stock defaults (including `gc.auto=6700`, `maintenance.auto=true`, `gc.autoDetach=true`, and `git gc` calling `git worktree prune --expire 3.months.ago`) are the effective config, and the lane does hold its own maintenance/prune mechanism; the installed `man git-fetch` documents `--auto-maintenance`. Two claim-level findings remain open for the L1: the S132 census that grounds Entry B has been overtaken by events (4 of 5 registrations are now prunable), and the tip's own `### Round 26` blocks were appended after `## Retired`, re-breaking the newest-first layout contract that C1 exists to enforce while both frozen C1 counters still pass.

Revision discipline: the lane HEAD moved seven times during the probe (jj exports). Every measurement below is labelled with the revision or sample it came from. Final sample: `166baa18f808071bc385187691713044a26bd663`, 2026-10-25T17:39:31Z, `master` == HEAD, HEAD detached; at that sample the frozen counters still reported `markers=0`, `headings=17 44 78`, `cases=12 pass=12`, gate `ok=2 fail=0` rc 0, and 6920 loose objects.

## Evidence

### E1 — host git and lane identity

```
$ git --version
git version 2.56.0                      # matches the expected 2.56.0

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --abbrev-ref HEAD
HEAD
$ git -C ... status --porcelain=v1 --branch        # first sample
## HEAD (no branch)

$ git -C ... rev-parse HEAD ; git -C ... rev-parse master      # first sample
d6c13b0f00066cbb342fdc50167849a5f1c726e5
d6c13b0f00066cbb342fdc50167849a5f1c726e5

$ git -C ... reflog show --date=iso -3
d6fe8a1 HEAD@{2026-10-25 14:31:32 -0300}: export from jj
ea0bbe6 HEAD@{2026-10-25 14:30:51 -0300}: export from jj
d6c13b0 HEAD@{2026-10-25 14:30:04 -0300}: export from jj
```

HEAD was detached at the branch commit in every sample taken (d6c13b0, ea0bbe6, d6fe8a1, ba8b54b, c594901, 0c92c2e, 9a6e0f13); `master` and `origin/master` point at the same OID as HEAD. The lane is an independent repo: `.git` is a directory, and the fleet root has no `worktrees/souji-shokunin` registration.

### E2 — effective maintenance config of the LANE repo (the asked command)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin config --list --show-origin \
    | grep -iE 'maintenance|gc\.|worktree'
(no output)
grep_exit=1

$ git -C ... config --get-regexp '^(gc|maintenance|fetch)\.'
keyprobe_rc=1                             # no matching key at any scope

$ git -C ... config --list --show-scope --show-origin
global  file:/home/vgpnk/.config/git/config   alias.co=checkout
global  file:/home/vgpnk/.config/git/config   alias.br=branch
global  file:/home/vgpnk/.config/git/config   alias.ci=commit
global  file:/home/vgpnk/.config/git/config   alias.st=status
global  file:/home/vgpnk/.config/git/config   init.defaultbranch=main
global  file:/home/vgpnk/.config/git/config   pull.rebase=true
global  file:/home/vgpnk/.config/git/config   push.autosetupremote=true
global  file:/home/vgpnk/.config/git/config   diff.algorithm=histogram
global  file:/home/vgpnk/.config/git/config   diff.colormoved=plain
global  file:/home/vgpnk/.config/git/config   diff.mnemonicprefix=true
global  file:/home/vgpnk/.config/git/config   commit.verbose=true
global  file:/home/vgpnk/.config/git/config   column.ui=auto
global  file:/home/vgpnk/.config/git/config   branch.sort=-committerdate
global  file:/home/vgpnk/.config/git/config   tag.sort=-version:refname
global  file:/home/vgpnk/.config/git/config   rerere.enabled=true
global  file:/home/vgpnk/.config/git/config   rerere.autoupdate=true
global  file:/home/vgpnk/.config/git/config   user.name=probe
global  file:/home/vgpnk/.config/git/config   user.email=probe@example.invalid
global  file:/home/vgpnk/.config/git/config   credential.https://github.com.helper=
global  file:/home/vgpnk/.config/git/config   credential.https://github.com.helper=!/home/vgpnk/.local/bin/gh auth git-credential
global  file:/home/vgpnk/.config/git/config   credential.https://gist.github.com.helper=
global  file:/home/vgpnk/.config/git/config   credential.https://gist.github.com.helper=!/home/vgpnk/.local/bin/gh auth git-credential
global  file:/home/vgpnk/.config/git/config   credential.https://origin.cursor.com/git.helper=
global  file:/home/vgpnk/.config/git/config   credential.https://origin.cursor.com/git.helper=!/home/vgpnk/.local/bin/origin credential-helper
global  file:/home/vgpnk/.config/git/config   credential.https://origin.cursor.com.helper=
global  file:/home/vgpnk/.config/git/config   credential.https://origin.cursor.com.helper=!/home/vgpnk/.local/bin/origin credential-helper
global  file:/home/vgpnk/.config/git/config   filter.lfs.clean=git-lfs clean -- %f
global  file:/home/vgpnk/.config/git/config   filter.lfs.smudge=git-lfs smudge -- %f
global  file:/home/vgpnk/.config/git/config   filter.lfs.process=git-lfs filter-process
global  file:/home/vgpnk/.config/git/config   filter.lfs.required=true
global  file:/home/vgpnk/.config/git/config   credential.helper=/usr/lib/git-core/git-credential-libsecret
local   file:.git/config                      core.repositoryformatversion=0
local   file:.git/config                      core.filemode=true
local   file:.git/config                      core.bare=false
local   file:.git/config                      core.logallrefupdates=true
local   file:.git/config                      user.name=souji-shokunin
local   file:.git/config                      user.email=souji@shokunin.local
local   file:.git/config                      remote.origin.url=https://github.com/VeigaPunk/shokunin-repo-hygiene.git
local   file:.git/config                      remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*
local   file:.git/config                      branch.master.remote=origin
local   file:.git/config                      branch.master.merge=refs/heads/master
local   file:.git/config                      lane.branch=master
local   file:.git/config                      lane.id=souji

$ git -C ... config --system --list
fatal: unable to read config file '/etc/gitconfig': No such file or directory
$ ls -l /etc/gitconfig
ls: cannot access '/etc/gitconfig': No such file or directory
$ git -C ... config --get-all include.path ; echo $?
1                                         # no include indirection
$ git -C ... config --get-all maintenance.repo ; echo $?
1                                         # repo not registered for scheduled maintenance
$ env | awk -F= '/^GIT_/{print $1}'       # no GIT_CONFIG_* override present
GIT_EDITOR
GIT_PAGER
GIT_TERMINAL_PROMPT
```

Effective config = stock defaults: nothing in global, local, system or environment opts the lane out. Defaults in force, quoted from the installed pages rendered as `MANWIDTH=100 man --nh --nj <page>` (line numbers as rendered):

- git-gc(1):120 `The default value is 6700.` (gc.auto)
- git-gc(1):136 `Default is true. This config variable acts as a fallback in case maintenance.autoDetach is` (gc.autoDetach)
- git-gc(1):189 `When git gc is run, it calls git worktree prune --expire 3.months.ago.` (gc.worktreePruneExpire)
- git-maintenance(1):355 `Defaults to true.` (maintenance.auto)
- git-maintenance(1):363 `If unset, the value of gc.autoDetach is used as a fallback. Defaults to true if both are`

### E3 — does the host's `man git-fetch` document `--auto-maintenance`? YES

```
$ MANWIDTH=100 man --nh --nj git-fetch | awk 'NR>=158 && NR<=176 {printf "%d:%s\n", NR, $0}'
164:     --auto-maintenance, --no-auto-maintenance, --auto-gc, --no-auto-gc
165:         Run git maintenance run --auto at the end to perform automatic repository maintenance if
166:         needed. This is enabled by default.
168:     --write-commit-graph, --no-write-commit-graph
169:         Write a commit-graph after fetching. This overrides the config
170:         setting fetch.writeCommitGraph.

$ git fetch -h 2>&1 | grep -n -i 'auto'
54:    --[no-]auto-maintenance
55:                          run 'maintenance --auto' after fetching
56:    --[no-]auto-gc        run 'maintenance --auto' after fetching
```

Installed page: `/usr/share/man/man1/git-fetch.1.gz` (15952 bytes, dated 2026-09-28).

Calibration caveat, relevant to the lane's read-from-bytes style: a plain-string grep of the compressed roff FAILS because the page escapes hyphens. The search only works escaped or after rendering:

```
$ zcat /usr/share/man/man1/git-fetch.1.gz | grep -n -i 'auto-maintenance'
(no output)
$ zcat /usr/share/man/man1/git-fetch.1.gz | grep -n 'auto\\-maintenance'
267:\fB\-\-auto\-maintenance\fR, \fB\-\-no\-auto\-maintenance\fR, \fB\-\-auto\-gc\fR, \fB\-\-no\-auto\-gc\fR
```

The same trap sits in this round's own snapshot: `census/round-26/sources/git-fetch.1.txt` is HTML and the sentence is split by tags and a newline (3195: a `<p>` with the `git maintenance run --auto` code spans, 3196: `repository maintenance if needed.`, 3197: `This is enabled by default.</p>`). Entry A's Gate quote is therefore NOT byte-contiguous in that snapshot; it (and Entry B's shorter quote) pass only because `tools/souji-gate-check.py:11` requires a quote to appear `verbatim (whitespace-collapsed)` (`squash()` at :54). A checker that does a byte-substring test on the `.gz` or the raw snapshot would report false absence.

### E4 — the lane's own prune / auto-gc state

```
$ git -C ... count-objects -v              # six samples across the probe window
count: 6683            # ~14:35Z
count: 6690
count: 6732
count: 6747            # 17:36Z at 0c92c2e
count: 6785            # 17:38Z at 9a6e0f13
count: 6920            # 17:39Z at 166baa1
in-pack: 1544   packs: 3   size-pack: 8791   size: 46156   prune-packable: 0   garbage: 0

$ ls -la .git/worktrees
ls: cannot access '.git/worktrees': No such file or directory
$ git -C ... worktree list
/home/vgpnk/Projects/shokunin/souji-shokunin  ea0bbe6 (detached HEAD)   # 1 entry, 0 registrations

$ ls -la .git/gc.log
ls: cannot access '.git/gc.log': No such file or directory
$ ls -la .git/objects/pack/*.pack
pack-4e7d760b502a3bd1479d91193f12cbe2d15b8220.pack   2026-10-18 15:09:36
pack-6f97363d41f64e54f046818c9b6e6cba9a772081.pack   2026-10-19 19:24:49
pack-f9f38aacc912b8fdc803c01c6ae987d5777089dd.pack   2026-10-19 19:24:49
```

The lane holds NO worktree-registration numerator (0 registrations, so 0 prunable) but it DOES hold the mechanism on stock defaults, and the default `gc.auto=6700` threshold was crossed inside the probe window (6683 → 6785 loose objects). The next object-writing porcelain command runs `git gc --auto` detached in the background (`gc.autoDetach` default true), which also runs `git worktree prune --expire 3.months.ago` and a repack, while HEAD is detached and the wave is mid-flight. `[INFERENCE]` the repack is harmless to reachability; the operability point is an unattended background write during integration.

### E5 — fleet-exposure denominator re-measurement (grounds Entry B's language)

```
$ git -C /home/vgpnk/Projects/shokunin worktree list
/home/vgpnk/Projects/shokunin               8177d1e9 (detached HEAD)
/fast/scratch/hyaku/native-mutation-proof   58c94352 [hyaku/native-mutation-proof] prunable
/fast/scratch/hyaku/root-closure-null-round e82b86b8 [hyaku/root-closure-null-round] prunable
/fast/scratch/hyaku/s3-nonauthor64          61145980 [hyaku/s3-nonauthor64] prunable
/fast/scratch/hyaku/s3-ready66              e82b86b8 [hyaku/s3-ready66] prunable

$ git -C /home/vgpnk/Projects/shokunin worktree prune --dry-run -v
Removing worktrees/s3-nonauthor64: gitdir file points to non-existent location
Removing worktrees/root-closure-null-round: gitdir file points to non-existent location
Removing worktrees/s3-ready66: gitdir file points to non-existent location
Removing worktrees/native-mutation-proof: gitdir file points to non-existent location
default_expiry_rc=0

$ git -C ... worktree prune --dry-run --expire=now -v
(identical four lines)                     expire_now_rc=0

$ ls /home/vgpnk/Projects/shokunin/.git/worktrees/*/locked
(each: No such file or directory)          # 0 locked

$ findmnt -T /fast
TARGET SOURCE         FSTYPE OPTIONS
/fast  /dev/nvme1n1p2 xfs    rw,nosuid,nodev,noatime,inode64,logbufs=8,logbsize=256k,noquota

$ ls /fast/scratch/hyaku
kaidoku-r34b  kama-r38  kama-r39  kama-r39-closure  kama-r39-fleet  kama-r39b
kumitate-pin  kumitate-r58-close  kumitate-r58-wave          # none of the four registered paths

$ git -C /home/vgpnk/Projects/shokunin config --list --show-origin | grep -icE 'maintenance|gc\.|worktree'
0
```

Both prune invocations were `--dry-run`; nothing was pruned, moved or touched. `/fast` is mounted and `/fast/scratch/hyaku` exists, so the four targets are genuinely gone, not unmounted. The fleet-root repo also carries no maintenance config, so it runs the same defaults.

Saved census bytes: `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out:21` `default expiry (3.months.ago):      (no output — none prunable)` and `:31-32` `today: 0 prunable, 0 locked, 5 registrations (all 4 extra have live working`.

Entry B at the final tip: `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md:73-74` `census (2026-10-23) found **5 registrations, 0 prunable, 0 locked** at` / `every expiry including --expire=now, so the fleet is currently *not*`; `:87` `in S132: 5 registrations, 0 prunable, 0 locked.`; its Gate ADMIT reason (now at `## Gate`, entry line 94 onward) describes the census as `a read-only census of the live fleet and not a point-in-time figure`.

### E6 — the lane's frozen counters at tips 9a6e0f13 and 166baa1 (read-only, informational for the landing gate)

```
$ git rev-parse HEAD   → 9a6e0f13b10cff82c1f6a05059779ed6c06f8a28   (2026-10-25T17:38:17Z)
                         re-run at 166baa18f808071bc385187691713044a26bd663 (17:39:31Z): c1
                         markers=0 headings=17 44 78; c3 cases=12 pass=12; gate entries=2
                         ok=2 fail=0 rc=0. K4's last run is at 9a6e0f13; the entries and
                         snapshots it reads did not change in 166baa1.

$ bash census/round-26/c1-counter.sh
markers=0
headings=17 44 78
$ bash census/round-26/c2-counter.sh
grounded_f1=2
registry_rows=132
$ bash census/round-26/c3-counter.sh
axis_check_tool=present
claims=3 flags=0
axis_check_exit=0
cases=12 pass=12 control=FALSE-GREEN-REJECTED
fixture_exit=0

$ python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md
claims=3 flags=0                                   k1_rc=0

$ python3 -B tools/souji-coverage-agreement.py --root . --rev 9a6e0f13... --base-rev 0eca7c8...
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0     k4_rc=0

$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
              corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources \
    --slice census/round-26/records/empty-slice \
    --slice-verdicts census/round-26/records/empty-verdicts
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0
gate_rc=0
```

Both admitted entries now carry `## Gate` (entry A line 69, entry B line 94). The two receipts named by the frozen RECEIPTS paragraph are committed and both record `rev=33e6807ea54ad5fa295d9138067a9a78f3b0f7ec`, rc 0, with the pre-registered argv:

- `census/round-26/records/c2-gate.tsv` → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`
- `census/round-26/records/c2-k4-after.tsv` → `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`

`33e6807` is an ancestor of the tip; `git diff 33e6807 HEAD` over the two entry paths and over `census/round-26/sources` is empty, and `sha256(git show 33e6807:tools/souji-gate-check.py)` equals the receipt's `tool_sha256=d5ed0805...`, likewise for `tools/souji-coverage-agreement.py` (`bb506469...`). So the receipts bind the bytes still present at the tip. `verify=ok` was NOT re-run by me (machine verification is another seat's item).

### E7 — probe-window transient (for the record; resolved at 33e6807/9a6e0f13)

At `ba8b54b` and `0c92c2e` the same frozen commands gave:

```
ba8b54b: python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py
         cases=11 pass=11            (no control token in the tool arm)
0c92c2e: python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py
         cases=12 pass=12 control=FALSE-GREEN-REJECTED      (fixed in c594901)

0c92c2e: gate-check on the two ADMITTED paths
         FAIL ... check1-no-gate (both)
         entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2      gate_rc=1
         # same command on the two W1 DRAFTS: entries=2 ok=2 fail=0, rc 0
0c92c2e: census/round-26/records/  → c2-gate.tsv and c2-k4-after.tsv absent;
         c3-control.tsv present (removed at 0c92c2e once its case became fixture case 12)
```

Those are revision-scoped observations, not the tip verdict. The tip verdict is E6.

### E8 — the tip's own Round 26 blocks violate the newest-first layout (sample 166baa1)

```
$ git log --oneline -1
166baa1 round-26: measurements block + r26 planned bullet (SCORECARD), lessons updates, ...

$ git diff --stat 9a6e0f13 HEAD -- SCORECARD.md
 SCORECARD.md | 10 ++++++++++
 1 file changed, 10 insertions(+)                 # pure append, no deletions

$ awk '/^## /{printf "%d:%s\n", NR, $0}' SCORECARD.md
9:## Axes
124:## Capabilities
158:## Planned
204:## Saturation / stagnation
210:## Tool certification (r9)
233:## Retired
$ awk '/^### Round/{printf "%d:%s\n", NR, $0}' SCORECARD.md
17:### Round 25 measurements ...
27:### Round 25 append-only corrections
44:### Round 24 measurements ...
78:### Round 23 measurements ...
239:### Round 26 append-only corrections
264:### Round 26 measurements ...

$ bash census/round-26/c1-counter.sh
markers=0
headings=17 44 78                                  # K2 sees only the 23/24/25 triple
```

So the newest round's blocks sit below `## Retired` / `None.` (line 235), 160+ lines after the oldest measurement block they should precede, and corrections precede measurements for r26 although the r25 pair runs measurements-then-corrections. Both frozen C1 counters still pass, because K1's marker regex looks for the deleted scaffold wording and K2's regex matches only `Round (23|24|25)`.


## Findings

1. **Host git is 2.56.0**, matching the expected version (E1). No version-dependent surprise in this probe.
2. **The lane's effective maintenance config is empty** — the asked grep returns nothing (exit 1), `config --get-regexp '^(gc|maintenance|fetch)\.'` returns nothing, there is no `/etc/gitconfig`, no `include.path`, no `maintenance.repo`, and no `GIT_CONFIG_*` environment override (E2). Defaults therefore govern: `gc.auto=6700`, `gc.autoDetach=true`, `maintenance.auto=true`, `maintenance.autoDetach` falling back to true, and `git gc` invoking `git worktree prune --expire 3.months.ago` (E2 quotes). Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.git/config`, `/home/vgpnk/.config/git/config`.
3. **Answer to "does the lane hold its own prune risk?"** Yes, structurally, with a zero numerator today. `.git/worktrees` is absent and `git worktree list` shows only the lane itself (0 registrations), so there is nothing for the lane to prune; but loose objects rose 6683 → 6920 across the probe and now exceed stock `gc.auto=6700`, with `.git/gc.log` absent and the newest pack from 2026-10-19 (E4). The lane is not exempt: no config opts it out of the trigger, and a `git gc --auto` will run worktree prune plus a detached repack. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.git/`.
4. **The lane is detached from its branch in every sample** — `rev-parse --abbrev-ref HEAD` prints `HEAD`, HEAD == `master`, reflog entries read `export from jj` (E1). `[INFERENCE]` this is the jj export mechanism rather than a lost commit, but it means the prereg header's "branch master, ahead=0" is a statement about the ref, not about the working HEAD.
5. **The installed `man git-fetch` documents `--auto-maintenance`** at OPTIONS: plain render line 164, `git fetch -h` lines 54-56, roff line 267 in escaped form (E3). The traps: the unescaped search misses the compressed page because of roff hyphen escaping, and the committed snapshot is HTML whose sentence spans lines 3195-3197, so the Gate quotes are whitespace-collapsed-verbatim only (`tools/souji-gate-check.py:11,54`). Location: `/usr/share/man/man1/git-fetch.1.gz:267`, `census/round-26/sources/git-fetch.1.txt:3190-3197`.
6. **Entry B's census-derived numerator is stale, so its "not exposed" clause is false at probe time.** The fleet-root repo lists 5 entries of which `git worktree list` marks 4 `prunable`; `worktree prune --dry-run` reports all four for removal at BOTH the default 3-month expiry and `--expire=now`, with 0 locked; their `/fast/scratch/hyaku/*` targets are gone while `/fast` is mounted (E5). The saved census recorded `0 prunable` on 2026-10-23 on the premise that `all 4 extra have live working` directories, and its own Gate reason calls the figure `not a point-in-time figure` — it is exactly a point-in-time figure, now overtaken. Location: `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md:73-74,87`; source `r23-worktree-census.out:21,31-32`.
7. **C2's frozen counters all pass at the final tip** — K1 `grounded_f1=2` and rows 132; K2 gate `ok=2 fail=0` rc 0 on the admitted paths; K4 `kill_tested=7 kill_violations=0` mismatches 0 (E6). The two receipts are committed at `33e6807`, whose entry and snapshot bytes are identical to the tip and whose tool digests match (E6).
8. **During the probe window, the claimed C2 gate receipt did not correspond to the frozen command** — at `0c92c2e` the frozen command on the admitted paths returned `fail=2` (`check1-no-gate`) while the drafts returned `ok=2`, and the commit message for `d6c13b0` claimed "real gate rc=0" (E7). Corrected at `33e6807` by adding `## Gate` to both entries. Recorded as a calibration event because the intermediate receipt was not producible by the frozen command. Location: commits `d6c13b0`, `33e6807`; `tools/souji-gate-check.py:65-75`.
9. **C1 red receipt revision is not the declared base.** `census/round-26/records/c1-before.tsv` records `rev=12fd90bcd9cdfab495e178023eeaa838a977fcbe`, i.e. the prereg-freeze commit, not `0eca7c8` as the prereg's red-before command names. Numerically benign: `git diff 0eca7c8 12fd90bc -- SCORECARD.md` is empty, so the counted bytes are identical; the C1 counter also re-reported `markers=0` and `headings=17 44 78` at the tip (E6). `c1-after.tsv` records `rev=07f83e69`, and the committed SCORECARD has not changed since that commit (verified at 9a6e0f13). Location: `census/round-26/records/c1-before.tsv`; `.ufo/waves/round-26/preregistration.txt` C1 DO-NOTHING CONTROL.
10. **The C1 protected-span ambiguity was resolved pre-data by amendment 2** (byte-content spans, not line positions), and the landed SCORECARD matches that shape: the diff against base has hunks at base lines 15, 89, 135 and 169 only — base lines 1-16 (title through the Axes table, so no score edit) untouched, the r25 and r24 blocks inserted above the Round 23 heading, the two r24 capability rows appended in `## Capabilities`, the two planned bullets appended, and the scaffold block deleted. Location: `.ufo/waves/round-26/preregistration-amendment-2.txt`; `git diff 0eca7c8..9a6e0f13 -- SCORECARD.md`.
11. **The working tree was dirty during the probe and is clean at the last sample.** `git status --porcelain -- SCORECARD.md` returned ` M SCORECARD.md` with 10 inserted working-tree lines at 17:38Z while the committed bytes still matched `07f83e69`; commit `166baa1` then committed exactly those 10 lines. C1's committed-byte claims therefore hold, but counters run before that commit read a mixed tree — the L1's landing gate must run at the final commit, not at an intermediate working tree. Location: `SCORECARD.md`, commit `166baa1`.
12. **The tip's own Round 26 blocks are appended after `## Retired`, re-breaking the newest-first layout that C1 exists to enforce, and neither frozen C1 counter can see it** (E8). Section order at `166baa1`: `## Retired` at 233 with `None.` at 235, then `### Round 26 append-only corrections` at 239 and `### Round 26 measurements` at 264, i.e. the newest round sits below the oldest measurement block (Round 23 at 78) and below the terminal section; r26 also runs corrections-before-measurements while r25 runs measurements-before-corrections. The file states the invariant it is now violating, in its own words at 246-247: `re-ordered the file (254 → 233 lines, Round 25 measurements above Round 24)`. K1 and K2 both still pass because their regexes are fixed to the deleted scaffold wording and to Rounds 23/24/25 respectively. Location: `SCORECARD.md:233,235,239,264`.

## Attack log

My assigned item is a probe, not an attack; I changed no frozen predicate, target, case set or axis and propose none (post-data relaxation is forbidden by the AMENDMENT RULES). Two claim-evidence attacks are recorded for the L1:

- **A1 — census currency (Entry B), open.** The claim `5 registrations, 0 prunable, 0 locked` plus `the fleet is currently *not*` exposed, and its Gate reason `not a point-in-time figure`, are contradicted by a read-only re-measurement two days later: 4 of 5 registrations are prunable at the default expiry and at `--expire=now`, 0 locked, and the exposure is live with no config change because both repos run stock defaults. A stricter-only fix is to date the sentence and append the re-measurement; the alternative is to drop the currency clause. Owner: the C2 seat plus the L1.
- **A2 — receipt-vs-command substitution (C2), observed and self-corrected inside the wave.** At `0c92c2e` the frozen gate command failed on the admitted paths while the drafts passed, and a committed receipt/message claimed rc 0 (E7); `33e6807` fixed the entries so the frozen command now matches. Retained because a receipt that cannot be reproduced by the frozen command is exactly the calibration failure mode the lane instruments, and only the L1 can decide whether the early receipt is superseded or withdrawn.
- **A3 — C1's K2 is a fixed round window, so the layout contract is unenforced for any round outside 23/24/25.** The tip demonstrates it: `### Round 26` blocks after `## Retired` score `markers=0` and `headings=17 44 78`, i.e. K1 and K2 both pass while the newest-first property the claim is about is false for the newest round (E8). This is a counter-coverage attack, not an implementer defect: the honest options are to record C1 as passing only its frozen Rounds 23-25 scope (and state that in the report), or to land a stricter-only amendment that generalizes the ordering predicate to every `### Round <n> measurements` heading. I propose neither change myself; post-data relaxation is forbidden and even a stricter predicate needs the amendment receipts before it is scored. Owner: the C1 seat plus the L1.

## Housekeeping

- Tool installs/upgrades: none (no pacman, no uv/npx, no downloaded binary; nothing was needed).
- Scratch: none created; `/var/tmp/souji-r26-LabGitVersion` does not exist.
- Writes: this report only. Every lane and fleet command was read-only (`log/show/diff/status/ls-tree/cat-file/rev-parse/config/worktree list`, `count-objects`); both `worktree prune` invocations were `--dry-run` and pruned nothing. Lane Python ran with `python3 -B`.
