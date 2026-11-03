# S54reviewer02 — attack report: frozen C2 v3 counter (souji round 54, wave w1)

Seat: reviewer (leaf member — no subagents dispatched; every probe run in-seat).
Axes: **coverage 8** (C2 target). C1/calibration-7 surfaces are other seats' scope; not attacked here.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Measured revision: `bfdbb336329e6afba3ab1ca83cbd6d9759271062` (lane tip = the round-54 capture commit).
Target under attack: `census/round-54/c2-counter.py` (v3) — **never edited**. Control arm: `census/round-53/c2-counter.py` (v2). Builder reused as authorized: `census/round-54/fixtures/build-fixtures.py` (stub-tool trick).

## 0. Freeze verification (before any probe)

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-54/c2-counter.py census/round-54/c1-counter.py census/round-54/fixtures/build-fixtures.py census/round-53/c2-counter.py census/round-53/c1-counter.py census/round-54/records/c2-selftest-expected.tsv
84b05295d5b84af23079c8fade6f7e640454ac25c56c842fb0233ea779735e09  census/round-54/c2-counter.py
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py
6515b97553dd6f6d207d638de2520c4367a56a1a37ff7329b9d914c329a349b7  census/round-53/c2-counter.py
a7928d05df794f14d5d0213ddb78d042f62819b52f5c49b3c838a1b96da1ed15  census/round-53/c1-counter.py
e32f793468cf370781a860f8b642b6a42e1d589f70c0b7f575ded130263fc00d  census/round-54/records/c2-selftest-expected.tsv
```

All C2-relevant pins match the preregistration (c2 v3 `84b05295…`, builder `ae5881f8…`, expected TSV `e32f7934…`). Lane tip confirmed: `bfdbb336 round-54: C2 capture — fleet-root census re-taken at fleet HEAD 3b0d5329…`.

## 1. Method and bounds

- Scratch `/fast/scratch/hyaku/souji-r54/S54reviewer02` — **deleted before yield**; raw outputs copied to `<seat>/runs/` (55 files), scripts + manifest to `<seat>/receipts/`.
- Fixtures built by the frozen builder (`build_one`): 10 C2 fixtures, single-commit repos; capture at `census/round-52/records/fleet-root-census.tsv`, receipt at `census/round-53/records/fleet-root-census-run.txt`, stub tool at `tools/souji-fleet-root-census.py` (sha256 `f509d0cb0d6d505cfb3a2358534ce90425d8de8fc7d75e1aa024346c0fbfe0fc`).
- Attack fixtures: copies of FH-HONEST with capture/receipt bytes edited, committed **inside the fixture** (`git -C <dir> rev-parse --show-toplevel` asserted == the fixture dir before each commit; identity `-c user.name=fixture -c user.email=fixture@local`; no git/jj mutation anywhere outside these fixtures). Where the attack does not target byte-binding, `CAPTURE_SHA256`/`ENTRIES` were recomputed so the only finding is the one under test.
- Counters invoked read-only (`git show` only). No lane tracked file touched. **No tool installs** (system python3 + git sufficed — nothing installed, nothing to record).
- 56 counter invocations total; 3 disclosed-invalid (§9).

## 2. Attack 1 — `#`-shape edges

Canonical v3 command form (per-attack root/rev substituted; full argv in `runs/v3-<name>.txt`):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-54/c2-counter.py \
  --root <fixture-dir> --rev <tip> \
  --capture census/round-52/records/fleet-root-census.tsv \
  --receipt census/round-53/records/fleet-root-census-run.txt \
  --scratch /fast/scratch/hyaku/souji-r54/S54reviewer02
```

### A1a-4TAB — `#`-leading row with 4 tabs (5 fields), consistent ENTRIES=3
Crafted line inserted after the `# SCOPE` line: `# ghost.txt\tfile\tyes\tno\ttracked` (capture bytes otherwise honest; receipt `CAPTURE_SHA256` recomputed).

```
$ python3 -B .../census/round-54/c2-counter.py --root .../attacks/A1a-4TAB --rev 07008a45758b5552ef814b0426353f825ae8f549 --capture census/round-52/records/fleet-root-census.tsv --receipt census/round-53/records/fleet-root-census-run.txt --scratch ...
--- rc=0 ---
SUMMARY entries=3 rows=3 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=n/a rev=07008a45758b
```
v2 arm: `--- rc=0 ---` same SUMMARY (rev=07008a45758b).

**Observed: v3 exits 0 — the row is silently dropped** (`entries=3 rows=3`: it never reaches `rows`, no finding). **Classification: NAMED LIMIT (NL-1).** The widened rule keys on `ln.count('\t') >= 5`; a `#`-leading line with ≤4 tabs is treated as a free-form comment and discarded with no finding, and the field-count rule never sees `#`-leading lines at all (they are intercepted by the comment branch before `len(f) != 6` is ever evaluated). Both arms blind — the claim's "any other `#`-leading 6-field row can no longer hide" holds only for ≥5-tab rows.

### A1a-7FLD — `#`-leading 7-field row (6 tabs)
Crafted line: `#\ta\tb\tc\td\te\tf`.
```
--- rc=1 ---
FINDING COMMENT-AMBIGUOUS-NAME comment shaped like a data row (>=5 tabs): '#\ta\tb\tc\td\te\tf'
SUMMARY entries=3 rows=3 ... receipt=ok sorted=ok tool_pin=n/a rev=3e82a2dca498
```
v2 arm: rc=0 (v2's `^#\S*(\t\S+){5}$` fullmatch fails on a 6th tab-group). **Instrumented ✓** — v3's tab-count rule fires generically where v2 was silent.

### A1a-plain7 — contrast: NON-`#` 7-field data row
Crafted row inserted in sort position: `g.txt\tfile\tyes\tno\ttracked\tnone\textra` (ENTRIES stays 3).
```
--- rc=1 ---
FINDING row field count 7: 'g.txt\tfile\tyes\tno\ttracked\tnone\textra'
SUMMARY entries=3 rows=3 ... rev=2bf1c5df82ee
```
v2 arm: rc=1, same finding. **The field-count rule DOES fire generically for non-`#` rows** — the blind spot in A1a-4TAB is the `#`-branch interception, not the field-count rule.

### A1b-SPACETABS — `#`-leading line with 5 tabs, first field `# ` + space only
Crafted line: `# \ta\tb\tc\td\te`.
```
--- rc=1 ---
FINDING COMMENT-AMBIGUOUS-NAME comment shaped like a data row (>=5 tabs): '# \ta\tb\tc\td\te'
SUMMARY ... rev=d91666024918
```
v2 arm: rc=0. **Instrumented ✓** — the tab-count rule is name-independent; fires on the degenerate name.

### A1c-LEGIT-TABS — false-positive probe: legitimate prose comment with 5 tabs
Crafted line: `# scope notes\talpha\tbeta\tgamma\tdelta\tepsilon` (capture otherwise honest, bindings recomputed).
```
--- rc=1 ---
FINDING COMMENT-AMBIGUOUS-NAME comment shaped like a data row (>=5 tabs): '# scope notes\talpha\tbeta\tgamma\tdelta\tepsilon'
SUMMARY ... rev=b9dd64b2cafd
```
v2 arm: rc=0 (v2 accepted this comment). **Observed: v3 kills an otherwise-honest capture because a prose comment carries five tabs. Classification: NAMED LIMIT (NL-2)** — the rule is shape-only and cannot distinguish a tab-heavy comment from a data row; over-broad refusal.

### A1d-COUNTED — `#`-leading name row DECLARED counted (ENTRIES=4, COUNT untracked-stray=1, receipt ENTRIES=4)
Crafted line: `# ghost.txt\tfile\tyes\tno\ttracked\tnone` (5 tabs).
```
--- rc=1 ---
FINDING COMMENT-AMBIGUOUS-NAME comment shaped like a data row (>=5 tabs): '# ghost.txt\tfile\tyes\tno\ttracked\tnone'
FINDING CAPTURE-RECEIPT-MISMATCH ENTRIES receipt=4 capture=4 rows=3
FINDING ENTRIES 4 != rows 3
FINDING COUNT untracked-stray declared 1 recomputed 0
SUMMARY entries=3 rows=3 ... counts=FAIL ... receipt=FAIL ... rev=40cad0e06cbb
```
v2 arm: rc=1 with the three generic findings (no COMMENT finding). **Answer to "(consistent capture — accepted?)": NO — a `#`-leading row is never counted.** The declared-counted form is refused (generic ENTRIES/COUNT/receipt mismatches, plus the named finding under v3); the consistent-excluded form is the A1a-4TAB silent drop. No defect beyond NL-1.

## 3. Attack 2 — receipt grammar edges

### A2a-LOWERKEY — unknown key in lowercase: `# generator=x`
```
--- rc=0 ---
SUMMARY entries=3 rows=3 ... receipt=ok sorted=ok tool_pin=n/a rev=83997138fa67
```
v2 arm: rc=0. **Observed: RECEIPT-UNKNOWN-KEY does NOT fire — the lowercase unknown key passes silently under BOTH arms. Classification: NAMED LIMIT (NL-3).** `RECEIPT_KV = '# ([A-Z0-9_]+)=(\S+)'` is uppercase-only; the routed surface ("unknown `# KEY=VALUE` refused") is instrumented only for uppercase KEYs.

### A2b-2SPACE-KEY — unknown key colliding after strip: `#  TOOL_SHA256=x` (two spaces)
```
--- rc=0 ---
SUMMARY ... receipt=ok ... rev=97aa158f21be
```
v2 arm: rc=0. **Observed: silently ignored — it evades BOTH the known-key grammar (needs exactly one space) and the unknown-key detector (same one-space anchor). Classification: NAMED LIMIT (NL-4).** Note it is ignored, not malformed: the receipt's real unparsed keys keep `recv` complete.

### A2b2-NOSPACE-KEY — `#TOOL_SHA256=x` (no space)
```
--- rc=0 ---
SUMMARY ... rev=03ef9001122a
```
v2 arm: rc=0. Same NL-4 class (zero-space variant also evades).

### A2e-LEADSPACE-KEY — contrast: `   # GENERATOR=x` (leading spaces)
```
--- rc=1 ---
FINDING RECEIPT-UNKNOWN-KEY receipt carries unknown key GENERATOR
SUMMARY ... receipt=ok ... rev=c210371c070d
```
v2 arm: rc=0. **Instrumented ✓** — the detector applies `ln.strip()` before matching, so *leading* whitespace is caught while *internal* extra/missing space is not. Sharpens the NL-4 wording.

### A2c-DUP-KEY — duplicate known key (`# ENTRIES=3` twice)
```
--- rc=1 ---
FINDING RECEIPT-MALFORMED receipt census/round-53/records/fleet-root-census-run.txt does not carry the RECEIPT_VERSION=1 grammar
SUMMARY ... receipt=FAIL ... rev=73fd8dac1076
```
v2 arm: rc=1, same finding. **Instrumented ✓** — duplicate known keys are caught as RECEIPT-MALFORMED by both arms.

### A2d-RECEIPT-CRLF — CRLF in the RECEIPT only (capture clean)
```
--- rc=1 ---
FINDING RECEIPT-CRLF receipt bytes carry CR (carriage return)
SUMMARY ... receipt=ok ... rev=5b72c04306c5
```
v2 arm: rc=0 (v2 accepted a CRLF receipt). **Instrumented ✓** — `RECEIPT-CRLF` is a dedicated named class and fires on receipt-only CRLF; `CAPTURE-CRLF` correctly absent. New work demonstrated (v2-arm acceptance row).

## 4. Attack 3 — `--tool-sha256` edges (on FH-HONEST `81c9f21461bf…`, no repo edit)

```
pin-correct   rc=0  SUMMARY ... tool_pin=ok rev=81c9f21461bf
pin-wrong     rc=1  FINDING TOOL-SHA-ARG-MISMATCH pinned=0509d0cb0d6d observed=f509d0cb0d6d
                    SUMMARY ... tool_pin=FAIL rev=81c9f21461bf
pin-63hex     rc=2  CANNOT-EVALUATE --tool-sha256 must be 64-hex
pin-65hex     rc=2  CANNOT-EVALUATE --tool-sha256 must be 64-hex
pin-uppercase rc=2  CANNOT-EVALUATE --tool-sha256 must be 64-hex
pin-absent    rc=0  SUMMARY ... tool_pin=n/a rev=81c9f21461bf
```
- Wrong 64-hex pin → `TOOL-SHA-ARG-MISMATCH`, exit 1 ✓ (the pin is shown able to fail).
- Correct pin → `tool_pin=ok` ✓.
- 63-hex / 65-hex / **uppercase** → exit 2 `CANNOT-EVALUATE` (bad-CLI grammar; never compared). **Classification: NAMED LIMIT (NL-5)** — the pin accepts lowercase 64-hex only; a caller pinning the *correct* digest in uppercase cannot evaluate at all.

### A3-NOARG-WRONGTOOL — wrong `TOOL_SHA256` in capture header AND receipt, run WITHOUT the pin
```
--- rc=1 ---
FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 receipt=ffffffffffff tool=f509d0cb0d6d capture=ffffffffffff
FINDING TOOL_SHA256 ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff != tool bytes f509d0cb0d6d505cfb3a2358534ce90425d8de8fc7d75e1aa024346c0fbfe0fc
SUMMARY ... tool_sha=FAIL ... receipt=FAIL ... rev=a2e633f59b25
```
v2 arm: rc=1, same two findings. **Answer to "(named limit — no pin, no check)": the tool-bytes binding is UNCONDITIONAL** — without the argument the capture header is still checked against the computed tool bytes and the receipt binding still applies, so a wrong tool claim is refused either way. **Classification: disclosed design** (the argument is an auxiliary caller-side pin, mirroring C1's `--record-sha256`); the only residue is cosmetic (`tool_pin=n/a` when omitted), folded into NL-5's wording.

## 5. Attack 4 — branch coverage FA7/FA8/FH2 under BOTH arms

```
v3-FA7-RECEIPT-ENTRIES  rc=1  FINDING CAPTURE-RECEIPT-MISMATCH ENTRIES receipt=4 capture=3 rows=3
v2-FA7-RECEIPT-ENTRIES  rc=1  FINDING CAPTURE-RECEIPT-MISMATCH ENTRIES receipt=4 capture=3 rows=3
v3-FA8-SYMLINK-CLASS    rc=1  FINDING class 'tracked' want 'symlink' for 'lnk'
v2-FA8-SYMLINK-CLASS    rc=1  FINDING class 'tracked' want 'symlink' for 'lnk'
v3-FH2-SYMLINK-HONEST   rc=0  SUMMARY entries=4 rows=4 ... receipt=ok sorted=ok tool_pin=n/a rev=6815d46eee0f
v2-FH2-SYMLINK-HONEST   rc=0  SUMMARY entries=4 rows=4 ... receipt=ok sorted=ok rev=6815d46eee0f
```
**All four kill runs exit 1 under both arms; FH2 exit 0 under both.** Branch coverage confirmed (r53 M-F1/M-F2 exercised; matches the frozen expected TSV rows).

## 6. Attack 5 — carry-over and standing checks

### Pinned selftest (frozen expected TSV, pinned builder)
```
$ python3 -B .../census/round-54/c2-counter.py --selftest --work .../selftest --builder-sha256 ae5881f8... --expected-sha256 e32f7934...
--- rc=0 ---
SELFTEST-CASE FH-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FH2-SYMLINK-HONEST pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE FA1-UNSORTED pass rc=1 want_rc=1 finding=ROWS-UNSORTED want_finding=ROWS-UNSORTED
SELFTEST-CASE FA2-COMMENT pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA3-TAMPER pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA4-SPACE-NAME pass rc=1 want_rc=1 finding=COMMENT-AMBIGUOUS-NAME want_finding=COMMENT-AMBIGUOUS-NAME
SELFTEST-CASE FA5-EXTRA-KEY pass rc=1 want_rc=1 finding=RECEIPT-UNKNOWN-KEY want_finding=RECEIPT-UNKNOWN-KEY
SELFTEST-CASE FA6-CRLF pass rc=1 want_rc=1 finding=CAPTURE-CRLF want_finding=CAPTURE-CRLF
SELFTEST-CASE FA7-RECEIPT-ENTRIES pass rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-RECEIPT-MISMATCH
SELFTEST-CASE FA8-SYMLINK-CLASS pass rc=1 want_rc=1 finding=class want_finding=-
SELFTEST pass cases=10
```

### Direct v3 kills with the v2 finding ids
```
v3-FA1-UNSORTED  rc=1  FINDING ROWS-UNSORTED data rows are not in ascending byte order of name
v3-FA2-COMMENT   rc=1  FINDING COMMENT-AMBIGUOUS-NAME comment shaped like a data row (>=5 tabs): '##odd\tfile\tno\tno\tuntracked-stray\treport-only'
v3-FA3-TAMPER    rc=1  FINDING CAPTURE-RECEIPT-MISMATCH CAPTURE_SHA256 receipt=a2caeea4ecb1 observed=a0c376c83883
```
v2 arm on the same fixtures: identical ids (runs/v2-FA1…, v2-FA2…, v2-FA3…). **v2-arm acceptance rows: v2-FA4 rc=0, v2-FA5 rc=0** — the before-state holds, the v3 claim is not vacuous.

### FA6 both arms (naming discipline)
```
v3-FA6-CRLF rc=1  FINDING CAPTURE-CRLF capture bytes carry CR (carriage return)   <- FIRST finding
                  FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 ... (v2-style cascade follows)
v2-FA6-CRLF rc=1  FINDING CAPTURE-RECEIPT-MISMATCH TOOL_SHA256 receipt=f509d0cb0d6d tool=f509d0cb0d6d capture=-   <- spurious first line
                  ... 18 further findings, no CR class anywhere
```
v3 prints the dedicated `CAPTURE-CRLF` **first**; v2's cascade leads with the spurious `CAPTURE-RECEIPT-MISMATCH` — exactly the r53 routed complaint.

### Real lane at the capture commit bfdbb336 (corrected paths)
```
lane-v3-r53capture       rc=0  SUMMARY entries=49 rows=49 ... receipt=ok sorted=ok tool_pin=n/a rev=bfdbb336329e
lane-v3-r53capture-pin   rc=0  SUMMARY ... receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
lane-v3-r54capture-pin   rc=0  SUMMARY ... receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
lane-v2-r53capture       rc=0  SUMMARY ... receipt=ok sorted=ok rev=bfdbb336329e
```
- **The r53 capture still verifies under v3 at bfdbb336** (with and without the `e7e79952…` pin) — carry-over standing check PASSES.
- **The prereg C2 recompute command passes**: v3 on the fresh round-54 capture + RECEIPT_VERSION=1 receipt with the base tool pin exits 0 `receipt=ok sorted=ok tool_pin=ok`.
- v2 still verifies its own capture at the r54 tip.

### Out-of-contract observation (r52 pair)
`v3` on `census/round-52/records/fleet-root-census.tsv` + its own `fleet-root-census-run.txt` → rc=1 `RECEIPT-MALFORMED … does not carry the RECEIPT_VERSION=1 grammar`. The r52 receipt is the old prose "provenance" format (no machine block) — the r52 capture belongs to the r52 counter arm; v2 behaves identically (same grammar). Not a v3 regression; no claim touches it.

## 7. Verdict table

| # | attack | observed | classification | suggested r55 wording |
|---|--------|----------|----------------|------------------------|
| 1a-i | A1a-4TAB: `#`-row, 4 tabs/5 fields, consistent ENTRIES | v3 rc=0 **silent drop** (entries=3 rows=3, no finding); v2 rc=0 | **NAMED LIMIT NL-1** | "the ≥5-tab rule leaves a ≤4-tab hiding channel: any `#`-leading line with fewer than five tabs is silently discarded as a free-form comment and never reaches the field-count rule" |
| 1a-ii | A1a-7FLD: `#`-row, 7 fields/6 tabs | v3 rc=1 COMMENT-AMBIGUOUS-NAME; v2 rc=0 | instrumented ✓ (generic tab-count) | — |
| 1a-iii | A1a-plain7: non-`#` 7-field row | both rc=1 `row field count 7` | field-count rule generic for non-`#` rows (contrast proving NL-1's cause) | — |
| 1b | A1b: `# ` + 5 tabs | v3 rc=1 COMMENT-AMBIGUOUS-NAME; v2 rc=0 | instrumented ✓ (name-independent) | — |
| 1c | A1c: legit prose comment, 5 tabs | v3 rc=1 COMMENT-AMBIGUOUS-NAME on an honest capture; v2 rc=0 | **NAMED LIMIT NL-2** (over-broad refusal) | "the rule is shape-only: a prose comment that legitimately carries five tabs is refused as data-shaped" |
| 1d | A1d: `#`-row declared counted (ENTRIES=4, stray COUNT=1, receipt 4) | v3 rc=1 COMMENT-AMBIGUOUS-NAME + ENTRIES/COUNT/receipt mismatches; v2 rc=1 generic only | answered: never counted; counted-form refused; excluded-form = NL-1 | — |
| 2a | A2a: `# generator=x` | v3 rc=0; v2 rc=0 | **NAMED LIMIT NL-3** | "RECEIPT-UNKNOWN-KEY instruments only uppercase KEYs (`[A-Z0-9_]+`); lowercase/mixed-case unknown keys pass unrefused" |
| 2b | A2b: `#  TOOL_SHA256=x` (two spaces) | v3 rc=0; v2 rc=0 | **NAMED LIMIT NL-4** | "unknown-key detection anchors exactly `# ` (one space, after strip); whitespace-variant keys (`#  KEY=x`, `#KEY=x`) evade it silently" |
| 2b' | A2b2: `#TOOL_SHA256=x` (no space) | v3 rc=0; v2 rc=0 | NAMED LIMIT NL-4 (same class) | (merged with 2b) |
| 2b'' | A2e: `   # GENERATOR=x` (leading spaces) | v3 rc=1 RECEIPT-UNKNOWN-KEY; v2 rc=0 | instrumented ✓ (strip catches leading ws — contrast for NL-4) | — |
| 2c | A2c: duplicate `# ENTRIES=3` | both rc=1 RECEIPT-MALFORMED | instrumented ✓ | — |
| 2d | A2d: receipt-only CRLF | v3 rc=1 **RECEIPT-CRLF** (first); v2 rc=0 | instrumented ✓ (new named class; v2-arm acceptance shown) | — |
| 3a | pin 63-hex | rc=2 CANNOT-EVALUATE | **NAMED LIMIT NL-5** | "`--tool-sha256` accepts lowercase 64-hex only; wrong length or uppercase → exit 2 CANNOT-EVALUATE, never compared" |
| 3b | pin 65-hex | rc=2 CANNOT-EVALUATE | NAMED LIMIT NL-5 | (merged) |
| 3c | pin uppercase (correct digest) | rc=2 CANNOT-EVALUATE | NAMED LIMIT NL-5 | (merged) |
| 3d | pin wrong 64-hex | rc=1 TOOL-SHA-ARG-MISMATCH, tool_pin=FAIL | instrumented ✓ (pin shown able to fail) | — |
| 3e | pin correct | rc=0 tool_pin=ok | ✓ | — |
| 3f | no pin | rc=0 tool_pin=n/a; wrong-tool capture still refused without pin (A3-NOARG rc=1 both arms) | disclosed design (binding unconditional) | "the pin argument is auxiliary; tool bytes stay bound via capture header + receipt when the pin is absent" |
| 4 | FA7 both arms | v3 rc=1, v2 rc=1 CAPTURE-RECEIPT-MISMATCH | branch coverage ✓ | — |
| 4 | FA8 both arms | v3 rc=1, v2 rc=1 (class rule) | branch coverage ✓ | — |
| 4 | FH2 both arms | v3 rc=0, v2 rc=0 | branch coverage ✓ (green) | — |
| 5 | FA1/FA2/FA3 under v3 | rc=1 with v2 ids ROWS-UNSORTED / COMMENT-AMBIGUOUS-NAME / CAPTURE-RECEIPT-MISMATCH | carry-over ✓ | — |
| 5 | pinned selftest | SELFTEST pass cases=10 | ✓ | — |
| 5 | r53 capture under v3 @ bfdbb336 | rc=0 (also with pin) | standing ✓ | — |
| 5 | r54 capture under v3 + e7e79952 pin @ bfdbb336 | rc=0 receipt=ok sorted=ok tool_pin=ok | prereg recompute ✓ | — |
| 5 | v2 on r53 capture @ bfdbb336 | rc=0 | standing ✓ | — |

**Routed defects (counter fails its own frozen claim): 0. Named limits routed to r55: 5 (NL-1…NL-5).**

## 8. Named limits carried to r55 (consolidated)

- **NL-1** — `#`-leading capture lines with ≤4 tabs are silently dropped (no finding); the field-count rule never evaluates `#`-leading lines. Both arms blind. (A1a-4TAB)
- **NL-2** — the ≥5-tab COMMENT-AMBIGUOUS-NAME rule is shape-only: a legitimate prose comment carrying five tabs is refused as data-shaped (over-broad; kills honest captures v2 accepted). (A1c)
- **NL-3** — RECEIPT-UNKNOWN-KEY's KEY class is uppercase-only; lowercase unknown keys pass unrefused under both arms. (A2a)
- **NL-4** — unknown-key detection anchors exactly `# ` after strip: internal extra-space and zero-space variants evade silently, while leading-space variants ARE caught (strip asymmetry). (A2b, A2b2, A2e)
- **NL-5** — `--tool-sha256` grammar is lowercase 64-hex only (uppercase/wrong length → exit 2, never compared); the argument is optional (`tool_pin=n/a`) but tool bytes remain bound via capture header + receipt regardless. (pin-63/65/uppercase, pin-absent, A3-NOARG)

Observation (no action): in v3's capture branch `DATA_LIKE_COMMENT.fullmatch(ln)` is subsumed by `ln.count('\t') >= 5` (every fullmatch has ≥5 tabs) — a dead predicate kept for v2 parity; harmless.

## 9. Honesty notes, disclosed defects, verification gaps

- **Disclosed runner defect (mine, not the lane's):** my first three lane runs passed the *fixture* capture path (`census/round-52/records/fleet-root-census.tsv`) instead of the per-round paths; they exited 1 with `CAPTURE-RECEIPT-MISMATCH CAPTURE_SHA256 receipt=922112361cdd observed=215bf849f318` + `FLEET_HEAD receipt=6e312f2ecd13 capture=e56cdb3365f52e7846b28872b0b83460375b1952`. That output is the r52 capture (its own receipt records `staged sha256: 215bf849f318…`) measured against the r53 receipt — a mispairing I created. **The receipt binding caught it immediately**, which is affirmative evidence for the binding. The corrected runs in §6 are the authoritative lane results. The 3 invalid outputs are preserved at `runs/lane-v3-r53capture.txt` (superseded in place by the corrected rerun — the invalid variant is quoted here and in `runs/matrix-stdout.txt`).
- All fixture commits ran inside fixtures I created this session, after asserting `git rev-parse --show-toplevel` == the fixture dir. No git/jj mutation anywhere else; no lane tracked file edited; the frozen counters/builder/expected TSVs were only read.
- **Not run (gaps):** C1 surfaces (F1–F12b) — other seats' scope; v2's own selftest; the r52 capture under the r52 counter arm; the do-nothing control files' embedded rows (I verified the equivalent rows directly instead: v2 accepts FA4/FA5, v2-FA6 cascade, wrong-pin refusal).
- Tooling authorization: **nothing installed** — system python3 + git sufficed.
- Scratch `/fast/scratch/hyaku/souji-r54/S54reviewer02` deleted before yield (receipts copied to `<seat>/runs/`, scripts + manifest to `<seat>/receipts/`).

Report trailer path: `.ufo/waves/round-54/w1/S54reviewer02.md` (this file, duplicated at `<seat>/report.md`).
