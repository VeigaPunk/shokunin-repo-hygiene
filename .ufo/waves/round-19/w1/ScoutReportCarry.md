STATUS: DONE — Q25(c)/Q36 carry checklist and current PARTIAL candidates identified.

# Findings

Apply this checklist to every r19 report `STATUS:` paragraph whose marker is in the contract failure channel, outside fences and tables:

1. **Inventory the paragraph, not just its first physical line.** Capture the STATUS marker and all prose continuation lines belonging to that paragraph. Do not treat fences, tables, quotes, headings, bullets, thematic breaks, or a new STATUS as continuation text. Check all seat reports; a report's first line is not the only possible failure marker. [Q25(c): `corpus/QUALITY.md:64`; paragraph boundaries: Q36, `corpus/QUALITY.md:90`]
2. **Carry the wording, not a summary.** In `corpus/lessons/round-19.md` under `## Seat-reported failures`, make an entry identifying the exact report path and source line, then quote the complete STATUS paragraph verbatim. The comparison may normalize formatting/whitespace, but that is not permission to paraphrase or silently omit source wording. [R18 shape: `corpus/lessons/round-18.md:75-90`; r19 destination/append rule: `corpus/lessons/round-19.md:129-132`]
3. **If shortening a wrapped paragraph, use only a valid source-line cut.** Either quote the normalized whole paragraph, or end the quoted prefix exactly at a physical-line end in the source and immediately append an ellipsis (`…`). A cut mid-source-line does not carry, even if followed by an ellipsis. An ellipsis is not a general summary marker. [Q36: `corpus/QUALITY.md:90`]
4. **Join wrapped lesson bullets before checking them.** A lesson entry may itself wrap across physical lines; join its continuation before comparing it with the source paragraph/prefix. [Q36: `corpus/QUALITY.md:90`]
5. **Give each entry a same-line disposition.** End the entry with `— open` if unresolved, or `— resolved@<rev>` if resolved, and state the resolution briefly. Use a revision that identifies the resolution; do not call a mixed outcome wholly resolved. Where only part is resolved, record the resolved portion and its revision while retaining `open` for the remainder, as the r18 mixed-disposition precedent does. [Q25(c): `corpus/QUALITY.md:64`; examples: `corpus/lessons/round-18.md:86,89`]
6. **Keep the round gate in view.** Apply the strict paragraph/cutoff rule to round 19; Q36 gates it at round 18 so pinned historical replays retain their prior verdicts. Do not use the pre-gate behavior as evidence that an r19 wrapped cut carries. [Q36: `corpus/QUALITY.md:90`]

Current wave-one PARTIAL candidates observed in report-leading STATUS lines:
- `ConnToolsPatterns` — disclosed a root census listing that expanded operator-sweep child names; `.ufo/waves/round-19/w1/ConnToolsPatterns.md:1` (item: `.ufo/waves/round-19/w1-spec.json:608-611`).
- `MutRevPin` — mutation verdicts are inconclusive because the proposed fixture is contract-blocked; `.ufo/waves/round-19/w1/MutRevPin.md:1` (item: `.ufo/waves/round-19/w1-spec.json:256-259`).

These are the two report-level PARTIAL lines found among the current wave-one report files, not a prediction about reports that have not yet been produced. Findings in a report whose STATUS is DONE are not, by themselves, failure-channel STATUS lines.

# Evidence

- Q25(c) defines the source set as contract failure-channel STATUS lines outside fences/tables and requires verbatim carry plus an `open` or `resolved@<rev>` disposition: `corpus/QUALITY.md:64`.
- Q36 defines the whole-paragraph boundary, valid physical-line cutoff with immediate ellipsis, invalid mid-line cutoff, joining wrapped lesson bullets, and round-18 gate: `corpus/QUALITY.md:90`.
- R18's section heading and introductory shape are at `corpus/lessons/round-18.md:75-78`; concrete entries and mixed status treatment are at `:79-90`.
- The current r19 lesson reserves the same heading and says entries are appended after waves return: `corpus/lessons/round-19.md:129-132`.
- The two current report-level PARTIAL lines and matching item names are at the paths cited above.

# Commands run

- Read `corpus/QUALITY.md:64,90`, `corpus/lessons/round-18.md:75-91`, `corpus/lessons/round-19.md:129-132`, and the cited current wave-one reports/spec entries.
- Searched the round-19 wave-one report directory for report-leading STATUS lines and `STATUS: PARTIAL`; enumerated the wave directory and read its item manifest.
- Read-only extraction: `git show HEAD:corpus/QUALITY.md | awk 'NR==64'`.
- No tests, gate, fixture, audit, census, or external documentation were run/read.

# Contract compliance

Only this assigned report was written. No tool was installed, no scratch was created, and no git/jj mutation or forbidden process action occurred. Source review used the current worktree; the read-only `git show` above did not alter it.