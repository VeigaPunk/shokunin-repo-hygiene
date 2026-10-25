# CritKillRules — round 26 kill-rule falsification (attack seat)

## Status

STATUS: PASS — all three claims attacked; 4 cheats that reach the frozen after-values survive the frozen counters, 6 instrument defects found, no lane write by this seat. Lane was mid-landing while I probed; every claim names the revision/timestamp it was read at.

## Evidence

Read-only. Base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; freeze `12fd90b`; HEAD observed `9a6e0f1` at `2026-10-25T17:37:45Z`. Scratch `/var/tmp/souji-r26-CritKillRules` (removed).

E1. Base SCORECARD (`git show 0eca7c8:SCORECARD.md`, 254 lines): Round 23 @17, Round 24 @175 (fenced), Round 25 @231; counter `markers=2 headings=17 175 231`.

E2. **C1 cheat A — markers only** (rename the two marker prefixes, nothing else): `markers=0 headings=17 175 231`. K2 fails (n25=231 not < n24=175), so this cheat alone is caught.

E3. **C1 cheat B — heading relocation only** (delete base lines 170-230 and base line 231; insert the base 231 and base 175 heading *lines* before base line 17; keep base 17-169 and 232-254): `markers=0 headings=17 18 19` → K1=0 and n25<n24<n23. Resulting file has **zero** copies of the Round 24 measurements table (`| C1 F2 debris census` count 0) and Round 25's measurements table orphaned under a heading inserted 120 lines earlier. Both frozen C1 counters green.

E4. Real C1 landing (SCORECARD last touched `07f83e6`): `markers=0 headings=17 44 78`; amendment-2 spans 1-16, 231-254, 175-207, 17-62, 95-137, 138-169 all present verbatim and in order; no ``` ```markdown ``` remnant; R3 note present. The landing did the work — E3 shows the counters could not have told.

E5. **C2 fabricated green**. Scratch repo (base `03b99df` = `corpus@0eca7c8`, cheat tip `8bbf698`): two invented entries with invented `## Gate` quote lines, two invented snapshot files under `census/round-26/sources/`, five invented Registry rows S128-S132, one README F1 entries-cell edit. No source opened, no staged package read, no mirror step. Outputs:
```
grounded_f1=2 / registry_rows=132                       (c2-counter logic)
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0    (gate-check, rc=0)
file  ok  .../corpus/SOURCES.md                         (sources-census validate, rc=0; W04/W01 only)
grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0  (coverage-agreement, rc=0)
```
All four C2 instruments reach the after-values on bytes no one ever read.

E6. Frozen C2 K1 command (`preregistration.txt:104`) — `git grep -l '^ground: F1' 0eca7c8 -- corpus/knowledge/ | wc -l` → `0` always (rev-pinned to base). The committed counter greps the worktree (`c2-counter.sh:7`). The frozen text can never print the after-value 2; only the counter can.

E7. C2 lane state at 17:37Z (`HEAD 9a6e0f1`): counter `grounded_f1=2 registry_rows=132`; gate-check `entries=2 ok=2 ... fail=0` rc0; coverage-agreement `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0` rc0; `c2-gate.tsv` and `c2-k4-after.tsv` verify ok; **no `c2-k3.tsv`**.

E8. **C3 named cheat** (tool hardcoding `claims=1 flags=0`): `tests/fixtures/r26-axis-check.py --tool <stub>` → `cases=12 pass=3`, rc=1. Caught.

E9. **C3 surviving cheat** — 20-line lookup table keyed on sha256 of the fixture's own 11 case preregs, mapping to expected `rc/claims/flags/rules`; implements none of R1-R4:
```
cases=12 pass=12 control=FALSE-GREEN-REJECTED      rc=0
```
`c3-counter.sh:13` prints only `tail -n 1`, so the fixture arm cannot distinguish E9 from the real tool; `c3-after.tsv` would look identical.

E10. **C3 R2 bypass**: claim `axis: coverage` + `surface-class: bookkeeping-file` → `FLAG C1 R2` (control, rc1). Same claim with one trailing line `surface-class: receipt-binding` → `claims=2 flags=0` rc0. The parser keeps only the last value (`tools/souji-axis-check.py:80`); R2 compares that last value (line 122). No fixture case has two `surface-class:` lines.

E11. Self-host at HEAD: `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0` rc0.

E12. Receipt verification (`python3 -B tools/souji-receipt-run.py verify --root . <receipt>`): FAIL `RECEIPT-COUNTS-ABSENT` for `c1-before.tsv`, `c1-after.tsv`, `c2-before.tsv`, `c2-after.tsv`, `c3-before.tsv`; ok for `c2-k4-base.tsv`, `c2-gate.tsv`, `c2-k4-after.tsv`, `c3-after.tsv`.

E13. Instrument digests: c1 `c8dbb76` (unchanged since `12fd90b`), c2 `e3f7a67` (unchanged), c3 `7d40f5d`@`12fd90b`/`89e0fce` → `b60bce`@`d2e6253` → `fcf954f`@`c594901`..HEAD. `c3-before.tsv` binds `7d40f5d`@`89e0fce` utc 17:35:06; `c3-after.tsv` binds `fcf954f`@`c594901` utc 17:35:07; an earlier `c3-control.tsv` bound `b60bce`@`d2e6253` and was removed at `0c92c2e`. C1/C2 red receipts were also re-derived at `12fd90b`/`89e0fce`, not at the `0eca7c8` rev their frozen red-before commands name.

## Findings

1. C1's frozen counter set accepts the heading-relocation cheat (E3). `census/round-26/c1-counter.sh:7-8` counts two marker prefixes and three heading line numbers; it never inspects what sits under a heading or whether a heading is inside a fence.
2. C1's real protection — amendment 2's per-span byte diff — is prose only. No committed instrument performs it: no tool under `tools/` or `tests/fixtures/` parses SCORECARD structure (only `c1-counter.sh` and unrelated pointer/declared-evidence tools read SCORECARD). The kill-rule clause "byte change inside protected spans" is therefore not executable at the landing gate.
3. C2's load-bearing clause "every cited source is re-opened THIS round" is not mechanically checkable by any frozen instrument. `tools/souji-gate-check.py:97-111` compares each Gate quote only with the bytes under `census/round-26/sources/` — written by the same seat — and `scripts/sources-census.sh` `row_pass`/`url_of` extracts URLs by regex and never fetches. Fabricating both sides (E5) yields green.
4. C2's frozen K1 command and its labeled instrument disagree (E6). Also the counter's grounded count accepts any `corpus/knowledge/*.md` with a `ground: F1` line — arbitrary stubs, not necessarily the two admitted entries.
5. C2's K3 (fleet validate) has no receipt: the prereg's RECEIPTS list names only c2-before, c2-k4-base, c2-after, c2-k4-after, c2-gate; `census/round-26/records/` still has no `c2-k3.tsv`. A landing can leave validate red while every named receipt verifies; `registry_rows=132` in `c2-after.tsv` is a grep count, not the validator's exit code.
6. C3's K2 green is forgeable because the fixture's worlds are static committed strings (`tests/fixtures/r26-axis-check.py:117-255`, written verbatim by `write_case` :321-327) and the counter reduces the run to `tail -n 1` (`c3-counter.sh:13`). E9 passes 12/12 with no rule implemented.
7. C3's `control=FALSE-GREEN-REJECTED` is not evidence about the submitted tool: case 12 runs the fixture's own `STUB_SOURCE` against the static worlds (`tests/fixtures/r26-axis-check.py:373-400`). E9's cheat tool received the label for free.
8. C3's R2 can be evaded with one extra neutral `surface-class:` line because the parser is last-wins (`tools/souji-axis-check.py:80`) and the case set has no duplicate-surface-class case (E10). The frozen R2 says a claim *whose declared surface class is* `bookkeeping-file` is flagged on any non-calibration axis; a claim declaring both is such a claim.
9. C3's R1 ignores the SCORECARD `## Retired` table (`tools/souji-axis-check.py:31` hardcodes the three axes), so a claim on a retired axis is not flagged and R3 can even demand one. Not exploitable this round (`None.` retired), but it is the frozen R1 wording ("non-retired") half-implemented.
10. Receipt layer: the prereg's "each `verify=ok`" is false for 5 of 9 receipts (E12), and those five include every C1/C2-K1 red/green pair — the pairs whose counters print no line matching the runner's counts grammar. C3's red and green bind different instrument bytes (E13) although the counter comment says "receipt-bound", and `c3-before` was re-derived at 17:35:06Z, after a green C3 receipt already existed at 17:29:29Z. C1/C2 red receipts were likewise re-derived at `12fd90b`/`89e0fce` rather than the frozen `0eca7c8`.

## Attack log

### A1 — C1 (calibration): cheapest fake green

- **Cheat**: heading relocation, E3 — 62 deleted lines + 2 inserted heading lines; no measurements block integrated, Round 24 table deleted. **Cost**: one edit, no reading of the fenced payload.
- **Marker-strip only** (the assignment's example): markers=0, headings stay `17 175 231` → **caught by K2** ordering. The "landed number disagrees with its receipt" clause is irrelevant here (no number is landed).
- **Heading relocation**: **survives both frozen counters.** Caught only by amendment 2's span diff, which no instrument implements (Finding 2). The real landing (`07f83e6`) does satisfy the spans (E4), so this is counter inadequacy, not an accusation.
- **Amendment (stricter only; post-data, red first)** — proposed text:

  > AMENDMENT 3 (C1, stricter). Add K3, receipt-bound: `bash census/round-26/c1-span-check.sh --base 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd --tip <tip>` printing `assertions=6 resolved=6 skipped=0 mismatches=0` (mismatches=0 iff: each of the six amendment-2 content spans occurs verbatim and in the order given in `<tip>:SCORECARD.md`; the base 170-230 scaffold block does not occur; both marker prefixes count 0). Receipt `c1-spans-after.tsv` must `verify` ok. Red arm committed BEFORE that green: the same instrument over a /var/tmp mutant tree carrying the heading-relocation cheat (markers=0, headings 17 18 19, Round 24 table absent) must print `mismatches=1` and exit 1, receipt `c1-spans-red.tsv`. K1/K2 unchanged.

### A2 — C2 (coverage): cheapest fake green

- **Cheat**: invent both sides, E5 — two stub entries with Gates, two snapshot files holding the quoted strings, five plausible Registry rows (unique URL, `used_by` = the stubs), one README cell edit. **Cost**: ~40 lines of text, zero network, zero source reading; mirror-validation step skipped and irrelevant (same bytes validate green in place).
- **Copy-staged variant** (no re-grounding at all): copy the staged package's quotes/snapshots/row text into the lane — gate-check compares quotes only to the lane's own snapshots (Finding 3), so identical result. [INFERENCE from code paths read, not executed]
- **Caught by**: nothing in the frozen set. K1 counts the two files; K2 form-checks quote-in-seat-snapshot; K3 is syntactic (`scripts/sources-census.sh` E01-E11 never open a URL); K4 only requires the entries be named in a README `F*` row. The "no byte written into shokuknow" clause is a provenance promise, not a counter.
- **Amendment (stricter only; red first)** — proposed text:

  > AMENDMENT (C2, stricter). (a) K3 is receipt-bound: `c2-k3.tsv` is a receipt of the exact fleet-validate command at tip, and the kill rule reads the receipt's `rc=0`, not the counter's `registry_rows`. (b) Add K5, source-provenance: every snapshot cited by an admitted entry's Gate must be accompanied by a fetch receipt line `sha256=<hex> source=<url or git object> utc=<ISO>` produced in the round window by the committed fetch instrument, and `souji-gate-check.py` must require it; a snapshot with no such line fails K2. (c) K1 is restated against the tip revision with the two admitted paths spelled out, and both must be blobs at tip. (d) The mirror-validate step is receipted (`c2-mirror.tsv`, validate rc=0 over the staged mirror). 

### A3 — C3 (operability): cheapest fake green

- **Cheat named in the seat brief** — tool hardcoding `claims=3 flags=0`: **caught**, `cases=12 pass=3` rc1 (E8).
- **Surviving cheat**: lookup table over the fixture's static case bytes (E9): `cases=12 pass=12 control=FALSE-GREEN-REJECTED` rc0, no rule implemented. **Also survives**: R2 evasion by a trailing neutral `surface-class:` line (E10) — a one-line edit makes a mis-declared claim green.
- **Caught by**: nothing frozen. The fixture is deterministic and public; case 12's control label does not involve the submitted tool (Finding 7).
- **Amendment (stricter only; red first)** — proposed text:

  > AMENDMENT (C3, stricter). (a) A duplicate `axis:`, `surface-class:` or `enumerate:` line inside one CLAIM block is a flag (R2/R1 ambiguity), not last-wins. (b) R1 parses the SCORECARD `## Retired` table and treats a retired axis as not owned. (c) The fixture generates 12 additional held-out worlds at run time by mutating the round's frozen MACHINE BLOCK (each wrong axis, each other surface class, `enumerate:` removed, a universal word inserted into a non-enumerate line, a duplicated `surface-class:` line) with expectations from an inline reference predicate; the pass line becomes `cases=24 pass=24`, and case 12's discriminator must include the submitted tool failing case 1 as well as the stub. (d) The counter prints the `cases=`/`pass=` line and the control line (no `tail -n 1` reduction).

### A4 — receipt layer (all three)

- **Cheat**: change the labeled counter after the red receipt and regenerate the red receipt at a later commit, one second before the green (E13). Kill rule does not compare `tool_sha256` across the pair, and "red-before" is satisfied by file order, not by clock.
- **Observed, not hypothetical**: `c3-before` binds `7d40f5d`, `c3-after` binds `fcf954f`; `c3-before` utc 17:35:06Z postdates a green `c3-after` at 17:29:29Z; 5/9 receipts fail `verify` (E12), so the "each `verify=ok`" sentence is currently unearned for the C1 and C2-K1 pairs.
- **Amendment (stricter only; red first)** — proposed text:

  > AMENDMENT (receipts, stricter, all claims). Every labeled counter must emit one line matching the receipt runner's counts grammar (`assertions=A resolved=R skipped=S mismatches=M`), `mismatches=0` iff all of the claim's after-predicates hold, so `verify` exits 0 for every red and green receipt. A red/green pair must bind identical `tool_sha256`; the red receipt's `utc` must be strictly earlier than the first after-data receipt; the red receipt must be derived at the revision its frozen red-before command names.

> Ordering note: A1/A3/A4 strengthen predicates after C1/C3 green data already exists. Under the frozen AMENDMENT RULES they cannot relax anything; they must be logged, their red arms committed first, and the affected after receipts re-derived at the resulting tip. The existing greens stay valid only for the frozen counter text and do not carry the strengthened evidence.
