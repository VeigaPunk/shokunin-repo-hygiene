source: S291 — git-update-index(1) `--skip-worktree` (https://git-scm.com/docs/git-update-index, NOTES; accessed 2026-11-05; located quote in `corpus/SOURCES.md` S291 row); probe on git 2.56.0 (round 61, `.ufo/waves/round-61/w1/S61ReviewerC2.md`)
verified-at: 2026-11-05 (round 61; host git 2.56.0)
recheck: `git -C <scratch-repo> update-index --skip-worktree <file>` after editing that file, then `git -C <scratch-repo> status --porcelain` — the probe output must still show the file as clean, and `git ls-files -v <file>` must show `S`

# A silent `git status` does not certify a receipt instrument's worktree bytes

ground: F4-adjacent — receipt instruments read from the worktree versus the committed blob (`knowledge/freeze-record-substance-binding.md` names the committed-blob digest as the binding)

## Claim

A receipt writer that refuses on `git status --porcelain` to detect a dirty tree can be blinded. Setting the
skip-worktree bit on a tracked file makes Git stop reporting its worktree content, so a modified instrument
can look clean while its worktree bytes differ from the committed blob.

## Manual

The manual gives the bit a goal different from assume-unchanged, and states the limit directly:
"This does not work as expected, since Git may still check working tree files against the index when
performing certain operations." (S291 NOTES). The manual therefore gives no guarantee that status stays silent.

## Measured (round 61, reviewer probe, not a frozen claim)

- A tracked `tracked.txt` edited after `git update-index --skip-worktree tracked.txt`: `git status --porcelain`
  prints nothing; `git ls-files -v` shows `S`.
- The r60 receipt writer (`tools/souji-receipt-write.py`, dirty check at line ~131) accepted the receipt for a
  file whose worktree bytes differed from HEAD, exit 0; the receipt named the worktree content, not the commit.
  Reviewer finding HIGH-1, `.ufo/waves/round-61/w1/S61ReviewerC2.md`.
- The writer's byte comparison (line ~173) covers only the declared instrument, so the blinding reaches any
  other tracked file the receipt depends on.

## Consequence

A dirty-tree refusal based on `git status` is not evidence that the committed bytes were measured. A stronger
writer compares the worktree bytes of every file it reads with `git cat-file blob <rev>:<path>`, or refuses
any skip-worktree or assume-unchanged entry (`git ls-files -v` lowercase or `S`). Neither is implemented in
round 61: this is named and routed to round 62, not claimed.

## What this does not prove

- The manual does not enumerate every git command that ignores the bit; the status silence is a version-scoped probe.
- No claim is made about other concealment mechanisms (assume-unchanged, sparse checkout).
