# r12 planner — claim measurement plan

Author: W2RoundSouji-8.R12Planner (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12Planner`; this committed copy is the durable form). 2026-10-19.

## Observations

- The proposed claims map to **calibration** (C1), **coverage** (C2), and **operability** (C3). STATE §2 records calibration as the lowest axis (legacy score 7; new scoring remains unrated).
- `corpus/QUALITY.md`, `corpus/SOURCES.md`, and `corpus/lessons/round-12.md` are absent. The only current `corpus/knowledge/` item is `obsidian-ledger.tsv`.
- The maintenance fixture now exists at `tests/fixtures/r12-maintenance-guard.sh`; its comments declare observed Git 2.55 outcomes, but I did not execute it. The current SKILL pre-quarantine checklist has not yet gained the proposed guard rows.
- The frozen contract was found at `fleet-ledger/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`, rather than the initially supplied path.
- Lesson pointers checked against their contents: Q1 `round-9.md:14`; Q2 should use `round-5.md:38-39` (the ART pointer to `SKILL.md:14-15` is not a lesson); Q3 `round-5.md:9-14`; Q4 `round-8.md:24-25`. Other relevant evidence includes `round-9.md:10-17`, `round-11.md:13-17`, and `LOG.md:373-375,381-382,432-436`.

## Proposed axes

1. C1 — calibration, the lowest recorded axis.
2. C2 — coverage, including entry coverage of declared frontier rows.
3. C3 — operability, with a runnable fixture and executable checklist guards.

## Ordered plan

1. **Establish criterion provenance.** Seed Q1–Q4 with the checked pointers above. Add criteria for STATE §4 classes 1, 2, 3, 4, 7, 8 and ART §7 M1–M8 where AGENTS/SKILL do not already capture the specific hazard. STATE classes 5 and 6 are already addressed by AGENTS.md’s worker-scope and headless-harness rules; M1 and M2 are only partially covered by SKILL’s digest-symlink and second-check rules.
2. **Add lesson records before citing new incidents.** The operator-sweep staging-scope and staging-hang evidence is in `LOG.md:373-375,381-382,432-436`, not an existing round lesson. Any QUALITY criteria using those incidents should cite round-12 Mistakes rows whose text is included in that lesson. M6 (ShellCheck warning severity) and M8 (Git auto-maintenance) likewise need explicit lesson grounding if retained.
3. **Specify the three counting gates.**
   - C1: one-line `awk` over `| id | class | evidence | captured-by | fix |` rows in `corpus/lessons/round-12.md`; count an `M…` row as captured when its `captured-by` cell is not `none`.
   - C2: count knowledge `.md` entries whose first three lines contain `source:`, `verified-at:`, and `recheck:`; count explicit `## Frontier` rows linking at least one entry; run the frozen SOURCES contract census (row count, malformed rows, histograms, duplicate IDs, enum violations, and missing mined `used-by` paths).
   - C3: run `bash tests/fixtures/r12-maintenance-guard.sh`, report its exit code, and count `maintenance\.auto|add -A|pathspec` in `SKILL.md`.
4. **Representative criterion:** Q1 should require every tool-behavior claim to name the verified version and host version; test by checking the entry’s versioned citation and running its stated recheck against that version. Lesson: `corpus/lessons/round-9.md:14`.
5. **Verification gate:** use synthetic files under `/var/tmp/souji-r12-XXXXXX` to exercise the three counting commands and record their actual outputs. Then re-check every QUALITY lesson pointer after the round-12 Mistakes rows exist. I have not run these synthetic command checks or the fixture.

## Hard blockers

None for drafting the plan. The final QUALITY lesson column depends on round-12 Mistakes rows for incidents without an existing lesson pointer; those rows need their text in place before their pointers can be treated as resolved.
