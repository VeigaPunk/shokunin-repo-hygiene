# Round 74 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatch digest (copied from `.ufo/watchdog.log` because the log is mutable):
`2026-11-06T20:31:52-03:00 launch souji round=74 pgid=3362356 driver=hyaku-inline attempt=1`;
`2026-11-06T21:15:33-03:00 complete souji round=74; hyaku-inline attempt=1`.
Lane base `43cd74bba84bb498b57a74377ccb0567d10864d5`, lane tip `0e1765a046cdb879df5e6ff242864311226491c0`.
The closure authored no round byte and ran no lane gate, counter or selftest (PROTOCOL §Gate standard,
Closure consequence). Every gate/counter/selftest number below is evidence-verified from committed receipts
read with `git show 0e1765a0:<path> | grep`. The source, SOURCES row and census numbers were re-measured by
the closure itself.

## Conformance

| check | command | observed | result |
|---|---|---|---|
| report committed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-74/souji.md` | `souji-shokunin <souji@shokunin.local> 0e5f1e82548ebfdff560dd6f5d7328d5d853ee2a 2026-11-06 21:13:50 -0300`. Filed before `complete` (21:15:33) and after the lane tip (21:12:59). | pass |
| `SHONEN` heading, one line per box | read report lines 108-113 | `## SHONEN` with 4 lines, all `[~]`, each with an evidence pointer | pass |
| cited lane commits exist and are ancestors of `master` | `git cat-file -e <h>^{commit} && git merge-base --is-ancestor <h> master` for bcdf2d16 ac573032 ec13ba7f 8fe48c86 a50e0ce2 b5e6d514 0e1765a0 (full hashes) | all 7 `ok`, all authored by `souji-shokunin` | pass |
| lane pushed, nothing left over | `scripts/hyaku/jj-lane.sh state …/souji-shokunin`; `git status --porcelain` | `state branch=master local=0e1765a0… remote=0e1765a0… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; `ls-remote origin refs/heads/master` = `0e1765a0…` | pass |
| prompt carries the template contract | `diff <(head -140 .ufo/prompts/souji-round-74.md) kimi-shokunin/templates/round-prompt.md` | only `{{LANE}}`/`{{ROUND}}`/`{{FLEET_ROOT}}`/`{{AXES}}` substitutions differ; §1-§5 are verbatim, followed by hyaku addendum §6/§7 | pass |
| frozen inputs untouched after freeze | `git diff --stat bcdf2d16 0e1765a0 -- census/round-74/preregistration.txt census/round-74/controls census/round-74/c1-gate-counter.py census/round-74/c2-defang.json census/round-74/c2-survivors.json census/round-73/c1-matrix.tsv` | empty | pass |
| fleet misroot | `git -C /home/vgpnk/Projects/shokunin status --porcelain` | `.scratch/*`, `?? .ufo/reports/round-72/tabi.md` and `?? trail-ids.txt`, none of them souji's | pass |

## Claims

### C1 — operability (pre-report gate byte truth): **improved** (re-measured from receipts)

- Before: `git show 0e1765a0:census/round-74/controls/c1-K-a-do-nothing.txt | grep -E '^(ROW|SUMMARY|EXIT=)'` gives GF1, GF2 and GF3 as `expect=FAIL clean=PASS rc=0 match=no`, then `SUMMARY rows=9 mismatches=3 errors=0` and `EXIT=1`.
- Controls (ii): K-b `SUMMARY rows=9 mismatches=4 errors=0` `EXIT=1`; K-c `mismatches=1` (GF2) `EXIT=1`. Both match the prereg.
- After (i): `records/c1-after.txt` has 9/9 rows `match=yes`, `SUMMARY rows=9 mismatches=0 errors=0`, `EXIT=0`. `records/wave-repair/c1-at-repair.txt` is identical.
- Result: matches the report (3 → 0, EXIT 1 → 0).
- (iii) domain trial (`records/c1-domain-trial.txt`):
  - Output: `check-tip=PASS check-report=PASS check-shonen=PASS check-clean=PASS check-prereg=PASS`, `check-report-contract=SKIPPED`, `EXIT=0`, lane master = ls-remote = `b5e6d514`, tracked=19304.
  - Bound gate sha256 `062b6d39…d341`. This equals `git show 0e1765a0:tools/souji-pre-report-gate.sh | sha256sum`.
  - Bound writer sha256 `70bbf1c2…defa`. This equals the writer at the tip.
- **Deviation (status-neutral):**
  - The prereg's conjunct (iii) names "the stage-W gate". The trial ran the *repaired* gate: stage-W `ec13ba7f` hashes to `3162de98…7c48`, and `git diff --stat ec13ba7f 0e1765a0 -- tools/souji-pre-report-gate.sh` shows 44+/13−.
  - The report discloses that "the repaired gate ran".
  - The trial's lane state is `b5e6d514`, not the cited tip. The tip only adds this receipt (`git diff --stat b5e6d514 0e1765a0` lists 1 file).
- Sourced-claim check: S317 was re-fetched by the closure (below), and the anchor supports "index entry records stat(2) data … object name".

### C2 — calibration (row-specific counter witness, r73 survivors): **improved** (evidence-verified, counts re-measured)

- (i) D6, D7 and D8:
  - Command: `for k in 6 7 8; do git show 0e1765a0:census/round-74/records/c2-after-D$k.txt | grep -cE '^SUMMARY .*base_unwitnessed=1( |$)'; done` → `1 1 1`.
  - The edited rows read `CASE FWw|FC1|FC2 … base=accept … base_witness=no`.
  - Before, on the r73 counter (`controls/c2-before-r73-D6..D8.txt`): `base_unwitnessed=0`, edited row `base_witness=yes`.
  - Result: 0 of 3 → 3 of 3.
- (ii) D1 to D5: the same grep gives `1` ×5.
- (iii) `records/c2-after-pristine.txt` reads `base_forgeries=15 … base_unwitnessed=0 … new_unwitnessed=0 … errors=0 regress=PASS`, `EXIT=0`.
- (iv) selftests, before `cases=52 pass=52 fail=0 EXIT=0` ×4. After:

  | mutant | cases | fail | EXIT |
  |---|---|---|---|
  | M08 | 62 | 1 | 1 |
  | M14 | 62 | 1 | 1 |
  | M15 | 62 | 2 | 1 |
  | M17 | 62 | 1 | 1 |

  Result: 0 of 4 → 4 of 4 killed.
- (v) `records/counter-selftest.txt`: `SELFTEST cases=62 pass=62 fail=0`, `EXIT=0`.
- Result: matches the report.
- Qualification, disclosed by the lane and routed by M3: the witness path set is declared, not derived. S74ExecC2 X4 credits an SY2 defang, and S74MutCounter X09/X15 survive.

### Axis harm

- `git diff 43cd74bb 0e1765a0 -- SCORECARD.md` is additions only: 2 capability rows (r74), the r74 done/r75 planned lines, and the `### Round 74 measurements` table.
- No score changed: calibration 7, coverage 8, operability 8.
- Spot reads support the additions:
  - QUALITY Q134 supersedes Q133's observation clause only, and Q135 is new.
  - SKILL registry rows exist at lines 935-936, plus the existing `souji-pre-report-gate` row at 256.
  - LOG has `## Round 74` at line 2985.
  - The lesson has `## Mistakes` M1-M4.

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1, 3 → 0 mismatches, controls red, domain trial PASS |
| calibration | improved | C2, 0/3 → 3/3 and 0/4 → 4/4, positive control green |
| coverage | unchanged | not claimed; SCORECARD score unchanged |

## Discernment spot-check (`corpus/lessons/round-74.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S317 gitformat-index(5) v2.56.0, anchor at offset 2497 | admit (A, mined) | `curl -sSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitformat-index.adoc` → 15194 bytes, sha256 `c8aca94073fed907c47f631db8a9c53a9a0a0007f8ea3cdce9722224bebbaa93`. This equals the row and the committed capture. Lines 101-106 read "this is stat(2) data / 32-bit file size / This is the on-disk size from stat(2), truncated to 32-bit. / Object name for the represented object". | agree | The quote is verbatim after whitespace normalisation, at 23 words (≤25). Bytes 2497.. of `census/round-74/srcs/gitformat-index.txt` hold the same text. The passage states that the entry keeps stat data beside the object name, which is the premise C1 rests on. A tier-A primary doc pinned at a tag fits scope. |
| first S317 anchor at offset 2194 ("4-bit object type valid values … 1110 (gitlink)") | reject (anchor) | same fetch, lines 88-90; bytes 2194.. of the capture match | agree | The text is real (17 words), but it documents only the mode's type field. It says nothing about stat fields vs object name, so it cannot ground the claim. Replacing it before landing was correct. |

- SOURCES row check: `git diff 43cd74bb 0e1765a0 -- corpus/SOURCES.md` adds exactly one row, `S317`.
  - Status `mined`, verified 2026-11-06, recheck `180d`.
  - `used-by` is `corpus/knowledge/filter-filemode-witness.md`. That file quotes S317 at line 146.
  - Row count `grep -cE '^ {0,3}\| *S[0-9]{3,}'`: 239 → 240.
- Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` gives `souji ok …/corpus/SOURCES.md`, 86 `W04` (duplicate-URL warnings, unchanged), `EXIT=0`.

## Trend verdicts

- **expansion: improved.** There is one new tier-A `mined` row (S317) on ground the lane did not hold: the index-entry on-disk layout. A knowledge entry (`filter-filemode-witness.md` r74) cites it. Two capability rows were admitted to SCORECARD.
- **quality: improved.** Q134 supersedes Q133's overstated observation clause with a narrower, measured one, and the superseded row is named. In-round wave repairs of the gate each carry W-vs-R receipts:
  - `evade-W.txt` `FORGERY=5 FORGERY-MODE=1` → `evade-R.txt` `FORGERY=2`;
  - fail-closed receipts;
  - r27/r36 regress receipts.

  No admitted entry failed its re-check here.
- **discernment: improved.** The non-author spot-check agrees with the gate on both the admit and the reject. The r73 overstatement became a superseding QUALITY row (Q134) backed by lesson M1.

## Routed defects (lane fixes next round)

1. **Domain-trial gate revision.** Prereg C1 (iii) names the stage-W gate, but `c1-domain-trial.txt` binds the repaired gate (`062b6d39…`, not stage-W `3162de98…`). It also measured the tree at `b5e6d514`, not the cited tip.
   - Next prereg should name the gate revision the trial must use, or record an amendment.
   - The report's "at the final tip" wording should say `b5e6d514`.
2. **Undisclosed probe class.** `records/wave-repair/evade-R.txt` carries `OVER-REFUSAL=1` on route `n-filemode-config`: the repaired gate FAILs a byte-equal tree whose mode differs, 100644 → 100755 under `core.fileMode=false`. The report's "FORGERY 6 → 2" omits this class.
   - The refusal is defensible because the mode change is real. However, the probe's bytes-only truth labels it over-refusal.
   - State the ruling, or make the probe's truth mode-aware.
3. **Routed items (a)-(e)** of `round-74.md` stay open on the queue:
   - row-keyed witness derived from the builders (X4, M3);
   - X09/X15;
   - the gate counter binding the writer hash and refusal class;
   - `souji-guard.r9-s18.sh:175`, `souji-record-agreement.py:351`, `souji-idx-repair.py`, writer M03;
   - Q99 freeze-check grammar (failing since r72);
   - caller `PATH`/`BASH_ENV` trust (S74Sentinel E1/E2).
4. **Stated gate limit.** Ignored-untracked forgeries (`f-info-exclude`, `f2-gitignore` remain `FORGERY` in `evade-R.txt`) are a stated limit, not yet a fixed row.
