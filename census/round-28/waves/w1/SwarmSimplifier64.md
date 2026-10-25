## Status
STATUS: PASS — wave spec hygiene clean; no violations of the six checks (distinct names, roles, prompt uniqueness, surface+concreteness, no model/routing asks, role counts). 9 items name their surface by unambiguous reference rather than a literal path (low-severity observations, reported for L1 awareness); all referenced pre-existing surfaces exist on disk.

## Evidence
Parser: `python3 -B` reading bytes of `.ufo/waves/round-28/w1-spec.json` (#7142), `w1/swarm-registry.json` (#37FB), `w1-dispatch.json` (this run; no writes).

- Item count: spec 64, registry 64, identical item→role mapping (`spec_items == reg_items` → True).
- Distinct names: 64/64 unique, zero duplicates.
- Role counts (spec, registry agree): executor 20, scribe 8, reviewer 12, critic 6, mutation-tester 6, connector 2, scout 6, sentinel 2, simplifier 2; total 64. Matches wave plan exactly.
- Roles used ⊆ defined role set; no foreign role, no `task` role in this wave (tenth role unused, permitted).
- Identical prompts: 0 (all sha256 digests distinct).
- Model/routing asks: 0. Only match is `model`/`routing` inside the Simplify-SpecHygiene validation prompt itself (the check text, not an ask).
- Concreteness: all 64 prompts carry exact handles — files, commands, expected outputs (`findings=2`, `cases=6 pass=6`, `NF=13`, `sha256sum -c`, exit codes); prompt length min 310 / median 477 / max 1224 chars.
- Surface existence spot-check (all EXIST): `scripts/sources-census.sh`, `tools/souji-landing-gate.py`, `tools/souji-coverage-agreement.py`, `tools/souji-axis-check.py`, `tools/souji-pre-report-gate.sh`, `tests/fixtures/r25-q57-check.sh`, `census/round-27/records/slice-verdicts.tsv`, `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`, `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/README.md`, `.ufo/waves/round-24/assimilation/slice-verdicts.tsv`.

## Findings
1. Clean — 64/64 items have distinct names (spec ↔ registry ↔ dispatch item sets consistent). Location: `w1-spec.json` items, `swarm-registry.json#37FB` members.
2. Clean — role counts match the wave plan exactly per role (executor 20, scribe 8, reviewer 12, critic 6, mutation-tester 6, connector 2, scout 6, sentinel 2, simplifier 2); no item uses a role outside the defined set.
3. Clean — no two items share an identical prompt (0 sha256 collisions across all 64).
4. Clean — no item asks for a model, provider, or routing; the only occurrence of these words is inside the hygiene-validation prompt itself.
5. Clean — every prompt is concrete (exact paths, commands, expected outputs, acceptance criteria; no open-ended phrasing).
6. Observation (not a violation) — 9 of 64 prompts name their surface by reference instead of a literal path: `Exec-MistakeMine` (Q57 checker / landing-gate / cell), `Rev-FrontierLesson` (lesson drafts by item name), `Rev-C2Rows` (SOURCES rows S212–S215), `Crit-C1` (Q57/Q59 cells), `Crit-C2` (entries, rows S212–S214), `Crit-C3` (manifests/gitignore/tool), `Crit-Overall` (claim shape), `Crit-Frontier` (SOURCES append on mirror), `Mut-C2` (C2 append rows). Each resolves unambiguously to artifacts named in sibling items (e.g., `Rev-C2Rows` → `Scribe-SOURCESRows`/`Exec-C2AppendBlock` output rows); none is vague. If the strict literal bar "every prompt contains a path" is desired, these nine are the set to tighten.
7. Confirmed — every pre-existing surface referenced by the prompts exists (tools, scripts, fixtures, corpus files, register, prior-round receipts); no phantom surface.

## Attack log
None — this item is a spec-validation (hygiene) check, not an attack; no counter/predicate/target challenged. No tool installs performed; no scratch created; no lane writes beyond this report.
