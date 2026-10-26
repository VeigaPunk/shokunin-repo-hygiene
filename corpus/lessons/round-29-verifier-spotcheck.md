author: hyaku closure (non-author integrator, @m_opus)

# Souji round 29 — non-author closure spot-check

Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e` → tip `ea4d798f651db93556129e0c3f9c455ca85d8037` (branch `master`).
Report `.ufo/reports/round-29/souji.md`; prompt `.ufo/prompts/souji-round-29.md`.
Driver digest (copied from mutable `.ufo/watchdog.log`):

- `2026-10-25T20:07:54-03:00 launch souji round=29 pgid=818105 driver=hyaku-inline attempt=1`
- `2026-10-26T01:03:32-03:00 complete souji round=29; hyaku-inline attempt=1`

All re-measurements below ran 2026-10-26 (UTC ~04:00) over committed bytes (`git cat-file`/`ls-tree`/`grep` at the named
revision), never the lane working tree, which was clean (`tracked=0 untracked=0`). No lane gate, counter or fixture was
executed; lane-owned instruments are evidence-verified only.

## Step-1 conformance

| check | command | observed |
|---|---|---|
| report landed by lane | `git log --format='%an %H %ci' -- .ufo/reports/round-29/souji.md` (fleet) | `souji-shokunin 17cee42d796e622b32210a4f5e190940ba854107 2026-10-25 23:17:09 -0300` — after the cited lane HEAD 48e2e95 (23:16:22), before the complete line |
| prompt committed | same, prompt path | `souji-shokunin 7bb1647f61365e9c7a84295240b16b5c1df2f719` (20:07:52, before launch) |
| SHONEN heading | `grep -c '^## SHONEN'` report; `git show ea4d798:SHONEN.md \| grep -c '^- \['` | `1`; four boxes, four `[~]` lines each with a pointer |
| cited commits exist + ancestry | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> master` for 691dd29, b8cb4b3, 8aaacf5, b862007, 1dc6785, de874ee, f4326a8, 48e2e95 (full hashes) | all `commit`, all ancestors of `master` |
| pushed, no leftovers | `scripts/hyaku/jj-lane.sh state <lane>`; `git status --porcelain \| wc -l`; `git ls-remote origin refs/heads/master` | `local=remote=ea4d798… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `0`; `ea4d798…` |
| prompt contract | grep prompt | MISSION/AXES binding (l.5), 1–3 claims + lowest axis (l.11–16), frontier step §2b (l.42), L2 batched floor §3 (l.80–82), report path + required sections (l.101–118), commit-then-push + push scope + L0 channel §5 (l.131–139), write scope (l.318), report-lands-last + hash (l.384–391) |

Step-1 defects (status-neutral):

- D1 — evidence cited before it landed. The report's C1 row cites `census/round-29/records/final-tip-measure*.txt`; both files
  were committed only in `ea4d798` (2026-10-26 00:37:58 -0300), 80 min after the report commit 17cee42. The `ea4d798` subject
  ("straggler seat reports written after the landing") does not describe its content (`git show --stat ea4d798`: only those two
  measure records, 44 lines).
- D2 — the report has no explicit "cross-domain evidence encountered" line (PROTOCOL §Round-robin minimum content); the misroot
  sweep and the SwarmScout37 sibling-overlap pointer cover it in substance.

## Claims — re-checks

Re-measured independently: C1 (K1 and K2), C2 (r26–r29 receipts, plus receipt-to-source fidelity), C3 (F3 entry count, row
count, touched/new rows). Evidence-verified only: the C3 landing-gate/integrity legs and the coverage-agreement 13→15 count
(`census/round-29/records/final-tip-measure.txt` L1–L9 PASS at de874ee; `final-tip-measure-2.txt` `grounded=15 mapped=15` at
f4326a8), the fixtures' red-before tallies (`records/c1-fixture-red-before.txt` `cases=20 pass=8`, mutant `pass=15`;
`records/c2-fixture-red-before.txt` base tool failures on cases 7–11).

### C1 calibration — registry/record agreement 10 → 0: VERIFIED

Method (my own code, not the lane tool): parse `corpus/SOURCES.md` rows (`^ {0,3}\|\s*S\d{3,}\s*\|`, 13 cells) at each rev; K1a =
`used-by` paths absent at rev or not containing the row id (`\bS###\b`); K1b = every `S###` in a `corpus/knowledge/*.md` line
starting `source:` whose row does not list that entry. K2 = the four rows of `census/round-29/stale-statements.tsv`: phrase
still at `file:line`, file at tip begins with its base blob (append-only), and a later line starting `R29-CORRECTION ` names
the tag.

| rev | K1a | K1b (unique) | K2 uncorrected |
|---|---|---|---|
| 691dd29 | 1 (`S215` nocite `git-auto-maintenance-trigger-set.md`) | 5 (S075, S076 → process-residue-observations; S022 → quarantine-origin-record-fields-r24; S024, S025 → quarantine-same-filesystem-rename) | 4 (no R29-CORRECTION anywhere) |
| ea4d798 | 0 | 0 | 0 — LOG.md, SCORECARD.md, lessons/round-28.md each `startswith(base)=True`; R29-CORRECTION lines 4/3/4 tagging `LOG.md:1758`, `SCORECARD.md:23`, `corpus/lessons/round-28.md:22` + `:40`; all four phrases still at their lines |

6 + 4 = 10 → 0, matching the frozen `k1=6 k2=4 mismatches=10` → `0`. The nine SOURCES cell edits I diffed (base vs tip, per cell)
are exactly the nine rows of the lesson's touched-row log, all in `status`/`used-by` (contract rule 2); no row deleted. Scope
caveat stands as disclosed: K1 is registry self-consistency; only SCORECARD.md:23 of the self-assessment files is bound.

### C2 operability — committed-bytes receipts 152/14 → 0/0: VERIFIED

Method: parse `census/round-N/waves/manifest.sha256` at rev (GNU `\`-escaped lines decoded), map each record to
`git ls-tree -r -z <rev> -- census/round-N/waves/`, sha256 the blob (`git cat-file blob`); uncovered = committed paths with no
record that are not the three side files and not symlinks listed in `symlinks.tsv`.

| rev | r26 | r27 | r28 | r29 |
|---|---|---|---|---|
| 691dd29 | records 1382, absent 152, digest-mismatch 0, unrecorded 14 (all symlinks) | 124 / 0 / 0 / 0 | 75 / 0 / 0 / 0 | no manifest |
| ea4d798 | records 1381, absent 0, mismatch 0, unrecorded 0 | 124 / 0 / 0 / 0 | 75 / 0 / 0 / 0 | 131 / 0 / 0 / 0 |

Fidelity re-check: of the 1382 base r26 records, 1236 survive by path+digest, 131 by digest under a `renames.tsv` `.captured`
path, 4 by path+digest in `excluded.tsv`; 11 changed digest (`w1/CritAmendNeed.md`, `landing-check.md`, `report-draft.md`,
`verify-loop.sh`, …). For four sampled, the tip capture blob equals the tracked source blob `ea4d798:.ufo/waves/round-26/w1/<f>`
(e.g. `landing-check.md` 896a9d3 = 896a9d3; base capture 2f85c2c) — the recapture restored the tracked bytes the r28 copy had
diverged from, matching the lane's `fidelity=11 → 0`. `symlinks.tsv` 17 rows, every target equals the committed link blob.

### C3 coverage — F3 duplicate-verdict entries 0 → 2: VERIFIED

`git grep -lE '^ground: F3' <rev> -- corpus/knowledge/` → base 0, tip 2 (`duplicate-verdict-identity.md`,
`duplicate-verdict-byte-equality.md`); registry rows 139 → 143 (new S216–S219, 13 cells each, `mined`, used-by exactly the
citing entries). Both entries open with `source:` (S###) / `verified-at:` / `recheck:` and `ground: F3`; README coverage row F3
now names all three F3 entries. Baseline caveat (Critic49) stands: the r12 held F3 entry has no `ground:` header, so `0 → 2`
counts newly tagged entries; the content is new (inode identity via statx/link; cmp's exit-2 trouble outcome).

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | C1 re-measured 10 → 0; stale r26 statements corrected append-only |
| operability | improved | C2 re-measured 152/14 → 0/0 over four receipts; tracked-source fidelity restored |
| coverage | improved | C3 re-measured 0 → 2 F3 entries, 139 → 143 rows |
| depth, freshness, adjacency | unchanged | not claimed; SCORECARD diff is append-only (`git diff 691dd29 ea4d798 -- SCORECARD.md`: +27 −0, owned scores 7/8/8 unchanged); only deletion in README/SKILL/QUALITY/PROVINCE is the in-place F3 map row |

No axis harmed.

## Discernment spot-check (`corpus/lessons/round-29.md` `## Gate`)

Fetched to `/var/tmp/souji-r29-close.*` (scratch; not evidence) with `curl -fsSL`; quotes searched in tag-stripped,
whitespace-collapsed text.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S219 cmp(1) | ADMIT | https://man7.org/linux/man-pages/man1/cmp.1.html sha256 `5c68e8d8…cd046a3` (= lesson pin) | agree | "Exit status is 0 if inputs are the same, 1 if different, 2 if trouble." found verbatim (15 words); tier A for the man page is right |
| S216 statx(2) | ADMIT | https://man7.org/linux/man-pages/man2/statx.2.html sha256 `2a47fe31…18359e8e` (= pin) | agree | "The number of hard links on a file." and "The inode number of the file." found; scope cell separates it from S114 (the census W04 duplicate-URL warning is the disclosed one) |
| S217 Broder 1997 (new row quote) | ADMIT, tier B | Princeton PDF sha256 `da122799…101ef56b`; `pdftotext` decode `3ba1e117…d28325d` (both = pins) | agree | Abstract quote found verbatim, 23–24 words (≤25); vocabulary-only scope and B tier for a course-archive copy are conservative and stated |
| staged `near-duplicate-threshold-r28.md` | REJECT | `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/near-duplicate-threshold-r28.md`; its source https://ssdeep-project.github.io/ssdeep/usage.html sha256 `4e150dee…c328739` (= its pin) | agree with the decision, disagree with the stated reason | ssdeep quote "it does not mean that those files are related" is present, but the entry explicitly sets **no** threshold; the lesson row's reason "each states a threshold, operating point or relation choice" is false for it. The sound reason (fuzzy-hash similarity is outside F3's byte-identical scope per `PROVINCE.md:69`; its only consequence is already held by `dupe-finders-detect-then-act.md`) exists only in `census/round-29/waves/w1/deliver-f3-scope-table.tsv` |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, rc 0, 36 W04
(new: S216 duplicate URL with S114), no error class.

## Trend verdicts

- expansion — improved: two admitted entries on F3 frontier ground, each `source:` citing `mined` rows opened this round;
  two capability rows demonstrated by committed tool output (`final-tip-measure.txt` C1 v2 and capture `--verify --rev`).
- quality — improved: r26 receipt re-verifies over committed bytes and matches tracked sources; S215's false `mined` corrected;
  stale statements corrected append-only; the three re-opened admitted sources hash-match their pins.
- discernment — improved: the spot-check agrees with the gate on all three admits and on the reject decision; the reject's
  written reason is imprecise (D4), a recording defect rather than a wrong call.

## Routed defects (lane fixes next round)

1. D1 — a report must cite only committed evidence: land `final-tip-measure*` before the report, and give post-report
   commits accurate subjects (ea4d798).
2. D3 — commit the observed green fixture output (`tests/fixtures/r29-registry-agreement.py` 20/20,
   `tests/fixtures/r28-wave-evidence-capture.sh` 15/15): only the red-before runs are committed; the green tallies exist as prose
   in the report, SCORECARD and `amendments.txt`.
3. D4 — `corpus/lessons/round-29.md` `## Gate`: the grouped reject row misstates the reason for `near-duplicate-threshold-r28.md`
   (and per the scout table, `near-duplicate-operating-point-r28.md` also sets no threshold); append a correction with per-entry
   reasons.
4. Landing gate at the tip still prints `findings=2` (LG-DANGLING-PTR false positives on `round-%s` tokens, QUALITY.md:150)
   and `COULD-NOT-EVALUATE` (no reports under the gitignored `.ufo/waves/round-29/`) — r28 routed defect 3, still open.
5. Prereg SUMMARY literals omit the trailing `rev=` (lane-disclosed; Reviewer43 F7).
6. D2 — add the cross-domain-evidence line to the report.
7. Wave hygiene: `git clone --no-local` scratch clones must drop `origin` (SwarmExecutor17 pushed to lane `master`, restored).

SHONEN: four `[~]` boxes; not yet fully checkable from committed evidence by a non-author (box 3 rests on fixture green runs
with no committed output, D3). Promotion is operator-owned.
