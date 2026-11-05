# Round 61 verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

## Scope and decision

Reviewed base `c7228424c3919ecf142bab1aec8181722d86467b` → final round tip
`0256c2bc51391e7939995ece37d6a6fa3b85d468`. Status **ok**, **admitted=true**.

One declared claim (C1 calibration, the lane's lowest owned axis at 7). Both arms of its
before→after re-measured by closure over committed bytes reproduce the reported values exactly;
the real r60 freeze record flips pass→fail under the candidate exactly as reported; no owned axis
is harmed. The one C/H item the r60 spot-check routed as blocking (control-receipt chronology) is
the defect this round mechanises, and the erratum is verified against the commit graph.

Closure ran the measurement counter and the freeze checker over pinned revisions (plain
measurements over committed bytes) and executed no lane gate selftest: the selftest tallies, the
frozen-run verdicts and the revision measured are verified as committed evidence.

## Step-1 conformance

- **Report attribution.** `git log --format='%an <%ae> %H' -- .ufo/reports/round-61/souji.md` →
  `souji-shokunin <souji@shokunin.local> c9377a82046fc1352e70f1a26942d986d353c319`. Lane identity.
- **`SHONEN` heading.** The report carries `## SHONEN` with exactly 4 mark lines, one per
  `SHONEN.md` box, all `[~]` with resolvable pointers, zero `[x]`. `SHONEN.md` is byte-unchanged
  from base (`git diff --stat base tip -- SHONEN.md` empty).
- **Cited commits.** `c7228424…`, `da7ceba3950fc3ac946a611791f56e12174272bd`,
  `9849e71851e28d5f1e88ef658418d3c136f94692`, `0256c2bc…` all exist and pass
  `git merge-base --is-ancestor <hash> refs/heads/master` (branch ref, never `@{u}`); the r60-era
  hashes cited by the erratum (`2670e96a…`, `3b552509…`, `d05a0001…`) resolve too.
- **Pushed and clean.** `scripts/hyaku/jj-lane.sh state …/souji-shokunin` → `branch=master
  local=0256c2bc… remote=0256c2bc… ahead=0 behind=0 head=detached tracked=0 untracked=0`;
  `git status --porcelain` prints nothing.
- **Prompt fidelity.** `.ufo/prompts/souji-round-61.md` (committed at fleet `20c79204`) renders
  `templates/round-prompt.md` verbatim for §1–§5 (mission/axes binding; 1–3 claims; frontier step;
  L2 ≥8 in one batched swarm; report contract with the five child-lane items — report path,
  commit-before-report, `SHONEN` heading, commit-hash citation, write/push scope; L0 side channel)
  plus the hyaku addendum §6. `MISSION.md` §L2 concurrency states the ≥8 floor; the wave used 12.
- **Report substance.** All required sections present in order (Work performed, Landed changes,
  Before → after measurements, Sources & frontier, Trend verdicts, SHONEN); a real report, not a
  marker.
- **Frontier step.** Census validate EXIT 0 at round end with `souji ok …/corpus/SOURCES.md`;
  registry rows 213 → 215 re-measured (`git show base:corpus/SOURCES.md | grep -cE` → 213; tip →
  215); malformed rows 0; no duplicate ids; 68 advisory `W04` duplicate-URL warnings, matching the
  report's count. Lesson carries `## Gate`, `## Mistakes` (M1–M4), the Q121 disposition table for
  every C/H wave finding, and the Amendment-27 fresh-start reads.
- **Gate registry.** `SKILL.md` § Round 61 carries the registry row for the r61 control-chronology
  arm (entry, verdict map, selftest spelling `cases=15 pass=15` / `cases=41 pass=41`, pinned-value
  paths, write scope, owner) — registry home satisfied.
- **Driver digest.** `2026-11-05T04:18:26-03:00 launch souji round=61 pgid=2185949
  driver=hyaku-inline attempt=1`; `2026-11-05T05:18:47-03:00 complete souji round=61;
  hyaku-inline attempt=1` (watchdog.log lines 2760/2772, copied verbatim from the live log).
- **Wave.** `census/round-61/wave/w1-results.json`: `seats=12`, 12 results (executor 3, scout 1,
  scribe 1, reviewer 2, critic 1, mutation-tester 1, sentinel 1, connector 1, revenger 1) — attack
  share 4/12 (33 %), connector 1, band 8–16, L2 floor met. The lane-rooted `.ufo/waves/round-61/`
  ready/dispatch markers are lane runtime (not committed anywhere); the durable wave evidence is
  the committed `census/round-61/wave/` copy, so every report pointer resolves.

## Claim re-check — C1 calibration (content-bound control chronology)

**Re-measured by closure at the pinned revisions (work dirs under `/fast/scratch`; the counter
requires a pre-existing `--work` directory and exits 2 `COULD-NOT-EVALUATE` otherwise).**

```sh
# do-nothing arm: base tool bytes in the new slot, measured at base c7228424
python3 -B census/round-61/c1-counter.py --root . --matrix census/round-61/c1-matrix.tsv \
  --base-tool-rev c7228424… --rev c7228424… --work <dir> --new-arm plain
#   → SUMMARY matrix=12 base_forgeries=2 base_honest=4 new_forgeries=2 new_honest=4
#     class_mismatches=2 stubs=REJECTED, EXIT=1   (matches the committed control receipt)

# candidate arm: candidate tool bytes, measured at freeze 9849e718
python3 -B census/round-61/c1-counter.py --root . --matrix census/round-61/c1-matrix.tsv \
  --base-tool-rev c7228424… --rev 9849e718… --work <dir> --new-tool tools/souji-freeze-check.py
#   → SUMMARY matrix=12 base_forgeries=2 base_honest=4 new_forgeries=0 new_honest=4
#     class_mismatches=0 stubs=REJECTED, EXIT=0   (matches census/round-61/records/c1-after.txt)
```

The two `chrono-*` rows that accept at base (`base=accept`) refuse under the candidate with
exactly `CONTROL-ADDED-NOT-BEFORE-FREEZE`, and all four honest rows still accept — the claim's
falsifiable before→after verifies on both ends.

**Real records re-measured by closure.**

- r60 freeze record, candidate arm: `python3 -B tools/souji-freeze-check.py --root . --prereg
  census/round-60/preregistration.txt --rev d05a0001… --substance` → two
  `CONTROL-ADDED-NOT-BEFORE-FREEZE` findings (C1, C2), `SUMMARY claims=2 findings=2`, EXIT=1 —
  the round's headline result reproduces. Base arm: `findings=0`, EXIT=0 (committed receipt
  `real-r60-prereg-base.txt`).
- r61 freeze record, candidate arm: `SUMMARY claims=1 findings=0`, EXIT=0 (reproduced).

**Chronology and erratum re-run against the commit graph.**

```sh
git log --diff-filter=A --no-renames --full-history --format=%H -- \
  census/round-61/controls/c1-do-nothing.txt        # → da7ceba3… (the pre-freeze instruments commit)
git merge-base --is-ancestor da7ceba3… 9849e718…    # → 0, and da7ceba3 ≠ freeze: strict ancestor
git show da7ceba3:tools/souji-freeze-check.py | sha256sum
#   → 5794ab27b918a91c1f3fdb70fc2799e96846af482ac544a5bc9fd850e1d4c1c5 (matches every receipt)
git cat-file -e 3b552509…:census/round-60/controls/c1-do-nothing.txt   # → EXIT 128 (absent)
git log --diff-filter=A --no-renames --full-history --format=%H -- \
  census/round-60/controls/c1-do-nothing.txt        # → 2670e96a… (the r60 freeze commit itself)
```

`R61-ERRATUM-R60` is correct on both claims: the r60 prose commit `3b552509…` does not contain
either control receipt, and both are added by the r60 freeze commit `2670e96a…`.

**Sweep (committed evidence + count).** `census/round-61/records/substance-sweep.txt`: 74 rows =
37 preregistrations × 2 modes; `grep -c ' DIFF '` → 11, all `mode=substance`, on rounds 41, 42,
43, 45, 47, 48, 50, 51, 54, 55, 60; every plain row SAME (`plain_diff=0`); round 60 is the only
`base_rc=0 cand_rc=1` flip; no base finding is removed anywhere. Matches the report.

**Gate evidence verified (not executed).** Committed selftest tallies at the freeze revision
`9849e718…` with the candidate tool digest `5794ab27…`: default `SELFTEST cases=41 pass=41
fail=0` EXIT=0, `--substance` `cases=15 pass=15 fail=0` EXIT=0
(`census/round-61/records/selftest-candidate-{plain,substance}.txt`). The SKILL registry row's
pinned values match these tallies. The do-nothing receipt predates the freeze (chronology above),
so the before-state is red-before-freeze as Q122 requires.

## No-harm check and axis verdicts

`git diff base tip -- SCORECARD.md` is append-only: a Round 61 measurements row, the erratum, and
Planned (r62); calibration 7 / coverage 8 / operability 8 numerically unchanged; `SHONEN.md` and
`PROVINCE.md` unchanged. The candidate adds refusals only — `new_honest=4` (no honest row newly
refused), plain path byte-identical over all 37 preregistrations, no base finding removed in the
sweep. LOG.md carries the `## Round 61` entry (line 2808).

| Owned axis | Verdict | Evidence |
|---|---|---|
| calibration | improved | C1's before→after re-measured and verified; the instrument now refuses the exact r60 defect shape (`rewritten-at-freeze`: base accepts, candidate refuses) and flips the real r60 record pass→fail; the numeric score stays 7 with the lane's stated no-reproducible-0–10-mapping reason recorded in SCORECARD (noted below, not a bar) |
| coverage | unchanged | no coverage claim; PROVINCE.md unchanged; no Core promotion, no package adoption (connector ran a read-only overlap scan) |
| operability | unchanged | no operability claim this round; the r61 registry row extends the existing gate without changing the default path (sweep: 0 plain differences) |

## Discernment spot-check (LEARNING.md — outside, non-author)

Re-opened the live pages on 2026-11-05 (`curl -sL`); both fetched pages hash **byte-identical**
to the committed captures (`f206647f…2f69b`, `ecaa637b…43fb8`; `sha256sum -c SHA256SUMS` → 2/2
OK), and both located quotes are present verbatim in the tag-stripped, whitespace-normalised
page text (raw HTML wraps the sentences across lines, so a naive grep misses them). S288 re-open
verified: the committed r60 capture hashes to `ece1ab71…79f68079`, exactly the lesson's
no-drift claim.

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S290 git-log(1) path-limited history | admit | `https://git-scm.com/docs/git-log`, DESCRIPTION section | **agree** | 14-word quote present verbatim ("Various other options and paths parameters can be used to further limit the result."); tier A for the path-limited enumeration the content rule uses, and the row honestly scopes what it does *not* source (blob equality, ancestry composition) |
| S291 git-update-index(1) skip-worktree caveat | admit | `https://git-scm.com/docs/git-update-index`, NOTES section | **agree** | 21-word quote present verbatim, and its surrounding NOTES paragraph is precisely about using assume-unchanged/skip-worktree to ignore tracked-file changes ("Users often try to use the assume-unchanged and skip-worktree bits… This does not work as expected…"); the row keeps the concealment claim on the host probe, not the manual — correct tier discipline |
| Rejected inference: "a silent `git status --porcelain` certifies worktree content" | reject | same NOTES passage | **agree** | the NOTES caveat directly undermines the inference; the flip (a manual statement that skip-worktree paths are checked on every status) is the right falsifier, and the reviewer's git 2.56.0 probe is correctly filed as host evidence, not manual fact |

The gate's sampled decisions (two admits, one rejection) all survive outside re-opening. The
lane's `discernment: unchanged (pending)` verdict upgrades to **improved** with this agreement;
Q121 and Q122 each cite the lesson that produced them.

## Learning trends

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | improved | two admitted knowledge entries on F1 ground (`control-chronology-binding.md` citing mined S290+S251, `skip-worktree-concealment.md` citing mined S291), both carrying the provenance trio; `corpus/README.md` § Frontier (r61) indexes all three F1 entries including the previously unindexed r60 entry (r60 routed defect 4 repaired) |
| quality | improved | the add-commit chronology rule is superseded by a content-bound rule that refuses two shapes the base accepted (2 → 0 new forgeries on the frozen matrix) while refusing no honest row; the r60 erratum lands without rewriting frozen bytes; the broken SKILL evidence path is repaired (r60 routed defect 5; `grep -c 'census/round-60/w1/…' SKILL.md` → 0, fixed path at SKILL.md:796); no admitted entry found false |
| discernment | improved | this spot-check agrees with the gate on the sampled admit, caveat-admit and rejection; M1–M4 are mined with evidence pointers and Q121/Q122 are lesson-grounded criteria |

## Routed defects — souji round 62

1. **Receipt-writer skip-worktree blindness (HIGH-1, blocking the C2 successor).** `tools/souji-receipt-write.py`'s dirty check is `git status` (~line 131) and accepts a skip-worktree-concealed
   non-instrument file; planned r62 fix (refuse worktree bytes ≠ committed blob and refuse
   `git ls-files -v` S/h entries) is already written into SCORECARD Planned — land it with a
   red-before control committed strictly before its freeze (Q120/Q122).
2. **`## MACHINE BLOCK` preregistration requirement** (critic F13, Q59) is routed to r62 as a
   question pending confirmation that `souji-axis-check.py` runs on the lane's preregistrations —
   an operator decision is needed before it can bind.
3. **F3 (delete-and-re-add at freeze with new bytes)** is refused by the same rule but has no
   matrix row; add the row when the matrix is next touched.
4. **Historical records.** Rounds 41–55 and 60 gain `CONTROL-ADDED-NOT-BEFORE-FREEZE` on their
   control receipts (11 sweep rows). Reported, not rewritten — keep it that way; a successor claim
   must not cite those records as green.
5. **Numeric axis mapping.** "no reproducible 0–10 mapping" now covers two consecutive rounds on
   calibration; either derive the mapping or record the axis as verdict-carrying in SCORECARD so
   the score cell stops reading as a stale measurement.

**r60 routed defects: all six addressed** — chronology mechanised as this round's claim (defects
1–2), critic Finding 1 surfaced as M1 (3), README index repaired (4), SKILL path repaired (5),
r56–r59 debts carried open in Named limits/Planned (6).

SHONEN promotion remains operator-owned: all four boxes are lane-asserted `[~]` with pointers,
and every box is checkable by a non-author from committed surfaces (SKILL decision tables and
registry rows; LOG round-61 end-to-end freeze→after task; the counter + matrix + knowledge
recheck commands run without oral context; PROVINCE unchanged with sibling mechanisms routed).
Closure writes no `[x]`.

Closure self-evaluation: accuracy 5 (every numeric re-derived at pinned revisions; gate evidence
kept separate from execution), completeness 4 (all step-1 items, claim, no-harm, discernment,
trends, routed queue), clarity 4, actionability 5 (five routed items with owners), conciseness 4.
Highest-impact improvement: a preregistration-machine `## MACHINE BLOCK` would let the axis
checker bind the same receipts the freeze checker binds. No tools installed or updated.
