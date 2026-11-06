# S69Connector — Sibling Overlap & Cross-Claim Scan Report
- **Mandate**: Sibling-overlap and cross-claim scan for round 69 (read-only).
- **Commands**:
  1. `python3 -c "import os,subprocess; ... rg -n --glob '!.git' <surface> <sibling_dirs>"`
  2. `diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' records/c2-clean.txt) <(... records/c2-ambient.txt)`
  3. `awk -F'\t' 'NR>1{print $5}' records/declared-coverage.tsv | sort | uniq -c`
- **Item 1 (Sibling Overlap Scan — 479 hits across 20 sibling repos, 0 contested)**:
  * `souji-receipt-write`: 3 hits (kaidoku:3; reference as fleet durability model; `kaidoku-shokunin/corpus/lessons/round-96.md:159`).
  * `status.showUntrackedFiles`: 2 hits (kengaku:2; git-status doc snapshot; `kengaku-shokunin/corpus/evidence/round78/sources/git-status.html:2364`).
  * `index.lock`: 32 hits (game-dev-3d:15, kasegi:5, mori:4, scripts:4, kengaku:2, kaidoku:1, tameshi:1; hygiene/locking checks; 0 contested).
  * `GIT_COMMON_DIR`: 54 hits (kengaku:29, kumitate:9, mori:7, kaidoku:2, kotodama:2, kake:1, kotoba:1, mado:1, tameshi:1, tsukuroi:1; drop/scrub lists vs souji value-check; 0 contested).
  * `fsmonitor`: 71 hits (kengaku:30, mori:22, tsukuroi:11, tabi:6, kaidoku:1, kama:1; `core.fsmonitor=false` plumbing flag/doc; 0 contested).
  * `GIT_OPTIONAL_LOCKS`: 260 hits (mado:70, kotodama:58, tabi:42, tsukuroi:27, mori:20, kumitate:16, kaidoku:10, kotoba:7, tameshi:4, kengaku:3, kama:2, kagi:1; read-hygiene; 0 contested).
  * `receipt writer`: 57 hits (kaidoku:33, kotodama:19, audio:5; lane-local writers/lessons; 0 contested).
  * **Verdict**: PASS (no sibling contests souji's writer, battery, or declared protections).
- **Item 2 (Cross-Claim Dependency Mapping)**:
  * **Shared Instruments**:
    - `c1-counter.py`: shared by C1 (battery engine) & C2 (`clean_env`, selftest). Modifying evaluation or scrub logic flips C1/C2.
    - `c1-matrix.tsv`: shared by C1 (47 rows, 3 base forgeries) & C2 (clean/ambient diff). Row edits alter C1 counts and C2 output.
    - `tools/souji-receipt-write.py`: candidate writer under test in both C1 and C2.
    - `battery-manifest.tsv` & `battery/`: shared between C1 & C3; mutant behavior directly decides C1 kills and C3 coverage rows.
    - `records/c1-after-battery.txt`: output of C1; cited directly by C3 `declared-coverage.tsv` col 6 evidence pointers.
  * **Verdict changes if file changed**:
    - Changing `battery-manifest.tsv` or any `battery/*.py` mutates C1 `BATTERY` outcome split and invalidates C3 `declared-coverage.tsv`.
    - Changing `c1-counter.py`'s `clean_env()` flips C2 ambient diff from 0 to >0 (`controls/c2-do-nothing-ambient.txt` EXIT=1).
  * **Verdict**: PASS (cross-claim dependencies mapped; no unhandled shared-instrument leaks).
- **Item 3 (Observed Decision Lines)**:
  * C1: `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, EXIT=0 (`records/c1-after-battery.txt:2529`).
  * C2: `diff` of 50 `^(CASE|SUMMARY|REGRESS|EXIT=)` lines between clean and ambient yields 0 diffs, EXIT=0 (`records/c2-clean.txt`, `records/c2-ambient.txt`).
  * C3: `12 mutant` and `2 limit` (`records/declared-coverage.tsv:2-15`, `battery-limits.tsv:2-3`).
- **Findings**:
  * [LOW] D29 `:(top)` mutant survives as named limit because `_index_stages(top)` runs from `-C top`, rendering `:(top)` redundant; resolvable in round 70 by invoking from subdirectory `root`.
  * [LOW] `tools/souji-receipt-write.py:git()` does not scrub `GIT_TRACE*` variables, unlike `c1-counter.py:clean_env()`.
- **Files written in seat directory** (`.ufo/waves/round-69/w1/S69Connector/`):
  1. `sibling-overlap-table.tsv` (479 rows: surface, path:line, lane, contested, reason, snippet)
  2. `claim-dependencies.tsv` (23 rows: claim, file, dependency role, evidence pointer)
  3. `proposal-non-obvious-move.md` (bounded round-70 proposal to close D29 limit and align trace scrubbing)
- **Report path**: `.ufo/waves/round-69/w1/S69Connector.md`