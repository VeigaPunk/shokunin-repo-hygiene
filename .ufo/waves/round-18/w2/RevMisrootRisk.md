STATUS: DONE — No untracked fleet-root file had a first line naming Souji Round 18.

Attacked claim: L1 misroot exposure (operability).

Finding: No actionable round-18-named untracked fleet-root file was observed. The read-only fleet-root status did expose nine untracked `.ufo/state/*report-baseline` files, but their first lines are SHA-256 of empty content (`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) and do not name Souji Round 18. No files were moved or deleted. The status also reported modified `.ufo/watchdog.log`; it was not inspected because it was not an untracked file within the requested scope.

Exact command and output:

```text
git -C /home/vgpnk/Projects/shokunin status --porcelain
 M .ufo/watchdog.log
?? .ufo/state/kaidoku.report-baseline
?? .ufo/state/kake.report-baseline
?? .ufo/state/kama.report-baseline
?? .ufo/state/mado.report-baseline
?? .ufo/state/mori.report-baseline
?? .ufo/state/souji.report-baseline
?? .ufo/state/tabi.report-baseline
?? .ufo/state/tameshi.report-baseline
?? .ufo/state/tsukuroi.report-baseline
```

Read only the first line of each untracked file named by that command:

```text
.ufo/state/kaidoku.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/kake.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/kama.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/mado.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/mori.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/souji.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/tabi.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/tameshi.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
.ufo/state/tsukuroi.report-baseline: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Verdict: This scoped probe found no evidence that an untracked fleet-root file's first line names Souji Round 18; the asked-for matching-path list is empty. It does not establish whether the other fleet-root status entries are attributable to this assignment. Smallest fix: none indicated by this probe.