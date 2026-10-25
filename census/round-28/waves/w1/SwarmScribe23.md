## Status
STATUS: PASS — delivered `census/round-28/records/log-entry-draft.md` (round-28 LOG.md entry draft, append-only style from prior rounds) using only pre-integration facts; all post-integration numbers marked `[AFTER]`. No writes outside the named delivery file and this report.

## Evidence
- `census/round-28/records/preregistration.txt` (lines 1–9 raw): frozen C1/C2/C3 claim text, counters, kill rules; base `3a2a80d0d18940a5e352ebc526da22a57dad83c4`, branch master, ahead=0, remote verified.
- Read-only git (`git status/log/branch/rev-parse`): control tip `0c96332` "round-28: frozen preregistration + before receipts + do-nothing controls" on master, `origin/master` = `0c96332`; HEAD detached at that commit.
- Before receipts (opened bytes): `c1-before.tsv` (findings=2, checked_reg=52, c1_rc=2), `c2-before.tsv` (grounded_f4=4, rows=135), `c3-before.tsv` (dirty_waves=163, manifests_26/27=absent), `axis-check-before.txt` (claims=3 flags=0 axis_rc=0).
- Independent verification: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 135; `grep -cE '^ground: F4' corpus/knowledge/*.md` → 4 (r33/r27/r24/r23 entries); `test -f tools/souji-wave-evidence-capture.sh` → absent; `test -f tests/fixtures/r28-wave-evidence-capture.sh` → absent; `.gitignore` absent; staged packages `origin-record-exclusivity-r28.md` / `origin-record-durability-r28.md` confirmed under `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/`.
- `LOG.md` (lines 1627–1750): round-24/25/27 entry style and residuals (r26 leftovers = 36 files, r27 attempt-2 C1 stop).
- Wave shape: `.ufo/waves/round-28/w1-spec.json` — wave `souji-r28-w1`, 64 items, reportDir `.ufo/waves/round-28/w1`, dispatched (`w1.ready.dispatched`, `w1-dispatch.json`).

## Findings
1. The frozen base and the current control tip differ by design: `3a2a80d` (frozen preregistration base) vs `0c96332` (control snapshot adding preregistration + before receipts). The draft cites both.
2. Every before-counter in my draft matches bytes I opened this run (c1/c2/c3-before.tsv) and the frozen contract text; no counter is challenged.
3. Am3 artifacts (capture tool, fixture, .gitignore) are absent at base, confirming the C3 surface is net-new; r26 wave dirty files are present in the working tree (163 paths) and are the C3 leftover target.
4. S119 zh-Hans `git-fetch(1)` edition is routed staged; C2's decision-time pin determines admit (S215) or kept-staged — recorded as a conditional in the draft, not asserted.
5. Delivered at the assignment-named path `census/round-28/records/log-entry-draft.md` (lane-relative), matching prior-round records convention; report at `.ufo/waves/round-28/w1/SwarmScribe23.md`.

## Attack log
None — scribe item; no predicate, target, counter, or case set challenged.
