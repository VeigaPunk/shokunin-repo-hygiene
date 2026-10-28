# R40mutationtester44 — C2 (operability) attack: join-widening monotonicity makes the r40 L4 analyzer a strict *weakening* of the r39 control it replaces

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt` (C2 predicate, line 8)
- Lane tip at measurement: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`
- r40 base revision (round-39 verified tip, named by the prereg): `0242085909fb6a4ee041c5443d76316ac6d59d4b`
- r39 candidate revision (the after-bytes the r39 C2 receipt measured): `2f6e981a105fc759205767d2a749a5f7d4fd0b8a`
- r39 control base revision: `ed30b7f5b77939c9073348d810730bc4f355708d`
- Role: mutation-tester (advisory; nothing in the lane was committed, pushed, or mutated)
- Scratch: `/fast/scratch/hyaku/souji-r40/R40mutationtester44` (removed before yield — see §7)
- Tool installs: **none** (the tooling directive permits installs; none was needed; `pacman` untouched)

---

## 0. Named edge case for item 44 (explicit)

**Item 44 = join-widening monotonicity.** Distinct from every r39 C2 attack, and from the
r39 seat `W1RevC2Doc` (`census/round-39/waves/w1/W1RevC2Doc.md`), which attacked the *token
semantics* of the **one-line** analyzer (its mutants A/B/C: wrong class named, both triggers
named, unenumerated triggers). r39's seat assumed the one-line analyzer as given and did **not**
ask what the r40 change *does to* the check.

r40 changes the analyzer itself: the C2 predicate (prereg line 8) says the r40 L4 analyzer
"**joins wrapped continuation lines into one class entry**" while the r39 control
"`docstring_classes` extracts only the first class line". Item 44 asks a different question:

> **Does joining change the L4 check's verdict, and in which direction?**

The answer, measured below, is: **joining can only ever turn a FAIL into a PASS; it can never
turn a PASS into a FAIL.** The r40 change is therefore a *strict weakening* of the very
discriminator the r40 leg is claimed to strengthen. This is the falsifier.

## 1. The instrument and the check under test

`census/round-39/c2-counter.py:133-144` (the r39 control, verbatim):

```python
def docstring_classes(tool):
    """Class token -> the first docstring line that starts with it (ast only, no source slicing)."""
    ...
    for line in doc.split("\n"):
        stripped = line.strip()
        for cls in ("RECORD-MISSING", "RECORD-MALFORMED"):
            if stripped.startswith(cls) and cls not in out:
                out[cls] = stripped
```

`census/round-39/c2-counter.py:222-238` (the L4 leg, verbatim):

```python
missing = classify(run_drift(new_drift, root, os.path.join(base_scratch, "absent.tsv")))
os.chmod(probe, 0)
locked = classify(run_drift(new_drift, root, probe))
...
new_ok = (
    missing in new_classes and "missing" in new_classes.get(missing, "").lower()
    and locked in new_classes and "EACCES" in new_classes.get(locked, "")
)
old_ok = ( ... same shape over old_classes ... )
leg("L4", new_ok and not old_ok, detail + " new_maps=%s old_maps=%s" % (new_ok, old_ok))
```

Two properties of this check drive the whole finding:

1. **The check is a substring-containment test on the extracted entry** — `"missing" in
   entry.lower()` and `"EACCES" in entry`. It is *not* a test of which class the entry names.
2. **The joined entry is the one-line entry plus the class line's continuation lines.** So the
   joined haystack is a **strict superset** of the one-line haystack for every docstring.

Therefore `one-line PASS ⇒ joined PASS` holds universally, and joining can only *add* passes.
Property 1 + property 2 = the falsifier: the r40 change cannot kill anything the r39 control
kills; it can only lose discrimination.

## 2. Mutation battery — committed mutants in a verified fixture

Fixture (scratch only; toplevel asserted before every commit):

```
$ FIX=$(mktemp -d /fast/scratch/hyaku/souji-r40/R40mutationtester44/fx.XXXXXX)
$ git clone --no-hardlinks --quiet /home/vgpnk/Projects/shokunin/souji-shokunin $FIX/repo
$ git -C $FIX/repo rev-parse --show-toplevel
/fast/scratch/hyaku/souji-r40/R40mutationtester44/fx.Z7PDFM/repo      # asserted == $FIX/repo
```

Each mutant replaces only the drift tool's **module docstring** (the behaviour-bearing point of
the C2 contract), leaving every raise site untouched. Runtime behaviour is therefore invariant —
verified for every mutant (§4).

| id | mutation | the docstring now claims |
|---|---|---|
| MUT-A | `RECORD-MALFORMED` entry = "a record file whose contents cannot be parsed; the absent-path case is **RECORD-MISSING**" | the absent path is `RECORD-MISSING` — **contradicts runtime**, which raises `RECORD-MALFORMED` |
| MUT-B | `RECORD-EMPTY` and `RECORD-OUTSIDE-ROOT` descriptions **transposed** | the empty class is the outside-root class and vice-versa — contradicts runtime |
| MUT-C | `RECORD-MISSING` entry = "the record path exists but cannot be opened" (no `EACCES`), `EACCES` pushed under `JSON-IS-RECORD` | the `RECORD-MISSING` class no longer names its trigger |
| MUT-D | `RECORD-MALFORMED` entry = "...an ENOENT path is not this class, it is **RECORD-MISSING**" | contradicts runtime |

**MUT-A is the falsifier.** The literal class token `RECORD-MISSING` contains the substring
`missing`, so the frozen `"missing" in entry.lower()` conjunct is satisfied by the entry naming
the **wrong** class. Measured: `'RECORD-MISSING'.lower()` contains `'missing'` → `True`.

## 3. Verdicts (exact commands, actual output)

### 3.1 Join-rule × mutant matrix — frozen L4 predicate shape, `monotone.py` / `tighten.py`

```
case        r39-1line  r40-join  STRENGTHENED
--------------------------------------------------------------
PRISTINE    PASS       PASS       PASS  S1+S2+S3 ok (claims ['enoent','missing','non-regular'] / ['cannot be opened','eacces','eloop'])
MUT-A       FAIL       PASS       FAIL  S1 trigger not found after masking sibling class tokens
MUT-B       PASS       PASS       PASS  S1+S2+S3 ok
MUT-D       FAIL       PASS       FAIL  S1 trigger not found after masking sibling class tokens
MUT-E       PASS       PASS       FAIL  S1 trigger not found after masking sibling class tokens
MUT-F       PASS       PASS       FAIL  S2 cross-class trigger claim: malformed-entry=['unreadable'] missing-entry=[]
MUT-G       FAIL       FAIL       FAIL  S1 trigger not found after masking sibling class tokens
```

**MUT-A and MUT-D: the r39 one-line control FAILS them; the r40 joined analyzer PASSES them.**
Two mutants that name the *wrong class* survive the r40 analyzer. MUT-E/MUT-F are variants that
survive *both* (the substring collision on the first line, and a positive inversion with no
sibling token) — they show the contamination is latent in the frozen token-presence check, not
merely introduced by joining.

### 3.2 The REAL committed r39 instrument, on committed mutant revisions

```
$ python3 -B census/round-39/c2-counter.py --root $FIX/repo --rev <mutant> \
      --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
PRISTINE  LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
MUT-A     LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
MUT-B     LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
MUT-C     LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
MUT-D     LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
```

The genuine r39 instrument kills MUT-A and MUT-D on L4. A faithful r40-style joined leg
(`r40leg.py`, reimplementing the prereg's "joins wrapped continuation lines into one class entry")
returns **PASS** on both. That is the regression, measured on the real instrument's own fixture.

### 3.3 Monotonicity, proved over an exhaustive synthetic family — `monotone.py`

15 docstrings (5 `RECORD-MALFORMED` class lines × 3 continuation variants):

```
  monotonicity violations (one-line PASS, joined FAIL) = 0
  cases where joined PASSES but one-line FAILS (lost discrimination) = 2
    * a record file whose contents cannot be parsed | the absent-path case is RECORD-MISSING
    * a record file whose contents cannot be parsed | missing (ENOENT) or non-regular record path
```

Zero violations in the direction that would make joining stronger; two in the direction that makes
it weaker. Superset property confirmed on every committed mutant:

```
  mutant MUT-A  one-line-entry-is-prefix-of-joined-entry: True
  mutant MUT-B  one-line-entry-is-prefix-of-joined-entry: True
  mutant MUT-C  one-line-entry-is-prefix-of-joined-entry: True
  mutant MUT-D  one-line-entry-is-prefix-of-joined-entry: True
```

### 3.4 Join-rule dependence — the predicate does not pin the rule — `monotone.py` PART 3

Three defensible readings of "join wrapped continuation lines into one class entry"
(`join-indent` = continuation is any deeper-indented following line; `join-until-class` =
continuation runs to the next class token; `join-paragraph` = continuation runs to the blank line)
give **different verdicts on identical bytes**:

```
  MUT-C verdict by join rule:
    join-indent        FAIL
    join-until-class   PASS
    join-paragraph     PASS
```

The prereg does not say which rule is meant, so an r40 counter's L4 verdict is **rule-dependent**.
This is a second, independent falsifier of the frozen predicate as written.

### 3.5 The claim's own control arm still holds — `monotone.py` PART 4

```
  r39 one-line analyzer (must MISS): FAIL
  join-indent        (must DETECT): PASS
  join-until-class   (must DETECT): PASS
  join-paragraph     (must DETECT): PASS
```

The r40 predicate's stated control ("a synthetic wrapped-trigger probe is detected while the r39
one-line analyzer misses it") is **achievable and reproduced** on all three join rules. The claim
is not unfalsifiable — it is falsifiable in the *wrong* direction: the same change that makes the
probe detectable makes the wrong-class mutants survive.

## 4. Runtime-behaviour invariance (the mutants are documentation-only)

Every mutant was re-run against its own bytes; the observed class/trigger pairs are identical to
pristine, so every mutant is a pure documentation defect and the L4 leg's runtime half is stable:

```
  absent path      -> RECORD-MALFORMED  REFUSAL RECORD-MALFORMED: .../absent.tsv is not a regular file
  unreadable path  -> RECORD-MISSING    REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '.../locked-probe.tsv'
```

and for every committed mutant: `absent->RECORD-MALFORMED unreadable->RECORD-MISSING` (11/11
mutant revisions checked).

## 5. The frozen list is not pinned — the pair set the r40 leg must cover is undefined in bytes

The prereg's C2 predicate requires the r40 analyzer to "verify **all observed class/trigger pairs
in the frozen list**". The prereg is the only committed artefact mentioning a frozen list:

```
$ grep -rn "frozen list" census/round-40/
census/round-40/preregistration.txt:8:...verifies all observed class/trigger pairs in the frozen list...
```

There is **no committed frozen list** — no item file, no pairs file, no class/trigger table. The
r39 L4 leg observes exactly **two** pairs (absent path → `RECORD-MALFORMED`; unreadable path →
`RECORD-MISSING`), yet the drift tool's docstring names **four** runtime-reachable `RECORD-*`
classes, and two more are reachable but never observed by L4:

```
  empty record   -> RECORD-EMPTY rc=2  REFUSAL RECORD-EMPTY: no REPO rows in ...
  escaping row   -> RECORD-OUTSIDE-ROOT rc=2  REFUSAL RECORD-OUTSIDE-ROOT: /etc resolves outside ...
  L4 observes only: absent-path, unreadable-path  (2 of 4 runtime-reachable RECORD-* classes)
```

MUT-B (transposing `RECORD-EMPTY` and `RECORD-OUTSIDE-ROOT`) therefore passes **both** analyzers
and **both** instruments — because neither ever observes those two classes. Whatever the r40 frozen
list turns out to contain, "all observed pairs" is only as strong as that list, and the list is not
in bytes.

## 6. A bounded measurement plan for the r40 counter (the strengthening that kills the mutants)

The mutants die under a check that (i) masks sibling class tokens out of the haystack before
matching, (ii) requires a whole-word trigger, and (iii) requires the two observed classes' entries
to name **disjoint** trigger sets. Measured verdicts are in §3.1 (`STRENGTHENED` column):

- **S1 — mask sibling class tokens, then require a whole-word trigger.** Kills MUT-A, MUT-D, MUT-E,
  MUT-G. (Masking is necessary because `RECORD-MISSING` contains `missing`; this is the mechanism
  behind the whole class of survivors.)
- **S2 — cross-class trigger exclusivity.** Kills MUT-F (the `RECORD-MALFORMED` entry claiming the
  unreadable-path trigger).
- **S3 — require a non-empty entry for every observed class**, so the frozen list is actually
  covered rather than silently absent.
- **Pin the join rule** in the counter's own docstring (indent / until-next-class-token /
  paragraph) — §3.4 shows the verdict moves with the rule.
- **Land the frozen list as bytes** (a committed pairs file, hashed and revision-bound like the
  r39 `c1-items.tsv`), so "all observed pairs in the frozen list" is checkable and the r40 counter
  cannot choose a weaker list after the fact.

With S1+S2+S3 the pristine bytes still PASS (claims `['enoent','missing','non-regular']` /
`['cannot be opened','eacces','eloop']`) and every mutant above is killed.

**This is a coverage finding, not a licence to change the frozen contract.** The prereg is frozen;
S1/S2/S3 are offered as a *measurement plan* for the r40 counter, whose implementation the round
still has to write. I do not claim the frozen predicate is wrong — I claim that the analyzer it
mandates, implemented in the natural way, does not deliver the discrimination the predicate
asserts, and that three specific committed mutants survive it.

## 7. Integrity, reproduction, scratch

**Lane untouched.** The only path written under the lane is this report.

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain
?? census/round-40/
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e
```

(`census/round-40/` was already untracked before this seat began — it is the preregistration
directory itself, present at the tip and not authored here.)

**Reproduction of the committed r39 receipt** (proves the harness is faithful):

```
$ python3 -B census/round-39/c2-counter.py --root . \
    --rev 2f6e981a105fc759205767d2a749a5f7d4fd0b8a \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
```

This matches `census/round-39/records/c2-after.txt` line for line (`SUMMARY legs=6 pass=6 fail=0
harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484`).

**Byte hashes — pristine / mutant / restored.**

```
pristine tool sha256 = e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
MUT-A  tool sha256    = bd71430327a48bc1a3fca83396156ec378068b96c3e44dc12fdc44a1195c9ae9
restored tool sha256  = e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
restored == pristine  : True
fixture git status    : (clean)
```

The fixture's drift bytes were restored to the exact base blob (`git show
0242085:tools/souji-worktree-drift.py`), committed, and re-hashed to the pristine digest above;
the fixture worktree is clean.

**Scratch.** `/fast/scratch/hyaku/souji-r40/R40mutationtester44` (harness `l4probe.py`,
`attack.py`, `r40leg.py`, `mutate.py`, `battery.py`, `matrix.py`, `scope.py`, `tighten.py`,
`monotone.py`, logs `*-log.txt`, and the fixture clone) — **removed before yield**. No file under
`/tmp`. No PATH directory, `~/.local/bin`, fleet-root tracked file, `.ufo/state`, watchdog,
operator config, template or fleet script was written.

## 8. Verdict

| claim | verdict |
|---|---|
| r40 C2 predicate (prereg line 8), as written | **ATTACKED, not refuted.** The predicate is falsifiable and I falsified one of its mandated implementations. |
| The r40 L4 analyzer "joins wrapped continuation lines into one class entry" | **ACHIEVABLE but UNDER-SPECIFIED.** Three defensible join rules disagree on identical bytes (MUT-C: FAIL/FAIL→PASS/PASS). The rule must be pinned in the counter's bytes. |
| r40 analyzer vs r39 one-line control, on the wrapped-trigger probe | **REPRODUCED.** r39 one-line FAILs the probe; all three join rules PASS it. The stated control arm holds. |
| r40 analyzer's *discrimination* vs the r39 control it replaces | **REGRESSED — the falsifier.** Joining is monotone-widening on a substring check: 0 monotonicity violations, 2 committed mutants (MUT-A, MUT-D) that name the **wrong class** and contradict runtime are **killed by the r39 control and PASS the r40 joined analyzer**. Measured on the real committed `census/round-39/c2-counter.py` fixture (§3.2). |
| "all observed class/trigger pairs in the frozen list" | **NOT CHECKABLE AS WRITTEN.** No frozen list exists in committed bytes; the r39 leg observes 2 of the 4 runtime-reachable `RECORD-*` classes, so MUT-B (transposed `RECORD-EMPTY`/`RECORD-OUTSIDE-ROOT`) passes every analyzer and both instruments. |
| A strengthening that kills the battery while the pristine bytes still pass | **PROVIDED (S1+S2+S3 + pinned rule + landed list).** Pristine PASS, all six mutants FAIL. Offered as a measurement plan for the r40 counter, not as a change to the frozen contract. |

**Bottom line.** The frozen r40 C2 predicate can be satisfied by a docstring that names the wrong
class, because the check it mandates is a substring test over a haystack that joining only
enlarges. The round's own r39 lesson (`corpus/lessons/round-39.md`, mistake M1) records that the
paragraph-joining variant was already **reverted** in r39 for a related reason; r40 proposes to
re-admit it. Before the r40 counter is written, the r40 C2 leg needs (a) the join rule pinned in
bytes, (b) the frozen list landed as revision-bound bytes, and (c) sibling-class-token masking plus
whole-word and cross-class-exclusive trigger matching — otherwise the r40 L4 leg will report
`PASS` on a drift docstring that is false about its refusal classes, which is precisely the R10
defect class C2 exists to police.

## 9. Verification gaps (what I did not run)

- I did not run the C1 or C3 counters; they are outside this seat's axis.
- The r40 counter does not exist yet (round-40 has only `preregistration.txt`), so the r40-style
  leg in `r40leg.py` is my reconstruction of the prereg's wording, not committed r40 bytes. Every
  claim about the *r40-style* verdict is labelled as such; every claim about the *r39* verdict
  comes from the real committed `census/round-39/c2-counter.py` run in §3.2.
- I did not test ELOOP, EISDIR, non-regular-file, schema-mismatch, duplicate-name or TOTAL-mismatch
  triggers beyond noting that the L4 leg does not observe them; MUT-B and MUT-E/F isolate two of
  those classes only.
- No semantic proof is offered for prose: every claim about a docstring is a measured token
  observation over the exact entry text printed in the receipts, plus the raise sites at
  `tools/souji-worktree-drift.py:129-139` (ENOENT → `RECORD-MALFORMED`; other errno →
  `RECORD-MISSING`).
- I did not attempt to weaken or strengthen any committed instrument; the S1/S2/S3 rule exists
  only in scratch and is offered as a plan.
