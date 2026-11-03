# S54mutation01 — kill-power audit of the r54 v3 counters (mutation tester)

Round 54, wave w1. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Seat dir `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-54/w1/S54mutation01/`.
Scratch `/fast/scratch/hyaku/souji-r54/S54mutation01/` (deleted at end; receipts copied here first).

Frozen inputs read first: `census/round-54/preregistration.txt` at freeze commit
`3c394cab0cd406bbab72b8d365e0f3deed4ef98a`. No lane byte was edited; every mutant is a
scratch copy. No tools installed (system `python3`, `git` only).

## 0. Pinned bytes, verified before and after the sweep

```
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  records/c1-selftest-expected.tsv
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  records/c2-selftest-expected.tsv
```

Observed before the sweep **and** after it (unchanged): both counters are the prereg pins.
Lane `git status --porcelain` and `HEAD=bfdbb336329e6afba3ab1ca83cbd6d9759271062` are
identical before/after (`receipts/lane-porcelain-after.txt`: the L1's same 8 untracked
`census/round-54/records/*` files). Nothing else written outside the seat dir, with one
disclosed transient: the branch probe imported the lane's `c1-counter.py` as a module, which
made CPython write `census/round-54/__pycache__/c1-counter.cpython-314.pyc` (mtime 17:42). It
was removed immediately (`rm -f …pyc && rmdir …/__pycache__`); `census/round-54/` ends with no
`__pycache__`, `git status --porcelain` is unchanged, and no counter byte was affected.

## 1. Baseline (pristine bytes, same detector)

Detector = the counter's own committed selftest (`--selftest --work DIR --expected <pinned TSV>`),
run on a scratch mirror that keeps the counter's `HERE/fixtures` and `HERE/records` layout.

```
python3 -B <mirror>/census/round-54/c1-counter.py --selftest --work W \
        --expected <mirror>/census/round-54/records/c1-selftest-expected.tsv
SELFTEST pass cases=13          EXIT=0
python3 -B <mirror>/census/round-54/c2-counter.py --selftest --work W \
        --expected <mirror>/census/round-54/records/c2-selftest-expected.tsv
SELFTEST pass cases=10          EXIT=0
```

A baseline failure would have been inconclusive; there is none. Restored-byte rerun after the
whole sweep reproduced both receipts **byte-for-byte** (`receipts/restored-c1-selftest.txt`,
`receipts/restored-c2-selftest.txt`; `identical-to-baseline=True` for both).

## 2. Determinism of the fixture builder

```
python3 -B build-fixtures.py --work work1 --manifest receipts/manifest-build1.tsv
python3 -B build-fixtures.py --work work1 --manifest receipts/manifest-build2.tsv   # same dir, rebuild
python3 -B build-fixtures.py --work work2 --manifest receipts/manifest-build3.tsv   # different dir
diff manifest-build1.tsv manifest-build2.tsv          -> IDENTICAL (whole file, incl. dir column)
diff <cols name,kind,base,tip,record_sha256 of 1 vs 3> -> IDENTICAL (23 fixtures)
```

All 23 rebuilt tip commits reproduce the committed matrix rev column exactly (0 mismatches;
e.g. `F8-BT4-PARITY tip=5a0fafb73fe6…`, `FA4-SPACE-NAME tip=e0aabc60013d…`).
Determinism check: **PASS**.

## 3. Mutant table

Verdict rule (as tasked): a fixture kills if its `SELFTEST-CASE` row fails against the pinned
expected TSV (rc or first finding differs); a mutant SURVIVES if all fixtures still match.
Every mutant is one hunk (`sha256` per mutant in `receipts/hashes.txt`; diffs in `receipts/M*.diff`);
builder + expected TSV inside every mutant tree are byte-identical to the lane's.

| id | branch mutated (one hunk) | killed by | verdict | reading |
|---|---|---|---|---|
| M1 | `hidden_lines`: drop the `~{3,}` alternative from the fence opener regex | **F7-TILDE-FENCE** | KILLED | rc 0 vs 1, `fenced=0` vs `2` |
| M2 | `hidden_lines`: drop `len(body) >= n` (any same-char run closes) | — | **SURVIVED** | coverage gap, not equivalent |
| M3 | `hidden_lines`: drop the `<!--` / `-->` branch | **F9-HTML-COMMENT** | KILLED | rc 0 vs 1, `fenced=0` vs `2` |
| M4 | `zone_tokens`: accept a token whose `m.end(1) > ZONE` | **F10-STRADDLE** | KILLED | rc 1 = 1, first finding `MULTIPLE-ANNOTATIONS` vs `ZONE-TOKEN-STRADDLES-EDGE`, `straddle=0` vs `1` |
| M5 | `measure`: drop the `elif m_val != recomputed` BOGUS-RECOMPUTED branch | **F11-BOGUS-RECOMP** | KILLED | rc 0 vs 1, `bogus=0` vs `1` |
| M6 | `measure`: drop the whole pair-scan refusal (UNFILED-SOURCES-ANNOTATION leg) | **F12-LOG-UNFILED** | KILLED | rc 0 vs 1, `logunfiled=0` vs `1` |
| M7 | `measure`: drop the `PTR_RE.search(ln)` pointer exemption | — | **SURVIVED** | false positive on the real lane (`LOG.md:2578`); coverage gap |
| M8 | capture scan: drop `ln.count('\t') >= 5`, keep only the old `DATA_LIKE_COMMENT` regex | **FA4-SPACE-NAME** | KILLED | rc 0 vs 1 (FA2 still killed by the old regex — non-vacuous) |
| M9 | drop the `RECEIPT-UNKNOWN-KEY` finding | **FA5-EXTRA-KEY** | KILLED | rc 0 vs 1 |
| M10 | drop `CAPTURE-CRLF` + `RECEIPT-CRLF` | **FA6-CRLF** | KILLED | rc 1 = 1, first finding `CAPTURE-RECEIPT-MISMATCH` vs `CAPTURE-CRLF` (the v2 cascade reappears) |
| M11 | `--tool-sha256` accepted but the mismatch finding removed | — | **SURVIVED** | no fixture/arm passes the pin; real-lane wrong-pin run kills it; coverage gap |
| M12 | `frozen_class`: `symlink` kind returns `'tracked'` | **FH2-SYMLINK-HONEST + FA8-SYMLINK-CLASS** | KILLED | FH2 rc 0→1 (`class_mismatch=1`); FA8 rc 1→0 |

Counts: **9 killed / 3 survived (M2, M7, M11)**.

## 4. Verbatim kill lines

```
M1  SELFTEST-CASE F7-TILDE-FENCE fail rc=0 want_rc=1 finding=- want_finding=CORRECTION-IN-FENCE
    SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=2daa874557c2 base=2daa874557c2
M3  SELFTEST-CASE F9-HTML-COMMENT fail rc=0 want_rc=1 finding=- want_finding=CORRECTION-IN-FENCE
    SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=fafd3a2e582f base=fafd3a2e582f
M4  SELFTEST-CASE F10-STRADDLE fail rc=1 want_rc=1 finding=MULTIPLE-ANNOTATIONS want_finding=ZONE-TOKEN-STRADDLES-EDGE
    SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=1 inert=1 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=aa36dab9c2ca base=aa36dab9c2ca
M5  SELFTEST-CASE F11-BOGUS-RECOMP fail rc=0 want_rc=1 finding=- want_finding=BOGUS-RECOMPUTED
    SUMMARY sites=2 mismatches=1 filed=1 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=7325d506da78 base=7325d506da78
M6  SELFTEST-CASE F12-LOG-UNFILED fail rc=0 want_rc=1 finding=- want_finding=UNFILED-SOURCES-ANNOTATION
    SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=ea328890f5c1 base=ea328890f5c1
M8  SELFTEST-CASE FA4-SPACE-NAME fail rc=0 want_rc=1 finding=- want_finding=COMMENT-AMBIGUOUS-NAME
    SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=n/a rev=e0aabc60013d
M9  SELFTEST-CASE FA5-EXTRA-KEY fail rc=0 want_rc=1 finding=- want_finding=RECEIPT-UNKNOWN-KEY
    SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=n/a rev=2a6fdc6df02b
M10 SELFTEST-CASE FA6-CRLF fail rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-CRLF
    SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=FAIL tool_sha=FAIL removal_proposed=3 receipt=FAIL sorted=ok tool_pin=n/a rev=17c582af6c10
M12 SELFTEST-CASE FH2-SYMLINK-HONEST fail rc=1 want_rc=0 finding=class want_finding=-
    SUMMARY entries=4 rows=4 unclassified=0 class_mismatch=1 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=n/a rev=6815d46eee0f
M12 SELFTEST-CASE FA8-SYMLINK-CLASS fail rc=0 want_rc=1 finding=- want_finding=-
    SUMMARY entries=4 rows=4 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=n/a rev=e5900e5c5000
```

M4 and M10 are **finding-order kills with unchanged rc** — the TSV's finding column is what
catches them, so those two rows are load-bearing for the "printed FIRST"/"named instead of
truncated" claims. M12 kills in both directions (honest symlink row must stay green; wrong-class
row must stay red).

## 5. Survivors: equivalence or coverage gap?

### M2 (parity length check) — COVERAGE GAP, not equivalent

Direct probe of both `hidden_lines` implementations on the two shapes:

```
F8-style  (```` / ```text / CORR / ````)   pristine-hidden=[3, 4]  M2-hidden=[3, 4]  same
bare-short-run (```` / ``` / CORR / ````)  pristine-hidden=[3, 4]  M2-hidden=[]      DIFFERS
```

The committed F8 fixture does not test the length rule: its inner line is ```` ```text ````
(a 3-tick run **with trailing text**), which already fails the `set(body) == {ch}` test, so the
fence never closes under either build. Hidden-line sets per fixture (pristine == M2 on all 13):

```
F4-FENCE [8, 9]   F7-TILDE-FENCE [8, 9]   F8-BT4-PARITY [8, 9, 10]   F9-HTML-COMMENT [7, 8, 9, 10]
others []         lane SCORECARD.md at HEAD: 0 fence lines, hidden=[]
```

So the `len(body) >= n` clause executes but never changes an outcome on the committed corpus or
the lane. **Missing fixture named: `F8b-BT4-SHORT-RUN`** — a ```` ```` ```` fence whose content
begins with a bare ` ``` ` line, corrections after it, closing ```` ```` ````; v3 must return
`CORRECTION-IN-FENCE`, M2-shaped code returns 0. (`M2.diff`, `M2.selftest.txt`, probe above.)

### M7 (pointer exemption) — COVERAGE GAP, not equivalent; honest lane breaks

No fixture carries a pointer:

```
fixture F12-LOG-UNFILED   LOG pair-line '- the r52 note said corpus/SOURCES.md 274 -> 275 rows.' ptr=False
fixture F12b-LOG-FILED    LOG pair-line '- the r52 note said corpus/SOURCES.md 3 -> 4 rows.'   ptr=False
```

The lane does. Real lane, same recompute args (rev `bfdbb336…`, base `fe12daad…`,
record `2b90a262…`, sources `f778b9d1…`/`9bf9234a…`):

```
pristine  EXIT=0  SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 ... logunfiled=0 logrecomp=0 ... rev=bfdbb336329e
M7        EXIT=1  FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2578 claims 274 -> 275 rows but the registry holds 200; no pair-form filing names it
                  SUMMARY ... logunfiled=1 ... rev=bfdbb336329e
```

`LOG.md:2578` is the meta-reference that quotes the annotation and carries the `LOG.md:2527`
pointer; `PTR_RE` matches (`'LOG.md:2'`) and exempts it on pristine bytes. **Missing fixture
named: `F12c-LOG-POINTER-EXEMPT`** — a LOG.md line quoting `corpus/SOURCES.md <A> -> <B> rows`
plus a `path:line` pointer, with no pair filing, overstating the registry; must stay green.

### M11 (`--tool-sha256` pin) — COVERAGE GAP + harness limit, not equivalent

No fixture or selftest row ever passes the pin: `run_selftest` calls `measure(..., None, buf)`
(argument 5 is hardcoded `None`), so the branch is unreachable from `--selftest` by construction.
Real lane distinguishes the two builds:

```
pristine, --tool-sha256 000…0  EXIT=1  FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=e7e79952f783
                                        SUMMARY entries=49 rows=49 ... tool_pin=FAIL rev=bfdbb336329e
M11,      --tool-sha256 000…0  EXIT=0  SUMMARY entries=49 rows=49 ... tool_pin=FAIL rev=bfdbb336329e
```

Both with the correct pin `e7e79952…`: pristine EXIT=0 `tool_pin=ok`, M11 EXIT=0 — i.e. the
normal real-lane arm cannot tell them apart; only the wrong-pin arm can. **Missing fixture/arm
named: `FA9-WRONG-TOOL-PIN`** (or a `--selftest --tool-sha256` arm) that passes a wrong digest
and expects `TOOL-SHA-ARG-MISMATCH`/rc 1.

## 6. Real-lane cross-checks (pristine, at the content tip)

```
C1 (rev bfdbb336…, base fe12daad…): EXIT=0
SITE path=SCORECARD.md line=1196 stated=78 recomputed=79 status=mismatch filed=yes
SITE path=census/round-51/preregistration.txt line=125 stated=78 recomputed=79 status=mismatch filed=yes
SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 recomputed=79 rev=bfdbb336329e base=fe12daad2549

C2 (capture census/round-54/records/fleet-root-census.tsv, receipt …-run.txt, pin e7e79952…): EXIT=0
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
```

Every other C1/C2 mutant also exits 0 on these honest-lane arms (no false positive from the
other 11 mutants; receipts `real-lane-M*.txt`). So the real lane kills only M7 (false positive)
and, with a wrong pin, M11.

## 7. Routed named limits (no edits made; the frozen bytes stand)

1. **M2 survivor** — `hidden_lines` parity clause (`len(body) >= n`) is instrumented but
   unexercised: F8 tests the "bare same-char run" rule, not the length rule. Route: add
   `F8b-BT4-SHORT-RUN` (see §5).
2. **M7 survivor** — the `PTR_RE` exemption is instrumented but no fixture carries a pointer
   line, while the honest lane does (`LOG.md:2578`). A regression deleting it would ship green.
   Route: add `F12c-LOG-POINTER-EXEMPT`.
3. **M11 survivor** — `--tool-sha256` is not exercised by any fixture and is structurally
   unreachable from the C2 selftest (`run_selftest` passes `None`). The prereg's "shown able to
   fail" evidence for this pin is the absent-instrument/expected-pin control, not a tool-pin
   row. Route: add `FA9-WRONG-TOOL-PIN` and/or a selftest arm that forwards the pin.
4. **Detector sensitivity (code-evident, `run_selftest`)** — the expected TSV asserts `rc` plus
   only the **first** `FINDING` id (`got_find = next(...)`); any mutation that changes a
   second-or-later finding while keeping the first and the rc would survive. M4/M10 happened to
   reorder the first finding, which is why they died.
5. **FA8 finding identity unconstrained** — `c2-counter` prints rule-problems through the same
   `FINDING <text>` prefix used for ids (`FINDING class 'symlink' want 'tracked' …`), so the
   matrix extractor sees `-`; the expected row is `rc=1, finding='-'`, a wildcard. A change to
   that diagnostic's text/order is not caught by the fixture set.
6. **v2 arms accepted every new attack fixture** (control property, no action): the committed
   `records/c1-matrix-v2.tsv` rows F7-F12 all `exit 0`, and `records/c2-matrix-v2.tsv` FA4/FA5
   all `exit 0`, so the nine kills above are v3-borne, not carry-over.

## 8. Receipts

Under `receipts/` in this seat directory:

- `c1-selftest-pristine.txt`, `c2-selftest-pristine.txt`, `restored-{c1,c2}-selftest.txt` (baseline + restored bytes, identical)
- `M1..M12.selftest.txt` / `.selftest.rc` (verbatim detector rows per mutant)
- `M1..M12.matrix.tsv` (per-fixture rc/finding/SUMMARY under each mutant; kind-filtered driver)
- `M1..M12.diff` (exactly one hunk each), `hashes.txt` (all counter/builder/expected digests)
- `manifest-build1/2/3.tsv`, `m1.nodir.tsv`, `m3.nodir.tsv` (determinism)
- `real-lane-c1-pristine.txt`, `real-lane-c2-pristine.txt`, `real-lane-M1..M12.txt`,
  `real-lane-c2-pristine-wrongpin.txt`, `real-lane-M11-wrongpin.txt`
- `verdict-table.txt`, `lane-porcelain-after.txt`, `build1/2/3.err`

Scratch `/fast/scratch/hyaku/souji-r54/S54mutation01/` deleted after copying; lane bytes and
lane HEAD unchanged; no mutating git/jj command was run anywhere.

## 9. Verdict

- **Killed 9/12** (M1, M3, M4, M5, M6, M8, M9, M10, M12) by committed fixtures exactly as
  expected; no mutant produced a baseline/restore divergence.
- **Survived 3/12** (M2, M7, M11) — all **coverage gaps, none equivalent**: each is
  behaviourally distinct on a shape the committed fixture set (and, for M11, the committed
  selftest harness) never reaches. Three concrete missing fixtures named above.
- **Determinism PASS**: same-dir rebuild byte-identical manifest; cross-dir revs identical;
  all 23 tips reproduce the committed matrix rows.
- No claim of this round is falsified; the kill-power holes are routed as named limits, and the
  frozen bytes were not edited.
