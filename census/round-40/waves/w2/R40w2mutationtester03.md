# R40w2mutationtester03 — C2 mutation probe

**Attack:** landed C2 counter, specifically L4b synthetic probe (counter lines 303–309), observed-pair trigger presence (288–301), source parsing path (276–284; expected AST-vs-source-slicing fault point), L6 consumer arm (327–354), and final harm gate (360–366). Consumer fixture list: lines 62–70. Frozen C2 claim: `census/round-40/preregistration.txt:7-8`.

**Verdict: INCONCLUSIVE.** The required exact revision tree contains a different C2 counter than the source presented in the lane. Running the real committed counter fails before argument parsing or mutation coverage: its import expects `docstring_classes.py` adjacent to the counter, but the recorded commit's analyser has a hyphenated filename. The lane working-tree counter instead uses dynamic loading and its pristine counter invocation passes; it is not the requested landed bytes. No mutant verdicts are valid because every attempted run from the commit version exits during import.

## Exact commands and outputs

Initial worktree (current lane, not the assigned immutable revision):

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03
```

Output:

```text
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```

The exact revision was then materialized in `/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03/repo`; `git rev-parse --show-toplevel` output was that exact path. Commit counter hash was `cd6b1e97d7276e166b56ac9342094b8c5b6e1ba610f320d5d71cb5124f888633`. Commit analyser hash was `bc418a58e751a69f00d5d9c207d5c174f486e759418f52367eb7fe0a339105ba`.

Exact-revision invocation:

```sh
python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03/repo/census/round-40/c2-counter.py --root /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03/repo --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03
```

Output:

```text
Traceback (most recent call last):
  File "/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03/repo/census/round-40/c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'docstring_classes'
RC=1
```

Each of five attempted counter mutants (drop L4b, accept missing pair, truncate source input, unconditional L6, remove final harm requirement) emitted the same traceback and `RC=1`; each is therefore **inconclusive**, not killed/survived. The first attempted versions outside the worktree likewise stopped on this import error. The mutation harness's pristine baseline could not be established on the specified commit bytes.

The discrepancy is directly observable: lane counter SHA256 `77bac23881b690de2c9748de714d50ed79b87d228c6eba5f4f0587abfe5c4d00`, versus commit counter SHA256 above. The commit has the failing import at line 46, while the lane source at lines 128–142 dynamically loads the hyphenated analyzer. Reported consumer-fixture mutation results are therefore unavailable.

**Scratch removed:** yes. The exact-revision scratch worktree and `/fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester03` were removed. No packages/tools installed.