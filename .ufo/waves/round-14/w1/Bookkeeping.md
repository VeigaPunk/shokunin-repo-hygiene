# Round 14 — Bookkeeping proposal (SoujiR14.Bookkeeping, w1)

Scope: proposal only. No shared bookkeeping written: SCORECARD.md, SHONEN.md, PROVINCE.md,
LOG.md, corpus/, census/ and tools/ are untouched by this seat. L1 integrates.

Evidence class: everything below is **code/document inspection** of the three named files plus
`corpus/lessons/round-13.md`, `AGENTS.md`, `tools/` and `tests/fixtures/` directory listings.
**Nothing here is exercised evidence.** No build, test, linter, smoke run or fixture was executed.
Opened only: `~/.omp/agent/RULES.md` (permitted), the lane's SCORECARD/SHONEN/PROVINCE/AGENTS,
and round-13 lesson grep. Not opened: anything under `census/operator-sweep-*`, nothing under
`~/.omp/agent/` beyond RULES.md.

Tool installs/updates by this seat: none. No tool was needed for read-only inspection.

## 1. Axis state (named axes: calibration, operability, coverage)

| axis | r13 score | r14 proposed delta | r14 proposed score | judged this round |
|---|---|---|---|---|
| calibration | 7 | 0 | 7 | yes |
| operability | 8 | 0 | 8 | yes |
| coverage | 8 | 0 | 8 | no (not judged; unchanged) |

Basis for delta 0 (inspection only):
- SCORECARD states the numeric delta for r13 was 0 on every axis pending outside closure; r13
  lesson (`corpus/lessons/round-13.md` ~L8-9) states "Scores stay 7/8/8 ... an integrity-test count
  is not a calibrated 0–10 score."
- r14 C1 (evidence-cache) and C2 (census boundary) are new fixtures whose tools and fixtures do
  **not yet exist** in the tree at the time of this inspection (see F1). A score cannot move on
  unexercised, unlanded code.
- Certification remains OFF; the r14 cache explicitly makes no proof of historical execution.
- Movement from 7/8 requires an L1 exercised run on a measured commit plus outside closure review
  (`corpus/lessons/round-13.md` ~L36: the orchestrator's closure supplies the outside admit/reject
  sample). Neither has happened.

Stagnation note (to-verify): SCORECARD saturation line sets a 3-round stagnation window. If r12
also recorded zero numeric delta on operability/calibration, r14 zero delta completes a 3-round
stagnation. I could not confirm r12 numeric deltas from the three files; L1 must check
`LOG.md` / `corpus/lessons/round-12.md` before writing the saturation prose.

## 2. Exact r14 score rows (proposed; delta 0)

Coverage row: **leave byte-identical** to the current row (r13 measured commits `31984f4 → 6f8ee0f`,
`last change r13`). Coverage was not re-measured in r14 and no admitted frontier entry is proposed.
Reason: S038 is a correction of S034 (a source-row correction under `corpus/SOURCES.md`), not a new
admitted ground entry; PROVINCE frontier promotion requires an admitted `corpus/knowledge/` entry
plus a SKILL rule, neither of which is in this round's listed write sets.

Calibration row — replace only after L1 exercises the cache fixtures on a measured commit:

    | calibration | 7 | unchanged numeric (r14 C1, self-verdict pending outside closure; delta 0): digest-bound evidence-cache eligibility; legacy/no-dependency, false `matched`, digest mismatch, missing/nonregular/symlink/escaping dependencies fail closed with named finding ids (exit 1 stale/failed, exit 2 malformed); per-result measured revision explicit; no proof of historical execution; labels/coverage/execution unproved; certification OFF | `python3 tools/souji-evidence-cache.py --selftest`; `<r14 evidence-cache fixture command, from C1 report>` | <L1 commit after C1 lands> | r14 |

Operability row — replace only after L1 exercises the census boundary fixture:

    | operability | 8 | unchanged numeric (r14 C2, self-verdict pending outside closure; delta 0): `tools/souji-census.sh` refuses a root or compare path that overlaps the credential-store boundary (lexical and canonical, including ancestor roots and aliases) before any git/find/du/content access; repo-root and `.scratch` symlinks are not followed into the credential store; fixtures use synthetic HOME under /var/tmp with command spies; no credentials, no operator-sweep access | `<r14 census-boundary fixture command, from C2 report>`; prior r13 commands retained (see §5) | <L1 commit after C2 lands> | r14 |

Capabilities table: add two rows only after exercise (do not add now):
- `evidence-cache eligibility` | digest-bound reuse decision for retained green records; fail-closed on legacy/stale/digest-mismatch; no historical-execution claim | `tools/souji-evidence-cache.py --selftest`, `tests/fixtures/r14-evidence-cache.py` | r14
- `census credential-boundary refusal` | census refuses credential-store roots and aliases before enumeration | `tests/fixtures/r14-census-boundary.py` | r14

The counting-command rule (`SCORECARD.md` L5-7) requires each non-`—` observation to carry its
counting command and measured commit. Do not write the r14 rows with placeholder commits; if the
commit is not yet known at integration, the row must say `to-verify` rather than invent a hash.

## 3. Planned wording

### 3a. SCORECARD `## Planned` — replace the stale r14 bullet

Current text (`SCORECARD.md` L54-60) is headed `r14 (planned r13)`. Proposed status line:

    - **r14 (planned in r13; executed r14):** comprehensive class-suite re-certification under
      Q6/Q18 was NOT run and remains separate from declared-fragment integrity and from the built-in
      smoke suites; certification stays OFF. Delivered as fixtures only: digest-bound evidence-cache
      eligibility (calibration) and census credential-store boundary refusal (operability); scores
      held at 7/8/8 pending outside closure. Kotodama `.scratch` age/receipt census remains a
      read-only, metadata-bounded frontier with no content inspection or removal. F2 wider size
      attribution, unreachable-object accounting and linked common-store aggregation remain frontier.
      Cross-device quarantine/K5 remains HELD under Q4/Q16.

Add (exact, new bullet):

    - **r15 (planned r14):** promote the r14 evidence-cache rule from fixture to counted calibration
      claim only if (a) `tools/souji-evidence-cache.py --selftest` and the r14 fixture pass on a
      measured commit, and (b) an outside closure reviewer samples its admit/reject. Historical
      replays of cache records remain evidence of digest consistency, not of actual historical
      execution. Comprehensive class-suite re-certification stays a separate, unclaimed track;
      certification stays OFF. F2 frontier and HELD K5 unchanged.

### 3b. SCORECARD `## Saturation / stagnation`

Keep the sentence "Saturation line: 8 per axis; stagnation window 3 rounds." Replace the score
clause with: `Scores per the rows above: coverage 8, operability 8, calibration 7; r14 numeric delta 0
on all axes (pending outside closure).` Do not state that any axis is saturated; calibration is 1
point below the line.

### 3c. PROVINCE.md — add a boundary sentence (new section, after `## Round 13 boundary refinement`)

    ## Round 14 boundary refinement

    `tools/souji-census.sh` refuses any root or compare path that overlaps the credential-store
    boundary (lexical or canonical, including ancestor roots and aliases) before enumeration. This
    enforces the `## Refuses` credentials row in code; it grants souji no credential read, and
    kagi-shokunin's province is unchanged.

Do not add frontier/core moves in PROVINCE. F1–F4 statuses are unchanged.

## 4. The four SHONEN assertions (proposed r14 marks)

All four stay `[~]`. Reason: `corpus/lessons/round-13.md` (~L36) states the lane "does not mark
SHONEN `[x]`" — the fresh outside admit/reject sample is reserved for the orchestrator's closure.
No r14 evidence in this seat justifies `[x]`.

1. **SKILL.md contains real decision tables, error patterns, checklists, cited sources** — `[~]`
   (unchanged). The evidence-cache exit-code contract (0 reusable / 1 stale-failed / 2
   malformed) is a tool contract, not yet a SKILL decision table. Do not add it to SKILL.md until
   a corpus entry is admitted (PROVINCE promotion rule). Pointer in the mark: `SKILL.md Decision
   tables, Error patterns, Checklists and Gate registry; corpus/SOURCES.md; corpus/lessons/round-13.md`
   plus `corpus/lessons/round-14.md` once L1 writes it.

2. **At least one end-to-end domain task executed and logged in LOG.md** — `[~]` (unchanged).
   Pointer `LOG.md:362` (operator sweep) remains the only cited domain run; I did not open it.
   Fixture runs in r14 are not a domain task and must not be logged as one.

3. **Instructions executable by an agent without oral context** — `[~]` (unchanged). r14 adds two
   self-invoking entry points (`--selftest` on the cache tool; the census boundary fixture). The
   mark upgrades only if L1 exercises the commands in §5 and records their exit codes.

4. **No cross-domain bleed (PROVINCE.md still accurate)** — `[~]` (unchanged). The C2 credential
   refusal is the PROVINCE `## Refuses` credentials row implemented in code. PROVINCE needs the §3c
   sentence to remain accurate; without it, the new refusal is an undocumented boundary. Pointer:
   `PROVINCE.md ## Refuses; ## Round 14 boundary refinement (proposed §3c)`.

## 5. Final L1 commands (identified; NOT run by this seat)

Run after C1 and C2 land and before writing scorecard rows. Order: fixtures first, then regression.

1. `python3 tools/souji-evidence-cache.py --selftest` — expect exit 0, named finding ids per C1
   report. (Tool path confirmed in shared interfaces; file **not yet present** — see F1.)
2. `python3 tests/fixtures/r14-evidence-cache.py` — C1 fixture; exact invocation to-verify from C1
   report (file not yet present).
3. `python3 tests/fixtures/r14-census-boundary.py` — C2 fixture; exact invocation to-verify from
   C2 report (file not yet present). Must use synthetic HOME under /var/tmp; L1 confirms no real
   credential-store path is read (command-spy output).
4. `shellcheck tools/souji-census.sh` — warning-level, expect exit 0 (r13 precedent in the
   operability row; exact flags to-verify).
5. Regression (unchanged from r13 rows; expected values from SCORECARD):
   - `python3 tools/souji-cert-evidence.py --selftest` → 36/36
   - `python3 tools/souji-cert-evidence.py` external fixture `tests/fixtures/r13-cert-evidence.py` → 5/5
   - `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` → 5/5
   - `bash tests/fixtures/r13-quarantine-bounds.sh` → 5/5
   - `bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6
   - `python3 census/round-13/run-verification.py --retry-failed` (r13 verification re-run, if L1 wants the
     census/verification.json to stay consistent)
6. Commit the r14 tools/fixtures (L1 commit) and record that commit as the `measured commit` for the
   calibration and operability rows. Coverage row keeps `31984f4 → 6f8ee0f`.

Do not run `census/round-14/count-claims.py` for coverage: that file is not present, and coverage is
unchanged.

## 6. Findings

- **F1 (blocking for scorecard rows):** At inspection time `tools/` contains no
  `souji-evidence-cache.py`, and `tests/fixtures/` contains no `r14-evidence-cache.py` or
  `r14-census-boundary.py`. The round-14 directory holds only `w1-dispatch.json`, `w1-spec.json`,
  and under `census/round-14/`: `claims.json`, `before.json`. The rows in §2 must not be written
  until L1 confirms these files landed. Until then, all r14 claims are proposals.
- **F2 (stale text):** SCORECARD `## Planned` labels the r14 bullet `(planned r13)`; it must be
  updated to a status line (§3a) so the planned list does not read as open work after r14 closes.
- **F3 (stagnation, to-verify):** see §1. The 3-round window may be complete at r14 if r12 was
  also zero-delta; L1 must confirm before writing saturation prose.
- **F4 (operability hygiene, report only):** `tools/` holds a large number of `cand-*.sh`,
  `impl-NN.sh`, `souji-census.impl-NN.sh`, `souji-quarantine.impl-NN.sh`, `souji-round9-selftest.sh`,
  and `souji-*.r9-s18.sh` copies alongside the canonical tools; `tests/fixtures/` holds `case-F1..F10/`
  directories. Which copies are canonical is not stated in the three files I read. A reader without
  oral context could execute the wrong census/quarantine script. This is a real operability question
  for L1/operator; I did not inspect git tracking status (to-verify) and propose no removal in this
  seat. Removal would require a receipt under AGENTS.md and is out of this seat's write set.
- **F5 (calibration precision):** The proposed calibration row must not say "proved" anywhere;
  SCORECARD's existing calibration row already states "labels/coverage/execution remain unproved".
  The r14 wording in §2 keeps that clause verbatim in spirit; any L1 edit must not drop it.
- **F6 (source citation):** The contract asks for S038 (correction of S034) only if the vendor
  timeout docs are opened this round by the SourceTimeout seat. This seat did not open them; no
  S038 or S039 citation is made here. S039 is reserved for L1-run evidence and is not usable in this
  proposal.

## 7. Out of scope / not done

- No writes to SCORECARD.md, SHONEN.md, PROVINCE.md, LOG.md, corpus, census or tools.
- No commit. No build, test, linter, formatter or smoke run.
- No access to `census/operator-sweep-20261019/`, `census/operator-sweep-20261018/`, or anything
  under `~/.omp/agent/` except RULES.md.
- No tool installs or upgrades by this seat (none required). Recorded per RULES.md: none.
