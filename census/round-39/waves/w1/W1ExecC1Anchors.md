# W1ExecC1Anchors — C1 anchor census at base (round 39, wave 1)

Seat: W1ExecC1Anchors (executor, lane souji-shokunin)
Assignment: for each of the 16 C1 items, count its anchor across the WHOLE lane tree at base
(`git grep -c -F <anchor> ed30b7f... -- .`), report named-file hits (expected 0), other-file hits,
and any item whose `must` tokens already sit on a line of the named file at base.
Lane base measured: `ed30b7f5b77939c9073348d810730bc4f355708d` (contract `base revision`).
Lane HEAD moved under me during the wave; the one HEAD measurement below pins `2201778` and is
labelled non-contract.

Instruments (kept on disk, /fast/scratch, ~9 KB total):
`/fast/scratch/hyaku/souji-r39/W1ExecC1Anchors/{anchor-census.py,vacuity.py,must-collide.py}`.
They import the committed counter `census/round-39/c1-counter.py` read-only
(`importlib` + `PYTHONDONTWRITEBYTECODE=1 python3 -B`) so token matching is the frozen
`has_token`, not a local re-implementation. No file in the lane was written.

---

## 0. Base revision resolves

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify ed30b7f5b77939c9073348d810730bc4f355708d^{commit}
ed30b7f5b77939c9073348d810730bc4f355708d
```
Verdict: PASS — base is a commit in this lane.

---

## 1. Named-file hits at base (expected 0)

```
$ for spec in "R39-C1-01 corpus/lessons/round-38.md" ... "R39-C1-16 corpus/lessons/round-36.md"; do
    out=$(git -C <lane> grep -c -F "$a" ed30b7f... -- "$f" 2>&1); printf '%s file=%s rc=%d out=%s\n' "$a" "$f" $? "${out:-<empty>}"; done
R39-C1-01 file=corpus/lessons/round-38.md rc=1 out=<empty>
R39-C1-02 file=corpus/lessons/round-38.md rc=1 out=<empty>
R39-C1-03 file=census/round-39/records/waves-wait.txt rc=1 out=<empty>
R39-C1-04 file=census/round-39/records/waves-capture.txt rc=1 out=<empty>
R39-C1-05 file=corpus/lessons/round-39.md rc=1 out=<empty>
R39-C1-06 file=SKILL.md rc=1 out=<empty>
R39-C1-07 file=corpus/lessons/round-39.md rc=1 out=<empty>
R39-C1-08 file=census/round-38/preregistration.txt rc=1 out=<empty>
R39-C1-09 file=census/round-38/preregistration.txt rc=1 out=<empty>
R39-C1-10 file=SCORECARD.md rc=1 out=<empty>
R39-C1-11 file=LOG.md rc=1 out=<empty>
R39-C1-12 file=LOG.md rc=1 out=<empty>
R39-C1-13 file=corpus/QUALITY.md rc=1 out=<empty>
R39-C1-14 file=corpus/lessons/round-38.md rc=1 out=<empty>
R39-C1-15 file=corpus/lessons/round-39.md rc=1 out=<empty>
R39-C1-16 file=corpus/lessons/round-36.md rc=1 out=<empty>
```
All 16: named-file hits = 0. Verdict: **PASS**, and it agrees with the committed control.

Cross-check against the control receipt's per-item classes
(`census/round-39/records/c1-before.txt`, `SUMMARY items=16 open=16 ... items_sha=d892b74f8358`):
5 items are `FILE-ABSENT` at base (`waves-wait.txt` 03, `waves-capture.txt` 04,
`corpus/lessons/round-39.md` 05/07/15) and the other 11 exist with zero anchor lines. My scan
reproduces exactly that partition:

```
$ python3 -B vacuity.py
R39-C1-01   corpus/lessons/round-38.md                    lines=282 anchor_lines=0 must_satisfied_lines=0
R39-C1-02   corpus/lessons/round-38.md                    lines=282 anchor_lines=0 must_satisfied_lines=0
R39-C1-03   census/round-39/records/waves-wait.txt        FILE-ABSENT
R39-C1-04   census/round-39/records/waves-capture.txt     FILE-ABSENT
R39-C1-05   corpus/lessons/round-39.md                    FILE-ABSENT
R39-C1-06   SKILL.md                                      lines=440 anchor_lines=0 must_satisfied_lines=0
R39-C1-07   corpus/lessons/round-39.md                    FILE-ABSENT
R39-C1-08   census/round-38/preregistration.txt           lines=228 anchor_lines=0 must_satisfied_lines=0
R39-C1-09   census/round-38/preregistration.txt           lines=228 anchor_lines=0 must_satisfied_lines=0
R39-C1-10   SCORECARD.md                                  lines=736 anchor_lines=0 must_satisfied_lines=0
R39-C1-11   LOG.md                                        lines=1872 anchor_lines=0 must_satisfied_lines=0
R39-C1-12   LOG.md                                        lines=1872 anchor_lines=0 must_satisfied_lines=0
R39-C1-13   corpus/QUALITY.md                             lines=219 anchor_lines=0 must_satisfied_lines=0
R39-C1-14   corpus/lessons/round-38.md                    lines=282 anchor_lines=0 must_satisfied_lines=0
R39-C1-15   corpus/lessons/round-39.md                    FILE-ABSENT
R39-C1-16   corpus/lessons/round-36.md                    lines=173 anchor_lines=0 must_satisfied_lines=0
```
Verdict: **PASS** — the base control `open=16` is reproducible and the anchor lines are genuinely
absent, not merely absent-from-the-named-file.

---

## 2. Other-file hits at base (whole-tree anchor census)

```
$ python3 -B anchor-census.py     # git grep -c -F <anchor> <rev> -- .  per anchor
rev=ed30b7f5b77939c9073348d810730bc4f355708d
items=16

id          named other total  must_line_at_base
R39-C1-01   0     0     0      none
R39-C1-02   0     0     0      none
R39-C1-03   0     14    14     FILE-ABSENT
R39-C1-04   0     7705  7705   FILE-ABSENT
R39-C1-05   0     0     0      FILE-ABSENT
R39-C1-06   0     0     0      none
R39-C1-07   0     0     0      FILE-ABSENT
R39-C1-08   0     0     0      none
R39-C1-09   0     0     0      none
R39-C1-10   0     0     0      none
R39-C1-11   0     0     0      none
R39-C1-12   0     0     0      none
R39-C1-13   0     0     0      none
R39-C1-14   0     0     0      none
R39-C1-15   0     0     0      FILE-ABSENT
R39-C1-16   0     0     0      none

named_nonzero: []
other_nonzero: [('R39-C1-03', 14), ('R39-C1-04', 7705)]
must_vacuous_candidates: []
```

**14 of 16 anchors are globally absent at base** (0 matches anywhere in the tree) — those are
tree-unique by construction and a whole-tree `grep` re-derives them without ambiguity.

**2 of 16 anchors are heavily collided.** Exact per-file census:

```
$ git grep -c -F 'dead=0' ed30b7f... -- .
.ufo/waves/round-18/w1/CensusWatchdog.patch:1
.ufo/waves/round-18/w1/CensusWatchdogFix.patch:3
.ufo/waves/round-26/assimilation/validate/tools/souji-census.sh:2
census/round-26/waves/assimilation/validate/tools/souji-census.sh:2
census/round-26/waves/w1/ExecResultsCount.md:2
census/round-32/waves/w1/deliver-souji-census.sh:2
tools/souji-census.sh:2
$ git grep -F 'dead=0' ed30b7f... -- . | wc -l
14

$ git grep -c -F 'SUMMARY' ed30b7f... -- . | wc -l
1689          # files (1688 text: -I drops tools/.../__pycache__/souji-landing-gate.cpython-314.pyc:7)
$ git grep -F 'SUMMARY' ed30b7f... -- . | wc -l
7706          # lines (7705 with -I)
$ git grep -c -F 'SUMMARY' ed30b7f... -- . | sort -t: -k2 -rn | head -3
census/round-30/waves/w1/SwarmMutationTester28-runs.txt:115
census/round-9/seat-10.json:78
SCORECARD.md:64
```

Verdict: **FAIL on the `c1-items.tsv` header claim** ("Line-unique anchors keep the predicate
re-derivable"), for R39-C1-03 (`dead=0`) and R39-C1-04 (`SUMMARY`). No close/false-close harm: the
counter only ever greps `row["file"]`, and every colliding file is outside the named path, so the
16-item closure verdict is unaffected. The harm is auditability — a third party re-deriving from
the anchor alone gets 14 and 7706 candidate lines, not one. `dead=0` is also a `must` token of item
02, so any whole-tree derivation of `dead=0` mixes two items.

---

## 3. Structural finding: anchor uniqueness is impossible at the landing revision

```
$ git grep -c -F R39-C1-01 HEAD -- .     # HEAD = 2201778
census/round-39/c1-items.tsv:1
census/round-39/records/c1-before.txt:1
corpus/lessons/round-38.md:1
corpus/lessons/round-39.md:1
$ git grep -c -F R39-C1-16 HEAD -- .
census/round-39/c1-items.tsv:1
census/round-39/records/c1-before.txt:1
corpus/lessons/round-36.md:1
corpus/lessons/round-39.md:1
```
(same shape for 03, 04, 06). At any revision that contains `census/round-39/c1-items.tsv` — i.e.
every landing revision — **every** anchor already occurs in the items table itself (as `path:1`,
the anchor column) and in `records/c1-before.txt` (as `anchor='R39-C1-01'`). At base both files are
absent, which is the only reason 14 items read 0.

Verdict: **PASS for the counter** (per-file read, unaffected), **INSTRUCTION for the round**: any
tree-wide anchor audit at the landing revision MUST exclude
`census/round-39/c1-items.tsv` and `census/round-39/records/c1-before.txt`, or it will always report
collisions; a reviewer re-deriving "line-unique" without that exclusion will wrongly fault all 16.

---

## 4. Vacuous-closeability: do the `must` tokens already sit on a line at base?

### 4a. In the named file — none

`must_satisfied_lines=0` for all 11 present files (§1 table, exact `has_token` semantics, mustnot
included). No item can be closed by appending the anchor to an existing named-file line.
Verdict: **PASS**.

### 4b. In some other lane file — R39-C1-04 only, and it exposes a real defect

```
$ python3 -B must-collide.py     # per item: lines anywhere at base satisfying all must + no mustnot
R39-C1-01   must0=S246                     whole_tree_must_lines=0 other_file=0
R39-C1-02   must0=w1-reports=42/42         whole_tree_must_lines=0 other_file=0
R39-C1-03   must0=waves=1                  whole_tree_must_lines=0 other_file=0
R39-C1-04   must0=records=                 whole_tree_must_lines=2 other_file=2
    OTHER census/round-29/records/preregistration.txt:7 :: C2 — axis operability ... `rN records= failed= uncovered= ...` and `SUMMARY manifests=<m> failed=<f> uncovered=<u>` ... `manifests=3 failed=0 uncovered=0 floor_violations=0`
    OTHER census/round-31/waves/w1/deliver-records-skeleton.md:163 :: | round-31 capture verify | `<records=<n> failed=0 uncovered=0>` |
R39-C1-05   must0=068f75dc                 whole_tree_must_lines=0 other_file=0
R39-C1-06   must0=r38-citation-commit      whole_tree_must_lines=0 other_file=0
R39-C1-07   must0=5f0dd45                  whole_tree_must_lines=0 other_file=0
R39-C1-08   must0=a7-counter-fixes2.txt    whole_tree_must_lines=0 other_file=0
R39-C1-09   must0=tighter-only             whole_tree_must_lines=0 other_file=0
R39-C1-10   must0=fcdecaa                  whole_tree_must_lines=0 other_file=0
R39-C1-11   must0=LOG-line-1855            whole_tree_must_lines=0 other_file=0
R39-C1-12   must0=LOG-line-1862            whole_tree_must_lines=0 other_file=0
R39-C1-13   must0=QUALITY-line-209         whole_tree_must_lines=0 other_file=0
R39-C1-14   must0=vacuity-operation=mismatches=3 whole_tree_must_lines=0 other_file=0
R39-C1-15   must0=6949319                  whole_tree_must_lines=0 other_file=0
R39-C1-16   must0=in-place                 whole_tree_must_lines=0 other_file=0
```

Item 04's whole `must` set (`records=`, `failed=0`, `uncovered=0`) is already carried verbatim, on
one line each, by two lane files at base — and both are **template** lines, not measurements. That
is only possible because of §5.

Verdict: **FAIL (calibration)** — item 04 is satisfiable by writing a shape it does not measure.

---

## 5. Falsification: `records=` can never match a measured `records=<n>`

`census/round-39/c1-counter.py:86-98` `has_token` requires `before` and `after` to be
non-alphanumeric. Token `records=` ends in `=`; therefore the character *after* it must be
non-alphanumeric. Any filled counter line puts a digit there.

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<import c1-counter.py; call has_token>'
FAIL 'records=' <= 'SUMMARY records=2056 failed=0 uncovered=0'
FAIL 'records=' <= 'SUMMARY records=0 failed=0 uncovered=0'
FAIL 'records=' <= 'SUMMARY: records=2056 failed=0 uncovered=0'
PASS 'records=' <= 'SUMMARY records=| failed=0 uncovered=0'
PASS 'records=' <= 'SUMMARY records= failed=0 uncovered=0'
PASS 'failed=0' <= 'SUMMARY records=2056 failed=0 uncovered=0'
PASS 'uncovered=0' <= 'SUMMARY records=2056 failed=0 uncovered=0'
PASS 'dead=0' <= '- waves=1 dead=0 seated=0'
PASS 'waves=1' <= '- waves=1 dead=0 seated=0'
PASS 'cases=9' <= 'LOG-line-1855 cases=9 fail=6'
FAIL 'cases=9' <= 'LOG-line-1855 cases=90 fail=6'
PASS 'vacuity-operation=mismatches=3' <= 'vacuity-operation=mismatches=3 three-rows'
PASS 'w1-reports=42/42' <= 'w1-reports=42/42,w2-reports=32/32'
PASS '/fast/scratch' <= 'cites-a-revision /fast/scratch'
```

Token-level confirmation on the two base collisions (line lengths 2069 / 66 bytes):

```
round29  has_token(records=)=True  has_token(failed=0)=True  has_token(uncovered=0)=True
         ... prints per round `rN records= failed= uncovered= floor_violation=` ...
round31  has_token(records=)=True  has_token(failed=0)=True  has_token(uncovered=0)=True
         | round-31 capture verify | `<records=<n> failed=0 uncovered=0>` |
```
Both pass only because `=` is followed by a space (`records= failed=`) or by `<`
(`<records=<n>`) — the template forms.

Consequence for the frozen predicate (C1 kills at `open != 0`):
- A truthful line `SUMMARY records=<n> failed=0 uncovered=0` in
  `census/round-39/records/waves-capture.txt` reads **OPEN PREDICATE-MISSING missing=['records=']**
  — item 04 can never close on a measured record.
- The only ways to close it are to write `records=` with nothing after it, `records=|`, or the
  literal template `<records=<n>`, i.e. an **unmeasured shape** — the exact class calibration
  exists to police (r38 R1/R13 stale-literal family).

Verdict: **FAIL (blocker for C1 as frozen)**. Remedies are all outside my write scope: (a) the
items row's must token should be `records=` with the value following a non-word char, (b) the token
should be split (`records` + value) or (c) the row should carry a synthetic line format the record
actually prints. Note the items table is frozen (`census/round-39/*-items.tsv` is do-not-edit), so
this needs an L1 decision, not a seat edit.

Adjacent fragility (not a defect, no action taken): `cases=9` (item 11) and `escapes=9` (item 13)
fail if the landing line writes `cases=9/9`, `cases=90` — the failure demo is quoted above.

---

## 6. Non-contract frontier snapshot (pinned, for the L1 only)

```
$ git rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923
$ python3 -B census/round-39/c1-counter.py --root <lane> --rev 2201778... \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/...
ITEM R39-C1-01 CLOSED   ... ITEM R39-C1-02 CLOSED
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-05 CLOSED ... ITEM R39-C1-16 CLOSED        (12 more CLOSED)
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
$ ls census/round-39/cells.tsv
ls: cannot access 'census/round-39/cells.tsv': No such file or directory
```
Reading (advisory, not a verdict; HEAD is a moving wave target): 14/16 items already close at
2201778; the two open ones are exactly the two collided-anchor record files, and item 04 will stay
open on any measured line per §5. Register file absent → `register_cells=0`, so C1's
`register_cells>=6 register_mismatches=0 commit_distinct>=2` legs are still at zero.

`items_sha=d892b74f8358` is identical here, at base, and in `records/c1-before.txt`: the items table
that the live counter reads is byte-identical to the one the control was taken with. Verdict:
**PASS** — items table not drifted.

---

## Verdict summary

| check | verdict |
|---|---|
| base revision resolves | PASS |
| named-file anchor hits at base = 0 (16/16) | PASS (control `open=16` reproduced; 5 FILE-ABSENT) |
| `must` tokens already on a named-file line at base (vacuity) | PASS (0/16) |
| other-file anchor hits at base | **FAIL for 2/16** — `dead=0` 14 lines/7 files (item 03), `SUMMARY` 7706 lines/1689 files (item 04); 14/16 are 0 |
| anchor uniqueness at landing rev | **impossible by construction** — every anchor also lives in `census/round-39/c1-items.tsv` + `records/c1-before.txt`; exclude both |
| `must` set already present on some other lane line at base | **FAIL for item 04** — template lines `census/round-29/records/preregistration.txt:7`, `census/round-31/waves/w1/deliver-records-skeleton.md:163` |
| item 04 closeable by a measured line | **FAIL** — `has_token('SUMMARY records=2056 ...','records=')=False`; only template/malformed forms close it |
| items table drift (`items_sha`) | PASS (`d892b74f8358` at base, at HEAD and in the control receipt) |

Risks carried to the L1: (1) item 04 is uncloseable-by-measurement unless the frozen row or the
record format is reconciled — writing the template to make it pass would itself be an R1/R13-class
calibration defect; (2) items 03/04 anchors are audit-ambiguous tree-wide, so a wave-2 reviewer
re-deriving the predicate must scope to the named file plus the two mandatory exclusions; (3) the
counter reads the items table from the working tree, not from `--rev`, so `items_sha` is the only
pin — confirm `items_sha=d892b74f8358` in the final SUMMARY.

Scratch retained on disk: `/fast/scratch/hyaku/souji-r39/W1ExecC1Anchors/`
(anchor-census.py, vacuity.py, must-collide.py; every run used `python3 -B` with
`PYTHONDONTWRITEBYTECODE=1`, so no `__pycache__` was created — `ls -la` shows the three `.py` files
only). No lane file written, no git/jj mutation, no tool install.
