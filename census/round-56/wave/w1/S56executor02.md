# S56executor02 — C2 reproduction (souji round 56, wave w1)

Role: executor. Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Measured revision: `cce21b555a617cadda782613ec1e9d3a0c12ac83` (base `fafe371694fea41c5d23f63083865d5ccf3f1d36`).
All claim evidence was read from committed bytes at that revision; no counter, fixture,
builder, expected-TSV or record byte was edited; no git/jj mutation ran; nothing was
committed or pushed. Scratch `/fast/scratch/hyaku/souji-r56/S56executor02/` (deleted before
yield after copying receipts here).

VERDICT: AGREE

All four assigned steps reproduce the frozen C2 claim exactly. No step disagrees.

---

## 0. Frozen pins verified before probing

Command (lane cwd):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum \
  census/round-56/c1-counter.py census/round-56/c2-counter.py \
  census/round-56/fixtures/build-fixtures.py census/round-56/fixtures/run-matrix.sh \
  census/round-56/records/c1-selftest-expected.tsv \
  census/round-56/records/c2-selftest-expected.tsv \
  census/round-55/c1-counter.py census/round-55/c2-counter.py
```

Output (all eight match the pins in `census/round-56/preregistration.txt`; receipt `pins.txt`):

```
975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179  census/round-56/c1-counter.py
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8  census/round-56/c2-counter.py
2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a  census/round-56/fixtures/build-fixtures.py
a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3  census/round-56/fixtures/run-matrix.sh
48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb  census/round-56/records/c1-selftest-expected.tsv
90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3  census/round-56/records/c2-selftest-expected.tsv
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
EXIT=0
```

No mismatch → no stop-and-report condition.

Disk guard before the heavy pass: `/fast/scratch/hyaku` 50% used, 405.5G free; no ENOSPC.

---

## 1. Pinned selftest — PASS

### 1a. Selftest with pins

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor02/ \
python3 -B census/round-56/c2-counter.py --selftest \
  --work /fast/scratch/hyaku/souji-r56/S56executor02/st \
  --builder-sha256 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a \
  --expected-sha256 90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3
```

Output (receipt `selftest.txt`), 18/18 cases pass:

```
SELFTEST-CASE FH-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FH2-SYMLINK-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FA1-UNSORTED pass rc=1 want_rc=1 finding=ROWS-UNSORTED want_finding=ROWS-UNSORTED
SELFTEST-CASE FA2-COMMENT pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA3-TAMPER pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA4-SPACE-NAME pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA5-EXTRA-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA6-CRLF pass rc=1 want_rc=1 finding=CAPTURE-CRLF want_finding=CAPTURE-CRLF
SELFTEST-CASE FA7-RECEIPT-ENTRIES pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA8-SYMLINK-CLASS pass rc=1 want_rc=1 finding=CLASS-MISMATCH want_finding=CLASS-MISMATCH
SELFTEST-CASE FB1-TAB4-ROW pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FB2-LOWER-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FB3-NOSPACE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC1-UNDERSCORE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC2-DIGIT-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FC3-EMPTY-VALUE-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA9-WRONG-TOOL-PIN pass rc=1 want_rc=1 finding=TOOL-SHA-ARG-MISMATCH want_finding=TOOL-SHA-ARG-MISMATCH
SELFTEST-CASE FB4-PIN-SHAPE pass rc=2 want_rc=2 finding=TOOL-SHA-ARG-MALFORMED want_finding=TOOL-SHA-ARG-MALFORMED
SELFTEST pass cases=18
EXIT=0
```

Matches the expected `SELFTEST pass cases=18`, EXIT=0, and pins verified before exec
(a wrong pin would have printed `CANNOT-EVALUATE PIN-MISMATCH` and exited 2).

### 1b. Wrong-tool-pin case through the real capture (T5's negative arm)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor02/ \
python3 -B census/round-56/c2-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev cce21b555a617cadda782613ec1e9d3a0c12ac83 \
  --capture census/round-55/records/fleet-root-census.tsv \
  --receipt census/round-55/records/fleet-root-census-run.txt \
  --tool-sha256 0000000000000000000000000000000000000000000000000000000000000000 \
  --scratch /fast/scratch/hyaku/souji-r56/S56executor02/
```

Output (receipt `wrong-tool-pin.txt`):

```
FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=e7e79952f783
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=FAIL rev=cce21b555a61
EXIT=1
```

Expected `TOOL-SHA-ARG-MISMATCH` and exit 1: reproduced. The observed tool digest
`e7e79952f783…` equals the pinned `e7e79952f7830d75…`, and the 64-zero pin is shape-valid
(64 lowercase hex) so it reaches the mismatch branch rather than `TOOL-SHA-ARG-MALFORMED`.

**Step 1 verdict: AGREE.**

---

## 2. Official matrix — byte-identical

### 2a. Build the fixtures (own git repos inside scratch)

```
cd /fast/scratch/hyaku/souji-r56/S56executor02 && \
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor02 python3 -B \
  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/fixtures/build-fixtures.py \
  --work /fast/scratch/hyaku/souji-r56/S56executor02/selftest
```

49 fixtures built (`C1_FIXTURES` 33 + `C2_FIXTURES` 16, the latter including FC1–FC3),
manifest has 50 lines (header + 49 rows), last lines:

```
BUILT FC2-DIGIT-KEY tip=663ee984eff5560c559876de3de10d60b0777950
BUILT FC3-EMPTY-VALUE-KEY tip=9085035ed77658c654dce9a4e70bf683cd6e2103
MANIFEST /fast/scratch/hyaku/souji-r56/S56executor02/selftest/fixture-manifest.tsv
EXIT=0
```

Host-guard assertion: each fixture is its own repo, e.g.
`git -C /fast/scratch/hyaku/souji-r56/S56executor02/selftest/F1-HONEST-TIP rev-parse --show-toplevel`
printed `/fast/scratch/hyaku/souji-r56/S56executor02/selftest/F1-HONEST-TIP` (EXIT=0). The
builder only mutates inside `<scratch>/selftest/`. Receipt `build-receipt.txt`.

### 2b. Matrix run

```
cd /fast/scratch/hyaku/souji-r56/S56executor02 && \
bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-56/fixtures/run-matrix.sh \
  /fast/scratch/hyaku/souji-r56/S56executor02 /fast/scratch/hyaku/souji-r56/S56executor02
```

Output (`matrix-run.txt`):

```
c1-v4 rc=0
c1-v5 rc=0
c2-v4 rc=0
c2-v5 rc=0
EXIT=0
```

### 2c. Byte comparison

```
for f in c2-matrix-v4.tsv c2-matrix-v5.tsv c1-matrix-v4.tsv c1-matrix-v5.tsv; do
  for ref in <lane>/census/round-56/records/$f <lane>/census/round-56/records/matrix-dryrun/$f; do
    cmp -s <scratch>/$f "$ref" && echo "IDENTICAL $f $ref" || { echo "DIFF ..."; cmp ... ; }
  done
done
```

Output (receipt `matrix-compare.txt`) — all eight comparisons identical, no first-differing
line exists:

```
IDENTICAL c2-matrix-v4.tsv .../census/round-56/records/c2-matrix-v4.tsv
IDENTICAL c2-matrix-v4.tsv .../census/round-56/records/matrix-dryrun/c2-matrix-v4.tsv
IDENTICAL c2-matrix-v5.tsv .../census/round-56/records/c2-matrix-v5.tsv
IDENTICAL c2-matrix-v5.tsv .../census/round-56/records/matrix-dryrun/c2-matrix-v5.tsv
IDENTICAL c1-matrix-v4.tsv .../census/round-56/records/c1-matrix-v4.tsv
IDENTICAL c1-matrix-v4.tsv .../census/round-56/records/matrix-dryrun/c1-matrix-v4.tsv
IDENTICAL c1-matrix-v5.tsv .../census/round-56/records/c1-matrix-v5.tsv
IDENTICAL c1-matrix-v5.tsv .../census/round-56/records/matrix-dryrun/c1-matrix-v5.tsv
EXIT=0
```

sha256 of the reproduced vs committed C2 matrices:

```
d7bf3a720bca0f3196444dbf46167fb67b184dfb4614bdcfb773fcfeb5c90c48  c2-matrix-v4.tsv (scratch)
d7bf3a720bca0f3196444dbf46167fb67b184dfb4614bdcfb773fcfeb5c90c48  records/c2-matrix-v4.tsv (committed)
d8613afdeb0c18897cd453db405ececbf8d964750764b02053c1bbe62df128e6  c2-matrix-v5.tsv (scratch)
d8613afdeb0c18897cd453db405ececbf8d964750764b02053c1bbe62df128e6  records/c2-matrix-v5.tsv (committed)
```

**Step 2 verdict: AGREE (byte-identical, post-freeze == dry-run).**

---

## 3. T1–T3 re-derived from the two committed matrices with plain Python

Script `derive-t1-t3.py` (kept here; splits TSV on tabs, compares the `exit` and `finding`
columns; the counter is not imported or invoked). Run over `records/`, `matrix-dryrun/`, and
the byte-identical reproduced matrix. Full output (`derive-t1-t3.txt`):

```
== records/
rows v4=16 v5=16 same-fixture-set=True
T1 (v4 exit 0, v5 exit != 0): ['FC1-UNDERSCORE-KEY', 'FC2-DIGIT-KEY', 'FC3-EMPTY-VALUE-KEY']
  T1-FINDING FC1-UNDERSCORE-KEY v4-finding=- v5-first-finding=RECEIPT-UNKNOWN-KEY
  T1-FINDING FC2-DIGIT-KEY v4-finding=- v5-first-finding=RECEIPT-UNKNOWN-KEY
  T1-FINDING FC3-EMPTY-VALUE-KEY v4-finding=- v5-first-finding=RECEIPT-UNKNOWN-KEY
T2 (v4 exit != 0, v5 exit 0): EMPTY
T3 carry-over rows=13 mismatches=NONE
all rows whose (exit, first finding) differ: ['FC1-UNDERSCORE-KEY', 'FC2-DIGIT-KEY', 'FC3-EMPTY-VALUE-KEY']
rc=0
== matrix-dryrun/
[identical output to records/, same T1/T2/T3]
rc=0
== reproduced scratch (byte-identical re-run)
[identical output, same T1/T2/T3]
rc=0
EXIT=0
```

Exactly the frozen predicates:

- T1 = `{FC1-UNDERSCORE-KEY, FC2-DIGIT-KEY, FC3-EMPTY-VALUE-KEY}`, first finding
  `RECEIPT-UNKNOWN-KEY` on each (v4 first finding `-`, i.e. exit 0 with no finding).
- T2 = empty (no narrowing regression).
- T3 = the other 13 rows have identical exit code and identical first finding under v4/v5.

Corroborating shape check of the three mutant receipts (committed fixture bytes, `git show`;
receipt `mutant-receipt-shapes.txt`) — each carries exactly the named unknown-key shape:

```
FC1: # _BUILDHOST=fixture      (underscore-initial key)
FC2: # 1BUILDHOST=fixture      (digit-initial key)
FC3: # BUILDHOST=             (unknown key, empty value)
```

Matrix kill rows (`matrix-kill-rows.txt`): v4 exits 0 with no finding on all three; v5
exits 1 with `RECEIPT-UNKNOWN-KEY` on all three; `FH-HONEST` and `FH2-SYMLINK-HONEST` exit 0
under both (honest-handling control intact).

**Step 3 verdict: AGREE.**

---

## 4. Real lane, v5 counter — exit 0, SUMMARY byte-equal to the committed tip

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
TMPDIR=/fast/scratch/hyaku/souji-r56/S56executor02/ \
python3 -B census/round-56/c2-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev cce21b555a617cadda782613ec1e9d3a0c12ac83 \
  --capture census/round-55/records/fleet-root-census.tsv \
  --receipt census/round-55/records/fleet-root-census-run.txt \
  --tool-sha256 e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b \
  --scratch /fast/scratch/hyaku/souji-r56/S56executor02/
```

Output (`real-lane-v5.txt`):

```
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=cce21b555a61
EXIT=0
```

Byte comparison of the SUMMARY line against `census/round-56/records/c2-tip.txt` line 1
(`tip-compare.txt`): `SUMMARY-BYTES-IDENTICAL` (EXIT=0). The committed tip file carries its
own `EXIT=0` line as line 2 (it is a 2-line receipt), so the comparison excludes that line —
see observation O3.

**Step 4 verdict: AGREE.**

---

## 5. Per-step verdicts

| Step | Content | Result |
|---|---|---|
| 1a | pinned selftest | `SELFTEST pass cases=18`, EXIT=0 → **AGREE** |
| 1b | wrong tool pin through real capture | `TOOL-SHA-ARG-MISMATCH`, EXIT=1 → **AGREE** |
| 2 | official matrix vs committed + dry-run | 4/4 C2 and 4/4 C1 comparisons byte-identical, no differing line → **AGREE** |
| 3 | T1–T3 by plain Python | T1 exact 3-row set with `RECEIPT-UNKNOWN-KEY`, T2 empty, T3 13/13 identical → **AGREE** |
| 4 | real lane v5 | exit 0, SUMMARY byte-equal to `c2-tip.txt` → **AGREE** |

---

## 6. Observations (named, not fixes; frozen bytes untouched)

- **O1 — matrix runner rc lines are function status, not counter exits.**
  `run-matrix.sh` runs under `set -u` (no `-e`, no `pipefail`) and `c2_arm()` ends in a
  `while` loop whose status is its last `printf`; the printed `c2-v4 rc=0` / `c2-v5 rc=0`
  therefore do not assert that every counter invocation exited 0. They are reproduced here
  exactly as the frozen script emits them; the authoritative per-fixture exit code is the
  TSV `exit` column, which is what step 3 compares. Reading risk only, no predicate fails.
- **O2 — matrix `finding` column is id-only.** The unknown-key detail lives in the counter's
  `FINDING RECEIPT-UNKNOWN-KEY receipt carries unknown key <K>` stdout line, not in the
  matrix column. The three shapes were confirmed directly from committed fixture bytes
  (step 3c), so the T1 attribution is independent of the extractor.
- **O3 — `c2-tip.txt` is a 2-line receipt.** Line 1 is SUMMARY, line 2 is `EXIT=0`; the
  "SUMMARY byte-equal (EXIT excluded)" check is therefore line-1 equality, which passed.
- **O4 — docstring residue.** The v5 docstring's SELFTEST-ROW-MISMATCH paragraph mentions
  `SELFTEST pass cases=14` as the historical v4 count while the frozen selftest runs 18
  cases. Cosmetic only; no predicate or assertion reads that sentence.
- **O5 — documented first-key limit.** The counter reports only the FIRST unknown receipt
  key (its own named limit). FC1–FC3 each carry a single unknown key, so the limit does not
  blur the T1 attribution.

No counter/fixture defect was found within this seat's assigned predicates; nothing is
routed to r57 from this seat.

Risks/blockers: none. No tool installs were made (no `pacman`, `uv`, `npx` or binary
install). No writes outside the seat dir and scratch; no git state changed. The main agent
owns post-integration gates; this seat ran only the assigned reproduction steps.

---

## 7. Receipt index (all in this seat dir, each ending with `EXIT=<rc>`)

- `pins.txt` — sha256 of the eight frozen pins
- `selftest.txt` — step 1a full output
- `wrong-tool-pin.txt` — step 1b full output
- `build-receipt.txt` — fixture build log + manifest line count
- `matrix-run.txt` — step 2b runner output
- `matrix-compare.txt` — step 2c byte comparisons
- `derive-t1-t3.py`, `derive-t1-t3.txt` — step 3 plain-Python derivation
- `mutant-receipt-shapes.txt` — committed receipt lines for FC1–FC3
- `matrix-kill-rows.txt` — v4/v5 rows for FC1–FC3 and the honest controls
- `real-lane-v5.txt` — step 4 full output
- `tip-compare.txt`, `real-summary.txt` — SUMMARY byte comparison
- `c2-matrix-v4.tsv`, `c2-matrix-v5.tsv` — reproduced matrices (byte-identical to committed)
