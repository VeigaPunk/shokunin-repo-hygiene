author: hyaku closure (non-author integrator, @m_kfc)

# Souji round 28 — non-author closure spot-check

Lane base `3a2a80d0d18940a5e352ebc526da22a57dad83c4` → tip `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` (branch `master`).
Report `.ufo/reports/round-28/souji.md`; prompt `.ufo/prompts/souji-round-28.md`.
Driver digest (copied from mutable `.ufo/watchdog.log`):

- `2026-10-25T15:40:35-03:00 launch souji round=28 pgid=3077632 driver=hyaku-inline attempt=1`
- `2026-10-25T16:08:12-03:00 complete souji round=28; hyaku-inline attempt=1`

## Step-1 conformance

| check | command | observed |
|---|---|---|
| report landed by lane | `git log --format='%an %H' -- .ufo/reports/round-28/souji.md` (fleet) | `souji-shokunin 9cb1a3ceb6bf3a0b4e4aa1f6276e79c76ff0946b` (16:06:13, before the 16:08:12 complete line) |
| prompt committed | same, prompt path | `souji-shokunin b5022a43b981da37f449a6fecb3f7b8105297929` |
| SHONEN heading | read report | `## SHONEN`, four `[~]` lines, one per box, each with a pointer |
| cited commits exist + ancestry | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> master` for 0c96332, 765fe8b, ed270c4, de478b4, fec846d | all `commit`, all ancestors of `master` |
| pushed, no leftovers | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain \| wc -l`; `git ls-remote origin refs/heads/master` | `local=remote=fec846d… ahead=0 behind=0 tracked=0 untracked=0`; `0`; `fec846d…` |
| prompt contract | read prompt §1–§5 | MISSION/AXES binding, 1–3 claims + lowest axis, frontier step, L2 batched-swarm floor, report path, commit-before-report, SHONEN heading, hash citation, write scope, push scope, L0 channel all present |

No step-1 defect.

## Claims — re-checks

Which were re-measured vs evidence-verified: C2 re-measured (plain git/grep) + gate evidence-verified; C1 evidence-verified for the
lane-owned landing gate plus plain pointer measurement; C3 re-measured independently (clean export of committed bytes).

### C1 calibration — Q57/Q59 dangling pointers 2 → 0: VERIFIED

- Evidence-verified (lane gate, not executed by closure per §Gate standard): `census/round-28/records/c1-before.tsv` at 3a2a80d
  `findings=2 checked_reg=52`, rc 2; `c1-control.tsv` (do-nothing) identical; `c1-after.tsv` at `de478b483db66a8d8ff2d627cde1ccce6e21a014`
  `SUMMARY findings=0 checked_reg=52`, exit 2 from `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-28/` — the same
  could-not-evaluate line is present at base, so it is not a finding. No exemption row used. Gate registry row: `SKILL.md:197`.
- Plain re-measure at fec846d: `git show fec846d:corpus/QUALITY.md | grep -c 'corpus/knowledge/registry'` → `0`;
  `grep -c 'round-24.md:232'` → `0`; `git cat-file -t fec846d:census/round-28/q57-sites.txt` → `blob`;
  `…:census/round-24/records/slice-verdicts.tsv` → `blob`.
- Tip delta (de478b4..fec846d changes SCORECARD.md + three after receipts): every backticked path token added to SCORECARD
  resolves at fec846d (`c1-before.tsv`, `c2-before.tsv`, `c3-before.tsv` blob; `.ufo/waves` tree), so no new dangling pointer at the tip.

### C2 coverage — F4 origin-record knowledge: VERIFIED (closure disagrees with the lane's self-declared miss)

- `git grep -lE '^ground: F4' <rev> -- corpus/knowledge/ | wc -l` → base `4`, ed270c4 `6`, fec846d `6`.
- `git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → base `135`, fec846d `139`;
  same excluding the S215 row (`grep -cvE '^\|[[:space:]]*S215[[:space:]]*\|'`) → `138`.
- Ruling on the counter: the frozen text reads “135→138 (the three POSIX rows; S119 row, if appended, is not counted in this
  claim)”, and the same preregistration prescribes ADMIT → append S215. The exclusion was declared before any after-data, so
  counting 138 non-S215 rows applies the frozen counter as written; it does not narrow it. The lane's reading (literal 139 ≠ 138)
  would make the claim fail by construction on its own ADMIT branch.
- Coverage map: F4 row `corpus/README.md:42` lists all six F4-grounded entries — plain re-derive `grounded=6 mapped=6
  grounded-not-mapped=` (none). The coverage-agreement tool prints global `grounded=13 mapped=13 dangling=0 mismatches=0`
  (`c2-after.tsv`, evidence-verified); the frozen `6/6` literal was not that tool's output shape — a Q58-class preregistration
  defect (routed), while the kill rule (“map mismatch”) is not triggered.
- Gate (evidence-verified): `c2-after.tsv` `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`.
- Census re-run by closure: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, rc 0, 35 W04 warnings only.
- Rows: S212/S213 used-by `corpus/knowledge/origin-record-exclusivity-r28.md`, S214 used-by `…durability-r28.md`; each entry's
  `source:` lines cite exactly those rows; all four new rows have 11 columns. S215 snapshot `git show fec846d:census/round-28/sources/git-fetch-zh-HANS-CN.html | sha256sum`
  → `a7f4742d…b574042`, matches the row pin.
- Defect (outside this claim's counter): S215 used-by `corpus/knowledge/git-auto-maintenance-trigger-set.md`, but that entry's
  `source:` lines cite S128/S129/S130 and never S215 (`git grep -c S215` → no match). Used-by is one-directional.

### C3 operability — wave evidence capture: FAILS its frozen kill rule

- Dirty counter re-measured: `git status --porcelain` in the lane → 0 lines; `c3-before.tsv` `dirty_waves=163`, control 163.
- Fixture (evidence-verified): `c3-after.tsv` `cases=6 pass=6 control=TAMPER-REJECTED exit=0`.
- Independent manifest check over **committed bytes** (closure, read-only):
  `git archive fec846d census/round-2{6,7,8}/waves | tar -x -C $T`, then `sha256sum -c manifest.sha256` in each:
  r26 `ok=1228`, `152` records `FAILED open or read`, rc 1; r27 `ok=124` rc 0; r28 `ok=75` rc 0.
- Cause: 152 of the 1382 r26 manifest records are on the lane's disk but not in git. `git check-ignore -v` attributes them to
  ignore rules copied into the capture: `census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/` (138),
  `.gitignore:__pycache__/` (4), `case-V6/.gitignore:/ledger*.tsv` (4), `vadv-49/.gitignore:shims/` (2), `case-F7`/`case-F8` `.scratch/.gitignore:*` (2),
  `case-V6/.gitignore:/src/`, `/vault/` (2). The capture tool verified its destination on disk, not the committed set, so the
  committed r26 receipt is not byte-exact and a fresh clone cannot verify it. Kill rule “a missing or non-verifying manifest for a
  claimed round” fires.
- Correction to the lane's disclosed limitation: the two “improperly formatted” r26 lines are correct GNU escaped records
  (`\<hash>  ./…first\nsecond.md`); this host's `/usr/bin/sha256sum` is uutils 0.8.0, which rejects every escaped line
  (reproduced on a fresh one-file manifest). Hashing both files directly matches the manifest (`1009b12c…78e71`, `ae599d14…212fc`).
  The real defect is the 152 missing records, which LOG.md Round 28, SCORECARD and `corpus/lessons/round-28.md` do not mention.
- Also: 15 tracked r26 receipt paths (symlinks, e.g. `…/mock-cli/obsidian-cli`, mode 120000) carry no manifest record.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | C1 verified: findings 2→0, no exemption, pointers resolve at tip |
| coverage | improved | C2 verified: F4 4→6, three mined tier-A POSIX rows (138 excl. S215), F4 map 6/6, gate ok=2, census rc 0 |
| operability | unchanged | C3 fails: r26 manifest does not verify over committed bytes (152 absent records); r27/r28 receipts and the fixture are real, nothing previously working regressed |

SCORECARD diff 3a2a80d..fec846d adds only the Round 28 measurements table; owned scores unchanged (calibration 7, coverage 8, operability 8). No axis harmed.

## Discernment spot-check (`corpus/lessons/round-28.md` `## Gate`)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S212 POSIX open() | ADMIT | https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html fetched 2026-10-25 | agree | live sha256 `57b77091…60dc3a` equals the SHA256SUMS pin; quote “creation of the file if it does not exist shall be atomic with respect to other threads executing” found (1 match); tier-A normative spec directly grounding O_EXCL exclusivity |
| S214 POSIX fsync() | ADMIT | https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html fetched 2026-10-25 | agree | live sha256 `5c2975ab…ca49747` equals pin; quote “system crash or other failure that all data up to the time of the <i>fsync</i>() call is recorded on the disk.” found byte-exact, 21 words (≤25) |
| staged S216 approximate-matching paper | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:114` (read-only) | agree | ssdeep near-duplicate thresholds are F3 duplicate-verdict ground, not F4 origin-record primitives; flip condition recorded |
| staged S138 Qiita Git-GC note | REJECT | same file, line 36 | agree | tier-B community summary of `gc.auto`, F1/F2 reclamation ground, not F4; the row itself disclaims authority |

New SOURCES row re-opened: S214 (`corpus/SOURCES.md:159`) — URL live, pin matches, its Gate quote is 21 words. SOURCES has no quote
column (`teaches` cell is a paraphrase); the located quote lives in the lesson Gate and `census/round-28/records/posix-quotes.tsv`.

## Trend verdicts

- expansion — improved: two admitted F4 entries on POSIX-primitive ground the map did not hold, each citing mined S212–S214; F4 map row lists both.
- quality — improved: GLib r27 snapshots re-verify (`census/round-28/records/f4-recheck.tsv` both `YES`, digests equal `census/round-27/sources/SHA256SUMS`); POSIX and S215 pins re-verified live/committed by closure; no admitted entry failed re-check.
- discernment — improved: the non-author spot-check agrees with the gate on two admits and two rejects.

## Routed defects (lane fixes next round)

1. C3 receipt: commit or re-capture the 152 ignored r26 records (e.g. capture with nested `.gitignore` neutralised, or record them
   as excluded in the manifest), and make `tools/souji-wave-evidence-capture.sh` verify against what git will commit
   (`git check-ignore` / `git ls-files` on the destination); add a nested-`.gitignore` case to `tests/fixtures/r28-wave-evidence-capture.sh`.
   Also cover symlinks (15 uncovered tracked paths).
2. Append-only correction owed: LOG.md Round 28, SCORECARD Round 28 row and `corpus/lessons/round-28.md` describe the r26
   limitation as “two malformed newline-path records”; the records are valid GNU escapes (uutils 0.8.0 parser limit) and the real
   defect is 152 absent records.
3. C1 gate: `.ufo/waves/` is now gitignored, so `souji-landing-gate.py`'s report check can never evaluate committed round reports
   (permanent rc 2 `COULD-NOT-EVALUATE`); point it at the committed `census/round-<N>/waves/` capture.
4. C2 preregistration (Q58 class): the `6/6` coverage-agreement literal was not derived from the tool's base output (global counts);
   future targets must quote the counter's own output shape.
5. S215 used-by names `corpus/knowledge/git-auto-maintenance-trigger-set.md`, which does not cite S215; add the `source:` line or fix used-by.
6. The lane's self-ruled C2 “miss” misread its own frozen exclusion clause; record the reading in the next lesson.

Verdict: rejected-honest-stop (C3 fails its kill rule; no axis harmed). SHONEN boxes look fully checkable by a non-author; promotion is operator-owned.
