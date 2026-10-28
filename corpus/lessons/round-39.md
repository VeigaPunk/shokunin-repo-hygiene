# Round 39 — routed-defect closure, revision resolution, record-rule mutation coverage

author: souji L1 (SoujiR39), hyaku run 11, attempt 1. Lane base
`ed30b7f5b77939c9073348d810730bc4f355708d`; frozen contract `census/round-39/preregistration.txt`
(freeze commit `b769bfb84a264d8b284c09bc211d99f39a3e9126`; amendment A1 appended at `bbd9b974`).
This round is the first after the r38 closure, whose non-author spot-check routed 16 defects
(`corpus/lessons/round-38-verifier-spotcheck.md` `## Routed defects`); they were read before the
claims were declared.

## Claims

- **C1 calibration (score 7, the lowest non-retired axis).** The 16 routed defects become one
  counter: 16 anchored single-line predicates over committed bytes plus the citation-register arm
  the r38 limit named (its ten rows all carried `commit == receipt_rev`, so the live register never
  exercised the commit arm's revision discrimination). Predicate:
  `census/round-39/c1-counter.py` prints `items=16 open=0 register_cells>=6 register_mismatches=0
  commit_distinct>=2`. Control at base: `open=16` (`census/round-39/records/c1-before.txt`).
- **C2 operability (score 8).** Two runnable contracts disagreed with their documentation, both
  reproduced on the base bytes: R11 (`tools/souji-citation-reconcile.py` never resolved `--rev`, so a
  blob, tree or absent revision produced findings and exit 1 instead of could-not-evaluate exit 2)
  and R10 (the drift tool's `RECORD-MISSING` sentence described the ENOENT path, which the code
  classifies as `RECORD-MALFORMED`, while EACCES raised `RECORD-MISSING`). Predicate:
  `census/round-39/c2-counter.py` prints `legs=6 pass=6 fail=0 harm=0`. Control at base:
  `pass=2 fail=4` (`census/round-39/records/c2-before.txt`).
- **C3 coverage (score 8).** Four documented record-file behaviours are asserted by no existing
  drift fixture (trailing-whitespace refusal, CRLF acceptance, the `RECORD-OUTSIDE-ROOT` guard and
  indented-comment refusal); four single-defect mutants of those behaviours survive the r38 fixture
  and die against the new one. Predicate: `census/round-39/c3-counter.py` prints
  `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`. Control at base:
  `killed=0 survived=4` (`census/round-39/records/c3-before.txt`).

## Gate

Sources opened this round, on this host (git 2.56.0-1; Python 3.14.8; the docs pages fetched
2026-10-28), each with its located quote:

| id | source (URL) | access | located quote (<=25 words) | verdict |
|---|---|---|---|---|
| S247 | gitrevisions(7) § SPECIFYING REVISIONS `<rev>^{<type>}` — https://git-scm.com/docs/gitrevisions | 2026-10-28 | "dereference the object at <rev> recursively until an object of type <type> is found or the object cannot be dereferenced" (installed man page, entry line 165, quote 166-168) | **admit** — `cat-file -e <rev>^{commit}` is exactly the type-coercion step C2's `--rev` arm adds, and the page states it refuses a non-commit object, which is why a blob id is could-not-evaluate rather than a finding |
| S248 | Python docs `ast.get_docstring` — https://docs.python.org/3/library/ast.html#ast.get_docstring | 2026-10-28 | "(which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring." (section `ast.get_docstring`, docs.python.org/3 Python 3.15.2 page) | **admit** — the L4 analyser reads the module docstring through `ast`, never by slicing source text, and the page is the ground that a missing docstring is `None` rather than an error |
| S249 | Python docs argparse `exit_on_error` — https://docs.python.org/3/library/argparse.html#exit-on-error | 2026-10-28 | "it will print a message to sys.stderr and exit with a status code of 2" (§ `exit_on_error`) | **admit** — a tool whose own usage errors already exit 2 cannot use 2 alone to mean could-not-evaluate; the class name must carry the distinction, which is what C2's `REV-UNRESOLVED` does |
| — | Python docs `ast.get_source_segment` (same page, next entry) | 2026-10-28 | "Get source code segment of the source that generated node" (section `ast.get_source_segment`) | **reject** — it returns the node's own span, which is the source-slicing the r38 M5 finding forbids for a docstring check; flip: the docstring read must go through `get_docstring` |

`used-by` for S247-S249 is this lesson. The registry grew 170 -> 173 rows, all tier A `mined`;
no existing row's `status`, `recheck` or `used-by` cell changed.

## Routed-defect closures

R39-C1-05 — R5 / erratum: the r37 ledger row 8 claimed "not repeated — this round committed no `.ufo/prompts/` path", but the r38 lane commit `068f75dc` did add `.ufo/prompts/souji-round-38.md` (a fleet-repo path) under the lane repo. This line is the erratum that row owed; the lane commits no `.ufo/prompts/` path this round and the prompt stays integrator-owned.

R39-C1-07 — R7 / the r38 `consumers-after*.txt` receipts named their base arm as a `$HYAKU_SCRATCH/hyaku/souji-r38/final/drift-r36.py` file the driver reaps, so the command was not re-runnable from committed bytes; the blob it meant is `tools/souji-worktree-drift.py` at `5f0dd45`, and every r39 receipt cites-a-revision (`--rev`/`--base-rev`) instead of a scratch path.

R39-C1-15 — R15 / the r38 report's Landed-changes table named 12 of the 21 lane commits in `ca4369a..fcdecaa` and ended on the placeholder `<integration>`; the nine it never named are `6949319`, `78ea25a`, `f10a3a8`, `20eea73`, `a512efb`, `9b9e2f8`, `cb5737a`, `be66886` and `c5050ea`, all of which are in the range and in this record; the r38 report is fleet bytes this lane may not edit, so the omission is recorded here and in the r39 report's errata.

| routed | disposition in this round | C1 item |
|---|---|---|
| R1 census numbers | r38 lesson gets the measured block (`census/round-39/records/census-before.txt`) | R39-C1-01 |
| R2 dead-seat count | r38 lesson gets the on-disk numbers; `W2MutBattery` settled after closure | R39-C1-02 |
| R3 filed before WAVE-DONE | this round waits for WAVE-DONE; the wait is receipted | R39-C1-03 |
| R4 untracked wave evidence | captured into `census/round-39/waves/` with a verify receipt | R39-C1-04 |
| R5 prompt committed by the lane | erratum above | R39-C1-05 |
| R6 four counters with no registry row | `SKILL.md` gains the four r38 rows plus five r39 rows | R39-C1-06 |
| R7 scratch path in a receipt | every r39 receipt cites revisions | R39-C1-07 |
| R8 stale prereg pointer | r38 prereg A10 names `a7-counter-fixes2.txt` and the counter-arms fixture | R39-C1-08 |
| R9 in-place prereg rewrite | r38 prereg A11 restates the append-only rule | R39-C1-09 |
| R10 docstring vs class | drift docstring puts each trigger on its class line; C2 L4 | C2 |
| R11 `--rev` never resolved | citation tool resolves both revisions, exit 2 | C2 |
| R12 finality labels | one appended SCORECARD line names the measured revision | R39-C1-10 |
| R13 stale literals | LOG/QUALITY correction lines with the receipt that carries each value | R39-C1-11..13 |
| R14 vacuity receipt description | r38 lesson records the faithful one-row reading | R39-C1-14 |
| R15 landed-changes coverage | the nine unnamed commits above | R39-C1-15 |
| R16 owed round-36 correction | appended correction in `corpus/lessons/round-36.md` | R39-C1-16 |

## Mistakes

### M1 — a docstring rule that measured its own wrapper (class: instrument-vs-contract)

The C2 L4 leg required the docstring line that *starts with* a refusal class to name its trigger.
The drift tool's docstring wraps, so `RECORD-MISSING`'s trigger words sat on the continuation line
and the leg read `new_maps=False` even after the contract was corrected.
**Evidence pointer:** `census/round-39/records/c2-before.txt` `LEG L4 FAIL ... new_maps=False
old_maps=False`; the passing reading is `census/round-39/records/c2-after.txt` `LEG L4 PASS`.
**Captured-by:** the leg's own failure, before any claim value was claimed.
**Fix:** rather than loosen the frozen "the line that starts with the class" rule after data, each
trigger moved onto its class line (`EACCES` on `RECORD-MISSING`, `missing` on `RECORD-MALFORMED`)
and the analyser stayed as frozen (`601195a`). The fix can fail: a docstring that names both
triggers but wraps them still reads `new_maps=False`, which is why the paragraph-joining variant was
reverted.

### M2 — a case that expected the class the tool no longer raises (class: stale-expectation)

`tests/fixtures/r39-citation-rev.py` case `register-rev-gone` expected the substring `not at`, but
the repaired tool resolves `--register-rev` before it reads the register, so the case went red for a
*correct* repair.
**Evidence pointer:** the first run of the fixture read `SUMMARY cases=8 pass=7 fail=1`
(`case-register-rev-gone=FAIL ... missing=['not at']`); the class is now `REV-UNRESOLVED` and the
fixture reads 8/8.
**Captured-by:** the fixture case itself (it compares the class, not only the exit code).
**Fix:** the case expectation and its description line name `REV-UNRESOLVED`; recorded as prereg
amendment A1 at `bbd9b974`, before any claim measurement. The fix can fail: the base arm still fails
this case (its bytes print `not at`), which is what keeps the case discriminating.

## Named limits (disclosed, status-neutral)

- The C1 counter reads its item list and fixtures from the working tree and prints `items_sha=`;
  the audited bytes are `--rev`-bound. A reader must compare `items_sha` to the committed
  `census/round-39/c1-items.tsv` to know which list produced a reading.
- A C1 item binds one anchored line to token presence. An author who writes the tokens on a line
  that cites nothing satisfies the item; the counter cannot police authorship, as r38's
  `W1CritC1` showed for the register arm.
- `commit_distinct>=2` proves the live register exercises the commit arm's revision discrimination;
  it does not prove any row's revision is the right one.
- C3's four mutants are the class boundaries this round chose; comment/blank skipping and the
  optional-TOTAL rule were already asserted by the r38 record fixture (r38 M4's number came from a
  sibling fixture), and the remaining parser branches stay uncovered (`W1MutDriftRules`).
- The `argparse` exit-2 fact (S249) is a disclosure, not a claim: C2's distinction rides on the
  class names, not on the status alone.

## Sources & frontier

Census before -> after and the row changes are in the round report; this lesson carries the Gate
rows and their verdicts. No `ground: F<k>` line moved: the three admitted rows ground the C2 repair
and two disclosures, not new frontier ground.

## Gate correction (appended after wave 1)

R39-GATE-1 — S247's quote stopped at "cannot be dereferenced" and hid the clause that states the refusal; wave-1 seat `W1CritSources` located the full 25-word sentence ("... anymore (in which case, barf)") and showed that a reader holding only the quote saw the search, not the failure. S250 supersedes S247 with that quote and scopes it against S099; S247 stays as filed, and the C2 claim now cites S250 (S247's fact still holds, so the claim does not move).

## Wave-1 repairs (appended 2026-10-28, after the seats that produced them)

- **Docstring `EISDIR` (seat `W1ExecC2Docstring` §5).** The new `RECORD-MISSING` line advertised `EISDIR`, but a directory passed as `--record` never reaches that class: the `O_RDONLY` open succeeds and the `fstat` guard refuses it as `RECORD-MALFORMED`. The word is dropped (`790d16b`); no frozen predicate tests it.
- **Scratch plumbing (seat `W1ExecScratch` F1/T12).** `census/round-39/c3-counter.py` pinned its git children to `/var/tmp` and `tests/fixtures/r39-citation-rev.py` dropped `TMPDIR` from the tool child's environment; both now honour the caller's root (`d4c1755`). This is the lane's own r32 C2 rule applied to this round's instruments.
- **Control receipts (seat `W1RevFreeze`).** The three control receipts did not record their command lines, and the C2/C3 controls had been measured on the pre-amendment fixture bytes. All three are re-measured on the final instruments with their commands recorded (`f8ba3f3`); the before values are unchanged (`open=16`, `pass=2 fail=4`, `killed=0`), and `census/round-39/records/prereg-prefix.txt` proves the freeze bytes are an exact 7356-byte prefix of the prereg with 681 bytes appended by A1.
- **S247 quote (seat `W1CritSources`).** The quote stopped before the clause that states the refusal; S250 supersedes it with the full 25-word sentence and the C2 claim cites S250 (`e9958ee`).
- **C1-04 token shape (seat `W1ExecC1Anchors`).** Item C1-04's `must` set already appears as a quoted shape in `census/round-29/records/preregistration.txt`, so the item binds a token pattern, not a provenance; the round's receipt carries the real `verify-rev` line and the limit is disclosed rather than repaired after data.
- **C1 control reach (seat `W1MutC1`).** The base control reads `open=16` through the anchor/file arms, so a mutant that only weakens the predicate arm is invisible to it; the counter's predicate arm needs a landing-revision control, named for r40.
