# S56connector01 — scoped findings (souji round 56, w1)

Read-only sibling-overlap scan at measured revision `cce21b555a617cadda782613ec1e9d3a0c12ac83`
(base `fafe3716…`). Frozen pins verified; no sibling tool executed. Full report:
`.ufo/waves/round-56/w1/S56connector01/S56connector01-report.md`.

## S1 class (splitlines vs LF)

| tool | present | mechanism | unit | scope | overlap with souji v5 |
|---|---|---|---|---|---|
| kaidoku `tools/round-59/annotation-audit.py` (`ba9ccbb9…`) | yes — `text.splitlines()` `:116` over `git show` bytes decoded `errors="replace"` `:220`; `strip()` `:114` | splitlines breaks on `\x0b \x0c \x1c-\x1e \x85 \u2028 \u2029`; a FF inside a `$` command splits it and can turn a valid probe into `COMMAND_UNREEXECUTABLE` | receipt-local lines: `$` command / integer output / `(base: N -> record: M)` | one receipt at one revision; re-derive via `git show\|lstree` + `grep -c` | **mechanism only**; unit and scope differ; no fence/comment/NUL/numstat grammar |
| chousa `corpus/evidence/round50/stale-count-check.py` (`4273436a…`) | yes — `splitlines()` at `:26` (receipt rows) and `:69` (prose); `NAMES` `:22` + `nums[k-1]` `:40` resolve `LOG.md:1803` as a splitlines index | a FF/VT/NEL before a named line shifts the index to a different physical line (same arithmetic as souji v3 S1 / F7-FF2) | count phrases (`QUOTES=n`, `n-row manifest`, `n located quotes`, `CAPTURE_BOUND=n/n`) vs `spans.tsv` data rows | its `PROSE` set includes `LOG.md` + `corpus/README.md` + QUALITY + lesson 49; `spans.tsv` | **mechanism only, file-scope name overlap**; different unit and grammar (`correction: … superseded by`, not `R5x-CORRECTION` + arrow pair) |

Liveness: no `[\x0b\x0c]` / `\xc2\x85` bytes in the kaidoku round-58/59 demo receipts or chousa's
prose + `spans.tsv`; `splitlines` count == LF count on all eight inputs. Class latent, not live.

## Overlap count (same unit + same grammar): N = 7

| tier | file(s) | overlap |
|---|---|---|
| exact r56 F27 disposition | kaidoku `tools/round-61/numstat-edge-audit.py` (`6b967e20`, `parse_numstat` `:151–163`, `NUMSTAT_BINARY` `:120`) | numstat per path between revs; binary `-` refused by name; uses `splitlines()` |
| same unit+grammar, different comparison | kama `tools/append-only-audit.py` (`2b9285bf`, `:465–473`), `round47-…-v2-check.py` (`a180ab84`, `:189–197`), `round48-…-v3-check.py` (`92b0f9f1`, `:324–334`), `round50-…-v5-check.py` (`925f07a4`, `:472–476`), `round51-…-v6-check.py` (`254e63ba`, `:306–311`), `round52-append-restore-check.py` (`29dfd886`, `:263–268`) | same `git diff --numstat` three-column grammar and deletion unit; binary skipped/recorded/unnamed |

Not counted: kaidoku `round-43/c2-score-r43.py:170–194` (exact numstat string for
`corpus/SOURCES.md`, outside C1's monitored path set); `round-44/c2-rubric.json` (mention only);
kama `__pycache__` artifacts. **C2 overlaps: 0** — no sibling parses `# KEY=VALUE` text receipts or
`RECEIPT_VERSION`; tameshi/kama/kaidoku receipt validators are JSON-key schemas (different grammar).
Finding-name collisions in siblings: 0 for all five r56 names.

Structural near-overlaps not counted: chousa `research-gate.sh:820–860` tracks HTML-comment state
with the **v4 loose opener** (`*'<!--'*` anywhere) — the F29 over-hide shape, but its unit is
section/heading state; tsukuroi `check-adjacency-overlap.py:178` / `check-boundary-contract.py:54` /
`check-edit-contract.py:68` / `check-owed-statements-r29.py:152–153` strip comments in their own
decision/statement docs.

## PTR / PAIR scope

v5 reads only `PAIR_SITES = ['LOG.md', 'corpus/README.md']` (`c1-counter.py:162`), `git show`
(`:442–447`), PTR-exempt on a `file.ext:NN` token (`:160`, `:450`). Sibling LOG-style pair filings
invisible: **27 lines in 14 lanes** (chousa 827; game-dev-2d 1353; kagi 1001; kaidoku 3190/3205/
3268/3357; kake 2459; kama 2289/2427; kasegi 1667/1745/1790/1905/2570; kotoba 2322/2325/2352/
2371/2928; kumitate README 94/96; mori 3262; revenger 1007; tabi 487; tameshi 1880; tsukuroi 389).
**None is a live souji surface** (all outside the two site files). Souji's sites hold 13 matching
lines; 0 mention a sibling lane. Fleet root `LOG.md`: 0; fleet `SCORECARD.md`: 1 (line 27) but not a
`PAIR_SITE`. Risk: 7 of the 27 are non-registry same-value pairs, so the shape-only predicate would
over-read if ever pointed cross-lane; a sibling pair quoted into souji's sites without a pointer would
be audited as a souji annotation (none exists at this revision).

## Bounded move

Record F27 as a **lane-local naming closure** in the r56 report/lesson (never in frozen or
claim-receipt bytes): `DELETIONS-UNREADABLE-BINARY` names souji's r55 mislabel; kaidoku round-61
already refuses binary as `NUMSTAT_BINARY`, and six kama instruments parse the same grammar. Route one
r57 item on whether the numstat binary/LF-only predicate becomes shared or stays duplicated.
Axes: calibration 7 (scoping only), coverage 8 (unchanged); nothing falsifies T1–T8/T1–T7.

VERDICT: OVERLAP-FOUND
