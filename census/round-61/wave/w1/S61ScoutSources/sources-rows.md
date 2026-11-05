Two SOURCES.md registry rows in the lane's exact 11-column shape
(`| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`),
to be inserted after the S289 row in `corpus/SOURCES.md`.

The scribe's draft (`.ufo/waves/round-61/w1/S61ScribeCorpus/sources-rows.md`) carries four
`QUOTE-PLACEHOLDER-<n>` markers. The filled values for those markers, taken from this seat's
captures, are:

  QUOTE-PLACEHOLDER-1 (S290 access record)
    git-log(1) OPTIONS `--diff-filter=[(A|C|D|M|R|T|U|X|B)...[*]]`, section DIFF FORMATTING,
    anchor id `Documentation/git-log.txt---diff-filterACDMRTUXB`; web manual "git-log last updated
    in 2.56.0"; page served 2026-11-05, curl -sSL HTTP 200, 375834 bytes, sha256
    `f206647fba42b627f46d29993490fbb585adedaa5d27b9ed575f50ef9002f69b`, capture
    `census/round-61/sources/s290-git-log.html`; host git 2.56.0

  QUOTE-PLACEHOLDER-2 (S290 located quote)
    "Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)"
    (15 words)

  QUOTE-PLACEHOLDER-3 (S291 access record)
    git-update-index(1) OPTIONS `--skip-worktree` / `--no-skip-worktree`, section SKIP-WORKTREE BIT,
    anchor id `Documentation/git-update-index.txt---skip-worktree`; web manual "git-update-index last
    updated in 2.52.0" (2.53.0 -> 2.56.0 no changes); page served 2026-11-05, curl -sSL HTTP 200,
    84442 bytes, sha256
    `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8`, capture
    `census/round-61/sources/s291-git-update-index.html`; host git 2.56.0

  QUOTE-PLACEHOLDER-4 (S291 located quote)
    "the object names recorded for the paths are not updated. Instead, these options set and unset
    the \"skip-worktree\" bit for the paths." (22 words)

Filled rows (11 columns each; the `teaches` cell keeps the scribe's wording, with the located quote
inlined verbatim):

| S290 | git-log(1) `--diff-filter` — https://git-scm.com/docs/git-log | docs | A | control-chronology add-commit resolution: the commit that ADDS a Control receipt path, read with `--diff-filter=A` | OPTIONS `--diff-filter`; section DIFF FORMATTING; accessed 2026-11-05 (access record: web manual "git-log last updated in 2.56.0", curl -sSL HTTP 200, 375834 bytes, sha256 `f206647fba42b627f46d29993490fbb585adedaa5d27b9ed575f50ef9002f69b`, capture `census/round-61/sources/s290-git-log.html`; host git 2.56.0) | `--diff-filter=A` selects only paths that are Added, so one history query on a receipt path names the commit that created it rather than every commit that touched it (located quote: "Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)") | queued | 2026-11-05 | 180d | corpus/knowledge/control-chronology-binding.md |
| S291 | git-update-index(1) `--skip-worktree` — https://git-scm.com/docs/git-update-index | docs | A | concealed worktree divergence in receipt instruments: a tracked instrument whose worktree bytes differ from its committed blob while its index entry carries the skip-worktree bit | OPTIONS `--skip-worktree, --no-skip-worktree`; section "Skip-worktree bit"; accessed 2026-11-05 (access record: web manual "git-update-index last updated in 2.52.0", curl -sSL HTTP 200, 84442 bytes, sha256 `ecaa637b1f39acc4a5a19729c2119b7a4a92cb9e1a2b4335d9557d0844143fb8`, capture `census/round-61/sources/s291-git-update-index.html`; host git 2.56.0) | the bit makes Git ignore the absence of a file and avoid treating it as an intentional deletion, and the manual gives it a goal different from assume-unchanged (located quote: "the object names recorded for the paths are not updated. Instead, these options set and unset the \"skip-worktree\" bit for the paths."); the manual does not state that a content change is hidden from status, so that effect is a round probe, not a sourced fact | queued | 2026-11-05 | 180d | corpus/knowledge/skip-worktree-concealment.md |

Caveat the L1 must carry into the lesson's `## Gate`: the S291 `teaches` cell says the concealment
effect is a probe result. The manual's own NOTES section says of the skip-worktree bit that "This
does not work as expected, since Git may still check working tree files against the index when
performing certain operations" — the page is not a guarantee that `git status --porcelain` stays
silent. The r61 probe (git 2.56.0, this host) showed exactly that silence for a modified tracked
file whose index entry carries the skip-worktree bit; that is a round observation, not the manual's
promise, and it is version-scoped.
