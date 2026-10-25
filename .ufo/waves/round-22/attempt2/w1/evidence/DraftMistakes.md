# DraftMistakes — evidence log

Seat: L1Souji22.DraftMistakes (scribe). Item: draft the attempt-2 `## Mistakes`
block. Lane root: /home/vgpnk/Projects/shokunin/souji-shokunin.
Read-only lane; this file and the seat report are the only writes. No tool was
installed. Nothing under corpus/, .ufo/state, MANIFEST.json or any sibling repo
was written; /home/vgpnk/Projects/shokuknow was read only.

Preregistration read before any verdict (`.ufo/waves/round-22/attempt2/preregistration.txt`),
frozen fields `class · evidence pointer · captured-by · fix`; "a fix counts only
when a fixture shows it can fail".

## E1 — item 1 pointer: the non-author spot-check

Read `corpus/lessons/round-22-verifier-spotcheck.md` (author Main, date
2026-10-21; base `41553adb…`, filed revision `e675f20a…`). Verbatim spans used:

- "**Not admitted; rejected-honest-stop.** Retain the finite recorded calibration
  gains, but original independent-oracle/strict-adequacy proof is not complete."
- "A positive counter, author-selected mutant saturation or retained VOID PASS
  cannot replace that missing authority."
- "Formal six-VOID accounting is not an exhaustive scope certificate: further
  same-class scratch-writing reviews, including the credited RevProbe258
  reproduction basis, were identified in outside metadata review. Its
  "compliant" label is not adopted."
- "The report's own strict-full-adequacy warning therefore remains controlling."

Governing criteria, read at `corpus/QUALITY.md`:

- `:7-8` fleet floor quoted in the file: "a count carries its command, a negative
  its sweep, a quote its location, an index row is a claim" (CORPUS.md rules).
- `:29` Q5: "A verdict table the lane publishes is re-derived by an independent
  blind seat before admission; a disagreement is adjudicated with its cause
  named, never by majority; a critical role has a second seat."
- `:65` Q26: "A confirmed read-only violation voids the findings that used its
  output; an executing or writing violation voids the seat's evidence."
- `:122` Q53: "State adequacy "of N listed mutants", never exhaustive."
- `:34` Q10 and `:41` Q17 (used in M15): Q17 "A claimed committed fixture or
  evidence fragment must resolve to a contained regular, non-symlink file at the
  measured revision; prose naming a fixture is not a substitute for the file."

No command execution is possible against a spot-check judgment; this pointer is
read evidence, not an executed check.

## E2 — item 2 pointer: register slice and citation-class rows

Register (read-only): `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`
`git -C /home/vgpnk/Projects/shokuknow rev-parse HEAD` → `8b94c5c12c0521e4cd9ed8e5b6939afd8518c715`;
`git ls-files --error-unmatch …` → TRACKED; last commit touching it `d4ab45f2`.

Frozen lane slice read from the committed derived file
`census/round-22/attempt2/quarantine-slice` → 8 ids: S114, S123, S124, S126,
S131, S133, S138, S118.

Rows read (register line → row): `:171` souji round1 S114; `:172` souji round2
S123; `:173` souji round2 S124; `:175` souji round2 S131; `:176` souji round3
S133; also `:174` S126, `:177` S138, `:361` S118. All carry `payload-absent`
except `:361`, which carries "the cited source could not be fetched, so no quote
was checked".

Citation-class rows (claimed quote's true home is a man page, cited against a
local probe artifact):

| register line | id | cited source (register) | claimed quote |
|---|---|---|---|
| :172 | S123 | `lanes/souji/round2/evidence/r23-trigger-prune.out` | `git worktree prune [-n] [-v] [--expire <expire>]` |
| :173 | S124 | `lanes/souji/round2/evidence/noreplace-probe.out` | second fragment `Don't overwrite newpath of the rename. Return an error if newpath already exists.` |
| :175 | S131 | `lanes/souji/round2/evidence/r23-worktree-census.out` | `-n, --dry-run With prune, do not remove anything; just report what it would remove.` |
| :176 | S133 | `lanes/souji/round3/evidence/r24-renameat2-probe.out` | `RENAME_NOREPLACE Don't overwrite newpath of the rename.` |

Executed: the quotes' actual homes.

```
$ export MANWIDTH=80; man git-worktree | col -b | sed -n '10,14p'
     git worktree lock [--reason <string>] <worktree>
     git worktree move <worktree> <new-path>
     git worktree prune [-n] [-v] [--expire <expire>]        <- line 12
     git worktree remove [-f] <worktree>
     git worktree repair [<path>...]
```

```
$ man git-worktree | col -b | sed -n '214,222p'
 214  Keep the worktree locked after creation. This is the equivalent of git
 215  worktree lock after git worktree add, but without a race condition.
 216
 217      -n, --dry-run
 218  With prune, do not remove anything; just report what it would remove.
 ...
```

```
$ man 2 rename | col -b | sed -n '88,96p'
 91      RENAME_NOREPLACE
 92  Don't  overwrite newpath of the rename.  Return an error if newpath
 93  already exists.
```

Executed: the quoted prose is absent from the artifacts the register cites
(all four artifacts exist; `grep -cF` counts below).

```
$ cd /home/vgpnk/Projects/shokuknow
lanes/souji/round2/evidence/r23-trigger-prune.out :: [git worktree prune] -> 0
lanes/souji/round2/evidence/r23-worktree-census.out :: [dry-run] -> 3
lanes/souji/round2/evidence/r23-worktree-census.out :: [do not remove anything] -> 0
lanes/souji/round3/evidence/r24-renameat2-probe.out :: [Don't overwrite newpath] -> 0
lanes/souji/round2/evidence/noreplace-probe.out :: [Don't overwrite newpath] -> 0
```

The three `dry-run` hits in `r23-worktree-census.out` are command labels
(`:3` "only `worktree list` and `worktree prune --dry-run` were used",
`:20` "--- prune census (dry-run only) ---", `:27` "prune --dry-run --expire
now: (no output — none prunable)"), not the quoted prose sentence.

Lane's own slice verdicts read: `census/round-22/attempt2/slice-verdicts.tsv`
(S123 `refused`; S124/S131/S133 `accepted` with the correction stated; S114
`accepted`; S126 `present`; S138 `accepted`; S118 `unverifiable`).

## E3 — item 3 pointer: SCORECARD asserted evidence at the frozen base

Base revision `4edb25dfe262515d0da63224bbba71e02e36cba5`; observed lane HEAD
`3216c1998fe04d7e23793ffd4e135bd37c3a11f4`.

```
$ git cat-file -e 4edb25d:AXES.md                                   -> ABSENT
$ git cat-file -e 4edb25d:reason-after.txt                          -> ABSENT
$ git cat-file -e 4edb25d:.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md -> ABSENT
$ git cat-file -e 4edb25d:census/round-21/reason-after.txt          -> PRESENT
$ ls -d .ufo/scopes                                                 -> No such file or directory
```

Before receipt (read): `census/round-22/attempt2/declared-evidence-before.tsv`
(57 lines; tracked at HEAD, added by `a211e4d`). Mismatch rows:

```
3  AXES.md                                                        A  mismatch:path-absent  not in tree at 4edb25d…
63 reason-after.txt                                               A  mismatch:path-absent  not in tree at 4edb25d…
77 .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md          A  mismatch:path-absent  not in tree at 4edb25d…
assertions=56 resolved=53 skipped=33 mismatches=3
```

Reproduced by this seat (same command as the preregistered C1 counter):

```
$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
    --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format counts
assertions=56 resolved=53 skipped=33 mismatches=3      (exit 1)

$ python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md \
    --rev HEAD --format counts
assertions=56 resolved=56 skipped=36 mismatches=0      (exit 0)

$ python3 -B tools/souji-declared-evidence.py --selftest
PASS fixture1 all-good -> 0 [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture2 absent path -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture3 dangling rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture4 wrong digest -> mismatch [assertions=3 resolved=2 skipped=0 mismatches=1]
PASS fixture5 path only at other rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture6 correct digest -> resolved [assertions=3 resolved=3 skipped=0 mismatches=0]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
PASS fixture7 command span -> skipped, not asserted [assertions=0 resolved=0 skipped=1 mismatches=0]
selftest=8/8 (exit 0)
```

Repair already landed at HEAD (`git diff 4edb25d HEAD -- SCORECARD.md`, 15
insertions / 6 deletions): line 3 token `AXES.md` → absolute fleet path
`/home/vgpnk/Projects/shokunin/AXES.md`; bare `reason-after.txt` →
`census/round-21/reason-after.txt`; the scope-file sentence now reads "that file
is absent (checked 2026-10-25, ls -> "No such file or directory"), so the finding
is not retrievable from committed bytes and is no longer presented as a banked
artifact." (+3 skipped at HEAD = the three tokens that stopped being asserted).

### Audit-seat TSVs (exact paths and status at read)

| path | status | content |
|---|---|---|
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap1.tsv` | READ | header `measured_revision=4edb25dfe…`; slice = base lines 45-49; 33 rows, `mismatches=0` |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap2.tsv` | READ | base lines 50-54; 25 rows, 0 mismatches |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap5.tsv` | READ — revision conflict | 22 rows, 0 mismatches, but measured on the repaired table (see E4) |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditReadme.tsv` | READ | 9 `mismatch:unresolved-either-base` rows, all `corpus/README.md` (lines 8, 90, 92, 217×2, 287, 311, 383×2) |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditAxes.tsv` | PENDING-SEAT | absent at read |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap3.tsv` | PENDING-SEAT | absent at read |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap4.tsv` | PENDING-SEAT | absent at read |
| `.ufo/waves/round-22/attempt2/w1/evidence/AuditSkillShonen.tsv` | PENDING-SEAT | absent at read |

(Also present and read: `RevScope.tsv`, `ScoutIdResolve.tsv` — 0 mismatch rows;
not SCORECARD audits.)

## E4 — measured-revision conflict in AuditCap5.tsv (finding, not a verdict)

`AuditCap5.tsv` reports `SCORECARD.md 74 tools/souji-declared-evidence.py A
resolved` and `SCORECARD.md 74 census/round-22/attempt2/declared-evidence-before.tsv
A resolved`, over lines 70-74.

```
$ git cat-file -e 4edb25d:tools/souji-declared-evidence.py   -> ABSENT
$ git cat-file -e HEAD:tools/souji-declared-evidence.py      -> PRESENT
$ git show 4edb25d:SCORECARD.md | sed -n '70,74p'            -> "## Planned" prose
$ sed -n '70,74p' SCORECARD.md                               -> capability rows 21-25
$ git merge-base --is-ancestor a211e4d 4edb25d               -> non-zero (base is ancestor of a211e4d)
$ git show 4edb25d:SCORECARD.md | sed -n '63p'               -> "| process-residue observations (r18; r21 synthetic repair) …"
```

The TSV has no `measured_revision` header and its line anchors and tokens match
HEAD, not the frozen base in its own prompt; base row 25 (line 63, the
`reason-after.txt` mismatch) is outside its reported slice. Its `mismatches=0`
therefore cannot corroborate the base state. Recorded as a seat-calibration
hazard, not as proof of a second defect.

## E5 — fail-ability of the three fixes (executed)

```
$ python3 -B tools/souji-gate-check.py --selftest
PASS fixture good -> ok                      [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail                 [fail=1]
PASS fixture long-quote -> fail              [fail=2]
PASS fixture quote-absent -> fail            [fail=2]
PASS fixture dangling-source -> fail         [fail=1]
PASS fixture no-reject -> fail               [fail=1]
PASS fixture no-gate -> fail                 [fail=1]
PASS fixture partial-verdicts -> fail        [slice_verdicts=1 slice_total=2 fail=1]
PASS control always-green -> FALSE-GREEN-REJECTED
selftest=9/9 (exit 0)
```

Live counter (preregistered C2 command, read-only):

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0    (exit 0)

$ same command with --slice-verdicts /dev/null
FAIL slice verdict-missing:S114 … S118 (8 lines)
entries=2 ok=2 slice_verdicts=0 slice_total=8 fail=8    (exit 1)
```

The `/dev/null` run is a negative control this seat executed (no file created);
it is not a claim about the historical before state.

## E6 — tool-bytes pin (the worktree copy was being edited by another seat)

`git status --porcelain` at 03:52 showed ` M tools/souji-gate-check.py`
(25 insertions/14 deletions vs HEAD) and ` M SCORECARD.md`. The gate-check
observations in E5 were therefore re-taken from the committed blob, and they are
identical to the worktree runs:

```
$ git show HEAD:tools/souji-gate-check.py | python3 -B - --selftest
... selftest=9/9 (exit 0), same nine fixture lines as E5

$ git show HEAD:tools/souji-gate-check.py | python3 -B - --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0   (exit 0)

$ same with --slice-verdicts /dev/null
entries=2 ok=2 slice_verdicts=0 slice_total=8 fail=8   (exit 1)
```

`tools/souji-declared-evidence.py` was not modified in the worktree
(`git status` does not list it), and that tool reads its declaration from the
revision (`read_declaration` uses `git show` when the file is tracked at `--rev`),
so rows 2-4 of the report's executed table describe committed bytes, not the
dirty worktree.

## E7 — numbering collision in the target file

`corpus/lessons/round-22.md` HEAD blob already contains attempt-2 rows:

```
$ git log --oneline -3 -- corpus/lessons/round-22.md
70af563 round-22: bookkeeping, lesson gates and LOG for attempt 2
fe7590b round-22: retain terminal reviews and mark strict adequacy unproven
473e98a round-22: resolve inherited adequacy falsifiers with environment-bound witnesses
$ git show HEAD:corpus/lessons/round-22.md | grep -n 'M13\|M16'
288:- **M13 — self-assessment overreach by the lane's own author.**
317:- **M16 — campaign row ids are not lane row ids.**
```

So M13–M16 are already used; the frozen "number from M13" instruction predates
that landing. Differences between those rows and this seat's verified block:
the landed M13 records captured-by as `none` (Q5/Q26/Q53 exist and apply), and
the landed M14 says "7 of 8 rows" (7 of 8 rows are `payload-absent`, but the
man-page-cited-against-a-local-artifact class is 3 rows plus one S124 fragment).

## Limits

- 4 of the 8 named audit TSVs were unread (PENDING-SEAT) at write time;
  `AuditCap5.tsv`'s measured revision is not the frozen base.
- The register lives in a different, read-only repository; this seat did not
  modify it and derives no admission from it.
- No web page was fetched by this seat; web-sourced rows (S114, S126, S138) are
  taken from the lane verdict TSV and the register, not re-verified here.
- Nothing in this log was produced by a subagent; no lane or fleet tool was
  installed or upgraded.
