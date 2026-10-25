# SwarmScribe26 — report (wave 1, round 28)

## Status
STATUS: PASS — deliverable `census/round-28/records/paths-draft.md` written (F4 Paths bullet extended S022→S152→S210→S211→S212→S213→S214 with one-line reason; two Search-log bullets pasted from Exec-C2SearchLog's `searchlog-draft.md`).

## Evidence
- `read` frozen `census/round-28/records/preregistration.txt` (raw lines 5-9): C2 texts — S212=open(), S213=rename(), S214=fsync(), status=mined, used-by exactly the admitted entries; S119 zh-Hans dispose rule (ADMIT → S215); counters 135→138 rows.
- `read` `corpus/SOURCES.md:165` (§ Paths, current F4 line, verbatim): `F4 origin-record writer and mechanism — S022 → S152 → S210 → S211: the FreeDesktop specification gives the record contract first; GLib's writer grounds the per-item sequence; the descriptor lifecycle separates reservation from content writing; the file-content helper shows temporary-file publication as a distinct implementation mechanism.`
- `read` `corpus/SOURCES.md:167-199` (§ Search log tail: last entry Round-25 at line 197; § Leads (unopened) at line 199 — additions insert between).
- `read` staged package entries `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/origin-record-exclusivity-r28.md` and `origin-record-durability-r28.md` (ground: O_EXCL+rename; fsync durability boundary) — used to word the appended reason.
- `read` `census/round-28/records/searchlog-draft.md` (Exec-C2SearchLog artifact, full raw lines 1-13) — source of the two Search-log bullets, copied verbatim.
- `write` `census/round-28/records/paths-draft.md` (deliverable, 6046 bytes). Sha: 6cc62c8e5cacba9f5a4bfb455766d15ce49931b81749e05ddd8a34d4133ee9b7.
- Read-only seat: no `git`/`jj` mutations; no scratch created; no tool installs (nothing to record under the channel rule).

## Findings
1. Draft replaces the F4 Paths bullet (SOURCES.md:165) with the extended sequence exactly as item dictates — spec first (S022), GLib writer/mechanism (S152/S210/S211), POSIX exclusivity/rename/fsync (S212/S213/S214); reason appended as one line. See `paths-draft.md` § Paths.
2. Staged r28 entries cite package-local ids S158/S159/S173; the draft references the round-28 lane rows S212–S214 per C2 and explicitly notes the row appends are the C2 executor/L1's step, out of scribe scope.
3. Search-log additions are taken verbatim from `searchlog-draft.md` (two paste-ready bullets: F4 re-grounding with 3 identified/screened/included, 0 excluded, sha256 pins, located quotes; S119 ADMIT disposition with decision-time pin, 2.56.0 edition line, negative sweep). [INFERENCE] none — quotes/URLs are the executor's exercised fetches, not re-verified by this seat.
4. Observation: `searchlog-draft.md` header names drafter SwarmExecutor12 while dispatch labels the item Exec-C2SearchLog (SwarmExecutor13); content is the canonical artifact at the seat's designated path — L1 may want to reconcile the seat label.
5. No other files touched; no attack items (scribe seat).

## Attack log
None (no predicate/counter/target objections; item is a draft, not an attack).
