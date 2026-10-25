# souji — round 23 report (hyaku session) — DRAFT

**This is a draft.** It is delivered at `.ufo/waves/round-23/w1/ScribeReport.md`; the L1
writes `/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/souji.md` itself, fills every
`<PLACEHOLDER>`, and deletes the *Placeholder index* section before landing.

Lane base and measured revision: **`1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`** (branch
`master`). Claims frozen before data in `.ufo/waves/round-23/preregistration.txt` at that base;
axes: **calibration 7 (lowest non-retired), operability 8, coverage 8**.

Every *before* value printed below was measured **this run by this scribe seat at the base
revision** with the command shown; every *after* value, and every commit hash, is a
placeholder. Numbers a seat reports but this draft does not itself re-measure are marked
`[SEAT]` where they appear. Nothing here is an execution claim about a check this seat did not
run.

## Work performed

**Declared claims (3), one per axis.** **C1 — calibration (7, the lane's lowest)**: the four
r22 bookkeeping defects the non-author spot-check routed here (D2 no receipt binds the named
revision, D5 superseded LOG numbers uncorrected, D4 README slice tally wrong, D1 uncommitted
round work) are repaired **and** the lane gains an instrument that re-derives them
(`tools/souji-record-agreement.py`, frozen keys K1–K4), such that the instrument reports
`mismatches=0` at the round tip while the do-nothing control — the same instrument at the base
revision — reports `mismatches>=1`. **C2 — operability (8)**: blob-bound receipts — a runner
that re-derives a counter at a full durable revision and emits a receipt binding
`(rev, tool path, tool sha256 at rev, command, rc, stdout)`, plus a verifier that refuses a
receipt whose recorded tool digest is not the committed blob at the named revision, closing the
spot-check's D3 (r22 after-run measured with tool blob `f26aa728` while the report cited
`5b8025a8…`; no *before* receipt existed at all). **C3 — coverage (8)**: one assimilation theme
(F2 repository size census, the lane's only frontier row with no entry) — 2 entries from
`/home/vgpnk/Projects/shokuknow/merge/souji/`, re-grounded in this lane on 2026-10-25, and
`>=3` registry rows continuing the id space at S115 (staged S112–S114 collide with this lane's
quarantine rows).

Wave: **one** v1 wave, `.ufo/waves/round-23/w1-spec.json`, **41 seats**, dispatched as exactly
one batched `task` call (role tally: 9 scout, 9 scribe, 9 reviewer, 4 critic, 3 executor,
2 revenger, 2 mutation-tester, 1 connector, 1 sentinel, 1 simplifier). Seat reports live under
`.ufo/waves/round-23/w1/`; evidence under `.ufo/waves/round-23/w1/evidence/`. Round total
`<SEATS_TOTAL>` seats (≤128), dead seats `<DEAD_SEATS>`, residual call `<RESIDUAL_SEATS>`.

### C1 — calibration (record agreement)

- **ScoutInherited** (scout) — classified the inherited r22 leftovers file by file: 5 modified
  `.ufo/waves/round-22/attempt2/w1/*.md` seat reports and 2 untracked
  `…/w1/evidence/impl-a/head-c9f1fe3.*` files, with `census/operator-sweep-20261019/` left
  operator-owned and untouched. Evidence: `.ufo/waves/round-23/w1/ScoutInherited.md`.
- **RevRecords** (revenger) — reconstructed, from committed bytes only, every `assertions=…`
  tuple and slice tally the four lane records claim today (`SCORECARD.md`, `LOG.md` *Round22
  attempt2*, `corpus/README.md` r22 sections, `corpus/lessons/round-22.md`). Evidence:
  `.ufo/waves/round-23/w1/RevRecords.md`.
- **ExecFixtureAgreement** (executor) — wrote the C1 fixture (`.ufo/waves/round-23/w1/
  r23-record-agreement.py` → `tests/fixtures/r23-record-agreement.py`): per-key mismatch classes,
  the base-scored do-nothing control, and the always-zero control that must be rejected. Evidence:
  `.ufo/waves/round-23/w1/ExecFixtureAgreement.md`.
- **MutCounter** (mutation-tester) — enumerated every predicate clause K1–K4 must implement and
  designed the mutant list (designed, not run against the lane). Evidence:
  `.ufo/waves/round-23/w1/MutCounter.md`.
- **CritC1Gameable** (critic) — ≥6 cheap moves an author could make to reach `mismatches=0`
  without repairing anything (delete the quoted numbers, move a number to another file, relax K3's
  class-occurrence rule, declare a giant `uncommitted:` exemption list, …). Evidence:
  `.ufo/waves/round-23/w1/CritC1Gameable.md`.
- **ScribeScorecard** (scribe) — drafted the SCORECARD repair: three axis rows plus the new
  capability row, the calibration row carrying the C1 mechanism, its counts line, the receipt path
  and the counting command. Evidence: `.ufo/waves/round-23/w1/ScribeScorecard.md`.

### C2 — operability (blob-bound receipts)

- **RevGateHistory** (revenger) — reconstructed the r22 gate-check digest history (every recorded
  digest with the revision it claims, actual `sha256sum` at base and tip, the tool's log) and
  tested whether the residual seat's `63/61/39/2` tuple reproduces. Evidence:
  `.ufo/waves/round-23/w1/RevGateHistory.md`.
- **ExecFixtureReceiptRun** (executor) — wrote the C2 fixture (`.ufo/waves/round-23/w1/
  r23-receipt-run.py` → `tests/fixtures/r23-receipt-run.py`) against the frozen receipt-v1 header
  order and the refusal path. Evidence: `.ufo/waves/round-23/w1/ExecFixtureReceiptRun.md`.
- **ExecGateReproduce** (executor) — independently reproduced the r22 gate-check before/after in
  `/var/tmp` mirrors of the base and tip trees, with no lane write. Evidence:
  `.ufo/waves/round-23/w1/ExecGateReproduce.md`.
- **MutReceipt** (mutation-tester) — enumerated the runner's clauses (full 40-hex rev, durable-ref
  reachability, `git archive` extraction, digest from the tree at rev not the worktree, `--out`
  outside `/tmp`, no write to the target repo, verify recomputing the digest, malformed-rev and
  missing-tool refusals, header order, real `rc`, stdout/stderr capture) and designed the mutants.
  Evidence: `.ufo/waves/round-23/w1/MutReceipt.md`.
- **CritC2Value** (critic) — asked whether the runner duplicates `tools/souji-rev-pin.py` /
  `census/round-22/attempt2/instrument-digests.txt`, and whether the counter is a capability
  measure or a grep for a string the author types. Evidence:
  `.ufo/waves/round-23/w1/CritC2Value.md`.

### C3 — coverage (F2 size census, one theme, 2 entries, ≥3 rows)

- **ScoutCountObjects** (scout) — opened `https://git-scm.com/docs/git-count-objects` live
  (host git 2.56.0): `-v` field list in page order, located quotes for `garbage`/`size-garbage`
  and `alternate`, installed man-page comparison, access 2026-10-25. Evidence:
  `.ufo/waves/round-23/w1/ScoutCountObjects.md`.
- **ScoutFsck** (scout) — `git-fsck` read-only surface: quotes for `--unreachable`,
  `--dangling`/`--no-dangling`, `--no-reflogs`, `--lost-found`, the default head set, and the
  write-side-effect answer with the page's own path pattern. Evidence:
  `.ufo/waves/round-23/w1/ScoutFsck.md`.
- **ScoutPrune** (scout) — `git-prune` scope, `-n/--dry-run`, `--expire`, the page's `git gc`
  recommendation, and whether `prune -n` reports the same set as `fsck --unreachable`. Evidence:
  `.ufo/waves/round-23/w1/ScoutPrune.md`.
- **ScoutCommunity** (scout) — fetched both staged community sources live (qiita JA, csdn ZH):
  reachability, whether either states the `gc.auto` 6700 threshold or a `garbage` gloss, verbatim
  quote per page. Evidence: `.ufo/waves/round-23/w1/ScoutCommunity.md`.
- **ScoutLocalHost** (scout) — host facts: `git --version`, whether the three man pages are
  installed, one `git count-objects -v` **against the lane repo only**, and whether `garbage` is 0;
  states the read-only basis and that no `fsck --lost-found` ran. Evidence:
  `.ufo/waves/round-23/w1/ScoutLocalHost.md`.
- **ScoutRegistryCensus** (scout) — C3 registry baseline at the base revision: census validate
  exit code and output, row count, max id, tier and status histograms. Evidence:
  `.ufo/waves/round-23/w1/ScoutRegistryCensus.md`.
- **ScoutIdCollision** (scout) — ran the frozen id-collision step in `/var/tmp` (lane ids vs
  staged `SOURCES.append.md` ids, `comm -12`) and proved the indented-row guard. Evidence:
  `.ufo/waves/round-23/w1/ScoutIdCollision.md`.
- **ConnectorSiblingSources** (connector) — sibling-overlap scan for the five URLs across
  `/home/vgpnk/Projects/shokunin/*-shokunin/corpus/SOURCES.md` (read-only): which lane already
  holds a row for each, with id and scope cell, and whether souji's row duplicates it. Evidence:
  `.ufo/waves/round-23/w1/ConnectorSiblingSources.md`.
- **ScribeEntryRepoSize** (scribe) — drafted `corpus/knowledge/repo-size-census-readonly.md` from
  the staged entry plus the three scout reports, with this lane's own `## Gate`, access date
  2026-10-25 and ≤25-word located quotes. Evidence:
  `.ufo/waves/round-23/w1/ScribeEntryRepoSize.md`.
- **ScribeEntryGarbage** (scribe) — drafted the second entry (community/target-language half of
  the `garbage` question). **Path divergence, L1 must resolve:** the frozen preregistration names
  `corpus/knowledge/count-objects-garbage-semantics-r24.md`; this item names
  `corpus/knowledge/count-objects-garbage-readings-r25.md`. The report and the C3 counting
  command below use the **preregistration** path; the L1 must land under one name and say which.
  Evidence: `.ufo/waves/round-23/w1/ScribeEntryGarbage.md`.
- **ScribeSourcesRows** (scribe) — drafted the `corpus/SOURCES.md` append block in the exact
  11-column order: `S115` git-count-objects(1), `S116` git-fsck(1), `S117` git-prune(1), and
  `S118`/`S119` (tier B) only if the community pages proved reachable. Evidence:
  `.ufo/waves/round-23/w1/ScribeSourcesRows.md`.
- **CritC3Ground** (critic) — attacked the F2 credit: does the lane already hold the read side
  (`knowledge/git-repo-structure-readonly.md` and the other entries), so that "frontier, no entry"
  → "entries admitted" is real movement rather than an import of unopened bytes. Evidence:
  `.ufo/waves/round-23/w1/CritC3Ground.md`.

### Records, gates and cross-cutting review

- **ScribeLog** (scribe) — drafted two **append-only** LOG blocks: (1) the r22 attempt-2
  correction entry naming the superseded tuple `assertions=56 resolved=53` and the slice tally,
  carrying the words `superseded by`, without rewriting the filed entry; (2) the round-23 entry.
  Evidence: `.ufo/waves/round-23/w1/ScribeLog.md`.
- **ScribeReadme** (scribe) — drafted `corpus/README.md`'s `### Round 23 corrections` block
  sweeping **every** r22 slice-tally mention to the receipt's tally, plus the F2 map row and
  Frontier note. Evidence: `.ufo/waves/round-23/w1/ScribeReadme.md`.
- **ScribeQuality** (scribe) — drafted two `corpus/QUALITY.md` criteria in the established
  5-column shape: **Q54** (closes D7 — the M17/M22 class whose `captured-by` is `none` gains a
  criterion) and `<Q55_ID>`. Evidence: `.ufo/waves/round-23/w1/ScribeQuality.md`.
- **ScribeLesson** (scribe) — drafted `corpus/lessons/round-23.md` on the r22 shape: claim and
  boundary, `## Mistakes` table (id, class, evidence, captured-by, fix/failure witness),
  `## Gate` with `### Opened sources` / `### Assimilation decisions` (≥1 ADMIT and ≥1 REJECT with
  a flip) / `### Independent expectations and rejected scope`, `## Seat-reported failures`.
  Evidence: `.ufo/waves/round-23/w1/ScribeLesson.md`.
- **RevD1** (reviewer) — D1: reproduced the uncommitted r22 round work (`git status --porcelain`),
  judged it against the "none uncommitted" claim, named the minimal repair. Evidence:
  `.ufo/waves/round-23/w1/RevD1.md`.
- **RevD2** (reviewer) — D2: whether any committed receipt binds the r22 C1 after-state at the
  revision SCORECARD names, and what the minimal binding repair is. Evidence:
  `.ufo/waves/round-23/w1/RevD2.md`.
- **RevD3** (reviewer) — D3: reproduced the tool-blob/`5b8025a8…` disagreement and the absent
  *before* receipt; named the repair and the command that proves closure. Evidence:
  `.ufo/waves/round-23/w1/RevD3.md`.
- **RevD4** (reviewer) — D4: reproduced the README slice-tally disagreement against
  `slice-verdicts.tsv` and listed every mention that needs the correction sweep. Evidence:
  `.ufo/waves/round-23/w1/RevD4.md`.
- **RevD5** (reviewer) — D5: reproduced the superseded LOG tuples and specified the append-only
  correction entry (named superseded value, `superseded by`, filed bytes retained). Evidence:
  `.ufo/waves/round-23/w1/RevD5.md`.
- **RevD6** (reviewer) — D6: reproduced the overbroad reject reason for
  `quarantine-staging-no-copy-r24` and stated the entry-level wording plus the delta it must name.
  Evidence: `.ufo/waves/round-23/w1/RevD6.md`.
- **RevD7** (reviewer) — D7: reproduced the `captured-by: none` rows and the unchanged
  `QUALITY.md`, and named the criterion shape that closes it. Evidence:
  `.ufo/waves/round-23/w1/RevD7.md`.
- **RevD8** (reviewer) — D8: reproduced the stray backtick on the `S118` slice row and the command
  that proves closure. Evidence: `.ufo/waves/round-23/w1/RevD8.md`.
- **RevSHONEN** (reviewer) — audited all four `SHONEN.md` boxes at the base: does each pointer
  resolve at the revision it names, and does it support the box's wording; cheapest change that
  would earn an `[x]` from a non-author verifier. Evidence:
  `.ufo/waves/round-23/w1/RevSHONEN.md`.
- **CritPrereg** (critic) — attacked the preregistration itself: causal separability of C1/C2/C3,
  one-command re-derivability of each after-state, universal clauses without an enumerating
  command, and the lowest-axis obligation. Evidence:
  `.ufo/waves/round-23/w1/CritPrereg.md`.
- **SentinelScope** (sentinel) — security/scope review of the round's surfaces: credential-shaped
  strings, unbounded echo of command output in both new tools' stdout, and the `git archive`
  materialisation boundary. Evidence: `.ufo/waves/round-23/w1/SentinelScope.md`.
- **SimplTouched** (simplifier) — YAGNI pass over the touched files: which new instrument
  duplicates an existing one, which existing helper could host the new checks in fewer lines, and
  what dead weight the touched records carry. Evidence:
  `.ufo/waves/round-23/w1/SimplTouched.md`.
- **ScoutMisroot** (scout) — pre-report misroot sweep of `git -C /home/vgpnk/Projects/shokunin
  status --porcelain` with no pathspec, classifying every untracked entry as self / other-lane /
  orchestrator / operator. `.scratch/` is orchestrator-owned by design and was never touched.
  Evidence: `.ufo/waves/round-23/w1/ScoutMisroot.md`.
- **ScribeReport** (scribe) — this draft. Evidence:
  `.ufo/waves/round-23/w1/ScribeReport.md`.

## Landed changes

Every row maps a change to its `LOG.md` entry and to a helper-confirmed `landed <hash>`; no hash
here is a candidate or a diagnostic. `<LOG_R23>` = the round-23 LOG entry; `<LOG_CORR>` = the
append-only r22 correction entry.

| Change | LOG entry | Commit |
|---|---|---|
| C1 instrument `tools/souji-record-agreement.py` (keys K1–K4) + `tests/fixtures/r23-record-agreement.py` | `<LOG_R23>` | `<COMMIT_C1_TOOL>` |
| C1 base control receipt `census/round-23/records/agreement-control-base.tsv` + after receipt `declared-evidence-after.tsv` | `<LOG_R23>` | `<COMMIT_C1_RECEIPTS>` |
| C2 runner `tools/souji-receipt-run.py` + `tests/fixtures/r23-receipt-run.py` | `<LOG_R23>` | `<COMMIT_C2_TOOL>` |
| C2 four bound receipts (declared-evidence before/after, gate-check before/after) + the stale-digest refusal receipt | `<LOG_R23>` | `<COMMIT_C2_RECEIPTS>` |
| C3 entry 1 `corpus/knowledge/repo-size-census-readonly.md` (+ snapshots) | `<LOG_R23>` | `<COMMIT_C3_ENTRY1>` |
| C3 entry 2 `<C3_ENTRY2_PATH>` (+ snapshots) | `<LOG_R23>` | `<COMMIT_C3_ENTRY2>` |
| C3 registry rows `S115`–`S<REG_MAX_AFTER>` in `corpus/SOURCES.md` | `<LOG_R23>` | `<COMMIT_C3_ROWS>` |
| r22 record repairs: `SCORECARD.md` axis + capability rows, `corpus/README.md` corrections, `LOG.md` correction entry | `<LOG_CORR>` | `<COMMIT_RECORDS>` |
| `corpus/QUALITY.md` Q54/`<Q55_ID>`; `corpus/lessons/round-23.md` | `<LOG_R23>` | `<COMMIT_QUALITY_LESSON>` |
| D1 closure: the 5 modified r22 seat reports + 2 untracked `impl-a/head-c9f1fe3.*` evidence files committed (or reverted) | `<LOG_CORR>` | `<COMMIT_D1>` |
| Wave spec, registry, 41 seat reports, evidence tree | `<LOG_R23>` | `<COMMIT_WAVE>` |
| Final measured numbers and measured revision | `<LOG_R23>` | `<COMMIT_FINAL>` |

Lane tip after landing: `<TIP_REV>`; `jj-lane.sh state` → `ahead=0 behind=0` `<TRACKED_COUNT>`.

## Before → after measurements

One command per claim; both ends of C1 and C2 use **the same tool bytes at the revision they
name**, and each receipt records the tool digest so the pairing is checkable, not asserted.

| Claim | Counting command (lane root) | Before (measured commit) | After (measured commit) | Verdict |
|---|---|---|---|---|
| C1 calibration | `python3 tools/souji-record-agreement.py --rev <full40> --root /home/vgpnk/Projects/shokunin/souji-shokunin` → `keys=K records=R occurrences=O mismatches=M`, exit 0 iff `M==0` | base `1208bfb`: `keys=4 records=<R_BEFORE> occurrences=<O_BEFORE> mismatches=<M_BEFORE>` (must be `>=1`), exit 1 — receipt `census/round-23/records/agreement-control-base.tsv` | tip `<TIP_REV>`: `keys=4 records=<R_AFTER> occurrences=<O_AFTER> mismatches=<M_AFTER>` (target `0`), exit `<C1_AFTER_RC>` | `<C1_VERDICT>` |
| C2 operability | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l`; each receipt re-checked with `python3 tools/souji-receipt-run.py verify <receipt>` | base `1208bfb`: **0** bound receipts (measured by this seat this run) | tip `<TIP_REV>`: `<RECEIPTS_AFTER>` bound receipts, all four `verify` runs exit 0 | `<C2_VERDICT>` |
| C3 coverage | `python3 tools/souji-gate-check.py --entries corpus/knowledge/repo-size-census-readonly.md corpus/knowledge/<C3_ENTRY2_BASENAME> --snapshot-dir census/round-23/sources --expect-slice 0` plus `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | base `1208bfb`: entries absent — `entries=2 ok=0 fail=<GATE_FAIL_BEFORE>`, exit 1; registry 114 rows, validate exit 0 | tip `<TIP_REV>`: `entries=2 ok=2 fail=0`, exit 0; registry `<REG_AFTER>` rows, 0 malformed, 0 duplicate ids, validate exit 0 | `<C3_VERDICT>` |

**C1 control, frozen and exercised.** The cheap control is *do nothing*: the same instrument at
base `1208bfb` must report `mismatches>=1`. Result `<M_BEFORE>` (`<CONTROL_VERDICT>`). The
fixture's cases 2–6 each require ≥1 mismatch, so an always-zero emitter is rejected by the same
harness: `<FIXTURE_CONTROL_LINE>`.

**C2 refusal demonstration (must fire).** `verify` on a receipt whose `tool_sha256` is the stale
r22 `5b8025a8…` value exits `<REFUSAL_RC>` with `RECEIPT-TOOL-DIGEST-MISMATCH`
(`<REFUSAL_RECEIPT>`). A receipt whose `verify` exits 0 while its tool bytes at rev differ from
the recorded digest kills the claim; `<C2_KILL_CHECK>`.

**C3 control (cheap append).** Appending the staged rows as-is (S112–S114) is the control; it
must fail on duplicate id. Receipt `<C3_CONTROL_RECEIPT>`, verdict `<C3_CONTROL_VERDICT>`.

### Verdicts and attacks on record

- **C1 — counter `<C1_COUNTER_VERDICT>`; axis move `<C1_AXIS_MOVE>`.** `CritC1Gameable`'s attacks
  on record: `<C1_ATTACKS>`. Calibration score `<CAL_SCORE>`.
- **C2 — counter `<C2_COUNTER_VERDICT>`; operability credit `<C2_CREDIT>`.** `CritC2Value`'s
  duplication finding: `<C2_DUP_FINDING>`. Operability score `<OPS_SCORE>`.
- **C3 — counter `<C3_COUNTER_VERDICT>`; coverage credit `<C3_CREDIT>`.** `CritC3Ground`'s
  finding: `<C3_GROUND_FINDING>`. Coverage score `<COV_SCORE>`.
- No axis harmed: `<NOHARM_LINE>`.

## Sources & frontier

Counting command (frozen by `CORPUS.md`), run at round start and round end:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```

- **Before** (measured by this seat at base `1208bfb`): `census` exit 0 —
  `rows 114 / tier.A 110 / tier.B 3 / tier.C 1 / status.mined 91 / status.queued 15 /
  status.rejected 8 / missing 0`; `validate` exit 0 with **30** `W04 duplicate url` warnings and
  no `E` findings.
- **After** (`<TIP_REV>`): `rows <REG_AFTER> / tier.A <TIER_A_AFTER> / tier.B <TIER_B_AFTER> /
  tier.C <TIER_C_AFTER> / status.mined <MINED_AFTER> / status.queued <QUEUED_AFTER> /
  status.rejected <REJECTED_AFTER> / missing 0`; `validate` exit `<VALIDATE_RC>` with
  `<WARN_AFTER>` duplicate-URL warnings.

Rows added: **`<ROWS_ADDED>`**, by tier `<TIER_ADDED_MIX>` — S115 git-count-objects(1),
S116 git-fsck(1), S117 git-prune(1), plus `<COMMUNITY_ROWS>` from the community pages.
Rows touched old→new: **`<ROWS_TOUCHED>`** (no existing row's `scope`/`anchor`/`teaches`/`status`/
`recheck`/`used-by` cell may be rewritten; a correction is an append, not an edit).
Frontier rows advanced: **F2 repository size census** — `corpus/README.md` map row, the Frontier
note and the `### Round 23` section. **No promotion to core.**

Honest bound on the F2 claim, stated here so the report cannot drift: the r13 row already records
a *bounded structure-census capability* (`knowledge/git-repo-structure-readonly.md`,
S035/S036/S037) with "wider size attribution remains frontier". The round therefore claims
**entries on F2's read side**, not a new frontier row and not a promotion; `CritC3Ground` grades
whether the admitted delta over the held entries is real (`<C3_GROUND_FINDING>`).

**Assimilation (§10).** One theme, package `/home/vgpnk/Projects/shokuknow/merge/souji/`
(read-only; no write, no commit, no campaign tool run). Id collision step before any write:
registry `<REG_BEFORE_IDS>` ids, staged `<STAGED_IDS>` ids, `collisions <COLLISIONS>`; adopted ids
continue at `S115` and citations are re-pointed **by document** (`<REPOINT_MAP>`). Every cited
source re-opened by this lane on 2026-10-25 with a ≤25-word located quote in the lesson's
`## Gate`; staged `opened` dates and quotes prove nothing.

## Trend verdicts

- **expansion — `<EXPANSION_VERDICT>`.** Evidence: `<EXPANSION_EVIDENCE>` (entries
  `<KNOW_BEFORE>` → `<KNOW_AFTER>` files under `corpus/knowledge`; rows 114 → `<REG_AFTER>`;
  `<ROWS_ADDED>` new rows, all with committed snapshots). Not claimed: `<EXPANSION_NOT_CLAIMED>`.
- **quality — `<QUALITY_VERDICT>`.** Evidence: `<QUALITY_EVIDENCE>` (both new instruments are
  fixture-backed, reject their own always-green controls, and are read-only; C1 repaired the four
  routed record defects; the C2 receipts bind tool bytes at a named revision). Bounds:
  `<QUALITY_BOUNDS>`.
- **discernment — `<DISCERNMENT_VERDICT>`.** Evidence: `<DISCERNMENT_EVIDENCE>` (per-defect
  non-author review D1–D8, an ADMIT/REJECT pair with a flip per entry, a REJECT whose reason is
  entry-level rather than sweeping). Bounds: `<DISCERNMENT_BOUNDS>` — a lane-dispatched seat is
  still the lane, so no independent admission is asserted.

## SHONEN

One line per box; `[x]` only where `RevSHONEN` records a pointer that a non-author can resolve
at the named revision.

- `[<BOX1_STATE>]` **SKILL.md contains real decision tables, error patterns, checklists, cited
  sources** — `<BOX1_EVIDENCE>` (new capability row + two tool rows whose selftests are
  committed; `RevSHONEN` verdict `<BOX1_VERDICT>`).
- `[<BOX2_STATE>]` **At least one end-to-end domain task executed and logged in LOG.md** —
  `<BOX2_EVIDENCE>` (`<LOG_R23>`: both counters run before and after at named revisions;
  `RevSHONEN` verdict `<BOX2_VERDICT>`).
- `[<BOX3_STATE>]` **Instructions executable by an agent without oral context** —
  `<BOX3_EVIDENCE>` (every command cited in this report runs at `<TIP_REV>`; the vendored or
  not-re-run payloads are labelled as such; `RevSHONEN` verdict `<BOX3_VERDICT>`).
- `[<BOX4_STATE>]` **No cross-domain bleed (PROVINCE.md still accurate)** — `<BOX4_EVIDENCE>`
  (the round touches git object databases, man pages and two community pages; credential,
  exposure and host-liveness decisions stay with Kagi/operator and Mori; `RevSHONEN` verdict
  `<BOX4_VERDICT>`).

**Holds / no-harm scope:** certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged; no
deletion, move or quarantine outside `souji-shokunin/`; no history rewrite; no credentials; no
live `/proc` census; no operator-sweep contents read or staged; `/home/vgpnk/Projects/shokuknow`
read-only. `<NOHARM_RECEIPTS>`.

**Misroot sweep:** `<MISROOT_SUMMARY>` (pre-report, no pathspec; every untracked fleet-root entry
classified self / other-lane / orchestrator / operator; `.scratch/` untouched).

## Stale-lane

Respawn-per-round; no other mission of this lane is open; **round 24 not started**. Lane has **no
`.gitignore`** while operator-owned `census/operator-sweep-20261019/` sits untracked — one
`git add -A` from lane history; reported, not acted on. `<STALE_LANE_EXTRA>`.

## Tool installs

`<TOOL_INSTALLS>` — tool, version, channel, reason, per the operator directive. No pacman
transaction was run (host-wide pause respected); no host service restarted.

## Routed-defect dispositions (D1–D8)

Each row: the spot-check's claim, this round's disposition, where it is closed, and the seat that
reviewed it. `<D_TABLE_NOTE>`

| # | Claim (r22 spot-check §6) | Disposition | Closed by | Reviewer verdict |
|---|---|---|---|---|
| D1 | 5 modified r22 seat reports + 2 untracked `impl-a/head-c9f1fe3.*` files uncommitted while the report claims none | `<D1_DISPOSITION>` | `<D1_CLOSURE>` | `RevD1`: `<D1_VERDICT>` |
| D2 | no committed receipt binds the C1 after-state at the revision SCORECARD names (`9301d98`); report names `77d6595` | `<D2_DISPOSITION>` | `<D2_CLOSURE>` (K1) | `RevD2`: `<D2_VERDICT>` |
| D3 | r22 after-run measured with tool blob `f26aa728` while the report cited `5b8025a8…`; no *before* (`fail=10`) receipt | `<D3_DISPOSITION>` | `<D3_CLOSURE>` (C2 receipts + refusal demo) | `RevD3`: `<D3_VERDICT>` |
| D4 | README says `1 present … 1 refused` where `slice-verdicts.tsv` holds 2 present / 0 refused | `<D4_DISPOSITION>` | `<D4_CLOSURE>` (K3) | `RevD4`: `<D4_VERDICT>` |
| D5 | LOG *Round22 attempt2* keeps `assertions=56 resolved=53` and slice `1 present, 1 refused`, no append-only correction | `<D5_DISPOSITION>` | `<D5_CLOSURE>` (K2) | `RevD5`: `<D5_VERDICT>` |
| D6 | lesson Gate's reject reason for `quarantine-staging-no-copy-r24` is overbroad | `<D6_DISPOSITION>` | `<D6_CLOSURE>` | `RevD6`: `<D6_VERDICT>` |
| D7 | M17/M22 record `captured-by: none` and no `QUALITY.md` criterion was written | `<D7_DISPOSITION>` | `<D7_CLOSURE>` (Q54) | `RevD7`: `<D7_VERDICT>` |
| D8 | derived slice row for `S118` carries a stray backtick | `<D8_DISPOSITION>` | `<D8_CLOSURE>` | `RevD8`: `<D8_VERDICT>` |

---

## Placeholder index (delete before landing)

Each token, the artifact that must supply it, and the command or file that proves the value.
"Seat" = the seat report named; "L1" = the L1 must produce it from the landed tree.

### Revisions and hashes

| Token | Fill from | Proof |
|---|---|---|
| `<BASE_REV>` | already `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` | `git rev-parse HEAD` at round start |
| `<TIP_REV>` | final lane tip | `jj-lane.sh state` → `local=` |
| `<COMMIT_C1_TOOL>`, `<COMMIT_C1_RECEIPTS>`, `<COMMIT_C2_TOOL>`, `<COMMIT_C2_RECEIPTS>`, `<COMMIT_C3_ENTRY1>`, `<COMMIT_C3_ENTRY2>`, `<COMMIT_C3_ROWS>`, `<COMMIT_RECORDS>`, `<COMMIT_QUALITY_LESSON>`, `<COMMIT_D1>`, `<COMMIT_WAVE>`, `<COMMIT_FINAL>` | helper `landed <hash>` lines | `git log --format='%H %s'` for each; every hash must be an ancestor of `<TIP_REV>` |
| `<R22_SCORECARD_REV>` (context only) | `9301d98c1c689c79741f0f1ba1f171138d20af07` | `SCORECARD.md:14` at base |
| `<TOOL_SHA256_AT_TIP>` | `sha256sum tools/souji-record-agreement.py` at `<TIP_REV>` | the receipt's `tool_sha256=` line |

### C1 numbers

| Token | Fill from | Proof |
|---|---|---|
| `<R_BEFORE>`, `<O_BEFORE>`, `<M_BEFORE>` | base run of the C1 command | `census/round-23/records/agreement-control-base.tsv`; `M_BEFORE` must be ≥1 or the counter is wrong and must be repaired before any after-data |
| `<R_AFTER>`, `<O_AFTER>`, `<M_AFTER>` | tip run | `census/round-23/records/declared-evidence-after.tsv`; target `0` |
| `<C1_AFTER_RC>`, `<C1_VERDICT>`, `<C1_COUNTER_VERDICT>`, `<C1_AXIS_MOVE>`, `<CAL_SCORE>` | tip run + critic verdicts | exit code of the same command; `CritC1Gameable.md`; axis row in `SCORECARD.md` |
| `<CONTROL_VERDICT>`, `<FIXTURE_CONTROL_LINE>`, `<C1_ATTACKS>` | fixture run | `tests/fixtures/r23-record-agreement.py` output; `CritC1Gameable.md` |

### C2 numbers

| Token | Fill from | Proof |
|---|---|---|
| `<RECEIPTS_AFTER>` | `grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/ \| wc -l` at `<TIP_REV>` | must be ≥4 |
| `<C2_VERDICT>`, `<C2_COUNTER_VERDICT>`, `<C2_CREDIT>`, `<OPS_SCORE>` | verify runs + `CritC2Value.md` | four `verify` exit codes; critic report |
| `<REFUSAL_RC>`, `<REFUSAL_RECEIPT>`, `<C2_KILL_CHECK>`, `<C2_DUP_FINDING>` | refusal demonstration | stale `5b8025a8…` receipt + `RECEIPT-TOOL-DIGEST-MISMATCH`; `CritC2Value.md` |

### C3 numbers

| Token | Fill from | Proof |
|---|---|---|
| `<C3_ENTRY2_PATH>`, `<C3_ENTRY2_BASENAME>` | **preregistration** name `corpus/knowledge/count-objects-garbage-semantics-r24.md` — or the name the L1 actually lands, with the divergence stated | `ScribeEntryGarbage.md` vs `preregistration.txt` C3 block |
| `<GATE_FAIL_BEFORE>` | base run of gate-check on absent entries | exit 1 at `1208bfb` |
| `<REG_AFTER>`, `<TIER_A_AFTER>`, `<TIER_B_AFTER>`, `<TIER_C_AFTER>`, `<MINED_AFTER>`, `<QUEUED_AFTER>`, `<REJECTED_AFTER>`, `<VALIDATE_RC>`, `<WARN_AFTER>` | `sources-census.sh census` + `validate` at `<TIP_REV>` | TSV `souji\trows\t…` and `souji\tok\t…` lines |
| `<REG_MAX_AFTER>`, `<ROWS_ADDED>`, `<TIER_ADDED_MIX>`, `<COMMUNITY_ROWS>`, `<ROWS_TOUCHED>`, `<REPOINT_MAP>`, `<REG_BEFORE_IDS>`, `<STAGED_IDS>`, `<COLLISIONS>` | census diff base→tip; `ScoutIdCollision.md`; `ConnectorSiblingSources.md` | `git diff <BASE_REV> <TIP_REV> -- corpus/SOURCES.md` |
| `<KNOW_BEFORE>`, `<KNOW_AFTER>` | `git ls-tree -r --name-only <rev> corpus/knowledge \| wc -l` | base measured **11** this run |
| `<C3_VERDICT>`, `<C3_COUNTER_VERDICT>`, `<C3_CREDIT>`, `<COV_SCORE>`, `<C3_GROUND_FINDING>`, `<C3_CONTROL_RECEIPT>`, `<C3_CONTROL_VERDICT>` | gate-check + census + `CritC3Ground.md` | exit codes; critic report |

### Records, wave and trends

| Token | Fill from | Proof |
|---|---|---|
| `<LOG_R23>`, `<LOG_CORR>` | `LOG.md` headings as landed | `grep -n '^## ' LOG.md \| tail` |
| `<Q55_ID>` | next free id after Q53 (Q54 is reserved for the D7 criterion) | `grep -oE 'Q[0-9]+' corpus/QUALITY.md \| sort -V \| tail -1` |
| `<SEATS_TOTAL>`, `<DEAD_SEATS>`, `<RESIDUAL_SEATS>`, `<TRACKED_COUNT>` | wave registry + `jj-lane.sh state` | `.ufo/waves/round-23/w1/swarm-registry.json`; seat report count |
| `<EXPANSION_VERDICT>`, `<QUALITY_VERDICT>`, `<DISCERNMENT_VERDICT>` + `*_EVIDENCE`, `*_NOT_CLAIMED`, `*_BOUNDS` | critic + reviewer reports | `CritC1Gameable.md`, `CritC2Value.md`, `CritC3Ground.md`, `RevD*.md` |
| `<BOX1_STATE>`…`<BOX4_STATE>`, `<BOX1_EVIDENCE>`…`<BOX4_EVIDENCE>`, `<BOX1_VERDICT>`…`<BOX4_VERDICT>` | `RevSHONEN.md` | `SHONEN.md`; `[x]` only with a named non-author verifier |
| `<NOHARM_LINE>`, `<NOHARM_RECEIPTS>`, `<MISROOT_SUMMARY>`, `<STALE_LANE_EXTRA>`, `<TOOL_INSTALLS>`, `<D_TABLE_NOTE>` | sentinel + misroot scout + L1 | `SentinelScope.md`, `ScoutMisroot.md` |
| `<D1_DISPOSITION>`…`<D8_DISPOSITION>`, `<D1_CLOSURE>`…`<D8_CLOSURE>`, `<D1_VERDICT>`…`<D8_VERDICT>` | `RevD1.md`…`RevD8.md` + the landed repair | each defect's one reproducing command and its closure command |
