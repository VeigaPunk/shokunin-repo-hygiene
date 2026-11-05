# Skip-worktree concealment — a receipt instrument's digest must come from its committed blob, not the file on disk

ground: F1 — git-native housekeeping vs receipts (the instrument-digest binding a receipt's `instrument_sha256` must answer to: the committed blob at its revision; extends `knowledge/freeze-record-substance-binding.md`)
source: S291 — git-update-index(1) `--skip-worktree`, section "Skip-worktree bit" (https://git-scm.com/docs/git-update-index; accessed 2026-11-05; located quotes QUOTE-PLACEHOLDER-3 and QUOTE-PLACEHOLDER-4 in `corpus/SOURCES.md`)
verified-at: 2026-11-05 — S291 opened this round; its located quotes are pending the scout capture
recheck: 180d — `MANWIDTH=100 man git-update-index | sed -n '/Skip-worktree bit/,/SPLIT INDEX/p'` after a git release

# A skip-worktree tracked instrument can differ from its committed blob with no status line the writer reads

## Claim (F1, sourced in part)

`tools/souji-receipt-write.py` (r60) writes `instrument_sha256` for the instrument a receipt names. The
r60 fixture did not discriminate a writer that digests the WORKTREE file instead of the committed blob at
the receipt's revision (named r60 limit). The r61 fixture adds a `concealed-divergence` case:
`git update-index --skip-worktree <instrument>` after the instrument is modified in the worktree. The
honest writer must refuse, because worktree bytes differ from the committed blob at the revision; the
concealing mutant emits a receipt with the worktree digest.

What the manual sources (S291, section "Skip-worktree bit"):

- The bit makes Git ignore the absence of the file, avoid updating it when possible, and not record its
  absence in commits. Git commands also avoid treating the lack of such files as an intentional deletion.
- The bit's goal differs from assume-unchanged, which leaves a file in the worktree and has Git omit
  checking it for changes. The two bits are not interchangeable for a check.

What the manual does NOT say: that a modified skip-worktree file is absent from `git status --porcelain`.
That status-silence reading is [INFERENCE] until the round's concealment probe (`census/round-61/`)
reproduces it. The writer must not depend on it either way: it compares bytes directly.

## Writer rule

- Digest the committed blob at the revision (`git cat-file blob <rev>:<instrument>`), never the worktree file.
- Compare the worktree file with that blob (`git hash-object <worktree-path>` against
  `git rev-parse <rev>:<instrument>`) and refuse on inequality, whatever `git status` prints.
- A clean `git status --porcelain` is not proof that the worktree equals the committed blob.

## What this does NOT prove

- **Equality is not correctness.** A committed blob equal to the worktree shows the bytes agree. It does
  not show the instrument ran correctly or that the named command ran at all.
- **One bit, one path.** A check built for skip-worktree does not cover assume-unchanged; that state
  needs its own case.
- **The bit can change.** The manual states that under sparse checkout a skip-worktree file found in the
  worktree has the bit cleared. The writer reads bytes at write time, never trusts the bit's state.
- **The fixture covers one route.** `concealed-divergence` kills the worktree-digest mutant. It does not
  establish the writer against other index-level concealment or against a truthful forgery.

## Decision rule

An instrument digest is bound only when it is the digest of the committed blob at the named revision and
the worktree file equals that blob. A skip-worktree flag, a clean status line or a matching worktree
digest alone does not bind it.

## Round evidence

- The r61 receipt-writer fixture: the r60 cases plus `concealed-divergence` and `partial-visibility`
  (`census/round-61/`). The honest writer passes all ten; the r60 fixture bytes fail both mutants.
- No measured result is stated here; the result is whatever the landed `census/round-61/` bytes show.
