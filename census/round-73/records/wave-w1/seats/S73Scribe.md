# S73Scribe — r73 corpus text: SOURCES S315/S316 + knowledge r73 section

Verdict: draft delivered; census validate **EXIT=0** on the committed registry with the two rows
appended (86 pre-existing W04, zero E codes). Every C1/C2 number I cite was **re-read from the
committed receipts and re-counted from `census/round-73/c1-matrix.tsv`** — this seat ran no counter
and no writer, so these are receipt facts, not execution evidence of mine.

Commands (lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`):
- quote locator over `census/round-73/srcs/*.txt` → S315 q1 offset **1435** (25 words), q2 **3539**
  (16); S316 q1 **2258** (18), q2 **3056** (15); `ALL_OK True`
- `curl -sS … racy-git.adoc` → `HTTP 200 bytes 9121`, sha256 `f661ed2d…b84ad` (= capture);
  `curl -sS … git-hash-object` → `HTTP 200 bytes 29933`, sha256 `b7e8f953…eb798` (= capture)
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <scratch>/corpus/SOURCES.md --today 2026-11-06`
  → `EXIT=0`, `file ok …`, 86 W04, no E
- same validate against the working-tree registry + my rows → `EXIT=1`, `E03 S315 duplicate id`,
  `E03 S316 duplicate id`
- `grep -E '^(SUMMARY|EXIT=)' census/round-73/records/c1-after.txt` → `matrix=80 base_forgeries=15
  base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0
  new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`; K-a
  `new_forgeries=3` EXIT=1; K-b `new_honest=0` EXIT=1; K-c `new_forgeries=15` EXIT=1; writer
  `SELFTEST cases=44 pass=44 fail=0`; counter `cases=52 pass=52 fail=0`; D1..D5 `base_unwitnessed=1`
  with `base_witness=no` on FWr/FWi/FWp/FWs/FC3; before receipts `base_forgeries=12` EXIT=0
- `awk` over the matrix → `rows=80 accept=21 refuse=59 base_expect_accept=36`

Evidence: `tools/souji-receipt-write.py:262` (`_truth_refusal`), `:610` pre-run, `:735` post-run,
`:742-744` instrument re-compare; `census/round-73/c1-counter.py:1063` (`tree_divergence`), `:1414`
(fail-closed witness), `:1483` (`claim_upheld`), `:1503` (classifier); `probes/fx-index-stat.txt`
3/3 FORGERY on both slots; `probes/fx-honest.txt` FXc `raw_equal=false`.

Findings:
- **MEDIUM** — the lane working tree already carries an uncommitted S315/S316 pair (mtime 19:15:51,
  not written by this seat) whose S316 anchors OPTIONS `--no-filters` at offset 3431 and whose S315
  anchors only the 3539 sentence; appending this seat's rows gives E03 for both ids. Only one pair
  can land, and the `source:` header line must name the S316 scope that lands (this draft follows the
  seat spec: DESCRIPTION).
- **LOW** — the 26-word racy-git sentence at offset 3374 ("the cached stat information the index entry
  records still exactly match …") exceeds the 25-word cap; the 1435 sentence carries the same claim
  at exactly 25 words.
- **LOW** — `census/round-73/records/m2-guard-canfail.txt` and `corpus/lessons/round-73.md` are
  untracked in the lane; not mine, not used as evidence.

Files written (all under `.ufo/waves/round-73/w1/S73Scribe/`): `sources-rows.md`,
`knowledge-r73.md`, `census-validate.txt`; this report at `.ufo/waves/round-73/w1/S73Scribe.md`.
No lane file edited, no commit, no tool installs; scratch `/fast/scratch/hyaku/souji-r73/S73Scribe`
and the two re-fetched copies removed.
