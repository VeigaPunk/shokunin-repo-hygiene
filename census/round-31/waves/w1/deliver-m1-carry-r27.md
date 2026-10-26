# deliver-m1-carry-r27 — round-31 M1 (mined mistake, round 27)

Seat SwarmScribe19. Target: `corpus/lessons/round-27.md`, which carries no `## Seat-reported failures`
section, so the 29 committed seat STATUS failure paragraphs under `census/round-27/waves/` went
uncarried. Fix shape: one append-only section at end of file, one bullet per failure paragraph, each
bullet quoting the paragraph normalized exactly as `tools/souji-landing-gate.py` normalizes it and
ending in one disposition (`open` or `resolved@<full 40-hex lane commit>`). No in-place edit, no
predicate/counter/case-set change.

## Receipts (all run this report, in a scratch clone with `origin` removed)

Scratch clone: `/fast/scratch/hyaku/souji-r31/SwarmScribe19/r.AfTj0S/c`, made with
`git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D/c"` then
`git -C "$D/c" remote remove origin` (`git -C ... remote -v` printed nothing;
`rev-parse --show-toplevel` printed that clone). Clone HEAD `1b811368461785040e955f41f9c97e62f61fd67c`
= lane HEAD at the time of this run.

1. RED-BEFORE (clone at `1b811368`):

```
python3 -B <clone>/tools/souji-landing-gate.py --root <clone> --rev 1b811368461785040e955f41f9c97e62f61fd67c --round 27 --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=29	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=29	status_lines=79	carry_heading=0	checked_reports=94
```

`cut -f1 | sort | uniq -c` over that output: `29 LG-SEAT-UNCARRIED`, `1 SUMMARY`. rc 1. Red-before
count = **29 LG-SEAT-UNCARRIED, `carry_heading=0`**.

Same red at the lane base (`--rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, run in the lane,
read-only, without `--fleet-root`): `findings=32` = `29 LG-SEAT-UNCARRIED` + `3 LG-DANGLING-PTR` (the
three pre-existing `.ufo/waves/hyaku/...` fleet pointers), `carry_heading=0`.

2. GREEN AFTER (append this block to the end of `corpus/lessons/round-27.md`, commit, re-run the same
BASE gate over the new commit `ea07520ee2622c54a463b207159823d04383e01e`):

```
SUMMARY	findings=0	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=29	status_lines=79	carry_heading=1	checked_reports=94
```

rc 0, `LG-SEAT-UNCARRIED` count = **0**. `checked_markers=29` is unchanged, so no marker disappeared —
every one of the 29 is now carried.

3. NO-FLEET-ROOT RUN at the same green commit: `3 LG-DANGLING-PTR` — exactly the three
`.ufo/waves/hyaku/...` pointers already present at lane HEAD, so the appended section introduced no
pointer. (A first draft that cited the wave delivery path in its preamble added a fourth; it was
replaced with a pointer-free sentence before the recorded run.)

4. LOAD-BEARING CONTROL (the carry can fail): deleting the single `ScribeLOG.md` bullet from the green
lesson in a scratch commit `44935719f47e2d00944d27bbcccbf345b11cd3cb` gives rc 1 and

```
LG-SEAT-UNCARRIED	census/round-27/waves/w1/ScribeLOG.md	line 2: STATUS: PARTIAL — drafted the Round27 LOG append entry from observed W1 artifacts; C1/C2/C3 acceptance results remain unobserved and L1 integration is pending.
SUMMARY	findings=1	...	checked_markers=29	...	carry_heading=1	checked_reports=94
```

The clone was reset to `ea07520e` afterwards; nothing else changed.

## Block to append (verbatim, after a blank line at end of `corpus/lessons/round-27.md`)

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

## Disposition basis (one line per carried entry)

Rule applied: `resolved@<lane commit>` only where the paragraph states a repo-state defect that the
landed bytes no longer show and the first lane commit that removed it can be named; `open` where any
stated defect or the named missing receipt still stands at HEAD, and for report-level items delivered
only outside the lane (a fleet-report sentence is not a lane commit). Every claim below was checked by
opening the named path at lane HEAD `1b811368461785040e955f41f9c97e62f61fd67c` or by running the
command shown.

| # | entry | disposition | basis |
|---|---|---|---|
| 1 | CritC3Attack.md:2 | open | Both drafts are now installed (`tools/souji-pre-report-gate.sh`, `tests/fixtures/r27-pre-report-gate.sh` at `6cb22dc`), but the second clause holds: the fixture's four cases never exercise the `check-report` or `check-prereg` red paths (`setup()` always writes both files), so it still does not establish all five check semantics. |
| 2 | CritCounterFidelity.md:5 | open | The false-`gate_sha256` clause is gone: `census/round-27/records/c1-before.tsv` (landed at `6cb22dc`) pins `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd`, which this run reproduced as `sha256(git cat-file -p e78ac7c:tools/souji-landing-gate.py)`. The fleet-root dependency and the unbound C2 receipts stand: the gate still resolves fleet pointers with a live `os.path.exists`, and `c2-before.tsv`/`c2-after.tsv` have no digest column. |
| 3 | CritErrorPatterns.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | The objects the review lacked now exist: fixture at `6cb22dc` and the landed counters `census/round-27/records/c1-after.tsv`, `c2-after.tsv`, `c3-after.tsv` (rev `6cb22dc`) committed in `c973d1a1`. |
| 4 | CritNoHarmAttack.md:2 | open | `--prereg` is now mandatory and the registry row exists, but the exemption-masking risk stands: the three rows of `corpus/pointer-exemptions.tsv` carry a path plus reason text only — no finding identity and no expiry. |
| 5 | CritReportContract.md:5 | open | The wave-shape/planner record exists only in `/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/souji.md:11` (fleet repo, not a lane commit), and no lane check rejects `[PENDING]` residue before filing (`grep -rln PENDING tools/ tests/fixtures/` is empty). |
| 6 | ExecC1Counter.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | The deliberately deferred live run is recorded: `census/round-27/records/c1-after.tsv` row `6cb22dc…  02b58f81…  2  52  2`, committed in `c973d1a1`. |
| 7 | ExecC3Counter.md:2 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | Gate and fixture both exist at `6cb22dc`, and the receipt `census/round-27/records/c3-after.tsv` records `cases=4 pass=4 control=FALSE-GREEN-REJECTED rc 0` with `tool_sha256 a9d9f520…` at that rev. |
| 8 | ExecCensusAfterScript.md:2 | open | No after-integration census receipt was committed for round 27: `census/round-27/records/` holds c1/c2/c3 receipts, the preregistration, rows/quarantine/slice tables and `sources-census-after.out` — no census-after output; the drafted `w1/census-after.sh` has no committed run. |
| 9 | ExecKnowledgeMechanism.md:2 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | `census/round-27/sources/glocalfile.c`, `gfileutils.c` and `SHA256SUMS` are committed there, with the entry headers' pins `66b588c4…` and `5161ae43…`, and the assimilation checks produced `sources-census-after.out`. |
| 10 | ExecPycacheFix.md:2 | open | The named tracked blob is still tracked at HEAD: `git ls-tree -r --name-only HEAD` lists `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` |
| 11 | ExecScorecardDraft.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | `SCORECARD.md:27-35` carries the round-27 before/after block with a counting command and measured commit per row, and the block contains no `PENDING` token (grep count 0). |
| 12 | LabGitIgnoreProbe.md:4 | open | Same falsification still holds at HEAD: 5 tracked `__pycache__` blobs, including the r10 `.pyc`. |
| 13 | LabSliceFetch.md:2 | open | The union persists in the landed record: `corpus/lessons/round-27.md` Gate — "S118 unverifiable because the registered DOI payload remains unavailable"; S119 stays rejected. |
| 14 | RevC2Entries.md:2 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | Both landed entries (`corpus/knowledge/origin-record-writer-r27.md`, `origin-record-mechanism-set-r33.md`) now carry `## Gate` sections with `opened: 2026-10-25` and `verified-at: 2026-10-25`, and `corpus/README.md:42` lists both in the F4 coverage-map row. |
| 15 | RevC2Rows.md:4 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | `corpus/SOURCES.md:154` (S152) no longer cites S146 (`grep S146` on that row: 0), and no landed row dangles: the gate at HEAD with `--fleet-root` reports zero `LG-DANGLING-PTR` for round 27. |
| 16 | RevC3Fixture.md:4 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | The success line is no longer unconditional in the installed bytes: `tests/fixtures/r27-pre-report-gate.sh` increments `passes` only inside `expect` and prints the frozen line only when `failures == 0 && passes == 4`, else a derived line to stderr with rc 1. |
| 17 | RevC3Gate.md:4 | open | The read-only breach is fixed (`export LC_ALL=C GIT_OPTIONAL_LOCKS=0` and `git --no-optional-locks`), but the false-PASS vectors stand: the unset list omits `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0`, `status --porcelain=v1 --untracked-files=all` still hides ignored files, and the heading test is still the prefix `grep -c '^## SHONEN'`. |
| 18 | RevMistake.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | The landed Mistakes row cites `corpus/lessons/round-26-verifier-spotcheck.md:13`, and line 13 is the routed leftovers defect, so the citation resolves; the frozen four-case test is committed at `6cb22dc`. |
| 19 | RevNoHarm.md:7 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | The staged dangling `corpus/` pointer did not land: the gate at HEAD with `--fleet-root` shows no `LG-DANGLING-PTR` for round 27, and `c1-after.tsv` records `findings=2`, not 3. |
| 20 | RevReportIntegrity.md:5 | open | The wave-shape/planner record and the 79-seat count landed only in the fleet report (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-27/souji.md:11`); no lane pre-filing zero-placeholder check exists. |
| 21 | ScoutScorecardState.md:4 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | (d) the planned r28 bullet exists at `SCORECARD.md:223`; (i) the committed preregistration parses — `python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`; (ii) `c1-before.tsv`'s `gate_sha256` equals the gate blob sha256 at `e78ac7c` (recomputed). |
| 22 | ScribeInvariant.md:2 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | That commit's only SKILL.md change is `+1/-1`: the `\| souji-pre-report-gate \| gate \| ...` registry row now at `SKILL.md:226`; the C3 delivery/test claims were measured in `c3-after.tsv`. |
| 23 | ScribeLOG.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | `LOG.md:1743` carries "Round 27 attempt 2" with the C1/C2/C3 outcomes, the 79-seat wave and the leftovers. |
| 24 | ScribeLessonGate.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | `corpus/lessons/round-27.md` `## Gate` landed there with ADMIT S152/S210/S211, dated located quotes and the S119 REJECT. |
| 25 | ScribePrereg.md:2 | resolved@6cb22dc20c9fdb3c7a49eaa1accabca339054c17 | The committed copy `census/round-27/records/preregistration.txt` parses under `tools/souji-axis-check.py` (`claims=3 flags=0`), so the delimiter refusal no longer applies to the landed preregistration. |
| 26 | ScribeReport.md:2 | open | The report-level items (integration measurements, landed revision, trends, SHONEN verification, stale-lane) were delivered in the fleet report, outside the lane; the lane's own lesson still has no Trend verdicts section, so no lane commit discharges them. |
| 27 | ScribeScorecard.md:2 | resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0 | The same `SCORECARD.md:27-35` block replaced the `[PENDING]` landing-tip values with values measured at `6cb22dc`. |
| 28 | SimplExistingTools.md:2 | open | No removal was made or recommended in the landed round-27 record: `corpus/lessons/round-27.md` `## Residuals` keeps the 36 inherited r26 wave files in place. |
| 29 | SimplWaveSpec.md:2 | open | The committed spec still states the stale count (`census/round-27/waves/w1-spec.json` contains `80-item`) while the landed record counts 79 seats; the artifact was never corrected. |
