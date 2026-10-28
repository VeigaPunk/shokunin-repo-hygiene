# R40w2sentinel03 — C2 scratch discipline

Target attacked: committed `census/round-40/c2-counter.py` at `128e412b0ced3c243dc27c3dd3332054a611bc2e`; scratch lifecycle at lines 216–229 (fresh scratch creation), 237–354 (work), 358–359 (cleanup). Claim: explicit `--scratch` keeps counter-created scratch artifacts under that root, removes them afterwards, and does not write elsewhere.

## Exact command and output

Command (with explicit TMPDIR and a fresh `--scratch` child):
```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel03; mkdir -p "$S" && trap 'rm -rf -- "$S"' EXIT && export TMPDIR="$S" && D="$S/probe" && mkdir "$D" && python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch "$D"; find "$S" -mindepth 1 -printf '%P %y %s bytes\\n'; du -sb "$S";
```

Real output:
```text
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
probe d 6 bytes
0   /fast/scratch/hyaku/souji-r40/w2/R40w2sentinel03
```

Observed paths created inside the supplied scratch root: `probe` (directory), observed after the counter returned; its directory size was 6 bytes at measurement. No counter-created descendants remained inside it. The shell's subsequent `find`/`du` reported total size 0 for the root. Peak size was not continuously sampled; the run established only the post-run size, so peak size is **INCONCLUSIVE** (cannot infer peak from post-run measurement). The counter's `finally` calls `shutil.rmtree(scratch, ignore_errors=True)` (lines 358–359), removing its `mkdtemp` child. The wrapper's fresh `probe` directory is not removed by the counter and was removed by the wrapper's EXIT trap.

External writes: no paths outside the specified scratch were instrumented, so whether the counter or its subprocesses wrote elsewhere is **INCONCLUSIVE**; the command's observed stdout/stderr and repository source reads do not establish absence of external writes. No install performed.

Follow-up command attempting to inspect the root after the EXIT trap:
```sh
find /fast/scratch/hyaku/souji-r40/w2/R40w2sentinel03 -mindepth 1 -printf '%P %y %s bytes\\n'; du -sb /fast/scratch/hyaku/souji-r40/w2/R40w2sentinel03;
```
Real output:
```text
find: ‘/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel03’: No such file or directory (os error 2)
du: cannot access '/fast/scratch/hyaku/souji-r40/w2/R40w2sentinel03': No such file or directory
```

Verdict: **INCONCLUSIVE** for the requested complete discipline claim: counter output proves its scratch child was removed, but no peak-space monitoring or external-write tracing was performed. The seat scratch directory was removed by the EXIT trap.