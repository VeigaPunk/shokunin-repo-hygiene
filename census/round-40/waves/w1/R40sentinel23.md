# R40sentinel23 — C2 operability: independent attack on the frozen r40 C2 claim

- Seat: sentinel (leaf member — no subagent dispatch).
- Axis: **operability**.
- Distinct item 23, named edge case: **the wrapped-continuation *join rule* itself — i.e. whether the r40
  L4 analyzer is permitted to join a class entry's continuation lines at all, and if so, where the
  entry stops.** Distinct from the r39 reviewer's items (which attacked L1/L2/L3 refusal-binding,
  L5/L6 worktree-binding, and the ancestor-resolver stub); distinct from the r39 mutation battery
  (which attacked the *fixture*, not the analyzer's join semantics).
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` — **read-only**; no production file written,
  no git/jj/index mutation, no commit, no push.
- Frozen contract read first: `census/round-40/preregistration.txt` (C2 predicate at line 8).
- Base revision under attack: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (r40 prereg line 2,
  "round-39 verified tip").
- Scratch: `/fast/scratch/hyaku/souji-r40/R40sentinel23/` (fixture clone `repo/`, root-owned clone
  `repo-root/`, harnesses `falsify.py`, `falsify2.py`, `falsifier_r40_leg.py`, `control_vacuity.py`,
  `blast.py`, `sweep.py`, `uidprobe.py`). **Removed before yield.**
- Tool installs/upgrades: **none**. pacman untouched (paused). No network access used.
- Python 3.14.8, git 2.56.0, uid 1000 (`vgpnk`), passwordless `sudo` available (used only to run the
  *committed* r39 counter as uid 0 — see F5).

## 0. Bottom line

The frozen C2 predicate is **not falsifiable as written**, because it does not name the thing the
r40 leg is supposed to test. Two independent, concrete defects:

- **F1 (HIGH, calibration).** The predicate's discriminator — *"a synthetic wrapped-trigger probe is
  detected while the r39 one-line analyzer misses it"* — is satisfied on the **committed r40 base
  artifact** by an analyzer that performs **no continuation-joining whatsoever**, and is *also*
  satisfied by an analyzer that joins unboundedly. Measured: the r39 one-line analyzer already
  reads `new_ok=True` on `0242085` for the frozen r39 pair set, because r39's own repair moved
  `EACCES` onto the `RECORD-MISSING` class line and `missing` onto the `RECORD-MALFORMED` class
  line. So the r39 control does **not** miss anything on the r40 base bytes, and the only place the
  r39-vs-r40 difference can live is a synthetic probe the r40 author writes themselves.
- **F2 (HIGH, calibration).** The predicate's kill condition — *"if any observed class mapping
  disagrees with runtime behavior"* — is **unreachable for an unbounded join**. A join that appends
  every remaining docstring line to a class entry reads a mis-homed trigger as *present on the
  wrong class* and still reports the pair satisfied. Measured: on a mutant with all 7
  continuation-only triggers re-homed to the wrong class, the bounded join reports **0/7** satisfied
  (correctly FAILs) while the unbounded join reports **7/7** satisfied (**PASSes the frozen
  predicate**). The r40 leg must therefore *bound* the join, and the predicate does not say so.

Two secondary findings (F3: join-rule ambiguity on the committed bytes; F4: no committed
class/trigger pair list exists, so "the frozen list" is author-supplied) and one robustness finding
(F5: the L4 EACCES observation is **uid-dependent** — the committed r39 counter passes 6/6 as
uid 1000 and fails L4 as uid 0 on byte-identical inputs).

**Verdict: C2's r40 predicate, as frozen, admits an analyzer that does not join, and an analyzer
that joins wrongly. It does not currently discriminate the r40 improvement from the r39 instrument
on the committed artifact. This is a predicate defect, not a counter defect — r40's C2 counter does
not exist yet.** Smallest remediation in §5.

## 1. What the frozen C2 predicate says, verbatim

`census/round-40/preregistration.txt:8`:

> Predicate: r40 L4 docstring analyzer joins wrapped continuation lines into one class entry and
> verifies all observed class/trigger pairs in the frozen list; a synthetic wrapped-trigger probe is
> detected while the r39 one-line analyzer misses it. Control: r39 `docstring_classes` extracts
> only the first class line. Kill if wrapped trigger is missed, or if any observed class mapping
> disagrees with runtime behavior. Measurement: r40 counter receipt comparing base and candidate
> bytes.

Three terms carry the whole leg and none is pinned:
1. *"joins wrapped continuation lines into one class entry"* — the join **rule** is unspecified.
2. *"all observed class/trigger pairs in the frozen list"* — **no such list is committed anywhere**
   (F4); "observed" pairs are what the counter chooses to probe.
3. *"a synthetic wrapped-trigger probe is detected while the r39 one-line analyzer misses it"* — the
   probe is author-written (F1).

The r39 predecessor this builds on: `census/round-39/c2-counter.py:133-146` (`docstring_classes`,
one line per class, hardcoded to two class names) and `:216-231` (leg L4). The r39 prereg's L4
wording is at `census/round-39/preregistration.txt:58-59`.

## 2. F1 (HIGH) — the r39 control does not miss anything on the r40 base artifact

**Command actually run** (scratch fixture clone at the r40 base revision; the lane was never
mutated):

```text
$ cd /fast/scratch/hyaku/souji-r40/R40sentinel23
$ git -C repo rev-parse --show-toplevel
/fast/scratch/hyaku/souji-r40/R40sentinel23/repo
$ git -C repo checkout 0242085909fb6a4ee041c5443d76316ac6d59d4b
$ git -C repo show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py > base-drift.py
$ sha256sum base-drift.py   # e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
```

Applying the **verbatim** r39 `docstring_classes()` (copied from `census/round-39/c2-counter.py:133-146`)
to the r40 base artifact:

```text
r40 base 0242085 -> {'RECORD-MISSING': 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path',
                     'RECORD-MALFORMED': 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'}
  r39 one-line analyzer on r40 base artifact: new_ok = True
  => r39 CONTROL ('misses it') holds? False
```

`new_ok` is the exact r39 L4 predicate (`census/round-39/c2-counter.py:226-231`):
`missing in new_classes and "missing" in new_classes[missing].lower() and locked in new_classes and
"EACCES" in new_classes[locked]`.

**Consequence.** On the r40 base bytes the r39 one-line analyzer already satisfies the whole L4
mapping. The r39 repair (`790d16b`, wave seat `W1ExecC2Docstring`) moved `EACCES` onto the
`RECORD-MISSING` class line and `missing` onto the `RECORD-MALFORMED` class line — that was r39's
deliberate fix for its own lesson M1 (`corpus/lessons/round-39.md:76-88`: *"a docstring rule that
measured its own wrapper"*; the same lesson records that the paragraph-joining variant *"was
reverted"*). The r40 predicate therefore cannot use the real artifact to separate the r39 analyzer
from an r40 analyzer; the separator is necessarily the **synthetic probe**, and the probe is
author-written by the same person who writes the joiner.

Demonstration that the frozen conjuncts are satisfiable with **zero joining** (`control_vacuity.py`):

```text
=== the r39 control arm, probe by probe ===
 novel class, trigger WRAPPED
   r39 one-line finds trigger? False   (control 'misses it' satisfied: True)
   NO-JOIN all-class analyzer finds it? False
   => frozen conjuncts satisfied WITHOUT any continuation-joining: False
 novel class, trigger FLAT
   r39 one-line finds trigger? False   (control 'misses it' satisfied: True)
   NO-JOIN all-class analyzer finds it? True
   => frozen conjuncts satisfied WITHOUT any continuation-joining: True
 RECORD-MISSING, trigger WRAPPED
   r39 one-line finds trigger? False   (control 'misses it' satisfied: True)
   NO-JOIN all-class analyzer finds it? False
   => frozen conjuncts satisfied WITHOUT any continuation-joining: False
```

The middle row is the hole: the r39 analyzer's class set is **hardcoded to two names**
(`census/round-39/c2-counter.py:141`), so it "misses" *any* probe whose class is not
`RECORD-MISSING`/`RECORD-MALFORMED` **for a reason unrelated to wrapping**. A probe on a novel class
name with a *flat* trigger satisfies *"the r39 one-line analyzer misses it"* while an analyzer that
performs no joining at all satisfies *"is detected"*. Both conjuncts hold with the improvement
absent. Note the frozen text says *"a synthetic wrapped-trigger probe"* — a wrapped probe on a
novel class does not rescue it either: the r39 analyzer still misses it for the wrong reason, so the
control does not *attribute* the miss to wrapping.

A stronger, non-vacuous variant is available and should be required: the probe's class must be one
the r39 analyzer **does** know (`RECORD-MISSING` or `RECORD-MALFORMED`), so that the r39 miss is
attributable to the wrapper and not to the class set.

## 3. F2 (HIGH) — the kill condition is unreachable for an unbounded join

**Command actually run** (`blast.py`): a mutant of the r40 base tool in which all seven
continuation-only class/trigger pairs are re-homed to the wrong class (the tool's *runtime
behaviour* is unchanged — only the docstring lies). Two joiners, both satisfying the literal
sentence *"joins wrapped continuation lines into one class entry"*:

```text
=== MUTANT: all 7 continuation-only triggers re-homed to the WRONG class ===
  join-A (bounded)      : 0/7 continuation-only pairs still 'satisfied' -> []
  join-BLOB (unbounded) : 7/7 continuation-only pairs still 'satisfied' -> [('RECORD-MALFORMED','duplicated name'),
      ('RECORD-MALFORMED','TOTAL row'), ('RECORD-OUTSIDE-ROOT','--root'),
      ('JSON-INSIDE-MEASURED-TREE','measured repository'), ('JSON-IS-RECORD','same inode'),
      ('JSON-NOT-REGULAR','FIFO'), ('JSON-UNWRITABLE','O_NOFOLLOW')]
```

The unbounded join (`class entry = class line + every remaining docstring line`) reports all seven
mis-homed triggers as still satisfied, because the trigger text is still somewhere downstream of the
class line. The frozen kill condition *"if any observed class mapping disagrees with runtime
behavior"* does **not** fire: the pair is present, only on the wrong class. So an analyzer that
cannot detect the mis-mapping the C2 leg exists to detect **PASSES** the frozen predicate.

The single-pair form of the same defect (`falsify2.py`), where `EACCES` is moved off
`RECORD-MISSING` onto `JSON-UNWRITABLE`:

```text
=== MUTANT 2: EACCES moved OFF RECORD-MISSING onto JSON-UNWRITABLE (wrong class) ===
  joiner=correct-bounded  RECORD-MISSING-names-EACCES = False   <-- r40 predicate verdict
  joiner=unbounded-blob   RECORD-MISSING-names-EACCES = True    <-- r40 predicate verdict
```

Note this is precisely the defect class r39's own `W1RevC2Doc` reported
(`census/round-39/waves/w1-results.json:142`: *"a tool whose RECORD-MALFORMED line names 'missing'
while its code raises RECORD-MISSING for a missing path reads LEG L4 PASS new_maps=True"*). r40's
predicate must bind *the class the trigger belongs to*, not *the presence of the token near the
class*. A bounded join plus a per-class exclusivity check does that; the frozen text does not
require either.

## 4. F3 (MEDIUM) — the join rule is ambiguous, and the committed bytes do not decide it

The r40 base docstring's refusal-class block is not uniformly aligned. Measured on
`base-drift.py` (the class-line description column vs. the continuation indent):

```text
class                        desc_col cont_indent  aligned
RECORD-MISSING                      25          25  YES
RECORD-MALFORMED                    25          25  YES
RECORD-EMPTY                        25         None  -
RECORD-OUTSIDE-ROOT                 25          25  YES
JSON-INSIDE-MEASURED-TREE           29          25  NO  <<<
JSON-IS-RECORD                      25          25  YES
JSON-NOT-REGULAR                    25          25  YES
JSON-HARDLINKED                     25         None  -
JSON-UNWRITABLE                     25          25  YES
USAGE                               25         None  -
```

`JSON-INSIDE-MEASURED-TREE` is the only class whose name is long enough to push its description past
the col-25 gutter, so its continuation sits at col 25 while its own description starts at col 29.
Two defensible join rules therefore disagree **on the pristine committed bytes**:

```text
=== continuation-only pairs satisfied on the PRISTINE r40 base ===
   join-A (indent>class-indent) = 7/7 ; join-B (indent==desc-col) = 6/7
   DISAGREE JSON-INSIDE-MEASURED-TREE <-> measured repository: A=True B=False
   join-B entry: 'JSON-INSIDE-MEASURED-TREE  the --json target lies under --root or under a'
   join-A entry: 'JSON-INSIDE-MEASURED-TREE  the --json target lies under --root or under a measured repository'
```

`measured repository` is the JSON-INSIDE-MEASURED-TREE trigger — verified reachable at runtime
(§6, sweep) — and it is **only** on that class's continuation line. So a join-B r40 leg, run
against the pristine base artifact, would report a *false* trigger miss and FAIL the frozen kill
condition *"if wrapped trigger is missed"*, while a join-A leg passes. Both readings satisfy the
frozen sentence. The join rule must be pinned, not left to the implementer.

## 5. F4 (MEDIUM) — "the frozen list" does not exist; it is author-supplied

The predicate requires the leg to verify *"all observed class/trigger pairs in the frozen list"*.
Searches over the whole lane and its full history found **no committed class→trigger pair table**:

```text
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ git ls-files | grep -iE "c2-item|class.*tsv|pair.*tsv"
.ufo/waves/round-22/attempt2/w1/evidence/gatefix/census/verdicts-badclass.tsv
.ufo/waves/round-18/w2/RevLivePairs.md
census/round-18/counter-exclusion-repair.json
census/round-18/live-fleet-pairs/pair1-base-b576341.tsv
...
$ git log --all --diff-filter=A --name-only --format="%H" | grep -iE "c2-item|class.*tsv|trigger.*tsv|pair.*tsv"
(no class/trigger pair table in any revision)
```

The nearest committed relatives are `census/round-32/c2-items.tsv` (a *scratch-path* enumeration,
unrelated) and `tests/fixtures/r38-drift-write-envelope.py:170-206` (the `docstring-enum` case,
which checks only that each **class token** appears in the docstring and that no **phantom class**
appears — it does **not** check trigger→class pairing at all). So the pair list, the trigger tokens,
and the probe set are all supplied by the r40 counter author, and the leg's own kill condition is
then evaluated against a list that author chose. r39 avoided this by landing its item list in the
same freeze commit as its counter (`b769bfb`: `census/round-39/c1-items.tsv` + `census/round-39/c2-counter.py`
+ `preregistration.txt` in one commit).

For scale, the ten classes and their runtime triggers are (measured, §6):

| class | trigger(s) | trigger on class line? |
|---|---|---|
| RECORD-MISSING | EACCES, ELOOP | yes (both) |
| RECORD-MALFORMED | ENOENT, non-regular | yes (both) |
| RECORD-MALFORMED | duplicated name, TOTAL row | **continuation only** |
| RECORD-EMPTY | no REPO rows | yes |
| RECORD-OUTSIDE-ROOT | --root | **continuation only** |
| JSON-INSIDE-MEASURED-TREE | measured repository | **continuation only** |
| JSON-IS-RECORD | same inode | **continuation only** |
| JSON-NOT-REGULAR | FIFO | **continuation only** |
| JSON-HARDLINKED | more than one link | yes |
| JSON-UNWRITABLE | O_NOFOLLOW | **continuation only** |
| USAGE | --timeout | yes |

Seven of the fifteen pairs are continuation-only — i.e. **the r40 improvement is load-bearing for
47% of the plausible pair set**, and the frozen text does not say which of these the leg must
cover.

## 6. F5 (MEDIUM, robustness) — the L4 EACCES observation is uid-dependent

The r39 L4 leg derives its `locked` class by chmod-ing a probe file to 0 and running the drift tool
(`census/round-39/c2-counter.py:224-225`). Under uid 0 the kernel bypasses the read permission, so
the tool reads the file instead of failing to open it, and raises a **different** class:

```text
$ python3 -B uidprobe.py base-drift.py
uid=1000  EACCES-probe -> RECORD-MISSING | ELOOP-probe -> RECORD-MISSING | ENOENT-probe -> RECORD-MALFORMED
$ sudo -n python3 -B uidprobe.py base-drift.py
uid=0     EACCES-probe -> RECORD-EMPTY   | ELOOP-probe -> RECORD-MISSING | ENOENT-probe -> RECORD-MALFORMED
```

Running the **committed, unmodified** r39 counter on byte-identical inputs, once as uid 1000 and
once as uid 0 on a root-owned clone of the same fixture (so `git rev-parse --show-toplevel` resolves
the same way):

```text
# uid 1000 (fixture clone owned by vgpnk)
$ TMPDIR=.../sc-nonroot python3 -B census/round-39/c2-counter.py --root "$PWD" \
    --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch .../sc-nonroot
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
NONROOT rc=0

# uid 0 (root-owned clone of the same fixture, same revisions)
$ sudo -n python3 -B census/round-39/c2-counter.py --root "$PWD" \
    --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch .../sc-root
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-EMPTY new_maps=False old_maps=False
SUMMARY legs=6 pass=5 fail=1 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
ROOT rc=1
```

Same tool bytes (`tool_sha=59f1e57d7af0/e48ed08e6728` both runs), same revisions, same fixture: the
C2 leg flips **PASS→FAIL** purely on uid. `ELOOP` is uid-stable (`RECORD-MISSING` at both uids) and
is the better probe. Any r40 leg that keeps the chmod-0/EACCES probe inherits this. This is a
**robustness disclosure for the r40 counter to inherit**, not a defect in the frozen predicate
itself.

A related note for whoever builds the r40 leg: the r40 base and the r39 after-revision have
**byte-identical** drift-tool bytes, so a base-vs-candidate comparison over tool bytes is degenerate
for L4:

```text
$ git show 2f6e981a105fc759205767d2a749a5f7d4fd0b8a:tools/souji-worktree-drift.py | sha256sum
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
$ git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py | sha256sum
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
$ git diff 2f6e981a105fc759205767d2a749a5f7d4fd0b8a 0242085909fb6a4ee041c5443d76316ac6d59d4b \
    --stat -- tools/souji-worktree-drift.py
(no output — identical)
```

And the r39 counter run at r40's own base against itself (the do-nothing control) fails L4 for the
expected reason — the r39 leg demands `new_ok and not old_ok`, which cannot hold when both arms are
the same bytes:

```text
$ python3 -B census/round-39/c2-counter.py --root "$PWD" \
    --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b ...
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=True
SUMMARY legs=6 pass=2 fail=4 harm=0
rc=1
```

## 7. Runtime observability sweep (all ten documented classes, measured)

`sweep.py`, uid 1000, against the r40 base tool bytes (`base-drift.py`, sha256 `e48ed08e6728`):

```text
uid=1000
expected case                observed class               rc  trigger-reason
RECORD-MALFORMED/ENOENT      RECORD-MALFORMED             2  ... is not a regular file
RECORD-EMPTY/no REPO rows    RECORD-EMPTY                 2  no REPO rows in ...
RECORD-MALFORMED/non-regular RECORD-MALFORMED             2  ... is not a regular file
RECORD-MISSING/EACCES        RECORD-MISSING               2  [Errno 13] Permission denied
RECORD-MISSING/ELOOP         RECORD-MISSING               2  [Errno 40] Too many levels of symbolic links
RECORD-MALFORMED/dup name    RECORD-MALFORMED             2  line 2 duplicates a
RECORD-MALFORMED/bad schema  RECORD-MALFORMED             2  line 1 does not match the census schema
RECORD-MALFORMED/TOTAL disagr RECORD-MALFORMED             2  TOTAL repos=9 but 1 REPO rows
RECORD-OUTSIDE-ROOT          RECORD-OUTSIDE-ROOT          2  ../escape resolves outside ...
JSON-INSIDE-MEASURED-TREE    JSON-INSIDE-MEASURED-TREE    2  ... is under ...
JSON-IS-RECORD               JSON-IS-RECORD               2  ... is the record file
JSON-NOT-REGULAR/FIFO        JSON-NOT-REGULAR             2  ... is not a regular file
JSON-HARDLINKED              JSON-HARDLINKED              2  ... has 2 links
USAGE/--root not a dir       USAGE                        2  --root ... is not a directory
USAGE/--timeout < 1          USAGE                        2  --timeout must be >= 1
```

Two ordering facts the r40 leg must respect (both measured):

- `JSON-NOT-REGULAR` (FIFO) only fires when the FIFO is **outside** `--root`; inside `--root` the
  `JSON-INSIDE-MEASURED-TREE` check fires first:

```text
fifo INSIDE --root     rc=2 classes_in_output=['JSON-INSIDE-MEASURED-TREE']
fifo OUTSIDE --root    rc=2 classes_in_output=['JSON-NOT-REGULAR']
```

- `USAGE/--root not a dir` requires `--root` to point at a **file**, and the tool checks it
  *before* the record (rc 2, `REFUSAL USAGE: --root ... is not a directory`).

Also: the r39 `classify()` helper (`census/round-39/c2-counter.py:125-131`) recognises only four
class names (`RECORD-MISSING`, `RECORD-MALFORMED`, `RECORD-EMPTY`, `RECORD-OUTSIDE-ROOT`) and
returns `NO-CLASS` otherwise, while `docstring_classes()` (`:141`) recognises only two. An r40 leg
covering the six `JSON-*`/`USAGE` classes must extend both.

## 8. Verdict

**The frozen r40 C2 predicate is not falsifiable as written, and the committed r40 base artifact
does not discriminate the r40 improvement from the r39 instrument.**

- **F1 (HIGH):** the r39 one-line analyzer already reads `new_ok=True` on the r40 base bytes for
  the frozen r39 pair set, so the stated control (*"the r39 one-line analyzer misses it"*) is
  satisfied on real bytes without any joining; and with an author-supplied probe class outside
  r39's hardcoded two-name set, both conjuncts are satisfied by an analyzer that never joins.
- **F2 (HIGH):** the kill condition *"any observed class mapping disagrees with runtime behavior"*
  does not fire for an unbounded join; on a mutant with all seven continuation-only triggers
  re-homed to the wrong class, the unbounded join reports **7/7 satisfied (PASS)** while the
  bounded join correctly reports **0/7 (FAIL)**. An analyzer blind to the mis-mapping passes the
  frozen predicate.
- **F3 (MEDIUM):** the join rule is ambiguous and the committed bytes do not decide it —
  `JSON-INSIDE-MEASURED-TREE` (desc col 29, continuation col 25) is satisfied 7/7 under one
  defensible rule and 6/7 under the other, on the *pristine* artifact.
- **F4 (MEDIUM):** no committed class/trigger pair list exists anywhere in the lane or its history;
  the list, the trigger tokens, and the probe set are all supplied by the r40 counter author, and
  the leg's kill condition is then evaluated against an author-chosen list.
- **F5 (MEDIUM):** the L4 EACCES observation is uid-dependent — the committed r39 counter passes
  6/6 as uid 1000 and fails L4 (`locked=RECORD-EMPTY`) as uid 0 on byte-identical inputs. `ELOOP`
  is uid-stable.

**Status of C2's r40 acceptance predicate: UNVERIFIED and, on this evidence, UNMEASURABLE as
frozen.** No r40 counter exists yet (`census/round-40/` contains only `preregistration.txt`), so
this is an attack on the *predicate*, not a measurement of a counter. This seat did **not** run any
r40 candidate counter and does not claim the r40 counter fails — only that the frozen predicate
admits the wrong implementations above.

## 9. Smallest remediation (bounded, for the r40 predicate/leg, before any after-data)

Smallest change that makes the predicate falsifiable, in priority order:

1. **Pin the join rule and require it to be bounded.** State the join rule in the leg (e.g.
   "a class entry is its class line plus the following lines whose indent exceeds the class
   line's indent, stopping at the next class line") and add a case that pins the bound: a probe
   whose trigger appears only in a **later** class's entry must read **absent** from the earlier
   class. This is the F2 kill; it is one extra probe.
2. **Pin the pair list as a committed artifact**, in the same freeze commit as the r40 counter
   (r39's precedent: `b769bfb` lands `c1-items.tsv` + `c2-counter.py` + `preregistration.txt`
   together). Name the file in the prereg, as r39's prereg names `census/round-39/c1-items.tsv`.
3. **Require exclusivity, not presence**: the leg must assert that a trigger token appears under
   **exactly one** class entry, so a re-homed trigger is detected. This is what the r39
   `W1RevC2Doc` mutant needs and what r39's `docstring_classes` could not see.
4. **Make the probe r39-attributable**: the synthetic probe's class must be `RECORD-MISSING` or
   `RECORD-MALFORMED` (the two the r39 analyzer knows), so that "the r39 analyzer misses it" is
   attributable to the wrapper rather than to the class set. Also add the r39-class-name variant so
   the control cannot be satisfied vacuously.
5. **Use the `ELOOP` trigger instead of `chmod 0`/EACCES** for the `RECORD-MISSING` observation
   (uid-stable, measured in §6), and state the uid the receipt was taken at.
6. **Decide the `JSON-INSIDE-MEASURED-TREE` column question explicitly** (F3): either the join rule
   is "indent > class-line indent" (7/7, continuation at col 25 is included) or the docstring is
   re-guttered so every class description starts at col 25. Do not leave it to the implementer.

## 10. Gates, surfaces, limits

- **Gates observed:** the r40 preregistration contract, the committed r39 counter/fixture/receipts,
  and the committed drift-tool bytes at the r40 base revision. No wave-result gates were consumed
  as evidence; no r40 counter was executed (none exists).
- **Surfaces touched:** this report only, at `.ufo/waves/round-40/w1/R40sentinel23.md`. Lane
  worktree state after the seat: `git status --short` shows only the pre-existing untracked
  `census/round-40/` (the prereg, present before this seat ran); HEAD unchanged at
  `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`. No git/jj/index mutation, no commit, no push.
- **Scratch:** `/fast/scratch/hyaku/souji-r40/R40sentinel23/` — removed before yield.
  Fixture clone `repo/` was created with `git clone` from the lane and `git checkout` of the base
  revision; `git -C repo rev-parse --show-toplevel` was asserted to the fixture root before any
  git operation in it. The root-owned clone `repo-root/` was a `cp -a` of that clone with
  `chown -R root:root`, used solely for the uid-0 run in F5; no commit was made in either.
- **Out of scope, not attempted:** C1 (calibration) and C3 (coverage) predicates; any production
  file; any frozen-claim edit; the sibling lanes; `.ufo/state`; fleet scripts and templates.
- **Known limits:** (a) F1/F2 are attacks on the *predicate text*; they do not measure an r40
  counter, which does not exist. (b) The trigger↔class table in §5 is derived from my own sweep
  (§7) and from the docstring, not from a committed pair list — F4 is exactly that gap. (c) The
  join rules compared in F3 are two of several defensible readings; the finding is that the
  committed bytes do not *decide* between readings, not that only these two exist. (d) The uid-0
  run in F5 needed passwordless `sudo` (available on this host); a host without it would only
  reproduce the uid-1000 arm.
- **Installs:** none. pacman untouched (paused per the operator directive). No tool was added or
  upgraded; everything above used the preinstalled Python 3.14.8 / git 2.56.0.
