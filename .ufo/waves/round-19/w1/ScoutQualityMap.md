STATUS: DONE — mapped the criterion lineage and lesson pointers; found one invalid Q36 lesson anchor

# Findings

- **Supersession rule:** `corpus/QUALITY.md:11-14` requires every criterion to cite its originating lesson; a superseded criterion is replaced by a new row that names the row it replaces, never edited in place. The scoped examples in Q25-Q35 are:
  - Q29 supersedes Q7 only for jj-colocated repositories; Q7 remains in force for plain repositories (`corpus/QUALITY.md:78`).
  - Q33 supersedes only Q32's ambiguous suffix and signal wording; the rest of Q32's process-residue/list-only contract remains (`:81-82`).
  - Q34 supersedes Q30's universal-liveness wording and states the narrower bounds and remaining limits (`:79,83`).
  - Q35 extends Q31; it does not replace it (`:80,84`).
  - Q25 and Q26 extend Q17/Q23 and Q24 respectively; Q27 and Q28 add their own criteria without superseding an older row (`:64-65,71-72`).
- **Next Q id:** At the round-18 boundary, Q35 is the latest row, so **Q36** was the next free id (`corpus/QUALITY.md:84-86`). The current worktree already has integrated Q36-Q38 (`:90-92`), making Q39 the next unused id *in that worktree*; those integrated rows are not independent acceptance evidence.
- **Claim-to-criterion map:**
  - **C1:** Q36 is the carry-check addition to Q25(c); Q38 extends the seat-audit contract in Q26 and its path/severity parsing rules in Q27. C1 combines both topics in the preregistration (`.ufo/waves/round-19/preregistration.txt:7-31`).
  - **C2:** Q37 extends Q25(b)'s measured-byte binding and Q31's landing-revision/measured-commit authority checks (`preregistration.txt:33-49`; `corpus/QUALITY.md:64,80`).
  - **C3:** the coverage claim adds a knowledge entry, not a new QUALITY criterion. Its process-residue content must stay within Q32-Q34 (list-only observation, Q33's narrowed suffix/signal rule, Q34's bounded-census limits); its antecedent gap is recorded at `corpus/lessons/round-18.md:119`. The applicable existing rows and their lessons are Q32/R18-M2, Q33/R18-M9 and Q34/R18-M8 (`corpus/QUALITY.md:81-83`; `corpus/lessons/round-18.md:24,30-31`).
- **No in-place criterion rewrite is warranted.** Append new rows. Q36/Q37/Q38 are additions to the existing rules; if an author intends a new rule to replace any old clause rather than extend it, the new row must explicitly name that scoped supersession. In particular, Q36 can extend Q25(c) while retaining Q25's marker-line obligation; if the ellipsis rule is intended to replace a literal reading of Q25(c)'s “verbatim” requirement, state a scoped supersession of Q25(c) rather than editing Q25. Do not rewrite Q30 or Q32: Q34 and Q33 already record their limited supersessions.

# Evidence

- **Q36 (C1 carry):** exact lesson rationale is `corpus/lessons/round-17.md:72` (D5 carry-format defect), `corpus/lessons/round-18.md:118` (wrap-truncation residual), and `corpus/lessons/round-18-verifier-spotcheck.md:151` (closure carries that residual). The detailed supporting scout report is `.ufo/waves/round-18/w1/ScoutCarryWrap.md:34-94`.
  - Citation defect in the current Q36 row: `corpus/QUALITY.md:90` names `corpus/lessons/round-16.md D5`, but round-16.md has no D5 section. Its relevant examples are at `corpus/lessons/round-16.md:73-74,78-79,84`; the actual D5 analysis is round-17.md:72. The phrase “r18 closure residual” should also resolve explicitly to the two round-18 lesson locations above.
- **Q37 (C2 revision pin):** lesson pointer is `corpus/lessons/round-18.md:120` (HEAD-pinned r13/r14 runners remain open). Supporting, non-lesson pointers are `.ufo/waves/round-18/w1/ScoutHeadPinned.md:18-24` and `corpus/SOURCES.md:99-101` (S079-S081). The latter are source-registry rows, not lessons.
- **Q38 (C1 audit):** lesson pointers are `corpus/lessons/round-18-verifier-spotcheck.md:148` (closure D4: missing signal class) and `corpus/lessons/round-18.md:28` (R18-M6, unauthorized SIGKILL). Supporting, non-lesson report: `.ufo/waves/round-18/w1/ScoutSeatAuditR18.md:47-58,97-99`.
- The R19 claim boundaries are recorded in `.ufo/waves/round-19/preregistration.txt:7-22` (C1 carry/audit), `:33-49` (C2), and `:51-64` (C3). The current Q36-Q38 rows are at `corpus/QUALITY.md:90-92`; Q25-Q35 are at `:64-65,71-84`.

# Commands run

- Searched the scoped QUALITY, preregistration, lesson, report, and source-registry paths with `functions.grep` to locate criterion ids and lesson anchors; opened the relevant lines with `functions.read`. Search results were used only as locators; the findings above are grounded in the opened text.
- Checked `xd://lsp`; it is not mounted (the read tool returned “No such tool” and listed the mounted devices). No LSP semantic request was available.
- No shell commands, tests, builds, fixtures, census tools, or network requests were run. No tool was installed or updated.

# Contract compliance

- Wrote only `.ufo/waves/round-19/w1/ScoutQualityMap.md`.
- No subagents or other orchestration runtime; no git/jj mutation, live process/census access, secret access, network access, or pacman transaction.
