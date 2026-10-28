# R40w2revenger02 — attack on the r40 C2 L4 leg (landed 128e412)

Seat: R40w2revenger02 (revenger, leaf). Item: r40 w2 falsify, C2 operability.
Landed instrument commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Base: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (r39 tip). Defect base used by the counter: `ed30b7f5b77939c9073348d810730bc4f355708d`.
Lane HEAD at measurement time: `549d9ec` (four commits after landing: `8a5fbdb`, `6ded124`, `556c24a`, `549d9ec`). All bytes below are the landed `128e412` bytes extracted with `git show <rev>:<path>`, not the worktree.

## Verdict

**FALSIFIED** — the C2 instrument as landed (a) cannot run at its own landed revision, and (b) its L4 predicate is coupled to docstring layout: it FAILS a correct docstring fix and PASSES a contradicted trigger mapping and an unchecked wrong mapping.

Installs: none. No pacman, no git mutation, no edits to the lane. Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2revenger02` was removed (verified absent).

## 1. What the r39 C2 L4 leg proved (not what it claimed)

Code: `census/round-39/c2-counter.py:133-143` (`docstring_classes`: first physical line starting with the class token, ast-only), `:219-238` (L4).

Runtime part (the only behavioural part of the leg):
- `census/round-39/c2-counter.py:221-226`: an absent path is classified `RECORD-MALFORMED`; a `chmod 0` path is classified `RECORD-MISSING` (run as uid 1000, so the chmod is effective).

Docstring part (the leg's check):
- `:230-232`: `"missing" in first_line[RECORD-MALFORMED].lower()` and `"EACCES" in first_line[RECORD-MISSING]`.

**Precise statement supported by r39 L4:** on the audited tool bytes, an absent record path exits as `RECORD-MALFORMED`, an unreadable one as `RECORD-MISSING`, and the first docstring line of those two classes contains the substrings `missing` and `EACCES` respectively.

**Not supported by r39 L4:**
1. Any statement about `RECORD-OUTSIDE-ROOT`, `RECORD-EMPTY`, `JSON-*`, or `USAGE`. The leg reads two classes only.
2. That the docstring is a complete or accurate refusal map. `tools/souji-worktree-drift.py:41-42` claims "Every refusal class the code can raise is named here"; the leg never tests that claim.
3. That a trigger token is the condition that raises the class. Substring co-occurrence on a line is all that is checked; negation is ignored (see M3 below).
4. That wrapped text is correct. The leg reads only the first line, so it cannot see a wrapped trigger at all.
5. ELOOP, ENOENT-vs-non-regular, or any other sub-branch.
6. Anything when the probe runs as root: `chmod 0` stays readable, the probe returns `RECORD-EMPTY`, and the leg fails rather than reporting could-not-evaluate. [INFERENCE from `c2-counter.py` probe logic; not run as root.]

**The r39 lesson's own account (`corpus/lessons/round-39.md:78-82`, M1)** says the fix was to move each trigger onto its class line rather than loosen the reader, and that "the fix can fail" for wrapped text, which is why the joined variant was reverted. That is an honest account of a layout-coupled check; the r39 pass is a docstring-typesetting outcome plus two runtime probes. R10 (`round-39.md:66`, "drift docstring puts each trigger on its class line") was closed by moving text to satisfy the reader.

## 2. What the r40 joined reading changes

Analyser: `census/round-40/docstring-classes.py` (committed bytes identical at 128e412, HEAD, and worktree).
- `:34` `CLASS_LINE` requires a hyphen in the class token.
- `:43-70` `_entries`: a line indented under a class is a continuation; blank or non-indented lines end the entry.
- `:73-80` `class_entries` (joined) and `first_line_entries` (one-line).

Leg: `census/round-40/c2-counter.py:248-274` (committed bytes). Frozen pairs `:74-78`: `(RECORD-MALFORMED, ENOENT)`, `(RECORD-MISSING, EACCES)`, `(RECORD-OUTSIDE-ROOT, --root)`. The `ok` condition at `:271` is `not missing_new and not missing_old and missed_by_first`.

What the joined reading changes in the provable statement:
- It adds one checked class: `RECORD-OUTSIDE-ROOT` with trigger `--root`, which r39 never checked (mutant M2 below shows r39 still passes when `--root` is removed).
- It adds continuation text to the entry. The statement becomes: each frozen trigger substring occurs somewhere in the class's joined text, and the runtime probe raises that class.
- It makes the one-line miss a property of the docstring layout: `missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']` on the landed bytes.
- It does NOT change the drift tool. `git diff --quiet 0242085 128e412 -- tools` is empty, so base and candidate drift tool bytes are identical. `missing_old` therefore equals `missing_new` by construction; the base arm of L4 measures nothing about the tool.

## 3. Commands and real output

### 3a. The landed counter cannot run at its landed revision

```
$ git -C $L show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c2-counter.py > $S/landed/c2-counter.py
$ git -C $L show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/docstring-classes.py > $S/landed/docstring-classes.py
$ python3 -B $S/landed/c2-counter.py --help
Traceback (most recent call last):
  File ".../landed/c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
ModuleNotFoundError: No module named 'docstring_classes'
```
Cause: `census/round-40/c2-counter.py:46` imports `docstring_classes`, but the file is `docstring-classes.py` (hyphen), `census/round-40/docstring-classes.py` (the committed name). The import fails before any argument is parsed. Commit `8a5fbdb` (after landing) replaced this with a by-path load (`HEAD:census/round-40/c2-counter.py` line 298 keeps the same `ok` condition; analyser bytes unchanged at HEAD).

### 3b. Shimmed run (import name fixed only; analyser and tool bytes unchanged)

```
$ cp $S/landed/docstring-classes.py $S/shim/docstring_classes.py
$ python3 -B $S/shim/c2-counter.py --root $L --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/shim
LEG L1 FAIL new rc=2 class=True old rc=2 class=True
LEG L2 FAIL new rc=2 class=True old rc=2 class=True
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 FAIL new=None old(one-line)=None
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=4 fail=3 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```
- L1/L2 fail at landed because the discriminating arm uses `--base-rev` (`census/round-40/c2-counter.py:242`), which is the already-repaired r39 tip; the defect is only live at `ed30b7f`. Fixed by `8a5fbdb` (`--defect-base-rev`).
- L5 fails because `run_fixture` appends `--work` (`c2-counter.py:179`) and `tests/fixtures/r40-docstring-joined.py:100-102` has no `--work` argument, so argparse rejects it and no SUMMARY prints.
- So even with the import fixed, the landed counter cannot reach `legs=7 pass=7`.

### 3c. L4 on the landed analyser and mutant drift tools

Driver: L4 logic reproduced verbatim from `census/round-40/c2-counter.py:249-274` and applied to mutant copies of the landed `tools/souji-worktree-drift.py`; `observed_pairs` is imported from the shim counter so probes are the real ones. Mutant edits are single `str.replace` with `count==1` assertions.

```
M0-landed: L4=PASS pairs=[('RECORD-MALFORMED','ENOENT','RECORD-MALFORMED'), ('RECORD-MISSING','EACCES','RECORD-MISSING'), ('RECORD-OUTSIDE-ROOT','--root','RECORD-OUTSIDE-ROOT')] missing_new=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
M1-rewrap-fix: L4=FAIL pairs=[...same, all raised correctly...] missing_new=[] missed_by_one_line=[]
M2-trigger-removed: L4=FAIL ... missing_new=['RECORD-OUTSIDE-ROOT-missing-trigger(--root)'] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
M3-negated-trigger: L4=PASS ... missing_new=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
M4-unprobed-class-wrong: L4=PASS ... missing_new=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
```
Mutant texts:
- M1 — move `--root` onto the `RECORD-OUTSIDE-ROOT` class line (the same fix r39 M1 applied to the other two classes). Docstring is now correct; every trigger is present; the leg FAILS because `ok` requires `missed_by_first` non-empty (`c2-counter.py:271`). **The leg penalises a correct fix.**
- M2 — `escapes --json` instead of `escapes --root`. Correctly FAILS.
- M3 — `a missing (not ENOENT)` for `RECORD-MALFORMED`. The runtime still raises MALFORMED on an absent path (ENOENT). The joined entry still contains the substring `ENOENT`, so the leg PASSES a docstring that denies its own trigger. **Substring, not token or negation-aware.**
- M4 — `RECORD-EMPTY  EACCES when the record is unreadable` (wrong; the tool raises `RECORD-EMPTY` for a comment-only record at `tools/souji-worktree-drift.py:168`). `RECORD-EMPTY` is not in `FROZEN_PAIRS` (`c2-counter.py:74-78`), so the leg PASSES. **Only 3 of 9 documented classes are checked; the rest of the class map is unchecked.**

The landed analyser's class map (M0) has nine keys; `USAGE` is absent. Commands:

```
$ python3 -B driver.py   # joined map for M0
classes keys (M0): ['RECORD-MISSING', 'RECORD-MALFORMED', 'RECORD-EMPTY', 'RECORD-OUTSIDE-ROOT', 'JSON-INSIDE-MEASURED-TREE', 'JSON-IS-RECORD', 'JSON-NOT-REGULAR', 'JSON-HARDLINKED', 'JSON-UNWRITABLE']
USAGE in map: False
```
Continuation bleed: `tools/souji-worktree-drift.py:61` (`  USAGE                  --root is not a directory, or --timeout < 1`) does not match `CLASS_LINE` (`docstring-classes.py:34`, needs a hyphen), so `_entries` (`:63`) folds it into the preceding entry. The joined `JSON-UNWRITABLE` entry is:
`'the --json write failed (including a symlinked path component, refused by the O_NOFOLLOW walk) USAGE                  --root is not a directory, or --timeout < 1'`
A `--root` that belongs to `USAGE` is therefore attributed to `JSON-UNWRITABLE`, and `USAGE` is unmapped.

### 3d. The same mutants under the r39 one-line leg

r39 L4 logic (`census/round-39/c2-counter.py:230-232`) applied to the same files:

```
M0-landed: r39-L4=PASS
M1-rewrap-fix: r39-L4=PASS
M2-trigger-removed: r39-L4=PASS   (RECORD-OUTSIDE-ROOT is never read by r39)
M3-negated-trigger: r39-L4=PASS
M4-unprobed-class-wrong: r39-L4=PASS
```
r39 L4 passes all five. The r40 joined leg catches M2 but also fails M1 and passes M3 and M4.

## 4. Divergences

| # | Claim | Evidence | Divergence |
|---|---|---|---|
| D1 | Landed `c2-counter.py` runs (prereg C2 measurement) | 3a: `ModuleNotFoundError` at `c2-counter.py:46` | Instrument cannot produce any receipt at 128e412 |
| D2 | L1/L2 discriminate base from candidate | 3b: `old rc=2 class=True` at base `0242085` (`c2-counter.py:242`) | Discriminating arm uses the repaired base; leg fails on good bytes |
| D3 | L5 fixture discriminates joined vs one-line | 3b: `new=None`; `r40-docstring-joined.py:100-102` vs `c2-counter.py:179` | Fixture rejects `--work`; SUMMARY never prints |
| D4 | L4 verifies the class/trigger map (prereg kill: "any observed class mapping disagrees with runtime") | M3, M4 PASS | Substring check accepts a contradicted trigger; unprobed classes unchecked |
| D5 | L4 measures wrapped-trigger reading (predicate) | M1 FAIL | Leg rewards the wrap, penalises the correct unwrapped docstring |
| D6 | Base vs candidate comparison of the drift tool | `git diff --quiet 0242085 128e412 -- tools` empty | `missing_old` == `missing_new` by construction; no tool change in r40 |
| D7 | "every refusal class the code can raise is named" (`tools/souji-worktree-drift.py:41-42`) | `USAGE` unmapped; bleed at `:61` | Docstring/analyser disagree; no leg checks it |

## 5. Verdict per axis

- C2 L4 predicate as landed: **FALSIFIED** (3a, 3c M1/M3/M4).
- Joined reading: **FALSIFIED** as a wrong contract — it measures layout, so the r40 prereg's "a correct fix passes" is not satisfied (3c M1).
- C2 counter receipt at landed revision: **FALSIFIED** — cannot run (3a); shimmed run reads 4/7 (3b).
- Post-landing commit `8a5fbdb` fixes D1 and D2; D3 is fixed only if `r40-docstring-joined.py` accepts `--work` (not checked at HEAD). HEAD L4 logic (`HEAD:census/round-40/c2-counter.py:298`) is unchanged, so D4-D7 still apply at HEAD. Not re-measured at HEAD (archive is 177 MB; L4 reproduced on landed bytes instead).

## 6. Re-run recipe (for the L1)

```
L=/home/vgpnk/Projects/shokunin/souji-shokunin; C=128e412b0ced3c243dc27c3dd3332054a611bc2e
S=/fast/scratch/hyaku/souji-r40/w2/<seat>; mkdir -p $S/landed $S/shim
git -C $L show $C:census/round-40/c2-counter.py > $S/landed/c2-counter.py
git -C $L show $C:census/round-40/docstring-classes.py > $S/landed/docstring-classes.py
git -C $L show $C:tools/souji-worktree-drift.py > $S/landed/drift-at-landed.py
python3 -B $S/landed/c2-counter.py --help            # D1: ModuleNotFoundError
cp $S/landed/docstring-classes.py $S/shim/docstring_classes.py; cp $S/landed/c2-counter.py $S/shim/
python3 -B $S/shim/c2-counter.py --root $L --rev $C --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/shim   # 3b
rm -rf -- "$S"
```
Mutant M1 (rewrap) is a single `str.replace` on `drift-at-landed.py`: `"  RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes\n                         --root\n"` → `"  RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes --root\n"`, then run the L4 logic from `c2-counter.py:249-274` with the mutant as `--tool`.

## 7. file:line index

- `census/round-40/c2-counter.py:46` — import name mismatch (D1)
- `census/round-40/c2-counter.py:74-78` — FROZEN_PAIRS (3 entries)
- `census/round-40/c2-counter.py:80-85` — SYNTHETIC_DOC (L4b, hard-coded)
- `census/round-40/c2-counter.py:179` — `--work` appended (D3)
- `census/round-40/c2-counter.py:242` — L1 base arm uses base-rev (D2)
- `census/round-40/c2-counter.py:248-274` — L4
- `census/round-40/c2-counter.py:262-264` — `raised != cls` (runtime check)
- `census/round-40/c2-counter.py:271` — `ok` requires non-empty `missed_by_first` (D5)
- `census/round-40/docstring-classes.py:34` — CLASS_LINE requires hyphen (USAGE dropped)
- `census/round-40/docstring-classes.py:43-70` — `_entries`; `:63` continuation rule
- `census/round-40/docstring-classes.py:73-80` — `class_entries` / `first_line_entries`
- `tools/souji-worktree-drift.py:41-42` — "Every refusal class ... named here" claim (D7)
- `tools/souji-worktree-drift.py:44-45` — RECORD-MISSING (EACCES on line 44)
- `tools/souji-worktree-drift.py:46-48` — RECORD-MALFORMED (missing on line 46)
- `tools/souji-worktree-drift.py:49` — RECORD-EMPTY (no trigger; M4)
- `tools/souji-worktree-drift.py:50-51` — RECORD-OUTSIDE-ROOT (`--root` wrapped to line 51)
- `tools/souji-worktree-drift.py:61` — USAGE (bleeds into JSON-UNWRITABLE)
- `tools/souji-worktree-drift.py:168` — RECORD-EMPTY raised
- `tests/fixtures/r40-docstring-joined.py:100-102` — no `--work` (D3)
- `census/round-39/c2-counter.py:133-143` — r39 docstring_classes (first line only)
- `census/round-39/c2-counter.py:221-226` — r39 runtime probes
- `census/round-39/c2-counter.py:230-232` — r39 L4 substring check
- `corpus/lessons/round-39.md:66` — R10
- `corpus/lessons/round-39.md:78-82` — M1 account
- `corpus/QUALITY.md:238` — Q91

## 8. Scratch

Scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2revenger02` was created for this seat and **removed**; `test -e` returned absent. Nothing was written outside it except this report.
