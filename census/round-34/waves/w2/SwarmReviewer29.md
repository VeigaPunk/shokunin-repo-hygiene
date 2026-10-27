# SwarmReviewer29 — round-34 w2, AttackC2J1Timeout (seat report)

Target: falsify the W1 finding on the C2 J1 timeout — test cost, deadlock, or real missed failure? Full evidence: `.ufo/waves/round-34/w2/AttackC2J1Timeout.md`.

## Status

**CONFIRMED, classification settled:** real instrument defect — self-recursion starvation, **not** test cost, **not** deadlock, **not** a missed stub failure. Frozen bytes verified (`cmp` of both files vs blobs at 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 → identical).

## Findings

1. **Structural starvation, not cost/load (HIGH).** `c2-counter.py:287-288` discards the J1 leg argv and re-invokes the real `tests/fixtures/r34-sandbox-junk.py` from `--root`; the fixture's stub legs keep a J1 junk row (`r34-sandbox-junk.py:105`) and the clone retains the real fixture, so every inner reading re-enters. Budget tie: fixture window 900 s hardcoded (`r34-sandbox-junk.py:119`) == inner counter's default junk-leg wait 900 s (`c2-counter.py:265`) with positive per-level work ⇒ the fixture always times out first, at every level, any host speed. Falsifies SwarmSentinel37 #7's "budgeted below its own cost / host load 43-54" reading — the control's real work is **13.4 s measured**; the rest is dead recursion wait. G3's junk-row-required rule (`c2-counter.py:62-63`) makes the re-entry unavoidable in every compliant legs set.
2. **Five stubs ARE rejected — timeout masked a would-be PASS (REPRODUCED, bounded probe B).** With the recursion alone neutralized by a disclosed scratch-local leaf fixture, the frozen counter bytes FAIL all five stubs in 13.4 s: W1/W3/W4/N3 `work witness failed creates=0/0 target=False`, W2 `CASE=0` vs `SUMMARY total=12`. The fixture's assertion inputs (five stub ids among FAIL rows, rc≠0) would yield `cases=5 pass=5 control=STUB-REJECTED` (derived from verified output + `r34-sandbox-junk.py:121-132`; the end-to-end print with the real fixture was intentionally not repeated — that is the oversized run). Every committed J1 FAIL is fail-by-exception; no prior record established the stub verdicts.
3. **Not a deadlock.** Per-level flocks sit on distinct nested lock files; processes progress (w1's committed 12-deep `r34-junk.*/inner` chain; probe B completes levels in seconds). No wait cycle.
4. **Direct-child-only timeout kills orphan deeper levels (LOW, operational).** Each timed-out `subprocess.run` kills only its child; deeper levels run out their own 900 s windows — explains w1's 30-55 post-run load receipts and the "host load" attributions. No orphans live at this seat's start or end (`pgrep` clean).
5. **No structured failure receipt (corroborates w1 SwarmReviewer27).** `r34-sandbox-junk.py:117-119` lacks a `TimeoutExpired` handler; traceback, rc 1, no `cases=` line — and the discarded pipe output held the five-stub verdicts.

## Evidence (summary)

- Source: `c2-counter.py:56-63,265,287-288`; `r34-sandbox-junk.py:28,105,117-132`; `c2-legs.tsv:40`; prereg `:59-66,90-93`.
- Committed: `records/junk-c2-final.txt:22` (900 s TimeoutExpired); w1 `deliver-c2-j1guards.txt` §2-§3 (J1 FAIL line, marker proof, 12-deep chain, load 36.69 after); `records/controls.txt` ("no pass is claimed").
- Probe B (only execution performed; read-only on lane): driver `/fast/scratch/hyaku/souji-r34/AttackC2J1Timeout/probe_b.py`; stub clone at scratch, stub rev `1293440fad0f518d0bd851354d539b2cc75125ea`, base tip `adac8bbc79a7ed77b632b309e70fd2a91b45dbd9`; `SUMMARY legs=12 pass=7 fail=5 harm=0` rc=1 in 13.4 s, load 2.30→5.82. Verbatim LEG lines in the full report. Scratch cleaned to 8 KB; no oversized run repeated.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2J1Timeout.md` (full evidence, attack log, residual gaps)
- `.ufo/waves/round-34/w2/SwarmReviewer29.md` (this file)
