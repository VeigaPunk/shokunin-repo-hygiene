# R40connector21 — C3 coverage claim attack: the kill-gate misattribution

Seat: connector (leaf; no subagent dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Frozen contract read first: `census/round-40/preregistration.txt` (C3 paragraph, line 10).
Base revision named by the preregistration: `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
Scratch: `/fast/scratch/hyaku/souji-r40/R40connector21` (removed at exit).
No tool installed or upgraded; `pacman` untouched. No git/jj/index mutation; no lane file written
except this report.

## Axes

- **Coverage** (primary, this seat's declared judged axis): whether the frozen C3 predicate can be
  *measured* at all by the instrument it names, i.e. whether a declared single-defect mutant for the
  invalid-UTF-8 branch can reach `killed=yes` under the r39 counter's scoring rule.
- **Operability** (secondary): whether the C3 counter is re-usable for r40 without inheriting a
  scoring defect.
- Calibration (C1) is **not** assessed by this attack.

## Named distinct edge case (item 21)

**The kill-gate misattribution: the r39 counter's `crash` veto reads the FIXTURE's stdout, and the
house-style fixture detail format re-prints the TOOL's stdout+stderr into the fixture's own stdout —
so a TOOL-side crash is scored as if the FIXTURE had crashed, and the mutant is reported `survived`
even though the fixture detected the difference.**

This is distinct from every sibling in the wave:

| sibling | edge it took | why item 21 differs |
|---|---|---|
| `R40executor39`, `R40executor51` | duplicate/multiple TOTAL multiplicity | item 21 is not about TOTAL at all |
| `R40revenger36` | conflicting duplicate TOTAL rows (first-invalid/last-valid) | same |
| `R40executor63` | invalid UTF-8 as an *uncovered branch* (prior r39 evidence only, no execution) | item 21 **executes** the invalid-UTF-8 branch and shows *why the branch cannot be scored* |
| `R40revenger48` | decoder replacement of invalid UTF-8 in a valid record | same — a *coverage* question, not a *scoring-instrument* question |
| `R40revenger60` | invalid-byte **fixture I/O** (text-mode write, `text=True` capture) | closest sibling; item 21 is **not** about fixture I/O at all — the fixture in item 21 writes the invalid bytes correctly in binary and captures correctly. The defect is in the **counter's kill predicate**, downstream of the fixture. |

Item 21's question is therefore strictly downstream of `R40revenger60`'s: *given a fixture that handles
the invalid bytes correctly, does the counter's kill predicate credit it?* Answer measured: **no.**

## Verdict

**A concrete falsifier of the frozen C3 predicate is established at the instrument level, and it is
repairable without touching the frozen claim.** Two findings, both executed against committed r39
artifacts:

**F1 (falsifier — high severity).** The C3 clause "each declared single-defect mutant is killed by the
r40 fixture" **cannot be satisfied for the invalid-UTF-8 branch by the natural mutant**, under the r39
counter's `score()` rule that the r40 counter inherits. The natural single-defect mutant for that
branch is `decode("utf-8","replace")` → `decode("utf-8","strict")` (the committed r39 wave already
proposed exactly this mutant as `N4` — see `census/round-39/waves/w1/W1MutDriftRules.md:121-127`).
Under that mutant the tool raises `UnicodeDecodeError` and dies with a traceback. The counter's rule
is `killed = proc.returncode == 1 and fails > 0 and not crash`, where
`crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)`
(`census/round-39/c3-counter.py:101-102`) — and `proc` is the **fixture** process. The fixture's own
failure-detail line embeds the tool's captured stdout+stderr verbatim
(`tests/fixtures/r39-drift-record-rules.py:79-80`, same shape in `tests/fixtures/r38-drift-record.py:79`),
so the tool's traceback text lands in the **fixture's stdout**, `crash` flips to `True`, and the kill is
vetoed. Measured: the fixture **did** detect the difference (`SUMMARY cases=6 pass=4 fail=2`, exit 1)
and the counter still reported `killed=no`.

**This is a false negative in the coverage instrument**, and it is *latent* in r39 — no r39 mutant
crashed, so every r39 receipt reads `crash=False` and the defect never fired
(`census/round-39/records/c3-after.txt:3-6`). It fires for the first time on the invalid-UTF-8
branch, which is precisely one of the three branches C3 newly names. The r40 C3 predicate is therefore
falsified *as measurable* on that branch unless the r40 instrument separates "the fixture crashed" from
"the tool crashed and the fixture reprinted it."

**F2 (falsifier — mutant admissibility constraint, medium severity).** C3 also requires that **all
mutants survive the r39 base fixture** ("r39 baseline mutants survive" / `base_killed=0`). One of the
two natural shapes for the *multiple-TOTAL-rows* branch — the mutant that makes the parser require the
TOTAL row to come **after** all REPO rows — is **already killed by both committed base fixtures**
(r39: `cases=7 pass=5 fail=2`; r38: `cases=10 pass=5 fail=5`). It is therefore **inadmissible** as an
r40 C3 mutant: declaring it makes the C3 predicate fail on its own control clause, and the failure is a
*battery* defect, not a coverage defect. The admissible shape for that branch is the duplicate-TOTAL /
first-TOTAL-wins family, which both base fixtures leave alive.

**Neither finding falsifies the coverage claim's substance** — the pristine tool's behaviour on all
three branches is now measured (§3) and the branches are genuinely coverable. The findings falsify
the claim **as an instrument-measurable predicate under the r39 counter's inherited scoring rule**,
and both are one-line repairs. Per the frozen instruction "a missed predicate is reported honestly",
this is reported as a falsifier of measurability, not of the coverage substance.

## 1. Evidence pointers (committed r39 artifacts)

1. **Frozen C3 predicate** — `census/round-40/preregistration.txt:10`:
   > "r40 fixture adds behavioral cases for duplicate/multiple TOTAL rows, `--skip-unrecorded`, and
   > invalid UTF-8 record bytes; each declared single-defect mutant is killed by the r40 fixture, the
   > pristine candidate passes, and all mutants survive the r39 base fixture."
   > "Kill if pristine fails, any mutant survives, any base mutant is killed, or fixture has no own
   > failure summary."

2. **The kill predicate** — `census/round-39/c3-counter.py:96-103`:
   ```python
   def score(fixture, tool, work):
       """Return (killed, detail) — the fixture must report its own failure summary (r38 A5)."""
       ...
       summaries = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY cases=")]
       ...
       crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)
       killed = proc.returncode == 1 and fails > 0 and not crash
   ```
   `proc` is the fixture subprocess. `proc.stdout + proc.stderr` is the **fixture's** stream.

3. **The fixture detail format that carries the tool's output into the fixture's stdout** —
   `tests/fixtures/r39-drift-record-rules.py:76-80`:
   ```python
       out = proc.stdout + proc.stderr
       missing = [t for t in want_tokens if t not in out]
       ok = proc.returncode == want_rc and not missing
       results.append((name, ok, "rc=%d want=%d missing=%r out=%r" % (
           proc.returncode, want_rc, missing, out.replace("\n", " ")[:160])))
   ```
   The r38 base fixture has the same shape (`tests/fixtures/r38-drift-record.py:79`), and its CRLF case
   (`r38-drift-record.py:88`) has it too. The `[:160]` truncation means only the first 160 characters
   of the detail are kept — the traceback header `Traceback (most recent call last):` is the **first**
   line of any Python traceback, so it always survives truncation. This is why the veto is reliable in
   the *wrong* direction.

4. **The tool's decode site** — `tools/souji-worktree-drift.py:147`:
   ```python
           raw = b"".join(chunks).decode("utf-8", "replace")
   ```
   This is the only decode of record bytes. `grep -c 'decode("utf-8", "replace")'` on the tool = **4**
   (lines 147, 190, 197, 304), so the r39 counter's `source.count(old) != 1` anchor rule
   (`c3-counter.py:161-166`) requires the anchor to be the full line
   `        raw = b"".join(chunks).decode("utf-8", "replace")` (count = 1) — verified.

5. **The r39 wave already proposed this exact mutant** — `census/round-39/waves/w1/W1MutDriftRules.md:121-127`
   names `N4` as the `decode("utf-8","replace")` → `"strict"` replacement and `:203-205` describes the
   resulting traceback. The r40 author will reach for it again.

6. **The r39 C3 receipts show the defect is latent** — `census/round-39/records/c3-after.txt:3-6`:
   ```
   MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
   MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
   MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
   MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
   ```
   `crash=False` on all four. No r39 mutant crashed, so the misattribution never fired.

7. **The A5 contract the crash gate exists to serve** — `corpus/lessons/round-38.md:204`:
   > "**A5 (battery kill gate, seat W1RevBattery).** A fixture that printed one `=FAIL` line, a SUMMARY
   > and then crashed scored `killed`; a kill now needs the fixture's own `fail=N` with `N > 0` and no
   > traceback."

   A5's intent is: *the fixture* must not crash. The implementation satisfies that intent but
   over-reaches: it vetoes a kill whenever the traceback **text** appears anywhere in the fixture's
   stream, including text the fixture copied out of the tool.

8. **The r40 candidate artifacts do not exist yet** — `ls census/round-40/` returns only
   `preregistration.txt`; `git status --short` returns `?? census/round-40/`. No r40 counter, fixture,
   mutant, or receipt was available to run. Therefore the *substance* of the C3 claim (pristine pass,
   mutant kills, base survival) is **unmeasured, not pass**; what is falsified here is the
   *measurability* of one of its three branches under the instrument the claim inherits.

## 2. Commands actually run, with outputs

All commands ran from `/fast/scratch/hyaku/souji-r40/R40connector21` with
`TMPDIR=/fast/scratch/hyaku/souji-r40/R40connector21`, against the **committed** base tool bytes
(`git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py`, sha256
`e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`, identical to HEAD's blob —
verified with `git show $BASE:… | sha256sum` and `git show HEAD:… | sha256sum`).

Scratch drivers (never in the lane): `r40-probe-fixture.py` (house-style fixture mirroring the
committed r39 fixture's shape, plus the three r40 branches), `harness.py`, `harness2.py`, `harness3.py`,
`probe2.py`, `admiss.py`, `a5check.py`, `landmine.py`, `refusalcheck.py`, `summaries.py`.
`harness.py`/`harness2.py`/`admiss.py` import the **committed** `census/round-39/c3-counter.py` and call
its own `score()` and `child_env()`, so the scoring rule under test is byte-identical to the instrument.

### 2.1 F1 — decisive isolation of the crash-gate misattribution

`harness3.py` builds **two** fixtures whose logic is identical except for whether the fixture redacts
the tool's traceback before printing it, then scores both against the pristine tool and against the
strict-decode mutant. The two variants differ **only** in the redaction:

```
$ python3 -B harness3.py --work /fast/scratch/hyaku/souji-r40/R40connector21
VARIANT house-style        pristine(killed=False rc=0 fails=0 crash=False cases=1) | strict-mutant(killed=False rc=1 fails=1 crash=True)  | fixture_rc=1 summary=SUMMARY cases=1 pass=0 fail=1 traceback_in_fixture_stdout=True
VARIANT traceback-scrubbed pristine(killed=False rc=0 fails=0 crash=False cases=1) | strict-mutant(killed=True  rc=1 fails=1 crash=False) | fixture_rc=1 summary=SUMMARY cases=1 pass=0 fail=1 traceback_in_fixture_stdout=False
```

Same tool, same mutant, same fixture case, same expected verdict. The **only** difference is whether
the fixture reprints the tool's traceback — and that single difference flips the kill from `no` to
`yes`. The pristine tool passes both variants identically (`rc=0 fails=0 crash=False`), so the flip is
attributable to the mutant, not to a fixture defect.

The tool-side traceback reproduced verbatim (`r40-probe-fixture.py` vs `MT3a-decode-strict.py`):

```
case-invalid-utf8-tolerated=FAIL rc=1 want=1 missing=['ABSENT'] out='Traceback (most recent call last):   File ".../MT3a-decode-strict.py", line 451, in <module>     sys.exit(main(sys.ar'
case-invalid-utf8-line=FAIL rc=1 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] out='Traceback (most recent call last):   File ".../MT3a-decode-strict.py", line 451, in <module>     sys.exit(main(sys.ar'
SUMMARY cases=6 pass=4 fail=2
rc=1
```

The fixture detected the difference in **2** cases and exited **1** with its own summary — exactly the
A5 kill conditions — and the counter still said `killed=no`.

### 2.2 F1 — A5's intent is preserved by the fix (the veto is not the whole story)

`a5check.py` distinguishes the two crash sources with two minimal fixtures:

```
(1) fixture raises in ITS OWN frames : killed=False  rc=1 fails=1 crash=True   [A5 intent => killed must be False]
(2) fixture reprints the TOOL traceback: killed=False  rc=1 fails=1 crash=True   [F1 => wrongly NOT killed]
```

Case (1) is A5's scenario and is correctly rejected. Case (2) is the misattribution. **The two cases
are textually indistinguishable to the current gate** — both put the string
`Traceback (most recent call last)` into the fixture's stdout — even though in (1) the fixture is
broken and in (2) the fixture is correct and the *tool* is broken. A gate that distinguishes "the
fixture process raised" (e.g. `proc.returncode not in (0, 1)` or a traceback whose frames name the
fixture file) from "the fixture printed a traceback it copied from the tool" separates them and keeps
A5 intact.

### 2.3 F2 — mutant admissibility matrix against the r39 counter's own `score()`

`admiss.py` scores six candidate r40 mutants against a scratch r40-style fixture, and against **both**
committed base fixtures (`r39-drift-record-rules.py` and `r38-drift-record.py`):

```
mutant                         r40-fixture            r39-base / r38-base
MT-duplicate-TOTAL-refused     killed=True  rc=1 fails=2 crash=False | r39:killed=False r38:killed=False
MT-total-first-wins            killed=True  rc=1 fails=2 crash=False | r39:killed=False r38:killed=False
MT-total-must-be-last          killed=True  rc=1 fails=5 crash=False | r39:killed=True  r38:killed=True
MT-skip-unrecorded-inverted    killed=True  rc=1 fails=2 crash=False | r39:killed=False r38:killed=False
MT-decode-ignore               killed=True  rc=1 fails=2 crash=False | r39:killed=False r38:killed=False
MT-decode-strict               killed=False rc=1 fails=2 crash=True  | r39:killed=False r38:killed=False
```

Reading:
- **`MT-total-must-be-last` is inadmissible.** It is killed by the r39 base fixture, violating C3's
  "all mutants survive the r39 base fixture" control clause. Per-case detail:
  ```
  # r39 base fixture vs MT-total-must-be-last
  case-good=FAIL rc=2 want=0 missing=['SUMMARY', 'record_repos=2'] out='REFUSAL RECORD-MALFORMED: line 3 TOTAL before REPO rows '
  case-crlf=FAIL rc=2 out='REFUSAL RECORD-MALFORMED: line 3 TOTAL before REPO rows '
  SUMMARY cases=7 pass=5 fail=2
  # r38 base fixture vs MT-total-must-be-last
  case-total-ok=FAIL rc=2 ... case-total-repos-mismatch=FAIL ... case-total-regs-mismatch=FAIL ...
  case-total-prunable-mismatch=FAIL ... case-comments-and-blanks=FAIL rc=2 want=0 ...
  SUMMARY cases=10 pass=5 fail=5
  ```
  The r39 base fixture's own `total-before-rows` case (`r39-drift-record-rules.py:88-89`) already
  accepts a TOTAL row placed *before* the REPO rows, so any mutant that forbids that ordering is
  already covered by the baseline and cannot be an r40 *new* mutant.
- **`MT-decode-strict` is inadmissible under the inherited gate** — it is the F1 victim.
- **`MT-decode-ignore` is admissible and works**: `killed=True`, and both base fixtures leave it alive.
  This is the practical workaround: the invalid-UTF-8 branch *can* be scored with a decode-policy
  mutant that does not crash.
- The `MT-duplicate-TOTAL-refused` and `MT-total-first-wins` shapes are both admissible for the
  multiple-TOTAL branch.

### 2.4 Pristine behaviour on all three branches (measured, for the r40 fixture author)

`probe2.py` / `refusalcheck.py` / `summaries.py`, against the pristine committed tool:

```
### P1 — invalid UTF-8: how many observables does the pristine tool have?
  invalid byte in REPO NAME field                      rc=1  DRIFT	ABSENT	al?pha	recorded regs=1 | DRIFT	UNRECORDED	alpha	live regs=1 prunable=0 | SUMMARY ...
  invalid byte alone on a structural line              rc=2  REFUSAL RECORD-MALFORMED: line 2 does not match the census schema
  invalid byte inside a COMMENT line                   rc=0  SUMMARY ... record_repos=2 ...
  invalid byte inside the TOTAL numbers                rc=2  REFUSAL RECORD-MALFORMED: line 3 does not match the census schema
  invalid byte as a trailing partial UTF-8 seq at EOF  rc=2  REFUSAL RECORD-MALFORMED: line 4 does not match the census schema

### P2 — duplicate TOTAL rows: is the EARLIER row validated?
  bogus TOTAL first, good TOTAL second                 rc=0  SUMMARY ... record_repos=2 ...
  good TOTAL first, bogus TOTAL second                 rc=2  REFUSAL RECORD-MALFORMED: TOTAL repos=7 but 2 REPO rows
  two IDENTICAL good TOTAL rows                        rc=0  SUMMARY ... record_repos=2 ...
  three TOTAL rows, middle good                        rc=2  REFUSAL RECORD-MALFORMED: TOTAL repos=7 but 2 REPO rows

### P3 — --skip-unrecorded: what exactly does it suppress?
  no flag                rc=1  DRIFT	UNREACHABLE	delta	UNREACHABLE:list-rc=128 | DRIFT	UNRECORDED	gamma	live regs=1 prunable=0 | SUMMARY ... drift_rows=2 unreachable=1
  --skip-unrecorded      rc=0  SUMMARY ... drift_rows=0 unreachable=0
```

Three consequences the r40 fixture author needs, none of them stated in the frozen predicate:

1. **The pristine tool does not refuse invalid UTF-8 — it TOLERATES it.** `decode("utf-8","replace")`
   substitutes U+FFFD. A fixture asserting "invalid UTF-8 → `RECORD-MALFORMED`" would **fail on the
   pristine candidate** and break C3's "pristine candidate passes" clause. The correct pristine
   expectation for an invalid byte *in a REPO name field* is `rc=1` with a `DRIFT ABSENT` row (the
   corrupted name matches no repository) **plus** a `DRIFT UNRECORDED` row for the real `alpha`
   (the corrupted name is no longer the recorded name, so `alpha` becomes unrecorded) — two drift rows,
   not one. Placement matters: the same invalid byte gives `rc=0` in a comment line, `rc=2` on a
   structural line, `rc=2` inside the TOTAL numbers. The tool's docstring
   (`tools/souji-worktree-drift.py:41-77`) names **no** refusal class for a decoding error, so there is
   no contract to assert against other than observed behaviour.

2. **`--skip-unrecorded` suppresses more than the `UNRECORDED` row.** It also suppresses the
   `UNREACHABLE` row for an unrecorded-but-broken repository (`delta`) *and* it moves the
   `unreachable=` summary counter from 1 to 0 (`drift_rows=2` → `drift_rows=0`). A fixture case that
   only asserts "no `UNRECORDED` row" leaves two further observables unpinned.

3. **The duplicate-TOTAL branch is "last TOTAL wins", and the earlier row is never validated.**
   `total = {...}` is overwritten on each TOTAL match (`tools/souji-worktree-drift.py:162-165`) and
   only the final value is checked against the REPO rows (`:169-178`). A *bogus* first TOTAL followed
   by a good second TOTAL is **accepted** (`rc=0`). This is the same ordering gap `R40revenger36`
   named; item 21 measured it and adds the admission consequence above.

### 2.5 Fixture-design landmine: the shared fleet

`landmine.py` — the r39 fixture builds **one** shared fleet and every case reuses it. The
`--skip-unrecorded` case needs a repository that is discoverable but *not* recorded, which means adding
a repo to the fleet — and that changes the exit code of every *other* case:

```
shared fleet, NO unrecorded repo : rc=0  ['SUMMARY ... drift_rows=0 unreachable=0']
shared fleet, WITH unrecorded repo: rc=1  ['DRIFT	UNRECORDED	gamma	live regs=1 prunable=0', 'SUMMARY ... drift_rows=1 unreachable=0']
```

The r39 `good` case asserts `rc=0` on that shared fleet
(`tests/fixtures/r39-drift-record-rules.py:87`). An r40 fixture that adds an unrecorded repo to the
shared fleet silently breaks every other case, including pristine. The r40 fixture must use a
**separate** fleet for the `--skip-unrecorded` case — my scratch fixture does
(`fleet(scratch, "unrecorded", extra="gamma")`), which is why its pristine run is clean.

### 2.6 Counter constraints the r40 author inherits

- `census/round-39/c3-counter.py:161` — the pristine gate requires `cases >= 6`; a shorter r40
  fixture reports `pristine=FAIL`.
- `census/round-39/c3-counter.py:161-166` — a mutant anchor that does not occur **exactly once** is
  a battery defect, not a kill (`MUTANT %s ANCHOR-COUNT %d`). Verified counts on the committed tool:
  `decode("utf-8", "replace")` → **4** (must use the full line at `:147`, count **1**);
  `    if not args.skip_unrecorded:` → 1; the `total = {...}` assignment → 1.
- `census/round-39/c3-counter.py:125-128` — the counter reads `--fixture`/`--base-fixture` from the
  filesystem (`open(args.fixture)`), not from the revision; the tool itself is read from the revision
  via `git show`. An r40 counter that keeps this shape measures the r40 fixture against the r40 tool
  bytes, which is what the C3 measurement clause ("r40 counter receipt, with base and after revisions
  explicitly named") requires for C1/C2 — C3's clause says "the pristine candidate passes", so the
  fixture and the tool must come from the same candidate revision.
- The preregistration's closing sentence — "All counters must accept explicit scratch paths and avoid
  hardcoded `/tmp`" — is satisfied by the r39 counter (`--scratch`, `tempfile.mkdtemp(dir=…)`) and my
  probes honour it (`TMPDIR` set, `--work` passed).

## 3. Bounded repair plan (no change to the frozen claim)

The coverage substance is sound and coverable; the instrument needs two narrow repairs. Neither
requires touching `census/round-40/preregistration.txt`.

1. **Separate the two crash sources in the kill gate.** Replace the textual veto in the r40 counter's
   `score()` with a check on the *fixture's own* execution. Minimal options, in order of preference:
   - treat "the fixture's subprocess exited with a traceback in its own frames" as the A5 veto
     (e.g. detect the traceback's frame file, or `proc.returncode` outside `{0, 1}`); **and**
   - recognise a *tool-side* traceback as a **kill**, not a veto — a tool that dies with a traceback
     is precisely a behavioural difference the fixture observed. Measured: this alone turns
     `MT-decode-strict` from `killed=no` into `killed=yes` (§2.1).
   - Alternative that requires no counter change: the r40 fixture redacts the tool's traceback from
     its own failure detail before printing (the `traceback-scrubbed` variant). Measured:
     `killed=True`. This is the smallest possible patch and it preserves A5 exactly.
   A5's intent is preserved either way: §2.2 shows the fixture-self-crash case stays `killed=False`.
2. **Declare only admissible mutants.** From §2.3: for the multiple-TOTAL branch use the
   duplicate-TOTAL-refused or first-TOTAL-wins shape; **not** the total-must-be-last shape (already
   killed by both base fixtures). For the invalid-UTF-8 branch use a decode-policy mutant that does
   not crash (e.g. `replace` → `ignore`, measured `killed=True`, both bases alive) — or the strict
   mutant *after* repair 1. For `--skip-unrecorded` use an inverted-flag or dropped-UNRECORDED-row
   mutant (measured `killed=True`, both bases alive).
3. **Use a separate fleet for the `--skip-unrecorded` case** (§2.5) and assert the pristine
   expectations measured in §2.4 — in particular that the pristine tool **tolerates** invalid UTF-8
   (`rc=1`, `DRIFT ABSENT` **and** `DRIFT UNRECORDED`) rather than refusing it, and that
   `--skip-unrecorded` also suppresses the unrecorded `UNREACHABLE` row and zeroes `unreachable=`.
4. **Pin the counter's own constraints** in the r40 fixture/counter header: `cases >= 6`,
   anchor-count == 1, the `SUMMARY cases=… pass=… fail=…` line, and the base-fixture survival clause.

## 4. Risks and limits

- **No r40 artifact was run.** `census/round-40/` contains only `preregistration.txt`. Pristine-pass,
  mutant-killed, and base-survival for the *actual* r40 fixture are **unmeasured, not pass**. F1 and F2
  are falsifiers of the *measurability* and *mutant admissibility* of the frozen predicate under the
  inherited instrument, demonstrated on the committed r39 tool bytes and the committed r39 counter.
- **F1 is a false negative in the instrument, not a false positive in the tool.** The pristine tool's
  behaviour was measured directly (§2.4); it is unchanged by any of this.
- **The misattribution is latent in r39, not hypothetical.** All four r39 receipts read
  `crash=False`; the defect becomes reachable for the first time on a branch whose natural mutant
  crashes.
- **F2 is a battery defect, not a coverage gap.** The multiple-TOTAL branch *is* coverable and the
  admissible mutant shapes are measured to work.
- **Scope.** This attack is confined to the C3 coverage axis and the C3 counter's scoring contract.
  C1 calibration and C2 operability are not assessed. No lane file was modified; the sole write is
  this report. No git/jj/index mutation was performed. `pacman` was not invoked and no package was
  installed or upgraded.
- **Scratch.** `/fast/scratch/hyaku/souji-r40/R40connector21` is removed before yield.

## 5. Commands actually run (summary list)

```
read /home/vgpnk/.omp/agent/RULES.md
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
read .../census/round-39/c3-counter.py:39-200
read .../tests/fixtures/r39-drift-record-rules.py        (full)
read .../tests/fixtures/r38-drift-record.py:50-143
read .../tools/souji-worktree-drift.py:1-451
read .../corpus/lessons/round-39-verifier-spotcheck.md:1-200
read .../census/round-39/waves/w1/W1MutDriftRules.md:1-60
read .../.ufo/waves/round-40/w1/{R40executor39,R40executor51,R40executor63,R40revenger36,R40revenger48,R40revenger60,R40critic31,R40scout41}.md
git -C <lane> log --oneline -15 ; rev-parse --show-toplevel ; rev-parse HEAD ; status --short
git -C <lane> show $BASE:tools/souji-worktree-drift.py | sha256sum
git -C <lane> show HEAD:tools/souji-worktree-drift.py | sha256sum
git -C <lane> show $BASE:tests/fixtures/r39-drift-record-rules.py | sha256sum
grep -n 'skip-unrecorded|TOTAL|utf-8|decode|surrogate|errors=' .../tools/souji-worktree-drift.py
grep -c -F <anchor> .../tools/souji-worktree-drift.py        (anchor-count discipline)
grep -n 'A5' .../corpus/lessons/round-38.md
grep -n 'cases >= 6' .../census/round-39/c3-counter.py
grep -h 'MUTANT' .../census/round-39/records/c3-after.txt
ls -la .../census/round-40/
mkdir -p /fast/scratch/hyaku/souji-r40/R40connector21
TMPDIR=$S python3 -B harness.py  --work $S --fixture $S/r40-probe-fixture.py --base-fixture <lane>/tests/fixtures/r39-drift-record-rules.py
TMPDIR=$S python3 -B harness2.py --work $S --fixture $S/r40-probe-fixture.py --base-fixture <lane>/tests/fixtures/r39-drift-record-rules.py
TMPDIR=$S python3 -B harness2.py --work $S --fixture $S/r40-probe-fixture.py --base-fixture <lane>/tests/fixtures/r38-drift-record.py
TMPDIR=$S python3 -B harness3.py --work $S
TMPDIR=$S python3 -B probe2.py
TMPDIR=$S python3 -B admiss.py
TMPDIR=$S python3 -B a5check.py
TMPDIR=$S python3 -B landmine.py
TMPDIR=$S python3 -B refusalcheck.py
TMPDIR=$S python3 -B summaries.py
python3 -B <lane>/tests/fixtures/r39-drift-record-rules.py --tool $S/MT3a-decode-strict.py --work $S
python3 -B <lane>/tests/fixtures/r39-drift-record-rules.py --tool $S/MT-total-must-be-last.py --work $S
python3 -B <lane>/tests/fixtures/r38-drift-record.py         --tool $S/MT-total-must-be-last.py --work $S
```

Git fixtures: every scratch fixture repo was created with `git init -q -b main <path>` and every
subsequent git command used `-C <exact fixture path>`; each repo's
`git -C <path> rev-parse --show-toplevel` was asserted equal to its realpath before the commit
(`make_repo` in every scratch driver, and `landmine.py`/`summaries.py`).
