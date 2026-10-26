# Round 27 — honest stop with F4 assimilation and pre-report gate

## Gate

Round 27 re-opened two GLib 2.84.0 source files (accessed 2026-10-25; byte pins in `census/round-27/sources/SHA256SUMS`).

- ADMIT: S152 / `gio/glocalfile.c` — `trashname = get_unique_filename (basename, i++);` (line 2256; snapshot `census/round-27/sources/glocalfile.c`): supports the writer's unique-name retry.
- ADMIT: S210 / `gio/glocalfile.c` — `O_EXCL` (line 2261; same snapshot): supports exclusive reservation of the info-file name.
- ADMIT: S211 / `glib/gfileutils.c` — `if (g_rename (old_name, new_name) == -1)` (line 1041; snapshot `census/round-27/sources/gfileutils.c`): supports publication by rename.
- REJECT: staged S119 zh-Hans git-fetch edition: decision-time version state cannot be reconstructed without a pinned snapshot; flip only when a decision-time snapshot and located quote are available.

The writer and mechanism entries each carry their own URL, opened date, located ≤25-word quotes, snapshot paths, and an ADMIT/REJECT decision. The two entries are admitted on F4 implementation ground only; the normative format remains the held S022 specification.

Quarantine slice: 8 rows re-opened (S114, S118, S123, S124, S126, S131, S133, S138); seven accepted with evidence and S118 unverifiable because the registered DOI payload remains unavailable and venue metadata conflicts. Full per-row decisions: `census/round-27/records/slice-verdicts.tsv`.

## Findings

- C1 calibration failed: landing-gate findings remained 2 at base and tip; the two tokens are parser overmatches but the S118 composite site also points at a stale class. No exemption was committed because it could mask a real citation defect. The result is an honest stop, not a narrowed target.
- C2 coverage passed its frozen counters at `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`: SOURCES rows 132→135; grounded F4 entries 2→4; gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`; sources census rc 0. Collision proof and its 24-row alias/reject/quarantine mapping are in `census/round-27/assimilation/`.
- C3 operability passed at the same candidate: pre-report gate installed; isolated fixture `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, rc 0. It checks remote branch equality, report presence, one SHONEN heading, clean worktree, and a required preregistration.
- The r26 routed S-language pin defect was not fixed by this round: S119 remained rejected; a future re-adoption needs a decision-time pinned snapshot and sha256.
- Attempt 1 ended with `lane-dead-no-report` (fleet watchdog line 1377); attempt 2 used the ready-file handoff. `considerthese/` is absent.

## Residuals

- C1 requires a truthful correction to Q57's composite site / stale class; do not suppress that defect with an exemption.
- No claim of overall admission: C1 failed, so the canonical all-claims admission condition is unmet.
- `.ufo/` wave runtime artifacts are not committable through `jj-lane.sh`; durable receipts and the dispatch results remain under `.ufo/waves/round-27/` for the round record, while committed evidence is in `census/round-27/`.
- 36 inherited r26 W1 files remain under `.ufo/waves/round-26/w1/`; the helper refuses `.ufo` paths. They were catalogued by `ExecInheritedResolve.md` and left untouched rather than bypassing the lane helper.

## Receipts

- C1 before/after: `census/round-27/records/c1-before.tsv`, `c1-after.tsv`.
- C2 after: `census/round-27/records/c2-after.tsv`; registry validation output `sources-census-after.out`.
- C3 after: `census/round-27/records/c3-after.tsv`.
- Frozen preregistration copy: `census/round-27/records/preregistration.txt`; machine instrument `python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`.
- Wave: one v2 wave, 79 seats (25 executor, 12 reviewer, 11 scout, 10 critic, 8 scribe, 6 mutation-tester, 3 connector, 3 simplifier, 1 revenger); no dead seats reported in `w1-results.json`. L1 performed the planner seat. Wave results and full reports remain under `.ufo/waves/round-27/`.

## Mistakes

- R26-M1 (class=landing; evidence `corpus/lessons/round-26-verifier-spotcheck.md:13`; captured-by: none; fix: `tools/souji-pre-report-gate.sh` clean-worktree check). The dirty-tree selftest case returns nonzero with `check-clean=FAIL`, showing the fix can fail on the routed leftover class.

## Seat-reported failures

Appended in round 31 (M1): the round-27 lesson carried no `## Seat-reported failures` section, so the 29
committed seat STATUS failure lines under `census/round-27/waves/` went uncarried (base gate at lane base
`9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`: `findings=32 ... checked_markers=29 ... carry_heading=0`).
Each bullet quotes one report's STATUS paragraph normalized exactly as the landing gate normalizes it (NFC,
`*` and backticks dropped, whitespace collapsed) from the bytes committed at that base, and carries one
disposition: `open` where the stated defect or missing receipt still stands at lane tip, or
`resolved@<full 40-hex>` where a later lane commit demonstrably discharged it. The basis for each
disposition (what was tested, and at which revision) is recorded in this round's wave-1 M1 delivery.

- `census/round-27/waves/w1/CritC3Attack.md` line 2 — open: STATUS: PARTIAL — the gate can replace genuine repetitive L1 preflight commands, but the only available artifacts are drafts and the frozen four-case test does not establish report readiness or all five check semantics.
- `census/round-27/waves/w1/CritCounterFidelity.md` line 5 — open: STATUS: PARTIAL — C1 values reproduce at base but its receipt binds a false gate sha256 and the counter depends on the live fleet root; C2 counters are worktree-scoped with no byte binding and no false-green control; C3 passes all four attack dimensions (design; fixtures not yet delivered).
- `census/round-27/waves/w1/CritErrorPatterns.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — review based on preregistration, SKILL.md, and staged C3 draft; installed fixture and landed counters are not present in the opened evidence.
- `census/round-27/waves/w1/CritNoHarmAttack.md` line 2 — open: STATUS: PARTIAL — identified material design risks; C1, C2, C3 behavioral checks were not run.
- `census/round-27/waves/w1/CritReportContract.md` line 5 — open: STATUS: PARTIAL — 4/6 checklist items pass on the current plan; item 5 (wave shape/seat counts/roles/dead seats/planner-seat mapping) is unplanned, and item 2 (bullet-to-pointer backing) has no enforcement against [PENDING] residue at filing. Both are fixable before filing; corrections below.
- `census/round-27/waves/w1/ExecC1Counter.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — script delivered and shell grammar checked; live gate execution was intentionally not performed.
- `census/round-27/waves/w1/ExecC3Counter.md` line 2 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: PARTIAL — counter draft written; installed gate and fixture were absent when inspected, so execution and receipt verification remain for L1 after integration.
- `census/round-27/waves/w1/ExecCensusAfterScript.md` line 2 — open: STATUS: PARTIAL — after-integration receipt script drafted; its measurements have not been run against integrated state.
- `census/round-27/waves/w1/ExecKnowledgeMechanism.md` line 2 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: PARTIAL — mechanism-entry draft delivered; source snapshots are not present in the lane census, and required assimilation checks remain unrun.
- `census/round-27/waves/w1/ExecPycacheFix.md` line 2 — open: STATUS: PARTIAL — draft delivered (w1/gitignore-draft.md), but the assignment's stated check "no tracked file matches __pycache__" FAILS: census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc is tracked (commit e879ba0); the other two __pycache__/ dirs are untracked.
- `census/round-27/waves/w1/ExecScorecardDraft.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — prepared the requested scorecard additions; all after-values remain EVIDENCE-PENDING because this seat did not measure a landing tip.
- `census/round-27/waves/w1/LabGitIgnoreProbe.md` line 4 — open: STATUS: PARTIAL — probe executed end-to-end; rule mechanics verified in a mirror repo; the assignment's lane criterion "no tracked lane file matches __pycache__ (count → 0)" is FALSIFIED by lane data: count = 1. Read-only seat: no lane writes (only this report).
- `census/round-27/waves/w1/LabSliceFetch.md` line 2 — open: STATUS: PARTIAL — S126, S138 and S118 corroborating record re-verified; S114 page reachable but tested r24 quote absent; DOI target still returns no body.
- `census/round-27/waves/w1/RevC2Entries.md` line 2 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: FAIL — neither staged entry is admission-ready; both fail frozen freshness/Gate/mapping requirements.
- `census/round-27/waves/w1/RevC2Rows.md` line 4 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: PARTIAL — rows are mechanically append-ready (every schema, uniqueness, enum, shape, and append-only check passes on a scratch copy; sources-census.sh validate --file rc 0, E=0), but two text defects must be fixed before landing: S152's scope cell cites registry-absent S146, and the C2 writer entry (used-by target) carries a rooted path token that will dangle at the tip and re-raise LG-DANGLING-PTR, killing C1's after=0.
- `census/round-27/waves/w1/RevC3Fixture.md` line 4 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: PARTIAL — harness behaves correctly against the real draft gate (all runtime probes green, control wired, worlds real), but its success line is a hardcoded literal: a scratch copy with the case-2 block deleted still printed cases=4 pass=4 control=FALSE-GREEN-REJECTED rc 0 (proven below). Verdict: needs fixes — one small harness-internal fix (F1) before L1 integration; frozen counter line unchanged when healthy.
- `census/round-27/waves/w1/RevC3Gate.md` line 4 — open: STATUS: PARTIAL — verdict needs fixes: 3 demonstrated false-PASS vectors (one is an end-to-end FALSE GREEN, rc=0) plus a read-only-contract breach (git status rewrites .git/index); hygiene/exit-code/git -C checks otherwise pass. The selftest fixture does not exist yet, so cases=4 pass=4 is unverifiable from this seat.
- `census/round-27/waves/w1/RevMistake.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — needs fixes: the evidence line resolves, but the cited line number in the scaffold is wrong and the C3 red-before proof is not yet committed as the frozen 4-case test.
- `census/round-27/waves/w1/RevNoHarm.md` line 7 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: PARTIAL — no-harm holds for C1 and C3 and for C2's append discipline, but one staged C2 file carries a dangling corpus/ pointer that would raise C1's frozen counter to 3 (≠0) if landed as-is (ConnClaims violation-in-waiting, finding 1), and two C2 landing dependencies (findings 2–3) must actually land. No axes-table edit exists in any draft; scores 7/8/8 hold.
- `census/round-27/waves/w1/RevReportIntegrity.md` line 5 — open: STATUS: PARTIAL — the planned report skeleton (ScribeReport, w1-spec.json:383-386) is conformant on the six contract sections, their order, SHONEN shape, and lands-last sequencing, but has 3 fixable gaps: no planned home for the round-shape/planner record (lane convention r25/r26), no zero-[PENDING] pre-filing check although the draft sanctions placeholders (marker-rule hazard the watchdog cannot see), and no explicit lane-tip citation line (ls-remote + full-40 hash + ancestry). Plus one count hazard (spec says 80, artifacts say 79). Verdict: plan conformant with gaps — all correctable in report content/sequencing before filing; none touches a frozen predicate, so no preregistration amendment is needed.
- `census/round-27/waves/w1/ScoutScorecardState.md` line 4 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — four of five preconditions hold at base e78ac7c; (d) does NOT: ## Planned names no round after r25 (no r26/r27/r28 bullet exists anywhere in the committed file), so the r28 planned bullet must be created by this round's landing (marked below). Two adjacent findings also reported: (i) the frozen r27 preregistration MACHINE BLOCK is not parseable by tools/souji-axis-check.py (rc=2); (ii) the wave's own c1-before.tsv receipt mislabels a git blob SHA-1 as gate_sha256.
- `census/round-27/waves/w1/ScribeInvariant.md` line 2 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: PARTIAL — scoped wording draft delivered; requested SKILL.md was not edited because this seat may write only its report and named delivery file. C3 delivery/test claims remain unverified by this seat.
- `census/round-27/waves/w1/ScribeLOG.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — drafted the Round27 LOG append entry from observed W1 artifacts; C1/C2/C3 acceptance results remain unobserved and L1 integration is pending.
- `census/round-27/waves/w1/ScribeLessonGate.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — drafted the requested Gate section with staged F4 rows, S119 rejection rationale/flip, dated quotes, and verifier placeholder; no counter or verifier execution claimed.
- `census/round-27/waves/w1/ScribePrereg.md` line 2 — resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17: STATUS: FAIL — axis-check refused the preregistration because its machine block delimiters do not match the required ## MACHINE BLOCK ... END section.
- `census/round-27/waves/w1/ScribeReport.md` line 2 — open: STATUS: PARTIAL — assembled evidence from opened round-27 artifacts; integration measurements, final landed revision, trends, SHONEN verification, and stale-lane state are not established by those artifacts. No product/repository code changed.
- `census/round-27/waves/w1/ScribeScorecard.md` line 2 — resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0: STATUS: PARTIAL — paste-ready Round 27 measurement block and planned bullet drafted; all landing-tip values remain [PENDING] for the L1.
- `census/round-27/waves/w1/SimplExistingTools.md` line 2 — open: STATUS: PARTIAL — identified historical/duplicate candidates, but no removals are safe to recommend from text grep alone; broad historical callouts remain.
- `census/round-27/waves/w1/SimplWaveSpec.md` line 2 — open: STATUS: PARTIAL — confirmed substantial overlap in the visible spec entries; the 80-item list was not fully enumerated from the truncated read.
- Round 31 wave-2 audit of this carry (`census/round-31/waves/w2/deliver-m1-audit-r27.md`, appended; the bullets above stand as written and the audit row supersedes their disposition where listed):
  - audit row 7: `ExecC3Counter.md:2` disposition `resolved@6cb22dc` is WRONG-RESOLVED (hash scope); the audit row names the commit that delivered it, or the defect still live at the round-31 tip.
  - audit row 21: `ScoutScorecardState.md:4` disposition `resolved@c973d1a` is WRONG-RESOLVED (substantive); the audit row names the commit that delivered it, or the defect still live at the round-31 tip.
  - audit row 22: `ScribeInvariant.md:2` disposition `resolved@6cb22dc` is WRONG-RESOLVED (hash scope); the audit row names the commit that delivered it, or the defect still live at the round-31 tip.
