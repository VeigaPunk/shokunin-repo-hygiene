# r12 scout surfaces — souji (transcribed by L1 from R12Scout final output)

Author: W2RoundSouji-8.R12Scout (read-only scout; its role forbade file writes, so the L1
transcribed its final message verbatim into this fragment). Source transcript:
`history://W2RoundSouji-8.R12Scout` (session-scoped; this committed copy is the durable form).
Measured 2026-10-19 ~18:45-18:50 -03:00, lane HEAD dcc8b9e.

### (a) Fleet Git exposure

**Command:** `bash -c` over `/home/vgpnk/Projects/shokunin` and its `*-shokunin` directories. For each repo, the script ran `GIT_OPTIONAL_LOCKS=0 git -C "$repo" worktree list --porcelain`, counted `^worktree`, `^locked`, and `^prunable` lines, and queried the four config keys. Global and system values were queried with `GIT_OPTIONAL_LOCKS=0 git config --global/--system --get`.

**Observed output** (paths and values as printed):

```text
/home/vgpnk/Projects/shokunin	worktrees=6 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/audio-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/chousa-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin	worktrees=5 locked=3 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/game-dev-3d-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kagi-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kaidoku-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kake-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kama-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kasegi-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kengaku-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kotoba-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kotodama-shokunin	worktrees=3 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/kumitate-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/lore-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/mado-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/mori-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/revenger-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/souji-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/tabi-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/tameshi-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
/home/vgpnk/Projects/shokunin/tsukuroi-shokunin	worktrees=2 locked=0 prunable=0	maintenance.auto=unset maintenance.strategy=unset gc.worktreePruneExpire=unset gc.auto=unset
global	maintenance.auto=unset	maintenance.strategy=unset	gc.worktreePruneExpire=unset	gc.auto=unset
system	maintenance.auto=unset	maintenance.strategy=unset	gc.worktreePruneExpire=unset	gc.auto=unset
```

An aggregate count command using the same prefixed `git worktree list` query observed **22 repositories, 52 worktree registrations, 3 locked, 0 prunable**. No queried config value was explicitly set at repo, global, or system scope.

### (b) D7: `game-dev-2d-shokunin` locks

**Command:** `GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin worktree list --porcelain`

**Observed output:**

```text
worktree /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin
HEAD e89905162b3a630a599607279681b30572010724
branch refs/heads/main

worktree /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/game-dev-2d-shokunin
HEAD e89905162b3a630a599607279681b30572010724
branch refs/heads/kaika/round

worktree /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r100
HEAD 2d5622828d6d985d70326367f8023f89f00a02f0
branch refs/heads/wt-r100
locked souji r5: pinned until game-dev-2d pushes wt branches or operator dispositions

worktree /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r98
HEAD 68bee6e7c07638a8abeb2812f249fc382ba7d50a
branch refs/heads/wt-r98
locked souji r5: pinned until game-dev-2d pushes wt branches or operator dispositions

worktree /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r99
HEAD fe1a996ed21fd048558ef31cc1d0c77253404101
branch refs/heads/wt-r99
locked souji r5: pinned until game-dev-2d pushes wt branches or operator dispositions
```

**Verdict:** observed state matches the “3 named-branch registrations PINNED (locks held)” claim in lane `SKILL.md:99–101`. The two other current registrations (main and the Kaika lane) are unlocked. In `LOG.md:135–141`, the history records the three pins, removal of two detached registrations, and an unlock; `LOG.md:205–206` later records the three registrations as “re-locked durably.” Current list: five registrations, three locked. The cited `SKILL.md` text was read from the lane worktree; its last committed revision is `2f303dc6e30d7650e1e513e3cbad75412efdc353`. `LOG.md` is at lane `HEAD` `dcc8b9e8382b74825363c75d641798c81dceb387`.

### (c) ShellCheck exposure

**Command:** `shellcheck -S warning -f gcc` and `shellcheck -S error -f gcc` on each absolute lane-tool path.

**Observed output:**

```text
tools/souji-verify.sh warnings=7 SC2115=0 SC2114=0 warning_exit=1 error_exit=0
tools/souji-vault-verify.sh warnings=9 SC2115=0 SC2114=0 warning_exit=1 error_exit=0
tools/souji-quarantine.sh warnings=9 SC2115=0 SC2114=0 warning_exit=1 error_exit=0
tools/souji-census.sh warnings=0 SC2115=0 SC2114=0 warning_exit=0 error_exit=0
TOTAL warnings=25 SC2115=0 SC2114=0
```

### (d) Filesystem devices

**Commands:** `stat -c '%d %m %n' <listed paths>` and `df -T /home /var/tmp /tmp`. The long `stat` output is trimmed by collapsing the repeated `/home` rows; the exceptions are shown explicitly.

**Observed device groups:** the lane worktree, all 21 `*-shokunin` repo roots, `$HOME/.souji-quarantine`, and `$HOME/.local/share/Trash` each printed device `30`, mount `/home`. `/var/tmp` printed `31 /`; `/tmp` printed `57 /tmp`.

**Observed `df -T` output:**

```text
Filesystem       Type  1K-blocks      Used Available Use% Mounted on
/dev/mapper/root btrfs 974646272 259541140 713602028  27% /home
/dev/mapper/root btrfs 974646272 259541140 713602028  27% /
tmpfs            tmpfs  15860892   1592080  14268812  11% /tmp
```

Same-device pairs among the 24 `/home` paths are on the same mount and support atomic rename semantics. Pairs between those paths and either `/var/tmp` or `/tmp`, and the `/var/tmp`–`/tmp` pair, cross devices; a cross-device `mv` requires copy-and-delete behavior. No moves were performed.

### (e) Host tools

**Commands:** `GIT_OPTIONAL_LOCKS=0 git --version`; `/usr/bin/rm --version | head -1`; `find --version | head -1`; `shellcheck --version`; `command -v` for the listed tools.

**Observed output:**

```text
git: git version 2.55.0
coreutils rm: rm (GNU coreutils) 9.11
findutils: find (GNU findutils) 4.11.0-modified
shellcheck: version: 0.11.0
rmlint: not found
jdupes: not found
fdupes: not found
fclones: not found
czkawka_cli: not found
rdfind: not found
trash-put: not found
gio: /usr/bin/gio
```

**Remaining unknown:** the config queries establish unset values, not the actual runtime behavior of Git’s auto-maintenance defaults; no commit or prune behavior was exercised.
