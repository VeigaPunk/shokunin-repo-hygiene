# ScribeSources — souji round 25 W1

Seat: ScribeSources, leaf. Lane base `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`, tip read `6e4737eab43d8fde1b85eb9f57023d29046705b4`. Report and draft only; `corpus/SOURCES.md` untouched. Date 2026-10-25. No tools installed or updated.

## Status

STATUS: PARTIAL — draft updated to preregistration amendment 2, but not validated in scratch after that rewrite. The amendment requires three rows, S124–S126, not the initially assigned two-row S124/S125 draft. It also rejects the initially specified gitglossary entry. Draft: `sources-rows.md`. The separate `ScribeSources-2.md` / `sources-rows-2.md` are the other seat's work and not this report's deliverable.

## Evidence

- Read `.ufo/waves/round-25/preregistration.txt` and amendment 2. Amendment 2 §4 specifies S124 = gitrepository-layout § commondir, S125 = git(1) § GIT_COMMON_DIR, S126 = git-worktree § DETAILS; it rejects the glossary candidate.
- At the lane tip, `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` returned 123; last row is S123.
- Read `.ufo/waves/round-25/w1/ScoutSourcesOpen.md`: S124 quote/URL/date and page hashes are recorded there; it explicitly rejects the glossary definition and records live git, git-worktree, git-rev-parse page access and exact relevant text.
- This seat fetched live `git`, `git-worktree`, `gitrepository-layout` and `gitglossary` HTML with `curl -fsSL`; each returned HTTP 200. `git` and `git-worktree` fetched bytes were identical to ScoutSourcesOpen's copies by `sha256sum`. Decompressed installed roff copies of git(1) and git-worktree(1) likewise matched ScoutSourcesOpen's hashes. `pacman -Qo /usr/share/man/man1/git.1.gz` returned owner `git 2.56.0-1`.
- Confirmed quote text: `git` § GIT_COMMON_DIR in web text; `git-worktree` § DETAILS in web text and installed roff; `gitrepository-layout` § commondir in web, installed roff and tag source (ScoutSourcesOpen records byte-level agreement and quotes). These are the amendment's three sources.
- gitglossary has no `common` term; ScoutSourcesOpen and ScoutSourcedClaimCheck independently swept live page, installed page and tagged glossary source. S125's initial glossary plan is rejected, not admitted.
- Initial scratch check (before amendment): source rows S124/S125 each had 11 cells; validator with a stub entry exited 0 with 32 W04 (31 baseline + S124/S033); without the entry exit 1 with E11 for both missing `used-by` paths. This does NOT validate the current three-row amendment-aligned draft. Initial scratch paths and logs: `/var/tmp/souji-r25-ScribeSources/validate-{base,noentry,entry}.out`.

## Findings

1. Amendment 2 supersedes the initial two-row task contract: current draft contains S124, S125 and S126. Rows carry status `mined` and the new knowledge-entry path, conditional on that entry landing in the same commit; otherwise rows need `queued` and `—`.
2. The current C3 entry draft under `w1/git-repo-structure-common-dir.md` still cites S125 as gitglossary and does not cite S126. It must be reconciled to amendment 2 before landing. This report does not edit it.
3. S124 shares the URL with S033 under a distinct scope; S125's git(1) URL is already used by S006/S036/S049/S089 under distinct scopes; S126's git-worktree URL appears in S003/S058/S123 under distinct scopes. These are disclosed in the draft; no existing row is altered.
4. Bare source IDs collide with campaign IDs: pre-r25 S124 refers to a staged NOREPLACE probe mapped to lane S109; S126 refers to staged GLib trash mapped to S113. The draft recommends by-document `SOURCES S124` / `SOURCES S126` wording and lesson disambiguation.
5. A `used-by` change log is not expected if the knowledge entry cites only the amended S124/S125/S126 rows. If it additionally cites S123/S089/S035/S054, the existing row's `used-by` must change and be logged old→new.
6. ScribeSources-2 confirmed it restored my original rows after an overwrite; it has kept its final work in `sources-rows-2.md` and `ScribeSources-2.md`. My current draft has now been rewritten in full to align with amendment 2.

## Artifact paths

- Draft: `.ufo/waves/round-25/w1/sources-rows.md`
- Report: `.ufo/waves/round-25/w1/ScribeSources.md`
- Initial validation evidence (pre-amendment only): `/var/tmp/souji-r25-ScribeSources/validate-base.out`, `validate-noentry.out`, `validate-entry.out`.

## Out of scope

No product/corpus registry edits, no changes to the C3 entry, no git/jj mutations, no tools installed, no cleanup outside this seat's scratch lane copies. Current amendment-aligned row set remains unvalidated; do not treat the pre-amendment result as a pass for S124–S126.
