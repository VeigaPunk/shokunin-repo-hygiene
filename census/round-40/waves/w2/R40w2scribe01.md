# Round 40 wave 2 — R40w2scribe01 (scribe)

## Work performed

- **C1 calibration — SAFE at the declared closure revision.** Attacked the requirement that anchored item lines combine the frozen token test with resolvable, revision-bound evidence, that register commits are strict descendants of receipt revisions, and that token-only forgeries stay open. `census/round-40/c1-counter.py:235-260` evaluates evidence resolution/ancestry/path/binding; `:179-232` checks register ancestry; `:305-343` emits and gates the counts. The committed counter from `128e412b0ced3c243dc27c3dd3332054a611bc2e`, run with `--rev 549d9ec53a1f5932337ff14438fcd22b0621828d` and the listed C1 input files, returned all three items CLOSED, all three forgeries OPEN, zero register violations, and exit 0 (output below). **Note:** evaluating the earlier instrument commit itself (`--rev 128e...`) returned `ANCHOR-ABSENT` for all three later claim items and `REGISTER-ABSENT`; that is an earlier-revision/data mismatch, not the closure-revision result.
- **C2 operability — FALSIFIED for the landed counter suite; the core continuation probe itself passes.** Attacked joined continuation parsing and full class/trigger verification. The analyzer joins continuation lines at `census/round-40/docstring-classes.py:43-80`; the counter's observed-pair and wrapped-trigger legs are at `census/round-40/c2-counter.py:275-309`. Running the committed counter bytes and analyser from the landed commit against the closure revision reports L4 and L4b PASS, but L1, L2, and L5 FAIL; aggregate is 4/7 and exit 1. Thus the advertised end-to-end C2 counter acceptance is not reproducible from the landed counter bytes, despite direct evidence that its join and wrapped-trigger checks pass.
- **C3 coverage — SAFE on the landed counter/fixture battery.** Attacked multiple TOTAL handling, `--skip-unrecorded`, invalid UTF-8, all declared single-defect mutants, pristine success, and survival against the r39 fixture. `tests/fixtures/r40-drift-record-branches.py:94-123` contains eight cases including identical/conflicting TOTAL rows, skip/no-skip, invalid UTF-8 record and comment bytes; `census/round-40/c3-counter.py:61-69` defines M15–M18 and `:163-205` runs pristine, mutant and base scoring. The committed C3 counter against `128e...` reports pristine OK, all 4 mutants killed, base_killed=0, cases=8, exit 0.

## Landed changes

- `128e412b0ced3c243dc27c3dd3332054a611bc2e` is the landed instrument commit. Its commit summary names the three corresponding instruments and fixtures: `census/round-40/c1-counter.py`, `census/round-40/c2-counter.py`, `census/round-40/c3-counter.py`, `census/round-40/docstring-classes.py`, and `tests/fixtures/r40-drift-record-branches.py` (commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`; `git show --stat` reported 24 files changed, 7959 insertions(+), 2 deletions(-)).
- C1 landed evidence checks are in `census/round-40/c1-counter.py:235-260` and strict-descendant register checks at `:212-232`; the observed closure-revision run is recorded below.
- C2 landed continuation joining is in `census/round-40/docstring-classes.py:43-80`; the targeted L4/L4b results passed, while the aggregate counter failed as detailed below.
- C3 landed branch fixture and mutant counter are `tests/fixtures/r40-drift-record-branches.py:94-146` and `census/round-40/c3-counter.py:61-69,163-207`; observed counter output is below.

## Commands and real output

Commands below extract the counter (and, for C2, analyser) from the landed commit into the seat scratch directory, set `TMPDIR` explicitly, and pass that directory as `--scratch`. C1's later-added measurement inputs were extracted from `HEAD`; the C1 evaluation revision is the closure revision. C2 and C3 were invoked with the landed commit as `--rev` for the initial run; C2 was also run with the closure revision. All temporary content was under `/fast/scratch/hyaku/souji-r40/w2/R40w2scribe01`.

**C1:**

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c1-counter.py > /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c1-counter.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:census/round-40/c1-items.tsv > /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c1-items.tsv
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:census/round-40/c1-forged.tsv > /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c1-forged.tsv
TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2scribe01 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c1-items.tsv --forged /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c1-forged.tsv --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3 --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01
```

Output:

```text
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
```

**C2 (landed counter and analyser bytes; target revision 128e...):**

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c2-counter.py > /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c2-counter.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/docstring-classes.py > /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/docstring_classes.py
TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2scribe01 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01
```

Output:

```text
LEG L1 FAIL new rc=2 class=True old rc=2 class=True
LEG L2 FAIL new rc=2 class=True old rc=2 class=True
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 FAIL new=None old(one-line)=None
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=4 fail=3 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```

The same landed counter/analyser bytes with `--rev 549d9ec53a1f5932337ff14438fcd22b0621828d` returned the same seven LEG lines and SUMMARY; process exit was 1. Exact command:

```sh
TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2scribe01 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01
```

**C3:**

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c3-counter.py > /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c3-counter.py
TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2scribe01 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2scribe01
```

Output:

```text
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
EXIT=0
```

**Additional diagnostic failures (for transparency):** the first C1 attempt targeting `--rev 128e...` failed before counter execution while extracting `census/round-40/c1-items.tsv` because it does not exist at that revision (`fatal: path 'census/round-40/c1-items.tsv' exists on disk, but not in '128e412b0ced3c243dc27c3dd3332054a611bc2e'`). A later C1 invocation passed the staged register file by absolute scratch path and consequently got `REGISTER-ABSENT`; corrected invocation above passes repository-relative `census/round-40/cells.tsv`. The first C2 invocation omitted the required colocated analyzer module and failed with `ModuleNotFoundError: No module named 'docstring_classes'`; corrected invocation above extracts it beside the counter.

## Scope, gates, limits

- Exact attacked surfaces: `census/round-40/c1-counter.py`, `census/round-40/c2-counter.py`, `census/round-40/c3-counter.py`, `census/round-40/docstring-classes.py`, and `tests/fixtures/r40-drift-record-branches.py` at the line ranges cited above.
- Gates exercised: committed counter executions; base-vs-candidate C2 and C3 fixture legs; C1 closure evidence/register/forgery checks. No build, lint, or unrelated tests were run.
- Out of scope: editing any tracked source, fixture, preregistration, SCORECARD, LOG, or corpus; git/jj mutations, commits, pushes, or installs. No tools were installed.
- Findings: C1 and C3 SAFE on the reported inputs; C2 FALSIFIED as an end-to-end landed counter suite (L1, L2, L5 fail, exit 1), while L4/L4b specifically support the continuation-join behavior. The round's recorded C2 receipt in `census/round-40/records/c2-after-d.txt:4-12` reports 7/7 PASS, but that receipt is not reproduced by executing the landed counter bytes above.
- Scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2scribe01` was explicitly removed; follow-up check output: `scratch_removed=yes`.
