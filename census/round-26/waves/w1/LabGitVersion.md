# LabGitVersion — host git version, lane maintenance config, man-page check

## Status

STATUS: PASS — all three probe questions answered on the live host and the lane repo: `git --version` is 2.56.0 as expected; the lane repo carries zero `gc.*`/`maintenance.*`/`fetch.*` config, so stock defaults (including `gc.auto=6700`, `maintenance.auto=true`, `gc.autoDetach=true`, `git gc` calling `git worktree prune --expire 3.months.ago`) are the effective config and the lane does hold its own maintenance/prune mechanism; the installed `man git-fetch` documents `--auto-maintenance`. Two adjacent claim-level findings (C2 K2 gate failing at the tip; S132 census currency) are recorded below for the L1.

Revisions: the lane HEAD moved throughout the probe (jj exports): d6c13b0 → ea0bbe6 → d6fe8a1 → ba8b54b → c594901 → 0c92c2e. Each measurement names its revision. Final sample: `0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b`, 2026-10-25T17:36:28Z, `master` == HEAD, HEAD detached.

## Evidence

### E1 — host git and lane identity

```
$ git --version
git version 2.56.0                      # matches the expected 2.56.0

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --abbrev-ref HEAD
HEAD
$ git -C ... status --porcelain=v1 --branch
## HEAD (no branch)

$ git -C ... rev-parse HEAD ; git -C ... rev-parse master
d6c13b0f00066cbb342fdc50167849a5f1c726e5       # first sample
d6c13b0f00066cbb342fdc50167849a5f1c726e5

$ git -C ... reflog show --date=iso -3
d6fe8a1 HEAD@{2026-10-25 14:31:32 -0300}: export from jj
ea0bbe6 HEAD@{2026-10-25 14:30:51 -0300}: export from jj
d6c13b0 HEAD@{2026-10-25 14:30:04 -0300}: export from jj
```

HEAD is detached at the branch commit in every sample; `master` and `origin/master` point at the same OID. The lane is an independent repo: `.git` is a directory, and the fleet root has no `worktrees/souji-shokunin` registration.

### E2 — effective maintenance config of the LANE repo (the asked command)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin config --list --show-origin \
    | grep -iE 'maintenance|gc\.|worktree'
(no output)
grep_exit=1

$ git -C ... config --get-regexp '^(gc|maintenance|fetch)\.'
keyprobe_rc=1                            # no matching keys at any scope

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
1                                        # no include indirection
$ git -C ... config --get-all maintenance.repo ; echo $?
1                                        # repo not registered for scheduled maintenance
$ env | awk -F= '/^GIT_/{print $1}'      # no GIT_CONFIG_* override
GIT_EDITOR
GIT_PAGER
GIT_TERMINAL_PROMPT
```

Effective config = stock defaults; nothing in global, local, system or environment opts the lane out. Defaults in force, from the installed pages (`MANWIDTH=100 man --nh --nj <page>`, line-numbered as rendered):

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

Installed page: `/usr/share/man/man1/git-fetch.1.gz` (15952 bytes, 2026-09-28).

Calibration caveat (matters to the lane's read-from-bytes style): a plain-string grep of the compressed roff FAILS because the page escapes hyphens; the unescaped search only works after rendering:

```
$ zcat /usr/share/man/man1/git-fetch.1.gz | grep -n -i 'auto-maintenance'
(no output)
$ zcat /usr/share/man/man1/git-fetch.1.gz | grep -n 'auto\\-maintenance'
267:\fB\-\-auto\-maintenance\fR, \fB\-\-no\-auto\-maintenance\fR, \fB\-\-auto\-gc\fR, \fB\-\-no\-auto\-gc\fR
```

The same trap exists in this round's own snapshot: `census/round-26/sources/git-fetch.1.txt` is HTML, and the sentence is split by tags and a newline (lines 3195-3197: a `<p>` opening with the `git maintenance run --auto` code spans, then `repository maintenance if needed.`, then `This is enabled by default.</p>`). Entry A's Gate quote (`entry-git-auto-maintenance-trigger-set.md`, Gate row 1) is therefore NOT byte-contiguous in the snapshot; it and Entry B's shorter quote pass only because `tools/souji-gate-check.py:11` checks that a quote appears `verbatim (whitespace-collapsed)` (`squash()` at :54). A future checker that does a byte-substring test on the `.gz` or on raw snapshot bytes would report false absence.

### E4 — the lane's own prune/auto-gc state

```
$ git -C ... count-objects -v          # four samples across the probe window
count: 6683            (first sample, ~14:35Z window start)
count: 6690
count: 6732
count: 6747            (17:36Z, tip 0c92c2e)
in-pack: 1544   packs: 3   size-pack: 8791   prune-packable: 0   garbage: 0

$ ls -la .git/worktrees
ls: cannot access '.git/worktrees': No such file or directory
$ git -C ... worktree list
/home/vgpnk/Projects/shokunin/souji-shokunin  ea0bbe6 (detached HEAD)     # 1 entry, 0 registrations

$ ls -la .git/gc.log
ls: cannot access '.git/gc.log': No such file or directory
$ ls -la .git/objects/pack/ | head
... multi-pack-index  2026-10-18 23:11:11
```

Answer to the assigned question: the lane holds NO worktree-registration numerator (0 registrations, so 0 prunable), but it DOES hold the mechanism, on stock defaults, and the default `gc.auto=6700` threshold was crossed inside the probe window (6683 → 6747 loose objects). The next object-writing porcelain command runs `git gc --auto` detached in the background (`gc.autoDetach` default true, `maintenance.auto` default true), which also runs `git worktree prune --expire 3.months.ago` and a repack, while HEAD is detached and the wave is mid-flight. `[INFERENCE]` the repack itself is harmless to reachability; the operability hazard is an unattended background write during integration.

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
(identical four lines)   expire_now_rc=0

$ ls /home/vgpnk/Projects/shokunin/.git/worktrees/*/locked
(all four: No such file or directory)          # 0 locked
$ findmnt -T /fast
TARGET SOURCE         FSTYPE OPTIONS
/fast  /dev/nvme1n1p2 xfs    rw,nosuid,nodev,noatime,inode64,...
$ ls /fast/scratch/hyaku
kaidoku-r34b  kama-r38  kama-r39  kama-r39-closure  kama-r39-fleet  kama-r39b
kumitate-pin  kumitate-r58-close  kumitate-r58-wave        # none of the four registered paths
$ git -C /home/vgpnk/Projects/shokunin config --list --show-origin | grep -icE 'maintenance|gc\.|worktree'
0
```

Both prune invocations were `--dry-run`; nothing was pruned, moved or touched. `/fast` is mounted and `/fast/scratch/hyaku` exists, so the four targets are genuinely gone, not unmounted. The fleet-root repo also carries no maintenance config, so it runs the same defaults.

Saved census bytes: `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-worktree-census.out:21` `default expiry (3.months.ago):      (no output — none prunable)` and `:31-32` `today: 0 prunable, 0 locked, 5 registrations (all 4 extra have live working`.

Entry B at the tip: `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md:73-74` `census (2026-10-23) found **5 registrations, 0 prunable, 0 locked** at` / `every expiry including --expire=now, so the fleet is currently *not*`; `:87` `in S132: 5 registrations, 0 prunable, 0 locked.`; Gate ADMIT reason `:110` describes the census as `a read-only census of the live fleet and not a point-in-time figure`.

### E6 — the lane's frozen counters at the final tip (read-only; informational for the landing gate)

```
tip=0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b   2026-10-25T17:36:28Z

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
claims=3 flags=0                                  k1_rc=0

$ python3 -B tools/souji-coverage-agreement.py --root . --rev 0c92c2e... --base-rev 0eca7c8...
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0     k4_rc=0

$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/git-auto-maintenance-trigger-set.md \
              corpus/knowledge/git-auto-maintenance-trigger-set-r23.md \
    --snapshot-dir census/round-26/sources \
    --slice census/round-26/records/empty-slice \
    --slice-verdicts census/round-26/records/empty-verdicts
FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md check1-no-gate: corpus/knowledge/git-auto-maintenance-trigger-set.md
FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md check1-no-gate: corpus/knowledge/git-auto-maintenance-trigger-set-r23.md
entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2
gate_rc=1

# same command with the two W1 DRAFTS as entries:
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0    draft_gate_rc=0
```

## Findings

1. **Host git is 2.56.0**, matching the expected version (E1). No version-dependent discrepancy in the probe.
2. **The lane repo's effective maintenance config is empty** — the asked grep returns nothing (exit 1), `config --get-regexp '^(gc|maintenance|fetch)\.'` returns nothing, there is no `/etc/gitconfig`, no `include.path`, no `maintenance.repo`, and no `GIT_CONFIG_*` environment override (E2). So defaults govern: `gc.auto=6700`, `gc.autoDetach=true`, `maintenance.auto=true`, `maintenance.autoDetach` falling back to true, and `git gc` invoking `git worktree prune --expire 3.months.ago` (E2 quotes). Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.git/config`, `/home/vgpnk/.config/git/config`.
3. **The lane's own prune numerator is zero but its threshold is crossed.** `.git/worktrees` is absent and `git worktree list` shows only the lane itself (detached HEAD, 0 registrations), so there is nothing for the lane to prune; yet loose objects rose 6683 → 6747 across the probe and now exceed the stock `gc.auto=6700`, with `.git/gc.log` absent and the newest pack from 2026-10-18 (E4). Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.git/`.
4. **The lane is detached from its branch at every sample** — `rev-parse --abbrev-ref HEAD` prints `HEAD`, `master` == HEAD, reflog entries read `export from jj` (E1). `[INFERENCE]` this is the jj export mechanism, not a lost commit; it is still a workspace-state fact the lane's calibre record should not assume away (the prereg header says "branch master").
5. **The installed `man git-fetch` documents `--auto-maintenance`** at section OPTIONS (plain render line 164, `git fetch -h` lines 54-56, roff line 267 escaped) (E3). The generic-string grep of the compressed page fails only because of roff hyphen escaping; the committed snapshot is HTML with the sentence split across lines 3195-3197, so Entry A's Gate quote is whitespace-collapsed-verbatim only. Location: `/usr/share/man/man1/git-fetch.1.gz:267`, `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-26/sources/git-fetch.1.txt:3190-3197`, `tools/souji-gate-check.py:11,54`.
6. **The fleet-exposure numerator in Entry B is stale at probe time, so the "not exposed" clause is false now.** The fleet-root repo lists 5 entries of which 4 are marked `prunable` by `git worktree list`, and `worktree prune --dry-run` reports all four for removal at BOTH the default 3-month expiry and `--expire=now`, with 0 locked; their `/fast/scratch/hyaku/*` targets are gone while `/fast` is mounted (E5). The saved census recorded `0 prunable` on 2026-10-23 on the premise that `all 4 extra have live working` directories. Entry B states `5 registrations, 0 prunable, 0 locked` and `the fleet is currently *not*` exposed, and its Gate reason calls the census `not a point-in-time figure` — it is exactly a point-in-time figure (census date 2026-10-23), and its numerator is now 4. Location: `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md:73-74,87,110`; source `r23-worktree-census.out:21,31-32`.
7. **C2's frozen K2 fails at the final tip (adjacent to my item, decisive for the C2 kill rule).** The pre-registered command run against the two admitted entry paths returns `entries=2 ok=0 fail=2`, rc 1, `check1-no-gate` for both; the committed entries have headings Claim / What this does NOT establish / Lane link and consequence / Freshness only, and point the Gate at `corpus/lessons/round-26.md` (`git-auto-maintenance-trigger-set.md:52`). The same command against the two W1 drafts returns `ok=2`, rc 0 — so the "real gate rc=0" reported in the C2 receipt was produced against drafts, not the admitted paths the frozen command names (E6). Location: `corpus/knowledge/git-auto-maintenance-trigger-set.md`, `...-r23.md`, `tools/souji-gate-check.py:65-75`.
8. **Two C2 receipts named by the frozen RECEIPTS paragraph are absent at the final tip**: `census/round-26/records/c2-gate.tsv` (K2) and `census/round-26/records/c2-k4-after.tsv` (K4 after). K4 itself passes when run at 0c92c2e (`grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0, matching amendment 1), so only the receipt is missing. Location: `census/round-26/records/` at `0c92c2e`.
9. **C1 red receipt revision is not the declared base.** `census/round-26/records/c1-before.tsv` records `rev=12fd90bcd9cdfab495e178023eeaa838a977fcbe`, i.e. the prereg-freeze commit one step after base, not `0eca7c8` as the prereg's red-before command names. Numerically benign — `git diff 0eca7c8 12fd90bc -- SCORECARD.md` is empty, so the counted bytes are identical — but the literal does not match. `c1-after.tsv` records `rev=07f83e69`, and `git diff 07f83e69 HEAD -- SCORECARD.md` is empty, so the green arm does bind the final SCORECARD bytes. Location: `census/round-26/records/c1-before.tsv`, `.ufo/waves/round-26/preregistration.txt` (C1 DO-NOTHING CONTROL).
10. **The C1 protected-span ambiguity was resolved pre-data by amendment 2** (byte-content spans, not line positions), and the landed SCORECARD matches its shape: base lines 1-16 unchanged (no axis-score edit), the r25 and r24 blocks inserted at base line 17, the two r24 capability rows appended in `## Capabilities`, the two planned bullets appended, and the scaffold block deleted (`git diff 0eca7c8..0c92c2e -- SCORECARD.md`: hunks at base 15, 89, 135, 169 only). Recorded here because my probe diff also showed the insertion inside the old positional "1-171" region. Location: `.ufo/waves/round-26/preregistration-amendment-2.txt`, `SCORECARD.md`.

## Attack log

My assigned item is a probe, not an attack, and I changed no frozen predicate, target, case set or axis, and propose none. Two claim-evidence attacks are recorded for the L1 (they are not requests to relax anything; post-data relaxation is not permitted under the AMENDMENT RULES):

- **A1 (against C2's K2 evidence, not its predicate).** The advertised `rc=0` gate run was executed against `.ufo/waves/round-26/w1/entry-*.md` drafts while the frozen command names `corpus/knowledge/*.md`; at the final tip the frozen command returns rc 1 with `fail=2`. Target substitution — the honest options are C2 FAIL as frozen, or a stricter-only amendment that makes the admitted entries carry a Gate section, decided by the L1 (owner: the C2 seat plus the L1 landing gate).
- **A2 (against Entry B's census currency).** The claim `5 registrations, 0 prunable, 0 locked` plus `the fleet is currently *not*` exposed, and its Gate reason `not a point-in-time figure`, are contradicted by a read-only re-measurement two days later: 4 of 5 registrations are prunable at the default expiry and at `--expire=now`, 0 locked. The exposure is live without any config change, because both repos run stock defaults. A stricter-only fix is to date the sentence and add the re-measurement; the alternative is to drop the currency clause.

## Housekeeping

- Tool installs/upgrades: none (no pacman, no uv/npx, no binary fetched; nothing was needed).
- Scratch: none created; `/var/tmp/souji-r26-LabGitVersion` does not exist.
- Writes: this report only. Every lane and fleet command was read-only (`log/show/diff/status/ls-tree/cat-file/rev-parse/config/worktree list`, `count-objects`); the two `worktree prune` invocations were `--dry-run` and pruned nothing. Lane Python ran with `python3 -B`.
