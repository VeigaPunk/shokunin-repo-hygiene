## Status
STATUS: PARTIAL — F4 coverage-map row updated; entries are absent at this observation, so instrument output against a committed candidate is unavailable.

## Evidence
- Base revision: `3a2a80d0d18940a5e352ebc526da22a57dad83c4`; current HEAD observed: `0c96332932e66bbaf9cf1c246091d3275a0ab612`.
- Old row bytes (README line 42 at base): `| F4 restorable quarantine, file-system semantics | frontier; layout and staging held; read-side fields admitted r24; reference writer + mechanism set admitted r27 (implementation evidence only) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md`, `knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md` |`
- New row bytes add only the two requested entries at the end of the entries cell; frontier/status unchanged: `| F4 restorable quarantine, file-system semantics | frontier; layout and staging held; read-side fields admitted r24; reference writer + mechanism set admitted r27 (implementation evidence only) | `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md`, `knowledge/quarantine-staging-no-copy-r23.md`, `knowledge/quarantine-origin-record-fields-r24.md`, `knowledge/origin-record-writer-r27.md`, `knowledge/origin-record-mechanism-set-r33.md`, `knowledge/origin-record-exclusivity-r28.md`, `knowledge/origin-record-durability-r28.md` |`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short -- corpus/README.md .ufo/waves/round-28/w1/SwarmExecutor10.md corpus/knowledge/origin-record-exclusivity-r28.md corpus/knowledge/origin-record-durability-r28.md` → `M corpus/README.md`; the two named lane knowledge files and report did not exist in the observed status.
- Source package files opened read-only at `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/origin-record-exclusivity-r28.md` and `.../origin-record-durability-r28.md`; they are staged-package material, not lane files.
- Agreement instrument was not run: it accepts committed revision bytes (`--rev` full durable commit), and neither the F4 entries nor a committed candidate were available to this seat.

## Findings
1. Updated only `corpus/README.md` F4 map row to append the two requested paths; frontier row/status preserved. Location: `corpus/README.md:42`.
2. Instrument result pending landing of entries and their same-commit map update. Do not infer grounded=6/mapped=6 from this row alone.

## Attack log
None.
