# S55connector01 — souji round 55, wave 1, seat S55connector01 (connector)

Role: connector. Task: sibling-overlap scan over the three declared surfaces (A line
numbering, B fleet-root receipt grammar, C declared-count agreement), PTR sanity on
the narrowed exemption, and at most ONE bounded proposal (recorded, never applied).
Lane: `souji-shokunin`. Seat dir: `.ufo/waves/round-55/w1/S55connector01/`
(receipts under `receipts/`). Scratch `/fast/scratch/hyaku/souji-r55/S55connector01/`
deleted before yield (receipts were copied to the seat dir first).

## 0. Pins, lane state, real-lane runs

Six frozen pins re-verified by sha256 before any probe; all match the preregistration:

```
944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2  census/round-55/c1-counter.py
e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c  census/round-55/c2-counter.py
e629a2e993b043bfc32904bc46612f5bdbc13909351cfe68f151b3f604fa8d62  census/round-55/fixtures/build-fixtures.py
ce13d4fff4b66175071ccef2a808baf3b1f928c5ec9985343580524450ef8315  census/round-55/fixtures/run-matrix.sh
ca096117204a7262aaba908f1e913aee876e70b8167e6d596028f8f475e7b76e  census/round-55/records/c1-selftest-expected.tsv
63391afab07930193df686b9b9a4b9f3d6b9074e7bd3ed3479ede8f05a8bd2bc  census/round-55/records/c2-selftest-expected.tsv
```

Lane tip at dispatch: `3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`, worktree clean.
**Lane HEAD moved during this seat's run** to `b6c6a93a6f892878da15e1de6c57ead221bd5be2`
(I ran no mutating git; the advance is someone else's commit). It changed the
registry count `git show HEAD:corpus/SOURCES.md` from 201 rows (at `3ce0ba03`) to
202 rows. Every real-lane number below is pinned to an explicit revision
(`3ce0ba03`), so it is unaffected; the PTR counts in §3 are the only figures that
depend on which HEAD I read, and they are labelled.

Real-lane runs at `3ce0ba03` (verbatim, `receipts/`):

- C1 v4 real lane, exit **0**:
  `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 record_sha=ok appended=ok multi=0 inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79`
- C2 v4 real lane, exit **0**:
  `SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok`
- C1 selftest (pinned builder + expected), exit **0**, `SELFTEST pass cases=27`.
- C2 selftest (pinned builder + expected), exit **0**, `SELFTEST pass cases=15`.

Frozen bytes were not edited. The two C2 receipt-probe attacks ran in throwaway
clones under scratch, built from the committed lane with one appended line.

## 1. Method

Scope: the 20 sibling lanes at `/home/vgpnk/Projects/shokunin/*-shokunin`, existing
dirs only, case-insensitive grep-style patterns, every hit opened or classified by a
stated criterion. Two file scopes are reported separately, because mixing them caused
an error in my first draft:

- **all-scope** = `tools/`, `corpus/`, `census/` including archived per-round dirs
  (`corpus/live/`, `corpus/evidence/`, `fixtures/`, `lessons/`, `gates/`, `waves/`);
- **live-only** = the same minus the archived dirs.

The per-file classification table is `receipts/sibling-classification.tsv` (136 loose
hits, lane / surface / file / class / evidence). It is a *loose* pass and is superseded
by the decisive counts below, which is why it contains false "overlap" rows.

Manual opening: I opened and read in full only the files cited by name in §2 (kaidoku
`annotation-audit.py`, chousa `stale-count-check.py`, kasegi `LOG.md:1667`, kaidoku
`custody-pair.py`). The remaining counts are script-classified on the stated criterion.
I did not hand-open each of the hits.

## 2. Per-surface verdicts

### Surface A — one-line-model / splitlines line numbering

**Verdict: the mechanism overlaps in 14 sibling lanes. Two sibling tools are directly
affected by the same class of form-feed divergence that souji's r54 HIGH S1 was.
Contract is disjoint from souji's counters, so this is a drift watch with a named
sibling defect, not a souji fix.**

Decisive criterion: `splitlines()` output enumerated into a 1-based line index, in a
file that also cites or matches a line number from another source.

Counts (`receipts/final_a.py` output, re-run this seat):

- all-scope: **73 files across 14 lanes**;
- live-only (archived round dirs excluded): **33 files across 10 lanes**
  (kagi 1, kaidoku 4, kama 5, kasegi 3, kotodama 6, lore 1, mori 2, revenger 2,
  tameshi 4, tsukuroi 5). The 73 figure in my first draft was all-scope, and I
  mislabelled it "live instrument"; that label was wrong.

Two divergences I verified by running the code:

1. **Sibling miss (verdict-relevant, the mirror of S1).**
   `kaidoku-shokunin/tools/round-59/annotation-audit.py` uses `text.splitlines()`
   (line 116) and anchors its annotation grammar at column 0 (`ANN_RE =
   ^\(.*?\bbase:...`). Probe (`receipts/` probe scripts, output reproduced in this
   session): a receipt whose annotation line starts with a form feed
   (`\x0c(base: 0 -> record: 1)`) is **found** by `splitlines()` at line 4 (the
   separator is consumed), but a LF-only split keeps the `\x0c` and the `^\(` anchor
   **does not match at all**. So the two models disagree in both directions: the
   sibling's current model sees it, a LF-only model would silently drop it. Souji's C1
   counter is LF-only by design (C1 v4 one-line model); it reads only souji's repo, so
   the sibling gap cannot reach souji's verdicts. Recorded, not fixed.

   *Correction to my first draft:* I had written that the annotation "is still found
   under LF-only, but its reported line differs". That was wrong. Under LF-only the
   annotation is not matched. The divergence is a miss, not a misnumber.

2. **Sibling verdict flip, reproduced.** `chousa-shokunin/corpus/evidence/round50/
   stale-count-check.py` feeds `read_text().splitlines()` (lines 26, 69) to `scan()`,
   whose `NAMES` regex resolves a human `superseded by line N`. Probe
   (`receipts/repro-chousa-final.txt`, re-run this seat, exit 0): stale count on
   LF-line 1, correction cites "line 1":
   - `splitlines()` numbering → `hits=[(2, 9, False)] unresolved=1` → **FAIL**;
   - LF-only numbering → `hits=[(1, 9, True)] unresolved=0` → **PASS**.
   The phantom line `splitlines()` inserts above the stale count breaks the citation
   match, so a sibling reports a stale count that does not exist.

Contract disjointness: souji's C1 v4 numbers lines by LF only everywhere
(`c1-counter.py:146-160`, `264-265`, `373`). Its counters take `--root LANE` and read
only that repo's committed bytes, so neither side's numbering reaches the other.

Souji-internal check: the only `splitlines()` left in the C1 counter is at line 227,
over `git diff --numstat`. I verified git quotes a path that contains a form feed
(`"evil\fname.txt"`, probe in `receipts/`), so a numstat line never carries an exotic
separator. This is the disclosed named limit, and it holds. The C2 counter splits on
`'\n'` only (lines 167, 261).

### Surface B — fleet-root capture receipt grammar (RECEIPT_VERSION=1)

**Verdict: no overlap. The `RECEIPT_VERSION=1` / `CAPTURE_SHA256` / `FLEET_HEAD` /
`ENTRIES` capture grammar is souji-unique.**

Decisive criterion: a `# KEY=VALUE` block carrying at least three keys and at least one
of the souji receipt names. Result: **0 sibling files**. The 23 loose `# KEY=VALUE`
hits across 8 lanes are unrelated per-tool headers (kaidoku `c1-run.sh` envelope knobs,
kasegi closure `VERDICT=`/`SHA=`, mori `CENSUS_SHA256=`, tsukuroi census `CLASSES=`,
mado `PASS=`/`FAIL=`, chousa `GATE_SHA256=`).

Nearest concept: `kaidoku-shokunin/.ufo/gates/custody-pair/custody-pair.py`, which is
`RECEIPT_VERSION = 2` with a different grammar: `# receipt-version: 2` (colon, hyphenated
key), `# tool: NAME sha256 HEX`, `# captured-utc:`, `# paths: N present: N`. Prose, not
a `KEY=VALUE` machine block. Different grammar, different keys, no shared surface.

### Surface C — declared-count annotation agreement

**Verdict: the problem class (declared vs recomputed count) overlaps; the grammar,
unit, file scope and finding names do not.**

Decisive criterion: a file containing both `declared` and a recomputed/re-derived
term. Result: **36 live files across 10 lanes** (kagi 1, kaidoku 15, kama 8, kasegi 3,
kotodama 3, mado 1, mori 1, revenger 1, tameshi 2, tsukuroi 1). Zero in audio, chousa,
game-dev-2d/3d, kake, kengaku, kotoba, kumitate, lore, tabi.

Closest analog: kaidoku `tools/round-59/annotation-audit.py`, driven fleet-wide by
`tools/round-60/annotation-sweep.py`. It binds `(base: N -> record: M)` to the nearest
`$` command and re-derives the `git show ... | grep -c` probe. Same problem class and
technique, but receipt-scoped (`.ufo/waves` receipts, not a registry), with its own
finding names (`ANNOTATION_OUTPUT_MISMATCH`, `ANNOTATION_REDERIVATION_MISMATCH`).
Souji C1 v4 is registry-scoped (`corpus/SOURCES.md` row count, a 32-char zone,
`R52/R53-CORRECTION` filings in `SCORECARD.md`, findings such as
`UNFILED-SOURCES-ANNOTATION`, `SOURCES-RECOMPUTE-MISMATCH`, `PAIR-FILING-INERT`).
The two instruments cannot fire on each other's bytes.

### Verdict summary

| Surface | Decisive count (all-scope / live-only) | Lanes | Verdict |
|---|---|---|---|
| A — one-line model / splitlines | 73 / 33 files | 14 / 10 | Mechanism overlaps; two sibling defects of the S1 class (one miss, one verdict flip, reproduced); contract disjoint. Drift watch. |
| B — RECEIPT_VERSION=1 grammar | 0 | 0 | No overlap. |
| C — declared-count agreement | 36 live | 10 | Problem class overlaps (kaidoku r59/r60 nearest); grammar, unit, scope, names disjoint. |

## 3. PTR sanity — the narrowed exemption vs. the fleet

Question: does the narrowed PTR exemption (path-like token with a dot extension, colon,
digit) break a sibling that uses a colon-digit timestamp on a `corpus/SOURCES.md` pair
line?

**Verdict: no sibling breakage and no souji regression.** Measured over all 21 repos,
in-scope = `max(a,b) > registry_rows` on a pair annotation in `LOG.md` /
`corpus/README.md` that names `corpus/SOURCES.md`:

- Pair-site lines that flip from v3-exempt (shape `[A-Za-z0-9_.\-]+:\d`) to not
  v4-exempt: **1** fleet-wide. It is `kasegi-shokunin/LOG.md:1667`, whose only
  colon-digit token is the ISO timestamp `2026-10-26T15:3`. The pair there is `18→19`,
  and kasegi's registry holds 92 rows, so `max = 19 <= 92` and the line is out of scope
  before the PTR exemption is consulted. **Inert flip.**
- souji's own in-scope pair lines (`LOG.md:2527`, `LOG.md:2578`, `corpus/README.md:870`):
  **0 newly exposed**. `LOG.md:2578` carries the path-like pointer `LOG.md:2527` and
  stays exempt under v4 as under v3. The other two are filed by `R53-CORRECTION` rows at
  `SCORECARD.md:1268` and `:1270`.
- souji's whole corpus holds one clock-only pair line
  (`corpus/lessons/round-36-verifier-spotcheck.md:166`), outside C1's two-file scope.
- Across the fleet, clock-only pair lines appear in prose in many lanes, but only 4
  sit on a `corpus/SOURCES.md` pair line (kumitate 2, mado 2). Drift watch only,
  since souji's instruments read only souji's repo.
- souji's committed `LOG.md`, `SCORECARD.md`, `corpus/README.md`, `corpus/SOURCES.md`
  and `census/round-51/preregistration.txt` contain zero exotic separators
  (`\x0b \x0c \x1c \x1d \x1e \x85`, `U+2028/9`).

## 4. The ONE bounded proposal (recorded, NOT applied)

### P1 — widen the C2 receipt key charset to admit hyphens, with one committed fixture

**The gap, measured.** C2 v4 lexes a receipt key with `RECEIPT_KV =
r'\s*#\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S+?)\s*'`. A hyphenated line such as
`# FOO-BAR=1` does not lex as a key at all, so it is neither validated nor reported.

Measured on the committed counter, same capture and pin, one appended line, two clones
(`receipts/c2-probe-plain-unknown-key.txt`, `receipts/c2-probe-hyphen-unknown-key.txt`):

| appended receipt line | C2 v4 exit | finding |
|---|---|---|
| `# FOOBAR=1` | **1** | `RECEIPT-UNKNOWN-KEY receipt carries unknown key FOOBAR` |
| `# FOO-BAR=1` | **0** | none (silently accepted) |

This is the same shape as the r54 NL-3/NL-4 items (an unknown key the detector cannot
see), one character wide.

Cross-lane relevance: the one sibling with a versioned receipt, kaidoku custody-pair,
emits hyphenated key names (`# receipt-version: 2`). Its grammar is different and it is
not a producer of souji's receipts, but the hyphenated-key shape is a shape the fleet
already uses.

**The change.** (1) `c2-counter.py`: widen the key class to `[A-Za-z0-9_-]`. Known-key
set, duplicate and sorted checks unchanged. (2) `build-fixtures.py`: add
`FB5-HYPHEN-KEY` (honest receipt plus `# FOO-BAR=1`). (3) `c2-selftest-expected.tsv`:
add `FB5-HYPHEN-KEY	1	RECEIPT-UNKNOWN-KEY`. (4) Re-pin the builder, expected and
control hashes.

**Acceptance evidence, with the limit stated.**

- Receipt lexer, honest committed receipt: current charset `known=5 unknown=[]`,
  widened `known=5 unknown=[]`. No new finding on the real-lane receipt
  (`receipts/widen_accept.txt`).
- Receipt lexer, all 13 committed C2 fixture receipts, rebuilt from the frozen builder
  and lexed under both charsets: the unknown-key output is identical on all 13
  (`FA5 ['GENERATOR']`, `FB2 ['generator']`, `FB3 ['BUILDHOST']`, the rest none);
  no committed fixture contains a hyphenated receipt key.
- **Limit:** I compared lexer output, not full counter exit codes. I did not run a
  patched copy of `c2-counter.py` across the 13 fixtures or the real lane. The
  "0 verdicts change" line in my first draft overstated this. The full-counter run is
  the remaining step, and it belongs to the amendment round, not to this seat.

**Second-order effects.**

- Runtime: none (one regex character class).
- Contract: a hyphenated key goes from silently ignored to named. The known-key set is
  unchanged, so no honest producer breaks.
- Substrate: the C2 population grows 13 → 14 and the expected TSV 15 → 16. The
  builder list, the pinned hashes and the control files all need re-pinning, as r54 did
  when it added FB1-FB3. **This cannot land in r55**, whose frozen bytes may not change.
  It belongs to r56 or an r55.1 amendment with its own freeze.
- Verification: the selftest gains an arm and must be re-pinned.
- Risk: a misspelt known key with a hyphen (`RECEIPT-VERSION=1`) is now refused as
  unknown. That is the intended outcome, and it closes the mirror gap of the existing
  missing-known-key check.
- Risk: the counter reports only the first unknown key. A receipt with a hyphenated
  unknown key ahead of a plain one would now report the hyphenated one. That is the
  intended semantics, and the prereg already names "only the FIRST unknown receipt
  key" as a limit.

**Status: RECORDED, NOT APPLIED.** No frozen r55 byte was edited.

## 5. Contradictions stated, not smoothed

1. Surface A shares a mechanism with souji's r54 HIGH S1, and a sibling
   (`chousa stale-count-check.py`) demonstrably flips a verdict under the same
   form-feed condition. Souji's own counter is repaired and its real lane is green.
   The sibling's defect has no owner in this round and is not souji's to fix.
2. Surface C shares a problem class with kaidoku r59/r60 and no grammar, unit, scope or
   finding name. Calling it overlap would overstate the coupling.
3. The C2 docstring's "unknown key in any of those shapes is refused" is true only for
   the shapes it enumerates. The hyphen shape is refused by neither path. That is why P1
   is stated as a next-round amendment and not as a defect in the frozen r55 bytes.
4. Lane HEAD advanced during the run. My earlier registry count (201) and the later one
   (202) differ for that reason, not because of a measurement error. The real-lane
   figures are unaffected because they are revision-pinned.

## 6. What I did NOT do

- Did not edit any frozen byte. P1 is a proposal.
- Did not run any mutating git or jj command in the lane. The attacks used throwaway
  clones under scratch, built by importing the committed builder.
- Did not write outside this seat directory and my scratch.
- Did not dispatch subagents (leaf seat). Did not judge, admit, edit, integrate or ship.
- Did not install or upgrade any tool (none was missing; pacman untouched).
- Did not hand-open every hit. Counts are script-classified on the stated criteria;
  the cited files were opened and read.
- Did not make a second proposal. The surface-A sibling defects have no lane that can
  act on them from here, and P1 is the single bounded change that improves an axis.

## 7. Receipts (all under this seat directory)

| File | What it shows |
|---|---|
| `receipts/c1-real-lane-at-tip.txt` | C1 v4 real lane at `3ce0ba03`, exit 0 |
| `receipts/c2-real-lane-at-tip.txt` | C2 v4 real lane at `3ce0ba03`, exit 0 |
| `receipts/c1-selftest-pinned.txt` | C1 selftest with pinned builder + expected, exit 0, 27 cases |
| `receipts/c2-selftest-pinned.txt` | C2 selftest with pinned builder + expected, exit 0, 15 cases |
| `receipts/sibling-classification.tsv` | 136 loose hits (superseded by the decisive counts; kept for audit) |
| `receipts/repro-chousa-final.txt` | chousa verdict flip: splitlines FAIL, LF-only PASS (re-run, exit 0) |
| `receipts/repro-chousa-lf-vs-splitlines.py` | the reproduction script |
| `receipts/c2-probe-plain-unknown-key.txt` | `# FOOBAR=1` → exit 1, RECEIPT-UNKNOWN-KEY |
| `receipts/c2-probe-hyphen-unknown-key.txt` | `# FOO-BAR=1` → exit 0, no finding (the gap) |
| `receipts/widen_accept.txt` | P1 lexer comparison over 13 committed C2 fixtures + real receipt (re-run, exit 0) |
| `receipts/widen_accept.py` | the P1 comparison script |
| `receipts/final_a.py` | the surface-A decisive scan (all-scope 73 / live-only 33) |
| `receipts/ptr_applicable.py`, `receipts/ptr_pop.py` | PTR applicability and souji in-scope pair lines |
