# ScribeSources-2 — souji round 25, wave 1 (S124/S125 rows, Gate, Paths, Search log, change log)

- Seat: L1Souji25.ScribeSources-2 (scribe, leaf, no dispatch).
- Lane HEAD: 6e4737eab43d8fde1b85eb9f57023d29046705b4 (master); base a6d2d15.
- Date: 2026-10-25.
- Draft written: `.ufo/waves/round-25/w1/sources-rows-2.md` (sha256 bf92a952…4588 at write time).
- Not edited: `corpus/SOURCES.md` and every other lane file.
- No git or jj writes.
- Scratch: `/var/tmp/souji-r25-ScribeSources-2/`, removed at finish.
- Tools installed or upgraded: none.

This report is at the `-2` path because the sibling seat L1Souji25.ScribeSources holds the same item and owns `ScribeSources.md` and `sources-rows.md`. Finding 1 covers the collision.

## Status

STATUS: PARTIAL.

The rows deliverable is complete:
- S124 and the primary S125 are drafted in the exact 11-column shape (NF=13), with no literal or escaped `|`.
- Both are tier A docs, `mined` (conditional on the C3 entry landing), opened 2026-10-25, recheck `on-release`.
- The draft also contains two fully formed alternate S125 rows, the Gate quotes, a `## Paths` bullet, a `## Search log` entry and the change log (none required).

PARTIAL because of a seat collision. My rewrite overwrote the sibling seat's `sources-rows.md`. I restored its two rows byte-exact, but its Paths, Search log and change-log sections are lost, and the owner seat has been asked to rewrite them.

## Evidence

- **Fetches** (all HTTP 200, 2026-10-25T12:28Z–12:33Z): `curl -fsSL` of the git-scm.com pages gitrepository-layout, gitglossary, git, git-rev-parse and git-worktree, plus raw.githubusercontent.com git/git `v2.56.0/Documentation/{gitrepository-layout,glossary-content,git,git-rev-parse,git-worktree}.adoc`.
- **Byte agreement with ScoutSourcesOpen**: all 10 files are sha256-identical to ScoutSourcesOpen's copies. Example values:
  - gitrepository-layout.html `ad7b52fb…c64c`
  - gitglossary.html `eb521ce9…c835`
  - git-worktree.html `fa25690b…63d2`
  - git-worktree.adoc `ee8a3685…fe8dc`
  - The full list is in the draft header.
- **Revision pin**: `git ls-remote https://github.com/git/git 'refs/tags/v2.56.0^{}'` returns `a018953688f1b10bddf91bff8747068f5f4746a4`.
- **Installed versions**: `pacman -Q git` returns `git 2.56.0-1`. The rendered man footers read `Git 2.56.0 2026-09-27`.
- **Row shape**: `awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {print NR,$2,"NF="NF}' sources-rows-2.md` printed `27 S124 NF=13`, `28 S125 NF=13`, `38 S125 NF=13`, `44 S125 NF=13`. `grep -c '\\|'` returned 0.
- **Quote check**: after whitespace normalisation, each quote was matched as a substring of the web text, the v2.56.0 adoc and the MANWIDTH=80 man rendering. All 15 checks returned True. Word counts and no-pipe results:
  - S124a: 23 words, no pipe
  - S124b: 12 words, no pipe
  - S125: 13 words, no pipe
  - alternate 1: 25 words, no pipe
  - alternate 2: 23 words, no pipe
- **Negative sweep**: `grep -ci common` returned 0 on gitglossary web text, on the v2.56.0 `glossary-content.adoc` and on the rendered installed page.
- **Next ids**: SOURCES ends at S123 (`corpus/SOURCES.md:143`), so S124 and S125 are the next unused ids.

## Findings

1. **Seat collision.**
   - My first message to L1Souji25.ScribeSources was delivered. Its reply ("output goes to `-2` names", recorded in its `ScribeSources.md` finding 6) never reached this seat.
   - My second write of `sources-rows.md` (about 09:33) overwrote its draft.
   - Remediation:
     - My draft moved to `sources-rows-2.md`.
     - `sources-rows.md` was rebuilt with a provenance note and the owner's two rows, byte-exact from `/var/tmp/souji-r25-ScribeSources/rows.txt` (`cmp` rc 0).
     - The owner was messaged to rewrite its lost sections.
   - The L1 should integrate from the owner's rewritten `sources-rows.md`, or from `sources-rows-2.md`, not from the restored stub alone.

2. **The briefed S125 document has no common-directory entry.**
   - gitglossary(7) at 2.56.0 has no `common directory` / `COMMON_DIR` entry (sweep above).
   - ScoutSourcesOpen (finding 2) and the sibling (finding 1) independently found the same.

3. **The primary S125 is the git-worktree(1) § DETAILS `$GIT_COMMON_DIR` clause.**
   - Location: `Documentation/git-worktree.adoc` L376-377 at v2.56.0, opened live this run.
   - Reason: it is the only opened sentence that grounds C3's measured equality, `probe.git_common_dir == A's resolved git dir` for `--repo B` (prereg L95-97).
   - Overlap: S123 anchors the same sentence, but S123's scope and teaches cover only the private-`$GIT_DIR` clause, so S125's scope cell excludes that clause.
   - Alternates in the draft:
     - Alternate 1, git(1) GIT_COMMON_DIR. This is ScoutSourcesOpen's recommendation. ScoutSourcesOpen did not check S089 (`corpus/SOURCES.md:109`), which already anchors `GIT_COMMON_DIR` ("GIT_COMMON_DIR and GIT_INDEX_FILE redirect their respective stores"). I narrowed alternate 1's scope to the worktree-specific split so it does not duplicate S089.
     - Alternate 2, the gitglossary § worktree entry. This matches the sibling's S125. It overlaps no row, but it names no directory, so it grounds neither C3 case.

4. **S124's teaches cell no longer claims anything about linked worktrees.**
   - § commondir (adoc L268-273) never mentions linked worktrees; ScoutSourcesOpen attack A2 makes the same point.
   - My first draft said "so a linked worktree's private gitdir alone is not the whole repository". The final cell states only the page's two facts: the pointer and the incompleteness. Linked-worktree resolution is S125's job.

5. **git-worktree § DETAILS gets the storage mechanism wrong for linked worktrees.**
   - The page says both settings "are made in a .git file" (adoc L377-378).
   - The common-dir pointer actually lives in the private gitdir's `commondir` file. ScoutSourcesOpen's host run observed `commondir: ../..` (an observation, not a source), and S124 documents the file.
   - S125's scope therefore excludes the storage mechanism.

6. **The web page for S124 carries an older stamp.** It reads "gitrepository-layout last updated in 2.49.0" (2.49.1 → 2.56.0 no changes), so the anchor states this. The 2.56.0 claim rests on the v2.56.0 adoc and the installed page.

7. **The glossary's per-worktree ref list is stale.** Its `per-worktree ref` entry (`glossary-content.adoc` L496-500, v2.56.0) names only HEAD and `refs/bisect/`, narrower than git-worktree § REFS (S123). Alternate 2's scope excludes the ref list for that reason.

8. **The bare id S124 is already used elsewhere.** It appears at `corpus/lessons/round-22.md` L323, L352, L363 and L432, and at `corpus/lessons/round-24.md` L234 (`rg -n -o '.{0,25}S124.{0,15}'`). The lesson, entry and README should write `SOURCES S124` / `SOURCES S125`, which is the same class of fix as prereg D5.

9. **Change log: none required.**
   - If the landed C3 entry also cites S123 or S089, that row's `used-by` gains `corpus/knowledge/git-repo-structure-common-dir.md`, logged old→new.
   - The current values are S123 `corpus/knowledge/count-objects-linked-worktree-garbage.md` and S089 `corpus/lessons/round-20.md`; the exact strings are in the draft.
   - Both new rows are `mined` only if that entry lands; otherwise use `queued` and set `used-by` to the round-25 lesson only.

10. **git-rev-parse `--git-common-dir` is left as a lead.**
    - Quote: "Show $GIT_COMMON_DIR if defined, else $GIT_DIR." (adoc L267-268).
    - It is the probe's exact call (`tools/souji-repo-structure.sh:193`), but the page is already registered (S079/S091/S099, other scopes), and a third row is outside the S124/S125 frame the prereg names (L106-110).

## Attack log

- **A1, on the brief:** S125 "must define the common directory" from gitglossary cannot be met at 2.56.0; the 0-match sweep covers three copies. No prereg predicate is changed; prereg C3 names only "S124/S125 opened this round", not documents.
- **A2, on the brief:** "S124 grounds where the git dir of linked worktrees resolves" overstates § commondir. That claim is moved to S125 (git-worktree § DETAILS clause).
- **A3, against the scout's recommended replacement:** git(1) GIT_COMMON_DIR as S125 would re-anchor S089's variable. It is kept only as a scoped alternate.

## Checks for the L1

Recheck these after integration:
- The awk NF census over `corpus/SOURCES.md` must print 0.
- `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` must give 125.
- The lane source validator (the sibling reports rc 0 with the entry present, and E11 without it).
- Exactly one S125 row is appended.
