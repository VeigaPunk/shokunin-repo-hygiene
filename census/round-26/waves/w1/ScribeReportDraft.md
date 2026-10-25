# ScribeReportDraft — round 26 report skeleton

Report: `.ufo/waves/round-26/w1/ScribeReportDraft.md`; deliverable: `.ufo/waves/round-26/w1/report-draft.md`.

## Status

STATUS: PASS — the skeleton exists with all eight required sections in order, the three declared claims named at top, and a per-section L1 checklist; every measured value is an `[EVIDENCE-PENDING: …]` placeholder and seven draft-time defects are handed to the L1 instead of being asserted as claim verdicts. The L1 committed the draft mid-flight at `166baa1`; the drafting seat's later wording-only edits remain uncommitted in the worktree (`M .ufo/waves/round-26/w1/report-draft.md`, 3 insertions / 2 deletions).

## Evidence

Read first: `.ufo/waves/round-26/preregistration.txt` (machine block C1 calibration / C2 coverage / C3 operability; base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`) plus `preregistration-amendment-1.txt` (`89e0fce`: C2 K4 literal corrected to base-derived `grounded=7`/`kill_tested=7`) and `preregistration-amendment-2.txt` (`965b869`: C1 kill rule read as byte-content spans). Structure source `.ufo/reports/round-25/souji.md` is **not** under the lane (`ls .ufo/` there shows only `quarantine/`, `waves/`); the round-25 fleet report exists only at `/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/souji.md`, read read-only.

- `git log --format='%h|%s' --reverse 0eca7c8..HEAD` at `166baa1` → 18 commits, `12fd90b` (freeze) … `166baa1`. The tip moved three times during this seat (`ba8b54b` → `c5949013` → `0c92c2e` → `33e6807` → `9a6e0f1` → `166baa1`), so the draft names no tip and uses `TIP-40`.
- Draft-time counter observations (this seat, HEAD `c5949013`, **not** the landing gate): `grep -cE '^(Insert…|Optional…)' SCORECARD.md` → `0`; `awk '/^### Round (23|24|25) measurements/…'` → `17 44 78 ` (17<44<78); `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `132`; `git grep -l '^ground: F1' HEAD -- corpus/knowledge/ | wc -l` → `2`.
- Receipt bytes read (never re-run): `c1-before` `rev=12fd90b` `markers=2 headings=17 175 231`; `c1-after` `rev=07f83e6` `markers=0 headings=17 44 78`; `c2-before` `rev=89e0fce` `grounded_f1=0 registry_rows=127`; `c2-after` `rev=e0f8dcd` `grounded_f1=2 registry_rows=132`; `c2-k4-base` `rev=0eca7c8` `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`; `c2-gate` `rev=33e6807` `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`; `c2-k4-after` `rev=33e6807` `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`; `c3-before` `rev=89e0fce` `axis_check_tool=absent`; `c3-after` `rev=c5949013` `claims=3 flags=0`, `cases=12 pass=12 control=FALSE-GREEN-REJECTED`.
- `git ls-tree --name-only 166baa1 census/round-26/records/` → `c1-before, c1-after, c2-before, c2-after, c2-gate, c2-k4-base, c2-k4-after, c3-before, c3-after, empty-slice, empty-verdicts` (no `c3-control`).
- `git ls-tree --name-only 0eca7c8 census/round-26/` → empty; `12fd90b` and `89e0fce` → all three counters present.
- Blob identity: `git rev-parse 0eca7c8:SCORECARD.md 12fd90b:SCORECARD.md` → both `4b564bc6…`; `0eca7c8:corpus/SOURCES.md 89e0fce:corpus/SOURCES.md` → both `f3cffccc…`.
- `python3 -c` over `.ufo/waves/round-26/w1-spec.json` → 87 items: executor 31, reviewer 15, scribe 11, scout 10, critic 9, mutation-tester 6, connector 2, simplifier 2, sentinel 1; `w1-dispatch.json` `counts.spawn=87`.
- Documentation state at `166baa1`: `corpus/QUALITY.md:143` Q59 present; `SCORECARD.md:264` `### Round 26 measurements …` present; `corpus/README.md` has no Round 26 section (`grep -niE '^## .*(round ?26|r26)'` → empty; last section `:538`); `LOG.md` has no Round 26 entry (last heading `1723:## 2026-10-25 — Round 25 honest stop…`).
- `ls -d considerthese` → No such file. `git status --porcelain` at `166baa1` → `?? tests/fixtures/__pycache__/`, `?? tools/__pycache__/` (untouched).
- Wrote exactly two files, both under `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/`. No `git` mutation, no `jj`, no `rm`/`mv`, no signals, no `agent://all`, no write outside the lane. No scratch directory was created (`/var/tmp/souji-r26-ScribeReportDraft/` never needed) — nothing to remove. Tool installs: **none** (no pacman/uv/npx/cargo/npm); lane Python ran as `python3 -B` only.

## Findings

1. **Delivery collision, benign.** The L1 committed this draft at `166baa1` while the drafting seat was still refining it; the committed bytes are the draft plus the seat's earlier fixes, and the remaining delta is two wording hunks (`verify=ok` phrasing; checklist item (a) naming the counters). Location: `.ufo/waves/round-26/w1/report-draft.md`.
2. **C1 after-receipt is not at the landing tip — open.** `c1-after.tsv` is bound to `rev=07f83e6` while the prereg requires the K1 after value "run at the landing tip in a clean tree"; SCORECARD changed at `166baa1`. Location: `census/round-26/records/c1-after.tsv`.
3. **C2 declared receipts — closed at `9a6e0f1`.** `c2-gate.tsv` and `c2-k4-after.tsv` (named by the C2 RECEIPTS block) were absent at `0c92c2e` and are present at `166baa1`, both bound to rev `33e6807`; only the tip re-bind remains.
4. **Lesson named a deleted receipt — closed at `166baa1`.** `c3-control.tsv` was removed at `0c92c2e` (control is fixture case 12) and `corpus/lessons/round-26.md` `## Receipts` no longer names it. Location: `corpus/lessons/round-26.md`.
5. **QUALITY Q59 — closed at `166baa1`.** `corpus/QUALITY.md:143` carries Q59 (axis/surface-class consistency, instrument-checked) and the R26-M1 mistakes row landed in the same commit.
6. **Round 26 documentation tail — open.** No `## Round 26` section in `corpus/README.md` and no Round 26 entry in `LOG.md` at `166baa1`; SHONEN box 2 depends on the LOG entry. Location: `corpus/README.md`, `LOG.md:1723`.
7. **Fixture case-count history.** The frozen set is 12 cases; the first landed fixture (`0833de9`) was 11 and `c5949013` adopted 12. The report must state the chronology rather than only `12/12`. Location: `tests/fixtures/r26-axis-check.py` history.
8. **Lane hygiene residue.** Untracked `tests/fixtures/__pycache__/` and `tools/__pycache__/` at `166baa1`; left untouched (not this seat's to remove).

## Attack log

- **A1 — frozen red-before revision is unsatisfiable as written (substantiated).** C1's control names `--rev 0eca7c8… --label census/round-26/c1-counter.sh`, but `git ls-tree 0eca7c8 census/round-26/` is empty; the counter first exists at `12fd90b`. Executed receipts therefore use `rev=12fd90b` (C1) and `89e0fce` (C2/C3). Not a predicate violation: `SCORECARD.md` blob `4b564bc628d40328d276476c4171c30817cd6e75` and `corpus/SOURCES.md` blob `f3cffccdb15be2b8ead6cf19fda8c8a8adc145d7` are each identical at base and at their receipt rev, so both readings are semantically at base. The report must disclose the executed rev plus blob identity and must not phrase the red arm as "run at 0eca7c8". Q58/R25-M1 class.
- **A2 — C1 is passable on K2 alone.** K2 checks heading order only; amendment 2's seven byte-content spans are the real guard. Omitting the span-diff annex would admit drift inside protected spans.
- **A3 — C3 can self-satisfy.** K1 is the checker run on its author's own prereg; only fixture case 1 (r25-C2 replica flagged on its frozen operability axis) and case 12 (always-green stub rejected) discriminate a weakened checker. Both must be shown at the tip.
