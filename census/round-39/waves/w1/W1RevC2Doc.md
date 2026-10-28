# W1RevC2Doc — C2 L4 attacked: a docstring can name both triggers and still be wrong

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Measured revision (lane tip): `2201778e7736af82e7d8a42dec2494f115bf3923`
  (`round-39: PROVINCE boundary note — two tool contracts repaired, no receipt class, certification OFF`)
- Base revision under test: `ed30b7f5b77939c9073348d810730bc4f355708d`
- Frozen contract read first: `census/round-39/preregistration.txt` (C2 legs L1-L6, predicate
  `SUMMARY legs=6 pass=6 fail=0 harm=0`)
- Role: reviewer (advisory; nothing committed, pushed or mutated in the lane)
- Scratch: `/fast/scratch/hyaku/souji-r39/W1RevC2Doc` (created and removed — see §Scratch)
- Tool installs: none. Read-only git only (`show`, `rev-parse`, `archive`, `status`, `diff`,
  `cat-file`); the single `git init` is inside the scratch fixture, toplevel asserted below.

## Verdicts in one line each

| check | verdict |
|---|---|
| C2 counter at `2201778` (the after reading) | **PASS** — `SUMMARY legs=6 pass=6 fail=0 harm=0`, reproduces `census/round-39/records/c2-after.txt` line for line |
| C2 counter at `ed30b7f` (the frozen control) | **PASS (control honest)** — `pass=2 fail=4 harm=0`, reproduces `c2-before.txt` including `tool_sha=56866ea8f832/14e9c0f77d7e` |
| **L4 vs the assigned mutant A** (docstring `RECORD-MALFORMED` line says "missing"; code raises `RECORD-MISSING` for a missing path) | **NOT CAUGHT** — the real counter prints `LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False` |
| L4 vs mutant B (both class lines name both triggers, contradictory) | **NOT CAUGHT** — `LEG L4 PASS ... new_maps=True`; the r38 record fixture also stays 10/10 |
| L4 vs mutant C (non-regular path raises `RECORD-MISSING`, docstring says `RECORD-MALFORMED`) | **NOT CAUGHT** — `LEG L4 PASS`; r38 record 10/10 and r36 worktree 12/12 |
| Who does kill mutant A | `tests/fixtures/r38-drift-record.py` `case-missing-record` (9/10) → counter `harm=1`; L4 contributes nothing |
| Frozen predicate at the tip | **HOLDS** — but L4's own docstring claim ("requires the docstring line that starts with that class to name its trigger (missing / EACCES)") is wider than what the rule enforces; see F1 |

## 1. Setup — bytes under test

```
$ mkdir -p /fast/scratch/hyaku/souji-r39/W1RevC2Doc/lane
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive HEAD | tar -x -C /fast/scratch/hyaku/souji-r39/W1RevC2Doc/lane
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tools/souji-worktree-drift.py > .../mut/drift-head.py
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed30b7f5b77939c9073348d810730bc4f355708d:tools/souji-worktree-drift.py > .../mut/drift-base.py
$ sha256sum .../mut/*.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  drift-head.py   (HEAD)
14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194  drift-base.py   (base)
6d33a5de3a71fb128036ed05bdd63476088204b20929aa10025cc6b7f4274423  drift-A.py
c1944b185022de9f12e551838ae267a2070468cea05f260ba73d21ffd12d2b05  drift-B.py
48d9fd9bfd40339e4381dbfffa478b20068c8b6df0da1953d7d02c3ad3bc5ff9  drift-C.py
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat HEAD -- tools/souji-worktree-drift.py census/round-39/c2-counter.py
(no output — both worktree files identical to HEAD)
```

`drift-base.py`'s hash `14e9c0f77d7e…` is the second component of `c2-before.txt`'s
`tool_sha=56866ea8f832/14e9c0f77d7e`, so the base bytes I mutated are the bytes the frozen control
measured.

## 2. The landed after reading and the frozen control, reproduced

```
$ python3 -B census/round-39/c2-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch /fast/scratch/hyaku/souji-r39/W1RevC2Doc/ctr
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc=0
```

Identical to `census/round-39/records/c2-after.txt` (same six `LEG` lines, same `SUMMARY`, same
`tool_sha`/`fixture_sha`). **Verdict: the C2 after predicate holds at the measured tip.**

```
$ python3 -B census/round-39/c2-counter.py --root <lane> \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --scratch .../ctr3
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=7ab7c3d85a81
rc=1
```

Byte-identical to `c2-before.txt`. **Verdict: the control receipt is honest and reproducible; the
do-nothing state does not satisfy the predicate.**

## 3. The rule under attack, quoted from the frozen counter

`census/round-39/c2-counter.py:214-236` (identical bytes in the worktree and in the `HEAD` archive;
`diff` printed `IDENTICAL`):

```python
        missing = classify(run_drift(new_drift, root, os.path.join(base_scratch, "absent.tsv")))
        os.chmod(probe, 0)
        locked = classify(run_drift(new_drift, root, probe))
        ...
        new_ok = (
            missing in new_classes and "missing" in new_classes.get(missing, "").lower()
            and locked in new_classes and "EACCES" in new_classes.get(locked, "")
        )
```

with `docstring_classes` storing **the whole stripped line, class token included**
(`census/round-39/c2-counter.py:133-146`: `if stripped.startswith(cls) … out[cls] = stripped`).

Consequence, stated before any mutant is run: for the missing trigger the second conjunct is
`"missing" in "<the observed class line>".lower()`. When the observed class is `RECORD-MISSING` the
line *begins with the string `RECORD-MISSING`*, which already contains `missing`. The conjunct is
therefore a tautology on that branch — it cannot fail no matter what the prose says:

```
$ python3 -B - <<'PY'   # direct measurement of the substring, not a paraphrase
VACUOUS: 'RECORD-MISSING' -> 'missing' present: True
VACUOUS: 'RECORD-MISSING         no prose at all' -> 'missing' present: True
VACUOUS: 'RECORD-MISSING         EACCES or ELOOP' -> 'missing' present: True
PY
```

## 4. Mutant A — the assigned attack (docstring says "missing", code raises `RECORD-MISSING`)

Construction: `drift-A.py` = `drift-head.py` with the `ENOENT` branch changed (docstring untouched, so
the `RECORD-MALFORMED` line still reads `a missing (ENOENT) or non-regular record path`):

```python
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise Refusal("RECORD-MISSING: %s" % exc)      # was RECORD-MALFORMED: … not a regular file
        raise Refusal("RECORD-MISSING: %s" % exc)
```

Fixture repo (scratch only; toplevel asserted before the first commit):

```
$ F=/fast/scratch/hyaku/souji-r39/W1RevC2Doc/fix
$ cp -a .../lane $F && git -C $F init -q && git -C $F rev-parse --show-toplevel
/fast/scratch/hyaku/souji-r39/W1RevC2Doc/fix
$ git -C $F add -A && cp drift-base.py $F/tools/souji-worktree-drift.py && git -C $F add -A \
    && git -C $F commit -qm base
b8d832b8266e0f9fb7c75cdd3f7922e88a39d83c     (c0 = HEAD tree, drift bytes = base)
2cf33e9660541a49574e9988837bb100ba688584     (c1 = mutant A)
```

The real counter, `--rev c1 --base-rev c0` (only the L4/L6 lines are meaningful here; the citation
tool is identical at both revs, so L1/L2/L5 are expected to fail and are not evidence):

```
$ python3 -B $S/lane/census/round-39/c2-counter.py --root $F --rev 2cf33e9660… --base-rev b8d832b826… --scratch $S/ctr2
LEG L4 PASS missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=False
LEG L6 FAIL r38-drift-record=9/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=1 tool_sha=59f1e57d7af0/6d33a5de3a71 fixture_sha=7ab7c3d85a81
rc=1
```

**Verdict: L4's rule does NOT catch the assigned mutant.** `new_maps=True` on a tool whose
documentation is wrong in both directions at once — the `RECORD-MALFORMED` line claims the missing
path while the code raises `RECORD-MISSING` for it, and the `RECORD-MISSING` line's own prose
(`EACCES or ELOOP opening the record path`) excludes it. L4 passes it because
`"missing" in "record-missing …"` is true by construction (§3) and because the only surviving
constraint on that line is the `EACCES` token, which the mutant never removed.

The mutant is nevertheless killed by a *behavioural* surface, not by the docstring leg:

```
$ python3 -B $S/lane/tests/fixtures/r38-drift-record.py --tool $S/mut/drift-A.py --work $S/ctr2
case-missing-record=FAIL rc=2 want=2 missing=['RECORD-MALFORMED', 'not a regular file'] out=["REFUSAL RECORD-MISSING: [Errno 2] No such file or directory: …/absent…tsv"]
SUMMARY cases=10 pass=9 fail=1
```

which is what makes the counter's `harm=1` and its exit 1. So the round is not defenceless against
mutant A — but the leg that claims to police *the docstring↔class mapping* is not the thing that
polices it.

## 5. Mutant B — both triggers named, documentation contradictory (the literal "names both and is wrong")

`drift-B.py` = `drift-head.py` with the `RECORD-MISSING` line widened to claim the missing trigger
too; code untouched, so the claim is false (a missing path raises `RECORD-MALFORMED`):

```
  RECORD-MISSING         EACCES or ELOOP opening the record path, or a missing
                         (ENOENT) path: the path exists but cannot be opened or read
  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
```

```
$ … --rev 2fd1bf5f31… --base-rev b8d832b826…
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L6 PASS r38-drift-record=10/10(base 10/10) … 
$ python3 -B $S/lane/tests/fixtures/r38-drift-record.py --tool $S/mut/drift-B.py --work $S/ctr2
SUMMARY cases=10 pass=10 fail=0
```

**Verdict: not caught by L4 and not caught by any drift fixture.** The docstring now says a missing
path raises `RECORD-MISSING` *and* `RECORD-MALFORMED`; the rule is satisfied by either class's line
carrying the token, so naming both makes it unfalsifiable. This is the general form the seat was
asked to show: token presence cannot distinguish "the right trigger" from "both triggers".

## 6. Mutant C — a trigger the leg never probes

`drift-C.py` = `drift-head.py` with the post-`fstat` non-regular branch changed to
`raise Refusal("RECORD-MISSING: %s" % path)`; the `RECORD-MALFORMED` line still claims
`a missing (ENOENT) or non-regular record path`.

```
$ python3 -B -   # observed classes via the counter's own classify()
C dir-record class: RECORD-MISSING
head dir-record class: RECORD-MALFORMED
$ … --rev ccd44d05d9… --base-rev b8d832b826…
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) …
$ python3 -B $S/lane/tests/fixtures/r36-worktree-drift.py --tool $S/mut/drift-C.py --work $S/ctr2
SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
```

**Verdict: not caught.** L4 probes exactly two triggers (missing path, `EACCES`), while the
`RECORD-MALFORMED` line enumerates five (missing, non-regular, schema, duplicate, TOTAL) and the
`RECORD-MISSING` line two (`EACCES`, `ELOOP`). Four of those seven documented triggers have no probe
at all; a false statement about any of them is invisible to L4.

## 7. What a mechanical tightening would buy (measured, not proposed on faith)

Stripping the class token before the token match — `dc[cls][len(cls):].lower()` — is a one-line,
byte-level change. Measured with the counter's own `classify`/`docstring_classes` on the same bytes:

```
drift-head.py   missing=RECORD-MALFORMED locked=RECORD-MISSING   frozen=True  tightened=True
drift-base.py   missing=RECORD-MALFORMED locked=RECORD-MISSING   frozen=False tightened=False
drift-A.py      missing=RECORD-MISSING   locked=RECORD-MISSING   frozen=True  tightened=False
drift-B.py      missing=RECORD-MALFORMED locked=RECORD-MISSING   frozen=True  tightened=True
drift-C.py      missing=RECORD-MALFORMED locked=RECORD-MISSING   frozen=True  tightened=True
```

The tightening kills mutant A and keeps the landed bytes passing; it does nothing about B or C,
because those are not substring artefacts — they are the structural limit of a two-probe token check.
(For completeness: removing the `EACCES` token from the `RECORD-MISSING` line does fail the frozen
rule — the `EACCES` conjunct is a genuine check — so the rule's only effective constraint on the
`RECORD-MISSING` line is the presence of `EACCES`.)

## 8. Honest limit of the token-presence docstring check (r38 M5, recurred)

r38 M5 (`corpus/lessons/round-38.md:113-124`) bound the `docstring-enum` case to *textual token
presence*, "not that each token is reachable or that its trigger is documented", and the round's own
named-limits list repeats it (`:180-182`). C2 L4 is the same instrument applied to the two record
class lines, and its limit is strictly worse than M5's because of §3:

1. **One of its four token probes is a tautology.** For a missing path that raises `RECORD-MISSING`,
   the "missing" token is supplied by the class name itself. L4's missing-trigger half therefore
   verifies only *that the class is documented at all*, never that the line names the trigger. This is
   not "the case is narrow"; it is a conjunct that cannot be false on the branch it is meant to test.
2. **Contradiction is indistinguishable from correctness.** A line naming both triggers passes even
   when the two lines contradict each other (mutant B).
3. **Two probes cannot witness a line that enumerates five triggers** (mutant C); `ELOOP`, non-regular,
   schema, duplicate and TOTAL claims are unverified.
4. **Prose falsehood is out of scope by construction.** Any token check accepts "a missing path is a
   `RECORD-MISSING` error" on the `RECORD-MALFORMED` line as long as the observed class's own line
   happens to carry its token.

### Should the round disclose it instead of widening the rule? — Yes, disclose.

- The predicate is frozen and the base control was measured before any after-data; tightening L4's
  analyser now would change the meaning of a leg after its data exists — the same goalpost move the
  round refused in M1 ("rather than loosen the frozen … rule after data"). Symmetry requires refusing
  the post-hoc tightening too.
- Widening cannot reach the property anyway. §7 shows the best mechanical widening buys one mutant
  (A) and still passes B and C; a check that would catch B/C has to compare prose *semantics* against
  raise sites, which no frozen token rule can do honestly.
- The behaviour half of R10 is already covered elsewhere: mutant A dies at
  `r38-drift-record.py:case-missing-record`. What remains uncovered is a docstring that is false while
  the behaviour is right — a documentation defect, exactly what a named limit is for.
- Concrete disclosure text the round can adopt (C2 / L4): *L4 is a two-probe token-presence check on
  the class lines. Its "missing" conjunct matches inside the class name `RECORD-MISSING` and cannot
  fail on that branch; it verifies only that the observed class is documented and that `EACCES`
  appears on the class line that actually raises for an unreadable record. It does not verify that a
  line's other enumerated triggers are correct, and it accepts contradictory lines that name both
  triggers (r39 W1RevC2Doc, mutants A/B/C).* A one-line correction of the counter's own L4 paragraph
  (`census/round-39/c2-counter.py:13-16`) is available and does not change the measurement; landing it
  is the L1's call, not mine.

## Findings by severity

- **F1 (medium, calibration — claim wider than counter).** `census/round-39/c2-counter.py:13-16`
  states L4 "requires the docstring line that starts with that class to name its trigger
  (missing / EACCES)". On the missing branch that requirement is vacuous (class-name substring, §3),
  demonstrated end-to-end: mutant A reads `LEG L4 PASS … new_maps=True` on the real counter. The
  frozen C2 predicate still holds at the tip (§2); the defect is in the leg's stated discrimination,
  not in the summary. Remedy: disclose (§8) and/or correct the L4 paragraph; do not change the rule
  after data.
- **F2 (medium, coverage).** Contradictory class lines pass (mutant B: `LEG L4 PASS`, r38 fixture
  10/10). Any future claim that L4 "verifies the docstring's class mapping" is falsified by B.
- **F3 (medium, coverage).** Four of the seven triggers the two lines enumerate have no probe
  (mutant C: `LEG L4 PASS`, r36 fixture 12/12, r38 record 10/10).
- **F4 (low, evidence binding).** `census/round-39/records/c2-after.txt` is **untracked** at the
  measured tip — `git status --porcelain -- tools census` prints `?? census/round-39/records/c2-after.txt`
  (the before receipt is tracked). It is byte-reproducible from committed bytes (§2) and binds the
  tool via `tool_sha`, so the claim is not weakened today; but the after-evidence can be rewritten
  with no diff trail. Either land it or cite the counter run as the evidence and drop the file from
  the claim.
- **F5 (low, verification gap in the leg).** `old_ok` reuses the **new** tool's observed classes
  (`missing`/`locked` are computed from `new_drift`) against the **old** docstring map. If a future
  mutant changed code and docstring together, the old arm would be scored against the new code's
  classes. Immaterial for the current base/new pair (base really raises `RECORD-MALFORMED` for a
  missing path, confirmed by `case-missing-record` on the base bytes), but it is a latent confound.

## Residual risk

The round's C2 claim — two runnable contracts repaired, predicate `pass=6` at the tip, base control
`pass=2` — is **not falsified** by anything above. What is falsified is the leg's own description:
L4 cannot witness the property its paragraph claims. Residual risk carried into the round-39 report:
a landed drift docstring that is false about the missing trigger or about any non-probed trigger would
read as a pass, and only the r38 fixture's `case-missing-record` (behaviour, not documentation) stands
between that and an undetected R10 recurrence.

## Verification gaps (what I did not run)

- I did not run the c1/c3 counters or the other C2 legs beyond the two full counter runs quoted in
  §2 (L1/L2/L3/L5/L6 were read from those runs only; I did not re-derive their fixtures).
- Mutants were exercised through the real counter over a scratch fixture repo whose citation-tool
  bytes are identical at both revs; therefore only `LEG L4`/`LEG L6` from those runs are evidence, and
  I say so where quoted. The clean `pass=6` reading is the lane run in §2.
- No semantic proof is offered for prose: every claim about the docstring is a measured token
  observation plus the raise site quoted at `tools/souji-worktree-drift.py:129-139`.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1RevC2Doc` was created for this seat and **removed** after the report
was written (`rm -rf`); it is not left on disk. Nothing outside that directory, the report path and
read-only git was written; no PATH directory, `~/.omp`, `~/.config`, fleet-root file, frozen receipt,
`preregistration.txt`, `*-items.tsv` or `*.json` spec was touched.
