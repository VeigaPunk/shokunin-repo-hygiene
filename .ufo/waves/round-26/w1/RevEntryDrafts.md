## Status
STATUS: PARTIAL — Entry A is admit-ready; Entry B has a required source-locator correction.

## Evidence
- Read frozen contract and amendment 1: `.ufo/waves/round-26/preregistration.txt` (C2 rows 75–100, 130–136); `.ufo/waves/round-26/preregistration-amendment-1.txt` lines 1–19.
- Read registry mapping: `corpus/SOURCES.md` rows S128–S132 (lines 149–153).
- Read both drafts and Gate sections. Revision reviewed: current lane worktree; frozen lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`.

## Findings
1. Entry A (`entry-git-auto-maintenance-trigger-set.md`): admit-ready. Its source IDs map to fetch docs (S128), builtins (S129), and pull.c (S130); all Gate quotes are located snapshots and <=25 words. Front matter includes `source:`, `verified-at:`, `recheck:`; `ground: F1` is present. All cited IDs are appended, and no claim depends on a non-appended row.
2. Entry B (`entry-git-auto-maintenance-trigger-set-r23.md`): defect at line 1. S131 correctly maps to the trigger fixture, but the citation must be re-pointed to S132 (worktree census) without naming the unadmitted file, as required by frozen C2 lines 83–89. The current line instead identifies S131 as fixture; it does not cite the required S132 census at the source-line level. Remaining S128–S130 mappings are correct; front matter trio and `ground: F1` are present. Its Gate's census evidence is identified by source path, not a >25-word quotation; no Gate quote-length violation observed. Fixture/census are both appended rows.

## Attack log
None.