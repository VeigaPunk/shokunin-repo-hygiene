## Status
STATUS: PASS — all six items (G09,G12,G13,G14,G15,G16) still-AGREE under the r35 counter; no flip, no LIST-DEFECT.

## Evidence
Command per item (flock under own scratch c1.lock, scratch /fast/scratch/hyaku/souji-r35/SwarmReviewer10-2/cnt-<id>, loadavg 35.7-41.8 at runs):
`python3 -B census/round-35/c1-counter.py --root <lane> --rev d1c940414087b606503662e4d115f51cb0fba40c --list-rev 4e9c295e9339cc2b13f7a0dd5ec9fc8213a9e18e --scratch <s> --only <id>` (rc=0 each; SUMMARY items=1 agree=1 unresolved=0 mismatches=0 withdrawn=0 restated=0 partial=1)
- ITEM G09 AGREE original rc=0 expect_exit=0 last=SUMMARY paragraphs=400 boundary_cuts=562 midline_cuts=842 violations=0
- ITEM G12 AGREE original rc=0 last=SUMMARY total=32 pass=32 fail=0 base_discriminating=14 (registered statement has no base_discriminating suffix; counter's prefix/collapse match accepted it)
- ITEM G13 AGREE original rc=0 last=SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160
- ITEM G14 AGREE original rc=0 last=SUMMARY total=4 pass=4 fail=0
- ITEM G15 AGREE original rc=0 last=SUMMARY total=8 pass=8 fail=0 base_discriminating=4 (same suffix remark)
- ITEM G16 AGREE original rc=0 last=SUMMARY total=3 pass=3 fail=0 base_discriminating=1 (same suffix remark)
Pin check: every item's `at` is `{REV}` (no non-{REV} pins). `git cat-file -e d1c9404…:<f>` ok for all 9 files (probe-carry-invariants.py, r21-read-root.py, souji-seat-audit.py, r21-reason-canary.sh, souji-proc-census.sh, r21-read-render-edges.py, run-acceptance.py, r21-replay-boundaries.py, r21-source-head.py). Embedded {BLOB:} pins also resolve: 6ff3413b:tools/souji-seat-audit.py, 6ff3413b:tools/souji-proc-census.sh, 8513d6ac:census/round-21/run-acceptance.py, 522dcd76:census/round-21/run-acceptance.py.

## Findings
1. G09..G16: still-AGREE, none flipped to MISMATCH (items.tsv lines 36,38-42).
2. Residual note (not a defect): G12/G15/G16 live output carries a trailing `base_discriminating=N` token absent from the registered statement; the r35 counter accepts it as AGREE via its prefix match — a stricter exact-line counter would flip these three. Not a claim blocker.

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-35/w1/SwarmReviewer10.md
