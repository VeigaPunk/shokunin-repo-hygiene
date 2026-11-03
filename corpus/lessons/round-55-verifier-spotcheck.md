author: hyaku closure (non-author integrator, @m_zfl)
round: souji 55 (attempt 1)
base: f056aaa031bb65de27e7fa5daa38b0d4a443aedc
tip: 6d8bfb8ebb00f4806e7f83a0173aa4768358de33 (= origin/master, verified by `git ls-remote`)
report: .ufo/reports/round-55/souji.md (fleet commits e1444324 report + L0, fb86d576 ERR-R55-A erratum)
dispatch digest: 2026-11-03T18:17:27-03:00 launch souji round=55 pgid=2790575 driver=hyaku-inline attempt=1 / 2026-11-03T19:11:55-03:00 complete souji round=55; hyaku-inline attempt=1 (watchdog.log lines 2098/2108)

## Verdict

status **ok** (real report: checkable work, evidence pointers, all contract sections; no marker).
**Not admitted** — verdict **rejected-harmed**: both declared claims re-verify on their frozen
predicates, but each carries a v3→v4 regression the lane itself recorded as a harm (C1 S55-S2,
C2 RD-A); the no-harm admission rule fails and the lane admits neither claim (lane default: no
admission until the operator rules, L0 filed). All numeric axis scores are unchanged (7/8/8).

## Step-1 conformance

- Report committed by the lane identity: `git log --format='%an %H' -- .ufo/reports/round-55/souji.md`
  → two commits, both `souji-shokunin <souji@shokunin.local>`: `e1444324` (report + one L0 line) and
  `fb86d576` (ERR-R55-A attribution erratum, appended after the filed bytes — append-only discipline held).
- `## SHONEN` heading present (report line 95) with exactly 4 `[~]` box lines — byte-consistent with
  the 4-box SHONEN.md seed; every box carries a resolvable pointer.
- Cited lane commits: all 10 (base `f056aaa0`, freeze `e8f33867`, `9a1eaaa2`, `4b10ddd1`, `3ce0ba03`,
  `913fa479`, `b6c6a93a`, `f9da665e`, `51551399`, tip `6d8bfb8e`) exist and
  `git merge-base --is-ancestor <h> refs/heads/master` holds for each (branch ref, never `@{u}`).
- Lane clean and pushed: `jj-lane.sh state` → `branch=master local=6d8bfb8e remote=6d8bfb8e ahead=0
  behind=0 tracked=0 untracked=0`; `git status --porcelain` empty.
- Prompt fidelity: `.ufo/prompts/souji-round-55.md` sections 1–5 match `templates/round-prompt.md`
  headers and carry the full round contract — mission/axes binding, 1–3 falsifiable claims on distinct
  axes with lowest-axis rule, L2 ≥8 in ONE batched call, commit-then-push ordering, push scope, L0
  side channel — plus the five child-lane items (report path/filename, commit-before-report, SHONEN
  heading requirement, commit-hash citation rule, write scope) and hyaku addendum §6.
- Frozen-byte discipline: `git log e8f33867..6d8bfb8e -- census/round-55/c{1,2}-counter.py
  census/round-55/fixtures/ census/round-55/preregistration.txt` → no commits; the frozen bytes did
  not change after the freeze (fixes correctly deferred to a future counter generation).
- Fleet census at closure: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
  → rc 0, 202 rows, 61 pre-existing W04 duplicate-url warnings (none naming S278).

## Per-claim re-check

Re-measured by this closure with plain commands over committed bytes; the lane's gates/selftests
were **evidence-verified only, never executed** (PROTOCOL §Gate standard, Closure consequence).

**C1 — calibration 7 (re-measured).** Exit-0 counts over the official 27-row matrices:
`awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-55/records/c1-matrix-v{3,4}.tsv`
→ **11 → 6** (reported 11 → 6: MATCH). Row-level (both TSVs): v3 exit 0 and v4 exit 1 with named
findings on all 8 acceptance attacks — F7-FF `CORRECTION-IN-FENCE`, F13 `ANCHOR-ALIAS-MISMATCH`,
F14 `PAIR-FILING-INERT`, F15/F16/F22 `UNFILED-SOURCES-ANNOTATION`, F20/F21 `BOGUS-RECOMPUTED`;
v3 exit 1 → v4 exit 0 on the three honest over-hide states F17/F18/F19; the 13 r54 carry-over rows
F1–F12b keep identical exit+finding under v4 (the byte diff v3→v4 is the counter label and new
`alias=`/`pairinert=` fields; verdict changes are exactly the 11 rows above). Evidence-verified:
`records/c1-selftest.txt` → `SELFTEST pass cases=27` (27/27, exit 0 asserted in prereg);
`records/c1-tip.txt` → `unfiled=0 … alias=0 pairinert=0` at rev `4b10ddd1741a` (measured revision
pinned inside the file); preregistration pins (record-sha256 `2b90a262…`, sources-rev-before
`f778b9d1…`, sources-rev-after `9bf9234a…`) match the cited commands. **Predicate holds; S55-S2
regression recorded as a harm (receipt `records/probe-s2-pair-indent-comment.txt`: frozen v3 exit 1
`UNFILED-SOURCES-ANNOTATION`, v4 exit 0 on the same overstatement).**

**C2 — coverage 8 (re-measured).** `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}'
census/round-55/records/c2-matrix-v{3,4}.tsv` → **5 → 2** (reported 5 → 2: MATCH). Row-level: FB1-
TAB4-ROW / FB2-LOWER-KEY / FB3-NOSPACE-KEY v3 exit 0 → v4 exit 1 with `COMMENT-AMBIGUOUS-NAME` /
`RECEIPT-UNKNOWN-KEY` ×2; FA8-SYMLINK-CLASS keeps exit 1 with the finding now named `CLASS-MISMATCH`
(Q110); FH, FH2, FA1–FA7 identical. Evidence-verified: `records/c2-selftest.txt` → `SELFTEST pass
cases=15` (15/15, including FA9-WRONG-TOOL-PIN rc 1 `TOOL-SHA-ARG-MISMATCH` and FB4-PIN-SHAPE rc 2);
`records/c2-tip.txt` → `receipt=ok sorted=ok tool_pin=ok` at rev `4b10ddd1741a`; wrong-pin leg rc 1
`TOOL-SHA-ARG-MISMATCH` committed in the selftest expected TSV; capture receipt `ENTRIES=49` with
`FLEET_HEAD=e5396bee…` (a real fleet commit, 2026-11-03 18:28) and `TOOL_SHA256=e7e79952…` matching
the prereg instrument pin. **Predicate holds; RD-A regression recorded as a harm (receipt
`wave/w1/S55reviewer02/receipt-key-differential.txt`: v3 refuses `1KEY=x`, `_KEY=x`, `2=x`; v4 passes).**

**Exploratory claims:** none declared — no `unprovable-but-better` ruling owed.

**No owned axis harmed structurally:** `git diff f056aaa0 6d8bfb8e -- SCORECARD.md` is purely
additive (one hunk, +57/−0: Round-55 measurements, r56 plan, harms table, corrections); calibration 7
/ coverage 8 / operability 8 unchanged; capability table untouched. The harm is inside the
instruments' verdict power (the two regressions), not in the scorecard bookkeeping.

## Per-axis verdicts

| axis | verdict | reason |
|---|---|---|
| calibration | harmed | Instrument gained real kill-power (8/8 acceptance attacks now refused, 3 honest over-hide states repaired, 11→6 exit-0) but S55-S2 lets v4 pass a real overstatement v3 refused — recorded as a harm by the lane and confirmed by the committed probe receipt. |
| coverage | harmed | FB1–FB3 receipt/comment surfaces newly killed with named findings (5→2) but RD-A narrows the receipt-key first-character class so v4 silently passes `1KEY=x`/`_KEY=x`/`2=x` that v3 refused — recorded as a harm by the lane and confirmed by the committed differential. |
| operability | unchanged | Numeric score 8 unchanged; landing suite re-run at the tip reports `unfiled=0` (rc asserted in prose, see routed defect 2); SCORECARD delta additive only. |

## Discernment spot-check (LEARNING.md — non-author)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S278 (Python 3.12 docs, `str.splitlines`) | admit | live fetch `https://docs.python.org/3.12/library/stdtypes.html` + committed capture | **agree** | All four located quotes verbatim on the live 3.12.16 page (18/15/25/13 words, all ≤25); `sha256sum census/round-55/sources/s278-python-stdtypes.html` = `0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352`, 648,964 bytes — byte-exact as claimed; tier A docs; teaches grounded (splitlines superset vs LF-only numbering); cited by the admitted entry. |
| reject sample | none exists | S277 reuse declaration (CommonMark 0.31.2) as the nearest negative decision | **agree** (with the honest no-reject record) | The Gate opened exactly one new page, so no candidate was rejected; the S277 reuse re-opened live: "Version 0.31.2 (2024-01-28)" heading and the 17-word §4.5 fence quote verbatim — leaving S277 untouched (no status/recheck/used-by change) was right. |
| Q62 fix (S277 id removed from the new entry's `source:` line) | correction applied in-round | both current bytes re-read | **agree** | S277 `used-by` names only `correction-filing-fence-grammar.md`; `splitlines-line-model.md` `source:` cites S278 only; the remaining S277 mention in the entry is prose, not a citation — no inconsistent cross-citation remains in either direction. |

Knowledge-entry provenance trio verified first-lines (`source: S278 …`, `verified-at: 2026-11-03 …`,
`recheck:` resolvable full command + fresh-fetch quote check). Search-log entry present with
question, 1/1/1/0 counts and stop rationale.

## Trend verdicts

- **expansion: unchanged** — registry 201 → 202 (+1, S278, tier A), one knowledge entry admitted,
  but it sits on Core ground the lane already holds (correction-filing line model); no frontier row
  advanced; corroborated by the SOURCES row count and the coverage-map claim in the report.
- **quality: harmed** — real kill-power gained on both instruments while two v3→v4 regressions
  (S55-S2, RD-A) are recorded as harms; the lane reports the trade and admits neither claim; both
  regressions are mined into `## Mistakes`. This closure confirms both measurements independently.
- **discernment: unchanged** — this non-author spot-check agrees with the round's only new admit and
  has no reject to test (none existed); the in-round attack seats are lane-dispatched and do not
  count as outside discernment; no disagreement arose to become a lesson.

## Routed defects — the lane must fix next round (r56)

1. **LOG.md hash tie-in gap.** The report's Landed-changes table ties all 9 commits to `LOG.md
   ## Round 55`, but LOG.md at the tip names only 6 hashes (`e8f33867` ×2, `9a1eaaa2`, `4b10ddd1`,
   `3ce0ba03`, `913fa479`, `b6c6a93a`); `f9da665e`, `51551399` and `6d8bfb8e` appear nowhere in
   LOG.md (grep count 0 each). Fix: append a LOG correction entry naming the three hashes.
2. **Tip receipts carry no exit-code line.** `records/c1-tip.txt` / `records/c2-tip.txt` (and the
   wave copies) show green SUMMARY fields but no `rc 0`; exit-0 is asserted in SCORECARD/LOG prose.
   Disclosed by ERRATUM-R55-5 and already in the r56 plan — keep routed until receipts carry rc.
3. **S55-S2 (C1 v4 regression, carried).** A four-space-indented `<!--` opener hides a real
   overstatement from the pair scan (v3 exit 1, v4 exit 0; introduced by R6). Fix in the next counter
   generation with its own prereg and a red-before fixture; frozen bytes stay untouched.
4. **RD-A (C2 v4 regression, carried).** Receipt keys beginning with a digit or underscore pass
   silently (first-character class narrowed without a differential). Same fix path as 3.
5. **Pointer nit.** The report cites the wave dispatch at `.ufo/waves/round-55/w1-dispatch.json`;
   the committed tree holds it at `census/round-55/wave/w1-dispatch.json` (the lesson documents the
   copy). Future reports cite the committed path.

## Operator items (not routed to the lane)

- **SHONEN:** all four boxes are `[~]` asserted-by-author and each looks checkable by a non-author
  (SKILL.md Round-55 gate-registry contracts; LOG.md end-to-end legs; `preregistration.txt` recompute
  commands; PROVINCE.md unchanged, sibling defects routed not edited). Promotion is operator-owned.
  Note: souji holds SHONEN.md but has no row in MANIFEST.json's 13-entry roster — for the operator
  to reconcile.
- **L0 open:** round-55 admission ruling (C2 RD-A, C1 S55-S2; options: admit with harms recorded, or
  re-run as r56 with fixes first; lane default: no admission until ruled). Carried, not assumed.
- **ERR-R55-A** (lane-appended erratum): kake's r72 L0 line rode souji's report commit e1444324 in
  the shared `.ufo/l0-questions.md`; recorded by the lane, history untouched. Attribution noted here.
- Route observation (status-neutral): the live `task.agentModelOverrides` today shows
  connector/sentinel/scribe/sonic/distiller/seance on `@m_flash`, not the prompt's run-15 `@m_mim`
  map; MISSION.md's role-class bucket table is advisory and the config file is the operator-owned
  authority the prompt itself names. Recorded for the operator; no lane action.
