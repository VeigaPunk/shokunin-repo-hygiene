# S75Connector — r75 C1/C2 causal separation + sibling overlap (read-only; lane tip 5d10e09e, master)
## 1. C1/C2 causal separation — SEPARABLE
- C1 receipt header columns bind only C1 bytes (recomputed with `git show <rev>:<path> | sha256sum`): counter 9ed4a97b, population 85257260, gate 620ed97e(W)/062b6d39(base K-a)/e0d2e149(K-b variant), writer 70bbf1c2, probe 09e18d8a — all equal the receipt `# bind`/`instrument_sha256` values.
- No C1 receipt reads a C2 byte: `grep -nE 'census/round-75/(c1-counter|c2-kill|c2-mutants)|records/variants/r(74|75)-' census/round-75/records/c1-after.txt census/round-75/controls/c1-K-*.txt` → none. No C2 receipt reads a gate/writer byte: same grep for `pre-report-gate|controls/variants/gate|souji-receipt-write` over records/c2-*.txt, controls/c2-*.txt → none; c1-counter.py, its variants and r60 fixture contain 0 gate refs.
- The writer is consumed by both but pinned to different revisions, so no shared mutable byte: C1 uses W blob 70bbf1c2; C2 reads `git_show(base_rev 8b9345b1, BASE_REL)` = 118597e0 (census/round-75/c1-counter.py:1793,1995). `git diff --stat 52d3f07d 5d10e09e -- tools/` = gate only (+18); writer unchanged by every r75 commit.
- C2 re-derived from committed receipts: `python3 -B census/round-75/c2-kill-counter.py --pristine census/round-75/records/c2-after-pristine-selftest.txt --mutant X09=…c2-after-X09-selftest.txt --mutant P1=… --mutant M08=… --mutant M14=… --mutant M15=… --mutant M17=…` → X09/P1/M08/M14 fail=1, M15/M17 fail=2, PRISTINE fail=0; `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS` EXIT=0. Same tool on controls/c2-before-r74-*+r74 receipts → killed=4, X09+P1 SURVIVED, EXIT=1; r75 pristine SELFTEST cases=64 pass=64 fail=0, before pristine 62/62.
- r74→r75 counter diff (`diff -u` of committed blobs) = 3 hunks, all at lines ≥2005 inside selftest (1748-2189); evaluate() at :1422 untouched — "no evaluate()/verdict code change" holds. C1: 25 ROW lines, population 25 routes; K-a mismatches=2 [f-info-exclude f5-info-exclude-dir], K-b mismatches=3 [f2 f6 f7] — match the frozen text.
- LOW: C2 receipts bind no sha for census/round-73/c1-matrix.tsv (only the path in `command=`); the matrix is unchanged base..tip so the kill numbers hold, but the receipts cannot prove its bytes.
## 2. Lane tools deciding "nothing uncommitted" from status (ignored excluded)
| file:line | decision | info/exclude-hidden file changes verdict? |
|---|---|---|
| tools/souji-pre-report-gate.sh:61 + :98 | check-clean | NO at tip (W block closes info/exclude+core.excludesFile); YES at base 52d3f07d |
| tools/souji-receipt-write.py:603, :715-724, _status_z:360 | dirty refusal + in-run compare | YES (neither the refusal nor the in-run compare sees it) |
| tools/souji-record-agreement.py:351 (K4) | uncommitted-path mismatch | YES (path omitted → PASS) |
| tools/souji-verify.sh:377,421,883; tools/souji-guard.r9-s18.sh:286; tools/souji-quarantine.sh:1198,1633 | removal verdict | NO (verdict NOT-SAFE either way; :1633 before/after sentinel blind) |
| tools/souji-verify.sh:713; tools/souji-guard.r9-s18.sh:153; tools/souji-quarantine.sh:1037 | same | NO (--ignored=matching) |
| tools/souji-idx-repair.py:145,253,275 | plumbing-repair verdict | NO (untracked-ignored outside its row class) |
| tools/souji-census.sh:1249; souji-landing-gate.py/gate-check.py/report-contract.py/freeze-check.py | census metric / no status read | NO / N/A |
## 3. Sibling pre-report/landing gates with a status-based cleanliness verdict
| lane | file:line | vulnerable |
|---|---|---|
| kama | tools/pre-report-gate.py:666 (round-clean arm, wave dir only) | YES |
| kaidoku | tools/round-29/prefile-check.sh:22; tools/round-42/prefile-gate.py:273 (:288 ignored listing warns, exit-neutral); tools/round-45/frozen-path-preflight.py:137; tools/round-46/gate.py:134 | YES ×4 |
| kumitate | scripts/round-gate.mjs:559 (--close TREE_DIRTY) | YES |
| mori | tools/mori-unlanded-check.py:58 (ignored deliberately out of scope) | YES |
| kengaku | plans/receipt_consistency_check.py:153 | YES |
| tabi | scripts/check-selfassessment.mjs:482 | YES |
| mado | quality/check-evidence-pointers.py:177 | YES |
| kasegi | corpus/instruments/r46-landing-gate.py:113 (historical instrument) | YES |
| kotoba | verifiers/check_r86_routed_repairs_v3.py:599 | YES |
| mori | tools/mori-pin-check.py:1588,1617; mado quality/landing-counters.sh:271 (--ignored) | NO |
| others | chousa/tsukuroi/tameshi/kagi/kotodama/lore/revenger/kake/audio/game-dev-2d/3d: no status-based pre-report cleanliness read; fleet scripts/hyaku/jj-lane.sh:179 = state display, inline.sh:172 = WARN only | N/A |
## Findings
- MEDIUM: 12 sites in 9 sibling lanes still decide "clean" from plain `git status --porcelain` and accept info/exclude-hidden content; fleet grep shows no sibling carries the `--exclude-per-directory` fix (souji gate only). Closest pre-report gate: kama:666; landing path: kumitate:559.
- LOW: the gate's own byte-truth helper, and the tool behind every receipt, still accepts a tree carrying info/exclude-hidden content (tools/souji-receipt-write.py:603); W fixes only the gate's clean verdict, not receipt producers.
- LOW: gate:98 treats ANY per-directory .gitignore as policy, not strictly the f7 self-ignoring .jj/.ruff_cache shape: an untracked .gitignore invisible to status (e.g. matched by a committed rule) can hide payload and still PASS — marginal extension of the stated limit (S319 semantics inference; not observed in-lane).
- LOW: no committed domain-trial receipt although the prereg pins check-clean=PASS at the report tip. At read time the lane has `M corpus/SOURCES.md`, `M corpus/knowledge/filter-filemode-witness.md`, so the trial is red by construction; sibling .ufo/waves/round-75/w1/S75ExecC1.md:8 recorded the same mid-wave FAIL. Falsifiable only at the L1's report-tip commit.
Files written: .ufo/waves/round-75/w1/S75Connector.md (this file); no other seat-dir file. Scratch /fast/scratch/hyaku/souji-r75/S75Connector used only for the two counter blobs and removed.
