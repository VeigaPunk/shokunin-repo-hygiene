# ExecReadmeMap — round-27 w1 report

## Status

STATUS: PASS — coverage-map draft delivered at `.ufo/waves/round-27/w1/readme-map.md`: F4 row (entries + status cells) and Frontier F4 `next` line quoted verbatim from `corpus/README.md` and replaced with exact lines matching the round's landing (candidate, admission pending closure; record format/staging tool changes stay operator decisions). No lane files written outside my report directory; read-only on the lane and on `/home/vgpnk/Projects/shokuknow`.

## Evidence

- `read .ufo/waves/round-27/preregistration.txt` (rev e78ac7c4837b81b634db4a927605a751a7f006ba): C2 counters "registry rows ... 132→135; grounded F4 `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l` 2→4; gate ... entries=2 ok=2 fail=0; round-end `sources-census.sh validate ...` rc 0"; kill rule id-collision.
- `read corpus/README.md:raw:42-43` (current F4 row, verbatim): `| F4 restorable quarantine, file-system semantics | frontier; layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md` |`.
- `read corpus/README.md:raw:49-50` (current Frontier F4 line, verbatim): `- F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator. *(r22: the primitive and the record's read side are now admitted — see § Round22 attempt 2; the record format and any staging tool change remain the operator's decision.)*`.
- `grep -rlE '^ground: F4' corpus/knowledge/` → `quarantine-staging-no-copy-r23.md`, `quarantine-origin-record-fields-r24.md` (the two grounded entries at base; matches `records/c2-before.tsv` grounded_f4=2, rows=132, gate_tool_present=absent).
- Staged-package sources exist at `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/origin-record-writer-r27.md` and `origin-record-mechanism-set-r33.md` (read-only listing; both files present).
- Consequently: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` shows lane HEAD `e78ac7c…`; no corpus changes by me.

## Findings

1. **F4 row, `corpus/README.md:42`** — entries cell gains `` `knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md` ``; status cell becomes "frontier; candidate, admission pending closure — layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2); origin-record writer + mechanism set re-grounded r27 (see § Round27)". Exact replacement in readme-map.md.
2. **Frontier F4 line, `corpus/README.md:49`** — `next` text becomes: record format (per-item origin records, trashinfo-style) and any staging tool change (`mv --no-copy`) remain operator decisions; origin-record writer + mechanism set re-grounded r27 candidates, admission pending closure (see § Round27). r22 footnote retained. Exact replacement in readme-map.md.
3. **Status-cell precedent** — "candidate, admission pending closure" mirrors the r17 F1-jj row `corpus/README.md:216` ("Core (candidate, admission pending closure)"); F4 stays frontier, so the phrase follows "frontier;" in the status cell.
4. **Coverage-agreement coupling** — once the two entries land with `ground: F4` lines, `tools/souji-coverage-agreement.py` (MISSING-FROM-MAP) requires both paths in the F4 row's entries column; the replacement satisfies it and brings grounded-F4 2→4. The "§ Round27" anchors require the appended Round 27 section; if none is appended, drop/replace the parentheticals (noted in readme-map.md). Apply in the same commit as the entries (Q56 precedent, `corpus/README.md:541`).

## Attack log

None — this seat is not an attack item; no counter/predicate disputed.
