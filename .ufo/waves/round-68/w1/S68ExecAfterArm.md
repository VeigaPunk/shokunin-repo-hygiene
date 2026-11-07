# S68ExecAfterArm — round-68 C1 after-arm (frozen counter)

## Verdict
- Battery regeneration: PASS — candidate + 14 mutants sha256 all MATCH census/round-68/battery/SHA256SUMS.
- Candidate run: PASS — EXIT=0, SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS, zero new=error rows, zero CASE rows with new!=expect (42 CASE rows).
- Mutant runs: 14/14 refuted (each EXIT=1, zero new=error rows). Declared-protection mismatches = 0. Survivors: none.
- stdout vs receipt: identical except the counter's trailing `# receipt=...` line in stdout (1-line diff, expected — receipt file holds the 4-line header + body; see counter write_receipt).

## Commands run
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f70da577eb1e1624cc63ab8fd0468565927d9b6a:tools/souji-receipt-write.py > $SCRATCH/cand/souji-receipt-write.py`
- `python3 -B census/round-68/mutate-writer.py $SCRATCH/cand/souji-receipt-write.py $SCRATCH/mut` (from lane root)
- Candidate: `python3 -B census/round-68/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix census/round-68/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev f70da577eb1e1624cc63ab8fd0468565927d9b6a --tool tools/souji-receipt-write.py --work $SCRATCH/work/CAND --receipt .ufo/waves/round-68/w1/S68ExecAfterArm/c1-after/CAND.txt`
- Each mutant: same with `--new-tool $SCRATCH/mut/<id>.py` in place of --rev/--tool, `--work $SCRATCH/work/<id>`, receipt `c1-after/<id>.txt`.
- Counts: `grep -c 'new=error' c1-after/<name>.txt`; `grep '^SUMMARY'`, `grep '^EXIT='`; candidate CASE diff via parsing `expect=` vs `new=` on CASE lines.

## Decisive output
- CAND: `SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS`, EXIT=0, error-rows=0, CASE-diff=0.
- K1 EXIT=1 class_mismatches=2 (new_forgeries=0 — refuted via class mismatch, claim_upheld at census/round-68/c1-counter.py:923-926).
- M-CD-NCABS EXIT=1 new_honest=10 class_mismatches=0 (refuted via honest shortfall, same predicate).
- M-CD-NCRAW EXIT=1 new_honest=9 class_mismatches=1.
- All other mutants EXIT=1 with new_forgeries>=1; all 14 EXIT=1, error-rows=0.
- Disk guard (pre-run): /fast/scratch/hyaku free 409.3G (50% use) — green.

## Files written (all under .ufo/waves/round-68/w1/S68ExecAfterArm/)
- c1-after/CAND.txt, c1-after/CAND.stdout, c1-after/CAND.stderr (empty, 0 bytes)
- c1-after/{K1,K2,K3,K4,K5,K6,K7,K8,M-CD-CALL,M-CD-EMPTY,M-CD-NCABS,M-CD-NCRAW,M-CD-ROOTREL,M-CD-SCRUB}.txt + .stdout + .stderr (all .stderr 0 bytes)
- c1-after/summary.tsv (header + 15 rows: name, exit, summary-line, error-rows, refuted)
- This report: .ufo/waves/round-68/w1/S68ExecAfterArm.md
- Scratch dir /fast/scratch/hyaku/souji-r68/S68ExecAfterArm removed before yield (see below).

## Findings
- LOW: Mutant receipts carry `rev=3639087917eaeb28719d7603110a6ec22782100e` (base rev) in their header, not the mutant identity; the mutant is bound only via the `command=` line's --new-tool path and the slot sha. Candidate receipt correctly carries `rev=f70da577...`. Not a predicate failure; noted for L1 integration (counter grammar, census/round-68/c1-counter.py:1170-1178).
- No other findings. No tool installs/updates (none needed).

Report: .ufo/waves/round-68/w1/S68ExecAfterArm.md
