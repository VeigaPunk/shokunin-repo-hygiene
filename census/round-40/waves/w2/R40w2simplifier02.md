# R40w2simplifier02 — YAGNI review of the landed C2 analyser and counter (round 40, wave 2, falsify)

Seat: R40w2simplifier02 (role simplifier), leaf member, no subagent dispatch.
Landed revision attacked: **128e412b0ced3c243dc27c3dd3332054a611bc2e** (base 0242085909fb6a4ee041c5443d76316ac6d59d4b, r39 tip; defect revision ed30b7f5b77939c9073348d810730bc4f355708d).
Lane HEAD moved during this run to 549d9ec (and later 556c24a, 6ded124, 8a5fbdb). Every command below was run against a clone pinned at 128e412, never against the lane working tree.

## Verdict

**FALSIFIED** for the C2 counter as landed (`census/round-40/c2-counter.py` at 128e412):

1. It cannot start. `ModuleNotFoundError: No module named 'docstring_classes'` (landed `c2-counter.py:46`); the analyser is committed as `docstring-classes.py` (hyphen), so the `import docstring_classes as dc` at line 46 never resolves. Exit 1, no `SUMMARY` line, no receipt.
2. Even with a scratch-only module shim (the analyser copied to `docstring_classes.py` inside my scratch clone), the landed counter does not reach 7/7: `SUMMARY legs=7 pass=4 fail=3 harm=0`. L1 and L2 fail by construction (they compare against the repaired base instead of the defect revision), and L5 fails because the counter passes `--work` to a fixture whose argparse does not accept it.
3. The fix is not in the landed commit. It arrived in 8a5fbdb ("counter fixes — the C2 legs use the defect revision and the committed analyser"), which is a descendant of 128e412. The C2 receipt that exists (`records/c2-after.txt`, `measured_at: 8a5fbdb…`, `pass=7 fail=0`) therefore describes a later revision, not the landed bytes, and `corpus/knowledge/docstring-class-continuation-lines-r40.md` cites a `records/c2-after.txt` that does not exist at 128e412.

Simplifier axis (the assigned question): `first_line_entries` is **needed** (not deletable). The counter needs the one-line reading as its control arm, and so does the fixture's `--one-line` mode. Four candidates for deletion are listed below; one of them (`old_first`) is a pure dead store flagged by ruff F841.

## Environment and installs

- `ruff 0.17.2` at `/home/vgpnk/.local/bin/ruff` (already present; **not installed by this seat**, no install performed). Used read-only with `--no-fix --no-cache --isolated`.
- `pyflakes` absent (`ModuleNotFoundError`); not installed. No pacman used.
- No tool installs or updates by this seat.

## Scratch

- Root: `/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier02/` (clone at `clone/`, pinned with `git -C clone checkout 128e412…`, `git -C $S/clone rev-parse --show-toplevel` = `$S/clone`).
- The lane was only read (`git clone` of the lane into scratch, `git show`, `git grep`, `git log`, `git cat-file`). No commit, no mutating git, no write to the lane apart from this report.
- The module shim `clone/census/round-40/docstring_classes.py` exists only inside the scratch clone.
- Scratch removal: see the final section.

## Commands run and real output

### 1. Landed counter, as committed (the attack)

```
$ S=/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier02; C=$S/clone
$ cd $S && python3 -B $C/census/round-40/c2-counter.py --root $C --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S
Traceback (most recent call last):
  File ".../clone/census/round-40/c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'docstring_classes'
RC=1
$ ls $C/census/round-40/
assimilation  c1-counter.py  c2-counter.py  c3-counter.py  docstring-classes.py  preregistration.txt  sources
```

### 2. Landed counter with a scratch-only module shim (the arms behind the crash)

```
$ cp $C/census/round-40/docstring-classes.py $C/census/round-40/docstring_classes.py   # scratch clone only
$ python3 -B $C/census/round-40/c2-counter.py --root $C --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S
LEG L1 FAIL new rc=2 class=True old rc=2 class=True
LEG L2 FAIL new rc=2 class=True old rc=2 class=True
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 FAIL new=None old(one-line)=None
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=4 fail=3 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
RC=1
```

Why each failing leg fails:

- **L1 / L2** (`c2-counter.py:221-224`, `:232-235`): `old_p = run_citation(old_cit, root, ZERO, …, register_rev=args.base_rev)` runs the **repaired** r39 base. That base *does* refuse with `REV-UNRESOLVED`, so `old_has` is True and `leg("L1", new_ok and not old_has)` cannot pass. The discriminating revision is the defect revision ed30b7f, where the tool does not refuse. Check at ed30b7f:
  ```
  $ python3 -B $S/cit-ed30.py --root $C --rev 000…0 --register census/round-38/cells.tsv --register-rev ed30b7f5b77939c9073348d810730bc4f355708d
  MISMATCH R38-C1-1 FILE-ABSENT SCORECARD.md at 0000000000000000000000000000000000000000
  …
  rc=1
  ```
  (no `REV-UNRESOLVED`, so ed30 is the correct discriminator; the landed counter never used it). At the landed base: `REFUSAL REV-UNRESOLVED: --rev 0000… does not resolve to a commit`, `rc=2`.
- **L5** (`c2-counter.py:292-293`, `run_fixture` `:178-181` appends `--work`): the fixture's CLI has no such flag (`tests/fixtures/r40-docstring-joined.py:99-102`):
  ```
  $ python3 -B $F --analyzer $C/census/round-40/docstring-classes.py … --work $S
  r40-docstring-joined.py: error: unrecognized arguments: --work /fast/scratch/…
  ```
  so the counter gets no `SUMMARY` line and reports `new=None old(one-line)=None`.
- **L3** passes but is weak (see candidate D below).

### 3. Fixture, as landed (what L5 is supposed to measure)

```
$ python3 -B $F --analyzer $C/census/round-40/docstring-classes.py --tool $C/tools/souji-worktree-drift.py
case-synthetic-joined-has-trigger=PASS
case-synthetic-primary-has-trigger=PASS
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=PASS
case-outside-root-trigger-primary=PASS
case-record-missing-eacces=PASS
case-record-malformed-enoent=PASS
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=9 fail=0
RC=0
$ python3 -B $F --analyzer $C/census/round-40/docstring-classes.py --tool $C/tools/souji-worktree-drift.py --one-line
case-synthetic-joined-has-trigger=PASS
case-synthetic-primary-has-trigger=FAIL primary='the first physical line of this entry'
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=FAIL missing=['RECORD-OUTSIDE-ROOT(--root)']
case-outside-root-trigger-primary=FAIL primary='a record row, or the gitdir it resolves to, escapes'
case-record-missing-eacces=PASS
case-record-malformed-enoent=PASS
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=6 fail=3
RC=1
```

The joined and one-line readings separate on 3 cases. `class-sets-equal` and `joined-not-shorter` are PASS in **both** modes (see candidate C).

### 4. Invariant fuzz on the landed analyser (`class-sets-equal`, `joined-not-shorter`)

Script: `$S/fuzz-join.py` (scratch), 20 000 random docstrings from ten line shapes (class lines, continuation lines, blank, prose, lower-case token, duplicate class, tab-indented), comparing `class_entries` with `first_line_entries`:

```
$ python3 -B $S/fuzz-join.py $C/census/round-40/docstring-classes.py
cases=20000 class_set_mismatch=0 order_mismatch=0 joined_shorter=0 joined_not_prefix_extension=0
RC=0
```

Structural reason (`docstring-classes.py:43-70`): both readings run the same loop, insert a key only on a `CLASS_LINE` match (`:48-54`), and `join` only appends to an existing key (`:65-66`). The key set and order cannot differ, and the joined text is always `first + " " + …`. The two fixture cases are tautologies over this analyser.

### 5. Unused names (AST scan + ruff, landed bytes)

```
$ ruff check --no-cache --no-fix --select F,E9 --isolated $C/census/round-40/c2-counter.py $C/census/round-40/docstring-classes.py $C/tests/fixtures/r40-docstring-joined.py
F401 [*] `ast` imported but unused        --> clone/census/round-40/c2-counter.py:35:8
F841 Local variable `old_first` is assigned to but never used --> clone/census/round-40/c2-counter.py:256:9
Found 2 errors.
```

Same two findings at 8a5fbdb (`c2-counter.py:35` `import ast`, `:283` `old_first`), so the lane HEAD still carries them.

### 6. Callers of each analyser function (landed tree, excluding round-38/39 and `.ufo`)

```
$ git -C $C grep -n 'classes_from_source\|first_line_entries\|class_entries' 128e412… -- census tests tools corpus | (non-round-39 hits)
census/round-40/c2-counter.py:253 dc.classes_from_source(new_src)     (L4 joined, new)
census/round-40/c2-counter.py:254 dc.first_line_entries(...new_src)  (L4 one-line control, new)
census/round-40/c2-counter.py:255 dc.classes_from_source(old_src)     (L4 joined, base)
census/round-40/c2-counter.py:256 dc.first_line_entries(...old_src)  (DEAD: never read)
census/round-40/c2-counter.py:267-268 new_first check -> missed_by_first (L4 discriminator)
census/round-40/c2-counter.py:277-280 class_entries / first_line_entries on SYNTHETIC_DOC (L4b)
tests/fixtures/r40-docstring-joined.py:53-57 class_entries / first_line_entries (joined vs --one-line primary)
census/round-40/docstring-classes.py:87-96 __main__ CLI: no invocation anywhere in the tree (only the analyser's own usage string)
```

No file in the tree invokes `docstring-classes.py` as a command. `corpus/README.md:788` and `corpus/knowledge/docstring-class-continuation-lines-r40.md:29` name the file as the analyser, not as a CLI.

## Answer to the assigned question

**Is `first_line_entries` needed outside the fixture's `--one-line` mode?** Yes. The counter itself needs it:
- L4's discriminator `missed_by_first` (`c2-counter.py:267-268`, `:271`) is the proof that "the join is load-bearing", and the only way to compute the one-line reading is `first_line_entries`.
- L4b (`:277-281`) reads it for the synthetic control.
- The fixture's `--one-line` mode (`r40-docstring-joined.py:54-57`, `:57`) uses the same function.

Keep the function and the `join` flag in `_entries` (`docstring-classes.py:43`, `:65`). Deleting it would delete the control arm, which is the one thing that makes C2's "join is load-bearing" claim checkable.

## Candidate deletions (each with reason and evidence)

| # | Where (landed) | Candidate | Reason | Evidence | Tradeoff |
|---|---|---|---|---|---|
| A | `census/round-40/c2-counter.py:35` | `import ast` | Dead import; nothing in the counter calls `ast.*` | ruff F401; AST scan | None. |
| B | `census/round-40/c2-counter.py:256` | `old_first = dc.first_line_entries(...)` | Dead store; the variable is never read (the L4 base check uses only `old_joined`) | ruff F841; AST scan (`old_first` loaded nowhere) | None; the call is pure. |
| C | `census/round-40/c2-counter.py:277-281` (L4b) **and** `tests/fixtures/r40-docstring-joined.py:88-94` (`class-sets-equal`, `joined-not-shorter`) | L4b duplicates fixture cases `synthetic-joined-has-trigger` and `synthetic-one-line-misses-trigger` (`fixture:64-66`, `:70-72`) on the same `SYNTHETIC_DOC`; L4b is run in L5 already, so it can only double-count. The two fixture cases `class-sets-equal` / `joined-not-shorter` cannot fail (fuzz 0/20 000; structural reason above). | Remove L4b; remove the two tautological fixture cases. | §4 fuzz, §3 both-mode PASS | Changes the documented fixture count `cases=9` (knowledge doc, records) to `cases=7`; the counter's L5 gate checks `fail` counts, not the total, so the gate is unaffected. |
| D | `census/round-40/docstring-classes.py:87-96` | `__main__` CLI | No caller in the tree; no doc names it as a command | §6 | Loses a manual inspection command. |

Candidates considered and **kept**:

- `first_line_entries` and the `join` flag (§ above): needed as the control.
- `classes_from_source` (`docstring-classes.py:83-84`): a two-line wrapper used by the counter at `:253`, `:255`. Inlining is cosmetic; keep.
- L3 (`c2-counter.py:242-246`): weak but can fail. It checks only `rc == 2` for both new and old with `--register-rev ZERO`; the probe `REFUSAL REV-UNRESOLVED: --register-rev 0000… does not resolve` shows the new tool refuses for the right class, but the leg does not assert the class. Not a cannot-fail arm (a changed rc fails it); recorded as a precision gap, not a deletion.
- L6 harm arm (`new_r[1] < old_r[1]`): can fail; keep.

Duplicate authority (not a deletion, a tradeoff): `FROZEN_PAIRS` (`c2-counter.py:74-78` vs `fixture:27-31`) and `SYNTHETIC_DOC` (`c2-counter.py:80-85` vs `fixture:33-38`) are defined twice and must stay in sync by hand. Removing one copy would need the fixture to receive the pairs through its CLI, which changes the fixture contract; reported, not recommended without a design decision.

## Verdict per arm (landed bytes, 128e412)

| Arm | Can fail? | Landed result | Note |
|---|---|---|---|
| import of analyser (`:46`) | yes | crashes | FALSIFIED |
| L1 (`:221-224`) | yes | FAIL with shim | wrong revision (base, not defect) |
| L2 (`:232-235`) | yes | FAIL with shim | same as L1 |
| L3 (`:242-246`) | yes, weakly | PASS | rc-only; precision gap |
| L4 (`:253-272`) | yes | PASS with shim | joined reading verified; `--root` found only in joined |
| L4b (`:277-281`) | yes, but duplicates L5 | PASS | candidate C |
| L5 (`:292-296`) | yes | FAIL with shim | `--work` unknown to fixture |
| L6 (`:312-325`) | yes | PASS with shim | consumers 10/10, 12/12, 12/12, 7/7, 16/16, 14/14, 8/8 |
| fixture `class-sets-equal` / `joined-not-shorter` | **no** | PASS in both modes | candidate C |

## Repair evidence (for the L1 attack; not a simplifier finding)

- 8a5fbdb (`git log --format='%h %s' 128e412..549d9ec -- census/round-40/c2-counter.py` → 8a5fbdb) adds `--defect-base-rev` and `load_analyzer` (from the committed analyser by path, `c2-counter.py` at 8a5fbdb) and passes `with_work=False` to the fixture. The landed commit has none of these.
- At 8a5fbdb the same two ruff findings remain (`:35`, `:283`), so candidates A and B are still live on the lane HEAD.

## Scope limits

- Attacked only 128e412 bytes plus the shim described above. The shim is a scratch-only copy of the analyser under a second name, used to measure the arms behind the crash; it is not a claim about landed behaviour.
- Did not run the C1 or C3 counters (other seats).
- Lane HEAD is past 128e412; statements about HEAD are labelled as such.

## Reproduce

```
S=/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier02; C=$S/clone
git clone -q /home/vgpnk/Projects/shokunin/souji-shokunin $C && git -C $C -c advice.detachedHead=false checkout -q 128e412b0ced3c243dc27c3dd3332054a611bc2e
cd $S && python3 -B $C/census/round-40/c2-counter.py --root $C --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S   # RC=1 ModuleNotFoundError
cp $C/census/round-40/docstring-classes.py $C/census/round-40/docstring_classes.py                                  # scratch-only shim
cd $S && python3 -B $C/census/round-40/c2-counter.py --root $C --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S   # SUMMARY legs=7 pass=4 fail=3
ruff check --no-cache --no-fix --select F,E9 --isolated $C/census/round-40/c2-counter.py                              # F401 :35, F841 :256
```

## Scratch removal

Removed: `rm -rf -- /fast/scratch/hyaku/souji-r40/w2/R40w2simplifier02` run before yield; re-check `test -e` returned absent (`SCRATCH_REMOVED`). The seat's `/fast/scratch/hyaku/souji-r40/w2/` no longer contains `R40w2simplifier02`.
