STATUS: DONE — inherited-state evidence captured; the observed checkout was already mid-round-19, not a clean preregistration-base tree.

# Findings

- Calibration is preregistered as the lowest non-retired axis (7); operability and coverage are 8 (`.ufo/waves/round-19/preregistration.txt:5`). Its stated base is `3ab2c81479f5004c8bc91946eea482caec45408f` (`.ufo/waves/round-19/preregistration.txt:3`).
- At the first branch check, `git rev-parse HEAD` returned `7d199d2b2446cac1a0c6d08c53e1e950e99bec35`; `git rev-parse --abbrev-ref HEAD` returned `HEAD`; `git status --porcelain=v1 --branch` began `## HEAD (no branch)`. The separate remote-ref check returned `origin/master` = `7d199d2b2446cac1a0c6d08c53e1e950e99bec35`. The worktree was detached at that observation.
- The lane advanced while I checked it (`7d199d2` → `c6703da` → `2efadf6` → `bbeb73b`). Final atomic ref snapshot at `2026-10-21T03:23:11-03:00`: `HEAD=bbeb73bd4dad181b9b293b242dbf5749acbe3568`; `refs/heads/master=bbeb73bd4dad181b9b293b242dbf5749acbe3568`; `refs/remotes/origin/master=bbeb73bd4dad181b9b293b242dbf5749acbe3568`. Thus those three refs were equal at that snapshot. The configured remote was `origin https://github.com/VeigaPunk/shokunin-repo-hygiene.git` for both fetch and push. Earlier, at the `c6703da` snapshot, `git log 3ab2c81..HEAD` counted 15 commits and `git log HEAD..3ab2c81` counted 0; the lane had already advanced beyond the preregistered base.
- The watchdog launch entry for this round is exactly `2026-10-21T00:38:34-03:00 launch souji round=19 pgid=2971251 driver=hyaku-inline attempt=1` (`/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:529`).
- The operator sweep path existed as a directory; metadata-only `stat` returned `/home/vgpnk/Projects/shokunin/souji-shokunin/census/operator-sweep-20261019|directory|2026-10-19 22:46:54.812526839 -0300`. Porcelain showed `?? census/operator-sweep-20261019/`. I did not list or read its contents.
- Round-19 author leftovers were **not absent** in the observed checkout. First captured porcelain included untracked `MutCarryEllipsis.md` and `ScribeSources.md`; the later exact snapshot below includes round-19 reports and generated records, and modified round-19 files. I cannot determine from Git status alone whether each report was stale or in-flight. This contradicts a clean/no-leftovers inheritance claim; it is not evidence that the files were stale.

First captured `git status --porcelain=v1 --branch` output:
```text
## HEAD (no branch)
?? .ufo/waves/round-19/w1/MutCarryEllipsis.md
?? .ufo/waves/round-19/w1/ScribeSources.md
?? census/operator-sweep-20261019/
?? tools/__pycache__/
```

Exact latest captured `git status --porcelain=v1` output (2026-10-21T03:23:11-03:00; captured before writing this report):
```text
 M .ufo/waves/round-19/w1/ScoutProcFd.md
 M census/round-19/run-acceptance.py
?? .ufo/waves/round-19/w1/ConnEvidenceLayout.md
?? .ufo/waves/round-19/w1/ConnRevPinSiblings.md
?? .ufo/waves/round-19/w1/CriticRoundAdmission.md
?? .ufo/waves/round-19/w1/RevHeadIntent.md
?? .ufo/waves/round-19/w1/RevProcEntry.md
?? .ufo/waves/round-19/w1/RevRevPin.md
?? .ufo/waves/round-19/w1/ReviewerGateBaseline.md
?? .ufo/waves/round-19/w1/ReviewerWavePlan.md
?? .ufo/waves/round-19/w1/ScoutAuditSignal.md
?? .ufo/waves/round-19/w1/ScoutCarryReplay.md
?? .ufo/waves/round-19/w1/ScoutDefects.md
?? census/operator-sweep-20261019/
?? census/round-14/__pycache__/
?? census/round-19/final-verification-bbeb73b.json
?? census/round-19/gate-replays-final-bbeb73b.json
?? tools/__pycache__/
```

# Evidence

- `.ufo/waves/round-19/preregistration.txt:3-5` — preregistered base and axis values.
- `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:529` — exact Souji round-19 launch entry, attempt 1.
- Git command outputs recorded above — detached first observation, ref equality in the final atomic snapshot, and complete porcelain snapshots. `git remote -v` returned the origin URL stated above.
- `stat` inspected only the operator sweep directory metadata; no contents were opened.

# Commands run

Read-only commands: `git rev-parse HEAD`; `git rev-parse --abbrev-ref HEAD`; `git rev-parse 3ab2c81479f5004c8bc91946eea482caec45408f`; `git status --porcelain=v1 --branch`; `git remote -v`; `git rev-parse refs/remotes/origin/master`; `git rev-parse refs/heads/master`; `git log --oneline -n 6`; `git log --oneline 3ab2c81..HEAD`; `git log --oneline HEAD..3ab2c81`; `git status --porcelain=v1`; `date --iso-8601=seconds`; and `stat -c '%n|%F|%y' census/operator-sweep-20261019`. Also read the preregistration and watchdog log, searched the watchdog log for the exact launch entry, and listed directory names to locate the logs and round-19 report area.

# Contract compliance

No Git/JJ mutation, signal, test, install, or sweep-content read was performed. The operator sweep directory was only observed through porcelain and metadata. This report is the only file written by this seat.