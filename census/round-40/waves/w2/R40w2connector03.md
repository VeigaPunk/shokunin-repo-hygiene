# R40w2connector03 — cross-claim separability matrix (C1/C2/C3), souji round 40 wave 2 (FALSIFY)

Date: 2026-10-28. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.

**What I attack:** the round's implied claim that its three instruments are separable — i.e. for each
pair (C1,C2), (C1,C3), (C2,C3), whether the FIRST claim's frozen target is reachable with the OTHER
claim's files absent from the tree. Any hidden cross-instrument read would make a "green" target
vacuous (it would silently degrade when a sibling instrument is removed) and would falsify the
preregistration's "Claims are distinct axes and independently measurable"
(census/round-40/preregistration.txt:13).

**Revisions used (all runs):**
- Checked-out revision everywhere: `549d9ec53a1f5932337ff14438fcd22b0621828d` — the closure revision
  (lane HEAD, detached; the only revision at which the C1 closure cells exist and all three green
  receipts `census/round-40/records/{c1,c2,c3}-after-d.txt` were measured).
- Instrument-landing commit per the assignment: `128e412b0ced3c243dc27c3dd3332054a611bc2e` (see
  Finding F1: it is also the ONLY commit that ever added these files, which bounds how separability
  can be shown).
- C2/C3 `--base-rev`: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (r39 tip, the preregistration base).

**File sets removed per row** (from the assignment's "Claims under attack" listing):
- C1 = `census/round-40/c1-counter.py` (+ its data `c1-items.tsv`, `c1-forged.tsv`, `cells.tsv`, kept)
- C2 = `census/round-40/docstring-classes.py`, `census/round-40/c2-counter.py`
- C3 = `tests/fixtures/r40-drift-record-branches.py`, `census/round-40/c3-counter.py`

## Static dependency map (why separability was expected)

C1 — `census/round-40/c1-counter.py`:
- reads `--items`/`--forged` from the WORKING TREE via `open()` (run(), c1-counter.py:273, opens at
  :289-296 of the invoked body);
- reads `--register` from git history: `git_show(root, register_rev, register)` c1-counter.py:184;
- runs the substrate reconciler bytes at REV: c1-counter.py:181
  (`git_show(root, rev, "tools/souji-citation-reconcile.py")`);
- evaluates items against `row["file"]` and `evidence_path` at pinned revisions via `git show`
  (evaluate_item, c1-counter.py:235).
- Grep over c1-counter.py for `c2-counter|c3-counter|docstring-classes|drift-record-branches|docstring-joined|c1-evidence`:
  **zero occurrences**. No sibling-instrument path appears anywhere in the counter.

C2 — `census/round-40/c2-counter.py`: reads its own analyser and fixture from history
(`ANALYZER = "census/round-40/docstring-classes.py"` c2-counter.py:46, loaded at :128;
`FIXTURE = "tests/fixtures/r40-docstring-joined.py"` c2-counter.py:61, fetched at :312), the
substrate tools (`CITATION` :59, `DRIFT` :60) and prior-round consumer fixtures (`CONSUMERS` :62-70,
all r36-r38/r39). **No C1 or C3 path appears.**

C3 — `census/round-40/c3-counter.py`: reads the substrate tool and its two fixtures from history
(c3-counter.py:144-146; defaults `--tool tools/souji-worktree-drift.py` :128,
`--fixture tests/fixtures/r40-drift-record-branches.py` :129,
`--base-fixture tests/fixtures/r39-drift-record-rules.py` :130). **No C1 or C2 path appears.**

Fixtures mirror this: `r40-drift-record-branches.py` touches only `--tool` (default the substrate
tool, :132) and `--work`; `r40-docstring-joined.py` defaults its analyzer to C2's OWN file
(:105-106) and the substrate tool (:107); `r40-c1-evidence.py` defaults to C1's OWN counter and the
r39 counter (:234-235) and copies the substrate reconciler from the lane (:44, :75).

## The matrix

| pair | removed from the work tree | clone | result (real run at 549d9ec) | verdict |
|---|---|---|---|---|
| (C1,C2) | `census/round-40/c2-counter.py`, `census/round-40/docstring-classes.py` | `$S/P12b` | rc **0**, `SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6` — byte-equal to full-tree baseline and to receipt `c1-after-d.txt` | C1 target REACHABLE — **SAFE** |
| (C1,C3) | `census/round-40/c3-counter.py`, `tests/fixtures/r40-drift-record-branches.py` | `$S/P13` | rc **0**, same byte-equal SUMMARY | C1 target REACHABLE — **SAFE** |
| (C2,C3) | `census/round-40/c3-counter.py`, `tests/fixtures/r40-drift-record-branches.py` | `$S/P23` | rc **0**, `SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741` — byte-equal to full-tree baseline and receipt `c2-after-d.txt` | C2 target REACHABLE — **SAFE** |
| union: C1 vs C2+C3 | all four C2+C3 files | `$S/U1` | rc **0**, byte-equal C1 SUMMARY | **SAFE** |
| union: C2 vs C1+C3 | `c1-counter.py` + both C3 files | `$S/U2` | rc **0**, byte-equal C2 SUMMARY | **SAFE** |
| union: C3 vs C1+C2 | `c1-counter.py` + both C2 files | `$S/U3` | rc **0**, `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e` — byte-equal to receipt `c3-after-d.txt` | **SAFE** |
| negative control | P12 **plus C1's own `c1-items.tsv`** | `$S/P12` | `REFUSAL USAGE: [Errno 2] No such file or directory: …/P12/census/round-40/c1-items.tsv`, rc **2** | procedure can fail — not a case-that-cannot-fail |

## Exact commands (re-runnable by the L1)

Scratch root (mine): `S=/fast/scratch/hyaku/souji-r40/w2/R40w2connector03`.
Every clone was verified before use: `git -C <clone> rev-parse --show-toplevel` == the clone dir and
`git -C <clone> rev-parse HEAD` == `549d9ec53a1f5932337ff14438fcd22b0621828d` (outputs echoed above).

```
git clone -q -s --no-checkout /home/vgpnk/Projects/shokunin/souji-shokunin "$S/base"
git -C "$S/base" checkout --detach -qf 549d9ec53a1f5932337ff14438fcd22b0621828d
# row (C1,C2):
git clone -q -s --no-checkout /home/vgpnk/Projects/shokunin/souji-shokunin "$S/P12b"
git -C "$S/P12b" checkout --detach -qf 549d9ec53a1f5932337ff14438fcd22b0621828d
rm "$S/P12b/census/round-40/c2-counter.py" "$S/P12b/census/round-40/docstring-classes.py"
mkdir -p "$S/w/c1-p12b"
( cd "$S/P12b" && python3 -B census/round-40/c1-counter.py --root "$S/P12b" \
    --rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
    --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv \
    --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3 \
    --scratch "$S/w/c1-p12b" ; echo rc=$? )
# rows (C1,C3) and (C2,C3): same shape with the C3 / C2 file lists shown in the matrix.
# baselines: same argv with --root "$S/base" and no rm.
```

Full baseline outputs (the pruned rows printed byte-identical stdout):

```
=== C1 baseline, full tree, relative paths ===
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
c1-base2-rc=0
=== C2 baseline ===
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
c2-base-rc=0
=== C3 baseline ===
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
c3-base-rc=0
```

All pruned rows (P12b, P13, P23, U1, U2, U3) printed stdout byte-equal to these baselines with the
same exit codes (rc=0); the negative control printed the REFUSAL USAGE line above with rc=2.

## Findings

**F1 — no existing revision separates any pair by tree content (demonstrability bound, not a
defect).** All seven r40 instrument files were added in exactly one commit:

```
git -C <lane> log --diff-filter=A --format='%h %s' -- \
  census/round-40/c1-counter.py census/round-40/c2-counter.py census/round-40/c3-counter.py \
  census/round-40/docstring-classes.py tests/fixtures/r40-drift-record-branches.py \
  tests/fixtures/r40-docstring-joined.py tests/fixtures/r40-c1-evidence.py
128e412 round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery
```

So "the exact revision to check out" that lacks a sibling claim's files does not exist for any
pair; the only possible demonstrations are (a) work-tree pruning at 549d9ec (what I ran), or (b) a
constructed deletion commit (not run: seats do not commit). Interpreting the matrix: work-tree
absence is also weaker than byte absence, because C2/C3 read their own instruments from HISTORY at
`--rev` (c2-counter.py:312, c3-counter.py:144-146) — removing sibling files from the work tree
cannot degrade them at all. The matrix rows therefore prove the strongest form reachable without
history rewriting: no instrument ever dereferences a sibling instrument's PATH, in the work tree or
in history.

**F2 — C1's green is data-coupled to the C2/C3 receipts (fine print, second-order).** C1 never
reads C2/C3 instrument bytes, but its items and register bind C2/C3 RECEIPT bytes:
`c1-items.tsv:3` (`R40-CLAIM-D2 … census/round-40/records/c2-after.txt@6ded124…`),
`cells.tsv:2-3` (`R40-CELL-02/03 … census/round-40/records/c2-after.txt|c3-after.txt@6ded124…`).
C1 checks only that those paths exist at the pinned revision and that the SCORECARD line cites the
revision — never their content. Consequence: if the C2/C3 receipts' contents were wrong, C1 would
still report a clean register; and deleting the C2/C3 instruments later cannot turn C1 red. The
preregistration's "independently measurable" holds for instruments, not for evidence data.

**F3 — substrate coupling.** All three claims read the same two tools: C1's register leg runs
`tools/souji-citation-reconcile.py` at REV (c1-counter.py:181), C2 audits both tools
(c2-counter.py:59-60), C3 mutates `tools/souji-worktree-drift.py` (c3-counter.py:144). File-level
separability coexists with substrate-level coupling: a drift-tool change moves C2 and C3 verdicts
together, and a citation-reconcile change moves C1 and C2 together. No harm observed — but the
claims are not independent of the substrate, only of each other.

**F4 — sharp edge hit live: an absolute `--register` path degrades to a clean-looking empty
register.** My first C1 invocation passed `--register "$S/base/census/round-40/cells.tsv"`
(absolute). `git show REV:/abs/path` fails, so `register_leg` returned `REGISTER-ABSENT`
(c1-counter.py:184-187) and the counter printed, with rc=1 only because of the floors:

```
REGISTER cells=0 mismatches=0 commit_rows=0 commit_hashes=0 violations=0 REGISTER-ABSENT
SUMMARY items=3 open=0 … register_cells=0 register_mismatches=0 register_violations=0 commit_rows=0 commit_hashes=0 …
c1-base-rc=1
```

Items still evaluated CLOSED while the register leg silently read nothing. With `--min-cells 0`
(non-default) this same invocation would exit 0 with `register_mismatches=0 register_violations=0`
— a vacuously clean register. This is the r39-carried, SKILL-documented contract ("A register
absent at a resolvable revision is not exit 2: it prints REGISTER-ABSENT", SKILL.md r39
`c1-counter` gate row), and the L1's receipt argv uses lane-relative paths, which resolve — so I
record it as a sharp edge, not a round-40 falsifier. All matrix rows above were re-run with
receipt-style relative paths.

**F5 — lane state note (context only).** `refs/heads/master` = `refs/remotes/origin/master` =
`994de3b` ("round-40: bind evidence path as well as revision; add path-substitution control"), one
commit AHEAD of the detached-HEAD closure revision, touching `census/round-40/c1-counter.py`
(+8/-2) and `tests/fixtures/r40-c1-evidence.py` (+9/-1); `git merge-base --is-ancestor` confirms
549d9ec IS an ancestor of 994de3b, and 994de3b/jj-keep commits are NOT ancestors of 549d9ec. All
verdicts here are pinned to the landed bytes at 549d9ec; the L1 should re-pin the matrix after that
amendment lands if it wants the master-bytes reading.

## Verdict

**SAFE** — for all three asked pairs and all three union readings: the first claim's frozen target
stays fully reachable (rc 0, output byte-equal to the full-tree baseline and to the committed
receipts) with the sibling claims' files absent from the work tree, and statically no counter or
fixture ever references a sibling instrument's path. Nothing FALSIFIED. The value of the matrix is
bounded by F1 (tree-separation by checkout alone is impossible; the demonstration is work-tree
pruning at 549d9ec) and qualified by F2/F3 (independence holds for instrument files, not for
receipt data or the shared substrate tools). INCONCLUSIVE for byte-level (history-absent)
separation, which would require a constructed deletion commit that seat rules forbid.

## Housekeeping

- Tools installed: none. Pacman: not run (paused host-wide). No mutating git/jj command was run in
  the lane or fleet repo; clones were `git clone` (read-only on the source) plus `git checkout
  --detach` inside my own scratch clones; file removals were plain `rm` inside those clones.
- Scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2connector03` (clones `base`, `P12`,
  `P12b`, `P13`, `P23`, `U1`, `U2`, `U3` and scratch work dirs under `w/`): **removed** before
  yielding (verified absent).
