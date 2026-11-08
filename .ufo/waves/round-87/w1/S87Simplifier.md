# S87Simplifier — C1 counter dead-arm audit (round 87)

status: complete — dead-arm audit of `census/round-87/c1-pointer-counter.py`, all candidate deletions measured
on both pinned populations with the ten frozen mutants. Lane was read-only; variants and batteries ran on copies
under `/fast/scratch/hyaku/souji-r87/S87Simplifier/` (deleted before yield). Receipts and the patched copies are
filed in `.ufo/waves/round-87/w1/S87Simplifier/`.

## Instruments and pristine control

- All nine instrument hashes re-measured: **all MATCH** (`receipts/instrument-hashes.txt`), including
  `c1-pointer-counter.py fd0a8e24…`. r86 population `79db70f6…` 49 rows; r87 `b066fa0f…` 51 rows.
- Pristine control = the filed counter bytes (variant `v0`, sha256 `fd0a8e24…`, byte-identical to the lane file)
  through the claim's own after command:
  `python3 -B census/round-87/c1-clause-battery.py --counter <v0> --work <dir> --only r86,r87 --expect-killed 18`
  → EXIT 0,
  `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`,
  `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`,
  `SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18`.
  The two r86 survivors are exactly `m12-token-on-line` and `m16-nf6b-punct`. The claim's numbers re-derive on my
  run (necessary, not sufficient).

## Method

Each deletion is a one-token edit of the filed counter; each patch was verified byte-exact (`patch -p1` against a
fresh copy reproduces the variant sha256). Each variant runs the claim's battery once with both pinned populations
and all ten frozen mutants — the battery scores the r86 49-row arm and the r87 51-row arm independently, so the
`--only r86 --expect-killed 8` before arm is measured inside the same run. A deletion counts as preserving iff both
pristine arms print `mismatches=0 errors=0 exit=0` and every mutant's kill **and mismatch count** is unchanged from
the control (`receipts/matrix.txt`).

## Table

| # | deletion (lane line) | pristine r86 | pristine r87 | killed_r86 | killed_r87 | verdict | recommendation |
|---|---|---|---|---|---|---|---|
| D1 | `or len(got) < 2` in the own-tree short-shape guard (378) | 49 rows, mism 0, err 0, exit 0 | 51 rows, mism 0, err 0, exit 0 | 8 * | 10 * | dead in logic, but instrument-blocked | r88, with m14 re-frozen |
| D2 | `bool(want) and ` in `_capture_ok` (360) | 49/0/0 exit 0 | 51/0/0 exit 0 | 8 | 10 | dead, free | **LAND** (diff D2) |
| D2b | `len(want) <= len(have) and ` (360) | 49/0/0 exit 0 | 51/0/0 exit 0 | 8 | 10 | dead, but the frozen stated limits name it "carried" | r88 (with the sentence reworded) |
| D2c | both of the above (360) | 49/0/0 exit 0 | 51/0/0 exit 0 | 8 | 10 | dead; subsumed by D2+D2b | not separately |
| D3 | `before_ok` before-byte half of `_whole` (266) | 49/0/0 exit 0 | 51/0/0 exit 0 | 8 | 10 | load-bearing semantic clause, unrowed | **keep** (a row is the r88 work) |
| D4 | `tt == tk` remnant | — | — | — | — | already deleted in r83; prose only | nothing to delete |
| D5 | `P04_PIN` / `P07_PIN` (harness 105-106) | — | — | — | — | used on every fixture build; proven tripwire | keep |

\* D1's kill counts are measured with the frozen ten where only m14's `old` text is retargeted to the surviving
guard line (`variants/mutants-d1.json`). With the **frozen** mutant file the battery exits 2 before scoring any
mutant — see D1 below. All other rows use the frozen instruments unchanged.

## Candidate detail

### D1 — `len(got) < 2` half: dead in logic, but it is the frozen mutant's anchor

Dead by construction: `_owntree_ok` is reached only with `len(want) >= 2` (the retained half). If `len(got) == 1`,
`_capture_ok` cannot return True (its CAPTURE prefix already yields a target-side list of length >= 2, so
`len(want) <= len(have)` fails), and the wave branch's `got[1:] == want[1:]` compares `[]` against a non-empty
`want[1:]`. Zero differences against the filed counter over the filed probe's 268,324 structured pairs and 60,000
random pairs per predicate (`receipts/dead-arm-probe.txt`, `PROBE PASS`). A wider in-session sweep of 24,209,680
structured pairs per predicate on the same alphabet also found no difference; its `--large` rerun was closed mid-run
at the L1's wrap-up request and `receipts/dead-arm-probe-large.txt` records the arm that completed
(`BULK _capture_ok pairs=24209680 diffs=none`).

Measurement: both pristine arms green; then
`BATTERY-FATAL: edit m14-short-shape occurs 0 times in the counter, need exactly 1` (`receipts/battery-d1.txt`,
EXIT 2) — the frozen mutant's `old` text embeds the deleted half. With m14 re-frozen (`old` = the surviving
`if len(want) < 2:`) the battery gives both arms green, `killed_r86=8 killed_r87=10 killed_total=18`, and the whole
per-mutant mismatch vector is identical to the control (`receipts/battery-d1-adapted-m14.txt`). So: the deletion is
behaviour-preserving on the population but **cannot land in r87** — the claim's kill rule fails on any mutant whose
`old` text does not occur exactly once. Land it in r88 together with the m14 re-freeze (diff D1 below).

### D2 — `bool(want)`: dead, land

Dead by construction: `CAPTURE` requires `(.+)` after a `/`-terminated prefix, and the target slice is
`.rstrip("/")`, so the matched remainder ends in a non-`/` byte and `want = [c for c in … if c]` is never empty
(scan: every CAPTURE match in the enumeration, `empty_want=0`). Zero differences over the same comparisons as D1.

Measurement: both arms green, `killed_r86=8`, `killed_r87=10`, every mutant's mismatch count identical to the
control, battery EXIT 0. No mutant's `old`/`new` text touches the line, so the frozen set applies unchanged.
Cost: the line loses 15 bytes; no other file needs to change.

### D2b — `len(want) <= len(have)`: dead, but named "carried" by the frozen stated limits

Dead by Python list semantics: `have[-len(want):]` has length `min(len(have), len(want))`, and equality with `want`
requires equal lengths, so the suffix test already implies `len(want) <= len(have)` (`SLICE-LEMMA bad=0`). Same
green arms and identical 8/10 kill vector as D2.

**Do not land in r87**: the preregistration's stated limits say this half "stays unrowed and is carried". Landing
the deletion would make the round's own sentence false (Amendment 59 self-falsification). It is dead weight for
r88, paired with a reworded limit sentence (diff D2b below). Keeping it also costs nothing but four tokens and
reads as the condition the suffix test enforces.

### D3 — the `_whole` before-byte half: load-bearing, unrowed — keep

The deletion changes **no** population verdict (both arms green, kills unchanged), which is exactly why deleting it
would be a silent instrument loss: it is a live semantic clause with no row. 3,984/20,000 random `_whole` calls flip
(and 19,808/150,000 in the wider ad-hoc run). Minimal witness:

    needle  = b"tests/vault/x/.git"
    line    = b"- copy at corpus/round-3/tests/vault/x/.git"
    filed   = False      D3 = True

The line names the needle only as the tail of `corpus/round-3/tests/vault/x/.git` — a different path. Dropping the
before-byte half would let a QUARANTINED row resolve on a declaration that names another path. This is one of the
three clauses the preregistration explicitly carries as unrowed; keep it and add a row in r88 (a declaration line
whose only occurrence of the token is such a tail), never delete it.

### D4 — `tt == tk` remnant: already gone

AST scan: r82 has `if tt == tk:` at line 317; r83 and r87 contain no `Compare` on `tt`/`tk`. The only remnant is
the r83 docstring sentence (line 369) that records the deletion. Nothing executable to delete; the prose is
provenance and stays. No variant was run.

### D5 — P04/P07 pins: used, not "unused"

Both pins are read in `build_fixture` (harness lines 224 and 240) and execute on every fixture build (132 battery
harness invocations this audit). Trip test: zeroing either pin aborts the harness with
`C1-HARNESS-FATAL: fixture: FixtureError: P0? byte source sha256 … is not the frozen 000…`, rc 2
(`receipts/pin-trip-p04.txt`, `pin-trip-p07.txt`). They guard the fixture's byte sources (the rows' byte-equality
premise). Deleting them would not change any row score, but it would remove a fail-closed check when the lane's
source bytes drift — keep.

## Recommended diffs

D2 — land now (lane lines 357-360):

```diff
--- a/census/round-87/c1-pointer-counter.py
+++ b/census/round-87/c1-pointer-counter.py
@@ -357,7 +357,7 @@
         return False
     want = [c for c in m.group(1).split("/") if c]
     have = [c for c in token[kr.end(0):].rstrip("/").split("/") if c]
-    return bool(want) and len(want) <= len(have) and have[-len(want):] == want
+    return len(want) <= len(have) and have[-len(want):] == want
```

D1 — r88, together with m14 re-frozen to `old = "    if len(want) < 2:\n"` (lane lines 375-378):

```diff
--- a/census/round-87/c1-pointer-counter.py
+++ b/census/round-87/c1-pointer-counter.py
@@ -375,7 +375,7 @@
     tk = token[kr.end(0):].rstrip("/")
     want = [c for c in tk.split("/") if c]
     got = [c for c in tt.split("/") if c]
-    if len(want) < 2 or len(got) < 2:
+    if len(want) < 2:
         return False
```

D2b — r88, only with the stated-limit sentence reworded (lane lines 357-360):

```diff
--- a/census/round-87/c1-pointer-counter.py
+++ b/census/round-87/c1-pointer-counter.py
@@ -357,7 +357,7 @@
         return False
     want = [c for c in m.group(1).split("/") if c]
     have = [c for c in token[kr.end(0):].rstrip("/").split("/") if c]
-    return bool(want) and len(want) <= len(have) and have[-len(want):] == want
+    return bool(want) and have[-len(want):] == want
```

Patch files: `receipts/d2.patch` (land), `receipts/d1.patch`, `receipts/d2b.patch`, `receipts/d2c.patch`,
`receipts/d3.patch`. Each was applied to a fresh copy of the filed counter with `patch -p1` and reproduced the
variant sha256 exactly: `d1 a30d3f3b…`, `d2 e1c653a3…`, `d2b 6e656498…`, `d2c 2e9de8b2…`, `d3 b6e60033…`.

## Landing notes for L1

- **D2** changes the filed counter bytes to sha256
  `e1c653a39836f9f4ddadb9a99d1067b32c03b875a4c7ee015f1848a7b6c83066`. No population/mutant/harness pin covers the
  counter's bytes (the battery prints the counter sha but does not pin it; the harness does not read it). The
  wave-level instrument-hash line for `c1-pointer-counter.py` and any after receipt would need the new hash; the
  measurement above shows the arms and the full kill vector are unchanged, so re-running the after command on the
  patched bytes costs one battery run and keeps the claim's wording true. If the round prefers frozen instruments
  byte-for-byte, hold D2 to r88 — same diff, same measurement.
- **D1 must not land in r87**: it makes the frozen m14 unappliable and the battery exits 2; the claim names the ten
  frozen mutants.
- **D2b must not land in r87** without the stated-limits rewording.
- D3 and D5 are not deletion candidates.

## Preserved contract

- No lane byte was modified; the filed counter, both populations, the harness, the battery and the mutant file were
  only read. All variants are copies filed in the seat dir.
- The deletions recommended above preserve, on both pinned populations, `mismatches=0 errors=0` and the complete
  ten-mutant kill/mismatch vector (control: 8/10/18, r86 survivors exactly m12 and m16).
- C2 was not touched by this seat.

## Receipts

- `receipts/instrument-hashes.txt` — nine instrument hashes re-measured, all MATCH; both population hashes/row counts.
- `receipts/battery-{v0,d1,d2,d2b,d2c,d3}.txt` — the claim's battery on each variant (both populations, ten mutants).
- `receipts/battery-d1-adapted-m14.txt` — D1 with m14's `old` retargeted (scratch instrument, labelled).
- `receipts/matrix.txt` — compact pristine/kill/mismatch matrix per variant.
- `receipts/*.patch` — exact diffs; `receipts/dead-arm-probe.py` + `.txt` — predicate-level differential proof
  (`PROBE PASS`); `dead-arm-probe-large.txt` — the widened rerun, partial (first arm complete, closed at the L1's
  wrap-up request).
- `receipts/pin-trip-p04.txt`, `pin-trip-p07.txt` — P04/P07 liveness.
- `variants/` — v0 and the five patched counters + the adapted mutant file, byte-identical to what was measured.

Scratch `/fast/scratch/hyaku/souji-r87/S87Simplifier/` was deleted before yield; nothing was left behind.
