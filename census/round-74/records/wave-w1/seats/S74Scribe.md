# S74Scribe — r74 corpus drafts (scribe): DONE

Verdict: S317 row and r74 knowledge section drafted for L1 integration; census validate exit 0; C1 numbers reproduced independently; C2 numbers re-counted from committed receipts. No HIGH/MEDIUM finding.

Findings
- LOW: prereg C1 conjunct (iii) receipt census/round-74/records/c1-domain-trial.txt is absent at tip 8fe48c86; by design it can only be produced at the final tip with the round report (peer S74ExecC1 has in-flight uncommitted domain.out). Not claimable yet; not a defect.
- LOW: lane worktree is concurrently dirty from L1/peer activity (git status at close: SCORECARD.md, SKILL.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md, corpus/knowledge/filter-filemode-witness.md modified; untracked census/round-74/records/regress-*.txt, corpus/lessons/round-74.md). I wrote nothing outside my seat dir and scratch; my S317 draft equals the lane's line 276 exactly (1100 bytes).

Evidence
- C1 re-run, S=/fast/scratch/hyaku/souji-r74/S74Scribe:
  `python3 -B census/round-74/c1-gate-counter.py --gate $S/c1gate/souji-pre-report-gate.sh --work $S/c1work-cand` -> `SUMMARY rows=9 mismatches=0 errors=0`, `EXIT=0` (gate copy beside tools/souji-receipt-write.py) = records/c1-after.txt.
  Base gate `git show 43cd74bba84bb498b57a74377ccb0567d10864d5:tools/souji-pre-report-gate.sh` -> mismatches=3 (GF1 GF2 GF3 match=no) EXIT=1 = controls/c1-K-a-do-nothing.txt; K-b=4, K-c=1 as committed.
- C2 receipts (committed bytes): D6 FWw / D7 FC1 / D8 FC2 each base_unwitnessed=1, edited-row base_witness=no, EXIT=1 (records/c2-after-D6..D8.txt); D1..D5 base_unwitnessed=1 (5/5); pristine base_forgeries=15 base_unwitnessed=0 EXIT=0; M08/M14/M15/M17 selftest fail=1,1,2,1 EXIT=1 (r73 before: 52/52 pass); r74 selftest 62/62 fail=0.
- S317 verified: capture sha256 c8aca94073fed907c47f631db8a9c53a9a0a0007f8ea3cdce9722224bebbaa93, 15194 bytes; quote at offset 2194 in census/round-74/srcs/gitformat-index.txt (17 words, occurs once); 11 cells / 12 pipes, no `|` inside a cell.
- Validate: `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $S/corpus/SOURCES.md` -> exit 0, 0 E-codes, 86 pre-existing W04; control without the row exit 0; stdout diff = final `ok` path line only.

Files written (all under /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-74/w1/):
- S74Scribe/sources-row.md — exact row to append after S316
- S74Scribe/knowledge-r74.md — r74 section for corpus/knowledge/filter-filemode-witness.md
- S74Scribe/census-validate.txt — commands, exit 0, findings
- S74Scribe/c1-cand.out, S74Scribe/c1-base.out — C1 counter re-run outputs
- S74Scribe.md — this report
Tools installed: none. Scratch /fast/scratch/hyaku/souji-r74/S74Scribe removed.
