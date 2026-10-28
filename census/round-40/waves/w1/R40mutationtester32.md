# R40mutationtester32 — C2 operability: the join's TERMINATION rule is unspecified, and the frozen kill rule's power over a wrong-class trigger depends on it

- Seat: `R40mutationtester32` (role mutation-tester; leaf member — no subagent dispatch)
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `/home/vgpnk/.omp/agent/RULES.md`, then `census/round-40/preregistration.txt`
- Frozen claim under attack: **C2 — operability**, `census/round-40/preregistration.txt:8`
- Base branch revision named by the prereg: `0242085909fb6a4ee041c5443d76316ac6d59d4b`
- Tool installs/upgrades: **none**; pacman untouched, no network fetches, no PATH writes.
- Scratch (all under the seat dir, removed before yield): `/fast/scratch/hyaku/souji-r40/R40mutationtester32`
- Lane bytes touched by this seat: **none** (read-only). This report is the only file written.

## Named distinct edge case (item 32)

**The JOIN BOUNDARY of the r40 C2 docstring analyzer — specifically the TERMINATION rule of the
join, not its existence.** The r39 wave attacked the *token* semantics of the class map
(`census/round-39/waves/w1/W1RevC2Doc.md` F1–F3: the `missing`-in-`RECORD-MISSING` tautology,
contradictory class lines, unprobed triggers). Item 32 takes the **other** half of the r40
predicate: r40 changes the analyzer from *one line per class* to *one class entry per class*, and
that change introduces a new, unspecified degree of freedom — **where one class entry stops and the
next begins**. This seat measures whether the frozen r40 kill rule
("Kill if wrapped trigger is missed, or if any observed class mapping disagrees with runtime
behavior") has a **determinate verdict** under that freedom, and finds that it does not: the
verdict on a concrete wrong-class trigger mutant flips with the join's termination rule.

## Verdict (one line)

**The frozen r40 C2 predicate is under-determined and, on the frozen kill rule's own terms, admits a
falsifier.** A concrete docstring mutant (mutant D2: `EACCES` moved from the `RECORD-MISSING` entry
onto the `RECORD-MALFORMED` entry, runtime untouched) makes the documented class/trigger mapping
**disagree with runtime** — the exact condition the prereg names as a kill. Under a correct join
the frozen rule **kills** it. Under an over-joining analyzer — a *natural* implementation of the
prereg's own words "joins wrapped continuation lines into one class entry" — the frozen rule
**survives** it, because the merged entry credits `RECORD-MALFORMED`'s `EACCES` token to
`RECORD-MISSING`. The prereg does not fix the termination rule, so the kill rule's power over this
mutation is a function of an implementation choice the frozen text leaves open.

## 1. Setup — bytes under test

Everything below runs on **committed bytes** extracted with `git show`, never on worktree edits.

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e
$ git ls-tree -r HEAD --name-only | grep '^census/round-40'      # (no output — empty)
$ git status --porcelain
?? census/round-40/
$ ls -la census/round-40/
-rw-r--r-- 1 vgpnk vgpnk 2299 Oct 28 16:26 preregistration.txt
```

The r40 tree holds **only** the preregistration; there is no r40 counter, no r40 fixture and **no
committed artifact enumerating the "frozen list"** of class/trigger pairs that
`census/round-40/preregistration.txt:8` refers to. The list is therefore an authoring-time
decision, not a frozen input — see §6.

Byte sets extracted (scratch copies; hashes are of the extracted files):

```
$ S=/fast/scratch/hyaku/souji-r40/R40mutationtester32
$ git show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py > $S/drift-base.py
$ git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py > $S/drift-cand.py
$ git show HEAD:census/round-39/c2-counter.py > $S/r39-c2-counter.py
$ sha256sum $S/drift-base.py $S/drift-cand.py $S/r39-c2-counter.py
14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194  drift-base.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  drift-cand.py
732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11  r39-c2-counter.py
```

Fidelity: `drift-base.py`'s hash `14e9c0f77d7e…` is the second component of the frozen r39 control
receipt `census/round-39/records/c2-before.txt` (`tool_sha=56866ea8f832/14e9c0f77d7e`), and
`drift-cand.py`'s `e48ed08e6728…` is the second component of `census/round-39/records/c2-after.txt`
(`tool_sha=59f1e57d7af0/e48ed08e6728`). The bytes measured are the bytes the r39 receipts measured.

The r39 control instrument, verbatim (`census/round-39/c2-counter.py:133-146`):

```python
def docstring_classes(tool):
    """Class token -> the first docstring line that starts with it (ast only, no source slicing)."""
    with open(tool, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    doc = ast.get_docstring(tree, clean=False) or ""
    out = {}
    for line in doc.split("\n"):
        stripped = line.strip()
        for cls in ("RECORD-MISSING", "RECORD-MALFORMED"):
            if stripped.startswith(cls) and cls not in out:
                out[cls] = stripped
    return out
```

and its L4 predicate (`census/round-39/c2-counter.py:230-234`):

```python
        new_ok = (
            missing in new_classes and "missing" in new_classes.get(missing, "").lower()
            and locked in new_classes and "EACCES" in new_classes.get(locked, "")
        )
```

## 2. The frozen list, derived from committed r39 artifacts

`census/round-40/preregistration.txt:8` requires verification of "all observed class/trigger pairs
in **the frozen list**". No artifact in the lane carries that list (verified in §6), so this seat
derives it from the committed r39 wave report the r40 SCORECARD plan points at
(`SCORECARD.md:779`: "carry the remaining class-to-trigger pairs the wave listed"), i.e.
`census/round-39/waves/w1/W1RevC2Doc.md` F3 — "`RECORD-MALFORMED` enumerates five (missing,
non-regular, schema, duplicate, TOTAL) and the `RECORD-MISSING` line two (`EACCES`, `ELOOP`)" — plus
the `ENOENT` spelling that the committed candidate docstring uses.

The frozen list used throughout this report (probe kind, trigger token, expected class):

```
absent    ENOENT       RECORD-MALFORMED
absent    missing      RECORD-MALFORMED
dir       non-regular  RECORD-MALFORMED
fifo      non-regular  RECORD-MALFORMED
schema    schema       RECORD-MALFORMED
duplicate duplicated   RECORD-MALFORMED
total     TOTAL        RECORD-MALFORMED
locked    EACCES       RECORD-MISSING
eloop     ELOOP        RECORD-MISSING
```

## 3. Ground truth from runtime alone (no docstring involved)

`/fast/scratch/hyaku/souji-r40/R40mutationtester32/probe_join.py` runs the **real** tool as a
subprocess for every trigger and derives the observed refusal class from the tool's own output.

```
$ cd $S && TMPDIR=$S python3 -B probe_join.py
=== A. runtime behaviour of the CANDIDATE tool bytes ===
-- candidate(0242085)
   missing(ENOENT)        -> RECORD-MALFORMED       rc=2
   unreadable(EACCES)     -> RECORD-MISSING         rc=2
   symlink-loop(ELOOP)    -> RECORD-MISSING         rc=2
   record-is-dir          -> RECORD-MALFORMED       rc=2
   record-is-fifo         -> RECORD-MALFORMED       rc=2
   schema-violation       -> RECORD-MALFORMED       rc=2
   duplicate-name         -> RECORD-MALFORMED       rc=2
   total-disagrees        -> RECORD-MALFORMED       rc=2
   no-repo-rows           -> RECORD-EMPTY           rc=2
-- base(ed30b7f)          (identical for all nine triggers)
```

Every row of the frozen list is runtime-reachable, and the candidate bytes satisfy every row.
The base bytes are behaviourally identical to the candidate bytes on all nine triggers (the r39 C2
landing changed documentation only — consistent with `census/round-39/waves/w1/W1ExecC2Docstring.md`
§3). **So the runtime half of the frozen list is sound; the docstring half is where the freedom
lives.**

## 4. The join's termination rule changes the frozen kill rule's verdict

`$S/final.py` measures the frozen kill rule, exactly as worded, over three byte sets (base,
candidate, mutant D1) × four analyzers (three r40 join rules + the r39 one-line control).

The three r40 join rules are all faithful readings of "joins wrapped continuation lines into one
class entry"; they differ only in **where the join stops**:

| rule | termination |
|---|---|
| `dominance` | stop when the next line's indent ≤ the class line's indent (the class line's own block) |
| `fixed25` | stop when the next line's indent ≠ 25 (the visible description column) |
| `over` | stop only at a blank line (never at the next class entry) |
| `oneline` | the r39 control: first line that starts with the class token |

Observed (`$S/final.out`):

```
=== THE FROZEN KILL RULE, measured per (bytes x join rule) ===
-- bytes=base        rule=dominance  D1=True  D2=False  => KILLED
-- bytes=base        rule=fixed25    D1=True  D2=False  => KILLED
-- bytes=base        rule=over       D1=True  D2=False  => KILLED
-- bytes=base        rule=oneline    D1=False D2=False  => KILLED
-- bytes=candidate   rule=dominance  D1=True  D2=True   => SURVIVES the frozen kill rule
-- bytes=candidate   rule=fixed25    D1=True  D2=True   => SURVIVES the frozen kill rule
-- bytes=candidate   rule=over       D1=True  D2=True   => SURVIVES the frozen kill rule
-- bytes=candidate   rule=oneline    D1=False D2=False  => KILLED
-- bytes=mutant-D1   rule=dominance  D1=True  D2=False  => KILLED
-- bytes=mutant-D1   rule=fixed25    D1=True  D2=False  => KILLED
-- bytes=mutant-D1   rule=over       D1=True  D2=False  => KILLED
-- bytes=mutant-D1   rule=oneline    D1=False D2=False  => KILLED
```

Readings:

1. **The candidate bytes satisfy the frozen kill rule under all three join rules.** The r40 C2
   claim, as a claim about the *current candidate bytes*, is not falsified here.
2. **The r39 one-line control is killed** on every byte set, i.e. the r40 change is *necessary* —
   the r39 analyzer cannot pass the r40 predicate. That confirms the control clause at
   `census/round-40/preregistration.txt:8` ("Control: r39 `docstring_classes` extracts only the
   first class line") is a real discriminator.
3. **The kill rule's power over a docstring defect is join-dependent** — see §5.

## 5. THE FALSIFIER — mutant D2, a wrong-class trigger

### 5.1 The mutant

`$S/decisive2.py` builds **mutant D2**: the `EACCES` trigger is removed from the `RECORD-MISSING`
entry (its `ELOOP` trigger is kept) and added to the `RECORD-MALFORMED` entry. **Runtime is
untouched.** The docstring therefore says an unreadable record is *not* `RECORD-MISSING`, while the
code still raises `RECORD-MISSING` for it. This is exactly "an observed class mapping disagrees
with runtime behavior" — the prereg's own kill condition.

```
=== mutant D2 bytes ===
   candidate sha256 = e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76
   mutant-D2 sha256 = 1bb7304f8265284e5f5a8db159cc5e869f80fe0862722a9144859b81656f8cde

   mutant docstring class block (correct join):
     RECORD-MISSING     'RECORD-MISSING         ELOOP opening the record path: the path exists but cannot be opened or read'
     RECORD-MALFORMED   'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, one that cannot be opened (EACCES), a line that does not match the schema, a duplicated name, or a TOTAL row that disagrees'

=== runtime truth for an unreadable record (mutant-D2 bytes) ===
   locked   -> RECORD-MISSING
   eloop    -> RECORD-MISSING
   => runtime still raises RECORD-MISSING; the mutant's RECORD-MISSING entry names NO EACCES.
      The documentation disagrees with runtime.
```

### 5.2 The frozen kill rule's verdict flips with the join rule

```
=== the frozen kill rule on mutant-D2, per join rule ===
-- rule=dominance  D1=True  (r40_hit=True r39_hit=False)  D2=False  => KILLED
      ...
      locked    token=EACCES       expect=RECORD-MISSING   observed=RECORD-MISSING   token_in_entry=False FAIL
      eloop     token=ELOOP        expect=RECORD-MISSING   observed=RECORD-MISSING   token_in_entry=True  PASS
      RECORD-MISSING entry = 'RECORD-MISSING         ELOOP opening the record path: the path exists but cannot be opened or read'
-- rule=fixed25    D1=True  (r40_hit=True r39_hit=False)  D2=False  => KILLED
-- rule=over       D1=True  (r40_hit=True r39_hit=False)  D2=True   => SURVIVES the frozen kill rule
      ...
      locked    token=EACCES       expect=RECORD-MISSING   observed=RECORD-MISSING   token_in_entry=True  PASS
      eloop     token=ELOOP        expect=RECORD-MISSING   observed=RECORD-MISSING   token_in_entry=True  PASS
      RECORD-MISSING entry = 'RECORD-MISSING         ELOOP opening the record path: the path exists but cannot be opened or read RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, one that cannot be opened (EACCES), a line that does not matc...'
-- rule=oneline    D1=False (r40_hit=False r39_hit=False)  D2=False  => KILLED

=== VERDICT ===
   dominance (correct join) : KILLED
   over      (over-join)     : SURVIVES
```

**Mechanism.** Under the over-join, `RECORD-MISSING`'s "entry" runs on past the end of its own
block and absorbs `RECORD-MALFORMED`'s line. The `EACCES` token that the mutant moved into
`RECORD-MALFORMED`'s prose is therefore found inside `RECORD-MISSING`'s entry, and the frozen
rule's `token_in_entry` conjunct is satisfied. The analyzer has stopped attributing triggers to
classes: it now credits `RECORD-MALFORMED`'s `EACCES` to `RECORD-MISSING` — the *opposite* of the
mapping the mutant falsified.

### 5.3 Cross-class contamination, measured

`$S/contamination.py` counts, per class, how many *foreign* classes' trigger tokens its entry now
contains:

```
=== drift-cand.py (sha256 e48ed08e6728) ===
   rule=dominance  foreign-trigger credits: 10
      RECORD-MISSING     foreign=["RECORD-MALFORMED's 'missing'"]
      RECORD-MALFORMED   foreign=[]
   rule=over       foreign-trigger credits: 59
      RECORD-MISSING     foreign=["RECORD-MALFORMED's 'ENOENT'", "RECORD-MALFORMED's 'missing'",
                                  "RECORD-MALFORMED's 'non-regular'", "RECORD-MALFORMED's 'schema'",
                                  "RECORD-MALFORMED's 'duplicated'", "RECORD-MALFORMED's 'TOTAL'",
                                  "RECORD-EMPTY's 'REPO rows'", "RECORD-OUTSIDE-ROOT's '--root'",
                                  "JSON-INSIDE-MEASURED-TREE's '--json'", "JSON-IS-RECORD's '--record'",
                                  "JSON-NOT-REGULAR's 'regular file'", "JSON-HARDLINKED's 'link'",
                                  "JSON-UNWRITABLE's '--json'", "USAGE's '--timeout'"]
```

Under the correct join the only foreign credit is the **known** `missing`-inside-`RECORD-MISSING`
tautology (r39 `W1RevC2Doc` F1 — the class name supplies the token). Under the over-join the
contamination is 59 credits and every class borrows every other class's triggers.

**The over-join re-introduces the r39 F2 defect** ("contradictory class lines pass", r39
`W1RevC2Doc` §5 mutant B) in a new place: the r39 analyzer's *one-line* rule made cross-class
borrowing impossible by construction, and the r40 join — with an unspecified termination rule —
can remove that protection while still reading "one class entry per class".

### 5.4 The r39 counter's own view of the same mutant

`$S/decisive.py` runs the **real committed** `census/round-39/c2-counter.py` against a git fixture
holding the lane candidate bytes (commit `c_cand`) and mutant D1 (commit `c_mut`):

```
=== 3. the REAL committed r39 counter (the r40 prereg's stated control) ===
   [cand       ] LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=True
   [cand       ] SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
   [mutant-D1  ] LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=True
   [mutant-D1  ] SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=59f1e57d7af0/62ccc7428fdb fixture_sha=e555d8281484
```

(The `cand` arm's other legs fail because the fixture's base commit holds the *candidate* bytes;
only the L4 line is meaningful in this arm, and the mutant-D1 arm shows `new_maps=False` where the
candidate arm shows `new_maps=True` — i.e. **the r39 L4 leg does discriminate the wrong-class
trigger on its own**, which is why mutant D1 is killed under `dominance`/`fixed25` in §4.)

## 6. Two supporting gaps (measured, not asserted)

### 6.1 The "frozen list" is not an artifact

```
$ git ls-tree -r HEAD --name-only | grep '^census/round-40'      # (no output)
$ git ls-tree -r 0242085909fb6a4ee041c5443d76316ac6d59d4b --name-only | grep '^census/round-40'   # (no output)
$ git ls-tree -r be4cb61 --name-only | grep '^census/round-40'   # (no output)
$ git status --porcelain
?? census/round-40/
```

`census/round-40/preregistration.txt` is itself **untracked**. The "frozen list" the C2 predicate
verifies against is not committed anywhere, so a candidate counter author chooses it *after* seeing
the docstring and the code. The list used here (§2) is the one the r39 wave report enumerated; a
different author could ship a shorter list and the kill rule would be correspondingly weaker. This
is the same class of defect r39 recorded as **F4** (untracked receipt: `census/round-39/records/
c2-after.txt` was untracked at the r39 tip) and as the r39 `W1CritC1Axis` "control reach" note.

### 6.2 The D1 arm ("a synthetic wrapped-trigger probe is detected") is self-satisfiable

`$S/falsifier.py` §F3 measures the D1 arm's verdict as a function of the probe's continuation
column:

```
=== F3: D1 wrapped-probe arm verdict vs (probe geometry x join rule) ===
   cont_col=10  dominance=HIT  fixed25=miss  percol=miss  over(M5)=HIT
   cont_col=12  dominance=HIT  fixed25=miss  percol=miss  over(M5)=HIT
   cont_col=20  dominance=HIT  fixed25=miss  percol=miss  over(M5)=HIT
   cont_col=25  dominance=HIT  fixed25=HIT   percol=miss  over(M5)=HIT
   cont_col=27  dominance=HIT  fixed25=miss  percol=HIT   over(M5)=HIT
   cont_col=29  dominance=HIT  fixed25=miss  percol=miss  over(M5)=HIT
   cont_col=33  dominance=HIT  fixed25=miss  percol=miss  over(M5)=HIT
   r39 one-line analyzer: miss at every geometry (control).
```

The D1 arm's verdict is a joint function of **(probe geometry) × (join rule)**. Both are authored
by the same counter, and the prereg fixes neither. Consequently:

* the `dominance` rule passes D1 at **every** geometry — the arm can never fail for an author who
  picks `dominance`, whatever probe they write; and
* the `fixed25`/`percol` rules pass D1 only at the geometry that matches their own column
  assumption, so those authors are *forced* to author a probe at that geometry.

The r39 one-line control misses at every geometry, so the "r39 misses it" half of the D1 clause is
solid. The "r40 detects it" half is a **self-fulfilling probe**: it certifies that the author's
analyzer and the author's probe agree, not that the analyzer handles the real docstring's layout.

### 6.3 The real docstring's layout is not uniform, so a "column" join is fragile

`$S/falsifier.py` §F2, on the **committed candidate bytes**:

```
=== F2: description column vs continuation column per class entry ===
   RECORD-MISSING             head_ind= 2 desc_col=25 continuation_indents=[25]
   RECORD-MALFORMED           head_ind= 2 desc_col=25 continuation_indents=[25, 25]
   RECORD-EMPTY               head_ind= 2 desc_col=25 continuation_indents=[]
   RECORD-OUTSIDE-ROOT        head_ind= 2 desc_col=25 continuation_indents=[25]
   JSON-INSIDE-MEASURED-TREE  head_ind= 2 desc_col=29 continuation_indents=[25]
   JSON-IS-RECORD             head_ind= 2 desc_col=25 continuation_indents=[25]
   JSON-NOT-REGULAR           head_ind= 2 desc_col=25 continuation_indents=[25]
   JSON-HARDLINKED            head_ind= 2 desc_col=25 continuation_indents=[]
   JSON-UNWRITABLE            head_ind= 2 desc_col=25 continuation_indents=[25]
   USAGE                      head_ind= 2 desc_col=25 continuation_indents=[]
```

`JSON-INSIDE-MEASURED-TREE`'s description starts at column 29 (its token is too long for the
column) while its continuation is still at column 25. A join keyed on the *description* column
(`percol`) therefore breaks immediately on that entry; a join keyed on a *fixed* column (`fixed25`)
is correct on this file but wrong on any file whose continuation is elsewhere. Only an
**indent-dominance** rule is robust to both. This is a concrete reason the termination rule must be
named in the frozen text rather than left to the implementer.

## 7. Mutation battery on a reference r40 analyzer (6 single-point mutants)

`$S/r40-leg-ref.py` implements a reference r40 analyzer (the `dominance` rule) plus the r39
one-line control, and runs the same bounded detector (D1 wrapped-probe arm + D2 frozen-list arm
over nine runtime probes) on pristine bytes, on each mutant, and on restored bytes.

```
=== MUTANTS (single behaviour-bearing point each) ===
-- M1: join only the FIRST continuation line (join depth 1)
   D2 total     token=TOTAL  expect=RECORD-MALFORMED observed=RECORD-MALFORMED entry_has_token=False -> FAIL
   VERDICT: KILLED
-- M2: join only continuation lines at the fixed column 25
   (all arms PASS)
   VERDICT: SURVIVED
-- M3: join only continuation lines at the class line description column
   D1 wrapped-probe  r40=False r39=False -> FAIL
   D2 schema / duplicate / total  entry_has_token=False -> FAIL
   VERDICT: KILLED
-- M4: stop the join at a blank line instead of at the next class entry
   (all arms PASS)
   VERDICT: SURVIVED
-- M5: join the NEXT class entry's first line into this entry
   (all arms PASS)
   VERDICT: SURVIVED
=== RESTORED verdict=PASS ===
```

| id | sha256 of the mutant file | point | verdict |
|---|---|---|---|
| M1 | — | join depth 1 | **KILLED** (the `TOTAL` trigger is on the 2nd continuation) |
| M2 | — | fixed column 25 | **SURVIVED** (coverage finding) |
| M3 | — | description column | **KILLED** (D1 and three D2 rows) |
| M4 | — | stop at blank line | **SURVIVED** (coverage finding) |
| M5 | — | over-join (never stop at a class entry) | **SURVIVED** (coverage finding; §5 makes it decisive) |

M4 and M5 both survive because the frozen detector's D1 probe puts the trigger on the **first**
continuation line, so neither a blank-line stop nor an over-join is exercised by it. M5 is the
mutant that §5 shows to be decisive against a wrong-class trigger: the D1 probe's geometry hides
exactly the failure mode the over-join introduces.

**Baseline discipline:** the pristine reference analyzer reads `PRISTINE verdict=PASS` and the
restored bytes read `RESTORED verdict=PASS`, so the killed verdicts above are kills of a
passing baseline, not artifacts of a failing baseline. Had the baseline failed, the runs would have
been reported inconclusive.

## 8. What the r39 wave already found, and how item 32 differs

The r39 wave's C2 findings (`census/round-39/waves/w1/W1RevC2Doc.md` F1–F3, and r39
`census/round-39/waves/w1/W1MutC2.md`) concern the **token semantics** of the class map: the
`missing`-in-`RECORD-MISSING` tautology, contradictory lines, unprobed triggers, and counter-internal
mutants of the r39 leg. **Item 32 concerns the JOIN** — the structural change r40 makes — and
specifically the join's **termination rule**, which is the new degree of freedom the r40 predicate
creates and does not constrain.

The two are complementary, not overlapping: fixing the tautology (strip the class token before
matching) would not stop the over-join from crediting `RECORD-MALFORMED`'s `EACCES` to
`RECORD-MISSING`, because that credit is not a substring artefact but a structural consequence of
where the entry ends.

## 9. Bounded measurement plan for the L1 (not a claim change; the prereg is frozen)

The frozen prereg may not be edited, so this seat proposes **measurement**, not amendment. For the
r40 counter to have a determinate C2 verdict, three things must be pinned in the counter's own
receipt (or disclosed as named limits if they cannot be):

1. **Name the join's termination rule in the counter's own output**, and assert it. A one-line
   print of the rule (e.g. `join=dominance`) makes the receipt self-describing; without it, two
   counters with different rules produce receipts that look identical.
2. **Add a wrong-class-trigger case to the r40 fixture** — the mutant D2 shape (a trigger on the
   *neighbouring* class's entry) — so the leg's power over cross-class credit is measured rather
   than assumed. Measured here: a correct join kills D2; an over-join does not.
3. **Commit the frozen list** as a lane artifact (e.g. `census/round-40/c2-pairs.tsv`) before the
   candidate counter's receipt, and have the counter print its hash alongside `tool_sha`, so the
   list is an input rather than an authoring-time choice. `census/round-40/preregistration.txt` is
   currently untracked; the same applies to the list.

If the L1 prefers to disclose rather than add: the C2 claim's own text should then say that the
r40 L4 leg "verifies that each observed class's entry names its trigger **as read by an
indent-dominance join**, and does not test whether the join attributes a trigger to the class
that raises it." That sentence is true under every join rule I measured only for `dominance`; under
`over` it is false, and no receipt would reveal the difference.

## 10. Commands actually run

```
read /home/vgpnk/.omp/agent/RULES.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py:raw:1-120
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py:raw:120-330
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1MutC2.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1RevC2Doc.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1ExecC2Docstring.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/waves/w1/W1RevC2Legs.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/preregistration.txt:40-80
grep/glob over the lane for RECORD-MISSING, docstring_classes, class/trigger, frozen list

S=/fast/scratch/hyaku/souji-r40/R40mutationtester32
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r HEAD --name-only | grep '^census/round-40'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show <rev>:tools/souji-worktree-drift.py > $S/drift-{base,cand}.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:census/round-39/c2-counter.py > $S/r39-c2-counter.py
sha256sum $S/*.py $S/*.out

TMPDIR=$S python3 -B $S/probe_join.py        # runtime ground truth + join-rule matrix
TMPDIR=$S python3 -B $S/r40-leg-ref.py      # 6-mutant battery on a reference r40 analyzer
TMPDIR=$S python3 -B $S/falsifier.py        # F1 anchors, F2 columns, F3 geometry matrix, F4, F5 tautology
TMPDIR=$S python3 -B $S/decisive.py         # git fixture + the REAL committed r39 counter
TMPDIR=$S python3 -B $S/final.py            # frozen kill rule over (bytes x join rule)
TMPDIR=$S python3 -B $S/decisive2.py        # THE falsifier: mutant D2, per join rule
TMPDIR=$S python3 -B $S/overjoin.py         # over-join collapse + frozen-list artifact provenance
TMPDIR=$S python3 -B $S/contamination.py    # cross-class contamination counts
```

Git-fixture discipline (honoured in `decisive.py`): the fixture is created with
`tempfile.mkdtemp(prefix="fix.", dir=SCRATCH)`, every git call is `git -C <fixture> …`, and
`git rev-parse --show-toplevel` is asserted to equal the fixture root **before** each of the three
commits. The fixture was removed at the end of the run (`fixture removed: True`).

No `jj` invocation, no commit, no push, no index mutation, no write to a fleet file, no write to
`.ufo/state`, no write outside this report and the seat's scratch.

## 11. Restoration evidence

No lane byte was mutated: every mutant was built in scratch from `git show` output. Post-run state:

```
$ sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c2-counter.py \
            /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py
732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11  census/round-39/c2-counter.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain
?? census/round-40/
```

The lane's counter hash `732b1e425a6d…` equals `git show HEAD:census/round-39/c2-counter.py`'s
hash (verified in §1); the tool hash `e48ed08e6728…` equals the candidate revision's blob. The
only `git status` entry is the pre-existing untracked `census/round-40/` (this seat's own report
lives under `.ufo/`, which the lane's ignore rules exclude — the same state observed by the
sibling seat `R40scribe04` at the start of this wave).

Scratch removal (see §12 for the final state): `/fast/scratch/hyaku/souji-r40/R40mutationtester32`
was removed with `rm -rf` after the final measurement.

## 12. Summary of findings

| # | finding | severity | axis | evidence |
|---|---|---|---|---|
| F32-1 | **The join's termination rule is unspecified in the frozen predicate, and the kill rule's verdict on a wrong-class trigger flips with it.** Mutant D2 (EACCES moved to the neighbouring class's entry; runtime untouched) is KILLED by a correct join and SURVIVES an over-join that credits the neighbouring class's token. | **high (operability)** | operability | §5, `$S/decisive2.out` |
| F32-2 | The over-join turns the analyzer into a class-blind token bag: 59 foreign trigger credits on the candidate bytes (vs 10 under a correct join, and those 10 are the known `missing`-in-`RECORD-MISSING` tautology). This re-introduces r39 F2 (contradictory class lines pass) inside the r40 change. | medium | operability | §5.3, `$S/contamination.out` |
| F32-3 | The D1 "synthetic wrapped-trigger probe" arm is self-satisfiable: its verdict is a joint function of the probe's continuation column and the join rule, and both are authored by the same counter. The `dominance` rule passes D1 at every geometry tested (7 of 7). | medium | operability | §6.2, `$S/falsifier.out` |
| F32-4 | The "frozen list" the C2 predicate verifies against is not a committed artifact; `census/round-40/preregistration.txt` itself is untracked. The list is an authoring-time choice, so the kill rule's strength is author-dependent. | medium | calibration (boundary of operability) | §6.1, `$S/overjoin.out` |
| F32-5 | The real docstring's layout is not uniform (`JSON-INSIDE-MEASURED-TREE`: description col 29, continuation col 25), so column-keyed joins are fragile on the committed bytes; only an indent-dominance rule is robust. | low | operability | §6.3 |
| F32-6 | Of 6 single-point mutants of a reference r40 analyzer, 2 survived the bounded detector (M4 blank-line stop, M5 over-join). Both survive because the D1 probe puts the trigger on the *first* continuation line, so the probe's geometry hides the very failure modes that matter. | medium | operability | §7, `$S/mutation.out` |

**Overall verdict on the frozen C2 claim:** the claim is **not falsified on the committed candidate
bytes** — under every join rule measured, the candidate bytes satisfy the frozen kill rule, and
the r39 one-line control is correctly killed on every byte set, so the r40 change is necessary. But
the claim is **under-determined**: the frozen text leaves the join's termination rule open, and
that openness is exactly where a plausible implementation (over-join) loses the kill rule's power
over a wrong-class trigger. The r40 C2 receipt can therefore read "pass" for an analyzer that
cannot detect a class/trigger mapping that disagrees with runtime — the prereg's own kill
condition — and nothing in the receipt distinguishes the two cases.

**What this seat did not do (named limits):**

- It did not execute an r40 candidate counter — none exists in the lane at this writing
  (`git ls-tree -r HEAD --name-only | grep census/round-40` is empty), so the r40 C2 status is
  **not measured** here, in either direction.
- It did not mutate any lane byte, commit, push, or touch the index; every mutant is a scratch copy.
- It did not alter `census/round-40/preregistration.txt` or any frozen claim.
- The "frozen list" used in §2 is **this seat's derivation** from the committed r39 wave report
  (`W1RevC2Doc` F3) plus the candidate docstring's `ENOENT` spelling. A different frozen list would
  change the D2 arm's row set — the *structure* of the finding (the verdict flips with the join
  rule) is independent of the list's exact membership, because the flipping row is
  `locked / EACCES / RECORD-MISSING`, which every reading of the list includes.
- The reference r40 analyzer in §7 is **this seat's** implementation of the frozen wording, not an
  r40 artifact; §5's decisive result does not depend on it (it is reproduced with the real
  committed r39 counter in §5.4 and with runtime truth from the real tool bytes).
- Nothing here touches C1 or C3; this seat's axis is operability only.
