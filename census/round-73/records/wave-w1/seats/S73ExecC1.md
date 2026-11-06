# S73ExecC1 — C1 falsification: writer byte-truth / index stat cache + receipt replayability

VERDICT: all 5 assigned items REPRODUCED from committed bytes; no C1 claim failed. No HIGH or MEDIUM finding.
Lane read-only for me; HEAD 312e8f29. Evidence copies: .ufo/waves/round-73/w1/S73ExecC1/evidence/ (+ evidence.txt).
Scratch /fast/scratch/hyaku/souji-r73/S73ExecC1 removed at exit.

1) C1 main arm, stage-W writer — REPRODUCED
 cmd: python3 -B census/round-73/c1-counter.py --root <lane> --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev b84ff90bff05fb057c5a8c4b0661a9ec41d9e4a2 --tool tools/souji-receipt-write.py --work $S/main
 out: SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0 base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0 errors=0 regress=PASS / EXIT=0
 body diff vs census/round-73/records/c1-after.txt: rc=0 (172=172 lines after the 4 run-receipt header lines).
 CASE FX1/FX2/FX3: new=refuse new_findings=RECEIPT-WORKTREE-STAT-CONCEALED, base=accept, base_witness=yes (rc base 0 / new 2); FXh new=accept base_witness=no; FXc new=accept base_witness=yes — identical to c1-after.txt.
 lane-base arm (--rev a789486d…): SUMMARY … new_forgeries=3 … class_mismatches=3 … EXIT=1; FX1-FX3 new=accept; body diff vs controls/c1-K-a-do-nothing.txt rc=0.

2) K-b / K-c literal replays from the `# command=` lines (only scratch prefix substituted) — REPRODUCED
 K-b: SUMMARY … new_forgeries=0 new_honest=0 class_mismatches=59 … regress=FAIL / EXIT=1; K-c: SUMMARY … new_forgeries=15 new_honest=21 class_mismatches=15 … regress=PASS / EXIT=1.
 Full output byte-identical to the committed receipts (80/80 CASE, 80/80 detail, all `# bind`/`# c1-counter`/SUMMARY/EXIT lines) except the two run-receipt metadata lines `# command=`/`# cwd=` my replay does not regenerate.

3) Writer selftest from `git show b84ff90b…:tools/souji-receipt-write.py` (sha256 d1ad5c79…f39 = c1-after slot-new bind) — REPRODUCED: SELFTEST cases=44 pass=44 fail=0 (lane-base writer: 42/42; case_43/44 at tools/souji-receipt-write.py:1952,1976).

4) mk-counter replay at 1eac307f (`git archive | tar -x`, then `python3 -B census/round-73/mk-counter.py`) — REPRODUCED: wrote counter sha256 3809ee7d… / matrix f2ced976…; cmp counter IDENTICAL, matrix IDENTICAL; first 75 rows byte-identical to census/round-72/c1-matrix.tsv; r72 counter sha 7578447d370…a912.

5) Freeze chronology — REPRODUCED: `git cat-file -e 23ecd070:census/round-73/c1-counter.py` fails rc=128 (path not in F; counter is stage I) and c1-matrix.tsv likewise; writer blob sha at 23ecd070 = aaacba33 = a789486d = b7790001…244d (lane base), b84ff90b = d1ad5c79…f39; ancestry a789486d < 23ecd070 < 1eac307f < aaacba33 < b84ff90b < 312e8f29 (all rc=0); ct F 1794002711 < I 1794002891 < K 1794002930 < W 1794003118 < A 1794003159.

Independent falsification probe (fresh fixtures, INDEX_STAT_CODE extracted from c1-counter.py:315-350, `-C <fixture>` with toplevel asserted): same-size in-place forge + index stat rewrite (oid kept, checksum recomputed, index mtime +5 s) leaves `git status --porcelain` EMPTY; stage-W writer refuses rc=2 RECEIPT-WORKTREE-STAT-CONCEALED pre-run, in-run and on the instrument, no receipt; lane-base writer accepts rc=0 and writes a receipt over the forged bytes; honest stale-mtime tree accepted rc=0. The defect is real and the stage-W writer closes it on routes I built.
Counter selftest (supporting): SELFTEST cases=52 pass=52 fail=0. Matrix re-derivation: 80 rows, 21 accept / 59 refuse, 15 refuse+base_expect=accept (12 carried + FX1-3), matching SUMMARY.

FINDINGS
- LOW: every committed round-73 receipt ends with two `EXIT=` lines (the counter prints one; run-receipt.sh appends one) — the prereg's counting `grep -E '^(SUMMARY|EXIT=)'` therefore returns two EXIT lines; harmless, but a strict single-line consumer would see a duplicate.
- LOW: the K-b/K-c `# cwd` line records lane master=1eac307f while today's replay runs at 312e8f29; output still identical because the command binds counter/matrix shas via `--bind` and `--new-tool`, so no drift. Receipt replayability holds on this host.
- LOW (observation, not my writes): the lane worktree became dirty mid-wave (SCORECARD.md 19:16:53, SKILL.md, corpus/*, records/m2-guard-canfail.txt 19:18:41, corpus/lessons/round-73.md 19:19:46) from sibling seats; none of my commands wrote inside the lane and all arms still reproduced committed bytes.

Files written: .ufo/waves/round-73/w1/S73ExecC1.md; .ufo/waves/round-73/w1/S73ExecC1/evidence.txt; .ufo/waves/round-73/w1/S73ExecC1/evidence/{main-stageW.out, base-lane-base.out, replay-c1-after.out, replay-K-a.out, replay-K-b.norm, replay-K-c.norm, counter-selftest.out, writer-selftest-stageW.out, writer-selftest-lane-base.out}.
No lane, fleet-root or sibling files touched; no git mutation; no sysctl/tool installs.
