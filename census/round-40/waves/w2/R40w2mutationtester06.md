# R40w2mutationtester06 — C2 fixture mutation probe

**Attack:** `tests/fixtures/r40-docstring-joined.py` must reject an analyzer that uses the one-line reading, drops the last class, or returns an empty class map. Frozen C2 claim is `census/round-40/preregistration.txt:7-8` (specifically it requires the joined analyzer to detect the synthetic wrapped trigger and verify frozen class/trigger pairs).

**Landed revision:** `128e412b0ced3c243dc27c3dd3332054a611bc2e` (confirmed with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show --stat 128e412b0ced3c243dc27c3dd3332054a611bc2e`). Target analyzer behavior is at `census/round-40/docstring-classes.py:73-84`, particularly `class_entries` at 73-75 and `classes_from_source` at 83-84. Fixture attacks/checks are `tests/fixtures/r40-docstring-joined.py:64-94`: synthetic joined vs primary comparisons (64-72), frozen pair validation (73-78), and class-set comparison (88-94). Fixture mutation injection is via `--analyzer` at lines 98-116.

Scratch used: `/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester06`; `TMPDIR` was not needed. No tools installed. Each command below was run against the committed analyzer bytes extracted from the landed commit; the analyzer scratch file was overwritten for each run. Command form:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r40-docstring-joined.py --analyzer /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester06/analyzer.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py
```

Results (actual output):

* **Pristine** — analyzer SHA-256 `bc418a58e751a69f00d5d9c207d5c174f486e759418f52367eb7fe0a339105ba`:
  ```text
  case-synthetic-joined-has-trigger=PASS
  case-synthetic-primary-has-trigger=PASS
  case-synthetic-one-line-misses-trigger=PASS
  case-frozen-pairs-present=PASS
  case-outside-root-trigger-primary=PASS
  case-record-missing-eacces=PASS
  case-record-malformed-enoent=PASS
  case-class-sets-equal=PASS
  case-joined-not-shorter=PASS
  SUMMARY cases=9 pass=9 fail=0
  EXIT 0
  ```
* **One-line mutant** — changed `classes_from_source` at analyzer lines 83-84 to return `first_line_entries(docstring_of(source))`; SHA-256 `79f68a6c22a02c17c5bdcc0dc88a87421ef126fce0407de48fdf82ed3c02fa40`:
  ```text
  case-synthetic-joined-has-trigger=PASS
  case-synthetic-primary-has-trigger=PASS
  case-synthetic-one-line-misses-trigger=PASS
  case-frozen-pairs-present=PASS
  case-outside-root-trigger-primary=PASS
  case-record-missing-eacces=PASS
  case-record-malformed-enoent=PASS
  case-class-sets-equal=PASS
  case-joined-not-shorter=PASS
  SUMMARY cases=9 pass=9 fail=0
  EXIT 0
  ```
  **Survived.** The fixture calculates `primary` from `first_line`/`joined` directly at lines 53-58; `classes_from_source` is never called, so the requested one-line analyzer mutation is not observed. This is a vacuous case for the mutation target.
* **Drop-last-class mutant** — changed `class_entries` at line 75 to drop the last dictionary entry after `_entries(doc, True)`; SHA-256 `45b680541f26909b900ec27ec096e74122554be1a83005bea7915cfdffb56bdd`:
  ```text
  case-synthetic-joined-has-trigger=FAIL joined=None
  case-synthetic-primary-has-trigger=FAIL primary=None
  case-synthetic-one-line-misses-trigger=PASS
  case-frozen-pairs-present=PASS
  case-outside-root-trigger-primary=PASS
  case-record-missing-eacces=PASS
  case-record-malformed-enoent=PASS
  case-class-sets-equal=FAIL joined=['JSON-HARDLINKED', 'JSON-INSIDE-MEASURED-TREE', 'JSON-IS-RECORD', 'JSON-NOT-REGULAR', 'RECORD-EMPTY', 'RECORD-MALFORMED', 'RECORD-MISSING', 'RECORD-OUTSIDE-ROOT'] one_line=['JSON-HARDLINKED', 'JSON-INSIDE-MEASURED-TREE', 'JSON-IS-RECORD', 'JSON-NOT-REGULAR', 'JSON-UNWRITABLE', 'RECORD-EMPTY', 'RECORD-MALFORMED', 'RECORD-MISSING', 'RECORD-OUTSIDE-ROOT']
  case-joined-not-shorter=PASS
  SUMMARY cases=9 pass=6 fail=3
  EXIT 1
  ```
  **Killed** (nonzero exit).
* **Empty-map mutant** — changed `class_entries` at line 75 to return `{}`; SHA-256 `4939dca039f8259cf99c93d26d00c08f31b98de27fd58e4aa9ce6c40bf16db0`:
  ```text
  case-synthetic-joined-has-trigger=FAIL joined=None
  case-synthetic-primary-has-trigger=FAIL primary=None
  case-synthetic-one-line-misses-trigger=PASS
  case-frozen-pairs-present=FAIL missing=['RECORD-MALFORMED(ENOENT)', 'RECORD-MISSING(EACCES)', 'RECORD-OUTSIDE-ROOT(--root)']
  case-outside-root-trigger-primary=FAIL primary=None
  case-record-missing-eacces=FAIL primary=None
  case-record-malformed-enoent=FAIL primary=None
  case-class-sets-equal=FAIL joined=[] one_line=['JSON-HARDLINKED', 'JSON-INSIDE-MEASURED-TREE', 'JSON-IS-RECORD', 'JSON-NOT-REGULAR', 'JSON-UNWRITABLE', 'RECORD-EMPTY', 'RECORD-MALFORMED', 'RECORD-MISSING', 'RECORD-OUTSIDE-ROOT']
  case-joined-not-shorter=PASS
  SUMMARY cases=9 pass=2 fail=7
  EXIT 1
  ```
  **Killed** (nonzero exit).

Restore evidence: extracted the committed analyzer from `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/docstring-classes.py` and restored it at the lane analyzer path. Restored SHA-256 equals pristine: `bc418a58e751a69f00d5d9c207d5c174f486e759418f52367eb7fe0a339105ba` (3840 bytes). The scratch directory is removed before yield.

## Verdict: FALSIFIED

The fixture does fail for dropped-class and empty-map behavior, but the specifically required one-line analyzer mutant survives with all nine cases passing (exit 0). The fixture therefore cannot demonstrate that its joined-primary reading catches the wrapped-trigger defect when that defect is in `classes_from_source`, the analyzer's production entry point.
