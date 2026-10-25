## Status
STATUS: FAIL — neither staged entry is admission-ready; both fail frozen freshness/Gate/mapping requirements.

## Evidence
- Read `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/origin-record-writer-r27.md` and `origin-record-mechanism-set-r33.md`; staged source rows are in `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`.
- Opened this round: GLib 2.84.0 `gio/glocalfile.c` and `glib/gfileutils.c` raw source URLs cited in S152/S210/S211. The staged entry headers still state verified/opened 2026-10-23 or 2026-10-24, not 2026-10-25.
- Rubric: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md:28,41,128,135` — Q4: “runs only under `/var/tmp`”; Q17: “contained regular, non-symlink file”; Q54 requires “every `§ <NAME>` locator resolve”; Q56 requires a “coverage-map row”.
- F4 map/frontier: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/README.md:42,49` — “per-item origin records (trashinfo-style)” and “record format ... remain the operator's decision.”

## Findings
1. **origin-record-writer-r27.md — needs fixes.** Header lines 2–3 report S152 and `verified-at` as 2026-10-23, although this round's mandated opening occurred 2026-10-25; this does not document this round's re-grounding. No `## Gate` block exists, so it lacks required admit and reject decisions. The claim “at every instant the on-disk state is one of ‘no record, no move’ or ‘record, then move’” and “can never clobber” overstate what the cited single implementation establishes as a universal guarantee; narrow to the observed GLib code path and its shown failure handling. Verdict: **needs fixes**.
2. **origin-record-mechanism-set-r33.md — needs fixes.** Header lines 2–5 cite S210/S211 with opened/verified date 2026-10-24, not this round; no `## Gate` block exists. Body lines 43–49 prescribes that a writer “needs both mechanisms” and speaks of a receipt, but the implementation is evidence about GLib, not a normative design decision for souji (the entry itself disclaims that at lines 53–58). Restate as observed GLib mechanism roles, not a requirement. Its Markdown mechanism table contains literal pipe delimiters; avoid using table text as a source quote, since the quote contract excludes `|`. Verdict: **needs fixes**.
3. **Q56 coverage map absent for both.** The current F4 coverage-map row at `corpus/README.md:42` enumerates four entries and names neither candidate; that same row's status does not meet Q56's required grounded F4 map inclusion. Add both paths to the F4 map in the integrating change.
4. **Q54/Q17 Gate evidence unresolved.** Neither entry has a Gate section or declares snapshot locators, so no Gate admit/reject set or locator resolution can be checked; add Gate decisions for each and ensure any declared snapshots/§ locators resolve to headings in the actual fetched snapshots. Recheck paths/evidence must resolve to contained regular non-symlink files at the measured revision (Q17).

## Attack log
None.