# R97ExecC1 — C1 re-derivation (independent of L1, committed bytes)

Seat: executor. Owns .ufo/waves/round-97/w1/R97ExecC1/ + this report. Scratch /fast/scratch/hyaku/souji-r97/R97ExecC1/ (deleted before yield). No tools installed. Lane read-only; nothing committed.

## Verdicts

- AFTER predicate (c1-survivor-search.py + declared-shapes.py): CONFIRMED EXACTLY. Check line, all 10 SEARCH lines, SEARCH-SUMMARY generated=10 ambiguous=0 uncompiled=0 hung=0 scored=10 errored=7 killed=2 survived=1, EXIT 0; SHAPES-SUMMARY shapes=14 mismatched=0, EXIT 0. Receipts: R97ExecC1/after-search.txt, R97ExecC1/after-shapes.txt.
- DO-NOTHING CONTROL (r95 via wrapper): CONFIRMED EXACTLY. Same summary, EXIT 0, then t1/t4 at hooked=70 / x1/x2 at hooked=70 under r95 (mismatched=2). Receipt: R97ExecC1/ctl-r95.txt + shapes-r95.txt. Wrapper runs r95 HOOK/verdict()/score()/main() unchanged (load + sys.exit(r95.main(sys.argv[1:]))).
- FORGERIES: CONFIRMED EXACTLY. FA errored=9/killed=0 shapes=0; FB errored=1/killed=6/survived=3 shapes=0; FC errored=6/killed=3 shapes=0; FD/FE summary unchanged shapes=2. C1-FORGERY-SUMMARY forgeries=5 refused=5, EXIT 0. Byte-identical to P2 receipt (modulo header lines + trailing EXIT 0). Receipt: R97ExecC1/forgery.txt.
- R96 SHAPE CONTROL: CONFIRMED mismatched=2 (x1/x2 at hooked=1, the A1 trade). Receipt: R97ExecC1/shapes-r96.txt.

## FALSIFIES-NUMBER (docstring only, reproducer below)

The instrument's docstring in census/round-97/c1-survivor-search.py (lines 39-40, repeated 45-46) states the frozen r95 hook on the same 14 scripts "scores mismatched=4 (t1/t4 and x1/x2 all errored)" / "the r95-rule control fails at mismatched=4 (r97: 14 shapes)". MEASURED (P2 controls/shapes-r95.txt AND my shapes-r95.txt): mismatched=2 — t1/t4 MISMATCH (plain=0 hooked=70), x1/x2 ok (plain=1 hooked=70, errored by design for crash shapes). No r95-table sentence in the prereg uses mismatched=4; the prereg CONTROL says r95 mismatched=2, which is correct. So this falsifies a docstring sentence of the frozen instrument, not any prereg predicate sentence — L1 may treat it as a wording staleness (likely carried from the r96-era "r94-rule mismatched=6" after the 12→14 shape change; A9 note at line 48 shows the shelf life). Reproducer: R97ExecC1/shapes-r95.txt (my re-run) vs census/round-97/c1-survivor-search.py:39-40.

No other falsification: every prereg C1 sentence tested (check line, summary, per-id verdicts, all 14 shape lines, 5 forgery lines with hashes) matched byte-for-byte.

## Per-target rows

6x66 ROWs; rc distribution + SOUJI-R97-CRASH evidence in R97ExecC1/row-table.txt. Semantic kills a491c22/h-ok-admits-one: rc∈{0,1} only, 1 match=no each, verdict yes via rc=1 leg — no rc=70 either, confirmed. a127c26: rc∈{0,1}, 0 mismatches, verdict no — confirmed. h-crash-late/h-atexit/h-thread: 66×rc=70, no kept marker in ROW detail (harness keeps detail only for match=error rows); h-sysexit/h-osexit: 56×SOUJI-R97-CRASH markers kept. h-sigkill: 66×rc=-9. h-crash-index: single rc=70 ROW (LD6) triggers errored. The sentinel check=pass line carries the per-channel reason assertion.

## Pins

All prereg short-hashes verified: search b8efc240..., targets 320ea2ec..., r95 search 6066508f..., counter fd0a8e24..., harness 1868a570..., population d6439f65.... Full table in R97ExecC1/pins.txt. Shape-script hashes for all 14 (a12==a2 bytes, v1==t3 bytes noted); all 44 sha256 measured. Forgery hashes identical to P2.

## Hunk inventory (r96→r97)

157-line diff, 431→483 lines. Every hunk classified in R97ExecC1/hunk-inventory.txt: docstring (3 hunks), HOOK (13: latch state, crash-first×2, RAISE latch, pending EH, _souji_reraise, atexit flush, RERAISE registration, A3 blocking restore, marker/tool-id strings, sentinel check strings), CHECKS (marker reasons), HAND (check-script filename only), rule (docstring-only). No UNEXPECTED hunks: gen/verdict/score/main/precondition/HAND content unchanged.

## Evidence

Receipts under .ufo/waves/round-97/w1/R97ExecC1/: after-search.txt, after-shapes.txt, ctl-r95.txt, shapes-r95.txt, shapes-r96.txt, forgery.txt, diff-r96-r97.txt, pins.txt, row-table.txt, hunk-inventory.txt.

Report: .ufo/waves/round-97/w1/R97ExecC1.md
