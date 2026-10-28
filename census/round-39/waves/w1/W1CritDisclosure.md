# W1CritDisclosure — souji round 39 wave 1, critic (disclosure of measurement limits)

Role: critic. Assignment: read the three counters and enumerate every limit their measurement
carries; say for each whether the round can close it or must name it in the report's limits;
produce the disclosure list the report must carry, with the receipt/line that proves each.

Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
lane base `ed30b7f5b77939c9073348d810730bc4f355708d`). Lane head moved during this review:
`2201778e…` (14:58) → `d4c17557b92fd98044e4c8f0ddc79c6d75701b15` (15:08, "C3/scratch — honour the
caller's TMPDIR"). Two instruments changed under me while I measured; that is itself finding D3.

Lane root used everywhere: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Scratch: `/fast/scratch/hyaku/souji-r39/W1CritDisclosure` (removed at the end — see §6).
No lane byte, no frozen receipt, no counter, no fixture was written or edited by this seat.
Every git command below is read-only (`log`, `show`, `rev-parse`, `diff`, `status`, `ls-tree`,
`cat-file`, `merge-base` inside the tools).

---

## 1. Checks run (command → output → verdict)

### X1 — which bytes are the instruments?

```
for f in census/round-39/c1-counter.py census/round-39/c2-counter.py census/round-39/c3-counter.py \
         tests/fixtures/r39-citation-rev.py tests/fixtures/r39-drift-record-rules.py; do
  printf '%-45s freeze=%s 2201778=%s head=%s wt=%s\n' "$f" \
    "$(git show b769bfb:$f|sha256sum|cut -c1-12)" "$(git show 2201778:$f|sha256sum|cut -c1-12)" \
    "$(git show HEAD:$f|sha256sum|cut -c1-12)" "$(sha256sum $f|cut -c1-12)"; done
```

```
census/round-39/c1-counter.py                 freeze=f908590d4623 2201778=f908590d4623 head=f908590d4623 wt=f908590d4623
census/round-39/c2-counter.py                 freeze=326caa162246 2201778=326caa162246 head=326caa162246 wt=326caa162246
census/round-39/c3-counter.py                 freeze=ff18d64c09f4 2201778=ff18d64c09f4 head=7f934c50b19a wt=7f934c50b19a
tests/fixtures/r39-citation-rev.py            freeze=c142c1bc28b8 2201778=7ab7c3d85a81 head=e555d8281484 wt=e555d8281484
tests/fixtures/r39-drift-record-rules.py      freeze=567c37a679f5 2201778=567c37a679f5 head=567c37a679f5 wt=567c37a679f5
```

Verdict: **WARN** — c1/c2 counters and the C3 candidate fixture are still the freeze bytes; the C3
counter and the C2 fixture changed after freeze, and the C2 fixture changed *twice* (c142c1bc →
7ab7c3d8 → e555d828). `census/round-39/records/c2-after.txt` records `fixture_sha=7ab7c3d85a81`,
bytes that now exist at no revision (`git rev-parse 2201778:…r39-citation-rev.py` = `c072ebe`,
`git rev-parse HEAD:…` = `deadfd1`). The C2 after-receipt therefore cannot be re-derived from any
commit; it can only be re-derived by re-running the counter today, which prints a different sha.

### X2 — C1 control reproduces at the base revision

```
python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv \
  --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1CritDisclosure/c1base
```

```
ITEM R39-C1-14 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-14'
ITEM R39-C1-15 OPEN FILE-ABSENT corpus/lessons/round-39.md
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

Verdict: **PASS as a control** (matches `c1-before.txt` byte for byte, same `items_sha`), but see
D1/D5/D6: the control's sensitivity is marker-presence, and the register arm reports a clean
`mismatches=0` while the register does not exist.

### X3 — C1 at the then-head (2201778)

```
python3 -B census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2201778e7736af82e7d8a42dec2494f115bf3923 --items census/round-39/c1-items.tsv \
  --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1CritDisclosure/c1head
```

```
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
… (14 ITEM … CLOSED)
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

Verdict: **C1 is not met at head** — `open=2`, `register_cells=0` (`census/round-39/cells.tsv` does
not exist: `ls census/round-39/cells.tsv` → `No such file or directory`). This is pending work, not
a defect, but the report must not present C1 as measured until both are closed.

### X4/X5/X6 — C2 control, after-reproduction, and re-measure after the fixture moved

```
python3 -B census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch …/c2base
```
```
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=e555d8281484
rc=1
```
```
python3 -B census/round-39/c2-counter.py --root … --rev 2201778e… --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch …/c2head
```
```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc=0
```
```
python3 -B census/round-39/c2-counter.py --root … --rev d4c17557b92fd98044e4c8f0ddc79c6d75701b15 --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch …/c2d4
```
```
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
rc=0
```

Verdict: **PASS for C2** at both heads (control `pass=2`, so the do-nothing state is excluded), with
one live demonstration of D2: the same counter at `--rev 2201778` printed `fixture_sha=7ab7c3d85a81`
at 15:04 and `fixture_sha=e555d8281484` at 15:12, because the fixture was read from the worktree
(`census/round-39/c2-counter.py:64` says so in prose; `:170`, `:237`, `:253` do it).

### X7 — C3 at the base revision with the frozen candidate fixture

```
python3 -B census/round-39/c3-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --scratch …/c3base
```
```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
rc=0
```

Re-run with the current (post-freeze) counter bytes at 15:2x — identical SUMMARY, `rc=0`:

```
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
```

Verdict: **FAIL of the round's control frame** — the frozen C3 predicate
(`mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`, exit 0) is reached at the *base*
revision. Only `tool_sha` differs from the after reading. C3's predicate is revision-insensitive: the
mutants are applied to whatever tool bytes `--rev` names, and the candidate fixture asserts
behaviours the base tool already has (`pristine=ok` at base). The prereg's blanket sentence "Every
claim below is one a do-nothing control cannot reach" is false for C3 as written. This is not a
defect of the coverage claim itself — the fixture really does kill four mutants — but it is a limit
the report must name, because the counter cannot distinguish "fixture written" from "tool repaired".

### X8/X10 — C3 after-reproduction at 2201778 and at d4c1755

```
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5   (rc=0, both heads)
```

Verdict: **PASS**, and the reading matches `census/round-39/records/c3-after.txt` exactly (same
`tool_sha`, `fixture_sha`, `cases`).

### X9 — what produced `c3-before.txt`?

```
python3 -B census/round-39/c3-counter.py --root … --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r38-drift-record.py \
  --scratch …/c3before
```
```
MUTANT M11 killed=no base_killed=no rc=0 fails=0 crash=False base:rc=0 fails=0 crash=False
… (M12, M13, M14 identical shape)
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=14e9c0f77d7e fixture_sha=ac0be0e7a49e
rc=1
```

`sha256sum tests/fixtures/r38-drift-record.py` → `ac0be0e7a49e683cd324ffa4…` — the committed
control's `fixture_sha` is the **base** fixture's sha256, not the frozen candidate's
(`567c37a679f5`). Verdict: **FAIL of the control's identity** — `c3-before.txt` is not a reading of
the frozen candidate at the base revision; it is the base fixture scored against itself (both arms
identical). It still proves "the r38 fixture leaves the four mutants alive", which is what
`base_killed=0` already says in every after-row, but it does not prove the control the prereg names,
and it omits its command string so the swap is invisible unless the sha is checked.

### X11 — kill attribution (are four mutants four behaviours?)

Mutants applied to `git show 2201778:tools/souji-worktree-drift.py`, then
`python3 -B tests/fixtures/r39-drift-record-rules.py --tool <mutant> --work <scratch>`:

```
pristine candidate: (0, [], 'SUMMARY cases=7 pass=7 fail=0')
pristine base-fixture: (0, [], 'SUMMARY cases=10 pass=10 fail=0')
M11 candidate: (1, ['trailing-space'], 'SUMMARY cases=7 pass=6 fail=1')
M12 candidate: (1, ['crlf'], 'SUMMARY cases=7 pass=6 fail=1')
M13 candidate: (1, ['outside-root'], 'SUMMARY cases=7 pass=6 fail=1')
M14 candidate: (1, ['indented-comment'], 'SUMMARY cases=7 pass=6 fail=1')
M11..M14 base-fixture: (0, [], 'SUMMARY cases=10 pass=10 fail=0')
```

Verdict: **PASS, and this closes the attribution limit** — kills are 1:1 with four distinct cases.
But the counter itself does not attribute (`census/round-39/c3-counter.py:102` accepts any
`fails>0`), so the report must carry this table or the claim "four behaviours covered" is unproven.

### X12 — "every existing drift fixture leaves them alive"

Each pre-round drift fixture run against pristine + M11..M14:

```
r36-worktree-drift         rc0 12/12 | 12/12 | 12/12 | 12/12 | 12/12
r37-drift-discrimination   rc0  6/6  |  6/6  |  6/6  |  6/6  |  6/6
r37-drift-escapes          rc0 12/12 | 12/12 | 12/12 | 12/12 | 12/12
r38-drift-record           rc0 10/10 | 10/10 | 10/10 | 10/10 | 10/10
r38-drift-write-envelope   rc0 12/12 | 12/12 | 12/12 | rc1 11/12 | 12/12
```

and the failing case, isolated:

```
case-record-outside-root=FAIL rc=1 out=['DRIFT\tABSENT\t../escaped\trecorded regs=1', 'DRIFT\tUNRECORDED\talpha\tlive regs=1 prunable=0']
SUMMARY cases=12 pass=11 fail=1
```

Verdict: **FAIL of the prereg sentence** ("Four single-defect mutants … survive every existing
fixture"): M13 is killed by `tests/fixtures/r38-drift-write-envelope.py`, a pre-round fixture that
`census/round-39/c2-counter.py:57` itself enumerates as a consumer. Independent reproduction of
`W1CritC3Axis.md` (same finding, same case). `base_killed=0` is an artefact of `--base-fixture`
defaulting to the single file `r38-drift-record.py` (`c3-counter.py:125`, `:174`).

### X13 — item R39-C1-04's `must` token `records=` and the whole-token rule

`has_token` from `c1-counter.py:86-100` applied to the natural SUMMARY forms:

```
'SUMMARY records=12 failed=0 uncovered=0' -> False
'SUMMARY records= failed=0 uncovered=0' -> True
'SUMMARY records=\nfailed=0' -> True
'SUMMARY records=0 failed=0 uncovered=0' -> False
```

Verdict: **FAIL as an authoring trap** — `census/round-39/c1-items.tsv` row `R39-C1-04` requires
`records=,failed=0,uncovered=0`; a SUMMARY line that states the count in the natural
`records=<N>` form reads OPEN, and only `records=` followed by whitespace (value omitted or
space-separated) closes it. The item is frozen and cannot be edited.

### X14 — L5 per-case discrimination

```
base tool arm:  case-rev-unknown=FAIL case-rev-blob=FAIL case-rev-tree=FAIL case-register-rev-gone=FAIL
                SUMMARY cases=8 pass=4 fail=4
head tool arm:  all 8 PASS   SUMMARY cases=8 pass=8 fail=0
```

Verdict: **PASS** — 4 of 8 cases discriminate; 4 (`rev-short`, `rev-symbolic`, `clean`,
`register-absent`) pass on both arms and are controls, not evidence.

### X15 — uid dependence of the C2 EACCES leg

```
sudo -n env TMPDIR=… python3 -B census/round-39/c2-counter.py --root … --rev 2201778e… --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
```
```
REFUSAL COULD-NOT-EVALUATE: --rev 2201778e7736af82e7d8a42dec2494f115bf3923 does not resolve
rc=2
```

Verdict: **WARN** — under uid 0 the counter refuses at revision resolution (git `safe.directory`
neutralised by the whitelist env), and even if it could read, `os.chmod(probe, 0)` would not produce
EACCES. Receipts are reproducible only by uid 1000 (`id -u` → `1000`).

### X16 — item R39-C1-01's numbers and the receipts

```
grep -rn "rows=170\|added=8\|W04=47" census/round-39/ | grep -v c1-items
census/round-39/records/census-before.txt:4:rows=170
census/round-39/records/census-before.txt:5:W04=47
census/round-39/records/census-after.txt:4:W04=47
```
`census-after.txt` also carries `rows=173`; `census-before.txt` carries no SUMMARY line and its own
note says its E11 count is a scratch artefact. Verdict: **WARN** — `SOURCES-added=8` is carried by
no committed receipt, and `170 + 8 ≠ 173`, so the closed line's arithmetic is not re-derived
anywhere the register arm can reach.

---

## 2. The disclosure list the report must carry

Format: **D#** limit → proof → closable this round? → smallest correction.

**D1 — The instruments are read from the worktree, not from the audited revision.**
C1: `c1-counter.py:196` `open(args.items, …)` (item catalogue), and the counter's own bytes.
C2: `c2-counter.py:64` ("Instrument (fixture) bytes come from the working tree"), `:170`, `:237`,
`:253` (candidate fixture + five consumer fixtures); `fixture_sha` covers only
`r39-citation-rev.py`.
C3: `c3-counter.py:124-125` `open(args.fixture)` / `open(args.base_fixture)`.
*Closable:* no (the counters are frozen and revision-bound tool bytes only). *Correction:* the
report must print the sha256 of every instrument it used — counters, `c1-items.tsv`, `cells.tsv`,
both fixtures, the five consumers — and state that only the tool/receipt/register arms are
revision-bound.

**D2 — The C2 instrument has already drifted inside this wave; the after-receipt is unreproducible.**
Proof: `census/round-39/records/c2-after.txt` `fixture_sha=7ab7c3d85a81`; that byte-string exists at
no revision (`2201778` → blob `c072ebe`, `HEAD d4c1755` → blob `deadfd1`; sha256 today
`e555d8281484`). Live observation: the same counter at `--rev 2201778` printed `fixture_sha=7ab7c3d85a81`
at 15:04 and `e555d8281484` at 15:12 (X4/X5/X6).
*Closable:* yes, by re-running C2 at the landing revision and quoting the sha the run actually used.
*Correction:* the report must carry the re-run's `fixture_sha` and say the committed
`c2-after.txt` was measured on superseded fixture bytes (A1 class change + the later `TMPDIR`
child-env change, `git diff b769bfb HEAD -- tests/fixtures/r39-citation-rev.py`).

**D3 — Two instruments changed after the freeze.**
Proof: X1 — `c3-counter.py` `ff18d64c09f4 → 7f934c50b19a` (env/TMPDIR only, per
`git diff b769bfb HEAD -- census/round-39/c3-counter.py`), `r39-citation-rev.py`
`c142c1bc28b8 → 7ab7c3d85a81 → e555d8281484`. Both committed receipts (`c2-after`, `c3-after`) were
produced by the freeze bytes.
*Closable:* yes for the reading (re-run reproduces `pass=6` / `killed=4`); no for the receipts.
*Correction:* the report must state, per counter, the sha that produced each receipt and the sha it
re-ran, and that the deltas are env-only (C3) / case-class + env (C2).

**D4 — Author-chosen anchors (C1).**
Proof: `c1-items.tsv` — 14 of 16 anchors are marker ids (`R39-C1-01` … `R39-C1-16`) that the fix
itself introduces; `c1-counter.py:212-222` closes an item on *any* one line containing the anchor
plus the author's `must` tokens. The base control's `open=16` is therefore guaranteed by
construction (the markers cannot exist at base).
*Closable:* no. *Correction:* the report must say C1 measures "one anchored line carries these
tokens", not "the defect is repaired", and must cite that the token sets were frozen at `b769bfb`
before the corrections landed (`c1-items.tsv` sha `d892b74f8358` in both the control and today's
run) — that is the only mitigation, and it must be stated as the mitigation, not as proof.

**D5 — `register_mismatches=0` is printed when the register does not exist.**
Proof: X3 — `REGISTER cells=0 mismatches=0 commit_distinct=0` with `cells.tsv` absent;
`c1-counter.py:155` returns `(0, 0, "REGISTER-ABSENT")` and the summary prints the 0.
*Closable:* yes. *Correction:* the report must never quote `register_mismatches=0` without
`register_cells=`; and it must state that at the audited head the register did not exist.

**D6 — `commit_distinct` is a row count, not a commit count, and the floor is 2 of 6.**
Proof: `c1-counter.py:129-147` counts rows whose 8th field differs from `receipt_rev`;
`make-cells.py` writes the same `args.commit` into every row, so the value is 1 distinct commit even
when the count is 6; the frozen floor is `>=2` (`--min-commit-distinct` default 2).
*Closable:* yes. *Correction:* the report must print the distinct commit *values* (expected: one),
the two receipt revs, and whether `--commit` differs from `--rev`; if `--commit == --rev` the commit
arm is degenerate and must be said to be.

**D7 — The register's cell count is the tool's count, never cross-checked.**
Proof: `c1-counter.py:156` computes `cells` from the register blob, `:230` overwrites it with the
reconciler's `SUMMARY cells=`; the two are never compared.
*Closable:* yes. *Correction:* the report must state that `register_cells` is the reconciler's count
and quote the register's own row count beside it.

**D8 — Item R39-C1-04's predicate rejects the natural value form.**
Proof: X13 — `records=<digits>` does not satisfy the whole-token rule; only `records=` followed by
whitespace does.
*Closable:* only by writing a line whose `records=` carries no value (or a space-separated value).
*Correction:* the report must quote the exact closing line and explain the spacing, or declare C1
missed; a reader must not be left thinking the counter accepted `records=12`.

**D9 — Items R39-C1-03/04 target files that do not exist, so C1 is unmet at head.**
Proof: X3 — `open=2`, both `FILE-ABSENT`; `git ls-tree HEAD census/round-39/records/` lists only the
three `-before.txt` receipts.
*Closable:* yes, by landing the two wave receipts. *Correction:* the report must not state C1's
predicate until `open=0` is observed.

**D10 — Item R39-C1-01's numbers are not carried by any receipt the register arm can reach.**
Proof: X16 — no committed SUMMARY line carries `SOURCES-added=8`; `census-before.txt` carries
`rows=170`/`W04=47` but no SUMMARY; `census-after.txt` carries `rows=173`. `170+8 ≠ 173`.
*Closable:* no (the counter checks lines, not arithmetic). *Correction:* the report must reconcile
170/8/173 in one sentence or mark the item as a token-only closure.

**D11 — C3's predicate is reachable at the base revision.**
Proof: X7 — `--rev ed30b7f` prints the frozen SUMMARY verbatim and exits 0; only `tool_sha` differs
(`14e9c0f77d7e` vs `e48ed08e6728`). Mutation testing is revision-independent by construction.
*Closable:* no, without changing the frozen counter. *Correction:* the report must say C3's control
is *fixture-swapped*, not revision-controlled, and must not claim "a do-nothing control cannot
reach" for C3.

**D12 — `c3-before.txt` is a reading of the base fixture, not of the frozen candidate.**
Proof: X9 — `fixture_sha=ac0be0e7a49e` = `sha256(tests/fixtures/r38-drift-record.py)`; reproduced
exactly by passing `--fixture tests/fixtures/r38-drift-record.py --base-fixture
tests/fixtures/r38-drift-record.py`. The receipt carries no command string.
*Closable:* yes, by restating what the receipt measured. *Correction:* the report must name the
control's instrument (the r38 fixture) and say the control's purpose is the *fixture* swap; the
candidate fixture's own base reading is `killed=4`, which is D11.

**D13 — Mutant selection bias (C3), and one mutant is not new coverage.**
Proof: X12 — M13 is killed by the pre-round `r38-drift-write-envelope.py`
(`case-record-outside-root`), so "every existing fixture leaves them alive" holds for M11/M12/M14
only. X11 — kills are 1:1 with four cases, but 3 of 7 cases (`good`, `total-before-rows`,
`comments-total-only`) assert behaviours no mutant targets; the mutant set is author-chosen (4 of
the documented record behaviours; the r38 battery adds 4 more).
*Closable:* partly (attribution: X11; the base-fixture quantifier: measure the whole set).
*Correction:* the report must record M13 as already covered by a pre-round fixture, must not call
it a new coverage gap, and must state that coverage is 4 mutants over an author-chosen behaviour
list, not a ratio.

**D14 — Fixture case counts are floors/equalities, not coverage measures.**
Proof: `c2-counter.py:244` requires `new_f[0] == 8` exactly (4 discriminating, X14);
`c3-counter.py:157` requires `cases >= 6` and the run reports `cases=7` (4 kill-attributed, X11).
*Closable:* no. *Correction:* the report must give the discriminating-case count beside each case
count.

**D15 — C2's L3 is exit-code-only; `classify` is first-match over a substring set; L4 is a wording
check.**
Proof: `c2-counter.py:213` (`leg("L3", ok, "new rc=%d old rc=%d")` — no class); `:125-131` fixed
priority `RECORD-MISSING` → `RECORD-MALFORMED` → … over `stdout+stderr`; `:133-143` requires the
class token to *start* a stripped docstring line and requires the literal string `EACCES`.
*Closable:* no. *Correction:* the report must say L3 proves "exit 2 for both revisions" only, that
L4 proves the docstring *wording* maps to the observed class, and that the class names stay
counter-intuitive (a missing file reports `RECORD-MALFORMED`, an EACCES file reports
`RECORD-MISSING` — `c2-after.txt` L4 line: `missing=RECORD-MALFORMED locked=RECORD-MISSING`).

**D16 — C2's consumer leg cannot see a weakened consumer fixture.**
Proof: `c2-counter.py:253` reads the consumer from the worktree for *both* arms, so both arms use
identical bytes; `:265-270` compares pass counts only.
*Closable:* no. *Correction:* the report must state that L6 proves the repaired tools keep the
current consumer fixtures green, not that the consumer fixtures are unchanged from base; the
consumer shas must be quoted.

**D17 — Receipts are reproducible only by uid 1000.**
Proof: X15 — as uid 0 the counter refuses (`REFUSAL COULD-NOT-EVALUATE … does not resolve`), and the
EACCES probe would not produce EACCES anyway.
*Closable:* no. *Correction:* the report must state the uid and filesystem class the receipts were
measured on.

**D18 — No counter hashes itself.**
Proof: C1 prints `items_sha` only; C2/C3 print `tool_sha`/`fixture_sha` only; none prints its own
sha256 (X1 shas had to be computed by hand).
*Closable:* yes. *Correction:* the report must print `f908590d4623`, `326caa162246`,
`7f934c50b19a` (or the sha it actually ran) and say whether each equals the freeze byte-string.

---

## 3. Ready-to-paste "Named limits" block for the round-39 report

> **Named limits of the r39 measurement.**
> (1) *Instrument binding.* The three counters read their item catalogue (C1), their fixtures and
> consumer fixtures (C2), and both fixtures (C3) from the worktree, not from `--rev`; only the
> audited tool bytes, the register blob (`--register-rev`) and the receipts are revision-bound.
> Counter/fixture sha256 quoted in this report pin the instrument; nothing else does.
> (2) *Instrument drift.* `tests/fixtures/r39-citation-rev.py` changed twice after the freeze
> (`c142c1bc` → `7ab7c3d8` → `e555d828`); `census/round-39/records/c2-after.txt` cites `7ab7c3d8`,
> which exists at no revision. `census/round-39/c3-counter.py` changed once (`ff18d64c` →
> `7f934c50`, env-only). Both after-receipts were produced by freeze bytes; the readings re-run
> under the current bytes are quoted beside them.
> (3) *C1 is a token-presence oracle.* Each of the 16 items closes on one author-chosen anchored
> line carrying author-chosen tokens; 14 anchors are marker ids introduced by the correction
> itself, so the base control's `open=16` is structural. The token sets were frozen before the
> corrections (items sha `d892b74f8358`), which is the mitigation, not a proof of repair.
> (4) *C1's register arm.* `commit_distinct` counts rows whose `commit` differs from `receipt_rev`
> (floor 2 of 6); it is not a distinct-commit count, and the generator writes one commit into every
> row. `register_mismatches=0` is printed even when the register is absent (`cells=0`), so the
> cell count must always be quoted with it. The register's cell count is the reconciler's, never
> cross-checked against the register's own row count.
> (5) *C1 items 03/04.* Both target wave receipts that did not exist at the audited head
> (`open=2`); item 04's `records=` token cannot match `records=<N>` under the whole-token rule, so
> its closing line must be read with its spacing in mind.
> (6) *C3's control is fixture-swapped, not revision-controlled.* The frozen C3 predicate is
> reached at `ed30b7f` with the frozen candidate (`killed=4`, exit 0); only `tool_sha` differs.
> `c3-before.txt` was measured with `--fixture tests/fixtures/r38-drift-record.py`
> (`fixture_sha=ac0be0e7a49e`), i.e. the base fixture scored against itself.
> (7) *C3's mutant set.* Four author-chosen mutants; M13 is already killed by the pre-round
> `tests/fixtures/r38-drift-write-envelope.py` (`case-record-outside-root`), so it is not a new
> coverage gap. Kills are 1:1 with four distinct cases (measured here), but the counter does not
> attribute them and three of seven cases target no mutant.
> (8) *C2 wording/exit-code legs.* L3 proves exit 2 only; L4 proves the docstring wording maps to
> the observed class, and the class names remain counter-intuitive (missing → `RECORD-MALFORMED`,
> EACCES → `RECORD-MISSING`). L6 uses the same worktree consumer bytes in both arms, so it cannot
> detect a weakened consumer fixture.
> (9) *Case counts are floors.* L5 requires exactly 8 cases (4 discriminating); C3 requires
> `cases>=6` (7 present, 4 kill-attributed).
> (10) *Environment.* Receipts are reproducible only as uid 1000 on a permission-enforcing
> filesystem; as uid 0 the C2 counter refuses at revision resolution.

---

## 4. Verdicts

| Check | Verdict |
|---|---|
| X1 instrument identity | **WARN** — C3 counter and C2 fixture drifted after freeze; C2 fixture drifted twice |
| X2 C1 base control | **PASS** (matches `c1-before.txt`) — sensitivity is marker-structural (D4) |
| X3 C1 at head | **NOT MET** — `open=2`, `register_cells=0` |
| X4 C2 base control | **PASS** — `pass=2 fail=4` (do-nothing excluded) |
| X5 C2 at 2201778 | **PASS** — `pass=6`, `fixture_sha=7ab7c3d85a81` |
| X6 C2 at d4c1755 | **PASS** — `pass=6`, `fixture_sha=e555d8281484` (instrument moved) |
| X7 C3 at base | **FAIL of the control frame** — frozen predicate reached at `ed30b7f`, exit 0 |
| X8/X10 C3 after | **PASS** — matches `c3-after.txt` |
| X9 `c3-before` identity | **FAIL** — measured with the base fixture as candidate |
| X11 kill attribution | **PASS** — 1:1, four distinct cases |
| X12 existing-fixture sweep | **FAIL of the prereg sentence** — M13 killed by `r38-drift-write-envelope` |
| X13 item-04 token | **FAIL as an authoring trap** — `records=12` reads OPEN |
| X14 L5 per-case | **PASS** — 4 of 8 discriminate |
| X15 uid 0 | **WARN** — refuses at revision resolution |
| X16 item-01 receipts | **WARN** — `SOURCES-added=8` in no SUMMARY; `170+8 ≠ 173` |

Smallest safe corrections the L1 can apply without touching frozen bytes: re-run C2 and C3 at the
landing revision and quote the shas the runs actually used (D2, D3, D18); state C3's control as a
fixture swap and record M13 as pre-round coverage (D11, D13); quote `register_cells` beside
`register_mismatches` and the distinct commit values beside `commit_distinct` (D5, D6); and carry
§3 verbatim as the report's named limits. Nothing here requires editing
`preregistration.txt`, `c1-items.tsv`, a counter, a fixture or a frozen receipt.

## 5. Counterexamples tested (and what survived)

1. *Can the do-nothing revision reach a frozen predicate?* Yes — C3 (X7), exit 0 at `ed30b7f`.
   Not fixable inside the frozen bytes; must be disclosed (D11).
2. *Is M13 unasserted by every existing fixture?* No — `r38-drift-write-envelope` kills it (X12).
   Claim text must shrink to M11/M12/M14 (D13).
3. *Is `c3-before.txt` a candidate-fixture reading?* No — its `fixture_sha` is the base fixture's
   (X9). The receipt must be described as the instrument swap it is (D12).
4. *Does a post-freeze worktree edit change a verdict at fixed `--rev`?* Yes, observed live for C2
   (X4/X5/X6, D2).
5. *Can item R39-C1-04 be closed with a normal SUMMARY line?* No (X13, D8).
6. *Is the commit arm real?* Yes — a row whose `commit` does not carry the receipt is refused
   (`tools/souji-citation-reconcile.py:214-243`, `COMMIT-RECEIPT-ABSENT`), so `commit_distinct` is
   not decorative; the limit is its floor and its single-value generator (D6), not its existence.

## 6. Scratch

`/fast/scratch/hyaku/souji-r39/W1CritDisclosure` was created for this review and removed at the end
(`rm -rf`); no tree of mine remains on disk. `/tmp` was not used. No tool was installed or upgraded
during this item.
