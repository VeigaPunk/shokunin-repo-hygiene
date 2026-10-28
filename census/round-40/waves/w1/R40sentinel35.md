# R40sentinel35 — C2 operability attack: the observed class/trigger pair has a *third* member the frozen list cannot express

- Seat: R40sentinel35 (sentinel; wave round-40 w1; leaf member — no subagent dispatch).
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Base branch revision named by the frozen prereg: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (r40 preregistration line 2). Lane HEAD at read time: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e`.
- Axis attacked: **operability (C2)**.
- Frozen contract read first: `census/round-40/preregistration.txt:7-8` (C2 paragraph), plus `:13` (counter hygiene rules).
- Read-only on lane bytes. **No production file written, no frozen claim edited, no commit/push, no git/jj/index mutation.** The only lane file this seat writes is this report. Tool installs/upgrades: **none**; pacman untouched (operator directive: pacman paused).
- Scratch: `/fast/scratch/hyaku/souji-r40/R40sentinel35/` (removed before yield — see §Scratch).

## Named distinct edge case (item 35), explicitly

Every other r40 w1 C2 seat attacks the **analyzer** (how wrapped continuation lines are joined into a class entry) or the **oracle** (how an observed class is read out of the tool's text). I attack a third component that no sibling names, and which the frozen predicate explicitly assumes away:

> **The class/trigger pair set is not closed over the tool's runtime behavior.** The r40 C2 predicate says the analyzer "verifies **all observed** class/trigger pairs in the frozen list" and kills "if **any observed** class mapping disagrees with runtime behavior". The word *observed* is what I attack: the drift tool has a **reachable runtime path that emits no refusal class at all** — it raises an uncaught `ValueError` and exits **1**, which the tool's own docstring and its SKILL.md registry row both define as *"1 drift rows found"*. So there exists a runtime outcome that (a) is not in any class/trigger pair list, (b) cannot be detected by joining continuation lines, and (c) collides in the exit code with the *success-with-findings* code, so every downstream consumer that keys on the exit code alone misreads a crash as a drift finding.

**Named edge:** `UNCLASSIFIABLE-RUNTIME-OUTCOME / EXIT-1-COLLISION` — a *schema-valid* record file (a `REPO` row whose name contains a NUL byte) drives the tool into an uncaught `ValueError: lstat: embedded null character in path`, exit 1, empty stdout, **no `REFUSAL <CLASS>:` line at all**. The frozen predicate's kill rule ("any observed class mapping disagrees with runtime behavior") has no vocabulary for this outcome, and the exit-code contract in the same docstring is falsified by it.

Distinctness from the sibling C2 edges in this wave (all in `.ufo/waves/round-40/w1/`):

| seat | edge | mine? |
|---|---|---|
| R40executor14 | privileged-runner inversion of the chmod-0 EACCES probe → `RECORD-EMPTY` | no — that is a *class* observation flipping; mine is a **no-class** outcome |
| R40sentinel11 | probe-filename / row-name oracle forgery; unfrozen entry-start rule; unenumerated pair list | no — that is **which class** is observed; mine is **that no class is observed** |
| R40executor38 / 62 / 50 / 26 / scout17 / mutationtester44 | continuation-join grammar (over-join, under-join, class-like continuation token, shadowing, join depth, monotonicity) | no — mine is orthogonal to joining entirely |
| R40connector21 / 45, R40reviewer42, R40revenger12 | the C3 counter's **crash detector** mis-scoring a *mutant*'s traceback as alive | no — those are about the *scoring rule for mutants*; mine is that the **pristine committed tool** has a reachable crash and an exit-code collision |

Grep confirming the edge was unclaimed before this report: `grep -l -iE "embedded null|null character|uncaught" .ufo/waves/round-40/w1/*.md` returned only the four **C3** files above (traceback-as-scoring), none of which concerns the C2 tool contract.

## Evidence pointers (committed r39 artifacts, exact lines)

| What | Where |
|---|---|
| Frozen C2 predicate + kill condition | `census/round-40/preregistration.txt:8` |
| Counter hygiene rule the r40 counter inherits | `census/round-40/preregistration.txt:13` ("All counters must accept explicit scratch paths and avoid hardcoded `/tmp`") |
| Committed r39 C2 counter (the control the r40 leg extends) | `census/round-39/c2-counter.py` at `0242085` |
| `classify()` — first-match substring scan over stdout+stderr | `census/round-39/c2-counter.py:125-131` |
| `docstring_classes()` — the r39 one-line extractor (the named control) | `census/round-39/c2-counter.py:133-144` |
| The L4 observation (probe set + mapping booleans) | `census/round-39/c2-counter.py:219-238` |
| Committed r39 after-receipt (the reading r40 must beat) | `census/round-39/records/c2-after.txt` (`LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False`) |
| r39's own review of L4's weakness (parsing side) | `census/round-39/waves/w1/W1RevC2Doc.md` §3 (`"missing" in "record-missing …"` is a tautology), §4-6 (mutants A/B/C) |
| r39 lesson recording the M1 "rule measured its own wrapper" mistake | `corpus/lessons/round-39.md:76-89` |
| Drift tool: `ROW` schema regex — a NUL byte is a legal row name | `tools/souji-worktree-drift.py:87` |
| Drift tool: `parse_record` accepts the record | `tools/souji-worktree-drift.py:150-168` |
| Drift tool: the uncaught `ValueError` site | `tools/souji-worktree-drift.py:287` (`os.path.realpath(os.path.join(root, row["name"]))`) |
| Drift tool: the `except ValueError` that exists 3 lines later but is unreachable for this input | `tools/souji-worktree-drift.py:290` (guards `os.path.commonpath`, not `os.path.realpath`) |
| Drift tool: `main()` catches only `Refusal` | `tools/souji-worktree-drift.py:444-446` |
| Drift tool: the exit-code contract that is falsified | `tools/souji-worktree-drift.py:41` ("Exit: 0 no drift rows, 1 drift rows found, 2 could-not-evaluate.") |
| SKILL.md registry row restating the same exit contract | `SKILL.md:254` ("0 no drift rows; 1 drift rows (REGS-CHANGED, …); 2 RECORD-MISSING / …") |
| Consumer that keys on rc==1 to mean "drift rows" | `tests/fixtures/r36-worktree-drift.py:152,163,172,201,254` |

## Commands actually run

All tool bytes under test came from `git -C <lane> show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py` into scratch (`drift-pin.py`, sha256 `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`, matching the `tool_sha=…/e48ed08e6728` component of the committed r39 receipts). Nothing was read from the worktree copy of the tool and nothing in the lane was modified.

```text
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py \
  > /fast/scratch/hyaku/souji-r40/R40sentinel35/drift-pin.py
cd /fast/scratch/hyaku/souji-r40/R40sentinel35 && python3 -B probe.py base          # L4 observation, non-root
cd /fast/scratch/hyaku/souji-r40/R40sentinel35 && sudo -n python3 -B probe.py base # L4 observation, root
cd /fast/scratch/hyaku/souji-r40/R40sentinel35 && python3 -B inventory.py         # 24-trigger runtime inventory
cd /fast/scratch/hyaku/souji-r40/R40sentinel35 && python3 -B spoof.py              # scratch-path channel
cd /fast/scratch/hyaku/souji-r40/R40sentinel35 && python3 -B falsifier.py          # decisive FAIL->PASS flip
cd /fast/scratch/hyaku/souji-r40/R40sentinel35 && python3 -B mutants.py            # docstring-side mutants
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c2-counter.py \
  --root . --rev 2f6e981a105fc759205767d2a749a5f7d4fd0b8a \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch <scratch>         # control replay
```

### 1. The runtime inventory — 24 triggers, 10 classes, one outcome that is *not* a class

`inventory.py` drove the committed tool through 24 distinct triggers. Full result (non-root):

```text
TRIGGER                                OBSERVED CLASS              RC  MESSAGE
ENOENT (absent record path)            RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: … is not a regular file
EACCES (mode-0 record file)            RECORD-MISSING               2  REFUSAL RECORD-MISSING: [Errno 13] Permission denied: …
ELOOP (self-referential symlink)       RECORD-MISSING               2  REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: …
non-regular (directory as record)      RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: … is not a regular file
non-regular (FIFO as record)           RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: … is not a regular file
schema violation                       RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
duplicate REPO name                    RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: line 2 duplicates x
TOTAL count disagrees                  RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: TOTAL repos=9 but 1 REPO rows
TOTAL row present twice                NO-CLASS                     1  DRIFT ABSENT x recorded regs=1
no REPO rows (comment only)            RECORD-EMPTY                 2  REFUSAL RECORD-EMPTY: no REPO rows in …
row resolves outside --root            RECORD-OUTSIDE-ROOT          2  REFUSAL RECORD-OUTSIDE-ROOT: ../escape resolves outside …
invalid UTF-8 bytes in record          RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: line 2 does not match the census schema
CRLF line endings                      NO-CLASS                     1  DRIFT ABSENT x recorded regs=1
trailing whitespace on row             RECORD-MALFORMED             2  REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
--json target is the record file       JSON-IS-RECORD               2  REFUSAL JSON-IS-RECORD: … is the record file
--json target under --root             JSON-INSIDE-MEASURED-TREE    2  REFUSAL JSON-INSIDE-MEASURED-TREE: … is under …
--json target is a FIFO                JSON-NOT-REGULAR             2  REFUSAL JSON-NOT-REGULAR: … is not a regular file
--json target is hardlinked            JSON-HARDLINKED              2  REFUSAL JSON-HARDLINKED: … has 2 links
USAGE: --root not a directory          USAGE                        2  REFUSAL USAGE: --root … is not a directory
USAGE: --timeout < 1                   USAGE                        2  REFUSAL USAGE: --timeout must be >= 1
missing --record / unknown flag / non-int --timeout   NO-CLASS       2  usage: drift-base.py [-h] --root ROOT --record RECORD …
```

Two consequences, both relevant to C2:

1. **The docstring's class table is complete** — an AST walk of every `raise Refusal(...)` site at the pinned bytes yields exactly the ten classes the docstring enumerates (`RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT, JSON-INSIDE-MEASURED-TREE, JSON-IS-RECORD, JSON-NOT-REGULAR, JSON-HARDLINKED, JSON-UNWRITABLE, USAGE`), with **zero** classes raised-but-unnamed and **zero** named-but-never-raised. So the *class vocabulary* is not the hole; the **pair list** and the **outcome space** are.
2. **`argparse` usage errors exit 2 with no `REFUSAL <CLASS>:` line** — a third no-class outcome alongside the crash below.

### 2. The decisive falsifier — `UNCLASSIFIABLE-RUNTIME-OUTCOME / EXIT-1-COLLISION`

A record file whose `REPO` row name contains a NUL byte is **schema-valid** (`ROW` at `tools/souji-worktree-drift.py:87` is `(?P<name>[^\t]+)`, which admits NUL), is accepted by `parse_record` (`tools/souji-worktree-drift.py:150-168`), and then crashes at `tools/souji-worktree-drift.py:287`:

```text
$ python3 -B drift-pin.py --root <wd> --record <wd>/nul.tsv --timeout 20
rc = 1
stdout = ''
stderr =
Traceback (most recent call last):
  File ".../drift-pin.py", line 451, in <module>
    sys.exit(main(sys.argv[1:]))
  File ".../drift-pin.py", line 444, in main
    return run(args)
  File ".../drift-pin.py", line 287, in run
    resolved = os.path.realpath(os.path.join(root, row["name"]))
  File "<frozen posixpath>", line 457, in realpath
ValueError: lstat: embedded null character in path
```

Measured facts about that run:

- `rc = 1`.
- `stdout` is **empty** — no `DRIFT` row, no `SUMMARY` line.
- **No refusal class is emitted at all**: the stderr contains none of `RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT, JSON-*, USAGE` (measured: `refusal_class_emitted=False`).
- `classify()` (`census/round-39/c2-counter.py:125-131`) returns **`NO-CLASS`** — correctly, since there is no class to find.

**The exit-code collision, measured side by side:**

```text
A) NUL row name       rc=1  stdout_empty=True   stderr_has_traceback=True
B) genuine drift run  rc=1  stdout_empty=False  stderr_has_traceback=False
   B stdout: 'DRIFT\tABSENT\tnotarepo\trecorded regs=1\nSUMMARY record=… live_prunable=1 …'
EXIT-CODE COLLISION: A rc=1 (crash, no SUMMARY, no drift rows) == B rc=1 (drift rows found)
```

`tools/souji-worktree-drift.py:41` documents `Exit: 0 no drift rows, 1 drift rows found, 2 could-not-evaluate.` and `SKILL.md:254` restates it (`0 no drift rows; 1 drift rows (REGS-CHANGED, …); 2 RECORD-MISSING / …`). The crash emits **exit 1 with no drift rows**, so it is consumed by every exit-code-keyed consumer as *the success-with-findings code*. `tests/fixtures/r36-worktree-drift.py` is exactly such a consumer: `:152,163,172,201,254` all assert `rc == 1` to mean "a drift row was found". A crash and a finding are indistinguishable there.

**Why this is a C2 kill, not a C3 gap.** The r40 C2 kill condition is *"if any observed class mapping disagrees with runtime behavior"*. The r39/r40 observation step turns a runtime run into a *pair* by reading a class token out of the run's text. For this runtime outcome there **is no class token**: the run has no refusal class, so it cannot appear in any class/trigger pair list, and no pair-list check — however the frozen list is enumerated, however the continuation lines are joined — can witness it. The pair set the predicate verifies is **not closed over the tool's runtime behavior**: it covers the ten `Refusal` classes and the ten `argparse` usage paths, and misses the outcomes where the tool produces neither.

That is a *falsifiable* statement, not a philosophical one, and the falsifier is one file write away from any r40 counter:

```text
# a counter that adds the trigger to its probe set must decide what to do with:
#   observed class = NO-CLASS, rc = 1, stdout empty, traceback on stderr
# today the r39 leg treats that as `missing in new_classes` == False -> leg FAILs,
# and the FAIL is indistinguishable from "the docstring disagrees with runtime".
```

### 3. A second, independent channel for the same no-class outcome (the tool's own path)

`classify()` scans stdout+stderr, and a traceback echoes the **file paths of the frames it prints**. The counter extracts the tool under test to a path **it chooses** — `census/round-39/c2-counter.py:97-104` writes it to `os.path.join(scratch, name)`, and `scratch` is the **caller-supplied** `--scratch` root that the r40 prereg *requires* counters to accept (`census/round-40/preregistration.txt:13`). Measured:

```text
tool path dir token plain            rc=1 classify()=NO-CLASS     (tool raised NO Refusal)
tool path dir token RECORD-MISSING   rc=1 classify()=RECORD-MISSING (tool raised NO Refusal)
```

So the same crash that emits no class is **read back as a class** purely because the operator chose a `--scratch` directory whose name contains a class token. The instrument then reports a *confidently wrong* observed class for a run that produced none — a strictly worse failure than the plain `NO-CLASS`, because it is believed.

### 4. The scratch-path channel against the *real* counter — an executed FAIL→PASS flip

This is the concrete falsifier of the r40 leg's own instrument, run against the committed r39 counter (which is the named control and the code the r40 leg extends), on a git fixture whose every command used `-C <fixture>` with the top-level asserted before the commit.

Fixture: `git archive 0242085` → `git init` → commit `c0` (base bytes) → commit `c1` (mutant: the `RECORD-MALFORMED` docstring entry no longer names its own trigger — `a missing (ENOENT) or non-regular record path` → `an ENOENT or non-regular record path`). Toplevel asserted: `/fast/scratch/hyaku/souji-r40/R40sentinel35/fix-e2e`.

```text
$ python3 -B fix-e2e/census/round-39/c2-counter.py --root .../fix-e2e \
      --rev e36a2ce523af10470c806c756988a0cad091034e \
      --base-rev 89492c50c6b0430789232967bb3ca519ae800f1f \
      --scratch .../e2e-clean
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=True

$ python3 -B fix-e2e/census/round-39/c2-counter.py --root .../fix-e2e \
      --rev e36a2ce523af10470c806c756988a0cad091034e \
      --base-rev 89492c50c6b0430789232967bb3ca519ae800f1f \
      --scratch .../e2e-RECORD-MISSING
LEG L4 FAIL missing=RECORD-MISSING locked=RECORD-MISSING new_maps=True old_maps=True
```

Same tool bytes, same revisions, same counter — **only the `--scratch` directory name differs** — and `new_maps` flips `False → True`. The mutant's `RECORD-MALFORMED` entry still does not name its own trigger, yet under the spoofed scratch the leg's mapping check is *satisfied*. Mechanism: the ENOENT observation is re-labelled `RECORD-MISSING` (the tool copies the record path into the refusal message), and the leg's "missing" conjunct `"missing" in classes[observed].lower()` is then evaluated against the `RECORD-MISSING` entry, whose **class token itself contains the substring "missing"** — the tautology r39's own reviewer documented (`census/round-39/waves/w1/W1RevC2Doc.md` §3).

I reproduce the same flip at the analyzer level in `falsifier.py`, holding the tool bytes fixed and varying only the scratch root:

```text
== M35-C (RECORD-MALFORMED entry drops 'missing')
   r39 one-line  RECORD-MALFORMED = 'RECORD-MALFORMED       an ENOENT or non-regular record path, a line'
   r40 joined    RECORD-MALFORMED = 'RECORD-MALFORMED       an ENOENT or non-regular record path, a line that does not match the schema, a duplicated name, or a TOTAL row that disagrees'
   clean scratch                observed missing=RECORD-MALFORMED locked=RECORD-MISSING   | r39-style leg=False r40-style leg=False
   scratch token RECORD-MISSING observed missing=RECORD-MISSING   locked=RECORD-MISSING   | r39-style leg=True  r40-style leg=True
```

**The joined (r40-shaped) analyzer inherits the flip.** Joining continuation lines widens the entry text and therefore widens the set of substrings that can satisfy a token check; it does not close the hole. This is the same conclusion R40sentinel11 reached by a different route (probe-name forgery vs. scratch-root forgery), and I cite it rather than claim it: my independent contribution here is that the r40 *joined* analyzer is affected too, and that the channel is the `--scratch` root the r40 prereg explicitly mandates be caller-supplied.

### 5. Privilege dependence (independently reproduced; executor14 owns this edge)

Same committed bytes, same revisions, same scratch root, two privilege levels:

```text
non-root (uid 1000): observed missing=RECORD-MALFORMED locked=RECORD-MISSING   L4-style ok first-line=True  joined=True
root    (uid 0)    : observed missing=RECORD-MALFORMED locked=RECORD-EMPTY    L4-style ok first-line=False joined=False
```

Root bypasses the mode-0 read bit, so the chmod-0 probe opens successfully and the tool raises `RECORD-EMPTY` instead of `RECORD-MISSING`. Confirmed end-to-end through the real counter on a root-owned fixture (`LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-EMPTY new_maps=False old_maps=False`) versus the same fixture as the owning user (`LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=True`). No r39 counter asserts a uid/privilege precondition (`grep -n "getuid\|geteuid" census/round-39/c*-counter.py` → no hits) and no r39 receipt records one (`census/round-39/records/c2-after.txt` carries the command, the six `LEG` lines and the `SUMMARY`, and nothing about the environment it ran in). **This edge is R40executor14's; I list it as independently confirmed and adjacent, not as my contribution.**

## Verdict

**C2 operability: the frozen predicate is not falsifiable against a candidate, and the measurement instrument it names admits an executed FAIL→PASS flip. No r40 candidate bytes exist in the lane (`census/round-40/` holds only `preregistration.txt`; `git status --porcelain` shows only `?? census/round-40/`), so I did not and could not execute the candidate counter — every FAIL/PASS above is a measurement of the committed r39 instrument (`census/round-39/c2-counter.py` at `0242085`) applied to committed r39 tool bytes (`e48ed08e…`), with the r40 side modelled as a joined analyzer over the same bytes.**

1. **Concrete falsifier (primary, mine).** The class/trigger pair set the predicate verifies is **not closed over the tool's runtime behavior**. A schema-valid record (a `REPO` row whose name contains a NUL byte) drives the committed tool into an uncaught `ValueError: lstat: embedded null character in path` (`tools/souji-worktree-drift.py:287`), exit **1**, empty stdout, **no refusal class emitted**. Exit 1 is what `tools/souji-worktree-drift.py:41` and `SKILL.md:254` define as *"drift rows found"*, so the crash is consumed by every exit-code-keyed consumer (`tests/fixtures/r36-worktree-drift.py:152,163,172,201,254`) as a successful finding. `classify()` returns `NO-CLASS` for it; no pair list can contain it; no continuation-join rule can witness it. **Kill condition is unreachable for this outcome.**
2. **Concrete falsifier (secondary, mine, executed end-to-end).** The observed-class half of the pair is **caller-controlled**: `classify()` is a first-match substring scan over stdout+stderr, the tool copies the record path into the refusal message, and the record path derives from the caller-supplied `--scratch` root the r40 prereg *requires* be explicit (`census/round-40/preregistration.txt:13`). A `--scratch` directory named `RECORD-MISSING` re-labels the ENOENT observation and flips the real counter's `new_maps` from `False` to `True` on a mutant whose mapping is genuinely wrong — measured on a git fixture with the top-level asserted, `c0`/`c1` named above. The joined (r40-shaped) analyzer inherits the flip.
3. **Third channel for the same no-class outcome (mine).** A crash traceback echoes frame file paths, and the counter extracts the tool under test **into the caller-supplied scratch**. With the scratch named `RECORD-MISSING`, the *same* crash that emits no class is read back as `RECORD-MISSING` — a confidently wrong observed class for a run that produced none.
4. **Confirmed-adjacent (R40executor14's edge).** The observed EACCES pair inverts under a privileged runner (`locked=RECORD-EMPTY`), with no uid precondition in any r39 counter and none recorded in any r39 receipt.
5. **Coverage note that bounds the whole axis.** The committed docstring's class table is *complete* (AST-enumerated: 10 raised classes, 10 documented classes, zero asymmetry). The unfrozen part is the **pair list** (the prereg names "the frozen list" but enumerates no pair — shared with R40sentinel11) and, per this report, the **outcome space**: the ten `Refusal` classes plus argparse's usage exits, but not the crash.

## Smallest remediation (for the r40 counter author; not a change to any frozen claim)

1. **Close the outcome space before enumerating pairs.** Make the observation step classify the *outcome*, not just the class: refuse (rc 2) any probe run whose stderr carries a traceback or whose stdout lacks the `SUMMARY` line, and never let such a run enter the pair set. The committed r39 counter has no such arm; `tests/fixtures/r36-worktree-drift.py` reads `SUMMARY` from stdout and would have caught the crash had the case existed.
2. **Derive the observed class positionally, not by priority scan.** Read the first `REFUSAL <CLASS>:` token in stderr (the tool's own format, `tools/souji-worktree-drift.py:445`), instead of the first *substring* match over stdout+stderr. That single change removes both the scratch-root channel and the crash-traceback channel, because neither can produce the `REFUSAL ` prefix.
3. **Keep the tool bytes out of the caller-controlled path.** Extract the audited tool into a subdirectory whose name is counter-chosen and token-free, or pass its bytes on stdin, so the frame paths echoed by a traceback cannot steer the oracle.
4. **Gate the EACCES probe on capability, not on uid.** A `chmod 0` + `open` capability probe refuses under `CAP_DAC_OVERRIDE` as well as under uid 0; print the observed pair and the runner's euid in the receipt so a reader can see which environment produced the reading.
5. **Separately, the tool-side defect deserves a routed defect.** The crash is a real, undisclosed defect in the committed tool: `tools/souji-worktree-drift.py:287` calls `os.path.realpath` on a schema-valid row name without the embedded-NUL guard its own `os.path.commonpath` call has three lines later (`:290`), and the resulting exit 1 collides with the documented "drift rows found" code. The minimal repair is to refuse the NUL row name with a named class (e.g. `RECORD-MALFORMED: row N has an invalid name`) so the outcome enters the class vocabulary the C2 leg can observe. I am not making that edit — it is outside this seat's read-only scope.

## Limits of this report

- Read-only on lane bytes; the only lane file written is this report. No commit, push, branch, index, or jj mutation. No production file, frozen claim, or template touched.
- The r40 candidate counter and fixture do not exist in the lane at read time; **no r40 behavior is claimed as measured**. Unrun is not pass.
- Findings 1–3 are properties of the *committed r39 instrument applied to committed r39 tool bytes*, with the r40 leg modelled as a joined analyzer over the same bytes (the joined analyzer is reimplemented in `falsifier.py` from the predicate text at `census/round-40/preregistration.txt:8`, not copied from an r40 candidate).
- Finding 5 and the scratch-root channel of finding 2 overlap R40executor14's and R40sentinel11's edges respectively; I cite those seats' reports rather than claiming the edges.
- The instrument-side deflate of finding 2 does not depend on the *specific* spoof token: any scratch name containing a class token from `classify`'s list re-labels the observation, and `RECORD-MISSING` was chosen because it is first in that priority list (`census/round-39/c2-counter.py:127`).

## Scratch

`/fast/scratch/hyaku/souji-r40/R40sentinel35/` — created for this seat, held only scratch fixtures and probe scripts (`probe.py`, `inventory.py`, `spoof.py`, `falsifier.py`, `mutants.py`, extracted tool bytes, git fixtures `fix-user`, `fix-root`, `fix-root3`, `fix-e2e`, `root-arm.txt`, revs files). **Removed before yield.** Nothing outside that directory was created, except one transient directory `/fast/scratch/hyaku/souji-rou40-scratch/` that was created by a mistyped write path and deleted immediately in the same session (it never contained evidence and is not cited above).

Report path relative to the lane root: `.ufo/waves/round-40/w1/R40sentinel35.md`
