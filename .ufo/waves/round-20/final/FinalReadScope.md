# FinalReadScope — pinned build 1988860

STATUS: PARTIAL — the ConsumerSkill report discloses its repository-root recursive `grep` but omits a preceding repository-root `glob`. Q45 makes both implicit root expansions scope violations, so the report's independent source-review conclusion is void as seat evidence and must be retained only as a named-file re-derivation below. This critic used only the specified pinned Git blobs; no actual protected subtree was accessed.

## Axes

- **Calibration (primary):** incomplete disclosure of a source-scope violation weakens the audit record and any independent credit assigned to that seat.
- **Operability (evidence provenance, secondary):** the report's no-defect conclusion is supportable only as a bounded source observation, not as runtime verification.
- **Coverage:** not implicated; this item makes no coverage claim.

## Counterexample and exact evidence

At pinned `census/round-20/transcripts/recovery/ConsumerSkill.txt:47-50`, the rendered calls include:

> `→ glob(/home/vgpnk/Projects/shokunin/souji-shokunin) ⇒ ok · 129 lines`
>
> `→ grep(souji-rev-pin|souji-seat-audit|count-claims|counter|recheck @ /home/vgpnk/Projects/shokunin/souji-shokunin) ⇒ ok · 415 lines`

The intervening two grep calls shown in the same excerpt target named `tools/` paths; the root `glob` and root `grep` are the deviations. `census/round-20/recovery/ConsumerSkill.md` (Residual risk and verification gaps; cited as line 20 by the round lesson) acknowledges one recursive repository-root `grep`, says its output is not used, and says no further repository-wide search occurred; it does not disclose the earlier root `glob`. Thus the issue is a concrete undercount in the report, not a claim that the hidden grep/glob output proves a product defect.

Separately, pinned `census/round-20/coordinator-start-excerpt.txt:43` records the coordinator's bare lane-root read, rendered as `→ read(/home/vgpnk/Projects/shokunin/souji-shokunin) ⇒ ok · 80 lines`. `census/round-20/coordinator-scope-deviation.json` explicitly records nested child-name/metadata exposure including the excluded operator-sweep directory name, and says no file inside it was opened. This is a confirmed Q45 deviation, not a clean metadata-only exception.

Pinned `corpus/QUALITY.md`, Q45, states that protected-subtree scope includes implicit directory expansion; a metadata-only exposure is disclosed; affected evidence is void and re-derived from named files; the oracle must flag root read/glob/grep calls, without probing the real protected tree.

## Void / re-derived boundary

- Void the ConsumerSkill root-glob/root-grep output as evidence, along with any seat-level conclusion that depends on those results. The report's claim that it did not use the grep output does not account for the omitted glob or replace Q45's required disposition.
- Re-derived narrowly from the allowed pinned `SKILL.md` and `corpus/README.md`: the SKILL points current historical-counter use to the Round 20 full-ID index, and the README's current counter examples use full-length IDs. This is a source-only observation of those named bytes, not a fresh resolution/reachability check of the IDs, a runtime refusal/pass, or proof of complete C2 input binding.
- The coordinator deviation's own disposition is appropriately explicit: its root listing is not used as claim evidence and relevant facts are re-derived from named files. This review independently read only those named pinned blobs and the deviation record; no file below `census/operator-sweep-20261019/` was opened or accessed.

## Smallest safe correction

Keep the transcript and report immutable. Append a correction to the round-20 deviation disposition identifying the omitted root `glob` at `ConsumerSkill.txt:47` in addition to the root `grep` at `:50`; mark the root-expansion-derived seat evidence void, and retain only the bounded named-file re-derivation above. Do not infer that protected file contents were actually read: the rendered evidence establishes implicit expansion and possible protected traversal, while the coordinator record specifically says no interior file was opened. No real protected-tree probe is warranted or was performed.

## Evidence boundary

Read-only inspection was via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<named-path>` for the exact files cited above. No target code, tests, builds, linters, formatters, smokes, census, or other runtime operations were run.