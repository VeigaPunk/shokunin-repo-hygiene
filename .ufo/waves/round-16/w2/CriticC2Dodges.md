# CriticC2Dodges — round 16 w2 (critic, calibration)

Target: the LG-SEAT-UNCARRIED failure channel after L1 revision 2:
`tools/souji-landing-gate.py:62-78` (`STATUS_PREFIX_RE`, `FAILURE_STATUS_WORDS`),
`:248-270` (`status_value`, `is_failure_line`), `:273-284` (`seat_failure_lines`).
Bytes: gate sha256 `e7d2439d…cb3f2`, fixture `tests/fixtures/r16-landing-gate.py`
sha256 `aae67c9c…13f2f`. Both are identical at the assigned HEAD `a6ec781`, at the current
HEAD `163158a` (the lesson commit that landed after dispatch), and in the worktree.
`git diff --stat` between all three is empty for gate, fixture and seat-audit.

Method: source reading plus an exact read of the 63 committed w1 reports
(`git cat-file --batch` on named paths at HEAD). This item is not ALLOWED-EXEC, so I
**did not run** the gate, the fixture or any regex. Every "missed" verdict below is derived
by hand from the cited code lines and Python `re` semantics. L1 should confirm it with the
falsifiers in §5.

Axis: **calibration**. Verdict: **partial**.

The channel holds for lines in the exact contract form. Fixture case 9 confirms this
(`r16-landing-gate.py:391-415`: SeatA/B/E/G are flagged), and so does the r15
`ConfigRepair.md:7` replay. The "misses are contract breaches, not gate defects" framing
holds only in part:

1. Only wave 2 has a vocabulary mandate. Every corpus the gate was measured on predates it.
2. Some misses remain even when a line follows the contract word for word. Those are gate defects.
3. For w2, the misses that really are breaches have no auditor today.

## 1. Which contract applies where (decides "breach" vs "defect")

| corpus the gate reads | committed contract text on STATUS | vocabulary mandated? |
|---|---|---|
| r13 replay `a31642d` (`.ufo/waves/round-13/w1-spec.json` context) | none: the context has no STATUS clause | no |
| r14 replay `cc21683` (`round-14/w1-spec.json` context) | none | no |
| r15 replay `b410186` (`round-15/w1-spec.json` context) | none: "Reports concise with exact lines, actionable findings and unrun checks." | no |
| r16 w1, 63 reports at HEAD (`round-16/w1-spec.json:3`) | "any known failure on a line starting `STATUS:`" | **no**: free wording |
| r16 w2 (`round-16/w2-spec.json:3`) | "A known failure goes on a line `STATUS: FAIL — <text>` (or INCOMPLETE/BLOCKED/PARTIAL); otherwise `STATUS: ok`." | **yes** |

Counterexample to the design comment at `tools/souji-landing-gate.py:65`: it says the
vocabulary is "the pinned failure vocabulary the wave contract requires seats to use". That
is false for every replay that measured the revision (r13/r14/r15) and for all 63 r16 w1
reports at HEAD. The r15 replay hit only because ConfigRepair happened to choose
`INCOMPLETE`. A miss in those corpora cannot be a seat's breach. It is a recall limit of the
gate, and it must be disclosed as one.

## 2. Measured recall on the w1 corpus (L1's own judgment as ground truth)

The lesson's hand-carried w1 list (`corpus/lessons/round-16.md:43-54`) names 12 STATUS lines
that L1 judged to be failures or defects. Their first value words, under the gate's tokenizer
(`:268-269`), are:

| report:line (lesson anchor) | first word the gate sees | in `FAILURE_STATUS_WORDS`? |
|---|---|---|
| ConnLogConvention.md:385 | `incomplete` | yes (a quotation of r15, not an r16 failure) |
| CriticNoHarmPreharm.md:14 | `residual` | no |
| MutateDirtyFilters.md:5 | `survived` | no |
| MutateScanConfig.md:2 | `probe` | no |
| SentinelCommandExec.md:91 | `f1` | no |
| CriticNamespaceWeakening.md:5 | `source` | no |
| RevengeFrozenPin.md:202 | `` `b5187351…` `` | no |
| RevengeInertKeys.md:245 | `r16` | no |
| SrcGitCheckAttr.md:113 (`**STATUS: PROBE RULE breach…`) | `probe` | no |
| SrcBashSetN.md:129 (under a colonless `## STATUS` heading at :127) | `live` | no |
| CriticGateVacuity.md:140 | `gate` | no |
| DraftLessonGate.md:98 | `skeleton` | no |

Result: **0 of 11** genuine r16 w1 failure lines are visible to the channel. The only visible
line is a quotation. All 11 reached the lesson only because L1 carried them by hand. The gate's
green at HEAD therefore certifies nothing about w1 carry.

I mapped artifact offsets to file lines and checked the mapping against 4 lesson anchors
(:14, :91, :129, :202), all exact.

### 2a. Failure-bearing w1 STATUS lines that neither the gate nor the lesson carries

Lesson `round-16.md:41` claims the list covers "every failure-channel STATUS line and every
non-ok STATUS line that reports a defect". These committed lines report a known failure or a
defect on the STATUS line itself, and none of them appears in `round-16.md:39-61`.

I did not check whether each was later fixed. Where that is open I wrote "disposition
unknown", not "unresolved".

| report:line | text on the STATUS line (verbatim excerpt) | gate first word |
|---|---|---|
| ConnQualityCriterion.md:203-204 | "draft complete and paste-ready; … Known failure carried: Q25(b) is red at HEAD `cbf688ab` until the r15 frozen pin and `measured_commit` are re-bound." | `draft` |
| CriticFixtureOverfit.md:49 | "findings advisory. … HARM_CASES omits 18 and 20 … tools/souji-preservation-evidence.py still holds the r15 class table and was not migrated. Known failure: none of this seat's conclusions were confirmed by a run." | `findings` |
| RevScanParse.md:206 | "no defect in the `scan_config_file` key/subsection/variable split; RSP-1 (High) is a real filter-execution bypass …" | `no` |
| SrcGitConfigIncludesRecheck.md:295 | "… C1's 'only a protected-namespace reach keeps whole-run exit 2' is contradicted by `usage_err` and by non-namespace `protected_fail` classes …" | `source` |
| RevStatusInfoFile.md:213 | "review complete. … F3/F4/F5 remain live in both cbf688a and the worktree." | `review` |
| RevRedaction.md:214 | "no defect found that breaks either fixture oracle; three real but narrow issues (F1 …, F2 …, F3 unredacted `--compare` baseline echo)" | `no` |
| RevGateSpec.md:226 | "review complete — … C2's contract needs P1–P9 applied … and cannot be green at cbf688a as written." | `review` |
| RevFixtureR16Edits.md:237-239 | "review complete … F4 must be re-pinned or retired." | `review` |
| SrcGitStatusRejected.md:66 | "ok; … S042's row cites installed 2.55.0" (installed is 2.56.0) | `ok` |

At minimum ConnQualityCriterion:203-204 (literally "Known failure") and RevScanParse:206
(a High-severity defect) meet L1's own line-41 criterion. Smallest fix: carry them with
`open`/`resolved@<hex>`, or narrow the wording at line 41.

Also, 9 committed w1 reports have **no** line-initial STATUS line in any shape:
LandingGate, PlanWalk, RevBoundFilters, RevHeaderDocs, RevIncludeResolve, RevMatrixRunner,
RevSoftPropagation, ScoutAltRefsConsumers and SrcPythonAst. Under the w1 contract that is
legal (it means "no known failure"). Under the w2 contract it would be a breach.

## 3. Rewordings the channel misses (static derivation from the cited lines)

Classes: **G** = gate defect (the line uses the contract word, or the miss comes from the
gate's own structural bug). **B** = w2 contract breach that can be audited mechanically.
**B\*** = w2 breach that needs a human reader. **D** = by design (pinned in the fixture).

| # | line as a seat writes it | why it is missed (code) | class under w2 |
|---|---|---|---|
| A1 | `STATUS: FAIL.` / `STATUS: FAIL, x` / `STATUS: BLOCKED; x` | `:269` strips only `*:—`, so the token is `fail.`, `fail,` or `blocked;` | **G** (contract word present) |
| A2 | `` STATUS: `FAIL` — x `` / `STATUS: [FAIL] x` / `STATUS: _FAIL_ x` / `STATUS: "FAIL" x` | backticks, brackets, underscores and quotes are not stripped (`:269`) | **G** |
| A3 | `STATUS: PARTIAL(3/5) x` / `STATUS: FAIL/BLOCKED x` / `STATUS: FAIL–x` (en dash, no space) | `\S+` at `:268` swallows the glued suffix | **G** |
| A4 | `STATUS: ❌ FAIL — x` / `STATUS: ✗ FAIL` | the first `\S+` is the emoji | **G**, minor |
| B1 | `- STATUS: FAIL — x` / `+ STATUS: …` / `1. STATUS: …` | `:71` allows only `[#*\s]` before STATUS, so a `*` bullet is detected but a `-` bullet is not (arbitrary asymmetry) | **G** for the asymmetry, **B** otherwise |
| B2 | `STATUS – FAIL` (en dash) / `STATUS - FAIL` / `STATUS = FAIL` / `STATUS：FAIL` (fullwidth colon) | `:71` separator is `[:—]` only | **B**; en dash is common autocorrect, so treat it as **G** |
| B3 | `__STATUS__: FAIL` / `` `STATUS: FAIL` `` / `STATUS (w2): FAIL` / `Final STATUS: FAIL` | decoration other than `#`/`*`, or text between STATUS and the separator | **B** |
| B4 | `## STATUS` heading, then `FAIL — x` on the next line | the heading has no separator; the value line has no prefix. Real w1 shape: SrcBashSetN.md:127 | **B** |
| C1 | `> STATUS: FAIL — x` | blockquote: `>` is not in the prefix class. Absent by design: fixture `:402`, `:415` (SeatH) | **D** (quotation suppression) / **B** |
| C2 | the STATUS line inside a ` ``` ` fence or as a `\|` table row | `:263`, `:282`. Absent by design: fixture `:397-400`, `:414` (SeatF) | **D** / **B** |
| C3 | a compliant `STATUS: FAIL — x` placed **after** an earlier line that begins with ` ``` ` but is not a fence delimiter (e.g. an inline ` ```x``` ` at line start), or after a ```` fence that contains a ``` line | `:279-281` toggles `in_fence` on any stripped line starting with ` ``` `, so the state inverts and every later line counts as fenced | **G** (seat fully compliant) |
| D1 | `STATUS: ok — but the selftest still fails 2/38` | first word `ok` | **B\*** (needs a reader) |
| D2 | `STATUS: draft complete; Known failure: …` (ConnQualityCriterion:203 shape) / `STATUS: findings advisory … Known failure: …` (CriticFixtureOverfit:49 shape) | first word is not in the vocabulary | **B** (first word ∉ {ok}∪vocab) |
| D3 | `STATUS: SURVIVED …`, `unverified`, `inconclusive`, `aborted`, `timeout`, `skipped`, `deferred`, `open`, `unresolved`, `degraded`, `NO-GO`, `not ok`, `failures`, `errors`, `regressed`, `blocker` | not in `FAILURE_STATUS_WORDS` (`:72-78`); inflections such as `failures`, `errors` and `regressed` are also absent | **B** |
| D4 | `STATUS: 3/5 checks FAIL` / `STATUS: 2 failing` | the first token is numeric | **B** |
| E1 | U+200B or U+FEFF before `STATUS`, or a homoglyph (Cyrillic `Ѕ`) | `str.strip()` does not remove U+200B/U+FEFF; `re.IGNORECASE` does not fold homoglyphs | adversarial; neither gate nor shape audit sees it. Residual only |

## 4. Decision: breach (auditable) or gate defect?

- **r13–r15 replays and r16 w1: gate limit, not a breach.** No vocabulary existed (§1).
  The lesson already scopes C2 as "not free-prose disclosure" (`round-16.md:21-22`). That
  scope is honest but incomplete. These misses are not free prose: they sit **on STATUS
  lines**, in exactly the channel the gate claims to cover, and §2 measures 0/11 recall there.
- **w2 and later, classes A1–A4, B1-asymmetry, B2-en-dash and C3: gate defects.** The
  seat's line carries the contract word, or the gate's own fence state is wrong. The contract
  cannot absorb these misses.
- **w2 and later, classes B and D2–D4: contract breaches that are auditable in principle,
  but nothing audits them today.** The fixture says a prose-only failure "is a contract
  breach for the seat audit, not a gate finding" (`r16-landing-gate.py:385-387`). The
  seat audit's pinned classes, however, are V-SURFACE, V-LIVE-CENSUS, V-WRITE-SCOPE, V-EXEC
  and V-RECURSIVE over transcripts (`tools/souji-seat-audit.py:10-20`). None of them reads
  report STATUS lines. So "auditable" is currently a claim with no mechanism behind it.
- **D1 (`ok` first, failure later on the line or in prose): breach, not mechanically
  auditable.** This is the tradeoff L1 accepted when it dropped phrase markers (42/42
  quotation false positives). It must be stated as a residual, not implied as covered.

## 5. Smallest safe corrections (advisory; L1 integrates and re-measures)

1. **Tokenizer (fixes A1–A4).** At `:268-269`, take the first alphabetic run after leading
   non-alphanumerics instead of the first `\S+`:
   `first = re.match(r"[^A-Za-z0-9]*([A-Za-z]+(?:-[A-Za-z]+)*)", value); word = first.group(1).lower() if first else ""`.
   Hyphen-joined runs keep `known-good` from collapsing to `known`. A numeric first token
   still yields no word, as it does today, so false positives do not grow on that path.
2. **Prefix (fixes B1-asymmetry, B2-en-dash).** Change `:71` to
   `^[#*+\-\s]*STATUS[*]*\s*[:—–]\s*(.*)$`. Keep `>` excluded, because fixture case 9 SeatH
   pins quotation suppression.
3. **Fence state (fixes C3).** At `:279-281`, recognise a fence opener only if it matches
   `^(`{3,}|~{3,})[^`]*$`, and close only on the same character with a run at least as long
   (CommonMark). Add a held-out case: an inline ` ```x``` ` at the start of a line, followed
   by a compliant `STATUS: FAIL — x` line that must be flagged.
4. **Make the w2 breach auditable (B, D2–D4), bound to the committed contract.** For each
   `.ufo/waves/round-N/wK/` whose committed `wK-spec.json` context carries the vocabulary
   clause, report (new id, e.g. `LG-STATUS-OFFCONTRACT`):
   - a report with zero STATUS-prefixed lines;
   - a STATUS line whose first word is not in {ok, fail, incomplete, blocked, partial}.

   This does not touch r13–r16 w1, which have no clause, so it cannot reintroduce the 10
   false positives per replay that killed revision 1. It also needs no phrase markers.
   Alternative owner: a STATUS-shape class in `souji-seat-audit.py`. Either way the fixture
   comment at `:385-387` must point to a real mechanism.
5. **Documentation drift.**
   - Gate `:62-66`: say the vocabulary is mandated from r16 w2 (`w2-spec.json:3`) and that
     the channel is a lower bound for earlier waves.
   - Fixture docstring `r16-landing-gate.py:21-23` still describes revision 1 ("first word is
     outside the benign allowlist, plus parse/do-not-ship/snapshot_tampered phrase markers").
     Rewrite it to revision 2.
   - Lesson `round-16.md:41`: carry the §2a lines or narrow "every … non-ok STATUS line that
     reports a defect".
   - Lesson `round-16.md:21`: add "channel recall on r16 w1 failure lines: 0/11 (all carried
     by hand)".
6. **Falsifiers to run (L1, ALLOWED-EXEC).**
   - Replay `a31642d --round 13`, `cc21683 --round 14` and `b410186 --round 15` before and
     after fixes 1–3. Expect 0 / 0 / unchanged (5) findings. Any increase is a measured false
     positive that must be listed.
   - Run `--rev HEAD --round 16` and expect no new LG-SEAT-UNCARRIED.
   - Run the fixture with new held-out lines (A1 `STATUS: FAIL.`, B1 `- STATUS: BLOCKED — x`,
     B2 `STATUS – PARTIAL — x`, C3). Each must be flagged.

Impacted axes: calibration (primary). No operability or safety effect: the gate is read-only
and the changes are local to `:71` and `:268-281`.

## Probe disclosure

- Shell and git: only `git -C <lane> ls-tree|cat-file|show|log|rev-parse|diff` on named
  paths and revisions, plus `sha256sum`. One `ls-tree -r --name-only` also listed `tools/`
  and `corpus/lessons/` names (names only, unnecessary breadth for `tools/`).
- The 63 w1 report names were taken from that listing and read via `cat-file --batch` on
  exact `HEAD:<path>` objects.
- read/grep only on exact named files: the gate, the fixture, `tools/souji-seat-audit.py`,
  `SKILL.md`, `corpus/lessons/round-16.md`, and `round-16/{w1,w2}-{spec,dispatch}.json`.
  Further grep/read calls ran on my own tool-output artifacts.
- No gate, fixture, census or regex execution. No writes besides this report.
- No `/var/tmp` scratch was created.
- Tool installs/updates: none.

STATUS: ok — every "missed" verdict in §3 is a static derivation and has not been run; §5.6 gives the commands that would confirm or refute each one.

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only HEAD .ufo/waves/round-16/ corpus/lessons/ tools/
for n in ConnFrontier ConnLogConvention ConnQualityCriterion ConnRoutedLedger ConnScorecard ConnShonen ConnSkillRegistry CriticClaimSeparability CriticDisclosureR3 CriticFixtureOverfit CriticGateVacuity CriticNamespaceWeakening CriticNoHarmPreharm DistillRoutedEvidence DraftLessonGate DraftLessonMistakes DraftOperatorQuestion DraftR15Correction DraftReportSkeleton DraftSkillSection LandingGate LandingGateFixture MutateDirtyFilters MutateScanConfig PlanWalk RevBoundFilters RevFixtureR16Edits RevGateSpec RevHeaderDocs RevIncludeResolve RevLegacySelftestGap RevListReposDoubleScan RevMatrixRunner RevR14NamespaceRetention RevRedaction RevScanParse RevSoftPropagation RevStatusInfoFile RevWorktreeConfigFlow RevengeFrozenPin RevengeInertKeys RevengeProbeRecurrence RevengeR15Landing ScoutAltRefsConsumers ScoutExcludesRelative ScoutFsmonitorValues ScoutGitHostVersion ScoutIncludeIfConditions ScoutPromisorConsumers ScoutStatusHooks ScoutWorktreeConfigSemantics SentinelCommandExec SiblingOverlap SimplifyCensusDiff SrcBashSetN SrcGitCheckAttr SrcGitConfigIncludesRecheck SrcGitNoLazyFetch SrcGitStatusRejected SrcGitattributesFilter SrcGitignoreXdg SrcPythonAst SrcShellcheckSC1046; do printf 'HEAD:.ufo/waves/round-16/w1/%s.md %s\n' "$n" "$n"; done | git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file --batch='=== %(rest) %(objectsize)'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1-spec.json a31642d:.ufo/waves/round-13/w1-spec.json cc21683:.ufo/waves/round-14/w1-spec.json
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only b410186 .ufo/waves/round-15/ && git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -3 -- corpus/lessons/round-16.md tools/souji-landing-gate.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae HEAD -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py tools/souji-seat-audit.py && git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat HEAD -- tools/souji-landing-gate.py tests/fixtures/r16-landing-gate.py
```
