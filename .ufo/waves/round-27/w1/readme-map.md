# Readme map — round 27 F4 coverage-row update (draft)

Status: draft for L1 integration; not applied to `corpus/README.md`. Quote of the current row text first, then exact replacement lines.

## Current F4 row (`corpus/README.md:42`, verbatim)

```
| F4 restorable quarantine, file-system semantics | frontier; layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md` |
```

## Replacement F4 row (exact)

```
| F4 restorable quarantine, file-system semantics | frontier; candidate, admission pending closure — layout held, staging primitive + record read side admitted r22 (see § Round22 attempt 2); origin-record writer + mechanism set re-grounded r27 (see § Round27) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md`, `knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md` |
```

Changes:
- entries cell gains `knowledge/origin-record-writer-r27.md` and `knowledge/origin-record-mechanism-set-r33.md` (appended after the four existing entries);
- status cell gains the round-outcome phrase "candidate, admission pending closure" (mirrors the r17 F1-jj frontier-row pattern "Core (candidate, admission pending closure)") and the r27 re-grounding clause; the r22 facts ("layout held, staging primitive + record read side admitted r22") are retained.

## Current Frontier F4 line (`corpus/README.md:49`, verbatim)

```
- F4 restorable quarantine — next: per-item origin records (trashinfo-style) and `mv --no-copy` staging are tool changes for the operator. *(r22: the primitive and the record's read side are now admitted — see § Round22 attempt 2; the record format and any staging tool change remain the operator's decision.)*
```

## Replacement Frontier F4 line (exact)

```
- F4 restorable quarantine — next: the record format (per-item origin records, trashinfo-style) and any staging tool change (`mv --no-copy`) remain operator decisions; the origin-record writer and mechanism set are re-grounded r27 candidates, admission pending closure (see § Round27). *(r22: the primitive and the record's read side are now admitted — see § Round22 attempt 2.)*
```

Changes:
- `next` text states the round outcome: record format/staging tool changes stay operator decisions; the two assimilated entries are re-grounded r27 candidates, admission pending closure.
- The r22 historical sentence is kept in the footnote; the duplicated "record format and any staging tool change remain the operator's decision" clause is retired from the footnote (now carried by the `next` text).

## Landing notes

- Apply both replacements at landing in the same commit as the two knowledge entries (Q56 coupling precedent: "The F2 knowledge entry and this map row land together", `corpus/README.md:541`).
- The "§ Round27" anchors resolve only if the Round 27 appended section exists; if the L1 does not append one, replace the parentheticals with "(C2, round 27)".
- Cover the coverage-agreement tool: once `knowledge/origin-record-writer-r27.md` and `knowledge/origin-record-mechanism-set-r33.md` land with `ground: F4` lines, `tools/souji-coverage-agreement.py` requires both paths in some `ground | status | entries` table (MISSING-FROM-MAP); this replacement satisfies it. With the two new `ground: F4` entries, the grounded-F4 counter (`grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`) goes 2 → 4 (before: `quarantine-staging-no-copy-r23.md`, `quarantine-origin-record-fields-r24.md`; see `.ufo/waves/round-27/records/c2-before.tsv`).
- Do not alter the F4 `ground` name ("restorable quarantine, file-system semantics") — it must match the new entries' `ground: F4` labels.
