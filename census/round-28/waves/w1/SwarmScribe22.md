## Status
STATUS: PARTIAL — Gate table draft delivered; POSIX candidate snapshots were not reopened independently in this seat.

## Evidence
- Command/tool: read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/records/preregistration.txt` first; read candidate drafts, S119 disposition, local snapshot, staged IDs/collisions, and log-entry draft; wrote `census/round-28/records/gate-table-draft.md`.
- S119 snapshot inspection: `grep` equivalent via `functions.grep` found the localized auto-maintenance paragraph at `census/round-28/sources/git-fetch-zh-HANS-CN.html:3117`; quote reproduced in gate table. SHA-256 `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042` is recorded in `census/round-28/records/s119-disposition.tsv:2`; not recalculated here.
- Revision: preregistration identifies base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`; no later revision was read or asserted.

## Findings
1. Gate table covers the two F4 entries (S212–S214), routed S119 S215 decision, and two reject candidates; each decision includes rationale and/or flip. Location: `census/round-28/records/gate-table-draft.md`.
2. S119 disposition says ADMIT and records decision-time URL, 2026-10-25 date, snapshot path, digest, and quote. Location: `census/round-28/records/s119-disposition.tsv:2`.
3. POSIX source URLs, dates, snapshot paths, and quotes are transcribed from the candidate drafts, not independently verified by this seat. Location: `.ufo/waves/round-28/w1/origin-record-exclusivity-r28.md:1-3,52-55` and `.ufo/waves/round-28/w1/origin-record-durability-r28.md:1-2,50-52`.
4. Staged inventory includes S119, S138, S216; collision inventory includes S119. Location: `census/round-28/records/assimilation/staged-ids:11,30,108` and `census/round-28/records/assimilation/collisions:11`.

## Attack log
- None. No counter, predicate, target, or case set challenged.

## Gates
- Not run: no gate, census, fixture, or source-reopen operation performed beyond opening the local S119 snapshot passage.

## Touched surfaces
- Created `census/round-28/records/gate-table-draft.md`.
- Created `.ufo/waves/round-28/w1/SwarmScribe22.md` (this report).

## Out of scope
- No product code or lane state changed; no git/jj operations; no files outside this lane written; no tool installation.