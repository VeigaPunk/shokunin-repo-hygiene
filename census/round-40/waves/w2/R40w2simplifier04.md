# R40w2simplifier04 — dead-weight review of the round-40 landed bytes

Seat: R40w2simplifier04 (role simplifier, wave 2, falsify). Judged on: calibration.
Landed instrument commit attacked: `128e412b0ced3c243dc27c3dd3332054a611bc2e`.
Base: `0242085909fb6a4ee041c5443d76316ac6d59d4b`. Lane HEAD at review time: `549d9ec53a1f5932337ff14438fcd22b0621828d`
(later commits 8a5fbdb, 6ded124, 556c24a, 549d9ec changed C2 and C3 and added the data inputs; C1 and the three fixtures and the docstring analyser are byte-identical between 128e412 and HEAD). Every "landed" result below was produced from `git archive 128e412` extracted into scratch; HEAD was run only where marked "context".

## Verdict

**FALSIFIED** (on the text, on the landed C2 harness, and on the C3 attribution claim). The file-level question is **SAFE**: no file the round added is pure dead weight; every one is cited by a claim or is an input to a counter/fixture. The dead weight is *inside* the files: an unused import and an unused local, a dead CLI argument, duplicated constants/helpers across the counters and fixtures, and fixture cases that test one predicate three times.

Summary of attacked items:

| # | Attack | Verdict |
|---|---|---|
| A1 | Landed `c2-counter.py` cannot start (`ModuleNotFoundError`) | FALSIFIED |
| A2 | Landed C2 L1/L2/L5 arms cannot pass on any base tried (inverted discriminating arm; fixture rejects `--work`) | FALSIFIED |
| A3 | Landed C3 "prints the failing case names" — prints `failing=-` for every kill | FALSIFIED |
| A4 | Landed C3 `--base-rev` is accepted and resolved but never used to read bytes | FALSIFIED (dead arg, misleading CLI text) |
| A5 | Landed C1 forged control is optional; omitting `--forged` exits 0 | FALSIFIED (vacuous pass) |
| A6 | Landed C1 binds only the revision on the line, never the evidence path | FALSIFIED (text and contract) |
| A7 | Knowledge `git-strict-descendant-relation-r40.md:42-43`: "only first-parent ancestry is tested" | FALSIFIED |
| A8 | Knowledge `docstring-class-continuation-lines-r40.md:39-41`: "each pair's trigger must actually be raised" | FALSIFIED (class only is checked) |
| A9 | Lesson vs README/KB: "new ground the lane did not hold" vs "sit on ground the lane already held" | FALSIFIED (self-contradiction) |
| A10 | Dangling / untracked evidence pointers (`records/c1-fixture.txt`, `waves/w1/R40reviewer18.md`, `.ufo/l0-questions.md`) | FALSIFIED |
| A11 | C2 "r39 one-line analyser" control is not the r39 analyser | FALSIFIED (control not measured) |
| A12 | Lesson M40-1: "same mutants killed=no under the r39 contract" | FALSIFIED (never measured; r39 counter has no M15-M18) |
| A13 | Source quotes S252/S253 are not verbatim at the cited locations; PEP 257 quote misattributed to S252 | FALSIFIED |
| A14 | GVFS entry: "settles the READ side", "agrees with the specification" | FALSIFIED (overreach; not checked this round) |
| A15 | Duplicated logic across the counters and fixtures | FALSIFIED (as a simplicity finding; listed below) |
| A16 | Unused import / unused local in `c2-counter.py` | FALSIFIED (ruff F401, F841) |
| A17 | File-level dead weight (does any added file carry no claim?) | SAFE |
| A18 | Assimilation counts (177 / 134 / 58) and the collision set | SAFE |
| A19 | Source snapshot hashes (SHA256SUMS, 5/5) | SAFE |
| A20 | Landed C1 on its data (HEAD), landed C3 kill/pristine/base verdicts, landed fixture pass counts | SAFE on the stated predicate (attribution and control caveats above) |

## Setup (re-runnable)

```
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
L=128e412b0ced3c243dc27c3dd3332054a611bc2e
BASE=0242085909fb6a4ee041c5443d76316ac6d59d4b
DEF=ed30b7f5b77939c9073348d810730bc4f355708d
HEAD=549d9ec53a1f5932337ff14438fcd22b0621828d
S=/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier04
mkdir -p "$S/landed" "$S/run" && git -C "$LANE" archive "$L" census/round-40 census/round-39/c1-counter.py census/round-39/c3-counter.py tests/fixtures tools | tar -x -C "$S/landed"
```

No package was installed. The only binary used is the pre-existing `~/.local/bin/ruff` (0.17.2), run with `--isolated --no-cache` against scratch copies; nothing was written into `~/.local/bin`. No pacman, no git/jj mutation, no commit.

Byte checks on the landed tree:

```
$ git -C "$LANE" ls-tree -r --name-only "$L" | grep -c docstring_classes
0
$ git -C "$LANE" diff --stat "$L" HEAD -- census/round-40/c1-counter.py census/round-40/docstring-classes.py tests/fixtures
 census/round-40/c2-counter.py | 59 ++++++++++++++++++++++--------
 census/round-40/c3-counter.py |  4 +-
 (c1-counter.py, docstring-classes.py and the three fixtures: no change)
```

## File inventory: which added files carry a claim

The landed commit adds 24 files (`git show --stat 128e412`). None is unclaimed:

- `census/round-40/c1-counter.py`, `c2-counter.py`, `c3-counter.py`: the three claims (C1/C2/C3).
- `census/round-40/docstring-classes.py`: the C2 joined analyser (imported by the C2 counter in HEAD; by the fixture).
- `census/round-40/preregistration.txt`: the claims.
- `census/round-40/assimilation/{collisions,reg-ids,staged-ids}`: the counts cited in `corpus/lessons/round-40.md:43-44` (A18).
- `census/round-40/sources/{SHA256SUMS,codecs.html,git-merge-base.1.txt,gvfs-trashitem-1.62.0.c,inspect-cleandoc.txt,inspect.html}`: pinned bytes for S251-S254 (A19). Caveat in A13: the two HTML snapshots are cited for quotes that do not match them verbatim, so their claim is currently broken, not dead.
- `corpus/knowledge/{docstring-class-continuation-lines,drift-record-invalid-utf8,git-strict-descendant-relation,origin-record-format-gvfs}-r40.md`: four knowledge entries; each carries a claim (text overreach in A7, A8, A13, A14).
- `corpus/lessons/round-40.md`, `corpus/README.md`, `corpus/SOURCES.md`: lesson, frontier row, source rows (text overreach in A9, A12, A13).
- `tests/fixtures/r40-c1-evidence.py`, `r40-docstring-joined.py`, `r40-drift-record-branches.py`: C1/C2/C3 own tests (dead-weight inside, A15/A16).

Landed-bytes fixture runs (all reproduced from `$S/landed`):

```
$ cd "$S/landed" && python3 -B tests/fixtures/r40-drift-record-branches.py --tool "$S/landed/tools/souji-worktree-drift.py" --work "$S/run/fx-branches"
case-good=PASS ... case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0          rc=0
$ python3 -B tests/fixtures/r40-docstring-joined.py --analyzer "$S/landed/census/round-40/docstring-classes.py" --tool "$S/landed/tools/souji-worktree-drift.py"
SUMMARY cases=9 pass=9 fail=0          rc=0
$ ... r40-docstring-joined.py ... --one-line
case-frozen-pairs-present=FAIL missing=['RECORD-OUTSIDE-ROOT(--root)']
case-outside-root-trigger-primary=FAIL primary='a record row, or the gitdir it resolves to, escapes'
SUMMARY cases=9 pass=6 fail=3          rc=1
$ python3 -B tests/fixtures/r40-c1-evidence.py --counter "$S/landed/census/round-40/c1-counter.py" --base-counter "$S/landed/census/round-39/c1-counter.py" --work "$S/run/c1fx"
SUMMARY cases=8 pass=8 fail=0          rc=0
```

## A1 — landed C2 cannot start (FALSIFIED)

`census/round-40/c2-counter.py:46` (landed): `import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)`. The committed analyser is `census/round-40/docstring-classes.py` (hyphen); no `docstring_classes.py` exists at 128e412 (count 0 above).

```
$ cd "$S/landed/census/round-40" && python3 -B c2-counter.py --root "$LANE" --rev "$L" --base-rev "$BASE" --scratch "$S/run/c2-landed"
Traceback (most recent call last):
  File ".../c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
ModuleNotFoundError: No module named 'docstring_classes'
rc=1
```

Exit 1 with a traceback, not a `REFUSAL` (rc 2): the C2 receipt cannot be produced from its own commit.

## A2 — landed C2 legs cannot pass (FALSIFIED)

Diagnostic only: a scratch copy named `docstring_classes.py` was placed next to the landed counter to get past A1; nothing in the lane was touched.

```
$ python3 -B c2-counter.py --root "$LANE" --rev "$L" --base-rev "$BASE" --scratch "$S/run/c2-shim-tip"
LEG L1 FAIL new rc=2 class=True old rc=2 class=True
LEG L2 FAIL new rc=2 class=True old rc=2 class=True
LEG L3 PASS ...
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 FAIL new=None old(one-line)=None
LEG L6 PASS ...
SUMMARY legs=7 pass=4 fail=3 harm=0 ...   rc=1

$ python3 -B c2-counter.py --root "$LANE" --rev "$L" --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S/run/c2-shim-defect"
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS ...
LEG L4 FAIL pairs=3 ... missing_old=['RECORD-MALFORMED-missing-trigger(ENOENT)', 'RECORD-MISSING-missing-trigger(EACCES)'] ...
LEG L5 FAIL new=None old(one-line)=None
SUMMARY legs=7 pass=5 fail=2 harm=0 ...   rc=1
```

Causes, all in landed bytes:

- L1/L2 (`c2-counter.py:221-224`, `:232-234`): the "old" arm runs the citation reconciler at `--base-rev`. At the r39 tip, the reconciler already refuses `REFUSAL REV-UNRESOLVED: --rev` (`git show 0242085:tools/souji-citation-reconcile.py`, line 249), so `not old_has` is false and L1/L2 can never pass against the base the preregistration names. At the defect revision the refusal is absent (`git show ed30b7f:... | grep -c 'REFUSAL REV-UNRESOLVED: --rev'` → 0), which is why the L1 arm passes only there. The landed counter gives no way to name the defect revision.
- L4 at the defect base fails on `missing_old` (c2 requires triggers in the base doc, which the defect base lacks) — the leg is not base-neutral.
- L5 (`c2-counter.py:178-179`, `:292-293`): `run_fixture` always appends `--work`, and the fixture rejects it:

```
$ python3 -B tests/fixtures/r40-docstring-joined.py --analyzer "$S/landed/census/round-40/docstring-classes.py" --tool "$S/landed/tools/souji-worktree-drift.py" --work "$S/run/fx-branches"
r40-docstring-joined.py: error: unrecognized arguments: --work ...
rc=2
```

  and from a scratch copy with no arguments the fixture resolves its analyser relative to its own file location:

```
usage: unreadable analyzer .../census/round-40/docstring-classes.py / tool .../tools/souji-worktree-drift.py
```

Context only (HEAD, not landed): the later commit 8a5fbdb repairs all of this; `python3 -B c2-counter.py --root "$LANE" --rev "$HEAD" --base-rev 0242085...` at HEAD prints `SUMMARY legs=7 pass=7 fail=0 harm=0`. The landed bytes are nonetheless falsified: no configuration passes on them.

## A3 — landed C3 kill attribution is empty (FALSIFIED)

`census/round-40/c3-counter.py:116-117` (landed):

```
failing = [l.split("=", 1)[0][5:] for l in proc.stdout.splitlines() if l.startswith("case-")
           and l.endswith("FAIL")]
```

The fixture prints `case-<name>=FAIL rc=... missing=...` — the line ends with the detail, not `FAIL`.

```
$ cd "$S/landed/census/round-40" && python3 -B c3-counter.py --root "$LANE" --rev "$L" --base-rev "$BASE" --scratch "$S/run/c3-landed"
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 ...
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- ...
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- ...
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- ...
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
rc=0
```

The docstring (`c3-counter.py:22-27`, landed) says "prints the failing case names so a kill is attributable to the branch case that covers it." At landed, `failing=-` for all four kills. The kill verdicts themselves (4/4, pristine ok, base_killed=0) are SAFE; the attribution claim is FALSIFIED. HEAD (`c3-counter.py:116-117` at 8a5fbdb+) uses `"=FAIL" in l.split(" ", 1)[0]` and is the repair.

## A4 — landed C3 `--base-rev` is dead (FALSIFIED, dead argument)

`census/round-40/c3-counter.py` landed: `--base-rev` is `required=True` (line 127), validated (`for flag, rev in (("--rev", args.rev), ("--base-rev", args.base_rev))`, line 133), and never read again. The base fixture is read from `--rev`:

```
146:        base_src = git_show(args.root, args.rev, args.base_fixture)
```

The CLI text (`c3-counter.py:30`, landed) documents `--base-rev REV` as an input to the base comparison. Since the verdict (`base_killed`) reads the base fixture at the candidate revision, the argument is dead and the usage text is misleading. (Remove the argument or read the base fixture at `--base-rev`; do not keep both.)

## A5 — landed C1 forged control is optional (FALSIFIED, vacuous pass)

`census/round-40/c1-counter.py:286` `if args.forged:` and `:351` `ap.add_argument("--forged")`; the exit predicate (`:335-342`) checks `open_count == 0 and forged_closed == 0` but never requires forged rows to exist.

```
$ cd "$S/landed/census/round-40" && python3 -B c1-counter.py --root "$LANE" --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items "$S/c1/items.tsv" --register census/round-40/cells.tsv --register-rev 549d9ec53a1f5932337ff14438fcd22b0621828d --scratch "$S/run/c1-head" | tail -1
SUMMARY items=3 open=0 forged=0 forged_open=0 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 ... forged_sha=-
rc=0
```

The preregistration's C1 target requires "the forged token-only item remains OPEN"; a run with no forged file reports zero forged items and exits 0. Fix by requiring `len(forged) >= 1` (or making `--forged` mandatory).

## A6 — landed C1 binds the revision, not the evidence path (FALSIFIED)

`c1-counter.py:251-259` (landed = HEAD for this file): the bound check is `any(evidence_rev.lower() in line.lower() for line in good)`. The evidence *path* is checked only for existence at the revision (`:256`); it is never required on the line. Rule 6 in the docstring (`:24`) says "the closing line itself cites the evidence revision"; nothing requires it to cite the file.

Scratch repo (`git -C "$D" init`, toplevel verified equal to `$D`), commit `c1` adds `other.txt` (unrelated) and `claim.txt` with `CLAIM-A rows=5 status=ok`; commit `c3` rewrites the line to `CLAIM-A rows=5 status=ok  (cites <c1 sha>)`. Item: `BARE-CITE  claim.txt  CLAIM-A  rows=5  -  other.txt@<c1 sha>`.

```
$ python3 -B c1-counter.py --root "$D" --rev "$C3" --items "$S/run/bare-items.tsv" --register reg.tsv --register-rev "$C3" --scratch "$S/run/bare-run"
ITEM BARE-CITE CLOSED
REFUSAL COULD-NOT-EVALUATE: tools/souji-citation-reconcile.py absent at ...   (rc=2: my scratch repo has no reconciler; the item verdict above is the point)
```

Same item with the line not citing the sha (`rev=C1`): `ITEM NOCITE OPEN EVIDENCE-NOT-BOUND <c1>` — SAFE for that branch. So a line that cites any ancestor commit and any existing file closes the item; the path is never bound. The lesson's frontier (`corpus/lessons/round-40.md:98-101`) names the gap only as "does not yet require the evidence to be the receipt's own revision" — understated.

## A7 — knowledge: "first-parent ancestry only" is false (FALSIFIED)

`corpus/knowledge/git-strict-descendant-relation-r40.md:42-43`: "Only ancestry through the first parent chain is tested; a merge commit's other parent is not examined."

Scratch repo `$S/run/fp-repo`: `A` on main, `B` on `side` (only reachable through merge `M`'s second parent), merge `M`.

```
$ git -C "$FP" rev-list --parents -n1 "$M"   →  M  <first parent>  B   (B is the second parent)
$ git -C "$FP" rev-list --first-parent "$M" | grep -c "$B"   →  0
$ git -C "$FP" merge-base --is-ancestor "$B" "$M"; echo rc=$?   →  rc=0
```

`git merge-base --is-ancestor` walks the full DAG; the landed register leg calls it at `c1-counter.py:225` and `:229`. A second-parent commit is therefore accepted as "inside the audited history". Either the limit goes or the counter adds a first-parent check; the sentence as written is false.

## A8 — knowledge: "each pair's trigger must actually be raised" is false (FALSIFIED)

`corpus/knowledge/docstring-class-continuation-lines-r40.md:39-41`: "The C2 counter's L4 leg re-derives the class/trigger pairs at run time — each pair's trigger must actually be raised by the audited tool — so a pair the tool no longer raises fails the leg instead of passing vacuously."

The landed `observed_pairs` (`c2-counter.py:153-177`) classifies only the refusal class (`classify` returns `RECORD-*` names). The trigger tokens are never looked up at runtime. Probes on the landed drift tool (run as uid 1000):

```
$ python3 -B "$S/landed/tools/souji-worktree-drift.py" --root "$S/run/probe" --record "$S/run/probe/absent.tsv" --timeout 20
REFUSAL RECORD-MALFORMED: .../absent.tsv is not a regular file        (no "ENOENT" in output)
$ ... --record "$S/run/probe/record-probe.tsv"        # chmod 0
REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '...'           (no "EACCES" in output)
$ ... --record "$S/run/probe/outside.tsv"             # REPO ../escape
REFUSAL RECORD-OUTSIDE-ROOT: ../escape resolves outside .../probe       (no "--root" in output)
```

The class is raised; the trigger token is not. The check is a substring match of the trigger against the docstring entry (`docstring-classes.py`, `fixture:73-78`), so "trigger documented" is verified and "trigger raised" is not. The chmod-0 probe also depends on uid != 0 (as root the probe would read and the leg would report `RECORD-MISSING-not-raised`). Reword to "class raised; trigger documented", and state the uid dependency.

## A9 — lesson contradicts itself and the README (FALSIFIED)

- `corpus/lessons/round-40.md:31-32` (Gate): "Ground: F4, a second reference implementation that only READS the per-item origin record — new ground the lane did not hold."
- `corpus/knowledge/origin-record-format-gvfs-r40.md:28-31`: "That cross-check is the new ground".
- `corpus/lessons/round-40.md:96-97` (Frontier): "the four new knowledge entries sit on ground the lane already held".
- `corpus/lessons/round-40.md:118` and `corpus/README.md` Round 40 frontier update: "All four sit on ground the lane already held".

Both cannot hold. Pick one.

## A10 — dangling and untracked evidence pointers (FALSIFIED)

Checked at 128e412 (`git cat-file -e "$L:$p"`), at HEAD, and in the worktree (`test -e`):

- `census/round-40/records/c1-fixture.txt` — cited at `corpus/knowledge/git-strict-descendant-relation-r40.md:32` and `corpus/knowledge/docstring-class-continuation-lines-r40.md:38`. Absent at landed, at HEAD and in the worktree.
- `census/round-40/waves/w1/R40reviewer18.md` — cited at `corpus/lessons/round-40.md:55`. Not in the landed commit; present in the worktree only as an untracked file (`git ls-files --error-unmatch` → "Did you forget to 'git add'?").
- `.ufo/l0-questions.md` — cited at `corpus/lessons/round-40.md:47` and `corpus/knowledge/origin-record-format-gvfs-r40.md:54`. Absent (`test -e` → MISSING).

## A11 — the C2 "r39 one-line analyser" control is not the r39 analyser (FALSIFIED)

Preregistration C2 control: "r39 `docstring_classes` extracts only the first class line." The landed counter's one-line reading is the *r40 module's* `first_line_entries` (`census/round-40/docstring-classes.py:78-80`, `_entries(doc, False)`), not the r39 function. I extracted the r39 function (`git show 0242085:census/round-39/c2-counter.py`, `def docstring_classes(tool)` at line 133) by AST, and ran it on the landed drift-tool bytes next to the r40 reading:

```
r39 classes: ['RECORD-MALFORMED', 'RECORD-MISSING']
r40 first-line classes: ['JSON-HARDLINKED', 'JSON-INSIDE-MEASURED-TREE', 'JSON-IS-RECORD', 'JSON-NOT-REGULAR', 'JSON-UNWRITABLE', 'RECORD-EMPTY', 'RECORD-MALFORMED', 'RECORD-MISSING', 'RECORD-OUTSIDE-ROOT']
same keys: False
```

So the control that L4/L4b/L5 and the fixture's `--one-line` measure is a different function from the one the preregistration names, and the r39 function misses far more than the wrapped trigger. Either measure the r39 function or rename the control (the "one-line" mode is a re-implementation, not the r39 reading). The joined analyser itself is SAFE: fixture 9/9, and HEAD C2 L4b `joined=True one_line=False`.

## A12 — lesson M40-1 contrast was never measured (FALSIFIED)

`corpus/lessons/round-40.md:71-73`: "the r40 battery's four mutants are scored `killed=yes` under the repaired contract while the same mutants are `killed=no` under the r39 contract (the seat's K1/K2 pair is reproduced by the r40 counter's own output …)."

- The r39 counter scores only M11-M14: `git show 0242085:census/round-39/c3-counter.py` lines 7-11 and MUTANTS at 51-57. M15-M18 are never scored under r39.
- The r40 counter has no r39-contract mode (`grep -n "K1\|K2\|r39" c3-counter.py` → only docstring references).
- The "failing case names printed" part is false at landed (A3).

## A13 — source quotes: verbatim checks and the PEP 257 attribution (FALSIFIED)

Checked on the pinned snapshots (`census/round-40/sources`), tags stripped, whitespace folded:

```
inspect.html            "Any whitespace that can be uniformly removed from the second line onwards is removed" -> False
                        actual: "All leading whitespace is removed from the first line.  Any leading whitespace that can be
                                 uniformly removed from the second line onwards is removed."
inspect-cleandoc.txt    the same sentence -> True   (installed interpreter docstring, lines 4-5)
codecs.html             "Replace with a replacement marker. On decoding, use U+FFFD, the official REPLACEMENT CHARACTER" -> False
                        actual: "Replace with a replacement marker. On encoding, use ? (ASCII character). On decoding, use
                                 � (U+FFFD, the official REPLACEMENT CHARACTER)."
git-merge-base.1.txt    "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true,
                         or with status 1 if not" -> present (lines 41-43; checker false-negative from tag-stripping `<commit>`)
gvfs-trashitem-1.62.0.c line 158 quote -> present verbatim (SAFE)
```

Affected text: `corpus/lessons/round-40.md:15-18` (S252, S253 "located quote"), `corpus/SOURCES.md` S252/S253 rows, `corpus/knowledge/docstring-class-continuation-lines-r40.md:12`, `corpus/knowledge/drift-record-invalid-utf8-r40.md:10-11`. The lesson's table says "located quote (<=25 words)"; for S252 the verbatim sentence is in the interpreter docstring, not the cited docs page; for S253 the quoted string does not occur in the page. The semantic claims survive; the quotes do not.

PEP 257: `census/round-40/docstring-classes.py:18-20` says "PEP 257 (S252, opened 2026-10-28) is the shape this analyser follows … 'the continuation lines ... should be joined' to form the summary." S252 is `inspect.cleandoc` (SOURCES row), not PEP 257; the lesson says PEP 257 was "screened and NOT cited" (`corpus/lessons/round-40.md:20-23`). The quoted phrase (split across the lines 19-20) is in no pinned snapshot (`tr '\n' ' '` + grep over `census/round-40/sources/*` finds none). Same misattribution at `tests/fixtures/r40-docstring-joined.py:11` and `census/round-40/c2-counter.py:10` (landed line 10 says "PEP 257's").

## A14 — GVFS entry overreach (FALSIFIED)

`corpus/knowledge/origin-record-format-gvfs-r40.md`:

- `:22-23` "For souji this settles the READ side of the per-item origin record" — one reader cannot settle a record format; the entry itself says "Not normative" (`:39-40`).
- `:28-31` "it agrees with the specification rather than replacing it" — S022 was not opened or compared this round. Unobserved, not evidence.
- `:22-23` "a record must carry the original path in ESCAPED form, the deletion date, and the base directory" — a `must` derived from one reader's behaviour.

Lines 158, 173, 180, 182, 193 of the snapshot were checked and are accurate (SAFE for the citation itself).

`corpus/knowledge/docstring-class-continuation-lines-r40.md:11-12`: "Python's own `inspect.cleandoc` documents exactly this reading" — cleandoc documents whitespace removal, not class-entry joining. Overreach.

## A15 — duplicated logic across counters and fixtures (FALSIFIED as simplicity)

Landed line numbers:

- `REV = re.compile(...)` and the `GIT_ENV` dict (identical content): `c1-counter.py:55-64`; `c2-counter.py:48-58`; `c3-counter.py:45-54`.
- `child_env` / `git` / `git_show` / `resolves` (or `git_resolves`): `c1-counter.py:67-91` (`child_env` 67, `git` 73, `git_show` 83, `git_resolves` 90); `c2-counter.py:88-114` (`child_env` 88, `git` 96, `git_show` 106, `resolves` 113); `c3-counter.py:72-93` (`child_env` 72, `git_show` 79, `resolves` 89). Three near-identical copies; they differ only in the `TMPDIR` handling.
- The `SUMMARY cases=(\d+) pass=(\d+) fail=(\d+)` parse: `c2-counter.py:182` (`run_fixture`); `c3-counter.py:108-111` and `:168-172` (`score`, and the pristine check).
- `FROZEN_PAIRS` and `SYNTHETIC_DOC` are duplicated between the C2 counter and the fixture: `c2-counter.py:74-78` & `:80-85` vs `tests/fixtures/r40-docstring-joined.py:27-31` & `:33-38`. HEAD additionally duplicates the `importlib` analyser loader (`c2-counter.py:128-142` at HEAD vs `fixture:41-47`).
- `r40-docstring-joined.py` predicates are redundant: `case-outside-root-trigger-primary` (`:79-81`), `case-record-missing-eacces` (`:82-84`), `case-record-malformed-enoent` (`:85-87`) assert exactly what `case-frozen-pairs-present` (`:73-78`) asserts. The `--one-line` output shows it: `case-frozen-pairs-present=FAIL` and `case-outside-root-trigger-primary=FAIL` for the same missing `--root`.

A shared helper module for the counters would remove the first three items; the duplicated FROZEN_PAIRS should be imported from one place, or the fixture should drop the three redundant cases.

## A16 — dead code in `c2-counter.py` (FALSIFIED)

```
$ ~/.local/bin/ruff check --no-cache --isolated --select F c1-counter.py c2-counter.py c3-counter.py docstring-classes.py ../../tests/fixtures/r40-*.py --output-format concise   # in $S/landed copies
c2-counter.py:35:8: F401 `ast` imported but unused
c2-counter.py:256:9: F841 Local variable `old_first` is assigned to but never used
Found 2 errors.   rc=1
```

The other six files are F-clean. `old_first` is computed (`c2-counter.py:256`) and never read; `ast` (`:35`) is imported and unused.

Also: `--base-rev` in C3 (A4) is dead.

Minor, reading-only, not exercised: `c1-counter.py:240` matches anchors by substring (`row["anchor"] in line`), so `R40-CLAIM-D1` also matches a line carrying `R40-CLAIM-D10`; scratch defaults fall back to `/var/tmp` (`c1-counter.py:297`, `c2-counter.py:202`, `c3-counter.py:74`, `:139`); C3 `subprocess.run` calls have no timeout (`c3-counter.py:103`, `:163`), so a hanging mutant hangs the counter.

## A17 — file-level dead weight (SAFE)

No file the round added is unclaimed. The inventory in "File inventory" above maps every file to a claim, a counter input, or a pinned source. The HTML snapshots are the nearest to dead (221 KB and 181 KB for one quoted sentence each), and A13 shows their quotes do not match, so they are currently cited for the wrong text rather than being unused.

## A18 — assimilation counts and collisions (SAFE)

```
$ cd "$LANE/census/round-40/assimilation" && wc -l reg-ids staged-ids collisions
 177 reg-ids
 134 staged-ids
  58 collisions
$ comm -12 <(sort reg-ids) <(sort staged-ids) | wc -l
58
$ comm -12 <(sort reg-ids) <(sort staged-ids) | cmp - <(sort collisions) && echo same
same
```

The counts cited in `corpus/lessons/round-40.md:43-44` match. The per-document claim ("every collision is a DIFFERENT document") is not checkable in-lane: the package `merge/souji/` is outside the lane. Only the lane side (S109 = RENAME_NOREPLACE probe, `corpus/SOURCES.md:136`) was confirmed.

## A19 — source snapshot hashes (SAFE)

```
$ cd "$LANE/census/round-40/sources" && sha256sum -c SHA256SUMS
codecs.html: OK
git-merge-base.1.txt: OK
gvfs-trashitem-1.62.0.c: OK
inspect-cleandoc.txt: OK
inspect.html: OK
```

## A20 — the landed predicates on their own data (SAFE, with caveats above)

- C1 on HEAD data (items, forged, cells from HEAD via `git show`, audited at HEAD): three items CLOSED, three forged OPEN (`EVIDENCE-NOT-BOUND`, `EVIDENCE-REV-UNRESOLVED`, `EVIDENCE-NOT-ANCESTOR`), register `cells=3 mismatches=0 violations=0`, `rc=0`. Note the item/forged/cell inputs are NOT in the landed commit (added at 6ded124 and 556c24a); at 128e412 itself the same counter reports `ANCHOR-ABSENT` and `NOT-ANCESTOR-OF-REV` (data postdates the landed rev).
- C1 fixture `r40-c1-evidence.py` 8/8 at landed (its `register-equal-rejected` and `register-backwards-rejected` cases exist and pass).
- C3 landed: pristine ok, four kills, base_killed=0 (see A3 for attribution).
- Fixtures: branches 8/8, docstring-joined 9/9 (one-line 6/9 — the wrapped-trigger probe is missed by the one-line reading, as claimed).
- The drift tool's record decoding matches the knowledge entry: `census/round-40` cites `tools/souji-worktree-drift.py:143-147` (`os.read(fd, 65536)` chunks joined before one `decode("utf-8", "replace")`), so a byte split across a 64 KiB boundary decodes as one stream, as `corpus/knowledge/drift-record-invalid-utf8-r40.md:45-47` says.

## Actions for the L1 (no edits made by this seat)

1. C2: fix the import name or the file name; pass the defect revision as the discriminating base; stop appending `--work` to the fixture or accept it in the fixture; resolve the analyser path from `--root`/`--rev`, not from the fixture's location.
2. C3: parse the failing case names with `"=FAIL" in l.split(" ", 1)[0]`; drop `--base-rev` or use it.
3. C1: require at least one forged row; require the evidence path (or a path token) on the closing line; correct the first-parent sentence.
4. Knowledge/lesson text: fix the quoted sources (S252 to the interpreter docstring or the page's "Any leading whitespace" sentence; S253 to the page's exact sentence); remove the PEP 257 attribution to S252; reword "trigger must actually be raised" to "class raised, trigger documented"; reconcile "new ground" vs "already held"; remove "settles the READ side" and "agrees with the specification"; remove the "killed=no under the r39 contract" claim unless measured; create or remove the dangling pointers (`records/c1-fixture.txt`, `.ufo/l0-questions.md`) and add `waves/w1/R40reviewer18.md` to the commit or drop the pointer.
5. Dead code: remove `import ast` and `old_first` from `c2-counter.py`; collapse the three duplicate fixture cases; share `REV`/`GIT_ENV`/git helpers.

## Scratch

Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier04` was used for the landed extraction, the fixture repos, the shim copies and the probe repos. It was removed in full with `rm -rf -- "$S" && test ! -e "$S"`: **removed**. The report itself is the only file written in the lane.
