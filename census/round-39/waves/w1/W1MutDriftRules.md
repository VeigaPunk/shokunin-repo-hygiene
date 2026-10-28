# W1MutDriftRules — record-parser mutation hunt (souji r39, wave 1)

Seat: mutation-tester (leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane HEAD at start `2201778e7736af82e7d8a42dec2494f115bf3923`, at end
`d4c1755` (a sibling landed bytes mid-seat; the tool bytes I measured did not change).
Tool measured: `tools/souji-worktree-drift.py`, sha256
`e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` (19688 bytes) — identical
to `git show 2201778:tools/souji-worktree-drift.py` and to `git show d4c1755:...` (verified by
`sha256sum` before and after; see Restoration).
Fixtures: `tests/fixtures/r39-drift-record-rules.py` sha256 `567c37a679f5…` (7 cases),
`tests/fixtures/r38-drift-record.py` sha256 `ac0be0e7a49e…` (10 cases).
Scratch: `/fast/scratch/hyaku/souji-r39/W1MutDriftRules` (removed at exit — see Scratch).
No tool was installed or upgraded; nothing outside the report path and my scratch was written.

Task: find record-parser behaviours the round's four mutants (M11–M14) and the r38 battery
(M7–M10 + the r36/r37/r38 fixtures) miss. **C3 is not widened here** — this is a limits report.

---

## 1. Branch inventory of `parse_record` (tool lines 128–183)

Read directly from the tool bytes. "Coverage" names the fixture/mutant that would die if the
branch were broken.

| # | line | branch | behaviour | covered by |
|---|------|--------|-----------|------------|
| B1 | 134 | `exc.errno == errno.ENOENT` | missing record → `RECORD-MALFORMED … is not a regular file` | `r38-drift-record` `missing-record` |
| B2 | 136 | any other `OSError` (EACCES, ELOOP) | `RECORD-MISSING: <exc>` | **no behavioural case**; only the static `docstring-enum` case of `r38-drift-write-envelope.py` pins the class *name* |
| B3 | 138 | `not stat.S_ISREG(fstat(fd))` | non-regular record (dir/FIFO/device) → `RECORD-MALFORMED` | **none** |
| B4 | 132 | `O_RDONLY \| O_NONBLOCK` (+ `set_blocking(True)` at 140) | a FIFO record can never block the run | **none** (only the `--json` FIFO is covered, `r38-drift-write-envelope` `fifo-json-*`) |
| B5 | 147 | `decode("utf-8", "replace")` | non-UTF-8 record bytes are tolerated (U+FFFD) | **none** |
| B6 | 153 | `not line.strip()` | blank lines skipped | `r38-drift-record` `comments-and-blanks` |
| B7 | 153 | `line.startswith("#")` (column 0 only) | comment lines skipped | `r38-drift-record` `comments-and-blanks`; inverse pinned by `r39` `indented-comment` |
| B8 | 159 | duplicate REPO name | `RECORD-MALFORMED … duplicates` | **M10** |
| B9 | 152 | `raw.splitlines()` | the Unicode terminator set splits a record | LF/CRLF only: **M12**, `r39` `crlf`. CR-alone / VT / FF / NEL / U+2028 **unpinned** |
| B10 | 160–163 | TOTAL row assigned wherever it appears; **last** row wins | position pinned by `r39` `total-before-rows`; **duplicate TOTAL rows unpinned** |
| B11 | 166 | line matching neither schema | `RECORD-MALFORMED … does not match the census schema` | `r38` `bad-line`, `r39` `trailing-space` |
| B12 | 168 | no REPO rows | `RECORD-EMPTY` | `r38` `empty-record`, `r39` `comments-total-only` |
| B13 | 170 | `TOTAL repos` vs row count | `RECORD-MALFORMED` | **M7** |
| B14 | 172 | `TOTAL regs` vs sum | `RECORD-MALFORMED` | **M8** |
| B15 | 174 | `TOTAL prunable` vs sum | `RECORD-MALFORMED` | **M9** |

Uncovered: **B2, B3, B4, B5, B10 (duplicate TOTAL), B9 (terminator set beyond LF/CRLF)**.
One mutant per uncovered branch below (N1–N5, N7); N6 is a negative control proving the
detector is alive on mutated bytes.

## 2. What I ran

Driver written in scratch (never in the lane): `probe.py` applies each mutant to a scratch copy of
the tool, scores it against both record fixtures with the r38 A5 contract (kill = fixture's own
`fail>0` + `rc==1` + no traceback), and then runs a **distinguishing probe** — a concrete input
where pristine and mutant differ observably, so a survivor means "unasserted behaviour", never
"semantically equivalent edit". A second driver `sweep_extra.py` scores the survivors against the
other three drift fixtures.

```
S=/fast/scratch/hyaku/souji-r39/W1MutDriftRules
TMPDIR=$S python3 -B $S/probe.py \
  --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py \
  --work $S \
  --fixture39 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r39-drift-record-rules.py \
  --fixture38 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py
TMPDIR=$S python3 -B $S/sweep_extra.py $S
```

### 2.1 Pristine controls and the seven mutants (verbatim output)

```
TOOL sha256=e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76 bytes=19688
PRISTINE fixture39=pass (SUMMARY cases=7 pass=7 fail=0 rc=0)
PRISTINE fixture38=pass (SUMMARY cases=10 pass=10 fail=0 rc=0)
MUTANT N1 killed39=no base38=no | branch: open() errno != ENOENT (EACCES/ELOOP) -> RECORD-MISSING | defect: unreadable-record class collapsed into RECORD-MALFORMED
  fixture39 SUMMARY cases=7 pass=7 fail=0 rc=0 fails=0 crash=False
  fixture38 SUMMARY cases=10 pass=10 fail=0 rc=0 fails=0 crash=False
  probe pristine: rc=2 REFUSAL RECORD-MISSING: [Errno 13] Permission denied: '…/eacces.tsv'
  probe mutant  : rc=2 REFUSAL RECORD-MALFORMED: …/eacces.tsv is not a regular file
  probe distinguishable=yes
MUTANT N2 killed39=no base38=no | branch: fstat S_ISREG guard -> RECORD-MALFORMED for a directory/FIFO record | defect: non-regular record path no longer refused (EISDIR traceback)
  fixture39 SUMMARY cases=7 pass=7 fail=0 rc=0 fails=0 crash=False
  fixture38 SUMMARY cases=10 pass=10 fail=0 rc=0 fails=0 crash=False
  probe pristine: rc=2 REFUSAL RECORD-MALFORMED: …/as-directory.tsv is not a regular file
  probe mutant  : rc=1 Traceback (most recent call last): … N2.py", line 451, in <module>
  probe distinguishable=yes
MUTANT N3 killed39=no base38=no | branch: O_NONBLOCK open so a FIFO record cannot block | defect: FIFO record blocks the run forever (no termination, no report)
  fixture39 SUMMARY cases=7 pass=7 fail=0 rc=0 fails=0 crash=False
  fixture38 SUMMARY cases=10 pass=10 fail=0 rc=0 fails=0 crash=False
  probe pristine: rc=2 REFUSAL RECORD-MALFORMED: …/as-fifo.tsv is not a regular file
  probe mutant  : TIMEOUT-HANG
  probe distinguishable=yes
MUTANT N4 killed39=no base38=no | branch: decode("utf-8", "replace") tolerance for non-UTF-8 record bytes | defect: invalid UTF-8 record bytes escape as a UnicodeDecodeError traceback
  fixture39 SUMMARY cases=7 pass=7 fail=0 rc=0 fails=0 crash=False
  fixture38 SUMMARY cases=10 pass=10 fail=0 rc=0 fails=0 crash=False
  probe pristine: rc=1 DRIFT	ABSENT	��	recorded regs=1 DRIFT	UNRECORDED	alpha	… SUMMARY record=…
  probe mutant  : rc=1 Traceback (most recent call last): … N4.py", line 451, in <module>
  probe distinguishable=yes
MUTANT N5 killed39=no base38=no | branch: TOTAL row assignment: any position, last row wins | defect: a second TOTAL row is refused as a schema violation (duplicate-TOTAL class unpinned)
  fixture39 SUMMARY cases=7 pass=7 fail=0 rc=0 fails=0 crash=False
  fixture38 SUMMARY cases=10 pass=10 fail=0 rc=0 fails=0 crash=False
  probe pristine: rc=0 SUMMARY … record_repos=2 record_regs=2 record_prun…
  probe mutant  : rc=2 REFUSAL RECORD-MALFORMED: line 4 does not match the census schema
  probe distinguishable=yes
MUTANT N6 killed39=yes base38=yes | branch: str.splitlines(): the whole Unicode line-terminator set splits a record | defect: NEGATIVE CONTROL: split("\r\n") also breaks LF records, so every case dies
  fixture39 SUMMARY cases=7 pass=5 fail=2 rc=1 fails=2 crash=False
  fixture38 SUMMARY cases=10 pass=3 fail=7 rc=1 fails=7 crash=False
  probe pristine: rc=0 SUMMARY … record_repos=2 record_regs=2 record_prunab…
  probe mutant  : rc=2 REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
  probe distinguishable=yes
MUTANT N7 killed39=no base38=no | branch: splitlines(): CR alone (and VT/FF/NEL/U+2028) also terminates a line | defect: a CR-only record is one schema-violating line; LF and CRLF still pass
  fixture39 SUMMARY cases=7 pass=7 fail=0 rc=0 fails=0 crash=False
  fixture38 SUMMARY cases=10 pass=10 fail=0 rc=0 fails=0 crash=False
  probe pristine: rc=0 SUMMARY … record_repos=2 record_regs=2 record_prunab…
  probe mutant  : rc=2 REFUSAL RECORD-MALFORMED: line 1 does not match the census schema
  probe distinguishable=yes
SUMMARY mutants=7 killed_by_r39=1 survived=6
```

Mutant definitions (single line each, anchor count verified `== 1` before application):

| id | branch | anchor → replacement |
|----|--------|----------------------|
| N1 | B2 | `raise Refusal("RECORD-MISSING: %s" % exc)` → `raise Refusal("RECORD-MALFORMED: %s is not a regular file" % path)` |
| N2 | B3 | `if not stat.S_ISREG(os.fstat(fd).st_mode):` → `if False and not stat.S_ISREG(…)` |
| N3 | B4 | `os.open(path, os.O_RDONLY \| os.O_NONBLOCK)` → `os.open(path, os.O_RDONLY)` |
| N4 | B5 | `.decode("utf-8", "replace")` → `.decode("utf-8", "strict")` |
| N5 | B10 | `m = TOTAL.match(line)` / `if m:` → `if m and total is None:` |
| N6 | B9 (control) | `raw.splitlines()` → `raw.split("\r\n")` |
| N7 | B9 (narrow) | `raw.splitlines()` → `re.split(r"\r\n\|\n", raw)` |

### 2.2 The survivors against the three other drift fixtures (verbatim)

```
PRISTINE r36-worktree-drift.py=pass (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0)
PRISTINE r37-drift-discrimination.py=pass (SUMMARY cases=6 pass=6 fail=0 rc=0)
PRISTINE r38-drift-write-envelope.py=pass (SUMMARY cases=12 pass=12 fail=0 rc=0)
MUTANT N1 vs r36-worktree-drift.py killed=no (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0 fails=0 crash=False)
MUTANT N1 vs r37-drift-discrimination.py killed=no (SUMMARY cases=6 pass=6 fail=0 rc=0 fails=0 crash=False)
MUTANT N1 vs r38-drift-write-envelope.py killed=yes (SUMMARY cases=12 pass=11 fail=1 rc=1 fails=1 crash=False)
MUTANT N2 vs r36-worktree-drift.py killed=no (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0 fails=0 crash=False)
MUTANT N2 vs r37-drift-discrimination.py killed=no (SUMMARY cases=6 pass=6 fail=0 rc=0 fails=0 crash=False)
MUTANT N2 vs r38-drift-write-envelope.py killed=no (SUMMARY cases=12 pass=12 fail=0 rc=0 fails=0 crash=False)
MUTANT N3 vs r36-worktree-drift.py killed=no (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0 fails=0 crash=False)
MUTANT N3 vs r37-drift-discrimination.py killed=no (SUMMARY cases=6 pass=6 fail=0 rc=0 fails=0 crash=False)
MUTANT N3 vs r38-drift-write-envelope.py killed=no (SUMMARY cases=12 pass=12 fail=0 rc=0 fails=0 crash=False)
MUTANT N4 vs r36-worktree-drift.py killed=no (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0 fails=0 crash=False)
MUTANT N4 vs r37-drift-discrimination.py killed=no (SUMMARY cases=6 pass=6 fail=0 rc=0 fails=0 crash=False)
MUTANT N4 vs r38-drift-write-envelope.py killed=no (SUMMARY cases=12 pass=12 fail=0 rc=0 fails=0 crash=False)
MUTANT N5 vs r36-worktree-drift.py killed=no (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0 fails=0 crash=False)
MUTANT N5 vs r37-drift-discrimination.py killed=no (SUMMARY cases=6 pass=6 fail=0 rc=0 fails=0 crash=False)
MUTANT N5 vs r38-drift-write-envelope.py killed=no (SUMMARY cases=12 pass=12 fail=0 rc=0 fails=0 crash=False)
MUTANT N7 vs r36-worktree-drift.py killed=no (SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED rc=0 fails=0 crash=False)
MUTANT N7 vs r37-drift-discrimination.py killed=no (SUMMARY cases=6 pass=6 fail=0 rc=0 fails=0 crash=False)
MUTANT N7 vs r38-drift-write-envelope.py killed=no (SUMMARY cases=12 pass=12 fail=0 rc=0 fails=0 crash=False)
```

N1's only kill is the **static** `docstring-enum` case (its `phantom=` arm: `RECORD-MISSING` stays
in the docstring but leaves the code). No fixture feeds an unreadable record, so the *behaviour*
is unasserted even though the *name* is pinned.

### 2.3 C3 at lane HEAD (context, read-only; not my claim)

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev $(git rev-parse HEAD) --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch /fast/scratch/hyaku/souji-r39/W1MutDriftRules
```
```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```
`cases=7` satisfies the frozen "fewer than six cases" kill rule. C3 holds as specified.

---

## 3. Verdicts

| check | verdict | evidence |
|-------|---------|----------|
| Pristine candidate fixture on unmutated tool | **PASS** | `cases=7 pass=7 fail=0 rc=0` |
| Pristine r38 fixture on unmutated tool | **PASS** | `cases=10 pass=10 fail=0 rc=0` |
| Detector is alive on mutated bytes (N6 control) | **PASS** | killed by both record fixtures (`fail=2`, `fail=7`) |
| Every mutant is behaviour-bearing, not equivalent | **PASS** | `probe distinguishable=yes` for all 7 |
| M11–M14 cover the record parser | **NO** | 6 uncovered behaviours named below |
| C3 predicate at lane HEAD | **PASS** | `mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7` |
| Round's four mutants miss the classes I list | **CONFIRMED** | 6 survivors × 5 fixtures, none killed |

Survivor classes (each survived `r39-drift-record-rules.py`, `r38-drift-record.py`,
`r36-worktree-drift.py`, `r37-drift-discrimination.py`, `r38-drift-write-envelope.py`):

1. **L1 — unreadable record (EACCES/ELOOP).** No fixture feeds a record it cannot open. Pristine
   `RECORD-MISSING` vs mutant `RECORD-MALFORMED` are both exit 2, so only a class-token assertion
   discriminates; the class name is pinned only nominally by `docstring-enum`.
2. **L2 — non-regular record path (directory).** Removing the `S_ISREG` guard turns a directory
   record into an uncaught `OSError(EISDIR)` traceback (exit 1, no `REFUSAL`), not a refusal.
   No fixture passes a directory as `--record`.
3. **L3 — FIFO record hangs forever.** Dropping `O_NONBLOCK` makes the run block with no
   termination and no report (`TIMEOUT-HANG`). The r38 envelope covers only `--json` FIFOs; no
   fixture creates a FIFO *record*. This is the r37 A2.4 defect class, still unasserted for the
   record path.
4. **L4 — non-UTF-8 record bytes.** Pristine tolerates them (`decode(…, "replace")`) and emits a
   drift row naming a U+FFFD phantom repo (`DRIFT ABSENT ��`); a strict decode escapes as a
   traceback. Neither direction is asserted.
5. **L5 — duplicate TOTAL rows.** Pristine takes the last TOTAL and ignores earlier ones; the
   mutant refuses the second row as a schema violation (`line 4 does not match the census
   schema`). The record grammar documents one TOTAL row and pins nothing for two.
6. **L6 — line-terminator set beyond LF/CRLF.** `str.splitlines()` also splits on CR alone, VT, FF,
   NEL and U+2028; only LF and CRLF are pinned (M12, `r39 crlf`). A CR-only record is accepted
   today and the narrow mutant N7 survives every fixture.

Adjacent observation (advisory, not a C3 miss claim): `census/round-39/records/c3-before.txt`
reads `cases=10 … fixture_sha=ac0be0e7a49e`, and `ac0be0e7a49e` is the sha256 of
`tests/fixtures/r38-drift-record.py` (10 cases), while the candidate fixture is
`567c37a679f5…` (7 cases) and does not exist at `ed30b7f`
(`git cat-file -e ed30b7f:tests/fixtures/r39-drift-record-rules.py` → *exists on disk, but not in
ed30b7f*). So the recorded before-control was scored with the **r38** fixture in the candidate
slot: it cannot distinguish "the new fixture has no such case" from "the base bytes have no such
behaviour". The frozen kill rule has no control-discrimination clause, so C3 is not missed by
this — but a r40 before-control should carry the candidate fixture's own sha at a revision where
that sha exists.

## 4. Restoration and scratch

The lane was never written: mutants live only in scratch copies, and the tool was read, never
opened for writing. Before/after: `sha256sum tools/souji-worktree-drift.py` →
`e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` both times;
`git status --porcelain tools/ tests/fixtures/` printed nothing (`STATUS-CLEAN-TOOL-AND-FIXTURES`).
No git/jj mutation was run anywhere; the only git calls were `rev-parse`, `show`, `cat-file`,
`status`, `log`. No `pacman`/install was run.
Scratch `/fast/scratch/hyaku/souji-r39/W1MutDriftRules` was removed at exit
(`rm -rf`), verified absent afterwards; the two drivers and their outputs are reproducible from
the commands in §2.
