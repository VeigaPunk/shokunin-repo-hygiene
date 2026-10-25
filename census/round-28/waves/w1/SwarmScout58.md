## Status
STATUS: PASS — read-only inventory of dirty `.ufo/waves` paths complete; TSV delivered at `.ufo/waves/round-28/w1/r26-leftovers-inventory.tsv` (intended location `census/round-28/records/r26-leftovers-inventory.tsv`; placed in my report dir per read-only seat bounds, for L1 to move).

## Evidence
- Frozen contract read first: `census/round-28/records/preregistration.txt` (C1/C2/C3 frozen at base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`).
- Snapshot A (15:46, plain `git status --porcelain=v1 --untracked-files=all | grep '.ufo/waves/'`): 169 lines (11 ` M`, 158 `??`).
- Snapshot B (~15:50, ground truth: physical walk of `.ufo/waves/` + `git ls-files` tracked set + plain porcelain for modified-tracked): 334 dirty rows. Breakdown: `a`=11, `b`=182, `c`=123, `d`=18. Dirty bytes total 2,622,970.
- `du -sh` per round dir: round-26 `19M` (15,764,397 B, 1383 files), round-27 `1.5M` (1,264,538 B, 123 files), round-28 `292K` (260,867 B, 19 files).
- `git rev-parse HEAD` now `0c96332932e66bbaf9cf1c246091d3275a0ab612` (master moved from frozen base during run).
- `.gitignore` tail now contains `.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/` (C3 mid-run state); `git check-ignore -v .ufo/waves/round-26/w1-results.json` → `.gitignore:1:.ufo/waves/`.
- Foreign-lane scan: zero basenames matching tsukuroi/kasegi/tower tokens; all dirty paths are under the lane's own `.ufo/waves/`.

## Findings
1. (a) Tracked-modified round-26 w1 — exactly 11 files, 151,271 B: `CritAmendNeed.md`, `ExecLandingCheck.md`, `LabGitVersion.md`, `ScribeQ58Note.md`, `SimpCounterCheck.md`, `landing-check.md`, `q58-note.md`, `report-draft.md`, `results-count.py`, `shonen-lines.md`, `verify-loop.sh` (all under `.ufo/waves/round-26/w1/`). Matches the named 11.
2. (b) Untracked round-26 — 182 files, 966,764 B: 28 files in `round-26/w1/` + `w1-results.json`; the remainder (153) are round-26 assimilation test fixtures under `round-26/assimilation/validate/tests/` (nested `categorygit` trees and vault fixtures), untracked and never committed.
3. (c) Untracked round-27 — 123 files, 1,264,538 B: `round-27/w1/` seat reports + `w1-results.json`, `w1-spec.json`, `w1-dispatch.json`, `w1-run.err`, `w1-validate.{out,err}`, `w1.ready[.dispatched]`, `preregistration.txt`, `census-before.txt`, `make-spec-r27.py`, `records/c{1,2,3}-before*`, `records/c1-base-findings.out`, `assimilation/{collisions,quarantine-slice,reg-ids,staged-ids}`.
4. (d) Other rounds — 18 files, 240,397 B: all round-28 current-work wave files (w1 dispatch/spec/ready/run.err, peer seat reports `SwarmExecutor03/07/11.md`, `SwarmScout55.md`, `swarm-registry.json`, `slice-verdicts.tsv`, `quarantine-slice.tsv`, `origin-record-{exclusivity,durability}-r28.md`, `snapshots/{open,rename,fsync}.html`, and my `r26-leftovers-inventory.tsv`). No round-24/25 dirty paths.
5. Snapshot instability: Snapshot A (172 rows) vs B (334) differ because concurrent seats wrote during the run (round-28 wave dir grew 9→19 files; round-26 `validate/tests` fixture tree appeared). Plain porcelain now reports only the 11 tracked-modified because `.ufo/waves/` is ignored; the untracked classes were recovered via `--ignored=matching` expansion + physical walk.

## Attack log
None — no counter/predicate/target/case-set changes proposed. The HEAD move (base `3a2a80d` → `0c96332`) and ignore-file state are observed mid-run facts, not counter disputes.
