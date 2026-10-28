# R40w2revenger03 — r39 C3 fixture reverse-engineering and r40 duplicate map

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Base: 0242085909fb6a4ee041c5443d76316ac6d59d4b (r39 tip)
Landed instrument commit: 128e412b0ced3c243dc27c3dd3332054a611bc2e
HEAD at run time: 549d9ec53a1f5932337ff14438fcd22b0621828d
Tool under test (unchanged since base): tools/souji-worktree-drift.py (`git diff --stat 0242085… HEAD -- tools/…` printed nothing)
C3 bytes between 128e412 and HEAD: only census/round-40/c3-counter.py changed (score() FAIL-line filter, lines 115-117); both fixtures byte-identical.

## Verdict

- **FALSIFIED (framing only):** the r40 fixture docstring and the r40 counter narrative claim the three record branches were "uncovered by every committed fixture" and that the invalid-UTF-8 cases show "an undecodable byte becomes U+FFFD". Both are false as stated: two of the r40 cases re-assert behaviour already asserted by r36/r37/r38, and no committed fixture asserts the U+FFFD substitution (a `backslashreplace` mutant survives all five committed drift fixtures).
- **SAFE (declared predicate):** the r40 counter at HEAD reproduces `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8`. The declared M15-M18 kill set holds.
- Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2revenger03/` removed at end (see Cleanup).

## Axes attacked

1. Behaviour actually asserted by each r39 case (from tool code, not case names).
2. Which r40 cases duplicate an r39 case (and which duplicate committed r36-r38 cases or other r40 cases).
3. Whether the r40 C3 kill set is complete for the branches it names (undeclared mutants).
4. Whether the counter's scoring contract is sound (crash handling).

## Commands run and real output

Every command ran with absolute paths, `python3 -B`, explicit `TMPDIR` and `--work` under the scratch dir. Nothing was written under the lane.

### 1. Fixtures against the landed tool

```
$ TMPDIR=$S/r39run python3 -B tests/fixtures/r39-drift-record-rules.py --tool $L/tools/souji-worktree-drift.py --work $S/r39run
case-good=PASS
case-trailing-space=PASS
case-total-before-rows=PASS
case-crlf=PASS
case-outside-root=PASS
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=7 fail=0            rc=0

$ TMPDIR=$S/r40run python3 -B tests/fixtures/r40-drift-record-branches.py --tool $L/tools/souji-worktree-drift.py --work $S/r40run
case-good=PASS
case-total-duplicate-identical=PASS
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0            rc=0
```

### 2. Per-case observed tool output (fixture `run_cases` imported and called directly, same tool)

```
$ TMPDIR=$S/observe python3 -B $S/observe/observe.py     # imports each fixture, calls run_cases(tool, $S/observe)
##### r39
good                 ok=True rc=0 want=0  out='SUMMARY ... record_repos=2 record_regs=2 re...'
trailing-space       ok=True rc=2 want=2  out='REFUSAL RECORD-MALFORMED: line 1 does not match the census schema '
total-before-rows    ok=True rc=0 want=0  out='SUMMARY ... record_repos=2 ...'
crlf                 ok=True rc=0         out='SUMMARY ... record_repos=2 ...'
outside-root         ok=True rc=2 want=2  out='REFUSAL RECORD-OUTSIDE-ROOT: ../escape resolves outside .../fleet '
indented-comment     ok=True rc=2 want=2  out='REFUSAL RECORD-MALFORMED: line 1 does not match the census schema '
comments-total-only  ok=True rc=2 want=2  out='REFUSAL RECORD-EMPTY: no REPO rows in .../record-c362zcha.tsv '
##### r40
good                       ok=True rc=0 want=0  out='SUMMARY ... record_repos=2 ...'
total-duplicate-identical  ok=True rc=0 want=0  out='SUMMARY ... record_repos=2 ...'
total-conflicting-second   ok=True rc=2 want=2  out='REFUSAL RECORD-MALFORMED: TOTAL repos=1 but 2 REPO rows '
total-repos-disagrees      ok=True rc=2 want=2  out='REFUSAL RECORD-MALFORMED: TOTAL repos=1 but 2 REPO rows '
skip-unrecorded-suppresses ok=True rc=0 want=0  out='SUMMARY ... record_repos=2 ...'
unrecorded-without-flag    ok=True rc=1 want=1  out='DRIFT\tUNRECORDED\tgamma\tlive regs=1 prunable=0 SUMMARY ...'
invalid-utf8-in-repo-name  ok=True rc=1 want=1  out='DRIFT\tABSENT\tal�pha\trecorded regs=1 SUMMARY ...'
invalid-utf8-in-comment    ok=True rc=0 want=0  out='SUMMARY ... record_repos=2 ...'
```

Note `al�pha` is the U+FFFD (bytes EF BF BD) produced by the tool; confirmed with `od -c` on a direct run: `D R I F T \t A B S E N T \t a l 357 277 275 p h a`.

### 3. The r40 counter at HEAD and at the landed rev

```
$ TMPDIR=$S/c3run/<rev> python3 -B census/round-40/c3-counter.py --root $L --rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
    --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/c3run/<rev> \
    --tool tools/souji-worktree-drift.py --fixture tests/fixtures/r40-drift-record-branches.py --base-fixture tests/fixtures/r39-drift-record-rules.py
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
rc=0
```
The 128e412 rev gives the identical SUMMARY line and the same per-mutant failing cases.

### 4. Undeclared mutants (probe harness `$S/probe/probe.py`, anchors counted with `source.count(old) == 1`, mutant written to scratch only)

```
ANCHOR P1-no-TOTAL-regs-check count=1       # line 172-173: `if total["regs"] != ...` -> `if False:`
  r39 rc=0 SUMMARY cases=7 pass=7 fail=0
  r40 rc=0 SUMMARY cases=8 pass=8 fail=0
ANCHOR P2-no-TOTAL-prunable-check count=1   # line 174-178
  r39 rc=0 SUMMARY cases=7 pass=7 fail=0
  r40 rc=0 SUMMARY cases=8 pass=8 fail=0
ANCHOR P3-decode-surrogateescape count=1    # line 147 replace -> surrogateescape
  r39 rc=0 SUMMARY cases=7 pass=7 fail=0
  r40 rc=1 traceback=True  (no SUMMARY line; fixture subprocess.text decode raised UnicodeDecodeError 0xff)
ANCHOR P4-decode-backslashreplace count=1   # line 147 replace -> backslashreplace
  r39 rc=0 SUMMARY cases=7 pass=7 fail=0
  r40 rc=0 SUMMARY cases=8 pass=8 fail=0
```

Direct tool runs on the same probes (fleet alpha/beta/gamma, each a `git init -q -b main` fixture repo, toplevel checked):

```
$ python3 -B $L/tools/souji-worktree-drift.py --root $F/fleet --record rec-regs9.tsv --skip-unrecorded    # TOTAL regs=9, rows sum 2
REFUSAL RECORD-MALFORMED: TOTAL regs=9 but REPO rows sum to 2          rc=2
$ python3 -B $P1/tool.py ...   (P1 mutant)
SUMMARY ... record_repos=2 record_regs=2 ... drift_rows=0 ...          rc=0
$ python3 -B $L/tools/souji-worktree-drift.py --root $F/fleet --record rec-prun9.tsv --skip-unrecorded    # TOTAL prunable=9
REFUSAL RECORD-MALFORMED: TOTAL prunable=9 but REPO rows sum to 0     rc=2
$ python3 -B $P2/tool.py ...   (P2 mutant)  -> rc=0
```

P1 and P2 survive the r39 and r40 fixtures, but are killed by committed r38 (see section 6). P3 crashes the r40 fixture. P4 survives every committed drift fixture (section 5).

### 5. P4 survives all committed drift fixtures

```
$ python3 -B tests/fixtures/r36-worktree-drift.py     --tool $P4/tool.py --work $S/prior/mut/...  -> SUMMARY cases=12 pass=12 fail=0   rc=0
$ python3 -B tests/fixtures/r37-drift-discrimination.py --tool $P4/tool.py ...                  -> SUMMARY cases=6 pass=6 fail=0     rc=0
$ python3 -B tests/fixtures/r38-drift-record.py      --tool $P4/tool.py ...                     -> SUMMARY cases=10 pass=10 fail=0   rc=0
$ python3 -B tests/fixtures/r39-drift-record-rules.py --tool $P4/tool.py ...                    -> SUMMARY cases=7 pass=7 fail=0     rc=0
$ python3 -B tests/fixtures/r40-drift-record-branches.py --tool $P4/tool.py ...                 -> SUMMARY cases=8 pass=8 fail=0     rc=0
```
Direct run: `DRIFT\tABSENT\tal\xffpha\trecorded regs=1 ...` (backslash text) versus the landed `DRIFT\tABSENT\tal\357\277\275pha` (U+FFFD). Same rc 1, same `ABSENT` token. The r40 invalid-utf8-in-repo-name case asserts only `["ABSENT"]` (fixture:116), so the replacement character is never checked, although the r40 docstring says it "becomes U+FFFD" (fixture:12-13).

Scoring-contract note: P3's crash makes the counter report `NO-SUMMARY` (counter:109-110) and `killed` requires no crash (counter:118). A mutant that crashes the fixture is therefore scored SURVIVED, even though the fixture did fail. This is a conservative false survivor, not a vacuous pass.

### 6. Prior committed fixtures already cover some r40 "new" branches

```
$ grep for "skip-unrecorded" across tests/ census/round-3*/ tools/  -> only r40 fixture lines 10,17,99,110 and the tool itself
$ grep for two TOTAL rows in one record body across r36-r40 fixtures -> only r40 (fixture:102-106)
$ grep for invalid-UTF-8 record bytes across r36-r39 fixtures       -> none
```

r36 `unrecorded` (tests/fixtures/r36-worktree-drift.py:194-204) asserts `rc == 1 and "UNRECORDED\tgamma"`. r37 `unrecorded-exact` (tests/fixtures/r37-drift-discrimination.py:173-177) asserts `rc == 1 and "UNRECORDED\tgamma\tlive regs=1 prunable=0"`. r38 total-repos/regs/prunable-mismatch (tests/fixtures/r38-drift-record.py:102-110) assert RECORD-MALFORMED for each TOTAL counter.

```
$ python3 -B tests/fixtures/r38-drift-record.py --tool $P1/tool.py   -> case-total-regs-mismatch=FAIL ... SUMMARY cases=10 pass=9 fail=1   rc=1
$ python3 -B tests/fixtures/r38-drift-record.py --tool $P2/tool.py   -> case-total-prunable-mismatch=FAIL ... SUMMARY cases=10 pass=9 fail=1 rc=1
$ python3 -B tests/fixtures/r38-drift-record.py --tool $L/tools/souji-worktree-drift.py -> SUMMARY cases=10 pass=10 fail=0 rc=0
$ python3 -B tests/fixtures/r36-worktree-drift.py --tool $L/... -> SUMMARY cases=12 pass=12 fail=0 rc=0
$ python3 -B tests/fixtures/r37-drift-discrimination.py --tool $L/... -> SUMMARY cases=6 pass=6 fail=0 rc=0
```

## Reverse-engineered r39 C3 cases (behaviour asserted, from tool code)

Tool line references: `tools/souji-worktree-drift.py`. Key lines: ROW regex `$`-anchored 87; TOTAL regex 88; `raw.decode(..."replace")` 147; `raw.splitlines()` 152; skip blank or column-0 `#` 153; ROW match 155; duplicate-name refusal 158-159; TOTAL assignment (last one wins) 162-165; schema refusal 166; RECORD-EMPTY 167-168; TOTAL repos/regs/prunable checks 169-178; outside-root refusal 292-293; UNRECORDED 370-383; exit 0/1 by drift 429; Refusal → rc 2 447.

| r39 case | fixture line | record body | tool path actually exercised | asserted (rc + tokens) |
|---|---|---|---|---|
| good | 88 | ROWS + TOTAL (2 repos) | accept path; no drift in the 2-repo fleet | rc 0; `SUMMARY`, `record_repos=2` |
| trailing-space | 89-91 | `REPO alpha ... prunable=0 ` (space) | fails ROW `$` anchor (87) → schema refusal (166) | rc 2; `RECORD-MALFORMED`, `does not match the census schema` |
| total-before-rows | 92-93 | TOTAL then ROWS | TOTAL check is after the loop (169), so order does not matter | rc 0; `SUMMARY`, `record_repos=2` |
| crlf | 94-104 | CRLF bytes | `splitlines` (152) splits `\r\n`; ROW matches | rc 0 and `record_repos=2` in out (checked in-line, not via run_case) |
| outside-root | 105-107 | `REPO ../escape` | `os.path.realpath` joined under root → commonpath escape (286-293) | rc 2; `RECORD-OUTSIDE-ROOT` |
| indented-comment | 108-109 | `  # indented comment` | `strip()` non-empty and `startswith("#")` is False (153) → schema refusal (166) | rc 2; `RECORD-MALFORMED`, `does not match the census schema` |
| comments-total-only | 110-111 | `# only a comment` + TOTAL | no ROW, so `rows` empty → RECORD-EMPTY (167-168) fires before TOTAL checks | rc 2; `RECORD-EMPTY` |

So the r39 base asserts: accept paths (good, total-before-rows, crlf), three schema refusals (trailing-space, indented-comment, plus the comment-only empty class), one containment refusal (outside-root). It asserts no TOTAL disagreement, no duplicate TOTAL, no UNRECORDED, no `--skip-unrecorded`, and no byte-level decoding behaviour. Its `comments-total-only` case is also just the RECORD-EMPTY path. Several of its cases share a refusal branch (trailing-space and indented-comment both use the schema refusal at tool:166).

## Mapping the r40 cases (fixture: tests/fixtures/r40-drift-record-branches.py)

| r40 case | lines | relation to r39 | relation to committed r36-r38 / r40 | classification |
|---|---|---|---|---|
| good | 100-101 | same record bytes, same rc 0 and `record_repos=2` tokens as r39 `good` (88); adds `--skip-unrecorded` and a third repo `gamma` in the fleet | none | **DUPLICATE of r39 good** (record accept), with a flag arm added |
| total-duplicate-identical | 102-103 | none (every r39 record has one TOTAL) | no committed case has two TOTAL rows | **NEW** (tool 162-165 last-wins, identical values) |
| total-conflicting-second | 104-106 | none | no committed case | **NEW** (first-TOTAL-wins mutant killed, M15) |
| total-repos-disagrees | 107-109 | none | same refusal class as r38 total-repos-mismatch (r38:102-104) | **DUPLICATE of r38 class**; observed output identical to total-conflicting-second |
| skip-unrecorded-suppresses | 110-111 | none | byte-identical invocation to r40 `good` (100-101); only the token list is weaker (`SUMMARY` vs `SUMMARY`+`record_repos=2`) | **INTERNAL DUPLICATE of r40 good** |
| unrecorded-without-flag | 112-113 | none | identical assertion to r36 `unrecorded` (r36:194-204) and r37 `unrecorded-exact` (r37:173-177) | **DUPLICATE of r36/r37** (not new; the docstring's "no committed fixture" is false here) |
| invalid-utf8-in-repo-name | 114-116 | none | no committed invalid-UTF-8 drift case | **NEW**, but asserts only the `ABSENT` token, not U+FFFD |
| invalid-utf8-in-comment | 117-120 | none | no committed invalid-UTF-8 drift case | **NEW** |

Summary:
- Duplicates an **r39** case: 1 of 8 (`good`).
- Duplicates a case in another r40 case: 1 (`skip-unrecorded-suppresses` duplicates `good`).
- Duplicates a committed r36-r38 case: 2 (`unrecorded-without-flag`, `total-repos-disagrees`).
- Genuinely new against every committed fixture: 4 (`total-duplicate-identical`, `total-conflicting-second`, `invalid-utf8-in-repo-name`, `invalid-utf8-in-comment`). The `--skip-unrecorded` arm (the suppression itself, via `good`) is also new, because no committed fixture passes the flag.

Pairing claim (fixture:17-19): for `--skip-unrecorded` the pair (`good` with flag → rc 0; `unrecorded-without-flag` → rc 1) does discriminate an inverted branch. For invalid UTF-8, the pair (name → ABSENT, comment → tolerated) is not an inverted-branch pair: there is no branch on the decode, and P4 survives both arms.

## Counter-level observations

- M15-M18 are the only declared mutants (census/round-40/c3-counter.py:62-68). Each anchor occurs exactly once (the run printed no ANCHOR-COUNT line).
- Declared-set kill attribution: M15 → total-conflicting-second; M16 → good, total-duplicate-identical, skip-unrecorded-suppresses, invalid-utf8-in-comment (M16 makes the flag-less runs see gamma); M17 → invalid-utf8-in-repo-name; M18 → total-repos-disagrees. The base fixture kills none (`base_killed=0`).
- The counter's pristine check requires `cases >= 8` (counter:179). Passing.
- Undeclared survivors on the r40 + r39 pair: P1 (TOTAL regs), P2 (TOTAL prunable), P4 (backslashreplace). P1 and P2 are killed by committed r38, so they are not a committed-suite gap. P4 is a real gap (no committed fixture pins U+FFFD).
- P3 crashes the r40 fixture; counter:115 and :118 score that as survived.

## Divergences from the r40 narrative

1. fixture:4-6 and corpus narrative: "stayed uncovered by every committed fixture" is false for unrecorded-without-flag (r36:194-204, r37:173-177) and total-repos-mismatch class (r38:102-104).
2. fixture:12-13: "an undecodable byte becomes U+FFFD" is not asserted; the name case asserts only `ABSENT` (fixture:116).
3. fixture:17-19: the invalid-UTF-8 "pair" does not discriminate an inverted branch (no such branch).

None of these falsify the declared C3 predicate (counter output above). They do falsify the coverage narrative, and the U+FFFD assertion gap is a real, re-runnable survivor (P4).

## Hygiene

- No edits to counters, fixtures, preregistration, SCORECARD.md, LOG.md, corpus/, or any committed file.
- Only mutating action: creating fixture repos under the scratch dir (`git -C "$D" init`, `rev-parse --show-toplevel` checked before commit; commit identity set via env `fixture@example.invalid` inside the fixture only).
- No installs; tools used: python3 (3.14), git. No pacman.
- Scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2revenger03/` removed after this report was written (see yield).
