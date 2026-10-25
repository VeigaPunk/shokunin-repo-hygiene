## Status
STATUS: PASS — drafted S152/S210/S211 registry continuation, F4 path, search log, and explicit no-existing-row-change record.

## Evidence
- Read frozen contract `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt` first; C2 requires S152/S210/S211 and no change to existing status/recheck/used-by was expected.
- Read current registry tail `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` lines 150–205 for 11-column table and `## Paths` / `## Search log` continuation conventions.
- Grounding source: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/ExecAssimMirror.md` lines 9–12 contains the normalized three rows. Its quoted evidence states: “GLib's local-file trash writes the record exclusively, never overwrites, writes before payload move”.
- Search log and path input: `w1/ExecSearchLogRow.md` lines 9–13 and `w1/ExecPathsStudy.md` lines 5–12; `w1/search-log.md` lines 5–12 and `w1/paths-study.md` line 1.
- Delivery: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/w1/sources-add.md` (new). No lane corpus file modified; no checks were run by this scribe.

## Findings
1. Draft contains the three supplied normalized 11-column rows; all are `mined`, opened `2026-10-25`, recheck `365d`, and used-by points to the two admitted knowledge entries.
2. Added F4 path S022 → S152 → S210 → S211 and the bounded GLib tag 2.84.0 search block (2 identified, 2 screened, 2 included, 0 excluded).
3. Explicitly recorded: no status, recheck, or used-by changes to existing registry rows this round.

## Attack log
None assigned. No predicate, target, counter, or case set changed.
