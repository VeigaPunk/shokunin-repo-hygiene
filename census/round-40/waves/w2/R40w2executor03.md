# R40w2executor03 — C2 counter run at landed revision (executor, w2 falsify)

Attacked: `census/round-40/c2-counter.py` (committed at 128e412b0ced3c243dc27c3dd3332054a611bc2e, line 46 `import docstring_classes as dc`) and the lane HEAD copy (549d9ec; the file was changed by 8a5fbdb "counter fixes").
Scratch: /fast/scratch/hyaku/souji-r40/w2/R40w2executor03/ (TMPDIR and --scratch passed explicitly).
L=/home/vgpnk/Projects/shokunin/souji-shokunin  R=128e412b0ced3c243dc27c3dd3332054a611bc2e  BASE=0242085909fb6a4ee041c5443d76316ac6d59d4b

## Run A — the counter AS COMMITTED at 128e412 (git show R:census/round-40/{c2-counter,docstring-classes}.py into $S/tree/census/round-40/)
cmd: `cd $S && TMPDIR=$S python3 -B $S/tree/census/round-40/c2-counter.py --root $L --rev $R --base-rev $BASE --scratch $S`
output (no LEG lines, no SUMMARY line):
```
Traceback (most recent call last):
  File ".../tree/census/round-40/c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
ModuleNotFoundError: No module named 'docstring_classes'
```
EXIT=1. Cause: the sibling file committed in 128e412 is `docstring-classes.py` (hyphen), not importable as `docstring_classes`. Same failure when the counter is extracted alone. So the landed-instrument bytes cannot produce any LEG/SUMMARY line; the C2 measurement receipt for the landed commit does not exist. Fixed later by 8a5fbdb (loads the analyser from committed bytes at --rev via load_analyzer).

## Run B — the lane HEAD copy of the counter (post-8a5fbdb; identical to 8a5fbdb: `git diff --stat 8a5fbdb HEAD -- c2-counter.py` empty), --rev $R
cmd: `TMPDIR=$S python3 -B $L/census/round-40/c2-counter.py --root $L --rev $R --base-rev $BASE --scratch $S`
```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```
EXIT=0.

## Observations
- Note L1/L2 "old" side uses --defect-base-rev ed30b7f5… (default), not --base-rev; with --base-rev (BASE) alone the discriminating arm would not hold (BASE already repaired). Stated in the counter's own --help; not a falsifier.
- L4 has only 3 observed pairs; only RECORD-OUTSIDE-ROOT is wrapped.

## Verdict
FALSIFIED for the landed bytes at 128e412 (Run A: ModuleNotFoundError, exit 1, no LEG/SUMMARY; command above). SAFE for the post-fix counter at HEAD run against rev 128e412 (Run B: 7/7 PASS, harm=0, exit 0). The C2 receipt must be cited from 8a5fbdb+ bytes, not the 128e412 commit.

Scratch dir /fast/scratch/hyaku/souji-r40/w2/R40w2executor03/ removed at the end of this seat (see final check below).
