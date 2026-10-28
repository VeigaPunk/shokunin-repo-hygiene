# W1ConnOverlap — cross-claim shared-surface scan (round 39, wave 1)

Role: connector. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane base: `ed30b7f5b77939c9073348d810730bc4f355708d`. Audited revision for every read below:
`2201778e7736af82e7d8a42dec2494f115bf3923` (HEAD at scan time).
Worktree at scan time: `M LOG.md`, `M corpus/QUALITY.md`; untracked `census/round-39/make-cells.py`,
`census/round-39/records/{c2-after,c3-after,census-after,census-before}.txt`;
`census/round-39/cells.tsv` **absent**. No tooling installed. No git/jj mutation of any kind.

Question: which surfaces do C1/C2/C3 share, and is a byte one claim touches read by another
claim's counter?

---

## 0. Read sets, as extracted from the counter sources

| claim | byte it reads | where (file:line) |
|---|---|---|
| C1 | `tools/souji-citation-reconcile.py` **extracted from `--rev` and executed** | `census/round-39/c1-counter.py:150` (`git_show(root, rev, "tools/souji-citation-reconcile.py")`), called from `:230` |
| C1 | that tool's stdout `SUMMARY cells=<n> mismatches=<n>` literal | `c1-counter.py:236,239` + `re.search(r"^SUMMARY cells=(\d+) mismatches=(\d+)$")` in `register_leg` |
| C1 | 10 distinct item files (16 rows) at `--rev` | `census/round-39/c1-items.tsv` rows R39-C1-01…16 |
| C1 | `census/round-39/cells.tsv` at `--register-rev` (absent at HEAD) | `c1-counter.py:153` |
| C1 | **planned** register receipts `census/round-39/records/c2-after.txt`, `c3-after.txt`, `c1-before.txt` | `census/round-39/make-cells.py:23-31` (ROWS) |
| C2 | `tools/souji-citation-reconcile.py` (new + base) | `c2-counter.py:52,169,181-182` |
| C2 | `tools/souji-worktree-drift.py` (new + base), **module docstring only** for L4 | `c2-counter.py:53,169,183-184`; `docstring_classes()` at `:133` |
| C2 | fixtures from the **worktree**, not from `--rev` | `c2-counter.py:170` (r39-citation-rev.py), `:252-254` (CONSUMERS `:54-59`) |
| C2 | `census/round-38/cells.tsv` as an inert CLI argument | `c2-counter.py:111` |
| C3 | `tools/souji-worktree-drift.py` at `--rev` (whole blob, then 4 anchored replacements) | `c3-counter.py:123` `git_show(args.root, args.rev, args.tool)`, default `--tool` |
| C3 | mutant anchors: drift code lines 152, 153, 293 | `c3-counter.py` MUTANTS tuple (`SKIP_ANCHOR`, `raw.splitlines()`, `RECORD-OUTSIDE-ROOT`) |
| C3 | fixtures from the **worktree** | `c3-counter.py:124-125` `open(args.fixture)`, `open(args.base_fixture)` |

Instrument line numbers in the audited blobs at HEAD (measured with the command shown):

```
$ git show HEAD:tools/souji-worktree-drift.py | grep -n "RECORD-MISSING\|RECORD-MALFORMED\|if not line.strip() or line.startswith\|for lineno, line in enumerate(raw.splitlines\|raise Refusal(\"RECORD-OUTSIDE-ROOT"
44:  RECORD-MISSING         EACCES or ELOOP opening the record path: the path
46:  RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line
152:    for lineno, line in enumerate(raw.splitlines(), 1):
153:        if not line.strip() or line.startswith("#"):
293:            raise Refusal("RECORD-OUTSIDE-ROOT: %s resolves outside %s" % (row["name"], root_real))
310:                    raise Refusal("RECORD-OUTSIDE-ROOT: %s gitdir resolves outside %s" % (row["name"], root_real))
```

---

## 1. Pair C1 / C2 — **shared instrument (coupling of evidence) + one-way verdict dependence**

The same blob, `tools/souji-citation-reconcile.py`, is executed by C1's register leg
(`c1-counter.py:150,230`) and audited by C2's L1/L2/L3/L5 (`c2-counter.py:181-182`). C2's claim
*is* the repair of that blob; C1's calibration arm *runs* that blob and requires its `SUMMARY`
literal.

Check 1a — both claims pin the same bytes (receipt cross-check + recomputation):

```
$ for rev in ed30b7f5b77939c9073348d810730bc4f355708d HEAD; do for f in tools/souji-citation-reconcile.py tools/souji-worktree-drift.py; do printf '%s ' "$f"; git show "$rev:$f" | sha256sum | cut -c1-12; done; done
tools/souji-citation-reconcile.py 56866ea8f832
tools/souji-worktree-drift.py 14e9c0f77d7e
tools/souji-citation-reconcile.py 59f1e57d7af0
tools/souji-worktree-drift.py e48ed08e6728
```

```
$ grep -o "tool_sha=[^ ]*" census/round-39/records/c2-after.txt census/round-39/records/c3-after.txt
census/round-39/records/c2-after.txt:tool_sha=59f1e57d7af0/e48ed08e6728
census/round-39/records/c3-after.txt:tool_sha=e48ed08e6728
```

→ The citation hash `59f1e57d7af0` in C2's receipt is the exact blob C1's counter would execute at
HEAD. **Verdict: shared instrument, confirmed.**

Check 1b — does C2's repair change C1's register verdict for C1's own invocation class?
C1 always passes a *resolved* `--rev` (it refuses earlier at `c1-counter.py` `git_resolves`), so the
R11 repair is never on C1's path. Measured on a real register (the r38 register, tracked, 10 rows):

```
$ for t in cit-base cit-head; do echo "== $t over r38 register at HEAD"; python3 -B $S/$t.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2201778e… --register census/round-38/cells.tsv --register-rev 2201778e…; echo "rc=$?"; done
== cit-base over r38 register at HEAD
SUMMARY cells=10 mismatches=0
rc=0
== cit-head over r38 register at HEAD
SUMMARY cells=10 mismatches=0
rc=0
```

→ Identical. **Verdict: no verdict dependence on the repaired code path.** The coupling is the
`SUMMARY` contract, not the refusal class.

Check 1c — is the coupling one-way and can it flip C1 alone? Probe: a copy of the HEAD citation
blob with one literal changed (`print("SUMMARY cells=` → `print("SUMMARYX cells=`), injected through
`register_leg` by patching `git_show` (no lane byte touched):

```
$ python3 -B -c "... m.git_show = patched ... m.register_leg(...)"
C1 REGISTER-LEG RAISES: register leg produced no SUMMARY (rc=0 stderr='')
```

and the broken blob itself:

```
$ python3 -B $S/cit-summary-broken.py --root … --rev 2201778e… --register census/round-38/cells.tsv --register-rev 2201778e…
SUMMARYX cells=10 mismatches=0
rc=0
```

→ C1 exits 2 (`REFUSAL COULD-NOT-EVALUATE`) on a single-literal regression in the blob C2 owns.
C2's counter never parses the citation tool's `SUMMARY` line itself, so the same regression would be
scored by C2 only through L5's fixture. **Verdict: C1's register arm is instrument-dependent on C2's
blob, one way. C2 reads no C1 byte (C1's 10 item files ∩ C2's read set = ∅).**

Check 1d — evidence coupling through the register receipts. `make-cells.py:25-27` binds three rows
to `census/round-39/records/c2-after.txt` with expected tokens `legs=6`, `harm=0`, `fail=0` — i.e.
C2's own `SUMMARY` fields. C1's calibration claim therefore quotes C2's result as its evidence.

Current state of C1's register arm (cells.tsv absent, so the arm cannot be scored at all):

```
$ TMPDIR=… python3 -B census/round-39/c1-counter.py --root … --rev 2201778e… --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv
ITEM R39-C1-01 CLOSED
ITEM R39-C1-02 CLOSED
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-05 CLOSED … ITEM R39-C1-16 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

---

## 2. Pair C1 / C3 — **no shared counter-read byte; shared receipt only (coupling of evidence)**

C1's item files are `corpus/lessons/round-38.md`, `census/round-39/records/waves-{wait,capture}.txt`,
`corpus/lessons/round-39.md`, `SKILL.md`, `census/round-38/preregistration.txt`, `SCORECARD.md`,
`LOG.md`, `corpus/QUALITY.md`, `corpus/lessons/round-36.md`. C3 reads only
`tools/souji-worktree-drift.py`, `tests/fixtures/r39-drift-record-rules.py`,
`tests/fixtures/r38-drift-record.py`.

```
$ grep -n "souji-citation-reconcile\|souji-worktree-drift\|cells.tsv\|r38-drift-record\|tool_sha" census/round-39/c1-counter.py census/round-39/c3-counter.py
census/round-39/c1-counter.py:21,150,152      (citation tool only)
census/round-39/c3-counter.py:4,16,24,110…    (drift tool + r38-drift-record only)
```

→ Empty intersection. **Verdict: byte-level separability holds for C1/C3.**

The coupling is evidential: `make-cells.py:28-29` binds REG-04/REG-05 to
`census/round-39/records/c3-after.txt`, expecting `killed=4` and `cases=7`. So C1's register arm
cannot pass while C3's receipt is absent (it is untracked today, §5) or disagrees. C1 never executes
C3's instrument.

---

## 3. Pair C2 / C3 — **shared blob, disjoint lines; plus a shared fixture pinned by neither**

Check 3a — same blob, disjoint line ranges. C2's L4 reads the module docstring: line 44
(`RECORD-MISSING`) and line 46 (`RECORD-MALFORMED`). C3 mutates code: line 152 (`splitlines`), line
153 (`SKIP_ANCHOR`), line 293 (`RECORD-OUTSIDE-ROOT`). **Verdict: shared blob, no shared byte.**

Check 3b — both receipts pin that blob identically, and it equals HEAD:

```
$ grep -o "tool_sha=[^ ]*" census/round-39/records/c2-after.txt census/round-39/records/c3-after.txt
census/round-39/records/c2-after.txt:tool_sha=59f1e57d7af0/e48ed08e6728
census/round-39/records/c3-after.txt:tool_sha=e48ed08e6728
$ git show HEAD:tools/souji-worktree-drift.py | sha256sum | cut -c1-12
e48ed08e6728
```

**Verdict: consistent.** Note the identity is a real cross-claim agreement: C2's second hash field
and C3's whole hash field are the same 12 hex digits.

Check 3c — anchor uniqueness, the coupling hazard C2 creates for C3. C3 fails a mutant with
`MUTANT <id> ANCHOR-COUNT n (expected 1)` if an anchor stops being unique; C2 owns docstring edits of
the same file (commit `790d16b`, `601195a`, `2201778` all rewrote that docstring). Measured at HEAD:

```
$ git show HEAD:tools/souji-worktree-drift.py | grep -c '        if not line.strip() or line.startswith("#"):'
1
$ git show HEAD:tools/souji-worktree-drift.py | grep -c '    for lineno, line in enumerate(raw.splitlines(), 1):'
1
$ git show HEAD:tools/souji-worktree-drift.py | grep -cF 'raise Refusal("RECORD-OUTSIDE-ROOT: %s resolves outside %s" % (row["name"], root_real))'
1
```

→ Unique today (the gitdir message at line 310 is what keeps M13 unique). **Verdict: a docstring edit
that quotes the skip line, e.g. as a "single-line rule" example, makes M11/M14 `ANCHOR-COUNT 2` and
fails C3 while C2 passes.** That is a live, same-file, C2-owned lever on C3's verdict.

Check 3d — `tests/fixtures/r38-drift-record.py` is read by **both** counters and hashed by
**neither**:

- C2: `CONSUMERS` entry `("r38-drift-record", "tests/fixtures/r38-drift-record.py", DRIFT, "--tool")`
  at `c2-counter.py:55`, scored as a consumer that must stay `10/10` green.
- C3: default `--base-fixture tests/fixtures/r38-drift-record.py`, scored as the base arm that must
  keep every mutant alive (`base_killed=0`).

```
$ git show HEAD:tests/fixtures/r38-drift-record.py | sha256sum | cut -c1-12
ac0be0e7a49e
```

C2's `fixture_sha` covers only `r39-citation-rev.py` (`c2-counter.py:170`); C3's covers only its
candidate (`fixture_sha=567c37a679f5`). **Verdict: shared evidence byte with no pin in either
receipt — an edit to it is invisible to both receipts yet can flip C3's `base_killed` or C2's L6.**

---

## 4. Receipt-level cross-checks (both counters re-run at HEAD)

```
$ TMPDIR=… python3 -B census/round-39/c2-counter.py --root … --rev 2201778e… --base-rev ed30b7f5…
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
```

```
$ TMPDIR=… python3 -B census/round-39/c3-counter.py --root … --rev 2201778e… --base-rev ed30b7f5…
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
rc=0
```

Check 4a — **`c2-after.txt` pins a fixture hash that no longer matches the fixture its counter reads:**

```
$ grep -o "fixture_sha=[^ ]*" census/round-39/records/c2-after.txt census/round-39/records/c3-after.txt
census/round-39/records/c2-after.txt:fixture_sha=7ab7c3d85a81
census/round-39/records/c3-after.txt:fixture_sha=567c37a679f5
$ sha256sum tests/fixtures/r39-citation-rev.py | cut -c1-12
e555d8281484
$ git show HEAD:tests/fixtures/r39-citation-rev.py | sha256sum | cut -c1-12
e555d8281484
$ git log --format='%h %ad %s' --date=iso -- tests/fixtures/r39-citation-rev.py
d4c1755 2026-10-28 14:58:20 -0300 round-39: C3/scratch — honour the caller's TMPDIR in c3-counter git children and the r39-citation-rev tool child (wave-1 W1ExecScratch)
bbd9b97 2026-10-28 14:44:44 -0300 round-39: C2 — resolve --rev/--register-rev (exit 2), drift RECORD-MISSING/MALFORMED contract, r39-citation-rev fixture
b769bfb 2026-10-28 14:32:16 -0300 round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
```

→ `7ab7c3d85a81 ≠ e555d8281484`. Cause: commit `d4c1755` (14:58:20) edited the fixture after the
`c2-after.txt` receipt was written (file mtime 14:57), and C2 hashes the fixture from the **worktree**
while it hashes tools from `--rev`. C3's receipt (`567c37a679f5`) still matches. **Verdict: STALE
field; the C2 receipt's own instrument hash no longer describes the bytes a re-run scores. The
citation tool only checks `expected` on a `SUMMARY` line, so this staleness passes the C1 register
silently.**

Check 4b — frozen-contract number vs instrument:

```
$ grep -n "six consumer\|five consumer\|L6 " census/round-39/preregistration.txt census/round-39/c2-counter.py
census/round-39/preregistration.txt:62:bytes, L6 six consumer fixtures stay green.
census/round-39/c2-counter.py:19:  L6  five consumer fixtures stay green and none loses a passing case against the base bytes.
$ grep -n "CONSUMERS = (" -A6 census/round-39/c2-counter.py
54:CONSUMERS = (
55:    ("r38-drift-record", …), 56: ("r36-worktree-drift", …), 57: ("r38-drift-envelope", …),
58:    ("r37-citation", …), 59: ("r38-citation-commit", …),
```

→ prereg says **six**, the instrument says and scores **five** (the c2-after L6 line lists five).
Unresolvable by measurement: the counter scores 5. **Verdict: CONTRADICTION between frozen contract
and instrument; must be disclosed, not reconciled.**

Check 4c — name-level coupling of the registry surface. C1 item R39-C1-06 closes on `SKILL.md:283`
(whole-token `r38-citation-commit,r38-drift-write-envelope,r38-drift-record,r38-drift-mutants`), while
C2's `CONSUMERS` runs `{r38-drift-record, r36-worktree-drift, r38-drift-write-envelope,
r37-citation-reconcile, r38-citation-commit}`. Intersection = 3. C1 registers `r38-drift-mutants`,
which C2 never runs; C2 depends on `r36-worktree-drift` and `r37-citation-reconcile`, which C1's
registry item never asserts. **Verdict: registry coverage seam — the R6 closure does not cover two
fixtures C2's L6 rests on.** The same file is also write-shared: C2/C3 seats add the r39 fixture rows
to `SKILL.md` while C1's R39-C1-06 binds line 283 of it, so a registry-row rewrite that disturbs that
line flips a C1 item without touching any C2/C3 verdict.

---

## 5. Live write-write overlap (same lines, different claims)

```
$ git status --porcelain=v1
 M LOG.md
 M corpus/QUALITY.md
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
$ git diff LOG.md corpus/QUALITY.md | grep "^+" | cut -c1-140
+R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) carries the superseded before-arm letters `cases=9 pass=3 fail=6 base_fail=6` and the count
+R39-C1-12 — LOG-line-1862 quotes the pre-amendment letters faithfully (`cells=9` and `cases=6 base_fail>=3` are the frozen r37 targets at
+R39-C1-13 — QUALITY-line-209's evidence cell (`census/round-37/records/c2-before.txt` (4 escapes) vs `c2-after.txt` (0)) should have carr
```

A sibling seat is rewriting **in place** the lines anchored `R39-C1-11/12/13` — the exact lines C1's
items read — while `make-cells.py:59-63` writes `cells.tsv` / `cells-lines.md` with the `R39-REG-0x`
lines that the L1 copies into the same three host files (`SCORECARD.md`, `LOG.md`,
`corpus/QUALITY.md`). Scored against the **worktree** bytes (same
`has_token` predicate, `--rev` bypassed):

```
$ python3 -B -c "... parse_items + has_token over worktree files ..." | grep -v CLOSED
WORKTREE R39-C1-03 OPEN FILE-ABSENT
WORKTREE R39-C1-04 OPEN FILE-ABSENT
```

→ the in-flight rewrite currently preserves every item token (14/16 CLOSED, same two FILE-ABSENT as
at HEAD). **Verdict: same-file/same-line overlap, currently harmless; it is the r38 R8/R9
in-place-rewrite class, so the landing must be scored at the landing revision, not the worktree.**

---

## Verdicts

| # | check | verdict |
|---|---|---|
| 1 | C1/C2 shared instrument blob | **SHARED — YES** (coupling of evidence) |
| 2 | C1 verdict dependence on C2's repair path | NO for resolved revs (`cells=10 mismatches=0` both) |
| 3 | C1 verdict dependence on the instrument's `SUMMARY` literal | **YES, one-way** (`register leg produced no SUMMARY`, C1 rc 2) |
| 4 | C1/C3 shared counter-read byte | **NO** (empty intersection) |
| 5 | C1/C3 shared evidence | **YES** — REG-04/05 read `c3-after.txt` |
| 6 | C2/C3 shared blob | **YES**, disjoint lines (44/46 vs 152/153/293) |
| 7 | C2/C3 shared fixture `r38-drift-record.py` | **YES**, pinned by neither (`ac0be0e7a49e`) |
| 8 | cross-receipt drift `tool_sha` | CONSISTENT (`e48ed08e6728` in both, = HEAD) |
| 9 | `c2-after.txt` `fixture_sha` | **STALE** (`7ab7c3d85a81` vs `e555d8281484`) |
| 10 | prereg "six consumers" vs instrument "five" | **CONTRADICTION** |
| 11 | C1 item lines vs register host lines | same-file/same-line, in-flight, currently harmless |

## What the report MUST disclose

1. C1's register leg **executes the C2-audited citation blob** (`c1-counter.py:150,230`): one
   regression in that blob is scored twice — as a C2 failure and as a C1 could-not-evaluate. Claims
   are separable; **verdicts are not**, in that direction.
2. C1's register rows **quote C2's and C3's receipts** as `expected` tokens (`legs=6`, `harm=0`,
   `fail=0`, `killed=4`, `cases=7`): C1's calibration evidence includes C2's and C3's outputs.
3. `c2-after.txt`'s `fixture_sha=7ab7c3d85a81` is stale against the fixture at HEAD
   (`e555d8281484`, changed by `d4c1755` after the receipt); the citation tool cannot see it.
4. `tests/fixtures/r38-drift-record.py` is read by both C2 (L6 consumer) and C3 (base arm) and is
   pinned by neither receipt.
5. `preregistration.txt:62` says six consumers; `c2-counter.py:19` and `CONSUMERS:54-59` say and
   score five.

Not required as a disclosure: the drift blob sharing itself (C2 docstring vs C3 code lines are
disjoint), but the C2-owned docstring edit that would quote the `SKIP_ANCHOR` line is the one lever
that kills C3 with `ANCHOR-COUNT 2` while C2 stays green — worth a one-line caveat if the drift
docstring is touched again.

## Scratch

`/fast/scratch/hyaku/souji-r39/W1ConnOverlap` **still on disk** at finish: `cit-base.py`,
`cit-head.py`, `cit-summary-broken.py`, `citation-reconcile.py` (written by the `register_leg` probe
into the scratch I passed). All counter runs used `TMPDIR=/fast/scratch/hyaku/souji-r39/W1ConnOverlap`.
No lane byte outside this report was written; no install was performed.
