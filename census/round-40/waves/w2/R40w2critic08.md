# R40w2critic08 — r40 C3 fixture pairings (falsify)

Role: critic. Target: `tests/fixtures/r40-drift-record-branches.py` pairings. Question: does each of the three
branches (multiple TOTAL rows, `--skip-unrecorded`, invalid UTF-8) have a paired case so that a mutant that
inverts the branch cannot pass both arms, and does any single-defect mutant survive the whole fixture?

Landed revision: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Bytes of `tools/souji-worktree-drift.py`
(sha256 `e48ed08e…2c76`) and `tests/fixtures/r40-drift-record-branches.py` (sha256 `a6ec36f0…7ee7`) are
identical at `128e412` and at HEAD `556c24a5…`. Base: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (ancestor of landed rev).
All reads were `git show <rev>:<path>` or the committed working files; nothing was committed or edited in the lane.

## Verdict

**FALSIFIED (pairings).** Three findings, one per branch:

1. Multiple TOTAL rows: the pair (`total-duplicate-identical` vs `total-conflicting-second`) does not isolate the
   duplicate-TOTAL decision. Mutant A3 (keep the first TOTAL only when its `repos` equals the second's) passes BOTH
   arms and every other case. Additionally the TOTAL `regs` and `prunable` consistency guards have no case at all
   (A7, A8, A9 survive).
2. `--skip-unrecorded`: the pair (`skip-unrecorded-suppresses` vs `unrecorded-without-flag`) holds for every
   inversion of the UNRECORDED branch (B1, B2, B3 killed). Survivors are flag-scoped effects on recorded-repo drift
   that no case exercises (B5, B6): the fixture never produces REGS-CHANGED or PRUNABLE-CHANGED.
3. Invalid UTF-8: the pair (`invalid-utf8-in-repo-name` vs `invalid-utf8-in-comment`) only asserts the token
   `ABSENT` in the repo-name arm. Any decoder that keeps the byte non-fatal and yields a non-matching name passes
   both arms: `backslashreplace` (C4), `latin-1` (C5), `ascii`+`replace` (C6) pass 8/8. `surrogateescape` (C3) makes
   the fixture itself crash (no own SUMMARY), which the C3 counter scores as not-killed. The docstring's
   "becomes U+FFFD" is never asserted.

The declared mutants M15–M18 are all killed by the landed counter (run 1 below), so the counter's own declared
claim holds; the falsification is of the pairing claim in the fixture docstring (`tests/fixtures/r40-drift-record-branches.py:17-19`:
"each has an arm … so a mutant that inverts the branch cannot pass both") and of coverage beyond the four declared mutants.

## Commands run and real output

### Run 1 — official C3 counter at the landed rev (exit 0)
```
$ env -i PATH=/usr/local/bin:/usr/bin:/bin TMPDIR=$S/counter python3 -B census/round-40/c3-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
    --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/counter
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
counter rc=0
```
(`--rev HEAD` is refused by the counter: `REFUSAL COULD-NOT-EVALUATE: --rev HEAD does not resolve`; the counter needs a 40-hex rev.)

### Run 2 — pristine fixtures at the landed rev
```
$ env -i PATH=/usr/local/bin:/usr/bin:/bin TMPDIR=$S/fix python3 -B tests/fixtures/r40-drift-record-branches.py --work $S/fix
case-good=PASS / case-total-duplicate-identical=PASS / case-total-conflicting-second=PASS / case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS / case-unrecorded-without-flag=PASS / case-invalid-utf8-in-repo-name=PASS / case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0          fixture rc=0
$ ... python3 -B tests/fixtures/r39-drift-record-rules.py --work $S/fix
SUMMARY cases=7 pass=7 fail=0          base rc=0
```

### Run 3 — pairing mutant battery (the attack)
Driver, committed to the report directory as a named scratch file:
`.ufo/waves/round-40/w2/R40w2critic08-attack.py`. It reads the tool and both fixtures with `git show <rev>:<path>`,
asserts each anchor occurs exactly once, writes each mutant into a scratch dir, and scores it with the candidate
fixture and the base fixture using the counter's kill rule (rc 1, own `SUMMARY … fail>0`, no traceback on stderr).
```
$ env -i PATH=/usr/local/bin:/usr/bin:/bin TMPDIR=$S python3 -B \
    .ufo/waves/round-40/w2/R40w2critic08-attack.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --scratch $S/attack
PRISTINE candidate killed=False rc=0 fails=0 | base killed=False rc=0 fails=0
A1 [A] declared M15: keep FIRST TOTAL -> candidate_killed=yes (failing=total-conflicting-second) | base_killed=no
A2 [A] refuse any second TOTAL (even identical) -> candidate_killed=yes (failing=total-duplicate-identical) | base_killed=no
A3 [A] keep FIRST only when repos equal -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
A4 [A] declared M18: repos guard disabled -> candidate_killed=yes (failing=total-repos-disagrees) | base_killed=no
A5 [A] repos guard '!=' -> '<' -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
A6 [A] repos guard '!=' -> '>' -> candidate_killed=yes (failing=total-repos-disagrees) | base_killed=no
A7 [A] regs guard disabled -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
A8 [A] prunable guard disabled -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
A9 [A] regs guard '!=' -> '>' -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
A10 [A] whole TOTAL consistency block disabled -> candidate_killed=yes (failing=total-conflicting-second,total-repos-disagrees) | base_killed=no
B1 [B] inverted: skip only WITH the flag -> candidate_killed=yes (failing=good,total-duplicate-identical,skip-unrecorded-suppresses,unrecorded-without-flag,invalid-utf8-in-comment) | base_killed=no
B2 [B] declared M16: always scan -> candidate_killed=yes (failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment) | base_killed=no
B3 [B] never scan -> candidate_killed=yes (failing=unrecorded-without-flag) | base_killed=no
B4 [B] flag also suppresses ABSENT rows -> candidate_killed=yes (failing=invalid-utf8-in-repo-name) | base_killed=no
B5 [B] REGS-CHANGED row dropped entirely -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
B6 [B] flag suppresses REGS-CHANGED rows -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
C1 [C] declared M17: decode 'ignore' -> candidate_killed=yes (failing=invalid-utf8-in-repo-name) | base_killed=no
C2 [C] decode strict -> candidate_killed=yes (failing=invalid-utf8-in-repo-name,invalid-utf8-in-comment) | base_killed=no
C3 [C] decode 'surrogateescape' -> candidate_killed=NO (NO-SUMMARY rc=1) | base_killed=no
C4 [C] decode 'backslashreplace' -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
C5 [C] decode latin-1 -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
C6 [C] decode ascii + replace -> candidate_killed=NO (rc=0 fails=0) | base_killed=no
C7 [C] replace kept, U+FFFD stripped from REPO names -> candidate_killed=yes (failing=invalid-utf8-in-repo-name) | base_killed=no
C8 [C] U+FFFD in a comment line refused -> candidate_killed=yes (failing=invalid-utf8-in-comment) | base_killed=no
C9 [C] any U+FFFD line silently skipped -> candidate_killed=yes (failing=invalid-utf8-in-repo-name) | base_killed=no
SURVIVORS-OF-CANDIDATE A3,A5,A7,A8,A9,B5,B6,C3,C4,C5,C6
```
No mutant is killed by the base fixture (r39), as the counter requires for the declared set.

### Run 4 — both-arm survivors, shown on the candidate fixture (all 8 cases PASS)
```
$ env -i PATH=... TMPDIR=$A/A3/cand python3 -B $A/r40-branches.py --tool $A/A3/tool.py --work $A/A3/cand   → 8/8 PASS, SUMMARY cases=8 pass=8 fail=0, rc=0
$ ... --tool $A/C4/tool.py  → 8/8 PASS, rc=0
$ ... --tool $A/C6/tool.py  → 8/8 PASS, rc=0
$ ... --tool $A/C5/tool.py  → 8/8 PASS, rc=0
```

### Run 5 — direct repro of the survivors (fleet of alpha, beta recorded; gamma unrecorded; `--skip-unrecorded`)
Record `a3dup.tsv` = REPO alpha regs=1, REPO beta regs=1, TOTAL repos=2 regs=2, TOTAL repos=2 regs=1 (same repos, conflicting regs):
```
pristine: rc=2  REFUSAL RECORD-MALFORMED: TOTAL regs=1 but REPO rows sum to 2
A3:       rc=0  SUMMARY record=…/a3dup.tsv record_repos=2 record_regs=2 …
```
Record `a7.tsv` = TOTAL repos=2 regs=3 (repos correct, regs wrong): pristine rc=2 `TOTAL regs=3 but REPO rows sum to 2`; A7 (regs guard off) rc=0; A9 (`>`) rc=2.
Record `a8.tsv` = TOTAL repos=2 regs=2 prunable=5: pristine rc=2 `TOTAL prunable=5 but REPO rows sum to 0`; A8 (prunable guard off) rc=0.
Record `b5.tsv` = REPO alpha regs=5 (live 1): pristine `--skip-unrecorded` rc=1 `DRIFT REGS-CHANGED alpha record=5 live=1`; B5 and B6 rc=0 `drift_rows=0`.
```
$ grep -c 'REGS-CHANGED\|PRUNABLE-CHANGED' tests/fixtures/r40-drift-record-branches.py   → 0
$ grep -c 'REGS-CHANGED\|PRUNABLE-CHANGED' tests/fixtures/r39-drift-record-rules.py      → 0
```

### Run 6 — what the invalid-UTF-8 arm actually sees (repo name `al\xffpha`, flag set)
```
pristine: DRIFT\tABSENT\tal\xef\xbf\xbdpha\trecorded regs=1          (U+FFFD)
C4 bs:    DRIFT\tABSENT\tal\\xffpha\trecorded regs=1                  (literal backslash escape)
C5 latin: DRIFT\tABSENT\tal\xc3\xbfpha\trecorded regs=1               (ÿ, U+00FF)
C3 surr:  (empty stdout; fixture's own subprocess decode raises UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff)
```
The fixture's only assertion on this arm is the token `ABSENT` and rc 1 (`tests/fixtures/r40-drift-record-branches.py:114-116`).

## Pairs (what each arm asserts, file:line)

| Branch | Arm A (branch does something) | Arm B (branch does not) | Inversion killed? | Pair isolates the branch? |
|---|---|---|---|---|
| Multiple TOTAL | `total-conflicting-second` rc2 (`fixture:104-106`) | `total-duplicate-identical` rc0 (`fixture:102-103`) | M15, A2 yes | **No** — conflicting arm has repos=1 (`fixture:105`), refused by the independent repos guard (`tool:170-171`) regardless of keep-first/last; A3 passes both arms |
| `--skip-unrecorded` | `unrecorded-without-flag` rc1 UNRECORDED (`fixture:112-113`) | `skip-unrecorded-suppresses` rc0 (`fixture:110-111`) | B1, B2, B3 yes | Yes for UNRECORDED; no case covers flag effects on REGS/PRUNABLE drift (B5, B6) |
| Invalid UTF-8 | `invalid-utf8-in-repo-name` rc1 ABSENT (`fixture:114-116`) | `invalid-utf8-in-comment` rc0 (`fixture:117-120`) | M17 (ignore), strict, U+FFFD-strip, comment-refuse yes | **No** for replace semantics — any non-fatal decoder yielding a non-matching name passes both arms (C4, C5, C6); U+FFFD never asserted |

## Survivors of the whole candidate fixture (single-defect, all predicted and reproduced)

- A3 `tool:164` keep first TOTAL only when repos equal — accepts a same-repos conflicting TOTAL (rc0, should be rc2).
- A5 `tool:170` `!=`→`<` — accepts repos > REPO rows (no case has repos > rows).
- A7 `tool:172-173` regs consistency guard removed; A8 `tool:174-178` prunable guard removed; A9 `tool:172` `!=`→`>` — no case has a TOTAL whose repos is correct but regs/prunable is wrong.
- B5 `tool:366-367` REGS-CHANGED dropped; B6 same row suppressed under `--skip-unrecorded` — no REGS-CHANGED case anywhere in r39 or r40.
- C3 `tool:147` `replace`→`surrogateescape` — fixture crashes (UnicodeDecodeError), no own SUMMARY; the counter's kill rule therefore scores it survived although something is detected.
- C4 `tool:147` `replace`→`backslashreplace`; C5 `replace`→`latin-1`; C6 `replace`→`ascii`+`replace` — pass 8/8.

None of these is one of the four declared M15–M18, so the landed counter's declared result (4/4 killed, base 0) is unaffected. They are reported as the pairing and coverage gap the task asked for.

## Reproduction

Everything above is reproducible from the committed bytes with:
```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
S=$(mktemp -d /fast/scratch/hyaku/souji-r40/w2/R40w2critic08.XXXX) && mkdir -p "$S/counter" "$S/attack"
env -i PATH=/usr/local/bin:/usr/bin:/bin TMPDIR="$S" python3 -B \
  .ufo/waves/round-40/w2/R40w2critic08-attack.py --root "$PWD" \
  --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --scratch "$S/attack"
```

## Tools, installs, scratch

- Installs: none. No pacman; no tool installed or updated. Interpreter: Python 3.14.8; git 2.56.0 (already present).
- Writes: only `.ufo/waves/round-40/w2/R40w2critic08.md` and the scratch file `.ufo/waves/round-40/w2/R40w2critic08-attack.py`.
  No lane file, counter, fixture, preregistration, SCORECARD.md, LOG.md or corpus file was edited; `git status` shows no change under `tests/`, `tools/`, or the r40 counter/prereg.
- Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2critic08/` **removed** (verified: `No such file or directory`).
- No git mutation was run; no commit, push or jj command.
