# R40mutationtester08 — C2 (operability): the frozen r40 L4 leg has **no reachable
# observed-class/trigger set** at the frozen base, and the r39 leg it inherits produces a
# **concrete FALSE PASS** on a demonstrably wrong mapping

- Seat: `R40mutationtester08` (role mutation-tester; leaf member — no subagent dispatch)
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen claim attacked: **C2 — operability**, `census/round-40/preregistration.txt:8`
- Base branch revision named by the prereg: `0242085909fb6a4ee041c5443d76316ac6d59d4b`
  (r39 verified tip). r39 control base: `ed30b7f5b77939c9073348d810730bc4f355708d`.
- Lane tip at measurement: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`
- Tool installs/upgrades: **none**. `pacman` untouched; no network fetch; nothing written to any
  `PATH` directory. Interpreter `Python 3.14.8`, `git 2.56.0`.
- Lane writes: **this report only**. No lane file, git/jj index, or config was mutated; no commit
  and no push was made by this seat. `git status --porcelain` in the lane shows the untracked
  `census/round-40/` (pre-existing, not mine) plus untracked files under `tests/fixtures/`
  written by sibling C1/C2 seats during this wave — **none of them is mine**; this seat wrote no
  file under `tests/` and created no file in the lane other than this report.
- Scratch: `/fast/scratch/hyaku/souji-r40/R40mutationtester08/` — all work; `TMPDIR` set explicitly
  on every child; removed before yield (§12).

## 0. Verdict in one line

**The frozen r40 C2 predicate is not falsifiable as written, and the falsifier is concrete:
the r40 base bytes already satisfy the joined-analyzer predicate over every reachable class, so
the L4 leg has no base/candidate separation left to measure — while the r39 leg it inherits
(`classify()` + `docstring_classes()`) produces a verified **FALSE PASS** on a candidate whose
docstring mapping is wrong, triggered by nothing more than a path name.**

---

## 1. Named distinct edge case (item 8, explicit)

Every other mutation-tester in this wave attacks the C2 leg's **analyzer** — how the docstring
lines are parsed or joined (`R40mutationtester20`: trigger-side token semantics; `R40mutationtester32`:
the join's termination rule; `R40mutationtester44`: join-widening monotonicity; `R40mutationtester56`:
the observation channel's path contamination).

**Item 8 = the OBSERVED-SET COVERAGE of the L4 leg — the product of two independent inherited
artifacts that the frozen predicate names nowhere:**

> **(a) the PROBE SET** — which refusal paths the counter actually triggers, and
> **(b) the CLASSIFIER's TOKEN LIST** — which class tokens the observed-class reader can
> recognise at all.

The frozen predicate says the r40 analyzer "verifies **all observed class/trigger pairs in the
frozen list**" and kills "if **any observed class mapping disagrees with runtime behavior**".
"Observed" and "the frozen list" are both products of (a) and (b). Neither is named in
`census/round-40/preregistration.txt`, and **no frozen list exists anywhere in the lane**:
`census/round-40/` contains exactly one file, `preregistration.txt` (2299 bytes), and
`git ls-files census/round-40` is empty (the directory is untracked at HEAD).

**The concrete consequence, measured below:** at the frozen r40 base the reachable class set is
**10**, the inherited `classify()` can recognise only **4** of them, the inherited probe set
observes only **2**, and **both of those 2 carry their trigger on the first line** — so the r40
analyzer's *join* is exercised by **zero** real classes at the base. The leg's entire
discriminating power therefore rests on a **synthetic probe the counter's own author writes**, and
on a **trigger vocabulary that is not frozen** (changing the trigger string flips the verdict on
the *same* committed bytes).

---

## 2. Instrument and byte identity (read-only; nothing mutated)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin
$ git log --oneline -3
be4cb61 round-39 verifier spot-check (integrator, hyaku): non-author admit/reject
0242085 round-39: lesson — carry entry names its resolution token
c2dcd62 round-39: lesson — Seat-reported failures carry for W1CritAssimilation (LG-SEAT-UNCARRIED)
$ git cat-file -e 0242085909fb6a4ee041c5443d76316ac6d59d4b^{commit} && echo YES
YES
```

Committed bytes under test (extracted with `git show`, never from the worktree):

| artifact | revision | sha256 |
|---|---|---|
| `tools/souji-worktree-drift.py` | `0242085` (r40 base) | `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` |
| `tools/souji-worktree-drift.py` | `ed30b7f` (r39 base) | `14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194` |
| `census/round-39/c2-counter.py` | `0242085` | `732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11` |

```
$ sha256sum census/round-39/c2-counter.py tools/souji-worktree-drift.py
732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11  census/round-39/c2-counter.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
```
(identical to the `git show` extractions above — the worktree copy and the committed bytes agree.)

---

## 3. The inherited r39 machinery, verbatim

`census/round-39/c2-counter.py:125-131` — the observed-class reader:

```python
def classify(proc):
    out = (proc.stdout + proc.stderr).replace("\n", " ")
    for cls in ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT"):
        if cls in out:
            return cls
    return "NO-CLASS"
```

`census/round-39/c2-counter.py:133-144` — the control analyzer the r40 predicate keeps as its
"control" (`"r39 docstring_classes extracts only the first class line"`):

```python
def docstring_classes(tool):
    ...
    for line in doc.split("\n"):
        stripped = line.strip()
        for cls in ("RECORD-MISSING", "RECORD-MALFORMED"):
            if stripped.startswith(cls) and cls not in out:
                out[cls] = stripped
    return out
```

`census/round-39/c2-counter.py:223-238` — the L4 leg the r40 leg must improve:

```python
missing = classify(run_drift(new_drift, root, os.path.join(base_scratch, "absent.tsv")))
os.chmod(probe, 0)
locked = classify(run_drift(new_drift, root, probe))
...
new_ok = (
    missing in new_classes and "missing" in new_classes.get(missing, "").lower()
    and locked in new_classes and "EACCES" in new_classes.get(locked, "")
)
...
leg("L4", new_ok and not old_ok, detail + " new_maps=%s old_maps=%s" % (new_ok, old_ok))
```

**Three facts about that inherited machinery drive every result below:**

1. `classify()` is a **priority-ordered substring scan** over `stdout+stderr` — not an anchored
   parse of the tool's own `REFUSAL <CLASS>:` banner.
2. `classify()`'s token list is **four tokens**: `RECORD-MISSING`, `RECORD-MALFORMED`,
   `RECORD-EMPTY`, `RECORD-OUTSIDE-ROOT`. The `JSON-*` and `USAGE` classes are not in it.
3. The L4 probe set is **two paths**: an absent path and a `chmod 0` path. Nothing else is probed.

---

## 4. Measurement A — the reachable class set at the frozen base (10), and what the inherited
artifacts can and cannot observe

Every refusal path of the committed r40-base tool was driven directly
(`probe.py`/`battery.py`, scratch copies only):

```
$ python3 -B battery.py $S/drift-r40base.py $S/run-base
=== OBSERVED runtime classes (drift-r40base.py) ===
  missing-path               -> RECORD-MALFORMED
  unreadable-path            -> RECORD-MISSING
  eloop-path                 -> RECORD-MISSING
  empty-record               -> RECORD-EMPTY
  row-outside-root           -> RECORD-OUTSIDE-ROOT
  root-not-a-directory       -> USAGE
  json-is-record             -> JSON-IS-RECORD
  json-inside-measured-tree  -> JSON-INSIDE-MEASURED-TREE
  json-not-regular           -> JSON-NOT-REGULAR
  json-hardlinked            -> JSON-HARDLINKED
  json-unwritable            -> JSON-UNWRITABLE
```

Raw stderr for two of them (the tool's own banner is unambiguous — the reader is what is weak):

```
REFUSAL RECORD-MALFORMED: /fast/scratch/.../absent.tsv is not a regular file
REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '/fast/scratch/.../probe.tsv'
```

**Reachable = 10 classes. Coverage of the two inherited artifacts:**

| artifact | covers | misses |
|---|---|---|
| `classify()` token list (4 tokens) | `RECORD-MISSING`, `RECORD-MALFORMED`, `RECORD-EMPTY`, `RECORD-OUTSIDE-ROOT` | **6 of 10**: `JSON-HARDLINKED`, `JSON-INSIDE-MEASURED-TREE`, `JSON-IS-RECORD`, `JSON-NOT-REGULAR`, `JSON-UNWRITABLE`, `USAGE` |
| inherited L4 probe set (2 paths) | `RECORD-MALFORMED`, `RECORD-MISSING` | **8 of 10**: the 6 above plus `RECORD-EMPTY`, `RECORD-OUTSIDE-ROOT` |

```
$ python3 -B battery8.py
=== 2. the INHERITED classify() token list (census/round-39/c2-counter.py:125) ===
  classes it CANNOT observe (6/10): JSON-HARDLINKED, JSON-INSIDE-MEASURED-TREE,
      JSON-IS-RECORD, JSON-NOT-REGULAR, JSON-UNWRITABLE, USAGE
=== 3. the INHERITED r39 L4 probe set (c2-counter.py:223,225) ===
  measured: ['RECORD-MALFORMED', 'RECORD-MISSING']
  classes the tool can raise but the inherited probe set never observes (8): ...
```

**This is the first measured consequence of item 8: the frozen predicate's phrase "all observed
class/trigger pairs" is evaluated over a set that is 2 classes wide under the inherited
instruments, while the tool can raise 10.** The predicate never says which set is meant.

---

## 5. Measurement B — at the frozen base, the join is exercised by **zero** real classes, and
the r40 base already PASSES the all-scope joined predicate

```
$ python3 -B battery3.py
=== r40base (0242085909fb) sha256=e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
  scope=r39pair  one-line(all)  FAIL RECORD-OUTSIDE-ROOT:lacks '--root'
  scope=r39pair  joined indent  PASS
  scope=all      one-line(all)  FAIL JSON-INSIDE-MEASURED-TREE:lacks 'measured repository';
                                     JSON-IS-RECORD:lacks 'same inode';JSON-NOT-REGULAR:lacks 'FIFO';
                                     JSON-UNWRITABLE:lacks 'O_NOFOLLOW'
  scope=all      joined indent  PASS
```

Two results follow.

**(B1) The base bytes already satisfy the joined analyzer over every reachable class.**
`scope=all  joined indent  PASS` on the *base* bytes. The frozen measurement is
"r40 counter receipt comparing base and candidate bytes" — but the base arm of the joined
comparison is already `PASS`. There is no base/candidate separation left on the tool bytes for
this predicate to measure: **any candidate that leaves the tool's docstring unchanged is
indistinguishable from the base under the joined analyzer.**

**(B2) The join has no real subject.** Under the inherited probe set the only two observed
classes are `RECORD-MALFORMED` (trigger `missing`) and `RECORD-MISSING` (trigger `EACCES`), and
**both triggers sit on the class line itself** — the r39 one-line analyzer already passes them:

```
=== 4. THE JOIN IS EXERCISED BY ZERO REAL CLASSES AT THE r40 BASE ===
  RECORD-MALFORMED   trigger='missing'  on FIRST line: True -> the one-line analyzer already passes it
  RECORD-MISSING     trigger='EACCES'   on FIRST line: True -> the one-line analyzer already passes it
```

The five classes whose triggers are **wrapped-only** (first line lacks them) are exactly the ones
the inherited probe set never observes:

```
=== which trigger tokens live ONLY on a wrapped continuation line? ===
  JSON-INSIDE-MEASURED-TREE    trigger='measured repository'  first-line=False joined=True  WRAPPED-ONLY
  JSON-IS-RECORD               trigger='same inode'            first-line=False joined=True  WRAPPED-ONLY
  JSON-NOT-REGULAR             trigger='FIFO'                  first-line=False joined=True  WRAPPED-ONLY
  JSON-UNWRITABLE              trigger='O_NOFOLLOW'            first-line=False joined=True  WRAPPED-ONLY
  RECORD-OUTSIDE-ROOT          trigger='--root'                first-line=False joined=True  WRAPPED-ONLY
```

So the r40 analyzer's new capability — the *join* — is exercised by **five classes that the
inherited probe set never triggers**, and **four of those five** (`JSON-INSIDE-MEASURED-TREE`,
`JSON-IS-RECORD`, `JSON-NOT-REGULAR`, `JSON-UNWRITABLE`) are classes the inherited `classify()`
cannot even name (`RECORD-OUTSIDE-ROOT` is in its token list but is likewise never probed). The
r40 leg must therefore add *both* a wider classifier *and* a wider probe set for the join to mean
anything; the frozen predicate mandates the join and none of the rest.

**Consequence, measured:** a mutant that deletes **six** of the tool's ten refusal-class docstring
entries (all `JSON-*` plus `USAGE`) is **invisible** to the inherited leg, which reports the same
verdict for it as for the pristine bytes — while the all-scope joined detector separates them:

```
=== 5. A MUTANT THAT DELETES 6 ENTRIES STILL PASSES THE INHERITED PREDICATE ===
  mutant: the six JSON-*/USAGE docstring entries are DELETED from the tool bytes.
  the runtime is unchanged (the tool still raises all six classes).
  runtime still raises: ['JSON-HARDLINKED', ..., 'USAGE']
  pristine r40 base          inherited L4 leg: missing=RECORD-MALFORMED locked=RECORD-MISSING new_ok=True
  mutant (6 entries deleted) inherited L4 leg: missing=RECORD-MALFORMED locked=RECORD-MISSING new_ok=True
  -> the inherited leg reports the SAME verdict for the pristine bytes and for
     a tool whose docstring lost six of its ten refusal-class entries.
=== 6. THE FULL-SCOPE JOIN does catch the mutant (the fix) ===
  pristine r40 base          all-scope joined: PASS
  mutant (6 entries deleted) all-scope joined: FAIL JSON-HARDLINKED:NO-ENTRY;JSON-INSIDE-MEASURED-TREE:NO-ENTRY;...
```

---

## 6. Measurement C — the trigger vocabulary is not frozen, and it flips the verdict on the
**same** committed bytes

The frozen predicate says "verifies all observed class/trigger pairs **in the frozen list**".
No such list exists in the lane (§1), so the trigger string for each class is the counter
author's free choice. That choice decides whether the one-line control "misses" the trigger:

```
=== E6 trigger-choice flip on the SAME base bytes (RECORD-MISSING) ===
      trigger='EACCES'                   one-line=True  joined=True
      trigger='ELOOP'                    one-line=True  joined=True
      trigger='cannot be opened or read' one-line=False joined=True
      trigger='cannot be read'           one-line=False joined=False
=== E6 trigger-choice flip (RECORD-MALFORMED) ===
      trigger='missing'                  one-line=True  joined=True
      trigger='ENOENT'                   one-line=True  joined=True
      trigger='does not match the schema' one-line=False joined=True
      trigger='not a regular file'       one-line=False joined=False
```

**For `RECORD-MISSING` and `RECORD-MALFORMED` — the only two classes the inherited probe set
observes — every natural trigger token sits on the first line**, so the r39 one-line control
*passes* and the frozen predicate's "the r39 one-line analyzer misses it" cannot be satisfied by
the real bytes at all. Only a synthetic probe, or one of the never-observed wrapped classes,
separates the two analyzers. And `trigger='not a regular file'` / `'cannot be read'` are tokens
that appear in **neither** the first line nor the joined entry of their own class — a trigger
vocabulary that is merely wrong, undetected by the leg.

A second, independent degeneracy in the same vocabulary: the trigger for `RECORD-OUTSIDE-ROOT`
(`--root`) also occurs in two other **refusal-class** entries (`JSON-INSIDE-MEASURED-TREE`,
`USAGE`), so a containment check for it is satisfied by the wrong entry. (The scan also matches
`UNRECORDED`, but that is a *drift* class named in the prose paragraph
`Drift classes: … UNRECORDED (a git work tree under --root …)`, not a refusal-class entry; it is
listed here only because the raw scan output is reproduced verbatim.)

```
=== E7 trigger-string collisions across class entries ===
      RECORD-OUTSIDE-ROOT   trigger='--root'   also in JSON-INSIDE-MEASURED-TREE, UNRECORDED, USAGE
```

---

## 7. THE FALSIFIER — a concrete FALSE PASS produced by the committed r39 leg on a wrong
mapping, reproducible end-to-end through the committed counter

This is the load-bearing result of the seat.

**The mechanism, in three steps.**

1. `classify()` is a **substring scan** over `stdout+stderr`, and the tool echoes the **record
   path** into that text (`REFUSAL RECORD-MALFORMED: <path> is not a regular file`). A path
   containing a class token therefore **re-labels the observed class**.
2. The trigger for `RECORD-MALFORMED` is the word **`missing`**, which is a **substring of the
   class token `RECORD-MISSING`**. So `classes["RECORD-MISSING"]` satisfies the `RECORD-MALFORMED`
   trigger check without ever naming the malformed-path condition.
3. Both probes then collapse onto **one** class, so the leg checks one entry twice and never
   checks the other.

**Step 1 — the misattribution, in the committed counter's own output:**

```
$ python3 -B battery7.py
=== the same false pass reproduced through the FULL COMMITTED r39 counter ===
  benign scratch                       LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=True
  scratch under a RECORD-MISSING dir   LEG L4 FAIL missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=True
```

The committed counter prints `missing=RECORD-MISSING` where the tool actually raised
`RECORD-MALFORMED`. The tool's own banner is unambiguous; only the reader is wrong:

```
  tool stderr: REFUSAL RECORD-MALFORMED: .../RECORD-MISSING/absent.tsv is not a regular file
  r39 classify() -> RECORD-MISSING   (tool actually raised RECORD-MALFORMED)
  anchored REFUSAL banner -> RECORD-MALFORMED
```

**Step 2 — the candidate is genuinely wrong.** A candidate commit whose only change removes the
`RECORD-MALFORMED` trigger wording from the docstring, while the runtime still raises
`RECORD-MALFORMED` for a missing (ENOENT) path:

```
MUTANT tool bytes: .../work7/drift-MUTANT-wrong-mapping.py
  RECORD-MALFORMED entry now = 'RECORD-MALFORMED       a record path the tool cannot parse, a line'
  runtime still raises RECORD-MALFORMED for a missing (ENOENT) path
  -> the documented trigger for RECORD-MALFORMED ('missing' / 'ENOENT') is GONE.
```

**Step 3 — the FALSE PASS, end-to-end through the committed counter, on a git fixture.**
(Fixture built per the git-fixture rule: `mktemp`-style scratch dir, every git command run with
`-C <fixture root>`, `git rev-parse --show-toplevel` asserted to print the fixture root before
each commit.)

```
$ git -C $F rev-parse --show-toplevel
/fast/scratch/hyaku/souji-r40/R40mutationtester08/fixture
$ git -C $F log --oneline
5d0a3bf candidate: RECORD-MALFORMED trigger wording removed (wrong mapping)
ac3a2e7 fixture base: r39 base drift bytes

$ TMPDIR=$SCR python3 -B census/round-39/c2-counter.py --root $F --rev $CAND --base-rev $BASE --scratch $SCR
=== committed r39 counter, CANDIDATE vs BASE, benign scratch ===
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False

$ TMPDIR=$SCR2 python3 -B census/round-39/c2-counter.py --root $F --rev $CAND --base-rev $BASE --scratch $SCR2
=== committed r39 counter, CANDIDATE vs BASE, scratch under a RECORD-MISSING dir ===
LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
```

**The same candidate bytes and the same counter give `LEG L4 FAIL` or `LEG L4 PASS` purely as a
function of the scratch directory's name.** The candidate's mapping is wrong in both runs —
verified independently:

```
=== candidate runtime vs candidate docstring ===
  runtime class for a MISSING path : RECORD-MALFORMED
  candidate docstring entry        : RECORD-MALFORMED       a record path the tool cannot parse, a line
```

**The fix is one line, and it is verified to remove the non-determinism without weakening the
check.** Reading the observed class from the tool's own anchored `REFUSAL <CLASS>:` banner:

```
--- scratch dir basename: fx-benign ---
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
--- scratch dir basename: RECORD-MISSING ---
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
```

Identical verdicts under both scratch roots, and `FAIL` — correct for a wrong candidate.

---

## 8. Reachability of the L4 leg under the frozen base revision

The r39 leg's shape is `leg("L4", new_ok and not old_ok, ...)`. Under the r40 base revision
`0242085` the tool's docstring is **already correct** for the two observed classes, so the
`old_ok` arm is `True` at the base:

```
$ python3 -B census/round-39/c2-counter.py --root . --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
      --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=True
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=59f1e57d7af0/e48ed08e672824e496f8 fixture_sha=e555d8281484
rc=1
```

`new_maps=True old_maps=True` → `new_ok and not old_ok` is `False`. **At the frozen r40 base, the
r39-shaped L4 leg is unsatisfiable for any candidate that leaves the tool's docstring correct** —
its `old_ok` arm can never be false. The same leg shape with the *r39* base as the comparison
point does separate:

```
$ python3 -B census/round-39/c2-counter.py --root . --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
      --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
SUMMARY legs=6 pass=6 fail=0 harm=0 ...
```

**The frozen r40 measurement ("r40 counter receipt comparing base and candidate bytes", base
`0242085`) therefore has no base/candidate separation on the tool bytes for the joined
comparison** — the base already passes it (§5 B1). The r40 leg must find its separation
somewhere other than the tool's docstring text (in the counter's own analyzer, in a wider
observed set, or in a synthetic probe), and the frozen predicate does not say where.

---

## 9. Bounded measurement plan for the r40 implementer

Each item is a *requirement the frozen predicate implies but does not state*, with the
measurement that would settle it. Nothing here is a frozen-claim change; these are the
pre-conditions the r40 leg must satisfy to be decidable at all.

1. **Freeze the observed set before the candidate.** Write the class→trigger list to a lane file
   (e.g. `census/round-40/c2-pairs.tsv`) *before* any candidate bytes exist, and record its
   sha256 in the receipt. Measurement: the receipt names the list file and its digest; a second
   run reproduces the same digest.
2. **Widen the classifier to every reachable class.** `classify()` must recognise all ten classes
   the tool can raise, and must read the class from the tool's **anchored** `REFUSAL <CLASS>:`
   banner, not from a substring scan of `stdout+stderr`. Measurement: the §7 fixture — the same
   candidate bytes must yield `LEG L4 FAIL` under *any* scratch-root name (verified: the
   anchored reader gives `FAIL`/`FAIL`).
3. **Widen the probe set to the reachable classes**, at minimum `RECORD-EMPTY` and
   `RECORD-OUTSIDE-ROOT` (the two `RECORD-*` classes the inherited probe set never triggers),
   plus the five wrapped-only classes if the join is to be exercised at all. Measurement: the
   receipt lists the observed class set per run; it must be 10, not 2.
4. **Require an observed class with no docstring entry to be a FAIL**, never a skip. A
   containment-only detector that skips absent entries passes the six-deleted-entries mutant
   (§5). Measurement: the §5 mutant must FAIL.
5. **State the trigger tokens, and require each to be unique to its class.** `--root` currently
   collides across four entries (§6). Measurement: a uniqueness check over the frozen list, run
   as part of the counter, reported in the receipt.
6. **State the join rule** (which lines belong to which entry) and the **absence rule**
   (an observed class with no entry = FAIL). Measurement: the receipt names the rule, and the
   §5 mutant fails under it.
7. **Do not rely on the synthetic wrapped-trigger probe alone.** The committed base bytes already
   carry five wrapped-only trigger tokens (§5) — the real bytes separate the analyzers without a
   synthetic file, and the synthetic probe's verdict depends on an unfrozen trigger choice (§6).
   Measurement: the receipt reports the joined analyzer's verdict on the *real* base bytes as
   well as on the synthetic probe.

---

## 10. What is *not* claimed

- **The r40 C2 claim is not falsified** — there are no r40 candidate bytes yet
  (`census/round-40/` holds only `preregistration.txt`; `git ls-files census/round-40` is empty).
  What is falsified is the claim's **measurability**: the predicate has a false-pass path
  inherited from r39 (§7), and its "observed class/trigger pairs in the frozen list" refers to a
  list that does not exist (§1) and to an observed set the inherited instruments compute as 2 of
  10 (§4).
- **The committed r39 counter's L4 leg was not designed for the 10-class set.** The defects in
  §7 are properties of the *inherited* instrument; the r40 leg inherits them unless it pins the
  observation channel (§9.2). Sibling seats in this wave reach the same conclusion from the
  analyzer side (`R40mutationtester20` token semantics, `R40mutationtester32` join termination,
  `R40mutationtester44` join-widening monotonicity, `R40mutationtester56` observation channel);
  this seat's distinct contribution is §4–§6 and §8: **the observed-set coverage**, the
  **unfrozen trigger vocabulary**, the **base saturation**, and the **unsatisfiable leg shape**
  under the frozen base revision.
- The r40 base's `0242085` docstring is *correct*; nothing in this report claims otherwise.

---

## 11. Commands actually run (all read-only against the lane; all writes under scratch)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel
$ git log --oneline -3 ; git cat-file -e 0242085909fb6a4ee041c5443d76316ac6d59d4b^{commit}
$ git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py   > $S/drift-r40base.py
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py   > $S/drift-r39base.py
$ git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/c2-counter.py    > $S/r39-c2-counter.py
$ sha256sum census/round-39/c2-counter.py tools/souji-worktree-drift.py
$ python3 -B census/round-39/c2-counter.py --root . --rev 0242085… --base-rev 0242085… --scratch $S
$ python3 -B census/round-39/c2-counter.py --root . --rev 0242085… --base-rev ed30b7f… --scratch $S
$ python3 -B probe.py   $S/drift-r40base.py $S/run-base          # §4 reachable class set
$ python3 -B battery.py                                        # §5 analyzer/scope matrix, tool-byte mutants
$ python3 -B battery2.py                                       # §5 F1–F5
$ python3 -B battery3.py                                       # §5 base-vs-candidate, clean() hazard, round-40 contents
$ python3 -B battery4.py                                       # §5 exact r39 L4 replication, exclusivity
$ python3 -B battery5.py                                       # §6 trigger-choice flip, self-satisfying token, skip-absent detector
$ python3 -B battery6.py                                       # §7 misattribution in the committed counter
$ python3 -B battery7.py                                       # §7 FALSE PASS on a wrong mapping
$ python3 -B battery8.py                                       # §4/§5 observed-set coverage, 6-entry-deletion mutant
$ python3 -B final.py                                          # §4–§6 consolidated evidence
# git fixture (scratch only), every command with -C <fixture root>:
$ git -C $F rev-parse --show-toplevel          # asserted before each commit
$ git -C $F commit -q -m "fixture base: r39 base drift bytes"
$ git -C $F commit -q -m "candidate: RECORD-MALFORMED trigger wording removed (wrong mapping)"
$ TMPDIR=$SCR  python3 -B census/round-39/c2-counter.py --root $F --rev $CAND --base-rev $BASE --scratch $SCR
$ TMPDIR=$SCR2 python3 -B census/round-39/c2-counter.py --root $F --rev $CAND --base-rev $BASE --scratch $SCR2
```

Every child ran with an explicit `TMPDIR` under `$S`. The lane was never written except for this
report.

## 12. Restoration / integrity evidence

```
$ sha256sum census/round-39/c2-counter.py tools/souji-worktree-drift.py
732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11  census/round-39/c2-counter.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
```
— identical to the pre-measurement values in §2. Every mutant lived only under
`$S/fixture` and `$S/work*`; the lane's git index, working tree and `.jj/` were not touched.
`git status --porcelain` shows the pre-existing untracked `census/round-40/` plus sibling seats'
untracked `tests/fixtures/` files; **this seat wrote only this report**.
Scratch `/fast/scratch/hyaku/souji-r40/R40mutationtester08/` is removed before yield.

**Final verdict: C2 operability — the frozen predicate is NOT yet falsifiable. A concrete
false-pass path exists in the inherited leg (verified end-to-end: `LEG L4 PASS` on a candidate
whose mapping is wrong, decided by the scratch directory's name), the observed set it is scoped
to is 2 of 10 reachable classes at the frozen base, the trigger vocabulary that decides the
verdict is unfrozen, and the r39 leg shape is unsatisfiable under the frozen base revision.**
