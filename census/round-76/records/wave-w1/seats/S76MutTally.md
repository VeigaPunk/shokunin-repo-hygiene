# S76MutTally — C2 mutation test: tally 5 killed / 5 survived, counter 1 killed / 5 survived (2 HIGH)

Method: a tally resolves lane-relative receipts from its own `__file__`, so all mutants ran from a byte-identical mirror (`<scratch>/mirror/census/round-7{4,5,6}`); tally mutants were scored by the real `python3 -B census/round-76/c2-binding-counter.py --tally <abs mutant>` from the lane root, counter mutants by `--tally census/round-76/c2-kill-tally.py` (must read 10/0) and `--tally census/round-75/c2-kill-counter.py` (10/5).
Lane bytes untouched: c2-kill-tally `fcaaec1b…`, c2-binding-counter `e22f634e…`, c2-population `c46ea8ff…` before and after; `git status --short -- census tools .gitignore` empty.

## A. census/round-76/c2-kill-tally.py — 10 single-edit mutants (detector: c2-binding-counter.py; target 10/0)
T01 drop instrument-sha compare (:93) → mismatches=1 b-pristine-r74, KILLED only via the pristine path (F3); T02 drop ` --selftest` check (:95) → 10/0 SURVIVED (F4).
T03 drop duplicate-digest check (:128) → 10/0 SURVIVED, provably equivalent (F9); T04 take LAST `instrument_sha256=` line (:83) → 10/0 SURVIVED (F5).
T05 `e = exits[-1]` instead of all-agree (:82) → mismatches=1 b-exit-disagree KILLED; T06 UNBOUND→KILLED (:133) → mismatches=3 (b-swap-x09-gets-m08, b-swap-p1-gets-x09, b-unknown-id) KILLED.
T07 skip pristine binding (:141) → mismatches=1 b-pristine-r74 KILLED; T08 P1 derived M17 then X15 (:58) → 10/0 EQUIVALENT: both orders give sha `fc91b5b3…` = P1 receipt.
T09 ignore composites (:58) → mismatches=2 (h-honest, h-honest-reordered) KILLED; T10 drop `ids.count(mid) != 1` (:128) → 10/0 SURVIVED (F6).

## B. Killing-case probes (direct tally run, rc 0 = accept; forged receipts in scratch only)
P1 X09 with ` --selftest` stripped: pristine rc1 (`killed=5 unbound=1`) / T02 rc0 (`6/0`) ⇒ kills T02. P2 X09 + bogus first `instrument_sha256=` line: pristine rc1 (`5/1`) / T04 rc0 (`6/0`) ⇒ kills T04.
P3 X09 filed twice, two distinct valid receipts (8 rows, 7 mutants): pristine rc1 (`killed=5 unbound=3`) / T10 rc0 (`killed=8`) ⇒ kills T10. P4 X15 receipt under M14 (unique digest): pristine rc1, T03 rc1 ⇒ dedupe not the catcher.

## C. census/round-76/c2-binding-counter.py — 6 single-edit mutants (r76 10/0, r75 10/5 expected)
K01 accept rc=2 as reject (:64-65) → r76 10/0 rc0, r75 10/5 rc1, exit-equivalent (F10); K02 drop SUMMARY requirement (:65) → r76 10/0, r75 10/5 SURVIVED (F7).
K03 `ok = int(got) <= int(exp)` (:71) → r76 10/0 rc0, r75 10/0 rc0 SURVIVED-HIGH (F1); K04 skip `b-*` rows (:57) → r76 10/0 rc0 rows=5, r75 10/0 rc0 rows=5 SURVIVED-HIGH (F2).
K05 population → `c2-population-alt.tsv` (:42) → r76 10/1 rc1, r75 10/6 rc1 KILLED; K06 accept >1 SUMMARY (:65) → r76 10/0 rc0, r75 10/5 rc1 SURVIVED (F8).

## Findings
HIGH F1 (K03): the frozen do-nothing r75 control itself prints `SUMMARY cases=10 mismatches=0` EXIT=0 (`ROW b-swap-x09-gets-m08 expect=1 got=0 match=yes`) — the device cannot detect a counter that accepts every rejection.
HIGH F2 (K04): the same 0/0 on the r75 control, and `cases=10` is len(population), not rows executed — 5 `ROW` lines under a `cases=10` SUMMARY, so skipping any subset of cases is invisible to the frozen target line.
MEDIUM F4/F5 (T02/T04): no receipt lacks ` --selftest` or carries two `instrument_sha256=` lines; P1 (`b-no-selftest-X09`) and P2 (`b-two-sha-X09`) are the killing cases, accepted by the mutants and rejected by the real tally.
MEDIUM F6 (T10): no case repeats an id; P3 (`b-repeated-id-x09`) yields `killed=8/8` for 7 distinct mutants.
MEDIUM F7/F8 (K02/K06): no tally omits SUMMARY or prints two; a silent exit-0 tally (`u-silent-exit0`) matches under K02, a two-SUMMARY tally (`u-two-summary`, green first) passes under K06.
LOW F3 (T01): the sha compare is never the sole detector — b-pristine-r74 kills it via the shared `bind()` on the pristine receipt; b-swap forgeries are caught by digest dedupe. LOW F9 (T03): dedupe is unreachable while sha binding holds (distinct ids never share a derived sha; same-id repeats need `ids.count`) — redundant defence, no killing case. LOW F10 (K01): exit-equivalent for every input; only `got=`/`errors=` columns change.
Files: `.ufo/waves/round-76/w1/S76MutTally.md`; `.ufo/waves/round-76/w1/S76MutTally/` `tally-mutants.tsv`, `tally-scoring.txt`, `counter-mutants.tsv`, `counter-scoring.txt`, `probes.txt`, `composite-order.txt`.
