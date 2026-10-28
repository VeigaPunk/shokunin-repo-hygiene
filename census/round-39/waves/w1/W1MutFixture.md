# W1MutFixture — mutation probe: does the r39 fixture's kill power depend on its own cases?

Role: mutation-tester (advisory; L1 integrates). Round 39 wave 1, C3 coverage.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (lane tip `2201778e7736af82e7d8a42dec2494f115bf3923`).
Frozen contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`, base `ed30b7f5b77939c9073348d810730bc4f355708d`).
Scratch: `/fast/scratch/hyaku/souji-r39/W1MutFixture` (explicit `--scratch`/`TMPDIR`, no `/tmp`). Removed at end (see Restoration).
No tool installs were needed (python3 stdlib + `git` only). No git/jj mutation was run; all git calls were read-only (`show`, `rev-parse`, `status`).

## Target of the probe

The frozen C3 predicate claims four record-rule mutants (M11 trailing-space tolerance, M12 CRLF
splitting broken, M13 outside-root guard removed, M14 indented comments accepted) are killed by
`tests/fixtures/r39-drift-record-rules.py`, and the base fixture leaves all four alive. This probe
asks the falsification question: **is each kill caused by the fixture case that names that
behaviour, or does the battery kill for an unrelated reason?** Four single-case deletions of the
candidate fixture, one per behaviour, are scored by the unmodified counter.

Lane bytes under test — identical before and after every run (see Restoration):

```
$ sha256sum tests/fixtures/r39-drift-record-rules.py tools/souji-worktree-drift.py census/round-39/c3-counter.py
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d  tests/fixtures/r39-drift-record-rules.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
ff18d64c09f48a2ee8fd9502ad8e6d549a92466fd7aad777b31ba7b513d3bcd1  census/round-39/c3-counter.py
```

Fixture/tool hashes equal the `fixture_sha=567c37a679f5` / `tool_sha=e48ed08e6728` recorded in
`census/round-39/records/c3-after.txt`, so the probe scores the same bytes the after-receipt scored.

## Fixture case inventory (7 cases, `census/round-39/c3-counter.py` requires `cases>=6`)

`good` · `trailing-space` · `total-before-rows` · `crlf` · `outside-root` · `indented-comment` ·
`comments-total-only`

Four case bodies were located in the lane fixture and asserted to occur exactly once before deletion
(no fuzzy matching, no reflow):

```
trailing-space occurrences: 1
crlf occurrences: 1
outside-root occurrences: 1
indented-comment occurrences: 1
```

Each mutant fixture is the pristine bytes minus exactly that case's statement, written to scratch,
byte-length checked (`len(mutated) == len(src) - len(deleted)`), and `compile()`-checked:

```
trailing-space syntax_rc= 0 lines= 138 sha= e8a33a5ded4c
crlf syntax_rc= 0 lines= 130 sha= b56c7f2008b7
outside-root syntax_rc= 0 lines= 138 sha= 139c91e3e664
indented-comment syntax_rc= 0 lines= 139 sha= d28fe59d5309
```

## Check 1 — pristine baseline (control)

```
$ (cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=/fast/scratch/hyaku/souji-r39/W1MutFixture \
   python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
   --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
   --fixture /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r39-drift-record-rules.py \
   --scratch /fast/scratch/hyaku/souji-r39/W1MutFixture)
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

Verdict: **PASS** — reproduces the frozen after-state (`killed=4 survived=0 pristine=ok base_killed=0`,
`cases=7 >= 6`), so the probe starts from a live battery.

## Check 2 — delete the trailing-space case

```
$ (cd <lane> && TMPDIR=<scratch> python3 -B census/round-39/c3-counter.py --root <lane> --rev 2201778e… \
   --base-rev ed30b7f5… --fixture /fast/scratch/hyaku/souji-r39/W1MutFixture/r39-drop-trailing-space.py --scratch <scratch>)
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=3 survived=1 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=e8a33a5ded4c
rc=1
```

Verdict: **KILL POWER ATTRIBUTED** — M11 stops being killed; M12/M13/M14 stay killed and the
pristine arm stays `ok` at `cases=6` (≥ the frozen floor). The trailing-space case is the sole
detector of M11.

## Check 3 — delete the crlf case

```
SUMMARY line: MUTANT M12 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M11 killed=yes / M13 killed=yes / M14 killed=yes  (each rc=1 fails=1 crash=False, base rc=0 fails=0)
SUMMARY mutants=4 killed=3 survived=1 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=b56c7f2008b7
rc=1
```

Verdict: **KILL POWER ATTRIBUTED** — only M12 loses its kill; the other three mutants and the
pristine arm are unaffected.

## Check 4 — delete the outside-root case

```
SUMMARY line: MUTANT M13 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M11 killed=yes / M12 killed=yes / M14 killed=yes  (each rc=1 fails=1 crash=False, base rc=0 fails=0)
SUMMARY mutants=4 killed=3 survived=1 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=139c91e3e664
rc=1
```

Verdict: **KILL POWER ATTRIBUTED** — only M13 loses its kill.

## Check 5 — delete the indented-comment case

```
SUMMARY line: MUTANT M14 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
MUTANT M11 killed=yes / M12 killed=yes / M13 killed=yes  (each rc=1 fails=1 crash=False, base rc=0 fails=0)
SUMMARY mutants=4 killed=3 survived=1 pristine=ok base_killed=0 cases=6 tool_sha=e48ed08e6728 fixture_sha=d28fe59d5309
rc=1
```

Verdict: **KILL POWER ATTRIBUTED** — only M14 loses its kill.

Every one of the four assigned deletions maps 1:1 onto exactly one surviving mutant, and the counter
exits 1 (`survived=1`) in all four mutated runs: **no case in the assignment is dead weight**.

## Check 6 — which case actually fails under each mutant (attribution in the fixture's own output)

Pristine lane fixture run directly against each mutant tool extracted from committed bytes
(`git show 2201778e…:tools/souji-worktree-drift.py`, mutation anchored exactly once):

```
$ python3 -B tests/fixtures/r39-drift-record-rules.py --tool <M11-tool.py> --work <scratch>
case-trailing-space=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] …
$ … --tool <M12-tool.py>
case-crlf=FAIL rc=2 out='REFUSAL RECORD-MALFORMED: line 1 does not match the census schema …
$ … --tool <M13-tool.py>
case-outside-root=FAIL rc=1 want=2 missing=['RECORD-OUTSIDE-ROOT'] out='DRIFT\tABSENT\t../escape\trecorded regs=1 …
$ … --tool <M14-tool.py>
case-indented-comment=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] …
$ … --tool <pristine-tool.py>
case-good=PASS
case-trailing-space=PASS
case-total-before-rows=PASS
case-crlf=PASS
case-outside-root=PASS
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=7 fail=0
```

Verdict: **PASS** — the failing case name under each mutant equals the case targeted by that
mutant's documented defect, and the pristine tool passes all 7 cases. The kill is not incidental:
M11 produces `rc=0` (silently accepts the trailing-space line), M13 produces `rc=1` with a DRIFT row
where a refusal is required, i.e. the mutants are real behaviour changes, not import/anchors noise.

## Check 7 — the three non-assigned cases (dead-weight scan of the rest of the fixture)

Single deletion of each remaining case, same command shape:

```
drop-good                -> SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6 sha=d7b9bc65a057  rc=0
drop-total-before-rows   -> SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6 sha=57a46a21d7db  rc=0
drop-comments-total-only -> SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=6 sha=f3b06e2ba1d3  rc=0
```

Verdict: **COVERAGE NOTE (not a failure of the frozen contract)** — `good`, `total-before-rows` and
`comments-total-only` carry no kill power for M11-M14. They are not asserted by C3 and are not
required to discriminate these four mutants; they are hygiene/ordering cases whose only contract
role is the `cases>=6` floor. No frozen predicate claims otherwise, so nothing here falsifies C3 —
but any future claim that the fixture's *seven* cases are all discriminating would be false: four of
seven discriminate.

## Check 8 — the `cases>=6` floor behaves as a floor (fail-closed)

Double deletion (trailing-space + crlf → 5 cases), same command shape:

```
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=5
rc=1
```

Verdict: **PASS (fail-closed)** — a short fixture voids the run instead of yielding a pass, exactly
as the frozen kill rule requires ("if the candidate fixture carries fewer than six cases"). Consequence
for calibration: the candidate fixture sits only **one case above** the frozen floor, so removing any
two cases — including two of the four discriminating ones — turns a would-be survivor into a void run
rather than a silently passing one. The floor cannot be evaded by case deletion, but the margin is 1.

## Verdict summary

| Check | Probe | Observed | Verdict |
|---|---|---|---|
| 1 | pristine baseline | `killed=4 survived=0 pristine=ok base_killed=0 cases=7`, rc 0 | PASS |
| 2 | delete trailing-space | M11 `killed=no`; `killed=3 survived=1`, rc 1 | KILL ATTRIBUTED |
| 3 | delete crlf | M12 `killed=no`; `killed=3 survived=1`, rc 1 | KILL ATTRIBUTED |
| 4 | delete outside-root | M13 `killed=no`; `killed=3 survived=1`, rc 1 | KILL ATTRIBUTED |
| 5 | delete indented-comment | M14 `killed=no`; `killed=3 survived=1`, rc 1 | KILL ATTRIBUTED |
| 6 | per-case attribution | each mutant fails exactly its own case; pristine 7/7 | PASS |
| 7 | delete good / total-before-rows / comments-total-only | `killed=4`, rc 0 each | COVERAGE NOTE (no kill power, 4 of 7 discriminate) |
| 8 | delete two cases (5 left) | `pristine=FAIL cases=5`, rc 1 | PASS (fail-closed; floor margin = 1) |

**No coverage defect in the frozen C3 contract was found by this probe.** Each of the four assigned
case deletions stops exactly one mutant from being killed, so all four cases are load-bearing and the
battery's kills depend on them. The only observations for the L1 are advisory: (a) three of the seven
cases (`good`, `total-before-rows`, `comments-total-only`) do not discriminate M11-M14 and exist to
satisfy inventory/ordering plus the `cases>=6` floor; (b) the fixture is one case above the frozen
floor, so the floor is 7-vs-6, not 7-vs-4.

## Restoration

No lane byte was mutated: every mutation landed on a copy under `/fast/scratch/hyaku/souji-r39/W1MutFixture`.
After all runs:

```
$ sha256sum tests/fixtures/r39-drift-record-rules.py tools/souji-worktree-drift.py
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d  tests/fixtures/r39-drift-record-rules.py
e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76  tools/souji-worktree-drift.py
$ git status --porcelain
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```

Hashes equal the pre-run values; `git status` is byte-identical to the state observed before the
first run (those five untracked files are pre-existing, not mine). Scratch tree removed and verified
below; no scratch remains on disk.
