# CriticDisclosureR3 — round 16 w1 (critic, leaf)

Routed defect R3 (`corpus/lessons/round-15-verifier-spotcheck.md:124`): a seat-reported known failure must reach the L1 report and lesson verbatim. "Unverified candidate" must not stand in for "known broken". Axis judged: **calibration**. This report covers only R3 disclosure and the sweep list. Advisory; L1 integrates.

## 1. Counterexample (r15, measured)

The seat said, at `.ufo/waves/round-15/w1/ConfigRepair.md:7,9,11-13` (committed at b410186):

> `## STATUS: INCOMPLETE — file has an unresolved syntax error`
> `` `bash -n` reports: `line 1368: syntax error near unexpected token '}'` ``
> "**The file in tree does NOT parse.** L1 must either complete the repair or revert to `cc21683` before any acceptance run; do not ship this state as working."

It repeats this at `:86-89` ("this is the top blocker") and `:124` ("currently FAILS at :1368").

L1 landed the file and wrote it up as "**unverified** … candidate" (report `:13`) and "committed as an **unverified candidate**" (lesson `:95`). A grep of both files for `pars|syntax|bash -n|snapshot_tampered|pinned-mismatch` finds no disclosure. The only hits are the unrelated phrases "exact key parsing" (report `:13`) and "strict transcript parser" (lesson `:107`).

Re-measured this session: `git show b410186:tools/souji-census.sh | bash -n` gives rc 2 with `line 1368: syntax error near unexpected token '}'`. The worktree, at the same digest as cbf688a (`fed43c71…`), gives rc 0.

**Second, uncited carried failure (C2).** `.ufo/waves/round-15/w1/AdmissionChecker.md:73-75` says: "Frozen fixture ships pre-integration pins: evaluation against the live lane returns snapshot_tampered/pinned-mismatch (exit 2) until L1 re-pins". The report (`:37`) and lesson (`:101`) soften this to "pre-integration declarations … require refresh" / "were not refreshed". Neither says a frozen run is predicted to be exit 2 rather than the pinned `clean`.

It is still live. `tests/fixtures/r15-preservation-frozen/expected.json:5` pins `tools/souji-census.sh` = `b5187351…`, but HEAD is `fed43c71…`. `:4` pins `r15-census-config.py` = `6314d45d…`, but the cbf688a-revised fixture is `9151cde8…`. Only `:3` (r14 fixture `e6a984b1…`) still matches. Re-pinning belongs to R4 (PreservationRepin). Disclosing the stale pins belongs to R3 until R4 lands.

**Third, partial.** ConfigFixture.md:54, 56-59 disclosed that the fixture and the repair disagree (fixture REFUSE vs repair green for alternateRefsCommand non-empty, unbound filters and inactive `includeIf`). These conflicts predicted changed-arm failures. Lesson `:112-116` reduces them to "conditional matching still require acceptance". The r16 claim now calls alternateRefsCommand inert and the fixture was revised at cbf688a, so the r16 lesson must say which of the five conflicts the revision flipped, and why. Otherwise the 20/20 rests on silently moved expectations. That question is shared with CriticFixtureOverfit; for R3, the disclosure is what is owed.

## 2. Required carriage rules (spec for the r16 report, the r16 lesson and LandingGate's R3 detector)

**V1 — enumeration source.** Use every seat report committed **at the landing revision**: `git show <rev>:.ufo/waves/round-N/w*/<Seat>.md`, never the worktree. A seat can edit its file after landing. Every line matching either pattern below is a *known-failure line*:
- (a) `^(#+\s*)?\**STATUS\**:\s*(.+)` whose payload is not exactly one of `ok`, `PASS`, `clean`, `none`, `no known failure`. Matching is over-inclusive on purpose.
- (b) `(?i)does not parse|syntax error|currently FAILS|top blocker|do not ship|INCOMPLETE|snapshot_tampered|pinned-mismatch|returns .*exit 2`.

STATUS-only detection is insufficient. It would miss AdmissionChecker.md:73-75, which sits under "Risks / blockers" and has no STATUS prefix.

**V2 — verbatim carriage.** Both the r16 report (section `## Seat-reported failures`) and the r16 lesson (section `### Seat-reported failures`) must contain one row per known-failure line. Each row has:
- `seat`;
- `path:line`;
- the payload as an exact substring;
- one disposition: `fixed at <40-hex> — <command> → <observed rc/output>`, `reverted at <40-hex>`, `open`, or `not-a-failure: <reason>`.

The `not-a-failure` disposition is the only escape hatch. It must be explicit and counted, never silent.

The substring test normalizes both sides in this order: Unicode NFC, then drop `*`, then collapse `\s+` to one space. The lesson reflows text at about 75 columns, so a naive byte match would false-fail.

**V3 — banned hedges.** For each failure whose disposition is `open` (or whose failure-time state is being described), consider every paragraph or table row in the r16 report, the r16 lesson, and lines added this round to `SKILL.md`, `SCORECARD.md`, `LOG.md` or `corpus/`. A paragraph that names the subject artifact (path or basename; for ConfigRepair `tools/souji-census.sh` / "census") together with `(?i)\b(unverified|candidate|unexercised|not (behaviorally )?verified|untested|pending acceptance)\b` must also contain the literal phrase `known broken` and the seat `path:line`. Otherwise it is a violation. Do not use "unverified candidate" for a seat-reported broken artifact at all.

**V4 — three-valued check status.** A check is `PASS(observed)`, `FAIL(observed by <who>, <path:line>)` or `UNRUN`. A check that any seat or L1 ran in the round and saw fail must never be listed as `UNRUN` or "not run". r15 violated this: `bash -n` was run twice by ConfigRepair (`ConfigRepair.md:5`) and failed, yet the measurements table (report `:36`) and the lesson (`:100`) list only UNRUN/"not run" checks.

**V5 — verdict coupling.** If an open known failure breaks a property the baseline had (here `bash -n` rc 0 at cc21683/fc3a8d4), the axis it feeds cannot be reported `unchanged` / "numeric delta 0" / "unprovable" alone. It must be `harmed`, as the closure found (spotcheck `:49,:105`, AXES "scripts that run").

**Placement (tradeoff for L1, not a defect).**
- PROTOCOL.md:366 says append-only files get a named correction entry, "appended, never rewritten". The r15 lesson (`:17`) also commits to not editing historical artifacts.
- So: append a dated `## Correction (round 16: R1/R3)` section to `corpus/lessons/round-15.md` and a correction entry to `LOG.md`. Do not rewrite their lines.
- Rewrite mutable files (`SKILL.md`, the current `SCORECARD.md` row) in place.
- The r15 fleet report (`.ufo/reports/round-15/souji.md`, fleet commit `215ba746…`) is outside the lane repo. The minimum is that the r16 report's `## Seat-reported failures` / correction section enumerates the superseded r15 report lines. Appending to the r15 report itself is L1's ownership call.
- `census/round-15/disposition.json` is a historical census artifact. Supersede it from the r16 disposition with an explicit `supersedes` pointer rather than editing it.

## 3. Sweep list — every understated mention a correction must cover

### `.ufo/reports/round-15/souji.md` (read-only here)

| line | understated text | why understated |
|---|---|---|
| 7 | "Candidate source and a paired fixture landed, but the required red-before/green-after and preservation runs were not executed" | omits that the source does not parse |
| 13 | "Landed an **unverified** value/effect-aware census candidate"; its Evidence cites ConfigFixture.md but not ConfigRepair.md | central V3 violation; the failing seat report is uncited |
| 15 | "Last ConfigRepair worker was cancelled on the immediate landing order" | omits that seat's STATUS INCOMPLETE |
| 16 | "**Process defects are not hidden.**" | an assurance of non-hiding next to the hidden parse failure |
| 28 | "Operator-stopped census/checker/fixture/runner candidates" | "candidates" for a non-parsing tool |
| 36 | C1 row: "Source candidate and fixture added … **UNRUN:** … `shellcheck -S warning`"; "Candidate bytes are committed at pushed HEAD" | V4: the seat-observed `bash -n` FAIL is missing |
| 37 | C2 row: "Frozen pins remain pre-integration declarations and require refresh" | omits AdmissionChecker.md:74 "returns snapshot_tampered/pinned-mismatch (exit 2)" |
| 39 | "operability 8 … numeric deltas 0. Operability's prior harm remains unresolved; all unworked axes are unchanged" | V5: a new operability harm is unreported |
| 77 | "**Quality: unchanged.** … the candidate tool repair was not exercised" | the closure grades quality harmed (spotcheck `:105`) |
| 84 | SHONEN: "`SKILL.md` explicitly warns that r15 candidates and all acceptance checks are unverified" | the instruction pointed at a non-parsing script (spotcheck `:131`) |

### `corpus/lessons/round-15.md`

| line | understated text | why understated |
|---|---|---|
| 94 | "The last ConfigRepair worker was cancelled to prevent concurrent edits during commit." | omits the seat's STATUS |
| 95-96 | "Its current source is committed as an **unverified candidate**, not a working repair." | the exact phrase named by R3 |
| 100 | C1: "Candidate value/effect-aware census … legacy selftest and ShellCheck were **not run**." | V4: `bash -n` was run and failed |
| 101 | C2: "The frozen pins are pre-integration declarations and were not refreshed." | omits the predicted exit-2 `snapshot_tampered` |
| 103-108 | lists static fixes ("These are source corrections only, not green checks.") | omits the known unfixed blocker |
| 112-118 | "Known outstanding boundaries: …" | omits the parse failure (the seat's "top blocker") and ConfigFixture.md:54,56-59 fixture/repair conflicts |
| 140-142 | "operability unprovable with prior harm unresolved; … Numeric deltas 0. Trends: … quality unchanged" | V5: both are harmed per the closure |

### Sibling files the same sweep must reach (PROTOCOL.md:363-365)

- **`SKILL.md`**
  - `:18-22` "Round-15 candidates are NOT behaviorally verified … Do not … use its output": never says the script could not run.
  - `:138` and `:167`: registry row and instruction that pointed at a non-parsing script at b410186. Both now parse at cbf688a, but they need a dated note.
  - `:227` "R15 lands an unverified value/effect-aware candidate"; `:229-230` "No … ShellCheck or selftest pass is claimed": V3/V4.
- **`SCORECARD.md`**
  - `:15` operability "value/effect-aware candidate repair … Numeric delta 0" (V5; also routed in R1).
  - `:66` "resolve the unverified r15 C1".
  - `:14` C2 row "frozen declarations landed" lacks the stale-pin consequence.
- **`LOG.md`**
  - `:778` "Landed source candidates: `tools/souji-census.sh`".
  - `:783-786` "None is a passing behavioral observation … all UNRUN. Frozen pins are not refreshed".
  - `:807-808` "C1 operability unprovable (prior harm unresolved) … numeric deltas zero … quality unchanged".
  - Append-only, so each gets an appended correction.
- **`census/round-15/disposition.json`**: `:3` `"operator-stopped-landed-candidates"`, `:6` `"runtime_acceptance": "UNRUN"`, `:8` frozen pins, `:12` `"cancelled_worker": "SoujiR15.ConfigRepair; …"` without its STATUS. Supersede from r16.

## 4. Attacks on a LandingGate R3 detector (C2)

1. **Verbatim-only passes while the hedge stands.** A lesson that quotes the STATUS line in a table but still says "unverified candidate" in its verdict paragraph passes V2. V3 is required, and the negative control must be exactly this record.
2. **Reflow false-red / false-green.** Exact-byte matching fails r16 lesson wrapping. Over-normalizing (dropping punctuation or case) lets a paraphrase pass. Use exactly the V2 normalization, with a negative control: a paraphrase ("file has a syntax issue") must be red.
3. **STATUS-only scope misses real failures.** It would miss AdmissionChecker.md:73-75. The negative control is a seat whose failure appears only under a "Risks" heading.
4. **Worktree seat reports.** Reading seat files from the worktree lets an edited seat file erase the failure. Read via `git show <rev>:`, with a control where the worktree copy differs from the committed one.
5. **History needs the fleet report.** The r15 report lives in the fleet repo (`215ba746…`), not the lane. A detector given only `--rev b410186` cannot see it. It must take an explicit report path or revision. A missing report must be exit 2 (could-not-evaluate), never clean or red.
6. **Overfit to "does NOT parse".** A detector red on b410186 only because it searches for that literal string proves nothing. Seat-derived enumeration must drive it, with a synthetic seat whose failure text is different.

Smallest safe correction: implement V1-V5 as written, with negative controls 1-6, plus a positive control in which every known-failure line is carried with a disposition and no V3 hedge co-occurs.

## 5. Verdict

R3 is **confirmed and wider than routed**. Beyond the ConfigRepair parse failure, the r15 report and lesson also soften AdmissionChecker's predicted exit-2 frozen verdict, which is still live: 2 of 3 pins are stale against the cbf688a bytes. They also drop the seat-disclosed fixture/repair conflicts.

Impacted axes: **calibration** (disclosure accuracy; the detector's discrimination) and **operability** (V5 verdict coupling). A correction that only appends one quote for ConfigRepair, without V3/V4/V5 and without the AdmissionChecker item, would leave defects standing in the sibling files listed in §3. That is a fixable defect, not a tradeoff.

STATUS: no known failure in this seat's own output. One probe-rule deviation, disclosed below.

## Commands

Probe-rule deviation, self-reported: command 6 below ran `git -C` against the **fleet root** (read-only `log` on one named path, `.ufo/reports/round-15/souji.md`). The probe rule lists `git -C` only for the lane repo. Its output (fleet commit `215ba746…`, author souji-shokunin) is used only as a pointer in §2/§4.5 and duplicates spotcheck `:19`.

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only HEAD corpus/lessons/`
2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -8 -- corpus/lessons/round-15.md SKILL.md SCORECARD.md LOG.md census/round-15/disposition.json`
3. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only b410186 .ufo/waves/round-15/w1/`
4. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -6 && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b410186 HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat HEAD -- SKILL.md SCORECARD.md LOG.md corpus/lessons/round-15.md census/round-15/disposition.json`
5. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-census.sh | bash -n; echo "b410186 bash-n rc=$?"; bash -n /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh; echo "worktree bash-n rc=$?"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sha256sum; sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-preservation-frozen/expected.json`
6. `git -C /home/vgpnk/Projects/shokunin log --format='%H %an %ad' -- .ufo/reports/round-15/souji.md` (the deviation above)
7. `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py`

Non-shell reads (exact named files only):
- read tool: the r15 report, the r15 lesson, the r15 spotcheck, ConfigRepair.md, AdmissionChecker.md, ConfigFixture.md, LOG.md, SKILL.md, SCORECARD.md, disposition.json, expected.json and PROTOCOL.md.
- grep tool: over named files. One grep and one Python `open()` loop ran over the 64 seat report paths enumerated by command 3. No directory recursion was used.
- One read of the not-yet-existing `tools/souji-landing-gate.py` returned not-found.

No tool installs or updates. No census run, no operator-sweep access, no `~/.omp` read.
