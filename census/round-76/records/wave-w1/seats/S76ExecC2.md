S76ExecC2 — C2 tally binding falsification
Verdict: C2 claim REPRODUCED exactly; ONE binding hole found (FALSE-GREEN).
Commands (cwd=souji-shokunin):
[1] python3 -B census/round-76/c2-binding-counter.py --tally census/round-76/c2-kill-tally.py → SUMMARY cases=10 mismatches=0 errors=0, exit 0. Matches records/c2-after.txt.
[2] same with census/round-75/c2-kill-counter.py → SUMMARY cases=10 mismatches=5 errors=0, exit 1; rows b-swap-x09-gets-m08, b-swap-p1-gets-x09, b-pristine-r74, b-unknown-id, b-exit-disagree all got=0 (no binding). Matches controls/c2-K-do-nothing-r75.txt.
[3] same with controls/variants/tally-K-b-reject-all.py → SUMMARY cases=10 mismatches=2 errors=0 ([h-honest, h-honest-reordered]), exit 1. Matches controls/c2-K-b-blanket-reject-all.txt. Blanket stays red: no false-green there.
[4] apply-edit.py recompute of each mutant onto census/round-75/c1-counter.py (X09, X15, M08, M14, M15, M17; P1=X15-then-M17):
    X09 0890321d… M08 6ae083b8… X15 54573344… M14 f92429d2… M15 0c355f3b… M17 bdc86901… P1 fc91b5b3…
    All 7 equal the instrument_sha256= lines in census/round-75/records/c2-after-*-selftest.txt and the sha256 of census/round-75/records/variants/r75-*-counter.py. Pristine 90a3c7b2… equals sha256(census/round-75/c1-counter.py). REPRODUCED (8/8).
    h-honest under r76 tally: killed=6 (ROW h-honest: SUMMARY mutants=6 killed=6 … pristine=PASS). REPRODUCED.
Forgery attempts (each run as full 6-mutant sets against census/round-76/c2-kill-tally.py):
  F1 reX09-body-pristine-fail0.txt (X09 header, body SELFTEST fail 1→0, EXIT=1): tally exit 1, X09 bind=ok verdict=UNREAD. REFUSED.
  F2 reX09-two-sha-lines.txt (instrument_sha256= twice, first correct second wrong): tally exit 1, bind=no-instrument-sha, UNBOUND. REFUSED.
  F3 reX09-selftest-in-path.txt (real --selftest removed; ' --selftest' only inside --work path): tally exit 0, all 6 KILLED, bind=ok. FALSE-GREEN.
  F4 reX09-crlf.bin (CRLF everywhere): tally exit 1, bind=instrument-mismatch (trailing \r kept in sha line; SELFTEST regex fails), UNBOUND. REFUSED.
  F5a X09 given twice with two different receipts (one F2): tally exit 1, both X09 bind=no-instrument-sha/duplicate, UNBOUND. REFUSED.
  F5b X09 twice (one X09 receipt, one P1 receipt): tally exit 1, bind=duplicate/instrument-mismatch, UNBOUND. REFUSED.
  F6 POSITIVE reX09-trailing-blanks.txt (3 trailing blank lines): tally exit 0, killed=6 pristine=PASS. Still ACCEPTS. OK.
  F7 --counter census/round-74/c1-counter.py override on honest set: tally exit 1, all bind=instrument-mismatch, pristine=FAIL. REFUSED (override cannot green a set).
  F8 reX09-pristine-body-exit0.txt (X09 header, pristine body, EXIT flipped to 0): tally exit 1, X09 bind=ok verdict=SURVIVED. REFUSED (honest set never full kill).
  F9 same file under two ids (X09 receipt as X09+M08): tally exit 1, M08 bind=instrument-mismatch UNBOUND. REFUSED.
  F10 pristine receipt as mutant X09: tally exit 1, bind=instrument-mismatch UNBOUND. REFUSED.
  REFUTED guesses: "--selftest only in a comment line" → not-a-selftest-run, UNBOUND, exit 1; "same digest reused as another id" → instrument-mismatch UNBOUND, exit 1. Both REFUSED.
Root cause (c2-kill-tally.py:84): _lane-read checks `" --selftest" in cmds[0]` — a substring test on the whole command= line, so ` --selftest` appearing in a --work PATH passes while the real flag is absent. The per-file forgeries F1/F2/F4/F5/F8/F9/F10 all stay red; F3 is the only FALSE-GREEN and it requires a hand-written header (consistent with the tally's stated limit, preregistration.txt:62 — "binding proves which instrument a receipt names, not that it ran").
Findings:
  MEDIUM: tally's selftest check accepts " --selftest" inside a path/arg value (F3 exit 0). Recommend exact token match (split on spaces, require a token "--selftest"), not substring search.
Files written (under .ufo/waves/round-76/w1/S76ExecC2/):
  reX09-body-pristine-fail0.txt, reX09-two-sha-lines.txt, reX09-selftest-in-path.txt, reX09-crlf.bin, reX09-pristine-body-exit0.txt, reX09-trailing-blanks.txt
Scratch /fast/scratch/hyaku/souji-r76/S76ExecC2 removed. No lane files edited; no git mutations.
