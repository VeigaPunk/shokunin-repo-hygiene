STATUS: DONE — C1 scope reviewed; no code edits.

# Findings

**Axis:** calibration (7, the lowest non-retired axis; `.ufo/waves/round-19/preregistration.txt:5,7-22`). No separate operability or coverage verdict is claimed.

**Strongest counterargument:** the strict rule does make the historical r16 zero a false negative *under Q36*. The seven wrapped STATUS reports identified in `.ufo/waves/round-18/w1/ScoutCarryWrap.md:20-32` are present in the current worktree: their source paragraphs continue after the quoted first physical line, while the lesson entries at `corpus/lessons/round-16.md:73-84` stop at that line without an ellipsis. The pinned expectation records `r16-landing` as exit 0 with no findings (`census/round-17/gate-replays-expected.json:53-58`); the current replay record still reports that result as a match (`census/round-19/gate-replays-final.json:124-150`). Since the integrated gate selects strict parsing only for `round_no >= 18` (`tools/souji-landing-gate.py:496-518`), it deliberately does not expose those seven failures on an ordinary `--round 16` replay. A reader who sees only the green replay could mistake legacy behavior for paragraph-aware validation.

**Decision for L1 to record:** keep the `>= 18` boundary. It preserves the pinned pre-r18 contract while applying the new rule to r18 and later; the current r19 lesson also checks r18 under the strict rule (`corpus/lessons/round-19.md:13-24`). Do not silently rewrite the historical expectation or describe r16's zero as a Q36 pass. The lesson already says the seven are known and not retro-corrected (`corpus/lessons/round-19.md:111-113`), so the defect is disclosed, not wholly silent. Make that note unambiguous: the retained r16 zero is a legacy-Q25 result and a false negative under Q36, with seven strict-only `LG-SEAT-UNCARRIED` cases. If L1 instead chooses retrospective enforcement, regenerate the historical replay expectation and explicitly re-adjudicate the r16 calibration admission; changing the gate alone would leave evidence and verdicts inconsistent.

**Ellipsis usability:** the rule is satisfiable for current authors: quote the whole normalized paragraph (no ellipsis needed), or end an excerpt at a source physical-line boundary and mark the omission with an ellipsis. Q36 and the r19 preregistration state this (`corpus/QUALITY.md:90`; `.ufo/waves/round-19/preregistration.txt:18-22`), and the current SKILL describes the same rule (`SKILL.md:115-121`). The synthetic cases include unmarked cut, marked cut, complete paragraph, and wrapped lesson bullet (`tests/fixtures/r19-carry-wrap.py:58-100`). The counterargument is historical/process-facing: r16's Q25 required a verbatim carry but did not define paragraph completion or ellipsis (`corpus/QUALITY.md:64`); the shared L1 prompt template asks for a lesson mistake but gives no carry punctuation rule (`/home/vgpnk/Projects/shokunin/templates/round-prompt.md:68-72`). Thus do not judge old authors against punctuation that was not specified then. For future authoring, put the short whole-paragraph-or-boundary-ellipsis instruction wherever lesson carries are assigned; it is now present in the r19 preregistration and Q36, not in the generic template.

**Smallest safe correction:** no gate change. Clarify the existing r19 carry-scope note with the legacy-vs-Q36 distinction above; retain the r16 replay bytes unless L1 explicitly elects a historical re-baseline. Ensure future author-facing lesson instructions expose the current carry format.

**Wave-2 falsifier:** a fresh reviewer, without relying on the W1 table or r19 fixture, should re-open the seven source/lesson pairs at `6ff91f5` and compare two isolated runs: the ordinary historical `--round 16` replay must retain its legacy 0, while a private strict-rule copy forced to evaluate that same revision under Q36 must produce exactly those seven `LG-SEAT-UNCARRIED` findings and no unrelated new IDs. Then give a fresh lesson author only the actual author-facing instructions and one real wrapped STATUS example; require them to produce both a complete carry and a boundary-ellipsis carry that pass, plus an unmarked-cut control that fails. Any count other than seven, a pass on the unmarked cut, rejection of either valid carry, or inability to discover the ellipsis instruction from the intended author-facing surface falsifies the current scope/disclosure/usability rationale.

# Evidence

- Seven concrete source continuations and corresponding unmarked lesson excerpts were re-read in the integrated worktree: `.ufo/waves/round-16/w2/ReopenS048.md:102-103`, `RerunGateFixture.md:12-16`, `RerunSeatAudit.md:157-162`, `RevCensusStatusFinal.md:359-364`, `RevengeSeatViolations.md:260-267`, `ScoutLsFilesPathspec.md:179-183`, `ScoutOptionalPrefix.md:238-240`; corresponding lesson entries are `corpus/lessons/round-16.md:73-84`.
- Historical result: `census/round-17/gate-replays-expected.json:53-58`; current recorded replay: `census/round-19/gate-replays-final.json:124-150`.
- The seven strict-only cases are also reported by the prior local review `ScoutCarryWrap.md:20-32`; I did not independently execute its reimplementation or the gate.
- Old criterion versus new criterion: `corpus/QUALITY.md:64,90`; current author guidance: `.ufo/waves/round-19/preregistration.txt:18-22`, `SKILL.md:115-121`; shared template scope: `/home/vgpnk/Projects/shokunin/templates/round-prompt.md:68-72`.

# Commands run

No shell commands, gate runs, fixtures, or tests. Read-only `read`, `grep`, and `glob` inspections only. No tools installed or updated.

# Contract compliance

Wrote only this required report. No code, test, corpus, census, scorecard, log, or skill files were edited. No subagents, git/jj mutations, signals, network access, or scratch files.