# R40w2scribe04 — SHONEN section draft

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources — evidence: `SKILL.md` Decision tables/Error patterns/Checklists/Gate registry; `corpus/SOURCES.md` S100-S103; `corpus/lessons/round-21.md` Gate. Non-author verifier named by the round-39 spot-check: hyaku closure (@m_zfl).
- [~] At least one end-to-end domain task executed and logged in LOG.md — evidence: `LOG.md:362`. Non-author verifier named by the round-39 spot-check: hyaku closure (@m_zfl).
- [~] Instructions executable by an agent without oral context — evidence: `census/round-21/run-acceptance.py`; `census/round-21/accepted-matrix.json`; `census/round-21/remote-source-after.json`. Non-author verifier named by the round-39 spot-check: hyaku closure (@m_zfl).
- [~] No cross-domain bleed (PROVINCE.md still accurate) — evidence: `PROVINCE.md` Round21 privacy boundary; `.ufo/waves/round-21/w1/ConnSiblingOverlap.md`; `corpus/lessons/round-21.md` Boundaries. Non-author verifier named by the round-39 spot-check: hyaku closure (@m_zfl).

## Evidence and verdict

Task attacked: attribution and evidence sufficiency for a draft `## SHONEN` section with exactly one line per `SHONEN.md` checklist box. The four box texts are at `SHONEN.md:5,7,9,11`; their existing evidence pointers are at lines 6, 8, 10, 12. The cited verifier attribution is `corpus/lessons/round-39-verifier-spotcheck.md:3`; its SHONEN assessment and checkable pointers are at lines 24 and 157-159. All four lines remain `[~]`: the spot-check says they are checkable, but does not record a per-box `[x]` certification. This is an evidence-preserving draft, not a promotion finding.

Exact command run and output:

```text
$ printf '%s\\n' '--- git show stat ---'; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat --oneline 128e412b0ced3c243dc27c3dd3332054a611bc2e; printf '%s\\n' '--- SHONEN lines ---'; nl -ba /home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md; printf '%s\\n' '--- spotcheck verifier anchors ---'; grep -nE 'author:|## Note for the operator|SHONEN|non-author' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-39-verifier-spotcheck.md
128e412 round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery
 census/round-40/assimilation/collisions            |   58 +
 census/round-40/assimilation/reg-ids               |  177 ++
 census/round-40/assimilation/staged-ids             |  134 +
 census/round-40/c1-counter.py                      |  362 +++
 census/round-40/c2-counter.py                      |  341 +++
 census/round-40/c3-counter.py                      |  211 +++
 census/round-40/docstring-classes.py               |   96 +++
 census/round-40/preregistration.txt                |   13 +
 census/round-40/sources/SHA256SUMS                 |    5 +
 census/round-40/sources/codecs.html                | 2312 +++++++++++++++++
 census/round-40/sources/git-merge-base.1.txt        |  191 +++
 census/round-40/sources/gvfs-trashitem-1.62.0.c     |  560 +++++++
 census/round-40/sources/inspect-cleandoc.txt        |    5 +
 census/round-40/sources/inspect.html                | 2654 +++++++++++++++++++
 corpus/README.md                                    |   24 +-
 corpus/SOURCES.md                                   |    9 +
 .../docstring-class-continuation-lines-r40.md       |   50 ++
 corpus/knowledge/drift-record-invalid-utf8-r40.md   |   49 ++
 .../git-strict-descendant-relation-r40.md           |   43 ++
 corpus/knowledge/origin-record-format-gvfs-r40.md  |   54 ++
 corpus/lessons/round-40.md                          |  102 +++
 tests/fixtures/r40-c1-evidence.py                   |  235 ++++
 tests/fixtures/r40-docstring-joined.py              |  126 ++++
 tests/fixtures/r40-drift-record-branches.py         |  150 ++++
24 files changed, 7959 insertions(+), 2 deletions(-)
     1  # souji-shokunin — Promotion checklist
     2  
     3  Promotion to shokunin requires all of:
     4  
     5  - [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources
     6    SKILL.md Decision tables/Error patterns/Checklists/Gate registry; corpus/SOURCES.md S100-S103; corpus/lessons/round-21.md Gate
     7  - [~] At least one end-to-end domain task executed and logged in LOG.md
     8    LOG.md:362 (2026-10-19 operator sweep: 96 pushed-receipt artifacts quarantined, second-checked, removed)
     9  - [~] Instructions executable by an agent without oral context
    10    census/round-21/run-acceptance.py; census/round-21/accepted-matrix.json (3/3 sources, each18/18); census/round-21/remote-source-after.json
    11  - [~] No cross-domain bleed (PROVINCE.md still accurate)
    12    PROVINCE.md Round21 privacy boundary; .ufo/waves/round-21/w1/ConnSiblingOverlap.md; corpus/lessons/round-21.md Boundaries
     1  # Round 39 — verifier spot-check (non-author)
     3  author: hyaku closure (non-author integrator, @m_zfl)
    24  | `SHONEN` heading, one line per box | `grep -c '^## SHONEN'` → 1; four following `- [~]` lines; `SHONEN.md` has 4 boxes | 1 heading, 4 `[~]` lines each with a resolvable pointer (`SKILL.md`, S247–S250, `LOG.md` §Round 39, `census/round-39/preregistration.txt`, `PROVINCE.md`); no `[x]`; `SHONEN.md` unchanged this round | pass |
    27  | report contract sections, in order | `grep -n '^## '` | Work performed · Landed changes · Before → after measurements · Sources & frontier · Trend verdicts · SHONEN, with Errata/Named limits/Tools installed after; required order holds | pass |
   102  ## Discernment spot-check (LEARNING.md — non-author)
   157  ## Note for the operator (promotion is operator-owned)
   159  `SHONEN.md` still carries four `[~]` self-assessments. Boxes 1–4 all look checkable by a non-author from
```

Verdict: SAFE for the scoped draft/attribution task: four boxes, four `[~]` lines, existing pointers retained, and non-author verifier explicitly named. This does not assert that round-40 promotion gates were re-tested. Scratch directory: none created; removal not applicable. No tools installed.