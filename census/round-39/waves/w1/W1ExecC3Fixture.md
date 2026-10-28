# W1ExecC3Fixture — exercise `r39-drift-record-rules.py` on its own

Seat: executor (leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
lane base `ed30b7f5b77939c9073348d810730bc4f355708d`). Measurement revision: lane `HEAD =
c0b007b42af9a03d7edc32533bcac27484223997`.
Bytes exercised (sha256, working tree == `HEAD`, verified below):

```
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d  tests/fixtures/r39-drift-record-rules.py
4e07f1df2a61c2bffdc1108fc97fe86feb6c6cc96bfdfa9c14415736877018be  tools/souji-worktree-drift.py
```

which are exactly the counter's `fixture_sha=567c37a679f5` / `tool_sha=4e07f1df2a61` (see §5).

Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecC3Fixture` (left clean at exit — §Scratch).
No lane file was created or modified by this seat except this report. No install/upgrade was needed;
no git/jj mutation was run (only `log`, `show`, `status --porcelain`, `rev-parse` reads).

## 1. The frozen fixture, run as specified — 7/7 PASS

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture
python3 -B tests/fixtures/r39-drift-record-rules.py --tool tools/souji-worktree-drift.py \
  --work /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture
```

Observed (exit 0):

```
case-good=PASS
case-trailing-space=PASS
case-total-before-rows=PASS
case-crlf=PASS
case-outside-root=PASS
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=7 fail=0
```

Byte provenance (working tree vs committed, same revision):

```
sha256sum tests/fixtures/r39-drift-record-rules.py  → 567c37a6…432a4d
git show HEAD:tests/fixtures/r39-drift-record-rules.py | sha256sum → 567c37a6…432a4d
sha256sum tools/souji-worktree-drift.py → 4e07f1df…7018be
git show HEAD:tools/souji-worktree-drift.py | sha256sum → 4e07f1df…7018be
git status --porcelain tests/fixtures/r39-drift-record-rules.py tools/souji-worktree-drift.py  → (empty)
```

Verdict: **PASS** — 7 cases (>= the frozen `cases>=6` floor), `pass=7 fail=0`, exit 0, fixture bytes
identical to committed bytes.

## 2. Usage/refusal arms of the fixture itself — PASS

```
python3 -B tests/fixtures/r39-drift-record-rules.py --tool tools/souji-worktree-drift.py \
  --work /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/no-such-dir
→ usage: --work must name an existing directory (/fast/…/no-such-dir)
→ RC=2

python3 -B tests/fixtures/r39-drift-record-rules.py --tool /nonexistent-tool \
  --work /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture
→ usage: unreadable tool /nonexistent-tool
→ RC=2
```

Verdict: **PASS** — both documented exit-2 usage arms hold. The fixture also cleans up after itself:
after the run in §1 no `souji-r39-record.*` directory remains under `--work` (listing in §Scratch
shows only my own files).

## 3. Every case replayed by hand against the tool (record bytes → tool output)

Manual fleet, built with the same harness env the fixture uses (`GIT_CONFIG_NOSYSTEM=1`,
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, fixture author/committer):

```
toplevel-alpha=/fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/hand/fleet-root/fleet/alpha
toplevel-beta=/fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/hand/fleet-root/fleet/beta
toplevel-fleetroot=fatal: not a git repository (or any parent up to mount point /)
```

Each record was written with `printf` under
`/fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/hand/fleet-root/` (the parent of `--root`, exactly
where the fixture's `mkstemp(dir=root)` puts it) and invoked as

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py \
  --root /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/hand/fleet-root/fleet \
  --record <record> --timeout 30
```

Record bytes below are `od -An -c` of the file actually fed to the tool (`\t`, `\n`, `\r`, and the
one trailing `0x20` are literal in the dump).

### 3.1 `good`

```
   R E P O \t a l p h a \t r e g s = 1 \t p r u n a b l e = 0 \n
   R E P O \t b e t a  \t r e g s = 1 \t p r u n a b l e = 0 \n
   T O T A L \t r e p o s = 2 \t r e g s = 2 \t p r u n a b l e = 0 \n

SUMMARY record=…/r-good.tsv record_repos=2 record_regs=2 record_prunable=0 live_repos=2 live_regs=2 live_prunable=0 drift_rows=0 unreachable=0
rc=0
```

Verdict **PASS, right reason**: rc 0 with `record_repos=2` *and* `live_repos=2 drift_rows=0` — the
two rows named two real worktrees the tool measured (`alpha`, `beta` above are their `rev-parse
--show-toplevel`). Not a vacuous pass: `unreachable=0` means both measurements ran.

### 3.2 `trailing-space`

```
   R E P O \t a l p h a \t r e g s = 1 \t p r u n a b l e = 0 ␠ \n      ← 0x20 before \n
   R E P O \t b e t a  \t r e g s = 1 \t p r u n a b l e = 0 \n
   T O T A L \t r e p o s = 2 \t r e g s = 2 \t p r u n a b l e = 0 \n

REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
rc=2
```

Verdict **PASS, right reason**: the refusal names **line 1** — the only line carrying the trailing
space — with the schema class, not a TOTAL disagreement or a containment refusal. The record is
otherwise valid (`alpha`/`beta` exist, TOTAL sums agree), so nothing else could refuse it first.

### 3.3 `total-before-rows`

```
   T O T A L \t r e p o s = 2 \t r e g s = 2 \t p r u n a b l e = 0 \n
   R E P O \t a l p h a \t r e g s = 1 \t p r u n a b l e = 0 \n
   R E P O \t b e t a  \t r e g s = 1 \t p r u n a b l e = 0 \n

SUMMARY record=…/r-total-before-rows.tsv record_repos=2 record_regs=2 record_prunable=0 live_repos=2 live_regs=2 live_prunable=0 drift_rows=0 unreachable=0
rc=0
```

Verdict **PASS, right reason**: TOTAL before the REPO rows is accepted, and TOTAL is *still
validated* (control in §4.5: the same order with `repos=3` is refused). So the case proves ordering
leniency without proving TOTAL-ignoring.

### 3.4 `crlf`

```
   R E P O \t a l p h a \t r e g s = 1 \t p r u n a b l e = 0 \r \n
   R E P O \t b e t a  \t r e g s = 1 \t p r u n a b l e = 0 \r \n
   T O T A L \t r e p o s = 2 \t r e g s = 2 \t p r u n a b l e = 0 \r \n

SUMMARY record=…/r-crlf.tsv record_repos=2 record_regs=2 record_prunable=0 live_repos=2 live_regs=2 live_prunable=0 drift_rows=0 unreachable=0
rc=0
```

Verdict **PASS, right reason**: the bytes really are `\r\n`, and the run is accepted with both repos
measured. If `\r` leaked into the names or the schema, the outcome would be rc 2 (schema) or rc 1
(`ABSENT`), not rc 0 — measured under M12 in §5.

### 3.5 `outside-root`

```
   R E P O \t . . / e s c a p e \t r e g s = 1 \t p r u n a b l e = 0 \n

REFUSAL RECORD-OUTSIDE-ROOT: ../escape resolves outside /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/hand/fleet-root/fleet
rc=2
```

Verdict **PASS, right reason**: the refusal names the escaping row and the resolved root. Control in
§4.3 shows the identical record with an in-root name is *not* rc 2 (it is rc 1 `ABSENT`), so the rc-2
class is keyed to the escape, not to any row failure.

### 3.6 `indented-comment`

```
   ␠ ␠ # ␠ i n d e n t e d ␠ c o m m e n t \n       ← two leading 0x20
   R E P O \t a l p h a \t r e g s = 1 \t p r u n a b l e = 0 \n
   R E P O \t b e t a  \t r e g s = 1 \t p r u n a b l e = 0 \n
   T O T A L \t r e p o s = 2 \t r e g s = 2 \t p r u n a b l e = 0 \n

REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
rc=2
```

Verdict **PASS, right reason**: line 1 is the indented comment; control in §4.4 shows the same line
unindented is rc 0. `line.startswith("#")` is what makes the indentation fatal, and the case is the
only assertion on it.

### 3.7 `comments-total-only`

```
   # ␠ o n l y ␠ a ␠ c o m m e n t \n
   T O T A L \t r e p o s = 2 \t r e g s = 2 \t p r u n a b l e = 0 \n

REFUSAL RECORD-EMPTY: no REPO rows in /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture/hand/fleet-root/r-comments-total-only.tsv
rc=2
```

Verdict **PASS, right reason** for the named rule ("a record whose only non-comment line is TOTAL is
RECORD-EMPTY"): a TOTAL line is not counted as a row, and `RECORD-EMPTY` is raised. Caveat recorded:
`RECORD-EMPTY` is raised *before* the TOTAL consistency checks, so this case alone cannot tell
"TOTAL-only is empty" from "TOTAL is ignored" — §3.3/§4.5 covers that other half. Also note the r38
fixture already had a *comment-only* empty case (`empty-record`, `# only a comment`) and a
`comments-and-blanks` case; the TOTAL-present variant is the new one.

## 4. Causal controls — each case's stated defect is the cause

Each control keeps the case's shape and removes/swaps only the defect:

### 4.1 trailing space removed → rc 0

```
   R E P O \t a l p h a \t r e g s = 1 \t p r u n a b l e = 0 \n   (no 0x20)
   … TOTAL …
SUMMARY record=…/c-trailing-space-no-trailing.tsv record_repos=2 … drift_rows=0 unreachable=0
rc=0
```

### 4.2 CRLF chopped to LF → rc 0

```
SUMMARY record=…/c-chop-crlf-to-lf.tsv record_repos=2 … drift_rows=0 unreachable=0
rc=0
```

### 4.3 `escape` (in-root, absent) instead of `../escape` → rc 1, never rc 2

```
DRIFT	ABSENT	escape	recorded regs=1
DRIFT	UNRECORDED	alpha	live regs=1 prunable=0
DRIFT	UNRECORDED	beta	live regs=1 prunable=0
SUMMARY record=…/c-outside-root-inside.tsv record_repos=1 record_regs=1 record_prunable=0 live_repos=0 live_regs=0 live_prunable=0 drift_rows=3 unreachable=0
rc=1
```

### 4.4 indented comment unindented → rc 0

```
SUMMARY record=…/c-indented-unindented.tsv record_repos=2 … drift_rows=0 unreachable=0
rc=0
```

### 4.5 comment + real rows (instead of comment + TOTAL only) → rc 0; TOTAL-first with `repos=3` → refused

```
SUMMARY record=…/c-comments-with-rows.tsv record_repos=2 … drift_rows=0 unreachable=0
rc=0

REFUSAL RECORD-MALFORMED: TOTAL repos=3 but 2 REPO rows
rc=2
```

Verdict: **PASS** — every case's outcome flips when its own defect is removed, and TOTAL validation
is live in the TOTAL-first position (so §3.3 is not a "TOTAL ignored" pass).

## 5. Wrong-reason probes

### 5.1 Degenerate stubs cannot satisfy the fixture

`stub-always-refuse.py` prints all four refusal class strings (`RECORD-MALFORMED … does not match the
census schema`, `RECORD-OUTSIDE-ROOT`, `RECORD-EMPTY`) plus a SUMMARY line and exits 2;
`stub-always-accept.py` prints the exact pristine SUMMARY line and exits 0.

```
python3 -B tests/fixtures/r39-drift-record-rules.py --tool <stub-always-refuse.py> --work <scratch>
case-good=FAIL rc=2 want=0 …
case-trailing-space=PASS
case-total-before-rows=FAIL rc=2 want=0 …
case-crlf=FAIL rc=2 …
case-outside-root=PASS
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=4 fail=3
rc=1

python3 -B tests/fixtures/r39-drift-record-rules.py --tool <stub-always-accept.py> --work <scratch>
case-good=PASS
case-trailing-space=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema']
case-total-before-rows=PASS
case-crlf=PASS
case-outside-root=FAIL rc=0 want=2 missing=['RECORD-OUTSIDE-ROOT']
case-indented-comment=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema']
case-comments-total-only=FAIL rc=0 want=2 missing=['RECORD-EMPTY']
SUMMARY cases=7 pass=3 fail=4
rc=1
```

Verdict: **PASS (discrimination)** — no single degenerate stance reaches 7/7. **Named fragility**:
the four refusal cases are individually satisfiable by a tool that refuses everything while printing
all class strings (`pass=4 fail=3` above); the fixture relies on its three rc-0 cases to block that
stub. `run_case` also checks only `rc == want_rc` and token *presence* — it never checks that the
refused line number or that no other class appeared. That is safe for M11–M14 (each mutant returns
rc 0 on its case) but it is why a blanket-refusal stub gets 4/7 rather than 0/7.

### 5.2 Independent 4-mutant arm: all four killed, base fixture kills none

Four single-defect copies of the lane tool in scratch (one documented rule each), scored by the r39
fixture and by the r38 base fixture (`tests/fixtures/r38-drift-record.py`):

| id | single edit applied to the copy (anchor, applied exactly once) |
|----|----------------------------------------------------------------|
| M11 | before `m = ROW.match(line)`: insert `line = line.rstrip(" \t")` (trailing whitespace tolerated) |
| M12 | `raw.splitlines()` → `raw.split("\n")` (CRLF leaves `\r`) |
| M13 | the `RECORD-OUTSIDE-ROOT` raise in `run()` → `pass` (containment guard removed) |
| M14 | `line.startswith("#")` → `line.lstrip().startswith("#")` (indented comments accepted) |

```
M11-trailing-whitespace-tolerated r39_rc=1 r39_killed=True r39_traceback=False
   r39| case-trailing-space=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] …
   r39| SUMMARY cases=7 pass=6 fail=1
M11-trailing-whitespace-tolerated r38_rc=0 r38_killed=False
   r38| SUMMARY cases=10 pass=10 fail=0
M12-crlf-splitting-broken r39_rc=1 r39_killed=True
   r39| case-crlf=FAIL rc=2 out='REFUSAL RECORD-MALFORMED: line 1 does not match the census schema '
   r39| SUMMARY cases=7 pass=6 fail=1
M12-crlf-splitting-broken r38_rc=0 r38_killed=False
   r38| SUMMARY cases=10 pass=10 fail=0
M13-outside-root-guard-removed r39_rc=1 r39_killed=True
   r39| case-outside-root=FAIL rc=1 want=2 missing=['RECORD-OUTSIDE-ROOT'] out='DRIFT\tABSENT\t../escape\t…'
   r39| SUMMARY cases=7 pass=6 fail=1
M13-outside-root-guard-removed r38_rc=0 r38_killed=False
   r38| SUMMARY cases=10 pass=10 fail=0
M14-indented-comments-accepted r39_rc=1 r39_killed=True
   r39| case-indented-comment=FAIL rc=0 want=2 missing=['RECORD-MALFORMED', 'does not match the census schema'] …
   r39| SUMMARY cases=7 pass=6 fail=1
M14-indented-comments-accepted r38_rc=0 r38_killed=False
   r38| SUMMARY cases=10 pass=10 fail=0
```

Verdict: **PASS** — 4/4 killed by the r39 fixture, exactly one case each, no tracebacks, exit 1; the
named base fixture `r38-drift-record.py` leaves 4/4 alive (`cases=10 pass=10`, exit 0). Matches the
frozen C3 arm I was asked to check (`mutants=4 killed=4 survived=0 base_killed=0`).

### 5.3 The frozen counter agrees with my arm (read-only cross-check)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev c0b007b42af9a03d7edc32533bcac27484223997 \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch /fast/scratch/hyaku/souji-r39/W1ExecC3Fixture

MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=4e07f1df2a61 fixture_sha=567c37a679f5
RC=0
```

Verdict: **PASS** — the frozen C3 predicate reads as required, and `tool_sha`/`fixture_sha` are the
same bytes I ran by hand (§0/§1), so the counter and my hand arm describe one object.

## 6. Cross-reference: M13 is not new coverage (measured here, not inherited)

The r38 write-envelope fixture already asserts `RECORD-OUTSIDE-ROOT`, so my M13 copy is killed twice:

```
python3 -B tests/fixtures/r38-drift-write-envelope.py --tool tools/souji-worktree-drift.py --work <scratch>
case-record-outside-root=PASS
SUMMARY cases=12 pass=12 fail=0          (pristine)

python3 -B tests/fixtures/r38-drift-write-envelope.py --tool <mut-M13.py> --work <scratch>
case-record-outside-root=FAIL rc=1 out=['DRIFT\tABSENT\t../escaped\trecorded regs=1', …]
SUMMARY cases=12 pass=11 fail=1          M13-fixture-rc=1
```

concurring with seat `W1ExecC3Baseline`. The fixture's own docstring claim — "`r36-worktree-drift.py`,
`r37-drift-discrimination.py` and `r38-drift-record.py` collectively say nothing about four documented
parse behaviours" — is true for those three files only (grep counts, `tests/fixtures/r36…r38`:
`OUTSIDE-ROOT` 0/0/0, `crlf` 0/0/0, `indented` 0/0/0, `prunable=0 ` + trailing space 0/0/0), and the
scope it names excludes the write-envelope fixture, so the docstring is not false — but the C3
*narrative* ("every existing drift fixture leaves alive") is, for M13. Frozen predicate unaffected
(`base_killed` names `r38-drift-record.py` only, which reads 10/10 under M13).

## 7. Coverage holes the fixture still leaves (falsification material, outside M11–M14)

Two neighbouring single defects in the *same two parse rules* survive the fixture (r39 `pass=7 fail=0`,
exit 0, no traceback):

| probe | single edit | r39 result |
|-------|-------------|------------|
| P1 | `m = TOTAL.match(line)` → `m = TOTAL.match(line.rstrip(" \t"))` (TOTAL tolerates trailing whitespace; REPO pattern stays `$`-anchored) | `pass=7 fail=0` — **survives** |
| P2 | `m = ROW.match(line)` → `m = ROW.match(line.lstrip(" \t"))` (an indented REPO row is accepted) | `pass=7 fail=0` — **survives** |

```
P1-total-trailing-whitespace-tolerated r39_rc=0 traceback=False
   r39| SUMMARY cases=7 pass=7 fail=0
P2-indented-repo-row-accepted r39_rc=0 traceback=False
   r39| SUMMARY cases=7 pass=7 fail=0
```

So the round's record-rule coverage is: trailing whitespace (`REPO` only, not `TOTAL`), CRLF, outside
root (`../` relative spelling only — the absolute-path spelling of the same guard is untested),
indented `#`. Not covered and not claimed: an indented REPO row, trailing whitespace on a TOTAL row,
trailing whitespace combined with CRLF, and an absolute-path escape row. The fixture meets its frozen
floor (`cases>=6`) regardless; I flag these as the next three cheap cases rather than as a C3 miss.

## Verdicts

| # | Check | Verdict |
|---|-------|---------|
| 1 | Frozen fixture as specified (`--tool tools/… --work /fast/scratch/…`) | **PASS** — `SUMMARY cases=7 pass=7 fail=0`, exit 0 |
| 2 | Fixture bytes == committed bytes at `HEAD`; tool bytes == counter `tool_sha` | **PASS** — sha256 identical |
| 3 | Usage arms (missing `--work`, unreadable `--tool`) | **PASS** — both exit 2 with the documented `usage:` lines |
| 4 | `good` tests what its name says | **PASS** — rc 0, `record_repos=2 live_repos=2 drift_rows=0 unreachable=0` |
| 5 | `trailing-space` | **PASS, right class/line** — `RECORD-MALFORMED: line 1 does not match the census schema`, rc 2; control without the 0x20 = rc 0 |
| 6 | `total-before-rows` | **PASS, right reason** — rc 0; TOTAL is not ignored (`repos=3` control refused) |
| 7 | `crlf` | **PASS, right reason** — `\r\n` bytes accepted rc 0; M12 breaks it to rc 2 |
| 8 | `outside-root` | **PASS, right class** — `RECORD-OUTSIDE-ROOT: ../escape resolves outside …`, rc 2; in-root control = rc 1, never rc 2 |
| 9 | `indented-comment` | **PASS, right class/line** — `RECORD-MALFORMED: line 1 …`, rc 2; unindented control = rc 0 |
| 10 | `comments-total-only` | **PASS, right class** — `RECORD-EMPTY`, rc 2; rows-present control = rc 0 |
| 11 | Any case passes for the wrong reason? | **NO** for a premature/other-class refusal. Named fragility: refusal cases are token-presence only, so an all-refusals stub scores 4/7 (`pass=4 fail=3`); rc-0 cases block it |
| 12 | Independent 4-mutant arm (own mutant definitions) | **PASS** — M11/M12/M13/M14 each killed by exactly one case (`fail=1`, exit 1, no traceback); r38 base fixture `pass=10 fail=0` on all four |
| 13 | Frozen C3 counter (read-only) | **PASS** — `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7`, RC=0 |
| 14 | Adjacent record-rule defects P1/P2 | **SURVIVE** — reported as coverage holes, not a C3 predicate miss |

**Overall: the fixture is sound for its frozen claim** — 7 cases, 7/7 green, every case's stated defect
is the cause of its outcome (control-flipped), 4/4 M11–M14 killed, base fixture kills none. Two
advisories for the L1: (i) four of seven cases are refusal cases that a blanket-refusal stub can
satisfy (the rc-0 cases are the load-bearing ones), and (ii) M13 duplicates the pre-round
`r38-drift-write-envelope.py` coverage, so the round's *new* record-rule coverage is M11/M12/M14 plus
two adjacent holes still open (P1, P2).

## Risks / notes for the L1

- I did not modify, stage or land anything; `git status --porcelain` in the lane shows only other
  seats' work (` M corpus/lessons/round-39.md`, untracked `census/round-39/records/*-after.txt`,
  `census-before.txt`), none of it mine.
- The fixture's `make_repo()` ignores `git init/commit` return codes (`sh(..., check=False)`), so a
  broken scratch git surfaces as a confusing `case-good=FAIL`, not as a usage error. Not observed
  here (both repos initialised; toplevels quoted in §3).
- The fixture also does not assert `git -C <path> rev-parse --show-toplevel == <path>` for the two
  repos it creates; the hard rule for seats' own fixtures. It cannot inherit a parent repo here
  (`hand/fleet-root/fleet` is not inside any repository — quoted `fatal: not a git repository`), so
  the measurement is unaffected.
- `--rev`/`--base-rev`: the counter reads tool/fixture bytes from `--rev` and the *fixture* is run
  from committed bytes extracted into scratch; I kept `--rev` at `HEAD` (`c0b007b`) where bytes equal
  the freeze content of both files, so my hand arm and the counter describe the same objects.
- No package install or upgrade was performed; no `pacman`.
- **Scratch**: `/fast/scratch/hyaku/souji-r39/W1ExecC3Fixture` was removed at the end of this seat
  (`rm -rf`); the drivers I wrote there (`hand-run.sh` with the seven `printf` record bodies, the
  literal `od -An -c` dumps and the controls; `mutant-drive.py` with the M11–M14 anchors quoted in
  §5.2; `probe-gaps.py` with the P1/P2 anchors quoted in §7) are reproducible from this report. The
  tree is **not** on disk at finish.
