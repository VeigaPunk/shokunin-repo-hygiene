STATUS: DONE — five of the seven cuts are incomplete first-line carries; two are complete-clause excerpts. No template limit is evidenced.

# Findings

The evidence points to the round-16 gate's carry unit, not a template limit, as the reason the five defective quotes stop where they do. The r16 lesson says its wave-2 STATUS entries are “quoted verbatim after the gate's normalization” (`corpus/lessons/round-16.md:56`), but the contemporaneous carry report states that the gate's needle was only the first physical STATUS line, and its proposed carry table explicitly supplies that first physical line as the carry needle (`.ufo/waves/round-16/w2/ConnLessonCarry.md:22-24,34-36`). Its transcript shows the report was assembled around that predicate and paste-ready carry rows (`census/round-16/transcripts/w2/ConnLessonCarry.txt:214-216`). The lesson then used the line-sized excerpts below.

[INFERENCE] The five bad cuts were copied at the detector's acceptance boundary: the physical source wraps supplied a convenient first-line excerpt, and the gate treated that excerpt as sufficient. The records reviewed contain no quote-length/template cap. The evidence does not establish L1's private motivation or whether the source hard wraps were hand-formatted; it does establish that the five cuts are not clause-complete and match the gate's one-line unit, rather than a demonstrated template limit.

| Round-16 lesson line | Source STATUS lines | Assessment |
|---|---|---|
| `corpus/lessons/round-16.md:73` | `.ufo/waves/round-16/w2/ReopenS048.md:102-103` | Incomplete: the excerpt stops mid-phrase; D5 identifies the dropped continuation at `RevD5Carry.md:39`. |
| `corpus/lessons/round-16.md:74` | `.ufo/waves/round-16/w2/RerunGateFixture.md:12-16` | Incomplete: it stops inside the null-stub result; D5 identifies the omitted continuation at `RevD5Carry.md:41`. |
| `corpus/lessons/round-16.md:78` | `.ufo/waves/round-16/w2/RerunSeatAudit.md:157-162` | Incomplete: it ends on a continuing conjunction; D5 identifies the omitted continuation at `RevD5Carry.md:42`. |
| `corpus/lessons/round-16.md:79` | `.ufo/waves/round-16/w2/RevCensusStatusFinal.md:359-364` | Incomplete: it leaves a parenthesis open and omits the rest of the disposition; D5 identifies this at `RevD5Carry.md:43`. |
| `corpus/lessons/round-16.md:82` | `.ufo/waves/round-16/w2/RevengeSeatViolations.md:260-268` | Clause cut: the carried proposition that four rows are not violations is complete; the source's following appositive gives the classification detail. D5 does not count it as a truncation defect (`RevD5Carry.md:47`). |
| `corpus/lessons/round-16.md:83` | `.ufo/waves/round-16/w2/ScoutLsFilesPathspec.md:179-183` | Clause cut: the proposition that both consumers have a nested-layout gap is complete; the following parenthetical names the consumers. D5 does not count it as a truncation defect (`RevD5Carry.md:47`). |
| `corpus/lessons/round-16.md:84` | `.ufo/waves/round-16/w2/ScoutOptionalPrefix.md:238-240` | Incomplete: it ends before the explanatory clauses; D5 identifies the dropped continuation at `RevD5Carry.md:40`. |

Thus, **two remain semantically complete as narrow propositions**, though neither reproduces the full STATUS paragraph; the other five are incomplete. This matches D5's distinction between five mid-phrase/mid-parenthesis cuts and two syntactically complete clause-boundary cuts (`.ufo/waves/round-17/w1/RevD5Carry.md:35-47`). D5's proposed channel rule is explicit: reproduce every physical line of the source paragraph or mark the quote with an ellipsis (`RevD5Carry.md:157`).

# Evidence

- `corpus/lessons/round-16.md:56,73-84` — r16's stated quote convention and all seven lesson excerpts.
- `.ufo/waves/round-16/w2/ConnLessonCarry.md:22-24,34-36,54-64,107` — the first-physical-line needle and rows expressed in that unit; the report separately flags the wrap-cut class.
- `census/round-16/transcripts/w2/ConnLessonCarry.txt:214-216` — transcript chronology of the carry report being assembled around the pinned predicate and paste-ready rows.
- `.ufo/waves/round-17/w1/RevD5Carry.md:35-47,117-157` — five incomplete cases, two clause-boundary cases, and the corrected carry rule.
- Source reports listed individually in the table above; for the two clause cuts, their continuation is visible at `ScoutLsFilesPathspec.md:179-183` and `RevengeSeatViolations.md:260-268`.

# Commands run

No shell command, gate, fixture, census, or test was run. Inspection used `read` and targeted `grep` on the named lane files and transcript records; no external fetch was made.

# Contract compliance

Wrote only `.ufo/waves/round-19/w1/RevCarryHistory.md`. No subagents, runtime, installs, git/jj mutation, restricted path reads, or process signals. Tool installs/updates: none.