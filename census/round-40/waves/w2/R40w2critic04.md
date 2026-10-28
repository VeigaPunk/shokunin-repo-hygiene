# R40w2critic04 — C2 frozen refusal-class list completeness (falsify)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Landed instrument commit: 128e412b0ced3c243dc27c3dd3332054a611bc2e (ancestor of lane HEAD 549d9ec5…, verified with `git merge-base --is-ancestor`)
Base revision: 0242085909fb6a4ee041c5443d76316ac6d59d4b (r39 tip)
Defect revision: ed30b7f5b77939c9073348d810730bc4f355708d (counter default, resolves)
Attacked: `tools/souji-worktree-drift.py` (docstring + `Refusal(` / `raise` sites), `census/round-40/c2-counter.py` FROZEN_PAIRS / classify / observed_pairs / L4, `census/round-40/docstring-classes.py` CLASS_LINE and join, `tests/fixtures/r40-docstring-joined.py`, `tests/fixtures/r38-drift-write-envelope.py:195-207` (the consumer leg that is the only non-C2 check of the docstring).

## Verdict

**FALSIFIED.** The frozen C2 list names 3 (class, trigger) pairs for a tool that can raise 10 refusal classes. Leg L4 is vacuous for the 7 classes it omits: deleting their documentation entries, or replacing their trigger text with wrong text, leaves the counter at `SUMMARY legs=7 pass=7 fail=0 harm=0`. Two further defects in the analyser: it cannot parse the one-word class `USAGE`, and it silently folds the `USAGE` line into the `JSON-UNWRITABLE` entry. An uncaught exception path exits 1, which the tool's documented exit contract assigns to "drift rows found", and it has no refusal class at all.

## 1. Every refusal class the audited tool can raise

Source: `tools/souji-worktree-drift.py` (landed bytes at 128e412). Docstring class list: lines 44–61. Raise sites from `grep -n "REFUSAL\|raise \|sys.exit\|return 2" tools/souji-worktree-drift.py`:

| Class | raise sites (file:line) | Documented at | In frozen C2 FROZEN_PAIRS? |
|---|---|---|---|
| RECORD-MISSING | :136 | :44-45 | yes (trigger `EACCES`) |
| RECORD-MALFORMED | :135, :139, :159, :166, :171, :173, :175 | :46-48 | yes (trigger `ENOENT`) |
| RECORD-EMPTY | :168 | :49 | **no** |
| RECORD-OUTSIDE-ROOT | :293, :310 | :50-51 | yes (trigger `--root`) |
| USAGE | :279, :441 (`REFUSAL USAGE: --timeout`) | :61 | **no** |
| JSON-NOT-REGULAR | :264, :269 | :56-57 | **no** |
| JSON-IS-RECORD | :334 | :54-55 | **no** |
| JSON-INSIDE-MEASURED-TREE | :341 | :52-53 | **no** |
| JSON-HARDLINKED | :418 | :58 | **no** |
| JSON-UNWRITABLE | :428 (also reached for any `OSError` in `open_nofollow`/write via :427) | :59-60 | **no** |

Ten classes are raised; three are frozen. **Seven are omitted**: RECORD-EMPTY, USAGE, JSON-NOT-REGULAR, JSON-IS-RECORD, JSON-INSIDE-MEASURED-TREE, JSON-HARDLINKED, JSON-UNWRITABLE.

Frozen list: `census/round-40/c2-counter.py:74-78`:
```
FROZEN_PAIRS = (
    ("RECORD-MALFORMED", "ENOENT"),
    ("RECORD-MISSING", "EACCES"),
    ("RECORD-OUTSIDE-ROOT", "--root"),
)
```
Runtime observation is also limited to three classes: `observed_pairs` (`c2-counter.py:170-192`) probes only the three frozen classes, and `classify` (`c2-counter.py:162-167`) recognises only `RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT`. It has no way to name any `JSON-*` or `USAGE` result (it returns `NO-CLASS`), so the counter cannot observe those classes even if a pair were added without editing the counter.

Non-class exits (not refusals, not named): argparse errors (exit 2, argparse text). Uncaught exceptions (exit 1), see section 4.

## 2. Commands and real output — landed bytes

Environment: `id -u` = 1000; `git --version` = 2.56.0; `python3 --version` = 3.14.8.

```
$ python3 -B census/round-40/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
    --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
    --scratch /fast/scratch/hyaku/souji-r40/w2/R40w2critic04
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
rc=0
```

Analyser output on landed bytes (`python3 -B census/round-40/docstring-classes.py tools/souji-worktree-drift.py | cut -f1`): 9 keys — RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT, JSON-INSIDE-MEASURED-TREE, JSON-IS-RECORD, JSON-NOT-REGULAR, JSON-HARDLINKED, JSON-UNWRITABLE. `USAGE` is not a key.

Mis-join, confirmed:
```
$ python3 -B -c "...class_entries(docstring_of(src))...; print('USAGE key present:', 'USAGE' in e); print(repr(e['JSON-UNWRITABLE']))"
USAGE key present: False
JSON-UNWRITABLE joined text: 'the --json write failed (including a symlinked path component, refused by the O_NOFOLLOW walk) USAGE                  --root is not a directory, or --timeout < 1'
```
Cause: `census/round-40/docstring-classes.py:34` `CLASS_LINE` requires a hyphenated token (`(?:-[A-Z0-9]+)+`), so `USAGE` at tool docstring line 61 is not an entry; it is treated as a continuation (`:63-66`) and joined into the previous entry. Consequence: the map attributes `--root` and `--timeout` to JSON-UNWRITABLE, which is false for that class.

## 3. Attack: is L4 vacuous for the omitted classes? — YES

Scratch: clone of the lane under /fast/scratch/hyaku/souji-r40/w2/R40w2critic04/lane (toplevel asserted equal to clone dir before every commit), mutant commits with throwaway identity inside that clone only. Each mutant was run through the real counter with `--rev <mutant> --base-rev 0242085… --scratch <scratch>`.

**Control (M2): remove the RECORD-OUTSIDE-ROOT trigger line (`--root`, tool docstring line 51).** Expected: L4 fails.
```
LEG L4 FAIL pairs=3 missing_new=['RECORD-OUTSIDE-ROOT-missing-trigger(--root)'] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
SUMMARY legs=7 pass=5 fail=2 harm=0
```
So L4 does detect a removed frozen trigger.

**M1: remove all seven omitted entries from the docstring (11 lines removed).**
```
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L6 FAIL ... r38-drift-envelope=11/12(base 12/12) ...
SUMMARY legs=7 pass=6 fail=1 harm=1
```
L4 passes; the only detector is the r38 consumer leg (see below).

**Per-class removal (one commit per class, counters run in parallel).** For each of the seven classes, L4 = PASS, every run:
```
RECORD-EMPTY                 rc=1 LEG L4 PASS ... | failing legs=['L6']
USAGE                        rc=1 LEG L4 PASS ... | failing legs=['L6']
JSON-NOT-REGULAR             rc=1 LEG L4 PASS ... | failing legs=['L6']
JSON-IS-RECORD               rc=1 LEG L4 PASS ... | failing legs=['L6']
JSON-INSIDE-MEASURED-TREE    rc=1 LEG L4 PASS ... | failing legs=['L6']
JSON-HARDLINKED              rc=1 LEG L4 PASS ... | failing legs=['L6']
JSON-UNWRITABLE              rc=1 LEG L4 PASS ... | failing legs=['L6']
```
Only L6 catches them, through `tests/fixtures/r38-drift-write-envelope.py:201-207` (`docstring-enum`: `missing` = raised tokens absent from the doc, `phantom` = doc tokens absent from code). That check tests class-token presence only.

**Trigger-only mutant (the decisive one).** Changed trigger text for four omitted classes, keeping the class tokens:
- RECORD-EMPTY `no REPO rows` → `no rows at all`
- JSON-HARDLINKED `the --json target has more than one link` → `the target has a link count above one`
- USAGE `--root is not a directory, or --timeout < 1` → `bad arguments were supplied`
- JSON-NOT-REGULAR `the --json target exists and is not a regular file` → `the target exists`

```
$ python3 -B census/round-40/c2-counter.py --root <scratch clone> --rev <mutant> --base-rev 0242085… --scratch <scratch>
LEG L1 PASS ...
LEG L2 PASS ...
LEG L3 PASS ...
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS ... r38-drift-envelope=12/12(base 12/12) ...
SUMMARY legs=7 pass=7 fail=0 harm=0
rc=0
```
Verdict on the leg: a wrong trigger, and a deleted USAGE trigger, reach `SUMMARY … pass=7 fail=0 harm=0`. No leg of the round checks trigger text for these classes. The brief's "every observed class/trigger pair must be verified" is not met for them.

Note on the USAGE case: the entry is documented as `USAGE --root … --timeout < 1`; the trigger `--root` in the joined text is the JSON-UNWRITABLE leak above, not USAGE's own text, so removing USAGE's trigger changes the joined text of JSON-UNWRITABLE and L4 still passes because its pairs are not checked for it.

## 4. Other attacks

**4a. Undocumented exit path (contract hole, not a class).** The tool's docstring says exit 1 = drift rows found and exit 2 = could-not-evaluate, and that "every refusal class the code can raise is named here". `measure()` calls `git()` which only catches `TimeoutExpired`; a missing `git` binary escapes as an uncaught exception.
```
$ env -i PATH=/nonexistent /usr/bin/python3 -B tools/souji-worktree-drift.py --root <fleet> --record <rec>   # fleet has repo1 with .git, record "REPO repo1 regs=1 prunable=0"
PATH-probe rc=1 stdout=''
PATH-probe stderr-tail=["FileNotFoundError: [Errno 2] No such file or directory: 'git'"]
```
rc=1 collides with "drift rows found"; no class names it. C2 cannot see this; no leg covers it. Source: `tools/souji-worktree-drift.py:184-198` (`measure`) and `:300` (`git rev-parse` in `run`), with `git()` at `:103-121`.

**4b. The counter's own classify list.** `census/round-40/c2-counter.py:164` enumerates four classes. It returns `NO-CLASS` for every JSON-* and USAGE result, so even a future pair for those classes would fail closed as "not raised" rather than be observed. Repairs need a counter edit, which is out of scope here.

**4c. RECORD-MISSING ELOOP.** The docstring (`:44-45`) and code (`:136`, every non-ENOENT errno) both cover ELOOP; C2 only verifies `EACCES`. Not a separate class, recorded for completeness.

**4d. Pair verification is substring membership.** `c2-counter.py:292-297` checks `trigger in new_joined[cls]`, a substring of the joined text, not that the trigger belongs to that class's own line. This is the source of the JSON-UNWRITABLE leak in section 2 being invisible to the counter.

## 5. Things I did NOT attack / out of scope

- C1 and C3 instruments: not in this lane.
- Did not run the L5/L6 consumer fixtures independently beyond what the counter printed.

## 6. Installs

None. No tool was installed or updated. No pacman.

## 7. Lane state and cleanup

- Writes: only the scratch directory and this report. The counter was run with `--scratch` pointing into my scratch dir; it wrote nothing into the lane.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short` at the time of my final check showed ` M SCORECARD.md` and untracked `census/round-40/records/{c1-after-d.txt,c1-before.txt,c2-after-d.txt,c3-after-d.txt,census-before.txt}`. I did not create, modify, or stage any of these; they belong to other seats or the main agent.
- Mutant commits lived only in the scratch clone (toplevel asserted equal to that clone's path before each commit).
- **Scratch removed:** `/fast/scratch/hyaku/souji-r40/w2/R40w2critic04` deleted with `shutil.rmtree`; `os.path.exists` after removal = False.

## 8. Re-run recipe for the L1 (landed bytes, no scratch clone needed)

```
python3 -B census/round-40/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --scratch /fast/scratch/hyaku/souji-r40/w2/<your-dir>
python3 -B census/round-40/docstring-classes.py tools/souji-worktree-drift.py | cut -f1
```
The mutant runs need a scratch clone with a committed mutant of `tools/souji-worktree-drift.py`; the commit recipe is in section 3.
