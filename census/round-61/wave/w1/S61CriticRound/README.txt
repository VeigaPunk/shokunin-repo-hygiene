S61CriticRound evidence (receipts). Probe scripts run with S=<scratch>; fixture repos were created under scratch only.
chrono-rule.txt        literal Q120 add-commit rule vs last-touch (F'') over fixture shapes S1-S5, H, H2
matrix-r60-rows.txt    r60 matrix builder (build-matrix.py, unchanged) rebuilt in scratch: honest rows all refused by literal rule
partial-visibility.txt chunked-without-pause vs chunked-with-pause vs honest temp+link, N=40
real-record-base.txt   base checker (git show c7228424) on census/round-60/preregistration.txt @ d05a0001, default and --substance
axis-check.txt         tools/souji-axis-check.py on v1/v2/v3 r61-shaped machine blocks and on r60 prereg
mutA-worktree-digest.py / mutB-chunked-direct.py  mutants made from tools/souji-receipt-write.py at c7228424 (one edit each)
  run: python3 -B tests/fixtures/r60-receipt-write.py --tool <mutant> --work DIR  -> pass=8 fail=0 (both)
