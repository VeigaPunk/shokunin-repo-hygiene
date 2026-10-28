source: S231 souji r35 fleet prune census — census/round-35/records/prune-census.tsv (sha256 8b37041ac1a954263c6f4e665a8105d37ac342c802fb11f596aadb69ec257177, run 2026-10-28, git 2.56.0); S232 git-worktree(1) § LIST OUTPUT FORMAT, `prunable` attribute (https://git-scm.com/docs/git-worktree; installed man page git 2.56.0-1, snapshot census/round-35/sources/git-worktree.1.txt)
verified-at: 2026-10-28 — git 2.56.0-1 on kernel 7.2.11-arch1-1; read-only (list + `prune --dry-run -v` only; `git worktree prune` was never run)
recheck: 30d — re-run the census: `for d in /home/vgpnk/Projects/shokunin/*/ /home/vgpnk/Projects/shokunin/; do git -C "$d" rev-parse --git-dir >/dev/null 2>&1 && { git -C "$d" worktree list --porcelain | grep -c '^worktree '; git -C "$d" worktree prune --dry-run -v | grep -c .; }; done` (expect regs=27 prunable=0 as of 2026-10-28; a nonzero prunable is a new exposure figure, not a falsification of this one)
ground: F1 — git-native housekeeping vs receipts (the fleet exposure numerator re-census named in the coverage map's F1 row)

# The fleet's live prune numerator is 27 registrations, 0 prunable (2026-10-28)

## Claim (F1, sourced)
A read-only census of every git repository under the fleet root on 2026-10-28
found **27 worktree registrations across 26 repositories and 0 registrations git
would prune today**. The counting command and record are committed:
`census/round-35/records/prune-census.tsv` — one `REPO\t<name>\tregs=\d+\tprunable=\d+`
row per repository plus `TOTAL\trepos=26\tregs=27\tprunable=0`; produced by
`git -C <repo> worktree list --porcelain` (count of `worktree ` records) and
`git -C <repo> worktree prune --dry-run -v` (count of non-empty lines) per repo.
mado-shokunin holds 2 registrations (the only repo above 1); every other repo
holds exactly 1 (its main worktree).

The `prunable` attribute the census reads is defined at git 2.56.0: git-worktree(1)
§ LIST OUTPUT FORMAT says a listed entry is marked `prunable` "if the worktree can
be pruned via `git worktree prune`", and the porcelain record prints the reason —
`prunable gitdir file points to non-existent location` in the manual's example
(snapshot `census/round-35/sources/git-worktree.1.txt` lines ~553-560 and ~625-628;
S232). `prune --dry-run -v` applies the same gate without writing: each printed
line is a registration the real `git worktree prune` would remove.

## Why the earlier figures are stale, not wrong
The merge package's staged entry `fleet-prune-census-drift-r33.md` carries
"40 registrations across 14 lanes" measured 2026-10-24, and an earlier lane
reading carried 16 prunable across 6 lane repos (2026-10-23). Those figures
described their dates: registrations appear and disappear with dispatch
worktrees, and the prunable set drains when the stale gitdir targets get
cleaned or auto-maintenance fires. This entry supersedes them as the current
numerator only; it does not falsify them. The coverage map's F1 row names
"fleet exposure numerator re-census" as the open item — this entry closes it
at this date; `verified-at`/`recheck` bound the claim.

## Boundary and limits
List-only observation: no `worktree prune` (mutating), no `worktree lock`, no
`gc` was run; F5 stays list-only per the round-18 hold. The census covers
registered worktrees only — a pruned-then-recreated registration between
measurements is invisible. `prune --dry-run -v` without `--expire` reports
candidates under the default expiry; at git 2.56.0 a bare `worktree prune`
uses `TIME_MAX` (no age limit) per builtin/worktree.c, so the dry-run set is
the *immediate* prunable set, not the 3-month-aged auto-maintenance set —
an unlocked registration whose gitdir died today still counts. Locked
registrations are never prunable (S003).
