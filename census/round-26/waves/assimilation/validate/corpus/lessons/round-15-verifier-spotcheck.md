author: hyaku closure (non-author integrator, @m_opus)

# Round 15 — non-author closure and verifier spot-check

## Decision

**Status: ok; admitted: false; verdict: rejected-harmed.** The report is substantive and committed, not a marker. Both declared claims are graded **unprovable**, because their acceptance never ran and an unrun check has not passed. Operability is also **harmed**, and this is measured, not inferred. The candidate `tools/souji-census.sh` landed at `b410186` and does not parse. At the baseline it parsed and passed ShellCheck. The lane's own seat report recorded the parse failure and said to revert or complete the file before shipping. L1 landed the file anyway. The report, lesson, SKILL, SCORECARD and LOG call it an "unverified candidate" and never say it does not parse. No lane-authored file and no SHONEN box is changed by this closure.

Reviewed: before `cc2168325768d5356a82c039dcdf787377c55784`, after `b410186cea626a67c92396ac58fbd57fb86876ac`, pre-harm reference `a31642d14006830ec62edf40b0354c3699728c4a`. The closure re-checks commands and committed bytes only. No lane gate, selftest, fixture or census run was executed (PROTOCOL §Gate standard, Closure consequence). The parse checks below are static (`bash -n`, `shellcheck`, Python `ast.parse`). They ran over `git show`/`git archive` bytes in `/var/tmp`, and that scratch directory was removed afterwards.

Driver digest (copied from mutable `.ufo/watchdog.log`):
- `2026-10-20T05:17:17-03:00 launch souji round=15 pgid=2493167 driver=hyaku-inline attempt=1`
- `2026-10-20T06:29:54-03:00 complete souji round=15; hyaku-inline attempt=1`

## Step-1 conformance

| check | command | observed | result |
|---|---|---|---|
| report landed by lane | `git -C <fleet> log --format='%an %H' -- .ufo/reports/round-15/souji.md` | `souji-shokunin 215ba74670a518f07c94efc4738a00f0bf6c6ba7` (2026-10-20T06:29:30-03:00) | ok |
| report after commit | lane `b410186` committed 06:28:00-03:00, report 06:29:30-03:00 | report cites `b410186` and `fc3a8d4` | ok |
| cited hashes ancestors | `merge-base --is-ancestor` for fc3a8d4, b410186, cc21683, a31642d | all `anc ok` | ok |
| pushed | `rev-list --count @{u}..HEAD` → `0`; `ls-remote origin` → `b410186… HEAD`, `refs/heads/master` | | ok |
| no uncommitted round work | `git status --porcelain` → only `?? census/operator-sweep-20261019/` | see the operator-sweep section | ok |
| SHONEN heading | report `## SHONEN`, 4 lines; `SHONEN.md` has 4 boxes | all `[~]` | ok |
| LOG binding | `LOG.md:726` "round 15: repair rejected-harmed configuration support first"; `LOG.md:770` "round 15 operator-stopped landing; claims unprovable" | | ok |
| prompt fidelity | Python `difflib` of `templates/round-prompt.md` vs `.ufo/prompts/souji-round-15.md` §1–5 | 22 changed lines, all `{{LANE}}/{{ROUND}}/{{FLEET_ROOT}}/{{AXES}}` substitutions; §6 hyaku addendum appended; prompt committed by `souji-shokunin` `97fed01` | ok |
| Sources & frontier, trend verdicts | present in report | | ok |

Conformance defects (status-neutral):
- **D1, disclosure omission.** `.ufo/waves/round-15/w1/ConfigRepair.md:7-13` says: "The file in tree does NOT parse. L1 must either complete the repair or revert to `cc21683` before any acceptance run; do not ship this state as working." `git grep -niE 'syntax error|does not parse|not parse|bash -n'` over LOG.md, SKILL.md, SCORECARD.md, corpus/ and census/round-15/ at b410186 finds no such disclosure, and the report has none either. The report's "unverified candidate" framing understates a known non-parsing state.
- **D2.** The report has no explicit cross-domain evidence section; the only touch is SiblingOverlap in SHONEN.

## Per-claim re-check

### C1 operability — unprovable (claim); axis harmed

The author reported a candidate value/effect-aware census plus a 20-ID fixture, with every check UNRUN. Re-derived:

| measurement | command | observed |
|---|---|---|
| census parses, per revision | `git show <rev>:tools/souji-census.sh > f; bash -n f; shellcheck -S warning f` | a31642d `bash-n=0 sc=0` (827 lines); cc21683 `0 / 0` (1539); fc3a8d4 `0 / 0` (1539); **b410186 `bash-n=2 sc=1` (1995)** |
| failure site | `bash -n` at b410186 | `line 1368: syntax error near unexpected token '}'`. ShellCheck 0.11.0: SC1046 at 1324 (`if [ "$INCLUDE_ROOT" = 1 ] …` in `list_repos`) has no `fi`. |
| reachability | `grep -n` of the dispatch at b410186 | arg parsing at 1959 and `run_selftest` call at 1976 come after line 1368, so every entry point, `--selftest` included, stops at the parse error [INFERENCE from bash's parse-as-read semantics; not executed] |
| worktree = HEAD | `git diff --quiet b410186 -- tools/souji-census.sh` | equal |
| tool digests | `sha256sum` | cc21683 = fc3a8d4 = `fcff8b057b3e7dc5…` (the r14 harmed tool); b410186 = `dab4122c997db9b9…` |
| behavioral evidence | `git cat-file -e b410186:census/round-15/verification.json` | absent; no r15 run transcript exists |
| fixture parses | `ast.parse tests/fixtures/r15-census-config.py` | rc 0 (parse only) |

Verdict: the claim is **unprovable**. There is no red-before/green-after and no preservation run. The **operability axis is harmed**. AXES.md:13 defines operability as "scripts that run". The lane's fleet census parsed at the baseline and does not parse at HEAD. `SKILL.md:167` ("Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`") and registry row `SKILL.md:138` now point at a non-parsing script. The SKILL warning ("Do not … use its output for operational decisions") does not say it cannot run. A disclosure would not satisfy the no-trade rule anyway, per the r14 closure. The r14 value-blind harm (routed R1) stays OPEN, and r15 compounds it rather than repairing it.

### C2 calibration — unprovable

| measurement | command | observed |
|---|---|---|
| checker, fixture and runner parse | `ast.parse` on `tools/souji-preservation-evidence.py`, `tests/fixtures/r15-preservation-evidence.py`, `census/round-15/run-verification.py` | all rc 0 (parse only) |
| frozen pins vs committed bytes | `tests/fixtures/r15-preservation-frozen/expected.json` vs `sha256sum` | r15-census-config.py `6314d45d…` matches; r14-census-boundary.py `e6a984b1…` matches; record.json `4749ad07…` matches; **tools/souji-census.sh pinned `b5187351…` matches no committed revision** (cc21683/fc3a8d4 `fcff8b05…`, b410186 `dab4122c…`). A frozen run would therefore be `snapshot_tampered` (could-not-evaluate), not the pinned `clean`. |
| selftest / external / frozen / record tally | committed evidence | none exists; the author declares all of them UNRUN |

Verdict: **unprovable**, with no committed self-test tally, frozen verdict or measured revision to verify. The checker is additive and nothing shows it harming calibration. Not `unprovable-but-better`: I cannot judge an unexercised checker better from its source alone.

Method summary: both claims were re-measured statically (parse, digest, presence of evidence). No gate evidence exists to verify, so nothing was evidence-verified.

### Axes

- **calibration:** unprovable.
- **operability:** harmed.
- **coverage:** unchanged.
- **depth:** unchanged.
- **freshness:** unchanged.
- **adjacency:** unchanged.

`git diff cc21683 b410186 -- SCORECARD.md` keeps the scores at calibration 7 / operability 8 / coverage 8, and the score rows correctly mark r15 UNRUN. The operability score row's "numeric delta 0" is contradicted by the parse regression above.

## Discernment spot-check (`corpus/lessons/round-15.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S041, non-author r14 closure | admit, A, mined | `git show cc21683:corpus/lessons/round-14-verifier-spotcheck.md`, line 7 | agree | The quote "Honest disclosure does not satisfy the protocol's no-trade admission rule." is present verbatim on line 7 (10 words). Anchor lines 104–106 (no-harm judgment) and 160–164 (routed defects 1–5) resolve. Own-work tier A is properly scoped. |
| S042, git-config(1) | admit, A, mined | https://git-scm.com/docs/git-config (served "last updated in 2.56.0"), re-opened 2026-10-20 | agree | The Includes sentence "The contents of the included file are inserted immediately, as if they had been found at the location of the include directive." is present (22 words, ≤25). The core.hooksPath `/dev/null` "disable all hooks" text is present, so the value-effect grounding is correct. |
| git-status(1) as a new row (draft S047) | reject (registry exclusion, search-log line) | https://git-scm.com/docs/git-status (served "last updated in 2.53.0") | agree, with a caveat | `--porcelain` text "remain stable across Git versions and regardless of user configuration" is present. It corroborates output format; it does not say which config values abort or neutralize, so excluding it as primary grounding is sound. Caveat: the opened and excluded source exists only as search-log prose, not as a `rejected` registry row (minor; routed R7). |
| C1/C2 admission | reject (unprovable, not admitted) | `census/round-15/disposition.json`; absent `verification.json` | agree | No measured after exists. The lane's refusal to self-admit is correct. |
| sources-draft S043–S046 as separate rows | reject (folded into S042) | `census/round-15/sources-draft.md` at b410186 | agree | They are subsections of one document. Counting them separately would inflate source growth. |

Newly written row check: S042's quote location is lesson line 22 and the quote is 22 words. S041's anchors resolve as above.

SOURCES census re-derived by this closure over `git show <rev>:corpus/SOURCES.md` (anchored `^\|\s*S\d{3,}\s*\|` rows, Counter over tier/status cells):
- before: 40 rows, `{'A': 36, 'B': 3, 'C': 1}`, `{'mined': 23, 'queued': 15, 'rejected': 2}`
- after: 42 rows, `{'A': 38, 'B': 3, 'C': 1}`, `{'mined': 25, 'queued': 15, 'rejected': 2}`
- digest: `sha256` of b410186 SOURCES.md = `5185720f8dfdf1a9a5e69143e61d1dfe99c3116adc058c7c6768a1217999662d`

All three match the report. The diff adds only S041/S042 plus one search-log line; no old row was touched.

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` gave exit 0:

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

## Trend verdicts

- **expansion: unchanged.** Agrees with the author. No knowledge entry or capability was admitted, and two registry rows are not expansion.
- **quality: harmed.** Disagrees with the author's `unchanged`. LEARNING.md counts quality as harmed when "an entry is found false or stale and left unmarked". The lane's own seat found its census script non-parsing (ConfigRepair.md:7–13). The held instruction `SKILL.md:167` and registry row `SKILL.md:138` were left marked only "unverified", not "does not run". Operability feeds this trend (LEARNING.md §Relation to the axes).
- **discernment: improved.** Agrees with the author. The r14 outside disagreement became lesson R15-M1 and grounded criterion Q22, with Q23/Q24 grounded in R15-M2/M3 (`corpus/QUALITY.md` "Round 15 criteria"). This spot-check agrees with the sampled admits and rejects.

## Operator-sweep directory (`census/operator-sweep-20261019/`)

**This is operator sweep output, not lane round work.** Evidence:
- The scripts say so in their own headers. `run-one-chunk.sh:2` reads "Operator sweep 2026-10-19 — one verify chunk (kotodama .scratch children)". `stage-hold-delete.sh:2` reads "souji operator sweep 2026-10-19 — stage (same-device mv) -> hold >=450s -> second check … -> rm -rf".
- The contents are fleet-wide hygiene data: a per-repo census (`census-before.tsv`, 22 repos), kotodama `.scratch` verify chunks and results, live-reference probes, staged/removed TSVs, and lore-scratch verdicts.
- All files carry mtimes from 2026-10-19 22:32–22:47 (one preserved file is dated 2026-10-18). That is before the r15 launch (2026-10-20 05:17) and before r13.
- r13 and r14 wave contracts already name it as operator-authored and forbid touching it (`.ufo/waves/round-13/w1-spec.json:3`, `round-14/w1-spec.json:3`). The r15 report (line 30) and `census/round-15/before.json` record it as operator-owned.
- Metadata fingerprint `find … -printf '%P\t%y\t%s\t%T@\t%m\n' | LC_ALL=C sort | sha256sum` = `f6a844662f23ec8b0026d3f48bb19d8b27bb137f7ebd57e273c201b8539782b8`, 155 entries, 152 `status -uall` lines. This is identical to the r13 SafetyOperator fingerprint, so the directory has not changed since r13.
- `git log --all -- census/operator-sweep-20261019` finds 0 commits, and the path is not ignored.

It is therefore not uncommitted lane debt. This closure read sample files to classify it and changed nothing. Its disposition (commit, `.git/info/exclude`, or relocation) is operator-owned.

## Routed defects (souji next round unless noted)

1. **R1, admission-blocking operability regression (new).** Restore a parsing `tools/souji-census.sh`: either complete the `list_repos` `if` at line 1324 (missing `fi`) or revert to the `cc21683` bytes. Then show `bash -n`, `shellcheck -S warning` and red-before/green-after under the committed fixture. Append a LOG correction entry naming the non-parsing landing. Sweep SKILL.md:138/167, SCORECARD's operability row ("numeric delta 0"), and the r15 lesson and report wording per §Evidence standard "Corrections sweep every mention".
2. **R2, r14 R1 still OPEN.** The value-blind benign-config repair remains admission-blocking, now compounded by R1.
3. **R3, disclosure.** A seat-reported known failure (ConfigRepair.md:7–13) must reach the L1 report and lesson verbatim. "Unverified candidate" must not stand for "known broken".
4. **R4, C2 frozen pins.** `tests/fixtures/r15-preservation-frozen/expected.json` pins `tools/souji-census.sh` at `b5187351…`, which no committed revision has. Re-pin after R1 and record the frozen verdict with its measured revision.
5. **R5, process (r14 R4 recurrence).** Q24 landed, but seats again ran prohibited probes or queries (LinkedPreserve `find -P`; SkillWording/ReportContract whole-lane search reaching the operator sweep), as the lane disclosed. Enforce it, don't just record it.
6. **R6, report contract.** Add an explicit cross-domain evidence line (D2).
7. **R7, minor curation.** Consider a `rejected` registry row for git-status(1), opened and excluded this round, so the reject is curated in the registry rather than only in search-log prose.
8. **Operator (not lane).** Decide the disposition of the untracked `census/operator-sweep-20261019/`.

SHONEN: all four boxes are `[~]` and none is checkable by a non-author as passing. In particular, "Instructions executable by an agent without oral context" fails while SKILL.md:167 points at a non-parsing script. This is not promotion-ready; promotion stays operator-owned.

Tool installs/updates by this closure: none.
